---
name: plan-then-build
description: Write a short implementation plan and get approval before building. Use for new features, refactors, multi-file changes, dependency changes, or whenever the request is big or vague.
---

# Plan, then build

## 1. Look before planning (keep it quick)
Read the files you expect to change and their neighbours. Find the existing pattern for this kind of change
(how other routes, components or commands are structured). Check installed versions of anything you will rely on.

## 2. Write the plan
Keep it under ~20 lines. Use this shape:

```
Goal: <one sentence, in the human's terms>
Approach: <two or three sentences>
Changes:
  1. <file> — <what and why>
  2. <file> — <what and why>
New dependencies: none | <name> (<why>)
Out of scope: <things you will deliberately not do>
Risks / questions: <anything you are unsure of; at most three>
How I'll verify: <commands or manual checks>
```

If there is a real choice to make (two reasonable approaches), give both in one line each with your recommendation.

## 3. Stop and wait
Ask: "Shall I go ahead?" Do not start editing until the human agrees or adjusts the plan.
If they say "just do it" for this kind of task in future, you may skip waiting for similar small tasks in the same session.

## 4. Build in the order of the plan
- Do the steps in order, verifying as you go.
- If you discover the plan is wrong (a hidden dependency, a bigger change than expected), stop, explain, and re-plan.
  Do not quietly expand the scope.

## 5. Close out
Report against the plan: each step done or not, how it was verified, and anything that changed from the plan.
