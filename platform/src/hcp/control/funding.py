"""Cumulative operation admission inside a single, already-reserved probe envelope.

Reservations survive restarts and are never released merely because a create call
timed out. A reconciled invoice/cleanup record is required before any refund.
"""

import copy

# Integer paise; includes the full search billing tail. These are pooled phase
# limits, not per-session allowances. No automatic price discovery fallback.
LIMITS = {
    "sql_minutes": (110, 551),
    "automated_dbu_milli": (4000, 6),
    "app_minutes": (33, 94),
    "search_cycles": (2, 80948),
    "lakebase_minutes": (35, 103),
    "serving_minutes": (60, 56),
    "genie_questions": (1, 3304),
    "luna_requests": (12, 5),
    "completion_sql_minutes": (30, 551),
    "azure_search_hours": (2, 1192),
}
ENVELOPE_PAISE = 280000


def claim(state, operation_id, meter, units):
    if not operation_id or meter not in LIMITS or type(units) is not int or units < 1:
        raise ValueError("Invalid priced operation")
    changed = copy.deepcopy(state)
    claims = changed.setdefault("cost_claims", {})
    item = {"meter": meter, "units": units}
    if operation_id in claims:
        if claims[operation_id] != item:
            raise PermissionError("Operation identity cannot be repriced or reused")
        return changed
    claims[operation_id] = item
    consumed = {}
    total = 0
    for entry in claims.values():
        key = entry["meter"]
        amount = entry["units"]
        if key not in LIMITS or type(amount) is not int or amount < 1:
            raise ValueError("Corrupt cost claims; fail closed")
        consumed[key] = consumed.get(key, 0) + amount
        if consumed[key] > LIMITS[key][0]:
            raise PermissionError("Cumulative meter allowance exhausted")
        # Automated DBU quantity is in milli-DBU; the rounded-up per-milli rate
        # intentionally over-reserves compared with the frozen rate card.
        total += amount * LIMITS[key][1]
    if total > ENVELOPE_PAISE:
        raise PermissionError("Cumulative phase envelope exhausted")
    return changed
