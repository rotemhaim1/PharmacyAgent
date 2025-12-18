#!/usr/bin/env python3
"""
Reset local database (backend/app.db) with the correct schema.
WARNING: This will delete all data in the local database.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.db.session import _default_sqlite_path
from app.db.seed import init_db, seed_if_empty


def reset_local_db():
    db_path = _default_sqlite_path()
    
    print(f"Database path: {db_path}")
    
    if db_path.exists():
        response = input(f"\nWARNING: This will DELETE {db_path} and recreate it.\nContinue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
        
        db_path.unlink()
        print(f"✓ Deleted {db_path}")
    
    print("\nCreating database with correct schema...")
    init_db()
    print("✓ Database schema created")
    
    print("\nSeeding database with initial data...")
    seed_if_empty()
    print("✓ Database seeded")
    
    print(f"\n✓ Done! Database ready at {db_path}")
    print("\nDefault user credentials:")
    print("  Phone: +972501000001 (or any of the seeded phones)")
    print("  Password: password123")


if __name__ == "__main__":
    reset_local_db()

