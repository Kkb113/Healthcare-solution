"""Read-only verification of persisted resource files, temporal controls and mirrors."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sqlite3
import sys
from decimal import Context,ROUND_HALF_UP,localcontext
from importlib import metadata,resources
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from validate_clinical_data import files_at,encode
from healthcare_synthetic.resource_validation import ResourceClinicalValidator,ResourceOperationalValidator,ResourceValidator
from healthcare_synthetic.resource_stock_validation import StockValidator
from healthcare_synthetic.resource_review import render_resources,review_gate


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(value):return hashlib.sha256(encode(value)).hexdigest()


def inspect_resources(output=ROOT/'output/resource-foundation',config_path=ROOT/'config/resource-foundation-generation.json',review_path=ROOT/'reviews/resource-foundation-review.json'):
    with localcontext(Context(prec=38,rounding=ROUND_HALF_UP)):
        return _inspect(Path(output).resolve(),Path(config_path),Path(review_path))


def _inspect(output,config_path,review_path):
    original=(output/'manifest.json').read_bytes();manifest=json.loads(original);cfg=read(config_path)
    if manifest['profile']!='CONNECTED_WORKFORCE_AND_STOCK' or manifest['status'] not in ('RESOURCE_FOUNDATION_PASSED','BLOCKED','REVIEW_PENDING'):raise ValueError('incomplete or wrong resource candidate')
    if sha(cfg)!=manifest['locks']['configuration_sha256']:raise ValueError('resource configuration lock differs')
    runtime={'python':platform.python_version(),'implementation':platform.python_implementation(),'tzdata':metadata.version('tzdata'),
        'chicago_sha256':hashlib.sha256(resources.files('tzdata').joinpath('zoneinfo/America/Chicago').read_bytes()).hexdigest()}
    if runtime!=manifest['locks']['runtime']:raise ValueError('resource runtime lock differs')
    for name,expected in manifest['locks']['files'].items():
        file=(ROOT/name).resolve()
        if ROOT not in file.parents or hashlib.sha256(file.read_bytes()).hexdigest()!=expected:raise ValueError('resource input/source lock differs: '+name)
    parent_path=(ROOT/cfg['parent_candidate']).resolve();gate=read(ROOT/'evidence/operational-flow/acceptance-gate.json');parent=read(parent_path/'manifest.json')
    if ROOT not in parent_path.parents or gate['status']!='PASSED' or parent['status']!='OPERATIONAL_FLOW_PASSED' or gate['business_sha256']!=cfg['parent_business_sha256'] or parent['business_sha256']!=gate['business_sha256']:raise ValueError('accepted operational anchor differs')
    if sha({k:v['sha256'] for k,v in sorted(parent['canonical_files'].items())})!=parent['business_sha256']:raise ValueError('parent file-map hash differs')
    actual={p.relative_to(parent_path).as_posix() for p in (parent_path/'canonical').iterdir() if p.is_file()}
    if actual!={v['file'] for v in parent['canonical_files'].values()}:raise ValueError('parent canonical inventory differs')
    for name,meta in parent['canonical_files'].items():
        file=(parent_path/meta['file']).resolve()
        if parent_path not in file.parents:raise ValueError('parent file path escaped')
        h=hashlib.sha256();size=count=0
        with file.open('rb') as stream:
            for line in stream:h.update(line);size+=len(line);count+=1
        if h.hexdigest()!=meta['sha256'] or size!=meta['bytes'] or count!=meta['rows']:raise ValueError('parent data checksum/count differs: '+name)
        if name!='clinical_event' and manifest['canonical_files'][name]['sha256']!=meta['sha256']:raise ValueError('immutable parent business table changed: '+name)
    tables=files_at(output,manifest);schema=read(ROOT/'contracts/phase0/schema.json');primary={t['name']:t['primary_key'][0] for t in schema['tables']}
    clinical_index={r['clinical_event_version_id']:r for r in tables['clinical_event']}
    changes={r['text_value'].split('procedure ')[1].split(':')[0] for r in tables['clinical_event'] if r['source_record_id'].endswith('/resource-response')}
    old_ids=set()
    with (parent_path/parent['canonical_files']['clinical_event']['file']).open(encoding='utf-8') as stream:
        for line in stream:
            row=json.loads(line);key=row['clinical_event_version_id'];old_ids.add(key);new=clinical_index.get(key)
            if new is None:raise ValueError('parent clinical fact missing')
            allowed={'author_assignment_id','consumption_group_key','generation_run_id'}
            if row['clinical_event_id'] in changes:allowed|={'occurred_at','period_end_at','encounter_version_id','recorded_at','known_from','export_available_at'}
            if any(new[k]!=v for k,v in row.items() if k not in allowed):raise ValueError('unexplained changed/stale parent clinical fact')
    if any(not r['source_record_id'].endswith('/resource-response') for key,r in clinical_index.items() if key not in old_ids):raise ValueError('unregistered new clinical fact')
    review_decision=read(review_path) if review_path.exists() else None
    graph={'coordination':(),'workforce':('coordination',),'clinical_binding':('coordination','workforce'),
        'inventory':('coordination','workforce','clinical_binding'),'validation':('coordination','workforce','clinical_binding','inventory')}
    ownership={'coordination':{'clinical_event'},'workforce':{'staff_shift'},'clinical_binding':{'clinical_event'},'inventory':{'clinical_event','inventory_movement'},'validation':set()}
    validation_only={f'src/healthcare_synthetic/{name}.py' for name in ('resource_validation','resource_stock_validation','resource_review','operational_review','clinical_validation','master_validation')}
    generation_locks={**manifest['locks'],'files':{k:v for k,v in manifest['locks']['files'].items() if k not in validation_only}}
    current_indexes={name:{r[primary[name]]:r for r in tables[name]} for name in ('clinical_event','staff_shift','inventory_movement')}
    connection=sqlite3.connect('file:'+(output/'checkpoints.sqlite3').as_posix()+'?mode=ro',uri=True);mirror=0;stored_validation=None
    try:
        if {r[0] for r in connection.execute('SELECT name FROM stages')}!=set(graph):raise ValueError('resource checkpoint stage inventory differs')
        for stage,parents in graph.items():
            local_hash,input_hash,payload,checksum,count=connection.execute('SELECT local_hash,input_hash,payload,checksum,row_count FROM stages WHERE name=?',(stage,)).fetchone()
            local=sha({'locks':manifest['locks'] if stage=='validation' else generation_locks,'review':review_decision if stage=='validation' else None})
            if local_hash!=local or input_hash!=sha({'local':local,'parents':{p:manifest['stage_checksums'][p] for p in parents}}):raise ValueError('checkpoint source/dependency fingerprint differs')
            if hashlib.sha256(payload.encode()).hexdigest()!=checksum or manifest['stage_checksums'].get(stage)!=checksum:raise ValueError('checkpoint corruption')
            value=json.loads(payload)
            if set(value)!={'tables','controls'} or set(value['tables'])!=ownership[stage] or sum(map(len,value['tables'].values()))!=count:raise ValueError('checkpoint ownership/physical row accounting differs')
            mirror+=count
            for name,rows in value['tables'].items():
                if len(rows)!=len(tables[name]) or len({r[primary[name]] for r in rows})!=len(rows):raise ValueError('checkpoint row count/uniqueness differs')
                excluded={'author_assignment_id','consumption_group_key','generation_run_id'} if stage=='coordination' else {'consumption_group_key','generation_run_id'} if stage=='clinical_binding' else set()
                for row in rows:
                    final=current_indexes[name].get(row[primary[name]])
                    if final is None or set(row)!=set(final) or any(final[k]!=v for k,v in row.items() if k not in excluded):raise ValueError('checkpoint/canonical business row differs')
            if stage=='validation':stored_validation=value['controls']
            del value,payload
    finally:connection.close()
    master_path=ROOT/'output/master-foundation';master_manifest=read(master_path/'manifest.json');ccfg=read(ROOT/'config/clinical-history-generation.json')
    if master_manifest['business_sha256']!=ccfg['master_business_sha256']:raise ValueError('accepted master anchor differs')
    master=files_at(master_path,master_manifest)
    policy=read(ROOT/'contracts/clinical-history-policy.json');policy['new_business_tables']+=['bed_event','facility_day_driver','staff_shift','inventory_movement']
    ocfg=read(ROOT/'config/operational-flow-generation.json');policy.update(site_transport_minutes=ocfg['site_transport_minutes'],site_transport_handover_max_minutes=ocfg['site_transport_handover_max_minutes'])
    clinical=ResourceClinicalValidator(tables,schema,ccfg,policy,master).run();operations=ResourceOperationalValidator(tables,schema,ocfg,manifest['simulation']).run()
    workforce=ResourceValidator(tables,schema,cfg).run();stock=StockValidator(tables,cfg).run()
    for name,result in [('clinical',clinical),('operations',operations),('workforce',workforce),('stock',stock)]:
        if result!=stored_validation[name]:raise ValueError('independent '+name+' controls differ from persisted validation')
    body,selection=render_resources(tables,cfg)
    if (output/'resource-review-sample.md').read_bytes()!=body.encode() or selection!=stored_validation['review_selection']:raise ValueError('resource review text/selected facts differ')
    review=review_gate(selection,review_decision);defects=clinical['defects']+operations['defects']+workforce['defects']+stock['defects']
    status='BLOCKED' if defects else 'RESOURCE_FOUNDATION_PASSED' if review['status']=='PASS' else 'REVIEW_PENDING'
    if manifest['rows_by_table']!={t:len(rows) for t,rows in tables.items()} or manifest['business_rows']!=sum(map(len,tables.values())):raise ValueError('candidate business row accounting differs')
    if manifest['checkpoint_mirror_rows']!=mirror or manifest['physical_serialized_rows']!=manifest['business_rows']+mirror+selection['mirror_rows']:raise ValueError('candidate physical mirror accounting differs')
    if read(output/'validation-report.json')!=stored_validation:raise ValueError('validation publication differs from committed checkpoint')
    if (output/'manifest.json').read_bytes()!=original:raise ValueError('candidate changed during independent inspection')
    return {'gate_status':status,'artifact_integrity':'PASS','business_sha256':manifest['business_sha256'],'clinical':clinical,'operations':operations,
        'workforce':workforce,'stock':stock,'review':review,'review_selection':selection,'defects':defects,
        'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/resource-foundation');p.add_argument('--report',type=Path);a=p.parse_args()
    try:result=inspect_resources(a.output)
    except Exception as exc:result={'gate_status':'BLOCKED','error':str(exc)}
    if a.report:a.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('gate_status','artifact_integrity','error') if k in result}));sys.exit(0 if result['gate_status']=='RESOURCE_FOUNDATION_PASSED' else 2)
