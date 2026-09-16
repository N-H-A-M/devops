// Mirrors the CreditCard model returned by the backend's
// GET /cards and GET /cards/{id} endpoints. Field names match the JSON
// keys exactly (snake_case) on purpose -- a manual camelCase mapping layer
// is one more place for the two sides to silently drift out of sync.
export interface CreditCard {
  id: string;
  name: string;
  issuer: string;
  annual_fee: number;
  base_cashback_percent: number;
  travel_multiplier: number;
  dining_multiplier: number;
  government_reward_modifier: Record<string, number>;
  foreign_transaction_fee_percent: number;
  apr: number;
  credit_score_required: string;
  signup_bonus: string | null;
  network_type: string;
  reward_tiers: Record<string, number>;
  fx_fee_schedule: string;
  reward_expiry_policy: string | null;
  limits: string;
  perks: string[];
}