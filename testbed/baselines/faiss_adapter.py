"""FAISS CPU baseline.

IndexFlatIP wrapped with IndexIDMap so delete() is O(1). All vectors are
L2-normalized before insert so inner-product == cosine similarity.
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

try:
    import faiss  # type: ignore
except ImportError as exc:  # pragma: no cover
    faiss = None
    _IMPORT_ERR = exc
else:
    _IMPORT_ERR = None


def _require_faiss() -> None:
    if faiss is None:
        raise ImportError(
            "faiss not installed. Install with: pip install faiss-cpu==1.8.0.post1"
        ) from _IMPORT_ERR


def _normalize(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float32).reshape(-1)
    n = float(np.linalg.norm(v))
    if n == 0.0:
        return v
    return v / n


class FaissMemory(MemoryBackend):
    """FAISS IndexIDMap(IndexFlatIP) for cosine retrieval with cheap deletes."""

    name = "faiss"

    def __init__(self, dim: int, index_kind: str = "Flat") -> None:
        _require_faiss()
        if index_kind != "Flat":
            raise NotImplementedError(
                f"faiss_adapter: only index_kind='Flat' is supported, got {index_kind!r}"
            )
        self.dim = int(dim)
        self.index_kind = index_kind
        self._build_empty_index()
        # key_id -> (int64 faiss id, value str)
        self._id_to_value: dict[str, str] = {}
        self._id_to_faiss: dict[str, int] = {}
        self._next_faiss_id: int = 0

    def _build_empty_index(self) -> None:
        flat = faiss.IndexFlatIP(self.dim)
        self.index = faiss.IndexIDMap(flat)

    def __len__(self) -> int:
        return len(self._id_to_value)

    def _assign_id(self) -> int:
        i = self._next_faiss_id
        self._next_faiss_id += 1
        return i

    def store(self, key_id: str, key_vec: np.ndarray, value: str) -> None:
        if key_id in self._id_to_value:
            raise KeyError(f"faiss_adapter: key_id {key_id!r} already stored")
        v = _normalize(key_vec)
        if v.shape[0] != self.dim:
            raise ValueError(
                f"faiss_adapter: vec dim {v.shape[0]} != configured dim {self.dim}"
            )
        fid = self._assign_id()
        self.index.add_with_ids(v[None, :], np.array([fid], dtype=np.int64))
        self._id_to_value[key_id] = value
        self._id_to_faiss[key_id] = fid

    def retrieve(self, query_vec: np.ndarray, k: int = 1) -> RetrievalResult:
        if len(self._id_to_value) == 0:
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
                f"faiss_adapter: query dim {q.shape[0]} != configured dim {self.dim}"
            )
        kk = max(1, min(k, len(self._id_to_value)))
        scores, ids = self.index.search(q[None, :].astype(np.float32), kk)
        scores = scores[0]
        ids = ids[0]
        # Reverse lookup faiss_id -> key_id
        faiss_to_key = {fid: kid for kid, fid in self._id_to_faiss.items()}
        top_ids: list[str] = []
        top_scores: list[float] = []
        for sc, fid in zip(scores, ids):
            if fid < 0:
                continue
            kid = faiss_to_key.get(int(fid))
            if kid is None:
                continue
            top_ids.append(kid)
            top_scores.append(float(sc))
        if not top_ids:
            return RetrievalResult(
                key_id=None,
                value=None,
                confidence=0.0,
                near_uniform_flag=False,
                distance=None,
                top_k_ids=[],
                top_k_scores=[],
            )
        best = top_ids[0]
        best_score = top_scores[0]
        return RetrievalResult(
            key_id=best,
            value=self._id_to_value[best],
            confidence=best_score,
            near_uniform_flag=False,
            distance=float(1.0 - best_score),
            top_k_ids=top_ids,
            top_k_scores=top_scores,
        )

    def store_batch(self, items: list[tuple[str, np.ndarray, str]]) -> None:
        """One faiss add_with_ids call for the whole batch."""
        if not items:
            return
        vecs: list[np.ndarray] = []
        fids: list[int] = []
        for key_id, key_vec, value in items:
            if key_id in self._id_to_value:
                raise KeyError(
                    f"faiss_adapter: key_id {key_id!r} already stored"
                )
            v = _normalize(key_vec)
            if v.shape[0] != self.dim:
                raise ValueError(
                    f"faiss_adapter: vec dim {v.shape[0]} != configured dim {self.dim}"
                )
            fid = self._assign_id()
            vecs.append(v)
            fids.append(fid)
            self._id_to_value[key_id] = value
            self._id_to_faiss[key_id] = fid
        arr = np.stack(vecs, axis=0).astype(np.float32, copy=False)
        ids_arr = np.asarray(fids, dtype=np.int64)
        self.index.add_with_ids(arr, ids_arr)

    def retrieve_batch(
        self, query_vecs: np.ndarray, k: int = 1
    ) -> list[RetrievalResult]:
        """Single index.search(B) call. This is FAISS's native fast path."""
        q_arr = np.asarray(query_vecs)
        if q_arr.ndim != 2:
            raise ValueError(
                f"faiss_adapter.retrieve_batch: query_vecs must be 2-D; got {q_arr.shape}"
            )
        if q_arr.shape[1] != self.dim:
            raise ValueError(
                f"faiss_adapter.retrieve_batch: query dim {q_arr.shape[1]} != {self.dim}"
            )
        B = q_arr.shape[0]
        if B == 0:
            return []
        if len(self._id_to_value) == 0:
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

        # L2-normalize each query row.
        norms = np.linalg.norm(q_arr, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        q_norm = (q_arr / norms).astype(np.float32, copy=False)

        kk = max(1, min(k, len(self._id_to_value)))
        scores, ids = self.index.search(q_norm, kk)

        faiss_to_key = {fid: kid for kid, fid in self._id_to_faiss.items()}

        results: list[RetrievalResult] = []
        for i in range(B):
            row_scores = scores[i]
            row_ids = ids[i]
            top_ids: list[str] = []
            top_scores: list[float] = []
            for sc, fid in zip(row_scores, row_ids):
                if fid < 0:
                    continue
                kid = faiss_to_key.get(int(fid))
                if kid is None:
                    continue
                top_ids.append(kid)
                top_scores.append(float(sc))
            if not top_ids:
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
            best = top_ids[0]
            best_score = top_scores[0]
            results.append(
                RetrievalResult(
                    key_id=best,
                    value=self._id_to_value[best],
                    confidence=best_score,
                    near_uniform_flag=False,
                    distance=float(1.0 - best_score),
                    top_k_ids=top_ids,
                    top_k_scores=top_scores,
                )
            )
        return results

    def edit(self, key_id: str, new_value: str) -> None:
        if key_id not in self._id_to_value:
            raise KeyError(f"faiss_adapter: edit on missing key_id {key_id!r}")
        self._id_to_value[key_id] = new_value

    def delete(self, key_id: str) -> DeletionCertificate:
        existed = key_id in self._id_to_value
        if existed:
            fid = self._id_to_faiss.pop(key_id)
            self._id_to_value.pop(key_id)
            sel = faiss.IDSelectorArray(np.array([fid], dtype=np.int64))
            self.index.remove_ids(sel)
        return DeletionCertificate(
            key_id=key_id,
            var_ratio=None,
            erased=existed,
            timestamp_ns=time.time_ns(),
        )

    def audit(self) -> AuditReport:
        storage = int(self.index.ntotal) * self.dim * 4
        return AuditReport(
            backend=self.name,
            n_items=len(self._id_to_value),
            kf1_above_thresh_frac=None,
            kf1_mean_oos_max_conf=None,
            kf2_max_isolation=None,
            tcft_mean_var_ratio=None,
            storage_bytes=storage,
            config={"dim": self.dim, "index_kind": self.index_kind},
        )

    def save(self, path: Path) -> None:
        _require_faiss()
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(path / "index.faiss"))
        sidecar = {
            "dim": self.dim,
            "index_kind": self.index_kind,
            "next_faiss_id": self._next_faiss_id,
            "id_to_value": self._id_to_value,
            "id_to_faiss": self._id_to_faiss,
        }
        with open(path / "ids.json", "w", encoding="utf-8") as f:
            json.dump(sidecar, f)

    def load(self, path: Path) -> None:
        _require_faiss()
        path = Path(path)
        self.index = faiss.read_index(str(path / "index.faiss"))
        with open(path / "ids.json", "r", encoding="utf-8") as f:
            sidecar = json.load(f)
        self.dim = int(sidecar["dim"])
        self.index_kind = sidecar.get("index_kind", "Flat")
        self._next_faiss_id = int(sidecar.get("next_faiss_id", 0))
        self._id_to_value = dict(sidecar["id_to_value"])
        self._id_to_faiss = {k: int(v) for k, v in sidecar["id_to_faiss"].items()}
