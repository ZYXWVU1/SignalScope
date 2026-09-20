# Implementation status

## Existing functionality preserved

Next.js App Router, TypeScript, Tailwind, five navigation routes, responsive system theme,
server-only backend health request, and loading/error/empty/offline states. FastAPI retains
`/live`, `/health`, explicit CORS, SQLAlchemy/psycopg, and the original baseline migration.

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

## Features not present in this checkout

Stock search/watchlist/history/charts, news collection/filtering/deduplication, Xiaoheihe
research/collection/metrics/trends, domain data tables, collector logs and overlapping-run
protection, dashboard data API, and cron jobs. These were absent before migration and remain
future implementation work. No existing data was deleted or tables recreated.

Deploying the current code publishes the foundation shell only, not a complete data product.
