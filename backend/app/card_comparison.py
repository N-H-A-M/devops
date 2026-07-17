import json, logging, sys, time, uuid
from src.postgres_sql import db
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response, Query, Request
from typing import List, Optional
from src.card_src.models import CreditCard

# Loads DATABASE_URL (and anything else) from a local .env file if present.
# In Kubernetes there's no .env file, so this is a harmless no-op there --
# env vars come from the Secret directly.
load_dotenv()

# ---------------------------------------------------------
# 0. STRUCTURED JSON LOGGING
# ---------------------------------------------------------
# One JSON object per log line on stdout. This is the format container
# platforms and log aggregators (CloudWatch, Datadog, ELK, etc.) expect --
# no parsing raw print() text with regex on the other end.
class JSONFormatter(logging.Formatter):
    # Standard LogRecord attributes we don't want duplicated in the output
    _RESERVED = {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "message", "taskName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Anything passed via logger.info("msg", extra={...}) gets merged in flat
        for key, value in record.__dict__.items():
            if key not in self._RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)


configure_logging()
logger = logging.getLogger("card_comparison")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db_pool()
    yield
    await db.close_db_pool()


app = FastAPI(
    title="Credit Card Analytics Backend",
    description="Backend tracking card metrics, reward rates, and foreign exchange overhead costs.",
    lifespan=lifespan,
)

# Process start time, used to report uptime on the liveness probe
_APP_START_TIME = time.monotonic()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Every request goes through this single structured log line --
    replaces scattered print()s with one consistent, greppable channel."""
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response

# ---------------------------------------------------------
# 3. CORE ANALYTICS ENDPOINTS
# ---------------------------------------------------------

 
@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy"}


@app.get("/health/live", tags=["System"], include_in_schema=False)
def liveness():
    """
    Liveness probe: is the process up and responding at all?
    No dependency checks here on purpose — if a DB or downstream service is slow,
    that should never cause Kubernetes to kill/restart a perfectly fine pod.
    """
    return {"status": "alive", "uptime_seconds": round(time.monotonic() - _APP_START_TIME, 1)}


@app.get("/health/ready", tags=["System"], include_in_schema=False)
async def readiness(response: Response):
    """
    Readiness probe: can this pod actually serve traffic right now?
    Runs a real SELECT 1 against Postgres with a short timeout. Returns 503
    (not 200) on failure, so Kubernetes pulls the pod out of the load-balancer
    rotation without restarting it.
    """
    is_ready = await db.check_db_alive()
    response.status_code = 200 if is_ready else 503
    if not is_ready:
        logger.warning("readiness_check_failed")
    return {"status": "ready" if is_ready else "not_ready"}


@app.get("/cards", response_model=List[CreditCard], tags=["Cards"])
async def list_cards():
    """Retrieve all tracked credit cards and their structural rates."""
    return await db.fetch_all_cards()

@app.get("/cards/compare", tags=["Cards"])
async def compare_cards(
    card_ids: List[str] = Query(
        ..., 
        description="List of card IDs to compare (Accepts 2 or 3 IDs)",
        #example=["cashcal-pro", "cal-365-vip"]
    )
):
    # Enforce minimum of 2 and maximum of 3 cards
    if len(card_ids) < 2 or len(card_ids) > 3:
        logger.warning("compare_invalid_card_count", extra={"card_ids": card_ids, "count": len(card_ids)})
        raise HTTPException(
            status_code=400, 
            detail="Comparison requires at least 2 cards and a maximum of 3 cards."
        )

    # Fetch whichever of the requested cards actually exist, then diff
    # against what was asked for -- one query instead of N round trips.
    found_cards = await db.fetch_cards_by_ids(card_ids)
    found_by_id = {c.id: c for c in found_cards}
    missing = [cid for cid in card_ids if cid not in found_by_id]
    if missing:
        logger.warning("compare_card_not_found", extra={"missing_ids": missing, "requested_ids": card_ids})
        raise HTTPException(status_code=404, detail=f"Card(s) not found: {', '.join(missing)}")
    # Preserve the order the caller requested, not DB return order
    selected_cards = [found_by_id[cid] for cid in card_ids]

    # Define the rows/attributes we want to map out visually
    attributes_to_compare = [
        ("ID", "id"),
        ("Card Name", "name"),
        ("Issuer", "issuer"),
        ("Annual Fee (NIS)", "annual_fee"),
        ("Base Cashback %", "base_cashback_percent"),
        ("Foreign Transaction Fee %", "foreign_transaction_fee_percent"),
        ("Network Type", "network_type"),
        ("Limits", "limits")
    ]

    # Pivot the data into a matrix structure (Row Name -> Card 1 Value -> Card 2 Value...)
    comparison_table = []
    for label, field in attributes_to_compare:
        row = {"attribute": label}
        for index, card in enumerate(selected_cards):
            # getattr reads the value dynamically from the Pydantic object
            row[f"card_{index + 1}"] = getattr(card, field)
        comparison_table.append(row)

    return {
        "card_count": len(selected_cards),
        "headers": [card.name for card in selected_cards],
        "rows": comparison_table
    }

@app.get("/cards/no-foreign-fees", response_model=List[CreditCard], tags=["Analytics"])
async def get_travel_friendly_cards():
    """Filter out only the cards that charge 0% on foreign purchases."""
    return await db.fetch_no_foreign_fee_cards()


@app.get("/cards/{card_id}", response_model=CreditCard)
async def get_card(card_id: str):
    card = await db.fetch_card(card_id)
    if not card:
        logger.warning("card_not_found", extra={"card_id": card_id})
        raise HTTPException(status_code=404, detail=f"Card not found '{card_id}' ")
    return card


@app.get("/calculate/foreign-purchase", tags=["Calculations"])
async def calculate_abroad_cost(
    card_id: str, 
    purchase_amount_usd: float, 
    shipping_tax_percent: float = Query(0.0, description="Any extra custom shipping tax or localized checkout overhead")
):
    """
    Simulates making a purchase abroad. 
    It calculates the transaction cost + the card's specific foreign transaction fee + any shipping tax.
    """
    # Find the requested card
    card = await db.fetch_card(card_id)
    if not card:
        logger.warning("card_not_found", extra={"card_id": card_id})
        raise HTTPException(status_code=404, detail=f"Card not found '{card_id}' ")
    
    # 1. Compute baseline taxes/shipping if specified
    shipping_tax_cost = purchase_amount_usd * (shipping_tax_percent / 100)
    subtotal = purchase_amount_usd + shipping_tax_cost
    
    # 2. Compute Card Foreign Exchange Fee
    fx_fee_cost = subtotal * (card.foreign_transaction_fee_percent / 100)
    
    # 3. Compute Total Cost out of pocket
    total_charged_to_user = subtotal + fx_fee_cost
    
    # 4. Compute baseline cashback earned on this transaction
    rewards_earned = subtotal * (card.base_cashback_percent / 100)
    
    return {
        "card_name": card.name,
        "base_amount_usd": purchase_amount_usd,
        "shipping_and_tax_overhead": shipping_tax_cost,
        "card_foreign_transaction_fee": fx_fee_cost,
        "total_wallet_deduction": total_charged_to_user,
        "estimated_rewards_earned_usd": rewards_earned,
        "net_cost_accounting_for_rewards": total_charged_to_user - rewards_earned
    }