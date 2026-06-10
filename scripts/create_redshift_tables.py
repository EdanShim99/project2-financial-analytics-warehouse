import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("REDSHIFT_HOST"),
    port=5439,
    dbname="dev",
    user=os.getenv("REDSHIFT_USER"),
    password=os.getenv("REDSHIFT_PASSWORD")
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("CREATE SCHEMA IF NOT EXISTS staging;")

cur.execute("""
    CREATE TABLE IF NOT EXISTS staging.stock_prices (
        symbol VARCHAR(10),
        date DATE,
        open_price DECIMAL(12,4),
        high_price DECIMAL(12,4),
        low_price DECIMAL(12,4),
        close_price DECIMAL(12,4),
        volume BIGINT,
        loaded_at TIMESTAMP DEFAULT GETDATE()
    );
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS staging.econ_indicators (
        series_id VARCHAR(50),
        date DATE,
        value DECIMAL(18,4),
        loaded_at TIMESTAMP DEFAULT GETDATE()
    );
""")

print("Tables created!")
cur.close()
conn.close()
