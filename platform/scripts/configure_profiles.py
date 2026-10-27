"""Append non-secret healthcare CLI profiles; preserve defaults and other profiles."""

from __future__ import annotations

import configparser
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    config = json.loads((ROOT / "platform/config/workspace.json").read_text())
    target = Path.home() / ".databrickscfg"
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    parsed = configparser.ConfigParser()
    parsed.read_string(existing)
    profiles = {
        config["workspace_profile"]: {
            "host": config["workspace_host"],
            "auth_type": "azure-cli",
            "azure_workspace_resource_id": config["workspace_resource_id"],
            "azure_tenant_id": config["tenant_id"],
        },
        config["account_profile"]: {
            "host": "https://accounts.azuredatabricks.net",
            "auth_type": "azure-cli",
            "account_id": config["account_id"],
            "azure_tenant_id": config["tenant_id"],
        },
    }
    additions = []
    for name, fields in profiles.items():
        if parsed.has_section(name):
            if any(
                parsed.get(name, key, fallback=None) != value
                for key, value in fields.items()
            ):
                raise SystemExit(f"Existing {name} differs; refusing to overwrite it")
            continue
        additions.append(
            "\n["
            + name
            + "]\n"
            + "".join(f"{key} = {value}\n" for key, value in fields.items())
        )
    if additions:
        # Validate everything before one append; no old credential content is printed.
        with target.open("a", encoding="utf-8") as handle:
            handle.write("".join(additions))
    print(
        "Healthcare CLI profiles verified; existing defaults and credentials preserved."
    )


if __name__ == "__main__":
    main()
