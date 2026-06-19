"""Append-only hash-chained audit log with JSON-lines persistence."""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Iterator


GENESIS_HASH = "sha256:" + "0" * 64


def _sha256_hex(payload: bytes) -> str:
    """SHA-256 hex digest with 'sha256:' prefix."""
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _canonical(obj: Any) -> bytes:
    """Deterministic JSON serialization for hashing/signing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


@dataclass
class AuditRecord:
    """A single audit log entry with hash-chain linkage."""

    id: str
    ts_ns: int
    operation: str
    request_payload: dict[str, Any]
    response_payload: dict[str, Any]
    latency_ms: float
    substrate_state_hash: str
    sha256_chain_prev: str = GENESIS_HASH
    sha256_self: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a dict copy suitable for JSON serialization."""
        return asdict(self)


class AuditLog:
    """Thread-safe append-only audit log with SHA-256 chain integrity."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path
        self._lock = threading.Lock()
        self._records: list[AuditRecord] = []
        self._index: dict[str, int] = {}
        self._last_hash: str = GENESIS_HASH
        if path is not None:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            if os.path.exists(path):
                self._load(path)

    def _load(self, path: str) -> None:
        """Replay existing JSONL file into memory."""
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                rec = AuditRecord(**data)
                self._records.append(rec)
                self._index[rec.id] = len(self._records) - 1
                self._last_hash = rec.sha256_self

    def append(
        self,
        operation: str,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
        latency_ms: float,
        substrate_state_hash: str,
    ) -> AuditRecord:
        """Append a new audit record; returns the persisted record with hashes set."""
        with self._lock:
            rec = AuditRecord(
                id="evt_" + uuid.uuid4().hex,
                ts_ns=time.time_ns(),
                operation=operation,
                request_payload=request_payload,
                response_payload=response_payload,
                latency_ms=latency_ms,
                substrate_state_hash=substrate_state_hash,
                sha256_chain_prev=self._last_hash,
            )
            body = {k: v for k, v in rec.to_dict().items() if k != "sha256_self"}
            rec.sha256_self = _sha256_hex(_canonical(body))
            self._records.append(rec)
            self._index[rec.id] = len(self._records) - 1
            self._last_hash = rec.sha256_self
            if self.path is not None:
                with open(self.path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec.to_dict(), default=str) + "\n")
            return rec

    def get(self, record_id: str) -> AuditRecord | None:
        """Look up an audit record by id."""
        idx = self._index.get(record_id)
        return self._records[idx] if idx is not None else None

    def list(
        self,
        filter_op: str | None = None,
        from_ts: int | None = None,
        to_ts: int | None = None,
    ) -> list[AuditRecord]:
        """Filter audit records by op name and ts_ns bounds."""
        out: list[AuditRecord] = []
        for rec in self._records:
            if filter_op is not None and rec.operation != filter_op:
                continue
            if from_ts is not None and rec.ts_ns < from_ts:
                continue
            if to_ts is not None and rec.ts_ns > to_ts:
                continue
            out.append(rec)
        return out

    def verify_chain(self) -> bool:
        """Verify hash-chain integrity for all stored records."""
        prev = GENESIS_HASH
        for rec in self._records:
            if rec.sha256_chain_prev != prev:
                return False
            body = {k: v for k, v in rec.to_dict().items() if k != "sha256_self"}
            expected = _sha256_hex(_canonical(body))
            if rec.sha256_self != expected:
                return False
            prev = rec.sha256_self
        return True

    def __len__(self) -> int:
        return len(self._records)

    def __iter__(self) -> Iterator[AuditRecord]:
        return iter(list(self._records))

    @property
    def head_hash(self) -> str:
        """Return current chain head hash."""
        return self._last_hash


def compute_state_hash(items: Iterable[tuple[str, list[float]]]) -> str:
    """Hash a snapshot of (atom_id, value-summary) pairs for substrate state."""
    summary: list[list[Any]] = []
    for atom_id, summary_vals in items:
        summary.append([atom_id, [round(float(v), 6) for v in summary_vals]])
    summary.sort(key=lambda r: r[0])
    return _sha256_hex(_canonical(summary))
