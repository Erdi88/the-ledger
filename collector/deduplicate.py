"""Conservative event identity; disagreement quarantines an entire cluster."""
import re
from .common import digest

def fingerprint(item):
 return (re.sub(r'\W+',' ',item['original_title'].lower()).strip(),item['published_at'][:10],item['event_type'])
def cluster(items):
 groups=[]
 for item in sorted(items,key=lambda x:(x['published_at'],x['id'])):
  keys={('url',item['canonical_url']),('doc',item['publisher'],item['provenance']['document_id']),('fingerprint',*fingerprint(item))}
  if item.get('event_key'):keys.add(('event',item['event_key'],item['event_type']))
  matches=[g for g in groups if g['keys']&keys]
  if matches:
   group=matches[0];group['items'].append(item);group['keys']|=keys
   for other in matches[1:]:group['items']+=other['items'];group['keys']|=other['keys'];groups.remove(other)
  else:groups.append({'keys':keys,'items':[item]})
 result=[]
 for group in groups:
  members=group['items'];first=dict(members[0]);claims=[claim for m in members for claim in m.get('claims',[])]
  seen={};conflicts=[]
  for claim in claims:
   # Date, unit/currency, definition and dataset must match before conflict comparison.
   key=tuple(claim.get(k) for k in ('metric','as_of','unit','definition','dataset'))
   if not all(key):continue
   if key in seen and str(seen[key]['value'])!=str(claim['value']):conflicts.extend([seen[key],claim])
   seen[key]=claim
  if conflicts:first['eligibility']='DISPUTED';first['eligibility_reason']='Comparable claims disagree; both retained for review'
  first['claims']=claims;first['disagreements']=conflicts
  first['cluster_sources']=[{'publisher':m['publisher'],'url':m['canonical_url'],'published_at':m['published_at'],'origin_id':m['origin_id']} for m in members]
  first['independent_origins']=sorted(set(m['origin_id'] for m in members))
  first['cluster_reason']='Canonical URL, publisher document ID, exact dated title, or reviewed event key; no name-only merge'
  first['cluster_id']=digest('|'.join(sorted(m['id'] for m in members)))[:24]
  result.append(first)
 return result
