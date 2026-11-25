"""FIXTURE simulations plus title samples from the returned live probe (no network)."""
import copy
import datetime as dt
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from collector.adapters import date, feed_kind, parse
from collector.common import ROOT, instant, stamp
from collector.coverage import coverage, health
from collector.collect import collect_source
from collector.http import Client, FetchError
from collector.normalize import normalize
from collector.eligibility import eligibility
from collector.probe import probe_source, main
from collector.topic import financial_topic
from collector.eligibility import within_recency_window
from collector.rank import score,select_top
from collector.collect import make_edition

NOW = instant('2026-10-13T05:00:00Z')
REGISTRY = json.loads((ROOT/'config/sources.json').read_text())


def registry_source(source_id):
    return copy.deepcopy(next(s for s in REGISTRY if s['id'] == source_id))


class OfflineFixes(unittest.TestCase):
    def test_registry_scope_language_and_ssb_adapter(self):
        self.assertEqual(len(REGISTRY), 29)
        self.assertEqual({s['id'] for s in REGISTRY if s['enabled']}, {'fed','ecb','bis','sec-press','bls'})
        self.assertTrue(all(s['terms_approved'] and s['terms_url'] for s in REGISTRY if s['enabled']))
        self.assertTrue(all(s['scope'] in ('broad', 'single_entity') for s in REGISTRY))
        self.assertEqual(registry_source('sec')['scope'], 'single_entity')
        self.assertEqual(registry_source('ssb')['adapter'], 'rss')
        self.assertEqual(registry_source('e24')['display_language'], 'no')
        nber=registry_source('nber');candidate=nber['allowlist_candidates'][0]
        self.assertEqual(candidate['domain'],'back.nber.org')
        self.assertEqual(candidate['approval_status'],'needs human approval')
        self.assertFalse(candidate['active']);self.assertNotIn(candidate['domain'],nber['allowed_domains'])
        for sid in ('dn','finansavisen'):
            source=registry_source(sid)
            self.assertFalse(source['enabled']);self.assertEqual(source['policy_status'],'disabled_by_policy')
            self.assertEqual(source['policy_reason'],'paywalled')
            from collector.registry import validate_source
            source['enabled']=True
            with self.assertRaisesRegex(ValueError,'disabled by policy'):validate_source(source)
        eia=registry_source('eia')
        self.assertFalse(eia['enabled']);self.assertIn('No year is guessed',eia['disabled_reason'])
        bls=registry_source('bls')
        self.assertEqual(bls['content_type'],'pointer');self.assertFalse(bls['critical'])

    def test_archive_candidates_use_configured_recency_windows(self):
        data=json.loads((ROOT/'live_probe_results.json').read_text())
        rows={r['source_id']:r for r in data['results']}
        for source_id in ('ethereum','sec'):
            source=registry_source(source_id);now=instant(rows[source_id]['health']['checked_at'])
            candidates=[i for i in rows[source_id]['items'] if within_recency_window(
                {'content_type':source['content_type'],'published_at':i['published_at']},now)]
            self.assertLess(len(candidates),len(rows[source_id]['items']))
            self.assertTrue(all(within_recency_window({'content_type':source['content_type'],'published_at':i['published_at']},now) for i in candidates))
            if source_id=='ethereum':self.assertEqual(candidates,[])

    def test_bls_pointer_is_not_candidate_or_macro_coverage(self):
        source=registry_source('bls');source['enabled']=True
        raw={'title':'Major Economic Indicators Latest Numbers','url':source['url'],
             'published_at':'2026-10-09T14:00:29Z','document_id':'FIXTURE-BLS','summary':''}
        item=normalize(raw,source,NOW,True)
        self.assertEqual(source['content_type'],'pointer')
        self.assertEqual(eligibility(item,NOW)['eligibility'],'REJECTED')
        client=Mock();client.fetch.return_value=(None,[item],{'http_status':200,'latency_ms':1})
        with patch('collector.collect.Client',return_value=client),patch('collector.registry.validate_source'):
            candidates,state=collect_source(source,NOW,Path('/tmp'),{})
        self.assertEqual(state['status'],'SUCCEEDED');self.assertEqual(candidates,[])
        self.assertEqual(coverage([source],[state],[],NOW)['macro']['state'],'NOT_CHECKED')

    def test_routine_fed_and_boe_items_stay_full_edition_below_top_five(self):
        probe=json.loads((ROOT/'live_probe_results.json').read_text())
        by_id={r['source_id']:r for r in probe['results']}
        expected=(('fed','approval of application by Isabella','fed_application_approval'),
                  ('fed','termination of enforcement action with SNB','enforcement_termination'),
                  ('boe','Money Markets Code Sub-Committee – September','boe_committee_minutes'))
        sources=[registry_source('fed'),registry_source('boe')]
        for source in sources:source['enabled']=True
        items=[]
        for source_id,fragment,event_type in expected:
            source=registry_source(source_id)
            sample=next(i for i in by_id[source_id]['items'] if fragment.lower() in i['headline'].lower())
            raw={'title':sample['headline'],'url':sample['link'],'published_at':stamp(NOW-dt.timedelta(hours=1)),
                 'document_id':sample['link'],'summary':''}
            item=normalize(raw,source,NOW,True)
            self.assertEqual(item['event_type'],event_type)
            items.append(item)
        source=registry_source('fed')
        sample=next(i for i in by_id['fed']['items'] if i['headline']=='Federal Reserve issues FOMC statement')
        items.append(normalize({'title':sample['headline'],'url':sample['link'],
                                'published_at':stamp(NOW-dt.timedelta(hours=1)),
                                'document_id':sample['link'],'summary':''},source,NOW,True))
        ranked=[score(i,NOW) for i in items]
        for item in ranked:
            if item['event_type'] in ('fed_application_approval','enforcement_termination','boe_committee_minutes'):
                self.assertEqual(item['score_components']['significance'],0)
        top=select_top(ranked)
        self.assertEqual([i['event_type'] for i in top],['rate_decision'])
        edition,_=make_edition(items,sources,[{'source_id':s['id'],'status':'SUCCEEDED'} for s in sources],NOW,True)
        story_types={i['event_type'] for i in edition['stories']}
        self.assertTrue({'fed_application_approval','enforcement_termination','boe_committee_minutes'}<=story_types)
        self.assertEqual({i['event_type'] for i in edition['stories'] if i['id'] in edition['top_ids']},{'rate_decision'})

    def test_feed_vs_feed_index_probe(self):
        s = registry_source('ssb')
        feed = b'<rss><channel><item><title>FIXTURE inflation</title><link>https://www.ssb.no/a</link><pubDate>Tue, 13 Oct 2026 04:00:00 GMT</pubDate></item></channel></rss>'
        index = b'<rss><channel><item><title>FIXTURE RSS collection</title><link>https://www.ssb.no/rss/prices.rss</link></item></channel></rss>'
        self.assertEqual(feed_kind(feed), 'feed')
        self.assertEqual(feed_kind(index), 'feed_index')
        for body,kind,status in ((feed,'feed','SUCCEEDED'),(index,'feed_index','FAILED')):
            client = Mock(robots_status=200)
            client.raw.return_value = (200,{'content-type':'application/rss+xml'},body,s['url'])
            with patch('collector.probe.Client',return_value=client):
                row=probe_source(s,NOW,Path('/tmp'),fixture=True)
            self.assertEqual(row['feed_kind'],kind)
            self.assertEqual(row['health']['status'],status)
            self.assertEqual(row['robots_result'],'allowed')

    def test_irregular_empty_feed_is_quiet_until_silence_or_structure_failure(self):
        s=registry_source('arxiv');s['enabled']=True;s['critical']=True
        empty=b'<rss><channel><title>FIXTURE arXiv q-fin</title></channel></rss>'
        self.assertEqual(parse(empty,s),[])
        h=health(s,[],NOW,{'http_status':200,'structure_valid':True})
        self.assertEqual(h['status'],'UNVERIFIED_EMPTY')
        self.assertIsNone(h['last_nonempty_at'])
        self.assertEqual(coverage([s],[h],[],NOW)[s['asset_classes'][0]]['state'],'NOT_CHECKED')
        recent_previous={'newest_published_at':'2026-10-12T00:00:00Z','last_nonempty_at':'2026-10-12T00:00:00Z','item_count':8}
        prior=health(s,[{'original_title':'FIXTURE prior','canonical_url':'https://arxiv.org/a','published_at':'2026-10-12T00:00:00Z'}],NOW,{'http_status':200},{})
        self.assertEqual(prior['last_nonempty_at'],NOW.isoformat().replace('+00:00','Z'))
        quiet=health(s,[],NOW,{'http_status':200,'structure_valid':True},recent_previous)
        self.assertEqual(quiet['status'],'SUCCEEDED')
        self.assertEqual(quiet['last_nonempty_at'],recent_previous['last_nonempty_at'])
        self.assertEqual(coverage([s],[quiet],[],NOW)[s['asset_classes'][0]]['state'],'CHECKED_QUIET')
        previous={'newest_published_at':'2020-01-01T00:00:00Z','item_count':0}
        previous['last_nonempty_at']='2020-01-01T00:00:00Z'
        self.assertEqual(health(s,[],NOW,{'http_status':200,'structure_valid':True},previous)['status'],'FAILED')
        self.assertEqual(health(s,[],NOW,{'http_status':200,'structure_valid':False})['status'],'FAILED')
        with self.assertRaisesRegex(ValueError,'channel'):
            parse(b'<rss/>',s)
        cached=Mock();cached.fetch.return_value=(None,[],{'http_status':304})
        with patch('collector.collect.Client',return_value=cached),patch('collector.registry.validate_source'):
            stories,state=collect_source(s,NOW,Path('/tmp'),recent_previous)
        self.assertEqual(stories,[])
        self.assertEqual(state['status'],'SUCCEEDED')

    def test_single_entity_cannot_complete_category(self):
        s=registry_source('sec');s['enabled']=True;s['critical']=True
        h={'source_id':s['id'],'status':'SUCCEEDED'}
        state=coverage([s],[h],[],NOW)['equities']
        self.assertEqual(state['state'],'PARTIAL')
        self.assertIn('broad critical',state['reason'])
        broad=copy.deepcopy(s);broad['id']='fixture-broad';broad['scope']='broad'
        broad['critical']=False
        self.assertEqual(coverage([s,broad],[h,{'source_id':'fixture-broad','status':'SUCCEEDED'}],[],NOW)['equities']['state'],'PARTIAL')
        broad['critical']=True
        self.assertEqual(coverage([s,broad],[h,{'source_id':'fixture-broad','status':'SUCCEEDED'}],[],NOW)['equities']['state'],'CHECKED_QUIET')

    def test_one_honest_user_agent_and_robots_refusal(self):
        with patch.dict('os.environ',{'LEDGER_CONTACT_EMAIL':'reader@example.org'}):
            agents={Client(registry_source(k),Path('/tmp')).ua for k in ('bls','imf','sec-press','sec')}
        self.assertEqual(len(agents),1)
        self.assertIn('contact: reader@example.org',agents.pop())
        s=registry_source('bls')
        with patch.dict('os.environ',{'LEDGER_CONTACT_EMAIL':'reader@example.org'}):
            c=Client(s,Path('/tmp'))
            with patch.object(c,'raw',return_value=(403,{},b'','https://www.bls.gov/robots.txt')):
                with self.assertRaises(FetchError) as raised:c.allowed(s['url'])
        self.assertEqual(raised.exception.robots_status,403)

    def test_403_robots_targets_retry_once_and_stay_failed(self):
        for source_id in ('bls','imf','sec-press'):
            s=registry_source(source_id)
            failed={'source_id':source_id,'robots_http_status':403,
                    'health':{'status':'FAILED','reason':'robots unavailable HTTP 403'}}
            with tempfile.TemporaryDirectory() as temp,patch.dict('os.environ',{'LEDGER_CONTACT_EMAIL':'reader@example.org'}),\
                 patch('collector.probe.config',return_value=[s]),\
                 patch('collector.probe.probe_source',side_effect=[copy.deepcopy(failed),copy.deepcopy(failed)]) as probe,\
                 patch('collector.probe.report',side_effect=lambda sources,rows,start,end:{'results':rows}),\
                 patch('collector.probe.markdown',return_value='FIXTURE draft'),patch('builtins.print'):
                self.assertEqual(main(['--output-dir',temp]),0)
                self.assertEqual(probe.call_count,2)
                saved=json.loads((Path(temp)/'live_probe_results.json').read_text())
                self.assertEqual(saved['results'][0]['attempts'],2)
                self.assertEqual(saved['results'][0]['health']['status'],'FAILED')
        s=registry_source('bls')
        failed={'source_id':'bls','http_status':403,'robots_http_status':200,
                'health':{'status':'FAILED','reason':'HTTP 403'}}
        with tempfile.TemporaryDirectory() as temp,patch.dict('os.environ',{'LEDGER_CONTACT_EMAIL':'reader@example.org'}),\
             patch('collector.probe.config',return_value=[s]),\
             patch('collector.probe.probe_source',side_effect=[copy.deepcopy(failed),copy.deepcopy(failed)]) as probe,\
             patch('collector.probe.report',side_effect=lambda sources,rows,start,end:{'results':rows}),\
             patch('collector.probe.markdown',return_value='FIXTURE draft'),patch('builtins.print'):
            self.assertEqual(main(['--output-dir',temp]),0)
            self.assertEqual(probe.call_count,2)

    def test_gzip_decodes_and_caps_expanded_body(self):
        s=registry_source('bls')
        with patch.dict('os.environ',{'LEDGER_CONTACT_EMAIL':'reader@example.org'}),patch('collector.http.public_addresses',return_value=['93.184.216.34']),patch('collector.http.time.sleep'):
            for payload,oversize in ((b'FIXTURE payload',False),(b'x'*2_000_001,True)):
                response=Mock(status=200)
                response.getheaders.return_value=[('content-encoding','gzip')]
                response.read1.side_effect=[gzip.compress(payload),b'']
                conn=Mock();conn.getresponse.return_value=response
                with patch('collector.http.PinnedHTTPS',return_value=conn):
                    if oversize:
                        with self.assertRaisesRegex(FetchError,'large'):
                            Client(s,Path('/tmp')).raw(s['url'])
                    else:
                        self.assertEqual(Client(s,Path('/tmp')).raw(s['url'])[2],payload)

    def test_redirect_domain_recorded_without_allowlisting(self):
        s=registry_source('nber')
        response=Mock(status=302)
        response.getheaders.return_value=[('location','https://blocked.example.net/new-feed')]
        conn=Mock();conn.getresponse.return_value=response
        with patch.dict('os.environ',{'LEDGER_CONTACT_EMAIL':'reader@example.org'}),patch('collector.http.public_addresses',return_value=['93.184.216.34']),patch('collector.http.PinnedHTTPS',return_value=conn),patch('collector.http.time.sleep'):
            with self.assertRaises(FetchError) as raised:Client(s,Path('/tmp')).raw(s['url'])
        self.assertEqual(raised.exception.redirect_domain,'blocked.example.net')
        self.assertNotIn('blocked.example.net',s['allowed_domains'])
        source=registry_source('nber');fake=Mock(robots_status=200)
        fake.raw.side_effect=FetchError('HTTPS allowlist violation',redirect_domain='back.nber.org')
        with patch('collector.probe.Client',return_value=fake):
            row=probe_source(source,NOW,Path('/tmp'),fixture=True)
        self.assertEqual(row['redirect_target_domain'],'back.nber.org')
        self.assertEqual(row['health']['status'],'FAILED')
        source=registry_source('finansavisen');fake=Mock()
        with patch('collector.probe.Client',return_value=fake):
            row=probe_source(source,NOW,Path('/tmp'),fixture=True)
        self.assertIn('Disabled by policy: paywalled',row['health']['reason'])
        fake.allowed.assert_not_called()

    def test_eia_yearless_rejected_with_clear_reason(self):
        with self.assertRaisesRegex(ValueError,'yearless publication date rejected'):
            date('Fri, 09 Oct  09:00:00 EST')

    def test_filter_report_lists_all_returned_cnbc_and_e24_titles(self):
        data=json.loads((ROOT/'live_probe_results.json').read_text())
        report=(ROOT/'filter_report.md').read_text()
        expected=sum(len(next(r for r in data['results'] if r['source_id']==sid)['items']) for sid in ('cnbc','e24'))
        self.assertEqual(report.count('|KEEP|')+report.count('|DROP|'),expected)
        self.assertIn('No FINANCE keyword matched',report)
        self.assertIn('OFF_TOPIC matched:',report)

    def test_real_probe_title_samples_filter_nonfinancial_topics(self):
        returned=json.loads((ROOT/'live_probe_results.json').read_text())
        by_id={r['source_id']:r for r in returned['results']}
        for sid,fragment in (('cnbc',"Red Bull's F1 team"),('cnbc','Republican groups'),
                             ('cnbc','ambassador to Greece'),('e24','lungebetennelse'),
                             ('e24','drømmejobben'),('e24','mellomvalget'),('e24','Epstein-varsler')):
            title=next(i['headline'] for i in by_id[sid]['items'] if fragment in i['headline'])
            self.assertFalse(financial_topic(title),title)
        for sid,fragment in (('cnbc','IMF warns bond yields'),('cnbc','retail inflation'),
                             ('e24','Burrito-aksje'),('e24','Oslo Børs')):
            title=next(i['headline'] for i in by_id[sid]['items'] if fragment in i['headline'])
            self.assertTrue(financial_topic(title),title)

    def test_norwegian_story_carries_display_language(self):
        s=registry_source('e24')
        raw={'title':'Norges Bank hever renten','url':'https://e24.no/okonomi/a/123',
             'published_at':'2026-10-13T04:00:00Z','document_id':'FIXTURE-1','summary':'',
             'asset_classes':['macro']}
        item=normalize(raw,s,NOW,True)
        self.assertEqual(item['display_language'],'no')
        self.assertEqual(item['original_language'],'no')
        self.assertEqual(eligibility(item,NOW)['eligibility'],'ATTRIBUTED')


if __name__=='__main__':unittest.main()
