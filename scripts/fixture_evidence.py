"""Write inspectable FIXTURE examples; never publication input."""
import json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'tests'))
from test_ledger import item,NOW
from collector.deduplicate import cluster
from collector.eligibility import eligibility
from collector.rank import score
from collector.common import ROOT,load,atomic,instant
from collector.gate import should_run
import tempfile
rows=[item(id=str(n),canonical_url=f'https://example.org/copy{n}',publisher=f'FIXTURE Syndicator {n}',event_key='FIXTURE-one-event',origin_id='FIXTURE-original') for n in range(5)]
claim={'metric':'profit','as_of':'2026-Q3','unit':'NOK','definition':'net','dataset':'FIXTURE','value':10,'source_url':'https://example.org/claim-a'}
conflict=cluster([item(claims=[claim]),item(id='b',claims=[{**claim,'value':11,'source_url':'https://example.org/claim-b'}])])[0]
results=[]
for event in load(ROOT/'tests/fixtures/historical.json'):
 now=instant(event['date']+'T23:00:00Z');v=score(item(published_at=event['date']+'T00:00:00Z',event_type=event['event_type'],asset_classes=event['assets']),now)
 results.append({**event,'score':v['editorial_score'],'components':v['score_components']})
triggers=[]
with tempfile.TemporaryDirectory() as temp:
 for day in ('2026-01-15','2026-07-15','2026-03-29','2026-10-25'):
  for hour in (4,5,6,8,10):
   now=instant(f'{day}T{hour:02}:00:00Z');ok,reason=should_run(now,temp)
   triggers.append({'utc':now.isoformat(),'passes_without_existing_edition':ok,'reason':reason})
atomic(ROOT/'evidence/fixture-examples.json',{'label':'FIXTURE: synthetic syndication, rejected promotion and conflicting claims; NOT natural live examples','cluster':cluster(rows)[0],'rejected':eligibility(item(content_type='promotional',original_title='FIXTURE promotional outcome claim'),NOW),'conflict':conflict,'historical_replays':results,'schedule_simulation':triggers})
print('Wrote evidence/fixture-examples.json (FIXTURE only)')
