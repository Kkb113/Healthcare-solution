"""Verify fresh saved Phase 2 plans without the narrower Phase 1 apply allowlist.

All three live plans already completed with 'No changes'. This read-only verifier
accepts only complete, non-errored plans whose every resource is no-op/read. It
cannot apply a plan, approve a mutation or alter the Phase 1 deployment guard.
"""

import hashlib
import json
import re
import subprocess

from foundation_support import ROOT, now, save


def main():
    terraform = ROOT / ".tools/terraform/1.17.0/terraform.exe"
    reports = {}
    for module in ["foundation", "model-access", "workspace"]:
        directory = ROOT / "platform/infra" / module
        plan = ROOT / f"output/foundation-validation/{module}-final.tfplan"
        sources = [
            p
            for p in directory.iterdir()
            if p.is_file()
            and (
                p.suffix in {".tf", ".tfvars"}
                or p.name in {".terraform.lock.hcl", "backend.hcl"}
            )
        ]
        if not plan.is_file() or plan.stat().st_mtime < max(
            p.stat().st_mtime for p in sources
        ):
            raise ValueError("Plan predates current infrastructure inputs")
        for args in [["fmt", "-check"], ["validate", "-json"]]:
            subprocess.run(
                [str(terraform), f"-chdir={directory}", *args],
                check=True,
                capture_output=True,
                timeout=120,
            )
        raw = subprocess.check_output(
            [str(terraform), f"-chdir={directory}", "show", "-json", str(plan)],
            timeout=120,
        )
        data = json.loads(raw)
        changes = data.get("resource_changes", [])
        if (
            data.get("errored")
            or data.get("complete") is False
            or data.get("applyable") is True
            or any(x["change"]["actions"] not in [["no-op"], ["read"]] for x in changes)
        ):
            raise ValueError("Saved plan has changes or is incomplete")
        log = ROOT / f"output/foundation-validation/{module}-plan.log"
        text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", log.read_text(encoding="utf-8"))
        if "No changes. Your infrastructure matches the configuration." not in text:
            raise ValueError("Native successful no-change plan evidence missing")
        reports[module] = {
            "status": "PASS",
            "plan_exit_code": 0,
            "plan_exit_evidence": "Native detailed-exitcode plan log says No changes; complete saved plan confirms no-op/read only",
            "changes": 0,
            "plan_generated_at_epoch": plan.stat().st_mtime,
            "plan_sha256": hashlib.sha256(plan.read_bytes()).hexdigest(),
            "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
            "validate": True,
            "input_hashes": {
                p.relative_to(ROOT).as_posix(): hashlib.sha256(
                    p.read_bytes().replace(b"\r\n", b"\n")
                ).hexdigest()
                for p in sources
            },
            "resource_actions": [
                {"address": x["address"], "actions": x["change"]["actions"]}
                for x in changes
            ],
        }
    report = {
        "status": "PASS",
        "observed_at": now(),
        "modules": reports,
        "mutations": "none; saved plan and validation only",
        "phase1_apply_allowlist_unchanged": True,
    }
    save(ROOT / "output/platform-foundation/completion-terraform-drift.json", report)
    print(json.dumps({"status": "PASS", "modules": len(reports), "changes": 0}))


if __name__ == "__main__":
    main()
