from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.agent import stream_chat
from app.db.seed import init_db, seed_if_empty
from app.db.session import SessionLocal


class ChatMessage(BaseModel):
    role: str = Field(..., examples=["user", "assistant"])
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    localeHint: Optional[str] = None


def create_app() -> FastAPI:
    app = FastAPI(title="Pharmacy Agent API", version="0.1.0")

    cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in cors_origins] if cors_origins != ["*"] else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> Dict[str, Any]:
        return {"ok": True}

    @app.on_event("startup")
    async def _startup() -> None:
        init_db()
        seed_if_empty()

    @app.post("/chat/stream")
    async def chat_stream(req: ChatRequest) -> StreamingResponse:
        async def _gen():
            with SessionLocal() as db:
                async for chunk in stream_chat(
                    db=db, messages=[m.model_dump() for m in req.messages], locale_hint=req.localeHint
                ):
                    yield chunk

        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
        return StreamingResponse(_gen(), media_type="text/event-stream", headers=headers)

    # Optional: serve built frontend (Docker/prod). This mount is added after API routes so /health and /chat/stream still work.
    dist_dir = os.getenv("FRONTEND_DIST_DIR")
    if dist_dir:
        dist_path = Path(dist_dir)
    else:
        dist_path = Path(__file__).resolve().parents[2] / "frontend" / "dist"

    if dist_path.exists():
        app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="frontend")

    return app


app = create_app()


