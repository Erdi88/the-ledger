"""Validate generated output, archive hashes, fixture boundaries and deployment size."""
import argparse
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from collector.common import load,digest
from collector.schema import validate

def verify(root,deploy=False):
 root=pathlib.Path(root);latest=load(root/'site/data/latest.json')
 if latest is None:raise ValueError('no generated edition')
 validate(latest)
 if deploy and (latest['fixture'] or not latest['deployable']):raise ValueError('not a deployable live edition')
 for row in load(root/'site/data/archive.json',[]):
  if row['path']!='editions/'+row['date']+'.json':raise ValueError('archive path')
  original=root/row['path'];copy=root/'site'/row['path']
  if digest(original.read_text())!=row['sha256'] or original.read_bytes()!=copy.read_bytes():raise ValueError('archive integrity')
  validate(load(original))
 for c in load(root/'site/data/corrections.json',[]):
  from collector.common import instant
  from collector.normalize import canonical
  instant(c['corrected_at']);canonical(c['source_url'])
  if not c['description'] or not c['reviewed_by']:raise ValueError('correction lacks review')
  original=load(root/'editions'/f"{c['edition_date']}.json")
  if c['story_id'] not in [s['id'] for s in original['stories']]:raise ValueError('correction target missing')
 size=sum(p.stat().st_size for p in (root/'site').rglob('*') if p.is_file())
 if size>10_000_000:raise ValueError('site exceeded 10 MB local budget; review archive retention before deploy')
 return {'valid':True,'deployable':latest['deployable'],'fixture':latest['fixture'],'site_bytes':size}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--deploy',action='store_true');a=p.parse_args()
 print(json.dumps(verify(a.root,a.deploy)))
