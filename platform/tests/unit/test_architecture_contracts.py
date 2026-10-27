"""Fault-oriented tests for the frozen design gate; no cloud resources started."""

from __future__ import annotations

import copy
import json
import shutil
import sys
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "platform/scripts"))
from freeze_gate_contracts import check_dependencies
from freeze_source_contracts import topological_order
from validate_architecture import (
    calculate_costs,
    load,
    number,
    price_lines,
    validate_package,
)
from write_architecture_gate import repository_digest


@pytest.fixture
def package(tmp_path):
    """Copy only the bounded design, not the 4.47 GB accepted release."""
    for relative in [
        "platform/contracts/architecture",
        "platform/docs/adr",
        "evidence/platform",
    ]:
        shutil.copytree(ROOT / relative, tmp_path / relative)
    shutil.copyfile(
        ROOT / "azure-databricks-implementation.md",
        tmp_path / "azure-databricks-implementation.md",
    )
    quality = load(ROOT / "platform/contracts/architecture/data-quality-contracts.json")
    for relative in [
        quality["rule_source"],
        *[p for p in quality["source_semantic_hashes"] if not p.startswith("data/")],
    ]:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return tmp_path


def mutate(root, filename, edit):
    path = root / "platform/contracts/architecture" / (filename + ".json")
    content = load(path)
    edit(content)
    path.write_text(json.dumps(content), encoding="utf-8")


def test_complete_design_is_valid_without_claiming_tenant_probes():
    result = validate_package(require_approval=False)
    assert result["source_columns"] == 526
    assert result["status"] == "PROPOSAL_VALIDATED_NOT_A_PHASE_PASS"
    assert result["tenant_probe_execution"].startswith("NOT_RUN")


def test_missing_scope_approval_blocks_gate(package):
    mutate(
        package,
        "design-review",
        lambda d: d.update(funded_scope_status="PENDING_USER_SCOPE_APPROVAL"),
    )
    with pytest.raises(ValueError, match="approval pending"):
        validate_package(package)


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-0.01", True])
def test_invalid_quantity_is_rejected(value):
    with pytest.raises((TypeError, ValueError)):
        number(value)


def test_cost_rounding_is_conservative_and_does_not_use_float():
    cost = price_lines(
        [{"id": "one", "rate": "r", "quantity": "1"}],
        {"r": {"usd": ".00001", "unit": "token", "meter": "fixture"}},
        "100",
        ".18",
    )
    assert cost["inr"] == "0.01"
    assert Decimal(cost["inr"]) >= Decimal(cost["usd"]) * 118


def test_unknown_price_fails_closed():
    with pytest.raises(ValueError, match="Unknown price"):
        price_lines([{"id": "x", "rate": "unknown", "quantity": "1"}], {}, "100", ".18")


def test_free_promotion_is_not_used_to_hide_cost():
    with pytest.raises(ValueError, match="promotional"):
        price_lines(
            [{"id": "x", "rate": "r", "quantity": "1"}],
            {"r": {"usd": "0", "unit": "DBU", "meter": "free"}},
            "100",
            ".18",
        )


def test_same_charge_cannot_be_attributed_twice():
    with pytest.raises(ValueError, match="Duplicate charge"):
        price_lines(
            [{"id": "x", "rate": "r", "quantity": "1"}] * 2,
            {"r": {"usd": "1", "unit": "DBU", "meter": "fixture"}},
            "100",
            ".18",
        )


def test_full_original_scope_does_not_fit_and_cannot_be_marked_pass():
    original = load(ROOT / "platform/contracts/architecture/full-scope-cost-model.json")
    costs = calculate_costs(original)
    assert not costs["build"]["fits"]
    assert Decimal(costs["build"]["total_inr"]) > 32000


def test_proposed_cost_includes_search_tails_and_stress_failure():
    model = load(ROOT / "platform/contracts/architecture/cost-model.json")
    costs = calculate_costs(model)
    assert costs["build"]["total_inr"] == "17802.05"
    assert costs["build"]["fits"]
    assert all(c["fits"] for c in costs["monthly"].values())
    assert costs["stress_cases"][0]["fits"]  # 4 DBU per Genie question
    assert not costs["stress_cases"][1]["fits"]  # +10% rates and FX
    assert Decimal(
        next(l["usd"] for l in costs["build"]["lines"] if l["id"] == "search")
    ) == Decimal("30.10")


@pytest.mark.parametrize(
    ("filename", "edit", "message"),
    [
        ("source-contracts", lambda d: d["tables"].pop(), "25 unique"),
        (
            "source-contracts",
            lambda d: d["tables"][0].update(canonical_rows=999),
            "row budget",
        ),
        (
            "source-contracts",
            lambda d: d.update(descriptor_sha256="0" * 64),
            "Release binding",
        ),
        ("delivery-temporal", lambda d: d.update(delivery_key=["sha256"]), "Checksum"),
        (
            "delivery-temporal",
            lambda d: d["reference_policy"].update(runtime_oracle_access=True),
            "Oracle separation",
        ),
        (
            "delivery-temporal",
            lambda d: d["reference_policy"].update(validation_business_write=True),
            "Oracle separation",
        ),
        (
            "kpi-catalog",
            lambda d: d["definitions"][0].update(sources=["invented_table"]),
            "KPI grain",
        ),
        (
            "ml-eligibility",
            lambda d: d["use_cases"][10].update(disposition="ELIGIBLE"),
            "Unsupported prospective",
        ),
        (
            "ml-eligibility",
            lambda d: d["split_policy"].update(
                validation_origins=["2024-01-01", "2025-06-30"]
            ),
            "Overlapping holdout",
        ),
        (
            "probe-matrix",
            lambda d: d["probes"][0].update(required=False),
            "Only inbound webhook",
        ),
        (
            "capability-matrix",
            lambda d: d["capabilities"][0].update(required_probe="missing"),
            "Capability missing",
        ),
        (
            "security-ownership",
            lambda d: d["resources"].append(copy.deepcopy(d["resources"][0])),
            "Duplicate lifecycle",
        ),
        (
            "test-workloads",
            lambda d: d["performance"].update(minimum_completed_per_component=10),
            "sample/concurrency",
        ),
        (
            "test-workloads",
            lambda d: d["genie"].update(agent_tool_questions=999),
            "Unfunded native",
        ),
        (
            "test-workloads",
            lambda d: d["agent_evaluation"].update(full_phases=[10, 12]),
            "Agent regression",
        ),
        (
            "spend-controls",
            lambda d: d["native_genie"].update(
                additional_resource_tag_filters=["space-id"]
            ),
            "Unsupported native Genie",
        ),
        (
            "spend-controls",
            lambda d: d["controller"]["limits"].update(
                search_billing_tail_hours_per_cycle=0
            ),
            "Missing search",
        ),
        (
            "cost-model",
            lambda d: d["rates"]["sql"].update(usd=".01"),
            "Rate/evidence mismatch",
        ),
        ("cost-model", lambda d: d.update(ceiling_inr="45000"), "Unapproved budget"),
        (
            "cost-model",
            lambda d: d["build"][0].update(quantity="2000"),
            "exceeds ceiling",
        ),
    ],
)
def test_corrupt_contract_blocks_gate(package, filename, edit, message):
    mutate(package, filename, edit)
    with pytest.raises(ValueError, match=message):
        validate_package(package, require_approval=False)


def test_dependency_cycle_and_missing_parent_fail():
    with pytest.raises(ValueError, match="cycle"):
        topological_order({"location": ["worker"], "worker": ["location"]})
    with pytest.raises(ValueError, match="Unknown dependency"):
        topological_order({"encounter": ["missing"]})


def test_real_dependency_has_locations_before_workers_before_encounters():
    source = load(ROOT / "platform/contracts/architecture/source-contracts.json")
    order = source["topological_order"]
    assert (
        order.index("cost_center")
        < order.index("location")
        < order.index("worker_assignment")
        < order.index("encounter")
        < order.index("clinical_event")
        < order.index("service_charge")
    )


def test_ml_cannot_start_before_both_gold_and_autopilot():
    contract = load(ROOT / "platform/contracts/architecture/gate-dependencies.json")
    passed = {"status": "PASS", "criteria": [{"status": "PASS"}]}
    with pytest.raises(ValueError, match="gate 7"):
        check_dependencies(8, {6: passed}, contract)
    check_dependencies(8, {6: passed, 7: passed}, contract)


def test_failed_criterion_cannot_hide_under_dependency_pass():
    contract = load(ROOT / "platform/contracts/architecture/gate-dependencies.json")
    with pytest.raises(ValueError, match="unpassed criterion"):
        check_dependencies(
            1, {0: {"status": "PASS", "criteria": [{"status": "FAIL"}]}}, contract
        )


def test_approved_cost_artifact_tampering_blocks_gate(package):
    mutate(package, "cost-model", lambda d: d.update(planning_inr_per_usd="100.01"))
    with pytest.raises(ValueError, match="Approved scope artifact changed"):
        validate_package(package)


def test_roadmap_criterion_edit_requires_new_baseline(package):
    plan = package / "azure-databricks-implementation.md"
    text = plan.read_text(encoding="utf-8").replace(
        "At least 18/20 correct per space", "At least 1/20 correct per space"
    )
    plan.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="Roadmap exit/dependency contract changed"):
        validate_package(package)


@pytest.mark.parametrize(
    ("filename", "edit", "message"),
    [
        (
            "delivery-temporal",
            lambda d: d.update(retrospective_known_to_as_feature=True),
            "Hindsight known_to",
        ),
        (
            "ml-eligibility",
            lambda d: d["staffing_rule_provenance"].update(accepted_base_hppd="8.0"),
            "Staffing rule differs",
        ),
        ("data-quality-contracts", lambda d: d["rules"].pop(), "55 distinct DQ"),
    ],
)
def test_accepted_business_semantics_cannot_be_silently_rewritten(
    package, filename, edit, message
):
    mutate(package, filename, edit)
    with pytest.raises(ValueError, match=message):
        validate_package(package, require_approval=False)


def test_repository_newline_hashing_does_not_change_release_raw_hashing(tmp_path):
    from freeze_source_contracts import digest

    windows = tmp_path / "windows.json"
    linux = tmp_path / "linux.json"
    windows.write_bytes(b'{"a":1}\r\n')
    linux.write_bytes(b'{"a":1}\n')
    assert repository_digest(windows) == repository_digest(linux)
    assert digest(windows) != digest(linux)
