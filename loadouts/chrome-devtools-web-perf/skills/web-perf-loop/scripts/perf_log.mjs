#!/usr/bin/env node
// Record page-speed measurements from Chrome DevTools traces and compare runs, so "faster" is a number, not a feeling.
// Usage:
//   node perf_log.mjs add --label before --url http://localhost:3000/ --lcp 3720 --cls 0.21 --inp 240 [--ttfb 900] [--note "..."]
//   node perf_log.mjs compare before after [--url URL]
//   node perf_log.mjs show
// Values: LCP, INP and TTFB in milliseconds, CLS unitless. Stored in .perf/runs.jsonl (one line per trace).
// compare uses the median of each label's runs (take 3 traces per state; single traces are noisy) and exits 1 when
// "after" is worse than "before" on any metric by more than the noise margin, or misses Google's "good" thresholds
// (LCP <= 2500 ms, INP <= 200 ms, CLS <= 0.1) that "before" met. Node standard library only; writes only .perf/.
import fs from "node:fs";
import path from "node:path";

const FILE = path.join(".perf", "runs.jsonl");
const GOOD = { lcp: 2500, inp: 200, cls: 0.1, ttfb: 800 };
const NOISE = { lcp: 100, inp: 20, cls: 0.01, ttfb: 100 }; // differences smaller than this are not a change
const METRICS = ["lcp", "cls", "inp", "ttfb"];

const args = process.argv.slice(2);
const opt = (n) => { const i = args.indexOf(`--${n}`); return i >= 0 ? args[i + 1] : undefined; };
const read = () => (fs.existsSync(FILE) ? fs.readFileSync(FILE, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)) : []);
const median = (xs) => { const s = [...xs].sort((a, b) => a - b); const m = Math.floor(s.length / 2); return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const fmt = (k, v) => (v === undefined ? "-" : k === "cls" ? v.toFixed(3) : `${Math.round(v)} ms`);

function add() {
  const label = opt("label"), url = opt("url");
  if (!label || !url) { console.error("add needs --label and --url"); process.exit(2); }
  const row = { at: new Date().toISOString(), label, url, note: opt("note") ?? "" };
  for (const k of METRICS) {
    const v = opt(k);
    if (v === undefined) continue;
    const n = Number(v);
    if (!Number.isFinite(n) || n < 0) { console.error(`--${k} must be a non-negative number`); process.exit(2); }
    row[k] = n;
  }
  if (row.lcp === undefined && row.cls === undefined && row.inp === undefined) { console.error("record at least one of --lcp, --cls, --inp"); process.exit(2); }
  fs.mkdirSync(".perf", { recursive: true });
  fs.appendFileSync(FILE, JSON.stringify(row) + "\n");
  const n = read().filter((r) => r.label === label && r.url === url).length;
  console.log(`recorded ${label} #${n} for ${url}${n < 3 ? ` (take ${3 - n} more for a stable median)` : ""}`);
}

function summary(rows) {
  const out = { n: rows.length };
  for (const k of METRICS) { const xs = rows.map((r) => r[k]).filter((v) => v !== undefined); if (xs.length) out[k] = median(xs); }
  return out;
}

function compare(a, b) {
  const url = opt("url");
  const rows = read().filter((r) => !url || r.url === url);
  const A = summary(rows.filter((r) => r.label === a)), B = summary(rows.filter((r) => r.label === b));
  if (!A.n || !B.n) { console.error(`need runs for both "${a}" and "${b}"`); process.exit(2); }
  let bad = 0;
  console.log(`metric   ${a.padEnd(10)} ${b.padEnd(10)} change     good`);
  for (const k of METRICS) {
    if (A[k] === undefined || B[k] === undefined) continue;
    const d = B[k] - A[k];
    let verdict = Math.abs(d) <= NOISE[k] ? "same" : d < 0 ? "better" : "WORSE";
    const goodB = B[k] <= GOOD[k];
    if (verdict === "WORSE") bad++;
    if (A[k] <= GOOD[k] && !goodB) { bad++; verdict += ", now misses good"; }
    console.log(`${k.toUpperCase().padEnd(8)} ${fmt(k, A[k]).padEnd(10)} ${fmt(k, B[k]).padEnd(10)} ${verdict.padEnd(10)} ${goodB ? "yes" : "no"} (<= ${fmt(k, GOOD[k])})`);
  }
  const few = [A, B].some((s) => s.n < 3);
  console.log(`runs: ${a} ${A.n}, ${b} ${B.n}${few ? " (fewer than 3: treat the result as a hint, not proof)" : ""}`);
  console.log(bad ? `perf: ${bad} regression(s)` : "perf: no regressions");
  process.exit(bad ? 1 : 0);
}

function show() {
  for (const r of read()) console.log(`${r.at} ${r.label.padEnd(10)} ${r.url} ${METRICS.filter((k) => r[k] !== undefined).map((k) => `${k}=${fmt(k, r[k])}`).join(" ")}${r.note ? ` (${r.note})` : ""}`);
}

const cmd = args[0];
if (cmd === "add") add();
else if (cmd === "compare" && args[1] && args[2] && !args[1].startsWith("--")) compare(args[1], args[2]);
else if (cmd === "show") show();
else { console.error("usage: perf_log.mjs add|compare <before> <after>|show (see the header)"); process.exit(2); }
