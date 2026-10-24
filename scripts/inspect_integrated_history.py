"""Run full persisted-domain, independent consumer, PIT and realism checks."""
import argparse
import gc
import json
import sys
from decimal import Context,ROUND_HALF_UP,localcontext
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from healthcare_synthetic.integrated_generation import load_snapshot,read,schema,sha_file
from healthcare_synthetic.integrated_consumers import build_index,connect,profile
from healthcare_synthetic.integrated_validation import domain_controls,reconcile,point_in_time,inspection_dependencies
from healthcare_synthetic.engine import atomic_json

def inspect(candidate,output):
    output.mkdir(parents=True,exist_ok=True)
    before=inspection_dependencies()
    with localcontext(Context(prec=38,rounding=ROUND_HALF_UP)):
        domains=domain_controls(candidate);atomic_json(output/'domain-controls.json',domains)
        gc.collect()
        tables,manifest=load_snapshot(candidate)
        consumers=reconcile(tables);pit=point_in_time(tables)
        atomic_json(output/'consumer-controls.json',consumers);atomic_json(output/'point-in-time.json',pit)
        del tables;gc.collect()
        indexed=build_index(candidate,output/'consumer-index.sqlite3',schema())
        db=connect(output/'consumer-index.sqlite3')
        try:realism=profile(db)
        finally:db.close()
        atomic_json(output/'realism-profiles.json',realism)
        result={'status':'PASS' if domains['status']==consumers['status']==pit['status']==realism['status']=='PASS' else 'FAIL',
                'seed':manifest['seed'],'business_sha256':manifest['business_sha256'],'rows':manifest['business_rows'],
                'domain_checks':domains['checks_freshly_executed'],'domain_defects':domains['defects'],
                'consumer_controls':consumers,'point_in_time':pit,'index':indexed,
                'realism_checks':realism['checks'],'partitions':realism['partitions'],
                'artifacts':{name:{'sha256':sha_file(output/name),'bytes':(output/name).stat().st_size} for name in ('domain-controls.json','consumer-controls.json','point-in-time.json','realism-profiles.json')},
                'inspection_dependencies':before,'dependencies_unchanged':before==inspection_dependencies(),
                'full_dataset_accepted':False,'solution_status':'BLOCKED_FOR_SOLUTION'}
        if not result['dependencies_unchanged']:raise ValueError('inspection code/contracts/configuration changed during inspection')
        atomic_json(output/'inspection.json',result)
        return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=ROOT/'output/integrated-history')
    p.add_argument('--output',type=Path,default=ROOT/'output/integrated-validation');a=p.parse_args()
    r=inspect(a.candidate,a.output);print(json.dumps({k:r[k] for k in ('status','seed','rows','domain_checks','domain_defects','realism_checks')}));sys.exit(0 if r['status']=='PASS' else 1)
