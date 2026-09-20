# Cloud setup: Supabase → Railway → Vercel

This guide deploys the existing foundation and its restored finite collectors. The frontend
still needs live-data presentation work, but collectors, domain tables, APIs, and run logging
are now present. Keep all work in the current SignalScope repository.

## 1. Connect the existing GitHub repository

The initial audit found no remote; during setup the checkout was linked to
`https://github.com/ZYXWVU1/SignalScope.git`, on `main`. Reuse this repository.
From `SignalScope`, verify:

```powershell
git remote -v
git branch --show-current
git log --oneline -5
```

Open the GitHub repository that already contains SignalScope. Copy its clone URL from
**Code**. If `origin` is missing, link that existing repository:

```powershell
git remote add origin <EXISTING_REPOSITORY_CLONE_URL>
git fetch origin
```

Check its default branch and history before pushing. This local checkout now uses
`main`. If histories diverge or are unrelated,
reconcile them before uploading changes; never force-push to replace remote history.
If `origin` already exists, reuse it after verifying it points to the intended repository.

The deployment instructions below assume the GitHub repository root contains `frontend/`
and `backend/`. If the remote instead contains a parent `SignalScope/` directory, prefix
both root/config paths accordingly. Do not relocate application code for deployment.

Commit the migration changes, then push your selected branch when ready. Connect Railway
and Vercel to that same repository and branch. Grant their GitHub integrations access to
that repository through their normal setup screens.

## 2. Create Supabase and configure the local backend

1. Open [Supabase](https://supabase.com/dashboard), sign in, and choose **New project**.
2. Select your organization, enter a name such as `signalscope-dev`, choose a region near
   the intended Railway region, and create a database password in your password manager.
3. Review the selected plan in the dashboard before creating the project. Wait until it is ready.
4. Open **Connect** and select **Session pooler**. Copy the PostgreSQL URI privately.
   Session mode is the straightforward IPv4-compatible option for this synchronous backend.
   A direct connection also works when the client has the required network support.
5. In the project root, copy `.env.example` to `.env` only if `.env` does not already exist.
6. Edit `SignalScope/.env` locally. Replace the URI's scheme with `postgresql+psycopg://`,
   fill in the database password privately, and append `?sslmode=require` (or
   `&sslmode=require` if it already contains a query). Percent-encode special characters
   in the password; do not change the provider-generated hostname or username.
7. Keep these local origins:

```dotenv
CORS_ORIGINS=["http://localhost:3000"]
FRONTEND_URL=http://localhost:3000
```

Never paste `DATABASE_URL` into chat. It belongs only in your ignored local `.env` and the
backend host's secret settings. A Supabase API key/anon key is not a PostgreSQL password;
this app connects through SQLAlchemy, not the Supabase JavaScript SDK.

Use **session mode on port 5432**, not the transaction pooler on 6543, for this setup.
The backend supplies TLS when `sslmode` is absent and preserves stricter certificate settings.
Do not disable TLS to work around connection errors.

From `SignalScope`:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Open `http://localhost:8000/health`. It must return HTTP 200 and `{"status":"ok"}`.
Then open `/health/db`; every returned table value must be `true` before running collectors.
In another terminal using the same virtual environment:

```powershell
$env:RUN_DATABASE_TESTS = '1'
pytest tests/test_database_integration.py
Remove-Item Env:RUN_DATABASE_TESTS
```

The migration chain creates Alembic revision tracking and the stock/news/gaming/run tables.
Do not manually invent tables in the Supabase Table Editor.
Use a separate Supabase project for production once you deploy real application data.

## 3. Verify local Next.js

From `SignalScope`, in a separate terminal:

```powershell
cd frontend
Copy-Item .env.example .env.local
npm ci
npm run dev
```

Do not overwrite an existing `.env.local`. Its local value should be:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Open `http://localhost:3000`. After step 2 passes, the overview should show **Backend and
database connected**. Stocks/news/gaming remain empty until their later implementation.
Try the navigation and **Check connection** button.

## 4. Create the Railway backend

1. Open [Railway](https://railway.com/dashboard) and create a project from your **existing
   GitHub repository**. Select the intended deployment branch.
2. Create/select the API service; set **Root Directory** to `/backend`.
3. Set the Railway configuration file path to `/backend/railway.json`. This file path is
   relative to the repository root, independently of the service Root Directory setting.
4. Use **Railpack**. It detects `requirements.txt` and installs Python dependencies.
   `.python-version` selects Python 3.12. No custom Dockerfile or database service is needed.
5. Add these service variables directly in Railway:

| Variable       | Value                                                                   |
| -------------- | ----------------------------------------------------------------------- |
| `DATABASE_URL` | Production Supabase session-pooler URI, configured privately            |
| `CORS_ORIGINS` | `[]` initially; replace with the exact Vercel origin after step 5       |
| `FRONTEND_URL` | Leave unset initially; set to the Vercel production origin after step 5 |

Provider keys are not needed for this foundation. Add `ALPHA_VANTAGE_API_KEY`, `NEWS_API_KEY`,
and pacing settings when their collectors exist. Do not define a fixed `PORT`; Railway provides it.

6. Verify the deployment settings loaded from the committed configuration:

```text
Builder: Railpack
Pre-deploy: alembic upgrade head
Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Healthcheck: /health
```

7. Deploy. A failed migration must prevent the new API deployment from becoming ready.
8. Under service networking, generate a public HTTPS domain. Open `<RAILWAY_API_ORIGIN>/health`,
   `<RAILWAY_API_ORIGIN>/health/db`, and `<RAILWAY_API_ORIGIN>/docs`. Require HTTP 200 before
   moving to Vercel.
9. Verify GitHub automatic deployments target the intended production branch. Enable waiting
   for CI checks if available in your project settings.

The config file prepares the deployment; it does not provision a project or set secrets by itself.
Use a single API replica initially. Migration changes should be backward-compatible with the
previous API version during future deployments.

## 5. Create the Vercel frontend

1. Open [Vercel](https://vercel.com/new), import the **same existing GitHub repository**.
2. Set **Root Directory** to `frontend` and use the **Next.js** framework preset.
3. Use Node.js 22 and the committed `vercel.json` defaults: install `npm ci`, build `npm run build`.
   Leave the output directory at the framework default. Do not set a static export directory.
4. Add `NEXT_PUBLIC_API_URL` with the HTTPS Railway API origin from step 4, without `/health`,
   credentials, a query string, or a fragment. Set it for Production and any Preview environments
   you intend to deploy. Do not set any database password or provider key in Vercel.
5. Deploy. Record the stable production frontend origin. Every API-origin change needs a new
   Vercel build because public Next.js variables are build-time configuration.
6. Return to Railway and set both `FRONTEND_URL` and `CORS_ORIGINS` using that exact origin:

```dotenv
FRONTEND_URL=https://YOUR_FRONTEND_DOMAIN
CORS_ORIGINS=["https://YOUR_FRONTEND_DOMAIN"]
```

Apply the Railway variable changes/redeploy. Add local or preview origins explicitly only
when needed. Do not use `*` or wildcard preview domains. Current health fetching is server-side,
but the explicit allowlist is also tested for future browser-to-API endpoints.

7. Open Vercel's production URL. Confirm connected status and all five navigation routes.
8. Push a normal follow-up commit to your production branch and verify both services deploy
   from the expected commit. Verify `/health` and the frontend again after deployment.

Railway and Vercel operate in the cloud; the website no longer depends on your computer once
these deployments are running. Automatic **collection** still depends on enabling the tested
Railway cron services below.

## Future collector services

**Do not enable these jobs yet.** First run all three commands locally against Supabase and
verify their records through `/api/collector-status` and the domain endpoints. These are the
Railway service settings after each collector has passed.

| Separate Railway service | Command                            | Cron schedule (UTC) |
| ------------------------ | ---------------------------------- | ------------------- |
| Stocks                   | `python -m scripts.collect_stocks` | `0 * * * *`         |
| Technology news          | `python -m scripts.collect_news`   | `15 * * * *`        |
| Gaming                   | `python -m scripts.collect_gaming` | `30 */2 * * *`      |

Each future service uses the same repository and `/backend` root, plus its own cron config.
Do not reuse the API's `railway.json`: that file starts Uvicorn, runs migrations, and requires
an HTTP healthcheck. Dedicated cron configuration must have no API start command, no healthcheck,
and no migration hook. Use one scheduling mechanism per collector, with Railway Cron owning it.

Before enabling any job, verify that it reads the existing watchlist where applicable, records
a collector run, deduplicates data, acquires a per-collector database advisory lock on a dedicated
session, and exits after closing all HTTP/database/browser resources. Locks must be held until
the run finishes and released in `finally`. No Redis or background infinite loop is needed.

Railway skips a scheduled launch if the previous execution is still running. Database locking
will additionally protect against manual or other-service overlap. Show last successful collection
from stored run records, not from Railway APIs.

The Xiaoheihe implementation uses the documented public JSON-LD HTML method and no browser
runtime. If the configured public page does not expose records, it records a successful empty
run rather than inventing endpoints or bypassing access controls.

## Troubleshooting and final acceptance

- **Database URL rejected:** use the PostgreSQL URI, not a Supabase web/API URL. Include the
  database/user/host and supported TLS mode. Keep credentials out of screenshots and logs.
- **Connection timeout / IPv6 error:** use the exact Session pooler URI from Supabase Connect.
  Check that the project is running and its network restrictions permit the backend.
- **Readiness 503:** verify the database connection and `alembic upgrade head` before changing
  the healthcheck. `/live` succeeding alone is not a database readiness pass.
- **Frontend offline:** verify its configured API origin, rebuild after variable changes,
  and check Railway `/health`. No client calls should go directly to providers or PostgreSQL.
- **CORS failure:** provide a JSON array of exact origins, with no path or wildcard.
- **Railway ignores configuration:** verify `/backend/railway.json` is explicitly selected;
  setting Root Directory alone does not select that config path.

Completion evidence: live Supabase integration test passes; Railway and Vercel URLs work;
frontend shows connected status; a GitHub push deploys both services. Collector execution and
domain-feature regression checks remain blocked until those features are built.

## Official references

- [Supabase connection modes and TLS](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Railway configuration](https://docs.railway.com/config-as-code/reference)
- [Railway monorepo config paths](https://docs.railway.com/builds/build-configuration)
- [Railpack Python dependency detection](https://railpack.com/languages/python)
- [Railway cron execution](https://docs.railway.com/cron-jobs)
- [Vercel monorepos](https://vercel.com/docs/monorepos)
- [Vercel environment variables](https://vercel.com/docs/environment-variables)
