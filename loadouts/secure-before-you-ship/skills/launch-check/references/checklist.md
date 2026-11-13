# Launch checklist

Severity in brackets is the default; raise it if the data is sensitive.

## Secrets
- [Critical] No live secret keys in source code or config files.
- [Critical] No secrets in client-exposed env vars or the built front-end bundle.
- [Critical] No `.env` files tracked by git. If one ever was, the keys in it need rotating.
- [High] Secrets in git history have been rotated (removing the commit is not enough).
- [Medium] `.env.example` exists and lists every variable with a dummy value.

## Authentication
- [Critical] Every API route / server action that touches user data checks the session on the server.
- [Critical] Admin pages and endpoints check a server-side role, not a client flag or a hidden URL.
- [High] Password reset and magic-link flows expire and are single use (default on most providers — confirm it is not disabled).
- [Medium] Email confirmation is required before an account can do anything costly.

## Data access
- [Critical] Database rules are on: Supabase RLS on every public table, Firebase rules not open, no public buckets with private files.
- [Critical] Users cannot read or change another user's rows by changing an ID in the request (test one by hand).
- [High] Update endpoints cannot change ownership or role fields.
- [High] Queries are parameterised; no string-built SQL.

## Abuse and cost
- [Critical] Endpoints that call paid APIs (LLM, email, SMS) need auth.
- [High] Those endpoints are rate limited per user or IP.
- [High] Provider spending limits or budget alerts are set.
- [Medium] Sign-up has some bot friction (captcha, email confirmation or invite).

## Input and output
- [High] Server-side validation on every input.
- [High] No unsanitised user HTML rendered.
- [Medium] Uploads checked for type and size server-side.
- [Medium] Error responses do not leak stack traces or SQL.

## Platform
- [High] HTTPS only. Cookies are `Secure`, `HttpOnly` and `SameSite=Lax` or stricter.
- [Medium] Security headers set: `Content-Security-Policy` (even a basic one), `X-Content-Type-Options: nosniff`,
  `Referrer-Policy`, `frame-ancestors` / `X-Frame-Options`.
- [Medium] CORS is not `*` on endpoints that use cookies.
- [Medium] Debug mode, test routes and seed endpoints are off in production.

## Dependencies
- [High] `npm audit --omit=dev` / `pip-audit` shows no critical issues in runtime dependencies.
- [Medium] Lockfile committed.
- [Medium] No unfamiliar or misspelt packages (check anything you do not recognise on the registry).

## Readiness (not security, but people notice)
- [Medium] Privacy policy and terms exist if you collect personal data (UK GDPR applies to UK users).
- [Medium] Error tracking or at least server logs are on.
- [Medium] Database backups are on and you know how to restore one.
