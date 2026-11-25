# Failure analysis, written before implementation

Each stage has five explicit risks and its planned guard. Test names and evidence are recorded in CHECKPOINT.md after implementation. Offline tests never establish network availability.

## Gate 0 — environment
1. Damage unrelated work → isolated the-ledger directory, no parent Git changes.
2. Mistake ASTRO aerospace files for ASTRO.RESEARCH → inspect names and README only.
3. Assume network works → direct DNS/HTTPS probe with error evidence.
4. Misrepresent tools → record Python, Node, browser availability.
5. Leak credentials → no environment dumps or secret reads.

## Gate 1 — sources
1. HTTP 200 login page mistaken for feed → structural parser canaries.
2. Accessible content mistaken for licensed content → independent terms approval required.
3. Search browser mistaken for collector network → separate evidence/status.
4. Administrative announcements counted as research → classify content and substance.
5. Invented source uptime → per-candidate attempt, status nullable on DNS failure.

## Gate 2 — scope
1. Invent coverage to reach threshold → machine-readable thresholds.
2. Count disabled sources → only verified usable sources count.
3. Count news as primary → tier-specific totals.
4. Ignore Norway → explicit Nordic requirement.
5. Treat offline as verified scope → offline decision never deployable.

## Gate 3 — model
1. Discovery date replaces publication date → distinct UTC timestamps.
2. Invent tickers → identifiers empty unless explicitly verified.
3. Raw bodies accumulate → sanitized metadata cache only, retention bounds.
4. Mixed fixtures/live → edition and story mode validation.
5. Frontend hardcodes claims → JSON-only rendering.

## Gate 4 — collection
1. SSRF via redirect/DNS rebinding → public IP validation and TLS connection pinned to validated IP.
2. Huge responses or hanging sites → response cap, timeout, redirect cap.
3. Feed injection/XSS → strip markup; frontend textContent.
4. Robots/rate limits ignored → robots check, source delay, no automatic retry storms.
5. Conditional response hides frozen data → cached metadata re-evaluated for freshness.

## Gate 5 — eligibility/dedupe
1. Opinion shown as fact → separate type and eligibility.
2. Syndication appears independent → cluster explicit origin/event keys, independent origins list.
3. Distinct company events merged → event type plus date/document constraints.
4. Contradiction silently dropped → preserve claims and quarantine DISPUTED clusters.
5. Promotion legitimized by ranking → rejection precedes scoring.

## Gate 6 — ranking
1. Routine rate decision always wins → bounded evidence-backed modifiers.
2. Guessed surprise → modifiers require supporting text and link.
3. Provenance or reading history changes score → fixed five-component formula.
4. Research expires like breaking news → content freshness windows.
5. Diversity hides important news → only Top 5 reordered, complete eligible list retained.

## Gate 7 — coverage/publication
1. Empty feed becomes quiet day → empty response fails health.
2. Research inactivity becomes outage → generous irregular silence threshold.
3. Optional failure makes edition partial → separate degraded Boolean.
4. Equity outage concealed by macro → category states and publication rule tests.
5. Failed first run published → deployable false and fallback status file.

## Gate 8 — reading
1. Mechanism asserted as event effect → only human-reviewed generic mechanism allowed.
2. Unreviewed glossary appears authoritative → needs human review label on every entry.
3. Older paper looks new → separate shelf and prominent publication date.
4. Clipboard leaks data → local-only fixed pack with no browser state.
5. Corrections disappear → timestamped correction overlay, original edition immutable.

## Gate 9 — frontend
1. Overflow on phones → fluid width, wrapping, no data tables.
2. JS fetch failure leaves plausible news → explicit unavailable/stale notice.
3. Archive date confused with today's date → edition timestamp always displayed.
4. Storage failure breaks reading → guarded localStorage and clipboard fallback.
5. Low contrast/inaccessible controls → supplied palettes, semantic controls, focus styles.

## Gate 10 — automation
1. DST misses publication → trigger simulation across winter/summer/transitions.
2. Duplicate cron overwrites edition → Oslo gate plus file lock and immutable create.
3. Failed collection replaces last valid edition → pointer update only after validation.
4. GitHub private/large runners incur costs → public guard, standard Ubuntu, no paid services.
5. Schedule stops or delays → visible age warning, documented monitoring and inactivity rule.

## Gate 11 — verification
1. Fixture evidence labeled live → mode assertions and separate output roots.
2. Tests duplicate implementation → branch/behavior assertions and adverse inputs.
3. Untested UI claimed verified → report browser absence explicitly.
4. Historical example contains fabricated facts → linked real event metadata; hypothetical score inputs labeled FIXTURE.
5. Validation misses archive mutation → digest manifest and correction overlay.

## Gate 12 — handoff
1. Premature deployment approval → explicit unmet network/legal/browser gates.
2. Stale docs contradict code → final validation and config-derived coverage report.
3. Glossary review omitted → complete 30-entry review list.
4. Account cost assumed zero → official limits plus account settings unknown.
5. Maintenance appears automatic → feed/terms reviews and scheduled health checks documented.

## Connected-machine probe and imported evidence (before implementation)
1. A returned HTTP 200 gets called a healthy source → reuse the production parser, normalization and health functions; test stale/empty/HTML responses.
2. A healthy endpoint silently grants reuse rights → probe is diagnostic, exports no excerpts until review, and importer requires locally recorded terms/corrections review independently.
3. FIXTURE, stale, incomplete or mismatched results enable sources → explicit mode, current policy/source fingerprints, complete candidate set, import age limit and re-evaluated freshness.
4. A standalone copy drifts from production health rules → reproducibly embed the exact current modules/config and verify their digest before import; test single-file execution outside the checkout.
5. Full source bodies or a SEC contact leak in the returned file → persist only bounded headline/link/timestamps/publisher metadata and diagnostics; strip excerpts for unreviewed probes; never serialize User-Agent/environment.
6. An unsupported HTML source or a missing SEC contact silently disappears → one explicit result per candidate, including blocked/not-built reasons; no automatic scraping or guessed contact.
7. Imported data mutates editions or executes content → strict JSON/URL/schema validation, dry-run default, explicit apply for registry enable flags only; never publish imported samples.
8. Probe passes once but import treats it as a present-day collection → recheck health at import time, record external evidence origin, and keep actual edition collection/audit as separate required steps.

## Offline fixes after returned probe — TESTED-OFFLINE

|Failure mode|Guard / test|
|---|---|
|An RSS directory is mistaken for an article feed|Probe distinguishes `feed_index` from `feed`; collector rejects known indexes. FIXTURE feed/index test. Ambiguous undated XML remains unknown and fails parsing.|
|A valid empty irregular feed is called failed, or an old silent feed is called quiet|Parsed feed structure is required; an empty irregular feed may succeed, but a remembered newest publication beyond `max_silence` fails. FIXTURE empty/304/silence tests.|
|One-company SEC filings are presented as market-wide equity coverage|`single_entity` cannot be a broad critical source; coverage stays PARTIAL until a broad critical source succeeds. FIXTURE coverage tests.|
|A forbidden robots response is bypassed after a retry|One retry uses the same honest contact User-Agent; 403 still fails. FIXTURE retry/robots tests.|
|Compressed input expands past the size cap|Gzip is streamed with an expanded 2 MB cap. FIXTURE compressed-bomb test.|
|Undated or unrelated headlines become plausible news|Yearless dates fail; a conservative financial-title gate rejects off-topic CNBC/E24 samples before ranking. Real titles can be missed or misclassified, so editorial review remains required.|
|A Norwegian title is shown without warning about language|`display_language` is carried into edition JSON and shown in story metadata; FIXTURE renderer assertion. No translation is inferred.|

## Recency, pointers and routine notices — TESTED-OFFLINE

|Failure mode|Guard / test|
|---|---|
|Large historical archives are mistaken for fresh stories|Candidates are filtered using the configured per-content-type publication window after source health is computed; eligibility repeats the check. Returned Ethereum/SEC metadata tests ensure old entries are excluded.|
|An evergreen statistics pointer makes macro coverage look healthy|BLS is `pointer`, non-critical, excluded from candidates, broad-scope counts and coverage. FIXTURE collection and coverage assertions.|
|First-seen empty feed is called quiet|`last_nonempty_at` persists only after a successful non-empty response; empty irregular sources without it report `UNVERIFIED_EMPTY`. FIXTURE arXiv check.|
|A redirect is silently allowlisted or paywalled publisher queried|NBER redirect target is an inactive human-approval candidate; DN and Finansavisen are skipped by policy. Registry validation rejects activation and tests the inactive domain.|
|Routine official notices occupy all Top 5 slots or disappear entirely|The configured routine event types have significance zero and are omitted by `select_top`, while eligible stories remain in the edition list. FIXTURE Fed/BoE headline replays.|
|Yearless EIA timestamps are guessed or silently accepted|Parser rejects with the raw date in its error; EIA remains disabled pending a live all-items date review. No year inference path exists.|
|Topic review changes the live filter unintentionally|`filter_report.md` is generated from returned CNBC/E24 headlines and current expressions; it records all rows and decisions without changing the title matcher.|
