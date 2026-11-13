---
name: sqlalchemy-2-guard
description: Check Python for SQLAlchemy 1.x APIs removed in 2.0, legacy session.query code, untyped models and writes that are never committed, before saying a database change is done. Use after writing or editing SQLAlchemy models, queries or transactions, when SQLAlchemy raises ObjectNotExecutableError or ArgumentError, or when porting 1.x snippets.
---

# SQLAlchemy 2 guard

SQLAlchemy 2.0 came out in January 2023, and agents still write 1.x: `engine.execute("...")`, `select([...])`,
`row["name"]`, `session.query()`, `declarative_base()` with untyped `Column`s. The removed APIs fail at once.
`session.query()` keeps working as legacy code. The dangerous change is quiet: there is no autocommit, so a write
done inside `engine.connect()` without `commit()` is rolled back when the block ends, and no error is raised.

## 1. Confirm the version
- `uv run python -c "import sqlalchemy; print(sqlalchemy.__version__)"` should print `2.x`. If it prints `1.4`,
  ask before migrating. 1.4 with `SQLALCHEMY_WARN_20=1` is the stepping stone.

## 2. Scan
```bash
python3 .agents/skills/sqlalchemy-2-guard/scripts/sqlalchemy2_guard.py app tests
```
(Use the path the skill was installed to: `.claude/skills/...` for Claude Code, `.agents/skills/...` for the others.)

- Every `error` line is removed 1.x code or the legacy Query API. Fix it with the replacement the line gives.
  `references/migration-table.md` has before/after code.
- `connect-then-write` warnings: if the block writes, switch to `engine.begin()` or call `conn.commit()`. If it only
  reads, add `# guard: ok`. That comment silences warnings, never errors.
- `untyped-column` and `backref` warnings: convert the model to `Mapped[]` / `mapped_column` and `back_populates`.
  These conversions don't change the schema. Run `alembic check` (or compare `CREATE TABLE` output) to confirm.

## 3. Let SQLAlchemy check it
```bash
uv run pytest -q -W error::sqlalchemy.exc.SADeprecationWarning
```
- Legacy calls such as `Query.get()` warn `LegacyAPIWarning`, a subclass of `SADeprecationWarning`, so they fail here.
- Every write test should read the row back in a **new** session or connection. If it reads it back in the same
  one, an uncommitted write still looks fine.

## 4. Report
Say how many 1.x calls you replaced, which write paths you checked for commits and with which test, and that the
scanner and the tests were clean.
