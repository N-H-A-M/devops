# app/repository.py
from typing import List, Optional
import asyncpg
from app.db import get_pool
from app.models import CreditCard


def _row_to_card(row: asyncpg.Record) -> CreditCard:
    tier = row["credit_score_tier"]
    note = row["credit_score_note"]
    credit_score_required = (
        f"{tier.replace('_', ' ').title()} ({note})"
        if note
        else tier.replace("_", " ").title()
    )

    return CreditCard(
        id=row["id"],
        name=row["name"],
        issuer=row["issuer"],
        annual_fee=float(row["annual_fee"]),
        base_cashback_percent=float(row["base_cashback_percent"]),
        travel_multiplier=float(row["travel_multiplier"]),
        dining_multiplier=float(row["dining_multiplier"]),
        government_reward_modifier=row["government_reward_modifier"],
        foreign_transaction_fee_percent=float(row["foreign_transaction_fee_percent"]),
        apr=float(row["apr"]),
        credit_score_required=credit_score_required,
        signup_bonus=row["signup_bonus"],
        network_type=row["network_type"],
        reward_tiers=row["reward_tiers"],
        fx_fee_schedule=row["fx_fee_schedule"],
        reward_expiry_policy=row["reward_expiry_policy"],
        limits=row["limits"],
        perks=list(row["perks"]),
    )


async def fetch_all_cards() -> List[CreditCard]:
    rows = await get_pool().fetch(
        "SELECT * FROM credit_cards WHERE is_active = TRUE ORDER BY id"
    )
    return [_row_to_card(r) for r in rows]


async def fetch_card(card_id: str) -> Optional[CreditCard]:
    row = await get_pool().fetchrow(
        "SELECT * FROM credit_cards WHERE id = $1 AND is_active = TRUE", card_id
    )
    return _row_to_card(row) if row else None


async def fetch_cards_by_ids(card_ids: List[str]) -> List[CreditCard]:
    rows = await get_pool().fetch(
        "SELECT * FROM credit_cards WHERE id = ANY($1::varchar[]) AND is_active = TRUE",
        card_ids,
    )
    return [_row_to_card(r) for r in rows]


async def fetch_no_foreign_fee_cards() -> List[CreditCard]:
    rows = await get_pool().fetch(
        "SELECT * FROM credit_cards WHERE foreign_transaction_fee_percent = 0 AND is_active = TRUE"
    )
    return [_row_to_card(r) for r in rows]