from configure_native_budgets import WORKSPACE, config


def test_native_genie_controls_cannot_block_other_workspaces_or_send_email():
    value = config("hcp-native-genie-build").as_dict()
    assert value["filter"]["workspace_id"]["values"] == [WORKSPACE]
    assert value["filter"]["tags"] == [
        {"key": "databricks-product", "value": {"operator": "IN", "values": ["genie"]}}
    ]
    assert {x["quantity_threshold"] for x in value["alert_configurations"]} == {
        "35",
        "25",
    }
    assert all(
        a == {"action_type": "BLOCK_USAGE"}
        for row in value["alert_configurations"]
        for a in row["action_configurations"]
    )


def test_optional_external_probe_has_a_tiny_scoped_limit():
    value = config("hcp-foundation-external-probe", external=True).as_dict()
    assert value["include_external_spend"] is True
    assert value["filter"]["workspace_id"]["values"] == [WORKSPACE]
    assert value["alert_configurations"][0]["quantity_threshold"] == "0.01"
