"""Apply only the four explicitly approved telemetry table grants, additively."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    request = json.loads(
        (ROOT / "platform/config/telemetry-access-request.json").read_text()
    )
    if request["approval_status"] != "USER_APPROVED_2026-10-27":
        raise SystemExit("The exact telemetry scope must have recorded user approval")
    config = json.loads((ROOT / "platform/config/workspace.json").read_text())
    env = {k: v for k, v in os.environ.items() if not k.startswith("DATABRICKS_")}
    env.update(
        DATABRICKS_HOST=config["workspace_host"],
        DATABRICKS_AUTH_TYPE="azure-cli",
        DATABRICKS_AZURE_RESOURCE_ID=config["workspace_resource_id"],
        ARM_SUBSCRIPTION_ID=config["subscription_id"],
    )
    report = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "principal": request["principal"],
        "results": [],
    }
    targets = (
        [("catalog", request["catalog"])]
        + [("schema", obj) for obj in request["schemas"]]
        + [("table", obj) for obj in request["tables"]]
    )
    with tempfile.TemporaryDirectory(dir=ROOT / "output") as directory:
        payload = Path(directory) / "grant.json"
        for kind, target in targets:
            payload.write_text(
                json.dumps(
                    {
                        "changes": [
                            {
                                "principal": request["principal"],
                                "add": target["privileges"],
                            }
                        ]
                    }
                )
            )
            result = subprocess.run(
                [
                    str(ROOT / ".tools/databricks/1.22.1/databricks.exe"),
                    "grants",
                    "update",
                    kind,
                    target["name"],
                    "--json",
                    "@" + str(payload),
                    "-o",
                    "json",
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            item = {
                "kind": kind,
                "name": target["name"],
                "privileges": target["privileges"],
                "status": "PASS" if result.returncode == 0 else "FAIL",
            }
            if result.returncode:
                item["error"] = result.stderr.strip()[:1000]
            report["results"].append(item)
            print(json.dumps(item), flush=True)
    report["status"] = (
        "PASS"
        if all(item["status"] == "PASS" for item in report["results"])
        else "FAIL"
    )
    destination = ROOT / "output/platform-readiness/telemetry-grants.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
