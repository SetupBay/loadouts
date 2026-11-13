#!/usr/bin/env python3
"""Find Pydantic v1 code (and FastAPI patterns built on it) in a FastAPI project on Pydantic v2.

Usage: python3 pydantic_v2_guard.py [PATH ...]        (default: the current folder)
       python3 pydantic_v2_guard.py --list            (print every rule)

A "guard: ok" comment on a line silences its warnings (never its errors).
Prints one line per finding:  path:line: level [rule] what is wrong -> what to use
Exit 0 when nothing at "error" level is found, 1 when something is, 2 on bad usage.
Standard library only. Read-only: it never edits a file and makes no network calls.
"""
import fnmatch
import os
import re
import sys

# (rule id, level, regex, message, file patterns). Patterns run against each line with comments removed.
RULES = [
    ('pydantic-v1-import', 'error', '\\bfrom\\s+pydantic\\.v1\\b|\\bimport\\s+pydantic\\.v1\\b|pydantic\\.v1\\.',
     'pydantic.v1 models are refused by FastAPI (PydanticV1NotSupportedError) -> plain pydantic v2 models', []),
    ('basesettings-import', 'error', 'from\\s+pydantic\\s+import\\s+[^#]*\\bBaseSettings\\b',
     'BaseSettings moved to pydantic-settings -> from pydantic_settings import BaseSettings, SettingsConfigDict', []),
    ('class-config', 'error', '^\\s+class\\s+Config\\s*(\\(|:)',
     'inner class Config -> model_config = ConfigDict(...) (settings: SettingsConfigDict)', []),
    ('orm-mode', 'error', '\\borm_mode\\b',
     'orm_mode -> from_attributes=True in ConfigDict', []),
    ('allow-population', 'error', '\\ballow_population_by_field_name\\b',
     'allow_population_by_field_name -> populate_by_name=True (or validate_by_name)', []),
    ('schema-extra', 'error', '\\bschema_extra\\b',
     'schema_extra -> json_schema_extra', []),
    ('anystr-config', 'error', '\\b(anystr_strip_whitespace|anystr_lower|max_anystr_length|min_anystr_length)\\b',
     'anystr_* config -> str_strip_whitespace, str_to_lower, str_max_length, str_min_length', []),
    ('validator', 'error', '@validator\\(|\\bimport\\s+[^#]*\\bvalidator\\b',
     "@validator -> @field_validator('x') with @classmethod (mode='before' for pre=True)", []),
    ('root-validator', 'error', '@root_validator\\b|\\broot_validator\\b',
     "@root_validator -> @model_validator(mode='before' | 'after')", []),
    ('each-item', 'error', '\\beach_item\\s*=',
     'validator(each_item=True) -> annotate the item type: list[Annotated[int, AfterValidator(f)]]', []),
    ('dict-method', 'error', '\\.dict\\(\\s*(\\)|[a-z_]+\\s*=)',
     '.dict() -> .model_dump() (exclude_unset=, by_alias= still work)', []),
    ('json-method', 'error', '\\.json\\(\\s*(exclude|include|by_alias|indent|models_as_dict)\\w*\\s*=',
     'model.json(...) -> .model_dump_json(...) (a bare .json() is left alone: HTTP responses have one too)', []),
    ('parse-obj', 'error', '\\.(parse_obj|parse_raw|parse_file)\\(',
     'parse_obj/parse_raw -> model_validate() / model_validate_json()', []),
    ('from-orm', 'error', '\\.from_orm\\(',
     'from_orm() -> model_validate(obj) with from_attributes=True', []),
    ('copy-update', 'error', '\\.copy\\(\\s*update\\s*=',
     '.copy(update=...) -> .model_copy(update=...)', []),
    ('schema-method', 'error', '\\.(schema|schema_json)\\(\\s*\\)',
     '.schema() -> .model_json_schema()', []),
    ('fields-attr', 'error', '\\.__fields__\\b|\\.__fields_set__\\b',
     '__fields__ -> model_fields (on the class); __fields_set__ -> model_fields_set', []),
    ('forward-refs', 'error', '\\.update_forward_refs\\(',
     'update_forward_refs() -> model_rebuild()', []),
    ('construct', 'error', '\\.construct\\(',
     '.construct() -> .model_construct()', []),
    ('field-regex', 'error', '\\bField\\([^)]*\\bregex\\s*=',
     'Field(regex=...) is removed -> Field(pattern=...)', []),
    ('field-const', 'error', '\\bField\\([^)]*\\bconst\\s*=',
     'Field(const=...) is removed -> Literal[...]', []),
    ('field-items', 'error', '\\b(min_items|max_items|unique_items)\\s*=',
     'min_items/max_items -> min_length/max_length (unique_items -> a set type)', []),
    ('allow-mutation', 'error', '\\ballow_mutation\\b',
     'allow_mutation -> frozen=True (field or model)', []),
    ('constr-regex', 'error', '\\bconstr\\([^)]*\\bregex\\s*=',
     'constr(regex=...) -> Annotated[str, StringConstraints(pattern=...)]', []),
    ('parse-obj-as', 'error', '\\bparse_obj_as\\(',
     'parse_obj_as(T, data) -> TypeAdapter(T).validate_python(data)', []),
    ('on-event', 'error', '\\.on_event\\(\\s*[\\"\'](startup|shutdown)[\\"\']',
     '@app.on_event is deprecated -> lifespan=asynccontextmanager function', []),
    ('optional-no-default', 'warn', '^\\s+\\w+\\s*:\\s*(Optional\\[[^\\]]+\\]|[\\w\\[\\], .]+\\|\\s*None)\\s*$',
     'Optional[X] with no default is REQUIRED in v2 (it only allows None) -> add = None if it may be left out', []),
    ('orm-response-dict', 'warn', 'response_model\\s*=\\s*dict\\b',
     'response_model=dict skips output filtering -> a response model', []),
]
FILES = ['*.py']
COMMENT = '#'
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".agents", ".claude", ".cursor", "dist", "build", "target", ".godot"}
COMPILED = [(rid, lvl, re.compile(rx), msg, globs) for rid, lvl, rx, msg, globs in RULES]


def strip_comment(line):
    """Drop a trailing comment, leaving string literals alone."""
    q = None
    i = 0
    while i < len(line):
        c = line[i]
        if q:
            if c == "\\":
                i += 2
                continue
            if c == q:
                q = None
        elif c in "\"'`":
            q = c
        elif line.startswith(COMMENT, i):
            return line[:i]
        i += 1
    return line


def wanted(name):
    return any(fnmatch.fnmatch(name, g) for g in FILES)


def walk(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for f in sorted(files):
                if wanted(f):
                    yield os.path.join(root, f)


def scan(path):
    out = []
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError as e:
        return [(path, 0, "error", "unreadable", str(e))]
    for n, raw in enumerate(lines, 1):
        code = strip_comment(raw)
        if not code.strip():
            continue
        accepted = "guard: ok" in raw  # a person accepted the warnings on this line
        for rid, lvl, rx, msg, globs in COMPILED:
            if accepted and lvl == "warn":
                continue
            if globs and not any(fnmatch.fnmatch(name, g) for g in globs):
                continue
            if rx.search(code):
                out.append((path, n, lvl, rid, msg))
    return out


def main(argv):
    if "--list" in argv:
        for rid, lvl, _, msg, globs in RULES:
            print(f"{lvl:5} [{rid}] {msg}" + (f"  (only {', '.join(globs)})" if globs else ""))
        return 0
    if any(a.startswith("-") for a in argv):
        print(__doc__)
        return 2
    paths = argv or ["."]
    for p in paths:
        if not os.path.exists(p):
            print(f"no such path: {p}", file=sys.stderr)
            return 2
    files = list(walk(paths))
    findings = []
    for f in files:
        findings.extend(scan(f))
    for path, n, lvl, rid, msg in findings:
        print(f"{os.path.relpath(path)}:{n}: {lvl} [{rid}] {msg}")
    errors = sum(1 for x in findings if x[2] == "error")
    warns = sum(1 for x in findings if x[2] == "warn")
    print(f"pydantic_v2_guard: {len(files)} file(s), {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
