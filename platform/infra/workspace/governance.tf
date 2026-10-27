# Account objects are explicitly bound to this workspace, never account-wide.
provider "databricks" {
  alias      = "account"
  profile    = "HEALTHCARE_ACCOUNT"
  host       = "https://accounts.azuredatabricks.net"
  account_id = "aed328b4-17bf-43f0-9399-c470ad8ea1b5"
  auth_type  = "azure-cli"
}

locals {
  component_groups = {
    medallion = ["hcp-data-engineers"]
    ml        = ["hcp-data-scientists"]
    agent     = ["hcp-clinical", "hcp-finance", "hcp-operations"]
    autopilot = ["hcp-data-engineers"]
    genie     = ["hcp-analysts", "hcp-auditors"]
    rti       = ["hcp-operations"]
  }
  governed_tags = {
    hcp_domain    = ["healthcare", "platform"]
    hcp_owner     = ["platform", "clinical", "finance", "operations"]
    hcp_pii_class = ["synthetic", "synthetic-phi", "control", "nonpatient-fixture"]
    hcp_sla_tier  = ["batch", "interactive", "operational", "control"]
    hcp_layer     = concat(tolist(local.business_schemas), ["platform", "security", "telemetry", "governance", "autopilot", "costs", "probe"])
  }
}

resource "databricks_budget_policy" "component" {
  provider              = databricks.account
  for_each              = local.component_groups
  policy_name           = "hcp-${each.key}"
  binding_workspace_ids = [7405619366453187]
  custom_tags = [
    { key = "project", value = "healthcare-platform" },
    { key = "component", value = each.key },
    { key = "costcenter", value = "healthcare-poc" },
    { key = "managedby", value = "terraform" }
  ]
}

resource "databricks_access_control_rule_set" "component_policy" {
  provider = databricks.account
  for_each = local.component_groups
  name     = "accounts/aed328b4-17bf-43f0-9399-c470ad8ea1b5/budgetPolicies/${databricks_budget_policy.component[each.key].policy_id}/ruleSets/default"
  grant_rules {
    role       = "roles/budgetPolicy.manager"
    principals = ["users/karthik@intellifysolutions.com", "groups/hcp-platform-admins"]
  }
  grant_rules {
    role = "roles/budgetPolicy.user"
    principals = concat(
      [for group in each.value : "groups/${group}"],
      [for principal in values(local.principals) : "servicePrincipals/${principal}"]
    )
  }
}

# Manager does not imply run-as. Scope both CI and the approved operator to Jobs.
resource "databricks_access_control_rule_set" "jobs_run_as" {
  provider = databricks.account
  name     = "accounts/aed328b4-17bf-43f0-9399-c470ad8ea1b5/servicePrincipals/${local.principals.jobs}/ruleSets/default"
  grant_rules {
    role       = "roles/servicePrincipal.manager"
    principals = ["users/karthik@intellifysolutions.com"]
  }
  grant_rules {
    role       = "roles/servicePrincipal.user"
    principals = ["servicePrincipals/${local.principals.cicd}", "users/karthik@intellifysolutions.com"]
  }
}

resource "databricks_tag_policy" "healthcare" {
  for_each    = local.governed_tags
  tag_key     = each.key
  description = "Healthcare-only governed namespace. No shared/Retail tag policies altered."
  values      = [for value in each.value : { name = value }]
}

resource "databricks_entity_tag_assignment" "catalog_domain" {
  for_each    = databricks_catalog.healthcare
  entity_type = "catalogs"
  entity_name = each.value.name
  tag_key     = databricks_tag_policy.healthcare["hcp_domain"].tag_key
  tag_value   = "healthcare"
}

output "component_policy_ids" {
  value = { for name, policy in databricks_budget_policy.component : name => policy.policy_id }
}
