# app/show_cards.py
import sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
import asyncio
from app.db import init_db_pool, close_db_pool, fetch_all_cards

async def main():
    await init_db_pool()
    try:
        cards = await fetch_all_cards()
        if not cards:
            print("No cards found in database.")
            return
        for card in cards:
            print(f"[{card.get('id')}] {card.get('name')} | Fee: {card.get('annual_fee')}")
    finally:
        await close_db_pool()

if __name__ == "__main__":
    asyncio.run(main())