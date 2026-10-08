# Keeping the pages current

There are three update paths: prices and headlines update themselves, developments are logged from the Update desk (or in one file), and the deeper numbers are refreshed each quarter. The Odds has its own model file, described in section 5.

## 1. Prices, analyst targets and headlines (automatic)

`.github/workflows/pages.yml` is scheduled for every 15 minutes on weekdays and every 6 hours at weekends (GitHub runs schedules only when it has spare capacity: in practice every 4 to 9 hours), and also runs on every push to `main` and on demand (the Update desk's **Refresh now** button or the Actions tab). Each run:

1. restores the last `site/data/quotes.json` and `site/data/news.json` from the Actions cache;
2. runs `scripts/fetch_quotes.py`, which downloads the latest price for all 92 tickers in one batch and, once a day, each company's average analyst target, rating, number of analysts and next report date;
3. runs `scripts/fetch_news.py` when the headlines are more than 3 hours old (always on **Refresh now**; on a push only when there are none yet, so published entries go live quickly);
4. rebuilds both pages with those numbers embedded (`--lenient`, see below), and deploys to GitHub Pages.

Scheduled runs are set a few minutes past the quarter-hour because GitHub delays, and sometimes drops, scheduled jobs at the start of the hour.

**If scheduled updates stop.** A new or changed schedule can take up to a day to start. If the Update desk shows that no scheduled update has run for a day, press **Restart automatic updates**: it shifts each scheduled minute by one, which makes GitHub register the schedule again. (An earlier note here blamed the account that wrote the schedule; that was wrong. The schedule started by itself on 2 October 2026.)

GitHub also pauses schedules in a public repository after 60 days without a commit. Publishing from the desk counts as a commit; if it ever happens, the desk shows **Switch them back on**.

Open pages reload `data/quotes.json` every 5 minutes. Safeguards:
- a ticker Yahoo cannot price keeps its last good price (or the 30 Sep 2026 snapshot), with its date shown;
- a target more than 3x or under 0.3x the price (for example, one not adjusted for a split) is dropped instead of shown;
- the page header says whether it is showing live prices or the snapshot, and when they were updated.

To add a company to the watchlist, add it to `C` and `Q` in `src/supply/supply_data.py` (the ticker must use Yahoo's suffix, such as `.T`, `.KS`, `.TW`, `.TWO`, `.SZ`, `.SS`, `.HK`, `.DE`, `.AS` or `.PA`) and list it in one of the `GROUPS`.

## 2. Developments (as they happen)

### From the Update desk

1. Open the **Update desk** on The Chain and connect GitHub once (README: "Connect GitHub").
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

`pages` picks where the entry appears (`supply`, `atlas` or both). Ids: link (node) ids, site ids and scenario ids are in `src/supply/supply_data.py`; company keys are the keys of `C` there; project ids are the first argument of each `it(...)` in `src/atlas/data_items.py`.

| `type` | Fields | Effect |
|---|---|---|
| `node_status` | `node`, `status` (`critical`, `serious`, `warning`), optional `state`, `line` | Re-rates a chokepoint and adds the source to it |
| `node_note` | `node`, `text` | Appends a sentence to a link's explanation |
| `site_status` | `site`, `status`, optional `note` | Changes a map site (`normal`, `ramping`, `tight`, `short`, `controlled`, `offline`, `struck`, `threatened`, `disrupted`, `at risk`) |
| `add_site` | `node`, `name`, `lat`, `lon`, optional `who`, `note`, `status`, `id` (made from the name if left out) | Puts a new plant, mine or campus on the map |
| `scenario_status` | `scenario`, optional `status` (`live`, `scheduled`, `plausible`, `tail`), `when` | Moves a worst case between "happening now", "on the calendar" and so on |
| `quote_note` | `company`, `proj` | Replaces the "projection to follow" text in the watchlist |
| `atlas_item_status` | `item`, optional `status`, `note_append` | Updates an project in The Money |
| `add_atlas_item` | `item`: `{title, who, cat, kind, date, place, country, lat, lon}`, optional `amount`, `status`, `note`, `prec` (default `city`), `gw`, `amount_note`, `partners`, `iso`, `id` (made from the title if left out) | Adds a new investment to The Money map and table |

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

The desk is one file, `src/common/desk.js`, loaded only on the GitHub Pages build. After changing it, the templates of The Chain or The Money, or `src/build.py`, run the browser tests:

```bash
pip install playwright && playwright install chromium
python tests/test_desk.py            # about 2 minutes; add --shots shots to save screenshots
```

They build the site into a temporary folder and answer every GitHub call with a stand-in, so nothing is published. They cover visitors, the news radar, connecting a key, turning the schedule on, Refresh now, publishing, editing and deleting, a paused workflow, build warnings, missing permissions, a cached page catching up, The Money bar and phone layouts.

## 5. The Odds: engine, model and page

The Odds (`/odds/`) is made of three files: the engine (the maths), the model (what is uncertain and what each thing does) and the page. `src/build.py` puts the engine and the model inside the page, so the page needs nothing else once it has loaded.

### The engine

`src/common/odds_engine.js` is the maths. It has no page, storage or network code, and the same file runs in the browser (`window.ODDS`) and in Node. What it does:

- **Drivers.** An event has a probability. A range has a low case (undercut 1 time in 10), a central case and a high case (beaten 1 time in 10).
- **Links.** Any two drivers can have a correlation. `reading()` puts one in plain numbers ("if A happens, B's chance goes from 25% to 60%") and `rhoForReading()` goes the other way. A set of links that cannot all be true together is replaced by the closest set that can, and the run reports how much it had to change.
- **Futures.** `simulate()` draws thousands of futures, turns each into shocks on the chain and changes in orders, runs the same weakest-link model as `src/supply/supply_model.py`, and records what gets built and what limited it. `given` supposes a situation ("the blockade happens") so that everything linked to it shifts with it.
- **Reading the results.** `summary()`, `whatMatters()` (which drivers move an outcome most), `bindingTable()` (what limits the build-out and how often), `subset()` and `profile()` (pick the futures with some outcome and see what they have in common).

### The model

`data/odds.json` lists what is uncertain about the 2027 build-out and what each thing does. Everything is measured against **the plan**: 100 is the capacity today's plans would add in 2027. It has:

- `drivers`: each has a plain `question`, how it `resolves` (or what to `watch`), a `basis` label (`judgement`, `researched`, `sourced` or `market`), a `note` saying where the number comes from, a `does` sentence, and its `effects`. A number that is not plain `judgement` also has `checked` (the day it was researched) and `src`, a list of sources as `{"t": "title", "u": "https://..."}`; the About panel shows them as links. The build leaves out a source without a title or a web link and lists it on the Update desk. An event has `p`, a `deadline` and a severity `sev` (1 = as The Chain's scenario has it); a range has `low`, `mid`, `high` and a `unit`.
- `links`: pairs of drivers with a correlation `rho` and the reason `why`. Positive means two events tend to happen together, or an event goes with the high side of a range. Write each link cause first (`a` is the thing that happens, `b` the thing it moves): the page reads it as "if a happens, b goes from … to …".
- `stories`: the groups the page files links under (US–China tension, the Gulf war, chip supply, power, AI demand and money), each with a `label` and a one-line `blurb`. Every driver names its `story`; a link goes in the story of its first driver unless it names a `story` of its own. A story the page does not know only moves those links to "Other links", and the Update desk lists it.
- `say` on every driver: the words a sentence uses for it. An event has `if` ("China blockades Taiwan", for "If China blockades Taiwan, …") and `of` ("of a Taiwan blockade", for "the chance of a Taiwan blockade"; start it with "of" or "that"). A quantity has `if`, which is its high case ("lab revenue hits its high case"), `subj` ("hyperscaler spending plans"), `pl: true` when the subject is plural, and optionally `unit` when its own `unit` reads badly after a number (lab revenue uses "(today = 100)").
- `buyers`: who places the orders (hyperscalers 70%, neoclouds 20%, sovereign 10%).

Effects are listed at the top of the simulation section of the engine. The common ones: `{"t": "scen", "id": "taiwan"}` applies one of The Chain's scenarios, `{"t": "ramp", "node": "cowos"}` makes a link deliver the range's value as a share of plan, `{"t": "dem", "seg": "neo", "m": 0.55}` multiplies a buyer group's orders, and `{"t": "demlvl", "seg": "hyper", "base": "mid"}` moves a group's orders with a range, measured against its starting central case.

Every starting number is marked `judgement` until it has been researched. When you change a number, update its `note` (the facts behind it, with dates), set `basis` (`researched` when it is a judgement made after research; `market` when it is anchored on a forecasting market; `sourced` when it is taken from one named source), set `checked` and `src`, and move `asOf` to the day you did it (deadlines are counted in months from `asOf`). Update `statusNote` to say which groups have been researched. The geopolitics and trade-rules group was researched on 8 Oct 2026.

### The page

`src/odds/template.html` shows one row per driver, grouped as in the model file: a chance (yes-or-no questions) or a low, central and high case (quantities), a slider, and an About panel with how the question resolves, what the driver does, where its number comes from and, for events, how bad it is if it happens. Results sit beside the list: the average and typical share of the plan that gets built, the spread, what holds it back, what matters most, and how much each stage of the chain delivers. **Suppose it happens** keeps only the futures in which something happens, so linked drivers shift; each affected row shows where it lands.

**What moves together** starts with one control for every link at once (none, half, as set, or 1.5 times as strong), each setting showing its chance of a bad year, so you can see what the links do before reading any of them. Below it the links are filed under five stories, folded until opened. Each link reads as a sentence with the current numbers ("If China blockades Taiwan, the chance that China's mineral controls return goes from 30% to 75%") and its strength is one of five words: much less likely, less likely, no link, more likely, much more likely (much lower to much higher when the second is a quantity), which set −0.6, −0.3, 0, +0.3 and +0.6. **Fine-tune** opens the exact strength (−0.95 to +0.95) and both readings with fields: typing where one should land works out the strength, and says so when no link could get it that far. Links can be added between any two drivers, from the bar above the stories or from a driver's row, and added ones deleted; a filter shows one driver's links, and a folded grid shows every pair at a glance.

Every driver's row also shows its links as tags ("↑↑ China's mineral controls return": arrows up for the same way, down for opposite ways, two for strong). A tag opens the link under the row, as a sentence read from that driver, with the five words. If a set of links cannot all be true at once, the page uses the closest set that can and says which pair moved most; at the 1.5 times setting the master control says so instead.

The numbers are worked out in a background worker, 10,000 futures at a time, always the same futures, so a change in the results comes from the numbers and not from chance. Changes are kept only until the page is reloaded.

### After a change

After changing the engine, the model file, or the chain in `src/supply/supply_data.py`, run:

```bash
node tests/test_engine.mjs           # a few seconds; needs Node 18 or later and python3
```

After changing the page, the engine or `src/build.py`, also run:

```bash
python tests/test_odds.py            # about a minute; add --shots shots to save screenshots
```

The tests compare the bell-curve functions with reference values from SciPy, the chain with the Python model on every link of every scenario, and simulated frequencies with the exact answers. For the model file they check that every driver is complete, that every link and scenario it names exists, that the starting links can all hold together, and that the plan is delivered in full when nothing goes wrong. The last lines print the baseline: the central case, the most frequent limits and the biggest swings.
