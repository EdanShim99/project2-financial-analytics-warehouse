from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys

sys.path.insert(0, "/opt/airflow")

from scripts.extract_stocks import run as extract_stocks
from scripts.extract_econ import run as extract_econ

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def load_to_redshift(**kwargs):
    """Load S3 data into Redshift staging tables."""
    import boto3
    import json
    import psycopg2
    import os

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

    # Load stocks
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
                symbol, date,
                float(values['1. open']),
                float(values['2. high']),
                float(values['3. low']),
                float(values['4. close']),
                int(values['5. volume'])
            ))

    cur.execute("DELETE FROM staging.stock_prices;")
    for i in range(0, len(rows), 500):
        batch = rows[i:i+500]
        args = ','.join(
            cur.mogrify("(%s,%s,%s,%s,%s,%s,%s)", row).decode()
            for row in batch
        )
        cur.execute(f"INSERT INTO staging.stock_prices (symbol, date, open_price, high_price, low_price, close_price, volume) VALUES {args}")
    print(f"Loaded {len(rows)} stock rows")

    # Load econ
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
            rows.append((series_id, obs['date'], float(obs['value'])))

    cur.execute("DELETE FROM staging.econ_indicators;")
    for i in range(0, len(rows), 500):
        batch = rows[i:i+500]
        args = ','.join(
            cur.mogrify("(%s,%s,%s)", row).decode()
            for row in batch
        )
        cur.execute(f"INSERT INTO staging.econ_indicators (series_id, date, value) VALUES {args}")
    print(f"Loaded {len(rows)} econ rows")

    cur.close()
    conn.close()


with DAG(
    dag_id="full_pipeline",
    default_args=default_args,
    description="Full ELT pipeline: extract, load to Redshift, transform with dbt",
    schedule="0 18 * * 1-5",
    start_date=datetime(2026, 5, 1),
    catchup=False,
    tags=["pipeline", "stocks", "econ"],
) as dag:

    extract_stock_data = PythonOperator(
        task_id="extract_stocks",
        python_callable=extract_stocks,
        op_kwargs={"execution_date": "{{ ds }}"},
    )

    extract_econ_data = PythonOperator(
        task_id="extract_econ",
        python_callable=extract_econ,
        op_kwargs={"execution_date": "{{ ds }}"},
    )

    load_data = PythonOperator(
        task_id="load_to_redshift",
        python_callable=load_to_redshift,
    )

    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command="cd /opt/airflow/dbt_project && dbt seed --profiles-dir profiles",
    )

    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command="cd /opt/airflow/dbt_project && dbt snapshot --profiles-dir profiles",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt_project && dbt run --profiles-dir profiles",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt_project && dbt test --profiles-dir profiles",
    )

    [extract_stock_data, extract_econ_data] >> load_data >> dbt_seed >> dbt_snapshot >> dbt_run >> dbt_test