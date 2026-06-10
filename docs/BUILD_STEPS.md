# Full process used to build Project 2 - Financial Analytics Warehouse

# Create S3 Bucket
project2-bucket-edan

# Create Redshift Serverless (Public Access ON)

# Add GitHub Secrets:
# REDSHIFT_HOST, REDSHIFT_USER, REDSHIFT_PASSWORD

# Get API keys from Alpha Vantage and FRED

# Create project structure
mkdir -p project2-financial-analytics-warehouse/{dags,scripts,infra,tests,.github/workflows}
cd project2-financial-analytics-warehouse

# Python Env Setup
python3 -m venv venv
source venv/bin/activate

Create .gitignore
Create .env
Create Dockerfile
Create docker-compose.yml

# Create logs directory
mkdir -p logs
sudo chmod -R 777 logs

# Create Extraction & Load Scripts
Create scripts/extract_stocks.py
Create scripts/extract_econ.py
Create scripts/create_redshift_tables.py
Create scripts/load_to_redshift.py
Create scripts/__init__.py

# Install project dependencies
pip install -r requirements.txt

dbt init dbt_project
sudo rm -rf dbt_project/models/example/

# Create dbt Project Structure
mkdir -p dbt_project/models/staging
mkdir -p dbt_project/models/marts
mkdir -p dbt_project/snapshots
mkdir -p dbt_project/seeds
mkdir -p dbt_project/profiles
mkdir -p dbt_project/dbt_packages
mkdir -p dbt_project/logs
mkdir -p dbt_project/target

# Create Staging models
dbt_project/models/staging/sources.yml
dbt_project/models/staging/stg_stock_prices.sql
dbt_project/models/staging/stg_econ_indicators.sql
dbt_project/models/staging/schema.yml

# Create Mart models
dbt_project/models/marts/fct_daily_prices.sql
dbt_project/models/marts/fct_econ_readings.sql
dbt_project/models/marts/dim_time.sql
dbt_project/models/marts/dim_company.sql
dbt_project/models/marts/schema.yml

# Create Seeds and Snapshots
dbt_project/seeds/companies.csv
dbt_project/snapshots/snap_company.sql
dbt_project/packages.yml
dbt_project/profiles/profiles.yml

Update dbt_project/dbt_project.yml

# Install dbt packages
cd dbt_project
dbt deps
dbt compile
cd ..

# Create Airflow DAG
mkdir -p dags
Create dags/full_pipeline_dag.py

# Docker Setup
docker compose build
docker compose up airflow-init
docker compose up -d

# Permissions
docker compose exec -u root airflow-scheduler bash -c "chown -R 50000:0 /opt/airflow/dbt_project"

# Install dbt pacakges inside container
docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt_project && dbt deps --profiles-dir profiles"

# Create Redshift tables
python scripts/create_redshift_tables.py

# Access Airflow UI
http://localhost:8080

# SQL & Python Linting
sqlfluff lint dbt_project/models/
flake8 scripts/ dags/ --max-line-length=120

# Push to GitHub
git add .
git commit -m "Initial full build"
git push