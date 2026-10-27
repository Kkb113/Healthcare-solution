from probe_lakebase_runtime import (
    digest,
    is_database_access_denial,
    project_specification,
)


def test_project_overrides_costly_defaults_and_keeps_native_password_login_off():
    project = project_specification()
    assert project.spec.enable_pg_native_login is False
    for settings in [
        project.spec.default_endpoint_settings,
        project.initial_endpoint_spec,
    ]:
        assert settings.autoscaling_limit_min_cu == 1
        assert settings.autoscaling_limit_max_cu == 2
        assert settings.suspend_timeout_duration.seconds == 300
        assert settings.no_suspension is None  # False is rejected by the GA API.
    assert (
        project.initial_endpoint_spec.group.min
        == project.initial_endpoint_spec.group.max
        == 1
    )


def test_reconciliation_detects_cdf_update_and_delete_changes():
    before = [(1, "A", 10), (2, "B", 20), (3, "A", 30)]
    after = [(1, "A", 11), (2, "B", 20), (4, "B", 40)]
    assert digest(before) != digest(after)


def test_database_denial_cannot_pass_because_of_network_or_tls_failure():
    from types import SimpleNamespace

    assert is_database_access_denial(SimpleNamespace(sqlstate="28000"))
    assert is_database_access_denial(RuntimeError('role "fixture" does not exist'))
    assert is_database_access_denial(
        RuntimeError("ERROR: password authentication failed for user 'fixture'")
    )
    for message in [
        "connection timed out",
        "certificate verify failed",
        "connection refused",
        "server temporarily unavailable",
    ]:
        assert not is_database_access_denial(RuntimeError(message))
