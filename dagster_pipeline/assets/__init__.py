"""
Dagster assets for the 4D pipeline.
"""

from dagster_pipeline.assets.extract import fakestore_raw_data
from dagster_pipeline.assets.transform import dbt_fakestore_assets

__all__ = ["fakestore_raw_data", "dbt_fakestore_assets"]
