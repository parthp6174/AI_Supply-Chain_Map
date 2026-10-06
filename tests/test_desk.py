#!/usr/bin/env python3
"""Browser tests for the Update desk (src/common/desk.js) against a fake GitHub API.

    pip install playwright && playwright install chromium
    python tests/test_desk.py                 # builds the site into a temp folder, serves it, runs every check
    python tests/test_desk.py --shots shots   # also saves screenshots (light, dark, phone) into shots/

Nothing here touches GitHub or the real site: api.github.com is answered by FakeGitHub below, and prices and
headlines come from fixtures made from the repo's own data. Exit code 1 if any check fails.

Covers: what visitors see; the news radar (grouping, hide, new, unsafe text and links); suggesting on GitHub;
connecting and disconnecting a key; turning the schedule on; Refresh now; publishing, editing and deleting an
entry with page changes (including a conflicting write); a paused workflow; build warnings; missing
permissions; an expired key; a cached page catching up with a newer build; the switch between the pages;
The Money bar; phones. The third page, The Odds, has its own tests in tests/test_odds.py.
"""
import argparse, base64, datetime as dt, functools, hashlib, http.server, json, os, re, subprocess, sys, tempfile, threading, time, urllib.parse

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "supply")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
import supply_data as D      # noqa: E402
import fetch_news as FN      # noqa: E402

TOKEN = "github_pat_" + "A" * 82
REPO = "/repos/Parthp6174/AI_Supply-Chain_Map"
REV = "abcdef123456"
DEV_TEXT = open(os.path.join(ROOT, "data", "developments.json"), encoding="utf-8").read()
DEV = json.loads(DEV_TEXT)
WF_TEXT = open(os.path.join(ROOT, ".github", "workflows", "pages.yml"), encoding="utf-8").read()
N_ENTRIES, N_UPCOMING = len(DEV["entries"]), len(DEV["upcoming"])
LOGGED = DEV["entries"][0]                     # a headline with this title must show as "In the log"
NOW = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
BASE = OUT = None                              # set in main()


def iso(d): return d.strftime("%Y-%m-%dT%H:%M:%SZ")
def b64(s): return base64.b64encode(s.encode()).decode()
def unb64(s): return base64.b64decode(s).decode()


# ---------------------------------------------------------------- fixtures
def quotes(ts, bump):
    out = {}
    for k, q in D.Q.items():
        out[k] = dict(sym=k.upper(), px=round(q["px"] * bump, 2), prev=q["px"], chg=round((bump - 1) * 100, 2), date=NOW.strftime("%Y-%m-%d"),
                      cur=q.get("cur", "$"), tgt=q.get("tgt"), n=q.get("n"), rating=q.get("rating"), next=q.get("next"),
                      psrc="yahoo", tsrc="yahoo" if q.get("tgt") else None)
    return dict(updated=iso(ts), pricesUpdated=iso(ts), targetsUpdated=iso(NOW - dt.timedelta(hours=9)), source="Yahoo Finance via yfinance",
                quotes=out, report=dict(prices_ok=len(out) - 2, prices_failed=["X", "Y"], targets_ok=80, targets_failed=[]))


def news(refreshed):
    topics = json.load(open(os.path.join(ROOT, "data", "news_queries.json")))["topics"]
    assert any(t["id"] == "memory" and "hbm" in t["links"].get("nodes", []) for t in topics), "tests expect a 'memory' topic linked to node 'hbm'"
    titles = [("taiwan", "PLA launches fresh drills around Taiwan as TSMC flags no disruption"), ("memory", "SK hynix says HBM4 sold out through 2027"),
              ("gulf", "Ras Laffan helium restart slips to November"), ("minerals", "China extends gallium licence pause to May 2027"),
              ("packaging", "TSMC adds CoWoS capacity in Chiayi ahead of Rubin ramp"), ("powergear", "GE Vernova gas turbine backlog tops 100 GW"),
              ("investments", "Microsoft unveils $25 billion AI campus in Wisconsin"), ("credit", "Oracle prices $18 billion bond to fund AI data centers"),
              ("labs", "Anthropic signs multi-gigawatt TPU deal"), ("optics", "Lumentum warns indium phosphide laser supply stays tight"),
              ("chips", "Nvidia says Rubin shipments start on schedule"), ("grid", "PJM capacity auction clears at record price on data center demand"),
              ("china", "Huawei Ascend 950 enters mass production"), ("capex", "Meta raises 2026 capex guidance again"),
              ("tools", "ASML books record EUV orders"), ("servers", "Foxconn AI server revenue doubles"), ("chiprules", "US tightens chip export rules for Malaysia and Thailand")]
    items = []
    for i, (tid, t) in enumerate(titles):
        items.append(dict(id=FN.item_id(t), t=t, src=["Reuters", "Bloomberg", "Nikkei Asia", "Financial Times"][i % 4], srcUrl="https://www.reuters.com",
                          u="https://news.google.com/rss/articles/CBMi" + hashlib.md5(t.encode()).hexdigest() + "?oc=5", d=iso(NOW - dt.timedelta(hours=2 + i * 5)), topics=[tid]))
    for it in items:                             # one story reported by four outlets, one of them with an unsafe link
        if it["t"].startswith("Oracle prices"):
            it.update(ids=[it["id"], "aaaaaaaaaaa1", "aaaaaaaaaaa2", "aaaaaaaaaaa3"], n=4, first=iso(NOW - dt.timedelta(days=2)),
                      more=[{"src": "Bloomberg", "u": "https://news.google.com/rss/articles/more1"}, {"src": "CNBC", "u": "javascript:alert(1)"}])
    items.append(dict(id="xss0000000001", t='<img src=x onerror="window.__xss=1">Bad headline', src="Evil", srcUrl="", u="javascript:window.__xss=2",
                      d=iso(NOW - dt.timedelta(hours=1)), topics=["chips"]))
    items.append(dict(id=FN.item_id(LOGGED["title"]), t=LOGGED["title"], src="Already", srcUrl="", u="https://example.com/already-logged",
                      d=iso(NOW - dt.timedelta(days=2)), topics=["gulf"]))
    updated = NOW - dt.timedelta(hours=1)
    if refreshed:
        t = "Brand new: Samsung wins Nvidia HBM4 qualification"
        items.append(dict(id=FN.item_id(t), t=t, src="Reuters", srcUrl="", u="https://news.google.com/rss/articles/CBMinew?oc=5", d=iso(NOW + dt.timedelta(minutes=1)), topics=["memory"]))
        updated = NOW + dt.timedelta(minutes=3)
    items.sort(key=lambda r: r["d"], reverse=True)
    return dict(updated=iso(updated), source="Google News", days=10, topics=[dict(id=t["id"], label=t["label"], links=t["links"]) for t in topics],
                items=items, report=dict(queries=36, ok=36, failed=[], items=len(items)))


FIX = {}


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


# ---------------------------------------------------------------- fake GitHub
class FakeGitHub:
    """Answers the handful of api.github.com calls the desk makes and records what was written."""

    def __init__(self, schedule_runs=None, wf_state="active", wf_by="claude", perms=("contents", "actions", "workflows")):
        self.dev_text, self.wf_text = DEV_TEXT, WF_TEXT
        self.dev_sha, self.wf_sha = "devsha0", "wfsha0"
        self.runs, self.next_id, self.polls = [], 5000, {}
        self.schedule_runs = schedule_runs or []
        self.wf_state, self.wf_by, self.perms = wf_state, wf_by, perms
        self.calls, self.puts, self.dispatches, self.unknown, self.enabled = [], [], [], [], 0
        self.refreshed = False
        self.conflict_once = False

    def run_obj(self, r):
        n = self.polls.get(r["id"], 0)
        status, concl = ("queued", None) if n < 1 else ("in_progress", None) if n < 5 else ("completed", "success")
        return dict(id=r["id"], event=r["event"], status=status, conclusion=concl, head_sha=r["head_sha"], created_at=r["created_at"],
                    html_url="https://github.com/Parthp6174/AI_Supply-Chain_Map/actions/runs/%d" % r["id"])

    def new_run(self, event, head_sha):
        self.next_id += 1
        self.runs.append(dict(id=self.next_id, event=event, head_sha=head_sha, created_at=iso(dt.datetime.now(dt.timezone.utc))))

    def handle(self, route, request):
        u = urllib.parse.urlparse(request.url); path, q = u.path, urllib.parse.parse_qs(u.query)
        method = request.method
        self.calls.append((method, path + ("?" + u.query if u.query else "")))

        def send(status, body=None):
            route.fulfill(status=status, headers={"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
                          body="" if body is None else json.dumps(body))
        denied = {"message": "Resource not accessible by personal access token"}
        if method == "OPTIONS":
            return route.fulfill(status=204, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"})
        if request.headers.get("authorization", "") != "Bearer " + TOKEN:
            return send(401, {"message": "Bad credentials"})
        if path == "/user":
            return send(200, {"login": "Parthp6174"})
        if path == REPO + "/contents/data/developments.json":
            if method == "GET":
                return send(200, {"content": b64(self.dev_text), "sha": self.dev_sha, "encoding": "base64"})
            if "contents" not in self.perms:
                return send(403, denied)
            body = json.loads(request.post_data)
            if self.conflict_once:                    # someone else changed the file a moment ago
                self.conflict_once = False; self.dev_sha = "devsha-other"
                return send(409, {"message": "data/developments.json does not match"})
            if body.get("sha") != self.dev_sha:
                return send(409, {"message": "sha mismatch"})
            text = unb64(body["content"]); json.loads(text)
            self.puts.append(("dev", body["message"], text))
            self.dev_text = text; self.dev_sha = "devsha%d" % len(self.puts)
            commit = "c0ffee%04d" % len(self.puts)
            self.new_run("push", commit)
            return send(200, {"content": {"sha": self.dev_sha}, "commit": {"sha": commit}})
        if path == REPO + "/contents/.github/workflows/pages.yml":
            if method == "GET":
                return send(200, {"content": b64(self.wf_text), "sha": self.wf_sha})
            if "workflows" not in self.perms:
                return send(403, denied)
            body = json.loads(request.post_data)
            self.wf_text = unb64(body["content"]); self.puts.append(("wf", body["message"], self.wf_text))
            self.wf_by = "Parthp6174"
            return send(200, {"content": {"sha": "wfsha1"}, "commit": {"sha": "wfc1"}})
        if path == REPO + "/actions/workflows/pages.yml":
            return send(200, {"id": 1, "state": self.wf_state, "path": ".github/workflows/pages.yml"})
        if path == REPO + "/actions/workflows/pages.yml/enable":
            self.enabled += 1; self.wf_state = "active"; return send(204)
        if path == REPO + "/actions/workflows/pages.yml/dispatches":
            if "actions" not in self.perms:
                return send(403, denied)
            self.dispatches.append(json.loads(request.post_data))
            self.new_run("workflow_dispatch", "head0")
            return send(204)
        if path == REPO + "/actions/workflows/pages.yml/runs":
            ev = (q.get("event") or [None])[0]; hs = (q.get("head_sha") or [None])[0]; per = int((q.get("per_page") or ["30"])[0])
            if ev == "schedule":
                return send(200, {"workflow_runs": self.schedule_runs[:per]})
            rs = sorted((r for r in self.runs if (not ev or r["event"] == ev) and (not hs or r["head_sha"] == hs)), key=lambda r: -r["id"])[:per]
            return send(200, {"workflow_runs": [self.run_obj(r) for r in rs]})
        m = re.match(re.escape(REPO) + r"/actions/runs/(\d+)(/jobs)?$", path)
        if m:
            rid = int(m.group(1)); r = next(r for r in self.runs if r["id"] == rid)
            if m.group(2):
                n = self.polls.get(rid, 0)
                steps = [("Install dependencies", "completed"), ("Fetch prices from Yahoo Finance", "in_progress" if n < 3 else "completed"),
                         ("Collect headlines from Google News", "in_progress" if n == 3 else ("completed" if n > 3 else "queued")),
                         ("Build pages", "in_progress" if n == 4 else "queued")]
                return send(200, {"jobs": [dict(name="build", status="in_progress" if n < 5 else "completed", steps=[dict(name=a, status=b) for a, b in steps])]})
            self.polls[rid] = self.polls.get(rid, 0) + 1
            obj = self.run_obj(r)
            if obj["status"] == "completed" and r["event"] == "workflow_dispatch":
                self.refreshed = True                 # the site now serves the refreshed prices and headlines
            return send(200, obj)
        if path == REPO + "/commits":
            return send(200, [{"author": {"login": self.wf_by}, "committer": {"login": self.wf_by}, "commit": {"committer": {"date": iso(NOW - dt.timedelta(hours=3))}}}])
        self.unknown.append(method + " " + path)
        return send(404, {"message": "Not Found: " + path})


def serve_data(fake):
    def handler(route, request):
        name = os.path.basename(urllib.parse.urlparse(request.url).path)
        fresh = bool(fake and fake.refreshed)
        if name == "quotes.json":
            body = FIX["quotes1" if fresh else "quotes0"]
        elif name == "news.json":
            body = FIX["news1" if fresh else "news0"]
        else:
            return route.fallback()
        route.fulfill(status=200, headers={"Content-Type": "application/json"}, body=body)
    return handler


# ---------------------------------------------------------------- helpers
RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + (("  -- " + str(detail)) if detail and not cond else ""), flush=True)


def clean_text(page, label):
    """Nothing like 'null', 'undefined' or '[object' printed in the bar or the desk."""
    txt = page.evaluate("(document.getElementById('desk-bar') ? document.getElementById('desk-bar').innerText : '') + ' ' + (document.getElementById('desk') ? document.getElementById('desk').innerText : '')")
    bad = re.findall(r"\bnull\b|\bundefined\b|\[object|NaN", txt)
    check(label + ": no stray null/undefined text", not bad, bad[:5])


def shot(target, name):
    if OUT:
        target.screenshot(path=os.path.join(OUT, name))


def is_data(u): return u.startswith(BASE) and re.search(r"/data/\w+\.json", u) is not None
def is_build(u): return u.startswith(BASE) and "/data/build.json" in u


def new_page(browser, fake, token=True, scheme="light", width=1280, height=900, storage=None):
    ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme)
    init = dict(storage or {})
    if token:
        init["aiscm.ghkey"] = TOKEN
    if init:
        ctx.add_init_script("(() => { const d = %s; for (const k in d) localStorage.setItem(k, d[k]); })();" % json.dumps(init))
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append("console:" + m.text) if m.type == "error" and not m.text.startswith("Failed to load resource") else None)
    page.on("dialog", lambda d: (errors.append("dialog:" + d.message), d.dismiss()))
    unauth = lambda r, q: r.fulfill(status=401, body='{"message":"Bad credentials"}', headers={"Access-Control-Allow-Origin": "*"})
    ctx.route("https://api.github.com/**", fake.handle if fake else unauth)
    ctx.route(is_data, serve_data(fake))
    ctx.route("https://fonts.googleapis.com/**", lambda r, q: r.fulfill(status=200, body="", headers={"Content-Type": "text/css"}))
    return ctx, page, errors


def build_json(page, body):
    page.route(is_build, lambda r, q: r.fulfill(status=200, headers={"Content-Type": "application/json"}, body=json.dumps(body)))


RELOADED = re.compile(r".*\?v=\d+#log$")
recent_schedule = lambda: [{"id": 1, "created_at": iso(dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=10))}]


# ---------------------------------------------------------------- the checks
def run_checks(browser):
    # 1. a visitor without a key
    ctx, page, errors = new_page(browser, None, token=False)
    page.goto(BASE + "#desk"); page.wait_for_selector("#dk-status .dk-cell"); page.wait_for_selector(".dk-ni")
    check("visitor: desk visible", page.is_visible("#desk"))
    check("visitor: bar shows Reload", "Reload" in page.inner_text("#desk-bar"), page.inner_text("#desk-bar"))
    check("visitor: toc link added", page.locator("nav.toc a[data-desk]").count() == 1)
    tabs = page.locator(".atlases a")
    check("switch: all three pages offered, this one marked", tabs.count() == 3 and tabs.nth(0).get_attribute("aria-current") == "page" and tabs.nth(1).get_attribute("aria-current") is None and tabs.nth(2).get_attribute("aria-current") is None)
    check("switch: sits above the page title", page.evaluate("document.querySelector('.atlases').getBoundingClientRect().bottom <= document.querySelector('h1').getBoundingClientRect().top"))
    check("switch: The Money tab points to its page", page.evaluate("document.querySelector('#nav-atlas').href") == BASE + "money/")
    check("switch: The Odds tab points to its page", page.evaluate("document.querySelector('#nav-odds').href") == BASE + "odds/" and "odds" in page.inner_text("#nav-odds-c"))
    check("visitor: radar lists stories", page.locator(".dk-ni").count() >= 15, page.locator(".dk-ni").count())
    check("visitor: unsafe headline shown as text", page.evaluate("window.__xss") is None and page.locator(".dk-nt", has_text="Bad headline").count() == 1)
    check("visitor: javascript: link not rendered", page.locator('a[href^="javascript"]').count() == 0)
    check("visitor: logged headline hidden by default", page.locator(".dk-nt", has_text=LOGGED["title"][:40]).count() == 0)
    page.check("#dk-allnews"); page.wait_for_timeout(200)
    check("visitor: logged headline tagged", page.locator(".dk-ni", has_text=LOGGED["title"][:40]).locator(".dk-tag").inner_text() == "In the log")
    page.uncheck("#dk-allnews")
    orc = page.locator(".dk-ni", has_text="Oracle prices $18 billion bond")
    check("radar: grouped story lists other sources", "Also: Bloomberg, CNBC and 1 more" in orc.locator(".dk-also").inner_text() and "4 reports" in orc.locator(".dk-nmeta").inner_text(), orc.inner_text())
    check("radar: unsafe source link not linked", orc.locator(".dk-also a").count() == 1)
    n0 = page.locator(".dk-ni").count()
    orc.get_by_role("button", name="Hide").click(); page.wait_for_timeout(200)
    check("radar: hide removes the story", page.locator(".dk-ni").count() == n0 - 1 and page.locator(".dk-ni", has_text="Oracle prices").count() == 0)
    check("radar: hide stores every report id", "aaaaaaaaaaa3" in page.evaluate("localStorage.getItem('aiscm.hiddenNews')"))
    page.reload(); page.wait_for_selector(".dk-ni"); page.wait_for_timeout(400)
    check("radar: hidden story stays hidden after reload", page.locator(".dk-ni", has_text="Oracle prices").count() == 0)
    check("radar: nothing marked new on a repeat visit", page.locator(".dk-new").count() == 0)
    check("visitor: connect panel shown", page.locator("#dk-connect h3").inner_text().startswith("Site owner"))
    check("visitor: publish button suggests", page.inner_text("#dk-publish") == "Suggest on GitHub")
    check("visitor: status shows price source", "from Yahoo" in page.inner_text("#dk-status"), page.inner_text("#dk-status"))
    clean_text(page, "visitor")
    page.fill("#dk-title", "Preview without a summary"); page.get_by_role("button", name="Preview", exact=True).click(); page.wait_for_timeout(150)
    clean_text(page, "visitor preview")
    page.get_by_role("button", name="Clear", exact=True).click()
    shot(page.locator("#desk"), "visitor_desk.png")
    page.locator(".dk-ni", has_text="Ras Laffan helium").get_by_role("button", name="Suggest for the log").click(); page.wait_for_timeout(600)
    check("visitor: form prefilled from the headline", page.input_value("#dk-title") == "Ras Laffan helium restart slips to November")
    check("visitor: links prefilled from the topic", page.locator("#dk-link-chips .nchip").count() >= 3, page.locator("#dk-link-chips .nchip").count())
    page.fill("#dk-summary", "Qatar said the restart slips a month.")
    with ctx.expect_page() as pop:
        page.click("#dk-publish")
    url = pop.value.url; pop.value.close()
    check("visitor: opens a prefilled GitHub issue", "issues/new" in url and "template=new-development.yml" in url and "Ras+Laffan" in url, url[:200])
    check("visitor: no page errors", not errors, errors[:3])
    ctx.close()

    # 2. the owner; the schedule has never run
    fake = FakeGitHub()
    ctx, page, errors = new_page(browser, fake)
    page.goto(BASE + "#desk"); page.wait_for_selector("#dk-alert .dk-alertcard.warn", timeout=10000)
    check("owner: connected panel", "Parthp6174" in page.inner_text("#dk-connect"))
    check("owner: alert says not started", "haven't started" in page.inner_text("#dk-alert"))
    check("owner: status not running", "Not running yet" in page.inner_text("#dk-status"))
    check("owner: log lists every entry", page.locator("#dk-entries .dk-er").count() == N_ENTRIES + N_UPCOMING, page.locator("#dk-entries .dk-er").count())
    clean_text(page, "owner")
    shot(page, "owner_desk.png")
    page.get_by_role("button", name="Restart automatic updates").click()
    page.wait_for_function("document.querySelector('#dk-status .dk-prog').className.includes('ok')", timeout=10000)
    wf = [x for x in fake.puts if x[0] == "wf"]
    check("owner: workflow committed once", len(wf) == 1)
    before, after = re.findall(r'cron: "([^"]+)"', WF_TEXT), re.findall(r'cron: "([^"]+)"', wf[0][2]) if wf else []
    def shifted(a, b):      # same hours and days; every minute changed, still in its quarter-hour, never on :00/:15/:30/:45
        mins = list(zip(a.split(" ")[0].split(","), b.split(" ")[0].split(",")))
        return a.split(" ", 1)[1] == b.split(" ", 1)[1] and all(x != y and int(y) % 15 and int(x) // 15 == int(y) // 15 for x, y in mins)
    check("owner: every scheduled minute shifted", len(before) == len(after) >= 1 and all(shifted(a, b) for a, b in zip(before, after)), (before, after))
    check("owner: rest of the workflow untouched", bool(wf) and re.sub(r'cron: "[^"]+"', "", wf[0][2]) == re.sub(r'cron: "[^"]+"', "", WF_TEXT))
    check("owner: alert gone after turning on", page.locator("#dk-alert .dk-alertcard.warn").count() == 0)
    check("owner: status says turned on", "Turned on" in page.inner_text("#dk-status"), page.inner_text("#dk-status"))
    check("owner: no page errors", not errors, errors[:3])

    # 3. Refresh now
    page.click("#dk-status .dk-refresh")
    page.wait_for_function("document.querySelector('#desk-bar .dk-prog').textContent.includes('Fetching prices')", timeout=30000)
    check("refresh: shows the step it is on", True)
    check("refresh: buttons disabled while busy", page.locator("#dk-status .dk-refresh").is_disabled())
    page.wait_for_function("document.querySelector('#dk-status .dk-prog').className.includes('ok')", timeout=90000)
    check("refresh: asks for prices and headlines", fake.dispatches and fake.dispatches[0] == {"ref": "main", "inputs": {"targets": "auto", "news": "always"}}, fake.dispatches)
    check("refresh: new headline appears", page.locator(".dk-nt", has_text="Brand new: Samsung").count() == 1)
    check("refresh: only the new headline is marked New", page.locator(".dk-new").count() == 1 and page.locator(".dk-ni", has_text="Brand new: Samsung").locator(".dk-new").count() == 1, page.locator(".dk-new").count())
    check("refresh: bar counts the new headline", "(1 new)" in page.inner_text("#desk-bar"), page.inner_text("#desk-bar"))
    check("refresh: watchlist shows live prices", "Yahoo Finance" in page.inner_text("#w-live"))
    clean_text(page, "after refresh")
    check("refresh: no page errors", not errors, errors[:3])

    # 4. publish an entry that also changes the pages
    page.locator(".dk-ni", has_text="SK hynix says HBM4").get_by_role("button", name="Add to log").click(); page.wait_for_timeout(500)
    page.fill("#dk-summary", "SK hynix told analysts its 2027 HBM4 output is fully booked.")
    page.select_option("#dk-ch-add", "node_status")
    page.select_option("#dk-c0-node", "hbm"); page.select_option("#dk-c0-status", "critical")
    check("publish: hint shows the current rating", "Now:" in page.locator(".dk-ch .dk-hint").first.inner_text())
    page.select_option("#dk-ch-add", "add_site")
    page.fill("#dk-c1-name", "Test HBM fab"); page.select_option("#dk-c1-node", "hbm")
    page.fill("#dk-c1-lat", "37.27, 127.01")
    check("publish: pasted coordinates split into both fields", page.input_value("#dk-c1-lat") == "37.27" and page.input_value("#dk-c1-lon") == "127.01")
    page.get_by_role("button", name="Preview", exact=True).click(); page.wait_for_timeout(200)
    check("publish: preview lists the changes", page.locator("#dk-preview li").count() == 2, page.inner_text("#dk-preview"))
    clean_text(page, "publish preview")
    with page.expect_navigation(url=RELOADED, timeout=90000):
        page.click("#dk-publish")
    page.wait_for_load_state("load")
    dev_puts = [x for x in fake.puts if x[0] == "dev"]
    check("publish: one commit", len(dev_puts) == 1)
    d = json.loads(dev_puts[0][2]); e = d["entries"][0]
    check("publish: entry first, with an id", e["id"].startswith(e["date"] + "-sk-hynix"), e["id"])
    check("publish: links from the topic", "hbm" in e["links"].get("nodes", []), e.get("links"))
    check("publish: source from the headline", e["source"]["label"].startswith("Bloomberg, ") and e["source"]["url"].startswith("https://news.google.com/"), e.get("source"))
    check("publish: changes saved", [c["type"] for c in e["changes"]] == ["node_status", "add_site"] and e["changes"][1]["lat"] == 37.27 and e["changes"][1]["id"] == "test-hbm-fab", e["changes"])
    check("publish: other entries byte-for-byte unchanged", json.dumps(d["entries"][1:], ensure_ascii=False) == json.dumps(DEV["entries"], ensure_ascii=False) and dev_puts[0][2].endswith("}\n"))
    check("publish: commit message", dev_puts[0][1].startswith("Add development: SK hynix"), dev_puts[0][1])
    check("publish: address cleaned after the reload", "?v=" not in page.url, page.url)
    check("publish: no page errors", not errors, errors[:3])

    # 5. edit it, then delete it while someone else changes the file
    page.wait_for_selector("#dk-entries .dk-er", timeout=10000)
    page.locator("#dk-entries .dk-er", has_text="SK hynix says HBM4").get_by_role("button", name="Edit").click(); page.wait_for_timeout(300)
    check("edit: form in edit mode", "Editing" in page.inner_text("#dk-editing") and page.inner_text("#dk-publish") == "Save changes")
    check("edit: changes restored", page.locator(".dk-ch").count() == 2 and page.input_value("#dk-c1-lat") == "37.27")
    page.fill("#dk-title", "SK hynix: HBM4 sold out through 2027")
    with page.expect_navigation(url=RELOADED, timeout=90000):
        page.click("#dk-publish")
    page.wait_for_selector("#dk-entries .dk-er")
    d = json.loads(fake.puts[-1][2])
    check("edit: same id, new title, same place", d["entries"][0]["title"] == "SK hynix: HBM4 sold out through 2027" and d["entries"][0]["id"] == e["id"] and len(d["entries"]) == N_ENTRIES + 1)
    check("edit: changes kept", len(d["entries"][0].get("changes", [])) == 2)
    fake.conflict_once = True
    row = page.locator("#dk-entries .dk-er", has_text="SK hynix: HBM4 sold out")
    row.get_by_role("button", name="Delete").click()
    with page.expect_navigation(url=RELOADED, timeout=90000):
        row.get_by_role("button", name="Delete").click()
    d = json.loads(fake.puts[-1][2])
    check("delete: removed, after retrying a conflicting write", len(d["entries"]) == N_ENTRIES and all(x["id"] != e["id"] for x in d["entries"]))
    check("delete: file back to its original content and layout", json.loads(fake.puts[-1][2]) == DEV and fake.puts[-1][2].startswith('{\n  "') and fake.puts[-1][2].endswith("}\n"))
    check("edit/delete: no page errors", not errors, errors[:3])
    check("owner flows: no unexpected API calls", not fake.unknown, fake.unknown[:5])
    ctx.close()

    # 6. a paused workflow, build warnings, and a key without the Actions permission
    fake = FakeGitHub(wf_state="disabled_inactivity", perms=("contents",))
    ctx, page, errors = new_page(browser, fake)
    build_json(page, {"built": iso(NOW), "warnings": ["entry 2026-10-02 'X': unknown nodes 'nope'; link removed"], "entries": N_ENTRIES, "upcoming": N_UPCOMING})
    page.goto(BASE + "#desk"); page.wait_for_selector("#dk-alert .dk-alertcard.warn", timeout=10000)
    txt = page.inner_text("#dk-alert")
    check("paused: alert explains the 60-day rule", "60 days" in txt, txt)
    check("warnings: shown to the owner", "left out of the last build" in txt and "unknown nodes" in txt, txt)
    clean_text(page, "alerts")
    shot(page.locator("#desk"), "alerts.png")
    page.get_by_role("button", name="Switch them back on").click(); page.wait_for_timeout(1500)
    check("paused: workflow re-enabled", fake.enabled == 1)
    page.click("#dk-status .dk-refresh"); page.wait_for_function("document.querySelector('#dk-status .dk-prog').className.includes('fail')", timeout=15000)
    check("permissions: says what to grant", "Read and write" in page.inner_text("#dk-status .dk-prog"), page.inner_text("#dk-status .dk-prog"))
    check("paused/permissions: no page errors", not errors, errors[:3])
    ctx.close()

    # 7. an expired key, then connecting for this session only
    ctx, page, errors = new_page(browser, FakeGitHub(), token=False, storage={"aiscm.ghkey": "github_pat_" + "B" * 82})
    page.goto(BASE + "#desk"); page.wait_for_selector("#dk-token", timeout=10000)
    check("expired key: back to the connect form with a reason", "didn't accept" in page.inner_text("#dk-connect"), page.inner_text("#dk-connect"))
    page.fill("#dk-token", "not a key"); page.click("#dk-connect .dk-btn")
    check("connect: rejects something that is not a key", "doesn't look like" in page.inner_text("#dk-conn-err"))
    page.fill("#dk-token", TOKEN); page.uncheck("#dk-remember"); page.click("#dk-connect .dk-btn")
    page.wait_for_selector("text=Connected to GitHub", timeout=10000)
    check("connect: kept for the session only", page.evaluate("localStorage.getItem('aiscm.ghkey')") is None and page.evaluate("sessionStorage.getItem('aiscm.ghkey')") == TOKEN)
    page.get_by_role("button", name="Disconnect").click(); page.wait_for_timeout(300)
    check("disconnect: key removed", page.evaluate("sessionStorage.getItem('aiscm.ghkey')") is None and page.locator("#dk-token").count() == 1)
    check("connect flow: no page errors", not errors, errors[:3])
    ctx.close()

    # 8. a cached page catches up with a newer build, once
    ctx, page, errors = new_page(browser, None, token=False)
    build_json(page, {"built": iso(NOW), "rev": "ffff00001111", "warnings": []})
    loads = []
    page.on("framenavigated", lambda f: loads.append(f.url) if f == page.main_frame else None)
    page.goto(BASE + "#watch"); page.wait_for_timeout(3500)
    check("stale page: reloads once for the new build", sum(1 for u in loads if "v=ffff00001111" in u) == 1, loads)
    check("stale page: keeps the section", page.url.endswith("#watch"), page.url)
    check("stale page: offers the new version if still behind", page.locator("#desk-bar .dk-fresh").count() == 1)
    clean_text(page, "stale page")
    check("stale page: no page errors", not errors, errors[:3])
    ctx.close()

    # 9. The Money: reached from the switch, its bar, and phones in both themes
    fake = FakeGitHub()
    ctx, page, errors = new_page(browser, fake, scheme="dark")
    page.goto(BASE); page.wait_for_selector("#dk-alert .dk-alertcard.warn", timeout=10000)    # the home page has finished talking to GitHub
    fake.calls.clear()
    page.click("#nav-atlas"); page.wait_for_url(BASE + "money/"); page.wait_for_selector("#desk-bar .dk-bt", timeout=10000); page.wait_for_timeout(800)
    check("switch: one click from the home page opens The Money", page.inner_text("h1").strip().lower() == "the money", page.inner_text("h1"))
    check("switch: The Money marked there, The Chain links home", page.get_attribute("#nav-atlas", "aria-current") == "page" and page.evaluate("document.querySelector('#nav-supply').href") == BASE)
    hero = page.inner_text("#kpis .kpi.hero .value").strip()
    check("switch: capex figure matches The Money headline", hero.startswith("$") and hero in page.inner_text("#nav-atlas-c"), (hero, page.inner_text("#nav-atlas-c")))
    check("atlas: bar with Refresh now", "Refresh now" in page.inner_text("#desk-bar"))
    clean_text(page, "atlas bar")
    check("atlas: desk link points back", page.get_attribute("nav.toc a[data-desk]", "href") == "../#desk")
    check("atlas: no GitHub calls on load", not fake.calls, fake.calls[:3])
    shot(page, "atlas_dark.png")
    check("atlas: no page errors", not errors, errors[:3])
    page.goto(BASE + "investment-atlas/#payback"); page.wait_for_url(BASE + "money/#payback"); page.wait_for_selector("#desk-bar .dk-bt", timeout=10000)
    check("old address: redirects to the page's new address and keeps the section", page.inner_text("h1").strip().lower() == "the money")
    check("brand: shown in the switch on both pages", page.inner_text(".atlases .at-brand").strip().lower() == "chokepoint")
    ctx.close()
    for scheme in ("light", "dark"):
        ctx, page, errors = new_page(browser, FakeGitHub(schedule_runs=recent_schedule(), wf_by="Parthp6174"), scheme=scheme, width=390, height=844)
        page.goto(BASE + "#desk"); page.wait_for_selector("text=Connected to GitHub", timeout=10000); page.wait_for_selector("#dk-entries .dk-er")
        page.wait_for_function("document.querySelector('#dk-status').innerText.includes('Running')", timeout=10000)
        check(f"phone {scheme}: schedule shown as running", True)
        check(f"phone {scheme}: no sideways scroll", page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), page.evaluate("[document.documentElement.scrollWidth, window.innerWidth]"))
        check(f"phone {scheme}: switch fits on one line each", page.evaluate("[...document.querySelectorAll('.atlases .at-t')].every(e => e.getBoundingClientRect().height < 24)"))
        clean_text(page, f"phone {scheme}")
        shot(page.locator("#desk"), f"phone_{scheme}_desk.png")
        check(f"phone {scheme}: no page errors", not errors, errors[:3])
        ctx.close()


def main():
    global BASE, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", default=None, help="folder for screenshots")
    a = ap.parse_args()
    if a.shots:
        OUT = os.path.abspath(a.shots); os.makedirs(OUT, exist_ok=True)
    FIX.update(quotes0=json.dumps(quotes(NOW - dt.timedelta(minutes=50), 1.0)), quotes1=json.dumps(quotes(NOW + dt.timedelta(minutes=3), 1.012)),
               news0=json.dumps(news(False)), news1=json.dumps(news(True)))
    with tempfile.TemporaryDirectory() as site:
        subprocess.run([sys.executable, os.path.join(ROOT, "src", "build.py"), "--target", "github", "--quotes", os.devnull + ".none", "--out", site],
                       check=True, env=dict(os.environ, GITHUB_SHA=REV + "7890"), stdout=subprocess.DEVNULL)
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
