#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml==6.0.3"]
# ///
"""Check EAS Workflows that run Maestro before they burn build minutes.

  uv run workflow_check.py [project dir]

Reads .eas/workflows/*.yml, eas.json, app.json and the Maestro flows the workflows point at.
fix:  maestro job without build_id or flow_path, a flow_path that doesn't exist, an Android maestro job not on a
      linux-*-nested-virtualization worker, a build profile feeding Maestro that isn't a simulator (iOS) or APK
      (Android) build, a flow whose appId isn't the app's bundle id or package, a secret-looking literal in env
warn: retries above 2 (hides flaky flows), a fingerprint job whose environment differs from the build profile's
"""
import json
import re
import sys
from pathlib import Path

import yaml

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
out = []


def add(level, where, msg):
    out.append((level, where, msg))


def load_json(name):
    p = root / name
    return json.loads(p.read_text()) if p.exists() else {}


eas = load_json("eas.json").get("build", {})
expo = load_json("app.json").get("expo", {})
app_ids = {expo.get("ios", {}).get("bundleIdentifier"), expo.get("android", {}).get("package")} - {None}

REF = re.compile(r"needs\.(\w+)\.outputs\.build_id")
SECRETISH = re.compile(r"(PASSWORD|SECRET|TOKEN|API_KEY)", re.I)

wf_dir = root / ".eas" / "workflows"
files = sorted(list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))) if wf_dir.exists() else []
if not files:
    add("fix", ".eas/workflows", "no workflow files")
maestro_jobs = 0

for wf in files:
    rel = wf.relative_to(root).as_posix()
    doc = yaml.safe_load(wf.read_text()) or {}
    jobs = doc.get("jobs") or {}
    for name, job in jobs.items():
        job = job or {}
        for key, val in (job.get("env") or {}).items():
            if SECRETISH.search(key) and isinstance(val, str) and "${{" not in val:
                add("fix", rel, f"{name}: env {key} is a literal; use an EAS environment variable (secret visibility)")
    for name, job in jobs.items():
        job = job or {}
        if job.get("type") != "maestro":
            continue
        maestro_jobs += 1
        params = job.get("params") or {}
        where = f"{rel}: {name}"
        build_ref = str(params.get("build_id") or "")
        if not build_ref:
            add("fix", where, "maestro job has no build_id")
        if not params.get("flow_path"):
            add("fix", where, "maestro job has no flow_path")
        flow_paths = params.get("flow_path") or []
        flow_paths = [flow_paths] if isinstance(flow_paths, str) else flow_paths
        # Find the platform and profiles of the build(s) feeding this job.
        platforms, profiles = set(), set()
        for src in REF.findall(build_ref):
            sjob = jobs.get(src) or {}
            sp = sjob.get("params") or {}
            if sjob.get("type") == "repack":
                inner = REF.findall(str(sp.get("build_id", "")))
                sjob = jobs.get(inner[0]) if inner else {}
                sp = (sjob or {}).get("params") or {}
            if sp.get("platform"):
                platforms.add(sp["platform"])
            if sp.get("profile"):
                profiles.add(sp["profile"])
        if "android" in platforms and "nested-virtualization" not in str(job.get("runs_on", "")):
            add("fix", where, "Android Emulator tests need runs_on: linux-*-nested-virtualization")
        for prof in sorted(profiles):
            p = eas.get(prof)
            if p is None:
                add("fix", where, f"build profile '{prof}' is not in eas.json")
                continue
            if "ios" in platforms and not (p.get("ios") or {}).get("simulator"):
                add("fix", where, f"profile '{prof}' isn't an iOS simulator build (ios.simulator: true)")
            if "android" in platforms and (p.get("android") or {}).get("buildType") != "apk":
                add("fix", where, f"profile '{prof}' builds an AAB; the emulator needs android.buildType: apk")
        if int(params.get("retries") or 0) > 2:
            add("warn", where, f"retries: {params['retries']} hides flaky flows; fix the flow instead")
        for fp in flow_paths:
            path = (root / fp).resolve()
            if not path.exists():
                add("fix", where, f"flow_path {fp} does not exist")
                continue
            flows = [path] if path.is_file() else sorted(list(path.rglob("*.yaml")) + list(path.rglob("*.yml")))
            for flow in flows:
                head = flow.read_text().split("\n---", 1)[0]
                m = re.search(r"^appId:\s*['\"]?([\w.\-${}]+)", head, re.M)
                frel = flow.relative_to(root).as_posix()
                if not m:
                    add("fix", frel, "no appId in the flow header")
                elif app_ids and "${" not in m.group(1) and m.group(1) not in app_ids:
                    add("fix", frel, f"appId {m.group(1)} is not the app's id ({', '.join(sorted(app_ids))})")
    fp_env = next((j.get("environment", "production") for j in jobs.values() if (j or {}).get("type") == "fingerprint"), None)
    if fp_env:
        build_profiles = {((j or {}).get("params") or {}).get("profile") for j in jobs.values() if (j or {}).get("type") in ("build", "get-build")} - {None}
        for prof in sorted(build_profiles):
            env = (eas.get(prof) or {}).get("environment")
            if env and env != fp_env:
                add("warn", rel, f"fingerprint uses environment '{fp_env}' but profile '{prof}' uses '{env}'; hashes won't match")

for level, where, msg in out:
    print(f"{level:<4} {where}: {msg}")
fixes = sum(1 for o in out if o[0] == "fix")
print(f"workflows: {len(files)}; maestro jobs: {maestro_jobs}; {fixes} to fix, {len(out) - fixes} warnings")
sys.exit(1 if fixes else 0)
