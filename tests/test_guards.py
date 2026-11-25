"""FIXTURE adverse-input tests for the remaining review findings."""
import copy,gzip,json,pathlib,tempfile,unittest
from unittest.mock import patch,Mock
from test_ledger import source,item,NOW,DATA,states
from collector.http import Client,FetchError
from collector.common import load,ROOT,stamp
from collector.collect import make_edition,run,collect_source
from collector.schema import validate
from collector.rank import score,apply_overrides
from collector.scope import evaluate
from collector.coverage import health

class Guards(unittest.TestCase):
 def test_response_cap_and_compressed_response(self):
  for headers,payload in [([('content-length','3000000')],b''),([('content-encoding','gzip')],gzip.compress(b'x'*2_000_001))]:
   response=Mock(status=200);response.getheaders.return_value=headers;response.read1.side_effect=[payload,b'']
   conn=Mock();conn.getresponse.return_value=response
   with patch('collector.http.public_addresses',return_value=['93.184.216.34']),patch('collector.http.PinnedHTTPS',return_value=conn),patch('collector.http.time.sleep'),self.assertRaises(FetchError):Client(source(),pathlib.Path('/tmp')).raw('https://example.org/a')
 def test_redirect_to_internal_domain_blocked(self):
  response=Mock(status=302);response.getheaders.return_value=[('location','https://127.0.0.1/secrets')]
  conn=Mock();conn.getresponse.return_value=response
  with patch('collector.http.public_addresses',return_value=['93.184.216.34']),patch('collector.http.PinnedHTTPS',return_value=conn),self.assertRaises(FetchError):Client(source(),pathlib.Path('/tmp')).raw('https://example.org/a')
 def test_200_parse_failure_records_http(self):
  fake=Mock();fake.fetch.return_value=(b'<html/>',None,{'http_status':200,'latency_ms':2})
  with patch('collector.collect.Client',return_value=fake):rows,h=collect_source(source(),NOW,pathlib.Path('/tmp'),{})
  self.assertEqual(h['http_status'],200);self.assertEqual(h['status'],'FAILED');self.assertEqual(rows,[])
 def test_conditional_get_rechecks_cached_freshness(self):
  stale=item(published_at='2020-01-01T00:00:00Z');fake=Mock();fake.fetch.return_value=(None,[stale],{'http_status':304,'latency_ms':1})
  with patch('collector.collect.Client',return_value=fake):rows,h=collect_source(source(),NOW,pathlib.Path('/tmp'),{})
  self.assertEqual(h['status'],'FAILED');self.assertEqual(rows,[])
 def test_promotional_copy_does_not_suppress_primary(self):
  promo=item(content_type='promotional',id='promo',published_at='2026-10-12T00:00:00Z')
  valid=item();e,q=make_edition([promo,valid],[source()],[{'source_id':source()['id'],'status':'SUCCEEDED'}],NOW,True)
  self.assertEqual(len(e['stories']),1);self.assertEqual(q[0]['eligibility'],'REJECTED')
 def test_disputed_cluster_stays_out_of_edition(self):
  claim={'metric':'x','as_of':'2026','unit':'NOK','definition':'net','dataset':'FIXTURE','value':1,'source_url':'https://example.org/a'}
  a=item(claims=[claim]);b=item(id='b',claims=[{**claim,'value':2,'source_url':'https://example.org/b'}])
  e,q=make_edition([a,b],[source()],[],NOW,True)
  self.assertEqual(e['stories'],[]);self.assertEqual(q[0]['eligibility'],'DISPUTED');self.assertEqual(len(q[0]['disagreements']),2)
 def test_speculative_crypto_does_not_enter_ranking(self):
  a=item(asset_classes=['crypto'],source_tier='T',id='crypto');b=item()
  e,q=make_edition([a,b],[source()],[],NOW,True)
  self.assertEqual(len(e['stories']),1);self.assertEqual(q[0]['id'],'crypto')
 def test_historical_archive_seen_url_blocks_republication(self):
  a=item();e,q=make_edition([a],[source()],[],NOW,True,{'_seen':[a['canonical_url']]})
  self.assertEqual(e['stories'],[])
 def test_ranking_override_requires_log(self):
  with self.assertRaises(ValueError):apply_overrides([score(item(),NOW)],[{'story_id':'x'}],NOW)
 def test_logged_override_is_visible(self):
  a=score(item(),NOW);before=a['editorial_score'];o={'story_id':a['id'],'reason':'FIXTURE editor review','editor':'FIXTURE','logged_at':'2026-10-12T00:00:00Z','expires_at':'2026-10-14T00:00:00Z','score_adjustment':.2}
  apply_overrides([a],[o],NOW);self.assertAlmostEqual(a['editorial_score'],before+.2);self.assertIn('FIXTURE editor review',a['ranking_reason'])
 def test_deployment_flag_cannot_override_coverage(self):
  with tempfile.TemporaryDirectory() as tmp:
   e=run(tmp,NOW);e['deployable']=True
   with self.assertRaises(ValueError):validate(e)
 def test_gonogo_offline_and_narrow(self):
  self.assertEqual(evaluate([],[],False)['decision'],'OFFLINE_FIXTURE_BUILD');self.assertEqual(evaluate([],[],True)['decision'],'DEFENSIBLE_NARROWER_SCOPE')
 def test_gonogo_full_requires_verified_substance(self):
  sources=[]
  for i in range(5):sources.append({**source(),'id':str(i),'asset_classes':['macro'] if i<3 else ['equities'],'substance_verified':True,'nordic':i==0})
  healths=[{'source_id':s['id'],'status':'SUCCEEDED'} for s in sources]
  self.assertEqual(evaluate(sources,healths,True)['decision'],'FULL_SCOPE')
  sources[-1]['substance_verified']=False
  self.assertEqual(evaluate(sources,healths,True)['decision'],'DEFENSIBLE_NARROWER_SCOPE')
 def test_glossary_human_review_inventory(self):
  entries=load(ROOT/'data/glossary.json');self.assertEqual(len(entries),30);self.assertEqual(len({g['id'] for g in entries}),30)
  self.assertTrue(all(g['review_status']=='needs human review' for g in entries))

class FinalGuards(unittest.TestCase):
 def test_administrative_material_not_padded_into_news(self):
  from collector.eligibility import eligibility
  self.assertEqual(eligibility(item(event_type='other'),NOW)['eligibility'],'REJECTED')
 def test_unreviewed_source_cannot_activate(self):
  from collector.registry import validate_source
  s=source();s['last_reviewed']=None
  with self.assertRaises(ValueError):validate_source(s)
 def test_secondary_requires_corrections_policy(self):
  from collector.registry import validate_source
  s=source();s['tier']='S'
  with self.assertRaises(ValueError):validate_source(s)
 def test_correction_overlay_preserves_original(self):
  import subprocess,sys
  from scripts.validate import verify
  with tempfile.TemporaryDirectory() as tmp:
   e=run(tmp,NOW,True);path=pathlib.Path(tmp)/'editions'/f"{e['date']}.json";before=path.read_bytes()
   result=subprocess.run([sys.executable,str(ROOT/'scripts/correct.py'),'--root',tmp,'--edition',e['date'],'--story',e['stories'][0]['id'],'--description','FIXTURE correction','--source','https://example.org/correction','--reviewed-by','FIXTURE Editor'],capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(before,path.read_bytes());self.assertTrue(verify(tmp)['valid']);self.assertEqual(len(load(pathlib.Path(tmp)/'site/data/corrections.json')),1)

class ScopeRestriction(unittest.TestCase):
 def test_failing_macro_bar_removes_coverage_without_mutating_registry(self):
  from collector.scope import restrict
  from collector.coverage import coverage
  original=source();items=[item()];result={'counts':{'macro_primary':1,'substantive_equity':0}}
  sources,restricted=restrict([original],items,result)
  c=coverage(sources,[{'source_id':original['id'],'status':'SUCCEEDED'}],[],NOW)
  self.assertEqual(c['macro']['state'],'NOT_CHECKED');self.assertIn('macro',original['asset_classes']);self.assertNotIn('macro',restricted[0]['asset_classes'])
