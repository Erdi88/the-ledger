# THE LEDGER checkpoint

## Gate 0 — complete (TESTED-OFFLINE)
- Independent directory: /home/erdi/Stock_News/the-ledger. Parent is not a Git repository; no Git repository created.
- Python 3.12.3, Node 22.23.2. No Chromium/Firefox or Playwright found.
- The Edge README inspected at /home/erdi/News; untouched. ASTRO.RESEARCH not found. Aerospace ASTRO directory left untouched.
- Direct HTTPS failed: curl exit 6, Could not resolve host www.ecb.europa.eu.
- Research-browser access to official GitHub docs works; it does not verify collector connectivity.
- Failure analysis for all gates recorded before implementation in FAILURE_MODES.md.

## Next
Gate 1: record direct attempts for source candidates; use the offline branch if DNS remains unavailable.

## Gates 1–2 — complete (TESTED-OFFLINE)
29/29 direct probes failed DNS; evidence/source-probes.json records every attempt. SOURCES_REPORT.md records unknown HTTP/terms, provisional formats/cadence, zero working counts in each category and Nordic gap. All registry entries disabled. Automatic decision: OFFLINE FIXTURE BUILD. GitHub docs separately retrieved through research browser.

## Gates 3–7 — implementation in progress (TESTED-OFFLINE; validation pending)
Metadata model, pinned HTTPS client, RSS/Atom/JSON/SEC parsers, explicit eligibility, conservative clustering, deterministic scoring, health states and publication rule implemented. No live source enabled; no runtime packages. Source terms remain unknown. Next: fixtures and behavior tests before marking these gates complete.

## Gate 3 — complete (TESTED-OFFLINE)
Independent stdlib Python package, JSON policy/registry, UTC metadata, immutable archive and static renderer. Executable schema validates provenance, IDs, timestamps, excerpt bounds, fixture mode and publication rule consistency. Zero runtime packages; cache stores sanitized metadata only.

## Gate 4 — complete for offline path (TESTED-OFFLINE)
RSS, Atom, explicit official JSON and SEC submissions parsers tested. HTTPS allowlist, pinned public DNS/TLS, timeout/deadline, size and redirect caps, robots checks, source delay, SEC contact requirement and conditional metadata caching implemented. Direct feed connectivity remains unverified; all real sources disabled.

## Gate 5 — complete for offline path (TESTED-OFFLINE)
Eligibility separates publisher tier/type; strict instrument checks reject missing context. Five syndicated FIXTURE copies collapse to one; same-company earnings/enforcement remain distinct; comparable contradictory claims retain both values in DISPUTED queue. A review found promotional copies could suppress valid representatives; fixed by excluding rejected items before clustering, with regression test.

## Gate 6 — complete for offline path (TESTED-OFFLINE)
Exact requested weights and documented bounded evidence modifiers, freshness windows, archive novelty, diversity and logged override rules. Ten real historical event references replayed with explicitly simulated FIXTURE scoring inputs. No return-prediction claim. Retrospective examples are not live service evidence.

## Gate 7 — complete for offline path (TESTED-OFFLINE)
Every health/coverage/publication branch tested. Irregular silence differs from frozen regular feeds. Optional failures only degrade checked states. First live-mode run with disabled sources yields zero stories, all eight categories NOT_CHECKED, PARTIAL status, STALE flag, deployable false.

## Gate 8 — complete for offline path (TESTED-OFFLINE)
Six synthetic stories, five selected; all six required reading fields, source links, labeled explanation origins, 30 needs-human-review glossary entries, weekly older-research shelf, local copy/read/save. No unreviewed glossary entry becomes a story explanation. Genuine source audit unavailable.

## Gate 9 — complete implementation (TESTED-OFFLINE)
Responsive text-first site, requested palettes, offline serif/sans fallbacks, filters with coverage, themes, archive, correction overlays and age warning. Node DOM simulation validates behaviors. Browser/mobile layout verification NOT BUILT: no browser available.

## Gate 10 — complete local preparation (TESTED-OFFLINE)
Daily and verify workflows prepared; no external actions taken. UTC triggers and Oslo gate tested for January/July and 2026-03-29/2026-10-25; valid daily edition blocks subsequent attempts. Public-repository/approval-variable guard, standard Ubuntu and <=10 MB / 1-day Pages artifact. GitHub execution/deployment NOT BUILT.

## Gate 11 — offline checks passing (TESTED-OFFLINE)
85 Python tests passing. Nine Node behavior/DOM tests passing (the Node isolated runner reports one passing test file). Initial frontend assertion incorrectly matched the words “No analytics”; narrowed to external script markup and reran successfully. HTTP 200 parse failure evidence and cached 304 freshness regression checks added. LIVE end-to-end collection, five-original audit and natural examples remain unverified because the execution environment has no DNS.

## Next
Gate 12: finish README, deployment instructions, feature report and evidence inventory; run final checks after documentation/config review.


## Gate 12 — complete local handoff (TESTED-OFFLINE)
All requested documents, candidate registry, deterministic collection/publication pipeline, static UI, archive structure, two prepared workflows and tests are present. FINAL_REPORT.md inventories feature status, zero live source counts, Norway gap, risks, subjective ranking choices, GitHub limits, 30 glossary review items and ordered manual steps. No GitHub repository, local Git repository, push, Pages change, billing activation or external publishing occurred.

Final verification: **90 Python tests + 9 Node behavior/DOM tests passed**. Both the nondeployable six-story FIXTURE preview and the nondeployable empty real-mode site validate. Additional guards reject administrative/unclassified material, require documented source activation/corrections policy, apply narrower scope thresholds before coverage and verify correction overlays preserve original bytes. Source connectivity remains unverified. Local HTTP smoke failed with `[Errno 1] Operation not permitted` when binding the server; evidence/local-http.json records it. No headless browser was available. YAML parsed locally only; Actions and Pages were never run.

### Resume here
The offline build is complete. The next required work is on a connected machine: source/robots/reuse verification, genuine collection and original-source audit, glossary/research review, and real mobile/browser inspection. Follow DEPLOYMENT.md in order. **Not ready for live deployment approval.** Fixtures, syntax checks and unit tests do not establish a live newspaper.


## Continuation — ready for connected-machine handoff (TESTED-OFFLINE)
- Read FINAL_REPORT.md, CHECKPOINT.md, SOURCES_REPORT.md, README.md and the registry.
- Required bounded network recheck: Fed/ECB/Norges Bank DNS all failed; one Fed HTTPS fetch failed DNS. Recorded evidence/network-recheck.json. Stopped network diagnosis immediately.
- Before implementation, recorded eight probe/import failure modes and guards in FAILURE_MODES.md.
- Added collector/probe.py, generated scripts/live_probe.py, reproducible scripts/build_live_probe.py, and scripts/ingest_live_probe.py. Standalone bundle uses exact existing transport/parser/normalizer/health rules plus 29 candidates and Oslo timezone data; requires Python 3.11+, no third-party packages.
- Diagnostic GETs are robots/security bounded; output contains metadata and no body/excerpt/contact. Each candidate gets an explicit result. Separate draft never overwrites the production source report. Unsupported HTML and missing SEC contact remain visible failures.
- Import validates complete/current source and engine identities, freshness, timestamps, metadata boundaries and success evidence. Local terms/corrections review remains mandatory. Dry run writes a proposal; --apply only updates enabled flags with backup and evaluates existing gonogo policy. Imported samples never become stories.
- Added www.sec.gov to SEC's allowlist because the existing adapter's canonical links use that host. All 29 source enable flags remain false; no thresholds, frontend or editions changed.
- Tests: 113 Python tests pass (90 existing + 23 new). The initial new test expected a different spelling of the existing SEC error message; corrected the assertion and reran the full suite. Passing evidence: evidence/continuation-python-tests.txt. Single-file execution tested in an isolated temporary directory with Python -I; no network mocks are claimed as live evidence.
- Live collection, five-original audit and browser/mobile work remain NOT BUILT as verification tasks. Per the user's explicit blocked-network branch, stop here and await the returned evidence; do not install browsers or continue network diagnosis.
- Next user command from an internet-connected copy of the-ledger: python3 scripts/live_probe.py --ask-contact
- File to return: live_probe_results.json (created in the command's current directory). Exact import commands and remaining deployment steps are in LIVE_VERIFICATION.md.

## Continuation — requested offline fixes after returned connected probe (2026-10-13)

- **LIVE-VERIFIED, historical returned evidence only:** `live_probe_results.json` came from the user's connected machine. Nine endpoints returned HTTP 200 and passed the previous probe's parse/health checks: Fed, ECB, BIS, BoE news, Apple-only SEC EDGAR, Ethereum Foundation, FT, CNBC and E24. SSB returned RSS content, arXiv returned a valid zero-item RSS response, EIA supplied a yearless date, and BLS/IMF/SEC press robots returned HTTP 403. NBER and Finansavisen encountered blocked cross-domain redirects; the old result did not capture target domains. None of these observations verifies the revised engine or reuse permission.
- **TESTED-OFFLINE:** SSB adapter changed to RSS; probe classifies feed versus feed index. Irregular zero-item parsed feeds can be CHECKED_QUIET while remembered silence/invalid structure still fails. Registry has `scope` and `display_language` on all 29 sources; Apple SEC is `single_entity`, which cannot complete a category without a broad critical source. One descriptive contact User-Agent applies to all live requests; BLS/IMF/SEC press get one retry on robots HTTP 403, with continued refusal failing. Gzip decompression enforces the 2 MB expanded cap. Redirect target domains are recorded without allowlist changes. EIA yearless dates log a rejection. Conservative title filtering excludes off-topic samples from the returned CNBC/E24 metadata. Norwegian titles carry a visible language label; no translation is inferred.
- **Tests:** 124 Python tests pass; `node --test tests/frontend.test.cjs`, `node --check site/app.js`, and `python3 -m compileall -q collector scripts` pass. Standalone probe regenerated and passes `--describe` with 29 bundled candidates. All 29 sources remain disabled. No fixture file, repository, push, external publication or source allowlist was changed.
- **NOT BUILT as verification:** No post-fix connected probe, actual NBER/Finansavisen target domain, live edition, five-story audit or visual browser/mobile run. The old results cannot be imported for activation because source and engine fingerprints changed. Next run on a connected machine: `python3 scripts/live_probe.py --ask-contact`; return `live_probe_results.json`. Remain at NOT_CHECKED coverage until reviewed source activation and a genuine collection succeed.

## Continuation — recency, pointer, empty-history and routine-ranking fixes

- **LIVE-VERIFIED evidence, revised code not live-run:** the returned headline/date metadata included Ethereum 642 entries, SEC Apple 1001, a one-item BLS evergreen pointer, zero-item arXiv, and the listed Fed/BoE routine events. Under configured 168-hour official-disclosure recency, offline replay keeps 0/642 Ethereum entries and 1/1001 SEC entries at the probe timestamp. This replay uses historical returned evidence and is not a new collection.
- **TESTED-OFFLINE:** collection filters story candidates by the configured content-type window after source health; eligibility applies the same limit. BLS is `pointer`, non-critical and omitted from story/coverage/scope counts. Per-source health persists `last_nonempty_at`; first-seen empty arXiv is `UNVERIFIED_EMPTY` and yields NOT_CHECKED, while a source with recent prior non-empty history may be CHECKED_QUIET through `max_silence`.
- **TESTED-OFFLINE:** NBER stores user-reported `back.nber.org` only in an inactive allowlist candidate requiring human approval. DN and Finansavisen are disabled by policy as paywalled, and their probe requests are skipped. Fed application approvals, enforcement terminations and BoE committee minutes have significance 0 and are omitted from Top 5 while remaining eligible for the full edition. The CNBC/E24 topic matcher was not changed; `filter_report.md` enumerates 30 CNBC and 39 E24 headline outcomes with the applied rule.
- **EIA:** the returned parser failure proves an observed yearless date, not that every feed item is yearless; bodies were not stored. EIA remains disabled, its reason is recorded, and the parser never guesses a year.
- **Tests:** 128 Python tests pass; the frontend test file, JavaScript syntax, Python compilation and standalone `--describe` pass. Probe bundle has 29 candidates. All source flags remain false; fixtures were not changed. No brotli handling, active allowlist expansion, network run, repository action or publication occurred.
- **NOT BUILT:** post-fix live health, actual story collection, five-original audit and browser/mobile visual run. The next connected step remains `python3 scripts/live_probe.py --ask-contact`, followed by terms review; no source is enabled by this continuation.

## Continuation — three-outcome topic filter (offline only, 2026-10-13)

- **TESTED-OFFLINE:** Replaced the title-only boolean gate with deterministic `KEEP`, `LOW_CONFIDENCE`, and `DROP` outcomes in `collector/topic.py`. E24 section paths establish the default; Norwegian stem/substring and requested English financial terms adjust it. Topic-based off-topic terms exclude sports, lifestyle, campaign, donor, raid, ambassador and career content. Strong economic terms override an off-topic match only to LOW_CONFIDENCE. Trump and Republican are not standalone off-topic terms.
- LOW_CONFIDENCE items remain eligible for the full edition with a visible label and are excluded from Top 5. Every DROP from successful collection is written with headline, canonical link, publisher, timestamps, source and rule to `data/filtered_out.json`. Edition coverage shows `N of M items filtered`. The count and JSON records are produced by real collection; no probe samples were written into production data.
- Added golden checks against the returned CNBC/E24 **probe samples**, including every requested KEEP / flexible / DROP example, E24 section decisions, compound matching and Top 5 exclusion. `filter_report_v2.md` reviews all 30 CNBC, 39 E24 and 10 FT probe headlines with applied rules and v1 comparison. FT had no v1 rows.
- **TESTED-OFFLINE:** `python3 -m unittest discover -s tests` — 134 tests pass. `node --test tests/frontend.test.cjs` passes; frontend test covers the displayed filter count. Rebuilt the standalone probe bundle to keep its embedded production modules synchronized. No sources, fixtures, or returned probe evidence changed. No network test was run.
- **LIVE-VERIFIED:** The underlying headline/link/timestamp metadata in the returned probe remains historical user-machine evidence. The v2 classifications and their report are not live collection evidence.
- **NOT BUILT:** Post-filter real collection, edition/story audit, browser/mobile visual check and deployment. All source enable flags remain false.

## Continuation — topic filter boundary repair (offline only, 2026-10-13)

- **TESTED-OFFLINE:** English short terms now require whole-word, case-insensitive matches; explicit Norwegian stems still match compounds. Matched terms are deduplicated and carried in filter results/collected metadata. Generic terms market, retail, trade, price, regnskap and inntekt cannot KEEP alone. E24 section defaults without keywords are LOW_CONFIDENCE; Naeringsliv and energy sections require strong terms to KEEP. AI model/chip product headlines remain LOW_CONFIDENCE unless a listed financial term also appears.
- Added regression cases for turmoil/oil, Chipotle/chip, SoftBank/bank, Fed's/fed, Hammack/eia/sec, weak standalone terms, technology stories and Top 5 exclusion. Existing probe-sample golden cases remain passing.
- Rebuilt [scripts/live_probe.py] in sync with its embedded topic module. Regenerated [filter_report_v3.md] from the untouched 30 CNBC, 39 E24 and 10 FT returned probe samples, showing v2→v3 results.
- **TESTED-OFFLINE:** Full Python suite: 137 tests pass; Node frontend suite passes; edited Python modules compile. No source flags changed (0/29 enabled), no fixture or probe-result file changed, and no network was used.
- Report classifications: CNBC 18 KEEP / 4 LOW_CONFIDENCE / 8 DROP; E24 19 / 12 / 8; FT 3 / 3 / 4. Historical probe metadata remains **LIVE-VERIFIED**; v3 classification is **TESTED-OFFLINE**.
