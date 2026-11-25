import re
from .common import instant,config

def within_recency_window(item,now):
 window=config('ranking')['freshness_hours'].get(item['content_type'],0)
 age=(now-instant(item['published_at'])).total_seconds()/3600
 return window>0 and 0<=age<=window

def eligibility(item,now):
 reason=None
 # Collection assigns this field before an item can enter the live pipeline.
 # Directly supplied historical evaluations keep their prior policy context.
 item.setdefault('topic_outcome','KEEP');item.setdefault('topic_rule','not evaluated by collection filter')
 routine=item['source_tier']=='P' and item['event_type'] in config('ranking').get('top_excluded_event_types',[])
 if routine and item['topic_outcome']=='DROP':item['topic_outcome']='KEEP';item['topic_rule']='authoritative routine disclosure retained in full edition'
 if item['content_type']=='pointer':reason='Pointer content is not a story candidate'
 elif item['source_tier'] in ('T','X'):reason='Discovery-only or excluded publisher'
 elif item['content_type'] in ('promotional','opinion'):reason='Promotion or opinion is not eligible news'
 elif re.search(r'\b(?:10x|price target|buy now|sell now|buy|sell|hold)\b',item['original_title'],re.I):reason='Recommendation or outcome claim excluded'
 elif item['topic_outcome']=='DROP' and not routine:reason='Outside financial topic scope: '+item['topic_rule']
 elif item['event_type']=='other' and not item.get('substantive_reviewed'):reason='Unclassified or administrative material requires substantive review'
 elif item['event_type']=='filing' and item['instrument_context'].get('filing_form') not in ('10-K','10-Q','20-F','8-K','6-K') and not item.get('substantive_reviewed'):reason='Filing substance unverified'
 elif item['original_language'] not in ('en','no') or item.get('display_language',item['original_language']) not in ('en','no'):reason='Unsupported or unknown display language'
 elif item['collection_status']!='SUCCEEDED':reason='Source collection did not succeed'
 elif (now-instant(item['published_at'])).total_seconds()<0:reason='Future publication time'
 elif not within_recency_window(item,now):reason='Outside content freshness window'
 elif 'funds' in item['asset_classes'] and not all(item['instrument_context'].get(k) for k in ('share_class','document_date')):reason='Share class/date unverified'
 elif 'crypto' in item['asset_classes'] and item['instrument_context'].get('crypto_evidence') not in ('regulator','on_chain','independent_reporting'):reason='Developer/exchange claims need separate verification'
 elif 'commodities' in item['asset_classes'] and item['instrument_context'].get('market') not in ('physical','futures'):reason='Physical/futures context unknown'
 elif 'derivatives' in item['asset_classes'] and not item['instrument_context'].get('exchange_verified'):reason='Exchange evidence unverified'
 item['eligibility']='REJECTED' if reason else ('VERIFIED' if item['source_tier']=='P' and item['primary_source_links'] else 'ATTRIBUTED' if item['source_tier']=='S' else 'REJECTED')
 item['eligibility_reason']=reason or ('Primary publication supports the event; issuer claims remain attributed' if item['eligibility']=='VERIFIED' else 'Single accountable secondary source; no independent corroboration claimed')
 return item
