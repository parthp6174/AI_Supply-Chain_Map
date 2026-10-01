# Keeping the atlases current

There are three update paths: prices update themselves, developments go into one file, and the deeper numbers are refreshed each quarter.

## 1. Prices and analyst targets (automatic)

`.github/workflows/pages.yml` runs every 15 minutes on weekdays, on every push to `main`, and on demand from the Actions tab. Each run:

1. restores the last `site/data/quotes.json` from the Actions cache;
2. runs `scripts/fetch_quotes.py`, which downloads the latest price for all 92 tickers in one batch and, once a day, each company's average analyst target, rating, number of analysts and next report date;
3. rebuilds both pages with those numbers embedded, and deploys to GitHub Pages.

Open pages reload `data/quotes.json` every 5 minutes. Safeguards:
- a ticker Yahoo cannot price keeps its last good price (or the 30 Sep 2026 snapshot), with its date shown;
- a target more than 3x or under 0.3x the price (for example, one not adjusted for a split) is dropped instead of shown;
- the page header says whether it is showing live prices or the snapshot, and when they were updated.

To add a company to the watchlist, add it to `C` and `Q` in `src/supply/supply_data.py` (the ticker must use Yahoo's suffix, such as `.T`, `.KS`, `.TW`, `.TWO`, `.SZ`, `.SS`, `.HK`, `.DE`, `.AS` or `.PA`) and list it in one of the `GROUPS`.

## 2. Developments (weekly, or as they happen)

Add one object to `entries` in `data/developments.json` and push. The build checks every id and stops with a readable error if something does not exist.

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
| `add_site` | `id`, `node`, `name`, `who`, `lat`, `lon`, `note`, optional `status` | Puts a new plant, mine or campus on the map |
| `scenario_status` | `scenario`, optional `status` (`live`, `scheduled`, `plausible`, `tail`), `when` | Moves a worst case between "happening now", "on the calendar" and so on |
| `quote_note` | `company`, `proj` | Replaces the "projection to follow" text in the watchlist |
| `atlas_item_status` | `item`, optional `status`, `note_append` | Updates an Investment Atlas project |
| `add_atlas_item` | `item`: `{id, title, who, cat, kind, amount, date, place, country, lat, lon, prec, status, note}`, optional `gw`, `amount_note`, `partners`, `iso` | Adds a new investment to the Investment Atlas map and table |

Dated events that have not happened yet (deadlines, plant openings) go in `upcoming` with a `date` (add `approx`, such as "Mid-2027", when the date is rough). Company report dates are added automatically from Yahoo.

Anyone can also open an issue with the **New development** form; the weekly review turns open issues into entries.

### The weekly review

Once a week, run through the "Early warnings to watch" under each scenario and these questions, adding an entry for each real change:

- **Export controls:** any MOFCOM notice on rare earths, gallium, germanium, indium or tungsten (pauses end 10 Nov and 27 Nov 2026); US chip export rules; Section 232 tariff changes.
- **Gulf and Taiwan:** Hormuz traffic, Ras Laffan restart, strikes or threats on Gulf data centers, PLA exercises around Taiwan.
- **Capacity:** CoWoS, HBM, InP lasers, T-glass, ABF substrates, gas turbines and transformers: new plants, delays or allocation changes.
- **Money:** new AI investments of $1B or more, lab funding rounds and revenue, hyperscaler capex guidance, credit ratings and refinancing for Oracle, CoreWeave and other leveraged builders.

Then rebuild (`python src/build.py`), check the build output for errors, and push.

## 3. Quarterly numbers (after each earnings season)

- `src/atlas/data_items.py`: update `BUILDERS` (capex by year, revenue run-rate, operating cash flow, 2026 spend), `LABS` (commitments, revenue), `FLOWS` (new contracts) and `COLLECTORS`; run `python src/atlas/model.py` to see the new payback verdicts.
- `src/supply/supply_data.py`: refresh market shares (HBM, wafers, substrates, optics, rack assembly) when new data appears, and the research snapshot in `Q` if Yahoo's coverage of a ticker is poor.
- Change "Research as of" dates in the two templates.
