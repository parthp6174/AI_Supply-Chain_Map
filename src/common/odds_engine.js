/* Odds engine for Chokepoint's probability lab. Pure functions: no page, no storage, no network.
   Works in the browser (window.ODDS) and in Node (require / import), so the same code is tested and shipped.

   The idea in plain words
   -----------------------
   - A DRIVER is something uncertain. An "event" either happens or not (you give its probability). A "range" is a
     quantity (you give a low case that is undercut 1 time in 10, a central case, and a high case beaten 1 time in 10).
   - Drivers move together. Each driver gets a hidden bell-curve number; the hidden numbers are correlated the way
     you say, and each driver's outcome is read off its own hidden number. This keeps every driver's own probability
     exactly as you set it, whatever the correlations (a "Gaussian copula").
   - "If A happens, B's chance becomes X" and a correlation are two views of the same link; cond() and rhoForCond()
     convert between them.
   - A set of correlations can be impossible together (A moves with B, B with C, but A against C). repairCorr()
     finds the closest set that is possible and reports how much it had to change.
   - Each simulated future turns the drivers into shocks on the supply chain and cuts or boosts to demand, runs the
     chain's weakest-link model, and records what gets built. Thousands of futures give the odds.
   - A SITUATION ("suppose the blockade happens") keeps only the futures that match it, so everything linked to it
     shifts with it. Picking futures by their outcome ("the build-out falls 20% short") and asking what they have
     in common works the same way, in reverse.

   Two conventions to keep in mind
   - A positive correlation means two events tend to happen together, or an event goes with the high side of a
     range, or two ranges come in high together. Whether "high" is good or bad depends on the driver.
   - Outcomes are shares of the plan for the period: 1 = everything planned is delivered or ordered.
*/
(function(root, factory){
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.ODDS = factory();
})(typeof self !== "undefined" ? self : this, function(){
"use strict";

/* ---------------------------------------------------------------- random numbers */
/** Seeded generator (mulberry32): the same seed always gives the same futures, so a change in the results is
    caused by a change in the inputs and not by chance. Returns numbers strictly between 0 and 1. */
function rng(seed){
  let a = (seed >>> 0) || 1;
  return function(){
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return (((t ^ (t >>> 14)) >>> 0) + 0.5) / 4294967296;
  };
}

/* ---------------------------------------------------------------- the bell curve */
/** Chance that a standard normal number is below x (Hart's algorithm as given by West, 2005; about 15 digits). */
function normCdf(x){
  if (x !== x) return NaN;
  const a = Math.abs(x);
  let c;
  if (a > 37) c = 0;
  else {
    const e = Math.exp(-a * a / 2);
    if (a < 7.07106781186547){
      let b = 3.52624965998911e-02 * a + 0.700383064443688;
      b = b * a + 6.37396220353165; b = b * a + 33.912866078383; b = b * a + 112.079291497871;
      b = b * a + 221.213596169931; b = b * a + 220.206867912376;
      c = e * b;
      b = 8.83883476483184e-02 * a + 1.75566716318264;
      b = b * a + 16.064177579207; b = b * a + 86.7807322029461; b = b * a + 296.564248779674;
      b = b * a + 637.333633378831; b = b * a + 793.826512519948; b = b * a + 440.413735824752;
      c = c / b;
    } else {
      let b = a + 0.65;
      b = a + 4 / b; b = a + 3 / b; b = a + 2 / b; b = a + 1 / b;
      c = e / b / 2.506628274631;
    }
  }
  return x > 0 ? 1 - c : c;
}
const A_ = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00];
const B_ = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01];
const C_ = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00];
const D_ = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00];
/** The x below which a standard normal number falls with chance p (Acklam's algorithm; `refine` adds one
    correction step for full precision; sampling skips it). */
function normInv(p, refine){
  if (!(p > 0)) return p === 0 ? -Infinity : NaN;
  if (!(p < 1)) return p === 1 ? Infinity : NaN;
  let x;
  if (p < 0.02425){
    const q = Math.sqrt(-2 * Math.log(p));
    x = (((((C_[0] * q + C_[1]) * q + C_[2]) * q + C_[3]) * q + C_[4]) * q + C_[5]) / ((((D_[0] * q + D_[1]) * q + D_[2]) * q + D_[3]) * q + 1);
  } else if (p > 1 - 0.02425){
    const q = Math.sqrt(-2 * Math.log(1 - p));
    x = -(((((C_[0] * q + C_[1]) * q + C_[2]) * q + C_[3]) * q + C_[4]) * q + C_[5]) / ((((D_[0] * q + D_[1]) * q + D_[2]) * q + D_[3]) * q + 1);
  } else {
    const q = p - 0.5, r = q * q;
    x = (((((A_[0] * r + A_[1]) * r + A_[2]) * r + A_[3]) * r + A_[4]) * r + A_[5]) * q / (((((B_[0] * r + B_[1]) * r + B_[2]) * r + B_[3]) * r + B_[4]) * r + 1);
  }
  if (refine !== false){
    const e = normCdf(x) - p, u = e * Math.sqrt(2 * Math.PI) * Math.exp(x * x / 2);
    x = x - u / (1 + x * u / 2);
  }
  return x;
}

/** Chance that two standard normal numbers with correlation rho are below h and below k at the same time.
    Uses Phi(h)Phi(k) + (1/2pi) * integral from 0 to asin(rho) of exp(-(h^2 + k^2 - 2hk sin t) / (2 cos^2 t)) dt,
    integrated with adaptive Simpson's rule. Checked against SciPy in tests/test_engine.mjs. */
function bvnCdf(h, k, rho){
  if (h === -Infinity || k === -Infinity) return 0;
  if (h === Infinity) return normCdf(k);
  if (k === Infinity) return normCdf(h);
  if (rho >= 1) return normCdf(Math.min(h, k));
  if (rho <= -1) return Math.max(0, normCdf(h) + normCdf(k) - 1);
  const base = normCdf(h) * normCdf(k);
  if (rho === 0) return base;
  const hh = h * h + k * k, hk2 = 2 * h * k;
  const f = t => { const c = Math.cos(t); return Math.exp(-(hh - hk2 * Math.sin(t)) / (2 * c * c)); };
  const b = Math.asin(rho);
  const simpson = (lo, hi, flo, fmid, fhi, whole, tol, depth) => {
    const mid = (lo + hi) / 2, lm = (lo + mid) / 2, rm = (mid + hi) / 2, flm = f(lm), frm = f(rm);
    const left = (mid - lo) / 6 * (flo + 4 * flm + fmid), right = (hi - mid) / 6 * (fmid + 4 * frm + fhi);
    const delta = left + right - whole;
    if (depth <= 0 || Math.abs(delta) <= 15 * tol) return left + right + delta / 15;
    return simpson(lo, mid, flo, flm, fmid, left, tol / 2, depth - 1) + simpson(mid, hi, fmid, frm, fhi, right, tol / 2, depth - 1);
  };
  // integrate in a few panels so a sharp drop near the end of the range is not stepped over
  let total = 0;
  const panels = 8;
  for (let i = 0; i < panels; i++){
    const lo = b * i / panels, hi = b * (i + 1) / panels, flo = f(lo), fhi = f(hi), fmid = f((lo + hi) / 2);
    total += simpson(lo, hi, flo, fmid, fhi, (hi - lo) / 6 * (flo + 4 * fmid + fhi), 1e-12, 28);
  }
  return Math.min(1, Math.max(0, base + total / (2 * Math.PI)));
}

/* ---------------------------------------------------------------- links between two events */
/** Chance that both of two events happen, given each one's chance and the correlation of their hidden numbers. */
function both(pa, pb, rho){
  if (pa <= 0 || pb <= 0) return 0;
  if (pa >= 1) return pb;
  if (pb >= 1) return pa;
  return bvnCdf(normInv(pa), normInv(pb), rho);
}
/** "If A happens, the chance of B becomes ...": P(B | A). */
function cond(pa, pb, rho){ return pa > 0 ? both(pa, pb, rho) / pa : pb; }
/** Find the correlation at which f(rho) equals target, for an f that rises with rho. Returns
    {rho, reached, min, max}: `reached` is what f actually gives there, which differs from target only when target
    is outside what is possible (min..max, at correlations -0.999 and +0.999). */
function solveRho(f, target){
  const LIM = 0.999, lo0 = f(-LIM), hi0 = f(LIM);
  if (!(hi0 > lo0)) return {rho: 0, reached: f(0), min: lo0, max: hi0};
  if (target <= lo0) return {rho: -LIM, reached: lo0, min: lo0, max: hi0};
  if (target >= hi0) return {rho: LIM, reached: hi0, min: lo0, max: hi0};
  let lo = -LIM, hi = LIM;
  for (let i = 0; i < 44; i++){
    const mid = (lo + hi) / 2;
    if (f(mid) < target) lo = mid; else hi = mid;
  }
  const rho = (lo + hi) / 2;
  return {rho, reached: f(rho), min: lo0, max: hi0};
}
/** The correlation that makes "if A happens, the chance of B becomes target" true. See solveRho for the result. */
function rhoForCond(pa, pb, target){ return solveRho(r => cond(pa, pb, r), target); }
/** Middle value of B's hidden number across the futures in which A's hidden number is in its top `pa` share
    (A "happens", for an event with chance pa). Zero when the two are unrelated. */
function condMedian(pa, rho){
  if (!(pa > 0 && pa < 1) || !rho) return 0;
  const t = normInv(1 - pa), half = pa / 2;
  let lo = -9, hi = 9;
  for (let i = 0; i < 44; i++){
    const x = (lo + hi) / 2;
    if (normCdf(x) - bvnCdf(x, t, rho) < half) lo = x; else hi = x;      // chance that B is below x and A happens
  }
  return (lo + hi) / 2;
}
/** A link between two drivers in plain numbers. The condition is "A happens" (event) or "A comes in at or above
    its high case" (range, a 1-in-10 outcome); the reading is B's chance (event) or B's central case (range).
    Returns {when: "happens" | "high", pa, unit: "chance" | "value", base, given}: base is B on its own, given is B
    under the condition. */
function reading(a, b, rho){
  const isEv = a.kind === "event", pa = isEv ? a.p : 0.1, when = isEv ? "happens" : "high";
  if (b.kind === "event") return {when, pa, unit: "chance", base: b.p, given: cond(pa, b.p, rho)};
  return {when, pa, unit: "value", base: rangeValue(b, 0), given: rangeValue(b, condMedian(pa, rho))};
}
/** The correlation that makes reading(a, b, rho).given equal to target. See solveRho for the result. */
function rhoForReading(a, b, target){ return solveRho(r => reading(a, b, r).given, target); }

/* ---------------------------------------------------------------- correlation grids */
function identity(n){ const m = []; for (let i = 0; i < n; i++){ m.push(new Array(n).fill(0)); m[i][i] = 1; } return m; }
function copyM(a){ return a.map(r => r.slice()); }
/** Cholesky factor L (lower triangle, L·Lᵀ = a), or null if `a` is not a valid (positive-definite) grid. */
function cholesky(a){
  const n = a.length, L = identity(n);
  for (let i = 0; i < n; i++){
    for (let j = 0; j <= i; j++){
      let s = a[i][j];
      for (let k = 0; k < j; k++) s -= L[i][k] * L[j][k];
      if (i === j){ if (!(s > 1e-10)) return null; L[i][i] = Math.sqrt(s); }
      else L[i][j] = s / L[j][j];
    }
    for (let j = i + 1; j < n; j++) L[i][j] = 0;
  }
  return L;
}
/** Eigenvalues and eigenvectors of a symmetric matrix (cyclic Jacobi). Returns {values, vectors} with vectors in columns. */
function jacobiEigen(a){
  const n = a.length, A = copyM(a), V = identity(n);
  for (let sweep = 0; sweep < 100; sweep++){
    let off = 0;
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) off += A[i][j] * A[i][j];
    if (off < 1e-22) break;
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++){
      if (Math.abs(A[p][q]) < 1e-300) continue;
      const theta = (A[q][q] - A[p][p]) / (2 * A[p][q]);
      const t = (theta >= 0 ? 1 : -1) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
      const c = 1 / Math.sqrt(t * t + 1), s = t * c;
      for (let k = 0; k < n; k++){ const akp = A[k][p], akq = A[k][q]; A[k][p] = c * akp - s * akq; A[k][q] = s * akp + c * akq; }
      for (let k = 0; k < n; k++){ const apk = A[p][k], aqk = A[q][k]; A[p][k] = c * apk - s * aqk; A[q][k] = s * apk + c * aqk; }
      for (let k = 0; k < n; k++){ const vkp = V[k][p], vkq = V[k][q]; V[k][p] = c * vkp - s * vkq; V[k][q] = s * vkp + c * vkq; }
    }
  }
  return {values: A.map((r, i) => r[i]), vectors: V};
}
function projectPsd(a, floor){
  const n = a.length, {values, vectors} = jacobiEigen(a), out = identity(n);
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++){
    let s = 0;
    for (let k = 0; k < n; k++) s += vectors[i][k] * Math.max(values[k], floor) * vectors[j][k];
    out[i][j] = s;
  }
  return out;
}
/** Closest valid correlation grid to `a` (Higham's alternating projections), with a small floor on the
    eigenvalues so the result can always be sampled from. */
function nearestCorr(a){
  const n = a.length;
  let Y = copyM(a), dS = identity(n).map(r => r.map(() => 0));
  for (let it = 0; it < 200; it++){
    const R = Y.map((r, i) => r.map((v, j) => v - dS[i][j]));
    const X = projectPsd(R, 0);
    dS = X.map((r, i) => r.map((v, j) => v - R[i][j]));
    let move = 0;
    const Yn = X.map((r, i) => r.map((v, j) => i === j ? 1 : v));
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) move = Math.max(move, Math.abs(Yn[i][j] - Y[i][j]));
    Y = Yn;
    if (move < 1e-10) break;
  }
  // make it strictly usable: lift tiny or negative eigenvalues, then rescale back to ones on the diagonal
  const P = projectPsd(Y, 1e-6), out = identity(n);
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) out[i][j] = i === j ? 1 : (P[i][j] + P[j][i]) / 2 / Math.sqrt(P[i][i] * P[j][j]);
  return out;
}
/** Build the full grid from a list of pairs and repair it if the pairs cannot all hold together.
    Returns {matrix, L, changed, maxDiff, worst: [idA, idB] | null}. */
function repairCorr(ids, pairs){
  const n = ids.length, at = new Map(ids.map((d, i) => [d, i])), M = identity(n);
  for (const [a, b, r] of pairs || []){
    const i = at.get(a), j = at.get(b);
    if (i == null || j == null || i === j) continue;
    const v = Math.max(-0.999, Math.min(0.999, +r || 0));
    M[i][j] = v; M[j][i] = v;
  }
  let L = cholesky(M);
  if (L) return {matrix: M, L, changed: false, maxDiff: 0, worst: null};
  const fixed = nearestCorr(M);
  L = cholesky(fixed);
  let maxDiff = 0, worst = null;
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++){
    const d = Math.abs(fixed[i][j] - M[i][j]);
    if (d > maxDiff){ maxDiff = d; worst = [ids[i], ids[j]]; }
  }
  return {matrix: fixed, L, changed: true, maxDiff, worst};
}

/* ---------------------------------------------------------------- drivers */
const Z10 = 1.2815515655446004;                      // the bell-curve value exceeded 1 time in 10
/** Value of a range driver for a hidden number z: `mid` at z = 0, `low` at the 1-in-10 low point, `high` at the
    1-in-10 high point, straight lines of different slope on each side (a "split normal"), clamped to min/max. */
function rangeValue(d, z){
  const v = d.mid + z * (z < 0 ? (d.mid - d.low) : (d.high - d.mid)) / Z10;
  return Math.min(d.max == null ? Infinity : d.max, Math.max(d.min == null ? -Infinity : d.min, v));
}
/** What a range driver's value means for a link or a buyer group: 1 at `base` (default 100), moving `k` for one
    (default 1) with the value. A value of 90 against a base of 100 gives 0.9; with k = 0.5 it gives 0.95.
    `add` is added to the value first, so a driver written as "15% above plan" (add: 100) gives 1.15. */
function level(v, e){ return 1 + (e.k == null ? 1 : e.k) * ((v + (e.add || 0)) / (e.base || 100) - 1); }
/** Share of the outcome period that an effect starting `t` months from now covers. The period starts
    `period.start` months from now and lasts `period.len` months; `dur` (optional) is how long the effect lasts. */
function overlap(t, period, dur){
  const a = Math.max(t, period.start), end = period.start + period.len;
  const b = dur == null ? end : Math.min(end, t + dur);
  return Math.max(0, b - a) / period.len;
}
const EDITABLE = ["p", "low", "mid", "high", "sev"];
/** Apply the owner's numbers on top of the model's starting numbers. `beliefs` is
    {drivers: {id: {p, low, mid, high, sev}}, corr: [[a, b, rho], ...]}; pairs in beliefs replace the model's.
    Only those five numbers can be changed, anything that is not a number is ignored, and the result is kept
    sensible (a chance between 0 and 1, low <= central <= high), so an old or damaged saved set cannot break a run. */
function applyBeliefs(model, beliefs){
  const b = beliefs || {}, over = b.drivers || {};
  const drivers = model.drivers.map(d => {
    const o = Object.assign({sev: 1}, d), mine = over[d.id] || {};
    for (const k of EDITABLE){ const v = mine[k]; if (typeof v === "number" && isFinite(v)) o[k] = v; }
    if (o.kind === "event") o.p = Math.min(1, Math.max(0, o.p));
    else { o.low = Math.min(o.low, o.mid); o.high = Math.max(o.high, o.mid); }
    o.sev = Math.max(0, o.sev);
    return o;
  });
  const key = (x, y) => x < y ? x + "|" + y : y + "|" + x, pairs = new Map();
  for (const [x, y, r] of model.corr || []) pairs.set(key(x, y), [x, y, r]);
  for (const pr of Array.isArray(b.corr) ? b.corr : []) if (Array.isArray(pr) && typeof pr[2] === "number" && isFinite(pr[2])) pairs.set(key(pr[0], pr[1]), [pr[0], pr[1], pr[2]]);
  return {drivers, corr: [...pairs.values()]};
}
/** Turn a condition on drivers into tests. `where` is {driverId: true | false | "low" | "high" | [from, to]}:
    true / false = the event happens / does not; "low" / "high" = a range comes in at or below its low case / at or
    above its high case; [from, to] = a range lands between two values.
    Returns {tests: [[driverIndex, fn, condition]], unknown}. */
function compileWhere(drivers, where){
  const tests = [], unknown = [];
  for (const id of Object.keys(where || {})){
    const i = drivers.findIndex(d => d.id === id), w = where[id], d = drivers[i];
    if (i < 0){ unknown.push(id); continue; }
    if (w === true) tests.push([i, v => v > 0.5, w]);
    else if (w === false) tests.push([i, v => v <= 0.5, w]);
    else if (w === "low") tests.push([i, v => v <= d.low, w]);
    else if (w === "high") tests.push([i, v => v >= d.high, w]);
    else if (Array.isArray(w) && w.length === 2) tests.push([i, v => v >= w[0] && v <= w[1], w]);
    else unknown.push(id);
  }
  return {tests, unknown};
}
/** List what is wrong with a model definition (empty list = fine). */
function check(model){
  const out = [], nodes = new Set(model.graph.nodes.map(n => n.id)), ids = new Set();
  const segW = (model.demand || {}).segments || {}, segs = new Set(Object.keys(segW).concat(["all"]));
  const share = v => v >= 0 && v <= 1;
  for (const d of model.drivers){
    if (ids.has(d.id)) out.push("driver '" + d.id + "' is listed twice");
    ids.add(d.id);
    if (d.kind === "event"){
      if (!share(d.p)) out.push(d.id + ": probability must be between 0 and 1");
      if (d.window != null && !(d.window > 0)) out.push(d.id + ": window must be a number of months above 0");
      if (d.from != null && !(d.from >= 0 && (d.window == null || d.from < d.window))) out.push(d.id + ": 'from' must be 0 or more and before the end of the window");
    } else if (d.kind === "range"){
      if (!(d.low <= d.mid && d.mid <= d.high)) out.push(d.id + ": needs low <= central <= high");
      if ((d.min != null && !(d.min <= d.low)) || (d.max != null && !(d.max >= d.high))) out.push(d.id + ": min and max must enclose the low and high cases");
    } else out.push(d.id + ": kind must be 'event' or 'range'");
    if (d.sev != null && !(d.sev >= 0)) out.push(d.id + ": severity cannot be negative");
    for (const e of d.effects || []){
      if (e.t === "scen"){ if (!model.scen || !model.scen[e.id]) out.push(d.id + ": unknown scenario '" + e.id + "'"); }
      else if (e.t === "shock" || e.t === "ramp" || e.t === "ease"){ if (!nodes.has(e.node)) out.push(d.id + ": unknown link '" + e.node + "'"); }
      else if (e.t === "dem" || e.t === "demlvl"){ if (!segs.has(e.seg)) out.push(d.id + ": unknown buyer group '" + e.seg + "'"); }
      else out.push(d.id + ": unknown effect type '" + e.t + "'");
      if ((e.t === "ramp" || e.t === "demlvl") && d.kind !== "range") out.push(d.id + ": '" + e.t + "' needs a range driver");
      if ((e.t === "scen" || e.t === "shock" || e.t === "dem" || e.t === "ease") && d.kind !== "event") out.push(d.id + ": '" + e.t + "' needs an event driver");
      if (e.t === "shock" && !share(e.s)) out.push(d.id + ": a shock is a lost share between 0 and 1");
      if (e.t === "ease" && !share(e.f)) out.push(d.id + ": 'ease' needs f between 0 and 1 (the share of the shortfall that remains)");
      if (e.t === "dem" && !(e.m >= 0)) out.push(d.id + ": 'dem' needs m of 0 or more (what the group's orders are multiplied by)");
      if (e.timing != null && e.timing !== "window" && e.timing !== "until" && e.timing !== "full") out.push(d.id + ": timing must be 'window', 'until' or 'full'");
      if (e.t === "scen" && model.scen && model.scen[e.id]) for (const k of (e.only || []).concat(e.skip || [])) if (!((model.scen[e.id].h0 || {})[k] != null)) out.push(d.id + ": scenario '" + e.id + "' has no shock on '" + k + "'");
      if ((e.t === "ramp" || e.t === "demlvl") && ((e.base != null && !(e.base > 0)) || (e.k != null && !isFinite(e.k)) || (e.add != null && !isFinite(e.add)))) out.push(d.id + ": 'base' must be above 0, and 'k' and 'add' numbers");
      if (e.on != null && e.on !== "yes" && e.on !== "no") out.push(d.id + ": 'on' must be 'yes' or 'no'");
      if (e.dur != null && !(e.dur > 0)) out.push(d.id + ": dur must be a number of months above 0");
    }
  }
  const seen = new Set();
  for (const [a, b, r] of model.corr || []){
    const k = a < b ? a + "|" + b : b + "|" + a;
    if (!ids.has(a) || !ids.has(b)) out.push("link " + a + " - " + b + ": unknown driver");
    else if (a === b) out.push("link " + a + " - " + b + ": a driver cannot be linked to itself");
    else if (seen.has(k)) out.push("link " + a + " - " + b + ": listed twice");
    seen.add(k);
    if (!(r >= -1 && r <= 1)) out.push("link " + a + " - " + b + ": correlation must be between -1 and 1");
  }
  for (const n of model.graph.nodes) for (const inp of n.inputs) if (!nodes.has(inp[0])) out.push("link '" + n.id + "' takes input from unknown '" + inp[0] + "'");
  const outs = (model.graph.outputs || []).map(o => o.id);
  for (const o of model.graph.outputs || []) for (const mx of o.mix) if (!nodes.has(mx[0])) out.push("output '" + o.id + "' uses unknown link '" + mx[0] + "'");
  if (model.supplyOutput != null && !outs.includes(model.supplyOutput)) out.push("supplyOutput '" + model.supplyOutput + "' is not one of the outputs");
  const tot = Object.values(segW).reduce((a, v) => a + v, 0);
  if (Object.keys(segW).length && Math.abs(tot - 1) > 1e-6) out.push("buyer groups must add up to 1 (they add up to " + tot + ")");
  if (model.period && !(model.period.len > 0 && model.period.start >= 0)) out.push("period needs start of 0 or more and len above 0 (months)");
  return out;
}

/** Turn the model file (data/odds.json, written with dates and readable fields) and the chain
    (supply_model.export_graph()) into the model that simulate() takes. Deadlines and start dates become months
    counted from the file's `asOf` date; an effect with "base": "mid" is measured against the driver's starting
    central case; everything else on a driver (label, question, note ...) is carried along. */
function assemble(file, chain){
  const MONTH = 86400000 * 365.25 / 12, months = (a, b) => (Date.parse(b) - Date.parse(a)) / MONTH;
  const drivers = file.drivers.map(d => {
    const o = Object.assign({}, d);
    if (d.kind === "event"){
      if (d.window == null && d.deadline) o.window = Math.max(0.1, months(file.asOf, d.deadline));
      if (d.from == null && d.starts) o.from = Math.max(0, months(file.asOf, d.starts));
    }
    // "base": "mid" ties an effect to the driver's starting central case, which is what the plan assumes
    o.effects = (d.effects || []).map(e => e.base === "mid" ? Object.assign({}, e, {base: d.mid}) : e);
    return o;
  });
  return {graph: chain.graph, scen: chain.scen, drivers, corr: (file.links || []).map(l => [l.a, l.b, l.rho]),
          demand: {segments: Object.fromEntries((file.buyers || []).map(b => [b.id, b.share]))},
          period: {start: Math.max(0, months(file.asOf, file.period.from)), len: file.period.months},
          supplyOutput: file.supplyOutput || "campus"};
}

/* ---------------------------------------------------------------- the supply chain (weakest link) */
/** Prepare the chain for fast repeated runs. Mirrors src/supply/supply_model.py: a link delivers the lesser of
    its own availability and, for each group of inputs, the weighted share those inputs deliver. */
function compileGraph(graph){
  const ids = graph.nodes.map(n => n.id), at = new Map(ids.map((d, i) => [d, i])), byId = new Map(graph.nodes.map(n => [n.id, n]));
  const order = [], seen = new Set();
  const visit = id => { if (seen.has(id)) return; seen.add(id); for (const inp of byId.get(id).inputs) visit(inp[0]); order.push(at.get(id)); };
  ids.forEach(visit);
  const groups = graph.nodes.map(n => {
    const g = new Map();
    for (const [src, grp, w, p] of n.inputs){
      if (w === 0) continue;
      const key = grp || "_" + src;
      if (!g.has(key)) g.set(key, {items: [], other: (graph.other || {})[n.id + "|" + key] || 0, tw: 0});
      g.get(key).items.push({s: at.get(src), w, p});
    }
    const list = [...g.values()];
    for (const x of list) x.tw = x.items.reduce((a, it) => a + it.w, 0) + x.other;
    return list;
  });
  const outputs = (graph.outputs || []).map(o => ({id: o.id, label: o.label, mix: o.mix.map(([id, w]) => [at.get(id), w])}));
  return {ids, at, order, groups, outputs, n: ids.length};
}
/** Delivered share for every link, given each link's own availability (1 = unharmed). `A` and `lim` are filled:
    lim[i] is the input that limits link i, or -1 when the link's own availability (or nothing) is the limit. */
function runChain(G, own, A, lim){
  for (const i of G.order){
    let m = 1, who = -1;
    for (const g of G.groups[i]){
      let sum = g.other, worst = -1, worstLoss = 0;
      for (const it of g.items){
        const loss = it.p * (1 - A[it.s]);
        sum += it.w * (1 - loss);
        if (it.w * loss > worstLoss){ worstLoss = it.w * loss; worst = it.s; }
      }
      const val = sum / g.tw;
      if (val < m){ m = val; who = worst; }
    }
    if (own[i] <= m){ A[i] = own[i]; if (lim) lim[i] = -1; }
    else { A[i] = m; if (lim) lim[i] = who; }
  }
  return A;
}
/** Follow the limiting inputs from link `i` back to the link whose own shortfall is the cause. */
function rootCause(lim, i){ let k = i, guard = 0; while (lim[k] >= 0 && guard++ < 1000) k = lim[k]; return k; }
/** One-off run for a plain set of shocks ({linkId: lost share}); returns {links: {id: delivered}, outputs: {id: delivered}}. */
function chainOnce(graph, shocks){
  const G = compileGraph(graph), own = new Float64Array(G.n).fill(1), A = new Float64Array(G.n);
  for (const k in shocks || {}) if (G.at.has(k)) own[G.at.get(k)] = 1 - shocks[k];
  runChain(G, own, A, null);
  const links = {}, outputs = {};
  G.ids.forEach((d, i) => { links[d] = A[i]; });
  for (const o of G.outputs) outputs[o.id] = o.mix.reduce((a, [i, w]) => a + A[i] * w, 0);
  return {links, outputs};
}

/* ---------------------------------------------------------------- simulation */
/* The model simulate() takes (assemble() builds it from data/odds.json and the chain):
     {graph, scen, drivers, corr: [[idA, idB, rho]], demand: {segments: {id: share}}, period: {start, len}, supplyOutput}
   Months are counted from today. A driver is
     {id, kind: "event", p, sev?, from?, window?, effects}   from..window = when it can start (default: now to the end of the period)
     {id, kind: "range", low, mid, high, min?, max?, effects}
   and each effect is one of
     {t: "scen", id, only?, skip?}   event: the scenario's first-12-month shocks times severity (all of them, only some, or all but some)
     {t: "shock", node, s}            event: the link loses share s times severity
     {t: "ease", node, f}             event: the link's shortfall is multiplied by f
     {t: "dem", seg, m}               event: the buyer group's orders are multiplied by m (seg "all" = every group)
     {t: "ramp", node, base?, k?, add?}     range: the link delivers level(value), at most 1
     {t: "demlvl", seg, base?, k?, add?}    range: the buyer group's orders are multiplied by level(value)
   Event effects also take
     on: "no"            apply when the event does not happen
     timing: "full"      the whole period (default)
             "window"    from a random start between `from` and `window` to the end of the period (or for `dur` months)
             "until"     already running, ending at a random point between `from` and `window`
*/
/** Run `n` futures. Options: {n = 10000, seed, beliefs, given, maxTries}.
    `given` keeps only the futures that match a situation, for example {tw_blockade: true} (see compileWhere for
    the form). The drivers linked to that situation shift the way the correlations say. Futures that do not match
    are thrown away before the chain is run, so a rare situation costs time, not accuracy; after `maxTries` draws
    (default 500 per future asked for) the run stops with fewer futures.
    Returns typed arrays per future plus the pieces needed to summarise them:
    {n (futures kept), asked, tried (draws made), chance (how likely the situation is under these numbers; 1
     without one), drivers, values: {driverId: Float32Array},
     out: {outputId | demand | built | tight: Float32Array}, binding: Int16Array, linkIds,
     corr: {changed, maxDiff, worst, matrix}, unknown (entries in `given` that could not be used)}.
    binding: -1 on plan, -2 demand is the limit, -3 the chain delivers its full plan but buyers want more than
    plan, otherwise the index (into linkIds) of the link whose own shortfall limits supply.
    "built" is the capacity actually added: the lesser of what the chain can supply (output `model.supplyOutput`,
    default "campus") and what buyers order. "tight" is demand divided by supply (above 1 = shortage). */
function simulate(model, opts){
  opts = opts || {};
  const n = opts.n || 10000, seed = opts.seed == null ? 20270101 : opts.seed;
  const {drivers, corr} = applyBeliefs(model, opts.beliefs);
  const m = drivers.length, ids = drivers.map(d => d.id);
  const rc = repairCorr(ids, corr), L = rc.L || identity(m);
  const G = compileGraph(model.graph), period = model.period || {start: 0, len: 12};
  const segNames = Object.keys((model.demand || {}).segments || {}), segW = segNames.map(s => model.demand.segments[s]);
  const segAt = new Map(segNames.map((s, i) => [s, i]));
  const supplyOut = G.outputs.find(o => o.id === (model.supplyOutput || "campus")) || G.outputs[G.outputs.length - 1];
  // thresholds and pre-resolved effects
  const isEvent = drivers.map(d => d.kind === "event");
  const thr = drivers.map(d => d.kind === "event" ? (d.p <= 0 ? Infinity : d.p >= 1 ? -Infinity : normInv(1 - d.p)) : 0);
  const fx = drivers.map(d => (d.effects || []).map(e => {
    const o = Object.assign({}, e);
    if (e.t === "scen") o.list = Object.entries(((model.scen || {})[e.id] || {}).h0 || {})
      .filter(([k]) => G.at.has(k) && (!e.only || e.only.includes(k)) && !(e.skip || []).includes(k)).map(([k, s]) => [G.at.get(k), s]);
    if (e.node != null) o.i = G.at.get(e.node);
    if (e.seg != null) o.g = e.seg === "all" ? -1 : segAt.get(e.seg);
    return o;
  }));
  const where = compileWhere(drivers, opts.given), tests = where.tests;
  // a situation that the owner's own numbers rule out: say so at once instead of drawing futures that cannot match
  const never = tests.some(([i, f]) => isEvent[i] && ((drivers[i].p <= 0 && !f(0)) || (drivers[i].p >= 1 && !f(1))));
  const maxTries = never ? 0 : (opts.maxTries || n * 500);
  // The drivers a situation is about are drawn first, so a future that does not match is dropped after a few
  // numbers instead of a full draw. If the situation includes events, the rarest of them is not left to luck at
  // all: its hidden number is drawn straight from the part of the bell curve where the condition holds.
  // Without a situation the order is the model's own, and a given seed always gives the same futures whatever
  // the beliefs (so two belief sets can be compared future by future).
  const condP = t => t[2] === true ? drivers[t[0]].p : 1 - drivers[t[0]].p;
  const evTests = tests.filter(t => isEvent[t[0]] && typeof t[2] === "boolean").sort((x, y) => condP(x) - condP(y));
  const first = [...new Set((evTests.length ? [evTests[0][0]] : []).concat(tests.map(t => t[0])))];
  let order = first.concat(ids.map((d, i) => i).filter(i => !first.includes(i))), lead = first.length, Lp = L;
  let direct = false, dYes = false, dP = 1;
  if (lead){
    Lp = cholesky(order.map(i => order.map(j => rc.matrix[i][j])));
    if (!Lp){ order = ids.map((d, i) => i); lead = m; Lp = L; }      // not expected; fall back to the plain order
    else if (evTests.length && !never){ direct = true; dYes = evTests[0][2]; dP = condP(evTests[0]); }
  }
  const testsAt = order.map((i, a) => direct && a === 0 ? [] : tests.filter(t => t[0] === i).map(t => t[1]));
  let values = {}, out = {};
  drivers.forEach(d => { values[d.id] = new Float32Array(n); });
  for (const o of G.outputs) out[o.id] = new Float32Array(n);
  out.demand = new Float32Array(n); out.built = new Float32Array(n); out.tight = new Float32Array(n);
  let binding = new Int16Array(n);
  const u1 = rng(seed), u2 = rng(seed ^ 0x9E3779B9);
  const eps = new Float64Array(m), vals = new Float64Array(m);
  const own = new Float64Array(G.n), ease = new Float64Array(G.n);
  const A = new Float64Array(G.n), lim = new Int32Array(G.n), seg = new Float64Array(segNames.length);
  const draw = a => {                                             // hidden number and outcome of the a-th driver in `order`
    const i = order[a];
    if (a === 0 && direct){                                       // the lower tail of chance dP, mirrored for "happens"
      const e = normInv(u1() * dP, false);
      eps[0] = dYes ? -e : e; vals[i] = dYes ? 1 : 0;
      return;
    }
    eps[a] = normInv(u1(), false);
    let s = 0; const La = Lp[a]; for (let b = 0; b <= a; b++) s += La[b] * eps[b];
    vals[i] = isEvent[i] ? (s > thr[i] ? 1 : 0) : rangeValue(drivers[i], s);
  };
  let r = 0, tried = 0;
  while (r < n && tried < maxTries){
    tried++;
    let a = 0, match = true;
    for (; a < lead && match; a++){
      draw(a);
      const fns = testsAt[a], v = vals[order[a]];
      for (let t = 0; t < fns.length; t++) if (!fns[t](v)){ match = false; break; }
    }
    if (!match) continue;
    for (; a < m; a++) draw(a);
    own.fill(1); ease.fill(1); seg.fill(1);
    for (let i = 0; i < m; i++){
      const d = drivers[i], start = u2(), v = vals[i], yes = isEvent[i] && v === 1;   // one timing draw per driver per future, used or not
      values[d.id][r] = v;
      for (const e of fx[i]){
        if (e.t === "ramp"){ own[e.i] *= Math.min(1, Math.max(0, level(v, e))); continue; }
        if (e.t === "demlvl"){ const k = Math.max(0, level(v, e)); if (e.g < 0) for (let g = 0; g < seg.length; g++) seg[g] *= k; else seg[e.g] *= k; continue; }
        if ((e.on === "no") === yes) continue;                    // effect fires on "yes" unless marked on: "no"
        let frac = 1;
        if (e.timing === "window" || e.timing === "until"){
          const w0 = d.from || 0, w1 = d.window == null ? period.start + period.len : d.window, at = w0 + start * Math.max(0, w1 - w0);
          frac = e.timing === "window" ? overlap(at, period, e.dur) : overlap(0, period, at);
        }
        if (e.t === "scen"){ for (const [k, s] of e.list) own[k] *= 1 - Math.min(1, s * d.sev * frac); }
        else if (e.t === "shock") own[e.i] *= 1 - Math.min(1, e.s * d.sev * frac);
        else if (e.t === "ease") ease[e.i] *= 1 - (1 - e.f) * frac;
        else if (e.t === "dem"){ const k = Math.max(0, 1 - (1 - e.m) * d.sev * frac); if (e.g < 0) for (let g = 0; g < seg.length; g++) seg[g] *= k; else seg[e.g] *= k; }
      }
    }
    for (let i = 0; i < G.n; i++) if (ease[i] !== 1) own[i] = 1 - (1 - own[i]) * ease[i];
    runChain(G, own, A, lim);
    for (const o of G.outputs){ let s = 0; for (const [i, w] of o.mix) s += A[i] * w; out[o.id][r] = s; }
    let dem = segNames.length ? 0 : 1;
    for (let g = 0; g < seg.length; g++) dem += segW[g] * seg[g];
    const sup = supplyOut ? out[supplyOut.id][r] : 1;
    out.demand[r] = dem; out.built[r] = Math.min(sup, dem); out.tight[r] = dem / Math.max(sup, 0.01);
    let b;
    if (sup < dem - 1e-9){
      if (sup >= 1 - 1e-9) b = -3;
      else {                                                       // blame the link that takes most off the supply output
        let node = -1, worst = 0;
        for (const [i, w] of supplyOut.mix){ const loss = w * (1 - A[i]); if (loss > worst){ worst = loss; node = i; } }
        b = node < 0 ? -1 : rootCause(lim, node);
      }
    } else b = dem < 1 - 1e-9 ? -2 : -1;
    binding[r] = b;
    r++;
  }
  if (r < n){
    for (const k in values) values[k] = values[k].subarray(0, r);
    for (const k in out) out[k] = out[k].subarray(0, r);
    binding = binding.subarray(0, r);
  }
  return {n: r, asked: n, tried, chance: tests.length ? (tried ? dP * r / tried : 0) : 1, drivers, values, out, binding,
          linkIds: G.ids, unknown: where.unknown,
          corr: {changed: rc.changed, maxDiff: rc.maxDiff, worst: rc.worst, matrix: rc.matrix}};
}
/** Only the futures of a finished run that match `where`: either a condition on drivers (see compileWhere) or a
    function of the future's number, for example r => res.out.built[r] < 0.8. Returns a result of the same shape
    (so every function below works on it), with `of` = how many futures it was picked from. */
function subset(res, where){
  let test, unknown = [];
  if (typeof where === "function") test = where;
  else {
    const c = compileWhere(res.drivers, where), cols = c.tests.map(([i, f]) => [res.values[res.drivers[i].id], f]);
    unknown = c.unknown;
    test = r => { for (let t = 0; t < cols.length; t++) if (!cols[t][1](cols[t][0][r])) return false; return true; };
  }
  const keep = [];
  for (let r = 0; r < res.n; r++) if (test(r)) keep.push(r);
  const pick = a => { const o = new a.constructor(keep.length); for (let i = 0; i < keep.length; i++) o[i] = a[keep[i]]; return o; };
  const values = {}, out = {};
  for (const k in res.values) values[k] = pick(res.values[k]);
  for (const k in res.out) out[k] = pick(res.out[k]);
  return {n: keep.length, of: res.of || res.n, asked: res.asked, tried: res.tried, chance: res.chance, drivers: res.drivers,
          values, out, binding: pick(res.binding), linkIds: res.linkIds, unknown, corr: res.corr};
}

/* ---------------------------------------------------------------- reading the results */
function mean(a){ let s = 0; for (let i = 0; i < a.length; i++) s += a[i]; return s / a.length; }
/** Values below which the given shares of futures fall, e.g. quantiles(arr, [0.1, 0.5, 0.9]). */
function quantiles(a, qs){
  if (!a.length) return qs.map(() => NaN);
  const s = Float64Array.from(a).sort();
  return qs.map(q => { const x = q * (s.length - 1), i = Math.floor(x), f = x - i; return i + 1 < s.length ? s[i] * (1 - f) + s[i + 1] * f : s[i]; });
}
/** Share of futures in which the value is below x. */
function probBelow(a, x){ let c = 0; for (let i = 0; i < a.length; i++) if (a[i] < x) c++; return c / a.length; }
/** Counts in equal bins between lo and hi (values outside go to the end bins). */
function histogram(a, lo, hi, bins){
  const h = new Array(bins).fill(0), w = (hi - lo) / bins;
  for (let i = 0; i < a.length; i++) h[Math.max(0, Math.min(bins - 1, Math.floor((a[i] - lo) / w)))]++;
  return h;
}
function summary(a){
  const q = quantiles(a, [0.05, 0.1, 0.5, 0.9, 0.95]);
  return {mean: mean(a), p05: q[0], p10: q[1], p50: q[2], p90: q[3], p95: q[4]};
}
/** How often each thing is the limit on what gets built: [{id, share, avgBuilt}], most frequent first.
    id is a link id, "demand" (buyers order less than the chain can supply), "plan" (the chain delivers its full
    plan but buyers want more) or "none" (on plan). */
function bindingTable(res){
  const acc = new Map();
  for (let r = 0; r < res.n; r++){
    const b = res.binding[r], id = b === -1 ? "none" : b === -2 ? "demand" : b === -3 ? "plan" : res.linkIds[b];
    const e = acc.get(id) || {id, count: 0, sum: 0};
    e.count++; e.sum += res.out.built[r]; acc.set(id, e);
  }
  return [...acc.values()].map(e => ({id: e.id, share: e.count / res.n, avgBuilt: e.sum / e.count})).sort((a, b) => b.share - a.share);
}
/** What matters most for an outcome: for each driver, how much of the spread in the outcome goes with it
    (`share`, 0 to 1; shares overlap when drivers are correlated) and the `swing`: for an event, the average outcome
    when it happens minus when it does not; for a range, the average outcome in the top fifth of the driver minus
    the bottom fifth. Sorted by share. */
function whatMatters(res, key){
  const y = res.out[key], n = res.n, my = mean(y);
  let vy = 0; for (let i = 0; i < n; i++) vy += (y[i] - my) * (y[i] - my);
  const rows = [];
  for (const d of res.drivers){
    const x = res.values[d.id];
    if (d.kind === "event"){
      let n1 = 0, s1 = 0, s0 = 0;
      for (let i = 0; i < n; i++){ if (x[i] > 0.5){ n1++; s1 += y[i]; } else s0 += y[i]; }
      const n0 = n - n1;
      if (!n1 || !n0 || !(vy > 0)){ rows.push({id: d.id, kind: d.kind, share: 0, swing: 0, pYes: n1 / n}); continue; }
      const m1 = s1 / n1, m0 = s0 / n0;
      rows.push({id: d.id, kind: d.kind, share: (n1 * (m1 - my) * (m1 - my) + n0 * (m0 - my) * (m0 - my)) / vy, swing: m1 - m0, pYes: n1 / n});
    } else {
      const mx = mean(x); let sxy = 0, sxx = 0;
      for (let i = 0; i < n; i++){ sxy += (x[i] - mx) * (y[i] - my); sxx += (x[i] - mx) * (x[i] - mx); }
      const [q20, q80] = quantiles(x, [0.2, 0.8]);
      let nl = 0, sl = 0, nh = 0, sh = 0;
      for (let i = 0; i < n; i++){ if (x[i] <= q20){ nl++; sl += y[i]; } if (x[i] >= q80){ nh++; sh += y[i]; } }
      rows.push({id: d.id, kind: d.kind, share: sxx > 0 && vy > 0 ? (sxy * sxy) / (sxx * vy) : 0, swing: nl && nh ? sh / nh - sl / nl : 0, pYes: null});
    }
  }
  return rows.sort((a, b) => b.share - a.share);
}
/** What a group of futures has in common. `sub` is a pick from `all` (see subset), for example the futures where
    the build-out falls short. For each driver: `all` and `picked` are how often it happens (event) or its average
    (range) in all futures and in the picked ones; `lift` is picked divided by all; `score` is the difference in
    units of the driver's usual spread. Sorted by the size of the score, so the most telling drivers come first. */
function profile(sub, all){
  const rows = [];
  for (const d of all.drivers){
    const a = all.values[d.id], ma = mean(a), mp = sub.n ? mean(sub.values[d.id]) : NaN;
    let va = 0; for (let i = 0; i < a.length; i++) va += (a[i] - ma) * (a[i] - ma);
    const sd = Math.sqrt(va / a.length);
    rows.push({id: d.id, kind: d.kind, all: ma, picked: mp, lift: ma > 0 ? mp / ma : null, score: sd > 0 && sub.n ? (mp - ma) / sd : 0});
  }
  return rows.sort((x, y) => Math.abs(y.score) - Math.abs(x.score));
}

return {rng, normCdf, normInv, bvnCdf, both, cond, rhoForCond, condMedian, reading, rhoForReading,
        cholesky, jacobiEigen, nearestCorr, repairCorr, rangeValue, level, overlap, applyBeliefs, compileWhere, check, assemble,
        compileGraph, runChain, rootCause, chainOnce, simulate, subset,
        mean, quantiles, probBelow, histogram, summary, bindingTable, whatMatters, profile, Z10};
});
