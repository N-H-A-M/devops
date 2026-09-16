import sys
from pathlib import Path

# Fix module imports regardless of where script is executed from
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import asyncio
from typing import Any, List, Dict
from app.db import init_db_pool, close_db_pool, _get_pool

async def run_query(query: str, *args) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return rows as dictionaries."""
    pool = _get_pool()
    if pool is None:
        await init_db_pool()
        pool = _get_pool()

    async with pool.acquire() as conn:
        records = await conn.fetch(query, *args)
        return [dict(record) for record in records]

async def execute_cmd(query: str, *args) -> str:
    """Execute INSERT, UPDATE, or DELETE commands."""
    pool = _get_pool()
    if pool is None:
        await init_db_pool()
        pool = _get_pool()

    async with pool.acquire() as conn:
        return await conn.execute(query, *args)