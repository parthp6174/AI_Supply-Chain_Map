// Tests for the odds engine (src/common/odds_engine.js). Run: node tests/test_engine.mjs
// No packages needed. One test calls python3 to compare the JavaScript supply-chain model with the Python one.
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs";

const require = createRequire(import.meta.url);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const O = require(path.join(ROOT, "src", "common", "odds_engine.js"));

let passed = 0;
const failed = [];
function check(name, ok, detail){
  if (ok) passed++; else failed.push(name + (detail === undefined ? "" : "  -- " + JSON.stringify(detail)));
  console.log((ok ? "PASS " : "FAIL ") + name);
}
const close = (a, b, tol) => Math.abs(a - b) <= tol;

// ---- the bell curve, against Python's math.erfc and SciPy's norm.ppf
const CDF = [[-8, 6.220960574271819e-16], [-5, 2.866515718791946e-07], [-3, 0.0013498980316300957], [-1.5, 0.06680720126885809], [-0.5, 0.3085375387259869], [0, 0.5], [0.25, 0.5987063256829237], [1, 0.8413447460685429], [2.5, 0.9937903346742238], [4, 0.9999683287581669], [6.5, 0.99999999995984]];
check("normCdf matches reference values", CDF.every(([x, v]) => Math.abs(O.normCdf(x) - v) <= 1e-14 + 1e-12 * v), CDF.map(([x, v]) => O.normCdf(x) - v));
const INV = [[1e-09, -5.9978070150076865], [1e-05, -4.264890793922825], [0.001, -3.090232306167813], [0.02, -2.053748910631823], [0.1, -1.2815515655446004], [0.3, -0.5244005127080409], [0.5, 0.0], [0.77, 0.7388468491852137], [0.95, 1.6448536269514722], [0.999, 3.090232306167813], [0.9999999, 5.199337582290661]];
check("normInv matches reference values", INV.every(([p, v]) => close(O.normInv(p), v, 1e-9)), INV.map(([p, v]) => O.normInv(p) - v));
check("normInv without the correction step is still close", INV.every(([p, v]) => close(O.normInv(p, false), v, 1e-6)));
check("normInv handles 0 and 1", O.normInv(0) === -Infinity && O.normInv(1) === Infinity);

// ---- two correlated bell curves, against SciPy's multivariate_normal.cdf
const BVN = [[0, 0, 0.5, 0.33333333333333337], [0, 0, -0.5, 0.16666666666666666], [1, -0.5, 0.3, 0.28313842024448094], [-1.2, 0.4, -0.7, 0.01784696384609044], [2, 2, 0.9, 0.9678609922306609], [-2, -2, 0.9, 0.013361256127019328], [-2.5, -1, 0.95, 0.006209659864737538], [0.3, 0.31, 0.99, 0.5982606497310639], [1.5, -1.5, -0.99, 0.007299611227271684], [-3, -3, 0.2, 1.1434588610970131e-05], [0.8, -2.2, 0.6, 0.013873223404474833], [-0.1, 0.1, 0.999, 0.4601721485295333], [2.3, -0.4, -0.85, 0.3338597840338507], [-1.6449, -1.6449, 0.5, 0.0121877918026142], [-1.2816, -0.8416, 0.7, 0.0689955553794398]];
const bvnErr = BVN.map(([h, k, r, v]) => Math.abs(O.bvnCdf(h, k, r) - v));
check("bvnCdf matches SciPy on 15 cases (worst error " + Math.max(...bvnErr).toExponential(1) + ")", Math.max(...bvnErr) < 2e-7, bvnErr);
check("bvnCdf: no correlation is the product", close(O.bvnCdf(0.7, -1.1, 0), O.normCdf(0.7) * O.normCdf(-1.1), 1e-15));
check("bvnCdf: closed form at the centre", [-0.9, -0.3, 0.2, 0.8].every(r => close(O.bvnCdf(0, 0, r), 0.25 + Math.asin(r) / (2 * Math.PI), 1e-10)));
check("bvnCdf: perfect correlation limits", close(O.bvnCdf(0.4, 1.3, 1), O.normCdf(0.4), 1e-15) && close(O.bvnCdf(0.4, 1.3, -1), O.normCdf(0.4) + O.normCdf(1.3) - 1, 1e-15));
check("bvnCdf: symmetric in its two arguments", close(O.bvnCdf(-0.6, 1.9, 0.45), O.bvnCdf(1.9, -0.6, 0.45), 1e-12));

// ---- links between two events
check("both: independent events multiply", close(O.both(0.2, 0.35, 0), 0.07, 1e-12));
check("cond: positive correlation raises the chance, negative lowers it", O.cond(0.1, 0.2, 0.5) > 0.2 && O.cond(0.1, 0.2, -0.5) < 0.2);
check("cond is consistent both ways (Bayes)", close(O.cond(0.1, 0.3, 0.4) * 0.1, O.cond(0.3, 0.1, 0.4) * 0.3, 1e-10));
{
  const r = O.rhoForCond(0.15, 0.25, 0.6);
  check("rhoForCond finds the correlation for a target", close(r.reached, 0.6, 1e-9) && close(O.cond(0.15, 0.25, r.rho), 0.6, 1e-9), r);
  const back = O.rhoForCond(0.15, 0.25, O.cond(0.15, 0.25, -0.37));
  check("rhoForCond undoes cond", close(back.rho, -0.37, 1e-6), back);
  const imp = O.rhoForCond(0.5, 0.1, 0.9);     // B has a 10% chance; given A (50%) it can be at most 20%
  check("rhoForCond reports what is reachable when the target is impossible", imp.reached < 0.21 && imp.rho > 0.99 && close(imp.max, imp.reached, 1e-12), imp);
}

// ---- correlation grids
{
  const bad = [[1, 0.9, 0.9], [0.9, 1, -0.9], [0.9, -0.9, 1]];
  check("cholesky rejects an impossible grid", O.cholesky(bad) === null);
  const fixed = O.nearestCorr(bad), ev = O.jacobiEigen(fixed).values;
  check("nearestCorr returns a usable grid", fixed.every((r, i) => close(r[i], 1, 1e-12)) && fixed.every((r, i) => r.every((v, j) => close(v, fixed[j][i], 1e-12))) && Math.min(...ev) > 0 && O.cholesky(fixed) !== null, ev);
  const good = [[1, 0.3, -0.2], [0.3, 1, 0.5], [-0.2, 0.5, 1]];
  const rep = O.repairCorr(["a", "b", "c"], [["a", "b", 0.3], ["a", "c", -0.2], ["b", "c", 0.5]]);
  check("repairCorr leaves a valid grid alone", !rep.changed && rep.maxDiff === 0 && JSON.stringify(rep.matrix) === JSON.stringify(good));
  const rep2 = O.repairCorr(["a", "b", "c"], [["a", "b", 0.9], ["a", "c", 0.9], ["b", "c", -0.9]]);
  check("repairCorr repairs an impossible grid and names the worst pair", rep2.changed && rep2.maxDiff > 0.05 && Array.isArray(rep2.worst) && rep2.L !== null, rep2.maxDiff);
  const e = O.jacobiEigen([[2, 1], [1, 2]]).values.slice().sort();
  check("jacobiEigen on a known matrix", close(e[0], 1, 1e-12) && close(e[1], 3, 1e-12), e);
}

// ---- range drivers and timing
{
  const d = {low: 70, mid: 90, high: 100, min: 0, max: 110};
  check("rangeValue hits low, central and high at the 1-in-10 points", close(O.rangeValue(d, -O.Z10), 70, 1e-9) && O.rangeValue(d, 0) === 90 && close(O.rangeValue(d, O.Z10), 100, 1e-9));
  check("rangeValue respects min and max", O.rangeValue(d, -9) === 0 && O.rangeValue(d, 9) === 110);
  const per = {start: 3, len: 12};
  check("overlap: before, during and after the year", O.overlap(0, per) === 1 && close(O.overlap(9, per), 0.5, 1e-12) && O.overlap(15, per) === 0 && close(O.overlap(1, per, 5), 0.25, 1e-12));
}

// ---- the supply chain: JavaScript against the Python model, every link, every scenario, both horizons
const py = "import json,sys; sys.path.insert(0,'src/supply'); import supply_model as M; print(json.dumps(M.export_graph(expected=True)))";
const FX = JSON.parse(execFileSync("python3", ["-c", py], {cwd: ROOT, encoding: "utf8", maxBuffer: 1 << 26}));
{
  let worst = 0, n = 0;
  for (const [id, sc] of Object.entries(FX.scen)) for (const h of [0, 1]){
    const got = O.chainOnce(FX.graph, sc[h ? "h1" : "h0"]), want = sc.expect[h];
    for (const k in want.links){ worst = Math.max(worst, Math.abs(got.links[k] - want.links[k])); n++; }
    for (const k in want.outputs){ worst = Math.max(worst, Math.abs(got.outputs[k] - want.outputs[k])); n++; }
  }
  check("chain model equals the Python model (" + n + " values, worst difference " + worst.toExponential(1) + ")", n > 1000 && worst < 1e-12, worst);
  const base = O.chainOnce(FX.graph, {});
  check("chain with no shocks delivers everything", Object.values(base.links).every(v => v === 1));
}

// ---- simulation on a toy model with answers that can be worked out by hand
const TOY = {
  graph: {nodes: [{id: "ore", inputs: []}, {id: "part", inputs: [["ore", null, 1, 1]]}, {id: "plant", inputs: []}, {id: "site", inputs: [["part", null, 1, 1], ["plant", null, 1, 1]]}],
          other: {}, outputs: [{id: "site", label: "Site", mix: [["site", 1]]}]},
  scen: {flood: {h0: {plant: 0.5}}},
  period: {start: 0, len: 12}, supplyOutput: "site",
  demand: {segments: {big: 0.8, small: 0.2}},
  drivers: [
    {id: "mine_shut", kind: "event", p: 0.3, effects: [{t: "shock", node: "ore", s: 0.4}]},
    {id: "flood", kind: "event", p: 0.1, effects: [{t: "scen", id: "flood"}]},
    {id: "orders", kind: "range", low: 80, mid: 100, high: 110, min: 0, max: 130, effects: [{t: "demlvl", seg: "big"}]},
    {id: "bust", kind: "event", p: 0.2, effects: [{t: "dem", seg: "small", m: 0.5}]},
  ],
  corr: [["mine_shut", "flood", 0.6]],
};
{
  check("check() accepts the toy model", O.check(TOY).length === 0, O.check(TOY));
  const brokenModel = JSON.parse(JSON.stringify(TOY));
  brokenModel.drivers[0].p = 1.4; brokenModel.drivers[1].effects[0].id = "nope"; brokenModel.corr.push(["mine_shut", "ghost", 0.2]);
  check("check() lists what is wrong with a broken model", O.check(brokenModel).length === 3, O.check(brokenModel));

  const N = 200000, R = O.simulate(TOY, {n: N, seed: 7});
  const freq = id => O.mean(R.values[id]);
  const se = p => 4 * Math.sqrt(p * (1 - p) / N);                       // four standard errors
  check("each event happens as often as its probability says", close(freq("mine_shut"), 0.3, se(0.3)) && close(freq("flood"), 0.1, se(0.1)) && close(freq("bust"), 0.2, se(0.2)), [freq("mine_shut"), freq("flood"), freq("bust")]);
  let bothN = 0; for (let i = 0; i < N; i++) if (R.values.mine_shut[i] && R.values.flood[i]) bothN++;
  const want = O.both(0.3, 0.1, 0.6);
  check("correlated events coincide as often as the maths says (" + (bothN / N).toFixed(4) + " vs " + want.toFixed(4) + ")", close(bothN / N, want, se(want)));
  let indep = 0; for (let i = 0; i < N; i++) if (R.values.mine_shut[i] && R.values.bust[i]) indep++;
  check("unlinked events coincide at the product of their chances", close(indep / N, 0.06, se(0.06)), indep / N);
  const q = O.quantiles(R.values.orders, [0.1, 0.5, 0.9]);
  check("range driver lands on its low, central and high cases", close(q[0], 80, 0.3) && close(q[1], 100, 0.2) && close(q[2], 110, 0.15), q);

  // supply: 1 normally, 0.6 if the mine shuts, 0.5 if the plant floods, 0.5 if both (the weaker link wins)
  const pMine = 0.3 - want, pFloodAny = 0.1;
  check("supply odds match the hand calculation", close(O.probBelow(R.out.site, 0.55), pFloodAny, se(pFloodAny)) && close(O.probBelow(R.out.site, 0.65), pFloodAny + pMine, se(pFloodAny + pMine)), [O.probBelow(R.out.site, 0.55), O.probBelow(R.out.site, 0.65)]);
  // demand: 0.8 * orders/100 + 0.2 * (0.5 if bust else 1)
  let dOk = true;
  for (let i = 0; i < 2000; i++) dOk = dOk && close(R.out.demand[i], 0.8 * R.values.orders[i] / 100 + 0.2 * (R.values.bust[i] ? 0.5 : 1), 1e-6);
  check("demand follows the buyer groups", dOk);
  let bOk = true;
  for (let i = 0; i < 2000; i++) bOk = bOk && close(R.out.built[i], Math.min(R.out.site[i], R.out.demand[i]), 1e-7) && close(R.out.tight[i], R.out.demand[i] / R.out.site[i], 1e-5);
  check("built is the lesser of supply and demand; tightness is their ratio", bOk);
  const bt = Object.fromEntries(O.bindingTable(R).map(r => [r.id, r]));
  check("binding table names root causes, demand and plan", ["ore", "plant", "demand", "plan"].every(k => bt[k] && bt[k].share > 0) && close(Object.values(bt).reduce((a, r) => a + r.share, 0), 1, 1e-9), Object.keys(bt));
  check("the mine, not the part made from it, is named as the cause", !bt.part && !bt.site);
  const wm = O.whatMatters(R, "site");
  check("what matters most for supply: the two supply events, not the demand drivers", wm[0].share > wm[2].share && ["mine_shut", "flood"].includes(wm[0].id) && ["mine_shut", "flood"].includes(wm[1].id) && wm[2].share < 0.001, wm.map(r => [r.id, +r.share.toFixed(4)]));
  check("swing has the right sign and size", close(wm.find(r => r.id === "flood").swing, 0.5 - (1 * (0.9 - pMine) + 0.6 * pMine) / 0.9, 0.01), wm.find(r => r.id === "flood").swing);
  const wd = O.whatMatters(R, "demand");
  check("what matters most for demand: orders first", wd[0].id === "orders" && wd[0].share > 0.5 && wd[0].swing > 0, wd.map(r => [r.id, +r.share.toFixed(3)]));

  const again = O.simulate(TOY, {n: 5000, seed: 7}), again2 = O.simulate(TOY, {n: 5000, seed: 7}), other = O.simulate(TOY, {n: 5000, seed: 8});
  check("same seed, same futures; different seed, different futures", O.mean(again.out.built) === O.mean(again2.out.built) && O.mean(again.out.built) !== O.mean(other.out.built));

  // the owner's numbers: probability, severity and a link, laid over the starting numbers
  const mine = O.simulate(TOY, {n: N, seed: 7, beliefs: {drivers: {flood: {p: 0.4, sev: 0.5}}, corr: [["mine_shut", "flood", 0]]}});
  check("beliefs change a probability", close(O.mean(mine.values.flood), 0.4, se(0.4)));
  check("beliefs change a severity (flood now costs 25%, so nothing falls below 0.55)", O.probBelow(mine.out.site, 0.55) === 0 && close(O.probBelow(mine.out.site, 0.8), 1 - 0.7 * 0.6, se(0.42)), O.probBelow(mine.out.site, 0.8));
  let b2 = 0; for (let i = 0; i < N; i++) if (mine.values.mine_shut[i] && mine.values.flood[i]) b2++;
  check("beliefs replace a link (now independent)", close(b2 / N, 0.12, se(0.12)), b2 / N);
  const s = O.summary(R.out.built);
  check("summary is ordered", s.p05 <= s.p10 && s.p10 <= s.p50 && s.p50 <= s.p90 && s.p90 <= s.p95 && s.mean > 0.5 && s.mean < 1);
  const hsum = O.histogram(R.out.built, 0, 1.2, 12).reduce((a, b) => a + b, 0);
  check("histogram counts every future", hsum === N);
}

// ---- timing and relief effects
{
  const M = JSON.parse(JSON.stringify(TOY));
  M.period = {start: 3, len: 12};
  M.drivers = [{id: "late", kind: "event", p: 1, window: 15, effects: [{t: "shock", node: "plant", s: 0.6, timing: "window"}]},
               {id: "fix", kind: "event", p: 1, effects: [{t: "ease", node: "plant", f: 0.5}]}];
  M.corr = []; M.demand = {segments: {}};
  const R = O.simulate(M, {n: 100000, seed: 3});
  // start uniform over 15 months; year is months 3..15; average share of the year hit = 3/15 * 1 + 12/15 * 0.5 = 0.6; shock 0.6 halved by the fix
  check("timing: an event part-way through the year costs part of the year", close(1 - O.mean(R.out.site), 0.6 * 0.6 * 0.5, 0.004), 1 - O.mean(R.out.site));
  check("with no buyer groups, demand is 1 and never the limit", O.mean(R.out.demand) === 1);
}

// ---- the real chain inside a simulation: a certain Taiwan blockade gives the scenario's own numbers
{
  const M = {graph: FX.graph, scen: FX.scen, period: {start: 0, len: 12}, demand: {segments: {}}, corr: [],
             drivers: [{id: "tw", kind: "event", p: 1, effects: [{t: "scen", id: "taiwan"}]}]};
  const R = O.simulate(M, {n: 50, seed: 1}), want = FX.scen.taiwan.expect[0].outputs;
  check("a certain Taiwan blockade reproduces the scenario's outputs", Object.keys(want).every(k => close(R.out[k][0], want[k], 1e-6)), [R.out.accel[0], want.accel]);
  const top = O.bindingTable(R)[0];
  check("and names a link inside Taiwan as the cause", ["foundry", "cowos"].includes(top.id) && close(top.share, 1, 1e-12), top);
}

// ---- links in plain numbers, for every pairing of event and range
{
  const ev = p => ({kind: "event", p}), rg = {kind: "range", low: 70, mid: 90, high: 100}, rg2 = {kind: "range", low: 10, mid: 20, high: 45};
  check("condMedian: nothing moves without a link; mirror image for a negative link", O.condMedian(0.3, 0) === 0 && close(O.condMedian(0.2, -0.5), -O.condMedian(0.2, 0.5), 1e-9) && O.condMedian(0.2, 0.5) > 0);
  check("condMedian: with a near-perfect link B sits in the middle of A's top slice", close(O.condMedian(0.1, 0.999), O.normInv(0.95), 0.01), O.condMedian(0.1, 0.999));
  const u = O.rng(99), rho = 0.6, t = O.normInv(0.8), zb = [];
  for (let i = 0; i < 400000; i++){ const a = O.normInv(u(), false), e = O.normInv(u(), false); if (a > t) zb.push(rho * a + Math.sqrt(1 - rho * rho) * e); }
  const emp = O.quantiles(zb, [0.5])[0];
  check("condMedian matches a direct simulation (" + emp.toFixed(3) + " vs " + O.condMedian(0.2, rho).toFixed(3) + ")", close(emp, O.condMedian(0.2, rho), 0.02));

  const r1 = O.reading(ev(0.15), ev(0.25), 0.4), r2 = O.reading(ev(0.15), rg, 0.5), r2n = O.reading(ev(0.15), rg, -0.5), r3 = O.reading(rg, ev(0.25), 0.5), r4 = O.reading(rg, rg2, 0.5);
  check("reading: event to event is the conditional chance", r1.when === "happens" && r1.unit === "chance" && r1.base === 0.25 && close(r1.given, O.cond(0.15, 0.25, 0.4), 1e-12));
  check("reading: event to range moves the central case the way the sign says", r2.unit === "value" && r2.base === 90 && r2.given > 90 && r2.given < 100 && r2n.given < 90 && r2n.given > 70, [r2.given, r2n.given]);
  check("reading: a range's condition is its high case, a 1-in-10 outcome", r3.when === "high" && r3.pa === 0.1 && close(r3.given, O.cond(0.1, 0.25, 0.5), 1e-12) && r4.when === "high" && r4.base === 20 && r4.given > 20);
  const pairs = [[ev(0.15), ev(0.25)], [ev(0.15), rg], [rg, ev(0.25)], [rg, rg2]];
  const back = pairs.map(([a, b]) => O.rhoForReading(a, b, O.reading(a, b, -0.37).given).rho);
  check("rhoForReading undoes reading for all four pairings", back.every(v => close(v, -0.37, 1e-5)), back);
  const far = O.rhoForReading(ev(0.15), rg, 500);
  // with a near-perfect link B's central case sits in the middle of A's top 15%: beyond B's own 1-in-10 high case
  check("rhoForReading says what is reachable when the target is not", far.rho > 0.99 && far.reached === far.max && close(far.reached, O.rangeValue(rg, O.normInv(1 - 0.075)), 0.05), far);
}

// ---- situations: keep only the futures that match
{
  const cl = x => JSON.parse(JSON.stringify(x));
  const N = 20000, want = O.cond(0.1, 0.3, 0.6);
  const G1 = O.simulate(TOY, {n: N, seed: 11, given: {flood: true}});
  const tol = 4 * Math.sqrt(want * (1 - want) / N);
  check("given an event: every future has it, and the linked event shifts as the maths says (" + O.mean(G1.values.mine_shut).toFixed(3) + " vs " + want.toFixed(3) + ")", G1.n === N && G1.asked === N && O.mean(G1.values.flood) === 1 && close(O.mean(G1.values.mine_shut), want, tol));
  check("one event in a situation is drawn directly: one draw per future, and its chance is reported", G1.tried === N && close(G1.chance, 0.1, 1e-12), [G1.tried, G1.chance]);
  check("given an event: unlinked drivers do not move", close(O.mean(G1.values.bust), 0.2, 4 * Math.sqrt(0.16 / N)) && close(O.quantiles(G1.values.orders, [0.5])[0], 100, 0.6));
  const G2 = O.simulate(TOY, {n: 5000, seed: 11, given: {orders: "high"}});
  check("given a range at its high case (about ten draws per future, chance about 10%)", G2.n === 5000 && G2.values.orders.every(v => v >= 110) && close(G2.tried / 5000, 10, 0.6) && close(G2.chance, 0.1, 0.006), [G2.tried / 5000, G2.chance]);
  const G3 = O.simulate(TOY, {n: 5000, seed: 11, given: {orders: [95, 105], mine_shut: false}});
  check("given a range between two values and an event that does not happen", G3.n === 5000 && G3.values.orders.every(v => v >= 95 && v <= 105) && O.mean(G3.values.mine_shut) === 0);
  const G4 = O.simulate(TOY, {n: 5000, seed: 11, beliefs: {drivers: {flood: {p: 0}}}, given: {flood: true}});
  const s4 = O.summary(G4.out.built);
  check("a situation the numbers rule out returns no futures at once, and nothing breaks", G4.n === 0 && G4.tried === 0 && Number.isNaN(s4.mean) && Number.isNaN(s4.p50) && O.bindingTable(G4).length === 0 && O.whatMatters(G4, "built").length === 4 && O.profile(G4, G1).length === 4);
  const G5 = O.simulate(TOY, {n: N, seed: 11, given: {flood: true, orders: "high"}, maxTries: 1000});
  check("a rare situation stops at the draw limit with fewer futures", G5.tried === 1000 && G5.n > 60 && G5.n < 150 && G5.out.built.length === G5.n && G5.binding.length === G5.n && close(G5.chance, 0.01, 0.005), [G5.n, G5.chance]);
  const G7 = O.simulate(TOY, {n: N, seed: 11, beliefs: {drivers: {flood: {p: 1e-9}}}, given: {flood: true}});
  check("a one-in-a-billion event can still be supposed, at no extra cost", G7.n === N && G7.tried === N && G7.chance === 1e-9 && O.mean(G7.values.flood) === 1 && close(O.mean(G7.values.mine_shut), O.cond(1e-9, 0.3, 0.6), 0.005), [O.mean(G7.values.mine_shut), O.cond(1e-9, 0.3, 0.6)]);
  const G8 = O.simulate(TOY, {n: N, seed: 11, given: {flood: false}}), want8 = (0.3 - O.both(0.3, 0.1, 0.6)) / 0.9;
  check("supposing an event does not happen (" + O.mean(G8.values.mine_shut).toFixed(3) + " vs " + want8.toFixed(3) + ")", G8.tried === N && close(G8.chance, 0.9, 1e-12) && O.mean(G8.values.flood) === 0 && close(O.mean(G8.values.mine_shut), want8, 4 * Math.sqrt(want8 * (1 - want8) / N)));
  const G9 = O.simulate(TOY, {n: N, seed: 11, given: {mine_shut: true, flood: true}});
  check("two events together: the rarer is drawn directly, and the chance of both comes out right (" + G9.chance.toFixed(4) + " vs " + O.both(0.3, 0.1, 0.6).toFixed(4) + ")", G9.n === N && O.mean(G9.values.flood) === 1 && O.mean(G9.values.mine_shut) === 1 && close(G9.tried / N, 1 / want, 0.03) && close(G9.chance, O.both(0.3, 0.1, 0.6), 0.002));
  check("no situation: every draw is kept and the chance is 1", O.simulate(TOY, {n: 500, seed: 1}).chance === 1 && G4.chance === 0);
  const G6 = O.simulate(TOY, {n: 2000, seed: 11, given: {ghost: true, flood: "sometimes"}});
  check("conditions that cannot be used are reported, not silently applied", G6.n === 2000 && G6.tried === 2000 && JSON.stringify(G6.unknown) === JSON.stringify(["ghost", "flood"]));

  // picking futures from a finished run
  const BIG = 200000, R = O.simulate(TOY, {n: BIG, seed: 7});
  const S = O.subset(R, {flood: true});
  check("subset by a driver agrees with the situation run", S.of === BIG && close(S.n / BIG, 0.1, 0.003) && O.mean(S.values.flood) === 1 && close(O.mean(S.values.mine_shut), want, 0.015) && S.binding.length === S.n);
  const bad = O.subset(R, r => R.out.site[r] < 0.55);
  check("subset by an outcome: the futures where supply halves are the flood futures", bad.n === S.n && O.subset(S, {mine_shut: true}).of === BIG);
  const pf = O.profile(bad, R), pm = pf.find(x => x.id === "mine_shut"), po = pf.find(x => x.id === "orders");
  check("profile: what the bad futures have in common, most telling first", pf[0].id === "flood" && pf[0].picked === 1 && close(pf[0].lift, 10, 0.3) && close(pm.lift, want / 0.3, 0.1) && pf[1].id === "mine_shut" && Math.abs(po.score) < 0.03 && close(po.lift, 1, 0.01), pf.map(x => [x.id, +x.score.toFixed(2)]));

  // an event linked to a range, and a range linked to an event, against their plain-number readings
  const M2 = cl(TOY); M2.corr = [["flood", "orders", -0.5]];
  const R2 = O.simulate(M2, {n: 300000, seed: 5}), S2 = O.subset(R2, {flood: true});
  const med = O.quantiles(S2.values.orders, [0.5])[0], rd = O.reading(R2.drivers[1], R2.drivers[2], -0.5);
  check("event to range: the central case in the futures where the event happens (" + med.toFixed(2) + " vs " + rd.given.toFixed(2) + ")", rd.base === 100 && rd.given < 95 && close(med, rd.given, 0.4));
  const med2 = O.quantiles(O.simulate(M2, {n: 60000, seed: 5, given: {flood: true}}).values.orders, [0.5])[0];
  check("and the same when the event is supposed from the start (" + med2.toFixed(2) + ")", close(med2, rd.given, 0.3));
  const M3 = cl(TOY); M3.corr = [["orders", "bust", -0.6]];
  const R3 = O.simulate(M3, {n: 300000, seed: 5}), S3 = O.subset(R3, {orders: "high"});
  const rd3 = O.reading(R3.drivers[2], R3.drivers[3], -0.6);
  check("range to event: the chance when the range comes in high (" + O.mean(S3.values.bust).toFixed(4) + " vs " + rd3.given.toFixed(4) + ")", close(S3.n / 300000, 0.1, 0.003) && close(O.mean(S3.values.bust), rd3.given, 4 * Math.sqrt(rd3.given * (1 - rd3.given) / S3.n) + 1e-4));

  // the owner's saved numbers cannot break a run
  const ab = O.applyBeliefs(TOY, {drivers: {flood: {p: "0.9", sev: NaN, effects: [], kind: "range"}, mine_shut: {p: 7}, orders: {low: 105, high: 90}, ghost: {p: 0.5}},
                                  corr: [["flood", "bust", "x"], "junk", ["bust", "flood", 0.3], ["flood", "mine_shut", 0.1]]});
  const D = Object.fromEntries(ab.drivers.map(d => [d.id, d]));
  check("beliefs: only numbers are taken, and only the five that can be edited", D.flood.p === 0.1 && D.flood.sev === 1 && D.flood.kind === "event" && D.flood.effects.length === 1 && ab.drivers.length === 4);
  check("beliefs: kept sensible (chance capped at 1, low <= central <= high)", D.mine_shut.p === 1 && D.orders.low === 100 && D.orders.high === 100 && D.orders.mid === 100);
  check("beliefs: a link replaces the starting one whichever way round it is written", ab.corr.length === 2 && ab.corr.some(c => c.includes("mine_shut") && c[2] === 0.1) && ab.corr.some(c => c.includes("bust") && c[2] === 0.3), ab.corr);
  check("the starting model is never changed by a run", JSON.stringify(TOY.drivers[1]) === JSON.stringify({id: "flood", kind: "event", p: 0.1, effects: [{t: "scen", id: "flood"}]}));

  const B = cl(TOY);
  B.drivers[0].window = -1; B.drivers[2].min = 90; B.drivers[0].effects[0].s = 1.5;
  B.drivers[1].effects.push({t: "ease", node: "plant", f: 2, timing: "soon", on: "maybe"});
  B.drivers[3].effects[0].m = -1;
  B.corr.push(["flood", "flood", 0.2], ["flood", "mine_shut", 0.1]);
  B.supplyOutput = "nope"; B.demand.segments.small = 0.1; B.period = {start: 0, len: 0}; B.graph.outputs[0].mix = [["nowhere", 1]];
  check("check() catches thirteen further kinds of mistake", O.check(B).length === 13, O.check(B));
}

// ---- a supply output made of several links (accelerators = GPUs + custom chips)
{
  const M = {graph: FX.graph, scen: FX.scen, period: {start: 0, len: 12}, demand: {segments: {}}, corr: [], supplyOutput: "accel",
             drivers: [{id: "pkg", kind: "event", p: 1, effects: [{t: "shock", node: "cowos", s: 0.5}]}]};
  const R = O.simulate(M, {n: 20, seed: 1}), top = O.bindingTable(R)[0];
  check("a mixed output still traces its shortfall to the link that caused it", O.check(M).length === 0 && R.out.accel[0] < 0.9 && top.id === "cowos" && top.share === 1, [R.out.accel[0], top]);
}

// ---- speed on the real chain (reported, not judged: machines differ)
{
  const nodes = FX.graph.nodes.map(n => n.id), scen = Object.keys(FX.scen).filter(k => Object.keys(FX.scen[k].h0).length);
  const drivers = [], corr = [];
  for (let i = 0; i < 14; i++) drivers.push({id: "e" + i, kind: "event", p: 0.03 + 0.02 * i, window: 15, effects: i < scen.length ? [{t: "scen", id: scen[i], timing: "window"}] : [{t: "shock", node: nodes[(i * 7) % nodes.length], s: 0.3, timing: "window"}, {t: "dem", seg: "all", m: 0.9}]});
  for (let i = 0; i < 13; i++) drivers.push({id: "r" + i, kind: "range", low: 80, mid: 97, high: 105, min: 0, max: 130, effects: i < 10 ? [{t: "ramp", node: nodes[(i * 5 + 3) % nodes.length]}] : [{t: "demlvl", seg: ["hyper", "neo", "sov"][i - 10]}]});
  for (let i = 0; i < 26; i++) corr.push([drivers[i].id, drivers[i + 1].id, i % 3 ? 0.3 : -0.2]);
  const M = {graph: FX.graph, scen: FX.scen, period: {start: 3, len: 12}, demand: {segments: {hyper: 0.7, neo: 0.2, sov: 0.1}}, drivers, corr};
  check("a model the size of the real one passes check()", O.check(M).length === 0, O.check(M));
  O.simulate(M, {n: 2000, seed: 1});                                   // warm up
  let t0 = performance.now(); const R = O.simulate(M, {n: 10000, seed: 1}); const t1 = performance.now() - t0;
  t0 = performance.now(); const Rg = O.simulate(M, {n: 10000, seed: 1, given: {e0: true}}); const t2 = performance.now() - t0;
  t0 = performance.now(); O.whatMatters(R, "built"); O.bindingTable(R); O.summary(R.out.built); const t3 = performance.now() - t0;
  console.log("INFO 27 drivers, 64 links: 10,000 futures in " + t1.toFixed(0) + " ms; given a 3% event (" + Rg.tried + " draws) in " + t2.toFixed(0) + " ms; summaries in " + t3.toFixed(0) + " ms");
  check("the full-size run produces sensible numbers", R.n === 10000 && O.mean(R.out.built) > 0.3 && O.mean(R.out.built) < 1 && Rg.n === 10000 && O.mean(Rg.out.built) < O.mean(R.out.built), [O.mean(R.out.built), O.mean(Rg.out.built)]);
}

// ---- effect options the real model uses
{
  const cl = x => JSON.parse(JSON.stringify(x));
  const M = cl(TOY); M.period = {start: 3, len: 12}; M.corr = []; M.demand = {segments: {}};
  const lost = drivers => { M.drivers = drivers; return 1 - O.mean(O.simulate(M, {n: 100000, seed: 4}).out.site); };
  // already running, ends at a random month between 0 and 9; the year is months 3 to 15; average share of the year hit = (6 * 6 / 2) / 9 / 12
  const until = lost([{id: "war", kind: "event", p: 1, window: 9, effects: [{t: "shock", node: "plant", s: 0.4, timing: "until"}]}]);
  check("timing 'until': a running problem that ends part-way costs the months before it ends", close(until, 0.4 / 6, 0.002), until);
  // starts at a random month between 9 and 15: average share hit = 3 / 12
  const late = lost([{id: "late", kind: "event", p: 1, from: 9, window: 15, effects: [{t: "shock", node: "plant", s: 0.5, timing: "window"}]}]);
  check("'from': an event that cannot start before a date", close(late, 0.5 * 0.25, 0.002), late);
  M.scen = {both: {h0: {ore: 0.2, plant: 0.3}}};
  const only = lost([{id: "a", kind: "event", p: 1, effects: [{t: "scen", id: "both", only: ["ore"]}]}]);
  const skip = lost([{id: "a", kind: "event", p: 1, effects: [{t: "scen", id: "both", skip: ["ore"]}]}]);
  const all = lost([{id: "a", kind: "event", p: 1, effects: [{t: "scen", id: "both"}]}]);
  check("a scenario can be applied whole, in part, or with a link left out", close(only, 0.2, 1e-6) && close(skip, 0.3, 1e-6) && close(all, 0.3, 1e-6), [only, skip, all]);
  M.drivers = [{id: "a", kind: "event", p: 1, effects: [{t: "scen", id: "both", only: ["site"], timing: "sometime"}]}];
  check("check() catches a scenario part that does not exist and an unknown timing", O.check(M).length === 2, O.check(M));
  check("level(): base, pass-through and offset", close(O.level(90, {}), 0.9, 1e-12) && close(O.level(90, {k: 0.5}), 0.95, 1e-12) && close(O.level(143, {base: 130}), 1.1, 1e-12) && close(O.level(15, {add: 100}), 1.15, 1e-12));
  const D = cl(TOY); D.corr = []; D.demand = {segments: {big: 1}};
  D.drivers = [{id: "more", kind: "range", low: 5, mid: 15, high: 30, effects: [{t: "demlvl", seg: "all", add: 100}]},
               {id: "rev", kind: "range", low: 120, mid: 160, high: 220, effects: [{t: "demlvl", seg: "big", base: 160, k: 0.5}]}];
  const R = O.simulate(D, {n: 4000, seed: 2});
  let ok = true;
  for (let i = 0; i < 4000; i++) ok = ok && close(R.out.demand[i], (1 + R.values.more[i] / 100) * (1 + 0.5 * (R.values.rev[i] / 160 - 1)), 1e-5);
  check("range effects with an offset and a partial pass-through combine as documented", ok);
}

// ---- the real model: data/odds.json on the real chain
{
  const file = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "odds.json"), "utf8"));
  const M = O.assemble(file, {graph: FX.graph, scen: FX.scen});
  check("the model file passes check()", O.check(M).length === 0, O.check(M));
  const groups = new Set(file.groups.map(g => g.id)), bases = new Set(Object.keys(file.bases)), bad = [], ids = new Set();
  for (const d of file.drivers){
    for (const k of ["id", "group", "kind", "label", "question", "basis", "note", "does"]) if (!d[k] || typeof d[k] !== "string") bad.push(d.id + ": needs " + k);
    if (!/^[a-z][a-z0-9_]*$/.test(d.id || "") || ids.has(d.id)) bad.push(d.id + ": id must be unique, lower case with underscores");
    ids.add(d.id);
    if (!groups.has(d.group)) bad.push(d.id + ": unknown group");
    if (!bases.has(d.basis)) bad.push(d.id + ": unknown basis");
    if (!d.resolves && !d.watch) bad.push(d.id + ": needs 'resolves' or 'watch'");
    if (!String(d.question || "").trim().endsWith("?")) bad.push(d.id + ": the question should end with a question mark");
    if (d.kind === "event" && !/^\d{4}-\d\d-\d\d$/.test(d.deadline || "")) bad.push(d.id + ": needs a deadline date");
    if (d.kind === "event" && d.starts && !(d.starts < d.deadline)) bad.push(d.id + ": starts must be before the deadline");
    if (d.kind === "range" && (!d.unit || d.min == null || d.max == null)) bad.push(d.id + ": needs unit, min and max");
    if (!Array.isArray(d.effects) || !d.effects.length) bad.push(d.id + ": needs at least one effect");
  }
  for (const l of file.links){
    if (!l.why) bad.push(l.a + " - " + l.b + ": needs a reason");
    if (!(Math.abs(l.rho) <= 0.9)) bad.push(l.a + " - " + l.b + ": starting links stay within -0.9 to 0.9");
  }
  for (const g of groups) if (!file.drivers.some(d => d.group === g)) bad.push("group " + g + " has no drivers");
  // the stories the links are filed under, and the plain words each driver reads with in a sentence
  const stories = new Set((file.stories || []).map(s => s.id)), byId0 = Object.fromEntries(file.drivers.map(d => [d.id, d]));
  for (const s of file.stories || []) if (!s.id || !s.label || !s.blurb || s.id === "other") bad.push("story " + s.id + ": needs id (not 'other'), label and blurb");
  for (const d of file.drivers){
    if (!stories.has(d.story)) bad.push(d.id + ": unknown story '" + d.story + "'");
    const s = d.say || {}, words = d.kind === "event" ? ["if", "of"] : ["if", "subj"];
    for (const k of words) if (!s[k] || typeof s[k] !== "string") bad.push(d.id + ": say needs '" + k + "'");
    if (d.kind === "event" && s.of && !/^(of|that) /.test(s.of)) bad.push(d.id + ": say.of starts with 'of' or 'that' (it follows 'the chance')");
    if (d.kind === "range" && s.if && !/high case$/.test(s.if)) bad.push(d.id + ": a quantity's say.if is its high case");
    if (/[.,]$/.test(s.if || "")) bad.push(d.id + ": say.if ends without punctuation");
  }
  // a researched number carries the day it was checked and at least one source with a web link
  for (const d of file.drivers){
    const srcs = d.src || [];
    for (const x of srcs) if (!x || !x.t || !/^https?:\/\//.test(x.u || "")) bad.push(d.id + ": each source needs a title (t) and a web link (u)");
    if (d.basis !== "judgement"){
      if (!/^\d{4}-\d\d-\d\d$/.test(d.checked || "") || d.checked > file.asOf) bad.push(d.id + ": a researched number needs the date it was checked (on or before asOf)");
      if (!srcs.length) bad.push(d.id + ": a researched number needs at least one source");
    }
  }
  for (const l of file.links) if (l.story != null && !stories.has(l.story)) bad.push(l.a + " - " + l.b + ": unknown story '" + l.story + "'");
  for (const s of stories) if (!file.links.some(l => (l.story || (byId0[l.a] || {}).story) === s)) bad.push("story " + s + " has no links");
  check("every driver and link in the model file is complete (" + file.drivers.length + " drivers, " + file.links.length + " links)", bad.length === 0 && file.drivers.length >= 20, bad);
  check("buyer groups add up to 1", close(file.buyers.reduce((a, b) => a + b.share, 0), 1, 1e-9));

  const byId = Object.fromEntries(M.drivers.map(d => [d.id, d])), yearEnd = M.period.start + M.period.len;
  check("dates become months from the file's date", M.period.start > 0 && M.period.start < 12 && close(byId.tw_blockade.window, yearEnd, 0.05) && byId.cn_minerals.from > 0 && byId.cn_minerals.from < byId.cn_minerals.window && close(byId.digestion.from, M.period.start, 0.01), [M.period, byId.tw_blockade.window, byId.cn_minerals.from]);
  check("\"base\": \"mid\" is tied to the starting central case", byId.capex_2027.effects[0].base === byId.capex_2027.mid && byId.sov_follow.effects[0].base === byId.sov_follow.mid && file.drivers.find(d => d.id === "capex_2027").effects[0].base === "mid");

  const N = 40000, R = O.simulate(M, {n: N}), sb = O.summary(R.out.built), sd = O.summary(R.out.demand);
  check("the starting links can all hold together (no repair needed)", R.corr.changed === false && R.unknown.length === 0);
  let finite = true;
  for (const k in R.out) for (let i = 0; i < N; i++) if (!(R.out[k][i] >= 0 && R.out[k][i] < 50)) finite = false;
  check("every outcome is a sensible number in every future", finite && R.n === N);
  check("baseline: most of the plan gets built, with a real downside", sb.p50 > 0.85 && sb.p50 < 0.98 && sb.p10 > 0.6 && sb.p10 < sb.p50 - 0.03 && sb.p95 <= 1 && O.probBelow(R.out.built, 0.6) < 0.06, sb);
  check("baseline: buyers want more than the plan in the central case", sd.p50 > 1 && sd.p50 < 1.4, sd);
  const calm = {drivers: {}};
  for (const d of file.drivers) calm.drivers[d.id] = d.kind === "event" ? {p: d.effects.every(e => e.on === "no") ? 1 : 0} : {low: d.mid, high: d.mid};
  const C = O.simulate(M, {n: 200, beliefs: calm});
  check("with every range at its central case and no events, the plan is delivered almost in full (" + (100 * C.out.built[0]).toFixed(1) + "%)", C.out.built[0] > 0.98 && C.out.built[0] <= 1 && C.out.built[199] === C.out.built[0], C.out.built[0]);
  const bt = O.bindingTable(R), wm = O.whatMatters(R, "built");
  check("limits and rankings cover the whole model", close(bt.reduce((a, b) => a + b.share, 0), 1, 1e-9) && wm.length === file.drivers.length && wm.every(w => w.share >= 0 && w.share <= 1.0000001));
  let supposed = 0;
  for (const d of M.drivers) if (d.kind === "event"){
    const g = O.simulate(M, {n: 1500, seed: 3, given: {[d.id]: true}});
    if (g.n === 1500 && close(g.chance, d.p, 1e-9) && O.mean(g.values[d.id]) === 1 && O.mean(g.out.built) > 0) supposed++;
  }
  check("every event can be supposed", supposed === M.drivers.filter(d => d.kind === "event").length, supposed);
  const tw = O.simulate(M, {n: 20000, seed: 3, given: {tw_blockade: true}});
  check("supposing a Taiwan blockade cuts the build-out sharply and raises the linked risks", O.mean(tw.out.built) < O.mean(R.out.built) - 0.2 && O.mean(tw.values.cn_minerals) > byId.cn_minerals.p + 0.2 && O.mean(tw.values.credit_squeeze) > byId.credit_squeeze.p + 0.15, [O.mean(tw.out.built), O.mean(tw.values.cn_minerals)]);
  const pc = v => (100 * v).toFixed(0) + "%";
  console.log("INFO baseline built: central " + pc(sb.p50) + " of plan, 1-in-10 low " + pc(sb.p10) + ", 1-in-10 high " + pc(sb.p90) + "; chance below 80%: " + pc(O.probBelow(R.out.built, 0.8)));
  console.log("INFO most frequent limits: " + bt.slice(0, 6).map(b => b.id + " " + pc(b.share)).join(", "));
  console.log("INFO biggest swings: " + wm.slice().sort((a, b) => Math.abs(b.swing) - Math.abs(a.swing)).slice(0, 6).map(w => w.id + " " + (100 * w.swing).toFixed(0)).join(", "));
}

console.log("\n" + (passed + failed.length) + " checks, " + failed.length + " failed");
for (const f of failed) console.log("  FAILED: " + f);
process.exit(failed.length ? 1 : 0);
