#!/usr/bin/env python3
"""Collect recent headlines for the news radar on the Update desk.

Runs Google News searches (last 7 days) for each topic in data/news_queries.json, drops obvious noise
(stock-pick listicles, market-research spam, the sources and title patterns listed in that file), groups
reports of the same story into one headline with its other sources, tags each with the topics that found
it and writes site/data/news.json. The page only shows these headlines; nothing reaches the development
log until someone adds it.

    python scripts/fetch_news.py                 # fetch if the last run is older than 3 hours
    python scripts/fetch_news.py --mode always   # fetch now
    python scripts/fetch_news.py --mode never    # keep the previous file
    python scripts/fetch_news.py --mode missing  # fetch only if there are no headlines yet (used on pushes)

Like the price script, it never fails the build: if every search fails, the previous headlines stay.
"""
import argparse, datetime as dt, email.utils, hashlib, json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UA = "Mozilla/5.0 (compatible; AI-Supply-Chain-Map/1.0; +https://github.com/Parthp6174/AI_Supply-Chain_Map)"
FEED = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


def now_utc():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso(d):
    return d.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def norm_title(t):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", t.lower())).strip()


def item_id(title):
    return hashlib.sha1(norm_title(title).encode()).hexdigest()[:12]


def parse_rss(raw):
    """Return [{t, src, srcUrl, u, d}] from a Google News RSS document."""
    root = ET.fromstring(raw)
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        src_el = item.find("source")
        src = (src_el.text or "").strip() if src_el is not None and src_el.text else ""
        src_url = (src_el.get("url") or "") if src_el is not None else ""
        if src and title.endswith(" - " + src):
            title = title[: -(len(src) + 3)].strip()
        if not title or not link.startswith(("https://", "http://")):
            continue
        try:
            d = email.utils.parsedate_to_datetime(item.findtext("pubDate") or "")
            if d.tzinfo is None:
                d = d.replace(tzinfo=dt.timezone.utc)
        except (TypeError, ValueError):
            continue
        out.append(dict(t=title, src=src, srcUrl=src_url if src_url.startswith(("https://", "http://")) else "", u=link, d=d))
    return out


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.5"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


STOP = set("""a an and are as at be been but by for from has have how in into is it its of on or over says said than
that the their this to up was were what when why will with after amid about more new now out vs via could would
may might just here there they them who whose which while""".split())


def tokens(title):
    """Distinctive words of a headline, with amounts normalised ("$15B" and "15 billion" match)."""
    t = title.lower().replace("\u2019", "'")
    t = re.sub(r"'s\b", "", t)
    t = re.sub(r"\$?(\d+(?:\.\d+)?)\s*(?:bn|b|billion)\b", r"\1 billion", t)
    t = re.sub(r"\$?(\d+(?:\.\d+)?)\s*(?:tn|trillion)\b", r"\1 trillion", t)
    t = re.sub(r"\$?(\d+(?:\.\d+)?)\s*(?:mn|m|million)\b", r"\1 million", t)
    return {w for w in re.findall(r"[a-z0-9]+(?:\.\d+)?", t) if w not in STOP and (len(w) >= 3 or w[0].isdigit())}


def same_story(a, b):
    shared = len(a & b)
    return shared >= 3 and shared / max(1, min(len(a), len(b))) >= 0.5


def noise_filter(cfg):
    sources = [s.lower() for s in cfg.get("skipSources", []) if s]
    pats = [re.compile(p, re.I) for p in cfg.get("skipTitles", [])]
    def is_noise(r):
        t = r["t"]
        return (len(re.findall(r"\w+", t)) < 4 or re.match(r"^(https?://|www\.)", t) is not None
                or any(s in r["src"].lower() or s in r["srcUrl"].lower() for s in sources) or any(p.search(t) for p in pats))
    return is_noise


def cluster(rows, cap):
    """Group reports of the same story. The earliest report gives a stable id; the most typical title leads."""
    groups = []
    for r in sorted(rows, key=lambda r: r["d"]):
        r["tok"] = tokens(r["t"])
        home = next((g for g in groups if any(same_story(r["tok"], m["tok"]) for m in g)), None)
        (home.append(r) if home else groups.append([r]))
    out = []
    for g in groups:
        lead = max(g, key=lambda m: (sum(len(m["tok"] & o["tok"]) for o in g if o is not m), m["d"]))
        topics = []
        for m in g:
            topics += [t for t in m["topics"] if t not in topics]
        others = sorted((m for m in g if m is not lead), key=lambda m: m["d"], reverse=True)
        out.append(dict(id=g[0]["id"], ids=[m["id"] for m in g], t=lead["t"], src=lead["src"], srcUrl=lead["srcUrl"], u=lead["u"],
                        d=iso(max(m["d"] for m in g)), first=iso(g[0]["d"]), topics=topics, n=len(g),
                        more=[dict(src=m["src"], u=m["u"]) for m in others[:5]]))
    out.sort(key=lambda r: r["d"], reverse=True)
    return out[:cap]


def collect(topics, days=10, per_query=10, cap=160, pause=1.0, fetcher=fetch, cfg=None):
    cutoff = now_utc() - dt.timedelta(days=days)
    is_noise = noise_filter(cfg or {})
    seen, report = {}, dict(queries=0, ok=0, failed=[], dropped=0)
    for t in topics:
        for q in t["queries"]:
            report["queries"] += 1
            try:
                rows = parse_rss(fetcher(FEED.format(q=urllib.parse.quote(q + " when:7d"))))
                report["ok"] += 1
            except Exception as e:  # network error, block or bad XML: skip this search
                report["failed"].append(f"{q}: {type(e).__name__}")
                rows = []
            rows = [r for r in rows if r["d"] >= cutoff]
            rows.sort(key=lambda r: r["d"], reverse=True)
            for r in rows[:per_query]:
                k = item_id(r["t"])
                if k in seen:
                    if t["id"] not in seen[k]["topics"]:
                        seen[k]["topics"].append(t["id"])
                    continue
                if is_noise(r):
                    report["dropped"] += 1
                    continue
                seen[k] = dict(id=k, t=r["t"], src=r["src"], srcUrl=r["srcUrl"], u=r["u"], d=r["d"], topics=[t["id"]])
            time.sleep(pause)
    items = cluster(list(seen.values()), cap)
    report["headlines"] = len(seen)
    report["items"] = len(items)
    return items, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["auto", "always", "never", "missing"], default="auto")
    ap.add_argument("--max-age-hours", type=float, default=3.0)
    ap.add_argument("--topics", default=os.path.join(ROOT, "data", "news_queries.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "site", "data", "news.json"))
    a = ap.parse_args()

    try:
        with open(a.out) as f:
            prev = json.load(f)
    except Exception:
        prev = None
    if a.mode == "never":
        print("news: skipped (mode never)"); return
    if a.mode == "missing" and prev and prev.get("items"):
        print("news: skipped, headlines already present"); return
    if a.mode == "auto" and prev and prev.get("updated"):
        try:
            age = (now_utc() - dt.datetime.fromisoformat(prev["updated"].replace("Z", "+00:00"))).total_seconds() / 3600
        except ValueError:
            age = 1e9
        if age < a.max_age_hours:
            print(f"news: skipped, last update {age:.1f} h ago"); return

    with open(a.topics) as f:
        cfg = json.load(f)
    topics = cfg["topics"]
    items, report = collect(topics, cfg=cfg)
    if not items and prev and prev.get("items"):
        prev["report"] = dict(report, note="every search failed; keeping the previous headlines")
        out = prev
    else:
        out = dict(updated=iso(now_utc()), source="Google News", days=10,
                   topics=[dict(id=t["id"], label=t["label"], links=t.get("links", {})) for t in topics],
                   items=items, report=report)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
    print("news:", json.dumps(report))


if __name__ == "__main__":
    main()
