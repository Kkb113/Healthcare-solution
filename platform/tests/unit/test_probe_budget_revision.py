from decimal import Decimal

from foundation_support import ROOT, load
from hcp.control.funding import ENVELOPE_PAISE, LIMITS


def test_approved_contingency_reallocation_preserves_entire_build_ceiling():
    revision = load(ROOT / "platform/config/probe-budget-revision.json")
    assert revision["status"] == "APPROVED"
    assert revision["test_scope_reduction"] is False
    assert (
        revision["proposed_build_ceiling_inr"]
        == revision["original_build_ceiling_inr"]
        == "20000.00"
    )
    for original, revised in [
        ("original_model_estimate_inr", "revised_model_estimate_inr"),
        ("original_genie_stress_estimate_inr", "revised_genie_stress_estimate_inr"),
    ]:
        actual = (
            Decimal(revision[original])
            + Decimal(revision["additional_search_upper_cost_inr"])
            - Decimal(revision["contingency_reallocation_inr"])
        )
        assert actual == Decimal(revision[revised]) < Decimal(20000)
    assert Decimal(revision["remaining_build_contingency_inr"]) == Decimal(650)
    # All individual maximum reservations fit the amended phase envelope.
    assert sum(units * price for units, price in LIMITS.values()) <= ENVELOPE_PAISE
