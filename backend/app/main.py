from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.agent import stream_chat
from app.auth import create_access_token, get_user_id_from_token, hash_password, verify_password
from app.db.models import User
from app.db.seed import init_db, seed_if_empty
from app.db.session import SessionLocal


class ChatMessage(BaseModel):
    role: str = Field(..., examples=["user", "assistant"])
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    localeHint: Optional[str] = None


class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=1, max_length=32)
    password: str = Field(..., min_length=6)
    preferred_language: str = Field(default="en", pattern="^(en|he)$")


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=1, max_length=32)
    password: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    full_name: str
    preferred_language: str


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

    @app.post("/auth/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
    async def signup(req: SignupRequest) -> AuthResponse:
        """Create a new user account."""
        try:
            with SessionLocal() as db:
                # Normalize phone: strip whitespace
                normalized_phone = req.phone.strip()
                
                # Check if phone already exists
                existing = db.execute(select(User).where(User.phone == normalized_phone)).scalars().first()
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Phone number already registered",
                    )

                # Create new user
                password_hash = hash_password(req.password)
                try:
                    user = User(
                        full_name=req.full_name.strip(),
                        phone=normalized_phone,
                        password_hash=password_hash,
                        preferred_language=req.preferred_language,
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                except Exception as e:
                    db.rollback()
                    import traceback
                    error_detail = f"Failed to create user: {str(e)}\n{traceback.format_exc()}"
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_detail,
                    )

                # Generate JWT token
                try:
                    access_token = create_access_token(data={"sub": user.id})
                except Exception as e:
                    import traceback
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to generate token: {str(e)}\n{traceback.format_exc()}",
                    )

                return AuthResponse(
                    access_token=access_token,
                    user_id=user.id,
                    full_name=user.full_name,
                    preferred_language=user.preferred_language,
                )
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error during signup: {str(e)}\n{traceback.format_exc()}",
            )

    @app.post("/auth/login", response_model=AuthResponse)
    async def login(req: LoginRequest) -> AuthResponse:
        """Authenticate user and return JWT token."""
        with SessionLocal() as db:
            user = db.execute(select(User).where(User.phone == req.phone)).scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid phone or password",
                )

            if not verify_password(req.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid phone or password",
                )

            # Generate JWT token
            access_token = create_access_token(data={"sub": user.id})

            return AuthResponse(
                access_token=access_token,
                user_id=user.id,
                full_name=user.full_name,
                preferred_language=user.preferred_language,
            )

    @app.on_event("startup")
    async def _startup() -> None:
        init_db()
        seed_if_empty()

    @app.post("/chat/stream")
    async def chat_stream(
        req: ChatRequest, authorization: Optional[str] = Header(None, alias="Authorization")
    ) -> StreamingResponse:
        # Extract token from Authorization header
        token: Optional[str] = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization[7:]

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = get_user_id_from_token(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        async def _gen():
            with SessionLocal() as db:
                async for chunk in stream_chat(
                    db=db,
                    messages=[m.model_dump() for m in req.messages],
                    locale_hint=req.localeHint,
                    user_id=user_id,
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


