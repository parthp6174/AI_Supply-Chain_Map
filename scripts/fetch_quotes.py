#!/usr/bin/env python3
"""Refresh share prices (and, once a day, analyst targets) for every listed company in the atlas.

Data comes from Yahoo Finance through the open-source `yfinance` package. The result is written to
site/data/quotes.json, which both pages load in the browser and merge over their built-in 30 Sep 2026 snapshot.

    python scripts/fetch_quotes.py                       # prices now; targets if the last refresh is >20h old
    python scripts/fetch_quotes.py --targets always      # force a target/rating/earnings-date refresh
    python scripts/fetch_quotes.py --targets never       # prices only

The script never fails the build: anything it cannot fetch keeps its previous value (or the snapshot),
and the run summary lists what failed.
"""
import argparse, datetime as dt, json, math, os, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "supply"))
import supply_data as D  # noqa: E402

REC = {"strong_buy": "Strong Buy", "buy": "Buy", "hold": "Hold", "underperform": "Underperform",
       "sell": "Sell", "strong_sell": "Strong Sell"}


def now_iso():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def num(v):
    try:
        v = float(v)
        return None if math.isnan(v) or math.isinf(v) else v
    except (TypeError, ValueError):
        return None


def symbol_map():
    """company key -> Yahoo symbol. Registry tickers already use Yahoo's suffixes (.T, .KS, .TW, .TWO, .SZ, .SS, .HK, .DE, .AS, .PA)."""
    return {k: D.C[k][1] for k in D.Q if D.C.get(k) and D.C[k][1]}


def load_prev(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def fetch_prices(symmap):
    import pandas as pd
    import yfinance as yf
    syms = sorted(set(symmap.values()))
    df = yf.download(syms, period="7d", interval="1d", group_by="ticker", auto_adjust=False,
                     progress=False, threads=True)
    out = {}
    for k, sym in symmap.items():
        try:
            sub = df[sym] if isinstance(df.columns, pd.MultiIndex) else df
            closes = sub["Close"].dropna()
            if closes.empty:
                continue
            last = num(closes.iloc[-1])
            prev = num(closes.iloc[-2]) if len(closes) > 1 else None
            if last is None:
                continue
            out[k] = dict(px=round(last, 4), prev=round(prev, 4) if prev else None,
                          chg=round((last / prev - 1) * 100, 2) if prev else None,
                          date=closes.index[-1].date().isoformat())
        except Exception:
            continue
    return out


def fetch_targets(symmap, pause=0.35):
    import yfinance as yf
    out, failed = {}, []
    for k, sym in symmap.items():
        try:
            info = yf.Ticker(sym).info or {}
        except Exception:
            failed.append(sym)
            time.sleep(pause)
            continue
        tgt = num(info.get("targetMeanPrice"))
        n = info.get("numberOfAnalystOpinions")
        rec = REC.get(info.get("recommendationKey") or "")
        ets = info.get("earningsTimestampStart") or info.get("earningsTimestamp")
        nxt = None
        if ets:
            try:
                d = dt.datetime.fromtimestamp(int(ets), dt.timezone.utc).date()
                if d >= dt.date.today():
                    nxt = d.isoformat()
            except Exception:
                pass
        out[k] = dict(tgt=tgt, n=int(n) if isinstance(n, (int, float)) and n == n else None, rating=rec,
                      cur=info.get("currency"), mcap=num(info.get("marketCap")), next=nxt)
        time.sleep(pause)
    return out, failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "site", "data", "quotes.json"))
    ap.add_argument("--prev", default=None, help="previous quotes.json to carry forward (defaults to --out)")
    ap.add_argument("--targets", choices=["auto", "always", "never"], default="auto")
    ap.add_argument("--max-age-hours", type=float, default=20.0)
    a = ap.parse_args()

    prev = load_prev(a.prev or a.out) or {}
    pq = prev.get("quotes", {})
    symmap = symbol_map()
    quotes = {}
    # start from the previous live values, else the research snapshot
    for k in symmap:
        s = D.Q[k]
        base = dict(sym=symmap[k], px=s["px"], prev=None, chg=None, date=s["asof"], cur=s["cur"],
                    tgt=s["tgt"], n=s["n"], rating=s["rating"], next=s["next"], psrc="snapshot", tsrc="snapshot")
        base.update({kk: vv for kk, vv in pq.get(k, {}).items() if vv is not None})
        quotes[k] = base

    report = {"prices_ok": 0, "prices_failed": [], "targets_ok": 0, "targets_failed": []}
    try:
        live = fetch_prices(symmap)
    except Exception as e:  # network or Yahoo outage: keep previous values
        print("price fetch failed:", e)
        live = {}
    for k, v in live.items():
        quotes[k].update(v)
        quotes[k]["psrc"] = "yahoo"
    report["prices_ok"] = len(live)
    report["prices_failed"] = sorted(symmap[k] for k in symmap if k not in live)

    due = a.targets == "always"
    if a.targets == "auto":
        last = prev.get("targetsUpdated")
        try:
            age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(last.replace("Z", "+00:00"))).total_seconds() / 3600
        except Exception:
            age = 1e9
        due = age >= a.max_age_hours
    targets_updated = prev.get("targetsUpdated")
    if due:
        try:
            tg, tfail = fetch_targets(symmap)
        except Exception as e:
            print("target fetch failed:", e)
            tg, tfail = {}, sorted(symmap.values())
        for k, v in tg.items():
            q = quotes[k]
            px = q.get("px")
            tgt = v.get("tgt")
            # drop targets that cannot be right (stale or not split-adjusted): more than 3x or under 0.3x the price
            if tgt and px and not (0.3 <= tgt / px <= 3.0):
                tgt = None
            if tgt:
                q.update(tgt=round(tgt, 4), n=v.get("n") or q.get("n"), rating=v.get("rating") or q.get("rating"), tsrc="yahoo")
            if v.get("next"):
                q["next"] = v["next"]
            if v.get("mcap"):
                q["mcap"] = v["mcap"]
            if v.get("cur"):
                q["curCode"] = v["cur"]
        report["targets_ok"] = sum(1 for k in tg if tg[k].get("tgt"))
        report["targets_failed"] = tfail
        if tg:
            targets_updated = now_iso()

    for q in quotes.values():
        # a carried-forward target that is now more than 3x or under 0.3x the price (e.g. after a split) is dropped
        if q.get("tgt") and q.get("px") and not (0.3 <= q["tgt"] / q["px"] <= 3.0):
            q.update(tgt=None, tsrc="dropped")
        q["up"] = round((q["tgt"] / q["px"] - 1) * 100, 2) if q.get("tgt") and q.get("px") else None

    out = dict(updated=now_iso() if live else prev.get("updated"),
               pricesUpdated=now_iso() if live else prev.get("pricesUpdated"),
               targetsUpdated=targets_updated,
               source="Yahoo Finance via yfinance", quotes=quotes, report=report)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
