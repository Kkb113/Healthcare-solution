"""Deterministic stratified review selection, rendering and recorded reviewer gate."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from .master_validation import years


def order(row, field):
    return hashlib.sha256(("identity-review/" + row[field]).encode()).hexdigest()


def select_review(tables, config):
    patients = sorted((r for r in tables["patient"] if r["revision_no"] == 1), key=lambda r: order(r, "patient_id"))
    histories = Counter(r["patient_id"] for r in tables["patient"])
    def patient_features(row):
        age = years(row["birth_date"], "2023-01-01")
        band = next(g for g in config["population"]["age_groups"] if int(g.split("-")[0]) <= age <= int(g.split("-")[1]))
        return {"age/" + band, "sex/" + row["administrative_sex"], "language/" + row["preferred_language"],
                "race/" + row["race_ethnicity"], "history/" + str(histories[row["patient_id"]] > 1)}
    workers_by_id = defaultdict(list)
    for row in tables["worker_assignment"]:
        workers_by_id[row["worker_id"]].append(row)
    workers = sorted((max(rows, key=lambda r: r["revision_no"]) for rows in workers_by_id.values()), key=lambda r: order(r, "worker_id"))
    def worker_features(row):
        return {"role/" + row["role"], "type/" + row["worker_type"], "site/" + row["facility_id"],
                "late-hire/" + str(row["hire_date"] >= "2023-01-01"), "terminated/" + str(row["termination_date"] is not None)}
    def choose(rows, count, features):
        wanted = set().union(*(features(r) for r in rows))
        selected = []
        while wanted:
            choices = [r for r in rows if r not in selected]
            best = max(choices, key=lambda r: len(features(r) & wanted))
            selected.append(best)
            wanted -= features(best)
        for row in rows:
            if len(selected) >= count:
                break
            if row not in selected:
                selected.append(row)
        if len(selected) != min(count, len(rows)):
            raise ValueError("review sample cannot meet declared size")
        return selected
    selected_patients = choose(patients, config["review"]["patients"], patient_features)
    selected_workers = choose(workers, config["review"]["workers"], worker_features)
    return selected_patients, selected_workers, {
        "patient_ids": [r["patient_id"] for r in selected_patients], "worker_ids": [r["worker_id"] for r in selected_workers],
        "patient_strata": sorted(set().union(*(patient_features(r) for r in selected_patients))),
        "worker_strata": sorted(set().union(*(worker_features(r) for r in selected_workers)))}


def render_review(tables, config):
    patients, workers, selection = select_review(tables, config)
    history = Counter(r["patient_id"] for r in tables["patient"])
    facilities = {r["facility_id"]: r["facility_code"] for r in tables["facility"]}
    text = ["# Master-data identity realism sample", "", "Scope: 100 synthetic patient identities and 50 synthetic worker identities, or the configured sample sizes. These are deliberate review mirrors, not extra canonical business records.", "", "Patient ages are at January 1, 2023. Worker rows show the latest known assignment, including later hires and former employees. Missing/unknown fields retain their meaning.", "", "## Patient identities", "", "| Stable identity | Name | Birth date / age | Administrative sex | Self-reported category | Language | Fictional address | History rows |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in patients:
        name = " ".join(v for v in (row["given_name"], row["middle_name"], row["family_name"], row["suffix"]) if v)
        text.append(f"| {row['patient_id']} | {name} | {row['birth_date']} / {years(row['birth_date'], '2023-01-01')} | {row['administrative_sex']} | {row['race_ethnicity']} | {row['preferred_language']} | {row['address_line']}, {row['city']} {row['state_code']} {row['postal_code']} | {history[row['patient_id']]} |")
    text += ["", "## Worker identities", "", "| Stable identity | Name | Role / specialty / credential | Employer | Arrangement / FTE | Hire / end | Credential interval | Loaded hourly cost |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in workers:
        text.append(f"| {row['worker_id']} | {row['given_name']} {row['family_name']} | {row['role']} / {row['specialty']} / {row['credential_code']} | {facilities[row['facility_id']]} | {row['worker_type']} / {row['fte']} | {row['hire_date']} / {row['termination_date'] or 'open'} | {row['credential_valid_from']} to {row['credential_valid_to']} | USD {row['hourly_cost_rate']} |")
    body = "\n".join(text) + "\n"
    selection.update({"sample_sha256": hashlib.sha256(body.encode()).hexdigest(), "patient_count": len(patients), "worker_count": len(workers),
                      "mirror_rows": len(patients) + len(workers), "mirror_bytes": len(body.encode())})
    return body, selection


def review_gate(selection, decision):
    passed = (decision is not None and decision.get("status") == "APPROVED" and decision.get("sample_sha256") == selection["sample_sha256"]
              and decision.get("patient_identities_reviewed") == selection["patient_count"] >= 100
              and decision.get("worker_identities_reviewed") == selection["worker_count"] >= 50
              and not decision.get("unresolved_critical_findings", ["MISSING_DISPOSITION"]))
    return {"rule_id": "REVIEW_SAMPLE", "severity": "P0", "scope": "STRATIFIED_IDENTITY_REVIEW", "status": "PASS" if passed else "PENDING_REVIEW",
            "sample_sha256": selection["sample_sha256"], "reviewer": decision.get("reviewer") if passed else None,
            "failures": [] if passed else [{"record_key": "review-sample", "reason": "Missing or stale recorded identity realism review"}]}
