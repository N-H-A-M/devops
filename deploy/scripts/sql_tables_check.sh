#!/usr/bin/env bash
set -e

# Automatically resolve paths without relying on current working directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"



CONTAINER="cards_postgres_localv2"
# 1. Get the exact database name running in the container
DB_NAME=$(docker exec $CONTAINER env | grep POSTGRES_DB | cut -d'=' -f2)
DB_NAME=${DB_NAME:-cards_db}

# 2. Get the exact username running in the container
DB_USER=$(docker exec $CONTAINER env | grep POSTGRES_USER | cut -d'=' -f2)
DB_USER=${DB_USER:-postgres}
echo "DATABASE USER is $DB_USER"
echo "DATABASE NAME is $DB_NAME"
echo "Starting live view of database on container $CONTAINER..."
echo "Press Ctrl+C to stop."
sleep 1

# Auto-refreshes every 2 seconds
watch -n 2 "docker exec -i $CONTAINER psql -U $DB_USER -d $DB_NAME -c '\x on' -c 'SELECT * FROM credit_cards;'"