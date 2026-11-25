"""Descriptions are metadata-derived. No unreviewed mechanism is published as explanation."""
from .common import ROOT,load

def explain(item,glossary):
 rationale=item.get('official_rationale')
 if rationale and item['source_tier']=='P' and rationale.get('source_url') in item['primary_source_links'] and rationale.get('reviewed') and rationale.get('quote') and rationale['quote'] in item['permitted_excerpt']:
  return {'origin':'ATTRIBUTED OFFICIAL EXPLANATION','text':f"{item['publisher']} states: “{rationale['quote']}”",'source_url':rationale['source_url']}
 match=next((g for g in glossary if item['event_type'] in g['event_types'] and g['review_status']=='reviewed'),None)
 if match:return {'origin':'REVIEWED EDUCATIONAL CONTEXT','text':match['explanation']+' This describes a general mechanism; this event’s effects are unknown.','source_url':match['url']}
 return {'origin':'UNAVAILABLE','text':'Explanation unavailable today','source_url':item['canonical_url']}

def prepare(item,glossary):
 item['what_happened']=f"{item['publisher']} published: {item['original_title']}"
 item['why_it_matters']=explain(item,glossary);item['explanation_source']=item['why_it_matters']['origin']
 item['what_confirmed']='The source published the linked document. Its claims remain attributable to the publisher.' if item['eligibility']=='VERIFIED' else f"Reported by {item['publisher']}; independent confirmation unavailable."
 item['what_uncertain']='Broader effects are unknown. No single cause established for any price movement.'
 return item

def learning(top,glossary,date):
 for item in top:
  for entry in glossary:
   if item['event_type'] in entry['event_types']:return {**entry,'tied_to':item['id'],'context':'Related to a featured story'}
 return {**glossary[int(date.replace('-',''))%len(glossary)],'tied_to':None,'context':"Not tied to today's news"}
