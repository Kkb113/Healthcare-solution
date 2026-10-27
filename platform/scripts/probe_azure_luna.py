"""Two-request exact Luna tool-call probe using keyless Azure CLI authentication."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
MODEL_SUBSCRIPTION = "0725b5e7-75db-4c60-b5e9-928c3df3fcd1"
ENDPOINT = "https://aoai-hcp-luna-0725fcd1.openai.azure.com/openai/v1/"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-billable-probe", action="store_true")
    if not parser.parse_args().execute_billable_probe:
        parser.error(
            "Explicit billable probe opt-in required (2 x 256 output tokens maximum)"
        )
    report = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL",
        "subscription_id": MODEL_SUBSCRIPTION,
        "endpoint": ENDPOINT,
        "model": "gpt-6-luna",
        "authentication": "Entra user; no API key",
        "requests": [],
    }
    try:
        token_result = subprocess.run(
            [
                "az.cmd",
                "account",
                "get-access-token",
                "--resource",
                "https://ai.azure.com",
                "--subscription",
                MODEL_SUBSCRIPTION,
                "-o",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=45,
            check=True,
        )
        token = json.loads(token_result.stdout)["accessToken"]
        client = OpenAI(base_url=ENDPOINT, api_key=token, max_retries=0, timeout=60)
        history = [
            {
                "role": "user",
                "content": "Use add_numbers to add 17 and 25; after the tool result, answer with only the resulting integer.",
            }
        ]
        tool = {
            "type": "function",
            "name": "add_numbers",
            "description": "Add two fixture integers.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                "required": ["a", "b"],
                "additionalProperties": False,
            },
        }
        for step in range(2):
            response = client.responses.create(
                model="gpt-6-luna",
                input=history,
                tools=[tool],
                tool_choice={"type": "function", "name": "add_numbers"}
                if step == 0
                else "none",
                reasoning={"effort": "none"},
                max_output_tokens=256,
                store=False,
            )
            report["requests"].append(
                {
                    "id": response.id,
                    "request_id": response._request_id,
                    "model": response.model,
                    "status": response.status,
                    "usage": response.usage.model_dump() if response.usage else None,
                    "output": [
                        item.model_dump(exclude_none=True) for item in response.output
                    ],
                }
            )
            if step == 0:
                calls = [
                    item for item in response.output if item.type == "function_call"
                ]
                if (
                    len(calls) != 1
                    or calls[0].name != "add_numbers"
                    or json.loads(calls[0].arguments) != {"a": 17, "b": 25}
                ):
                    raise ValueError("Unexpected tool request")
                history.extend(
                    item.model_dump(exclude_none=True) for item in response.output
                )
                history.append(
                    {
                        "type": "function_call_output",
                        "call_id": calls[0].call_id,
                        "output": "42",
                    }
                )
            elif response.output_text.strip() != "42":
                raise ValueError(
                    "Final answer did not reconcile to the local tool result"
                )
        report["status"] = "PASS"
    except Exception as error:  # noqa: BLE001 - CLI boundary records failure and cleanup
        # OpenAI SDK error strings exclude Authorization headers; never serialize clients/tokens.
        report["error"] = str(error)[:2000]
    target = ROOT / "output/platform-readiness/azure-luna-probe.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
