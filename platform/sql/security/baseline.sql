-- Each command is deployed independently; a failed command aborts the migration.
CREATE TABLE IF NOT EXISTS hc_ops.security.principal_scope (
  binding_id STRING NOT NULL,
  tenant_id STRING NOT NULL,
  entra_object_id STRING NOT NULL,
  databricks_principal_id STRING NOT NULL,
  principal_name STRING NOT NULL,
  persona_id STRING,
  role STRING NOT NULL,
  facility_ids ARRAY<STRING> NOT NULL,
  phi_access BOOLEAN NOT NULL,
  valid_from TIMESTAMP NOT NULL,
  valid_to TIMESTAMP NOT NULL,
  revoked_at TIMESTAMP,
  scope_version BIGINT NOT NULL,
  asserted_by STRING NOT NULL,
  asserted_at TIMESTAMP NOT NULL
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true', 'hcp.classification' = 'security-control');
-- COMMAND ----------
ALTER TABLE hc_ops.security.principal_scope OWNER TO `hcp-platform-admins`;
-- COMMAND ----------
CREATE OR REPLACE FUNCTION hc_ops.security.facility_allowed(facility STRING)
RETURNS BOOLEAN
COMMENT 'Fail closed: latest assertion only; duplicates, expiry and revocation deny.'
RETURN COALESCE(array_contains((
  SELECT CASE WHEN COUNT(*) = 1 AND COUNT_IF(
    tenant_id = '807ebfbb-86ca-41a5-87df-d9c348b89f83'
    AND entra_object_id RLIKE '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    AND databricks_principal_id <> ''
    AND scope_version > 0
    AND role IN ('hcp-platform-admins', 'hcp-data-engineers', 'hcp-data-scientists',
                 'hcp-analysts', 'hcp-clinical', 'hcp-finance', 'hcp-operations',
                 'hcp-auditors', 'sp-hcp-jobs', 'sp-hcp-validation')
    AND valid_from <= current_timestamp() AND current_timestamp() < valid_to
    AND revoked_at IS NULL
  ) = 1 THEN first(facility_ids) ELSE CAST(array() AS ARRAY<STRING>) END
  FROM hc_ops.security.principal_scope
  WHERE lower(principal_name) = lower(current_user())
    AND scope_version = (
      SELECT MAX(scope_version) FROM hc_ops.security.principal_scope
      WHERE lower(principal_name) = lower(current_user())
    )
), facility), FALSE);
-- COMMAND ----------
ALTER FUNCTION hc_ops.security.facility_allowed OWNER TO `hcp-platform-admins`;
-- COMMAND ----------
CREATE OR REPLACE FUNCTION hc_ops.security.phi_allowed(facility STRING)
RETURNS BOOLEAN
RETURN hc_ops.security.facility_allowed(facility) AND COALESCE((
  SELECT COUNT(*) = 1 AND COUNT_IF(phi_access AND role IN ('hcp-clinical', 'hcp-platform-admins', 'sp-hcp-jobs', 'sp-hcp-validation')) = 1
  FROM hc_ops.security.principal_scope
  WHERE lower(principal_name) = lower(current_user())
    AND scope_version = (
      SELECT MAX(scope_version) FROM hc_ops.security.principal_scope
      WHERE lower(principal_name) = lower(current_user())
    )
), FALSE);
-- COMMAND ----------
ALTER FUNCTION hc_ops.security.phi_allowed OWNER TO `hcp-platform-admins`;
-- COMMAND ----------
CREATE OR REPLACE FUNCTION hc_ops.security.mask_person_name(value STRING, facility STRING)
RETURNS STRING
RETURN CASE WHEN hc_ops.security.phi_allowed(facility) THEN value ELSE '[REDACTED]' END;
-- COMMAND ----------
ALTER FUNCTION hc_ops.security.mask_person_name OWNER TO `hcp-platform-admins`;
-- COMMAND ----------
CREATE OR REPLACE VIEW hc_ops.telemetry.workspace_usage
AS SELECT * FROM system.billing.usage WHERE workspace_id = '7405619366453187';
-- COMMAND ----------
CREATE OR REPLACE VIEW hc_ops.telemetry.workspace_prices
AS SELECT p.* FROM system.billing.list_prices AS p
WHERE EXISTS (
  SELECT 1 FROM system.billing.usage AS u
  WHERE u.workspace_id = '7405619366453187' AND u.sku_name = p.sku_name
);
-- COMMAND ----------
CREATE OR REPLACE VIEW hc_ops.telemetry.workspace_job_runs
AS SELECT * FROM system.lakeflow.job_run_timeline WHERE workspace_id = '7405619366453187';
-- COMMAND ----------
CREATE OR REPLACE VIEW hc_ops.telemetry.workspace_lineage
AS SELECT * FROM system.access.table_lineage WHERE workspace_id = '7405619366453187';
