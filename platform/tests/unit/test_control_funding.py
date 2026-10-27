import pytest
from hcp.control.funding import claim
from hcp.control.state import initial_state


def test_claims_are_cumulative_and_idempotent_across_windows():
    state = claim(initial_state(), "search-one", "search_cycles", 1)
    assert claim(state, "search-one", "search_cycles", 1) == state
    state = claim(state, "search-two", "search_cycles", 1)
    with pytest.raises(PermissionError, match="exhausted"):
        claim(state, "search-three", "search_cycles", 1)
    with pytest.raises(PermissionError, match="identity"):
        claim(state, "search-one", "sql_minutes", 1)
    assert initial_state().get("cost_claims") is None


def test_pooled_cost_limit_is_separate_from_individual_meter_caps(monkeypatch):
    monkeypatch.setattr("hcp.control.funding.ENVELOPE_PAISE", 100)
    with pytest.raises(PermissionError, match="phase envelope"):
        claim(initial_state(), "search-with-unfunded-pool", "search_cycles", 1)


@pytest.mark.parametrize("units", [True, 0, -1, 1.5, "1"])
def test_bad_quantities_fail_closed(units):
    with pytest.raises(ValueError):
        claim(initial_state(), "bad", "sql_minutes", units)
