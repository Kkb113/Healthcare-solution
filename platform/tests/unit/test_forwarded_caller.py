"""Request identity never falls back to privileged environment credentials."""

from types import SimpleNamespace

import pytest
from hcp.auth.forwarded import forwarded_caller
from hcp.common.config import HOST as WORKSPACE_HOST


@pytest.mark.parametrize("token", [None, "", " token", "a\nb", "x" * 16385])
def test_invalid_forwarded_token_never_initializes_app_client(token):
    def forbidden(**kwargs):
        raise AssertionError("No SDK call allowed without a user credential")

    with pytest.raises(PermissionError):
        forwarded_caller(token, forbidden)


def test_verified_identity_comes_from_authoritative_me_not_request_headers():
    calls = []
    client = SimpleNamespace(
        current_user=SimpleNamespace(
            me=lambda: SimpleNamespace(
                id="immutable-db-id", user_name="verified-caller"
            )
        )
    )

    def factory(**kwargs):
        calls.append(kwargs)
        return client

    result = forwarded_caller("opaque-fixture-token", factory)
    assert result.databricks_id == "immutable-db-id"
    assert result.client is client
    assert calls == [
        {"host": WORKSPACE_HOST, "token": "opaque-fixture-token", "auth_type": "pat"}
    ]


def test_invalid_user_token_never_retries_as_app_identity():
    def rejected(**kwargs):
        raise PermissionError("TOKEN_REJECTED")

    with pytest.raises(PermissionError, match="TOKEN_REJECTED"):
        forwarded_caller("invalid-fixture", rejected)
