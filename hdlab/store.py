"""Persistent trace storage backed by DuckDB over Parquet files."""

from __future__ import annotations

from pathlib import Path

from .tracing import TraceEvent


class TraceStore:
    """Indexed, queryable persistence for trace events."""

    def __init__(self, path: Path) -> None:
        raise NotImplementedError("Week 4")

    def append(self, events: list[TraceEvent]) -> None:
        """Persist a batch of events."""
        raise NotImplementedError("Week 4")

    def query(self, sql: str) -> list[dict]:
        """Run a SQL query against the trace store."""
        raise NotImplementedError("Week 4")
