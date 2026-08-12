-- ============================================================
-- Credit Card Analytics: seed.sql
-- Seeds the 3 cards currently hardcoded in CARDS_INFO.
--
-- NOTE on credit_score_tier: the old freeform strings didn't map cleanly
-- onto a fixed enum, so I made a judgment call splitting them into
-- tier + note. Check these three before relying on them for filtering:
--   "Good (Student options available upon credential validation)" -> good / note
--   "Standard/Good"                                                -> good / note
--   "Good"                                                          -> good / (no note)
-- ============================================================

INSERT INTO credit_cards (
    id, name, issuer, annual_fee, base_cashback_percent,
    travel_multiplier, dining_multiplier,
    government_reward_modifier, reward_tiers,
    foreign_transaction_fee_percent, apr,
    credit_score_tier, credit_score_note,
    signup_bonus, network_type, fx_fee_schedule,
    reward_expiry_policy, limits, perks
) VALUES
(
    'cashcal-pro',
    'CashCal Pro',
    'Cal (Credit Cards for Israel Ltd. / Diners Club Israel)',
    0.00,
    1.00,
    1.00,
    1.00,
    '{
        "year_1_under_10k": 0.5,
        "year_1_over_10k_pre_july_2025": 0.8,
        "year_1_over_10k_post_july_2025": 0.6,
        "year_2_plus_under_10k": 0.38,
        "year_2_plus_over_10k": 0.5
    }'::jsonb,
    '{
        "year_1_under_10k_nis": 1.0,
        "year_1_over_10k_nis_post_july_2025": 1.25,
        "year_2_plus_under_10k_nis": 0.75,
        "year_2_plus_over_10k_nis": 1.0
    }'::jsonb,
    1.00,
    12.50,
    'good',
    'Student options available upon credential validation',
    'Reduced promotional 1% FX fee during year 1 and elevated cashback tiering.',
    'Diners Club (Domestic Israel) / Mastercard (International & Online)',
    '1% foreign currency transaction fee applied during the first 12 months from card issuance, adjusting to 2% from the 13th month onwards.',
    'Accumulated cashback must be transferred to BUYME by the end of the first calendar quarter of the following year (March 31st), otherwise balances of 50 NIS or higher are wiped. Balances under 50 NIS roll over to the next calendar year.',
    'Maximum accumulation capped at 450 NIS per calendar month and 5,400 NIS per calendar year. Requires a minimum transaction volume of 1 NIS per month to trigger collection. Non-eligible items include cash withdrawals, P2P transfers/apps, and wallet reloads.',
    ARRAY[
        'Automatic enrollment into the CashCal Pro rewards tier upon card activation',
        'Direct point transfer pipeline to BUYME digital shopping vouchers',
        'Redemption available in multi-step increments of 50 NIS (Minimum activation floor is 50 NIS)',
        'Post-cancellation preservation: Unreleased points can still be managed via Cal app for up to 6 months and transferred up until March 31st of the following year'
    ]
),
(
    'max-back-total',
    'MAX Back Total',
    'Max',
    0.00,
    1.00,
    1.00,
    1.00,
    '{
        "year_1": 0.5,
        "year_2_plus": 0.375
    }'::jsonb,
    '{
        "year_1_everyday": 1.0,
        "year_2_plus_everyday": 0.75
    }'::jsonb,
    3.00,
    12.50,
    'good',
    'Advertised as "Standard/Good" -- confirm exact minimum tier with issuer',
    'Elevated year 1 conversion baseline (1.0% cashback drops down to 0.75% from year 2 onward).',
    'Visa or Mastercard (Private/Non-corporate only)',
    'Fixed transaction fee added directly to converted NIS balance during the next monthly statement.',
    'Each annual points pool is valid for 3 years. Remainder is wiped on the 4th billing cycle following the end of that pool''s timeline.',
    'Max annual cap of 2,000 points per calendar year. Absolute wallet ceiling of 6,000 concurrent points. Partial/fractional points are discarded at statement closing.',
    ARRAY[
        'MAX Treats (תוכנית הפינוקים) automatic enrollment',
        'MAX GiftCard redemption (1:1 ratio, min 75 points, max 1,500 points per card)',
        'FOOD GiftCard redemption (1:0.9 ratio, min 75 points, max 1,500 points per card)',
        'Accumulate & Return (צובר ושב) interest savings channel (1:0.9 ratio, min 500 points)',
        'SKYMAX flights hub transfer (1:0.42 point conversion ratio, min 75 points)',
        'Crypto asset tracking via Bits of Gold (1:0.9 ratio, min 75 points)'
    ]
),
(
    'cal-365-vip',
    'Cal 365 VIP',
    'Cal (Credit Cards for Israel Ltd.) in partnership with Mashbir 365',
    100.00,
    10.00,
    1.00,
    1.00,
    '{
        "standard_rate": 0.0
    }'::jsonb,
    '{
        "fashion_shoes_homeware_textiles_luggage": 15.0,
        "undergarments_sports_swimwear": 10.0,
        "cosmetics_appliances_electronics_jewelry": 5.0
    }'::jsonb,
    2.80,
    12.50,
    'good',
    NULL,
    '50 NIS welcome voucher, 50 NIS physical card setup voucher, 50 NIS statement credit, and 100 NIS cashback bonus if spending 500 NIS in 3 months.',
    'Cal Credit Card Network',
    'Standard Cal tariff applies after promotional period. 6-month free card fee waiver for new cardholders.',
    'Points expire on a rolling basis 24 months from collection. Remaining points stay valid for 24 months even if card is cancelled.',
    'Minimum redemption floor: 30 points. Maximum redemption per transaction: 2,000 points. Double points on birthday month up to 1,000 NIS spend.',
    ARRAY[
        'Valid across all Mashbir department stores nationwide (excluding outlet clearance)',
        'Anti-reselling cap safeguard (Max 4 identical barcodes in Electronics/Cosmetics)',
        'Points clear and become deployable 2 business days after the initial transaction',
        'Benefits extend to cardholder, domestic partner, and dependent children up to age 21'
    ]
);
