#!/usr/bin/env python3
"""Read the forecasting-market prices that The Odds shows beside its drivers.

Each driver in data/odds.json can list markets that ask the same or a related question ("markets": [{"src":
"polymarket", "id": ...}]). This script asks Polymarket's public Gamma API for each one's current price and writes
site/data/markets.json:

    {"fetched": "2026-10-08T19:00:00Z",
     "items": {"polymarket:2382819": {"yes": 0.0335, "at": "2026-10-08T19:00:00Z", "question": "Will China blockade
               Taiwan in 2026?", "end": "2027-01-01T04:59:00Z", "closed": false, "volume": 405516, "week": 0.0005,
               "bid": 0.033, "ask": 0.034}},
     "errors": []}

"yes" is the price of the market's Yes side (0 to 1); the page turns it into the side the driver names. A market
that cannot be read this time keeps its last good price and the time it was read ("at"), so the page can say how
old it is; markets no longer listed are dropped.

    python scripts/fetch_markets.py                      # read every listed market
    python scripts/fetch_markets.py --out /tmp/m.json    # write somewhere else

Like the other refresh scripts it never stops the build. It exits with 1 only when markets are listed and none of
them could be read, so that the failure shows in the Actions run.
"""
import argparse, datetime as dt, json, os, sys, time, urllib.error, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
API = "https://gamma-api.polymarket.com/markets/{id}"
UA = "Mozilla/5.0 (compatible; Chokepoint/1.0; +https://github.com/Parthp6174/AI_Supply-Chain_Map)"


def now_iso():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def listed(odds):
    """{key: spec} for every market listed on a driver. Only Polymarket, by its numeric market id, for now."""
    out = {}
    for d in odds.get("drivers", []):
        for m in d.get("markets") or []:
            if isinstance(m, dict) and m.get("src") == "polymarket" and str(m.get("id", "")).isdigit():
                out["polymarket:" + str(m["id"])] = m
    return out


def number(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f and f not in (float("inf"), float("-inf")) else None


def parse_market(obj):
    """One Gamma market object -> the item kept for the page. Raises ValueError if it is not a usable yes/no price."""
    if not isinstance(obj, dict):
        raise ValueError("not a market object")
    def as_list(v):
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except ValueError:
                return None
        return v if isinstance(v, list) else None
    outcomes, prices = as_list(obj.get("outcomes")), as_list(obj.get("outcomePrices"))
    if not outcomes or not prices or len(outcomes) != len(prices):
        raise ValueError("no outcome prices")
    names = [str(o).strip().lower() for o in outcomes]
    if "yes" not in names:
        raise ValueError("not a yes-or-no market")
    yes = number(prices[names.index("yes")])
    if yes is None or not 0 <= yes <= 1:
        raise ValueError("price out of range")
    item = {"yes": round(yes, 4), "question": str(obj.get("question") or "")[:300], "closed": bool(obj.get("closed"))}
    end = str(obj.get("endDate") or "")
    if len(end) >= 10 and end[4] == "-":
        item["end"] = end[:20]
    vol = number(obj.get("volumeNum", obj.get("volume")))
    if vol is not None and vol >= 0:
        item["volume"] = round(vol)
    for key, out in (("oneWeekPriceChange", "week"), ("bestBid", "bid"), ("bestAsk", "ask")):
        v = number(obj.get(key))
        if v is not None and -1 <= v <= 1:
            item[out] = round(v, 4)
    return item


def get_json(url, tries=2):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, ValueError) as e:
            last = e
            if i + 1 < tries:
                time.sleep(2)
    raise last


def refresh(odds, previous, fetch=None, now=None):
    """Return (markets file, number read now). `previous` is the last file (or None); `fetch` reads one URL
    (default: get_json, looked up when called)."""
    fetch = fetch or get_json
    now = now or now_iso()
    want = listed(odds)
    old = (previous or {}).get("items") or {}
    items, errors, ok = {}, [], 0
    for key, spec in want.items():
        try:
            item = parse_market(fetch(API.format(id=spec["id"])))
            item["at"] = now
            items[key] = item
            ok += 1
        except Exception as e:      # one bad market never stops the others
            errors.append(f"{key}: {type(e).__name__}: {e}"[:200])
            if isinstance(old.get(key), dict) and "yes" in old[key]:
                items[key] = old[key]                      # keep the last good price, with the time it was read
    return {"fetched": now, "items": items, "errors": errors}, ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--odds", default=os.path.join(ROOT, "data", "odds.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "site", "data", "markets.json"))
    a = ap.parse_args()
    with open(a.odds, encoding="utf-8") as f:
        odds = json.load(f)
    previous = None
    if os.path.exists(a.out):
        try:
            with open(a.out, encoding="utf-8") as f:
                previous = json.load(f)
        except (OSError, ValueError):
            previous = None
    data, ok = refresh(odds, previous)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    tmp = a.out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, a.out)
    n = len(listed(odds))
    print(f"market odds: {ok} of {n} read now, {len(data['items'])} kept, {len(data['errors'])} errors")
    for e in data["errors"]:
        print("  " + e)
    return 1 if n and not ok else 0


if __name__ == "__main__":
    sys.exit(main())
