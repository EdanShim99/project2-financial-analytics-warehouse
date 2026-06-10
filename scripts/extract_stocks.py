import os
import json
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import boto3
from datetime import datetime

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BUCKET = os.getenv("S3_BUCKET")
BASE_URL = "https://www.alphavantage.co/query"

SYMBOLS = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "GOOGL": "Technology",
    "JPM": "Financials",
    "GS": "Financials",
    "JNJ": "Healthcare",
    "PFE": "Healthcare",
    "XOM": "Energy",
    "PG": "Consumer Staples",
    "DIS": "Communication Services",
}


def get_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=3,
        status_forcelist=[500, 502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def extract_daily_prices(session, symbol):
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": API_KEY,
    }
    response = session.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "Error Message" in data:
        raise ValueError(f"API error for {symbol}: {data['Error Message']}")
    if "Note" in data:
        raise ValueError(f"Rate limit hit: {data['Note']}")

    return data


def upload_to_s3(data, symbol, execution_date):
    s3 = boto3.client("s3")
    key = f"raw/stocks/{execution_date}/{symbol}.json"
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json",
    )
    print(f"Uploaded {key}")


def run(execution_date=None):
    if execution_date is None:
        execution_date = datetime.now().strftime("%Y-%m-%d")

    session = get_session()
    results = {"success": [], "failed": []}

    for symbol in SYMBOLS:
        try:
            print(f"Extracting {symbol}...")
            data = extract_daily_prices(session, symbol)
            upload_to_s3(data, symbol, execution_date)
            results["success"].append(symbol)
            time.sleep(15)
        except Exception as e:
            print(f"Failed {symbol}: {e}")
            results["failed"].append({"symbol": symbol, "error": str(e)})

    print(f"Done. Success: {len(results['success'])}, Failed: {len(results['failed'])}")

    if results["failed"]:
        raise Exception(f"Failed symbols: {results['failed']}")

    return results


if __name__ == "__main__":
    run()