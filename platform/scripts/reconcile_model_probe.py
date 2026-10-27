"""Consolidate bounded compatibility, scoped access, capacity and cost evidence."""

import hashlib
import json
import sys
from decimal import Decimal

from foundation_support import ROOT, load, now, save

sys.path.insert(0, str(ROOT / "platform/src"))


def main():
    directory = ROOT / "output/platform-foundation"
    tools = load(directory / "model-tool-roundtrip-format-failure.json")
    formats = load(directory / "model-responses-probe.json")
    capacity = load(directory / "luna-current-capacity.json")
    profile = load(ROOT / "platform/config/luna-capacity-profile.json")
    external = load(directory / "external-budget-probe.json")
    assert formats["status"] == "FORMAT_COMPATIBILITY_PASS"
    accepted = [
        row for item in [tools, formats] for row in item["requests"] if "usage" in row
    ]
    assert {row["case"] for row in accepted} == {
        "tool_request",
        "tool_result",
        "json_schema",
        "stream",
    }
    assert all(row["model"] == "gpt-6-luna" for row in accepted)
    assert any(
        row.get("case") == "no_grant" and row.get("status") in {401, 403, 404}
        for row in tools["requests"]
    )
    assert all(
        "oauth_secret_revoked" in item["cleanup"]
        and "temporary_principal_deleted" in item["cleanup"]
        for item in [tools, formats]
    )
    assert capacity["model"]["name"] == profile["model"]
    assert capacity["model"]["version"] == profile["revision"]
    assert capacity["sku"]["name"] == profile["deployment_type"] == "DataZoneStandard"
    assert (
        capacity["sku"]["capacity"] == 100
        and capacity["provisioningState"] == "Succeeded"
    )
    rates = {
        r["key"]: Decimal(str(r["count"]))
        for r in capacity["rateLimits"]
        if r["renewalPeriod"] == 60
    }
    per_minute = Decimal(profile["offered_turns_per_minute"]) / 100
    request_units = token_units = 0
    for row in profile["mix"]:
        request_units += row["turns_per_100"] * len(
            row["estimated_input_caps_per_call"]
        )
        token_units += row["turns_per_100"] * (
            sum(row["estimated_input_caps_per_call"]) + sum(row["output_caps_per_call"])
        )
    multiplier = 1 + Decimal(profile["headroom_fraction"])
    assert token_units * per_minute * multiplier <= rates["token"]
    assert request_units * per_minute * multiplier <= rates["request"]
    inputs = sum(row["usage"]["input_tokens"] for row in accepted)
    outputs = sum(row["usage"]["output_tokens"] for row in accepted)
    assert inputs <= 24000 and outputs <= 3072
    assert external["status"] == "UNSUPPORTED_EXTERNAL_BETA"
    report = {
        "status": "COMPATIBILITY_AND_DECLARED_CAPACITY_PASS",
        "observed_at": now(),
        "model": profile["model"],
        "revision": profile["revision"],
        "accepted_fixture_calls": len(accepted),
        "input_tokens": inputs,
        "output_tokens": outputs,
        "permission_denial_positive_control": True,
        "tool_arithmetic_assertion": "Original bounded runner asserted function arguments 17+25 and final answer 42 before recording tool_result",
        "json_stream_tool_required_cases": [r["case"] for r in accepted],
        "sizing": {
            "concurrent_clients": 10,
            "completed_benchmark_minimum": 100,
            "offered_turns_per_minute": 20,
            "tpm_including_twenty_percent_headroom": str(
                token_units * per_minute * multiplier
            ),
            "rpm_including_twenty_percent_headroom": str(
                request_units * per_minute * multiplier
            ),
        },
        "live_429_observed": False,
        "retry_and_fail_closed_test_suite": "platform/tests/unit/test_request_policy.py",
        "application_budget_contract": "platform/config/application-budget-probe.json",
        "external_gateway_beta": external["status"],
        "limits": "Nominal per-intent capped POC profile only. Quality, true ten-client full-answer latency, quota estimator and rolling-window dispatch controls remain mandatory in Phase10; no guarantee at all global token ceilings.",
        "all_phase2_holds_retained": True,
        "billing_settled": False,
    }
    names = [
        "model-tool-roundtrip-format-failure.json",
        "model-responses-probe.json",
        "luna-current-capacity.json",
        "external-budget-probe.json",
    ]
    report["input_hashes"] = {
        name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
        for name in names
    }
    save(directory / "model-probe-reconciliation.json", report)
    print(json.dumps({"status": report["status"], "sizing": report["sizing"]}))


if __name__ == "__main__":
    main()
