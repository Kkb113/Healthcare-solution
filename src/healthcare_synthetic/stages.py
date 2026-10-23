"""Registered modules with small, configuration-driven development implementations.

These are executable extension points, not the later full healthcare simulators.
Each module owns its scalar projections. It reads only its declared parents.
"""
from __future__ import annotations

import copy
import json
from datetime import timedelta
from pathlib import Path

from .core import (Clock, age_on, allocate_cents, canonical, code_at, digest, draw,
                   instant, local_instant, money, stable_id, temporal_lookup)
from .sources import parse, recovery_exercises, serialize
from .validation import defects, execute, gate, profile, reconcile_candidate, validate_candidate, validate_exports

ROOT = Path(__file__).resolve().parents[2]


def output(tables=None, **controls):
    return {"tables": tables or {}, "controls": controls}


def identities(config, reference, parents):
    rows = []
    for person in reference["patients"]:
        key = stable_id("patient", person["source_key"])
        name = person.get("name") or person["names"][draw(config["seed"], key, config["stages"]["identities"]["name_stream"], upper=len(person["names"]))]
        rows.append({"key": key, "name": name, "dob": person["dob"], "service_date": person["service_date"],
                     "age": age_on(person["dob"], person["service_date"]), "email": key + "@example.invalid"})
    workers = [{**r, "key": stable_id("worker_version", r["key"]), "worker": stable_id("worker", r["worker"])} for r in reference["workers"]]
    catalog = [{"key": stable_id("catalog", r["domain"], r["code"], r["version"]), **r} for r in reference["codes"]]
    return output({"patient": rows, "worker_assignment": workers, "catalog_item": catalog})


def clinical(config, reference, parents):
    cfg = config["stages"]["clinical"]
    if not 0 <= cfg["observation_min"] <= cfg["observation_max"] <= 100:
        raise ValueError("invalid observation fixture range")
    code = code_at(reference["codes"], "DIAGNOSIS", "FIXTURE_DX", cfg["code_date"], cfg["known_at"])
    return output(observation_min=cfg["observation_min"], observation_max=cfg["observation_max"], unit=cfg["unit"], code_version=code["version"])


def demand(config, reference, parents):
    cfg, pathway = config["stages"]["demand"], parents["clinical"]["controls"]
    if not 1 <= cfg["acuity_min"] <= cfg["acuity_max"] <= 5:
        raise ValueError("invalid configured acuity range")
    patient = stable_id("patient", cfg["patient_source"])
    if patient not in {r["key"] for r in parents["identities"]["tables"]["patient"]}:
        raise ValueError("demand references missing patient")
    ed, ipd = stable_id("encounter", patient, "ED"), stable_id("encounter", patient, "IPD")
    rows = []
    for key, kind, prior, start, end in ((ed, "ED", None, cfg["ed_start"], cfg["admit"]), (ipd, "IPD", ed, cfg["admit"], cfg["discharge"])):
        if instant(start) >= instant(end):
            raise ValueError("invalid encounter interval")
        rows.append({"key": key, "patient": patient, "type": kind, "prior": prior, "start": start, "end": end,
                     "acuity": cfg["acuity_min"] + draw(config["seed"], key, "acuity", upper=1 + cfg["acuity_max"] - cfg["acuity_min"])})
    clock = Clock(config["clock"]["start"], config["clock"]["end"])
    for visit in rows:
        clock.schedule(stable_id("observation", visit["key"]), visit["start"], 10, {"encounter": visit["key"]})
    observations = []
    while clock:
        event = clock.pop()
        observations.append({"key": event["event_id"], "encounter": event["payload"]["encounter"], "at": event["at"],
                             "value": str(pathway["observation_min"] + draw(config["seed"], event["event_id"], "observation", upper=1 + pathway["observation_max"] - pathway["observation_min"])), "unit": pathway["unit"]})
    return output({"encounter": rows, "clinical_event": observations})


def resources(config, reference, parents):
    cfg = config["stages"]["resources"]
    visit = next(r for r in parents["demand"]["tables"]["encounter"] if r["type"] == "IPD")
    if not instant(visit["start"]) < instant(cfg["transfer"]) < instant(visit["end"]):
        raise ValueError("transfer outside IPD interval")
    beds = [{"key": stable_id("interval", visit["key"], i), "bed": bed, "patient": visit["patient"], "start": start, "end": end}
            for i, bed, start, end in ((0, "fixture-bed-a", visit["start"], cfg["transfer"]), (1, "fixture-bed-b", cfg["transfer"], visit["end"]))]
    start, end = local_instant(cfg["shift_start_local"]), local_instant(cfg["shift_end_local"])
    shift = {"key": stable_id("shift", "worker-a", start), "worker": stable_id("worker", "worker-a"),
             "start": start, "end": end, "worked": str(int((end - start).total_seconds()) // 3600),
             "productive": cfg["productive"], "nonproductive": cfg["nonproductive"], "break": cfg["break"]}
    stock = [{"key": stable_id("stock", kind), "qty": cfg[field]} for kind, field in (("opening", "stock_opening"), ("receipt", "stock_receipt"), ("consumption", "stock_consume"))]
    return output({"bed_interval": beds, "staff_shift": [shift], "inventory_movement": stock})


def billing(config, reference, parents):
    # Parents provide the resource/care boundary before any billing can publish.
    if not parents["resources"]["tables"]["bed_interval"]:
        raise ValueError("no performed resource context")
    cfg = config["stages"]["billing"]
    from decimal import Decimal
    units, price = Decimal(cfg["units"]), Decimal(cfg["unit_price"])
    billed = money(units * price)
    payment, refund = money(cfg["partial_payment"]), money(cfg["refund"])
    if not 0 <= refund <= payment <= billed or units <= 0 or price <= 0:
        raise ValueError("invalid payment/refund fixture")
    claim, charge = stable_id("claim", "opening-claim"), stable_id("charge", "fixture-service")
    pay, ret = stable_id("payment", claim), stable_id("refund", claim)
    postings = []
    for journal, amount, debit_account, credit_account in ((pay, payment, "cash", "ar"), (ret, refund, "ar", "cash")):
        for side, account in (("debit", debit_account), ("credit", credit_account)):
            postings.append({"key": stable_id("posting", journal, side, account), "journal": journal,
                             "debit": amount if side == "debit" else "0.00", "credit": amount if side == "credit" else "0.00"})
    allocation = allocate_cents(cfg["cost_pool"], cfg["weights"])
    return output({
        "service_charge": [{"key": charge, "units": cfg["units"], "price": cfg["unit_price"], "billed": billed}],
        "claim": [{"key": claim, "billed": billed, "opening_ar": billed}],
        "claim_line": [{"key": stable_id("claimline", claim, charge), "claim": claim, "charge": charge, "amount": billed}],
        "claim_event": [{"key": pay, "claim": claim, "ar_delta": -payment, "cash_delta": payment, "reverses": None},
                        {"key": ret, "claim": claim, "ar_delta": refund, "cash_delta": -refund, "reverses": pay}],
        "financial_posting": postings,
        "cost_allocation": [{"key": stable_id("cost", destination), "destination": destination, "amount": amount} for destination, amount in allocation.items()],
        "finance_monthly": [{"key": stable_id("finance", cfg["month"], "ACTUAL", "v1"), "month": cfg["month"], "scenario": "ACTUAL", "vintage": "v1", "amount": money(cfg["cost_pool"]), "unit": "USD"}]
    })


def serialization(config, reference, parents):
    cfg = config["stages"]["serialization"]
    workers = [{"key": r["key"], "EmployeeID": r["worker"], "FirstName": r["name"].split()[0],
                "LastName": r["name"].split()[-1], "Rate": r["rate"]} for r in parents["identities"]["tables"]["worker_assignment"]]
    monthly = [{"key": r["key"], "Period": r["month"], "Version": r["vintage"], "amount": r["amount"]} for r in parents["billing"]["tables"]["finance_monthly"]]
    envelopes = [serialize("WORKDAY", "fixture-worker-history", cfg["vintage"], cfg["available_at"], workers,
                           {"key": "string", "EmployeeID": "string", "FirstName": "string", "LastName": "string", "Rate": "decimal"}),
                 serialize("AXIOM", "fixture-finance/2024-11", cfg["vintage"], cfg["available_at"], monthly,
                           {"key": "string", "Period": "string", "Version": "string", "amount": "decimal"})]
    for envelope in envelopes:
        rows = parse(envelope, envelope["manifest"]["schema"])
        if digest(rows) != digest(sorted(rows, key=canonical)):
            raise ValueError("source canonical row ordering")
    return output(envelopes=envelopes, physical_rows=sum(e["manifest"]["expected_rows"] for e in envelopes),
                  physical_bytes=sum(e["manifest"]["bytes"] for e in envelopes))


def faults(config, reference, parents):
    if config["stages"]["faults"]["enabled"] is not True:
        raise ValueError("mandatory source negative controls cannot be disabled")
    return output(recovery=recovery_exercises())


def mutate(data, path, value):
    result = copy.deepcopy(data)
    cursor = result
    parts = path.split(".")
    for part in parts[:-1]:
        cursor = cursor[int(part)] if isinstance(cursor, list) else cursor[part]
    final = int(parts[-1]) if isinstance(cursor, list) else parts[-1]
    cursor[final] = copy.deepcopy(value)
    return result


def microfixtures(catalog):
    results, controls = [], []
    for case in catalog["cases"]:
        positive = execute(case["rule_id"], case["positive"], case["severity"], case["case_key"])
        results.append(positive)
        for fault in case["faults"]:
            data = case["positive"]
            for change in fault["changes"]:
                data = mutate(data, change["path"], change["value"])
            result = execute(case["rule_id"], data, case["severity"], case["case_key"] + "/" + fault["name"])
            detected = result["status"] == "FAIL" and fault["reason_contains"] in result["failures"][0]["reason"]
            controls.append({"rule_id": case["rule_id"], "fault": fault["name"], "status": "PASS" if detected else "FAIL",
                             "expected_detector": fault["reason_contains"], "detector_result": result})
    return results, controls


def validation(config, reference, parents):
    from .engine import merged
    path = config["stages"]["validation"]["rules"]
    if path != "contracts/phase1/rule-fixtures.json":
        raise ValueError("unapproved rule-fixture catalog")
    catalog = json.loads((ROOT / path).read_text(encoding="utf-8"))
    required_rules = {r["id"]: r["severity"] for r in json.loads((ROOT / "contracts/phase0/validation-rules.json").read_text(encoding="utf-8"))["rules"]}
    cases = catalog["cases"]
    if len(cases) != len(required_rules) or {c["rule_id"]: c["severity"] for c in cases} != required_rules:
        raise ValueError("rule-fixture coverage/severities differ from frozen Phase 0 catalog")
    if any(not c["faults"] or c["classification"] not in ("VALID_BUSINESS", "ADVERSE_OUTCOME") for c in cases):
        raise ValueError("every rule requires positive and negative controls with explicit classifications")
    results, negative = microfixtures(catalog)
    tables = json.loads(canonical(merged(parents)))
    results.extend(validate_candidate(tables, config["expectations"]))
    results.append(validate_exports(tables, parents["serialization"]["controls"]["envelopes"]))
    recovery = parents["faults"]["controls"]["recovery"]
    expected_faults = {"F_DUP", "F_LATE", "F_MISSING", "F_SCHEMA", "F_UNMAPPED", "F_REPLACE", "F_CORRUPT"}
    if len(recovery) != 7 or {r["fault_id"] for r in recovery} != expected_faults:
        raise ValueError("source recovery coverage incomplete")
    for entry in recovery:
        results.append({"rule_id": entry["fault_id"], "severity": "P0", "scope": "SOURCE_RECOVERY", "status": entry["status"],
                        "failures": [] if entry["status"] == "PASS" else [{"record_key": entry["fault_id"], "reason": entry["observed"]}]})
    for entry in negative:
        results.append({"rule_id": "NEGATIVE_" + entry["rule_id"] + ":" + entry["fault"], "severity": "P0", "scope": "NEGATIVE_CONTROL",
                        "status": entry["status"], "failures": [] if entry["status"] == "PASS" else [{"record_key": entry["fault"], "reason": "intended detector missed seeded fault"}]})
    selected = temporal_lookup(reference["workers"], "worker", "worker-a", "2024-11-03T06:00:00Z", "2024-11-04T00:00:00Z")
    corrected = temporal_lookup(reference["workers"], "worker", "worker-a", "2024-11-03T06:00:00Z", "2024-11-11T00:00:00Z")
    controls = parents["clinical"]["controls"]
    expected = config["expectations"]
    pass_selection = (selected["rate"] == expected["worker_before_rate"] and corrected["rate"] == expected["worker_after_rate"]
                      and controls["code_version"] == expected["code_version"])
    results.append({"rule_id": "P1_ASOF_LOOKUPS", "severity": "P0", "scope": "DEVELOPMENT_PROJECTION", "status": "PASS" if pass_selection else "FAIL",
                    "failures": [] if pass_selection else [{"record_key": "worker-a/FIXTURE_DX", "reason": "golden bitemporal/code release selection"}]})
    return output(results=results, negative_controls=negative, source_recovery=parents["faults"]["controls"]["recovery"],
                  profiling=profile(tables), defects=defects(results), gate=gate(results),
                  reconciliation=reconcile_candidate(tables, expected),
                  coverage_scope="Microfixtures and declared scalar development projections only; full Phase 0 data rules remain unexecuted on release data.")


IMPLEMENTATIONS = {"identities": identities, "clinical": clinical, "demand": demand, "resources": resources,
                   "billing": billing, "serialization": serialization, "faults": faults, "validation": validation}
