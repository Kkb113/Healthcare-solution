"""Validate design contracts and hand-calculated design arithmetic; not generated data."""
from __future__ import annotations
import argparse
import calendar
import hashlib
import json
import re
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_contracts(root=ROOT):
    return {name: json.loads((root / f"contracts/phase0/{name}.json").read_text(encoding="utf-8"))
            for name in ["schema", "baseline", "validation-rules", "source-contracts", "clinical-type-matrix", "realism-targets", "scenarios"]}

def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def age_on(dob, on):
    # Feb-29 birthday is Feb-28 in nonleap years, an explicit baseline convention.
    birthday = (dob.month, dob.day)
    if birthday == (2, 29) and not calendar.isleap(on.year):
        birthday = (2, 28)
    return on.year - dob.year - ((on.month, on.day) < birthday)

def run_checks(bundle):
    checks = []
    def check(name, result, detail):
        checks.append({"id": name, "passed": bool(result), "detail": detail})
    schema, b = bundle["schema"], bundle["baseline"]
    tables = schema["tables"]
    by_name = {t["name"]: t for t in tables}
    check("TABLE_COUNT", b["minimum_tables"] <= len(tables) <= b["maximum_tables"] and len(by_name) == len(tables), f"{len(tables)} tables; unique names required")
    planned = sum(t["planned_rows"] for t in tables)
    check("BUDGET", b["minimum_planned_records"] <= planned <= b["maximum_records"], f"Planned={planned:,}; reserve={b['maximum_records']-planned:,}")
    check("BUDGET_SYNC", b["tables"] == {t["name"]: t["planned_rows"] for t in tables}, "Schema and baseline have identical per-table budgets")
    check("POSITIVE_BUDGETS", all(type(t["planned_rows"]) is int and t["planned_rows"] > 0 for t in tables), "Every table has a positive integer envelope")
    days = (date.fromisoformat(b["business_end_date_inclusive"]) - date.fromisoformat(b["business_start_date"])).days + 1
    check("HORIZON", days == 1096 and b["business_start_date"] == "2023-01-01" and b["business_end_date_inclusive"] == "2025-12-31", f"{days} days, 36 months including leap year")
    grace = datetime.fromisoformat(b["final_export_grace_end_utc"].replace("Z", "+00:00"))
    check("EXPORT_GRACE", datetime(2026, 1, 5, tzinfo=timezone.utc) <= grace <= datetime(2026, 1, 15, tzinfo=timezone.utc) and "No post-cutoff" in b["export_grace_policy"], "December close may arrive in January; no extra clinical/payment outcomes are manufactured")
    check("DRIVER_DAYS", b["tables"]["facility_day_driver"] == b["network"]["facilities"] * days, "One facility-day row per local day")
    column_maps = {}
    problems = []
    ref_problems = []
    for t in tables:
        cols = {c["name"]: c for c in t["columns"]}
        column_maps[t["name"]] = cols
        if len(cols) != len(t["columns"]):
            problems.append(t["name"] + ": duplicate column")
        for field in ["grain", "source_authority", "history_policy", "classification"]:
            if not t.get(field):
                problems.append(t["name"] + ": missing " + field)
        for c in t["columns"]:
            if not re.fullmatch(r"STRING|BOOLEAN|DATE|TIMESTAMP|INT|DECIMAL\(18,(2|6)\)", c["type"]):
                problems.append(t["name"] + "." + c["name"] + ": unsupported/non-scalar type")
            if type(c.get("nullable")) is not bool or not c.get("description") or not c.get("authority") or not c.get("correction_policy"):
                problems.append(t["name"] + "." + c["name"] + ": incomplete dictionary")
            if c["type"].startswith("DECIMAL") and not c.get("unit"):
                problems.append(t["name"] + "." + c["name"] + ": decimal lacks unit")
        for pk in t["primary_key"]:
            if pk not in cols or cols[pk]["nullable"]:
                problems.append(t["name"] + ": missing/nullable primary key")
        for unique in t["unique_keys"]:
            if not unique or any(x not in cols for x in unique):
                problems.append(t["name"] + ": invalid unique key")
    for t in tables:
        for c in t["columns"]:
            if "references" not in c:
                continue
            target_table, target_column = c["references"].split(".")
            target = column_maps.get(target_table, {}).get(target_column)
            if target is None:
                ref_problems.append(t["name"] + "." + c["name"] + ": absent target")
            elif target["type"] != c["type"]:
                ref_problems.append(t["name"] + "." + c["name"] + ": type mismatch")
            elif [target_column] != by_name[target_table]["primary_key"]:
                ref_problems.append(t["name"] + "." + c["name"] + ": FK must target row identity; stable-ID lookup is a separate logical rule")
    check("DICTIONARY", not problems, "; ".join(problems) or "All scalar field definitions, units, keys and history metadata complete")
    check("REFERENCES", not ref_problems, "; ".join(ref_problems) or "All physical FKs target matching typed primary keys")
    logical_errors = []
    for logical in schema["logical_reference_contracts"]:
        source_table, source_col = logical["source"].split(".")
        if source_col not in column_maps.get(source_table, {}):
            logical_errors.append(logical["source"])
        targets = [logical["target"]] if "target" in logical else list(logical["target_by_entity_type"].values())
        for target in targets:
            target_table, target_col = target.split(".")
            if target_col not in column_maps.get(target_table, {}) or not logical.get("selection"):
                logical_errors.append(target)
    check("LOGICAL_REFERENCES", not logical_errors, "; ".join(logical_errors) or "Stable identities, typed scopes/crosswalks and source-group predicates are explicitly declared")
    rules = bundle["validation-rules"]["rules"]
    rule_ids = {r["id"] for r in rules}
    rule_errors = []
    if len(rule_ids) != len(rules):
        rule_errors.append("duplicate rule ID")
    for r in rules:
        if any(t not in by_name for t in r["tables"]):
            rule_errors.append(r["id"] + ": unknown table")
        if not all(r.get(k) for k in ["formula_or_invariant", "expected", "owner", "scope", "evidence", "failure_action"]):
            rule_errors.append(r["id"] + ": incomplete acceptance definition")
        if r["severity"] not in {"P0", "P1", "P2"} or not re.fullmatch(r"Phase [2-9]", r["execution_phase"]):
            rule_errors.append(r["id"] + ": invalid severity/execution phase")
        if r["implementation_status"] != "SPECIFIED_NOT_DATA_EXECUTED":
            rule_errors.append(r["id"] + ": premature data validation claim")
    for t in tables:
        expected_rules = {r["id"] for r in rules if t["name"] in r["tables"]}
        if not expected_rules or set(t["rule_ids"]) != expected_rules:
            rule_errors.append(t["name"] + ": rule coverage mismatch")
    check("RULE_CATALOG", not rule_errors, "; ".join(rule_errors) or f"{len(rules)} uniquely owned, scoped rules with full table coverage")
    sources = bundle["source-contracts"]
    source_errors = []
    if {s["target_table"] for s in sources["canonical_exports"]} != set(by_name):
        source_errors.append("missing canonical source coverage")
    for s in sources["canonical_exports"]:
        cols = column_maps.get(s["target_table"], {})
        mappings = {m["target_column"]: m for m in s["field_mappings"]}
        if set(mappings) != set(cols) or not s.get("control_totals") or not s.get("replay"):
            source_errors.append(s["id"] + ": incomplete export contract")
        for name, col in cols.items():
            if name in mappings and mappings[name]["required"] == col["nullable"]:
                source_errors.append(s["id"] + ": required/nullable mismatch")
    for s in sources["source_families"]:
        if s["target_table"] not in by_name or any(x not in column_maps.get(s["target_table"], {}) for x in s["maps"].values()):
            source_errors.append(s["id"] + ": unmapped field/table")
    check("SOURCES", not source_errors, "; ".join(source_errors) or "Canonical fields and Workday/Axiom/ADT layouts map to known columns")
    types = bundle["clinical-type-matrix"]["types"]
    event_types = set(column_maps["clinical_event"]["event_type"]["allowed_values"])
    matrix_ok = set(types) == event_types and all(all(x in column_maps["clinical_event"] for x in v["required"]) and v.get("parent") for v in types.values())
    check("CLINICAL_MATRIX", matrix_ok, "Every event family has explicit required fields, domain and provenance semantics")
    scenarios = bundle["scenarios"]["scenarios"]
    check("SCENARIOS", len(scenarios) == 12 and len({s["id"] for s in scenarios}) == 12 and all(s["minimum_cases"] > 0 and s["fixture_required"] and s["expected"] and set(s["tables"]) <= set(by_name) and set(s["rule_ids"]) <= rule_ids for s in scenarios), "12 causal scenarios with positive coverage, exact fixtures and valid rule dependencies")
    targets = bundle["realism-targets"]["targets"]
    target_errors = []
    for target in targets:
        if not all(target.get(x) for x in ["id", "metric", "denominator", "provenance", "owner"]):
            target_errors.append("incomplete target")
        if "target" in target and abs(sum(target["target"].values()) - 1) > 1e-9:
            target_errors.append(target["id"] + ": shares do not sum to one")
        if "lower" in target and target["lower"] > target["upper"]:
            target_errors.append(target["id"] + ": invalid interval")
        if "target" not in target and "lower" not in target and "tolerance" not in target:
            target_errors.append(target["id"] + ": no acceptance threshold")
    check("REALISM_TARGETS", not target_errors and len(targets) >= 10, "; ".join(target_errors) or "All thresholds preregistered with denominators and assumption/source provenance")
    n, staffing = b["network"], b["staffing"]
    check("BED_CAPACITY", n["facilities"] * n["beds_per_facility"] == n["total_beds"] and n["facilities"] * (n["icu_beds_per_facility"] + n["medical_surgical_beds_per_facility"]) == n["total_beds"], "72 beds = 3 x (4 ICU + 20 medicine/surgery)")
    licensed = n["total_beds"] * days
    occupied = n["planned_bed_days"]
    staffed = n["planned_staffed_bed_days"]
    check("OCCUPANCY", 0 < occupied <= staffed <= licensed and Decimal(str(n["planned_ipd_episodes"])) * Decimal(str(n["ipd_mean_in_window_bed_days"])) == occupied, f"Licensed={licensed}, staffed={staffed}, occupied={occupied}; staffed occupancy={occupied/staffed:.6%}")
    check("OPENING", 0 < n["opening_occupied_beds"] <= n["total_beds"] and n["carry_in_ipd_included"] == n["opening_occupied_beds"], "57 opening occupied beds linked to 57 in-window carry-in encounters")
    check("PATHWAY_ROUTES", abs(sum(p["share"] for p in b["ipd_pathway_mix"]) - 1) < 1e-9 and abs(sum(p["share"] * p["target_mean_days"] for p in b["ipd_pathway_mix"]) - 5.21) < 1e-9 and sum(b["admission_routes"].values()) == n["planned_ipd_episodes"], "Case mix sums to one; 5.21-day completed-duration assumption and all 12,000 admission routes reconciled")
    check("ENCOUNTER_ROWS", sum(n["distinct_encounters"].values()) + n["opening_closed_encounters"] + n["encounter_lifecycle_revision_rows"] + n["encounter_correction_rows"] == b["tables"]["encounter"], "56k intersecting +2k opening-only +68k lifecycle +4k correction =130k")
    check("PATIENT_WORKER_ROWS", n["distinct_patients"] + n["patient_revision_rows"] == b["tables"]["patient"] and n["distinct_workers"] + n["worker_revision_rows"] == b["tables"]["worker_assignment"], "Stable persons plus versions reconcile to table envelopes")
    check("CLINICAL_ROWS", sum(b["clinical_event_budget"].values()) == b["tables"]["clinical_event"], "Every event family plus revisions counted")
    check("CLINICAL_BUDGET_FAMILIES", set(b["clinical_event_budget"]) == event_types | {"REVISION_ROWS"} and all(x > 0 for x in b["clinical_event_budget"].values()), "No omitted/zero clinical event family or uncounted revision class")
    check("BED_EVENT_ROWS", sum(b["bed_event_budget"].values()) == b["tables"]["bed_event"] and b["bed_event_budget"]["opening"] == n["total_beds"], "All opening/transitions/capacity/correction rows counted")
    intervals = b["bed_interval_design"]
    check("BED_INTERVALS", intervals["distinct_ipd"] + intervals["extra_transfers"] == intervals["total_intervals"] and intervals["total_intervals"] * 4 <= b["bed_event_budget"]["occupy_vacate_clean_ready"], "15k intervals and allowance for four primary transitions each")
    turnover_days = Decimal(str(intervals["total_intervals"])) * Decimal(str(intervals["average_turnaround_hours"])) / 24
    check("TURNAROUND", occupied + turnover_days <= staffed, f"Turnaround allowance {turnover_days} bed-days fits staffed slack")
    shift_rows = staffing["distinct_work_shifts"] + staffing["leave_unavailable_blocks"] + staffing["revision_rows"]
    nursing = staffing["distinct_work_shifts"] * staffing["rn_share_of_work_shifts"] * staffing["productive_hours_per_work_shift"]
    nursing_required = occupied * staffing["modeled_rn_hours_per_patient_day"]
    annual_hours = staffing["distinct_work_shifts"] * staffing["shift_hours"] / 3
    annual_capacity = staffing["rostered_workers"] * staffing["mean_rostered_worker_fte"] * staffing["annual_paid_hours_per_fte"]
    check("STAFF_ROWS", shift_rows == b["tables"]["staff_shift"], "52k work +4k leave/unavailable +14k versions =70k rows")
    check("STAFF_FEASIBILITY", nursing >= nursing_required and annual_hours <= annual_capacity and 0 < staffing["rn_share_of_work_shifts"] <= 1, f"RN supply={nursing:.0f}h, modeled requirement={nursing_required:.0f}h; annual worked={annual_hours:.0f}h <= contracted capacity={annual_capacity:.0f}h")
    cb = b["claim_budget"]
    check("CLAIM_ROWS", cb["current_period_originals"] + cb["opening_originals"] == b["tables"]["claim"] and sum(cb["events"].values()) == b["tables"]["claim_event"], "54k new +2k opening claims; all 160k lifecycle events budgeted")
    check("CHARGE_LINE_CAPACITY", b["tables"]["claim_line"] <= b["tables"]["service_charge"] and b["tables"]["claim_line"] >= b["tables"]["claim"], "One-charge/one-original-line baseline is feasible without duplicating charges")
    check("FINANCIAL_SERIES", b["finance_series"]["financial_row_budget"] == b["tables"]["finance_monthly"], "Selected series, not unbudgeted dense account/vintage Cartesian product")
    grid = b["finance_row_breakdown"]
    independently_computed_grid = {
        "actual_pnl_45_centers_11_accounts_36_months": b["tables"]["cost_center"] * len(b["account_sets"]["pnl"]) * 36,
        "actual_balance_3_control_centers_6_accounts_36_months": n["facilities"] * len(b["account_sets"]["balance"]) * 36,
        "actual_stats_15_centers_4_measures_36_months": 15 * 4 * 36,
        "original_budget_45_centers_6_accounts_36_months": b["tables"]["cost_center"] * len(b["account_sets"]["budget"]) * 36,
        "midyear_budget_45_centers_6_accounts_12_months": b["tables"]["cost_center"] * len(b["account_sets"]["budget"]) * 12,
        "forecast_12_selected_centers_2_accounts_12_vintages_3_months": n["facilities"] * 4 * 2 * 12 * 3,
        "budget_stats_3_centers_4_measures_36_months": n["facilities"] * 4 * 36,
        "correction_vintage_allowance": 1116}
    check("FINANCIAL_GRID", grid == independently_computed_grid and sum(grid.values()) == b["tables"]["finance_monthly"], "Account/center/month/vintage products independently recomputed, not just a matching grand total")
    check("POSTING_ROWS", sum(b["financial_posting_budget"].values()) == b["tables"]["financial_posting"], "All source, opening and monthly cost-pool reclassification journal lines counted")
    check("POOL_CLOSE_LINES", b["financial_posting_budget"]["monthly_pool_close"] >= b["tables"]["cost_center"] * 36 * 4 * 2, "Up to four categories per center/month have counted debit and credit reclassification lines")
    check("ALLOCATION_FEASIBILITY", sum(b["cost_allocation_components"].values()) <= b["tables"]["cost_allocation"] and b["cost_allocation_components"]["ipd_four_categories"] == n["planned_ipd_episodes"] * 4 and b["cost_allocation_components"]["ed_op_average_2_25_categories"] == (n["distinct_encounters"]["ED"] + n["distinct_encounters"]["OPD"]) * 2.25, "Patient/category/month/transfer allocations, nonpatient/residual and revision allowance fit 180k rows")
    # Small independent design examples, not generated patient rows or a Phase 1 harness.
    census = 57 + 18 + 2 - 15 - 1
    stock = Decimal("100") + Decimal("25") - Decimal("18") - Decimal("2")
    debit = money("100.01") + money("25.00")
    credit = money("90.00") + money("35.01")
    check("HAND_CALCULATIONS", census == 61 and stock == 105 and debit == credit and money("0.005") == Decimal("0.01"), "Independent census/stock/debit-credit/rounding arithmetic")
    check("AGE_FIXTURES", age_on(date(1980, 10, 24), date(2023, 10, 23)) == 42 and age_on(date(1980, 10, 24), date(2023, 10, 24)) == 43 and age_on(date(2004, 2, 29), date(2023, 2, 28)) == 19, "Birthday and configured leap-day convention")
    check("SOLUTION_LOCK", b["solution_status"] == "BLOCKED_FOR_SOLUTION" and "Phase 1" in b["next_phase"], "No generator, datasets, models, dashboards or solution deployment authorized by these design checks")
    return checks

def report(root=ROOT):
    bundle = load_contracts(root)
    checks = run_checks(bundle)
    schema = bundle["schema"]
    ddl = (root / "contracts/phase0/databricks-schema.sql").read_text(encoding="utf-8")
    dictionary = (root / "docs/phase-0/data-dictionary.md").read_text(encoding="utf-8")
    expected_fks = sum("references" in c for t in schema["tables"] for c in t["columns"])
    artifact_ok = ddl.count("CREATE TABLE IF NOT EXISTS") == len(schema["tables"]) and ddl.count("PRIMARY KEY (") == len(schema["tables"]) and ddl.count("FOREIGN KEY (") == expected_fks and all(dictionary.count("## " + t["name"] + "\n") == 1 for t in schema["tables"])
    checks.append({"id": "OFFLINE_SCHEMA_ARTIFACTS", "passed": artifact_ok, "detail": f"Offline DDL has {len(schema['tables'])} PK definitions and {expected_fks} FK declarations; dictionary covers every table. No live DDL executed."})
    broken = []
    document_count = 0
    for doc in root.rglob("*.md"):
        if ".git" in doc.parts or ".venv" in doc.parts:
            continue
        document_count += 1
        content = doc.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            target = target.strip("<>").split("#", 1)[0]
            if not target or re.match(r"[a-zA-Z]+://", target):
                continue
            if not (doc.parent / target).exists():
                broken.append(str(doc.relative_to(root)) + " -> " + target)
    checks.append({"id": "DOCUMENT_LINKS", "passed": not broken, "detail": "; ".join(broken) or f"All local Markdown links resolve across {document_count} documents"})
    gate = json.loads((root / "evidence/phase-0/gate.json").read_text(encoding="utf-8"))
    total = sum(t["planned_rows"] for t in schema["tables"])
    summary_docs = [(root / p).read_text(encoding="utf-8") for p in ["README.md", "docs/phase-0/README.md", "docs/phase-0/review-and-gate.md"]]
    gate_ok = gate["planned_records"] == total and gate["canonical_business_tables"] == len(schema["tables"]) and gate["reserve_records"] == bundle["baseline"]["maximum_records"] - total and gate["actual_generated_business_records"] == 0 and gate["solution_status"] == "BLOCKED_FOR_SOLUTION" and all(f"{total:,}" in text for text in summary_docs)
    checks.append({"id": "GATE_ARTIFACTS", "passed": gate_ok, "detail": "Gate/README/review agree with the contract budget, zero generated records and blocked solution scope"})
    files = sorted((root / "contracts/phase0").glob("*"))
    hashes = {str(p.relative_to(root)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
    return {"phase": 0, "validation_scope": "Contract integrity and independently calculated design feasibility only; no generated-data validations have been executed.",
            "baseline_version": bundle["baseline"]["version"], "passed": all(c["passed"] for c in checks),
            "check_count": len(checks), "checks": checks, "contract_sha256": hashes,
            "business_tables": len(bundle["schema"]["tables"]), "planned_records": sum(t["planned_rows"] for t in bundle["schema"]["tables"]),
            "actual_generated_records": 0, "solution_status": "BLOCKED_FOR_SOLUTION"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Write design-check evidence JSON.")
    args = parser.parse_args()
    result = report()
    for check in result["checks"]:
        print(("PASS" if check["passed"] else "FAIL") + " " + check["id"] + ": " + check["detail"])
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{sum(c['passed'] for c in result['checks'])}/{len(result['checks'])} design checks passed; generated business records=0")
    raise SystemExit(0 if result["passed"] else 1)

if __name__ == "__main__":
    main()
