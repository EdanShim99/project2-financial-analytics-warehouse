import os
import json
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import boto3
from datetime import datetime

API_KEY = os.getenv("FRED_API_KEY")
BUCKET = os.getenv("S3_BUCKET")
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

INDICATORS = {
    "GDP": "Gross Domestic Product",
    "UNRATE": "Unemployment Rate",
    "CPIAUCSL": "Consumer Price Index",
    "FEDFUNDS": "Federal Funds Rate",
    "T10Y2Y": "10Y-2Y Treasury Spread",
    "HOUST": "Housing Starts",
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


def extract_indicator(session, series_id):
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 365,
    }
    response = session.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "error_code" in data:
        raise ValueError(f"API error for {series_id}: {data['error_message']}")

    return data


def upload_to_s3(data, series_id, execution_date):
    s3 = boto3.client("s3")
    key = f"raw/econ/{execution_date}/{series_id}.json"
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

    for series_id in INDICATORS:
        try:
            print(f"Extracting {series_id} ({INDICATORS[series_id]})...")
            data = extract_indicator(session, series_id)
            upload_to_s3(data, series_id, execution_date)
            results["success"].append(series_id)
            time.sleep(2)
        except Exception as e:
            print(f"Failed {series_id}: {e}")
            results["failed"].append({"series_id": series_id, "error": str(e)})

    print(f"Done. Success: {len(results['success'])}, Failed: {len(results['failed'])}")

    if results["failed"]:
        raise Exception(f"Failed indicators: {results['failed']}")

    return results


if __name__ == "__main__":
    run()