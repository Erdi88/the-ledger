from .common import stamp,instant,config

def health(source,items,now,meta,previous=None):
 previous=previous or {};reason=None
 if meta.get('http_status') not in (200,304):reason='Invalid HTTP response'
 elif not items and source['cadence_type']=='regular':reason='Empty response'
 elif not items and not meta.get('structure_valid'):reason='Empty response without validated feed structure'
 elif not items and source['cadence_type']=='irregular' and not previous.get('last_nonempty_at'):
  reason='UNVERIFIED_EMPTY: no prior non-empty response recorded'
 elif items and len(items)<max(1,source['baseline_item_count']//4):reason='Implausible item count versus reviewed baseline'
 elif any(not i.get('original_title') or not i.get('canonical_url') or not i.get('published_at') for i in items):reason='Canary fields missing'
 if reason is None:
  newest=max((instant(i['published_at']) for i in items),default=None)
  threshold=source['max_staleness'] if source['cadence_type']=='regular' else source['max_silence']
  if newest is not None:
   age=(now-newest).total_seconds()/3600
   if age>threshold:reason=f'Frozen/silent beyond {threshold} hours'
   elif age<0:reason='Future item'
  elif source['cadence_type']=='irregular':
   last_nonempty=instant(previous['last_nonempty_at'])
   silence=(now-last_nonempty).total_seconds()/3600
   if silence<0:reason='Future last_nonempty_at timestamp'
   elif silence>source['max_silence']:reason=f"Frozen/silent beyond {source['max_silence']} hours"
 # A previously multi-item archive disappearing to one item is structural damage.
 if previous.get('item_count',0)>=4 and len(items)==1:reason='Archive structure collapsed'
 status='UNVERIFIED_EMPTY' if reason and reason.startswith('UNVERIFIED_EMPTY:') else 'SUCCEEDED' if reason is None else 'FAILED'
 ok=status=='SUCCEEDED'
 newest=max((instant(i['published_at']) for i in items),default=None)
 return {'source_id':source['id'],'publisher':source['publisher'],'status':status,'reason':reason,'checked_at':stamp(now),'last_success':stamp(now) if ok else previous.get('last_success'),'last_nonempty_at':stamp(now) if ok and items else previous.get('last_nonempty_at'),'failures':0 if ok else previous.get('failures',0)+1,'item_count':len(items),'newest_published_at':stamp(newest) if newest else previous.get('newest_published_at'),'publication_latency_hours':round((now-newest).total_seconds()/3600,2) if newest else None,**meta}

def coverage(sources,healths,items,now):
 result={};states={h['source_id']:h for h in healths}
 for category in config('coverage')['categories']:
  selected=[s for s in sources if s['enabled'] and s['content_type']!='pointer' and category in s['asset_classes']]
  good=[s for s in selected if states.get(s['id'],{}).get('status')=='SUCCEEDED']
  failed=[s for s in selected if s not in good];critical=[s for s in selected if s['critical']]
  broad_critical=[s for s in critical if s.get('scope','broad')=='broad']
  failed_critical=[s for s in critical if s not in good]
  qualifying=[i for i in items if category in i['asset_classes'] and i['source_id'] in {s['id'] for s in good} and i['eligibility'] in ('VERIFIED','ATTRIBUTED')]
  if not good:state='NOT_CHECKED'
  elif not broad_critical or failed_critical:state='PARTIAL'
  else:state='CHECKED_WITH_STORIES' if qualifying else 'CHECKED_QUIET'
  result[category]={'state':state,'degraded':state.startswith('CHECKED_') and any(not s['critical'] for s in failed),'checked_sources':[s['publisher'] for s in good],'failed_sources':[s['publisher'] for s in failed],'failed_critical_sources':[s['publisher'] for s in failed_critical],'checked_at':stamp(now),'reason':'No critical source configured' if good and not critical else 'No broad critical source configured' if good and not broad_critical else 'No sources succeeded or configured' if not good else None}
 return result

def publication_rule(states):
 cfg=config('coverage');missing=[c for c in cfg['critical_categories'] if not states[c]['state'].startswith('CHECKED_')]
 if not missing:return {'status':'FULL','allowed':True,'missing':[]}
 other=sum(v['state'].startswith('CHECKED_') for k,v in states.items() if k not in cfg['critical_categories'])
 return {'status':'PARTIAL','allowed':other>=cfg['minimum_other_checked'],'missing':missing}
