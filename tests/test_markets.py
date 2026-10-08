#!/usr/bin/env python3
"""Tests for scripts/fetch_markets.py, the market-odds refresh. No network: Polymarket's answers are recorded below
in the shape its Gamma API returns (prices as JSON text inside the JSON, as the real API does).

    python tests/test_markets.py
"""
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import fetch_markets as F

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- " + str(detail)))


# recorded on 8 Oct 2026 (trimmed to the fields the script reads)
TAIWAN = {"id": "2382819", "question": "Will China blockade Taiwan in 2026?", "slug": "will-china-blockade-taiwan-by-in-2026",
          "endDate": "2027-01-01T04:59:00Z", "active": True, "closed": False, "outcomes": "[\"Yes\", \"No\"]",
          "outcomePrices": "[\"0.0335\", \"0.9665\"]", "volume": "405516.42825900007", "volumeNum": 405516.42825900007,
          "lastTradePrice": 0.034, "bestBid": 0.033, "bestAsk": 0.034, "oneWeekPriceChange": 0.0005}
HORMUZ = {"id": "2176270", "question": "Strait of Hormuz traffic returns to normal by December 31?", "endDate": "2027-01-01T04:59:00Z",
          "active": True, "closed": False, "outcomes": "[\"Yes\", \"No\"]", "outcomePrices": "[\"0.205\", \"0.795\"]",
          "volume": "13747749.834674994", "volumeNum": 13747749.834674994, "bestBid": 0.2, "bestAsk": 0.21, "oneWeekPriceChange": -0.01}
ODDS = {"drivers": [
    {"id": "tw_blockade", "markets": [{"src": "polymarket", "id": "2382819", "side": "yes"}, {"src": "polymarket", "id": "677407", "side": "yes"}]},
    {"id": "gulf_persist", "markets": [{"src": "polymarket", "id": "2176270", "side": "no"}]},
    {"id": "euv_halt"},
    {"id": "odd_one", "markets": [{"src": "kalshi", "id": "X"}, {"src": "polymarket", "id": "not-a-number"}, "junk"]}]}


def fake(answers):
    def fetch(url):
        key = url.rsplit("/", 1)[-1]
        a = answers.get(key)
        if isinstance(a, Exception):
            raise a
        if a is None:
            raise OSError("404")
        return a
    return fetch


def main():
    # which markets get read
    want = F.listed(ODDS)
    check("listed: Polymarket markets by numeric id, nothing else", sorted(want) == ["polymarket:2176270", "polymarket:2382819", "polymarket:677407"], sorted(want))

    # one market
    it = F.parse_market(TAIWAN)
    check("parse: the Yes price, read from the prices sent as text", it["yes"] == 0.0335 and it["question"] == TAIWAN["question"] and it["closed"] is False, it)
    check("parse: volume, closing date, weekly change, bid and ask", it["volume"] == 405516 and it["end"] == "2027-01-01T04:59:00Z" and it["week"] == 0.0005 and it["bid"] == 0.033 and it["ask"] == 0.034, it)
    flipped = dict(TAIWAN, outcomes="[\"No\", \"Yes\"]", outcomePrices="[\"0.9665\", \"0.0335\"]")
    check("parse: finds Yes wherever it is listed", F.parse_market(flipped)["yes"] == 0.0335)
    check("parse: also takes real lists", F.parse_market(dict(TAIWAN, outcomes=["Yes", "No"], outcomePrices=["0.2", "0.8"]))["yes"] == 0.2)
    bad = 0
    for broken in (dict(TAIWAN, outcomePrices="[\"1.7\", \"-0.7\"]"), dict(TAIWAN, outcomePrices="not json"), dict(TAIWAN, outcomes="[\"Trump\", \"Harris\"]"),
                   dict(TAIWAN, outcomePrices="[\"0.5\"]"), dict(TAIWAN, outcomePrices="[\"NaN\", \"0.5\"]"), "a string", None):
        try:
            F.parse_market(broken)
        except ValueError:
            bad += 1
    check("parse: refuses prices out of range, unreadable or missing, and markets that are not yes or no", bad == 7, bad)
    closed = F.parse_market(dict(TAIWAN, closed=True, outcomePrices="[\"0\", \"1\"]"))
    check("parse: a closed market keeps its final price", closed["closed"] is True and closed["yes"] == 0)

    # a full refresh
    data, ok = F.refresh(ODDS, None, fetch=fake({"2382819": TAIWAN, "2176270": HORMUZ}), now="2026-10-08T19:00:00Z")
    check("refresh: reads what it can and says what failed", ok == 2 and sorted(data["items"]) == ["polymarket:2176270", "polymarket:2382819"] and len(data["errors"]) == 1 and "677407" in data["errors"][0], data)
    check("refresh: stamps each price with the time it was read", data["items"]["polymarket:2382819"]["at"] == "2026-10-08T19:00:00Z" and data["fetched"] == "2026-10-08T19:00:00Z")
    later, ok2 = F.refresh(ODDS, data, fetch=fake({"2382819": dict(TAIWAN, outcomePrices="[\"0.04\", \"0.96\"]"), "2176270": OSError("timeout")}), now="2026-10-08T23:00:00Z")
    check("refresh: a market that fails keeps its last good price and the time of that price", ok2 == 1 and later["items"]["polymarket:2176270"]["yes"] == 0.205 and later["items"]["polymarket:2176270"]["at"] == "2026-10-08T19:00:00Z"
          and later["items"]["polymarket:2382819"]["yes"] == 0.04 and later["items"]["polymarket:2382819"]["at"] == "2026-10-08T23:00:00Z", later["items"])
    fewer = {"drivers": [ODDS["drivers"][0]]}
    pruned, _ = F.refresh(fewer, later, fetch=fake({"2382819": TAIWAN}), now="2026-10-09T00:00:00Z")
    check("refresh: a market no longer listed is dropped", "polymarket:2176270" not in pruned["items"], pruned["items"])
    junk, _ = F.refresh(ODDS, {"items": {"polymarket:2176270": "junk"}}, fetch=fake({}), now="2026-10-09T00:00:00Z")
    check("refresh: a damaged earlier file is ignored", junk["items"] == {} and len(junk["errors"]) == 3, junk)

    # the command, end to end, with no network: the file is written and the exit code shows the failure
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "markets_test_%d.json" % os.getpid())
    odds_tmp = tmp + ".odds.json"
    try:
        json.dump(ODDS, open(odds_tmp, "w"))
        F.get_json = fake({"2382819": TAIWAN, "2176270": HORMUZ, "677407": dict(TAIWAN, id="677407")})
        sys.argv = ["fetch_markets.py", "--odds", odds_tmp, "--out", tmp]
        code = F.main()
        got = json.load(open(tmp))
        check("command: writes the file and exits 0 when anything was read", code == 0 and len(got["items"]) == 3 and not os.path.exists(tmp + ".tmp"), (code, got))
        F.get_json = fake({})
        code = F.main()
        got = json.load(open(tmp))
        check("command: exits 1 when nothing could be read, keeping the last prices", code == 1 and len(got["items"]) == 3, (code, len(got["items"])))
    finally:
        for p in (tmp, odds_tmp):
            if os.path.exists(p):
                os.remove(p)

    # the real model file lists markets the script can read
    real = F.listed(json.load(open(os.path.join(ROOT, "data", "odds.json"), encoding="utf-8")))
    check("model file: lists at least one market, all by numeric id", len(real) >= 1 and all(k.split(":")[1].isdigit() for k in real), sorted(real))

    bad = [r for r in RESULTS if not r[1]]
    print("\n%d checks, %d failed" % (len(RESULTS), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
