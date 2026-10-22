from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.repositories.author_repo import AuthorRepository
from backend.app.schemas.author import AuthorResponse, AuthorDetailResponse

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.get("", response_model=List[AuthorResponse], summary="List Authors")
def list_authors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve paginated list of registered authors."""
    repo = AuthorRepository(db)
    return repo.list_all(skip=skip, limit=limit)


@router.get("/{author_id}", response_model=AuthorDetailResponse, summary="Get Author Details")
def get_author(author_id: str, db: Session = Depends(get_db)):
    """Retrieve full author profile along with their catalog of books."""
    repo = AuthorRepository(db)
    author = repo.get_by_id_with_books(author_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with ID '{author_id}' was not found.",
        )
    return author
