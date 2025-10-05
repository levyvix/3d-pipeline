# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a 4D data pipeline (**d**lt → **d**bt → **D**uckDB → **D**agster) for ingesting and transforming data from the FakeStore API. The pipeline extracts raw data using dlt, loads it into DuckDB, transforms it using dbt, and orchestrates everything with Dagster.

## Architecture

**Data Flow:**
1. **Extraction (dlt)**: `main.py` or Dagster asset uses dlt's REST API source to extract products, carts, and users from FakeStore API
2. **Loading**: Data loads into DuckDB database file `rest_api_fakestore.duckdb` in schema `rest_api_data`
3. **Transformation (dbt)**: dbt models in `dbt_project/fakestoreapi/models/` transform raw data into staging views and mart tables in schema `dbt_schema`
4. **Orchestration (Dagster)**: Dagster manages asset dependencies and pipeline execution

**Database Setup:**
- **Primary database**: DuckDB (local file at `/home/levi/3d-pipeline/rest_api_fakestore.duckdb`)
- **Alternative**: PostgreSQL supported via Docker Compose in `postgres_db/` (optional, not currently active)
- dlt destination: `"duckdb"` (configured in `main.py` line 20)
- dbt profile target: `duck` (configured in `profiles.yml` line 2)
- dlt writes to: `rest_api_data` schema
- dbt writes to: `dbt_schema` schema

**dbt Model Structure:**
- `models/staging/fakestore/`: Source definitions and staging views (stg_carts, stg_products, stg_users, stg_carts_products)
- `models/marts/`: Dimension and fact tables (dim_products, dim_users, fct_sales)
- Staging models materialized as views, marts as tables (configured in dbt_project.yml)

**Dagster Assets:**
- `dagster_pipeline/assets/extract.py`: dlt extraction asset (`fakestore_raw_data`)
- `dagster_pipeline/assets/transform.py`: dbt transformation assets (`dbt_fakestore`)
- Custom `FakestoreDbtTranslator` maps dbt source dependencies to dlt assets for proper lineage

## Common Commands

**Initial Setup:**
```bash
# Install dependencies
uv sync

# Install dbt packages
cd dbt_project/fakestoreapi && uv run dbt deps
```

**Dagster Orchestration (Recommended):**
```bash
# Start Dagster UI and daemon
dagster dev -m dagster_pipeline
# Opens at http://localhost:3000

# Materialize all assets (extract + transform)
dagster asset materialize --select '*' -m dagster_pipeline

# Materialize specific asset
dagster asset materialize --select fakestore_raw_data -m dagster_pipeline
dagster asset materialize --select dbt_fakestore -m dagster_pipeline
```

**Legacy Direct Execution:**
```bash
# Run dlt extraction and loading (without Dagster)
uv run python main.py

# Run dbt models
cd dbt_project/fakestoreapi && uv run dbt run

# Run specific dbt model
cd dbt_project/fakestoreapi && uv run dbt run --select stg_products

# Run dbt tests (data tests + unit tests)
cd dbt_project/fakestoreapi && uv run dbt test

# Run only unit tests (fast, no database)
cd dbt_project/fakestoreapi && uv run dbt test --select test_type:unit

# Run model and downstream dependencies
cd dbt_project/fakestoreapi && uv run dbt run --select stg_products+

# Build all models and run tests
cd dbt_project/fakestoreapi && uv run dbt build
```

**Database:**
```bash
# Query DuckDB
duckdb rest_api_fakestore.duckdb

# Optional: Start PostgreSQL (if switching from DuckDB)
cd postgres_db && docker-compose up -d
cd postgres_db && docker-compose down
```

## Key Files

- `main.py`: dlt pipeline configuration for FakeStore API ingestion (standalone mode)
- `dagster_pipeline/definitions.py`: Dagster pipeline definitions, resources, and jobs
- `dagster_pipeline/assets/extract.py`: dlt extraction asset wrapped for Dagster
- `dagster_pipeline/assets/transform.py`: dbt transformation assets with custom translator
- `dbt_project/fakestoreapi/profiles.yml`: dbt database connection settings (targets: `duck`, `dev`)
- `dbt_project/fakestoreapi/dbt_project.yml`: dbt project configuration and materialization settings
- `dbt_project/fakestoreapi/models/schema.yml`: Source definitions pointing to dlt-loaded tables
- `dbt_project/fakestoreapi/models/staging/fakestore/schema.yml`: Staging model tests (40 tests)
- `dbt_project/fakestoreapi/models/marts/schema.yml`: Mart model tests (16 tests)
- `rest_api_fakestore.duckdb`: DuckDB database file (created by dlt)

## Important Notes

- **dbt working directory**: Always run dbt commands from `dbt_project/fakestoreapi/`
- **Use `uv run`**: Always prefix Python/dbt commands with `uv run` to use project dependencies (not global installations)
- **Database**: Currently configured for DuckDB; PostgreSQL support available but not active
- **Data source**: FakeStore API endpoints: `/products` (20 items), `/carts` (7 items), `/users` (10 items)
- **dlt metadata**: Automatically creates `_dlt_id` and `_dlt_load_id` columns for lineage tracking
- **Write disposition**: dlt uses `replace` mode (full refresh on each run)
- **Tests**: Project includes 89 data tests + 8 unit tests across staging and mart layers
- **Dagster lineage**: Custom `FakestoreDbtTranslator` ensures dbt models depend on dlt assets in Dagster UI
