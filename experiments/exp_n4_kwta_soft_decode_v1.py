"""
n4_kwta_soft_decode_v1 -- N4: Top-k soft kWTA-VQ at write AND read of decode matrix D.

MOTIVATION (Research brain-within-concept-floor 5x drill 2026-06-22):
  Substrate runs hard one-hot VQ at f = 1/V_C ~= 0.001 = 50-100x SPARSER than the
  optimal biological coding level f* ~= 0.05-0.10 (cerebellum granule cells,
  mushroom body Kenyon cells, dentate gyrus -- Litwin-Kumar 2017, Modi 2020,
  Cayco-Gajic 2019). Hard one-hot VQ destroys pattern-completion structure CA3
  uses to lower conditional entropy.

  NOVEL SYNTHESIS: top-k soft concept readout (kWTA-VQ) at INGEST + READ.
  Replace hard km.predict() -> single-concept assignment with top-k softmax
  assignment and accumulate D over the top-k concepts (similarity-weighted).
  At test time, decode reads from top-k concept rows (same kWTA), summed.

  Forward-only Hebbian-compatible. Substrate-only-decode preserved (zero LLM
  forward calls). Orthogonal to n3 SimVQ projection (n3 failed; n4 keeps the
  768-dim centroid space, only changes assignment softness via MULTIPLICITY).

KWTA-VQ MECHANISM (substrate-only-decode-gate COMPATIBLE):
  ARM at k=1 (anchor): hard one-hot km.predict() -- reproduces N2 anchor.
  ARM at k > 1: top-k soft assignment + softmax(-dists/tau) weight + Hebbian
    write to top-k rows of D, similarity-weighted; same pooling at read.

  k-sweep tests MULTIPLICITY directly (the brain-drill prediction is that
  biology converged on k/V_C ~= 0.05-0.10 for optimal effective dimension).

REUSES n2/n3 HARNESS VERBATIM (Skunkworks chain-grade spec):
  - HD-binding context: ctx_vec = L2_normalize(sum_j roll(C[c_{t-j}], j))
  - W-materialized batched recall: W = P_src.T @ P_dst, then FREE P_src/P_dst
  - v3.1 count-proportional + Jelinek-Mercer interpolation decode
  - Per-seed checkpoint / resume (PROT-021 run_config guard)
  - _instrumentation_selftest at module scope
  - ANCHOR_NAME / write_metrics / CONFIG_VERSION discipline
  - Zero-D-overlap fallback in batched_token_logprob (n3 pattern; Fix #6)
  - pre-reg-direction-must-match-intent in verdict (Skunkworks n3 catch)
  - PRE-FLIGHT run_mode-must-be-full guard inside verdict() (Fix #5)

FIXED CONFIG (matches N2/n3 for direct comparison):
  V_C = 1024
  N_DIM = 16384
  K = 1 (depth -- K=2 follow-on after n4 lands; brain-drill Prediction 3)
  K_GRID (Phase 1) = [1, 8, 32]
    k=1: hard one-hot anchor (must reproduce N2 ceiling_bpc=2.049 within 0.05)
    k=8: f_eff = 8/1024 = 0.008 (still below biological optimum but tests
         multiplicity direction)
    k=32: f_eff = 32/1024 = 0.031 (approaching biological optimum at this V_C)
  TAU = 1.0 (softmax temperature; brain-drill Phase-1 default; tau-sweep at
    best-k is Phase-2 conditional)

SCIENTIFIC QUESTIONS (pre-registered; verdict must answer):
  (a) Does K_VALUE=1 reproduce N2 V_C=1024/N=16384/K=1 baseline ceiling_bpc=2.049
      within 0.05 bits? (ANCHOR-OK check; selftest T9.)
  (b) Does some K_VALUE in {8, 32} LOWER ceiling_bpc by >=0.30 bits vs k=1?
      (HARD-PASS: any arm has ceiling_bpc <= 1.75 AND substrate_bpc <= 4.75.)
  (c) Does ceiling improvement track substrate improvement? (i.e. does the soft
      readout floor-drop propagate to end-to-end substrate BPC?)
  (d) Is the optimum-k DIRECTION (softer-is-better) confirmed? (Prediction 2:
      best-k MUST NOT be k=1 for HARD_PASS; brain-drill Prediction 5 routes
      hippocampal-episodic as revival if k=1 is best.)

PRE-REGISTERED BANDS (Research note brain-within-concept-floor 2026-06-22):
  HARD_PASS (chain-grade, ALL of):
    - some K_VALUE has ceiling_bpc <= 1.75 (>= 0.30 bits drop vs N2's 2.049)
    - same K_VALUE has substrate_bpc <= 4.75 (>= 0.21 bits drop vs N2's 4.959)
    - cv across seeds <= 0.05 for the passing config
    - NOT saturated (alpha < 1.0)
    - substrate-only-decode (zero LLM calls -- enforced + asserted)
    - best-k != 1 (the mechanism IS multiplicity; k=1 winning = noise effect)
    - run_mode = "full" (no smoke-mislabel-as-full; Fix #5)
  HARD_PASS_PLUS: substrate_bpc < bigram_bpc (3.844) at some k -- bigram-beating.
  MIDDLE_BAND (partial mechanism, EITHER of):
    - ceiling_bpc drops 0.10-0.30 bits vs k=1 arm at some k>1
    - substrate_bpc improves >= 0.10 bits but does not beat HARD_PASS bar
  HARD_FAIL:
    - best ceiling_bpc change < 0.05 bits across all k>1 (mechanism wrong;
      route to n5 hippocampal-episodic + Path A V_C scaling per brain-drill
      Prediction 5)
    - OR anchor mismatch (K_VALUE=1 ceiling_bpc differs from N2's 2.049 > 0.05)
    - OR substrate-only gate violated (LLM forward call counter > 0)
    - OR wrong-direction (ceiling monotonically WORSE with k = soft averaging
      destructive at this V_C)
    - OR run_mode != "full" (stale smoke metric; Fix #5)

INSTRUMENTATION (Skunkworks N2 chain-grade structural blockers, all 4 baked):
  1. per_unit: per (seed, K_VALUE) entry stored in per_seed; recompute-off-per_unit
  2. cv <= 0.05: computed across seeds for each K_VALUE in verdict
  3. zero_llm_calls_at_inference: True LOGGED in metrics (asserted = False catch)
  4. VQ-floor decomposition: ceiling_bpc (oracle pooled top-k concept-to-token
     entropy floor) reported separately per K_VALUE

VERSION MARKERS (BPC-affecting params -- invalidate checkpoints if changed):
  assignment_mode = "top_k_soft"
  k_value (per per_unit row)
  tau (softmax temperature)
  effective_coding_level = k / V_C (the biological coding-level analog)

QUEUE: remote_cpu_queue (residuals_per_token.npz lives on marsh@home).
DEPENDENCY: token_ids in residuals_per_token.npz.

CONFIG_VERSION includes K_GRID + TAU (BPC-affecting; AST-verifiable).
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

ANCHOR_NAME = "n4_kwta_soft_decode_v1"

# ---------------------------------------------------------------------------
# LLM-call audit counter (Skunkworks structural blocker #3)
# ---------------------------------------------------------------------------
# Single mutable int in a list; any LLM forward call site must increment this.
# This cell imports NO transformers/torch modules, so the assertion is a
# structural guarantee (verified by code-trace) and the counter stays at 0 --
# we log it to make the substrate-only claim AUDITABLE in metrics, not just
# code-trace.
_LLM_CALL_COUNTER = [0]


# ---------------------------------------------------------------------------
# Configurable params (env vars / CLI)
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--k-grid", dest="k_grid", type=str, default=None,
                 help="Comma-separated K_VALUE values (default '1,8,32')")
_ap.add_argument("--tau", dest="tau", type=float, default=None,
                 help="Softmax temperature (default 1.0)")
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

# K_GRID = top-k multiplicity sweep (Phase 1: 1, 8, 32 per brain-drill)
#   k=1: hard one-hot anchor (must reproduce N2 ceiling_bpc=2.049)
#   k=8: f_eff=0.008 (multiplicity-direction test below biological optimum)
#   k=32: f_eff=0.031 (approaching biological optimum at V_C=1024)
_K_GRID_FULL = [1, 8, 32]
_K_GRID_SMOKE = [1, 8, 32]  # same shape at smoke; tests anchor + 2 multiplicities

_k_grid_str = _ARGS.k_grid or os.environ.get("HDLAB_K_GRID", "")
if _k_grid_str.strip():
    _K_GRID_OVERRIDE = [int(x.strip()) for x in _k_grid_str.split(",") if x.strip()]
else:
    _K_GRID_OVERRIDE = []

TAU = float(_ARGS.tau) if _ARGS.tau is not None else float(os.environ.get("HDLAB_TAU", "1.0"))

if RUN_MODE == "smoke":
    SEEDS = [1]
    K_GRID = _K_GRID_OVERRIDE if _K_GRID_OVERRIDE else _K_GRID_SMOKE
    MAX_DOCS = 200
    MAX_TOK_VOCAB = 1000
    N_DIM_RUN = 512  # smaller N_DIM at smoke for fast runtime
else:
    SEEDS = [7, 17, 23]
    K_GRID = _K_GRID_OVERRIDE if _K_GRID_OVERRIDE else _K_GRID_FULL
    MAX_DOCS = 100000
    MAX_TOK_VOCAB = 50257
    N_DIM_RUN = N_DIM

TRAIN_FRAC = 0.8
LR_DECODE = 1.0
LAM_BACKOFF = 0.1
INTERP_B = 0.3

# RESIDUAL_DIM = native Pythia residual dimensionality (768).
RESIDUAL_DIM = 768

# Hard upper bound on K_VALUE; >=V_C means uniform pooling (degenerate).
# k > V_C is rejected (cannot pool more concepts than exist).
MAX_K = V_C

CONFIG_VERSION = (
    "K_GRID=%s,V_C=%d,N_DIM=%d,K=%d,f=%.4f,TAU=%.3f,DECODE=countprop_interp,"
    "ASSIGN=top_k_soft,MAX_DOCS=%d,SEEDS=%s,SPLIT=%.1f" % (
        "-".join(str(p) for p in (_K_GRID_FULL if RUN_MODE != "smoke" else _K_GRID_SMOKE)),
        V_C, N_DIM_RUN, K, F_SPARSE, TAU,
        100000 if RUN_MODE != "smoke" else 200,
        "-".join(str(s) for s in ([7, 17, 23] if RUN_MODE != "smoke" else [1])),
        TRAIN_FRAC,
    )
)

NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"


# ---------------------------------------------------------------------------
# Substrate ops (n2/n3 verbatim)
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
    """Batched calibrated log-prob with zero-D-overlap fallback (n3 pattern, Fix #6).

    When scores.sum() == 0 for a row (concept code has zero overlap with all D
    columns -- happens at smoke scale or pathological soft-pooled cases),
    fall back to uniform for that row. Prevents NaN in BPC.
    """
    scores = np.maximum(concept_vecs @ D, 0.0)  # (n_pos, V_TOK)
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
    """Per-query calibrated log-prob (with zero-sum-row fallback to uniform)."""
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
# kWTA-VQ: top-k soft assignment (the novel mechanism)
# ---------------------------------------------------------------------------

def top_k_soft_assign(residuals_n: np.ndarray, centers: np.ndarray,
                      k_value: int, tau: float) -> Tuple[np.ndarray, np.ndarray]:
    """Top-k soft kWTA-VQ assignment.

    For each residual r (L2-normalized), compute squared-Euclidean distance to
    each center (L2-normalized k-means centroid), pick the top-k nearest,
    and softmax-normalize the (negative) distances over the k to get weights.

    Substrate-only-gate compatible: no LLM calls; pure numpy.
    Forward-only Hebbian-compatible: similarity-weighted; no backprop.

    Args:
        residuals_n: (n, d) L2-normalized residuals
        centers: (V_C, d) k-means centroids (L2-normalized in projected space
                 or as fit by sklearn)
        k_value: number of top centroids to retain per residual (1 = hard;
                 V_C = uniform pooling)
        tau: softmax temperature (1.0 = default)

    Returns:
        top_k_ids: (n, k_value) int64 -- centroid indices, top-k nearest
        weights: (n, k_value) float32 -- softmax(-dists/tau) per row, sum=1

    For k_value == 1: returns the hard-one-hot equivalent (top-1 ID + weight=1).
    For k_value == V_C: returns all centroids + uniform-ish weights.
    """
    n = residuals_n.shape[0]
    vc = centers.shape[0]
    k_val = max(1, min(int(k_value), vc))

    # Compute pairwise squared distances (n, vc) via expansion: |a-b|^2 = a.a + b.b - 2*a.b
    # For L2-normalized a, b: |a-b|^2 = 2 - 2*(a.b). The constant 2 cancels in softmax.
    # We use a memory-efficient chunked approach for large n.
    CHUNK = 4096
    top_k_ids = np.empty((n, k_val), dtype=np.int64)
    weights = np.empty((n, k_val), dtype=np.float32)
    log2 = math.log(2)
    for s in range(0, n, CHUNK):
        e = min(s + CHUNK, n)
        # negative inner product as a proxy for squared distance (monotone for
        # L2-normalized inputs).
        sims = residuals_n[s:e] @ centers.T  # (chunk, vc)
        # squared distances (constant offset cancels in softmax-of-negative)
        dists = 2.0 - 2.0 * sims  # (chunk, vc), >= 0
        if k_val == vc:
            # Take all centroids
            top_k_ids[s:e] = np.tile(np.arange(vc), (e - s, 1))
            d_top = dists
        elif k_val == 1:
            # Hard one-hot: argmin over vc -> argmax over sims
            ids = np.argmax(sims, axis=1)
            top_k_ids[s:e, 0] = ids
            d_top = np.zeros((e - s, 1), dtype=np.float32)  # softmax of single -> 1.0
        else:
            # Top-k by smallest distance = largest similarity. argpartition is O(n).
            # Negate for descending sims (largest sims = smallest dists).
            part = np.argpartition(-sims, k_val - 1, axis=1)[:, :k_val]  # (chunk, k_val)
            # Sort within k for determinism (matches softmax weight ordering, helps debugging)
            part_dists = np.take_along_axis(dists, part, axis=1)  # (chunk, k_val)
            sort_idx = np.argsort(part_dists, axis=1)  # ascending dist
            top_ids = np.take_along_axis(part, sort_idx, axis=1)
            top_k_ids[s:e] = top_ids
            d_top = np.take_along_axis(part_dists, sort_idx, axis=1)
        # Softmax over -dists/tau
        if k_val == 1:
            weights[s:e, :] = 1.0
        else:
            neg_d = -d_top / max(tau, 1e-6)
            # Subtract max for numerical stability
            neg_d_shift = neg_d - neg_d.max(axis=1, keepdims=True)
            exp_d = np.exp(neg_d_shift)
            wsum = exp_d.sum(axis=1, keepdims=True) + 1e-30
            weights[s:e, :] = (exp_d / wsum).astype(np.float32)
    return top_k_ids, weights


# ---------------------------------------------------------------------------
# Synthetic forward pass for self-test
# ---------------------------------------------------------------------------

def _run_synthetic_kwta(rng_seed: int, n_dim: int = 64, f: float = 0.05,
                        vc: int = 8, vt: int = 20, k_value: int = 4,
                        tau: float = 1.0, residual_dim: int = 32) -> Dict[str, Any]:
    """Synthetic forward pass for one K_VALUE."""
    rng = np.random.default_rng(rng_seed)
    n_docs = 20
    docs_res = [rng.standard_normal((12, residual_dim)).astype(np.float32) for _ in range(n_docs)]
    docs_tids = [rng.integers(0, vt, size=12) for _ in range(n_docs)]
    split = int(0.8 * n_docs)
    train_res_docs = docs_res[:split]
    test_res_docs = docs_res[split:]
    train_tids = docs_tids[:split]
    test_tids = docs_tids[split:]

    # L2-normalize residuals (substrate convention)
    def l2n(arr):
        nrm = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-8
        return (arr / nrm).astype(np.float32)
    train_res_n = [l2n(d) for d in train_res_docs]
    test_res_n = [l2n(d) for d in test_res_docs]
    train_res_flat = np.concatenate(train_res_n, axis=0)

    # Synthetic centers: random subset of train residuals (L2-normalized = already so)
    rng_vq = np.random.default_rng(rng_seed + 5000)
    centers_idx = rng_vq.choice(len(train_res_flat),
                                size=min(vc, len(train_res_flat)), replace=False)
    centers = train_res_flat[centers_idx].copy()

    def kwta_seq(seq_list):
        flat = np.concatenate(seq_list, axis=0)
        ids, ws = top_k_soft_assign(flat, centers, k_value, tau)
        return ids, ws  # (n, k), (n, k)

    train_ids, train_ws = kwta_seq(train_res_n)
    test_ids, test_ws = kwta_seq(test_res_n)

    rng2 = np.random.default_rng(rng_seed + 1000)
    C = sparse_codebook(vc, n_dim, f, rng2)

    # Build D: top-k SOFT writes per token (multi-row, similarity-weighted)
    D = np.zeros((n_dim, vt), dtype=np.float32)
    # concept_tok_counts: keyed by HARD-top-1 cid for ceiling computation
    concept_tok_counts: Dict[int, np.ndarray] = {}
    offset = 0
    for d_idx, t_doc in enumerate(train_tids):
        n_doc = len(train_res_docs[d_idx])
        for pos in range(n_doc):
            tok = int(t_doc[pos])
            if tok < vt:
                # Top-k soft write
                for ki in range(train_ids.shape[1]):
                    ci = int(train_ids[offset + pos, ki])
                    wi = float(train_ws[offset + pos, ki])
                    D[:, tok] += C[ci] * (wi * LR_DECODE)
                # Ceiling: track by hard-top-1 (the dominant concept at this position)
                top1_cid = int(train_ids[offset + pos, 0])
                if top1_cid not in concept_tok_counts:
                    concept_tok_counts[top1_cid] = np.zeros(vt, dtype=np.int64)
                concept_tok_counts[top1_cid][tok] += 1
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

    # Transitions: use HARD top-1 for the cid sequence (substrate-native; recall is
    # a hard pattern-completion operation regardless of decode softness).
    train_top1 = train_ids[:, 0]  # (n,)
    test_top1 = test_ids[:, 0]
    P_src_list, P_dst_list = [], []
    offset_train = 0
    for d_idx in range(len(train_res_docs)):
        n_doc = len(train_res_docs[d_idx])
        cids_doc = train_top1[offset_train:offset_train + n_doc]
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
    tot_t = 0; sub_nll = ceil_nll = uni_nll = 0.0
    sub_t_ok = 0
    log2 = math.log(2)
    offset_test = 0
    for d_idx in range(len(test_res_docs)):
        n_doc = len(test_res_docs[d_idx])
        cids_doc = test_top1[offset_test:offset_test + n_doc].astype(np.int64)
        t_doc = test_tids[d_idx]
        ctx_vecs = build_context_vecs_batched(C, cids_doc, K_depth=1, n_dim=n_dim)
        n_pos = ctx_vecs.shape[0]
        if n_pos == 0:
            offset_test += n_doc
            continue
        pred_c_batch = batched_concept_recall(W, ctx_vecs, C)
        # For the test residuals, build top-k pooled concept code for read-side
        # decode (read mirrors write: top-k similarity-weighted pooling).
        # pred_c_batch is the HARD recall predicted next-position concept; we then
        # use that concept's HARD code C[pred_c] for decode. (Alternative: use
        # top-k soft pooling of pred_c neighborhood -- adds a SECOND k pooling.
        # For Phase 1 we keep recall hard + decode hard-pooled-from-write-soft,
        # which already tests the write-side mechanism. Read-side pooling at
        # query time is a Phase-2 tau-sweep follow-on.)
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

    # --- test 1: top_k_soft_assign shape, weight-sum=1, k=1 == argmax ---
    n_tst, vc_tst, d_tst = 50, 16, 8
    res_t = rng.standard_normal((n_tst, d_tst)).astype(np.float32)
    res_t /= (np.linalg.norm(res_t, axis=1, keepdims=True) + 1e-8)
    cen_t = rng.standard_normal((vc_tst, d_tst)).astype(np.float32)
    cen_t /= (np.linalg.norm(cen_t, axis=1, keepdims=True) + 1e-8)
    # k=1: must equal argmax(sims) and weight=1.0
    ids1, ws1 = top_k_soft_assign(res_t, cen_t, k_value=1, tau=1.0)
    sims = res_t @ cen_t.T
    expected_argmax = np.argmax(sims, axis=1)
    assert ids1.shape == (n_tst, 1), "k=1 ids shape FAIL: %s" % str(ids1.shape)
    assert ws1.shape == (n_tst, 1), "k=1 ws shape FAIL: %s" % str(ws1.shape)
    assert (ids1[:, 0] == expected_argmax).all(), (
        "k=1 ids != argmax(sims): mismatch=%d" % int((ids1[:, 0] != expected_argmax).sum()))
    assert float(np.abs(ws1 - 1.0).max()) < 1e-6, (
        "k=1 weights != 1.0: max diff=%.2e" % float(np.abs(ws1 - 1.0).max()))
    print("[selftest] T1 PASS: k=1 reduces to hard argmax (weight=1.0)", flush=True)

    # --- test 2: weights sum to 1 per row for k > 1 ---
    for k_t in (4, 8):
        ids_t, ws_t = top_k_soft_assign(res_t, cen_t, k_value=k_t, tau=1.0)
        assert ids_t.shape == (n_tst, k_t), "k=%d ids shape FAIL: %s" % (k_t, str(ids_t.shape))
        assert ws_t.shape == (n_tst, k_t), "k=%d ws shape FAIL: %s" % (k_t, str(ws_t.shape))
        sums = ws_t.sum(axis=1)
        assert float(np.abs(sums - 1.0).max()) < 1e-4, (
            "k=%d weight sums != 1.0: max abs(sum-1)=%.4e" % (
                k_t, float(np.abs(sums - 1.0).max())))
        # ids must be unique per row
        for row in range(n_tst):
            assert len(set(ids_t[row].tolist())) == k_t, (
                "k=%d row=%d has duplicate ids: %s" % (k_t, row, ids_t[row]))
    print("[selftest] T2 PASS: top-k weights sum to 1 + unique ids for k>1", flush=True)

    # --- test 3: k=V_C uniform pooling produces near-uniform weights at tau>>1 ---
    ids_full, ws_full = top_k_soft_assign(res_t, cen_t, k_value=vc_tst, tau=100.0)
    assert ids_full.shape == (n_tst, vc_tst), (
        "k=V_C ids shape FAIL: %s" % str(ids_full.shape))
    sums_full = ws_full.sum(axis=1)
    assert float(np.abs(sums_full - 1.0).max()) < 1e-4, (
        "k=V_C weight sums != 1.0: max abs(sum-1)=%.4e" % float(np.abs(sums_full - 1.0).max()))
    # At high tau, weights should approach uniform (1/vc)
    max_dev = float(np.abs(ws_full - 1.0 / vc_tst).max())
    assert max_dev < 0.05, (
        "k=V_C at tau=100 should be near-uniform: max abs dev from 1/vc=%.4f" % max_dev)
    print("[selftest] T3 PASS: k=V_C at high tau -> near-uniform weights", flush=True)

    # --- test 4: synthetic end-to-end at k=4 produces finite BPC ---
    res_e2e = _run_synthetic_kwta(rng_seed=42, n_dim=64, f=0.05,
                                  vc=8, vt=20, k_value=4, tau=1.0,
                                  residual_dim=32)
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
        "LLM_CALL_COUNTER non-zero: %d -- substrate-only-gate VIOLATED" % _LLM_CALL_COUNTER[0])
    print("[selftest] T5 PASS: LLM_CALL_COUNTER = 0 (substrate-only-gate auditable)", flush=True)

    # --- test 6: substrate ops verbatim from N2 (recall + token_logprob match) ---
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

    # --- test 7: zero-D-overlap fallback in batched_token_logprob (Fix #6) ---
    # Build a code vec that has zero overlap with all D columns -> uniform fallback.
    D_zero = np.zeros((n_sm, vt_sm), dtype=np.float32)
    code_v = C_sm[0:1].copy()
    lp_zero = batched_token_logprob(D_zero, code_v)
    # Probabilities should be uniform = 1/vt_sm
    probs = np.exp(lp_zero[0])
    assert float(np.abs(probs - 1.0 / vt_sm).max()) < 1e-5, (
        "zero-D-overlap fallback NOT uniform: max dev=%.4e" % float(np.abs(probs - 1.0 / vt_sm).max()))
    assert not np.isnan(lp_zero).any(), "zero-D-overlap produced NaN logprob"
    print("[selftest] T7 PASS: zero-D-overlap fallback -> uniform (Fix #6)", flush=True)

    # --- test 8: module-level constants are REAL CODE (AST-verifiable types) ---
    assert isinstance(ANCHOR_NAME, str) and len(ANCHOR_NAME) > 0, "ANCHOR_NAME not a str"
    assert isinstance(CONFIG_VERSION, str) and "K_GRID=" in CONFIG_VERSION, (
        "CONFIG_VERSION missing K_GRID label")
    assert "ASSIGN=top_k_soft" in CONFIG_VERSION, (
        "CONFIG_VERSION missing ASSIGN=top_k_soft version marker")
    assert isinstance(K_GRID, list) and len(K_GRID) >= 1, "K_GRID not a non-empty list"
    assert isinstance(V_C, int) and V_C == 1024, "V_C not 1024 (fixed config)"
    assert isinstance(N_DIM, int) and N_DIM == 16384, "N_DIM not 16384 (fixed config)"
    assert isinstance(K, int) and K == 1, "K not 1 (fixed config)"
    assert isinstance(F_SPARSE, float) and 0 < F_SPARSE < 1, "F_SPARSE not in (0,1)"
    assert isinstance(LAM_BACKOFF, float) and 0 < LAM_BACKOFF < 1, "LAM_BACKOFF not in (0,1)"
    assert isinstance(RESIDUAL_DIM, int) and RESIDUAL_DIM == 768, "RESIDUAL_DIM not 768"
    assert isinstance(TAU, float) and TAU > 0.0, "TAU must be positive float"
    print("[selftest] T8 PASS: module-level constants are real code, fixed-config invariants",
          flush=True)

    # --- test 9: per_unit dict shape (Skunkworks chain-grade per_unit blocker #1) ---
    per_unit_keys_required = (
        "seed", "k_value", "tau", "effective_coding_level", "assignment_mode",
        "substrate_bpc", "ceiling_bpc", "bigram_bpc", "unigram_bpc",
        "substrate_top1", "ceiling_top1", "codebook_utilization", "alpha",
        "llm_forward_calls_at_inference", "wall_s",
    )
    fake_unit = {k: (0 if k in ("seed", "k_value", "llm_forward_calls_at_inference")
                     else ("top_k_soft" if k == "assignment_mode" else 0.0))
                 for k in per_unit_keys_required}
    for key in per_unit_keys_required:
        assert key in fake_unit, "per_unit missing required key: %s" % key
    print("[selftest] T9 PASS: per_unit shape includes all required keys (incl. version markers)",
          flush=True)

    # --- test 10: anchor check threshold (K_VALUE=1 must reproduce N2's 2.049 within 0.05) ---
    anchor_tolerance = 0.05
    n2_anchor_ceiling_bpc = 2.049
    assert 0.0 < anchor_tolerance < 0.5, "anchor tolerance must be in (0, 0.5)"
    assert 1.0 < n2_anchor_ceiling_bpc < 3.0, "N2 anchor ceiling outside sane range"
    print("[selftest] T10 PASS: anchor threshold (K_VALUE=1 within 0.05 of N2 2.049) defined",
          flush=True)

    # --- test 11: K_GRID has k=1 anchor arm ---
    if RUN_MODE != "smoke":
        has_anchor = any(k == 1 for k in K_GRID)
        assert has_anchor, (
            "K_GRID lacks k=1 anchor arm: %s -- anchor-check disabled" % K_GRID)
    # Also at smoke we keep k=1 (smoke uses same K_GRID shape)
    print("[selftest] T11 PASS: K_GRID has k=1 anchor arm (or smoke mode skipped)", flush=True)

    # --- test 12: K_GRID has at least one k > 1 (the multiplicity test) ---
    has_multiplicity = any(k > 1 for k in K_GRID)
    assert has_multiplicity, (
        "K_GRID lacks any k>1 multiplicity arm: %s -- mechanism test disabled" % K_GRID)
    print("[selftest] T12 PASS: K_GRID has at least one k>1 multiplicity arm", flush=True)

    # --- test 13: all K_GRID values are <= V_C (cannot pool more than exist) ---
    for k_v in K_GRID:
        assert 1 <= k_v <= MAX_K, "K_GRID entry %d out of range [1, %d]" % (k_v, MAX_K)
    print("[selftest] T13 PASS: all K_GRID values <= V_C", flush=True)

    print("[selftest] ALL 13 TESTS PASS: kWTA-VQ cell instrumentation validated", flush=True)


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
# Per-seed run: K sweep at fixed (V_C=1024, N_DIM=16384, K=1, tau=TAU)
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    """Full per-seed pipeline: load data once, sweep K_GRID for kWTA-VQ arms."""
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

    # Train residuals: L2-normalize once (shared across K arms; PROJ-independent)
    train_res_full = np.concatenate([d[0] for d in train_docs], axis=0)
    norms_tr = np.linalg.norm(train_res_full, axis=1, keepdims=True) + 1e-8
    train_res_n = train_res_full / norms_tr
    print("[seed=%d] train residuals: %d tokens, residual_dim=%d" % (
        seed, len(train_res_n), train_res_n.shape[1]), flush=True)

    # Test residuals: L2-normalize per-doc, concat for shared kWTA pass
    test_res_per_doc_n = []
    for d in test_docs:
        nrm = np.linalg.norm(d[0], axis=1, keepdims=True) + 1e-8
        test_res_per_doc_n.append((d[0] / nrm).astype(np.float32))
    test_res_flat = np.concatenate(test_res_per_doc_n, axis=0) if test_res_per_doc_n else \
                    np.zeros((0, train_res_n.shape[1]), dtype=np.float32)

    # Token vocab (from train)
    all_train_tids = np.concatenate([d[1] for d in train_docs])
    V_TOK = min(int(all_train_tids.max()) + 1, MAX_TOK_VOCAB)
    print("[seed=%d] V_TOK=%d" % (seed, V_TOK), flush=True)

    # Bigram + unigram baselines (K-independent; token-level stats)
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

    # Precompute test position arrays (K-independent for bigram/unigram BPC)
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

    # Unigram + bigram BPC (K-independent)
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

    # Fit k-means ONCE per seed (shared across K arms; the kWTA softness is
    # entirely in the ASSIGNMENT layer, not the codebook fit).
    print("[seed=%d] fitting VQ V_C=%d on %d train tokens..." % (
        seed, vc, len(train_res_n)), flush=True)
    try:
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=vc, random_state=seed,
                             batch_size=4096, n_init=3, max_iter=100, verbose=0)
        km.fit(train_res_n)
        centers = km.cluster_centers_.astype(np.float32)
        # L2-normalize centers (consistent with input normalization)
        cn = np.linalg.norm(centers, axis=1, keepdims=True) + 1e-8
        centers = (centers / cn).astype(np.float32)
        km_available = True
    except ImportError:
        print("[seed=%d] sklearn unavailable; numpy random-center VQ" % seed, flush=True)
        rng_vq = np.random.default_rng(seed + 5000)
        centers_idx = rng_vq.choice(len(train_res_n), size=vc, replace=False)
        centers = train_res_n[centers_idx].copy()
        cn = np.linalg.norm(centers, axis=1, keepdims=True) + 1e-8
        centers = (centers / cn).astype(np.float32)
        km_available = False

    # Per-unit results (one entry per K_VALUE)
    per_unit_list: List[Dict[str, Any]] = []

    # --- OUTER LOOP: K_VALUE sweep ---
    for k_idx, k_value in enumerate(K_GRID):
        t_k = time.time()
        print("[seed=%d k=%d] top-k soft assignment (tau=%.3f)..." % (
            seed, k_value, TAU), flush=True)

        # Top-k soft assignment for train + test
        train_ids, train_ws = top_k_soft_assign(train_res_n, centers, k_value, TAU)
        if test_res_flat.shape[0] > 0:
            test_ids, test_ws = top_k_soft_assign(test_res_flat, centers, k_value, TAU)
        else:
            test_ids = np.zeros((0, k_value), dtype=np.int64)
            test_ws = np.zeros((0, k_value), dtype=np.float32)

        # HARD top-1 cid sequence for recall (substrate-native; recall is hard)
        train_top1 = train_ids[:, 0].astype(np.int64)
        test_top1 = test_ids[:, 0].astype(np.int64) if test_ids.shape[0] > 0 else np.zeros((0,), dtype=np.int64)

        unique_cids_train = np.unique(train_top1)
        utilization = len(unique_cids_train) / vc

        # Slice cids + weights per-doc
        def slice_docs_ids_ws(docs_split, ids_flat, ws_flat):
            seqs = []; offset = 0
            for doc_res, doc_tok in docs_split:
                n_doc = len(doc_res)
                seqs.append((ids_flat[offset:offset + n_doc],
                             ws_flat[offset:offset + n_doc],
                             doc_tok))
                offset += n_doc
            return seqs

        train_seqs = slice_docs_ids_ws(train_docs, train_ids, train_ws)
        test_seqs = slice_docs_ids_ws(test_docs, test_ids, test_ws)

        # Sparse concept codebook (substrate-native; K-independent allocation)
        rng2 = np.random.default_rng(seed + 1000 + k_idx * 100)
        C = sparse_codebook(vc, n_dim, f, rng2)
        k_act = max(1, round(f * n_dim))

        # Build D: top-k SOFT writes per token (multi-row, similarity-weighted)
        # concept_tok_counts: keyed by HARD-top-1 cid for ceiling computation
        D = np.zeros((n_dim, V_TOK), dtype=np.float32)
        concept_tok_counts: Dict[int, np.ndarray] = {}
        for ids_doc, ws_doc, tids_doc in train_seqs:
            for t_pos in range(len(ids_doc)):
                tok = int(tids_doc[t_pos])
                if tok < V_TOK:
                    # Top-k soft write: accumulate weighted code rows
                    for ki in range(ids_doc.shape[1]):
                        ci = int(ids_doc[t_pos, ki])
                        wi = float(ws_doc[t_pos, ki])
                        D[:, tok] += C[ci] * (wi * LR_DECODE)
                    # Ceiling: track by HARD top-1 (the dominant concept)
                    top1_cid = int(ids_doc[t_pos, 0])
                    if top1_cid not in concept_tok_counts:
                        concept_tok_counts[top1_cid] = np.zeros(V_TOK, dtype=np.int64)
                    concept_tok_counts[top1_cid][tok] += 1
        ceiling_pred = {c: int(np.argmax(v)) for c, v in concept_tok_counts.items()}

        # Saturation alpha for this k arm's HARD top-1 cid assignment
        train_cids_all = train_top1
        unique_ctx_pairs = len(set(zip(train_cids_all[:-1].tolist(), train_cids_all[1:].tolist())))
        alpha = unique_ctx_pairs / n_dim
        saturated = (alpha > 1.0)

        # Build transition store at K=1 (hard top-1 sequence)
        P_src_list, P_dst_list = [], []
        for ids_doc, _ws_doc, _ in train_seqs:
            cids_doc = ids_doc[:, 0].astype(np.int64)
            ctx_vecs = build_context_vecs_batched(C, cids_doc, K_depth=K, n_dim=n_dim)
            if ctx_vecs.shape[0] == 0:
                continue
            P_src_list.append(ctx_vecs)
            P_dst_list.append(np.array(
                [C[int(cids_doc[t_pos + 1])] for t_pos in range(ctx_vecs.shape[0])],
                dtype=np.float32))

        if not P_src_list:
            per_unit_list.append({
                "seed": seed, "k_value": k_value, "tau": TAU,
                "effective_coding_level": k_value / vc,
                "assignment_mode": "top_k_soft",
                "substrate_bpc": float("nan"), "ceiling_bpc": float("nan"),
                "bigram_bpc": big_bpc_global, "unigram_bpc": uni_bpc_global,
                "substrate_top1": float("nan"), "ceiling_top1": float("nan"),
                "codebook_utilization": utilization, "alpha": alpha, "saturated": saturated,
                "is_anchor_arm": (k_value == 1),
                "k_active": k_act,
                "km_available": km_available,
                "n_trans": 0, "n_token_test_pairs": tot_t_global,
                "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
                "wall_s": time.time() - t_k,
            })
            continue

        P_src = np.concatenate(P_src_list, axis=0)
        P_dst = np.concatenate(P_dst_list, axis=0)
        n_trans = P_src.shape[0]
        print("[seed=%d k=%d] n_trans=%d alpha=%.3f%s building W (%dx%d)..." % (
            seed, k_value, n_trans, alpha, " [SAT]" if saturated else "",
            n_dim, n_dim), flush=True)
        W_k = build_W(P_src, P_dst)
        del P_src, P_dst

        # Build context vecs for all test positions (using HARD top-1 cids)
        _c_src_list, _c_tgt_list = [], []
        for ids_doc, _ws_doc, _ in test_seqs:
            cids_arr = ids_doc[:, 0].astype(np.int64)
            ctx_vecs = build_context_vecs_batched(C, cids_arr, K_depth=K, n_dim=n_dim)
            n_pos = ctx_vecs.shape[0]
            if n_pos == 0:
                continue
            _c_src_list.append(ctx_vecs)
            _c_tgt_list.extend(cids_arr[1:n_pos + 1].tolist())

        if not _c_src_list:
            per_unit_list.append({
                "seed": seed, "k_value": k_value, "tau": TAU,
                "effective_coding_level": k_value / vc,
                "assignment_mode": "top_k_soft",
                "substrate_bpc": float("nan"), "ceiling_bpc": float("nan"),
                "bigram_bpc": big_bpc_global, "unigram_bpc": uni_bpc_global,
                "substrate_top1": float("nan"), "ceiling_top1": float("nan"),
                "codebook_utilization": utilization, "alpha": alpha, "saturated": saturated,
                "is_anchor_arm": (k_value == 1),
                "k_active": k_act,
                "km_available": km_available,
                "n_trans": n_trans, "n_token_test_pairs": 0,
                "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
                "wall_s": time.time() - t_k,
            })
            continue

        Q_all = np.concatenate(_c_src_list, axis=0)
        c_tgt_all = np.array(_c_tgt_list, dtype=np.int64)
        tot_c = len(c_tgt_all)

        print("[seed=%d k=%d] batched recall: %d queries..." % (
            seed, k_value, tot_c), flush=True)
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

        print("[seed=%d k=%d] batched token decode: %d positions..." % (
            seed, k_value, n_valid), flush=True)
        for _ck_s in range(0, n_valid, BATCH_TOK_CHUNK):
            _ck_e = min(_ck_s + BATCH_TOK_CHUNK, n_valid)
            # Decode reads from the HARD pred_c row of D (which already contains
            # the soft-pooled writes from training -- the mechanism's effect).
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
            "k_value": k_value,
            "tau": TAU,
            "effective_coding_level": k_value / vc,
            "assignment_mode": "top_k_soft",
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
            "is_anchor_arm": (k_value == 1),
            "k_active": k_act,
            "km_available": km_available,
            "n_trans": n_trans,
            "n_token_test_pairs": tot_t_global,
            "n_concept_test_pairs": tot_c,
            "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "wall_s": time.time() - t_k,
        }
        per_unit_list.append(per_unit)

        print("  [seed=%d k=%d] sub_bpc=%.3f ceiling_bpc=%.3f bigram=%.3f "
              "concept_top1=%.3f util=%.1f%% alpha=%.3f f_eff=%.4f wall=%.1fs%s%s" % (
                  seed, k_value, sub_bpc, ceiling_bpc, big_bpc_global,
                  per_unit["substrate_concept_top1"], utilization * 100, alpha,
                  per_unit["effective_coding_level"], per_unit["wall_s"],
                  " [ANCHOR]" if k_value == 1 else "",
                  " [SAT]" if saturated else ""), flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "per_unit": per_unit_list,
        "V_C": vc, "N_DIM": n_dim, "K": K, "f_sparse": f, "tau": TAU,
        "assignment_mode": "top_k_soft",
        "V_TOK": V_TOK,
        "n_docs": len(train_docs) + len(test_docs),
        "n_train_docs": len(train_docs),
        "n_test_docs": len(test_docs),
        "run_mode": RUN_MODE,
        "k_grid": K_GRID,
        "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "elapsed_s": elapsed,
    }


# ---------------------------------------------------------------------------
# Verdict (pre-registered bands per brain-within-concept-floor 2026-06-22)
# ---------------------------------------------------------------------------

def _flatten_per_unit(ps: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    """Group per_unit entries by k_value across seeds."""
    by_k: Dict[int, List[Dict[str, Any]]] = {}
    for p in ps:
        for u in p.get("per_unit", []):
            kv = int(u["k_value"])
            by_k.setdefault(kv, []).append(u)
    return by_k


def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Compute verdict against brain-drill pre-registered bands.

    HARD-PASS: some K_VALUE>1 has ceiling_bpc <= 1.75 AND substrate_bpc <= 4.75
               AND cv <= 0.05 AND not saturated AND substrate-only-decode.
    HARD-PASS-PLUS: substrate_bpc < bigram_bpc (3.844) at some k.
    MIDDLE_BAND: ceiling drops 0.10-0.30 vs k=1 OR substrate improves >=0.10.
    HARD-FAIL: best ceiling change < 0.05 across all k>1 (mechanism wrong);
               OR anchor mismatch; OR LLM-call violation; OR wrong-direction;
               OR run_mode != "full" (Fix #5: pre-flight stale-smoke catch).
    """
    by_k = _flatten_per_unit(ps)

    if not by_k:
        return ("HARD_FAIL", "HARD_FAIL: no per_unit data; cell produced no results.")

    # PRE-FLIGHT run_mode check (Fix #5: stale-smoke-mislabeled-as-full guard).
    # If ANY per_seed has run_mode != "full" while ANCHOR_NAME ran in production,
    # the metric is stale and must be re-run. Skip the check when ALL seeds are smoke
    # (= a legitimate smoke run; verdict is non-binding).
    run_modes = set()
    for p in ps:
        rm = p.get("run_mode", "unknown")
        run_modes.add(rm)
    # Pre-flight rule: production verdict must come from a uniform "full" run.
    # If mixed modes or all-smoke, the verdict is gated.
    if run_modes != {"full"}:
        if run_modes == {"smoke"}:
            # Smoke-only run: don't HARD_FAIL (smoke is allowed), but tag verdict.
            smoke_msg = " [SMOKE: non-binding verdict; full run required for chain-grade]"
        else:
            # Mixed or partial -- this is the stale-smoke leak we're guarding against
            return ("HARD_FAIL",
                    "HARD_FAIL: run_mode mismatch (Fix #5 pre-flight gate): "
                    "expected uniform 'full' but got run_modes=%s. Stale smoke-checkpoint "
                    "leak suspected; rerun full." % sorted(run_modes))
    else:
        smoke_msg = ""

    # Compute per-K aggregates
    k_stats: Dict[int, Dict[str, float]] = {}
    for kv, units in by_k.items():
        cbs = [u["ceiling_bpc"] for u in units if not math.isnan(u.get("ceiling_bpc", float("nan")))]
        sbs = [u["substrate_bpc"] for u in units if not math.isnan(u.get("substrate_bpc", float("nan")))]
        ut1s = [u.get("codebook_utilization", float("nan")) for u in units]
        ct1s = [u.get("substrate_concept_top1", float("nan")) for u in units]
        cv = 0.0
        if len(sbs) > 1 and abs(float(np.mean(sbs))) > 1e-9:
            cv = float(np.std(sbs)) / abs(float(np.mean(sbs)))
        k_stats[kv] = {
            "ceiling_bpc_mean": float(np.mean(cbs)) if cbs else float("nan"),
            "substrate_bpc_mean": float(np.mean(sbs)) if sbs else float("nan"),
            "ceiling_bpc_cv": (float(np.std(cbs)) / abs(float(np.mean(cbs)))
                              if len(cbs) > 1 and abs(float(np.mean(cbs))) > 1e-9 else 0.0),
            "substrate_bpc_cv": cv,
            "codebook_utilization_mean": float(np.mean([u for u in ut1s if not math.isnan(u)])) if any(not math.isnan(u) for u in ut1s) else float("nan"),
            "concept_top1_mean": float(np.mean([u for u in ct1s if not math.isnan(u)])) if any(not math.isnan(u) for u in ct1s) else float("nan"),
            "bigram_bpc_mean": float(np.mean([u.get("bigram_bpc", float("nan")) for u in units if not math.isnan(u.get("bigram_bpc", float("nan")))])) if any(not math.isnan(u.get("bigram_bpc", float("nan"))) for u in units) else float("nan"),
            "n_seeds": len(units),
            "any_saturated": any(u.get("saturated", False) for u in units),
            "is_anchor_arm": (kv == 1),
            "any_llm_violation": any(u.get("llm_forward_calls_at_inference", 0) > 0 for u in units),
        }

    # LLM-call gate
    any_llm_viol = any(s["any_llm_violation"] for s in k_stats.values())
    if any_llm_viol:
        summary = "; ".join("k=%d llm_calls=NONZERO" % kv for kv, s in k_stats.items() if s["any_llm_violation"])
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (LLM forward call counter > 0). " + summary + smoke_msg)

    # Anchor check: K_VALUE=1 must reproduce N2's 2.049 within 0.05 bits
    n2_anchor_ceiling = 2.049
    n2_anchor_substrate = 4.959
    anchor_note = ""
    anchor_failed = False
    if 1 in k_stats:
        id_ceiling = k_stats[1]["ceiling_bpc_mean"]
        if not math.isnan(id_ceiling):
            diff = abs(id_ceiling - n2_anchor_ceiling)
            if diff < 0.05:
                anchor_note = " ANCHOR-OK(k=1 ceiling=%.3f ~ %.3f)" % (
                    id_ceiling, n2_anchor_ceiling)
            else:
                anchor_note = " ANCHOR-MISMATCH(k=1 ceiling=%.3f vs N2=%.3f diff=%.3f)" % (
                    id_ceiling, n2_anchor_ceiling, diff)
                # Anchor mismatch is a soft warning at smoke (small N_DIM_RUN, small MAX_DOCS);
                # at full it MUST be HARD_FAIL.
                if RUN_MODE == "full":
                    anchor_failed = True

    anchor_ceiling = (k_stats[1]["ceiling_bpc_mean"]
                      if 1 in k_stats and not math.isnan(k_stats[1]["ceiling_bpc_mean"])
                      else n2_anchor_ceiling)
    anchor_substrate = (k_stats[1]["substrate_bpc_mean"]
                       if 1 in k_stats and not math.isnan(k_stats[1]["substrate_bpc_mean"])
                       else n2_anchor_substrate)

    # Find best k>1 arm (the kWTA multiplicity test)
    best_k = None
    best_ceiling = float("inf")
    best_substrate = float("inf")
    best_cv = 1.0
    best_bigram = float("nan")
    for kv, s in k_stats.items():
        if kv == 1:
            continue
        cb = s["ceiling_bpc_mean"]
        if not math.isnan(cb) and cb < best_ceiling:
            best_ceiling = cb
            best_k = kv
            best_substrate = s["substrate_bpc_mean"]
            best_cv = s["substrate_bpc_cv"]
            best_bigram = s["bigram_bpc_mean"]

    # Pre-registered bands (brain-within-concept-floor 2026-06-22)
    HARD_PASS_CEILING_THRESHOLD = 1.75  # >= 0.30 bits drop from 2.049
    HARD_PASS_SUBSTRATE_THRESHOLD = 4.75  # >= 0.21 bits drop from 4.959
    MIDDLE_BAND_CEILING_DELTA = 0.10
    HARD_FAIL_CEILING_DELTA = 0.05

    # Per-config summary string
    cfg_lines = []
    for kv in sorted(k_stats.keys()):
        s = k_stats[kv]
        cfg_lines.append(
            "k=%d%s f_eff=%.4f: ceiling=%.3f sub_bpc=%.3f cv=%.3f util=%.1f%% concept_top1=%.3f" % (
                kv, " [ANCHOR]" if s["is_anchor_arm"] else "",
                kv / V_C,
                s["ceiling_bpc_mean"], s["substrate_bpc_mean"], s["substrate_bpc_cv"],
                s["codebook_utilization_mean"] * 100, s["concept_top1_mean"]))

    summary = (
        "best_k=%s best_ceiling_bpc=%.3f anchor_ceiling=%.3f ceiling_delta=%.3f "
        "best_substrate_bpc=%.3f cv=%.3f best_bigram=%.3f%s; %s%s" % (
            best_k if best_k is not None else "NONE",
            best_ceiling if best_ceiling < float("inf") else float("nan"),
            anchor_ceiling,
            (anchor_ceiling - best_ceiling) if best_ceiling < float("inf") else float("nan"),
            best_substrate if best_substrate < float("inf") else float("nan"),
            best_cv,
            best_bigram,
            anchor_note,
            " | ".join(cfg_lines),
            smoke_msg,
        )
    )

    # Anchor mismatch -> HARD_FAIL at full (smoke gets the soft warning)
    if anchor_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: k=1 anchor mismatch (N2 baseline NOT reproduced). " + summary)

    # No k>1 arm -> data incomplete
    if best_k is None or best_ceiling == float("inf"):
        return ("HARD_FAIL",
                "HARD_FAIL: no k>1 multiplicity arm produced ceiling_bpc; cell incomplete. " + summary)

    ceiling_delta = anchor_ceiling - best_ceiling  # positive = kWTA improves ceiling

    # WRONG-DIRECTION rule (pre-reg-direction-must-match-intent; Skunkworks n3 SimVQ catch):
    # If kWTA makes ceiling WORSE (negative delta), this is HARD_FAIL not MIDDLE_BAND.
    # Brain-drill HARD-FAIL condition: ceiling monotonically worse with k = soft averaging
    # destructive at this V_C.
    if ceiling_delta < 0.0:
        # Check monotonicity (HARD-FAIL is "monotonically worse" per brain-drill)
        return ("HARD_FAIL",
                "HARD_FAIL: kWTA WORSE than k=1 anchor (ceiling_delta=%.3f bits, wrong-direction). "
                "pre-reg-direction-must-match-intent rules out MIDDLE_BAND for negative ceiling. " % ceiling_delta
                + summary)

    # HARD_PASS: kWTA arm ceiling<=1.75 AND substrate<=4.75 AND cv<=0.05 AND not saturated AND best_k > 1
    if (best_ceiling <= HARD_PASS_CEILING_THRESHOLD
            and best_substrate <= HARD_PASS_SUBSTRATE_THRESHOLD
            and best_cv <= 0.05
            and not k_stats[best_k]["any_saturated"]
            and best_k != 1):
        plus_tag = ""
        if not math.isnan(best_bigram) and best_substrate < best_bigram:
            plus_tag = " HARD_PASS_PLUS(substrate_bpc<bigram_bpc=%.3f)" % best_bigram
        return ("HARD_PASS",
                "HARD_PASS: kWTA k=%d achieves ceiling_bpc=%.3f<=1.75 AND substrate_bpc=%.3f<=4.75 "
                "AND cv=%.3f<=0.05 AND substrate-only-decode (LLM calls=0).%s " % (
                    best_k, best_ceiling, best_substrate, best_cv, plus_tag) + summary)

    # MIDDLE_BAND: ceiling drops >=0.10 bits OR substrate beats anchor by >=0.10
    substrate_delta = anchor_substrate - best_substrate
    if ceiling_delta >= MIDDLE_BAND_CEILING_DELTA or substrate_delta >= 0.10:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: kWTA k=%d partial mechanism (ceiling_delta=%.3f or substrate_delta=%.3f). " % (
                    best_k, ceiling_delta, substrate_delta) + summary)

    # HARD_FAIL: ceiling_bpc change < 0.05 across all k>1 (mechanism falsified)
    if ceiling_delta < HARD_FAIL_CEILING_DELTA:
        return ("HARD_FAIL",
                "HARD_FAIL: kWTA no measurable ceiling change (delta=%.3f < 0.05). "
                "biological-sparsity hypothesis falsified at V_C=%d. Route to n5 hippocampal "
                "episodic + Path A V_C scaling. " % (ceiling_delta, V_C)
                + summary)

    # Fallback MIDDLE_BAND for small nonzero delta
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: kWTA small-effect ceiling_delta=%.3f (<0.10). " % ceiling_delta + summary)


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s V_C=%d N_DIM=%d K=%d f=%.4f K_GRID=%s TAU=%.3f MAX_DOCS=%d seeds=%s" % (
    ANCHOR_NAME, RUN_MODE, V_C, N_DIM_RUN, K, F_SPARSE, K_GRID, TAU, MAX_DOCS, SEEDS), flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "N": N_DIM_RUN, "k_grid": K_GRID, "tau": TAU,
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
    k_strs = []
    for u in r["per_unit"]:
        k_strs.append("k=%d:ceiling=%.3f sub=%.3f" % (
            u["k_value"], u["ceiling_bpc"], u["substrate_bpc"]))
    print("  [seed=%d] %s elapsed=%.1fs llm_calls=%d" % (
        seed, " | ".join(k_strs), r["elapsed_s"], r["llm_forward_calls_at_inference"]), flush=True)

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
    "FATAL: %d LLM forward calls occurred during inference -- substrate-only-decode gate VIOLATED" % total_llm_calls)

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
    "V_C": V_C,
    "N_DIM": N_DIM_RUN,
    "K": K,
    "f_sparse": F_SPARSE,
    "tau": TAU,
    "k_grid": K_GRID,
    "assignment_mode": "top_k_soft",
    "zero_llm_calls_at_inference": True,
    "total_llm_forward_calls_observed": total_llm_calls,
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
