import argparse
import datetime as dt
import fcntl
import json
from pathlib import Path
from .common import ROOT,UTC,OSLO,config,load,atomic,stamp
from .http import Client
from .adapters import parse,feed_kind
from .normalize import normalize
from .eligibility import eligibility,within_recency_window
from .deduplicate import cluster
from .rank import score,select_top
from .coverage import health,coverage,publication_rule
from .editorial import prepare,learning
from .publish import publish
from .topic import topic_decision


def collect_source(source,now,cache,previous,filtered_out=None,filter_metrics=None):
 meta={};start=__import__('time').monotonic()
 try:
  from .registry import validate_source
  validate_source(source)
  client=Client(source,cache);body,cached,meta=client.fetch()
  if cached is not None:
   items=cached
   for item in items:item['retrieved_at']=stamp(now);item['provenance']['retrieved_at']=stamp(now)
  else:
   if source['adapter'] in ('rss','atom') and feed_kind(body)=='feed_index':
    raise ValueError('Feed index is not an article feed')
   items=[normalize(row,source,now) for row in parse(body,source)]
  meta['structure_valid']=True
  state=health(source,items,now,meta,previous)
  if state['status']=='SUCCEEDED':
   if body is not None:client.save(items)
   routine_types=set(config('ranking').get('top_excluded_event_types',[]))
   kept=[]
   for item in items:
    if filter_metrics is not None:filter_metrics['total']+=1
    if source['content_type']=='pointer':decision={'outcome':'DROP','rule':'source content type is pointer'}
    elif not within_recency_window(item,now):decision={'outcome':'DROP','rule':'outside configured content-type recency window'}
    elif source['tier']=='P' and source['content_type']=='official_disclosure':decision={'outcome':'KEEP','rule':'official financial authority publication; keyword topic filter applies to secondary reporting only'}
    elif source['tier']=='P' and item['event_type'] in routine_types:decision={'outcome':'KEEP','rule':'authoritative routine disclosure retained in full edition'}
    else:decision=topic_decision(item['original_title'],item['canonical_url'],source)
    item['topic_outcome']=decision['outcome'];item['topic_rule']=decision['rule'];item['topic_matched_terms']=decision.get('matched_terms',[])
    if decision['outcome']=='DROP':
     if filtered_out is not None:filtered_out.append({'source_id':source['id'],'publisher':item['publisher'],'headline':item['original_title'],'link':item['canonical_url'],'published_at':item['published_at'],'retrieved_at':item['retrieved_at'],'outcome':'DROP','rule':decision['rule'],'matched_terms':decision.get('matched_terms',[])})
    else:kept.append(item)
   return kept,state
  return [],state
 except Exception as exc:
  return [],{'source_id':source['id'],'publisher':source['publisher'],'status':'FAILED','reason':str(exc),'checked_at':stamp(now),'last_success':previous.get('last_success'),'last_nonempty_at':previous.get('last_nonempty_at'),'failures':previous.get('failures',0)+1,'item_count':0,'http_status':meta.get('http_status'),'latency_ms':round((__import__('time').monotonic()-start)*1000,1),'publication_latency_hours':None}

def make_edition(items,sources,healths,now,fixture=False,previous=None,filter_summary=None):
 glossary=load(ROOT/'data/glossary.json');previous=previous or {}
 seen=previous.get('_seen',[])+[key for i in previous.get('stories',[]) for key in (i['source_id']+':'+i['provenance']['document_id'],i['canonical_url'])]
 evaluated=[eligibility(i,now) for i in items]
 queue=[i for i in evaluated if i['eligibility']=='REJECTED']
 clustered=cluster([i for i in evaluated if i['eligibility'] in ('VERIFIED','ATTRIBUTED')]);queue += [i for i in clustered if i['eligibility']=='DISPUTED']
 eligible=[prepare(score(i,now,seen),glossary) for i in clustered if i['eligibility'] in ('VERIFIED','ATTRIBUTED')]
 # A previously published unchanged event cannot become news merely by rediscovery.
 eligible=[i for i in eligible if i['score_components']['novelty']>0]
 states=coverage(sources,healths,eligible,now);rule=publication_rule(states)
 from .rank import apply_overrides
 apply_overrides(eligible,config('editorial')['overrides'],now)
 top=select_top(eligible);stories=sorted(eligible,key=lambda i:(-i['editorial_score'],i['id']))[:config('editorial')['max_edition']]
 # Ensure diversity-selected stories survive the full edition size cap.
 for i in top:
  if i not in stories:
   replace=next(j for j in reversed(range(len(stories))) if stories[j] not in top)
   stories[replace]=i
 date=now.astimezone(OSLO).date().isoformat()
 shelf=load(ROOT/'data/research_shelf.json',[])
 shelf=[i for i in shelf if i['fixture']==fixture and i.get('approved') and i['published_at']<=stamp(now)]
 # Rotate at ISO week boundaries, preserving stable ordering within a week.
 week=now.astimezone(OSLO).isocalendar().week
 shelf=(shelf[week%len(shelf):]+shelf[:week%len(shelf)])[:3] if shelf else []
 edition={'schema_version':1,'date':date,'edition_at':stamp(now),'status':rule['status'],'fixture':fixture,'verification_status':'TESTED-OFFLINE' if fixture else 'LIVE-VERIFIED','deployable':rule['allowed'] and not fixture,'publication_allowed':rule['allowed'],'missing_categories':rule['missing'],'coverage':states,'filter_summary':filter_summary or {'filtered_count':0,'total_count':0},'stories':stories,'top_ids':[i['id'] for i in top],'learning':learning(top,glossary,date),'research_shelf':shelf,'corrections':[],'ranking_policy':config('ranking'),'editorial_overrides':config('editorial')['overrides']}
 if not items and not any(h['status']=='SUCCEEDED' for h in healths):edition['verification_status']='TESTED-OFFLINE'
 return edition,queue

def run(root,now,fixture=False):
 root=Path(root);(root/'data').mkdir(parents=True,exist_ok=True)
 with (root/'data/collector.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  old=load(root/'editions'/f'{now.astimezone(OSLO).date()}.json')
  if old:
   if old['fixture']!=fixture:raise ValueError('use a separate output directory for fixture and live runs')
   from .schema import validate
   validate(old)
   publish(old,root,'Recovered existing valid edition');return old
  previous=load(root/'site/data/latest.json',{})
  previous['_seen']=[]
  for archive in (root/'editions').glob('*.json'):
   for old_item in load(archive,{}).get('stories',[]):
    previous['_seen'].extend([old_item['source_id']+':'+old_item['provenance']['document_id'],old_item['canonical_url']])
  old_health={h['source_id']:h for h in load(root/'data/health.json',[])}
  if fixture:
   data=load(ROOT/'tests/fixtures/scenario.json');sources=data['sources'];items=[];healths=[]
   for source in sources:
    raw=[r for r in data['items'] if r['source_id']==source['id']]
    normalized=[]
    for row in raw:
     item=normalize(row,source,now,True)
     for key in ('event_key','origin_id','claims','instrument_context','official_rationale','evidence_modifiers'):
      if key in row:item[key]=row[key]
     normalized.append(item)
    healths.append(health(source,normalized,now,{'http_status':200,'latency_ms':0,'evidence':'FIXTURE'},old_health.get(source['id'])))
    items.extend(normalized)
  else:
   sources=config('sources');items=[];healths=[];cache=root/'data/cache';cache.mkdir(parents=True,exist_ok=True)
   # Retain only sanitized metadata, bounded by both age and size.
   files=sorted(cache.glob('*.json'),key=lambda p:p.stat().st_mtime,reverse=True);total=0
   for n,path in enumerate(files):
    total+=path.stat().st_size
    policy=config('editorial')
    if n>=policy['cache_max_files'] or total>policy['cache_max_bytes'] or now.timestamp()-path.stat().st_mtime>policy['cache_retention_days']*86400:path.unlink()
   filtered_out=[];filter_metrics={'total':0}
   for source in sources:
    if not source['enabled']:continue
    result,state=collect_source(source,now,cache,old_health.get(source['id'],{}),filtered_out,filter_metrics);items+=result;healths.append(state)
   atomic(root/'data/filtered_out.json',{'generated_at':stamp(now),'filtered_count':len(filtered_out),'total_count':filter_metrics['total'],'items':filtered_out})
  from .scope import evaluate,restrict
  scope=evaluate(sources,healths,not fixture and any(h.get('http_status') is not None for h in healths))
  if not fixture and scope['decision']!='FULL_SCOPE':sources,items=restrict(sources,items,scope)
  edition,queue=make_edition(items,sources,healths,now,fixture,previous,{'filtered_count':len(filtered_out) if not fixture else 0,'total_count':filter_metrics['total'] if not fixture else 0})
  atomic(root/'data/health.json',healths);atomic(root/'data/research_queue.json',queue)
  reason='Missing critical coverage: '+', '.join(edition['missing_categories'])
  published=publish(edition,root,reason)
  atomic(root/'data/run.json',{'at':stamp(now),'fixture':fixture,'verification_status':edition['verification_status'],'source_health':healths,'scope':scope,'coverage':edition['coverage'],'published_locally':published,'deployable':edition['deployable'],'reason':None if published else reason,'rejected_or_disputed':len(queue)})
  return edition
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='.');p.add_argument('--fixture',action='store_true');p.add_argument('--now');a=p.parse_args()
 from .common import instant
 now=instant(a.now) if a.now else dt.datetime.now(UTC)
 if a.fixture and Path(a.output).resolve()==ROOT:raise SystemExit('FIXTURE requires isolated --output build/fixture')
 edition=run(a.output,now,a.fixture)
 print(json.dumps({'date':edition['date'],'status':edition['status'],'fixture':edition['fixture'],'deployable':edition['deployable'],'stories':len(edition['stories']),'missing':edition['missing_categories']}))
