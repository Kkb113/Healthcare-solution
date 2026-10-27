"""Pure state transitions. Cloud adapters use conditional writes and a lease."""

import copy
from datetime import datetime, timedelta, timezone

from hcp.common.clocks import utc_instant
from hcp.common.config import WORKSPACE_ID

STATES = {"ASLEEP", "STARTING", "AWAKE", "STOPPING", "FAILED"}
KINDS = {
    "warehouse",
    "job",
    "pipeline",
    "app",
    "serving",
    "search",
    "lakebase",
    "synced_table",
    "genie",
    "dashboard",
    "alert",
}


def initial_state():
    return {
        "schema_version": 1,
        "workspace_id": WORKSPACE_ID,
        "revision": 0,
        "state": "ASLEEP",
        "session": None,
        "resources": [],
        "events": [],
    }


def instant(value):
    return utc_instant(datetime.fromisoformat(value.replace("Z", "+00:00")))


def validate(state):
    if (
        state["schema_version"] != 1
        or state["workspace_id"] != WORKSPACE_ID
        or state["state"] not in STATES
        or isinstance(state["revision"], bool)
        or state["revision"] < 0
    ):
        raise ValueError("Unrecognized platform control state")
    identities = set()
    for resource in state["resources"]:
        identity = (resource["kind"], resource["id"])
        if (
            identity in identities
            or resource["kind"] not in KINDS
            or not resource["id"]
        ):
            raise ValueError("Ambiguous or unsupported resource manifest")
        if not (
            resource["name"].startswith("hcp-") or resource["name"].startswith("hcp_")
        ):
            raise ValueError("Resource is outside the healthcare namespace")
        if resource["owner"] not in {"terraform", "bundle", "api-adapter"}:
            raise ValueError("Resource must have one declared lifecycle owner")
        identities.add(identity)
    session = state["session"]
    if state["state"] in {"STARTING", "AWAKE"} and not session:
        raise ValueError("Awake state has no funded session")
    if session:
        if not session["reservation_id"] or session["profile"] not in {
            "foundation",
            "batch",
            "rti",
        }:
            raise ValueError("Unknown funded session")
        duration = instant(session["deadline_utc"]) - instant(session["started_at_utc"])
        if not timedelta(0) < duration <= timedelta(minutes=120):
            raise ValueError("Session must have a bounded two-hour hard deadline")


def open_window(
    state, session_id, reservation_id, deadline, at=None, profile="foundation"
):
    validate(state)
    at = utc_instant(at or datetime.now(timezone.utc))
    deadline = utc_instant(deadline)
    if state["state"] != "ASLEEP" or not session_id or not reservation_id:
        raise ValueError("A funded window starts only from verified sleep")
    changed = copy.deepcopy(state)
    changed["state"] = "STARTING"
    changed["session"] = {
        "id": session_id,
        "reservation_id": reservation_id,
        "profile": profile,
        "started_at_utc": at.isoformat(),
        "deadline_utc": deadline.isoformat(),
    }
    validate(changed)
    return changed


def admission(state, reservation_available, at=None):
    validate(state)
    at = utc_instant(at or datetime.now(timezone.utc))
    if (
        state["state"] not in {"STARTING", "AWAKE"}
        or not reservation_available
        or instant(state["session"]["deadline_utc"]) <= at
    ):
        raise PermissionError("DENY_UNFUNDED_ASLEEP_OR_EXPIRED")


def register(state, resource):
    changed = copy.deepcopy(state)
    previous = [
        r
        for r in changed["resources"]
        if r["kind"] == resource["kind"] and r["id"] == resource["id"]
    ]
    if previous:
        if previous[0] != resource:
            raise ValueError("Resource identity/owner is immutable within a manifest")
        return changed
    changed["resources"].append(resource)
    validate(changed)
    return changed


def transition(state, wanted, ready=False, asleep=False, at=None):
    validate(state)
    allowed = {
        "ASLEEP": {"ASLEEP"},
        "STARTING": {"AWAKE", "STOPPING", "FAILED"},
        "AWAKE": {"AWAKE", "STOPPING", "FAILED"},
        "STOPPING": {"ASLEEP", "FAILED", "STOPPING"},
        "FAILED": {"STOPPING", "FAILED"},
    }
    if (
        wanted not in allowed[state["state"]]
        or wanted == "AWAKE"
        and not ready
        or wanted == "ASLEEP"
        and not asleep
    ):
        raise ValueError("Unverified or illegal lifecycle transition")
    if wanted == "AWAKE":
        admission(state, True, at)
    changed = copy.deepcopy(state)
    changed["state"] = wanted
    if wanted == "ASLEEP":
        changed["last_session"] = changed["session"]
        changed["session"] = None
    validate(changed)
    return changed


def needs_shutdown(state, observed_running, at=None):
    validate(state)
    at = utc_instant(at or datetime.now(timezone.utc))
    return bool(observed_running) and (
        state["state"] not in {"AWAKE", "STARTING"}
        or not state["session"]
        or instant(state["session"]["deadline_utc"]) <= at
    )
