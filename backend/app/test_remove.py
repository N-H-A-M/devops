# app/test_remove.py
from sqlalchemy import text
from app.db import engine

def insert_test_card():
    query = text("""
        DELETE FROM credit_cards WHERE id='test-card-99';
    """)

    with engine.connect() as conn:
        conn.execute(query)
        conn.commit()
        print("✅ Successfully removed test card from database!")

if __name__ == "__main__":
    insert_test_card()