"""Failure-oriented infrastructure and durable-spend tests; no cloud compute."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "platform/scripts"))
from configure_foundation_identity import (
    CONFIGURATION,
    OPERATOR,
    check_preservation,
    identity_digest,
    scope_schema,
    validate_config,
    validate_schema,
)
from foundation_ledger import (
    BlobLedger,
    exposure,
    initial_ledger,
    reserve,
    to_paise,
    update_snapshot,
)
from foundation_support import CONFIG, AzureRest, CloudHttpError, load, review_plan
from verify_foundation import validate_budgets, validate_storage


@pytest.fixture
def config():
    return load(CONFIG)


@pytest.fixture
def ledger(config):
    return initial_ledger(config)


def snapshot(scope, amount="1", credits="0"):
    return {
        "scope": scope,
        "currency": "USD",
        "positive_cost_usd": amount,
        "credits_usd": credits,
        "period_start": "2026-10-01",
    }


@pytest.mark.parametrize(
    "amount,fx,tax",
    [
        ("-1", "100", "0.18"),
        ("NaN", "100", "0.18"),
        ("Infinity", "100", "0.18"),
        ("1", "0", "0.18"),
        ("1", "100", "-0.1"),
    ],
)
def test_invalid_price_fails_closed(amount, fx, tax):
    with pytest.raises(ValueError):
        to_paise(amount, fx, tax)


def test_paise_rounds_up_not_down():
    assert to_paise("0.00001") == 1
    assert to_paise("1") == 11800


def test_pending_costs_do_not_expire_or_reset(ledger):
    ledger["created_at"] = "2025-01-01T00:00:00Z"
    ledger["updated_at"] = "2027-01-01T00:00:00Z"
    assert exposure(ledger)["outstanding_reservations_paise"] == 25000
    assert exposure(ledger)["billing_status"] == "PROVISIONAL"


def test_idempotent_reservation_conflict_and_no_mutation(ledger):
    changed = reserve(ledger, "test", 5000, 2)
    assert reserve(changed, "test", 5000, 2) == changed
    assert "test" not in ledger["reservations"]
    with pytest.raises(ValueError, match="Conflicting"):
        reserve(changed, "test", 6000, 2)


@pytest.mark.parametrize("amount", [-1, 0, True, 1.5, "100"])
def test_bad_reservation_rejected(ledger, amount):
    with pytest.raises(ValueError):
        reserve(ledger, "test", amount, 2)


@pytest.mark.parametrize("amount", [-100, True, 1.5])
def test_corrupt_persisted_reservation_rejected(ledger, amount):
    ledger["reservations"]["prerequisite-readiness"]["paise"] = amount
    with pytest.raises(ValueError):
        exposure(ledger)


def test_unverified_settlement_cannot_reduce_cost(ledger):
    ledger["reservations"]["prerequisite-readiness"]["status"] = "RECONCILED"
    with pytest.raises(ValueError):
        exposure(ledger)


def test_budget_admission_and_pause(ledger):
    with pytest.raises(ValueError, match="Funded window"):
        reserve(ledger, "too-large", 2000000, 2)
    ledger = reserve(ledger, "pending", 1775000, 2)
    assert exposure(ledger)["pause_new_work"]
    with pytest.raises(ValueError, match="pause threshold"):
        reserve(ledger, "further", 1, 2)


def test_whole_period_snapshot_replaces_not_adds_and_credits_not_discounted(ledger):
    scope = "subscriptions/test"
    first = update_snapshot(ledger, scope, snapshot(scope, "1", "-10"), {scope})
    second = update_snapshot(first, scope, snapshot(scope, "2", "-100"), {scope})
    assert exposure(second)["observed_cost_with_planning_reserves_paise"] == 23600
    assert exposure(second)["outstanding_reservations_paise"] == 25000


def test_empty_billing_cannot_erase_previously_observed_spend(ledger):
    scope = "subscriptions/test"
    observed = update_snapshot(ledger, scope, snapshot(scope, "10"), {scope})
    delayed = update_snapshot(observed, scope, snapshot(scope, "0"), {scope})
    assert exposure(delayed)["observed_cost_with_planning_reserves_paise"] == 118000
    assert delayed["snapshots"][scope]["reported_positive_cost_usd"] == "0"


def test_calendar_reset_cannot_hide_build_cost(ledger):
    scope = "subscriptions/test"
    with pytest.raises(ValueError, match="fixed project start"):
        update_snapshot(
            ledger, scope, snapshot(scope) | {"period_start": "2026-11-01"}, {scope}
        )


@pytest.mark.parametrize(
    "change",
    [
        {"currency": "EUR"},
        {"positive_cost_usd": "-1"},
        {"credits_usd": "NaN"},
        {"credits_usd": "1"},
        {"scope": "wrong"},
    ],
)
def test_invalid_snapshot_does_not_write(ledger, change):
    value = snapshot("subscriptions/test") | change
    with pytest.raises(ValueError):
        update_snapshot(ledger, "subscriptions/test", value, {"subscriptions/test"})
    assert ledger["snapshots"] == {}


class MemoryBlob:
    """Emulates server CAS, with an optional competing writer before PUT."""

    def __init__(self, content, races=0, unavailable=False, missing_etag=False):
        self.content = copy.deepcopy(content)
        self.version = 1
        self.races = races
        self.unavailable = unavailable
        self.missing_etag = missing_etag
        self.writes = 0

    def request(self, method, url, *, body=None, headers=None):
        if self.unavailable:
            raise CloudHttpError(503, "Unavailable")
        if method == "GET":
            return (
                200,
                {} if self.missing_etag else {"ETag": str(self.version)},
                json.dumps(self.content).encode(),
            )
        if headers.get("If-None-Match"):
            raise CloudHttpError(412, "BlobExists")
        if self.races:
            self.races -= 1
            self.version += 1
            self.content = reserve(self.content, f"other-{self.version}", 100, 2)
        if headers.get("If-Match") != str(self.version):
            raise CloudHttpError(412, "ConditionNotMet")
        self.content = copy.deepcopy(body)
        self.version += 1
        self.writes += 1
        return 201, {}, b""


def test_existing_ledger_init_does_not_reset(config, ledger):
    ledger = reserve(ledger, "existing", 1000, 2)
    client = MemoryBlob(ledger)
    actual, created = BlobLedger(config, client).initialize()
    assert not created and actual == ledger and client.writes == 0


def test_concurrent_ledger_retry_preserves_both_reservations(config, ledger):
    client = MemoryBlob(ledger, races=1)
    result = BlobLedger(config, client).transact(
        lambda old: reserve(old, "mine", 1000, 2)
    )
    assert {"mine", "other-2"} <= set(result["reservations"])
    assert client.writes == 1


def test_concurrent_retry_exhaustion_fails_without_overwrite(config, ledger):
    client = MemoryBlob(ledger, races=10)
    with pytest.raises(RuntimeError, match="bounded retries"):
        BlobLedger(config, client).transact(
            lambda old: reserve(old, "mine", 1000, 2), attempts=2
        )
    assert "mine" not in client.content["reservations"] and client.writes == 0


@pytest.mark.parametrize(
    "options,exception",
    [({"unavailable": True}, CloudHttpError), ({"missing_etag": True}, ValueError)],
)
def test_unavailable_ledger_admits_no_write(config, ledger, options, exception):
    client = MemoryBlob(ledger, **options)
    with pytest.raises(exception):
        BlobLedger(config, client).transact(lambda old: reserve(old, "mine", 1000, 2))
    assert client.writes == 0


@pytest.mark.parametrize("field", ["ceiling_paise", "reservations"])
def test_ledger_transaction_cannot_reset_budget_or_reservations(config, ledger, field):
    client = MemoryBlob(ledger)

    def corrupt(value):
        value[field] = {} if field == "reservations" else 3000000
        return value

    with pytest.raises(ValueError):
        BlobLedger(config, client).transact(corrupt)
    assert client.writes == 0


@pytest.mark.parametrize(
    "url",
    [
        "http://management.azure.com/",
        "https://attacker.invalid/",
        "https://user@management.azure.com/",
        "https://management.azure.com:8443/",
    ],
)
def test_oauth_destination_guard_before_token_request(config, url):
    client = AzureRest(
        config["workspace_subscription"],
        "https://management.azure.com/",
        {"management.azure.com"},
    )
    with pytest.raises(ValueError, match="destination"):
        client.request("GET", url)
    assert client._token is None


def change(resource_type="azurerm_storage_account", after=None, actions=None):
    return {
        "resource_changes": [
            {
                "address": resource_type + ".healthcare",
                "type": resource_type,
                "change": {
                    "actions": actions or ["create"],
                    "after": after
                    or {"name": "sthcpd054dev", "resource_group_name": "rg-hcp-dev"},
                },
            }
        ]
    }


@pytest.mark.parametrize(
    "actions", [["delete"], ["delete", "create"], ["create", "delete"], ["forget"]]
)
def test_destroy_replacement_unknown_actions_blocked(actions):
    with pytest.raises(ValueError, match="Destructive/unknown"):
        review_plan(change(actions=actions), "foundation")


@pytest.mark.parametrize(
    "resource_type",
    [
        "azurerm_databricks_workspace",
        "azurerm_nat_gateway",
        "azurerm_eventhub_namespace",
        "azurerm_log_analytics_workspace",
    ],
)
def test_unapproved_resource_type_blocked(resource_type):
    with pytest.raises(ValueError, match="outside approved"):
        review_plan(change(resource_type), "foundation")


def test_foreign_resource_group_blocked():
    with pytest.raises(ValueError, match="resource group"):
        review_plan(
            change(after={"name": "sthcpd054dev", "resource_group_name": "retail"}),
            "foundation",
        )


def test_role_escalation_and_sibling_scope_blocked():
    for role, scope in [
        ("Owner", "/resourceGroups/rg-hcp-dev"),
        ("Reader", "/resourceGroups/rg-hcp-dev-other"),
    ]:
        with pytest.raises(ValueError):
            review_plan(
                change(
                    "azurerm_role_assignment",
                    {"role_definition_name": role, "scope": scope},
                ),
                "foundation",
            )


def test_federated_identity_wildcard_blocked():
    with pytest.raises(ValueError, match="trust widened"):
        review_plan(
            change(
                "azuread_application_federated_identity_credential",
                {"subject": "repo:Kkb113/Healthcare-solution:*"},
            ),
            "foundation",
        )


def test_exact_model_cannot_be_changed():
    with pytest.raises(ValueError, match="preserve"):
        review_plan(
            change("azurerm_cognitive_deployment", {"name": "gpt-6-luna"}, ["update"]),
            "model-access",
        )


def storage_fixture(config):
    storage = {
        "isHnsEnabled": True,
        "allowBlobPublicAccess": False,
        "allowSharedKeyAccess": False,
        "minimumTlsVersion": "TLS1_2",
        "sku": {"name": "Standard_LRS"},
    }
    containers = [
        {"name": name, "properties": {"publicAccess": None}}
        for name in config["containers"]
    ]
    policy = {
        "policy": {
            "rules": [
                {
                    "enabled": True,
                    "definition": {
                        "filters": {
                            "prefixMatch": ["landing/"],
                            "blobTypes": ["blockBlob"],
                        },
                        "actions": {
                            "baseBlob": {
                                "tierToCool": {"daysAfterModificationGreaterThan": 90}
                            }
                        },
                    },
                }
            ]
        }
    }
    return storage, containers, policy


def test_storage_policy_live_shapes_and_negative_checks(config):
    storage, containers, policy = storage_fixture(config)
    validate_storage(storage, containers, policy, config)
    validate_storage(storage, containers, {"properties": policy}, config)
    containers[0]["properties"]["publicAccess"] = "Blob"
    with pytest.raises(ValueError, match="Public"):
        validate_storage(storage, containers, policy, config)
    containers[0]["properties"]["publicAccess"] = None
    policy["policy"]["rules"][0]["definition"]["actions"]["baseBlob"]["delete"] = {
        "daysAfterModificationGreaterThan": 90
    }
    with pytest.raises(ValueError, match="deletion"):
        validate_storage(storage, containers, policy, config)


def test_missing_budget_alert_is_failure(config):
    budgets = {}
    for name, amount in [
        ("workspace-build", 165),
        ("workspace-monthly", 55),
        ("model-build", 35),
        ("model-monthly", 5),
    ]:
        levels = [25, 50, 75, 90] if name.endswith("build") else [50, 80, 100]
        budgets[name] = {
            "properties": {
                "amount": amount,
                "category": "Cost",
                "timeGrain": "Annually" if name.endswith("build") else "Monthly",
                "notifications": {
                    str(level): {
                        "threshold": level,
                        "enabled": True,
                        "operator": "GreaterThanOrEqualTo",
                        "contactEmails": ["karthik@intellifysolutions.com"],
                    }
                    for level in levels
                },
            }
        }
    validate_budgets(budgets, config)
    budgets["workspace-build"]["properties"]["notifications"].pop("90")
    with pytest.raises(ValueError, match="thresholds"):
        validate_budgets(budgets, config)


@pytest.fixture
def provisioning():
    return load(CONFIGURATION)


def test_scim_exact_scopes_exclude_every_other_user(provisioning):
    default = {
        "synchronizationRules": [
            {
                "objectMappings": [
                    {
                        "sourceObjectName": name,
                        "enabled": True,
                        "scope": None,
                        "flowTypes": "Add,Update,Delete",
                    }
                    for name in ["Group", "User"]
                ]
            }
        ]
    }
    scoped = scope_schema(default, provisioning)
    validate_schema(scoped, provisioning)
    groups, user = scoped["synchronizationRules"][0]["objectMappings"]
    assert len(groups["scope"]["groups"]) == 8
    assert user["scope"]["groups"][0]["clauses"][0]["targetOperand"]["values"] == [
        OPERATOR
    ]
    assert default["synchronizationRules"][0]["objectMappings"][0]["scope"] is None
    user["scope"]["groups"][0]["clauses"][0]["targetOperand"]["values"].append(
        "unauthorized-user"
    )
    with pytest.raises(ValueError, match="scope widened"):
        validate_schema(scoped, provisioning)


@pytest.mark.parametrize(
    "change",
    [
        {"allowed_user_object_ids": ["someone-else"]},
        {"account_aim_enabled": True},
        {"allowed_group_object_ids": {}},
        {"mode": "AIM"},
    ],
)
def test_scim_cannot_expand_explicit_approval(provisioning, change):
    with pytest.raises(ValueError, match="explicit user approval"):
        validate_config(provisioning | change)


def test_preservation_digest_works_without_local_bootstrap_files(monkeypatch):
    before = {"user/example": "original-metadata-hash"}
    expected = {"preserved_identities_sha256": identity_digest(before)}
    monkeypatch.setattr(
        "configure_foundation_identity.preserved_identities", lambda _: before
    )
    assert check_preservation(None, expected) == before
    monkeypatch.setattr(
        "configure_foundation_identity.preserved_identities",
        lambda _: before | {"user/another": "changed"},
    )
    with pytest.raises(ValueError, match="Out-of-scope"):
        check_preservation(None, expected)


@pytest.mark.parametrize("fault", ["delete", "missing-scope", "extra-mapping"])
def test_scim_unsafe_schema_rejected(provisioning, fault):
    schema = scope_schema(
        {
            "synchronizationRules": [
                {
                    "objectMappings": [
                        {"sourceObjectName": name, "enabled": True}
                        for name in ["Group", "User"]
                    ]
                }
            ]
        },
        provisioning,
    )
    mapping = schema["synchronizationRules"][0]["objectMappings"][0]
    if fault == "delete":
        mapping["flowTypes"] = "Add,Update,Delete"
    elif fault == "missing-scope":
        mapping["scope"] = None
    else:
        schema["synchronizationRules"][0]["objectMappings"].append(
            {"sourceObjectName": "ServicePrincipal"}
        )
    with pytest.raises((ValueError, TypeError)):
        validate_schema(schema, provisioning)
