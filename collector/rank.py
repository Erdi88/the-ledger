from .common import config,instant

def score(item,now,seen_documents=()):
 policy=config('ranking');event=item['event_type'];baseline=policy['baseline'].get(event,1)
 modifiers=[]
 for m in item.get('evidence_modifiers',[]):
  if m.get('kind') in ('surprise','systemic_scale','situation_changed','stated_magnitude') and m.get('evidence_text') and m.get('source_url') in item['primary_source_links']:
   modifiers.append(m)
 significance=min(5,baseline+min(2,len(modifiers)))
 age=max(0,(now-instant(item['published_at'])).total_seconds()/3600)
 window=policy['freshness_hours'][item['content_type']]
 timely=5 if age<=window*.1 else 4 if age<=window*.25 else 3 if age<=window*.5 else 2 if age<=window else 0
 components={'significance':significance,'novelty':5 if not any(key in seen_documents for key in (item['provenance']['document_id'],item['source_id']+':'+item['provenance']['document_id'],item['canonical_url'])) else (3 if item.get('material_update') else 0),'timeliness':timely,'breadth':min(5,1+len(item['asset_classes'])),'educational_value':policy['educational'].get(event,1)}
 item['score_components']=components;item['editorial_score']=round(sum(components[k]*v for k,v in policy['weights'].items()),3)
 item['ranking_reason']=f"{event.replace('_',' ')}: significance {significance}/5 ({len(modifiers)} documented modifiers), novelty {components['novelty']}/5, freshness {timely}/5, breadth {components['breadth']}/5, learning {components['educational_value']}/5."
 return item

def select_top(items,limit=5):
 excluded=set(config('ranking').get('top_excluded_event_types',[]))
 ranked=sorted((i for i in items if i['event_type'] not in excluded and i.get('topic_outcome')!='LOW_CONFIDENCE'),key=lambda i:(-i['editorial_score'],i['published_at'],i['id']))
 chosen=[];publishers={};assets={}
 for item in ranked:
  if publishers.get(item['publisher'],0)>=2 or any(assets.get(c,0)>=2 for c in item['asset_classes']):continue
  chosen.append(item);publishers[item['publisher']]=publishers.get(item['publisher'],0)+1
  for c in item['asset_classes']:assets[c]=assets.get(c,0)+1
  if len(chosen)==limit:return chosen
 # Only relax when there are too few eligible alternatives.
 for item in ranked:
  if item not in chosen:chosen.append(item)
  if len(chosen)==limit:break
 return chosen


def apply_overrides(items,overrides,now):
 """Overrides require an explicit dated editorial log and never change eligibility."""
 for override in overrides:
  if not all(override.get(k) for k in ('story_id','reason','editor','logged_at','expires_at')):raise ValueError('incomplete override log')
  if instant(override['logged_at'])>now:raise ValueError('future override')
  if instant(override['expires_at'])<now:continue
  adjustment=float(override.get('score_adjustment',0))
  if not -1<=adjustment<=1:raise ValueError('override adjustment out of bounds')
  for item in items:
   if item['id']==override['story_id']:
    item['editorial_override']=override
    item['editorial_score']=max(0,min(5,round(item['editorial_score']+adjustment,3)))
    item['ranking_reason']+=' Logged editorial adjustment: '+override['reason']
