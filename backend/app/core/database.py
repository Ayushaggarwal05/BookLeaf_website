import sqlite3
import logging
from typing import Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy 2.x declarative base class."""
    pass


# Connection arguments & pooling strategy
connect_args = {}
engine_kwargs = {
    "echo": settings.DEBUG and settings.ENVIRONMENT == "development",
}

if settings.is_sqlite:
    connect_args["check_same_thread"] = False
    engine_kwargs["connect_args"] = connect_args
else:
    # Production-ready PostgreSQL pooling
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    })


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforce foreign key constraints when using SQLite."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_db_engine(db_url: str = None) -> Engine:
    """Create and return a configured SQLAlchemy engine with validation."""
    target_url = db_url or settings.DATABASE_URL
    try:
        return create_engine(target_url, **engine_kwargs)
    except Exception as exc:
        logger.critical(f"Failed to initialize database engine for URL '{target_url}': {exc}")
        raise RuntimeError(f"Database configuration error: {exc}") from exc


engine = create_db_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a transactional database session per request."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_database_connection(db_session: Session = None) -> dict:
    """Validate database connectivity and report database dialect and status."""
    session = db_session or SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": engine.dialect.name,
            "connected": True,
        }
    except SQLAlchemyError as exc:
        logger.error(f"Database health check failed: {exc}")
        return {
            "status": "unhealthy",
            "database": engine.dialect.name,
            "connected": False,
            "error": str(exc),
        }
    finally:
        if db_session is None:
            session.close()
