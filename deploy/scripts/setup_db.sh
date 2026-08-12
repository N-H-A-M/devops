#!/bin/bash
set -e

# 1. Load the environment variables from .env
if [ -f .env ]; then
    set -a
    source .env
    set +a
else
    echo "❌ .env file not found! Please create one with DATABASE_URL."
    exit 1
fi

# 2. Parse the credentials safely using Python to avoid sed errors
DB_USER=$(python3 -c "from urllib.parse import urlparse; p = urlparse('''$DATABASE_URL'''); print(p.username or '')")
DB_PASS=$(python3 -c "from urllib.parse import urlparse; p = urlparse('''$DATABASE_URL'''); print(p.password or '')")
DB_NAME=$(python3 -c "from urllib.parse import urlparse; p = urlparse('''$DATABASE_URL'''); print(p.path.lstrip('/'))")

# Fallback path to your SQL schema file
SQL_FILE_PATH="/home/devwork/devops project/devops/backend/migrations/versions/schema.sql"

echo "⚙️  Starting robust database environment setup..."
echo "DEBUG parsed values: User='$DB_USER', DB='$DB_NAME'"

# 3. Check and Create the User if it doesn't exist
USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'")
if [ "$USER_EXISTS" != "1" ]; then
    echo "👤 User '$DB_USER' does not exist. Creating now..."
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS' SUPERUSER;"
else
    echo "✅ User '$DB_USER' already exists. Skipping user creation."
fi

# 4. Check and Create the Database if it doesn't exist
DB_EXISTS=$(sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME" && echo "1" || echo "0")
if [ "$DB_EXISTS" != "1" ]; then
    echo "🗄️  Database '$DB_NAME' does not exist. Creating now..."
    sudo -u postgres psql -c "CREATE DATABASE \"$DB_NAME\" OWNER $DB_USER;"
else
    echo "✅ Database '$DB_NAME' already exists. Skipping database creation."
fi

# 5. Check if tables inside the schema file already exist before executing
SEED_FILE_PATH="/home/devwork/devops project/devops/backend/migrations/versions/seed.sql"

if [ -f "$SQL_FILE_PATH" ]; then
    echo "📝 Schema file found. Checking for existing tables..."
    
    TABLE_EXISTS=$(sudo psql -h 127.0.0.1  -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='credit_cards';")
    
    if [ "$TABLE_EXISTS" != "1" ]; then
        echo "🚀 Table credit_cards missing. Executing schema file..."
        sudo psql -h 127.0.0.1 -U "$DB_USER" -d "$DB_NAME" < "$SQL_FILE_PATH"
        
        # --- NEW SEEDING BLOCK ---
        if [ -f "$SEED_FILE_PATH" ]; then
            echo "🌱 Seed file found. Injecting initial data: $SEED_FILE_PATH"
            sudo psql -h 127.0.0.1 -U "$DB_USER" -d "$DB_NAME" < "$SEED_FILE_PATH"
            echo "✅ Data successfully seeded!"
        else
            echo "ℹ️  No seed file found at $SEED_FILE_PATH. Skipping data injection."
        fi
        # -------------------------
        
    else
        echo "ℹ️  Tables already exist in '$DB_NAME' ($TABLES_COUNT found). Skipping schema and seed execution to protect data."
    fi
else
    echo "⚠️  Warning: Schema file not found at $SQL_FILE_PATH. Skipping table initialization."
fi

echo "🎉 Database verification complete! Ready to accept connections."