"""
SQLAlchemy engine and session dependency.
Import `get_db` into routers to obtain a database session.
"""

import logging

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Database URL
# ---------------------------------------------------------------------------
db_url = settings.DATABASE_URL

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
if db_url.startswith("sqlite"):
    # SQLite-specific configuration
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
    )

    # Enable WAL mode and foreign-key enforcement for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragmas(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

else:
    # PostgreSQL / production configuration
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
    )


# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ---------------------------------------------------------------------------
# Base class for all ORM models
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------
def get_db():
    """Yields a database session and ensures it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()