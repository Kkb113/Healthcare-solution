"""Offline Phase 0 contract/cost validation, with optional accepted-release verification.

This is a design-gate harness, not an implementation of future ingestion, security,
model serving or transactional spend enforcement. Tenant probes remain future gates.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from decimal import ROUND_CEILING, Decimal
from pathlib import Path

from freeze_gate_contracts import build as build_gate_contract
from freeze_source_contracts import (
    DESCRIPTOR,
    RELEASE,
    ROOT,
    build,
    digest,
    load,
    topological_order,
)

CONTRACTS = ROOT / "platform/contracts/architecture"
PAISE = Decimal("0.01")


def number(value) -> Decimal:
    if isinstance(value, bool):
        raise TypeError("Boolean is not a numeric quantity")
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError("Quantity must be finite and nonnegative")
    return result


def price_lines(lines: list, rates: dict, fx: str, tax: str, factor="1") -> dict:
    result = []
    identities = set()
    for line in lines:
        if line["id"] in identities:
            raise ValueError("Duplicate charge attribution")
        identities.add(line["id"])
        rate = rates.get(line["rate"])
        if not rate or not rate.get("unit") or not rate.get("meter"):
            raise ValueError("Unknown price/unit: fail closed")
        if number(rate["usd"]) == 0:
            raise ValueError("Free/promotional zero price not permitted in feasibility")
        usd = number(line["quantity"]) * number(rate["usd"]) * number(factor)
        inr = (usd * number(fx) * (1 + number(tax))).quantize(
            PAISE, rounding=ROUND_CEILING
        )
        result.append(
            {
                "id": line["id"],
                "quantity": line["quantity"],
                "unit": rate["unit"],
                "usd": str(usd),
                "inr_including_tax_reserve": str(inr),
            }
        )
    return {
        "lines": result,
        "usd": str(sum((Decimal(row["usd"]) for row in result), Decimal(0))),
        "inr": str(
            sum(
                (Decimal(row["inr_including_tax_reserve"]) for row in result),
                Decimal(0),
            )
        ),
    }


def calculate_costs(model: dict) -> dict:
    fx, tax = model["planning_inr_per_usd"], model["tax_reserve_fraction"]
    build_cost = price_lines(model["build"], model["rates"], fx, tax)
    extra = number(model["preflight_unsettled_inr"]) + number(
        model["build_contingency_inr"]
    )
    total = Decimal(build_cost["inr"]) + extra
    build_cost.update(
        {
            "preflight_pending_inr": model["preflight_unsettled_inr"],
            "contingency_inr": model["build_contingency_inr"],
            "total_inr": str(total),
            "ceiling_inr": model["ceiling_inr"],
            "fits": total <= number(model["ceiling_inr"]),
        }
    )
    monthly = {}
    for name, lines in model["monthly"].items():
        cost = price_lines(lines, model["rates"], fx, tax)
        total = Decimal(cost["inr"]) + number(model["monthly_contingency_inr"])
        monthly[name] = dict(
            cost,
            total_inr=str(total),
            contingency_inr=model["monthly_contingency_inr"],
            fits=total <= number(model["monthly_ceiling_inr"]),
        )
    stresses = []
    for case in model["stress_cases"]:
        lines = [dict(line) for line in model["build"]]
        if "genie_quantity" in case:
            next(line for line in lines if line["id"] == "native-genie")["quantity"] = (
                case["genie_quantity"]
            )
        cost = price_lines(lines, model["rates"], case["fx"], tax, case["rate_factor"])
        total = Decimal(cost["inr"]) + extra
        fits = total <= number(model["ceiling_inr"])
        stresses.append(
            {
                "name": case["name"],
                "total_inr": str(total),
                "fits": fits,
                "expected": case["expected"],
                "matches_expected": fits == (case["expected"] == "WITHIN_BUDGET"),
            }
        )
    return {
        "build": build_cost,
        "monthly": monthly,
        "stress_cases": stresses,
        "basis": "Published USD unit rates × unmeasured engineering quantities; INR100/USD +18% planning tax reserve; no credits/free promotional units. Later gates must substitute measured usage and reconcile delayed invoices.",
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_package(root=ROOT, with_release=False, require_approval=True) -> dict:
    folder = root / "platform/contracts/architecture"
    objects = {p.stem: load(p) for p in folder.glob("*.json")}
    require(
        objects["gate-dependencies"] == build_gate_contract(root),
        "Roadmap exit/dependency contract changed without baseline review",
    )
    source = objects["source-contracts"]
    tables = source["tables"]
    names = {table["table"] for table in tables}
    require(len(names) == len(tables) == 25, "Exactly 25 unique source tables required")
    require(source["descriptor_sha256"] == DESCRIPTOR, "Release binding drift")
    require(
        sum(t["canonical_rows"] for t in tables) == source["business_rows"] == 1937925,
        "Canonical row budget drift",
    )
    require(
        source["delivery_files"] == 3445 and len(source["source_systems"]) == 8,
        "Delivery/source contract drift",
    )
    deps = {table["table"]: table["upstream"] for table in tables}
    require(
        topological_order(deps) == source["topological_order"],
        "Load dependency order drift",
    )
    for table in tables:
        columns = table["columns"]
        require(
            len({col["canonical"] for col in columns}) == len(columns),
            "Duplicate canonical column",
        )
        require(
            set(table["primary_key"]) <= {col["canonical"] for col in columns},
            "Unmapped primary key",
        )
        require(
            all(
                col.get("source") and col.get("type") and "nullable" in col
                for col in columns
            ),
            "Incomplete column mapping",
        )
        for col in columns:
            if col["reference_target"]:
                target, field = col["reference_target"].split(".")
                require(target in names, "Unknown referenced table")
                target_columns = next(
                    t["columns"] for t in tables if t["table"] == target
                )
                require(
                    field in {c["canonical"] for c in target_columns},
                    "Unknown referenced column",
                )
    history = objects["delivery-temporal"]
    require(
        history["retrospective_known_to_as_feature"] is False,
        "Hindsight known_to cannot define feature visibility",
    )
    require(
        "manifest_file_id" in history["delivery_key"]
        and "sha256" not in history["delivery_key"],
        "Checksum cannot be delivery identity",
    )
    require(
        history["reference_policy"]["runtime_oracle_access"] is False
        and history["reference_policy"]["validation_business_write"] is False,
        "Oracle separation broken",
    )
    kpis = objects["kpi-catalog"]
    require(len(kpis["definitions"]) == kpis["count"] == 42, "KPI coverage drift")
    require(len({k["id"] for k in kpis["definitions"]}) == 42, "Duplicate KPI identity")
    require(
        sum(k["reference_test"] for k in kpis["definitions"]) == 20,
        "Twenty independent KPI checks required",
    )
    require(
        all(
            set(k["sources"]) <= names
            and k["grain"]
            and k["formula"]
            and k["unit"]
            and k["denominator"]
            for k in kpis["definitions"]
        ),
        "Incomplete KPI grain/source/unit",
    )
    ml = objects["ml-eligibility"]
    require(
        ml["staffing_rule_provenance"]["accepted_base_hppd"] == "5.5",
        "Staffing rule differs from accepted source",
    )
    require(
        [m["id"] for m in ml["use_cases"]] == [f"M{i}" for i in range(1, 14)],
        "All 13 dispositions required",
    )
    require(
        all(
            set(m["sources"]) <= names
            and m["decision_origin"]
            and m["feature_rules"]
            and m["label"]
            for m in ml["use_cases"]
        ),
        "Incomplete ML eligibility",
    )
    require(
        ml["use_cases"][10]["disposition"] == "RETROSPECTIVE_ONLY"
        and ml["use_cases"][5]["disposition"] == "DERIVED",
        "Unsupported prospective model",
    )
    require(
        ml["online_contract"]["compatible"] == ["M4", "M10"], "Online eligibility drift"
    )
    split = ml["split_policy"]
    require(
        split["training_origins"][1]
        < split["validation_origins"][0]
        <= split["validation_origins"][1]
        < split["untouched_test_origins"][0],
        "Overlapping holdout partitions",
    )
    require(
        split["untouched_test_origins"] == ["2025-07-01", "2025-12-31"],
        "Roadmap holdout drift",
    )
    probes = objects["probe-matrix"]["probes"]
    pmap = {p["id"]: p for p in probes}
    require(len(pmap) == len(probes) == 16, "Probe identity coverage")
    require(
        [p["id"] for p in probes if not p["required"]] == ["P11"],
        "Only inbound webhook optional",
    )
    for cap in objects["capability-matrix"]["capabilities"]:
        require(
            cap["required_probe"] in pmap
            and cap["id"] in pmap[cap["required_probe"]]["capabilities"],
            "Capability missing probe",
        )
        require(
            cap["official_url"].startswith("https://learn.microsoft.com/")
            and cap["reviewed_on"] == "2026-10-27",
            "Missing dated primary source",
        )
        require((root / cap["tenant_evidence"]).is_file(), "Missing tenant evidence")
        require(
            cap["unresolved_probe_blocks_dependent_provisioning"],
            "Unresolved capability must block dependent provisioning",
        )
    security = objects["security-ownership"]
    resources = security["resources"]
    require(
        len({r["resource"] for r in resources}) == len(resources),
        "Duplicate lifecycle ownership",
    )
    require(
        all(
            r["owner"]
            in {
                "terraform",
                "bundle",
                "api-adapter",
                "reference-only",
                "control-plane-adapter",
            }
            and r["rollback"]
            for r in resources
        ),
        "Missing lifecycle/rollback owner",
    )
    require(
        len(security["roles"]) == 8 and len(security["copies"]) == 6,
        "Authorization scope incomplete",
    )
    work = objects["test-workloads"]
    require(
        work["performance"]["minimum_completed_per_component"] >= 100
        and work["performance"]["concurrent_users"] == 10,
        "Performance sample/concurrency weakened",
    )
    require(
        len(work["replay"]["gold_days"]) == 5
        and len(work["replay"]["autopilot_clean_days"]) == 7,
        "Replay samples weakened",
    )
    require(
        work["replay"]["poll_seconds"] <= 120
        and work["replay"]["detection_max_wall_minutes"] == 15,
        "Required operational polling weakened",
    )
    require(
        work["agent_evaluation"]["full_questions"]
        == sum(work["agent_evaluation"]["case_mix"].values())
        == 200
        and work["agent_evaluation"]["full_phases"] == [10, 12, 13],
        "Agent regression scope lost",
    )
    genie = work["genie"]
    require(
        genie["initial_questions"]
        == genie["initial_questions_per_space"] * genie["spaces"],
        "Genie question budget mismatch",
    )
    require(
        genie["total_native_build_questions"]
        == sum(
            genie[k]
            for k in [
                "initial_questions",
                "recreate_questions",
                "batch_release_questions",
                "rti_regression_questions",
                "agent_tool_questions",
                "control_and_probe_questions",
            ]
        ),
        "Unfunded native questions",
    )
    require(
        sum(w["search_cycles"] for w in work["lifecycle_windows"]) == 4,
        "Search lifecycle count mismatch",
    )
    rti = work["rti"]
    require(
        len(rti["seeds"]) >= 5
        and rti["completed_ipd_per_seed_min"] >= 1000
        and rti["online_soak_minutes"] == 120
        and rti["accelerated_minutes"] == 30,
        "RTI realism/soak scope weakened",
    )
    require(
        rti["maximum_total_ingress_events"] <= 1000000
        and len(rti["seeded_alerts"]) == 7,
        "RTI event/alert contract",
    )
    spending = objects["spend-controls"]
    require(
        spending["native_genie"]["resource_tag"] == {"databricks-product": "genie"}
        and not spending["native_genie"]["additional_resource_tag_filters"],
        "Unsupported native Genie scope",
    )
    require(
        spending["native_genie"]["maximum_build_questions"]
        == genie["total_native_build_questions"],
        "Native spending scope drift",
    )
    require(
        spending["controller"]["limits"]["search_billing_tail_hours_per_cycle"] == 24,
        "Missing search billing tail",
    )
    require(
        spending["controller"]["limits"]["apps_max_aggregate_build_hours"] == 24,
        "App hours drift",
    )
    cost_model = objects["cost-model"]
    require(
        number(cost_model["ceiling_inr"])
        == number(spending["build_ceiling_inr"])
        == 20000,
        "Unapproved budget increase",
    )
    prices = load(root / cost_model["rate_evidence"])
    for name, rate in cost_model["rates"].items():
        if name == "allowance":
            continue
        evidence = prices["rates"].get(name)
        require(
            evidence is not None
            and number(evidence["usd"]) == number(rate["usd"])
            and evidence["unit"] == rate["unit"],
            "Rate/evidence mismatch",
        )
        if evidence["status"] == "RETAIL_API":
            item = evidence["item"]
            require(
                item["currencyCode"] == "USD"
                and item["armRegionName"] == "eastus"
                and number(item["retailPrice"]) == number(rate["usd"])
                and item["type"] == "Consumption",
                "Invalid regional price evidence",
            )
    costs = calculate_costs(cost_model)
    require(costs["build"]["fits"], "Complete build exceeds ceiling")
    require(
        all(m["fits"] for m in costs["monthly"].values()),
        "Monthly profile exceeds target",
    )
    require(
        all(s["matches_expected"] for s in costs["stress_cases"]),
        "Cost stress expectation mismatch",
    )
    require(
        number(
            next(
                l["quantity"] for l in cost_model["build"] if l["id"] == "native-genie"
            )
        )
        == genie["total_native_build_questions"]
        * number(cost_model["usage_uncertainty"]["genie_dbu_per_request"]),
        "Genie cost quantity drift",
    )
    review = objects["design-review"]
    dq = objects["data-quality-contracts"]
    require(
        len(dq["rules"]) == dq["rule_count"] == 55
        and len({r["rule_id"] for r in dq["rules"]}) == 55,
        "55 distinct DQ rule contracts required",
    )
    require(
        all(
            set(rule["tables"]) <= names and rule["invariant"] and rule["gate_action"]
            for rule in dq["rules"]
        ),
        "Unmapped DQ rule",
    )
    require(
        digest(root / dq["rule_source"]) == dq["rule_source_sha256"],
        "DQ rule provenance changed",
    )
    for relative, expected in dq["source_semantic_hashes"].items():
        if with_release or not relative.startswith("data/"):
            require(
                digest(root / relative) == expected,
                "Source semantic provenance changed",
            )
    require(
        len(review["raci"]) == 6 and len(review["decisions"]) == 15, "RACI/ADR coverage"
    )
    require(
        [d["id"] for d in review["decisions"]]
        == [f"ADR-{i:02d}" for i in range(1, 16)],
        "ADR identity mismatch",
    )
    for decision in review["decisions"]:
        text = (root / decision["file"]).read_text(encoding="utf-8")
        require(
            decision["id"] in text
            and all(
                f"**{s}:**" in text
                for s in [
                    "Status",
                    "Context",
                    "Decision",
                    "Alternatives considered",
                    "Consequences and acceptance",
                    "Rollback and evolution",
                ]
            ),
            "Incomplete ADR",
        )
    if require_approval:
        require(
            review["funded_scope_status"] == "APPROVED_BY_USER",
            "Funded scope approval pending; Phase 0 cannot PASS",
        )
        approval = review["funded_scope_approval"]
        require(
            approval["authority"] == "DIRECT_USER_APPROVAL"
            and approval["decision"] == "ACCEPT_REDUCED_POC_SCOPE_KEEP_20000",
            "Wrong scope approval authority",
        )
        for filename, expected in approval["artifact_hashes"].items():
            require(
                digest(root / filename) == expected, "Approved scope artifact changed"
            )
    if with_release:
        for relative, expected in dq["accepted_policy_hashes"].items():
            require(
                digest(root / relative) == expected,
                "Accepted policy provenance changed",
            )
        require(build() == source, "Frozen source matrix differs from accepted release")
        for name, expected in source["input_hashes"].items():
            require(digest(root / name) == expected, "Source/acceptance hash mismatch")
        accepted = load(root / "reviews/dataset-release-v1.1.0-acceptance.json")
        require(
            accepted["status"] == "DATA_ACCEPTED"
            and accepted["descriptor_sha256"] == DESCRIPTOR,
            "Dataset not accepted",
        )
    return {
        "status": "PASS" if require_approval else "PROPOSAL_VALIDATED_NOT_A_PHASE_PASS",
        "costs": costs,
        "source_tables": len(tables),
        "source_columns": sum(len(t["columns"]) for t in tables),
        "business_rows": source["business_rows"],
        "adrs": 15,
        "kpis": 42,
        "ml_dispositions": 13,
        "dq_rules": 55,
        "probes": len(probes),
        "tenant_probe_execution": "NOT_RUN: required in stated later phases; Phase0 verifies design/probe plan only",
        "accepted_release_binding": "CHECKED"
        if with_release
        else "NOT_RUN: use --with-release locally; payload not in CI",
        "scope_approval": review["funded_scope_status"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-release", action="store_true")
    parser.add_argument("--proposal", action="store_true")
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "output/platform-architecture/design-validation.json",
    )
    args = parser.parse_args()
    result = validate_package(
        with_release=args.with_release, require_approval=not args.proposal
    )
    result["evaluated_at"] = datetime.now(timezone.utc).isoformat()
    result["source_sha"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    if args.with_release:
        command = [
            sys.executable,
            "-B",
            "-m",
            "release_tooling.cli",
            "verify",
            "--package",
            str(RELEASE),
            "--descriptor-sha256",
            DESCRIPTOR,
        ]
        checked = subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True, check=True
        )
        result["full_release_verification"] = json.loads(checked.stdout)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k not in {"costs", "full_release_verification"}
            },
            indent=2,
        )
    )
    print(
        json.dumps(
            {
                "build_inr": result["costs"]["build"]["total_inr"],
                "monthly_inr": {
                    k: v["total_inr"] for k, v in result["costs"]["monthly"].items()
                },
                "stress": result["costs"]["stress_cases"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
