"""Cloud identity assertions come from a trusted verifier, never request headers."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from hcp.common.clocks import utc_instant


@dataclass(frozen=True)
class Identity:
    tenant_id: str
    object_id: str
    principal_name: str

    def __post_init__(self):
        UUID(self.tenant_id)
        UUID(self.object_id)
        if not self.principal_name:
            raise ValueError("Verified principal name is required")


@dataclass(frozen=True)
class Binding:
    identity: Identity
    version: int
    role: str
    facilities: frozenset[str]
    phi: bool
    valid_from: datetime
    valid_to: datetime
    revoked_at: datetime | None = None

    def __post_init__(self):
        if (
            isinstance(self.version, bool)
            or not isinstance(self.version, int)
            or self.version < 1
            or not isinstance(self.phi, bool)
            or not isinstance(self.facilities, frozenset)
            or any(
                not isinstance(facility, str) or not facility
                for facility in self.facilities
            )
            or utc_instant(self.valid_from) >= utc_instant(self.valid_to)
        ):
            raise ValueError("Invalid scope version or validity interval")


def resolve(identity: Identity, bindings: list[Binding], at: datetime) -> Binding:
    candidates = [b for b in bindings if b.identity == identity]
    if not candidates:
        raise PermissionError("DENY_UNMAPPED")
    latest = max(b.version for b in candidates)
    current = [b for b in candidates if b.version == latest]
    if len(current) != 1:
        raise PermissionError("DENY_AMBIGUOUS")
    binding = current[0]
    if binding.revoked_at is not None or not (
        utc_instant(binding.valid_from)
        <= utc_instant(at)
        < utc_instant(binding.valid_to)
    ):
        raise PermissionError("DENY_INACTIVE")
    return binding


def authorize(binding: Binding, facility: str, domain: str, phi=False):
    domains = {
        "hcp-clinical": {"clinical", "quality", "flow"},
        "hcp-finance": {"finance", "revenue"},
        "hcp-operations": {"flow", "workforce"},
        "hcp-analysts": {
            "clinical",
            "quality",
            "flow",
            "workforce",
            "finance",
            "revenue",
        },
        "hcp-auditors": {
            "clinical",
            "quality",
            "flow",
            "workforce",
            "finance",
            "revenue",
        },
        "hcp-data-engineers": {
            "clinical",
            "quality",
            "flow",
            "workforce",
            "finance",
            "revenue",
        },
        "hcp-data-scientists": {
            "clinical",
            "quality",
            "flow",
            "workforce",
            "finance",
            "revenue",
        },
        "hcp-platform-admins": {
            "clinical",
            "quality",
            "flow",
            "workforce",
            "finance",
            "revenue",
        },
    }
    if (
        facility not in binding.facilities
        or domain not in domains.get(binding.role, set())
        or phi
        and not binding.phi
    ):
        raise PermissionError("DENY_SCOPE")
