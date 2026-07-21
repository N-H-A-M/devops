"""
Database access layer. Owns the connection pool and all SQL.
Endpoints in card_comparison.py should never see raw asyncpg Records or
write SQL directly -- they call these functions and get CreditCard objects back.
"""
import asyncio, asyncpg, json , logging, os
from dotenv import load_dotenv
from typing import List, Optional
from app.models import CreditCard
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
logger = logging.getLogger("card_comparison")
_pool: Optional[asyncpg.Pool] = None

load_dotenv()



def _get_database_url() -> str:
    """
    Reads the connection string from the environment ONLY. Never hardcode
    a connection string here, in card_comparison.py, or anywhere else in
    the codebase. Locally this comes from a gitignored .env file; in
    Kubernetes it comes from a Secret mounted as an env var. The app
    doesn't need to know or care which -- same variable name either way.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Copy .env.example to .env and fill it in "
            "for local dev, or check the Secret is mounted correctly in Kubernetes."
        )
    return url


# 1. Get the URL and create the engine
engine = create_engine(_get_database_url())

# 2. Create the session maker (globally importable)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Create the Base (globally importable)
Base = declarative_base()

async def _register_jsonb_codec(conn: asyncpg.Connection) -> None:
    """Makes JSONB columns come back as native dicts instead of raw strings."""
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
        raise RuntimeError("DB pool not initialized -- did the app startup/lifespan run?")
    return _pool


def _row_to_card(row: asyncpg.Record) -> CreditCard:
    """
    Maps a DB row onto the existing CreditCard Pydantic model. The model
    still has a single `credit_score_required` field, so we recombine the
    DB's split tier + note columns into one display string here -- this
    keeps the API response shape stable even though storage is normalized.
    """
    tier = row["credit_score_tier"]
    note = row["credit_score_note"]
    credit_score_required = f"{tier.replace('_', ' ').title()} ({note})" if note else tier.replace('_', ' ').title()

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
    rows = await _get_pool().fetch(
        "SELECT * FROM credit_cards WHERE is_active = TRUE ORDER BY id"
    )
    return [_row_to_card(r) for r in rows]


async def fetch_card(card_id: str) -> Optional[CreditCard]:
    row = await _get_pool().fetchrow(
        "SELECT * FROM credit_cards WHERE id = $1 AND is_active = TRUE", card_id
    )
    return _row_to_card(row) if row else None


async def fetch_cards_by_ids(card_ids: List[str]) -> List[CreditCard]:
    rows = await _get_pool().fetch(
        "SELECT * FROM credit_cards WHERE id = ANY($1::varchar[]) AND is_active = TRUE",
        card_ids,
    )
    return [_row_to_card(r) for r in rows]


async def fetch_no_foreign_fee_cards() -> List[CreditCard]:
    rows = await _get_pool().fetch(
        "SELECT * FROM credit_cards WHERE foreign_transaction_fee_percent = 0 AND is_active = TRUE"
    )
    return [_row_to_card(r) for r in rows]


async def check_db_alive(timeout_seconds: float = 2.0) -> bool:
    """Real readiness check: can we actually reach and query Postgres right now?"""
    try:
        pool = _get_pool()
        async with pool.acquire() as conn:
            await asyncio.wait_for(conn.execute("SELECT 1"), timeout=timeout_seconds)
        return True
    except Exception as e:
        logger.warning("db_health_check_failed", extra={"error": str(e)})
        return False
