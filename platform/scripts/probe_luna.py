"""Bounded, explicit opt-in native GPT-6 Luna Responses compatibility probe.

Two requests maximum; no retries, real patient data, SQL compute or deployment.
The only tool is a local, deterministic arithmetic fixture.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = "system.ai.gpt-6-luna"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-billable-probe", action="store_true")
    parser.add_argument(
        "--route", choices=["native", "azure-gateway"], default="native"
    )
    args = parser.parse_args()
    if not args.execute_billable_probe:
        parser.error(
            "Explicit --execute-billable-probe required (at most 2 x 256 output tokens)"
        )
    config = json.loads((ROOT / "platform/config/workspace.json").read_text())
    env = {k: v for k, v in os.environ.items() if not k.startswith("DATABRICKS_")}
    env.update(
        DATABRICKS_HOST=config["workspace_host"],
        DATABRICKS_AUTH_TYPE="azure-cli",
        DATABRICKS_AZURE_RESOURCE_ID=config["workspace_resource_id"],
        ARM_SUBSCRIPTION_ID=config["subscription_id"],
    )
    executable = ROOT / ".tools/databricks/1.22.1/databricks.exe"
    model = (
        MODEL
        if args.route == "native"
        else "intellify_healthcare_dbw.readiness.gpt_6_luna"
    )
    report = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "route": "/ai-gateway/openai/v1/responses",
        "workspace_id": config["workspace_id"],
        "requests": [],
        "max_requests": 2,
        "max_output_tokens_per_request": 256,
        "data": "fixed non-patient arithmetic fixture",
        "status": "FAIL",
    }
    history = [
        {
            "role": "user",
            "content": "Use the add_numbers tool to add 17 and 25. After receiving the result, reply with only the resulting integer.",
        }
    ]
    tool = {
        "type": "function",
        "name": "add_numbers",
        "description": "Add two integers in a synthetic test fixture.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
            "additionalProperties": False,
        },
    }
    try:
        with tempfile.TemporaryDirectory(dir=ROOT / "output") as directory:
            for step in range(2):
                body = {
                    "model": model,
                    "input": history,
                    "tools": [tool],
                    "tool_choice": {"type": "function", "name": "add_numbers"}
                    if step == 0
                    else "none",
                    "reasoning": {"effort": "none"},
                    "max_output_tokens": 256,
                }
                if args.route == "azure-gateway":
                    body["store"] = False
                payload = Path(directory) / "request.json"
                payload.write_text(json.dumps(body), encoding="utf-8")
                result = subprocess.run(
                    [
                        str(executable),
                        "api",
                        "post",
                        report["route"],
                        "--json",
                        "@" + str(payload),
                        "-o",
                        "json",
                    ],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=90,
                    check=False,
                )
                if result.returncode:
                    # This CLI command receives no secret arguments; errors are bounded.
                    report["error"] = result.stderr.strip()[:2000]
                    break
                response = json.loads(result.stdout)
                report["requests"].append(
                    {
                        "step": step + 1,
                        "id": response.get("id"),
                        "response_model": response.get("model"),
                        "status": response.get("status"),
                        "usage": response.get("usage"),
                        "output": response.get("output"),
                    }
                )
                if step == 0:
                    calls = [
                        item
                        for item in response.get("output", [])
                        if item.get("type") == "function_call"
                    ]
                    if len(calls) != 1 or calls[0].get("name") != "add_numbers":
                        raise ValueError(
                            "Expected exactly one add_numbers function call"
                        )
                    values = json.loads(calls[0]["arguments"])
                    if values != {"a": 17, "b": 25}:
                        raise ValueError("Tool arguments differ from the fixture")
                    history += response["output"]
                    history.append(
                        {
                            "type": "function_call_output",
                            "call_id": calls[0]["call_id"],
                            "output": "42",
                        }
                    )
                else:
                    answer = "".join(
                        part.get("text", "")
                        for item in response.get("output", [])
                        for part in item.get("content", [])
                        if part.get("type") == "output_text"
                    ).strip()
                    if answer != "42":
                        raise ValueError(
                            "Final answer did not reconcile to the local tool result"
                        )
                    report["status"] = "PASS"
    except (ValueError, subprocess.TimeoutExpired) as error:
        report["error"] = str(error)
    destination = ROOT / (
        "output/platform-readiness/luna-probe.json"
        if args.route == "native"
        else "output/platform-readiness/azure-gateway-luna-probe.json"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
