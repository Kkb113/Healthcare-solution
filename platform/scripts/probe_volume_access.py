"""Actual Jobs principal round trip through an isolated UC managed volume."""

import hashlib
import io
import json

from databricks.sdk.errors import NotFound
from databricks.sdk.service import catalog as c
from foundation_support import ROOT, databricks_clients, now, save
from platform_control import ControlStore, admission
from probe_security_baseline import JOBS, principal_client

NAME = "hc_test._foundation_probe.runtime_io"
FILE = "/Volumes/hc_test/_foundation_probe/runtime_io/roundtrip.txt"
PAYLOAD = b"Healthcare foundation nonpatient storage fixture.\n"


def main():
    admission(ControlStore().read()[0], True)
    account, operator = databricks_clients()
    report = {
        "status": "INCOMPLETE",
        "started_at": now(),
        "validations": {},
        "cleanup": {},
    }
    volume_created = False
    try:
        for location in ["hcp_uc_managed_dev", "hcp_landing_dev"]:
            validated = operator.storage_credentials.validate(
                storage_credential_name="hcp_storage_dev",
                external_location_name=location,
            ).as_dict()
            report["validations"][location] = validated
            assert len(validated["results"]) == 6
            assert all(row["result"] == "PASS" for row in validated["results"])
        operator.volumes.create(
            "hc_test",
            "_foundation_probe",
            "runtime_io",
            c.VolumeType.MANAGED,
            comment="Temporary nonpatient runtime IO fixture; delete after probe",
        )
        volume_created = True
        operator.grants.update(
            "VOLUME",
            NAME,
            changes=[
                c.PermissionsChange(
                    principal=JOBS[1],
                    add=[c.Privilege.READ_VOLUME, c.Privilege.WRITE_VOLUME],
                )
            ],
        )
        with principal_client(account, JOBS) as jobs:
            jobs.files.upload(FILE, io.BytesIO(PAYLOAD), overwrite=False)
            downloaded = jobs.files.download(FILE)
            actual = downloaded.contents.read()
            assert actual == PAYLOAD
            jobs.files.delete(FILE)
            try:
                jobs.files.download(FILE)
            except NotFound:
                report["file_deleted"] = True
            else:
                raise AssertionError("Deleted file remains readable")
        report.update(
            status="PASS",
            principal="sp-hcp-jobs",
            bytes=len(PAYLOAD),
            sha256=hashlib.sha256(PAYLOAD).hexdigest(),
            oracle_denial_evidence="security-probe.json/jobs_cannot_read_oracle",
        )
    finally:
        if volume_created:
            operator.volumes.delete(NAME)
            try:
                operator.volumes.read(NAME)
            except NotFound:
                report["cleanup"]["volume_deleted"] = True
        report["completed_at"] = now()
        save(ROOT / "output/platform-foundation/volume-probe.json", report)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
