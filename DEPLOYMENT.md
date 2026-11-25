# Deployment preparation — no external deployment performed

**Current decision: NOT ready for deployment approval.** The code is TESTED-OFFLINE; source collection, reuse rights, meaningful Norwegian coverage, a live five-story audit, and browser layout remain unverified. Follow steps in order. Do not enable publication merely because tests pass.

## 1. Complete the local source gate first

On a machine with working internet, enter the project directory and run:

```sh
python3 scripts/live_probe.py --ask-contact
```

Inspect `live_probe_results.json` and `live_probe_draft/SOURCES_REPORT.md`. A successful diagnostic is only endpoint evidence. Find the actual feed/API using the publisher's official documentation. Verify robots.txt, terms, content structure and reuse of headline/link/excerpt; record the exact official terms link and rationale. Do not enable a source with unresolved reuse terms. Leave excerpt_words at 0 unless permission supports an excerpt. Do not scrape paywalls or treat HTML discovery pages as implemented adapters. For secondary sources, verify an accountable corrections policy.

Edit `config/sources.json` only for verified sources: `url`, `adapter`, `allowed_domains` (including canonical document hosts such as www.sec.gov when using data.sec.gov), `terms_url`, `license_note`, `terms_approved`, `last_reviewed`, `enabled`, exact category scope, cadence and empirically reviewed count/freshness thresholds. Set `substance_verified: true` only after inspecting substantive documents. Document Norwegian coverage separately. The one-company SEC endpoint is insufficient by itself for broad equity coverage. Keep unused categories visibly NOT_CHECKED. No paid key or subscription is needed or allowed.

For all live collection requests, set `LEDGER_CONTACT_EMAIL` to a real contact email. THE LEDGER uses it in one descriptive User-Agent for every source, including SEC. In GitHub later, store it as a repository Actions secret of that name; never in frontend files or Git. Review whether you want a dedicated public contact address before doing so.

## 2. Verify a genuine local edition

```sh
python3 -m unittest discover -s tests -v
node --test tests/frontend.test.cjs
python3 -m collector.collect --output build/live
python3 scripts/validate.py --root build/live
python3 -m http.server 8000 --bind 127.0.0.1 --directory build/live/site
```

Inspect `build/live/data/run.json`, `health.json`, `candidate.json`, the research queue and visible coverage. Fill `evidence/LIVE_AUDIT.md` against five original documents if five qualify; never manufacture five. When fewer qualify, record the count and finish the five-document audit across subsequent editions before approving launch. Record natural clustering/rejection/conflict examples if found; otherwise retain labeled fixtures.

Use a real browser at 320px, 375px, 768px and desktop: inspect overflow, text size, theme, filters, archive, keyboard navigation, stale/partial banners, clipboard fallback and blocked localStorage. Time the Top 5 reading experience on a phone. Review all 30 glossary entries listed in FINAL_REPORT.md and their actual explainer URLs; record `reviewed_by`, `reviewed_at`, `link_verified: true` and `review_status: reviewed` only after review. Approve real research titles/abstract-derived descriptions and reuse rights before adding live shelf records. Do not change fixture records to pretend they are real.

## 3. Check your GitHub account and $0 constraints

Use GitHub Free with a **PUBLIC** repository and standard `ubuntu-latest` runners. Read the current official [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions) and [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) pages again before deployment.

Verified documentation at build time: standard public-repository and Pages runner usage is free. Free includes 2,000 monthly private-repository minutes, 500 MB artifact storage shared with Packages, and 10 GB cache per repository. Larger runners always charge. This workflow uses no Actions cache, limits the site to 10 MB and retains Pages artifacts for one day. Shared account storage from other projects is unknown: inspect your account's Billing & licensing → Usage and Budgets and alerts. Keep paid services disabled and configure usage stopping at your chosen $0 budget where supported. Without a valid payment method, over-quota usage is blocked. Adding billing, increasing cache limits, using larger runners, excess shared artifact storage, private runner usage, paid plans, custom domains or third-party services can incur costs. The workflow cannot certify your account's overall bill.

Free Pages requires a public repository. Private repository Pages needs an eligible paid plan; do not choose that path for this $0 MVP. The published site and source history will be public even though intended for one reader. Local read/saved state is never uploaded. No private account details or secrets belong in the repository.

## 4. Create the PUBLIC repository yourself

After source/legal/browser review and your deployment approval, use GitHub → New repository → name `the-ledger` → **Public**. Leave initial README/license/gitignore options empty because these files already exist locally. No repository has been created by this build.

## 5. Prepare and push this independent directory

Use this directory, not The Edge or any parent repository. Replace YOUR_USERNAME below with your account. Review staged files before committing; no fixture build or cache should be staged.

```sh
cd /home/erdi/Stock_News/the-ledger
python3 -m collector.collect --output .
python3 scripts/validate.py --root . --deploy
git init -b main
git add .
git diff --cached --stat
git diff --cached --check
git commit -m 'Add THE LEDGER static newspaper'
git remote add origin https://github.com/YOUR_USERNAME/the-ledger.git
git push -u origin main
```

If `--deploy` fails, stop before GitHub publication and resolve the missing coverage; do not bypass the guard. The fixture demo remains under ignored `build/`. Do not force-push over unrelated work. This preparation contains no Git repository and has performed no push.

## 6. Configure Actions and Pages

In repository Settings → Actions → General, allow the official actions used by these workflows. The daily job requests `contents: write` to commit immutable editions; branch protection or organization policies may prevent that. Configure the permitted workflow identity appropriately; do not broadly disable protections to mask an error.

In Settings → Pages → Build and deployment → Source, choose **GitHub Actions**. In Settings → Secrets and variables → Actions, add any SEC User-Agent secret needed. Only after your deployment approval, add repository variable **LEDGER_DEPLOY_APPROVED = true**. Until then, daily collection/deployment jobs are skipped. No other credential is required; Actions provides its scoped token.

## 7. Run the workflows

Run **Verify** manually and inspect the tests. Run **Daily edition** manually after 06:30 Europe/Oslo. The timezone gate also applies to manual runs. Before that time it logs a clean skip. If today's valid edition already exists, collection skips and the existing validated site may still be packaged for a deployment retry. The expected Pages URL is `https://YOUR_USERNAME.github.io/the-ledger/`; verify the actual URL shown by GitHub.

The update job validates the edition, commits the edition/status files, and packages `site/` only when a deployable real latest edition exists. A blocked later collection retains that edition and may deploy its updated STALE status. The deploy job uses only `pages: write` and `id-token: write`. A failed deployment does not replace the currently served site.

## 8. Monitor and troubleshoot

1. Check the edition timestamp and Coverage today first. A cron entry is not evidence of freshness. Schedules at 04:00/05:00/06:00/08:00/10:00 UTC can be delayed or dropped. The first passing attempt is 06:00 UTC in winter, 05:00 UTC in summer.
2. Inspect Actions job logs and retained `data/run.json` / `data/health.json` for failed sources. Unknown, frozen, empty or changed feeds must not be recorded as quiet news. Fix the adapter/policy and use the next scheduled attempt or manual dispatch.
3. If no real source qualifies, expect PARTIAL + STALE and no deployable first edition. Verify permissions and endpoint structure; do not lower health thresholds merely to turn a warning off.
4. If an edition is valid but not deployed, inspect Pages permissions/environment and artifact retention; rerun Daily edition to package the existing archive again.
5. GitHub disables public scheduled workflows after 60 days without repository activity. Re-enable in Actions after prolonged inactivity; normal daily archive commits provide activity. No artificial keepalive is added. See [schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
6. Review source terms, health thresholds and adapters monthly; review account usage and 10 MB site budget as the archive grows. Pages permits a 1 GB published site, recommends a <=1 GB source repo, has a soft 100 GB/month bandwidth limit and a 10-minute deployment timeout. The soft 10 builds/hour limit excludes custom Actions publishing workflows.
7. A build/platform outage cannot always write an immediate remote failure banner. The browser independently marks an edition STALE after 36 hours and rechecks its age while open. Monitor Actions failure notifications as well.

No live data audit, account configuration, repository creation, workflow execution or Pages publication was performed here.
