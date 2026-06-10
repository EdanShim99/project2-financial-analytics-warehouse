import boto3
import json
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)
bucket = os.getenv('S3_BUCKET')

conn = psycopg2.connect(
    host=os.getenv('REDSHIFT_HOST'),
    port=5439,
    dbname='dev',
    user=os.getenv('REDSHIFT_USER'),
    password=os.getenv('REDSHIFT_PASSWORD')
)
conn.autocommit = True
cur = conn.cursor()


def load_stocks():
    # List all stock files
    response = s3.list_objects_v2(Bucket=bucket, Prefix='raw/stocks/')
    rows = []

    for obj in response.get('Contents', []):
        key = obj['Key']
        if not key.endswith('.json'):
            continue

        symbol = key.split('/')[-1].replace('.json', '')
        data = json.loads(s3.get_object(Bucket=bucket, Key=key)['Body'].read())
        time_series = data.get('Time Series (Daily)', {})

        for date, values in time_series.items():
            rows.append((
                symbol,
                date,
                float(values['1. open']),
                float(values['2. high']),
                float(values['3. low']),
                float(values['4. close']),
                int(values['5. volume'])
            ))

    # Clear and reload
    cur.execute("DELETE FROM staging.stock_prices;")
    for i in range(0, len(rows), 500):
        batch = rows[i:i+500]
        args = ','.join(
            cur.mogrify("(%s,%s,%s,%s,%s,%s,%s)", row).decode()
            for row in batch
        )
        cur.execute(f"""
            INSERT INTO staging.stock_prices
            (symbol, date, open_price, high_price, low_price, close_price, volume)
            VALUES {args}
        """)

    print(f"Loaded {len(rows)} stock price rows")


def load_econ():
    response = s3.list_objects_v2(Bucket=bucket, Prefix='raw/econ/')
    rows = []

    for obj in response.get('Contents', []):
        key = obj['Key']
        if not key.endswith('.json'):
            continue

        series_id = key.split('/')[-1].replace('.json', '')
        data = json.loads(s3.get_object(Bucket=bucket, Key=key)['Body'].read())

        for obs in data.get('observations', []):
            if obs['value'] == '.':
                continue
            rows.append((
                series_id,
                obs['date'],
                float(obs['value'])
            ))

    # Clear and reload
    cur.execute("DELETE FROM staging.econ_indicators;")
    for i in range(0, len(rows), 500):
        batch = rows[i:i+500]
        args = ','.join(
            cur.mogrify("(%s,%s,%s)", row).decode()
            for row in batch
        )
        cur.execute(f"""
            INSERT INTO staging.econ_indicators
            (series_id, date, value)
            VALUES {args}
        """)

    print(f"Loaded {len(rows)} econ indicator rows")


if __name__ == '__main__':
    load_stocks()
    load_econ()
    cur.close()
    conn.close()
    print("Done!")
