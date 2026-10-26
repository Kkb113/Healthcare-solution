"""Full-population contracts and independent disposable consumer comparisons."""
from __future__ import annotations

import gc
import json
from collections import Counter, defaultdict
from datetime import timedelta
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext

from .integrated_generation import ROOT, financial_config, load_snapshot, read, schema
from .integrated_consumers import (START, END, GRACE, claim_balances, selected_allocations,
    finance_series, variances, latest, feature_snapshot, instant, stamp, month, digest)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inspection_dependencies():
    from .integrated_generation import sha_file
    # Native source parsing/export is validated and bound separately. A reader
    # repair must not invalidate unrelated clinical/accounting population tests.
    files = [p for p in sorted((ROOT/'src/healthcare_synthetic').glob('*.py'))
             if not p.stem.startswith('source_') and p.stem not in ('integrated_exports','integrated_source_validation')]
    files += [ROOT/'scripts/inspect_integrated_history.py']
    files += sorted((ROOT/'config').glob('*.json')) + sorted((ROOT/'contracts').rglob('*.json'))
    return {p.relative_to(ROOT).as_posix():sha_file(p) for p in files}


def domain_controls(candidate):
    """Execute the accepted domain validators again, on current persisted facts."""
    from .master_pipeline import load_inputs
    from .master_validation import MasterValidator
    from .resource_validation import ResourceClinicalValidator, ResourceOperationalValidator, ResourceValidator
    from .resource_stock_validation import StockValidator
    from .financial_validation import validate_financial
    manifest = read(candidate / 'manifest.json'); seed = manifest['seed']
    from .integrated_master_context import amend
    tables, _ = load_snapshot(candidate); master, _ = load_snapshot(ROOT / 'output/master-foundation'); master = amend(master)
    ccfg = read(ROOT/'config/clinical-history-generation.json'); ccfg['seed'] = seed
    ocfg = read(ROOT/'config/operational-flow-generation.json'); ocfg['seed'] = seed
    rcfg = read(ROOT/'config/resource-foundation-generation.json'); rcfg['seed'] = seed
    mc, mp, _, refs, _ = load_inputs(ROOT/'config/master-data-generation.json')
    print('Fresh integrated domain: master',flush=True)
    results = {'master': MasterValidator(master, read(ROOT/'contracts/phase0/schema.json'), mc, mp, refs).run()}
    policy = read(ROOT/'contracts/clinical-history-policy.json')
    policy['new_business_tables'] += ['bed_event','facility_day_driver','staff_shift','inventory_movement']
    policy.update(site_transport_minutes=ocfg['site_transport_minutes'],site_transport_handover_max_minutes=ocfg['site_transport_handover_max_minutes'])
    resource_names = set(read(ROOT/'output/resource-foundation/manifest.json')['canonical_files'])
    resource = {k: v for k,v in tables.items() if k in resource_names}
    resource['catalog_item'] = [r for r in resource['catalog_item'] if r['code'] not in {'BILL-ROOM','BILL-ICU','BILL-ED','BILL-OPD','BILL-HOLD'}]
    resource_schema = read(ROOT/'contracts/phase0/schema.json')
    # Domain budget checks use the effective integrated envelope, including the
    # reviewed reassignments; the planned total itself is never relaxed.
    effective = {t['name']: t['planned_rows'] for t in schema()['tables']}
    for table in resource_schema['tables']:
        table['planned_rows'] = effective.get(table['name'], table['planned_rows'])
    print('Fresh integrated domain: clinical',flush=True)
    results['clinical'] = ResourceClinicalValidator(resource, resource_schema, ccfg, policy, master).run()
    print('Fresh integrated domain: operations',flush=True)
    results['operations'] = ResourceOperationalValidator(resource, resource_schema, ocfg, manifest['simulation']).run()
    print('Fresh integrated domain: workforce',flush=True)
    results['workforce'] = ResourceValidator(resource, resource_schema, rcfg).run()
    print('Fresh integrated domain: stock',flush=True)
    results['stock'] = StockValidator(resource, rcfg).run()
    print('Fresh integrated domain: finance',flush=True)
    results['finance'] = validate_financial(tables, financial_config(seed), schema())
    defects = [{'domain': name, **failure} for name, result in results.items() for failure in result['defects']]
    return {'status': 'PASS' if not defects else 'FAIL', 'domains': results, 'defects': defects,
            'checks_freshly_executed': sum(len(r.get('checks', [])) for r in results.values()), 'business_sha256': manifest['business_sha256']}


def reconcile(tables):
    from .financial_queries import claim_history, selected_costs, select_monthly
    from .resource_queries import labor_totals, inventory_ledger_at
    from .operational_validation import bed_intervals
    coverage = {r['coverage_version_id']: r for r in tables['patient_coverage']}; payers = {r['payer_plan_id']: r for r in tables['payer_plan']}
    claim = claim_balances(tables['claim'], tables['claim_event'], coverage, payers)
    expected = claim_history(tables, END, GRACE)
    require({k: Decimal(v) for k,v in claim['ar_by_original'].items()} == {k: Decimal(v) for k,v in expected['balances'].items()}, 'original-level AR differs')
    require(sum(map(Decimal, claim['cash_by_month'].values())) == Decimal(expected['cash']), 'claim signed cash differs')
    require(claim['observed_initial_insured'] == expected['observed_initial_insured_claims'] and claim['denied_initial_insured'] == expected['initial_denied_insured_claims'], 'original denial denominator differs')
    shifts = latest(tables['staff_shift'], 'shift_id'); labor = defaultdict(lambda: defaultdict(Decimal))
    for r in shifts.values():
        for field in ('worked_hours','productive_hours','paid_nonproductive_hours','unpaid_break_hours','overtime_hours','loaded_cost'):
            labor[month(r['planned_start'])][field] += Decimal(r[field])
        require(Decimal(r['worked_hours']) == Decimal(r['productive_hours'])+Decimal(r['paid_nonproductive_hours'])+Decimal(r['unpaid_break_hours']), 'captured attendance components differ')
    for m, totals in labor.items():
        oracle = labor_totals(tables, GRACE, m)['totals']
        require(all(v == Decimal(oracle[k]) for k,v in totals.items()), 'monthly labor consumer differs: '+m)
    stocks = defaultdict(lambda: [Decimal(0),Decimal(0)])
    for r in tables['inventory_movement']:
        if r['occurred_at'] <= END and r['export_available_at'] <= GRACE:
            key = r['location_id'],r['catalog_item_id'],r['lot_id']; stocks[key][0] += Decimal(r['quantity_base']); stocks[key][1] += Decimal(r['extended_cost'])
    oracle_stock = inventory_ledger_at(tables, END, GRACE)
    require(sum(v[1] for v in stocks.values()) == Decimal(oracle_stock['total_book_value_usd']), 'lot book value differs')
    for r in oracle_stock['balances']:
        require(stocks[r['location_id'],r['catalog_item_id'],r['lot_id']] == [Decimal(r['quantity_base']), Decimal(r['book_value_usd'])], 'stock lot/location/product consumer differs')
    allocations = selected_allocations(tables['cost_allocation']); costs = defaultdict(Decimal); by_pool = defaultdict(Decimal); patient_month = defaultdict(Decimal)
    enc = {r['encounter_version_id']: r for r in tables['encounter']}
    for r in allocations:
        costs[r['destination_type']] += Decimal(r['allocated_amount']); by_pool[r['posting_id']] += Decimal(r['allocated_amount'])
        if r['encounter_version_id']:
            patient_month[enc[r['encounter_version_id']]['encounter_id'],r['accounting_month'],r['cost_category']] += Decimal(r['allocated_amount'])
    for posting in tables['financial_posting']:
        if posting['eligible_for_allocation']:
            require(by_pool[posting['posting_id']] == Decimal(posting['debit_amount'])-Decimal(posting['credit_amount']), 'selected allocation pool differs')
    require(dict(costs) == {k: Decimal(v) for k,v in selected_costs(tables, GRACE)['totals'].items()}, 'cost destination selection differs')
    series = finance_series(tables['finance_monthly']); periods = sorted({r['accounting_month'] for r in tables['finance_monthly']})
    for m in periods:
        for scenario in ('ACTUAL','BUDGET','FORECAST'):
            our = {r['finance_record_id'] for r in series.values() if r['accounting_month']==m and r['scenario']==scenario}
            require(our == {r['finance_record_id'] for r in select_monthly(tables, scenario, m, GRACE)}, 'finance series/vintage selection differs')
    cats = {r['catalog_item_id']: r for r in tables['catalog_item']}; actual_checks = 0; grouped = defaultdict(list)
    for r in tables['finance_monthly']:
        if r['scenario']=='ACTUAL' and r['amount'] is not None:
            grouped[r['accounting_month'], r['published_at']].append(r)
    for (m, known), actuals in grouped.items():
        following = (instant(m+'T00:00:00Z').date().replace(day=28)+timedelta(days=4)).replace(day=1).isoformat()
        pnl = defaultdict(Decimal); balances = defaultdict(Decimal)
        for p in tables['financial_posting']:
            if p['posting_date'] >= following or max(p['known_from'],p['export_available_at'])>known:
                continue
            a = cats[p['account_catalog_id']]; value = Decimal(p['debit_amount'])-Decimal(p['credit_amount'])
            if a['account_class'] in ('ASSET','LIABILITY','EQUITY'):
                balances[p['facility_id'],p['account_catalog_id']] += value
            elif p['posting_date'] >= m:
                pnl[p['cost_center_id'],p['account_catalog_id']] += value
        for r in actuals:
            a = cats[r['account_catalog_id']]
            value = balances[r['facility_id'],r['account_catalog_id']] if a['account_class'] in ('ASSET','LIABILITY','EQUITY') else pnl[r['cost_center_id'],r['account_catalog_id']]
            if a['normal_balance']=='CREDIT':
                value = -value
            require(value == Decimal(r['amount']), 'GL/Axiom grain differs: '+r['finance_record_id']); actual_checks += 1
    # Independent full-state integration versus paired occupancy-boundary oracle.
    superseded = {r['corrects_bed_event_id'] for r in tables['bed_event'] if r['corrects_bed_event_id']}
    events = defaultdict(list); locations = {r['location_id']: r for r in tables['location']}; integrated = defaultdict(int)
    for r in tables['bed_event']:
        if r['bed_event_id'] not in superseded:
            events[r['bed_location_id']].append(r)
    for bid, history in events.items():
        ordered = sorted(history, key=lambda r:(r['effective_at'],r['sequence_no']))
        for i,r in enumerate(ordered):
            a = max(START, r['effective_at']); z = min(END, ordered[i+1]['effective_at'] if i+1<len(ordered) else END)
            if r['occupancy_state']=='OCCUPIED' and a<z:
                integrated[bid] += int((instant(z)-instant(a)).total_seconds())
    intervals = bed_intervals(tables['bed_event'], enc); paired = defaultdict(int)
    for bid,eid,a,z in intervals:
        paired[bid] += int((instant(z)-instant(a)).total_seconds())
    require(dict(integrated)==dict(paired), 'bed-level occupied seconds differ between independent consumers')
    # Compute actual multiplication exposure before any analytical join. A safe
    # consumer emits one charge/bed interval/cost fact regardless of dimensions.
    diag = Counter(enc[r['encounter_version_id']]['encounter_id'] for r in tables['clinical_condition'] if r['encounter_version_id'])
    clinical = Counter(enc[r['encounter_version_id']]['encounter_id'] for r in tables['clinical_event'])
    claim_lines = Counter()
    headers = {r['claim_id']: r for r in tables['claim']}
    for r in tables['claim_line']:
        claim_lines[enc[headers[r['claim_id']]['encounter_version_id']]['encounter_id']] += 1
    bed_count = Counter(eid for _,eid,_,_ in intervals); exposed = 0; naive = Decimal(0); protected = Decimal(0); current_billed = Decimal(0)
    for r in tables['service_charge']:
        eid = enc[r['encounter_version_id']]['encounter_id']; factor = max(1,diag[eid])*max(1,clinical[eid])*max(1,claim_lines[eid])*max(1,bed_count[eid])
        exposed += factor>1; naive += Decimal(r['billed_amount'])*factor; protected += Decimal(r['billed_amount'])
        if r['service_to'] >= '2023-01-01' and r['service_from'] <= '2025-12-31':
            current_billed += Decimal(r['billed_amount'])
    require(exposed>0 and naive>protected and len({r['charge_id'] for r in tables['service_charge']})==len(tables['service_charge']), 'fanout negative control is vacuous or charge grain is not unique')
    variance = variances(tables['finance_monthly']); variance_states = Counter(r['state'] for r in variance)
    require(all(variance_states[s]>0 for s in ('COMPARABLE','NO_PLAN','ZERO_PLAN')), 'variance missing/zero states collapsed')
    return {'status':'PASS','unexplained_differences':0,'original_ar_accounts':len(claim['ar_by_original']),
            'claim_cash_months':len(claim['cash_by_month']),'staffing_months_including_opening_context':len(labor),
            'staffing_business_months':len([m for m in labor if '2023-01'<=m<='2025-12']),
            'staffing_opening_context_months':sorted(m for m in labor if m<'2023-01'),'lot_location_product_grains':len(stocks),
            'selected_cost_pool_postings':len(by_pool),'patient_month_category_grains':len(patient_month),
            'axiom_monetary_grain_reconciliations':actual_checks,'variance_comparisons':len(variance),'variance_states':dict(variance_states),
            'bed_interval_rows':len(intervals),'bed_seconds_grains':len(paired),'occupied_seconds':sum(paired.values()),
            'fanout':{'exposed_charge_rows':exposed,'naive_join_all_context_billed_usd':str(naive),'protected_all_context_billed_usd':str(protected),
                      'protected_in_window_billed_usd':str(current_billed),'prewindow_context_billed_usd':str(protected-current_billed),
                      'protected_occupied_seconds':sum(paired.values()),'protected_patient_cost_usd':str(costs['PATIENT'])},
            'signed_claim_cash_usd':str(sum(map(Decimal,claim['cash_by_month'].values()))), 'selected_costs_usd':{k:str(v) for k,v in costs.items()}}


def point_in_time(tables):
    checks = []; enc = {r['encounter_version_id']: r for r in tables['encounter']}
    for r in tables['encounter']:
        if r['revision_no']==1:
            require(instant(r['export_available_at']) <= instant(r['arrival_at'])+timedelta(hours=2), 'encounter feed exceeds the readmission-label completeness watermark')
    checks.append('initial_encounter_two_hour_delivery_watermark_validated')
    def before(at):
        return stamp(instant(at)-timedelta(seconds=1))
    late = next(r for r in tables['clinical_condition'] if r['encounter_version_id'] and r['revision_no']==1 and r['export_available_at']>r['known_from'] and START<r['known_from']<END)
    eid = enc[late['encounter_version_id']]['encounter_id']; at = min(before(late['export_available_at']), '2026-01-01T05:59:59Z')
    early = feature_snapshot(tables,eid,at,at)
    require(late['condition_id'] not in early['diagnoses'], 'late diagnosis leaked before delivery'); checks.append('late_diagnosis_hidden')
    actual = next(r for r in tables['clinical_event'] if r['event_type']=='PROCEDURE' and r['period_end_at'] and START<r['occurred_at'] and r['export_available_at']<END)
    eid = enc[actual['encounter_version_id']]['encounter_id']; at = before(actual['export_available_at'])
    require(actual['clinical_event_id'] not in feature_snapshot(tables,eid,at,at)['performed_events'], 'planned/performed care confused'); checks.append('actual_service_hidden_before_delivery')
    after = actual['export_available_at']
    require(actual['clinical_event_id'] in feature_snapshot(tables,eid,after,after)['performed_events'], 'delivered completed service absent'); checks.append('delivered_service_visible')
    discharged = next(r for r in tables['encounter'] if r['discharged_at'] and START<r['discharged_at']<END and r['export_available_at']<END and r['encounter_class']=='IPD' and r['disposition']=='HOME')
    at = before(discharged['export_available_at']); e = feature_snapshot(tables,discharged['encounter_id'],at,at)
    require(e.get('observed_discharge') is None and e['readmission_label']=='UNKNOWN', 'discharge or negative label leaked'); checks.append('future_discharge_and_censored_negative_hidden')
    initial = next(r for r in tables['staff_shift'] if r['attendance_status']=='PUBLISHED' and r['actual_start'] is None)
    selected = latest(tables['staff_shift'],'shift_id',initial['export_available_at'])[initial['shift_id']]
    require(selected['actual_end'] is None and Decimal(selected['worked_hours'])==0, 'roster plan leaked actual attendance'); checks.append('roster_plan_separate_from_actual')
    revision = next(r for r in tables['staff_shift'] if r['revision_no']>=3)
    selected = latest(tables['staff_shift'],'shift_id',before(revision['export_available_at']))[revision['shift_id']]
    require(selected['revision_no']<revision['revision_no'], 'later roster correction leaked'); checks.append('roster_correction_asof')
    revised = next(r for r in tables['finance_monthly'] if r['scenario']=='BUDGET' and r['supersedes_vintage_id'])
    early = finance_series(tables['finance_monthly'],before(revised['published_at']))
    require(revised['finance_record_id'] not in {r['finance_record_id'] for r in early.values()}, 'future plan vintage leaked'); checks.append('budget_vintage_asof')
    for r in tables['finance_monthly']:
        if r['scenario'] in ('BUDGET','FORECAST'):
            require(r['published_at'] < r['accounting_month']+'T00:00:00Z', 'hindsight plan publication')
    checks.append('every_plan_vintage_precedes_target')
    open_visit = next(r for r in latest(tables['encounter'],'encounter_id').values() if r['encounter_class']=='IPD' and r['discharged_at'] is None)
    require(feature_snapshot(tables,open_visit['encounter_id'],GRACE,'2026-01-01T05:59:59Z')['readmission_label']=='UNKNOWN', 'open stay became a negative outcome'); checks.append('open_stay_label_unknown')
    # Retrospective closure metadata is irrelevant to these independent views.
    sample = [{**r,'known_to':'1900-01-01T00:00:00Z'} for r in tables['staff_shift']]
    require(latest(sample,'shift_id',GRACE).keys()==latest(tables['staff_shift'],'shift_id',GRACE).keys(), 'retrospective known_to leaked into selector'); checks.append('retrospective_closure_ignored')
    return {'status':'PASS','checks':checks,'future_fact_failures':0,'unknown_outcomes_preserved':True}
