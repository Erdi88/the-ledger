"""FIXTURE-only checks for the portable diagnostic and evidence importer.

Simulated network responses are never emitted to evidence/ as live findings.
"""
import base64
import copy
import datetime as dt
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import zlib

from collector.common import ROOT, instant, stamp
from collector.coverage import health
from collector.probe import (ENGINE_FILES, activation, engine_digest, fingerprint,
                             ingest, main, markdown, probe_source, report, summarize,
                             validate_import)

NOW = instant('2026-10-13T05:00:00Z')
RSS = b'''<rss><channel><item><title>FIXTURE monetary policy decision</title>
<link>https://example.org/decision</link><guid>FIXTURE-document</guid>
<pubDate>Tue, 13 Oct 2026 04:00:00 GMT</pubDate>
<description>FIXTURE body text must never be stored</description></item></channel></rss>'''


def source(reviewed=False):
    s = json.loads((ROOT/'tests/fixtures/scenario.json').read_text())['sources'][0]
    s['enabled'] = False
    s['terms_approved'] = reviewed
    if not reviewed:
        s.update(last_reviewed=None, terms_url=None, license_note='UNVERIFIED')
    return s


def result(body=RSS, s=None, status=200, fixture=True, previous=None):
    s = s or source()
    client = Mock()
    client.raw.return_value = (status, {'content-type': 'application/rss+xml'}, body, s['url'])
    with patch('collector.probe.Client', return_value=client):
        return probe_source(s, NOW, Path('/tmp'), previous, fixture=fixture)


def external(s=None):
    # Simulated user-machine result exists only in test memory/temp files.
    s = s or source()
    row = result(s=s, fixture=False)
    return report([s], [row], NOW, NOW)


class LiveProbeTests(unittest.TestCase):
    def test_shared_health_rules_and_no_body_or_excerpt_persistence(self):
        r = result()
        self.assertEqual(r['health']['status'], 'SUCCEEDED')
        self.assertEqual(r['verification_status'], 'TESTED-OFFLINE')
        self.assertTrue(r['fixture'])
        self.assertEqual(r['items'][0]['excerpt'], '')
        self.assertNotIn('body text must never be stored', json.dumps(r))
        expected = health(source(), [{'original_title': r['items'][0]['headline'],
            'canonical_url': r['items'][0]['link'], 'published_at': r['items'][0]['published_at']}], NOW, {'http_status': 200})
        self.assertEqual(r['health']['status'], expected['status'])
        self.assertEqual(r['health']['publication_latency_hours'], expected['publication_latency_hours'])

    def test_200_html_is_not_healthy_feed(self):
        r = result(b'<html><body>FIXTURE login</body></html>')
        self.assertEqual(r['http_status'], 200)
        self.assertEqual(r['health']['status'], 'FAILED')
        self.assertFalse(r['parse_ok'])

    def test_empty_and_frozen_fail(self):
        for body in (b'<rss><channel/></rss>', RSS.replace(b'13 Oct 2026', b'13 Oct 2020')):
            with self.subTest(body=body):
                self.assertEqual(result(body)['health']['status'], 'FAILED')

    def test_irregular_availability_and_structure(self):
        s = source();s['cadence_type'] = 'irregular';s['health_check'] = 'availability'
        body = RSS.replace(b'13 Oct 2026', b'01 Apr 2026')
        self.assertEqual(result(body, s)['health']['status'], 'SUCCEEDED')
        self.assertEqual(result(body, s, previous={'item_count': 8})['health']['status'], 'FAILED')

    def test_robots_refusal_is_recorded(self):
        fake = Mock();fake.allowed.side_effect = ValueError('FIXTURE robots disallows URL')
        with patch('collector.probe.Client', return_value=fake):
            r = probe_source(source(), NOW, Path('/tmp'), fixture=True)
        self.assertFalse(r['robots_allowed']);fake.raw.assert_not_called()
        self.assertIn('robots', r['health']['reason'])

    def test_unsupported_html_gets_record_not_success(self):
        s = source();s['adapter'] = 'html'
        r = result(b'<html/>', s)
        self.assertEqual(r['adapter_status'], 'NOT BUILT')
        self.assertEqual(r['health']['status'], 'FAILED')

    def test_http_failure_preserved(self):
        r = result(b'FIXTURE unavailable', status=503)
        self.assertEqual(r['http_status'], 503)
        self.assertEqual(r['health']['status'], 'FAILED')

    def test_missing_sec_contact_is_recorded_without_fake_contact(self):
        s = source();s['adapter'] = 'sec';s['id'] = 'sec'
        with patch.dict('os.environ', {}, clear=True):
            r = probe_source(s, NOW, Path('/tmp'), fixture=True)
        self.assertIsNone(r['http_status']);self.assertIn('LEDGER_CONTACT_EMAIL', r['health']['reason'])

    def test_sec_contact_redacted_from_error(self):
        value = 'fixture@example.org'
        with patch.dict('os.environ', {'LEDGER_CONTACT_EMAIL': value}), patch('collector.probe.Client', side_effect=ValueError(value)):
            r = probe_source(source(), NOW, Path('/tmp'), fixture=True)
        self.assertNotIn(value, json.dumps(r))

    def test_healthy_does_not_grant_rights(self):
        r = result();s, _, reason = activation(source(), r, NOW)
        self.assertFalse(s['enabled']);self.assertIn('review', reason)

    def test_local_review_allows_healthy_source(self):
        s = source(True);proposal, _, reason = activation(s, result(s=s), NOW)
        self.assertTrue(proposal['enabled']);self.assertIsNone(reason)

    def test_tier_t_cannot_count_as_enabled_news(self):
        s = source(True);s['tier'] = 'T'
        self.assertFalse(activation(s, result(s=s), NOW)[0]['enabled'])

    def test_recheck_freshness_at_import(self):
        s = source(True);s['max_staleness'] = 2
        data = external(s);rows = validate_import(data, [s], NOW+dt.timedelta(hours=3))
        summary = summarize([s], rows, NOW+dt.timedelta(hours=3))
        self.assertFalse(summary['sources'][0]['enabled'])
        self.assertIn('No longer healthy', summary['decisions'][0]['reason'])

    def test_fixture_evidence_refused(self):
        data = report([source()], [result()], NOW, NOW, fixture=True)
        self.assertIn('FIXTURE', markdown(data))
        with self.assertRaisesRegex(ValueError, 'FIXTURE'):
            validate_import(data, [source()], NOW)

    def test_old_and_future_evidence_refused(self):
        data = external()
        for now in (NOW-dt.timedelta(seconds=1), NOW+dt.timedelta(hours=25)):
            with self.assertRaises(ValueError):validate_import(data, [source()], now)

    def test_incomplete_duplicate_and_unknown_candidate_refused(self):
        for change in ('missing', 'duplicate', 'unknown'):
            d = external()
            if change == 'missing':d['results'] = []
            elif change == 'duplicate':d['results'] *= 2
            else:d['results'][0]['source_id'] = 'unknown'
            with self.assertRaises(ValueError):validate_import(d, [source()], NOW)

    def test_changed_engine_or_source_refused(self):
        d = external();d['engine_sha256'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'engine'):validate_import(d, [source()], NOW)
        s = source();s['max_staleness'] = 9999
        with self.assertRaisesRegex(ValueError, 'changed source'):validate_import(external(), [s], NOW)

    def test_forged_success_and_extra_body_field_refused(self):
        for kind in ('stale', 'body', 'private_url', 'count', 'fixture_row'):
            d = external();r = d['results'][0]
            if kind == 'stale':r['items'][0]['published_at'] = '2020-01-01T00:00:00Z'
            elif kind == 'body':r['items'][0]['body'] = 'FIXTURE forbidden'
            elif kind == 'private_url':r['items'][0]['link'] = 'http://127.0.0.1/a'
            elif kind == 'count':r['health']['item_count'] = 99
            else:r['fixture'] = True
            with self.assertRaises(ValueError):
                rows = validate_import(d, [source()], NOW)
                summarize([source()], rows, NOW)

    def test_file_cannot_grant_terms_or_override_gonogo(self):
        d = external();d['sources'][0]['terms_approved'] = True
        d['gonogo'] = {'decision': 'FULL_SCOPE'};d['enablement_draft'] = [{'enable': True}]
        rows = validate_import(d, [source()], NOW)
        summary = summarize([source()], rows, NOW)
        self.assertFalse(summary['sources'][0]['enabled'])
        self.assertEqual(summary['gonogo']['counts']['overall'], 0)

    def test_dry_run_then_apply_changes_only_enabled_and_backs_up(self):
        s = source(True);data = external(s)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);(root/'config').mkdir()
            registry = root/'config/sources.json';registry.write_text(json.dumps([s]))
            evidence = root/'probe.json';evidence.write_text(json.dumps(data))
            before = registry.read_bytes()
            summary = ingest(evidence, root, NOW)
            self.assertEqual(before, registry.read_bytes());self.assertFalse(summary['applied'])
            summary = ingest(evidence, root, NOW, apply=True)
            changed = json.loads(registry.read_text())[0]
            self.assertTrue(changed.pop('enabled'));expected = copy.deepcopy(s);expected.pop('enabled')
            self.assertEqual(changed, expected)
            self.assertEqual(len(list((root/'evidence').glob('sources-before-import-*'))), 1)
            self.assertFalse((root/'editions').exists())

    def test_all_candidates_written_and_draft_does_not_replace_production(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);original = root/'SOURCES_REPORT.md';original.write_text('FIXTURE original')
            with patch('collector.probe.config', side_effect=lambda name: [source()] if name == 'sources' else __import__('collector.common', fromlist=['config']).config(name)), patch('collector.probe.probe_source', side_effect=lambda s,n,c,p: result(s=s, fixture=False)), patch('builtins.print'):
                main(['--output-dir', temp])
            self.assertEqual(original.read_text(), 'FIXTURE original')
            self.assertTrue((root/'live_probe_results.json').exists())
            self.assertTrue((root/'live_probe_draft/SOURCES_REPORT.md').exists())

    def test_bundle_has_exact_production_engine_and_registry(self):
        namespace = runpy.run_path(str(ROOT/'scripts/live_probe.py'))
        files = json.loads(zlib.decompress(base64.b64decode(namespace['PAYLOAD'])))
        for name in (*ENGINE_FILES, 'config/sources.json'):
            self.assertEqual(base64.b64decode(files[name]), (ROOT/name).read_bytes(), name)

    def test_single_file_runs_outside_project_without_packages(self):
        with tempfile.TemporaryDirectory() as temp:
            script = Path(temp)/'live_probe.py';shutil.copyfile(ROOT/'scripts/live_probe.py', script)
            r = subprocess.run([sys.executable, '-I', str(script), '--describe'], cwd=temp,
                               capture_output=True, text=True, timeout=10)
            self.assertEqual(r.returncode, 0, r.stderr)
            d = json.loads(r.stdout)
            self.assertEqual(d['candidate_count'], 29)
            self.assertEqual(d['engine_sha256'], engine_digest())
            self.assertEqual(d['status'], 'TESTED-OFFLINE')
