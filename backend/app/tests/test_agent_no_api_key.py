from __future__ import annotations

import asyncio

from app.agent import stream_chat


def test_agent_stream_errors_without_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")

    async def _collect():
        # db is unused when key is missing; pass None and rely on early return
        chunks = []
        async for c in stream_chat(db=None, messages=[{"role": "user", "content": "hi"}], locale_hint="en", user_id="test-user-id"):
            chunks.append(c.decode("utf-8"))
        return "".join(chunks)

    out = asyncio.run(_collect())
    assert "Missing OPENAI_API_KEY" in out


