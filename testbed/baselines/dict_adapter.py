"""In-memory dict baseline: ground-truth oracle.

Stores (key_vec, value) in a plain dict keyed by key_id. Retrieval is brute-force
cosine over all stored vectors; argmax wins. Useful as the recall ceiling that
every other backend is measured against.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from testbed.api import (
    AuditReport,
    DeletionCertificate,
    MemoryBackend,
    RetrievalResult,
)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


class DictMemory(MemoryBackend):
    """Brute-force cosine oracle. No dependencies beyond numpy."""

    name = "dict"

    def __init__(self, dim: int | None = None) -> None:
        self.dim = dim
        # key_id -> (key_vec float32, value str)
        self._items: dict[str, tuple[np.ndarray, str]] = {}

    def __len__(self) -> int:
        return len(self._items)

    def store(self, key_id: str, key_vec: np.ndarray, value: str) -> None:
        v = np.asarray(key_vec, dtype=np.float32).reshape(-1)
        if self.dim is None:
            self.dim = int(v.shape[0])
        elif v.shape[0] != self.dim:
            raise ValueError(
                f"dict_adapter: vec dim {v.shape[0]} != configured dim {self.dim}"
            )
        self._items[key_id] = (v, value)

    def retrieve(self, query_vec: np.ndarray, k: int = 1) -> RetrievalResult:
        if not self._items:
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
        ids = list(self._items.keys())
        vecs = np.stack([self._items[i][0] for i in ids], axis=0)
        # Cosine
        qn = float(np.linalg.norm(q))
        vn = np.linalg.norm(vecs, axis=1)
        denom = vn * (qn if qn > 0 else 1.0)
        denom[denom == 0.0] = 1.0
        sims = (vecs @ q) / denom
        order = np.argsort(-sims)
        top = order[:k]
        top_ids = [ids[i] for i in top]
        top_scores = [float(sims[i]) for i in top]
        best_id = top_ids[0]
        best_score = top_scores[0]
        return RetrievalResult(
            key_id=best_id,
            value=self._items[best_id][1],
            confidence=best_score,
            near_uniform_flag=False,
            distance=float(1.0 - best_score),
            top_k_ids=top_ids,
            top_k_scores=top_scores,
        )

    def retrieve_batch(self, query_vecs: np.ndarray, k: int = 1) -> list[RetrievalResult]:
        """Single matmul over (B, dim) x (M, dim).T for the whole batch."""
        q_arr = np.asarray(query_vecs, dtype=np.float32)
        if q_arr.ndim != 2:
            raise ValueError(
                f"dict_adapter.retrieve_batch: query_vecs must be 2-D; got {q_arr.shape}"
            )
        B = q_arr.shape[0]
        if B == 0:
            return []
        if not self._items:
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

        ids = list(self._items.keys())
        vecs = np.stack([self._items[i][0] for i in ids], axis=0)
        vn = np.linalg.norm(vecs, axis=1)
        vn[vn == 0.0] = 1.0
        qn = np.linalg.norm(q_arr, axis=1)
        qn[qn == 0.0] = 1.0
        # sims: (B, M)
        sims = (q_arr @ vecs.T) / (qn[:, None] * vn[None, :])
        kk = max(1, min(k, len(ids)))
        # top-kk indices per row
        if kk == 1:
            top_idx = np.argmax(sims, axis=1, keepdims=True)
        else:
            # partial-sort top kk descending
            part = np.argpartition(-sims, kth=kk - 1, axis=1)[:, :kk]
            # order each row's top-kk by their sim
            row_sims = np.take_along_axis(sims, part, axis=1)
            order = np.argsort(-row_sims, axis=1)
            top_idx = np.take_along_axis(part, order, axis=1)

        results: list[RetrievalResult] = []
        for b in range(B):
            row_top = top_idx[b]
            top_ids = [ids[i] for i in row_top]
            top_scores = [float(sims[b, i]) for i in row_top]
            best = top_ids[0]
            best_score = top_scores[0]
            results.append(
                RetrievalResult(
                    key_id=best,
                    value=self._items[best][1],
                    confidence=best_score,
                    near_uniform_flag=False,
                    distance=float(1.0 - best_score),
                    top_k_ids=top_ids,
                    top_k_scores=top_scores,
                )
            )
        return results

    def edit(self, key_id: str, new_value: str) -> None:
        if key_id not in self._items:
            raise KeyError(f"dict_adapter: edit on missing key_id {key_id!r}")
        vec, _ = self._items[key_id]
        self._items[key_id] = (vec, new_value)

    def delete(self, key_id: str) -> DeletionCertificate:
        existed = key_id in self._items
        if existed:
            self._items.pop(key_id)
        return DeletionCertificate(
            key_id=key_id,
            var_ratio=None,
            erased=existed,
            timestamp_ns=time.time_ns(),
        )

    def audit(self) -> AuditReport:
        # Storage = json blob size for the current state.
        payload = self._dump_payload()
        storage = len(json.dumps(payload).encode("utf-8"))
        return AuditReport(
            backend=self.name,
            n_items=len(self._items),
            kf1_above_thresh_frac=None,
            kf1_mean_oos_max_conf=None,
            kf2_max_isolation=None,
            tcft_mean_var_ratio=None,
            storage_bytes=storage,
            config={"dim": self.dim},
        )

    def _dump_payload(self) -> dict:
        return {
            "dim": self.dim,
            "items": {
                k: {"vec": v.tolist(), "value": s} for k, (v, s) in self._items.items()
            },
        }

    def save(self, path: Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        out = path / "dict_state.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(self._dump_payload(), f)

    def load(self, path: Path) -> None:
        path = Path(path)
        src = path / "dict_state.json"
        with open(src, "r", encoding="utf-8") as f:
            payload = json.load(f)
        self.dim = payload.get("dim")
        self._items = {
            k: (np.asarray(item["vec"], dtype=np.float32), item["value"])
            for k, item in payload.get("items", {}).items()
        }
