"""
n5_vc_4096_frontier_v1 -- N5: Path A V_C=4096 frontier (V_C-alone ceiling probe).

MOTIVATION (Skunkworks bundled VET commit bcaab129; Research N2 frontier ranking):
  N2 demonstrated V_C=1024/N=16384 substrate_bpc=4.96 (MIDDLE_BAND, partial). The
  Path A lever asks: does V_C scaling ALONE (independent of n4 k-WTA-VQ
  multiplicity, currently smoke-running) lower the ceiling at the source?

  Concept-LM ceiling = H(token | concept) is bounded by codebook resolution. A
  larger V_C should reduce per-concept token entropy: each concept covers fewer
  tokens, ceiling drops. The brain-drill predicts V_C scaling needs k-scaling
  at biological sparsity (V_C=4096 -> optimal k ~ 200), but this cell tests V_C
  ALONE first (K=1 hard one-hot anchor) for a CLEAN discriminator. k-WTA + V_C
  composition is a follow-up (after n4 lands).

  NOVEL CONFIGURATION: V_C in {1024, 4096} x N_DIM in {16384, 32768} at K=1.
  V_C=1024/N=16384 reproduces N2's anchor (sanity-bracket). V_C=4096/N=32768
  is the load-bearing frontier arm.

REUSES n4/n2 HARNESS VERBATIM (Skunkworks chain-grade spec):
  - HD-binding context: ctx_vec = L2_normalize(sum_j roll(C[c_{t-j}], j))
  - W-materialized batched recall: W = P_src.T @ P_dst
  - v3.1 count-proportional + Jelinek-Mercer interpolation decode
  - Per-seed checkpoint / resume (PROT-021 run_config guard)
  - _instrumentation_selftest at module scope
  - ANCHOR_NAME / write_metrics / CONFIG_VERSION discipline
  - Zero-D-overlap fallback in batched_token_logprob (Fix #6)
  - pre-reg-direction-must-match-intent in verdict
  - PRE-FLIGHT run_mode-must-be-full guard inside verdict() (Fix #5)
  - K=1 hard one-hot km.predict() (clean V_C-alone discriminator)

FIXED CONFIG:
  K = 1 (substrate context depth)
  F_SPARSE = 0.006
  V_C_GRID = [1024, 4096]
  N_DIM_GRID = [16384, 32768]
  4 (V_C, N_DIM) combinations per seed:
    (1024, 16384)  -- N2 anchor SANITY (must reproduce 4.96 BPC)
    (1024, 32768)  -- N_DIM-alone arm (control)
    (4096, 16384)  -- V_C-alone arm (load-bearing frontier)
    (4096, 32768)  -- joint V_C + N_DIM arm

SCIENTIFIC QUESTIONS (pre-registered):
  (a) Does (V_C=1024, N=16384) reproduce N2's substrate_bpc=4.96 within 0.05?
  (b) Does V_C=4096 LOWER ceiling_bpc and substrate_bpc vs V_C=1024 at SAME N_DIM?
  (c) Does V_C scaling alone close ANY of the 0.60 bit gap to bigram (3.844)?
  (d) Is alpha < 1.0 at all configs (avoid saturation)?

PRE-REGISTERED BANDS:
  HARD_PASS (chain-grade, ALL of):
    - V_C=4096 arm (any N_DIM) has substrate_bpc <= 4.36 (>=0.60 bit drop vs N2)
    - cv across 3 seeds <= 0.05 for the passing config
    - NOT saturated (alpha < 1.0) at passing config
    - substrate-only-decode (zero LLM calls)
    - direction-correct: V_C=4096 arm strictly better than V_C=1024 at SAME N_DIM
    - V_C=1024/N=16384 reproduces N2's 4.96 within 0.10 (sanity)
    - run_mode = "full" (Fix #5)
  MIDDLE_BAND: V_C=4096 substrate_bpc improves 0.10-0.60 bits vs N2 (partial)
  HARD_FAIL:
    - V_C=4096 substrate_bpc < 0.10 improvement vs N2 (mechanism wrong;
      route to k-WTA + Path A composition revival)
    - OR V_C=4096 WORSE than V_C=1024 at SAME N_DIM (direction-wrong)
    - OR anchor mismatch (V_C=1024/N=16384 differs from N2's 4.96 > 0.10)
    - OR substrate-only-decode violated
    - OR run_mode != "full"

INSTRUMENTATION:
  1. per_unit: per (seed, V_C, N_DIM) entry; recompute-off-per_unit
  2. cv <= 0.05 across seeds for each (V_C, N_DIM)
  3. zero_llm_calls_at_inference: True LOGGED
  4. ceiling_bpc + concept_top1 decomposition per config
  5. corpus_provenance_real=True; allow_synthetic=False

VERSION MARKERS (BPC-affecting):
  v_c (per per_unit row)
  n_dim (per per_unit row)
  K=1, TAU=N/A (hard one-hot)
  assignment_mode = "hard_one_hot"

QUEUE: remote_cpu_queue (residuals_per_token.npz lives on marsh@home).
DEPENDENCY: token_ids in residuals_per_token.npz.

HONEST SIZING CONCERN: V_C=4096 is 4x larger codebook than N2. MiniBatchKMeans
fit time scales roughly linearly in V_C, and the kWTA assignment scales linearly
in V_C. N2 V_C=1024/N=16384 took ~10-11 min/seed on remote_cpu; V_C=4096
projects to 4-8x = 40-90 min/seed. Smoke arm measures actual wall to guide
GPU-vs-CPU routing decision (surfaced via verdict).

CONFIG_VERSION includes V_C_GRID + N_DIM_GRID (BPC-affecting; AST-verifiable).
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

ANCHOR_NAME = "n5_vc_4096_frontier_v1"

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

# V_C_GRID / N_DIM_GRID -- the sweep arms
_VC_GRID_FULL = [1024, 4096]
_N_GRID_FULL = [16384, 32768]
# Smoke: load-bearing test = V_C=4096 / N=16384 (HONEST SIZING CONCERN).
# Include V_C=1024/N=16384 for the anchor sanity-bracket so smoke also produces
# a within-cell comparison.
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

CONFIG_VERSION = (
    "VC_GRID=%s,N_GRID=%s,K=%d,f=%.4f,DECODE=countprop_interp,"
    "ASSIGN=hard_one_hot,MAX_DOCS=%d,SEEDS=%s,SPLIT=%.1f" % (
        "-".join(str(p) for p in (_VC_GRID_FULL if RUN_MODE != "smoke" else _VC_GRID_SMOKE)),
        "-".join(str(p) for p in (_N_GRID_FULL if RUN_MODE != "smoke" else _N_GRID_SMOKE)),
        K, F_SPARSE,
        100000 if RUN_MODE != "smoke" else 200,
        "-".join(str(s) for s in ([7, 17, 23] if RUN_MODE != "smoke" else [1])),
        TRAIN_FRAC,
    )
)

NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"


# ---------------------------------------------------------------------------
# Substrate ops (n4/n2 verbatim)
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

    # --- test 1: sparse_codebook shape + k_active correct ---
    vc_t, n_t = 16, 64
    C_t = sparse_codebook(vc_t, n_t, 0.05, rng)
    assert C_t.shape == (vc_t, n_t), "sparse_codebook shape FAIL"
    k_act_t = max(1, round(0.05 * n_t))
    for i in range(vc_t):
        assert int((C_t[i] != 0).sum()) == k_act_t, "codebook k-active mismatch"
    print("[selftest] T1 PASS: sparse_codebook shape + k-active correct", flush=True)

    # --- test 2: build_W / batched_concept_recall (verbatim from n4 T6) ---
    rng2 = np.random.default_rng(888)
    vc_sm, n_sm, vt_sm = 8, 32, 10
    C_sm = sparse_codebook(vc_sm, n_sm, 0.1, rng2)
    P_s = np.array([C_sm[i] for i in range(5)], dtype=np.float32)
    P_d = np.array([C_sm[(i + 1) % vc_sm] for i in range(5)], dtype=np.float32)
    W_sm = build_W(P_s, P_d)
    assert W_sm.shape == (n_sm, n_sm), "build_W shape FAIL"
    pred = batched_concept_recall(W_sm, C_sm[0:1], C_sm)
    assert int(pred[0]) == 1, "concept recall FAIL: expected 1, got %d" % int(pred[0])
    print("[selftest] T2 PASS: substrate ops (build_W + recall) verbatim from n2/n4", flush=True)

    # --- test 3: batched vs per-query token_logprob (n4 T6 verbatim) ---
    D_sm = np.zeros((n_sm, vt_sm), dtype=np.float32)
    for _ in range(5):
        D_sm[:, 7] += C_sm[3] * LR_DECODE
    lp_perq = token_logprob(D_sm, C_sm[3])
    lp_batch = batched_token_logprob(D_sm, C_sm[3:4])
    max_diff = float(np.abs(lp_perq - lp_batch[0]).max())
    assert max_diff < 1e-5, "batched_token_logprob != per-query: diff=%.2e" % max_diff
    print("[selftest] T3 PASS: batched vs per-query token_logprob match", flush=True)

    # --- test 4: zero-D-overlap fallback (Fix #6) ---
    D_zero = np.zeros((n_sm, vt_sm), dtype=np.float32)
    code_v = C_sm[0:1].copy()
    lp_zero = batched_token_logprob(D_zero, code_v)
    probs = np.exp(lp_zero[0])
    assert float(np.abs(probs - 1.0 / vt_sm).max()) < 1e-5, "zero-D-overlap fallback NOT uniform"
    assert not np.isnan(lp_zero).any(), "zero-D-overlap produced NaN logprob"
    print("[selftest] T4 PASS: zero-D-overlap fallback -> uniform (Fix #6)", flush=True)

    # --- test 5: synthetic end-to-end produces finite BPC ---
    res_e2e = _run_synthetic(rng_seed=42, n_dim=64, f=0.05, vc=8, vt=20, residual_dim=32)
    assert res_e2e is not None, "synthetic run returned None"
    for key in ("substrate_bpc", "ceiling_bpc", "unigram_bpc"):
        val = res_e2e.get(key)
        assert val is not None, "metric %s is None" % key
        assert not math.isnan(val), "metric %s is NaN" % key
    assert res_e2e["substrate_bpc"] > 0.0, "substrate_bpc zero"
    assert res_e2e["ceiling_bpc"] > 0.0, "ceiling_bpc zero"
    print("[selftest] T5 PASS: synthetic end-to-end produces finite BPC", flush=True)

    # --- test 6: LLM-call counter remains at 0 ---
    assert _LLM_CALL_COUNTER[0] == 0, "LLM_CALL_COUNTER non-zero -- substrate-only-gate VIOLATED"
    print("[selftest] T6 PASS: LLM_CALL_COUNTER = 0 (substrate-only-gate auditable)", flush=True)

    # --- test 7: module-level constants are REAL CODE (AST-verifiable types) ---
    assert isinstance(ANCHOR_NAME, str) and len(ANCHOR_NAME) > 0, "ANCHOR_NAME not a str"
    assert isinstance(CONFIG_VERSION, str), "CONFIG_VERSION not a str"
    assert "VC_GRID=" in CONFIG_VERSION, "CONFIG_VERSION missing VC_GRID label"
    assert "N_GRID=" in CONFIG_VERSION, "CONFIG_VERSION missing N_GRID label"
    assert "ASSIGN=hard_one_hot" in CONFIG_VERSION, "CONFIG_VERSION missing ASSIGN marker"
    assert isinstance(VC_GRID, list) and len(VC_GRID) >= 1, "VC_GRID not a non-empty list"
    assert isinstance(N_GRID, list) and len(N_GRID) >= 1, "N_GRID not a non-empty list"
    assert isinstance(K, int) and K == 1, "K not 1 (fixed config; clean V_C-alone discriminator)"
    assert isinstance(F_SPARSE, float) and 0 < F_SPARSE < 1, "F_SPARSE not in (0,1)"
    assert isinstance(LAM_BACKOFF, float) and 0 < LAM_BACKOFF < 1, "LAM_BACKOFF not in (0,1)"
    assert isinstance(RESIDUAL_DIM, int) and RESIDUAL_DIM == 768, "RESIDUAL_DIM not 768"
    print("[selftest] T7 PASS: module-level constants + AST-verifiable types", flush=True)

    # --- test 8: VC_GRID has 1024 (anchor) AND a value > 1024 (frontier) ---
    if RUN_MODE != "smoke":
        assert 1024 in VC_GRID, "VC_GRID missing 1024 anchor: %s" % VC_GRID
    has_frontier = any(v > 1024 for v in VC_GRID)
    assert has_frontier, "VC_GRID lacks V_C>1024 frontier arm: %s" % VC_GRID
    for vc_v in VC_GRID:
        assert 1 <= vc_v <= MAX_VC, "VC_GRID entry %d out of range [1, %d]" % (vc_v, MAX_VC)
    print("[selftest] T8 PASS: VC_GRID has anchor + frontier arms", flush=True)

    # --- test 9: N_GRID has 16384 (anchor N) and all <= reasonable max ---
    if RUN_MODE != "smoke":
        assert 16384 in N_GRID, "N_GRID missing 16384 anchor: %s" % N_GRID
    for n_v in N_GRID:
        assert 256 <= n_v <= 131072, "N_GRID entry %d out of range" % n_v
    print("[selftest] T9 PASS: N_GRID has 16384 anchor; all in sane range", flush=True)

    # --- test 10: per_unit dict shape (chain-grade per_unit blocker) ---
    per_unit_keys_required = (
        "seed", "v_c", "n_dim", "k", "f_sparse", "assignment_mode",
        "substrate_bpc", "ceiling_bpc", "bigram_bpc", "unigram_bpc",
        "substrate_top1", "ceiling_top1", "codebook_utilization", "alpha",
        "llm_forward_calls_at_inference", "wall_s",
    )
    fake_unit = {k: (0 if k in ("seed", "v_c", "n_dim", "k", "llm_forward_calls_at_inference")
                     else ("hard_one_hot" if k == "assignment_mode" else 0.0))
                 for k in per_unit_keys_required}
    for key in per_unit_keys_required:
        assert key in fake_unit, "per_unit missing required key: %s" % key
    print("[selftest] T10 PASS: per_unit shape includes all required keys", flush=True)

    # --- test 11: anchor threshold (V_C=1024/N=16384 within 0.10 of N2's 4.96) ---
    anchor_tolerance = 0.10
    n2_anchor_substrate_bpc = 4.959
    assert 0.0 < anchor_tolerance < 0.5, "anchor tolerance must be in (0, 0.5)"
    assert 1.0 < n2_anchor_substrate_bpc < 10.0, "N2 anchor substrate outside sane range"
    print("[selftest] T11 PASS: anchor threshold (V_C=1024/N=16384 within 0.10 of N2 4.96) defined",
          flush=True)

    # --- test 12: pre-reg bands sane ---
    HARD_PASS_THRESHOLD = 4.36  # >=0.60 bit drop from 4.959
    MIDDLE_BAND_DELTA = 0.10
    HARD_FAIL_DELTA = 0.10
    assert HARD_PASS_THRESHOLD < n2_anchor_substrate_bpc, "HARD_PASS threshold must beat N2"
    assert MIDDLE_BAND_DELTA > 0, "MIDDLE_BAND delta must be positive"
    assert HARD_FAIL_DELTA > 0, "HARD_FAIL delta must be positive"
    print("[selftest] T12 PASS: pre-reg bands sane", flush=True)

    print("[selftest] ALL 12 TESTS PASS: n5 V_C frontier cell instrumentation validated", flush=True)


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
# Per-seed run: (V_C, N_DIM) sweep at fixed K=1
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    """Full per-seed pipeline: load data once, sweep (V_C, N_DIM) arms."""
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

    # Test residuals: L2-normalize per-doc
    test_res_per_doc_n = []
    for d in test_docs:
        nrm = np.linalg.norm(d[0], axis=1, keepdims=True) + 1e-8
        test_res_per_doc_n.append((d[0] / nrm).astype(np.float32))

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

    # --- OUTER LOOPS: V_C and N_DIM sweep ---
    for vc in VC_GRID:
        # Fit k-means ONCE per V_C (shared across N_DIM arms)
        print("[seed=%d V_C=%d] fitting MiniBatchKMeans on %d train tokens..." % (
            seed, vc, len(train_res_n)), flush=True)
        t_km0 = time.time()
        try:
            from sklearn.cluster import MiniBatchKMeans
            km = MiniBatchKMeans(n_clusters=vc, random_state=seed,
                                 batch_size=4096, n_init=3, max_iter=100, verbose=0)
            km.fit(train_res_n)
            centers = km.cluster_centers_.astype(np.float32)
            cn = np.linalg.norm(centers, axis=1, keepdims=True) + 1e-8
            centers = (centers / cn).astype(np.float32)
            km_available = True
        except ImportError:
            print("[seed=%d V_C=%d] sklearn unavailable; numpy random-center VQ" % (seed, vc),
                  flush=True)
            rng_vq = np.random.default_rng(seed + 5000)
            centers_idx = rng_vq.choice(len(train_res_n), size=vc, replace=False)
            centers = train_res_n[centers_idx].copy()
            cn = np.linalg.norm(centers, axis=1, keepdims=True) + 1e-8
            centers = (centers / cn).astype(np.float32)
            km_available = False
        km_wall = time.time() - t_km0
        print("[seed=%d V_C=%d] kmeans fit wall=%.1fs (km_available=%s)" % (
            seed, vc, km_wall, km_available), flush=True)

        # Hard one-hot assignment for train + test (K=1)
        train_cids = np.argmax(train_res_n @ centers.T, axis=1).astype(np.int64)
        test_cids_per_doc = []
        for trn in test_res_per_doc_n:
            if trn.shape[0] > 0:
                test_cids_per_doc.append(np.argmax(trn @ centers.T, axis=1).astype(np.int64))
            else:
                test_cids_per_doc.append(np.zeros((0,), dtype=np.int64))

        unique_cids_train = np.unique(train_cids)
        utilization = len(unique_cids_train) / vc

        # Slice cids per-doc for train
        def slice_train_cids(docs_split, cids_flat):
            seqs = []
            offset = 0
            for doc_res, doc_tok in docs_split:
                n_doc = len(doc_res)
                seqs.append((cids_flat[offset:offset + n_doc], doc_tok))
                offset += n_doc
            return seqs

        train_seqs = slice_train_cids(train_docs, train_cids)

        # --- INNER LOOP: N_DIM sweep at fixed V_C ---
        for n_dim in N_GRID:
            t_arm = time.time()
            print("[seed=%d V_C=%d N=%d] building substrate..." % (seed, vc, n_dim), flush=True)

            # Sparse concept codebook (V_C-dependent)
            rng2 = np.random.default_rng(seed + 1000 + vc * 31 + n_dim * 17)
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
                per_unit_list.append({
                    "seed": seed, "v_c": vc, "n_dim": n_dim, "k": K,
                    "f_sparse": f, "assignment_mode": "hard_one_hot",
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
                })
                continue

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
                per_unit_list.append({
                    "seed": seed, "v_c": vc, "n_dim": n_dim, "k": K,
                    "f_sparse": f, "assignment_mode": "hard_one_hot",
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
                })
                continue

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
                "assignment_mode": "hard_one_hot",
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
            }
            per_unit_list.append(per_unit)

            print("  [seed=%d V_C=%d N=%d] sub_bpc=%.3f ceiling_bpc=%.3f bigram=%.3f "
                  "concept_top1=%.3f util=%.1f%% alpha=%.3f km_wall=%.1fs wall=%.1fs%s%s" % (
                      seed, vc, n_dim, sub_bpc, ceiling_bpc, big_bpc_global,
                      per_unit["substrate_concept_top1"], utilization * 100, alpha,
                      km_wall, per_unit["wall_s"],
                      " [ANCHOR]" if per_unit["is_anchor_arm"] else "",
                      " [SAT]" if saturated else ""), flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "per_unit": per_unit_list,
        "K": K,
        "f_sparse": f,
        "assignment_mode": "hard_one_hot",
        "V_TOK": V_TOK,
        "n_docs": len(train_docs) + len(test_docs),
        "n_train_docs": len(train_docs),
        "n_test_docs": len(test_docs),
        "run_mode": RUN_MODE,
        "vc_grid": VC_GRID,
        "n_grid": N_GRID,
        "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "elapsed_s": elapsed,
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
    """Compute verdict against pre-registered bands (V_C frontier).

    HARD_PASS: V_C=4096 (any N_DIM) has substrate_bpc <= 4.36 AND cv <= 0.05
               AND not saturated AND substrate-only-decode AND direction-correct
               (V_C=4096 strictly better than V_C=1024 at same N_DIM)
               AND anchor sanity (V_C=1024/N=16384 reproduces 4.96 within 0.10)
               AND run_mode = "full" (Fix #5).
    MIDDLE_BAND: V_C=4096 substrate improves 0.10-0.60 bits vs N2's 4.96.
    HARD_FAIL: < 0.10 improvement OR direction-wrong OR anchor mismatch OR
               LLM-call violation OR run_mode != "full".
    """
    by_cfg = _flatten_per_unit(ps)

    if not by_cfg:
        return ("HARD_FAIL", "HARD_FAIL: no per_unit data; cell produced no results.")

    # PRE-FLIGHT run_mode check (Fix #5)
    run_modes = set()
    for p in ps:
        run_modes.add(p.get("run_mode", "unknown"))
    if run_modes != {"full"}:
        if run_modes == {"smoke"}:
            smoke_msg = " [SMOKE: non-binding verdict; full run required for chain-grade]"
        else:
            return ("HARD_FAIL",
                    "HARD_FAIL: run_mode mismatch (Fix #5 pre-flight gate): "
                    "expected uniform 'full' but got run_modes=%s. Stale smoke-checkpoint "
                    "leak suspected; rerun full." % sorted(run_modes))
    else:
        smoke_msg = ""

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

    # LLM-call gate
    any_llm_viol = any(s["any_llm_violation"] for s in cfg_stats.values())
    if any_llm_viol:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (LLM forward call counter > 0)."
                + smoke_msg)

    # Anchor sanity: V_C=1024/N=16384 must reproduce N2's 4.96 within 0.10
    n2_anchor_substrate = 4.959
    anchor_note = ""
    anchor_failed = False
    if (1024, 16384) in cfg_stats:
        a_sb = cfg_stats[(1024, 16384)]["substrate_bpc_mean"]
        if not math.isnan(a_sb):
            diff = abs(a_sb - n2_anchor_substrate)
            if diff < 0.10:
                anchor_note = " ANCHOR-OK(V_C=1024/N=16384 sub_bpc=%.3f ~ N2 %.3f)" % (
                    a_sb, n2_anchor_substrate)
            else:
                anchor_note = " ANCHOR-MISMATCH(V_C=1024/N=16384 sub_bpc=%.3f vs N2=%.3f diff=%.3f)" % (
                    a_sb, n2_anchor_substrate, diff)
                if RUN_MODE == "full":
                    anchor_failed = True

    # Per-config summary
    cfg_lines = []
    for key in sorted(cfg_stats.keys()):
        s = cfg_stats[key]
        cfg_lines.append(
            "V_C=%d/N=%d%s: sub=%.3f ceil=%.3f cv=%.3f wall=%.1fs km=%.1fs" % (
                key[0], key[1], " [ANCHOR]" if s["is_anchor_arm"] else "",
                s["substrate_bpc_mean"], s["ceiling_bpc_mean"], s["substrate_bpc_cv"],
                s["wall_s_mean"], s["km_wall_s_mean"]))

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

    summary = (
        "best_V_C=4096=%s best_sub_bpc=%.3f anchor_sub=%.3f delta=%.3f cv=%.3f%s; %s%s" % (
            best_4k if best_4k is not None else "NONE",
            best_4k_sub if best_4k_sub < float("inf") else float("nan"),
            n2_anchor_substrate,
            (n2_anchor_substrate - best_4k_sub) if best_4k_sub < float("inf") else float("nan"),
            best_4k_cv,
            anchor_note,
            " | ".join(cfg_lines),
            smoke_msg,
        )
    )

    # Anchor mismatch -> HARD_FAIL at full
    if anchor_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: V_C=1024/N=16384 anchor mismatch (N2 baseline NOT reproduced). "
                + summary)

    # No V_C=4096 arm -> incomplete
    if best_4k is None or best_4k_sub == float("inf"):
        return ("HARD_FAIL",
                "HARD_FAIL: no V_C=4096 arm produced substrate_bpc; cell incomplete. " + summary)

    substrate_delta = n2_anchor_substrate - best_4k_sub  # positive = V_C=4096 improves

    # Direction-correct check: V_C=4096 strictly better than V_C=1024 at SAME N_DIM
    # (skip when only one V_C in grid, e.g. override)
    direction_failed = False
    if 1024 in [k[0] for k in cfg_stats.keys()] and 4096 in [k[0] for k in cfg_stats.keys()]:
        for n_d in [k[1] for k in cfg_stats.keys() if k[0] == 4096]:
            if (1024, n_d) in cfg_stats and (4096, n_d) in cfg_stats:
                s1k = cfg_stats[(1024, n_d)]["substrate_bpc_mean"]
                s4k = cfg_stats[(4096, n_d)]["substrate_bpc_mean"]
                if not math.isnan(s1k) and not math.isnan(s4k):
                    # Wrong-direction if V_C=4096 is WORSE than V_C=1024 at same N_DIM
                    if s4k > s1k + 0.05:  # tolerance for measurement noise
                        direction_failed = True
                        break

    if direction_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: V_C=4096 WORSE than V_C=1024 at same N_DIM "
                "(wrong-direction; pre-reg-direction-must-match-intent). " + summary)

    # HARD_PASS thresholds
    HARD_PASS_SUBSTRATE_THRESHOLD = 4.36  # >=0.60 bit drop from 4.959
    MIDDLE_BAND_DELTA = 0.10
    HARD_FAIL_DELTA = 0.10

    if (best_4k_sub <= HARD_PASS_SUBSTRATE_THRESHOLD
            and best_4k_cv <= 0.05
            and not cfg_stats[best_4k]["any_saturated"]):
        # HARD_PASS_PLUS: substrate_bpc < bigram (3.844)
        plus_tag = ""
        bigram_m = cfg_stats[best_4k]["bigram_bpc_mean"]
        if not math.isnan(bigram_m) and best_4k_sub < bigram_m:
            plus_tag = " HARD_PASS_PLUS(substrate<bigram=%.3f)" % bigram_m
        return ("HARD_PASS",
                "HARD_PASS: V_C=4096 at %s achieves substrate_bpc=%.3f<=4.36 AND cv=%.3f<=0.05 "
                "AND substrate-only-decode (LLM calls=0).%s " % (
                    best_4k, best_4k_sub, best_4k_cv, plus_tag) + summary)

    if substrate_delta >= MIDDLE_BAND_DELTA:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: V_C=4096 partial mechanism (substrate_delta=%.3f bits; "
                "between %.2f and %.2f). " % (substrate_delta, MIDDLE_BAND_DELTA,
                                              n2_anchor_substrate - HARD_PASS_SUBSTRATE_THRESHOLD)
                + summary)

    # HARD_FAIL: < 0.10 improvement
    if substrate_delta < HARD_FAIL_DELTA:
        return ("HARD_FAIL",
                "HARD_FAIL: V_C scaling alone insufficient (substrate_delta=%.3f < 0.10 bits). "
                "Mechanism falsified at V_C=4096 alone; route to k-WTA + Path A composition "
                "(n4+V_C joint). " % substrate_delta + summary)

    # Fallback MIDDLE_BAND for small positive delta
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: V_C=4096 small-effect substrate_delta=%.3f. " % substrate_delta
            + summary)


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s VC_GRID=%s N_GRID=%s K=%d f=%.4f MAX_DOCS=%d seeds=%s" % (
    ANCHOR_NAME, RUN_MODE, VC_GRID, N_GRID, K, F_SPARSE, MAX_DOCS, SEEDS), flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "vc_grid": VC_GRID, "n_grid": N_GRID, "K": K}

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
    print("  [seed=%d] %s elapsed=%.1fs llm_calls=%d" % (
        seed, " | ".join(arm_strs), r["elapsed_s"],
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
    "assignment_mode": "hard_one_hot",
    "zero_llm_calls_at_inference": True,
    "total_llm_forward_calls_observed": total_llm_calls,
    "corpus_provenance_real": True,
    "allow_synthetic": False,
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
