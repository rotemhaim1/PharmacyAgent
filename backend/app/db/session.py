from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def _default_sqlite_path() -> Path:
    # Keep DB inside backend/ by default.
    backend_dir = Path(__file__).resolve().parents[2]
    return backend_dir / "app.db"


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    return f"sqlite:///{_default_sqlite_path().as_posix()}"


engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False} if get_database_url().startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


