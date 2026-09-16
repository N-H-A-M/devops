import sys
from pathlib import Path

# Add project root to sys.path before any app imports
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
from app.db import init_db_pool, close_db_pool
from app.test_utils import execute_cmd

async def remove_test_card(card_id: str = "test-card-99"):
    query = "DELETE FROM credit_cards WHERE id = $1;"
    status = await execute_cmd(query, card_id)
    
    deleted_count = status.split(" ")[-1]
    if deleted_count != "0":
        print(f"Successfully removed card '{card_id}' from database! ({status})")
    else:
        print(f"Card '{card_id}' was not found in database. ({status})")

async def main():
    await init_db_pool()
    try:
        await remove_test_card("test-card-99")
    finally:
        await close_db_pool()

if __name__ == "__main__":
    asyncio.run(main())