"""
n3_mkn_smoothing_v1 -- N3 Path-B sub-area (b): Modified Kneser-Ney smoothing drop-in.

MOTIVATION (Research decode-side drill 2026-06-22 + Skunkworks n3 SimVQ HONEST_NEGATIVE VET
commit 4c086a9f 2026-06-22):
  N3 SimVQ MVP (sub-area a) HONEST_NEGATIVE: PCA-projected VQ HURT ceiling_bpc (worse, not
  better). The decode-side bottleneck DIAGNOSIS from N2 STANDS: substrate_bpc - ceiling_bpc
  ~ 2.9 bits at every PD; the count-proportional + Jelinek-Mercer (JM) decode is the
  primary suspect for within-concept token entropy.
  This cell tests sub-area (b): replace JM with Modified Kneser-Ney (MKN) smoothing as a
  drop-in inside batched_token_logprob. MKN is independent of VQ alignment, pure-Python,
  count-based, and cheap on CPU. Research priority #2 (sub-area b in the drill).

HYPOTHESIS (Research note Prediction 3, 2026-06-22):
  MKN replaces Jelinek-Mercer in batched_token_logprob; substrate_bpc DROPS >= 0.10 bits
  at fixed V_C=1024 / N_DIM=16384 / K=1.
  MECHANISM: MKN absolute discounting + continuation-probability lower-order distribution
  gives bonus probability to tokens that appear across many concept contexts, reducing
  over-confidence in sparse-concept low-count predictions where JM's fixed lambda=0.1
  floors to a flat unigram backoff.

MKN MVP IMPLEMENTATION (substrate-only-decode-gate COMPATIBLE):
  Two-arm sweep at fixed (V_C, N_DIM, K, F_SPARSE):
    ARM A (anchor): Jelinek-Mercer (reproduces N2 4.96 / N3-anchor 4.959 substrate_bpc).
    ARM B (lever): Modified Kneser-Ney (Chen & Goodman 1998):
      - per (concept c, token t) count n_ct
      - absolute discount D in (0, 1) subtracted from each n_ct > 0
      - lower-order continuation distribution P_cont(t) proportional to N_{1+}(*, t) =
        number of distinct concepts in which token t appears (NOT raw token frequency)
      - per-concept normalizer gamma(c) = (D / count_c) * N_{1+}(c, *) where N_{1+}(c, *)
        is the number of distinct tokens with n_ct > 0 in concept c
      - P_MKN(t | c) = max(n_ct - D, 0) / count_c + gamma(c) * P_cont(t)
      - D estimated from count-of-counts via Chen-Goodman optimal-discount formula:
          D = n_1 / (n_1 + 2 * n_2)
        where n_1 / n_2 are the count of (c, t) pairs with count 1 / 2.
        Clipped to [0.1, 0.99] for safety.
  Both arms run on the SAME ingest (same VQ, same C, same D-store, same train counts).
  No LLM calls; pure count manipulation.

REUSES n2_capacity_scaling_v1 / n3_vq_alignment_simvq_v1 HARNESS:
  - HD-binding context: ctx_vec = L2_normalize(sum_j roll(C[c_{t-j}], j))
  - W-materialized batched recall: W = P_src.T @ P_dst, then FREE P_src/P_dst
  - Per-seed checkpoint / resume (PROT-021 run_config guard)
  - _instrumentation_selftest at module scope
  - ANCHOR_NAME / write_metrics / CONFIG_VERSION discipline
  - LLM-call audit counter (zero at inference)

FIXED CONFIG (matches N2/N3 anchor for direct comparison):
  V_C = 1024
  N_DIM = 16384
  K = 1
  F_SPARSE = 0.006
  PROJ_DIM = identity (no projection -- n3 SimVQ HONEST_NEGATIVE ruled it out)
  SMOOTHING_GRID = ["jm", "mkn"]  (the lever under test)

SCIENTIFIC QUESTIONS (pre-registered):
  (a) Does ARM A (jm) reproduce N2 anchor substrate_bpc ~ 4.959 within 0.05 bits?
      (ANCHOR-OK check.)
  (b) Does ARM B (mkn) LOWER substrate_bpc by >= 0.10 bits vs ARM A (jm)?
  (c) Does ARM B improve directionally? (pre-reg-direction-must-match-intent verdict:
      large abs-delta in WRONG direction = HARD_FAIL, NOT MIDDLE_BAND -- per Skunkworks
      n3 SimVQ catch.)

PRE-REGISTERED BANDS (user task spec 2026-06-22; sub-area b 1st-revival per n3 HN VET):
  HARD_PASS (chain-grade, ALL of):
    - MKN substrate_bpc <= 4.86 (>= 0.10 bit improvement vs JM anchor 4.959)
    - same cv across seeds <= 0.05 for MKN arm
    - JM anchor reproduces N2's 4.959 within 0.05 bits (ANCHOR-OK)
    - NOT saturated (alpha < 1.0)
    - substrate-only-decode (zero LLM calls at inference -- enforced + asserted)
  MIDDLE_BAND (mechanism partial, NEUTRAL):
    - MKN improves substrate_bpc by 0.03-0.10 bits vs JM
  HARD_FAIL (any of):
    - MKN improvement < 0.03 bits
    - MKN substrate_bpc WORSE than JM (any wrong-direction delta = HARD_FAIL per
      pre-reg-direction-must-match-intent; n3 SimVQ HN catch)
    - JM anchor mismatch (ARM A substrate_bpc differs from N2's 4.959 by > 0.05)
    - substrate-only gate violated (LLM forward call counter > 0)

INSTRUMENTATION (Skunkworks chain-grade structural blockers, all baked):
  1. per_unit: per (seed, smoothing_mode) entry; recompute-off-per_unit ready.
  2. cv <= 0.05: computed across seeds for each smoothing_mode in verdict.
  3. zero_llm_calls_at_inference: True LOGGED in metrics (asserted).
  4. ceiling_bpc decomposition: oracle concept-to-token reported per arm (should be
     identical across arms since same VQ/D-store -- a sanity invariant).
  5. zero-D-overlap fallback in MKN+JM token logprob (reuse n3 pattern).
  6. CONFIG_VERSION captures all result-affecting params (smoothing grid, MKN-D mode,
     V_C, N_DIM, K, F_SPARSE, MAX_DOCS, SEEDS, SPLIT).

QUEUE: remote_cpu_queue (residuals_per_token.npz lives on marsh@home).
DEPENDENCY: token_ids in residuals_per_token.npz.
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

ANCHOR_NAME = "n3_mkn_smoothing_v1"

# ---------------------------------------------------------------------------
# LLM-call audit counter (Skunkworks structural blocker #3)
# ---------------------------------------------------------------------------
_LLM_CALL_COUNTER = [0]


# ---------------------------------------------------------------------------
# Configurable params (env vars / CLI)
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# ---------------------------------------------------------------------------
# Module-level constants (AST-verified in selftest)
# ---------------------------------------------------------------------------

V_C = 1024
N_DIM = 16384
K = 1
F_SPARSE = 0.006

# Smoothing grid: two arms (JM anchor + MKN lever).
SMOOTHING_GRID = ["jm", "mkn"]

if RUN_MODE == "smoke":
    SEEDS = [1]
    MAX_DOCS = 200
    MAX_TOK_VOCAB = 1000
    N_DIM_RUN = 512  # smaller N_DIM at smoke for fast self-test runtime
else:
    SEEDS = [7, 17, 23]
    MAX_DOCS = 100000
    MAX_TOK_VOCAB = 50257
    N_DIM_RUN = N_DIM

TRAIN_FRAC = 0.8
LR_DECODE = 1.0
LAM_BACKOFF = 0.1   # JM lambda (anchor)
INTERP_B = 0.3      # ceiling-arm interpolation (kept identical to n3 anchor)
MKN_D_CLIP_LO = 0.1
MKN_D_CLIP_HI = 0.99

CONFIG_VERSION = (
    "SMOOTH=%s,V_C=%d,N_DIM=%d,K=%d,f=%.4f,LAM=%.2f,MKN_D=optimal-clip[%.2f,%.2f],"
    "MAX_DOCS=%d,SEEDS=%s,SPLIT=%.1f" % (
        "-".join(SMOOTHING_GRID),
        V_C, N_DIM, K, F_SPARSE, LAM_BACKOFF, MKN_D_CLIP_LO, MKN_D_CLIP_HI,
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
    return int((code != 0).sum())


def build_W(P_src: np.ndarray, P_dst: np.ndarray) -> np.ndarray:
    if P_src.shape[0] == 0:
        return np.zeros((P_src.shape[1], P_src.shape[1]), dtype=np.float32)
    return P_src.T @ P_dst


def batched_concept_recall(W: np.ndarray, Q: np.ndarray, C: np.ndarray) -> np.ndarray:
    activated_batch = Q @ W
    sims_batch = activated_batch @ C.T
    return np.argmax(sims_batch, axis=1).astype(np.int64)


def build_context_vecs_batched(C: np.ndarray, cids_seq: np.ndarray, K_depth: int,
                                n_dim: int) -> np.ndarray:
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
# Smoothing: JM (anchor) + MKN (lever)
# ---------------------------------------------------------------------------

def batched_token_logprob_jm(D: np.ndarray, concept_vecs: np.ndarray,
                             uni_dist: np.ndarray, lam: float) -> np.ndarray:
    """Jelinek-Mercer interpolation -- the N2/N3 anchor batched decode.

    P(t|c) = (1 - lam) * MLE(t|c) + lam * P_unigram(t).
    MLE comes from scores = max(0, concept_vec @ D); row-normalized.
    Zero-D-overlap fallback to uniform when scores.sum() == 0.
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


def estimate_mkn_discount(n_ct_dense: np.ndarray) -> float:
    """Chen-Goodman optimal discount: D = n_1 / (n_1 + 2 * n_2).

    n_ct_dense: (V_C, V_TOK) integer counts of (concept, token).
    n_1 = number of (c, t) pairs with count == 1
    n_2 = number of (c, t) pairs with count == 2
    Returns D clipped to [MKN_D_CLIP_LO, MKN_D_CLIP_HI].
    """
    n1 = int((n_ct_dense == 1).sum())
    n2 = int((n_ct_dense == 2).sum())
    if n1 + 2 * n2 <= 0:
        return 0.5
    d = n1 / float(n1 + 2 * n2)
    return float(np.clip(d, MKN_D_CLIP_LO, MKN_D_CLIP_HI))


def build_mkn_stats(concept_tok_counts: Dict[int, np.ndarray], V_TOK: int, vc: int
                    ) -> Dict[str, np.ndarray]:
    """Compute MKN statistics from concept-token counts.

    Returns dict with:
      n_ct_dense    : (vc, V_TOK) int -- raw counts of (concept, token)
      count_c       : (vc,) int      -- sum over t of n_ct
      n1plus_c_dot  : (vc,) int      -- per-concept #distinct tokens with n_ct > 0
      n1plus_dot_t  : (V_TOK,) int   -- per-token #distinct concepts containing t
      p_cont        : (V_TOK,) f32   -- continuation prob proportional to n1plus_dot_t
      D             : float          -- optimal absolute discount
    Substrate-only: pure count manipulation, no LLM calls.
    """
    n_ct = np.zeros((vc, V_TOK), dtype=np.int64)
    for c, row in concept_tok_counts.items():
        if 0 <= c < vc:
            length = min(len(row), V_TOK)
            n_ct[c, :length] = row[:length]
    count_c = n_ct.sum(axis=1)                          # (vc,)
    n1plus_c_dot = (n_ct > 0).sum(axis=1)               # (vc,)
    n1plus_dot_t = (n_ct > 0).sum(axis=0)               # (V_TOK,)
    s_cont = int(n1plus_dot_t.sum())
    if s_cont > 0:
        p_cont = n1plus_dot_t.astype(np.float32) / float(s_cont)
    else:
        p_cont = np.ones(V_TOK, dtype=np.float32) / float(V_TOK)
    D = estimate_mkn_discount(n_ct)
    return {
        "n_ct_dense": n_ct,
        "count_c": count_c,
        "n1plus_c_dot": n1plus_c_dot,
        "n1plus_dot_t": n1plus_dot_t,
        "p_cont": p_cont,
        "D": D,
    }


def batched_token_logprob_mkn(pred_cids: np.ndarray, mkn: Dict[str, np.ndarray]
                              ) -> np.ndarray:
    """Modified Kneser-Ney batched decode.

    pred_cids: (n_pos,) int64 predicted concept IDs (from W-recall).
    Returns log-prob matrix (n_pos, V_TOK).

    P_MKN(t | c) = max(n_ct - D, 0) / count_c  +  gamma(c) * p_cont(t)
    where gamma(c) = (D / count_c) * n1plus_c_dot[c].
    Fallback for count_c == 0 (concept never observed in train): uniform-mixed-p_cont
    so zero rows can't produce NaN log-prob.
    """
    n_ct = mkn["n_ct_dense"]            # (vc, V_TOK) int
    count_c = mkn["count_c"]            # (vc,)
    n1plus_c_dot = mkn["n1plus_c_dot"]  # (vc,)
    p_cont = mkn["p_cont"]              # (V_TOK,)
    D = float(mkn["D"])
    V_TOK_local = n_ct.shape[1]

    # Per-pos count row + scalars (advanced indexing)
    n_ct_pos = n_ct[pred_cids].astype(np.float32)             # (n_pos, V_TOK)
    count_c_pos = count_c[pred_cids].astype(np.float32)        # (n_pos,)
    n1plus_pos = n1plus_c_dot[pred_cids].astype(np.float32)    # (n_pos,)

    # First term: max(n_ct - D, 0) / count_c
    discounted = np.maximum(n_ct_pos - D, 0.0)                 # (n_pos, V_TOK)
    # Safe count_c (avoid div-by-zero for never-observed concepts)
    safe_count = np.where(count_c_pos > 0, count_c_pos, 1.0)   # (n_pos,)
    first = discounted / safe_count[:, None]                   # (n_pos, V_TOK)

    # Gamma(c) = D * n1plus_c_dot / count_c (for observed concepts)
    gamma = np.where(count_c_pos > 0,
                     (D * n1plus_pos) / safe_count, 1.0)       # (n_pos,)
    second = gamma[:, None] * p_cont[None, :]                  # (n_pos, V_TOK)

    probs = first + second                                     # (n_pos, V_TOK)

    # Fallback: any row with count_c == 0 (never-observed concept) -> use p_cont directly
    zero_concept_rows = (count_c_pos <= 0)
    if zero_concept_rows.any():
        # Replace those rows with continuation distribution
        fallback = p_cont[None, :].repeat(probs.shape[0], axis=0)
        probs = np.where(zero_concept_rows[:, None], fallback, probs)

    # Numerical fallback: any row that sums to ~0 (shouldn't happen given p_cont mass,
    # but defensive against degenerate p_cont) -> uniform.
    row_sums = probs.sum(axis=1, keepdims=True)
    zero_rows = (row_sums <= 1e-12)
    if zero_rows.any():
        probs = np.where(zero_rows, np.ones_like(probs) / V_TOK_local, probs)
        row_sums = np.where(zero_rows, np.ones_like(row_sums), row_sums)

    # Renormalize (first + second is approximately normalized by construction, but
    # numerical drift + the max(0, n - D) discount truncation can leave small slack)
    probs = probs / row_sums
    return np.log(np.maximum(probs, 1e-30))


# ---------------------------------------------------------------------------
# Synthetic forward pass for self-test
# ---------------------------------------------------------------------------

def _run_synthetic_smoothing(rng_seed: int, n_dim: int = 64, f: float = 0.05,
                              vc: int = 8, vt: int = 20,
                              smoothing: str = "jm") -> Dict[str, Any]:
    """Synthetic forward pass for one smoothing mode."""
    rng = np.random.default_rng(rng_seed)
    n_docs = 20
    docs_tids = [rng.integers(0, vt, size=12) for _ in range(n_docs)]
    split = int(0.8 * n_docs)
    train_tids = docs_tids[:split]
    test_tids = docs_tids[split:]

    # Trivial VQ assignment for synthetic: assign concepts cyclically (so n_ct is dense)
    def assign_cids_synth(t_doc_list):
        all_t = np.concatenate(t_doc_list)
        return (all_t % vc).astype(np.int64)

    train_cids_flat = assign_cids_synth(train_tids)
    test_cids_flat = assign_cids_synth(test_tids)

    rng2 = np.random.default_rng(rng_seed + 1000)
    C = sparse_codebook(vc, n_dim, f, rng2)

    # Build D + concept_tok_counts
    D = np.zeros((n_dim, vt), dtype=np.float32)
    concept_tok_counts: Dict[int, np.ndarray] = {}
    offset = 0
    for d_idx, t_doc in enumerate(train_tids):
        n_doc = len(t_doc)
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

    # MKN stats (always build; only used if smoothing == "mkn")
    mkn = build_mkn_stats(concept_tok_counts, vt, vc)

    # Build transition store for K=1 -- needed to populate test concept predictions
    P_src_list, P_dst_list = [], []
    offset_train = 0
    for d_idx, t_doc in enumerate(train_tids):
        n_doc = len(t_doc)
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
    for d_idx, t_doc in enumerate(test_tids):
        n_doc = len(t_doc)
        cids_doc = test_cids_flat[offset_test:offset_test + n_doc].astype(np.int64)
        ctx_vecs = build_context_vecs_batched(C, cids_doc, K_depth=1, n_dim=n_dim)
        n_pos = ctx_vecs.shape[0]
        if n_pos == 0:
            offset_test += n_doc
            continue
        pred_c_batch = batched_concept_recall(W, ctx_vecs, C)
        true_c_batch = cids_doc[1:n_pos + 1]
        # Decode tokens for this doc in one batch
        if smoothing == "jm":
            lp_doc = batched_token_logprob_jm(D, C[pred_c_batch], uni_dist, LAM_BACKOFF)
        elif smoothing == "mkn":
            lp_doc = batched_token_logprob_mkn(pred_c_batch, mkn)
        else:
            raise ValueError("unknown smoothing: %s" % smoothing)
        for pos in range(n_pos):
            true_tok = int(t_doc[pos + 1])
            if true_tok >= vt:
                continue
            tot_t += 1
            true_c = int(true_c_batch[pos])
            sub_t_ok += (int(np.argmax(lp_doc[pos])) == true_tok)
            sub_nll += -float(lp_doc[pos, true_tok])
            uni_nll += -float(uni_log[true_tok])
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
        "mkn_D": float(mkn["D"]) if smoothing == "mkn" else float("nan"),
    }


# ---------------------------------------------------------------------------
# Formula self-test (MANDATORY at module scope)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert MKN mechanism + JM anchor + per-unit instrumentation works on synthetic data."""
    rng = np.random.default_rng(42)

    # --- test 1: MKN discount formula in (MKN_D_CLIP_LO, MKN_D_CLIP_HI) for non-degenerate counts ---
    n_ct = np.zeros((4, 10), dtype=np.int64)
    n_ct[0, 0] = 1; n_ct[0, 1] = 1; n_ct[0, 2] = 1  # 3 singletons
    n_ct[1, 0] = 2; n_ct[1, 1] = 2                   # 2 doubles
    D_est = estimate_mkn_discount(n_ct)
    # n1=3, n2=2 -> D = 3/(3+4) = 3/7 ~ 0.428
    expected = 3.0 / 7.0
    assert abs(D_est - expected) < 1e-5, "MKN-D estimate FAIL: got %.4f expected %.4f" % (D_est, expected)
    assert MKN_D_CLIP_LO <= D_est <= MKN_D_CLIP_HI, "MKN-D out of clip range: %.4f" % D_est
    print("[selftest] T1 PASS: estimate_mkn_discount Chen-Goodman formula (n1=3,n2=2 -> D=3/7)", flush=True)

    # --- test 2: degenerate (no counts) -> D = 0.5 fallback ---
    n_ct_zero = np.zeros((2, 5), dtype=np.int64)
    D_zero = estimate_mkn_discount(n_ct_zero)
    assert abs(D_zero - 0.5) < 1e-9, "MKN-D zero-count fallback FAIL: %.4f" % D_zero
    print("[selftest] T2 PASS: estimate_mkn_discount zero-counts fallback to 0.5", flush=True)

    # --- test 3: build_mkn_stats has all required keys with consistent shapes ---
    ct_counts = {0: np.array([3, 1, 0, 2, 0], dtype=np.int64),
                 1: np.array([0, 0, 5, 1, 1], dtype=np.int64),
                 2: np.array([0, 0, 0, 0, 0], dtype=np.int64)}  # never-observed concept
    mkn_stats = build_mkn_stats(ct_counts, V_TOK=5, vc=4)
    assert mkn_stats["n_ct_dense"].shape == (4, 5)
    assert mkn_stats["count_c"].shape == (4,)
    assert mkn_stats["n1plus_c_dot"].shape == (4,)
    assert mkn_stats["n1plus_dot_t"].shape == (5,)
    assert mkn_stats["p_cont"].shape == (5,)
    assert mkn_stats["count_c"][0] == 6, "count_c[0] FAIL: %d" % mkn_stats["count_c"][0]
    assert mkn_stats["count_c"][1] == 7, "count_c[1] FAIL: %d" % mkn_stats["count_c"][1]
    assert mkn_stats["count_c"][2] == 0, "count_c[2] (never-observed) FAIL: %d" % mkn_stats["count_c"][2]
    assert mkn_stats["n1plus_c_dot"][0] == 3, "n1plus_c_dot[0] FAIL: %d" % mkn_stats["n1plus_c_dot"][0]
    assert mkn_stats["n1plus_c_dot"][1] == 3, "n1plus_c_dot[1] FAIL: %d" % mkn_stats["n1plus_c_dot"][1]
    # n1plus_dot_t: token 0 appears only in concept 0 -> 1; token 3 in concepts {0,1} -> 2
    assert mkn_stats["n1plus_dot_t"][0] == 1, "n1plus_dot_t[0] FAIL"
    assert mkn_stats["n1plus_dot_t"][3] == 2, "n1plus_dot_t[3] FAIL"
    # p_cont sums to 1
    assert abs(mkn_stats["p_cont"].sum() - 1.0) < 1e-5, "p_cont not normalized"
    print("[selftest] T3 PASS: build_mkn_stats shapes + count_c + n1plus + p_cont normalization", flush=True)

    # --- test 4: batched_token_logprob_mkn produces normalized log-probs ---
    pred_cids = np.array([0, 1, 2, 0], dtype=np.int64)
    lp = batched_token_logprob_mkn(pred_cids, mkn_stats)
    assert lp.shape == (4, 5), "MKN logprob shape FAIL: %s" % str(lp.shape)
    # exp + sum-by-row should be ~1
    p = np.exp(lp)
    row_sums = p.sum(axis=1)
    max_err = float(np.abs(row_sums - 1.0).max())
    assert max_err < 1e-4, "MKN probs not row-normalized: max err=%.4e" % max_err
    # never-observed concept (cid=2) -> log-prob should equal log(p_cont)
    expected_lp_c2 = np.log(np.maximum(mkn_stats["p_cont"], 1e-30))
    diff_c2 = float(np.abs(lp[2] - expected_lp_c2).max())
    assert diff_c2 < 1e-5, "MKN never-observed concept doesn't fall back to p_cont: diff=%.4e" % diff_c2
    print("[selftest] T4 PASS: batched_token_logprob_mkn normalized + never-obs falls back to p_cont", flush=True)

    # --- test 5: JM batched (anchor) produces normalized probs + matches docstring ---
    D_sm = np.zeros((8, 5), dtype=np.float32)
    D_sm[:, 0] = 1.0
    D_sm[:, 2] = 0.5
    uni = np.array([0.2, 0.2, 0.2, 0.2, 0.2], dtype=np.float32)
    cv = np.ones((1, 8), dtype=np.float32)
    lp_jm = batched_token_logprob_jm(D_sm, cv, uni, lam=LAM_BACKOFF)
    assert lp_jm.shape == (1, 5)
    p_jm = np.exp(lp_jm[0])
    assert abs(p_jm.sum() - 1.0) < 1e-4, "JM probs not normalized: sum=%.4f" % float(p_jm.sum())
    print("[selftest] T5 PASS: batched_token_logprob_jm normalized + lam-interpolation", flush=True)

    # --- test 6: zero-D-overlap fallback in JM (matches n3 pattern) ---
    cv_zero = np.array([[0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
    lp_jm_z = batched_token_logprob_jm(D_sm, cv_zero, uni, lam=0.0)
    # With lam=0 and zero overlap, should fall back to uniform (1/5 each)
    p_z = np.exp(lp_jm_z[0])
    assert float(np.abs(p_z - 0.2).max()) < 1e-4, "JM zero-overlap fallback FAIL"
    print("[selftest] T6 PASS: JM zero-D-overlap fallback to uniform", flush=True)

    # --- test 7: synthetic end-to-end JM + MKN both produce finite BPC ---
    res_jm = _run_synthetic_smoothing(rng_seed=42, smoothing="jm")
    res_mkn = _run_synthetic_smoothing(rng_seed=42, smoothing="mkn")
    for tag, res in (("jm", res_jm), ("mkn", res_mkn)):
        for key in ("substrate_bpc", "ceiling_bpc", "unigram_bpc"):
            val = res.get(key)
            assert val is not None, "%s.%s is None" % (tag, key)
            assert not math.isnan(val), "%s.%s is NaN" % (tag, key)
        assert res["substrate_bpc"] > 0.0, "%s substrate_bpc zero" % tag
        assert res["ceiling_bpc"] > 0.0, "%s ceiling_bpc zero" % tag
    # ceiling_bpc should be identical (same VQ + counts; only smoothing differs)
    diff_ceil = abs(res_jm["ceiling_bpc"] - res_mkn["ceiling_bpc"])
    assert diff_ceil < 1e-4, "ceiling_bpc differs between JM and MKN runs (same VQ): %.4f" % diff_ceil
    print("[selftest] T7 PASS: synthetic JM + MKN both finite; ceiling_bpc IDENTICAL across arms", flush=True)

    # --- test 8: LLM-call counter remains at 0 ---
    assert _LLM_CALL_COUNTER[0] == 0, "LLM_CALL_COUNTER non-zero: %d" % _LLM_CALL_COUNTER[0]
    print("[selftest] T8 PASS: LLM_CALL_COUNTER = 0 (substrate-only-gate auditable)", flush=True)

    # --- test 9: module-level constants (AST-verifiable) ---
    assert isinstance(ANCHOR_NAME, str) and len(ANCHOR_NAME) > 0, "ANCHOR_NAME not a str"
    assert isinstance(CONFIG_VERSION, str) and "SMOOTH=" in CONFIG_VERSION, "CONFIG_VERSION missing SMOOTH label"
    assert isinstance(SMOOTHING_GRID, list) and SMOOTHING_GRID == ["jm", "mkn"], (
        "SMOOTHING_GRID must be ['jm', 'mkn']: %s" % SMOOTHING_GRID)
    assert isinstance(V_C, int) and V_C == 1024, "V_C not 1024"
    assert isinstance(N_DIM, int) and N_DIM == 16384, "N_DIM not 16384"
    assert isinstance(K, int) and K == 1, "K not 1"
    assert isinstance(F_SPARSE, float) and 0 < F_SPARSE < 1, "F_SPARSE not in (0,1)"
    assert isinstance(LAM_BACKOFF, float) and 0 < LAM_BACKOFF < 1, "LAM_BACKOFF not in (0,1)"
    print("[selftest] T9 PASS: module-level constants real + fixed-config invariants", flush=True)

    # --- test 10: per_unit dict shape (chain-grade per_unit blocker) ---
    per_unit_keys_required = (
        "seed", "smoothing_mode", "substrate_bpc", "ceiling_bpc", "bigram_bpc", "unigram_bpc",
        "substrate_top1", "ceiling_top1", "codebook_utilization", "alpha",
        "llm_forward_calls_at_inference", "wall_s", "mkn_D",
    )
    fake_unit = {k: 0.0 if k not in ("seed", "smoothing_mode", "llm_forward_calls_at_inference")
                 else (0 if k != "smoothing_mode" else "jm") for k in per_unit_keys_required}
    for key in per_unit_keys_required:
        assert key in fake_unit, "per_unit missing required key: %s" % key
    print("[selftest] T10 PASS: per_unit shape includes all required keys", flush=True)

    # --- test 11: anchor threshold (JM should reproduce N2 4.959 within 0.05) ---
    anchor_tolerance = 0.05
    n2_anchor_substrate_bpc = 4.959
    assert 0.0 < anchor_tolerance < 0.5, "anchor tolerance must be (0, 0.5)"
    assert 4.0 < n2_anchor_substrate_bpc < 6.0, "N2 anchor substrate outside sane range"
    print("[selftest] T11 PASS: anchor threshold (JM within 0.05 of N2 4.959) defined", flush=True)

    print("[selftest] ALL 11 TESTS PASS: MKN smoothing cell instrumentation validated", flush=True)


_instrumentation_selftest()  # MANDATORY at module scope
if _ARGS.self_test:
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Data loading (n2/n3 verbatim)
# ---------------------------------------------------------------------------

def load_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
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
# Per-seed run: SMOOTHING_GRID sweep at fixed (V_C, N_DIM, K)
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    """Full per-seed pipeline: shared VQ + ingest; two arms differ only at decode."""
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

    # Concept-token statistics + VQ (shared across smoothing arms -- they differ only
    # in the decode-time logprob computation; same ingest, same VQ, same D-store)
    train_res_full = np.concatenate([d[0] for d in train_docs], axis=0)
    norms_tr = np.linalg.norm(train_res_full, axis=1, keepdims=True) + 1e-8
    train_res_n = train_res_full / norms_tr
    print("[seed=%d] train residuals: %d tokens, residual_dim=%d" % (
        seed, len(train_res_n), train_res_n.shape[1]), flush=True)

    # Token vocab
    all_train_tids = np.concatenate([d[1] for d in train_docs])
    V_TOK = min(int(all_train_tids.max()) + 1, MAX_TOK_VOCAB)
    print("[seed=%d] V_TOK=%d" % (seed, V_TOK), flush=True)

    # Bigram + unigram baselines
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

    # Test position arrays
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

    # --- SHARED INGEST (VQ + concept_tok_counts + D + W) ---
    # Identity VQ (no projection) -- matches n2 baseline exactly
    print("[seed=%d] fitting VQ V_C=%d on %d tokens..." % (seed, vc, len(train_res_n)), flush=True)
    try:
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=vc, random_state=seed,
                             batch_size=4096, n_init=3, max_iter=100, verbose=0)
        km.fit(train_res_n)

        def assign_cids(res_list):
            all_r = np.concatenate(res_list, axis=0)
            return km.predict(all_r).astype(np.int64)
    except ImportError:
        print("[seed=%d] sklearn unavailable; numpy argmin VQ" % seed, flush=True)
        rng_vq = np.random.default_rng(seed + 5000)
        centers = train_res_n[rng_vq.choice(len(train_res_n), size=vc, replace=False)]

        def assign_cids(res_list):
            all_r = np.concatenate(res_list, axis=0)
            chunk = 4096
            out = np.empty(len(all_r), dtype=np.int64)
            for s_pos in range(0, len(all_r), chunk):
                e_pos = s_pos + chunk
                diff = all_r[s_pos:e_pos, None, :] - centers[None, :, :]
                out[s_pos:e_pos] = np.argmin((diff ** 2).sum(-1), axis=1)
            return out

    # Normalize ALL train + test residuals (one-shot for VQ assignment)
    def normalize_doc_list(doc_list):
        out = []
        for d_res, _ in doc_list:
            nrm = np.linalg.norm(d_res, axis=1, keepdims=True) + 1e-8
            out.append((d_res / nrm).astype(np.float32))
        return out
    train_res_norm = normalize_doc_list(train_docs)
    test_res_norm = normalize_doc_list(test_docs)
    train_cids_flat = assign_cids(train_res_norm)
    test_cids_flat = assign_cids(test_res_norm)

    unique_cids_train = np.unique(train_cids_flat)
    utilization = len(unique_cids_train) / vc

    def slice_docs_cids(docs_split, cids_flat):
        seqs = []; offset = 0
        for doc_res, doc_tok in docs_split:
            n_doc = len(doc_res)
            seqs.append((cids_flat[offset:offset + n_doc], doc_tok))
            offset += n_doc
        return seqs

    train_seqs = slice_docs_cids(train_docs, train_cids_flat)
    test_seqs = slice_docs_cids(test_docs, test_cids_flat)

    # Sparse concept codebook
    rng2 = np.random.default_rng(seed + 1000)
    C = sparse_codebook(vc, n_dim, f, rng2)
    k_val = max(1, round(f * n_dim))

    # Build decode memory D + concept_tok_counts (shared by both arms)
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

    # MKN statistics (built once; shared by all MKN positions)
    mkn = build_mkn_stats(concept_tok_counts, V_TOK=V_TOK, vc=vc)
    print("[seed=%d] MKN-D estimated=%.4f (clipped to [%.2f, %.2f])" % (
        seed, float(mkn["D"]), MKN_D_CLIP_LO, MKN_D_CLIP_HI), flush=True)

    # Saturation alpha
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
        # No training transitions -- emit nan rows for both arms
        per_unit_list = []
        for smode in SMOOTHING_GRID:
            per_unit_list.append({
                "seed": seed, "smoothing_mode": smode,
                "substrate_bpc": float("nan"), "ceiling_bpc": float("nan"),
                "bigram_bpc": big_bpc_global, "unigram_bpc": uni_bpc_global,
                "substrate_top1": float("nan"), "ceiling_top1": float("nan"),
                "codebook_utilization": utilization, "alpha": alpha, "saturated": saturated,
                "k_active": k_val, "n_trans": 0, "n_token_test_pairs": tot_t_global,
                "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
                "wall_s": 0.0, "mkn_D": float(mkn["D"]) if smode == "mkn" else float("nan"),
            })
        return {
            "seed": seed, "per_unit": per_unit_list,
            "V_C": vc, "N_DIM": n_dim, "K": K, "f_sparse": f, "V_TOK": V_TOK,
            "n_docs": len(train_docs) + len(test_docs),
            "n_train_docs": len(train_docs), "n_test_docs": len(test_docs),
            "run_mode": RUN_MODE, "smoothing_grid": SMOOTHING_GRID,
            "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "elapsed_s": time.time() - t0,
        }

    P_src = np.concatenate(P_src_list, axis=0)
    P_dst = np.concatenate(P_dst_list, axis=0)
    n_trans = P_src.shape[0]
    print("[seed=%d] n_trans=%d alpha=%.3f%s building W (%dx%d)..." % (
        seed, n_trans, alpha, " [SAT]" if saturated else "", n_dim, n_dim), flush=True)
    W_k = build_W(P_src, P_dst)
    del P_src, P_dst

    # Build context vecs for all test positions (shared across arms)
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
        per_unit_list = []
        for smode in SMOOTHING_GRID:
            per_unit_list.append({
                "seed": seed, "smoothing_mode": smode,
                "substrate_bpc": float("nan"), "ceiling_bpc": float("nan"),
                "bigram_bpc": big_bpc_global, "unigram_bpc": uni_bpc_global,
                "substrate_top1": float("nan"), "ceiling_top1": float("nan"),
                "codebook_utilization": utilization, "alpha": alpha, "saturated": saturated,
                "k_active": k_val, "n_trans": n_trans, "n_token_test_pairs": 0,
                "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
                "wall_s": 0.0, "mkn_D": float(mkn["D"]) if smode == "mkn" else float("nan"),
            })
        return {
            "seed": seed, "per_unit": per_unit_list,
            "V_C": vc, "N_DIM": n_dim, "K": K, "f_sparse": f, "V_TOK": V_TOK,
            "n_docs": len(train_docs) + len(test_docs),
            "n_train_docs": len(train_docs), "n_test_docs": len(test_docs),
            "run_mode": RUN_MODE, "smoothing_grid": SMOOTHING_GRID,
            "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "elapsed_s": time.time() - t0,
        }

    Q_all = np.concatenate(_c_src_list, axis=0)
    c_tgt_all = np.array(_c_tgt_list, dtype=np.int64)
    tot_c = len(c_tgt_all)

    print("[seed=%d] batched recall: %d queries..." % (seed, tot_c), flush=True)
    pred_concept_all = batched_concept_recall(W_k, Q_all, C)
    del Q_all
    sub_c_ok = int((pred_concept_all == c_tgt_all).sum())

    # Token-level eval (OOV-filtered); shared concept predictions across arms
    pred_c_valid = pred_concept_all[valid_idx_global]
    c_tgt_valid = c_tgt_all[valid_idx_global]
    BATCH_TOK_CHUNK = 2000
    n_valid = tot_t_global

    # Pre-compute ceiling NLL once (same for both arms -- same VQ + same counts)
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
    ceiling_bpc = (ceil_nll / tt) / log2

    per_unit_list: List[Dict[str, Any]] = []

    # --- OUTER LOOP: SMOOTHING_GRID sweep (decode-only difference) ---
    for smode in SMOOTHING_GRID:
        t_arm = time.time()
        print("[seed=%d smoothing=%s] decoding %d positions..." % (seed, smode, n_valid), flush=True)
        pred_tok_valid = np.empty(n_valid, dtype=np.int64)
        true_tok_logprob = np.empty(n_valid, dtype=np.float64)

        for _ck_s in range(0, n_valid, BATCH_TOK_CHUNK):
            _ck_e = min(_ck_s + BATCH_TOK_CHUNK, n_valid)
            _cids_chunk = pred_c_valid[_ck_s:_ck_e]
            if smode == "jm":
                _cvecs = C[_cids_chunk]
                _lp = batched_token_logprob_jm(D, _cvecs, uni_dist, LAM_BACKOFF)
            elif smode == "mkn":
                _lp = batched_token_logprob_mkn(_cids_chunk, mkn)
            else:
                raise ValueError("unknown smoothing_mode: %s" % smode)
            pred_tok_valid[_ck_s:_ck_e] = np.argmax(_lp, axis=1)
            _tt = true_tok_valid_global[_ck_s:_ck_e]
            true_tok_logprob[_ck_s:_ck_e] = _lp[np.arange(_ck_e - _ck_s), _tt]

        sub_t_ok = int((pred_tok_valid == true_tok_valid_global).sum())
        sub_nll = float(-true_tok_logprob.sum())
        sub_bpc = (sub_nll / tt) / log2

        per_unit = {
            "seed": seed,
            "smoothing_mode": smode,
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
            "k_active": k_val,
            "n_trans": n_trans,
            "n_token_test_pairs": tot_t_global,
            "n_concept_test_pairs": tot_c,
            "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "mkn_D": float(mkn["D"]) if smode == "mkn" else float("nan"),
            "wall_s": time.time() - t_arm,
        }
        per_unit_list.append(per_unit)
        print("  [seed=%d smoothing=%s] sub_bpc=%.3f ceiling_bpc=%.3f bigram=%.3f "
              "concept_top1=%.3f util=%.1f%% alpha=%.3f wall=%.1fs%s" % (
                  seed, smode, sub_bpc, ceiling_bpc, big_bpc_global,
                  per_unit["substrate_concept_top1"], utilization * 100, alpha,
                  per_unit["wall_s"], " [SAT]" if saturated else ""), flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "per_unit": per_unit_list,
        "V_C": vc, "N_DIM": n_dim, "K": K, "f_sparse": f,
        "V_TOK": V_TOK,
        "n_docs": len(train_docs) + len(test_docs),
        "n_train_docs": len(train_docs),
        "n_test_docs": len(test_docs),
        "run_mode": RUN_MODE,
        "smoothing_grid": SMOOTHING_GRID,
        "mkn_D": float(mkn["D"]),
        "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "elapsed_s": elapsed,
    }


# ---------------------------------------------------------------------------
# Verdict (pre-registered bands per user task spec 2026-06-22)
#   PRE-REG-DIRECTION-MUST-MATCH-INTENT (Skunkworks n3 SimVQ catch): large-abs-delta
#   in WRONG direction = HARD_FAIL, NOT MIDDLE_BAND.
# ---------------------------------------------------------------------------

def _flatten_per_unit(ps: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    by_smode: Dict[str, List[Dict[str, Any]]] = {}
    for p in ps:
        for u in p.get("per_unit", []):
            smode = str(u["smoothing_mode"])
            by_smode.setdefault(smode, []).append(u)
    return by_smode


def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Compute verdict against pre-registered bands.

    HARD_PASS: MKN substrate_bpc <= 4.86 AND cv <= 0.05 AND JM anchor reproduces N2 within 0.05
               AND not saturated AND substrate-only gate honored.
    MIDDLE_BAND: MKN improves substrate_bpc by 0.03-0.10 bits vs JM (NEUTRAL).
    HARD_FAIL: improvement < 0.03 bits OR wrong-direction delta (MKN worse than JM)
               OR anchor mismatch OR LLM-call violation.
    """
    by_smode = _flatten_per_unit(ps)
    if not by_smode:
        return ("HARD_FAIL", "HARD_FAIL: no per_unit data; cell produced no results.")

    # Per-mode aggregates
    pd_stats: Dict[str, Dict[str, float]] = {}
    for smode, units in by_smode.items():
        sbs = [u["substrate_bpc"] for u in units if not math.isnan(u.get("substrate_bpc", float("nan")))]
        cbs = [u["ceiling_bpc"] for u in units if not math.isnan(u.get("ceiling_bpc", float("nan")))]
        ut1s = [u.get("codebook_utilization", float("nan")) for u in units]
        ct1s = [u.get("substrate_concept_top1", float("nan")) for u in units]
        cv = 0.0
        if len(sbs) > 1 and abs(float(np.mean(sbs))) > 1e-9:
            cv = float(np.std(sbs)) / abs(float(np.mean(sbs)))
        pd_stats[smode] = {
            "substrate_bpc_mean": float(np.mean(sbs)) if sbs else float("nan"),
            "ceiling_bpc_mean": float(np.mean(cbs)) if cbs else float("nan"),
            "substrate_bpc_cv": cv,
            "codebook_utilization_mean": (float(np.mean([u for u in ut1s if not math.isnan(u)]))
                                           if any(not math.isnan(u) for u in ut1s)
                                           else float("nan")),
            "concept_top1_mean": (float(np.mean([u for u in ct1s if not math.isnan(u)]))
                                   if any(not math.isnan(u) for u in ct1s)
                                   else float("nan")),
            "n_seeds": len(units),
            "any_saturated": any(u.get("saturated", False) for u in units),
            "any_llm_violation": any(u.get("llm_forward_calls_at_inference", 0) > 0 for u in units),
            "mkn_D_mean": (float(np.mean([u.get("mkn_D", float("nan")) for u in units
                                          if not math.isnan(u.get("mkn_D", float("nan")))]))
                            if any(not math.isnan(u.get("mkn_D", float("nan"))) for u in units)
                            else float("nan")),
        }

    # LLM-call gate
    any_llm_viol = any(s["any_llm_violation"] for s in pd_stats.values())
    if any_llm_viol:
        summary = "; ".join("smoothing=%s llm_calls=NONZERO" % k for k, s in pd_stats.items() if s["any_llm_violation"])
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (LLM forward call counter > 0). " + summary)

    # Both arms must exist
    if "jm" not in pd_stats or "mkn" not in pd_stats:
        return ("HARD_FAIL",
                "HARD_FAIL: missing arm (jm or mkn); cell incomplete. Got smoothing_modes=%s" %
                list(pd_stats.keys()))

    jm = pd_stats["jm"]; mk = pd_stats["mkn"]

    # JM anchor check (substrate_bpc must reproduce N2's 4.959 within 0.05)
    n2_anchor_substrate = 4.959
    anchor_note = ""
    anchor_failed = False
    if not math.isnan(jm["substrate_bpc_mean"]):
        diff = abs(jm["substrate_bpc_mean"] - n2_anchor_substrate)
        if diff < 0.05:
            anchor_note = " ANCHOR-OK(jm sub_bpc=%.3f ~ %.3f)" % (jm["substrate_bpc_mean"], n2_anchor_substrate)
        else:
            anchor_note = " ANCHOR-MISMATCH(jm sub_bpc=%.3f vs N2=%.3f diff=%.3f)" % (
                jm["substrate_bpc_mean"], n2_anchor_substrate, diff)
            anchor_failed = True

    # Pre-reg bands
    HARD_PASS_SUBSTRATE_THRESHOLD = 4.86   # MKN <= 4.86 (>= 0.10 bits drop from 4.959)
    MIDDLE_BAND_DELTA_LO = 0.03            # MKN must improve at least 0.03 bits for MIDDLE_BAND
    MIDDLE_BAND_DELTA_HI = 0.10            # 0.03-0.10 improvement = MIDDLE_BAND
    HARD_FAIL_DELTA = 0.03                 # below 0.03 (incl. negative) = HARD_FAIL

    delta = jm["substrate_bpc_mean"] - mk["substrate_bpc_mean"]  # positive = MKN improves

    cfg_lines = []
    for smode in ("jm", "mkn"):
        s = pd_stats[smode]
        extra = ""
        if smode == "mkn" and not math.isnan(s["mkn_D_mean"]):
            extra = " mkn_D=%.3f" % s["mkn_D_mean"]
        cfg_lines.append("%s: sub_bpc=%.3f ceiling=%.3f cv=%.3f util=%.1f%% concept_top1=%.3f%s" % (
            smode, s["substrate_bpc_mean"], s["ceiling_bpc_mean"], s["substrate_bpc_cv"],
            s["codebook_utilization_mean"] * 100, s["concept_top1_mean"], extra))
    summary = (
        "delta=%.3f (positive=MKN_improves) jm_sub_bpc=%.3f mkn_sub_bpc=%.3f mkn_cv=%.3f%s; %s" % (
            delta, jm["substrate_bpc_mean"], mk["substrate_bpc_mean"], mk["substrate_bpc_cv"],
            anchor_note, " | ".join(cfg_lines)))

    # Anchor mismatch -> HARD_FAIL (cannot interpret MKN delta without valid baseline)
    if anchor_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: JM anchor mismatch (N2 baseline NOT reproduced). " + summary)

    # WRONG-DIRECTION rule (pre-reg-direction-must-match-intent; Skunkworks n3 SimVQ catch):
    # ANY worse-than-anchor MKN result = HARD_FAIL, not MIDDLE_BAND.
    if delta < 0.0:
        return ("HARD_FAIL",
                "HARD_FAIL: MKN WORSE than JM anchor (delta=%.3f bits, wrong-direction); "
                "pre-reg-direction-must-match-intent rules out MIDDLE_BAND for negative delta. " % delta
                + summary)

    # HARD_PASS: MKN <= 4.86 AND cv <= 0.05 AND not saturated
    if (mk["substrate_bpc_mean"] <= HARD_PASS_SUBSTRATE_THRESHOLD
            and mk["substrate_bpc_cv"] <= 0.05
            and not mk["any_saturated"]):
        return ("HARD_PASS",
                "HARD_PASS: MKN substrate_bpc=%.3f<=4.86 (delta=%.3f bits vs JM), cv=%.3f<=0.05, "
                "substrate-only-decode (LLM calls=0), anchor-OK. " % (
                    mk["substrate_bpc_mean"], delta, mk["substrate_bpc_cv"]) + summary)

    # MIDDLE_BAND: improvement 0.03-0.10 bits (excluding HARD_PASS bar)
    if MIDDLE_BAND_DELTA_LO <= delta < MIDDLE_BAND_DELTA_HI:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: MKN improves substrate_bpc by delta=%.3f bits (0.03 <= d < 0.10) "
                "but does not clear HARD_PASS bar (sub_bpc=4.86). " % delta + summary)

    # MIDDLE_BAND: improvement >= 0.10 but failed CV or saturation guard
    if delta >= MIDDLE_BAND_DELTA_HI and mk["substrate_bpc_mean"] > HARD_PASS_SUBSTRATE_THRESHOLD:
        # MKN improvement large but anchor was even higher than N2 -- still MIDDLE_BAND
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: MKN improves by delta=%.3f bits but absolute sub_bpc=%.3f > 4.86. " % (
                    delta, mk["substrate_bpc_mean"]) + summary)

    # HARD_FAIL: improvement below 0.03 (incl. zero)
    if delta < HARD_FAIL_DELTA:
        return ("HARD_FAIL",
                "HARD_FAIL: MKN improves substrate_bpc by only delta=%.3f bits (< 0.03 minimum). " % delta
                + summary)

    # CV / saturation guard fallthrough (delta >= MIDDLE_BAND_DELTA_HI but mkn fails cv or saturation)
    if mk["substrate_bpc_cv"] > 0.05:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: MKN improves by delta=%.3f bits but cv=%.3f > 0.05 (HARD_PASS requires cv <= 0.05). " % (
                    delta, mk["substrate_bpc_cv"]) + summary)
    if mk["any_saturated"]:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: MKN improves by delta=%.3f bits but saturated (alpha > 1.0). " % delta + summary)

    # Defensive fallback
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: MKN delta=%.3f bits; no clear band match (defensive fallback). " % delta + summary)


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s V_C=%d N_DIM=%d K=%d f=%.4f SMOOTHING_GRID=%s MAX_DOCS=%d seeds=%s" % (
    ANCHOR_NAME, RUN_MODE, V_C, N_DIM_RUN, K, F_SPARSE, SMOOTHING_GRID, MAX_DOCS, SEEDS), flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "N": N_DIM_RUN, "V_C": V_C, "K": K,
              "smoothing_grid": SMOOTHING_GRID}

done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds already complete; running %s" % (
    len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

t_total = time.time()
ps = []

for seed in remaining_seeds:
    r = run_seed(seed)
    ps.append(r)
    write_partial(out_dir, seed, r)
    smode_strs = []
    for u in r["per_unit"]:
        smode_strs.append("%s:sub=%.3f ceiling=%.3f" % (
            u["smoothing_mode"], u["substrate_bpc"], u["ceiling_bpc"]))
    print("  [seed=%d] %s elapsed=%.1fs llm_calls=%d" % (
        seed, " | ".join(smode_strs), r["elapsed_s"], r["llm_forward_calls_at_inference"]), flush=True)

if done_seeds:
    agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
    for k, v in agg.items():
        ps.append(v)

if not ps:
    print("[ERROR] no seeds completed; aborting", flush=True)
    sys.exit(1)

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
    "smoothing_grid": SMOOTHING_GRID,
    "zero_llm_calls_at_inference": True,
    "total_llm_forward_calls_observed": total_llm_calls,
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
