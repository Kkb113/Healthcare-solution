"""Copy the locally built wheel into the ignored app vendor directory, hash checked."""

import hashlib
import shutil

import tomllib
from foundation_support import ROOT


def prepare():
    source = ROOT / "platform/probes/authorization_app"
    project = tomllib.loads((source / "pyproject.toml").read_text())
    path = project["tool"]["uv"]["sources"]["intellify-healthcare-platform"]["path"]
    target = source / path
    wheel = ROOT / "platform/dist" / target.name
    lock = tomllib.loads((source / "uv.lock").read_text())
    package = next(
        row for row in lock["package"] if row["name"] == "intellify-healthcare-platform"
    )
    expected = package["wheels"][0]["hash"]
    if "sha256:" + hashlib.sha256(wheel.read_bytes()).hexdigest() != expected:
        raise PermissionError(
            "Built wheel differs from reviewed app lock; reconcile version and artifact before provisioning"
        )
    if target.exists() and target.read_bytes() != wheel.read_bytes():
        raise PermissionError(
            "Refusing to replace a different immutable vendor artifact"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copyfile(wheel, target)
    return target


if __name__ == "__main__":
    print(prepare().relative_to(ROOT))
