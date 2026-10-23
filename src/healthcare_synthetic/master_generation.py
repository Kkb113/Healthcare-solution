"""Full-schema master records and opening health context, with no encounter simulation."""
from __future__ import annotations

import bisect
import calendar
import copy
import json
import re
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from .core import age_on, draw, instant, money, stable_id

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = {t["name"]: t for t in json.loads((ROOT / "contracts/phase0/schema.json").read_text())["tables"]}
OPENING = "2022-12-15T06:00:00Z"


class MasterGenerator:
    def __init__(self, config, references, run_id):
        self.config, self.refs, self.run_id = config, references, run_id
        self.seed = config["seed"]
        self.weights = {}

    def pick(self, entity, stream, values):
        key = ("pool", id(values)) if len(values) > 100 else tuple(tuple(v) for v in values)
        if key not in self.weights:
            cumulative, total = [], 0
            for label, weight in values:
                total += int(weight)
                cumulative.append(total)
            self.weights[key] = ([v[0] for v in values], cumulative, total, values)
        labels, cumulative, total, _ = self.weights[key]
        return labels[bisect.bisect_right(cumulative, draw(self.seed, entity, stream, upper=total))]

    def weighted(self, entity, stream, mapping):
        # JSON object order is not part of canonical configuration identity.
        return self.pick(entity, stream, sorted(mapping.items()))

    def row(self, table, record_key, recorded=OPENING, **fields):
        row = {c["name"]: None for c in SCHEMA[table]["columns"]}
        authority = SCHEMA[table]["source_authority"]
        row.update(source_system=authority, source_record_id=str(record_key), recorded_at=recorded,
                   export_available_at=(instant(recorded) + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
                   generation_run_id=self.run_id)
        unknown = set(fields) - set(row)
        if unknown:
            raise ValueError(f"unregistered columns {table}: {unknown}")
        row.update(fields)
        for column in SCHEMA[table]["columns"]:
            if row[column["name"]] is None and not column["nullable"]:
                raise ValueError(f"missing required generation field {table}.{column['name']}")
        return row

    def version(self, table, identity, revision, valid_from, known_from, **fields):
        primary = SCHEMA[table]["primary_key"][0]
        return self.row(table, f"{identity}/v{revision}", known_from, **{primary: stable_id(table + "_version", identity, revision)},
                        revision_no=revision, valid_from=valid_from, valid_to=None, known_from=known_from, known_to=None, **fields)

    def history(self, table, identity, fields, changes, valid_from=OPENING, known_from=OPENING):
        rows = [self.version(table, identity, 1, valid_from, known_from, **fields)]
        current = rows[0]
        for effective, known, updates in changes:
            current["known_to"] = known
            old_fields = {k: current[k] for k in fields}
            closed = self.version(table, identity, len(rows) + 1, current["valid_from"], known, **old_fields)
            closed["valid_to"] = effective
            rows.append(closed)
            new_fields = {**old_fields, **updates}
            current = self.version(table, identity, len(rows) + 1, effective, known, **new_fields)
            rows.append(current)
        return rows

    def names(self, entity, birth, series=None, self_report=None):
        if series is None:
            series = "F" if draw(self.seed, entity, "name-series", upper=2) == 0 else "M"
        if draw(self.seed, entity, "cross-series", upper=100) < self.config["population"]["naming_series_cross_percent"]:
            series = "M" if series == "F" else "F"
        cohort = int(birth[:4]) // 10 * 10
        pool = self.refs["names"]["given_names"][f"{cohort}/{series}"]
        given = self.pick(entity, "given-name", pool)
        surname_pool = self.refs["names"]["surnames"]
        if self_report in self.refs["names"]["surname_profiles"] and draw(self.seed, entity, "surname-cross-population", upper=100) >= self.config["population"]["surname_population_mix_percent"]:
            surname_pool = self.refs["names"]["surname_profiles"][self_report]
        family = self.pick(entity, "family-name", surname_pool)
        if draw(self.seed, entity, "hyphenated", upper=100) < self.config["population"]["hyphenated_surname_percent"]:
            other = self.pick(entity, "second-family-name", self.refs["names"]["surnames"])
            if other != family:
                family += "-" + other
        return given, family, pool

    def address(self, entity):
        cfg = self.config["population"]
        place = self.pick(entity, "geography", [[str(i), p["weight"]] for i, p in enumerate(cfg["geography"])])
        area = cfg["geography"][int(place)]
        number = 101 + draw(self.seed, entity, "street-number", upper=9800)
        street = cfg["streets"][draw(self.seed, entity, "street-name", upper=len(cfg["streets"]))]
        kind = cfg["street_types"][draw(self.seed, entity, "street-type", upper=len(cfg["street_types"]))]
        line = f"{number} {street} {kind}"
        if draw(self.seed, entity, "apartment", upper=100) < 18:
            line += f" Apt {1 + draw(self.seed, entity, 'unit', upper=48)}"
        return {"address_line": line, "city": area["city"], "state_code": area["state"], "postal_code": area["postal_code"]}

    def organizations(self, parents):
        cfg = self.config["organization"]
        facilities, centers, locations = [], [], []
        for site in cfg["facilities"]:
            fid = stable_id("facility", site["code"])
            facilities.append(self.row("facility", site["code"], facility_id=fid, facility_code=site["code"], facility_name=site["name"],
                                       city=site["city"], state_code="IL", postal_code=site["postal_code"], timezone="America/Chicago",
                                       opened_on="2001-01-01", currency="USD", fiscal_calendar="CALENDAR_YEAR"))
            cc = {code: stable_id("cost_center", fid, code) for code, _, _ in cfg["centers"]}
            for code, name, kind in cfg["centers"]:
                centers.append(self.row("cost_center", site["code"] + "/" + code, cost_center_id=cc[code], facility_id=fid,
                                        parent_cost_center_id=None if code == "ADMINISTRATION" else cc["ADMINISTRATION"],
                                        cost_center_code=site["code"] + "-" + code, cost_center_name=name, center_type=kind, active_from="2001-01-01"))
            loc = {code: stable_id("location", fid, code) for code, *_ in cfg["departments"] + cfg["units"]}
            def add(code, name, kind, service, center, parent=None, isolation=False):
                key = loc.setdefault(code, stable_id("location", fid, code))
                locations.append(self.row("location", site["code"] + "/" + code, location_id=key, facility_id=fid,
                                          parent_location_id=parent, cost_center_id=cc[center], location_code=code, location_name=name,
                                          location_type=kind, service_line=service, licensed_bed=kind == "BED", isolation_capable=isolation,
                                          active_from="2001-01-01"))
            for code, name, service, center in cfg["departments"]:
                add(code, name, "DEPARTMENT", service, center)
            for code, name, department, service, center in cfg["units"]:
                add(code, name, "UNIT", service, center, loc[department])
            for unit, rooms, beds in cfg["beds"]:
                service, center = ("MEDICINE", "MEDICINE") if unit == "MED" else (("SURGERY", "SURGERY") if unit == "SURG" else ("ICU", "ICU"))
                for room in range(1, rooms + 1):
                    code = f"{unit}-R{room:02}"
                    isolated = unit == "ICU" or code in cfg["isolation_room_codes"]
                    add(code, f"{unit} Room {room}", "ROOM", service, center, loc[unit], isolated)
                    for bed in range(1, beds + 1):
                        add(f"{code}-B{bed}", f"{unit} Room {room} Bed {chr(64 + bed)}", "BED", service, center, loc[code], isolated)
        return {"facility": facilities, "cost_center": centers, "location": locations}

    def patients(self, parents):
        cfg = self.config["population"]
        identities = [stable_id("patient", i) for i in range(cfg["patients"])]
        changed = sorted(identities, key=lambda p: draw(self.seed, p, "history-rank"))[:cfg["patient_history_changes"]]
        changes_by_id = {p: i for i, p in enumerate(changed)}
        result = []
        for index, patient in enumerate(identities):
            band = self.weighted(patient, "age-band", cfg["age_groups"])
            low, high = map(int, band.split("-"))
            age = low + draw(self.seed, patient, "age-in-band", upper=high - low + 1)
            month = 1 + draw(self.seed, patient, "birth-month", upper=12)
            year = 2023 - age - (month != 1)
            day = 1 + draw(self.seed, patient, "birth-day", upper=calendar.monthrange(year, month)[1])
            if month == 1 and day > 1:
                year -= 1
            birth = date(year, month, day).isoformat()
            sex = self.weighted(patient, "administrative-sex", cfg["administrative_sex"])
            self_report = self.weighted(patient, "self-reported-race", cfg["race_ethnicity"])
            given, family, pool = self.names(patient, birth, sex if sex in ("M", "F") else None, self_report)
            middle = None
            if draw(self.seed, patient, "middle-present", upper=100) < cfg["middle_name_percent"]:
                middle = self.pick(patient, "middle-name", pool)
                if draw(self.seed, patient, "middle-format", upper=100) < cfg["middle_initial_percent"]:
                    middle = middle[0] + "."
            suffix = None
            if sex == "M" and draw(self.seed, patient, "suffix", upper=100) < cfg["suffix_percent"]:
                suffix = ["Jr.", "Sr.", "III"][draw(self.seed, patient, "suffix-kind", upper=3)]
            address_key = f"shared-residence/{index // 2}" if index < cfg["shared_address_people"] else patient
            address = self.address(address_key)
            missing = draw(self.seed, patient, "contact-missing", upper=100) < cfg["contact_missing_percent"]
            email = re.sub(r"[^a-z]", "", (given + "." + family).lower()) + "." + patient[-6:] + "@patients.example"
            area = {"Springfield": "217", "Peoria": "309", "Rockford": "815"}[address["city"]]
            phone = f"+1-{area}-555-{100 + draw(self.seed, address_key, 'phone', upper=100):04}"
            gender = None
            if draw(self.seed, patient, "gender-unknown", upper=100) >= cfg["gender_reporting"]["unknown_percent"]:
                distribution = cfg["gender_reporting"].get(sex, cfg["gender_reporting"]["OTHER"])
                gender = self.weighted(patient, "gender-self-report", distribution)
            fields = dict(patient_id=patient, mrn=f"MRN-{index + 1:08}", given_name=given, middle_name=middle,
                          family_name=family, suffix=suffix, birth_date=birth, administrative_sex=sex, gender_identity=gender,
                          race_ethnicity=self_report,
                          preferred_language=self.weighted(patient, "language", cfg["languages"]),
                          test_email=None if missing else email, test_phone=None if missing else phone, deceased_at=None, **address)
            history = []
            if patient in changes_by_id:
                rank = changes_by_id[patient]
                year_change = 2023 + draw(self.seed, patient, "change-year", upper=3)
                effective = f"{year_change}-{1 + draw(self.seed, patient, 'change-month', upper=12):02}-15T06:00:00Z"
                if rank < cfg["history_kinds"]["family_name"]:
                    new_family = self.pick(patient, "changed-family", self.refs["names"]["surnames"])
                    if new_family == family:
                        new_family = family + "-" + self.refs["names"]["surnames"][-1][0]
                    update = {"family_name": new_family}
                elif rank < cfg["history_kinds"]["family_name"] + cfg["history_kinds"]["address"]:
                    update = self.address(patient + "/new-residence")
                else:
                    effective = "2023-01-01T06:00:00Z"
                    update = {"middle_name": self.pick(patient, "corrected-middle", pool)}
                known = (instant(effective) + timedelta(days=2 + draw(self.seed, patient, "report-delay", upper=12))).isoformat().replace("+00:00", "Z")
                history.append((effective, known, update))
            result.extend(self.history("patient", patient, fields, history))
        return {"patient": result}

    def catalog(self, parents):
        rows = []
        for code in self.refs["codes"]["rows"]:
            group = "REFERENCE_ONLY"
            if code["domain"] == "DIAGNOSIS":
                group = {"I50": "HEART_FAILURE", "J44": "COPD", "J18": "PNEUMONIA", "K40": "GENERAL_SURGERY", "M17": "ORTHOPEDIC", "M16": "ORTHOPEDIC"}.get(code["code"][:3], "GENERAL_MEDICINE")
            else:
                group = "ORTHOPEDIC" if code["code"].startswith("0SR") else "GENERAL_SURGERY"
            fields = {k: code[k] for k in ("domain", "code_system", "code", "version", "display", "valid_from", "valid_to")}
            rows.append(self.row("catalog_item", f"{code['code_system']}/{code['code']}/{code['version']}", code["valid_from"] + "T00:00:00Z",
                                 catalog_item_id=stable_id("catalog", code["code_system"], code["code"], code["version"]), clinical_group=group, **fields))
        local = self.refs["local"]["items"]
        local_ids = {r["code"]: stable_id("catalog", r["code_system"], r["code"], r["version"]) for r in local}
        for item in local:
            fields = {k: v for k, v in item.items() if k != "allergen_code"}
            rows.append(self.row("catalog_item", f"HOSPITAL_LOCAL/{item['code']}/{item['version']}", "2022-01-01T00:00:00Z",
                                 catalog_item_id=local_ids[item["code"]], allergen_catalog_id=local_ids.get(item.get("allergen_code")), **fields))
        return {"catalog_item": rows}

    def workforce(self, parents):
        cfg = self.config["workforce"]
        organizations = parents["organizations"]
        facilities = organizations["facility"]
        locations = {(r["facility_id"], r["location_code"]): r for r in organizations["location"]}
        result = []
        for site_index, facility in enumerate(facilities):
            fid = facility["facility_id"]
            leader = stable_id("worker", fid, "ADMIN", 0)
            for role_spec in cfg["roles"]:
                role, count = role_spec["role"], role_spec["count_per_facility"]
                for index in range(count):
                    worker = stable_id("worker", fid, role, index)
                    late = (role == "ADMIN" and index >= count - 3) or (role == "PHYSICIAN" and index >= count - 3)
                    terminates = (role == "RN" and index >= count - 4) or (role == "HOUSEKEEPING" and index >= count - 2)
                    age = 24 + draw(self.seed, worker, "worker-age", upper=43)
                    birth = f"{2023 - age}-{'01' if late else '06'}-15"
                    given, family, _ = self.names(worker, birth)
                    hire = f"2024-{2 + index % 4:02}-01" if late else f"{max(int(birth[:4]) + 20, 2010 + draw(self.seed, worker, 'hire-year', upper=12))}-03-01"
                    specialization = role_spec["specialties"][index % len(role_spec["specialties"])]
                    credential = role_spec["credentials"][index % len(role_spec["credentials"])]
                    possible_homes = cfg["specialty_home"][specialization]
                    home = possible_homes[index % len(possible_homes)]
                    location = locations[(fid, home)]
                    center_id = location["cost_center_id"]
                    if specialization in cfg["specialty_center_overrides"]:
                        center_id = stable_id("cost_center", fid, cfg["specialty_center_overrides"][specialization])
                    manager = leader if index == 0 or role == "ADMIN" else stable_id("worker", fid, role, 0)
                    if role == "ADMIN" and index >= 5 and index % 5:
                        manager = stable_id("worker", fid, "ADMIN", index % 5)
                    worker_type = "AGENCY" if role == "RN" and index in range(1, 7) else ("CONTRACT" if role == "PHYSICIAN" and index in range(1, 5) else "EMPLOYEE")
                    offset = sum(r["count_per_facility"] for r in cfg["roles"][:cfg["roles"].index(role_spec)] if r["role"] in cfg["rostered_roles"])
                    fte = cfg["rostered_fte_cycle"][(offset + index) % 4] if role in cfg["rostered_roles"] else ["0.800000", "1.000000"][index % 2]
                    rate = money(Decimal(role_spec["min_rate"]) + Decimal(draw(self.seed, worker, "rate-cents", upper=int((Decimal(role_spec["max_rate"]) - Decimal(role_spec["min_rate"])) * 100) + 1)) / 100)
                    rate = money(rate * (Decimal(cfg["agency_loaded_factor"]) if worker_type == "AGENCY" else (Decimal(cfg["contract_loaded_factor"]) if worker_type == "CONTRACT" else 1)))
                    credential_start = hire if late else cfg["initial_credential_start"]
                    fields = dict(worker_id=worker, employee_number=f"EMP-{site_index + 1}{cfg['roles'].index(role_spec):02}{index + 1:03}",
                                  given_name=given, family_name=family, birth_date=birth, facility_id=fid, home_location_id=location["location_id"],
                                  cost_center_id=center_id, manager_worker_id=None if worker == leader else manager,
                                  role=role, specialty=specialization, credential_code=credential, credential_valid_from=credential_start,
                                  credential_valid_to=cfg["renewed_credential_end"] if late else cfg["initial_credential_end"], worker_type=worker_type, fte=fte,
                                  hourly_cost_rate=format(rate, "f"), currency="USD", hire_date=hire, termination_date=None)
                    changes = []
                    base_time = hire + "T06:00:00Z" if late else OPENING
                    if not late:
                        effective = f"2024-{1 + draw(self.seed, worker, 'renewal-month', upper=5):02}-01T06:00:00Z"
                        known = (instant(effective) + timedelta(days=1 + draw(self.seed, worker, "hr-delay", upper=10))).isoformat().replace("+00:00", "Z")
                        update = {"credential_valid_from": effective[:10], "credential_valid_to": cfg["renewed_credential_end"],
                                  "hourly_cost_rate": format(money(rate * Decimal(cfg["renewal_loaded_factor"])), "f")}
                        if role == "RN" and index in range(3, 25, 3):
                            destination = locations[(fid, "SURG" if home == "MED" else "MED")]
                            update.update(home_location_id=destination["location_id"], cost_center_id=destination["cost_center_id"])
                        changes.append((effective, known, update))
                    if terminates:
                        effective = f"2025-{3 + index % 9:02}-01T06:00:00Z"
                        changes.append((effective, effective, {"termination_date": effective[:10]}))
                    result.extend(self.history("worker_assignment", worker, fields, changes, valid_from=base_time, known_from=base_time))
        return {"worker_assignment": result}

    def payers(self, parents):
        result = []
        cfg = self.config["coverage"]
        names = {"MEDICARE": "Prairie Senior Health", "MEDICAID": "Illinois Community Access", "COMMERCIAL": "Heartland Assurance", "SELF_PAY": "Patient Direct Responsibility"}
        for kind in names:
            for product in range(4):
                code = f"{kind}-{product + 1}"
                factor = {"MEDICARE": "0.420000", "MEDICAID": "0.300000", "COMMERCIAL": "0.620000", "SELF_PAY": "0.550000"}[kind]
                result.append(self.row("payer_plan", code, "2022-01-01T06:00:00Z", payer_plan_id=stable_id("payer", code, "2022-01-01"),
                                       plan_code=code, payer_name=names[kind], plan_name=names[kind] + [" Community", " Choice", " Select", " Access"][product],
                                       payer_type=kind, reimbursement_method="SELF_PAY" if kind == "SELF_PAY" else ("CASE_RATE" if kind in ("MEDICARE", "COMMERCIAL") else "PER_DIEM"),
                                       authorization_required=kind in ("MEDICAID", "COMMERCIAL"), allowed_factor=factor, valid_from="2022-01-01"))
        for index, kind in enumerate(("COMMERCIAL", "COMMERCIAL", "MEDICAID", "SELF_PAY")):
            code = "RENEWAL-" + str(index + 1)
            for start, end, factor in (("2022-01-01", "2024-01-01", "0.580000"), ("2024-01-01", None, "0.610000")):
                result.append(self.row("payer_plan", code + "/" + start, "2022-01-01T06:00:00Z" if end else "2023-12-01T06:00:00Z",
                                       payer_plan_id=stable_id("payer", code, start), plan_code=code, payer_name=names[kind], plan_name=names[kind] + " Annual Renewal " + str(index + 1),
                                       payer_type=kind, reimbursement_method="SELF_PAY" if kind == "SELF_PAY" else "FEE_SCHEDULE",
                                       authorization_required=kind != "SELF_PAY", allowed_factor="0.550000" if kind == "SELF_PAY" else factor, valid_from=start, valid_to=end))
        return {"payer_plan": result}

    def coverage(self, parents):
        patients = [r for r in parents["patients"]["patient"] if r["revision_no"] == 1]
        plans = parents["payers"]["payer_plan"]
        stable = [p for p in plans if not p["plan_code"].startswith("RENEWAL")]
        cfg = self.config["coverage"]
        ranked = sorted(patients, key=lambda p: draw(self.seed, p["patient_id"], "coverage-history-rank"))
        renewal = {p["patient_id"]: i for i, p in enumerate(ranked[:cfg["renewal_patients"]])}
        change = {p["patient_id"] for p in ranked[cfg["renewal_patients"]:cfg["renewal_patients"] + cfg["other_change_patients"]]}
        result = []
        for patient in patients:
            pid = patient["patient_id"]
            if pid in renewal:
                code = "RENEWAL-" + str(renewal[pid] % 4 + 1)
                selected = sorted((p for p in plans if p["plan_code"] == code), key=lambda p: p["valid_from"])
                periods = [(OPENING, "2024-01-01T06:00:00Z", OPENING, selected[0]), ("2024-01-01T06:00:00Z", None, "2023-12-15T06:00:00Z", selected[1])]
            else:
                age = age_on(patient["birth_date"], OPENING[:10])
                kind = self.weighted(pid, "primary-payer", cfg["payer_mix_65plus"] if age >= 65 else cfg["payer_mix_under65"])
                pool = [p for p in stable if p["payer_type"] == kind]
                chosen = pool[draw(self.seed, pid, "payer-product", upper=len(pool))]
                periods = [(OPENING, None, OPENING, chosen)]
                if pid in change:
                    effective = f"{2023 + 2 * draw(self.seed, pid, 'coverage-change-year', upper=2)}-{2 + draw(self.seed, pid, 'coverage-change-month', upper=10):02}-01T06:00:00Z"
                    alternatives = [p for p in stable if p["payer_type"] != kind and (p["payer_type"] != "MEDICARE" or age_on(patient["birth_date"], effective[:10]) >= 65)]
                    new = alternatives[draw(self.seed, pid, "new-payer-product", upper=len(alternatives))]
                    periods = [(OPENING, effective, OPENING, chosen), (effective, None, (instant(effective) - timedelta(days=7)).isoformat().replace("+00:00", "Z"), new)]
            for ordinal, (start, end, known, plan) in enumerate(periods):
                identity = stable_id("coverage", pid, ordinal)
                row = self.version("patient_coverage", identity, 1, start, known,
                                   coverage_id=identity, patient_version_id=patient["patient_version_id"], payer_plan_id=plan["payer_plan_id"],
                                   synthetic_member_id=("SP-" if plan["payer_type"] == "SELF_PAY" else "MBR-") + stable_id("member", pid, plan["plan_code"])[-16:].upper(),
                                   coverage_status="SELF_PAY" if plan["payer_type"] == "SELF_PAY" else "ACTIVE")
                row["valid_to"] = end
                result.append(row)
        return {"patient_coverage": result}

    def security(self, parents):
        workers = [r for r in parents["workforce"]["worker_assignment"] if r["revision_no"] == 1 and r["hire_date"] < "2023-01-01"]
        # Read-only synthetic analytics principals; these are not live access grants.
        selected = sorted(workers, key=lambda r: (r["role"] != "ADMIN", draw(self.seed, r["worker_id"], "principal-rank")))[:self.config["security"]["principals"]]
        organizations = parents["organizations"]
        centers = organizations["cost_center"]
        result, grant_index = [], 0
        for worker in selected:
            own_centers = [r for r in centers if r["facility_id"] == worker["facility_id"]][:4]
            scopes = [("FACILITY", worker["facility_id"], "FACILITY_MANAGER"), ("LOCATION", worker["home_location_id"], "UNIT_MANAGER")]
            scopes.extend(("COST_CENTER", r["cost_center_id"], "FINANCE_ANALYST" if i % 2 == 0 else "HR_ANALYST") for i, r in enumerate(own_centers))
            if worker["manager_worker_id"] is None:
                scopes[0] = ("NETWORK", "ALL_NETWORK", "NETWORK_ANALYST")
            for scope_type, scope, role in scopes:
                grant = stable_id("grant", worker["worker_id"], scope_type, scope, role)
                fields = dict(grant_id=grant, principal_id="demo-" + worker["employee_number"], worker_id=worker["worker_id"],
                              role=role, scope_type=scope_type, scope_key=scope, decision="ALLOW")
                changes = []
                if grant_index < self.config["security"]["changed_grants"]:
                    effective = f"2025-{1 + grant_index % 11:02}-01T06:00:00Z"
                    changes = [(effective, effective, {"decision": "REVOKED"})]
                result.extend(self.history("access_scope", grant, fields, changes))
                grant_index += 1
        return {"access_scope": result}

    def mappings(self, parents):
        cfg = self.config["mapping"]
        patient = [p for p in parents["patients"]["patient"] if p["revision_no"] == 1]
        worker = [p for p in parents["workforce"]["worker_assignment"] if p["revision_no"] == 1]
        organizations = parents["organizations"]
        catalog = parents["catalog"]["catalog_item"]
        entries = []
        for row in patient[:cfg["patient"]]:
            entries.append(("LEGACY_EHR", "PATIENT", "LEG-" + row["mrn"], row["patient_id"], OPENING, None))
        for row in worker:
            for namespace in cfg["worker_namespaces"]:
                entries.append((namespace, "WORKER", namespace[:2] + "-" + row["employee_number"], row["worker_id"], row["valid_from"], None))
        for row in organizations["location"]:
            entries.append(("ADT_LOCATION", "LOCATION", row["source_record_id"], row["location_id"], OPENING, None))
        for row in organizations["cost_center"]:
            for namespace in cfg["center_namespaces"]:
                entries.append((namespace, "COST_CENTER", namespace[:2] + "-" + row["cost_center_code"], row["cost_center_id"], OPENING, None))
        for row in catalog[:cfg["catalog"]]:
            entries.append(("TERMINOLOGY_ALIAS", "CATALOG", row["source_record_id"], row["catalog_item_id"], row["valid_from"] + "T00:00:00Z", None))
        for row in parents["payers"]["payer_plan"]:
            entries.append(("AXIOM_PAYER", "PAYER_PLAN", row["source_record_id"], row["payer_plan_id"], row["valid_from"] + "T06:00:00Z", None))
        units = [r for r in organizations["location"] if r["location_type"] in ("DEPARTMENT", "UNIT")]
        for index, row in enumerate(units):
            entries.append(("UNIT_FINANCE", "UNIT_COST_CENTER", row["location_id"], row["cost_center_id"], OPENING,
                            "2024-07-01T05:00:00Z" if index < cfg["unit_association_changes"] else None))
            if index < cfg["unit_association_changes"]:
                center = next(c for c in organizations["cost_center"] if c["facility_id"] == row["facility_id"] and c["cost_center_name"] == "Facilities and Engineering")
                entries.append(("UNIT_FINANCE", "UNIT_COST_CENTER", row["location_id"], center["cost_center_id"], "2024-07-01T05:00:00Z", None))
        result = []
        for namespace, entity, key, target, start, end in entries:
            identity = stable_id("mapping", namespace, entity, key, start)
            row = self.version("source_key_map", identity, 1, start, start,
                               mapping_id=identity, source_namespace=namespace, entity_type=entity, source_key=key, target_key=target, mapping_status="MAPPED")
            row["valid_to"] = end
            result.append(row)
        return {"source_key_map": result}

    def opening_health(self, parents):
        cfg = self.config["opening_health"]
        patients = [r for r in parents["patients"]["patient"] if r["revision_no"] == 1]
        catalog = parents["catalog"]["catalog_item"]
        dx = {r["code"]: r for r in catalog if r["domain"] == "DIAGNOSIS" and r["version"] == "FY2023-OCT"}
        allergens = [r for r in catalog if r["domain"] == "ALLERGEN"]
        minimum_age = cfg["minimum_ages"]
        candidates = []
        for patient in patients:
            age = age_on(patient["birth_date"], "2023-01-01")
            weight = next(weight for band, weight in cfg["age_weights"].items() if int(band.split("-")[0]) <= age <= int(band.split("-")[1]))
            for code in cfg["condition_codes"]:
                if age >= minimum_age[code]:
                    rank = draw(self.seed, patient["patient_id"], "baseline-problem/" + code) // weight
                    candidates.append((rank, patient["patient_id"], code, patient))
        selected = sorted(candidates, key=lambda r: r[:3])[:cfg["problems"]]
        result = []
        for _, _, code, patient in selected:
            identity = stable_id("condition", patient["patient_id"], "opening-problem", code)
            max_years = max(1, min(10, age_on(patient["birth_date"], "2023-01-01") - minimum_age[code] + 1))
            onset = f"{2022 - draw(self.seed, identity, 'onset-years', upper=max_years)}-06-15T05:00:00Z"
            row = self.version("clinical_condition", identity, 1, OPENING, OPENING, condition_id=identity,
                               patient_version_id=patient["patient_version_id"], encounter_version_id=None, catalog_item_id=dx[code]["catalog_item_id"],
                               condition_type="PROBLEM", status="ACTIVE", diagnosis_rank=0, present_on_admission="NOT_APPLICABLE", onset_at=onset,
                               resolved_at=None, reaction=None, severity=self.weighted(identity, "severity", cfg["severity_weights"]))
            result.append(row)
        selected_allergy = sorted(patients, key=lambda p: draw(self.seed, p["patient_id"], "allergy-rank"))[:cfg["allergies"]]
        for patient in selected_allergy:
            identity = stable_id("condition", patient["patient_id"], "opening-allergy")
            allergen = allergens[draw(self.seed, identity, "ingredient", upper=len(allergens))]
            reaction = cfg["allergy_reactions"][draw(self.seed, identity, "reaction", upper=len(cfg["allergy_reactions"]))]
            result.append(self.version("clinical_condition", identity, 1, OPENING, OPENING, condition_id=identity,
                                       patient_version_id=patient["patient_version_id"], encounter_version_id=None,
                                       catalog_item_id=allergen["catalog_item_id"], condition_type="ALLERGY", status="ACTIVE", diagnosis_rank=0,
                                       present_on_admission="NOT_APPLICABLE", onset_at="2021-06-15T05:00:00Z", resolved_at=None,
                                       reaction=reaction, severity="MODERATE" if reaction == "Wheezing" else "MILD"))
        return {"clinical_condition": result}


MASTER_STAGES = {
    "organizations": (), "catalog": (), "patients": (), "workforce": ("organizations",), "payers": (),
    "coverage": ("patients", "payers"), "security": ("organizations", "workforce"),
    "mappings": ("organizations", "patients", "workforce", "catalog", "payers"),
    "opening_health": ("patients", "catalog"),
}
