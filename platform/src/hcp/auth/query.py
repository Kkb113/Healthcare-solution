"""Read-only SQL uses a caller-owned client; remediation has no path here."""

import re
import time

IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")


def object_name(catalog, schema, table):
    if any(
        not IDENTIFIER.fullmatch(value) for value in [catalog, schema, table]
    ) or catalog not in {"hc_dev", "hc_test", "hc_prod", "hc_ops"}:
        raise ValueError("Unapproved governed object identifier")
    return ".".join(f"`{value}`" for value in [catalog, schema, table])


class ReadClient:
    def __init__(self, workspace_client, warehouse_id, timeout_seconds=60):
        self.client = workspace_client
        self.warehouse_id = warehouse_id
        self.timeout = timeout_seconds

    def select(self, statement, parameters=None):
        # Tools supply parameterized single read statements. Arbitrary DDL and
        # multi-statement execution belong to the separately privileged owner.
        if (
            not re.match(r"^\s*SELECT\b", statement, re.IGNORECASE)
            or ";" in statement
            or re.search(
                r"\b(COPY|INSERT|UPDATE|DELETE|MERGE|ALTER|DROP|CREATE|GRANT|REVOKE|PUT|REMOVE)\b",
                statement,
                re.IGNORECASE,
            )
        ):
            raise PermissionError("Read-only query client rejects this statement")
        response = self.client.statement_execution.execute_statement(
            warehouse_id=self.warehouse_id,
            statement=statement,
            parameters=parameters,
            wait_timeout="0s",
        )
        deadline = time.monotonic() + self.timeout
        while response.status.state.value in {"PENDING", "RUNNING"}:
            if time.monotonic() >= deadline:
                self.client.statement_execution.cancel_execution(response.statement_id)
                raise TimeoutError("SQL read exceeded its deadline")
            time.sleep(0.25)
            response = self.client.statement_execution.get_statement(
                response.statement_id
            )
        if response.status.state.value != "SUCCEEDED":
            raise RuntimeError("Governed SQL read failed")
        return response
