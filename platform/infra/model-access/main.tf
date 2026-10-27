terraform {
  required_version = "= 1.17.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 5.11.0"
    }
  }
}

# Model-only subscription exception. The Databricks workspace stays in d054... .
provider "azurerm" {
  subscription_id                 = "0725b5e7-75db-4c60-b5e9-928c3df3fcd1"
  tenant_id                       = "807ebfbb-86ca-41a5-87df-d9c348b89f83"
  resource_provider_registrations = "none"
  features {
    cognitive_account {
      purge_soft_delete_on_destroy = false
    }
  }
}

locals {
  tags = {
    project     = "healthcare-platform"
    owner       = "karthik"
    costcenter  = "healthcare-poc"
    environment = "readiness"
    managedby   = "terraform"
  }
}

resource "azurerm_resource_group" "model" {
  name     = "rg-hcp-model-access"
  location = "eastus"
  tags     = local.tags
}

resource "azurerm_cognitive_account" "luna" {
  name                          = "aoai-hcp-luna-0725fcd1"
  location                      = azurerm_resource_group.model.location
  resource_group_name           = azurerm_resource_group.model.name
  kind                          = "OpenAI"
  sku_name                      = "S0"
  custom_subdomain_name         = "aoai-hcp-luna-0725fcd1"
  local_auth_enabled            = false
  public_network_access_enabled = true
  tags                          = local.tags
}

resource "azurerm_cognitive_deployment" "luna" {
  name                 = "gpt-6-luna"
  cognitive_account_id = azurerm_cognitive_account.luna.id
  model {
    format  = "OpenAI"
    name    = "gpt-6-luna"
    version = "2026-09-22"
  }
  sku {
    name     = "DataZoneStandard"
    capacity = 100
  }
  version_upgrade_option = "NoAutoUpgrade"
}

# Only this operator can invoke the keyless readiness deployment initially.
resource "azurerm_role_assignment" "operator_inference" {
  name                 = uuidv5("dns", "hcp-luna-0725fcd1-operator-inference")
  scope                = azurerm_cognitive_account.luna.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = "5ee77c8e-621d-4953-9502-1be929c977e1"
  principal_type       = "User"
}

resource "azurerm_databricks_access_connector" "gateway" {
  name                = "ac-hcp-luna-gateway"
  location            = azurerm_resource_group.model.location
  resource_group_name = azurerm_resource_group.model.name
  identity {
    type = "SystemAssigned"
  }
  tags = local.tags
}

resource "azurerm_role_assignment" "gateway_inference" {
  name                 = uuidv5("dns", "hcp-luna-0725fcd1-gateway-inference")
  scope                = azurerm_cognitive_account.luna.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_databricks_access_connector.gateway.identity[0].principal_id
  principal_type       = "ServicePrincipal"
}

output "gateway_access_connector_id" {
  value = azurerm_databricks_access_connector.gateway.id
}

resource "azurerm_consumption_budget_resource_group" "model_monthly" {
  name              = "hcp-model-monthly"
  resource_group_id = azurerm_resource_group.model.id
  amount            = 5
  time_grain        = "Monthly"
  time_period {
    start_date = "2026-10-01T00:00:00Z"
    end_date   = "2027-10-01T00:00:00Z"
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

resource "azurerm_consumption_budget_resource_group" "model_build" {
  name              = "hcp-model-build"
  resource_group_id = azurerm_resource_group.model.id
  amount            = 35
  time_grain        = "Annually"
  time_period {
    start_date = "2026-10-01T00:00:00Z"
    end_date   = "2027-10-01T00:00:00Z"
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

output "model_endpoint" {
  value = azurerm_cognitive_account.luna.endpoint
}

output "model_resource_id" {
  value = azurerm_cognitive_account.luna.id
}
