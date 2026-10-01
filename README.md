# AI Supply Chain Map

Two linked, interactive pages about the AI build-out, with live share prices:

- **AI Supply Chain Atlas** (`site/index.html`): every link from a quartz mine to a frontier model. 64 links in 11 stages, the companies at each one and their market shares, 91 mapped plants, mines and campuses, 31 chokepoints, ten failure scenarios run through a stress model, and a 92-company watchlist with prices, analyst targets and the projections to follow.
- **AI Investment Atlas** (`site/investment-atlas/index.html`): 85 AI investments announced since 2024 on a world map, the capex of the seven biggest builders, the compute two labs have signed for, and a payback test of what revenue all of it has to earn by 2030.

Once GitHub Pages is on, the site lives at **https://parthp6174.github.io/AI_Supply-Chain_Map/** (the Investment Atlas at `/investment-atlas/`).

## Turn on the live site (one time)

1. **Settings → Pages → Build and deployment → Source: GitHub Actions.** GitHub Pages is free for public repositories.
2. **Actions tab → "Refresh prices and publish site" → Run workflow** to publish right away. After that it runs by itself.

## How it stays current

| What | How often | How |
|---|---|---|
| Share prices | Every 15 minutes, Monday to Friday | `.github/workflows/pages.yml` runs `scripts/fetch_quotes.py` (Yahoo Finance via `yfinance`) and redeploys. Open pages re-check every 5 minutes. |
| Analyst targets, ratings, next report dates | Once a day | Same job; the script refreshes them when they are more than 20 hours old. |
| News and new developments | Weekly, or whenever you add one | One entry in `data/developments.json`. An entry is dated and sourced, links to the boxes, sites, scenarios, companies and Investment Atlas projects it touches, and can change ratings and statuses. Pushing the file rebuilds the site. |
| Capex, revenue and backlog | After each earnings season | Edit `src/atlas/data_items.py` (builders, labs, deals) and push. |

To suggest a development without editing files, open an issue with the **New development** form. The full procedure, including every kind of change an entry can make, is in [docs/UPDATING.md](docs/UPDATING.md).

If Yahoo Finance is down or rate-limits a run, the pages keep the last good prices, or the 30 Sep 2026 research snapshot, and say which they are showing.

## Repository layout

```
data/developments.json       dated log of developments; the main thing to edit
src/supply/supply_data.py    the chain: links, companies, shares, chokepoints, sites, scenarios, snapshot quotes
src/supply/supply_model.py   stress model and diagram layout
src/atlas/data_items.py      investments, builders, labs, deals
src/atlas/model.py           payback model (Python mirror of the page's logic)
src/*/template.html          page templates
src/common/                  map projection and precomputed country outlines
src/build.py                 builds both pages
scripts/fetch_quotes.py      price and analyst-target refresh
site/                        built pages (what GitHub Pages serves)
```

## Build locally

```bash
pip install -r requirements.txt
python scripts/fetch_quotes.py          # optional: live prices into site/data/quotes.json
python src/build.py                     # writes site/index.html and site/investment-atlas/index.html
python -m http.server -d site 8000      # then open http://localhost:8000
```

`python src/build.py --target artifact` writes the versions published on claude.ai to `dist/artifact/`.

## Sources and caveats

Every figure links to its source on the page. Market shares come from different years and definitions; the stress model shows the share of planned supply still delivered under each shock, not a forecast; analyst targets are consensus averages. This is a research tool, not investment advice.
