"""Temporary nonpatient OBO probe. No credential or request-header logging."""

import os
from urllib.parse import urlsplit

from databricks.sdk import WorkspaceClient
from fastapi import FastAPI, HTTPException, Request
from hcp.auth.forwarded import forwarded_caller
from hcp.common.config import HOST

app = FastAPI()
WAREHOUSE = "bd30bdac29080126"
TABLE = "hc_test.gold.app_authorization_fixture"
METRIC = "hc_test.semantic.hcp_foundation_metric"


def connect_sql(**kwargs):
    # The documented OBO path uses the connector's Thrift transport. Keep the
    # forwarded token request-local; never use the app's credential provider.
    from databricks import sql

    return sql.connect(**kwargs)


def query_fixture(token, facility, metric=False):
    statement = (
        f"SELECT facility_id, MEASURE(fixture_count) AS fixture_count FROM {METRIC} WHERE facility_id = :facility GROUP BY facility_id ORDER BY facility_id"
        if metric
        else f"SELECT facility_id, person_name FROM {TABLE} WHERE facility_id = :facility ORDER BY facility_id"
    )
    with (
        connect_sql(
            server_hostname=urlsplit(HOST).hostname,
            http_path=f"/sql/1.0/warehouses/{WAREHOUSE}",
            access_token=token,
            use_kernel=False,
            use_sea=False,
            use_inline_params=False,
            enable_telemetry=False,
            _socket_timeout=30,
            _retry_stop_after_attempts_count=1,
            session_configuration={"statement_timeout": "90"},
        ) as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute(
            statement,
            {"facility": facility},
        )
        return [list(row) for row in cursor.fetchall()]


@app.get("/api/health")
def health():
    import sys
    from importlib.metadata import version

    return {
        "status": "ready",
        "fixture": True,
        "python": sys.version,
        "sdk": version("databricks-sdk"),
        "shared_library": version("intellify-healthcare-platform"),
    }


@app.get("/api/fixture")
def fixture(request: Request, facility_id: str = "A"):
    return read_fixture(request, facility_id)


@app.get("/api/metric")
def metric_fixture(request: Request, facility_id: str = "A"):
    return read_fixture(request, facility_id, metric=True)


def read_fixture(request, facility_id, metric=False):
    if facility_id not in {"A", "B"}:
        raise HTTPException(400, "INVALID_FACILITY")
    stage = "verify_caller"
    token_present = bool(request.headers.get("x-forwarded-access-token"))
    try:
        caller = forwarded_caller(
            request.headers.get("x-forwarded-access-token"), WorkspaceClient
        )
        stage = "query"
        rows = query_fixture(
            request.headers["x-forwarded-access-token"], facility_id, metric
        )
        return {
            "caller_id": caller.databricks_id,
            "rows": rows,
        }
    except HTTPException:
        raise
    except Exception as error:
        # Deliberately return a fixed error; SDK error strings can carry headers.
        raise HTTPException(
            403,
            {
                "code": "CALLER_NOT_AUTHORIZED",
                "stage": stage,
                "user_token_present": token_present,
                "error_type": type(error).__name__,
                "error_code": getattr(error, "error_code", None),
            },
        ) from error


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ["DATABRICKS_APP_PORT"]),
        access_log=False,
    )
