from __future__ import annotations

import datetime as dt
import uuid
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
    loyalty_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    prescriptions: Mapped[List["Prescription"]] = relationship(back_populates="user")


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    name_he: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    active_ingredients_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    form: Mapped[str] = mapped_column(String(64), nullable=False)
    strength: Mapped[str] = mapped_column(String(64), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(200), nullable=False)
    otc_or_rx: Mapped[str] = mapped_column(String(8), nullable=False)  # "otc" | "rx"
    label_instructions: Mapped[str] = mapped_column(Text, nullable=False)
    warnings: Mapped[str] = mapped_column(Text, nullable=False)

    inventory_items: Mapped[List["InventoryItem"]] = relationship(back_populates="medication")
    prescriptions: Mapped[List["Prescription"]] = relationship(back_populates="medication")


class InventoryItem(Base):
    __tablename__ = "inventory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    medication_id: Mapped[str] = mapped_column(String(36), ForeignKey("medications.id"), nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(String(36), nullable=False)
    store_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_updated: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: dt.datetime.now(dt.timezone.utc)
    )

    medication: Mapped["Medication"] = relationship(back_populates="inventory_items")


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    medication_id: Mapped[str] = mapped_column(String(36), ForeignKey("medications.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")  # active|requested|filled|cancelled
    refills_left: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expires_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="prescriptions")
    medication: Mapped["Medication"] = relationship(back_populates="prescriptions")


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    type: Mapped[str] = mapped_column(String(64), nullable=False)  # prescription_request|inventory_reservation|customer_service
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    medication_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("medications.id"), nullable=True, index=True)
    store_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: dt.datetime.now(dt.timezone.utc)
    )


