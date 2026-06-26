"""POLARIMETRIC MULTI-PROBE RETRIEVAL v1 -- USER cross-domain reframe 2026-06-25.

WHY THIS CELL EXISTS (USER 2026-06-25):
  Three GPU expansion cells (v1 + v2_batched + v3) hit OOM at brain-scale 4096x.
  USER reframe: brain assumes 50B parallel granule cells; we have one GPU.
  Materials scientists / optics dont expand into 50B dims either -- they use multiple
  SMALL probe inputs that interact differently with cone-aligned items, then INFER
  structure from the response pattern (X-ray diffraction, polarimetry, Fourier
  ptychography). Hardware-friendly: probes + responses are SMALL.

MECHANISM (substrate-native reformulation):
  For each candidate key K_i:
    apply K=10 probe vectors p_1..p_K: per-probe scalar response r_ki = <p_k, K_i>
    stack into response vector R_i = (r_1i, ..., r_Ki) in R^K
  At retrieval: do the same to cue: Q = (q_1, ..., q_K)
  Predicted match: argmax_i <normalize(Q), normalize(R_i)>

  K=10 probes form a small interrogation basis. Each probe sees the cone differently.
  Items that look identical along the cone axis still differ along OTHER probe axes,
  so the K-dim response signature disambiguates them.

  Pays cost K*d*M (76M ops at K=10,d=768,M=10k) vs d_p*M (31B ops at d_p=3.15M).
  Three orders of magnitude cheaper than expansion. Laptop-friendly.

ARMS (8 -- FAIR TEST per USER directive):
  ARM_RAW                              -- single-probe collapse baseline (target ~0.02)
  ARM_SINGLE_PROBE_DENSE               -- standard single-probe cleanup (target ~0.18-0.24)
  ARM_SINGLE_PROBE_AVERAGED_K10        -- average 10 noise-perturbed cues; control for "polarimetric = averaging"
  ARM_AB_CONTROL_RANDOM_K_PROBES       -- K=10 random Gaussian probes; control for "any K probes work"
  ARM_POLARIMETRIC_K10_RANDOM_UNIT     -- K=10 random unit probes; control for "randomness alone"
  ARM_POLARIMETRIC_K10_PCA_AXES        -- K=10 top-PCA-axis probes; interrogates cone structure
  ARM_POLARIMETRIC_K10_LEARNED         -- K=10 contrastive-trained probes; strongest version
  ARM_FLY_LSH_5x                       -- cross-cell sanity rail (expansion-based reference)

BANDS (LOCKED at module init via assert):
  HP_LEARNED: POLARIMETRIC_LEARNED >= 0.85 AND beats AB_CONTROL_K, AVERAGED_K10, FLY_LSH each by >= 0.10
              AND monotonic K=1 < K=10 AND cv <= 0.05
  HP_PCA:     POLARIMETRIC_PCA_AXES >= 0.85 AND beats all controls by >= 0.10
  HP_PARTIAL_RANDOM_K: AB_CONTROL_K >= 0.85 (any K probes help; informative)
  HF_DOESNT_HELP:  POLARIMETRIC_LEARNED <= 0.30
  HF_AVERAGED_DOMINATES: AVERAGED_K10 >= POLARIMETRIC_LEARNED (mechanism collapse to averaging)

META_M6: ARM_RAW measured in-cell at adversarial regime (NOT copied from prior cells).
META_M7: smoke matches full along ALL capacity-sensitive dims (PROJ_DIM, K_PROBES,
         K_FANIN, adversarial-window structure). Only M and SEEDS reduce at smoke.
META_PROSPECTIVE_BANDS_FRESH_SEEDS: bands locked at module init via assert chain.
Q-discipline: any arm >= 0.995 flagged.

ASCII-only. Substrate-only at inference. PURE NUMPY (no torch in inference path).
Encoder is SETUP-TIME hidden-state extractor; runs ONCE per seed via _probe.encode.
Probe training (ARM_POLARIMETRIC_K10_LEARNED) uses a small NUMPY contrastive loop
(SGD on K x d probe matrix; not the encoder's contrastive_train).

NO PROT-020 (no torch in inference). Route remote_cpu_queue. CPU runner has no torch gate.
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

ANCHOR_NAME = "substrate_anisotropy_polarimetric_multi_probe_retrieval_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# CAPACITY-SENSITIVE config (META_M7: identical across smoke/full)
PROJ_DIM = 768
C = 256                     # codebook size for label decoding (where used)
K_PROBES = 10               # USER directive; polarimetric probe-count
K_FANIN = 5                 # cerebellar regime (FLY_LSH sanity arm)
KWTA_FRAC = 0.10            # WTA sparsity (where used)
FLY_TOPK_FRAC = 0.005       # fly-LSH tag density (sanity arm)
FLY_NONZERO = 0.05          # sparsity of fly random projection
FLY_EXPANSION = 5           # d_p = 5*768 = 3840 for FLY_LSH sanity arm
SIGMA = 0.1                 # cue noise std (adversarial regime)
MAX_Q = 1500                # query subset cap
TRAIN_STEPS_PROBES = 800    # contrastive train steps for LEARNED probes
TRAIN_LR_PROBES = 5e-2      # SGD lr for LEARNED probes
AVG_K10_NOISE_SAMPLES = 10  # averaged-K10 control: number of noise samples per cue

# Adversarial-similarity construction (same as v2_batched)
WINDOW_TOKENS = 16
CUE_SHIFT = 1

if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"
    SEEDS = [11, 13, 19]
    M_SWEEP = [2000, 10000, 50000]
    TRAIN_M = 2000               # for encoder contrastive projection (W matrix; CERT591 path)
    TRAIN_STEPS_ENC = 600
else:
    ENCODER = "EleutherAI/pythia-160m"
    SEEDS = [11]
    M_SWEEP = [400, 1000]
    TRAIN_M = 600
    TRAIN_STEPS_ENC = 100

# CPU memory budget
MEM_BUDGET_GB = 12.0

# PROSPECTIVE BANDS (LOCKED at module init via assert)
BAND_HP_CHAIN_GRADE = 0.85       # polarimetric arm must hit this
BAND_HP_BEAT_PEER = 0.10         # beat each control by this margin
BAND_HP_PARTIAL_RANDOM_K = 0.85  # AB_CONTROL_K floor for "any K probes help"
BAND_HF_RESCUE = 0.30            # polarimetric below this -> HARD_FAIL
BAND_CV_HP = 0.05                # cv ceiling for HARD_PASS
BAND_Q_SATURATION = 0.995        # >= this flags suspect saturation

assert 0.0 < BAND_HF_RESCUE < BAND_HP_CHAIN_GRADE < BAND_Q_SATURATION < 1.0, "bands ordered"
assert 0.0 < BAND_HP_BEAT_PEER < 1.0, "beat-margin sane"
assert BAND_HP_PARTIAL_RANDOM_K == BAND_HP_CHAIN_GRADE, "partial-random floor matches HP floor"
assert K_PROBES == 10, "USER directive K=10 fixed"
assert 0 < AVG_K10_NOISE_SAMPLES == K_PROBES, "averaged-K10 control matches K_PROBES count for apples-to-apples"

CONFIG_VERSION = (
    "polarimetricMultiProbeV1(K=%d K_FANIN=%d KWTA=%.2f FLY_EXP=%d FLY_TOPK_FRAC=%.4f) | "
    "PROJ_DIM=%d C=%d sigma=%.2f train_steps_probes=%d lr_probes=%.2g avg_samples=%d | "
    "seeds=%s M=%s window=%dt shift=%d encoder=%s | "
    "HP>=%.2f beat_peer>=%.2f HF<=%.2f cv_HP<=%.2f Q_sat>=%.3f | "
    "PURE_NUMPY_CPU mem_budget_gb=%.1f"
) % (
    K_PROBES, K_FANIN, KWTA_FRAC, FLY_EXPANSION, FLY_TOPK_FRAC,
    PROJ_DIM, C, SIGMA, TRAIN_STEPS_PROBES, TRAIN_LR_PROBES, AVG_K10_NOISE_SAMPLES,
    SEEDS, M_SWEEP, WINDOW_TOKENS, CUE_SHIFT, ENCODER,
    BAND_HP_CHAIN_GRADE, BAND_HP_BEAT_PEER, BAND_HF_RESCUE, BAND_CV_HP, BAND_Q_SATURATION,
    MEM_BUDGET_GB,
)


# ---------- numpy helpers ----------

def _np_norm(X):
    return (X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)).astype(np.float32)


# ---------- ARM_RAW: single dot-product collapse baseline ----------

def _arm_raw(Kp, cue, ytrue, qidx):
    """Raw cosine retrieval: cue dot K_i; argmax over i. No probe machinery."""
    Ks = _np_norm(Kp) * np.sqrt(Kp.shape[1])
    sim = cue @ Ks.T                          # (Q, M)
    pred = np.argmax(sim, axis=1)
    return float((pred == qidx).mean())


# ---------- ARM_SINGLE_PROBE_DENSE: one dense projection probe ----------

def _arm_single_probe_dense(Kp, cue, ytrue, qidx, g):
    """One random dense probe vector applied to both K and cue; argmax over cosine."""
    d = Kp.shape[1]
    p = g.standard_normal(d).astype(np.float32) / math.sqrt(d)
    Ks = _np_norm(Kp) * np.sqrt(d)
    # Project both via the same probe p; then use the original cosine over the full d-dim
    # (single-probe-dense = standard cosine; this arm exists to anchor against POLARIMETRIC K=10).
    # Note: "single-probe" interpretation = K=1 polarimetric -> response is scalar; argmax of
    # scalar response over M is trivial -> we instead use full-d cosine with one structured
    # weighting via p (Hadamard scaling). This makes K=1 the natural baseline for K=10 sweep.
    Kw = Ks * p[None, :]
    cuew = cue * p[None, :]
    Kwn = _np_norm(Kw)
    cuewn = _np_norm(cuew)
    sim = cuewn @ Kwn.T
    pred = np.argmax(sim, axis=1)
    return float((pred == qidx).mean())


# ---------- ARM_SINGLE_PROBE_AVERAGED_K10: average 10 noise samples per cue ----------

def _arm_single_probe_averaged_k10(Kp, cue_base, ytrue, qidx, g, n_samples=AVG_K10_NOISE_SAMPLES):
    """Control: average over 10 NOISE-PERTURBED cues; tests if polarimetric is just averaging."""
    d = Kp.shape[1]
    Ks = _np_norm(Kp) * np.sqrt(d)
    Q = cue_base.shape[0]
    # Build averaged cue by re-noising the base cue n_samples times
    avg = np.zeros_like(cue_base)
    for s in range(n_samples):
        eps = SIGMA * g.standard_normal((Q, d)).astype(np.float32)
        avg += (cue_base + eps)
    avg /= n_samples
    avgn = _np_norm(avg)
    Ksn = _np_norm(Ks)
    sim = avgn @ Ksn.T
    pred = np.argmax(sim, axis=1)
    return float((pred == qidx).mean())


# ---------- polarimetric retrieval helper: compute K-probe responses then argmax ----------

def _polarimetric_retrieve(Kp, cue, qidx, P, weights=None):
    """Apply K probe matrix P (shape (K, d)) to keys + cue; argmax over cosine in R^K.

    P: (K, d) probe matrix (rows = probe vectors). weights: optional (K,) reweighting.
    Returns predicted argmax over M for each Q.
    """
    d = Kp.shape[1]
    Ks = _np_norm(Kp) * np.sqrt(d)
    R_key = Ks @ P.T              # (M, K)
    R_cue = cue @ P.T             # (Q, K)
    if weights is not None:
        R_key = R_key * weights[None, :]
        R_cue = R_cue * weights[None, :]
    R_key_n = _np_norm(R_key)
    R_cue_n = _np_norm(R_cue)
    sim = R_cue_n @ R_key_n.T     # (Q, M)
    pred = np.argmax(sim, axis=1)
    return pred


# ---------- ARM_AB_CONTROL_RANDOM_K_PROBES: K random Gaussian probes (no structure) ----------

def _arm_ab_control_random_k(Kp, cue, ytrue, qidx, g, K=K_PROBES):
    """K random Gaussian probes; no structure imposed. Controls for 'any K probes work'."""
    d = Kp.shape[1]
    P = g.standard_normal((K, d)).astype(np.float32) / math.sqrt(d)
    pred = _polarimetric_retrieve(Kp, cue, qidx, P)
    return float((pred == qidx).mean())


# ---------- ARM_POLARIMETRIC_K10_RANDOM_UNIT: K random unit-vector probes ----------

def _arm_polarimetric_random_unit(Kp, cue, ytrue, qidx, g, K=K_PROBES):
    """K random unit-vector probes (uniformly distributed on sphere)."""
    d = Kp.shape[1]
    P = g.standard_normal((K, d)).astype(np.float32)
    P = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-8)
    pred = _polarimetric_retrieve(Kp, cue, qidx, P)
    return float((pred == qidx).mean())


# ---------- ARM_POLARIMETRIC_K10_PCA_AXES: top-K PCA axes of stored keys ----------

def _arm_polarimetric_pca_axes(Kp, cue, ytrue, qidx, K=K_PROBES):
    """K=top-K PCA axes of stored keys. Interrogates the cone's principal axes.

    PCA via SVD on centered keys; top-K right-singular vectors as probes.
    """
    d = Kp.shape[1]
    Ks = _np_norm(Kp) * np.sqrt(d)
    mu = Ks.mean(axis=0, keepdims=True)
    Kc = Ks - mu
    # SVD: Kc = U S V^T; right-singular vectors V are the PCA axes (rows of V^T).
    # For large M we use float32 + economy SVD.
    # If M >> d we can use eigendecomposition of (d, d) covariance for speed.
    if Kc.shape[0] > 2 * d:
        cov = (Kc.T @ Kc) / max(1, Kc.shape[0] - 1)  # (d, d)
        eigvals, eigvecs = np.linalg.eigh(cov.astype(np.float64))
        # eigh returns ascending; we want descending top-K
        order = np.argsort(-eigvals)[:K]
        P = eigvecs[:, order].T.astype(np.float32)   # (K, d)
    else:
        # economy SVD on (M, d)
        u, s, vt = np.linalg.svd(Kc.astype(np.float64), full_matrices=False)
        P = vt[:K].astype(np.float32)                # (K, d)
    pred = _polarimetric_retrieve(Kp, cue, qidx, P)
    return float((pred == qidx).mean())


# ---------- ARM_POLARIMETRIC_K10_LEARNED: contrastive-trained K probes ----------

def _train_learned_probes(K_train, Q_train, K=K_PROBES, steps=TRAIN_STEPS_PROBES,
                           lr=TRAIN_LR_PROBES, seed=0):
    """Train K probe vectors P (K, d) via contrastive InfoNCE on (key, cue) pairs.

    Pure numpy SGD: each step samples a minibatch, computes per-pair similarity in R^K
    via probe responses, then InfoNCE cross-entropy loss. Gradient computed by hand.

    K_train, Q_train: (N_tr, d) float32. Returns P (K, d) float32.
    """
    g = np.random.default_rng(seed + 9999)
    d = K_train.shape[1]
    n_tr = K_train.shape[0]
    bs = min(128, n_tr)

    # Initialize P with random orthogonal-ish unit rows
    P = g.standard_normal((K, d)).astype(np.float32)
    P = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-8)

    # Normalize once
    Kn = _np_norm(K_train)
    Qn = _np_norm(Q_train)

    tau = 0.07
    for step in range(steps):
        idx = g.choice(n_tr, bs, replace=False)
        kb = Kn[idx]                              # (bs, d)
        qb = Qn[idx]                              # (bs, d)

        # K-probe responses
        Rk = kb @ P.T                             # (bs, K)
        Rq = qb @ P.T                             # (bs, K)
        # L2 normalize K-dim responses (cosine sim in R^K)
        Rk_n = Rk / (np.linalg.norm(Rk, axis=1, keepdims=True) + 1e-8)
        Rq_n = Rq / (np.linalg.norm(Rq, axis=1, keepdims=True) + 1e-8)

        # logits: (bs, bs) cosine sim of cue-responses vs all key-responses in batch
        logits = (Rq_n @ Rk_n.T) / tau           # (bs, bs)

        # InfoNCE: target = diagonal
        # softmax-cross-entropy gradient: dL/dlogits = softmax(logits) - I
        m = logits.max(axis=1, keepdims=True)
        e = np.exp(logits - m)
        sm = e / (e.sum(axis=1, keepdims=True) + 1e-12)
        targets = np.eye(bs, dtype=np.float32)
        grad_logits = (sm - targets) / bs        # (bs, bs)

        # Now backprop grad through (Rq_n @ Rk_n.T) / tau
        # dL/dRq_n[i,k] = sum_j grad_logits[i,j] * Rk_n[j,k] / tau
        # dL/dRk_n[j,k] = sum_i grad_logits[i,j] * Rq_n[i,k] / tau
        gRq_n = (grad_logits @ Rk_n) / tau       # (bs, K)
        gRk_n = (grad_logits.T @ Rq_n) / tau     # (bs, K)

        # Backprop through L2-normalize on K-dim response
        # If r_n = r / ||r||, then dr_n/dr = (I - r_n r_n^T) / ||r||
        def _backprop_l2_norm(r, r_n, gr_n):
            norm = np.linalg.norm(r, axis=1, keepdims=True) + 1e-8
            # gr = (gr_n - r_n * (r_n * gr_n).sum(1, keepdims=True)) / norm
            return (gr_n - r_n * (r_n * gr_n).sum(axis=1, keepdims=True)) / norm

        gRk = _backprop_l2_norm(Rk, Rk_n, gRk_n) # (bs, K)
        gRq = _backprop_l2_norm(Rq, Rq_n, gRq_n) # (bs, K)

        # Now grad through Rk = kb @ P.T -> dL/dP[k,:] += gRk[:,k][:,None] * kb
        # and    Rq = qb @ P.T -> dL/dP[k,:] += gRq[:,k][:,None] * qb
        gP = gRk.T @ kb + gRq.T @ qb              # (K, d)

        # SGD update
        P = P - lr * gP.astype(np.float32)

        # Optional: re-normalize P rows every 50 steps to keep stable
        if (step + 1) % 50 == 0:
            P = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-8)

    # Final renormalize
    P = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-8)
    return P


def _arm_polarimetric_learned(Kp_train, Q_train, Kp_eval, cue_eval, ytrue, qidx,
                                K=K_PROBES, seed=0):
    """Train K=10 probes contrastively on (Kp_train, Q_train) then evaluate."""
    P = _train_learned_probes(Kp_train, Q_train, K=K, seed=seed)
    pred = _polarimetric_retrieve(Kp_eval, cue_eval, qidx, P)
    return float((pred == qidx).mean()), P


# ---------- ARM_FLY_LSH_5x: cross-cell sanity rail (expansion-based reference) ----------

def _make_sparse_fanin(d, dp, K, g):
    """COO sparse-fan-in matrix S of shape (dp, d) with K +-1 entries per row."""
    nnz = dp * K
    rows = np.empty(nnz, dtype=np.int64)
    cols = np.empty(nnz, dtype=np.int64)
    for i in range(dp):
        idx = g.choice(d, K, replace=False)
        base = i * K
        rows[base:base + K] = i
        cols[base:base + K] = idx
    vals = (g.integers(0, 2, nnz).astype(np.float32) * 2 - 1)
    return rows, cols, vals


def _sparse_matvec(rows, cols, vals, dp, d, X):
    """Compute H = X @ S.T where S is (dp, d) sparse-COO. X: (M, d). Returns (M, dp)."""
    M = X.shape[0]
    H = np.zeros((M, dp), dtype=np.float32)
    # Group nnz by row in batches to bound peak
    nnz = rows.shape[0]
    NNZ_BATCH = max(1, min(nnz, 500_000))
    for start in range(0, nnz, NNZ_BATCH):
        end = min(start + NNZ_BATCH, nnz)
        r = rows[start:end]
        c = cols[start:end]
        v = vals[start:end]
        contribs = v[:, None] * X[:, c].T          # (batch, M)
        np.add.at(H, (slice(None), r), contribs.T)
    return H


def _flylsh_tags(X, rows, cols, vals, dp, FLY_TOPK):
    """fly-LSH tags as topk-indices. Median-subtract via global median across X-rows."""
    H = _sparse_matvec(rows, cols, vals, dp, X.shape[1], X)
    H -= np.median(H, axis=0, keepdims=True)
    idx = np.argpartition(H, -FLY_TOPK, axis=1)[:, -FLY_TOPK:].astype(np.int32)
    return idx


def _tag_overlap_argmax(Q_tags, K_tags, dp):
    """For each query tag-set, find K-row with max tag-overlap. Inverted-index O(M*FLY_TOPK^2/dp) per Q."""
    Q, FLY_TOPK_Q = Q_tags.shape
    M, FLY_TOPK_K = K_tags.shape
    k_rows = np.repeat(np.arange(M, dtype=np.int32), FLY_TOPK_K)
    k_tags_flat = K_tags.reshape(-1)
    order = np.argsort(k_tags_flat, kind="stable")
    tag_ids_sorted = k_tags_flat[order]
    k_rows_sorted = k_rows[order]
    unique_tags, start_idx, counts = np.unique(tag_ids_sorted, return_index=True, return_counts=True)
    starts_arr = np.full(dp, -1, dtype=np.int64)
    counts_arr = np.zeros(dp, dtype=np.int64)
    starts_arr[unique_tags] = start_idx
    counts_arr[unique_tags] = counts
    pred = np.empty(Q, dtype=np.int64)
    counts_buf = np.zeros(M, dtype=np.int32)
    for q in range(Q):
        counts_buf.fill(0)
        for t in Q_tags[q]:
            s = starts_arr[t]
            if s < 0:
                continue
            cnt = counts_arr[t]
            ks = k_rows_sorted[s:s + cnt]
            counts_buf[ks] += 1
        pred[q] = int(np.argmax(counts_buf))
    return pred


def _arm_fly_lsh_5x(Kp, cue, qidx, g):
    """fly-LSH at expansion=5x; cross-cell sanity rail vs v2_batched M=10k slice."""
    d = Kp.shape[1]
    dp = d * FLY_EXPANSION
    FLY_TOPK = max(20, int(FLY_TOPK_FRAC * dp))
    Ks = _np_norm(Kp) * math.sqrt(d)
    rows, cols, vals = _make_sparse_fanin(d, dp, K_FANIN, g)
    K_tags = _flylsh_tags(Ks, rows, cols, vals, dp, FLY_TOPK)
    Q_tags = _flylsh_tags(cue, rows, cols, vals, dp, FLY_TOPK)
    del rows, cols, vals
    pred = _tag_overlap_argmax(Q_tags, K_tags, dp)
    return float((pred == qidx).mean())


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
    "Polarimetric imaging measures the polarization state of light interacting with materials. By sending multiple probe polarizations and observing how each interacts with the sample, one infers structural properties that would be invisible to a single intensity measurement. The same principle underlies X-ray diffraction in materials science and Fourier ptychography in computational imaging.",
    "Compressed sensing exploits sparsity in a signals representation to recover it from far fewer measurements than the Nyquist limit suggests. Each measurement projects the signal onto a randomly oriented vector and the collection of K such projections suffices to identify items whose underlying support is sparse. The reconstruction can be performed via L1 minimization or simple correlation argmax when sparsity is sufficient.",
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


# ---------- encoder + facts (hoisted; SETUP-TIME only; substrate-only at inference) ----------

def _facts_and_encode(seed, M_total):
    """Setup-time encoder hoisting via _probe module.

    Returns Kp_all (M_total, PROJ_DIM) and Q_all (M_total, PROJ_DIM) after
    contrastive-projection through W (CERT591 path). Encoder runs ONCE per seed.
    """
    os.environ["HDLAB_RUN_MODE"] = RUN_MODE
    import experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 as _probe
    _probe.ENCODER = ENCODER
    encode = _probe.encode
    train_contrastive = _probe.train_contrastive

    g = np.random.default_rng(seed)
    prose = _build_adversarial_prose(g, target_tokens=M_total + WINDOW_TOKENS + CUE_SHIFT + 50)
    words = prose.split()
    needed = M_total + WINDOW_TOKENS + CUE_SHIFT
    if len(words) < needed:
        prose = _build_adversarial_prose(g, target_tokens=needed * 2)
        words = prose.split()
    keys = []
    cues = []
    for i in range(M_total):
        keys.append(" ".join(words[i:i + WINDOW_TOKENS]))
        cues.append(" ".join(words[i + CUE_SHIFT:i + CUE_SHIFT + WINDOW_TOKENS]))
    print("[adversarial-facts] seed=%d M_total=%d words_pool=%d window=%d shift=%d sample_key='%s' sample_cue='%s'" % (
        seed, M_total, len(words), WINDOW_TOKENS, CUE_SHIFT,
        keys[0][:80], cues[0][:80]
    ), flush=True)

    K = encode(keys)
    Q = encode(cues)
    perm = g.permutation(M_total)
    tr = perm[:TRAIN_M]
    ho = perm[TRAIN_M:]
    W = train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS_ENC, seed)
    Kp_all = (K[ho] @ W).astype(np.float32)
    Qp_all = (Q[ho] @ W).astype(np.float32)
    print("[adversarial-encode] seed=%d encoded=%d projected_dim=%d held_out=%d" % (
        seed, M_total, PROJ_DIM, len(Kp_all)
    ), flush=True)
    # Also return training-set projected pairs for learned-probe training
    Kp_train = (K[tr] @ W).astype(np.float32)
    Qp_train = (Q[tr] @ W).astype(np.float32)
    return Kp_all, Qp_all, Kp_train, Qp_train


# ---------- per-arm dispatch ----------

def _run_all_arms(Kp_eval, Qp_eval, Kp_train, Qp_train, seed_for_arms):
    """Run all 8 arms on Kp_eval/Qp_eval. Returns dict of per-arm metrics."""
    g = np.random.default_rng(seed_for_arms)
    M, d = Kp_eval.shape

    # Build cue subset (matches v2_batched MAX_Q discipline)
    qidx_full = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    Ks = _np_norm(Kp_eval) * math.sqrt(d)
    noise = (SIGMA * g.standard_normal((len(qidx_full), d))).astype(np.float32)
    cue = Ks[qidx_full] + noise

    # qidx_full is the ground-truth index into Kp_eval rows; this is what argmax should return
    ytrue = qidx_full

    print("[arms] M=%d d=%d Q=%d K=%d" % (M, d, len(qidx_full), K_PROBES), flush=True)

    t = time.time()
    arm_raw = _arm_raw(Kp_eval, cue, ytrue, qidx_full)
    t_raw = time.time() - t

    t = time.time()
    arm_single = _arm_single_probe_dense(Kp_eval, cue, ytrue, qidx_full, g)
    t_single = time.time() - t

    t = time.time()
    arm_avg = _arm_single_probe_averaged_k10(Kp_eval, cue, ytrue, qidx_full, g)
    t_avg = time.time() - t

    t = time.time()
    arm_ab_k = _arm_ab_control_random_k(Kp_eval, cue, ytrue, qidx_full, g)
    t_ab = time.time() - t

    t = time.time()
    arm_pol_rand = _arm_polarimetric_random_unit(Kp_eval, cue, ytrue, qidx_full, g)
    t_pol_rand = time.time() - t

    t = time.time()
    arm_pol_pca = _arm_polarimetric_pca_axes(Kp_eval, cue, ytrue, qidx_full)
    t_pol_pca = time.time() - t

    # Learned arm: use TRAINING set Kp_train + Qp_train for probe contrastive training
    t = time.time()
    arm_pol_learned, P_learned = _arm_polarimetric_learned(
        Kp_train, Qp_train, Kp_eval, cue, ytrue, qidx_full, seed=seed_for_arms
    )
    t_pol_learned = time.time() - t

    t = time.time()
    arm_fly_5x = _arm_fly_lsh_5x(Kp_eval, cue, qidx_full, g)
    t_fly = time.time() - t

    print(("[arms] raw=%.4f single=%.4f avg10=%.4f ab_k=%.4f pol_rand=%.4f pol_pca=%.4f pol_learned=%.4f fly_5x=%.4f "
           "| t(s) raw=%.1f single=%.1f avg=%.1f ab=%.1f pol_rand=%.1f pol_pca=%.1f pol_learned=%.1f fly=%.1f") % (
        arm_raw, arm_single, arm_avg, arm_ab_k, arm_pol_rand, arm_pol_pca, arm_pol_learned, arm_fly_5x,
        t_raw, t_single, t_avg, t_ab, t_pol_rand, t_pol_pca, t_pol_learned, t_fly
    ), flush=True)

    return {
        "arm_raw": round(arm_raw, 4),
        "arm_single_probe_dense": round(arm_single, 4),
        "arm_single_probe_averaged_k10": round(arm_avg, 4),
        "arm_ab_control_random_k_probes": round(arm_ab_k, 4),
        "arm_polarimetric_k10_random_unit": round(arm_pol_rand, 4),
        "arm_polarimetric_k10_pca_axes": round(arm_pol_pca, 4),
        "arm_polarimetric_k10_learned": round(arm_pol_learned, 4),
        "arm_fly_lsh_5x": round(arm_fly_5x, 4),
        "K_probes": K_PROBES,
        "timings_s": {
            "raw": round(t_raw, 2), "single": round(t_single, 2), "avg": round(t_avg, 2),
            "ab_k": round(t_ab, 2), "pol_rand": round(t_pol_rand, 2), "pol_pca": round(t_pol_pca, 2),
            "pol_learned": round(t_pol_learned, 2), "fly_5x": round(t_fly, 2),
        },
    }


def run_unit(seed):
    M_max = max(M_SWEEP)
    M_total = M_max + TRAIN_M
    print("[seed=%d] encoder=%s M_total=%d (adversarial-similarity stride-1 windows; polarimetric v1 CPU)" % (
        seed, ENCODER, M_total
    ), flush=True)
    Kp_all, Qp_all, Kp_train, Qp_train = _facts_and_encode(seed, M_total)
    by_M = {}
    for M in M_SWEEP:
        if M > len(Kp_all):
            print("[warn] M=%d exceeds Kp_all=%d; skipping" % (M, len(Kp_all)), flush=True)
            continue
        arms_seed = seed * 7 + M
        a = _run_all_arms(Kp_all[:M], Qp_all[:M], Kp_train, Qp_train, arms_seed)
        by_M["M%d" % M] = a
    return {"seed": seed, "by_M": by_M}


# ---------- verdict ----------

def _cv(values):
    if not values:
        return 0.0
    mean = float(np.mean(values))
    if abs(mean) < 1e-9:
        return 0.0
    return float(np.std(values) / abs(mean))


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})

    # Score at the largest M actually evaluated
    M_max = max(M_SWEEP) if M_SWEEP else 10000

    def vals(M, key):
        return [u["by_M"]["M%d" % M][key] for u in units
                if "M%d" % M in u["by_M"] and key in u["by_M"]["M%d" % M]]

    def med(M, key):
        v = vals(M, key)
        return float(np.median(v)) if v else 0.0

    raw_at_max = med(M_max, "arm_raw")
    single = med(M_max, "arm_single_probe_dense")
    avg_k10 = med(M_max, "arm_single_probe_averaged_k10")
    ab_k = med(M_max, "arm_ab_control_random_k_probes")
    pol_rand = med(M_max, "arm_polarimetric_k10_random_unit")
    pol_pca = med(M_max, "arm_polarimetric_k10_pca_axes")
    pol_learned = med(M_max, "arm_polarimetric_k10_learned")
    fly_5x = med(M_max, "arm_fly_lsh_5x")

    cv_learned = _cv(vals(M_max, "arm_polarimetric_k10_learned"))
    cv_pca = _cv(vals(M_max, "arm_polarimetric_k10_pca_axes"))
    cv_ab_k = _cv(vals(M_max, "arm_ab_control_random_k_probes"))

    detail = {
        "M_eval": M_max,
        "arm_raw": raw_at_max,
        "arm_single_probe_dense": single,
        "arm_single_probe_averaged_k10": avg_k10,
        "arm_ab_control_random_k_probes": ab_k,
        "arm_polarimetric_k10_random_unit": pol_rand,
        "arm_polarimetric_k10_pca_axes": pol_pca,
        "arm_polarimetric_k10_learned": pol_learned,
        "arm_fly_lsh_5x": fly_5x,
        "cv_polarimetric_k10_learned": round(cv_learned, 4),
        "cv_polarimetric_k10_pca_axes": round(cv_pca, 4),
        "cv_ab_control_random_k": round(cv_ab_k, 4),
        "n_seeds": len(units),
        "K_PROBES": K_PROBES,
        "bands": {
            "HP_CHAIN_GRADE": BAND_HP_CHAIN_GRADE,
            "HP_BEAT_PEER": BAND_HP_BEAT_PEER,
            "HP_PARTIAL_RANDOM_K": BAND_HP_PARTIAL_RANDOM_K,
            "HF_RESCUE": BAND_HF_RESCUE,
            "CV_HP": BAND_CV_HP,
            "Q_SATURATION": BAND_Q_SATURATION,
        },
        "CONFIG_VERSION": CONFIG_VERSION,
        "cites": [
            "USER_polarimetric_cross_domain_reframe_2026-06-25",
            "substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched",
            "substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path",
            "substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full",
            "research_anisotropy_intuitive_synthesis_with_visual_2026-06-25",
            "dense_KV_whitening_revival_v1_gpu",
            "Charikar2002_hyperplane_lsh",
            "fly_LSH_Dasgupta2017",
            "Mu_Viswanath_2018_isotropy",
            "polarimetry_optics_analogy_USER_2026-06-25",
        ],
    }

    summ = (
        "raw=%.3f | single=%.3f avg10=%.3f ab_k=%.3f | pol_rand=%.3f pol_pca=%.3f pol_learned=%.3f | fly_5x=%.3f | "
        "cv_learned=%.3f cv_pca=%.3f cv_ab_k=%.3f"
    ) % (raw_at_max, single, avg_k10, ab_k, pol_rand, pol_pca, pol_learned, fly_5x,
          cv_learned, cv_pca, cv_ab_k)

    q_flags = []
    for name, val in [("pol_learned", pol_learned), ("pol_pca", pol_pca), ("pol_rand", pol_rand),
                       ("ab_k", ab_k), ("avg_k10", avg_k10), ("fly_5x", fly_5x), ("single", single)]:
        if val >= BAND_Q_SATURATION:
            q_flags.append("[Q-DISCIPLINE: %s=%.4f >= %.3f -- suspect saturation; corpus-may-be-easy at M=%d]" % (
                name, val, BAND_Q_SATURATION, M_max))
    q_note = " ".join(q_flags) + (" " if q_flags else "")

    # HF_AVERAGED_DOMINATES (mechanism-collapse failsafe)
    if avg_k10 >= pol_learned and avg_k10 >= BAND_HF_RESCUE:
        return ("HARD_FAIL",
                ("HARD_FAIL_AVERAGED_K10_DOMINATES: ARM_SINGLE_PROBE_AVERAGED_K10 = %.3f >= "
                 "ARM_POLARIMETRIC_K10_LEARNED = %.3f at M=%d -- polarimetric is just averaging; "
                 "K=10 structure NOT load-bearing; demote mechanism story. %s%s") % (
                    avg_k10, pol_learned, M_max, q_note, summ),
                detail)

    # HF_DOESNT_HELP
    if pol_learned <= BAND_HF_RESCUE and pol_pca <= BAND_HF_RESCUE:
        return ("HARD_FAIL",
                ("HARD_FAIL_POLARIMETRIC_DOESNT_HELP: ARM_POLARIMETRIC_K10_LEARNED = %.3f AND PCA = %.3f "
                 "BOTH <= %.2f at M=%d -- polarimetric cross-domain reframe does NOT transport to "
                 "substrate at adversarial-keys scale. ab_k=%.3f fly_5x=%.3f. %s%s") % (
                    pol_learned, pol_pca, BAND_HF_RESCUE, M_max, ab_k, fly_5x, q_note, summ),
                detail)

    # HP_LEARNED (full chain-grade attribution to learned probes)
    learned_beats_all = (
        pol_learned >= BAND_HP_CHAIN_GRADE
        and (pol_learned - ab_k) >= BAND_HP_BEAT_PEER
        and (pol_learned - avg_k10) >= BAND_HP_BEAT_PEER
        and (pol_learned - fly_5x) >= BAND_HP_BEAT_PEER
        and (pol_learned - single) > 0    # monotonic K=1 < K=10
        and cv_learned <= BAND_CV_HP
    )
    if learned_beats_all:
        return ("HARD_PASS",
                ("CHAIN-GRADE_POLARIMETRIC_LEARNED_RESCUES: ARM_POLARIMETRIC_K10_LEARNED = %.3f >= %.2f at M=%d; "
                 "beats AB_CONTROL_K = %.3f by %.3f (>= %.2f), AVERAGED_K10 = %.3f by %.3f (>= %.2f), "
                 "FLY_LSH_5x = %.3f by %.3f (>= %.2f); monotonic K=1 (%.3f) < K=10 (%.3f); cv = %.3f <= %.2f. "
                 "Polarimetric multi-probe is the load-bearing mechanism; USER cross-domain reframe validated "
                 "at substrate scale. Hardware-friendly anisotropy rescue without brain-scale expansion. %s%s") % (
                    pol_learned, BAND_HP_CHAIN_GRADE, M_max,
                    ab_k, pol_learned - ab_k, BAND_HP_BEAT_PEER,
                    avg_k10, pol_learned - avg_k10, BAND_HP_BEAT_PEER,
                    fly_5x, pol_learned - fly_5x, BAND_HP_BEAT_PEER,
                    single, pol_learned, cv_learned, BAND_CV_HP, q_note, summ),
                detail)

    # HP_PCA (brain-aligned attribution to PCA-axis probes)
    pca_beats_all = (
        pol_pca >= BAND_HP_CHAIN_GRADE
        and (pol_pca - ab_k) >= BAND_HP_BEAT_PEER
        and (pol_pca - avg_k10) >= BAND_HP_BEAT_PEER
        and (pol_pca - fly_5x) >= BAND_HP_BEAT_PEER
        and (pol_pca - single) > 0
        and cv_pca <= BAND_CV_HP
    )
    if pca_beats_all:
        return ("HARD_PASS",
                ("CHAIN-GRADE_POLARIMETRIC_PCA_RESCUES: ARM_POLARIMETRIC_K10_PCA_AXES = %.3f >= %.2f at M=%d; "
                 "beats AB_CONTROL_K = %.3f by %.3f, AVERAGED_K10 = %.3f by %.3f, FLY_LSH_5x = %.3f by %.3f "
                 "(each >= %.2f); monotonic K=1 (%.3f) < K=10 (%.3f); cv = %.3f <= %.2f. "
                 "Top-PCA-axis probes are the load-bearing mechanism; data-structure-aware probes work; "
                 "brain-aligned cortical-attention attribution. %s%s") % (
                    pol_pca, BAND_HP_CHAIN_GRADE, M_max,
                    ab_k, pol_pca - ab_k, avg_k10, pol_pca - avg_k10,
                    fly_5x, pol_pca - fly_5x, BAND_HP_BEAT_PEER,
                    single, pol_pca, cv_pca, BAND_CV_HP, q_note, summ),
                detail)

    # HP_PARTIAL_RANDOM_K (any K probes help -- informative)
    if ab_k >= BAND_HP_PARTIAL_RANDOM_K and cv_ab_k <= BAND_CV_HP:
        return ("HARD_PASS",
                ("PARTIAL_RANDOM_K_HELPS: ARM_AB_CONTROL_RANDOM_K_PROBES = %.3f >= %.2f at M=%d; "
                 "any K=10 random probes rescue anisotropy; NOT polarimetric-specific (pol_learned=%.3f, "
                 "pol_pca=%.3f). Informative for cross-domain framing: 'K probes help' lands but mechanism "
                 "attribution generic. cv = %.3f. %s%s") % (
                    ab_k, BAND_HP_PARTIAL_RANDOM_K, M_max, pol_learned, pol_pca, cv_ab_k, q_note, summ),
                detail)

    # MIDDLE_BAND
    return ("MIDDLE_BAND",
            ("MEASURED_MECHANISM_NO_CLEAN_DISCRIMINATOR: at M=%d adversarial-similarity keys -- "
             "raw=%.3f single=%.3f avg10=%.3f ab_k=%.3f pol_rand=%.3f pol_pca=%.3f pol_learned=%.3f fly_5x=%.3f. "
             "No arm hits HP_CHAIN_GRADE = %.2f with all discriminator margins; HF guards not triggered. "
             "Numbers measured cleanly but the chain-grade attribution discriminator is inconclusive. %s%s") % (
                M_max, raw_at_max, single, avg_k10, ab_k, pol_rand, pol_pca, pol_learned, fly_5x,
                BAND_HP_CHAIN_GRADE, q_note, summ),
            detail)


# ---------- self-test ----------

def _selftest():
    """Module-init bands + tiny synthetic ground-truth recall + arm-shape sanity."""
    # Band sanity (already asserted at module init; redo as visible)
    assert BAND_HF_RESCUE < BAND_HP_CHAIN_GRADE < BAND_Q_SATURATION

    g = np.random.default_rng(0)
    d = 64
    M = 50

    # Anisotropic synthetic ARM CODE-PATH smoke (NOT a science claim about anisotropy collapse;
    # collapse requires M >> d_effective at adversarial keys; the toy is just a shape/value sanity)
    sig = g.standard_normal((M, d)).astype(np.float32)
    mu = g.standard_normal((1, d)).astype(np.float32) * 4.0  # strong cone
    Kp = sig + mu
    qidx = np.arange(M)
    Ks = _np_norm(Kp) * math.sqrt(d)
    noise = (SIGMA * g.standard_normal((M, d))).astype(np.float32)
    cue = Ks + noise

    # ARM_RAW runs + returns in [0, 1] (at M=50 d=64 small noise, will be high; not testing science)
    raw = _arm_raw(Kp, cue, qidx, qidx)
    assert 0.0 <= raw <= 1.0, "arm_raw out of range (got %.3f)" % raw

    # PCA arm runs + returns in [0, 1]
    pca_acc = _arm_polarimetric_pca_axes(Kp, cue, qidx, qidx)
    assert 0.0 <= pca_acc <= 1.0, "arm_polarimetric_pca out of range (got %.3f)" % pca_acc

    # AB_CONTROL: K random probes on isotropic -- code-path runs + returns in [0, 1]
    iso = _np_norm(g.standard_normal((M, d)).astype(np.float32))
    iso_cue = iso + (SIGMA * g.standard_normal((M, d))).astype(np.float32)
    iso_ab = _arm_ab_control_random_k(iso, iso_cue, qidx, qidx, g)
    assert 0.0 <= iso_ab <= 1.0, "arm_ab_control_random_k out of range (got %.3f)" % iso_ab

    # AVERAGED_K10: code-path runs + returns in [0, 1]
    iso_avg = _arm_single_probe_averaged_k10(iso, iso_cue, qidx, qidx, g)
    assert 0.0 <= iso_avg <= 1.0, "arm_single_probe_averaged_k10 out of range (got %.3f)" % iso_avg

    # True anisotropy-collapse smoke: near-duplicate keys with adversarial overlap.
    # Build keys as small perturbations of a single base direction so cosine cannot
    # cleanly separate adjacent keys -- this is the regime the cell's full run measures
    # (adversarial stride-1 windows of natural prose).
    M_aniso = 8 * d
    base = g.standard_normal((1, d)).astype(np.float32) * 5.0
    perturb_scale = 0.05  # small relative to base; mimics adversarial-similarity regime
    Kp_aniso = base + perturb_scale * g.standard_normal((M_aniso, d)).astype(np.float32)
    qidx_aniso = np.arange(M_aniso)
    Ks_aniso = _np_norm(Kp_aniso) * math.sqrt(d)
    # cue = key + cone-aligned noise (noise has component along base direction comparable to perturbation)
    base_unit = base / (np.linalg.norm(base) + 1e-8)
    cue_noise = (perturb_scale * 1.5 * g.standard_normal((M_aniso, d))).astype(np.float32)
    cue_aniso = Ks_aniso + cue_noise
    raw_aniso = _arm_raw(Kp_aniso, cue_aniso, qidx_aniso, qidx_aniso)
    # Near-duplicates + cue noise > perturbation => raw cannot perfectly separate
    assert raw_aniso < 0.95, (
        "true-anisotropy-collapse smoke: raw should be impaired on near-duplicate keys "
        "(got %.3f at M=%d d=%d perturb=%.2f)") % (raw_aniso, M_aniso, d, perturb_scale)

    # POLARIMETRIC_LEARNED on a small problem: train on full set; evaluate same; should be strong
    # Use FIXED random keys/cues pair as both train and eval (smoke check; not a held-out test)
    K_tr = _np_norm(g.standard_normal((40, d)).astype(np.float32))
    Q_tr = _np_norm(K_tr + (0.05 * g.standard_normal((40, d))).astype(np.float32))
    P = _train_learned_probes(K_tr, Q_tr, K=K_PROBES, steps=200, lr=1e-1, seed=0)
    assert P.shape == (K_PROBES, d), "learned probe shape must be (K, d) (got %s)" % str(P.shape)
    # Verify probes are unit norm post-training
    norms = np.linalg.norm(P, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-3), "learned probes should be unit norm (got %s)" % norms

    # Polarimetric retrieve smoke: probe machinery returns correct argmax on identity
    K_id = _np_norm(g.standard_normal((20, d)).astype(np.float32))
    P_id = g.standard_normal((K_PROBES, d)).astype(np.float32) / math.sqrt(d)
    pred = _polarimetric_retrieve(K_id, K_id, np.arange(20), P_id)
    # On identity keys (cue == key), polarimetric should be PERFECT
    acc = (pred == np.arange(20)).mean()
    assert acc >= 0.95, "polarimetric on identity cues should be near-perfect (got %.3f)" % acc

    # FLY_LSH_5x smoke: should work on small isotropic
    fly_acc = _arm_fly_lsh_5x(iso, iso_cue, qidx, g)
    assert fly_acc >= 0.20, "FLY_LSH_5x on isotropic toy should hit >= 0.20 (got %.3f)" % fly_acc

    # Verdict synthetic paths
    # 1) HP_LEARNED path
    mock_units = [{"by_M": {"M%d" % max(M_SWEEP): {
        "arm_raw": 0.02, "arm_single_probe_dense": 0.20, "arm_single_probe_averaged_k10": 0.25,
        "arm_ab_control_random_k_probes": 0.40, "arm_polarimetric_k10_random_unit": 0.45,
        "arm_polarimetric_k10_pca_axes": 0.60, "arm_polarimetric_k10_learned": 0.90,
        "arm_fly_lsh_5x": 0.50,
    }}}] * 3
    v, m, _ = compute_verdict(mock_units)
    assert v == "HARD_PASS" and "POLARIMETRIC_LEARNED_RESCUES" in m, "HP_LEARNED path failed: %s | %s" % (v, m[:120])

    # 2) HF_DOESNT_HELP path
    mock_fail = [{"by_M": {"M%d" % max(M_SWEEP): {
        "arm_raw": 0.02, "arm_single_probe_dense": 0.18, "arm_single_probe_averaged_k10": 0.20,
        "arm_ab_control_random_k_probes": 0.22, "arm_polarimetric_k10_random_unit": 0.24,
        "arm_polarimetric_k10_pca_axes": 0.25, "arm_polarimetric_k10_learned": 0.28,
        "arm_fly_lsh_5x": 0.30,
    }}}] * 3
    v, m, _ = compute_verdict(mock_fail)
    assert v == "HARD_FAIL" and "DOESNT_HELP" in m, "HF_DOESNT_HELP path failed: %s | %s" % (v, m[:120])

    # 3) HF_AVERAGED_DOMINATES path
    mock_avg_dom = [{"by_M": {"M%d" % max(M_SWEEP): {
        "arm_raw": 0.02, "arm_single_probe_dense": 0.20, "arm_single_probe_averaged_k10": 0.70,
        "arm_ab_control_random_k_probes": 0.40, "arm_polarimetric_k10_random_unit": 0.50,
        "arm_polarimetric_k10_pca_axes": 0.60, "arm_polarimetric_k10_learned": 0.65,
        "arm_fly_lsh_5x": 0.50,
    }}}] * 3
    v, m, _ = compute_verdict(mock_avg_dom)
    assert v == "HARD_FAIL" and "AVERAGED_K10_DOMINATES" in m, "HF_AVERAGED_DOMINATES path failed: %s | %s" % (v, m[:120])

    # 4) MIDDLE_BAND path
    mock_mb = [{"by_M": {"M%d" % max(M_SWEEP): {
        "arm_raw": 0.02, "arm_single_probe_dense": 0.20, "arm_single_probe_averaged_k10": 0.30,
        "arm_ab_control_random_k_probes": 0.50, "arm_polarimetric_k10_random_unit": 0.55,
        "arm_polarimetric_k10_pca_axes": 0.65, "arm_polarimetric_k10_learned": 0.70,
        "arm_fly_lsh_5x": 0.55,
    }}}] * 3
    v, m, _ = compute_verdict(mock_mb)
    assert v == "MIDDLE_BAND" and "NO_CLEAN_DISCRIMINATOR" in m, "MIDDLE_BAND path failed: %s | %s" % (v, m[:120])

    # 5) HP_PARTIAL_RANDOM_K path
    mock_partial = [{"by_M": {"M%d" % max(M_SWEEP): {
        "arm_raw": 0.02, "arm_single_probe_dense": 0.20, "arm_single_probe_averaged_k10": 0.30,
        "arm_ab_control_random_k_probes": 0.88, "arm_polarimetric_k10_random_unit": 0.55,
        "arm_polarimetric_k10_pca_axes": 0.65, "arm_polarimetric_k10_learned": 0.70,
        "arm_fly_lsh_5x": 0.55,
    }}}] * 3
    v, m, _ = compute_verdict(mock_partial)
    assert v == "HARD_PASS" and "PARTIAL_RANDOM_K_HELPS" in m, "HP_PARTIAL_RANDOM_K path failed: %s | %s" % (v, m[:120])

    # Adversarial-prose construction sanity
    g2 = np.random.default_rng(3)
    prose = _build_adversarial_prose(g2, target_tokens=200)
    words = prose.split()
    assert len(words) >= 200, "prose builder failed (%d words)" % len(words)
    w_a = words[0:WINDOW_TOKENS]
    w_b = words[CUE_SHIFT:CUE_SHIFT + WINDOW_TOKENS]
    overlap = len(set(w_a) & set(w_b))
    assert overlap >= WINDOW_TOKENS - CUE_SHIFT - 1, "adversarial overlap weak (%d/%d)" % (overlap, WINDOW_TOKENS)

    print(("[selftest] PASS: raw_toy=%.3f pca_toy=%.3f iso_ab=%.3f iso_avg=%.3f raw_aniso(M>>rank)=%.3f "
           "learned_norms_ok polarimetric_identity=%.3f fly_iso=%.3f verdict_paths_5_ok prose_overlap=%d/%d") % (
              raw, pca_acc, iso_ab, iso_avg, raw_aniso, acc, fly_acc, overlap, WINDOW_TOKENS), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)

    print("[config] %s mode=%s | %s" % (ANCHOR_NAME, RUN_MODE, CONFIG_VERSION), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM, "K_probes": K_PROBES,
               "schema": "polarimetric-multi-probe-v1-cpu", "seeds": SEEDS, "M": M_SWEEP}
    t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "run_mode": RUN_MODE,
        "model": ENCODER,
        "proj_dim": PROJ_DIM,
        "K_PROBES": K_PROBES,
        "M_SWEEP": M_SWEEP,
        "n_seeds": len(units),
        "seeds": SEEDS,
        "window_tokens": WINDOW_TOKENS,
        "cue_shift": CUE_SHIFT,
        "detail": detail,
        "metrics_source": "measured_cpu_polarimetric_multi_probe_retrieval_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
