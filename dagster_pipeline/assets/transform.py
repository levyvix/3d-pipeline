"""Transform raw data using dbt (staging and mart models)."""

from pathlib import Path
from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets, DbtProject, DagsterDbtTranslator


DBT_PROJECT_DIR = Path(__file__).parent.parent.parent / "dbt_project" / "fakestoreapi"
dbt_project = DbtProject(project_dir=DBT_PROJECT_DIR, target="duck")




@dbt_assets(
    manifest=dbt_project.manifest_path,
    project=dbt_project,
)
def dbt_fakestore_assets(
    context: AssetExecutionContext,
    dbt: DbtCliResource,
):
    """Run dbt models: staging (stg_*) and marts (dim_*, fct_*)."""
    yield from dbt.cli(["build"], context=context).stream()
