"""Small local contract check, also used by the deployed smoke wheel."""

import argparse
import json

from hcp import __version__
from hcp.common.config import Target


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", choices=["dev", "test", "prod"], required=True)
    parser.add_argument("--warehouse-id", required=True)
    args = parser.parse_args()
    target = Target(args.environment, args.warehouse_id)
    print(
        json.dumps(
            {
                "status": "PASS",
                "package_version": __version__,
                "catalog": target.catalog,
            }
        )
    )
