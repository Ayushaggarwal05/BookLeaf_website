import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Argon2 password hasher
password_hasher = PasswordHash((Argon2Hasher(),))


def get_password_hash(password: str) -> str:
    """Hash password using Argon2."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    """Verify password against Argon2 hash with constant-time comparison."""
    if not hashed_password:
        return False
    try:
        return password_hasher.verify(plain_password, hashed_password)
    except Exception as exc:
        logger.warning(f"Password verification error: {exc}")
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT access token with expiration timestamp."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now,
    })
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT access token signature and expiration."""
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
