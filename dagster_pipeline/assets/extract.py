"""
Data extraction asset using dlt to fetch data from FakeStore API.
"""

import dlt
from dagster import asset, AssetExecutionContext
from dlt.sources.rest_api import rest_api_source


@asset(
    group_name="extraction",
    description="Extract products, carts, and users from FakeStore API using dlt and load into DuckDB",
    compute_kind="dlt",
)
def fakestore_raw_data(context: AssetExecutionContext) -> None:
    """
    Extracts data from FakeStore API and loads it into DuckDB.

    This asset wraps the dlt pipeline that:
    - Fetches products, carts, and users from FakeStore API
    - Loads data into rest_api_data schema in DuckDB
    - Uses replace write disposition for full refresh
    """
    context.log.info("Starting dlt extraction from FakeStore API")

    # Configure REST API source
    source = rest_api_source(
        {
            "client": {
                "base_url": "https://fakestoreapi.com",
            },
            "resources": [
                "products",
                "carts",
                "users",
            ],
        }
    )

    # Configure dlt pipeline
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_fakestore",
        destination="duckdb",
        dataset_name="rest_api_data",
    )

    # Run pipeline with replace mode
    load_info = pipeline.run(source, write_disposition="replace")

    context.log.info(f"dlt pipeline completed: {load_info}")
    context.log.info(f"Loaded {len(load_info.loads_ids)} load(s)")

    # Log table statistics
    for package in load_info.load_packages:
        for table in package.schema_update.get("tables", {}).keys():
            context.log.info(f"Loaded table: {table}")
