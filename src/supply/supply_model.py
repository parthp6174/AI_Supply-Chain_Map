"""Stress model (mirrors the page's JS) and network layout for the AI Supply Chain Atlas."""
import supply_data as D

NODE = {n["id"]: n for n in D.NODES}
TIER_IDX = {t: i for i, (t, _) in enumerate(D.TIERS)}


def topo():
    order, seen = [], set()
    def visit(i):
        if i in seen:
            return
        seen.add(i)
        for inp in NODE[i]["inputs"]:
            visit(inp[0])
        order.append(i)
    for n in D.NODES:
        visit(n["id"])
    return order


ORDER = topo()


def scenario_shocks(sc, h):
    """h = 0 (first 12 months) or 1 (by year 3)."""
    if sc.get("kind") == "compound":
        out = {}
        for sid in sc["combine"]:
            sub = next(s for s in D.SCEN if s["id"] == sid)
            for k, v in scenario_shocks(sub, h).items():
                out[k] = max(out.get(k, 0), v)
        for k, v in sc.get("extra", {}).items():
            out[k] = max(out.get(k, 0), v[h])
        return out
    out = {k: v[h] for k, v in sc.get("shocks", {}).items()}
    if h == 1:
        for k, v in sc.get("shocks3_extra", {}).items():
            out[k] = max(out.get(k, 0), v)
    return out


def avail(shocks):
    A = {}
    for i in ORDER:
        n = NODE[i]
        groups = {}
        for (src, g, w, p) in n["inputs"]:
            if w == 0:
                continue
            key = g or ("_" + src)
            groups.setdefault(key, []).append((src, w, p))
        m = 1.0
        for g, lst in groups.items():
            other = D.GROUP_OTHER.get((i, g), 0.0)
            tw = sum(w for _, w, _ in lst) + other
            val = (sum(w * (1 - p * (1 - A[s])) for s, w, p in lst) + other) / tw
            m = min(m, val)
        A[i] = min(1 - shocks.get(i, 0.0), m)
    return A


def outputs(A):
    return {o["id"]: sum(A[k] * w for k, w in o["mix"]) for o in D.OUTPUTS}


def export_graph(expected=False):
    """The chain and the scenarios as plain data for the JavaScript engine (src/common/odds_engine.js).
    With expected=True each scenario also carries this module's own results, so tests can compare the two."""
    graph = dict(nodes=[dict(id=n["id"], inputs=[list(x) for x in n["inputs"]]) for n in D.NODES],
                 other={f"{i}|{g}": v for (i, g), v in D.GROUP_OTHER.items()},
                 outputs=[dict(id=o["id"], label=o["label"], mix=[list(m) for m in o["mix"]]) for o in D.OUTPUTS])
    scen = {}
    for sc in D.SCEN:
        e = dict(kind=sc.get("kind", "supply"), h0=scenario_shocks(sc, 0), h1=scenario_shocks(sc, 1))
        if sc.get("cut"):
            e["cut"] = list(sc["cut"])
        if expected:
            e["expect"] = [dict(links=avail(e[h]), outputs=outputs(avail(e[h]))) for h in ("h0", "h1")]
        scen[sc["id"]] = e
    return dict(graph=graph, scen=scen)


# ---------------------------------------------------------------- layout
COLW, BOXW, BOXH, ROWH, PADX, TOP = 104, 92, 34, 42, 30, 44
SI_ROWS, PW_ROWS, LANE_GAP = 9, 3, 30


def layout():
    cols = {t: [] for t, _ in D.TIERS}
    for n in D.NODES:
        cols[n["tier"]].append(n["id"])
    si_top = TOP
    si_bot = si_top + SI_ROWS * ROWH
    pw_top = si_bot + LANE_GAP
    pw_bot = pw_top + PW_ROWS * ROWH
    pos = {}
    # initial order = data order; then barycenter sweeps on y within lane
    def place(col_ids, band_top, band_rows):
        k = len(col_ids)
        if k == 0:
            return
        span = band_rows * ROWH
        step = span / k
        for j, i in enumerate(col_ids):
            pos[i] = [None, band_top + step * (j + 0.5) - BOXH / 2]
    tiers = [t for t, _ in D.TIERS]
    lanes = {}
    for t in tiers:
        si = [i for i in cols[t] if NODE[i]["lane"] == "si"]
        pw = [i for i in cols[t] if NODE[i]["lane"] == "pw"]
        mx = [i for i in cols[t] if NODE[i]["lane"] == "mx"]
        lanes[t] = (si, pw, mx)
    outs = {i: [] for i in NODE}
    for n in D.NODES:
        for inp in n["inputs"]:
            outs[inp[0]].append(n["id"])

    def do_place():
        for ci, t in enumerate(tiers):
            si, pw, mx = lanes[t]
            place(si, si_top, SI_ROWS)
            place(pw, pw_top, PW_ROWS)
            if mx:
                if t == "campus":
                    # campus spans the silicon band; capital sits in the power band
                    pass
                else:
                    place(mx, si_top, SI_ROWS + PW_ROWS + LANE_GAP / ROWH)
            for i in cols[t]:
                if i in pos:
                    pos[i][0] = PADX + ci * COLW
        # campus column special
        ci = tiers.index("campus")
        pos["campus"] = [PADX + ci * COLW, si_top + 4]
        pos["capital"] = [PADX + ci * COLW, pw_top + (PW_ROWS * ROWH - BOXH) / 2]

    do_place()
    for sweep in range(8):
        for t in tiers:
            for lane in lanes[t]:
                if len(lane) < 2:
                    continue
                def bc(i):
                    nb = [x[0] for x in NODE[i]["inputs"]] + outs[i]
                    ys = [pos[x][1] for x in nb if x in pos]
                    return sum(ys) / len(ys) if ys else pos[i][1]
                lane.sort(key=bc)
        do_place()
    H = pw_bot + 12
    W = PADX + (len(tiers) - 1) * COLW + BOXW + 8
    boxes = {}
    for i, (x, y) in pos.items():
        h = BOXH
        if i == "campus":
            h = SI_ROWS * ROWH - 8
        boxes[i] = dict(x=round(x, 1), y=round(y, 1), w=BOXW, h=h)
    bands = dict(si=[si_top, si_bot], pw=[pw_top, pw_bot])
    return dict(w=W, h=H, boxes=boxes, bands=bands, colw=COLW, top=TOP)


if __name__ == "__main__":
    base = avail({})
    assert all(abs(v - 1) < 1e-9 for v in base.values())
    for sc in D.SCEN:
        for h in (0, 1):
            if sc.get("kind") == "demand":
                continue
            A = avail(scenario_shocks(sc, h))
            o = outputs(A)
            print(f"{sc['id']:<9} h{h}", "  ".join(f"{k}={v*100:5.1f}%" for k, v in o.items()))
    L = layout()
    print("layout", L["w"], L["h"])
