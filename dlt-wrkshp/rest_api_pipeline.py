"""dlt REST API pipeline: load Claude Code agent logs from the test traces API into DuckDB."""

import argparse
from typing import Any

import dlt
from dlt.hub import run
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources


@dlt.source(name="agent_logs")
def agent_logs_source(base_url: str = dlt.config.value) -> Any:
    """Load fake Claude Code agent logs from the test traces API.

    Args:
        base_url: API base URL. Auto-loaded from .dlt/config.toml under [sources.agent_logs].
    """
    config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resources": [
            {
                "name": "logs",
                "primary_key": "uuid",
                "write_disposition": "replace",
                "endpoint": {
                    "path": "logs",
                    "data_selector": "logs",
                    "params": {
                        "limit": 1000,
                    },
                    "paginator": {
                        "type": "offset",
                        "limit": 1000,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "total_path": "total",
                        "stop_after_empty_page": True,
                    },
                },
            },
        ],
    }

    yield from rest_api_resources(config)


def load_agent_logs(full: bool = False) -> None:
    pipeline = dlt.pipeline(
        pipeline_name="agent_logs_pipeline",
        destination="playground",
        dataset_name="agent_logs",
        dev_mode=not full,
    )

    source = agent_logs_source()
    if not full:
        source.add_limit(1)

    load_info = pipeline.run(source)
    print(load_info)  # noqa: T201


@run.pipeline("agent_logs_pipeline")
def ingest_agent_logs() -> None:
    load_agent_logs(full=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="Load the full dataset (all ~1,000,000 rows) into the stable 'agent_logs' "
        "dataset. Without this flag, runs a single-page debug load into a fresh dev dataset.",
    )
    args = parser.parse_args()
    load_agent_logs(full=args.full)
