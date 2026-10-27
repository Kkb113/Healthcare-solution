"""Exercise the app handler locally without credentials or a network listener."""

import importlib.util
from contextlib import nullcontext
from types import SimpleNamespace

import pytest
from foundation_support import ROOT

spec = importlib.util.spec_from_file_location(
    "authorization_app", ROOT / "platform/probes/authorization_app/app.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_missing_user_token_fails_even_with_app_environment_credentials(monkeypatch):
    monkeypatch.setenv("DATABRICKS_CLIENT_ID", "privileged-app-fixture")
    request = SimpleNamespace(headers={"x-forwarded-user": "forged-admin"})
    with pytest.raises(module.HTTPException) as error:
        module.fixture(request)
    assert error.value.status_code == 403


def test_forged_identity_headers_are_not_authorization_inputs(monkeypatch):
    captured = []

    def execute(statement, parameters):
        captured.append({"statement": statement, "parameters": parameters})

    def connect(**kwargs):
        captured.append(kwargs)
        cursor = SimpleNamespace(
            execute=execute, fetchall=lambda: [("A", "Fixture Alice")]
        )
        return nullcontext(SimpleNamespace(cursor=lambda: nullcontext(cursor)))

    caller = SimpleNamespace(
        databricks_id="verified-A",
        client=object(),
    )
    monkeypatch.setattr(module, "forwarded_caller", lambda token, factory: caller)
    monkeypatch.setattr(module, "connect_sql", connect)
    request = SimpleNamespace(
        headers={
            "x-forwarded-access-token": "fixture-user-token",
            "x-facility-id": "B",
            "x-entra-object-id": "forged-admin",
        }
    )
    result = module.fixture(request, "A")
    assert result["caller_id"] == "verified-A"
    assert captured[0]["access_token"] == "fixture-user-token"
    assert "credentials_provider" not in captured[0]
    assert captured[0]["use_inline_params"] is False
    assert captured[0]["use_kernel"] is False
    assert captured[0]["enable_telemetry"] is False
    assert captured[1]["parameters"] == {"facility": "A"}
    assert ":facility" in captured[1]["statement"]


def test_facility_injection_is_rejected_before_any_sdk_call():
    with pytest.raises(module.HTTPException) as error:
        module.fixture(SimpleNamespace(headers={}), "A' OR TRUE")
    assert error.value.status_code == 400


def test_metric_route_uses_caller_token_and_bound_facility(monkeypatch):
    captured = []

    def execute(statement, parameters):
        captured.append((statement, parameters))

    cursor = SimpleNamespace(execute=execute, fetchall=lambda: [("A", 1)])

    def connect(**kwargs):
        assert kwargs["access_token"] == "metric-caller-token"
        return nullcontext(SimpleNamespace(cursor=lambda: nullcontext(cursor)))

    monkeypatch.setattr(module, "connect_sql", connect)
    monkeypatch.setattr(
        module,
        "forwarded_caller",
        lambda *_: SimpleNamespace(databricks_id="metric-caller"),
    )
    result = module.metric_fixture(
        SimpleNamespace(
            headers={
                "x-forwarded-access-token": "metric-caller-token",
                "x-facility-id": "B",
            }
        ),
        "A",
    )
    assert result == {"caller_id": "metric-caller", "rows": [["A", 1]]}
    assert "MEASURE(fixture_count)" in captured[0][0]
    assert captured[0][1] == {"facility": "A"}
