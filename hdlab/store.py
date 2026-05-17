"""Persistent trace storage backed by DuckDB."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb

from .tracing import TraceEvent


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
    step BIGINT PRIMARY KEY,
    op VARCHAR NOT NULL,
    inputs_json VARCHAR NOT NULL,
    output_json VARCHAR NOT NULL,
    modulator_state_json VARCHAR NOT NULL,
    timestamp_ns BIGINT NOT NULL,
    elapsed_ns BIGINT NOT NULL,
    query_id VARCHAR,
    tags_json VARCHAR
);
CREATE INDEX IF NOT EXISTS idx_events_op ON events (op);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events (timestamp_ns);
CREATE INDEX IF NOT EXISTS idx_events_query ON events (query_id);
"""


class TraceStore:
    """Indexed, queryable persistence for trace events."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path) if path != ":memory:" else path
        self._conn = duckdb.connect(str(self.path))
        self._conn.execute(SCHEMA_SQL)

    def append(self, events: list[TraceEvent]) -> None:
        """Persist a batch of events."""
        if not events:
            return
        rows = [
            (
                e.step,
                e.op,
                json.dumps(e.inputs),
                json.dumps(e.output),
                json.dumps(e.modulator_state),
                e.timestamp_ns,
                e.elapsed_ns,
                e.query_id,
                json.dumps(e.tags),
            )
            for e in events
        ]
        self._conn.executemany(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )

    def query(self, sql: str) -> list[dict[str, Any]]:
        """Run an arbitrary SQL query and return rows as dicts."""
        cur = self._conn.execute(sql)
        if cur.description is None:
            return []
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def all_events(self) -> list[TraceEvent]:
        """Return every persisted event, ordered by step."""
        rows = self.query("SELECT * FROM events ORDER BY step")
        return [
            TraceEvent(
                step=r["step"],
                op=r["op"],
                inputs=json.loads(r["inputs_json"]),
                output=json.loads(r["output_json"]),
                modulator_state=json.loads(r["modulator_state_json"]),
                timestamp_ns=r["timestamp_ns"],
                elapsed_ns=r["elapsed_ns"],
                query_id=r.get("query_id"),
                tags=json.loads(r["tags_json"]) if r.get("tags_json") else {},
            )
            for r in rows
        ]

    def count(self) -> int:
        rows = self.query("SELECT COUNT(*) AS n FROM events")
        return int(rows[0]["n"]) if rows else 0

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "TraceStore":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
