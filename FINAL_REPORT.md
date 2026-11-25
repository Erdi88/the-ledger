# THE LEDGER — current status after offline fixes

**Not ready for deployment approval.** The user-machine probe supplied LIVE-VERIFIED endpoint evidence for nine sources under the previous probe code, including E24 and the Apple-only SEC feed. No source is enabled or reuse-approved, and no real edition or five-story audit has run. The original offline baseline follows below and should be read as historical; its zero-HTTP finding described this sandbox before the returned probe.

|Requested item|Status|Result / limit|
|---|---|---|
|Three-outcome topic filter and Top 5 exclusion|TESTED-OFFLINE|`collector/topic.py` returns KEEP / LOW_CONFIDENCE / DROP; low-confidence items are full-edition only; each collected drop retains its rule in `data/filtered_out.json`; coverage displays the filtered count|
|CNBC, E24 and FT headline review|TESTED-OFFLINE|[filter_report_v2.md](filter_report_v2.md) covers all 79 returned probe headlines with v1 comparison; golden policy checks use labeled probe samples|
|Per-content-type story recency|TESTED-OFFLINE|Collection and eligibility reject out-of-window candidates; old probe timestamps give Ethereum 0/642 and Apple SEC 1/1001 within the configured 168-hour window|
|BLS pointer classification|TESTED-OFFLINE|Pointer content is excluded from stories, macro coverage and critical scope; BLS is non-critical|
|Empty irregular feed history|TESTED-OFFLINE|`last_nonempty_at` is stored; initial empty arXiv is `UNVERIFIED_EMPTY`; only a previously non-empty source can be checked quiet|
|NBER, DN and Finansavisen policy|TESTED-OFFLINE|`back.nber.org` is an inactive candidate requiring human approval; DN and Finansavisen are skipped as paywalled; no auth hostname is allowlisted|
|Routine Fed and BoE notices|TESTED-OFFLINE|Configured significance 0 and excluded from Top 5; eligible items remain in the full edition|
|CNBC/E24 title filter review|TESTED-OFFLINE|[filter_report.md](filter_report.md) lists all 69 kept/dropped headlines and matching current rule; matcher unchanged|
|EIA dates|TESTED-OFFLINE|Yearless dates reject; EIA stays disabled. Old probe cannot prove whether every feed item lacks a year because bodies were not retained|
|Contact User-Agent, 403 robots retry, gzip cap after decompression, redirect-domain recording|TESTED-OFFLINE|Mock transport tests; BLS/IMF/SEC press remain failed unless a future lawful probe succeeds|
|Returned 2026-10-13 probe observations|LIVE-VERIFIED|Nine HTTP 200 parsed/healthy endpoints under old policy; SSB was RSS, arXiv zero-item, EIA date yearless, three robots 403, NBER/Finansavisen cross-domain redirects|
|NBER redirect target|LIVE-VERIFIED (user-reported)|`back.nber.org` is stored as an inactive candidate only; no allowlist expansion is active|
|Finansavisen authentication/paywall hostname|NOT BUILT|Exact hostname remains unknown and is not needed because requests are disabled by policy|
|Post-fix source health, live edition, five-original audit, visual browser/mobile checks|NOT BUILT|No post-fix network or browser run; all enable flags remain false|

The technically healthy old endpoints do **not** prove current full-scope coverage. The SEC feed covers one company, E24 content was not audited for substantive reuse, and all categories remain NOT_CHECKED in the product. The next connected probe must be generated with the revised standalone script and run with `python3 scripts/live_probe.py --ask-contact`; return `live_probe_results.json`. The old result is incompatible with the revised fingerprint and cannot be used for activation. No repository, push or deployment occurred.

Final offline checks are recorded in CHECKPOINT.md after this continuation. The frontend, standalone probe and all source flags remain TESTED-OFFLINE; all 29 `enabled` flags remain false. No fixture file was changed. Browser/mobile visual checks remain NOT BUILT.

---

# THE LEDGER — earlier offline baseline (historical)

**Decision: not ready to approve GitHub deployment.** The independent project is built locally and tested offline. The execution environment could not resolve any of 29 candidate source hosts. No live source was activated, no genuine live newspaper was published locally, and no GitHub repository, push, Pages setting or external publication was performed.

The default generated site truthfully shows PARTIAL / STALE / NOT DEPLOYABLE with zero stories. `build/fixture/site` is a separate labeled FIXTURE demonstration with six stories and five featured items. It is never deployable. “Complete” in the gate checklist means completion of the expressly permitted offline path; it does not mean an operating service.

## Latest continuation — blocked-network handoff

**TESTED-OFFLINE:** standalone production-rule probe and guarded results importer
implemented; 113 Python tests pass, including 23 new probe/import tests. The single
file runs outside the checkout with Python's isolated mode and no installed packages.

**NOT BUILT:** live five-story collection/audit and browser/mobile verification
remain pending. The three required DNS lookups and one HTTPS fetch failed again;
`evidence/network-recheck.json` records the exact results. No prolonged network
diagnosis followed. No new LIVE-VERIFIED service claim is made.

Run `python3 scripts/live_probe.py --ask-contact` on a connected computer;
return **live_probe_results.json**. [LIVE_VERIFICATION.md](LIVE_VERIFICATION.md)
documents its separate draft report, dry-run/application commands, review guards
and remaining steps. The default source enable flags, editions and site design
remain unchanged. The SEC allowlist now includes the document host already used
by its adapter. No repository, push or deployment occurred.

## Feature status

Every status below uses the required vocabulary. A feature with fixture tests is TESTED-OFFLINE even when its implementation is complete.

|Feature|Status|Evidence and limit|
|---|---|---|
|Environment isolation and reproducible local build|TESTED-OFFLINE|New the-ledger directory; original projects untouched; no local Git repository created|
|Live feed/API collection|NOT BUILT|Operational service unverified; 29 direct attempts fail DNS; adapters exist but all live registry entries disabled|
|Source availability probe utility|TESTED-OFFLINE|evidence/source-probes.json records actual DNS failures, not success|
|Current GitHub documentation lookup|LIVE-VERIFIED|Official documents retrieved with research-browser tool; links in SOURCES_REPORT.md|
|Reusable-source/legal approval|NOT BUILT|No source's reuse/robots terms established in collector environment; disabled until review|
|Curated candidate registry and automatic scope decision|TESTED-OFFLINE|29 candidates; scope.py and config/gonogo.json; full/narrow/offline cases tested|
|RSS/Atom parsing|TESTED-OFFLINE|Publication versus update timestamps, canaries, entity rejection, text normalization tests|
|Official JSON and SEC submissions parsers|TESTED-OFFLINE|Explicit JSON schema and columnar SEC fixtures; actual endpoints not parsed live|
|HTML article scraping|NOT BUILT|Excluded; HTML candidates are discovery pages only|
|Security controls and sanitized conditional cache|TESTED-OFFLINE|Allowlist, private-IP/mixed-DNS, robots, redirect, cap, SEC contact, 304/frozen-data tests; real TLS/network behavior unverified|
|UTC metadata and Oslo display/date/DST|TESTED-OFFLINE|Separate timestamp fields and day precision; winter, summer and both 2026 DST transitions tested|
|Identifiers and asset-specific eligibility|TESTED-OFFLINE|No inferred ticker identifiers; strict fund/crypto/commodity/derivative guards; most generic items in these categories will be rejected until metadata is supplied|
|Publisher tiers, types, eligibility and attribution|TESTED-OFFLINE|Promotion/opinion/T/X exclusions and single-secondary attribution tested|
|Deterministic dedupe and event clustering|TESTED-OFFLINE|Five syndicated copies → one, earliest eligible item, separate company events; evidence/fixture-examples.json|
|Structured dispute handling|TESTED-OFFLINE|Comparable claims retain both values; dates/units/definitions/datasets compared; excluded from news|
|Automatic free-text contradiction/syndication detection|NOT BUILT|Conservative exact identities or reviewed structured keys only|
|Deterministic ranking, diversity, explanations and overrides|TESTED-OFFLINE|90-test suite includes score rules, corporate surprise priority, promotion/crypto rejection and logged overrides|
|Ten real historical-event ranking replays|TESTED-OFFLINE|Official historical references found via browser; scoring/time inputs explicitly FIXTURE; not a live collector run or validated editorial model|
|Source health, quarantine and four coverage states|TESTED-OFFLINE|All requested state branches, irregular feeds, frozen 200 and cached 304 tested|
|Publication rule and first-run refusal|TESTED-OFFLINE|FULL, permitted PARTIAL, keep-last-valid and blocked first run tested|
|Immutable archives, hashes, local idempotency|TESTED-OFFLINE|Archive mutation rejected; repeated runs preserve same edition|
|Timestamped manual correction overlay|TESTED-OFFLINE|Implementation and overlay validation; original JSON never rewritten|
|Top 5 and full edition/category filters|TESTED-OFFLINE|JSON-driven six-field stories and per-filter coverage; no hardcoded frontend stories|
|Attributed official explanation|TESTED-OFFLINE|Reviewed FIXTURE central-bank quote traced to <=25-word excerpt; missing rationale gives unavailable fallback|
|Automatic official-rationale extraction|NOT BUILT|Generic real adapters default to unavailable; no invented rationale|
|Reviewed generic explanation mechanism|TESTED-OFFLINE|Only human-reviewed glossary entries may supply context; none reviewed yet|
|30 beginner glossary drafts and daily mapping|TESTED-OFFLINE|All say needs human review; links are proposed and unverified|
|Weekly research shelf selection|TESTED-OFFLINE|One original synthetic paper/abstract with older date and working-paper label; no approved live papers|
|Copy Story Pack, read/saved state|TESTED-OFFLINE|Browser-local text only; no outbound copy call; no private state included; localStorage failures tested|
|Light/dark responsive newspaper UI|TESTED-OFFLINE|Requested palettes and offline fonts; Node DOM behavior assertions|
|Real browser/mobile visual testing|NOT BUILT|No installed headless browser found; layout/clipboard permissions not visually verified|
|Local HTTP serving smoke test|NOT BUILT|Environment denied the listening socket with Operation not permitted; evidence/local-http.json|
|Daily/verify Actions workflows|TESTED-OFFLINE|Prepared YAML; gate tested at every required trigger/date; never executed on GitHub|
|GitHub Pages deployment|NOT BUILT|Intentionally not performed; user-only instructions in DEPLOYMENT.md|
|Live original-source five-story audit|NOT BUILT|evidence/LIVE_AUDIT.md is an explicitly pending worksheet|
|Five-minute / five-days-a-week habit outcome|NOT BUILT|Reading-time estimate implemented; actual beginner usability and retention not evaluated|
|AI, recommendations, signals, charts, market data and personalization|NOT BUILT|Intentionally excluded from MVP|

## Actual source and coverage results

**Verified working primary sources: none. Verified working news sources: none.** Exactly which candidates were attempted, their endpoint, expected format/cadence, latency and reuse status are in SOURCES_REPORT.md and evidence/source-probes.json. Zero HTTP responses were received; statuses are unknown, not fabricated HTTP codes. Historical official pages and GitHub docs located through the research browser are not counted as working adapters.

|Category|Working primary|Working news|Real-mode local coverage state|
|---|---:|---:|---|
|Equities|0|0|NOT_CHECKED|
|Funds / ETFs|0|0|NOT_CHECKED|
|Crypto|0|0|NOT_CHECKED|
|Macro|0|0|NOT_CHECKED|
|Bonds / rates|0|0|NOT_CHECKED|
|FX|0|0|NOT_CHECKED|
|Commodities / energy|0|0|NOT_CHECKED|
|Derivatives / options|0|0|NOT_CHECKED|

The real-mode run is a blocked local run with disabled sources, **not a genuine network collection**. It correctly retains no deployable edition. The policy threshold counts are 0/3 macro primary, 0/1 Nordic, 0/2 substantive equity, 0/5 overall; the result is OFFLINE_FIXTURE_BUILD.

Norway does **not** yet have verified meaningful coverage. Norges Bank, SSB, NewsWeb/Euronext, Finanstilsynet and the Norwegian news candidates could not be retrieved directly. Substantive content was not established; routine administrative notices would not suffice. No other Nordic country has a verified adapter. The source report describes expansion prerequisites and thin free coverage rather than equating those gaps with no news.

## How editorial decisions work

Ranking uses the requested five weights unchanged, event baselines with bounded documented modifiers, per-type freshness, full-archive novelty and a diversity pass. Every selected story stores all components and a visible reason. Overrides require an explicit editor/reason/time/expiry log. Initial weights and educational/breadth rubrics remain subjective and unvalidated. Source tier affects eligibility and labels, not score. No user behavior changes ranking.

Dedupe uses canonical URLs, publisher-scoped document IDs, exact dated-title fingerprints and optionally reviewed event keys. It preserves sources and structured disagreements. Known syndicated origin IDs count once; general semantic matching is deliberately absent. Metadata alone will miss some paraphrased duplicates, unexpected event types, revised data and material updates. Those limits are preferable to confident misassociation but require editorial maintenance.

The real historical regression set comprises five Fed decisions (2020-03-15, 2022-03-16, 2022-06-15, 2024-07-31, 2024-09-18), Apple's 2019-01-02 outlook letter, three 2023 bank closures (SVB, Signature, First Republic) and ECB's 2024-07-18 decision. Exact official links and FIXTURE scores appear in evidence/fixture-examples.json. The corporate-priority comparison uses explicit hypothetical surprise inputs; it does not claim to reconstruct market expectations. No natural live cluster, promotion rejection or conflict was observed; all supplied examples are labeled FIXTURE.

## Largest ways the reader could be misled

1. **Coverage mistaken for comprehensiveness.** A successful narrow feed or a single issuer's SEC submissions is not coverage of an entire market. Visible category states and strict critical-source configuration reduce this risk; a professional review must set actual market scope before launch.
2. **Issuer claims mistaken for independent fact.** P describes the publisher, not guaranteed truth. Confirmed fields state that a document was published; explanation is attributed or unavailable. Generic title-based descriptions lose context, so originals remain central.
3. **Editorial proxies mistaken for financial significance.** Broad source category tags, event baselines and glossary mappings can over-prioritize familiar macro material. No score predicts returns. Calibrate with a larger, diverse historical set and test comprehension with the intended reader.

## Largest operational failure modes

1. **Endpoint, terms or format changes.** Robots, missing dates/canaries, empty/frozen feeds and ambiguous instruments fail closed. False quarantine can also occur; reviewed baselines and source-specific parsers need maintenance.
2. **Schedule, permissions or deployment failure.** Best-effort cron, inactivity disablement, branch policy and expired artifacts can interrupt publication. Immutable archives and the 36-hour browser age warning protect against silent apparent freshness; monitoring remains necessary.
3. **Configuration/review drift.** Overbroad category mapping, outdated reuse approval, unreviewed glossary text or stale research can make an apparently healthy newspaper weak. Review monthly, record changes and rerun the affected tests and live audit.

Unconfirmed assumptions: feed URLs and cadence, permitted metadata reuse, actual source richness, account billing/permissions, phone layout and reader comprehension. All candidate thresholds are provisional. The JSON API adapter is a fixed schema that must be mapped to a specific approved provider before use. Source health cannot automatically judge economic importance or know that a feed is omitting a crucial story.

A professional financial journalist would review source balance, add permitted independent reporting, inspect original documents and contradictions, calibrate significance, and write/review concise source-grounded explanations. An experienced long-term investor would ask for clearer business/accounting mechanisms, economic context, uncertainty and fees/risk definitions, and resist confusing daily attention with durable importance. Neither change calls for a recommendation engine.

## $0 hosting and limitations

Current official documentation was LIVE-VERIFIED through the research browser: standard public-repository/Pages runners free; GitHub Free private allowance 2,000 minutes/month, 500 MB shared artifact storage, 10 GB cache/repository. Larger runners charge. Pages Free requires public repositories; paid plans are needed for private-repository Pages. Published site <=1 GB, repository recommended <=1 GB, soft bandwidth 100 GB/month, deployment timeout 10 minutes, soft 10 builds/hour with custom Actions exception. Public schedules disable after 60 inactive days and may be delayed/dropped.

Account setup was not inspected. Paid plans, larger runners, private usage beyond allowances, shared artifact/storage overages, custom domains and other services can create cost. This project uses standard Ubuntu, no package installation, no Actions cache and <=10 MB / one-day artifacts; no billing was activated. Inspect account budgets/payment/storage before publishing. See the exact [official references and caveats in SOURCES_REPORT.md](SOURCES_REPORT.md) and numbered [DEPLOYMENT.md](DEPLOYMENT.md) steps.

## Manual steps, in order

1. On a connected machine rerun probes; verify official endpoints, robots, reuse terms and substantive content. Enable only defensible sources with reviewed category/health metadata and a genuine SEC contact if used.
2. Collect a real local edition, inspect source/coverage health, and finish the five-original audit. Narrow scope honestly when necessary; do not relabel missing categories as quiet.
3. Review every glossary entry below, its link and mechanism wording; add approved live research. Record reviewers/dates. Test the phone reading experience and real browser controls.
4. Confirm a GitHub Free account, public-repository choice, account-wide storage and $0 billing settings. Create a new PUBLIC the-ledger repository yourself.
5. Generate and validate a deployable real edition in the independent project; inspect files, initialize local Git, commit and push using DEPLOYMENT.md commands.
6. Enable Pages with GitHub Actions, configure required permissions/SEC secret, then explicitly set LEDGER_DEPLOY_APPROVED=true only after your deployment approval.
7. Run Verify and Daily edition; inspect the deployed URL and actual timestamps, source links, warnings and archive. Monitor failures and monthly source/account health; re-enable schedules after prolonged inactivity.

## Glossary: all 30 entries need human review

No entry is approved. Proposed explainer URLs were not live-verified; verify the exact page as well as content. These drafts are displayed with their review warning and do not supply story explanations until explicitly reviewed.

1. **Policy rate** (`policy-rate`) — needs human review. [Proposed explainer](https://www.ecb.europa.eu/ecb-and-you/explainers/tell-me/html/key_interest_rates.en.html).
2. **Inflation** (`inflation`) — needs human review. [Proposed explainer](https://www.ecb.europa.eu/ecb-and-you/explainers/tell-me-more/html/what_is_inflation.en.html).
3. **Real interest rate** (`real-rates`) — needs human review. [Proposed explainer](https://www.ecb.europa.eu/ecb-and-you/explainers/tell-me/html/nominal_and_real_interest_rates.en.html).
4. **Company earnings** (`earnings`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks).
5. **Company guidance** (`guidance`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/how-read-investments).
6. **Liquidity** (`liquidity`) — needs human review. [Proposed explainer](https://www.bankofengland.co.uk/explainers/what-is-financial-stability).
7. **Bond** (`bond`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/investment-products/bonds-or-fixed-income-products/bonds).
8. **Bond yield** (`yield`) — needs human review. [Proposed explainer](https://www.finra.org/investors/investing/investment-products/bonds).
9. **Duration** (`duration`) — needs human review. [Proposed explainer](https://www.finra.org/investors/insights/duration-what-interest-rate-hike-could-do-your-bond-portfolio).
10. **Credit risk** (`credit-risk`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/investment-products/bonds-or-fixed-income-products/bonds).
11. **Exchange rate** (`fx`) — needs human review. [Proposed explainer](https://www.rba.gov.au/education/resources/explainers/exchange-rates-and-their-measurement.html).
12. **Gross domestic product** (`gdp`) — needs human review. [Proposed explainer](https://www.bea.gov/resources/learning-center/what-to-know-gdp).
13. **Unemployment rate** (`unemployment`) — needs human review. [Proposed explainer](https://www.bls.gov/cps/cps_htgm.htm).
14. **Data revisions** (`revision`) — needs human review. [Proposed explainer](https://www.bea.gov/resources/learning-center/what-to-know-gdp).
15. **Base effects** (`base-effects`) — needs human review. [Proposed explainer](https://www.ecb.europa.eu/ecb-and-you/explainers/tell-me-more/html/what_is_inflation.en.html).
16. **Exchange-traded fund** (`etf`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/investment-products/exchange-traded-funds-etfs).
17. **Fund share class** (`share-class`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/investment-products/mutual-funds).
18. **Fund expenses** (`expense-ratio`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/investment-products/mutual-funds).
19. **Tracking difference** (`tracking`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/investment-products/index-funds).
20. **Diversification** (`diversification`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/glossary/diversification).
21. **Market capitalization** (`market-cap`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks).
22. **Cash flow** (`cash-flow`) — needs human review. [Proposed explainer](https://www.sec.gov/about/reports-publications/investorpubsbegfinstmtguide).
23. **Share dilution** (`dilution`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks).
24. **Futures contract** (`futures`) — needs human review. [Proposed explainer](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/FuturesMarketBasics/index.htm).
25. **Options** (`options`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/investment-products/options).
26. **Leverage** (`leverage`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/investment-products/margin).
27. **Energy inventories** (`inventory`) — needs human review. [Proposed explainer](https://www.eia.gov/petroleum/supply/weekly/).
28. **Blockchain records** (`blockchain`) — needs human review. [Proposed explainer](https://www.nist.gov/blockchain).
29. **Asset custody** (`custody`) — needs human review. [Proposed explainer](https://www.investor.gov/introduction-investing/investing-basics/investment-products/crypto-assets).
30. **Working papers** (`working-paper`) — needs human review. [Proposed explainer](https://www.bis.org/list/workpap/index.htm).

## Evidence and final decision

- `evidence/python-tests.txt`: Python suite output (90 passing at the report checkpoint).
- `evidence/frontend-tests.txt`: nine passing Node behavior/DOM tests; these are not mobile layout proof.
- `evidence/source-probes.json`: 29 real attempted direct source connections, all DNS failures.
- `evidence/fixture-examples.json`: labeled synthetic cluster, rejection, dispute, historical replay and DST schedule evidence.
- `data/run.json`: nondeployable real-mode local build and all NOT_CHECKED states.
- `build/fixture/site`: nondeployable synthetic newspaper preview.
- `evidence/LIVE_AUDIT.md`: pending genuine source audit.
- `evidence/local-http.json`: local preview serving attempt blocked by this environment; no served-page claim.

The project is ready for **local review and live verification work**. It is **not ready for approval to deploy as a live newspaper**. Fixture correctness, YAML parsing and this implementation do not establish reliable sources, legal reuse, financial editorial quality or a working live service.
