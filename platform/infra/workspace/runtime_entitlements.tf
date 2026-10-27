# Statement Execution requires SQL access in addition to warehouse CAN_USE.
# Scope is the two existing healthcare automation identities, not workspace users.
resource "databricks_entitlements" "runtime_sql" {
  for_each = {
    jobs       = "147109184184541"
    validation = "144866838711850"
  }
  service_principal_id        = each.value
  workspace_access           = true
  databricks_sql_access       = true
  allow_cluster_create       = false
  allow_instance_pool_create = false
}
