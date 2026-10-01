/* Update desk for the AI Supply Chain Map site (GitHub Pages only; loaded after each page's own script).

   Everyone: see when prices and headlines were last refreshed, reload them, browse the news radar and
   suggest a development (opens a prefilled GitHub issue).
   The site owner, after connecting a fine-grained GitHub key that stays in this browser: refresh prices and
   headlines now, publish, edit or delete developments, and turn automatic updates on.

   Outside text (headlines, entries, build warnings) is only inserted with textContent, and only http(s) links are used. */
(function(){
"use strict";
const S = window.SCMAP;
if (!S || !S.DATA || !S.DATA.desk) return;
const DATA = S.DATA, CFG = DATA.desk;
const API = "https://api.github.com", REPO = "/repos/" + CFG.repo, WF = REPO + "/actions/workflows/" + CFG.workflow;
const deskEl = document.getElementById("desk"), barEl = document.getElementById("desk-bar");
const FULL = !!(deskEl && S.NODES);
const K_TOKEN = "aiscm.ghkey", K_HIDE = "aiscm.hiddenNews", K_SEEN = "aiscm.seenNews";
const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

/* ---------------- helpers ---------------- */
function h(tag, attrs, ...kids){
  const e = document.createElement(tag);
  if (attrs) for (const k in attrs){
    const v = attrs[k];
    if (v == null || v === false) continue;
    if (k === "class") e.className = v;
    else if (k === "text") e.textContent = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? "" : v);
  }
  for (const c of kids.flat()) if (c != null && c !== false) e.append(c.nodeType ? c : document.createTextNode(String(c)));
  return e;
}
const $ = (q, r) => (r || document).querySelector(q);
const sleep = ms => new Promise(r => setTimeout(r, ms));
function storage(kind){ try { const s = window[kind]; s.getItem("_"); return s; } catch(e){ return null; } }
const LS = storage("localStorage"), SS = storage("sessionStorage");
function getItem(k){ for (const s of [LS, SS]){ if (!s) continue; try { const v = s.getItem(k); if (v != null) return v; } catch(e){} } return null; }
function setItem(k, v, persist){ const s = persist === false ? SS : LS; if (!s) return false; try { s.setItem(k, v); return true; } catch(e){ return false; } }
function delItem(k){ for (const s of [LS, SS]){ if (!s) continue; try { s.removeItem(k); } catch(e){} } }
function safeUrl(u){ return typeof u === "string" && /^https?:\/\/[^\s<>"]+$/i.test(u.trim()) ? u.trim() : null; }
function hostOf(u){ try { return new URL(u).hostname.replace(/^www\./, ""); } catch(e){ return "Source"; } }
function slug(t, n){ return String(t).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, n || 64).replace(/-+$/, "") || "entry"; }
function uniqueId(base, taken){ let id = base, k = 2; while (taken.has(id)) id = base + "-" + (k++); return id; }
function pad(n){ return String(n).padStart(2, "0"); }
function ymd(d){ return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
function todayISO(){ return ymd(new Date()); }
function localDate(iso){ const d = new Date(iso); return isNaN(d) ? "" : ymd(d); }
function clock(d){ d = new Date(d); return isNaN(d) ? "" : d.toLocaleTimeString([], {hour: "numeric", minute: "2-digit"}); }
function stamp(iso){ const d = new Date(iso); if (isNaN(d)) return ""; return d.toDateString() === new Date().toDateString() ? clock(d) : d.getDate() + " " + MONTHS[d.getMonth()] + ", " + clock(d); }
function ago(iso){ const ms = Date.now() - Date.parse(iso); if (!(ms >= -60000)) return ""; const m = Math.round(Math.max(0, ms) / 60000); if (m < 1) return "just now"; if (m < 60) return m + " min ago"; const hr = Math.round(m / 60); if (hr < 24) return hr + " h ago"; const dd = Math.round(hr / 24); return dd + (dd === 1 ? " day ago" : " days ago"); }
function longDate(s){ const p = String(s || "").split("-"); return p.length === 3 && MONTHS[+p[1] - 1] ? (+p[2]) + " " + MONTHS[+p[1] - 1] + " " + p[0] : String(s || ""); }
function normT(t){ return String(t || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim(); }
function b64decode(b64){ const bin = atob(String(b64).replace(/\s+/g, "")); const bytes = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i); return new TextDecoder("utf-8").decode(bytes); }
function b64encode(str){ const bytes = new TextEncoder().encode(str); let bin = ""; for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000)); return btoa(bin); }
function readSet(k){ try { const a = JSON.parse(getItem(k) || "null"); return Array.isArray(a) ? new Set(a) : null; } catch(e){ return null; } }

/* ---------------- state ---------------- */
const ST = {token: getItem(K_TOKEN), login: null, quotes: null, news: null, build: null, health: null, manual: false,
            dev: null, devSha: null, devError: null, busy: false, prog: null, newsTopic: "all", newsAll: false, newsLimit: 20,
            newIds: new Set(), newIdsFor: null};

/* ---------------- GitHub API ---------------- */
class GhError extends Error { constructor(msg, status){ super(msg); this.status = status; } }
async function gh(path, opt){
  opt = opt || {};
  const headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"};
  if (ST.token) headers.Authorization = "Bearer " + ST.token;
  if (opt.body) headers["Content-Type"] = "application/json";
  let r;
  try { r = await fetch(API + path, {method: opt.method || "GET", headers, body: opt.body ? JSON.stringify(opt.body) : undefined, cache: "no-store"}); }
  catch(e){ throw new GhError("Couldn't reach GitHub. Check your connection and try again.", 0); }
  if (r.status === 204) return null;
  let js = null; try { js = await r.json(); } catch(e){}
  if (!r.ok) throw new GhError((js && js.message) || ("GitHub answered " + r.status + "."), r.status);
  return js;
}
function explain(e, what){
  const s = e && e.status;
  if (s === 401) return "GitHub didn't accept your key. It may have expired or been deleted: disconnect and connect a new one.";
  if ((s === 403 || s === 429) && /rate limit/i.test(e.message)) return "GitHub's rate limit was reached. Wait a few minutes and try again.";
  if (s === 403) return "Your key isn't allowed to " + (what || "do that") + ". On GitHub, give it Read and write access to Contents, Actions and Workflows for AI_Supply-Chain_Map.";
  if (s === 404) return "Your key can't see the AI_Supply-Chain_Map repository or the file it needs. Check the key's repository access on GitHub.";
  if (s === 409) return "The file changed on GitHub at the same moment. Try again.";
  if (s === 422) return "GitHub rejected the request: " + e.message;
  return (e && e.message) || "Something went wrong.";
}

/* ---------------- published data ---------------- */
async function getJSON(url){
  if (!url) return null;
  try { const r = await fetch(url + (url.includes("?") ? "&" : "?") + "t=" + Date.now(), {cache: "no-store"}); return r.ok ? await r.json() : null; }
  catch(e){ return null; }
}
async function loadStatus(){
  const [q, n, b] = await Promise.all([getJSON(CFG.quotesUrl), getJSON(CFG.newsUrl), getJSON(CFG.buildUrl)]);
  if (q) ST.quotes = q;
  if (n && Array.isArray(n.items)) ST.news = n;
  if (b) ST.build = b;
}

/* ---------------- progress messages ---------------- */
let ticker = null, clearT = null;
function setProg(p){
  ST.prog = p;
  if (ticker){ clearInterval(ticker); ticker = null; }
  clearTimeout(clearT);
  if (p && p.state === "run" && p.t0) ticker = setInterval(paintProg, 1000);
  if (p && p.state === "ok" && p.fade) clearT = setTimeout(() => { if (ST.prog === p) setProg(null); }, 9000);
  paintProg();
}
function paintProg(){
  const p = ST.prog;
  document.querySelectorAll(".dk-prog").forEach(el => {
    el.textContent = "";
    const show = p && (el.dataset.where === "any" || el.dataset.where === (p.where || "top"));
    el.className = "dk-prog" + (show ? " " + p.state : "");
    if (!show) return;
    let txt = p.text;
    if (p.state === "run" && p.t0){ const s = Math.max(0, Math.round((Date.now() - p.t0) / 1000)); txt += " · " + Math.floor(s / 60) + ":" + pad(s % 60); }
    el.append(h("span", {text: txt}));
    const link = safeUrl(p.link);
    if (link) el.append(" ", h("a", {href: link, target: "_blank", rel: "noopener", text: p.state === "fail" ? "See what happened" : "Details"}));
  });
}
function prog(where){ return h("span", {class: "dk-prog", "data-where": where, "aria-live": "polite"}); }
function paintButtons(){ document.querySelectorAll(".dk-refresh, #dk-publish, .dk-busy-off, .dk-elist button").forEach(b => { b.disabled = ST.busy; }); }

/* ---------------- following a GitHub Actions run ---------------- */
const STEPS = [[/^save/i, "Saving data"], [/prices/i, "Fetching prices from Yahoo Finance"], [/headlines/i, "Collecting headlines"],
               [/build pages/i, "Rebuilding the pages"], [/pages|upload/i, "Packaging the site"], [/^post|complete/i, "Finishing"]];
function stepText(js){
  const jobs = (js && js.jobs) || [];
  const job = jobs.find(j => j.status === "in_progress") || jobs.find(j => j.status !== "completed");
  if (!job) return "Finishing";
  if (/deploy/i.test(job.name)) return "Publishing the site";
  const st = (job.steps || []).find(s => s.status === "in_progress");
  if (st) for (const [re, t] of STEPS) if (re.test(st.name)) return t;
  return "Starting up";
}
async function latestRunId(event){
  try { const js = await gh(WF + "/runs?per_page=1" + (event ? "&event=" + event : "")); const r = ((js && js.workflow_runs) || [])[0]; return r ? r.id : 0; }
  catch(e){ return null; }
}
/* Wait for the run that `match` picks (found with the extra `query`), report its steps, and return it when done.
   If a newer run replaced it (GitHub cancels a waiting run when another queues behind it), follow that one:
   it starts from the latest commit, so it carries the same changes. */
async function follow(match, query, label, where, t0){
  const deadline = Date.now() + 15 * 60 * 1000;
  let target = null;
  while (Date.now() < deadline){
    await sleep(target ? 4000 : 2500);
    try {
      if (!target){
        const js = await gh(WF + "/runs?per_page=10" + (query || ""));
        const c = ((js && js.workflow_runs) || []).filter(match).sort((a, b) => a.id - b.id);
        if (!c.length){ setProg({state: "run", where, text: label + " · waiting for GitHub to start", t0}); continue; }
        target = c[0];
      } else target = (await gh(REPO + "/actions/runs/" + target.id)) || target;
      if (target.status === "completed"){
        if (target.conclusion === "cancelled"){
          const js = await gh(WF + "/runs?per_page=10");
          const next = ((js && js.workflow_runs) || []).filter(r => r.id > target.id).sort((a, b) => a.id - b.id)[0];
          if (next){ target = next; continue; }
        }
        return target;
      }
      let txt = /queued|requested/.test(target.status) ? "queued at GitHub" : "waiting for the update before it to finish";
      if (target.status === "in_progress"){ txt = "Starting up"; try { txt = stepText(await gh(REPO + "/actions/runs/" + target.id + "/jobs")); } catch(e){} }
      setProg({state: "run", where, text: label + " · " + txt, t0, link: target.html_url});
    } catch(e){ if (e.status && e.status < 500) throw e; }
  }
  throw new GhError("This is taking longer than usual. Check the Actions tab on GitHub.", -1);
}

/* ---------------- actions ---------------- */
async function refreshNow(){
  if (ST.busy || !ST.token) return;
  ST.busy = true; paintButtons();
  const where = "top", t0 = Date.now();
  const before = ST.quotes && ST.quotes.updated, beforeNews = ST.news && ST.news.updated;
  setProg({state: "run", where, text: "Refreshing · asking GitHub to start", t0});
  try {
    const base = await latestRunId("workflow_dispatch");
    await gh(WF + "/dispatches", {method: "POST", body: {ref: CFG.branch, inputs: {targets: "auto", news: "always"}}});
    const run = await follow(r => r.event === "workflow_dispatch" && (base == null ? Date.parse(r.created_at) >= t0 - 120000 : r.id > base),
                             "&event=workflow_dispatch", "Refreshing", where, t0);
    if (run.conclusion !== "success"){ setProg({state: "fail", where, text: "The refresh didn't finish (" + (run.conclusion || "unknown") + ").", link: run.html_url}); return; }
    setProg({state: "run", where, text: "Refreshing · loading the new data", t0});
    for (let i = 0; i < 10; i++){
      await sleep(i ? 4000 : 1500);
      await loadStatus();
      const q = !before || (ST.quotes && ST.quotes.updated !== before), n = !beforeNews || (ST.news && ST.news.updated !== beforeNews);
      if (q && n) break;
    }
    if (S.refreshLive) await S.refreshLive();
    renderAll();
    setProg({state: "ok", where, fade: true, text: "Updated at " + clock(new Date()) + "."});
  } catch(e){ setProg({state: "fail", where, text: explain(e, "start an update")}); }
  finally { ST.busy = false; paintButtons(); }
}
async function reloadData(){
  if (ST.busy) return;
  setProg({state: "run", where: "top", text: "Loading the latest published data"});
  await loadStatus();
  if (S.refreshLive) await S.refreshLive();
  renderAll();
  setProg({state: "ok", where: "top", fade: true, text: "Showing the latest published data."});
}
async function loadDevs(){
  const f = await gh(REPO + "/contents/" + CFG.devPath + "?ref=" + CFG.branch);
  let dev;
  try { dev = JSON.parse(b64decode(f.content)); }
  catch(e){ throw new GhError("data/developments.json on GitHub isn't valid JSON, so the desk can't edit it. Fix it on GitHub first.", -2); }
  if (!dev || typeof dev !== "object" || Array.isArray(dev)) dev = {};
  dev.entries = Array.isArray(dev.entries) ? dev.entries : [];
  dev.upcoming = Array.isArray(dev.upcoming) ? dev.upcoming : [];
  ST.dev = dev; ST.devSha = f.sha; ST.devError = null;
  return dev;
}
async function mutateDevs(mutate, message){
  const dev = JSON.parse(JSON.stringify(await loadDevs()));
  mutate(dev);
  const res = await gh(REPO + "/contents/" + CFG.devPath, {method: "PUT", body: {message, content: b64encode(JSON.stringify(dev, null, 2) + "\n"), sha: ST.devSha, branch: CFG.branch}});
  ST.dev = dev; ST.devSha = res && res.content && res.content.sha;
  return res && res.commit && res.commit.sha;
}
async function commitAndPublish(label, mutate, message, where){
  if (ST.busy) return false;
  ST.busy = true; paintButtons();
  const t0 = Date.now();
  setProg({state: "run", where, text: label + " · saving to GitHub", t0});
  try {
    let sha;
    try { sha = await mutateDevs(mutate, message); }
    catch(e){ if (e.status !== 409) throw e; sha = await mutateDevs(mutate, message); }
    const run = await follow(sha ? r => r.head_sha === sha : r => r.event === "push" && Date.parse(r.created_at) >= t0 - 120000,
                             sha ? "&head_sha=" + sha : "&event=push", label, where, t0);
    if (run.conclusion !== "success"){ setProg({state: "fail", where, text: "Saved to GitHub, but the site didn't rebuild (" + (run.conclusion || "unknown") + ").", link: run.html_url}); return false; }
    setProg({state: "ok", where, text: "Published. Reloading the page…"});
    await sleep(1500);
    location.replace(location.pathname + "?v=" + Date.now() + "#log");
    return true;
  } catch(e){ setProg({state: "fail", where, text: explain(e, "save changes")}); return false; }
  finally { ST.busy = false; paintButtons(); }
}
/* A commit that changes the schedule makes its author the account the schedule runs under, so the owner
   "turns on" automatic updates by shifting every scheduled minute by one (staying off :00, :15, :30 and :45). */
function rotateCron(text){
  let n = 0;
  const out = text.replace(/(cron:\s*["'])(\d+(?:,\d+)*)(\s)/g, (m, a, mins, b) => {
    n++;
    return a + mins.split(",").map(x => { const v = +x, base = v % 15; return v - base + (base % 14) + 1; }).join(",") + b;
  });
  return n ? out : null;
}
function firstRunText(){
  const d = new Date(), wd = d.getUTCDay() >= 1 && d.getUTCDay() <= 5 && d.getUTCHours() < 22;
  return wd ? "The first scheduled update usually runs within 15 to 30 minutes." : "Weekend updates run every 6 hours; weekday updates restart Monday.";
}
async function turnOnSchedule(){
  if (ST.busy || !ST.token) return;
  ST.busy = true; paintButtons();
  const where = "top";
  setProg({state: "run", where, text: "Turning on automatic updates", t0: Date.now()});
  try {
    const f = await gh(REPO + "/contents/" + CFG.wfPath + "?ref=" + CFG.branch);
    const next = rotateCron(b64decode(f.content));
    if (!next) throw new GhError("Couldn't find the schedule in the workflow file.", -3);
    await gh(REPO + "/contents/" + CFG.wfPath, {method: "PUT", body: {message: "Turn on automatic updates from the Update desk\n\nGitHub runs a schedule under the account that last changed it, so this change from the owner's account starts it.", content: b64encode(next), sha: f.sha, branch: CFG.branch}});
    ST.health = Object.assign({}, ST.health, {wfBy: ST.login, wfAt: new Date().toISOString()});
    ST.manual = false;
    setProg({state: "ok", where, text: "Automatic updates are on. " + firstRunText()});
  } catch(e){
    if (e.status === 403 || e.status === 404){ ST.manual = true; setProg({state: "fail", where, text: "Your key can't change the workflow file. The box above shows two ways to fix that."}); }
    else setProg({state: "fail", where, text: explain(e, "change the schedule")});
  } finally { ST.busy = false; renderAll(); }
}
async function enableWorkflow(){
  if (ST.busy || !ST.token) return;
  ST.busy = true; paintButtons();
  setProg({state: "run", where: "top", text: "Switching updates back on", t0: Date.now()});
  try {
    await gh(WF + "/enable", {method: "PUT"});
    ST.health = Object.assign({}, ST.health, {state: "active"});
    setProg({state: "ok", where: "top", text: "Updates are switched back on."});
  } catch(e){ setProg({state: "fail", where: "top", text: explain(e, "switch the workflow on")}); }
  finally { ST.busy = false; renderAll(); }
}
async function checkHealth(){
  const [wf, runs, commits] = await Promise.all([
    gh(WF).catch(() => null),
    gh(WF + "/runs?event=schedule&per_page=1").catch(() => null),
    gh(REPO + "/commits?sha=" + CFG.branch + "&path=" + encodeURIComponent(CFG.wfPath) + "&per_page=1").catch(() => null)]);
  const out = {checked: Date.now(), error: !runs, state: wf && wf.state};
  const r = runs && (runs.workflow_runs || [])[0];
  out.last = r ? r.created_at : null;
  const c = Array.isArray(commits) && commits[0];
  if (c){ out.wfBy = (c.author && c.author.login) || (c.committer && c.committer.login) || null; out.wfAt = c.commit && c.commit.committer && c.commit.committer.date; }
  ST.health = out;
}
function scheduleState(){
  const s = ST.health;
  if (!ST.token || !s || s.error) return null;
  if (s.state && s.state !== "active") return "disabled";
  const last = s.last ? Date.parse(s.last) : 0, changed = s.wfAt ? Date.parse(s.wfAt) : 0;
  const mine = s.wfBy && ST.login && s.wfBy.toLowerCase() === ST.login.toLowerCase();
  if (mine && changed > last && Date.now() - changed < 2 * 3600 * 1000) return "pending";
  if (!last) return "never";
  const d = new Date(), busyHours = d.getUTCDay() >= 1 && d.getUTCDay() <= 5 && d.getUTCHours() >= 2 && d.getUTCHours() <= 21;
  return Date.now() - last > (busyHours ? 3 : 12) * 3600 * 1000 ? "stopped" : "ok";
}
async function connect(tok, remember, errEl, btn){
  tok = String(tok || "").trim();
  if (!tok){ errEl.textContent = "Paste your key first."; return; }
  if (!/^[A-Za-z0-9_]{30,255}$/.test(tok)){ errEl.textContent = "That doesn't look like a GitHub key. Fine-grained keys start with github_pat_."; return; }
  btn.disabled = true; errEl.textContent = "Checking the key…";
  const prev = ST.token; ST.token = tok;
  try {
    const me = await gh("/user");
    await gh(REPO + "/contents/" + CFG.devPath + "?ref=" + CFG.branch);
    await gh(WF);
    ST.login = me && me.login;
    delItem(K_TOKEN); setItem(K_TOKEN, tok, remember);
    errEl.textContent = "";
    await afterConnect();
  } catch(e){ ST.token = prev; errEl.textContent = explain(e, "read this repository"); btn.disabled = false; }
}
async function afterConnect(){
  renderAll();
  if (!FULL) return;
  try { if (!ST.login){ const me = await gh("/user"); ST.login = me && me.login; } }
  catch(e){ if (e.status === 401){ disconnect(explain(e)); return; } }
  try { await loadDevs(); } catch(e){ ST.devError = explain(e, "read the log"); }
  await checkHealth();
  renderAll();
}
function disconnect(msg){
  delItem(K_TOKEN);
  Object.assign(ST, {token: null, login: null, dev: null, devSha: null, devError: null, health: null, manual: false});
  if (FULL) clearForm();
  renderAll();
  if (typeof msg === "string"){ const el = $("#dk-conn-err"); if (el) el.textContent = msg; }
}

/* ---------------- news bookkeeping ---------------- */
function hiddenSet(){ return readSet(K_HIDE) || new Set(); }
function saveHidden(set){ setItem(K_HIDE, JSON.stringify([...set].slice(-2500))); }
/* Headlines not seen on an earlier visit are "new"; nothing is new on the first visit. The full desk marks them seen. */
function idsOf(it){ return Array.isArray(it.ids) && it.ids.length ? it.ids : [it.id]; }
function newIds(){
  const N = ST.news;
  if (!N) return new Set();
  if (ST.newIdsFor === N.updated) return ST.newIds;
  const seen = readSet(K_SEEN), items = N.items || [];
  ST.newIds = seen ? new Set(items.filter(it => !idsOf(it).some(id => seen.has(id))).map(it => it.id)) : new Set();
  ST.newIdsFor = N.updated;
  if (FULL){ const all = new Set(seen || []); items.forEach(it => idsOf(it).forEach(id => all.add(id))); setItem(K_SEEN, JSON.stringify([...all].slice(-2500))); }
  return ST.newIds;
}
function loggedSets(){
  const urls = new Set(), titles = new Set();
  const add = e => { if (!e) return; if (e.source && e.source.url) urls.add(e.source.url); if (e.title) titles.add(normT(e.title)); };
  const d = DATA.devs || {};
  (d.entries || []).forEach(add); (d.upcoming || []).forEach(add);
  if (ST.dev){ ST.dev.entries.forEach(add); ST.dev.upcoming.forEach(add); }
  return {urls, titles};
}
function newsState(it, hid, lg){
  if (lg.urls.has(it.u) || lg.titles.has(normT(it.t)) || (it.more || []).some(m => lg.urls.has(m.u))) return "logged";
  return idsOf(it).some(id => hid.has(id)) ? "hidden" : "open";
}
function newCount(){
  const N = ST.news; if (!N) return 0;
  const fresh = newIds(), hid = hiddenSet(), lg = loggedSets();
  return (N.items || []).filter(it => fresh.has(it.id) && newsState(it, hid, lg) === "open").length;
}

/* ---------------- compact bar (both pages) ---------------- */
function actionButton(){
  const b = ST.token
    ? h("button", {type: "button", class: "dk-btn dk-refresh", onclick: refreshNow, title: "Fetch the latest prices and headlines now (about 2 minutes)"}, "Refresh now")
    : h("button", {type: "button", class: "ghost dk-refresh", onclick: reloadData, title: "Load the latest published prices and headlines"}, "Reload");
  b.disabled = ST.busy;
  return b;
}
function renderBar(){
  if (!barEl) return;
  barEl.hidden = false; barEl.textContent = "";
  const q = ST.quotes, n = ST.news, nc = newCount();
  const fresh = q && q.updated && Date.now() - Date.parse(q.updated) < 2 * 3600 * 1000;
  const parts = [
    h("span", {class: "dk-dot" + (q && q.updated ? (fresh ? "" : " stale") : " off"), "aria-hidden": "true"}),
    h("span", {class: "dk-bt"}, q && q.updated ? "Prices updated " + stamp(q.updated) : "Prices: 30 Sep 2026 snapshot",
      n && n.updated ? " · Headlines " + stamp(n.updated) + (nc ? " (" + nc + " new)" : "") : ""),
    behind() ? h("a", {class: "dk-fresh", href: freshUrl(behind()), text: "This page has been updated: load the new version"}) : null,
    actionButton(), prog("any"),
    h("a", {class: "dk-link", href: CFG.deskUrl, text: FULL ? "Update desk ↓" : "Update desk →"})];
  barEl.append(...parts.filter(Boolean));   // DOM append() would print a null as text
  paintProg();
}

/* ---------------- full desk (Supply Chain Atlas page) ---------------- */
function renderStatus(){
  const box = $("#dk-status"); if (!box) return;
  box.textContent = "";
  const q = ST.quotes, n = ST.news, rep = q && q.report, total = q && q.quotes ? Object.keys(q.quotes).length : 0;
  const cell = (label, value, sub, cls) => h("div", {class: "dk-cell" + (cls ? " " + cls : "")}, h("div", {class: "dk-lab", text: label}), h("div", {class: "dk-val", text: value}), sub ? h("div", {class: "dk-subv", text: sub}) : null);
  const nc = newCount();
  let auto;
  if (ST.token){
    const st = scheduleState(), s = ST.health || {};
    const map = {
      ok: ["Running", "Last ran " + stamp(s.last), ""], pending: ["Turned on", "Waiting for the first scheduled run", ""],
      never: ["Not running yet", "Turn them on below", "warn"], stopped: ["Stopped", "Last ran " + stamp(s.last), "warn"],
      disabled: ["Switched off", "GitHub paused the schedule", "warn"]};
    const m = map[st] || ["Every 15 minutes", ST.health ? "Couldn't check GitHub" : "Checking…", ""];
    auto = cell("Automatic updates", m[0], m[1], m[2]);
  } else {
    const b = ST.build;
    auto = cell("Site rebuilt", b && b.built ? stamp(b.built) : "—", b && b.built ? ago(b.built) : "Every 15 minutes on weekdays");
  }
  box.append(
    cell("Prices", q && q.updated ? stamp(q.updated) : "30 Sep snapshot",
      q && q.updated ? ago(q.updated) + (rep && total ? " · " + rep.prices_ok + " of " + total + " from Yahoo" : "") : "Live prices appear after the first update"),
    cell("Analyst targets", q && q.targetsUpdated ? stamp(q.targetsUpdated) : "Not yet", "Refreshed once a day"),
    cell("Headlines", n && n.updated ? stamp(n.updated) : "Not yet",
      n ? (n.items || []).length + " stories from the last " + (n.days || 10) + " days" + (nc ? " · " + nc + " new" : "") : "Collected every 3 hours"),
    auto,
    h("div", {class: "dk-cell dk-act"}, actionButton(), prog("top")));
  paintProg();
}
function renderAlert(){
  const box = $("#dk-alert"); if (!box) return;
  box.textContent = ""; box.hidden = true;
  if (!ST.token) return;
  const st = scheduleState();
  if (st === "never" || st === "stopped"){
    const card = h("div", {class: "dk-alertcard warn"},
      h("b", {text: st === "never" ? "Automatic updates haven't started." : "Automatic updates seem to have stopped."}), " ",
      st === "never"
        ? "GitHub runs the schedule under the account that last changed it, and that was an account that can't run it here. Changing it once from your account fixes this; the button does it for you."
        : "GitHub stops a schedule when the account that last changed it can't run it, and sometimes skips runs when it is busy. Changing the schedule once from your account usually restarts it; the button does it for you.");
    if (ST.manual) card.append(h("p", null, "Your key can't edit workflow files. Either add “Workflows: Read and write” to the key on GitHub and press the button again, or ",
      h("a", {href: CFG.repoUrl + "/edit/" + CFG.branch + "/" + CFG.wfPath, target: "_blank", rel: "noopener", text: "open the workflow file on GitHub"}),
      ", change each number before the first space in the two cron lines by one (for example 7,22,37,52 to 8,23,38,53) and press Commit changes."));
    card.append(h("div", {class: "dk-alertact"}, h("button", {type: "button", class: "dk-btn dk-busy-off", onclick: turnOnSchedule}, "Turn on automatic updates")));
    box.append(card);
  } else if (st === "disabled"){
    const why = ST.health.state === "disabled_inactivity" ? "GitHub pauses schedules in public repositories after 60 days without a commit." : "The workflow was switched off on the Actions tab.";
    box.append(h("div", {class: "dk-alertcard warn"}, h("b", {text: "Automatic updates are switched off on GitHub."}), " ", why,
      h("div", {class: "dk-alertact"}, h("button", {type: "button", class: "dk-btn dk-busy-off", onclick: enableWorkflow}, "Switch them back on"))));
  }
  const w = (ST.build && ST.build.warnings) || [];
  if (w.length){
    const ul = h("ul"); w.slice(0, 8).forEach(x => ul.append(h("li", {text: x})));
    if (w.length > 8) ul.append(h("li", {text: "…and " + (w.length - 8) + " more"}));
    box.append(h("div", {class: "dk-alertcard crit"},
      h("b", {text: w.length === 1 ? "One part of the log was left out of the last build." : w.length + " parts of the log were left out of the last build."}),
      ul, h("p", {text: "The rest of the site built normally. Fix these with Edit under Your log, or in data/developments.json on GitHub."})));
  }
  box.hidden = !box.childNodes.length;
  paintButtons();
}

/* news radar */
function renderNews(){
  const box = $("#dk-news"); if (!box) return;
  box.textContent = "";
  const N = ST.news;
  box.append(h("div", {class: "dk-head"}, h("h3", {text: "News radar"}),
    N && N.updated ? h("span", {class: "dk-sub", text: "Google News, last " + (N.days || 10) + " days · updated " + stamp(N.updated)}) : null));
  if (N && (N.items || []).length) box.append(h("p", {class: "dk-sub dk-radarnote", text: "Reports of the same story are grouped. Nothing here reaches the pages until it is added to the log."}));
  if (!N || !(N.items || []).length){
    box.append(h("p", {class: "dk-empty", text: ST.token ? "No headlines yet. Press Refresh now to collect them." : "Headlines appear here after the next update."}));
    return;
  }
  const topics = new Map((N.topics || []).map(t => [t.id, t]));
  const fresh = newIds(), hid = hiddenSet(), lg = loggedSets();
  const visible = it => ST.newsAll || newsState(it, hid, lg) === "open";
  const count = {}; (N.items || []).forEach(it => { if (visible(it)) (it.topics || []).forEach(t => { count[t] = (count[t] || 0) + 1; }); });
  const sel = h("select", {id: "dk-topic", "aria-label": "Topic"});
  sel.append(h("option", {value: "all"}, "All topics"));
  (N.topics || []).forEach(t => sel.append(h("option", {value: t.id}, t.label + " (" + (count[t.id] || 0) + ")")));
  sel.value = topics.has(ST.newsTopic) ? ST.newsTopic : "all";
  sel.addEventListener("change", () => { ST.newsTopic = sel.value; ST.newsLimit = 20; renderNews(); });
  const chk = h("input", {type: "checkbox", id: "dk-allnews"}); chk.checked = ST.newsAll;
  chk.addEventListener("change", () => { ST.newsAll = chk.checked; ST.newsLimit = 20; renderNews(); });
  box.append(h("div", {class: "filters dk-nf"}, sel, h("label", {class: "chk", for: "dk-allnews"}, chk, "Show hidden and logged")));
  const list = (N.items || []).filter(it => (ST.newsTopic === "all" || (it.topics || []).includes(ST.newsTopic)) && visible(it));
  const ol = h("ol", {class: "dk-nlist"});
  list.slice(0, ST.newsLimit).forEach(it => {
    const u = safeUrl(it.u), st = newsState(it, hid, lg);
    const meta = h("div", {class: "dk-nmeta"}, h("span", {text: ago(it.d) || localDate(it.d)}), it.src ? h("span", {text: it.src}) : null,
      it.n > 1 ? h("span", {text: it.n + " reports"}) : null,
      st === "open" && fresh.has(it.id) ? h("span", {class: "dk-new", text: "New"}) : null,
      st !== "open" ? h("span", {class: "dk-tag", text: st === "logged" ? "In the log" : "Hidden"}) : null);
    const title = u ? h("a", {class: "dk-nt", href: u, target: "_blank", rel: "noopener noreferrer", text: it.t}) : h("span", {class: "dk-nt", text: it.t});
    const tps = h("div", {class: "dk-ntopics"});
    (it.topics || []).forEach(id => { const t = topics.get(id); if (t) tps.append(h("span", {class: "dk-chip", text: t.label})); });
    let also = null;
    const more = (it.more || []).filter(m => m && m.src);
    if (more.length){
      also = h("div", {class: "dk-also"}, "Also: ");
      more.forEach((m, i) => { const mu = safeUrl(m.u); also.append(i ? ", " : "", mu ? h("a", {href: mu, target: "_blank", rel: "noopener noreferrer", text: m.src}) : m.src); });
      const rest = (it.n || 0) - 1 - more.length;
      if (rest > 0) also.append(" and " + rest + " more");
    }
    const act = h("div", {class: "dk-nact"},
      st !== "logged" ? h("button", {type: "button", class: "ghost", onclick: () => fillFromNews(it, topics)}, ST.token ? "Add to log" : "Suggest for the log") : null,
      st === "hidden" ? h("button", {type: "button", class: "ghost", onclick: () => { idsOf(it).forEach(id => hid.delete(id)); saveHidden(hid); renderNews(); renderBar(); renderStatus(); }}, "Unhide")
        : st === "open" ? h("button", {type: "button", class: "ghost", onclick: () => { idsOf(it).forEach(id => hid.add(id)); saveHidden(hid); renderNews(); renderBar(); renderStatus(); }}, "Hide") : null);
    ol.append(h("li", {class: "dk-ni"}, meta, title, also, tps, act));
  });
  box.append(ol);
  if (!list.length) box.append(h("p", {class: "dk-empty", text: "Nothing new here. Tick “Show hidden and logged” to see everything."}));
  if (list.length > ST.newsLimit) box.append(h("button", {type: "button", class: "ghost dk-more", onclick: () => { ST.newsLimit += 20; renderNews(); }}, "Show " + Math.min(20, list.length - ST.newsLimit) + " more"));
}

/* entry form */
const OPT = {};
const F = {kind: "entry", links: [], changes: [], editing: null};
const RATING = {critical: "Critical", serious: "Serious", warning: "Watch"};
const CHANGES = {
  node_status: {label: "Re-rate a chokepoint", f: [["node", "Chokepoint", "chokes"], ["status", "New rating", "rating"], ["line", "One-line summary shown with the rating", "text"]], req: ["node"], any: ["status", "line"],
    hint: c => { const n = S.NODE[c.node]; return n && n.choke ? "Now: " + (RATING[n.choke.status] || n.choke.status) + (n.choke.line ? " · " + n.choke.line : "") : ""; }},
  node_note: {label: "Add a note to a link in the chain", f: [["node", "Link", "nodes"], ["text", "Sentence to add to its explanation", "text"]], req: ["node", "text"]},
  site_status: {label: "Change a map site's status", f: [["site", "Site", "sites"], ["status", "Status", "sitestatus"], ["note", "Replace the site's note", "text"]], req: ["site"], any: ["status", "note"],
    hint: c => { const s = (DATA.sites || []).find(x => x.id === c.site); return s ? "Now: " + OPT.name("sitestatus", s.status || "normal") + (s.note ? " · " + s.note : "") : ""; }},
  scenario_status: {label: "Move a worst-case scenario", f: [["scenario", "Scenario", "scen"], ["status", "Now", "scenstatus"], ["when", "When (shown on the scenario)", "text"]], req: ["scenario"], any: ["status", "when"],
    hint: c => { const s = S.SC[c.scenario]; return s ? "Now: " + OPT.name("scenstatus", s.status) + (s.when ? " · " + s.when : "") : ""; }},
  quote_note: {label: "Update a watchlist projection", f: [["company", "Company", "companies"], ["proj", "Projection to follow", "text"]], req: ["company", "proj"],
    hint: c => { const q = S.QU[c.company]; return q && q.proj ? "Now: " + q.proj : ""; }},
  atlas_item_status: {label: "Update an Investment Atlas project", f: [["item", "Project", "atlas"], ["status", "New status", "status"], ["note_append", "Sentence to add to its note", "text"]], req: ["item"], any: ["status", "note_append"],
    hint: c => { const a = (DATA.atlas || []).find(x => x.id === c.item); return a && a.s ? "Now: " + a.s : ""; }},
  add_site: {label: "Add a site to the map", f: [["name", "Name", "text"], ["who", "Company", "text"], ["node", "Link in the chain", "nodes"], ["lat", "Latitude", "lat"], ["lon", "Longitude", "lon"], ["status", "Status", "sitestatus"], ["note", "Note", "text"]], req: ["name", "node", "lat", "lon"],
    hint: () => "Tip: right-click the place in Google Maps and click the coordinates to copy them, then paste both into Latitude."},
  add_atlas_item: {label: "Add an Investment Atlas project", f: [["title", "Project", "text"], ["who", "Who", "text"], ["cat", "Category", "cat"], ["kind", "Type", "kind"], ["amount", "Amount, US$ billions", "number"], ["amount_note", "Amount note", "text"], ["date", "Announced (YYYY-MM)", "ym"], ["status", "Status", "status"], ["place", "Place", "text"], ["country", "Country", "countries"], ["lat", "Latitude", "lat"], ["lon", "Longitude", "lon"], ["prec", "Pin marks", "prec"], ["gw", "Gigawatts", "number"], ["partners", "Partners", "text"], ["note", "Note", "text"]], req: ["title", "who", "cat", "kind", "date", "place", "country", "lat", "lon"],
    hint: () => "Tip: right-click the place in Google Maps and click the coordinates to copy them, then paste both into Latitude."}
};
function buildOptions(){
  OPT.nodes = S.NODES.map(n => [n.id, n.short]);
  OPT.chokes = S.NODES.filter(n => n.choke).map(n => [n.id, n.short]);
  OPT.sites = (DATA.sites || []).map(s => [s.id, s.name]).sort((a, b) => a[1].localeCompare(b[1]));
  OPT.scen = (S.SCEN || []).map(s => [s.id, s.name]);
  OPT.companies = Object.keys(S.QU || {}).filter(k => S.CO[k]).map(k => [k, S.CO[k].n + (S.CO[k].t ? " (" + S.CO[k].t + ")" : "")]).sort((a, b) => a[1].localeCompare(b[1]));
  OPT.atlas = (DATA.atlas || []).filter(a => a.id).map(a => [a.id, a.t]).sort((a, b) => a[1].localeCompare(b[1]));
  OPT.rating = [["critical", "Critical"], ["serious", "Serious"], ["warning", "Watch"]];
  OPT.sitestatus = [["normal", "Operating"], ["ramping", "Ramping or under construction"], ["tight", "Tight supply"], ["short", "Short supply"], ["controlled", "Under export control"], ["offline", "Offline"], ["struck", "Struck"], ["threatened", "Threatened"], ["disrupted", "Disrupted"], ["at risk", "At risk"]];
  OPT.scenstatus = [["live", "Happening now"], ["scheduled", "On the calendar"], ["plausible", "Plausible"], ["tail", "Tail risk"]];
  OPT.cat = [["compute", "Data centers & power"], ["chips", "Chips & manufacturing"], ["funding", "AI company funding"]];
  OPT.kind = [["site", "Site"], ["program", "Pledge or multi-site plan"], ["funding", "Funding round"]];
  OPT.prec = [["city", "The city"], ["site", "The exact site"], ["region", "The region"], ["hq", "The company's headquarters"], ["country", "The country"]];
  OPT.countries = (CFG.countries || []).map(c => [c, c]);
  OPT.name = (list, id) => { const r = (OPT[list] || []).find(x => x[0] === id); return r ? r[1] : String(id == null ? "" : id); };
  OPT.pick = [];
  S.NODES.forEach(n => OPT.pick.push({kind: "nodes", id: n.id, label: "Chain link · " + n.short}));
  OPT.scen.forEach(([k, l]) => OPT.pick.push({kind: "scenarios", id: k, label: "Scenario · " + l}));
  OPT.companies.forEach(([k, l]) => OPT.pick.push({kind: "companies", id: k, label: "Company · " + l}));
  OPT.sites.forEach(([k, l]) => OPT.pick.push({kind: "sites", id: k, label: "Site · " + l}));
  OPT.atlas.forEach(([k, l]) => OPT.pick.push({kind: "atlasItems", id: k, label: "Investment · " + l}));
  OPT.byLabel = new Map(OPT.pick.map(p => [p.label, p]));
  OPT.byKey = new Map(OPT.pick.map(p => [p.kind + ":" + p.id, p]));
}
function buildForm(){
  buildOptions();
  const box = $("#dk-form"); box.textContent = "";
  const dl = h("datalist", {id: "dk-link-list"}); OPT.pick.forEach(p => dl.append(h("option", {value: p.label})));
  const sl = h("datalist", {id: "dk-status-list"}); ["Announced", "Planned", "Signed", "Under construction", "Operating", "Expanding", "Delayed", "At risk", "Paused", "Cancelled"].forEach(v => sl.append(h("option", {value: v})));
  const linkIn = h("input", {type: "text", id: "dk-link-in", list: "dk-link-list", autocomplete: "off", placeholder: "Type to search: CoWoS, TSMC, Taiwan, Ras Laffan…"});
  const addLink = () => {
    const p = OPT.byLabel.get(linkIn.value.trim());
    if (!p) return false;
    if (!F.links.includes(p)) F.links.push(p);
    linkIn.value = ""; renderLinks(); return true;
  };
  linkIn.addEventListener("input", () => { if (OPT.byLabel.has(linkIn.value.trim())) addLink(); });
  linkIn.addEventListener("keydown", e => { if (e.key === "Enter"){ e.preventDefault(); if (!addLink() && linkIn.value.trim()) showErr("Pick one of the suggestions in the list."); } });
  const chSel = h("select", {id: "dk-ch-add", "aria-label": "Add a change"});
  chSel.append(h("option", {value: ""}, "Add a change…"));
  Object.keys(CHANGES).forEach(k => chSel.append(h("option", {value: k}, CHANGES[k].label)));
  chSel.addEventListener("change", () => { if (chSel.value){ F.changes.push({type: chSel.value}); chSel.value = ""; renderChanges(); } });
  const lab = (id, text, input, req) => h("label", {class: "dk-f" + (req ? " req" : ""), for: id}, h("span", {text}), input);
  box.append(
    h("div", {class: "dk-head"}, h("h3", {id: "dk-form-title", text: "Add a development"}), h("span", {class: "dk-sub", id: "dk-form-sub"})),
    h("div", {class: "dk-editing", id: "dk-editing", hidden: true}),
    h("div", {class: "dk-fields"},
      h("div", {class: "seg", id: "dk-kind", role: "group", "aria-label": "Entry type"},
        h("button", {type: "button", "data-k": "entry", onclick: () => setKind("entry")}, "Development"),
        h("button", {type: "button", "data-k": "upcoming", onclick: () => setKind("upcoming")}, "Coming up")),
      h("div", {class: "dk-row2"}, lab("dk-date", "Date", h("input", {type: "date", id: "dk-date", value: todayISO()}), true),
        h("label", {class: "dk-f", for: "dk-approx", id: "dk-approx-wrap", hidden: true}, h("span", {text: "Show the date as (optional)"}), h("input", {type: "text", id: "dk-approx", placeholder: "Mid-2027"}))),
      lab("dk-title", "Headline", h("input", {type: "text", id: "dk-title", maxlength: "220"}), true),
      lab("dk-summary", "What happened and why it matters", h("textarea", {id: "dk-summary", rows: "3", maxlength: "1500", placeholder: "Two or three sentences with the numbers that matter."})),
      h("div", {class: "dk-row2"}, lab("dk-srclabel", "Source name", h("input", {type: "text", id: "dk-srclabel", placeholder: "Reuters, 1 Oct 2026"})),
        lab("dk-srcurl", "Source link", h("input", {type: "url", id: "dk-srcurl", placeholder: "https://"}))),
      h("div", {class: "dk-f"}, h("span", {text: "Show it on"}), h("div", {class: "dk-checks"},
        h("label", {class: "chk", for: "dk-pg-supply"}, h("input", {type: "checkbox", id: "dk-pg-supply", checked: true}), "Supply Chain Atlas"),
        h("label", {class: "chk", for: "dk-pg-atlas"}, h("input", {type: "checkbox", id: "dk-pg-atlas", checked: true}), "Investment Atlas"))),
      h("div", {class: "dk-f"}, h("label", {for: "dk-link-in", text: "Connect it to"}), linkIn, dl, sl, h("div", {class: "nchips", id: "dk-link-chips"})),
      h("div", {class: "dk-f", id: "dk-chwrap"}, h("span", {text: "Change the pages (optional)"}), h("div", {id: "dk-ch-list"}), chSel),
      h("div", {class: "dk-err", id: "dk-err", role: "alert"}),
      h("div", {class: "dk-actions"},
        h("button", {type: "button", class: "dk-btn", id: "dk-publish", onclick: publish}, "Publish"),
        h("button", {type: "button", class: "ghost", onclick: showPreview}, "Preview"),
        h("button", {type: "button", class: "ghost", onclick: clearForm}, "Clear"),
        prog("form")),
      h("div", {class: "dk-preview", id: "dk-preview", hidden: true})));
  setKind("entry"); renderLinks(); renderChanges();
}
function setKind(k){
  F.kind = k;
  document.querySelectorAll("#dk-kind button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.k === k)));
  $("#dk-approx-wrap").hidden = k !== "upcoming";
  $("#dk-chwrap").hidden = k !== "entry";
  renderFormMode();
}
function renderFormMode(){
  if (!$("#dk-form-title")) return;
  $("#dk-form-title").textContent = F.editing ? "Edit entry" : F.kind === "upcoming" ? "Add a dated event" : "Add a development";
  $("#dk-form-sub").textContent = ST.token ? "Publishes to both pages in about two minutes" : "Not connected: this opens a suggestion on GitHub";
  const ed = $("#dk-editing"); ed.textContent = "";
  ed.hidden = !F.editing;
  if (F.editing) ed.append(h("span", null, "Editing “", h("b", {text: F.editing.title}), "”"), h("button", {type: "button", class: "ghost", onclick: clearForm}, "Cancel editing"));
  $("#dk-publish").textContent = ST.token ? (F.editing ? "Save changes" : "Publish") : "Suggest on GitHub";
}
function renderLinks(){
  const box = $("#dk-link-chips"); if (!box) return;
  box.textContent = "";
  F.links.forEach((p, i) => box.append(h("button", {type: "button", class: "nchip", title: "Remove", onclick: () => { F.links.splice(i, 1); renderLinks(); }}, p.label + " ×")));
}
function renderChanges(){
  const box = $("#dk-ch-list"); if (!box) return;
  box.textContent = "";
  F.changes.forEach((c, i) => {
    const def = CHANGES[c.type]; if (!def) return;
    const grid = h("div", {class: "dk-chgrid"}), hint = h("p", {class: "dk-hint"});
    const paintHint = () => { hint.textContent = def.hint ? def.hint(c) : ""; };
    const inputs = {};
    def.f.forEach(([key, label, kind]) => {
      const id = "dk-c" + i + "-" + key;
      let input;
      if (kind === "status") input = h("input", {id, type: "text", list: "dk-status-list"});
      else if (OPT[kind]){ input = h("select", {id}); input.append(h("option", {value: ""}, "Choose…")); OPT[kind].forEach(([v, l]) => input.append(h("option", {value: v}, l))); }
      else if (kind === "lat" || kind === "lon" || kind === "number") input = h("input", {id, type: "text", inputmode: "decimal"});
      else if (kind === "ym") input = h("input", {id, type: "text", placeholder: "2026-10"});
      else input = h("input", {id, type: "text"});
      input.value = c[key] == null ? "" : String(c[key]);
      inputs[key] = input;
      const sync = () => {
        const m = kind === "lat" && /^\s*(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)\s*$/.exec(input.value);
        if (m && inputs.lon){ input.value = m[1]; inputs.lon.value = m[2]; c.lon = m[2]; }
        c[key] = input.value; paintHint();
      };
      input.addEventListener("input", sync); input.addEventListener("change", sync);
      grid.append(h("label", {class: "dk-f" + (def.req.includes(key) ? " req" : ""), for: id}, h("span", {text: label}), input));
    });
    paintHint();
    box.append(h("fieldset", {class: "dk-ch"},
      h("legend", null, def.label, h("button", {type: "button", class: "xbtn", "aria-label": "Remove this change", onclick: () => { F.changes.splice(i, 1); renderChanges(); }}, "×")), hint, grid));
  });
}
function showErr(msg){ const el = $("#dk-err"); if (el) el.textContent = msg || ""; }
function clearForm(){
  if (!$("#dk-form-title")) return;
  F.kind = "entry"; F.links = []; F.changes = []; F.editing = null;
  ["dk-approx", "dk-title", "dk-summary", "dk-srclabel", "dk-srcurl", "dk-link-in"].forEach(id => { const el = document.getElementById(id); if (el) el.value = ""; });
  $("#dk-date").value = todayISO();
  ["dk-pg-supply", "dk-pg-atlas"].forEach(id => { document.getElementById(id).checked = true; });
  const pv = $("#dk-preview"); pv.hidden = true; pv.textContent = "";
  showErr(""); setKind("entry"); renderLinks(); renderChanges();
}
/* Read the form into an entry. Throws an Error listing everything that needs fixing. */
function collect(){
  const err = [];
  const v = id => (document.getElementById(id).value || "").trim();
  const kind = F.kind, date = v("dk-date"), title = v("dk-title"), summary = v("dk-summary"), sl = v("dk-srclabel"), su = v("dk-srcurl"), approx = v("dk-approx");
  const pages = []; if ($("#dk-pg-supply").checked) pages.push("supply"); if ($("#dk-pg-atlas").checked) pages.push("atlas");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) err.push("Pick a date.");
  if (!title) err.push("Write a headline.");
  if (su && !safeUrl(su)) err.push("The source link has to start with https://.");
  if (!pages.length) err.push("Choose at least one page to show it on.");
  if (kind === "upcoming" && date && date < todayISO() && !F.editing) err.push("A coming-up date has to be today or later.");
  const links = {};
  F.links.forEach(p => { (links[p.kind] = links[p.kind] || []).push(p.id); });
  const changes = [];
  const siteIds = new Set((DATA.sites || []).map(s => s.id)), itemIds = new Set((DATA.atlas || []).map(a => a.id));
  if (kind === "entry") F.changes.forEach(c => {
    const def = CHANGES[c.type]; if (!def) return;
    const keys = new Set(def.f.map(x => x[0])), out = {type: c.type}, missing = [];
    for (const k in c) if (k !== "type" && k[0] !== "_" && !keys.has(k) && c[k] != null && c[k] !== "") out[k] = c[k];   // keep fields the form doesn't show
    def.f.forEach(([key, label, k]) => {
      let val = c[key] == null ? "" : String(c[key]).trim();
      if (!val){ delete out[key]; if (def.req.includes(key)) missing.push(label.toLowerCase()); return; }
      if (k === "lat" || k === "lon" || k === "number"){
        const n = Number(k === "number" ? val.replace(/[$,\s]/g, "") : val);
        if (!isFinite(n)){ err.push(def.label + ": " + label.toLowerCase() + " has to be a number."); return; }
        if (k === "lat" && Math.abs(n) > 90){ err.push(def.label + ": latitude has to be between -90 and 90."); return; }
        if (k === "lon" && Math.abs(n) > 180){ err.push(def.label + ": longitude has to be between -180 and 180."); return; }
        val = n;
      }
      if (k === "ym" && !/^\d{4}-\d{2}$/.test(val)){ err.push(def.label + ": the date has to look like 2026-10."); return; }
      out[key] = val;
    });
    if (missing.length) err.push(def.label + ": add the " + missing.join(", ") + ".");
    if (def.any && !def.any.some(k => out[k] != null && out[k] !== "")) err.push(def.label + ": fill in at least one of " + def.any.map(k => def.f.find(x => x[0] === k)[1].toLowerCase()).join(" or ") + ".");
    if (c.type === "add_site"){ out.id = c._id || uniqueId(slug(out.name || "site", 40), siteIds); siteIds.add(out.id); if (!out.status) out.status = "normal"; }
    if (c.type === "add_atlas_item"){
      const item = Object.assign({}, out); delete item.type;
      item.id = c._id || uniqueId(slug(item.title || "project", 40), itemIds); itemIds.add(item.id);
      if (!item.prec) item.prec = "city";
      changes.push({type: "add_atlas_item", item}); return;
    }
    changes.push(out);
  });
  if (err.length) throw new Error(err.join(" "));
  const e = {id: F.editing ? F.editing.id : null, date};
  if (kind === "upcoming" && approx) e.approx = approx;
  e.title = title;
  if (summary) e.summary = summary;
  e.pages = pages;
  if (Object.keys(links).length) e.links = links;
  if (su) e.source = {label: sl || hostOf(su), url: safeUrl(su)};
  if (changes.length) e.changes = changes;
  return {kind, entry: e};
}
function describeChange(c){
  const nm = OPT.name;
  switch (c.type){
    case "node_status": return "Re-rate " + nm("nodes", c.node) + (c.status ? " to " + nm("rating", c.status) : "") + (c.line ? ": " + c.line : "");
    case "node_note": return "Add to " + nm("nodes", c.node) + ": " + c.text;
    case "site_status": return nm("sites", c.site) + (c.status ? " becomes " + nm("sitestatus", c.status).toLowerCase() : "") + (c.note ? ": " + c.note : "");
    case "scenario_status": return nm("scen", c.scenario) + (c.status ? " moves to " + nm("scenstatus", c.status).toLowerCase() : "") + (c.when ? " (" + c.when + ")" : "");
    case "quote_note": return nm("companies", c.company) + " projection: " + c.proj;
    case "atlas_item_status": return nm("atlas", c.item) + (c.status ? " status: " + c.status : "") + (c.note_append ? (c.status ? "; " : " note: ") + c.note_append : "");
    case "add_site": return "New map site: " + c.name + " (" + nm("nodes", c.node) + ")";
    case "add_atlas_item": { const it = c.item || c; return "New Investment Atlas project: " + it.title + (it.amount != null && it.amount !== "" ? " ($" + it.amount + "B)" : ""); }
  }
  return c.type;
}
function showPreview(){
  const pv = $("#dk-preview");
  let res; try { res = collect(); } catch(e){ showErr(e.message); pv.hidden = true; return; }
  showErr("");
  const e = res.entry;
  pv.textContent = "";
  pv.append(h("div", {class: "dk-lab", text: (res.kind === "upcoming" ? "Coming up" : "Development") + " · preview"}),
    h("div", {class: "dv-date", text: e.approx || longDate(e.date)}), h("div", {class: "dv-t", text: e.title}));
  if (e.summary) pv.append(h("p", {class: "dv-s", text: e.summary}));
  if (F.links.length){ const w = h("div", {class: "nchips"}); F.links.forEach(p => w.append(h("span", {class: "nchip", text: p.label}))); pv.append(w); }
  if (e.source && e.source.url) pv.append(h("a", {class: "dv-src", href: e.source.url, target: "_blank", rel: "noopener", text: e.source.label}));
  if (e.changes){ const ul = h("ul", {class: "dk-chlist"}); e.changes.forEach(c => ul.append(h("li", {text: describeChange(c)}))); pv.append(ul); }
  pv.hidden = false;
}
function fillFromNews(it, topics){
  clearForm();
  const d = localDate(it.first || it.d) || todayISO();
  $("#dk-date").value = d > todayISO() ? todayISO() : d;
  $("#dk-title").value = it.t;
  $("#dk-srclabel").value = (it.src ? it.src + ", " : "") + longDate($("#dk-date").value);
  $("#dk-srcurl").value = safeUrl(it.u) || "";
  (it.topics || []).forEach(id => {
    const t = topics.get(id), L = (t && t.links) || {};
    Object.keys(L).forEach(k => (L[k] || []).forEach(x => { const p = OPT.byKey.get(k + ":" + x); if (p && !F.links.includes(p)) F.links.push(p); }));
  });
  renderLinks();
  $("#dk-form").scrollIntoView({behavior: "smooth", block: "start"});
  setTimeout(() => $("#dk-summary").focus({preventScroll: true}), 450);
}
function editEntry(id){
  const dev = ST.dev; if (!dev) return;
  let kind = "entry", e = dev.entries.find(x => x.id === id);
  if (!e){ kind = "upcoming"; e = dev.upcoming.find(x => x.id === id); }
  if (!e) return;
  clearForm();
  F.editing = {id, kind, title: e.title};
  $("#dk-date").value = e.date || ""; $("#dk-approx").value = e.approx || ""; $("#dk-title").value = e.title || ""; $("#dk-summary").value = e.summary || "";
  $("#dk-srclabel").value = (e.source && e.source.label) || ""; $("#dk-srcurl").value = (e.source && e.source.url) || "";
  const pages = Array.isArray(e.pages) ? e.pages : ["supply", "atlas"];
  $("#dk-pg-supply").checked = pages.includes("supply"); $("#dk-pg-atlas").checked = pages.includes("atlas");
  const L = e.links || {};
  Object.keys(L).forEach(k => (Array.isArray(L[k]) ? L[k] : []).forEach(x => { const p = OPT.byKey.get(k + ":" + x); if (p && !F.links.includes(p)) F.links.push(p); }));
  F.changes = (e.changes || []).filter(c => c && CHANGES[c.type]).map(c => c.type === "add_atlas_item" ? Object.assign({_id: c.item && c.item.id}, c.item || {}, {type: c.type}) : Object.assign({_id: c.id}, c));
  setKind(kind); renderLinks(); renderChanges();
  $("#dk-form").scrollIntoView({behavior: "smooth", block: "start"});
}
async function publish(){
  let res; try { res = collect(); } catch(e){ showErr(e.message); return; }
  showErr("");
  if (!ST.token){ suggest(res); return; }
  const editing = F.editing, e = res.entry;
  await commitAndPublish(editing ? "Saving" : "Publishing", dev => {
    const taken = new Set(dev.entries.concat(dev.upcoming).map(x => x && x.id).filter(Boolean));
    let at = -1;
    if (editing){
      at = (editing.kind === "upcoming" ? dev.upcoming : dev.entries).findIndex(x => x && x.id === editing.id);
      dev.entries = dev.entries.filter(x => !x || x.id !== editing.id); dev.upcoming = dev.upcoming.filter(x => !x || x.id !== editing.id);
      e.id = editing.id;
    } else e.id = uniqueId(slug(e.date + "-" + e.title), taken);
    const list = res.kind === "upcoming" ? dev.upcoming : dev.entries;
    if (editing && editing.kind === res.kind && at >= 0) list.splice(at, 0, e); else list.unshift(e);
  }, (editing ? "Edit " : "Add ") + (res.kind === "upcoming" ? "upcoming event: " : "development: ") + e.title, "form");
}
function removeEntry(id, title){
  return commitAndPublish("Deleting", dev => {
    dev.entries = dev.entries.filter(x => !x || x.id !== id); dev.upcoming = dev.upcoming.filter(x => !x || x.id !== id);
  }, "Remove development: " + title, "log");
}
function suggest(res){
  const e = res.entry, lines = [];
  if (res.kind === "upcoming") lines.push("Coming-up event" + (e.approx ? " (shown as " + e.approx + ")" : ""));
  if (F.links.length) lines.push("Connected to: " + F.links.map(p => p.label).join("; "));
  (e.changes || []).forEach(c => lines.push("Change: " + describeChange(c)));
  const q = new URLSearchParams({template: "new-development.yml", title: "[Development] " + e.title, date: e.date, headline: e.title,
    summary: e.summary || "", source: (e.source && e.source.url) || "", change: lines.join("\n")});
  window.open(CFG.repoUrl + "/issues/new?" + q.toString(), "_blank", "noopener");
  setProg({state: "ok", where: "form", text: "Opened a suggestion on GitHub. Submit it there."});
}

/* your log */
function renderEntries(){
  const box = $("#dk-entries"); if (!box) return;
  box.textContent = "";
  box.append(h("div", {class: "dk-head"}, h("h3", {text: ST.token ? "Your log" : "Editing the log"}),
    h("a", {class: "dk-sub", href: CFG.repoUrl + "/blob/" + CFG.branch + "/" + CFG.devPath, target: "_blank", rel: "noopener", text: "Open the file on GitHub"})));
  if (!ST.token){ box.append(h("p", {class: "dk-empty", text: "The site owner edits and deletes entries here after connecting GitHub. Anyone can suggest a new one with the form above."})); return; }
  if (ST.devError){ box.append(h("p", {class: "dk-err", text: ST.devError})); return; }
  if (!ST.dev){ box.append(h("p", {class: "dk-empty", text: "Loading the log from GitHub…"})); return; }
  const row = e => {
    const act = h("span", {class: "dk-eact"});
    const reset = () => { act.textContent = ""; act.append(
      h("button", {type: "button", class: "ghost", onclick: () => editEntry(e.id)}, "Edit"),
      h("button", {type: "button", class: "ghost", onclick: () => { act.textContent = ""; act.append(h("span", {class: "dk-confirm", text: "Delete?"}),
        h("button", {type: "button", class: "ghost dk-danger", onclick: () => removeEntry(e.id, e.title)}, "Delete"),
        h("button", {type: "button", class: "ghost", onclick: reset}, "Keep")); paintButtons(); }}, "Delete")); paintButtons(); };
    reset();
    return h("li", {class: "dk-er"}, h("span", {class: "dv-date", text: e.approx || longDate(e.date)}), h("span", {class: "dk-et", title: e.title, text: e.title}), act);
  };
  const ok = x => x && typeof x === "object" && x.id;
  const a = h("ol", {class: "dk-elist"}); ST.dev.entries.filter(ok).slice().sort((x, y) => String(y.date).localeCompare(String(x.date))).forEach(e => a.append(row(e)));
  const b = h("ol", {class: "dk-elist"}); ST.dev.upcoming.filter(ok).slice().sort((x, y) => String(x.date).localeCompare(String(y.date))).forEach(e => b.append(row(e)));
  box.append(h("h4", {text: "Developments (" + ST.dev.entries.length + ")"}), a, h("h4", {text: "Coming up (" + ST.dev.upcoming.length + ")"}), b, prog("log"));
  paintButtons(); paintProg();
}

/* connect */
function renderConnect(){
  const box = $("#dk-connect"); if (!box) return;
  box.textContent = "";
  if (ST.token){
    box.append(h("h3", {text: "Connected to GitHub"}),
      h("p", {class: "dk-p"}, "Signed in as ", h("b", {text: ST.login || "…"}), ". Your key stays in this browser and is only sent to GitHub."),
      h("div", {class: "dk-actions"}, h("button", {type: "button", class: "ghost", onclick: () => disconnect()}, "Disconnect"),
        h("a", {class: "ghost", href: "https://github.com/settings/personal-access-tokens", target: "_blank", rel: "noopener", text: "Manage keys on GitHub"}),
        h("a", {class: "ghost", href: CFG.repoUrl + "/actions", target: "_blank", rel: "noopener", text: "Update history"})),
      h("p", {class: "dk-fine", text: "Keys expire. When this one does, GitHub emails you; create a new one with the same settings and connect it here."}));
    return;
  }
  const inp = h("input", {type: "password", id: "dk-token", autocomplete: "off", spellcheck: "false", placeholder: "github_pat_…"});
  const rem = h("input", {type: "checkbox", id: "dk-remember", checked: true});
  const err = h("div", {class: "dk-err", role: "alert", id: "dk-conn-err"});
  const btn = h("button", {type: "button", class: "dk-btn", onclick: () => connect(inp.value, rem.checked, err, btn)}, "Connect");
  inp.addEventListener("keydown", e => { if (e.key === "Enter") btn.click(); });
  box.append(h("h3", {text: "Site owner: connect GitHub"}),
    h("p", {class: "dk-p", text: "Connecting lets this page refresh the data on demand and publish entries, using a GitHub key that stays in this browser."}),
    h("ol", {class: "dk-steps"},
      h("li", null, h("a", {href: "https://github.com/settings/personal-access-tokens/new", target: "_blank", rel: "noopener", text: "Create a fine-grained key on GitHub"}), ". Name it, for example “Update desk”, and pick an expiry such as 90 days."),
      h("li", null, "Under Repository access choose ", h("b", {text: "Only select repositories"}), " and pick ", h("b", {text: "AI_Supply-Chain_Map"}), "."),
      h("li", null, "Under Permissions, add ", h("b", {text: "Contents"}), ", ", h("b", {text: "Actions"}), " and ", h("b", {text: "Workflows"}), ", each set to Read and write."),
      h("li", null, "Generate the key, copy it and paste it here.")),
    h("label", {class: "dk-f", for: "dk-token"}, h("span", {text: "GitHub key"}), inp),
    h("label", {class: "chk", for: "dk-remember"}, rem, "Remember on this device"),
    err, h("div", {class: "dk-actions"}, btn),
    h("p", {class: "dk-fine", text: "Anyone with the key can change this repository, so keep it private. Untick Remember on shared computers; you can delete the key on GitHub at any time."}));
}

function buildDesk(){
  deskEl.hidden = false; deskEl.textContent = "";
  deskEl.append(
    h("div", {class: "sec-head"}, h("h2", {text: "Update desk"}),
      h("p", {text: "Refresh prices and headlines, scan the news radar, and log what matters. Entries published here update both pages for everyone in about two minutes."})),
    h("div", {class: "dk-status card", id: "dk-status"}),
    h("div", {class: "dk-alert", id: "dk-alert", hidden: true}),
    h("div", {class: "dk-grid"}, h("div", {class: "card panel", id: "dk-news"}), h("div", {class: "card panel", id: "dk-form"})),
    h("div", {class: "dk-grid dk-grid2"}, h("div", {class: "card panel", id: "dk-entries"}), h("div", {class: "card panel", id: "dk-connect"})));
  buildForm();
}
function addTocLink(){
  const toc = document.querySelector("nav.toc");
  if (!toc || toc.querySelector("a[data-desk]")) return;
  const a = h("a", {href: CFG.deskUrl, "data-desk": "1", text: "Update desk"});
  const before = toc.querySelector('a[href="#log"]') || toc.querySelector("a.companion");
  before ? toc.insertBefore(a, before) : toc.append(a);
}
function renderAll(){
  renderBar();
  if (!FULL) return;
  renderStatus(); renderAlert(); renderNews(); renderFormMode(); renderEntries(); renderConnect();
  paintButtons();
}

const CSS = `
.desk-bar{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin-top:14px;padding:8px 12px;border:1px solid var(--line);border-radius:var(--r);background:var(--surface);font-size:var(--fs-sm);color:var(--ink-2)}
.desk-bar .dk-bt{flex:1 1 220px;min-width:0}
.desk-bar .dk-link{font-weight:600;color:var(--ink);white-space:nowrap;text-decoration:none}
.desk-bar .dk-link:hover{text-decoration:underline}
.desk-bar .dk-prog{flex:1 1 100%;order:9}
.desk-bar .dk-fresh{color:var(--ink);font-weight:600}
.dk-dot{width:8px;height:8px;border-radius:50%;background:var(--good);flex:none;box-shadow:0 0 0 3px color-mix(in srgb,var(--good) 22%,transparent)}
.dk-dot.stale{background:var(--warn);box-shadow:0 0 0 3px color-mix(in srgb,var(--warn) 25%,transparent)}
.dk-dot.off{background:var(--faint);box-shadow:none}
.dk-btn{border:1px solid var(--ink);background:var(--ink);color:var(--surface);border-radius:var(--r);padding:6px 13px;font:inherit;font-size:var(--fs-sm);font-weight:600;cursor:pointer;white-space:nowrap}
.dk-btn:hover{filter:brightness(1.2)}
.dk-btn:disabled,.desk-bar .ghost:disabled,#desk .ghost:disabled{opacity:.5;cursor:default;filter:none}
#desk a.ghost{text-decoration:none;display:inline-block}
.dk-prog{font-size:var(--fs-sm);color:var(--ink-2);min-width:0}
.dk-prog:empty{display:none}
.dk-prog.ok{color:var(--good-ink)} .dk-prog.fail{color:var(--crit-ink)}
.dk-prog a{color:inherit}
#desk .dk-status{display:grid;grid-template-columns:repeat(4,minmax(0,1fr)) minmax(0,1.3fr);gap:1px;background:var(--line);overflow:hidden}
#desk .dk-cell{background:var(--surface);padding:12px 14px;display:grid;gap:3px;align-content:start;min-width:0}
#desk .dk-cell.warn{box-shadow:inset 3px 0 0 var(--warn)}
#desk .dk-lab{font-family:var(--font-mono);font-size:var(--fs-xs);text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}
#desk .dk-val{font-size:18px;font-weight:600;line-height:1.2}
#desk .dk-subv{font-size:var(--fs-xs);color:var(--muted)}
#desk .dk-act{align-content:center;justify-items:start;gap:8px}
#desk .dk-alert{display:grid;gap:10px;margin-top:12px}
.dk-alertcard{border:1px solid var(--line);border-radius:var(--r);padding:12px 14px;background:var(--surface);font-size:var(--fs-sm);color:var(--ink-2);max-width:none}
.dk-alertcard b{color:var(--ink)}
.dk-alertcard.warn{border-color:color-mix(in srgb,var(--warn) 65%,transparent);background:color-mix(in srgb,var(--warn) 9%,var(--surface))}
.dk-alertcard.crit{border-color:color-mix(in srgb,var(--crit) 50%,transparent);background:color-mix(in srgb,var(--crit) 6%,var(--surface))}
.dk-alertcard ul{margin:6px 0;padding-left:18px}
.dk-alertcard p{margin:6px 0 0}
.dk-alertact{margin-top:10px}
#desk .dk-grid{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:14px;margin-top:14px;align-items:start}
#desk .dk-head{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;justify-content:space-between;margin-bottom:8px}
#desk .dk-sub{font-size:var(--fs-xs);color:var(--muted)}
#desk a.dk-sub{color:var(--ink-2)}
#desk .dk-empty{color:var(--muted);font-size:var(--fs-sm);margin:6px 0}
#desk .dk-p{font-size:var(--fs-sm);color:var(--ink-2);margin:6px 0 10px}
#desk .dk-radarnote{margin:0 0 8px}
#desk .dk-nf{margin:4px 0 6px}
#desk .dk-nf select{width:auto;max-width:100%}
.dk-nlist{list-style:none;margin:0;padding:0;display:grid;max-height:780px;overflow:auto}
.dk-ni{display:grid;gap:5px;padding:10px 0;border-top:1px solid var(--grid)}
.dk-nmeta{display:flex;flex-wrap:wrap;gap:4px 10px;font-size:var(--fs-xs);color:var(--muted);font-family:var(--font-mono)}
.dk-new{color:var(--good-ink);font-weight:600}
.dk-tag{color:var(--ink-2)}
.dk-nt{font-weight:600;font-size:var(--fs-sm);color:var(--ink);line-height:1.35;text-decoration:none}
a.dk-nt:hover{text-decoration:underline}
.dk-also{font-size:var(--fs-xs);color:var(--muted)}
.dk-also a{color:var(--ink-2)}
.dk-ntopics{display:flex;flex-wrap:wrap;gap:4px}
.dk-chip{font-size:10.5px;border:1px solid var(--line);border-radius:999px;padding:1px 7px;color:var(--ink-2)}
.dk-nact{display:flex;gap:6px;flex-wrap:wrap}
.dk-nact .ghost,.dk-eact .ghost{padding:3px 9px;font-size:var(--fs-xs)}
.dk-more{margin-top:10px}
.dk-fields{display:grid;gap:11px}
.dk-f{display:grid;gap:4px;min-width:0}
.dk-f > span:first-child,.dk-f > label:first-child{font-family:var(--font-mono);font-size:var(--fs-xs);text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.dk-f.req > span:first-child::after{content:" *";color:var(--crit-ink)}
.dk-row2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px}
#desk input[type=text],#desk input[type=url],#desk input[type=date],#desk input[type=password],#desk textarea,#desk select{width:100%;border:1px solid var(--line);border-radius:var(--r);background:var(--surface);color:var(--ink);padding:6px 9px;font:inherit;font-size:var(--fs-sm);min-width:0}
#desk textarea{resize:vertical;min-height:66px}
.dk-checks{display:flex;flex-wrap:wrap;gap:6px 16px}
.dk-ch{border:1px solid var(--line);border-radius:var(--r);padding:8px 10px 10px;margin:0 0 8px;min-width:0}
.dk-ch legend{font-size:var(--fs-sm);font-weight:600;display:flex;gap:6px;align-items:center;padding:0 4px}
.dk-chgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.dk-hint{font-size:var(--fs-xs);color:var(--muted);margin:0 0 8px}
.dk-hint:empty{display:none}
.dk-err{color:var(--crit-ink);font-size:var(--fs-sm)}
.dk-err:empty{display:none}
.dk-actions{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.dk-preview{border:1px dashed var(--border);border-radius:var(--r);padding:10px 12px;display:grid;gap:4px}
.dk-preview .dv-s{margin:2px 0}
.dk-chlist{margin:4px 0 0;padding-left:18px;font-size:var(--fs-sm);color:var(--ink-2)}
.dk-editing{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;background:var(--wash);border-radius:var(--r);padding:8px 10px;font-size:var(--fs-sm);margin-bottom:10px}
.dk-elist{list-style:none;margin:4px 0 14px;padding:0;max-height:330px;overflow:auto}
.dk-er{display:grid;grid-template-columns:96px minmax(0,1fr) auto;gap:8px;align-items:center;padding:6px 0;border-bottom:1px solid var(--grid);font-size:var(--fs-sm)}
.dk-et{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dk-eact{display:flex;gap:4px;align-items:center}
.dk-danger{color:var(--crit-ink)!important;border-color:color-mix(in srgb,var(--crit) 50%,transparent)!important}
.dk-confirm{font-size:var(--fs-xs);color:var(--ink-2)}
.dk-steps{margin:0 0 12px;padding-left:20px;display:grid;gap:6px;font-size:var(--fs-sm);color:var(--ink-2)}
.dk-fine{font-size:var(--fs-xs);color:var(--muted);margin:10px 0 0}
#desk .dk-grid2 h4{margin:10px 0 2px}
#dk-connect .dk-f{margin:4px 0 8px}
@media (max-width:1099px){ #desk .dk-status{grid-template-columns:repeat(2,minmax(0,1fr))} #desk .dk-act{grid-column:1/-1} #desk .dk-grid{grid-template-columns:minmax(0,1fr)} }
@media (max-width:560px){ .dk-row2,.dk-chgrid{grid-template-columns:minmax(0,1fr)} .dk-er{grid-template-columns:minmax(0,1fr) auto} .dk-er .dv-date{display:none} }
`;

/* GitHub Pages caches each page for about 10 minutes. If the published build is newer than this copy
   (a different commit), load the fresh one: automatically on arrival, or with a link once someone is reading. */
const cameWith = (/[?&]v=([\w-]+)/.exec(location.search) || [])[1] || null;
function behind(){ const live = ST.build && ST.build.rev; return live && DATA.rev && live !== DATA.rev ? live : null; }
function freshUrl(v){ return location.pathname + "?v=" + encodeURIComponent(v) + location.hash; }
function reloadIfBehind(){
  const live = behind();
  if (!live || cameWith === live || getItem("aiscm.rev") === live) return false;
  setItem("aiscm.rev", live, false);
  location.replace(freshUrl(live));
  return true;
}
async function init(){
  document.head.append(h("style", {text: CSS}));
  if (cameWith && history.replaceState) history.replaceState(null, "", location.pathname + location.hash);
  if (FULL) buildDesk();
  addTocLink();
  renderAll();
  await loadStatus();
  if (reloadIfBehind()) return;
  renderAll();
  if (ST.token) afterConnect();
  let lastPoll = Date.now();
  const poll = async () => {
    if (ST.busy || document.hidden) return;
    lastPoll = Date.now();
    const was = ST.news && ST.news.updated;
    await loadStatus();
    renderBar();
    if (FULL){ renderStatus(); renderAlert(); if (ST.news && ST.news.updated !== was) renderNews(); }
  };
  setInterval(poll, 5 * 60 * 1000);
  // catch up as soon as someone comes back to a tab that was in the background
  document.addEventListener("visibilitychange", () => { if (!document.hidden && Date.now() - lastPoll > 60 * 1000){ poll(); if (S.refreshLive) S.refreshLive(); } });
}
window.SCMAP_DESK = {rotateCron, slug, uniqueId, b64encode, b64decode, scheduleState, state: ST};
init();
})();
