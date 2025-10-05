"""
Dagster pipeline for orchestrating the 4D data pipeline.

This package contains:
- Data extraction assets (dlt)
- Data transformation assets (dbt)
- DuckDB resource configuration
- Pipeline schedules
"""

from dagster_pipeline.definitions import defs

__all__ = ["defs"]
