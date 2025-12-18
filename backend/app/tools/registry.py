from __future__ import annotations

from typing import Any, Callable, Dict, List

from sqlalchemy.orm import Session

from app.tools.tool_impl import (
    check_inventory,
    check_prescription_requirement,
    create_prescription_request,
    get_current_user,
    get_medication_by_name,
    get_user_by_phone,
    reserve_inventory,
)


ToolFn = Callable[[Session, Dict[str, Any]], Dict[str, Any]]


TOOL_NAME_TO_FN: Dict[str, ToolFn] = {
    "get_medication_by_name": get_medication_by_name,
    "check_inventory": check_inventory,
    "check_prescription_requirement": check_prescription_requirement,
    "get_user_by_phone": get_user_by_phone,
    "get_current_user": get_current_user,
    "create_prescription_request": create_prescription_request,
    "reserve_inventory": reserve_inventory,
}


OPENAI_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_medication_by_name",
            "description": "Resolve a user-provided medication name (English/Hebrew) to a medication record in the catalog.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Medication name query (EN/HE)."}},
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Check stock availability for a medication, optionally for a specific store.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medication_id": {"type": "string"},
                    "store_name": {"type": "string", "description": "Optional store name."},
                },
                "required": ["medication_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_prescription_requirement",
            "description": "Return whether a medication requires a prescription (Rx) or is OTC.",
            "parameters": {
                "type": "object",
                "properties": {"medication_id": {"type": "string"}},
                "required": ["medication_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_by_phone",
            "description": "Look up a user by phone number to continue prescription workflows.",
            "parameters": {
                "type": "object",
                "properties": {"phone": {"type": "string"}},
                "required": ["phone"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_user",
            "description": "Get information about the currently authenticated user. Use this for prescription requests instead of asking for phone number.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_prescription_request",
            "description": "Create a prescription fulfillment/request ticket for a user and medication (no medical advice).",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "medication_id": {"type": "string"},
                    "pickup_store": {"type": "string"},
                },
                "required": ["user_id", "medication_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reserve_inventory",
            "description": "Reserve inventory for pickup at a specific store. Decrements stock if successful.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medication_id": {"type": "string"},
                    "store_name": {"type": "string"},
                    "quantity": {"type": "integer", "minimum": 1},
                },
                "required": ["medication_id", "store_name", "quantity"],
                "additionalProperties": False,
            },
        },
    },
]


