"""SchemaExemplarBayes: cheap-compression Bayesian schema router.

Extracted from Batch C Compression Pareto v1 MM finding (2026-07-01 Skunkworks
7cef91b3): at chain-grade N=8192, 10x schema compression via LSE-Bayes routing
only drops recall by ~0.10 (0.877 -> 0.773). 100x hardmax centroid pooling
LOSES 96% recall (H2 refuted). EXEMPLAR_BAYES-10x is the cost-optimal Pareto
point for schema-clustered fact retrieval.

Storage note: this primitive is a ROUTING mechanism, not a storage compressor.
All facts remain stored; the compression is in retrieval-lookup locality:
readout partitions n_facts into k_schemas clusters, computes per-schema
log-posterior via LSE over cluster exemplars, then picks winning cluster's
argmax exemplar. Compression ratio = n_facts / k_schemas.

For true storage compression (bytes-per-fact axis), see Batch E
bytes_per_fact_pareto v1.1 findings: BINARY_DENSE dominates at 32x storage
compression with no recall loss at N=4096.
"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

import numpy as np
from scipy.special import logsumexp


def _l2(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """L2 normalize (B, D) row-wise."""
    n = np.linalg.norm(X, axis=1, keepdims=True) + eps
    return (X / n).astype(np.float32)


def _kmeans_partition(
    facts: np.ndarray,
    k: int,
    rng: np.random.Generator,
    n_iter: int = 12,
) -> Tuple[np.ndarray, np.ndarray]:
    """k-means partition facts (n_facts, N) into k clusters.
    Returns (assignments (n_facts,), centroids (k, N))."""
    n_facts = facts.shape[0]
    init_idx = rng.choice(n_facts, size=k, replace=False)
    centroids = facts[init_idx].copy()
    assignments = np.zeros(n_facts, dtype=np.int64)
    for _ in range(n_iter):
        sims = facts @ centroids.T
        new_assign = np.argmax(sims, axis=1).astype(np.int64)
        if np.array_equal(new_assign, assignments):
            break
        assignments = new_assign
        for c in range(k):
            mask = assignments == c
            if mask.sum() == 0:
                centroids[c] = facts[rng.integers(n_facts)]
            else:
                centroids[c] = _l2(facts[mask].mean(axis=0, keepdims=True))[0]
    return assignments, centroids


class SchemaExemplarBayesIndex:
    """LSE-Bayes over k schema clusters; 10x compression Pareto sweet-spot.

    Usage:
        idx = SchemaExemplarBayesIndex(compression_ratio=10, seed=7)
        idx.fit(facts)                    # facts: (n_facts, N) L2-normed
        preds = idx.predict(queries)      # queries: (n_queries, N) -> (n_queries,) fact idx

    At compression_ratio=10, expected recall ~= 0.90 of no-compression baseline
    (per Batch C v1 3-seed cross-check at N=8192, n_facts=10000; Skunkworks
    a7708cb2 tier=MM).

    Absolute impact: use this over HARDMAX_CENTROID compression when you need
    schema-locality retrieval AND want to preserve recall within ~10%. Avoid
    100x HARDMAX (Batch C measured 96% recall loss).
    """

    def __init__(
        self,
        compression_ratio: int = 10,
        beta: Optional[float] = None,
        kmeans_iter: int = 12,
        seed: int = 7,
    ):
        if compression_ratio < 2:
            raise ValueError(f"compression_ratio must be >=2, got {compression_ratio}")
        self.compression_ratio = int(compression_ratio)
        self.beta = beta
        self.kmeans_iter = int(kmeans_iter)
        self.rng = np.random.default_rng(seed)
        self._fitted = False
        self.facts: Optional[np.ndarray] = None
        self.assignments: Optional[np.ndarray] = None
        self.schema_to_facts: Optional[Dict[int, np.ndarray]] = None
        self.k_schemas: int = 0

    def _beta_for(self, k: int) -> float:
        if self.beta is not None:
            return float(self.beta)
        return 6.0 + math.log2(max(k, 2))

    def fit(self, facts: np.ndarray) -> "SchemaExemplarBayesIndex":
        """Fit schema clustering over (n_facts, N) fact matrix (L2-normed)."""
        if facts.ndim != 2:
            raise ValueError(f"facts must be (n_facts, N); got shape {facts.shape}")
        n_facts, _ = facts.shape
        k = max(2, int(round(n_facts / self.compression_ratio)))
        assignments, _ = _kmeans_partition(facts, k, self.rng, self.kmeans_iter)
        schema_to_facts: Dict[int, np.ndarray] = {}
        for c in range(k):
            mask = assignments == c
            if mask.sum() > 0:
                schema_to_facts[c] = np.where(mask)[0]
        self.facts = facts
        self.assignments = assignments
        self.schema_to_facts = schema_to_facts
        self.k_schemas = len(schema_to_facts)
        self._fitted = True
        return self

    def predict(self, queries: np.ndarray) -> np.ndarray:
        """LSE-Bayes readout over schema clusters. Returns (n_queries,) fact idx."""
        if not self._fitted:
            raise RuntimeError("SchemaExemplarBayesIndex not fit; call fit(facts) first")
        if queries.ndim != 2:
            raise ValueError(f"queries must be (n_queries, N); got shape {queries.shape}")
        beta = self._beta_for(self.k_schemas)
        log_prior = math.log(1.0 / self.k_schemas)
        n_queries = queries.shape[0]
        preds = np.zeros(n_queries, dtype=np.int64)
        sims_all = queries @ self.facts.T  # (n_queries, n_facts)
        for qi in range(n_queries):
            best_score = -np.inf
            best_fact = 0
            for c, fact_idxs in self.schema_to_facts.items():
                s_in_c = sims_all[qi, fact_idxs]
                score = log_prior + logsumexp(beta * s_in_c)
                if score > best_score:
                    best_score = score
                    best_fact = int(fact_idxs[int(np.argmax(s_in_c))])
            preds[qi] = best_fact
        return preds

    def stats(self) -> Dict[str, Any]:
        """Diagnostics for cell-author + audit."""
        if not self._fitted:
            return {"fitted": False}
        cluster_sizes = np.array([len(v) for v in self.schema_to_facts.values()])
        return {
            "fitted": True,
            "n_facts": int(self.facts.shape[0]),
            "n_schemas": int(self.k_schemas),
            "compression_ratio_effective": float(self.facts.shape[0] / max(self.k_schemas, 1)),
            "cluster_size_mean": float(cluster_sizes.mean()),
            "cluster_size_std": float(cluster_sizes.std()),
            "cluster_size_min": int(cluster_sizes.min()),
            "cluster_size_max": int(cluster_sizes.max()),
            "beta_at_readout": self._beta_for(self.k_schemas),
        }


__all__ = ["SchemaExemplarBayesIndex"]
