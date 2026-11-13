# AGENTS.md: security baseline

These rules apply to every change in this repository, whatever the stack.

## Secrets
- Never hard-code API keys, tokens, passwords or connection strings. Read them from environment variables.
- Never put a secret in a variable the browser can see: `NEXT_PUBLIC_*`, `VITE_*`, `PUBLIC_*`, `EXPO_PUBLIC_*`,
  or anything bundled into client JavaScript. If the front end needs a third-party API, call it through a server route.
- Never log secrets, full request headers, or whole environment objects.
- Keep `.env`, `.env.local` and similar files out of git. Keep `.env.example` up to date with dummy values.
- If you find a secret committed to git, stop and tell the human. Deleting the line is not enough —
  it must be rotated with the provider.

## Auth and access
- Every route, server action and API handler that reads or changes user data checks who the user is *on the server*.
- Check authorisation on the resource, not just login: "is this user allowed to touch *this* row?"
- Admin features check an admin role stored server-side, never a flag sent by the client.
- Database access rules (Supabase RLS, Firebase Security Rules, Postgres grants) are the real boundary.
  Do not turn them off to make something work.

## Input and output
- Validate all input on the server with a schema (zod, valibot, pydantic). Client validation is for UX only.
- Use parameterised queries or the ORM. Never build SQL with string concatenation.
- Do not render user content as raw HTML (`dangerouslySetInnerHTML`, `v-html`, `set:html`, `innerHTML`)
  unless it has been sanitised.
- File uploads: check type and size server-side, store outside the web root or in object storage, never trust the filename.

## Cost and abuse
- Any endpoint that calls a paid API (LLMs, email, SMS, maps) needs auth or rate limiting, and ideally both.
- Set spending caps or budget alerts on paid providers where they exist.

## Dependencies
- Prefer well-known packages. Check that a package name is real and spelled correctly before installing it.
- Do not add a dependency for something the platform already does.

## When unsure
Ask the human, or run the `launch-check` skill and report what it finds.
