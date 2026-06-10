# Project 2 Steps

Create S3 Bucket
# project2-bucket-edan
Create Redshift Serverless (public accessible ON)
Get API Keys from Alpha Vantage and FRED

mkdir -p project2-financial-analytics-warehouse/{dags,scripts,infra,tests,.github/workflows}

python3 -m venv venv
source venv/bin/activate

Create .gitignore
Create .env
Create Dockerfile
Create docker-compose.yml

mkdir -p logs && sudo chmod -R 777 logs

Create scripts/extract_stocks.py
Create scripts/extract_econ.py
Create scripts/create_redshift_tables.py
Create scripts/load_to_redshift.py

pip install dbt-core dbt-redshift
dbt init dbt_project

mkdir -p dbt_project/models/staging
mkdir -p dbt_project/models/marts
mkdir -p dbt_project/snapshots
mkdir -p dbt_project/seeds
mkdir -p dbt_project/profiles

Create models/staging/sources.yml
Create models/staging/stg_stock_prices.sql
Create models/staging/stg_econ_indicators.sql
Create models/staging/schema.yml

Create models/marts/fct_daily_prices.sql
Create models/marts/fct_econ_readings/sq;
Create models/marts/dim_time.sql
Create models/marts/dim_company.sql
Create models/marts/schema.yml

Create dbt_project/packages.yml
Create dbt_project/snapshots/snap_company.sql
Create dbt_proejct/seeds/companies.csv
Create dbt_project/profiles/profiles.yml

Update dbt_project/dbt_project.yml
sudo rm -rf dbt_project/models/example/

mkdir -p dags
mkdir -p dbt_project/dbt_packages dbt_project/logs dbt_project/target

Create dags/full_pipeline_dag.py
Create scripts/__init__.py

docker compose build
docker compose up airflow-init
docker compose up -d

docker compose exec -u root airflow-scheduler bash -c "chown -R 50000:0 /opt/airflow/dbt_project"
docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt_project && dbt deps --profiles-dir profiles"

pip install python-dotenv
python scripts/create_redshift_tables.py

Airflow UI at localhost:8080