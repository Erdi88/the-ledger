"""Executable strict checks at every publication boundary."""
from .common import instant,OSLO
from .normalize import canonical
STATES={'NOT_CHECKED','PARTIAL','CHECKED_WITH_STORIES','CHECKED_QUIET'}
def validate(edition):
 if edition.get('schema_version')!=1:raise ValueError('schema version')
 now=instant(edition['edition_at'])
 if edition['date']!=now.astimezone(OSLO).date().isoformat():raise ValueError('edition date is not Oslo date')
 if edition['status'] not in ('FULL','PARTIAL'):raise ValueError('edition status')
 if edition['verification_status'] not in ('LIVE-VERIFIED','TESTED-OFFLINE'):raise ValueError('verification status')
 if edition['fixture'] and edition['deployable']:raise ValueError('fixture cannot deploy')
 from .coverage import publication_rule
 rule=publication_rule(edition['coverage'])
 if edition['publication_allowed']!=rule['allowed'] or edition['status']!=rule['status'] or edition['missing_categories']!=rule['missing']:raise ValueError('publication rule mismatch')
 if edition['deployable']!=(rule['allowed'] and not edition['fixture']):raise ValueError('deployable flag mismatch')
 for paper in edition['research_shelf']:
  if paper['fixture']!=edition['fixture']:raise ValueError('mixed research fixture/live')
  instant(paper['published_at']);canonical(paper['url'])
 ids=[]
 for item in edition['stories']:
  ids.append(item['id'])
  if not item['original_title'] or item['canonical_url']!=canonical(item['canonical_url']):raise ValueError('canonical metadata')
  if item['eligibility'] not in ('VERIFIED','ATTRIBUTED'):raise ValueError('ineligible news')
  if item.get('display_language',item.get('original_language')) not in ('en','no'):raise ValueError('unsupported story display language')
  if item['fixture']!=edition['fixture'] or item['provenance']['fixture']!=edition['fixture']:raise ValueError('mixed fixture and live')
  if len(item['permitted_excerpt'].split())>25:raise ValueError('excerpt limit')
  if item['published_at']>item['retrieved_at']:raise ValueError('publication chronology')
  for field in ('published_at','retrieved_at','event_at','corrected_at'):
   if item.get(field):
    instant(item[field])
    if not item[field].endswith('Z'):raise ValueError('UTC timestamp required')
  if not item['provenance']['document_id'] or not item['provenance']['source_url']:raise ValueError('provenance missing')
  for identifier in item['identifiers']:
   if not identifier.get('verified') or not identifier.get('source_url'):raise ValueError('unverified identifier')
   if 'ticker' in identifier and not identifier.get('mic'):raise ValueError('ticker requires MIC')
  if item['why_it_matters']['origin'] not in ('ATTRIBUTED OFFICIAL EXPLANATION','REVIEWED EDUCATIONAL CONTEXT','UNAVAILABLE'):raise ValueError('explanation origin')
 if len(ids)!=len(set(ids)):raise ValueError('duplicate story IDs')
 if len(edition['top_ids'])>5 or len(set(edition['top_ids']))!=len(edition['top_ids']) or not set(edition['top_ids'])<=set(ids):raise ValueError('Top 5 references')
 if set(edition['coverage'])!={'equities','funds','crypto','macro','bonds','fx','commodities','derivatives'}:raise ValueError('category set')
 for state in edition['coverage'].values():
  if state['state'] not in STATES or not isinstance(state['degraded'],bool):raise ValueError('coverage state')
  if state['state'].startswith('CHECKED_') and not state['checked_sources']:raise ValueError('checked without sources')
  instant(state['checked_at'])
 return True
