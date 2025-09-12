import os
from dotenv import load_dotenv
import psycopg2
load_dotenv()
def get_db_connection():
    try:
        database_url = os.environ["DATABASE_URL"] 
    except KeyError:
        raise RuntimeError("DATABASE_URL environment variable not set")

    try:
        conn = psycopg2.connect(database_url)
        return conn
    except psycopg2.Error as e:
        raise RuntimeError(f"Database connection failed: {e}")


