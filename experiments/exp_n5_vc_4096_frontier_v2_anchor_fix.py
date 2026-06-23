"""
n5_vc_4096_frontier_v2_anchor_fix -- Path A V_C=4096 frontier with N2-anchor-reproduction gate.

REVIVAL OF n5_vc_4096_frontier_v1 (HARD_FAIL 2026-06-22 wall=5530s):
  v1 HARD_FAIL via ANCHOR MISMATCH at the V_C=1024/N=16384 sanity arm:
    v1 measured sub_bpc=5.084 vs N2 baseline's 4.959 (diff=0.125, exceeds tolerance).
  v1 headline (V_C=4096 best sub_bpc=5.680) is INVALIDATED because the baseline-
  reproduction CAN-FAIL gate failed -- the comparison "V_C=4096 vs V_C=1024
  baseline" is noise until the V_C=1024 baseline reproduces.

ROOT CAUSES (audit of v1 vs N2 v1 baseline):
  1. CODEBOOK RNG SEED FORMULA DIVERGED:
       v1:  rng2 = default_rng(seed + 1000 + vc*31 + n_dim*17)
              => (seed=7, vc=1024, n=16384) seed=310279
       N2:  rng2 = default_rng(seed + 1000 + n_dim_idx*100)
              => (seed=7, n_dim_idx=2 i.e. n=16384) seed=1207
     Different RNG seed -> different sparse codebook C -> different W matrix
     -> different recall -> different sub_bpc. NON-COMMUTING with N2.
  2. VQ ASSIGNMENT METHOD DIVERGED:
       v1:  centers = L2-normalize(km.cluster_centers_);
            cids = np.argmax(residuals_n @ centers.T)  (cosine-sim argmax)
       N2:  cids = km.predict(residuals_n)  (sklearn euclidean argmin
            against RAW non-normalized cluster_centers_)
     Sklearn's km.predict() != cosine-sim argmax post-L2-norm; the two are
     close-but-not-equal and accumulate disagreement across 100k tokens.

ANCHOR-FIX DESIGN (this v2):
  - V_C=1024 arms: replicate N2 baseline VERBATIM:
      * RNG: rng_C = default_rng(seed + 1000 + n_dim_idx * 100)
      * VQ:  cids = km.predict(residuals_l2norm)  (no manual argmax)
    This forces byte-for-byte reproduction of the N2 anchor cell at
    (V_C=1024, N=16384), which is the load-bearing harness check.
  - V_C=4096 arms: same N2-style km.predict assignment; codebook RNG uses an
    offset disjoint from the V_C=1024 arms so the two RNG streams cannot
    collide. (RNG formula: seed + 1000 + n_dim_idx*100 + 50000.)
  - CAN-FAIL PRE-FLIGHT GATE: run V_C=1024/N=16384 arm FIRST per seed.
    If sub_bpc not in [4.94, 4.98] (N2's 4.959 +/- 0.02), ABORT WITH
    HARD_FAIL_HARNESS_DRIFT before running the V_C=4096 sweep. Saves
    ~90 min of compute when the harness is drifted.
  - n_seeds = 3 (same as v1), V_C_GRID = [1024, 4096] unchanged,
    N_GRID = [16384, 32768] unchanged.

FIXED CONFIG (unchanged from v1):
  K = 1 (substrate context depth)
  F_SPARSE = 0.006
  V_C_GRID = [1024, 4096]
  N_DIM_GRID = [16384, 32768]
  TRAIN_FRAC = 0.8
  LR_DECODE = 1.0
  LAM_BACKOFF = 0.1
  INTERP_B = 0.3
  seeds = [7, 17, 23] full; [1] smoke

SCIENTIFIC QUESTIONS (PRE-REGISTERED; SAME AS v1 PLUS GATE):
  (a) ANCHOR_PRE-GATE: V_C=1024/N=16384 sub_bpc in [4.94, 4.98] for each seed
      (HARD ABORT on miss; tolerance tightened to +/-0.02 vs v1's +/-0.10).
  (b) HARD_PASS: V_C=4096 best sub_bpc <= N2(4.959) - margin(0.10) = 4.859,
      cv <= 0.05.
  (c) HARD_FAIL: V_C=4096 best sub_bpc >= N2 4.959 (no lift at frontier).
  (d) MIDDLE_BAND: V_C=4096 best in (4.859, 4.959) (partial mechanism).

PRE-REGISTERED BANDS (CHAIN-GRADE per Skunkworks spec):
  HARD_PASS_GATE: V_C=1024/N=16384 anchor pre-gate reproduces N2 (4.94 <= sub <= 4.98).
  HARD_PASS: V_C=4096 best sub_bpc <= 4.859 (N2 4.959 - 0.10 margin)
             AND cv <= 0.05 AND not saturated AND zero LLM calls
             AND direction-correct AND run_mode = "full".
  MIDDLE_BAND: V_C=4096 best in (4.859, 4.959).
  HARD_FAIL: V_C=4096 best >= 4.959 (no lift), or harness drift, or any
             cross-gate failure.

INSTRUMENTATION (REQUIRED, per Skunkworks chain-grade spec):
  per_unit: (seed, V_C, N_DIM); cv <= 0.05
  zero_llm_calls_at_inference: True LOGGED
  ceiling_bpc + concept_top1 per config
  corpus_provenance_real=True; allow_synthetic=False
  CONFIG_VERSION includes "anchor-fix-N2-baseline-reproduction-gate" marker
  ANCHOR_PRE-GATE result LOGGED per seed (PASS / FAIL / SKIP)

REUSES n4/n2 HARNESS VERBATIM:
  - HD-binding context: ctx_vec = L2_normalize(sum_j roll(C[c_{t-j}], j))
  - W-materialized batched recall: W = P_src.T @ P_dst
  - v3.1 count-proportional + Jelinek-Mercer interpolation decode
  - Per-seed checkpoint / resume (PROT-021 run_config guard)
  - _instrumentation_selftest at module scope
  - ANCHOR_NAME / write_metrics / CONFIG_VERSION discipline
  - Zero-D-overlap fallback in batched_token_logprob (Fix #6)
  - K=1 hard one-hot (clean V_C-alone discriminator)
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

ANCHOR_NAME = "n5_vc_4096_frontier_v2_anchor_fix"

# ---------------------------------------------------------------------------
# LLM-call audit counter (substrate-only-decode gate; structural blocker #3)
# ---------------------------------------------------------------------------
_LLM_CALL_COUNTER = [0]


# ---------------------------------------------------------------------------
# Configurable params
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--vc-grid", dest="vc_grid", type=str, default=None,
                 help="Comma-separated V_C values (default '1024,4096')")
_ap.add_argument("--n-grid", dest="n_grid", type=str, default=None,
                 help="Comma-separated N_DIM values (default '16384,32768')")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# ---------------------------------------------------------------------------
# Module-level constants (AST-verified)
# ---------------------------------------------------------------------------

K = 1
F_SPARSE = 0.006

# V_C_GRID / N_DIM_GRID -- unchanged from v1
_VC_GRID_FULL = [1024, 4096]
_N_GRID_FULL = [16384, 32768]
_VC_GRID_SMOKE = [1024, 4096]
_N_GRID_SMOKE = [16384]

_vc_str = _ARGS.vc_grid or os.environ.get("HDLAB_VC_GRID", "")
if _vc_str.strip():
    _VC_GRID_OVERRIDE = [int(x.strip()) for x in _vc_str.split(",") if x.strip()]
else:
    _VC_GRID_OVERRIDE = []

_n_str = _ARGS.n_grid or os.environ.get("HDLAB_N_GRID", "")
if _n_str.strip():
    _N_GRID_OVERRIDE = [int(x.strip()) for x in _n_str.split(",") if x.strip()]
else:
    _N_GRID_OVERRIDE = []

if RUN_MODE == "smoke":
    SEEDS = [1]
    VC_GRID = _VC_GRID_OVERRIDE if _VC_GRID_OVERRIDE else _VC_GRID_SMOKE
    N_GRID = _N_GRID_OVERRIDE if _N_GRID_OVERRIDE else _N_GRID_SMOKE
    MAX_DOCS = 200
    MAX_TOK_VOCAB = 1000
else:
    SEEDS = [7, 17, 23]
    VC_GRID = _VC_GRID_OVERRIDE if _VC_GRID_OVERRIDE else _VC_GRID_FULL
    N_GRID = _N_GRID_OVERRIDE if _N_GRID_OVERRIDE else _N_GRID_FULL
    MAX_DOCS = 100000
    MAX_TOK_VOCAB = 50257

TRAIN_FRAC = 0.8
LR_DECODE = 1.0
LAM_BACKOFF = 0.1
INTERP_B = 0.3
RESIDUAL_DIM = 768

# Largest V_C in any cell run; used in selftest range checks.
MAX_VC = 65536

# ANCHOR-FIX PRE-GATE constants (load-bearing; v2 discriminator)
N2_ANCHOR_SUBSTRATE_BPC = 4.959
ANCHOR_PREGATE_TOLERANCE = 0.02  # tightened vs v1's 0.10
ANCHOR_PREGATE_LOW = N2_ANCHOR_SUBSTRATE_BPC - ANCHOR_PREGATE_TOLERANCE   # 4.939
ANCHOR_PREGATE_HIGH = N2_ANCHOR_SUBSTRATE_BPC + ANCHOR_PREGATE_TOLERANCE  # 4.979

# HARD_PASS / MIDDLE_BAND / HARD_FAIL thresholds
HARD_PASS_MARGIN = 0.10
HARD_PASS_THRESHOLD = N2_ANCHOR_SUBSTRATE_BPC - HARD_PASS_MARGIN  # 4.859

CONFIG_VERSION = (
    "VC_GRID=%s,N_GRID=%s,K=%d,f=%.4f,DECODE=countprop_interp,"
    "ASSIGN=km_predict_n2_baseline,VQ_RNG=n2_n_dim_idx_100,"
    "MAX_DOCS=%d,SEEDS=%s,SPLIT=%.1f,"
    "anchor-fix-N2-baseline-reproduction-gate-tol_%.2f" % (
        "-".join(str(p) for p in (_VC_GRID_FULL if RUN_MODE != "smoke" else _VC_GRID_SMOKE)),
        "-".join(str(p) for p in (_N_GRID_FULL if RUN_MODE != "smoke" else _N_GRID_SMOKE)),
        K, F_SPARSE,
        100000 if RUN_MODE != "smoke" else 200,
        "-".join(str(s) for s in ([7, 17, 23] if RUN_MODE != "smoke" else [1])),
        TRAIN_FRAC,
        ANCHOR_PREGATE_TOLERANCE,
    )
)

NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"


# ---------------------------------------------------------------------------
# Substrate ops (n2 verbatim)
# ---------------------------------------------------------------------------

def sparse_codebook(vc: int, n: int, f: float, rng: np.random.Generator) -> np.ndarray:
    """Build sparse binary codebook, shape (vc, n), k = round(f*n) active per row."""
    k = max(1, round(f * n))
    C = np.zeros((vc, n), dtype=np.float32)
    for i in range(vc):
        idx = rng.choice(n, k, replace=False)
        C[i, idx] = 1.0
    return C


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
    """Batched calibrated log-prob with zero-D-overlap fallback (Fix #6, n4 pattern)."""
    scores = np.maximum(concept_vecs @ D, 0.0)
    row_sums = scores.sum(axis=1, keepdims=True)
    zero_rows = (row_sums <= 1e-12)
    V_TOK_local = scores.shape[1]
    safe_scores = np.where(zero_rows, np.ones_like(scores) / V_TOK_local, scores)
    safe_sums = np.where(zero_rows, np.ones_like(row_sums), row_sums)
    probs = safe_scores / safe_sums
    if uni_dist is not None and lam > 0.0:
        probs = (1.0 - lam) * probs + lam * uni_dist[None, :]
    return np.log(np.maximum(probs, 1e-30))


def token_logprob(D: np.ndarray, concept_vec: np.ndarray,
                  uni_dist: np.ndarray = None, lam: float = 0.1) -> np.ndarray:
    """Per-query calibrated log-prob (with zero-sum fallback to uniform)."""
    scores = np.maximum(D.T @ concept_vec, 0.0)
    s = float(scores.sum())
    if s <= 1e-12:
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
# N2-baseline VQ assignment (km.predict on L2-normalized residuals, then assign
# against raw cluster_centers_ via sklearn's internal euclidean argmin).
# This is the byte-for-byte N2 assignment used in exp_n2_capacity_scaling_v1.
# ---------------------------------------------------------------------------

def n2_baseline_assign_cids(km_model, doc_res_list: List[np.ndarray]) -> np.ndarray:
    """N2-VERBATIM assignment: l2-normalize residuals, then km.predict.

    This is the EXACT pipeline N2 uses; we replicate it here so the V_C=1024
    arm of v2 reproduces the N2 baseline at byte-level (subject to the same
    km being fit with identical (n_clusters, random_state, batch_size,
    n_init, max_iter) parameters).
    """
    all_r = np.concatenate(doc_res_list, axis=0)
    nrm = np.linalg.norm(all_r, axis=1, keepdims=True) + 1e-8
    return km_model.predict(all_r / nrm).astype(np.int64)


# ---------------------------------------------------------------------------
# RNG seed formulas (N2-style; load-bearing for anchor reproduction)
# ---------------------------------------------------------------------------

def codebook_rng_seed(seed: int, n_dim_idx: int, vc: int) -> int:
    """Compute deterministic RNG seed for codebook C.

    For V_C=1024: use N2's exact formula (seed + 1000 + n_dim_idx*100).
    For V_C>1024: same base + 50000 offset so the two streams cannot collide.
    """
    base = seed + 1000 + n_dim_idx * 100
    if vc <= 1024:
        return base
    return base + 50000


# ---------------------------------------------------------------------------
# Synthetic forward pass for self-test
# ---------------------------------------------------------------------------

def _run_synthetic(rng_seed: int, n_dim: int = 64, f: float = 0.05,
                   vc: int = 8, vt: int = 20, residual_dim: int = 32) -> Dict[str, Any]:
    """Synthetic forward pass at K=1 hard one-hot for one (V_C, N_DIM)."""
    rng = np.random.default_rng(rng_seed)
    n_docs = 20
    docs_res = [rng.standard_normal((12, residual_dim)).astype(np.float32) for _ in range(n_docs)]
    docs_tids = [rng.integers(0, vt, size=12) for _ in range(n_docs)]
    split = int(0.8 * n_docs)
    train_res_docs = docs_res[:split]
    test_res_docs = docs_res[split:]
    train_tids = docs_tids[:split]
    test_tids = docs_tids[split:]

    def l2n(arr):
        nrm = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-8
        return (arr / nrm).astype(np.float32)
    train_res_n = [l2n(d) for d in train_res_docs]
    test_res_n = [l2n(d) for d in test_res_docs]
    train_res_flat = np.concatenate(train_res_n, axis=0)

    # Synthetic centers (random subset of train residuals)
    rng_vq = np.random.default_rng(rng_seed + 5000)
    centers_idx = rng_vq.choice(len(train_res_flat),
                                size=min(vc, len(train_res_flat)), replace=False)
    centers = train_res_flat[centers_idx].copy()

    def hard_assign(seq_list):
        flat = np.concatenate(seq_list, axis=0)
        sims = flat @ centers.T
        return np.argmax(sims, axis=1).astype(np.int64)

    train_cids = hard_assign(train_res_n)
    test_cids = hard_assign(test_res_n)

    rng2 = np.random.default_rng(rng_seed + 1000)
    C = sparse_codebook(vc, n_dim, f, rng2)

    # Build D: hard one-hot writes per token
    D = np.zeros((n_dim, vt), dtype=np.float32)
    concept_tok_counts: Dict[int, np.ndarray] = {}
    offset = 0
    for d_idx, t_doc in enumerate(train_tids):
        n_doc = len(train_res_docs[d_idx])
        for pos in range(n_doc):
            tok = int(t_doc[pos])
            if tok < vt:
                ci = int(train_cids[offset + pos])
                D[:, tok] += C[ci] * LR_DECODE
                if ci not in concept_tok_counts:
                    concept_tok_counts[ci] = np.zeros(vt, dtype=np.int64)
                concept_tok_counts[ci][tok] += 1
        offset += n_doc

    uni_tok = np.zeros(vt, dtype=np.int64)
    for t_doc in train_tids:
        for pos in range(len(t_doc) - 1):
            tt1 = int(t_doc[pos + 1])
            if tt1 < vt:
                uni_tok[tt1] += 1
    uni_dist = uni_tok.astype(np.float32) + 1e-6
    uni_dist /= uni_dist.sum()
    uni_log = np.log(uni_dist + 1e-300)

    # Transitions
    P_src_list, P_dst_list = [], []
    offset_train = 0
    for d_idx in range(len(train_res_docs)):
        n_doc = len(train_res_docs[d_idx])
        cids_doc = train_cids[offset_train:offset_train + n_doc]
        ctx_vecs = build_context_vecs_batched(C, cids_doc.astype(np.int64),
                                              K_depth=1, n_dim=n_dim)
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
    tot_t = 0
    sub_nll = ceil_nll = uni_nll = 0.0
    sub_t_ok = 0
    log2 = math.log(2)
    offset_test = 0
    for d_idx in range(len(test_res_docs)):
        n_doc = len(test_res_docs[d_idx])
        cids_doc = test_cids[offset_test:offset_test + n_doc].astype(np.int64)
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

    # --- T1: sparse_codebook shape + k_active correct ---
    vc_t, n_t = 16, 64
    C_t = sparse_codebook(vc_t, n_t, 0.05, rng)
    assert C_t.shape == (vc_t, n_t), "sparse_codebook shape FAIL"
    k_act_t = max(1, round(0.05 * n_t))
    for i in range(vc_t):
        assert int((C_t[i] != 0).sum()) == k_act_t, "codebook k-active mismatch"
    print("[selftest] T1 PASS: sparse_codebook shape + k-active correct", flush=True)

    # --- T2: build_W / batched_concept_recall ---
    rng2 = np.random.default_rng(888)
    vc_sm, n_sm, vt_sm = 8, 32, 10
    C_sm = sparse_codebook(vc_sm, n_sm, 0.1, rng2)
    P_s = np.array([C_sm[i] for i in range(5)], dtype=np.float32)
    P_d = np.array([C_sm[(i + 1) % vc_sm] for i in range(5)], dtype=np.float32)
    W_sm = build_W(P_s, P_d)
    assert W_sm.shape == (n_sm, n_sm), "build_W shape FAIL"
    pred = batched_concept_recall(W_sm, C_sm[0:1], C_sm)
    assert int(pred[0]) == 1, "concept recall FAIL: expected 1, got %d" % int(pred[0])
    print("[selftest] T2 PASS: substrate ops (build_W + recall)", flush=True)

    # --- T3: batched vs per-query token_logprob ---
    D_sm = np.zeros((n_sm, vt_sm), dtype=np.float32)
    for _ in range(5):
        D_sm[:, 7] += C_sm[3] * LR_DECODE
    lp_perq = token_logprob(D_sm, C_sm[3])
    lp_batch = batched_token_logprob(D_sm, C_sm[3:4])
    max_diff = float(np.abs(lp_perq - lp_batch[0]).max())
    assert max_diff < 1e-5, "batched_token_logprob != per-query: diff=%.2e" % max_diff
    print("[selftest] T3 PASS: batched vs per-query token_logprob match", flush=True)

    # --- T4: zero-D-overlap fallback (Fix #6) ---
    D_zero = np.zeros((n_sm, vt_sm), dtype=np.float32)
    code_v = C_sm[0:1].copy()
    lp_zero = batched_token_logprob(D_zero, code_v)
    probs = np.exp(lp_zero[0])
    assert float(np.abs(probs - 1.0 / vt_sm).max()) < 1e-5, "zero-D-overlap fallback NOT uniform"
    assert not np.isnan(lp_zero).any(), "zero-D-overlap produced NaN logprob"
    print("[selftest] T4 PASS: zero-D-overlap fallback -> uniform (Fix #6)", flush=True)

    # --- T5: synthetic end-to-end produces finite BPC ---
    res_e2e = _run_synthetic(rng_seed=42, n_dim=64, f=0.05, vc=8, vt=20, residual_dim=32)
    assert res_e2e is not None, "synthetic run returned None"
    for key in ("substrate_bpc", "ceiling_bpc", "unigram_bpc"):
        val = res_e2e.get(key)
        assert val is not None, "metric %s is None" % key
        assert not math.isnan(val), "metric %s is NaN" % key
    assert res_e2e["substrate_bpc"] > 0.0, "substrate_bpc zero"
    assert res_e2e["ceiling_bpc"] > 0.0, "ceiling_bpc zero"
    print("[selftest] T5 PASS: synthetic end-to-end produces finite BPC", flush=True)

    # --- T6: LLM-call counter remains at 0 ---
    assert _LLM_CALL_COUNTER[0] == 0, "LLM_CALL_COUNTER non-zero -- substrate-only-gate VIOLATED"
    print("[selftest] T6 PASS: LLM_CALL_COUNTER = 0 (substrate-only-gate auditable)", flush=True)

    # --- T7: module-level constants are REAL CODE (AST-verifiable types) ---
    assert isinstance(ANCHOR_NAME, str) and len(ANCHOR_NAME) > 0, "ANCHOR_NAME not a str"
    assert isinstance(CONFIG_VERSION, str), "CONFIG_VERSION not a str"
    assert "VC_GRID=" in CONFIG_VERSION, "CONFIG_VERSION missing VC_GRID label"
    assert "N_GRID=" in CONFIG_VERSION, "CONFIG_VERSION missing N_GRID label"
    assert "ASSIGN=km_predict_n2_baseline" in CONFIG_VERSION, (
        "CONFIG_VERSION missing N2-baseline assignment marker")
    assert "anchor-fix-N2-baseline-reproduction-gate" in CONFIG_VERSION, (
        "CONFIG_VERSION missing v2 anchor-fix marker")
    assert isinstance(VC_GRID, list) and len(VC_GRID) >= 1, "VC_GRID not a non-empty list"
    assert isinstance(N_GRID, list) and len(N_GRID) >= 1, "N_GRID not a non-empty list"
    assert isinstance(K, int) and K == 1, "K not 1 (fixed config; clean V_C-alone discriminator)"
    assert isinstance(F_SPARSE, float) and 0 < F_SPARSE < 1, "F_SPARSE not in (0,1)"
    assert isinstance(LAM_BACKOFF, float) and 0 < LAM_BACKOFF < 1, "LAM_BACKOFF not in (0,1)"
    assert isinstance(RESIDUAL_DIM, int) and RESIDUAL_DIM == 768, "RESIDUAL_DIM not 768"
    print("[selftest] T7 PASS: module-level constants + AST-verifiable types", flush=True)

    # --- T8: VC_GRID has 1024 (anchor) AND a value > 1024 (frontier) ---
    if RUN_MODE != "smoke":
        assert 1024 in VC_GRID, "VC_GRID missing 1024 anchor: %s" % VC_GRID
    has_frontier = any(v > 1024 for v in VC_GRID)
    assert has_frontier, "VC_GRID lacks V_C>1024 frontier arm: %s" % VC_GRID
    for vc_v in VC_GRID:
        assert 1 <= vc_v <= MAX_VC, "VC_GRID entry %d out of range [1, %d]" % (vc_v, MAX_VC)
    print("[selftest] T8 PASS: VC_GRID has anchor + frontier arms", flush=True)

    # --- T9: N_GRID has 16384 (anchor N) and all in sane range ---
    if RUN_MODE != "smoke":
        assert 16384 in N_GRID, "N_GRID missing 16384 anchor: %s" % N_GRID
    for n_v in N_GRID:
        assert 256 <= n_v <= 131072, "N_GRID entry %d out of range" % n_v
    print("[selftest] T9 PASS: N_GRID has 16384 anchor; all in sane range", flush=True)

    # --- T10: per_unit dict shape (chain-grade per_unit blocker) ---
    per_unit_keys_required = (
        "seed", "v_c", "n_dim", "k", "f_sparse", "assignment_mode",
        "substrate_bpc", "ceiling_bpc", "bigram_bpc", "unigram_bpc",
        "substrate_top1", "ceiling_top1", "codebook_utilization", "alpha",
        "llm_forward_calls_at_inference", "wall_s",
    )
    fake_unit = {k: (0 if k in ("seed", "v_c", "n_dim", "k", "llm_forward_calls_at_inference")
                     else ("km_predict_n2_baseline" if k == "assignment_mode" else 0.0))
                 for k in per_unit_keys_required}
    for key in per_unit_keys_required:
        assert key in fake_unit, "per_unit missing required key: %s" % key
    print("[selftest] T10 PASS: per_unit shape includes all required keys", flush=True)

    # --- T11: anchor pre-gate band is tight (+/-0.02 vs v1's +/-0.10) ---
    assert 0.0 < ANCHOR_PREGATE_TOLERANCE < 0.10, (
        "ANCHOR_PREGATE_TOLERANCE %.3f outside (0, 0.10) -- must be tightened vs v1"
        % ANCHOR_PREGATE_TOLERANCE)
    assert ANCHOR_PREGATE_LOW < N2_ANCHOR_SUBSTRATE_BPC < ANCHOR_PREGATE_HIGH, (
        "pre-gate band does not bracket N2 anchor")
    assert N2_ANCHOR_SUBSTRATE_BPC == 4.959, (
        "N2_ANCHOR_SUBSTRATE_BPC drifted from documented 4.959")
    print("[selftest] T11 PASS: anchor pre-gate band [%.3f, %.3f] tight (+/- %.3f)" % (
        ANCHOR_PREGATE_LOW, ANCHOR_PREGATE_HIGH, ANCHOR_PREGATE_TOLERANCE), flush=True)

    # --- T12: pre-reg bands sane ---
    assert HARD_PASS_THRESHOLD < N2_ANCHOR_SUBSTRATE_BPC, (
        "HARD_PASS threshold %.3f must beat N2 anchor %.3f" % (
            HARD_PASS_THRESHOLD, N2_ANCHOR_SUBSTRATE_BPC))
    assert HARD_PASS_MARGIN > 0, "HARD_PASS margin must be positive"
    assert abs(HARD_PASS_THRESHOLD - (N2_ANCHOR_SUBSTRATE_BPC - HARD_PASS_MARGIN)) < 1e-9, (
        "HARD_PASS_THRESHOLD inconsistent with N2 anchor - margin")
    print("[selftest] T12 PASS: pre-reg bands sane (HARD_PASS<=%.3f; margin=%.2f)" % (
        HARD_PASS_THRESHOLD, HARD_PASS_MARGIN), flush=True)

    # --- T13: codebook_rng_seed matches N2 baseline at V_C=1024 ---
    # N2 baseline: rng2 = default_rng(seed + 1000 + n_dim_idx * 100)
    for (s, n_idx) in [(7, 0), (7, 1), (17, 2), (23, 0)]:
        expected_n2 = s + 1000 + n_idx * 100
        actual = codebook_rng_seed(s, n_idx, vc=1024)
        assert actual == expected_n2, (
            "codebook_rng_seed(seed=%d, n_idx=%d, vc=1024) = %d != N2 expected %d" % (
                s, n_idx, actual, expected_n2))
    # V_C=4096 must be disjoint
    for (s, n_idx) in [(7, 0), (17, 2)]:
        seed_1k = codebook_rng_seed(s, n_idx, vc=1024)
        seed_4k = codebook_rng_seed(s, n_idx, vc=4096)
        assert seed_4k != seed_1k, (
            "V_C=4096 RNG seed must differ from V_C=1024 at same (seed, n_idx)")
    print("[selftest] T13 PASS: codebook_rng_seed matches N2 at V_C=1024; V_C=4096 disjoint",
          flush=True)

    print("[selftest] ALL 13 TESTS PASS: n5 v2 anchor-fix cell instrumentation validated",
          flush=True)


_instrumentation_selftest()  # MANDATORY at module scope
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
            "token_ids key NOT present in residuals_per_token.npz."
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
# Per-arm evaluation (factored out so the anchor pre-gate can call it first)
# ---------------------------------------------------------------------------

def _eval_one_arm(seed: int, vc: int, n_dim: int, n_dim_idx: int, f: float,
                  train_seqs, test_cids_per_doc, test_docs,
                  train_cids, V_TOK, tot_t_global,
                  valid_idx_global, true_tok_valid_global,
                  uni_dist, uni_log, uni_tok_pred,
                  big_bpc_global, uni_bpc_global,
                  utilization, km_available, km_wall) -> Dict[str, Any]:
    """Evaluate one (V_C, N_DIM) arm; return per_unit dict.

    Pure compute on already-assigned cids -- both pre-gate anchor and main
    sweep go through here. Uses N2-style codebook RNG seed.
    """
    log2 = math.log(2)
    t_arm = time.time()

    # Sparse concept codebook (N2-style RNG seed for V_C=1024 byte-reproduction)
    rng_seed_C = codebook_rng_seed(seed, n_dim_idx, vc)
    rng2 = np.random.default_rng(rng_seed_C)
    C = sparse_codebook(vc, n_dim, f, rng2)
    k_act = max(1, round(f * n_dim))

    # Build D: hard one-hot writes per token
    D = np.zeros((n_dim, V_TOK), dtype=np.float32)
    concept_tok_counts: Dict[int, np.ndarray] = {}
    for cids_doc, tids_doc in train_seqs:
        for t_pos in range(len(cids_doc)):
            tok = int(tids_doc[t_pos])
            if tok < V_TOK:
                ci = int(cids_doc[t_pos])
                D[:, tok] += C[ci] * LR_DECODE
                if ci not in concept_tok_counts:
                    concept_tok_counts[ci] = np.zeros(V_TOK, dtype=np.int64)
                concept_tok_counts[ci][tok] += 1
    ceiling_pred = {c: int(np.argmax(v)) for c, v in concept_tok_counts.items()}

    # Saturation alpha
    unique_ctx_pairs = len(set(zip(train_cids[:-1].tolist(), train_cids[1:].tolist())))
    alpha = unique_ctx_pairs / n_dim
    saturated = (alpha > 1.0)

    # Build transition store
    P_src_list, P_dst_list = [], []
    for cids_doc, _ in train_seqs:
        if len(cids_doc) < 2:
            continue
        ctx_vecs = build_context_vecs_batched(C, cids_doc, K_depth=K, n_dim=n_dim)
        if ctx_vecs.shape[0] == 0:
            continue
        P_src_list.append(ctx_vecs)
        P_dst_list.append(np.array(
            [C[int(cids_doc[t_pos + 1])] for t_pos in range(ctx_vecs.shape[0])],
            dtype=np.float32))

    if not P_src_list:
        return {
            "seed": seed, "v_c": vc, "n_dim": n_dim, "k": K,
            "f_sparse": f, "assignment_mode": "km_predict_n2_baseline",
            "substrate_bpc": float("nan"), "ceiling_bpc": float("nan"),
            "bigram_bpc": big_bpc_global, "unigram_bpc": uni_bpc_global,
            "substrate_top1": float("nan"), "ceiling_top1": float("nan"),
            "codebook_utilization": utilization,
            "alpha": alpha, "saturated": saturated,
            "is_anchor_arm": (vc == 1024 and n_dim == 16384),
            "k_active": k_act,
            "km_available": km_available, "km_wall_s": km_wall,
            "n_trans": 0, "n_token_test_pairs": tot_t_global,
            "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "wall_s": time.time() - t_arm,
            "corpus_provenance_real": True,
            "allow_synthetic": False,
            "codebook_rng_seed": rng_seed_C,
        }

    P_src = np.concatenate(P_src_list, axis=0)
    P_dst = np.concatenate(P_dst_list, axis=0)
    n_trans = P_src.shape[0]
    print("[seed=%d V_C=%d N=%d] n_trans=%d alpha=%.3f%s building W (%dx%d)..." % (
        seed, vc, n_dim, n_trans, alpha, " [SAT]" if saturated else "",
        n_dim, n_dim), flush=True)
    W_a = build_W(P_src, P_dst)
    del P_src, P_dst

    # Build context vecs for all test positions
    _c_src_list, _c_tgt_list = [], []
    for i_doc, cids_arr in enumerate(test_cids_per_doc):
        if cids_arr.shape[0] == 0:
            continue
        ctx_vecs = build_context_vecs_batched(C, cids_arr, K_depth=K, n_dim=n_dim)
        n_pos = ctx_vecs.shape[0]
        if n_pos == 0:
            continue
        _c_src_list.append(ctx_vecs)
        _c_tgt_list.extend(cids_arr[1:n_pos + 1].tolist())

    if not _c_src_list:
        return {
            "seed": seed, "v_c": vc, "n_dim": n_dim, "k": K,
            "f_sparse": f, "assignment_mode": "km_predict_n2_baseline",
            "substrate_bpc": float("nan"), "ceiling_bpc": float("nan"),
            "bigram_bpc": big_bpc_global, "unigram_bpc": uni_bpc_global,
            "substrate_top1": float("nan"), "ceiling_top1": float("nan"),
            "codebook_utilization": utilization,
            "alpha": alpha, "saturated": saturated,
            "is_anchor_arm": (vc == 1024 and n_dim == 16384),
            "k_active": k_act,
            "km_available": km_available, "km_wall_s": km_wall,
            "n_trans": n_trans, "n_token_test_pairs": 0,
            "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "wall_s": time.time() - t_arm,
            "corpus_provenance_real": True,
            "allow_synthetic": False,
            "codebook_rng_seed": rng_seed_C,
        }

    Q_all = np.concatenate(_c_src_list, axis=0)
    c_tgt_all = np.array(_c_tgt_list, dtype=np.int64)
    tot_c = len(c_tgt_all)

    print("[seed=%d V_C=%d N=%d] batched recall: %d queries..." % (
        seed, vc, n_dim, tot_c), flush=True)
    pred_concept_all = batched_concept_recall(W_a, Q_all, C)
    del Q_all

    sub_c_ok = int((pred_concept_all == c_tgt_all).sum())

    # Token-level eval
    pred_c_valid = pred_concept_all[valid_idx_global]
    c_tgt_valid = c_tgt_all[valid_idx_global]

    BATCH_TOK_CHUNK = 2000
    n_valid = tot_t_global
    pred_tok_valid = np.empty(n_valid, dtype=np.int64)
    true_tok_logprob = np.empty(n_valid, dtype=np.float64)

    print("[seed=%d V_C=%d N=%d] batched token decode: %d positions..." % (
        seed, vc, n_dim, n_valid), flush=True)
    for _ck_s in range(0, n_valid, BATCH_TOK_CHUNK):
        _ck_e = min(_ck_s + BATCH_TOK_CHUNK, n_valid)
        _cvecs = C[pred_c_valid[_ck_s:_ck_e]]
        _lp = batched_token_logprob(D, _cvecs, uni_dist, LAM_BACKOFF)
        pred_tok_valid[_ck_s:_ck_e] = np.argmax(_lp, axis=1)
        _tt = true_tok_valid_global[_ck_s:_ck_e]
        true_tok_logprob[_ck_s:_ck_e] = _lp[np.arange(_ck_e - _ck_s), _tt]

    sub_t_ok = int((pred_tok_valid == true_tok_valid_global).sum())
    sub_nll = float(-true_tok_logprob.sum())

    ceil_t_ok = 0
    ceil_nll = 0.0
    for _i in range(n_valid):
        _ctgt = int(c_tgt_valid[_i])
        _tt = int(true_tok_valid_global[_i])
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
        "v_c": vc,
        "n_dim": n_dim,
        "k": K,
        "f_sparse": f,
        "assignment_mode": "km_predict_n2_baseline",
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
        "is_anchor_arm": (vc == 1024 and n_dim == 16384),
        "k_active": k_act,
        "km_available": km_available,
        "km_wall_s": km_wall,
        "n_trans": n_trans,
        "n_token_test_pairs": tot_t_global,
        "n_concept_test_pairs": tot_c,
        "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "wall_s": time.time() - t_arm,
        "corpus_provenance_real": True,
        "allow_synthetic": False,
        "codebook_rng_seed": rng_seed_C,
    }

    print("  [seed=%d V_C=%d N=%d] sub_bpc=%.3f ceiling_bpc=%.3f bigram=%.3f "
          "concept_top1=%.3f util=%.1f%% alpha=%.3f km_wall=%.1fs wall=%.1fs%s%s" % (
              seed, vc, n_dim, sub_bpc, ceiling_bpc, big_bpc_global,
              per_unit["substrate_concept_top1"], utilization * 100, alpha,
              km_wall, per_unit["wall_s"],
              " [ANCHOR]" if per_unit["is_anchor_arm"] else "",
              " [SAT]" if saturated else ""), flush=True)
    return per_unit


# ---------------------------------------------------------------------------
# Per-seed run: anchor pre-gate FIRST, then (V_C, N_DIM) sweep at fixed K=1
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    """Per-seed pipeline: anchor pre-gate FIRST, then full sweep.

    On pre-gate FAIL: skip the V_C=4096 arms, return per_unit list containing
    only the anchor arm with anchor_pregate_failed=True so the verdict()
    function can emit HARD_FAIL_HARNESS_DRIFT.
    """
    t0 = time.time()
    f = F_SPARSE

    res, bnd, tids = load_data()
    docs = build_docs(res, bnd, tids, MAX_DOCS)
    print("[seed=%d] loaded %d docs, V_C_GRID=%s N_GRID=%s K=%d" % (
        seed, len(docs), VC_GRID, N_GRID, K), flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(docs)).tolist()
    docs = [docs[i] for i in perm]
    split = int(TRAIN_FRAC * len(docs))
    train_docs = docs[:split]
    test_docs = docs[split:]

    log2 = math.log(2)

    # Train residuals: L2-normalize once
    train_res_full = np.concatenate([d[0] for d in train_docs], axis=0)
    norms_tr = np.linalg.norm(train_res_full, axis=1, keepdims=True) + 1e-8
    train_res_n = train_res_full / norms_tr
    print("[seed=%d] train residuals: %d tokens, residual_dim=%d" % (
        seed, len(train_res_n), train_res_n.shape[1]), flush=True)

    # Token vocab
    all_train_tids = np.concatenate([d[1] for d in train_docs])
    V_TOK = min(int(all_train_tids.max()) + 1, MAX_TOK_VOCAB)
    print("[seed=%d] V_TOK=%d" % (seed, V_TOK), flush=True)

    # Bigram + unigram baselines (V_C / N_DIM independent)
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

    # Precompute test position arrays (V_C / N_DIM independent for bigram/unigram BPC)
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

    # Unigram + bigram BPC
    if tot_t_global > 0:
        uni_nll_global = float(-uni_log[true_tok_valid_global].sum())
        uni_bpc_global = (uni_nll_global / tot_t_global) / log2
        big_nll_global = 0.0
        big_t_ok_global = 0
        for _i in range(tot_t_global):
            _ts = int(t_src_tok_valid_global[_i])
            _tt = int(true_tok_valid_global[_i])
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

    per_unit_list: List[Dict[str, Any]] = []
    anchor_pregate_status = "NOT_RUN"
    anchor_pregate_sub_bpc = float("nan")

    # =========================================================================
    # CACHE per-VC: fit km ONCE per VC, share across N_DIM arms.
    # Phase 1 = run the anchor arm (V_C=1024, N=16384) FIRST and gate.
    # =========================================================================

    km_cache: Dict[int, Tuple[Any, np.ndarray, np.ndarray, bool, float, float]] = {}
    # vc -> (km, train_cids, test_cids_concat, km_available, km_wall, utilization)
    test_doc_lengths = [d[0].shape[0] for d in test_docs]

    def get_vc_fit(vc: int):
        """Fit km + assign cids (train + per-test-doc) using N2-baseline pipeline.
        Cached per VC across the N_DIM sweep."""
        if vc in km_cache:
            return km_cache[vc]
        print("[seed=%d V_C=%d] fitting MiniBatchKMeans on %d train tokens (N2-baseline)..." % (
            seed, vc, len(train_res_n)), flush=True)
        t_km0 = time.time()
        try:
            from sklearn.cluster import MiniBatchKMeans
            km = MiniBatchKMeans(n_clusters=vc, random_state=seed,
                                 batch_size=4096, n_init=3, max_iter=100, verbose=0)
            km.fit(train_res_n)
            km_available = True
        except ImportError:
            print("[seed=%d V_C=%d] sklearn unavailable -- numpy random-center VQ" % (seed, vc),
                  flush=True)
            km = None
            km_available = False
        km_wall = time.time() - t_km0
        print("[seed=%d V_C=%d] kmeans fit wall=%.1fs (km_available=%s)" % (
            seed, vc, km_wall, km_available), flush=True)

        # N2-VERBATIM assignment: km.predict on L2-normalized residuals.
        # NO additional center L2-normalization step. NO cosine-sim argmax.
        if km is not None:
            train_cids = km.predict(train_res_n).astype(np.int64)
            # Assign test cids per-doc (so we keep doc structure)
            test_cids_per_doc = []
            for d in test_docs:
                tn = d[0]
                nrm = np.linalg.norm(tn, axis=1, keepdims=True) + 1e-8
                tn_n = tn / nrm
                if tn_n.shape[0] > 0:
                    test_cids_per_doc.append(km.predict(tn_n).astype(np.int64))
                else:
                    test_cids_per_doc.append(np.zeros((0,), dtype=np.int64))
        else:
            # Fallback numpy random-center VQ (rare; sklearn always available on remote)
            rng_vq = np.random.default_rng(seed + 5000)
            centers_idx = rng_vq.choice(len(train_res_n), size=vc, replace=False)
            centers_fallback = train_res_n[centers_idx].copy()
            # Match N2 fallback: euclidean nearest-center on l2-normalized residuals
            def _assign_fallback(arr_n: np.ndarray) -> np.ndarray:
                chunk = 4096
                out = np.empty(len(arr_n), dtype=np.int64)
                for s_pos in range(0, len(arr_n), chunk):
                    e_pos = s_pos + chunk
                    diff = arr_n[s_pos:e_pos, None, :] - centers_fallback[None, :, :]
                    out[s_pos:e_pos] = np.argmin((diff ** 2).sum(-1), axis=1)
                return out
            train_cids = _assign_fallback(train_res_n)
            test_cids_per_doc = []
            for d in test_docs:
                tn = d[0]
                nrm = np.linalg.norm(tn, axis=1, keepdims=True) + 1e-8
                tn_n = tn / nrm
                if tn_n.shape[0] > 0:
                    test_cids_per_doc.append(_assign_fallback(tn_n))
                else:
                    test_cids_per_doc.append(np.zeros((0,), dtype=np.int64))

        unique_cids_train = np.unique(train_cids)
        utilization = len(unique_cids_train) / vc
        if utilization < 0.5:
            print("[seed=%d V_C=%d] WARNING: VQ low utilization %.0f%% (collapse?)" % (
                seed, vc, utilization * 100), flush=True)

        km_cache[vc] = (km, train_cids, test_cids_per_doc, km_available, km_wall, utilization)
        return km_cache[vc]

    def build_train_seqs(cids_flat: np.ndarray):
        """Slice train_cids back into per-doc tuples (cids_doc, tids_doc)."""
        seqs = []
        offset = 0
        for doc_res, doc_tok in train_docs:
            n_doc = len(doc_res)
            seqs.append((cids_flat[offset:offset + n_doc], doc_tok))
            offset += n_doc
        return seqs

    # ------------------------------------------------------------------
    # PHASE 1: ANCHOR PRE-GATE (V_C=1024, N=16384)
    # ------------------------------------------------------------------
    anchor_idx_in_n_grid = N_GRID.index(16384) if 16384 in N_GRID else 0
    if 1024 in VC_GRID and 16384 in N_GRID:
        print("\n[ANCHOR-PRE-GATE seed=%d] running V_C=1024/N=16384 first; "
              "gate band=[%.3f, %.3f] (N2 %.3f +/- %.3f)" % (
                  seed, ANCHOR_PREGATE_LOW, ANCHOR_PREGATE_HIGH,
                  N2_ANCHOR_SUBSTRATE_BPC, ANCHOR_PREGATE_TOLERANCE), flush=True)

        km, train_cids, test_cids_per_doc, km_available, km_wall, utilization = get_vc_fit(1024)
        train_seqs = build_train_seqs(train_cids)
        anchor_unit = _eval_one_arm(
            seed=seed, vc=1024, n_dim=16384, n_dim_idx=anchor_idx_in_n_grid, f=f,
            train_seqs=train_seqs, test_cids_per_doc=test_cids_per_doc, test_docs=test_docs,
            train_cids=train_cids, V_TOK=V_TOK, tot_t_global=tot_t_global,
            valid_idx_global=valid_idx_global, true_tok_valid_global=true_tok_valid_global,
            uni_dist=uni_dist, uni_log=uni_log, uni_tok_pred=uni_tok_pred,
            big_bpc_global=big_bpc_global, uni_bpc_global=uni_bpc_global,
            utilization=utilization, km_available=km_available, km_wall=km_wall,
        )
        anchor_unit["pregate_arm"] = True
        per_unit_list.append(anchor_unit)
        anchor_pregate_sub_bpc = float(anchor_unit.get("substrate_bpc", float("nan")))

        # Gate check
        if math.isnan(anchor_pregate_sub_bpc):
            anchor_pregate_status = "FAIL_NAN"
        elif ANCHOR_PREGATE_LOW <= anchor_pregate_sub_bpc <= ANCHOR_PREGATE_HIGH:
            anchor_pregate_status = "PASS"
            print("[ANCHOR-PRE-GATE seed=%d] PASS: sub_bpc=%.3f in [%.3f, %.3f]" % (
                seed, anchor_pregate_sub_bpc, ANCHOR_PREGATE_LOW, ANCHOR_PREGATE_HIGH),
                flush=True)
        else:
            anchor_pregate_status = "FAIL_DRIFT"
            print("[ANCHOR-PRE-GATE seed=%d] FAIL_DRIFT: sub_bpc=%.3f NOT in [%.3f, %.3f] "
                  "(N2=%.3f); ABORTING V_C=4096 sweep -- saves ~90min compute" % (
                      seed, anchor_pregate_sub_bpc, ANCHOR_PREGATE_LOW,
                      ANCHOR_PREGATE_HIGH, N2_ANCHOR_SUBSTRATE_BPC), flush=True)

    else:
        # In smoke mode we may not have the anchor arm in the grid; allow pass-through
        anchor_pregate_status = "SKIPPED_NOT_IN_GRID"

    # ------------------------------------------------------------------
    # PHASE 2: full sweep (skipped if pre-gate FAIL_DRIFT in full mode)
    # ------------------------------------------------------------------
    skip_sweep = (anchor_pregate_status in ("FAIL_DRIFT", "FAIL_NAN") and RUN_MODE == "full")

    if skip_sweep:
        print("[seed=%d] SKIPPING V_C=4096 sweep due to ANCHOR-PRE-GATE %s" % (
            seed, anchor_pregate_status), flush=True)
    else:
        for vc in VC_GRID:
            for n_dim_idx, n_dim in enumerate(N_GRID):
                # Skip the anchor arm we already ran in pregate
                if vc == 1024 and n_dim == 16384 and any(
                        u.get("pregate_arm", False) and u["v_c"] == 1024 and u["n_dim"] == 16384
                        for u in per_unit_list):
                    continue
                km, train_cids, test_cids_per_doc, km_available, km_wall, utilization = get_vc_fit(vc)
                train_seqs = build_train_seqs(train_cids)
                unit = _eval_one_arm(
                    seed=seed, vc=vc, n_dim=n_dim, n_dim_idx=n_dim_idx, f=f,
                    train_seqs=train_seqs, test_cids_per_doc=test_cids_per_doc,
                    test_docs=test_docs,
                    train_cids=train_cids, V_TOK=V_TOK, tot_t_global=tot_t_global,
                    valid_idx_global=valid_idx_global,
                    true_tok_valid_global=true_tok_valid_global,
                    uni_dist=uni_dist, uni_log=uni_log, uni_tok_pred=uni_tok_pred,
                    big_bpc_global=big_bpc_global, uni_bpc_global=uni_bpc_global,
                    utilization=utilization, km_available=km_available, km_wall=km_wall,
                )
                per_unit_list.append(unit)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "per_unit": per_unit_list,
        "K": K,
        "f_sparse": f,
        "assignment_mode": "km_predict_n2_baseline",
        "V_TOK": V_TOK,
        "n_docs": len(train_docs) + len(test_docs),
        "n_train_docs": len(train_docs),
        "n_test_docs": len(test_docs),
        "run_mode": RUN_MODE,
        "vc_grid": VC_GRID,
        "n_grid": N_GRID,
        "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "elapsed_s": elapsed,
        "anchor_pregate_status": anchor_pregate_status,
        "anchor_pregate_sub_bpc": anchor_pregate_sub_bpc,
        "anchor_pregate_band_low": ANCHOR_PREGATE_LOW,
        "anchor_pregate_band_high": ANCHOR_PREGATE_HIGH,
        "n2_anchor_substrate_bpc": N2_ANCHOR_SUBSTRATE_BPC,
    }


# ---------------------------------------------------------------------------
# Verdict (pre-registered bands per task spec)
# ---------------------------------------------------------------------------

def _flatten_per_unit(ps: List[Dict[str, Any]]) -> Dict[Tuple[int, int], List[Dict[str, Any]]]:
    """Group per_unit entries by (V_C, N_DIM) across seeds."""
    by_cfg: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}
    for p in ps:
        for u in p.get("per_unit", []):
            key = (int(u["v_c"]), int(u["n_dim"]))
            by_cfg.setdefault(key, []).append(u)
    return by_cfg


def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Compute verdict against pre-registered bands.

    GATE 0: anchor pre-gate -- ANY seed with FAIL_DRIFT -> HARD_FAIL_HARNESS_DRIFT.
    GATE 1: run_mode = "full" (Fix #5).
    GATE 2: zero LLM calls.
    Then HARD_PASS / MIDDLE_BAND / HARD_FAIL per substrate_bpc bands.
    """
    by_cfg = _flatten_per_unit(ps)

    if not by_cfg:
        return ("HARD_FAIL", "HARD_FAIL: no per_unit data; cell produced no results.")

    # GATE 1: run_mode (Fix #5)
    run_modes = set()
    for p in ps:
        run_modes.add(p.get("run_mode", "unknown"))
    if run_modes != {"full"}:
        if run_modes == {"smoke"}:
            smoke_msg = " [SMOKE: non-binding verdict; full run required for chain-grade]"
        else:
            return ("HARD_FAIL",
                    "HARD_FAIL: run_mode mismatch (Fix #5 pre-flight gate): "
                    "expected uniform 'full' but got run_modes=%s." % sorted(run_modes))
    else:
        smoke_msg = ""

    # GATE 0: ANCHOR PRE-GATE
    pregate_statuses = [p.get("anchor_pregate_status", "NOT_RUN") for p in ps]
    pregate_subs = [p.get("anchor_pregate_sub_bpc", float("nan")) for p in ps]
    any_fail_drift = any(s in ("FAIL_DRIFT", "FAIL_NAN") for s in pregate_statuses)
    if any_fail_drift and RUN_MODE == "full":
        msg_parts = []
        for p in ps:
            msg_parts.append("seed=%d pregate_status=%s anchor_sub=%.3f" % (
                p.get("seed", -1),
                p.get("anchor_pregate_status", "?"),
                p.get("anchor_pregate_sub_bpc", float("nan"))))
        return ("HARD_FAIL",
                "HARD_FAIL_HARNESS_DRIFT: V_C=1024/N=16384 anchor pre-gate failed in "
                "[%.3f, %.3f] (N2 %.3f +/- %.3f). "
                "Comparison V_C=4096-vs-V_C=1024 INVALIDATED -- the V_C=1024 baseline "
                "does not reproduce N2 within tolerance. Per-seed: %s%s" % (
                    ANCHOR_PREGATE_LOW, ANCHOR_PREGATE_HIGH,
                    N2_ANCHOR_SUBSTRATE_BPC, ANCHOR_PREGATE_TOLERANCE,
                    " | ".join(msg_parts), smoke_msg))

    # Per-config aggregates
    cfg_stats: Dict[Tuple[int, int], Dict[str, float]] = {}
    for key, units in by_cfg.items():
        cbs = [u["ceiling_bpc"] for u in units if not math.isnan(u.get("ceiling_bpc", float("nan")))]
        sbs = [u["substrate_bpc"] for u in units if not math.isnan(u.get("substrate_bpc", float("nan")))]
        wts = [u.get("wall_s", 0.0) for u in units]
        kmws = [u.get("km_wall_s", 0.0) for u in units]
        cv = 0.0
        if len(sbs) > 1 and abs(float(np.mean(sbs))) > 1e-9:
            cv = float(np.std(sbs)) / abs(float(np.mean(sbs)))
        cfg_stats[key] = {
            "ceiling_bpc_mean": float(np.mean(cbs)) if cbs else float("nan"),
            "substrate_bpc_mean": float(np.mean(sbs)) if sbs else float("nan"),
            "substrate_bpc_cv": cv,
            "ceiling_bpc_cv": (float(np.std(cbs)) / abs(float(np.mean(cbs)))
                              if len(cbs) > 1 and abs(float(np.mean(cbs))) > 1e-9 else 0.0),
            "bigram_bpc_mean": float(np.mean([u.get("bigram_bpc", float("nan")) for u in units
                                              if not math.isnan(u.get("bigram_bpc", float("nan")))])) if any(
                not math.isnan(u.get("bigram_bpc", float("nan"))) for u in units) else float("nan"),
            "wall_s_mean": float(np.mean(wts)) if wts else 0.0,
            "km_wall_s_mean": float(np.mean(kmws)) if kmws else 0.0,
            "n_seeds": len(units),
            "any_saturated": any(u.get("saturated", False) for u in units),
            "any_llm_violation": any(u.get("llm_forward_calls_at_inference", 0) > 0 for u in units),
            "is_anchor_arm": (key == (1024, 16384)),
        }

    # GATE 2: LLM-call gate
    any_llm_viol = any(s["any_llm_violation"] for s in cfg_stats.values())
    if any_llm_viol:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (LLM forward call counter > 0)."
                + smoke_msg)

    # Per-config summary
    cfg_lines = []
    for key in sorted(cfg_stats.keys()):
        s = cfg_stats[key]
        cfg_lines.append(
            "V_C=%d/N=%d%s: sub=%.3f ceil=%.3f cv=%.3f wall=%.1fs km=%.1fs" % (
                key[0], key[1], " [ANCHOR]" if s["is_anchor_arm"] else "",
                s["substrate_bpc_mean"], s["ceiling_bpc_mean"], s["substrate_bpc_cv"],
                s["wall_s_mean"], s["km_wall_s_mean"]))

    # Anchor pre-gate PASS note for summary
    pregate_note = " ANCHOR-PRE-GATE: %s (sub_bpc per seed=%s; band=[%.3f, %.3f])" % (
        "/".join(pregate_statuses),
        "/".join("%.3f" % s if not math.isnan(s) else "NaN" for s in pregate_subs),
        ANCHOR_PREGATE_LOW, ANCHOR_PREGATE_HIGH)

    # Find best V_C=4096 arm
    best_4k = None
    best_4k_sub = float("inf")
    best_4k_cv = 1.0
    for key, s in cfg_stats.items():
        if key[0] != 4096:
            continue
        sb = s["substrate_bpc_mean"]
        if not math.isnan(sb) and sb < best_4k_sub:
            best_4k_sub = sb
            best_4k_cv = s["substrate_bpc_cv"]
            best_4k = key

    # No V_C=4096 arm -> only possible in smoke or skipped-due-to-pregate
    if best_4k is None or best_4k_sub == float("inf"):
        return ("HARD_FAIL",
                "HARD_FAIL: no V_C=4096 arm produced substrate_bpc; cell incomplete." +
                pregate_note + " | " + " | ".join(cfg_lines) + smoke_msg)

    substrate_delta = N2_ANCHOR_SUBSTRATE_BPC - best_4k_sub  # positive = V_C=4096 improves

    summary = (
        "best_V_C=4096=%s best_sub_bpc=%.3f anchor_target=%.3f delta=%.3f cv=%.3f.%s | %s%s" % (
            best_4k,
            best_4k_sub,
            N2_ANCHOR_SUBSTRATE_BPC,
            substrate_delta,
            best_4k_cv,
            pregate_note,
            " | ".join(cfg_lines),
            smoke_msg,
        )
    )

    # Direction-correct check: V_C=4096 strictly better than V_C=1024 at SAME N_DIM
    direction_failed = False
    if 1024 in [k[0] for k in cfg_stats.keys()] and 4096 in [k[0] for k in cfg_stats.keys()]:
        for n_d in [k[1] for k in cfg_stats.keys() if k[0] == 4096]:
            if (1024, n_d) in cfg_stats and (4096, n_d) in cfg_stats:
                s1k = cfg_stats[(1024, n_d)]["substrate_bpc_mean"]
                s4k = cfg_stats[(4096, n_d)]["substrate_bpc_mean"]
                if not math.isnan(s1k) and not math.isnan(s4k):
                    if s4k > s1k + 0.05:
                        direction_failed = True
                        break

    if direction_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: V_C=4096 WORSE than V_C=1024 at same N_DIM "
                "(wrong-direction; pre-reg-direction-must-match-intent). " + summary)

    # HARD_PASS: V_C=4096 best sub_bpc <= 4.859 (N2 4.959 - 0.10 margin)
    if (best_4k_sub <= HARD_PASS_THRESHOLD
            and best_4k_cv <= 0.05
            and not cfg_stats[best_4k]["any_saturated"]):
        plus_tag = ""
        bigram_m = cfg_stats[best_4k]["bigram_bpc_mean"]
        if not math.isnan(bigram_m) and best_4k_sub < bigram_m:
            plus_tag = " HARD_PASS_PLUS(substrate<bigram=%.3f)" % bigram_m
        return ("HARD_PASS",
                "HARD_PASS: V_C=4096 at %s achieves substrate_bpc=%.3f<=%.3f AND cv=%.3f<=0.05 "
                "AND substrate-only-decode (LLM calls=0).%s " % (
                    best_4k, best_4k_sub, HARD_PASS_THRESHOLD, best_4k_cv, plus_tag) + summary)

    # MIDDLE_BAND: substrate_delta in (0, HARD_PASS_MARGIN)
    if best_4k_sub < N2_ANCHOR_SUBSTRATE_BPC:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: V_C=4096 partial mechanism (best_sub=%.3f < N2 anchor %.3f "
                "but > HARD_PASS threshold %.3f). " % (
                    best_4k_sub, N2_ANCHOR_SUBSTRATE_BPC, HARD_PASS_THRESHOLD)
                + summary)

    # HARD_FAIL: V_C=4096 >= N2 anchor (no lift at frontier)
    return ("HARD_FAIL",
            "HARD_FAIL: V_C=4096 frontier does not lift over N2 baseline "
            "(best_sub=%.3f >= N2 anchor %.3f). V_C scaling alone insufficient; "
            "route to k-WTA + V_C joint (n4+V_C composition). " % (
                best_4k_sub, N2_ANCHOR_SUBSTRATE_BPC) + summary)


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s VC_GRID=%s N_GRID=%s K=%d f=%.4f MAX_DOCS=%d seeds=%s" % (
    ANCHOR_NAME, RUN_MODE, VC_GRID, N_GRID, K, F_SPARSE, MAX_DOCS, SEEDS), flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)
print("[config] ANCHOR-PRE-GATE band=[%.3f, %.3f] (N2 %.3f +/- %.3f)" % (
    ANCHOR_PREGATE_LOW, ANCHOR_PREGATE_HIGH,
    N2_ANCHOR_SUBSTRATE_BPC, ANCHOR_PREGATE_TOLERANCE), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "vc_grid": VC_GRID, "n_grid": N_GRID, "K": K,
              "assign_mode": "km_predict_n2_baseline",
              "anchor_pregate_tol": ANCHOR_PREGATE_TOLERANCE}

done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds already complete; running %s" % (
    len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

t_total = time.time()
ps = []

for seed in remaining_seeds:
    r = run_seed(seed)
    ps.append(r)
    write_partial(out_dir, seed, r)
    arm_strs = []
    for u in r["per_unit"]:
        arm_strs.append("V_C=%d/N=%d:sub=%.3f ceil=%.3f wall=%.1fs" % (
            u["v_c"], u["n_dim"], u["substrate_bpc"], u["ceiling_bpc"], u["wall_s"]))
    print("  [seed=%d] PREGATE=%s | %s elapsed=%.1fs llm_calls=%d" % (
        seed, r.get("anchor_pregate_status", "?"),
        " | ".join(arm_strs), r["elapsed_s"],
        r["llm_forward_calls_at_inference"]), flush=True)

if done_seeds:
    agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
    for k, v in agg.items():
        ps.append(v)

if not ps:
    print("[ERROR] no seeds completed; aborting", flush=True)
    sys.exit(1)

# Assert no LLM calls happened during the entire run
total_llm_calls = sum(p.get("llm_forward_calls_at_inference", 0) for p in ps)
assert total_llm_calls == 0, (
    "FATAL: %d LLM forward calls -- substrate-only-decode gate VIOLATED" % total_llm_calls)

v, vmsg = verdict(ps)
print("\n[VERDICT] " + vmsg, flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "config_version": CONFIG_VERSION,
    "verdict": v,
    "verdict_msg": vmsg,
    "summary": vmsg,
    "run_mode": RUN_MODE,
    "n_seeds": len(ps),
    "K": K,
    "f_sparse": F_SPARSE,
    "vc_grid": VC_GRID,
    "n_grid": N_GRID,
    "assignment_mode": "km_predict_n2_baseline",
    "zero_llm_calls_at_inference": True,
    "total_llm_forward_calls_observed": total_llm_calls,
    "corpus_provenance_real": True,
    "allow_synthetic": False,
    "anchor_pregate_band_low": ANCHOR_PREGATE_LOW,
    "anchor_pregate_band_high": ANCHOR_PREGATE_HIGH,
    "anchor_pregate_tolerance": ANCHOR_PREGATE_TOLERANCE,
    "n2_anchor_substrate_bpc": N2_ANCHOR_SUBSTRATE_BPC,
    "hard_pass_threshold": HARD_PASS_THRESHOLD,
    "hard_pass_margin": HARD_PASS_MARGIN,
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
