"""Lightweight Postgres helper for Phase 1 (independent).

Uses asyncpg and expects DATABASE_URL env var in standard libpq form, e.g.:
  postgres://user:password@host:port/dbname

No pooling sophistication—simple singleton connection for workshop clarity.
"""
from __future__ import annotations

import asyncio
import os
from typing import Optional

import asyncpg
from dotenv import load_dotenv

load_dotenv()

_conn: Optional[asyncpg.Connection] = None

async def get_conn() -> asyncpg.Connection:
    global _conn
    if _conn and not _conn.is_closed():
        return _conn
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set for Phase 1")
    _conn = await asyncpg.connect(url)
    return _conn

async def init_schema():
    conn = await get_conn()
    # Separate tables with phase-specific prefix to avoid collisions
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS phase1_documents (
            id SERIAL PRIMARY KEY,
            title TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS phase1_chunks (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES phase1_documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding DOUBLE PRECISION[] NOT NULL,
            UNIQUE(document_id, chunk_index)
        );
        """
    )

async def reset_schema():
    """Dangerous: drops and recreates phase1 tables (for workshop resets)."""
    conn = await get_conn()
    await conn.execute(
        """
        DROP TABLE IF EXISTS phase1_chunks;
        DROP TABLE IF EXISTS phase1_documents;
        """
    )
    await init_schema()

if __name__ == "__main__":
    asyncio.run(init_schema())
