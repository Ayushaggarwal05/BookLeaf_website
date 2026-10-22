import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from backend.app.core.database import check_database_connection, get_db, SessionLocal
from backend.app.models.author import Author


def test_database_session_commit_and_query(db: Session):
    """Test standard database session commit and retrieval behavior."""
    db.execute(text("SELECT 1"))
    author = Author(
        id="AUTH_TEST_01",
        name="Test Author",
        email="test.author@example.com",
        city="Test City",
        joined_date=pytest.importorskip("datetime").date(2026, 1, 1),
    )
    db.add(author)
    db.flush()

    found = db.get(Author, "AUTH_TEST_01")
    assert found is not None
    assert found.name == "Test Author"
    assert found.email == "test.author@example.com"


def test_database_session_rollback_on_error(db: Session):
    """Test that a transaction rollback clears uncommitted dirty state."""
    author = Author(
        id="AUTH_TEST_ROLLBACK",
        name="Rollback Author",
        email="rollback@example.com",
        joined_date=pytest.importorskip("datetime").date(2026, 1, 1),
    )
    db.add(author)
    db.flush()

    # Manual rollback
    db.rollback()

    found = db.get(Author, "AUTH_TEST_ROLLBACK")
    assert found is None


def test_check_database_connection_healthy(db: Session):
    """Test check_database_connection reports healthy when connection is live."""
    result = check_database_connection(db)
    assert result["status"] == "healthy"
    assert result["connected"] is True
    assert "database" in result


def test_get_db_generator_lifecycle():
    """Test get_db generator properly yields and closes the session."""
    gen = get_db()
    session = next(gen)
    assert isinstance(session, Session)
    # Complete generator
    try:
        next(gen)
    except StopIteration:
        pass
