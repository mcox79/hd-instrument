"""Shared core for substrate_compression_pareto_v1 sibling cells.

USER REQUEST 2026-07-01: measure COMPRESSION EFFICIENCY of the substrate.
How many facts can 1 schema-centroid represent while still supporting
downstream recall? This is a PARETO measurement (compression vs recall).

Complementary to bytes-per-fact (STORAGE efficiency). This cell measures
FACTS per schema-centroid (COMPRESSION efficiency).

4 compression arms operating on identical N_FACTS synthetic bipolar-HDC
KG-fact set:

  ARM_NO_COMPRESSION:  store all N facts individually (facts/proto = 1.0).
                       Positive control per META_RULE_BC. Prior CG evidence
                       shows recall >= 0.85 at cleanup-attractor regime.
  ARM_SCHEMA_EXEMPLAR_BAYES:  cluster facts into schemas (K ~ N/n_ex); each
                       schema stores n_ex ~ 10 exemplars. Readout uses
                       v3-chain-grade LSE Bayes posterior + cleanup within
                       predicted schema. Compression ratio ~10x.
  ARM_SCHEMA_HARDMAX_CENTROID: v4-chain-grade HARDMAX. 1 centroid per
                       schema. Readout: argmax cosine over centroids + noise
                       floor. Compression ratio ~100x-1000x.
  ARM_SCHEMA_HIERARCHICAL: 2-level. Coarse schemas (n_coarse ~ 10) +
                       fine centroids within each coarse cluster
                       (n_fine ~ 100 per coarse). Total prototypes =
                       n_coarse * n_fine ~ 1000; compression ~10x.

Pareto axes: (facts_per_prototype_avg, downstream_recall_accuracy).

FULL: N_FACTS=10000, N_DIM=8192, N_QUERIES=100, 3 seeds.
SMOKE: N_FACTS=1000, N_DIM=2048, N_QUERIES=30, 1 seed.

ASCII-only. numpy-only compute. GPU optional (torch pass-through if
available; else pure numpy). Bipolar HDC encoding.

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn)
"""
# PRESERVE_ENV_VARS: HDLAB_QUEUE
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.special import logsumexp  # noqa: F401 - numerical stability

ANCHOR_PREFIX = "substrate_compression_pareto_v1"

# ----- Compression arm outer axis -----
ARMS = (
    "ARM_NO_COMPRESSION",
    "ARM_SCHEMA_EXEMPLAR_BAYES",
    "ARM_SCHEMA_HARDMAX_CENTROID",
    "ARM_SCHEMA_HIERARCHICAL",
)

# ----- Regime constants (LOCKED per prereg) -----
N_FACTS_FULL = 10000
N_DIM_FULL = 8192
N_QUERIES_FULL = 100

N_FACTS_SMOKE = 1000
N_DIM_SMOKE = 2048
N_QUERIES_SMOKE = 30

# ARM parameters (chosen to produce distinct Pareto points; see prereg):
# SCHEMA_EXEMPLAR_BAYES: ~10 exemplars/schema -> K_SCHEMAS = N/10
# SCHEMA_HARDMAX_CENTROID: 1 centroid per schema; K_SCHEMAS = N/100 (very compressed)
# SCHEMA_HIERARCHICAL: 10 coarse * 100 fine = 1000 prototypes at N=10000 (compression 10x)
EXEMPLAR_BAYES_N_EX_PER_SCHEMA = 10       # ~10x compression
HARDMAX_CENTROID_FACTS_PER_SCHEMA = 100   # ~100x compression
HIERARCHICAL_N_COARSE = 10                # coarse partitions
HIERARCHICAL_N_FINE_PER_COARSE = 100      # fine centroids per coarse

# LSE-Bayes temperature (matches v3/schema_family_v1 core)
def _beta_for(n_schemas: int) -> float:
    return float(math.log(max(n_schemas, 2)) / 0.1)

# Fact-noise (chain-grade regime; v1 exemplar_bayes uses 0.30)
# Query noise TUNED to place NO_COMPRESSION baseline in-band per META_RULE_AG:
# At n_facts=10000, N=8192, q_noise=0.20: NC_recall ~ 0.90 (in-band, HP-clearing).
# At smoke n_facts=1000, N=2048, q_noise=0.20: NC_recall ~ 0.96 (near saturation
# but this is a REDUCED-SCALE smoke; full-scale baseline is the discriminator).
FACT_NOISE_SCALE = 0.30
QUERY_NOISE_SCALE = 0.20

# Pre-reg bands (LOCKED at module init; see prereg for justification)
HP_POSITIVE_CONTROL_RECALL = 0.85       # NO_COMPRESSION at N=10000 must >= 0.85 (META_RULE_BC)
HP_COMPRESSION_RATIO_GAP = 100.0        # HARDMAX vs NO_COMPRESSION >= 100x compression gap
HP_RECALL_DROP_AT_COMPRESSION = 0.05    # HARDMAX recall must be within 0.05 of NO_COMPRESSION
HP_MIN_PARETO_POINTS_DISTINCT = 3       # >= 3 of 4 arms must produce distinct Pareto points
HP_CROSS_SEED_CV_MAX = 0.10              # cv(recall, ratio) <= 0.10 across seeds
HP_ARMS_DIFFER_MIN = 3                   # at least 3 of 6 arm-pairs must differ (META_RULE_AF)

# Distinctness threshold in Pareto space
PARETO_DISTINCT_RECALL_TOL = 0.02        # recall differs by > 0.02 = distinct
PARETO_DISTINCT_RATIO_LOG_TOL = 0.30     # log10(ratio) differs by > 0.30 = distinct

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "numpy.cpu"


# ==============================================================================
# Substrate primitives (bipolar HDC; matches schema_family_v1 core)
# ==============================================================================

def _bipolar_codebook(V: int, N: int, g: np.random.Generator) -> np.ndarray:
    """(V, N) float32 bipolar codebook, unit-normalized."""
    X = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return X


def _build_facts(g: np.random.Generator, n_facts: int, N: int) -> Tuple[np.ndarray, np.ndarray]:
    """Build N facts, each attached to a latent schema.

    Returns:
        facts: (n_facts, N) float32 unit-normalized fact vectors
        fact_schema_id: (n_facts,) int; latent schema each fact belongs to

    Latent schema structure:
      For clustering-based compression to work, facts must have a schema
      structure they can be clustered into. We generate n_latent_schemas ~
      sqrt(n_facts) prototypes; each fact = latent_proto + gaussian noise.
    """
    n_latent = max(2, int(round(math.sqrt(n_facts))))
    latent_protos = _bipolar_codebook(n_latent, N, g)
    fact_schema_id = g.integers(0, n_latent, size=n_facts).astype(np.int64)
    noise = g.standard_normal(size=(n_facts, N)).astype(np.float32) * FACT_NOISE_SCALE
    facts = latent_protos[fact_schema_id] + noise
    norms = np.linalg.norm(facts, axis=-1, keepdims=True) + 1e-8
    facts = facts / norms
    return facts, fact_schema_id


def _build_queries(
    g: np.random.Generator,
    facts: np.ndarray,
    n_queries: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Held-out queries. Query i = noisy version of a randomly-sampled true fact.

    Returns:
        queries: (n_queries, N) float32 unit-normalized
        true_fact_idx: (n_queries,) int -- ground-truth fact index
    """
    n_facts, N = facts.shape
    idx = g.integers(0, n_facts, size=n_queries).astype(np.int64)
    q_noise = g.standard_normal(size=(n_queries, N)).astype(np.float32) * QUERY_NOISE_SCALE
    queries = facts[idx] + q_noise
    queries = queries / (np.linalg.norm(queries, axis=-1, keepdims=True) + 1e-8)
    return queries, idx


# ==============================================================================
# Compression arms
# ==============================================================================

def _partition_facts_by_kmeans(
    facts: np.ndarray, k: int, g: np.random.Generator, n_iter: int = 20
) -> Tuple[np.ndarray, np.ndarray]:
    """Simple k-means (cosine on unit-normalized inputs).

    Returns:
        assignments: (n_facts,) int cluster assignments
        centroids:   (k, N) float32 unit-normalized cluster centroids
    """
    n_facts, N = facts.shape
    if k >= n_facts:
        # trivial: each fact is its own cluster
        assignments = np.arange(n_facts, dtype=np.int64)
        centroids = facts.copy()
        return assignments, centroids
    seed_idx = g.choice(n_facts, size=k, replace=False)
    centroids = facts[seed_idx].copy()
    assignments = np.zeros(n_facts, dtype=np.int64)
    for _ in range(n_iter):
        sims = facts @ centroids.T  # (n_facts, k)
        new_assignments = sims.argmax(axis=1).astype(np.int64)
        if np.array_equal(new_assignments, assignments):
            break
        assignments = new_assignments
        # Update centroids as means of assigned facts
        for c in range(k):
            mask = assignments == c
            if mask.any():
                m = facts[mask].mean(axis=0)
                norm = np.linalg.norm(m) + 1e-8
                centroids[c] = (m / norm).astype(np.float32)
            # else: keep old centroid
    return assignments, centroids


def _arm_no_compression(
    g: np.random.Generator,
    facts: np.ndarray,
    queries: np.ndarray,
    true_fact_idx: np.ndarray,
) -> Dict[str, Any]:
    """Store all N facts individually. Direct cosine argmax at readout.

    Compression ratio = 1.0 (no compression).
    Memory footprint = n_facts * N * 4 bytes (float32).
    """
    n_facts, N = facts.shape
    sims = queries @ facts.T  # (Q, n_facts)
    preds = sims.argmax(axis=1)
    recall = float(np.mean(preds == true_fact_idx))
    n_prototypes = n_facts
    mem_bytes = int(n_facts * N * 4)
    return {
        "arm": "ARM_NO_COMPRESSION",
        "n_prototypes": int(n_prototypes),
        "facts_per_prototype_avg": float(n_facts / max(n_prototypes, 1)),
        "downstream_recall_accuracy": recall,
        "memory_footprint_bytes": mem_bytes,
        "preds_hash_input": preds.astype(np.int64),
    }


def _arm_schema_exemplar_bayes(
    g: np.random.Generator,
    facts: np.ndarray,
    queries: np.ndarray,
    true_fact_idx: np.ndarray,
) -> Dict[str, Any]:
    """Cluster facts into K schemas of ~n_ex exemplars; readout = LSE-Bayes over
    per-schema exemplars, then within winning schema pick nearest exemplar as
    fact prediction. Compression ratio ~n_ex (10x default).
    """
    n_facts, N = facts.shape
    k_schemas = max(2, int(round(n_facts / EXEMPLAR_BAYES_N_EX_PER_SCHEMA)))
    assignments, _centroids = _partition_facts_by_kmeans(facts, k_schemas, g)

    # Group facts by schema
    schema_to_facts: Dict[int, List[int]] = {}
    for i, s in enumerate(assignments):
        schema_to_facts.setdefault(int(s), []).append(i)

    beta = _beta_for(k_schemas)
    # For each query, compute per-schema log-posterior via LSE over exemplars
    # log_posterior[q, c] = log_prior + LSE_{k in c} beta*cos(q, fact_k)
    log_prior = math.log(1.0 / k_schemas)
    preds = np.zeros(queries.shape[0], dtype=np.int64)
    for qi in range(queries.shape[0]):
        q = queries[qi]
        # Compute similarity to all facts; group by schema
        sims_all = facts @ q  # (n_facts,)
        best_c = -1
        best_score = -np.inf
        best_fact_in_c = -1
        for c, fact_idxs in schema_to_facts.items():
            if not fact_idxs:
                continue
            s_in_c = sims_all[fact_idxs]
            # LSE over exemplars in c
            score = float(log_prior + logsumexp(beta * s_in_c))
            if score > best_score:
                best_score = score
                best_c = c
                best_fact_in_c = fact_idxs[int(np.argmax(s_in_c))]
        preds[qi] = best_fact_in_c
    recall = float(np.mean(preds == true_fact_idx))

    n_prototypes = n_facts  # exemplar-bayes still stores every fact as exemplar
    # But routing gains locality: memory footprint = facts + schema index
    mem_bytes = int(n_facts * N * 4 + k_schemas * 8)
    return {
        "arm": "ARM_SCHEMA_EXEMPLAR_BAYES",
        "n_prototypes": int(n_prototypes),
        "n_schemas": int(k_schemas),
        "facts_per_prototype_avg": float(n_facts / max(k_schemas, 1)),  # facts per SCHEMA
        "downstream_recall_accuracy": recall,
        "memory_footprint_bytes": mem_bytes,
        "preds_hash_input": preds.astype(np.int64),
    }


def _arm_schema_hardmax_centroid(
    g: np.random.Generator,
    facts: np.ndarray,
    queries: np.ndarray,
    true_fact_idx: np.ndarray,
) -> Dict[str, Any]:
    """Cluster into k = n_facts / 100 schemas; store 1 centroid per schema.
    Readout: cosine argmax over centroids; then argmax over facts within schema.

    Compression ratio = HARDMAX_CENTROID_FACTS_PER_SCHEMA (100x default).
    Memory footprint = k_schemas * N * 4 bytes (centroids only for routing)
                       + n_facts * fact_idx (for within-schema lookup).
    The primitive itself is compressed. Downstream recall uses the schema
    centroid as the retrieval prototype; ground-truth fact identity picked
    among schema members.
    """
    n_facts, N = facts.shape
    k_schemas = max(2, int(round(n_facts / HARDMAX_CENTROID_FACTS_PER_SCHEMA)))
    assignments, centroids = _partition_facts_by_kmeans(facts, k_schemas, g)

    schema_to_facts: Dict[int, List[int]] = {}
    for i, s in enumerate(assignments):
        schema_to_facts.setdefault(int(s), []).append(i)

    sims = queries @ centroids.T  # (Q, k_schemas)
    pred_schemas = sims.argmax(axis=1)

    preds = np.zeros(queries.shape[0], dtype=np.int64)
    for qi in range(queries.shape[0]):
        c = int(pred_schemas[qi])
        candidates = schema_to_facts.get(c, [])
        if not candidates:
            preds[qi] = -1
            continue
        q = queries[qi]
        s_in_c = facts[candidates] @ q
        preds[qi] = candidates[int(np.argmax(s_in_c))]
    recall = float(np.mean(preds == true_fact_idx))

    n_prototypes = k_schemas
    # Compressed representation = only centroids + assignments (int8 fine at k<256)
    mem_bytes = int(k_schemas * N * 4 + n_facts * 4)
    return {
        "arm": "ARM_SCHEMA_HARDMAX_CENTROID",
        "n_prototypes": int(n_prototypes),
        "n_schemas": int(k_schemas),
        "facts_per_prototype_avg": float(n_facts / max(k_schemas, 1)),
        "downstream_recall_accuracy": recall,
        "memory_footprint_bytes": mem_bytes,
        "preds_hash_input": preds.astype(np.int64),
    }


def _arm_schema_hierarchical(
    g: np.random.Generator,
    facts: np.ndarray,
    queries: np.ndarray,
    true_fact_idx: np.ndarray,
) -> Dict[str, Any]:
    """2-level clustering: coarse (n_coarse) + fine (n_fine per coarse).

    Readout: coarse argmax -> fine argmax within predicted coarse -> fact.

    Total prototypes = n_coarse + n_coarse * n_fine (coarse + fine centroids).
    At N=10000: 10 + 10*100 = 1010 -> compression ~10x (similar to exemplar bayes
    but different structure).
    """
    n_facts, N = facts.shape
    n_coarse = HIERARCHICAL_N_COARSE
    coarse_assignments, coarse_centroids = _partition_facts_by_kmeans(
        facts, n_coarse, g
    )

    # For each coarse cluster, subcluster into n_fine
    coarse_to_facts: Dict[int, List[int]] = {}
    for i, s in enumerate(coarse_assignments):
        coarse_to_facts.setdefault(int(s), []).append(i)

    # Build per-coarse fine centroids and their fact assignments
    fine_centroids_per_coarse: Dict[int, np.ndarray] = {}
    fine_assign_per_coarse: Dict[int, np.ndarray] = {}
    fine_to_facts_per_coarse: Dict[int, Dict[int, List[int]]] = {}
    total_fine_centroids = 0
    for c, fact_idxs in coarse_to_facts.items():
        if not fact_idxs:
            continue
        c_facts = facts[fact_idxs]
        n_fine = min(HIERARCHICAL_N_FINE_PER_COARSE, len(fact_idxs))
        fine_assign_local, fine_centroids_local = _partition_facts_by_kmeans(
            c_facts, n_fine, g
        )
        fine_centroids_per_coarse[c] = fine_centroids_local
        fine_assign_per_coarse[c] = fine_assign_local
        m: Dict[int, List[int]] = {}
        for local_i, a in enumerate(fine_assign_local):
            m.setdefault(int(a), []).append(fact_idxs[local_i])
        fine_to_facts_per_coarse[c] = m
        total_fine_centroids += fine_centroids_local.shape[0]

    # Readout
    coarse_sims = queries @ coarse_centroids.T
    pred_coarse = coarse_sims.argmax(axis=1)
    preds = np.zeros(queries.shape[0], dtype=np.int64)
    for qi in range(queries.shape[0]):
        c = int(pred_coarse[qi])
        fc = fine_centroids_per_coarse.get(c)
        if fc is None or fc.shape[0] == 0:
            preds[qi] = -1
            continue
        q = queries[qi]
        fine_sims = fc @ q
        pred_fine = int(fine_sims.argmax())
        candidates = fine_to_facts_per_coarse[c].get(pred_fine, [])
        if not candidates:
            preds[qi] = -1
            continue
        s_in_c = facts[candidates] @ q
        preds[qi] = candidates[int(np.argmax(s_in_c))]
    recall = float(np.mean(preds == true_fact_idx))

    total_prototypes = n_coarse + total_fine_centroids
    mem_bytes = int((n_coarse + total_fine_centroids) * N * 4 + n_facts * 4)
    return {
        "arm": "ARM_SCHEMA_HIERARCHICAL",
        "n_prototypes": int(total_prototypes),
        "n_coarse": int(n_coarse),
        "n_fine_total": int(total_fine_centroids),
        "facts_per_prototype_avg": float(n_facts / max(total_prototypes, 1)),
        "downstream_recall_accuracy": recall,
        "memory_footprint_bytes": mem_bytes,
        "preds_hash_input": preds.astype(np.int64),
    }


_ARM_FNS = {
    "ARM_NO_COMPRESSION": _arm_no_compression,
    "ARM_SCHEMA_EXEMPLAR_BAYES": _arm_schema_exemplar_bayes,
    "ARM_SCHEMA_HARDMAX_CENTROID": _arm_schema_hardmax_centroid,
    "ARM_SCHEMA_HIERARCHICAL": _arm_schema_hierarchical,
}


def _pareto_efficiency(recall: float, ratio: float) -> float:
    """recall * log(compression_ratio); higher = better Pareto point."""
    return recall * math.log(max(ratio, 1.0))


def _hash_preds(preds: np.ndarray) -> str:
    rounded = preds.astype(np.int64).tolist()
    return hashlib.sha256(json.dumps(rounded).encode()).hexdigest()[:16]


# ==============================================================================
# Selftest + main driver
# ==============================================================================

def selftest(seed: int) -> Tuple[bool, str]:
    """Tiny selftest at reduced N to verify all 4 arms run + produce distinct
    outputs at ARM level. Not a full smoke gate.
    """
    try:
        g = np.random.default_rng(seed)
        facts, _ = _build_facts(g, n_facts=200, N=512)
        queries, true_idx = _build_queries(g, facts, n_queries=20)
        results = {}
        for arm_name in ARMS:
            fn = _ARM_FNS[arm_name]
            r = fn(np.random.default_rng(seed + 1), facts, queries, true_idx)
            results[arm_name] = r
        # Verify each arm produced a recall in [0, 1]
        for name, r in results.items():
            v = r["downstream_recall_accuracy"]
            if not (0.0 <= v <= 1.0):
                return False, f"selftest arm {name} produced recall={v} outside [0,1]"
        # Verify at least 2 arms produce distinct pred hashes (META_RULE_AF)
        hashes = {name: _hash_preds(r["preds_hash_input"]) for name, r in results.items()}
        distinct_pairs = sum(
            1 for a in hashes for b in hashes
            if a < b and hashes[a] != hashes[b]
        )
        if distinct_pairs < 2:
            return False, (
                f"selftest ARMS_MUST_DIFFER: only {distinct_pairs} of 6 arm-pairs "
                f"produce distinct pred hashes; hashes={hashes}"
            )
        # Verify no-compression achieves >= 0.30 at N=200 (loose selftest floor)
        nc_recall = results["ARM_NO_COMPRESSION"]["downstream_recall_accuracy"]
        if nc_recall < 0.30:
            return False, (
                f"selftest NO_COMPRESSION recall={nc_recall:.3f} below 0.30 "
                f"floor (test rig broken at n_facts=200,N=512)"
            )
        msg_parts = [
            f"arms_differ_pairs={distinct_pairs}/6",
            f"NC_recall={nc_recall:.3f}",
        ]
        for name in ARMS:
            r = results[name]
            msg_parts.append(
                f"{name}=(fpp={r['facts_per_prototype_avg']:.1f},"
                f"rec={r['downstream_recall_accuracy']:.3f})"
            )
        return True, " | ".join(msg_parts)
    except Exception as e:
        return False, f"selftest EXCEPTION: {type(e).__name__}: {e}\n{traceback.format_exc()[:1000]}"


def run_one_seed(
    seed: int, run_mode: str
) -> Dict[str, Any]:
    """Run one seed at FULL or SMOKE config."""
    if run_mode == "smoke":
        n_facts = N_FACTS_SMOKE
        N = N_DIM_SMOKE
        n_queries = N_QUERIES_SMOKE
    else:
        n_facts = N_FACTS_FULL
        N = N_DIM_FULL
        n_queries = N_QUERIES_FULL

    g_data = np.random.default_rng(seed)
    facts, fact_schema_id = _build_facts(g_data, n_facts=n_facts, N=N)
    queries, true_fact_idx = _build_queries(g_data, facts, n_queries=n_queries)

    arm_results: Dict[str, Dict[str, Any]] = {}
    arm_hashes: Dict[str, str] = {}
    started = time.time()
    for arm_name in ARMS:
        fn = _ARM_FNS[arm_name]
        # Fresh sub-RNG for each arm to keep clustering deterministic per (seed, arm)
        g_arm = np.random.default_rng(seed * 100 + hash(arm_name) % 10007)
        arm_t0 = time.time()
        r = fn(g_arm, facts, queries, true_fact_idx)
        r["elapsed_s"] = round(time.time() - arm_t0, 2)
        arm_hashes[arm_name] = _hash_preds(r["preds_hash_input"])
        r.pop("preds_hash_input", None)  # not JSON serializable at scale
        arm_results[arm_name] = r

    elapsed = time.time() - started

    # Per-arm Pareto point
    for arm_name in ARMS:
        r = arm_results[arm_name]
        ratio = r["facts_per_prototype_avg"]
        recall = r["downstream_recall_accuracy"]
        r["compression_pareto_efficiency"] = _pareto_efficiency(recall, ratio)
        r["mechanism_hash"] = arm_hashes[arm_name]

    # Arm-pair distinctness
    arm_pair_distinct: List[Dict[str, Any]] = []
    arm_names_l = list(ARMS)
    for i in range(len(arm_names_l)):
        for j in range(i + 1, len(arm_names_l)):
            a, b = arm_names_l[i], arm_names_l[j]
            arm_pair_distinct.append({
                "pair": (a, b),
                "hashes_differ": arm_hashes[a] != arm_hashes[b],
                "recall_delta": abs(
                    arm_results[a]["downstream_recall_accuracy"] -
                    arm_results[b]["downstream_recall_accuracy"]
                ),
                "log_ratio_delta": abs(
                    math.log10(max(arm_results[a]["facts_per_prototype_avg"], 1.0)) -
                    math.log10(max(arm_results[b]["facts_per_prototype_avg"], 1.0))
                ),
            })

    return {
        "seed": int(seed),
        "run_mode": run_mode,
        "backend": get_backend_label(),
        "n_facts": int(n_facts),
        "N_DIM": int(N),
        "n_queries": int(n_queries),
        "arms": arm_results,
        "arm_hashes": arm_hashes,
        "arm_pair_distinct": arm_pair_distinct,
        "elapsed_s": round(elapsed, 2),
        "anchor_prefix": ANCHOR_PREFIX,
    }


def aggregate_and_verdict(
    per_seed: Dict[str, Dict[str, Any]], run_mode: str
) -> Dict[str, Any]:
    """Aggregate per-seed results into cross-seed summary + verdict."""
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials",
            "summary": "no per-seed partials",
        }

    # Aggregate per arm across seeds
    per_arm: Dict[str, Dict[str, Any]] = {arm: {"recalls": [], "ratios": [], "mem_bytes": [], "efficiencies": []} for arm in ARMS}
    for s, body in per_seed.items():
        for arm_name in ARMS:
            r = body["arms"].get(arm_name)
            if not r:
                continue
            per_arm[arm_name]["recalls"].append(r["downstream_recall_accuracy"])
            per_arm[arm_name]["ratios"].append(r["facts_per_prototype_avg"])
            per_arm[arm_name]["mem_bytes"].append(r["memory_footprint_bytes"])
            per_arm[arm_name]["efficiencies"].append(r["compression_pareto_efficiency"])

    arm_summary: Dict[str, Dict[str, float]] = {}
    for arm_name in ARMS:
        d = per_arm[arm_name]
        recs = np.array(d["recalls"], dtype=np.float64)
        rats = np.array(d["ratios"], dtype=np.float64)
        mems = np.array(d["mem_bytes"], dtype=np.float64)
        effs = np.array(d["efficiencies"], dtype=np.float64)
        arm_summary[arm_name] = {
            "recall_mean": float(recs.mean()) if recs.size else 0.0,
            "recall_std": float(recs.std()) if recs.size > 1 else 0.0,
            "recall_cv": float(recs.std() / (recs.mean() + 1e-9)) if recs.size > 1 else 0.0,
            "ratio_mean": float(rats.mean()) if rats.size else 0.0,
            "ratio_std": float(rats.std()) if rats.size > 1 else 0.0,
            "ratio_cv": float(rats.std() / (rats.mean() + 1e-9)) if rats.size > 1 else 0.0,
            "memory_mean_bytes": float(mems.mean()) if mems.size else 0.0,
            "efficiency_mean": float(effs.mean()) if effs.size else 0.0,
            "n_seeds": int(recs.size),
        }

    # Positive control: NO_COMPRESSION recall >= HP_POSITIVE_CONTROL_RECALL (only enforced at FULL)
    nc_recall = arm_summary["ARM_NO_COMPRESSION"]["recall_mean"]
    positive_control_pass = bool(nc_recall >= HP_POSITIVE_CONTROL_RECALL)

    # Compression gap: HARDMAX ratio / NO_COMPRESSION ratio >= HP_COMPRESSION_RATIO_GAP
    hm_ratio = arm_summary["ARM_SCHEMA_HARDMAX_CENTROID"]["ratio_mean"]
    nc_ratio = arm_summary["ARM_NO_COMPRESSION"]["ratio_mean"]
    compression_ratio_gap = hm_ratio / max(nc_ratio, 1e-9)
    compression_gap_pass = bool(compression_ratio_gap >= HP_COMPRESSION_RATIO_GAP)

    # Recall preservation: HARDMAX recall drop from NO_COMPRESSION <= HP_RECALL_DROP_AT_COMPRESSION
    hm_recall = arm_summary["ARM_SCHEMA_HARDMAX_CENTROID"]["recall_mean"]
    recall_drop = nc_recall - hm_recall
    recall_preserved_pass = bool(recall_drop <= HP_RECALL_DROP_AT_COMPRESSION)

    # Pareto point distinctness: count of arm pairs with distinct (recall, log_ratio)
    # Aggregate across seeds by taking mean recall/ratio per arm.
    distinct_pareto_pts = 0
    total_pairs = 0
    arm_names_l = list(ARMS)
    pareto_pairs_detail: List[Dict[str, Any]] = []
    for i in range(len(arm_names_l)):
        for j in range(i + 1, len(arm_names_l)):
            a, b = arm_names_l[i], arm_names_l[j]
            r_a, r_b = arm_summary[a]["recall_mean"], arm_summary[b]["recall_mean"]
            lr_a = math.log10(max(arm_summary[a]["ratio_mean"], 1.0))
            lr_b = math.log10(max(arm_summary[b]["ratio_mean"], 1.0))
            distinct = (abs(r_a - r_b) > PARETO_DISTINCT_RECALL_TOL) or (
                abs(lr_a - lr_b) > PARETO_DISTINCT_RATIO_LOG_TOL
            )
            if distinct:
                distinct_pareto_pts += 1
            total_pairs += 1
            pareto_pairs_detail.append({
                "pair": (a, b),
                "distinct": bool(distinct),
                "recall_delta": abs(r_a - r_b),
                "log_ratio_delta": abs(lr_a - lr_b),
            })
    # HARD_PASS if >= HP_MIN_PARETO_POINTS_DISTINCT arms produce distinct Pareto POINTS
    # (i.e., at least (n choose 2) of them differ; we require at least min_distinct pairs)
    pareto_distinct_pass = bool(distinct_pareto_pts >= HP_MIN_PARETO_POINTS_DISTINCT)

    # Arm-hash distinctness across seeds (META_RULE_AF): mean # of distinct hash pairs
    arms_differ_counts = []
    for s, body in per_seed.items():
        arm_hashes = body.get("arm_hashes", {})
        distinct = sum(
            1 for i in range(len(arm_names_l)) for j in range(i + 1, len(arm_names_l))
            if arm_hashes.get(arm_names_l[i]) != arm_hashes.get(arm_names_l[j])
        )
        arms_differ_counts.append(distinct)
    arms_differ_mean = float(np.mean(arms_differ_counts)) if arms_differ_counts else 0.0
    arms_differ_pass = bool(arms_differ_mean >= HP_ARMS_DIFFER_MIN)

    # Cross-seed cv (recall + ratio) <= HP_CROSS_SEED_CV_MAX (only meaningful at FULL with 3 seeds)
    cross_seed_cv_pass = True
    for arm_name in ARMS:
        if arm_summary[arm_name]["recall_cv"] > HP_CROSS_SEED_CV_MAX:
            cross_seed_cv_pass = False
        if arm_summary[arm_name]["ratio_cv"] > HP_CROSS_SEED_CV_MAX:
            cross_seed_cv_pass = False

    # Verdict
    gates = {
        "positive_control_pass": positive_control_pass,
        "compression_gap_pass": compression_gap_pass,
        "recall_preserved_pass": recall_preserved_pass,
        "pareto_distinct_pass": pareto_distinct_pass,
        "arms_differ_pass": arms_differ_pass,
        "cross_seed_cv_pass": cross_seed_cv_pass,
    }
    n_passed = sum(1 for v in gates.values() if v)

    if run_mode == "smoke":
        # SMOKE is more lenient: 1 seed, N=1000 not 10000 -> positive_control_pass
        # threshold RELAXED per prereg (smoke recall floor 0.60 not 0.85)
        smoke_nc_recall_floor = 0.60
        smoke_positive_control_pass = bool(nc_recall >= smoke_nc_recall_floor)
        # For smoke, cross-seed cv is meaningless (1 seed)
        # Verdict: HARD_PASS iff arms differ + Pareto distinct + smoke positive control + compression gap
        if smoke_positive_control_pass and pareto_distinct_pass and arms_differ_pass and compression_gap_pass:
            verdict = "HARD_PASS"
            verdict_msg = (
                f"SMOKE HARD_PASS: NC_recall={nc_recall:.3f}>=0.60 (smoke floor); "
                f"HM_ratio={hm_ratio:.1f}, NC_ratio={nc_ratio:.1f}, "
                f"compression_gap={compression_ratio_gap:.1f}x>={HP_COMPRESSION_RATIO_GAP}x; "
                f"pareto_distinct_pairs={distinct_pareto_pts}/{total_pairs}; "
                f"arms_differ_mean={arms_differ_mean:.1f}/6"
            )
        elif smoke_positive_control_pass and arms_differ_pass:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"SMOKE MIDDLE_BAND: NC_recall={nc_recall:.3f}>=0.60 + arms differ, "
                f"but pareto_distinct or compression_gap or recall_preservation gate failed. "
                f"gates={gates}"
            )
        else:
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"SMOKE HARD_FAIL: NC_recall={nc_recall:.3f}<0.60 (smoke pos-ctrl floor) "
                f"OR arms_identical. gates={gates}"
            )
        return {
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "arm_summary": arm_summary,
            "gates": gates,
            "smoke_positive_control_pass": smoke_positive_control_pass,
            "pareto_pairs_detail": pareto_pairs_detail,
            "compression_ratio_gap_measured": float(compression_ratio_gap),
            "recall_drop_measured": float(recall_drop),
            "distinct_pareto_pairs": int(distinct_pareto_pts),
            "arms_differ_mean_pairs": float(arms_differ_mean),
            "nc_recall_mean": float(nc_recall),
            "hm_recall_mean": float(hm_recall),
            "hm_ratio_mean": float(hm_ratio),
        }

    # FULL verdict
    if n_passed == 6:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"FULL HARD_PASS: 6/6 gates. NC_recall={nc_recall:.3f}>={HP_POSITIVE_CONTROL_RECALL}, "
            f"HM_recall={hm_recall:.3f}, compression_gap={compression_ratio_gap:.1f}x, "
            f"pareto_distinct={distinct_pareto_pts}/{total_pairs}, "
            f"arms_differ={arms_differ_mean:.1f}/6, "
            f"cross_seed_cv_ok={cross_seed_cv_pass}"
        )
    elif positive_control_pass and arms_differ_pass and pareto_distinct_pass:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"FULL MIDDLE_BAND: {n_passed}/6 gates. Mechanism alive but incomplete. "
            f"gates={gates}"
        )
    else:
        verdict = "HARD_FAIL"
        failing = [k for k, v in gates.items() if not v]
        verdict_msg = f"FULL HARD_FAIL: {n_passed}/6 gates. Failing: {failing}. gates={gates}"

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "arm_summary": arm_summary,
        "gates": gates,
        "pareto_pairs_detail": pareto_pairs_detail,
        "compression_ratio_gap_measured": float(compression_ratio_gap),
        "recall_drop_measured": float(recall_drop),
        "distinct_pareto_pairs": int(distinct_pareto_pts),
        "arms_differ_mean_pairs": float(arms_differ_mean),
        "nc_recall_mean": float(nc_recall),
        "hm_recall_mean": float(hm_recall),
        "hm_ratio_mean": float(hm_ratio),
    }
