"""Healthcare-only Genie block controls and optional external-provider budget probe.

No email destination or outbound notification is configured. These approximate
native controls supplement the application ledger; they are not an invoice cap.
"""

import argparse
import json
from decimal import Decimal

from databricks.sdk.errors import InvalidParameterValue
from databricks.sdk.service import billing as b
from foundation_support import ROOT, databricks_clients, now, save

ACCOUNT = "aed328b4-17bf-43f0-9399-c470ad8ea1b5"
WORKSPACE = 7405619366453187


def alert(amount, per_user=False):
    return b.CreateBudgetConfigurationBudgetAlertConfigurations(
        quantity_threshold=amount,
        quantity_type=b.AlertConfigurationQuantityType.LIST_PRICE_DOLLARS_USD,
        scope_type=b.AlertConfigurationScopeType.ALERT_CONFIGURATION_SCOPE_TYPE_PER_USER
        if per_user
        else b.AlertConfigurationScopeType.ALERT_CONFIGURATION_SCOPE_TYPE_SHARED,
        time_period=b.AlertConfigurationTimePeriod.MONTH,
        trigger_type=b.AlertConfigurationTriggerType.CUMULATIVE_SPENDING_EXCEEDED,
        action_configurations=[
            b.CreateBudgetConfigurationBudgetActionConfigurations(
                action_type=b.ActionConfigurationType.BLOCK_USAGE
            )
        ],
    )


def config(name, external=False):
    return b.CreateBudgetConfigurationBudget(
        account_id=ACCOUNT,
        display_name=name,
        resource_type=b.BudgetResourceType.BUDGET_RESOURCE_TYPE_UNITY_AI_GATEWAY,
        include_external_spend=external,
        filter=b.BudgetConfigurationFilter(
            workspace_id=b.BudgetConfigurationFilterWorkspaceIdClause(
                operator=b.BudgetConfigurationFilterOperator.IN, values=[WORKSPACE]
            ),
            tags=[]
            if external
            else [
                b.BudgetConfigurationFilterTagClause(
                    key="databricks-product",
                    value=b.BudgetConfigurationFilterClause(
                        operator=b.BudgetConfigurationFilterOperator.IN,
                        values=["genie"],
                    ),
                )
            ],
        ),
        alert_configurations=[alert("0.01")]
        if external
        else [alert("35"), alert("25", per_user=True)],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--external-probe", action="store_true")
    args = parser.parse_args()
    account, _ = databricks_clients()
    name = (
        "hcp-foundation-external-probe"
        if args.external_probe
        else "hcp-native-genie-build"
    )
    expected = config(name, args.external_probe)
    matched = [v for v in account.budgets.list() if v.display_name == name]
    if len(matched) > 1:
        raise ValueError("Ambiguous healthcare budget name")
    budget_id = matched[0].budget_configuration_id if matched else None
    report = {
        "status": "INCOMPLETE",
        "observed_at": now(),
        "name": name,
        "scope": "healthcare workspace only",
        "outbound_notifications": 0,
    }
    try:
        if not budget_id:
            created = account.budgets.create(expected)
            budget_id = created.budget.budget_configuration_id
        current = account.budgets.get(budget_id).budget
        assert current.filter.workspace_id.values == [WORKSPACE]
        assert current.resource_type == expected.resource_type
        assert current.include_external_spend == args.external_probe
        amounts = sorted(
            Decimal(x.quantity_threshold) for x in current.alert_configurations
        )
        assert amounts == sorted(
            Decimal(x.quantity_threshold) for x in expected.alert_configurations
        )
        assert all(
            all(
                a.action_type == b.ActionConfigurationType.BLOCK_USAGE
                for a in row.action_configurations
            )
            for row in current.alert_configurations
        )
        report.update(
            status="CONFIGURATION_PASS_ENFORCEMENT_PENDING",
            budget=current.as_dict(),
            external_provider_beta_coverage="CONFIGURED_NOT_YET_MEASURED"
            if args.external_probe
            else "NOT_APPLICABLE",
        )
    except Exception as error:
        report["failure"] = {"type": type(error).__name__, "message": str(error)[:700]}
        if (
            args.external_probe
            and isinstance(error, InvalidParameterValue)
            and "include_external_spend is not enabled" in str(error)
        ):
            report["status"] = "UNSUPPORTED_EXTERNAL_BETA"
            report["external_provider_beta_coverage"] = "NOT_ENABLED_IN_ACCOUNT"
            report["probe_budget_created"] = False
            report["primary_application_ledger_required_in_phase_10"] = True
        else:
            raise
    finally:
        if args.external_probe and budget_id:
            account.budgets.delete(budget_id)
            report["probe_budget_deleted"] = True
        save(
            ROOT
            / (
                "output/platform-foundation/external-budget-probe.json"
                if args.external_probe
                else "output/platform-foundation/genie-native-budget.json"
            ),
            report,
        )
    print(json.dumps(report))


if __name__ == "__main__":
    main()
