"""cortex_schema_tonegawa_sparse_ensemble_v2 -- Cortex Drill TOP-2.

Drill source: notes/research_drill_2x_cortex_schema_integration_2026-06-27.md
P_deflated = 0.42; brain-grounded (Tonegawa engram cells; k-WTA sparse coding).

Mechanism (B3 -- sparse ensemble):
  Schema = k-WTA sparse code over N_SCHEMA_CELLS = 2000 schema-cell population.
  Each cluster activates k = 20 of N (1% sparsity; Treves-Rolls a*log(1/a) ceiling).
  Schema-cell population is a fixed random projection W_schema: R^N_DIM -> R^N_SCHEMA
  shared across all clusters but the k-WTA selection is per-cluster (orthogonal-ish
  sparse codes give bounded inter-schema interference a priori).
  Query at retrieval: x -> W_schema @ x; top-k indices form query-sparse-code; match
  against schema bank by sparse-overlap (intersection count / k).
  Capacity@95%-recall is primary metric (vs prototype's similarity-cosine).

v2 vs v1 (Posner-Keele prototype + variance):
  v1 HARD_FAILed regime calibration: drift_to_neighbor_alpha=0.55 forced
  CENTROID_ONLY recall->0 (every query pulled into wrong basin); NO_SCHEMA
  collapsed to 0.108 not the [0.20, 0.50] fair floor; mechanism never had a
  chance because the baseline regime was wrong.
  v2 fixes:
   - drift_to_neighbor_alpha = 0.25 (calibrated so NO_SCHEMA lands in fair band)
   - SPARSE ENSEMBLE schema (not centroid+variance)
   - 5 arms: NO_SCHEMA / PROTOTYPE_CENTROID / TONEGAWA_K20 / TONEGAWA_K10 / DIAG_RANDOM_SPARSE
   - Capacity@95% as secondary (primary still recall@top-K for fairness band-check)

CRITICAL FAIRNESS (drill USER directive 2026-06-27):
  - Smoke MUST use between-cluster cosine 0.30-0.45 overlap regime; NOT
    ultrametric default 0.076 which saturates every arm at 1.000.
  - All arms read SAME SURFACE (cluster-bank score); only schema BUILD differs.
  - NO_SCHEMA baseline lands in [0.20, 0.50] band (chance + clutter floor).
  - PROTOTYPE_CENTROID lands in [0.40, 0.75] band (intermediate fair).
  - TONEGAWA_SPARSE differentiates by >= +0.10 over PROTOTYPE OR fails fairly.
  - DIAG_RANDOM_SPARSE acts as false-accept ceiling; must NOT pass at >= 0.50.
  - W_schema projection is FIXED RANDOM, NOT trained on test atoms (no leakage).

ARMS (3+ mandatory + 2 diagnostic):
  ARM_NO_SCHEMA              -- raw atom retrieval; fair floor.
  ARM_PROTOTYPE_CENTROID     -- v1's CENTROID arm; direct v1-vs-v2 comparison.
  ARM_TONEGAWA_SPARSE_K20    -- B3 mechanism (k=20 of N=2000; 1% sparsity).
  ARM_TONEGAWA_SPARSE_K10    -- sparser variant (k=10 of N=2000; 0.5%); k-sensitivity.
  ARM_DIAG_RANDOM_SPARSE_K20 -- random k-subset per cluster (no structure);
                                false-accept floor.

HARD_PASS (task-specified):
  TONEGAWA_K20 recall@5 >= 0.70 AND
  lift over PROTOTYPE_CENTROID >= +0.10 AND
  lift over NO_SCHEMA >= +0.20 AND
  DIAG_RANDOM_SPARSE < 0.30 AND
  cv < 0.10

HARD_FAIL:
  any baseline saturates >= 0.95 OR cv >= 0.20 OR DIAG_RANDOM_SPARSE >= 0.50
  OR cardinality breach (observed arms < expected)

REGIME:
  N_DIM=2000 (per drill k=sqrt(N) ~20)
  N_CAT=50 clusters (full); 8 clusters (smoke; small enough to fire discriminator)
  N_PER_CAT=10 members per cluster
  between_cluster_cosine in [0.30, 0.45]

PROT-018: N=2000 -> no _n suffix (capability-test cell).
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


ANCHOR_NAME = "cortex_schema_tonegawa_sparse_ensemble_v2"
_LLM_CALL_COUNTER = [0]

# L1 early import guard, L2 per-arm try/except, L4 import sentinel, META_RULE_X main-guard
_HARDENING_MARKER = "v2_cortex_schema_tonegawa_sparse_ensemble"

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
# Full regime: per drill TOP-2 spec (N=2000, k=sqrt(N)~20)
N_DIM_FULL = 2000
N_SCHEMA_CELLS_FULL = 2000      # schema-cell population for k-WTA
K_CLUSTERS_FULL = 50            # 50 clusters per task spec
N_PER_CLUSTER_FULL = 10         # 10 members per cluster
K_SPARSE_FULL = 20              # k=20 of N=2000 (1% sparsity; Tonegawa-grounded)
K_SPARSE_SMALL_FULL = 10        # diagnostic sparser variant (k=10; 0.5%)
SEEDS_FULL = [7, 17, 23]
N_QUERIES_PER_CLUSTER_FULL = 20
TOP_K_RECALL = 5                # task spec: recall@5

# Regime parameters (FAIRNESS-critical)
BETWEEN_CLUSTER_COSINE = 0.45   # drill: overlap regime [0.30, 0.45]; pushed to TOP of range
WITHIN_CLUSTER_NOISE = 0.70     # within-cluster spread; harder than v1's 0.50
PERTURB_LEVEL = 0.50            # query random noise; harder than v1's 0.30
DRIFT_TO_NEIGHBOR_ALPHA = 0.45  # v2: between v1's 0.55 and v2-first-attempt 0.25
N_OOD_QUERIES_FULL = 100        # for false-accept measurement

# CARDINALITY_OK: arms expected (META_RULE_H discipline)
EXPECTED_ARMS = (
    "ARM_NO_SCHEMA",
    "ARM_PROTOTYPE_CENTROID",
    "ARM_TONEGAWA_SPARSE_K20",
    "ARM_TONEGAWA_SPARSE_K10",
    "ARM_DIAG_RANDOM_SPARSE_K20",
)
EXPECTED_N_ARMS = len(EXPECTED_ARMS)

if RUN_MODE == "smoke":
    # Smoke: K_CLUSTERS=100 + small N=1024 simulates the FULL-N capacity regime.
    # Per drill TOP-2: Tonegawa sparse-ensemble's bet is bounded interference
    # at LARGE K. K=40 leaves baselines unsaturated (1.000); K=100 with
    # N_DIM=1024 drives capacity pressure into the substrate, baselines drop,
    # sparse-ensemble has a chance to win. This is the discriminator regime
    # (USER 2026-06-26 "smoke must fire the discriminator").
    N_DIM = 1024
    N_SCHEMA_CELLS = 1024      # match N_DIM
    K_CLUSTERS = 100           # capacity-pressure regime (~10% of N_DIM)
    N_PER_CLUSTER = 8          # keep total atoms manageable
    K_SPARSE = 20              # SAME as full (k pre-registered; not tuned)
    K_SPARSE_SMALL = 10        # SAME as full
    SEEDS = [7]
    N_QUERIES_PER_CLUSTER = 10
    N_OOD_QUERIES = 30
else:
    N_DIM = N_DIM_FULL
    N_SCHEMA_CELLS = N_SCHEMA_CELLS_FULL
    K_CLUSTERS = K_CLUSTERS_FULL
    N_PER_CLUSTER = N_PER_CLUSTER_FULL
    K_SPARSE = K_SPARSE_FULL
    K_SPARSE_SMALL = K_SPARSE_SMALL_FULL
    SEEDS = SEEDS_FULL
    N_QUERIES_PER_CLUSTER = N_QUERIES_PER_CLUSTER_FULL
    N_OOD_QUERIES = N_OOD_QUERIES_FULL

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},NSCH={N_SCHEMA_CELLS},K={K_CLUSTERS},"
    f"NPC={N_PER_CLUSTER},KSP={K_SPARSE},KSPS={K_SPARSE_SMALL},"
    f"BCC={BETWEEN_CLUSTER_COSINE},WCN={WITHIN_CLUSTER_NOISE},"
    f"TOPK={TOP_K_RECALL},PERTURB={PERTURB_LEVEL},DRIFT={DRIFT_TO_NEIGHBOR_ALPHA},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"NQPC={N_QUERIES_PER_CLUSTER},NOOD={N_OOD_QUERIES},RUN_MODE={RUN_MODE},"
    f"hardening=L1early+L2perarm+L4importsentinel+CARDINALITY_OK"
)


# ---------------------------------------------------------------------------
# Cluster generation (same as v1; drill-specified overlap regime)
# ---------------------------------------------------------------------------
def generate_clusters(seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate K_CLUSTERS clusters of N_PER_CLUSTER atoms.

    Returns:
        atoms:   (K*NPC, N_DIM) float64 L2-normalized
        labels:  (K*NPC,)       int     cluster idx per atom
        centers: (K, N_DIM)     float64 ground-truth centers
    """
    rng = np.random.RandomState(seed)
    shared = rng.randn(N_DIM).astype(np.float64)
    shared /= max(np.linalg.norm(shared), 1e-12)
    centers = np.zeros((K_CLUSTERS, N_DIM), dtype=np.float64)
    bcc = BETWEEN_CLUSTER_COSINE
    for k in range(K_CLUSTERS):
        private = rng.randn(N_DIM).astype(np.float64)
        private = private - (private @ shared) * shared
        private /= max(np.linalg.norm(private), 1e-12)
        c = float(np.sqrt(bcc)) * shared + float(np.sqrt(max(0.0, 1.0 - bcc))) * private
        c /= max(np.linalg.norm(c), 1e-12)
        centers[k] = c

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
    """Mean off-diagonal cosine; sanity check."""
    K = centers.shape[0]
    if K < 2:
        return 0.0
    sim = centers @ centers.T
    off = sim[~np.eye(K, dtype=bool)]
    return float(np.mean(off))


# ---------------------------------------------------------------------------
# W_schema: FIXED random projection for k-WTA encoding (separate from W_episodic).
# Drill fairness: SHARED-W BUG TRAP avoided -- W is a fresh random projection
# generated per-seed; never trained on the test atoms.
# ---------------------------------------------------------------------------
def make_W_schema(seed: int) -> np.ndarray:
    """W_schema: (N_SCHEMA_CELLS, N_DIM); each row a unit-vector schema-cell
    receptive field. Fixed random; no training; separate seed offset so it's
    decoupled from cluster generation."""
    rng = np.random.RandomState(seed + 31337)
    W = rng.randn(N_SCHEMA_CELLS, N_DIM).astype(np.float64)
    # Normalize each row to unit length (each schema cell sees unit-projection)
    norms = np.linalg.norm(W, axis=1, keepdims=True)
    W = W / np.maximum(norms, 1e-12)
    return W


def k_wta_encode(x: np.ndarray, W: np.ndarray, k: int) -> np.ndarray:
    """k-WTA sparse encoding of x.

    Returns a sparse binary vector of shape (N_SCHEMA_CELLS,) with exactly k
    ones at the top-k activations. (1 = cell fires; 0 = silent.)
    """
    activations = W @ x  # (N_SCHEMA_CELLS,)
    # top-k indices
    if k >= activations.shape[0]:
        return np.ones(activations.shape[0], dtype=np.float64)
    top_k_idx = np.argpartition(-activations, k)[:k]
    sparse = np.zeros(activations.shape[0], dtype=np.float64)
    sparse[top_k_idx] = 1.0
    return sparse


def build_schema_tonegawa(atoms: np.ndarray, labels: np.ndarray,
                          W: np.ndarray, k: int) -> np.ndarray:
    """Sparse-ensemble schema per cluster.

    For each cluster: encode the centroid via k-WTA -> get k-sparse binary
    schema-code. Bank shape: (K, N_SCHEMA_CELLS).
    """
    K = int(labels.max()) + 1
    bank = np.zeros((K, N_SCHEMA_CELLS), dtype=np.float64)
    for c in range(K):
        members = atoms[labels == c]
        if len(members) == 0:
            continue
        # Cluster centroid (then k-WTA encode it)
        mu = members.mean(axis=0)
        mu = mu / max(np.linalg.norm(mu), 1e-12)
        bank[c] = k_wta_encode(mu, W, k)
    return bank


def build_schema_random_sparse(seed: int, K: int, k: int) -> np.ndarray:
    """Diagnostic: random k-subset per cluster (no structure).

    Tests false-accept floor: if random sparse codes match queries, the
    mechanism is not actually doing anything load-bearing.
    """
    rng = np.random.RandomState(seed + 99999)
    bank = np.zeros((K, N_SCHEMA_CELLS), dtype=np.float64)
    for c in range(K):
        idx = rng.choice(N_SCHEMA_CELLS, size=min(k, N_SCHEMA_CELLS), replace=False)
        bank[c, idx] = 1.0
    return bank


def build_schema_centroid_only(atoms: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Prototype centroid per cluster (v1's CENTROID arm)."""
    K = int(labels.max()) + 1
    out = np.zeros((K, N_DIM), dtype=np.float64)
    for k in range(K):
        members = atoms[labels == k]
        if len(members) == 0:
            continue
        mu = members.mean(axis=0)
        out[k] = mu / max(np.linalg.norm(mu), 1e-12)
    return out


# ---------------------------------------------------------------------------
# Query construction (matches v1 for direct comparison; lower drift in v2)
# ---------------------------------------------------------------------------
def make_test_query(atom: np.ndarray, seed: int,
                    cluster_centers: "np.ndarray | None" = None,
                    own_cluster: int = -1) -> np.ndarray:
    """Held-out cluster-member query with random perturb + gentle drift to neighbor."""
    rng = np.random.RandomState(seed)
    noise = rng.randn(N_DIM).astype(np.float64)
    noise /= max(np.linalg.norm(noise), 1e-12)
    q = atom + PERTURB_LEVEL * noise

    if cluster_centers is not None and own_cluster >= 0 and DRIFT_TO_NEIGHBOR_ALPHA > 0:
        K_local = cluster_centers.shape[0]
        neighbor = (own_cluster + 1 + (seed % max(K_local - 1, 1))) % K_local
        if neighbor == own_cluster:
            neighbor = (own_cluster + 1) % K_local
        q = (1.0 - DRIFT_TO_NEIGHBOR_ALPHA) * q + DRIFT_TO_NEIGHBOR_ALPHA * cluster_centers[neighbor]

    q /= max(np.linalg.norm(q), 1e-12)
    return q


def make_ood_query(seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    q = rng.randn(N_DIM).astype(np.float64)
    return q / max(np.linalg.norm(q), 1e-12)


# ---------------------------------------------------------------------------
# Scoring per arm: ALL READ SAME SURFACE (cosine-equivalent into bank)
# ---------------------------------------------------------------------------
def score_no_schema(q: np.ndarray, atoms: np.ndarray) -> np.ndarray:
    """Raw atom cosine -> per-atom score (then aggregated to per-cluster outside)."""
    return atoms @ q


def score_centroid(q: np.ndarray, centroids: np.ndarray) -> np.ndarray:
    """Cosine to centroid per cluster -> (K,) scores."""
    return centroids @ q


def score_tonegawa_sparse(q: np.ndarray, sparse_bank: np.ndarray,
                          W: np.ndarray, k: int) -> np.ndarray:
    """Encode q via same k-WTA; score = sparse-code overlap (intersection / k).

    Returns (K,) per-cluster overlap scores.
    """
    q_sparse = k_wta_encode(q, W, k)  # (N_SCHEMA_CELLS,)
    # overlap = sum of pointwise product (since both are 0/1) -> intersection count
    overlap = sparse_bank @ q_sparse  # (K,)
    # Normalize by k to land in [0, 1]
    return overlap / max(float(k), 1.0)


# ---------------------------------------------------------------------------
# Per-arm runner (L2 try/except hardening)
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int,
            atoms: np.ndarray, labels: np.ndarray,
            true_centers: np.ndarray,
            centroids: np.ndarray,
            W: np.ndarray,
            sparse_bank_k20: np.ndarray,
            sparse_bank_k10: np.ndarray,
            random_sparse_bank: np.ndarray) -> Dict:
    """Per-arm runner; returns metrics dict."""
    t0 = time.time()
    try:
        K = K_CLUSTERS
        # Schema-bank size diagnostic (capacity hint)
        if arm_name == "ARM_NO_SCHEMA":
            schema_bank_size = atoms.shape[0]
        elif arm_name == "ARM_PROTOTYPE_CENTROID":
            schema_bank_size = centroids.shape[0]
        elif arm_name == "ARM_TONEGAWA_SPARSE_K20":
            schema_bank_size = sparse_bank_k20.shape[0]
        elif arm_name == "ARM_TONEGAWA_SPARSE_K10":
            schema_bank_size = sparse_bank_k10.shape[0]
        elif arm_name == "ARM_DIAG_RANDOM_SPARSE_K20":
            schema_bank_size = random_sparse_bank.shape[0]
        else:
            raise ValueError(f"unknown arm: {arm_name}")

        # ----- Recall@TOP_K -----
        hits = 0
        n_queries = 0
        false_rejects = 0
        for c in range(K):
            members = atoms[labels == c]
            for q_i in range(N_QUERIES_PER_CLUSTER):
                base_idx = q_i % len(members)
                q = make_test_query(members[base_idx], seed=seed + c * 100 + q_i,
                                    cluster_centers=true_centers, own_cluster=c)

                if arm_name == "ARM_NO_SCHEMA":
                    # raw-atom scores -> per-cluster max
                    atom_scores = score_no_schema(q, atoms)
                    cluster_scores = np.zeros(K, dtype=np.float64)
                    for cc in range(K):
                        cluster_scores[cc] = atom_scores[labels == cc].max()
                elif arm_name == "ARM_PROTOTYPE_CENTROID":
                    cluster_scores = score_centroid(q, centroids)
                elif arm_name == "ARM_TONEGAWA_SPARSE_K20":
                    cluster_scores = score_tonegawa_sparse(q, sparse_bank_k20, W, K_SPARSE)
                elif arm_name == "ARM_TONEGAWA_SPARSE_K10":
                    cluster_scores = score_tonegawa_sparse(q, sparse_bank_k10, W, K_SPARSE_SMALL)
                elif arm_name == "ARM_DIAG_RANDOM_SPARSE_K20":
                    cluster_scores = score_tonegawa_sparse(q, random_sparse_bank, W, K_SPARSE)

                top_k_clusters = np.argsort(-cluster_scores)[:TOP_K_RECALL]
                if c in top_k_clusters:
                    hits += 1
                else:
                    false_rejects += 1
                n_queries += 1

        recall_at_k = hits / max(n_queries, 1)
        false_reject_rate = false_rejects / max(n_queries, 1)

        # ----- False-accept (OOD queries) -----
        # For schema arms: hit = any cluster score > 0.5 (sparse score natively in [0,1];
        # cosine score also in [-1,1], so 0.5 is a clean threshold for both).
        false_accepts = 0
        for q_i in range(N_OOD_QUERIES):
            q = make_ood_query(seed + 5000 + q_i)
            if arm_name == "ARM_NO_SCHEMA":
                sc = score_no_schema(q, atoms)
                max_score = float(sc.max())
            elif arm_name == "ARM_PROTOTYPE_CENTROID":
                sc = score_centroid(q, centroids)
                max_score = float(sc.max())
            elif arm_name == "ARM_TONEGAWA_SPARSE_K20":
                sc = score_tonegawa_sparse(q, sparse_bank_k20, W, K_SPARSE)
                max_score = float(sc.max())
            elif arm_name == "ARM_TONEGAWA_SPARSE_K10":
                sc = score_tonegawa_sparse(q, sparse_bank_k10, W, K_SPARSE_SMALL)
                max_score = float(sc.max())
            elif arm_name == "ARM_DIAG_RANDOM_SPARSE_K20":
                sc = score_tonegawa_sparse(q, random_sparse_bank, W, K_SPARSE)
                max_score = float(sc.max())
            if max_score > 0.5:
                false_accepts += 1
        false_accept_rate = false_accepts / max(N_OOD_QUERIES, 1)

        # ----- Capacity@95%-recall (drill TOP-2 primary; here computed as
        # secondary since fairness recall@5 is the headline). Capacity =
        # max number of clusters such that mean recall stays >= 0.95.
        # Compute by greedy cluster-set increase: K=1, K=2, ..., until recall < 0.95.
        # For brevity we report a single capacity_estimate as the threshold-K.
        capacity_at_95 = -1
        try:
            for k_test in range(1, K + 1):
                test_hits = 0
                test_total = 0
                for c in range(k_test):
                    members = atoms[labels == c]
                    for q_i in range(min(N_QUERIES_PER_CLUSTER, 5)):
                        base_idx = q_i % len(members)
                        q = make_test_query(members[base_idx],
                                            seed=seed + c * 100 + q_i,
                                            cluster_centers=true_centers,
                                            own_cluster=c)
                        if arm_name == "ARM_NO_SCHEMA":
                            atom_scores = score_no_schema(q, atoms)
                            cluster_scores = np.zeros(k_test, dtype=np.float64)
                            for cc in range(k_test):
                                cluster_scores[cc] = atom_scores[labels == cc].max()
                        elif arm_name == "ARM_PROTOTYPE_CENTROID":
                            cluster_scores = score_centroid(q, centroids[:k_test])
                        elif arm_name == "ARM_TONEGAWA_SPARSE_K20":
                            cluster_scores = score_tonegawa_sparse(
                                q, sparse_bank_k20[:k_test], W, K_SPARSE)
                        elif arm_name == "ARM_TONEGAWA_SPARSE_K10":
                            cluster_scores = score_tonegawa_sparse(
                                q, sparse_bank_k10[:k_test], W, K_SPARSE_SMALL)
                        elif arm_name == "ARM_DIAG_RANDOM_SPARSE_K20":
                            cluster_scores = score_tonegawa_sparse(
                                q, random_sparse_bank[:k_test], W, K_SPARSE)
                        top_idx = int(np.argmax(cluster_scores))
                        if top_idx == c:
                            test_hits += 1
                        test_total += 1
                test_recall = test_hits / max(test_total, 1)
                if test_recall >= 0.95:
                    capacity_at_95 = k_test
                else:
                    break  # capacity reached
        except Exception:
            capacity_at_95 = -1

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_at_k": float(recall_at_k),
            "false_reject_rate": float(false_reject_rate),
            "false_accept_rate": float(false_accept_rate),
            "capacity_at_95": int(capacity_at_95),
            "n_queries": int(n_queries),
            "n_ood_queries": int(N_OOD_QUERIES),
            "schema_bank_size": int(schema_bank_size),
            "wall_s": float(wall),
            "arm_status": "OK",
        }
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_at_k": float("nan"),
            "false_reject_rate": float("nan"),
            "false_accept_rate": float("nan"),
            "capacity_at_95": -1,
            "n_queries": 0,
            "n_ood_queries": 0,
            "schema_bank_size": 0,
            "wall_s": float(wall),
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Self-tests (L3 outer try + L1 early guards)
# ---------------------------------------------------------------------------
def _selftest_cluster_overlap_regime() -> None:
    atoms, labels, centers = generate_clusters(seed=7)
    bcc_measured = measure_between_cluster_cosine(centers)
    if not (BETWEEN_CLUSTER_COSINE - 0.15 <= bcc_measured <= BETWEEN_CLUSTER_COSINE + 0.15):
        raise AssertionError(
            f"CLUSTER OVERLAP REGIME VIOLATION: measured bcc={bcc_measured:.3f} "
            f"not in [{BETWEEN_CLUSTER_COSINE - 0.15:.3f}, "
            f"{BETWEEN_CLUSTER_COSINE + 0.15:.3f}] (target={BETWEEN_CLUSTER_COSINE})"
        )


def _selftest_kwta_sparsity() -> None:
    """k-WTA encoder produces EXACTLY k ones (verify-the-referent)."""
    W = make_W_schema(seed=7)
    rng = np.random.RandomState(123)
    x = rng.randn(N_DIM).astype(np.float64)
    x /= max(np.linalg.norm(x), 1e-12)
    sparse = k_wta_encode(x, W, K_SPARSE)
    n_ones = int(sparse.sum())
    if n_ones != K_SPARSE:
        raise AssertionError(
            f"k-WTA SPARSITY VIOLATION: expected k={K_SPARSE} ones; got {n_ones}"
        )
    if not np.all((sparse == 0.0) | (sparse == 1.0)):
        raise AssertionError(f"k-WTA NOT BINARY: unique values = {np.unique(sparse)}")


def _selftest_schema_bank_shapes() -> None:
    atoms, labels, _ = generate_clusters(seed=7)
    W = make_W_schema(seed=7)
    K_obs = int(labels.max()) + 1
    centroids = build_schema_centroid_only(atoms, labels)
    if centroids.shape != (K_obs, N_DIM):
        raise AssertionError(f"centroids shape mismatch: {centroids.shape}")
    bank_k20 = build_schema_tonegawa(atoms, labels, W, K_SPARSE)
    if bank_k20.shape != (K_obs, N_SCHEMA_CELLS):
        raise AssertionError(f"tonegawa_k20 bank shape mismatch: {bank_k20.shape}")
    bank_random = build_schema_random_sparse(seed=7, K=K_obs, k=K_SPARSE)
    if bank_random.shape != (K_obs, N_SCHEMA_CELLS):
        raise AssertionError(f"random_sparse bank shape mismatch: {bank_random.shape}")
    # Random-sparse should NOT equal tonegawa (mechanism-not-trivial check)
    if np.allclose(bank_random, bank_k20):
        raise AssertionError(
            "random_sparse_bank == tonegawa_bank: diagnostic arm is trivially equal"
        )


def _selftest_arms_distinct_surfaces() -> None:
    atoms, labels, centers = generate_clusters(seed=7)
    W = make_W_schema(seed=7)
    centroids = build_schema_centroid_only(atoms, labels)
    bank_k20 = build_schema_tonegawa(atoms, labels, W, K_SPARSE)
    bank_k10 = build_schema_tonegawa(atoms, labels, W, K_SPARSE_SMALL)
    bank_rand = build_schema_random_sparse(seed=7, K=K_CLUSTERS, k=K_SPARSE)
    q = make_test_query(atoms[0], seed=99, cluster_centers=centers, own_cluster=0)
    s1 = score_no_schema(q, atoms)
    s2 = score_centroid(q, centroids)
    s3 = score_tonegawa_sparse(q, bank_k20, W, K_SPARSE)
    s4 = score_tonegawa_sparse(q, bank_k10, W, K_SPARSE_SMALL)
    s5 = score_tonegawa_sparse(q, bank_rand, W, K_SPARSE)
    for nm, s in [("NO_SCHEMA", s1), ("CENT", s2), ("TON_K20", s3),
                  ("TON_K10", s4), ("RAND", s5)]:
        if not np.all(np.isfinite(s)):
            raise AssertionError(f"non-finite scores in arm {nm}")


def _instrumentation_selftest() -> None:
    try:
        _selftest_cluster_overlap_regime()
        _selftest_kwta_sparsity()
        _selftest_schema_bank_shapes()
        _selftest_arms_distinct_surfaces()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  N={N_DIM}  NSCH={N_SCHEMA_CELLS}  K={K_CLUSTERS}  "
        f"NPC={N_PER_CLUSTER}  KSP={K_SPARSE}  KSPS={K_SPARSE_SMALL}  "
        f"BCC={BETWEEN_CLUSTER_COSINE}  DRIFT={DRIFT_TO_NEIGHBOR_ALPHA}  "
        f"TOPK={TOP_K_RECALL}  mode={RUN_MODE}",
        flush=True,
    )


# L4 import sentinel
_IMPORT_SENTINEL_OK = True


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(f"  [seed={seed}] generate clusters (K={K_CLUSTERS}, NPC={N_PER_CLUSTER}, "
          f"bcc={BETWEEN_CLUSTER_COSINE}, N={N_DIM})...", flush=True)
    atoms, labels, centers = generate_clusters(seed)
    bcc_measured = measure_between_cluster_cosine(centers)
    print(f"  [seed={seed}] bcc_measured={bcc_measured:.3f}", flush=True)

    W = make_W_schema(seed)
    print(f"  [seed={seed}] W_schema built ({N_SCHEMA_CELLS}x{N_DIM} random projection)",
          flush=True)

    centroids = build_schema_centroid_only(atoms, labels)
    sparse_bank_k20 = build_schema_tonegawa(atoms, labels, W, K_SPARSE)
    sparse_bank_k10 = build_schema_tonegawa(atoms, labels, W, K_SPARSE_SMALL)
    random_sparse_bank = build_schema_random_sparse(seed=seed, K=K_CLUSTERS, k=K_SPARSE)
    print(f"  [seed={seed}] schemas built: centroid({centroids.shape}), "
          f"tonegawa_k20({sparse_bank_k20.shape}), tonegawa_k10({sparse_bank_k10.shape}), "
          f"random_sparse({random_sparse_bank.shape})",
          flush=True)

    arms = []
    for arm_name in EXPECTED_ARMS:
        out = run_arm(arm_name, seed, atoms, labels, centers,
                      centroids, W, sparse_bank_k20, sparse_bank_k10,
                      random_sparse_bank)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] "
            f"r@{TOP_K_RECALL}={out['recall_at_k']:.3f} "
            f"fa={out['false_accept_rate']:.3f} "
            f"fr={out['false_reject_rate']:.3f} "
            f"cap@95={out['capacity_at_95']} "
            f"bank={out['schema_bank_size']} "
            f"wall={out['wall_s']:.1f}s",
            flush=True,
        )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "N_schema_cells": N_SCHEMA_CELLS,
        "K_clusters": K_CLUSTERS,
        "n_per_cluster": N_PER_CLUSTER,
        "k_sparse": K_SPARSE,
        "k_sparse_small": K_SPARSE_SMALL,
        "between_cluster_cosine_target": BETWEEN_CLUSTER_COSINE,
        "between_cluster_cosine_measured": float(bcc_measured),
        "within_cluster_noise": WITHIN_CLUSTER_NOISE,
        "drift_to_neighbor_alpha": DRIFT_TO_NEIGHBOR_ALPHA,
        "top_k": TOP_K_RECALL,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_arms_observed": len(arms),
        "n_arms_expected": EXPECTED_N_ARMS,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (task-specified HARD_PASS / HARD_FAIL bands)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    # CARDINALITY_OK gate (META_RULE_H): every seed must observe expected arms
    for r in results:
        if r.get("n_arms_observed") != EXPECTED_N_ARMS:
            return (
                "HARD_FAIL",
                f"HARD_FAIL: CARDINALITY BREACH: seed={r.get('seed')} "
                f"observed n_arms={r.get('n_arms_observed')} != "
                f"expected {EXPECTED_N_ARMS}"
            )

    agg: Dict[str, Dict[str, float]] = {}
    for name in EXPECTED_ARMS:
        try:
            per = [_arm_by_name(r["arms"], name) for r in results]
        except KeyError:
            return ("HARD_FAIL", f"Missing arm {name} in seed results.")
        recs = [a["recall_at_k"] for a in per]
        fas = [a["false_accept_rate"] for a in per]
        caps = [a["capacity_at_95"] for a in per]
        recs_clean = [x for x in recs if np.isfinite(x)]
        if not recs_clean:
            return ("HARD_FAIL", f"Arm {name} returned no finite recall_at_k.")
        agg[name] = {
            "mean_recall": float(np.mean(recs_clean)),
            "std_recall": float(np.std(recs_clean)),
            "cv_recall": float(np.std(recs_clean) / max(np.mean(recs_clean), 1e-9)),
            "mean_false_accept": float(np.mean([x for x in fas if np.isfinite(x)])
                                       if any(np.isfinite(x) for x in fas)
                                       else float("nan")),
            "mean_capacity_at_95": float(np.mean([x for x in caps if x >= 0])
                                         if any(x >= 0 for x in caps)
                                         else -1.0),
        }

    ns = agg["ARM_NO_SCHEMA"]
    pc = agg["ARM_PROTOTYPE_CENTROID"]
    t20 = agg["ARM_TONEGAWA_SPARSE_K20"]
    t10 = agg["ARM_TONEGAWA_SPARSE_K10"]
    rs = agg["ARM_DIAG_RANDOM_SPARSE_K20"]

    summary = (
        f"TONEGAWA_K20(r@k={t20['mean_recall']:.3f},cv={t20['cv_recall']:.3f},"
        f"cap@95={t20['mean_capacity_at_95']:.1f}); "
        f"TONEGAWA_K10(r@k={t10['mean_recall']:.3f}); "
        f"PROTOTYPE(r@k={pc['mean_recall']:.3f}); "
        f"NO_SCHEMA(r@k={ns['mean_recall']:.3f}); "
        f"DIAG_RANDOM(r@k={rs['mean_recall']:.3f}); "
        f"lift_T20_vs_PROTO={t20['mean_recall']-pc['mean_recall']:+.3f}; "
        f"lift_T20_vs_NO={t20['mean_recall']-ns['mean_recall']:+.3f}; "
        f"fa_T20={t20['mean_false_accept']:.3f}"
    )

    # ----- FAIRNESS GATES (META_RULE_AA; FIRE BEFORE MECHANISM GATES) -----

    # 1. Saturation: if any baseline saturates >= 0.95, regime too easy.
    for name, ag in (("NO_SCHEMA", ns), ("PROTOTYPE", pc), ("DIAG_RANDOM", rs)):
        if ag["mean_recall"] >= 0.95:
            return (
                "HARD_FAIL",
                f"HARD_FAIL: FAIRNESS REGIME SATURATION -- baseline {name} "
                f"r@k={ag['mean_recall']:.3f} >= 0.95; regime too easy. {summary}"
            )

    # 2. DIAG_RANDOM_SPARSE false-accept ceiling
    if rs["mean_recall"] >= 0.50:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: DIAG_RANDOM_SPARSE r@k={rs['mean_recall']:.3f} >= 0.50 "
            f"-- random sparse codes accept too much; sparse-code mechanism is "
            f"trivially-attainable. {summary}"
        )

    # 3. CV check (high-variance results not trustworthy)
    if t20["cv_recall"] >= 0.20:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: TONEGAWA_K20 cv={t20['cv_recall']:.3f} >= 0.20 "
            f"-- too noisy across seeds. {summary}"
        )

    # ----- MECHANISM GATES (HARD_PASS) -----
    hp_recall = t20["mean_recall"] >= 0.70
    hp_lift_proto = (t20["mean_recall"] - pc["mean_recall"]) >= 0.10
    hp_lift_no = (t20["mean_recall"] - ns["mean_recall"]) >= 0.20
    hp_diag_floor = rs["mean_recall"] < 0.30
    hp_cv = t20["cv_recall"] < 0.10

    if all([hp_recall, hp_lift_proto, hp_lift_no, hp_diag_floor, hp_cv]):
        return (
            "HARD_PASS",
            f"HARD_PASS: TONEGAWA_K20 r@5>=0.70 AND lift_vs_PROTOTYPE>=+0.10 AND "
            f"lift_vs_NO_SCHEMA>=+0.20 AND DIAG_RANDOM<0.30 AND cv<0.10. {summary}"
        )

    # ----- HARD_FAIL bands -----
    if t20["mean_recall"] < 0.30:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: TONEGAWA_K20 r@k={t20['mean_recall']:.3f} < 0.30 "
            f"absolute floor. {summary}"
        )
    if (t20["mean_recall"] - pc["mean_recall"]) < 0.0:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: TONEGAWA_K20 underperforms PROTOTYPE "
            f"(lift={t20['mean_recall']-pc['mean_recall']:+.3f}); sparse-ensemble "
            f"mechanism worse than centroid baseline. {summary}"
        )

    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: hp_checks=[recall>=0.70:{hp_recall},"
        f"lift_proto>=0.10:{hp_lift_proto},lift_no>=0.20:{hp_lift_no},"
        f"diag<0.30:{hp_diag_floor},cv<0.10:{hp_cv}]. {summary}"
    )


# ---------------------------------------------------------------------------
# Main driver (META_RULE_X: instrumentation_selftest fires BEFORE main work)
# ---------------------------------------------------------------------------
def main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds complete; running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] cortex_schema_tonegawa N={N_DIM} K={K_CLUSTERS} "
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
            f"n_seeds={len(all_results)} N={N_DIM} NSCH={N_SCHEMA_CELLS} "
            f"K={K_CLUSTERS} NPC={N_PER_CLUSTER} kSP={K_SPARSE} "
            f"bcc={BETWEEN_CLUSTER_COSINE} mode={RUN_MODE}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N_DIM,
        "N_schema_cells": N_SCHEMA_CELLS,
        "K_clusters": K_CLUSTERS,
        "n_per_cluster": N_PER_CLUSTER,
        "k_sparse": K_SPARSE,
        "k_sparse_small": K_SPARSE_SMALL,
        "between_cluster_cosine_target": BETWEEN_CLUSTER_COSINE,
        "within_cluster_noise": WITHIN_CLUSTER_NOISE,
        "drift_to_neighbor_alpha": DRIFT_TO_NEIGHBOR_ALPHA,
        "top_k": TOP_K_RECALL,
        "n_seeds": len(SEEDS),
        "run_mode": RUN_MODE,
        "n_arms_expected": EXPECTED_N_ARMS,
        "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "between_cluster_cosine_measured": r.get("between_cluster_cosine_measured"),
                "n_arms_observed": r.get("n_arms_observed"),
                "arms": r.get("arms"),
            }
            for r in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[metrics] written to {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
