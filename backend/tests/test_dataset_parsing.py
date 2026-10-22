import pytest
from datetime import date
from decimal import Decimal
from pathlib import Path

from backend.app.services.seed_service import (
    load_dataset_file,
    parse_date,
    parse_decimal,
)


def test_load_official_dataset_file():
    """Verify official JSON file can be located and contains expected structure."""
    data = load_dataset_file()
    assert isinstance(data, dict)
    assert "authors" in data
    authors = data["authors"]
    assert len(authors) == 10

    # Verify total books count across all authors
    total_books = sum(len(a.get("books", [])) for a in authors)
    assert total_books == 18


def test_parse_date_valid():
    """Verify valid date strings format as Python date objects."""
    assert parse_date("2023-03-15") == date(2023, 3, 15)
    assert parse_date("2024-12-31") == date(2024, 12, 31)


def test_parse_date_none_and_empty():
    """Verify empty/null dates return None."""
    assert parse_date(None) is None
    assert parse_date("") is None


def test_parse_decimal_monetary_precision():
    """Verify monetary values are converted to exact Decimals, preserving precision."""
    val1 = parse_decimal(399)
    assert isinstance(val1, Decimal)
    assert val1 == Decimal("399")

    val2 = parse_decimal(42.50)
    assert isinstance(val2, Decimal)
    assert val2 == Decimal("42.5")

    val3 = parse_decimal(None)
    assert val3 is None


def test_dataset_contains_expected_fields():
    """Verify first author and book retain required assignment fields."""
    data = load_dataset_file()
    first_author = data["authors"][0]
    assert first_author["author_id"] == "AUTH001"
    assert first_author["name"] == "Priya Sharma"
    assert "@" in first_author["email"]
    assert "books" in first_author
    assert len(first_author["books"]) >= 1

    first_book = first_author["books"][0]
    assert first_book["book_id"] == "BK001"
    assert first_book["title"] == "Whispers of the Ganges"
    assert "isbn" in first_book
    assert "genre" in first_book
    assert "mrp" in first_book
    assert "total_copies_sold" in first_book
    assert "total_royalty_earned" in first_book
    assert "royalty_paid" in first_book
    assert "royalty_pending" in first_book
