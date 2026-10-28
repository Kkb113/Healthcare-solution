"""Match real provider usage to the retained, already-completed tenant probes.

This closes attribution, not the Azure invoice. No reservations are released and
neither missing records nor a missing price can become a zero-cost assertion.
"""

import json
from decimal import Decimal

from foundation_support import ROOT, load, now, save

JOBS = "658faa8a-72bf-4285-bf4c-3cd25778ac5f"
PROJECT = "14fc3c6c-8800-4de9-a5e1-5e9d2a1fb3a5"
PIPELINE = "2b801446-8bee-45a5-ac51-6ef72f7912c8"


def parsed(row, column):
    return json.loads(row.get(column) or "{}")


def reconcile(rows):
    selected = {
        "serverless_job": [
            r
            for r in rows
            if r["billing_origin_product"] == "JOBS"
            and parsed(r, "resource_metadata").get("job_id") == "619642680220846"
            and parsed(r, "caller_metadata").get("run_as") == JOBS
        ],
        "serverless_pipeline": [
            r
            for r in rows
            if r["billing_origin_product"] == "DLT"
            and parsed(r, "resource_metadata").get("dlt_pipeline_id")
            == "8d191903-9e6d-43b1-b33a-f7e164c209e0"
            and parsed(r, "caller_metadata").get("run_as") == JOBS
        ],
        "lakebase_compute": [
            r
            for r in rows
            if r["billing_origin_product"] == "LAKEBASE"
            and parsed(r, "resource_metadata").get("project_id") == PROJECT
            and "DATABASE_SERVERLESS_COMPUTE" in r["sku_name"]
        ],
        "lakebase_storage": [
            r
            for r in rows
            if r["billing_origin_product"] == "LAKEBASE"
            and parsed(r, "resource_metadata").get("project_id") == PROJECT
            and r["usage_unit"] == "DSU"
        ],
        "lakebase_sync": [
            r
            for r in rows
            if r["billing_origin_product"] == "LAKEBASE"
            and parsed(r, "resource_metadata").get("dlt_pipeline_id") == PIPELINE
            and parsed(r, "caller_metadata").get("run_as") == JOBS
        ],
        "native_genie_paid_caller": [
            r
            for r in rows
            if r["billing_origin_product"] == "GENIE"
            and parsed(r, "caller_metadata").get("run_as") == JOBS
            and parsed(r, "resource_metadata").get("genie", {}).get("agent_id")
            == "01f1d21c4cf91a5a83edbadce06fa7fb"
            and r["sku_name"] != "GENIE_FREE_USAGE"
        ],
    }
    cases = {}
    for name, matches in selected.items():
        if not matches:
            raise ValueError(f"Missing attributable provider rows for {name}")
        units = {r["usage_unit"] for r in matches}
        if len(units) != 1 or any(
            r.get("usd_list_unit_price") is None for r in matches
        ):
            raise ValueError("Incompatible units or unmatched provider prices")
        quantity = sum((Decimal(r["net_quantity"]) for r in matches), Decimal(0))
        cost = sum(
            (
                Decimal(r["net_quantity"]) * Decimal(r["usd_list_unit_price"])
                for r in matches
            ),
            Decimal(0),
        )
        if quantity <= 0 or cost <= 0:
            raise ValueError("No positive attributable consumption")
        cases[name] = {
            "status": "PASS",
            "usage_unit": units.pop(),
            "net_quantity": str(quantity),
            "usd_list_cost": str(cost),
            "provider_records": sum(int(r["provider_records"]) for r in matches),
            "rows": matches,
        }
    # Keep the two-DBU/question planning bound despite this one small pilot.
    if Decimal(cases["native_genie_paid_caller"]["net_quantity"]) > 2:
        raise ValueError("Measured pilot exceeds the remaining Genie cost model")
    automated = sum(
        Decimal(cases[k]["net_quantity"])
        for k in ["serverless_job", "serverless_pipeline", "lakebase_sync"]
    )
    if automated > 4:
        raise ValueError("Probe automated DBU allowance exceeded")
    if Decimal(cases["lakebase_compute"]["net_quantity"]) > Decimal(35) / 60 * 2:
        raise ValueError("Measured Lakebase compute exceeds reserved allowance")
    return {
        "status": "PASS",
        "observed_at": now(),
        "cases": cases,
        "automated_probe_dbu": str(automated),
        "remaining_cost_assumptions": {
            "native_genie_dbu_per_question": "2; retained conservative assumption, pilot is not a workload-wide bound",
            "lakebase_maximum_cu": 2,
            "lakebase_planning_database_dbu_per_hour": "2; retained upper engineering allowance, not a measured universal CU conversion",
            "database_sku_usd_per_dbu": "0.26",
            "sync_sku_usd_per_dbu": "0.45",
        },
        "provider_attribution_complete": True,
        "invoice_final": False,
        "reservations_released": False,
        "native_search_full_tail_holds_retained": True,
        "later_phase_full_workload_pilots_required": True,
    }


def main():
    source = load(ROOT / "output/platform-foundation/probe-billing.json")
    report = reconcile(source["rows"])
    report["source_statement_id"] = source["statement_id"]
    report["source_observed_at"] = source["observed_at"]
    save(ROOT / "output/platform-foundation/probe-billing-reconciliation.json", report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "attributed_components": len(report["cases"]),
                "automated_probe_dbu": report["automated_probe_dbu"],
                "reservations_released": False,
            }
        )
    )


if __name__ == "__main__":
    main()
