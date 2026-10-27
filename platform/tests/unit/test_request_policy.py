from types import SimpleNamespace

import pytest
from hcp.agent.request_policy import bounded_request, preflight


@pytest.mark.parametrize(
    "change,expected",
    [
        ({}, "ALLOW"),
        ({"ledger_available": False}, "LEDGER_UNAVAILABLE"),
        ({"remaining_paise": 0}, "BUDGET_EXHAUSTED"),
        ({"input_rate": None}, "UNKNOWN_PRICE"),
        ({"output_rate": "NaN"}, "UNKNOWN_PRICE"),
    ],
)
def test_tiny_limit_faults_fail_before_dispatch(change, expected):
    values = {
        "ledger_available": True,
        "remaining_paise": 10,
        "input_rate": 1298,
        "output_rate": 6490,
        "input_cap": 2000,
        "output_cap": 256,
    }
    assert preflight(**(values | change)) == expected


class Rejection(Exception):
    def __init__(self, status, retry_after="1"):
        self.status_code = status
        self.response = SimpleNamespace(headers={"retry-after": retry_after})


def test_explicit_429_retry_reserves_each_dispatch_and_observes_retry_after():
    calls, reservations, delays = [], [], []

    def dispatch():
        calls.append(1)
        if len(calls) == 1:
            raise Rejection(429, "2")
        return {"answer": 42}

    def reserve(attempt):
        reservations.append(attempt)
        return True

    assert bounded_request(dispatch, reserve, delays.append) == {"answer": 42}
    assert reservations == [0, 1] and delays == [2]


@pytest.mark.parametrize(
    "error", [Rejection(403), Rejection(404), TimeoutError(), ConnectionError()]
)
def test_permission_and_ambiguous_transport_failures_are_not_retried(error):
    reservations = []

    def reserve(attempt):
        reservations.append(attempt)
        return True

    def dispatch():
        raise error

    with pytest.raises(type(error)):
        bounded_request(dispatch, reserve, lambda _: pytest.fail("unexpected retry"))
    assert reservations == [0]


def test_failed_second_reservation_prevents_second_billable_attempt():
    calls = []

    def dispatch():
        calls.append(1)
        raise Rejection(429)

    with pytest.raises(PermissionError, match="NOT_RESERVED"):
        bounded_request(dispatch, lambda attempt: attempt == 0, lambda _: None)
    assert len(calls) == 1
