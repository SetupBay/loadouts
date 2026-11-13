#!/usr/bin/env node
// Decide whether a change can ship as an EAS Update or needs a new store build.
// Uses the project's own expo-updates CLI (fingerprint:generate) and app config; no Expo account needed.
//
//   node ota_check.mjs config                 check app config + eas.json are set up for safe updates
//   node ota_check.mjs record  [file]         save the current native fingerprint (run when a build is cut)
//   node ota_check.mjs compare [file]         exit 0 "OTA-safe" if native fingerprint unchanged, 1 if a build is needed
//
// file defaults to .eas/build-fingerprint.json. Platforms: ios and android (AL_PLATFORMS to override).
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";

const [cmd = "", fileArg] = process.argv.slice(2);
const file = fileArg ?? ".eas/build-fingerprint.json";
const platforms = (process.env.AL_PLATFORMS ?? "ios,android").split(",").map((s) => s.trim()).filter(Boolean);
const npx = process.platform === "win32" ? "npx.cmd" : "npx";

function runJson(args) {
  const r = spawnSync(npx, ["--no-install", ...args], { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  if (r.status !== 0) {
    console.error(`failed: npx ${args.join(" ")}\n${(r.stderr || r.stdout || "").trim().slice(0, 2000)}`);
    process.exit(2);
  }
  const out = r.stdout.slice(r.stdout.indexOf("{"));
  return JSON.parse(out);
}

const keyOf = (s) => s.id ?? s.filePath ?? `${s.type}:${s.name ?? "?"}`;

function fingerprint(platform) {
  const fp = runJson(["expo-updates", "fingerprint:generate", "--platform", platform]);
  return { hash: fp.hash, sources: Object.fromEntries(fp.sources.map((s) => [keyOf(s), s.hash])) };
}

async function checkConfig() {
  const problems = [];
  const notes = [];
  const cfg = runJson(["expo", "config", "--json", "--type", "public"]);
  const rv = cfg.runtimeVersion;
  for (const p of platforms) {
    const prv = cfg[p]?.runtimeVersion ?? rv;
    if (prv === undefined) problems.push(`${p}: no runtimeVersion; set { "policy": "fingerprint" }`);
    else if (typeof prv === "object" && prv.policy !== "fingerprint") notes.push(`${p}: runtimeVersion policy "${prv.policy}" relies on people bumping versions when native code changes; "fingerprint" does it for you`);
    else if (typeof prv === "string") notes.push(`${p}: runtimeVersion "${prv}" is manual; bump it with every native change or switch to { "policy": "fingerprint" }`);
  }
  const url = cfg.updates?.url;
  if (!url || !/^https:\/\/u\.expo\.dev\/[0-9a-f-]{36}$/.test(url)) problems.push(`updates.url is ${url ? `"${url}"` : "missing"}; expected https://u.expo.dev/<projectId> (run eas update:configure once)`);
  const projectId = cfg.extra?.eas?.projectId;
  if (url && projectId && !url.endsWith(projectId)) problems.push(`updates.url does not match extra.eas.projectId (${projectId})`);
  if (cfg.updates?.enabled === false) problems.push("updates.enabled is false: builds will never download an update");

  if (!fs.existsSync("eas.json")) problems.push("no eas.json");
  else {
    // Validate and resolve "extends" with Expo's own eas.json parser (the @expo/eas-json dev dependency).
    let easJson;
    try { easJson = createRequire(path.resolve("package.json"))("@expo/eas-json"); }
    catch { problems.push("@expo/eas-json is not installed: add it as a dev dependency pinned to your eas-cli version"); }
    if (easJson) {
      const { EasJsonAccessor, EasJsonUtils } = easJson;
      const acc = EasJsonAccessor.fromProjectPath(process.cwd());
      const channels = new Map();
      try {
        for (const name of await EasJsonUtils.getBuildProfileNamesAsync(acc)) {
          const prof = await EasJsonUtils.getBuildProfileAsync(acc, platforms[0], name);
          if (prof.developmentClient) continue;
          if (!prof.channel) { problems.push(`eas.json build.${name}: no channel, so its builds cannot receive updates`); continue; }
          if (channels.has(prof.channel)) problems.push(`eas.json build.${name} and build.${channels.get(prof.channel)} share channel "${prof.channel}"`);
          channels.set(prof.channel, name);
        }
        if (!channels.has("production")) problems.push('eas.json: no build profile on channel "production"');
      } catch (e) {
        problems.push(e.message.replace(/\n/g, " "));
      }
    }
  }
  for (const n of notes) console.log(`note: ${n}`);
  for (const p of problems) console.log(`problem: ${p}`);
  if (problems.length) { console.log(`config: ${problems.length} problem(s)`); process.exit(1); }
  console.log(`config: ok (runtimeVersion ${JSON.stringify(rv)}, channels checked)`);
}

if (cmd === "config") await checkConfig();
else if (cmd === "record") {
  const data = { recordedAt: new Date().toISOString(), platforms: Object.fromEntries(platforms.map((p) => [p, fingerprint(p)])) };
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(data, null, 2)}\n`);
  for (const p of platforms) console.log(`recorded ${p}: ${data.platforms[p].hash}`);
} else if (cmd === "compare") {
  if (!fs.existsSync(file)) { console.log(`no baseline at ${file}: run "record" when you cut the build`); process.exit(2); }
  const base = JSON.parse(fs.readFileSync(file, "utf8")).platforms;
  let changed = false;
  for (const p of platforms) {
    const now = fingerprint(p);
    const was = base[p];
    if (!was) { console.log(`${p}: no baseline recorded`); changed = true; continue; }
    if (now.hash === was.hash) { console.log(`${p}: unchanged (${now.hash})`); continue; }
    changed = true;
    console.log(`${p}: native fingerprint changed ${was.hash} -> ${now.hash}`);
    const keys = new Set([...Object.keys(was.sources), ...Object.keys(now.sources)]);
    for (const k of [...keys].sort()) {
      if (!(k in was.sources)) console.log(`  added: ${k}`);
      else if (!(k in now.sources)) console.log(`  removed: ${k}`);
      else if (was.sources[k] !== now.sources[k]) console.log(`  changed: ${k}`);
    }
  }
  if (changed) { console.log("needs a new build: do not ship this as an EAS Update"); process.exit(1); }
  console.log("OTA-safe: native layer unchanged, an EAS Update can carry this change");
} else {
  console.log("usage: ota_check.mjs config | record [file] | compare [file]");
  process.exit(2);
}
