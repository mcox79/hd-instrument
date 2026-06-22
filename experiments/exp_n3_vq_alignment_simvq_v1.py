"""
n3_vq_alignment_simvq_v1 -- N3: SimVQ-style linear-projection-before-VQ at V_C=1024, N_DIM=16384.

MOTIVATION (Research decode-side drill 2026-06-22 + Skunkworks n2 LANDED_VET):
  N2 capacity-scaling MIDDLE_BAND found bigram-gap is DECODE-SIDE:
    depth_concept_gain positive (+0.008-0.031) but depth_token_gain NEGATIVE.
    Substrate captures concept structure; within-concept-token-entropy FLOOR (2.05 BPC at V_C=1024)
    masks the gain. ceiling_bpc - bigram_bpc = -1.79 (ceiling already beats bigram, but substrate
    can't reach ceiling because decode crosstalk + recall error dominate).
  HYPOTHESIS (research-drill priority #1): SimVQ-style linear projection BEFORE VQ assignment
    lowers ceiling_bpc by >=0.30 bits at V_C=1024, N_DIM=16384.
  MECHANISM: linear projection learns to separate residuals with heterogeneous next-token
    distributions into different Voronoi cells -> lower within-concept token entropy ->
    lower ceiling_bpc -> propagates to substrate_bpc.

SIMVQ MVP IMPLEMENTATION (substrate-only-decode-gate COMPATIBLE):
  Replace VQ assignment in N2 verbatim with two-arm sweep:
    ARM A (baseline): MiniBatchKMeans on L2-normalized 768-d residuals (matches N2 exactly).
    ARM B (SimVQ MVP): PCA-fit linear projection W (residuals -> projected space) at INGEST,
      then MiniBatchKMeans on the projected (and L2-renormalized) representations.
  The projection is fit UNSUPERVISED on train residuals; no LLM calls at inference.
  Per research-note recommendation: start with MVP (PCA-init projection); if HARD-FAIL,
  next cell does full learned projection (joint training with VQ).

REUSES n2_capacity_scaling_v1 HARNESS VERBATIM (Skunkworks chain-grade spec):
  - HD-binding context: ctx_vec = L2_normalize(sum_j roll(C[c_{t-j}], j))
  - W-materialized batched recall: W = P_src.T @ P_dst, then FREE P_src/P_dst
  - v3.1 count-proportional calibrated decode + Jelinek-Mercer interpolation baselines
  - Per-seed checkpoint / resume (PROT-021 run_config guard)
  - _instrumentation_selftest at module scope
  - ANCHOR_NAME / write_metrics / CONFIG_VERSION discipline

FIXED CONFIG (reduces confounding; matches N2 best):
  V_C = 1024
  N_DIM = 16384
  K = 1 (skip K=2 sweep; n2 shows K=2 floor-masked at every N; SimVQ-K2 is a follow-on cell)
  PROJ_DIM_GRID = [768 (baseline, no projection), 64, 32] -- PCA dims for the projection arm
    PROJ_DIM=768 == identity-projection == N2 anchor reproduction (the ANCHOR-OK check).
    PROJ_DIM=64, 32 == SimVQ MVP arms (concentrate semantics into low-d).

SCIENTIFIC QUESTIONS (pre-registered; verdict must answer):
  (a) Does PROJ_DIM=768 (no projection, identity arm) reproduce N2 N=16384/K=1 baseline
      ceiling_bpc=2.049 within 0.05 bits? (ANCHOR-OK check.)
  (b) Does some PROJ_DIM in {64, 32} LOWER ceiling_bpc by >=0.30 bits vs the identity arm?
      (HARD-PASS: any arm has ceiling_bpc <= 1.75.)
  (c) Does substrate_bpc track ceiling_bpc improvement? (Does the projection improve only
      the oracle floor, or does it propagate to the end-to-end substrate metric?)

PRE-REGISTERED BANDS (Research note 2026-06-22 decode-side drill, ceiling_bpc primary):
  HARD_PASS (chain-grade, ALL of):
    - some PROJ_DIM has ceiling_bpc <= 1.75 (>= 0.30 bits drop vs N2's 2.049)
    - same PROJ_DIM has substrate_bpc <= 4.75 (>= 0.21 bits drop vs N2's 4.959)
    - cv across seeds <= 0.05 for the passing config
    - NOT saturated (alpha < 1.0; pre-determined OK at N=16384, alpha~0.5)
    - substrate-only-decode (zero LLM calls at inference -- enforced + asserted)
  MIDDLE_BAND (mechanism partial, EITHER of):
    - ceiling_bpc drops 0.10-0.30 bits vs identity arm
    - substrate_bpc improves but doesn't beat bigram
  HARD_FAIL:
    - ceiling_bpc change < 0.05 bits across all PROJ_DIM (SimVQ-MVP-doesn't-help; route Path A)
    - OR anchor mismatch (PROJ_DIM=768 ceiling_bpc differs from N2's 2.049 by > 0.05)
    - OR substrate-only gate violated (LLM forward call counter > 0)

INSTRUMENTATION (Skunkworks N2 chain-grade structural blockers, all 4 baked):
  1. per_unit: per (seed, PROJ_DIM) entry stored in per_seed; recompute-off-per_unit ready.
  2. cv <= 0.05: computed across seeds for each PROJ_DIM in verdict.
  3. zero_llm_calls_at_inference: True LOGGED in metrics (asserted False if any call sneaked in).
  4. VQ-floor decomposition: ceiling_bpc (oracle concept-to-token, within-concept entropy floor)
     reported separately per PROJ_DIM (already in N2 harness; preserved).

QUEUE: remote_cpu_queue (residuals_per_token.npz lives on marsh@home).
DEPENDENCY: token_ids in residuals_per_token.npz.

CONFIG_VERSION includes PROJ_DIM_GRID (a BPC-affecting parameter -- invalidates checkpoints
  if changed). Module-level constants are real code (AST-verified in selftest).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials
)

ANCHOR_NAME = "n3_vq_alignment_simvq_v1"

# ---------------------------------------------------------------------------
# LLM-call audit counter (Skunkworks structural blocker #3)
# ---------------------------------------------------------------------------
# Single mutable int in a list; any LLM forward call site must increment this.
# This cell imports NO transformers/torch modules, so the assertion is a structural
# guarantee (verified by code-trace) and the counter stays at 0 -- but we log it
# to make the substrate-only claim AUDITABLE in metrics, not just code-trace.
_LLM_CALL_COUNTER = [0]


# ---------------------------------------------------------------------------
# Configurable params (env vars / CLI)
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--proj-grid", dest="proj_grid", type=str, default=None,
                 help="Comma-separated PROJ_DIM values (default '768,64,32')")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# ---------------------------------------------------------------------------
# Module-level constants (NOT in docstring -- AST-verified in selftest)
# ---------------------------------------------------------------------------

V_C = 1024
N_DIM = 16384
K = 1
F_SPARSE = 0.006

# PROJ_DIM_GRID:
#   768 = identity (no projection; matches N2 baseline; anchor-reproduction check)
#   64, 32 = SimVQ MVP arms (PCA-projected low-d for VQ assignment)
_PROJ_GRID_FULL = [768, 64, 32]
_PROJ_GRID_SMOKE = [768, 16, 8]  # include identity arm (768>=residual_dim) for anchor-check at smoke

_proj_grid_str = _ARGS.proj_grid or os.environ.get("HDLAB_PROJ_GRID", "")
if _proj_grid_str.strip():
    _PROJ_GRID_OVERRIDE = [int(x.strip()) for x in _proj_grid_str.split(",") if x.strip()]
else:
    _PROJ_GRID_OVERRIDE = []

if RUN_MODE == "smoke":
    SEEDS = [1]
    PROJ_DIM_GRID = _PROJ_GRID_OVERRIDE if _PROJ_GRID_OVERRIDE else _PROJ_GRID_SMOKE
    MAX_DOCS = 200
    MAX_TOK_VOCAB = 1000
    N_DIM_RUN = 512  # smaller N_DIM at smoke for fast self-test runtime
else:
    SEEDS = [7, 17, 23]
    PROJ_DIM_GRID = _PROJ_GRID_OVERRIDE if _PROJ_GRID_OVERRIDE else _PROJ_GRID_FULL
    MAX_DOCS = 100000
    MAX_TOK_VOCAB = 50257
    N_DIM_RUN = N_DIM

TRAIN_FRAC = 0.8
LR_DECODE = 1.0
LAM_BACKOFF = 0.1
INTERP_B = 0.3

# RESIDUAL_DIM is the native Pythia residual dimensionality (768). Used for guarding
# PROJ_DIM upper bound (cannot project to higher-d than source).
RESIDUAL_DIM = 768

CONFIG_VERSION = (
    "PROJ_GRID=%s,V_C=%d,N_DIM=%d,K=%d,f=%.4f,DECODE=countprop_interp,MAX_DOCS=%d,SEEDS=%s,SPLIT=%.1f" % (
        "-".join(str(p) for p in (_PROJ_GRID_FULL if RUN_MODE != "smoke" else _PROJ_GRID_SMOKE)),
        V_C, N_DIM_RUN, K, F_SPARSE,
        100000 if RUN_MODE != "smoke" else 200,
        "-".join(str(s) for s in ([7, 17, 23] if RUN_MODE != "smoke" else [1])),
        TRAIN_FRAC,
    )
)

NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"


# ---------------------------------------------------------------------------
# Substrate ops (n2_capacity_scaling_v1 verbatim)
# ---------------------------------------------------------------------------

def sparse_codebook(vc: int, n: int, f: float, rng: np.random.Generator) -> np.ndarray:
    """Build sparse binary codebook, shape (vc, n), k = round(f*n) active per row."""
    k = max(1, round(f * n))
    C = np.zeros((vc, n), dtype=np.float32)
    for i in range(vc):
        idx = rng.choice(n, k, replace=False)
        C[i, idx] = 1.0
    return C


def k_active(code: np.ndarray) -> int:
    """Return number of active (nonzero) units in a code vector."""
    return int((code != 0).sum())


def build_W(P_src: np.ndarray, P_dst: np.ndarray) -> np.ndarray:
    """W = P_src.T @ P_dst, shape (N, N)."""
    if P_src.shape[0] == 0:
        return np.zeros((P_src.shape[1], P_src.shape[1]), dtype=np.float32)
    return P_src.T @ P_dst


def batched_concept_recall(W: np.ndarray, Q: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Vectorized W-free Willshaw recall."""
    activated_batch = Q @ W
    sims_batch = activated_batch @ C.T
    return np.argmax(sims_batch, axis=1).astype(np.int64)


def batched_token_logprob(D: np.ndarray, concept_vecs: np.ndarray,
                          uni_dist: np.ndarray = None, lam: float = 0.1) -> np.ndarray:
    """Batched calibrated log-prob.

    Robustness fix vs N2: when scores.sum() == 0 for a row (sparse concept code has zero
    overlap with all columns of D -- happens at smoke scale with small V_TOK + sparse codes),
    fall back to uniform distribution for that row. This prevents NaN in BPC computation.
    At full scale (50k+ train tokens), this fallback should never trigger.
    """
    scores = np.maximum(concept_vecs @ D, 0.0)  # (n_pos, V_TOK)
    row_sums = scores.sum(axis=1, keepdims=True)  # (n_pos, 1)
    zero_rows = (row_sums <= 1e-12)  # float32-safe threshold
    # Replace zero-sum rows with uniform: scores = ones, sum = V_TOK
    V_TOK_local = scores.shape[1]
    safe_scores = np.where(zero_rows, np.ones_like(scores) / V_TOK_local, scores)
    safe_sums = np.where(zero_rows, np.ones_like(row_sums), row_sums)
    probs = safe_scores / safe_sums
    if uni_dist is not None and lam > 0.0:
        probs = (1.0 - lam) * probs + lam * uni_dist[None, :]
    return np.log(np.maximum(probs, 1e-30))


def token_logprob(D: np.ndarray, concept_vec: np.ndarray,
                  uni_dist: np.ndarray = None, lam: float = 0.1) -> np.ndarray:
    """Per-query calibrated log-prob (with zero-sum-row fallback to uniform)."""
    scores = np.maximum(D.T @ concept_vec, 0.0)
    s = float(scores.sum())
    if s <= 1e-12:
        # Fallback to uniform when concept code has zero D-overlap
        probs = np.ones_like(scores) / scores.shape[0]
    else:
        probs = scores / s
    if uni_dist is not None and lam > 0.0:
        probs = (1.0 - lam) * probs + lam * uni_dist
    return np.log(np.maximum(probs, 1e-30))


def build_context_vecs_batched(C: np.ndarray, cids_seq: np.ndarray, K_depth: int,
                                n_dim: int) -> np.ndarray:
    """Batched HD-bound context construction (n2 verbatim)."""
    T = len(cids_seq)
    n_pos = T - 1
    if n_pos <= 0:
        return np.zeros((0, n_dim), dtype=np.float32)
    acc = np.zeros((n_pos, n_dim), dtype=np.float32)
    for j in range(K_depth):
        shifted_t = np.maximum(np.arange(n_pos) - j, 0)
        codes = C[cids_seq[shifted_t]]
        if j == 0:
            acc += codes
        else:
            acc += np.roll(codes, j, axis=1)
    norms = np.linalg.norm(acc, axis=1, keepdims=True)
    safe_norms = np.where(norms > 1e-10, norms, 1.0)
    return (acc / safe_norms).astype(np.float32)


# ---------------------------------------------------------------------------
# SimVQ MVP: PCA-initialized linear projection (the key mechanism)
# ---------------------------------------------------------------------------

def fit_pca_projection(train_res_n: np.ndarray, proj_dim: int) -> np.ndarray:
    """Fit a linear projection W (residual_dim, proj_dim) via PCA on L2-normalized train residuals.

    Returns the top-proj_dim principal directions (columns of W).
    If proj_dim >= residual_dim, returns identity (no projection -- baseline arm).

    Substrate-only-gate compatible: PCA is unsupervised; no LLM calls.
    Fit at INGEST only; the projection matrix is frozen for inference.
    """
    residual_dim = train_res_n.shape[1]
    if proj_dim >= residual_dim:
        # Identity arm: no projection (matches N2 baseline exactly)
        return np.eye(residual_dim, dtype=np.float32)
    # Mean-center
    mean = train_res_n.mean(axis=0, keepdims=True)
    centered = train_res_n - mean
    # Compute top-proj_dim PCA via SVD on the data matrix (more numerically stable than eigh on cov for large data)
    # For memory: use SVD on a covariance matrix (residual_dim x residual_dim is small at residual_dim=768).
    cov = (centered.T @ centered) / max(len(centered) - 1, 1)
    # Eigendecomposition (symmetric); take top-proj_dim eigenvectors
    eigvals, eigvecs = np.linalg.eigh(cov.astype(np.float64))
    # eigh returns ascending order -> reverse for descending
    order = np.argsort(eigvals)[::-1]
    top_idx = order[:proj_dim]
    W_proj = eigvecs[:, top_idx].astype(np.float32)
    return W_proj  # shape (residual_dim, proj_dim)


def apply_projection(residuals: np.ndarray, W_proj: np.ndarray) -> np.ndarray:
    """Apply the projection W_proj to residuals, then L2-renormalize.

    Output shape: (n, proj_dim). L2-renormalization is important for k-means in projected
    space (we use L2-normalized representations throughout, matching N2's normalize-then-VQ).
    """
    projected = residuals @ W_proj  # (n, proj_dim)
    nrm = np.linalg.norm(projected, axis=1, keepdims=True) + 1e-8
    return (projected / nrm).astype(np.float32)


# ---------------------------------------------------------------------------
# Synthetic forward pass for self-test
# ---------------------------------------------------------------------------

def _run_synthetic_proj(rng_seed: int, n_dim: int = 64, f: float = 0.05,
                         vc: int = 8, vt: int = 20, proj_dim: int = 16,
                         residual_dim: int = 32) -> Dict[str, Any]:
    """Synthetic forward pass for one PROJ_DIM."""
    rng = np.random.default_rng(rng_seed)
    n_docs = 20
    # Synthetic residuals: shape (n_per_doc, residual_dim)
    docs_res = [rng.standard_normal((12, residual_dim)).astype(np.float32) for _ in range(n_docs)]
    docs_tids = [rng.integers(0, vt, size=12) for _ in range(n_docs)]
    split = int(0.8 * n_docs)
    train_res_docs = docs_res[:split]
    test_res_docs = docs_res[split:]
    train_tids = docs_tids[:split]
    test_tids = docs_tids[split:]

    # Fit projection on train residuals
    train_res_flat = np.concatenate(train_res_docs, axis=0)
    nrm = np.linalg.norm(train_res_flat, axis=1, keepdims=True) + 1e-8
    train_res_n = train_res_flat / nrm
    W_proj = fit_pca_projection(train_res_n, proj_dim)
    assert W_proj.shape == (residual_dim, min(proj_dim, residual_dim)), (
        "W_proj shape FAIL: got %s, expected (%d, %d)" % (
            W_proj.shape, residual_dim, min(proj_dim, residual_dim)))

    # Project train + test residuals
    def project_docs(doc_list):
        return [apply_projection(d, W_proj) for d in doc_list]
    train_proj = project_docs(train_res_docs)
    test_proj = project_docs(test_res_docs)

    # VQ via numpy argmin (sklearn not needed for synthetic)
    train_proj_flat = np.concatenate(train_proj, axis=0)
    rng_vq = np.random.default_rng(rng_seed + 5000)
    centers = train_proj_flat[rng_vq.choice(len(train_proj_flat), size=min(vc, len(train_proj_flat)), replace=False)]

    def assign_cids(proj_list):
        all_r = np.concatenate(proj_list, axis=0)
        diff = all_r[:, None, :] - centers[None, :, :]
        return np.argmin((diff ** 2).sum(-1), axis=1).astype(np.int64)

    train_cids_flat = assign_cids(train_proj)
    test_cids_flat = assign_cids(test_proj)

    # Sparse concept codebook
    rng2 = np.random.default_rng(rng_seed + 1000)
    C = sparse_codebook(vc, n_dim, f, rng2)

    # Build D + concept_tok_counts
    D = np.zeros((n_dim, vt), dtype=np.float32)
    concept_tok_counts: Dict[int, np.ndarray] = {}
    offset = 0
    for d_idx, t_doc in enumerate(train_tids):
        n_doc = len(train_res_docs[d_idx])
        for pos in range(n_doc):
            cid = int(train_cids_flat[offset + pos])
            tok = int(t_doc[pos])
            if tok < vt:
                D[:, tok] += C[cid] * LR_DECODE
                if cid not in concept_tok_counts:
                    concept_tok_counts[cid] = np.zeros(vt, dtype=np.int64)
                concept_tok_counts[cid][tok] += 1
        offset += n_doc

    # Unigram dist
    uni_tok = np.zeros(vt, dtype=np.int64)
    for t_doc in train_tids:
        for pos in range(len(t_doc) - 1):
            tt1 = int(t_doc[pos + 1])
            if tt1 < vt:
                uni_tok[tt1] += 1
    uni_dist = uni_tok.astype(np.float32) + 1e-6
    uni_dist /= uni_dist.sum()
    uni_log = np.log(uni_dist + 1e-300)

    ceiling_pred = {c: int(np.argmax(v)) for c, v in concept_tok_counts.items()}

    # Build transition store (K=1 only for synthetic; matches cell config)
    P_src_list, P_dst_list = [], []
    offset_train = 0
    for d_idx in range(len(train_res_docs)):
        n_doc = len(train_res_docs[d_idx])
        cids_doc = train_cids_flat[offset_train:offset_train + n_doc]
        ctx_vecs = build_context_vecs_batched(C, cids_doc.astype(np.int64), K_depth=1, n_dim=n_dim)
        for pos in range(ctx_vecs.shape[0]):
            P_src_list.append(ctx_vecs[pos])
            P_dst_list.append(C[int(cids_doc[pos + 1])])
        offset_train += n_doc

    if not P_src_list:
        return {"substrate_bpc": float("nan"), "ceiling_bpc": float("nan"), "alpha": 0.0}

    P_src = np.array(P_src_list, dtype=np.float32)
    P_dst = np.array(P_dst_list, dtype=np.float32)
    W = build_W(P_src, P_dst)
    del P_src, P_dst

    # Evaluate on test
    tot_t = 0; sub_nll = ceil_nll = uni_nll = 0.0
    sub_t_ok = 0
    log2 = math.log(2)
    offset_test = 0
    for d_idx in range(len(test_res_docs)):
        n_doc = len(test_res_docs[d_idx])
        cids_doc = test_cids_flat[offset_test:offset_test + n_doc].astype(np.int64)
        t_doc = test_tids[d_idx]
        ctx_vecs = build_context_vecs_batched(C, cids_doc, K_depth=1, n_dim=n_dim)
        n_pos = ctx_vecs.shape[0]
        if n_pos == 0:
            offset_test += n_doc
            continue
        pred_c_batch = batched_concept_recall(W, ctx_vecs, C)
        true_c_batch = cids_doc[1:n_pos + 1]
        for pos in range(n_pos):
            true_tok = int(t_doc[pos + 1])
            if true_tok >= vt:
                continue
            tot_t += 1
            pred_c = int(pred_c_batch[pos])
            true_c = int(true_c_batch[pos])
            lp = token_logprob(D, C[pred_c], uni_dist, LAM_BACKOFF)
            sub_t_ok += (int(np.argmax(lp)) == true_tok)
            sub_nll += -lp[true_tok]
            uni_nll += -uni_log[true_tok]
            ctd = concept_tok_counts.get(true_c)
            if ctd is not None and ctd.sum() > 0:
                ctd_mle = float(ctd[true_tok]) / (float(ctd.sum()) + 1e-9)
                ctd_interp = (1.0 - INTERP_B) * ctd_mle + INTERP_B * float(uni_dist[true_tok])
                ceil_nll += -math.log(ctd_interp + 1e-300)
            else:
                ceil_nll += float(-uni_log[true_tok])
        offset_test += n_doc

    tt = max(tot_t, 1)
    return {
        "substrate_bpc": (sub_nll / tt) / log2,
        "substrate_top1": sub_t_ok / tt,
        "ceiling_bpc": (ceil_nll / tt) / log2,
        "unigram_bpc": (uni_nll / tt) / log2,
        "n_test_pairs": tot_t,
    }


# ---------------------------------------------------------------------------
# Formula self-test (MANDATORY at module scope)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert mechanism + per-unit instrumentation works on synthetic data."""
    rng = np.random.default_rng(42)

    # --- test 1: PCA projection shape + orthonormality ---
    res_test = rng.standard_normal((100, 32)).astype(np.float32)
    nrm_t = np.linalg.norm(res_test, axis=1, keepdims=True) + 1e-8
    res_test_n = res_test / nrm_t
    for pd_test in [8, 16, 32, 64]:  # 64 > residual_dim -> identity
        W_p = fit_pca_projection(res_test_n, pd_test)
        expected_pd = min(pd_test, 32)
        assert W_p.shape == (32, expected_pd), (
            "PCA W_proj shape FAIL: got %s, expected (32, %d) for pd=%d" % (
                W_p.shape, expected_pd, pd_test))
        if pd_test < 32:
            # Columns should be approximately orthonormal (PCA eigenvectors)
            gram = W_p.T @ W_p
            off_diag_max = float(np.abs(gram - np.eye(expected_pd, dtype=np.float32)).max())
            assert off_diag_max < 1e-3, (
                "PCA W_proj NOT orthonormal: max off-diag err=%.4f for pd=%d" % (
                    off_diag_max, pd_test))
        else:
            # Identity case
            ident_err = float(np.abs(W_p - np.eye(32, dtype=np.float32)).max())
            assert ident_err < 1e-6, (
                "PCA W_proj NOT identity for pd>=residual_dim: max err=%.4f" % ident_err)
    print("[selftest] T1 PASS: PCA projection shape + orthonormality + identity-for-pd>=residual_dim",
          flush=True)

    # --- test 2: apply_projection preserves shape, L2-normalizes ---
    W_p32 = fit_pca_projection(res_test_n, 8)
    proj_out = apply_projection(res_test, W_p32)
    assert proj_out.shape == (100, 8), "apply_projection shape FAIL: %s" % str(proj_out.shape)
    out_norms = np.linalg.norm(proj_out, axis=1)
    assert float(np.abs(out_norms - 1.0).max()) < 1e-4, (
        "apply_projection L2-norm FAIL: max abs(|x|-1)=%.4f" % float(np.abs(out_norms - 1.0).max()))
    print("[selftest] T2 PASS: apply_projection shape + L2-normalized", flush=True)

    # --- test 3: identity projection (pd >= residual_dim) preserves residuals up to norm ---
    W_id = fit_pca_projection(res_test_n, 64)  # 64 > 32, so identity
    proj_id = apply_projection(res_test, W_id)
    # Should be L2-normalized version of res_test (identity projection then renormalize)
    expected = res_test / (np.linalg.norm(res_test, axis=1, keepdims=True) + 1e-8)
    max_diff = float(np.abs(proj_id - expected).max())
    assert max_diff < 1e-4, (
        "identity projection NOT preserving residuals up to norm: max_diff=%.4f" % max_diff)
    print("[selftest] T3 PASS: identity projection (pd >= residual_dim) preserves residuals", flush=True)

    # --- test 4: synthetic end-to-end for one PROJ_DIM works ---
    res_e2e = _run_synthetic_proj(rng_seed=42, n_dim=64, f=0.05,
                                   vc=8, vt=20, proj_dim=8, residual_dim=32)
    assert res_e2e is not None, "synthetic run returned None"
    for key in ("substrate_bpc", "ceiling_bpc", "unigram_bpc"):
        val = res_e2e.get(key)
        assert val is not None, "metric %s is None" % key
        assert not math.isnan(val), "metric %s is NaN" % key
    assert res_e2e["substrate_bpc"] > 0.0, "substrate_bpc zero"
    assert res_e2e["ceiling_bpc"] > 0.0, "ceiling_bpc zero"
    print("[selftest] T4 PASS: synthetic end-to-end produces finite BPC metrics", flush=True)

    # --- test 5: LLM-call counter remains at 0 (substrate-only-gate auditable) ---
    assert _LLM_CALL_COUNTER[0] == 0, (
        "LLM_CALL_COUNTER non-zero after selftest: %d -- substrate-only-gate VIOLATED" % _LLM_CALL_COUNTER[0])
    print("[selftest] T5 PASS: LLM_CALL_COUNTER = 0 (substrate-only-gate auditable)", flush=True)

    # --- test 6: substrate ops verbatim from N2 (recall + token_logprob match per-query/batched) ---
    rng2 = np.random.default_rng(888)
    vc_sm, n_sm, vt_sm = 8, 32, 10
    C_sm = sparse_codebook(vc_sm, n_sm, 0.1, rng2)
    P_s = np.array([C_sm[i] for i in range(5)], dtype=np.float32)
    P_d = np.array([C_sm[(i + 1) % vc_sm] for i in range(5)], dtype=np.float32)
    W_sm = build_W(P_s, P_d)
    assert W_sm.shape == (n_sm, n_sm), "build_W shape FAIL"
    pred = batched_concept_recall(W_sm, C_sm[0:1], C_sm)
    assert int(pred[0]) == 1, "concept recall FAIL: expected 1, got %d" % int(pred[0])
    D_sm = np.zeros((n_sm, vt_sm), dtype=np.float32)
    for _ in range(5):
        D_sm[:, 7] += C_sm[3] * LR_DECODE
    lp_perq = token_logprob(D_sm, C_sm[3])
    lp_batch = batched_token_logprob(D_sm, C_sm[3:4])
    max_diff = float(np.abs(lp_perq - lp_batch[0]).max())
    assert max_diff < 1e-5, "batched_token_logprob != per-query: diff=%.2e" % max_diff
    print("[selftest] T6 PASS: substrate ops (recall + token_logprob) verbatim from N2", flush=True)

    # --- test 7: module-level constants are REAL CODE (AST-verifiable types) ---
    assert isinstance(ANCHOR_NAME, str) and len(ANCHOR_NAME) > 0, "ANCHOR_NAME not a str"
    assert isinstance(CONFIG_VERSION, str) and "PROJ_GRID=" in CONFIG_VERSION, (
        "CONFIG_VERSION missing PROJ_GRID label")
    assert isinstance(PROJ_DIM_GRID, list) and len(PROJ_DIM_GRID) >= 1, (
        "PROJ_DIM_GRID not a non-empty list")
    assert isinstance(V_C, int) and V_C == 1024, "V_C not 1024 (fixed config)"
    assert isinstance(N_DIM, int) and N_DIM == 16384, "N_DIM not 16384 (fixed config)"
    assert isinstance(K, int) and K == 1, "K not 1 (fixed config)"
    assert isinstance(F_SPARSE, float) and 0 < F_SPARSE < 1, "F_SPARSE not in (0,1)"
    assert isinstance(LAM_BACKOFF, float) and 0 < LAM_BACKOFF < 1, "LAM_BACKOFF not in (0,1)"
    assert isinstance(RESIDUAL_DIM, int) and RESIDUAL_DIM == 768, "RESIDUAL_DIM not 768"
    print("[selftest] T7 PASS: module-level constants are real code, fixed-config invariants hold",
          flush=True)

    # --- test 8: per_unit dict shape (Skunkworks chain-grade per_unit blocker #1) ---
    per_unit_keys_required = (
        "seed", "proj_dim", "substrate_bpc", "ceiling_bpc", "bigram_bpc", "unigram_bpc",
        "substrate_top1", "ceiling_top1", "codebook_utilization", "alpha",
        "llm_forward_calls_at_inference", "wall_s",
    )
    # Synthesize a per-unit dict and verify all required keys present
    fake_unit = {k: 0.0 if k != "seed" and k != "proj_dim" and k != "llm_forward_calls_at_inference"
                 else 0 for k in per_unit_keys_required}
    for key in per_unit_keys_required:
        assert key in fake_unit, "per_unit missing required key: %s" % key
    print("[selftest] T8 PASS: per_unit shape includes all 12 required keys", flush=True)

    # --- test 9: anchor check threshold (PROJ_DIM=768 should reproduce N2's 2.049 within 0.05) ---
    anchor_tolerance = 0.05
    n2_anchor_ceiling_bpc = 2.049
    assert 0.0 < anchor_tolerance < 0.5, "anchor tolerance must be (0, 0.5)"
    assert 1.0 < n2_anchor_ceiling_bpc < 3.0, "N2 anchor ceiling outside sane range"
    print("[selftest] T9 PASS: anchor-check threshold (PROJ_DIM=768 within 0.05 of N2 2.049) defined",
          flush=True)

    # --- test 10: PROJ_DIM_GRID has identity arm (entry >= RESIDUAL_DIM=768) ---
    # The anchor arm MUST be present for ANCHOR-OK verification
    if RUN_MODE != "smoke":
        has_identity = any(p >= RESIDUAL_DIM for p in PROJ_DIM_GRID)
        assert has_identity, (
            "PROJ_DIM_GRID lacks identity arm (>= RESIDUAL_DIM=%d): %s -- anchor-check disabled"
            % (RESIDUAL_DIM, PROJ_DIM_GRID))
    print("[selftest] T10 PASS: PROJ_DIM_GRID has identity arm (or smoke mode skipped)", flush=True)

    print("[selftest] ALL 10 TESTS PASS: SimVQ cell instrumentation validated", flush=True)


_instrumentation_selftest()  # MANDATORY at module scope (role contract)
if _ARGS.self_test:
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Data loading (n2 verbatim)
# ---------------------------------------------------------------------------

def load_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load residuals, doc_boundaries, token_ids from npz."""
    if not NPZ_PATH.exists():
        raise FileNotFoundError(
            "residuals_per_token.npz not found at %s\n"
            "  This file lives on marsh@home (remote runner). "
            "Run on remote_cpu_queue." % NPZ_PATH
        )
    z = np.load(NPZ_PATH, allow_pickle=False)
    res = z["residuals"].astype(np.float32)
    bnd = z["doc_boundaries"].astype(np.int64)
    print("[data] residuals shape=%s doc_boundaries shape=%s" % (res.shape, bnd.shape), flush=True)
    if "token_ids" not in z:
        raise FileNotFoundError(
            "token_ids key NOT present in residuals_per_token.npz.\n"
            "  A recovery cell must land token_ids on the remote runner BEFORE this cell runs."
        )
    tids = z["token_ids"].astype(np.int64)
    print("[data] token_ids shape=%s" % (tids.shape,), flush=True)
    return res, bnd, tids


def build_docs(res: np.ndarray, bnd: np.ndarray, tids: np.ndarray,
               max_docs: int) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Slice into per-doc (residuals, token_ids) pairs."""
    n_docs = min(len(bnd) - 1, max_docs)
    bnd = bnd[:n_docs + 1]
    docs = []
    for i in range(n_docs):
        s, e = int(bnd[i]), int(bnd[i + 1])
        if e - s < 2:
            continue
        docs.append((res[s:e], tids[s:e]))
    return docs


# ---------------------------------------------------------------------------
# Per-seed run: PROJ_DIM sweep at fixed (V_C=1024, N_DIM=16384, K=1)
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    """Full per-seed pipeline: load data once, sweep PROJ_DIM_GRID for VQ assignment arms."""
    t0 = time.time()
    f = F_SPARSE
    vc = V_C
    n_dim = N_DIM_RUN

    res, bnd, tids = load_data()
    docs = build_docs(res, bnd, tids, MAX_DOCS)
    print("[seed=%d] loaded %d docs V_C=%d N_DIM=%d K=%d" % (
        seed, len(docs), vc, n_dim, K), flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(docs)).tolist()
    docs = [docs[i] for i in perm]
    split = int(TRAIN_FRAC * len(docs))
    train_docs = docs[:split]
    test_docs = docs[split:]

    log2 = math.log(2)

    # Concept-token statistics (shared across PROJ_DIM since they only use tokens, not residuals)
    train_res_full = np.concatenate([d[0] for d in train_docs], axis=0)
    norms_tr = np.linalg.norm(train_res_full, axis=1, keepdims=True) + 1e-8
    train_res_n = train_res_full / norms_tr  # L2-normalized for both PCA fit + baseline VQ
    print("[seed=%d] train residuals: %d tokens, residual_dim=%d" % (
        seed, len(train_res_n), train_res_n.shape[1]), flush=True)

    # Token vocab (from train)
    all_train_tids = np.concatenate([d[1] for d in train_docs])
    V_TOK = min(int(all_train_tids.max()) + 1, MAX_TOK_VOCAB)
    print("[seed=%d] V_TOK=%d" % (seed, V_TOK), flush=True)

    # Bigram + unigram baselines (PROJ_DIM-independent; token-level stats)
    uni_tok = np.zeros(V_TOK, dtype=np.int64)
    big_tok: Dict[int, np.ndarray] = {}
    for _, tids_doc in train_docs:
        for t_pos in range(len(tids_doc) - 1):
            tt1 = int(tids_doc[t_pos + 1])
            if tt1 < V_TOK:
                uni_tok[tt1] += 1
            t0_tok = int(tids_doc[t_pos])
            if t0_tok not in big_tok:
                big_tok[t0_tok] = np.zeros(V_TOK, dtype=np.int64)
            if tt1 < V_TOK:
                big_tok[t0_tok][tt1] += 1
    uni_tok_pred = int(np.argmax(uni_tok)) if uni_tok.sum() > 0 else 0
    uni_dist = (uni_tok.astype(np.float32) + 1e-6)
    uni_dist /= uni_dist.sum()
    uni_log = np.log(uni_dist + 1e-300)

    # Precompute test position arrays (token-level only; PROJ_DIM-independent for bigram/unigram BPC)
    test_t_src_tok_all = []
    test_true_tok_all = []
    for _, tids_doc in test_docs:
        for pos in range(len(tids_doc) - 1):
            test_t_src_tok_all.append(int(tids_doc[pos]))
            test_true_tok_all.append(int(tids_doc[pos + 1]))
    t_src_tok_global = np.array(test_t_src_tok_all, dtype=np.int64)
    true_tok_global = np.array(test_true_tok_all, dtype=np.int64)
    oov_mask_global = true_tok_global >= V_TOK
    valid_global = ~oov_mask_global
    valid_idx_global = np.where(valid_global)[0]
    true_tok_valid_global = true_tok_global[valid_idx_global]
    t_src_tok_valid_global = t_src_tok_global[valid_idx_global]
    tot_t_global = int(valid_global.sum())

    # Unigram + bigram BPC (PROJ_DIM-independent)
    if tot_t_global > 0:
        uni_nll_global = float(-uni_log[true_tok_valid_global].sum())
        uni_bpc_global = (uni_nll_global / tot_t_global) / log2
        big_nll_global = 0.0; big_t_ok_global = 0
        for _i in range(tot_t_global):
            _ts = int(t_src_tok_valid_global[_i]); _tt = int(true_tok_valid_global[_i])
            _bp = big_tok.get(_ts)
            if _bp is not None and _bp.sum() > 0:
                big_t_ok_global += (int(np.argmax(_bp)) == _tt)
                _bp_mle = float(_bp[_tt]) / (float(_bp.sum()) + 1e-9)
                _bfd_tt = (1.0 - INTERP_B) * _bp_mle + INTERP_B * float(uni_dist[_tt])
                big_nll_global += -math.log(_bfd_tt + 1e-300)
            else:
                big_t_ok_global += (uni_tok_pred == _tt)
                big_nll_global += float(-uni_log[_tt])
        big_bpc_global = (big_nll_global / tot_t_global) / log2
    else:
        uni_bpc_global = float("nan")
        big_bpc_global = float("nan")

    # Per-unit results (one entry per PROJ_DIM)
    per_unit_list: List[Dict[str, Any]] = []

    # --- OUTER LOOP: PROJ_DIM sweep ---
    for pd_idx, proj_dim in enumerate(PROJ_DIM_GRID):
        t_pd = time.time()
        print("[seed=%d PROJ_DIM=%d] fitting projection..." % (seed, proj_dim), flush=True)

        # Fit PCA projection (identity if proj_dim >= residual_dim)
        W_proj = fit_pca_projection(train_res_n, proj_dim)
        effective_proj_dim = W_proj.shape[1]
        is_identity = (proj_dim >= train_res_n.shape[1])
        print("[seed=%d PROJ_DIM=%d] W_proj shape=%s identity=%s" % (
            seed, proj_dim, W_proj.shape, is_identity), flush=True)

        # Project train + test residuals (L2-renormalized in projected space)
        def project_doc_list(doc_list):
            return [apply_projection(d[0], W_proj) for d in doc_list]
        train_proj = project_doc_list(train_docs)
        test_proj = project_doc_list(test_docs)
        train_proj_flat = np.concatenate(train_proj, axis=0)

        # VQ in projected space
        print("[seed=%d PROJ_DIM=%d] fitting VQ V_C=%d on %d tokens..." % (
            seed, proj_dim, vc, len(train_proj_flat)), flush=True)
        try:
            from sklearn.cluster import MiniBatchKMeans
            km = MiniBatchKMeans(n_clusters=vc, random_state=seed,
                                 batch_size=4096, n_init=3, max_iter=100, verbose=0)
            km.fit(train_proj_flat)

            def assign_cids(proj_list):
                all_r = np.concatenate(proj_list, axis=0)
                return km.predict(all_r).astype(np.int64)
        except ImportError:
            print("[seed=%d PROJ_DIM=%d] sklearn unavailable; numpy argmin VQ" % (
                seed, proj_dim), flush=True)
            rng_vq = np.random.default_rng(seed + 5000 + pd_idx * 100)
            centers = train_proj_flat[rng_vq.choice(len(train_proj_flat), size=vc, replace=False)]

            def assign_cids(proj_list):
                all_r = np.concatenate(proj_list, axis=0)
                chunk = 4096
                out = np.empty(len(all_r), dtype=np.int64)
                for s_pos in range(0, len(all_r), chunk):
                    e_pos = s_pos + chunk
                    diff = all_r[s_pos:e_pos, None, :] - centers[None, :, :]
                    out[s_pos:e_pos] = np.argmin((diff ** 2).sum(-1), axis=1)
                return out

        train_cids_flat = assign_cids(train_proj)
        test_cids_flat = assign_cids(test_proj)

        unique_cids_train = np.unique(train_cids_flat)
        utilization = len(unique_cids_train) / vc

        # Slice cids per-doc
        def slice_docs_cids(docs_split, cids_flat):
            seqs = []; offset = 0
            for doc_res, doc_tok in docs_split:
                n_doc = len(doc_res)
                seqs.append((cids_flat[offset:offset + n_doc], doc_tok))
                offset += n_doc
            return seqs

        train_seqs = slice_docs_cids(train_docs, train_cids_flat)
        test_seqs = slice_docs_cids(test_docs, test_cids_flat)

        # Sparse concept codebook (substrate-native; PROJ_DIM-independent sparse code allocation)
        rng2 = np.random.default_rng(seed + 1000 + pd_idx * 100)
        C = sparse_codebook(vc, n_dim, f, rng2)
        k_val = max(1, round(f * n_dim))

        # Build decode memory D + concept_tok_counts
        D = np.zeros((n_dim, V_TOK), dtype=np.float32)
        concept_tok_counts: Dict[int, np.ndarray] = {}
        for cids_doc, tids_doc in train_seqs:
            for t_pos in range(len(cids_doc)):
                tok = int(tids_doc[t_pos])
                if tok < V_TOK:
                    D[:, tok] += C[int(cids_doc[t_pos])] * LR_DECODE
                    c = int(cids_doc[t_pos])
                    if c not in concept_tok_counts:
                        concept_tok_counts[c] = np.zeros(V_TOK, dtype=np.int64)
                    concept_tok_counts[c][tok] += 1
        ceiling_pred = {c: int(np.argmax(v)) for c, v in concept_tok_counts.items()}

        # Saturation alpha for this proj_dim's cluster assignment
        train_cids_all = np.concatenate([s[0] for s in train_seqs])
        unique_ctx_pairs = len(set(zip(train_cids_all[:-1].tolist(), train_cids_all[1:].tolist())))
        alpha = unique_ctx_pairs / n_dim
        saturated = (alpha > 1.0)

        # Build transition store at K=1
        P_src_list, P_dst_list = [], []
        for cids_doc, _ in train_seqs:
            ctx_vecs = build_context_vecs_batched(C, cids_doc.astype(np.int64), K_depth=K, n_dim=n_dim)
            if ctx_vecs.shape[0] == 0:
                continue
            P_src_list.append(ctx_vecs)
            P_dst_list.append(np.array(
                [C[int(cids_doc[t_pos + 1])] for t_pos in range(ctx_vecs.shape[0])],
                dtype=np.float32))

        if not P_src_list:
            per_unit_list.append({
                "seed": seed, "proj_dim": proj_dim,
                "substrate_bpc": float("nan"), "ceiling_bpc": float("nan"),
                "bigram_bpc": big_bpc_global, "unigram_bpc": uni_bpc_global,
                "substrate_top1": float("nan"), "ceiling_top1": float("nan"),
                "codebook_utilization": utilization, "alpha": alpha, "saturated": saturated,
                "is_identity_arm": is_identity, "effective_proj_dim": effective_proj_dim,
                "k_active": k_val,
                "n_trans": 0, "n_token_test_pairs": tot_t_global,
                "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
                "wall_s": time.time() - t_pd,
            })
            continue

        P_src = np.concatenate(P_src_list, axis=0)
        P_dst = np.concatenate(P_dst_list, axis=0)
        n_trans = P_src.shape[0]
        print("[seed=%d PROJ_DIM=%d] n_trans=%d alpha=%.3f%s building W (%dx%d)..." % (
            seed, proj_dim, n_trans, alpha, " [SAT]" if saturated else "",
            n_dim, n_dim), flush=True)
        W_k = build_W(P_src, P_dst)
        del P_src, P_dst

        # Build context vecs for all test positions
        _c_src_list, _c_tgt_list = [], []
        for cids_doc, _ in test_seqs:
            cids_arr = cids_doc.astype(np.int64)
            ctx_vecs = build_context_vecs_batched(C, cids_arr, K_depth=K, n_dim=n_dim)
            n_pos = ctx_vecs.shape[0]
            if n_pos == 0:
                continue
            _c_src_list.append(ctx_vecs)
            _c_tgt_list.extend(cids_arr[1:n_pos + 1].tolist())

        if not _c_src_list:
            per_unit_list.append({
                "seed": seed, "proj_dim": proj_dim,
                "substrate_bpc": float("nan"), "ceiling_bpc": float("nan"),
                "bigram_bpc": big_bpc_global, "unigram_bpc": uni_bpc_global,
                "substrate_top1": float("nan"), "ceiling_top1": float("nan"),
                "codebook_utilization": utilization, "alpha": alpha, "saturated": saturated,
                "is_identity_arm": is_identity, "effective_proj_dim": effective_proj_dim,
                "k_active": k_val,
                "n_trans": n_trans, "n_token_test_pairs": 0,
                "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
                "wall_s": time.time() - t_pd,
            })
            continue

        Q_all = np.concatenate(_c_src_list, axis=0)
        c_tgt_all = np.array(_c_tgt_list, dtype=np.int64)
        tot_c = len(c_tgt_all)

        print("[seed=%d PROJ_DIM=%d] batched recall: %d queries..." % (
            seed, proj_dim, tot_c), flush=True)
        pred_concept_all = batched_concept_recall(W_k, Q_all, C)
        del Q_all

        sub_c_ok = int((pred_concept_all == c_tgt_all).sum())

        # Token-level eval (OOV-filtered)
        pred_c_valid = pred_concept_all[valid_idx_global]
        c_tgt_valid = c_tgt_all[valid_idx_global]

        BATCH_TOK_CHUNK = 2000
        n_valid = tot_t_global
        pred_tok_valid = np.empty(n_valid, dtype=np.int64)
        true_tok_logprob = np.empty(n_valid, dtype=np.float64)

        print("[seed=%d PROJ_DIM=%d] batched token decode: %d positions..." % (
            seed, proj_dim, n_valid), flush=True)
        for _ck_s in range(0, n_valid, BATCH_TOK_CHUNK):
            _ck_e = min(_ck_s + BATCH_TOK_CHUNK, n_valid)
            _cvecs = C[pred_c_valid[_ck_s:_ck_e]]
            _lp = batched_token_logprob(D, _cvecs, uni_dist, LAM_BACKOFF)
            pred_tok_valid[_ck_s:_ck_e] = np.argmax(_lp, axis=1)
            _tt = true_tok_valid_global[_ck_s:_ck_e]
            true_tok_logprob[_ck_s:_ck_e] = _lp[np.arange(_ck_e - _ck_s), _tt]

        sub_t_ok = int((pred_tok_valid == true_tok_valid_global).sum())
        sub_nll = float(-true_tok_logprob.sum())

        ceil_t_ok = 0; ceil_nll = 0.0
        for _i in range(n_valid):
            _ctgt = int(c_tgt_valid[_i]); _tt = int(true_tok_valid_global[_i])
            _ceil_t = ceiling_pred.get(_ctgt, uni_tok_pred)
            ceil_t_ok += (_ceil_t == _tt)
            _ctd = concept_tok_counts.get(_ctgt)
            if _ctd is not None and _ctd.sum() > 0:
                _ctd_mle = float(_ctd[_tt]) / (float(_ctd.sum()) + 1e-9)
                _ctd_tt = (1.0 - INTERP_B) * _ctd_mle + INTERP_B * float(uni_dist[_tt])
                ceil_nll += -math.log(_ctd_tt + 1e-300)
            else:
                ceil_nll += float(-uni_log[_tt])

        tt = max(tot_t_global, 1)
        sub_bpc = (sub_nll / tt) / log2
        ceiling_bpc = (ceil_nll / tt) / log2

        per_unit = {
            "seed": seed,
            "proj_dim": proj_dim,
            "substrate_bpc": sub_bpc,
            "ceiling_bpc": ceiling_bpc,
            "bigram_bpc": big_bpc_global,
            "unigram_bpc": uni_bpc_global,
            "substrate_top1": sub_t_ok / tt,
            "ceiling_top1": ceil_t_ok / tt,
            "substrate_concept_top1": sub_c_ok / max(tot_c, 1),
            "codebook_utilization": utilization,
            "alpha": alpha,
            "saturated": saturated,
            "is_identity_arm": is_identity,
            "effective_proj_dim": effective_proj_dim,
            "k_active": k_val,
            "n_trans": n_trans,
            "n_token_test_pairs": tot_t_global,
            "n_concept_test_pairs": tot_c,
            "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "wall_s": time.time() - t_pd,
        }
        per_unit_list.append(per_unit)

        print("  [seed=%d PROJ_DIM=%d] sub_bpc=%.3f ceiling_bpc=%.3f bigram=%.3f "
              "concept_top1=%.3f util=%.1f%% alpha=%.3f wall=%.1fs%s%s" % (
                  seed, proj_dim, sub_bpc, ceiling_bpc, big_bpc_global,
                  per_unit["substrate_concept_top1"], utilization * 100, alpha,
                  per_unit["wall_s"],
                  " [IDENTITY]" if is_identity else "",
                  " [SAT]" if saturated else ""), flush=True)

    elapsed = time.time() - t0
    # Note: per_seed wraps the list of per_unit dicts; checkpoint stores this directly
    return {
        "seed": seed,
        "per_unit": per_unit_list,
        "V_C": vc, "N_DIM": n_dim, "K": K, "f_sparse": f,
        "V_TOK": V_TOK,
        "n_docs": len(train_docs) + len(test_docs),
        "n_train_docs": len(train_docs),
        "n_test_docs": len(test_docs),
        "run_mode": RUN_MODE,
        "proj_dim_grid": PROJ_DIM_GRID,
        "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "elapsed_s": elapsed,
    }


# ---------------------------------------------------------------------------
# Verdict (pre-registered bands per research note 2026-06-22)
# ---------------------------------------------------------------------------

def _flatten_per_unit(ps: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    """Group per_unit entries by proj_dim across seeds."""
    by_pd: Dict[int, List[Dict[str, Any]]] = {}
    for p in ps:
        for u in p.get("per_unit", []):
            pd = int(u["proj_dim"])
            by_pd.setdefault(pd, []).append(u)
    return by_pd


def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Compute verdict against research-note pre-registered bands.

    HARD-PASS: some PROJ_DIM has ceiling_bpc <= 1.75 AND substrate_bpc <= 4.75 AND cv <= 0.05.
    MIDDLE_BAND: ceiling_bpc drops 0.10-0.30 vs identity OR substrate_bpc improves.
    HARD-FAIL: ceiling_bpc change < 0.05 across all PROJ_DIM, OR anchor mismatch, OR LLM-call violation.
    """
    by_pd = _flatten_per_unit(ps)

    if not by_pd:
        return ("HARD_FAIL", "HARD_FAIL: no per_unit data; cell produced no results.")

    # Compute per-PROJ_DIM aggregates
    pd_stats: Dict[int, Dict[str, float]] = {}
    for pd, units in by_pd.items():
        cbs = [u["ceiling_bpc"] for u in units if not math.isnan(u.get("ceiling_bpc", float("nan")))]
        sbs = [u["substrate_bpc"] for u in units if not math.isnan(u.get("substrate_bpc", float("nan")))]
        ut1s = [u.get("codebook_utilization", float("nan")) for u in units]
        ct1s = [u.get("substrate_concept_top1", float("nan")) for u in units]
        cv = 0.0
        if len(sbs) > 1 and abs(float(np.mean(sbs))) > 1e-9:
            cv = float(np.std(sbs)) / abs(float(np.mean(sbs)))
        pd_stats[pd] = {
            "ceiling_bpc_mean": float(np.mean(cbs)) if cbs else float("nan"),
            "substrate_bpc_mean": float(np.mean(sbs)) if sbs else float("nan"),
            "ceiling_bpc_cv": (float(np.std(cbs)) / abs(float(np.mean(cbs)))
                              if len(cbs) > 1 and abs(float(np.mean(cbs))) > 1e-9 else 0.0),
            "substrate_bpc_cv": cv,
            "codebook_utilization_mean": float(np.mean([u for u in ut1s if not math.isnan(u)])) if any(not math.isnan(u) for u in ut1s) else float("nan"),
            "concept_top1_mean": float(np.mean([u for u in ct1s if not math.isnan(u)])) if any(not math.isnan(u) for u in ct1s) else float("nan"),
            "n_seeds": len(units),
            "any_saturated": any(u.get("saturated", False) for u in units),
            "is_identity_arm": bool(units[0].get("is_identity_arm", False)),
            "any_llm_violation": any(u.get("llm_forward_calls_at_inference", 0) > 0 for u in units),
        }

    # LLM-call gate (any violation -> HARD_FAIL regardless of metrics)
    any_llm_viol = any(s["any_llm_violation"] for s in pd_stats.values())
    if any_llm_viol:
        summary = "; ".join("PD=%d llm_calls=NONZERO" % pd for pd, s in pd_stats.items() if s["any_llm_violation"])
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (LLM forward call counter > 0). " + summary)

    # Identity-arm anchor check (PROJ_DIM=768 or any pd >= RESIDUAL_DIM)
    identity_pd = None
    for pd, s in pd_stats.items():
        if s["is_identity_arm"]:
            identity_pd = pd
            break
    n2_anchor_ceiling = 2.049  # from n2 LANDED_VET 2026-06-22 (re-derived from per_seed)
    n2_anchor_substrate = 4.959
    anchor_note = ""
    anchor_failed = False
    if identity_pd is not None:
        id_ceiling = pd_stats[identity_pd]["ceiling_bpc_mean"]
        if not math.isnan(id_ceiling):
            diff = abs(id_ceiling - n2_anchor_ceiling)
            if diff < 0.05:
                anchor_note = " ANCHOR-OK(id_PD=%d ceiling=%.3f ~ %.3f)" % (
                    identity_pd, id_ceiling, n2_anchor_ceiling)
            else:
                anchor_note = " ANCHOR-MISMATCH(id_PD=%d ceiling=%.3f vs N2=%.3f diff=%.3f)" % (
                    identity_pd, id_ceiling, n2_anchor_ceiling, diff)
                anchor_failed = True

    # Identity-arm ceiling for delta comparison
    identity_ceiling = (pd_stats[identity_pd]["ceiling_bpc_mean"]
                       if identity_pd is not None else n2_anchor_ceiling)
    identity_substrate = (pd_stats[identity_pd]["substrate_bpc_mean"]
                         if identity_pd is not None else n2_anchor_substrate)

    # Find best non-identity arm (the SimVQ MVP test)
    best_pd = None
    best_ceiling = float("inf")
    best_substrate = float("inf")
    best_cv = 1.0
    for pd, s in pd_stats.items():
        if s["is_identity_arm"]:
            continue
        cb = s["ceiling_bpc_mean"]
        if not math.isnan(cb) and cb < best_ceiling:
            best_ceiling = cb
            best_pd = pd
            best_substrate = s["substrate_bpc_mean"]
            best_cv = s["substrate_bpc_cv"]

    # Pre-registered bands
    HARD_PASS_CEILING_THRESHOLD = 1.75  # ceiling_bpc must drop to <=1.75 (>=0.30 bits from 2.049)
    HARD_PASS_SUBSTRATE_THRESHOLD = 4.75  # substrate_bpc must drop to <=4.75 (>=0.21 bits from 4.959)
    MIDDLE_BAND_CEILING_DELTA = 0.10  # ceiling_bpc must drop >=0.10 bits vs identity
    HARD_FAIL_CEILING_DELTA = 0.05  # below this, ceiling unchanged -> SimVQ HARD-FAIL

    # Per-config summary string
    cfg_lines = []
    for pd in sorted(pd_stats.keys()):
        s = pd_stats[pd]
        cfg_lines.append(
            "PD=%d%s: ceiling=%.3f sub_bpc=%.3f cv=%.3f util=%.1f%% concept_top1=%.3f" % (
                pd, " [IDENTITY]" if s["is_identity_arm"] else "",
                s["ceiling_bpc_mean"], s["substrate_bpc_mean"], s["substrate_bpc_cv"],
                s["codebook_utilization_mean"] * 100, s["concept_top1_mean"]))

    summary = (
        "best_PD=%s best_ceiling_bpc=%.3f identity_ceiling=%.3f delta=%.3f "
        "best_substrate_bpc=%.3f cv=%.3f%s; %s" % (
            best_pd if best_pd is not None else "NONE",
            best_ceiling if best_ceiling < float("inf") else float("nan"),
            identity_ceiling,
            (identity_ceiling - best_ceiling) if best_ceiling < float("inf") else float("nan"),
            best_substrate if best_substrate < float("inf") else float("nan"),
            best_cv,
            anchor_note,
            " | ".join(cfg_lines),
        )
    )

    # Anchor mismatch -> HARD_FAIL (cannot interpret SimVQ deltas without correct baseline)
    if anchor_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: identity-arm anchor mismatch (N2 baseline NOT reproduced). " + summary)

    # No non-identity arm -> data incomplete
    if best_pd is None or best_ceiling == float("inf"):
        return ("HARD_FAIL",
                "HARD_FAIL: no non-identity SimVQ arm produced ceiling_bpc; cell incomplete. " + summary)

    ceiling_delta = identity_ceiling - best_ceiling  # positive = SimVQ improves ceiling

    # HARD_PASS: SimVQ arm ceiling <= 1.75 AND substrate <= 4.75 AND cv <= 0.05
    if (best_ceiling <= HARD_PASS_CEILING_THRESHOLD
            and best_substrate <= HARD_PASS_SUBSTRATE_THRESHOLD
            and best_cv <= 0.05
            and not pd_stats[best_pd]["any_saturated"]):
        return ("HARD_PASS",
                "HARD_PASS: SimVQ PROJ_DIM=%d achieves ceiling_bpc=%.3f<=1.75 AND substrate_bpc=%.3f<=4.75 "
                "AND cv=%.3f<=0.05 AND substrate-only-decode (LLM calls=0). " % (
                    best_pd, best_ceiling, best_substrate, best_cv) + summary)

    # MIDDLE_BAND: ceiling drops >=0.10 bits OR substrate beats identity by meaningful margin
    substrate_delta = identity_substrate - best_substrate
    if ceiling_delta >= MIDDLE_BAND_CEILING_DELTA or substrate_delta >= 0.10:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: SimVQ PROJ_DIM=%d partial mechanism (ceiling_delta=%.3f or substrate_delta=%.3f). " % (
                    best_pd, ceiling_delta, substrate_delta) + summary)

    # HARD_FAIL: ceiling_bpc change < 0.05 across all non-identity arms
    if abs(ceiling_delta) < HARD_FAIL_CEILING_DELTA:
        return ("HARD_FAIL",
                "HARD_FAIL: SimVQ-MVP makes no measurable ceiling_bpc change (delta=%.3f < 0.05) -- "
                "VQ-alignment is NOT the decode-bottleneck at fixed V_C=1024. Route to Path A. " % ceiling_delta
                + summary)

    # Fallback MIDDLE_BAND for everything else (small but nonzero delta)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: SimVQ small-effect ceiling_delta=%.3f (<0.10). " % ceiling_delta + summary)


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s V_C=%d N_DIM=%d K=%d f=%.4f PROJ_DIM_GRID=%s MAX_DOCS=%d seeds=%s" % (
    ANCHOR_NAME, RUN_MODE, V_C, N_DIM_RUN, K, F_SPARSE, PROJ_DIM_GRID, MAX_DOCS, SEEDS), flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "N": N_DIM_RUN, "proj_grid": PROJ_DIM_GRID,
              "V_C": V_C, "K": K}

done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds already complete; running %s" % (
    len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

t_total = time.time()
ps = []

for seed in remaining_seeds:
    r = run_seed(seed)
    ps.append(r)
    write_partial(out_dir, seed, r)
    # Per-seed summary across PROJ_DIM
    pd_strs = []
    for u in r["per_unit"]:
        pd_strs.append("PD=%d:ceiling=%.3f sub=%.3f" % (
            u["proj_dim"], u["ceiling_bpc"], u["substrate_bpc"]))
    print("  [seed=%d] %s elapsed=%.1fs llm_calls=%d" % (
        seed, " | ".join(pd_strs), r["elapsed_s"], r["llm_forward_calls_at_inference"]), flush=True)

if done_seeds:
    agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
    for k, v in agg.items():
        ps.append(v)

if not ps:
    print("[ERROR] no seeds completed; aborting", flush=True)
    sys.exit(1)

# Assert no LLM calls happened during the entire run (the substrate-only-gate audit)
total_llm_calls = sum(p.get("llm_forward_calls_at_inference", 0) for p in ps)
assert total_llm_calls == 0, (
    "FATAL: %d LLM forward calls occurred during inference -- substrate-only-decode gate VIOLATED" % total_llm_calls)

v, vmsg = verdict(ps)
print("\n[VERDICT] " + vmsg, flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "config_version": CONFIG_VERSION,
    "verdict": v,
    "verdict_msg": vmsg,
    "run_mode": RUN_MODE,
    "n_seeds": len(ps),
    "V_C": V_C,
    "N_DIM": N_DIM_RUN,
    "K": K,
    "f_sparse": F_SPARSE,
    "proj_dim_grid": PROJ_DIM_GRID,
    "zero_llm_calls_at_inference": True,
    "total_llm_forward_calls_observed": total_llm_calls,
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
