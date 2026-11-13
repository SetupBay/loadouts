---
name: launch-check
description: Pre-launch security and readiness audit for web apps. Use when the user says they are about to launch, deploy, go live, share the link, or asks "is my app safe?".
---

# Launch check

Produce a plain-English, severity-ranked fix list that a non-expert can act on.
**Report first. Do not change code until the human picks which fixes to apply.**

## Steps

1. **Map the app (2 minutes, no more).** Identify the framework, where server code runs, the database and
   auth provider, the hosting platform, and every third-party API it calls. Read `package.json` /
   `requirements.txt` / `pyproject.toml`, the env example file, and the routes or API folder.

2. **Work through `references/checklist.md`.** For each item decide: pass, fail, or can't tell.
   Prefer evidence from the code. Useful searches:
   - Secrets in code: `git grep -nE "(sk_live|sk_test|sb_secret_|service_role|AKIA[0-9A-Z]{16}|ghp_|xox[bp]-|-----BEGIN)"`
   - Secrets in history: `git log -p --all -S "sk_live" | head` (repeat for other patterns that hit)
   - Client-exposed env: `git grep -nE "(NEXT_PUBLIC_|VITE_|PUBLIC_|EXPO_PUBLIC_)[A-Z_]*(SECRET|PRIVATE|SERVICE|TOKEN)"`
   - Committed env files: `git ls-files | grep -E "(^|/)\.env"`
   - Raw HTML: `git grep -nE "dangerouslySetInnerHTML|v-html|set:html|innerHTML\s*="`
   - String-built SQL: `git grep -nE "(query|execute|raw)\(.*(\+|\$\{|f\")"`
   - Server routes without an auth check: list every API route and note which ones read the user.

3. **Check the database rules** if there is one. Supabase: every public table has RLS enabled with real
   policies. Firebase: rules are not `allow read, write: if true`. Plain Postgres/MySQL: the app user is not a superuser.

4. **Check abuse and cost.** List every endpoint that triggers a paid API. Note whether it requires auth and is rate limited.

5. **Write the report** in this format:

```
Launch check — <app name> — <date>
Verdict: Not ready / Ready with fixes / Ready

CRITICAL (fix before anyone else sees the link)
1. <what is wrong, in one sentence> — <file:line>
   Why it matters: <the realistic bad outcome>
   Fix: <the concrete change>

HIGH (fix before launch day)
...
MEDIUM (fix in the first week)
...
Couldn't check: <items needing dashboard access, with how the human can check them>
```

Keep each finding to three or four lines. Do not pad the report with passes; list passes as a single line count.

6. **Offer the fixes.** Ask which to apply. Rotated keys, dashboard settings and DNS changes are jobs for the
   human — explain exactly where to click, but do not pretend you did them.
