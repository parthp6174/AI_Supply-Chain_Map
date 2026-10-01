# Keeping the atlases current

There are three update paths: prices and headlines update themselves, developments are logged from the Update desk (or in one file), and the deeper numbers are refreshed each quarter.

## 1. Prices, analyst targets and headlines (automatic)

`.github/workflows/pages.yml` runs every 15 minutes on weekdays, every 6 hours at weekends, on every push to `main`, and on demand (the Update desk's **Refresh now** button or the Actions tab). Each run:

1. restores the last `site/data/quotes.json` and `site/data/news.json` from the Actions cache;
2. runs `scripts/fetch_quotes.py`, which downloads the latest price for all 92 tickers in one batch and, once a day, each company's average analyst target, rating, number of analysts and next report date;
3. runs `scripts/fetch_news.py` when the headlines are more than 3 hours old (always on **Refresh now**; on a push only when there are none yet, so published entries go live quickly);
4. rebuilds both pages with those numbers embedded (`--lenient`, see below), and deploys to GitHub Pages.

Scheduled runs are set a few minutes past the quarter-hour because GitHub delays, and sometimes drops, scheduled jobs at the start of the hour.

**Who the schedule runs as.** GitHub runs a schedule under the account that last changed one of its `cron` lines, and only if that account can run workflows in the repository. Change those lines only from the owner's account. The Update desk checks this and shows **Turn on automatic updates** when the schedule hasn't run; the button commits a one-minute shift of the schedule from the owner's account. Edits to other parts of the workflow file don't change who the schedule runs as.

GitHub also pauses schedules in a public repository after 60 days without a commit. Publishing from the desk counts as a commit; if it ever happens, the desk shows **Switch them back on**.

Open pages reload `data/quotes.json` every 5 minutes. Safeguards:
- a ticker Yahoo cannot price keeps its last good price (or the 30 Sep 2026 snapshot), with its date shown;
- a target more than 3x or under 0.3x the price (for example, one not adjusted for a split) is dropped instead of shown;
- the page header says whether it is showing live prices or the snapshot, and when they were updated.

To add a company to the watchlist, add it to `C` and `Q` in `src/supply/supply_data.py` (the ticker must use Yahoo's suffix, such as `.T`, `.KS`, `.TW`, `.TWO`, `.SZ`, `.SS`, `.HK`, `.DE`, `.AS` or `.PA`) and list it in one of the `GROUPS`.

## 2. Developments (as they happen)

### From the Update desk

1. Open the **Update desk** on the Supply Chain Atlas and connect GitHub once (README: "Connect GitHub").
2. Press **Refresh now** if the headlines are more than a few hours old, then scan the **News radar**. Filter by topic; **Hide** what doesn't matter (hidden headlines are remembered in that browser).
3. **Add to log** on a headline fills in the date, headline, source and the chain links for its topic. Write two or three sentences on what happened and why it matters, adjust the links, and add any changes (the same change types as the table below).
4. **Preview**, then **Publish**. The desk commits the entry to `data/developments.json`, follows the rebuild, and reloads the page with the entry in the log, on both pages, about two minutes later.
5. **Your log** lists every entry with **Edit** and **Delete**. Use **Coming up** for dated events that haven't happened yet.

Each entry gets a permanent `id` (date plus headline). Visitors without a key can fill in the same form; **Suggest on GitHub** opens a prefilled issue instead of publishing.

### By hand

Add one object to `entries` in `data/developments.json` and push. Locally, `python src/build.py` checks every id and stops with a readable error if something does not exist. The workflow builds with `--lenient` instead: a broken link or change is left out, the rest of the site still publishes with fresh prices, and the problem is listed on the Update desk (and in `site/data/build.json`) until it is fixed.

```json
{
  "date": "2026-11-10",
  "title": "China extends its pause on mineral export controls to May 2027",
  "summary": "Two or three sentences with the numbers that matter.",
  "pages": ["supply", "atlas"],
  "links": {"nodes": ["ree", "gallium"], "scenarios": ["minerals"], "companies": ["mp"], "sites": [], "atlasItems": []},
  "source": {"label": "Reuters, 10 Nov 2026", "url": "https://..."},
  "changes": [
    {"type": "node_status", "node": "gallium", "status": "warning", "line": "Pause extended; licences flowing."},
    {"type": "scenario_status", "scenario": "minerals", "status": "plausible", "when": "Pause now ends May 2027"}
  ]
}
```

`pages` picks where the entry appears (`supply`, `atlas` or both). Ids: link (node) ids, site ids and scenario ids are in `src/supply/supply_data.py`; company keys are the keys of `C` there; Investment Atlas ids are the first argument of each `it(...)` in `src/atlas/data_items.py`.

| `type` | Fields | Effect |
|---|---|---|
| `node_status` | `node`, `status` (`critical`, `serious`, `warning`), optional `state`, `line` | Re-rates a chokepoint and adds the source to it |
| `node_note` | `node`, `text` | Appends a sentence to a link's explanation |
| `site_status` | `site`, `status`, optional `note` | Changes a map site (`normal`, `ramping`, `tight`, `short`, `controlled`, `offline`, `struck`, `threatened`, `disrupted`, `at risk`) |
| `add_site` | `node`, `name`, `lat`, `lon`, optional `who`, `note`, `status`, `id` (made from the name if left out) | Puts a new plant, mine or campus on the map |
| `scenario_status` | `scenario`, optional `status` (`live`, `scheduled`, `plausible`, `tail`), `when` | Moves a worst case between "happening now", "on the calendar" and so on |
| `quote_note` | `company`, `proj` | Replaces the "projection to follow" text in the watchlist |
| `atlas_item_status` | `item`, optional `status`, `note_append` | Updates an Investment Atlas project |
| `add_atlas_item` | `item`: `{title, who, cat, kind, date, place, country, lat, lon}`, optional `amount`, `status`, `note`, `prec` (default `city`), `gw`, `amount_note`, `partners`, `iso`, `id` (made from the title if left out) | Adds a new investment to the Investment Atlas map and table |

Dated events that have not happened yet (deadlines, plant openings) go in `upcoming` with a `date` (add `approx`, such as "Mid-2027", when the date is rough). Company report dates are added automatically from Yahoo.

Anyone can also open an issue with the **New development** form; the weekly review turns open issues into entries.

### The news radar

`data/news_queries.json` lists 17 topics, each with one or more Google News searches (last 7 days) and the chain links, scenarios, companies and sites a headline on that topic connects to. Edit it to add or sharpen a topic; ids must exist in `src/supply/supply_data.py`. `scripts/fetch_news.py` keeps up to 160 stories from the last 10 days. It groups reports of the same story under one headline (the desk lists the other sources), tags each story with every topic that found it, and drops noise: the sources in `skipSources` and titles matching the `skipTitles` patterns (stock-pick listicles, market-research press releases, price-target notes). Add to either list when junk gets through. Headlines link through Google News; replace the link with the publisher's own if you prefer.

### The weekly review

Once a week, run through the news radar, the "Early warnings to watch" under each scenario and these questions, adding an entry for each real change:

- **Export controls:** any MOFCOM notice on rare earths, gallium, germanium, indium or tungsten (pauses end 10 Nov and 27 Nov 2026); US chip export rules; Section 232 tariff changes.
- **Gulf and Taiwan:** Hormuz traffic, Ras Laffan restart, strikes or threats on Gulf data centers, PLA exercises around Taiwan.
- **Capacity:** CoWoS, HBM, InP lasers, T-glass, ABF substrates, gas turbines and transformers: new plants, delays or allocation changes.
- **Money:** new AI investments of $1B or more, lab funding rounds and revenue, hyperscaler capex guidance, credit ratings and refinancing for Oracle, CoreWeave and other leveraged builders.

Publish from the desk, or rebuild (`python src/build.py`), check the build output for errors, and push.

## 3. Quarterly numbers (after each earnings season)

- `src/atlas/data_items.py`: update `BUILDERS` (capex by year, revenue run-rate, operating cash flow, 2026 spend), `LABS` (commitments, revenue), `FLOWS` (new contracts) and `COLLECTORS`; run `python src/atlas/model.py` to see the new payback verdicts.
- `src/supply/supply_data.py`: refresh market shares (HBM, wafers, substrates, optics, rack assembly) when new data appears, and the research snapshot in `Q` if Yahoo's coverage of a ticker is poor.
- Change "Research as of" dates in the two templates.

## 4. Changing the Update desk itself

The desk is one file, `src/common/desk.js`, loaded only on the GitHub Pages build. After changing it, the templates or `src/build.py`, run the browser tests:

```bash
pip install playwright && playwright install chromium
python tests/test_desk.py            # about 2 minutes; add --shots shots to save screenshots
```

They build the site into a temporary folder and answer every GitHub call with a stand-in, so nothing is published. They cover visitors, the news radar, connecting a key, turning the schedule on, Refresh now, publishing, editing and deleting, a paused workflow, build warnings, missing permissions, a cached page catching up, the Investment Atlas bar and phone layouts.
