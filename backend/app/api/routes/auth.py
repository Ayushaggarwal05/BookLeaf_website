from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.dependencies import AuthenticatedUser, get_current_user
from backend.app.schemas.auth import LoginRequest, TokenResponse, CurrentUserResponse
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & Identity"])


@router.post("/login", response_model=TokenResponse, summary="Authenticate User or Author")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate author or administrative user using email and password.
    Returns signed JWT access token and user identity.
    """
    auth_service = AuthService(db)
    try:
        user_principal, token = auth_service.authenticate(
            email=credentials.email,
            password=credentials.password,
        )
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            role=user_principal.role,
            user_id=user_principal.id,
            email=user_principal.email,
            name=user_principal.full_name,
            author_id=user_principal.author_id,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=CurrentUserResponse, summary="Get Current Authenticated Identity")
def get_me(current_user: AuthenticatedUser = Depends(get_current_user)):
    """
    Retrieve current authenticated user context and role from validated JWT token.
    Never relies on client-supplied author or role parameters.
    """
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        author_id=current_user.author_id,
    )
