# Example rules

Auto-attached, scoped to React components:

```markdown
---
description: React component conventions.
globs: src/components/**/*.tsx
alwaysApply: false
---

- Function components only; props typed with an exported `type <Name>Props`.
- Data fetching lives in hooks under `src/hooks/`, never inside components.
- Every new component gets a story in the same folder: `<Name>.stories.tsx`.
```

Agent-requested, no globs:

```markdown
---
description: Use when writing or changing a database migration.
alwaysApply: false
---

- Create migrations with `npm run db:new -- <name>`; never edit an applied migration.
- Every migration is reversible: write the down step and run `npm run db:rollback` locally before committing.
```

Always on (keep these rare and short):

```markdown
---
alwaysApply: true
---

- Package manager is pnpm. Never run npm or yarn install.
```

Copilot equivalent of the first example, at `.github/instructions/components.instructions.md`:

```markdown
---
applyTo: "src/components/**/*.tsx"
---

- Function components only; props typed with an exported `type <Name>Props`.
```
