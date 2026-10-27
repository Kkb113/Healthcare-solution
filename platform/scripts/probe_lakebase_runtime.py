"""Bounded GA Lakebase OAuth/CDF/RLS/suspend-resume capability fixture."""

import argparse
import hashlib
import json
import time
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone

import certifi
import psycopg
from databricks.sdk.common.lro import LroOptions
from databricks.sdk.errors import NotFound, PermissionDenied
from databricks.sdk.service import iam
from databricks.sdk.service import postgres as pg
from deploy_security_baseline import execute
from foundation_support import ROOT, databricks_clients, load, now, save
from lakebase_lifecycle import PROJECT, SYNC, hard_disable
from platform_control import ControlStore, admission, admit_operation, instant, register
from probe_security_baseline import JOBS, principal_client

SOURCE = "hc_test._foundation_probe.hcp_cdf_source"
POLICY = "7c255664-af70-3981-b198-06b758e5d67e"
WAREHOUSE = "bd30bdac29080126"
OUTPUT = ROOT / "output/platform-foundation/lakebase-runtime.json"


def project_specification():
    return pg.Project(
        spec=pg.ProjectSpec(
            display_name="hcp-foundation-lakebase",
            budget_policy_id=POLICY,
            pg_version=17,
            enable_pg_native_login=False,
            default_endpoint_settings=pg.ProjectDefaultEndpointSettings(
                autoscaling_limit_min_cu=1,
                autoscaling_limit_max_cu=2,
                suspend_timeout_duration=pg.Duration(seconds=300),
            ),
        ),
        initial_endpoint_spec=pg.InitialEndpointSpec(
            autoscaling_limit_min_cu=1,
            autoscaling_limit_max_cu=2,
            suspend_timeout_duration=pg.Duration(seconds=300),
            group=pg.EndpointGroupSpec(min=1, max=1),
        ),
    )


def digest(rows):
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def is_database_access_denial(error):
    if getattr(error, "sqlstate", None) in {"28000", "28P01", "42501"}:
        return True
    message = str(error).lower()
    if "password authentication failed for user" in message:
        return True  # Lakebase proxy can return this without a SQLSTATE.
    return "role" in message and any(
        part in message
        for part in ["does not exist", "not found", "not authorized", "not permitted"]
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry-data-access-check", action="store_true")
    parser.add_argument("--resume-confirmed-role-denial", action="store_true")
    args = parser.parse_args()
    if OUTPUT.exists():
        prior = load(OUTPUT)
        archive = OUTPUT.with_name("lakebase-token-mint-assertion-attempt.json")
        if args.resume_confirmed_role_denial:
            archive = OUTPUT.with_name(
                "lakebase-proxy-denial-classification-attempt.json"
            )
            earlier = load(
                OUTPUT.with_name("lakebase-token-mint-assertion-attempt.json")
            )
        else:
            earlier = {"elapsed_seconds": 0}
        if not (
            (args.retry_data_access_check or args.resume_confirmed_role_denial)
            and not archive.exists()
            and prior.get("failure_type")
            == (
                "OperationalError"
                if args.resume_confirmed_role_denial
                else "AssertionError"
            )
            and prior.get("cleanup", {}).get("project_purged") is True
            and prior.get("cleanup", {}).get("endpoint_hard_disabled") is True
            and not prior.get("cleanup_errors")
            and not prior.get("synced_table")
            and prior.get("elapsed_seconds", 2100) + earlier["elapsed_seconds"] + 1800
            <= 35 * 60
        ):
            raise PermissionError(
                "Reconcile the prior Lakebase attempt before another create"
            )
        save(archive, prior)
    account, operator = databricks_clients()
    store = ControlStore()
    state = store.read()[0]
    admission(state, True)
    if (
        instant(state["session"]["deadline_utc"]) - datetime.now(timezone.utc)
    ).total_seconds() < 1800:
        raise PermissionError(
            "Thirty guarded minutes required before Lakebase provisioning"
        )
    admit_operation(store, "lakebase-foundation-lifecycle", "lakebase_minutes", 35)
    admit_operation(store, "lakebase-cdf-pipeline", "automated_dbu_milli", 2000)
    # SQL uses the existing funded aggregate pool; no independent per-probe pool.
    if (
        sum(
            x["units"]
            for x in store.read()[0].get("cost_claims", {}).values()
            if x["meter"] == "sql_minutes"
        )
        < 110
    ):
        raise PermissionError("Reconciled SQL runtime allocation is required")
    identities = load(
        ROOT / "output/platform-foundation/authorization-identities.json"
    )["principals"]
    broker_identity = identities["operations"]
    denied_identity = identities["clinical"]
    report = {
        "status": "INCOMPLETE",
        "started_at": now(),
        "cases": [],
        "cleanup": {},
        "accelerated_sync": False,
        "credential_persistence": False,
        "billing_status": "PENDING_PROVIDER_ATTRIBUTION",
        "empty_billing_is_zero": False,
    }
    save(OUTPUT, report)
    stack = ExitStack()
    project_created = False
    synced_created = False
    endpoint_name = pipeline_id = None
    started = time.monotonic()
    deadline = started + 25 * 60

    def check_deadline():
        if time.monotonic() >= deadline:
            raise TimeoutError("Lakebase fixture reached its cleanup deadline")
        admission(store.read()[0], True)

    def source_sql(statement):
        check_deadline()
        return execute(operator, WAREHOUSE, statement, control=store)

    def connect(client, username):
        check_deadline()
        credential = client.postgres.generate_database_credential(
            endpoint_name, ttl=pg.Duration(seconds=3600)
        )
        return psycopg.connect(
            host=host,
            port=5432,
            dbname="databricks_postgres",
            user=username,
            password=credential.token,
            sslmode="verify-full",
            sslrootcert=certifi.where(),
            connect_timeout=8,
            options="-c statement_timeout=10000",
            autocommit=True,
        )

    def keep_connection(connection):
        # Connections are closed explicitly before disable. Register idempotent
        # close callbacks rather than context-manager transaction exit on an
        # already closed connection during final cleanup.
        stack.callback(connection.close)
        return connection

    def copied_rows(connection):
        return connection.execute(
            'SELECT id, facility_id, measure FROM "_foundation_probe".hcp_synced_fixture ORDER BY id'
        ).fetchall()

    def await_copy(connection, expected):
        while time.monotonic() < deadline:
            try:
                if copied_rows(connection) == expected:
                    return
            except (psycopg.errors.UndefinedTable, psycopg.errors.InvalidSchemaName):
                pass
            synced = operator.postgres.get_synced_table(SYNC)
            report["last_sync_status"] = (
                synced.status.as_dict() if synced.status else {}
            )
            save(OUTPUT, report)
            time.sleep(5)
        raise TimeoutError("CDF copy did not reconcile before deadline")

    try:
        jobs = stack.enter_context(principal_client(account, JOBS))
        broker = stack.enter_context(
            principal_client(
                account,
                (broker_identity["databricks_id"], broker_identity["application_id"]),
            )
        )
        denied = stack.enter_context(
            principal_client(
                account,
                (denied_identity["databricks_id"], denied_identity["application_id"]),
            )
        )
        other_identity = identities["analysts"]
        other_actor = stack.enter_context(
            principal_client(
                account,
                (other_identity["databricks_id"], other_identity["application_id"]),
            )
        )
        actor_a, actor_b = denied.current_user.me().id, other_actor.current_user.me().id
        assert (
            actor_a == denied_identity["databricks_id"]
            and actor_b == other_identity["databricks_id"]
        )
        report["verified_scope_actors"] = [actor_a, actor_b]
        store.transact(
            lambda old: register(
                old,
                {
                    "kind": "lakebase",
                    "id": PROJECT,
                    "name": "hcp-foundation-lakebase",
                    "owner": "api-adapter",
                },
            )
        )
        project_created = True  # A timed-out create remains an uncertain resource.
        project = operator.postgres.create_project(
            project_specification(), "hcp-foundation-lakebase"
        ).wait(LroOptions(timeout=timedelta(minutes=4)))
        report["project"] = project.as_dict()
        save(OUTPUT, report)
        branches = list(operator.postgres.list_branches(PROJECT))
        assert len(branches) == 1
        branch = branches[0].name
        endpoints = list(operator.postgres.list_endpoints(branch))
        assert len(endpoints) == 1
        endpoint = endpoints[0]
        endpoint_name = endpoint.name
        host = endpoint.status.hosts.host
        assert endpoint.status.autoscaling_limit_min_cu == 1
        assert endpoint.status.autoscaling_limit_max_cu == 2
        assert endpoint.status.suspend_timeout_duration.seconds == 300
        report["endpoint"] = endpoint.as_dict()
        report["cases"].append(
            {"case": "bounded_compute_configuration", "status": "PASS"}
        )
        operator.permissions.update(
            "database-projects",
            PROJECT.removeprefix("projects/"),
            access_control_list=[
                iam.AccessControlRequest(
                    service_principal_name="6640afb9-483e-46f6-8b83-405feca8c227",
                    permission_level=iam.PermissionLevel.CAN_MANAGE,
                ),
                iam.AccessControlRequest(
                    service_principal_name=JOBS[1],
                    permission_level=iam.PermissionLevel.CAN_USE,
                ),
                iam.AccessControlRequest(
                    service_principal_name=broker_identity["application_id"],
                    permission_level=iam.PermissionLevel.CAN_USE,
                ),
            ],
        )
        admin = keep_connection(connect(operator, "karthik@intellifysolutions.com"))
        admin.execute("CREATE EXTENSION IF NOT EXISTS databricks_auth")
        for principal in [JOBS[1], broker_identity["application_id"]]:
            admin.execute(
                "SELECT databricks_create_role(%s, 'SERVICE_PRINCIPAL')", (principal,)
            )
        from psycopg import sql

        admin.execute(
            sql.SQL(
                "GRANT CREATE, CONNECT ON DATABASE databricks_postgres TO {}"
            ).format(sql.Identifier(JOBS[1]))
        )
        admin.execute(
            sql.SQL("GRANT CONNECT ON DATABASE databricks_postgres TO {}").format(
                sql.Identifier(broker_identity["application_id"])
            )
        )
        assert admin.execute("SELECT 1").fetchone() == (1,)
        assert admin.execute(
            "SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=%s)",
            (denied_identity["application_id"],),
        ).fetchone() == (False,)
        try:
            connect(denied, denied_identity["application_id"]).close()
        except (NotFound, PermissionDenied, psycopg.OperationalError) as error:
            if isinstance(
                error, psycopg.OperationalError
            ) and not is_database_access_denial(error):
                raise
            report["cases"].append(
                {
                    "case": "end_user_has_no_database_access",
                    "status": "PASS",
                    "denial": type(error).__name__,
                    "sqlstate": getattr(error, "sqlstate", None),
                    "database_role_exists": False,
                    "token_mint_does_not_imply_data_access": True,
                }
            )
        else:
            raise AssertionError("Unexpected database connection for end-user fixture")
        assert admin.execute("SELECT 1").fetchone() == (1,)
        source_sql(
            f"CREATE TABLE {SOURCE} (id BIGINT NOT NULL, facility_id STRING, measure INT) USING DELTA TBLPROPERTIES ('delta.enableChangeDataFeed'='true')"
        )
        source_sql(f"INSERT INTO {SOURCE} VALUES (1,'A',10),(2,'B',20),(3,'A',30)")
        operator.warehouses.stop(WAREHOUSE).result(timeout=timedelta(minutes=1))
        store.transact(
            lambda old: register(
                old,
                {
                    "kind": "synced_table",
                    "id": SYNC,
                    "name": "hcp-foundation-synced",
                    "owner": "api-adapter",
                },
            )
        )
        synced_created = True
        synced = jobs.postgres.create_synced_table(
            pg.SyncedTable(
                spec=pg.SyncedTableSyncedTableSpec(
                    source_table_full_name=SOURCE,
                    branch=branch,
                    postgres_database="databricks_postgres",
                    primary_key_columns=["id"],
                    create_database_objects_if_missing=True,
                    scheduling_policy=pg.SyncedTableSyncedTableSpecSyncedTableSchedulingPolicy.TRIGGERED,
                    accelerated_sync=False,
                    new_pipeline_spec=pg.NewPipelineSpec(
                        budget_policy_id=POLICY,
                        pipeline_channel=pg.NewPipelineSpecPipelineChannel.CURRENT,
                        storage_catalog="hc_test",
                        storage_schema="_foundation_probe",
                    ),
                )
            ),
            "hc_test._foundation_probe.hcp_synced_fixture",
        ).wait(LroOptions(timeout=timedelta(minutes=8)))
        report["synced_table"] = synced.as_dict()
        pipeline_id = synced.status.pipeline_id if synced.status else None
        await_copy(admin, [(1, "A", 10), (2, "B", 20), (3, "A", 30)])
        synced = operator.postgres.get_synced_table(SYNC)
        pipeline_id = synced.status.pipeline_id
        report["pipeline_id"] = pipeline_id
        report["pipeline"] = operator.pipelines.get(pipeline_id).as_dict()
        source_sql(
            f"MERGE INTO {SOURCE} t USING (SELECT 1L id,'A' facility_id,11 measure UNION ALL SELECT 4L,'B',40) s ON t.id=s.id WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *"
        )
        source_sql(f"DELETE FROM {SOURCE} WHERE id=3")
        operator.warehouses.stop(WAREHOUSE).result(timeout=timedelta(minutes=1))
        update = jobs.pipelines.start_update(pipeline_id)
        report["cdf_update_id"] = update.update_id
        expected = [(1, "A", 11), (2, "B", 20), (4, "B", 40)]
        await_copy(admin, expected)
        report["cases"].append(
            {
                "case": "cdf_insert_update_delete_reconciled",
                "status": "PASS",
                "sha256": digest(expected),
            }
        )
        # Synced tables cannot carry PG RLS. Only the trusted broker can read
        # the raw copy; its fixed query always includes the verified scope.
        admin.execute(
            sql.SQL('GRANT USAGE ON SCHEMA "_foundation_probe" TO {}').format(
                sql.Identifier(broker_identity["application_id"])
            )
        )
        admin.execute(
            sql.SQL(
                'GRANT SELECT ON "_foundation_probe".hcp_synced_fixture TO {}'
            ).format(sql.Identifier(broker_identity["application_id"]))
        )
        broker_db = keep_connection(connect(broker, broker_identity["application_id"]))
        assert broker_db.execute(
            'SELECT id FROM "_foundation_probe".hcp_synced_fixture WHERE facility_id=%s ORDER BY id',
            ("A",),
        ).fetchall() == [(1,)]
        admin.execute("CREATE SCHEMA application_fixture")
        admin.execute(
            "CREATE TABLE application_fixture.scope (actor TEXT, facilities TEXT[], version INT NOT NULL CHECK(version>0), valid_from TIMESTAMPTZ NOT NULL, valid_to TIMESTAMPTZ NOT NULL, revoked BOOLEAN NOT NULL DEFAULT FALSE)"
        )
        admin.execute(
            "CREATE TABLE application_fixture.metric (id INT PRIMARY KEY, facility TEXT, measure INT)"
        )
        for actor, facility in [(actor_a, "A"), (actor_b, "B")]:
            admin.execute(
                "INSERT INTO application_fixture.scope VALUES (%s,%s,1,now()-interval '1 day',now()+interval '30 minutes',false)",
                (actor, [facility]),
            )
        admin.execute(
            "INSERT INTO application_fixture.metric VALUES (1,'A',11),(2,'B',20)"
        )
        admin.execute(
            "ALTER TABLE application_fixture.metric ENABLE ROW LEVEL SECURITY"
        )
        admin.execute("ALTER TABLE application_fixture.metric FORCE ROW LEVEL SECURITY")
        admin.execute(
            "CREATE POLICY actor_scope ON application_fixture.metric USING (EXISTS (SELECT 1 FROM application_fixture.scope s WHERE s.actor=nullif(current_setting('hcp.actor',true),'') AND s.version=(SELECT max(x.version) FROM application_fixture.scope x WHERE x.actor=s.actor) AND (SELECT count(*) FROM application_fixture.scope x WHERE x.actor=s.actor AND x.version=s.version)=1 AND metric.facility=ANY(s.facilities) AND NOT s.revoked AND s.valid_from<=now() AND now()<s.valid_to))"
        )
        admin.execute(
            sql.SQL("GRANT USAGE ON SCHEMA application_fixture TO {}").format(
                sql.Identifier(broker_identity["application_id"])
            )
        )
        admin.execute(
            sql.SQL(
                "GRANT SELECT ON ALL TABLES IN SCHEMA application_fixture TO {}"
            ).format(sql.Identifier(broker_identity["application_id"]))
        )
        for actor, rows in [(None, []), (actor_a, [(1,)]), (actor_b, [(2,)])]:
            with broker_db.transaction():
                if actor:
                    broker_db.execute(
                        "SELECT set_config('hcp.actor',%s,true)", (actor,)
                    )
                assert (
                    broker_db.execute(
                        "SELECT id FROM application_fixture.metric ORDER BY id"
                    ).fetchall()
                    == rows
                )
        for scope_version, mode in [(2, "expired"), (3, "revoked"), (4, "ambiguous")]:
            for _ in range(2 if mode == "ambiguous" else 1):
                admin.execute(
                    "INSERT INTO application_fixture.scope VALUES (%s,ARRAY['A'],%s,now()-interval '1 day',CASE WHEN %s THEN now()-interval '1 minute' ELSE now()+interval '30 minutes' END,%s)",
                    (actor_a, scope_version, mode == "expired", mode == "revoked"),
                )
            with broker_db.transaction():
                broker_db.execute("SELECT set_config('hcp.actor',%s,true)", (actor_a,))
                assert (
                    broker_db.execute(
                        "SELECT id FROM application_fixture.metric"
                    ).fetchall()
                    == []
                )
        attributes = admin.execute(
            "SELECT rolsuper,rolbypassrls,rolcreatedb,rolcreaterole FROM pg_roles WHERE rolname=%s",
            (broker_identity["application_id"],),
        ).fetchone()
        assert attributes == (False, False, False, False)
        report["cases"].append(
            {
                "case": "broker_scope_rls_missing_cross_facility_expired_revoked_ambiguous",
                "status": "PASS",
            }
        )
        disabled_probe_credential = broker.postgres.generate_database_credential(
            endpoint_name
        )
        broker_db.close()
        before = digest(copied_rows(admin))
        admin.close()
        operator.pipelines.stop(pipeline_id)
        for _ in range(20):
            if operator.pipelines.get(pipeline_id).state.value in {"IDLE", "FAILED"}:
                break
            time.sleep(3)
        else:
            raise TimeoutError("Sync did not stop before hard disable")
        idle_started = time.monotonic()
        while time.monotonic() - idle_started <= 390:
            check_deadline()
            metadata = operator.postgres.get_endpoint(endpoint_name)
            if metadata.status.current_state == pg.EndpointStatusState.IDLE:
                report["cases"].append(
                    {
                        "case": "native_idle_suspend",
                        "status": "PASS",
                        "observed_seconds": round(time.monotonic() - idle_started, 3),
                    }
                )
                break
            time.sleep(10)
        else:
            raise TimeoutError("Configured 300-second idle suspension was not observed")
        hard_disable(operator, endpoint_name)
        try:
            psycopg.connect(
                host=host,
                port=5432,
                dbname="databricks_postgres",
                user=broker_identity["application_id"],
                password=disabled_probe_credential.token,
                sslmode="verify-full",
                sslrootcert=certifi.where(),
                connect_timeout=8,
            ).close()
        except psycopg.OperationalError as error:
            if "disabled" not in str(error).lower():
                raise
            report["cases"].append(
                {"case": "hard_disable_rejects_connection", "status": "PASS"}
            )
        else:
            raise AssertionError("Connection woke hard-disabled endpoint")
        for _ in range(6):
            check_deadline()
            assert operator.postgres.get_endpoint(endpoint_name).status.disabled is True
            assert operator.pipelines.get(pipeline_id).state.value in {"IDLE", "FAILED"}
            time.sleep(5)
        operator.postgres.update_endpoint(
            endpoint_name,
            pg.Endpoint(
                name=endpoint_name,
                spec=pg.EndpointSpec(
                    endpoint_type=pg.EndpointType.ENDPOINT_TYPE_READ_WRITE,
                    disabled=False,
                ),
            ),
            pg.FieldMask(["spec.disabled"]),
        ).wait(LroOptions(timeout=timedelta(minutes=1)))
        ready_deadline = min(deadline, time.monotonic() + 90)
        while time.monotonic() < ready_deadline:
            if (
                operator.postgres.get_endpoint(endpoint_name).status.current_state
                == pg.EndpointStatusState.ACTIVE
            ):
                break
            time.sleep(3)
        with connect(operator, "karthik@intellifysolutions.com") as resumed:
            assert digest(copied_rows(resumed)) == before
        report["cases"].append(
            {"case": "resume_integrity", "status": "PASS", "sha256": before}
        )
        report["status"] = "FUNCTIONAL_PASS_BILLING_PENDING"
    except Exception as error:
        report["status"] = "FAIL"
        report["failure_type"] = type(error).__name__
        raise
    finally:
        errors = []
        if synced_created and not pipeline_id:
            try:
                uncertain_sync = operator.postgres.get_synced_table(SYNC)
                pipeline_id = (
                    uncertain_sync.status.pipeline_id if uncertain_sync.status else None
                )
                report["cleanup_discovered_pipeline_id"] = pipeline_id
            except NotFound:
                pass
            except Exception as error:  # noqa: BLE001 -- preserve uncertain cleanup
                errors.append(
                    {
                        "operation": "resolve_sync_pipeline",
                        "error_type": type(error).__name__,
                    }
                )
        actions = [("connections_and_credentials_closed", stack.close)]
        if pipeline_id:
            actions.append(
                ("pipeline_stopped", lambda: operator.pipelines.stop(pipeline_id))
            )
        if synced_created:
            actions.append(
                (
                    "synced_table_deleted",
                    lambda: operator.postgres.delete_synced_table(SYNC).wait(
                        LroOptions(timeout=timedelta(minutes=2))
                    ),
                )
            )
        if pipeline_id:
            actions.append(
                ("pipeline_deleted", lambda: operator.pipelines.delete(pipeline_id))
            )
        if endpoint_name:
            actions.append(
                (
                    "endpoint_hard_disabled",
                    lambda: hard_disable(operator, endpoint_name),
                )
            )
        if project_created:
            actions.append(
                (
                    "project_purged",
                    lambda: operator.postgres.delete_project(PROJECT, purge=True).wait(
                        LroOptions(timeout=timedelta(minutes=2))
                    ),
                )
            )
        actions.append(("source_table_deleted", lambda: operator.tables.delete(SOURCE)))
        for name, action in actions:
            try:
                action()
                report["cleanup"][name] = True
            except NotFound:
                report["cleanup"][name] = True
            except Exception as error:  # noqa: BLE001 -- attempt all cleanup; no false PASS
                errors.append({"operation": name, "error_type": type(error).__name__})
        report["cleanup_errors"] = errors
        report["completed_at"] = now()
        report["elapsed_seconds"] = round(time.monotonic() - started, 3)
        if errors or report["elapsed_seconds"] > 1800:
            report["status"] = "FAIL_CLEANUP_OR_DEADLINE"
        save(OUTPUT, report)
    print(json.dumps({"status": report["status"], "cases": len(report["cases"])}))


if __name__ == "__main__":
    main()
