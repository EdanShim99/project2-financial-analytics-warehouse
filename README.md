# Financial Analytics Data Warehouse
An end-to-end data engineering pipeline that ingests financial and macroeconomic data, loads it into Amazon Redshift, transforms it using dbt, and orchestrates workflows with Apache Airflow.

# Overview
This project demonstrates:
- API data extraction (Alpha Vantage, FRED)
- Data loading into Amazon Redshift Serverless
- dbt transformations using staging and marts layers
- Snapshot modeling for historical tracking
- Dockerized Airflow orchestration
- Automated CI validation with GitHub Actions
- SQL linting (SQLFluff) and Python linting (flake8)

# Architecture
APIs -> Python ETL -> Redshift -> dbt -> Airflow -> GitHub Actions (CI)

# Tech Stack
- Python
- Amazon Redshift Serverless
- dbt
- Apache Airflow (Docker)
- SQLFluff
- GitHub Actions

# Continuous Integration
On every push, GitHub Actions:
- Installs project dependencies
- Runs Python linting
- Runs SQL linting with the dbt templater
- Compiles the dbt project using a CI target
This ensures the project builds cleanly and remains reproducible.