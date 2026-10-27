"""Install pinned official Windows CLI archives without changing system PATH."""

from __future__ import annotations

import hashlib
import json
import os
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    if os.name != "nt":
        raise SystemExit("This bootstrap pins Windows amd64 packages only.")
    specs = json.loads((ROOT / "platform/config/tool-versions.json").read_text())
    for name, spec in specs.items():
        destination = ROOT / ".tools" / name / spec["version"]
        destination.mkdir(parents=True, exist_ok=True)
        archive = destination / "package.zip"
        if not archive.exists():
            with urllib.request.urlopen(spec["url"], timeout=120) as response:
                archive.write_bytes(response.read())
        if hashlib.sha256(archive.read_bytes()).hexdigest() != spec["sha256"]:
            raise SystemExit(f"Checksum mismatch: {name}; no extraction performed")
        with zipfile.ZipFile(archive) as package:
            for member in package.infolist():
                target = (destination / member.filename).resolve()
                if not target.is_relative_to(destination.resolve()):
                    raise SystemExit("Archive path escapes the tool directory")
            package.extractall(destination)
        print(f"Verified {name} {spec['version']}: {destination / (name + '.exe')}")


if __name__ == "__main__":
    main()
