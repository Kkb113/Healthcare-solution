locals {
  catalogs            = toset(["hc_dev", "hc_test", "hc_prod", "hc_ops"])
  business_schemas    = toset(["landing", "reference", "bronze", "silver", "gold", "semantic", "features", "ml", "pred", "agent", "dq"])
  environment_schemas = { for pair in setproduct(["hc_dev", "hc_test", "hc_prod"], local.business_schemas) : "${pair[0]}.${pair[1]}" => { catalog = pair[0], schema = pair[1] } }
  operations_schemas  = { for name in ["security", "autopilot", "telemetry", "costs", "governance"] : "hc_ops.${name}" => { catalog = "hc_ops", schema = name } }
  probe_schemas       = { for name in ["hc_dev", "hc_test"] : "${name}._foundation_probe" => { catalog = name, schema = "_foundation_probe" } }
  schemas             = merge(local.environment_schemas, local.operations_schemas, local.probe_schemas)
  principals = {
    cicd       = "6640afb9-483e-46f6-8b83-405feca8c227"
    jobs       = "658faa8a-72bf-4285-bf4c-3cd25778ac5f"
    validation = "5d3656f0-eac7-4874-b49b-02f637df54ec"
  }
  groups = toset(["hcp-platform-admins", "hcp-data-engineers", "hcp-data-scientists", "hcp-analysts", "hcp-clinical", "hcp-finance", "hcp-operations", "hcp-auditors"])
}

resource "databricks_catalog" "healthcare" {
  for_each                       = local.catalogs
  name                           = each.value
  owner                          = "hcp-platform-admins"
  storage_root                   = "abfss://uc-managed@sthcpd054dev.dfs.core.windows.net/catalogs/${each.value}"
  isolation_mode                 = "ISOLATED"
  enable_predictive_optimization = "DISABLE"
  comment                        = "Synthetic healthcare POC; Terraform-owned governed ${each.value}; production data release is a later gate"
  properties                     = { managedby = "terraform", project = "healthcare-platform", synthetic = "true" }
  force_destroy                  = false
  depends_on                     = [databricks_external_location.healthcare]
  lifecycle { prevent_destroy = true }
}

resource "databricks_workspace_binding" "healthcare_catalog" {
  for_each       = databricks_catalog.healthcare
  securable_name = each.value.name
  securable_type = "catalog"
  workspace_id   = 7405619366453187
  binding_type   = "BINDING_TYPE_READ_WRITE"
}

resource "databricks_schema" "healthcare" {
  for_each                       = local.schemas
  catalog_name                   = databricks_catalog.healthcare[each.value.catalog].name
  name                           = each.value.schema
  owner                          = "hcp-platform-admins"
  enable_predictive_optimization = "DISABLE"
  comment                        = "Terraform-owned; explicit table policies/grants required before data exposure"
  properties                     = { managedby = "terraform", layer = each.value.schema, project = "healthcare-platform" }
  force_destroy                  = false
  lifecycle { prevent_destroy = true }
}

resource "databricks_volume" "landing" {
  for_each         = toset(["hc_dev", "hc_test", "hc_prod"])
  name             = "raw"
  catalog_name     = databricks_catalog.healthcare[each.value].name
  schema_name      = databricks_schema.healthcare["${each.value}.landing"].name
  volume_type      = "EXTERNAL"
  storage_location = "abfss://landing@sthcpd054dev.dfs.core.windows.net/${each.value}/raw"
  owner            = "hcp-platform-admins"
  comment          = "Environment-isolated immutable native deliveries; no source upload in platform foundation"
  lifecycle { prevent_destroy = true }
}

resource "databricks_grants" "catalog" {
  for_each = databricks_catalog.healthcare
  catalog  = each.value.name
  grant {
    principal  = "hcp-platform-admins"
    privileges = ["ALL_PRIVILEGES"]
  }
  dynamic "grant" {
    for_each = setunion(setsubtract(local.groups, toset(["hcp-platform-admins"])), toset(values(local.principals)))
    content {
      principal  = grant.value
      privileges = ["USE_CATALOG"]
    }
  }
}

resource "databricks_grants" "schema" {
  for_each = databricks_schema.healthcare
  schema   = each.value.id
  grant {
    principal  = "hcp-platform-admins"
    privileges = ["ALL_PRIVILEGES"]
  }
  dynamic "grant" {
    for_each = each.value.catalog_name == "hc_ops" && each.value.name == "security" ? toset([]) : setunion(setsubtract(local.groups, toset(["hcp-platform-admins"])), toset(values(local.principals)))
    content {
      principal = grant.value
      privileges = distinct(concat(
        ["USE_SCHEMA"],
        each.value.name == "_foundation_probe" && contains([local.principals.cicd, local.principals.jobs], grant.value) ? ["CREATE_TABLE", "CREATE_FUNCTION", "CREATE_MODEL", "SELECT", "MODIFY"] : [],
        each.value.name == "reference" && grant.value == local.principals.validation ? ["SELECT"] : [],
        each.value.catalog_name == "hc_ops" && each.value.name == "telemetry" && grant.value == local.principals.jobs ? ["SELECT"] : [],
        contains(["hc_dev", "hc_test"], each.value.catalog_name) && contains(["bronze", "silver", "gold", "features", "ml", "pred", "dq"], each.value.name) && grant.value == local.principals.jobs ? ["CREATE_TABLE", "CREATE_MODEL", "SELECT", "MODIFY"] : []
      ))
    }
  }
}

resource "databricks_grants" "landing_volume" {
  for_each = databricks_volume.landing
  volume   = each.value.id
  grant {
    principal  = "hcp-platform-admins"
    privileges = ["ALL_PRIVILEGES"]
  }
  grant {
    principal  = local.principals.cicd
    privileges = ["READ_VOLUME", "WRITE_VOLUME"]
  }
  grant {
    principal  = local.principals.jobs
    privileges = ["READ_VOLUME"]
  }
  grant {
    principal  = local.principals.validation
    privileges = ["READ_VOLUME"]
  }
}

output "platform_catalogs" { value = { for name, value in databricks_catalog.healthcare : name => value.id } }
output "landing_volumes" { value = { for name, value in databricks_volume.landing : name => value.volume_path } }
