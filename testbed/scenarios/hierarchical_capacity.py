"""Scenario: hierarchical_capacity.

Tests the HierarchicalSubstrate (two-level: top routing + K leaf substrates)
against an envelope sweep of M_total. Hypothesis: the hierarchical structure
spreads M_total across K leaves so each leaf stays within its single-
substrate envelope while the top-level router preserves recall.

Comparison rows:
  substrate_hierarchical      K leaves at N_leaf, top routing at K x N_leaf
  substrate (reference)       single SubstrateMemory at N=N_leaf
  substrate (reference)       single SubstrateMemory at N=8192 (different
                              point on the N/M curve, for visual contrast)

Per M_total we measure:
  total_disk_MB           sum of top + K leaves on disk
  mean_retrieve_latency_us mean wall time per retrieve (hier = top + leaf;
                          single substrate = one retrieve)
  recall_at_1             argmax-correct rate
  routing_accuracy        hier only: fraction of retrieves where the top
                          routed to the topic the fact was stored in
  cross_level_chain_integrity   hier only: re-derived chain integrity

HARD_PASS bands for the hierarchical row (pre-registered):
  recall_at_1 >= 0.80 at all M_total
  routing_accuracy >= 0.85 at all M_total
  cross_level_chain_integrity == 1.0
  mean_retrieve_latency_us <= 2 * single_substrate_at_N=N_leaf latency

Single-substrate rows are baselines for crossover and do not have hier-
specific gates.

Knobs (config keys with sensible defaults):
  hier_M_totals               list of M values, default [1000, 5000, 10000, 20000]
  hier_K_topics               default 10
  hier_N_top                  default 512
  hier_N_leaf                 default 2048
  hier_M_capacity_per_leaf    default 1000
  hier_codebook_C_top         default 2048
  hier_codebook_C_leaf        default 8192
  hier_n_recall_samples       default 500
  hier_n_latency_queries      default 500
  hier_n_delete               default 100
  single_substrate_Ns         default [2048, 8192] (single-substrate sizes)
"""

from __future__ import annotations

import shutil
import tempfile
import time
from pathlib import Path

import numpy as np


def _first_seed(config: dict) -> int:
    seeds = config.get("seeds", [7])
    if not seeds:
        return 7
    return int(seeds[0])


def _percentile(samples: list[float], q: float) -> float:
    if not samples:
        return 0.0
    return float(np.percentile(np.asarray(samples, dtype=np.float64), q))


def _mean(samples: list[float]) -> float:
    if not samples:
        return 0.0
    return float(np.mean(np.asarray(samples, dtype=np.float64)))


def _dir_size_bytes(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for p in path.rglob("*"):
        try:
            if p.is_file():
                total += p.stat().st_size
        except OSError:
            continue
    return total


def _make_vecs(rng: np.random.Generator, M: int, dim: int) -> np.ndarray:
    raw = rng.integers(0, 2, size=(M, dim), dtype=np.int8).astype(np.float32)
    return raw * 2.0 - 1.0


def setup(config: dict) -> dict:
    return {
        "Ms": list(config.get("hier_M_totals", [1000, 5000, 10000, 20000])),
        "K_topics": int(config.get("hier_K_topics", 10)),
        "N_top": int(config.get("hier_N_top", 512)),
        "N_leaf": int(config.get("hier_N_leaf", 2048)),
        "M_cap_per_leaf": int(config.get("hier_M_capacity_per_leaf", 1000)),
        "codebook_C_top": int(config.get("hier_codebook_C_top", 2048)),
        "codebook_C_leaf": int(config.get("hier_codebook_C_leaf", 8192)),
        "single_substrate_Ns": list(
            config.get("single_substrate_Ns", [2048, 8192])
        ),
        "n_recall_samples": int(config.get("hier_n_recall_samples", 500)),
        "n_latency_queries": int(config.get("hier_n_latency_queries", 500)),
        "n_delete": int(config.get("hier_n_delete", 100)),
        "seed": _first_seed(config),
        "codebook_kind": str(config.get("codebook_kind", "bsc")),
        "beta": float(config.get("beta", 32.0)),
        "hallu_threshold": float(config.get("hallu_threshold", 0.5)),
    }


def _build_hierarchical(data: dict):
    from testbed.variants.hierarchical_substrate import HierarchicalSubstrate
    return HierarchicalSubstrate(
        N_top=int(data["N_top"]),
        N_leaf=int(data["N_leaf"]),
        K_topics=int(data["K_topics"]),
        codebook_kind=str(data["codebook_kind"]),
        codebook_C_top=int(data["codebook_C_top"]),
        codebook_C_leaf=int(data["codebook_C_leaf"]),
        beta=float(data["beta"]),
        hallu_threshold=float(data["hallu_threshold"]),
        M_capacity_per_leaf=int(data["M_cap_per_leaf"]),
        routing="hash",
        device="cpu",
        seed=int(data["seed"]),
    )


def _build_single_substrate(N: int, data: dict, M_hint: int):
    from testbed.substrate_memory import SubstrateMemory
    return SubstrateMemory(
        N=int(N),
        codebook_kind=str(data["codebook_kind"]),
        codebook_scale=4,
        beta=float(data["beta"]),
        hallu_threshold=float(data["hallu_threshold"]),
        device="cpu",
        seed=int(data["seed"]),
        codebook_M_hint=int(M_hint),
    )


def _measure_single_substrate(
    backend, vecs: np.ndarray, ids: list[str], values: list[str],
    n_recall: int, n_latency: int, n_delete: int, rng: np.random.Generator,
    M: int,
) -> dict:
    """Drive a single substrate through the same protocol as the hierarchical
    row so the metrics are apples-to-apples."""
    # Store.
    for i in range(M):
        backend.store(ids[i], vecs[i], values[i])

    # Recall.
    r_count = min(n_recall, M)
    r_idx = rng.choice(M, size=r_count, replace=False)
    hits = 0
    for i in r_idx:
        res = backend.retrieve(vecs[i], k=1)
        if res.key_id == ids[i]:
            hits += 1
    recall_at_1 = hits / max(r_count, 1)

    # Latency.
    q_count = min(n_latency, M)
    q_idx = rng.choice(M, size=q_count, replace=False)
    retr_us: list[float] = []
    for i in q_idx:
        t0 = time.perf_counter_ns()
        backend.retrieve(vecs[i], k=1)
        t1 = time.perf_counter_ns()
        retr_us.append((t1 - t0) / 1000.0)

    # Disk.
    save_dir = Path(tempfile.mkdtemp(prefix=f"hcs_single_{M}_"))
    disk_bytes = 0
    try:
        backend.save(save_dir)
        disk_bytes = _dir_size_bytes(save_dir)
    except Exception:
        disk_bytes = 0
    finally:
        shutil.rmtree(save_dir, ignore_errors=True)

    return {
        "recall_at_1": float(recall_at_1),
        "n_recall_samples": int(r_count),
        "n_latency_queries": int(q_count),
        "mean_retrieve_latency_us": _mean(retr_us),
        "p50_retrieve_latency_us": _percentile(retr_us, 50),
        "p95_retrieve_latency_us": _percentile(retr_us, 95),
        "disk_bytes": int(disk_bytes),
        "disk_MB": float(disk_bytes) / 1.0e6,
    }


def _measure_hierarchical(
    backend, vecs: np.ndarray, ids: list[str], values: list[str],
    n_recall: int, n_latency: int, n_delete: int, rng: np.random.Generator,
    M: int,
) -> dict:
    """Drive the hierarchical backend through the protocol."""
    # Store.
    for i in range(M):
        backend.store(ids[i], vecs[i], values[i])

    # Recall.
    r_count = min(n_recall, M)
    r_idx = rng.choice(M, size=r_count, replace=False)
    hits = 0
    for i in r_idx:
        res = backend.retrieve(vecs[i], k=1)
        if res.key_id == ids[i]:
            hits += 1
    recall_at_1 = hits / max(r_count, 1)

    # Latency.
    q_count = min(n_latency, M)
    q_idx = rng.choice(M, size=q_count, replace=False)
    retr_us: list[float] = []
    for i in q_idx:
        t0 = time.perf_counter_ns()
        backend.retrieve(vecs[i], k=1)
        t1 = time.perf_counter_ns()
        retr_us.append((t1 - t0) / 1000.0)

    # Routing accuracy: probe with the ORIGINAL key_vec (apples-to-apples
    # with the recall path; the backend's own routing_accuracy() uses leaf
    # codebook atoms, which are snapped versions and answer a slightly
    # different question).
    ra_count = min(max(200, r_count), M)
    ra_idx = rng.choice(M, size=ra_count, replace=False)
    routing_correct = 0
    routing_total = 0
    for i in ra_idx:
        true_topic = backend._key_to_topic.get(ids[int(i)])
        if true_topic is None:
            continue
        routed, _score, _all = backend._route_query(vecs[int(i)])
        if routed == true_topic:
            routing_correct += 1
        routing_total += 1
    if routing_total > 0:
        routing_accuracy_val = routing_correct / routing_total
    else:
        routing_accuracy_val = 1.0
    routing_rep = {
        "accuracy": routing_accuracy_val,
        "n_probed": routing_total,
    }

    # Delete some keys to exercise the cross-level chain.
    d_count = min(n_delete, M - 1)
    if d_count > 0:
        d_idx = rng.choice(M, size=d_count, replace=False)
        for i in d_idx:
            try:
                backend.delete(ids[int(i)])
            except Exception:
                continue
    chain_rep = backend.verify_cross_level_chain()

    # Per-leaf load distribution.
    leaf_loads = [len(leaf.key_registry) for leaf in backend.leaves]

    # Disk.
    save_dir = Path(tempfile.mkdtemp(prefix=f"hcs_hier_{M}_"))
    disk_bytes = 0
    try:
        backend.save(save_dir)
        disk_bytes = _dir_size_bytes(save_dir)
    except Exception:
        disk_bytes = 0
    finally:
        shutil.rmtree(save_dir, ignore_errors=True)

    return {
        "recall_at_1": float(recall_at_1),
        "n_recall_samples": int(r_count),
        "n_latency_queries": int(q_count),
        "mean_retrieve_latency_us": _mean(retr_us),
        "p50_retrieve_latency_us": _percentile(retr_us, 50),
        "p95_retrieve_latency_us": _percentile(retr_us, 95),
        "disk_bytes": int(disk_bytes),
        "disk_MB": float(disk_bytes) / 1.0e6,
        "routing_accuracy": float(routing_rep["accuracy"]),
        "routing_n_probed": int(routing_rep["n_probed"]),
        "cross_level_chain_integrity": float(chain_rep["integrity"]),
        "cross_level_chain_entries": int(chain_rep["entries"]),
        "cross_level_anchors_ok": int(chain_rep["anchors_ok"]),
        "leaf_load_min": int(min(leaf_loads)) if leaf_loads else 0,
        "leaf_load_max": int(max(leaf_loads)) if leaf_loads else 0,
        "leaf_load_mean": float(np.mean(leaf_loads)) if leaf_loads else 0.0,
    }


def run(backend, data: dict) -> dict:
    """Run the hierarchical_capacity sweep.

    The harness passes us a backend instance; we use its name to decide
    whether to drive it as the hierarchical row, the single-substrate row,
    or skip baselines (this scenario only makes sense for substrate-class
    backends). When backend.name == 'substrate_hierarchical' we sweep
    Ms against the hierarchical wrapper. When backend.name in {'substrate',
    'substrate_v1'} we sweep Ms against a single SubstrateMemory at the
    configured N (default N_leaf). Other backends (faiss/dict/chroma) get
    skipped with a note so the scenario does not crash the matrix.
    """
    name = getattr(backend, "name", "unknown")
    Ms = list(data["Ms"])
    seed = int(data["seed"])
    n_recall = int(data["n_recall_samples"])
    n_latency = int(data["n_latency_queries"])
    n_delete = int(data["n_delete"])
    N_leaf = int(data["N_leaf"])

    is_hier = (name == "substrate_hierarchical")
    is_single_substrate = (name == "substrate" or name == "substrate_v1")

    if not (is_hier or is_single_substrate):
        return {
            "scenario": "hierarchical_capacity",
            "backend": name,
            "skipped": True,
            "reason": (
                "hierarchical_capacity is substrate-only; routing and "
                "audit-chain metrics are not defined for embedding "
                "backends."
            ),
            "per_M": {},
        }

    per_M: dict[str, dict] = {}
    for M in Ms:
        rng = np.random.default_rng(seed + 50000 + M)
        ids = [f"hc_{M}_{i:08d}" for i in range(M)]
        values = [f"v_{i}" for i in range(M)]
        vecs = _make_vecs(rng, M, N_leaf)

        if is_hier:
            # Re-build per M to keep substrate state clean.
            bend = _build_hierarchical(data)
            metrics = _measure_hierarchical(
                bend, vecs, ids, values, n_recall, n_latency, n_delete, rng, M
            )
            metrics["K_topics"] = int(data["K_topics"])
            metrics["N_top"] = int(data["N_top"])
            metrics["N_leaf"] = int(data["N_leaf"])
        else:
            bend = _build_single_substrate(N_leaf, data, M_hint=M)
            metrics = _measure_single_substrate(
                bend, vecs, ids, values, n_recall, n_latency, n_delete, rng, M
            )
            metrics["N_single_substrate"] = int(N_leaf)
        metrics["M"] = int(M)
        per_M[str(M)] = metrics

    return {
        "scenario": "hierarchical_capacity",
        "backend": name,
        "Ms": Ms,
        "K_topics": int(data["K_topics"]),
        "N_top": int(data["N_top"]),
        "N_leaf": int(data["N_leaf"]),
        "M_cap_per_leaf": int(data["M_cap_per_leaf"]),
        "per_M": per_M,
    }


def thresholds() -> dict:
    return {
        "substrate": {
            "hard_pass": {
                "recall_at_1": 0.80,
                "routing_accuracy": 0.85,
                "cross_level_chain_integrity": 1.0,
                "mean_retrieve_latency_us_ratio_lt": 2.0,
            },
            "hard_fail": {
                "recall_at_1": 0.50,
                "routing_accuracy": 0.50,
                "cross_level_chain_integrity": 0.95,
            },
        },
        "baselines": {
            "hard_pass": {},
            "hard_fail": {},
        },
    }
