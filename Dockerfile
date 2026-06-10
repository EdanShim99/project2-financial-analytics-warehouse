FROM apache/airflow:2.9.1-python3.12

USER airflow

RUN pip install --no-cache-dir \
    --only-binary=grpcio,cryptography \
    requests \
    boto3 \
    apache-airflow-providers-amazon \
    psycopg2-binary \
    python-dotenv \
    dbt-core==1.8.1 \
    dbt-redshift==1.8.1

RUN mkdir -p /opt/airflow/dbt_project/logs /opt/airflow/dbt_project/target /opt/airflow/dbt_project/dbt_packages && \
    chown -R 50000:0 /opt/airflow/dbt_project