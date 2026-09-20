from collections.abc import Callable
from datetime import UTC, datetime
from typing import TypeVar

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import session_scope
from app.models import CollectorRun

T = TypeVar("T")


def run_once(collector: str, work: Callable[[Session], tuple[int, int]]) -> tuple[int, int]:
    """Run one finite collection, record its result, and release the PostgreSQL lock."""
    started = datetime.now(UTC)
    with session_scope() as session:
        try:
            acquired = session.execute(
                text("SELECT pg_try_advisory_xact_lock(hashtext(:collector))"),
                {"collector": collector},
            ).scalar()
            if not acquired:
                raise RuntimeError(f"{collector} is already running")
            run = CollectorRun(collector=collector, status="RUNNING", started_at=started)
            session.add(run)
            session.flush()
            found, inserted = work(session)
            run.status = "SUCCESS"
            run.items_found = found
            run.items_inserted = inserted
            run.finished_at = datetime.now(UTC)
            session.commit()
            return found, inserted
        except Exception as exc:
            session.rollback()
            failed = CollectorRun(
                collector=collector,
                status="FAILED",
                started_at=started,
                finished_at=datetime.now(UTC),
                error_message=str(exc)[:4000],
            )
            session.add(failed)
            session.commit()
            raise
