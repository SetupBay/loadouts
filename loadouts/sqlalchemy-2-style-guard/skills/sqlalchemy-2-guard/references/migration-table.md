# SQLAlchemy 1.x → 2.0 style table

From the SQLAlchemy 2.0 migration guide (https://docs.sqlalchemy.org/en/21/changelog/migration_20.html) and the
ORM querying guide. Checked against SQLAlchemy 2.1.6.

## Removed in 2.0 (raises)

| 1.x | 2.x | Error on 2.1.6 |
|---|---|---|
| `engine.execute("select 1")` | `with engine.connect() as c: c.execute(text("select 1"))` | `AttributeError` |
| `conn.execute("select 1")` | `conn.execute(text("select 1"))` | `ObjectNotExecutableError` |
| `select([User.id, User.name])` | `select(User.id, User.name)` | `ArgumentError` |
| `MetaData(bind=engine)` | `MetaData()`; pass the engine to `create_all(engine)` | `TypeError` |
| `Session(engine, autocommit=True)` | `with Session(engine) as s, s.begin(): ...` | `ArgumentError` |
| `row["name"]` | `row.name`, `row._mapping["name"]` | `TypeError` |

## Legacy (still runs, warns or is discouraged)

| 1.x | 2.0 style |
|---|---|
| `session.query(User).all()` | `session.scalars(select(User)).all()` |
| `session.query(User).filter_by(name=n).first()` | `session.scalars(select(User).filter_by(name=n)).first()` |
| `session.query(User).get(1)` (`LegacyAPIWarning`) | `session.get(User, 1)` |
| `session.query(func.count(User.id)).scalar()` | `session.scalar(select(func.count(User.id)))` |
| `from sqlalchemy.ext.declarative import declarative_base` (`MovedIn20Warning`) | `class Base(DeclarativeBase): pass` |
| `id = Column(Integer, primary_key=True)` | `id: Mapped[int] = mapped_column(primary_key=True)` |
| `name = Column(String, nullable=True)` | `name: Mapped[str \| None] = mapped_column(String(80))` |
| `relationship("Post", backref="author")` | `posts: Mapped[list["Post"]] = relationship(back_populates="author")` on both sides |
| `lazy="dynamic"` | `posts: WriteOnlyMapped["Post"] = relationship()` |
| `create_engine(url, future=True)` | `create_engine(url)` |

## Transactions: writes that vanish

| Code | What happens on 2.x | Fix |
|---|---|---|
| `with engine.connect() as c: c.execute(insert_stmt)` | rolled back at the end of the block | `with engine.begin() as c:` or `c.commit()` |
| `s = Session(engine); s.add(u)` and no commit | discarded when the session closes | `with Session(engine) as s, s.begin(): s.add(u)` |
