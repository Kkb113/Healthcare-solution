terraform {
  required_version = "= 1.17.0"
  backend "azurerm" {}
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "= 1.140.0"
    }
  }
}

provider "databricks" {
  profile                     = "HEALTHCARE_AZURE"
  host                        = "https://adb-7405619366453187.7.azuredatabricks.net"
  auth_type                   = "azure-cli"
  azure_workspace_resource_id = "/subscriptions/d054aa64-95db-467b-a25c-387de70b15bd/resourceGroups/Databricks/providers/Microsoft.Databricks/workspaces/intellify-healthcare-dbw"
}

resource "databricks_storage_credential" "healthcare" {
  name    = "hcp_storage_dev"
  comment = "Dedicated healthcare ADLS identity; Terraform workspace foundation owned"
  azure_managed_identity {
    access_connector_id = "/subscriptions/d054aa64-95db-467b-a25c-387de70b15bd/resourceGroups/rg-hcp-dev/providers/Microsoft.Databricks/accessConnectors/ac-hcp-dev"
  }
}

resource "databricks_external_location" "healthcare" {
  for_each           = toset(["uc-managed", "landing"])
  name               = "hcp_${replace(each.value, "-", "_")}_dev"
  url                = "abfss://${each.value}@sthcpd054dev.dfs.core.windows.net/"
  credential_name    = databricks_storage_credential.healthcare.id
  comment            = "Dedicated healthcare ${each.value}; Terraform workspace foundation owned"
  skip_validation    = false
  enable_file_events = false
}
