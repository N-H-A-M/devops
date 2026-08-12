# app/db.py
import asyncio
import json
import logging
import os
from typing import Optional
import asyncpg
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from app.models import CreditCard

load_dotenv()
logger = logging.getLogger("card_comparison")
_pool: Optional[asyncpg.Pool] = None


def _get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Copy .env.example to .env and fill it in."
        )
    return url


# 1. Get the URL and create the engine
engine = create_engine(_get_database_url())
# 2. Create the Base (globally importable)
Base = declarative_base()

async def _register_jsonb_codec(conn: asyncpg.Connection) -> None:
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


async def init_db_pool() -> None:
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=_get_database_url(),
        min_size=1,
        max_size=10,
        command_timeout=5,
        init=_register_jsonb_codec,
    )
    logger.info("db_pool_started", extra={"min_size": 1, "max_size": 10})


async def close_db_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        logger.info("db_pool_closed")
        _pool = None


def _get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool not initialized -- did startup run?")
    return _pool


async def check_db_alive(timeout_seconds: float = 2.0) -> bool:
    try:
        pool = _get_pool()
        async with pool.acquire() as conn:
            await asyncio.wait_for(conn.execute("SELECT 1"), timeout=timeout_seconds)
        return True
    except Exception as e:
        logger.warning("db_health_check_failed", extra={"error": str(e)})
        return False

async def fetch_all_cards():
    """Fetch all credit cards using raw asyncpg query."""
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")

    async with _pool.acquire() as conn:
        records = await conn.fetch("SELECT * FROM credit_cards;")
        return [dict(r) for r in records]