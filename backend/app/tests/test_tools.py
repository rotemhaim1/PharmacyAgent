from __future__ import annotations

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import InventoryItem, Medication, User
from app.db.session import Base
from app.tools.tool_impl import (
    check_inventory,
    check_prescription_requirement,
    create_prescription_request,
    get_medication_by_name,
    get_user_by_phone,
    reserve_inventory,
)


def _make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return SessionLocal()


def test_get_medication_by_name_exact_match_en():
    db = _make_db()
    m = Medication(
        name="Paracetamol",
        name_he="פרצטמול",
        active_ingredients_json=json.dumps(["acetaminophen"]),
        form="tablet",
        strength="500 mg",
        manufacturer="Synthetic",
        otc_or_rx="otc",
        label_instructions="Label instructions: test",
        warnings="Warnings: test",
    )
    db.add(m)
    db.commit()

    out = get_medication_by_name(db, {"query": "paracetamol"})
    assert out["found"] is True
    assert out["medication"]["id"] == m.id


def test_get_medication_by_name_alias_dexamol():
    db = _make_db()
    m = Medication(
        name="Paracetamol",
        name_he="פרצטמול",
        active_ingredients_json=json.dumps(["acetaminophen"]),
        form="tablet",
        strength="500 mg",
        manufacturer="Synthetic",
        otc_or_rx="otc",
        label_instructions="Label instructions: test",
        warnings="Warnings: test",
    )
    db.add(m)
    db.commit()

    out = get_medication_by_name(db, {"query": "dexamol"})
    assert out["found"] is True
    assert out["medication"]["id"] == m.id


def test_get_medication_by_name_ambiguous():
    db = _make_db()
    db.add_all(
        [
            Medication(
                name="Omeprazole",
                name_he="אומפרזול",
                active_ingredients_json="[]",
                form="capsule",
                strength="20 mg",
                manufacturer="Synthetic",
                otc_or_rx="otc",
                label_instructions="x",
                warnings="x",
            ),
            Medication(
                name="Omeprazole XR",
                name_he="אומפרזול XR",
                active_ingredients_json="[]",
                form="capsule",
                strength="20 mg",
                manufacturer="Synthetic",
                otc_or_rx="otc",
                label_instructions="x",
                warnings="x",
            ),
        ]
    )
    db.commit()

    # Use a partial query to trigger ambiguity (exact match should resolve deterministically).
    out = get_medication_by_name(db, {"query": "omepraz"})
    assert out["found"] is False
    assert out["error"] == "ambiguous"
    assert len(out["alternatives"]) >= 2


def test_check_inventory_statuses():
    db = _make_db()
    med = Medication(
        name="Ibuprofen",
        name_he="איבופרופן",
        active_ingredients_json="[]",
        form="tablet",
        strength="200 mg",
        manufacturer="Synthetic",
        otc_or_rx="otc",
        label_instructions="x",
        warnings="x",
    )
    db.add(med)
    db.flush()
    db.add_all(
        [
            InventoryItem(medication_id=med.id, store_id="S1", store_name="A", quantity=0),
            InventoryItem(medication_id=med.id, store_id="S2", store_name="B", quantity=2),
            InventoryItem(medication_id=med.id, store_id="S3", store_name="C", quantity=10),
        ]
    )
    db.commit()

    out = check_inventory(db, {"medication_id": med.id})
    statuses = {r["store_name"]: r["status"] for r in out["results"]}
    assert statuses["A"] == "out"
    assert statuses["B"] == "low"
    assert statuses["C"] == "in_stock"


def test_check_prescription_requirement():
    db = _make_db()
    med = Medication(
        name="Metformin",
        name_he="מטפורמין",
        active_ingredients_json="[]",
        form="tablet",
        strength="500 mg",
        manufacturer="Synthetic",
        otc_or_rx="rx",
        label_instructions="x",
        warnings="x",
    )
    db.add(med)
    db.commit()

    out = check_prescription_requirement(db, {"medication_id": med.id})
    assert out["requires_prescription"] is True


def test_get_user_by_phone_and_create_request_and_reserve():
    db = _make_db()
    user = User(full_name="Test User", phone="+972501234567", preferred_language="en", loyalty_id=None)
    med = Medication(
        name="Amoxicillin",
        name_he="אמוקסיצילין",
        active_ingredients_json="[]",
        form="capsule",
        strength="500 mg",
        manufacturer="Synthetic",
        otc_or_rx="rx",
        label_instructions="x",
        warnings="x",
    )
    db.add_all([user, med])
    db.flush()
    inv = InventoryItem(medication_id=med.id, store_id="S1", store_name="Tel Aviv - Dizengoff", quantity=5)
    db.add(inv)
    db.commit()

    u = get_user_by_phone(db, {"phone": " +97250-123-4567 "})
    assert u["found"] is True

    req = create_prescription_request(db, {"user_id": user.id, "medication_id": med.id, "pickup_store": "Tel Aviv - Dizengoff"})
    assert req["status"] == "created"
    assert req["request_id"]

    res1 = reserve_inventory(db, {"medication_id": med.id, "store_name": "Tel Aviv - Dizengoff", "quantity": 2})
    assert res1["reserved"] is True
    assert res1["reservation_id"]

    # Stock should be decremented
    inv2 = db.query(InventoryItem).filter(InventoryItem.id == inv.id).first()
    assert inv2 is not None
    assert inv2.quantity == 3


