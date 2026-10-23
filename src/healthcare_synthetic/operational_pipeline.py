"""Restartable, content-locked integrated patient-flow candidate."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from decimal import Context, ROUND_HALF_UP, localcontext
from pathlib import Path

from .clinical_pipeline import ROOT, load_master
from .core import canonical, digest
from .engine import Store, atomic_json, check_budget, single_writer
from .operational_demand import DemandGenerator
from .operational_generation import FlowSimulator, connect_site_transfers
from .operational_validation import OperationalValidator, IntegratedClinicalValidator
from .operational_review import render_operations, review_gate

GRAPH={'flow':(),'care_springfield':('flow',),'care_peoria':('flow',),'care_rockford':('flow',),
       'triage':('flow',),'drivers':(),'validation':('flow','care_springfield','care_peoria','care_rockford','triage','drivers')}

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def source_locks(cfg,runtime):
    # Explicit closure: future unrelated modules must not perturb this profile's metadata.
    names=('core','engine','master_generation','master_pipeline','master_validation','clinical_generation','clinical_pipeline',
           'clinical_validation','operational_demand','operational_generation','operational_timing','operational_pipeline','operational_validation','operational_review')
    paths=[ROOT/f'src/healthcare_synthetic/{name}.py' for name in names]
    paths+=sorted((ROOT/'contracts/phase0').glob('*.json'))
    paths+=[ROOT/p for p in ('contracts/operational-flow-policy.json','contracts/clinical-history-policy.json','contracts/reference-package-lock.json',
                            'config/clinical-history-generation.json','evidence/clinical-histories/acceptance-gate.json')]
    return {'files':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'runtime':runtime,
            'configuration_sha256':digest(cfg),'accepted_clinical_sha256':cfg['accepted_clinical_sha256']}

def verify_parent(cfg):
    gate=read(ROOT/'evidence/clinical-histories/acceptance-gate.json')
    path=(ROOT/cfg['accepted_clinical_candidate']).resolve()
    if ROOT not in path.parents:raise ValueError('clinical parent outside workspace')
    manifest=read(path/'manifest.json')
    if gate['status']!='PASSED' or manifest['status']!='CLINICAL_HISTORIES_PASSED' or gate['business_sha256']!=cfg['accepted_clinical_sha256'] or manifest['business_sha256']!=gate['business_sha256']:
        raise ValueError('accepted clinical anchor mismatch')
    if digest({k:v['sha256'] for k,v in sorted(manifest['canonical_files'].items())})!=gate['business_sha256']:raise ValueError('clinical file-map hash mismatch')
    actual={p.relative_to(path).as_posix() for p in (path/'canonical').iterdir() if p.is_file()}
    if actual!={v['file'] for v in manifest['canonical_files'].values()}:raise ValueError('clinical parent inventory differs')
    for name,meta in manifest['canonical_files'].items():
        file=(path/meta['file']).resolve()
        if path not in file.parents:raise ValueError('parent file escaped snapshot')
        sha=hashlib.sha256();size=rows=0
        with file.open('rb') as stream:
            for line in stream:sha.update(line);size+=len(line);rows+=1
        if sha.hexdigest()!=meta['sha256'] or size!=meta['bytes'] or rows!=meta['rows']:raise ValueError('accepted clinical file checksum/count mismatch: '+name)

def merge(master,outputs):
    tables=dict(master)
    for stage,value in outputs.items():
        for name,rows in value['tables'].items():
            if name in ('clinical_condition','clinical_event'):tables[name]=[*tables.get(name,[]),*rows]
            elif name in tables:raise ValueError('unexpected shared operational ownership: '+name)
            else:tables[name]=rows
    return tables

def validate_tables(tables,master,schema,cfg,simulation):
    clinical_cfg=read(ROOT/'config/clinical-history-generation.json');clinical_policy=read(ROOT/'contracts/clinical-history-policy.json')
    clinical_policy['new_business_tables']+=['bed_event','facility_day_driver']
    clinical_policy.update(site_transport_minutes=cfg['site_transport_minutes'],site_transport_handover_max_minutes=cfg['site_transport_handover_max_minutes'])
    clinical=IntegratedClinicalValidator(tables,schema,clinical_cfg,clinical_policy,master).run()
    operations=OperationalValidator(tables,schema,cfg,simulation).run()
    defects=clinical['defects']+[{'defect_id':digest(r)[:32],'severity':'P0',**r} for r in operations['defects']]
    return {'clinical':clinical,'operations':operations,'defects':defects}

def run_operations(config_path=ROOT/'config/operational-flow-generation.json',output_dir=ROOT/'output/operational-flow',
                   review_path=ROOT/'reviews/operational-flow-review.json',fail_stage=None,crash_stage=None):
    with localcontext(Context(prec=38,rounding=ROUND_HALF_UP)):
        return _run(Path(config_path),Path(output_dir).resolve(),Path(review_path),fail_stage,crash_stage)

def _run(config_path,output,review_path,fail_stage,crash_stage):
    cfg=read(config_path);baseline=read(ROOT/'config/operational-flow-generation.json')
    if set(cfg)!=set(baseline) or cfg['profile']!='OPERATIONAL_PATIENT_FLOW' or type(cfg['seed']) is not int:raise ValueError('operational profile contract mismatch')
    if any(cfg[k]!=baseline[k] for k in cfg if k!='seed'):raise ValueError('reviewed operational configuration changed')
    if ROOT not in output.parents or output.relative_to(ROOT).parts[0] not in ('output','data'):raise ValueError('candidate must be ignored workspace output/data')
    if fail_stage not in (None,*GRAPH) or crash_stage not in (None,*GRAPH):raise ValueError('unknown failure stage')
    verify_parent(cfg)
    ccfg=read(ROOT/'config/clinical-history-generation.json');master,schema,runtime=load_master(ccfg)
    ccfg={**ccfg,'seed':cfg['seed']};policy=read(ROOT/'contracts/clinical-history-policy.json')
    locks=source_locks(cfg,runtime);review=read(review_path) if review_path.exists() else None
    validation_only={'src/healthcare_synthetic/'+name+'.py' for name in ('clinical_validation','operational_validation','operational_review')}
    generation_locks={**locks,'files':{name:value for name,value in locks['files'].items() if name not in validation_only}}
    local={s:digest({'locks':locks if s=='validation' else generation_locks,'review':review if s=='validation' else None}) for s in GRAPH}
    output.mkdir(parents=True,exist_ok=True)
    with single_writer(output/'run.lock'):
        if (output/'manifest.json').exists() and read(output/'manifest.json')['profile']!=cfg['profile']:raise ValueError('wrong candidate profile')
        manifest={'profile':cfg['profile'],'implementation_phase':4,'status':'RUNNING','locks':locks,'executed':[],'reused':[],'invalidated':[],
                  'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION','started_at':datetime.now(timezone.utc).isoformat()}
        atomic_json(output/'manifest.json',manifest)
        for leaf in ('candidate-ready.json','validation-report.json','operational-review-sample.md'):(output/leaf).unlink(missing_ok=True)
        store=Store(output/'checkpoints.sqlite3');attempt=None
        try:
            old=store.stages()
            for s,r in old.items():
                if s not in GRAPH or hashlib.sha256(r['payload'].encode()).hexdigest()!=r['checksum']:raise ValueError('operational checkpoint corruption: '+s)
            invalid={s for s,r in old.items() if r['local_hash']!=local[s]}
            for s,parents in GRAPH.items():
                if set(parents)&invalid:invalid.add(s)
            with store.db:
                for s in invalid:store.db.execute('DELETE FROM stages WHERE name=?',(s,))
                store.db.execute("UPDATE attempts SET status='INTERRUPTED' WHERE status='RUNNING'")
                attempt=store.db.execute('INSERT INTO attempts(started,status) VALUES (?,?)',(manifest['started_at'],'RUNNING')).lastrowid
            for s in invalid:old.pop(s,None)
            manifest['invalidated']=sorted(invalid);outputs={};hashes={}
            site_codes={'care_springfield':'HSP-SPR','care_peoria':'HSP-PEO','care_rockford':'HSP-RFD'}
            facilities={r['facility_code']:r['facility_id'] for r in master['facility']}
            for stage,parents in GRAPH.items():
                fingerprint=digest({'local':local[stage],'parents':{p:hashes[p] for p in parents}})
                cached=old.pop(stage,None)
                if cached and cached['input_hash']==fingerprint:
                    value=json.loads(cached['payload']);hashes[stage]=cached['checksum'];manifest['reused'].append(stage)
                else:
                    g=DemandGenerator(merge(master,{p:outputs[p] for p in parents if p=='flow'}),ccfg,policy,'operations-'+fingerprint[:24],cfg)
                    if stage=='flow':
                        journeys=connect_site_transfers(g,g.journeys(),cfg['continuous_site_transfers'],cfg)
                        proposed=merge(master,{'journeys':{'tables':journeys}})
                        context_generator=DemandGenerator(proposed,ccfg,policy,'bookings-'+fingerprint[:24],cfg)
                        proposed.update(context_generator.appointments());proposed.update(context_generator.placement_assessments())
                        sim=FlowSimulator(proposed,g,cfg)
                        beds,controls=sim.run()
                        opening_ids={c['condition_version_id'] for c in master['clinical_condition']}
                        health=[r for r in sim.t['clinical_condition'] if r['condition_version_id'] not in opening_ids]
                        value={'tables':{'encounter':sim.t['encounter'],'clinical_condition':health,'appointment':sim.t['appointment'],'clinical_event':sim.t['clinical_event'],**beds},'controls':controls}
                    elif stage.startswith('care_'):value={'tables':g.care(facilities[site_codes[stage]]),'controls':{}}
                    elif stage=='triage':value={'tables':g.triage(),'controls':{}}
                    elif stage=='drivers':value={'tables':g.drivers(),'controls':{}}
                    else:
                        tables=merge(master,outputs);control=validate_tables(tables,master,schema,cfg,outputs['flow']['controls'])
                        _,selection=render_operations(tables,cfg)
                        control['review']=review_gate(selection,review);control['review_selection']=selection
                        control['gate_status']='BLOCKED' if control['defects'] else 'OPERATIONAL_FLOW_PASSED' if control['review']['status']=='PASS' else 'REVIEW_PENDING'
                        value={'tables':{},'controls':control}
                    check_budget(merge(master,{**outputs,stage:value}),1958210,schema)
                    hashes[stage]=store.publish(stage,local[stage],fingerprint,value,fail=stage==fail_stage,crash=stage==crash_stage)
                    manifest['executed'].append(stage)
                outputs[stage]=value
                logging.getLogger(__name__).info('Operational stage %s: %s',stage,'reused' if stage in manifest['reused'] else 'executed')
                del cached
            tables=merge(master,outputs);control=outputs['validation']['controls'];files={}
            canonical_dir=output/'canonical';canonical_dir.mkdir(exist_ok=True)
            for table,rows in tables.items():
                primary=next(t['primary_key'][0] for t in schema['tables'] if t['name']==table)
                file=canonical_dir/(table.replace('_','-')+'.jsonl');temp=file.with_suffix('.tmp');sha=hashlib.sha256();size=0
                with temp.open('wb') as stream:
                    for row in sorted(rows,key=lambda r:r[primary]):
                        line=(canonical(row)+'\n').encode();stream.write(line);sha.update(line);size+=len(line)
                temp.replace(file);files[table]={'file':file.relative_to(output).as_posix(),'rows':len(rows),'bytes':size,'sha256':sha.hexdigest()}
            body,selection=render_operations(tables,cfg)
            (output/'operational-review-sample.md').write_text(body,encoding='utf-8',newline='\n')
            atomic_json(output/'validation-report.json',control)
            total=sum(map(len,tables.values()));mirrors=sum(r['row_count'] for r in store.stages().values())
            manifest.update(status=control['gate_status'],business_sha256=digest({k:v['sha256'] for k,v in sorted(files.items())}),canonical_files=files,
                rows_by_table={k:len(v) for k,v in tables.items()},business_rows=total,generated_business_tables=len(tables),release_business_tables=25,
                remaining_planned_rows=1958210-total,reserve_rows=41790,checkpoint_mirror_rows=mirrors,review_mirror_rows=selection['mirror_rows'],
                physical_serialized_rows=total+mirrors+selection['mirror_rows'],stage_checksums=hashes,simulation=outputs['flow']['controls'],
                trajectory_status='CAPACITY_INTEGRATED_PENDING_WORKFORCE_INVENTORY',next_phase='Workforce, resources and inventory - not started')
            if manifest['status']=='OPERATIONAL_FLOW_PASSED':atomic_json(output/'candidate-ready.json',{k:manifest[k] for k in ('status','business_sha256','full_dataset_accepted','solution_status')})
        except Exception as exc:manifest.update(status='FAILED',error=str(exc));raise
        finally:
            manifest['finished_at']=datetime.now(timezone.utc).isoformat()
            if attempt is not None:
                with store.db:store.db.execute('UPDATE attempts SET status=?,finished=?,manifest=? WHERE id=?',(manifest['status'],manifest['finished_at'],canonical(manifest),attempt))
            atomic_json(output/'manifest.json',manifest);store.close()
        return manifest
