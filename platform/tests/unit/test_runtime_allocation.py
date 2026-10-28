import json
from decimal import Decimal

from foundation_support import ROOT
from hcp.control.funding import ENVELOPE_PAISE, LIMITS


def test_runtime_allocation_fits_approved_pool_without_reducing_required_scope():
    policy = json.loads(
        (ROOT / "platform/config/probe-runtime-allocation.json").read_text()
    )
    scope = json.loads(
        (ROOT / "platform/contracts/architecture/test-workloads.json").read_text()
    )
    maximum = sum(units * paise for units, paise in LIMITS.values())
    assert maximum == int(Decimal(policy["maximum_phase2_operation_pool_inr"]) * 100)
    assert maximum <= ENVELOPE_PAISE == 280000
    assert ENVELOPE_PAISE + 25000 == 305000
    assert (
        scope["genie"]["total_native_build_questions"]
        == policy["native_questions_in_entire_build"]
        == 124
    )
    assert (
        policy["control_and_probe_questions_consumed_in_phase2"]
        + policy["control_and_probe_questions_remaining_for_later_control_tests"]
        == scope["genie"]["control_and_probe_questions"]
    )
    assert (
        LIMITS["lakebase_minutes"][0]
        >= policy["lakebase_probe_contract_minutes"]
        + policy["additional_lakebase_cleanup_reserve_minutes"]
    )
    assert Decimal(policy["revised_doubled_genie_stress_inr"]) < Decimal(
        policy["build_ceiling_inr"]
    )
