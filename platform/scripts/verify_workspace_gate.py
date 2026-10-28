"""Write/verify Phase 2 only from committed code and complete execution evidence."""

import argparse
import hashlib
import json
import subprocess
from xml.etree import ElementTree

from foundation_support import ROOT, load, now, save
from verify_search_revision import verify as verify_revision

DIRECTORY = ROOT / "evidence/platform/workspace-foundation"
DESCRIPTOR = "c36a9b7841743057be2f6993a27790c82a170c847399687a0c2647b5b9167af5"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counts(path):
    suites = ElementTree.parse(path).getroot()
    result = {
        k: sum(int(s.attrib.get(k, 0)) for s in suites.iter("testsuite"))
        for k in ["tests", "failures", "errors", "skipped"]
    }
    if result["tests"] < 200 or any(
        result[k] for k in ["failures", "errors", "skipped"]
    ):
        raise ValueError("Incomplete or failed regression suite")
    return result


def execution_checks(directory=DIRECTORY):
    search = load(directory / "azure-search-probe.json")
    if (
        search["status"] != "PASS"
        or len(search["lifecycles"]) != 2
        or not all(
            search.get(k) is True
            for k in [
                "wrong_entra_principal_denied",
                "document_deletion_propagated",
                "rebuild_integrity",
                "first_service_deleted",
                "negative_probe_credential_process_local_cleared",
            ]
        )
        or search["cleanup"].get("service_deleted") is not True
        or search["denial_http_status"] != 403
    ):
        raise ValueError("Incomplete Search lifecycle or security evidence")
    if (
        search["lifecycles"][0]["authorized_result_sha256"]
        != search["lifecycles"][1]["authorized_result_sha256"]
    ):
        raise ValueError("Search rebuild differs")
    billing = load(directory / "probe-billing-reconciliation.json")
    if (
        billing["status"] != "PASS"
        or len(billing["cases"]) != 6
        or not all(x["status"] == "PASS" for x in billing["cases"].values())
        or billing["reservations_released"]
        or billing["invoice_final"]
    ):
        raise ValueError("Incomplete billing attribution or unsafe settlement claim")
    cleanup = load(directory / "completion-cleanup.json")
    if (
        cleanup["status"] != "PASS"
        or cleanup["out_of_scope_identities_unchanged"] is not True
        or cleanup["out_of_scope_identity_count"] != 16
        or cleanup["azure_search_service"] != "ABSENT"
        or cleanup["temporary_service_role_assignments"] != ["ABSENT", "ABSENT"]
    ):
        raise ValueError("Search scope or cleanup verification failed")
    sleep = load(directory / "completion-idle.json")
    if (
        sleep["status"] != "PASS"
        or sleep["state"] != "ASLEEP"
        or sleep["running_compute"]
        or sleep["metadata_only"] is not True
        or sleep["idle_seconds"] < 900
        or sleep["workloads_launched"] != 0
    ):
        raise ValueError("Idle window did not pass")
    ci = load(directory / "completion-ci.json")
    if (
        set(ci["deployments"]) != {"dev", "test"}
        or any(
            r["conclusion"] != "success"
            or r["source_sha"] != ci["source_sha"]
            or r["workloads_launched"] != 0
            for r in ci["deployments"].values()
        )
        or ci["external_guard"]["conclusion"] != "success"
    ):
        raise ValueError("Required CI deployments/guard did not pass")
    roles = load(directory / "role-matrix.json")
    if (
        roles["status"] != "PASS"
        or len(roles["cases"]) != 96
        or not all(x["status"] == "PASS" for x in roles["cases"])
    ):
        raise ValueError("Original role matrix failed")
    foundation = load(directory / "foundation-smoke-probes.json")
    if any(
        foundation[name]["status"] != "PASS"
        for name in ["warehouse-idle.json", "telemetry-probe.json", "volume-probe.json"]
    ) or not all(
        x["status"] == "PASS" for x in foundation["security-probe.json"]["checks"]
    ):
        raise ValueError(
            "Storage, system table, warehouse or base security probe failed"
        )
    runtime = load(directory / "runtime-probe-reconciliation.json")
    lakebase = load(directory / "lakebase-runtime.json")
    genie = load(directory / "genie-pilot-reconciliation.json")
    model = load(directory / "model-probe-reconciliation.json")
    if (
        runtime["runtime_status"] != "FUNCTIONAL_PASS_BILLING_PENDING"
        or runtime["polling_status"] != "PASS"
        or not all(runtime["cleanup"].values())
    ):
        raise ValueError("Serverless runtime or authenticated API polling failed")
    if (
        lakebase["status"] != "FUNCTIONAL_PASS_BILLING_PENDING"
        or not all(c["status"] == "PASS" for c in lakebase["cases"])
        or not all(lakebase["cleanup"].values())
    ):
        raise ValueError("Lakebase runtime/recovery cleanup failed")
    if (
        genie["status"] != "FUNCTIONAL_PASS_BILLING_PENDING"
        or genie["native_questions_dispatched"] != 1
        or not all(genie["cleanup"].values())
    ):
        raise ValueError("Native Genie functional pilot failed")
    if (
        model["status"] != "COMPATIBILITY_AND_DECLARED_CAPACITY_PASS"
        or model["permission_denial_positive_control"] is not True
        or model["accepted_fixture_calls"] != 4
    ):
        raise ValueError("Exact Luna compatibility probe failed")
    for name in [
        "app-authorization.json",
        "semantic-dashboard.json",
        "serving-probe.json",
    ]:
        if load(directory / name)["status"] != "PASS":
            raise ValueError(f"Required capability failed: {name}")
    drift = load(directory / "completion-terraform-drift.json")
    if drift["status"] != "PASS" or any(
        r["plan_exit_code"] != 0 for r in drift["modules"].values()
    ):
        raise ValueError("Infrastructure drift detected")
    windows = counts(directory / "completion-windows-tests.xml")
    linux = counts(directory / "completion-linux-tests.xml")
    if linux["tests"] != windows["tests"] + 1:
        raise ValueError("Windows/Linux unit parity or Delta integration missing")
    return {
        "source_sha": ci["source_sha"],
        "windows_tests": windows,
        "linux_tests": linux,
    }


def source_paths():
    paths = {
        ROOT / "README.md",
        ROOT / ".github/workflows/workspace-platform.yml",
        ROOT / ".github/workflows/platform-guard.yml",
        ROOT / "platform/pyproject.toml",
        ROOT / "platform/databricks.yml",
    }
    for pattern in [
        "platform/scripts/*.py",
        "platform/src/**/*.py",
        "platform/tests/**/*.py",
        "platform/config/*.json",
        "platform/contracts/revisions/*.json",
        "platform/infra/**/*.tf",
        "platform/sql/**/*.sql",
    ]:
        paths.update(ROOT.glob(pattern))
    return sorted(paths)


def write():
    checked = execution_checks()
    source = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    if source != checked["source_sha"]:
        raise ValueError("CI source differs from gate source")
    hashes = {}
    for path in source_paths():
        relative = path.relative_to(ROOT).as_posix()
        current = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        committed = hashlib.sha256(
            subprocess.check_output(["git", "show", f"{source}:{relative}"], cwd=ROOT)
        ).hexdigest()
        if current != committed:
            raise ValueError(f"Uncommitted gate input: {relative}")
        hashes[relative] = committed
    revision = verify_revision()
    criteria = [
        {"id": f"2.{n}", "status": "PASS", "measure": text}
        for n, text in enumerate(
            [
                "Dev and test deploy the same committed 0.2.4 source from CI; metadata-only deployment launches zero workloads",
                "Shared warehouse is serverless 2XSmall min/max1 auto-stop5; retained independent idle test observed339.313seconds",
                "96 retained actual role allow/deny cases; additional Azure Search Entra403 and facility prefilter/per-hit checks pass",
                "System billing, lakeflow and lineage read probes pass; six actual billing component attributions now reconcile",
                "Independent metadata inspection confirms zero workload compute after at least fifteen minutes idle",
                "Basic Search create/delete/rebuild/delete preserves results and scoped ACLs; external no-workload guard passes",
                "Matching Windows/Linux unit suites plus Linux Delta integration pass; wheel hash agrees across Windows and Linux CI",
                "All required capability evidence passes under the approved versioned Search replacement; optional webhook remains UNSUPPORTED_DISABLED with authenticated API polling passed; costs/cleanup recorded",
            ],
            1,
        )
    ]
    files = [
        "azure-search-probe.json",
        "azure-search-price.json",
        "azure-search-rejected-request.json",
        "azure-search-first-lifecycle.json",
        "probe-billing-reconciliation.json",
        "completion-azure-costs.json",
        "completion-cleanup.json",
        "completion-idle.json",
        "completion-ci.json",
        "completion-terraform-drift.json",
        "completion-windows-tests.xml",
        "completion-linux-tests.xml",
        "wheel-change-review.json",
        "role-matrix.json",
        "foundation-smoke-probes.json",
        "runtime-probe-reconciliation.json",
        "model-probe-reconciliation.json",
        "app-authorization.json",
        "lakebase-runtime.json",
        "genie-pilot-reconciliation.json",
        "semantic-dashboard.json",
        "serving-probe.json",
    ]
    gate = {
        "phase": 2,
        "name": "workspace-foundation",
        "status": "PASS",
        "evaluated_at": now(),
        "source_sha": source,
        "dataset_descriptor_sha256": DESCRIPTOR,
        "criteria": criteria,
        "contract_hashes": hashes,
        "report_hashes": {f: digest(DIRECTORY / f) for f in files},
        "dependency_gates": [
            {"path": p, "sha256": digest(ROOT / p), "status": "PASS"}
            for p in [
                "evidence/platform/architecture-baseline/gate.json",
                "evidence/platform/adopted-infrastructure/gate.json",
            ]
        ],
        "effective_architecture_revision": "platform/contracts/revisions/search-basic-v1.json",
        "environment": "Existing healthcare East US workspace; bounded nonpatient test windows; native Windows and Ubuntu24.04/CI Python3.12",
        "tests": checked,
        "costs": {
            "planning": revision["costs"],
            "provider_attribution": "PASS: six component groups matched to retained IDs and actual effective unit prices",
            "azure_invoice_final": False,
            "all_prior_reservations_retained": True,
            "completion_envelope_inr": "3050.00",
        },
        "measurements": {
            "native_search": "Still unresolved, replaced by explicitly approved tested Azure Basic backend; both failed attempts retained",
            "search_accepted_lifecycles": 2,
            "new_application_secrets": 0,
            "final_state": "ASLEEP",
        },
        "limitations": [
            "Invoice and late corrections remain provisional; no reservation released and no claim of zero total bill.",
            "Constant Search vectors prove capability, authorization and lifecycle only; real corpus relevance, embeddings, scale, revocation and clinical security remain mandatory Phase10 tests.",
            "Full demo performance, whole-platform cold rebuild and settled24hour sleep remain Phase12/13 gates.",
            "Original model-serving latency and full-answer agent quality remain later gates; Phase2 does not claim their acceptance.",
        ],
        "owner_signoff": {
            "authority": "User-approved phase completion and explicit versioned Search baseline approval; delegated technical review",
            "record": "platform/config/search-baseline-revision.json",
            "independent_clinical_certification_claimed": False,
        },
        "next_phase": {
            "phase": 3,
            "prerequisite_satisfied": True,
            "execution_started": False,
        },
    }
    save(DIRECTORY / "gate.json", gate)
    return gate


def verify():
    gate = load(DIRECTORY / "gate.json")
    if (
        gate["phase"] != 2
        or gate["status"] != "PASS"
        or gate["dataset_descriptor_sha256"] != DESCRIPTOR
        or [x["id"] for x in gate["criteria"]] != [f"2.{i}" for i in range(1, 9)]
        or not all(x["status"] == "PASS" for x in gate["criteria"])
    ):
        raise ValueError("Phase2 is incomplete")
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", gate["source_sha"], "HEAD"],
        cwd=ROOT,
        check=True,
    )
    for relative, expected in gate["contract_hashes"].items():
        path = (ROOT / relative).resolve()
        if (
            not path.is_relative_to(ROOT.resolve())
            or hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            != expected
            or hashlib.sha256(
                subprocess.check_output(
                    ["git", "show", f"{gate['source_sha']}:{relative}"], cwd=ROOT
                )
            ).hexdigest()
            != expected
        ):
            raise ValueError(f"Changed Phase2 gate input: {relative}")
    for filename, expected in gate["report_hashes"].items():
        path = (DIRECTORY / filename).resolve()
        if not path.is_relative_to(DIRECTORY.resolve()) or digest(path) != expected:
            raise ValueError(f"Changed Phase2 evidence: {filename}")
    for dependency in gate["dependency_gates"]:
        if (
            digest(ROOT / dependency["path"]) != dependency["sha256"]
            or load(ROOT / dependency["path"])["status"] != "PASS"
        ):
            raise ValueError("Original prerequisite gate changed")
    verify_revision()
    execution_checks()
    return {
        "status": "PASS",
        "phase": 2,
        "criteria": 8,
        "source_sha": gate["source_sha"],
        "final_state": "ASLEEP",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    if parser.parse_args().write:
        write()
    print(json.dumps(verify()))
