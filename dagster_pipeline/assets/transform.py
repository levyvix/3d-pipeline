"""Transform raw data using dbt (staging and mart models)."""

from pathlib import Path
from typing import Any, Mapping
from dagster import AssetExecutionContext, AssetKey, AssetDep, AssetSpec
from dagster_dbt import DbtCliResource, dbt_assets, DbtProject, DagsterDbtTranslator

DBT_PROJECT_DIR = Path(__file__).parent.parent.parent / "dbt_project" / "fakestoreapi"
dbt_project = DbtProject(project_dir=DBT_PROJECT_DIR, target="duck")


class FakestoreDbtTranslator(DagsterDbtTranslator):
    """Map dbt source tables to dlt asset dependencies."""

    def get_asset_spec(self, manifest: Mapping[str, Any], unique_id: str, project=None) -> AssetSpec:
        default_spec = super().get_asset_spec(manifest, unique_id, project)

        dbt_node = manifest["nodes"].get(unique_id)
        if not dbt_node:
            return default_spec
        if dbt_node.get("resource_type") != "model":
            return default_spec

        # Find all fakestore source dependencies for this model
        dependencies = dbt_node.get("depends_on", {}).get("nodes", [])
        dlt_assets = []

        for dep in dependencies:
            if not dep.startswith("source.fakestoreapi.fakestore."):
                continue

            # Extract table name: "source.fakestoreapi.fakestore.products" → "products"
            table_name = dep.split(".")[-1]

            # Map child tables to their parent: "carts__products" → "carts"
            if "__" in table_name:
                table_name = table_name.split("__")[0]

            dlt_assets.append(AssetKey(["fakestore", table_name]))

        if not dlt_assets:
            return default_spec

        # Add dlt assets as upstream dependencies
        new_deps = list(default_spec.deps or [])
        for asset_key in dlt_assets:
            new_deps.append(AssetDep(asset_key))

        return default_spec._replace(deps=new_deps)


@dbt_assets(manifest=dbt_project.manifest_path, project=dbt_project, dagster_dbt_translator=FakestoreDbtTranslator())
def dbt_fakestore_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """Run dbt models: staging (stg_*) and marts (dim_*, fct_*)."""
    yield from dbt.cli(["build"], context=context).stream()
