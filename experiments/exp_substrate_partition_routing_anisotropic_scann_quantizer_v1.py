"""ANISOTROPIC ScaNN-style VQ quantizer for substrate partition routing -- Gap 2 Anchor R1.

PARENT CONTEXT (REFRAME handoff per Research 2026-06-26):
  - notes/research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md (section 4, Candidate R2)
  - notes/exp_dev_handoff_research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md (Anchor 1)
  - REFRAME cumulative evidence: 5 independent isotropization HARD_FAILs (whitening, MIMO,
    DG, polarimetric) + AB_CONTROL_4096x ties fly-LSH at brain-scale expansion.
  - "Substrate's anisotropy is a FEATURE, not a bug" -- the partition routing chain-grade
    spine EXPLOITS the cone structure; this cell strengthens the spine with the production-
    validated Google ScaNN recipe (Guo et al 2020, arXiv:1908.10396).

MECHANISM (one paragraph):
  Substrate's existing partition routing (chain-grade @ M=10M via hierarchical 2-level)
  uses k-means quantization with isotropic L2 loss to assign keys to partitions. Inside
  each partition, dense Tikhonov-regularized cleanup handles retrieval. The bottleneck
  for routing quality is the QUANTIZATION step: L2 k-means doesn't know which axes
  matter for cosine retrieval. Guo et al 2020's anisotropic VQ replaces the symmetric
  L2 loss with an ANISOTROPIC loss that penalizes quantization error along the query
  direction more heavily than orthogonal. Concretely: for codebook center c_i and key
  k assigned to partition i, the per-key loss is h_parallel * ||k_parallel - c_i,parallel||^2
  + h_perp * ||k_perp - c_i,perp||^2 where parallel/perp are decomposed along query direction;
  with h_parallel >> h_perp (e.g. T-power weighting, T>1) the quantizer learns to align
  cluster centroids with high-cosine retrieval directions. This is the production billion-
  scale recipe that gives ScaNN 2x advantage over FAISS-IVF on ANN-Benchmarks.

  Substrate-novel claim: applying anisotropic VQ at the partition routing step on real
  Pythia adversarial-similarity keys lifts route_acc + recall@1 at M=100k compared to
  current isotropic k-means baseline. If HARD_PASS, locks in anisotropic ScaNN as a
  drop-in spine improvement for the substrate's chain-grade partition routing.

CRITICAL PATTERN-CHECK (Skunkworks lesson, MIMO + DG SMOKE_HARD_FAILs 2026-06-26):
  Both MIMO (effrank +186x but recall -0.027) and DG (rank +5.79x but recall -0.147)
  showed HUGE geometric lifts with NO recall benefit. If ARM_SCANN_ANISOTROPIC_VQ shows
  quantization-error reduction (geometric metric) but no recall lift (or worse, sign-flip),
  that's the SAME structural mismatch -- substrate's Tikhonov cleanup may already exploit
  the cone, and "anisotropy-aware quantization" may just rearrange the same regularizer.
  Smoke MUST report BOTH route_acc + recall@1; if smoke shows geometric improvement +
  recall regression OR zero recall change, GATE and report rather than dispatch full.

ARMS (per handoff Anchor 1):
  CROSS-CELL SANITY RAIL (Fix #28 by-construction-saturation sentinel):
    ARM_KNN_BASELINE at M=400 -- must >= 0.9 on every config. Keys-themselves corruption
    catch; if KNN drops below 0.9 the encoded keys are degraded and any routing-arm "lift"
    is artifact.

  MECHANISM ARMS:
    ARM_ISOTROPIC_KMEANS  -- current substrate partition routing baseline; standard L2
                              k-means quantizer; reproduces chain-grade routing recall.
    ARM_SCANN_ANISOTROPIC_VQ  -- main test; Guo et al 2020 ScaNN anisotropic VQ loss
                                  applied at partition assignment.
    ARM_LEARNED_ANISO_LOSS    -- gradient-trained per-cluster anisotropic loss matrix;
                                  upper bound on what anisotropy-aware quantization can do.

  DIAGNOSTICS (per handoff):
    - route_acc per arm: fraction of queries routed to the partition that contains the
      true key (mechanistic check; the quantization-error analog).
    - recall@1 per arm: fraction of queries where the rerank within the routed partition
      retrieves the true key. This is the LOAD-BEARING outcome metric.
    - per-cluster cone-alignment metric: average cosine between cluster centroid and
      mean direction of keys in that cluster. Higher = quantizer tracks the local cone.

  M-SCALING SWEEP:
    M = [400, 10000, 100000]. M=400 = KNN sentinel. M=10k = where current partition routing
    starts to need help. M=100k = adversarial brain-scale (handoff Anchor 1 budget).

PRE-REGISTERED BANDS (LOCKED AT MODULE INIT):

  HARD_PASS_CHAIN_GRADE_AT_M_100K:
    ARM_SCANN_ANISOTROPIC_VQ recall@1 at M=100k >= 0.70
    AND lift over ARM_ISOTROPIC_KMEANS >= 0.10 absolute
    AND ARM_SCANN route_acc at M=100k >= 0.95
    AND cv across seeds for ARM_SCANN recall <= 0.05
    AND ARM_KNN_BASELINE at M=400 >= 0.90

  HARD_PASS_PARTIAL:
    Lift over ARM_ISOTROPIC_KMEANS >= 0.05 at M=100k
    AND KNN sentinel preserved
    AND no recall regression (lift > 0)
    (some HARD_PASS conditions not met)

  MIDDLE_BAND:
    Lift in (0.02, 0.05] at M=100k AND no recall regression

  HARD_FAIL_ANISOTROPIC_VQ_DOESNT_HELP:
    Lift <= 0.02 at M=100k -- isotropic kmeans already optimal for substrate cone
    OR KNN sentinel drops below 0.90 (corruption catch).

  HARD_FAIL_GEOMETRIC_NO_RECALL (MIMO/DG pattern):
    quant_error_reduction >= 0.20 (geometric improvement)
    AND recall lift <= 0.00 (no recall benefit; sign-flip allowed)
    -- substrate's Tikhonov cleanup already exploits the cone; "anisotropy-aware
    quantization" just rearranges the same regularizer.

Q-DISCIPLINE: any arm >= 0.995 flags suspect saturation; bands favor under-claim.

Disciplines (load-bearing):
  - ASCII only.
  - Substrate-only at inference; encoder is SETUP-TIME hidden-state extractor.
  - Per-arm metrics (Fix #28); read metrics.json per-arm, NOT verdict_msg.
  - atexit per-seed checkpoint + restartable (per Fix #20).
  - META_M7 capacity-sensitive dims (PROJ_DIM, N_PARTITIONS_PER_M, PART_SIZE_TARGET,
    SCANN_T, LEARNED_LR, LEARNED_STEPS, KNN_TOPK) IDENTICAL across smoke and full --
    ONLY M, n_seeds, and encoder differ.
  - Smoke MUST emit BOTH route_acc + recall@1 + quant_error metrics; if smoke shows
    MIMO/DG pattern (geometric lift, no recall lift), GATE and report.

Routing: local CPU (Tier A per handoff). M=100k matmul-bound; numpy CPU adequate;
~3-5 hr full wall on laptop.

Cites:
  - Guo, R. et al (2020). "Accelerating Large-Scale Inference with Anisotropic
    Vector Quantization." ICML 2020. arXiv:1908.10396 (ScaNN production recipe).
  - notes/research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md (R2 candidate).
  - notes/exp_dev_handoff_research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md.
  - data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json (chain-grade
    spine being extended).
  - data/exp_substrate_partition_routing_10M_full_v2/metrics.json (chain-grade @ M=1M).
"""
from __future__ import annotations
import sys, os, argparse, time, math, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_partition_routing_anisotropic_scann_quantizer_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# CAPACITY-SENSITIVE (META_M7) -- IDENTICAL smoke/full
PROJ_DIM = 768                  # post-contrastive projection dim (matches handoff anchor 1)
PART_SIZE_TARGET = 2000         # matches substrate's chain-grade partition routing target
KM_ITERS = 25                   # k-means EM iterations
SCANN_ITERS = 25                # anisotropic-VQ EM iterations (matches Guo et al budget)
SCANN_T = 2.0                   # ScaNN T-power weighting (h_parallel = T^2; h_perp = 1)
LEARNED_LR = 0.05               # learned-loss-matrix SGD lr
LEARNED_STEPS = 150             # learned-loss-matrix SGD steps
KNN_TOPK = 1                    # KNN baseline = top-1 cosine
SIGMA = 0.1                     # cue noise sigma (matches adversarial-keys regime)
MAX_Q = 1500                    # max cue count per M
WINDOW_TOKENS = 16              # adversarial-similarity stride-1 windows (matches anisotropy cells)
CUE_SHIFT = 1
RERANK_PARTITIONS = 1           # within-partition exact cosine rerank (single routed partition)

# MODE-DEPENDENT (ONLY THESE DIFFER smoke vs full)
if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"
    SEEDS = [11, 13, 19]
    M_SWEEP = [400, 10000, 100000]
    TRAIN_M = 10000
    TRAIN_STEPS = 600
else:
    ENCODER = "EleutherAI/pythia-160m"
    SEEDS = [11]
    M_SWEEP = [400, 2000]       # smoke: must trigger meaningful partition routing at M=2k
    TRAIN_M = 800
    TRAIN_STEPS = 100

# PRE-REG BANDS (LOCKED AT MODULE INIT)
BAND_HP_CHAIN_GRADE = 0.70      # SCANN recall@1 floor at M=100k
BAND_HP_LIFT = 0.10             # lift over ISOTROPIC_KMEANS for HARD_PASS
BAND_HP_ROUTE_ACC = 0.95        # route_acc floor for HARD_PASS
BAND_HP_PARTIAL_LIFT = 0.05     # lift for HARD_PASS_PARTIAL
BAND_MIDDLE_LIFT = 0.02         # strictly above -> MIDDLE_BAND
BAND_HF_LIFT = 0.015            # at-or-below -> HARD_FAIL_DOESNT_HELP (must be < MIDDLE_LIFT)
BAND_HF_GEOMETRIC_LIFT = 0.20   # quant_error reduction threshold for MIMO/DG-pattern catch
BAND_KNN_SENTINEL = 0.90        # KNN at M=400 floor (Fix #28)
BAND_CV_HP = 0.05               # seed cv ceiling for HARD_PASS
BAND_Q_SATURATION = 0.995       # suspect saturation
BAND_CONE_ALIGN_MIN = 0.30      # cone-alignment metric sanity floor (post-fit)

assert 0.0 < BAND_HF_LIFT < BAND_MIDDLE_LIFT < BAND_HP_PARTIAL_LIFT < BAND_HP_LIFT < 1.0, "lift band ordering"
assert 0.0 < BAND_KNN_SENTINEL < 1.0, "knn sentinel"
assert 0.0 < BAND_HP_CHAIN_GRADE < BAND_HP_ROUTE_ACC < 1.0, "recall floor < route floor"
assert 1.0 > SCANN_T > 0.0 or SCANN_T > 1.0, "T-power weighting positive"

CONFIG_VERSION = (
    "scann_aniso_vq_v1 (knn / iso_kmeans / scann_aniso / learned_aniso) | "
    "proj=%d part_target=%d km_iters=%d scann_iters=%d scann_T=%.2f "
    "lr=%.3f steps=%d sigma=%.2f window=%dt shift=%d | "
    "seeds=%s M=%s encoder=%s | CPU_numpy"
) % (
    PROJ_DIM, PART_SIZE_TARGET, KM_ITERS, SCANN_ITERS, SCANN_T,
    LEARNED_LR, LEARNED_STEPS, SIGMA, WINDOW_TOKENS, CUE_SHIFT,
    SEEDS, M_SWEEP, ENCODER,
)


# ---------- numerical helpers ----------

def _np_norm(X):
    return (X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)).astype(np.float32)


def _knn_topk_recall(K, cue, ytrue_idx, topk=1):
    """Cosine-similarity exhaustive KNN; recall@top-1 over normalized vectors.

    K: (M, D) keys. cue: (Q, D). ytrue_idx: (Q,) the row index in K of true match.
    Returns mean recall@topk.
    """
    Kn = _np_norm(K)
    cn = _np_norm(cue)
    sim = cn @ Kn.T  # Q x M
    if topk == 1:
        idx = np.argmax(sim, axis=1)
        return float((idx == ytrue_idx).mean())
    topk_idx = np.argpartition(sim, -topk, axis=1)[:, -topk:]
    hits = np.any(topk_idx == ytrue_idx[:, None], axis=1)
    return float(hits.mean())


# ---------- ISOTROPIC k-means (current substrate baseline quantizer) ----------

def _kmeans_isotropic(K, n_parts, iters, seed):
    """Standard L2 k-means partition assignment.

    K: (M, D) normalized keys.
    Returns:
      centroids: (n_parts, D) float32
      assign:    (M,) int64
      quant_err: float -- mean squared L2 distance to assigned centroid
    """
    M, D = K.shape
    g = np.random.default_rng(seed)
    # k-means++ light init: pick first center random; subsequent farthest from current centers
    centroids = np.empty((n_parts, D), dtype=np.float32)
    centroids[0] = K[int(g.integers(0, M))]
    if n_parts > 1:
        # naive farthest-point seeding
        min_dist = np.linalg.norm(K - centroids[0][None], axis=1) ** 2
        for ci in range(1, n_parts):
            # pick row probabilistically proportional to min_dist for diversity
            prob = min_dist / (min_dist.sum() + 1e-12)
            idx = int(g.choice(M, p=prob))
            centroids[ci] = K[idx]
            new_dist = np.linalg.norm(K - centroids[ci][None], axis=1) ** 2
            min_dist = np.minimum(min_dist, new_dist)

    assign = np.zeros(M, dtype=np.int64)
    for it in range(iters):
        # assignment: argmin L2
        # ||k - c||^2 = ||k||^2 - 2 k.c + ||c||^2; since K normalized, ||k||^2 = 1
        sim = K @ centroids.T  # (M, n_parts)
        c_norm_sq = (centroids ** 2).sum(axis=1)  # (n_parts,)
        # negative L2 dist (omit constant ||k||^2)
        scores = 2 * sim - c_norm_sq[None, :]
        new_assign = np.argmax(scores, axis=1).astype(np.int64)
        if it > 0 and (new_assign == assign).mean() > 0.999:
            assign = new_assign
            break
        assign = new_assign
        # update centroids
        for ci in range(n_parts):
            mask = assign == ci
            if mask.sum() > 0:
                centroids[ci] = K[mask].mean(axis=0)
            # else: keep prev centroid (empty cluster fallback)

    # quantization error
    diff = K - centroids[assign]
    quant_err = float((diff ** 2).sum(axis=1).mean())
    return centroids, assign, quant_err


# ---------- ScaNN anisotropic VQ (Guo et al 2020) ----------

def _scann_anisotropic_vq(K, n_parts, iters, T, seed):
    """Anisotropic vector quantization (Guo et al 2020 ScaNN).

    The anisotropic loss per (k, c_i) pair decomposes the residual r = k - c_i into
    components parallel and perpendicular to k:
        r_parallel = (r . k_hat) k_hat        where k_hat = k / ||k||
        r_perp     = r - r_parallel
    And weights them:
        L_aniso(k, c_i) = h_parallel * ||r_parallel||^2 + h_perp * ||r_perp||^2
    with h_parallel / h_perp = T^2 (T=2 gives 4x weight on parallel direction).

    For normalized K (||k||=1):
        ||r_parallel||^2 = (1 - k . c_i)^2
        ||r_perp||^2     = ||c_i||^2 - (k . c_i)^2 - (1 - k . c_i)^2 + 2(1 - k.c_i)
                          actually: ||r_perp||^2 = ||r||^2 - ||r_parallel||^2
                          where ||r||^2 = 1 - 2 k.c_i + ||c_i||^2 (since ||k||=1)

    Assignment: argmin_i L_aniso(k, c_i)
    Update: c_i = argmin_{c} sum_{k in cluster_i} L_aniso(k, c)
            (closed-form via weighted mean -- derived below)

    Closed-form update derivation:
      For fixed cluster S_i with normalized keys {k_j} (||k_j||=1):
      d/dc sum_{j in S_i} [h_par * (1 - k_j.c)^2 + h_perp * (||c||^2 - 2 k_j.c + 1 - (1 - k_j.c)^2)]
      = sum_j [-2 h_par * (1 - k_j.c) k_j + h_perp * (2 c - 2 k_j - 2 (1 - k_j.c) (-k_j))]
      = sum_j [-2 h_par k_j + 2 h_par (k_j.c) k_j + 2 h_perp c - 2 h_perp k_j + 2 h_perp (1 - k_j.c) k_j]

      Set to 0:
      sum_j [h_par (k_j.c) k_j - h_perp (k_j.c) k_j + h_perp c - h_perp k_j + h_perp k_j - h_par k_j] = 0
      Wait, let me redo: h_par - h_perp factor:
      sum_j [h_par (k_j.c) k_j + h_perp c - h_par k_j + h_perp (-k_j.c) k_j] = 0   (after collecting)

      Let h_par = T^2, h_perp = 1, alpha = T^2 - 1 (excess parallel weight).
      Per Guo et al equation 6 closed-form: c = (sum k_j) / |S_i| balanced + alpha-weighted parallel.

      In practice (per ScaNN code): use a few iterations of Newton on the per-cluster loss
      OR approximate with weighted average: c = ((h_par - h_perp) * (sum k_j k_j^T) + h_perp * sum k_j) / |S_i|
      ... actually the closed-form is c_i = (h_perp I + (h_par - h_perp) M)^-1 r where M is per-cluster
      outer-product mean and r is per-cluster key mean. This is a small D x D solve per cluster.

      For computational simplicity and to faithfully follow the Guo et al recipe, we use the
      D x D closed-form update per cluster.

    K: (M, D) normalized keys.
    Returns:
      centroids: (n_parts, D) float32
      assign:    (M,) int64
      quant_err_aniso: float -- mean L_aniso per key (the loss the quantizer minimizes)
      quant_err_l2:    float -- ALSO compute standard L2 error for cross-arm comparability
    """
    M, D = K.shape
    h_par = float(T ** 2)
    h_perp = 1.0
    alpha = h_par - h_perp   # excess parallel weight (>0 since T > 1)

    # Init via standard k-means a few iters first (gives a sensible warm start)
    centroids, assign, _ = _kmeans_isotropic(K, n_parts, max(2, iters // 5), seed)

    for it in range(iters):
        # assignment: argmin L_aniso
        # L = h_par * (1 - k.c)^2 + h_perp * (||c||^2 - 2 k.c + 1 - (1 - k.c)^2)
        # Expand: (1-k.c)^2 = 1 - 2 k.c + (k.c)^2
        # L = h_par - 2 h_par k.c + h_par (k.c)^2 + h_perp ||c||^2 - 2 h_perp k.c + h_perp - h_perp (1 - 2 k.c + (k.c)^2)
        # = h_par - 2 h_par k.c + h_par (k.c)^2 + h_perp ||c||^2 - 2 h_perp k.c + h_perp - h_perp + 2 h_perp k.c - h_perp (k.c)^2
        # = h_par - 2 h_par k.c + h_par (k.c)^2 + h_perp ||c||^2 - h_perp (k.c)^2
        # = h_par - 2 h_par k.c + (h_par - h_perp) (k.c)^2 + h_perp ||c||^2
        # = h_par - 2 h_par k.c + alpha (k.c)^2 + h_perp ||c||^2
        # Drop k-only constant h_par.
        sim = K @ centroids.T  # (M, n_parts)
        c_norm_sq = (centroids ** 2).sum(axis=1)  # (n_parts,)
        L = -2 * h_par * sim + alpha * (sim ** 2) + h_perp * c_norm_sq[None, :]
        new_assign = np.argmin(L, axis=1).astype(np.int64)
        if it > 0 and (new_assign == assign).mean() > 0.999:
            assign = new_assign
            break
        assign = new_assign

        # update centroids via D x D closed-form solve per cluster
        # gradient = sum_j [-2 h_par k_j + 2 alpha (k_j.c) k_j + 2 h_perp c] = 0
        # =>  (h_perp |S_i| I + alpha M_i) c = h_par r_i
        #     where M_i = sum_j k_j k_j^T, r_i = sum_j k_j
        for ci in range(n_parts):
            mask = assign == ci
            if mask.sum() == 0:
                continue
            Ki = K[mask]  # (n_i, D)
            n_i = Ki.shape[0]
            r_i = Ki.sum(axis=0)  # (D,)
            # M_i = Ki.T @ Ki, but for large n_i we use it once
            M_i = Ki.T @ Ki  # (D, D)
            A = h_perp * n_i * np.eye(D, dtype=np.float64) + alpha * M_i.astype(np.float64)
            b = h_par * r_i.astype(np.float64)
            try:
                c_new = np.linalg.solve(A, b).astype(np.float32)
            except np.linalg.LinAlgError:
                c_new = Ki.mean(axis=0).astype(np.float32)
            centroids[ci] = c_new

    # final assignment + losses
    sim = K @ centroids.T
    c_norm_sq = (centroids ** 2).sum(axis=1)
    L = -2 * h_par * sim + alpha * (sim ** 2) + h_perp * c_norm_sq[None, :]
    assign_final = np.argmin(L, axis=1).astype(np.int64)

    # report both losses for cross-arm interpretation
    L_aniso = float(L[np.arange(M), assign_final].mean() + h_par)  # add back dropped constant
    diff = K - centroids[assign_final]
    quant_err_l2 = float((diff ** 2).sum(axis=1).mean())
    return centroids, assign_final, quant_err_aniso_(M, h_par, h_perp, alpha, K, centroids, assign_final), quant_err_l2


def quant_err_aniso_(M, h_par, h_perp, alpha, K, centroids, assign):
    """Compute mean anisotropic loss after fit (for diagnostics)."""
    c_assigned = centroids[assign]
    k_dot_c = (K * c_assigned).sum(axis=1)  # (M,)
    c_sq = (c_assigned ** 2).sum(axis=1)  # (M,)
    # L_per_key = h_par (1 - k.c)^2 + h_perp (||c||^2 + 1 - 2 k.c - (1 - k.c)^2)
    # = h_par - 2 h_par k.c + alpha k.c^2 + h_perp ||c||^2  (constant h_par retained)
    L = h_par - 2 * h_par * k_dot_c + alpha * (k_dot_c ** 2) + h_perp * c_sq
    return float(L.mean())


# ---------- LEARNED anisotropic loss (gradient upper bound) ----------

def _learned_aniso_kmeans(K, n_parts, iters, lr, steps, seed):
    """Gradient-trained per-cluster T weighting; upper bound on anisotropic quantization.

    Parametrize the loss with PER-CLUSTER T_i (positive); train via gradient on the
    classification-loss equivalent (-log p of routing the closest key to each cluster).

    Implementation: alternate (1) hard-assign via current T_i + (2) gradient step on T_i +
    centroid-update via closed-form (same as ScaNN with cluster-specific T).
    """
    M, D = K.shape
    centroids, assign, _ = _kmeans_isotropic(K, n_parts, max(2, iters // 5), seed)
    T_per = np.ones(n_parts, dtype=np.float64) * SCANN_T

    rng = np.random.default_rng(seed * 13 + 7)
    sample_n = min(M, 2000)
    sample_idx = rng.choice(M, sample_n, replace=False)

    for it in range(iters):
        sim_all = K @ centroids.T
        c_norm_sq = (centroids ** 2).sum(axis=1)
        # per-cluster T -> per-key loss matrix
        T2 = T_per ** 2
        alpha_per = T2 - 1.0
        L_mat = -2 * T2[None, :] * sim_all + alpha_per[None, :] * (sim_all ** 2) + c_norm_sq[None, :]
        new_assign = np.argmin(L_mat, axis=1).astype(np.int64)
        if it > 0 and (new_assign == assign).mean() > 0.999:
            assign = new_assign
            break
        assign = new_assign

        # update centroids per-cluster with that cluster's T_i (same closed-form)
        for ci in range(n_parts):
            mask = assign == ci
            if mask.sum() == 0:
                continue
            Ki = K[mask]
            n_i = Ki.shape[0]
            r_i = Ki.sum(axis=0).astype(np.float64)
            M_i = (Ki.T @ Ki).astype(np.float64)
            T2_c = T_per[ci] ** 2
            alpha_c = T2_c - 1.0
            A = n_i * np.eye(D, dtype=np.float64) + alpha_c * M_i
            b = T2_c * r_i
            try:
                centroids[ci] = np.linalg.solve(A, b).astype(np.float32)
            except np.linalg.LinAlgError:
                pass

        # learned-T grad step: minimize sum_j L(k_j, c_{assign(j)}; T_{assign(j)})
        # dL/dT_i for j in S_i: dL/dT (where alpha = T^2-1) = -4T k.c + 2T k.c^2 = 2T (k.c^2 - 2 k.c)
        sim_assigned = (K * centroids[assign]).sum(axis=1)  # (M,)
        for ci in range(n_parts):
            mask = assign == ci
            if mask.sum() == 0:
                continue
            s = sim_assigned[mask]
            grad_T = float(2.0 * T_per[ci] * (s ** 2 - 2 * s).mean())
            T_per[ci] = max(0.1, T_per[ci] - lr * grad_T)

    # final loss accounting
    diff = K - centroids[assign]
    quant_err_l2 = float((diff ** 2).sum(axis=1).mean())
    return centroids, assign, T_per, quant_err_l2


# ---------- per-cluster cone-alignment metric ----------

def _cone_alignment(K, centroids, assign):
    """Per-cluster cosine between centroid (unit) and mean direction of keys (unit).

    Returns mean across clusters (weighted by cluster size).
    """
    n_parts = centroids.shape[0]
    total = 0.0
    total_w = 0
    for ci in range(n_parts):
        mask = assign == ci
        n_i = int(mask.sum())
        if n_i < 2:
            continue
        mean_k = K[mask].mean(axis=0)
        mean_k_n = mean_k / (np.linalg.norm(mean_k) + 1e-12)
        c_n = centroids[ci] / (np.linalg.norm(centroids[ci]) + 1e-12)
        total += float(mean_k_n @ c_n) * n_i
        total_w += n_i
    return total / max(1, total_w)


# ---------- arm evaluation: route + within-partition rerank ----------

def _route_and_rerank(K, centroids, assign, cue, ytrue_idx):
    """For each cue: argmax cosine vs centroids -> route to partition -> rerank within partition.

    Returns (route_acc, recall_at_1) where:
      route_acc = fraction of cues routed to the partition holding the true key
      recall_at_1 = fraction of cues where reranked top-1 within routed partition is the true key
    """
    Q = cue.shape[0]
    # route via cosine vs centroid (NOT anisotropic; production ScaNN routing uses normalized centroids)
    Cn = _np_norm(centroids)
    cn = _np_norm(cue)
    sim_to_centroid = cn @ Cn.T  # (Q, n_parts)
    routes = np.argmax(sim_to_centroid, axis=1).astype(np.int64)
    true_partition = assign[ytrue_idx]
    route_acc = float((routes == true_partition).mean())

    # rerank within routed partition by exact cosine vs the keys in that partition
    Kn = _np_norm(K)
    hits = 0
    for q in range(Q):
        p = int(routes[q])
        idx_in_p = np.where(assign == p)[0]
        if len(idx_in_p) == 0:
            continue
        sims = Kn[idx_in_p] @ cn[q]  # (n_in_p,)
        best = idx_in_p[int(np.argmax(sims))]
        if best == ytrue_idx[q]:
            hits += 1
    recall_at_1 = hits / Q
    return route_acc, recall_at_1


# ---------- per-seed arms runner ----------

def _arms_numpy(Kp, seed_for_arms, M_target):
    """Run all four arms on the (M_target x D) key slice; pure numpy."""
    M = Kp.shape[0]
    D = Kp.shape[1]
    g = np.random.default_rng(seed_for_arms)
    # normalize keys to unit-norm (matches retrieval-by-cosine convention)
    K = _np_norm(Kp)

    # cues: subset of keys + cone-aligned noise
    if M <= MAX_Q:
        qidx = np.arange(M)
    else:
        qidx = np.sort(g.choice(M, MAX_Q, replace=False))
    noise = (SIGMA * g.standard_normal((len(qidx), D))).astype(np.float32)
    cue = (K[qidx] + noise).astype(np.float32)
    ytrue_idx = qidx.astype(np.int64)

    # partition count: target ~PART_SIZE_TARGET per partition
    n_parts = max(2, M // PART_SIZE_TARGET)

    # ARM_KNN_BASELINE (rank-blind sentinel; Fix #28)
    arm_knn = _knn_topk_recall(K, cue, ytrue_idx, topk=KNN_TOPK)

    # ARM_ISOTROPIC_KMEANS
    t0 = time.time()
    cen_iso, assign_iso, qerr_iso_l2 = _kmeans_isotropic(K, n_parts, KM_ITERS, seed_for_arms)
    route_acc_iso, recall_iso = _route_and_rerank(K, cen_iso, assign_iso, cue, ytrue_idx)
    cone_iso = _cone_alignment(K, cen_iso, assign_iso)
    t_iso = time.time() - t0

    # ARM_SCANN_ANISOTROPIC_VQ
    t0 = time.time()
    cen_scann, assign_scann, qerr_scann_aniso, qerr_scann_l2 = _scann_anisotropic_vq(
        K, n_parts, SCANN_ITERS, SCANN_T, seed_for_arms + 1
    )
    route_acc_scann, recall_scann = _route_and_rerank(K, cen_scann, assign_scann, cue, ytrue_idx)
    cone_scann = _cone_alignment(K, cen_scann, assign_scann)
    t_scann = time.time() - t0

    # ARM_LEARNED_ANISO_LOSS
    t0 = time.time()
    cen_learned, assign_learned, T_per, qerr_learned_l2 = _learned_aniso_kmeans(
        K, n_parts, SCANN_ITERS, LEARNED_LR, LEARNED_STEPS, seed_for_arms + 2
    )
    route_acc_learned, recall_learned = _route_and_rerank(K, cen_learned, assign_learned, cue, ytrue_idx)
    cone_learned = _cone_alignment(K, cen_learned, assign_learned)
    t_learned = time.time() - t0

    # quantization-error reduction (geometric metric for MIMO/DG pattern catch)
    # if scann_l2 > iso_l2 the geometric was made WORSE; expected for ScaNN since it does NOT
    # minimize L2 -- the diagnostic uses the OWN-loss reduction (qerr_scann_aniso vs the L_aniso
    # computed on iso centroids).
    h_par = SCANN_T ** 2
    h_perp = 1.0
    alpha = h_par - h_perp
    qerr_iso_under_aniso = quant_err_aniso_(M, h_par, h_perp, alpha, K, cen_iso, assign_iso)
    quant_err_aniso_reduction = float((qerr_iso_under_aniso - qerr_scann_aniso) / max(qerr_iso_under_aniso, 1e-9))

    return {
        "M": M_target,
        "n_parts": n_parts,
        "arm_knn_baseline": round(arm_knn, 4),
        "arm_isotropic_kmeans": {
            "route_acc": round(route_acc_iso, 4),
            "recall_at_1": round(recall_iso, 4),
            "quant_err_l2": round(qerr_iso_l2, 6),
            "cone_alignment": round(cone_iso, 4),
            "elapsed_s": round(t_iso, 2),
        },
        "arm_scann_anisotropic_vq": {
            "route_acc": round(route_acc_scann, 4),
            "recall_at_1": round(recall_scann, 4),
            "quant_err_l2": round(qerr_scann_l2, 6),
            "quant_err_aniso": round(qerr_scann_aniso, 6),
            "quant_err_aniso_reduction_vs_iso": round(quant_err_aniso_reduction, 4),
            "cone_alignment": round(cone_scann, 4),
            "elapsed_s": round(t_scann, 2),
        },
        "arm_learned_aniso_loss": {
            "route_acc": round(route_acc_learned, 4),
            "recall_at_1": round(recall_learned, 4),
            "quant_err_l2": round(qerr_learned_l2, 6),
            "cone_alignment": round(cone_learned, 4),
            "T_per_cluster_mean": round(float(np.mean(T_per)), 3),
            "T_per_cluster_std": round(float(np.std(T_per)), 3),
            "elapsed_s": round(t_learned, 2),
        },
        "lift_scann_over_iso": round(recall_scann - recall_iso, 4),
        "lift_learned_over_iso": round(recall_learned - recall_iso, 4),
        "lift_route_scann_over_iso": round(route_acc_scann - route_acc_iso, 4),
    }


# ---------- adversarial-similarity facts (consecutive-token stride-1 windows) ----------

_PROSE_POOL = [
    "The cerebellum contains more neurons than the rest of the brain combined and plays a critical role in motor learning and sensorimotor integration. Granule cells in the cerebellar cortex receive sparse fan-in connections from mossy fibers, with each granule cell typically synapsing with only four to seven mossy fiber inputs. This sparse expansion creates a high-dimensional representation that separates similar input patterns into distinguishable patterns of granule cell activity.",
    "Drosophila olfactory processing relies on a similar sparse expansion architecture. The roughly fifty projection neurons sending information to the mushroom body diverge onto two thousand Kenyon cells, with each Kenyon cell sampling input from only about six projection neurons. Hashing approaches inspired by this fly architecture have proven competitive with sophisticated deep learning methods for nearest neighbor search in high dimensional spaces.",
    "Hyperdimensional computing operates on vectors of thousands of dimensions and uses simple operations like binding multiplication and superposition addition to compose structured information. The capacity of dense superposition memory scales with the effective dimensionality of the underlying representation space and decreases when stored items become correlated rather than orthogonal.",
    "Anisotropy in pretrained language model representations limits direct application of distance based retrieval methods. Token embeddings in models like BERT and Pythia cluster in narrow cones rather than spreading uniformly across the hypersphere. This concentration reduces the effective dimensionality from theoretical bounds set by the embedding size to a much smaller fraction determined by the eigenvalue spread of the covariance matrix.",
    "Whitening transformations can rotate anisotropic distributions to appear isotropic but cannot increase the underlying rank of a representation. The Mu and Viswanath analysis showed that simple post processing fixes appear to help on word similarity benchmarks while leaving the deeper rank deficiency unchanged. Architectural approaches that expand into higher dimensional sparse spaces address the rank limitation more fundamentally.",
    "Random sparse projections create new axes of representation by combining input dimensions in unpredictable ways. Some projections happen to emphasize directions orthogonal to the dominant anisotropy cone, recovering separability that was lost in the original space. The fly olfactory circuit appears to exploit exactly this property to discriminate odors that share many of the same molecular features.",
    "Locality sensitive hashing partitions vectors into buckets such that similar inputs land in the same bucket with high probability. Charikar described a hyperplane based method using sign patterns from random Gaussian projections. The output is a binary sketch where Hamming distance approximates angular distance in the original space and the dimensionality of the sketch can be tuned independently of the input dimensionality.",
    "Memory augmented neural networks attempt to combine the flexibility of dense gradient based learning with the precise content addressable retrieval of external storage. Attention mechanisms provide a continuous approximation to retrieval that can be trained end to end but suffer from quadratic complexity in the number of stored items and require careful temperature calibration to avoid mass collapsing to uniform distributions.",
    "Substrate native hyperdimensional architectures aim to perform inference without calling out to dense neural network components at retrieval time. The encoder may be used once during setup to extract hidden state representations but the inference time operations stay within the hyperdimensional algebra. This separation allows the substrate to be analyzed and verified independently of the encoder used to bootstrap its initial representations.",
    "Capacity bounds for associative memory derive from the dimensionality of the storage substrate and the orthogonality of stored patterns. When the substrate dimensionality is large and stored patterns are uncorrelated the capacity scales linearly with dimensions. When patterns are correlated as in real language model residuals the effective capacity drops dramatically and recall accuracy collapses past a regime dependent threshold.",
    "The relationship between sparse expansion and retrieval accuracy depends on the specific structure of the input distribution. Synthetic random inputs achieve capacity matching theoretical bounds while naturalistic anisotropic inputs require either explicit decorrelation or architectural compensation. The cerebellar fly inspired sparse fan in approach addresses the latter by creating new axes through random combination rather than attempting to reshape the underlying input distribution.",
]


def _build_adversarial_prose(g, target_tokens):
    pool = list(_PROSE_POOL)
    pieces = []
    total_words = 0
    while total_words < target_tokens:
        idx = int(g.integers(0, len(pool)))
        pieces.append(pool[idx])
        total_words += len(pool[idx].split())
    return " ".join(pieces)


def _facts_and_encode(seed: int, n_total: int) -> np.ndarray:
    """Setup-time encoder hoisting via _probe module.

    Substrate-only at inference; encoder runs ONCE per seed; rest is pure numpy.
    """
    os.environ["HDLAB_RUN_MODE"] = RUN_MODE
    import experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 as _probe
    _probe.ENCODER = ENCODER
    encode = _probe.encode
    train_contrastive = _probe.train_contrastive

    g = np.random.default_rng(seed)
    prose = _build_adversarial_prose(g, target_tokens=n_total + WINDOW_TOKENS + CUE_SHIFT + 50)
    words = prose.split()
    needed = n_total + WINDOW_TOKENS + CUE_SHIFT
    while len(words) < needed:
        prose = _build_adversarial_prose(g, target_tokens=needed * 2)
        words = prose.split()
    keys = []
    cues = []
    for i in range(n_total):
        keys.append(" ".join(words[i:i + WINDOW_TOKENS]))
        cues.append(" ".join(words[i + CUE_SHIFT:i + CUE_SHIFT + WINDOW_TOKENS]))
    print("[adv-facts] seed=%d n_total=%d words=%d window=%d shift=%d sample_key=%r" % (
        seed, n_total, len(words), WINDOW_TOKENS, CUE_SHIFT, keys[0][:60]
    ), flush=True)

    K = encode(keys)
    Q = encode(cues)

    perm = g.permutation(n_total)
    tr = perm[:TRAIN_M]
    ho = perm[TRAIN_M:]
    W = train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed)
    Kp_all = (K[ho] @ W).astype(np.float32)
    print("[adv-encode] seed=%d encoded=%d projected_dim=%d held_out=%d" % (
        seed, n_total, PROJ_DIM, len(Kp_all)), flush=True)
    return Kp_all


def run_unit(seed: int) -> Dict:
    n_total = max(M_SWEEP) + TRAIN_M
    print("[seed=%d] encoder=%s n_total=%d M_SWEEP=%s mode=%s" % (
        seed, ENCODER, n_total, M_SWEEP, RUN_MODE), flush=True)
    t_enc = time.time()
    Kp_all = _facts_and_encode(seed, n_total)
    t_enc_s = time.time() - t_enc
    print("  [seed=%d] encoder elapsed=%.1fs" % (seed, t_enc_s), flush=True)

    by_M = {}
    for M in M_SWEEP:
        arms_seed = seed * 7 + M
        Kp_M = Kp_all[:M].astype(np.float32)
        t0 = time.time()
        a = _arms_numpy(Kp_M, arms_seed, M)
        by_M["M%d" % M] = a
        print(("  [seed=%d M=%d] knn=%.3f | "
               "iso_kmeans: route=%.3f recall=%.3f qerr_l2=%.4f cone=%.3f | "
               "scann_aniso: route=%.3f recall=%.3f qerr_aniso=%.4f qerr_red=%.3f cone=%.3f | "
               "learned: route=%.3f recall=%.3f cone=%.3f T_mean=%.2f | "
               "lift_scann=%.3f lift_learned=%.3f lift_route_scann=%.3f t=%.1fs"
               ) % (
            seed, M, a["arm_knn_baseline"],
            a["arm_isotropic_kmeans"]["route_acc"], a["arm_isotropic_kmeans"]["recall_at_1"],
            a["arm_isotropic_kmeans"]["quant_err_l2"], a["arm_isotropic_kmeans"]["cone_alignment"],
            a["arm_scann_anisotropic_vq"]["route_acc"], a["arm_scann_anisotropic_vq"]["recall_at_1"],
            a["arm_scann_anisotropic_vq"]["quant_err_aniso"],
            a["arm_scann_anisotropic_vq"]["quant_err_aniso_reduction_vs_iso"],
            a["arm_scann_anisotropic_vq"]["cone_alignment"],
            a["arm_learned_aniso_loss"]["route_acc"], a["arm_learned_aniso_loss"]["recall_at_1"],
            a["arm_learned_aniso_loss"]["cone_alignment"],
            a["arm_learned_aniso_loss"]["T_per_cluster_mean"],
            a["lift_scann_over_iso"], a["lift_learned_over_iso"], a["lift_route_scann_over_iso"],
            time.time() - t0,
        ), flush=True)
    return {"seed": seed, "by_M": by_M, "encoder_elapsed_s": round(t_enc_s, 2),
            "run_mode": RUN_MODE, "M_SWEEP": M_SWEEP, "N": PROJ_DIM}


def _med_std(values):
    if not values:
        return 0.0, 0.0
    return float(np.median(values)), float(np.std(values))


def _cv(values):
    vals = [v for v in values if isinstance(v, (int, float)) and not math.isnan(v) and v >= 0]
    if len(vals) < 2:
        return float("nan")
    m = float(np.mean(vals))
    if abs(m) < 1e-9:
        return 0.0
    return float(np.std(vals) / abs(m))


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    M_max = max(M_SWEEP)
    M_min = min(M_SWEEP)

    def vals(M, arm, key):
        out = []
        for u in units:
            r = u["by_M"].get("M%d" % M, {}).get(arm, {})
            v = r.get(key) if isinstance(r, dict) else None
            if v is not None and isinstance(v, (int, float)) and not math.isnan(v):
                out.append(float(v))
        return out

    def vals_top(M, key):
        out = []
        for u in units:
            r = u["by_M"].get("M%d" % M, {})
            v = r.get(key)
            if v is not None and isinstance(v, (int, float)) and not math.isnan(v):
                out.append(float(v))
        return out

    # Sentinel
    knn_vals = vals_top(M_min, "arm_knn_baseline")
    knn_med, knn_std = _med_std(knn_vals)
    knn_pass = knn_med >= BAND_KNN_SENTINEL

    # Mechanism at M_max
    iso_recall_vals = vals(M_max, "arm_isotropic_kmeans", "recall_at_1")
    scann_recall_vals = vals(M_max, "arm_scann_anisotropic_vq", "recall_at_1")
    learned_recall_vals = vals(M_max, "arm_learned_aniso_loss", "recall_at_1")
    iso_route_vals = vals(M_max, "arm_isotropic_kmeans", "route_acc")
    scann_route_vals = vals(M_max, "arm_scann_anisotropic_vq", "route_acc")
    learned_route_vals = vals(M_max, "arm_learned_aniso_loss", "route_acc")
    iso_qerr_vals = vals(M_max, "arm_isotropic_kmeans", "quant_err_l2")
    scann_qerr_red_vals = vals(M_max, "arm_scann_anisotropic_vq", "quant_err_aniso_reduction_vs_iso")
    iso_cone_vals = vals(M_max, "arm_isotropic_kmeans", "cone_alignment")
    scann_cone_vals = vals(M_max, "arm_scann_anisotropic_vq", "cone_alignment")

    iso_recall, iso_std = _med_std(iso_recall_vals)
    scann_recall, scann_std = _med_std(scann_recall_vals)
    learned_recall, learned_std = _med_std(learned_recall_vals)
    iso_route, _ = _med_std(iso_route_vals)
    scann_route, _ = _med_std(scann_route_vals)
    learned_route, _ = _med_std(learned_route_vals)
    scann_qerr_red, _ = _med_std(scann_qerr_red_vals)
    iso_cone, _ = _med_std(iso_cone_vals)
    scann_cone, _ = _med_std(scann_cone_vals)

    lift_scann = scann_recall - iso_recall
    lift_learned = learned_recall - iso_recall
    lift_route_scann = scann_route - iso_route

    scann_cv = _cv(scann_recall_vals)

    # Q-discipline
    q_flags = []
    for name, val in [("scann_recall", scann_recall), ("iso_recall", iso_recall),
                       ("learned_recall", learned_recall), ("knn_sentinel", knn_med)]:
        if val >= BAND_Q_SATURATION:
            q_flags.append("[Q-DISCIPLINE: %s=%.4f >= %.3f -- suspect saturation]" % (
                name, val, BAND_Q_SATURATION))
    q_note = " ".join(q_flags) + (" " if q_flags else "")

    summ = (
        "knn@M=%d=%.3f | iso_km: route=%.3f recall=%.3f cone=%.3f | "
        "scann: route=%.3f recall=%.3f qerr_red=%.3f cone=%.3f | "
        "learned: route=%.3f recall=%.3f | "
        "lift_scann_recall=%.3f lift_scann_route=%.3f lift_learned_recall=%.3f | "
        "scann_cv=%.3f"
    ) % (M_min, knn_med, iso_route, iso_recall, iso_cone,
         scann_route, scann_recall, scann_qerr_red, scann_cone,
         learned_route, learned_recall,
         lift_scann, lift_route_scann, lift_learned, scann_cv)

    detail = {
        "M_eval": M_max,
        "M_sentinel": M_min,
        "knn_at_sentinel": round(knn_med, 4),
        "iso_kmeans_recall": round(iso_recall, 4),
        "iso_kmeans_route_acc": round(iso_route, 4),
        "iso_kmeans_cone_alignment": round(iso_cone, 4),
        "scann_anisotropic_recall": round(scann_recall, 4),
        "scann_anisotropic_route_acc": round(scann_route, 4),
        "scann_anisotropic_quant_err_reduction": round(scann_qerr_red, 4),
        "scann_anisotropic_cone_alignment": round(scann_cone, 4),
        "scann_anisotropic_std": round(scann_std, 4),
        "scann_anisotropic_cv": round(scann_cv, 4),
        "learned_recall": round(learned_recall, 4),
        "learned_route_acc": round(learned_route, 4),
        "lift_scann_recall_over_iso": round(lift_scann, 4),
        "lift_scann_route_over_iso": round(lift_route_scann, 4),
        "lift_learned_recall_over_iso": round(lift_learned, 4),
        "knn_sentinel_pass": bool(knn_pass),
        "n_seeds": len(units),
        "bands": {
            "HP_CHAIN_GRADE": BAND_HP_CHAIN_GRADE,
            "HP_LIFT": BAND_HP_LIFT,
            "HP_ROUTE_ACC": BAND_HP_ROUTE_ACC,
            "HP_PARTIAL_LIFT": BAND_HP_PARTIAL_LIFT,
            "MIDDLE_LIFT": BAND_MIDDLE_LIFT,
            "HF_LIFT": BAND_HF_LIFT,
            "HF_GEOMETRIC_LIFT": BAND_HF_GEOMETRIC_LIFT,
            "KNN_SENTINEL": BAND_KNN_SENTINEL,
            "CV_HP": BAND_CV_HP,
            "Q_SATURATION": BAND_Q_SATURATION,
        },
        "CONFIG_VERSION": CONFIG_VERSION,
        "cites": [
            "research_gap2_REFRAME_anisotropy_is_feature_2026-06-26",
            "exp_dev_handoff_research_gap2_REFRAME_anisotropy_is_feature_2026-06-26",
            "Guo_et_al_2020_ScaNN_arXiv_1908.10396",
            "substrate_partition_routing_hierarchical_2level_v1",
            "substrate_partition_routing_10M_full_v2",
        ],
    }

    # GATE 0: KNN sentinel (Fix #28 corruption catch)
    if not knn_pass:
        return ("HARD_FAIL",
                ("HARD_FAIL_KNN_SENTINEL: KNN@M=%d = %.3f < %.2f -> keys themselves are corrupted; "
                 "any routing-arm lift is artifact. %s%s") % (
                    M_min, knn_med, BAND_KNN_SENTINEL, q_note, summ),
                detail)

    # GATE 1: MIMO/DG-pattern catch -- huge geometric improvement but no recall lift
    if (scann_qerr_red >= BAND_HF_GEOMETRIC_LIFT and lift_scann <= 0.0):
        return ("HARD_FAIL",
                ("HARD_FAIL_GEOMETRIC_NO_RECALL: scann_quant_err_reduction=%.3f >= %.2f (geometric "
                 "improvement) BUT scann_recall_lift=%.3f <= 0 (NO recall benefit; MIMO/DG pattern). "
                 "Substrate's Tikhonov cleanup may already exploit the cone; anisotropy-aware "
                 "quantization just rearranges the same regularizer. %s%s") % (
                    scann_qerr_red, BAND_HF_GEOMETRIC_LIFT, lift_scann, q_note, summ),
                detail)

    # GATE 2: HARD_PASS_CHAIN_GRADE_AT_M_100K
    if (scann_recall >= BAND_HP_CHAIN_GRADE
            and lift_scann >= BAND_HP_LIFT
            and scann_route >= BAND_HP_ROUTE_ACC
            and (math.isnan(scann_cv) or scann_cv <= BAND_CV_HP)
            and knn_pass):
        return ("HARD_PASS",
                ("HARD_PASS_CHAIN_GRADE_AT_M_%d: scann_recall=%.3f >= %.2f AND "
                 "lift_over_iso=%.3f >= %.2f AND route_acc=%.3f >= %.2f AND cv=%.3f <= %.2f. "
                 "Anisotropic-VQ strengthens substrate partition routing spine on real Pythia "
                 "adversarial-similarity keys at M=%d. %s%s") % (
                    M_max, scann_recall, BAND_HP_CHAIN_GRADE, lift_scann, BAND_HP_LIFT,
                    scann_route, BAND_HP_ROUTE_ACC, scann_cv, BAND_CV_HP, M_max, q_note, summ),
                detail)

    # GATE 3: HARD_PASS_PARTIAL
    if lift_scann >= BAND_HP_PARTIAL_LIFT and lift_scann > 0:
        return ("HARD_PASS",
                ("HARD_PASS_PARTIAL_SCANN_ANISO: lift_over_iso=%.3f >= %.2f at M=%d but not all "
                 "HARD_PASS conditions met (recall=%.3f vs >=%.2f; route_acc=%.3f vs >=%.2f; "
                 "cv=%.3f vs <=%.2f). Mechanism helps but doesn't chain-grade. %s%s") % (
                    lift_scann, BAND_HP_PARTIAL_LIFT, M_max,
                    scann_recall, BAND_HP_CHAIN_GRADE, scann_route, BAND_HP_ROUTE_ACC,
                    scann_cv, BAND_CV_HP, q_note, summ),
                detail)

    # GATE 4: MIDDLE_BAND
    if lift_scann > BAND_MIDDLE_LIFT:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_SCANN_ANISO: lift_over_iso=%.3f in (%.2f, %.2f] at M=%d -- "
                 "anisotropic-VQ helps modestly but doesn't chain-grade. %s%s") % (
                    lift_scann, BAND_MIDDLE_LIFT, BAND_HP_PARTIAL_LIFT, M_max, q_note, summ),
                detail)

    # GATE 5: HARD_FAIL_DOESNT_HELP
    return ("HARD_FAIL",
            ("HARD_FAIL_ANISOTROPIC_VQ_DOESNT_HELP: lift_over_iso=%.3f <= %.2f at M=%d. "
             "Isotropic k-means is already optimal for substrate's cone at this regime; "
             "ScaNN anisotropic VQ does not add value. learned=%.3f (lift=%.3f) "
             "confirms whether upper-bound also fails. %s%s") % (
                lift_scann, BAND_HF_LIFT, M_max, learned_recall, lift_learned, q_note, summ),
            detail)


# ---------- self-test ----------

def _selftest():
    """Validate: (a) helpers; (b) iso k-means convergence; (c) ScaNN aniso convergence;
    (d) learned aniso convergence; (e) route_and_rerank ground-truth; (f) cone-alignment math;
    (g) band ordering + verdict synthetic paths."""

    g = np.random.default_rng(0)
    D = 64
    M = 400
    n_parts = M // 50  # 8 partitions for the toy

    # Build keys: clustered around a few directions
    n_clusters_true = 6
    centers_true = _np_norm(g.standard_normal((n_clusters_true, D)).astype(np.float32))
    keys = []
    labels_true = []
    for ci in range(n_clusters_true):
        n_c = M // n_clusters_true + (1 if ci < M % n_clusters_true else 0)
        cs = centers_true[ci][None] + 0.20 * g.standard_normal((n_c, D)).astype(np.float32)
        keys.append(cs)
        labels_true.extend([ci] * n_c)
    K_raw = np.concatenate(keys, axis=0)[:M]
    K = _np_norm(K_raw)

    # (a) helpers
    assert K.shape == (M, D)
    assert np.allclose(np.linalg.norm(K, axis=1), 1.0, atol=1e-5)

    # (b) iso k-means converges + non-trivial assignment
    cen_iso, assign_iso, qerr_iso_l2 = _kmeans_isotropic(K, n_parts, KM_ITERS, 7)
    assert cen_iso.shape == (n_parts, D)
    assert assign_iso.shape == (M,)
    # at least 2 clusters used
    used = len(set(assign_iso.tolist()))
    assert used >= 2, "iso kmeans collapsed to 1 cluster"
    # qerr_l2 finite + positive
    assert qerr_iso_l2 > 0 and qerr_iso_l2 < 4.0, "iso qerr_l2 out of range: %f" % qerr_iso_l2
    print("[selftest] iso_kmeans: clusters_used=%d qerr_l2=%.4f" % (used, qerr_iso_l2), flush=True)

    # (c) ScaNN aniso converges + produces valid centroids
    cen_scann, assign_scann, qerr_scann_aniso, qerr_scann_l2 = _scann_anisotropic_vq(
        K, n_parts, SCANN_ITERS, SCANN_T, 7
    )
    assert cen_scann.shape == (n_parts, D)
    assert assign_scann.shape == (M,)
    used_scann = len(set(assign_scann.tolist()))
    assert used_scann >= 2, "scann collapsed to 1 cluster"
    # qerr_scann_aniso should be LOWER than iso under the same loss (sanity check)
    h_par = SCANN_T ** 2
    h_perp = 1.0
    alpha = h_par - h_perp
    qerr_iso_under_aniso = quant_err_aniso_(M, h_par, h_perp, alpha, K, cen_iso, assign_iso)
    assert qerr_scann_aniso <= qerr_iso_under_aniso + 1e-4, (
        "ScaNN doesn't minimize its OWN loss: scann=%f iso_under_scann=%f" % (
            qerr_scann_aniso, qerr_iso_under_aniso))
    print("[selftest] scann_aniso: clusters_used=%d qerr_aniso=%.4f vs iso_under_aniso=%.4f" % (
        used_scann, qerr_scann_aniso, qerr_iso_under_aniso), flush=True)

    # (d) learned aniso runs + produces T per cluster
    cen_learned, assign_learned, T_per, qerr_learned_l2 = _learned_aniso_kmeans(
        K, n_parts, 5, LEARNED_LR, 30, 7
    )
    assert cen_learned.shape == (n_parts, D)
    assert T_per.shape == (n_parts,)
    assert (T_per > 0).all()
    print("[selftest] learned_aniso: T_mean=%.3f T_std=%.3f" % (
        float(np.mean(T_per)), float(np.std(T_per))), flush=True)

    # (e) route_and_rerank on identity cues should be near-perfect
    cue_id = K.copy()
    ytrue_idx_id = np.arange(M, dtype=np.int64)
    route_acc, recall = _route_and_rerank(K, cen_iso, assign_iso, cue_id, ytrue_idx_id)
    # at noise-free identity, route_acc should be 1.0 (since cue==key, cue's closest centroid is key's partition)
    assert route_acc >= 0.95, "identity route_acc too low: %.3f" % route_acc
    # recall@1 on identity cues should be 1.0 (key is in its own partition; rerank finds it)
    assert recall >= 0.95, "identity recall too low: %.3f" % recall
    print("[selftest] route_and_rerank identity: route_acc=%.3f recall=%.3f" % (route_acc, recall),
          flush=True)

    # (f) cone-alignment math: identity case should be ~1.0 since centroid is mean of cluster
    # (for iso k-means centroid IS the cluster mean, so post-norm cone alignment is high)
    cone = _cone_alignment(K, cen_iso, assign_iso)
    assert cone >= BAND_CONE_ALIGN_MIN, "iso k-means cone_alignment too low: %.3f" % cone
    print("[selftest] cone_alignment iso: %.3f >= %.2f" % (cone, BAND_CONE_ALIGN_MIN), flush=True)

    # (g) band assertions + verdict synthetic paths
    assert BAND_HF_LIFT < BAND_MIDDLE_LIFT < BAND_HP_PARTIAL_LIFT < BAND_HP_LIFT

    # HP_CHAIN_GRADE path
    mock_hp = [{"by_M": {"M%d" % max(M_SWEEP): {
        "arm_knn_baseline": 0.95,
        "arm_isotropic_kmeans": {"route_acc": 0.85, "recall_at_1": 0.55, "quant_err_l2": 0.10, "cone_alignment": 0.40},
        "arm_scann_anisotropic_vq": {"route_acc": 0.97, "recall_at_1": 0.72, "quant_err_l2": 0.12,
                                      "quant_err_aniso": 0.05, "quant_err_aniso_reduction_vs_iso": 0.30,
                                      "cone_alignment": 0.55},
        "arm_learned_aniso_loss": {"route_acc": 0.98, "recall_at_1": 0.75, "quant_err_l2": 0.11,
                                    "cone_alignment": 0.60, "T_per_cluster_mean": 2.5, "T_per_cluster_std": 0.5},
        "lift_scann_over_iso": 0.17, "lift_learned_over_iso": 0.20, "lift_route_scann_over_iso": 0.12,
    }, "M%d" % min(M_SWEEP): {"arm_knn_baseline": 0.95}}}]
    # also need M_min sentinel entry
    mock_hp[0]["by_M"]["M%d" % min(M_SWEEP)] = {"arm_knn_baseline": 0.95,
        "arm_isotropic_kmeans": {"route_acc": 0.9, "recall_at_1": 0.95, "quant_err_l2": 0.05, "cone_alignment": 0.5},
        "arm_scann_anisotropic_vq": {"route_acc": 0.9, "recall_at_1": 0.96, "quant_err_l2": 0.05,
                                      "quant_err_aniso": 0.02, "quant_err_aniso_reduction_vs_iso": 0.1,
                                      "cone_alignment": 0.5},
        "arm_learned_aniso_loss": {"route_acc": 0.9, "recall_at_1": 0.96, "quant_err_l2": 0.05,
                                    "cone_alignment": 0.5, "T_per_cluster_mean": 2.0, "T_per_cluster_std": 0.1},
        "lift_scann_over_iso": 0.01, "lift_learned_over_iso": 0.01, "lift_route_scann_over_iso": 0.0,
    }
    mock_hp = mock_hp * 3
    v, msg, _ = compute_verdict(mock_hp)
    assert v == "HARD_PASS" and "CHAIN_GRADE" in msg, "HP_CHAIN_GRADE path failed: %s | %s" % (v, msg[:200])
    print("[selftest] verdict HP_CHAIN_GRADE path PASS", flush=True)

    # HF_KNN_SENTINEL path
    mock_knn_fail = [{"by_M": {
        "M%d" % min(M_SWEEP): {"arm_knn_baseline": 0.50,
            "arm_isotropic_kmeans": {"route_acc": 0.9, "recall_at_1": 0.5, "quant_err_l2": 0.05, "cone_alignment": 0.5},
            "arm_scann_anisotropic_vq": {"route_acc": 0.9, "recall_at_1": 0.5, "quant_err_l2": 0.05,
                                          "quant_err_aniso": 0.05, "quant_err_aniso_reduction_vs_iso": 0.1,
                                          "cone_alignment": 0.5},
            "arm_learned_aniso_loss": {"route_acc": 0.9, "recall_at_1": 0.5, "quant_err_l2": 0.05,
                                        "cone_alignment": 0.5, "T_per_cluster_mean": 2.0, "T_per_cluster_std": 0.1},
            "lift_scann_over_iso": 0.0, "lift_learned_over_iso": 0.0, "lift_route_scann_over_iso": 0.0},
        "M%d" % max(M_SWEEP): {"arm_knn_baseline": 0.30,
            "arm_isotropic_kmeans": {"route_acc": 0.5, "recall_at_1": 0.3, "quant_err_l2": 0.1, "cone_alignment": 0.3},
            "arm_scann_anisotropic_vq": {"route_acc": 0.6, "recall_at_1": 0.4, "quant_err_l2": 0.1,
                                          "quant_err_aniso": 0.05, "quant_err_aniso_reduction_vs_iso": 0.3,
                                          "cone_alignment": 0.4},
            "arm_learned_aniso_loss": {"route_acc": 0.65, "recall_at_1": 0.45, "quant_err_l2": 0.1,
                                        "cone_alignment": 0.45, "T_per_cluster_mean": 2.5, "T_per_cluster_std": 0.3},
            "lift_scann_over_iso": 0.1, "lift_learned_over_iso": 0.15, "lift_route_scann_over_iso": 0.1},
    }}] * 3
    v, msg, _ = compute_verdict(mock_knn_fail)
    assert v == "HARD_FAIL" and "KNN_SENTINEL" in msg, "HF_KNN_SENTINEL path failed: %s | %s" % (v, msg[:200])
    print("[selftest] verdict HF_KNN_SENTINEL path PASS", flush=True)

    # HF_GEOMETRIC_NO_RECALL (MIMO/DG pattern)
    mock_geom_no_recall = [{"by_M": {
        "M%d" % min(M_SWEEP): {"arm_knn_baseline": 0.95,
            "arm_isotropic_kmeans": {"route_acc": 0.9, "recall_at_1": 0.95, "quant_err_l2": 0.05, "cone_alignment": 0.5},
            "arm_scann_anisotropic_vq": {"route_acc": 0.9, "recall_at_1": 0.95, "quant_err_l2": 0.05,
                                          "quant_err_aniso": 0.05, "quant_err_aniso_reduction_vs_iso": 0.1,
                                          "cone_alignment": 0.5},
            "arm_learned_aniso_loss": {"route_acc": 0.9, "recall_at_1": 0.95, "quant_err_l2": 0.05,
                                        "cone_alignment": 0.5, "T_per_cluster_mean": 2.0, "T_per_cluster_std": 0.1},
            "lift_scann_over_iso": 0.0, "lift_learned_over_iso": 0.0, "lift_route_scann_over_iso": 0.0},
        "M%d" % max(M_SWEEP): {"arm_knn_baseline": 0.90,
            "arm_isotropic_kmeans": {"route_acc": 0.85, "recall_at_1": 0.55, "quant_err_l2": 0.10, "cone_alignment": 0.40},
            "arm_scann_anisotropic_vq": {"route_acc": 0.96, "recall_at_1": 0.53, "quant_err_l2": 0.14,
                                          "quant_err_aniso": 0.02, "quant_err_aniso_reduction_vs_iso": 0.40,
                                          "cone_alignment": 0.60},
            "arm_learned_aniso_loss": {"route_acc": 0.97, "recall_at_1": 0.54, "quant_err_l2": 0.13,
                                        "cone_alignment": 0.65, "T_per_cluster_mean": 3.0, "T_per_cluster_std": 0.5},
            "lift_scann_over_iso": -0.02, "lift_learned_over_iso": -0.01, "lift_route_scann_over_iso": 0.11},
    }}] * 3
    v, msg, _ = compute_verdict(mock_geom_no_recall)
    assert v == "HARD_FAIL" and "GEOMETRIC_NO_RECALL" in msg, (
        "HF_GEOMETRIC_NO_RECALL path failed: %s | %s" % (v, msg[:200]))
    print("[selftest] verdict HF_GEOMETRIC_NO_RECALL (MIMO/DG pattern) path PASS", flush=True)

    # HF_DOESNT_HELP
    mock_hf = [{"by_M": {
        "M%d" % min(M_SWEEP): {"arm_knn_baseline": 0.95,
            "arm_isotropic_kmeans": {"route_acc": 0.9, "recall_at_1": 0.95, "quant_err_l2": 0.05, "cone_alignment": 0.5},
            "arm_scann_anisotropic_vq": {"route_acc": 0.9, "recall_at_1": 0.95, "quant_err_l2": 0.05,
                                          "quant_err_aniso": 0.05, "quant_err_aniso_reduction_vs_iso": 0.0,
                                          "cone_alignment": 0.5},
            "arm_learned_aniso_loss": {"route_acc": 0.9, "recall_at_1": 0.95, "quant_err_l2": 0.05,
                                        "cone_alignment": 0.5, "T_per_cluster_mean": 2.0, "T_per_cluster_std": 0.1},
            "lift_scann_over_iso": 0.0, "lift_learned_over_iso": 0.0, "lift_route_scann_over_iso": 0.0},
        "M%d" % max(M_SWEEP): {"arm_knn_baseline": 0.90,
            "arm_isotropic_kmeans": {"route_acc": 0.85, "recall_at_1": 0.55, "quant_err_l2": 0.10, "cone_alignment": 0.40},
            "arm_scann_anisotropic_vq": {"route_acc": 0.86, "recall_at_1": 0.56, "quant_err_l2": 0.10,
                                          "quant_err_aniso": 0.05, "quant_err_aniso_reduction_vs_iso": 0.05,
                                          "cone_alignment": 0.41},
            "arm_learned_aniso_loss": {"route_acc": 0.87, "recall_at_1": 0.56, "quant_err_l2": 0.10,
                                        "cone_alignment": 0.42, "T_per_cluster_mean": 2.0, "T_per_cluster_std": 0.2},
            "lift_scann_over_iso": 0.01, "lift_learned_over_iso": 0.01, "lift_route_scann_over_iso": 0.01},
    }}] * 3
    v, msg, _ = compute_verdict(mock_hf)
    assert v == "HARD_FAIL" and "DOESNT_HELP" in msg, "HF_DOESNT_HELP path failed: %s | %s" % (v, msg[:200])
    print("[selftest] verdict HF_DOESNT_HELP path PASS", flush=True)

    # MIDDLE_BAND path
    mock_mb = [{"by_M": {
        "M%d" % min(M_SWEEP): {"arm_knn_baseline": 0.95,
            "arm_isotropic_kmeans": {"route_acc": 0.9, "recall_at_1": 0.95, "quant_err_l2": 0.05, "cone_alignment": 0.5},
            "arm_scann_anisotropic_vq": {"route_acc": 0.9, "recall_at_1": 0.95, "quant_err_l2": 0.05,
                                          "quant_err_aniso": 0.05, "quant_err_aniso_reduction_vs_iso": 0.05,
                                          "cone_alignment": 0.5},
            "arm_learned_aniso_loss": {"route_acc": 0.9, "recall_at_1": 0.95, "quant_err_l2": 0.05,
                                        "cone_alignment": 0.5, "T_per_cluster_mean": 2.0, "T_per_cluster_std": 0.1},
            "lift_scann_over_iso": 0.0, "lift_learned_over_iso": 0.0, "lift_route_scann_over_iso": 0.0},
        "M%d" % max(M_SWEEP): {"arm_knn_baseline": 0.90,
            "arm_isotropic_kmeans": {"route_acc": 0.85, "recall_at_1": 0.55, "quant_err_l2": 0.10, "cone_alignment": 0.40},
            "arm_scann_anisotropic_vq": {"route_acc": 0.88, "recall_at_1": 0.59, "quant_err_l2": 0.10,
                                          "quant_err_aniso": 0.05, "quant_err_aniso_reduction_vs_iso": 0.08,
                                          "cone_alignment": 0.45},
            "arm_learned_aniso_loss": {"route_acc": 0.89, "recall_at_1": 0.60, "quant_err_l2": 0.10,
                                        "cone_alignment": 0.46, "T_per_cluster_mean": 2.2, "T_per_cluster_std": 0.3},
            "lift_scann_over_iso": 0.04, "lift_learned_over_iso": 0.05, "lift_route_scann_over_iso": 0.03},
    }}] * 3
    v, msg, _ = compute_verdict(mock_mb)
    assert v == "MIDDLE_BAND" and "MIDDLE_BAND_SCANN" in msg, "MIDDLE_BAND path failed: %s | %s" % (v, msg[:200])
    print("[selftest] verdict MIDDLE_BAND path PASS", flush=True)

    print("[selftest] PASS: iso_kmeans + scann_aniso_vq + learned_aniso + route_rerank + "
          "cone_alignment + verdict_paths(HP/HF_KNN/HF_GEOM/HF_DONTHELP/MB) ALL", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)

    print("[config] %s mode=%s | %s" % (ANCHOR_NAME, RUN_MODE, CONFIG_VERSION), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM,
               "schema": "scann-aniso-vq-v1", "seeds": SEEDS, "M": M_SWEEP}
    t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))

    units = list(aggregate_partials(
        out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg
    ).values())

    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "headline": msg,
        "run_mode": RUN_MODE,
        "model": ENCODER,
        "proj_dim": PROJ_DIM,
        "M_SWEEP": M_SWEEP,
        "n_seeds": len(units),
        "seeds": [int(s.replace("s", "")) for s in [u.get("seed_key", "s%d" % u.get("seed", 0)) for u in units]] if units else SEEDS,
        "window_tokens": WINDOW_TOKENS,
        "cue_shift": CUE_SHIFT,
        "detail": detail,
        "metrics_source": "measured_cpu_scann_anisotropic_vq_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "config_version": CONFIG_VERSION,
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
