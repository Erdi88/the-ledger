import copy
import datetime as dt
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch,Mock
from collector.common import ROOT,UTC,instant,load,stamp,atomic
from collector.adapters import parse,date
from collector.normalize import normalize,canonical
from collector.eligibility import eligibility
from collector.deduplicate import cluster
from collector.rank import score,select_top
from collector.coverage import health,coverage,publication_rule
from collector.editorial import explain
from collector.collect import run,make_edition,collect_source
from collector.publish import publish
from collector.gate import should_run
from collector.schema import validate
from collector.http import check_url,public_addresses,Client,FetchError
from scripts.validate import verify
NOW=instant('2026-10-13T05:00:00Z')
DATA=load(ROOT/'tests/fixtures/scenario.json')
def source():return copy.deepcopy(DATA['sources'][0])
def item(**changes):
 value=normalize(DATA['items'][0],source(),NOW,True)
 value.update(changes);return value

def states():
 return {c:{'state':'NOT_CHECKED','degraded':False,'checked_sources':[],'failed_sources':[],'failed_critical_sources':[],'checked_at':stamp(NOW),'reason':None} for c in ('equities','funds','crypto','macro','bonds','fx','commodities','derivatives')}

class Parsing(unittest.TestCase):
 def test_rss_provenance(self):
  xml=b'<rss><channel><item><title>FIXTURE Title</title><link>https://example.org/a</link><guid>a</guid><pubDate>Tue, 13 Oct 2026 04:00:00 GMT</pubDate><description>&lt;b&gt;FIXTURE&lt;/b&gt; text</description></item></channel></rss>'
  raw=parse(xml,source())[0];v=normalize(raw,source(),NOW,True)
  self.assertEqual(v['provenance']['document_id'],'a');self.assertEqual(v['permitted_excerpt'],'FIXTURE text');self.assertEqual(v['original_title'],'FIXTURE Title')
 def test_atom_published_not_updated(self):
  s=source();s['adapter']='atom'
  xml=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>x</id><title>FIXTURE</title><published>2026-10-12T04:00:00Z</published><updated>2026-10-13T04:00:00Z</updated><link href="https://example.org/a"/></entry></feed>'
  self.assertEqual(parse(xml,s)[0]['published_at'],'2026-10-12T04:00:00Z')
  with self.assertRaises(ValueError):parse(xml.replace(b'published',b'missing'),s)
 def test_json_canary(self):
  s=source();s['adapter']='json'
  self.assertEqual(len(parse(json.dumps({'items':[{'id':'x','title':'FIXTURE','url':'https://example.org/a','published_at':'2026-10-13T04:00:00Z'}]}).encode(),s)),1)
  with self.assertRaises(ValueError):parse(b'{"results":[]}',s)
 def test_sec_date_precision_and_accession(self):
  s=source();s['adapter']='sec'
  raw=parse(json.dumps({'cik':'0000320193','name':'FIXTURE','filings':{'recent':{'accessionNumber':['0001-26-000001'],'form':['8-K'],'filingDate':['2026-10-12'],'primaryDocument':['a.htm']}}}).encode(),s)[0]
  self.assertEqual(raw['publication_precision'],'day');self.assertIn('/320193/000126000001/a.htm',raw['url'])
 def test_entity_block(self):
  with self.assertRaises(ValueError):parse(b'<!DOCTYPE rss [<!ENTITY x "y">]><rss/>',source())
 def test_html_not_feed(self):
  with self.assertRaises(ValueError):parse(b'<html><body>Login</body></html>',source())
 def test_excerpt_cap(self):
  s=source();s['excerpt_words']=1000;raw=copy.deepcopy(DATA['items'][0]);raw['summary']=' '.join(['FIXTURE']*100)
  self.assertEqual(len(normalize(raw,s,NOW,True)['permitted_excerpt'].split()),25)
 def test_zero_excerpt(self):
  s=source();s['excerpt_words']=0
  self.assertEqual(normalize(DATA['items'][0],s,NOW,True)['permitted_excerpt'],'')
 def test_canonical(self):
  self.assertEqual(canonical('https://EXAMPLE.org/a?utm_source=x&x=1#foo'),'https://example.org/a?x=1')
 def test_future_rejected(self):
  raw=copy.deepcopy(DATA['items'][0]);raw['published_at']='2027-01-01T00:00:00Z'
  with self.assertRaises(ValueError):normalize(raw,source(),NOW,True)
 def test_timezone_required(self):
  with self.assertRaises(ValueError):instant('2026-10-13T05:00:00')
  self.assertEqual(date('Tue, 13 Oct 2026 06:00:00 +0200'),'2026-10-13T04:00:00Z')

class Security(unittest.TestCase):
 def test_url_allowlist(self):
  for url in ['http://example.org/a','https://example.org.evil.test/a','https://u:p@example.org/a','https://example.org:8080/a','https://localhost/a']:
   with self.subTest(url=url),self.assertRaises(FetchError):check_url(url,['example.org'])
 def test_private_and_mixed_dns(self):
  for addresses in [['127.0.0.1'],['10.0.0.1'],['::1'],['169.254.169.254'],['93.184.216.34','192.168.1.1']]:
   with patch('collector.http.socket.getaddrinfo',return_value=[(2,1,6,'',(a,443)) for a in addresses]),self.assertRaises(FetchError):public_addresses('example.org')
 def test_sec_user_agent_required(self):
  s=source();s['adapter']='sec';s['id']='sec'
  with patch.dict('os.environ',{},clear=True),self.assertRaises(FetchError):Client(s,pathlib.Path('/tmp'))
 def test_robots_failure_and_disallow(self):
  for status,body in [(503,b''),(200,b'User-agent: *\nDisallow: /')]:
   c=Client(source(),pathlib.Path('/tmp'))
   with patch.object(c,'raw',return_value=(status,{},body,'https://example.org/robots.txt')),self.assertRaises(FetchError):c.allowed('https://example.org/a')
 def test_redirect_limit(self):
  with self.assertRaises(FetchError):Client(source(),pathlib.Path('/tmp')).raw('https://example.org/a',redirects=4)
 def test_304_requires_cache(self):
  with tempfile.TemporaryDirectory() as temp:
   c=Client(source(),pathlib.Path(temp))
   with patch.object(c,'allowed'),patch.object(c,'raw',return_value=(304,{},b'','https://example.org/a')),self.assertRaises(FetchError):c.fetch()
 def test_cache_contains_no_body(self):
  with tempfile.TemporaryDirectory() as temp:
   c=Client(source(),pathlib.Path(temp));c.pending={'etag':'v1'};c.save([item()]);data=load(pathlib.Path(temp)/(source()['id']+'.json'))
   self.assertNotIn('body',data);self.assertNotIn('summary',data['items'][0])
 def test_source_exception_quarantined(self):
  with patch('collector.collect.Client',side_effect=ValueError('FIXTURE parser failed')):
   rows,state=collect_source(source(),NOW,pathlib.Path('/tmp'),{})
  self.assertEqual(rows,[]);self.assertEqual(state['status'],'FAILED')

class Editorial(unittest.TestCase):
 def test_promotion_and_opinion_rejected(self):
  for typ in ('promotional','opinion'):
   self.assertEqual(eligibility(item(content_type=typ),NOW)['eligibility'],'REJECTED')
 def test_discovery_not_fact(self):
  for tier in ('T','X'):self.assertEqual(eligibility(item(source_tier=tier),NOW)['eligibility'],'REJECTED')
 def test_secondary_attributed(self):
  self.assertEqual(eligibility(item(source_tier='S',primary_source_links=[]),NOW)['eligibility'],'ATTRIBUTED')
 def test_crypto_speculation_rejected(self):
  self.assertEqual(eligibility(item(asset_classes=['crypto'],instrument_context={'crypto_evidence':'developer_claim'}),NOW)['eligibility'],'REJECTED')
 def test_fund_requires_share_class(self):
  self.assertEqual(eligibility(item(asset_classes=['funds']),NOW)['eligibility'],'REJECTED')
 def test_commodity_and_derivatives_context(self):
  for category in ('commodities','derivatives'):self.assertEqual(eligibility(item(asset_classes=[category]),NOW)['eligibility'],'REJECTED')
 def test_per_type_freshness(self):
  old=stamp(NOW-dt.timedelta(days=10))
  self.assertEqual(eligibility(item(published_at=old,content_type='reporting'),NOW)['eligibility'],'REJECTED')
  self.assertEqual(eligibility(item(published_at=old,content_type='research'),NOW)['eligibility'],'VERIFIED')
 def test_display_language(self):
  self.assertEqual(eligibility(item(original_language='no',display_language='no'),NOW)['eligibility'],'VERIFIED')
  self.assertEqual(eligibility(item(original_language='unknown',display_language='unknown'),NOW)['eligibility'],'REJECTED')
 def test_official_rationale(self):
  v=item(official_rationale=DATA['items'][0]['official_rationale']);result=explain(v,[])
  self.assertEqual(result['origin'],'ATTRIBUTED OFFICIAL EXPLANATION');self.assertIn('FIXTURE Central Bank states:',result['text']);self.assertNotIn('price',result['text'])
 def test_no_rationale_no_explanation(self):self.assertEqual(explain(item(),[])['text'],'Explanation unavailable today')
 def test_unreviewed_mechanism_not_explanation(self):self.assertEqual(explain(item(),load(ROOT/'data/glossary.json'))['origin'],'UNAVAILABLE')
 def test_reviewed_generic_context(self):
  glossary=load(ROOT/'data/glossary.json');glossary[0]['review_status']='reviewed'
  self.assertEqual(explain(item(),glossary)['origin'],'REVIEWED EDUCATIONAL CONTEXT')
 def test_twenty_five_word_rationale_boundary(self):
  v=item(official_rationale={'reviewed':True,'source_url':'https://example.org/rate','quote':'not in excerpt'})
  self.assertEqual(explain(v,[])['origin'],'UNAVAILABLE')

class Dedupe(unittest.TestCase):
 def test_five_syndicated_one_event(self):
  rows=[item(id=str(n),canonical_url=f'https://example.org/copy{n}',publisher=f'FIXTURE {n}',event_key='FIXTURE-event-1',origin_id='FIXTURE-original') for n in range(5)]
  result=cluster(rows);self.assertEqual(len(result),1);self.assertEqual(len(result[0]['cluster_sources']),5);self.assertEqual(len(result[0]['independent_origins']),1)
 def test_company_events_stay_distinct(self):
  a=item(event_type='earnings');b=item(id='b',canonical_url='https://example.org/b',original_title='FIXTURE Investigation',event_type='enforcement');b['provenance']['document_id']='b'
  self.assertEqual(len(cluster([a,b])),2)
 def test_disagreement_keeps_both(self):
  claim={'metric':'profit','as_of':'2026-Q3','unit':'NOK','definition':'net','dataset':'FIXTURE','value':10,'source_url':'https://example.org/a'}
  a=item(claims=[claim]);b=item(id='b',claims=[{**claim,'value':11,'source_url':'https://example.org/b'}]);result=cluster([a,b])[0]
  self.assertEqual(result['eligibility'],'DISPUTED');self.assertEqual({x['value'] for x in result['disagreements']},{10,11})
 def test_currency_difference_not_conflict(self):
  a=item(claims=[{'metric':'profit','as_of':'2026-Q3','unit':'NOK','definition':'net','dataset':'FIXTURE','value':10}]);b=copy.deepcopy(a);b['claims'][0].update(unit='USD',value=11)
  self.assertEqual(cluster([a,b])[0]['disagreements'],[])
 def test_earliest_original(self):
  a=item(id='a',published_at='2026-10-12T01:00:00Z');b=item(id='b')
  self.assertEqual(cluster([b,a])[0]['id'],'a')

class Ranking(unittest.TestCase):
 def test_surprise_corporate_beats_routine_macro(self):
  macro=score(item(),NOW)
  corp=item(event_type='profit_warning',asset_classes=['equities'],evidence_modifiers=[{'kind':k,'evidence_text':'FIXTURE explicitly stated','source_url':'https://example.org/rate'} for k in ('surprise','situation_changed')])
  self.assertGreater(score(corp,NOW)['editorial_score'],macro['editorial_score'])
 def test_unsupported_modifier_ignored(self):
  v=score(item(evidence_modifiers=[{'kind':'surprise','evidence_text':'','source_url':'https://example.org/rate'}]),NOW)
  self.assertEqual(v['score_components']['significance'],3)
 def test_tier_does_not_change_score(self):self.assertEqual(score(item(),NOW)['editorial_score'],score(item(source_tier='S'),NOW)['editorial_score'])
 def test_diversity(self):
  rows=[score(item(id=str(n),publisher='FIXTURE '+str(n//2),asset_classes=[['equities','macro','crypto','funds'][n//2]]),NOW) for n in range(8)]
  top=select_top(rows);self.assertEqual(len(top),5)
  for c in ('equities','macro','crypto','funds'):self.assertLessEqual(sum(c in i['asset_classes'] for i in top),2)
 def test_duplicate_has_no_novelty(self):
  v=item();self.assertEqual(score(v,NOW,[v['provenance']['document_id']])['score_components']['novelty'],0)
 def test_ten_real_historical_event_replays(self):
  rows=load(ROOT/'tests/fixtures/historical.json');self.assertGreaterEqual(len(rows),10)
  results=[]
  for row in rows:
   now=instant(row['date']+'T23:00:00Z')
   v=item(original_title='FIXTURE replay — '+row['title'],published_at=row['date']+'T00:00:00Z',event_type=row['event_type'],asset_classes=row['assets'],canonical_url=row['url'])
   v=score(eligibility(v,now),now);self.assertEqual(v['eligibility'],'VERIFIED');self.assertTrue(0<=v['editorial_score']<=5);results.append(v)
  self.assertGreater(max(i['editorial_score'] for i in results if i['event_type']=='emergency'),max(i['editorial_score'] for i in results if i['event_type']=='rate_decision'))

class HealthCoverage(unittest.TestCase):
 def test_empty_200_failed(self):self.assertEqual(health(source(),[],NOW,{'http_status':200})['status'],'FAILED')
 def test_frozen_200_failed(self):self.assertEqual(health(source(),[item(published_at='2020-01-01T00:00:00Z')],NOW,{'http_status':200})['status'],'FAILED')
 def test_irregular_no_new_items_ok(self):
  s=source();s['cadence_type']='irregular'
  self.assertEqual(health(s,[item(published_at='2026-04-01T00:00:00Z')],NOW,{'http_status':200})['status'],'SUCCEEDED')
 def test_irregular_structural_change_failed(self):self.assertEqual(health(source(),[item()],NOW,{'http_status':200},{'item_count':8})['status'],'FAILED')
 def test_irregular_silence_alarm(self):
  s=source();s['cadence_type']='irregular'
  self.assertEqual(health(s,[item(published_at='2020-01-01T00:00:00Z')],NOW,{'http_status':200})['status'],'FAILED')
 def test_last_success_preserved(self):
  h=health(source(),[],NOW,{'http_status':500},{'last_success':'2026-10-12T00:00:00Z','failures':2})
  self.assertEqual(h['failures'],3);self.assertEqual(h['last_success'],'2026-10-12T00:00:00Z')
 def test_not_configured(self):self.assertEqual(coverage([],[],[],NOW)['macro']['state'],'NOT_CHECKED')
 def test_all_failed(self):self.assertEqual(coverage([source()],[],[],NOW)['macro']['state'],'NOT_CHECKED')
 def test_no_critical_partial(self):
  s=source();s['critical']=False
  self.assertEqual(coverage([s],[{'source_id':s['id'],'status':'SUCCEEDED'}],[],NOW)['macro']['state'],'PARTIAL')
 def test_failed_critical_partial(self):
  s=source();other={**s,'id':'other'}
  c=coverage([s,other],[{'source_id':s['id'],'status':'SUCCEEDED'}],[],NOW)['macro']
  self.assertEqual(c['state'],'PARTIAL');self.assertTrue(c['failed_critical_sources'])
 def test_checked_quiet_names_and_time(self):
  s=source();c=coverage([s],[{'source_id':s['id'],'status':'SUCCEEDED'}],[],NOW)['macro']
  self.assertEqual(c['state'],'CHECKED_QUIET');self.assertEqual(c['checked_sources'],[s['publisher']]);self.assertEqual(c['checked_at'],stamp(NOW))
 def test_checked_stories(self):
  s=source();c=coverage([s],[{'source_id':s['id'],'status':'SUCCEEDED'}],[eligibility(item(),NOW)],NOW)['macro']
  self.assertEqual(c['state'],'CHECKED_WITH_STORIES')
 def test_optional_failure_degraded(self):
  s=source();other={**s,'id':'optional','publisher':'FIXTURE Optional','critical':False}
  c=coverage([s,other],[{'source_id':s['id'],'status':'SUCCEEDED'}],[],NOW)['macro']
  self.assertEqual(c['state'],'CHECKED_QUIET');self.assertTrue(c['degraded']);self.assertEqual(c['failed_sources'],['FIXTURE Optional'])
 def test_equities_outage_not_hidden_by_macro(self):
  s=source();eq={**s,'id':'equity','asset_classes':['equities']}
  c=coverage([s,eq],[{'source_id':s['id'],'status':'SUCCEEDED'}],[],NOW)
  self.assertEqual(c['equities']['state'],'NOT_CHECKED');self.assertEqual(c['macro']['state'],'CHECKED_QUIET')
 def test_normal_publication(self):
  c=states()
  for k in ('macro','equities'):c[k]['state']='CHECKED_QUIET'
  self.assertEqual(publication_rule(c),{'status':'FULL','allowed':True,'missing':[]})
 def test_partial_publication(self):
  c=states()
  for k in ('macro','bonds','commodities'):c[k]['state']='CHECKED_QUIET'
  result=publication_rule(c);self.assertTrue(result['allowed']);self.assertEqual(result['status'],'PARTIAL');self.assertEqual(result['missing'],['equities'])
 def test_block_publication(self):
  c=states();c['macro']['state']='CHECKED_QUIET'
  self.assertFalse(publication_rule(c)['allowed'])

class PublishingSchedule(unittest.TestCase):
 def test_fixture_e2e_schema_and_archive(self):
  with tempfile.TemporaryDirectory() as tmp:
   e=run(tmp,NOW,True);self.assertTrue(validate(e));self.assertFalse(e['deployable']);self.assertEqual(len(e['top_ids']),5);self.assertTrue(verify(tmp)['fixture'])
 def test_live_empty_first_run_not_deployable(self):
  with tempfile.TemporaryDirectory() as tmp:
   e=run(tmp,NOW);self.assertFalse(e['deployable']);self.assertEqual(e['status'],'PARTIAL');self.assertTrue(load(pathlib.Path(tmp)/'site/data/status.json')['stale']);self.assertFalse(list((pathlib.Path(tmp)/'editions').glob('*.json')))
 def test_keep_last_good(self):
  with tempfile.TemporaryDirectory() as tmp:
   prior=run(tmp,NOW,True);before=(pathlib.Path(tmp)/'site/data/latest.json').read_bytes()
   e=copy.deepcopy(prior);e.update(publication_allowed=False,status='PARTIAL',missing_categories=['equities'])
   e['coverage']['equities']['state']='NOT_CHECKED'
   # With only macro/bonds/commodities/derivatives configured, remove two other checks too.
   e['coverage']['commodities']['state']='NOT_CHECKED';e['coverage']['derivatives']['state']='NOT_CHECKED'
   self.assertFalse(publish(e,tmp,'FIXTURE equity outage'));self.assertEqual((pathlib.Path(tmp)/'site/data/latest.json').read_bytes(),before);self.assertTrue(load(pathlib.Path(tmp)/'site/data/status.json')['stale'])
 def test_idempotent(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=run(tmp,NOW,True);b=run(tmp,NOW+dt.timedelta(hours=2),True)
   self.assertEqual(a,b);self.assertEqual(len(list((pathlib.Path(tmp)/'editions').glob('*.json'))),1)
 def test_archive_mutation_detected(self):
  with tempfile.TemporaryDirectory() as tmp:
   run(tmp,NOW,True);path=pathlib.Path(tmp)/'editions/2026-10-13.json';path.write_text(path.read_text()+' ')
   with self.assertRaises(ValueError):verify(tmp)
 def test_fixture_cannot_deploy(self):
  with tempfile.TemporaryDirectory() as tmp:
   run(tmp,NOW,True)
   with self.assertRaises(ValueError):verify(tmp,True)
 def test_immutable_conflict(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=run(tmp,NOW,True);a['edition_at']='2026-10-13T06:00:00Z'
   with self.assertRaises(ValueError):publish(a,tmp,'FIXTURE')
 def test_schema_duplicate(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=run(tmp,NOW,True);a['stories'].append(a['stories'][0])
   with self.assertRaises(ValueError):validate(a)
 def test_schema_mixed_mode(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=run(tmp,NOW,True);a['stories'][0]['fixture']=False
   with self.assertRaises(ValueError):validate(a)
 def test_all_triggers_winter_summer_and_dst(self):
  for day,first in [('2026-01-15',6),('2026-07-15',5),('2026-03-29',5),('2026-10-25',6)]:
   with self.subTest(day=day),tempfile.TemporaryDirectory() as tmp:
    passed=[]
    for hour in (4,5,6,8,10):
     now=instant(f'{day}T{hour:02}:00:00Z')
     allow,_=should_run(now,tmp)
     if allow:passed.append(hour)
    self.assertEqual(passed[0],first)
    # Construct an explicit FIXTURE model, then mark a test-only copy live to
    # simulate a successful prior edition. Never written outside TemporaryDirectory.
    fixture=run(tmp,NOW,True);fixture.update(date=day,edition_at=f'{day}T{first:02}:00:00Z',fixture=False,deployable=True,verification_status='LIVE-VERIFIED')
    fixture['stories']=[];fixture['top_ids']=[];fixture['research_shelf']=[]
    atomic(pathlib.Path(tmp)/'editions'/f'{day}.json',fixture)
    self.assertTrue(all(not should_run(instant(f'{day}T{hour:02}:00:00Z'),tmp)[0] for hour in passed))
 def test_oslo_midnight_date(self):
  with tempfile.TemporaryDirectory() as tmp:
   e=run(tmp,instant('2026-10-13T22:30:00Z'),True);self.assertEqual(e['date'],'2026-10-14')

if __name__=='__main__':unittest.main()
