"""
Dagster resources for the 4D pipeline.
"""

from pathlib import Path
from dagster_dbt import DbtCliResource
from dagster_duckdb import DuckDBResource

# Path to DuckDB database
DUCKDB_PATH = Path(__file__).parent.parent / "rest_api_fakestore.duckdb"

# Path to dbt project
DBT_PROJECT_DIR = Path(__file__).parent.parent / "dbt_project" / "fakestoreapi"


def get_duckdb_resource() -> DuckDBResource:
    """
    Get DuckDB resource pointing to the pipeline database.
    """
    return DuckDBResource(database=str(DUCKDB_PATH))


def get_dbt_resource() -> DbtCliResource:
    """
    Get dbt CLI resource configured for the FakeStore project.
    """
    return DbtCliResource(
        project_dir=str(DBT_PROJECT_DIR),
        target="duck",
    )
