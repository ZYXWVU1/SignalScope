# Verification — no-Docker migration, 2026-09-20

## Baseline before changes

Commit `ca197d1`: backend 3 tests passed / 1 database integration skipped; Ruff and mypy
passed; Next.js lint and production build passed. Earlier native startup and browser inspection
confirmed the dashboard offline state and Settings navigation. A real database was not verified.

## Migration and collector checks

| Check                                              | Result                                                  |
| -------------------------------------------------- | ------------------------------------------------------- |
| Backend unit tests                                 | 17 passed; 1 real database integration test skipped     |
| Collector/parser tests                             | Stock/news/Xiaoheihe normalization passed               |
| Alembic domain migration                           | Offline SQL generated for all seven required tables     |
| Standalone collector entry points                  | Three finite `python -m scripts.collect_*` commands    |
| Frontend deployment/API configuration tests        | 9 passed                                                |
| Ruff lint and formatting                           | Passed                                                  |
| Mypy                                               | Passed                                                  |
| Next.js lint and production build                  | Passed; all five routes compiled                        |
| Native Uvicorn startup                             | Passed without container runtime                        |
| Native standard `npm start`                        | Passed without standalone-copy wrapper                  |
| HTTP `/live`                                       | 200 and expected JSON                                   |
| HTTP `/health` with test-only unreachable database | 503, as expected                                        |
| Frontend HTTP routes                               | All five returned 200; overview displayed offline state |
| Native allowed-origin CORS preflight               | Passed                                                  |
| Supabase connection and Alembic application        | Pending private database configuration                  |
| Railway / Vercel deployment                        | Pending user-created projects and GitHub linkage        |
| Cloud collector execution                          | Pending live Supabase and provider credentials          |
| GitHub workflow execution                          | Configuration prepared; not run remotely                |

The unreachable database used for smoke checks was an explicit test-only `.invalid` hostname,
not a connection to Supabase. These checks do not establish cloud readiness. The collector
commands exist, but they are deliberately not run against external providers until Supabase
is configured and provider credentials are supplied.

Upstream Starlette/httpx and AnyIO deprecation warnings remain non-failing.
Node's TypeScript test loader also emits a non-failing module-type inference warning.
The UI and existing migration revision were preserved.
No database schema or cloud account was mutated by the local migration checks.

See [cloud setup](CLOUD_SETUP.md) for the remaining live acceptance steps.
