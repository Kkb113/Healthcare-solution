"""Content-locked, restartable workforce and inventory candidate publication."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime,timezone
from decimal import Context,ROUND_HALF_UP,localcontext
from pathlib import Path

from .core import canonical,digest
from .clinical_pipeline import ROOT,load_master
from .engine import Store,atomic_json,check_budget,single_writer
from .resource_generation import coordinate_services
from .resource_workforce import WorkforceGenerator,bind_working_authors
from .resource_inventory import InventoryGenerator
from .resource_validation import ResourceClinicalValidator,ResourceOperationalValidator,ResourceValidator
from .resource_stock_validation import StockValidator

GRAPH={'coordination':(),'workforce':('coordination',),'clinical_binding':('coordination','workforce'),
       'inventory':('coordination','workforce','clinical_binding'),
       'validation':('coordination','workforce','clinical_binding','inventory')}


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def accepted_parent(cfg):
    path=(ROOT/cfg['parent_candidate']).resolve();gate=read(ROOT/'evidence/operational-flow/acceptance-gate.json');m=read(path/'manifest.json')
    if ROOT not in path.parents or m['status']!='OPERATIONAL_FLOW_PASSED' or gate['status']!='PASSED' or m['business_sha256']!=cfg['parent_business_sha256'] or gate['business_sha256']!=cfg['parent_business_sha256']:
        raise ValueError('accepted operational parent anchor mismatch')
    tables={};actual={p.relative_to(path).as_posix() for p in (path/'canonical').iterdir() if p.is_file()}
    if actual!={meta['file'] for meta in m['canonical_files'].values()}:raise ValueError('parent canonical inventory differs')
    for name,meta in m['canonical_files'].items():
        file=(path/meta['file']).resolve()
        if path not in file.parents:raise ValueError('parent file path escaped snapshot')
        sha=hashlib.sha256();size=0;rows=[]
        with file.open('rb') as stream:
            for line in stream:sha.update(line);size+=len(line);rows.append(json.loads(line))
        if sha.hexdigest()!=meta['sha256'] or size!=meta['bytes'] or len(rows)!=meta['rows']:raise ValueError('accepted parent checksum/count differs: '+name)
        tables[name]=rows
    if digest({k:v['sha256'] for k,v in sorted(m['canonical_files'].items())})!=m['business_sha256']:raise ValueError('parent file-map digest differs')
    return tables,m


def merge(parent,outputs):
    result=dict(parent)
    for value in outputs.values():result.update(value['tables'])
    return result


def locks(cfg,runtime):
    names=('core','engine','master_generation','master_pipeline','master_validation','clinical_pipeline','clinical_validation',
           'operational_validation','operational_review','resource_generation','resource_workforce','resource_inventory','resource_pipeline',
           'resource_validation','resource_stock_validation','resource_review')
    files=[ROOT/f'src/healthcare_synthetic/{name}.py' for name in names]
    files+=sorted((ROOT/'contracts/phase0').glob('*.json'))
    files+=[ROOT/p for p in ('contracts/resource-foundation-policy.json','contracts/clinical-history-policy.json','config/clinical-history-generation.json',
        'config/operational-flow-generation.json','evidence/operational-flow/acceptance-gate.json')]
    return {'files':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'runtime':runtime,
        'configuration_sha256':digest(cfg),'accepted_operational_sha256':cfg['parent_business_sha256']}


def validate_resources(tables,parent,schema,cfg,simulation):
    ccfg=read(ROOT/'config/clinical-history-generation.json');policy=read(ROOT/'contracts/clinical-history-policy.json')
    policy['new_business_tables']+=['bed_event','facility_day_driver','staff_shift','inventory_movement']
    ocfg=read(ROOT/'config/operational-flow-generation.json');policy.update(site_transport_minutes=ocfg['site_transport_minutes'],site_transport_handover_max_minutes=ocfg['site_transport_handover_max_minutes'])
    master={name:rows for name,rows in parent.items() if name not in ('encounter','appointment','clinical_event','bed_event','facility_day_driver')}
    # The baseline condition subset belongs to the immutable accepted master, not
    # every provisional source diagnosis regenerated during clinical integration.
    original_master,_,_=load_master(ccfg);master=original_master
    clinical=ResourceClinicalValidator(tables,schema,ccfg,policy,master).run()
    operations=ResourceOperationalValidator(tables,schema,ocfg,simulation).run()
    workforce=ResourceValidator(tables,schema,cfg,parent).run();stock=StockValidator(tables,cfg,parent).run()
    defects=[]
    for domain,result in [('clinical',clinical),('operations',operations),('workforce',workforce),('stock',stock)]:
        for failure in result['defects']:defects.append({'defect_id':digest([domain,failure])[:32],'severity':'P0','domain':domain,**failure})
    return {'clinical':clinical,'operations':operations,'workforce':workforce,'stock':stock,'defects':defects}


def run_resources(config_path=ROOT/'config/resource-foundation-generation.json',output_dir=ROOT/'output/resource-foundation',
                  review_path=ROOT/'reviews/resource-foundation-review.json',fail_stage=None,crash_stage=None):
    with localcontext(Context(prec=38,rounding=ROUND_HALF_UP)):
        return _run(Path(config_path),Path(output_dir).resolve(),Path(review_path),fail_stage,crash_stage)


def _run(config_path,output,review_path,fail_stage,crash_stage):
    from .resource_review import render_resources,review_gate
    cfg=read(config_path);baseline=read(ROOT/'config/resource-foundation-generation.json')
    if set(cfg)!=set(baseline) or cfg['profile']!='CONNECTED_WORKFORCE_AND_STOCK' or type(cfg['seed']) is not int or any(cfg[k]!=baseline[k] for k in cfg if k!='seed'):raise ValueError('reviewed resource profile/configuration changed')
    if ROOT not in output.parents or output.relative_to(ROOT).parts[0] not in ('output','data'):raise ValueError('candidate must remain in ignored workspace output/data')
    if fail_stage not in (None,*GRAPH) or crash_stage not in (None,*GRAPH):raise ValueError('unknown resource failure stage')
    parent,parent_manifest=accepted_parent(cfg);_,schema,runtime=load_master(read(ROOT/'config/clinical-history-generation.json'))
    source_locks=locks(cfg,runtime);review=read(review_path) if review_path.exists() else None
    validation_only={f'src/healthcare_synthetic/{name}.py' for name in ('resource_validation','resource_stock_validation','resource_review','operational_review','clinical_validation','master_validation')}
    generation_locks={**source_locks,'files':{k:v for k,v in source_locks['files'].items() if k not in validation_only}}
    local={s:digest({'locks':source_locks if s=='validation' else generation_locks,'review':review if s=='validation' else None}) for s in GRAPH}
    output.mkdir(parents=True,exist_ok=True)
    with single_writer(output/'run.lock'):
        if (output/'manifest.json').exists() and read(output/'manifest.json')['profile']!=cfg['profile']:raise ValueError('wrong candidate profile')
        manifest={'profile':cfg['profile'],'implementation_phase':5,'status':'RUNNING','locks':source_locks,'started_at':datetime.now(timezone.utc).isoformat(),
            'executed':[],'reused':[],'invalidated':[],'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}
        atomic_json(output/'manifest.json',manifest)
        for leaf in ('candidate-ready.json','validation-report.json','resource-review-sample.md'):(output/leaf).unlink(missing_ok=True)
        store=Store(output/'checkpoints.sqlite3');attempt=None
        try:
            cached=store.stages()
            for stage,r in cached.items():
                if stage not in GRAPH or hashlib.sha256(r['payload'].encode()).hexdigest()!=r['checksum']:raise ValueError('resource checkpoint corruption: '+stage)
            invalid={s for s,r in cached.items() if r['local_hash']!=local[s]}
            for s,parents in GRAPH.items():
                if set(parents)&invalid:invalid.add(s)
            with store.db:
                for s in invalid:store.db.execute('DELETE FROM stages WHERE name=?',(s,))
                store.db.execute("UPDATE attempts SET status='INTERRUPTED' WHERE status='RUNNING'")
                attempt=store.db.execute('INSERT INTO attempts(started,status) VALUES (?,?)',(manifest['started_at'],'RUNNING')).lastrowid
            manifest['invalidated']=sorted(invalid);outputs={};hashes={}
            for stage,parents in GRAPH.items():
                fingerprint=digest({'local':local[stage],'parents':{p:hashes[p] for p in parents}});old=cached.pop(stage,None)
                if old and stage not in invalid and old['input_hash']==fingerprint:
                    value=json.loads(old['payload']);hashes[stage]=old['checksum'];manifest['reused'].append(stage)
                else:
                    tables=merge(parent,outputs);run_id='resources-'+fingerprint[:24]
                    if stage=='coordination':value=coordinate_services(parent,cfg,run_id)
                    elif stage=='workforce':value=WorkforceGenerator(tables,cfg,run_id).plan().materialize()
                    elif stage=='clinical_binding':value=bind_working_authors(tables,cfg,run_id)
                    elif stage=='inventory':value=InventoryGenerator(tables,cfg,run_id).run()
                    else:
                        control=validate_resources(tables,parent,schema,cfg,parent_manifest['simulation']);_,selection=render_resources(tables,cfg)
                        control['review_selection']=selection;control['review']=review_gate(selection,review)
                        control['gate_status']='BLOCKED' if control['defects'] else 'RESOURCE_FOUNDATION_PASSED' if control['review']['status']=='PASS' else 'REVIEW_PENDING'
                        value={'tables':{},'controls':control}
                    check_budget(merge(parent,{**outputs,stage:value}),1958210,schema)
                    hashes[stage]=store.publish(stage,local[stage],fingerprint,value,fail=stage==fail_stage,crash=stage==crash_stage);manifest['executed'].append(stage)
                outputs[stage]=value;del old
                logging.getLogger(__name__).info('Resource stage %s: %s',stage,'reused' if stage in manifest['reused'] else 'executed')
            tables=merge(parent,outputs);control=outputs['validation']['controls'];canonical_dir=output/'canonical';canonical_dir.mkdir(exist_ok=True);files={}
            for table,rows in tables.items():
                primary=next(t['primary_key'][0] for t in schema['tables'] if t['name']==table)
                target=canonical_dir/(table.replace('_','-')+'.jsonl');temporary=target.with_suffix('.tmp');sha=hashlib.sha256();size=0
                with temporary.open('wb') as stream:
                    for row in sorted(rows,key=lambda r:r[primary]):line=(canonical(row)+'\n').encode();stream.write(line);sha.update(line);size+=len(line)
                temporary.replace(target);files[table]={'file':target.relative_to(output).as_posix(),'rows':len(rows),'bytes':size,'sha256':sha.hexdigest()}
            body,selection=render_resources(tables,cfg);(output/'resource-review-sample.md').write_text(body,encoding='utf-8',newline='\n');atomic_json(output/'validation-report.json',control)
            total=sum(map(len,tables.values()));mirrors=sum(r['row_count'] for r in store.stages().values())
            manifest.update(status=control['gate_status'],business_sha256=digest({k:v['sha256'] for k,v in sorted(files.items())}),canonical_files=files,
                rows_by_table={k:len(v) for k,v in tables.items()},business_rows=total,generated_business_tables=len(tables),release_business_tables=25,
                remaining_planned_rows=1958210-total,reserve_rows=41790,checkpoint_mirror_rows=mirrors,review_mirror_rows=selection['mirror_rows'],
                physical_serialized_rows=total+mirrors+selection['mirror_rows'],stage_checksums=hashes,simulation=parent_manifest['simulation'],
                trajectory_status='WORKFORCE_AND_STOCK_INTEGRATED',next_phase='Revenue cycle and financial reconciliation - not started')
            if manifest['status']=='RESOURCE_FOUNDATION_PASSED':atomic_json(output/'candidate-ready.json',{k:manifest[k] for k in ('status','business_sha256','full_dataset_accepted','solution_status')})
        except Exception as exc:manifest.update(status='FAILED',error=str(exc));raise
        finally:
            manifest['finished_at']=datetime.now(timezone.utc).isoformat()
            if attempt is not None:
                with store.db:store.db.execute('UPDATE attempts SET status=?,finished=?,manifest=? WHERE id=?',(manifest['status'],manifest['finished_at'],canonical(manifest),attempt))
            atomic_json(output/'manifest.json',manifest);store.close()
        return manifest
