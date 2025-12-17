from __future__ import annotations

import datetime as dt
import json
import random
import uuid
from typing import List

from sqlalchemy import select

from app.db.models import InventoryItem, Medication, Prescription, Ticket, User
from app.db.session import Base, SessionLocal, engine


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed_if_empty() -> None:
    with SessionLocal() as db:
        existing = db.execute(select(User.id).limit(1)).first()
        if existing:
            return

        random.seed(1337)

        users = [
            User(full_name="Rotem Cohen", phone="+972501000001", preferred_language="he", loyalty_id="L-1001"),
            User(full_name="Noam Levi", phone="+972501000002", preferred_language="he", loyalty_id="L-1002"),
            User(full_name="Yael Mizrahi", phone="+972501000003", preferred_language="he", loyalty_id="L-1003"),
            User(full_name="Daniel Katz", phone="+972501000004", preferred_language="en", loyalty_id="L-1004"),
            User(full_name="Maya Rosen", phone="+972501000005", preferred_language="en", loyalty_id="L-1005"),
            User(full_name="Amit Shani", phone="+972501000006", preferred_language="he", loyalty_id="L-1006"),
            User(full_name="Tamar Azulay", phone="+972501000007", preferred_language="he", loyalty_id="L-1007"),
            User(full_name="Eitan Peretz", phone="+972501000008", preferred_language="en", loyalty_id="L-1008"),
            User(full_name="Lior Bar", phone="+972501000009", preferred_language="en", loyalty_id="L-1009"),
            User(full_name="Shira Gold", phone="+972501000010", preferred_language="he", loyalty_id="L-1010"),
        ]
        db.add_all(users)

        meds = [
            Medication(
                name="Paracetamol",
                name_he="פרצטמול",
                active_ingredients_json=json.dumps(["acetaminophen"], ensure_ascii=False),
                form="tablet",
                strength="500 mg",
                manufacturer="Synthetic Pharma",
                otc_or_rx="otc",
                label_instructions=(
                    "Label instructions: Take as directed on the package label. Do not exceed the maximum daily dose "
                    "stated on the label."
                ),
                warnings="Warnings: Contains acetaminophen. Overdose may cause severe liver damage. Keep out of reach of children.",
            ),
            Medication(
                name="Ibuprofen",
                name_he="איבופרופן",
                active_ingredients_json=json.dumps(["ibuprofen"], ensure_ascii=False),
                form="tablet",
                strength="200 mg",
                manufacturer="Synthetic Pharma",
                otc_or_rx="otc",
                label_instructions="Label instructions: Take with food or milk if stomach upset occurs. Use the lowest effective dose per label.",
                warnings="Warnings: NSAID. May increase risk of stomach bleeding. Do not use if allergic to NSAIDs.",
            ),
            Medication(
                name="Amoxicillin",
                name_he="אמוקסיצילין",
                active_ingredients_json=json.dumps(["amoxicillin"], ensure_ascii=False),
                form="capsule",
                strength="500 mg",
                manufacturer="Synthetic Pharma",
                otc_or_rx="rx",
                label_instructions="Label instructions: Use only as prescribed. Complete the full course as prescribed.",
                warnings="Warnings: Antibiotic. Allergic reactions may occur. Seek urgent care for signs of a severe allergy.",
            ),
            Medication(
                name="Metformin",
                name_he="מטפורמין",
                active_ingredients_json=json.dumps(["metformin"], ensure_ascii=False),
                form="tablet",
                strength="500 mg",
                manufacturer="Synthetic Pharma",
                otc_or_rx="rx",
                label_instructions="Label instructions: Take only as prescribed. Follow the dosing schedule provided by the prescriber/pharmacist.",
                warnings="Warnings: Prescription medication. Follow professional instructions. Contact a healthcare professional with questions.",
            ),
            Medication(
                name="Omeprazole",
                name_he="אומפרזול",
                active_ingredients_json=json.dumps(["omeprazole"], ensure_ascii=False),
                form="capsule",
                strength="20 mg",
                manufacturer="Synthetic Pharma",
                otc_or_rx="otc",
                label_instructions="Label instructions: Take as directed on the package label. Swallow whole; do not crush or chew.",
                warnings="Warnings: If symptoms persist, consult a healthcare professional. Keep out of reach of children.",
            ),
        ]
        db.add_all(meds)
        db.flush()

        stores = [
            ("S-TA", "Tel Aviv - Dizengoff"),
            ("S-JLM", "Jerusalem - King George"),
            ("S-HFA", "Haifa - Carmel"),
        ]

        inv_items: List[InventoryItem] = []
        for med in meds:
            for store_id, store_name in stores:
                qty = random.choice([0, 2, 5, 12, 30])
                inv_items.append(
                    InventoryItem(
                        medication_id=med.id,
                        store_id=store_id,
                        store_name=store_name,
                        quantity=qty,
                        last_updated=_now(),
                    )
                )
        db.add_all(inv_items)

        # A few example prescriptions for Rx meds
        rx_meds = [m for m in meds if m.otc_or_rx == "rx"]
        presc = [
            Prescription(user_id=users[0].id, medication_id=rx_meds[0].id, status="active", refills_left=1, expires_at=_now() + dt.timedelta(days=60)),
            Prescription(user_id=users[3].id, medication_id=rx_meds[1].id, status="active", refills_left=2, expires_at=_now() + dt.timedelta(days=90)),
        ]
        db.add_all(presc)

        # Example ticket to show the concept
        db.add(
            Ticket(
                type="customer_service",
                user_id=users[1].id,
                payload_json=json.dumps({"topic": "hours", "note": "Store hours question"}, ensure_ascii=False),
                status="created",
            )
        )

        db.commit()


def main() -> None:
    init_db()
    seed_if_empty()
    print("DB ready (created tables; seeded if empty).")


if __name__ == "__main__":
    main()


