-- ============================================================
-- Credit Card Analytics: schema.sql
-- ============================================================

CREATE TABLE credit_cards (
    id VARCHAR(50) PRIMARY KEY,                   
    name VARCHAR(100) NOT NULL,
    issuer VARCHAR(100) NOT NULL,

    annual_fee NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (annual_fee >= 0),
    base_cashback_percent NUMERIC(5, 2) NOT NULL CHECK (base_cashback_percent >= 0),
    travel_multiplier NUMERIC(4, 2) NOT NULL DEFAULT 1.00 CHECK (travel_multiplier >= 0),
    dining_multiplier NUMERIC(4, 2) NOT NULL DEFAULT 1.00 CHECK (dining_multiplier >= 0),

    -- JSONB keeps the nested timeline / tier mappings intact and query-able
    government_reward_modifier JSONB NOT NULL,
    reward_tiers JSONB NOT NULL,

    foreign_transaction_fee_percent NUMERIC(5, 2) NOT NULL
        CHECK (foreign_transaction_fee_percent BETWEEN 0 AND 100),
    apr NUMERIC(5, 2) NOT NULL CHECK (apr >= 0),

    -- Structured tier for programmatic eligibility checks, free text for display detail
    credit_score_tier VARCHAR(20) NOT NULL
        CHECK (credit_score_tier IN ('poor', 'fair', 'good', 'very_good', 'excellent')),
    credit_score_note TEXT,

    signup_bonus TEXT,
    network_type VARCHAR(100) NOT NULL,
    fx_fee_schedule TEXT NOT NULL,
    reward_expiry_policy TEXT,
    limits TEXT NOT NULL,

    perks TEXT[] NOT NULL DEFAULT '{}',

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Keep updated_at accurate without relying on the app remembering to set it
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_credit_cards_updated_at
    BEFORE UPDATE ON credit_cards
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

-- Speeds up your two most common filters
CREATE INDEX idx_credit_cards_active ON credit_cards (is_active) WHERE is_active = TRUE;
CREATE INDEX idx_credit_cards_fx_fee ON credit_cards (foreign_transaction_fee_percent);