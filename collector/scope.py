"""Gate 2 thresholds applied to health-verified, terms-approved source records."""
from .common import config

def evaluate(sources,healths,network_available):
 if not network_available:return {'decision':'OFFLINE_FIXTURE_BUILD','counts':{'macro_primary':0,'nordic':0,'substantive_equity':0,'overall':0}}
 good={h['source_id'] for h in healths if h['status']=='SUCCEEDED'}
 working=[s for s in sources if s['id'] in good and s['enabled'] and s['terms_approved'] and s['content_type']!='pointer']
 broad=[s for s in working if s.get('scope','broad')=='broad']
 counts={'macro_primary':sum(s['tier']=='P' and 'macro' in s['asset_classes'] for s in broad),'nordic':sum(s.get('nordic',False) for s in broad),'substantive_equity':sum('equities' in s['asset_classes'] and s.get('substance_verified') is True for s in broad),'overall':len(working)}
 full=all(counts[k]>=v for k,v in config('gonogo').items())
 return {'decision':'FULL_SCOPE' if full else 'DEFENSIBLE_NARROWER_SCOPE','counts':counts,'categories_with_working_sources':sorted({c for s in working for c in s['asset_classes']})}

def restrict(sources,items,result):
 """Narrow source/category maps before coverage; original registry stays unchanged."""
 import copy
 sources=copy.deepcopy(sources);items=copy.deepcopy(items)
 thresholds=config('gonogo');counts=result['counts']
 blocked=[]
 if counts['macro_primary']<thresholds['macro_primary']:blocked.append('macro')
 if counts['substantive_equity']<thresholds['substantive_equity']:blocked.append('equities')
 for source in sources:source['asset_classes']=[c for c in source['asset_classes'] if c not in blocked]
 for item in items:
  item['provenance']['original_asset_classes']=item['asset_classes'][:]
  item['asset_classes']=[c for c in item['asset_classes'] if c not in blocked]
  if not item['asset_classes']:item['collection_status']='OUTSIDE_VERIFIED_SCOPE'
 return sources,items
