"""Independent full-schema master validation; no generator or generation arithmetic import."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp lacks UTC offset")
    return parsed


def years(birth, day):
    born, on = date.fromisoformat(birth), date.fromisoformat(day)
    try:
        anniversary = born.replace(year=on.year)
    except ValueError:
        anniversary = date(on.year, 2, 28)
    return on.year - born.year - (on < anniversary)


def contains(row, valid, known, availability=True):
    return (row["valid_from"] <= valid and (row["valid_to"] is None or valid < row["valid_to"])
            and row["known_from"] <= known and (row["known_to"] is None or known < row["known_to"])
            and (not availability or row["export_available_at"] <= known))


def rectangles_overlap(a, b):
    def overlaps(start, end):
        return (a[end] is None or b[start] < a[end]) and (b[end] is None or a[start] < b[end])
    return overlaps("valid_from", "valid_to") and overlaps("known_from", "known_to")


def grouped(rows, field):
    result = defaultdict(list)
    for row in rows:
        result[row[field]].append(row)
    return result


class MasterValidator:
    def __init__(self, tables, schema, config, policy, references):
        self.tables, self.schema, self.cfg, self.policy, self.refs = tables, {t["name"]: t for t in schema["tables"]}, config, policy, references
        self.results, self.metrics = [], {}
        self.indices = {t: {r[spec["primary_key"][0]]: r for r in tables.get(t, [])} for t, spec in self.schema.items()}

    def need(self, condition, key, reason):
        if not condition:
            error = ValueError(reason)
            error.record_key = str(key)
            raise error

    def check(self, name):
        try:
            getattr(self, "check_" + name.lower())()
            return {"rule_id": name, "status": "PASS", "severity": "P0", "scope": "FULL_MASTER_DATA", "failures": []}
        except Exception as exc:
            return {"rule_id": name, "status": "FAIL", "severity": "P0", "scope": "FULL_MASTER_DATA",
                    "failures": [{"record_key": getattr(exc, "record_key", name), "reason": str(exc), "error_type": type(exc).__name__}]}

    def run(self, names=None):
        names = names or [n for n in self.policy["master_checks"] if n != "REVIEW_SAMPLE"]
        self.results = [self.check(n) for n in names]
        failed = [r for r in self.results if r["status"] != "PASS"]
        return {"status": "MASTER_CHECKS_PASSED" if not failed else "BLOCKED", "checks": self.results,
                "metrics": self.metrics, "defects": [{"defect_id": hashlib.sha256((r["rule_id"] + f["record_key"]).encode()).hexdigest()[:32],
                "rule_id": r["rule_id"], "severity": r["severity"], **f} for r in failed for f in r["failures"]],
                "full_dataset_accepted": False, "solution_status": "BLOCKED_FOR_SOLUTION"}

    def check_schema(self):
        self.need(set(self.tables) == set(self.policy["permitted_tables"]), "tables", "master table inventory differs from policy")
        for table, rows in self.tables.items():
            columns = self.schema[table]["columns"]
            names = {c["name"] for c in columns}
            primary = self.schema[table]["primary_key"][0]
            for row in rows:
                key = row.get(primary, "MISSING_KEY")
                self.need(set(row) == names, key, f"full schema column mismatch in {table}")
                for col in columns:
                    value, kind = row[col["name"]], col["type"]
                    self.need(value is not None or col["nullable"], key, f"required {col['name']} is null")
                    if value is None:
                        continue
                    valid = False
                    if kind == "STRING":
                        valid = isinstance(value, str) and bool(value.strip())
                    elif kind == "BOOLEAN":
                        valid = type(value) is bool
                    elif kind in ("INT", "BIGINT"):
                        valid = type(value) is int
                    elif kind == "DATE":
                        valid = isinstance(value, str) and date.fromisoformat(value).isoformat() == value
                    elif kind == "TIMESTAMP":
                        valid = isinstance(value, str) and timestamp(value).utcoffset().total_seconds() == 0
                    elif kind.startswith("DECIMAL"):
                        match = re.fullmatch(r"DECIMAL\((\d+),(\d+)\)", kind)
                        precision, scale = map(int, match.groups())
                        valid = isinstance(value, str) and bool(re.fullmatch(r"-?\d+(?:\.\d+)?", value))
                        if valid:
                            number = Decimal(value)
                            valid = number.is_finite() and len(value.lstrip("-").replace(".", "").lstrip("0")) <= precision and max(0, -number.as_tuple().exponent) <= scale
                    self.need(valid, key, f"wrong type/scale for {col['name']}: {kind}")
                    if col.get("allowed_values"):
                        self.need(value in col["allowed_values"], key, f"unknown discriminator {col['name']}")

    def check_keys(self):
        for table, rows in self.tables.items():
            spec = self.schema[table]
            for columns in [spec["primary_key"], *spec.get("unique_keys", [])]:
                values = [tuple(r[c] for c in columns) for r in rows]
                self.need(len(values) == len(set(values)), table, f"duplicate key {columns}")
            source = [(r["source_system"], r["source_record_id"]) for r in rows]
            self.need(len(source) == len(set(source)), table, "duplicate source version identity")

    def check_references(self):
        for table, rows in self.tables.items():
            for column in self.schema[table]["columns"]:
                if "references" not in column:
                    continue
                target, field = column["references"].split(".")
                keys = {r[field] for r in self.tables.get(target, [])}
                for row in rows:
                    value = row[column["name"]]
                    self.need(value is None or value in keys, row[self.schema[table]["primary_key"][0]], f"orphan {table}.{column['name']} -> {target}.{field}")

    def check_availability(self):
        grace = timestamp(self.cfg["window"]["delivery_grace_end"])
        for table, rows in self.tables.items():
            for row in rows:
                key = row[self.schema[table]["primary_key"][0]]
                self.need(row["source_system"] == self.schema[table]["source_authority"], key, "incorrect source authority")
                recorded, available = timestamp(row["recorded_at"]), timestamp(row["export_available_at"])
                self.need(recorded <= available <= grace, key, "source/export chronology or grace exceeded")
                if "known_from" in row:
                    self.need(row["known_from"] == row["recorded_at"], key, "knowledge backdated relative to source recording")

    def check_rectangles(self):
        identities = {"patient": "patient_id", "worker_assignment": "worker_id", "access_scope": "grant_id",
                      "patient_coverage": "coverage_id", "source_key_map": "mapping_id", "clinical_condition": "condition_id"}
        for table, identity in identities.items():
            for key, versions in grouped(self.tables[table], identity).items():
                for row in versions:
                    self.need(row["valid_to"] is None or timestamp(row["valid_from"]) < timestamp(row["valid_to"]), key, "empty/reversed valid interval")
                    self.need(row["known_to"] is None or timestamp(row["known_from"]) < timestamp(row["known_to"]), key, "empty/reversed knowledge interval")
                for i, left in enumerate(versions):
                    for right in versions[i + 1:]:
                        self.need(not rectangles_overlap(left, right), key, "overlapping bitemporal rectangles")
                self.need(sorted(r["revision_no"] for r in versions) == list(range(1, len(versions) + 1)), key, "noncontiguous history revisions")

    def check_patient_identities(self):
        people = grouped(self.tables["patient"], "patient_id")
        mrns = {}
        for key, rows in people.items():
            self.need(len({r["birth_date"] for r in rows}) == len({r["mrn"] for r in rows}) == 1, key, "identity split across immutable birth/MRN facts")
            row = min(rows, key=lambda r: r["revision_no"])
            self.need(row["mrn"] not in mrns or mrns[row["mrn"]] == key, key, "MRN merged distinct people")
            mrns[row["mrn"]] = key
            self.need(18 <= years(row["birth_date"], "2023-01-01") <= 100, key, "adult eligibility or impossible birth date")
            for revision in rows:
                for field in ("given_name", "family_name"):
                    value = revision[field]
                    self.need(not re.search(r"\d|\b(?:patient|unknown)\b", value, re.I) and len(value) >= 2, key, "placeholder human name")
                email, phone = revision["test_email"], revision["test_phone"]
                self.need(email is None or re.fullmatch(r"[a-z.]+[a-f0-9]{6}@patients\.example", email), key, "contact email outside reserved namespace")
                self.need(phone is None or re.fullmatch(r"\+1-(217|309|815)-555-01\d{2}", phone), key, "phone outside fictional reserved range")
                self.need(revision["deceased_at"] is None or timestamp(revision["deceased_at"]).date() >= date.fromisoformat(revision["birth_date"]), key, "death precedes birth")
        names = Counter((rows[0]["given_name"], rows[0]["family_name"]) for rows in people.values())
        collisions = sum(n > 1 for n in names.values())
        self.need(collisions >= self.policy["thresholds"]["minimum_collision_groups"], "name collisions", "insufficient legitimate name-collision cases")
        self.metrics["patients"] = {"stable_people": len(people), "versions": len(self.tables["patient"]), "name_collision_groups": collisions,
                                    "given_names": len({v[0] for v in names}), "family_names": len({v[1] for v in names})}

    def check_demographics(self):
        first = [r for r in self.tables["patient"] if r["revision_no"] == 1]
        n = len(first)
        actual_ages = Counter()
        for row in first:
            age = years(row["birth_date"], "2023-01-01")
            group = next(g for g in self.cfg["population"]["age_groups"] if int(g.split("-")[0]) <= age <= int(g.split("-")[1]))
            actual_ages[group] += 1
            places = {(r["city"], r["state"], r["postal_code"]) for r in self.cfg["population"]["geography"]}
            self.need((row["city"], row["state_code"], row["postal_code"]) in places, row["patient_id"], "inconsistent city/state/postal area")
        groups = {"age_groups": actual_ages, "administrative_sex": Counter(r["administrative_sex"] for r in first),
                  "race_ethnicity": Counter(r["race_ethnicity"] for r in first), "languages": Counter(r["preferred_language"] for r in first)}
        tolerance = Decimal(self.policy["thresholds"]["demographic_absolute_tolerance"])
        for key, actual in groups.items():
            expected = self.cfg["population"][key]
            self.need(set(actual) <= set(expected), key, "undeclared demographic category")
            for label, weight in expected.items():
                self.need(abs(Decimal(actual[label]) / n - Decimal(weight) / sum(expected.values())) <= tolerance, key + "/" + label, "predeclared demographic band failed")
        addresses = Counter((r["address_line"], r["city"], r["postal_code"]) for r in first)
        self.need(max(addresses.values()) / n <= float(self.policy["thresholds"]["maximum_address_share"]), "addresses", "universal/default address concentration")
        self.need(sum(count > 1 for count in addresses.values()) >= self.policy["thresholds"]["min_shared_addresses"], "addresses", "missing legitimate shared-address cases")
        self.metrics["demographics"] = {key: dict(value) for key, value in groups.items()}
        self.metrics["addresses"] = {"distinct": len(addresses), "shared": sum(v > 1 for v in addresses.values()), "max_people_at_address": max(addresses.values())}

    def check_name_weights(self):
        first = [r for r in self.tables["patient"] if r["revision_no"] == 1]
        source = self.refs["names"]
        expected = defaultdict(Decimal)
        cohorts = Counter((int(r["birth_date"][:4]) // 10 * 10, r["administrative_sex"]) for r in first)
        cross = Decimal(self.cfg["population"]["naming_series_cross_percent"]) / 100
        for (cohort, sex), count in cohorts.items():
            probabilities = {"F": 1 - cross if sex == "F" else (cross if sex == "M" else Decimal(".5")),
                             "M": 1 - cross if sex == "M" else (cross if sex == "F" else Decimal(".5"))}
            for series, probability in probabilities.items():
                pool = source["given_names"][f"{cohort}/{series}"]
                denominator = sum(weight for _, weight in pool)
                for name, weight in pool:
                    expected[name] += Decimal(count) * probability * weight / denominator / len(first)
        observed = Counter(r["given_name"] for r in first)
        def variation(observed, expected, n):
            top = sorted(expected, key=lambda k: (-expected[k], k))[:100]
            distance = sum(abs(Decimal(observed[k]) / n - expected[k]) for k in top)
            distance += abs((1 - sum(Decimal(observed[k]) / n for k in top)) - (1 - sum(expected[k] for k in top)))
            return distance / 2
        given_tv = variation(observed, expected, len(first))
        single_surnames = [r["family_name"] for r in first if "-" not in r["family_name"]]
        denominator = sum(weight for _, weight in source["surnames"])
        marginal = {name: Decimal(weight) / denominator for name, weight in source["surnames"]}
        expected_surname = defaultdict(Decimal)
        categories = Counter(r["race_ethnicity"] for r in first)
        cross_population = Decimal(self.cfg["population"]["surname_population_mix_percent"]) / 100
        for category, count in categories.items():
            pool = source["surname_profiles"].get(category, source["surnames"])
            total = sum(weight for _, weight in pool)
            for name, weight in pool:
                expected_surname[name] += Decimal(count) / len(first) * ((1 - cross_population) * Decimal(weight) / total + cross_population * marginal[name])
        surname_tv = variation(Counter(single_surnames), expected_surname, len(single_surnames))
        limits = self.policy["thresholds"]
        self.need(len(observed) >= limits["min_given_names"] and len({r["family_name"] for r in first}) >= limits["min_surnames"], "name diversity", "insufficient weighted name diversity")
        self.need(given_tv <= Decimal(limits["name_total_variation"]) and surname_tv <= Decimal(limits["name_total_variation"]), "name distribution", "SSA/Census weighted total-variation threshold")
        by_family = grouped(first, "family_name")
        mixed = sum(len({r["race_ethnicity"] for r in rows}) > 1 for rows in by_family.values() if len(rows) >= 5)
        self.need(mixed >= limits["minimum_mixed_race_repeated_surnames"], "names/race", "surname-to-demographic assignment appears deterministic")
        self.metrics["name_weights"] = {"given_top100_other_tv": str(given_tv), "surname_top100_other_tv": str(surname_tv), "mixed_race_repeated_surnames": mixed,
                                       "source_hashes": [s["sha256"] for s in source["sources"]]}

    def check_org_hierarchy(self):
        for table, key, parent in (("cost_center", "cost_center_id", "parent_cost_center_id"), ("location", "location_id", "parent_location_id")):
            rows = self.indices[table]
            for identity, row in rows.items():
                seen, cursor = set(), row
                while cursor[parent] is not None:
                    self.need(cursor[key] not in seen, identity, "hierarchy cycle")
                    seen.add(cursor[key])
                    cursor = rows[cursor[parent]]
                    self.need(cursor["facility_id"] == row["facility_id"], identity, "cross-facility hierarchy")
                self.need(row["active_to"] is None or row["active_from"] < row["active_to"], identity, "reversed active interval")
        beds = [r for r in self.tables["location"] if r["location_type"] == "BED"]
        self.need(len(beds) == 72 and sum(r["service_line"] == "ICU" for r in beds) == 12, "beds", "licensed 72/12 ICU inventory mismatch")
        self.need(all(r["licensed_bed"] == (r["location_type"] == "BED") for r in self.tables["location"]), "bed flags", "nonbed licensed capacity")
        self.need(all(self.indices["cost_center"][r["cost_center_id"]]["facility_id"] == r["facility_id"] for r in self.tables["location"]), "location centers", "cross-facility financial responsibility")
        for facility in self.tables["facility"]:
            site_beds = [r for r in beds if r["facility_id"] == facility["facility_id"]]
            self.need(len(site_beds) == 24 and sum(r["service_line"] == "ICU" for r in site_beds) == 4, facility["facility_id"], "per-facility bed/ICU inventory mismatch")
        self.metrics["organization"] = {"facilities": 3, "centers": 45, "locations": 150, "beds": 72, "icu_beds": 12, "general_beds": 60}

    def check_workforce(self):
        specs = {r["role"]: r for r in self.cfg["workforce"]["roles"]}
        people = grouped(self.tables["worker_assignment"], "worker_id")
        for key, rows in people.items():
            for row in rows:
                spec = specs[row["role"]]
                self.need(years(row["birth_date"], row["hire_date"]) >= 18, key, "worker younger than 18 at hire")
                self.need(row["credential_code"] in spec["credentials"] and row["specialty"] in spec["specialties"], key, "role/credential/specialty mismatch")
                self.need(row["credential_valid_from"] < row["credential_valid_to"], key, "credential validity reversed")
                self.need(row["termination_date"] is None or row["hire_date"] < row["termination_date"], key, "employment end before hire")
                self.need(0 < Decimal(row["fte"]) <= 1 and Decimal(row["hourly_cost_rate"]) > 0, key, "invalid FTE or loaded cost")
                location = self.indices["location"][row["home_location_id"]]
                center = self.indices["cost_center"][row["cost_center_id"]]
                self.need(location["facility_id"] == center["facility_id"] == row["facility_id"], key, "worker home/center facility mismatch")
                self.need(location["location_code"] in self.cfg["workforce"]["specialty_home"][row["specialty"]], key, "specialty incompatible with home service")
            for day in ("2023-01-02", "2024-01-02", "2024-07-02", "2025-01-02", "2025-12-30"):
                valid = day + "T18:00:00Z"
                known = (timestamp(valid) + timedelta(days=1)).isoformat().replace("+00:00", "Z")
                matches = [r for r in rows if contains(r, valid, known)]
                self.need(len(matches) <= 1, key, "overlapping exclusive worker assignments")
                if matches:
                    row = matches[0]
                    if row["hire_date"] <= day and (row["termination_date"] is None or day < row["termination_date"]):
                        self.need(row["credential_valid_from"] <= day < row["credential_valid_to"], key, "expired active worker credential")
        first = [r for r in self.tables["worker_assignment"] if r["revision_no"] == 1]
        roster = [r for r in first if r["role"] in self.cfg["workforce"]["rostered_roles"]]
        self.need(len(people) == 300 and len(roster) == 180, "worker counts", "300 workers/180 roster population mismatch")
        self.need(sum(Decimal(r["fte"]) for r in roster) / len(roster) == Decimal("0.65"), "roster FTE", "roster FTE differs from frozen feasibility baseline")
        self.need(Counter(r["role"] for r in first) == Counter({r["role"]: r["count_per_facility"] * 3 for r in specs.values()}), "worker roles", "configured role counts differ")
        self.metrics["workforce"] = {"stable_workers": len(people), "versions": len(self.tables["worker_assignment"]), "rostered_workers": len(roster),
                                      "opening_roster_mean_fte": str(sum(Decimal(r["fte"]) for r in roster) / len(roster)),
                                      "roles": dict(Counter(r["role"] for r in first)), "types": dict(Counter(r["worker_type"] for r in first)),
                                      "late_hires": sum(r["hire_date"] >= "2023-01-01" for r in first),
                                      "terminated": len({r["worker_id"] for r in self.tables["worker_assignment"] if r["termination_date"]})}

    def check_managers(self):
        workers = grouped(self.tables["worker_assignment"], "worker_id")
        for day in ("2023-01-02", "2024-08-02", "2025-12-30"):
            at, known = day + "T18:00:00Z", day + "T23:00:00Z"
            current = {k: [r for r in rows if contains(r, at, known)] for k, rows in workers.items()}
            for key, versions in current.items():
                if not versions:
                    continue
                cursor, seen = key, set()
                while cursor is not None:
                    self.need(cursor not in seen, key, "manager cycle/self management")
                    seen.add(cursor)
                    self.need(cursor in current and len(current[cursor]) == 1, key, "manager stable identity ambiguous/missing as of time")
                    row = current[cursor][0]
                    self.need(cursor == key or row["termination_date"] is None or day < row["termination_date"], key, "terminated manager")
                    cursor = row["manager_worker_id"]

    def check_coverage(self):
        patients = self.indices["patient"]
        rows = self.tables["patient_coverage"]
        for product, versions in grouped(self.tables["payer_plan"], "plan_code").items():
            for plan in versions:
                self.need(0 < Decimal(plan["allowed_factor"]) <= 1, plan["payer_plan_id"], "invalid contractual reimbursement factor")
                self.need(plan["valid_to"] is None or plan["valid_from"] < plan["valid_to"], plan["payer_plan_id"], "payer contract interval reversed")
            versions = sorted(versions, key=lambda r: r["valid_from"])
            self.need(all(a["valid_to"] is not None and a["valid_to"] <= b["valid_from"] for a, b in zip(versions, versions[1:])), product, "overlapping payer contract versions")
        by_person = defaultdict(list)
        for row in rows:
            patient = patients[row["patient_version_id"]]
            plan = self.indices["payer_plan"][row["payer_plan_id"]]
            by_person[patient["patient_id"]].append(row)
            self.need(row["valid_from"][:10] >= plan["valid_from"] and (plan["valid_to"] is None or row["valid_to"] is not None and row["valid_to"][:10] <= plan["valid_to"]), row["coverage_id"], "coverage outside payer contract validity")
            self.need((row["coverage_status"] == "SELF_PAY") == (plan["payer_type"] == "SELF_PAY"), row["coverage_id"], "implicit/misclassified self pay")
            if plan["payer_type"] == "MEDICARE":
                self.need(years(patient["birth_date"], row["valid_from"][:10]) >= 65, row["coverage_id"], "Medicare under 65 without modeled disability basis")
        self.need(set(by_person) == {r["patient_id"] for r in self.tables["patient"]}, "coverage population", "missing patient primary coverage")
        for key, versions in by_person.items():
            for i, a in enumerate(versions):
                for b in versions[i + 1:]:
                    self.need(not rectangles_overlap(a, b), key, "overlapping primary coverage")
            ordered = sorted(versions, key=lambda r: r["valid_from"])
            self.need(ordered[0]["valid_from"] <= "2023-01-01T06:00:00Z" and ordered[-1]["valid_to"] is None, key, "unexplained coverage boundary gap")
            self.need(all(a["valid_to"] == b["valid_from"] for a, b in zip(ordered, ordered[1:])), key, "coverage gap between enrollments")
        self.metrics["coverage"] = {"patients": len(by_person), "rows": len(rows), "changed_patients": sum(len(v) > 1 for v in by_person.values()), "payer_classes": sorted({r["payer_type"] for r in self.tables["payer_plan"]})}

    def check_catalog(self):
        official = {(r["code_system"], r["code"], r["version"]): r for r in self.refs["codes"]["rows"]}
        local = {(r["code_system"], r["code"], r["version"]): r for r in self.refs["local"]["items"]}
        for row in self.tables["catalog_item"]:
            key = row["catalog_item_id"]
            identity = row["code_system"], row["code"], row["version"]
            ref = official.get(identity) or local.get(identity)
            self.need(ref is not None, key, "unapproved or invented vocabulary code")
            for field in ("display", "valid_from", "valid_to", "domain"):
                self.need(row[field] == ref[field], key, f"reference release differs in {field}")
            if identity in local:
                for field, value in ref.items():
                    if field != "allergen_code":
                        self.need(row[field] == value, key, "local reference attribute differs: " + field)
                if ref.get("allergen_code"):
                    substance = self.indices["catalog_item"].get(row["allergen_catalog_id"])
                    self.need(substance and substance["code"] == ref["allergen_code"], key, "medication points to wrong allergen substance")
            if row["domain"] == "MEDICATION":
                self.need(row["formulation"] and row["strength_unit"] and row["base_unit"] and Decimal(row["strength_per_base_unit"]) > 0 and Decimal(row["pack_to_base_factor"]) > 0, key, "missing medication strength/unit/pack conversion")
                self.need(row["allergen_catalog_id"] in self.indices["catalog_item"] and self.indices["catalog_item"][row["allergen_catalog_id"]]["domain"] == "ALLERGEN", key, "medication allergen family unresolved")
            else:
                self.need(all(row[f] is None for f in ("formulation", "strength_per_base_unit", "strength_unit", "allergen_catalog_id")), key, "medication-only discriminator fields on nonmedication")
            if row["domain"] == "ACCOUNT":
                self.need(row["account_class"] in ("ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE") and row["normal_balance"] in ("DEBIT", "CREDIT") and row["base_unit"] == "USD", key, "account discriminator/unit")
            else:
                self.need(row["account_class"] is None and row["normal_balance"] is None, key, "account-only fields on nonaccount")
        self.need(set(r["domain"] for r in self.tables["catalog_item"]) == {"DIAGNOSIS", "PROCEDURE", "OBSERVATION", "LAB", "MEDICATION", "ALLERGEN", "SUPPLY", "ACCOUNT", "DENIAL"}, "catalog domains", "required catalog domain omitted")
        self.metrics["catalog"] = {"domains": dict(Counter(r["domain"] for r in self.tables["catalog_item"])), "official_rows": len(official), "local_rows": len(local), "releases": sorted({r["version"] for r in official.values()})}

    def check_crosswalks(self):
        target = {"PATIENT": {r["patient_id"] for r in self.tables["patient"]}, "WORKER": {r["worker_id"] for r in self.tables["worker_assignment"]},
                  "LOCATION": set(self.indices["location"]), "COST_CENTER": set(self.indices["cost_center"]), "CATALOG": set(self.indices["catalog_item"]),
                  "PAYER_PLAN": set(self.indices["payer_plan"]), "UNIT_COST_CENTER": set(self.indices["cost_center"])}
        groups = defaultdict(list)
        for row in self.tables["source_key_map"]:
            key = row["mapping_version_id"]
            self.need(row["target_key"] in target[row["entity_type"]] and row["mapping_status"] == "MAPPED", key, "typed crosswalk target missing/unmapped")
            groups[(row["source_namespace"], row["entity_type"], row["source_key"])].append(row)
            if row["entity_type"] == "UNIT_COST_CENTER":
                source = self.indices["location"].get(row["source_key"])
                self.need(source and source["location_type"] in ("DEPARTMENT", "UNIT") and source["facility_id"] == self.indices["cost_center"][row["target_key"]]["facility_id"], key, "unit/finance association is untyped or cross-facility")
        for key, rows in groups.items():
            for i, a in enumerate(rows):
                for b in rows[i + 1:]:
                    self.need(not rectangles_overlap(a, b), key, "source-key mapping ambiguous at valid/known time")
        self.need(set(target) == {r["entity_type"] for r in self.tables["source_key_map"]}, "mapping domains", "unrepresented source mapping domain")
        self.metrics["crosswalks"] = {"rows": len(self.tables["source_key_map"]), "types": dict(Counter(r["entity_type"] for r in self.tables["source_key_map"])), "namespaces": sorted({r["source_namespace"] for r in self.tables["source_key_map"]})}

    def check_access(self):
        workers = grouped(self.tables["worker_assignment"], "worker_id")
        targets = {"NETWORK": {"ALL_NETWORK"}, "FACILITY": set(self.indices["facility"]), "LOCATION": set(self.indices["location"]), "COST_CENTER": set(self.indices["cost_center"])}
        revoked, allowed = 0, 0
        for row in self.tables["access_scope"]:
            key = row["access_scope_id"]
            self.need(row["worker_id"] in workers and row["scope_key"] in targets[row["scope_type"]], key, "access typed scope/worker missing")
            if contains(row, "2025-12-30T18:00:00Z", "2025-12-31T18:00:00Z"):
                if row["decision"] == "REVOKED":
                    revoked += 1
                else:
                    allowed += 1
        self.need(revoked > 0 and allowed > 0, "access lifecycles", "revocation/remaining active grant cases missing")
        self.metrics["access"] = {"current_revoked": revoked, "current_allowed": allowed, "rows": len(self.tables["access_scope"])}

    def check_opening_health(self):
        problems, allergies = 0, 0
        affected = set()
        for row in self.tables["clinical_condition"]:
            key = row["condition_version_id"]
            patient = self.indices["patient"][row["patient_version_id"]]
            item = self.indices["catalog_item"][row["catalog_item_id"]]
            affected.add(patient["patient_id"])
            self.need(row["encounter_version_id"] is None and row["diagnosis_rank"] == 0 and row["present_on_admission"] == "NOT_APPLICABLE", key, "opening assertion fabricated encounter/diagnosis")
            self.need(row["condition_type"] in ("PROBLEM", "ALLERGY") and row["status"] == "ACTIVE", key, "opening condition discriminator")
            self.need(row["onset_at"] is not None and patient["birth_date"] <= row["onset_at"][:10] <= row["known_from"][:10] <= "2023-01-01", key, "opening onset/knowledge chronology")
            self.need(item["valid_from"] <= row["valid_from"][:10] and (item["valid_to"] is None or row["valid_from"][:10] < item["valid_to"]), key, "opening assertion code release not valid")
            if row["condition_type"] == "ALLERGY":
                allergies += 1
                self.need(item["domain"] == "ALLERGEN" and row["reaction"], key, "missing typed allergy substance/reaction")
            else:
                problems += 1
                self.need(item["domain"] == "DIAGNOSIS" and row["reaction"] is None, key, "problem uses wrong domain/allergy field")
        self.need(problems == self.cfg["opening_health"]["problems"] and allergies == self.cfg["opening_health"]["allergies"], "opening health", "opening-context counts differ from reserved budget")
        self.metrics["opening_health"] = {"problems": problems, "allergies": allergies, "patients_with_assertions": len(affected), "absence_semantics": "Unasserted conditions are unknown/out of scope, not confirmed absence"}

    def check_asof(self):
        examined = 0
        for table, identity in (("patient", "patient_id"), ("worker_assignment", "worker_id")):
            for key, rows in grouped(self.tables[table], identity).items():
                if len(rows) < 3:
                    continue
                first = min(rows, key=lambda r: r["revision_no"])
                closed = next(r for r in rows if r["revision_no"] == 2)
                new = next(r for r in rows if r["revision_no"] == 3)
                valid = new["valid_from"]
                before = (timestamp(new["known_from"]) - timedelta(seconds=1)).isoformat().replace("+00:00", "Z")
                after = (timestamp(new["export_available_at"]) + timedelta(seconds=1)).isoformat().replace("+00:00", "Z")
                previous = [r for r in rows if contains(r, valid, before)]
                current = [r for r in rows if contains(r, valid, after)]
                self.need(len(previous) == 1 and previous[0] is first and len(current) == 1 and current[0] is new, key, "retroactive/as-of history does not resolve old/new intended version")
                earlier = (timestamp(valid) - timedelta(seconds=1)).isoformat().replace("+00:00", "Z")
                old_slice = [r for r in rows if contains(r, earlier, after)]
                self.need(len(old_slice) == 1 and old_slice[0] is closed, key, "historical business segment not preserved")
                examined += 1
        self.need(examined >= 1000, "as-of probes", "insufficient effective/knowledge boundary probes")
        self.metrics["asof"] = {"changed_identities_probed": examined, "probes_per_identity": 3}

    def check_budget(self):
        actual = {table: len(rows) for table, rows in self.tables.items()}
        self.need(actual == self.cfg["budgets"] == self.policy["exact_budgets"], "master budgets", "master row budget differs, including versions/opening context")
        self.need(sum(actual.values()) == self.policy["expected_rows"] < 2_000_000, "master total", "master/whole-release volume exceeded")
        self.need(all(n <= self.schema[t]["planned_rows"] for t, n in actual.items()) and len(self.schema) == 25, "release boundary", "master domain consumes unbudgeted rows or extra business tables")
        self.metrics["budget"] = {"generated_master_rows": sum(actual.values()), "rows_by_table": actual,
                                  "frozen_release_rows": 1958210, "remaining_planned_rows": 1958210 - sum(actual.values()), "release_cap_reserve": 41790}
