"""Verify historical infrastructure exit evidence; this is not a live health check."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from xml.etree import ElementTree

from foundation_support import ROOT, load

EVIDENCE = ROOT / "evidence/platform/adopted-infrastructure"
REPORTS = [
    "terraform-drift",
    "control-plane",
    "databricks",
    "storage-probe",
    "vault-probe",
    "costs",
    "identity",
    "scim-on-demand",
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def counts(path):
    root = ElementTree.parse(path).getroot()
    return {
        key: sum(int(s.attrib.get(key, 0)) for s in root.iter("testsuite"))
        for key in ["tests", "failures", "errors", "skipped"]
    }


def check_reports(reports):
    require(set(reports) == set(REPORTS), "Missing required foundation report")
    require(
        all(r["status"] == "PASS" for r in reports.values()), "Failed foundation report"
    )
    drift = reports["terraform-drift"]["modules"]
    require(
        set(drift) == {"foundation", "model-access", "workspace"}
        and all(
            m["plan_exit_code"] == 0
            and m["validate"]
            and all(r["actions"] == ["no-op"] for r in m["reviewed_resources"])
            for m in drift.values()
        ),
        "Infrastructure drift or unvalidated module",
    )
    db = reports["databricks"]["results"]
    require(
        db["workspace"]["workspace_id"] == 7405619366453187
        and db["workspace"]["compute_mode"] == "SERVERLESS"
        and db["workspace"]["pricing_tier"] == "PREMIUM",
        "Wrong adopted workspace",
    )
    require(
        set(db["storage_validation"]) == {"hcp_uc_managed_dev", "hcp_landing_dev"}
        and all(
            len(value["results"]) == 6
            and all(item["result"] == "PASS" for item in value["results"])
            for value in db["storage_validation"].values()
        ),
        "UC storage validation incomplete",
    )
    identity = reports["identity"]["results"]
    native = reports["scim-on-demand"]["outcomes"]
    require(
        set(native) == set(identity["groups"])
        and all(
            any(
                record["source_id"] == identity["groups"][name]["external_id"]
                for record in records
            )
            and all(
                record["status"]["status"] in {"Success", "Skipped"}
                and record["status"].get("errorCode") in {None, "RedundantExport"}
                for record in records
            )
            for name, records in native.items()
        ),
        "Native SCIM end-to-end coverage incomplete",
    )
    require(
        identity["mode"] == "SCIM"
        and len(identity["groups"]) == 8
        and identity["out_of_scope_identities_unchanged"]
        and identity["scheduled_sync_success"]
        and identity["assigned_only"]
        and identity["account_aim_enabled"] is False,
        "Identity provisioning incomplete or outside approved scope",
    )
    require(
        set(db["principals"]) == {"sp-hcp-cicd", "sp-hcp-jobs", "sp-hcp-validation"},
        "Three named foundation principals required",
    )
    require(
        not db["warehouses"]
        and not db["apps"]
        and not db["jobs"]
        and all(e["builtin_foundation_models"] for e in db["serving_endpoints"]),
        "Unexpected Phase 1 workload compute",
    )
    cloud = reports["control-plane"]["results"]
    forbidden = {
        "microsoft.eventhub/namespaces",
        "microsoft.network/natgateways",
        "microsoft.operationalinsights/workspaces",
        "microsoft.databricks/workspaces",
    }
    require(
        not any(r["type"].lower() in forbidden for r in cloud["resources"]),
        "Forbidden Azure infrastructure",
    )
    require(
        cloud["model_keyless"]
        and len(cloud["model_deployments"]) == 1
        and cloud["model_deployments"][0]["sku"]["name"] == "DataZoneStandard",
        "Exact-model exception scope changed",
    )
    from verify_foundation import validate_budgets

    validate_budgets(
        cloud["budgets"],
        {"build_ceiling_paise": 2000000, "monthly_target_paise": 600000},
    )
    for report, keys in [
        (
            "storage-probe",
            [
                "read_write",
                "stale_etag_rejected",
                "anonymous_denied",
                "concurrent_lease_rejected",
            ],
        ),
        ("vault-probe", ["rbac_secret_write_read"]),
    ]:
        require(
            all(reports[report]["results"].get(k) is True for k in keys),
            "Incomplete live negative/access probe",
        )
    cost = reports["costs"]["results"]
    require(
        not cost["exposure"]["over_ceiling"]
        and cost["prior_reservations_preserved"]
        and cost["billing_settled"] is False,
        "Unsafe cost/settlement claim",
    )


def verify(directory: Path = EVIDENCE):
    gate = load(directory / "gate.json")
    require(
        gate["phase"] == 1 and gate["status"] == "PASS", "Foundation gate is not PASS"
    )
    require(
        [c["id"] for c in gate["criteria"]] == ["1.1", "1.2", "1.3", "1.4", "1.5"]
        and all(c["status"] == "PASS" for c in gate["criteria"]),
        "Missing/failing foundation exit",
    )
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", gate["source_sha"], "HEAD"],
        cwd=ROOT,
        check=True,
    )
    for relative, expected in gate["input_hashes"].items():
        require(
            (ROOT / relative).resolve().is_relative_to(ROOT.resolve()),
            "Unsafe evidence path",
        )
        raw = subprocess.check_output(
            ["git", "show", f"{gate['source_sha']}:{relative}"], cwd=ROOT
        )
        require(
            hashlib.sha256(raw).hexdigest() == expected,
            "Historical source binding mismatch",
        )
    for filename, expected in gate["report_hashes"].items():
        path = (directory / filename).resolve()
        require(path.is_relative_to(directory.resolve()), "Unsafe report path")
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == expected,
            "Execution report tampered",
        )
    reports = {name: load(directory / f"{name}.json") for name in REPORTS}
    for report in reports.values():
        require(
            report["source_sha"] == gate["source_sha"]
            and report["input_hashes"] == gate["input_hashes"],
            "Reports do not bind the same executable source",
        )
    check_reports(reports)
    test_counts = counts(directory / "all-platform-tests.xml")
    require(
        test_counts == gate["tests"]
        and test_counts["tests"] >= 91
        and not any(test_counts[k] for k in ["errors", "failures", "skipped"]),
        "Incomplete/failed regression suite",
    )
    require(
        hashlib.sha256(
            (ROOT / "evidence/platform/architecture-baseline/gate.json").read_bytes()
        ).hexdigest()
        == gate["prerequisite_gate_sha256"],
        "Phase 0 prerequisite binding changed",
    )
    return {
        "status": "PASS",
        "phase": 1,
        "criteria": 5,
        "tests": test_counts["tests"],
        "source_sha": gate["source_sha"],
        "scope": "Historical foundation exit evidence; rerun live checks before funded deployment",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(verify()))
