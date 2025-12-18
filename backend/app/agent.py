from __future__ import annotations

import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional

from openai import OpenAI
from sqlalchemy.orm import Session

from app.policy import build_system_prompt
from app.tools.registry import OPENAI_TOOLS, TOOL_NAME_TO_FN


def _load_api_key() -> Optional[str]:
    # Preferred: env var (Docker/prod). Optional fallback: local api-key.txt for convenience.
    key = os.getenv("OPENAI_API_KEY")
    # If the env var is present (even empty), respect it and do not fall back to file.
    if key is not None:
        key = key.strip()
        return key or None
    repo_root = Path(__file__).resolve().parents[2]
    candidate = repo_root / "api-key.txt"
    if candidate.exists():
        return candidate.read_text(encoding="utf-8").strip() or None
    return None


async def stream_chat(
    *, db: Optional[Session], messages: List[Dict[str, Any]], locale_hint: Optional[str], user_id: str
) -> AsyncIterator[bytes]:
    """
    Stateless agent loop: client sends full conversation each turn.
    Streams assistant tokens via SSE; executes tools when model requests them.
    user_id: Authenticated user ID (required for reservations).
    """
    api_key = _load_api_key()
    if not api_key:
        yield _sse("error", {"type": "error", "message": "Missing OPENAI_API_KEY (set env var)."})
        yield _sse("done", {"type": "done"})
        return

    model = os.getenv("OPENAI_MODEL", "gpt-5")
    client = OpenAI(api_key=api_key)

    working_messages: List[Dict[str, Any]] = [{"role": "system", "content": build_system_prompt(locale_hint)}]
    working_messages.extend(messages)

    try:
        max_tool_rounds = 8
        for _round in range(max_tool_rounds):
            tool_calls_acc: Dict[int, Dict[str, Any]] = {}

            # Run one streamed model step. If it ends with tool_calls, execute and continue.
            stream = client.chat.completions.create(
                model=model,
                messages=working_messages,
                tools=OPENAI_TOOLS,
                tool_choice="auto",
                stream=True,
            )

            finish_reason: Optional[str] = None
            for chunk in stream:
                choice = chunk.choices[0]
                finish_reason = choice.finish_reason or finish_reason
                delta = choice.delta

                if getattr(delta, "content", None):
                    yield _sse("delta", {"type": "delta", "text": delta.content})

                # Accumulate tool calls (streamed).
                if getattr(delta, "tool_calls", None):
                    for tc in delta.tool_calls:
                        idx = tc.index
                        acc = tool_calls_acc.setdefault(
                            idx, {"id": None, "type": "function", "function": {"name": "", "arguments": ""}}
                        )
                        if getattr(tc, "id", None):
                            acc["id"] = tc.id
                        if getattr(tc, "function", None):
                            if getattr(tc.function, "name", None):
                                acc["function"]["name"] = tc.function.name
                            if getattr(tc.function, "arguments", None):
                                acc["function"]["arguments"] += tc.function.arguments

                await asyncio.sleep(0)

            # No tools requested: done.
            if finish_reason != "tool_calls":
                break

            tool_calls = [tool_calls_acc[i] for i in sorted(tool_calls_acc.keys())]
            if not tool_calls:
                yield _sse("error", {"type": "error", "message": "Model requested tool_calls but none were provided."})
                break

            # Ensure required fields for OpenAI tool-calling protocol.
            for i, tc in enumerate(tool_calls):
                tc.setdefault("type", "function")
                if not tc.get("id"):
                    tc["id"] = "call_" + uuid.uuid4().hex
                if "function" not in tc:
                    tc["function"] = {"name": "", "arguments": "{}"}
                tc["function"].setdefault("name", "")
                tc["function"].setdefault("arguments", "{}")

            # Append assistant tool call message as required by chat tool protocol.
            working_messages.append({"role": "assistant", "tool_calls": tool_calls})

            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                tool_call_id = tc["id"]
                yield _sse("tool_status", {"type": "tool_status", "status": "running", "tool": tool_name})

                fn = TOOL_NAME_TO_FN.get(tool_name)
                if not fn:
                    result = {"error": "unknown_tool", "tool": tool_name}
                else:
                    try:
                        args = json.loads(tc["function"]["arguments"] or "{}")
                    except Exception:
                        args = {}
                        result = {"error": "invalid_tool_arguments_json"}
                    else:
                        if db is None:
                            result = {"error": "db_unavailable"}
                        else:
                            # Pass user_id to tools that need it
                            if tool_name == "reserve_inventory":
                                from app.tools.tool_impl import reserve_inventory
                                result = reserve_inventory(db, args, user_id=user_id)
                            elif tool_name == "get_current_user":
                                from app.tools.tool_impl import get_current_user
                                result = get_current_user(db, args, user_id=user_id)
                            else:
                                result = fn(db, args)

                yield _sse("tool_status", {"type": "tool_status", "status": "done", "tool": tool_name})
                working_messages.append(
                    {"role": "tool", "tool_call_id": tool_call_id, "content": json.dumps(result, ensure_ascii=False)}
                )
    except Exception as e:
        # Always surface errors to the UI; otherwise the browser looks “stuck”.
        yield _sse("error", {"type": "error", "message": f"Agent error: {type(e).__name__}: {e}"})
    finally:
        yield _sse("done", {"type": "done"})


def _sse(event: str, data: Dict[str, Any]) -> bytes:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


