#!/usr/bin/env python3
"""
Simple script to view database contents.
Usage: python view_db.py
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.db.models import User, Medication, InventoryItem, Prescription, Ticket
from sqlalchemy import select


def view_db():
    with SessionLocal() as db:
        print("=" * 80)
        print("DATABASE CONTENTS")
        print("=" * 80)
        
        # Users
        users = db.execute(select(User)).scalars().all()
        print(f"\n📋 USERS ({len(users)} total):")
        print("-" * 80)
        for u in users:
            print(f"  ID: {u.id}")
            print(f"  Name: {u.full_name}")
            print(f"  Phone: {u.phone}")
            print(f"  Language: {u.preferred_language}")
            print(f"  Loyalty ID: {u.loyalty_id or 'N/A'}")
            print()
        
        # Medications
        meds = db.execute(select(Medication)).scalars().all()
        print(f"\n💊 MEDICATIONS ({len(meds)} total):")
        print("-" * 80)
        for m in meds:
            print(f"  ID: {m.id}")
            print(f"  Name (EN): {m.name}")
            print(f"  Name (HE): {m.name_he}")
            print(f"  Form: {m.form}")
            print(f"  Strength: {m.strength}")
            print(f"  OTC/Rx: {m.otc_or_rx}")
            print()
        
        # Inventory
        inv = db.execute(select(InventoryItem)).scalars().all()
        print(f"\n📦 INVENTORY ({len(inv)} total):")
        print("-" * 80)
        for i in inv:
            med = db.execute(select(Medication).where(Medication.id == i.medication_id)).scalars().first()
            med_name = med.name if med else "Unknown"
            print(f"  Store: {i.store_name}")
            print(f"  Medication: {med_name}")
            print(f"  Quantity: {i.quantity}")
            print(f"  Last Updated: {i.last_updated}")
            print()
        
        # Prescriptions
        presc = db.execute(select(Prescription)).scalars().all()
        print(f"\n📝 PRESCRIPTIONS ({len(presc)} total):")
        print("-" * 80)
        for p in presc:
            user = db.execute(select(User).where(User.id == p.user_id)).scalars().first()
            med = db.execute(select(Medication).where(Medication.id == p.medication_id)).scalars().first()
            user_name = user.full_name if user else "Unknown"
            med_name = med.name if med else "Unknown"
            print(f"  ID: {p.id}")
            print(f"  User: {user_name}")
            print(f"  Medication: {med_name}")
            print(f"  Status: {p.status}")
            print(f"  Refills Left: {p.refills_left}")
            print()
        
        # Tickets (Reservations, etc.)
        tickets = db.execute(select(Ticket)).scalars().all()
        print(f"\n🎫 TICKETS ({len(tickets)} total):")
        print("-" * 80)
        for t in tickets:
            user_name = "N/A"
            med_name = "N/A"
            if t.user_id:
                user = db.execute(select(User).where(User.id == t.user_id)).scalars().first()
                user_name = user.full_name if user else "Unknown"
            if t.medication_id:
                med = db.execute(select(Medication).where(Medication.id == t.medication_id)).scalars().first()
                med_name = med.name if med else "Unknown"
            print(f"  ID: {t.id}")
            print(f"  Type: {t.type}")
            print(f"  User: {user_name}")
            print(f"  Medication: {med_name}")
            print(f"  Store: {t.store_name or 'N/A'}")
            print(f"  Status: {t.status}")
            print(f"  Created: {t.created_at}")
            print()
        
        print("=" * 80)


if __name__ == "__main__":
    view_db()

