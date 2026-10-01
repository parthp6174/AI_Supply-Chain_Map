"""Equal Earth projection for the atlas maps.

`proj(lon, lat)` places points on the 1000-unit-wide map. `load()` returns the precomputed country outlines in
world_geo.json, so a normal build needs only numpy. To regenerate the outlines from Natural Earth:

    git clone --depth 1 --filter=blob:none --sparse https://github.com/nvkelso/natural-earth-vector ne
    git -C ne sparse-checkout set --no-cone /geojson/ne_50m_admin_0_countries.geojson /geojson/ne_50m_admin_1_states_provinces_lakes.geojson
    NE_DIR=ne/geojson/ python src/common/geo.py --regenerate
"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NE = os.environ.get("NE_DIR", os.path.join(HERE, "ne", "geojson")) + os.sep
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
M = math.sqrt(3) / 2
LAT_MIN, LAT_MAX = -57.0, 83.7
W = 1000.0


def ee_raw(lon, lat):
    lam = np.radians(lon); phi = np.radians(lat)
    th = np.arcsin(M * np.sin(phi)); t2 = th * th; t6 = t2 * t2 * t2
    x = lam * np.cos(th) / (M * (A1 + 3 * A2 * t2 + t6 * (7 * A3 + 9 * A4 * t2)))
    y = th * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
    return x, y

XMAX, _ = ee_raw(np.array([180.0]), np.array([0.0])); XMAX = float(XMAX[0])
_, YTOP = ee_raw(np.array([0.0]), np.array([LAT_MAX])); YTOP = float(YTOP[0])
_, YBOT = ee_raw(np.array([0.0]), np.array([LAT_MIN])); YBOT = float(YBOT[0])
S = W / (2 * XMAX)
H = round((YTOP - YBOT) * S, 1)


def proj(lon, lat):
    lon = np.asarray(lon, float); lat = np.clip(np.asarray(lat, float), LAT_MIN, LAT_MAX)
    x, y = ee_raw(lon, lat)
    return (x + XMAX) * S, (YTOP - y) * S


def dp(pts, tol):
    """Douglas-Peucker on an (n,2) array; keeps first and last."""
    n = len(pts)
    if n < 3:
        return pts
    keep = np.zeros(n, bool); keep[0] = keep[-1] = True
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        p, q = pts[a], pts[b]
        seg = pts[a + 1:b]
        d = q - p
        L = math.hypot(*d)
        if L == 0:
            dist = np.hypot(*(seg - p).T)
        else:
            dist = np.abs(d[0] * (seg[:, 1] - p[1]) - d[1] * (seg[:, 0] - p[0])) / L
        i = int(np.argmax(dist))
        if dist[i] > tol:
            k = a + 1 + i
            keep[k] = True
            stack.append((a, k)); stack.append((k, b))
    return pts[keep]


def ring_area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def fmt(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def ring_path(p):
    out = "M" + fmt(p[0, 0]) + " " + fmt(p[0, 1])
    for x, y in p[1:]:
        out += "L" + fmt(x) + " " + fmt(y)
    return out + "Z"


def geom_rings(g):
    if g["type"] == "Polygon":
        return [g["coordinates"]]
    if g["type"] == "MultiPolygon":
        return g["coordinates"]
    return []


def build_paths(features, tol, min_area, keep_small=()):
    out = []
    for f in features:
        props = f["properties"]
        code = props.get("ADM0_A3") or props.get("adm0_a3")
        parts = []
        for poly in geom_rings(f["geometry"]):
            for ri, ring in enumerate(poly):
                a = np.array(ring, float)
                if len(a) < 4:
                    continue
                x, y = proj(a[:, 0], a[:, 1])
                p = np.column_stack([x, y])
                # drop consecutive duplicates
                m = np.ones(len(p), bool); m[1:] = np.any(np.abs(np.diff(p, axis=0)) > 1e-6, axis=1)
                p = p[m]
                area = ring_area(p)
                if area < min_area and code not in keep_small:
                    continue
                q = dp(p, tol)
                if len(q) < 4:
                    if code in keep_small and len(p) >= 4:
                        q = p[:: max(1, len(p) // 6)]
                    else:
                        continue
                parts.append(ring_path(q))
        if parts:
            out.append((code, "".join(parts), props))
    return out


def ocean_outline(n=90):
    top = [proj(lo, LAT_MAX) for lo in np.linspace(-180, 180, n)]
    right = [proj(180, la) for la in np.linspace(LAT_MAX, LAT_MIN, n)]
    bot = [proj(lo, LAT_MIN) for lo in np.linspace(180, -180, n)]
    left = [proj(-180, la) for la in np.linspace(LAT_MIN, LAT_MAX, n)]
    pts = np.array([[float(x), float(y)] for x, y in top + right + bot + left])
    return ring_path(dp(pts, 0.05))


def build():
    world = json.load(open(NE + "ne_50m_admin_0_countries.geojson"))
    feats = [f for f in world["features"] if f["properties"]["ADM0_A3"] not in ("ATA",)]
    countries = build_paths(feats, tol=0.22, min_area=0.35, keep_small=("SGP", "BHR", "QAT", "HKG", "TWN", "ISR", "LUX"))
    st = json.load(open(NE + "ne_50m_admin_1_states_provinces_lakes.geojson"))
    us = [f for f in st["features"] if f["properties"].get("adm0_a3") == "USA"
          and f["properties"].get("name") not in ("Alaska", "Hawaii")]
    states = build_paths(us, tol=0.12, min_area=0.02)
    states_path = "".join(p for _, p, _ in states)
    return dict(w=W, h=H, ocean=ocean_outline(),
                countries=[dict(c=c, n=pr.get("NAME") or pr.get("ADMIN"), d=d) for c, d, pr in countries],
                states=states_path)


def load():
    with open(os.path.join(HERE, "world_geo.json")) as f:
        return json.load(f)


if __name__ == "__main__" and "--regenerate" in sys.argv:
    g = build()
    with open(os.path.join(HERE, "world_geo.json"), "w") as f:
        json.dump(g, f, separators=(",", ":"))
    print("wrote world_geo.json")
elif __name__ == "__main__":
    g = build()
    s = json.dumps(g, separators=(",", ":"))
    print("viewBox", g["w"], g["h"], "countries", len(g["countries"]), "bytes", len(s), "states bytes", len(g["states"]))
    x, y = proj(-99.73, 32.52); print("Abilene", float(x), float(y))
    x, y = proj(126.98, 37.57); print("Seoul", float(x), float(y))
