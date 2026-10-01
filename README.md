# AI Supply Chain Map

Two linked, interactive pages about the AI build-out, with live share prices:

- **AI Supply Chain Atlas** (`site/index.html`): every link from a quartz mine to a frontier model. 64 links in 11 stages, the companies at each one and their market shares, 91 mapped plants, mines and campuses, 31 chokepoints, ten failure scenarios run through a stress model, and a 92-company watchlist with prices, analyst targets and the projections to follow.
- **AI Investment Atlas** (`site/investment-atlas/index.html`): 85 AI investments announced since 2024 on a world map, the capex of the seven biggest builders, the compute two labs have signed for, and a payback test of what revenue all of it has to earn by 2030.

The site lives at **https://parthp6174.github.io/AI_Supply-Chain_Map/** (the Investment Atlas at `/investment-atlas/`).

## Run it from the site: the Update desk

The Supply Chain Atlas has an **Update desk** section (linked from the navigation on both pages). Everyone sees when prices and headlines were last refreshed, the news radar, and a form that opens a suggestion on GitHub. After the owner connects GitHub once, the desk can also:

- **Refresh now**: fetch the latest prices and headlines and republish both pages (about two minutes, with live progress).
- **News radar**: stories from the last 10 days on every chokepoint, scenario and money topic, collected from Google News every 3 hours, with repeat coverage grouped and stock-pick noise filtered out. **Add to log** turns a headline into a draft entry with its source and links filled in; **Hide** clears one you don't need.
- **Publish, edit or delete developments**, including changes to the pages: re-rate a chokepoint, change a site's status, move a scenario, update a projection or an Investment Atlas project, or add a new site or project. Publishing rebuilds both pages in about two minutes.
- **Turn on automatic updates**, and switch them back on if GitHub pauses them (see below).
- Show anything the last build had to leave out, so a mistake in an entry never takes the site down.

### Connect GitHub (one time per browser)

1. Create a fine-grained key at **GitHub → Settings → Developer settings → Fine-grained tokens** ([direct link](https://github.com/settings/personal-access-tokens/new)). Pick an expiry, for example 90 days.
2. **Repository access:** Only select repositories → `AI_Supply-Chain_Map`.
3. **Permissions:** Contents, Actions and Workflows, each **Read and write**.
4. Generate it, then paste it into **Site owner: connect GitHub** at the bottom of the Update desk.

The key is kept only in that browser (or only for the session if you untick "Remember on this device") and is only sent to `api.github.com`. Commits made from the desk are made by your account.

### Turn on automatic updates (one time)

GitHub runs a schedule under the account that last changed it. The schedule in this repository was written by a Claude account that can't run it, so the desk shows **Turn on automatic updates** until it runs: one click commits a one-minute shift of the schedule from your account. If you'd rather do it by hand, edit `.github/workflows/pages.yml` on GitHub and change each minute in the two `cron` lines by one (for example `7,22,37,52` to `8,23,38,53`).

## How it stays current

| What | How often | How |
|---|---|---|
| Share prices | Every 15 minutes, Monday to Friday, and on demand | `.github/workflows/pages.yml` runs `scripts/fetch_quotes.py` (Yahoo Finance via `yfinance`) and redeploys. Open pages re-check every 5 minutes. |
| Analyst targets, ratings, next report dates | Once a day | Same job; the script refreshes them when they are more than 20 hours old. |
| Headlines for the news radar | Every 3 hours, and on demand | `scripts/fetch_news.py` runs the Google News searches in `data/news_queries.json`. Headlines are only shown on the desk; nothing reaches the pages until someone adds it. |
| Developments | Whenever you add one | From the Update desk, or one entry in `data/developments.json` pushed to `main`. An entry is dated and sourced, links to the boxes, sites, scenarios, companies and Investment Atlas projects it touches, and can change ratings and statuses. |
| Capex, revenue and backlog | After each earnings season | Edit `src/atlas/data_items.py` (builders, labs, deals) and push. |

Visitors can suggest a development from the desk or with the **New development** issue form. The full procedure, including every kind of change an entry can make, is in [docs/UPDATING.md](docs/UPDATING.md).

If Yahoo Finance or Google News is down or rate-limits a run, the pages keep the last good prices and headlines, or the 30 Sep 2026 research snapshot, and say which they are showing.

## Repository layout

```
data/developments.json       dated log of developments (the desk edits this file)
data/news_queries.json       news radar topics and searches
src/supply/supply_data.py    the chain: links, companies, shares, chokepoints, sites, scenarios, snapshot quotes
src/supply/supply_model.py   stress model and diagram layout
src/atlas/data_items.py      investments, builders, labs, deals
src/atlas/model.py           payback model (Python mirror of the page's logic)
src/*/template.html          page templates
src/common/desk.js           the Update desk (GitHub Pages only)
src/common/                  map projection and precomputed country outlines
src/build.py                 builds both pages
scripts/fetch_quotes.py      price and analyst-target refresh
scripts/fetch_news.py        news radar refresh
site/                        built pages (what GitHub Pages serves)
```

## Build locally

```bash
pip install -r requirements.txt
python scripts/fetch_quotes.py          # optional: live prices into site/data/quotes.json
python scripts/fetch_news.py --mode always   # optional: headlines into site/data/news.json
python src/build.py                     # writes site/index.html and site/investment-atlas/index.html
python -m http.server -d site 8000      # then open http://localhost:8000
```

`python src/build.py` stops with a list of problems if a development links to something that doesn't exist; the workflow builds with `--lenient`, which leaves out only the broken part and lists it on the Update desk. `python src/build.py --target artifact` writes the versions published on claude.ai to `dist/artifact/`.

## Sources and caveats

Every figure links to its source on the page. Market shares come from different years and definitions; the stress model shows the share of planned supply still delivered under each shock, not a forecast; analyst targets are consensus averages. This is a research tool, not investment advice.
