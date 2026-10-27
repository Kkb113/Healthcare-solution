"""Bounded serverless wheel/Lakeflow and authenticated failure-polling probes.

One job contains a successful Delta task followed by an intentional argument
validation failure. No job/pipeline notification receiver or schedule is enabled.
"""

import argparse
import hashlib
import json
import time
from contextlib import ExitStack

from databricks.sdk.service import catalog, compute, jobs, pipelines, workspace
from foundation_support import ROOT, databricks_clients, load, now, save
from platform_control import ControlStore, admit_operation, register
from probe_security_baseline import JOBS, principal_client

OUTPUT = ROOT / "output/platform-foundation/serverless-runtime.json"
PATH = "/Workspace/hcp/probes/serverless"
JOBS_PRINCIPAL = "658faa8a-72bf-4285-bf4c-3cd25778ac5f"
POLICY = "69fd7474-2feb-3cca-b79f-c5e1f17e77e5"
SCHEMA = "hc_test._foundation_probe"


def job_arguments(wheel):
    return {
        "name": "hcp-foundation-runtime",
        "max_concurrent_runs": 1,
        "timeout_seconds": 780,
        "budget_policy_id": POLICY,
        "access_control_list": [
            jobs.JobAccessControlRequest(
                service_principal_name=JOBS_PRINCIPAL,
                permission_level=jobs.JobPermissionLevel.CAN_VIEW,
            )
        ],
        "performance_target": jobs.PerformanceTarget.STANDARD,
        "run_as": jobs.JobRunAs(service_principal_name=JOBS_PRINCIPAL),
        "tags": {"project": "healthcare-platform", "component": "medallion"},
        "environments": [
            jobs.JobEnvironment(
                environment_key="probe",
                spec=compute.Environment(environment_version="5", dependencies=[wheel]),
            )
        ],
        "tasks": [
            jobs.Task(
                task_key=key,
                environment_key="probe",
                timeout_seconds=600 if index == 0 else 90,
                max_retries=0,
                depends_on=[jobs.TaskDependency(task_key="delta_replay")]
                if index
                else None,
                python_wheel_task=jobs.PythonWheelTask(
                    package_name="intellify_healthcare_platform",
                    entry_point="hcp-smoke",
                    parameters=["--catalog", target],
                ),
            )
            for index, (key, target) in enumerate(
                [("delta_replay", "hc_test"), ("expected_failure", "hc_prod")]
            )
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume-denied-launch", action="store_true")
    args = parser.parse_args()
    if OUTPUT.exists():
        prior = load(OUTPUT)
        archive = OUTPUT.with_name("serverless-runtime-launch-denied.json")
        if not (
            args.resume_denied_launch
            and prior.get("error_type") == "PermissionDenied"
            and not prior.get("job_id")
            and not prior.get("pipeline_id")
            and not prior.get("cleanup_errors")
            and not archive.exists()
        ):
            raise PermissionError(
                "Retain and reconcile the existing runtime attempt first"
            )
        save(archive, prior)
    wheels = list((ROOT / "platform/dist").glob("*.whl"))
    if len(wheels) != 1:
        raise ValueError("Exactly one locally tested wheel is required")
    wheel = wheels[0]
    source = ROOT / "platform/probes/pipeline_constants.py"
    report = {
        "status": "RUNNING",
        "started_at": now(),
        "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
        "pipeline_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "notifications_enabled": False,
        "poll_interval_seconds": 5,
        "cleanup": {},
        "samples": [],
    }
    save(OUTPUT, report)
    account, client = databricks_clients()
    identities = ExitStack()
    store = ControlStore()
    admit_operation(store, "serverless-runtime-fixture", "automated_dbu_milli", 2000)
    start = time.monotonic()
    deadline = start + 14 * 60
    temporary_privilege = False
    job_id = pipeline_id = run_id = None
    try:
        poller = identities.enter_context(principal_client(account, JOBS))
        report["polling_principal"] = poller.current_user.me().user_name
        # This privilege is absent in the baseline; remove only our added grant.
        prior = client.grants.get("schema", SCHEMA)
        for item in prior.privilege_assignments or []:
            if item.principal == JOBS_PRINCIPAL and any(
                p.value == "CREATE_MATERIALIZED_VIEW" for p in item.privileges or []
            ):
                raise PermissionError(
                    "Unexpected pre-existing probe materialization grant"
                )
        client.grants.update(
            "schema",
            SCHEMA,
            changes=[
                catalog.PermissionsChange(
                    principal=JOBS_PRINCIPAL,
                    add=[catalog.Privilege.CREATE_MATERIALIZED_VIEW],
                )
            ],
        )
        temporary_privilege = True
        client.workspace.mkdirs(PATH)
        for name, payload in [
            (wheel.name, wheel.read_bytes()),
            (source.name, source.read_bytes()),
        ]:
            client.workspace.upload(
                PATH + "/" + name,
                payload,
                format=workspace.ImportFormat.AUTO,
                overwrite=False,
            )
        created = client.jobs.create(**job_arguments(PATH + "/" + wheel.name))
        job_id = created.job_id
        report["job_id"] = job_id
        save(OUTPUT, report)
        store.transact(
            lambda old: register(
                old,
                {
                    "kind": "job",
                    "id": str(job_id),
                    "name": "hcp-foundation-runtime",
                    "owner": "api-adapter",
                },
            )
        )
        actual = client.jobs.get(job_id).settings
        assert actual.environments[0].spec.environment_version == "5"
        assert actual.tasks[0].new_cluster is None
        report["job_configuration"] = actual.as_dict()
        run_id = client.jobs.run_now(job_id).run_id
        report["run_id"] = run_id
        save(OUTPUT, report)
        pipeline_id = client.pipelines.create(
            name="hcp-foundation-runtime",
            catalog="hc_test",
            schema="_foundation_probe",
            channel="CURRENT",
            serverless=True,
            continuous=False,
            development=True,
            run_as=pipelines.RunAs(service_principal_name=JOBS_PRINCIPAL),
            budget_policy_id=POLICY,
            libraries=[
                pipelines.PipelineLibrary(
                    file=pipelines.FileLibrary(path=PATH + "/" + source.name)
                )
            ],
            environment=pipelines.PipelinesEnvironment(environment_version="5"),
            tags={"project": "healthcare-platform", "component": "medallion"},
        ).pipeline_id
        report["pipeline_id"] = pipeline_id
        save(OUTPUT, report)
        store.transact(
            lambda old: register(
                old,
                {
                    "kind": "pipeline",
                    "id": pipeline_id,
                    "name": "hcp-foundation-runtime",
                    "owner": "api-adapter",
                },
            )
        )
        actual_pipeline = client.pipelines.get(pipeline_id)
        assert actual_pipeline.spec.serverless is True
        assert actual_pipeline.spec.channel == "CURRENT"
        report["pipeline_configuration"] = actual_pipeline.spec.as_dict()
        client.pipelines.update_permissions(
            pipeline_id,
            access_control_list=[
                pipelines.PipelineAccessControlRequest(
                    service_principal_name=JOBS_PRINCIPAL,
                    permission_level=pipelines.PipelinePermissionLevel.CAN_VIEW,
                )
            ],
        )
        update_id = client.pipelines.start_update(pipeline_id).update_id
        report["update_id"] = update_id
        save(OUTPUT, report)
        while time.monotonic() < deadline:
            run = poller.jobs.get_run(run_id)
            update = poller.pipelines.get_update(pipeline_id, update_id).update
            job_terminal = run.state.life_cycle_state.value in {
                "TERMINATED",
                "SKIPPED",
                "INTERNAL_ERROR",
            }
            pipeline_terminal = update.state.value in {
                "COMPLETED",
                "FAILED",
                "CANCELED",
            }
            report["samples"].append(
                {
                    "at": now(),
                    "run_state": run.state.as_dict(),
                    "update_state": update.state.value,
                    "task_attempts": [
                        {
                            "task_key": task.task_key,
                            "run_id": task.run_id,
                            "state": task.state.as_dict(),
                        }
                        for task in run.tasks or []
                    ],
                }
            )
            save(OUTPUT, report)
            if job_terminal and pipeline_terminal:
                break
            time.sleep(5)
        else:
            raise TimeoutError("Serverless probe exceeded its bounded polling window")
        report["terminal_run"] = run.as_dict()
        report["terminal_update"] = update.as_dict()
        save(OUTPUT, report)
        success = select_successful_task(run.tasks, "delta_replay")
        failures = [
            task
            for task in run.tasks
            if task.task_key == "expected_failure"
            and task.state.result_state
            and task.state.result_state.value == "FAILED"
        ]
        assert failures
        assert run.state.result_state.value == "FAILED"
        assert update.state.value == "COMPLETED"
        report["failure_detection_seconds"] = round(time.monotonic() - start, 3)
        assert report["failure_detection_seconds"] <= 900
        output = client.jobs.get_run_output(success.run_id)
        # Bounded constant-only task stdout; there are no source records/tokens.
        report["delta_task_output"] = output.as_dict()
        report["expected_failure_output"] = client.jobs.get_run_output(
            failures[0].run_id
        ).as_dict()
        report["terminal_run"] = run.as_dict()
        report["terminal_update"] = update.as_dict()
        report["status"] = "RUNTIME_PASS_BILLING_RECONCILIATION_PENDING"
        report["billing"] = {"status": "PENDING", "empty_is_zero": False}
    except Exception as error:
        report["status"] = "FAIL"
        report["error_type"] = type(error).__name__
        raise
    finally:
        errors = []
        operations = []
        if run_id:

            def cancel_active():
                if client.jobs.get_run(run_id).state.life_cycle_state.value not in {
                    "TERMINATED",
                    "SKIPPED",
                    "INTERNAL_ERROR",
                }:
                    client.jobs.cancel_run(run_id)

            operations.append(("run_reconciled", cancel_active))
        if pipeline_id:

            def stop_pipeline():
                state = client.pipelines.get(pipeline_id).state.value
                if state not in {"IDLE", "DELETED", "FAILED"}:
                    client.pipelines.stop(pipeline_id)
                    cleanup_deadline = time.monotonic() + 60
                    while time.monotonic() < cleanup_deadline:
                        if client.pipelines.get(pipeline_id).state.value in {
                            "IDLE",
                            "DELETED",
                            "FAILED",
                        }:
                            return
                        time.sleep(3)
                    raise TimeoutError("Pipeline did not stop before cleanup deadline")

            operations.extend(
                [
                    (
                        "pipeline_stopped",
                        stop_pipeline,
                    ),
                    (
                        "pipeline_deleted",
                        lambda: client.pipelines.delete(pipeline_id, cascade=True),
                    ),
                ]
            )
        if job_id:
            operations.append(("job_deleted", lambda: client.jobs.delete(job_id)))
        for table in ["wheel_smoke", "pipeline_constants"]:

            def delete_table(name=table):
                from databricks.sdk.errors import NotFound

                try:
                    client.tables.delete(SCHEMA + "." + name)
                except NotFound:
                    pass

            operations.append((table + "_deleted", delete_table))
        if temporary_privilege:
            operations.append(
                (
                    "temporary_grant_removed",
                    lambda: client.grants.update(
                        "schema",
                        SCHEMA,
                        changes=[
                            catalog.PermissionsChange(
                                principal=JOBS_PRINCIPAL,
                                remove=[catalog.Privilege.CREATE_MATERIALIZED_VIEW],
                            )
                        ],
                    ),
                )
            )
        operations.append(
            (
                "source_directory_removed",
                lambda: client.workspace.delete(PATH, recursive=True),
            )
        )
        for name, action in operations:
            try:
                action()
                report["cleanup"][name] = True
            except Exception as error:  # noqa: BLE001 -- continue all cleanup; gate fails
                errors.append({"operation": name, "error_type": type(error).__name__})
                print("Cleanup failure:", name, type(error).__name__)
        identities.close()
        report["cleanup_errors"] = errors
        report["completed_at"] = now()
        report["elapsed_seconds"] = round(time.monotonic() - start, 3)
        if errors:
            report["status"] = "CLEANUP_FAILED"
        save(OUTPUT, report)
    print(
        json.dumps(
            {"status": report["status"], "job_id": job_id, "pipeline_id": pipeline_id}
        )
    )


def select_successful_task(tasks, key):
    matches = [
        task
        for task in tasks
        if task.task_key == key
        and task.state.result_state
        and task.state.result_state.value == "SUCCESS"
    ]
    if len(matches) != 1:
        raise AssertionError("A single successful fixture attempt must be proven")
    return matches[0]


if __name__ == "__main__":
    main()
