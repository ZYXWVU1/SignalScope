# SignalScope

Market, technology news, and gaming intelligence, built on Next.js and FastAPI.

**Current implementation: foundation plus standalone collectors.** This checkout has five
dashboard routes, FastAPI APIs, SQLAlchemy/Alembic domain tables, provider-backed stock/news
collectors, and a conservative public-HTML Xiaoheihe collector. Cloud deployment and a live
Supabase connection are still pending.

No Docker or local PostgreSQL installation is required. Use Python 3.12, Node.js 22, and
hosted Supabase PostgreSQL.

## Architecture

```mermaid
flowchart TD
  GitHub[Existing GitHub repository] --> Vercel[Vercel · Next.js]
  GitHub --> Railway[Railway · FastAPI]
  Browser[User browser] --> Vercel
  Vercel --> Railway
  Railway --> Supabase[(Supabase PostgreSQL)]
  GitHub -. future .-> Cron[Railway cron collectors]
  Cron -. future .-> Supabase
```

The frontend still checks FastAPI from its server. Only the public API origin is exposed
through `NEXT_PUBLIC_API_URL`; database credentials and provider keys stay backend-side.
No provider calls or scraping happen on page load.

## Start here

Follow [the step-by-step cloud setup guide](docs/CLOUD_SETUP.md) to create your Supabase,
Railway, and Vercel projects using your existing GitHub repository.

The existing remote is `https://github.com/ZYXWVU1/SignalScope.git`, on branch `main`.
Reuse that repository; do not create a replacement or force-push over existing history.

## Local backend

Create a Supabase development project and copy its **Connect → Session pooler** URI.
From the `SignalScope` root, copy the example only if you do not already have `.env`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` privately. Set `DATABASE_URL` to your Supabase PostgreSQL URI, with the
`postgresql+psycopg://` scheme and `?sslmode=require`. Do not post it in chat or commit it.
The backend also accepts standard `postgresql://` and normalizes the driver.
TLS is required; stronger `verify-full` settings are preserved.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

On macOS/Linux, activate with `source .venv/bin/activate`.
Open [API docs](http://localhost:8000/docs).
[Readiness](http://localhost:8000/health) must return HTTP 200 and `{"status":"ok"}`
after the database is reachable and migrated. `/live` is process liveness only.

Settings read the root `.env` regardless of the backend working directory.
Missing or invalid `DATABASE_URL` fails configuration validation without printing its value.

## Local frontend

In another terminal, from `SignalScope`:

```powershell
cd frontend
Copy-Item .env.example .env.local
npm ci
npm run dev
```

The example sets `NEXT_PUBLIC_API_URL=http://localhost:8000`.
Open [the dashboard](http://localhost:3000).
For a local production build, run `npm run build` followed by `npm start`.
The frontend has no implicit localhost API fallback.

## Environment variables

| Location                        | Variable                                                | Purpose                                                  |
| ------------------------------- | ------------------------------------------------------- | -------------------------------------------------------- |
| Root `.env` / Railway           | `DATABASE_URL`                                          | Private Supabase session-pooler or direct PostgreSQL URI |
| Root `.env` / Railway           | `CORS_ORIGINS`                                          | JSON array of exact frontend origins; defaults to none   |
| Root `.env` / Railway           | `FRONTEND_URL`                                          | One additional exact frontend origin                     |
| Frontend `.env.local` / Vercel  | `NEXT_PUBLIC_API_URL`                                   | Public FastAPI origin; HTTPS Railway origin on Vercel    |
| Railway                         | `PORT`                                                  | Supplied by Railway; used by Uvicorn                     |
| Root `.env` / Railway           | `ALPHA_VANTAGE_API_KEY`, `NEWS_API_KEY`                 | Provider credentials                                     |
| Root `.env` / Railway           | `XHH_REQUEST_DELAY_SECONDS`, `XHH_PUBLIC_FEED_URL`, `XHH_PUBLIC_POST_URLS` | Public collection settings |
| Root `.env` / Railway cron      | `NEWS_COLLECTION_INTERVAL`, `STOCK_COLLECTION_INTERVAL` | Deployment cadence documentation                         |

Frontend variables never contain database URLs, passwords, or provider keys.
Changing a public Next.js variable on Vercel requires a new build/deployment.
Vercel builds reject a missing, non-HTTPS, or loopback API origin.

## Production configuration

| Service         | Repository root directory | Configuration                                                 |
| --------------- | ------------------------- | ------------------------------------------------------------- |
| Railway API     | `/backend`                | Config file path `/backend/railway.json`; Railpack            |
| Vercel frontend | `frontend`                | `frontend/vercel.json`; Next.js preset                        |
| Supabase        | Hosted project            | Existing Alembic migration applied through Railway pre-deploy |

Railway installs `requirements.txt`, runs `alembic upgrade head` before deployment,
and starts `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
It checks `/health` before making a deployment ready. No tables are manually recreated.
The existing baseline migration remains unchanged.

Connect both hosting projects to the same existing GitHub repository and production branch.
This checkout's branch is `main`; use that branch for production deployments.
No remote resources, provider credentials, or cloud schedules have been created by this migration.

## Checks

From `backend`, with its virtual environment active:

```powershell
ruff check .
ruff format --check .
mypy app
pytest
```

Unit tests isolate configuration and mock database checks. They do not contact Supabase.
To test a real migrated development/test database:

```powershell
alembic upgrade head
$env:RUN_DATABASE_TESTS = '1'
pytest tests/test_database_integration.py
Remove-Item Env:RUN_DATABASE_TESTS
```

From `frontend`:

```powershell
npm run lint
npm run typecheck
npm test
npm run build
```

GitHub Actions runs these checks without a database service. An optional manually dispatched
Supabase integration job uses a dedicated `SUPABASE_TEST_DATABASE_URL` secret in the
`supabase-test` GitHub environment, on the default branch only. It applies migrations forward;
it never downgrades a shared database. No production scheduling runs in Actions.

## API and preserved UI

- `GET /live`: process liveness.
- `GET /health`: database and baseline migration readiness; returns 503 on failure.
- `GET /health/db`: readiness plus required-table status without connection details.
- `GET /docs`: generated API documentation.
- `GET /api/dashboard`, `/api/stocks`, `/api/news`, `/api/gaming`, `/api/gaming/trending`.
- `GET /api/watchlist`, `POST /api/watchlist`, `DELETE /api/watchlist/{symbol}`.
- `GET /api/collector-status` shows the last finite run for each collector.
- Overview, Stocks, Tech News, Gaming, Settings navigation, responsive light/dark styling,
  offline/error/loading/empty states, and existing text are preserved.

## Collection and remaining work

The finite collector commands are available from `backend` and do not run when a page opens:

```powershell
python -m scripts.collect_stocks
python -m scripts.collect_news
python -m scripts.collect_gaming
```

They share the Supabase `DATABASE_URL`, record success/failure in `collector_runs`, use
database advisory locks to prevent overlap, deduplicate snapshots/articles/posts, and exit.
Do not activate Railway cron services until each command has passed against Supabase. Future
schedules belong in Railway Cron only; see [the setup guide](docs/CLOUD_SETUP.md#future-collector-services).

The application will use APIs whenever possible and only collect publicly accessible web data
where necessary. Xiaoheihe access research precedes its conservative public JSON-LD parser.
No AI tokens are used by these collectors.

[Migration audit](docs/NO_DOCKER_MIGRATION.md) ·
[Implementation status](docs/IMPLEMENTATION_STATUS.md) ·
[Verification results](docs/VERIFICATION.md)
