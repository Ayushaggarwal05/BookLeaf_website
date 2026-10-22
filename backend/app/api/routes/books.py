from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.repositories.book_repo import BookRepository
from backend.app.schemas.book import BookResponse

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=List[BookResponse], summary="List Books")
def list_books(
    author_id: Optional[str] = Query(None, description="Filter books by author ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve list of books, optionally filtered by author."""
    repo = BookRepository(db)
    if author_id:
        return repo.list_by_author(author_id)
    return repo.list_all(skip=skip, limit=limit)


@router.get("/{book_id}", response_model=BookResponse, summary="Get Book Details")
def get_book(book_id: str, db: Session = Depends(get_db)):
    """Retrieve full book metrics including publishing details and royalties."""
    repo = BookRepository(db)
    book = repo.get_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID '{book_id}' was not found.",
        )
    return book
