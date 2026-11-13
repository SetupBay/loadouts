---
name: web-perf-loop
description: Measure page speed with Chrome DevTools MCP traces under mobile throttling, fix the slowest part, and prove the change with before/after medians. Use when a page feels slow, LCP, CLS or INP is poor, or the user mentions Core Web Vitals, PageSpeed or Lighthouse scores.
---

# Web performance loop with Chrome DevTools MCP

The `chrome-devtools` MCP server gives you a real Chrome: traces, network, console and Lighthouse. Use it to measure
before you change anything, change one thing, and measure again. "It should be faster now" is not a result.

Two facts that trip agents up:
- **`lighthouse_audit` excludes performance.** It scores accessibility, SEO, best practices and agentic browsing.
  For speed, record a trace with `performance_start_trace`.
- **One trace is noise.** Take three per state and compare medians.

## 1. Set up the measurement
1. Start the site the way users get it: a production build (`npm run build && npm run start`, or the preview
   command), not the dev server. Dev servers are slower and change between runs.
2. `new_page` or `navigate_page` to the URL.
3. `emulate` a mid-range phone, in one call (each call replaces the last): `cpuThrottlingRate: 4`,
   `networkConditions: "Slow 4G"`. Keep these settings for every run in the comparison.

## 2. Record the baseline (three times)
1. `performance_start_trace` with `reload: true`, `autoStop: true`, and `ignoreCache: true` for a cold load.
2. Read the result: LCP, CLS, TTFB and the insight sets. For the biggest problem, call
   `performance_analyze_insight` with its insight set id and name, such as `LCPBreakdown`, `DocumentLatency` or
   `RenderBlocking`, to see what to fix (late-discovered LCP image, render-blocking CSS or fonts, slow server, layout
   shifts from images without sizes).
3. Log each run: `node .agents/skills/web-perf-loop/scripts/perf_log.mjs add --label before --url <url> --lcp <ms> --cls <value> --ttfb <ms>`
   (Claude Code installs the skill under `.claude/skills/`). For INP, interact (`click`, `type_text`) during a trace
   started without `reload`, then log `--inp`.

## 3. Change one thing
Fix the largest insight only: preload or `fetchpriority="high"` on the LCP image, width and height on images,
`font-display: swap` or a preloaded font, deferred non-critical scripts, a cached server response. Check
`list_network_requests` and `list_console_messages` for errors the change caused.

## 4. Measure again and compare
Rebuild, then repeat step 2 three times with `--label after`, and run:
```bash
node .agents/skills/web-perf-loop/scripts/perf_log.mjs compare before after
```
It prints the medians, the change per metric with a noise margin, and whether each meets Google's "good"
thresholds (LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1). It exits 1 on any regression. If nothing improved, revert the
change and say so; do not stack another guess on top.

## 5. Quality checks and report
- Run `lighthouse_audit` (`mode: "navigation"`, `device: "mobile"`) for accessibility, SEO and best practices, and
  fix what your change broke.
- Report the before/after table from `compare`, the throttling used, what you changed and why (the insight), and the
  run counts. Lab numbers are not field data; say so.
