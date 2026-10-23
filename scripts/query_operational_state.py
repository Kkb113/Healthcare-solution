"""Read canonical event history as a bounded historical bed-availability projection."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from healthcare_synthetic.operational_queries import availability

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/operational-flow');p.add_argument('--at',required=True);p.add_argument('--known-at');p.add_argument('--sex',choices=('M','F','X','UNKNOWN'));p.add_argument('--isolation',action='store_true');a=p.parse_args()
    manifest=json.loads((a.output/'manifest.json').read_text())
    if manifest['status']!='OPERATIONAL_FLOW_PASSED':raise ValueError('query requires an operationally accepted candidate')
    tables={}
    for name in ('location','bed_event','encounter','patient'):
        meta=manifest['canonical_files'][name];file=(a.output/meta['file']).resolve()
        if a.output.resolve() not in file.parents:raise ValueError('query input escaped candidate')
        checksum=hashlib.sha256();rows=[];size=0
        with file.open('rb') as f:
            for line in f:checksum.update(line);size+=len(line);rows.append(json.loads(line))
        if checksum.hexdigest()!=meta['sha256'] or len(rows)!=meta['rows'] or size!=meta['bytes']:raise ValueError('query input checksum differs: '+name)
        tables[name]=rows
    request={'administrative_sex':a.sex,'isolation_required':a.isolation,'allowed_services':['MEDICINE','SURGERY']} if a.sex else None
    result=availability(tables,a.at,a.known_at,request)
    print(json.dumps(result,indent=2))
