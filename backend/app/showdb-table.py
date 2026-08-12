# app/show_cards.py
import sys
import os
from pathlib import Path
from sqlalchemy import text, create_engine
from dotenv import load_dotenv

current_file = Path(__file__).resolve()
backend_dir = current_file.parents[1]  # adjusts to parent directory
root_dir   = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

load_dotenv(root_dir / ".env")
user     = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD") 
db_name  = os.getenv("DB_NAME")
port     = os.getenv("DB_PORT", "5432")
raw_url = os.getenv("DATABASE_URL", f"postgresql://{user}:{password}@localhost:{port}/{db_name}")
local_url = raw_url.replace("@postgres_db:", "@localhost:")
engine = create_engine(local_url)
def display_cards_table():
    query = text("""
        SELECT 
            id, 
            name, 
            issuer, 
            network_type, 
            annual_fee, 
            base_cashback_percent, 
            is_active 
        FROM credit_cards 
        ORDER BY id;
    """)

    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()

        if not rows:
            print("⚠️ No cards found in the database!")
            return

        header_fmt = "{:<16} | {:<25} | {:<15} | {:<10} | {:<8} | {:<8} | {:<6}"
        row_fmt    = "{:<16} | {:<25} | {:<15} | {:<10} | ${:<7.2f} | {:<17.1f}% | {:<6}"

        print("\n" + "-"*110)
        print(header_fmt.format("ID", "Name", "Issuer", "Network", "Fee", "Base CashBack", "Active"))
        print("-"*110)

        for row in rows:
            print(row_fmt.format(
                row.id, 
                row.name[:25], 
                row.issuer[:15], 
                row.network_type, 
                float(row.annual_fee), 
                float(row.base_cashback_percent), 
                str(row.is_active)
            ))
        print("-"*110 + "\n")

if __name__ == "__main__":
    display_cards_table()