#!/usr/bin/env python3
"""Collect recent headlines for the news radar on the Update desk.

Runs Google News searches (last 7 days) for each topic in data/news_queries.json, removes duplicates,
tags each headline with the topics that found it and writes site/data/news.json. The page only shows
these headlines; nothing reaches the development log until someone adds it.

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


def collect(topics, days=10, per_query=10, cap=160, pause=1.0, fetcher=fetch):
    cutoff = now_utc() - dt.timedelta(days=days)
    seen, report = {}, dict(queries=0, ok=0, failed=[])
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
                seen[k] = dict(id=k, t=r["t"], src=r["src"], srcUrl=r["srcUrl"], u=r["u"], d=iso(r["d"]), topics=[t["id"]])
            time.sleep(pause)
    items = sorted(seen.values(), key=lambda r: r["d"], reverse=True)[:cap]
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
        topics = json.load(f)["topics"]
    items, report = collect(topics)
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
