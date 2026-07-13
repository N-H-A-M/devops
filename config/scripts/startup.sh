#!/bin/bash
set -e

# 1. Activate your virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 2. Correctly source the .env file without using export $(cat ...)
if [ -f .env ]; then
    # Using 'set -a' tells bash to automatically export all variables read from the file
    set -a
    source .env
    set +a
else
    echo "❌ .env file not found! Please create one with DATABASE_URL."
    exit 1
fi

# 3. Dedicated variables for fallback provisioning (matching your debug URL)
DB_USER="dsa"
DB_PASS="f3szpv"
DB_NAME="cards_db"

echo "⚙️ Checking PostgreSQL local environment..."

# 4. Create the Database User if it doesn't exist
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS' SUPERUSER;"

# 5. Create the Database if it doesn't exist
sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME" || \
sudo -u postgres psql -c "CREATE DATABASE \"$DB_NAME\" OWNER $DB_USER;"

echo "✅ PostgreSQL environment is verified and ready."

# 6. Set PYTHONPATH and launch
export PYTHONPATH=$PYTHONPATH:.
echo "🚀 Starting Uvicorn API server..."
uvicorn src.card_src.card_comparison:app --reload