#!/usr/bin/env bash

# Stop on errors
set -e

# Define relative path to .env file
ENV_FILE="../.env"

echo "🧹 [1/4] Stopping containers and removing volumes..."
docker compose --env-file "$ENV_FILE" down --volumes --remove-orphans

echo "🚀 [2/4] Rebuilding and starting services..."
docker compose --env-file "$ENV_FILE" up --build -d

echo "⏳ [3/4] Waiting for services to pass healthchecks..."
# Wait until postgres_db reaches healthy status (timeout after 30s)
TIMEOUT=30
ELAPSED=0
until [ "$(docker inspect --format='{{json .State.Health.Status}}' cards_postgres_localv2 2>/dev/null)" == '"healthy"' ]; do
  if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "❌ Timeout waiting for database healthcheck."
    docker compose logs postgres_db
    exit 1
  fi
  echo "   Waiting for database to be healthy ($ELAPSED/$TIMEOUT sec)..."
  sleep 3
  ELAPSED=$((ELAPSED + 3))
done

echo "✅ Database is healthy!"

echo "📋 [4/4] Checking running container statuses..."
docker compose ps

echo "--- Backend Logs ---"
docker compose logs backend --tail 20

echo "🎉 Everything is up! Testing backend endpoint..."
curl -s -o /dev/null -w "Backend Status Code: %{http_code}\n" http://localhost:8000/docs || echo "Backend ping finished."