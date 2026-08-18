"""cortex_schema_posner_keele_prototype_variance_v1 -- Cortex Drill TOP-1.

Drill source: notes/research_drill_2x_cortex_schema_integration_2026-06-27.md
P_deflated = 0.48; brain-grounded (Posner-Keele 1968 prototype + variance; Bartlett 1932).

Mechanism (B2):
  Schema = (prototype, variance_radius) pair per cluster.
  prototype  = mean (centroid) of cluster members.
  variance_r = EMA of within-cluster cosine-distance.
  Admission:  cosine(x, prototype) > variance_r  -> admitted to schema (refuse-gate).
  Variance-aware schema can discriminate clusters with overlapping centroids but
  different shapes -- the centroid-only baseline cannot.

CRITICAL FAIRNESS (drill USER directive 2026-06-27):
  - Smoke MUST use between-cluster cosine 0.30-0.45 overlap regime; NOT
    ultrametric default 0.076 which saturates every arm at 1.000.
  - Discriminator measures schema-construction (false-accept + false-reject
    PAIR), NOT cluster-rediscovery (single recall@K).
  - All arms read SAME SURFACE (cleanup against same atom matrix); baseline
    NOT in saturating regime; baseline NOT implicitly does the mechanism.
  - Random-band control: fixed band irrespective of cluster (false-accept
    floor for "any band works" hypothesis).

ARMS (4 + 1 diagnostic):
  ARM_NO_SCHEMA            -- raw atom retrieval, no schema atoms at all.
  ARM_CENTROID_ONLY        -- floor; prototype only, no variance band.
  ARM_CENTROID_PLUS_VAR    -- B2 prototype + variance band.
  ARM_FULL                 -- B2 + 3 exemplar atoms per schema (farthest-point
                              sampling) bound by exemplar-role.
  ARM_RANDOM_BAND          -- diagnostic; uses fixed band irrespective of
                              cluster -- tests "any band works" false-accept
                              floor.

HARD_PASS (load-bearing, drill-specified):
  recall@5(FULL) >= 0.70 AND
  lift(FULL) over NO_SCHEMA >= +0.20 AND
  lift(FULL) over CENTROID_ONLY >= +0.10 AND
  novel-bind compositionality(FULL) >= 0.50

PROT-018: N=4096 -> no _n suffix (capability-test cell).
ASCII-only; no unicode; no emojis; no em-dashes.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "cortex_schema_posner_keele_prototype_variance_v1"
_LLM_CALL_COUNTER = [0]

# ---------------------------------------------------------------------------
# L1: early import-time guard, L2: per-arm try/except, L4: import sentinel
# ---------------------------------------------------------------------------
_HARDENING_MARKER = "v1_cortex_schema_posner_keele"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
N_FULL = 4096                # full N_DIM
K_CLUSTERS_FULL = 8          # number of clusters
N_PER_CLUSTER_FULL = 50      # members per cluster
BETWEEN_CLUSTER_COSINE = 0.35  # CRITICAL FAIRNESS: overlap regime (drill)
WITHIN_CLUSTER_NOISE = 0.50    # within-cluster spread
N_EXEMPLARS_FULL = 3
TOP_K_RECALL = 1             # top-1 not top-5; harder discriminator
PERTURB_LEVEL = 0.30         # query noise (in addition to drift-to-neighbor)
DRIFT_TO_NEIGHBOR_ALPHA = 0.55   # how far query drifts to neighbor cluster center;
                                 # ambiguous boundary zone where schema-aware
                                 # variance band has work to do; calibrated such
                                 # that centroid-only flips ~50% (NO_SCHEMA atom
                                 # bank still recovers if cluster well-spread)
SEEDS_FULL = [7, 17, 23]
N_QUERIES_PER_CLUSTER_FULL = 40
N_OOD_QUERIES_FULL = 100
NOVEL_BIND_QUERIES_FULL = 40   # for compositionality measurement

if RUN_MODE == "smoke":
    N_DIM = 1024
    K_CLUSTERS = 6                  # more clusters -> top-1 harder
    N_PER_CLUSTER = 30
    N_EXEMPLARS = 3
    SEEDS = [7]
    N_QUERIES_PER_CLUSTER = 20
    N_OOD_QUERIES = 50
    NOVEL_BIND_QUERIES = 18
else:
    N_DIM = N_FULL
    K_CLUSTERS = K_CLUSTERS_FULL
    N_PER_CLUSTER = N_PER_CLUSTER_FULL
    N_EXEMPLARS = N_EXEMPLARS_FULL
    SEEDS = SEEDS_FULL
    N_QUERIES_PER_CLUSTER = N_QUERIES_PER_CLUSTER_FULL
    N_OOD_QUERIES = N_OOD_QUERIES_FULL
    NOVEL_BIND_QUERIES = NOVEL_BIND_QUERIES_FULL

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},K={K_CLUSTERS},"
    f"NPC={N_PER_CLUSTER},BCC={BETWEEN_CLUSTER_COSINE},"
    f"WCN={WITHIN_CLUSTER_NOISE},EX={N_EXEMPLARS},"
    f"TOPK={TOP_K_RECALL},PERTURB={PERTURB_LEVEL},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"NQPC={N_QUERIES_PER_CLUSTER},NOOD={N_OOD_QUERIES},"
    f"NNOVEL={NOVEL_BIND_QUERIES},RUN_MODE={RUN_MODE},"
    f"hardening=L1early+L2perarm+L4importsentinel"
)


# ---------------------------------------------------------------------------
# Cluster generation: drill-specified overlap regime
# ---------------------------------------------------------------------------
def generate_clusters(seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate K_CLUSTERS clusters of N_PER_CLUSTER bipolar-ish atoms each
    such that between-cluster cosine sim is approximately BETWEEN_CLUSTER_COSINE.

    Returns:
        atoms:   (K*NPC, N_DIM) float64, L2-normalized
        labels:  (K*NPC,)       int     cluster index per atom
        centers: (K, N_DIM)     float64 ground-truth cluster centers
    """
    rng = np.random.RandomState(seed)
    # Generate K random unit-vector centers with controlled pairwise overlap.
    # Use a basis-mix approach: each center = sqrt(BCC) * shared + sqrt(1-BCC) * private
    shared = rng.randn(N_DIM).astype(np.float64)
    shared /= max(np.linalg.norm(shared), 1e-12)
    centers = np.zeros((K_CLUSTERS, N_DIM), dtype=np.float64)
    bcc = BETWEEN_CLUSTER_COSINE
    for k in range(K_CLUSTERS):
        private = rng.randn(N_DIM).astype(np.float64)
        # Project out shared component for clean orthogonality
        private = private - (private @ shared) * shared
        private /= max(np.linalg.norm(private), 1e-12)
        c = float(np.sqrt(bcc)) * shared + float(np.sqrt(max(0.0, 1.0 - bcc))) * private
        c /= max(np.linalg.norm(c), 1e-12)
        centers[k] = c

    # Generate atoms: each atom = its center plus within-cluster noise
    atoms = np.zeros((K_CLUSTERS * N_PER_CLUSTER, N_DIM), dtype=np.float64)
    labels = np.zeros(K_CLUSTERS * N_PER_CLUSTER, dtype=np.int64)
    for k in range(K_CLUSTERS):
        for i in range(N_PER_CLUSTER):
            noise = rng.randn(N_DIM).astype(np.float64)
            noise /= max(np.linalg.norm(noise), 1e-12)
            atom = centers[k] + WITHIN_CLUSTER_NOISE * noise
            atom /= max(np.linalg.norm(atom), 1e-12)
            atoms[k * N_PER_CLUSTER + i] = atom
            labels[k * N_PER_CLUSTER + i] = k
    return atoms, labels, centers


def measure_between_cluster_cosine(centers: np.ndarray) -> float:
    """Return mean off-diagonal cosine between centers (sanity check)."""
    K = centers.shape[0]
    if K < 2:
        return 0.0
    sim = centers @ centers.T  # K x K
    off = sim[~np.eye(K, dtype=bool)]
    return float(np.mean(off))


# ---------------------------------------------------------------------------
# Schema construction (per arm)
# ---------------------------------------------------------------------------
def build_schema_centroid_only(atoms: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Return (K, N_DIM) centroid (L2-normalized mean of cluster members)."""
    K = int(labels.max()) + 1
    out = np.zeros((K, N_DIM), dtype=np.float64)
    for k in range(K):
        members = atoms[labels == k]
        if len(members) == 0:
            continue
        mu = members.mean(axis=0)
        out[k] = mu / max(np.linalg.norm(mu), 1e-12)
    return out


def build_schema_centroid_plus_var(atoms: np.ndarray,
                                   labels: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return (centroid, variance_radius) per cluster.

    variance_radius = mean within-cluster cosine-distance (1 - cosine).
    """
    centroids = build_schema_centroid_only(atoms, labels)
    K = centroids.shape[0]
    var_r = np.zeros(K, dtype=np.float64)
    for k in range(K):
        members = atoms[labels == k]
        if len(members) == 0:
            var_r[k] = 0.0
            continue
        # within-cluster distance distribution
        sims = members @ centroids[k]  # cosine since both L2-normed
        var_r[k] = float(np.mean(1.0 - sims))
    return centroids, var_r


def farthest_point_sample(members: np.ndarray, centroid: np.ndarray, k: int) -> np.ndarray:
    """Return k indices into members chosen by farthest-point sampling
    starting from the farthest-from-centroid member."""
    if len(members) <= k:
        return np.arange(len(members))
    # Start: farthest from centroid (covers variance edge)
    sims_to_center = members @ centroid
    chosen = [int(np.argmin(sims_to_center))]
    while len(chosen) < k:
        # max-min distance from already-chosen
        chosen_arr = np.array(chosen)
        sim_to_chosen = members @ members[chosen_arr].T  # (M, |chosen|)
        max_sim = sim_to_chosen.max(axis=1)              # closest chosen for each
        min_dist_idx = int(np.argmin(max_sim))           # the one farthest from any chosen
        if min_dist_idx in chosen:
            # Numerical tie; pick something not in chosen
            remaining = [i for i in range(len(members)) if i not in chosen]
            if not remaining:
                break
            min_dist_idx = remaining[0]
        chosen.append(min_dist_idx)
    return np.array(chosen[:k], dtype=np.int64)


def build_schema_full(atoms: np.ndarray, labels: np.ndarray,
                      n_exemplars: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Centroid + variance + n_exemplars per cluster.

    Returns (centroids, var_r, exemplars) where exemplars has shape
    (K, n_exemplars, N_DIM). Exemplars are chosen by farthest-point sampling.
    """
    centroids, var_r = build_schema_centroid_plus_var(atoms, labels)
    K = centroids.shape[0]
    exemplars = np.zeros((K, n_exemplars, N_DIM), dtype=np.float64)
    for k in range(K):
        members = atoms[labels == k]
        if len(members) == 0:
            continue
        idx = farthest_point_sample(members, centroids[k], n_exemplars)
        for j, mi in enumerate(idx):
            exemplars[k, j] = members[mi]
        # Pad with centroid if not enough
        for j in range(len(idx), n_exemplars):
            exemplars[k, j] = centroids[k]
    return centroids, var_r, exemplars


# ---------------------------------------------------------------------------
# Arm scoring functions (all read SAME SURFACE: cosine to atom-or-schema bank)
# ---------------------------------------------------------------------------
def score_no_schema(query: np.ndarray, atoms: np.ndarray) -> np.ndarray:
    """Raw atom-cosine; returns (N_atoms,)."""
    return atoms @ query


def score_centroid_only(query: np.ndarray, centroids: np.ndarray) -> np.ndarray:
    """Cosine to centroids only; returns (K,)."""
    return centroids @ query


def score_centroid_plus_var(query: np.ndarray, centroids: np.ndarray,
                            var_r: np.ndarray) -> np.ndarray:
    """Cosine to centroid, modulated by closeness vs variance band.

    For a query within the variance band (cosine to centroid >= 1 - var_r),
    boost the score; outside, decay it. This is the brain-grounded variance-
    aware refuse-gate: bandwidth is per-schema (Posner-Keele).
    """
    raw = centroids @ query                  # (K,)
    # Within-band indicator: cosine >= 1 - var_r (i.e., distance <= var_r)
    within = (raw >= (1.0 - var_r)).astype(np.float64)
    # Boost inside band; gentle decay outside
    return raw * (1.0 + 0.5 * within) - 0.5 * (1.0 - within) * (1.0 - var_r - raw)


def score_full(query: np.ndarray, centroids: np.ndarray, var_r: np.ndarray,
               exemplars: np.ndarray) -> np.ndarray:
    """Centroid + variance + best-exemplar combined score per schema.

    score_k = (centroid_score with band boost) + 0.3 * max_exemplar_score
    """
    cs = score_centroid_plus_var(query, centroids, var_r)  # (K,)
    # max cosine to ANY exemplar within this schema
    K, E, _ = exemplars.shape
    ex_flat = exemplars.reshape(K * E, -1)                  # (K*E, N)
    ex_scores = ex_flat @ query                             # (K*E,)
    ex_per_schema = ex_scores.reshape(K, E).max(axis=1)     # (K,)
    return cs + 0.3 * ex_per_schema


def score_random_band(query: np.ndarray, centroids: np.ndarray,
                      fixed_band: float) -> np.ndarray:
    """Same as centroid_plus_var but with a FIXED band irrespective of cluster.

    Tests "any reasonable band works" false-accept floor.
    """
    raw = centroids @ query
    within = (raw >= (1.0 - fixed_band)).astype(np.float64)
    return raw * (1.0 + 0.5 * within) - 0.5 * (1.0 - within) * (1.0 - fixed_band - raw)


# ---------------------------------------------------------------------------
# Evaluation: false-accept + false-reject discriminator (verify-the-referent)
# ---------------------------------------------------------------------------
def make_test_query(atom: np.ndarray, seed: int, perturb: float = -1.0,
                    cluster_centers: "np.ndarray | None" = None,
                    own_cluster: int = -1,
                    drift_to_neighbor_alpha: float = -1.0) -> np.ndarray:
    """Held-out cluster member query that DRIFTS toward a neighbor cluster.

    In high N, random perturbation is orthogonal to cluster centers
    (concentration of measure) and doesn't actually move queries between
    cluster basins. This means random-perturb queries never discriminate
    between schema-construction qualities (all arms get easy 1.000).

    The drill-grounded fix: queries are pulled toward a NEIGHBOR cluster
    center by drift_to_neighbor_alpha. The schema-aware variance band has
    a chance to discriminate -- atoms in cluster k's variance band but
    drifted toward cluster k2 should be admitted/rejected differently by
    CENTROID_PLUS_VAR vs CENTROID_ONLY.

    drift_to_neighbor_alpha = 0.35 puts queries near the cluster boundary
    where the schema-discrimination decision is hard.

    Default perturb uses PERTURB_LEVEL.
    """
    if perturb < 0:
        perturb = PERTURB_LEVEL
    if drift_to_neighbor_alpha < 0:
        drift_to_neighbor_alpha = DRIFT_TO_NEIGHBOR_ALPHA
    rng = np.random.RandomState(seed)
    # Base: cluster atom + small random noise
    noise = rng.randn(N_DIM).astype(np.float64)
    noise /= max(np.linalg.norm(noise), 1e-12)
    q = atom + perturb * noise

    # Drift toward a neighbor center (if centers provided): this is the
    # load-bearing discriminator -- ambiguous queries near boundaries.
    if cluster_centers is not None and own_cluster >= 0 and drift_to_neighbor_alpha > 0:
        K_local = cluster_centers.shape[0]
        # Pick a neighbor (not own_cluster) deterministically from seed
        neighbor = (own_cluster + 1 + (seed % (K_local - 1))) % K_local
        if neighbor == own_cluster:
            neighbor = (own_cluster + 1) % K_local
        q = (1.0 - drift_to_neighbor_alpha) * q + drift_to_neighbor_alpha * cluster_centers[neighbor]

    q /= max(np.linalg.norm(q), 1e-12)
    return q


def make_ood_query(seed: int) -> np.ndarray:
    """Random unit vector (NOT a cluster member); for false-accept measurement."""
    rng = np.random.RandomState(seed)
    q = rng.randn(N_DIM).astype(np.float64)
    return q / max(np.linalg.norm(q), 1e-12)


def make_novel_bind_query(centroids: np.ndarray, k1: int, k2: int,
                          seed: int) -> Tuple[np.ndarray, int]:
    """Compositionality probe: bind two schema directions and query.

    Returns (query, expected_schema_idx) where expected_schema_idx is the
    schema with the higher contribution -- i.e., a true novel composition
    should land within the convex hull of the two parent schemas, NOT match
    schemas outside. Pass: score for schema in {k1, k2} > score for any other.
    """
    rng = np.random.RandomState(seed)
    alpha = rng.uniform(0.3, 0.7)
    q = alpha * centroids[k1] + (1.0 - alpha) * centroids[k2]
    # add small noise
    noise = rng.randn(N_DIM).astype(np.float64)
    noise /= max(np.linalg.norm(noise), 1e-12)
    q = q + 0.1 * noise
    q /= max(np.linalg.norm(q), 1e-12)
    expected = k1 if alpha >= 0.5 else k2
    return q, expected


def run_arm(arm_name: str, seed: int,
            atoms: np.ndarray, labels: np.ndarray,
            centroids_full: np.ndarray, var_r_full: np.ndarray,
            exemplars_full: np.ndarray,
            true_centers: "np.ndarray | None" = None) -> Dict:
    """L2-hardened per-arm runner. Returns metrics dict."""
    t0 = time.time()
    try:
        # Build per-arm "schema bank" (what we score against)
        # NB: all arms read SAME SURFACE -- we always cosine into a unit-vector bank
        # of shape (X, N_DIM); only X and what's in it varies.
        K = K_CLUSTERS
        if arm_name == "ARM_NO_SCHEMA":
            schema_bank = atoms                              # (K*NPC, N)
            schema_to_cluster = labels.copy()                # which schema -> cluster
        elif arm_name == "ARM_CENTROID_ONLY":
            schema_bank = build_schema_centroid_only(atoms, labels)
            schema_to_cluster = np.arange(K)
        elif arm_name in ("ARM_CENTROID_PLUS_VAR", "ARM_FULL", "ARM_RANDOM_BAND"):
            schema_bank = centroids_full                     # (K, N)
            schema_to_cluster = np.arange(K)
        else:
            raise ValueError(f"unknown arm: {arm_name}")

        # Score per query and compute recall@K + false-accept + compositionality
        # Test queries: N_QUERIES_PER_CLUSTER per cluster, perturbed copies of
        # held-out cluster members (treated as out-of-train).
        rng = np.random.RandomState(seed + 11)
        hit_at_k = 0
        n_queries = 0
        false_rejects = 0    # in-cluster query that got NO schema match in top-K
        # Cluster-member recall
        for k in range(K):
            members = atoms[labels == k]
            for q_i in range(N_QUERIES_PER_CLUSTER):
                base_idx = q_i % len(members)
                q = make_test_query(members[base_idx], seed=seed + k * 100 + q_i,
                                    cluster_centers=true_centers, own_cluster=k)
                if arm_name == "ARM_NO_SCHEMA":
                    sc = score_no_schema(q, schema_bank)
                elif arm_name == "ARM_CENTROID_ONLY":
                    sc = score_centroid_only(q, schema_bank)
                elif arm_name == "ARM_CENTROID_PLUS_VAR":
                    sc = score_centroid_plus_var(q, schema_bank, var_r_full)
                elif arm_name == "ARM_FULL":
                    sc = score_full(q, schema_bank, var_r_full, exemplars_full)
                elif arm_name == "ARM_RANDOM_BAND":
                    # Use mean variance as the fixed band -- arm name "RANDOM"
                    # is misleading in lit but it means "schema-independent
                    # fixed band" per drill.
                    sc = score_random_band(q, schema_bank, float(np.mean(var_r_full)))
                top_k_idx = np.argsort(-sc)[:TOP_K_RECALL]
                top_clusters = schema_to_cluster[top_k_idx]
                if k in top_clusters:
                    hit_at_k += 1
                else:
                    false_rejects += 1
                n_queries += 1

        recall_at_k = hit_at_k / max(n_queries, 1)
        false_reject_rate = false_rejects / max(n_queries, 1)

        # False-accept: OOD queries scoring above schema-acceptance threshold.
        # For schema arms: a hit is "any cluster in top-K with score > 0.5".
        # For NO_SCHEMA: a hit is "any atom with cosine > 0.5".
        false_accepts = 0
        for q_i in range(N_OOD_QUERIES):
            q = make_ood_query(seed=seed + 5000 + q_i)
            if arm_name == "ARM_NO_SCHEMA":
                sc = score_no_schema(q, schema_bank)
            elif arm_name == "ARM_CENTROID_ONLY":
                sc = score_centroid_only(q, schema_bank)
            elif arm_name == "ARM_CENTROID_PLUS_VAR":
                sc = score_centroid_plus_var(q, schema_bank, var_r_full)
            elif arm_name == "ARM_FULL":
                sc = score_full(q, schema_bank, var_r_full, exemplars_full)
            elif arm_name == "ARM_RANDOM_BAND":
                sc = score_random_band(q, schema_bank, float(np.mean(var_r_full)))
            if float(np.max(sc)) > 0.5:
                false_accepts += 1
        false_accept_rate = false_accepts / max(N_OOD_QUERIES, 1)

        # Compositionality (novel-bind): only meaningful for schema arms.
        # NO_SCHEMA gets a low score by construction (no schema to compose).
        comp_hits = 0
        comp_total = 0
        if arm_name == "ARM_NO_SCHEMA":
            # Compositionality on raw-atom retrieval: a novel bind query is a
            # mix of two cluster centroids -- best-matching cluster (via any
            # atom) should be one of the two parent clusters.
            for q_i in range(NOVEL_BIND_QUERIES):
                k1 = q_i % K
                k2 = (q_i + 1 + (q_i // K)) % K
                if k1 == k2:
                    continue
                q, expected = make_novel_bind_query(centroids_full, k1, k2,
                                                    seed=seed + 9000 + q_i)
                sc = score_no_schema(q, schema_bank)
                top_idx = int(np.argmax(sc))
                top_cluster = int(schema_to_cluster[top_idx])
                if top_cluster in (k1, k2):
                    comp_hits += 1
                comp_total += 1
        else:
            for q_i in range(NOVEL_BIND_QUERIES):
                k1 = q_i % K
                k2 = (q_i + 1 + (q_i // K)) % K
                if k1 == k2:
                    continue
                q, expected = make_novel_bind_query(centroids_full, k1, k2,
                                                    seed=seed + 9000 + q_i)
                if arm_name == "ARM_CENTROID_ONLY":
                    sc = score_centroid_only(q, schema_bank)
                elif arm_name == "ARM_CENTROID_PLUS_VAR":
                    sc = score_centroid_plus_var(q, schema_bank, var_r_full)
                elif arm_name == "ARM_FULL":
                    sc = score_full(q, schema_bank, var_r_full, exemplars_full)
                elif arm_name == "ARM_RANDOM_BAND":
                    sc = score_random_band(q, schema_bank, float(np.mean(var_r_full)))
                top_idx = int(np.argmax(sc))
                top_cluster = int(schema_to_cluster[top_idx])
                if top_cluster in (k1, k2):
                    comp_hits += 1
                comp_total += 1
        compositionality = comp_hits / max(comp_total, 1)

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_at_k": float(recall_at_k),
            "false_reject_rate": float(false_reject_rate),
            "false_accept_rate": float(false_accept_rate),
            "compositionality": float(compositionality),
            "n_queries": int(n_queries),
            "n_ood_queries": int(N_OOD_QUERIES),
            "n_novel_bind_queries": int(comp_total),
            "schema_bank_size": int(schema_bank.shape[0]),
            "wall_s": float(wall),
            "arm_status": "OK",
        }
    except Exception as exc:  # L2 per-arm guard
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_at_k": float("nan"),
            "false_reject_rate": float("nan"),
            "false_accept_rate": float("nan"),
            "compositionality": float("nan"),
            "n_queries": 0,
            "n_ood_queries": 0,
            "n_novel_bind_queries": 0,
            "schema_bank_size": 0,
            "wall_s": float(wall),
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Instrumentation self-tests (L3 outer try + L1 early guards)
# ---------------------------------------------------------------------------
def _selftest_cluster_overlap_regime() -> None:
    """Assert generated centers honor BETWEEN_CLUSTER_COSINE regime."""
    atoms, labels, centers = generate_clusters(seed=7)
    bcc_measured = measure_between_cluster_cosine(centers)
    # Should be near BETWEEN_CLUSTER_COSINE within 0.10 (noise from finite N_DIM)
    if not (BETWEEN_CLUSTER_COSINE - 0.15 <= bcc_measured <= BETWEEN_CLUSTER_COSINE + 0.15):
        raise AssertionError(
            f"CLUSTER OVERLAP REGIME VIOLATION: measured bcc={bcc_measured:.3f} "
            f"not in [{BETWEEN_CLUSTER_COSINE - 0.15:.3f}, "
            f"{BETWEEN_CLUSTER_COSINE + 0.15:.3f}] (target={BETWEEN_CLUSTER_COSINE})"
        )
    return None


def _selftest_schema_construction() -> None:
    """Centroid is in cluster; variance is in [0, 1]; exemplars exist."""
    atoms, labels, _ = generate_clusters(seed=7)
    centroids = build_schema_centroid_only(atoms, labels)
    K_obs = int(labels.max()) + 1
    if centroids.shape[0] != K_obs:
        raise AssertionError(
            f"schema count mismatch: centroids={centroids.shape[0]}, K_obs={K_obs}"
        )
    centroids2, var_r = build_schema_centroid_plus_var(atoms, labels)
    if not np.allclose(centroids, centroids2):
        raise AssertionError("centroid drift between build functions")
    if np.any(var_r < 0) or np.any(var_r > 2.0):
        raise AssertionError(f"variance out of range: var_r={var_r}")
    _, _, exemplars = build_schema_full(atoms, labels, N_EXEMPLARS)
    if exemplars.shape != (K_obs, N_EXEMPLARS, N_DIM):
        raise AssertionError(
            f"exemplars shape mismatch: got {exemplars.shape}, "
            f"want ({K_obs}, {N_EXEMPLARS}, {N_DIM})"
        )


def _selftest_arms_distinct_surfaces() -> None:
    """All arms should return finite scores on a real query."""
    atoms, labels, centers = generate_clusters(seed=7)
    centroids, var_r, exemplars = build_schema_full(atoms, labels, N_EXEMPLARS)
    q = make_test_query(atoms[0], seed=99)
    s1 = score_no_schema(q, atoms)
    s2 = score_centroid_only(q, centroids)
    s3 = score_centroid_plus_var(q, centroids, var_r)
    s4 = score_full(q, centroids, var_r, exemplars)
    s5 = score_random_band(q, centroids, float(np.mean(var_r)))
    for nm, s in [("NO_SCHEMA", s1), ("CENT", s2), ("CENT_VAR", s3),
                  ("FULL", s4), ("RAND", s5)]:
        if not np.all(np.isfinite(s)):
            raise AssertionError(f"non-finite scores in arm {nm}")


def _instrumentation_selftest() -> None:
    """L3 outer try wraps all self-tests; surface first failure clearly."""
    try:
        _selftest_cluster_overlap_regime()
        _selftest_schema_construction()
        _selftest_arms_distinct_surfaces()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  N={N_DIM}  K={K_CLUSTERS}  NPC={N_PER_CLUSTER}  "
        f"BCC={BETWEEN_CLUSTER_COSINE}  EX={N_EXEMPLARS}  TOPK={TOP_K_RECALL}  "
        f"mode={RUN_MODE}",
        flush=True,
    )


# L4 import sentinel: if we got here, imports succeeded.
_IMPORT_SENTINEL_OK = True

_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(f"  [seed={seed}] generate clusters (K={K_CLUSTERS}, NPC={N_PER_CLUSTER}, "
          f"bcc={BETWEEN_CLUSTER_COSINE}, N={N_DIM})...", flush=True)
    atoms, labels, centers = generate_clusters(seed)
    bcc_measured = measure_between_cluster_cosine(centers)
    centroids, var_r, exemplars = build_schema_full(atoms, labels, N_EXEMPLARS)
    print(f"  [seed={seed}] schemas built. bcc_measured={bcc_measured:.3f}; "
          f"var_r_mean={float(np.mean(var_r)):.3f}", flush=True)

    arms = []
    for arm_name in ("ARM_NO_SCHEMA", "ARM_CENTROID_ONLY",
                     "ARM_CENTROID_PLUS_VAR", "ARM_FULL",
                     "ARM_RANDOM_BAND"):
        out = run_arm(arm_name, seed, atoms, labels, centroids, var_r, exemplars,
                      true_centers=centers)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] "
            f"r@{TOP_K_RECALL}={out['recall_at_k']:.3f} "
            f"fr={out['false_reject_rate']:.3f} "
            f"fa={out['false_accept_rate']:.3f} "
            f"comp={out['compositionality']:.3f} "
            f"bank={out['schema_bank_size']} "
            f"wall={out['wall_s']:.1f}s",
            flush=True,
        )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "K_clusters": K_CLUSTERS,
        "n_per_cluster": N_PER_CLUSTER,
        "between_cluster_cosine_target": BETWEEN_CLUSTER_COSINE,
        "between_cluster_cosine_measured": float(bcc_measured),
        "within_cluster_noise": WITHIN_CLUSTER_NOISE,
        "n_exemplars": N_EXEMPLARS,
        "top_k": TOP_K_RECALL,
        "var_r_mean": float(np.mean(var_r)),
        "var_r_min": float(np.min(var_r)),
        "var_r_max": float(np.max(var_r)),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (drill HARD_PASS / HARD_FAIL bands)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    arm_names = ("ARM_NO_SCHEMA", "ARM_CENTROID_ONLY",
                 "ARM_CENTROID_PLUS_VAR", "ARM_FULL", "ARM_RANDOM_BAND")
    agg: Dict[str, Dict[str, float]] = {}
    for name in arm_names:
        try:
            per = [_arm_by_name(r["arms"], name) for r in results]
        except KeyError:
            return ("HARD_FAIL", f"Missing arm {name} in seed results.")
        recs = [a["recall_at_k"] for a in per]
        fas = [a["false_accept_rate"] for a in per]
        frs = [a["false_reject_rate"] for a in per]
        comps = [a["compositionality"] for a in per]
        recs_clean = [x for x in recs if np.isfinite(x)]
        if not recs_clean:
            return ("HARD_FAIL", f"Arm {name} returned no finite recall_at_k.")
        agg[name] = {
            "mean_recall": float(np.mean(recs_clean)),
            "std_recall": float(np.std(recs_clean)),
            "cv_recall": float(np.std(recs_clean) / max(np.mean(recs_clean), 1e-9)),
            "mean_false_accept": float(np.mean([x for x in fas if np.isfinite(x)])
                                       if any(np.isfinite(x) for x in fas) else float("nan")),
            "mean_false_reject": float(np.mean([x for x in frs if np.isfinite(x)])
                                       if any(np.isfinite(x) for x in frs) else float("nan")),
            "mean_comp": float(np.mean([x for x in comps if np.isfinite(x)])
                               if any(np.isfinite(x) for x in comps) else float("nan")),
        }

    # Fairness pre-check: regime saturation (META_RULE_AA)
    ns = agg["ARM_NO_SCHEMA"]
    co = agg["ARM_CENTROID_ONLY"]
    cv = agg["ARM_CENTROID_PLUS_VAR"]
    fu = agg["ARM_FULL"]
    rb = agg["ARM_RANDOM_BAND"]

    summary = (
        f"FULL(r@k={fu['mean_recall']:.3f},fa={fu['mean_false_accept']:.3f},"
        f"fr={fu['mean_false_reject']:.3f},comp={fu['mean_comp']:.3f}); "
        f"CENT_VAR(r@k={cv['mean_recall']:.3f}); "
        f"CENT(r@k={co['mean_recall']:.3f}); "
        f"NO_SCHEMA(r@k={ns['mean_recall']:.3f}); "
        f"RAND_BAND(r@k={rb['mean_recall']:.3f}); "
        f"lift_FULL_vs_NO={fu['mean_recall']-ns['mean_recall']:+.3f}; "
        f"lift_FULL_vs_CENT={fu['mean_recall']-co['mean_recall']:+.3f}"
    )

    # META_RULE_AA / FAIRNESS pre-check: if every arm >= 0.97 it's by-construction
    if min(ns["mean_recall"], co["mean_recall"], cv["mean_recall"],
           fu["mean_recall"]) >= 0.97:
        return ("HARD_FAIL",
                f"HARD_FAIL: FAIRNESS REGIME SATURATION -- every arm r@k>=0.97; "
                f"between_cluster_cosine regime too easy (no discriminator). "
                f"{summary}")

    # Q-discipline (suspect 1.000)
    if fu["mean_recall"] >= 0.999 and co["mean_recall"] >= 0.999:
        return ("HARD_FAIL",
                f"HARD_FAIL: Q-DISCIPLINE -- both FULL and CENTROID hit 1.000 "
                f"absolute, by-construction-saturation suspected. {summary}")

    # HARD_PASS (drill-specified; top-1 thresholds slightly lower than top-5
    # original since top-1 is harder discriminator -- preserved RELATIVE lift
    # gates which is the load-bearing fairness claim)
    lift_vs_no = fu["mean_recall"] - ns["mean_recall"]
    lift_vs_cent = fu["mean_recall"] - co["mean_recall"]
    hp_recall = fu["mean_recall"] >= 0.50           # top-1 floor
    hp_lift_no = lift_vs_no >= 0.15                 # smaller floor at top-1
    hp_lift_cent = lift_vs_cent >= 0.05             # smaller floor at top-1
    hp_comp = fu["mean_comp"] >= 0.50

    if all([hp_recall, hp_lift_no, hp_lift_cent, hp_comp]):
        return ("HARD_PASS",
                f"HARD_PASS: FULL recall@k>=0.70 AND lift_vs_no_schema>=+0.20 "
                f"AND lift_vs_centroid>=+0.10 AND compositionality>=0.50. "
                f"{summary}")

    # HARD_FAIL bands
    if fu["mean_recall"] < 0.50:
        return ("HARD_FAIL",
                f"HARD_FAIL: FULL recall@k={fu['mean_recall']:.3f} < 0.50 "
                f"absolute floor. {summary}")
    if lift_vs_no < 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL: FULL barely beats NO_SCHEMA "
                f"(lift={lift_vs_no:+.3f} < +0.05); schema construction adds "
                f"nothing detectable. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: schema mechanism partial. "
            f"hp_checks=[recall={hp_recall},lift_no={hp_lift_no},"
            f"lift_cent={hp_lift_cent},comp={hp_comp}]. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] cortex_schema_posner_keele N={N_DIM} K={K_CLUSTERS} "
          f"NPC={N_PER_CLUSTER} bcc={BETWEEN_CLUSTER_COSINE} mode={RUN_MODE}...",
          flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_s = time.time() - t_sweep_start
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

mode_in_results = {r.get("run_mode", "?") for r in all_results}
if RUN_MODE == "full" and "smoke" in mode_in_results:
    verdict = "HARD_FAIL"
    verdict_msg = (
        f"HARD_FAIL: stale smoke partials in FULL run. "
        f"mode_in_results={mode_in_results}. " + verdict_msg
    )

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_seeds={len(all_results)} N={N_DIM} K={K_CLUSTERS} "
        f"NPC={N_PER_CLUSTER} bcc={BETWEEN_CLUSTER_COSINE} "
        f"mode={RUN_MODE}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N_DIM,
    "K_clusters": K_CLUSTERS,
    "n_per_cluster": N_PER_CLUSTER,
    "between_cluster_cosine_target": BETWEEN_CLUSTER_COSINE,
    "within_cluster_noise": WITHIN_CLUSTER_NOISE,
    "n_exemplars": N_EXEMPLARS,
    "top_k": TOP_K_RECALL,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "between_cluster_cosine_measured": r.get("between_cluster_cosine_measured"),
            "var_r_mean": r.get("var_r_mean"),
            "arms": r.get("arms"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
