#!/usr/bin/env bash

# Exit immediately if a command fails
set -e

# -----------------------------------------------------------------------------
# 1. PATH RESOLUTION (Absolute Paths)
# -----------------------------------------------------------------------------
# Find the absolute directory where THIS script lives (e.g. /home/.../devops project/deploy)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Resolve absolute path to project root and .env file
export PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
ENV_FILE="$PROJECT_ROOT/.env"
COMPOSE_FILE="$PROJECT_ROOT/deploy/docker-compose.yaml"

# Always execute docker commands from the deploy folder
cd "$PROJECT_ROOT"
echo "📂 Project Root: $PROJECT_ROOT"
echo "🐳 Compose File:  $COMPOSE_FILE"
echo "🔑 ENV File:      $ENV_FILE"

# -----------------------------------------------------------------------------
# 2. PRE-FLIGHT CHECK
# -----------------------------------------------------------------------------
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ ERROR: .env file not found at $ENV_FILE!"
    echo "Please create a .env file in the root directory before running this script."
    exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ ERROR: docker-compose.yaml not found at $COMPOSE_FILE!"
    exit 1
fi

# -----------------------------------------------------------------------------
# 3. EXECUTION
# -----------------------------------------------------------------------------
echo " [1/4] Stopping containers and removing volumes..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" down --volumes --remove-orphans

echo " [2/4] Rebuilding and starting services..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up --build -d

echo " [3/4] Waiting for database healthcheck..."
TIMEOUT=30
ELAPSED=0
until [ "$(docker inspect --format='{{json .State.Health.Status}}' cards_postgres_localv2 2>/dev/null)" == '"healthy"' ]; do
  if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "❌ Timeout waiting for database healthcheck."
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs postgres_db
    exit 1
  fi
  echo "   Waiting for database to become healthy ($ELAPSED/$TIMEOUT sec)..."
  sleep 3
  ELAPSED=$((ELAPSED + 3))
done

echo "✅ Database is healthy!"

echo " [4/4] Checking running container statuses..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps

echo "--- Backend Logs ---"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs backend --tail 25

echo " Success! Testing backend endpoint at http://localhost:8000/docs..."
curl -s -o /dev/null -w "Backend HTTP Status Code: %{http_code}\n" http://localhost:8000/docs || echo "Backend check finished."