"""Bounded request-policy primitives; no ledger storage or model dispatch.

Phase 10 must supply atomic reservations and settlement. A local preflight
decision alone never authorizes a production model request.
"""

from decimal import ROUND_CEILING, Decimal


def preflight(
    *, ledger_available, remaining_paise, input_rate, output_rate, input_cap, output_cap
):
    if ledger_available is not True:
        return "LEDGER_UNAVAILABLE"
    if input_rate is None or output_rate is None:
        return "UNKNOWN_PRICE"
    rates = [Decimal(str(value)) for value in [input_rate, output_rate]]
    if any(not value.is_finite() or value < 0 for value in rates):
        return "UNKNOWN_PRICE"
    if any(
        type(value) is not int or value < 0
        for value in [remaining_paise, input_cap, output_cap]
    ):
        raise ValueError("Invalid budget or token quantity")
    # Rates are integer-money planning paise per million tokens, tax/FX already
    # incorporated by the caller's versioned rate card.
    estimate = (
        (rates[0] * input_cap + rates[1] * output_cap) / 1_000_000
    ).to_integral_value(rounding=ROUND_CEILING)
    return (
        "ALLOW" if estimate > 0 and estimate <= remaining_paise else "BUDGET_EXHAUSTED"
    )


def bounded_request(dispatch, reserve_attempt, sleep, *, maximum_attempts=2):
    if type(maximum_attempts) is not int or not 1 <= maximum_attempts <= 2:
        raise ValueError("Only one explicit 429 retry is permitted")
    for attempt in range(maximum_attempts):
        if reserve_attempt(attempt) is not True:
            raise PermissionError("REQUEST_NOT_RESERVED")
        try:
            return dispatch()
        except Exception as error:
            # A timeout/connection failure is ambiguous and retains its hold.
            # Permission failures are terminal. Never retry either implicitly.
            if (
                getattr(error, "status_code", None) != 429
                or attempt + 1 >= maximum_attempts
            ):
                raise
            headers = getattr(getattr(error, "response", None), "headers", {}) or {}
            try:
                delay = float(headers.get("retry-after", 1))
            except (ValueError, TypeError):
                raise ValueError("Invalid retry-after; fail closed") from error
            if not 0 <= delay <= 5:
                raise PermissionError("RETRY_OUTSIDE_REQUEST_DEADLINE") from error
            sleep(delay)
    raise AssertionError("Unreachable request policy state")
