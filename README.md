# THE LEDGER

Understand the markets. See beyond the headlines.

An English-language, static financial newspaper for one reader. Its purpose is a short daily reading habit and understanding, with deliberate Norway/Nordic coverage when reliable sources are available. This repository is an **offline-tested local build**, not an operating news service. No GitHub repository, push, Pages configuration or external deployment has been performed.

**Status: TESTED-OFFLINE implementation; LIVE-VERIFIED returned endpoint diagnostics only.** A connected-machine probe dated 2026-10-13 reached and parsed nine sources under the previous engine; the revised engine has not been run online. All real sources remain disabled until current health, structure and reuse rights are verified. The default site displays missing coverage. The separate demo says **FIXTURE** on its edition, stories and research. See [SOURCES_REPORT.md](SOURCES_REPORT.md), [CHECKPOINT.md](CHECKPOINT.md), [FAILURE_MODES.md](FAILURE_MODES.md) and [FINAL_REPORT.md](FINAL_REPORT.md).

## Continue live verification from another machine

The three-host DNS/one-URL recheck is still blocked. Run the self-contained probe on
a connected computer: `python3 scripts/live_probe.py --ask-contact`.
Return **live_probe_results.json**. It also writes a separate draft source report.
See [LIVE_VERIFICATION.md](LIVE_VERIFICATION.md) for standalone copying, ingestion,
review requirements and remaining steps. The probe and importer are TESTED-OFFLINE;
no source has been enabled by this continuation.

## Read the local fixture preview

From this directory, with Python 3.11+ and Node 22+ for frontend tests:

```sh
python3 -m unittest discover -s tests -v
node --test tests/frontend.test.cjs
python3 -m collector.collect --fixture --output build/fixture --now 2026-10-13T05:00:00Z
python3 scripts/validate.py --root build/fixture
python3 -m http.server 8000 --bind 127.0.0.1 --directory build/fixture/site
```

Open `http://127.0.0.1:8000`. The fixed demo clock makes the fixtures reproducible; its age warning is intentionally real and becomes visible after 36 hours. A file:// preview cannot fetch JSON reliably; use the local server. Browser layout has not been verified in this environment. This sandbox also denied a local listening socket; run the preview command from an environment that permits localhost serving. No packages need installing.

For the real-mode missing-coverage preview: `python3 -m collector.collect --output build/live`, then serve `build/live/site`. This command does not silently switch to fixtures. Real source collection requires the documented verification steps first.

## Components and why they exist

|Component|Purpose / dependency justification|
|---|---|
|Python 3.11+ standard library|HTTPS, XML/JSON parsing, UTC/Oslo times, tests and atomic file operations without third-party runtime packages|
|Node built-in test runner|Tests browser logic and a small DOM simulation without frontend packages; not a production dependency|
|`collector/probe.py` and standalone probe/import scripts|Run the identical health rules on a connected machine and import bounded evidence without copying article bodies or granting reuse approval|
|`collector/http.py`|One place for allowlists, public IP/TLS pinning, robots, bounded requests and conditional metadata caches|
|`collector/adapters/`|RSS/Atom, explicit JSON schema and SEC columnar submissions; source-specific format changes fail closed|
|`normalize`, `eligibility`, `deduplicate`, `rank`|Separate evidence, identity and editorial judgments so each is inspectable|
|`registry`, `coverage`, `scope`, `gate`, `schema`, `publish`|Enforce truthful coverage, automatic scope thresholds, Oslo scheduling and immutable publication|
|`editorial.py` and `data/`|Constrained source attribution, reviewed mechanisms and beginner concepts without inference services|
|`site/` HTML/CSS/vanilla JS|Accessible static reading surface, local browser state and no backend|
|GitHub's checkout/setup/upload-pages/deploy-pages Actions|Prepared standard tools for checkout, runtimes and Pages publication; not run here|

There is no framework, database, market data service, AI API or AI infrastructure, analytics, remote font dependency, scraping framework, or unused cloud setup. Linux/macOS `fcntl` provides the local collection lock; on Windows use WSL. GitHub Ubuntu runners include the timezone database. Libre Baskerville and DM Sans are named in CSS; where absent, Georgia and Arial provide offline fallbacks. Font files are not bundled.

## Data and trust

The collector persists only allowed metadata, bounded excerpts and original descriptions grounded in the linked metadata. Response bodies exist only in memory and are never written. Cached records are sanitized, ignored by Git, capped at 2 MB per response/cache file and pruned to 7 days / 64 files / 2 MB aggregate at run start. Actions currently uses ephemeral caches, so conditional requests mainly benefit repeated local runs. No paid credentials are used; all live requests require a descriptive User-Agent with a real contact email.

Every story preserves ID, exact textual headline, publisher, canonical HTTPS URL, event/publication/retrieval/correction times, publication precision, original language, source tier, separate content type, asset classes, identifiers, excerpt, primary links, access limitations, collection status and provenance. SEC filing dates are date-only and visibly labeled; no exact release time is invented. `event_at` and identifiers stay unknown/empty unless verified. SEC's candidate endpoint covers one issuer and is a diagnostic, not market-wide equity coverage. All source domain lists and item classifications need review before activation.

P means official primary publisher; S means accountable secondary reporting; T is discovery only; X is excluded. A primary document establishes what its issuer published, not the independent truth of all its claims. Promotional and opinion content never enters news. Unclassified/administrative items require explicit substantive review; routine filing types are excluded. Headline length is bounded to reject implausible feed payloads. English-only eligibility rejects untranslated material. Funds require share class/date; crypto requires separately classified evidence; commodities require physical/futures context; derivatives require verified exchange evidence. Current generic adapters do not infer these details, so ambiguous items are rejected. Preliminary/revised data defaults to **unknown**; specific adapters must establish the revision status before labeling it.

No claims are extracted from an article body. “What happened” attributes the original title to its publisher. “Why it matters” permits a reviewed quote inside the allowed excerpt, a human-reviewed glossary mechanism, or “Explanation unavailable today.” The generic live adapters currently produce the unavailable fallback; automatic official-rationale extraction is not implemented. Unreviewed glossary entries remain visibly marked and cannot supply a story explanation. No price-movement causality is inferred.

## Ranking policy

`config/ranking.json` uses `0.30 significance + 0.20 novelty + 0.15 timeliness + 0.15 breadth + 0.20 educational_value`, each component 0–5. Initial editorial policy, not validated predictive signals.

- Significance baseline: emergency 4; profit warning/rate decision/inflation/employment/enforcement 3; earnings/energy report/research 2; filing/other 1. Up to two +1 modifiers for stated surprise, systemic scale, changed situation or magnitude; each requires supporting text and a primary source link. No extraction guesses whether an event was expected. For example, a documented two-modifier corporate warning reaches 5 and can outrank an unmodified routine rate decision at 3.
- Novelty: new document/URL 5, explicit material update 3, archived unchanged document/URL 0. Unchanged stories are excluded from resurfacing. Full local archive is consulted. A source-specific, reviewed material-update determination is required; the generic parser never invents one.
- Timeliness: 5 in the first 10% of its window, then 4 through 25%, 3 through 50%, 2 through expiry, then ineligible. Reporting 48h; official disclosure 168h; research 2,160h. These broad initial windows require source-specific editorial review before launch.
- Breadth: `min(5, 1 + number of verified configured asset classes)`. This is a modest exposure proxy, not a measurement of economic impact; broad source tags can bias it and need review.
- Educational value: rate/inflation/research 5; earnings/warning/emergency/employment/energy 4; enforcement 3; filing 2; other 1. These are subjective policy judgments.

The Top 5 diversity pass caps each publisher and every tagged asset class at two, then relaxes only to fill remaining places when no eligible alternative fits. The full edition retains all eligible items up to the explicit 30-story reading cap. No watchlist, popularity, price data, local read/saved state or publisher tier enters the score. Component scores and a reason appear in every story. Overrides require a story ID, editor, reason, UTC logged/expiry times, and a score adjustment bounded to +/-1 in `config/editorial.json`. Log weight changes in `weight_change_log`; none have occurred.

Ten real historical events are referenced in `tests/fixtures/historical.json`. Event dates and official documents were found through the research browser; replay timing and score inputs are FIXTURE assumptions. These establish regression cases, not historical optimality or performance. A professional editor should calibrate baselines on a larger, diverse corpus.

## Identity and disagreement

Dedupe uses canonical URLs, publisher-scoped document IDs, exact normalized title plus day/event type, and optional reviewed event keys. It never matches a company by name alone. Clusters preserve every source and the earliest eligible original, with explicit origin IDs so known syndicated copies count once. Different wording without a shared reviewed key is deliberately left separate; general automatic syndication detection is not built. Distinct same-company events stay separate. Conflicts compare metric, date, currency/unit, definition and dataset before retaining both values. DISPUTED clusters stay in the local research queue and out of public news. Structured claim extraction is not automatic; naturally occurring conflicts have not been verified.

## Coverage and publication

A successful HTTP response must parse, have expected canaries and plausible count/archive structure, and satisfy source-specific freshness or generous irregular-source silence thresholds. Empty, malformed and frozen feeds fail. Each source has last success, failure count, item count, request latency and publication latency. Failures are quarantined individually. Candidate baselines/cadences are provisional, not measured.

Each category is evaluated in this order:

1. No successful configured source: `NOT_CHECKED`.
2. At least one success, but no critical source configured or any critical failure: `PARTIAL`.
3. All configured critical sources succeeded: `CHECKED_WITH_STORIES` or `CHECKED_QUIET` according to eligible stories.

An optional failure adds `degraded: true` to a checked category. It does not create a fifth state or by itself make the edition partial. Quiet displays sources and Oslo check time. Filters expose the same warnings as the edition coverage panel.

## Topic filtering

The deterministic headline filter returns `KEEP`, `LOW_CONFIDENCE`, or `DROP`. E24 URL sections set a default for approved business/economy sections; explicit keyword and off-topic signals adjust that result. `LOW_CONFIDENCE` items can appear in the full edition and never enter Top 5. Each collection writes dropped headline metadata and the applied rule to `data/filtered_out.json`; the coverage panel shows `N of M items filtered`. The complete offline review of returned CNBC, E24, and FT probe samples is in `filter_report_v2.md`. Keyword rules are editorial policy and require review as the feeds change.

Automatic scope evaluation removes macro from the checked set when fewer than three primary macro sources succeed, and equities when fewer than two substantively reviewed equity sources succeed. These categories remain NOT_CHECKED in a narrower live run; the original registry is not rewritten. Default critical categories are macro and equities. If both are checked, publish FULL. Otherwise publish PARTIAL only when at least two **other** categories are checked, with missing critical categories named. Otherwise preserve the latest valid edition and write a STALE status sidecar. First run writes only a nondeployable local candidate. Fixtures are always nondeployable even if their simulated coverage passes. The schema independently re-evaluates the publication rule. `config/coverage.json` controls this policy; changing critical categories requires explicit recorded editorial justification, not a shortcut around failed checks.

## Archives, failure and maintenance

Edition date is Europe/Oslo date. The collector locks, creates an immutable `editions/YYYY-MM-DD.json`, validates, copies it into `site/editions`, then atomically replaces the latest pointer. Duplicate runs reuse the valid archive. `site/data/archive.json` holds SHA-256 integrity hashes. Do not manually edit originals. Material corrections use an append-only dated overlay:

```sh
python3 scripts/correct.py --root . --edition YYYY-MM-DD --story STORY_ID \
  --description 'Reviewed correction text' --source 'https://official-source.example/document' \
  --reviewed-by 'Editor name'
python3 scripts/validate.py --root .
```

Corrections are displayed with their source and time; the original stays available. Editorial changes must be reviewed before external publication. Automated correction discovery is not implemented.

Schedules at 04:00, 05:00, 06:00, 08:00 and 10:00 UTC pass only after 06:30 Oslo and when today's valid edition is absent. Winter's first passing trigger is 06:00 UTC; summer's is 05:00 UTC. Scheduling is best-effort: jobs can be delayed or dropped, and public schedules disable after 60 days without repository activity. Edition timestamps and the 36-hour STALE banner are the real freshness signal. A workflow/platform failure that cannot publish a status file is visible through this age warning, not instantaneous remote failure detection. Monitor Actions and re-enable schedules after prolonged inactivity. No keepalive is included; normal daily archive commits provide activity.

Review feed structure, permissions, freshness and classification monthly, and after any health failure. Review glossary and shelf documents manually before launch. Inspect publication quality, not article count. The <=5 minute habit target remains untested with a real reader. See [DEPLOYMENT.md](DEPLOYMENT.md) for exact user steps and billing constraints.

## Research bot (added 2026-11-25)

Beside the newspaper, `bot/` runs a daily experiment: it fetches prices (Yahoo), US fundamentals (SEC EDGAR) and macro series,
predicts **up or down** for ~30 Norwegian and US stocks at 1- and 3-month horizons, logs every guess in `bot_data/predictions.jsonl`,
and grades itself when the horizon passes. Scores are on the site at `track-record.html`. See [bot/PRINCIPLES.md](bot/PRINCIPLES.md)
for the Graham/Munger/Outsiders rules it applies and its honest limits. Run it locally with
`pip install -r bot/requirements.txt && python -m bot.run daily`. It does not trade and is not investment advice.
