terraform {
  required_version = "= 1.17.0"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "= 5.11.0" }
    azuread = { source = "hashicorp/azuread", version = "= 3.10.0" }
  }
}

provider "azurerm" {
  subscription_id                 = "d054aa64-95db-467b-a25c-387de70b15bd"
  tenant_id                       = "807ebfbb-86ca-41a5-87df-d9c348b89f83"
  resource_provider_registrations = "none"
  storage_use_azuread             = true
  features {}
}

provider "azuread" {
  tenant_id = "807ebfbb-86ca-41a5-87df-d9c348b89f83"
}

locals {
  tags       = { project = "healthcare-platform", owner = "karthik", costcenter = "healthcare-poc", environment = "dev", managedby = "terraform" }
  groups     = toset(["hcp-platform-admins", "hcp-data-engineers", "hcp-data-scientists", "hcp-analysts", "hcp-clinical", "hcp-finance", "hcp-operations", "hcp-auditors"])
  principals = toset(["sp-hcp-cicd", "sp-hcp-jobs", "sp-hcp-validation"])
}

resource "azurerm_resource_group" "healthcare" {
  name     = "rg-hcp-dev"
  location = "eastus"
  tags     = local.tags
  lifecycle { prevent_destroy = true }
}

# Existing SERVERLESS workspace is referenced, never recreated or imported as
# a classic workspace. This foundation owns only dedicated healthcare resources.
resource "azurerm_storage_account" "healthcare" {
  name                            = "sthcpd054dev"
  resource_group_name             = azurerm_resource_group.healthcare.name
  location                        = azurerm_resource_group.healthcare.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  is_hns_enabled                  = true
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = false
  tags                            = local.tags
  lifecycle { prevent_destroy = true }
  blob_properties {
    delete_retention_policy { days = 7 }
    container_delete_retention_policy { days = 7 }
  }
}

resource "azurerm_storage_container" "healthcare" {
  for_each              = toset(["uc-managed", "landing", "checkpoints", "tfstate", "control"])
  name                  = each.value
  storage_account_id    = azurerm_storage_account.healthcare.id
  container_access_type = "private"
  depends_on            = [azurerm_role_assignment.operator_storage]
  lifecycle { prevent_destroy = true }
}

# Tier only delivered landing files. State, checkpoints, control records and
# Unity Catalog managed data must never inherit an automatic deletion rule.
resource "azurerm_storage_management_policy" "landing" {
  storage_account_id = azurerm_storage_account.healthcare.id
  rule {
    name    = "cool-landing-after-ninety-days"
    enabled = true
    filters {
      prefix_match = ["landing/"]
      blob_types   = ["blockBlob"]
    }
    actions {
      base_blob { tier_to_cool_after_days_since_modification_greater_than = 90 }
    }
  }
}

resource "azurerm_key_vault" "healthcare" {
  name                       = "kv-hcp-d054-dev"
  resource_group_name        = azurerm_resource_group.healthcare.name
  location                   = azurerm_resource_group.healthcare.location
  tenant_id                  = "807ebfbb-86ca-41a5-87df-d9c348b89f83"
  sku_name                   = "standard"
  rbac_authorization_enabled = true
  soft_delete_retention_days = 7
  tags                       = local.tags
  lifecycle { prevent_destroy = true }
}

resource "azurerm_role_assignment" "platform_secrets" {
  name                 = uuidv5("dns", "hcp-d054-dev-platform-secrets")
  scope                = azurerm_key_vault.healthcare.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = azuread_group.healthcare["hcp-platform-admins"].object_id
  principal_type       = "Group"
}

resource "azurerm_databricks_access_connector" "healthcare" {
  name                = "ac-hcp-dev"
  resource_group_name = azurerm_resource_group.healthcare.name
  location            = azurerm_resource_group.healthcare.location
  identity { type = "SystemAssigned" }
  tags = local.tags
  lifecycle { prevent_destroy = true }
}

resource "azurerm_role_assignment" "connector_storage" {
  name                 = uuidv5("dns", "hcp-d054-dev-connector-storage")
  scope                = azurerm_storage_account.healthcare.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.healthcare.identity[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "operator_storage" {
  name                 = uuidv5("dns", "hcp-d054-dev-operator-storage")
  scope                = azurerm_storage_account.healthcare.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = "5ee77c8e-621d-4953-9502-1be929c977e1"
  principal_type       = "User"
}

resource "azuread_group" "healthcare" {
  for_each         = local.groups
  display_name     = each.value
  security_enabled = true
  owners           = ["5ee77c8e-621d-4953-9502-1be929c977e1"]
  members          = each.value == "hcp-platform-admins" ? ["5ee77c8e-621d-4953-9502-1be929c977e1"] : []
  # Membership is an Entra business/security decision after bootstrap. Routine
  # infrastructure apply must not erase an administrator's subsequent changes.
  lifecycle { ignore_changes = [members] }
}

resource "azuread_application" "foundation" {
  for_each         = local.principals
  display_name     = each.value
  sign_in_audience = "AzureADMyOrg"
  owners           = ["5ee77c8e-621d-4953-9502-1be929c977e1"]
}

resource "azuread_service_principal" "foundation" {
  for_each  = local.principals
  client_id = azuread_application.foundation[each.value].client_id
  owners    = ["5ee77c8e-621d-4953-9502-1be929c977e1"]
}

resource "azuread_application_federated_identity_credential" "github_main" {
  application_id = azuread_application.foundation["sp-hcp-cicd"].id
  display_name   = "github-healthcare-main"
  audiences      = ["api://AzureADTokenExchange"]
  issuer         = "https://token.actions.githubusercontent.com"
  subject        = "repo:Kkb113@176327882/Healthcare-solution@1430602110:ref:refs/heads/main"
}

# CI can manage the dedicated foundation RG, and read only the existing workspace.
# It receives no Owner/User Access Administrator or business-data grants.
resource "azurerm_role_assignment" "ci_foundation" {
  name                 = uuidv5("dns", "hcp-d054-dev-ci-foundation")
  scope                = azurerm_resource_group.healthcare.id
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.foundation["sp-hcp-cicd"].object_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "ci_workspace_read" {
  name                 = uuidv5("dns", "hcp-d054-dev-ci-workspace-read")
  scope                = "/subscriptions/d054aa64-95db-467b-a25c-387de70b15bd/resourceGroups/Databricks/providers/Microsoft.Databricks/workspaces/intellify-healthcare-dbw"
  role_definition_name = "Reader"
  principal_id         = azuread_service_principal.foundation["sp-hcp-cicd"].object_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "ci_state" {
  name                 = uuidv5("dns", "hcp-d054-dev-ci-state")
  scope                = azurerm_storage_container.healthcare["tfstate"].id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azuread_service_principal.foundation["sp-hcp-cicd"].object_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "ci_control" {
  name                 = uuidv5("dns", "hcp-d054-dev-ci-control")
  scope                = azurerm_storage_container.healthcare["control"].id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azuread_service_principal.foundation["sp-hcp-cicd"].object_id
  principal_type       = "ServicePrincipal"
}

output "foundation" {
  value = {
    resource_group      = azurerm_resource_group.healthcare.name
    storage_account     = azurerm_storage_account.healthcare.name
    oidc_subject        = azuread_application_federated_identity_credential.github_main.subject
    access_connector_id = azurerm_databricks_access_connector.healthcare.id
    key_vault_id        = azurerm_key_vault.healthcare.id
    groups              = { for name, group in azuread_group.healthcare : name => group.object_id }
    principals = { for name, app in azuread_application.foundation : name => {
      client_id = app.client_id
      object_id = azuread_service_principal.foundation[name].object_id
    } }
  }
}

resource "azurerm_consumption_budget_subscription" "monthly" {
  name            = "hcp-platform-monthly"
  subscription_id = "/subscriptions/d054aa64-95db-467b-a25c-387de70b15bd"
  amount          = 55
  time_grain      = "Monthly"
  time_period {
    start_date = "2026-10-01T00:00:00Z"
    end_date   = "2027-10-01T00:00:00Z"
  }
  filter {
    tag {
      name   = "project"
      values = ["healthcare-platform"]
    }
  }
  dynamic "notification" {
    for_each = toset([50, 80, 100])
    content {
      enabled        = true
      threshold      = notification.value
      operator       = "GreaterThanOrEqualTo"
      contact_emails = ["karthik@intellifysolutions.com"]
    }
  }
}

resource "azurerm_consumption_budget_subscription" "build" {
  name            = "hcp-platform-build"
  subscription_id = "/subscriptions/d054aa64-95db-467b-a25c-387de70b15bd"
  amount          = 165
  time_grain      = "Annually"
  time_period {
    start_date = "2026-10-01T00:00:00Z"
    end_date   = "2027-10-01T00:00:00Z"
  }
  filter {
    tag {
      name   = "project"
      values = ["healthcare-platform"]
    }
  }
  dynamic "notification" {
    for_each = toset([25, 50, 75, 90])
    content {
      enabled        = true
      threshold      = notification.value
      operator       = "GreaterThanOrEqualTo"
      contact_emails = ["karthik@intellifysolutions.com"]
    }
  }
}
