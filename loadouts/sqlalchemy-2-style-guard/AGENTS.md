# AGENTS.md: SQLAlchemy 2 project (1.x and legacy Query guard)

This project uses **SQLAlchemy 2.x** (`sqlalchemy>=2.1,<3`) in **2.0 style**: typed `Mapped[]` models,
`select()` statements and explicit transactions. Most SQLAlchemy code you have seen is 1.x. Some of it was removed,
some still runs as the "legacy" Query API, and one change loses writes without an error.

## Version facts
- Check the pin first: `uv pip show sqlalchemy`.
- Removed in 2.0: `engine.execute()`, plain SQL strings in `execute()` (use `text()`), `select([...])`,
  `MetaData(bind=)`, `autocommit=True`, and string keys on rows (`row["name"]`).
- No autocommit: `with engine.connect() as conn:` rolls back anything you didn't `conn.commit()`. Use
  `with engine.begin() as conn:` for writes. Sessions work the same way: `with Session(engine) as s, s.begin():`.
- `session.query(...)` still runs but is legacy. New code uses `session.scalars(select(...))` / `session.execute(...)`.
- If you're not sure of an API, check the 2.0 migration guide (https://docs.sqlalchemy.org/en/21/changelog/migration_20.html)
  instead of copying 1.x answers.

## Rules
- Models: `class Base(DeclarativeBase): pass`, then `name: Mapped[str] = mapped_column(String(80))`.
  `Mapped[str | None]` for nullable columns.
- Relationships: `relationship(back_populates=...)` on both sides. Use `lazy="raise"` or `selectinload` when N+1
  queries matter. Use `WriteOnlyMapped` for big collections, not `lazy="dynamic"`.
- Queries: `select(User).where(User.name == name)`, then `session.scalars(stmt).all()` or `.one_or_none()`.
  Use `session.get(User, pk)` for primary keys.
- Raw SQL only through `text("... :name")` with bound parameters. Never use f-strings.
- Writes happen inside `engine.begin()` or `session.begin()`, or are followed by an explicit commit.
- Don't upgrade or downgrade SQLAlchemy without asking the human.

## Before you say "done"
1. Run the `sqlalchemy-2-guard` scanner on the files you touched. It must report `0 error(s)`. Read every `warn`.
2. Run the tests with SQLAlchemy's own warnings as errors:
   `uv run pytest -q -W error::sqlalchemy.exc.SADeprecationWarning`.
3. For every write path you touched, say which test shows the row is really there afterwards.
