"""Tiny signed UC model + minimum CPU serving lifecycle, no healthcare rows."""

import argparse
import json
import os
import time
import traceback
import uuid
from contextlib import ExitStack
from datetime import datetime, timezone

import mlflow
import pandas as pd
from databricks.sdk.errors import NotFound, PermissionDenied
from databricks.sdk.service import ml
from databricks.sdk.service.catalog import PermissionsChange, Privilege
from databricks.sdk.service.serving import (
    DataframeSplitInput,
    EndpointCoreConfigInput,
    ServedEntityInput,
    ServingModelWorkloadType,
)
from foundation_support import ROOT, databricks_clients, load, now, save
from mlflow.models import infer_signature
from platform_control import ControlStore, admission, admit_operation, instant, register
from probe_security_baseline import JOBS, VALIDATION, principal_client

MODEL = "hc_test._foundation_probe.hcp_constant_fixture"
ENDPOINT = "hcp-foundation-constant"
POLICY = "f01fb651-df8d-3b44-9543-962043f2292c"
SERVING_REQUIREMENTS = ["mlflow==3.17.2", "pandas==3.1.0", "cloudpickle==3.1.2"]


def main():
    from hcp.ml.constant_fixture import ConstantFixture

    parser = argparse.ArgumentParser()
    parser.add_argument("--resume-local-logging", action="store_true")
    parser.add_argument("--retry-readiness", action="store_true")
    parser.add_argument("--retry-full-mlflow", action="store_true")
    parser.add_argument("--resume-model-grant", action="store_true")
    args = parser.parse_args()
    store = ControlStore()
    state = store.read()[0]
    admission(state, True)
    if (
        instant(state["session"]["deadline_utc"]) - datetime.now(timezone.utc)
    ).total_seconds() < 900:
        raise PermissionError("At least fifteen minutes required in guarded window")
    prior_claim = any(
        x.get("meter") == "serving_minutes"
        for x in state.get("cost_claims", {}).values()
    )
    if prior_claim:
        prior = load(ROOT / "output/platform-foundation/serving-probe.json")
        local_resume = (
            args.resume_local_logging
            and prior.get("failure", {}).get("type")
            in {
                "UnicodeEncodeError",
                "ValueError",
                "MlflowException",
                "ResourceDoesNotExist",
            }
            and not prior.get("model_version")
            and prior.get("cleanup", {}).get("endpoint_deleted") is True
        )
        archive = (
            ROOT / "output/platform-foundation/serving-first-readiness-attempt.json"
        )
        readiness_retry = (
            args.retry_readiness
            and not archive.exists()
            and prior.get("failure", {}).get("type") == "TimeoutError"
            and prior.get("cleanup", {}).get("endpoint_deleted") is True
            and prior.get("cleanup", {}).get("model_deleted") is True
            and prior.get("elapsed_seconds", 3600) + 900 <= 3600
        )
        full_archive = (
            ROOT / "output/platform-foundation/serving-incompatible-skinny-attempt.json"
        )
        full_retry = (
            args.retry_full_mlflow
            and (not full_archive.exists() or load(full_archive) == prior)
            and prior.get("failure", {}).get("message")
            == "Serving environment build failed"
            and prior.get("cleanup", {}).get("endpoint_deleted") is True
            and prior.get("cleanup", {}).get("model_deleted") is True
            and prior.get("elapsed_seconds", 3600)
            + load(archive).get("elapsed_seconds", 3600)
            + 900
            <= 3600
        )
        grant_archive = (
            ROOT / "output/platform-foundation/serving-invalid-grant-attempt.json"
        )
        grant_resume = (
            args.resume_model_grant
            and not grant_archive.exists()
            and prior.get("failure", {}).get("type") == "InvalidState"
            and prior.get("failure", {}).get("message")
            == "REGISTERED_MODEL is not enabled"
            and prior.get("endpoint_create_attempted") is False
            and prior.get("cleanup", {}).get("endpoint_deleted") is True
            and prior.get("cleanup", {}).get("model_deleted") is True
        )
        if not (local_resume or readiness_retry or full_retry or grant_resume):
            raise PermissionError(
                "Reconcile existing serving attempt before provisioning again"
            )
        if readiness_retry:
            save(archive, prior)
        if full_retry:
            save(full_archive, prior)
        if grant_resume:
            save(grant_archive, prior)
    admit_operation(store, "constant-serving-lifecycle", "serving_minutes", 60)
    store.transact(
        lambda value: register(
            value,
            {
                "kind": "serving",
                "id": ENDPOINT,
                "name": ENDPOINT,
                "owner": "api-adapter",
            },
        )
    )
    account, client = databricks_clients()
    report = {
        "status": "INCOMPLETE",
        "started_at": now(),
        "model": MODEL,
        "endpoint": ENDPOINT,
        "calls": [],
        "cleanup": {},
        "clinical_model": False,
        "endpoint_create_attempted": False,
        "readiness_samples": [],
        "pip_requirements": SERVING_REQUIREMENTS,
    }
    experiment_id = None
    original_acl = []
    acl_captured = False
    identities = ExitStack()
    begin = time.monotonic()
    try:
        report["experiment_name"] = (
            "/hcp/foundation-serving-probe-" + uuid.uuid4().hex[:8]
        )
        experiment_id = client.experiments.create_experiment(
            report["experiment_name"]
        ).experiment_id
        report["experiment_id"] = experiment_id
        for item in client.experiments.get_permissions(
            experiment_id
        ).access_control_list:
            for permission in item.all_permissions or []:
                if not permission.inherited:
                    original_acl.append(
                        ml.ExperimentAccessControlRequest(
                            user_name=item.user_name,
                            group_name=item.group_name,
                            service_principal_name=item.service_principal_name,
                            permission_level=permission.permission_level,
                        )
                    )
        acl_captured = True
        client.experiments.update_permissions(
            experiment_id,
            access_control_list=[
                ml.ExperimentAccessControlRequest(
                    service_principal_name=JOBS[1],
                    permission_level=ml.ExperimentPermissionLevel.CAN_EDIT,
                )
            ],
        )
        runtime = identities.enter_context(principal_client(account, JOBS))
        keys = [
            "DATABRICKS_CONFIG_PROFILE",
            "DATABRICKS_HOST",
            "DATABRICKS_AUTH_TYPE",
            "DATABRICKS_CLIENT_ID",
            "DATABRICKS_CLIENT_SECRET",
        ]
        prior_env = {key: os.environ.get(key) for key in keys}

        def restore_env():
            for key, value in prior_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        identities.callback(restore_env)
        os.environ.pop("DATABRICKS_CONFIG_PROFILE", None)
        os.environ.update(
            {
                "DATABRICKS_HOST": runtime.config.host,
                "DATABRICKS_AUTH_TYPE": "oauth-m2m",
                "DATABRICKS_CLIENT_ID": runtime.config.client_id,
                "DATABRICKS_CLIENT_SECRET": runtime.config.client_secret,
            }
        )
        mlflow.set_tracking_uri("databricks")
        mlflow.set_registry_uri("databricks-uc")
        mlflow.set_experiment(experiment_id=experiment_id)
        report["registry_principal"] = JOBS[1]
        sample = pd.DataFrame({"input": [1]})
        expected = ConstantFixture().predict(None, sample)
        with mlflow.start_run():
            logged = mlflow.pyfunc.log_model(
                name="constant_fixture",
                python_model=ConstantFixture(),
                signature=infer_signature(sample, expected),
                input_example=sample,
                code_paths=[str(ROOT / "platform/src/hcp")],
                registered_model_name=MODEL,
                await_registration_for=90,
                pip_requirements=report["pip_requirements"],
                metadata={"synthetic_fixture": True, "clinical_use": False},
            )
        version = str(logged.registered_model_version)
        assert (
            mlflow.pyfunc.load_model(f"models:/{MODEL}/{version}")
            .predict(sample)
            .equals(expected)
        )
        report["model_version"] = version
        report["signature"] = logged.signature.to_dict()
        runtime.grants.update(
            "function",  # UC registered-model grants use FUNCTION in this API.
            MODEL,
            changes=[
                PermissionsChange(
                    principal="karthik@intellifysolutions.com",
                    add=[Privilege.EXECUTE],
                )
            ],
        )
        report["temporary_endpoint_creator_execute"] = True
        admission(store.read()[0], True)
        report["endpoint_create_attempted"] = True
        client.serving_endpoints.create(
            ENDPOINT,
            budget_policy_id=POLICY,
            config=EndpointCoreConfigInput(
                name=ENDPOINT,
                served_entities=[
                    ServedEntityInput(
                        entity_name=MODEL,
                        entity_version=version,
                        name="constant",
                        workload_size="Small",
                        workload_type=ServingModelWorkloadType.CPU,
                        scale_to_zero_enabled=True,
                    )
                ],
            ),
        )
        # Reserve cleanup time inside the fifteen-minute probe contract. Capture
        # readiness/build diagnostics before deleting an unsuccessful endpoint.
        while time.monotonic() - begin < 810:
            configured = client.serving_endpoints.get(ENDPOINT)
            report["last_endpoint_metadata"] = configured.as_dict()
            report["readiness_samples"].append(
                {"at": now(), "state": configured.state.as_dict()}
            )
            if configured.state.ready and configured.state.ready.value == "READY":
                break
            if (
                configured.state.config_update
                and configured.state.config_update.value == "UPDATE_FAILED"
            ):
                raise RuntimeError("Serving environment build failed")
            save(
                ROOT / "output/platform-foundation/serving-probe-progress.json", report
            )
            time.sleep(10)
        else:
            raise TimeoutError(
                "Serving endpoint did not become ready within the funded probe"
            )
        entity = configured.config.served_entities[0]
        assert entity.scale_to_zero_enabled and entity.workload_size.lower() == "small"
        report["minimum_cpu_sku"] = entity.as_dict()
        report["readiness_seconds"] = round(time.monotonic() - begin, 3)
        for kind in ["first_after_deploy", "warm"]:
            admission(store.read()[0], True)
            start = time.monotonic()
            response = client.serving_endpoints.query(
                ENDPOINT,
                dataframe_split=DataframeSplitInput(columns=["input"], data=[[1]]),
            )
            assert response.predictions == [{"prediction": 42}]
            report["calls"].append(
                {
                    "case": kind,
                    "elapsed_ms": round((time.monotonic() - start) * 1000, 3),
                    "reconciled_prediction": 42,
                }
            )
        with principal_client(account, VALIDATION) as wrong:
            try:
                wrong.serving_endpoints.query(
                    ENDPOINT,
                    dataframe_split=DataframeSplitInput(columns=["input"], data=[[1]]),
                )
            except (PermissionDenied, NotFound) as error:
                report["caller_denied"] = type(error).__name__
            else:
                raise AssertionError("Unexpected unauthorized serving access")
        report["status"] = "PASS"
    except Exception as error:  # noqa: BLE001 - bounded fixture; always clean up
        report["status"] = "FAIL"
        report["failure"] = {
            "type": type(error).__name__,
            "code": getattr(error, "error_code", None),
            "stack": traceback.format_tb(error.__traceback__),
            "message": str(error)[:600],
        }
    finally:
        if report.get("failure") and report["endpoint_create_attempted"]:
            try:
                logs = client.serving_endpoints.build_logs(ENDPOINT, "constant")
                report["build_log_tail"] = logs.logs[-6000:] if logs.logs else ""
            except Exception as error:  # noqa: BLE001 -- diagnostics must not prevent cleanup
                report["build_log_error"] = type(error).__name__
        try:
            try:
                client.serving_endpoints.delete(ENDPOINT)
            except NotFound:
                pass
            deadline = time.monotonic() + 150
            while time.monotonic() < deadline:
                try:
                    client.serving_endpoints.get(ENDPOINT)
                except NotFound:
                    report["cleanup"]["endpoint_deleted"] = True
                    break
                time.sleep(3)
        except Exception as error:  # noqa: BLE001 - retain cleanup errors and continue
            report["cleanup"]["endpoint_error"] = type(error).__name__
        try:
            current_model = client.registered_models.get(MODEL)
            if current_model.created_by not in {
                "karthik@intellifysolutions.com",
                JOBS[1],
            }:
                raise PermissionError(
                    "Temporary model creator does not match the authorized operator"
                )
            for version_record in list(client.model_versions.list(MODEL)):
                client.model_versions.delete(MODEL, version_record.version)
            client.registered_models.delete(MODEL)
            report["cleanup"]["model_deleted"] = True
        except NotFound:
            report["cleanup"]["model_deleted"] = True
        except Exception as error:  # noqa: BLE001 -- finish identity and experiment cleanup
            report["cleanup"]["model_error"] = type(error).__name__
        if experiment_id:
            try:
                if acl_captured:
                    client.experiments.set_permissions(
                        experiment_id, access_control_list=original_acl
                    )
                    report["cleanup"]["experiment_permissions_restored"] = True
                client.experiments.delete_experiment(experiment_id)
                report["cleanup"]["experiment_soft_deleted"] = True
            except Exception as error:  # noqa: BLE001 -- never skip secret revocation
                report["cleanup"]["experiment_error"] = type(error).__name__
        try:
            identities.close()
            report["cleanup"]["runtime_secret_revoked"] = True
        except Exception as error:  # noqa: BLE001 -- retain explicit credential cleanup failure
            report["cleanup"]["runtime_secret_error"] = type(error).__name__
        report["completed_at"] = now()
        report["elapsed_seconds"] = round(time.monotonic() - begin, 3)
        if (
            not report["cleanup"].get("endpoint_deleted")
            or not report["cleanup"].get("model_deleted")
            or any(key.endswith("_error") for key in report["cleanup"])
            or report["elapsed_seconds"] > 900
        ):
            report["status"] = "FAIL_CLEANUP_OR_DEADLINE"
        save(ROOT / "output/platform-foundation/serving-probe.json", report)
    print(json.dumps(report))
    if report["status"] != "PASS":
        raise RuntimeError(
            "Serving capability probe failed; inspect sanitized evidence"
        )


if __name__ == "__main__":
    main()
