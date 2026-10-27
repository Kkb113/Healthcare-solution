from uuid import uuid4

import pytest
from probe_role_matrix import LAYER_ROLES, domain_scope, scope_insert


def test_all_eight_human_roles_have_explicit_gold_and_domain_contracts():
    assert len(LAYER_ROLES["gold"]) == 8
    assert domain_scope("finance") == {"finance", "revenue"}
    assert domain_scope("operations") == {"flow", "workforce"}
    assert "finance" not in domain_scope("clinical")
    assert "analysts" not in LAYER_ROLES["silver"]


@pytest.mark.parametrize("mode", ["active", "revoked", "expired", "ambiguous"])
def test_negative_scope_assertions_keep_identity_and_version(mode):
    record = {
        "application_id": str(uuid4()),
        "entra_object_id": str(uuid4()),
        "databricks_id": "123",
        "role": "hcp-finance",
    }
    value = scope_insert(record, 4, mode)
    assert record["application_id"] in value and record["entra_object_id"] in value
    assert ", 4," in value
    if mode == "expired":
        assert "current_timestamp() - INTERVAL 1 MINUTE" in value
