"""alloc_routing_excitability_trace_smoke_v1 -- substrate-native forward-only learned sparse routing.

Tests whether per-position scalar excitability traces (Tonegawa-CREB analog) improve
sparse-coding allocation over random-K and k-WTA-Hebbian baselines, on clean synthetic
bipolar atoms (no substrate-graph contamination). 3-arm cell at production-ish scale
N_DIM=4096 / M=2000 / K_sparse=100 (2.5% sparsity).

DESIGN (3 arms x 3 seeds at N_DIM=4096):
  ARM_RANDOM_SPARSE       baseline: for each new atom, K=100 nonzero positions sampled
                          uniformly at random. Current substrate default; Drosophila-MB analog.
  ARM_EXCITABILITY_TRACE  mechanism: maintain per-position scalar E[i]; for each new atom,
                          sample K positions via softmax(beta * E[i]); after write, E[i] += alpha
                          for chosen positions, then E[i] *= 0.99 for all. Rich-get-richer.
                          Tonegawa-CREB engram allocation analog.
  ARM_KWTA_HEBBIAN        compare: maintain weight matrix W [N_DIM, n_features]; for each new
                          atom, compute pre-activations W @ x_input; select top-K by abs;
                          Hebbian update on selected rows. Marr-Albus cerebellar analog.

USER DIRECTIVE 2026-06-23 compliant: no MiniLM, no BGE, no proprietary embedding. All 3 arms
substrate-native + forward-only (no backprop). Pure numpy.

PRE-REG bands (per USER-explicit override of research drill bands; user dispatch prompt
2026-06-23). Discriminator = ARM_EXCITABILITY_TRACE vs ARM_RANDOM_SPARSE on clean synthetic.

  METRIC A: cleanup recall@1 at sigma in {0.5, 1.0, 1.5} per arm.
  METRIC B: capacity at sigma=1.0 -- M_capacity := largest M where recall@1 >= 0.80.
  METRIC C: clustering purity -- K-means over atom-embeddings, mechanism-family purity.
  METRIC D: position-reuse stats -- distribution of E[i] (or selection-count for non-trace arms).

  HARD_PASS (excitability-trace works; chain-grade-eligible substrate-native learned routing):
    ARM_EXCITABILITY_TRACE achieves ALL THREE:
      recall@1 at sigma=1.0 >= 0.50
      capacity at sigma=1.0 >= 1.5x ARM_RANDOM_SPARSE
      clustering purity >= ARM_RANDOM_SPARSE + 0.05

  HARD_FAIL (excitability-trace adds no value; mechanism dead):
    ARM_EXCITABILITY_TRACE recall@1 at sigma=1.0 <= ARM_RANDOM_SPARSE + 0.02
    AND capacity not lifted (within 1.05x)
    AND clustering purity not improved (within +0.01)

  MIDDLE_BAND: partial benefit (one or two metrics lift but not all three at HARD_PASS thresholds).

SANITY (CONFOUND_FAIL detector):
  sigma=0 across all 3 arms must yield recall@1 = 1.000 at M=10 (light load).

SUBSTRATE-ONLY: n_llm_calls = 0; numpy-only; no torch; local_cpu_queue.

Cites:
  - notes/research_drill_sparse_allocation_routing_learning_2026-06-23.md (source-of-truth)
  - notes/exp_dev_handoff_research_drill_sparse_allocation_routing_learning_2026-06-23.md (handoff)
  - Tonegawa 2007/2014/2016 (CREB engram allocation)
  - Marr 1969 / Albus 1971 (cerebellar k-WTA Hebbian)
  - Lin et al 2014 eLife (Drosophila APL sparse coding)
  - Moraitis 2021 SoftHebb (HARD_FAIL prior on weight-based learning, distinct layer)

Skunkworks structural blockers honored:
  #3 _LLM_CALL_COUNTER = [0] (substrate-only)
  #1 per_unit per seed
  #2 cv across seeds in compute_verdict
  #4 atexit synthesizer for timeout-resilience
"""
from __future__ import annotations

import argparse
import atexit
import os
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (  # noqa: E402
    aggregate_partials, get_output_dir, write_metrics, write_partial_key,
)

ANCHOR_NAME = "alloc_routing_excitability_trace_smoke_v1"
_LLM_CALL_COUNTER = [0]

# Pre-reg HARD bands (per USER 2026-06-23 explicit dispatch prompt)
HP_RECALL_S1 = 0.50          # ARM_EXC recall@1 @ sigma=1.0 must be >= this
HP_CAPACITY_RATIO = 1.5      # ARM_EXC capacity / ARM_RANDOM capacity must be >= this
HP_CLUSTER_LIFT = 0.05       # ARM_EXC cluster purity - ARM_RANDOM purity must be >= this
HF_RECALL_LIFT_MAX = 0.02    # ARM_EXC recall - ARM_RANDOM recall <= this triggers HF arm
HF_CAPACITY_RATIO = 1.05     # ARM_EXC / ARM_RANDOM capacity <= this triggers HF arm
HF_CLUSTER_LIFT_MAX = 0.01   # ARM_EXC - ARM_RANDOM purity <= this triggers HF arm

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke"
            if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full"))

# Config -- production-ish scale per USER prompt
N_DIM = 4096
M = 2000
K_SPARSE = 100
SIGMA_SWEEP = [0.0, 0.5, 1.0, 1.5]
DISCRIMINATOR_SIGMA = 1.0
# Mechanism families for clustering purity discriminator: assign each atom a "family"
# label via deterministic family-index = i % N_FAMILIES; family centroids are random
# bipolar prototypes; family members = centroid + within-family noise.
N_FAMILIES = 20

# Excitability-trace hyperparameters (per USER prompt)
EXC_BETA = 2.0
EXC_ALPHA = 0.1
EXC_DECAY = 0.99

# K-WTA hyperparameters
KWTA_ETA = 0.01

# Capacity sweep grid -- find largest M with recall>=0.80
CAPACITY_M_GRID_FULL = [500, 1000, 2000, 3000, 5000, 8000]
CAPACITY_M_GRID_SMOKE = [200, 500, 1000, 1500]
CAPACITY_RECALL_THRESH = 0.80
CAPACITY_SIGMA = 1.0

# Sanity-check (CONFOUND_FAIL): all arms must recall=1.0 at sigma=0 light-load
SANITY_M = 10
SANITY_N_EVAL = 10

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_EVAL_RECALL = 200
    CAPACITY_M_GRID = CAPACITY_M_GRID_FULL
    M_EFFECTIVE = M
else:
    SEEDS = [0]
    N_EVAL_RECALL = 60
    CAPACITY_M_GRID = CAPACITY_M_GRID_SMOKE
    # Smoke uses M_EFFECTIVE large enough to push past the random-baseline saturation
    # regime so the discriminator can actually fire (else by-construction-saturation makes
    # all arms look identical at small M / large N_DIM).
    M_EFFECTIVE = 1000

ARMS = ["ARM_RANDOM_SPARSE", "ARM_EXCITABILITY_TRACE", "ARM_KWTA_HEBBIAN"]

CONFIG_VERSION = (
    "alloc_routing_excitability_trace_smoke_v1; N_DIM=%d M=%d K_SPARSE=%d "
    "sigmas=%s arms=%s seeds=%s mode=%s "
    "EXC(beta=%.2f,alpha=%.2f,decay=%.2f) KWTA(eta=%.3f) "
    "N_FAMILIES=%d N_EVAL=%d capM=%s capThresh=%.2f capSigma=%.2f"
) % (
    N_DIM, M_EFFECTIVE, K_SPARSE, SIGMA_SWEEP, ARMS, SEEDS, RUN_MODE,
    EXC_BETA, EXC_ALPHA, EXC_DECAY, KWTA_ETA,
    N_FAMILIES, N_EVAL_RECALL, CAPACITY_M_GRID, CAPACITY_RECALL_THRESH, CAPACITY_SIGMA,
)


# ============================================================================
# Substrate primitives
# ============================================================================

def _make_family_centroids(n_dim: int, n_families: int, rng: np.random.Generator) -> np.ndarray:
    """N_FAMILIES random bipolar prototypes [n_families, n_dim]."""
    return (rng.integers(0, 2, size=(n_families, n_dim)) * 2 - 1).astype(np.float32)


def _make_atoms_from_families(
    n_atoms: int,
    n_dim: int,
    n_families: int,
    rng: np.random.Generator,
    family_noise_p: float = 0.20,
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate (atoms [n_atoms, n_dim], family_labels [n_atoms]).

    Each atom = centroid for its family with `family_noise_p` of bits flipped.
    Bipolar in {-1, +1}.
    """
    centroids = _make_family_centroids(n_dim, n_families, rng)
    labels = (np.arange(n_atoms) % n_families).astype(np.int64)
    base = centroids[labels].copy()  # [n_atoms, n_dim]
    flip_mask = (rng.random((n_atoms, n_dim)) < family_noise_p)
    base[flip_mask] *= -1
    return base.astype(np.float32), labels


def _sparse_project(atom_bipolar: np.ndarray, positions: np.ndarray, n_dim: int) -> np.ndarray:
    """Project a bipolar atom onto a K-sparse N_DIM vector keeping atom-signs at `positions`.

    Result has K_SPARSE nonzeros; values at positions are the atom-bipolar values at those
    positions (so the storage layer preserves a signed K-sparse signature of the atom).
    """
    out = np.zeros(n_dim, dtype=np.float32)
    out[positions] = atom_bipolar[positions]
    return out


def _l2_normalize(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        n = np.linalg.norm(X)
        return X / (n + eps)
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / (n + eps)


# ============================================================================
# Allocation ARMS
# ============================================================================

def alloc_random_sparse(
    atoms: np.ndarray, k_sparse: int, n_dim: int, seed: int
) -> Tuple[np.ndarray, np.ndarray]:
    """ARM 1 baseline: uniform random K positions per atom. No learning.

    Returns (codebook [M, n_dim] sparse, position_use_count [n_dim]).
    """
    M_local = atoms.shape[0]
    rng = np.random.default_rng(seed * 101 + 1)
    codebook = np.zeros((M_local, n_dim), dtype=np.float32)
    use_count = np.zeros(n_dim, dtype=np.int64)
    for i in range(M_local):
        positions = rng.choice(n_dim, size=k_sparse, replace=False)
        codebook[i] = _sparse_project(atoms[i], positions, n_dim)
        use_count[positions] += 1
    return codebook, use_count


def alloc_excitability_trace(
    atoms: np.ndarray, k_sparse: int, n_dim: int, seed: int,
    beta: float = EXC_BETA, alpha: float = EXC_ALPHA, decay: float = EXC_DECAY,
) -> Tuple[np.ndarray, np.ndarray]:
    """ARM 2 mechanism: per-position scalar excitability trace; softmax-weighted sample.

    For each atom:
      probs = softmax(beta * E)
      positions = sample K_SPARSE without replacement via Gumbel-top-K
      write atom into codebook at positions
      E[positions] += alpha
      E *= decay (global)

    Returns (codebook, excitability_trace [n_dim]) so caller can inspect distribution.
    """
    M_local = atoms.shape[0]
    rng = np.random.default_rng(seed * 101 + 2)
    codebook = np.zeros((M_local, n_dim), dtype=np.float32)
    E = np.ones(n_dim, dtype=np.float32)
    # Gumbel-top-K sampling: positions = argsort_top_K(beta * E + gumbel_noise)
    for i in range(M_local):
        logits = beta * E
        # subtract max for stability
        logits = logits - logits.max()
        # Gumbel: -log(-log(U))
        u = rng.random(n_dim).astype(np.float32)
        u = np.clip(u, 1e-9, 1.0 - 1e-9)
        g = -np.log(-np.log(u))
        scores = logits + g
        # top-K positions
        positions = np.argpartition(scores, -k_sparse)[-k_sparse:]
        codebook[i] = _sparse_project(atoms[i], positions, n_dim)
        # Update trace
        E[positions] += alpha
        E *= decay
        # Cap E to prevent runaway in long runs
        if E.max() > 1e6:
            E = E * (1e6 / E.max())
    return codebook, E


def alloc_kwta_hebbian(
    atoms: np.ndarray, k_sparse: int, n_dim: int, seed: int,
    eta: float = KWTA_ETA,
) -> Tuple[np.ndarray, np.ndarray]:
    """ARM 3 compare: top-K by abs(W @ x) preactivation; Hebbian update on selected rows.

    State: W [n_dim, atom_dim]; init small random.
    For each atom x:
      pre = W @ x  -> [n_dim]
      positions = top-K abs(pre)
      codebook[i] at those positions = atom values
      W[positions] += eta * x  (Hebbian)
    Substrate-native; pure feedforward competitive (cerebellar Marr-Albus analog).

    Returns (codebook, use_count [n_dim]).
    """
    M_local, d = atoms.shape
    rng = np.random.default_rng(seed * 101 + 3)
    codebook = np.zeros((M_local, n_dim), dtype=np.float32)
    use_count = np.zeros(n_dim, dtype=np.int64)
    # Init W with small random noise; identity-ish scale per feature dim
    W = rng.standard_normal((n_dim, d)).astype(np.float32) * (0.01 / np.sqrt(d))
    for i in range(M_local):
        x = atoms[i]
        pre = W @ x  # [n_dim]
        positions = np.argpartition(np.abs(pre), -k_sparse)[-k_sparse:]
        codebook[i] = _sparse_project(x, positions, n_dim)
        use_count[positions] += 1
        # Hebbian update on selected rows (signed-bipolar x; small eta)
        W[positions] += eta * x[None, :]
    return codebook, use_count


# ============================================================================
# Cleanup metric
# ============================================================================

def _argmax_cleanup_batch(cues: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """For each cue, return argmax_i <cue, codebook[i]>."""
    sims = cues @ codebook.T  # [n_cues, M]
    return np.argmax(sims, axis=1)


def cleanup_recall_at_sigmas(
    codebook: np.ndarray, atoms: np.ndarray, sigmas: list, n_eval: int, seed: int
) -> Dict[float, float]:
    """For each sigma, sample n_eval random atom indices; noise the corresponding atom;
    project to codebook positions of that atom (i.e., use atom-noise as cue); cleanup.

    Cue construction: take the sparse-codebook entry for atom i, add gaussian noise of
    std sigma in the codebook space; clean up by argmax-dot vs codebook. recall@1 =
    fraction recovered correct index.
    """
    M_local = codebook.shape[0]
    rng = np.random.default_rng(seed * 233 + 7)
    query_idx = rng.choice(M_local, size=min(n_eval, M_local), replace=False)
    cues_clean = codebook[query_idx]
    out: Dict[float, float] = {}
    for sig in sigmas:
        noise = sig * rng.standard_normal(cues_clean.shape).astype(np.float32)
        pred = _argmax_cleanup_batch(cues_clean + noise, codebook)
        out[float(sig)] = float((pred == query_idx).sum()) / max(len(query_idx), 1)
    return out


# ============================================================================
# Capacity metric (Metric B): largest M with recall>=0.80 at sigma=1.0
# ============================================================================

def measure_capacity(
    alloc_fn, atoms_full: np.ndarray, k_sparse: int, n_dim: int, seed: int,
    m_grid: list, sigma: float, recall_thresh: float, n_eval: int,
) -> Dict:
    """Run alloc_fn over progressively larger M (subset of atoms_full); return largest M
    where recall@1 at sigma >= recall_thresh.
    """
    out_results = []
    largest_passing = 0
    for M_try in m_grid:
        if M_try > atoms_full.shape[0]:
            continue
        atoms_sub = atoms_full[:M_try]
        codebook, _ = alloc_fn(atoms_sub, k_sparse, n_dim, seed)
        r = cleanup_recall_at_sigmas(codebook, atoms_sub, [sigma], min(n_eval, M_try), seed)
        recall_val = r[float(sigma)]
        out_results.append({"M": int(M_try), "recall_at_sigma": float(recall_val)})
        if recall_val >= recall_thresh:
            largest_passing = M_try
    return {
        "m_grid": list(m_grid),
        "results": out_results,
        "largest_M_passing": int(largest_passing),
        "recall_thresh": float(recall_thresh),
        "sigma": float(sigma),
    }


# ============================================================================
# Clustering purity (Metric C): K-means over codebook with mechanism-family labels
# ============================================================================

def _kmeans_simple(
    X: np.ndarray, k: int, seed: int, max_iter: int = 25,
) -> np.ndarray:
    """Lloyd's k-means returning cluster assignments [n]. Simple; no sklearn dep."""
    n, d = X.shape
    rng = np.random.default_rng(seed * 419 + 11)
    # k-means++-lite init: random points
    init_idx = rng.choice(n, size=min(k, n), replace=False)
    centers = X[init_idx].copy()
    assign = np.zeros(n, dtype=np.int64)
    for _ in range(max_iter):
        # distances [n, k]
        d2 = ((X[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        new_assign = np.argmin(d2, axis=1)
        if np.array_equal(new_assign, assign):
            break
        assign = new_assign
        # Recompute centers; if cluster empty, leave center as-is
        for c in range(k):
            mask = (assign == c)
            if mask.any():
                centers[c] = X[mask].mean(axis=0)
    return assign


def clustering_purity(
    codebook: np.ndarray, true_labels: np.ndarray, n_clusters: int, seed: int,
) -> float:
    """K-means with n_clusters then majority-vote purity over true_labels."""
    M_local = codebook.shape[0]
    if M_local < n_clusters:
        return 0.0
    # Normalize codebook rows so kmeans operates on direction
    X = _l2_normalize(codebook)
    assign = _kmeans_simple(X, n_clusters, seed)
    total_correct = 0
    for c in range(n_clusters):
        mask = (assign == c)
        if not mask.any():
            continue
        labels_in_cluster = true_labels[mask]
        # majority count
        vals, counts = np.unique(labels_in_cluster, return_counts=True)
        total_correct += int(counts.max())
    return float(total_correct) / max(M_local, 1)


# ============================================================================
# Position-reuse stats (Metric D): distribution of E[i] or use_count[i]
# ============================================================================

def position_reuse_stats(arr: np.ndarray) -> Dict:
    """Distribution summary of position trace / use_count."""
    a = np.asarray(arr, dtype=np.float64)
    n_total = a.size
    nonzero_mask = (a > 0)
    n_nonzero = int(nonzero_mask.sum())
    summary = {
        "n_total": int(n_total),
        "n_nonzero": n_nonzero,
        "fraction_used": float(n_nonzero) / max(n_total, 1),
        "mean": float(a.mean()),
        "std": float(a.std()),
        "min": float(a.min()),
        "max": float(a.max()),
        "p10": float(np.percentile(a, 10)),
        "p50": float(np.percentile(a, 50)),
        "p90": float(np.percentile(a, 90)),
        "p99": float(np.percentile(a, 99)),
        # coefficient of variation = std/mean; >1 means heavy-tailed structured use
        "cv": float(a.std() / max(abs(a.mean()), 1e-9)),
    }
    return summary


# ============================================================================
# Per-seed unit
# ============================================================================

def run_unit(seed: int) -> Dict:
    t0 = time.time()
    print("\n[seed=%d] building synthetic family-prototype atoms M=%d N_DIM=%d N_FAMILIES=%d"
          % (seed, M_EFFECTIVE, N_DIM, N_FAMILIES), flush=True)
    rng_data = np.random.default_rng(seed * 7919 + 13)
    # Build atoms once per seed; same atoms across all arms
    atoms_main, labels_main = _make_atoms_from_families(M_EFFECTIVE, N_DIM, N_FAMILIES, rng_data)
    # For capacity sweep, build the largest needed atom set ONCE; arms subset it
    max_cap_M = max(CAPACITY_M_GRID) if CAPACITY_M_GRID else M_EFFECTIVE
    if max_cap_M > M_EFFECTIVE:
        atoms_for_cap, _ = _make_atoms_from_families(max_cap_M, N_DIM, N_FAMILIES, rng_data)
    else:
        atoms_for_cap = atoms_main
    # Sanity atoms (very small)
    atoms_sanity, _ = _make_atoms_from_families(SANITY_M, N_DIM, N_FAMILIES, rng_data)

    by_arm: Dict[str, Dict] = {}
    arm_fns = {
        "ARM_RANDOM_SPARSE": alloc_random_sparse,
        "ARM_EXCITABILITY_TRACE": alloc_excitability_trace,
        "ARM_KWTA_HEBBIAN": alloc_kwta_hebbian,
    }
    for arm_label in ARMS:
        t_arm = time.time()
        print("  [seed=%d arm=%s] allocating M=%d" % (seed, arm_label, M_EFFECTIVE), flush=True)
        fn = arm_fns[arm_label]
        codebook, position_state = fn(atoms_main, K_SPARSE, N_DIM, seed)
        t_alloc = time.time() - t_arm

        # Metric A: cleanup recall@1 at sigmas
        t_a = time.time()
        cleanup = cleanup_recall_at_sigmas(
            codebook, atoms_main, SIGMA_SWEEP, N_EVAL_RECALL, seed)
        t_clean = time.time() - t_a

        # Metric B: capacity sweep at sigma=1.0
        t_b = time.time()
        cap = measure_capacity(
            fn, atoms_for_cap, K_SPARSE, N_DIM, seed,
            CAPACITY_M_GRID, CAPACITY_SIGMA, CAPACITY_RECALL_THRESH, N_EVAL_RECALL)
        t_cap = time.time() - t_b

        # Metric C: clustering purity over codebook (with mechanism-family ground truth)
        t_c = time.time()
        purity = clustering_purity(codebook, labels_main, N_FAMILIES, seed)
        t_pur = time.time() - t_c

        # Metric D: position-reuse stats
        reuse = position_reuse_stats(position_state)

        # Sanity sigma=0 at M=10
        cb_sanity, _ = fn(atoms_sanity, K_SPARSE, N_DIM, seed)
        sanity = cleanup_recall_at_sigmas(cb_sanity, atoms_sanity, [0.0], SANITY_N_EVAL, seed)

        by_arm[arm_label] = {
            "cleanup_recall": {str(k): round(v, 4) for k, v in cleanup.items()},
            "recall_discriminator": round(cleanup.get(DISCRIMINATOR_SIGMA, 0.0), 4),
            "capacity": cap,
            "capacity_largest_M_passing": int(cap["largest_M_passing"]),
            "clustering_purity": round(purity, 4),
            "position_reuse": reuse,
            "sanity_M10_sigma0_recall": round(sanity[0.0], 4),
            "wall_alloc_s": round(t_alloc, 2),
            "wall_cleanup_s": round(t_clean, 2),
            "wall_capacity_s": round(t_cap, 2),
            "wall_purity_s": round(t_pur, 2),
        }
        a = by_arm[arm_label]
        print(("    [seed=%d arm=%s] disc=%.3f basin_0=%.3f basin_1.5=%.3f cap_largest=%d "
               "purity=%.3f reuse_frac=%.3f cv=%.2f sanity10=%.3f "
               "(alloc=%.1fs clean=%.1fs cap=%.1fs pur=%.1fs)") % (
                  seed, arm_label, a["recall_discriminator"],
                  cleanup.get(0.0, 0.0), cleanup.get(1.5, 0.0),
                  a["capacity_largest_M_passing"], a["clustering_purity"],
                  a["position_reuse"]["fraction_used"], a["position_reuse"]["cv"],
                  a["sanity_M10_sigma0_recall"],
                  t_alloc, t_clean, t_cap, t_pur), flush=True)

    return {
        "seed": seed,
        "by_arm": by_arm,
        "N": N_DIM,
        "N_DIM": N_DIM,
        "M": M_EFFECTIVE,
        "K_SPARSE": K_SPARSE,
        "N_EVAL_RECALL": N_EVAL_RECALL,
        "N_FAMILIES": N_FAMILIES,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units: list) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})
    arm_labels = list(units[0]["by_arm"].keys())

    by_arm_agg: Dict[str, Dict] = {}
    for arm_label in arm_labels:
        disc_vals = [u["by_arm"][arm_label]["recall_discriminator"] for u in units]
        cap_vals = [u["by_arm"][arm_label]["capacity_largest_M_passing"] for u in units]
        pur_vals = [u["by_arm"][arm_label]["clustering_purity"] for u in units]
        basin_keys = list(units[0]["by_arm"][arm_label]["cleanup_recall"].keys())
        basin_agg = {}
        for sk in basin_keys:
            vals = [u["by_arm"][arm_label]["cleanup_recall"].get(sk, 0.0) for u in units]
            basin_agg[sk] = round(float(np.mean(vals)), 4)
        d_mean = float(np.mean(disc_vals))
        d_std = float(np.std(disc_vals))
        d_cv = d_std / max(abs(d_mean), 1e-6)
        c_mean = float(np.mean(cap_vals))
        c_std = float(np.std(cap_vals))
        p_mean = float(np.mean(pur_vals))
        p_std = float(np.std(pur_vals))
        # Sanity check
        sanity_vals = [u["by_arm"][arm_label]["sanity_M10_sigma0_recall"] for u in units]
        sanity_min = float(np.min(sanity_vals))
        by_arm_agg[arm_label] = {
            "recall_discriminator_mean": round(d_mean, 4),
            "recall_discriminator_std": round(d_std, 4),
            "recall_discriminator_cv": round(d_cv, 4),
            "capacity_largest_M_passing_mean": round(c_mean, 2),
            "capacity_largest_M_passing_std": round(c_std, 2),
            "clustering_purity_mean": round(p_mean, 4),
            "clustering_purity_std": round(p_std, 4),
            "basin_robustness_mean": basin_agg,
            "sanity_M10_sigma0_min": round(sanity_min, 4),
        }

    # Sanity sigma=0 at M=10 check
    sanity_failures = []
    for arm_label in arm_labels:
        sn = by_arm_agg[arm_label]["sanity_M10_sigma0_min"]
        if sn < 0.999:
            sanity_failures.append("%s sanity_M10=%.4f" % (arm_label, sn))
    sanity_ok = (len(sanity_failures) == 0)

    # Pull baseline + mechanism arm aggs
    base = by_arm_agg["ARM_RANDOM_SPARSE"]
    exc = by_arm_agg["ARM_EXCITABILITY_TRACE"]
    kwta = by_arm_agg["ARM_KWTA_HEBBIAN"]

    # Compute discriminator scores
    recall_lift = exc["recall_discriminator_mean"] - base["recall_discriminator_mean"]
    base_cap = max(base["capacity_largest_M_passing_mean"], 1.0)
    cap_ratio = exc["capacity_largest_M_passing_mean"] / base_cap
    purity_lift = exc["clustering_purity_mean"] - base["clustering_purity_mean"]

    # HARD_PASS criteria (ALL THREE)
    hp_recall_ok = exc["recall_discriminator_mean"] >= HP_RECALL_S1
    hp_cap_ok = cap_ratio >= HP_CAPACITY_RATIO
    hp_pur_ok = purity_lift >= HP_CLUSTER_LIFT
    hard_pass = hp_recall_ok and hp_cap_ok and hp_pur_ok

    # HARD_FAIL criteria (ALL THREE failed)
    hf_recall_dead = recall_lift <= HF_RECALL_LIFT_MAX
    hf_cap_dead = cap_ratio <= HF_CAPACITY_RATIO
    hf_pur_dead = purity_lift <= HF_CLUSTER_LIFT_MAX
    hard_fail = hf_recall_dead and hf_cap_dead and hf_pur_dead

    detail = {
        "by_arm_agg": by_arm_agg,
        "discriminator_sigma": DISCRIMINATOR_SIGMA,
        "recall_lift_exc_vs_random": round(recall_lift, 4),
        "capacity_ratio_exc_vs_random": round(cap_ratio, 4),
        "purity_lift_exc_vs_random": round(purity_lift, 4),
        "hp_recall_ok": hp_recall_ok,
        "hp_cap_ok": hp_cap_ok,
        "hp_pur_ok": hp_pur_ok,
        "hf_recall_dead": hf_recall_dead,
        "hf_cap_dead": hf_cap_dead,
        "hf_pur_dead": hf_pur_dead,
        "sanity_sigma0_M10_ok": sanity_ok,
        "sanity_sigma0_M10_failures": sanity_failures,
        "n_seeds": len(units),
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "HD-substrate-native forward-only learned-sparse-allocation drill; 3 arms "
            "(RANDOM_SPARSE / EXCITABILITY_TRACE / KWTA_HEBBIAN) at N_DIM=%d M=%d K=%d; "
            "discriminator = ARM_EXCITABILITY_TRACE vs ARM_RANDOM_SPARSE on clean synthetic "
            "family-prototype atoms; HARD_PASS requires recall@sigma=%.1f >= %.2f AND "
            "capacity-ratio >= %.2fx AND purity-lift >= %.2f."
        ) % (
            N_DIM, M_EFFECTIVE, K_SPARSE,
            DISCRIMINATOR_SIGMA, HP_RECALL_S1, HP_CAPACITY_RATIO, HP_CLUSTER_LIFT,
        ),
        "cites": [
            "notes/research_drill_sparse_allocation_routing_learning_2026-06-23.md",
            "notes/exp_dev_handoff_research_drill_sparse_allocation_routing_learning_2026-06-23.md",
            "Tonegawa_CREB_engram_allocation_2007_2014_2016",
            "Marr_1969_Albus_1971_cerebellar_k_WTA",
            "Lin_eLife_2014_Drosophila_APL_sparse",
        ],
    }

    summary = (
        "ALLOC_ROUTING @ sigma=%.1f: RANDOM=disc%.3f/cap%d/pur%.3f | "
        "EXC=disc%.3f/cap%d/pur%.3f | KWTA=disc%.3f/cap%d/pur%.3f | "
        "lift_recall=%.3f cap_ratio=%.2fx lift_pur=%.3f | sanity_ok=%s"
    ) % (
        DISCRIMINATOR_SIGMA,
        base["recall_discriminator_mean"], int(base["capacity_largest_M_passing_mean"]),
        base["clustering_purity_mean"],
        exc["recall_discriminator_mean"], int(exc["capacity_largest_M_passing_mean"]),
        exc["clustering_purity_mean"],
        kwta["recall_discriminator_mean"], int(kwta["capacity_largest_M_passing_mean"]),
        kwta["clustering_purity_mean"],
        recall_lift, cap_ratio, purity_lift, sanity_ok,
    )

    # CONFOUND check first
    if not sanity_ok:
        return ("CONFOUND_FAIL",
                ("CONFOUND_FAIL: sigma=0 M=10 sanity recall < 1.000 for %d arm(s) (%s); "
                 "implementation bug suspected, NOT mechanism rejection. " % (
                     len(sanity_failures), "; ".join(sanity_failures))) + summary,
                detail)

    if hard_pass:
        return ("HARD_PASS",
                ("ALLOC_ROUTING HARD_PASS: ARM_EXCITABILITY_TRACE clears ALL THREE -- "
                 "recall@sigma=%.1f=%.3f>=%.2f AND capacity-ratio=%.2fx>=%.2fx AND "
                 "purity-lift=%.3f>=%.2f over ARM_RANDOM_SPARSE; substrate-native forward-only "
                 "learned-sparse-routing primitive demonstrated; chain-grade-eligible. " % (
                     DISCRIMINATOR_SIGMA, exc["recall_discriminator_mean"], HP_RECALL_S1,
                     cap_ratio, HP_CAPACITY_RATIO, purity_lift, HP_CLUSTER_LIFT)) + summary,
                detail)

    if hard_fail:
        return ("HARD_FAIL",
                ("ALLOC_ROUTING HARD_FAIL: ARM_EXCITABILITY_TRACE adds no value over RANDOM_SPARSE -- "
                 "recall-lift=%.3f<=%.2f AND capacity-ratio=%.2fx<=%.2fx AND purity-lift=%.3f<=%.2f; "
                 "substrate-native forward-only learned-routing mechanism dead at production scope; "
                 "pivot to backprop minimum infrastructure (Anchor 2) per research drill. " % (
                     recall_lift, HF_RECALL_LIFT_MAX, cap_ratio, HF_CAPACITY_RATIO,
                     purity_lift, HF_CLUSTER_LIFT_MAX)) + summary,
                detail)

    return ("MIDDLE_BAND",
            ("ALLOC_ROUTING MIDDLE_BAND: partial benefit from EXCITABILITY_TRACE -- "
             "recall-lift=%.3f cap-ratio=%.2fx purity-lift=%.3f; not all three HP thresholds "
             "met but not all three HF thresholds tripped either; characterize via ablation "
             "(alpha/beta/decay sweep). " % (recall_lift, cap_ratio, purity_lift)) + summary,
            detail)


# ============================================================================
# atexit synthesizer
# ============================================================================
_METRICS_WRITTEN = [False]
_OUT_DIR_REF: list = [None]
_T0_REF: list = [None]


def _synthesize_on_exit() -> None:
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                    "atexit synthesize: compute_verdict failed: %s" % e,
                                    {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units)
                       if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "M": M_EFFECTIVE,
            "K_SPARSE": K_SPARSE,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_alloc_routing_excitability_trace_smoke_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (
                len(units), len(SEEDS), msg),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ============================================================================
# Self-test (mechanism + sanity + verdict-shape)
# ============================================================================

def _selftest() -> None:
    # T1: family-atom builder produces bipolar atoms with correct shape + family labels
    rng = np.random.default_rng(0)
    atoms_t, labels_t = _make_atoms_from_families(40, 64, n_families=4, rng=rng)
    assert atoms_t.shape == (40, 64), "T1 atoms shape: %s" % (atoms_t.shape,)
    uniq = set(np.unique(atoms_t).tolist())
    assert uniq.issubset({-1.0, 1.0}), "T1 atoms not bipolar: %s" % uniq
    assert labels_t.shape == (40,) and labels_t.max() == 3, "T1 labels: %s" % labels_t

    # T2: alloc_random_sparse produces (M, n_dim) sparse codebook with K nonzeros per row
    cb_r, uc_r = alloc_random_sparse(atoms_t, k_sparse=8, n_dim=64, seed=0)
    assert cb_r.shape == (40, 64), "T2 cb shape: %s" % (cb_r.shape,)
    nz_per_row = (cb_r != 0).sum(axis=1)
    assert (nz_per_row == 8).all(), "T2 K_sparse violated: nz_per_row=%s" % nz_per_row[:5]
    assert uc_r.shape == (64,), "T2 uc shape: %s" % (uc_r.shape,)
    assert uc_r.sum() == 40 * 8, "T2 use_count sum off: %d vs %d" % (uc_r.sum(), 40 * 8)

    # T3: alloc_excitability_trace produces correct shape; trace evolves (cv > 0)
    cb_e, E_e = alloc_excitability_trace(atoms_t, k_sparse=8, n_dim=64, seed=0)
    assert cb_e.shape == (40, 64), "T3 cb_e shape: %s" % (cb_e.shape,)
    nz_per_row_e = (cb_e != 0).sum(axis=1)
    assert (nz_per_row_e == 8).all(), "T3 K_sparse violated: nz=%s" % nz_per_row_e[:5]
    assert E_e.shape == (64,), "T3 E_e shape: %s" % (E_e.shape,)
    # After many writes with rich-get-richer, trace should be non-uniform
    cv_e = float(E_e.std() / max(E_e.mean(), 1e-9))
    assert cv_e > 0.0, "T3 trace cv must be > 0: %.4f" % cv_e

    # T3b: identical seed -> deterministic trace evolution
    cb_e2, E_e2 = alloc_excitability_trace(atoms_t, k_sparse=8, n_dim=64, seed=0)
    assert np.allclose(E_e, E_e2), "T3b excitability not deterministic across runs"
    assert np.allclose(cb_e, cb_e2), "T3b codebook not deterministic across runs"

    # T4: alloc_kwta_hebbian produces correct shape + K_sparse nonzeros
    cb_k, uc_k = alloc_kwta_hebbian(atoms_t, k_sparse=8, n_dim=64, seed=0)
    assert cb_k.shape == (40, 64), "T4 cb_k shape: %s" % (cb_k.shape,)
    nz_per_row_k = (cb_k != 0).sum(axis=1)
    assert (nz_per_row_k == 8).all(), "T4 K_sparse violated: nz=%s" % nz_per_row_k[:5]

    # T5: cleanup_recall_at_sigmas: sigma=0 should give recall=1.0 (perfect on clean)
    out = cleanup_recall_at_sigmas(cb_r, atoms_t, [0.0], 10, seed=0)
    assert 0.0 in out and out[0.0] == 1.0, "T5 sigma=0 cleanup not 1.0: %s" % out

    # T6: clustering_purity returns float in [0, 1]; perfect-replica codebook has high purity
    # Build a synthetic perfect-cluster codebook for purity=1.0 test
    cb_perfect = np.zeros((16, 8), dtype=np.float32)
    labels_perfect = np.array([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3])
    for c in range(4):
        cb_perfect[labels_perfect == c] = np.eye(4)[c][None, :].repeat(2, axis=1)
    pur = clustering_purity(cb_perfect, labels_perfect, n_clusters=4, seed=0)
    assert pur >= 0.99, "T6 perfect-cluster purity should be ~1.0; got %.4f" % pur

    # T7: position_reuse_stats returns dict with required keys
    stats = position_reuse_stats(uc_r)
    for key in ("mean", "std", "p50", "cv", "fraction_used"):
        assert key in stats, "T7 missing key %s" % key

    # T8: measure_capacity returns dict with results
    rng2 = np.random.default_rng(1)
    atoms_big, _ = _make_atoms_from_families(50, 64, n_families=4, rng=rng2)
    cap = measure_capacity(alloc_random_sparse, atoms_big, 8, 64, seed=0,
                            m_grid=[10, 25, 50], sigma=0.0, recall_thresh=0.80, n_eval=10)
    assert cap["largest_M_passing"] >= 10, "T8 capacity: sigma=0 must pass at M=10: %s" % cap

    # T9: compute_verdict CONFOUND_FAIL when sanity recall < 1.0
    def _mk_unit(recall_per_arm, cap_per_arm, pur_per_arm, sanity=1.0):
        by_arm_local = {}
        for al, rd, cap_m, pp in zip(ARMS, recall_per_arm, cap_per_arm, pur_per_arm):
            by_arm_local[al] = {
                "cleanup_recall": {"0.0": 1.0, "0.5": rd + 0.05, "1.0": rd, "1.5": rd - 0.05},
                "recall_discriminator": rd,
                "capacity": {"largest_M_passing": cap_m},
                "capacity_largest_M_passing": cap_m,
                "clustering_purity": pp,
                "position_reuse": {"mean": 1.0, "std": 0.0, "cv": 0.0, "fraction_used": 1.0,
                                   "p50": 1.0, "n_total": 64, "n_nonzero": 64,
                                   "min": 1.0, "max": 1.0, "p10": 1.0, "p90": 1.0, "p99": 1.0},
                "sanity_M10_sigma0_recall": sanity,
                "wall_alloc_s": 0.0, "wall_cleanup_s": 0.0,
                "wall_capacity_s": 0.0, "wall_purity_s": 0.0,
            }
        return {
            "seed": 0, "by_arm": by_arm_local, "N": 64, "N_DIM": 64, "M": 40,
            "K_SPARSE": 8, "N_EVAL_RECALL": 10, "N_FAMILIES": 4,
            "run_mode": "smoke", "config_version": "selftest", "elapsed_s_seed": 0.01,
        }
    u_bad = _mk_unit([0.30, 0.60, 0.40], [400, 1500, 500], [0.30, 0.55, 0.35], sanity=0.80)
    v_b, m_b, _ = compute_verdict([u_bad])
    assert v_b == "CONFOUND_FAIL", "T9 expected CONFOUND_FAIL got %s" % v_b

    # T10: HARD_PASS when exc lifts all three
    u_hp = _mk_unit([0.30, 0.60, 0.40], [400, 1500, 500], [0.30, 0.55, 0.35])
    v_hp, m_hp, d_hp = compute_verdict([u_hp])
    assert v_hp == "HARD_PASS", "T10 expected HARD_PASS got %s msg=%s" % (v_hp, m_hp[:200])
    assert d_hp["hp_recall_ok"] and d_hp["hp_cap_ok"] and d_hp["hp_pur_ok"], (
        "T10 detail flags not set: %s" % d_hp)

    # T11: HARD_FAIL when exc dead on all three
    u_hf = _mk_unit([0.30, 0.31, 0.32], [400, 410, 420], [0.30, 0.305, 0.31])
    v_hf, m_hf, _ = compute_verdict([u_hf])
    assert v_hf == "HARD_FAIL", "T11 expected HARD_FAIL got %s msg=%s" % (v_hf, m_hf[:200])

    # T12: MIDDLE when partial (e.g. recall lifts but capacity does not)
    u_mb = _mk_unit([0.30, 0.55, 0.32], [400, 410, 420], [0.30, 0.305, 0.31])
    v_mb, m_mb, _ = compute_verdict([u_mb])
    assert v_mb == "MIDDLE_BAND", "T12 expected MIDDLE_BAND got %s msg=%s" % (v_mb, m_mb[:200])

    print("[selftest] PASS: T1 atoms_bipolar + T2 random_alloc + T3 exc_trace + "
          "T3b determinism + T4 kwta_alloc + T5 sigma0_cleanup + T6 purity + "
          "T7 reuse_stats + T8 capacity + T9 CONFOUND_FAIL + T10 HARD_PASS + "
          "T11 HARD_FAIL + T12 MIDDLE_BAND OK", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print(("[config] %s mode=%s N_DIM=%d M=%d K_SPARSE=%d N_EVAL=%d "
           "seeds=%s arms=%s | name_says_smoke=%s | %s") % (
              ANCHOR_NAME, RUN_MODE, N_DIM, M_EFFECTIVE, K_SPARSE, N_EVAL_RECALL,
              SEEDS, ARMS, _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM, "M": M_EFFECTIVE,
               "schema": "alloc-routing-excitability-trace-smoke-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(
        out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "M": M_EFFECTIVE,
        "K_SPARSE": K_SPARSE,
        "N_EVAL_RECALL": N_EVAL_RECALL,
        "N_FAMILIES": N_FAMILIES,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_alloc_routing_excitability_trace_smoke_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (HD substrate-native; forward-only; no LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "_name_says_smoke_workaround": _NAME_SAYS_SMOKE,
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
