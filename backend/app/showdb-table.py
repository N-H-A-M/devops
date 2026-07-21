# app/show_cards.py
from sqlalchemy import text
from app.db import engine

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