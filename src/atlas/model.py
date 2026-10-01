"""Payback model (mirrors the JS in the page) — used to sanity-check defaults."""
import data_items as D

YEARS_TO_2030 = 4.25  # Oct 2026 -> end of 2030


def crf(r, n):
    if r == 0:
        return 1.0 / n
    return r / (1 - (1 + r) ** -n)


def ant_annual_avg(y0=2026, y1=2031):
    """Average annual Anthropic commitment over calendar years y0..y1-1, each contract spread evenly over its term."""
    tot = 0.0
    for _, amt, s, e in D.ANT_SCHEDULE:
        rate = amt / (e - s)
        ov = max(0.0, min(e, y1) - max(s, y0))
        tot += rate * ov
    return tot / (y1 - y0)


def run(hurdle=0.10, mode="5yr", margin=0.60, credit=1.0, lab_share=0.50, short_share=0.60, short_life=5, long_life=20):
    if mode == "5yr":
        factor = crf(hurdle, 5)
    else:
        factor = short_share * crf(hurdle, short_life) + (1 - short_share) * crf(hurdle, long_life)
    out = []
    for b in D.BUILDERS:
        K = sum(b["capex"])
        Kai = K * b["share"]
        need = Kai * factor / margin
        gain = b["rev_now"] - b["rev_2023"]
        credited = gain * (credit if b["id"] in ("msft", "googl", "amzn", "meta") else 1.0)
        mult = need / credited
        growth = mult ** (1 / YEARS_TO_2030) - 1 if mult > 1 else 0.0
        fund = b["spend26"] / b["ocf"]
        out.append(dict(name=b["name"], K=K, Kai=Kai, need=need, base=credited, mult=mult, growth=growth, fund=fund))
    for l in D.LABS:
        annual = l["annual"] if l["annual"] else ant_annual_avg()
        need = annual / lab_share
        mult = need / l["rev_now"]
        growth = mult ** (1 / YEARS_TO_2030) - 1 if mult > 1 else 0.0
        out.append(dict(name=l["name"], K=l["commit"], Kai=annual, need=need, base=l["rev_now"], mult=mult, growth=growth, fund=annual / l["rev_now"]))
    return out


def verdict(mult, fund, lab=False):
    if mult <= 1.5 and fund <= 1.25 and not lab:
        return "Leading"
    if mult <= 2.0:
        return "On track"
    if mult <= 3.5:
        return "Must keep innovating"
    return "Needs a breakthrough"


if __name__ == "__main__":
    print("Anthropic avg annual 2026-2030:", round(ant_annual_avg(), 1))
    for y in range(2026, 2034):
        print(" ", y, round(ant_annual_avg(y, y + 1), 1))
    for label, kw in [("5-yr payback", {}), ("asset life", {"mode": "life"}), ("5yr credit 50%", {"credit": 0.5})]:
        rows = run(**kw)
        print("\n==", label)
        tb = sum(r["Kai"] for r in rows[:7]); nb = sum(r["need"] for r in rows[:7]); bb = sum(r["base"] for r in rows[:7])
        for r in rows:
            lab = r["name"] in ("OpenAI", "Anthropic")
            print(f"{r['name']:<16} K={r['K']:7.1f} Kai={r['Kai']:7.1f} need={r['need']:7.1f} base={r['base']:7.1f} x{r['mult']:5.2f} g={r['growth']*100:5.1f}% fund={r['fund']:4.2f}  {verdict(r['mult'], r['fund'], lab)}")
        print(f"BUILDERS gross K={sum(r['K'] for r in rows[:7]):.1f} Kai={tb:.1f} need={nb:.1f} base={bb:.1f}")
        print(f"LABS need={rows[7]['need']+rows[8]['need']:.1f} base={rows[7]['base']+rows[8]['base']:.1f}")
    tot = sum(x["amount"] or 0 for x in D.ITEMS)
    print("\nheadline total mapped:", round(tot, 1), "items with $:", sum(1 for x in D.ITEMS if x["amount"]))
    from collections import Counter
    print(Counter(x["cat"] for x in D.ITEMS), Counter(x["kind"] for x in D.ITEMS))
    print("countries:", len(set(x["country"] for x in D.ITEMS)))
    for c in ("compute", "chips", "funding"):
        print(c, round(sum(x["amount"] or 0 for x in D.ITEMS if x["cat"] == c), 1))
