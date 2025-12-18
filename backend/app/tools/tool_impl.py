from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import InventoryItem, Medication, Ticket, User


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).lower()


def _inventory_status(qty: int) -> str:
    if qty <= 0:
        return "out"
    if qty < 5:
        return "low"
    return "in_stock"


def get_medication_by_name(db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
    query = (args.get("query") or "").strip()
    if not query:
        return {"found": False, "medication": None, "alternatives": [], "error": "empty_query"}

    qn = _normalize(query)
    # Simple brand-name aliases (helps with common local names).
    alias_map = {
        "dexamol": "paracetamol",
        "דקסמול": "פרצטמול",
    }
    qn = alias_map.get(qn, qn)

    # Prefer exact case-insensitive match (English/Hebrew).
    exact_stmt = select(Medication).where(
        (func.lower(Medication.name) == qn) | (func.lower(Medication.name_he) == qn)
    )
    exact = db.execute(exact_stmt).scalars().all()
    if len(exact) == 1:
        return {"found": True, "medication": _med_to_dict(exact[0]), "alternatives": []}

    # Fallback: substring match.
    like = f"%{qn}%"
    like_stmt = (
        select(Medication)
        .where((func.lower(Medication.name).like(like)) | (func.lower(Medication.name_he).like(like)))
        .limit(10)
    )
    matches = db.execute(like_stmt).scalars().all()
    if not matches:
        return {"found": False, "medication": None, "alternatives": [], "error": "not_found"}
    if len(matches) > 1:
        return {
            "found": False,
            "medication": None,
            "alternatives": [m.name for m in matches],
            "error": "ambiguous",
        }
    return {"found": True, "medication": _med_to_dict(matches[0]), "alternatives": []}


def check_inventory(db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
    medication_id = (args.get("medication_id") or "").strip()
    if not medication_id:
        return {"results": [], "error": "missing_medication_id"}

    store_name = (args.get("store_name") or "").strip()
    stmt = select(InventoryItem).where(InventoryItem.medication_id == medication_id)
    if store_name:
        stmt = stmt.where(func.lower(InventoryItem.store_name) == _normalize(store_name))

    items = db.execute(stmt).scalars().all()
    if not items and store_name:
        return {"results": [], "error": "unknown_store_or_no_record"}

    results = [
        {"store_name": it.store_name, "quantity": it.quantity, "status": _inventory_status(it.quantity)}
        for it in items
    ]
    return {"results": results}


def check_prescription_requirement(db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
    medication_id = (args.get("medication_id") or "").strip()
    if not medication_id:
        return {"requires_prescription": None, "notes": "", "error": "missing_medication_id"}

    med = db.get(Medication, medication_id)
    if not med:
        return {"requires_prescription": None, "notes": "", "error": "not_found"}

    requires = med.otc_or_rx == "rx"
    notes = "Prescription required (Rx)." if requires else "Over-the-counter (OTC)."
    return {"requires_prescription": requires, "notes": notes}


def get_user_by_phone(db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
    phone = (args.get("phone") or "").strip()
    if not phone or len(phone) < 7:
        return {"found": False, "user": None, "error": "invalid_phone"}

    # Normalize: keep + and digits only.
    norm = re.sub(r"[^0-9+]", "", phone)
    stmt = select(User).where(User.phone == norm)
    user = db.execute(stmt).scalars().first()
    if not user:
        return {"found": False, "user": None}
    return {"found": True, "user": {"id": user.id, "full_name": user.full_name, "preferred_language": user.preferred_language}}


def create_prescription_request(db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
    user_id = (args.get("user_id") or "").strip()
    medication_id = (args.get("medication_id") or "").strip()
    pickup_store = (args.get("pickup_store") or "").strip() or None

    if not user_id or not medication_id:
        return {"request_id": None, "status": "error", "error": "missing_required_fields"}

    if not db.get(User, user_id):
        return {"request_id": None, "status": "error", "error": "unknown_user"}
    if not db.get(Medication, medication_id):
        return {"request_id": None, "status": "error", "error": "unknown_medication"}

    t = Ticket(
        type="prescription_request",
        user_id=user_id,
        medication_id=medication_id,
        store_name=pickup_store,
        payload_json=json.dumps({"pickup_store": pickup_store}, ensure_ascii=False),
        status="created",
    )
    db.add(t)
    db.commit()
    return {"request_id": t.id, "status": "created"}


def reserve_inventory(db: Session, args: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
    medication_id = (args.get("medication_id") or "").strip()
    store_name = (args.get("store_name") or "").strip()
    quantity = int(args.get("quantity") or 0)

    if not medication_id or not store_name or quantity <= 0:
        return {"reserved": False, "reason": "missing_required_fields"}

    if not user_id:
        return {"reserved": False, "reason": "authentication_required"}

    stmt = select(InventoryItem).where(
        (InventoryItem.medication_id == medication_id)
        & (func.lower(InventoryItem.store_name) == _normalize(store_name))
    )
    item = db.execute(stmt).scalars().first()
    if not item:
        return {"reserved": False, "reason": "store_or_item_not_found"}
    if item.quantity < quantity:
        return {"reserved": False, "reason": "insufficient_stock"}

    item.quantity -= quantity
    t = Ticket(
        type="inventory_reservation",
        user_id=user_id,
        medication_id=medication_id,
        store_name=item.store_name,
        payload_json=json.dumps({"quantity": quantity}, ensure_ascii=False),
        status="created",
    )
    db.add(t)
    db.commit()
    return {"reserved": True, "reservation_id": t.id}


def _med_to_dict(m: Medication) -> Dict[str, Any]:
    try:
        ingredients = json.loads(m.active_ingredients_json or "[]")
    except Exception:
        ingredients = []
    return {
        "id": m.id,
        "name": m.name,
        "name_he": m.name_he,
        "active_ingredients": ingredients,
        "form": m.form,
        "strength": m.strength,
        "manufacturer": m.manufacturer,
        "otc_or_rx": m.otc_or_rx,
        "label_instructions": m.label_instructions,
        "warnings": m.warnings,
    }


