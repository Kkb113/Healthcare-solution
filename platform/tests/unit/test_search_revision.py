import json
import shutil

import pytest
from foundation_support import ROOT
from verify_search_revision import verify


@pytest.fixture
def revision(tmp_path):
    for relative in [
        "platform/contracts/revisions/search-basic-v1.json",
        "platform/config/search-baseline-revision.json",
        "platform/config/search-backend.json",
        "platform/config/completion-cost-model.json",
        "platform/contracts/architecture/cost-model.json",
        "platform/contracts/architecture/gate-dependencies.json",
        "evidence/platform/architecture-baseline/gate.json",
        "evidence/platform/workspace-foundation/azure-search-price.json",
    ]:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return tmp_path


def test_versioned_search_revision_preserves_frozen_baseline_and_fits_budget():
    result = verify()
    assert result["status"] == "PASS" and result["frozen_criteria_unchanged"]
    assert result["costs"]["build"]["total_inr"] == "15568.28"


@pytest.mark.parametrize(
    ("path", "edit"),
    [
        (
            "platform/config/search-baseline-revision.json",
            lambda x: x.update(status="PENDING"),
        ),
        ("platform/config/search-backend.json", lambda x: x.update(replicas=2)),
        (
            "platform/config/search-backend.json",
            lambda x: x.update(no_24x7_search=False),
        ),
        (
            "platform/contracts/revisions/search-basic-v1.json",
            lambda x: x.update(required_tests_reduced=True),
        ),
        (
            "platform/config/completion-cost-model.json",
            lambda x: x["build"][1].update(quantity="1"),
        ),
        (
            "platform/config/completion-cost-model.json",
            lambda x: next(r for r in x["build"] if r["id"] == "search").update(
                quantity="0"
            ),
        ),
        (
            "evidence/platform/workspace-foundation/azure-search-price.json",
            lambda x: x["item"].update(armRegionName="other"),
        ),
        (
            "evidence/platform/architecture-baseline/gate.json",
            lambda x: x.update(status="FAIL"),
        ),
    ],
)
def test_unapproved_or_underfunded_revision_fails_closed(revision, path, edit):
    target = revision / path
    data = json.loads(target.read_text())
    edit(data)
    target.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        verify(revision)
