#!/usr/bin/env python3
"""Database Seed Script.

Populate the database with initial data after migrations.
Run automatically with: fastmvc db reset --seed

Usage:
    python scripts/seed.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your models here
# from example.entity import Item

# Database URL from environment or default
DATABASE_URL = "sqlite:///./app.db"
# For PostgreSQL: "postgresql://user:pass@localhost/dbname"


def seed_data():
    """Seed the database with initial data."""
    print("🌱 Seeding database...")

    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Example: Add initial items
        # initial_items = [
        #     {"name": "Welcome Item", "description": "Your first item", "completed": False},
        #     {"name": "Learn FastMVC", "description": "Explore the framework", "completed": False},
        # ]
        #
        # for item_data in initial_items:
        #     item = Item(**item_data)
        #     db.add(item)
        #
        # db.commit()

        print("✅ Seed data applied successfully!")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
