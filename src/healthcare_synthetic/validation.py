"""Independent microfixture checks and projected-candidate checks.

No generation helpers are imported here. These checks exercise rule families;
they do not certify the full Phase 0 schema or a later healthcare data release.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, datetime
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext
from functools import wraps
from importlib import resources
from io import BytesIO
from zoneinfo import ZoneInfo

RULES = {}


def exact_context(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        with localcontext(Context(prec=38, rounding=ROUND_HALF_UP)):
            return fn(*args, **kwargs)
    return wrapped


def facility_date(value):
    # Independent time-zone loading; no call to generator temporal utilities.
    zone_bytes = resources.files("tzdata").joinpath("zoneinfo/America/Chicago").read_bytes()
    zone = ZoneInfo.from_file(BytesIO(zone_bytes), key="America/Chicago")
    return dt(value).astimezone(zone).date()


def rule(name):
    def register(fn):
        RULES[name] = fn
        return fn
    return register


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def dt(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.tzinfo is not None, "timestamp requires offset")
    return result


def dec(value):
    require(isinstance(value, (str, int)) and not isinstance(value, bool), "exact decimal required")
    number = Decimal(value)
    require(number.is_finite(), "finite decimal required")
    return number


def cents(value):
    return value.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)


def inside(row, valid, known):
    return (dt(row["valid_from"]) <= dt(valid)
            and (row["valid_to"] is None or dt(valid) < dt(row["valid_to"]))
            and dt(row["known_from"]) <= dt(known)
            and (row["known_to"] is None or dt(known) < dt(row["known_to"])))


def no_overlap(rows, group, start, end):
    for i, left in enumerate(rows):
        for right in rows[i + 1:]:
            if left[group] == right[group]:
                require(dt(left[end]) <= dt(right[start]) or dt(right[end]) <= dt(left[start]),
                        f"overlap {left['key']} / {right['key']}")


@rule("ID01")
def identity(x):
    keys = [r["key"] for r in x["rows"]]
    require(all(isinstance(k, str) and k for k in keys), "missing or wrong-type key")
    require(len(keys) == len(set(keys)), "duplicate primary key")
    for row in x["rows"]:
        require(isinstance(row["name"], str) and row["name"].strip(), "required scalar name")


@rule("ID02")
def references(x):
    for row in x["rows"]:
        require(row["parent"] in x["parents"], f"orphan reference {row['key']}")


@rule("TM01")
def rectangles(x):
    for row in x["rows"]:
        for start, end in (("valid_from", "valid_to"), ("known_from", "known_to")):
            require(row[end] is None or dt(row[start]) < dt(row[end]), "empty temporal interval")
    for i, a in enumerate(x["rows"]):
        for b in x["rows"][i + 1:]:
            if a["person"] == b["person"]:
                overlaps = []
                for start, end in (("valid_from", "valid_to"), ("known_from", "known_to")):
                    overlaps.append((a[end] is None or dt(b[start]) < dt(a[end]))
                                    and (b[end] is None or dt(a[start]) < dt(b[end])))
                require(not all(overlaps), "overlapping business/knowledge rectangles")


@rule("TM02")
def availability(x):
    for row in x["rows"]:
        require(dt(row["recorded"]) <= dt(row["available"]), "export before source recording")
        if row["selected"]:
            require(max(dt(row["recorded"]), dt(row["available"]), dt(row["known"])) <= dt(x["as_of"]),
                    "future fact in as-of projection")


@rule("TM03")
def lifecycle_knowledge(x):
    for row in x["rows"]:
        require(row["outcome_at"] is None or dt(row["outcome_at"]) <= dt(row["known_from"]),
                "outcome leaked into earlier lifecycle version")


@rule("NM01")
def names(x):
    import re
    for row in x["rows"]:
        require(isinstance(row["name"], str) and len(row["name"].split()) >= 2
                and not re.search(r"\d|\b(?:patient|worker|test|unknown)\b", row["name"], re.I),
                "placeholder human name")


@rule("NM02")
def ages(x):
    for row in x["rows"]:
        birth, day = date.fromisoformat(row["dob"]), date.fromisoformat(row["service_date"])
        try:
            anniversary = birth.replace(year=day.year)
        except ValueError:
            anniversary = date(day.year, 2, 28)
        years = day.year - birth.year - (day < anniversary)
        require(years == row["age"] and 18 <= years <= 110, "age at local service date")
        require(row["email"].endswith("@example.invalid"), "contact outside test namespace")


@rule("OR01")
def organization(x):
    nodes = {r["key"]: r for r in x["rows"]}
    require(len(nodes) == len(x["rows"]), "duplicate location")
    for row in nodes.values():
        seen, cursor = set(), row
        while cursor["parent"] is not None:
            require(cursor["key"] not in seen, "hierarchy cycle")
            seen.add(cursor["key"])
            cursor = nodes[cursor["parent"]]
            require(cursor["facility"] == row["facility"], "cross-facility hierarchy")
    beds = [r for r in nodes.values() if r["type"] == "BED"]
    require(Counter(r["capability"] for r in beds) == Counter(x["expected_beds"]), "bed inventory mismatch")
    require(set(r["key"] for r in beds) == set(x["opening_beds"]), "missing opening bed state")


@rule("WK01")
def worker(x):
    matches = [r for r in x["assignments"] if inside(r, x["start"], x["as_of"])]
    require(len(matches) == 1, "worker assignment not unique as of both times")
    a = matches[0]
    require(a["role"] == x["role"] and dt(a["credential_end"]) >= dt(x["end"]), "ineligible credential/role")
    require(dec(a["rate"]) == dec(x["applied_rate"]), "retroactive rate selected with hindsight")


@rule("WK02")
def manager(x):
    rows = {r["key"]: r["manager"] for r in x["rows"]}
    for key in rows:
        seen, cursor = set(), key
        while cursor is not None:
            require(cursor in rows, "missing manager stable identity")
            require(cursor not in seen, "self management or manager cycle")
            seen.add(cursor)
            cursor = rows[cursor]


@rule("AC01")
def access(x):
    for row in x["rows"]:
        require(row["scope"] in x["targets"][row["scope_type"]], "wrong scope discriminator/key")
        require(not (row["decision"] == "REVOKE" and row["read_allowed"]), "revocation did not deny")


@rule("CV01")
def coverage(x):
    no_overlap(x["enrollments"], "patient", "start", "end")
    require(x["claim_patient"] == x["coverage_patient"] == x["encounter_patient"], "coverage patient mismatch")
    require(x["payer"] != "" and (x["insured"] or x["payer"] == "SELF_PAY"), "missing self-pay classification")


@rule("CD01")
def codes(x):
    require(x["actual_domain"] == x["required_domain"] and x["actual_unit"] == x["required_unit"], "code domain/unit")
    matches = [r for r in x["versions"] if r["start"] <= x["service_date"] < r["end"]
               and dt(r["published"]) <= dt(x["as_of"])]
    require(len(matches) == 1 and matches[0]["key"] == x["selected_version"], "wrong effective code release")


@rule("CD02")
def catalog_types(x):
    for row in x["rows"]:
        if row["domain"] == "MEDICATION":
            require(dec(row["strength"]) > 0 and dec(row["base_conversion"]) > 0 and row["unit"], "medication conversion missing")
        elif row["domain"] == "ACCOUNT":
            require(row["class"] in ("ASSET", "LIABILITY", "REVENUE", "EXPENSE", "EQUITY")
                    and row["normal"] in ("DEBIT", "CREDIT"), "invalid account discriminator")
        else:
            require(row["domain"] in x["allowed_domains"], "unknown catalog domain")


@rule("EN01")
def episode(x):
    rows = {r["key"]: r for r in x["rows"]}
    for row in rows.values():
        seen, cursor = set(), row
        while cursor["prior"] is not None:
            require(cursor["key"] not in seen, "encounter cycle")
            seen.add(cursor["key"])
            cursor = rows[cursor["prior"]]
            require(row["patient"] == cursor["patient"], "linked episode patient mismatch")
    require(len(rows) == x["visit_count"], "bed transfer created an extra visit")


@rule("EN02")
def chronology(x):
    for row in x["rows"]:
        values = [dt(row[k]) for k in ("arrival", "decision", "admit", "discharge") if row[k] is not None]
        require(values == sorted(values), "encounter chronology")
        require((row["status"] == "OPEN") == (row["discharge"] is None), "open/discharge censoring")


@rule("EN03")
def death_cutoff(x):
    for row in x["rows"]:
        if row["domain"] == "CARE":
            require(x["death"] is None or dt(row["at"]) <= dt(x["death"]), "care after death")
            require(dt(row["at"]) <= dt(x["cutoff"]), "future care outcome")


@rule("CN01")
def condition(x):
    for row in x["rows"]:
        if row["type"] == "DIAGNOSIS":
            require(row["encounter"] is not None and row["rank"] >= 1, "diagnosis requires encounter/rank")
        else:
            require(row["type"] in ("PROBLEM", "ALLERGY") and row["rank"] == 0, "condition family/rank")
            if row["type"] == "ALLERGY":
                require(row["substance"] and row["reaction"], "allergy substance/reaction")


@rule("CN02")
def diagnosis_coverage(x):
    for row in x["rows"]:
        if row["status"] == "COMPLETE" and row["assessed"]:
            require(row["primary_count"] == 1 or row["uncertainty_reviewed"], "assessed encounter lacks diagnosis")


@rule("CE01")
def clinical_types(x):
    for row in x["rows"]:
        require(row["type"] in x["matrix"], "unknown clinical event type")
        spec = x["matrix"][row["type"]]
        require(all(row.get(f) is not None for f in spec["required"]), "missing event-specific scalar")
        require(all(row.get(f) is None for f in spec["forbidden"]), "fabricated field for event type")
        require(not any(isinstance(v, (list, dict)) for v in row.values()), "uncounted nested facts")


@rule("CE02")
def medication(x):
    for row in x["rows"]:
        require(dt(row["order_at"]) <= dt(row["at"]), "administration before order")
        require(row["route"] in x["allowed_routes"] and dec(x["min_dose"]) <= dec(row["dose"]) <= dec(x["max_dose"]), "pathway dose/route")
        require(row["substance"] not in x["active_allergens"], "active drug allergy conflict")


@rule("CE03")
def notes(x):
    for assertion in x["assertions"]:
        require(assertion["fact_key"] in x["facts"], "note assertion lacks structured fact")
        fact = x["facts"][assertion["fact_key"]]
        require(dt(fact["known"]) <= dt(x["authored"])
                and assertion["polarity"] == fact["polarity"], "note hindsight or lost negation")


@rule("AP01")
def appointment(x):
    require(dt(x["booked"]) < dt(x["end"]), "appointment booking chronology")
    if x["status"] == "NO_SHOW":
        require(dt(x["known"]) >= dt(x["end"]), "premature no-show")
    if x["status"] == "RESCHEDULED":
        require(x["replacement"] in x["retained_slots"], "lost replacement history")


@rule("BD01")
def beds(x):
    no_overlap(x["rows"], "bed", "start", "end")
    no_overlap(x["rows"], "patient", "start", "end")
    for row in x["rows"]:
        require(row["clean"] and row["service"] == "OPEN" and row["required"] == row["capability"], "incompatible/unclean/closed bed")


@rule("BD02")
def bed_states(x):
    states = {}
    for row in sorted(x["rows"], key=lambda r: (r["effective"], r["sequence"])):
        prior = states.get(row["bed"])
        require((row["occupancy"] == "OCCUPIED") == (row["patient"] is not None), "occupant/post-state mismatch")
        require(not (row["service"] == "CLOSED" and row["patient"] is not None), "occupied closure")
        require(prior is None or row["sequence"] > prior["sequence"], "bed sequence not increasing")
        states[row["bed"]] = row
    require(states == x["expected_current"], "correction projection differs from expected current state")


@rule("BD03")
def census(x):
    require(x["opening"] + x["admissions"] + x["transfer_in"] - x["discharges"] - x["transfer_out"] == x["closing"], "census roll-forward")


@rule("BD04")
def occupied_seconds(x):
    total = 0
    start, end = dt(x["window_start"]), dt(x["window_end"])
    for row in x["intervals"]:
        total += max(0, int((min(end, dt(row["end"])) - max(start, dt(row["start"]))).total_seconds()))
    require(total == x["event_integral_seconds"], "event integral differs from clipped intervals")


@rule("BD05")
def unmet_capacity(x):
    require(set(x["arrivals"]) == set(x["placed"]) | set(x["waiting"]) | set(x["diverted"]), "dropped demand")
    require(not (set(x["placed"]) & (set(x["waiting"]) | set(x["diverted"]))), "demand disposition duplicated")


@rule("SF01")
def staff_hours(x):
    no_overlap(x["rows"], "worker", "start", "end")
    for row in x["rows"]:
        components = [dec(row[k]) for k in ("productive", "nonproductive", "break")]
        require(all(v >= 0 for v in components), "negative staff component")
        actual = Decimal(str((dt(row["end"]) - dt(row["start"])).total_seconds())) / 3600
        require(actual == dec(row["worked"]) == sum(components), "elapsed/worked/component hours disagree")
        require(0 <= dec(row["overtime"]) <= sum(components[:2]), "overtime exceeds paid hours")


@rule("SF02")
def staffing_demand(x):
    required = sum(dec(r["patient_days"]) * dec(r["hours_per_day"]) for r in x["acuity_groups"])
    require(dec(x["productive_hours"]) + dec(x["shortage_hours"]) >= required, "unexplained staffing shortage")


@rule("IV01")
def inventory(x):
    balance = dec(x["opening"])
    transfers = defaultdict(Decimal)
    for row in x["movements"]:
        balance += dec(row["qty"])
        if row["transfer"] is not None:
            transfers[row["transfer"]] += dec(row["qty"])
    require(balance == dec(x["closing"]), "stock roll-forward")
    require(all(v == 0 for v in transfers.values()), "unpaired stock transfer")


@rule("IV02")
def consumption(x):
    used = sum(dec(r["dose"]) * dec(r["conversion"]) for r in x["administrations"] if r["status"] == "COMPLETE")
    require(used + dec(x["waste"]) == -sum(map(dec, x["stock_consumptions"])), "dose/base-unit consumption mismatch")


@rule("IV03")
def lot_valuation(x):
    for row in x["rows"]:
        require(row["received"] <= row["issued"] < row["expires"], "lot issued before arrival/after expiry")
        require(cents(dec(row["qty"]) * dec(row["unit_cost"])) == dec(row["extended"]), "lot valuation rounding")


@rule("CH01")
def charges(x):
    for row in x["rows"]:
        require(row["service_status"] == "COMPLETE" or row["room_day_predicate"], "unperformed charge provenance")
        require(cents(dec(row["units"]) * dec(row["price"])) == dec(row["billed"]), "charge arithmetic")


@rule("CL01")
def claim_lines(x):
    require(sum(dec(r["amount"]) for r in x["lines"]) == dec(x["billed"]), "claim original header/line sum")
    charge_keys = [r["charge"] for r in x["lines"]]
    require(len(charge_keys) == len(set(charge_keys)), "charge billed in multiple original lines")
    require(all(r["patient"] == x["patient"] for r in x["lines"]), "claim line patient mismatch")


@rule("CL02")
def claim_state(x):
    allowed = {"NEW": {"SUBMITTED"}, "SUBMITTED": {"DENIED", "PARTIAL", "PAID"},
               "DENIED": {"RESUBMITTED", "APPEALED"}, "RESUBMITTED": {"PAID", "DENIED"},
               "APPEALED": {"PAID", "DENIED"}, "PARTIAL": {"PAID", "REFUNDED", "PARTIAL"},
               "PAID": {"REFUNDED"}, "REFUNDED": {"PARTIAL", "PAID"}}
    state = x["initial"]
    for row in x["events"]:
        if row["state"] == "OPENING":
            require(state == "NEW" and dec(row["ar_delta"]) == 0, "opening counted as new submission")
            state = row["opening_state"]
        else:
            require(row["state"] in allowed[state], "invalid claim transition")
            state = row["state"]
        require(row["claim"] == x["claim"], "resubmission created a new original claim")


@rule("CL03")
def receivables(x):
    ar, cash = dec(x["opening_ar"]), dec(x["opening_cash"])
    seen = {}
    for row in x["events"]:
        ar += dec(row["ar_delta"])
        cash += dec(row["cash_delta"])
        if dec(row["cash_delta"]) < 0:
            require(row["reverses"] in seen and -dec(row["cash_delta"]) <= dec(seen[row["reverses"]]["cash_delta"]), "unlinked/excess refund")
        if row["type"] == "RECLASS":
            require(dec(row["cash_delta"]) == 0 and dec(row["revenue_delta"]) == 0, "reclassification fabricated cash/revenue")
        seen[row["key"]] = row
    require(ar == dec(x["closing_ar"]) and cash == dec(x["closing_cash"]), "AR/cash roll-forward")


@rule("CL04")
def denials(x):
    require(dt(x["evidence_known"]) <= dt(x["decision"]), "denial evidence from future")
    require(not (x["appeal_state"] == "OPEN" and dec(x["final_loss"]) != 0), "open appeal treated as final loss")


@rule("GL01")
def journals(x):
    totals = defaultdict(lambda: [Decimal(0), Decimal(0)])
    for row in x["lines"]:
        debit, credit = dec(row["debit"]), dec(row["credit"])
        require(debit >= 0 and credit >= 0 and ((debit > 0) != (credit > 0)), "one positive journal side required")
        require(row["account_domain"] == "ACCOUNT", "non-account journal code")
        key = (row["entity"], row["currency"], row["date"], row["journal"])
        totals[key][0] += debit
        totals[key][1] += credit
    require(all(d == c for d, c in totals.values()), "unbalanced entity/currency/date/journal")


@rule("GL02")
def source_journals(x):
    require(set(x["source_totals"]) == set(x["journal_totals"]), "missing source journal group")
    for key, value in x["source_totals"].items():
        require(dec(value) == dec(x["journal_totals"][key]), f"source journal mismatch {key}")


@rule("GL03")
def stock_accounting(x):
    require(dec(x["receipt_expense"]) == 0, "purchase expensed before consumption")
    require(dec(x["receipt_asset"]) == dec(x["receipt_ap"]), "receipt asset/AP mismatch")
    require(dec(x["consume_expense"]) == -dec(x["consume_asset"]), "consumption expense/asset mismatch")


@rule("CO01")
def costs(x):
    require(sum(dec(r["amount"]) for r in x["allocations"]) == dec(x["pool"]), "cost pool not conserved")
    require(sum(dec(r["share"]) for r in x["allocations"]) == 1, "allocation shares not one")
    require(dec(x["gl_after"]) == dec(x["gl_before"]), "analytical allocation duplicated GL expense")


@rule("CO02")
def destinations(x):
    current = {r["run"] for r in x["rows"] if r["selected"]}
    require(len(current) == 1, "multiple or missing selected cost runs")
    for row in x["rows"]:
        require(row["destination"] in ("PATIENT", "NONPATIENT", "RESIDUAL"), "unknown cost destination")
        require((row["destination"] == "PATIENT") == (row["encounter"] is not None), "wrong cost destination/encounter")


@rule("AX01")
def axiom_actual(x):
    for row in x["rows"]:
        value = dec(row["movement"]) + (dec(row["opening"]) if row["class"] in ("ASSET", "LIABILITY", "EQUITY") else 0)
        require(value == dec(row["axiom"]), f"Axiom account/center/month mismatch {row['key']}")


@rule("AX02")
def axiom_grain(x):
    seen = set()
    for row in x["rows"]:
        require(date.fromisoformat(row["month"]).day == 1, "Axiom month must be first day")
        key = (row["center"], row["measure"], row["month"], row["scenario"])
        if row["selected"]:
            require(key not in seen, "multiple selected vintages")
            seen.add(key)
        if row["measure"] == "MONEY":
            require(row["account"] and row["amount"] is not None and row["quantity"] is None and row["unit"] == "USD", "monetary grain/unit")
        else:
            require(row["amount"] is None and row["quantity"] is not None and row["unit"] != "USD", "statistical grain/unit")


@rule("AX03")
def forecast_availability(x):
    require(all(dt(t) <= dt(x["published"]) for t in x["input_known"]), "future information in forecast vintage")


@rule("SR01")
def round_trip(x):
    require(x["expected_rows"] == len(x["parsed"]), "export row count")
    require(sorted(x["canonical"], key=lambda r: r["key"]) == sorted(x["parsed"], key=lambda r: r["key"]), "round trip scope/values")
    require(sum(dec(r["amount"]) for r in x["parsed"]) == dec(x["expected_total"]), "export control total")


@rule("SR02")
def crosswalk(x):
    for row in x["rows"]:
        matches = [m for m in x["mappings"] if m["source"] == row["source"] and m["namespace"] == row["namespace"] and inside(m, row["valid_at"], row["as_of"])]
        require(len(matches) == 1 and matches[0]["target"] in x["typed_targets"][row["entity"]], "unmapped/ambiguous/incorrectly typed key")


@rule("SR03")
def replay(x):
    require(x["first_state"] == x["repeated_state"] == x["independent_expected"], "replay altered economic/current state")


@rule("DR01")
def daily_drivers(x):
    pairs = [(r["facility"], r["date"]) for r in x["rows"]]
    start, end = date.fromisoformat(x["start"]), date.fromisoformat(x["end"])
    expected = {(f, date.fromordinal(d).isoformat()) for f in x["facilities"] for d in range(start.toordinal(), end.toordinal() + 1)}
    require(set(pairs) == expected and len(pairs) == len(expected), "driver facility/date coverage")
    for row in x["rows"]:
        require(dt(row["calendar_known"]) <= dt(row["observations_known"]), "realized driver knowledge chronology")


@rule("RS01")
def realism_band(x):
    require(x["denominator"] >= x["minimum_sample"], "insufficient realism denominator requires review")
    rate = dec(x["numerator"]) / dec(x["denominator"])
    require(dec(x["lower"]) <= rate <= dec(x["upper"]), "preregistered realism band")


@rule("RS02")
def connected_scenarios(x):
    require(x["observed_cases"] >= x["minimum_cases"], "missing connected scenario cases")
    require(set(x["required_domains"]) <= set(x["linked_domains"]), "scenario missing downstream effects")
    require(not (set(x["feature_columns"]) & {"scenario_id", "expected_outcome", "fault_label"}), "scenario labels leaked to business features")


@rule("CP01")
def volume(x):
    require(20 <= x["table_count"] <= 25, "business table boundary")
    require(sum(x["rows_by_table"].values()) <= 2_000_000, "canonical business record ceiling")
    require(x["counted_versions"] == x["all_versions"], "uncounted business histories")


@rule("RP01")
def rebuild(x):
    require(x["locked_inputs"] == x["rebuild_inputs"] and x["first_hash"] == x["rebuild_hash"], "clean rebuild/input lock mismatch")


@rule("FN01")
def independent_grains(x):
    expected = {k: sum(dec(r["amount"]) for r in x["facts"] if r["encounter"] == k) for k in x["target_encounters"]}
    require(set(expected) == set(x["reported"]), "fact reporting scope mismatch")
    require(all(v == dec(x["reported"][k]) for k, v in expected.items()), "join multiplied independent facts")


@exact_context
def execute(rule_id, data, severity="P0", key=None):
    """Unknown checks, missing columns and detector exceptions fail closed."""
    key = key or data.get("case_key", "UNSPECIFIED")
    try:
        require(rule_id in RULES, "unknown validation rule")
        RULES[rule_id](data)
        return {"rule_id": rule_id, "severity": severity, "scope": "DEVELOPMENT_MICROFIXTURE",
                "status": "PASS", "failures": []}
    except Exception as exc:
        return {"rule_id": rule_id, "severity": severity, "scope": "DEVELOPMENT_MICROFIXTURE",
                "status": "FAIL", "failures": [{"record_key": key, "reason": str(exc), "error_type": type(exc).__name__}]}


def gate(results):
    require(bool(results), "empty validation evidence cannot pass")
    require(all(r["severity"] in ("P0", "P1", "P2") and r["status"] in ("PASS", "FAIL") for r in results), "unknown severity/status cannot pass")
    blockers = [r for r in results if r["status"] != "PASS" and r["severity"] in ("P0", "P1")]
    return {"status": "BLOCKED" if blockers else "FIXTURES_PASSED",
            "blocking_rules": sorted(set(r["rule_id"] for r in blockers)),
            "dataset_accepted": False, "solution_status": "BLOCKED_FOR_SOLUTION"}


def defects(results):
    rows = []
    for result in results:
        for failure in result["failures"]:
            key = [result["rule_id"], failure["record_key"]]
            defect_id = hashlib.sha256(json.dumps(key, separators=(",", ":")).encode()).hexdigest()[:32]
            rows.append({"defect_id": defect_id, "rule_id": result["rule_id"], "severity": result["severity"],
                         "record_key": failure["record_key"], "reason": failure["reason"], "status": "OPEN"})
    return rows


def profile(tables):
    result = {}
    for table, rows in sorted(tables.items()):
        columns = sorted(set().union(*(r.keys() for r in rows))) if rows else []
        result[table] = {"rows": len(rows), "columns": {}}
        for col in columns:
            values = [r.get(col) for r in rows]
            nonnull = [v for v in values if v is not None]
            result[table]["columns"][col] = {
                "nulls": len(values) - len(nonnull),
                "distinct": len({json.dumps(v, sort_keys=True) for v in nonnull}),
                "min": min(nonnull) if nonnull else None, "max": max(nonnull) if nonnull else None}
    return result


@exact_context
def validate_candidate(tables, expectations):
    """Validate the small declared projection, never bypass the full release schema."""
    results = []

    def capture(name, fn):
        try:
            fn()
            results.append({"rule_id": name, "severity": "P0", "scope": "DEVELOPMENT_PROJECTION", "status": "PASS", "failures": []})
        except Exception as exc:
            results.append({"rule_id": name, "severity": "P0", "scope": "DEVELOPMENT_PROJECTION", "status": "FAIL",
                            "failures": [{"record_key": getattr(exc, "record_key", name), "reason": str(exc), "error_type": type(exc).__name__}]})

    def keyed(condition, key, reason):
        if not condition:
            error = ValueError(reason)
            error.record_key = key
            raise error

    def shape():
        require(set(tables) == set(expectations["projection"]), "missing/extra fixture table")
        for table, spec in expectations["projection"].items():
            rows = tables[table]
            require(len(rows) == spec["rows"], f"fixture count mismatch {table}")
            keys = []
            for row in rows:
                key = row.get("key", f"{table}:missing-key")
                keyed(set(row) == set(spec["fields"]), key, f"wrong fixture projection {table}")
                keyed(isinstance(key, str) and bool(key), key, "invalid fixture key")
                keyed(not any(isinstance(v, (list, dict, float)) for v in row.values()), key, "non-scalar/float fixture")
                keys.append(key)
            require(len(set(keys)) == len(keys), f"duplicate fixture key {table}")
    capture("P1_SHAPE", shape)

    def people():
        for r in tables["patient"]:
            dob, day = date.fromisoformat(r["dob"]), date.fromisoformat(r["service_date"])
            try:
                anniversary = dob.replace(year=day.year)
            except ValueError:
                anniversary = date(day.year, 2, 28)
            actual = day.year - dob.year - (day < anniversary)
            keyed(actual == r["age"] and actual >= 18, r["key"], "calendar age")
            keyed(r["name"] in expectations["names"] and r["email"].endswith("@example.invalid"), r["key"], "fixture identity/contact")
    capture("P1_IDENTITIES", people)

    def visits():
        patients = {r["key"] for r in tables["patient"]}
        encounters = {r["key"]: r for r in tables["encounter"]}
        for r in encounters.values():
            keyed(r["patient"] in patients, r["key"], "orphan patient")
            keyed(dt(r["start"]) <= dt(r["end"]), r["key"], "encounter chronology")
            keyed(date(2023, 1, 1) <= facility_date(r["start"]) <= facility_date(r["end"]) <= date(2025, 12, 31),
                  r["key"], "care outside frozen local business window; delivery grace cannot add care")
            if r["prior"]:
                prior = encounters[r["prior"]]
                keyed(r["patient"] == prior["patient"] and dt(prior["end"]) <= dt(r["start"]), r["key"], "linked ED/IPD episode")
        for r in tables["clinical_event"]:
            e = encounters[r["encounter"]]
            keyed(dt(e["start"]) <= dt(r["at"]) <= dt(e["end"]), r["key"], "care outside encounter")
            keyed(r["unit"] == expectations["observation_unit"] and dec(r["value"]) >= dec(expectations["observation_min"])
                  and dec(r["value"]) <= dec(expectations["observation_max"]), r["key"], "configured observation/unit range")
    capture("P1_CHRONOLOGY", visits)

    def links():
        patients = {r["key"] for r in tables["patient"]}
        workers = {r["worker"] for r in tables["worker_assignment"]}
        claims = {r["key"] for r in tables["claim"]}
        charges_by_key = {r["key"]: r for r in tables["service_charge"]}
        events = {r["key"]: r for r in tables["claim_event"]}
        for r in tables["bed_interval"]:
            keyed(r["patient"] in patients, r["key"], "orphan bed occupant")
        for r in tables["staff_shift"]:
            keyed(r["worker"] in workers, r["key"], "orphan staffed worker")
        for r in tables["claim_line"]:
            keyed(r["claim"] in claims and r["charge"] in charges_by_key, r["key"], "orphan claim/charge")
            keyed(dec(r["amount"]) == dec(charges_by_key[r["charge"]]["billed"]), r["key"], "claim line differs from charge")
        for r in events.values():
            keyed(r["claim"] in claims, r["key"], "orphan claim event")
            if dec(r["cash_delta"]) < 0:
                keyed(r["reverses"] in events and dec(events[r["reverses"]]["cash_delta"]) >= -dec(r["cash_delta"]), r["key"], "unlinked/excess refund")
    capture("P1_REFERENCES", links)

    def resources():
        beds_rows = tables["bed_interval"]
        no_overlap(beds_rows, "bed", "start", "end")
        no_overlap(beds_rows, "patient", "start", "end")
        actual_seconds = sum(int((dt(r["end"]) - dt(r["start"])).total_seconds()) for r in beds_rows)
        require(actual_seconds == expectations["occupied_seconds"], "hand-calculated bed integral")
        for r in tables["staff_shift"]:
            actual = Decimal(str((dt(r["end"]) - dt(r["start"])).total_seconds())) / 3600
            keyed(actual == dec(r["worked"]) == dec(r["productive"]) + dec(r["nonproductive"]) + dec(r["break"]), r["key"], "DST shift hours")
        quantity = sum(dec(r["qty"]) for r in tables["inventory_movement"])
        require(quantity == dec(expectations["closing_stock"]), "independent stock ledger")
    capture("P1_RESOURCES", resources)

    def finance():
        charge = tables["service_charge"][0]
        keyed(cents(dec(charge["units"]) * dec(charge["price"])) == dec(charge["billed"]), charge["key"], "charge units/price")
        claim = tables["claim"][0]
        require(dec(claim["billed"]) == sum(dec(r["amount"]) for r in tables["claim_line"]), "claim lines/header")
        ar = dec(claim["opening_ar"]) + sum(dec(r["ar_delta"]) for r in tables["claim_event"])
        cash = sum(dec(r["cash_delta"]) for r in tables["claim_event"])
        require(ar == dec(expectations["closing_ar"]) and cash == dec(expectations["closing_cash"]), "independent payment/refund reconciliation")
        totals = defaultdict(lambda: [Decimal(0), Decimal(0)])
        for row in tables["financial_posting"]:
            d, c = dec(row["debit"]), dec(row["credit"])
            keyed(d >= 0 and c >= 0 and ((d > 0) != (c > 0)), row["key"], "journal one-sided positive")
            totals[row["journal"]][0] += d
            totals[row["journal"]][1] += c
        require(all(d == c for d, c in totals.values()), "independent balanced journals")
        require(sum(dec(r["amount"]) for r in tables["cost_allocation"]) == dec(expectations["pool"]), "independent cost allocation")
        require(dec(tables["finance_monthly"][0]["amount"]) == dec(expectations["pool"]), "monthly Axiom fixture reconciliation")
    capture("P1_FINANCE", finance)
    return results


@exact_context
def reconcile_candidate(tables, expected):
    """Expose independently calculated observations alongside literal golden expectations."""
    observed = {
        "occupied_seconds": sum(int((dt(r["end"]) - dt(r["start"])).total_seconds()) for r in tables["bed_interval"]),
        "closing_stock": sum(dec(r["qty"]) for r in tables["inventory_movement"]),
        "closing_ar": sum(dec(r["opening_ar"]) for r in tables["claim"]) + sum(dec(r["ar_delta"]) for r in tables["claim_event"]),
        "closing_cash": sum(dec(r["cash_delta"]) for r in tables["claim_event"]),
        "pool": sum(dec(r["amount"]) for r in tables["cost_allocation"]),
    }
    return {key: {"scope": "DEVELOPMENT_PROJECTION", "expected": str(expected[key]), "observed": str(value),
                  "difference": str(dec(str(value)) - dec(str(expected[key])))} for key, value in observed.items()}


@exact_context
def validate_exports(tables, envelopes):
    """Use csv/hashlib directly; do not call generator serializer/parser."""
    import csv
    import io
    try:
        require(len(envelopes) == 2 and {e["manifest"]["source"] for e in envelopes} == {"WORKDAY", "AXIOM"}, "missing/duplicate source projection")
        expected = {
            "WORKDAY": [{"key": r["key"], "EmployeeID": r["worker"], "FirstName": r["name"].split()[0], "LastName": r["name"].split()[-1], "Rate": r["rate"]} for r in tables["worker_assignment"]],
            "AXIOM": [{"key": r["key"], "Period": r["month"], "Version": r["vintage"], "amount": r["amount"]} for r in tables["finance_monthly"]],
        }
        for envelope in envelopes:
            m, payload = envelope["manifest"], envelope["payload"]
            require(hashlib.sha256(payload.encode("utf-8")).hexdigest() == m["sha256"], "source byte checksum")
            require(len(payload.encode("utf-8")) == m["bytes"], "source byte length")
            rows = list(csv.DictReader(io.StringIO(payload, newline="")))
            require(len(rows) == m["expected_rows"], "source row count")
            require(sorted(rows, key=lambda r: r["key"]) == sorted(expected[m["source"]], key=lambda r: r["key"]), "source round-trip values")
            require(sum(dec(r.get("amount", "0")) for r in rows) == dec(m["amount_total"]), "source amount control total")
        return {"rule_id": "P1_EXPORTS", "severity": "P0", "scope": "DEVELOPMENT_SOURCE_PROJECTION", "status": "PASS", "failures": []}
    except Exception as exc:
        return {"rule_id": "P1_EXPORTS", "severity": "P0", "scope": "DEVELOPMENT_SOURCE_PROJECTION", "status": "FAIL", "failures": [{"record_key": "Workday/Axiom fixture file", "reason": str(exc)}]}
