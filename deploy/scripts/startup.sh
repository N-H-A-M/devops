#!/bin/bash
set -e

# 1. Load your local .env file
if [ -f .env ]; then
    set -a
    source .env
    set +a
else
    echo "❌ .env file not found!"
    exit 1
fi

# 2. Extract values from your existing DATABASE_URL so you don't have to duplicate variables
export DB_USER=$(python3 -c "from urllib.parse import urlparse; p = urlparse('''$DATABASE_URL'''); print(p.username or '')")
export DB_PASSWORD=$(python3 -c "from urllib.parse import urlparse; p = urlparse('''$DATABASE_URL'''); print(p.password or '')")
export DB_NAME=$(python3 -c "from urllib.parse import urlparse; p = urlparse('''$DATABASE_URL'''); print(p.path.lstrip('/'))")
COMPOSE_FILE="./k8s/db_compose.yaml"

echo "🐳 Spinning up secure, isolated PostgreSQL container..."
docker compose -f "$COMPOSE_FILE" up -d postgres_db

echo "⏳ Waiting for database readiness..."
until docker compose -f "$COMPOSE_FILE" exec postgres_db pg_isready -U "$DB_USER" -d "$DB_NAME"; do
  sleep 1
done

echo "✅ Database is ready!"

# 3. Launch Uvicorn locally
export PYTHONPATH=$PYTHONPATH:.
echo "🚀 Starting Uvicorn API server..."
uvicorn src.card_src.card_comparison:app --reload