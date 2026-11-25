"""Activation is separate from reachability: fail closed on missing review metadata."""
import datetime as dt
from .http import check_url

def validate_source(source):
 required=('id','publisher','tier','content_type','asset_classes','adapter','url','enabled','license_note','added_on','last_reviewed','critical','cadence_type','health_check','max_staleness','max_silence','baseline_item_count')
 if any(k not in source for k in required):raise ValueError('source registry fields missing')
 if not source['id'].startswith('fixture-') and any(k not in source for k in ('scope','display_language')):raise ValueError('source scope/display language missing')
 if source.get('scope','broad') not in ('broad','single_entity'):raise ValueError('invalid source scope')
 if source.get('display_language',source.get('language')) not in ('en','no','unknown'):raise ValueError('invalid display language')
 if source.get('policy_status')=='disabled_by_policy' and source.get('enabled'):raise ValueError('source is disabled by policy: '+str(source.get('policy_reason','')))
 for candidate in source.get('allowlist_candidates',[]):
  if candidate.get('approval_status')!='needs human approval' or candidate.get('active') is not False or candidate.get('domain') in source.get('allowed_domains',[]):raise ValueError('candidate allowlist entry must remain inactive pending human approval')
 if not source['enabled']:return
 if not source.get('terms_approved') or not source['last_reviewed'] or not source.get('terms_url') or source['license_note'].startswith('UNVERIFIED'):raise ValueError('documented source/terms review required')
 dt.date.fromisoformat(source['last_reviewed'])
 check_url(source['url'],source['allowed_domains']);check_url(source['terms_url'],source['allowed_domains'])
 if source['tier']=='S' and not source.get('corrections_policy_url'):raise ValueError('secondary source corrections policy required')
 if source['cadence_type'] not in ('regular','irregular') or source['health_check']!=('freshness' if source['cadence_type']=='regular' else 'availability'):raise ValueError('cadence/health policy mismatch')
 if source['baseline_item_count']<1:raise ValueError('reviewed baseline required')
 if source['adapter'] not in ('rss','atom','json','sec'):raise ValueError('adapter NOT BUILT')
