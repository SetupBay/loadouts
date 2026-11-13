# Review instructions

## What blocking means here
Blocking: incorrect logic, unscoped database queries, secrets or personal data in code, logs or errors, migrations that are not
backward compatible, removed authorisation checks. Style, naming and refactoring suggestions are nits at most.

## Cap the nits
Report at most five nits per review.

## Do not report
- Anything CI already enforces: lint, formatting, type errors, spelling
- Generated files under `<generated paths>` and lockfiles
- Test code that deliberately breaks production rules

## Always check
- <New API routes have an integration test>
- <Log lines do not include email addresses, user IDs or request bodies>
- <Database queries are scoped to the caller's tenant>

## Evidence
Behaviour claims need a path:line citation from the source, not an inference from a name.
