# No-Docker migration audit

Audit completed before changing application logic on 2026-09-20, against commit `ca197d1`.
Scope: the existing `SignalScope` repository only. Git history remains intact.

## Actual current architecture

All tracked application, test, configuration, migration, and documentation files were
inspected; the dependency lockfile inventory was checked separately. Generated dependencies,
tool caches, and build output are not application source.

- `frontend/`: Next.js 16 App Router, React 19, TypeScript, Tailwind. Five routes:
  Overview, Stocks, Tech News, Gaming, Settings. Only Overview calls the backend,
  through the server-only `lib/api.ts` helper. Other domain pages are explicit placeholders.
- `backend/`: FastAPI `/live` and `/health`; SQLAlchemy/psycopg engine; Pydantic settings.
  `/health` checks PostgreSQL and baseline Alembic revision `0001_foundation`.
- `backend/alembic/`: one empty baseline migration establishing revision tracking.
  **No domain models or application data tables exist.**
- `backend/tests/`: three unit tests and one opt-in PostgreSQL integration test.
- No collector scripts, parsers, external provider adapters, collector run logs, locks,
  scheduler loops, APScheduler, or GitHub collection schedules exist.
- No Git remote, deployment configuration for cloud providers, or local database credentials
  are configured. No cloud deployment can be identified from this repository.

The new brief describes a potentially complete product. This checkout is still a foundation.
Migration must preserve that actual functionality without claiming missing features work.

## Baseline verification

Before changes: backend tests 3 passed / 1 real-database test skipped; Ruff and mypy passed;
frontend lint and production build passed. Prior native startup and browser checks are recorded
in `VERIFICATION.md`. A real database connection has never been verified in this checkout.

## Existing Docker dependencies

- Root `docker-compose.yml`: local database, migration job, API, and frontend; service-hostname URLs.
- Two Dockerfiles and two `.dockerignore` files.
- CI PostgreSQL service container and local database credentials.
- Root environment example includes container database defaults and `POSTGRES_*` variables.
- README and status documents describe Compose as the acceptance path.
- Frontend uses standalone build packaging and a custom static-copy startup script.

## Files to modify

| Files | Migration |
| --- | --- |
| `backend/app/config.py`, `database/session.py` | Required cloud URL, psycopg normalization, TLS, bounded pool, explicit CORS |
| Root `.env.example` | Hosted database configuration; remove local database credentials |
| `frontend/lib/api.ts`, `.env.example` | Central `NEXT_PUBLIC_API_URL`; remove localhost fallback |
| `frontend/next.config.ts`, `package.json` | Standard Next.js build/start for Vercel and local Node |
| `.github/workflows/ci.yml` | Unit checks without a database service; explicitly gated cloud integration |
| `backend/railway.json`, `.python-version` (new) | Railpack build, migration pre-deploy, `$PORT`, health check |
| `frontend/vercel.json` (new) | Next.js project defaults; root directory is configured in Vercel |
| Tests and documentation | Configuration/CORS regressions and accurate cloud setup/status |

## Files that remain unchanged

Keep the UI, routes, components, styling, dependency strategy, SQLAlchemy Base, existing
Alembic revision and migration template, health response contract, and existing Git history.
Do not add the Supabase JS SDK or rebuild the app. No existing stock/news/gaming logic exists
to rewrite or remove. No production cron jobs should be enabled until real collectors exist.

## Database and deployment changes

Use a Supabase development database for local Python, and a separate production database for
Railway. `DATABASE_URL` remains backend-only. Use the session pooler or direct connection;
do not use transaction pooling for migrations or future session advisory locks. Preserve
the supplied hostname, user, database, and encoded password; use psycopg and TLS.

Railway's API service will run `alembic upgrade head` before Uvicorn. Vercel builds `frontend/`.
Both link to the existing GitHub repository and its selected production branch. The browser
continues accessing Next.js; Next.js checks FastAPI, which accesses PostgreSQL.

## Risks and blocked steps

- No Supabase URL or cloud account/project selection is available. Live connection, migrations,
  remote deployment, and end-to-end cloud checks must remain explicitly pending.
- Preparing configuration can proceed locally; it is not proof of cloud migration success.
- Container files can be retired after baseline inspection and native startup checks because
  no existing container deployment or data volume has been identified. Git retains the originals.
- Do not run migration downgrade tests against a shared development or production database.
- Keep CI cloud credentials out of pull-request jobs; use a dedicated test database and manual job.
- Allow only explicit frontend origins. Vercel preview domains require deliberate configuration.
- Public deployment will expose a foundation shell, not stock/news/gaming functionality.
- Future Railway cron services must not inherit the API start command or its migration hook.
  Use one scheduler per collector; add database run locking with the actual collectors.

## Local migration outcome

The native API and standard Next.js production server were verified before retiring the
container files. Tests cover database URL validation/TLS, allowed and denied origins,
frontend cloud-origin selection, offline handling, and Vercel configuration guards.
No UI component or Alembic revision was replaced. Docker files, CI's database service,
and standalone-copy startup script are removed. No replacement container configuration exists.

At the user's request, new cloud projects will be created/configured by following
`CLOUD_SETUP.md`; passwords and connection strings stay outside chat. The local checkout
still lacks a GitHub remote URL. Supabase migration and hosting verification remain pending,
so this is a prepared source migration, not a completed public deployment.

## References checked

- [Supabase connection modes](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Supabase SQLAlchemy guidance](https://supabase.com/docs/guides/troubleshooting/using-sqlalchemy-with-supabase-FUqebT)
- [Railway configuration reference](https://docs.railway.com/config-as-code/reference)
- [Railway monorepo configuration](https://docs.railway.com/builds/build-configuration)
- [Railpack Python](https://railpack.com/languages/python)
- [Vercel monorepos](https://vercel.com/docs/monorepos)
