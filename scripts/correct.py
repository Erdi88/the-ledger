"""Append a reviewed, timestamped correction; never rewrite an edition."""
import argparse,pathlib,sys,datetime as dt
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from collector.common import load,atomic,stamp,UTC
from collector.normalize import canonical
p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--edition',required=True);p.add_argument('--story',required=True);p.add_argument('--description',required=True);p.add_argument('--source',required=True);p.add_argument('--reviewed-by',required=True);a=p.parse_args()
root=pathlib.Path(a.root);edition=load(root/'editions'/f'{a.edition}.json')
if not edition or a.story not in [s['id'] for s in edition['stories']]:raise SystemExit('No such edition/story')
path=root/'site/data/corrections.json';rows=load(path,[])
rows.append({'edition_date':a.edition,'story_id':a.story,'description':a.description,'source_url':canonical(a.source),'reviewed_by':a.reviewed_by,'corrected_at':stamp(dt.datetime.now(UTC))})
atomic(path,rows)
print('Correction appended; original edition unchanged. Validate before publishing.')
