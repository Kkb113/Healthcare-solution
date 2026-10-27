"""Bounded App metadata inspection through initial identity provisioning."""

import time


def wait_initial_provisioning(
    client, name, deadline, sleeper=time.sleep, clock=time.monotonic
):
    while clock() < deadline:
        app = client.apps.get(name)
        state = app.compute_status.state.value if app.compute_status else "UNKNOWN"
        if state == "ERROR":
            raise RuntimeError("App initial provisioning failed")
        # no_compute still has a STARTING phase for URL, OAuth and identity
        # provisioning. A start request is invalid until that phase settles.
        if app.service_principal_id and state in {"STOPPED", "ACTIVE"}:
            return app
        sleeper(3)
    raise TimeoutError("App initial identity provisioning exceeded deadline")
