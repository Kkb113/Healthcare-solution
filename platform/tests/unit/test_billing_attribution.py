import copy
import json
from types import SimpleNamespace

import pytest
from foundation_ledger import exposure, initial_ledger, update_snapshot
from foundation_support import CONFIG, load
from reconcile_probe_billing import JOBS, PIPELINE, PROJECT, reconcile


def provider_rows():
    rows = []
    for product, meta, unit in [
        ("JOBS", {"job_id": "619642680220846"}, "DBU"),
        ("DLT", {"dlt_pipeline_id": "8d191903-9e6d-43b1-b33a-f7e164c209e0"}, "DBU"),
        ("LAKEBASE", {"project_id": PROJECT}, "DBU"),
        ("LAKEBASE", {"project_id": PROJECT}, "DSU"),
        ("LAKEBASE", {"dlt_pipeline_id": PIPELINE}, "DBU"),
        ("GENIE", {"genie": {"agent_id": "01f1d21c4cf91a5a83edbadce06fa7fb"}}, "DBU"),
    ]:
        rows.append(
            {
                "billing_origin_product": product,
                "resource_metadata": json.dumps(meta),
                "caller_metadata": json.dumps({"run_as": JOBS}),
                "net_quantity": "0.1",
                "usd_list_unit_price": "0.26",
                "usage_unit": unit,
                "sku_name": "PREMIUM_DATABASE_SERVERLESS_COMPUTE"
                if "project_id" in meta and unit == "DBU"
                else "fixture",
                "provider_records": "1",
            }
        )
    return rows


def test_all_required_billing_is_attributable_without_releasing_holds():
    result = reconcile(provider_rows())
    assert result["status"] == "PASS" and len(result["cases"]) == 6
    assert result["invoice_final"] is False and result["reservations_released"] is False


@pytest.mark.parametrize(
    "edit",
    [
        lambda rows: rows.pop(),
        lambda rows: rows[-1].update(billing_origin_product="AI_GATEWAY"),
        lambda rows: rows[-1].update(caller_metadata='{"run_as":"unrelated"}'),
        lambda rows: rows[-1].update(sku_name="GENIE_FREE_USAGE"),
        lambda rows: rows[-1].update(usd_list_unit_price=None),
        lambda rows: rows[-1].update(net_quantity="0"),
        lambda rows: rows[-1].update(net_quantity="3"),
        lambda rows: rows[0].update(net_quantity="5"),
        lambda rows: rows[2].update(net_quantity="2"),
    ],
)
def test_missing_ambiguous_unpriced_or_over_budget_usage_blocks_reconciliation(edit):
    rows = copy.deepcopy(provider_rows())
    edit(rows)
    with pytest.raises(ValueError):
        reconcile(rows)


def test_inr_snapshot_uses_no_fx_multiplier_and_preserves_larger_usd_history():
    scope = "subscriptions/fixture"
    ledger = initial_ledger(load(CONFIG))
    old = {
        "scope": scope,
        "currency": "USD",
        "positive_cost_usd": "10",
        "credits_usd": "-1",
        "period_start": "2026-10-01",
    }
    ledger = update_snapshot(ledger, scope, old, {scope})
    revised = {
        "scope": scope,
        "currency": "INR",
        "positive_cost_inr": "100",
        "credits_inr": "-200",
        "period_start": "2026-10-01",
    }
    ledger = update_snapshot(ledger, scope, revised, {scope})
    assert exposure(ledger)["observed_cost_with_planning_reserves_paise"] == 118000
    revised["positive_cost_inr"] = "2000"
    ledger = update_snapshot(ledger, scope, revised, {scope})
    assert exposure(ledger)["observed_cost_with_planning_reserves_paise"] == 236000
    assert exposure(ledger)["outstanding_reservations_paise"] == 25000


def test_expired_demo_window_deletes_search_without_any_workload_query(monkeypatch):
    from hcp.control.state import initial_state
    from platform_control import guard

    state = initial_state()
    resource = {
        "kind": "azure_search",
        "id": "scoped-fixture",
        "running": True,
        "owned": True,
    }
    store = SimpleNamespace(read=lambda: (state, "etag"))
    monkeypatch.setattr("platform_control.inventory", lambda *_: [resource])
    calls = []
    monkeypatch.setattr(
        "platform_control.down", lambda *a, **k: calls.append(k) or {"status": "PASS"}
    )
    assert guard(store, object())["status"] == "PASS"
    assert calls == [{"expected_session_id": None}]


def test_managed_identity_denial_credential_is_cleared_without_app_secrets(monkeypatch):
    from probe_azure_search import denied_principal

    token = SimpleNamespace(azure_aad=SimpleNamespace(aad_token="fixture-token"))
    credentials = SimpleNamespace(
        generate_temporary_service_credential=lambda *a, **k: token
    )
    monkeypatch.setattr(
        "platform_control.workspace_client",
        lambda: SimpleNamespace(credentials=credentials),
    )
    client = SimpleNamespace(_token=None)
    monkeypatch.setattr("probe_azure_search.data_client", lambda: client)
    with denied_principal() as actual:
        assert actual._token == "fixture-token"
    assert token.azure_aad.aad_token is None and client._token is None
