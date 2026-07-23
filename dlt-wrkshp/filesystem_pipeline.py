"""dlt filesystem pipeline: load local Claude Code session logs (JSONL) into DuckDB."""

import hashlib
import json

import dlt
from dlt.sources.filesystem import filesystem, read_jsonl


def ensure_uuid(record: dict) -> dict:
    """Some record types (e.g. permission-mode, file-history-snapshot) have no uuid.

    merge on primary_key="uuid" requires a non-null value, so synthesize a
    deterministic id from the record content for rows that lack one.
    """
    if not record.get("uuid"):
        record["uuid"] = hashlib.sha1(
            json.dumps(record, sort_keys=True, default=str).encode()
        ).hexdigest()
    return record


def normalize_answers(record: dict) -> dict:
    """toolUseResult.answers is a dict keyed by the literal question text, which
    would make dlt mint one new column per distinct question ever asked. Convert
    it to a bounded list of {question, answer} pairs (a child table) instead.
    """
    tool_use_result = record.get("toolUseResult")
    if isinstance(tool_use_result, dict):
        answers = tool_use_result.get("answers")
        if isinstance(answers, dict):
            tool_use_result["answers"] = [
                {"question": question, "answer": answer}
                for question, answer in answers.items()
            ]
    return record


def load_logs() -> None:
    """Load Claude Code session log files into DuckDB.

    bucket_url is read from .dlt/config.toml under [sources.filesystem].
    file_glob is set inline so it lives next to the code that depends on it.
    """
    pipeline = dlt.pipeline(
        pipeline_name="claude_logs_pipeline",
        destination="duckdb",
        dataset_name="claude_logs",
    )

    reader = (
        filesystem(
            file_glob="**/*.jsonl",
            incremental=dlt.sources.incremental("modification_date"),
        )
        | read_jsonl()
    ).with_name("logs")
    reader.add_map(normalize_answers)
    reader.add_map(ensure_uuid)
    reader.apply_hints(primary_key="uuid")

    load_info = pipeline.run(reader, write_disposition="merge")
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    load_logs()
