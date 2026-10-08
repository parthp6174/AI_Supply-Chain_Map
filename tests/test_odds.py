#!/usr/bin/env python3
"""Browser tests for The Odds, the probability lab (src/odds/template.html with src/common/odds_engine.js).

    pip install playwright && playwright install chromium
    python tests/test_odds.py                 # builds the site into a temp folder, serves it, runs every check
    python tests/test_odds.py --shots shots   # also saves screenshots (desktop, a supposed situation, phone) into shots/

Nothing is published and nothing outside this machine is contacted. Exit code 1 if any check fails.

Covers: the third tab on all three pages; every driver's row; the starting results against the engine run on the
page itself; changing a chance, a range and a severity; typing decimals; resetting; supposing an event, a range
case and something impossible; the links (stories, the five words, Fine-tune, adding and deleting, each driver's tags
and the panel they open, the grid) and how strongly they hold at once; chart tooltips by mouse and keyboard; a browser
without workers; phones in light and dark. The maths is tested separately in tests/test_engine.mjs.
"""
import argparse, functools, http.server, json, os, re, subprocess, sys, tempfile, threading

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE = json.load(open(os.path.join(ROOT, "data", "odds.json"), encoding="utf-8"))
DRIVERS = {d["id"]: d for d in FILE["drivers"]}
N_EVENTS = sum(1 for d in FILE["drivers"] if d["kind"] == "event")
N_RANGES = len(FILE["drivers"]) - N_EVENTS
BASE = OUT = SITE = None
RESULTS = []
IDLE = "window.ODDSLAB && ODDSLAB.res.cur && !ODDSLAB.busy"


def iso_ago(hours):
    import datetime as dt
    t = dt.datetime.now(dt.timezone.utc).replace(microsecond=0) - dt.timedelta(hours=hours)
    return t.isoformat().replace("+00:00", "Z")


# market odds as scripts/fetch_markets.py writes them: prices recorded on 8 Oct 2026, read 2 hours before the test
# (one 3 days before), plus a market nobody lists and one with an impossible price, which the build must drop
MARKET_SAMPLE = {"fetched": iso_ago(2), "errors": [], "items": {
    "polymarket:2382819": {"yes": 0.0335, "at": iso_ago(2), "question": "Will China blockade Taiwan in 2026?", "end": "2027-01-01T04:59:00Z", "closed": False, "volume": 405516, "week": 0.0005, "bid": 0.033, "ask": 0.034},
    "polymarket:677407": {"yes": 0.0435, "at": iso_ago(2), "question": "China x Taiwan military clash before 2027?", "end": "2027-01-01T04:59:00Z", "closed": False, "volume": 3447247, "week": -0.002},
    "polymarket:2176270": {"yes": 0.205, "at": iso_ago(2), "question": "Strait of Hormuz traffic returns to normal by December 31?", "end": "2027-01-01T04:59:00Z", "closed": False, "volume": 13747749, "week": -0.01},
    "polymarket:4713484": {"yes": 0.44, "at": iso_ago(72), "question": "US-Iran ceasefire continues through December 31?", "end": "2026-12-31T23:59:00Z", "closed": False, "volume": 108719},
    "polymarket:1345235": {"yes": 0.228, "at": iso_ago(2), "question": "Will OpenAI not IPO by December 31, 2027?", "end": "2028-01-01T04:59:00Z", "closed": False, "volume": 91105},
    "polymarket:999": {"yes": 0.5, "at": iso_ago(1), "question": "Not listed on any driver"},
    "polymarket:1811266": {"yes": 7, "at": iso_ago(1), "question": "An impossible price"}}}
STRIP_DONE = "window.ODDSLAB && !ODDSLAB.busy && !ODDSLAB.stripBusy && Object.keys(ODDSLAB.strip.res).length === 4"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- " + str(detail)[:300]))


def shot(target, name):
    if OUT:
        target.screenshot(path=os.path.join(OUT, name))


def new_page(browser, scheme="light", width=1280, height=900, init=None, touch=False):
    ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme, has_touch=touch, is_mobile=touch)
    if init:
        ctx.add_init_script(init)
    ctx.route("https://fonts.googleapis.com/**", lambda r, q: r.fulfill(status=200, body="", headers={"Content-Type": "text/css"}))
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append("console:" + m.text) if m.type == "error" and not m.text.startswith("Failed to load resource") else None)
    page.on("dialog", lambda d: (errors.append("dialog:" + d.message), d.dismiss()))
    return ctx, page, errors


def settle(page):
    """Wait until the page has finished working out the numbers for the latest change."""
    page.wait_for_timeout(130)
    page.wait_for_function(IDLE, timeout=20000)
    page.wait_for_timeout(60)


def hero(page):
    return int(page.inner_text("#hero-v").strip().rstrip("%"))


def typed(page, selector, value):
    """Type a number into a field and leave the field."""
    page.fill(selector, str(value)); page.locator(selector).blur(); settle(page)


def slide(page, selector, value):
    page.evaluate("([s, v]) => { const e = document.querySelector(s); e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('change', {bubbles: true})); }", [selector, value])
    settle(page)


def clean_text(page, label):
    text = page.inner_text("body")
    bad = [w for w in ("null", "undefined", "NaN", "[object", "n/a") if w in text]
    check(f"{label}: no stray null, undefined or NaN on the page", not bad, bad)


# ---------------------------------------------------------------- the checks
def run_checks(browser):
    ctx, page, errors = new_page(browser)
    page.goto(BASE + "odds/"); settle(page)

    # 1. the page and the switch
    check("page: title and heading", page.title() == "The Odds · Chokepoint" and page.inner_text("h1").strip().lower() == "the odds", page.title())
    tabs = page.locator(".atlases a")
    check("switch: three pages offered, The Odds marked", tabs.count() == 3 and page.get_attribute("#nav-odds", "aria-current") == "page" and page.get_attribute("#nav-supply", "aria-current") is None)
    check("switch: the other tabs point to their pages", page.evaluate("[document.querySelector('#nav-supply').href, document.querySelector('#nav-atlas').href]") == [BASE, BASE + "money/"])
    check("switch: each tab has its one-line summary", all(len(page.inner_text(f"#nav-{k}-c").strip()) > 20 for k in ("supply", "atlas", "odds")))
    check("notice: starting numbers are marked provisional", "Provisional" in page.inner_text("#notice") or "PROVISIONAL" in page.inner_text("#notice"), page.inner_text("#notice"))
    check("notice: says the numbers are first estimates", FILE["statusNote"][:40] in page.inner_text("#notice-t"))

    # 2. the drivers
    rows = page.locator(".drv")
    check(f"drivers: one row for each of the {len(DRIVERS)}", rows.count() == len(DRIVERS), rows.count())
    check("drivers: grouped under the four headings", page.locator(".grp").count() == len(FILE["groups"]) and [t.strip().lower() for t in page.locator(".grp-h h3").all_inner_texts()] == [g["label"].lower() for g in FILE["groups"]])
    check("drivers: one field per chance and three per quantity", page.locator(".drv .nf").count() == N_EVENTS + 3 * N_RANGES, page.locator(".drv .nf").count())
    check("drivers: every row shows its question", page.evaluate("[...document.querySelectorAll('.drv-q')].every(e => e.textContent.trim().endsWith('?'))"))
    shown = page.evaluate("Object.fromEntries([...document.querySelectorAll('.drv')].map(r => [r.dataset.id, [...r.querySelectorAll('.drv-top .nf')].map(f => +f.value)]))")
    want = {k: ([round(d["p"] * 100, 1)] if d["kind"] == "event" else [d["low"], d["mid"], d["high"]]) for k, d in DRIVERS.items()}
    check("drivers: fields show the starting numbers from the model file", shown == want, [k for k in want if shown.get(k) != want[k]][:4])
    check("drivers: every control has a spoken name", page.evaluate("[...document.querySelectorAll('.drv input')].every(e => (e.getAttribute('aria-label') || '').length > 8 || e.id)"))
    check("drivers: nothing changed yet, Reset all is off", page.inner_text("#dchanged") == "These are the starting numbers" and page.is_disabled("#reset-all"))

    # 3. the starting results, against the engine run on the page's own thread
    base = page.evaluate("ODDSLAB.compute({n: ODDSLAB.N, seed: ODDSLAB.SEED, beliefs: {drivers: {}}, given: {}})")
    h0 = hero(page)
    check("results: worked out in a background worker", page.evaluate("ODDSLAB.usingWorker()") is True)
    check(f"results: the headline is the engine's average ({h0}% of plan)", h0 == round(base["built"]["mean"] * 100) and 78 <= h0 <= 97, (h0, base["built"]["mean"]))
    check("results: typical, low and tightness tiles filled in", [page.inner_text(s) for s in ("#t-mid", "#t-low", "#t-tight")] == [page.evaluate("pct(%r)" % base["built"]["p50"]), page.evaluate("pct(%r)" % base["built"]["p10"]), "%d%%" % round(base["tight"]["p50"] * 100)])
    below80 = page.inner_text("#t-below")
    page.select_option("#t-thr", "0.9")
    check("results: the threshold can be changed", page.inner_text("#t-below") == page.evaluate("pct(%r)" % base["below"]["0.9"]) and page.inner_text("#t-below") != below80, (below80, page.inner_text("#t-below")))
    page.select_option("#t-thr", "0.8")
    check("results: no comparison shown while nothing is changed", page.is_hidden("#hero-d") and page.locator("#hist-lg .lg").count() == 0 and page.is_hidden("#situ"))
    check("chart: bars drawn and described for screen readers", page.locator("#hist path.bar").count() >= 10 and "On average %d%% of plan" % h0 in page.get_attribute("#hist", "aria-label") and "average %d%%" % h0 in page.text_content("#hist text.lab"))
    page.click("#b-hist details summary")
    check("chart: the same numbers as a table", page.locator("#hist-tbl tbody tr").count() == 8 and page.locator("#hist-tbl tbody tr").nth(3).inner_text().split()[-1] == page.inner_text("#t-mid") and page.locator("#hist-tbl tbody tr").nth(7).inner_text().split()[-1] == page.evaluate("pct(%r)" % base["built"]["mean"]), page.locator("#hist-tbl tbody tr").nth(7).inner_text())
    lim = page.evaluate("[...document.querySelectorAll('#lim .row')].map(r => [r.querySelector('.nm').firstChild.textContent, parseFloat(r.querySelector('.val').textContent)])")
    check("limits: shares add up to about 100%", 7 <= len(lim) <= 8 and abs(sum(v for _, v in lim) - 100) < 1.5, lim)
    check("limits: named in plain words, not by id", all((re.search(r"[A-Z]", n) or n.endswith("other links")) and "_" not in n for n, _ in lim) and any(n.startswith("Demand") for n, _ in lim), [n for n, _ in lim])
    check("limits: each link says which numbers move it", page.locator("#lim button.row small").count() >= 4 and page.locator("#lim button.row small").first.inner_text().startswith("moved by "))
    mat = page.locator("#mat .row .nm")
    check("what matters: ten rows, the Taiwan blockade first", mat.count() == 10 and mat.first.inner_text().startswith("Taiwan blockade"), mat.first.inner_text())
    page.click('#mat-seg [data-m="swing"]')
    first_swing = page.locator("#mat .row .val").first.inner_text()
    check("what matters: can be ranked by the size of the swing", page.get_attribute('#mat-seg [data-m="swing"]', "aria-pressed") == "true" and re.fullmatch(r"[+−]\d+", first_swing.strip()) is not None, first_swing)
    page.click('#mat-seg [data-m="share"]')
    check("down the chain: six stages with a central and a low value", page.locator("#outs .orow").count() == 7 and re.fullmatch(r"\d+(\.\d)?%", page.locator("#outs .orow").nth(1).locator(".r").first.inner_text()) is not None)
    clean_text(page, "start")
    shot(page, "odds_desktop.png")

    # 4. tooltips: mouse and keyboard
    page.evaluate("document.querySelector('#hist').scrollIntoView({block: 'center'})")
    box = page.locator("#hist .hit").nth(12).bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    check("chart: hovering a bar shows its share of futures", page.is_visible("#tip") and "of plan" in page.inner_text("#tip .tt") and "%" in page.inner_text("#tip .tr b"), page.inner_text("#tip"))
    page.mouse.move(5, 5)
    check("chart: the tooltip goes away", page.is_hidden("#tip"))
    page.focus("#hist"); page.keyboard.press("ArrowRight"); page.keyboard.press("ArrowRight")
    tip1 = page.inner_text("#tip .tt") if page.is_visible("#tip") else ""
    page.keyboard.press("ArrowLeft")
    check("chart: arrow keys read the bars one by one", "of plan" in tip1 and page.is_visible("#tip") and page.inner_text("#tip .tt") != tip1 and page.locator("#hist .bar.on").count() <= 1, tip1)
    page.keyboard.press("Escape")
    check("chart: Escape closes the tooltip", page.is_hidden("#tip"))
    page.locator("#lim .row").first.focus()
    check("limits: focusing a row explains it", page.is_visible("#tip") and "of futures" in page.inner_text("#tip"), page.inner_text("#tip") if page.is_visible("#tip") else "")
    page.locator("#lim .row").first.blur()

    # 5. change a chance
    typed(page, '#d-tw_blockade [data-f="p"]', 30)
    h1 = hero(page)
    check(f"change: a 30% chance of a blockade lowers the headline ({h0}% to {h1}%)", h1 <= h0 - 4, (h0, h1))
    check("change: the row is marked and shows where it started", "changed" in page.get_attribute("#d-tw_blockade", "class") and "Started at 3%" in page.inner_text("#d-tw_blockade .drv-note"), page.inner_text("#d-tw_blockade .drv-note"))
    check("change: counted above the list, Reset all is on", page.inner_text("#dchanged") == "1 number changed" and page.is_enabled("#reset-all"))
    check("change: compared with the starting numbers", page.is_visible("#hero-d") and "below the starting numbers (%d%%)" % h0 in page.inner_text("#hero-d") and [t.strip() for t in page.locator("#hist-lg .lg").all_inner_texts()] == ["Your numbers", "Starting numbers"] and page.locator("#hist path.ref").count() == 1 and page.locator("#lim .trk u").count() >= 5, page.inner_text("#hero-d"))
    check("change: the slider follows the typed number", page.input_value("#d-tw_blockade .drv-ctl .sl") == "30" and page.get_attribute("#d-tw_blockade .drv-ctl .sl", "aria-valuetext") == "30%")
    page.click("#d-tw_blockade .drv-note button")
    settle(page)
    check("reset one: back to the starting number and the starting results", hero(page) == h0 and page.input_value('#d-tw_blockade [data-f="p"]') == "3" and page.is_hidden("#hero-d") and page.inner_text("#dchanged") == "These are the starting numbers")
    slide(page, "#d-gulf_persist .drv-ctl .sl", 80)
    check("slider: moving it sets the chance", page.input_value('#d-gulf_persist [data-f="p"]') == "80" and page.evaluate("ODDSLAB.cur.gulf_persist.p") == 0.8)
    # decimals survive while the page re-renders around the field
    page.click('#d-tw_blockade [data-f="p"]'); page.fill('#d-tw_blockade [data-f="p"]', ""); page.keyboard.type("2.", delay=40); settle(page)
    mid_typing = page.input_value('#d-tw_blockade [data-f="p"]')
    page.keyboard.type("5", delay=40); settle(page)
    check("typing: a decimal is not overwritten while it is being typed", page.input_value('#d-tw_blockade [data-f="p"]') == "2.5" and page.evaluate("ODDSLAB.cur.tw_blockade.p") == 0.025, (mid_typing, page.input_value('#d-tw_blockade [data-f="p"]')))
    typed(page, '#d-tw_blockade [data-f="p"]', 250)
    check("typing: a chance above 100 is brought back to 100", page.input_value('#d-tw_blockade [data-f="p"]') == "100" and page.evaluate("ODDSLAB.cur.tw_blockade.p") == 1)
    page.fill('#d-tw_blockade [data-f="p"]', ""); page.locator('#d-tw_blockade [data-f="p"]').blur(); settle(page)
    check("typing: an empty field goes back to the last number", page.input_value('#d-tw_blockade [data-f="p"]') == "100")

    # 6. a quantity: low, central, high
    d = DRIVERS["inp_ramp"]
    typed(page, '#d-inp_ramp [data-f="mid"]', d["low"] - 8)
    vals = lambda: [float(page.input_value(f'#d-inp_ramp [data-f="{f}"]')) for f in ("low", "mid", "high")]
    check("range: a central case below the low case takes the low case with it", vals() == [d["low"] - 8, d["low"] - 8, d["high"]], vals())
    typed(page, '#d-inp_ramp [data-f="high"]', d["low"] - 30)
    check("range: the high case cannot go below the central case", vals() == [d["low"] - 8, d["low"] - 8, d["low"] - 8], vals())
    typed(page, '#d-inp_ramp [data-f="high"]', d["high"])
    slide(page, "#d-inp_ramp .drv-ctl .sl", d["low"] + 2)
    check("range: the slider moves low, central and high together", vals() == [d["low"] + 2, d["low"] + 2, min(d["max"], d["high"] + 10)], vals())
    check("range: the band on the slider follows", page.evaluate("(() => { const i = document.querySelector('#d-inp_ramp .slw .trk i'); return parseFloat(i.style.width) > 5 && parseFloat(i.style.left) > 30; })()"))

    # 7. severity, in the About panel
    page.click("#reset-all"); settle(page)
    check("reset all: everything back, results back", hero(page) == h0 and page.is_disabled("#reset-all") and page.evaluate("JSON.stringify(ODDSLAB.cur.inp_ramp)") == json.dumps({"low": d["low"], "mid": d["mid"], "high": d["high"]}, separators=(",", ":")), page.evaluate("JSON.stringify(ODDSLAB.cur.inp_ramp)"))
    check("about: closed to begin with", page.is_hidden("#m-cn_minerals"))
    page.click('#d-cn_minerals button[aria-controls="m-cn_minerals"]')
    panel = page.inner_text("#m-cn_minerals")
    cn = DRIVERS["cn_minerals"]
    deadline = page.evaluate("fmtDate(%r)" % cn["deadline"])
    check("about: shows how we will know, the deadline, what it does and where the number comes from", all(t in panel for t in ("How we will know", "Deadline", deadline, "What it does here", "Where the number comes from", cn["basis"].capitalize())) and cn["note"][:50] in panel, panel[:200])
    links = page.evaluate("[...document.querySelectorAll('#m-cn_minerals .srcs a')].map(a => [a.textContent, a.href, a.target, a.rel])")
    check("about: a researched number lists its sources as links, with the day it was checked", len(links) == len(cn.get("src", [])) > 0 and all(l[1] == x["u"] and l[0] == x["t"] and l[2] == "_blank" and "noopener" in l[3] for l, x in zip(links, cn["src"])) and page.evaluate("fmtDate(%r)" % cn["checked"]) in page.inner_text("#m-cn_minerals .tagb"), links[:1])
    n_res = sum(1 for d in FILE["drivers"] if d["basis"] != "judgement")
    check("footer: says how many numbers are researched", ("%d of %d researched" % (n_res, len(DRIVERS))) in page.inner_text("#foot"), page.inner_text("#foot"))
    check("about: only events that have a size get a severity slider", page.locator("#m-cn_minerals [data-f='sev']").count() == 1 and page.locator("#d-cpo_volume [data-f='sev']").count() == 0 and page.locator("#d-cowos_ramp [data-f='sev']").count() == 0)
    typed(page, '#d-cn_minerals [data-f="p"]', 100)
    h_p = hero(page)
    slide(page, "#m-cn_minerals [data-f='sev']", 1)
    check(f"severity: the full scenario is worse than 0.3 of it ({h_p}% to {hero(page)}%)", hero(page) < h_p - 5 and "1 × the standard case" in page.inner_text("#m-cn_minerals .sevrow output") and "0.3 × as bad" in page.inner_text("#d-cn_minerals .drv-note"), (h_p, hero(page), page.inner_text("#d-cn_minerals .drv-note")))
    page.click("#reset-all"); settle(page)

    # 8. suppose
    page.click('#d-tw_blockade [data-sup="true"]'); settle(page)
    h_tw = hero(page)
    sit = page.evaluate("ODDSLAB.compute({n: ODDSLAB.N, seed: ODDSLAB.SEED, beliefs: {drivers: {}}, given: {tw_blockade: true}})")
    check(f"suppose: a blockade cuts the headline ({h0}% to {h_tw}%), as the engine says", h_tw == round(sit["built"]["mean"] * 100) and h_tw < h0 - 25, (h_tw, sit["built"]["mean"]))
    check("suppose: the situation and its chance are shown", page.is_visible("#situ") and "Taiwan blockade: happens" in page.inner_text("#situ-chips") and "a chance of 3%" in page.inner_text("#situ-t"), page.inner_text("#situ"))
    check("suppose: compared with your numbers without it", "below your numbers without this situation (%d%%)" % h0 in page.inner_text("#hero-d") and [t.strip() for t in page.locator("#hist-lg .lg").all_inner_texts()] == ["In this situation", "Without the situation"], page.inner_text("#hero-d"))
    note = page.inner_text("#d-cn_minerals .drv-note")
    m = re.search(r"In this situation its chance is (\d+)%", note)
    check("suppose: a linked event shows where it lands", m is not None and int(m.group(1)) == round(sit["drivers"]["cn_minerals"]["p"] * 100) and int(m.group(1)) > 60, note)
    check("suppose: a linked quantity shows where it lands", "In this situation its central case is" in page.inner_text("#d-capex_2027 .drv-note"), page.inner_text("#d-capex_2027 .drv-note"))
    check("suppose: unlinked rows say nothing (no noise shown as an effect)", page.inner_text("#d-jp_quake .drv-note").strip() == "" and page.inner_text("#d-inp_ramp .drv-note").strip() == "")
    check("suppose: the row and its button are marked", "supposed" in page.get_attribute("#d-tw_blockade", "class") and page.get_attribute('#d-tw_blockade [data-sup="true"]', "aria-pressed") == "true")
    clean_text(page, "supposed")
    page.evaluate("document.querySelector('#lab-grid').scrollIntoView()")
    shot(page, "odds_supposed.png")
    page.click("#situ-chips .xbtn"); settle(page)
    check("suppose: removing it restores the results", hero(page) == h0 and page.is_hidden("#situ") and page.get_attribute('#d-tw_blockade [data-sup="true"]', "aria-pressed") == "false")
    page.click('#d-cowos_ramp button[aria-controls="m-cowos_ramp"]'); page.click('#d-cowos_ramp [data-sup="low"]'); settle(page)
    check("suppose: a quantity at its low case, a 1-in-10 situation", "CoWoS packaging: at its low case or worse" in page.inner_text("#situ-chips") and re.search(r"a chance of (9|10|11)(\.\d)?%", page.inner_text("#situ-t")) is not None and hero(page) < h0, page.inner_text("#situ-t"))
    page.click('#d-cowos_ramp [data-sup="high"]'); settle(page)
    check("suppose: choosing the high case replaces the low case", page.locator("#situ-chips .chipx").count() == 1 and "high case or better" in page.inner_text("#situ-chips") and hero(page) >= h0)
    page.click("#situ-clear"); settle(page)
    typed(page, '#d-euv_halt [data-f="p"]', 0)
    page.click('#d-euv_halt [data-sup="true"]'); settle(page)
    check("suppose: something with no chance is called impossible, not shown as numbers", page.is_visible("#empty") and "cannot happen" in page.inner_text("#empty") and page.is_hidden("#hero") and page.is_hidden("#b-hist") and not errors, page.inner_text("#empty") if page.is_visible("#empty") else errors[:2])
    page.click("#reset-all"); settle(page)
    check("reset all: also drops what was supposed", hero(page) == h0 and page.is_hidden("#situ") and page.is_visible("#hero"))

    # 9. links: plain sentences in stories, five words, Fine-tune, add and delete, filter, impossible sets, the grid
    STORY_OF = lambda l: l.get("story") or DRIVERS[l["a"]]["story"]
    stories = [s for s in FILE["stories"]]
    check(f"stories: the links sit in {len(stories)} stories, folded to begin with", [t.strip() for t in page.locator("#stories details.story:not([hidden]) .st-name").all_inner_texts()] == [s["label"] for s in stories] and page.locator("#stories details.story[open]").count() == 0)
    metas = page.evaluate("[...document.querySelectorAll('#stories details.story:not([hidden]) .st-meta')].map(e => e.textContent)")
    want_meta = ["%d links" % sum(1 for l in FILE["links"] if STORY_OF(l) == s["id"]) for s in stories]
    check("stories: each says how many links it holds", metas == want_meta, (metas, want_meta))
    rows = page.locator("#stories .lk")
    check(f"links: one row for each of the {len(FILE['links'])}, with its reason", rows.count() == len(FILE["links"]) and all(l["why"] in page.text_content("#lk-%s--%s" % (l["a"], l["b"])) for l in FILE["links"]))
    check("grid: folded away, a square for every pair, a sign for every link", page.evaluate("document.querySelector('#grid-box').open") is False and page.locator("#grid rect.c").count() == len(DRIVERS) * (len(DRIVERS) - 1) and page.locator("#grid text.sg").count() == 2 * len(FILE["links"]), page.locator("#grid text.sg").count())
    TW = "#lk-tw_blockade--cn_minerals"
    want = page.evaluate("""(() => { const M = ODDSLAB.MODEL.drivers, a = M.find(d => d.id === 'tw_blockade'), b = M.find(d => d.id === 'cn_minerals');
        return [pct(ODDS.reading(a, b, 0.5).given), ODDSLAB.tgt(ODDS.reading(a, b, 0.5).given, true), ODDSLAB.tgt(ODDS.reading(b, a, 0.5).given, true)]; })()""")
    check("links: each reads as a sentence with the engine's numbers", page.text_content(TW + " .say") == "If China blockades Taiwan, the chance that China's mineral controls return goes from 30%% to %s." % want[0], page.text_content(TW + " .say"))
    pressed = lambda sel: page.text_content(sel + ' .steps [aria-pressed="true"]')
    check("links: the five words show each link's strength", pressed(TW) == "Much more likely" and pressed("#lk-tw_blockade--us_chip_rules") == "More likely" and pressed("#lk-tw_blockade--capex_2027") == "Lower" and page.text_content("#lk-tw_blockade--capex_2027 .steps button") == "Much lower", (pressed(TW), pressed("#lk-tw_blockade--us_chip_rules"), pressed("#lk-tw_blockade--capex_2027"), page.text_content("#lk-tw_blockade--capex_2027 .steps button")))
    check("links: a quantity reads with its unit", re.fullmatch(r"If China blockades Taiwan, hyperscaler spending plans go from 130% to \d+(\.\d)?% of 2026 plans\.", page.text_content("#lk-tw_blockade--capex_2027 .say") or "") is not None, page.text_content("#lk-tw_blockade--capex_2027 .say"))
    check("links: a quantity as the cause reads as its high case", (page.text_content("#lk-lab_revenue--openai_funding .say") or "").startswith("If lab revenue hits its high case, the chance that OpenAI raises $30B or more goes from 70% to "), page.text_content("#lk-lab_revenue--openai_funding .say"))
    page.click("#st-uschina > summary")
    check("stories: a click opens one", page.evaluate("document.querySelector('#st-uschina').open") is True and page.is_visible(TW + " .say"))
    typed(page, '#d-cn_minerals [data-f="p"]', 60)
    check("links: the sentences follow your chances", "from 60% to" in page.text_content(TW + " .say"), page.text_content(TW + " .say"))
    typed(page, '#d-cn_minerals [data-f="p"]', 30)
    page.click(TW + ' .steps [data-step="3"]'); settle(page)
    check("five words: 'more likely' sets +0.3 and is marked and counted", page.evaluate("ODDSLAB.links.find(l => l.a === 'tw_blockade' && l.b === 'cn_minerals').rho") == 0.3 and pressed(TW) == "More likely" and "changed" in page.get_attribute(TW, "class") and "Started at +0.5 (much more likely)" in page.inner_text(TW + " [data-v=note]") and page.inner_text("#dchanged") == "1 link changed" and "1 changed" in page.inner_text("#st-uschina .st-meta"), page.inner_text(TW + " [data-v=note]"))
    check("five words: the sentence follows", int(re.search(r"to (\d+)%", page.text_content(TW + " .say")).group(1)) < int(want[1]), page.text_content(TW + " .say"))
    page.click(TW + ' .steps [data-step="3"]'); settle(page)
    check("five words: choosing the word it already shows changes nothing", page.evaluate("ODDSLAB.links.find(l => l.a === 'tw_blockade' && l.b === 'cn_minerals').rho") == 0.3)
    check("fine-tune: closed to begin with", page.is_hidden(TW + " .lk-fine") and page.get_attribute(TW + ' [data-act="fine"]', "aria-expanded") == "false")
    page.click(TW + ' [data-act="fine"]')
    check("fine-tune: shows the exact strength and both readings", page.is_visible(TW + " .lk-fine") and page.input_value(TW + " [data-f=rho]") == "0.3" and "If China's mineral controls return, the chance of a Taiwan blockade goes from 3% to" in page.inner_text(TW + ' .lk-read[data-dir="ba"]'), page.inner_text(TW + " .lk-fine"))
    typed(page, TW + ' [data-f="rho"]', 0.8)
    check("fine-tune: a typed strength is stored, and the readings and slider follow", page.evaluate("ODDSLAB.links.find(l => l.a === 'tw_blockade' && l.b === 'cn_minerals').rho") == 0.8 and int(page.input_value(TW + ' .lk-read[data-dir="ab"] [data-f="target"]')) > 90 and abs(float(page.input_value(TW + " [data-f=rhos]")) - 0.8) < 1e-9 and pressed(TW) == "Much more likely")
    check("change a link: the grid marks it, and the results compare with the starting numbers", page.locator("#grid circle.dot").count() == 2 and page.is_visible("#hero-d") and "the starting numbers" in page.inner_text("#hero-d"))
    page.click('#d-tw_blockade [data-sup="true"]'); settle(page)
    note = page.inner_text("#d-cn_minerals .drv-note")
    m = re.search(r"In this situation its chance is (\d+)%", note)
    check("change a link: the futures use it (supposing a blockade now lifts the mineral controls above 90%)", m is not None and int(m.group(1)) > 90, note)
    page.click("#situ-clear"); settle(page)
    US = "#lk-tw_blockade--us_chip_rules"
    page.click(US + ' [data-act="fine"]')
    typed(page, US + ' .lk-read[data-dir="ab"] [data-f="target"]', 40)
    rho = page.evaluate("ODDSLAB.links.find(l => l.b === 'us_chip_rules' && l.a === 'tw_blockade').rho")
    expect = page.evaluate("(() => { const M = ODDSLAB.MODEL.drivers, a = M.find(d => d.id === 'tw_blockade'), b = M.find(d => d.id === 'us_chip_rules'); return Math.round(ODDS.rhoForReading(a, b, 0.4).rho * 100) / 100; })()")
    check(f"aim a link: 'if the first happens, 40%' sets the strength to {rho}", rho == expect and 0.05 < rho < 0.9 and page.input_value(US + ' .lk-read[data-dir="ab"] [data-f="target"]') == "40" and page.input_value(US + " [data-f=rho]") == str(rho) and "to 40%" in page.text_content(US + " .say"), (rho, expect))
    # a rare event cannot become a 90% one just because a commoner one happens: at most P(blockade) / P(tighter rules)
    cap = 100 * DRIVERS["tw_blockade"]["p"] / DRIVERS["us_chip_rules"]["p"]
    typed(page, US + ' .lk-read[data-dir="ba"] [data-f="target"]', 90)
    note = page.inner_text(US + " [data-v=note]")
    m = re.search(r"can only take Taiwan blockade as far as ([\d.]+)%", note)
    check("aim a link: an unreachable target says how far a link can go", page.evaluate("ODDSLAB.links.find(l => l.b === 'us_chip_rules' && l.a === 'tw_blockade').rho") == 0.95 and m is not None and cap * 0.75 < float(m.group(1)) <= cap + 0.05, (note, cap))
    CT = "#lk-cn_minerals--chip_tariff"
    page.click(CT + ' .steps [data-step="2"]'); settle(page)
    check("no link: a starting link is kept as removed, with a way back", pressed(CT) == "No link" and "off" in page.get_attribute(CT, "class") and "Removed. It started at +0.3" in page.inner_text(CT + " [data-v=note]") and page.evaluate("ODDSLAB.links.find(l => l.a === 'cn_minerals' && l.b === 'chip_tariff').rho") == 0)
    check("no link: no longer counted or drawn", "33 links in all" in page.inner_text("#lk-count") and page.locator("#grid text.sg").count() == 2 * (len(FILE["links"]) - 1), page.inner_text("#lk-count"))
    page.click(CT + " [data-v=note] button"); settle(page)
    check("reset one link: back at its starting strength", page.evaluate("ODDSLAB.links.find(l => l.a === 'cn_minerals' && l.b === 'chip_tariff').rho") == 0.3 and pressed(CT) == "More likely" and "34 links in all" in page.inner_text("#lk-count") and "changed" not in page.get_attribute(CT, "class"))
    page.select_option("#lk-a", "jp_quake"); page.select_option("#lk-b", "tglass_ramp")
    check("add a link: offered for a pair with none", page.inner_text("#lk-add button") == "Add link" and page.is_enabled("#lk-add button"))
    page.click("#lk-add button"); settle(page)
    NEW = "#lk-jp_quake--tglass_ramp"
    check("add a link: a new row at the top of its first driver's story, at no link until given a strength", page.locator(NEW).count() == 1 and page.locator("#st-chips .lk").first.get_attribute("id") == NEW[1:] and page.evaluate("document.querySelector('#st-chips').open") is True and pressed(NEW) == "No link" and "Pick how strong" in page.inner_text(NEW + " [data-v=note]") and page.evaluate("document.activeElement === document.querySelector('%s .steps [aria-pressed=true]')" % NEW))
    page.click(NEW + ' .steps [data-step="1"]'); settle(page)
    page.click(NEW + ' [data-act="fine"]')
    check("add a link: once set it counts, is drawn, and reads both ways", "35 links in all" in page.inner_text("#lk-count") and page.locator("#grid text.sg").count() == 2 * len(FILE["links"]) + 2 and page.text_content(NEW + " .say").startswith("If an earthquake hits Japan's materials makers, T-glass cloth goes from 99% to ") and "If T-glass cloth hits its high case, the chance of an earthquake" in page.inner_text(NEW + ' .lk-read[data-dir="ba"]'), page.text_content(NEW + " .say"))
    page.select_option("#lk-a", "tw_blockade"); page.select_option("#lk-b", "cn_minerals")
    check("add a link: an existing pair is offered as 'Show this link'", page.inner_text("#lk-add button") == "Show this link")
    page.click(NEW + ' [data-act="delete"]'); settle(page)
    check("delete an added link: the row goes", page.locator(NEW).count() == 0 and "34 links in all" in page.inner_text("#lk-count"))
    page.select_option("#lk-filter", "tw_blockade")
    n_tw = sum(1 for l in FILE["links"] if "tw_blockade" in (l["a"], l["b"]))
    page.select_option("#lk-filter", "capex_2027")
    n_cx = sum(1 for l in FILE["links"] if "capex_2027" in (l["a"], l["b"]))
    check(f"filter: only the {n_cx} links of one driver, in every story that has them, opened", page.locator("#stories .lk:visible").count() == n_cx and page.is_hidden("#lk-empty") and page.evaluate("[...document.querySelectorAll('#stories details.story:not([hidden])')].map(e => e.id + (e.open ? '+' : ''))") == ["st-uschina+", "st-demand+"], page.evaluate("[...document.querySelectorAll('#stories details.story:not([hidden])')].map(e => e.id + (e.open ? '+' : ''))"))
    page.select_option("#lk-filter", "euv_halt")
    check("filter: a driver with no links says so", page.locator("#stories .lk:visible").count() == 0 and page.is_visible("#lk-empty"))
    page.select_option("#lk-filter", "")
    # each driver's own links, as tags on its row
    chips = page.locator("#d-tw_blockade .lchip[data-k]")
    check(f"driver links: Taiwan blockade's row shows its {n_tw} links as tags", chips.count() == n_tw and "Moves with" in page.inner_text("#d-tw_blockade .drv-links .dl-k") and page.inner_text("#d-euv_halt .drv-links .dl-k") == "No links yet")
    first = page.locator('#d-tw_blockade .lchip[data-k="cn_minerals|tw_blockade"]')
    check("driver links: a tag shows the direction and strength, and marks a change", first.locator(".ar").inner_text() == "↑↑" and "pos" in first.locator(".ar").get_attribute("class") and "changed" in first.get_attribute("class") and page.locator('#d-tw_blockade .lchip[data-k="capex_2027|tw_blockade"] .ar').inner_text() == "↓")
    first.click(); page.wait_for_timeout(150)
    box = "#d-tw_blockade .lk-in"
    check("driver links: a tag opens the link under the row, as the same sentence", page.is_visible(box) and first.get_attribute("aria-expanded") == "true" and page.text_content(box + " .say") == page.text_content(TW + " .say") and page.text_content(box + ' .steps [aria-pressed="true"]') == "Much more likely",
          (page.is_visible(box), first.get_attribute("aria-expanded"), page.text_content(box + " .say"), page.text_content(TW + " .say"), page.text_content(box + ' .steps [aria-pressed="true"]')))
    page.click(box + ' .steps [data-step="0"]'); settle(page)
    check("driver links: a word chosen there changes the link everywhere", page.evaluate("ODDSLAB.links.find(l => l.a === 'tw_blockade' && l.b === 'cn_minerals').rho") == -0.6 and pressed(TW) == "Much less likely" and first.locator(".ar").inner_text() == "↓↓" and "neg" in first.locator(".ar").get_attribute("class") and page.locator('#d-cn_minerals .lchip[data-k="cn_minerals|tw_blockade"] .ar').inner_text() == "↓↓")
    page.click(box + ' [data-act="reset"]'); settle(page)
    check("driver links: Reset there puts it back", page.evaluate("ODDSLAB.links.find(l => l.a === 'tw_blockade' && l.b === 'cn_minerals').rho") == 0.5 and page.is_hidden(box + ' [data-act="reset"]') and "changed" not in first.get_attribute("class"))
    page.click(box + " .xbtn")
    check("driver links: the panel closes", page.is_hidden(box) and first.get_attribute("aria-expanded") == "false")
    page.click("#d-euv_halt .lchip.add")
    check("driver links: 'Add a link' asks what to link it with", page.is_visible("#d-euv_halt .lk-in select") and page.evaluate("document.activeElement === document.querySelector('#d-euv_halt .lk-in select')"))
    page.select_option("#d-euv_halt .lk-in select", "foundry_ramp"); page.click('#d-euv_halt .lk-in button[type="submit"]'); settle(page)
    E = "#lk-euv_halt--foundry_ramp"
    check("driver links: a link added from a row reads from that row's driver", page.locator(E).count() == 1 and page.text_content("#d-euv_halt .lk-in .say") == "If EUV supply stops, leading-edge wafers stay at 105% of plan." and page.locator("#d-euv_halt .lchip[data-k]").count() == 1, page.text_content("#d-euv_halt .lk-in .say"))
    page.click('#d-euv_halt .lk-in .steps [data-step="0"]'); settle(page)
    check("driver links: once given a strength it shows on both rows and in its story", page.evaluate("ODDSLAB.links.find(l => l.a === 'euv_halt').rho") == -0.6 and "EUV supply stops" in page.inner_text("#d-foundry_ramp .drv-links") and pressed(E) == "Much lower" and page.locator("#st-chips " + E).count() == 1)
    page.click('#d-euv_halt .lk-in [data-act="delete"]'); settle(page)
    check("driver links: deleting it there removes it everywhere", page.locator(E).count() == 0 and page.is_hidden("#d-euv_halt .lk-in") and "EUV supply stops" not in page.inner_text("#d-foundry_ramp .drv-links") and "34 links in all" in page.inner_text("#lk-count"))
    for key, v in (("digestion--capex_2027", "0.95"), ("lab_revenue--capex_2027", "0.95"), ("lab_revenue--digestion", "-0.95")):
        page.evaluate("document.querySelector('#lk-%s').closest('details').open = true" % key)
        if page.is_hidden(f"#lk-{key} .lk-fine"):
            page.click(f'#lk-{key} [data-act="fine"]')
        typed(page, f"#lk-{key} [data-f=rho]", v)
    check("impossible links: a warning says what was adjusted", page.is_visible("#lk-warn") and "The biggest change was to" in page.inner_text("#lk-warn-t") and page.is_visible("#hero-adj"), page.inner_text("#lk-warn-t") if page.is_visible("#lk-warn") else "")
    check("impossible links: adjusted rows say what was used", page.locator("#stories [data-v=note]", has_text="so that all the links fit together").count() >= 1)
    check("impossible links: the results are still worked out", re.fullmatch(r"\d+%", page.inner_text("#hero-v")) is not None and not errors)
    # the grid: mouse, keyboard
    page.click("#grid-box > summary")
    page.evaluate("document.querySelector('#grid').scrollIntoView({block: 'center'})")
    cell = page.locator('#grid rect.c[data-i="0"][data-j="4"]')            # Taiwan blockade x China's mineral controls
    box_ = cell.bounding_box(); page.mouse.move(box_["x"] + 9, box_["y"] + 9)
    check("grid: hovering a square names the pair and its link", page.is_visible("#tip") and "Taiwan blockade and China's mineral controls return" in page.inner_text("#tip"), page.inner_text("#tip") if page.is_visible("#tip") else "")
    cell.click(); page.wait_for_timeout(700)
    check("grid: clicking a linked square opens its row at Fine-tune", page.evaluate("document.activeElement === document.querySelector('%s [data-f=rho]')" % TW) and "flash" in page.get_attribute(TW, "class") and page.is_visible(TW + " .lk-fine"))
    page.locator('#grid rect.c[data-i="8"][data-j="0"]').click(); page.wait_for_timeout(500)          # EUV x Taiwan: no link
    check("grid: clicking an empty square sets up the add form", page.input_value("#lk-a") == "euv_halt" and page.input_value("#lk-b") == "tw_blockade" and page.inner_text("#lk-add button") == "Add link")
    page.focus("#grid"); page.keyboard.press("ArrowRight")
    check("grid: arrow keys move across the pairs", page.is_visible("#tip") and " and " in page.inner_text("#tip .tt"))
    page.keyboard.press("Escape")
    page.click("#reset-all"); settle(page)
    check("reset all: every link back to its start", page.locator("#stories .lk.changed").count() == 0 and page.is_hidden("#lk-warn") and "34 links in all" in page.inner_text("#lk-count") and hero(page) == h0 and page.locator("#grid circle.dot").count() == 0 and page.locator(".lchip.changed").count() == 0)
    clean_text(page, "links")

    # 9b. how strongly things move together: every link at once
    page.wait_for_function(STRIP_DONE, timeout=30000)
    cols = page.locator("#ms-cols .ms-col")
    vals = page.evaluate("[...document.querySelectorAll('#ms-cols .ms-v')].map(e => e.textContent)")
    lite = page.evaluate("""[0, 0.5, 1, 1.5].map(k => ODDSLAB.compute({n: ODDSLAB.N, seed: ODDSLAB.SEED, lite: true, given: {},
        beliefs: {drivers: {}, corr: ODDSLAB.links.map(l => [l.a, l.b, Math.max(-0.95, Math.min(0.95, Math.round(l.rho * k * 1000) / 1000))])}}))""")
    check("master: four settings, each with its chance of a bad year from the engine", cols.count() == 4 and vals == [page.evaluate("pct(%r)" % x["below"]["0.8"]) for x in lite] and page.get_attribute('#ms-cols .ms-col[data-k="1"]', "aria-pressed") == "true", vals)
    check("master: 'as set' matches the results, and links make a bad year likelier", vals[2] == page.inner_text("#t-below") and lite[2]["below"]["0.8"] > lite[0]["below"]["0.8"] * 1.2 and "if nothing were linked" in page.inner_text("#ms-cap"), page.inner_text("#ms-cap"))
    page.locator('#ms-cols .ms-col[data-k="0"]').hover()
    check("master: hovering a setting explains it", page.is_visible("#tip") and "no links at all" in page.inner_text("#tip") and "Average built" in page.inner_text("#tip"), page.inner_text("#tip") if page.is_visible("#tip") else "")
    page.mouse.move(5, 5)
    page.click('#ms-cols .ms-col[data-k="0"]'); settle(page)
    check("master: 'none' unlinks everything for the results", page.evaluate("ODDSLAB.scale") == 0 and hero(page) == round(lite[0]["mean"] * 100) and page.get_attribute('#ms-cols .ms-col[data-k="0"]', "aria-pressed") == "true" and page.is_visible("#hero-scale") and "no links at all" in page.inner_text("#hero-scale") and page.inner_text("#dchanged") == "No links at all" and page.is_enabled("#reset-all") and "The results above use no links at all" in page.inner_text("#ms-cap"), (hero(page), lite[0]["mean"], page.inner_text("#dchanged")))
    check("master: your links stay as you set them", page.evaluate("ODDSLAB.links.find(l => l.a === 'tw_blockade' && l.b === 'cn_minerals').rho") == 0.5 and page.text_content(TW + " .say") == "If China blockades Taiwan, the chance that China's mineral controls return goes from 30%% to %s." % want[0])
    page.click('#d-tw_blockade [data-sup="true"]'); settle(page)
    check("master: with no links, supposing one thing moves nothing else", page.inner_text("#d-cn_minerals .drv-note").strip() == "", page.inner_text("#d-cn_minerals .drv-note"))
    page.click("#situ-clear"); settle(page)
    page.click('#ms-cols .ms-col[data-k="1.5"]'); settle(page); page.wait_for_function(STRIP_DONE, timeout=30000)
    check("master: 'stronger' says when links that strong cannot all hold, without the warning meant for your own links", page.evaluate("ODDSLAB.scale") == 1.5 and "cannot all be true at once" in page.inner_text("#ms-cap") and page.is_hidden("#lk-warn") and page.is_hidden("#hero-adj") and hero(page) == round(lite[3]["mean"] * 100), page.inner_text("#ms-cap"))
    page.select_option("#t-thr", "0.7")
    check("master: follows the threshold chosen in the results", page.inner_text("#ms-thr") == "70%" and page.locator("#ms-cols .ms-v").first.inner_text() == page.evaluate("pct(%r)" % lite[0]["below"]["0.7"]))
    page.select_option("#t-thr", "0.8")
    page.click("#reset-all"); settle(page)
    check("reset all: links back to 'as set'", page.evaluate("ODDSLAB.scale") == 1 and page.get_attribute('#ms-cols .ms-col[data-k="1"]', "aria-pressed") == "true" and page.is_hidden("#hero-scale") and hero(page) == h0 and page.is_disabled("#reset-all"))
    clean_text(page, "master")
    page.evaluate("document.querySelector('#links').scrollIntoView()")
    shot(page, "odds_links.png")

    # 9c. market odds: Polymarket prices beside the drivers (the build embedded the sample written in main())
    MKD = {d["id"]: d.get("markets", []) for d in FILE["drivers"]}
    n_mk = sum(1 for k in ("tw_blockade", "gulf_persist", "gulf_dc_hit", "openai_funding") if MKD.get(k))
    check("markets: the line above the drivers says how many have market odds and how old they are", page.inner_text("#mkt-age") == "Market odds on %d drivers, read 2 hours ago; some are out of date." % n_mk, page.inner_text("#mkt-age"))
    check("markets: only listed markets with a sensible price reach the page", sorted(page.evaluate("Object.keys(ODDSLAB.markets.items)")) == sorted(k for k in MARKET_SAMPLE["items"] if k not in ("polymarket:999", "polymarket:1811266")), page.evaluate("Object.keys(ODDSLAB.markets.items)"))
    tw = page.locator("#d-tw_blockade .drv-mkt .mchip")
    close = MKD["tw_blockade"][0]
    check("markets: a driver shows each market with the price of the side it names", tw.count() == 2 and close["label"] in tw.nth(0).inner_text() and page.evaluate("pct(0.0335)") in tw.nth(0).inner_text()
          and "close" in tw.nth(0).get_attribute("class") and "related" in tw.nth(1).get_attribute("class") and tw.nth(0).get_attribute("href") == close["url"] and tw.nth(0).get_attribute("target") == "_blank" and "noopener" in tw.nth(0).get_attribute("rel"),
          [tw.nth(i).inner_text() for i in range(tw.count())])
    check("markets: a market priced on its No side shows the No price", page.evaluate("pct(1 - 0.205)") in page.inner_text("#d-gulf_persist .drv-mkt .mchip"), page.inner_text("#d-gulf_persist .drv-mkt"))
    check("markets: a price read days ago is marked as old", "stale" in page.get_attribute("#d-gulf_dc_hit .drv-mkt .mchip", "class") and "old" in page.inner_text("#d-gulf_dc_hit .drv-mkt .mchip").lower())
    check("markets: drivers without markets show no market line", page.is_hidden("#d-euv_halt .drv-mkt") and page.locator("#d-cn_minerals .drv-mkt .mchip").count() == 0)
    tw.nth(1).hover()
    tip = page.inner_text("#tip") if page.is_visible("#tip") else ""
    check("markets: hovering a market explains it", "Polymarket" in tip and "This week:" in tip and "Traded:" in tip and "Read:" in tip and MKD["tw_blockade"][1]["differs"][:30] in tip, tip)
    page.mouse.move(5, 5)
    use = page.locator('#d-tw_blockade [data-act="use-mkt"]')
    check("markets: a close fit offers its price with one click", use.count() == 1 and use.inner_text() == "Use " + page.evaluate("pct(0.0335)"))
    use.click(); settle(page)
    check("markets: 'Use' sets the chance to the market's, and the results follow", page.evaluate("ODDSLAB.cur.tw_blockade.p") == 0.0335 and page.input_value('#d-tw_blockade [data-f="p"]') == page.evaluate("num(3.35)") and "changed" in page.get_attribute("#d-tw_blockade", "class")
          and page.locator('#d-tw_blockade [data-act="use-mkt"]').count() == 0 and page.is_visible("#hero-d"), page.input_value('#d-tw_blockade [data-f="p"]'))
    page.click("#d-tw_blockade .drv-note button"); settle(page)
    check("markets: after a reset the offer comes back", page.locator('#d-tw_blockade [data-act="use-mkt"]').count() == 1 and hero(page) == h0)
    if page.is_hidden("#m-tw_blockade"):
        page.click('#d-tw_blockade button[aria-controls="m-tw_blockade"]')
    about = page.inner_text('#m-tw_blockade [data-v="mkt-dd"]')
    check("markets: the About panel quotes each market's own question, how it differs, its size and age", MARKET_SAMPLE["items"]["polymarket:2382819"]["question"] in about and close["differs"][:40] in about and "$406k traded" in about and "read 2 hours ago" in about
          and page.locator('#m-tw_blockade [data-v="mkt-dd"] a').first.get_attribute("href") == close["url"], about[:300])
    newer = json.loads(json.dumps(MARKET_SAMPLE)); newer["fetched"] = iso_ago(0); newer["items"]["polymarket:2382819"].update(yes=0.05, at=iso_ago(0))
    json.dump(newer, open(os.path.join(SITE, "data", "markets.json"), "w"))
    got = page.evaluate("ODDSLAB.refreshMarkets()")
    check("markets: newer prices published by the refresh replace the built-in ones", got is True and page.evaluate("pct(0.05)") in page.inner_text("#d-tw_blockade .drv-mkt .mchip") and "read just now" in page.inner_text("#mkt-age"), (got, page.inner_text("#d-tw_blockade .drv-mkt")))
    older = json.loads(json.dumps(MARKET_SAMPLE)); older["fetched"] = iso_ago(30); older["items"]["polymarket:2382819"].update(yes=0.9)
    json.dump(older, open(os.path.join(SITE, "data", "markets.json"), "w"))
    check("markets: an older file never replaces newer prices", page.evaluate("ODDSLAB.refreshMarkets()") is False and page.evaluate("pct(0.05)") in page.inner_text("#d-tw_blockade .drv-mkt .mchip"))
    os.remove(os.path.join(SITE, "data", "markets.json"))
    clean_text(page, "markets")

    # 10. jumping from a result to the number behind it
    page.evaluate("document.querySelector('#lab-grid').scrollIntoView(); document.querySelector('#results').scrollTop = 99999")
    page.locator("#mat button.row").nth(1).click(); page.wait_for_timeout(900)
    target = page.evaluate("(() => { const r = document.querySelector('.drv.flash'); if (!r) return null; const b = r.getBoundingClientRect(); return [r.dataset.id, b.top >= 0 && b.bottom <= innerHeight]; })()")
    check("what matters: clicking a row goes to its number", target is not None and target[1] is True, target)
    check("no page errors on the desktop run", not errors, errors[:3])
    t = page.evaluate("""async () => { const t0 = performance.now(); const f = document.querySelector('#d-gulf_dc_hit [data-f="p"]'); f.value = 33; f.dispatchEvent(new Event('change', {bubbles: true}));
        await new Promise(ok => { const tick = () => (!ODDSLAB.busy && ODDSLAB.cur.gulf_dc_hit.p === 0.33 && ODDSLAB.res.refKind === 'start') ? ok() : setTimeout(tick, 5); setTimeout(tick, 70); }); return performance.now() - t0; }""")
    print("INFO one change, from typing to new results on screen: %d ms" % t)
    ctx.close()

    # 11. a browser without background workers still works, with the same numbers
    ctx, page, errors = new_page(browser, init="delete window.Worker;")
    page.goto(BASE + "odds/"); settle(page)
    check("no worker: the page still works and gives the same headline", page.evaluate("ODDSLAB.usingWorker()") is False and hero(page) == h0 and not errors, (hero(page), errors[:2]))
    ctx.close()

    # 12. the other two pages lead here
    ctx, page, errors = new_page(browser)
    page.goto(BASE); page.wait_for_selector("#nav-odds")
    check("home: third tab points to The Odds", page.locator(".atlases a").count() == 3 and page.evaluate("document.querySelector('#nav-odds').href") == BASE + "odds/" and len(page.inner_text("#nav-odds-c")) > 20)
    page.click("#nav-odds"); page.wait_for_url(BASE + "odds/"); settle(page)
    check("home: one click opens The Odds", page.inner_text("h1").strip().lower() == "the odds" and hero(page) == h0)
    page.click("#nav-atlas"); page.wait_for_url(BASE + "money/"); page.wait_for_selector("#nav-odds")
    check("The Money: third tab points to The Odds", page.evaluate("document.querySelector('#nav-odds').href") == BASE + "odds/" and page.get_attribute("#nav-atlas", "aria-current") == "page")
    ctx.close()

    # 13. phones
    for scheme in ("light", "dark"):
        ctx, page, errors = new_page(browser, scheme=scheme, width=390, height=844, touch=True)
        page.goto(BASE + "odds/"); settle(page)
        check(f"phone {scheme}: no sideways scroll", page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), page.evaluate("[document.documentElement.scrollWidth, window.innerWidth]"))
        check(f"phone {scheme}: switch fits on one line each", page.evaluate("[...document.querySelectorAll('.atlases .at-t')].every(e => e.getBoundingClientRect().height < 24)"))
        check(f"phone {scheme}: results come before the numbers", page.evaluate("document.querySelector('#results').getBoundingClientRect().top < document.querySelector('#drivers').getBoundingClientRect().top"))
        page.evaluate("document.querySelector('#hero').scrollIntoView({block: 'center'})"); page.wait_for_timeout(300)
        check(f"phone {scheme}: no headline bar while the headline is on screen", page.is_hidden("#mini"))
        page.evaluate("document.querySelector('#d-cowos_ramp').scrollIntoView({block: 'center'})"); page.wait_for_timeout(400)
        check(f"phone {scheme}: the headline follows you down the list", page.is_visible("#mini") and "%d%% of plan" % h0 in page.inner_text("#mini"), page.inner_text("#mini") if page.is_visible("#mini") else "")
        typed(page, '#d-cowos_ramp [data-f="mid"]', 80)
        check(f"phone {scheme}: the bar updates as numbers change", int(re.search(r"(\d+)% of plan", page.inner_text("#mini")).group(1)) < h0, page.inner_text("#mini"))
        sizes = page.evaluate("[...document.querySelectorAll('#d-cowos_ramp .nf, #d-cowos_ramp .ghost, #d-tw_blockade .ghost, #d-tw_blockade .sl')].map(e => e.getBoundingClientRect().height).filter(v => v > 0)")
        check(f"phone {scheme}: fields, sliders and buttons are big enough to tap", len(sizes) >= 7 and min(sizes) >= 36, sizes)
        clean_text(page, f"phone {scheme}")
        shot(page, f"odds_phone_{scheme}.png")
        check(f"phone {scheme}: no page errors", not errors, errors[:3])
        ctx.close()


def main():
    global BASE, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", default=None, help="folder for screenshots")
    a = ap.parse_args()
    if a.shots:
        OUT = os.path.abspath(a.shots); os.makedirs(OUT, exist_ok=True)
    with tempfile.TemporaryDirectory() as site:
        global SITE
        SITE = site
        sample = os.path.join(site, "markets-sample.json")
        json.dump(MARKET_SAMPLE, open(sample, "w"))
        subprocess.run([sys.executable, os.path.join(ROOT, "src", "build.py"), "--target", "github", "--quotes", os.devnull + ".none", "--markets", sample, "--out", site],
                       check=True, env=dict(os.environ, GITHUB_SHA="abcdef1234567890"), stdout=subprocess.DEVNULL)
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=site))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        BASE = "http://127.0.0.1:%d/" % srv.server_address[1]
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                try:
                    run_checks(browser)
                finally:
                    browser.close()
        finally:
            srv.shutdown()
    bad = [r for r in RESULTS if not r[1]]
    print("\n%d checks, %d failed" % (len(RESULTS), len(bad)))
    for b in bad:
        print("  FAILED:", b[0], b[2])
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
