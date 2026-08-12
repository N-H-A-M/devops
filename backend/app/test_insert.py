# app/test_insert.py
import asyncio
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def insert_test_card():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set.")

    conn = await asyncpg.connect(db_url)
    try:
        query = """
            INSERT INTO credit_cards (
                id, name, issuer, annual_fee, base_cashback_percent, 
                travel_multiplier, dining_multiplier, government_reward_modifier, 
                foreign_transaction_fee_percent, apr, credit_score_tier, credit_score_note, 
                signup_bonus, network_type, reward_tiers, fx_fee_schedule, 
                reward_expiry_policy, limits, perks, is_active
            ) VALUES (
                'test-card-99', 'Silverline Titanium Test', 'Apex Bank', 0.00, 3.5, 
                1.0, 1.0, '{"rate": 1.0}'::jsonb, 0.0, 18.99, 'excellent', '740+', 
                '50000 points', 'Visa', '{}'::jsonb, '{}'::jsonb, 
                'None', '{}'::jsonb, ARRAY['No Annual Fee', '3.5% Cash Back'], TRUE
            ) ON CONFLICT (id) DO NOTHING;
        """
        await conn.execute(query)
        print("Successfully inserted test card into database!")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(insert_test_card())