"""Scenario: factorized_vs_dense.

Compare FactorizedSubstrate to SubstrateMemory at the SAME (N, codebook_C,
beta, seed) over a sweep of M/N ratios. For each ratio:

  - Instantiate a dense SubstrateMemory and a FactorizedSubstrate with
    M_capacity = M_target.
  - Store the SAME M items on both backends (same key vectors, same values,
    so atom allocations match across backends).
  - Measure memory footprint, store/retrieve latencies (p50, p95), recall
    on n_query random samples, and the math-identity gate
    w_parity_max_abs_delta = ||dense.W - fact.U @ fact.V.T||_inf.

The math-identity gate is the load-bearing correctness check: it MUST be
< 1e-5 at every measured M/N cell. If any cell violates this, the
factorized substrate is not a drop-in replacement and the result must be
flagged as a regression. HARD_PASS bands are gated on this delta.

Pareto-frontier note: at M_capacity < N/2 the factorized form is cheaper
on memory (2*N*M < N*N); at M_capacity > N/2 the dense form is cheaper.
On retrieve latency the crossover is at M_capacity ~ N (where the matvec
cost matches).

This scenario is substrate-only: baselines (dict, faiss, chroma,
sqlite_vec) do not implement the U/V factorization, so it returns a
"substrate_only_scenario" marker when called on them.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np
import torch

from testbed.api import MemoryBackend


def _first_seed(config: dict) -> int:
    seeds = config.get("seeds", [7])
    return int(seeds[0]) if seeds else 7


def _percentile(samples: list[float], q: float) -> float:
    if not samples:
        return 0.0
    return float(np.percentile(np.asarray(samples, dtype=np.float64), q))


def _make_vecs(rng: np.random.Generator, M: int, dim: int) -> np.ndarray:
    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    return raw * 2.0 - 1.0


def setup(config: dict) -> dict:
    dim = int(config.get("dim", 512))
    N = int(config.get("N", dim))
    seed = _first_seed(config)
    # M/N ratios to sweep.
    ratios = list(config.get(
        "factorized_M_per_N_ratios", [0.10, 0.25, 0.50, 1.0, 2.0]
    ))
    n_recall = int(config.get("factorized_n_recall_samples", 200))
    n_latency = int(config.get("factorized_n_latency_queries", 100))
    codebook_kind = str(config.get("codebook_kind", "bsc"))
    codebook_scale = int(config.get("codebook_scale", 4))
    beta = float(config.get("beta", 32.0))
    return {
        "dim": dim,
        "N": N,
        "seed": seed,
        "ratios": ratios,
        "n_recall": n_recall,
        "n_latency": n_latency,
        "codebook_kind": codebook_kind,
        "codebook_scale": codebook_scale,
        "beta": beta,
    }


def _measure_cell(
    N: int,
    M: int,
    seed: int,
    codebook_kind: str,
    codebook_scale: int,
    beta: float,
    n_recall: int,
    n_latency: int,
) -> dict:
    """Build both backends, store M items in lockstep, measure and parity-check.

    Returns the per-cell dict with footprint, latency, recall, and the
    math-identity delta.
    """
    from testbed.substrate_memory import SubstrateMemory
    from testbed.variants.factorized_substrate import FactorizedSubstrate

    rng = np.random.default_rng(seed + 7919 + M)

    dense = SubstrateMemory(
        N=N, codebook_kind=codebook_kind, codebook_scale=codebook_scale,
        beta=beta, seed=seed,
    )
    fact = FactorizedSubstrate(
        N=N, codebook_kind=codebook_kind, codebook_scale=codebook_scale,
        beta=beta, M_capacity=M, seed=seed,
    )

    # Sanity: same codebook (same seed + kind + scale + N).
    cb_match = bool(torch.allclose(dense.codebook, fact.codebook))

    # Build M items via codebook rows so both backends allocate identical
    # key atoms via the snap path. Pick rows that are sparse enough to avoid
    # collisions: row_i = i * (C // M) % C.
    C = dense.C
    step = max(1, C // max(M, 1))
    target_rows = [(i * step) % C for i in range(M)]
    # If step==1 and M > C/2, some collisions are inevitable; clip to keep
    # the codebook from being exhausted on store.
    if len(set(target_rows)) < len(target_rows):
        # Fall back to consecutive distinct rows.
        target_rows = list(range(M))
    ids = [f"fac_{i:06d}" for i in range(M)]
    values = [f"v_{i}" for i in range(M)]
    # Pre-extract key vectors.
    kvecs = [dense.codebook[r].detach().cpu().numpy() for r in target_rows]

    # Store loop: per-item latency for the first n_latency items, then
    # remainder batched. Measure both backends symmetrically.
    boundary = min(n_latency, M)
    dense_store_us: list[float] = []
    fact_store_us: list[float] = []
    for i in range(boundary):
        t0 = time.perf_counter_ns()
        dense.store(ids[i], kvecs[i], values[i])
        t1 = time.perf_counter_ns()
        dense_store_us.append((t1 - t0) / 1000.0)
        t0 = time.perf_counter_ns()
        fact.store(ids[i], kvecs[i], values[i])
        t1 = time.perf_counter_ns()
        fact_store_us.append((t1 - t0) / 1000.0)
    # Remainder per-item (we want both backends to walk identical paths;
    # batched paths differ across backends and skew parity).
    for i in range(boundary, M):
        dense.store(ids[i], kvecs[i], values[i])
        fact.store(ids[i], kvecs[i], values[i])

    # Math-identity check: dense.W vs fact.U @ fact.V.T.
    W_fact = fact._materialize_W()
    w_parity_max_abs_delta = float((dense.W - W_fact).abs().max().item())

    # Memory footprint in bytes (counts only the matrix payload, not codebook
    # or registries; codebook is shared logically across both).
    dense_W_bytes = dense.W.element_size() * dense.W.numel()
    fact_UV_bytes = (
        fact.U.element_size() * fact.U.numel()
        + fact.V.element_size() * fact.V.numel()
    )

    # Retrieve latency: n_latency random key vectors.
    q_count = min(n_latency, M)
    q_idx = rng.choice(M, size=q_count, replace=False)
    dense_retr_us: list[float] = []
    fact_retr_us: list[float] = []
    for i in q_idx:
        t0 = time.perf_counter_ns()
        dense.retrieve(kvecs[i], k=1)
        t1 = time.perf_counter_ns()
        dense_retr_us.append((t1 - t0) / 1000.0)
        t0 = time.perf_counter_ns()
        fact.retrieve(kvecs[i], k=1)
        t1 = time.perf_counter_ns()
        fact_retr_us.append((t1 - t0) / 1000.0)

    # Recall: n_recall random stored keys, identity returned.
    r_count = min(n_recall, M)
    r_idx = rng.choice(M, size=r_count, replace=False)
    dense_hits = 0
    fact_hits = 0
    for i in r_idx:
        rd = dense.retrieve(kvecs[i], k=1)
        rf = fact.retrieve(kvecs[i], k=1)
        if rd.key_id == ids[i]:
            dense_hits += 1
        if rf.key_id == ids[i]:
            fact_hits += 1

    return {
        "M": M,
        "M_capacity": M,
        "N": N,
        "M_over_N": M / float(N),
        "codebook_match": cb_match,
        "w_parity_max_abs_delta": w_parity_max_abs_delta,
        "dense_W_bytes": int(dense_W_bytes),
        "fact_UV_bytes": int(fact_UV_bytes),
        "dense_W_MB": dense_W_bytes / 1.0e6,
        "fact_UV_MB": fact_UV_bytes / 1.0e6,
        "memory_savings_ratio": (
            dense_W_bytes / fact_UV_bytes if fact_UV_bytes > 0 else None
        ),
        "p50_store_us_dense": _percentile(dense_store_us, 50),
        "p95_store_us_dense": _percentile(dense_store_us, 95),
        "p50_store_us_fact": _percentile(fact_store_us, 50),
        "p95_store_us_fact": _percentile(fact_store_us, 95),
        "p50_retrieve_us_dense": _percentile(dense_retr_us, 50),
        "p95_retrieve_us_dense": _percentile(dense_retr_us, 95),
        "p50_retrieve_us_fact": _percentile(fact_retr_us, 50),
        "p95_retrieve_us_fact": _percentile(fact_retr_us, 95),
        "retrieve_speedup_p50": (
            _percentile(dense_retr_us, 50) / _percentile(fact_retr_us, 50)
            if _percentile(fact_retr_us, 50) > 0 else None
        ),
        "recall_at_1_dense": dense_hits / max(r_count, 1),
        "recall_at_1_fact": fact_hits / max(r_count, 1),
        "n_recall_samples": r_count,
        "n_latency_queries": q_count,
    }


def run(backend: MemoryBackend, data: dict) -> dict:
    # This scenario only makes sense when the backend is the factorized
    # variant. For other backends, return a marker.
    if not getattr(backend, "name", "").startswith("substrate_factorized"):
        return {
            "scenario": "factorized_vs_dense",
            "backend": backend.name,
            "substrate_only_scenario": True,
            "skipped": True,
            "reason": "factorized_vs_dense is a substrate_factorized-only scenario",
        }

    N = int(data["N"])
    seed = int(data["seed"])
    ratios = list(data["ratios"])
    n_recall = int(data["n_recall"])
    n_latency = int(data["n_latency"])
    codebook_kind = str(data["codebook_kind"])
    codebook_scale = int(data["codebook_scale"])
    beta = float(data["beta"])

    per_ratio: dict[str, dict] = {}
    parity_deltas: list[float] = []

    for ratio in ratios:
        M = max(1, int(round(N * float(ratio))))
        # Cap M by half the codebook so we don't burn out atom allocation.
        # codebook C ~ codebook_scale * N; M < C / 2 is safe headroom.
        max_safe_M = int(codebook_scale * N // 2)
        if M > max_safe_M:
            per_ratio[f"{ratio:.2f}"] = {
                "M_over_N": ratio,
                "M": M,
                "skipped": True,
                "reason": (
                    f"M={M} exceeds half of codebook C={codebook_scale * N}; "
                    "raise codebook_scale or lower M/N"
                ),
            }
            continue
        cell = _measure_cell(
            N=N, M=M, seed=seed,
            codebook_kind=codebook_kind,
            codebook_scale=codebook_scale,
            beta=beta,
            n_recall=n_recall, n_latency=n_latency,
        )
        per_ratio[f"{ratio:.2f}"] = cell
        parity_deltas.append(cell["w_parity_max_abs_delta"])

    max_parity_delta = max(parity_deltas) if parity_deltas else None
    math_identity_holds = (
        (max_parity_delta is not None) and (max_parity_delta < 1e-5)
    )

    # Pareto-frontier notes: at which ratio does factorized beat dense?
    mem_win_ratios = sorted(
        [float(k) for k, v in per_ratio.items()
         if isinstance(v, dict) and v.get("memory_savings_ratio") is not None
         and v["memory_savings_ratio"] > 1.0]
    )
    lat_win_ratios = sorted(
        [float(k) for k, v in per_ratio.items()
         if isinstance(v, dict) and v.get("retrieve_speedup_p50") is not None
         and v["retrieve_speedup_p50"] > 1.0]
    )

    return {
        "scenario": "factorized_vs_dense",
        "backend": backend.name,
        "ratios": ratios,
        "per_ratio": per_ratio,
        "max_w_parity_max_abs_delta": max_parity_delta,
        "math_identity_holds": math_identity_holds,
        "memory_win_M_per_N_ratios": mem_win_ratios,
        "latency_win_M_per_N_ratios": lat_win_ratios,
        "first_memory_win_ratio": mem_win_ratios[0] if mem_win_ratios else None,
        "first_latency_win_ratio": lat_win_ratios[0] if lat_win_ratios else None,
    }


def thresholds() -> dict:
    """HARD_PASS: math identity holds (max delta < 1e-5) across all cells.
    HARD_FAIL: any cell exceeds 1e-3.
    """
    return {
        "substrate": {
            "hard_pass": {"max_w_parity_max_abs_delta": 1e-5},
            "hard_fail": {"max_w_parity_max_abs_delta": 1e-3},
        },
        "baselines": {
            "hard_pass": {},
            "hard_fail": {},
        },
    }
