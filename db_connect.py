import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        # THIS IS THE CRITICAL LINE
        db_url = os.getenv("DATABASE_URL")
        
        if db_url:
            conn = psycopg2.connect(db_url)
        else:
            # This fallback is only for your local computer
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME", "military_food_db"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "postgres"),
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432")
            )
        return conn
    except Exception as e:
        print(f"[FATAL DB ERROR] {e}")
        raise e
