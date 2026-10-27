"""Make the pure-Python wheel identical across Windows, WSL and Linux CI.

Normalize packaging text newlines, ZIP attributes/order and RECORD checksums.
Store tiny files uncompressed to avoid host zlib differences. Source bytes and
model code are not rewritten. Run after the pinned PEP517 build, before hashing.
"""

import argparse
import base64
import csv
import hashlib
import io
import os
import zipfile
from pathlib import Path, PurePosixPath

import tomllib


def canonicalize(path):
    path = Path(path)
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or any(
            PurePosixPath(n).is_absolute()
            or ".." in PurePosixPath(n).parts
            or "\\" in n
            for n in names
        ):
            raise ValueError("Ambiguous or unsafe wheel members")
        records = [n for n in names if n.endswith(".dist-info/RECORD")]
        if len(records) != 1:
            raise ValueError("Exactly one wheel RECORD is required")
        record = records[0]
        prefix = record.rsplit("/", 1)[0]
        if any(not n.startswith(("hcp/", prefix + "/")) for n in names):
            raise ValueError("Unexpected package in healthcare wheel")
        payloads = {n: archive.read(n) for n in names if n != record}
    for name, content in payloads.items():
        if name.startswith(prefix + "/"):
            payloads[name] = content.replace(b"\r\n", b"\n")
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    for name, content in sorted(payloads.items()):
        digest = (
            base64.urlsafe_b64encode(hashlib.sha256(content).digest())
            .rstrip(b"=")
            .decode()
        )
        writer.writerow([name, "sha256=" + digest, len(content)])
    writer.writerow([record, "", ""])
    payloads[record] = stream.getvalue().encode()
    target = path.with_suffix(".canonical.tmp")
    try:
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_STORED) as archive:
            for name, content in sorted(payloads.items()):
                info = zipfile.ZipInfo(name, date_time=(2024, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_STORED
                archive.writestr(info, content)
        os.replace(target, path)
    finally:
        if target.exists():
            target.unlink()
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path, nargs="?")
    args = parser.parse_args()
    platform = Path(__file__).resolve().parents[1]
    version = tomllib.loads((platform / "pyproject.toml").read_text())["project"][
        "version"
    ]
    path = (
        args.wheel
        or platform
        / "dist"
        / f"intellify_healthcare_platform-{version}-py3-none-any.whl"
    )
    print(canonicalize(path))
