# Review prompt template

Save as review-prompt.txt, fill the angle brackets, keep it under 40 lines.

```
You are reviewing a diff you did not write. You cannot edit files. The diff is on stdin.

Goal of the change: <one or two sentences>.
How it is tested: <command>, which <passes / was not run because …>.
Focus on: <for example: error handling in the API client, the migration's down step, race conditions in the cache>.

Report only problems that would cause wrong behaviour, security issues, data loss, broken callers or missing tests
for changed behaviour. Ignore style and naming unless they hide a bug.

Format, most severe first, at most 10 items:
<blocking|should-fix|nit> — <path>:<line> — <problem> — <suggested fix>

If you find nothing blocking, say "No blocking issues" and stop.
```
