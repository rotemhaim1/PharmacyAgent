#!/usr/bin/env python3
"""
Delete records from the database.
Usage: python delete_db_records.py
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.db.models import User, Medication, InventoryItem, Prescription, Ticket
from sqlalchemy import select


def show_menu():
    print("\n" + "=" * 60)
    print("DATABASE DELETION MENU")
    print("=" * 60)
    print("1. Delete all tickets/reservations")
    print("2. Delete a specific ticket by ID")
    print("3. Delete all tickets for a specific user")
    print("4. Delete a specific user (and their tickets/prescriptions)")
    print("5. Delete all prescriptions")
    print("6. List all users")
    print("7. List all tickets")
    print("0. Exit")
    print("=" * 60)


def delete_all_tickets():
    with SessionLocal() as db:
        tickets = db.execute(select(Ticket)).scalars().all()
        count = len(tickets)
        if count == 0:
            print("No tickets to delete.")
            return
        
        response = input(f"Delete {count} ticket(s)? (yes/no): ")
        if response.lower() == "yes":
            for t in tickets:
                db.delete(t)
            db.commit()
            print(f"✓ Deleted {count} ticket(s).")


def delete_ticket_by_id():
    ticket_id = input("Enter ticket ID: ").strip()
    with SessionLocal() as db:
        ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalars().first()
        if not ticket:
            print(f"Ticket {ticket_id} not found.")
            return
        
        print(f"Ticket: {ticket.type} - {ticket.status} (Created: {ticket.created_at})")
        response = input("Delete this ticket? (yes/no): ")
        if response.lower() == "yes":
            db.delete(ticket)
            db.commit()
            print("✓ Ticket deleted.")


def delete_user_tickets():
    user_id = input("Enter user ID: ").strip()
    with SessionLocal() as db:
        user = db.execute(select(User).where(User.id == user_id)).scalars().first()
        if not user:
            print(f"User {user_id} not found.")
            return
        
        tickets = db.execute(select(Ticket).where(Ticket.user_id == user_id)).scalars().all()
        count = len(tickets)
        
        print(f"User: {user.full_name} ({user.phone})")
        print(f"Tickets: {count}")
        
        if count == 0:
            print("No tickets to delete.")
            return
        
        response = input(f"Delete {count} ticket(s) for this user? (yes/no): ")
        if response.lower() == "yes":
            for t in tickets:
                db.delete(t)
            db.commit()
            print(f"✓ Deleted {count} ticket(s).")


def delete_user():
    user_id = input("Enter user ID: ").strip()
    with SessionLocal() as db:
        user = db.execute(select(User).where(User.id == user_id)).scalars().first()
        if not user:
            print(f"User {user_id} not found.")
            return
        
        # Count related records
        tickets = db.execute(select(Ticket).where(Ticket.user_id == user_id)).scalars().all()
        prescriptions = db.execute(select(Prescription).where(Prescription.user_id == user_id)).scalars().all()
        
        print(f"User: {user.full_name} ({user.phone})")
        print(f"  - Tickets: {len(tickets)}")
        print(f"  - Prescriptions: {len(prescriptions)}")
        
        response = input("Delete this user and all related records? (yes/no): ")
        if response.lower() == "yes":
            # Delete related records first
            for t in tickets:
                db.delete(t)
            for p in prescriptions:
                db.delete(p)
            db.delete(user)
            db.commit()
            print("✓ User and related records deleted.")


def delete_all_prescriptions():
    with SessionLocal() as db:
        prescriptions = db.execute(select(Prescription)).scalars().all()
        count = len(prescriptions)
        if count == 0:
            print("No prescriptions to delete.")
            return
        
        response = input(f"Delete {count} prescription(s)? (yes/no): ")
        if response.lower() == "yes":
            for p in prescriptions:
                db.delete(p)
            db.commit()
            print(f"✓ Deleted {count} prescription(s).")


def list_users():
    with SessionLocal() as db:
        users = db.execute(select(User)).scalars().all()
        print(f"\nUSERS ({len(users)} total):")
        print("-" * 60)
        for u in users:
            print(f"ID: {u.id}")
            print(f"Name: {u.full_name}")
            print(f"Phone: {u.phone}")
            print(f"Language: {u.preferred_language}")
            print()


def list_tickets():
    with SessionLocal() as db:
        tickets = db.execute(select(Ticket)).scalars().all()
        print(f"\nTICKETS ({len(tickets)} total):")
        print("-" * 60)
        for t in tickets:
            user_name = "N/A"
            if t.user_id:
                user = db.execute(select(User).where(User.id == t.user_id)).scalars().first()
                user_name = user.full_name if user else "Unknown"
            
            print(f"ID: {t.id}")
            print(f"Type: {t.type}")
            print(f"User: {user_name}")
            print(f"Status: {t.status}")
            print(f"Created: {t.created_at}")
            print()


def main():
    while True:
        show_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            delete_all_tickets()
        elif choice == "2":
            delete_ticket_by_id()
        elif choice == "3":
            delete_user_tickets()
        elif choice == "4":
            delete_user()
        elif choice == "5":
            delete_all_prescriptions()
        elif choice == "6":
            list_users()
        elif choice == "7":
            list_tickets()
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()

