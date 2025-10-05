# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a 3D data pipeline (**d**lt → **d**bt → **D**uckDB) for ingesting and transforming data from the FakeStore API. The pipeline extracts raw data using dlt, loads it into a database (supports both DuckDB and PostgreSQL), and transforms it using dbt into staging and mart models.

## Architecture

**Data Flow:**
1. **Extraction (dlt)**: `main.py` uses dlt's REST API source to extract products, carts, and users from FakeStore API
2. **Loading**: Data loads into database (`dlt_data.rest_api_data` schema) - supports DuckDB or PostgreSQL
3. **Transformation (dbt)**: dbt models in `dbt_project/fakestoreapi/models/` transform raw data into staging views and mart tables

**Database Setup:**
- Project supports both DuckDB and PostgreSQL (see dependencies in `pyproject.toml`)
- Current configuration uses PostgreSQL via Docker Compose in `postgres_db/`
- dlt destination configured in `main.py` (currently set to "postgres")
- dbt connection configured in `dbt_project/fakestoreapi/profiles.yml` (currently postgres: host: localhost, user: loader, password: 123)
- dlt writes to: `dlt_data.rest_api_data` schema
- dbt writes to: `dlt_data.dbt_schema` schema

**dbt Model Structure:**
- `models/staging/fakestore/`: Source definitions and staging views (stg_carts, stg_products, stg_users, stg_carts_products)
- `models/marts/`: Dimension and fact tables (dim_products, dim_users, fct_sales)
- Staging models materialized as views, marts as tables (configured in dbt_project.yml)

## Common Commands

**Database:**
```bash
# Start Postgres database
cd postgres_db && docker-compose up -d

# Stop database
cd postgres_db && docker-compose down
```

**Data Pipeline:**
```bash
# Run dlt extraction and loading
python main.py

# Run all dbt models
cd dbt_project/fakestoreapi && dbt run

# Run specific dbt model
cd dbt_project/fakestoreapi && dbt run --select stg_products

# Run dbt tests
cd dbt_project/fakestoreapi && dbt test

# Run model and downstream dependencies
cd dbt_project/fakestoreapi && dbt run --select stg_products+
```

**Development:**
```bash
# Install dependencies (UV)
uv sync

# Run Python scripts with UV
uv run python main.py

# Run any command in the virtual environment
uv run <command>

# Activate virtual environment manually (if needed)
source .venv/bin/activate
```

## Key Files

- `main.py`: dlt pipeline configuration for FakeStore API ingestion
- `dbt_project/fakestoreapi/profiles.yml`: dbt database connection settings
- `dbt_project/fakestoreapi/models/schema.yml`: Source definitions pointing to dlt-loaded tables
- `.env`: Contains `POSTGRES_PASSW` environment variable

## Notes

- The dbt project working directory is `dbt_project/fakestoreapi/` - always run dbt commands from there
- Source data comes from FakeStore API endpoints: /products, /carts, /users
- dlt automatically creates `_dlt_id` and `_dlt_load_id` columns for lineage tracking
