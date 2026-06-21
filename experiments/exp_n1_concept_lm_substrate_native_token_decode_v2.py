"""
n1_concept_lm_substrate_native_token_decode_v2 -- N1: substrate-native token-level LM, SUBSTRATE-OPTIMAL config.

CHANGES FROM v1 (substrate-optimal per Research density-scour 2026-06-21):
  - N_DIM: 1024 (dense, under-capacity) -> 4096 (Willshaw-sparse, configurable).
  - ENCODING: dense bipolar cf-RPE -> SPARSE Willshaw-style codes, f = round(f*N)/N active fraction.
    * Concept codebook C: shape (V_C, N_DIM), sparse binary {0,1}, k = round(f*N) active per row.
    * Transition memory W: stored as stacked sparse concept-pair patterns (P_src, P_dst);
      recall uses W-free single-step: argmax_c( C[c] . sign( (s @ P_src.T) @ P_dst ) )
      -- EXACTLY the proven readout from exp_sparse_boundary_v2_cpu_v1 (atom a3f473dd lineage).
    * Capacity at N=4096, f=0.006: ~80k+ patterns (vs ~565 dense at N=4096, ~140 at N=1024).
  - DECODE MEMORY D: still substrate-native (no LLM head at inference).
    * D shape (N_DIM, V_TOK). Column j = sum of C[concept] for all (concept_t, token_t=j) in train.
    * Decode: sparse-code concept vector v -> scores = D.T @ v -> argmax.
    * Because v is sparse (k-of-N active), the inner product selects only k columns of D.
  - V_C: configurable (env HDLAB_V_C or --v-c, default 256).
  - SATURATION GUARD: compute alpha = n_unique_pairs / N_DIM; if recall plateaus >=0.5 across
    all queries OR alpha > 1.0, mark the result PROVEN-BOUND (tiered), not chain-grade.
  - CODEBOOK UTILIZATION CHECK: warn if >50% of V_C clusters are unused (VQ collapse).
  NOTE: SimVQ/FSQ alignment-rescue + full V_C sweep {256,1024,4096} are N2's job.
        N1 uses a single default config but exposes the param so N2 can sweep without re-authoring.

SUBSTRATE-ONLY-NESS GATE (unchanged from v1):
  At INFERENCE, no transformer is called. Codebook built from Pythia-160m residuals at INGEST.
  BOUNDARY: Pythia-160m runs ONCE at ingest to produce residuals. NOT called at inference.
  token embeddings in D are from a static lookup built from train tokens, NOT the LM-head softmax.

PIPELINE:
  Load residuals_per_token.npz (residuals (sum_T,768), doc_boundaries, token_ids -- REQUIRED).
  VQ -> concept IDs per token (train-fit only, no test leakage).
  Build:
    (a) sparse codebook C: V_C sparse binary codes of shape (V_C, N_DIM), k active per row.
    (b) transition store: sparse pattern matrices P_src (M_trans x N_DIM), P_dst (M_trans x N_DIM)
        from train (concept_t, concept_{t+1}) pairs (one pair per adjacent train token).
    (c) decode memory D (N_DIM, V_TOK): Hebbian accumulation C[concept_t] onto column token_t.
  ANALYTIC CEILING: oracle concept prediction + best concept->token decode on TEST.
  TOKEN METRICS on TEST (substrate path: sparse-W recall->concept->D->token):
    - next-token top-1 accuracy
    - bits-per-character (BPC) = cross-entropy / log(2) in bits per token
  BASELINES: token-unigram, token-bigram-Markov, analytic ceiling.

PRE-REGISTERED BANDS (Skunkworks N3 corpus-eval cert-bands, 2026-06-21T16:06:58Z):
  HARD_PASS (chain-grade): substrate-native BPC < token-BIGRAM on held-out
    AND cv <= 0.05 across seeds
    AND substrate-only-decode verified (zero LLM calls at inference).
  MIDDLE_BAND: substrate BPC in (bigram_BPC, unigram_BPC] (captures some structure, not chain-grade).
  HARD_FAIL: substrate BPC >= unigram_BPC (no real structure)
    OR any LLM forward call in the inference path (substrate-only violated).

SATURATION GUARD (mandatory, pre-registered):
  alpha = n_unique_transition_pairs / N_DIM.
  If alpha > 1.0 OR recall plateaus >=0.5 across all queries:
    Demote to PROVEN-BOUND in verdict_msg (not chain-grade chain-pass).

TOKEN_IDS REQUIREMENT:
  token_ids key MUST be present in residuals_per_token.npz.
  If absent, raises FileNotFoundError (do NOT silently fall back to index-proxy tokens).

FORMULA SELF-TESTS (PROT-022): _instrumentation_selftest() at module scope tests:
  1. Sparse codebook construction: k active per row.
  2. Sparse transition store+recall on synthetic data (W-free single-step from sparse_boundary_v2).
  3. Decode memory D accumulation + argmax decode.
  4. BPC formula (cross-entropy / log(2)).
  5. doc_boundaries slice correctness.
  6. Instrumentation: all claimed metrics non-null after one synthetic forward pass.

ASCII-only. write_metrics. PROT-021 run_config guard. PROT-018: no _nN suffix (N is configurable
  via env/CLI; production N_DIM default is 4096, stated in CONFIG_VERSION). CPU numpy + sklearn
  only; no torch/GPU.

QUEUE: remote_cpu_queue (residuals_per_token.npz is on marsh@home; NOT on local laptop).
  DEPENDENCY: token_ids recovery cell must land on remote runner BEFORE this cell runs.

CONFIG_VERSION = "V_C=256,N_DIM=4096,f=0.006,DECODE=freq,MAX_DOCS=100000,SEEDS=7-17-23,SPLIT=0.8"
  Changes to any of these params invalidate checkpoints.
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

ANCHOR_NAME = "n1_concept_lm_substrate_native_token_decode_v2"

# ---------------------------------------------------------------------------
# Configurable params (env vars / CLI, with substrate-optimal defaults)
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--n-dim", dest="n_dim", type=int, default=None)
_ap.add_argument("--v-c", dest="v_c", type=int, default=None)
_ap.add_argument("--f-sparse", dest="f_sparse", type=float, default=None)
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# N_DIM: substrate-optimal 4096 (was 1024 in v1; 16x storage, ~80k capacity vs ~140).
N_DIM = _ARGS.n_dim if _ARGS.n_dim is not None else int(os.environ.get("HDLAB_N_DIM", "4096"))
# f_sparse: Willshaw sweet-spot log(N)/N ~ 0.006 at N=4096 (k=round(0.006*4096)=25 active).
F_SPARSE = _ARGS.f_sparse if _ARGS.f_sparse is not None else float(os.environ.get("HDLAB_F_SPARSE", "0.006"))
# V_C: exposed for N2 sweep; N1 default 256.
V_C_DEFAULT = _ARGS.v_c if _ARGS.v_c is not None else int(os.environ.get("HDLAB_V_C", "256"))

if RUN_MODE == "smoke":
    SEEDS = [1]
    V_C = 32           # small concept vocab for smoke
    MAX_DOCS = 100     # small doc count for fast smoke
    MAX_TOK_VOCAB = 1000
    # Smoke uses smaller N_DIM so self-test completes fast; note: still exercises code path
    _SMOKE_N_DIM = min(N_DIM, 512)
else:
    SEEDS = [7, 17, 23]
    V_C = V_C_DEFAULT
    MAX_DOCS = 100000
    MAX_TOK_VOCAB = 50257  # Pythia uses GPT-2 tokenizer (~50k vocab)
    _SMOKE_N_DIM = N_DIM

TRAIN_FRAC = 0.8
LR_DECODE = 1.0  # decode memory: count-based; weight per observation

CONFIG_VERSION = "V_C=%d,N_DIM=%d,f=%.4f,DECODE=freq,MAX_DOCS=%d,SEEDS=%s,SPLIT=%.1f" % (
    V_C_DEFAULT, N_DIM, F_SPARSE, 100000 if RUN_MODE != "smoke" else 100,
    "-".join(str(s) for s in ([7, 17, 23] if RUN_MODE != "smoke" else [1])),
    TRAIN_FRAC,
)

NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"


# ---------------------------------------------------------------------------
# Sparse Willshaw-style substrate ops
# (sparse_pat + recall idiom REUSED from exp_sparse_boundary_v2_cpu_v1, atom a3f473dd lineage)
# ---------------------------------------------------------------------------

def sparse_codebook(vc: int, n: int, f: float, rng: np.random.Generator) -> np.ndarray:
    """Build sparse binary codebook, shape (vc, n), k = round(f*n) active units per row.

    Each row has exactly k positions set to 1, rest 0. Willshaw-style: no normalization needed;
    the sparse inner-product IS the similarity (overlap count). k active out of n: typical overlap
    between two random codes = k^2/n << k (near-orthogonal at f << 1).
    """
    k = max(1, round(f * n))
    C = np.zeros((vc, n), dtype=np.float32)
    for i in range(vc):
        idx = rng.choice(n, k, replace=False)
        C[i, idx] = 1.0
    return C  # shape (vc, n)


def k_active(code: np.ndarray) -> int:
    """Return number of active (nonzero) units in a code vector."""
    return int((code != 0).sum())


def sparse_store(C_src: np.ndarray, C_dst: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Store concept transition pairs as raw pattern matrices.

    Returns:
        P_src: (M_trans, N) -- source concept codes (one row per transition)
        P_dst: (M_trans, N) -- destination concept codes
    W-free single-step recall (from exp_sparse_boundary_v2_cpu_v1):
        recalled_dst = sign( (query_src @ P_src.T) @ P_dst )
    Proven readout: 8x@f=0.10 / 20x@f=0.02 / >=300x@f=0.005 super-capacity (a3f473dd).
    """
    # C_src, C_dst: (M_trans, N) already in caller -- just return them
    return C_src, C_dst


def sparse_recall_next(P_src: np.ndarray, P_dst: np.ndarray,
                       query: np.ndarray, C: np.ndarray) -> int:
    """W-free single-step Willshaw recall: predict next concept from current.

    Args:
        P_src: (M, N) stored source patterns
        P_dst: (M, N) stored destination patterns
        query: (N,) current concept code (sparse)
        C: (V_C, N) codebook for cleanup argmax

    Returns:
        predicted_concept_id (int)
    """
    if P_src.shape[0] == 0:
        return 0
    # W-free single-step: sign( (q @ P_src.T) @ P_dst ) -- proven from sparse_boundary_v2
    # (q @ P_src.T) gives overlap of query with each stored source; weight P_dst rows by overlap
    # -> reconstructed dst activation; argmax over C = nearest concept
    overlaps = query @ P_src.T          # (M,) -- dot-product similarities
    activated = overlaps @ P_dst        # (N,) -- weighted sum of dst patterns
    # Cleanup: argmax similarity of activated signal with each codebook row
    # (equivalent to argmax C @ sign(activated), but inner-product with C is more numerically stable)
    sims = C @ activated                # (V_C,) -- each row dot activated
    return int(np.argmax(sims))


def build_W(P_src: np.ndarray, P_dst: np.ndarray) -> np.ndarray:
    """Precompute collapsed weight matrix W = P_src.T @ P_dst, shape (N, N).

    Identity: for any query q (N,),
        (q @ P_src.T) @ P_dst == q @ (P_src.T @ P_dst) == q @ W
    Proof: sum_i (q . P_src[i]) * P_dst[i] = P_src.T @ (overlaps) applied to rows of P_dst
         = (P_src.T @ P_dst) @ q  [outer-product identity].
    Cost: one (N, M) @ (M, N) matmul -> (N, N) done ONCE per seed instead of once per query.
    At N=4096, M~40000: W is 4096x4096 float32 = 67 MB.
    Returns zeros matrix if P_src is empty (no transitions stored).
    """
    if P_src.shape[0] == 0:
        return np.zeros((P_src.shape[1], P_src.shape[1]), dtype=np.float32)
    return P_src.T @ P_dst  # (N, N)


def batched_concept_recall(W: np.ndarray, Q: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Vectorized Willshaw concept recall for a batch of query vectors.

    Equivalent to calling sparse_recall_next(P_src, P_dst, Q[i], C) for each i,
    but using the precomputed W = P_src.T @ P_dst (shape N x N).

    Args:
        W: (N, N) precomputed weight matrix from build_W()
        Q: (n_pos, N) batch of source concept codes
        C: (V_C, N) codebook for cleanup argmax

    Returns:
        pred_concept_ids: (n_pos,) int64 array of predicted next concept ids
    """
    # activated_batch[i] = Q[i] @ W  -- the per-row W-free recall, batched
    activated_batch = Q @ W              # (n_pos, N)
    # sims_batch[i, c] = C[c] . activated_batch[i] -- nearest codebook entry
    sims_batch = activated_batch @ C.T   # (n_pos, V_C)
    return np.argmax(sims_batch, axis=1).astype(np.int64)


def batched_token_logprob(D: np.ndarray, concept_vecs: np.ndarray) -> np.ndarray:
    """Batched log-probability over tokens for multiple concept vectors.

    Args:
        D: (N, V_TOK) decode memory
        concept_vecs: (n_pos, N) concept code vectors

    Returns:
        log_probs_batch: (n_pos, V_TOK) log-probabilities (base-e), same math as token_logprob()
    """
    scores = concept_vecs @ D           # (n_pos, V_TOK)
    scores -= scores.max(axis=1, keepdims=True)   # numerically stable softmax
    exp_s = np.exp(scores)
    log_probs = scores - np.log(exp_s.sum(axis=1, keepdims=True) + 1e-300)
    return log_probs


def decode_token(D: np.ndarray, concept_vec: np.ndarray) -> int:
    """Predict token: argmax over D.T @ concept_vec, shape (V_TOK,).

    D shape (N_DIM, V_TOK). Column j = accumulated C[concept] vectors for token j.
    For sparse concept_vec (k active), D.T @ concept_vec selects k columns of D and sums them.
    Substrate-native: no LLM head, no transformer inference.
    """
    scores = D.T @ concept_vec  # shape (V_TOK,)
    return int(np.argmax(scores))


def token_logprob(D: np.ndarray, concept_vec: np.ndarray) -> np.ndarray:
    """Return log-probability distribution over tokens given concept vector.

    Uses softmax over D.T @ concept_vec for BPC computation.
    Returns log-probabilities (log-base-e), shape (V_TOK,).
    """
    scores = D.T @ concept_vec  # (V_TOK,)
    scores = scores - scores.max()
    exp_s = np.exp(scores)
    log_probs = scores - np.log(exp_s.sum() + 1e-300)
    return log_probs


# ---------------------------------------------------------------------------
# Formula self-test (PROT-022 + instrumentation gate)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small synthetic scale."""
    rng = np.random.default_rng(42)
    n, f_test, vc, vt = 256, 0.05, 8, 20  # tiny synthetic scale
    k = max(1, round(f_test * n))

    # --- test 1: sparse codebook: k active per row ---
    C = sparse_codebook(vc, n, f_test, rng)
    assert C.shape == (vc, n), "codebook shape FAIL"
    for i in range(vc):
        assert k_active(C[i]) == k, (
            "codebook row %d: expected %d active, got %d" % (i, k, k_active(C[i]))
        )
    # Near-orthogonal check: avg pairwise overlap should be << k
    overlaps = C @ C.T  # (vc, vc)
    np.fill_diagonal(overlaps, 0.0)
    mean_cross_overlap = float(overlaps.sum()) / (vc * (vc - 1))
    assert mean_cross_overlap < k * 0.5, (
        "codebook rows NOT near-orthogonal: mean_cross_overlap=%.2f vs k=%d" % (mean_cross_overlap, k)
    )

    # --- test 2: sparse transition store+recall (W-free, proven idiom) ---
    # Build 5 synthetic transitions: store C[i] -> C[(i+1)%vc] for i in 0..4
    M_trans = 5
    P_src_list, P_dst_list = [], []
    for i in range(M_trans):
        P_src_list.append(C[i])
        P_dst_list.append(C[(i + 1) % vc])
    P_src = np.array(P_src_list, dtype=np.float32)  # (M_trans, n)
    P_dst = np.array(P_dst_list, dtype=np.float32)

    # Recall concept 0 -> should predict concept 1
    pred_c = sparse_recall_next(P_src, P_dst, C[0], C)
    assert pred_c == 1, "sparse W-free recall FAIL: expected concept 1, got %d" % pred_c

    # --- test 3: decode memory D accumulation + argmax decode ---
    # Build D with concept 3 strongly associated to token 7 (dominant: 5 obs),
    # concept 5 associated to token 2 (2 obs), so argmax for C[3] -> 7.
    D = np.zeros((n, vt), dtype=np.float32)
    for _ in range(5):
        D[:, 7] += C[3] * LR_DECODE
    D[:, 2] += C[3] * LR_DECODE
    for _ in range(2):
        D[:, 2] += C[5] * LR_DECODE
    t_pred = decode_token(D, C[3])
    assert t_pred == 7, "decode memory argmax FAIL: expected tok 7, got %d" % t_pred

    # --- test 4: BPC formula ---
    # Use a MORE UNIFORM D_test to ensure BPC is in a testable range.
    # 5 concepts each vote once for a different token -> log_probs spread ~uniformly.
    D_test = np.zeros((n, vt), dtype=np.float32)
    for i in range(5):
        D_test[:, i] += C[i] * LR_DECODE
    log_probs = token_logprob(D_test, C[2])
    assert log_probs.shape == (vt,), "log_probs shape FAIL"
    assert not np.isnan(log_probs).any(), "log_probs has NaN"
    # For C[2] queried against D_test: column 2 has C[2] weight, others have C[i!=2].
    # Because sparse codes are near-orthogonal, concept 2's column wins.
    # Check the log-prob for token 2 (predicted argmax) -- BPC should be finite and >= 0.
    # The true_token for BPC is NOT the argmax in practice; test that BPC is finite.
    bpc_argmax = -log_probs[2] / math.log(2)  # argmax token -> BPC near 0 (high confidence)
    # Token 4 (not related to C[2]) should have significantly higher BPC
    bpc_other = -log_probs[4] / math.log(2)
    assert bpc_argmax >= 0.0, "BPC for argmax token must be >= 0: %.3f" % bpc_argmax
    assert bpc_argmax < 60.0, "BPC for argmax token unreasonably large: %.3f" % bpc_argmax
    assert bpc_other > bpc_argmax, "BPC should be lower for predicted token than for random token"
    # Also check log_probs are proper log-probs (max ~= 0, all finite)
    assert log_probs.max() <= 1e-6, "log_probs max > 0 (not valid log-probs): %.6f" % log_probs.max()
    assert not np.isinf(log_probs).any(), "log_probs has Inf"

    # --- test 5: doc_boundaries slice ---
    bnd = np.array([0, 3, 7, 12], dtype=np.int64)
    fake_toks = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], dtype=np.int64)
    segs = [fake_toks[bnd[i]:bnd[i + 1]] for i in range(len(bnd) - 1)]
    assert len(segs) == 3, "doc_boundaries n_docs FAIL"
    assert len(segs[0]) == 3, "doc_boundaries len0 FAIL"

    # --- test 6: instrumentation - all metrics computable on synthetic data ---
    result = _run_seed_synthetic(rng_seed=42, n_dim=n, f=f_test, vc=vc, vt=vt)
    assert result is not None, "synthetic run returned None"
    for key in ("substrate_top1", "substrate_bpc", "unigram_top1", "unigram_bpc",
                "bigram_top1", "bigram_bpc", "ceiling_top1", "ceiling_bpc"):
        val = result.get(key)
        assert val is not None, "metric %s is None" % key
        assert not math.isnan(val), "metric %s is NaN" % key
    assert result["substrate_bpc"] > 0.0, "substrate_bpc is zero (sentinel)"
    assert result["unigram_bpc"] > 0.0, "unigram_bpc is zero (sentinel)"

    # --- test 7: batched recall == per-query recall (CORRECTNESS GATE) ---
    # Reuse P_src/P_dst and C from test 2 above.
    # Query all concepts and compare batched path vs per-query path.
    W_test = build_W(P_src, P_dst)
    assert W_test.shape == (n, n), "build_W shape FAIL: %s" % str(W_test.shape)

    # Per-query results (old path)
    perq_concepts = np.array([sparse_recall_next(P_src, P_dst, C[i], C)
                               for i in range(vc)], dtype=np.int64)
    # Batched results (new path)
    Q_all = C.copy()  # (vc, n) -- query all codebook rows
    batch_concepts = batched_concept_recall(W_test, Q_all, C)
    assert perq_concepts.shape == batch_concepts.shape, "shape mismatch"
    mismatches = int((perq_concepts != batch_concepts).sum())
    assert mismatches == 0, (
        "batched_concept_recall != per-query: %d/%d mismatches. "
        "per-query=%s batched=%s" % (mismatches, vc, perq_concepts, batch_concepts)
    )

    # Token log-prob: per-query vs batched for a few concept vectors
    D_check = D_test  # (n, vt) from test 4 above
    for i in range(min(vc, 5)):
        lp_perq = token_logprob(D_check, C[i])              # (vt,) per-query
        lp_batch = batched_token_logprob(D_check, C[i:i+1]) # (1, vt) batched
        max_diff = float(np.abs(lp_perq - lp_batch[0]).max())
        assert max_diff < 1e-5, (
            "batched_token_logprob row %d max_diff=%.2e > 1e-5" % (i, max_diff)
        )

    # substrate_concept_top1, substrate_top1, substrate_bpc must match between
    # per-query (result from test 6 via _run_seed_synthetic) and batched path.
    # _run_seed_synthetic uses per-query path; compare to batched via a direct check
    # on the first test transition (concept 0 -> concept 1 was stored, check batched predicts 1).
    batch_single = batched_concept_recall(W_test, C[0:1], C)
    assert int(batch_single[0]) == 1, (
        "batched single-row check FAIL: expected 1, got %d" % int(batch_single[0])
    )

    print("[selftest] PASS: sparse-codebook k-of-N, W-free recall, decode-D-argmax, "
          "BPC formula, boundaries, instrumentation, batched==per-query", flush=True)


def _run_seed_synthetic(rng_seed: int, n_dim: int = 128, f: float = 0.05,
                         vc: int = 8, vt: int = 20) -> Dict[str, Any]:
    """Run one synthetic forward pass for selftest instrumentation gate."""
    rng = np.random.default_rng(rng_seed)
    n_docs = 20
    docs_cids = [rng.integers(0, vc, size=12) for _ in range(n_docs)]
    docs_tids = [rng.integers(0, vt, size=12) for _ in range(n_docs)]

    split = int(0.8 * n_docs)
    train_cids, test_cids = docs_cids[:split], docs_cids[split:]
    train_tids, test_tids = docs_tids[:split], docs_tids[split:]

    rng2 = np.random.default_rng(rng_seed + 1)
    C = sparse_codebook(vc, n_dim, f, rng2)

    # Build transition store
    P_src_list, P_dst_list = [], []
    for cids in train_cids:
        for t in range(len(cids) - 1):
            P_src_list.append(C[int(cids[t])])
            P_dst_list.append(C[int(cids[t + 1])])
    P_src = np.array(P_src_list, dtype=np.float32) if P_src_list else np.zeros((0, n_dim), dtype=np.float32)
    P_dst = np.array(P_dst_list, dtype=np.float32) if P_dst_list else np.zeros((0, n_dim), dtype=np.float32)

    D = np.zeros((n_dim, vt), dtype=np.float32)
    for cids, tids in zip(train_cids, train_tids):
        for t in range(len(cids)):
            tok = int(tids[t])
            if tok < vt:
                D[:, tok] += C[int(cids[t])] * LR_DECODE

    # Token baselines from train
    uni_tok = np.zeros(vt, dtype=np.int64)
    big_tok: Dict[int, np.ndarray] = {}
    for cids, tids in zip(train_cids, train_tids):
        for t in range(len(tids) - 1):
            tt1 = int(tids[t + 1])
            if tt1 < vt:
                uni_tok[tt1] += 1
            t0 = int(tids[t])
            if t0 not in big_tok:
                big_tok[t0] = np.zeros(vt, dtype=np.int64)
            if tt1 < vt:
                big_tok[t0][tt1] += 1
    uni_pred = int(np.argmax(uni_tok)) if uni_tok.sum() > 0 else 0
    uni_dist = uni_tok.astype(np.float32) + 1e-6
    uni_dist /= uni_dist.sum()
    uni_log = np.log(uni_dist + 1e-300)

    # Ceiling: per-concept most-frequent token in train
    concept_tok_counts: Dict[int, np.ndarray] = {}
    for cids, tids in zip(train_cids, train_tids):
        for t in range(len(cids)):
            c = int(cids[t]); tok = int(tids[t])
            if tok < vt:
                if c not in concept_tok_counts:
                    concept_tok_counts[c] = np.zeros(vt, dtype=np.int64)
                concept_tok_counts[c][tok] += 1
    ceiling_pred = {c: int(np.argmax(v)) for c, v in concept_tok_counts.items()}

    # TEST eval
    tot = 0
    sub_ok = big_ok = uni_ok = ceil_ok = 0
    sub_nll = big_nll = uni_nll = ceil_nll = 0.0

    for cids, tids in zip(test_cids, test_tids):
        for t in range(len(cids) - 1):
            true_tok = int(tids[t + 1])
            true_cid = int(cids[t + 1])
            tot += 1

            pred_cid = sparse_recall_next(P_src, P_dst, C[int(cids[t])], C)
            pred_tok = decode_token(D, C[pred_cid])
            log_probs = token_logprob(D, C[pred_cid])

            sub_ok += (pred_tok == true_tok)
            sub_nll += -log_probs[true_tok]

            uni_ok += (uni_pred == true_tok)
            uni_nll += -uni_log[true_tok]

            bp_tok_arr = big_tok.get(int(tids[t]))
            if bp_tok_arr is not None and bp_tok_arr.sum() > 0:
                bfd = bp_tok_arr.astype(np.float32) / (bp_tok_arr.sum() + 1e-6)
                big_ok += (int(np.argmax(bp_tok_arr)) == true_tok)
                big_nll += -math.log(float(bfd[true_tok]) + 1e-300)
            else:
                big_ok += (uni_pred == true_tok)
                big_nll += -uni_log[true_tok]

            ceil_pred_tok = ceiling_pred.get(true_cid, uni_pred)
            ceil_ok += (ceil_pred_tok == true_tok)
            ctd = concept_tok_counts.get(true_cid)
            if ctd is not None and ctd.sum() > 0:
                ctd_d = ctd.astype(np.float32) / (ctd.sum() + 1e-6)
                ceil_nll += -math.log(float(ctd_d[true_tok]) + 1e-300)
            else:
                ceil_nll += -uni_log[true_tok]

    if tot == 0:
        return {k: float("nan") for k in ("substrate_top1", "substrate_bpc",
                "unigram_top1", "unigram_bpc", "bigram_top1", "bigram_bpc",
                "ceiling_top1", "ceiling_bpc")}

    log2 = math.log(2)
    return {
        "substrate_top1": sub_ok / tot,
        "substrate_bpc": (sub_nll / tot) / log2,
        "unigram_top1": uni_ok / tot,
        "unigram_bpc": (uni_nll / tot) / log2,
        "bigram_top1": big_ok / tot,
        "bigram_bpc": (big_nll / tot) / log2,
        "ceiling_top1": ceil_ok / tot,
        "ceiling_bpc": (ceil_nll / tot) / log2,
        "n_test_pairs": tot,
    }


_instrumentation_selftest()  # Called at module scope before sweep
if _ARGS.self_test:
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load residuals, doc_boundaries, token_ids from npz.

    Returns:
        residuals: shape (sum_T, 768) float32
        doc_boundaries: shape (n_docs+1,) int64
        token_ids: shape (sum_T,) int64 -- REQUIRED; raises if absent

    NOTE: token_ids MUST be present (v2 requirement). Silent fallback to index-proxy
    is NOT allowed -- it produces meaningless token metrics.
    """
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
            "  Do NOT silently fall back to index-proxy tokens -- that produces meaningless metrics."
        )
    tids = z["token_ids"].astype(np.int64)
    print("[data] token_ids shape=%s" % (tids.shape,), flush=True)
    return res, bnd, tids


def build_docs(res: np.ndarray, bnd: np.ndarray, tids: np.ndarray,
               max_docs: int) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Slice into per-doc (residuals, token_ids) pairs, min 2 tokens."""
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
# Per-seed run
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    """Full per-seed pipeline: load, VQ, build sparse substrate, evaluate."""
    t0 = time.time()
    n_dim = N_DIM  # full-run production N_DIM (from configurable param)
    f = F_SPARSE   # Willshaw active fraction

    res, bnd, tids = load_data()
    docs = build_docs(res, bnd, tids, MAX_DOCS)
    print("[seed=%d] loaded %d docs" % (seed, len(docs)), flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(docs)).tolist()
    docs = [docs[i] for i in perm]
    split = int(TRAIN_FRAC * len(docs))
    train_docs = docs[:split]
    test_docs = docs[split:]

    # --- VQ: MiniBatchKMeans on train residuals ---
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
            for s in range(0, len(all_rn), chunk):
                e = s + chunk
                diff = all_rn[s:e, None, :] - centers[None, :, :]
                out[s:e] = np.argmin((diff ** 2).sum(-1), axis=1)
            return out

    # Assign concept IDs per split (NO TEST tokens in km fit = no leakage)
    train_cids_flat = assign_cids([d[0] for d in train_docs])
    test_cids_flat = assign_cids([d[0] for d in test_docs])

    # Codebook utilization check (SATURATION GUARD)
    unique_cids_train = np.unique(train_cids_flat)
    utilization = len(unique_cids_train) / V_C
    if utilization < 0.5:
        print("[seed=%d] WARNING: VQ COLLAPSE? only %.0f%% of V_C=%d clusters used. "
              "SimVQ/FSQ alignment-rescue needed (N2 job). BPC floor may be VQ-limited."
              % (seed, utilization * 100, V_C), flush=True)
    print("[seed=%d] codebook utilization=%.1f%% (%d/%d clusters active)" % (
        seed, utilization * 100, len(unique_cids_train), V_C), flush=True)

    # Slice back to per-doc sequences
    def slice_docs(docs_split, cids_flat):
        seqs = []; offset = 0
        for doc_res, doc_tok in docs_split:
            n = len(doc_res)
            seqs.append((cids_flat[offset:offset + n], doc_tok))
            offset += n
        return seqs

    train_seqs = slice_docs(train_docs, train_cids_flat)
    test_seqs = slice_docs(test_docs, test_cids_flat)

    # --- Sparse concept codebook (NOT km centroids -- substrate-native random sparse codes) ---
    rng2 = np.random.default_rng(seed + 1000)
    C = sparse_codebook(V_C, n_dim, f, rng2)
    k_val = max(1, round(f * n_dim))
    print("[seed=%d] sparse codebook: N_DIM=%d f=%.4f k=%d (active per code)" % (
        seed, n_dim, f, k_val), flush=True)

    # --- Build transition store (W-free Willshaw) ---
    # Collect all (src_code, dst_code) train transition pairs
    P_src_list, P_dst_list = [], []
    for cids, _ in train_seqs:
        for t in range(len(cids) - 1):
            P_src_list.append(C[int(cids[t])])
            P_dst_list.append(C[int(cids[t + 1])])
    n_trans = len(P_src_list)
    P_src = np.array(P_src_list, dtype=np.float32) if n_trans > 0 else np.zeros((0, n_dim), dtype=np.float32)
    P_dst = np.array(P_dst_list, dtype=np.float32) if n_trans > 0 else np.zeros((0, n_dim), dtype=np.float32)
    print("[seed=%d] transition store: %d pairs (alpha=n_trans/N_DIM=%.3f)" % (
        seed, n_trans, n_trans / max(n_dim, 1)), flush=True)

    # VECTORIZATION: build W = P_src.T @ P_dst ONCE (N x N, ~67 MB at N=4096).
    # Then free P_src/P_dst to reclaim ~655 MB each before the batched eval matmuls.
    # Identity: (q @ P_src.T) @ P_dst == q @ W for any query q.
    print("[seed=%d] building W = P_src.T @ P_dst (%dx%d)..." % (
        seed, n_dim, n_dim), flush=True)
    W = build_W(P_src, P_dst)  # (N, N)
    del P_src, P_dst            # free ~655 MB each; W is ~67 MB at N=4096

    # SATURATION GUARD: alpha = unique transition pairs / N_DIM
    n_unique_pairs = len(set(zip(train_cids_flat[:-1].tolist(), train_cids_flat[1:].tolist())))
    alpha = n_unique_pairs / n_dim
    saturated = (alpha > 1.0)
    print("[seed=%d] saturation: alpha=%.3f (n_unique_pairs=%d / N_DIM=%d) -> %s" % (
        seed, alpha, n_unique_pairs, n_dim,
        "SATURATED (>1.0; demote to PROVEN-BOUND)" if saturated else "OK"), flush=True)

    # --- Build decode memory D (concept -> token) ---
    all_train_tids = np.concatenate([tids_d for _, tids_d in train_seqs])
    actual_max_tok = min(int(all_train_tids.max()) + 1, MAX_TOK_VOCAB)
    V_TOK = actual_max_tok
    print("[seed=%d] V_TOK=%d (from train data)" % (seed, V_TOK), flush=True)

    D = np.zeros((n_dim, V_TOK), dtype=np.float32)
    for cids, tids_doc in train_seqs:
        for t in range(len(cids)):
            tok = int(tids_doc[t])
            if tok < V_TOK:
                D[:, tok] += C[int(cids[t])] * LR_DECODE

    # --- Compute token-level baselines from train ---
    uni_tok = np.zeros(V_TOK, dtype=np.int64)
    big_tok: Dict[int, np.ndarray] = {}
    for cids, tids_doc in train_seqs:
        for t in range(len(tids_doc) - 1):
            tt1 = int(tids_doc[t + 1])
            if tt1 < V_TOK:
                uni_tok[tt1] += 1
            t0_tok = int(tids_doc[t])
            if t0_tok not in big_tok:
                big_tok[t0_tok] = np.zeros(V_TOK, dtype=np.int64)
            if tt1 < V_TOK:
                big_tok[t0_tok][tt1] += 1
    uni_tok_pred = int(np.argmax(uni_tok)) if uni_tok.sum() > 0 else 0
    uni_dist = (uni_tok.astype(np.float32) + 1e-6)
    uni_dist /= uni_dist.sum()
    uni_log = np.log(uni_dist + 1e-300)

    # --- Concept-level baselines (sanity) ---
    uni_c = np.zeros(V_C, dtype=np.int64)
    big_c: Dict[int, np.ndarray] = {}
    for cids, _ in train_seqs:
        for t in range(len(cids) - 1):
            uni_c[int(cids[t + 1])] += 1
            c = int(cids[t])
            if c not in big_c:
                big_c[c] = np.zeros(V_C, dtype=np.int64)
            big_c[c][int(cids[t + 1])] += 1
    uni_c_pred = int(np.argmax(uni_c)) if uni_c.sum() > 0 else 0
    big_c_pred = {k: int(np.argmax(v)) for k, v in big_c.items()}

    # --- Analytic ceiling: per-concept most-frequent token (train stats) ---
    concept_tok_counts: Dict[int, np.ndarray] = {}
    for cids, tids_doc in train_seqs:
        for t in range(len(cids)):
            c = int(cids[t]); tok = int(tids_doc[t])
            if tok < V_TOK:
                if c not in concept_tok_counts:
                    concept_tok_counts[c] = np.zeros(V_TOK, dtype=np.int64)
                concept_tok_counts[c][tok] += 1
    ceiling_pred = {c: int(np.argmax(v)) for c, v in concept_tok_counts.items()}

    # --- Evaluate on TEST (VECTORIZED PATH) ---
    # Step 1: flatten all test (c_src, c_tgt, t_src_tok, true_tok) across docs into arrays.
    # doc_end_idx[i] = cumulative n_pos after doc i, used for plateau sampling.
    _c_src_list: List[int] = []
    _c_tgt_list: List[int] = []
    _t_src_tok_list: List[int] = []
    _true_tok_list: List[int] = []
    _doc_end_idx: List[int] = []   # cumulative concept-pair count after each doc

    _running_tot_c = 0
    for (cids, tids_doc) in test_seqs:
        n_pos = len(cids) - 1
        if n_pos < 1:
            _doc_end_idx.append(_running_tot_c)
            continue
        for t in range(n_pos):
            _c_src_list.append(int(cids[t]))
            _c_tgt_list.append(int(cids[t + 1]))
            _t_src_tok_list.append(int(tids_doc[t]))
            _true_tok_list.append(int(tids_doc[t + 1]))
        _running_tot_c += n_pos
        _doc_end_idx.append(_running_tot_c)

    log2 = math.log(2)

    if _running_tot_c == 0:
        # No test positions at all -- return zero counts (handled below by max(tot,1))
        tot_c = 0; sub_c_ok = 0; uni_c_ok = 0; big_c_ok = 0
        tot_t = 0
        sub_t_ok = uni_t_ok = big_t_ok = ceil_t_ok = 0
        sub_nll = uni_nll = big_nll = ceil_nll = 0.0
        plateau_saturated = False
    else:
        c_src_all = np.array(_c_src_list, dtype=np.int64)   # (tot_c,)
        c_tgt_all = np.array(_c_tgt_list, dtype=np.int64)
        t_src_tok_all = np.array(_t_src_tok_list, dtype=np.int64)
        true_tok_all = np.array(_true_tok_list, dtype=np.int64)

        # Step 2: BATCH concept recall -- one (tot_c, N) @ (N, N) matmul instead of tot_c x (M, N) pairs
        print("[seed=%d] batched concept recall: %d queries..." % (seed, len(c_src_all)), flush=True)
        Q_batch = C[c_src_all]                              # (tot_c, N) -- source concept codes
        pred_concept_all = batched_concept_recall(W, Q_batch, C)  # (tot_c,) int64
        del Q_batch                                         # free (tot_c, N) intermediate

        # Concept-level accuracy bookkeeping (cheap; no matmul)
        tot_c = int(len(c_src_all))
        sub_c_ok = int((pred_concept_all == c_tgt_all).sum())
        uni_c_ok = int((uni_c_pred == c_tgt_all).sum())
        big_c_pred_arr = np.array([big_c_pred.get(int(cs), uni_c_pred) for cs in c_src_all],
                                  dtype=np.int64)
        big_c_ok = int((big_c_pred_arr == c_tgt_all).sum())

        # Step 3: OOV mask -- skip positions where true_tok >= V_TOK
        oov_mask = true_tok_all >= V_TOK                    # (tot_c,) bool; True = skip
        valid_mask = ~oov_mask                              # (tot_c,) bool; True = keep
        valid_idx = np.where(valid_mask)[0]                 # indices into tot_c arrays

        tot_t = int(valid_mask.sum())
        if tot_t == 0:
            sub_t_ok = uni_t_ok = big_t_ok = ceil_t_ok = 0
            sub_nll = uni_nll = big_nll = ceil_nll = 0.0
        else:
            pred_c_valid = pred_concept_all[valid_idx]      # (tot_t,)
            true_tok_valid = true_tok_all[valid_idx]        # (tot_t,)
            c_tgt_valid = c_tgt_all[valid_idx]              # (tot_t,)
            t_src_tok_valid = t_src_tok_all[valid_idx]      # (tot_t,)

            # Step 4: BATCH token decode -- (tot_t, N) @ (N, V_TOK) -> (tot_t, V_TOK)
            # Memory note: tot_t ~10k, V_TOK ~50k -> 10k*50k*4 bytes = ~2 GB peak.
            # To control RAM, process in chunks of BATCH_TOK_CHUNK rows.
            BATCH_TOK_CHUNK = 2000   # ~400 MB per chunk at V_TOK=50257, N=4096
            n_valid = tot_t
            pred_tok_valid = np.empty(n_valid, dtype=np.int64)
            # log_prob of true token per valid position
            true_tok_logprob = np.empty(n_valid, dtype=np.float64)

            print("[seed=%d] batched token decode: %d positions (chunk=%d)..." % (
                seed, n_valid, BATCH_TOK_CHUNK), flush=True)
            for _ck_s in range(0, n_valid, BATCH_TOK_CHUNK):
                _ck_e = min(_ck_s + BATCH_TOK_CHUNK, n_valid)
                _cvecs = C[pred_c_valid[_ck_s:_ck_e]]      # (chunk, N)
                _lp = batched_token_logprob(D, _cvecs)      # (chunk, V_TOK)
                pred_tok_valid[_ck_s:_ck_e] = np.argmax(_lp, axis=1)
                # log-prob of the TRUE token at each position
                _tt = true_tok_valid[_ck_s:_ck_e]
                true_tok_logprob[_ck_s:_ck_e] = _lp[np.arange(_ck_e - _ck_s), _tt]

            # Substrate top-1 and NLL
            sub_t_ok = int((pred_tok_valid == true_tok_valid).sum())
            sub_nll = float(-true_tok_logprob.sum())

            # Unigram (cheap: all positions same pred and same log-prob lookup)
            uni_t_ok = int((uni_tok_pred == true_tok_valid).sum())
            uni_nll = float(-uni_log[true_tok_valid].sum())

            # Bigram (per-position dict lookup -- cheap Python loop over valid positions)
            big_t_ok = 0; big_nll = 0.0
            for _i in range(n_valid):
                _ts = int(t_src_tok_valid[_i]); _tt = int(true_tok_valid[_i])
                _bp = big_tok.get(_ts)
                if _bp is not None and _bp.sum() > 0:
                    big_t_ok += (int(np.argmax(_bp)) == _tt)
                    _bfd = _bp.astype(np.float32) / (_bp.sum() + 1e-6)
                    big_nll += -math.log(float(_bfd[_tt]) + 1e-300)
                else:
                    big_t_ok += (uni_tok_pred == _tt)
                    big_nll += float(-uni_log[_tt])

            # Ceiling (oracle concept -> best token; per-position dict lookup -- cheap)
            ceil_t_ok = 0; ceil_nll = 0.0
            for _i in range(n_valid):
                _ctgt = int(c_tgt_valid[_i]); _tt = int(true_tok_valid[_i])
                _ceil_t = ceiling_pred.get(_ctgt, uni_tok_pred)
                ceil_t_ok += (_ceil_t == _tt)
                _ctd = concept_tok_counts.get(_ctgt)
                if _ctd is not None and _ctd.sum() > 0:
                    _ctd_d = _ctd.astype(np.float32) / (_ctd.sum() + 1e-6)
                    ceil_nll += -math.log(float(_ctd_d[_tt]) + 1e-300)
                else:
                    ceil_nll += float(-uni_log[_tt])

        # Recall plateau tracker: sample sub_c_ok/tot_c at doc boundaries (every 100 positions)
        recall_plateau_checks: List[float] = []
        _cum_ok = 0; _cum_tot = 0
        _prev_end = 0
        for _di, _end in enumerate(_doc_end_idx):
            if _end == _prev_end:
                continue
            _seg_pred = pred_concept_all[_prev_end:_end]
            _seg_tgt = c_tgt_all[_prev_end:_end]
            _cum_ok += int((_seg_pred == _seg_tgt).sum())
            _cum_tot = _end
            if _cum_tot % 100 == 50 and _cum_tot > 0:
                recall_plateau_checks.append(_cum_ok / max(_cum_tot, 1))
            _prev_end = _end

        # Saturation guard: recall plateau across test positions
        plateau_saturated = False
        if recall_plateau_checks and len(recall_plateau_checks) >= 3:
            recent = recall_plateau_checks[-3:]
            if min(recent) >= 0.5:
                plateau_saturated = True
    any_saturated = saturated or plateau_saturated

    tc = max(tot_c, 1); tt = max(tot_t, 1)
    elapsed = time.time() - t0

    return {
        "seed": seed,
        "n_docs": len(train_seqs) + len(test_seqs),
        "n_train_docs": len(train_seqs),
        "n_test_docs": len(test_seqs),
        "V_TOK": V_TOK,
        "V_C": V_C,
        "N_DIM": n_dim,
        "f_sparse": f,
        "k_active": k_val,
        "n_trans": n_trans,
        "n_unique_pairs": n_unique_pairs,
        "alpha": alpha,
        "codebook_utilization": utilization,
        "saturated": any_saturated,
        "run_mode": RUN_MODE,
        # concept-level
        "substrate_concept_top1": sub_c_ok / tc,
        "unigram_concept_top1": uni_c_ok / tc,
        "bigram_concept_top1": big_c_ok / tc,
        "n_concept_test_pairs": tot_c,
        # token-level
        "substrate_top1": sub_t_ok / tt,
        "substrate_bpc": (sub_nll / tt) / log2,
        "unigram_top1": uni_t_ok / tt,
        "unigram_bpc": (uni_nll / tt) / log2,
        "bigram_top1": big_t_ok / tt,
        "bigram_bpc": (big_nll / tt) / log2,
        "ceiling_top1": ceil_t_ok / tt,
        "ceiling_bpc": (ceil_nll / tt) / log2,
        "n_token_test_pairs": tot_t,
        "elapsed_s": elapsed,
    }


# ---------------------------------------------------------------------------
# Verdict (Skunkworks N3 corpus-eval cert-bands, 2026-06-21T16:06:58Z)
# ---------------------------------------------------------------------------

def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    def _mean(key: str) -> float:
        vals = [p[key] for p in ps if key in p and p[key] is not None and not math.isnan(p[key])]
        return float(np.mean(vals)) if vals else float("nan")

    sub_bpc = _mean("substrate_bpc")
    uni_bpc = _mean("unigram_bpc")
    big_bpc = _mean("bigram_bpc")
    ceil_bpc = _mean("ceiling_bpc")
    sub_top1 = _mean("substrate_top1")
    uni_top1 = _mean("unigram_top1")
    big_top1 = _mean("bigram_top1")
    sub_c_top1 = _mean("substrate_concept_top1")
    alpha = _mean("alpha")

    # CV across seeds (required for HARD_PASS)
    bpc_vals = [p["substrate_bpc"] for p in ps if "substrate_bpc" in p
                and not math.isnan(p["substrate_bpc"])]
    cv = (float(np.std(bpc_vals)) / abs(float(np.mean(bpc_vals))) if len(bpc_vals) > 1
          and abs(float(np.mean(bpc_vals))) > 1e-9 else 0.0)

    any_saturated = any(p.get("saturated", False) for p in ps)
    distillation_gap = sub_bpc - ceil_bpc

    summary = (
        "substrate_bpc=%.2f unigram_bpc=%.2f bigram_bpc=%.2f ceiling_bpc=%.2f "
        "distillation_gap=%.2f_bits "
        "sub_top1=%.3f uni_top1=%.3f big_top1=%.3f "
        "concept_top1=%.3f bpc_cv=%.3f alpha=%.3f "
        "(V_C=%d N_DIM=%d f=%.4f mode=%s seeds=%d%s)" % (
            sub_bpc, uni_bpc, big_bpc, ceil_bpc, distillation_gap,
            sub_top1, uni_top1, big_top1,
            sub_c_top1, cv, alpha,
            V_C, N_DIM, F_SPARSE, RUN_MODE, len(ps),
            " SATURATION-FLAG" if any_saturated else "",
        )
    )

    # SATURATION GATE: demote to PROVEN-BOUND if saturated
    saturation_note = (
        " [PROVEN-BOUND: alpha=%.3f>1.0 or recall-plateau>=0.5; "
        "not chain-grade -- tiered result]" % alpha if any_saturated else ""
    )

    # Skunkworks N3 bands (2026-06-21T16:06:58Z):
    # HARD_FAIL: substrate BPC >= unigram_BPC (no real structure)
    if math.isnan(sub_bpc) or sub_bpc >= uni_bpc:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate token decode does not beat unigram (no real structure). "
                + summary)

    # HARD_PASS: sub_bpc < bigram_bpc AND cv <= 0.05 AND substrate-only (zero LLM at inference)
    # substrate-only is structural (enforced by design -- no LLM calls in this script at inference)
    if sub_bpc < big_bpc and cv <= 0.05:
        if any_saturated:
            return ("MIDDLE_BAND",
                    "MIDDLE_BAND (saturation-demote): sub_bpc < bigram but SATURATION FLAG raised; "
                    "demote to PROVEN-BOUND -- not chain-grade. " + summary + saturation_note)
        return ("HARD_PASS",
                "HARD_PASS: substrate-native BPC < token-bigram AND cv<=0.05 AND substrate-only-decode. "
                + summary)

    # MIDDLE_BAND: sub_bpc in (bigram_bpc, unigram_bpc)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: substrate BPC beats unigram but not bigram. " + summary + saturation_note)


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s V_C=%d N_DIM=%d f=%.4f MAX_DOCS=%d seeds=%s" % (
    ANCHOR_NAME, RUN_MODE, V_C, N_DIM, F_SPARSE, MAX_DOCS, SEEDS), flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "N": N_DIM}

done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds already complete; running %s" % (
    len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

t_total = time.time()
ps = []

for seed in remaining_seeds:
    r = run_seed(seed)
    ps.append(r)
    write_partial(out_dir, seed, r)
    print("  [seed=%d] substrate_bpc=%.2f unigram_bpc=%.2f bigram_bpc=%.2f "
          "sub_top1=%.3f concept_top1=%.3f alpha=%.3f%s" % (
              seed, r["substrate_bpc"], r["unigram_bpc"], r["bigram_bpc"],
              r["substrate_top1"], r["substrate_concept_top1"], r["alpha"],
              " [SATURATED]" if r.get("saturated") else ""), flush=True)

# Load any done seeds from checkpoint
if done_seeds:
    agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
    for k, v in agg.items():
        ps.append(v)

if not ps:
    print("[ERROR] no seeds completed; aborting", flush=True)
    sys.exit(1)

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
    "N_DIM": N_DIM,
    "f_sparse": F_SPARSE,
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
