# Copilot review-only instructions

Save as `.github/instructions/code-review.instructions.md`. `applyTo` limits which files the rules attach to;
`excludeAgent: "coding-agent"` keeps the file away from the Copilot coding agent so it is used for review only.

```markdown
---
applyTo: "**"
excludeAgent: "coding-agent"
---

<paste the same four sections as the shared rule list>
```
