"""Verify each forwarded OAuth caller; never use the app identity as a fallback."""

from dataclasses import dataclass

from hcp.common.config import HOST as WORKSPACE_HOST


@dataclass(frozen=True)
class VerifiedCaller:
    databricks_id: str
    principal_name: str
    client: object


def forwarded_caller(token, client_factory):
    if not isinstance(token, str) or not token or token != token.strip():
        raise PermissionError("MISSING_OR_INVALID_USER_TOKEN")
    if len(token) > 16384 or any(ord(char) < 33 for char in token):
        raise PermissionError("MISSING_OR_INVALID_USER_TOKEN")
    # Explicit token authentication prevents SDK environment credentials from
    # silently substituting the much more privileged app service principal.
    client = client_factory(host=WORKSPACE_HOST, token=token, auth_type="pat")
    current = client.current_user.me()
    if not current.id or not current.user_name:
        raise PermissionError("UNVERIFIED_CALLER")
    return VerifiedCaller(str(current.id), current.user_name, client)
