-- OFFLINE PHASE 0 CONTRACT ONLY. Do not deploy before the data-phase implementation authorizes it.
-- Target Unity Catalog catalog/schema must exist; namespaces below are placeholders for later configuration.
-- Scalar schemas; no uncounted JSON/array business facts. PK/FK metadata does not enforce integrity.

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`facility` (
  `facility_id` STRING NOT NULL,
  `facility_code` STRING NOT NULL,
  `facility_name` STRING NOT NULL,
  `city` STRING NOT NULL,
  `state_code` STRING NOT NULL,
  `postal_code` STRING NOT NULL,
  `timezone` STRING NOT NULL,
  `opened_on` DATE NOT NULL,
  `closed_on` DATE,
  `currency` STRING NOT NULL,
  `fiscal_calendar` STRING NOT NULL,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_facility` PRIMARY KEY (`facility_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`cost_center` (
  `cost_center_id` STRING NOT NULL,
  `facility_id` STRING NOT NULL,
  `parent_cost_center_id` STRING,
  `cost_center_code` STRING NOT NULL,
  `cost_center_name` STRING NOT NULL,
  `center_type` STRING NOT NULL,
  `active_from` DATE NOT NULL,
  `active_to` DATE,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_cost_center` PRIMARY KEY (`cost_center_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`location` (
  `location_id` STRING NOT NULL,
  `facility_id` STRING NOT NULL,
  `parent_location_id` STRING,
  `cost_center_id` STRING NOT NULL,
  `location_code` STRING NOT NULL,
  `location_name` STRING NOT NULL,
  `location_type` STRING NOT NULL,
  `service_line` STRING NOT NULL,
  `licensed_bed` BOOLEAN NOT NULL,
  `isolation_capable` BOOLEAN NOT NULL,
  `active_from` DATE NOT NULL,
  `active_to` DATE,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_location` PRIMARY KEY (`location_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`patient` (
  `patient_version_id` STRING NOT NULL,
  `patient_id` STRING NOT NULL,
  `mrn` STRING NOT NULL,
  `given_name` STRING NOT NULL,
  `middle_name` STRING,
  `family_name` STRING NOT NULL,
  `suffix` STRING,
  `birth_date` DATE NOT NULL,
  `administrative_sex` STRING NOT NULL,
  `gender_identity` STRING,
  `race_ethnicity` STRING NOT NULL,
  `preferred_language` STRING NOT NULL,
  `address_line` STRING NOT NULL,
  `city` STRING NOT NULL,
  `state_code` STRING NOT NULL,
  `postal_code` STRING NOT NULL,
  `test_email` STRING,
  `test_phone` STRING,
  `deceased_at` TIMESTAMP,
  `revision_no` INT NOT NULL,
  `valid_from` TIMESTAMP NOT NULL,
  `valid_to` TIMESTAMP,
  `known_from` TIMESTAMP NOT NULL,
  `known_to` TIMESTAMP,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_patient` PRIMARY KEY (`patient_version_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`worker_assignment` (
  `worker_assignment_id` STRING NOT NULL,
  `worker_id` STRING NOT NULL,
  `employee_number` STRING NOT NULL,
  `given_name` STRING NOT NULL,
  `family_name` STRING NOT NULL,
  `birth_date` DATE NOT NULL,
  `facility_id` STRING NOT NULL,
  `home_location_id` STRING NOT NULL,
  `cost_center_id` STRING NOT NULL,
  `manager_worker_id` STRING,
  `role` STRING NOT NULL,
  `specialty` STRING NOT NULL,
  `credential_code` STRING NOT NULL,
  `credential_valid_from` DATE NOT NULL,
  `credential_valid_to` DATE NOT NULL,
  `worker_type` STRING NOT NULL,
  `fte` DECIMAL(18,6) NOT NULL,
  `hourly_cost_rate` DECIMAL(18,2) NOT NULL,
  `currency` STRING NOT NULL,
  `hire_date` DATE NOT NULL,
  `termination_date` DATE,
  `revision_no` INT NOT NULL,
  `valid_from` TIMESTAMP NOT NULL,
  `valid_to` TIMESTAMP,
  `known_from` TIMESTAMP NOT NULL,
  `known_to` TIMESTAMP,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_worker_assignment` PRIMARY KEY (`worker_assignment_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`access_scope` (
  `access_scope_id` STRING NOT NULL,
  `grant_id` STRING NOT NULL,
  `principal_id` STRING NOT NULL,
  `worker_id` STRING NOT NULL,
  `role` STRING NOT NULL,
  `scope_type` STRING NOT NULL,
  `scope_key` STRING NOT NULL,
  `decision` STRING NOT NULL,
  `revision_no` INT NOT NULL,
  `valid_from` TIMESTAMP NOT NULL,
  `valid_to` TIMESTAMP,
  `known_from` TIMESTAMP NOT NULL,
  `known_to` TIMESTAMP,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_access_scope` PRIMARY KEY (`access_scope_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`payer_plan` (
  `payer_plan_id` STRING NOT NULL,
  `plan_code` STRING NOT NULL,
  `payer_name` STRING NOT NULL,
  `plan_name` STRING NOT NULL,
  `payer_type` STRING NOT NULL,
  `reimbursement_method` STRING NOT NULL,
  `authorization_required` BOOLEAN NOT NULL,
  `allowed_factor` DECIMAL(18,6) NOT NULL,
  `valid_from` DATE NOT NULL,
  `valid_to` DATE,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_payer_plan` PRIMARY KEY (`payer_plan_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`patient_coverage` (
  `coverage_version_id` STRING NOT NULL,
  `coverage_id` STRING NOT NULL,
  `patient_version_id` STRING NOT NULL,
  `payer_plan_id` STRING NOT NULL,
  `synthetic_member_id` STRING NOT NULL,
  `coverage_status` STRING NOT NULL,
  `revision_no` INT NOT NULL,
  `valid_from` TIMESTAMP NOT NULL,
  `valid_to` TIMESTAMP,
  `known_from` TIMESTAMP NOT NULL,
  `known_to` TIMESTAMP,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_patient_coverage` PRIMARY KEY (`coverage_version_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`catalog_item` (
  `catalog_item_id` STRING NOT NULL,
  `domain` STRING NOT NULL,
  `allergen_catalog_id` STRING,
  `code_system` STRING NOT NULL,
  `code` STRING NOT NULL,
  `version` STRING NOT NULL,
  `display` STRING NOT NULL,
  `valid_from` DATE NOT NULL,
  `valid_to` DATE,
  `base_unit` STRING,
  `formulation` STRING,
  `strength_per_base_unit` DECIMAL(18,6),
  `strength_unit` STRING,
  `pack_to_base_factor` DECIMAL(18,6),
  `account_class` STRING,
  `normal_balance` STRING,
  `clinical_group` STRING,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_catalog_item` PRIMARY KEY (`catalog_item_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`source_key_map` (
  `mapping_version_id` STRING NOT NULL,
  `mapping_id` STRING NOT NULL,
  `source_namespace` STRING NOT NULL,
  `entity_type` STRING NOT NULL,
  `source_key` STRING NOT NULL,
  `target_key` STRING NOT NULL,
  `mapping_status` STRING NOT NULL,
  `revision_no` INT NOT NULL,
  `valid_from` TIMESTAMP NOT NULL,
  `valid_to` TIMESTAMP,
  `known_from` TIMESTAMP NOT NULL,
  `known_to` TIMESTAMP,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_source_key_map` PRIMARY KEY (`mapping_version_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`encounter` (
  `encounter_version_id` STRING NOT NULL,
  `encounter_id` STRING NOT NULL,
  `episode_id` STRING NOT NULL,
  `previous_encounter_version_id` STRING,
  `patient_version_id` STRING NOT NULL,
  `facility_id` STRING NOT NULL,
  `location_id` STRING NOT NULL,
  `coverage_version_id` STRING NOT NULL,
  `attending_assignment_id` STRING,
  `encounter_class` STRING NOT NULL,
  `admission_source` STRING NOT NULL,
  `initial_acuity` INT NOT NULL,
  `arrival_at` TIMESTAMP NOT NULL,
  `admission_decision_at` TIMESTAMP,
  `admitted_at` TIMESTAMP,
  `medically_ready_at` TIMESTAMP,
  `discharged_at` TIMESTAMP,
  `disposition` STRING NOT NULL,
  `planned` BOOLEAN NOT NULL,
  `carry_in` BOOLEAN NOT NULL,
  `revision_no` INT NOT NULL,
  `known_from` TIMESTAMP NOT NULL,
  `known_to` TIMESTAMP,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_encounter` PRIMARY KEY (`encounter_version_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`clinical_condition` (
  `condition_version_id` STRING NOT NULL,
  `condition_id` STRING NOT NULL,
  `patient_version_id` STRING NOT NULL,
  `encounter_version_id` STRING,
  `catalog_item_id` STRING NOT NULL,
  `condition_type` STRING NOT NULL,
  `status` STRING NOT NULL,
  `diagnosis_rank` INT NOT NULL,
  `present_on_admission` STRING NOT NULL,
  `onset_at` TIMESTAMP,
  `resolved_at` TIMESTAMP,
  `reaction` STRING,
  `severity` STRING NOT NULL,
  `revision_no` INT NOT NULL,
  `valid_from` TIMESTAMP NOT NULL,
  `valid_to` TIMESTAMP,
  `known_from` TIMESTAMP NOT NULL,
  `known_to` TIMESTAMP,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_clinical_condition` PRIMARY KEY (`condition_version_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`clinical_event` (
  `clinical_event_version_id` STRING NOT NULL,
  `clinical_event_id` STRING NOT NULL,
  `encounter_version_id` STRING NOT NULL,
  `catalog_item_id` STRING,
  `parent_event_version_id` STRING,
  `author_assignment_id` STRING NOT NULL,
  `event_type` STRING NOT NULL,
  `occurred_at` TIMESTAMP NOT NULL,
  `period_end_at` TIMESTAMP,
  `order_start_at` TIMESTAMP,
  `order_end_at` TIMESTAMP,
  `dose_interval_hours` DECIMAL(18,6),
  `as_needed` BOOLEAN,
  `max_doses_per_day` INT,
  `administration_sequence` INT,
  `specimen_id` STRING,
  `collected_at` TIMESTAMP,
  `result_ready_at` TIMESTAMP,
  `document_signed_at` TIMESTAMP,
  `status` STRING NOT NULL,
  `numeric_value` DECIMAL(18,6),
  `value_unit` STRING,
  `text_value` STRING,
  `reference_low` DECIMAL(18,6),
  `reference_high` DECIMAL(18,6),
  `dose_quantity` DECIMAL(18,6),
  `dose_unit` STRING,
  `route` STRING,
  `consumed_base_quantity` DECIMAL(18,6),
  `consumption_group_key` STRING,
  `document_type` STRING,
  `aggregation` STRING NOT NULL,
  `revision_no` INT NOT NULL,
  `known_from` TIMESTAMP NOT NULL,
  `known_to` TIMESTAMP,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_clinical_event` PRIMARY KEY (`clinical_event_version_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`appointment` (
  `appointment_id` STRING NOT NULL,
  `patient_version_id` STRING NOT NULL,
  `location_id` STRING NOT NULL,
  `worker_assignment_id` STRING,
  `replacement_appointment_id` STRING,
  `resulting_encounter_version_id` STRING,
  `appointment_type` STRING NOT NULL,
  `booked_at` TIMESTAMP NOT NULL,
  `scheduled_start` TIMESTAMP NOT NULL,
  `scheduled_end` TIMESTAMP NOT NULL,
  `arrived_at` TIMESTAMP,
  `cancelled_at` TIMESTAMP,
  `no_show_recorded_at` TIMESTAMP,
  `cancel_reason` STRING,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_appointment` PRIMARY KEY (`appointment_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`bed_event` (
  `bed_event_id` STRING NOT NULL,
  `bed_location_id` STRING NOT NULL,
  `encounter_version_id` STRING,
  `corrects_bed_event_id` STRING,
  `transfer_group_id` STRING,
  `sequence_no` INT NOT NULL,
  `effective_at` TIMESTAMP NOT NULL,
  `event_type` STRING NOT NULL,
  `occupancy_state` STRING NOT NULL,
  `service_state` STRING NOT NULL,
  `staffing_enabled` BOOLEAN NOT NULL,
  `reserved` BOOLEAN NOT NULL,
  `reason` STRING NOT NULL,
  `delivery_at` TIMESTAMP NOT NULL,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_bed_event` PRIMARY KEY (`bed_event_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`staff_shift` (
  `shift_version_id` STRING NOT NULL,
  `shift_id` STRING NOT NULL,
  `worker_assignment_id` STRING NOT NULL,
  `location_id` STRING NOT NULL,
  `cost_center_id` STRING NOT NULL,
  `shift_type` STRING NOT NULL,
  `planned_start` TIMESTAMP NOT NULL,
  `planned_end` TIMESTAMP NOT NULL,
  `actual_start` TIMESTAMP,
  `actual_end` TIMESTAMP,
  `worked_hours` DECIMAL(18,6) NOT NULL,
  `productive_hours` DECIMAL(18,6) NOT NULL,
  `paid_nonproductive_hours` DECIMAL(18,6) NOT NULL,
  `unpaid_break_hours` DECIMAL(18,6) NOT NULL,
  `overtime_hours` DECIMAL(18,6) NOT NULL,
  `loaded_cost` DECIMAL(18,2) NOT NULL,
  `currency` STRING NOT NULL,
  `posting_group_key` STRING NOT NULL,
  `attendance_status` STRING NOT NULL,
  `revision_no` INT NOT NULL,
  `known_from` TIMESTAMP NOT NULL,
  `known_to` TIMESTAMP,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_staff_shift` PRIMARY KEY (`shift_version_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`inventory_movement` (
  `movement_id` STRING NOT NULL,
  `location_id` STRING NOT NULL,
  `catalog_item_id` STRING NOT NULL,
  `lot_id` STRING NOT NULL,
  `movement_type` STRING NOT NULL,
  `occurred_at` TIMESTAMP NOT NULL,
  `quantity_base` DECIMAL(18,6) NOT NULL,
  `unit_cost` DECIMAL(18,6) NOT NULL,
  `extended_cost` DECIMAL(18,2) NOT NULL,
  `expires_on` DATE NOT NULL,
  `transfer_group_id` STRING,
  `consumption_group_key` STRING,
  `nonpatient_waste_base` DECIMAL(18,6) NOT NULL,
  `reverses_movement_id` STRING,
  `posting_group_key` STRING NOT NULL,
  `currency` STRING NOT NULL,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_inventory_movement` PRIMARY KEY (`movement_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`service_charge` (
  `charge_id` STRING NOT NULL,
  `encounter_version_id` STRING NOT NULL,
  `catalog_item_id` STRING NOT NULL,
  `clinical_event_version_id` STRING,
  `cost_center_id` STRING NOT NULL,
  `service_from` DATE NOT NULL,
  `service_to` DATE NOT NULL,
  `revenue_category` STRING NOT NULL,
  `units` DECIMAL(18,6) NOT NULL,
  `unit_code` STRING NOT NULL,
  `unit_price` DECIMAL(18,2) NOT NULL,
  `billed_amount` DECIMAL(18,2) NOT NULL,
  `currency` STRING NOT NULL,
  `authorization_status` STRING NOT NULL,
  `authorization_known_at` TIMESTAMP NOT NULL,
  `reverses_charge_id` STRING,
  `posting_group_key` STRING NOT NULL,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_service_charge` PRIMARY KEY (`charge_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`claim` (
  `claim_id` STRING NOT NULL,
  `encounter_version_id` STRING NOT NULL,
  `coverage_version_id` STRING NOT NULL,
  `claim_number` STRING NOT NULL,
  `service_from` DATE NOT NULL,
  `service_to` DATE NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  `first_submitted_at` TIMESTAMP,
  `original_billed_amount` DECIMAL(18,2) NOT NULL,
  `opening_ar` DECIMAL(18,2) NOT NULL,
  `opening_contractual_adjustments` DECIMAL(18,2) NOT NULL,
  `opening_cash_collected` DECIMAL(18,2) NOT NULL,
  `opening_writeoffs` DECIMAL(18,2) NOT NULL,
  `carry_in` BOOLEAN NOT NULL,
  `currency` STRING NOT NULL,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_claim` PRIMARY KEY (`claim_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`claim_line` (
  `claim_line_id` STRING NOT NULL,
  `claim_id` STRING NOT NULL,
  `charge_id` STRING NOT NULL,
  `line_no` INT NOT NULL,
  `billed_amount` DECIMAL(18,2) NOT NULL,
  `expected_allowed_amount` DECIMAL(18,2) NOT NULL,
  `currency` STRING NOT NULL,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_claim_line` PRIMARY KEY (`claim_line_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`claim_event` (
  `claim_event_id` STRING NOT NULL,
  `claim_id` STRING NOT NULL,
  `claim_line_id` STRING,
  `denial_catalog_id` STRING,
  `reverses_claim_event_id` STRING,
  `event_type` STRING NOT NULL,
  `attempt_no` INT NOT NULL,
  `occurred_at` TIMESTAMP NOT NULL,
  `contractual_adjustment_delta` DECIMAL(18,2) NOT NULL,
  `payer_liability_delta` DECIMAL(18,2) NOT NULL,
  `patient_liability_delta` DECIMAL(18,2) NOT NULL,
  `cash_delta` DECIMAL(18,2) NOT NULL,
  `writeoff_delta` DECIMAL(18,2) NOT NULL,
  `recognized_revenue_delta` DECIMAL(18,2) NOT NULL,
  `ar_delta` DECIMAL(18,2) NOT NULL,
  `posting_group_key` STRING NOT NULL,
  `currency` STRING NOT NULL,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_claim_event` PRIMARY KEY (`claim_event_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`financial_posting` (
  `posting_id` STRING NOT NULL,
  `journal_id` STRING NOT NULL,
  `line_no` INT NOT NULL,
  `facility_id` STRING NOT NULL,
  `cost_center_id` STRING NOT NULL,
  `account_catalog_id` STRING NOT NULL,
  `posting_date` DATE NOT NULL,
  `service_from` DATE NOT NULL,
  `service_to` DATE NOT NULL,
  `debit_amount` DECIMAL(18,2) NOT NULL,
  `credit_amount` DECIMAL(18,2) NOT NULL,
  `currency` STRING NOT NULL,
  `source_domain` STRING NOT NULL,
  `source_group_key` STRING NOT NULL,
  `allocation_pool_key` STRING,
  `eligible_for_allocation` BOOLEAN NOT NULL,
  `reverses_posting_id` STRING,
  `known_from` TIMESTAMP NOT NULL,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_financial_posting` PRIMARY KEY (`posting_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`cost_allocation` (
  `allocation_id` STRING NOT NULL,
  `posting_id` STRING NOT NULL,
  `encounter_version_id` STRING,
  `cost_center_id` STRING NOT NULL,
  `allocation_run_id` STRING NOT NULL,
  `destination_type` STRING NOT NULL,
  `cost_category` STRING NOT NULL,
  `accounting_month` DATE NOT NULL,
  `driver_quantity` DECIMAL(18,6) NOT NULL,
  `driver_unit` STRING NOT NULL,
  `allocation_share` DECIMAL(18,6) NOT NULL,
  `allocated_amount` DECIMAL(18,2) NOT NULL,
  `currency` STRING NOT NULL,
  `known_from` TIMESTAMP NOT NULL,
  `supersedes_run_id` STRING,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_cost_allocation` PRIMARY KEY (`allocation_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`finance_monthly` (
  `finance_record_id` STRING NOT NULL,
  `facility_id` STRING NOT NULL,
  `cost_center_id` STRING NOT NULL,
  `account_catalog_id` STRING,
  `measure_code` STRING NOT NULL,
  `accounting_month` DATE NOT NULL,
  `scenario` STRING NOT NULL,
  `vintage_id` STRING NOT NULL,
  `published_at` TIMESTAMP NOT NULL,
  `amount` DECIMAL(18,2),
  `quantity` DECIMAL(18,6),
  `unit_code` STRING NOT NULL,
  `report_template_id` STRING NOT NULL,
  `source_file_id` STRING NOT NULL,
  `supersedes_vintage_id` STRING,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_finance_monthly` PRIMARY KEY (`finance_record_id`) NOT ENFORCED
) USING DELTA;

CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`facility_day_driver` (
  `facility_day_id` STRING NOT NULL,
  `facility_id` STRING NOT NULL,
  `calendar_date` DATE NOT NULL,
  `day_of_week` INT NOT NULL,
  `holiday` BOOLEAN NOT NULL,
  `season` STRING NOT NULL,
  `respiratory_index` DECIMAL(18,6) NOT NULL,
  `weather_index` DECIMAL(18,6) NOT NULL,
  `calendar_known_at` TIMESTAMP NOT NULL,
  `observations_known_at` TIMESTAMP NOT NULL,
  `calendar_source` STRING NOT NULL,
  `source_system` STRING NOT NULL,
  `source_record_id` STRING NOT NULL,
  `recorded_at` TIMESTAMP NOT NULL,
  `export_available_at` TIMESTAMP NOT NULL,
  `generation_run_id` STRING NOT NULL,
  CONSTRAINT `pk_facility_day_driver` PRIMARY KEY (`facility_day_id`) NOT ENFORCED
) USING DELTA;

-- Informational foreign keys, added after all table definitions. Execute only under a later authorized data phase.
-- This is a new-environment schema template, not an idempotent constraint migration or tested live deployment.
ALTER TABLE `healthcare_synthetic`.`core`.`cost_center` ADD CONSTRAINT `fk_cost_center_facility_id` FOREIGN KEY (`facility_id`) REFERENCES `healthcare_synthetic`.`core`.`facility` (`facility_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`cost_center` ADD CONSTRAINT `fk_cost_center_parent_cost_center_id` FOREIGN KEY (`parent_cost_center_id`) REFERENCES `healthcare_synthetic`.`core`.`cost_center` (`cost_center_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`location` ADD CONSTRAINT `fk_location_facility_id` FOREIGN KEY (`facility_id`) REFERENCES `healthcare_synthetic`.`core`.`facility` (`facility_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`location` ADD CONSTRAINT `fk_location_parent_location_id` FOREIGN KEY (`parent_location_id`) REFERENCES `healthcare_synthetic`.`core`.`location` (`location_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`location` ADD CONSTRAINT `fk_location_cost_center_id` FOREIGN KEY (`cost_center_id`) REFERENCES `healthcare_synthetic`.`core`.`cost_center` (`cost_center_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`worker_assignment` ADD CONSTRAINT `fk_worker_assignment_facility_id` FOREIGN KEY (`facility_id`) REFERENCES `healthcare_synthetic`.`core`.`facility` (`facility_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`worker_assignment` ADD CONSTRAINT `fk_worker_assignment_home_location_id` FOREIGN KEY (`home_location_id`) REFERENCES `healthcare_synthetic`.`core`.`location` (`location_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`worker_assignment` ADD CONSTRAINT `fk_worker_assignment_cost_center_id` FOREIGN KEY (`cost_center_id`) REFERENCES `healthcare_synthetic`.`core`.`cost_center` (`cost_center_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`patient_coverage` ADD CONSTRAINT `fk_patient_coverage_patient_version_id` FOREIGN KEY (`patient_version_id`) REFERENCES `healthcare_synthetic`.`core`.`patient` (`patient_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`patient_coverage` ADD CONSTRAINT `fk_patient_coverage_payer_plan_id` FOREIGN KEY (`payer_plan_id`) REFERENCES `healthcare_synthetic`.`core`.`payer_plan` (`payer_plan_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`catalog_item` ADD CONSTRAINT `fk_catalog_item_allergen_catalog_id` FOREIGN KEY (`allergen_catalog_id`) REFERENCES `healthcare_synthetic`.`core`.`catalog_item` (`catalog_item_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`encounter` ADD CONSTRAINT `fk_encounter_previous_encounter_version_id` FOREIGN KEY (`previous_encounter_version_id`) REFERENCES `healthcare_synthetic`.`core`.`encounter` (`encounter_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`encounter` ADD CONSTRAINT `fk_encounter_patient_version_id` FOREIGN KEY (`patient_version_id`) REFERENCES `healthcare_synthetic`.`core`.`patient` (`patient_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`encounter` ADD CONSTRAINT `fk_encounter_facility_id` FOREIGN KEY (`facility_id`) REFERENCES `healthcare_synthetic`.`core`.`facility` (`facility_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`encounter` ADD CONSTRAINT `fk_encounter_location_id` FOREIGN KEY (`location_id`) REFERENCES `healthcare_synthetic`.`core`.`location` (`location_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`encounter` ADD CONSTRAINT `fk_encounter_coverage_version_id` FOREIGN KEY (`coverage_version_id`) REFERENCES `healthcare_synthetic`.`core`.`patient_coverage` (`coverage_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`encounter` ADD CONSTRAINT `fk_encounter_attending_assignment_id` FOREIGN KEY (`attending_assignment_id`) REFERENCES `healthcare_synthetic`.`core`.`worker_assignment` (`worker_assignment_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`clinical_condition` ADD CONSTRAINT `fk_clinical_condition_patient_version_id` FOREIGN KEY (`patient_version_id`) REFERENCES `healthcare_synthetic`.`core`.`patient` (`patient_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`clinical_condition` ADD CONSTRAINT `fk_clinical_condition_encounter_version_id` FOREIGN KEY (`encounter_version_id`) REFERENCES `healthcare_synthetic`.`core`.`encounter` (`encounter_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`clinical_condition` ADD CONSTRAINT `fk_clinical_condition_catalog_item_id` FOREIGN KEY (`catalog_item_id`) REFERENCES `healthcare_synthetic`.`core`.`catalog_item` (`catalog_item_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`clinical_event` ADD CONSTRAINT `fk_clinical_event_encounter_version_id` FOREIGN KEY (`encounter_version_id`) REFERENCES `healthcare_synthetic`.`core`.`encounter` (`encounter_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`clinical_event` ADD CONSTRAINT `fk_clinical_event_catalog_item_id` FOREIGN KEY (`catalog_item_id`) REFERENCES `healthcare_synthetic`.`core`.`catalog_item` (`catalog_item_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`clinical_event` ADD CONSTRAINT `fk_clinical_event_parent_event_version_id` FOREIGN KEY (`parent_event_version_id`) REFERENCES `healthcare_synthetic`.`core`.`clinical_event` (`clinical_event_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`clinical_event` ADD CONSTRAINT `fk_clinical_event_author_assignment_id` FOREIGN KEY (`author_assignment_id`) REFERENCES `healthcare_synthetic`.`core`.`worker_assignment` (`worker_assignment_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`appointment` ADD CONSTRAINT `fk_appointment_patient_version_id` FOREIGN KEY (`patient_version_id`) REFERENCES `healthcare_synthetic`.`core`.`patient` (`patient_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`appointment` ADD CONSTRAINT `fk_appointment_location_id` FOREIGN KEY (`location_id`) REFERENCES `healthcare_synthetic`.`core`.`location` (`location_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`appointment` ADD CONSTRAINT `fk_appointment_worker_assignment_id` FOREIGN KEY (`worker_assignment_id`) REFERENCES `healthcare_synthetic`.`core`.`worker_assignment` (`worker_assignment_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`appointment` ADD CONSTRAINT `fk_appointment_replacement_appointment_id` FOREIGN KEY (`replacement_appointment_id`) REFERENCES `healthcare_synthetic`.`core`.`appointment` (`appointment_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`appointment` ADD CONSTRAINT `fk_appointment_resulting_encounter_version_id` FOREIGN KEY (`resulting_encounter_version_id`) REFERENCES `healthcare_synthetic`.`core`.`encounter` (`encounter_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`bed_event` ADD CONSTRAINT `fk_bed_event_bed_location_id` FOREIGN KEY (`bed_location_id`) REFERENCES `healthcare_synthetic`.`core`.`location` (`location_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`bed_event` ADD CONSTRAINT `fk_bed_event_encounter_version_id` FOREIGN KEY (`encounter_version_id`) REFERENCES `healthcare_synthetic`.`core`.`encounter` (`encounter_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`bed_event` ADD CONSTRAINT `fk_bed_event_corrects_bed_event_id` FOREIGN KEY (`corrects_bed_event_id`) REFERENCES `healthcare_synthetic`.`core`.`bed_event` (`bed_event_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`staff_shift` ADD CONSTRAINT `fk_staff_shift_worker_assignment_id` FOREIGN KEY (`worker_assignment_id`) REFERENCES `healthcare_synthetic`.`core`.`worker_assignment` (`worker_assignment_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`staff_shift` ADD CONSTRAINT `fk_staff_shift_location_id` FOREIGN KEY (`location_id`) REFERENCES `healthcare_synthetic`.`core`.`location` (`location_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`staff_shift` ADD CONSTRAINT `fk_staff_shift_cost_center_id` FOREIGN KEY (`cost_center_id`) REFERENCES `healthcare_synthetic`.`core`.`cost_center` (`cost_center_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`inventory_movement` ADD CONSTRAINT `fk_inventory_movement_location_id` FOREIGN KEY (`location_id`) REFERENCES `healthcare_synthetic`.`core`.`location` (`location_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`inventory_movement` ADD CONSTRAINT `fk_inventory_movement_catalog_item_id` FOREIGN KEY (`catalog_item_id`) REFERENCES `healthcare_synthetic`.`core`.`catalog_item` (`catalog_item_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`inventory_movement` ADD CONSTRAINT `fk_inventory_movement_reverses_movement_id` FOREIGN KEY (`reverses_movement_id`) REFERENCES `healthcare_synthetic`.`core`.`inventory_movement` (`movement_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`service_charge` ADD CONSTRAINT `fk_service_charge_encounter_version_id` FOREIGN KEY (`encounter_version_id`) REFERENCES `healthcare_synthetic`.`core`.`encounter` (`encounter_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`service_charge` ADD CONSTRAINT `fk_service_charge_catalog_item_id` FOREIGN KEY (`catalog_item_id`) REFERENCES `healthcare_synthetic`.`core`.`catalog_item` (`catalog_item_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`service_charge` ADD CONSTRAINT `fk_service_charge_clinical_event_version_id` FOREIGN KEY (`clinical_event_version_id`) REFERENCES `healthcare_synthetic`.`core`.`clinical_event` (`clinical_event_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`service_charge` ADD CONSTRAINT `fk_service_charge_cost_center_id` FOREIGN KEY (`cost_center_id`) REFERENCES `healthcare_synthetic`.`core`.`cost_center` (`cost_center_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`service_charge` ADD CONSTRAINT `fk_service_charge_reverses_charge_id` FOREIGN KEY (`reverses_charge_id`) REFERENCES `healthcare_synthetic`.`core`.`service_charge` (`charge_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`claim` ADD CONSTRAINT `fk_claim_encounter_version_id` FOREIGN KEY (`encounter_version_id`) REFERENCES `healthcare_synthetic`.`core`.`encounter` (`encounter_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`claim` ADD CONSTRAINT `fk_claim_coverage_version_id` FOREIGN KEY (`coverage_version_id`) REFERENCES `healthcare_synthetic`.`core`.`patient_coverage` (`coverage_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`claim_line` ADD CONSTRAINT `fk_claim_line_claim_id` FOREIGN KEY (`claim_id`) REFERENCES `healthcare_synthetic`.`core`.`claim` (`claim_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`claim_line` ADD CONSTRAINT `fk_claim_line_charge_id` FOREIGN KEY (`charge_id`) REFERENCES `healthcare_synthetic`.`core`.`service_charge` (`charge_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`claim_event` ADD CONSTRAINT `fk_claim_event_claim_id` FOREIGN KEY (`claim_id`) REFERENCES `healthcare_synthetic`.`core`.`claim` (`claim_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`claim_event` ADD CONSTRAINT `fk_claim_event_claim_line_id` FOREIGN KEY (`claim_line_id`) REFERENCES `healthcare_synthetic`.`core`.`claim_line` (`claim_line_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`claim_event` ADD CONSTRAINT `fk_claim_event_denial_catalog_id` FOREIGN KEY (`denial_catalog_id`) REFERENCES `healthcare_synthetic`.`core`.`catalog_item` (`catalog_item_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`claim_event` ADD CONSTRAINT `fk_claim_event_reverses_claim_event_id` FOREIGN KEY (`reverses_claim_event_id`) REFERENCES `healthcare_synthetic`.`core`.`claim_event` (`claim_event_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`financial_posting` ADD CONSTRAINT `fk_financial_posting_facility_id` FOREIGN KEY (`facility_id`) REFERENCES `healthcare_synthetic`.`core`.`facility` (`facility_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`financial_posting` ADD CONSTRAINT `fk_financial_posting_cost_center_id` FOREIGN KEY (`cost_center_id`) REFERENCES `healthcare_synthetic`.`core`.`cost_center` (`cost_center_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`financial_posting` ADD CONSTRAINT `fk_financial_posting_account_catalog_id` FOREIGN KEY (`account_catalog_id`) REFERENCES `healthcare_synthetic`.`core`.`catalog_item` (`catalog_item_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`financial_posting` ADD CONSTRAINT `fk_financial_posting_reverses_posting_id` FOREIGN KEY (`reverses_posting_id`) REFERENCES `healthcare_synthetic`.`core`.`financial_posting` (`posting_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`cost_allocation` ADD CONSTRAINT `fk_cost_allocation_posting_id` FOREIGN KEY (`posting_id`) REFERENCES `healthcare_synthetic`.`core`.`financial_posting` (`posting_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`cost_allocation` ADD CONSTRAINT `fk_cost_allocation_encounter_version_id` FOREIGN KEY (`encounter_version_id`) REFERENCES `healthcare_synthetic`.`core`.`encounter` (`encounter_version_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`cost_allocation` ADD CONSTRAINT `fk_cost_allocation_cost_center_id` FOREIGN KEY (`cost_center_id`) REFERENCES `healthcare_synthetic`.`core`.`cost_center` (`cost_center_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`finance_monthly` ADD CONSTRAINT `fk_finance_monthly_facility_id` FOREIGN KEY (`facility_id`) REFERENCES `healthcare_synthetic`.`core`.`facility` (`facility_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`finance_monthly` ADD CONSTRAINT `fk_finance_monthly_cost_center_id` FOREIGN KEY (`cost_center_id`) REFERENCES `healthcare_synthetic`.`core`.`cost_center` (`cost_center_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`finance_monthly` ADD CONSTRAINT `fk_finance_monthly_account_catalog_id` FOREIGN KEY (`account_catalog_id`) REFERENCES `healthcare_synthetic`.`core`.`catalog_item` (`catalog_item_id`) NOT ENFORCED;
ALTER TABLE `healthcare_synthetic`.`core`.`facility_day_driver` ADD CONSTRAINT `fk_facility_day_driver_facility_id` FOREIGN KEY (`facility_id`) REFERENCES `healthcare_synthetic`.`core`.`facility` (`facility_id`) NOT ENFORCED;
