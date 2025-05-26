import dlt
from dlt.sources.rest_api import rest_api_source


source = rest_api_source(
    {
        "client": {
            "base_url": "https://fakestoreapi.com",
        },
        "resources": [
            "products",
            "carts",
            "users",
        ],
    }
)

pipeline = dlt.pipeline(
    pipeline_name="rest_api_fakestore",
    destination="duckdb",
    dataset_name="rest_api_data",
)

load_info = pipeline.run(source)
print(load_info)  # noqa: T201
