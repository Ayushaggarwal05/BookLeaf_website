"""
Convenience seed runner for BookLeaf Author Support & Communication Portal.
Reads from data/bookleaf_sample_data.json and imports authors & books idempotently.
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app.services.seed_service import run_seed

if __name__ == "__main__":
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    print("==================================================")
    print("  BookLeaf Database Seeding Utility")
    print("==================================================")
    try:
        results = run_seed(file_arg)
        print("\nSeed Summary:")
        print(f"  Source Authors in file : {results['source_authors_count']}")
        print(f"  Source Books in file   : {results['source_books_count']}")
        print(f"  Authors Inserted       : {results['authors_inserted']}")
        print(f"  Authors Updated        : {results['authors_updated']}")
        print(f"  Books Inserted         : {results['books_inserted']}")
        print(f"  Books Updated          : {results['books_updated']}")
        print(f"  Status                 : {results['status'].upper()}")
        print("==================================================")
        print("Database seed completed successfully.")
    except Exception as err:
        print(f"\n[ERROR] Seeding failed: {err}", file=sys.stderr)
        sys.exit(1)
