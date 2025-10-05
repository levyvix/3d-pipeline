# 4D Data Pipeline (**d**lt -> **d**bt -> **D**uckDB -> **D**agster)

A complete orchestrated data pipeline for ingesting and transforming data from the FakeStore API using modern data stack tools.

## Architecture

```
FakeStore API -> dlt (Extract & Load) -> DuckDB -> dbt (Transform) -> Analytics-Ready Tables
                                            ^
                                            |
                                      Dagster (Orchestration)
```

### Components

- **dlt**: Extracts data from FakeStore API and loads into DuckDB
- **dbt**: Transforms raw data into staging and mart models
- **DuckDB**: Local analytical database
- **Dagster**: Orchestrates the pipeline with scheduling, monitoring, and observability

### Data Flow

1. **Extract**: dlt's REST API source fetches products, users, and carts from FakeStore API
2. **Load**: Data loads into `rest_api_fakestore.duckdb` database (schema: `rest_api_data`)
3. **Transform**: dbt models create staging views and mart tables
4. **Orchestrate**: Dagster manages asset dependencies, schedules, and pipeline execution

## Project Structure

```
|-- dagster_pipeline/                # Dagster orchestration
|   |-- __init__.py
|   |-- definitions.py               # Main Dagster definitions
|   |-- resources.py                 # DuckDB & dbt resources
|   |-- assets/
|   |   |-- extract.py               # dlt extraction asset
|   |   `-- transform.py             # dbt transformation assets
|-- main.py                          # dlt pipeline configuration (legacy)
|-- dbt_project/
|   `-- fakestoreapi/
|       |-- models/
|       |   |-- staging/
|       |   |   `-- fakestore/       # Staging models (views)
|       |   |       |-- stg_products.sql
|       |   |       |-- stg_users.sql
|       |   |       |-- stg_carts.sql
|       |   |       |-- stg_carts_products.sql
|       |   |       `-- schema.yml   # Staging tests
|       |   |-- marts/               # Mart models (tables)
|       |   |   |-- dim_products.sql
|       |   |   |-- dim_users.sql
|       |   |   |-- fct_sales.sql
|       |   |   `-- schema.yml       # Mart tests
|       |   `-- schema.yml           # Source definitions & tests
|       |-- profiles.yml             # dbt database connections
|       |-- dbt_project.yml          # dbt project config
|       `-- packages.yml             # dbt packages (dbt_utils)
|-- postgres_db/                     # PostgreSQL Docker setup (optional)
`-- rest_api_fakestore.duckdb        # DuckDB database file
```

## Setup

### Prerequisites

- Python 3.8+
- [UV](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Install dependencies
uv sync

# Install dbt packages
cd dbt_project/fakestoreapi
uv run dbt deps
```

## Usage

### 1. Extract and Load Data

Run the dlt pipeline to fetch data from FakeStore API:

```bash
uv run python main.py
```

This creates/replaces data in `rest_api_fakestore.duckdb` with the latest data from:
- `/products` endpoint (20 products)
- `/users` endpoint (10 users)
- `/carts` endpoint (7 carts with line items)

### 2. Transform Data

Run dbt to build staging views and mart tables:

```bash
cd dbt_project/fakestoreapi

# Build all models and run tests
uv run dbt build

# Or run models and tests separately
uv run dbt run    # Build models
uv run dbt test   # Run data quality tests
```

### 3. Query Analytics Tables

```bash
# Open DuckDB CLI
duckdb rest_api_fakestore.duckdb

# Query mart tables
SELECT * FROM dbt_schema.dim_products;
SELECT * FROM dbt_schema.dim_users;
SELECT * FROM dbt_schema.fct_sales;
```

## dbt Models

### Staging Layer (`models/staging/fakestore/`)

Staging views clean and rename raw source columns:

- **stg_products**: Product catalog with renamed columns
- **stg_users**: User information with flattened address fields
- **stg_carts**: Cart transactions with timestamps
- **stg_carts_products**: Cart line items (junction table)

### Mart Layer (`models/marts/`)

Analytics-ready dimension and fact tables:

- **dim_products**: Product dimension (20 products)
  - Columns: product_id, product_name, product_price, product_category, product_rating, etc.

- **dim_users**: User dimension (10 users)
  - Columns: user_id, email, username, first_name, last_name, address fields

- **fct_sales**: Sales fact table (cart line items)
  - Columns: cart_id, user_id, product_id, ordered_at, product_quantity, product_price, total_price
  - Grain: One row per product per cart

## Data Quality Tests

The project includes comprehensive data quality tests:

### Data Tests (89 tests)

Traditional dbt tests that run against the database:

- **Source tests** (33): Validate raw data integrity
  - Uniqueness on IDs
  - Not null constraints
  - Referential integrity
  - Accepted values for categories

- **Staging tests** (40): Ensure clean staging layer
  - All source tests plus transformations
  - Positive values for prices and quantities
  - Rating bounds (0-5)

- **Mart tests** (16): Business logic validation
  - Dimensional integrity
  - Fact table calculations (total_price = price � quantity)
  - Foreign key relationships

### Unit Tests (8 tests)

Fast, isolated tests using mock data (no database required):

- **stg_products** (2 tests):
  - Column renaming transformation
  - Null rating handling

- **stg_users** (2 tests):
  - User data restructuring
  - Missing address data handling

- **stg_carts_products** (2 tests):
  - Cart line item mapping
  - Quantity value handling

- **fct_sales** (2 tests):
  - Total price calculation logic
  - Multiple products per cart

### Running Tests

```bash
cd dbt_project/fakestoreapi

# Run all tests (data tests + unit tests)
uv run dbt test

# Run only unit tests (fast, no DB connection needed)
uv run dbt test --select test_type:unit

# Run only data tests (requires database)
uv run dbt test --select test_type:data

# Run tests for specific model
uv run dbt test --select stg_products
```

### Important Note: Using dbt-core

This project has **dbt-core** installed via `uv`, but you may have **dbt-fusion** installed globally. Always use `uv run dbt` to ensure you're using the correct dbt version from the project environment:

```bash
# ✅ Correct - uses project's dbt-core
uv run dbt test

# ❌ May use global dbt-fusion instead
dbt test
```

## Database Support

### DuckDB (Default)

The project uses DuckDB for fast local analytics:

```bash
# Default target in profiles.yml
uv run dbt run --target duck
```

### PostgreSQL (Alternative)

PostgreSQL is also supported via Docker:

```bash
# Start PostgreSQL
cd postgres_db
docker-compose up -d

# Update main.py to use postgres destination
# destination="postgres" in main.py

# Run dbt with postgres profile
uv run dbt run --target dev
```

## Configuration

### dlt Configuration (`main.py`)

- **Write disposition**: `replace` (full refresh on each run)
- **Destination**: DuckDB (change to `"postgres"` for PostgreSQL)
- **Dataset name**: `rest_api_data`

### dbt Configuration

- **Profiles** (`profiles.yml`): Database connections
  - `duck` target: DuckDB at `/home/levi/3d-pipeline/rest_api_fakestore.duckdb`
  - `dev` target: PostgreSQL (localhost:5432)

- **Project** (`dbt_project.yml`): Model materializations
  - Staging: `view`
  - Marts: `table`

## Common Commands

### Dagster Orchestration (Recommended)

```bash
# Start Dagster web UI and daemon
dagster dev -m dagster_pipeline
# Opens UI at http://localhost:3000

# Materialize all assets (via UI or CLI)
dagster asset materialize --select '*' -m dagster_pipeline

# Materialize specific asset
dagster asset materialize --select fakestore_raw_data -m dagster_pipeline
```

### Legacy Commands (Direct Execution)

```bash
# Full pipeline refresh
uv run python main.py                                    # Extract & load
cd dbt_project/fakestoreapi && uv run dbt build         # Transform & test

# dbt model operations
uv run dbt run --select stg_products                    # Run specific model
uv run dbt run --select stg_products+                   # Run model + downstream
uv run dbt test --select stg_products                   # Test specific model

# Database operations
duckdb rest_api_fakestore.duckdb                        # Open DuckDB CLI
cd postgres_db && docker-compose up -d                  # Start PostgreSQL
cd postgres_db && docker-compose down                   # Stop PostgreSQL
```

## Data Lineage

```
Dagster Asset: fakestore_raw_data
    |
    v
Sources (rest_api_data schema)
|-- products
|-- users
|-- carts
`-- carts__products
    |
    v
Dagster Asset: dbt_fakestore (Staging)
    |
    v
Staging (dbt_schema, views)
|-- stg_products
|-- stg_users
|-- stg_carts
`-- stg_carts_products
    |
    v
Dagster Asset: dbt_fakestore (Marts)
    |
    v
Marts (dbt_schema, tables)
|-- dim_products
|-- dim_users
`-- fct_sales

## Example Queries

```sql
-- Top selling products
SELECT
    p.product_name,
    p.product_category,
    SUM(s.product_quantity) as total_quantity_sold,
    SUM(s.total_price) as total_revenue
FROM dbt_schema.fct_sales s
JOIN dbt_schema.dim_products p ON s.product_id = p.product_id
GROUP BY p.product_name, p.product_category
ORDER BY total_revenue DESC
LIMIT 10;

-- Customer purchase summary
SELECT
    u.username,
    u.email,
    COUNT(DISTINCT s.cart_id) as num_orders,
    SUM(s.total_price) as total_spent
FROM dbt_schema.fct_sales s
JOIN dbt_schema.dim_users u ON s.user_id = u.user_id
GROUP BY u.username, u.email
ORDER BY total_spent DESC;

-- Sales by category
SELECT
    p.product_category,
    COUNT(DISTINCT s.cart_id) as num_orders,
    SUM(s.product_quantity) as items_sold,
    SUM(s.total_price) as revenue
FROM dbt_schema.fct_sales s
JOIN dbt_schema.dim_products p ON s.product_id = p.product_id
GROUP BY p.product_category
ORDER BY revenue DESC;
```

## License

This project is for educational purposes, using the public [FakeStore API](https://fakestoreapi.com/).
