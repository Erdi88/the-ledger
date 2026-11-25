"""Immutable editions and an atomic latest pointer; safe restart after partial writes."""
import json
import shutil
from pathlib import Path
from .common import atomic,load,digest,ROOT
from .schema import validate

def assets(root):
 site=Path(root)/'site';site.mkdir(parents=True,exist_ok=True)
 for name in ('index.html','style.css','app.js','.nojekyll'):
  src=ROOT/'site'/name
  if src.exists() and src.resolve()!=(site/name).resolve():shutil.copyfile(src,site/name)
 filtered=Path(root)/'data/filtered_out.json'
 if filtered.exists():
  (site/'data').mkdir(parents=True,exist_ok=True);shutil.copyfile(filtered,site/'data/filtered_out.json')
 return site

def publish(edition,root,reason):
 validate(edition);root=Path(root);site=assets(root)
 atomic(root/'data'/'candidate.json',edition)
 latest=load(site/'data/latest.json')
 allowed=edition['publication_allowed']
 if not allowed:
  atomic(site/'data/status.json',{'stale':True,'reason':reason,'attempted_at':edition['edition_at'],'missing':edition['missing_categories']})
  if not latest:atomic(site/'data/latest.json',edition) # visibly nondeployable first-run local candidate
  return False
 archive=root/'editions'/f"{edition['date']}.json";archive.parent.mkdir(parents=True,exist_ok=True)
 if archive.exists():
  existing=load(archive)
  if existing!=edition:raise ValueError('immutable edition already exists; use correction overlay')
 else:
  # File lock in collector serializes local runs. Exclusive create forbids overwrite.
  with archive.open('x') as f:json.dump(edition,f,ensure_ascii=False,indent=2);f.write('\n')
 target=site/'editions'/archive.name;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and target.read_bytes()!=archive.read_bytes():raise ValueError('archive copy changed')
 if not target.exists():shutil.copyfile(archive,target)
 records=[]
 for path in sorted((root/'editions').glob('*.json'),reverse=True):
  records.append({'date':path.stem,'path':'editions/'+path.name,'sha256':digest(path.read_text())})
 atomic(site/'data/archive.json',records)
 atomic(site/'data/latest.json',edition)
 atomic(site/'data/status.json',{'stale':False,'reason':None,'attempted_at':edition['edition_at'],'missing':[]})
 if not (site/'data/corrections.json').exists():atomic(site/'data/corrections.json',[])
 return True
