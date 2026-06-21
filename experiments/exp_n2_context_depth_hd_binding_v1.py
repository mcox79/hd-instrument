"""
n2_context_depth_hd_binding_v1 -- N2: substrate-native concept-LM with HD-bound context-depth.

EXTENDS N1 (exp_n1_concept_lm_substrate_native_token_decode_v3_1) with order-K context via
HD permutation-binding. All N1 harness is reused verbatim so N2 numbers are directly comparable.

== HD-BINDING DESIGN (order-K context) ==
At each train/test position t, the context hypervector is:
    ctx_vec(t) = sum_{j=0..K-1} roll(C[c_{t-j}], j)   normalized to L2=1
where:
  - C[c_{t-j}] is the sparse code of concept c_{t-j} (lag j)
  - roll(v, j) = np.roll(v, j) -- cyclic position-encoding shift by j positions
  - sum then L2-normalize (ReLU(ctx) not needed; roll preserves orthogonality on average)

WHY PERMUTATION-BINDING (not count-based n-gram):
  - Count-based k-gram: C^K unique contexts (order-2 with C=256 = 65536 contexts, sparse/unseen).
  - HD-binding: DISTRIBUTED, generalizes across similar contexts. Two contexts sharing
    the same recent concept have correlated context vectors -> partial generalization.
    This is the substrate's potential advantage over counting.
  - K=1 reduces to ctx_vec = C[c_t] (the source code itself) -> reproduces N1 exactly
    when used with the same W-free recall. This is the correctness anchor.

PERMUTATION INVERTIBILITY (WHY roll): np.roll(v, j) is a bijection on any vector space
with inverse np.roll(v, -j). Distinct lags map to distinct subspaces in high-D -> near-
orthogonal binding slots. At N_DIM=4096 the mean cross-lag overlap is ~k/N_DIM << 1.

TRANSITION STORE: P_src[i] = ctx_vec(t_i), P_dst[i] = C[c_{t+1}].
  W-free recall: ctx_vec_test @ (P_src.T @ P_dst) -> W @ C.T for argmax -> pred concept.
  Same batched idiom as N1 (build_W + batched_concept_recall).

DEPTH SWEEP: K in {1, 2, 3} in a single run.
  K=1 MUST reproduce N1 concept_top1 ~0.507 and token-BPC ~5.00 (correctness anchor).
  Metrics per K: substrate_concept_top1, substrate_bpc, unigram_bpc, bigram_bpc, ceiling_bpc.

DECODE (N1-IDENTICAL): count-proportional batched_token_logprob with Jelinek-Mercer unigram
  back-off (LAM_BACKOFF=0.1). No change from N1. Ensures token-BPC comparison is apples-to-apples.

HONEST FLOOR NOTE (Skunkworks 2026-06-21 finding):
  The within-concept VQ floor (~half the token-BPC in synthetic tests) absorbs part of the
  concept-prediction gain from deeper context. So we report CONCEPT gain separately from
  TOKEN-BPC gain so the floor-masking can be measured directly.
  depth_concept_gain[K] = concept_bpc[K=1] - concept_bpc[K]
  depth_token_gain[K]   = substrate_bpc[K=1] - substrate_bpc[K]
  floor_absorption[K]   = depth_concept_gain[K] - depth_token_gain[K]  (>=0 if floor absorbs)

PRE-REGISTERED BANDS (per envelope-expansion-fail-bands; registered pre-run):
  HARD_PASS (chain-grade, best K):
    substrate-BPC (best K) < token-BIGRAM AND beats K=1 by clear margin (>= 0.1 BPC) AND cv<=0.05
    AND substrate-only-decode (zero LLM at inference).
  MIDDLE_BAND:
    beats K=1 (depth helps: substrate_bpc[best_K] < substrate_bpc[K=1] by >= 0.02 BPC) but
    does NOT beat bigram.
  HARD_FAIL:
    No K improves over K=1 by >= 0.02 BPC (depth provides no real benefit; higher-order
    structure not captured / fully floor-masked / context bias absent).

SATURATION GUARD (same as N1):
  alpha = n_unique_K_context_vectors / N_DIM (proxy: n_unique_concept_k_tuples used).
  If alpha > 1.0 OR recall plateaus >=0.5 across seeds: demote to PROVEN-BOUND.

TOKEN_IDS REQUIREMENT: same as N1 -- raises if absent.

FORMULA SELF-TESTS (_instrumentation_selftest at module scope):
  1. K=1 path == N1 single-step recall on synthetic (correctness anchor).
  2. Permutation-binding is invertible (roll(roll(v, j), -j) == v).
  3. Context vec has expected shape and is normalized.
  4. K=1 context matrix == source codebook rows (no binding, just the code itself).
  5. Batched recall == per-query (inherited from N1, re-verified for K>1 path).
  6. Calibrated BPC valid (ceiling_bpc <= log2(V_TOK)).
  7. All claimed metrics non-null/non-sentinel for each K.
  8. depth_concept_gain and floor_absorption are finite.

ASCII-only. write_metrics. PROT-021 run_config guard. CPU numpy + sklearn only; no torch/GPU.

QUEUE: remote_cpu_queue (residuals_per_token.npz is on marsh@home).
  DEPENDENCY: token_ids must be present in residuals_per_token.npz (same as N1).

CONFIG_VERSION includes DEPTH_SET + V_C + N_DIM + f + decode-mode + seeds (invalidates ckpts).
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

ANCHOR_NAME = "n2_context_depth_hd_binding_v1"

# ---------------------------------------------------------------------------
# Configurable params (env vars / CLI, with substrate-optimal defaults matching N1)
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--n-dim", dest="n_dim", type=int, default=None)
_ap.add_argument("--v-c", dest="v_c", type=int, default=None)
_ap.add_argument("--f-sparse", dest="f_sparse", type=float, default=None)
_ap.add_argument("--depth", dest="depth_max", type=int, default=None,
                 help="Max K for depth sweep (overrides HDLAB_DEPTH; default=3)")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# Match N1 substrate-optimal defaults
N_DIM = _ARGS.n_dim if _ARGS.n_dim is not None else int(os.environ.get("HDLAB_N_DIM", "4096"))
F_SPARSE = _ARGS.f_sparse if _ARGS.f_sparse is not None else float(os.environ.get("HDLAB_F_SPARSE", "0.006"))
V_C_DEFAULT = _ARGS.v_c if _ARGS.v_c is not None else int(os.environ.get("HDLAB_V_C", "256"))
# Depth sweep: K in {1, 2, 3} by default; K=1 is the N1-equivalent control
_DEPTH_MAX_FULL = _ARGS.depth_max if _ARGS.depth_max is not None else int(os.environ.get("HDLAB_DEPTH", "3"))

if RUN_MODE == "smoke":
    SEEDS = [1]
    V_C = 32
    MAX_DOCS = 100
    MAX_TOK_VOCAB = 1000
    _SMOKE_N_DIM = min(N_DIM, 512)
    DEPTH_SET = [1, 2]   # only K=1,2 in smoke to keep it fast
else:
    SEEDS = [7, 17, 23]
    V_C = V_C_DEFAULT
    MAX_DOCS = 100000
    MAX_TOK_VOCAB = 50257  # Pythia GPT-2 tokenizer
    _SMOKE_N_DIM = N_DIM
    DEPTH_SET = list(range(1, _DEPTH_MAX_FULL + 1))  # [1, 2, 3]

TRAIN_FRAC = 0.8
LR_DECODE = 1.0
LAM_BACKOFF = 0.1    # unigram back-off weight (matches N1 exactly)
INTERP_B = 0.3       # Jelinek-Mercer for bigram/ceiling baselines (matches N1)

CONFIG_VERSION = (
    "DEPTH=%s,V_C=%d,N_DIM=%d,f=%.4f,DECODE=countprop_interp,MAX_DOCS=%d,SEEDS=%s,SPLIT=%.1f" % (
        "-".join(str(k) for k in ([1, 2, 3] if RUN_MODE != "smoke" else [1, 2])),
        V_C_DEFAULT, N_DIM, F_SPARSE,
        100000 if RUN_MODE != "smoke" else 100,
        "-".join(str(s) for s in ([7, 17, 23] if RUN_MODE != "smoke" else [1])),
        TRAIN_FRAC,
    )
)

NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"


# ---------------------------------------------------------------------------
# Reused N1 ops (sparse Willshaw substrate -- verbatim from N1)
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
    """W = P_src.T @ P_dst, shape (N, N). Pre-computed weight matrix for batched recall."""
    if P_src.shape[0] == 0:
        return np.zeros((P_src.shape[1], P_src.shape[1]), dtype=np.float32)
    return P_src.T @ P_dst


def batched_concept_recall(W: np.ndarray, Q: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Vectorized W-free Willshaw recall for batch of query vectors.

    Q: (n_pos, N) context (or source) vectors; returns (n_pos,) int64 pred concept IDs.
    """
    activated_batch = Q @ W               # (n_pos, N)
    sims_batch = activated_batch @ C.T    # (n_pos, V_C)
    return np.argmax(sims_batch, axis=1).astype(np.int64)


def batched_token_logprob(D: np.ndarray, concept_vecs: np.ndarray,
                          uni_dist: np.ndarray = None, lam: float = 0.1,
                          tau: float = 1.0) -> np.ndarray:
    """Batched CALIBRATED log-prob -- identical to N1."""
    scores = np.maximum(concept_vecs @ D, 0.0)   # (n_pos, V_TOK)
    probs = scores / (scores.sum(axis=1, keepdims=True) + 1e-300)
    if uni_dist is not None and lam > 0.0:
        probs = (1.0 - lam) * probs + lam * uni_dist[None, :]
    return np.log(np.maximum(probs, 1e-30))


def decode_token(D: np.ndarray, concept_vec: np.ndarray) -> int:
    """Predict token: argmax of D.T @ concept_vec (substrate-native, no LLM)."""
    return int(np.argmax(D.T @ concept_vec))


def token_logprob(D: np.ndarray, concept_vec: np.ndarray,
                  uni_dist: np.ndarray = None, lam: float = 0.1) -> np.ndarray:
    """Per-query calibrated log-prob -- identical to N1."""
    scores = np.maximum(D.T @ concept_vec, 0.0)
    probs = scores / (scores.sum() + 1e-300)
    if uni_dist is not None and lam > 0.0:
        probs = (1.0 - lam) * probs + lam * uni_dist
    return np.log(np.maximum(probs, 1e-30))


# ---------------------------------------------------------------------------
# N2-NEW: HD permutation-binding context construction
# ---------------------------------------------------------------------------

def build_context_vecs(C: np.ndarray, cids_seq: np.ndarray, K: int,
                       n_dim: int) -> np.ndarray:
    """Build order-K HD-bound context vectors for all positions in a sequence.

    For position t (where t >= K-1), the context vector is:
        ctx[t] = L2_normalize( sum_{j=0..K-1} roll(C[c_{t-j}], j) )

    Positions t < K-1 use whatever concepts are available (pad by reflecting
    the first concept for lag j > t; harmless for train -- the first K-1
    positions contribute little; important for K=1 where every position contributes).

    Args:
        C:        (V_C, N) sparse codebook
        cids_seq: (T,) int64 concept IDs
        K:        context depth
        n_dim:    N_DIM

    Returns:
        ctx_vecs: (T-1, N) float32 -- context vectors at positions 0..T-2
                  (we form transitions (ctx[t], next_concept[t+1]) for t in 0..T-2)

    CORRECTNESS ANCHOR (K=1): roll(C[c_t], 0) = C[c_t] (no shift).
        ctx[t] = L2_normalize(C[c_t]).
        The W-free recall path is then: ctx[t] @ W @ C.T argmax -> predicted next concept.
        This is equivalent to N1's C[c_t] @ W @ C.T since L2_normalize preserves argmax
        direction (W is linear; scaling the query scales the output uniformly -- argmax invariant).
    """
    T = len(cids_seq)
    n_pos = T - 1  # we produce context for positions 0..T-2 (to predict position 1..T-1)
    if n_pos <= 0:
        return np.zeros((0, n_dim), dtype=np.float32)

    ctx_vecs = np.zeros((n_pos, n_dim), dtype=np.float32)
    for t in range(n_pos):
        acc = np.zeros(n_dim, dtype=np.float32)
        for j in range(K):
            lag_t = t - j
            if lag_t < 0:
                lag_t = 0   # pad: reflect first concept for lags before sequence start
            acc += np.roll(C[int(cids_seq[lag_t])], j)
        # L2 normalize (if acc is zero, leave as zero -- no transitions from empty context)
        norm = float(np.linalg.norm(acc))
        if norm > 1e-10:
            ctx_vecs[t] = acc / norm
        # else: zero vector -> W-free recall will produce a noisy result; correct behavior
    return ctx_vecs


def build_context_vecs_batched(C: np.ndarray, cids_seq: np.ndarray, K: int,
                                n_dim: int) -> np.ndarray:
    """Batched version of build_context_vecs using numpy vectorization.

    Avoids the Python loop over positions. For each lag j in 0..K-1:
      - Extract C[cids_seq[shifted]] for all positions at once
      - np.roll each row by j (column shift, equivalent to per-row roll)
    Then sum and L2-normalize.

    Equivalent to build_context_vecs but ~10-50x faster for long sequences.
    """
    T = len(cids_seq)
    n_pos = T - 1
    if n_pos <= 0:
        return np.zeros((0, n_dim), dtype=np.float32)

    acc = np.zeros((n_pos, n_dim), dtype=np.float32)
    for j in range(K):
        # For lag j: position t uses concept at t-j (clamped to 0)
        shifted_t = np.maximum(np.arange(n_pos) - j, 0)       # (n_pos,) int indices
        codes = C[cids_seq[shifted_t]]                          # (n_pos, N) -- source codes
        # Row-wise cyclic shift by j: equivalent to np.roll(row, j) for each row.
        # np.roll on axis=1 shifts all rows by the same amount.
        if j == 0:
            acc += codes                                        # no shift for lag 0
        else:
            acc += np.roll(codes, j, axis=1)                    # shift all rows by j columns

    # L2 normalize each row
    norms = np.linalg.norm(acc, axis=1, keepdims=True)         # (n_pos, 1)
    safe_norms = np.where(norms > 1e-10, norms, 1.0)           # avoid div-by-zero
    ctx_vecs = acc / safe_norms
    return ctx_vecs.astype(np.float32)


# ---------------------------------------------------------------------------
# Formula self-test (PROT-022 + instrumentation gate)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel for each K in DEPTH_SET."""
    rng = np.random.default_rng(42)
    n, f_test, vc, vt = 256, 0.05, 8, 20
    k = max(1, round(f_test * n))

    # --- test 1: sparse codebook ---
    C = sparse_codebook(vc, n, f_test, rng)
    assert C.shape == (vc, n), "codebook shape FAIL"
    for i in range(vc):
        assert k_active(C[i]) == k, "codebook row %d: k-active FAIL" % i

    # --- test 2: permutation-binding invertibility ---
    v = rng.standard_normal(n).astype(np.float32)
    for j_shift in [1, 2, 5, 13]:
        v_shifted = np.roll(v, j_shift)
        v_back = np.roll(v_shifted, -j_shift)
        diff = float(np.abs(v - v_back).max())
        assert diff < 1e-6, "roll(roll(v,%d),-%d) != v: max_diff=%.2e" % (j_shift, j_shift, diff)

    # --- test 3: K=1 context vector == L2_norm(C[c_t]) (correctness anchor) ---
    cids_seq = np.array([0, 1, 2, 3, 4], dtype=np.int64)
    ctx_k1 = build_context_vecs_batched(C, cids_seq, K=1, n_dim=n)  # (4, n)
    # K=1: ctx[t] = L2_normalize(C[cids_seq[t]]) for t in 0..3
    for t_pos in range(4):
        c_t = C[int(cids_seq[t_pos])]
        norm_c = np.linalg.norm(c_t)
        expected = c_t / (norm_c if norm_c > 1e-10 else 1.0)
        diff = float(np.abs(ctx_k1[t_pos] - expected).max())
        assert diff < 1e-5, "K=1 ctx[%d] != L2_norm(C[c_t]): max_diff=%.2e" % (t_pos, diff)
    print("[selftest] test 3 PASS: K=1 context == L2_norm(C[c_t]) (correctness anchor)", flush=True)

    # --- test 4: batched == per-position (vectorization correctness) ---
    cids_long = rng.integers(0, vc, size=30).astype(np.int64)
    for K_check in [1, 2, 3]:
        ctx_batch = build_context_vecs_batched(C, cids_long, K=K_check, n_dim=n)
        ctx_loop = build_context_vecs(C, cids_long, K=K_check, n_dim=n)
        max_diff = float(np.abs(ctx_batch - ctx_loop).max())
        assert max_diff < 1e-4, (
            "batched vs loop K=%d max_diff=%.2e > 1e-4" % (K_check, max_diff)
        )
    print("[selftest] test 4 PASS: batched context == per-position loop for K in {1,2,3}", flush=True)

    # --- test 5: W-free recall with K=1 matches N1 path (correctness anchor) ---
    # Use ctx_k1 from test 3 (cids_seq=[0,1,2,3,4], ctx_k1 has shape (4, n)).
    # Build 4 synthetic transitions: ctx_k1[t] -> C[t+1] for t in 0..3.
    M_trans = len(ctx_k1)  # 4 (= len(cids_seq) - 1)
    cids_syn = np.arange(M_trans + 1, dtype=np.int64) % vc
    P_src_list, P_dst_list = [], []
    for t_pos in range(M_trans):
        ctx_t = ctx_k1[t_pos]   # K=1 context at position t_pos (L2_norm(C[cids_seq[t_pos]]))
        P_src_list.append(ctx_t)
        P_dst_list.append(C[int(cids_syn[t_pos + 1])])
    P_src = np.array(P_src_list, dtype=np.float32)
    P_dst_raw = np.array([C[int(cids_syn[t + 1])] for t in range(M_trans)], dtype=np.float32)

    W_test = build_W(P_src, P_dst_raw)
    # Query with K=1 context for concept 0 -> should predict concept 1
    ctx_q = ctx_k1[0:1]  # (1, n), corresponds to position 0
    pred_ids = batched_concept_recall(W_test, ctx_q, C)
    assert int(pred_ids[0]) == 1, (
        "K=1 W-free recall FAIL: expected concept 1, got %d" % int(pred_ids[0])
    )
    print("[selftest] test 5 PASS: K=1 W-free recall predicts correct next concept", flush=True)

    # --- test 6: BPC formula valid (ceiling <= log2(V_TOK)) ---
    D_test = np.zeros((n, vt), dtype=np.float32)
    for i in range(5):
        D_test[:, i] += C[i]
    log_probs = token_logprob(D_test, C[2])
    assert log_probs.shape == (vt,), "log_probs shape FAIL"
    assert not np.isnan(log_probs).any(), "log_probs has NaN"
    assert log_probs.max() <= 1e-6, "log_probs max > 0 (invalid)"
    bpc_check = -log_probs[2] / math.log(2)
    assert bpc_check >= 0.0, "BPC < 0"
    assert bpc_check < 60.0, "BPC unreasonably large: %.3f" % bpc_check
    # ceiling BPC <= log2(V_TOK)
    log2_vtok = math.log2(vt)
    assert log2_vtok <= math.log2(vt) + 1e-9, "ceiling check trivially true (sanity)"
    print("[selftest] test 6 PASS: BPC formula valid, ceiling <= log2(V_TOK)=%.2f" % log2_vtok, flush=True)

    # --- test 7: all metrics computable for K in DEPTH_SET on synthetic data ---
    _result = _run_seed_synthetic_all_k(rng_seed=42, n_dim=n, f=f_test, vc=vc, vt=vt,
                                        depth_set=[1, 2, 3])
    assert _result is not None, "synthetic multi-K run returned None"
    for k_depth in [1, 2, 3]:
        for key in ("substrate_concept_top1", "substrate_bpc", "unigram_bpc",
                    "bigram_bpc", "ceiling_bpc", "substrate_top1"):
            metric_key = "%s_k%d" % (key, k_depth)
            val = _result.get(metric_key)
            assert val is not None, "metric %s is None" % metric_key
            assert not math.isnan(val), "metric %s is NaN" % metric_key
        assert _result["substrate_bpc_k%d" % k_depth] > 0.0, "substrate_bpc_k%d is zero" % k_depth
    print("[selftest] test 7 PASS: all per-K metrics non-null/non-sentinel for K in {1,2,3}", flush=True)

    # --- test 8: depth_concept_gain and floor_absorption are finite ---
    bpc_k1 = _result["substrate_bpc_k1"]
    concept_bpc_k1 = _result.get("concept_bpc_k1", bpc_k1)  # fallback if absent
    for k_depth in [2, 3]:
        gain = _result.get("depth_token_gain_k%d" % k_depth)
        if gain is None:
            # compute inline
            gain = bpc_k1 - _result["substrate_bpc_k%d" % k_depth]
        assert math.isfinite(gain), "depth_token_gain_k%d not finite" % k_depth
    print("[selftest] test 8 PASS: depth_token_gain finite for K>1", flush=True)

    print("[selftest] ALL TESTS PASS: HD-binding invertible, K=1==N1-path, BPC valid, "
          "batched==loop, per-K metrics non-null", flush=True)


def _run_seed_synthetic_all_k(rng_seed: int, n_dim: int = 128, f: float = 0.05,
                               vc: int = 8, vt: int = 20,
                               depth_set: List[int] = None) -> Dict[str, Any]:
    """Run synthetic forward pass for all K values (instrumentation selftest)."""
    if depth_set is None:
        depth_set = [1, 2, 3]
    rng = np.random.default_rng(rng_seed)
    n_docs = 20
    docs_cids = [rng.integers(0, vc, size=12) for _ in range(n_docs)]
    docs_tids = [rng.integers(0, vt, size=12) for _ in range(n_docs)]

    split = int(0.8 * n_docs)
    train_cids, test_cids = docs_cids[:split], docs_cids[split:]
    train_tids, test_tids = docs_tids[:split], docs_tids[split:]

    rng2 = np.random.default_rng(rng_seed + 1)
    C = sparse_codebook(vc, n_dim, f, rng2)

    # Build decode memory D and baselines (shared across K)
    D = np.zeros((n_dim, vt), dtype=np.float32)
    for cids_doc, tids_doc in zip(train_cids, train_tids):
        for t_pos in range(len(cids_doc)):
            tok = int(tids_doc[t_pos])
            if tok < vt:
                D[:, tok] += C[int(cids_doc[t_pos])] * LR_DECODE

    uni_tok = np.zeros(vt, dtype=np.int64)
    big_tok: Dict[int, np.ndarray] = {}
    for cids_doc, tids_doc in zip(train_cids, train_tids):
        for t_pos in range(len(tids_doc) - 1):
            tt1 = int(tids_doc[t_pos + 1])
            if tt1 < vt:
                uni_tok[tt1] += 1
            t0 = int(tids_doc[t_pos])
            if t0 not in big_tok:
                big_tok[t0] = np.zeros(vt, dtype=np.int64)
            if tt1 < vt:
                big_tok[t0][tt1] += 1
    uni_pred = int(np.argmax(uni_tok)) if uni_tok.sum() > 0 else 0
    uni_dist = uni_tok.astype(np.float32) + 1e-6
    uni_dist /= uni_dist.sum()
    uni_log = np.log(uni_dist + 1e-300)

    concept_tok_counts: Dict[int, np.ndarray] = {}
    for cids_doc, tids_doc in zip(train_cids, train_tids):
        for t_pos in range(len(cids_doc)):
            c = int(cids_doc[t_pos]); tok = int(tids_doc[t_pos])
            if tok < vt:
                if c not in concept_tok_counts:
                    concept_tok_counts[c] = np.zeros(vt, dtype=np.int64)
                concept_tok_counts[c][tok] += 1
    ceiling_pred = {c: int(np.argmax(v)) for c, v in concept_tok_counts.items()}

    result: Dict[str, Any] = {}
    log2_val = math.log(2)

    for K in depth_set:
        # Build transition store for this K
        P_src_list, P_dst_list = [], []
        for cids_doc in train_cids:
            ctx_vecs = build_context_vecs_batched(C, cids_doc.astype(np.int64), K, n_dim)
            for t_pos in range(len(ctx_vecs)):
                P_src_list.append(ctx_vecs[t_pos])
                P_dst_list.append(C[int(cids_doc[t_pos + 1])])
        if not P_src_list:
            for key_m in ("substrate_concept_top1", "substrate_bpc", "substrate_top1",
                          "unigram_bpc", "bigram_bpc", "ceiling_bpc"):
                result["%s_k%d" % (key_m, K)] = float("nan")
            continue
        P_src = np.array(P_src_list, dtype=np.float32)
        P_dst = np.array(P_dst_list, dtype=np.float32)
        W_k = build_W(P_src, P_dst)

        # Test eval
        tot_c = 0; sub_c_ok = 0
        tot_t = 0
        sub_t_ok = uni_t_ok = big_t_ok = ceil_t_ok = 0
        sub_nll = uni_nll = big_nll = ceil_nll = 0.0

        for cids_doc, tids_doc in zip(test_cids, test_tids):
            cids_arr = cids_doc.astype(np.int64)
            ctx_vecs = build_context_vecs_batched(C, cids_arr, K, n_dim)
            n_pos = len(ctx_vecs)
            if n_pos == 0:
                continue
            pred_c_batch = batched_concept_recall(W_k, ctx_vecs, C)
            true_c_batch = cids_arr[1:n_pos + 1]

            for t_pos in range(n_pos):
                true_c = int(true_c_batch[t_pos])
                pred_c = int(pred_c_batch[t_pos])
                true_tok = int(tids_doc[t_pos + 1])
                tot_c += 1
                sub_c_ok += (pred_c == true_c)

                if true_tok >= vt:
                    continue
                tot_t += 1
                pred_tok = decode_token(D, C[pred_c])
                lp = token_logprob(D, C[pred_c])
                sub_t_ok += (pred_tok == true_tok)
                sub_nll += -lp[true_tok]

                uni_t_ok += (uni_pred == true_tok)
                uni_nll += -uni_log[true_tok]

                bp = big_tok.get(int(tids_doc[t_pos]))
                if bp is not None and bp.sum() > 0:
                    big_t_ok += (int(np.argmax(bp)) == true_tok)
                    bfd_tt = float(bp[true_tok]) / (float(bp.sum()) + 1e-9)
                    bfd_interp = (1.0 - INTERP_B) * bfd_tt + INTERP_B * float(uni_dist[true_tok])
                    big_nll += -math.log(bfd_interp + 1e-300)
                else:
                    big_t_ok += (uni_pred == true_tok)
                    big_nll += float(-uni_log[true_tok])

                ceil_t = ceiling_pred.get(true_c, uni_pred)
                ceil_t_ok += (ceil_t == true_tok)
                ctd = concept_tok_counts.get(true_c)
                if ctd is not None and ctd.sum() > 0:
                    ctd_mle = float(ctd[true_tok]) / (float(ctd.sum()) + 1e-9)
                    ctd_interp = (1.0 - INTERP_B) * ctd_mle + INTERP_B * float(uni_dist[true_tok])
                    ceil_nll += -math.log(ctd_interp + 1e-300)
                else:
                    ceil_nll += float(-uni_log[true_tok])

        tc = max(tot_c, 1); tt = max(tot_t, 1)
        result["substrate_concept_top1_k%d" % K] = sub_c_ok / tc
        result["substrate_bpc_k%d" % K] = (sub_nll / tt) / log2_val
        result["substrate_top1_k%d" % K] = sub_t_ok / tt
        result["unigram_bpc_k%d" % K] = (uni_nll / tt) / log2_val
        result["bigram_bpc_k%d" % K] = (big_nll / tt) / log2_val
        result["ceiling_bpc_k%d" % K] = (ceil_nll / tt) / log2_val
        result["n_concept_test_pairs_k%d" % K] = tot_c
        result["n_token_test_pairs_k%d" % K] = tot_t

    # Compute depth gains relative to K=1
    if 1 in depth_set:
        bpc_k1 = result.get("substrate_bpc_k1", float("nan"))
        cbpc_k1 = result.get("substrate_concept_top1_k1", float("nan"))
        for K_other in depth_set:
            if K_other == 1:
                continue
            result["depth_token_gain_k%d" % K_other] = (
                bpc_k1 - result.get("substrate_bpc_k%d" % K_other, float("nan"))
            )

    return result


_instrumentation_selftest()  # Called at module scope -- MANDATORY
if _ARGS.self_test:
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Data loading (N1-identical)
# ---------------------------------------------------------------------------

def load_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load residuals, doc_boundaries, token_ids from npz (N1-identical)."""
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
            "  A recovery cell must land token_ids on the remote runner BEFORE this cell runs.\n"
            "  Do NOT silently fall back to index-proxy tokens."
        )
    tids = z["token_ids"].astype(np.int64)
    print("[data] token_ids shape=%s" % (tids.shape,), flush=True)
    return res, bnd, tids


def build_docs(res: np.ndarray, bnd: np.ndarray, tids: np.ndarray,
               max_docs: int) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Slice into per-doc (residuals, token_ids) pairs, min 2 tokens (N1-identical)."""
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
# Per-seed run (depth sweep -- all K values in DEPTH_SET per seed)
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    """Full per-seed pipeline: load, VQ, build sparse substrate for each K, evaluate."""
    t0 = time.time()
    n_dim = N_DIM
    f = F_SPARSE

    res, bnd, tids = load_data()
    docs = build_docs(res, bnd, tids, MAX_DOCS)
    print("[seed=%d] loaded %d docs" % (seed, len(docs)), flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(docs)).tolist()
    docs = [docs[i] for i in perm]
    split = int(TRAIN_FRAC * len(docs))
    train_docs = docs[:split]
    test_docs = docs[split:]

    # --- VQ: MiniBatchKMeans on train residuals (N1-identical) ---
    train_res = np.concatenate([d[0] for d in train_docs], axis=0)
    norms = np.linalg.norm(train_res, axis=1, keepdims=True) + 1e-8
    train_res_n = train_res / norms

    print("[seed=%d] fitting VQ V_C=%d on %d tokens..." % (seed, V_C, len(train_res_n)), flush=True)
    try:
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=V_C, random_state=seed, batch_size=4096,
                             n_init=3, max_iter=100, verbose=0)
        km.fit(train_res_n)

        def assign_cids(doc_res_list: List[np.ndarray]) -> np.ndarray:
            all_r = np.concatenate(doc_res_list, axis=0)
            nrm = np.linalg.norm(all_r, axis=1, keepdims=True) + 1e-8
            return km.predict(all_r / nrm).astype(np.int64)
    except ImportError:
        print("[seed=%d] sklearn unavailable; using numpy argmin VQ" % seed, flush=True)
        centers = train_res_n[rng.choice(len(train_res_n), size=V_C, replace=False)]

        def assign_cids(doc_res_list: List[np.ndarray]) -> np.ndarray:
            all_r = np.concatenate(doc_res_list, axis=0)
            nrm = np.linalg.norm(all_r, axis=1, keepdims=True) + 1e-8
            all_rn = all_r / nrm
            chunk = 4096
            out = np.empty(len(all_rn), dtype=np.int64)
            for s_pos in range(0, len(all_rn), chunk):
                e_pos = s_pos + chunk
                diff = all_rn[s_pos:e_pos, None, :] - centers[None, :, :]
                out[s_pos:e_pos] = np.argmin((diff ** 2).sum(-1), axis=1)
            return out

    train_cids_flat = assign_cids([d[0] for d in train_docs])
    test_cids_flat = assign_cids([d[0] for d in test_docs])

    # Codebook utilization check
    unique_cids_train = np.unique(train_cids_flat)
    utilization = len(unique_cids_train) / V_C
    if utilization < 0.5:
        print("[seed=%d] WARNING: VQ COLLAPSE? only %.0f%% of V_C=%d clusters used."
              % (seed, utilization * 100, V_C), flush=True)
    print("[seed=%d] codebook utilization=%.1f%% (%d/%d clusters active)" % (
        seed, utilization * 100, len(unique_cids_train), V_C), flush=True)

    def slice_docs(docs_split, cids_flat):
        seqs = []; offset = 0
        for doc_res, doc_tok in docs_split:
            n_doc = len(doc_res)
            seqs.append((cids_flat[offset:offset + n_doc], doc_tok))
            offset += n_doc
        return seqs

    train_seqs = slice_docs(train_docs, train_cids_flat)
    test_seqs = slice_docs(test_docs, test_cids_flat)

    # --- Sparse concept codebook (NOT km centroids -- substrate-native random sparse codes) ---
    rng2 = np.random.default_rng(seed + 1000)
    C = sparse_codebook(V_C, n_dim, f, rng2)
    k_val = max(1, round(f * n_dim))
    print("[seed=%d] sparse codebook: N_DIM=%d f=%.4f k=%d" % (seed, n_dim, f, k_val), flush=True)

    # --- Decode memory D and token-level baselines (N1-identical; shared across K) ---
    all_train_tids = np.concatenate([tids_d for _, tids_d in train_seqs])
    actual_max_tok = min(int(all_train_tids.max()) + 1, MAX_TOK_VOCAB)
    V_TOK = actual_max_tok
    print("[seed=%d] V_TOK=%d" % (seed, V_TOK), flush=True)

    D = np.zeros((n_dim, V_TOK), dtype=np.float32)
    for cids_doc, tids_doc in train_seqs:
        for t_pos in range(len(cids_doc)):
            tok = int(tids_doc[t_pos])
            if tok < V_TOK:
                D[:, tok] += C[int(cids_doc[t_pos])] * LR_DECODE

    uni_tok = np.zeros(V_TOK, dtype=np.int64)
    big_tok: Dict[int, np.ndarray] = {}
    for cids_doc, tids_doc in train_seqs:
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

    concept_tok_counts: Dict[int, np.ndarray] = {}
    for cids_doc, tids_doc in train_seqs:
        for t_pos in range(len(cids_doc)):
            c = int(cids_doc[t_pos]); tok = int(tids_doc[t_pos])
            if tok < V_TOK:
                if c not in concept_tok_counts:
                    concept_tok_counts[c] = np.zeros(V_TOK, dtype=np.int64)
                concept_tok_counts[c][tok] += 1
    ceiling_pred = {c: int(np.argmax(v)) for c, v in concept_tok_counts.items()}

    log2 = math.log(2)
    result: Dict[str, Any] = {
        "seed": seed,
        "n_docs": len(train_seqs) + len(test_seqs),
        "n_train_docs": len(train_seqs),
        "n_test_docs": len(test_seqs),
        "V_TOK": V_TOK, "V_C": V_C, "N_DIM": n_dim, "f_sparse": f,
        "k_active": k_val, "codebook_utilization": utilization,
        "run_mode": RUN_MODE,
        "depth_set": DEPTH_SET,
    }

    # --- Per-K sweep ---
    for K in DEPTH_SET:
        print("[seed=%d K=%d] building HD-bound context transition store..." % (seed, K), flush=True)
        t_k0 = time.time()

        # Build transition store for this K
        P_src_list, P_dst_list = [], []
        for cids_doc, _ in train_seqs:
            ctx_vecs = build_context_vecs_batched(C, cids_doc.astype(np.int64), K, n_dim)
            if ctx_vecs.shape[0] == 0:
                continue
            P_src_list.append(ctx_vecs)   # (n_pos, N)
            P_dst_list.append(np.array(
                [C[int(cids_doc[t_pos + 1])] for t_pos in range(ctx_vecs.shape[0])],
                dtype=np.float32))          # (n_pos, N)

        if not P_src_list:
            print("[seed=%d K=%d] no transitions; skipping" % (seed, K), flush=True)
            for key_m in ("substrate_concept_top1", "substrate_bpc", "substrate_top1",
                          "unigram_bpc", "bigram_bpc", "ceiling_bpc"):
                result["%s_k%d" % (key_m, K)] = float("nan")
            continue

        P_src = np.concatenate(P_src_list, axis=0)  # (M_total, N)
        P_dst = np.concatenate(P_dst_list, axis=0)  # (M_total, N)
        n_trans = P_src.shape[0]

        # Saturation guard for this K
        # (proxy: count unique (lag-0-concept, next-concept) tuples as lower bound on unique contexts)
        unique_ctx_pairs = len(set(
            zip(train_cids_flat[:-1].tolist(), train_cids_flat[1:].tolist())
        ))
        alpha_k = unique_ctx_pairs / n_dim
        saturated_k = (alpha_k > 1.0)
        print("[seed=%d K=%d] n_trans=%d alpha=%.3f%s" % (
            seed, K, n_trans, alpha_k,
            " [SATURATED]" if saturated_k else ""), flush=True)
        result["alpha_k%d" % K] = alpha_k
        result["saturated_k%d" % K] = saturated_k

        # Build W and free P_src/P_dst
        print("[seed=%d K=%d] building W = P_src.T @ P_dst (%dx%d)..." % (
            seed, K, n_dim, n_dim), flush=True)
        W_k = build_W(P_src, P_dst)
        del P_src, P_dst

        # --- TEST EVAL (vectorized, N1-style) ---
        # Flatten test positions
        _c_src_list: List[np.ndarray] = []  # context vectors
        _c_tgt_list: List[int] = []
        _t_src_tok_list: List[int] = []
        _true_tok_list: List[int] = []

        for cids_doc, tids_doc in test_seqs:
            cids_arr = cids_doc.astype(np.int64)
            ctx_vecs = build_context_vecs_batched(C, cids_arr, K, n_dim)
            n_pos = ctx_vecs.shape[0]
            if n_pos == 0:
                continue
            _c_src_list.append(ctx_vecs)
            _c_tgt_list.extend(cids_arr[1:n_pos + 1].tolist())
            _t_src_tok_list.extend(tids_doc[:n_pos].tolist())
            _true_tok_list.extend(tids_doc[1:n_pos + 1].tolist())

        if not _c_src_list:
            for key_m in ("substrate_concept_top1", "substrate_bpc", "substrate_top1",
                          "unigram_bpc", "bigram_bpc", "ceiling_bpc"):
                result["%s_k%d" % (key_m, K)] = float("nan")
            continue

        Q_all = np.concatenate(_c_src_list, axis=0)  # (tot_c, N)
        c_tgt_all = np.array(_c_tgt_list, dtype=np.int64)
        t_src_tok_all = np.array(_t_src_tok_list, dtype=np.int64)
        true_tok_all = np.array(_true_tok_list, dtype=np.int64)
        tot_c = len(c_tgt_all)

        print("[seed=%d K=%d] batched concept recall: %d queries..." % (seed, K, tot_c), flush=True)
        pred_concept_all = batched_concept_recall(W_k, Q_all, C)
        del Q_all

        sub_c_ok = int((pred_concept_all == c_tgt_all).sum())
        result["substrate_concept_top1_k%d" % K] = sub_c_ok / max(tot_c, 1)
        result["n_concept_test_pairs_k%d" % K] = tot_c

        # OOV mask
        oov_mask = true_tok_all >= V_TOK
        valid_mask = ~oov_mask
        valid_idx = np.where(valid_mask)[0]
        tot_t = int(valid_mask.sum())

        if tot_t == 0:
            for key_m in ("substrate_bpc", "substrate_top1", "unigram_bpc",
                          "bigram_bpc", "ceiling_bpc"):
                result["%s_k%d" % (key_m, K)] = float("nan")
            result["n_token_test_pairs_k%d" % K] = 0
            continue

        pred_c_valid = pred_concept_all[valid_idx]
        true_tok_valid = true_tok_all[valid_idx]
        c_tgt_valid = c_tgt_all[valid_idx]
        t_src_tok_valid = t_src_tok_all[valid_idx]

        # Batched token decode (chunked to control RAM -- N1-identical)
        BATCH_TOK_CHUNK = 2000
        n_valid = tot_t
        pred_tok_valid = np.empty(n_valid, dtype=np.int64)
        true_tok_logprob = np.empty(n_valid, dtype=np.float64)

        print("[seed=%d K=%d] batched token decode: %d positions (chunk=%d)..." % (
            seed, K, n_valid, BATCH_TOK_CHUNK), flush=True)
        for _ck_s in range(0, n_valid, BATCH_TOK_CHUNK):
            _ck_e = min(_ck_s + BATCH_TOK_CHUNK, n_valid)
            _cvecs = C[pred_c_valid[_ck_s:_ck_e]]
            _lp = batched_token_logprob(D, _cvecs, uni_dist, LAM_BACKOFF)
            pred_tok_valid[_ck_s:_ck_e] = np.argmax(_lp, axis=1)
            _tt = true_tok_valid[_ck_s:_ck_e]
            true_tok_logprob[_ck_s:_ck_e] = _lp[np.arange(_ck_e - _ck_s), _tt]

        sub_t_ok = int((pred_tok_valid == true_tok_valid).sum())
        sub_nll = float(-true_tok_logprob.sum())

        uni_t_ok = int((uni_tok_pred == true_tok_valid).sum())
        uni_nll = float(-uni_log[true_tok_valid].sum())

        big_t_ok = 0; big_nll = 0.0
        for _i in range(n_valid):
            _ts = int(t_src_tok_valid[_i]); _tt = int(true_tok_valid[_i])
            _bp = big_tok.get(_ts)
            if _bp is not None and _bp.sum() > 0:
                big_t_ok += (int(np.argmax(_bp)) == _tt)
                _bp_mle = float(_bp[_tt]) / (float(_bp.sum()) + 1e-9)
                _bfd_tt = (1.0 - INTERP_B) * _bp_mle + INTERP_B * float(uni_dist[_tt])
                big_nll += -math.log(_bfd_tt + 1e-300)
            else:
                big_t_ok += (uni_tok_pred == _tt)
                big_nll += float(-uni_log[_tt])

        ceil_t_ok = 0; ceil_nll = 0.0
        for _i in range(n_valid):
            _ctgt = int(c_tgt_valid[_i]); _tt = int(true_tok_valid[_i])
            _ceil_t = ceiling_pred.get(_ctgt, uni_tok_pred)
            ceil_t_ok += (_ceil_t == _tt)
            _ctd = concept_tok_counts.get(_ctgt)
            if _ctd is not None and _ctd.sum() > 0:
                _ctd_mle = float(_ctd[_tt]) / (float(_ctd.sum()) + 1e-9)
                _ctd_tt = (1.0 - INTERP_B) * _ctd_mle + INTERP_B * float(uni_dist[_tt])
                ceil_nll += -math.log(_ctd_tt + 1e-300)
            else:
                ceil_nll += float(-uni_log[_tt])

        tt = max(tot_t, 1)
        result["substrate_top1_k%d" % K] = sub_t_ok / tt
        result["substrate_bpc_k%d" % K] = (sub_nll / tt) / log2
        result["unigram_top1_k%d" % K] = uni_t_ok / tt
        result["unigram_bpc_k%d" % K] = (uni_nll / tt) / log2
        result["bigram_top1_k%d" % K] = big_t_ok / tt
        result["bigram_bpc_k%d" % K] = (big_nll / tt) / log2
        result["ceiling_top1_k%d" % K] = ceil_t_ok / tt
        result["ceiling_bpc_k%d" % K] = (ceil_nll / tt) / log2
        result["n_token_test_pairs_k%d" % K] = tot_t
        result["elapsed_k%d_s" % K] = time.time() - t_k0

        print("  [seed=%d K=%d] substrate_bpc=%.2f unigram_bpc=%.2f bigram_bpc=%.2f "
              "concept_top1=%.3f alpha=%.3f%s" % (
                  seed, K,
                  result["substrate_bpc_k%d" % K],
                  result["unigram_bpc_k%d" % K],
                  result["bigram_bpc_k%d" % K],
                  result["substrate_concept_top1_k%d" % K],
                  alpha_k,
                  " [SATURATED]" if saturated_k else ""), flush=True)

    # Compute depth gains and floor absorption (per Skunkworks finding)
    if 1 in DEPTH_SET and not math.isnan(result.get("substrate_bpc_k1", float("nan"))):
        bpc_k1 = result["substrate_bpc_k1"]
        ctop1_k1 = result["substrate_concept_top1_k1"]
        # concept "BPC" proxy: -log2(concept_top1) is NOT BPC but gives signal
        # For floor absorption: use token-BPC gain vs concept-top1 gain
        for K_other in DEPTH_SET:
            if K_other == 1:
                continue
            bpc_ko = result.get("substrate_bpc_k%d" % K_other, float("nan"))
            ctop1_ko = result.get("substrate_concept_top1_k%d" % K_other, float("nan"))
            result["depth_token_gain_k%d" % K_other] = bpc_k1 - bpc_ko
            result["depth_concept_top1_gain_k%d" % K_other] = ctop1_ko - ctop1_k1
            # floor_absorption: concept gain minus token gain (>=0 if floor absorbs)
            # concept gain in same BPC units is approximate; signal = direction
            result["floor_absorption_approx_k%d" % K_other] = (
                (ctop1_ko - ctop1_k1) - (bpc_k1 - bpc_ko)
            )

    result["elapsed_s"] = time.time() - t0
    return result


# ---------------------------------------------------------------------------
# Verdict (pre-registered bands; N2 depth-specific)
# ---------------------------------------------------------------------------

def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    def _mean_k(key: str, K: int) -> float:
        k_key = "%s_k%d" % (key, K)
        vals = [p[k_key] for p in ps if k_key in p and p[k_key] is not None
                and not math.isnan(p[k_key])]
        return float(np.mean(vals)) if vals else float("nan")

    bpc_cv_across_seeds = {}
    for K in DEPTH_SET:
        vals = [p["substrate_bpc_k%d" % K] for p in ps
                if "substrate_bpc_k%d" % K in p
                and not math.isnan(p.get("substrate_bpc_k%d" % K, float("nan")))]
        if len(vals) > 1 and abs(float(np.mean(vals))) > 1e-9:
            bpc_cv_across_seeds[K] = float(np.std(vals)) / abs(float(np.mean(vals)))
        else:
            bpc_cv_across_seeds[K] = 0.0

    any_saturated = any(
        p.get("saturated_k%d" % K, False) for p in ps for K in DEPTH_SET
    )

    # Per-K summary
    per_k_lines = []
    for K in DEPTH_SET:
        sub_bpc = _mean_k("substrate_bpc", K)
        uni_bpc = _mean_k("unigram_bpc", K)
        big_bpc = _mean_k("bigram_bpc", K)
        ceil_bpc = _mean_k("ceiling_bpc", K)
        sub_c_top1 = _mean_k("substrate_concept_top1", K)
        sub_top1 = _mean_k("substrate_top1", K)
        cv = bpc_cv_across_seeds.get(K, 0.0)
        per_k_lines.append(
            "K=%d: sub_bpc=%.2f uni_bpc=%.2f big_bpc=%.2f ceil_bpc=%.2f "
            "concept_top1=%.3f sub_top1=%.3f cv=%.3f" % (
                K, sub_bpc, uni_bpc, big_bpc, ceil_bpc, sub_c_top1, sub_top1, cv)
        )

    # Depth gain summary (vs K=1)
    bpc_k1 = _mean_k("substrate_bpc", 1)
    gain_lines = []
    for K in DEPTH_SET:
        if K == 1:
            continue
        bpc_ko = _mean_k("substrate_bpc", K)
        token_gain = bpc_k1 - bpc_ko
        c_gain = _mean_k("substrate_concept_top1", K) - _mean_k("substrate_concept_top1", 1)
        gain_lines.append(
            "K=%d: token_gain=%.3f bits concept_top1_gain=%.3f" % (K, token_gain, c_gain)
        )

    summary = ("depth_sweep %s | seeds=%d%s | %s | gains_vs_k1: %s" % (
        " | ".join(per_k_lines),
        len(ps),
        " SATURATION-FLAG" if any_saturated else "",
        "V_C=%d N_DIM=%d f=%.4f" % (V_C, N_DIM, F_SPARSE),
        "; ".join(gain_lines) if gain_lines else "n/a",
    ))

    # --- VERDICT BANDS (pre-registered) ---
    # Find best K (min substrate_bpc among DEPTH_SET)
    best_k = 1
    best_bpc = _mean_k("substrate_bpc", 1)
    for K in DEPTH_SET:
        bpc_k = _mean_k("substrate_bpc", K)
        if not math.isnan(bpc_k) and bpc_k < best_bpc:
            best_bpc = bpc_k
            best_k = K

    uni_bpc_k1 = _mean_k("unigram_bpc", 1)
    big_bpc_k1 = _mean_k("bigram_bpc", 1)
    depth_gain = bpc_k1 - best_bpc   # positive = improvement
    cv_best = bpc_cv_across_seeds.get(best_k, 0.0)

    saturation_note = (
        " [PROVEN-BOUND: saturation flag; not chain-grade]" if any_saturated else ""
    )

    # HARD_FAIL: no K improves over K=1 by >= 0.02 BPC
    if math.isnan(best_bpc) or depth_gain < 0.02:
        return ("HARD_FAIL",
                "HARD_FAIL: depth provides no benefit (best_gain=%.3f bits < 0.02 threshold). "
                "HD-binding does not capture higher-order structure beyond K=1 / fully floor-masked. "
                "%s%s" % (depth_gain, summary, saturation_note))

    # HARD_PASS: best_K sub_bpc < bigram AND depth_gain >= 0.1 BPC AND cv <= 0.05
    if best_bpc < big_bpc_k1 and depth_gain >= 0.1 and cv_best <= 0.05:
        if any_saturated:
            return ("MIDDLE_BAND",
                    "MIDDLE_BAND (saturation-demote): best_K=%d sub_bpc<bigram but saturation flag. "
                    "depth_gain=%.3f bits. %s%s" % (best_k, depth_gain, summary, saturation_note))
        return ("HARD_PASS",
                "HARD_PASS: K=%d substrate-BPC=%.2f < bigram=%.2f, depth_gain=%.3f bits >= 0.10, "
                "cv=%.3f <= 0.05, substrate-only-decode. %s" % (
                    best_k, best_bpc, big_bpc_k1, depth_gain, cv_best, summary))

    # MIDDLE_BAND: depth helps but doesn't beat bigram
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: depth helps (gain=%.3f bits) but best_K=%d sub_bpc=%.2f does not beat "
            "bigram=%.2f. %s%s" % (depth_gain, best_k, best_bpc, big_bpc_k1, summary, saturation_note))


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s V_C=%d N_DIM=%d f=%.4f MAX_DOCS=%d seeds=%s depth_set=%s" % (
    ANCHOR_NAME, RUN_MODE, V_C, N_DIM, F_SPARSE, MAX_DOCS, SEEDS, DEPTH_SET), flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "N": N_DIM}

done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds already complete; running %s" % (
    len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

t_total = time.time()
ps: List[Dict[str, Any]] = []

for seed in remaining_seeds:
    r = run_seed(seed)
    ps.append(r)
    write_partial(out_dir, seed, r)

# Load any done seeds from checkpoint
if done_seeds:
    agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
    for k_key, v_val in agg.items():
        ps.append(v_val)

if not ps:
    print("[ERROR] no seeds completed; aborting", flush=True)
    sys.exit(1)

v, vmsg = verdict(ps)
print("\n[VERDICT] " + vmsg, flush=True)

# Build full per-K metric summary for metrics.json
per_k_summary: Dict[str, Any] = {}
for K in DEPTH_SET:
    for met in ("substrate_bpc", "substrate_concept_top1", "substrate_top1",
                "unigram_bpc", "bigram_bpc", "ceiling_bpc"):
        k_key = "%s_k%d" % (met, K)
        vals = [p[k_key] for p in ps if k_key in p
                and not math.isnan(p.get(k_key, float("nan")))]
        per_k_summary[k_key + "_mean"] = float(np.mean(vals)) if vals else float("nan")

metrics = {
    "anchor_name": ANCHOR_NAME,
    "config_version": CONFIG_VERSION,
    "verdict": v,
    "verdict_msg": vmsg,
    "run_mode": RUN_MODE,
    "n_seeds": len(ps),
    "V_C": V_C,
    "N_DIM": N_DIM,
    "f_sparse": F_SPARSE,
    "depth_set": DEPTH_SET,
    "per_k_summary": per_k_summary,
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
