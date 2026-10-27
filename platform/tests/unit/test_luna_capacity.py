import json
from decimal import Decimal

from foundation_support import ROOT


def test_capacity_sizes_exact_frozen_ten_user_mix_with_twenty_percent_headroom():
    profile = json.loads(
        (ROOT / "platform/config/luna-capacity-profile.json").read_text()
    )
    frozen = json.loads(
        (ROOT / "platform/contracts/architecture/test-workloads.json").read_text()
    )
    app = json.loads(
        (ROOT / "platform/contracts/architecture/spend-controls.json").read_text()
    )["app"]
    expected = {
        "structuredSQL": 25,
        "forecast": 20,
        "notes": 20,
        "composite": 15,
        "denied": 10,
        "unsupported/abstain": 10,
    }
    assert {row["intent"]: row["turns_per_100"] for row in profile["mix"]} == expected
    assert (
        profile["concurrent_clients"] == frozen["performance"]["concurrent_users"] == 10
    )
    assert (
        profile["minimum_completed_benchmark_turns"]
        == frozen["performance"]["minimum_completed_per_component"]
        == 100
    )
    token_total = requests = 0
    for row in profile["mix"]:
        inputs, outputs = (
            row["estimated_input_caps_per_call"],
            row["output_caps_per_call"],
        )
        assert len(inputs) == len(outputs) <= app["max_model_calls_per_turn"]
        assert all(0 < value <= app["input_tokens_per_call"] for value in inputs)
        assert all(0 < value <= app["output_tokens_per_call"] for value in outputs)
        token_total += row["turns_per_100"] * (sum(inputs) + sum(outputs))
        requests += row["turns_per_100"] * len(inputs)
    headroom = 1 + Decimal(profile["headroom_fraction"])
    per_minute = Decimal(profile["offered_turns_per_minute"]) / 100
    assert (
        token_total * per_minute * headroom == Decimal(90300) < profile["verified_tpm"]
    )
    assert requests * per_minute * headroom == Decimal("44.4") < profile["verified_rpm"]
