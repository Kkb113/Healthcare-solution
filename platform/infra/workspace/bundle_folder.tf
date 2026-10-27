# /Shared inherits users CAN_MANAGE and cannot be secured by a child ACL.
# Keep executable bundle artifacts outside that hierarchy; verify inherited ACLs.
resource "databricks_directory" "bundle_root" {
  path = "/hcp"
}

resource "databricks_permissions" "bundle_root" {
  directory_path = databricks_directory.bundle_root.path
  access_control {
    group_name       = "hcp-platform-admins"
    permission_level = "CAN_MANAGE"
  }
  access_control {
    service_principal_name = local.principals.cicd
    permission_level       = "CAN_MANAGE"
  }
  access_control {
    service_principal_name = local.principals.jobs
    permission_level       = "CAN_READ"
  }
}
