"""Read-only inspection of financial canonical files, source anchors and checkpoints."""
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
from healthcare_synthetic.financial_validation import validate_financial
from healthcare_synthetic.financial_review import render_financial,review_gate

GRAPH={'billing':(), 'claims':('billing',), 'posting':('billing','claims'), 'allocation':('billing','claims','posting'),
       'planning':('billing','claims','posting'), 'validation':('billing','claims','posting','allocation','planning')}
OWNERS={'billing':{'catalog_item','service_charge'},'claims':{'claim','claim_line','claim_event'},'posting':{'financial_posting'},
        'allocation':{'cost_allocation'},'planning':{'finance_monthly'},'validation':set()}
VALIDATION_ONLY={'src/healthcare_synthetic/financial_validation.py','src/healthcare_synthetic/financial_review.py','src/healthcare_synthetic/financial_oracles.py','src/healthcare_synthetic/financial_room_validation.py'}


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(value):return hashlib.sha256(encode(value)).hexdigest()


def inspect_financial(output=ROOT/'output/financial-history',config_path=ROOT/'config/financial-history-generation.json',review_path=ROOT/'reviews/financial-history-review.json'):
    with localcontext(Context(prec=38,rounding=ROUND_HALF_UP)):
        return _inspect(Path(output).resolve(),Path(config_path),Path(review_path))


def _inspect(output,config_path,review_path):
    raw=(output/'manifest.json').read_bytes();manifest=json.loads(raw);cfg=read(config_path)
    if manifest['profile']!='CONNECTED_FINANCIAL_HISTORY' or manifest['status'] not in ('FINANCIAL_HISTORY_PASSED','REVIEW_PENDING','BLOCKED'):raise ValueError('incomplete or wrong financial candidate')
    if sha(cfg)!=manifest['locks']['configuration_sha256']:raise ValueError('financial configuration lock differs')
    runtime={'python':platform.python_version(),'implementation':platform.python_implementation(),'tzdata':metadata.version('tzdata'),
             'chicago_sha256':hashlib.sha256(resources.files('tzdata').joinpath('zoneinfo/America/Chicago').read_bytes()).hexdigest()}
    if runtime!=manifest['locks']['runtime']:raise ValueError('financial runtime lock differs')
    for name,expected in manifest['locks']['files'].items():
        file=(ROOT/name).resolve()
        if ROOT not in file.parents or hashlib.sha256(file.read_bytes()).hexdigest()!=expected:raise ValueError('financial source/input lock differs: '+name)
    parent_path=(ROOT/cfg['parent_candidate']).resolve();parent=read(parent_path/'manifest.json');gate=read(ROOT/'evidence/resource-foundation/acceptance-gate.json')
    if ROOT not in parent_path.parents or parent['status']!='RESOURCE_FOUNDATION_PASSED' or gate['status']!='PASSED' or parent['business_sha256']!=cfg['parent_business_sha256'] or gate['business_sha256']!=cfg['parent_business_sha256']:raise ValueError('accepted resource anchor differs')
    if sha({k:v['sha256'] for k,v in sorted(parent['canonical_files'].items())})!=parent['business_sha256']:raise ValueError('resource parent map hash differs')
    actual={p.relative_to(parent_path).as_posix() for p in (parent_path/'canonical').iterdir() if p.is_file()}
    if actual!={v['file'] for v in parent['canonical_files'].values()}:raise ValueError('resource parent file inventory differs')
    for name,m in parent['canonical_files'].items():
        file=(parent_path/m['file']).resolve()
        if parent_path not in file.parents:raise ValueError('resource parent path escaped')
        h=hashlib.sha256();size=count=0
        with file.open('rb') as stream:
            for line in stream:h.update(line);size+=len(line);count+=1
        if h.hexdigest()!=m['sha256'] or size!=m['bytes'] or count!=m['rows']:raise ValueError('resource parent checksum/count differs: '+name)
        if name!='catalog_item' and manifest['canonical_files'][name]['sha256']!=m['sha256']:raise ValueError('accepted clinical/resource table changed: '+name)
    tables=files_at(output,manifest);schema=read(ROOT/'contracts/phase0/schema.json');primary={t['name']:t['primary_key'][0] for t in schema['tables']}
    cat={r['catalog_item_id']:r for r in tables['catalog_item']};old=set()
    with (parent_path/parent['canonical_files']['catalog_item']['file']).open(encoding='utf-8') as stream:
        for line in stream:
            r=json.loads(line);old.add(r['catalog_item_id'])
            if cat.get(r['catalog_item_id'])!=r:raise ValueError('accepted catalog vocabulary changed')
    additions=[r for k,r in cat.items() if k not in old]
    if len(additions)!=5 or {r['code'] for r in additions}!={'BILL-ROOM','BILL-ICU','BILL-ED','BILL-OPD','BILL-HOLD'} or any(r['domain']!='PROCEDURE' or r['code_system']!='HOSPITAL_LOCAL' for r in additions):raise ValueError('unregistered billing vocabulary amendment')
    for t in schema['tables']:
        if t['name']=='catalog_item':t['planned_rows']+=5
        elif t['name']=='claim':t['planned_rows']=58000
        elif t['name']=='claim_line':t['planned_rows']=117000
        elif t['name']=='claim_event':t['planned_rows']=220000
        elif t['name']=='cost_allocation':t['planned_rows']=165000
        elif t['name']=='clinical_condition':t['planned_rows']=85000
        elif t['name']=='inventory_movement':t['planned_rows']=55000
    decision=read(review_path) if review_path.exists() else None
    generation_locks={**manifest['locks'],'files':{k:v for k,v in manifest['locks']['files'].items() if k not in VALIDATION_ONLY}}
    connection=sqlite3.connect('file:'+(output/'checkpoints.sqlite3').as_posix()+'?mode=ro',uri=True);mirror=0;stored=None
    try:
        if {r[0] for r in connection.execute('SELECT name FROM stages')}!=set(GRAPH):raise ValueError('financial checkpoint inventory differs')
        for stage,parents in GRAPH.items():
            local_hash,input_hash,payload,checksum,count=connection.execute('SELECT local_hash,input_hash,payload,checksum,row_count FROM stages WHERE name=?',(stage,)).fetchone()
            local=sha({'locks':manifest['locks'] if stage=='validation' else generation_locks,'review':decision if stage=='validation' else None})
            if local_hash!=local or input_hash!=sha({'local':local,'parents':{p:manifest['stage_checksums'][p] for p in parents}}):raise ValueError('financial checkpoint input/dependency fingerprint differs')
            if hashlib.sha256(payload.encode()).hexdigest()!=checksum or manifest['stage_checksums'][stage]!=checksum:raise ValueError('financial checkpoint corruption')
            value=json.loads(payload)
            if set(value)!={'tables','controls'} or set(value['tables'])!=OWNERS[stage] or sum(map(len,value['tables'].values()))!=count:raise ValueError('financial checkpoint ownership/row accounting differs')
            mirror+=count
            for name,rows in value['tables'].items():
                index={r[primary[name]]:r for r in tables[name]}
                if len(rows)!=len(index) or len({r[primary[name]] for r in rows})!=len(rows) or any(index.get(r[primary[name]])!=r for r in rows):raise ValueError('financial checkpoint/canonical content differs')
            if stage=='validation':stored=value['controls']
            del value,payload
    finally:connection.close()
    controls=validate_financial(tables,cfg,schema);body,selection=render_financial(tables,cfg)
    if (output/'financial-review-sample.md').read_bytes()!=body.encode():raise ValueError('financial review publication differs')
    controls['review_selection']=selection;controls['review']=review_gate(selection,decision)
    controls['gate_status']='BLOCKED' if controls['defects'] else 'FINANCIAL_HISTORY_PASSED' if controls['review']['status']=='PASS' else 'REVIEW_PENDING'
    if controls!=stored or read(output/'validation-report.json')!=stored:raise ValueError('independent financial controls differ from committed/published report')
    if manifest['rows_by_table']!={t:len(r) for t,r in tables.items()} or manifest['business_rows']!=sum(map(len,tables.values())):raise ValueError('financial business row accounting differs')
    if manifest['checkpoint_mirror_rows']!=mirror or manifest['physical_serialized_rows']!=manifest['business_rows']+mirror+selection['mirror_rows']:raise ValueError('financial physical mirror accounting differs')
    if (output/'manifest.json').read_bytes()!=raw:raise ValueError('financial candidate changed during inspection')
    return {**controls,'artifact_integrity':'PASS','business_sha256':manifest['business_sha256'],'accepted_resource_sha256':parent['business_sha256'],
            'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/financial-history');p.add_argument('--report',type=Path);a=p.parse_args()
    try:result=inspect_financial(a.output)
    except Exception as exc:result={'gate_status':'BLOCKED','error':str(exc)}
    if a.report:a.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('gate_status','artifact_integrity','error') if k in result}));sys.exit(0 if result['gate_status']=='FINANCIAL_HISTORY_PASSED' else 2)
