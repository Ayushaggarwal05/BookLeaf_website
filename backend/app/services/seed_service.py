import json
import logging
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.models.author import Author
from backend.app.models.book import Book

logger = logging.getLogger(__name__)


class DatasetValidationError(Exception):
    """Raised when JSON dataset structure or records are invalid."""
    pass


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse YYYY-MM-DD date string into date object, returning None if missing or empty."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise DatasetValidationError(f"Invalid date format '{date_str}', expected YYYY-MM-DD: {exc}")


def parse_decimal(val: Any) -> Optional[Decimal]:
    """Safely convert numeric/monetary values to Decimal to prevent float inaccuracies."""
    if val is None:
        return None
    try:
        return Decimal(str(val))
    except Exception as exc:
        raise DatasetValidationError(f"Invalid monetary/numeric value '{val}': {exc}")


def load_dataset_file(file_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Locate and parse the JSON dataset file without altering source data.
    Raises FileNotFoundError if missing or json.JSONDecodeError if malformed.
    """
    target = file_path or settings.resolved_sample_data_path

    if not target.exists():
        raise FileNotFoundError(
            f"Official dataset file not found at: {target.resolve()}. "
            "Please ensure 'data/bookleaf_sample_data.json' exists."
        )

    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict) or "authors" not in data:
        raise DatasetValidationError(
            "Invalid dataset format: Root JSON must be an object with an 'authors' list."
        )

    if not isinstance(data["authors"], list):
        raise DatasetValidationError("Invalid dataset format: 'authors' property must be a list.")

    return data


def import_sample_data(
    db: Session,
    dataset: Optional[Dict[str, Any]] = None,
    file_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Import and upsert authors and books idempotently.
    Guarantees:
    - Never deletes or modifies user-created support tickets.
    - Preserves all source fields accurately.
    - Avoids duplicate records when run multiple times.
    - Transactional: commits on complete success, rollbacks on error.
    """
    if dataset is None:
        dataset = load_dataset_file(file_path)

    if not isinstance(dataset, dict) or "authors" not in dataset:
        raise DatasetValidationError(
            "Invalid dataset format: Root JSON must be an object with an 'authors' list."
        )

    if not isinstance(dataset["authors"], list):
        raise DatasetValidationError("Invalid dataset format: 'authors' property must be a list.")

    authors_list = dataset.get("authors", [])
    total_authors_in_source = len(authors_list)
    total_books_in_source = sum(len(a.get("books", [])) for a in authors_list)

    summary = {
        "source_authors_count": total_authors_in_source,
        "source_books_count": total_books_in_source,
        "authors_inserted": 0,
        "authors_updated": 0,
        "books_inserted": 0,
        "books_updated": 0,
        "errors": [],
        "status": "pending",
    }

    try:
        for a_idx, author_raw in enumerate(authors_list):
            author_id = author_raw.get("author_id")
            if not author_id:
                raise DatasetValidationError(f"Author at index {a_idx} is missing required 'author_id'.")

            name = author_raw.get("name")
            email = author_raw.get("email")
            if not name or not email:
                raise DatasetValidationError(f"Author {author_id} is missing required 'name' or 'email'.")

            joined_date = parse_date(author_raw.get("joined_date"))
            if not joined_date:
                raise DatasetValidationError(f"Author {author_id} has invalid or missing 'joined_date'.")

            # Check existing author by ID or email
            existing_author = db.get(Author, author_id)
            if not existing_author:
                existing_author = db.query(Author).filter(Author.email == email).first()

            if existing_author:
                # Update attributes while preserving primary key
                existing_author.name = name
                existing_author.email = email
                existing_author.phone = author_raw.get("phone")
                existing_author.city = author_raw.get("city")
                existing_author.joined_date = joined_date
                summary["authors_updated"] += 1
            else:
                new_author = Author(
                    id=author_id,
                    name=name,
                    email=email,
                    phone=author_raw.get("phone"),
                    city=author_raw.get("city"),
                    joined_date=joined_date,
                )
                db.add(new_author)
                summary["authors_inserted"] += 1

            # Flush author to ensure foreign key constraint satisfaction for books
            db.flush()

            # Process books for this author
            books_raw = author_raw.get("books", [])
            for b_idx, book_raw in enumerate(books_raw):
                book_id = book_raw.get("book_id")
                if not book_id:
                    raise DatasetValidationError(
                        f"Book at index {b_idx} for author {author_id} is missing 'book_id'."
                    )

                title = book_raw.get("title")
                isbn = book_raw.get("isbn")
                genre = book_raw.get("genre")
                status = book_raw.get("status", "In Production")

                if not title or not isbn or not genre:
                    raise DatasetValidationError(
                        f"Book {book_id} is missing required 'title', 'isbn', or 'genre'."
                    )

                pub_date = parse_date(book_raw.get("publication_date"))
                payout_date = parse_date(book_raw.get("last_royalty_payout_date"))
                mrp = parse_decimal(book_raw.get("mrp"))
                author_royalty = parse_decimal(book_raw.get("author_royalty_per_copy"))
                copies_sold = int(book_raw.get("total_copies_sold", 0))
                total_royalty_earned = parse_decimal(book_raw.get("total_royalty_earned")) or Decimal("0.00")
                royalty_paid = parse_decimal(book_raw.get("royalty_paid")) or Decimal("0.00")
                royalty_pending = parse_decimal(book_raw.get("royalty_pending")) or Decimal("0.00")

                available_on = book_raw.get("available_on", [])
                print_partner = book_raw.get("print_partner")

                existing_book = db.get(Book, book_id)
                if not existing_book:
                    existing_book = db.query(Book).filter(Book.isbn == isbn).first()

                if existing_book:
                    existing_book.author_id = author_id
                    existing_book.title = title
                    existing_book.isbn = isbn
                    existing_book.genre = genre
                    existing_book.publication_date = pub_date
                    existing_book.status = status
                    existing_book.mrp = mrp
                    existing_book.author_royalty_per_copy = author_royalty
                    existing_book.total_copies_sold = copies_sold
                    existing_book.total_royalty_earned = total_royalty_earned
                    existing_book.royalty_paid = royalty_paid
                    existing_book.royalty_pending = royalty_pending
                    existing_book.last_royalty_payout_date = payout_date
                    existing_book.print_partner = print_partner
                    existing_book.available_on = available_on
                    summary["books_updated"] += 1
                else:
                    new_book = Book(
                        id=book_id,
                        author_id=author_id,
                        title=title,
                        isbn=isbn,
                        genre=genre,
                        publication_date=pub_date,
                        status=status,
                        mrp=mrp,
                        author_royalty_per_copy=author_royalty,
                        total_copies_sold=copies_sold,
                        total_royalty_earned=total_royalty_earned,
                        royalty_paid=royalty_paid,
                        royalty_pending=royalty_pending,
                        last_royalty_payout_date=payout_date,
                        print_partner=print_partner,
                        available_on=available_on,
                    )
                    db.add(new_book)
                    summary["books_inserted"] += 1

        # Provision demo admin and author credentials for local dev/testing
        from backend.app.services.auth_service import AuthService
        auth_service = AuthService(db)
        summary["auth_provisioning"] = auth_service.provision_demo_accounts()

        db.commit()
        summary["status"] = "success"
        logger.info(
            f"Sample data import finished successfully: "
            f"Authors ({summary['authors_inserted']} inserted, {summary['authors_updated']} updated), "
            f"Books ({summary['books_inserted']} inserted, {summary['books_updated']} updated)."
        )
        return summary

    except Exception as exc:
        db.rollback()
        summary["status"] = "error"
        summary["errors"].append(str(exc))
        logger.error(f"Sample data import failed and rolled back: {exc}")
        raise


def run_seed(file_path: Optional[str] = None) -> Dict[str, Any]:
    """CLI / Execution helper to run seeding with an isolated session."""
    target_path = Path(file_path) if file_path else None
    with SessionLocal() as session:
        return import_sample_data(session, file_path=target_path)


if __name__ == "__main__":
    import sys
    print("Starting BookLeaf database seed...")
    cli_path = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        res = run_seed(cli_path)
        print("Seed completed successfully:")
        print(f"  Source Authors: {res['source_authors_count']}")
        print(f"  Source Books:   {res['source_books_count']}")
        print(f"  Authors Added:  {res['authors_inserted']}, Updated: {res['authors_updated']}")
        print(f"  Books Added:    {res['books_inserted']}, Updated: {res['books_updated']}")
    except Exception as err:
        print(f"Seed failed: {err}", file=sys.stderr)
        sys.exit(1)
