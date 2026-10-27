"""Validate pinned infrastructure and require zero drift without applying changes."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from foundation_support import (
    CONFIG,
    OUTPUT,
    ROOT,
    load,
    now,
    review_plan,
    save,
    source_binding,
)


def check(terraform: Path) -> dict:
    if not terraform.is_file():
        raise ValueError("Terraform executable does not exist")
    config = load(CONFIG)
    env = os.environ | {
        "ARM_SUBSCRIPTION_ID": config["workspace_subscription"],
        "TF_IN_AUTOMATION": "1",
    }
    results = {}
    for module in config["terraform_modules"]:
        directory = ROOT / "platform/infra" / module

        def run(arguments, expected=(0,), directory=directory, module=module):
            result = subprocess.run(
                [str(terraform), f"-chdir={directory}", *arguments],
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=600,
                check=False,
            )
            (OUTPUT / f"{module}-{arguments[0]}.log").write_text(
                result.stdout + result.stderr, encoding="utf-8", newline="\n"
            )
            if result.returncode not in expected:
                raise RuntimeError(
                    f"Terraform {module} {arguments[0]} failed with exit {result.returncode}; inspect ignored output log"
                )
            return result

        run(["fmt", "-check"])
        run(["validate", "-json"])
        plan = OUTPUT / f"{module}-final.tfplan"
        result = run(
            [
                "plan",
                "-input=false",
                "-lock-timeout=60s",
                "-detailed-exitcode",
                f"-out={plan}",
            ],
            expected=(0, 2),
        )
        raw = run(["show", "-json", str(plan)])
        import json

        reviewed = review_plan(json.loads(raw.stdout), module)
        if result.returncode != 0 or any(
            item["actions"] != ["no-op"] for item in reviewed
        ):
            raise ValueError(f"Terraform {module} has drift; no changes applied")
        results[module] = {
            "status": "PASS",
            "validate": True,
            "plan_exit_code": result.returncode,
            "reviewed_resources": reviewed,
        }
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--terraform", type=Path, required=True)
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {
        **source_binding(),
        "observed_at": now(),
        "status": "PASS",
        "modules": check(args.terraform.resolve()),
        "mutations": "none; plan only",
    }
    save(OUTPUT / "terraform-drift.json", report)
    print("PASS: all three infrastructure modules validate with zero changes")


if __name__ == "__main__":
    main()
