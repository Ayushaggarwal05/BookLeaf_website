import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash, create_access_token
from backend.app.models.author import Author
from backend.app.models.user import User


def test_auth_login_author_success(client: TestClient, db: Session):
    """Test author login with valid credentials returns token and role."""
    author = Author(
        id="AUTH_LOGIN_01",
        name="Login Author",
        email="login.author@example.com",
        joined_date=date(2024, 1, 1),
        hashed_password=get_password_hash("ValidPass123!"),
        is_active=True,
    )
    db.add(author)
    db.commit()

    res = client.post(
        "/api/v1/auth/login",
        json={"email": "login.author@example.com", "password": "ValidPass123!"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "author"
    assert data["author_id"] == "AUTH_LOGIN_01"
    assert data["email"] == "login.author@example.com"


def test_auth_login_admin_success(client: TestClient, db: Session):
    """Test admin login with valid credentials returns token and role."""
    admin = User(
        id="USR_ADMIN_LOGIN",
        email="login.admin@bookleaf.in",
        full_name="Admin Login Tester",
        role="admin",
        is_active=True,
        hashed_password=get_password_hash("AdminPass123!"),
    )
    db.add(admin)
    db.commit()

    res = client.post(
        "/api/v1/auth/login",
        json={"email": "login.admin@bookleaf.in", "password": "AdminPass123!"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["author_id"] is None


def test_auth_login_invalid_password(client: TestClient, db: Session):
    """Test login with wrong password returns 401."""
    author = Author(
        id="AUTH_LOGIN_02",
        name="Wrong Pass Author",
        email="wrongpass@example.com",
        joined_date=date(2024, 1, 1),
        hashed_password=get_password_hash("CorrectPass123!"),
        is_active=True,
    )
    db.add(author)
    db.commit()

    res = client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "IncorrectPassword!"},
    )
    assert res.status_code == 401
    assert "invalid email or password" in res.json()["detail"].lower()


def test_auth_login_nonexistent_email(client: TestClient):
    """Test login with non-existent email returns 401."""
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "SomePassword123!"},
    )
    assert res.status_code == 401


def test_auth_me_endpoint_success(client: TestClient, db: Session):
    """Test GET /api/v1/auth/me returns current user profile."""
    author = Author(
        id="AUTH_ME_01",
        name="Me Author",
        email="me.author@example.com",
        joined_date=date(2024, 1, 1),
        hashed_password=get_password_hash("Pass123!"),
        is_active=True,
    )
    db.add(author)
    db.commit()

    token = create_access_token({
        "sub": author.id,
        "email": author.email,
        "role": "author",
        "author_id": author.id,
    })

    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "AUTH_ME_01"
    assert data["email"] == "me.author@example.com"
    assert data["role"] == "author"
    assert data["author_id"] == "AUTH_ME_01"


def test_auth_me_expired_token(client: TestClient, db: Session):
    """Test that expired tokens return 401."""
    author = Author(
        id="AUTH_EXPIRED_01",
        name="Expired Token Author",
        email="expired@example.com",
        joined_date=date(2024, 1, 1),
        is_active=True,
    )
    db.add(author)
    db.commit()

    token = create_access_token(
        {"sub": author.id, "email": author.email, "role": "author", "author_id": author.id},
        expires_delta=timedelta(minutes=-10),
    )

    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 401
    assert "expired" in res.json()["detail"].lower()
