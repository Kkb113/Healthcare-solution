"""Bounded exact-Luna probe via a temporary OAuth principal and keyless gateway.

Only fixed arithmetic, JSON and streaming fixtures; no patient data, SQL or
business grants. At most five dispatches; SDK automatic retries are disabled.
"""

import argparse
import json
import uuid

from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
from databricks.sdk.service import catalog as c
from databricks.sdk.service.iam import ComplexValue, WorkspacePermission
from foundation_support import ROOT, databricks_clients, now, save
from openai import APIStatusError, OpenAI
from platform_control import ControlStore, admission, claim

MODEL = "intellify_healthcare_dbw.readiness.gpt_6_luna"
GRANTS = [
    ("CATALOG", "intellify_healthcare_dbw", c.Privilege.USE_CATALOG),
    ("SCHEMA", "intellify_healthcare_dbw.readiness", c.Privilege.USE_SCHEMA),
    ("MODEL_SERVICE", MODEL, c.Privilege.EXECUTE),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume-formats", action="store_true")
    args = parser.parse_args()
    store = ControlStore()
    admission(store.read()[0], True)
    account, operator = databricks_clients()
    operator.ai_gateway.get_model_service(name="model-services/" + MODEL)
    principal = None
    secret = None
    added = []
    report = {
        "status": "INCOMPLETE",
        "started_at": now(),
        "requests": [],
        "cleanup": [],
        "maximum_requests": 2 if args.resume_formats else 5,
    }
    try:
        principal = account.service_principals.create(
            display_name="hcp-foundation-luna-probe", active=True
        )
        # Crash-recovery identifiers only. The OAuth secret is never persisted.
        save(
            ROOT / "output/platform-foundation/luna-principal-manifest.json",
            {"id": principal.id, "application_id": principal.application_id},
        )
        account.workspace_assignment.update(
            7405619366453187, int(principal.id), permissions=[WorkspacePermission.USER]
        )
        operator.service_principals.update(
            principal.id,
            application_id=principal.application_id,
            display_name=principal.display_name,
            entitlements=[ComplexValue(value="workspace-access")],
        )
        secret = account.service_principal_secrets.create(
            principal.id, lifetime="3600s"
        )
        client = WorkspaceClient(
            config=Config(
                host=operator.config.host,
                auth_type="oauth-m2m",
                client_id=principal.application_id,
                client_secret=secret.secret,
                retry_timeout_seconds=20,
            )
        )
        assert client.current_user.me().user_name == principal.application_id
        headers = client.config.authenticate()
        sdk = OpenAI(
            api_key=headers["Authorization"].removeprefix("Bearer "),
            base_url=operator.config.host + "/ai-gateway/openai/v1",
            max_retries=0,
            timeout=45,
        )
        dispatches = 0

        def invoke(**kwargs):
            nonlocal dispatches
            if (
                dispatches >= report["maximum_requests"]
                or len(json.dumps(kwargs).encode()) > 2000
            ):
                raise PermissionError("Probe request/context bound exhausted")

            def admit(state):
                admission(state, True)
                return claim(
                    state, "luna-dispatch-" + uuid.uuid4().hex, "luna_requests", 1
                )

            store.transact(admit)
            dispatches += 1
            return sdk.responses.create(**kwargs)

        common = {
            "model": MODEL,
            "reasoning": {"effort": "none"},
            "max_output_tokens": 256,
            "store": False,
        }
        if not args.resume_formats:
            try:
                invoke(input="Return 42.", **common)
            except APIStatusError as error:
                if error.status_code not in {401, 403, 404}:
                    raise
                report["requests"].append(
                    {"case": "no_grant", "status": error.status_code}
                )
            else:
                raise AssertionError("Unmapped model caller unexpectedly admitted")
        for kind, name, privilege in GRANTS:
            operator.grants.update(
                kind,
                name,
                changes=[
                    c.PermissionsChange(
                        principal=principal.application_id, add=[privilege]
                    )
                ],
            )
            added.append((kind, name, privilege))
        if not args.resume_formats:
            tool = {
                "type": "function",
                "name": "add_numbers",
                "description": "Add fixed fixture integers.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                    "required": ["a", "b"],
                    "additionalProperties": False,
                },
            }
            history = [
                {
                    "role": "user",
                    "content": "Use add_numbers to add 17 and 25, then return only the resulting integer.",
                }
            ]
            first = invoke(
                input=history,
                tools=[tool],
                tool_choice={"type": "function", "name": "add_numbers"},
                **common,
            )
            calls = [item for item in first.output if item.type == "function_call"]
            assert len(calls) == 1 and calls[0].name == "add_numbers"
            assert json.loads(calls[0].arguments) == {"a": 17, "b": 25}
            report["requests"].append(
                {
                    "case": "tool_request",
                    "usage": first.usage.model_dump(),
                    "model": first.model,
                }
            )
            history += [item.model_dump() for item in first.output]
            history += [
                {
                    "type": "function_call_output",
                    "call_id": calls[0].call_id,
                    "output": "42",
                }
            ]
            second = invoke(input=history, tools=[tool], tool_choice="none", **common)
            assert second.output_text.strip() == "42"
            report["requests"].append(
                {
                    "case": "tool_result",
                    "usage": second.usage.model_dump(),
                    "model": second.model,
                }
            )
        schema = {
            "type": "json_schema",
            "name": "arithmetic_fixture",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {"answer": {"type": "integer"}},
                "required": ["answer"],
                "additionalProperties": False,
            },
        }
        third = invoke(
            input="Return answer 42 in the requested schema.",
            text={"format": schema},
            **common,
        )
        assert json.loads(third.output_text) == {"answer": 42}
        report["requests"].append(
            {
                "case": "json_schema",
                "usage": third.usage.model_dump(),
                "model": third.model,
            }
        )
        text = ""
        completed = None
        for event in invoke(input="Return only 42.", stream=True, **common):
            if event.type == "response.output_text.delta":
                text += event.delta
            elif event.type == "response.completed":
                completed = event.response
        assert text.strip() == "42" and completed is not None
        report["requests"].append(
            {
                "case": "stream",
                "usage": completed.usage.model_dump(),
                "model": completed.model,
            }
        )
        report["input_tokens"] = sum(
            x.get("usage", {}).get("input_tokens", 0) for x in report["requests"]
        )
        report["output_tokens"] = sum(
            x.get("usage", {}).get("output_tokens", 0) for x in report["requests"]
        )
        assert report["input_tokens"] <= 24000 and report["output_tokens"] <= 3072
        report["status"] = (
            "FORMAT_COMPATIBILITY_PASS"
            if args.resume_formats
            else "COMPATIBILITY_PASS_CAPACITY_PENDING"
        )
        report["denial_positive_control"] = (
            "Operator verified service exists; the same temporary caller succeeded only after explicit grants"
        )
    except Exception as error:
        report["failure"] = {
            "type": type(error).__name__,
            "http_status": getattr(error, "status_code", None),
            "code": getattr(error, "error_code", None),
            "request_id": getattr(error, "request_id", None),
        }
        raise
    finally:
        if principal:
            for kind, name, privilege in reversed(added):
                operator.grants.update(
                    kind,
                    name,
                    changes=[
                        c.PermissionsChange(
                            principal=principal.application_id, remove=[privilege]
                        )
                    ],
                )
            if secret:
                account.service_principal_secrets.delete(principal.id, secret.id)
                report["cleanup"].append("oauth_secret_revoked")
            account.workspace_assignment.delete(7405619366453187, int(principal.id))
            account.service_principals.delete(principal.id)
            report["cleanup"].append("temporary_principal_deleted")
        report["completed_at"] = now()
        save(ROOT / "output/platform-foundation/model-responses-probe.json", report)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
