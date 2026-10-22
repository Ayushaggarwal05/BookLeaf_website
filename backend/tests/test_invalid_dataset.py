import pytest
from pathlib import Path
from sqlalchemy.orm import Session

from backend.app.services.seed_service import (
    import_sample_data,
    load_dataset_file,
    DatasetValidationError,
)


def test_missing_dataset_file_raises_filenotfound():
    """Verify loading from non-existent file path raises FileNotFoundError."""
    non_existent = Path("data/definitely_not_a_real_dataset_file.json")
    with pytest.raises(FileNotFoundError) as exc_info:
        load_dataset_file(non_existent)
    assert "not found" in str(exc_info.value).lower()


def test_malformed_root_json_raises_validation_error(db: Session):
    """Verify non-dictionary root JSON raises DatasetValidationError."""
    invalid_data = ["not", "a", "dictionary"]
    with pytest.raises(DatasetValidationError) as exc_info:
        import_sample_data(db, dataset=invalid_data)
    assert "root json must be an object" in str(exc_info.value).lower()


def test_author_missing_required_fields(db: Session):
    """Verify author record missing email raises DatasetValidationError and rolls back."""
    invalid_data = {
        "authors": [
            {
                "author_id": "AUTH_BAD",
                "name": "Nameless Author",
                # email is intentionally missing
                "joined_date": "2024-01-01",
                "books": [],
            }
        ]
    }
    with pytest.raises(DatasetValidationError) as exc_info:
        import_sample_data(db, dataset=invalid_data)
    assert "missing required 'name' or 'email'" in str(exc_info.value).lower()


def test_author_invalid_date_format(db: Session):
    """Verify invalid date format raises DatasetValidationError."""
    invalid_data = {
        "authors": [
            {
                "author_id": "AUTH_DATE_BAD",
                "name": "Bad Date Author",
                "email": "baddate@example.com",
                "joined_date": "15/03/2023",  # Expected YYYY-MM-DD
                "books": [],
            }
        ]
    }
    with pytest.raises(DatasetValidationError) as exc_info:
        import_sample_data(db, dataset=invalid_data)
    assert "invalid date format" in str(exc_info.value).lower()


def test_book_missing_isbn(db: Session):
    """Verify book missing required ISBN raises DatasetValidationError."""
    invalid_data = {
        "authors": [
            {
                "author_id": "AUTH_BOOK_BAD",
                "name": "Book Author",
                "email": "bookauthor@example.com",
                "joined_date": "2024-01-01",
                "books": [
                    {
                        "book_id": "BK_NO_ISBN",
                        "title": "Title with No ISBN",
                        # isbn missing
                        "genre": "Fiction",
                    }
                ],
            }
        ]
    }
    with pytest.raises(DatasetValidationError) as exc_info:
        import_sample_data(db, dataset=invalid_data)
    assert "missing required 'title', 'isbn', or 'genre'" in str(exc_info.value).lower()
