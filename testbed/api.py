"""Shared API surface for the substrate memory testbed.

All memory backends (substrate, FAISS, Chroma, sqlite-vec, dict) implement
the MemoryBackend ABC defined here. Scenarios and the harness import only
from this module to stay backend-agnostic.

Confidence semantics differ across backends (softmax max-prob for substrate,
inner-product score for FAISS, distance score for Chroma). Scenarios should
record both the raw native confidence AND a normalized rank-only signal
(argmax-correct as 1.0 else 0.0). See risk register in
notes/testbed_architecture_2026-05-29.md.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np


@dataclass
class RetrievalResult:
    """Result of a single retrieve() call.

    key_id: stored id matching the query, or None if backend judged the query
        out-of-store (substrate uses near_uniform_flag for this; baselines
        return the nearest-neighbor id with no rejection).
    value: stored value string at key_id, or None when key_id is None.
    confidence: backend-native confidence score. Substrate emits softmax max
        probability over the codebook. FAISS emits the inner-product score.
        Chroma emits 1 minus normalized distance. Comparable only within a
        single backend.
    near_uniform_flag: substrate-specific signal that the response is
        statistically indistinguishable from random codebook noise (KF-1
        hallucination structural impossibility). Baselines set this to False.
    distance: backend-specific distance (FAISS/Chroma); None for substrate.
    top_k_ids: ranked list of candidate key_ids (length up to k).
    top_k_scores: backend-native scores aligned with top_k_ids.
    """

    key_id: Optional[str]
    value: Optional[str]
    confidence: float
    near_uniform_flag: bool
    distance: Optional[float] = None
    top_k_ids: list[str] = field(default_factory=list)
    top_k_scores: list[float] = field(default_factory=list)


@dataclass
class DeletionCertificate:
    """Result of a single delete() call.

    key_id: id that was deleted.
    var_ratio: TCFT thermodynamic certificate. Substrate emits the variance
        ratio of W @ key_atom after delete to W @ random_atom; values below
        0.10 satisfy the TCFT HARD_PASS band confirmed at N=8192 5-seed.
        Baselines emit None (deletion is structural, not thermodynamic).
    erased: True if a post-delete retrieve on the same key returns a
        different key_id (or None).
    timestamp_ns: monotonic ns timestamp of the delete call.
    """

    key_id: str
    var_ratio: Optional[float]
    erased: bool
    timestamp_ns: int


@dataclass
class AuditReport:
    """Backend self-audit summary.

    All substrate-specific killer-feature metrics are Optional; baselines
    populate them with None to make the contrast explicit in the report.
    """

    backend: str
    n_items: int
    kf1_above_thresh_frac: Optional[float]
    kf1_mean_oos_max_conf: Optional[float]
    kf2_max_isolation: Optional[float]
    tcft_mean_var_ratio: Optional[float]
    storage_bytes: int
    config: dict


class MemoryBackend(ABC):
    """Abstract base for all five memory backends.

    Implementations live in testbed/substrate_memory.py and
    testbed/baselines/. Subclasses MUST set the `name` class attribute and
    implement every abstract method.
    """

    name: str = "abstract"

    @abstractmethod
    def store(self, key_id: str, key_vec: np.ndarray, value: str) -> None:
        """Store a (key_vec, value) pair under key_id. key_vec is a float
        ndarray of shape (dim,). Substrate snaps key_vec to its nearest
        codebook atom; baselines store key_vec verbatim."""

    @abstractmethod
    def retrieve(self, query_vec: np.ndarray, k: int = 1) -> RetrievalResult:
        """Return top-k retrieval for query_vec. k=1 by default."""

    @abstractmethod
    def edit(self, key_id: str, new_value: str) -> None:
        """In-place edit of the value at key_id. Substrate performs the
        outer-product subtract+add (KF-2 isolation-preserving). Baselines
        update the value field of the stored row."""

    @abstractmethod
    def delete(self, key_id: str) -> DeletionCertificate:
        """Remove key_id from the backend. Substrate computes TCFT
        var_ratio; baselines emit var_ratio=None."""

    @abstractmethod
    def audit(self) -> AuditReport:
        """Run backend-native audit and return a populated AuditReport.
        Substrate samples KF-1 + KF-2 + TCFT panels; baselines populate the
        killer-feature fields with None."""

    @abstractmethod
    def save(self, path: Path) -> None:
        """Persist backend state to a directory (creates path if missing)."""

    @abstractmethod
    def load(self, path: Path) -> None:
        """Load backend state from a directory previously written by save()."""

    @abstractmethod
    def __len__(self) -> int:
        """Number of stored (key_id, value) pairs."""

    def supports_killer_features(self) -> bool:
        """Override to True on the substrate backend. Baselines stay False;
        report.py uses this to populate the killer-feature panel."""
        return False
