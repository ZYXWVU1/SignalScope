import os

# Unit tests never connect to a real database. The integration job must supply its own URL.
if os.getenv("RUN_DATABASE_TESTS") != "1":
    os.environ["DATABASE_URL"] = "postgresql+psycopg://test:test@unit-test.invalid/test"
    os.environ["CORS_ORIGINS"] = '["https://signalscope.example"]'
    os.environ["FRONTEND_URL"] = "https://signalscope.example"
