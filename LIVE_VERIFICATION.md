# Connected-machine handoff

**Status: TESTED-OFFLINE.** The continuation checked DNS for the Federal Reserve,
ECB and Norges Bank and attempted one HTTPS fetch. All failed DNS. Evidence is in
`evidence/network-recheck.json`. No further source/network diagnosis was performed.
No source was enabled and no story, edition, repository or deployment was created.

The new probe/import tooling passed offline tests. A passing mock response is a
**FIXTURE**, not proof that any source works. The five-real-story collection and
audit remain **NOT BUILT** as live verification tasks.

## Run this on your internet-connected machine

Requires Python 3.11 or newer. No pip packages, keys, paid services or checkout are
required by the generated standalone file. From your copy of `the-ledger`, run:

```sh
python3 scripts/live_probe.py --ask-contact
```

Alternatively, copy **only** `scripts/live_probe.py` to another computer and run:

```sh
python3 live_probe.py --ask-contact
```

On Windows, `py -3.11` (or your installed newer Python launcher) can replace
`python3`. The script includes the Oslo timezone data it needs.

The private prompt asks for a **real contact email** for one descriptive THE LEDGER
User-Agent used with every source, including SEC. This is not an API credential.
It is used only in memory/request headers and is not written to results. If
`LEDGER_CONTACT_EMAIL` is already set, no prompt occurs. A blank answer aborts
without sending requests.

Allow the command to finish. It prints progress for all 29 candidates, including
failures, and creates these files in your **current directory**:

- **`live_probe_results.json` — return this file.** It contains source identity,
  HTTP/robots/parser/health evidence, metadata samples, timestamps and the draft
  go/no-go result. It contains no full article bodies or environment variables.
- `live_probe_draft/SOURCES_REPORT.md` — the readable draft, for your inspection.
  It does not overwrite the existing project `SOURCES_REPORT.md`.

A failed or blocked candidate still produces a row. Keep and return the result even
if many sources fail. No browser automation, scraping, publication or source
activation occurs in this command. Probe results should be returned promptly;
activation imports require evidence from the last 24 hours. Older results remain
useful for diagnosis, but must be rerun before activation.

## What the probe checks

The single file bundles byte-for-byte copies of the current production HTTPS client,
RSS/Atom/JSON/SEC parsers, normalization and health functions. It applies HTTPS/domain
and public-IP restrictions, TLS hostname verification, robots, response deadlines,
size and redirect limits, and the configured request delay. It then requires:

1. A valid HTTP response with a fresh body (200; an unsolicited 304 fails because
   this diagnostic requests a full response).
2. Successful parsing and required fields/structure, including canonical URLs and
   publication timestamps.
3. Plausible item count versus configured baseline and previous-run archive checks.
4. For regular feeds: newest publication inside `max_staleness`. For irregular
   feeds: available, structurally valid content inside generous `max_silence`;
   zero items can be healthy when structure passes and remembered silence is in bounds.

Repeat runs in the same output directory consult previous compatible results for
archive-collapse checks. A first run has only the registry baseline; it cannot
establish an empirical archive history. Body content is processed in memory and
never cached. Exported items contain only headline, canonical link, publisher,
publication/retrieval timestamps and an **empty excerpt**. Diagnostic excerpts are
always omitted while reuse rights are being established (zero is within the
25-word limit).

This command examines disabled candidates without granting reuse permission or
changing the production collection gate. The diagnostic uses bounded robots-aware
GETs; `Client.fetch` still requires approved terms for production. Known prohibitions
must still be respected. HTML candidate discovery pages are recorded as unavailable
adapters, even when their HTTP request succeeds. They cannot pass feed health merely
by returning a page. Unsupported endpoints need explicit reviewed replacements;
there is no automatic source discovery or scraping.

A result marked LIVE-VERIFIED records an actual HTTP response on the machine running
the probe, including failures such as 403 or a 200 login page. **Only a separate
SUCCEEDED health result** counts as technically healthy. Neither label establishes
reuse permission, independent truth, substantive content or broad market coverage.

## Ingest the returned JSON in the existing project

First run a dry import from the project root:

```sh
python3 scripts/ingest_live_probe.py /path/to/live_probe_results.json
```

This makes no network request, changes no source enable flags and creates no
edition. It writes `evidence/probe-import.json` with proposed enablement, reasons,
and a fresh go/no-go evaluation using `config/gonogo.json`.

The importer refuses FIXTURE/unknown-origin results, missing or duplicate sources,
old/future timestamps, mismatched engine or source-health fingerprints, unexpected
article fields, unsafe links, and inconsistent claimed health. It re-evaluates
freshness at import time. The file's `sources`, `enablement_draft` and `gonogo`
sections are informational; they cannot override the local registry or policy.
Returned JSON is data, never executable code. Imported evidence is explicitly
attributed to the user's machine, not claimed as a collector run in this workspace.
It is not cryptographic attestation of the remote machine.

**Before activation**, independently review and record in local
`config/sources.json`:

- Reuse rationale and official `terms_url`, `license_note`, `terms_approved: true`
  and actual `last_reviewed` date. Set an excerpt allowance only if supported.
- A corrections policy URL for an S-tier publisher. T/X sources remain disabled.
- Verified substantive company content (`substance_verified: true`) before counting
  a source toward the equity threshold. Inspect meaningful Norway/Nordic content.
- Appropriate critical-source choices, actual category scope and measured health
  baselines. Current candidate mappings are provisional.

Then apply the verified proposal:

```sh
python3 scripts/ingest_live_probe.py /path/to/live_probe_results.json --apply
```

Only enable flags change. Sources with failed/expired health or missing local review
stay disabled; a previously enabled source that fails is disabled. The pre-import
registry is backed up under `evidence/sources-before-import-<timestamp>.json`.
The command does not lower the macro/equity thresholds, edit articles, mark sources
as legally reviewed, or publish the imported samples.

No sources currently have approved reuse records. Therefore a first dry import may
show technically healthy feeds but **zero enabled sources**. That is the intended
separation of evidence and approval, not a reason to override the guard.

## Keep the single-file copy in sync

The committed `scripts/live_probe.py` is generated, not hand-maintained. Its trusted
local sources are `collector/probe.py`, production parser/security/health modules,
and the current registry/config. The bundler is justified so the exact health rules
can run on a computer that has only this one file.

If a feed URL, adapter, allowlist, language/category or health threshold changes,
regenerate the probe **before** another run:

```sh
python3 scripts/build_live_probe.py
```

Run that generator in this Linux checkout (it reads the installed Europe/Oslo
zoneinfo file). The resulting single-file probe works on other supported Python
platforms. Local terms-review and enable flags may change after a probe; endpoint
and health policy changes require new evidence. The importer checks the full current
engine/policy digest, so changed code or ranking/editorial policy may also require a
fresh bundle/probe. The test suite checks that embedded code/config exactly match
the checkout. The SEC canonical document host `www.sec.gov` was added to its existing
allowlist because the existing SEC adapter emits those links; SEC remains disabled.

## Remaining steps before deployment

1. Return `live_probe_results.json`. Resolve failed candidate URLs/adapters and
   rights/substance reviews from the evidence, then import without relaxing policy.
2. On the connected machine, run a **genuine** collection:
   `python3 -m collector.collect --output build/live`, then
   `python3 scripts/validate.py --root build/live`. Inspect source health and
   category coverage. Probe samples are not edition input.
3. Audit five published real stories against originals using
   `evidence/LIVE_AUDIT.md`: original publisher/link, publication versus event time,
   numeric claims, tier/type, event association, dedupe and uncertainty. Do not
   manufacture five stories to reach the target.
4. Perform browser/mobile verification and glossary/research review. This
   continuation stops at the blocked-network handoff as requested; it did not
   install a browser or attempt another preview server. Existing manual checks are
   in DEPLOYMENT.md step 2 (320/375/768px and desktop, overflow, themes, filters,
   archive, keyboard, clipboard fallback, blocked storage, stale/partial warnings).
5. Review the live scope, source report and publication decision. Confirm account
   settings and the $0 public-repository plan described in DEPLOYMENT.md.
6. Only after your later deployment approval, follow the remaining numbered
   deployment steps yourself. No repository creation, push or deployment has been
   performed in this continuation.
