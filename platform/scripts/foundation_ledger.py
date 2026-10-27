"""Durable cumulative build ledger; independent of workload compute and app budgets.

Azure cost snapshots are provisional and replace an earlier snapshot from the
same scope. Pending reservations survive resets/restarts. This ledger is not the
Phase 10 application-token reservation service or an Azure invoice guarantee.
"""

from __future__ import annotations

import copy
import json
from decimal import ROUND_CEILING, Decimal
from email.utils import formatdate
from urllib.parse import quote

from foundation_support import CONFIG, AzureRest, CloudHttpError, load, now


def integer_paise(value, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, int) or value < int(positive):
        raise ValueError(
            "Money must be nonnegative integer paise (positive when required)"
        )
    return value


def validate_ledger(ledger: dict) -> None:
    """Corrupt persisted control data must never make a funded window cheaper."""
    if (
        ledger["schema_version"] != 1
        or ledger["project"] != "healthcare-platform"
        or ledger["currency"] != "INR"
        or ledger["billing_status"] != "PROVISIONAL"
    ):
        raise ValueError("Unrecognized ledger identity/version/status")
    integer_paise(ledger["ceiling_paise"], positive=True)
    integer_paise(ledger["monthly_target_paise"], positive=True)
    integer_paise(ledger["revision"])
    for reservation in ledger["reservations"].values():
        integer_paise(reservation["paise"], positive=True)
        # Settlement needs independent evidence and a later controller contract.
        # No expiry, calendar reset or optimistic release exists in Phase 1.
        if reservation["status"] != "PENDING_PROVIDER_SETTLEMENT":
            raise ValueError(
                "Reservation settlement is not supported by this controller"
            )
    for scope, snapshot in ledger["snapshots"].items():
        if snapshot["scope"] != scope or snapshot["currency"] != "USD":
            raise ValueError("Snapshot identity/currency conflict")
        to_paise(
            snapshot["positive_cost_usd"],
            snapshot.get("planning_fx", "100"),
            snapshot.get("tax_reserve", "0.18"),
        )
        credits = Decimal(str(snapshot.get("credits_usd", "0")))
        if not credits.is_finite() or credits > 0:
            raise ValueError("Credits must be finite and nonpositive")


def to_paise(usd: str, fx="100", tax="0.18") -> int:
    value = Decimal(str(usd))
    exchange = Decimal(str(fx))
    reserve = Decimal(str(tax))
    if (
        not all(x.is_finite() for x in [value, exchange, reserve])
        or value < 0
        or exchange <= 0
        or reserve < 0
    ):
        raise ValueError("Invalid ledger price/FX/tax")
    return int(
        (value * exchange * (1 + reserve) * 100).to_integral_value(
            rounding=ROUND_CEILING
        )
    )


def initial_ledger(config: dict) -> dict:
    return {
        "schema_version": 1,
        "project": "healthcare-platform",
        "ceiling_paise": config["build_ceiling_paise"],
        "monthly_target_paise": config["monthly_target_paise"],
        "currency": "INR",
        "revision": 0,
        "created_at": now(),
        "updated_at": now(),
        "snapshots": {},
        "reservations": {
            "prerequisite-readiness": {
                "paise": config["preflight_reservation_paise"],
                "status": "PENDING_PROVIDER_SETTLEMENT",
                "phase": "prerequisites",
            },
            "foundation-validation": {
                "paise": config["foundation_validation_reservation_paise"],
                "status": "PENDING_PROVIDER_SETTLEMENT",
                "phase": 1,
            },
        },
        "events": [],
        "billing_status": "PROVISIONAL",
        "note": "Empty/missing/delayed billing is not zero spend. Retain reservations until charges are independently reconciled. No calendar reset of cumulative build spend.",
    }


def exposure(ledger: dict) -> dict:
    validate_ledger(ledger)
    snapshots = sum(
        to_paise(
            s["positive_cost_usd"],
            s.get("planning_fx", "100"),
            s.get("tax_reserve", "0.18"),
        )
        for s in ledger["snapshots"].values()
    )
    reserved = sum(r["paise"] for r in ledger["reservations"].values())
    total = snapshots + reserved
    return {
        "observed_cost_with_planning_reserves_paise": snapshots,
        "outstanding_reservations_paise": reserved,
        "exposure_paise": total,
        "remaining_paise": ledger["ceiling_paise"] - total,
        "pause_new_work": total >= 1800000,
        "over_ceiling": total > ledger["ceiling_paise"],
        "billing_status": ledger["billing_status"],
    }


def reserve(ledger: dict, reservation_id: str, paise: int, phase: int) -> dict:
    validate_ledger(ledger)
    integer_paise(paise, positive=True)
    if (
        not reservation_id
        or isinstance(phase, bool)
        or not isinstance(phase, int)
        or phase < 1
    ):
        raise ValueError("Reservation needs an identity and positive phase number")
    if reservation_id in ledger["reservations"]:
        previous = ledger["reservations"][reservation_id]
        if previous["paise"] != paise or previous["phase"] != phase:
            raise ValueError("Conflicting immutable reservation identity")
        return ledger
    if (
        exposure(ledger)["pause_new_work"]
        or exposure(ledger)["remaining_paise"] < paise
    ):
        raise ValueError("Funded window exceeds remaining budget or pause threshold")
    changed = copy.deepcopy(ledger)
    changed["reservations"][reservation_id] = {
        "paise": paise,
        "phase": phase,
        "status": "PENDING_PROVIDER_SETTLEMENT",
    }
    changed["events"].append(
        {"kind": "RESERVE", "id": reservation_id, "at": now(), "paise": paise}
    )
    return changed


def update_snapshot(
    ledger: dict, scope: str, snapshot: dict, expected_scopes: set[str]
) -> dict:
    validate_ledger(ledger)
    if (
        scope not in expected_scopes
        or snapshot["currency"] != "USD"
        or snapshot["scope"] != scope
    ):
        raise ValueError("Unexpected cost scope or currency")
    to_paise(snapshot["positive_cost_usd"])
    credits = Decimal(str(snapshot.get("credits_usd", "0")))
    if not credits.is_finite() or credits > 0:
        raise ValueError(
            "Credits must be zero or negative and do not reduce gross exposure"
        )
    changed = copy.deepcopy(ledger)
    snapshot = copy.deepcopy(snapshot)
    if snapshot.get("period_start") != "2026-10-01":
        raise ValueError(
            "Cumulative build snapshots must retain the fixed project start"
        )
    previous = ledger["snapshots"].get(scope)
    if previous and Decimal(snapshot["positive_cost_usd"]) < Decimal(
        previous["positive_cost_usd"]
    ):
        # An empty/delayed/revised query cannot erase already observed gross spend.
        snapshot["reported_positive_cost_usd"] = snapshot["positive_cost_usd"]
        snapshot["positive_cost_usd"] = previous["positive_cost_usd"]
        snapshot["status"] = "PROVISIONAL_REGRESSION_RETAINED"
    # Latest whole-period snapshot replaces prior totals, not additive billing.
    changed["snapshots"][scope] = snapshot
    validate_ledger(changed)
    return changed


class BlobLedger:
    def __init__(self, config=None, client=None):
        self.config = config or load(CONFIG)
        host = f"{self.config['storage_account']}.blob.core.windows.net"
        self.client = client or AzureRest(
            self.config["workspace_subscription"], "https://storage.azure.com/", {host}
        )
        self.url = f"https://{host}/{self.config['control_container']}/{quote(self.config['ledger_blob'], safe='/')}"

    @staticmethod
    def headers(extra=None):
        return {
            "x-ms-version": "2023-11-03",
            "x-ms-date": formatdate(usegmt=True),
            **(extra or {}),
        }

    def read(self):
        _, headers, body = self.client.request("GET", self.url, headers=self.headers())
        ledger = json.loads(body)
        validate_ledger(ledger)
        if (
            ledger["ceiling_paise"] != self.config["build_ceiling_paise"]
            or ledger["monthly_target_paise"] != self.config["monthly_target_paise"]
        ):
            raise ValueError("Existing ledger budget conflict")
        return ledger, headers.get("ETag") or headers.get("Etag")

    def initialize(self):
        content = initial_ledger(self.config)
        try:
            self.client.request(
                "PUT",
                self.url,
                body=content,
                headers=self.headers(
                    {"If-None-Match": "*", "x-ms-blob-type": "BlockBlob"}
                ),
            )
            return content, True
        except CloudHttpError as error:
            if error.status != 412 and not (
                error.status == 409 and error.code == "BlobAlreadyExists"
            ):
                raise
            existing, _ = self.read()
            if (
                existing["ceiling_paise"] != self.config["build_ceiling_paise"]
                or existing["project"] != "healthcare-platform"
            ):
                raise ValueError("Existing ledger identity/budget conflict") from error
            return existing, False

    def transact(self, operation, attempts=5):
        for _ in range(attempts):
            original, etag = self.read()
            if not etag:
                raise ValueError("Ledger ETag unavailable; fail closed")
            changed = operation(copy.deepcopy(original))
            validate_ledger(changed)
            if any(
                changed[key] != original[key]
                for key in [
                    "project",
                    "ceiling_paise",
                    "monthly_target_paise",
                    "currency",
                    "created_at",
                ]
            ):
                raise ValueError(
                    "Transaction attempted to alter immutable ledger identity"
                )
            if not set(original["reservations"]) <= set(changed["reservations"]):
                raise ValueError("Transaction cannot discard pending reservations")
            if any(
                changed["reservations"][key] != value
                for key, value in original["reservations"].items()
            ):
                raise ValueError(
                    "Transaction cannot alter an existing pending reservation"
                )
            if changed == original:
                return original
            changed["revision"] = original["revision"] + 1
            changed["updated_at"] = now()
            try:
                self.client.request(
                    "PUT",
                    self.url,
                    body=changed,
                    headers=self.headers(
                        {"If-Match": etag, "x-ms-blob-type": "BlockBlob"}
                    ),
                )
                return changed
            except CloudHttpError as error:
                if error.status != 412:
                    raise
        raise RuntimeError(
            "Concurrent ledger updates exhausted bounded retries; no write admitted"
        )
