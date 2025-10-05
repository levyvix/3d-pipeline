"""
Dagster assets for the 4D pipeline.
"""

from dagster_pipeline.assets.extract import fakestore_assets
from dagster_pipeline.assets.transform import dbt_fakestore_assets

__all__ = ["fakestore_assets", "dbt_fakestore_assets"]
