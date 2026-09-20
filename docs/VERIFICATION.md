# Foundation verification — 2026-09-20

All project files and local dependency/tool caches are contained in `SignalScope`.

| Check | Result |
| --- | --- |
| Backend pytest | 3 passed; real PostgreSQL test skipped |
| Ruff lint and formatting | Passed |
| Mypy strict checks | Passed |
| Alembic PostgreSQL offline migration SQL | Generated successfully |
| Uvicorn startup | Passed |
| Live HTTP `/live` | 200, `{"status":"ok"}` |
| Live HTTP `/health` without PostgreSQL | 503, as expected |
| Frontend ESLint | Passed |
| Frontend TypeScript | Passed |
| Next.js production build | Passed, all five routes generated |
| Standalone production server | Started successfully |
| Live frontend HTTP checks | All five routes returned HTTP 200 |
| Browser inspection | Dashboard offline/empty state rendered; Settings navigation worked |
| npm installation audit | 0 known vulnerabilities reported at install time |
| Docker Compose / live PostgreSQL integration | Not run: Docker/PostgreSQL unavailable in this environment |
| CI | Added, not run remotely |
| Deployment | Not performed |

The Python tests emitted upstream Starlette/httpx and AnyIO deprecation warnings.
These did not fail the tests. Provider APIs were not called, and no API keys were required.

**Phase 1 is not yet accepted.** A healthy real PostgreSQL connection remains required.
The source brief explicitly prohibits moving to the stock phase until the foundation works.

Next acceptance command, after Docker is available, from the project root:

```powershell
Copy-Item .env.example .env # only if .env does not already exist
docker compose up --build -d
Invoke-RestMethod http://localhost:8000/health
```

Confirm the dashboard reports a connection and run the PostgreSQL integration test
using the README instructions. Docker build, migrations against PostgreSQL, and container
health dependencies are configured but have not been validated by this local run.
