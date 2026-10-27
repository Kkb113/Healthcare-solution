"""Validate explicit environment and workspace targets before a cloud operation."""

from dataclasses import dataclass
from urllib.parse import urlparse

WORKSPACE_ID = 7405619366453187
HOST = "https://adb-7405619366453187.7.azuredatabricks.net"
CATALOGS = {"dev": "hc_dev", "test": "hc_test", "prod": "hc_prod"}


@dataclass(frozen=True)
class Target:
    environment: str
    warehouse_id: str
    workspace_id: int = WORKSPACE_ID
    host: str = HOST

    def __post_init__(self):
        if self.environment not in CATALOGS or self.workspace_id != WORKSPACE_ID:
            raise ValueError("Unapproved healthcare environment/workspace")
        parsed = urlparse(self.host)
        if (
            self.host != HOST
            or parsed.username
            or parsed.password
            or not self.warehouse_id
        ):
            raise ValueError("Explicit approved host and warehouse are required")

    @property
    def catalog(self):
        return CATALOGS[self.environment]
