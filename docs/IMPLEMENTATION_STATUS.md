# Implementation status

The supplied specification requires Phase 1 to pass before starting Phase 2.

## Foundation implemented

- Docker Compose PostgreSQL with persistent storage, health checks, and localhost ports.
- Independent migration job before FastAPI starts.
- FastAPI `/health` checks PostgreSQL and the expected Alembic revision; `/live` checks process liveness.
- SQLAlchemy engine, Pydantic environment configuration, explicit CORS, baseline Alembic migration.
- Next.js App Router, TypeScript, Tailwind, five navigation routes, responsive system theme.
- Server-only API connection, bounded timeout, offline/loading/error/empty states.
- Backend unit tests and opt-in PostgreSQL integration test; CI configuration.

## Acceptance gate

Phase 1 is not accepted until all of these have been observed:

1. `docker compose up --build -d` starts the database, applies migrations, and starts both apps.
2. `http://localhost:8000/health` returns HTTP 200 and exactly `{"status":"ok"}`.
3. `http://localhost:3000` loads and reports the backend and database connected.
4. The PostgreSQL integration test passes.

The baseline migration only establishes Alembic revision tracking. Domain tables belong to
subsequent phases; the current pages intentionally have no generated market or news records.

## Remaining work in order

Stock tables/provider/watchlist/collection/charts; technology news collection and UI;
documented live Xiaoheihe research before any scraping code; gaming collection and UI;
unified data endpoint; independent scheduled collector jobs; feature tests and operational
hardening; full documentation and deployment.

No collectors, third-party integrations, AI calls, scheduled collection, authentication,
or public deployment are implemented in this foundation. Do not deploy publicly as a finished MVP.
