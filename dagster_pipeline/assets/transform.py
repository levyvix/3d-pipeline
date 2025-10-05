"""
Data transformation assets using dbt to transform raw data into staging and mart models.
"""

from pathlib import Path
from typing import Any, Mapping
from dagster import AssetExecutionContext, AssetKey, AssetDep, AssetSpec
from dagster_dbt import DbtCliResource, dbt_assets, DbtProject, DagsterDbtTranslator

# Get the dbt project path
DBT_PROJECT_DIR = Path(__file__).parent.parent.parent / "dbt_project" / "fakestoreapi"

# Define the dbt project
dbt_project = DbtProject(
    project_dir=DBT_PROJECT_DIR,
    target="duck",
)


class CustomDagsterDbtTranslator(DagsterDbtTranslator):
    """Custom translator to add extraction asset as upstream dependency."""

    def get_asset_spec(self, manifest: Mapping[str, Any], unique_id: str, project = None) -> AssetSpec:
        """Add fakestore_raw_data as upstream dependency for models that use fakestore sources."""
        default_spec = super().get_asset_spec(manifest, unique_id, project)

        # Get the dbt node from manifest
        dbt_node = manifest["nodes"].get(unique_id) or manifest["sources"].get(unique_id)

        # Only process model nodes
        if not dbt_node or dbt_node.get("resource_type") != "model":
            return default_spec

        # Check if this model depends on fakestore sources
        node_list = dbt_node.get("depends_on", {}).get("nodes", [])
        depends_on_fakestore = False
        for node in node_list:
            if "source.fakestoreapi.fakestore" in node:
                depends_on_fakestore = True
                break

        # If no fakestore dependency, return default spec
        if not depends_on_fakestore:
            return default_spec

        # Add extraction asset as upstream dependency
        updated_deps = list(default_spec.deps or [])
        updated_deps.append(AssetDep(AssetKey(["fakestore_raw_data"])))

        return default_spec._replace(deps=updated_deps)


@dbt_assets(
    manifest=dbt_project.manifest_path,
    project=dbt_project,
    dagster_dbt_translator=CustomDagsterDbtTranslator(),
)
def dbt_fakestore_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """
    dbt models for FakeStore data transformation.

    This asset represents all dbt models in the project:
    - Staging layer: stg_products, stg_users, stg_carts, stg_carts_products
    - Mart layer: dim_products, dim_users, fct_sales

    The dbt DAG automatically handles dependencies between models.
    Depends on fakestore_raw_data extraction asset.
    """
    yield from dbt.cli(["build"], context=context).stream()
