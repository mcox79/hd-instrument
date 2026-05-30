"""Chroma baseline.

PersistentClient with a single collection. Distance is squared L2 by default;
we surface confidence = 1 / (1 + distance) so closer matches score higher.
"""

from __future__ import annotations

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
    import chromadb  # type: ignore
except ImportError as exc:  # pragma: no cover
    chromadb = None
    _IMPORT_ERR = exc
else:
    _IMPORT_ERR = None


def _require_chroma() -> None:
    if chromadb is None:
        raise ImportError(
            "chromadb not installed. Install with: pip install chromadb==0.5.20"
        ) from _IMPORT_ERR


def _dir_size_bytes(p: Path) -> int:
    if not p.exists():
        return 0
    total = 0
    for child in p.rglob("*"):
        if child.is_file():
            try:
                total += child.stat().st_size
            except OSError:
                pass
    return total


class ChromaMemory(MemoryBackend):
    """Chroma PersistentClient wrapped to the MemoryBackend ABC."""

    name = "chroma"

    def __init__(
        self,
        persist_dir: Path,
        collection_name: str = "testbed",
        dim: int | None = None,
    ) -> None:
        _require_chroma()
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.dim = dim
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        # cosine collection if available, else default L2
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def __len__(self) -> int:
        try:
            return int(self.collection.count())
        except Exception:
            return 0

    def store(self, key_id: str, key_vec: np.ndarray, value: str) -> None:
        v = np.asarray(key_vec, dtype=np.float32).reshape(-1)
        if self.dim is None:
            self.dim = int(v.shape[0])
        self.collection.add(
            ids=[key_id],
            embeddings=[v.tolist()],
            documents=[value],
        )

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
        q = np.asarray(query_vec, dtype=np.float32).reshape(-1)
        kk = max(1, min(k, n))
        res = self.collection.query(
            query_embeddings=[q.tolist()],
            n_results=kk,
        )
        ids_lists = res.get("ids") or [[]]
        dist_lists = res.get("distances") or [[]]
        doc_lists = res.get("documents") or [[]]
        ids_row = ids_lists[0] if ids_lists else []
        dist_row = dist_lists[0] if dist_lists else []
        docs_row = doc_lists[0] if doc_lists else []
        if not ids_row:
            return RetrievalResult(
                key_id=None,
                value=None,
                confidence=0.0,
                near_uniform_flag=False,
                distance=None,
                top_k_ids=[],
                top_k_scores=[],
            )
        top_ids = list(ids_row)
        top_scores = [float(1.0 / (1.0 + float(d))) for d in dist_row]
        best = top_ids[0]
        best_score = top_scores[0]
        best_doc = docs_row[0] if docs_row else None
        best_dist = float(dist_row[0]) if dist_row else None
        return RetrievalResult(
            key_id=best,
            value=best_doc,
            confidence=best_score,
            near_uniform_flag=False,
            distance=best_dist,
            top_k_ids=top_ids,
            top_k_scores=top_scores,
        )

    def store_batch(self, items: list[tuple[str, np.ndarray, str]]) -> None:
        """Single collection.add call for the whole batch."""
        if not items:
            return
        ids: list[str] = []
        embs: list[list[float]] = []
        docs: list[str] = []
        for key_id, key_vec, value in items:
            v = np.asarray(key_vec, dtype=np.float32).reshape(-1)
            if self.dim is None:
                self.dim = int(v.shape[0])
            ids.append(key_id)
            embs.append(v.tolist())
            docs.append(value)
        self.collection.add(ids=ids, embeddings=embs, documents=docs)

    def retrieve_batch(self, query_vecs: np.ndarray, k: int = 1) -> list[RetrievalResult]:
        """Native batched query."""
        q_arr = np.asarray(query_vecs, dtype=np.float32)
        if q_arr.ndim != 2:
            raise ValueError(
                f"chroma_adapter.retrieve_batch: query_vecs must be 2-D; got {q_arr.shape}"
            )
        B = q_arr.shape[0]
        if B == 0:
            return []
        n = len(self)
        if n == 0:
            empty = RetrievalResult(
                key_id=None,
                value=None,
                confidence=0.0,
                near_uniform_flag=False,
                distance=None,
                top_k_ids=[],
                top_k_scores=[],
            )
            return [empty for _ in range(B)]
        kk = max(1, min(k, n))
        res = self.collection.query(
            query_embeddings=[q_arr[i].tolist() for i in range(B)],
            n_results=kk,
        )
        ids_lists = res.get("ids") or []
        dist_lists = res.get("distances") or []
        doc_lists = res.get("documents") or []
        results: list[RetrievalResult] = []
        for i in range(B):
            ids_row = ids_lists[i] if i < len(ids_lists) else []
            dist_row = dist_lists[i] if i < len(dist_lists) else []
            docs_row = doc_lists[i] if i < len(doc_lists) else []
            if not ids_row:
                results.append(
                    RetrievalResult(
                        key_id=None,
                        value=None,
                        confidence=0.0,
                        near_uniform_flag=False,
                        distance=None,
                        top_k_ids=[],
                        top_k_scores=[],
                    )
                )
                continue
            top_ids = list(ids_row)
            top_scores = [float(1.0 / (1.0 + float(d))) for d in dist_row]
            results.append(
                RetrievalResult(
                    key_id=top_ids[0],
                    value=docs_row[0] if docs_row else None,
                    confidence=top_scores[0],
                    near_uniform_flag=False,
                    distance=float(dist_row[0]) if dist_row else None,
                    top_k_ids=top_ids,
                    top_k_scores=top_scores,
                )
            )
        return results

    def edit(self, key_id: str, new_value: str) -> None:
        self.collection.update(ids=[key_id], documents=[new_value])

    def delete(self, key_id: str) -> DeletionCertificate:
        # Probe existence pre-delete via get(); chroma delete is idempotent.
        try:
            existing = self.collection.get(ids=[key_id])
            existed = bool(existing.get("ids"))
        except Exception:
            existed = True
        try:
            self.collection.delete(ids=[key_id])
        except Exception:
            existed = False
        return DeletionCertificate(
            key_id=key_id,
            var_ratio=None,
            erased=existed,
            timestamp_ns=time.time_ns(),
        )

    def audit(self) -> AuditReport:
        return AuditReport(
            backend=self.name,
            n_items=len(self),
            kf1_above_thresh_frac=None,
            kf1_mean_oos_max_conf=None,
            kf2_max_isolation=None,
            tcft_mean_var_ratio=None,
            storage_bytes=_dir_size_bytes(self.persist_dir),
            config={
                "persist_dir": str(self.persist_dir),
                "collection_name": self.collection_name,
                "dim": self.dim,
            },
        )

    def save(self, path: Path) -> None:
        # Chroma persists automatically. If caller passes a different path,
        # we simply note it; we do not move the on-disk DB.
        # Best-effort flush by closing+reopening.
        target = Path(path)
        target.mkdir(parents=True, exist_ok=True)
        # No-op: chroma writes through.
        return

    def load(self, path: Path) -> None:
        # Re-open client at path; replaces in-memory handle.
        _require_chroma()
        self.persist_dir = Path(path)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
