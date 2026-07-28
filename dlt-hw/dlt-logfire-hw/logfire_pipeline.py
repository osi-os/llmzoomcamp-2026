from typing import Any, Optional

import dlt
from dlt.common.pendulum import pendulum
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources


@dlt.source(name="logfire")
def logfire_source(
    read_token: str = dlt.secrets.value,
    min_timestamp: Optional[str] = None,
) -> Any:
    """Load trace/span data from Pydantic Logfire's Query API (US region).

    Args:
        read_token: Logfire read token (Logfire UI: Settings -> Read tokens,
            or `logfire read-tokens create`). Auto-loaded from secrets.toml.
        min_timestamp: ISO8601 lower bound applied to `start_timestamp`.
            Defaults to 7 days ago.

    Example:
        pipeline.run(logfire_source())
        pipeline.run(logfire_source(min_timestamp="2026-07-01T00:00:00Z"))
    """
    if min_timestamp is None:
        min_timestamp = pendulum.now("UTC").subtract(days=7).to_iso8601_string()

    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://logfire-us.pydantic.dev/v2/",
            "auth": {
                "type": "bearer",
                "token": read_token,
            },
            "headers": {
                "Accept": "application/json",
            },
        },
        "resources": [
            {
                "name": "records",
                "endpoint": {
                    "path": "query",
                    "method": "POST",
                    "json": {
                        "sql": "SELECT * FROM records",
                        "min_timestamp": min_timestamp,
                    },
                    "data_selector": "data",
                },
            },
        ],
    }

    yield from rest_api_resources(config)


def load_logfire() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="logfire",
        destination="duckdb",
        dataset_name="logfire_data",
        dev_mode=True,
    )

    load_info = pipeline.run(logfire_source().add_limit(1))
    print(load_info)  # noqa: T201


if __name__ == "__main__":
    load_logfire()
