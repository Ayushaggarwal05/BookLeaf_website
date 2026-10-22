import os
import sqlite3
import pytest
from pathlib import Path
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.core.database import Base, get_db
from backend.app.main import app
import backend.app.models  # noqa: F401

TEST_DB_FILE = Path(__file__).resolve().parent / "test_bookleaf.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE.as_posix()}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Ensure SQLite enforces foreign keys strictly in tests."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test tables at test session start and cleanup at teardown."""
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except Exception:
            pass

    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except Exception:
            pass


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Provide a clean transactional session per test, rolled back or cleaned up."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
