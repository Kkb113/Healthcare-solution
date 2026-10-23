"""Author/render Phase 0 metadata only. This script never generates patient data."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"
TABLES = []

def c(name, dtype, description, nullable=False, ref=None, values=None, unit=None):
    result = {"name": name, "type": dtype, "nullable": nullable,
              "description": description, "authority": "table_source",
              "correction_policy": "append_revision_or_reversal"}
    if ref:
        result["references"] = ref
    if values:
        result["allowed_values"] = values.split("|")
    if unit:
        result["unit"] = unit
    return result

def key(name, description, ref=None, nullable=False):
    return c(name, "STRING", description, nullable, ref)

def text(name, description, nullable=False, values=None):
    return c(name, "STRING", description, nullable, values=values)

def ts(name, description, nullable=False):
    return c(name, "TIMESTAMP", description, nullable, unit="UTC instant")

def date(name, description, nullable=False):
    return c(name, "DATE", description, nullable, unit="local calendar date")

def num(name, description, nullable=False, unit=None):
    return c(name, "DECIMAL(18,6)", description, nullable, unit=unit)

def money(name, description, nullable=False):
    return c(name, "DECIMAL(18,2)", description, nullable, unit="row currency")

def flag(name, description):
    return c(name, "BOOLEAN", description)

def integer(name, description):
    return c(name, "INT", description)

def history():
    return [integer("revision_no", "Monotone revision within the stable business identity, starting at 1."),
            ts("valid_from", "Start of business validity; inclusive."),
            ts("valid_to", "End of business validity; exclusive; null means open.", True),
            ts("known_from", "First source knowledge of this revision; no backdating."),
            ts("known_to", "Knowledge supersession time; exclusive; null means not superseded.", True)]

def table(name, pk, grain, rows, source, fields, unique=(), notes=""):
    common = [text("source_system", "Source authority namespace; synthetic source, never a live-system claim."),
              text("source_record_id", "Stable source record/version key; scoped by source_system."),
              ts("recorded_at", "Source recording timestamp; knowledge/availability begins no earlier than this instant."),
              ts("export_available_at", "First time this version can appear in an export/delivery; not event time."),
              text("generation_run_id", "Generation manifest identifier; excluded from future model features.")]
    TABLES.append({"name": name, "primary_key": [pk], "grain": grain,
                   "planned_rows": rows, "source_authority": source,
                   "history_policy": "As stated by grain; referenced rows never physically deleted.",
                   "notes": notes, "unique_keys": [list(x) for x in unique],
                   "columns": fields + common,
                   "rule_ids": [], "classification": "wholly_synthetic_business_data"})

table("facility", "facility_id", "One fictional hospital; stable identity and geography.", 3, "ORG_MASTER", [
    key("facility_id", "Canonical hospital ID."), text("facility_code", "Unique readable hospital code."),
    text("facility_name", "Believable fictional hospital name; no numbered placeholder."),
    text("city", "Fictional hospital's modeled Illinois city."), text("state_code", "US state postal code."),
    text("postal_code", "Public postal area, not a copied personal address."), text("timezone", "IANA timezone; America/Chicago in v1."),
    date("opened_on", "First operating date."), date("closed_on", "Last operating date, exclusive.", True),
    text("currency", "ISO currency; USD."), text("fiscal_calendar", "CALENDAR_YEAR in v1.")], [("facility_code",)])

table("cost_center", "cost_center_id", "One stable financial responsibility center; replacements receive a new ID.", 45, "WORKDAY", [
    key("cost_center_id", "Canonical financial responsibility center."),
    key("facility_id", "Owning hospital.", "facility.facility_id"),
    key("parent_cost_center_id", "Financial parent; acyclic hierarchy.", "cost_center.cost_center_id", True),
    text("cost_center_code", "Canonical cost-center code."), text("cost_center_name", "Realistic named responsibility center."),
    text("center_type", "Center purpose.", values="CLINICAL|SUPPORT|ADMINISTRATION|SHARED"),
    date("active_from", "Activation date."), date("active_to", "Exclusive retirement date.", True)], [("cost_center_code",)])

table("location", "location_id", "One department, ward, room or physical bed; hierarchical location, not an occupancy snapshot.", 150, "ADT_LOCATION", [
    key("location_id", "Stable location identity."), key("facility_id", "Owning hospital.", "facility.facility_id"),
    key("parent_location_id", "Location parent in the same hospital.", "location.location_id", True),
    key("cost_center_id", "Default responsibility; event-time costs retain their actual center.", "cost_center.cost_center_id"),
    text("location_code", "Readable location code."), text("location_name", "Named ward, room or bed."),
    text("location_type", "Location grain.", values="DEPARTMENT|UNIT|ROOM|BED"),
    text("service_line", "Capability.", values="ED|AMBULATORY|MEDICINE|SURGERY|ICU|STEP_DOWN|SUPPORT"),
    flag("licensed_bed", "True only on inpatient BED rows counted in licensed capacity."),
    flag("isolation_capable", "Placement capability; distinct from current availability."),
    date("active_from", "Commissioning date."), date("active_to", "Exclusive retirement date.", True)], [("facility_id", "location_code")],
    "150 = 15 departments + 15 units + 48 rooms + 72 beds. Physical parents stay stable; service/staffing closures are bed events.")

table("patient", "patient_version_id", "One bitemporal demographic version of a persistent synthetic patient.", 22000, "EHR_REGISTRATION", [
    key("patient_version_id", "Immutable demographic version key."), key("patient_id", "Stable identity across demographic versions."),
    text("mrn", "Stable synthetic enterprise medical record number."), text("given_name", "Birth-cohort-weighted plausible first name."),
    text("middle_name", "Optional realistic middle name/initial.", True), text("family_name", "Plausible surname; duplicates permitted."),
    text("suffix", "Optional suffix.", True), date("birth_date", "Birth date; event age is derived using local calendar birthdays."),
    text("administrative_sex", "Source administrative field, not inferred from name.", values="F|M|X|UNKNOWN"),
    text("gender_identity", "Optional self-described administrative attribute, never inferred.", True),
    text("race_ethnicity", "Configured self-report category, not assigned from surname."), text("preferred_language", "Language preference code."),
    text("address_line", "Fictional street address with plausible formatting."), text("city", "Modeled city."),
    text("state_code", "US state."), text("postal_code", "Geographically consistent postal area."),
    text("test_email", "Non-deliverable contact under .example.", True), text("test_phone", "Reserved fictional contact, not real patient contact.", True),
    ts("deceased_at", "Known death occurrence; later administrative transactions are permitted.", True),
    *history()], [("patient_id", "revision_no")], "20,000 stable patients + 2,000 demographic revisions. Adult cohort only; no guardian/newborn entity is required.")

table("worker_assignment", "worker_assignment_id", "One bitemporal version of one worker's single exclusive primary assignment.", 900, "WORKDAY", [
    key("worker_assignment_id", "Immutable worker/assignment version."), key("worker_id", "Stable worker identity; same worker across versions."),
    text("employee_number", "Stable synthetic employee reference."), text("given_name", "Plausible first name."),
    text("family_name", "Plausible surname."), date("birth_date", "Worker birth date."),
    key("facility_id", "Primary employer facility.", "facility.facility_id"),
    key("home_location_id", "Home clinical/support unit.", "location.location_id"),
    key("cost_center_id", "Primary responsibility center.", "cost_center.cost_center_id"),
    key("manager_worker_id", "Logical stable worker reference resolved bitemporally, not a FK to a nonunique column.", nullable=True),
    text("role", "One primary role; baseline excludes multiple concurrent assignments.", values="PHYSICIAN|RN|LPN|THERAPIST|TECHNICIAN|PHARMACIST|HOUSEKEEPING|ADMIN"),
    text("specialty", "Role-appropriate specialty or generalist."),
    text("credential_code", "Primary role credential; secondary credentials outside v1."),
    date("credential_valid_from", "Credential valid start."), date("credential_valid_to", "Credential expiry, exclusive."),
    text("worker_type", "Employment arrangement.", values="EMPLOYEE|AGENCY|CONTRACT"),
    num("fte", "Contract FTE fraction.", unit="FTE"), money("hourly_cost_rate", "Loaded hourly cost rate, including employer burden."),
    text("currency", "USD."), date("hire_date", "Start of employment."), date("termination_date", "Employment end, exclusive.", True),
    *history()], [("worker_id", "revision_no")], "300 stable workers and 600 assignment/name/rate/credential revisions. Temporary worked-unit changes are shift rows; physicians use synthetic provider identifiers, not real NPI identities.")

table("access_scope", "access_scope_id", "One bitemporal grant/revocation version for a synthetic principal and business scope.", 1800, "WORKDAY_SECURITY", [
    key("access_scope_id", "Grant version identity."), key("grant_id", "Stable grant identity."),
    text("principal_id", "Synthetic identity-provider subject; no live access is granted."),
    key("worker_id", "Logical stable worker link, resolved through worker_assignment."),
    text("role", "Read-only demo entitlement.", values="NETWORK_ANALYST|FACILITY_MANAGER|UNIT_MANAGER|FINANCE_ANALYST|HR_ANALYST"),
    text("scope_type", "Typed scope target.", values="NETWORK|FACILITY|LOCATION|COST_CENTER"),
    key("scope_key", "Typed scope key; NETWORK is the explicit ALL_NETWORK sentinel."),
    text("decision", "Grant outcome.", values="ALLOW|REVOKED"), *history()], [("grant_id", "revision_no")])

table("payer_plan", "payer_plan_id", "One versioned fictional payer product/contract.", 24, "PAYER_CONTRACT", [
    key("payer_plan_id", "Contract version identity."), text("plan_code", "Stable product code."),
    text("payer_name", "Fictional payer name."), text("plan_name", "Readable product name."),
    text("payer_type", "Payer class.", values="MEDICARE|MEDICAID|COMMERCIAL|SELF_PAY"),
    text("reimbursement_method", "Simplified contractual method.", values="CASE_RATE|FEE_SCHEDULE|PER_DIEM|SELF_PAY"),
    flag("authorization_required", "Default; service-specific overrides come from source mapping rules."),
    num("allowed_factor", "Configured reimbursement fraction, not a real contract.", unit="fraction"),
    date("valid_from", "Contract start."), date("valid_to", "Exclusive contract end.", True)], [("plan_code", "valid_from")])

table("patient_coverage", "coverage_version_id", "One bitemporal primary coverage enrollment interval/version.", 28000, "EHR_COVERAGE", [
    key("coverage_version_id", "Immutable coverage version."), key("coverage_id", "Stable enrollment identity."),
    key("patient_version_id", "Identity assertion; stable patient consistency checked across versions.", "patient.patient_version_id"),
    key("payer_plan_id", "Versioned payer contract.", "payer_plan.payer_plan_id"),
    text("synthetic_member_id", "Synthetic insurance membership reference."),
    text("coverage_status", "Enrollment state.", values="ACTIVE|EXPIRED|CANCELLED|SELF_PAY"),
    *history()], [("coverage_id", "revision_no")], "One primary payer at an instant; secondary coordination excluded explicitly. 20,000 opening enrollments plus changes/revisions.")

table("catalog_item", "catalog_item_id", "One code/product/account version within a typed, validated vocabulary.", 3000, "REFERENCE_CATALOG", [
    key("catalog_item_id", "Code version key."), text("domain", "Typed vocabulary.", values="DIAGNOSIS|PROCEDURE|OBSERVATION|LAB|MEDICATION|ALLERGEN|SUPPLY|ACCOUNT|DENIAL"),
    key("allergen_catalog_id", "MEDICATION product's modeled ingredient/allergen family; target domain ALLERGEN.", "catalog_item.catalog_item_id", True),
    text("code_system", "ICD-10-CM/PCS, LOINC, local test service/formulary/account or denial namespace."),
    text("code", "Versioned code string."), text("version", "Published release or synthetic catalog version."),
    text("display", "Human-readable description; no placeholder labels."),
    date("valid_from", "Code validity start."), date("valid_to", "Exclusive code validity end.", True),
    text("base_unit", "UCUM or documented stock base unit.", True),
    text("formulation", "MEDICATION-only formulation, such as tablet, oral solution or inhalation product.", True),
    num("strength_per_base_unit", "Medication strength per stock base unit; required for medication products.", True, "strength unit/base unit"),
    text("strength_unit", "Medication strength unit.", True), num("pack_to_base_factor", "Positive pack/base conversion.", True, "base units/pack"),
    text("account_class", "ACCOUNT-only classification.", True, "ASSET|LIABILITY|EQUITY|REVENUE|EXPENSE"),
    text("normal_balance", "ACCOUNT-only normal side.", True, "DEBIT|CREDIT"),
    text("clinical_group", "Reviewed pathway or service grouping.", True)], [("domain", "code_system", "code", "version")],
    "A vocabulary table, not an untyped entity/attribute store. No JSON payloads or hidden clinical line arrays.")

table("source_key_map", "mapping_version_id", "One bitemporal typed crosswalk or association mapping.", 10000, "INTEGRATION_CONTROL", [
    key("mapping_version_id", "Immutable mapping version."), key("mapping_id", "Stable crosswalk business identity."),
    text("source_namespace", "Workday/Axiom/EHR source namespace."), text("entity_type", "Typed target mapping.", values="PATIENT|WORKER|LOCATION|COST_CENTER|CATALOG|PAYER_PLAN|UNIT_COST_CENTER"),
    text("source_key", "Opaque source identifier; exact matching only."),
    key("target_key", "Target stable ID or immutable row key, as specified by entity_type."),
    text("mapping_status", "Approved exact mapping or controlled unmapped fault.", values="MAPPED|UNMAPPED"),
    *history()], [("mapping_id", "revision_no")], "Only alternate keys and associations need rows. Default source keys are retained on every business row; no silent fuzzy matching.")

table("encounter", "encounter_version_id", "One knowledge revision of an ED, inpatient or ambulatory encounter.", 130000, "EHR_ADT", [
    key("encounter_version_id", "Immutable encounter revision."), key("encounter_id", "Stable clinical visit identity."),
    key("episode_id", "Stable cross-encounter grouping; same patient, continuous care episode."),
    key("previous_encounter_version_id", "Linked predecessor; no cross-patient links.", "encounter.encounter_version_id", True),
    key("patient_version_id", "Patient demographics known at encounter creation.", "patient.patient_version_id"),
    key("facility_id", "Treating hospital.", "facility.facility_id"),
    key("location_id", "Initial treating unit.", "location.location_id"),
    key("coverage_version_id", "Coverage snapshot known at service time.", "patient_coverage.coverage_version_id"),
    key("attending_assignment_id", "Attending credential/assignment snapshot.", "worker_assignment.worker_assignment_id", True),
    text("encounter_class", "Care setting.", values="ED|IPD|OPD"),
    text("admission_source", "Route.", values="ED|ELECTIVE|DIRECT|TRANSFER|WALK_IN"),
    integer("initial_acuity", "Configured triage category 1-5, distinct from final severity."),
    ts("arrival_at", "Arrival/registration instant."), ts("admission_decision_at", "Decision to admit; boarding starts here.", True),
    ts("admitted_at", "Start of inpatient encounter; null for non-IPD.", True),
    ts("medically_ready_at", "Known discharge readiness; never retrospectively exposed.", True),
    ts("discharged_at", "Observed encounter end; null when still open.", True),
    text("disposition", "Observed end or current disposition.", values="OPEN|HOME|TRANSFER|DEATH|DIVERTED|LEFT_WITHOUT_SEEN|CANCELLED"),
    flag("planned", "Elective/planned encounter, distinct from readmission exclusion logic."),
    flag("carry_in", "Already active at reporting-window start."),
    integer("revision_no", "Knowledge revision number."), ts("known_from", "Source availability of this revision."),
    ts("known_to", "Exclusive supersession, null if current.", True)], [("encounter_id", "revision_no")],
    "56,000 encounters intersecting the window plus 2,000 completed pre-window opening-AR contexts; 68,000 lifecycle revisions and 4,000 corrections. First arrival, admission and discharge facts are separate knowledge revisions, never exposed early.")

table("clinical_condition", "condition_version_id", "One diagnosis/problem/allergy assertion version with optional encounter context.", 95000, "EHR_CLINICAL", [
    key("condition_version_id", "Assertion revision key."), key("condition_id", "Stable problem/allergy or encounter-diagnosis identity."),
    key("patient_version_id", "Patient assertion identity.", "patient.patient_version_id"),
    key("encounter_version_id", "Encounter diagnosis context; nullable for longitudinal problems/allergies.", "encounter.encounter_version_id", True),
    key("catalog_item_id", "DIAGNOSIS for diagnoses/problems; ALLERGEN for modeled drug-allergy substances.", "catalog_item.catalog_item_id"),
    text("condition_type", "Typed assertion.", values="DIAGNOSIS|PROBLEM|ALLERGY"),
    text("status", "Clinical status.", values="ACTIVE|RESOLVED|INACTIVE|REFUTED|UNKNOWN"),
    integer("diagnosis_rank", "Rank >=1 on encounter diagnoses; 0 on other assertion types."),
    text("present_on_admission", "POA status.", values="Y|N|UNKNOWN|NOT_APPLICABLE"),
    ts("onset_at", "Observed/reported onset; may precede reporting window.", True),
    ts("resolved_at", "Known resolution, not invented at cutoff.", True),
    text("reaction", "ALLERGY-only reaction description.", True),
    text("severity", "Clinical assertion severity.", values="MILD|MODERATE|SEVERE|UNKNOWN"), *history()], [("condition_id", "revision_no")])

table("clinical_event", "clinical_event_version_id", "One scalar clinical event/value or text document version; typed event family.", 580000, "EHR_CLINICAL", [
    key("clinical_event_version_id", "Immutable fact/document revision key."), key("clinical_event_id", "Stable order/result/administration/document identity."),
    key("encounter_version_id", "Encounter context known at documentation time.", "encounter.encounter_version_id"),
    key("catalog_item_id", "Typed code; null only for document prose with document_type.", "catalog_item.catalog_item_id", True),
    key("parent_event_version_id", "Order/result provenance; self FK with no cycles.", "clinical_event.clinical_event_version_id", True),
    key("author_assignment_id", "Authorized clinician's assignment snapshot.", "worker_assignment.worker_assignment_id"),
    text("event_type", "Typed event; no unvalidated opaque payload.", values="ORDER|OBSERVATION|LAB_RESULT|PROCEDURE|MED_ADMIN|MED_DISPENSE|DOCUMENT"),
    ts("occurred_at", "Order placement, measurement, performance, administration or authorship occurrence."),
    ts("period_end_at", "End of procedure/explicit measurement summary interval.", True),
    ts("order_start_at", "ORDER-only intended therapy/service start; must not precede placement unless explicit retrospective documentation.", True),
    ts("order_end_at", "ORDER-only intended therapy/service end; null means ongoing at cutoff.", True),
    num("dose_interval_hours", "Medication ORDER interval for scheduled doses; not a substitute for PRN maximum.", True, "hours"),
    c("as_needed", "BOOLEAN", "Medication ORDER PRN flag; null for nonmedication events.", True),
    c("max_doses_per_day", "INT", "Medication ORDER maximum administrations per local day; positive when applicable.", True),
    c("administration_sequence", "INT", "Positive sequence within stable medication order for an administration/dispense.", True),
    text("specimen_id", "LAB_RESULT synthetic specimen identity; shared by its scalar analytes.", True),
    ts("collected_at", "LAB_RESULT specimen collection; order precedes collection.", True),
    ts("result_ready_at", "LAB_RESULT result availability, not visible before collection/analysis completes.", True),
    ts("document_signed_at", "DOCUMENT signature availability; null if legitimately unsigned/open.", True),
    text("status", "Event lifecycle.", values="PLANNED|COMPLETED|CANCELLED|NOT_DONE|CORRECTED"),
    num("numeric_value", "Scalar observation/lab result; text_value used for qualitative results.", True, "value_unit"),
    text("value_unit", "Result UCUM unit.", True), text("text_value", "Qualitative result or fact-grounded note text.", True),
    num("reference_low", "Context-specific reference low, not universal clinical threshold.", True, "value_unit"),
    num("reference_high", "Context-specific reference high.", True, "value_unit"),
    num("dose_quantity", "Ordered/administered dose.", True, "dose_unit"), text("dose_unit", "Dose unit.", True),
    text("route", "Medication administration route.", True),
    num("consumed_base_quantity", "Actual modeled stock consumption after strength conversion.", True, "catalog base unit"),
    text("consumption_group_key", "Lot/unit/day consumption group reconciled to inventory issue quantities.", True),
    text("document_type", "DOCUMENT-only type.", True, "ED_NOTE|PROGRESS_NOTE|DISCHARGE_SUMMARY|OP_NOTE|OPERATIVE_NOTE"),
    text("aggregation", "POINT or explicitly labeled daily-summary observation; no fabricated monitor completeness.", values="POINT|DAILY_MIN|DAILY_MAX|DAILY_MEAN|NOT_APPLICABLE"),
    integer("revision_no", "Knowledge revision number."), ts("known_from", "Knowledge availability of this version."),
    ts("known_to", "Exclusive supersession time.", True)], [("clinical_event_id", "revision_no")],
    "560,000 distinct clinical events + 20,000 revisions. All modeled formulary administrations and selected diagnostic/clinical variables; not full telemetry or every EHR field.")

table("appointment", "appointment_id", "One immutable booked slot; reschedule creates linked replacement, not an overwritten slot.", 30000, "EHR_SCHEDULING", [
    key("appointment_id", "Booking identity."), key("patient_version_id", "Patient snapshot at booking.", "patient.patient_version_id"),
    key("location_id", "Booked unit.", "location.location_id"), key("worker_assignment_id", "Scheduled clinician.", "worker_assignment.worker_assignment_id", True),
    key("replacement_appointment_id", "Replacement slot after rescheduling.", "appointment.appointment_id", True),
    key("resulting_encounter_version_id", "Resulting encounter, if attended.", "encounter.encounter_version_id", True),
    text("appointment_type", "Booked service.", values="FOLLOW_UP|CONSULTATION|ELECTIVE_ADMISSION|PROCEDURE"),
    ts("booked_at", "Slot creation."), ts("scheduled_start", "Planned service start."), ts("scheduled_end", "Planned service end."),
    ts("arrived_at", "Check-in time, if attended.", True), ts("cancelled_at", "Known cancellation time.", True),
    ts("no_show_recorded_at", "No-show determination time, never known at booking.", True),
    text("cancel_reason", "Cancellation/reschedule reason.", True, "PATIENT|CAPACITY|PROVIDER|RESCHEDULE|OTHER")])

table("bed_event", "bed_event_id", "One immutable bed state change/correction or opening-state assertion.", 80000, "ADT_BED", [
    key("bed_event_id", "Stable event ID; deduplicate repeated deliveries."),
    key("bed_location_id", "Must reference location_type BED.", "location.location_id"),
    key("encounter_version_id", "Occupant context for OCCUPY/VACATE/open occupied states.", "encounter.encounter_version_id", True),
    key("corrects_bed_event_id", "Earlier assertion being corrected; correction semantics replay full affected bed history.", "bed_event.bed_event_id", True),
    text("transfer_group_id", "Atomic correlated transfer identifier.", True),
    integer("sequence_no", "Monotone per bed source sequence; ties use event ID after correction resolution."),
    ts("effective_at", "Business state-change instant."),
    text("event_type", "Transition category.", values="OPENING|OCCUPY|VACATE|CLEAN_START|READY|SERVICE_CHANGE|STAFF_CHANGE|RESERVE|RELEASE|CORRECTION"),
    text("occupancy_state", "Full post-transition occupancy assertion.", values="EMPTY|OCCUPIED|DIRTY|CLEANING"),
    text("service_state", "Physical service state.", values="IN_SERVICE|BLOCKED|OUT_OF_SERVICE"),
    flag("staffing_enabled", "Physical staffed-capacity flag; labor coverage is separately measured."),
    flag("reserved", "Empty bed reservation; does not imply a second occupant."),
    text("reason", "Recorded operational cause."), ts("delivery_at", "Simulated event arrival; source recording remains separate.")], [("bed_location_id", "sequence_no")])

table("staff_shift", "shift_version_id", "One knowledge version of a worker/unit shift or leave block.", 70000, "ROSTER_TIME", [
    key("shift_version_id", "Immutable revision."), key("shift_id", "Stable roster slot identity."),
    key("worker_assignment_id", "Worker role/rate validity snapshot.", "worker_assignment.worker_assignment_id"),
    key("location_id", "Worked/scheduled unit.", "location.location_id"),
    key("cost_center_id", "Actual worked responsibility center.", "cost_center.cost_center_id"),
    text("shift_type", "Work or unavailability block.", values="WORK|LEAVE|UNAVAILABLE"),
    ts("planned_start", "Published planned start."), ts("planned_end", "Published planned end."),
    ts("actual_start", "Observed attendance start.", True), ts("actual_end", "Observed attendance end.", True),
    num("worked_hours", "Elapsed attended hours; zero before actual completion.", unit="hours"),
    num("productive_hours", "Productive subset of worked hours.", unit="hours"),
    num("paid_nonproductive_hours", "Paid attended nonproductive subset.", unit="hours"),
    num("unpaid_break_hours", "Unpaid attended subset.", unit="hours"),
    num("overtime_hours", "Classified subset of paid hours, not extra elapsed hours.", unit="hours"),
    money("loaded_cost", "Loaded payable shift expense under effective rate/multiplier."), text("currency", "USD."),
    text("posting_group_key", "Deterministic workforce journal source-group key."),
    text("attendance_status", "Known attendance state.", values="PUBLISHED|WORKED|ABSENT|CANCELLED|ON_LEAVE"),
    integer("revision_no", "Roster/attendance revision number."), ts("known_from", "Publication of this revision."), ts("known_to", "Exclusive supersession.", True)], [("shift_id", "revision_no")],
    "56,000 distinct shift/leave blocks + 14,000 revisions. Rate and attendance corrections are versioned, not overwritten.")

table("inventory_movement", "movement_id", "One signed location/item/lot stock movement in base units.", 60000, "INVENTORY_PHARMACY", [
    key("movement_id", "Immutable movement identity."), key("location_id", "Stock location.", "location.location_id"),
    key("catalog_item_id", "MEDICATION or SUPPLY item.", "catalog_item.catalog_item_id"),
    text("lot_id", "Synthetic lot identifier."), text("movement_type", "Signed movement.", values="OPENING|RECEIPT|CONSUME|RETURN|TRANSFER_IN|TRANSFER_OUT|EXPIRE|ADJUSTMENT"),
    ts("occurred_at", "Movement effective time."), num("quantity_base", "Signed quantity: inflow positive, outflow negative.", unit="catalog base unit"),
    num("unit_cost", "Cost per base unit; decimal six-place precision.", unit="USD/base unit"), money("extended_cost", "Rounded signed quantity times unit cost."),
    date("expires_on", "Lot expiry date."), text("transfer_group_id", "Pair/group for cross-location stock movement.", True),
    text("consumption_group_key", "Daily item/lot/unit group matching modeled administrations and explicit waste.", True),
    num("nonpatient_waste_base", "Nonpatient waste component for consumption groups.", unit="catalog base unit"),
    key("reverses_movement_id", "Reversal reference with opposite signed effect.", "inventory_movement.movement_id", True),
    text("posting_group_key", "Deterministic inventory accounting source group."), text("currency", "USD.")])

table("service_charge", "charge_id", "One encounter/revenue-category/billing-period charge line with explicit units and interval; not an uncounted list of daily charges.", 120000, "BILLING", [
    key("charge_id", "Immutable charge identity."), key("encounter_version_id", "Charge encounter snapshot.", "encounter.encounter_version_id"),
    key("catalog_item_id", "Versioned billable service/procedure or medication/supply category.", "catalog_item.catalog_item_id"),
    key("clinical_event_version_id", "Specific billable event if one-to-one; room-day/category charges use their declared scope.", "clinical_event.clinical_event_version_id", True),
    key("cost_center_id", "Performing responsibility center.", "cost_center.cost_center_id"),
    date("service_from", "Inclusive local service-period start."), date("service_to", "Inclusive local service-period end; line cannot span accounting months."),
    text("revenue_category", "Typed price bucket.", values="ROOM|PROCEDURE|LAB|PHARMACY|ED|AMBULATORY|OTHER"),
    num("units", "Charge units, with returns represented by linked signed charges.", unit="unit_code"),
    text("unit_code", "Price basis."), money("unit_price", "Synthetic price per unit."), money("billed_amount", "Rounded units times price."),
    text("currency", "USD."), text("authorization_status", "Known pre-service authorization state.", values="NOT_REQUIRED|PENDING|APPROVED|DENIED|EXPIRED"),
    ts("authorization_known_at", "First knowledge of authorization state."),
    key("reverses_charge_id", "Credit/reversal reference.", "service_charge.charge_id", True),
    text("posting_group_key", "Charge/recognition source group; cash is never inferred from this field.")])

table("claim", "claim_id", "One original primary institutional claim; attempts are events, not new original claims.", 56000, "RCM", [
    key("claim_id", "Original claim identity."), key("encounter_version_id", "Claim encounter snapshot.", "encounter.encounter_version_id"),
    key("coverage_version_id", "Payer enrollment known/verified for service.", "patient_coverage.coverage_version_id"),
    text("claim_number", "Source original claim reference."), date("service_from", "First service date."), date("service_to", "Last observed service date."),
    ts("created_at", "Draft identity creation."), ts("first_submitted_at", "First submission; null if still draft.", True),
    money("original_billed_amount", "Original submitted claim-line total; changes are adjustment events."),
    money("opening_ar", "Opening carry-in receivable balance only; not billed or collected again."),
    money("opening_contractual_adjustments", "Historical signed contractual reductions included in opening AR; zero on new claims."),
    money("opening_cash_collected", "Historical net settlements before window; not current-period cash; zero on new claims."),
    money("opening_writeoffs", "Historical net write-offs before window; zero on new claims."),
    flag("carry_in", "Open receivable present at reporting-window start."), text("currency", "USD.")], [("claim_number",)],
    "54,000 current-period original claims plus 2,000 carry-in claims. In-progress claims and self-pay/no-submission episodes are explicit.")

table("claim_line", "claim_line_id", "One original claim charge line, preserving a one-charge-to-one-line baseline contract.", 112000, "RCM", [
    key("claim_line_id", "Claim-line identity."), key("claim_id", "Original claim.", "claim.claim_id"),
    key("charge_id", "Underlying billed charge; a charge cannot be in two live original claims.", "service_charge.charge_id"),
    integer("line_no", "Positive sequence in claim."), money("billed_amount", "Original line charge."),
    money("expected_allowed_amount", "Prospective contractual estimate, not final adjudication."),
    text("currency", "USD.")], [("claim_id", "line_no"), ("charge_id",)])

table("claim_event", "claim_event_id", "One signed immutable submission, adjudication, settlement or adjustment event.", 160000, "RCM_REMITTANCE", [
    key("claim_event_id", "Immutable event ID; repeated delivery has no new economic effect."),
    key("claim_id", "Original claim.", "claim.claim_id"), key("claim_line_id", "Optional line-level detail.", "claim_line.claim_line_id", True),
    key("denial_catalog_id", "DENIAL vocabulary row for a denial.", "catalog_item.catalog_item_id", True),
    key("reverses_claim_event_id", "Earlier event reversed by this event.", "claim_event.claim_event_id", True),
    text("event_type", "Financial/state event.", values="OPENING|SUBMITTED|ADJUDICATED|DENIED|APPEALED|RESUBMITTED|PAYMENT|PATIENT_PAYMENT|WRITEOFF|REFUND|REVERSAL"),
    integer("attempt_no", "Submission/appeal attempt >=1; OPENING uses 0."), ts("occurred_at", "Economic/source occurrence time."),
    money("contractual_adjustment_delta", "Positive reduction of gross AR; negative reversal."),
    money("payer_liability_delta", "Signed change to payer allocated responsibility."),
    money("patient_liability_delta", "Signed change to patient responsibility; reclassification does not itself create revenue."),
    money("cash_delta", "Receipt positive, refund/reversal negative."),
    money("writeoff_delta", "Positive final reduction of AR, negative reversal."),
    money("recognized_revenue_delta", "Signed recognition or estimate correction, separate from cash."),
    money("ar_delta", "Signed billed-claim AR movement. First submission assigns previously recognized unbilled service AR; it is not new revenue."),
    text("posting_group_key", "Remittance/AR/cash journal group."), text("currency", "USD.")])

table("financial_posting", "posting_id", "One debit/credit journal line; daily operational source groups or explicit monthly cost-pool close.", 180000, "SYNTHETIC_GL", [
    key("posting_id", "Immutable posting line."), key("journal_id", "Balanced journal grouping."), integer("line_no", "Positive line sequence."),
    key("facility_id", "Accounting entity.", "facility.facility_id"), key("cost_center_id", "Responsibility center.", "cost_center.cost_center_id"),
    key("account_catalog_id", "ACCOUNT vocabulary row.", "catalog_item.catalog_item_id"),
    date("posting_date", "Accounting date."), date("service_from", "Start of represented source service interval."), date("service_to", "End of represented source service interval."),
    money("debit_amount", "Nonnegative debit; exactly one side is positive."), money("credit_amount", "Nonnegative credit; reversal swaps sides."),
    text("currency", "USD."), text("source_domain", "Economic origin.", values="OPENING|WORKFORCE|INVENTORY|REVENUE|AR|CASH|OVERHEAD|ACCRUAL|RECLASSIFICATION|COST_POOL_CLOSE"),
    text("source_group_key", "Deterministic daily operational or monthly pool-close key; aggregation never loses the reconciliation predicate."),
    text("allocation_pool_key", "Month/center/category expense pool identity; null for nonexpense postings.", True),
    flag("eligible_for_allocation", "True only on monthly expense-pool debit/reversal; daily source expenses are reclassified, not allocated a second time."),
    key("reverses_posting_id", "Opposite-side reversal link.", "financial_posting.posting_id", True),
    ts("known_from", "When posting is known/available; later adjustments are new postings.")], [("journal_id", "line_no")],
    "Daily source groups plus monthly debit-pool/credit-original-expense reclassifications preserve net expense. Allocation targets monthly pool expense lines, keeping patient-month detail within budget. All journal/reclass lines count in 180,000 rows.")

table("cost_allocation", "allocation_id", "One eligible monthly expense-pool-posting allocation to an encounter or explicit nonpatient/residual destination.", 180000, "COST_ACCOUNTING", [
    key("allocation_id", "Allocation line identity."), key("posting_id", "Eligible expense debit or signed reversal pool line.", "financial_posting.posting_id"),
    key("encounter_version_id", "Patient allocation destination; null on NONPATIENT/RESIDUAL.", "encounter.encounter_version_id", True),
    key("cost_center_id", "Destination responsibility center.", "cost_center.cost_center_id"),
    text("allocation_run_id", "Selected allocation version; never sum multiple runs."),
    text("destination_type", "Typed destination.", values="PATIENT|NONPATIENT|RESIDUAL"),
    text("cost_category", "Expense attribution.", values="LABOR|DRUG|SUPPLY|OVERHEAD|OTHER"),
    date("accounting_month", "First day of posting month."),
    num("driver_quantity", "Selected allocation driver amount.", unit="driver_unit"), text("driver_unit", "Patient-hours, service units or approved cost driver."),
    num("allocation_share", "Share of source signed expense, summing to one within selected run.", unit="fraction"),
    money("allocated_amount", "Rounded signed expense times share with deterministic residual apportionment."),
    text("currency", "USD."), ts("known_from", "First availability of this allocation run."),
    text("supersedes_run_id", "Earlier run identity, if rerun.", True)], [("posting_id", "allocation_run_id", "allocation_id")])

table("finance_monthly", "finance_record_id", "One month/cost-center/account-or-statistical-measure/scenario/vintage/currency-or-unit value.", 36000, "AXIOM", [
    key("finance_record_id", "Immutable normalized export value."), key("facility_id", "Financial entity.", "facility.facility_id"),
    key("cost_center_id", "Responsibility center.", "cost_center.cost_center_id"),
    key("account_catalog_id", "ACCOUNT code for monetary values; null on statistical measures.", "catalog_item.catalog_item_id", True),
    text("measure_code", "Measure.", values="ACCOUNT_AMOUNT|PATIENT_DAYS|ADMISSIONS|PRODUCTIVE_HOURS|FTE"),
    date("accounting_month", "First calendar day of the target accounting month."),
    text("scenario", "Values must not be summed across scenarios.", values="ACTUAL|BUDGET|FORECAST"),
    text("vintage_id", "Immutable scenario/version identity; forecast knowledge preserved."),
    ts("published_at", "First availability of this vintage."), money("amount", "Monetary value, null for statistical quantities.", True),
    num("quantity", "Statistical value, null for money.", True, "unit_code"), text("unit_code", "USD, patient_days, admissions, hours or FTE."),
    text("report_template_id", "Bounded source report family, not a new business table."),
    text("source_file_id", "Synthetic monthly export manifest identity."),
    text("supersedes_vintage_id", "Earlier export/version, if corrected.", True)],
    [("cost_center_id", "account_catalog_id", "measure_code", "accounting_month", "scenario", "vintage_id", "unit_code")],
    "36,000 explicit selected account/statistical series including revisions; no implied dense 45 centers x every code x every monthly forecast. Required series/vintages listed in baseline.")

table("facility_day_driver", "facility_day_id", "One facility/local-day external/calendar observation; no future realized data is known early.", 3288, "EXTERNAL_DRIVER", [
    key("facility_day_id", "Stable facility/day key."), key("facility_id", "Facility.", "facility.facility_id"),
    date("calendar_date", "Local day."), integer("day_of_week", "ISO weekday 1-7."), flag("holiday", "Published calendar holiday known in advance."),
    text("season", "Configured season."), num("respiratory_index", "Synthetic observed community demand index, not real surveillance.", unit="index"),
    num("weather_index", "Synthetic observed weather disruption index.", unit="index"),
    ts("calendar_known_at", "Publication time of advance-known calendar features."),
    ts("observations_known_at", "First availability of realized daily indices."),
    text("calendar_source", "Public calendar reference or explicit synthetic assumption.")], [("facility_id", "calendar_date")])

CLINICAL_TYPES = {"ORDER": 50000, "OBSERVATION": 70000, "LAB_RESULT": 70000,
                  "PROCEDURE": 20000, "MED_ADMIN": 260000, "MED_DISPENSE": 20000,
                  "DOCUMENT": 70000, "REVISION_ROWS": 20000}

RULE_DEFINITIONS = [
    ("ID01", "P0", "ALL", "PK uniqueness and required scalar fields", "PK not null and count(*)=count(distinct PK); required columns correctly typed", "0 failures", "Data", "Phase 2"),
    ("ID02", "P0", "ALL", "Explicit and typed references", "All nonnull physical FKs resolve; polymorphic/stable-ID references satisfy entity-specific lookup", "0 orphans or ambiguities", "Data", "Phase 2"),
    ("TM01", "P0", "patient,worker_assignment,access_scope,patient_coverage,clinical_condition,source_key_map", "Bitemporal intervals", "valid_from<valid_to and known_from<known_to when ends exist; no exclusive business/knowledge overlap", "0 invalid rectangles", "Data", "Phase 2"),
    ("TM02", "P0", "ALL", "Source knowledge versus export", "recorded_at<=export_available_at; as-of projection requires applicable known_from and export availability", "0 future facts", "Data", "Phase 7"),
    ("TM03", "P0", "encounter,clinical_event,staff_shift", "Lifecycle knowledge", "Initial and subsequent lifecycle values use separate versions; no final outcome in earlier known interval", "0 leakage fixtures fail", "Data", "Phase 3"),
    ("NM01", "P1", "patient,worker_assignment,facility,location", "Believable identities", "Required human names present; no numbered generic person names; distinct persons may share names", "0 unexplained placeholders; realism sample passes", "Business", "Phase 2"),
    ("NM02", "P1", "patient,worker_assignment", "Age and contacts", "Age uses local calendar birthdays; service age>=18; identity contacts use documented test namespaces", "0 impossible ages or real copied contacts", "Business", "Phase 2"),
    ("OR01", "P0", "facility,location,cost_center", "Hierarchy and bed inventory", "Parent chains acyclic/same facility; 72 BED rows, 12 ICU and 60 medicine/surgery; opening state covers each bed", "Exact baseline or approved scope change", "Operations", "Phase 2"),
    ("WK01", "P1", "worker_assignment,staff_shift", "Assignment and credential validity", "Worked shift resolves eligible worker, role, credential and effective cost/rate as of service and knowledge", "0 unauthorized worked assignments", "Workforce", "Phase 5"),
    ("WK02", "P0", "worker_assignment", "Manager identity", "manager_worker_id resolves a distinct stable worker as of both valid and knowledge time; no cycles", "0 invalid manager chains", "Workforce", "Phase 2"),
    ("AC01", "P0", "access_scope", "Scope and revocation", "Scope key resolves its scope_type; NETWORK uses ALL_NETWORK; revoked rows deny later test reads", "0 invalid targets or post-revocation grants", "Security", "Phase 7"),
    ("CV01", "P0", "patient_coverage,encounter,claim", "Primary coverage", "One primary enrollment per stable patient/time; encounter/claim patient matches coverage; SELF_PAY explicit", "0 cross-person or overlapping primary coverage", "Revenue", "Phase 2"),
    ("CD01", "P1", "catalog_item,clinical_condition,clinical_event", "Vocabulary and unit validity", "Correct domain, release, effective date and UCUM/base unit; discharge-based diagnosis/procedure selection follows code-system rule", "0 hard code/unit violations", "Clinical", "Phase 3"),
    ("CD02", "P0", "catalog_item,financial_posting", "Catalog type discriminators", "MEDICATION requires strength/base-unit conversion; ACCOUNT requires account_class and normal_balance; no opaque extra facts", "0 untyped or invalid catalog rows", "Data", "Phase 2"),
    ("EN01", "P0", "encounter,appointment", "Encounter episode identity", "Linked encounters share stable patient; episodes acyclic; ED/IPD separate visits, internal bed transfers not new encounters", "0 identity/episode violations", "Operations", "Phase 3"),
    ("EN02", "P0", "encounter", "Observed chronology", "arrival<=decision<=IPD start<=observed discharge where applicable; open values remain null; prewindow completed rows are opening-AR context", "0 impossible lifecycle orders", "Clinical", "Phase 3"),
    ("EN03", "P0", "encounter,patient", "Death and cutoff", "No new care after known death; post-death billing permitted; unobserved future outcomes remain censored", "0 invented care/outcomes", "Clinical", "Phase 3"),
    ("CN01", "P1", "clinical_condition", "Condition family constraints", "DIAGNOSIS requires encounter and rank>=1; PROBLEM/ALLERGY rank=0; ALLERGY requires drug substance and reaction", "0 family-specific failures", "Clinical", "Phase 3"),
    ("CN02", "P0", "clinical_condition,encounter", "Diagnosis coverage", "Each completed clinically assessed encounter has a primary diagnosis or explicit reviewed diagnostic uncertainty; no diagnosis required for left-without-seen", "100% applicable encounters covered", "Clinical", "Phase 3"),
    ("CE01", "P0", "clinical_event", "Clinical event discriminator", "Event-specific required fields match type matrix; no fabricated fields; every scalar result counts a row", "0 matrix failures", "Clinical", "Phase 3"),
    ("CE02", "P0", "clinical_event,clinical_condition", "Orders, administration and allergy", "Results/admin link valid earlier orders; active drug-allergy conflict rejected; dose/route within reviewed pathway configuration", "0 hard clinical contradictions", "Clinical", "Phase 3"),
    ("CE03", "P1", "clinical_event", "Fact-grounded notes", "DOCUMENT text contains only structured facts known at authored time; negation and uncertain diagnoses preserved", "0 material sampled contradictions; repetition target passes", "Clinical", "Phase 3"),
    ("AP01", "P1", "appointment", "Booked-slot history", "booked<scheduled_end; no-show unavailable before scheduled end; cancelled/rescheduled slot retained and replacement linked", "0 invalid transitions", "Operations", "Phase 3"),
    ("BD01", "P0", "bed_event,encounter,location", "Exclusive compatible occupancy", "One active occupant per bed and one inpatient bed per stable patient; capability/cleanliness/service rules respected", "0 unexplained conflicts", "Operations", "Phase 4"),
    ("BD02", "P0", "bed_event", "State machine", "Resolve corrections before applying full post-state in effective sequence; no occupied closure without relocation; null occupant only when empty/nonoccupancy", "0 illegal state transitions", "Operations", "Phase 4"),
    ("BD03", "P0", "bed_event,encounter", "Census roll-forward", "opening+admissions+external transfers in-discharges-external transfers out=closing at same scope/time", "Exact equality", "Operations", "Phase 4"),
    ("BD04", "P0", "bed_event", "Occupied seconds", "Event-state integral equals independently reconstructed bed intervals clipped to window", "0 seconds unexplained difference", "Operations", "Phase 4"),
    ("BD05", "P1", "bed_event,encounter", "Unmet capacity", "Waiting/diversion/deferred appointments explicitly explain exhausted compatible capacity; no dropped arrivals", "100% arrivals have current or terminal disposition", "Operations", "Phase 4"),
    ("SF01", "P0", "staff_shift", "Hours equation", "worked_hours=productive+paid_nonproductive+unpaid_break; overtime<=paid hours; no overlapping WORK intervals", "0 unexplained differences", "Workforce", "Phase 5"),
    ("SF02", "P1", "staff_shift,bed_event,worker_assignment", "Demand-linked staffing", "RN productive requirement uses acuity-adjusted patient-days; coverage shortages are explicit, not hidden by census deletion", "Registered cohort/shift targets pass", "Workforce", "Phase 5"),
    ("IV01", "P0", "inventory_movement", "Stock roll-forward", "opening+signed movements=closing by location/item/lot/base unit; paired transfers balance", "0 quantity difference or unexplained negative stock", "Supply", "Phase 5"),
    ("IV02", "P0", "inventory_movement,clinical_event,catalog_item", "Administration consumption", "CONSUME group negative stock quantity equals administered converted base units plus explicit nonpatient waste; receipts not consumed twice", "Exact base-unit equality at six-place precision", "Supply", "Phase 5"),
    ("IV03", "P1", "inventory_movement", "Lot expiry and valuation", "No issue before stock arrival/after expiry; extended_cost=HALF_UP(quantity_base*unit_cost,2); reversal opposite", "0 unexplained violations", "Supply", "Phase 5"),
    ("CH01", "P0", "service_charge,clinical_event,encounter", "Charge provenance", "Charge links performed billable service or declared room-day/category predicate; billed=HALF_UP(units*unit_price,2); no charge for cancelled/not-done service", "0 untraceable or invalid amounts", "Finance", "Phase 6"),
    ("CL01", "P0", "claim,claim_line,service_charge", "Original claim totals", "Original billed header equals original line sum; lines match charge and patient; each charge in at most one live original claim", "0 cents difference", "Revenue", "Phase 6"),
    ("CL02", "P0", "claim_event,claim", "Claim lifecycle", "Attempt/state valid; resubmissions retain original claim; OPENING is not new-period submission", "0 invalid attempts or denominator duplication", "Revenue", "Phase 6"),
    ("CL03", "P0", "claim_event", "AR/cash movements", "Opening AR plus signed event ar_delta equals closing; liability reclassification alone creates no cash/revenue; cash/refund reversals linked", "0 cents unexplained", "Finance", "Phase 6"),
    ("CL04", "P1", "claim_event,service_charge", "Denial evidence availability", "Denial causes relate to real authorization/coding/timing facts available at decision; open appeal is not final loss", "All sampled reasons supported", "Revenue", "Phase 6"),
    ("GL01", "P0", "financial_posting,catalog_item", "Double entry", "Exactly one positive debit/credit per line; journal debit=credit per entity/currency/date; account domains valid", "0 cents imbalance", "Finance", "Phase 6"),
    ("GL02", "P0", "financial_posting,staff_shift,inventory_movement,service_charge,claim_event", "Source group reconciliation", "Each source-group journal amount reconciles to latest eligible underlying facts under registered recognition policy", "0 unexplained cents; lineage predicate mandatory", "Finance", "Phase 6"),
    ("GL03", "P0", "financial_posting,inventory_movement", "Stock purchase versus expense", "Receipts post asset/AP; consumption posts expense/asset; no simultaneous purchase and consumption double-expense", "0 double-counted expense", "Finance", "Phase 6"),
    ("CO01", "P0", "cost_allocation,financial_posting", "Cost pool conservation", "Selected run allocations PATIENT+NONPATIENT+RESIDUAL equal eligible signed expense source; shares sum 1; no allocation counted as new GL expense", "0 cents difference", "Finance", "Phase 6"),
    ("CO02", "P0", "cost_allocation", "Destination and run selection", "PATIENT requires encounter; other destinations require null encounter; select one current known run, not all versions", "0 invalid destinations or duplicated runs", "Finance", "Phase 6"),
    ("AX01", "P0", "finance_monthly,financial_posting", "Axiom actual reconciliation", "Latest known ACTUAL equals P&L monthly movement or balance-sheet cumulative closing balance per account class, center, month, USD and explicit reclass/timing entries", "0 cents difference at every declared grain", "Finance", "Phase 6"),
    ("AX02", "P0", "finance_monthly", "Scenario/vintage/unit grain", "Monetary rows have account+amount+USD, stats have quantity+unit; no summing scenarios or revisions; first-day month required", "0 invalid unit/grain combinations", "Finance", "Phase 6"),
    ("AX03", "P0", "finance_monthly,facility_day_driver", "No hindsight forecasts", "Budget/forecast uses only inputs available before vintage published_at; realized future indices never used early", "0 leakage fixture failures", "Finance", "Phase 8"),
    ("SR01", "P0", "ALL", "Source round trip", "Parsed export rows and control totals equal declared canonical scope; snapshots replace, deltas add once, versions retained", "0 unexplained differences", "Data", "Phase 7"),
    ("SR02", "P0", "source_key_map", "Crosswalk resolution", "Typed target exists; source namespace/key/time resolves exactly one mapping; UNMAPPED rows are challenge inputs, not accepted canonical facts", "0 unapproved unmapped facts", "Data", "Phase 7"),
    ("SR03", "P0", "bed_event,claim_event,inventory_movement,financial_posting", "Idempotent replay", "Repeated delivery has no new economic or occupancy effect; corrections converge to independent expected state", "0 state or amount difference", "Data", "Phase 7"),
    ("DR01", "P1", "facility_day_driver", "Daily driver coverage", "3 facilities x1096 dates exactly once; calendar-known time separate from realized-observation-known time", "3288 rows and no missing/duplicate day", "Data", "Phase 2"),
    ("RS01", "P1", "ALL", "Marginal and conditional realism", "Apply preregistered target bands by denominator/date/cohort; low-count cells use documented intervals or manual review", "All realism targets pass before release", "Business", "Phase 8"),
    ("RS02", "P1", "clinical_event,encounter,staff_shift,claim_event", "Connected scenario behavior", "Scenario-specific expected effects appear in linked domains, no hidden scenario labels in business features", "Every required scenario meets coverage and expected causal direction", "Business", "Phase 8"),
    ("CP01", "P0", "ALL", "Business volume/table boundary", "20<=physical business tables<=25; all versions/openings/corrections counted; canonical total<=2,000,000", "No over-cap release; never truncate linked data", "Data", "Phase 8"),
    ("RP01", "P0", "ALL", "Clean rebuild", "Pinned code/config/reference/seed reproduces normalized sorted business hashes, excluding volatile execution metadata", "Exact hash equality", "Data", "Phase 9"),
    ("FN01", "P0", "encounter,clinical_condition,clinical_event,claim_line,cost_allocation", "Independent fact grains", "Aggregate each fact to declared target before joining; pairwise joins cannot multiply census/charges/cost", "All hand-calculated fan-out fixtures pass", "Data", "Phase 8"),
]

RULES = []
for rid, severity, names, title, expression, expected, owner, phase in RULE_DEFINITIONS:
    RULES.append({"id": rid, "severity": severity,
                  "tables": [t["name"] for t in TABLES] if names == "ALL" else names.split(","),
                  "title": title, "formula_or_invariant": expression, "expected": expected,
                  "scope": "Latest applicable knowledge/business version at declared scope/time; raw challenge faults evaluated against expected disposition.",
                  "owner": owner, "execution_phase": phase,
                  "evidence": "Rule results, scoped counts/totals, failing keys, fixture expectation and independent reviewer disposition.",
                  "failure_action": "Block dependent gate; correct upstream cause; regenerate affected descendants.",
                  "implementation_status": "SPECIFIED_NOT_DATA_EXECUTED"})

BASELINE = {
    "version": VERSION, "status": "DESIGN_BASELINE", "prepared_date": "2026-10-23",
    "business_start_date": "2023-01-01", "business_end_date_inclusive": "2025-12-31",
    "final_export_grace_end_utc": "2026-01-10T23:59:59Z",
    "export_grace_policy": "Only source delivery/December-close knowledge may occur after the business cutoff. No post-cutoff clinical care, claim payment or outcome is invented. December 2025 actuals may be published January 5, 2026 and remain unavailable to December as-of queries.",
    "local_timezone": "America/Chicago", "currency": "USD", "fiscal_year_start_month": 1,
    "minimum_tables": 20, "maximum_tables": 25, "minimum_planned_records": 1000000,
    "maximum_records": 2000000, "record_cap_scope": "canonical published business rows, including versions, openings, corrections and any published challenge rows",
    "physical_export_count_policy": "Report every serialized snapshot/mirror row separately; no claim of <=2m across copies.",
    "network": {"facilities": 3, "beds_per_facility": 24, "total_beds": 72,
                "icu_beds_per_facility": 4, "medical_surgical_beds_per_facility": 20,
                "adult_min_age_at_service": 18, "planned_ipd_episodes": 12000,
                "carry_in_ipd_included": 57, "ipd_mean_in_window_bed_days": 5.2,
                "planned_bed_days": 62400, "planned_staffed_bed_days": 77950,
                "opening_occupied_beds": 57, "staffed_capacity_policy": "Close empty beds only; occupied patients retain physical bed status; coverage shortfall is separate.",
                "distinct_encounters": {"IPD": 12000, "ED": 27000, "OPD": 17000},
                "opening_closed_encounters": 2000, "encounter_lifecycle_revision_rows": 68000,
                "encounter_correction_rows": 4000, "distinct_patients": 20000,
                "patient_revision_rows": 2000, "distinct_workers": 300, "worker_revision_rows": 600},
    "scope": {"included": ["adult community inpatient medicine", "limited elective general/orthopedic surgery", "adult ED", "hospital ambulatory follow-up", "short-stay ICU stabilization", "primary payer institutional claims", "modeled formulary administrations", "selected clinical measurements and diagnostic results", "daily source-group double-entry ledger"],
              "excluded": ["pediatrics", "maternity and newborns", "long-term intensive care", "transplants and complex tertiary surgery", "complete device telemetry", "full PACS imagery", "every EHR observation", "secondary payer coordination", "professional claims", "live Workday/Axiom tenant certification", "deployed analytics or forecasting"]},
    "clinical_event_budget": CLINICAL_TYPES,
    "bed_event_budget": {"opening": 72, "occupy_vacate_clean_ready": 60000,
                         "service_staff_reservation": 18528, "corrections": 1400},
    "bed_interval_design": {"distinct_ipd": 12000, "extra_transfers": 3000,
                            "total_intervals": 15000, "average_turnaround_hours": 1.25},
    "staffing": {"distinct_work_shifts": 52000, "leave_unavailable_blocks": 4000,
                 "revision_rows": 14000, "shift_hours": 12, "productive_hours_per_work_shift": 10.5,
                 "rn_share_of_work_shifts": 0.70, "modeled_rn_hours_per_patient_day": 5.5,
                 "rostered_workers": 180, "mean_rostered_worker_fte": 0.65,
                 "annual_paid_hours_per_fte": 2080},
    "claim_budget": {"current_period_originals": 54000, "opening_originals": 2000,
                     "events": {"OPENING": 2000, "SUBMITTED": 54000, "ADJUDICATED": 48000,
                                "PAYMENT": 44000, "EXCEPTIONS_APPEALS_ADJUSTMENTS": 12000}},
    "financial_grain": "Daily source-group journal lines plus explicit monthly pool-close reclassifications; exact source predicates; journals balanced per entity/currency.",
    "accounting_policy": {"recognition": "Gross service receivable/revenue at completed eligible service with explicit contractual estimate. Before submission the AR is unbilled, derived from eligible unclaimed charges. SUBMITTED assigns net service AR to the billed claim subledger without new revenue or net GL AR. Later adjudication changes estimates, never books gross revenue twice.",
                          "cash": "Receipt debits cash and credits AR; refunds/reversals use linked opposite entries.",
                          "inventory": "Receipts debit inventory/credit AP; actual consumption credits inventory/debits expense; no double expense of purchase plus consumption.",
                          "labor": "Actual loaded payable shift cost debits labor expense/credits payroll payable; daily aggregation retains source predicate.",
                          "allocations": "Monthly pool-close debits pool expense and credits original expense, preserving net total. Only eligible pool debit/reversal lines are allocated to encounter-month/category or nonpatient/residual. Daily source expense is never allocated twice; allocation rows create no new GL expense.",
                          "rounding": "Decimal HALF_UP to cents at charge/posting line; largest remainder deterministic allocation, tie-break by destination ID."},
    "finance_series": {"actual": "11 required P&L control accounts at 45 centers and 6 required balance accounts at 3 facility control centers; control zeros explicitly required. P&L is monthly movement; balance sheet is cumulative closing balance including opening journals.",
                       "budget": "6 selected P&L accounts at 45 centers; original budget before each year, Jul-Dec midyear revisions in 2024/2025. No zero-filling absent comparison series.",
                       "forecast": "Quarterly published forward 3-month expense/revenue forecasts; not every account/center/month; target horizon clipped to observed reporting window.",
                       "statistics": ["ADMISSIONS", "PATIENT_DAYS", "PRODUCTIVE_HOURS", "FTE"],
                       "financial_row_budget": 36000,
                       "axiom_inventory_assumption": "900 report definitions grouped into 12 representative layout families; exercise all 12. Not 900 nonempty files every month. Actual tenant inventory is outside the simulated contract."},
    "budget_policy": "Planned rows are inclusive design envelopes, not quotas. Never pad, truncate descendants, or discard over-cap episodes. Regenerate/recalibrate complete causal histories if global cap would be exceeded.",
    "solution_status": "BLOCKED_FOR_SOLUTION", "next_phase": "Phase 1 only after Phase 0 gate",
    "review_authority": {"business_owner": "Kkb113", "design_reviewer": "Codex",
                         "delegation": "User explicitly authorized Codex to review and finalize Phase 0 in this chat.",
                         "review_scope": "Design coherence, clinical pathway assumptions, simplified finance policy, contracts and arithmetic; not independent licensed clinical validation or vendor certification."},
    "financial_posting_budget": {"opening": 500, "workforce": 60000, "inventory": 50000,
                                  "revenue_ar_cash": 50000, "monthly_pool_close": 12960,
                                  "overhead_accrual_other_reclassification": 6540},
    "finance_row_breakdown": {"actual_pnl_45_centers_11_accounts_36_months": 17820,
                               "actual_balance_3_control_centers_6_accounts_36_months": 648,
                               "actual_stats_15_centers_4_measures_36_months": 2160,
                               "original_budget_45_centers_6_accounts_36_months": 9720,
                               "midyear_budget_45_centers_6_accounts_12_months": 3240,
                               "forecast_12_selected_centers_2_accounts_12_vintages_3_months": 864,
                               "budget_stats_3_centers_4_measures_36_months": 432,
                               "correction_vintage_allowance": 1116},
    "account_sets": {"pnl": ["GROSS_REVENUE", "CONTRA_REVENUE", "LABOR_DIRECT", "DRUG_DIRECT", "SUPPLY_DIRECT", "OVERHEAD_DIRECT", "LABOR_POOL", "DRUG_POOL", "SUPPLY_POOL", "OVERHEAD_POOL", "OTHER_EXPENSE"],
                     "balance": ["CASH", "AR", "INVENTORY", "AP", "PAYROLL_PAYABLE", "OPENING_EQUITY"],
                     "budget": ["GROSS_REVENUE", "CONTRA_REVENUE", "LABOR_POOL", "DRUG_POOL", "SUPPLY_POOL", "OVERHEAD_POOL"]},
    "ipd_pathway_mix": [{"family": "HEART_FAILURE", "share": 0.20, "target_mean_days": 5.6},
                         {"family": "COPD", "share": 0.15, "target_mean_days": 5.2},
                         {"family": "PNEUMONIA", "share": 0.15, "target_mean_days": 6.6},
                         {"family": "GENERAL_MEDICINE", "share": 0.10, "target_mean_days": 4.8},
                         {"family": "GENERAL_SURGERY", "share": 0.30, "target_mean_days": 4.8},
                         {"family": "ORTHOPEDIC", "share": 0.10, "target_mean_days": 4.0}],
    "admission_routes": {"elective_new": 4800, "ed_new": 6000, "direct_external_new": 1143, "occupied_carry_in": 57},
    "cost_allocation_components": {"ipd_four_categories": 48000, "cross_month_ipd": 8640,
                                    "transfer_centers": 12000, "ed_op_average_2_25_categories": 99000,
                                    "nonpatient_residual": 6000, "allocation_revisions": 5000},
    "tables": {t["name"]: t["planned_rows"] for t in TABLES}
}

CLINICAL_MATRIX = {
    "ORDER": {"required": ["catalog_item_id"], "domains": ["MEDICATION", "PROCEDURE", "LAB", "OBSERVATION"], "parent": "none required; order precedes descendants"},
    "OBSERVATION": {"required": ["catalog_item_id", "value_unit"], "domains": ["OBSERVATION"], "parent": "optional earlier order; numeric or qualitative value required, not both empty"},
    "LAB_RESULT": {"required": ["catalog_item_id", "parent_event_version_id", "value_unit", "specimen_id", "collected_at", "result_ready_at"], "domains": ["LAB"], "parent": "earlier compatible ORDER; collection<=result_ready<=knowledge; each analyte is one scalar row"},
    "PROCEDURE": {"required": ["catalog_item_id", "parent_event_version_id"], "domains": ["PROCEDURE"], "parent": "earlier compatible ORDER; not-done/cancelled not billed"},
    "MED_ADMIN": {"required": ["catalog_item_id", "parent_event_version_id", "dose_quantity", "dose_unit", "route", "consumed_base_quantity", "consumption_group_key", "administration_sequence"], "domains": ["MEDICATION"], "parent": "earlier active medication ORDER; completed administration consumes positive converted stock; schedule/PRN maximum checked by stable order and local day"},
    "MED_DISPENSE": {"required": ["catalog_item_id", "parent_event_version_id", "dose_quantity", "dose_unit", "consumed_base_quantity", "consumption_group_key"], "domains": ["MEDICATION"], "parent": "earlier medication ORDER; prescribed quantity is not assumed administered"},
    "DOCUMENT": {"required": ["document_type", "text_value"], "domains": [], "parent": "optional provenance; catalog_item_id null; only facts known at occurred_at"}
}

CLINICAL_MATRIX["ORDER"]["conditional_requirements"] = "For MEDICATION orders require dose_quantity, dose_unit, route, order_start_at, as_needed and max_doses_per_day; scheduled orders also require positive dose_interval_hours. Other order families do not carry fake medication fields."
for medication_type in ("MED_ADMIN", "MED_DISPENSE"):
    CLINICAL_MATRIX[medication_type]["required"] = [x for x in CLINICAL_MATRIX[medication_type]["required"] if x not in ("consumed_base_quantity", "consumption_group_key")]
    CLINICAL_MATRIX[medication_type]["conditional_requirements"] = "COMPLETED requires positive consumed_base_quantity and resolvable consumption_group_key; CANCELLED/NOT_DONE consumes zero and has null consumption group. Inpatient ward dispensing is a transfer, not a second consumed dose. MED_DISPENSE represents take-home supply only in v1."

REALISM = [
    {"id": "AGE", "metric": "Patient age at first in-window service, distinct patients", "denominator": "patients with qualifying service; adult at each service", "target": {"18-34": 0.16, "35-49": 0.20, "50-64": 0.26, "65-79": 0.25, "80-100": 0.13}, "tolerance": "Each share within 0.04 absolute; cells n<200 use 95% Wilson interval review", "provenance": "Configured fictional hospital catchment, not a US prevalence estimate", "owner": "Business"},
    {"id": "OCC", "metric": "Occupied bed-days / staffed bed-days", "denominator": "77950 staffed days, time-weighted", "lower": 0.74, "upper": 0.86, "provenance": "Capacity/demand design calibration", "owner": "Operations"},
    {"id": "LOS", "metric": "Completed uncensored IPD mean LOS in days", "denominator": "Completed IPD excluding opening-only AR contexts", "lower": 4.4, "upper": 6.2, "provenance": "Configured adult pathway mix; 5.2 clipped occupied days per intersecting episode is a separate budget identity", "owner": "Clinical"},
    {"id": "TAIL", "metric": "Share of completed IPD stays over 10 days", "denominator": "Completed IPD, adequate followup", "lower": 0.025, "upper": 0.09, "provenance": "Configured long-stay component; not a measured benchmark", "owner": "Clinical"},
    {"id": "REPEAT", "metric": "Share of patients with >=2 distinct intersecting encounters", "denominator": "Distinct active patients, not demographic versions", "lower": 0.40, "upper": 0.75, "provenance": "Longitudinal cohort design", "owner": "Business"},
    {"id": "PAYER", "metric": "Coverage at service, by distinct encounter", "denominator": "Intersecting encounters, single primary plan", "target": {"COMMERCIAL": 0.40, "MEDICARE": 0.35, "MEDICAID": 0.15, "SELF_PAY": 0.10}, "tolerance": "Each share within 0.05 absolute; cohort/age compatibility checked independently", "provenance": "Fictional configured payer mix", "owner": "Finance"},
    {"id": "DENIAL", "metric": "Original claims with initial full/partial denial", "denominator": "Current-period originals with observed first adjudication, not attempts or unresolved claims", "lower": 0.08, "upper": 0.12, "provenance": "Configured demonstration mix", "owner": "Finance"},
    {"id": "READMIT", "metric": "Unplanned network readmission within 30 days", "denominator": "Eligible live discharges with full 30-day followup; continuous transfers excluded", "lower": 0.08, "upper": 0.16, "provenance": "Configured care-pathway mix", "owner": "Clinical"},
    {"id": "NOTES", "metric": "Exact duplicate normalized note bodies after removing identity/date fields", "denominator": "At least 100 notes per evaluated document_type", "lower": 0.0, "upper": 0.15, "provenance": "Text-diversity design threshold; factual consistency remains a hard rule", "owner": "Clinical"},
    {"id": "NAMES", "metric": "Weighted name frequencies and collisions", "denominator": "Stable persons, cohort-conditioned sources", "tolerance": "Top-100+OTHER total variation <=0.10 against configured source weights; >=300 distinct given names and >=1000 surnames among 20000 patients; no uniqueness requirement for names", "provenance": "SSA birth-cohort given names and Census 2010 surnames; public aggregates only", "owner": "Business"},
    {"id": "RN", "metric": "Productive RN hours / configured required RN hours", "denominator": "Unit/shift acuity-weighted requirement, pooled month", "lower": 0.90, "upper": 1.20, "provenance": "5.5 RN hours per patient-day is a modeling input, not a staffing recommendation; shortage scenarios evaluated separately", "owner": "Workforce"},
    {"id": "SEASON", "metric": "Peak/trough monthly ED arrival rate per active day, pooled network", "denominator": "All 36 months; compare rates rather than raw unequal-month counts", "lower": 1.10, "upper": 1.80, "provenance": "Configured seasonality plus shocks; facility curves differ", "owner": "Operations"}
]

SCENARIOS = [
    ("S01", "Chronic repeat care", 300, ["patient", "clinical_condition", "encounter", "clinical_event", "patient_coverage"], "Persistent known condition across >=2 encounters; ages and coverage reflect event date", ["CN01", "CE02", "CV01"]),
    ("S02", "Elective care and reschedule", 100, ["appointment", "encounter", "clinical_event", "service_charge", "claim"], "Old booking retained; completed procedure has resources/charge; cancelled service has no charge", ["AP01", "CH01"]),
    ("S03", "ED to IPD", 500, ["encounter", "bed_event", "clinical_condition"], "Two encounters share episode/patient; boarding begins at decision; one network admission", ["EN01", "BD03"]),
    ("S04", "Respiratory surge", 200, ["facility_day_driver", "encounter", "clinical_event", "bed_event", "staff_shift", "inventory_movement"], "Winter 2024 surge raises related demand and resource use over matched nonshock days; no deterministic individual outcome", ["RS02", "SF02"]),
    ("S05", "Bed closure", 12, ["bed_event", "encounter", "appointment"], "2024 summer staged empty-bed maintenance reduces staffed capacity; queues/deferment explicit; total lost staffed days budget 962", ["BD01", "BD02", "BD05"]),
    ("S06", "Absence and agency", 60, ["worker_assignment", "staff_shift", "financial_posting"], "2025 February temporary absence creates replacement/overtime or explicit coverage gap with linked cost", ["WK01", "SF01", "GL02"]),
    ("S07", "Stockout and expiry", 30, ["inventory_movement", "clinical_event", "financial_posting"], "Lot eligibility constrains issue; substitute/delay and waste explicitly accounted, no negative stock", ["IV01", "IV02", "IV03"]),
    ("S08", "Denial appeal and recovery", 200, ["service_charge", "claim", "claim_line", "claim_event", "financial_posting"], "Reason supported by known facts; original identity retained; partial/final recovery and cash distinct", ["CL02", "CL03", "CL04"]),
    ("S09", "Cross-month care and settlement", 200, ["encounter", "service_charge", "claim_event", "financial_posting", "finance_monthly"], "Service/recognition/settlement periods differ through explicit journal movements", ["GL01", "AX01"]),
    ("S10", "Coverage and workforce reorganization", 60, ["patient_coverage", "worker_assignment", "access_scope", "source_key_map"], "Mid-2024/2025 effective change retains old mapping and later-recorded corrections; revocation tested", ["TM01", "CV01", "AC01"]),
    ("S11", "Late correction and replay", 100, ["bed_event", "claim_event", "source_key_map"], "Late/duplicate delivery converges to independent expected state; historical knowledge not overwritten", ["TM02", "SR03"]),
    ("S12", "Window boundaries", 100, ["encounter", "claim", "claim_event", "inventory_movement", "bed_event"], "57 occupied openings, 2000 opening claims/closed-encounter contexts; nonzero final open cases and censored followup", ["EN03", "CL03", "BD03"])
]

def source_contracts():
    # Identity mappings are illustrative canonical exports; source-key transforms are explicit below.
    contracts = []
    for t in TABLES:
        contracts.append({"id": "CANON_" + t["name"].upper(), "source": t["source_authority"],
                          "target_table": t["name"], "format": "UTF-8 RFC4180 CSV or Parquet; types follow schema.json",
                          "mode": "APPEND_IMMUTABLE_VERSIONS_OR_MOVEMENTS", "business_key": t["primary_key"],
                          "field_mappings": [{"source_field": x["name"], "target_column": x["name"], "transform": "identity with schema type parsing", "required": not x["nullable"]} for x in t["columns"]],
                          "availability": "recorded_at <= export_available_at; delayed delivery never changes economic occurrence",
                          "control_totals": ["row_count", "business_key_count", "sha256", "min_max_recorded_at"],
                          "replay": "Deduplicate exact source version keys, not whole stable-person or claim identity"})
    families = [
        {"id": "WD_WORKER", "source": "WORKDAY", "target_table": "worker_assignment", "cadence": "Weekly full Sunday 07:00 UTC; daily changes 07:00 UTC", "mode": "SNAPSHOT_PLUS_VERSIONED_DELTA", "source_keys": ["EmployeeID", "EffectiveDate", "ExtractVersion"], "maps": {"EmployeeID": "worker_id", "FirstName": "given_name", "LastName": "family_name", "CostCenterReference": "cost_center_id", "ManagerEmployeeID": "manager_worker_id", "EffectiveDate": "valid_from"}},
        {"id": "WD_COST_CENTER", "source": "WORKDAY", "target_table": "cost_center", "cadence": "Weekly Sunday 07:00 UTC", "mode": "FULL_SNAPSHOT", "source_keys": ["CostCenterReference"], "maps": {"CostCenterReference": "cost_center_id", "CostCenterName": "cost_center_name", "ParentReference": "parent_cost_center_id"}},
        {"id": "WD_SECURITY", "source": "WORKDAY_SECURITY", "target_table": "access_scope", "cadence": "Daily 07:00 UTC; corrections next batch", "mode": "VERSIONED_DELTA", "source_keys": ["GrantReference", "EffectiveDate", "ExtractVersion"], "maps": {"PrincipalReference": "principal_id", "EmployeeID": "worker_id", "ScopeReference": "scope_key", "Role": "role", "Decision": "decision"}},
        {"id": "AX_ACTUAL", "source": "AXIOM", "target_table": "finance_monthly", "cadence": "Monthly close day 5 08:00 UTC; replacement corrections with new vintage", "mode": "REPLACE_DECLARED_SCOPE_VERSION", "source_keys": ["ReportID", "Period", "CostCenter", "Account", "Version"], "maps": {"Period": "accounting_month", "CostCenter": "cost_center_id", "Account": "account_catalog_id", "Amount": "amount", "Version": "vintage_id", "ReportID": "report_template_id"}},
        {"id": "AX_BUDGET", "source": "AXIOM", "target_table": "finance_monthly", "cadence": "Original December 15 before plan year; midyear revision July 1 in 2024/2025", "mode": "APPEND_VINTAGE", "source_keys": ["PlanYear", "Period", "CostCenter", "Account", "Version"], "maps": {"Period": "accounting_month", "CostCenter": "cost_center_id", "Account": "account_catalog_id", "Amount": "amount", "Version": "vintage_id"}},
        {"id": "AX_FORECAST", "source": "AXIOM", "target_table": "finance_monthly", "cadence": "Quarterly first business day, next 3 target months only", "mode": "APPEND_VINTAGE", "source_keys": ["Publication", "Period", "CostCenter", "Account", "Version"], "maps": {"Publication": "published_at", "Period": "accounting_month", "CostCenter": "cost_center_id", "Account": "account_catalog_id", "Amount": "amount", "Version": "vintage_id"}},
        {"id": "AX_STATS", "source": "AXIOM", "target_table": "finance_monthly", "cadence": "Monthly close day 5", "mode": "REPLACE_DECLARED_SCOPE_VERSION", "source_keys": ["Period", "CostCenter", "Measure", "Version"], "maps": {"Period": "accounting_month", "CostCenter": "cost_center_id", "Measure": "measure_code", "Quantity": "quantity", "Unit": "unit_code", "Version": "vintage_id"}},
        {"id": "ADT_EVENT", "source": "ADT_BED", "target_table": "bed_event", "cadence": "Event occurrence plus simulated source/delivery delay; historical bounded replay", "mode": "APPEND_EVENT_DEDUP_ID", "source_keys": ["MessageControlID"], "maps": {"MessageControlID": "bed_event_id", "BedReference": "bed_location_id", "EffectiveTime": "effective_at", "Sequence": "sequence_no", "CorrectionReference": "corrects_bed_event_id"}},
    ]
    return {"version": VERSION, "canonical_exports": contracts, "source_families": families,
            "source_transform_policy": "Resolve ID references through typed source_key_map at valid+knowledge time; parse UTC/date/decimals exactly; unknown mappings quarantine. No guessed identifiers.",
            "axiom_layout_families": ["actual-long", "actual-wide-months", "actual-with-adjustments", "budget-original", "budget-revised", "forecast-amount", "forecast-drivers", "statistics-volume", "statistics-workforce", "variance-comparison", "account-mapping", "center-mapping"],
            "wide_and_variance_policy": "Unpivot wide period columns into counted scalar canonical rows. Variance-only fields are reconciled/recomputed, never added as actuals. Mapping exports populate source_key_map/cost_center/catalog_item, not hidden tables.",
            "manifest_fields": ["file_id", "source_contract_id", "schema_version", "scope", "period", "vintage", "replacement_of", "expected_rows", "control_totals", "sha256", "available_at"],
            "faults": [{"id": "F_DUP", "action": "deduplicate exact event/version, no economic/state change"},
                       {"id": "F_LATE", "action": "retain availability; reproject affected period/bed if beyond normal lateness"},
                       {"id": "F_MISSING", "action": "mark partition incomplete, block certified close; never silently fill zero"},
                       {"id": "F_SCHEMA", "action": "quarantine incompatible layout; compatible additive fields handled only through versioned contract"},
                       {"id": "F_UNMAPPED", "action": "quarantine scoped rows; record missing key and block dependent totals"},
                       {"id": "F_REPLACE", "action": "replace exact source scope/vintage, retain prior knowledge history; no double add"},
                       {"id": "F_CORRUPT", "action": "reject/quarantine with row evidence; manifest fails until corrected"}]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check generated metadata is current without writing.")
    args = parser.parse_args()
    # Other contracts are maintained as explicit versioned JSON, not generated business data.
    for t in TABLES:
        t["rule_ids"] = [r["id"] for r in RULES if t["name"] in r["tables"]]
    schema = {"version": VERSION, "dialect": "Azure Databricks Unity Catalog Delta; offline contract only",
              "common_availability_rule": "A revision is usable only after recorded_at and export_available_at and applicable known_from; event time does not override knowledge.",
              "logical_reference_contracts": [
                  {"source": "worker_assignment.manager_worker_id", "target": "worker_assignment.worker_id", "selection": "exactly one applicable valid+knowledge revision; acyclic manager chain"},
                  {"source": "access_scope.worker_id", "target": "worker_assignment.worker_id", "selection": "stable worker exists and grant validity/knowledge checked"},
                  {"source": "source_key_map.target_key", "target_by_entity_type": {"PATIENT": "patient.patient_id", "WORKER": "worker_assignment.worker_id", "LOCATION": "location.location_id", "COST_CENTER": "cost_center.cost_center_id", "CATALOG": "catalog_item.catalog_item_id", "PAYER_PLAN": "payer_plan.payer_plan_id", "UNIT_COST_CENTER": "cost_center.cost_center_id"}, "selection": "typed lookup; UNIT_COST_CENTER source_key is the source/canonical unit association"},
                  {"source": "access_scope.scope_key", "target_by_entity_type": {"FACILITY": "facility.facility_id", "LOCATION": "location.location_id", "COST_CENTER": "cost_center.cost_center_id"}, "selection": "NETWORK only uses ALL_NETWORK sentinel"},
                  {"source": "clinical_event.consumption_group_key", "target": "inventory_movement.consumption_group_key", "selection": "group-level unit/item/lot/base-unit conservation, not a falsely unique row FK"},
                  {"source": "financial_posting.source_group_key", "target": "staff_shift.posting_group_key", "selection": "WORKFORCE domain; analogous source-specific predicates for inventory, charges, claim events and pool-close journals"}],
              "tables": TABLES}
    outputs = {
        "contracts/phase0/schema.json": json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
        "contracts/phase0/baseline.json": json.dumps(BASELINE, indent=2, ensure_ascii=False) + "\n",
        "contracts/phase0/validation-rules.json": json.dumps({"version": VERSION, "rules": RULES}, indent=2) + "\n",
        "contracts/phase0/source-contracts.json": json.dumps(source_contracts(), indent=2) + "\n",
        "contracts/phase0/clinical-type-matrix.json": json.dumps({"version": VERSION, "types": CLINICAL_MATRIX}, indent=2) + "\n",
        "contracts/phase0/realism-targets.json": json.dumps({"version": VERSION, "targets": REALISM}, indent=2) + "\n",
        "contracts/phase0/scenarios.json": json.dumps({"version": VERSION, "scenarios": [{"id": sid, "title": title, "minimum_cases": count, "tables": tables, "expected": expected, "rule_ids": rules, "owner": "Codex (user-designated baseline reviewer); future generation evidence required", "fixture_required": True} for sid, title, count, tables, expected, rules in SCENARIOS]}, indent=2) + "\n",
    }
    dictionary = ["# Phase 0 field-level data dictionary", "", "Baseline 1.0.0. Generated by `scripts/build_phase0_spec.py`; edit the authoring definitions and re-render. No business data is generated.", "",
                  "All timestamps are UTC instants; all periods are half-open. Each column inherits its table's source authority. Every correction is an append-only revision/reversal; stable master retirements retain referenced rows. Mutable demographic, assignment, condition and coverage facts are bitemporal. Financial and operational movements are immutable.", ""]
    ddl = ["-- OFFLINE PHASE 0 CONTRACT ONLY. Do not deploy before the data-phase implementation authorizes it.",
           "-- Target Unity Catalog catalog/schema must exist; namespaces below are placeholders for later configuration.",
           "-- Scalar schemas; no uncounted JSON/array business facts. PK/FK metadata does not enforce integrity.", ""]
    deferred_fks = []
    for t in TABLES:
        dictionary += [f"## {t['name']}", "", f"**Grain:** {t['grain']}  ",
                       f"**Source:** {t['source_authority']} | **Planned rows:** {t['planned_rows']:,} | **PK:** `{','.join(t['primary_key'])}`", "", t["notes"], "",
                       "| Column | Type | Nullable | Reference / allowed values / unit | Meaning |", "| --- | --- | --- | --- | --- |"]
        definitions = []
        for col in t["columns"]:
            extra = col.get("references", "")
            if col.get("allowed_values"):
                extra += " " + ", ".join(col["allowed_values"])
            if col.get("unit"):
                extra += " [" + col["unit"] + "]"
            dictionary.append(f"| `{col['name']}` | `{col['type']}` | {'yes' if col['nullable'] else 'no'} | {extra.strip()} | {col['description']} |")
            definitions.append(f"  `{col['name']}` {col['type']}" + ("" if col["nullable"] else " NOT NULL"))
            if col.get("references"):
                target, target_col = col["references"].split(".")
                deferred_fks.append(f"ALTER TABLE `healthcare_synthetic`.`core`.`{t['name']}` ADD CONSTRAINT `fk_{t['name']}_{col['name']}` FOREIGN KEY (`{col['name']}`) REFERENCES `healthcare_synthetic`.`core`.`{target}` (`{target_col}`) NOT ENFORCED;")
        definitions.append(f"  CONSTRAINT `pk_{t['name']}` PRIMARY KEY ({', '.join('`'+x+'`' for x in t['primary_key'])}) NOT ENFORCED")
        ddl += [f"CREATE TABLE IF NOT EXISTS `healthcare_synthetic`.`core`.`{t['name']}` (", ",\n".join(definitions), ") USING DELTA;", ""]
        dictionary += ["", "**Unique business keys:** " + ("; ".join(" + ".join(x) for x in t["unique_keys"]) or "Primary key only; additional conditional uniqueness is in the rule catalog."),
                       "", "**Validation rules:** " + ", ".join(t["rule_ids"]), ""]
    ddl += ["-- Informational foreign keys, added after all table definitions. Execute only under a later authorized data phase.", "-- This is a new-environment schema template, not an idempotent constraint migration or tested live deployment.", *deferred_fks, ""]
    outputs["docs/phase-0/data-dictionary.md"] = "\n".join(dictionary).rstrip() + "\n"
    outputs["contracts/phase0/databricks-schema.sql"] = "\n".join(ddl)
    total = sum(t["planned_rows"] for t in TABLES)
    n, s = BASELINE["network"], BASELINE["staffing"]
    budget_doc = ["# Three-year record budget", "", "Baseline 1.0.0. Generated from the authoritative definitions in `scripts/build_phase0_spec.py`.", "",
                  f"**{len(TABLES)} business tables; {total:,} planned records; {BASELINE['maximum_records']-total:,} remaining below the 2,000,000 hard ceiling.**", "",
                  "Envelopes include versions, lifecycle revisions, openings, corrections and declared business line facts. They are feasible planning allowances, not arbitrary quotas to pad or truncate. Future stochastic generation may use contingency, but an over-cap candidate must be recalibrated as connected histories and regenerated.", "",
                  "| Table | Inclusive planned rows | Grain |", "| --- | ---: | --- |"]
    budget_doc += [f"| `{t['name']}` | {t['planned_rows']:,} | {t['grain']} |" for t in TABLES]
    budget_doc += [f"| **Total** | **{total:,}** | |", "", "## Capacity and workload arithmetic", "",
                   "- Window: 1,096 days. Licensed capacity: 72 x 1,096 = 78,912 bed-days.",
                   "- Planned empty-bed closures remove 962 staffed bed-days, leaving 77,950. Occupied days: 12,000 intersecting IPD episodes x 5.2 clipped days = 62,400.",
                   f"- Licensed occupancy: {62400/78912:.4%}; staffed occupancy: {62400/77950:.4%}. These are calibration expectations, not fixed outcomes or clinical benchmarks.",
                   "- 12,000 IPD intervals plus 3,000 extra transfers yield 15,000 intervals. At 1.25 hours mean cleaning/turnaround, 781.25 bed-days fit within staffed slack.",
                   "- 80,000 bed events include 72 opening states, 60,000 primary transition allowance, 18,528 service/staffing/reservation changes and 1,400 corrections. Actual carry-in/open-end histories may need fewer four-transition sequences; no duplicate opening admission is generated to fill a quota.",
                   "- 130,000 encounter rows = 56,000 intersecting visits + 2,000 completed opening-AR contexts + 68,000 lifecycle versions + 4,000 corrections. Opening-only contexts do not add occupancy or new-period admissions.",
                   "- 70,000 shift rows = 52,000 worked shifts + 4,000 leave/unavailability blocks + 14,000 revisions. Never sum all shift versions as worked time.",
                   "- Productive RN supply: 52,000 x 0.70 x 10.5 = 382,200 hours. Modeled RN requirement: 62,400 x 5.5 = 343,200 hours. This permits aggregate slack and local absence/coverage gaps, not an assertion that every shift is safely staffed.",
                   "- Annual worked hours: 52,000 x 12 / 3 = 208,000. Contracted roster capacity: 180 workers x 0.65 mean FTE x 2,080 = 243,360 hours/year; other workers cover nonrostered roles. Role-specific FTE/rate histories remain varied.",
                   "", "## Counted clinical-event detail", "", "| Family | Rows |", "| --- | ---: |"]
    budget_doc += [f"| {kind} | {value:,} |" for kind, value in CLINICAL_TYPES.items()]
    budget_doc += ["", "6000 ED admissions +4800 elective +1143 direct/external +57 occupied carry-ins =12000 intersecting IPD. Code/clinical assumptions and uncensored LOS are validated separately from clipped bed-day arithmetic.",
                   "", "## Revenue, finance and allocation detail", "",
                   "56,000 claims include 54,000 current-period originals and 2,000 openings. The 160,000 event envelope counts 2,000 opening assertions, 54,000 submissions, 48,000 adjudications, 44,000 payments and 12,000 denial/appeal/resubmission/adjustment/refund/other events. Unsettled/unknown cases remain open.",
                   "", "120,000 charges have explicit billing-category intervals/quantities, split at month boundaries. 112,000 claim lines reference those charges once; unbilled/self-pay/open charge lines remain identifiable. This grain preserves billing units without inventing uncounted daily charge facts.",
                   "", "180,000 allocation rows fund patient-month/center/category detail: approximately 48,000 base IPD category allocations, 8,200 cross-month additions, 12,000 transfer-center additions, approximately 100,000 ED/OP category allocations, and approximately 11,800 nonpatient/residual/revision allowance. These are design envelopes; exact counts follow actual care and journal pools. Monthly pool close avoids daily allocation fan-out while retaining traceable signed expense.",
                   "", "All opening and monthly pool-close journals count in the following 180,000 posting rows:", "", "| Posting family | Rows |", "| --- | ---: |"]
    budget_doc += [f"| {kind} | {value:,} |" for kind, value in BASELINE["financial_posting_budget"].items()]
    budget_doc += ["", "The 36,000 normalized financial rows have an explicit sparse-series contract. No unbudgeted Cartesian product of all account/cost-center/scenario/vintage combinations is assumed.", "", "| Series/vintage coverage | Rows |", "| --- | ---: |"]
    budget_doc += [f"| {kind} | {value:,} |" for kind, value in BASELINE["finance_row_breakdown"].items()]
    budget_doc += ["", "Actual P&L includes 11 defined control accounts at 45 centers; balance levels use six accounts at three designated facility control centers. The six budget accounts cover gross/contra revenue and four cost pools. Source expense accounts zeroed by monthly close remain required reconciliation controls, not arbitrary padding. Correction-vintage allowance is a maximum plan, not a mandate to fabricate corrections.",
                   "", "## Physical release accounting", "",
                   "Every business version/opening is counted above. Derived intervals/calendar/census stay views. Export snapshots, repeated deliveries and raw-file mirrors report their physical serialized counts and bytes separately from canonical rows. Control reports contain metrics, hashes and evidence rather than hidden business transactions.",
                   "", "Future generation must publish actual per-table and total counts, source mirror counts and reserve consumption. No generator or patient records have been created in Phase 0.", ""]
    outputs["docs/phase-0/record-budget.md"] = "\n".join(budget_doc)
    differences = []
    for name, content in outputs.items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                differences.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    if differences:
        raise SystemExit("Stale generated contracts: " + ", ".join(differences))
    print(f"Phase 0 metadata {'verified' if args.check else 'rendered'}: {len(TABLES)} tables, "
          f"{sum(t['planned_rows'] for t in TABLES):,} planned rows. No patient data generated.")

if __name__ == "__main__":
    main()
