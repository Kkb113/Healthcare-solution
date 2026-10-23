"""Independently inspect persisted operational files, locks and transactional mirrors."""
import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from validate_clinical_data import files_at, encode
from healthcare_synthetic.operational_validation import OperationalValidator, IntegratedClinicalValidator
from healthcare_synthetic.operational_review import render_operations, review_gate

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def inspect_operations(output=ROOT/'output/operational-flow',config_path=ROOT/'config/operational-flow-generation.json',review_path=ROOT/'reviews/operational-flow-review.json'):
    output=Path(output).resolve();original=(output/'manifest.json').read_bytes();manifest=json.loads(original);cfg=read(config_path)
    if manifest['profile']!='OPERATIONAL_PATIENT_FLOW' or manifest['status'] not in ('OPERATIONAL_FLOW_PASSED','BLOCKED','REVIEW_PENDING'):raise ValueError('candidate incomplete or wrong profile')
    if hashlib.sha256(encode(cfg)).hexdigest()!=manifest['locks']['configuration_sha256']:raise ValueError('operational configuration lock mismatch')
    from importlib import metadata,resources
    import platform
    runtime={'python':platform.python_version(),'implementation':platform.python_implementation(),'tzdata':metadata.version('tzdata'),
             'chicago_sha256':hashlib.sha256(resources.files('tzdata').joinpath('zoneinfo/America/Chicago').read_bytes()).hexdigest()}
    if runtime!=manifest['locks']['runtime']:raise ValueError('operational runtime mismatch')
    for relative,expected in manifest['locks']['files'].items():
        file=(ROOT/relative).resolve()
        if ROOT not in file.parents or hashlib.sha256(file.read_bytes()).hexdigest()!=expected:raise ValueError('input lock mismatch: '+relative)
    parent=read(ROOT/'evidence/clinical-histories/acceptance-gate.json')
    if parent['status']!='PASSED' or parent['business_sha256']!=manifest['locks']['accepted_clinical_sha256']:raise ValueError('clinical acceptance anchor differs')
    parent_path=(ROOT/cfg['accepted_clinical_candidate']).resolve()
    if ROOT not in parent_path.parents:raise ValueError('parent path escaped workspace')
    pm=read(parent_path/'manifest.json')
    if pm['business_sha256']!=parent['business_sha256']:raise ValueError('clinical parent differs')
    # Verify the full accepted parent without retaining a second full event dataset in memory.
    for table,meta in pm['canonical_files'].items():
        file=(parent_path/meta['file']).resolve()
        if parent_path not in file.parents:raise ValueError('parent canonical path escaped')
        sha=hashlib.sha256();size=count=0
        with file.open('rb') as stream:
            for line in stream:sha.update(line);size+=len(line);count+=1
        if sha.hexdigest()!=meta['sha256'] or size!=meta['bytes'] or count!=meta['rows']:raise ValueError('parent file checksum differs: '+table)
    master_path=ROOT/'output/master-foundation';master=files_at(master_path,read(master_path/'manifest.json'))
    tables=files_at(output,manifest);schema=read(ROOT/'contracts/phase0/schema.json')
    primary={t['name']:t['primary_key'][0] for t in schema['tables']}
    connection=sqlite3.connect('file:'+(output/'checkpoints.sqlite3').as_posix()+'?mode=ro',uri=True)
    hashes={t:{} for t in tables};seen=set();mirror=0
    try:
        for stage,payload,checksum,stored_count in connection.execute('SELECT name,payload,checksum,row_count FROM stages'):
            if hashlib.sha256(payload.encode()).hexdigest()!=checksum or manifest['stage_checksums'].get(stage)!=checksum:raise ValueError('checkpoint corruption')
            seen.add(stage);value=json.loads(payload);count=sum(map(len,value['tables'].values()));mirror+=count
            if count!=stored_count:raise ValueError('checkpoint row count mismatch')
            for table,rows in value['tables'].items():
                for r in rows:
                    key=r[primary[table]]
                    if key in hashes[table]:raise ValueError('duplicate checkpoint business row')
                    hashes[table][key]=hashlib.sha256(encode(r)).digest()
        if seen!=set(manifest['stage_checksums']):raise ValueError('checkpoint inventory mismatch')
        # Accepted master rows are a separately verified immutable input, not checkpoint copies.
        for table,rows in master.items():
            for r in rows:
                key=r[primary[table]]
                if key in hashes[table]:raise ValueError('master duplicated by checkpoint')
                hashes[table][key]=hashlib.sha256(encode(r)).digest()
        for table,rows in tables.items():
            if len(rows)!=len(hashes[table]):raise ValueError('checkpoint/canonical count differs')
            for r in rows:
                if hashes[table].get(r[primary[table]])!=hashlib.sha256(encode(r)).digest():raise ValueError('checkpoint/canonical row differs')
    finally:connection.close()
    del hashes
    cp=read(ROOT/'contracts/clinical-history-policy.json');cp['new_business_tables']+=['bed_event','facility_day_driver']
    cp.update(site_transport_minutes=cfg['site_transport_minutes'],site_transport_handover_max_minutes=cfg['site_transport_handover_max_minutes'])
    clinical=IntegratedClinicalValidator(tables,schema,read(ROOT/'config/clinical-history-generation.json'),cp,master).run()
    operations=OperationalValidator(tables,schema,cfg,manifest['simulation']).run()
    body,selection=render_operations(tables,cfg)
    if (output/'operational-review-sample.md').read_bytes()!=body.encode():raise ValueError('operational review differs')
    review=review_gate(selection,read(review_path) if Path(review_path).exists() else None)
    defects=clinical['defects']+operations['defects']
    status='BLOCKED' if defects else 'OPERATIONAL_FLOW_PASSED' if review['status']=='PASS' else 'REVIEW_PENDING'
    if manifest['rows_by_table']!={t:len(r) for t,r in tables.items()} or manifest['business_rows']!=sum(map(len,tables.values())):raise ValueError('manifest row totals differ')
    if mirror!=manifest['checkpoint_mirror_rows'] or manifest['physical_serialized_rows']!=manifest['business_rows']+mirror+selection['mirror_rows']:raise ValueError('physical mirror accounting differs')
    if (output/'manifest.json').read_bytes()!=original:raise ValueError('candidate changed during inspection')
    return {'gate_status':status,'artifact_integrity':'PASS','business_sha256':manifest['business_sha256'],'clinical':clinical,'operations':operations,
            'defects':defects,'review':review,'review_selection':selection,'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/operational-flow');p.add_argument('--report',type=Path);a=p.parse_args()
    try:result=inspect_operations(a.output)
    except Exception as exc:result={'gate_status':'BLOCKED','error':str(exc)}
    if a.report:a.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('gate_status','artifact_integrity','error') if k in result}));sys.exit(0 if result['gate_status']=='OPERATIONAL_FLOW_PASSED' else 2)
