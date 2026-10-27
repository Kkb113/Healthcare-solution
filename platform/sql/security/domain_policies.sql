CREATE OR REPLACE FUNCTION hc_ops.security.domain_allowed(domain STRING)
RETURNS BOOLEAN
RETURN COALESCE(array_contains((
  SELECT CASE WHEN COUNT(*) = 1 AND COUNT_IF(
    tenant_id = '807ebfbb-86ca-41a5-87df-d9c348b89f83'
    AND valid_from <= current_timestamp() AND current_timestamp() < valid_to
    AND revoked_at IS NULL AND scope_version > 0
  ) = 1 THEN
    CASE first(role)
      WHEN 'hcp-clinical' THEN array('clinical', 'quality', 'flow')
      WHEN 'hcp-finance' THEN array('finance', 'revenue')
      WHEN 'hcp-operations' THEN array('flow', 'workforce')
      WHEN 'hcp-analysts' THEN array('clinical', 'quality', 'flow', 'workforce', 'finance', 'revenue')
      WHEN 'hcp-data-engineers' THEN array('clinical', 'quality', 'flow', 'workforce', 'finance', 'revenue')
      WHEN 'hcp-data-scientists' THEN array('clinical', 'quality', 'flow', 'workforce', 'finance', 'revenue')
      WHEN 'hcp-auditors' THEN array('clinical', 'quality', 'flow', 'workforce', 'finance', 'revenue')
      WHEN 'hcp-platform-admins' THEN array('clinical', 'quality', 'flow', 'workforce', 'finance', 'revenue')
      WHEN 'sp-hcp-jobs' THEN array('clinical', 'quality', 'flow', 'workforce', 'finance', 'revenue')
      WHEN 'sp-hcp-validation' THEN array('clinical', 'quality', 'flow', 'workforce', 'finance', 'revenue')
      ELSE CAST(array() AS ARRAY<STRING>)
    END
  ELSE CAST(array() AS ARRAY<STRING>) END
  FROM hc_ops.security.principal_scope
  WHERE lower(principal_name) = lower(current_user())
    AND scope_version = (
      SELECT MAX(scope_version) FROM hc_ops.security.principal_scope
      WHERE lower(principal_name) = lower(current_user())
    )
), domain), FALSE);
-- COMMAND ----------
ALTER FUNCTION hc_ops.security.domain_allowed OWNER TO `hcp-platform-admins`;
-- COMMAND ----------
CREATE OR REPLACE FUNCTION hc_ops.security.scope_allowed(facility STRING, domain STRING)
RETURNS BOOLEAN
RETURN hc_ops.security.facility_allowed(facility) AND hc_ops.security.domain_allowed(domain);
-- COMMAND ----------
ALTER FUNCTION hc_ops.security.scope_allowed OWNER TO `hcp-platform-admins`;
