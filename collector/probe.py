"""Diagnostic source checks and strict, non-publishing evidence ingestion.

Uses production transport, parsing, normalization and health functions. Never
confuses technical health with reuse approval, or probe samples with an edition.
"""
import argparse
import copy
import datetime as dt
import getpass
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

from .adapters import parse, feed_kind
from .common import ROOT, UTC, config, instant, stamp
from .coverage import health
from .http import Client, check_url
from .normalize import normalize
from .registry import validate_source
from .scope import evaluate

VERSION = 1
MAX_IMPORT_BYTES = 20_000_000
MAX_AGE_HOURS = 24
# Review/enablement fields are deliberately excluded: importer trusts local
# reviews, never legal or editorial approval supplied by a result file.
IDENTITY_FIELDS = ('id', 'publisher', 'tier', 'content_type', 'asset_classes',
                   'adapter', 'url', 'allowed_domains', 'allowlist_candidates', 'policy_status', 'policy_reason',
                   'disabled_reason', 'language', 'display_language', 'scope', 'critical',
                   'cadence_type', 'health_check', 'max_staleness', 'max_silence',
                   'baseline_item_count', 'min_interval_seconds', 'nordic')
ENGINE_FILES = ('collector/__init__.py', 'collector/common.py', 'collector/http.py',
                'collector/adapters/__init__.py', 'collector/normalize.py',
                'collector/coverage.py', 'collector/registry.py', 'collector/scope.py',
                'collector/topic.py',
                'collector/probe.py', 'config/editorial.json', 'config/ranking.json', 'config/coverage.json',
                'config/gonogo.json')
ITEM_FIELDS = {'headline', 'link', 'publisher', 'published_at', 'retrieved_at', 'excerpt'}


def atomic(path, value):
    """Portable UTF-8 output, including Windows without a UTF-8 locale."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def fingerprint(source):
    fields = {key: source.get(key) for key in IDENTITY_FIELDS}
    return hashlib.sha256(json.dumps(fields, sort_keys=True).encode()).hexdigest()


def engine_digest(root=ROOT):
    value = hashlib.sha256()
    for name in ENGINE_FILES:
        value.update(name.encode() + b'\0' + (Path(root) / name).read_bytes() + b'\0')
    return value.hexdigest()


def check_items(items):
    return [{'original_title': i['headline'], 'canonical_url': i['link'],
             'published_at': i['published_at']} for i in items]


def probe_source(source, now, cache_dir, previous=None, fixture=False):
    """GET is diagnostic only: no terms bypass in Client.fetch or publication.

    Unreviewed sources can be inspected, subject to robots, but are never enabled.
    No body is cached and excerpts are always omitted from diagnostic evidence.
    """
    started = time.monotonic()
    s = copy.deepcopy(source)
    s['excerpt_words'] = 0
    previous = previous or {}
    row = {'source_id': s['id'], 'source_fingerprint': fingerprint(source),
           'url': s['url'], 'publisher': s['publisher'], 'adapter': s['adapter'],
           'fixture': fixture, 'checked_at': stamp(now), 'http_status': None,
           'attempts': 1,
           'format': 'unknown', 'feed_kind': 'unknown', 'robots_allowed': False,
           'robots_result': 'unknown', 'robots_http_status': None,
           'redirect_target_domain': None, 'parse_ok': False,
           'normalization_ok': False, 'items': [], 'previous_health': previous,
           'verification_status': 'TESTED-OFFLINE', 'health': None}
    if s.get('policy_status') == 'disabled_by_policy':
        row['health'] = health(s, [], now, {'http_status': None}, previous)
        row['health']['reason'] = 'Disabled by policy: '+str(s.get('policy_reason','unspecified'))+'; request skipped'
        row['latency_ms'] = round((time.monotonic() - started) * 1000, 1)
        row['health']['latency_ms'] = row['latency_ms']
        return row
    try:
        client = Client(s, cache_dir)
        client.allowed(s['url'])
        row['robots_allowed'] = True
        robots_status = getattr(client, 'robots_status', None)
        row['robots_http_status'] = robots_status if type(robots_status) is int else None
        row['robots_result'] = 'allowed'
        # No conditional request on this diagnostic: a complete response permits
        # parsing/health re-evaluation when the JSON is returned to another machine.
        status, headers, body, final_url = client.raw(s['url'])
        row.update(http_status=status, final_url=final_url,
                   content_type=headers.get('content-type', 'unknown'),
                   response_bytes=len(body))
        row['format'] = s['adapter']
        if s['adapter'] in ('rss','atom'):
            row['feed_kind'] = feed_kind(body)
        if not fixture:
            row['verification_status'] = 'LIVE-VERIFIED'  # HTTP evidence only
        if status != 200:
            raise ValueError(f'HTTP {status}; a fresh 200 body is required by the probe')
        if row['feed_kind'] == 'feed_index':
            raise ValueError('Feed index is not an article feed; choose a reviewed specific feed URL')
        parsed = parse(body, s)
        row['parse_ok'] = True
        normalized = [normalize(i, s, now, fixture) for i in parsed]
        row['normalization_ok'] = True
        row['items'] = [{'headline': i['original_title'], 'link': i['canonical_url'],
                         'publisher': i['publisher'], 'published_at': i['published_at'],
                         'retrieved_at': i['retrieved_at'], 'excerpt': ''}
                        for i in normalized]
        row['health'] = health(s, normalized, now, {'http_status': status, 'structure_valid': True}, previous)
    except Exception as exc:
        # Exceptions never carry the body or the declared SEC contact into output.
        reason = str(exc)
        contact = os.environ.get('LEDGER_CONTACT_EMAIL', '')
        if contact:
            reason = reason.replace(contact, '[redacted contact]')
        row['redirect_target_domain'] = getattr(exc, 'redirect_domain', None)
        row['robots_http_status'] = getattr(exc, 'robots_status', None) or row['robots_http_status']
        if not row['robots_allowed'] and row['robots_http_status'] is not None:
            row['robots_result'] = 'refused HTTP '+str(row['robots_http_status'])
        elif 'robots disallows' in reason:
            row['robots_result'] = 'disallowed by robots.txt'
        row['health'] = health(s, [], now, {'http_status': row['http_status']}, previous)
        row['health']['reason'] = reason[:500]
        if s['adapter'] not in ('rss', 'atom', 'json', 'sec'):
            row['adapter_status'] = 'NOT BUILT'
    row['latency_ms'] = round((time.monotonic() - started) * 1000, 1)
    row['health']['latency_ms'] = row['latency_ms']
    return row


def activation(source, row, now):
    """Re-evaluate returned technical evidence against local policy and review."""
    s = copy.deepcopy(source)
    s['enabled'] = False
    if row['health']['status'] != 'SUCCEEDED':
        return s, row['health'], row['health']['reason'] or 'Probe failed'
    if not (row['http_status'] == 200 and row['parse_ok'] is True
            and row['normalization_ok'] is True and row['robots_allowed'] is True):
        raise ValueError('Success without complete HTTP/parse/robots evidence')
    observed = instant(row['checked_at'])
    at_probe = health(s, check_items(row['items']), observed,
                      {'http_status': row['http_status'], 'structure_valid': row['parse_ok']}, row['previous_health'])
    if at_probe['status'] != 'SUCCEEDED':
        raise ValueError('Claimed successful health disagrees with returned metadata')
    current = health(s, check_items(row['items']), now,
                     {'http_status': row['http_status'], 'structure_valid': row['parse_ok']}, row['previous_health'])
    if current['status'] != 'SUCCEEDED':
        return s, current, 'No longer healthy at import time: ' + current['reason']
    if s['tier'] not in ('P', 'S'):
        return s, current, 'Discovery/excluded tier cannot be enabled as news'
    try:
        s['enabled'] = True
        validate_source(s)
        if dt.date.fromisoformat(s['last_reviewed']) > now.date():
            raise ValueError('Source review is future-dated')
    except (ValueError, KeyError, TypeError) as exc:
        s['enabled'] = False
        return s, current, str(exc)
    return s, current, None


def summarize(sources, rows, now):
    proposed, healths, decisions = [], [], []
    for source, row in zip(sources, rows):
        s, h, reason = activation(source, row, now)
        proposed.append(s)
        healths.append(h)
        decisions.append({'source_id': s['id'], 'enable': s['enabled'], 'reason': reason,
                          'health_at_evaluation': h['status']})
    network = any(r['http_status'] is not None for r in rows)
    return {'sources': proposed, 'decisions': decisions,
            'gonogo': evaluate(proposed, healths, network)}


def report(sources, rows, started, finished, fixture=False):
    summary = summarize(sources, rows, finished)
    return {'schema_version': VERSION, 'kind': 'THE_LEDGER_SOURCE_PROBE',
            'fixture': fixture, 'evidence_origin': 'FIXTURE' if fixture else 'USER_MACHINE_NETWORK',
            'verification_status': 'LIVE-VERIFIED' if not fixture and any(
                r['http_status'] is not None for r in rows) else 'TESTED-OFFLINE',
            'started_at': stamp(started), 'finished_at': stamp(finished),
            'engine_sha256': engine_digest(), 'candidate_count': len(sources),
            'sources': sources, 'results': rows, 'gonogo': summary['gonogo'],
            'enablement_draft': summary['decisions'],
            'notice': 'Diagnostics only; HTTP evidence is not healthy coverage or reuse permission. '
                      'No edition or original-document audit has been performed. No article bodies stored.'}


def markdown(data):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ').replace('<', '&lt;').replace('>', '&gt;')
    sources, rows = data['sources'], data['results']
    lines = ['# SOURCES_REPORT — draft from connected-machine probe', '',
             '**FIXTURE — TESTED-OFFLINE**' if data['fixture'] else
             '**' + data['verification_status'] + ' (scope: diagnostic HTTP results only)**', '',
             data['notice'], '', 'Finished: ' + data['finished_at'], '',
             'A successful parse is required in addition to HTTP 200. Terms, cadence, substance '
             'and category tags remain provisional unless reviewed locally. Unsupported HTML adapters '
             'are failed health, even when their page is reachable. No automatic scraping is added.', '',
             '|Source|HTTP|Format|Feed type|Robots|Redirect domain|Health|Latency ms|Cadence / limit hours|Reason|',
             '|---|---:|---|---|---|---|---|---:|---|---|']
    for s, r in zip(sources, rows):
        limit = s['max_staleness'] if s['cadence_type'] == 'regular' else s['max_silence']
        lines.append('|'+ '|'.join(cell(x) for x in (s['publisher'], r['http_status'], r['format'],
            r.get('feed_kind','unknown'), r.get('robots_result','unknown'),
            r.get('redirect_target_domain') or '—', r['health']['status'], r['latency_ms'], f"{s['cadence_type']} / {limit}",
            r['health']['reason'] or 'HTTP + parser + structure + source health passed')) + '|')
    decisions = {d['source_id']: d for d in data['enablement_draft']}
    lines += ['', '## Category counts (source tags, not complete market coverage)', '',
              '|Category|Technically healthy primary|Technically healthy news|Approved usable primary|Approved usable news|',
              '|---|---:|---:|---:|---:|']
    for category in config('coverage')['categories']:
        counts = []
        for approved in (False, True):
            for tier in ('P', 'S'):
                counts.append(sum(category in s['asset_classes'] and s['tier'] == tier
                    and r['health']['status'] == 'SUCCEEDED'
                    and (not approved or decisions[s['id']]['enable']) for s, r in zip(sources, rows)))
        lines.append('|'+category+'|'+'|'.join(map(str, counts))+'|')
    lines += ['', '## Norway / Nordics and substantive content', '']
    for s, r in zip(sources, rows):
        if s.get('nordic'):
            lines.append('- '+cell(s['publisher'])+': '+r['health']['status']+'; '+
                         cell(s.get('substance_assessment', 'Substance unknown')))
    lines += ['', 'Meaningful Norwegian coverage and substantive versus administrative content require '
              'original-document inspection. Healthy endpoints alone do not establish either.', '',
              '## Gate 2 / activation draft', '',
              'Thresholds: `'+json.dumps(config('gonogo'), sort_keys=True)+'`',
              'Decision: `'+data['gonogo']['decision']+'`; counts: `'+json.dumps(data['gonogo']['counts'])+'`', '']
    for d in data['enablement_draft']:
        lines.append('- '+cell(d['source_id'])+': '+('eligible for local activation' if d['enable'] else
                     'disabled — '+cell(d['reason'])))
    lines += ['', 'Thin/unknown coverage must remain NOT_CHECKED. Import rechecks timestamps, health '
              'and local review records; this draft never changes the registry or production report.', '',
              'Return `live_probe_results.json`. Next: locally review rights/corrections/substance, '
              'ingest results, run genuine collection, and audit five original stories before deployment.', '']
    return '\n'.join(lines)


def validate_import(data, sources, now):
    if data.get('schema_version') != VERSION or data.get('kind') != 'THE_LEDGER_SOURCE_PROBE':
        raise ValueError('Unknown probe result schema')
    if data.get('fixture') is not False or data.get('evidence_origin') != 'USER_MACHINE_NETWORK':
        raise ValueError('FIXTURE or unknown-origin evidence cannot enable sources')
    if data.get('verification_status') not in ('LIVE-VERIFIED', 'TESTED-OFFLINE'):
        raise ValueError('Invalid verification status')
    if data.get('engine_sha256') != engine_digest():
        raise ValueError('Probe engine/policy changed; regenerate the script and rerun the probe')
    start, finish = instant(data['started_at']), instant(data['finished_at'])
    if not start <= finish <= now or (now-start).total_seconds() > MAX_AGE_HOURS*3600:
        raise ValueError('Probe evidence is future-dated or older than 24 hours; rerun it')
    rows = data['results']
    expected = {s['id'] for s in sources}
    if len(rows) != len(expected) or {r['source_id'] for r in rows} != expected:
        raise ValueError('Results must contain every current candidate exactly once')
    if data['candidate_count'] != len(sources):
        raise ValueError('Candidate count mismatch')
    by_id = {r['source_id']: r for r in rows}
    for source in sources:
        r = by_id[source['id']]
        if r.get('fixture') is not False or r['source_fingerprint'] != fingerprint(source):
            raise ValueError('FIXTURE or changed source/health policy: '+source['id'])
        if r['url'] != source['url'] or r['publisher'] != source['publisher']:
            raise ValueError('Source identity mismatch')
        if not start <= instant(r['checked_at']) <= finish:
            raise ValueError('Source check timestamp outside run')
        expected_status = 'LIVE-VERIFIED' if r['http_status'] is not None else 'TESTED-OFFLINE'
        if r.get('verification_status') != expected_status:
            raise ValueError('HTTP evidence/verification status mismatch')
        if r['health']['status'] not in ('SUCCEEDED', 'FAILED', 'UNVERIFIED_EMPTY'):
            raise ValueError('Invalid source health status')
        if r['health']['item_count'] != len(r['items']):
            raise ValueError('Item count mismatch')
        if r['http_status'] is not None and (type(r['http_status']) is not int or not 100 <= r['http_status'] <= 599):
            raise ValueError('Invalid HTTP status')
        for i in r['items']:
            if set(i) != ITEM_FIELDS or any(not isinstance(i[k], str) for k in ITEM_FIELDS):
                raise ValueError('Only approved metadata fields may be imported')
            if not i['headline'] or len(i['headline']) > 500 or i['publisher'] != source['publisher'] or i['excerpt'] != '':
                raise ValueError('Invalid headline/publisher or unexpected probe excerpt')
            check_url(i['link'], source['allowed_domains'])
            if not instant(i['published_at']) <= instant(i['retrieved_at']) == instant(r['checked_at']):
                raise ValueError('Invalid publication/retrieval chronology')
    # File-provided sources, gonogo and enablement_draft are never authoritative.
    return [by_id[s['id']] for s in sources]


def ingest(path, root=ROOT, now=None, apply=False):
    now = now or dt.datetime.now(UTC)
    path, root = Path(path), Path(root)
    if path.stat().st_size > MAX_IMPORT_BYTES:
        raise ValueError('Probe result exceeds 20 MB import limit')
    data = json.loads(path.read_text(encoding='utf-8'))
    sources = json.loads((root/'config/sources.json').read_text(encoding='utf-8'))
    rows = validate_import(data, sources, now)
    summary = summarize(sources, rows, now)
    output = {'verification_status': data['verification_status'],
              'evidence_origin': 'USER_MACHINE_NETWORK (imported; not run in this environment)',
              'imported_at': stamp(now), 'input_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'applied': apply, 'decisions': summary['decisions'], 'gonogo': summary['gonogo'],
              'notice': 'No edition produced. Local terms review is independent of technical health.'}
    if apply:
        # Keep a recoverable pre-import registry; do not rewrite local approvals or other fields.
        backup = root/'evidence'/('sources-before-import-'+stamp(now).replace(':', '-')+'.json')
        if backup.exists():
            raise ValueError('Backup already exists; use a new import time')
        atomic(backup, sources)
        atomic(root/'config/sources.json', summary['sources'])
    atomic(root/'evidence/probe-import.json', output)
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description='THE LEDGER standalone source health probe; no packages or keys required')
    parser.add_argument('--output-dir', type=Path, default=Path.cwd())
    parser.add_argument('--ask-contact', '--ask-sec-contact', action='store_true',
                        help='Prompt privately for a real contact email used in one descriptive User-Agent for all sources')
    parser.add_argument('--describe', action='store_true', help='Print bundle identity/candidate count without network access')
    args = parser.parse_args(argv)
    sources = config('sources')
    if args.describe:
        print(json.dumps({'candidate_count': len(sources), 'engine_sha256': engine_digest(),
                          'status': 'TESTED-OFFLINE', 'notice': 'No network attempted'}))
        return 0
    if args.ask_contact and not os.environ.get('LEDGER_CONTACT_EMAIL'):
        contact = getpass.getpass('Real contact email for source requests (blank skips checks): ').strip()
        if contact:
            os.environ['LEDGER_CONTACT_EMAIL'] = contact
    if any(not s['id'].startswith('fixture-') for s in sources) and not os.environ.get('LEDGER_CONTACT_EMAIL'):
        raise SystemExit('Set LEDGER_CONTACT_EMAIL or use --ask-contact; no requests sent')
    started = dt.datetime.now(UTC)
    rows = []
    old = args.output_dir/'live_probe_results.json'
    previous = {}
    if old.exists():
        try:
            prior = json.loads(old.read_text(encoding='utf-8'))
            if prior.get('fixture') is False and prior.get('engine_sha256') == engine_digest():
                previous = {r['source_id']: r for r in prior['results']}
        except (ValueError, KeyError, TypeError):
            pass  # A corrupt prior diagnostic cannot establish history.
    with tempfile.TemporaryDirectory(prefix='ledger-probe-cache-') as temp:
        for number, source in enumerate(sources, 1):
            prior = previous.get(source['id'], {})
            previous_health = prior.get('health', {}) if prior.get('source_fingerprint') == fingerprint(source) else {}
            r = probe_source(source, dt.datetime.now(UTC), Path(temp), previous_health)
            if source['id'] in ('bls','imf','sec-press') and (r.get('robots_http_status') == 403 or r.get('http_status') == 403):
                r = probe_source(source, dt.datetime.now(UTC), Path(temp), previous_health)
                r['attempts'] = 2
            rows.append(r)
            print(f"[{number}/{len(sources)}] {source['id']}: {r['health']['status']} — "
                  f"{r['health']['reason'] or 'parse, structure and freshness passed'}", flush=True)
    data = report(sources, rows, started, dt.datetime.now(UTC))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    atomic(old, data)
    draft = args.output_dir/'live_probe_draft/SOURCES_REPORT.md'
    draft.parent.mkdir(parents=True, exist_ok=True)
    draft.write_text(markdown(data), encoding='utf-8')
    print('Return this file: '+str(old.resolve()))
    print('Draft report: '+str(draft.resolve()))
    return 0
