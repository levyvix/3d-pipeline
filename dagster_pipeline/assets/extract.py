"""Extract data from FakeStore API using dlt."""

import dlt
from dlt.sources.rest_api import rest_api_source
from dagster import AssetExecutionContext, AssetKey
from dagster_embedded_elt.dlt import (
    DagsterDltResource,
    DagsterDltTranslator,
    dlt_assets,
)


class FakestoreDltTranslator(DagsterDltTranslator):
    """Create nested asset keys: products → ['fakestore', 'products']."""

    def get_asset_spec(self, data):
        default_spec = super().get_asset_spec(data)
        return default_spec._replace(key=AssetKey(["fakestore", data.resource.name]))


@dlt_assets(
    dlt_source=rest_api_source(
        {
            "client": {"base_url": "https://fakestoreapi.com"},
            "resource_defaults": {
                "write_disposition": "replace",
            },
            "resources": ["products", "carts", "users"],
        }
    ),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="rest_api_fakestore",
        destination="duckdb",
        dataset_name="rest_api_data",
    ),
    name="fakestore",
    group_name="extraction",
    dagster_dlt_translator=FakestoreDltTranslator(),
)
def fakestore_assets(context: AssetExecutionContext, dlt: DagsterDltResource):
    """Extract products, carts, and users from FakeStore API into DuckDB."""
    yield from dlt.run(context=context)
