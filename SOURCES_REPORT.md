# Source reality check — current offline-fix update

**LIVE-VERIFIED (returned user-machine probe dated 2026-10-13):** nine endpoints returned HTTP 200, parsed and passed the *previous* health rules: Federal Reserve, ECB, BIS, Bank of England news, Apple-only SEC EDGAR submissions, Ethereum Foundation, FT, CNBC and E24. This is endpoint evidence, not approved reuse, substantive coverage, a working edition or verification of the revised code. All 29 sources remain disabled. The earlier DNS-only attempt is preserved below as historical context.

**TESTED-OFFLINE (this revision):** SSB's endpoint was observed as `application/rss+xml` in the returned probe, so its adapter is now RSS. The next probe records `feed` versus `feed_index`; the old probe did not preserve the response body, so SSB's exact kind is still **unknown**. ArXiv's valid zero-item irregular feed is accepted as quiet only when structure passes and remembered silence has not exceeded `max_silence`. The Apple SEC feed is `single_entity`, so it cannot complete equity coverage alone. BLS, IMF and SEC press had robots HTTP 403 in the returned probe; the next run sends one descriptive contact User-Agent for every source and retries those three once if robots still returns 403. A refusal remains a failure. EIA's observed yearless date is rejected with an explicit log reason. Gzip is decoded with the 2 MB limit enforced on expanded content. CNBC and E24 off-topic headline samples are excluded by the title gate. Norwegian source language is retained and visibly labeled.

**Redirect domains:** The returned probe failed NBER and Finansavisen on cross-domain redirects but did not record targets. The user later identified NBER's target as `back.nber.org`; the Finansavisen authentication/paywall hostname remains unknown. The probe records redirect domains while keeping redirects blocked; no target is active in either allowlist.

## Follow-up offline policy updates

**TESTED-OFFLINE:** The returned NBER target is now known from the user's report as `back.nber.org`; it is stored only under `allowlist_candidates` with `active: false` and `approval_status: needs human approval`. It is absent from `allowed_domains`. DN and Finansavisen are explicitly `disabled_by_policy: paywalled`; probes skip requests to them. BLS is now `content_type: pointer`, non-critical, excluded from story candidates and coverage. Ethereum's returned 642 items yield 0 within its configured 168-hour disclosure window; Apple SEC's 1001 filings yield 1 within that window at the probe timestamp. These are offline recency calculations on LIVE-VERIFIED headline/date metadata, not a new collection.

For arXiv, the old result proves only that its feed parsed with zero entries on that run. It contains no prior non-empty history, so under the revised rule that observation is **UNVERIFIED_EMPTY**, not checked quiet. A later non-empty successful response will establish `last_nonempty_at`; only then can an empty feed be CHECKED_QUIET, until `max_silence` expires. EIA's parser stopped at an observed yearless date. Since bodies are not stored, the old file cannot establish whether *every* EIA entry lacked a year. EIA remains disabled until a live review verifies all dates; the code never guesses a year.

Fed bank application approvals, Fed enforcement terminations and BoE committee minutes now have significance 0 and are excluded from the Top 5 by ranking policy; eligible items remain in the full edition. The existing CNBC/E24 topic matcher was not changed. [filter_report.md](filter_report.md) lists all 30 CNBC and 39 E24 headlines and their existing keep/drop rule, with classification marked TESTED-OFFLINE.

**NOT BUILT as live verification:** a post-fix connected probe, reuse review, source activation, genuine edition and five-story original audit. Current go/no-go for approved operational sources remains 0 working because none is enabled or legally reviewed. No category is shown as checked in the product.

---

# Initial source reality check — historical local DNS-only attempt

**Collector network unavailable. All 29 direct candidate attempts failed before an HTTP response (DNS resolution). Collection and publication are TESTED-OFFLINE. No live newspaper has been verified.** The research browser separately retrieved official GitHub documentation; that does not establish feed availability.

Evidence: `evidence/source-probes.json` contains per-URL errors, UTC attempt times and measured latency. HTTP status is **unknown**, never invented as 200. Endpoint formats below are candidates, not confirmed formats. Cadence and substantive assessments are provisional editorial expectations. Terms and robots permission remain unverified for every source; all live sources are disabled, and excerpt allowance is zero pending review. An accessible headline is not automatically reusable.

## Continuation: connected-machine handoff (TESTED-OFFLINE)

A fresh three-host DNS check (Fed, ECB, Norges Bank) and one Fed HTTPS fetch failed
with temporary name-resolution errors. See `evidence/network-recheck.json`. No
additional network diagnosis or live-source claim followed. The historical table
below is unchanged.

Run `python3 scripts/live_probe.py --ask-contact` on a connected machine and
return `live_probe_results.json`. This supersedes the older HEAD-only probe for
activation evidence: it performs production parsing, normalization and health
checks. Its draft goes to `live_probe_draft/SOURCES_REPORT.md`, leaving this report
intact. Import with `python3 scripts/ingest_live_probe.py live_probe_results.json`
(dry run); activation also requires independently documented local reuse review.
See [LIVE_VERIFICATION.md](LIVE_VERIFICATION.md). No candidate is enabled yet.

## Candidate attempts

|Candidate|Endpoint / expected format|HTTP / latency ms|Cadence|Substance (unverified)|Reuse decision|
|---|---|---|---|---|---|
|Federal Reserve|[rss](https://www.federalreserve.gov/feeds/press_all.xml)|unknown / 7.5|regular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|ECB|[rss](https://www.ecb.europa.eu/rss/press.html)|unknown / 6.9|regular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|Norges Bank|[html](https://www.norges-bank.no/en/news-events/news-publications/RSS/)|unknown / 6.4|irregular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|Statistics Norway|[html](https://www.ssb.no/en/rss)|unknown / 5.7|regular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|BLS|[rss](https://www.bls.gov/feed/bls_latest.rss)|unknown / 0.5|regular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|EIA|[rss](https://www.eia.gov/rss/todayinenergy.xml)|unknown / 0.1|regular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|Eurostat|[html](https://ec.europa.eu/eurostat/web/rss)|unknown / 0.4|regular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|BIS|[rss](https://www.bis.org/doclist/all_pressrels.rss)|unknown / 0.4|irregular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|IMF|[html](https://www.imf.org/en/News/RSS)|unknown / 0.3|irregular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|Bank of England|[rss](https://www.bankofengland.co.uk/rss/news)|unknown / 0.3|irregular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|Bank of England research|[rss](https://www.bankofengland.co.uk/rss/working-papers)|unknown / 0.6|irregular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|SEC EDGAR|[sec](https://data.sec.gov/submissions/CIK0000320193.json)|unknown / 0.6|irregular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|Euronext / NewsWeb|[html](https://newsweb.oslobors.no/)|unknown / 1.0|irregular|CANDIDATE ONLY: mixed; inspect material disclosures vs routine notices|Disabled; terms unknown|
|Finanstilsynet|[html](https://www.finanstilsynet.no/en/news-archive/)|unknown / 0.7|irregular|CANDIDATE ONLY: mixed; enforcement vs administrative notices|Disabled; terms unknown|
|NBER|[rss](https://www.nber.org/rss/new.xml)|unknown / 0.5|irregular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|arXiv q-fin|[rss](https://rss.arxiv.org/rss/q-fin)|unknown / 0.1|irregular|CANDIDATE ONLY: research; individual paper licenses differ|Disabled; terms unknown|
|SSRN|[html](https://www.ssrn.com/index.cfm/en/)|unknown / 0.5|irregular|CANDIDATE ONLY: research; permission unknown|Disabled; terms unknown|
|Vanguard official documents|[html](https://investor.vanguard.com/investment-products/etfs)|unknown / 0.5|irregular|CANDIDATE ONLY: mixed; prospectuses vs promotion|Disabled; terms unknown|
|Ethereum Foundation|[rss](https://blog.ethereum.org/feed.xml)|unknown / 0.7|irregular|CANDIDATE ONLY: developer claims; independent verification needed|Disabled; terms unknown|
|SEC press releases|[rss](https://www.sec.gov/news/pressreleases.rss)|unknown / 0.4|irregular|CANDIDATE ONLY: substantive|Disabled; terms unknown|
|Reuters|[html](https://www.reuters.com/)|unknown / 0.4|regular|CANDIDATE ONLY: news; reusable feed unknown|Disabled; terms unknown|
|Associated Press|[html](https://apnews.com/hub/business)|unknown / 0.1|regular|CANDIDATE ONLY: news; reusable feed unknown|Disabled; terms unknown|
|Financial Times|[rss](https://www.ft.com/rss/home)|unknown / 0.3|regular|CANDIDATE ONLY: restricted; permission unknown|Disabled; terms unknown|
|CNBC|[rss](https://www.cnbc.com/id/100003114/device/rss/rss.html)|unknown / 0.5|regular|CANDIDATE ONLY: news; terms review required|Disabled; terms unknown|
|MarketWatch|[rss](https://feeds.content.dowjones.io/public/rss/mw_topstories)|unknown / 0.2|regular|CANDIDATE ONLY: news; terms review required|Disabled; terms unknown|
|E24|[rss](https://e24.no/rss)|unknown / 0.4|regular|CANDIDATE ONLY: news; terms review required|Disabled; terms unknown|
|Dagens Næringsliv|[html](https://www.dn.no/)|unknown / 0.5|regular|CANDIDATE ONLY: restricted; permission unknown|Disabled; terms unknown|
|Finansavisen|[html](https://www.finansavisen.no/)|unknown / 0.4|regular|CANDIDATE ONLY: restricted; permission unknown|Disabled; terms unknown|
|Nikkei Asia|[html](https://asia.nikkei.com/)|unknown / 0.4|regular|CANDIDATE ONLY: restricted; permission unknown|Disabled; terms unknown|

## Verified working sources by asset class

|Asset class|Working primary|Working news|Assessment|
|---|---:|---:|---|
|equities|0|0|NOT_CHECKED; substantive coverage unverified|
|funds|0|0|NOT_CHECKED; substantive coverage unverified|
|crypto|0|0|NOT_CHECKED; substantive coverage unverified|
|macro|0|0|NOT_CHECKED; substantive coverage unverified|
|bonds|0|0|NOT_CHECKED; substantive coverage unverified|
|fx|0|0|NOT_CHECKED; substantive coverage unverified|
|commodities|0|0|NOT_CHECKED; substantive coverage unverified|
|derivatives|0|0|NOT_CHECKED; substantive coverage unverified|

Free coverage is unproven for every category here. Official macro data and central-bank documents are the most defensible candidates for a later narrow launch. Official filings can establish company events but do not supply independent explanation. Funds require dated share-class documents. Crypto developer claims do not establish independent facts. FX and bonds cannot inherit broad coverage merely because a macro feed exists: item-level classification and category-specific critical sources must be reviewed. Derivatives and commodities need instrument-specific official documents. No paid or paywalled content has been collected.

## Norway / Nordics

Norges Bank, SSB, NewsWeb/Euronext and Finanstilsynet were attempted, along with E24, DN and Finansavisen. None yielded an HTTP response in the execution environment. **Meaningful Norwegian coverage is not verified.** Monetary policy, statistics and material company disclosures are promising substantive candidates; routine exchange notices are not enough. Norwegian-language items must retain their original language and title; no automatic translation is implemented. Other Nordic countries currently have no verified sources.

## Automatic scope decision (Gate 2)

`config/gonogo.json`: macro primary >=3, Nordic >=1, substantive equity sources >=2, overall >=5. Observed: 0, 0, 0, 0. Decision: **OFFLINE FIXTURE BUILD**, not FULL SCOPE. All real categories are NOT_CHECKED. Synthetic fixtures exercise the architecture and presentation, never the availability of a real service. Expansion requires real feed parse/health evidence, documented robots and reuse terms, source-specific thresholds, and the five-story human audit before a deployment approval.

## Live verification on a connected machine

1. `python3 scripts/probe_sources.py` — repeat availability probes; inspect `evidence/source-probes.json`.
2. Open each proposed source's official feed information, reuse terms and robots.txt. Record terms URL, permission rationale, `last_reviewed`, exact allowlisted domains, suitable cadence/thresholds, source tier and excerpt allowance in `config/sources.json`. Enable only approved sources. HTML candidates are discovery pages, not implemented scraping adapters.
3. Set `LEDGER_CONTACT_EMAIL` to a real contact email for one descriptive User-Agent across all sources, including SEC, in the local environment / Actions secret. No paid key is needed. Do not commit the contact value.
4. `python3 -m collector.collect --output build/live` — genuine local run; inspect `build/live/data/run.json` and its sanitized per-source evidence.
5. `python3 scripts/validate.py --root build/live`; audit five original documents, dates, figures and event associations using `evidence/LIVE_AUDIT.md`.
6. Run the tests and inspect the local site. Fixture output is never promoted to live output.

## GitHub documentation (research-browser verification only)

Retrieved from current official documentation during this build:

- [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions): standard hosted runners in public repositories and Pages builds are free. Free account allowance: 2,000 minutes/month for private repository use, 500 MB artifact storage shared with Packages, 10 GB cache per repository. Larger runners always charge. Storage overages and private runner minutes can charge when billing is enabled. No payment method means usage is blocked at quota. Account billing configuration was not inspected.
- [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits): Free supports public repositories; private-repository Pages requires a qualifying paid plan. Published site maximum 1 GB; source repository recommended <=1 GB; soft bandwidth 100 GB/month; deployment timeout 10 minutes; soft 10 builds/hour excludes custom Actions publishing workflows. This public newspaper must contain no secrets or private reading state.
- [Scheduled workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule): schedules may be delayed/dropped, run on default branch, and public repository schedules are disabled after 60 days without repository activity. Daily edition commits provide normal activity; after a prolonged failure, manually re-enable the workflow. No artificial keepalive is necessary.

These are documentation facts, not a verification of this user's account, a workflow execution, or a Pages deployment.
