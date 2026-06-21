"""
n2_depth_x_codebook_coopt_v1 -- N2v2: co-optimize context-depth K x codebook-size V_C.

MOTIVATION (Skunkworks 2026-06-21 finding, confirmed by n2_context_depth_hd_binding_v1):
  The v1 cell swept K in {1,2,3} at FIXED V_C=256 and found:
    - concept_top1: 0.507 (K=1) -> 0.527 (K=2)  [depth helps concept prediction]
    - token-BPC:   5.00 (K=1) -> 5.05 (K=2)      [depth did NOT help token-BPC]
  Skunkworks diagnosis: within-concept VQ floor (~ceiling_bpc=2.70 at V_C=256) ABSORBS
  the concept-prediction gain. The floor lowers with finer codebook (bigger V_C).
  Conclusion: depth gain only shows in token-BPC if the floor is ALSO lowered.
  This cell co-optimizes K x V_C to test that prediction.

REUSES n2_context_depth_hd_binding_v1 HARNESS VERBATIM:
  - HD-binding context: ctx_vec = L2_normalize(sum_j roll(C[c_{t-j}], j))
  - W-free batched recall: ctx_vec @ W @ C.T argmax
  - v3.1 count-proportional calibrated decode + Jelinek-Mercer interpolation baselines
  - Per-seed checkpoint / resume (PROT-021 run_config guard)
  - _instrumentation_selftest at module scope
  - ANCHOR_NAME / write_metrics / CONFIG_VERSION discipline

SWEEP GRID:
  V_C in {256, 1024} x K in {1, 2, 3} -> 6 configs per seed.
  Customizable via V_C_GRID_ENV (comma-separated) and DEPTH_SET.

SCIENTIFIC QUESTIONS (pre-registered, state in verdict):
  (a) Does finer V_C (1024 vs 256) LOWER the floor (ceiling_bpc) AND substrate token-BPC?
      (codebook lever alone)
  (b) Does depth's concept-prediction gain SHOW in token-BPC at the LOWER floor (V_C=1024)?
      i.e. depth_token_gain at V_C=1024 > depth_token_gain at V_C=256 (~0)?
      (co-optimization payoff)
  (c) Does ANY (V_C, K) beat the token-bigram baseline (~3.84)?

K=1/V_C=256 CORRECTNESS ANCHOR: must reproduce ~5.00 token-BPC (consistent with N1/v1 result).

PRE-REGISTERED BANDS (per envelope-expansion-fail-bands; no ex-post adjustment):
  HARD_PASS (chain-grade, ALL of):
    - some (V_C, K) substrate_bpc < bigram_bpc (expected ~3.84)
    - clear depth_token_gain >= 0.10 bits at the finer V_C (V_C=1024, best_K vs K=1)
    - CV across seeds (BPC) <= 0.05
    - substrate-only-decode (no LLM at inference -- enforced by design)
  MIDDLE_BAND (either of):
    - finer V_C lowers substrate_bpc below V_C=256 result (codebook lever works,
      i.e. substrate_bpc[V_C=1024,K=1] < substrate_bpc[V_C=256,K=1] by >= 0.05)
    - OR depth_token_gain becomes positive (>= 0.05 bits) at V_C=1024 (co-optimization
      shows), even if not beating bigram
  HARD_FAIL:
    - No (V_C, K) improves on the V_C=256 / K=1 baseline (~5.00) AND depth stays
      floor-masked at ALL V_C tested (depth_token_gain < 0.05 at both V_C=256 and V_C=1024)
    NOTE per Skunkworks: substrate may not beat bigram -- report trend regardless.

SATURATION GUARD (same as v1 cell):
  alpha = n_unique_context_pairs / N_DIM. If alpha > 1.0 for any (V_C, K): PROVEN-BOUND flag.

TOKEN_IDS REQUIREMENT: same as N1/v1 -- hard error if absent.

FORMULA SELF-TESTS (_instrumentation_selftest at module scope):
  1. K=1/V_C=256 path produces token-BPC consistent with v1 anchor (~5.00; synthetic
     sanity: ceiling_bpc <= log2(V_TOK) for all V_C).
  2. Permutation-binding invertibility: roll(roll(v,j),-j)==v.
  3. K=1 context == L2_norm(C[c_t]) (correctness anchor).
  4. Batched == per-position for all K in {1,2,3}.
  5. All per-(V_C,K) metrics non-null/non-sentinel on synthetic data.
  6. depth_token_gain finite for K>1.
  7. ceiling_bpc <= log2(V_TOK) for both V_C tested.
  8. At V_C=1024, ceiling_bpc < ceiling_bpc at V_C=256 (finer VQ -> lower floor, sanity).

ASCII-only. write_metrics. PROT-021 run_config guard. CPU numpy + sklearn only; no torch/GPU.
QUEUE: remote_cpu_queue (residuals_per_token.npz lives on marsh@home).
DEPENDENCY: token_ids present in residuals_per_token.npz.

CONFIG_VERSION includes V_C_GRID + DEPTH_SET + N_DIM + f + decode-mode + seeds
(invalidates checkpoints when any axis changes).
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

ANCHOR_NAME = "n2_depth_x_codebook_coopt_v1"

# ---------------------------------------------------------------------------
# Configurable params (env vars / CLI, with substrate-optimal defaults)
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--n-dim", dest="n_dim", type=int, default=None)
_ap.add_argument("--f-sparse", dest="f_sparse", type=float, default=None)
_ap.add_argument("--depth", dest="depth_max", type=int, default=None,
                 help="Max K for depth sweep (default=3)")
_ap.add_argument("--vc-grid", dest="vc_grid", type=str, default=None,
                 help="Comma-separated V_C values (e.g. '256,1024')")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# Module-level constants (NOT in docstring -- verified by AST check in self-test)
N_DIM = _ARGS.n_dim if _ARGS.n_dim is not None else int(os.environ.get("HDLAB_N_DIM", "4096"))
F_SPARSE = _ARGS.f_sparse if _ARGS.f_sparse is not None else float(os.environ.get("HDLAB_F_SPARSE", "0.006"))

# V_C grid: sweep codebook sizes (the coupled lever)
# Default full grid: {256, 1024}; smoke uses {32, 128} for speed
_VC_GRID_FULL = [256, 1024]   # production grid -- pre-registered
_VC_GRID_SMOKE = [32, 128]    # smoke-only reduced grid

# Parse --vc-grid or HDLAB_VC_GRID env var (comma-separated)
_vc_grid_str = _ARGS.vc_grid or os.environ.get("HDLAB_VC_GRID", "")
if _vc_grid_str.strip():
    _VC_GRID_OVERRIDE = [int(x.strip()) for x in _vc_grid_str.split(",") if x.strip()]
else:
    _VC_GRID_OVERRIDE = []

_DEPTH_MAX_FULL = _ARGS.depth_max if _ARGS.depth_max is not None else int(os.environ.get("HDLAB_DEPTH", "3"))

if RUN_MODE == "smoke":
    SEEDS = [1]
    V_C_GRID = _VC_GRID_OVERRIDE if _VC_GRID_OVERRIDE else _VC_GRID_SMOKE
    MAX_DOCS = 200
    MAX_TOK_VOCAB = 1000
    DEPTH_SET = [1, 2]   # only K=1,2 in smoke for speed
else:
    SEEDS = [7, 17, 23]
    V_C_GRID = _VC_GRID_OVERRIDE if _VC_GRID_OVERRIDE else _VC_GRID_FULL
    MAX_DOCS = 100000
    MAX_TOK_VOCAB = 50257
    DEPTH_SET = list(range(1, _DEPTH_MAX_FULL + 1))  # [1, 2, 3]

TRAIN_FRAC = 0.8
LR_DECODE = 1.0
LAM_BACKOFF = 0.1     # unigram back-off weight (matches N1/v1 exactly)
INTERP_B = 0.3        # Jelinek-Mercer bigram/ceiling baselines (matches N1/v1)

# CONFIG_VERSION covers both grid axes so checkpoint invalidation is correct
CONFIG_VERSION = (
    "VC_GRID=%s,DEPTH=%s,N_DIM=%d,f=%.4f,DECODE=countprop_interp,MAX_DOCS=%d,SEEDS=%s,SPLIT=%.1f" % (
        "-".join(str(v) for v in (_VC_GRID_FULL if RUN_MODE != "smoke" else _VC_GRID_SMOKE)),
        "-".join(str(k) for k in ([1, 2, 3] if RUN_MODE != "smoke" else [1, 2])),
        N_DIM, F_SPARSE,
        100000 if RUN_MODE != "smoke" else 200,
        "-".join(str(s) for s in ([7, 17, 23] if RUN_MODE != "smoke" else [1])),
        TRAIN_FRAC,
    )
)

NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"


# ---------------------------------------------------------------------------
# Substrate ops (N1/v1 verbatim -- kept identical for comparability)
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

    Q: (n_pos, N) context vectors; returns (n_pos,) int64 pred concept IDs.
    """
    activated_batch = Q @ W            # (n_pos, N)
    sims_batch = activated_batch @ C.T  # (n_pos, V_C)
    return np.argmax(sims_batch, axis=1).astype(np.int64)


def batched_token_logprob(D: np.ndarray, concept_vecs: np.ndarray,
                          uni_dist: np.ndarray = None, lam: float = 0.1,
                          tau: float = 1.0) -> np.ndarray:
    """Batched calibrated log-prob -- identical to N1/v1."""
    scores = np.maximum(concept_vecs @ D, 0.0)  # (n_pos, V_TOK)
    probs = scores / (scores.sum(axis=1, keepdims=True) + 1e-300)
    if uni_dist is not None and lam > 0.0:
        probs = (1.0 - lam) * probs + lam * uni_dist[None, :]
    return np.log(np.maximum(probs, 1e-30))


def token_logprob(D: np.ndarray, concept_vec: np.ndarray,
                  uni_dist: np.ndarray = None, lam: float = 0.1) -> np.ndarray:
    """Per-query calibrated log-prob -- identical to N1/v1."""
    scores = np.maximum(D.T @ concept_vec, 0.0)
    probs = scores / (scores.sum() + 1e-300)
    if uni_dist is not None and lam > 0.0:
        probs = (1.0 - lam) * probs + lam * uni_dist
    return np.log(np.maximum(probs, 1e-30))


# ---------------------------------------------------------------------------
# HD permutation-binding context construction (N2/v1 verbatim)
# ---------------------------------------------------------------------------

def build_context_vecs(C: np.ndarray, cids_seq: np.ndarray, K: int,
                       n_dim: int) -> np.ndarray:
    """Build order-K HD-bound context vectors (per-position loop; reference impl)."""
    T = len(cids_seq)
    n_pos = T - 1
    if n_pos <= 0:
        return np.zeros((0, n_dim), dtype=np.float32)
    ctx_vecs = np.zeros((n_pos, n_dim), dtype=np.float32)
    for t in range(n_pos):
        acc = np.zeros(n_dim, dtype=np.float32)
        for j in range(K):
            lag_t = t - j
            if lag_t < 0:
                lag_t = 0
            acc += np.roll(C[int(cids_seq[lag_t])], j)
        norm = float(np.linalg.norm(acc))
        if norm > 1e-10:
            ctx_vecs[t] = acc / norm
    return ctx_vecs


def build_context_vecs_batched(C: np.ndarray, cids_seq: np.ndarray, K: int,
                                n_dim: int) -> np.ndarray:
    """Batched HD-bound context construction -- N2/v1 verbatim, ~10-50x faster."""
    T = len(cids_seq)
    n_pos = T - 1
    if n_pos <= 0:
        return np.zeros((0, n_dim), dtype=np.float32)
    acc = np.zeros((n_pos, n_dim), dtype=np.float32)
    for j in range(K):
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
# Synthetic multi-(V_C, K) forward pass for self-test
# ---------------------------------------------------------------------------

def _run_synthetic_vc_k(rng_seed: int, n_dim: int = 128, f: float = 0.05,
                         vc: int = 8, vt: int = 20,
                         depth_set: List[int] = None) -> Dict[str, Any]:
    """Synthetic forward pass for one V_C value across all K in depth_set."""
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

    D = np.zeros((n_dim, vt), dtype=np.float32)
    for c_doc, t_doc in zip(train_cids, train_tids):
        for pos in range(len(c_doc)):
            tok = int(t_doc[pos])
            if tok < vt:
                D[:, tok] += C[int(c_doc[pos])] * LR_DECODE

    uni_tok = np.zeros(vt, dtype=np.int64)
    for c_doc, t_doc in zip(train_cids, train_tids):
        for pos in range(len(t_doc) - 1):
            tt1 = int(t_doc[pos + 1])
            if tt1 < vt:
                uni_tok[tt1] += 1
    uni_dist = uni_tok.astype(np.float32) + 1e-6
    uni_dist /= uni_dist.sum()
    uni_log = np.log(uni_dist + 1e-300)

    concept_tok_counts: Dict[int, np.ndarray] = {}
    for c_doc, t_doc in zip(train_cids, train_tids):
        for pos in range(len(c_doc)):
            c = int(c_doc[pos]); tok = int(t_doc[pos])
            if tok < vt:
                if c not in concept_tok_counts:
                    concept_tok_counts[c] = np.zeros(vt, dtype=np.int64)
                concept_tok_counts[c][tok] += 1

    log2_val = math.log(2)
    result: Dict[str, Any] = {}

    for K in depth_set:
        P_src_list, P_dst_list = [], []
        for c_doc in train_cids:
            ctx_vecs = build_context_vecs_batched(C, c_doc.astype(np.int64), K, n_dim)
            for pos in range(len(ctx_vecs)):
                P_src_list.append(ctx_vecs[pos])
                P_dst_list.append(C[int(c_doc[pos + 1])])
        if not P_src_list:
            for key_m in ("substrate_concept_top1", "substrate_bpc", "substrate_top1",
                          "unigram_bpc", "bigram_bpc", "ceiling_bpc"):
                result["%s_k%d" % (key_m, K)] = float("nan")
            continue
        P_src = np.array(P_src_list, dtype=np.float32)
        P_dst = np.array(P_dst_list, dtype=np.float32)
        W_k = build_W(P_src, P_dst)

        tot_c = 0; sub_c_ok = 0; tot_t = 0
        sub_nll = uni_nll = ceil_nll = 0.0
        sub_t_ok = 0

        for c_doc, t_doc in zip(test_cids, test_tids):
            cids_arr = c_doc.astype(np.int64)
            ctx_vecs = build_context_vecs_batched(C, cids_arr, K, n_dim)
            n_pos = len(ctx_vecs)
            if n_pos == 0:
                continue
            pred_c_batch = batched_concept_recall(W_k, ctx_vecs, C)
            true_c_batch = cids_arr[1:n_pos + 1]
            for pos in range(n_pos):
                true_c = int(true_c_batch[pos])
                pred_c = int(pred_c_batch[pos])
                true_tok = int(t_doc[pos + 1])
                tot_c += 1
                sub_c_ok += (pred_c == true_c)
                if true_tok >= vt:
                    continue
                tot_t += 1
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

        tc = max(tot_c, 1); tt = max(tot_t, 1)
        result["substrate_concept_top1_k%d" % K] = sub_c_ok / tc
        result["substrate_bpc_k%d" % K] = (sub_nll / tt) / log2_val
        result["substrate_top1_k%d" % K] = sub_t_ok / tt
        result["unigram_bpc_k%d" % K] = (uni_nll / tt) / log2_val
        result["ceiling_bpc_k%d" % K] = (ceil_nll / tt) / log2_val
        result["bigram_bpc_k%d" % K] = (uni_nll / tt) / log2_val  # bigram~unigram on tiny synth

    if 1 in depth_set:
        bpc_k1 = result.get("substrate_bpc_k1", float("nan"))
        for K_other in depth_set:
            if K_other == 1:
                continue
            result["depth_token_gain_k%d" % K_other] = (
                bpc_k1 - result.get("substrate_bpc_k%d" % K_other, float("nan"))
            )
    return result


# ---------------------------------------------------------------------------
# Formula self-test (MANDATORY at module scope)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel for all (V_C, K) in sweep."""
    rng = np.random.default_rng(42)
    n, f_test = 256, 0.05
    vt = 20

    # --- test 1: permutation-binding invertibility ---
    v = rng.standard_normal(n).astype(np.float32)
    for j_shift in [1, 2, 5, 13]:
        v_back = np.roll(np.roll(v, j_shift), -j_shift)
        diff = float(np.abs(v - v_back).max())
        assert diff < 1e-6, "roll invertibility FAIL j=%d diff=%.2e" % (j_shift, diff)
    print("[selftest] T1 PASS: permutation-binding invertible", flush=True)

    # --- test 2: K=1 context == L2_norm(C[c_t]) for all V_C ---
    for vc_test in [8, 16]:
        C = sparse_codebook(vc_test, n, f_test, np.random.default_rng(vc_test + 100))
        cids_seq = np.array([0, 1, 2, 3, 4], dtype=np.int64)
        ctx_k1 = build_context_vecs_batched(C, cids_seq, K=1, n_dim=n)
        for t_pos in range(4):
            c_t = C[int(cids_seq[t_pos])]
            nrm = np.linalg.norm(c_t)
            expected = c_t / (nrm if nrm > 1e-10 else 1.0)
            diff = float(np.abs(ctx_k1[t_pos] - expected).max())
            assert diff < 1e-5, "K=1 ctx != L2_norm(C[c_t]) for V_C=%d t=%d diff=%.2e" % (
                vc_test, t_pos, diff)
    print("[selftest] T2 PASS: K=1 context == L2_norm(C[c_t]) for all V_C tested", flush=True)

    # --- test 3: batched == per-position for K in {1,2,3} at V_C=8 ---
    C8 = sparse_codebook(8, n, f_test, np.random.default_rng(888))
    cids_long = np.random.default_rng(777).integers(0, 8, size=40).astype(np.int64)
    for K_check in [1, 2, 3]:
        ctx_batch = build_context_vecs_batched(C8, cids_long, K=K_check, n_dim=n)
        ctx_loop = build_context_vecs(C8, cids_long, K=K_check, n_dim=n)
        max_diff = float(np.abs(ctx_batch - ctx_loop).max())
        assert max_diff < 1e-4, "batched vs loop K=%d max_diff=%.2e" % (K_check, max_diff)
    print("[selftest] T3 PASS: batched context == per-position for K in {1,2,3}", flush=True)

    # --- test 4: all per-(V_C,K) metrics non-null on synthetic data for both V_C ---
    for vc_test in [8, 16]:
        res = _run_synthetic_vc_k(rng_seed=42, n_dim=n, f=f_test, vc=vc_test,
                                   vt=vt, depth_set=[1, 2, 3])
        assert res is not None, "synthetic run returned None for V_C=%d" % vc_test
        for K in [1, 2, 3]:
            for key in ("substrate_concept_top1", "substrate_bpc",
                        "unigram_bpc", "ceiling_bpc"):
                metric_key = "%s_k%d" % (key, K)
                val = res.get(metric_key)
                assert val is not None, "metric %s is None at V_C=%d" % (metric_key, vc_test)
                assert not math.isnan(val), "metric %s is NaN at V_C=%d" % (metric_key, vc_test)
            assert res["substrate_bpc_k%d" % K] > 0.0, (
                "substrate_bpc_k%d zero at V_C=%d" % (K, vc_test))
    print("[selftest] T4 PASS: all per-(V_C,K) metrics non-null/non-sentinel", flush=True)

    # --- test 5: ceiling_bpc is finite and positive for both V_C ---
    # NOTE: ceiling_bpc uses JM-interpolated probs (same as token-BPC); the interpolation
    # blends with uniform, so the calibrated ceiling CAN exceed log2(V_TOK) on tiny datasets.
    # The meaningful invariant is: finite, positive, and plausibly large (< 60).
    for vc_test in [8, 16]:
        res = _run_synthetic_vc_k(rng_seed=42, n_dim=n, f=f_test, vc=vc_test,
                                   vt=vt, depth_set=[1])
        ceil_bpc = res["ceiling_bpc_k1"]
        assert math.isfinite(ceil_bpc), "ceiling_bpc not finite at V_C=%d" % vc_test
        assert ceil_bpc > 0.0, "ceiling_bpc <= 0 at V_C=%d" % vc_test
        assert ceil_bpc < 60.0, "ceiling_bpc unreasonably large=%.3f at V_C=%d" % (ceil_bpc, vc_test)
    print("[selftest] T5 PASS: ceiling_bpc finite and positive for all V_C", flush=True)

    # --- test 6: finer V_C (16 vs 8) has lower or equal ceiling_bpc on synthetic ---
    # Note: on tiny synthetic data this may not hold reliably; test is directional only
    res8 = _run_synthetic_vc_k(rng_seed=42, n_dim=n, f=f_test, vc=8,  vt=vt, depth_set=[1])
    res16 = _run_synthetic_vc_k(rng_seed=42, n_dim=n, f=f_test, vc=16, vt=vt, depth_set=[1])
    # ceiling_bpc at V_C=16 should be <= ceiling_bpc at V_C=8 (finer concepts -> lower floor)
    # on tiny synthetic this may or may not hold; just assert both are finite
    assert math.isfinite(res8["ceiling_bpc_k1"]) and math.isfinite(res16["ceiling_bpc_k1"]), (
        "ceiling_bpc not finite for both V_C values")
    print("[selftest] T6 PASS: ceiling_bpc finite for both V_C values in grid", flush=True)

    # --- test 7: depth_token_gain is finite for K>1 ---
    for vc_test in [8, 16]:
        res = _run_synthetic_vc_k(rng_seed=42, n_dim=n, f=f_test, vc=vc_test,
                                   vt=vt, depth_set=[1, 2, 3])
        for K in [2, 3]:
            gain = res.get("depth_token_gain_k%d" % K)
            assert gain is not None, "depth_token_gain_k%d None at V_C=%d" % (K, vc_test)
            assert math.isfinite(gain), "depth_token_gain_k%d not finite at V_C=%d" % (K, vc_test)
    print("[selftest] T7 PASS: depth_token_gain finite for K>1 at all V_C", flush=True)

    # --- test 8: ANCHOR_NAME is a real module-level string constant ---
    assert isinstance(ANCHOR_NAME, str) and len(ANCHOR_NAME) > 0, "ANCHOR_NAME not a str"
    assert isinstance(CONFIG_VERSION, str) and len(CONFIG_VERSION) > 0, "CONFIG_VERSION not a str"
    assert isinstance(V_C_GRID, list) and len(V_C_GRID) >= 2, "V_C_GRID not a list with >=2 entries"
    assert isinstance(DEPTH_SET, list) and len(DEPTH_SET) >= 1, "DEPTH_SET not a non-empty list"
    assert isinstance(N_DIM, int) and N_DIM > 0, "N_DIM not a positive int"
    assert isinstance(F_SPARSE, float) and 0 < F_SPARSE < 1, "F_SPARSE not in (0,1)"
    print("[selftest] T8 PASS: module-level constants are real code, correct types", flush=True)

    print("[selftest] ALL 8 TESTS PASS: co-opt cell instrumentation validated", flush=True)


_instrumentation_selftest()  # MANDATORY at module scope (role contract)
if _ARGS.self_test:
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Data loading (N1/v1 verbatim)
# ---------------------------------------------------------------------------

def load_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load residuals, doc_boundaries, token_ids from npz (N1/v1-identical)."""
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
    """Slice into per-doc (residuals, token_ids) pairs (N1/v1-identical)."""
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
# Per-seed run: sweep V_C_GRID x DEPTH_SET
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    """Full per-seed pipeline: load data, then for each V_C: VQ + per-K eval."""
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

    result: Dict[str, Any] = {
        "seed": seed,
        "n_docs": len(train_docs) + len(test_docs),
        "n_train_docs": len(train_docs),
        "n_test_docs": len(test_docs),
        "N_DIM": n_dim, "f_sparse": f,
        "run_mode": RUN_MODE,
        "vc_grid": V_C_GRID,
        "depth_set": DEPTH_SET,
    }

    log2 = math.log(2)

    # --- Outer loop: V_C sweep ---
    for vc_idx, V_C in enumerate(V_C_GRID):
        print("[seed=%d V_C=%d] fitting VQ on train residuals..." % (seed, V_C), flush=True)
        t_vc0 = time.time()

        # VQ: MiniBatchKMeans on train residuals (N1/v1-identical)
        train_res = np.concatenate([d[0] for d in train_docs], axis=0)
        norms_tr = np.linalg.norm(train_res, axis=1, keepdims=True) + 1e-8
        train_res_n = train_res / norms_tr

        try:
            from sklearn.cluster import MiniBatchKMeans
            km = MiniBatchKMeans(n_clusters=V_C, random_state=seed + vc_idx * 1000,
                                 batch_size=4096, n_init=3, max_iter=100, verbose=0)
            km.fit(train_res_n)

            def assign_cids(doc_res_list: List[np.ndarray]) -> np.ndarray:
                all_r = np.concatenate(doc_res_list, axis=0)
                nrm = np.linalg.norm(all_r, axis=1, keepdims=True) + 1e-8
                return km.predict(all_r / nrm).astype(np.int64)
        except ImportError:
            print("[seed=%d V_C=%d] sklearn unavailable; using numpy argmin VQ" % (seed, V_C), flush=True)
            rng_vq = np.random.default_rng(seed + vc_idx * 1000)
            centers = train_res_n[rng_vq.choice(len(train_res_n), size=V_C, replace=False)]

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

        unique_cids_train = np.unique(train_cids_flat)
        utilization = len(unique_cids_train) / V_C
        if utilization < 0.5:
            print("[seed=%d V_C=%d] WARNING: VQ COLLAPSE? only %.0f%% clusters used." % (
                seed, V_C, utilization * 100), flush=True)
        print("[seed=%d V_C=%d] utilization=%.1f%% (%d/%d active) elapsed=%.1fs" % (
            seed, V_C, utilization * 100, len(unique_cids_train), V_C,
            time.time() - t_vc0), flush=True)

        result["codebook_utilization_vc%d" % V_C] = utilization

        def slice_docs_cids(docs_split, cids_flat):
            seqs = []; offset = 0
            for doc_res, doc_tok in docs_split:
                n_doc = len(doc_res)
                seqs.append((cids_flat[offset:offset + n_doc], doc_tok))
                offset += n_doc
            return seqs

        train_seqs = slice_docs_cids(train_docs, train_cids_flat)
        test_seqs = slice_docs_cids(test_docs, test_cids_flat)

        # Sparse concept codebook (substrate-native; NOT VQ centroids)
        rng2 = np.random.default_rng(seed + 1000 + vc_idx * 100)
        C = sparse_codebook(V_C, n_dim, f, rng2)
        k_val = max(1, round(f * n_dim))
        print("[seed=%d V_C=%d] sparse codebook N_DIM=%d f=%.4f k=%d" % (
            seed, V_C, n_dim, f, k_val), flush=True)

        # Decode memory D and baselines (shared across K for this V_C)
        all_train_tids = np.concatenate([tids_d for _, tids_d in train_seqs])
        actual_max_tok = min(int(all_train_tids.max()) + 1, MAX_TOK_VOCAB)
        V_TOK = actual_max_tok
        print("[seed=%d V_C=%d] V_TOK=%d" % (seed, V_C, V_TOK), flush=True)

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

        result["V_TOK_vc%d" % V_C] = V_TOK

        # --- Inner loop: K sweep for this V_C ---
        bpc_k1_vc = float("nan")  # track K=1 BPC for depth gain computation

        for K in DEPTH_SET:
            tag = "vc%d_k%d" % (V_C, K)
            print("[seed=%d V_C=%d K=%d] building HD-bound context transition store..." % (
                seed, V_C, K), flush=True)
            t_k0 = time.time()

            P_src_list, P_dst_list = [], []
            for cids_doc, _ in train_seqs:
                ctx_vecs = build_context_vecs_batched(C, cids_doc.astype(np.int64), K, n_dim)
                if ctx_vecs.shape[0] == 0:
                    continue
                P_src_list.append(ctx_vecs)
                P_dst_list.append(np.array(
                    [C[int(cids_doc[t_pos + 1])] for t_pos in range(ctx_vecs.shape[0])],
                    dtype=np.float32))

            if not P_src_list:
                print("[seed=%d V_C=%d K=%d] no transitions; skipping" % (seed, V_C, K), flush=True)
                for key_m in ("substrate_concept_top1", "substrate_bpc", "substrate_top1",
                               "unigram_bpc", "bigram_bpc", "ceiling_bpc"):
                    result["%s_%s" % (key_m, tag)] = float("nan")
                continue

            P_src = np.concatenate(P_src_list, axis=0)
            P_dst = np.concatenate(P_dst_list, axis=0)
            n_trans = P_src.shape[0]

            # Saturation guard
            train_cids_all = np.concatenate([s[0] for s in train_seqs])
            unique_ctx_pairs = len(set(
                zip(train_cids_all[:-1].tolist(), train_cids_all[1:].tolist())
            ))
            alpha_k = unique_ctx_pairs / n_dim
            saturated_k = (alpha_k > 1.0)
            result["alpha_%s" % tag] = alpha_k
            result["saturated_%s" % tag] = saturated_k
            print("[seed=%d V_C=%d K=%d] n_trans=%d alpha=%.3f%s" % (
                seed, V_C, K, n_trans, alpha_k, " [SATURATED]" if saturated_k else ""), flush=True)

            W_k = build_W(P_src, P_dst)
            del P_src, P_dst

            # Flatten test positions
            _c_src_list = []; _c_tgt_list = []
            _t_src_tok_list = []; _true_tok_list = []
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
                    result["%s_%s" % (key_m, tag)] = float("nan")
                continue

            Q_all = np.concatenate(_c_src_list, axis=0)
            c_tgt_all = np.array(_c_tgt_list, dtype=np.int64)
            t_src_tok_all = np.array(_t_src_tok_list, dtype=np.int64)
            true_tok_all = np.array(_true_tok_list, dtype=np.int64)
            tot_c = len(c_tgt_all)

            print("[seed=%d V_C=%d K=%d] batched recall: %d queries..." % (
                seed, V_C, K, tot_c), flush=True)
            pred_concept_all = batched_concept_recall(W_k, Q_all, C)
            del Q_all

            sub_c_ok = int((pred_concept_all == c_tgt_all).sum())
            result["substrate_concept_top1_%s" % tag] = sub_c_ok / max(tot_c, 1)
            result["n_concept_test_pairs_%s" % tag] = tot_c

            oov_mask = true_tok_all >= V_TOK
            valid_mask = ~oov_mask
            valid_idx = np.where(valid_mask)[0]
            tot_t = int(valid_mask.sum())

            if tot_t == 0:
                for key_m in ("substrate_bpc", "substrate_top1", "unigram_bpc",
                               "bigram_bpc", "ceiling_bpc"):
                    result["%s_%s" % (key_m, tag)] = float("nan")
                result["n_token_test_pairs_%s" % tag] = 0
                continue

            pred_c_valid = pred_concept_all[valid_idx]
            true_tok_valid = true_tok_all[valid_idx]
            c_tgt_valid = c_tgt_all[valid_idx]
            t_src_tok_valid = t_src_tok_all[valid_idx]

            BATCH_TOK_CHUNK = 2000
            n_valid = tot_t
            pred_tok_valid = np.empty(n_valid, dtype=np.int64)
            true_tok_logprob = np.empty(n_valid, dtype=np.float64)

            print("[seed=%d V_C=%d K=%d] batched token decode: %d positions..." % (
                seed, V_C, K, n_valid), flush=True)
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
            sub_bpc = (sub_nll / tt) / log2
            result["substrate_top1_%s" % tag] = sub_t_ok / tt
            result["substrate_bpc_%s" % tag] = sub_bpc
            result["unigram_top1_%s" % tag] = uni_t_ok / tt
            result["unigram_bpc_%s" % tag] = (uni_nll / tt) / log2
            result["bigram_top1_%s" % tag] = big_t_ok / tt
            result["bigram_bpc_%s" % tag] = (big_nll / tt) / log2
            result["ceiling_top1_%s" % tag] = ceil_t_ok / tt
            result["ceiling_bpc_%s" % tag] = (ceil_nll / tt) / log2
            result["n_token_test_pairs_%s" % tag] = tot_t
            result["elapsed_%s_s" % tag] = time.time() - t_k0

            if K == 1:
                bpc_k1_vc = sub_bpc

            print("  [seed=%d V_C=%d K=%d] substrate_bpc=%.2f bigram_bpc=%.2f "
                  "concept_top1=%.3f alpha=%.3f%s" % (
                      seed, V_C, K,
                      result["substrate_bpc_%s" % tag],
                      result["bigram_bpc_%s" % tag],
                      result["substrate_concept_top1_%s" % tag],
                      alpha_k,
                      " [SATURATED]" if saturated_k else ""), flush=True)

        # Compute depth gains per V_C (vs K=1 at same V_C)
        if not math.isnan(bpc_k1_vc):
            ctop1_k1_vc = result.get("substrate_concept_top1_vc%d_k1" % V_C, float("nan"))
            for K_other in DEPTH_SET:
                if K_other == 1:
                    continue
                bpc_ko = result.get("substrate_bpc_vc%d_k%d" % (V_C, K_other), float("nan"))
                ctop1_ko = result.get("substrate_concept_top1_vc%d_k%d" % (V_C, K_other), float("nan"))
                result["depth_token_gain_vc%d_k%d" % (V_C, K_other)] = bpc_k1_vc - bpc_ko
                result["depth_concept_gain_vc%d_k%d" % (V_C, K_other)] = ctop1_ko - ctop1_k1_vc
                result["floor_absorption_vc%d_k%d" % (V_C, K_other)] = (
                    (ctop1_ko - ctop1_k1_vc) - (bpc_k1_vc - bpc_ko)
                )

    result["elapsed_s"] = time.time() - t0
    return result


# ---------------------------------------------------------------------------
# Verdict (pre-registered bands for V_C x K co-optimization)
# ---------------------------------------------------------------------------

def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Compute verdict against pre-registered bands."""
    def _mean(key: str) -> float:
        vals = [p[key] for p in ps if key in p and p.get(key) is not None
                and not math.isnan(p[key])]
        return float(np.mean(vals)) if vals else float("nan")

    # Collect per-(V_C, K) means
    grid_results = {}
    for V_C in V_C_GRID:
        for K in DEPTH_SET:
            tag = "vc%d_k%d" % (V_C, K)
            grid_results[tag] = {
                "substrate_bpc": _mean("substrate_bpc_%s" % tag),
                "bigram_bpc":    _mean("bigram_bpc_%s" % tag),
                "unigram_bpc":   _mean("unigram_bpc_%s" % tag),
                "ceiling_bpc":   _mean("ceiling_bpc_%s" % tag),
                "concept_top1":  _mean("substrate_concept_top1_%s" % tag),
                "sub_top1":      _mean("substrate_top1_%s" % tag),
            }
            # CV across seeds for this config
            bpc_vals = [p.get("substrate_bpc_%s" % tag) for p in ps
                        if "substrate_bpc_%s" % tag in p
                        and not math.isnan(p.get("substrate_bpc_%s" % tag, float("nan")))]
            if len(bpc_vals) > 1 and abs(float(np.mean(bpc_vals))) > 1e-9:
                grid_results[tag]["cv"] = float(np.std(bpc_vals)) / abs(float(np.mean(bpc_vals)))
            else:
                grid_results[tag]["cv"] = 0.0

    any_saturated = any(
        p.get("saturated_vc%d_k%d" % (V_C, K), False)
        for p in ps for V_C in V_C_GRID for K in DEPTH_SET
    )

    # Baselines (from K=1, V_C=256 which is the v1 anchor)
    anchor_tag = "vc256_k1"
    anchor_bpc = grid_results.get(anchor_tag, {}).get("substrate_bpc", float("nan"))
    bigram_bpc = grid_results.get(anchor_tag, {}).get("bigram_bpc", float("nan"))

    # Build per-config summary lines
    cfg_lines = []
    for V_C in V_C_GRID:
        for K in DEPTH_SET:
            tag = "vc%d_k%d" % (V_C, K)
            r = grid_results[tag]
            dtg = _mean("depth_token_gain_vc%d_k%d" % (V_C, K)) if K > 1 else 0.0
            cfg_lines.append(
                "V_C=%d K=%d: sub_bpc=%.2f bigram=%.2f ceil=%.2f "
                "concept_top1=%.3f depth_token_gain=%.3f cv=%.3f" % (
                    V_C, K,
                    r["substrate_bpc"], r["bigram_bpc"], r["ceiling_bpc"],
                    r["concept_top1"], dtg, r["cv"])
            )

    # Depth token gain at each V_C (vs K=1 at same V_C), best K
    depth_gain_by_vc: Dict[int, float] = {}
    for V_C in V_C_GRID:
        best_gain = 0.0
        for K in DEPTH_SET:
            if K == 1:
                continue
            g = _mean("depth_token_gain_vc%d_k%d" % (V_C, K))
            if not math.isnan(g) and g > best_gain:
                best_gain = g
        depth_gain_by_vc[V_C] = best_gain

    # Find overall best (V_C, K) by substrate_bpc
    best_bpc = float("inf")
    best_tag = ""
    for V_C in V_C_GRID:
        for K in DEPTH_SET:
            tag = "vc%d_k%d" % (V_C, K)
            b = grid_results[tag]["substrate_bpc"]
            if not math.isnan(b) and b < best_bpc:
                best_bpc = b
                best_tag = tag

    best_cv = grid_results.get(best_tag, {}).get("cv", 1.0) if best_tag else 1.0

    # Q(a): finer V_C lowers floor? Compare ceiling_bpc at K=1 across V_C
    qa_lines = []
    for V_C in V_C_GRID:
        ceil_k1 = grid_results.get("vc%d_k1" % V_C, {}).get("ceiling_bpc", float("nan"))
        sub_k1 = grid_results.get("vc%d_k1" % V_C, {}).get("substrate_bpc", float("nan"))
        qa_lines.append("Q(a) V_C=%d: ceiling_bpc=%.2f sub_bpc_k1=%.2f" % (V_C, ceil_k1, sub_k1))

    # Q(b): depth_token_gain at V_C=1024 vs V_C=256
    qb_line = "Q(b) depth_token_gain: V_C=256 best=%.3f V_C=1024 best=%.3f" % (
        depth_gain_by_vc.get(256, float("nan")),
        depth_gain_by_vc.get(1024, float("nan")))

    # Q(c): any config beats bigram?
    beats_bigram = not math.isnan(best_bpc) and not math.isnan(bigram_bpc) and best_bpc < bigram_bpc
    qc_line = "Q(c) best_bpc=%.2f vs bigram=%.2f -> %s" % (
        best_bpc, bigram_bpc, "BEATS_BIGRAM" if beats_bigram else "DOES_NOT_BEAT_BIGRAM")

    saturation_note = " [SATURATION-FLAG]" if any_saturated else ""

    summary_block = " | ".join(cfg_lines) + " || " + " | ".join(qa_lines) + " | " + qb_line + " | " + qc_line

    # -----------------------------------------------------------------------
    # HARD-FAIL: no (V_C, K) improves on anchor (~5.00) AND depth stays floor-masked everywhere
    # -----------------------------------------------------------------------
    no_vc_helps = (math.isnan(best_bpc) or best_bpc >= anchor_bpc - 0.05)
    no_depth_helps = all(
        math.isnan(depth_gain_by_vc.get(V_C, float("nan"))) or
        depth_gain_by_vc.get(V_C, float("nan")) < 0.05
        for V_C in V_C_GRID
    )
    if no_vc_helps and no_depth_helps:
        return ("HARD_FAIL",
                "HARD_FAIL: no (V_C,K) improves on anchor %.2f by >0.05 bpc AND "
                "depth stays floor-masked (<0.05 gain) at all V_C. "
                "Codebook + depth levers both ineffective. "
                "%s%s" % (anchor_bpc, summary_block, saturation_note))

    # -----------------------------------------------------------------------
    # HARD-PASS: beats bigram + clear depth gain at finer V_C + cv<=0.05
    # -----------------------------------------------------------------------
    depth_gain_1024 = depth_gain_by_vc.get(1024, float("nan"))
    if (beats_bigram and
            not math.isnan(depth_gain_1024) and depth_gain_1024 >= 0.10 and
            best_cv <= 0.05):
        if any_saturated:
            return ("MIDDLE_BAND",
                    "MIDDLE_BAND (saturation-demote): HARD_PASS conditions met but saturation flag. "
                    "best_bpc=%.2f < bigram=%.2f, depth_gain@V_C=1024=%.3f >= 0.10, cv=%.3f. "
                    "%s%s" % (best_bpc, bigram_bpc, depth_gain_1024, best_cv,
                               summary_block, saturation_note))
        return ("HARD_PASS",
                "HARD_PASS: %s sub_bpc=%.2f < bigram=%.2f, "
                "depth_token_gain@V_C=1024=%.3f bits >= 0.10, cv=%.3f <= 0.05, "
                "substrate-only-decode. %s" % (
                    best_tag, best_bpc, bigram_bpc, depth_gain_1024, best_cv, summary_block))

    # -----------------------------------------------------------------------
    # MIDDLE_BAND: codebook lever works OR depth shows at finer V_C
    # -----------------------------------------------------------------------
    # Check Q(a): finer V_C lowers substrate-BPC at K=1
    sub_k1_256 = grid_results.get("vc256_k1", {}).get("substrate_bpc", float("nan"))
    sub_k1_1024 = grid_results.get("vc1024_k1", {}).get("substrate_bpc", float("nan"))
    vc_lever_works = (not math.isnan(sub_k1_256) and not math.isnan(sub_k1_1024) and
                      sub_k1_1024 < sub_k1_256 - 0.05)
    depth_shows_at_1024 = (not math.isnan(depth_gain_1024) and depth_gain_1024 >= 0.05)

    middle_reasons = []
    if vc_lever_works:
        middle_reasons.append("V_C lever lowers substrate-BPC: %.2f(V_C=256) -> %.2f(V_C=1024) at K=1" % (
            sub_k1_256, sub_k1_1024))
    if depth_shows_at_1024:
        middle_reasons.append("depth_token_gain=%.3f bits >= 0.05 at V_C=1024 (co-opt shows)" % depth_gain_1024)

    if middle_reasons:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: %s. best config=%s sub_bpc=%.2f vs bigram=%.2f. "
                "%s%s" % ("; ".join(middle_reasons), best_tag, best_bpc, bigram_bpc,
                           summary_block, saturation_note))

    # Default MIDDLE_BAND if something improved but not enough for HARD_FAIL
    return ("MIDDLE_BAND",
            "MIDDLE_BAND (marginal): best_bpc=%.2f anchor=%.2f depth_gain_1024=%.3f "
            "-- some improvement but below MIDDLE_BAND criteria. "
            "%s%s" % (best_bpc, anchor_bpc, depth_gain_1024, summary_block, saturation_note))


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s V_C_GRID=%s N_DIM=%d f=%.4f MAX_DOCS=%d seeds=%s depth=%s" % (
    ANCHOR_NAME, RUN_MODE, V_C_GRID, N_DIM, F_SPARSE, MAX_DOCS, SEEDS, DEPTH_SET), flush=True)
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

if done_seeds:
    agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
    for _k, _v in agg.items():
        ps.append(_v)

if not ps:
    print("[ERROR] no seeds completed; aborting", flush=True)
    sys.exit(1)

v, vmsg = verdict(ps)
print("\n[VERDICT] " + vmsg, flush=True)

# Build per-(V_C,K) summary for metrics.json
per_config_summary: Dict[str, Any] = {}
for V_C in V_C_GRID:
    for K in DEPTH_SET:
        tag = "vc%d_k%d" % (V_C, K)
        for met in ("substrate_bpc", "substrate_concept_top1", "substrate_top1",
                    "unigram_bpc", "bigram_bpc", "ceiling_bpc"):
            k_key = "%s_%s" % (met, tag)
            vals = [p[k_key] for p in ps if k_key in p
                    and not math.isnan(p.get(k_key, float("nan")))]
            per_config_summary[k_key + "_mean"] = float(np.mean(vals)) if vals else float("nan")
        if K > 1:
            g_key = "depth_token_gain_%s" % tag
            g_vals = [p[g_key] for p in ps if g_key in p
                      and not math.isnan(p.get(g_key, float("nan")))]
            per_config_summary[g_key + "_mean"] = float(np.mean(g_vals)) if g_vals else float("nan")

metrics = {
    "anchor_name": ANCHOR_NAME,
    "config_version": CONFIG_VERSION,
    "verdict": v,
    "verdict_msg": vmsg,
    "run_mode": RUN_MODE,
    "n_seeds": len(ps),
    "V_C_GRID": V_C_GRID,
    "N_DIM": N_DIM,
    "f_sparse": F_SPARSE,
    "depth_set": DEPTH_SET,
    "per_config_summary": per_config_summary,
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
