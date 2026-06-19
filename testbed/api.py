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
    hallu_signals: optional Path-15 multi-signal hallucination detection
        panel. Substrate populates with a dict containing
        {posterior_entropy_flag, low_norm_flag, low_concentration_flag,
        high_distance_flag, composite_flag, composite_score, response_norm,
        concentration_ratio, min_dist_to_stored}. Baselines leave this None.
        See substrate_memory._compute_hallu_signals for details. This field
        is additive: it does NOT replace near_uniform_flag (which remains the
        canonical KF-1 single-signal flag tied to the existing audit panel).
    """

    key_id: Optional[str]
    value: Optional[str]
    confidence: float
    near_uniform_flag: bool
    distance: Optional[float] = None
    top_k_ids: list[str] = field(default_factory=list)
    top_k_scores: list[float] = field(default_factory=list)
    hallu_signals: Optional[dict] = None


@dataclass
class DeletionCertificate:
    """Audit-grade deletion certificate.

    Core fields (all backends populate):
    - key_id: id that was deleted.
    - erased: True if a post-delete retrieve on the same key returns a
      different key_id (or None). Backend-trivial for row-removal baselines.
    - timestamp_ns: monotonic ns timestamp of the delete call.

    Substrate-only audit-trail fields (None for baselines):
    - var_ratio: TCFT thermodynamic certificate. Variance ratio of W @ key
      after delete to var pre or var of random query. Values below 0.10
      satisfy the TCFT HARD_PASS band confirmed at N=8192 5-seed.
    - key_hash: SHA256(key_id) hex digest. Identifies the deleted fact in
      tamper-evident logs without exposing the key_id itself.
    - w_state_hash_before: SHA256 of the W matrix bytes BEFORE the erase
      step. Anchors the certificate to a specific substrate state.
    - w_state_hash_after: SHA256 of the W matrix bytes AFTER the erase step.
      Together with w_state_hash_before, this is the bit-exact attestation
      that the substrate state changed in the documented way.
    - verification_probes: list of dicts, one per verification probe run
      after the erase. Each entry has {probe_idx, max_prob, near_uniform_flag,
      returned_key_id}. Used by compliance auditors to confirm the erased
      fact is no longer recoverable from the substrate state itself.

    The 4 substrate-only fields together constitute the cryptographically
    verifiable audit artifact suitable for regulated-industry compliance
    (GDPR Article 17 erasure attestation, HIPAA audit trails, financial
    record retention).
    """

    key_id: str
    var_ratio: Optional[float]
    erased: bool
    timestamp_ns: int
    key_hash: Optional[str] = None
    w_state_hash_before: Optional[str] = None
    w_state_hash_after: Optional[str] = None
    verification_probes: Optional[list[dict]] = None


@dataclass
class AuditReport:
    """Backend self-audit summary.

    All substrate-specific killer-feature metrics are Optional; baselines
    populate them with None to make the contrast explicit in the report.

    Path-15 multi-signal hallucination detection fields:
    - kf1_composite_fire_rate: composite_flag fire rate on OOS samples.
      Composite fires when at least 2 of {posterior_entropy, low_norm,
      low_concentration, high_distance} agree. None for baselines.
    - kf1_per_signal_fire_rates: dict {posterior_entropy, low_norm,
      low_concentration, high_distance} -> fire rate on OOS samples.
      None for baselines.
    """

    backend: str
    n_items: int
    kf1_above_thresh_frac: Optional[float]
    kf1_mean_oos_max_conf: Optional[float]
    kf2_max_isolation: Optional[float]
    tcft_mean_var_ratio: Optional[float]
    storage_bytes: int
    config: dict
    kf1_composite_fire_rate: Optional[float] = None
    kf1_per_signal_fire_rates: Optional[dict] = None


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

    # --- Optional batched API ------------------------------------------------
    # Default implementations loop over the single-item ops so every backend
    # transparently supports batching. Backends with a native batched form
    # (substrate's matmul-fused outer-product accumulation, FAISS's
    # index.search(B), Chroma's collection.query(B)) override these.

    def store_batch(self, items: list[tuple[str, np.ndarray, str]]) -> None:
        """Store a batch of (key_id, key_vec, value) tuples.

        Default: loop over self.store. Backends override to fuse the work.
        Order MUST be preserved: item i is stored before item i+1 from the
        caller's perspective (so any atom-allocation determinism, edit
        sequencing, or audit ordering remains identical to a single-item
        loop).
        """
        for key_id, key_vec, value in items:
            self.store(key_id, key_vec, value)

    def retrieve_batch(
        self, query_vecs: np.ndarray, k: int = 1
    ) -> list[RetrievalResult]:
        """Retrieve top-k results for a batch of query vectors.

        query_vecs: shape (B, dim) float ndarray. Returns list of length B.
        Default: loop over self.retrieve. Backends override to fuse the work.
        """
        q = np.asarray(query_vecs)
        if q.ndim != 2:
            raise ValueError(
                f"retrieve_batch: query_vecs must be 2-D (B, dim); got shape {q.shape}"
            )
        return [self.retrieve(q[i], k=k) for i in range(q.shape[0])]

    def supports_killer_features(self) -> bool:
        """Override to True on the substrate backend. Baselines stay False;
        report.py uses this to populate the killer-feature panel."""
        return False
