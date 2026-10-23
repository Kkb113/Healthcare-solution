"""Restartable, source-bound financial foundation with fail-closed publication."""
from __future__ import annotations

import copy
import hashlib
import json
import logging
import platform
from datetime import datetime, timezone
from decimal import Context, ROUND_HALF_UP, localcontext
from importlib import metadata, resources
from pathlib import Path

from .core import canonical, digest
from .engine import Store, atomic_json, check_budget, single_writer
from .financial_billing import billing, claims
from .financial_postings import postings
from .financial_allocations import allocations
from .financial_planning import monthly

ROOT=Path(__file__).resolve().parents[2]
GRAPH={'billing':(), 'claims':('billing',), 'posting':('billing','claims'),
       'allocation':('billing','claims','posting'), 'planning':('billing','claims','posting'),
       'validation':('billing','claims','posting','allocation','planning')}
OWNERS={'billing':{'catalog_item','service_charge'},'claims':{'claim','claim_line','claim_event'},
        'posting':{'financial_posting'},'allocation':{'cost_allocation'},'planning':{'finance_monthly'},'validation':set()}
VALIDATION_ONLY={'src/healthcare_synthetic/financial_validation.py','src/healthcare_synthetic/financial_review.py','src/healthcare_synthetic/financial_oracles.py','src/healthcare_synthetic/financial_room_validation.py'}


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def finance_schema():
    schema=read(ROOT/'contracts/phase0/schema.json')
    for t in schema['tables']:
        if t['name']=='catalog_item':t['planned_rows']+=5
        elif t['name']=='claim':t['planned_rows']=58000
        elif t['name']=='claim_line':t['planned_rows']=117000
        elif t['name']=='claim_event':t['planned_rows']=220000
        elif t['name']=='cost_allocation':t['planned_rows']=165000
        elif t['name']=='clinical_condition':t['planned_rows']=85000
        elif t['name']=='inventory_movement':t['planned_rows']=55000
    return schema


def accepted_parent(cfg):
    path=(ROOT/cfg['parent_candidate']).resolve();gate=read(ROOT/'evidence/resource-foundation/acceptance-gate.json');manifest=read(path/'manifest.json')
    if ROOT not in path.parents or manifest['status']!='RESOURCE_FOUNDATION_PASSED' or gate['status']!='PASSED' or manifest['business_sha256']!=cfg['parent_business_sha256'] or gate['business_sha256']!=cfg['parent_business_sha256']:
        raise ValueError('accepted resource parent anchor mismatch')
    actual={p.relative_to(path).as_posix() for p in (path/'canonical').iterdir() if p.is_file()}
    if actual!={m['file'] for m in manifest['canonical_files'].values()}:raise ValueError('parent canonical inventory differs')
    tables={}
    for name,m in manifest['canonical_files'].items():
        file=(path/m['file']).resolve()
        if path not in file.parents:raise ValueError('parent path escaped snapshot')
        h=hashlib.sha256();size=0;rows=[]
        with file.open('rb') as stream:
            for line in stream:h.update(line);size+=len(line);rows.append(json.loads(line))
        if h.hexdigest()!=m['sha256'] or size!=m['bytes'] or len(rows)!=m['rows']:raise ValueError('parent checksum/count differs: '+name)
        tables[name]=rows
    if digest({k:v['sha256'] for k,v in sorted(manifest['canonical_files'].items())})!=manifest['business_sha256']:raise ValueError('parent file-map digest differs')
    return tables,manifest


def merge(parent,outputs):
    result=dict(parent)
    for value in outputs.values():result.update(value['tables'])
    return result


def locks(cfg):
    modules=('core','engine','master_generation','master_validation','clinical_validation','operational_validation','resource_stock_validation',
             'financial_common','financial_billing','financial_postings','financial_allocations','financial_planning','financial_pipeline','financial_validation','financial_review','financial_oracles','financial_room_validation')
    files=[ROOT/f'src/healthcare_synthetic/{m}.py' for m in modules]
    files+=sorted((ROOT/'contracts/phase0').glob('*.json'))
    files += [ROOT/'contracts/financial-history-policy.json',ROOT/'evidence/resource-foundation/acceptance-gate.json']
    runtime={'python':platform.python_version(),'implementation':platform.python_implementation(),'tzdata':metadata.version('tzdata'),
             'chicago_sha256':hashlib.sha256(resources.files('tzdata').joinpath('zoneinfo/America/Chicago').read_bytes()).hexdigest()}
    if runtime['python']!='3.10.10' or runtime['implementation']!='CPython' or runtime['tzdata']!='2025.2':raise ValueError('financial runtime differs')
    return {'files':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'runtime':runtime,
            'configuration_sha256':digest(cfg),'accepted_resource_sha256':cfg['parent_business_sha256']}


def run_financial(config_path=ROOT/'config/financial-history-generation.json',output_dir=ROOT/'output/financial-history',
                  review_path=ROOT/'reviews/financial-history-review.json',fail_stage=None,crash_stage=None):
    with localcontext(Context(prec=38,rounding=ROUND_HALF_UP)):
        return _run(Path(config_path),Path(output_dir).resolve(),Path(review_path),fail_stage,crash_stage)


def _run(config_path,output,review_path,fail_stage,crash_stage):
    from .financial_validation import validate_financial
    from .financial_review import render_financial,review_gate
    cfg=read(config_path);baseline=read(ROOT/'config/financial-history-generation.json')
    if set(cfg)!=set(baseline) or cfg['profile']!='CONNECTED_FINANCIAL_HISTORY' or type(cfg['seed']) is not int or any(cfg[k]!=baseline[k] for k in cfg if k!='seed'):raise ValueError('reviewed financial profile/configuration changed')
    if ROOT not in output.parents or output.relative_to(ROOT).parts[0] not in ('output','data'):raise ValueError('financial candidate must remain in ignored workspace output/data')
    if fail_stage not in (None,*GRAPH) or crash_stage not in (None,*GRAPH):raise ValueError('unknown financial failure stage')
    parent,parent_manifest=accepted_parent(cfg);schema=finance_schema();source_locks=locks(cfg);review=read(review_path) if review_path.exists() else None
    generation_locks={**source_locks,'files':{k:v for k,v in source_locks['files'].items() if k not in VALIDATION_ONLY}}
    local={s:digest({'locks':source_locks if s=='validation' else generation_locks,'review':review if s=='validation' else None}) for s in GRAPH}
    output.mkdir(parents=True,exist_ok=True)
    with single_writer(output/'run.lock'):
        if (output/'manifest.json').exists() and read(output/'manifest.json')['profile']!=cfg['profile']:raise ValueError('wrong candidate profile')
        manifest={'profile':cfg['profile'],'implementation_phase':6,'status':'RUNNING','locks':source_locks,'started_at':datetime.now(timezone.utc).isoformat(),
                  'executed':[],'reused':[],'invalidated':[],'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}
        atomic_json(output/'manifest.json',manifest)
        for name in ('candidate-ready.json','validation-report.json','financial-review-sample.md'):(output/name).unlink(missing_ok=True)
        store=Store(output/'checkpoints.sqlite3');attempt=None
        try:
            cached=store.stages()
            for s,r in cached.items():
                if s not in GRAPH or hashlib.sha256(r['payload'].encode()).hexdigest()!=r['checksum']:raise ValueError('financial checkpoint corruption: '+s)
            invalid={s for s,r in cached.items() if r['local_hash']!=local[s]}
            for s,parents in GRAPH.items():
                if set(parents)&invalid:invalid.add(s)
            with store.db:
                for s in invalid:store.db.execute('DELETE FROM stages WHERE name=?',(s,))
                store.db.execute("UPDATE attempts SET status='INTERRUPTED' WHERE status='RUNNING'")
                attempt=store.db.execute('INSERT INTO attempts(started,status) VALUES (?,?)',(manifest['started_at'],'RUNNING')).lastrowid
            manifest['invalidated']=sorted(invalid);outputs={};hashes={}
            functions={'billing':billing,'claims':claims,'posting':postings,'allocation':allocations,'planning':monthly}
            for stage,parents in GRAPH.items():
                fingerprint=digest({'local':local[stage],'parents':{p:hashes[p] for p in parents}});old=cached.pop(stage,None)
                if old and stage not in invalid and old['input_hash']==fingerprint:
                    value=json.loads(old['payload']);hashes[stage]=old['checksum'];manifest['reused'].append(stage)
                else:
                    tables=merge(parent,outputs);run_id='financial-'+fingerprint[:24]
                    if stage!='validation':value=functions[stage](tables,cfg,run_id)
                    else:
                        controls=validate_financial(tables,cfg,schema);_,selection=render_financial(tables,cfg)
                        controls['review_selection']=selection;controls['review']=review_gate(selection,review)
                        controls['gate_status']='BLOCKED' if controls['defects'] else 'FINANCIAL_HISTORY_PASSED' if controls['review']['status']=='PASS' else 'REVIEW_PENDING'
                        value={'tables':{},'controls':controls}
                    if set(value['tables'])!=OWNERS[stage]:raise ValueError('financial stage ownership differs')
                    check_budget(merge(parent,{**outputs,stage:value}),1995215,schema)
                    hashes[stage]=store.publish(stage,local[stage],fingerprint,value,fail=stage==fail_stage,crash=stage==crash_stage);manifest['executed'].append(stage)
                outputs[stage]=value;del old
                logging.getLogger(__name__).info('Financial stage %s: %s',stage,'reused' if stage in manifest['reused'] else 'executed')
            tables=merge(parent,outputs);controls=outputs['validation']['controls'];canonical_dir=output/'canonical';canonical_dir.mkdir(exist_ok=True);files={}
            for table,rows in tables.items():
                pk=next(t['primary_key'][0] for t in schema['tables'] if t['name']==table);target=canonical_dir/(table.replace('_','-')+'.jsonl');temp=target.with_suffix('.tmp');h=hashlib.sha256();size=0
                with temp.open('wb') as stream:
                    for r in sorted(rows,key=lambda r:r[pk]):line=(canonical(r)+'\n').encode();stream.write(line);h.update(line);size+=len(line)
                temp.replace(target);files[table]={'file':target.relative_to(output).as_posix(),'rows':len(rows),'bytes':size,'sha256':h.hexdigest()}
            body,selection=render_financial(tables,cfg);(output/'financial-review-sample.md').write_text(body,encoding='utf-8',newline='\n');atomic_json(output/'validation-report.json',controls)
            if locks(read(config_path))!=source_locks or (read(review_path) if review_path.exists() else None)!=review:raise ValueError('financial sources/configuration/review changed during generation')
            total=sum(map(len,tables.values()));mirrors=sum(r['row_count'] for r in store.stages().values())
            manifest.update(status=controls['gate_status'],business_sha256=digest({k:v['sha256'] for k,v in sorted(files.items())}),canonical_files=files,
                rows_by_table={k:len(v) for k,v in tables.items()},business_rows=total,generated_business_tables=len(tables),release_business_tables=25,
                remaining_planned_rows=1995215-total,reserve_rows=4785,catalog_extension_rows=5,checkpoint_mirror_rows=mirrors,review_mirror_rows=selection['mirror_rows'],
                physical_serialized_rows=total+mirrors+selection['mirror_rows'],stage_checksums=hashes,simulation=parent_manifest['simulation'],
                trajectory_status='FINANCIAL_HISTORY_INTEGRATED',next_phase='Source-system exports and delivery simulation - not started')
            if manifest['status']=='FINANCIAL_HISTORY_PASSED':atomic_json(output/'candidate-ready.json',{k:manifest[k] for k in ('status','business_sha256','full_dataset_accepted','solution_status')})
        except Exception as exc:manifest.update(status='FAILED',error=str(exc));raise
        finally:
            manifest['finished_at']=datetime.now(timezone.utc).isoformat()
            if attempt is not None:
                with store.db:store.db.execute('UPDATE attempts SET status=?,finished=?,manifest=? WHERE id=?',(manifest['status'],manifest['finished_at'],canonical(manifest),attempt))
            atomic_json(output/'manifest.json',manifest);store.close()
        return manifest
