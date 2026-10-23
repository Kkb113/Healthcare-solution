"""Bounded master-data consumer helpers; no operational or analytics solution."""
from datetime import date


def visible(row, valid_at, known_at):
    return (row["valid_from"] <= valid_at and (row["valid_to"] is None or valid_at < row["valid_to"])
            and row["known_from"] <= known_at and (row["known_to"] is None or known_at < row["known_to"])
            and row["recorded_at"] <= known_at and row["export_available_at"] <= known_at)


def one(rows, reason):
    if len(rows) != 1:
        raise ValueError(f"{reason}: expected one applicable record, found {len(rows)}")
    return rows[0]


def person_at(rows, patient_id, valid_at, known_at):
    return one([r for r in rows if r["patient_id"] == patient_id and visible(r, valid_at, known_at)], "patient identity")


def worker_at(rows, worker_id, valid_at, known_at):
    return one([r for r in rows if r["worker_id"] == worker_id and visible(r, valid_at, known_at)], "worker identity")


def eligible_worker(rows, worker_id, valid_at, known_at):
    row = worker_at(rows, worker_id, valid_at, known_at)
    day = valid_at[:10]
    return (row["hire_date"] <= day and (row["termination_date"] is None or day < row["termination_date"])
            and row["credential_valid_from"] <= day < row["credential_valid_to"])


def primary_coverage(tables, patient_id, valid_at, known_at):
    versions = {r["patient_version_id"] for r in tables["patient"] if r["patient_id"] == patient_id}
    return one([r for r in tables["patient_coverage"] if r["patient_version_id"] in versions and visible(r, valid_at, known_at)], "primary coverage")


def source_target(rows, namespace, entity_type, source_key, valid_at, known_at):
    row = one([r for r in rows if (r["source_namespace"], r["entity_type"], r["source_key"]) == (namespace, entity_type, source_key)
               and r["mapping_status"] == "MAPPED" and visible(r, valid_at, known_at)], "typed crosswalk")
    return row["target_key"]


def authorized(tables, principal, role, scope_type, scope, valid_at, known_at):
    grants = [r for r in tables["access_scope"] if (r["principal_id"], r["role"], r["scope_type"], r["scope_key"]) == (principal, role, scope_type, scope)
              and visible(r, valid_at, known_at)]
    if not grants or any(r["decision"] == "REVOKED" for r in grants):
        return False
    return all(eligible_worker(tables["worker_assignment"], r["worker_id"], valid_at, known_at) for r in grants)
