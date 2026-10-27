import pytest
from hcp.control.funding import claim
from hcp.control.state import initial_state


def test_claims_are_cumulative_and_idempotent_across_windows():
    state = claim(initial_state(), "search-one", "search_cycles", 1)
    assert claim(state, "search-one", "search_cycles", 1) == state
    with pytest.raises(PermissionError, match="exhausted"):
        claim(state, "search-two", "search_cycles", 1)
    with pytest.raises(PermissionError, match="identity"):
        claim(state, "search-one", "sql_minutes", 1)
    assert initial_state().get("cost_claims") is None


def test_pooled_cost_limit_is_separate_from_individual_meter_caps():
    state = initial_state()
    for meter, units in [
        ("sql_minutes", 90),
        ("automated_dbu_milli", 4000),
        ("app_minutes", 30),
        ("search_cycles", 1),
        ("lakebase_minutes", 60),
        ("serving_minutes", 60),
    ]:
        state = claim(state, meter, meter, units)
    with pytest.raises(PermissionError, match="phase envelope"):
        claim(state, "expensive-remainder", "genie_questions", 3)


@pytest.mark.parametrize("units", [True, 0, -1, 1.5, "1"])
def test_bad_quantities_fail_closed(units):
    with pytest.raises(ValueError):
        claim(initial_state(), "bad", "sql_minutes", units)
