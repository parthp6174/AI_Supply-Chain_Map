# AI Supply Chain Map

Three linked, interactive pages about the AI build-out, with live share prices:

- **The Chain** (`site/index.html`): every link from a quartz mine to a frontier model. 64 links in 11 stages, the companies at each one and their market shares, 91 mapped plants, mines and campuses, 31 chokepoints, ten failure scenarios run through a stress model, and a 92-company watchlist with prices, analyst targets and the projections to follow.
- **The Money** (`site/money/index.html`): 85 AI investments announced since 2024 on a world map, the capex of the seven biggest builders, the compute two labs have signed for, and a payback test of what revenue all of it has to earn by 2030.
- **The Odds** (`site/odds/index.html`): a probability lab. 27 things that could stall or speed up the 2027 build-out, each with a chance or a range you can change, and the links between them. The page runs 10,000 futures in your browser and shows how much of the plan gets built, how wide the spread is, what holds it back and what matters most. "Suppose it happens" shows how everything linked to an event shifts with it. The starting numbers are first estimates and are marked provisional.

The site lives at **https://parthp6174.github.io/AI_Supply-Chain_Map/** (The Money at `/money/`, The Odds at `/odds/`; The Money's first address, `/investment-atlas/`, redirects to it).

## Run it from the site: the Update desk

The Chain has an **Update desk** section (linked from the navigation on both pages). Everyone sees when prices and headlines were last refreshed, the news radar, and a form that opens a suggestion on GitHub. After the owner connects GitHub once, the desk can also:

- **Refresh now**: fetch the latest prices and headlines and republish both pages (about two minutes, with live progress).
- **News radar**: stories from the last 10 days on every chokepoint, scenario and money topic, collected from Google News every 3 hours, with repeat coverage grouped and stock-pick noise filtered out. **Add to log** turns a headline into a draft entry with its source and links filled in; **Hide** clears one you don't need.
- **Publish, edit or delete developments**, including changes to the pages: re-rate a chokepoint, change a site's status, move a scenario, update a projection or an project in The Money, or add a new site or project. Publishing rebuilds both pages in about two minutes.
- **Restart automatic updates** if GitHub stops running them (see below).
- Show anything the last build had to leave out, so a mistake in an entry never takes the site down.

### Connect GitHub (one time per browser)

1. Create a fine-grained key at **GitHub → Settings → Developer settings → Fine-grained tokens** ([direct link](https://github.com/settings/personal-access-tokens/new)). Pick an expiry, for example 90 days.
2. **Repository access:** Only select repositories → `AI_Supply-Chain_Map`.
3. **Permissions:** Contents, Actions and Workflows, each **Read and write**.
4. Generate it, then paste it into **Site owner: connect GitHub** at the bottom of the Update desk.

The key is kept only in that browser (or only for the session if you untick "Remember on this device") and is only sent to `api.github.com`. Commits made from the desk are made by your account.

### Automatic updates

GitHub runs the update on a schedule, but only when it has spare capacity. The schedule asks for every 15 minutes on weekdays; in the first days GitHub ran it every 4 to 9 hours (it took about a day to start). Use **Refresh now** on the desk for fresh prices at any moment. If no scheduled update has run for a day, the desk offers **Restart automatic updates**, which shifts the schedule by a minute so GitHub registers it again.

## How it stays current

| What | How often | How |
|---|---|---|
| Share prices | Every few hours (GitHub's schedule), and on demand | `.github/workflows/pages.yml` runs `scripts/fetch_quotes.py` (Yahoo Finance via `yfinance`) and redeploys. Open pages re-check every 5 minutes. |
| Analyst targets, ratings, next report dates | Once a day | Same job; the script refreshes them when they are more than 20 hours old. |
| Headlines for the news radar | Every 3 hours, and on demand | `scripts/fetch_news.py` runs the Google News searches in `data/news_queries.json`. Headlines are only shown on the desk; nothing reaches the pages until someone adds it. |
| Developments | Whenever you add one | From the Update desk, or one entry in `data/developments.json` pushed to `main`. An entry is dated and sourced, links to the boxes, sites, scenarios, companies and projects in The Money it touches, and can change ratings and statuses. |
| Capex, revenue and backlog | After each earnings season | Edit `src/atlas/data_items.py` (builders, labs, deals) and push. |

Visitors can suggest a development from the desk or with the **New development** issue form. The full procedure, including every kind of change an entry can make, is in [docs/UPDATING.md](docs/UPDATING.md).

If Yahoo Finance or Google News is down or rate-limits a run, the pages keep the last good prices and headlines, or the 30 Sep 2026 research snapshot, and say which they are showing.

## Repository layout

```
data/developments.json       dated log of developments (the desk edits this file)
data/news_queries.json       news radar topics and searches
data/odds.json               the probability lab's model: 27 uncertain drivers, what each does, starting numbers and links
src/supply/supply_data.py    the chain: links, companies, shares, chokepoints, sites, scenarios, snapshot quotes
src/supply/supply_model.py   stress model and diagram layout
src/atlas/data_items.py      investments, builders, labs, deals
src/atlas/model.py           payback model (Python mirror of the page's logic)
src/*/template.html          page templates (supply, atlas, odds)
src/common/desk.js           the Update desk (GitHub Pages only)
src/common/odds_engine.js    probability and correlation engine behind The Odds (inlined into its page)
src/common/                  map projection and precomputed country outlines
src/build.py                 builds the three pages
scripts/fetch_quotes.py      price and analyst-target refresh
scripts/fetch_news.py        news radar refresh
tests/test_desk.py           browser tests for the Update desk (fake GitHub API)
tests/test_engine.mjs        tests for the probability engine and the model file (Node, no packages)
tests/test_odds.py           browser tests for The Odds
site/                        built pages (what GitHub Pages serves)
```

## Build locally

```bash
pip install -r requirements.txt
python scripts/fetch_quotes.py          # optional: live prices into site/data/quotes.json
python scripts/fetch_news.py --mode always   # optional: headlines into site/data/news.json
python src/build.py                     # writes site/index.html, site/money/index.html and site/odds/index.html
python -m http.server -d site 8000      # then open http://localhost:8000
```

`python src/build.py` stops with a list of problems if a development links to something that doesn't exist, or if `data/odds.json` names a link, scenario or driver that doesn't exist; the workflow builds with `--lenient`, which leaves out only the broken part and lists it on the Update desk. `python src/build.py --target artifact` writes the versions published on claude.ai to `dist/artifact/` (The Chain and The Money only).

## Sources and caveats

Every figure links to its source on the page. Market shares come from different years and definitions; the stress model shows the share of planned supply still delivered under each shock, not a forecast; analyst targets are consensus averages. The Odds turns the numbers you give it into ranges of outcomes; its starting numbers are first estimates by judgement, not researched forecasts. This is a research tool, not investment advice.
