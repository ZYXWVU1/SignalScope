import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.database.session import check_database, engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    engine.dispose()


app = FastAPI(title="SignalScope API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)


class Health(BaseModel):
    status: Literal["ok"] = "ok"


def require_database() -> None:
    try:
        check_database()
    except Exception:
        logger.warning("Database readiness check failed")
        raise HTTPException(
            status_code=503, detail="Database unavailable or migrations pending"
        ) from None


@app.get("/health", response_model=Health)
def health(_: Annotated[None, Depends(require_database)]) -> Health:
    """Readiness: PostgreSQL must respond and the migration must be applied."""
    return Health()


@app.get("/live", response_model=Health)
def live() -> Health:
    """Process liveness only; does not imply that PostgreSQL is ready."""
    return Health()
