"""Dagster definitions for the 3D pipeline (dlt → dbt → DuckDB)."""

from pathlib import Path
from dagster import Definitions, load_assets_from_modules, define_asset_job, AssetSelection
from dagster_dbt import DbtCliResource
from dagster_duckdb import DuckDBResource
from dagster_embedded_elt.dlt import DagsterDltResource
from dagster_pipeline.assets import extract, transform

PIPELINE_ROOT = Path(__file__).parent.parent
DBT_PROJECT_DIR = PIPELINE_ROOT / "dbt_project" / "fakestoreapi"
DUCKDB_PATH = PIPELINE_ROOT / "rest_api_fakestore.duckdb"

defs = Definitions(
    assets=load_assets_from_modules([extract, transform]),
    jobs=[define_asset_job("fakestore_pipeline", selection=AssetSelection.all())],
    resources={
        "dlt": DagsterDltResource(),
        "duckdb": DuckDBResource(database=str(DUCKDB_PATH)),
        "dbt": DbtCliResource(project_dir=str(DBT_PROJECT_DIR), target="duck"),
    },
)
