"""One paid-principal native Genie question; retain unknown billing as pending."""

import json
import time

from databricks.sdk.errors import NotFound, PermissionDenied
from databricks.sdk.service import catalog, iam
from deploy_security_baseline import execute
from foundation_support import ROOT, databricks_clients, now, save
from platform_control import ControlStore, admit_operation
from probe_security_baseline import JOBS, VALIDATION, principal_client

TABLE = "hc_test._foundation_probe.hcp_genie_fixture"
WAREHOUSE = "bd30bdac29080126"
OUTPUT = ROOT / "output/platform-foundation/genie-pilot.json"


def space_definition():
    return {
        "version": 2,
        "config": {},
        "data_sources": {"tables": [{"identifier": TABLE}]},
        "instructions": {},
    }


def result_rows(caller, response):
    statement = response.statement_response
    rows = statement.result.data_array if statement.result else None
    if rows is None:
        # Genie may return only result metadata. Read the existing statement's
        # cached first chunk as the same caller; never execute a second query
        # or infer a value from the model's prose answer.
        rows = caller.statement_execution.get_statement_result_chunk_n(
            statement.statement_id, 0
        ).data_array
    if rows is None:
        raise RuntimeError("Genie cached statement data is unavailable")
    return rows


def main():
    if OUTPUT.exists():
        raise PermissionError(
            "Reconcile the previous paid question before another pilot"
        )
    report = {
        "status": "INCOMPLETE",
        "started_at": now(),
        "native_questions_dispatched": 0,
        "caller_application_id": JOBS[1],
        "caller_databricks_id": JOBS[0],
        "human_free_usage_assumed": False,
        "billing": {"status": "PENDING", "empty_is_zero": False},
        "cleanup": {},
    }
    account, operator = databricks_clients()
    store = ControlStore()
    admit_operation(store, "genie-pilot-sql", "sql_minutes", 10)
    begin = time.monotonic()
    space_id = None
    try:
        for query in [
            f"CREATE TABLE {TABLE} (id INT, measure INT) USING DELTA",
            f"INSERT INTO {TABLE} VALUES (1, 10), (2, 20), (3, 30)",
        ]:
            execute(operator, WAREHOUSE, query, control=store)
        operator.grants.update(
            "table",
            TABLE,
            changes=[
                catalog.PermissionsChange(
                    principal=JOBS[1], add=[catalog.Privilege.SELECT]
                )
            ],
        )
        space = operator.genie.create_space(
            WAREHOUSE,
            json.dumps(space_definition()),
            parent_path="/hcp",
            title="hcp-foundation-genie-pilot",
            description="Temporary nonpatient native billing and authorization fixture",
        )
        space_id = space.space_id
        report["space_id"] = space_id
        save(OUTPUT, report)
        operator.permissions.update(
            "genie",
            space_id,
            access_control_list=[
                iam.AccessControlRequest(
                    service_principal_name=JOBS[1],
                    permission_level=iam.PermissionLevel.CAN_RUN,
                )
            ],
        )
        with principal_client(account, VALIDATION) as denied:
            try:
                denied.genie.get_space(space_id)
            except (NotFound, PermissionDenied) as error:
                report["ungranted_principal_denied"] = type(error).__name__
            else:
                raise AssertionError(
                    "Unexpected native-space access for ungranted principal"
                )
        with principal_client(account, JOBS) as caller:
            assert caller.current_user.me().id == JOBS[0]
            assert execute(
                caller, WAREHOUSE, f"SELECT COUNT(*) FROM {TABLE}", control=store
            ).result.data_array == [["3"]]
            admit_operation(
                store, "genie-native-question-foundation-001", "genie_questions", 1
            )
            # Persist before dispatch: an HTTP timeout must never erase a question.
            report["native_questions_dispatched"] = 1
            report["dispatch_at"] = now()
            save(OUTPUT, report)
            initial = caller.genie.start_conversation(
                space_id, "How many rows are in hcp_genie_fixture?"
            ).response
            report["conversation_id"] = initial.conversation_id
            report["message_id"] = initial.message_id or initial.id
            save(OUTPUT, report)
            deadline = begin + 8 * 60
            while time.monotonic() < deadline:
                message = caller.genie.get_message(
                    space_id, initial.conversation_id, report["message_id"]
                )
                if message.status.value in {
                    "COMPLETED",
                    "FAILED",
                    "CANCELLED",
                    "QUERY_RESULT_EXPIRED",
                }:
                    break
                time.sleep(3)
            else:
                raise TimeoutError(
                    "Native Genie pilot did not settle inside its funded window"
                )
            report["message"] = message.as_dict()
            assert message.status.value == "COMPLETED"
            result = caller.genie.get_message_query_result(
                space_id, initial.conversation_id, report["message_id"]
            )
            report["query_result"] = result.as_dict()
            rows = result_rows(caller, result)
            assert rows == [["3"]]
            report["reconciled_data_array"] = rows
            report["status"] = "FUNCTIONAL_PASS_BILLING_PENDING"
    except Exception as error:
        report["failure_type"] = type(error).__name__
        report["status"] = "FAIL"
        raise
    finally:
        errors = []
        actions = []
        if space_id:
            actions.extend(
                [
                    (
                        "funded_access_revoked",
                        lambda: operator.permissions.set(
                            "genie",
                            space_id,
                            access_control_list=[
                                iam.AccessControlRequest(
                                    user_name="karthik@intellifysolutions.com",
                                    permission_level=iam.PermissionLevel.CAN_MANAGE,
                                )
                            ],
                        ),
                    ),
                    ("space_trashed", lambda: operator.genie.trash_space(space_id)),
                ]
            )
        actions.append(("fixture_deleted", lambda: operator.tables.delete(TABLE)))
        for name, action in actions:
            try:
                action()
                report["cleanup"][name] = True
            except NotFound:
                report["cleanup"][name] = True
            except Exception as error:  # noqa: BLE001 -- finish independent cleanup and fail gate
                errors.append({"operation": name, "error_type": type(error).__name__})
        report["cleanup_errors"] = errors
        report["completed_at"] = now()
        report["elapsed_seconds"] = round(time.monotonic() - begin, 3)
        if errors:
            report["status"] = "CLEANUP_FAILED"
        save(OUTPUT, report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "questions": report["native_questions_dispatched"],
            }
        )
    )


if __name__ == "__main__":
    main()
