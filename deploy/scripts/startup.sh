#!/bin/bash
set -e

# 1. Dynamically locate the project root relative to this script's location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
COMPOSE_FILE="$PROJECT_ROOT/deploy/docker-compose.yaml"
ENV_FILE="$PROJECT_ROOT/.env"

# 2. Check for .env file or prompt the user for DATABASE_URL
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
elif [ -z "$DATABASE_URL" ]; then
    echo "⚠️  No .env file found at $ENV_FILE"
    read -p "Enter your PostgreSQL DATABASE_URL [default: postgresql://postgres:postgres@localhost:5432/cards_db]: " input_url
    export DATABASE_URL="${input_url:-postgresql://postgres:postgres@localhost:5432/cards_db}"
fi

# 3. Extract database credentials dynamically using Python
export DB_USER=$(python3 -c "from urllib.parse import urlparse; p = urlparse('''$DATABASE_URL'''); print(p.username or 'postgres')")
export DB_PASSWORD=$(python3 -c "from urllib.parse import urlparse; p = urlparse('''$DATABASE_URL'''); print(p.password or 'postgres')")
export DB_NAME=$(python3 -c "from urllib.parse import urlparse; p = urlparse('''$DATABASE_URL'''); print(p.path.lstrip('/') or 'cards_db')")

echo "🐳 Spinning up isolated PostgreSQL container using $COMPOSE_FILE..."
docker compose -f "$COMPOSE_FILE" up -d postgres_db

echo "⏳ Waiting for database readiness..."
until docker compose -f "$COMPOSE_FILE" exec postgres_db pg_isready -U "$DB_USER" -d "$DB_NAME"; do
  sleep 1
done

echo "✅ Database is ready and reachable!"