"""sqlite-vec baseline.

vec0 virtual table for embeddings + a sister `kv` table for id -> value mapping.
Cosine via L2-normalized vectors (vec0 supports L2 distance natively).
"""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path

import numpy as np

from testbed.api import (
    AuditReport,
    DeletionCertificate,
    MemoryBackend,
    RetrievalResult,
)

try:
    import sqlite_vec  # type: ignore
except ImportError as exc:  # pragma: no cover
    sqlite_vec = None
    _IMPORT_ERR = exc
else:
    _IMPORT_ERR = None


def _require_sqlite_vec() -> None:
    if sqlite_vec is None:
        raise ImportError(
            "sqlite_vec not installed. Install with: pip install sqlite-vec==0.1.7a2"
        ) from _IMPORT_ERR


def _pack(vec: np.ndarray) -> bytes:
    v = np.ascontiguousarray(np.asarray(vec, dtype=np.float32).reshape(-1))
    return v.tobytes()


def _normalize(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float32).reshape(-1)
    n = float(np.linalg.norm(v))
    if n == 0.0:
        return v
    return v / n


class SqliteVecMemory(MemoryBackend):
    """sqlite-vec vec0 backend wrapped to the MemoryBackend ABC."""

    name = "sqlite_vec"

    def __init__(self, db_path: Path, dim: int) -> None:
        _require_sqlite_vec()
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.dim = int(dim)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        self._next_rowid: int = 0
        self._init_schema()
        self._load_next_rowid()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            f"CREATE VIRTUAL TABLE IF NOT EXISTS vec_items "
            f"USING vec0(embedding FLOAT[{self.dim}])"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS kv ("
            "rowid INTEGER PRIMARY KEY, "
            "key_id TEXT UNIQUE NOT NULL, "
            "value TEXT NOT NULL)"
        )
        cur.execute("CREATE INDEX IF NOT EXISTS kv_key_idx ON kv(key_id)")
        self.conn.commit()

    def _load_next_rowid(self) -> None:
        cur = self.conn.cursor()
        cur.execute("SELECT COALESCE(MAX(rowid), 0) FROM kv")
        row = cur.fetchone()
        self._next_rowid = int(row[0]) if row else 0

    def __len__(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM kv")
        return int(cur.fetchone()[0])

    def _next_id(self) -> int:
        self._next_rowid += 1
        return self._next_rowid

    def store(self, key_id: str, key_vec: np.ndarray, value: str) -> None:
        v = _normalize(key_vec)
        if v.shape[0] != self.dim:
            raise ValueError(
                f"sqlite_vec_adapter: vec dim {v.shape[0]} != configured dim {self.dim}"
            )
        cur = self.conn.cursor()
        cur.execute("SELECT rowid FROM kv WHERE key_id = ?", (key_id,))
        if cur.fetchone() is not None:
            raise KeyError(f"sqlite_vec_adapter: key_id {key_id!r} already stored")
        rid = self._next_id()
        cur.execute(
            "INSERT INTO vec_items(rowid, embedding) VALUES (?, ?)",
            (rid, _pack(v)),
        )
        cur.execute(
            "INSERT INTO kv(rowid, key_id, value) VALUES (?, ?, ?)",
            (rid, key_id, value),
        )
        self.conn.commit()

    def retrieve(self, query_vec: np.ndarray, k: int = 1) -> RetrievalResult:
        n = len(self)
        if n == 0:
            return RetrievalResult(
                key_id=None,
                value=None,
                confidence=0.0,
                near_uniform_flag=False,
                distance=None,
                top_k_ids=[],
                top_k_scores=[],
            )
        q = _normalize(query_vec)
        if q.shape[0] != self.dim:
            raise ValueError(
                f"sqlite_vec_adapter: query dim {q.shape[0]} != configured dim {self.dim}"
            )
        kk = max(1, min(k, n))
        cur = self.conn.cursor()
        cur.execute(
            "SELECT v.rowid, v.distance, kv.key_id, kv.value "
            "FROM vec_items v JOIN kv ON kv.rowid = v.rowid "
            "WHERE v.embedding MATCH ? AND k = ? "
            "ORDER BY v.distance",
            (_pack(q), kk),
        )
        rows = cur.fetchall()
        if not rows:
            return RetrievalResult(
                key_id=None,
                value=None,
                confidence=0.0,
                near_uniform_flag=False,
                distance=None,
                top_k_ids=[],
                top_k_scores=[],
            )
        top_ids = [r[2] for r in rows]
        top_dists = [float(r[1]) for r in rows]
        top_scores = [1.0 / (1.0 + d) for d in top_dists]
        best_id = top_ids[0]
        best_value = rows[0][3]
        best_dist = top_dists[0]
        return RetrievalResult(
            key_id=best_id,
            value=best_value,
            confidence=top_scores[0],
            near_uniform_flag=False,
            distance=best_dist,
            top_k_ids=top_ids,
            top_k_scores=top_scores,
        )

    def edit(self, key_id: str, new_value: str) -> None:
        cur = self.conn.cursor()
        cur.execute("UPDATE kv SET value = ? WHERE key_id = ?", (new_value, key_id))
        if cur.rowcount == 0:
            raise KeyError(f"sqlite_vec_adapter: edit on missing key_id {key_id!r}")
        self.conn.commit()

    def delete(self, key_id: str) -> DeletionCertificate:
        cur = self.conn.cursor()
        cur.execute("SELECT rowid FROM kv WHERE key_id = ?", (key_id,))
        row = cur.fetchone()
        existed = row is not None
        if existed:
            rid = int(row[0])
            cur.execute("DELETE FROM vec_items WHERE rowid = ?", (rid,))
            cur.execute("DELETE FROM kv WHERE rowid = ?", (rid,))
            self.conn.commit()
        return DeletionCertificate(
            key_id=key_id,
            var_ratio=None,
            erased=existed,
            timestamp_ns=time.time_ns(),
        )

    def audit(self) -> AuditReport:
        storage = self.db_path.stat().st_size if self.db_path.exists() else 0
        return AuditReport(
            backend=self.name,
            n_items=len(self),
            kf1_above_thresh_frac=None,
            kf1_mean_oos_max_conf=None,
            kf2_max_isolation=None,
            tcft_mean_var_ratio=None,
            storage_bytes=int(storage),
            config={"db_path": str(self.db_path), "dim": self.dim},
        )

    def save(self, path: Path) -> None:
        # The db file IS the persistence layer; just flush.
        try:
            self.conn.commit()
        except Exception:
            pass

    def load(self, path: Path) -> None:
        _require_sqlite_vec()
        try:
            self.conn.close()
        except Exception:
            pass
        self.db_path = Path(path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        self._init_schema()
        self._load_next_rowid()
