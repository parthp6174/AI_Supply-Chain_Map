#!/usr/bin/env python3
"""Build both pages from the data files.

    python src/build.py                                  # GitHub Pages site -> site/
    python src/build.py --target artifact                # claude.ai versions -> dist/artifact/
    python src/build.py --quotes site/data/quotes.json   # embed the latest live quotes as the fallback snapshot

    python src/build.py --lenient                        # CI: skip broken developments and report them instead of failing

Inputs: src/supply/supply_data.py, src/atlas/data_items.py and data/developments.json.
By default the build stops with a clear message if a development links to something that does not exist.
With --lenient (used by the GitHub workflow) it drops only the broken part, keeps building so prices keep
updating, and lists what it dropped in site/data/build.json for the Update desk to show.
"""
import argparse, copy, datetime as dt, json, math, os, re, shutil, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for sub in ("common", "atlas", "supply"):
    sys.path.insert(0, os.path.join(ROOT, "src", sub))
import geo                      # noqa: E402
import data_items as A          # noqa: E402
import supply_data as D         # noqa: E402
import supply_model as M        # noqa: E402

REPO = "Parthp6174/AI_Supply-Chain_Map"
REPO_URL = "https://github.com/" + REPO
SITE_URL = "https://parthp6174.github.io/AI_Supply-Chain_Map/"
ARTIFACT_URLS = {"supply": "https://claude.ai/artifact/CdidyJg9J9QccBbjBS8c7z",
                 "atlas": "https://claude.ai/artifact/4AnG4Rk35RdMEn3aKYr7Pm"}
MARKET_KEYS = ["msft", "googl", "amzn", "meta", "orcl", "crwv", "spcx", "nvda", "tsmc", "avgo", "amd", "mu"]
ISO = {"United States": "USA", "United Arab Emirates": "ARE", "Saudi Arabia": "SAU", "India": "IND", "United Kingdom": "GBR",
       "Norway": "NOR", "Portugal": "PRT", "France": "FRA", "Belgium": "BEL", "Germany": "DEU", "Spain": "ESP", "Japan": "JPN",
       "South Korea": "KOR", "Argentina": "ARG", "China": "CHN", "Taiwan": "TWN", "Netherlands": "NLD", "Italy": "ITA",
       "Sweden": "SWE", "Finland": "FIN", "Denmark": "DNK", "Ireland": "IRL", "Canada": "CAN", "Mexico": "MEX", "Brazil": "BRA",
       "Chile": "CHL", "Australia": "AUS", "Malaysia": "MYS", "Singapore": "SGP", "Indonesia": "IDN", "Thailand": "THA",
       "Vietnam": "VNM", "Philippines": "PHL", "Qatar": "QAT", "Kuwait": "KWT", "Bahrain": "BHR", "Oman": "OMN", "Israel": "ISR",
       "Egypt": "EGY", "South Africa": "ZAF", "Kenya": "KEN", "Nigeria": "NGA", "Morocco": "MAR", "Poland": "POL",
       "Switzerland": "CHE", "Austria": "AUT", "Kazakhstan": "KAZ", "New Zealand": "NZL", "Iceland": "ISL"}


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- developments
NODE_STATUS = {"critical", "serious", "warning"}
SITE_STATUS = {"normal", "ramping", "tight", "short", "controlled", "offline", "struck", "threatened", "disrupted", "at risk"}
SCEN_STATUS = {"live", "scheduled", "plausible", "tail"}
ATLAS_CAT = {"compute", "chips", "funding"}
ATLAS_KIND = {"site", "program", "funding"}
ATLAS_PREC = {"site", "city", "region", "hq", "country"}


def slugify(text, n=64):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")[:n].strip("-") or "entry"


def load_devs(problems, lenient):
    path = os.path.join(ROOT, "data", "developments.json")
    try:
        with open(path) as f:
            dev = json.load(f)
    except json.JSONDecodeError as e:
        if not lenient:
            raise BuildError(f"data/developments.json is not valid JSON: {e}")
        problems.append(f"data/developments.json is not valid JSON ({e}); built without developments")
        dev = {}
    if not isinstance(dev, dict):
        if not lenient:
            raise BuildError("data/developments.json must be an object with 'entries' and 'upcoming' lists")
        problems.append("data/developments.json must be an object with 'entries' and 'upcoming' lists; built without developments")
        dev = {}
    for key in ("entries", "upcoming"):
        lst = dev.get(key, [])
        if not isinstance(lst, list):
            problems.append(f"'{key}' in data/developments.json must be a list; left out")
            lst = []
        bad = [x for x in lst if not isinstance(x, dict)]
        if bad:
            problems.append(f"{len(bad)} item(s) in '{key}' are not objects; left out")
        dev[key] = [x for x in lst if isinstance(x, dict)]
    seen = set()
    for lst in (dev["entries"], dev["upcoming"]):
        for e in lst:
            base = e.get("id") or slugify(f"{e.get('date', '')}-{e.get('title', '')}")
            i, k = base, 2
            while i in seen:
                i = f"{base}-{k}"; k += 1
            if e.get("id") and i != e["id"]:
                problems.append(f"entry id '{e['id']}' is used twice; the second copy is shown as '{i}'")
            e["id"] = i; seen.add(i)
    return dev


def apply_developments(dev, nodes, sites, scen, quotes, items, sup_src, atl_src, problems):
    """Validate every entry and apply its changes. Broken links and changes are dropped and recorded in `problems`."""
    node = {n["id"]: n for n in nodes}
    site = {s["id"]: s for s in sites}
    sc = {s["id"]: s for s in scen}
    item = {i["id"]: i for i in items}
    known = dict(nodes=node, sites=site, scenarios=sc, companies=D.C, atlasItems=item)

    def clean(e, where):
        """Drop an entry missing date or title; drop link ids that do not exist. Returns False to drop the entry."""
        if not e.get("date") or not e.get("title") or not re.match(r"^\d{4}-\d{2}-\d{2}$", str(e.get("date", ""))):
            problems.append(f"{where}: needs a title and a date like 2026-10-15; left out")
            return False
        e["title"] = str(e["title"])
        L = e.get("links") if isinstance(e.get("links"), dict) else {}
        for kind, table in known.items():
            ids = L.get(kind) or []
            ids = ids if isinstance(ids, list) else [ids]
            bad = [k for k in ids if not isinstance(k, str) or k not in table]
            if bad:
                problems.append(f"{where}: unknown {kind} {', '.join(repr(b) for b in bad)}; link removed")
            L[kind] = [k for k in ids if isinstance(k, str) and k in table]
        e["links"] = {k: v for k, v in L.items() if k in known and v}
        src = e.get("source")
        if src is not None:
            url = src.get("url") if isinstance(src, dict) else None
            if url and not re.match(r"^https?://\S+$", str(url)):
                problems.append(f"{where}: source link must start with http:// or https://; link removed")
                url = None
            if url:
                e["source"] = dict(label=str(src.get("label") or "Source"), url=url)
            else:
                e.pop("source", None)
        if not isinstance(e.get("pages", []), list):
            e["pages"] = ["supply", "atlas"]
        return True

    def num(v, lo, hi, what):
        v = float(v)
        if not lo <= v <= hi:
            raise ValueError(f"{what} {v} is out of range")
        return v

    kept = []
    for i, e in enumerate(sorted(dev["entries"], key=lambda e: str(e.get("date", "")))):
        where = f"entry {e.get('date')} '{str(e.get('title', ''))[:48]}'"
        if not clean(e, where):
            continue
        kept.append(e)
        skey = None
        if (e.get("source") or {}).get("url"):
            skey = f"dev{i}"
            label = (e["source"].get("label") or "Source") + " - " + e["title"]
            sup_src[skey] = (label, e["source"]["url"]); atl_src[skey] = (label, e["source"]["url"])
        changes = e.get("changes") or []
        if not isinstance(changes, list):
            problems.append(f"{where}: 'changes' must be a list; changes skipped")
            changes = []
        for ch in changes:
            t = ch.get("type") if isinstance(ch, dict) else "(not an object)"
            try:
                if not isinstance(ch, dict):
                    raise ValueError("a change must be an object with a 'type'")
                if t == "node_status":
                    n = node[ch["node"]]
                    if not n.get("choke"):
                        raise ValueError(f"'{ch['node']}' is not a chokepoint")
                    if ch.get("status") and ch["status"] not in NODE_STATUS:
                        raise ValueError(f"rating '{ch['status']}' must be critical, serious or warning")
                    if ch.get("status"): n["choke"]["status"] = ch["status"]
                    if ch.get("state"): n["choke"]["state"] = ch["state"]
                    if ch.get("line"): n["choke"]["line"] = ch["line"]
                    if skey: n["src"].append(skey)
                elif t == "node_note":
                    n = node[ch["node"]]
                    if not ch.get("text"): raise ValueError("note text is empty")
                    n["why"] = n["why"].rstrip() + " " + ch["text"]
                    if skey: n["src"].append(skey)
                elif t == "site_status":
                    st = site[ch["site"]]
                    if ch.get("status") and ch["status"] not in SITE_STATUS:
                        raise ValueError(f"site status '{ch['status']}' is not one of {sorted(SITE_STATUS)}")
                    if ch.get("status"): st["status"] = ch["status"]
                    if ch.get("note"): st["note"] = ch["note"]
                    if skey: st["src"].append(skey)
                elif t == "add_site":
                    if ch["node"] not in node: raise ValueError(f"unknown link '{ch['node']}'")
                    sid = ch.get("id") or slugify(ch["name"], 40)
                    if sid in site: raise ValueError(f"a site with id '{sid}' already exists")
                    if ch.get("status", "normal") not in SITE_STATUS: raise ValueError(f"site status '{ch.get('status')}' is not allowed")
                    new = dict(id=sid, node=ch["node"], name=ch["name"], who=ch.get("who", ""), lat=num(ch["lat"], -90, 90, "latitude"),
                               lon=num(ch["lon"], -180, 180, "longitude"), note=ch.get("note", ""), status=ch.get("status", "normal"),
                               src=[skey] if skey else [])
                    sites.append(new); site[new["id"]] = new
                elif t == "scenario_status":
                    s0 = sc[ch["scenario"]]
                    if ch.get("status") and ch["status"] not in SCEN_STATUS:
                        raise ValueError(f"scenario status '{ch['status']}' must be live, scheduled, plausible or tail")
                    for f in ("status", "when"):
                        if ch.get(f): s0[f] = ch[f]
                elif t == "quote_note":
                    if ch["company"] not in quotes: raise ValueError(f"no watchlist entry for '{ch['company']}'")
                    if not ch.get("proj"): raise ValueError("projection text is empty")
                    quotes[ch["company"]]["proj"] = ch["proj"]
                elif t == "atlas_item_status":
                    it = item[ch["item"]]
                    if ch.get("status"): it["status"] = ch["status"]
                    if ch.get("note_append"): it["note"] = (it["note"] or "").rstrip() + " " + ch["note_append"]
                    if skey: it["src"] = list(it["src"]) + [skey]
                elif t == "add_atlas_item":
                    f = ch["item"]
                    iid = f.get("id") or slugify(f["title"], 40)
                    if iid in item: raise ValueError(f"an Investment Atlas item with id '{iid}' already exists")
                    if f["cat"] not in ATLAS_CAT: raise ValueError(f"category '{f['cat']}' must be compute, chips or funding")
                    if f["kind"] not in ATLAS_KIND: raise ValueError(f"type '{f['kind']}' must be site, program or funding")
                    if f.get("prec", "city") not in ATLAS_PREC: raise ValueError(f"pin precision '{f.get('prec')}' is not allowed")
                    if not re.match(r"^\d{4}-\d{2}$", str(f["date"])): raise ValueError("date must look like 2026-10")
                    if f["country"] not in ISO and not f.get("iso"): raise ValueError(f"no ISO code for '{f['country']}'; add 'iso'")
                    amount = None if f.get("amount") in (None, "") else float(f["amount"])
                    gw = None if f.get("gw") in (None, "") else float(f["gw"])
                    new = A.it(iid, f["title"], f["who"], f["cat"], f["kind"], amount, f["date"], f["place"], f["country"],
                               num(f["lat"], -90, 90, "latitude"), num(f["lon"], -180, 180, "longitude"), f.get("prec", "city"),
                               f.get("status") or "Announced", f.get("note", ""), [skey] if skey else [], gw=gw,
                               amount_note=f.get("amount_note") or None, partners=f.get("partners") or None)
                    if f.get("iso"): ISO[f["country"]] = f["iso"]
                    items.append(new); item[new["id"]] = new
                else:
                    raise ValueError(f"unknown change type '{t}'")
            except KeyError as ex:
                problems.append(f"{where}: change '{t}' is missing a field or refers to something that does not exist ({ex}); change skipped")
            except (ValueError, TypeError, AttributeError) as ex:
                problems.append(f"{where}: change '{t}' skipped: {ex}")
    dev["entries"] = kept
    dev["upcoming"] = [e for e in dev["upcoming"] if clean(e, f"upcoming {e.get('date')} '{str(e.get('title', ''))[:48]}'")]


def dev_payload(dev, page):
    keep = lambda e: page in e.get("pages", ["supply", "atlas"])
    ent = sorted([e for e in dev["entries"] if keep(e)], key=lambda e: e["date"], reverse=True)
    up = sorted([e for e in dev["upcoming"] if keep(e)], key=lambda e: e["date"])
    strip = lambda e: {k: v for k, v in e.items() if k != "changes"}
    return dict(entries=[strip(e) for e in ent], upcoming=[strip(e) for e in up])


# ---------------------------------------------------------------- quotes
def merge_quotes(Q, path):
    meta = None
    if path and os.path.exists(path):
        with open(path) as f:
            js = json.load(f)
        for k, L in js.get("quotes", {}).items():
            q = Q.get(k)
            if not q or L.get("px") is None or L.get("psrc") != "yahoo":
                continue
            if L.get("date") and q.get("asof") and L["date"] < q["asof"]:
                continue
            q.update(px=L["px"], asof=L.get("date", q["asof"]), chg=L.get("chg"), live=True)
            if L.get("tsrc") == "yahoo" and L.get("tgt"):
                q.update(tgt=L["tgt"], n=L.get("n") or q.get("n"), rating=L.get("rating") or q.get("rating"), tsrc="yahoo")
            if L.get("next"):
                q["next"] = L["next"]
            if q.get("tgt") and not (0.3 <= q["tgt"] / q["px"] <= 3.0):
                q["tgt"] = None
            q["up"] = round((q["tgt"] / q["px"] - 1) * 100, 2) if q.get("tgt") and q.get("px") else None
        meta = dict(updated=js.get("updated"), source=js.get("source"))
    return meta


# ---------------------------------------------------------------- helpers
def number_sources(order_keys, registry):
    used = []
    for k in order_keys:
        if k and k not in used and k in registry:
            used.append(k)
    return {k: {"n": i + 1, "l": registry[k][0], "u": registry[k][1]} for i, k in enumerate(used)}


def spread(points, thresh, base, step):
    """Union-find clusters of co-located pins, spread in a ring."""
    n = len(points); parent = list(range(n))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if math.hypot(points[i]["ax"] - points[j]["ax"], points[i]["ay"] - points[j]["ay"]) < thresh:
                parent[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    for idx in groups.values():
        if len(idx) == 1:
            p = points[idx[0]]; p["x"], p["y"] = p["ax"], p["ay"]; continue
        cx = sum(points[i]["ax"] for i in idx) / len(idx); cy = sum(points[i]["ay"] for i in idx) / len(idx)
        idx.sort(key=lambda i: -(points[i].get("amount") or 0))
        R = base + step * len(idx)
        for k, i in enumerate(idx):
            a = -math.pi / 2 + 2 * math.pi * k / len(idx)
            points[i]["x"] = round(cx + R * math.cos(a), 2); points[i]["y"] = round(cy + R * math.sin(a), 2)


def box(lon0, lon1, lat0, lat1):
    lons = np.concatenate([np.linspace(lon0, lon1, 40), np.full(40, lon1), np.linspace(lon1, lon0, 40), np.full(40, lon0)])
    lats = np.concatenate([np.full(40, lat1), np.linspace(lat1, lat0, 40), np.full(40, lat0), np.linspace(lat0, lat1, 40)])
    x, y = geo.proj(lons, lats)
    return [round(float(x.min()), 1), round(float(y.min()), 1), round(float(x.max()), 1), round(float(y.max()), 1)]


def desk_config(page):
    """Settings the Update desk (src/common/desk.js) needs on the GitHub Pages site."""
    up = "" if page == "supply" else "../"
    return dict(repo=REPO, branch="main", workflow="pages.yml", devPath="data/developments.json", wfPath=".github/workflows/pages.yml",
                newsUrl=up + "data/news.json", buildUrl=up + "data/build.json", quotesUrl=up + "data/quotes.json",
                deskUrl=("" if page == "supply" else "../") + "#desk", repoUrl=REPO_URL, siteUrl=SITE_URL,
                countries=sorted(ISO) if page == "supply" else None)


def full_document(page, extra_body=""):
    """Wrap a page written for the claude.ai artifact skeleton into a standalone HTML document."""
    i = page.index('<div class="wrap">')
    head, body = page[:i], page[i:]
    title = head[head.index("<title>") + 7: head.index("</title>")]
    desc = ""
    if 'name="description" content="' in head:
        j = head.index('name="description" content="') + len('name="description" content="')
        desc = head[j: head.index('"', j)]
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
            f"<meta property=\"og:title\" content=\"{title}\">\n<meta property=\"og:description\" content=\"{desc}\">\n"
            "<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n"
            + head + "</head>\n<body>\n" + body + "\n" + extra_body + "\n</body>\n</html>\n")


def dump(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


# ---------------------------------------------------------------- build
def build(target, quotes_path, lenient=False):
    g = geo.load()
    problems = []
    dev = load_devs(problems, lenient)
    nodes = copy.deepcopy(D.NODES); sites = copy.deepcopy(D.SITES); scen = copy.deepcopy(D.SCEN)
    Q = copy.deepcopy(D.Q); items = copy.deepcopy(A.ITEMS)
    sup_src = dict(D.S); atl_src = dict(A.S)
    apply_developments(dev, nodes, sites, scen, Q, items, sup_src, atl_src, problems)
    if problems and not lenient:
        raise BuildError("data/developments.json has problems:\n  - " + "\n  - ".join(problems))
    qmeta = merge_quotes(Q, quotes_path)
    gh = target == "github"
    links = dict(
        supply=dict(companion="investment-atlas/" if gh else ARTIFACT_URLS["atlas"], quotes="data/quotes.json" if gh else None),
        atlas=dict(companion="../" if gh else ARTIFACT_URLS["supply"], quotes="../data/quotes.json" if gh else None))

    # ---------------- supply page
    M.NODE.clear(); M.NODE.update({n["id"]: n for n in nodes})
    L = M.layout()
    tier_order = [t for t, _ in D.TIERS]
    order = []
    for n in sorted(nodes, key=lambda n: tier_order.index(n["tier"])): order += n["src"]
    for s in scen: order += s["srcs"]
    for s in sites: order += s["src"]
    order.append("sa_all")
    sources = number_sources(order, sup_src)

    def cat_of(nid):
        n = M.NODE[nid]
        if n["tier"] in ("mine", "refine", "mat"): return "mat"
        return "si" if n["lane"] == "si" else "pw"
    sp = []
    for s in sites:
        x, y = geo.proj(s["lon"], s["lat"])
        d = {k: v for k, v in s.items() if k not in ("lat", "lon")}
        d["ax"], d["ay"] = round(float(x), 2), round(float(y), 2); d["cat"] = cat_of(s["node"])
        sp.append(d)
    spread(sp, 0.8, 0.45, 0.22)
    atlas_pts = []
    for it in items:
        x, y = geo.proj(it["lon"], it["lat"])
        atlas_pts.append(dict(id=it["id"], t=it["title"], w=it["who"], a=it["amount"], c=it["cat"], p=it["place"], s=it["status"],
                              x=round(float(x), 2), y=round(float(y), 2)))
    regions = [dict(label="World", box=[0, 0, g["w"], g["h"]]), dict(label="United States", box=box(-125, -66, 24, 50)),
               dict(label="Europe", box=box(-10, 30, 36, 62)), dict(label="East Asia", box=box(100, 146, 18, 45)),
               dict(label="Japan, Korea & Taiwan", box=box(118, 143, 21.5, 41)), dict(label="Gulf", box=box(44, 60, 21, 30))]
    roles = {}
    for nd in nodes:
        for f in nd["firms"]:
            roles.setdefault(f[0], [])
            if nd["id"] not in roles[f[0]]: roles[f[0]].append(nd["id"])
    companies = {k: dict(n=v[0], t=v[1], c=v[2], r=roles.get(k, [])) for k, v in D.C.items()}
    tw = next(s for s in scen if s["id"] == "taiwan")
    O0 = M.outputs(M.avail(M.scenario_shocks(tw, 0))); O1 = M.outputs(M.avail(M.scenario_shocks(tw, 1)))
    for nd in nodes: nd["box"] = L["boxes"][nd["id"]]
    sdata = dict(asOf="2026-09-30", target=target, atlasUrl=links["supply"]["companion"], quotesUrl=links["supply"]["quotes"],
                 quotesMeta=qmeta, repoUrl=REPO_URL, tiers=[dict(id=t, label=l) for t, l in D.TIERS], nodes=nodes,
                 layout=dict(w=L["w"], h=L["h"], bands=L["bands"], colw=L["colw"], top=L["top"]),
                 groupOther={a + "|" + b: v for (a, b), v in D.GROUP_OTHER.items()}, outputs=D.OUTPUTS, scen=scen, sites=sp,
                 atlas=atlas_pts, regions=regions, companies=companies, quotes=Q,
                 groups=[dict(id=a, label=b, keys=c) for a, b, c in D.GROUPS], sources=sources,
                 taiwan=dict(y1=round(O0["accel"], 3), y3=round(O1["accel"], 3)), devs=dev_payload(dev, "supply"),
                 siteUrl=SITE_URL, desk=desk_config("supply") if gh else None)
    with open(os.path.join(ROOT, "src", "supply", "template.html")) as f:
        tpl = f.read()
    supply_html = tpl.replace("__DATA__", dump(sdata)).replace("__GEO__", dump(g))

    # ---------------- investment atlas page
    pts = []
    for x in items:
        px_, py_ = geo.proj(x["lon"], x["lat"])
        it = {k: v for k, v in x.items() if k not in ("lat", "lon")}
        it["ax"], it["ay"] = round(float(px_), 2), round(float(py_), 2)
        if x["country"] not in ISO: raise BuildError(f"Add an ISO code for '{x['country']}' (field 'iso' in add_atlas_item)")
        it["iso"] = ISO[x["country"]]
        pts.append(it)
    spread(pts, 0.9, 0.6, 0.32)
    order = []
    for it in pts: order += it["src"]
    for b in A.BUILDERS + A.LABS: order += b["src"]
    for f in A.FLOWS: order += f[6]
    for c in A.COLLECTORS: order.append(c["src"])
    order += ["jpm_650", "bain_2t", "gs_12t", "jpm_consensus"]
    asources = number_sources(order, atl_src)
    flows = [dict(amount=f[2], type=f[3], term=f[4], note=f[5], src=f[6], **{"from": f[0], "to": f[1]}) for f in A.FLOWS]
    labs = [dict(l) for l in A.LABS]
    for l in labs:
        if l["id"] == "oai":
            l["fundOverride"] = "Needs outside capital"
            l["fundNote"] = "Projects about $278B of cash burn in 2026-2030 and raised $122B in March 2026."
        else:
            l["fundOverride"] = "Stretching cash flow"
            l["fundNote"] = "First operating profit in Q2 2026, but commitments ramp to about $83B a year in 2027-29 against a $65B run-rate; raised $65B in May 2026."
    lab_signed = sum(f["amount"] for f in flows if f["from"] in ("OpenAI", "Anthropic") and f["type"] not in ("Equity", "Guarantee") and f["amount"])
    aregions = [dict(label="World", box=[0, 0, g["w"], g["h"]]), dict(label="United States", box=box(-125, -66, 24, 50)),
                dict(label="Texas", box=box(-107.2, -93.3, 25.6, 36.6)), dict(label="Europe", box=box(-12, 30, 35, 70)),
                dict(label="Gulf & India", box=box(44, 90, 8, 30)), dict(label="East Asia", box=box(110, 146, 20, 43))]
    market = [dict(k=k, n=D.C[k][0], t=D.C[k][1], q=Q[k]) for k in MARKET_KEYS if k in Q]
    adata = dict(asOf="2026-09-30", target=target, supplyUrl=links["atlas"]["companion"], quotesUrl=links["atlas"]["quotes"],
                 quotesMeta=qmeta, repoUrl=REPO_URL, items=pts, sources=asources, flows=flows, builders=A.BUILDERS, labs=labs,
                 antSchedule=[list(x) for x in A.ANT_SCHEDULE], collectors=A.COLLECTORS, regions=aregions, labSigned=lab_signed,
                 market=market, devs=dev_payload(dev, "atlas"), siteUrl=SITE_URL, desk=desk_config("atlas") if gh else None)
    with open(os.path.join(ROOT, "src", "atlas", "template.html")) as f:
        atpl = f.read()
    atlas_html = atpl.replace("__DATA__", dump(adata)).replace("__GEO__", dump(g))

    if gh:
        out1 = os.path.join(ROOT, "site", "index.html"); out2 = os.path.join(ROOT, "site", "investment-atlas", "index.html")
        os.makedirs(os.path.dirname(out2), exist_ok=True)
        open(out1, "w").write(full_document(supply_html, '<script src="desk.js" defer></script>'))
        open(out2, "w").write(full_document(atlas_html, '<script src="../desk.js" defer></script>'))
        open(os.path.join(ROOT, "site", ".nojekyll"), "w").write("")
        shutil.copyfile(os.path.join(ROOT, "src", "common", "desk.js"), os.path.join(ROOT, "site", "desk.js"))
        os.makedirs(os.path.join(ROOT, "site", "data"), exist_ok=True)
        with open(os.path.join(ROOT, "site", "data", "build.json"), "w") as f:
            json.dump(dict(built=dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                           warnings=problems, entries=len(dev["entries"]), upcoming=len(dev["upcoming"])), f, ensure_ascii=False)
    else:
        d = os.path.join(ROOT, "dist", "artifact"); os.makedirs(d, exist_ok=True)
        out1 = os.path.join(d, "ai-supply-chain-atlas.html"); out2 = os.path.join(d, "ai-investment-atlas.html")
        open(out1, "w").write(supply_html); open(out2, "w").write(atlas_html)
    print(f"built {target}: {os.path.relpath(out1, ROOT)} ({len(supply_html)//1024} KB), {os.path.relpath(out2, ROOT)} ({len(atlas_html)//1024} KB);"
          f" {len(dev['entries'])} developments, {len(items)} atlas items, {len(sites)} sites; live quotes: {'yes' if qmeta else 'no'}")
    for p in problems:
        print("  warning:", p)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["github", "artifact"], default="github")
    ap.add_argument("--quotes", default=os.path.join(ROOT, "site", "data", "quotes.json"))
    ap.add_argument("--lenient", action="store_true", help="skip broken developments instead of failing (used in CI)")
    a = ap.parse_args()
    try:
        build(a.target, a.quotes, a.lenient)
    except BuildError as e:
        print("BUILD FAILED\n" + str(e)); sys.exit(1)
