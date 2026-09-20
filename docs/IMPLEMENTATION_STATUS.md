# Implementation status

## Existing functionality preserved and restored

Next.js App Router, TypeScript, Tailwind, five navigation routes, responsive system theme,
server-only backend health request, and loading/error/empty/offline states. FastAPI retains
`/live`, `/health`, explicit CORS, SQLAlchemy/psycopg, and the original migration chain. Domain
tables, API routes, provider abstractions, parser tests, and three finite collector entry points
now exist.

## No-Docker migration

- Required hosted `DATABASE_URL`, TLS, bounded SQLAlchemy connection pool.
- Environment-driven frontend API origin using `NEXT_PUBLIC_API_URL`.
- Standard Python and Node startup, no container startup script.
- Railway Railpack configuration, migration pre-deploy, readiness check, dynamic port.
- Vercel Next.js configuration and cloud setup guide.
- No local PostgreSQL or container configuration; CI unit checks require neither.
- Existing Git repository and commit history retained.

## Acceptance still pending

A Supabase project and its private connection configuration are needed before real database
checks and `alembic upgrade head` can be verified. Railway and Vercel must be linked to the
existing GitHub repository, configured, deployed, and tested with their public URLs.

The user's migration request replaces the original Docker acceptance path. Native startup
has been checked, but the foundation still needs a real migrated cloud database.

## Remaining product work

Frontend data cards, charts, richer filters, provider credentials, live Supabase verification,
and Railway/Vercel deployment remain. The Xiaoheihe feed is intentionally conservative and
requires a configured public URL; it does not bypass access controls. No existing data was
deleted or tables manually recreated.

Deploying the current code publishes the foundation plus backend collection APIs. It is not
yet the complete dashboard product until live data is verified through the UI.
