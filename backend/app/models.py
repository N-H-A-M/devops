from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class CreditCard(BaseModel):
    id: str = Field(..., description="Unique URL-safe identifier for the card")
    name: str = Field(..., description="The official marketing name of the card")
    issuer: str = Field(..., description="Name of card issuer company (e.g., Max, Cal, Isracard)")
    annual_fee: float = Field(..., ge=0, description="Annual membership fee")

    # Rewards Breakdown (Kept for US/Global style cards)
    base_cashback_percent: float = Field(..., description="Flat cashback rate on everyday purchases")
    travel_multiplier: float = Field(default=1.0, description="Points multiplier for travel bookings (e.g. 3x)")
    dining_multiplier: float = Field(default=1.0, description="Points multiplier for restaurants (e.g. 4x)")

    government_reward_modifier: Dict[str, float] = Field(
        ...,
        description="Cash back percentage rates for government payments mapped by timeline (e.g., {'year_1': 0.5, 'year_2': 0.38})"
    )

    # International & Abroad Overhead
    foreign_transaction_fee_percent: float = Field(..., description="Percentage fee added by the issuer when spending money abroad", ge=0, le=100)
    apr: float = Field(..., ge=0, description="Annual Percentage Rate.")
    credit_score_required: Optional[str] = Field(None, description="Typical credit tier required")
    signup_bonus: Optional[str] = Field(None, description="Current introductory offer. Can be blank.")

    # --- Israeli Club Rules Alignment ---
    network_type: str = Field(..., description="Dual-network routing rules if applicable (e.g., Diners/Mastercard)")

    reward_tiers: Dict[str, float] = Field(
        ...,
        description="Mapping of spending milestones thresholds to cashback/point return percentages"
    )

    fx_fee_schedule: str = Field(..., description="How foreign transaction fees scale or drop over time")
    reward_expiry_policy: Optional[str] = Field(None, description="Rules governing when points disappear")
    limits: str = Field(..., description="Monthly or annual tracking caps and point erasure windows")
    perks: List[str] = Field(default=[], description="List of extra benefits or redemption systems")
