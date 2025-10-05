"""
Main Dagster definitions for the 4D pipeline.

This module brings together all assets, resources, and schedules.
"""

from dagster import Definitions, load_assets_from_modules, define_asset_job, AssetSelection
from dagster_pipeline.assets import extract, transform
from dagster_pipeline.resources import get_dbt_resource, get_duckdb_resource

# Load all assets
all_assets = load_assets_from_modules([extract, transform])

# Define resources
resources = {
    "dbt": get_dbt_resource(),
    "duckdb": get_duckdb_resource(),
}

# Define jobs
fakestore_pipeline_job = define_asset_job(
    name="fakestore_pipeline",
    description="Full pipeline: Extract from FakeStore API → Transform with dbt",
    selection=AssetSelection.all(),
)

# Create Dagster definitions
defs = Definitions(
    assets=all_assets,
    jobs=[fakestore_pipeline_job],
    resources=resources,
)
