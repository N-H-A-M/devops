import json
import logging
import sys
import time
import uuid 
import os
from contextlib import asynccontextmanager
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response, Query, Request, Path
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app import db
from .models import CreditCard

# Loads DATABASE_URL from local .env file if present
load_dotenv()
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
# ---------------------------------------------------------
# 0. STRUCTURED JSON LOGGING
# ---------------------------------------------------------
class JSONFormatter(logging.Formatter):
    _RESERVED = {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "message", "taskName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
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

origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_APP_START_TIME = time.monotonic()


@app.middleware("http")
async def log_requests(request: Request, call_next):
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
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# ---------------------------------------------------------
# 3. CORE ANALYTICS ENDPOINTS
# ---------------------------------------------------------

@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy"}


@app.get("/health/live", tags=["System"], include_in_schema=False)
def liveness():
    return {"status": "alive", "uptime_seconds": round(time.monotonic() - _APP_START_TIME, 1)}


@app.get("/health/ready", tags=["System"], include_in_schema=False)
async def readiness(response: Response):
    try:
        is_ready = await db.check_db_alive()
    except Exception as exc:
        logger.error("readiness_check_exception", extra={"error": str(exc)})
        is_ready = False

    response.status_code = 200 if is_ready else 503
    return {"status": "ready" if is_ready else "not_ready"}


@app.get("/cards", response_model=List[CreditCard], tags=["Cards"])
async def list_cards():
    return await db.fetch_all_cards()


@app.get("/cards/compare", tags=["Cards"])
async def compare_cards(
    card_ids: List[str] = Query(
        ..., 
        description="List of card IDs to compare (Accepts 2 or 3 IDs)",
    )
):
    if len(card_ids) < 2 or len(card_ids) > 3:
        logger.warning("compare_invalid_card_count", extra={"card_ids": card_ids, "count": len(card_ids)})
        raise HTTPException(
            status_code=400, 
            detail="Comparison requires at least 2 cards and a maximum of 3 cards."
        )

    found_cards = await db.fetch_cards_by_ids(card_ids)
    found_by_id = {c.id: c for c in found_cards}
    missing = [cid for cid in card_ids if cid not in found_by_id]
    if missing:
        logger.warning("compare_card_not_found", extra={"missing_ids": missing, "requested_ids": card_ids})
        raise HTTPException(status_code=404, detail=f"Card(s) not found: {', '.join(missing)}")
    
    selected_cards = [found_by_id[cid] for cid in card_ids]

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

    comparison_table = []
    for label, field in attributes_to_compare:
        row = {"attribute": label}
        for index, card in enumerate(selected_cards):
            row[f"card_{index + 1}"] = getattr(card, field)
        comparison_table.append(row)

    return {
        "card_count": len(selected_cards),
        "headers": [card.name for card in selected_cards],
        "rows": comparison_table
    }


@app.get("/cards/no-foreign-fees", response_model=List[CreditCard], tags=["Analytics"])
async def get_travel_friendly_cards():
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
    purchase_amount_usd: float = Query(..., gt=0, description="Must be greater than $0"), 
    shipping_tax_percent: float = Query(0.0, ge=0, le=100, description="Tax percentage between 0 and 100")
    ):
    card = await db.fetch_card(card_id)
    if not card:
        logger.warning("card_not_found", extra={"card_id": card_id})
        raise HTTPException(status_code=404, detail=f"Card not found '{card_id}' ")
    
    shipping_tax_cost = purchase_amount_usd * (shipping_tax_percent / 100)
    subtotal = purchase_amount_usd + shipping_tax_cost
    fx_fee_cost = subtotal * (card.foreign_transaction_fee_percent / 100)
    total_charged_to_user = subtotal + fx_fee_cost
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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", extra={"path": request.url.path, "error": str(exc)})
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )