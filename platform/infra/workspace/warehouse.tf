# A single physical warehouse serves the isolated logical targets. This is the
# aggregate one-cluster cost profile, not one concurrently running cluster per target.
resource "databricks_sql_endpoint" "healthcare" {
  name                      = "hcp-sql-shared"
  cluster_size              = "2X-Small"
  min_num_clusters          = 1
  max_num_clusters          = 1
  auto_stop_mins            = 5
  enable_serverless_compute = true
  warehouse_type            = "PRO"
  enable_photon             = true
  no_wait                   = true
  channel { name = "CHANNEL_NAME_CURRENT" }
  tags {
    custom_tags {
      key   = "project"
      value = "healthcare-platform"
    }
    custom_tags {
      key   = "component"
      value = "shared-sql"
    }
    custom_tags {
      key   = "managedby"
      value = "terraform"
    }
  }
  timeouts { create = "8m" }
}

resource "databricks_permissions" "warehouse" {
  sql_endpoint_id = databricks_sql_endpoint.healthcare.id
  access_control {
    group_name       = "hcp-platform-admins"
    permission_level = "CAN_MANAGE"
  }
  dynamic "access_control" {
    for_each = setsubtract(local.groups, toset(["hcp-platform-admins"]))
    content {
      group_name       = access_control.value
      permission_level = "CAN_USE"
    }
  }
  dynamic "access_control" {
    for_each = toset(values(local.principals))
    content {
      service_principal_name = access_control.value
      permission_level       = access_control.value == local.principals.cicd ? "CAN_MANAGE" : "CAN_USE"
    }
  }
}

output "warehouse_id" {
  value = databricks_sql_endpoint.healthcare.id
}
