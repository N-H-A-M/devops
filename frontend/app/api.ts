import { CreditCard } from '../types/card_specs';

// Set NEXT_PUBLIC_API_URL in .env.local (see .env.local.example).
// The localhost fallback is only for convenience in local dev --
// never hardcode a real deployment URL here.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function apiFetch<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`);
  } catch {
    throw new ApiError(`Could not reach the API at ${API_BASE_URL}. Is the backend running?`);
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(body?.detail ?? `Request failed (${response.status})`, response.status);
  }

  return response.json();
}

export function getCards(): Promise<CreditCard[]> {
  return apiFetch<CreditCard[]>('/cards');
}