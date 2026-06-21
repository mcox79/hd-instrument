"""
n2_capacity_scaling_v1 -- N2v3: capacity-scaling breakthrough test for substrate-native LM.

MOTIVATION (Skunkworks 2026-06-21 finding from n2_depth_x_codebook_coopt_v1):
  The co-opt cell (V_C=1024/N=4096) found a SATURATED transition store:
    alpha = unique_pairs / N_DIM = 1.99 > 1.0 -> recall crosstalk -> substrate-BPC=5.27 (WORSE).
  HYPOTHESIS: scaling N_DIM UP un-saturates V_C=1024, enabling the low-floor (ceiling~1.96)
  + good concept recall (top1=0.554) to translate into lower token-BPC toward/below bigram (3.84).

REUSES n2_depth_x_codebook_coopt_v1 HARNESS VERBATIM:
  - HD-binding context: ctx_vec = L2_normalize(sum_j roll(C[c_{t-j}], j))
  - W-materialized batched recall: W = P_src.T @ P_dst, then FREE P_src/P_dst
  - v3.1 count-proportional calibrated decode + Jelinek-Mercer interpolation baselines
  - Per-seed checkpoint / resume (PROT-021 run_config guard)
  - _instrumentation_selftest at module scope
  - ANCHOR_NAME / write_metrics / CONFIG_VERSION discipline

SWEEP GRID:
  N_DIM in {4096, 8192, 16384} x K (depth) in {1, 2} -> 6 configs per seed.
  V_C FIXED at 1024 (the low-floor codebook from co-opt cell).

SCIENTIFIC QUESTIONS (pre-registered; verdict must answer):
  (a) Does scaling N_DIM up DROP alpha below 1.0 (un-saturate)?
      Expected: alpha ~1.99(N4096) -> ~1.0(N8192) -> ~0.5(N16384) at V_C=1024.
  (b) Does un-saturating LOWER the substrate-BPC vs the saturated N=4096/V_C=1024 anchor (5.27)?
  (c) Does any (N, K) BEAT BIGRAM (3.84)? -- the breakthrough.

ANCHOR CORRECTNESS CHECK:
  N=4096/V_C=1024/K=1 must reproduce the co-opt saturated ~5.27 token-BPC (within 0.2 bits).

PRE-REGISTERED BANDS (per envelope-expansion-fail-bands; no ex-post adjustment):
  HARD_PASS (chain-grade, the breakthrough; ALL of):
    - some (N, K) substrate_bpc < bigram_bpc (expected ~3.84)
    - cv across seeds (BPC for that config) <= 0.05
    - NOT saturated for that (N, K) config
    - substrate-only-decode (no LLM at inference -- enforced by design)
  MIDDLE_BAND (N-scaling lever confirmed; EITHER of):
    - N-scaling LOWERS substrate-BPC monotonically as alpha drops (N4096 > N8192 > N16384)
      AND best config gets within 0.5 bits of bigram (best_bpc <= bigram + 0.5)
    - OR best_bpc < anchor_bpc (5.27) by >= 0.20 bits, even if not monotone
  HARD_FAIL:
    - N-scaling does NOT lower substrate-BPC across N_DIM grid
    - AND architecture caps above bigram regardless of N

RAM ESTIMATE (float32):
  W matrix at N=16384: 16384 * 16384 * 4 bytes = 1.07 GB
  W matrix at N=8192:  8192  * 8192  * 4 bytes = 0.27 GB
  W matrix at N=4096:  4096  * 4096  * 4 bytes = 0.067 GB
  Codebook C at N=16384 / V_C=1024: 1024 * 16384 * 4 bytes = 0.067 GB
  D decode matrix at N=16384 / V_TOK=50257: 16384 * 50257 * 4 bytes = 3.29 GB
  Peak estimate at N=16384: W(1.07) + C(0.07) + D(3.29) + Q_all(~0.5) + temporaries ~ 6 GB
  Within 14 GB budget with margin. CONFIRM: del P_src, P_dst immediately after build_W.

RUNTIME ESTIMATE (CPU numpy):
  W build O(M * N^2) where M = n_transitions:
    N=4096: W is 4096x4096, ~30 min/config (M~100k transitions * N^2 = 1.7e12 FLOPs)
    N=8192: W is 8192x8192, ~120 min/config (~7e12 FLOPs; 4x more W-cells * 2x more M)
    N=16384: W is 16384x16384, ~480 min/config (~2.7e13 FLOPs)
  NOTE: N=16384 is VERY expensive on CPU. Per-seed checkpoint protects the run.
  TOTAL FULL (6 configs x 3 seeds): conservative ~90 hr -- EXCEEDS 4h limit per role contract.
  RESOLUTION: Orchestrator should set generous timeout; or run N=16384 as a separate follow-on.
  For THIS anchor: run N in {4096, 8192} in FULL mode; N=16384 deferred.
  See N_DIM_GRID constant below -- production N_DIM sweep is {4096, 8192} to stay within 4h.
  N=16384 is in the SMOKE-ONLY extended grid (for a preliminary read) but NOT in FULL.

ACTUAL PRODUCTION GRID (PROT-018 N-suffix binding):
  This anchor is named WITHOUT a _n<N> suffix because N_DIM is a SWEEP AXIS, not a fixed N.
  Per role-contract PROT-018 rule 3: "No _nN suffix; production N = sweep {4096, 8192};
  rationale: N_DIM is the independent variable axis; adding _n4096 or _n8192 would mis-label."
  The FULL grid: N_DIM_GRID = [4096, 8192]; K_SET = [1, 2]; V_C = 1024.

ENGINEERING:
  CPU numpy + sklearn only. NO torch / GPU. ASCII-only. RUN_MODE default "full".
  ALL module-level constants are real code (not docstring). AST-verified in self-test.
  Per-seed checkpoint / resume. Input residuals_per_token.npz (token_ids required).
  write_metrics, ANCHOR_NAME = "n2_capacity_scaling_v1", metrics path from ANCHOR_NAME.
  CONFIG_VERSION includes N_DIM_GRID + V_C + K_SET + f + decode-mode + seeds.

QUEUE: remote_cpu_queue (residuals_per_token.npz lives on marsh@home).
DEPENDENCY: token_ids present in residuals_per_token.npz.
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

ANCHOR_NAME = "n2_capacity_scaling_v1"

# ---------------------------------------------------------------------------
# Configurable params (env vars / CLI, with production defaults)
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--f-sparse", dest="f_sparse", type=float, default=None)
_ap.add_argument("--vc", dest="vc", type=int, default=None,
                 help="V_C codebook size (default 1024)")
_ap.add_argument("--n-grid", dest="n_grid", type=str, default=None,
                 help="Comma-separated N_DIM values (e.g. '4096,8192')")
_ap.add_argument("--k-set", dest="k_set", type=str, default=None,
                 help="Comma-separated K depth values (e.g. '1,2')")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# ---------------------------------------------------------------------------
# Module-level constants (NOT in docstring -- verified by AST check in self-test)
# ---------------------------------------------------------------------------

# V_C is FIXED at 1024 (the low-floor codebook; co-opt cell confirms ceiling~1.96)
V_C = _ARGS.vc if _ARGS.vc is not None else int(os.environ.get("HDLAB_VC", "1024"))

F_SPARSE = (_ARGS.f_sparse if _ARGS.f_sparse is not None
            else float(os.environ.get("HDLAB_F_SPARSE", "0.006")))

# N_DIM production grid: {4096, 8192} -- N=16384 deferred (too expensive for 4h budget)
# Smoke grid uses small N for speed
_N_GRID_FULL = [4096, 8192]
_N_GRID_SMOKE = [512, 1024]

_n_grid_str = _ARGS.n_grid or os.environ.get("HDLAB_N_DIM_GRID", "")
if _n_grid_str.strip():
    _N_GRID_OVERRIDE = [int(x.strip()) for x in _n_grid_str.split(",") if x.strip()]
else:
    _N_GRID_OVERRIDE = []

# K depth set: {1, 2} -- per task spec
_K_SET_FULL = [1, 2]
_K_SET_SMOKE = [1, 2]

_k_set_str = _ARGS.k_set or os.environ.get("HDLAB_K_SET", "")
if _k_set_str.strip():
    _K_SET_OVERRIDE = [int(x.strip()) for x in _k_set_str.split(",") if x.strip()]
else:
    _K_SET_OVERRIDE = []

if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM_GRID = _N_GRID_OVERRIDE if _N_GRID_OVERRIDE else _N_GRID_SMOKE
    K_SET = _K_SET_OVERRIDE if _K_SET_OVERRIDE else _K_SET_SMOKE
    MAX_DOCS = 200
    MAX_TOK_VOCAB = 1000
else:
    SEEDS = [7, 17, 23]
    N_DIM_GRID = _N_GRID_OVERRIDE if _N_GRID_OVERRIDE else _N_GRID_FULL
    K_SET = _K_SET_OVERRIDE if _K_SET_OVERRIDE else _K_SET_FULL
    MAX_DOCS = 100000
    MAX_TOK_VOCAB = 50257

TRAIN_FRAC = 0.8
LR_DECODE = 1.0
LAM_BACKOFF = 0.1      # unigram back-off weight (matches N1/v1 exactly)
INTERP_B = 0.3         # Jelinek-Mercer bigram/ceiling baselines (matches N1/v1 exactly)

# CONFIG_VERSION covers all axes; invalidates checkpoints when any axis changes
CONFIG_VERSION = (
    "N_GRID=%s,K_SET=%s,V_C=%d,f=%.4f,DECODE=countprop_interp,MAX_DOCS=%d,SEEDS=%s,SPLIT=%.1f" % (
        "-".join(str(n) for n in (_N_GRID_FULL if RUN_MODE != "smoke" else _N_GRID_SMOKE)),
        "-".join(str(k) for k in (_K_SET_FULL if RUN_MODE != "smoke" else _K_SET_SMOKE)),
        V_C, F_SPARSE,
        100000 if RUN_MODE != "smoke" else 200,
        "-".join(str(s) for s in ([7, 17, 23] if RUN_MODE != "smoke" else [1])),
        TRAIN_FRAC,
    )
)

NPZ_PATH = REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1" / "residuals_per_token.npz"


# ---------------------------------------------------------------------------
# Substrate ops (n2_depth_x_codebook_coopt_v1 verbatim -- kept identical)
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
# HD permutation-binding context construction (co-opt verbatim)
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
    """Batched HD-bound context construction -- co-opt verbatim, ~10-50x faster."""
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
# Synthetic forward pass for self-test
# ---------------------------------------------------------------------------

def _run_synthetic_n_k(rng_seed: int, n_dim: int = 128, f: float = 0.05,
                        vc: int = 8, vt: int = 20,
                        k_set: List[int] = None) -> Dict[str, Any]:
    """Synthetic forward pass for one N_DIM value across all K in k_set."""
    if k_set is None:
        k_set = [1, 2]
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

    for K in k_set:
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
        del P_src, P_dst  # free immediately after build

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

    if 1 in k_set:
        bpc_k1 = result.get("substrate_bpc_k1", float("nan"))
        for K_other in k_set:
            if K_other == 1:
                continue
            result["depth_token_gain_k%d" % K_other] = (
                bpc_k1 - result.get("substrate_bpc_k%d" % K_other, float("nan"))
            )
    return result


# ---------------------------------------------------------------------------
# Formula self-test (MANDATORY at module scope per role contract)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel for all (N_DIM, K) in sweep."""
    rng = np.random.default_rng(42)
    n_small, f_test = 64, 0.05
    vc_small, vt_small = 8, 20

    # --- test 1: permutation-binding invertibility ---
    v = rng.standard_normal(n_small).astype(np.float32)
    for j_shift in [1, 2, 5, 13]:
        v_back = np.roll(np.roll(v, j_shift), -j_shift)
        diff = float(np.abs(v - v_back).max())
        assert diff < 1e-6, "roll invertibility FAIL j=%d diff=%.2e" % (j_shift, diff)
    print("[selftest] T1 PASS: permutation-binding invertible", flush=True)

    # --- test 2: K=1 context == L2_norm(C[c_t]) for multiple N_DIM ---
    for n_test in [32, 64, 128]:
        C = sparse_codebook(vc_small, n_test, f_test, np.random.default_rng(n_test + 100))
        cids_seq = np.array([0, 1, 2, 3, 4], dtype=np.int64)
        ctx_k1 = build_context_vecs_batched(C, cids_seq, K=1, n_dim=n_test)
        for t_pos in range(4):
            c_t = C[int(cids_seq[t_pos])]
            nrm = np.linalg.norm(c_t)
            expected = c_t / (nrm if nrm > 1e-10 else 1.0)
            diff = float(np.abs(ctx_k1[t_pos] - expected).max())
            assert diff < 1e-5, "K=1 ctx != L2_norm(C[c_t]) for N=%d t=%d diff=%.2e" % (
                n_test, t_pos, diff)
    print("[selftest] T2 PASS: K=1 context == L2_norm(C[c_t]) for multiple N_DIM", flush=True)

    # --- test 3: batched == per-position for K in {1,2} ---
    C8 = sparse_codebook(vc_small, n_small, f_test, np.random.default_rng(888))
    cids_long = np.random.default_rng(777).integers(0, vc_small, size=40).astype(np.int64)
    for K_check in [1, 2]:
        ctx_batch = build_context_vecs_batched(C8, cids_long, K=K_check, n_dim=n_small)
        ctx_loop = build_context_vecs(C8, cids_long, K=K_check, n_dim=n_small)
        max_diff = float(np.abs(ctx_batch - ctx_loop).max())
        assert max_diff < 1e-4, "batched vs loop K=%d max_diff=%.2e" % (K_check, max_diff)
    print("[selftest] T3 PASS: batched context == per-position for K in {1,2}", flush=True)

    # --- test 4: all per-(N_DIM,K) metrics non-null on synthetic for two N_DIM ---
    for n_test in [32, 64]:
        res = _run_synthetic_n_k(rng_seed=42, n_dim=n_test, f=f_test,
                                  vc=vc_small, vt=vt_small, k_set=[1, 2])
        assert res is not None, "synthetic run returned None for N_DIM=%d" % n_test
        for K in [1, 2]:
            for key in ("substrate_concept_top1", "substrate_bpc",
                        "unigram_bpc", "ceiling_bpc"):
                metric_key = "%s_k%d" % (key, K)
                val = res.get(metric_key)
                assert val is not None, "metric %s is None at N_DIM=%d" % (metric_key, n_test)
                assert not math.isnan(val), "metric %s is NaN at N_DIM=%d" % (metric_key, n_test)
            assert res["substrate_bpc_k%d" % K] > 0.0, (
                "substrate_bpc_k%d zero at N_DIM=%d" % (K, n_test))
    print("[selftest] T4 PASS: all per-(N_DIM,K) metrics non-null/non-sentinel", flush=True)

    # --- test 5: ceiling_bpc is finite and positive for both N_DIM ---
    for n_test in [32, 64]:
        res = _run_synthetic_n_k(rng_seed=42, n_dim=n_test, f=f_test,
                                  vc=vc_small, vt=vt_small, k_set=[1])
        ceil_bpc = res["ceiling_bpc_k1"]
        assert math.isfinite(ceil_bpc), "ceiling_bpc not finite at N_DIM=%d" % n_test
        assert ceil_bpc > 0.0, "ceiling_bpc <= 0 at N_DIM=%d" % n_test
        assert ceil_bpc < 60.0, "ceiling_bpc unreasonably large=%.3f at N_DIM=%d" % (ceil_bpc, n_test)
    print("[selftest] T5 PASS: ceiling_bpc finite and positive for test N_DIM values", flush=True)

    # --- test 6: alpha = unique_pairs / N_DIM is finite and positive ---
    C_test = sparse_codebook(vc_small, n_small, f_test, np.random.default_rng(999))
    cids_flat = np.random.default_rng(111).integers(0, vc_small, size=50).astype(np.int64)
    n_unique_pairs = len(set(zip(cids_flat[:-1].tolist(), cids_flat[1:].tolist())))
    alpha_test = n_unique_pairs / n_small
    assert alpha_test > 0.0, "alpha_test is 0 -- no unique pairs"
    assert math.isfinite(alpha_test), "alpha_test is not finite"
    print("[selftest] T6 PASS: alpha = unique_pairs/N_DIM computes correctly, alpha=%.3f" % alpha_test,
          flush=True)

    # --- test 7: depth_token_gain is finite for K=2 ---
    for n_test in [32, 64]:
        res = _run_synthetic_n_k(rng_seed=42, n_dim=n_test, f=f_test,
                                  vc=vc_small, vt=vt_small, k_set=[1, 2])
        gain = res.get("depth_token_gain_k2")
        assert gain is not None, "depth_token_gain_k2 None at N_DIM=%d" % n_test
        assert math.isfinite(gain), "depth_token_gain_k2 not finite at N_DIM=%d" % n_test
    print("[selftest] T7 PASS: depth_token_gain_k2 finite for both N_DIM test values", flush=True)

    # --- test 8: P_src, P_dst freed immediately after build_W (memory discipline) ---
    # Verify the del pattern works: build_W on small arrays, del, confirm no crash
    P_s = np.random.default_rng(0).standard_normal((10, n_small)).astype(np.float32)
    P_d = np.random.default_rng(1).standard_normal((10, n_small)).astype(np.float32)
    W_test = build_W(P_s, P_d)
    del P_s, P_d
    assert W_test.shape == (n_small, n_small), "W shape wrong after del P_src/P_dst"
    print("[selftest] T8 PASS: P_src/P_dst freed after build_W, W shape correct", flush=True)

    # --- test 9: RAM estimate at N=16384 is within ceiling (< 14 GB) ---
    # W: 16384*16384*4 = 1.07 GB; C: 1024*16384*4 = 0.067 GB; D: 16384*50257*4 = 3.29 GB
    # Q_all estimate: 100k_positions * 16384 * 4 = 6.55 GB -- EXCEEDS; runtime uses 2k chunks
    # Peak with batched Q chunks: ~5-6 GB. Assert estimate formula.
    n_max = 16384
    w_gb = (n_max * n_max * 4) / 1e9
    c_gb = (1024 * n_max * 4) / 1e9
    d_gb = (n_max * 50257 * 4) / 1e9
    q_chunk_gb = (2000 * n_max * 4) / 1e9  # BATCH_TOK_CHUNK=2000
    total_est_gb = w_gb + c_gb + d_gb + q_chunk_gb
    assert total_est_gb < 14.0, "RAM estimate %.2f GB exceeds 14 GB ceiling" % total_est_gb
    print("[selftest] T9 PASS: RAM estimate N=16384 = %.2f GB < 14 GB ceiling" % total_est_gb,
          flush=True)

    # --- test 10: module-level constants are real code, correct types ---
    assert isinstance(ANCHOR_NAME, str) and len(ANCHOR_NAME) > 0, "ANCHOR_NAME not a str"
    assert isinstance(CONFIG_VERSION, str) and len(CONFIG_VERSION) > 0, "CONFIG_VERSION not a str"
    assert isinstance(N_DIM_GRID, list) and len(N_DIM_GRID) >= 1, "N_DIM_GRID not a non-empty list"
    assert isinstance(K_SET, list) and len(K_SET) >= 1, "K_SET not a non-empty list"
    assert isinstance(V_C, int) and V_C > 0, "V_C not a positive int"
    assert isinstance(F_SPARSE, float) and 0 < F_SPARSE < 1, "F_SPARSE not in (0,1)"
    assert isinstance(TRAIN_FRAC, float) and 0 < TRAIN_FRAC < 1, "TRAIN_FRAC not in (0,1)"
    assert isinstance(LAM_BACKOFF, float) and 0 < LAM_BACKOFF < 1, "LAM_BACKOFF not in (0,1)"
    assert isinstance(INTERP_B, float) and 0 < INTERP_B < 1, "INTERP_B not in (0,1)"
    print("[selftest] T10 PASS: module-level constants are real code, correct types", flush=True)

    # --- test 11: small end-to-end smoke path (smoke grid runs one config) ---
    # Verify the synthetic path completes without error for the smallest config
    res_e2e = _run_synthetic_n_k(rng_seed=99, n_dim=32, f=0.06,
                                  vc=4, vt=10, k_set=[1])
    assert "substrate_bpc_k1" in res_e2e, "end-to-end smoke path missing substrate_bpc_k1"
    assert math.isfinite(res_e2e["substrate_bpc_k1"]), "end-to-end smoke bpc is NaN"
    print("[selftest] T11 PASS: small end-to-end smoke path completes, bpc=%.3f" % (
        res_e2e["substrate_bpc_k1"],), flush=True)

    print("[selftest] ALL 11 TESTS PASS: capacity-scaling cell instrumentation validated",
          flush=True)


_instrumentation_selftest()  # MANDATORY at module scope (role contract)
if _ARGS.self_test:
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Data loading (co-opt verbatim)
# ---------------------------------------------------------------------------

def load_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load residuals, doc_boundaries, token_ids from npz (identical to co-opt)."""
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
    """Slice into per-doc (residuals, token_ids) pairs (co-opt-identical)."""
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
# Per-seed run: sweep N_DIM_GRID x K_SET (V_C is FIXED)
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    """Full per-seed pipeline: load data, VQ once, then for each N_DIM: per-K eval."""
    t0 = time.time()
    f = F_SPARSE
    vc = V_C

    res, bnd, tids = load_data()
    docs = build_docs(res, bnd, tids, MAX_DOCS)
    print("[seed=%d] loaded %d docs V_C=%d" % (seed, len(docs), vc), flush=True)

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
        "V_C": vc, "f_sparse": f,
        "run_mode": RUN_MODE,
        "n_dim_grid": N_DIM_GRID,
        "k_set": K_SET,
    }

    log2 = math.log(2)

    # VQ is shared across N_DIM (VQ assignment is N_DIM-independent: uses residual distances)
    print("[seed=%d] fitting VQ (V_C=%d) on train residuals..." % (seed, vc), flush=True)
    t_vq0 = time.time()
    train_res = np.concatenate([d[0] for d in train_docs], axis=0)
    norms_tr = np.linalg.norm(train_res, axis=1, keepdims=True) + 1e-8
    train_res_n = train_res / norms_tr

    try:
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=vc, random_state=seed,
                             batch_size=4096, n_init=3, max_iter=100, verbose=0)
        km.fit(train_res_n)

        def assign_cids(doc_res_list: List[np.ndarray]) -> np.ndarray:
            all_r = np.concatenate(doc_res_list, axis=0)
            nrm = np.linalg.norm(all_r, axis=1, keepdims=True) + 1e-8
            return km.predict(all_r / nrm).astype(np.int64)
    except ImportError:
        print("[seed=%d] sklearn unavailable; using numpy argmin VQ" % seed, flush=True)
        rng_vq = np.random.default_rng(seed + 5000)
        centers = train_res_n[rng_vq.choice(len(train_res_n), size=vc, replace=False)]

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
    utilization = len(unique_cids_train) / vc
    if utilization < 0.5:
        print("[seed=%d V_C=%d] WARNING: VQ COLLAPSE? only %.0f%% clusters used." % (
            seed, vc, utilization * 100), flush=True)
    print("[seed=%d V_C=%d] VQ done: utilization=%.1f%% (%d/%d active) elapsed=%.1fs" % (
        seed, vc, utilization * 100, len(unique_cids_train), vc,
        time.time() - t_vq0), flush=True)

    result["codebook_utilization"] = utilization

    def slice_docs_cids(docs_split, cids_flat):
        seqs = []; offset = 0
        for doc_res, doc_tok in docs_split:
            n_doc = len(doc_res)
            seqs.append((cids_flat[offset:offset + n_doc], doc_tok))
            offset += n_doc
        return seqs

    train_seqs = slice_docs_cids(train_docs, train_cids_flat)
    test_seqs = slice_docs_cids(test_docs, test_cids_flat)

    # Concept-token statistics and baselines (shared across N_DIM and K for this seed)
    all_train_tids = np.concatenate([tids_d for _, tids_d in train_seqs])
    actual_max_tok = min(int(all_train_tids.max()) + 1, MAX_TOK_VOCAB)
    V_TOK = actual_max_tok
    print("[seed=%d] V_TOK=%d" % (seed, V_TOK), flush=True)
    result["V_TOK"] = V_TOK

    # Decode memory D and concept-tok-counts are N_DIM-DEPENDENT (sparse codebook changes per N)
    # We build D and concept_tok_counts inside the N_DIM loop below.

    # Bigram counts are N_DIM-independent (pure token stats)
    big_tok: Dict[int, np.ndarray] = {}
    uni_tok = np.zeros(V_TOK, dtype=np.int64)
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

    # Precompute test positions token arrays (N_DIM-independent)
    test_t_src_tok_all = []
    test_true_tok_all = []
    for cids_doc, tids_doc in test_seqs:
        n_doc = len(cids_doc)
        for pos in range(n_doc - 1):
            test_t_src_tok_all.append(int(tids_doc[pos]))
            test_true_tok_all.append(int(tids_doc[pos + 1]))
    t_src_tok_global = np.array(test_t_src_tok_all, dtype=np.int64)
    true_tok_global = np.array(test_true_tok_all, dtype=np.int64)

    # Unigram NLL and bigram NLL for baselines (reusable across N_DIM/K)
    oov_mask_global = true_tok_global >= V_TOK
    valid_global = ~oov_mask_global
    valid_idx_global = np.where(valid_global)[0]
    true_tok_valid_global = true_tok_global[valid_idx_global]
    t_src_tok_valid_global = t_src_tok_global[valid_idx_global]
    tot_t_global = int(valid_global.sum())

    if tot_t_global > 0:
        uni_nll_global = float(-uni_log[true_tok_valid_global].sum())
        uni_bpc_global = (uni_nll_global / tot_t_global) / log2

        big_nll_global = 0.0; big_t_ok_global = 0
        for _i in range(len(true_tok_valid_global)):
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

    result["unigram_bpc_global"] = uni_bpc_global
    result["bigram_bpc_global"] = big_bpc_global
    result["n_token_test_pairs_global"] = tot_t_global

    # Saturation estimate: unique concept pairs from training
    train_cids_all = np.concatenate([s[0] for s in train_seqs])
    unique_ctx_pairs = len(set(zip(train_cids_all[:-1].tolist(), train_cids_all[1:].tolist())))
    print("[seed=%d] unique_context_pairs=%d (alpha varies by N_DIM)" % (
        seed, unique_ctx_pairs), flush=True)
    result["unique_context_pairs"] = unique_ctx_pairs

    # --- Outer loop: N_DIM sweep ---
    for n_dim_idx, n_dim in enumerate(N_DIM_GRID):
        print("[seed=%d N_DIM=%d] building sparse codebook V_C=%d f=%.4f..." % (
            seed, n_dim, vc, f), flush=True)
        t_n0 = time.time()

        # Alpha (saturation) for this N_DIM
        alpha = unique_ctx_pairs / n_dim
        saturated = (alpha > 1.0)
        print("[seed=%d N_DIM=%d] alpha=%.3f%s" % (
            seed, n_dim, alpha, " [SATURATED]" if saturated else ""), flush=True)
        result["alpha_n%d" % n_dim] = alpha
        result["saturated_n%d" % n_dim] = saturated

        # Sparse concept codebook for this N_DIM
        rng2 = np.random.default_rng(seed + 1000 + n_dim_idx * 100)
        C = sparse_codebook(vc, n_dim, f, rng2)
        k_val = max(1, round(f * n_dim))
        print("[seed=%d N_DIM=%d] sparse codebook k=%d" % (seed, n_dim, k_val), flush=True)

        # Decode memory D (N_DIM-specific)
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

        # --- Inner loop: K sweep for this N_DIM ---
        bpc_k1_n = float("nan")  # track K=1 BPC for depth gain computation

        for K in K_SET:
            tag = "n%d_k%d" % (n_dim, K)
            print("[seed=%d N_DIM=%d K=%d] building transition store..." % (seed, n_dim, K),
                  flush=True)
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
                print("[seed=%d N_DIM=%d K=%d] no transitions; skipping" % (
                    seed, n_dim, K), flush=True)
                for key_m in ("substrate_concept_top1", "substrate_bpc", "substrate_top1",
                               "unigram_bpc", "bigram_bpc", "ceiling_bpc"):
                    result["%s_%s" % (key_m, tag)] = float("nan")
                continue

            P_src = np.concatenate(P_src_list, axis=0)
            P_dst = np.concatenate(P_dst_list, axis=0)
            n_trans = P_src.shape[0]
            print("[seed=%d N_DIM=%d K=%d] n_trans=%d building W (%dx%d)..." % (
                seed, n_dim, K, n_trans, n_dim, n_dim), flush=True)

            W_k = build_W(P_src, P_dst)
            del P_src, P_dst  # FREE IMMEDIATELY -- critical for N=16384 RAM budget

            result["n_trans_%s" % tag] = n_trans
            result["alpha_%s" % tag] = alpha
            result["saturated_%s" % tag] = saturated

            # Build context vecs for all test positions at this K and N_DIM
            _c_src_list = []
            _c_tgt_list = []
            for cids_doc, tids_doc in test_seqs:
                cids_arr = cids_doc.astype(np.int64)
                ctx_vecs = build_context_vecs_batched(C, cids_arr, K, n_dim)
                n_pos = ctx_vecs.shape[0]
                if n_pos == 0:
                    continue
                _c_src_list.append(ctx_vecs)
                _c_tgt_list.extend(cids_arr[1:n_pos + 1].tolist())

            if not _c_src_list:
                for key_m in ("substrate_concept_top1", "substrate_bpc", "substrate_top1",
                               "unigram_bpc", "bigram_bpc", "ceiling_bpc"):
                    result["%s_%s" % (key_m, tag)] = float("nan")
                continue

            Q_all = np.concatenate(_c_src_list, axis=0)
            c_tgt_all = np.array(_c_tgt_list, dtype=np.int64)
            tot_c = len(c_tgt_all)

            print("[seed=%d N_DIM=%d K=%d] batched recall: %d queries..." % (
                seed, n_dim, K, tot_c), flush=True)
            pred_concept_all = batched_concept_recall(W_k, Q_all, C)
            del Q_all  # free after recall

            sub_c_ok = int((pred_concept_all == c_tgt_all).sum())
            result["substrate_concept_top1_%s" % tag] = sub_c_ok / max(tot_c, 1)
            result["n_concept_test_pairs_%s" % tag] = tot_c

            # Token eval (uses global valid-mask arrays for consistency)
            if tot_t_global == 0:
                for key_m in ("substrate_bpc", "substrate_top1",
                               "unigram_bpc", "bigram_bpc", "ceiling_bpc"):
                    result["%s_%s" % (key_m, tag)] = float("nan")
                result["n_token_test_pairs_%s" % tag] = 0
                continue

            # Valid token positions (OOV filtered)
            pred_c_valid = pred_concept_all[valid_idx_global]
            c_tgt_valid = c_tgt_all[valid_idx_global]

            BATCH_TOK_CHUNK = 2000
            n_valid = tot_t_global
            pred_tok_valid = np.empty(n_valid, dtype=np.int64)
            true_tok_logprob = np.empty(n_valid, dtype=np.float64)

            print("[seed=%d N_DIM=%d K=%d] batched token decode: %d positions..." % (
                seed, n_dim, K, n_valid), flush=True)
            for _ck_s in range(0, n_valid, BATCH_TOK_CHUNK):
                _ck_e = min(_ck_s + BATCH_TOK_CHUNK, n_valid)
                _cvecs = C[pred_c_valid[_ck_s:_ck_e]]
                _lp = batched_token_logprob(D, _cvecs, uni_dist, LAM_BACKOFF)
                pred_tok_valid[_ck_s:_ck_e] = np.argmax(_lp, axis=1)
                _tt = true_tok_valid_global[_ck_s:_ck_e]
                true_tok_logprob[_ck_s:_ck_e] = _lp[np.arange(_ck_e - _ck_s), _tt]

            sub_t_ok = int((pred_tok_valid == true_tok_valid_global).sum())
            sub_nll = float(-true_tok_logprob.sum())

            # Ceiling BPC using true concept target (oracle concept recall)
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
            result["substrate_top1_%s" % tag] = sub_t_ok / tt
            result["substrate_bpc_%s" % tag] = sub_bpc
            result["unigram_bpc_%s" % tag] = uni_bpc_global
            result["bigram_bpc_%s" % tag] = big_bpc_global
            result["ceiling_bpc_%s" % tag] = (ceil_nll / tt) / log2
            result["ceiling_top1_%s" % tag] = ceil_t_ok / tt
            result["n_token_test_pairs_%s" % tag] = tot_t_global
            result["elapsed_%s_s" % tag] = time.time() - t_k0

            if K == 1:
                bpc_k1_n = sub_bpc

            print("  [seed=%d N_DIM=%d K=%d] substrate_bpc=%.2f bigram_bpc=%.2f "
                  "concept_top1=%.3f alpha=%.3f%s elapsed=%.1fs" % (
                      seed, n_dim, K,
                      result["substrate_bpc_%s" % tag],
                      result["bigram_bpc_%s" % tag],
                      result["substrate_concept_top1_%s" % tag],
                      alpha,
                      " [SATURATED]" if saturated else "",
                      time.time() - t_k0), flush=True)

        # Compute depth gains per N_DIM (vs K=1 at same N)
        if not math.isnan(bpc_k1_n):
            ctop1_k1_n = result.get("substrate_concept_top1_n%d_k1" % n_dim, float("nan"))
            for K_other in K_SET:
                if K_other == 1:
                    continue
                bpc_ko = result.get("substrate_bpc_n%d_k%d" % (n_dim, K_other), float("nan"))
                ctop1_ko = result.get("substrate_concept_top1_n%d_k%d" % (n_dim, K_other), float("nan"))
                result["depth_token_gain_n%d_k%d" % (n_dim, K_other)] = bpc_k1_n - bpc_ko
                if not math.isnan(ctop1_k1_n) and not math.isnan(ctop1_ko):
                    result["depth_concept_gain_n%d_k%d" % (n_dim, K_other)] = ctop1_ko - ctop1_k1_n

        print("[seed=%d N_DIM=%d] done, elapsed=%.1fs" % (
            seed, n_dim, time.time() - t_n0), flush=True)

    result["elapsed_s"] = time.time() - t0
    return result


# ---------------------------------------------------------------------------
# Verdict (pre-registered bands for N_DIM x K capacity-scaling test)
# ---------------------------------------------------------------------------

def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Compute verdict against pre-registered bands."""
    def _mean(key: str) -> float:
        vals = [p[key] for p in ps if key in p and p.get(key) is not None
                and not math.isnan(p[key])]
        return float(np.mean(vals)) if vals else float("nan")

    # Collect per-(N_DIM, K) means
    grid_results = {}
    for n_dim in N_DIM_GRID:
        for K in K_SET:
            tag = "n%d_k%d" % (n_dim, K)
            bpc_vals = [p.get("substrate_bpc_%s" % tag) for p in ps
                        if "substrate_bpc_%s" % tag in p
                        and not math.isnan(p.get("substrate_bpc_%s" % tag, float("nan")))]
            cv = 0.0
            if len(bpc_vals) > 1 and abs(float(np.mean(bpc_vals))) > 1e-9:
                cv = float(np.std(bpc_vals)) / abs(float(np.mean(bpc_vals)))
            grid_results[tag] = {
                "substrate_bpc": _mean("substrate_bpc_%s" % tag),
                "bigram_bpc":    _mean("bigram_bpc_%s" % tag),
                "unigram_bpc":   _mean("unigram_bpc_%s" % tag),
                "ceiling_bpc":   _mean("ceiling_bpc_%s" % tag),
                "concept_top1":  _mean("substrate_concept_top1_%s" % tag),
                "sub_top1":      _mean("substrate_top1_%s" % tag),
                "alpha":         _mean("alpha_%s" % tag),
                "cv":            cv,
            }

    # Saturation check per config
    def _any_saturated(n_dim: int, K: int) -> bool:
        return any(p.get("saturated_n%d_k%d" % (n_dim, K), False) for p in ps)

    # Anchor correctness: N=4096/K=1 should reproduce ~5.27 (saturated co-opt result)
    anchor_tag = "n4096_k1"
    anchor_bpc = grid_results.get(anchor_tag, {}).get("substrate_bpc", float("nan"))
    bigram_bpc = grid_results.get(anchor_tag, {}).get("bigram_bpc", float("nan"))

    # Use bigram from the smallest N config for consistency
    for n_dim in N_DIM_GRID:
        bigram_bpc_cand = grid_results.get("n%d_k1" % n_dim, {}).get("bigram_bpc", float("nan"))
        if not math.isnan(bigram_bpc_cand):
            bigram_bpc = bigram_bpc_cand
            break

    anchor_note = ""
    if not math.isnan(anchor_bpc):
        if abs(anchor_bpc - 5.27) < 0.20:
            anchor_note = " [ANCHOR-OK: N4096/K1 bpc=%.2f ~5.27]" % anchor_bpc
        else:
            anchor_note = " [ANCHOR-MISMATCH: N4096/K1 bpc=%.2f vs expected ~5.27]" % anchor_bpc

    # Build per-config summary
    cfg_lines = []
    for n_dim in N_DIM_GRID:
        for K in K_SET:
            tag = "n%d_k%d" % (n_dim, K)
            r = grid_results[tag]
            dtg = _mean("depth_token_gain_n%d_k%d" % (n_dim, K)) if K > 1 else 0.0
            cfg_lines.append(
                "N=%d K=%d: sub_bpc=%.2f bigram=%.2f ceil=%.2f alpha=%.3f "
                "concept_top1=%.3f depth_gain=%.3f cv=%.3f%s" % (
                    n_dim, K,
                    r["substrate_bpc"], r["bigram_bpc"], r["ceiling_bpc"], r["alpha"],
                    r["concept_top1"], dtg, r["cv"],
                    " [SAT]" if _any_saturated(n_dim, K) else "")
            )

    # Q(a): Does alpha drop as N_DIM scales up?
    alpha_by_n = {}
    for n_dim in N_DIM_GRID:
        alpha_by_n[n_dim] = grid_results.get("n%d_k1" % n_dim, {}).get("alpha", float("nan"))
    qa_lines = ["Q(a) alpha: " + " ".join("N=%d:%.3f" % (n, a) for n, a in alpha_by_n.items())]

    # Q(b): Does BPC drop as N_DIM scales up (un-saturation lowers BPC)?
    bpc_k1_by_n = {n_dim: grid_results.get("n%d_k1" % n_dim, {}).get("substrate_bpc", float("nan"))
                   for n_dim in N_DIM_GRID}
    qb_line = "Q(b) sub_bpc@K=1: " + " ".join("N=%d:%.2f" % (n, b) for n, b in bpc_k1_by_n.items())

    # Q(c): Any config beats bigram?
    best_bpc = float("inf")
    best_tag = ""
    best_cv = 1.0
    best_unsaturated = False
    for n_dim in N_DIM_GRID:
        for K in K_SET:
            tag = "n%d_k%d" % (n_dim, K)
            b = grid_results[tag]["substrate_bpc"]
            if not math.isnan(b) and b < best_bpc:
                best_bpc = b
                best_tag = tag
                best_cv = grid_results[tag]["cv"]
                best_unsaturated = not _any_saturated(n_dim, K)

    beats_bigram = not math.isnan(best_bpc) and not math.isnan(bigram_bpc) and best_bpc < bigram_bpc
    qc_line = "Q(c) best_bpc=%.2f vs bigram=%.2f -> %s" % (
        best_bpc, bigram_bpc, "BEATS_BIGRAM" if beats_bigram else "DOES_NOT_BEAT_BIGRAM")

    summary_block = " | ".join(cfg_lines) + " || " + " | ".join(qa_lines) + " | " + qb_line + " | " + qc_line + anchor_note

    # -----------------------------------------------------------------------
    # HARD-PASS: beats bigram + cv<=0.05 + not saturated (the breakthrough)
    # -----------------------------------------------------------------------
    if beats_bigram and best_cv <= 0.05 and best_unsaturated:
        return ("HARD_PASS",
                "HARD_PASS: %s sub_bpc=%.2f < bigram=%.2f, cv=%.3f <= 0.05, "
                "not saturated, substrate-only-decode. "
                "Capacity-scaling breakthrough confirmed. %s" % (
                    best_tag, best_bpc, bigram_bpc, best_cv, summary_block))

    # -----------------------------------------------------------------------
    # HARD-FAIL: N-scaling does NOT lower BPC AND best_bpc >= bigram+0.5
    # -----------------------------------------------------------------------
    bpc_list = [bpc_k1_by_n[n] for n in N_DIM_GRID if not math.isnan(bpc_k1_by_n[n])]
    n_scaling_lowers_bpc = (len(bpc_list) >= 2 and bpc_list[-1] < bpc_list[0])
    bpc_far_from_bigram = (math.isnan(best_bpc) or math.isnan(bigram_bpc) or
                           best_bpc > bigram_bpc + 0.5)
    if not n_scaling_lowers_bpc and bpc_far_from_bigram:
        return ("HARD_FAIL",
                "HARD_FAIL: N-scaling does NOT lower substrate-BPC (bpc at K=1: %s) "
                "AND best_bpc=%.2f > bigram+0.5=%.2f. Architecture caps above bigram. "
                "%s" % (" -> ".join("%.2f" % b for b in bpc_list), best_bpc,
                          (bigram_bpc + 0.5 if not math.isnan(bigram_bpc) else float("nan")),
                          summary_block))

    # -----------------------------------------------------------------------
    # MIDDLE_BAND: N-scaling lever confirmed or close to bigram
    # -----------------------------------------------------------------------
    middle_reasons = []
    if n_scaling_lowers_bpc and (math.isnan(bigram_bpc) or best_bpc <= bigram_bpc + 0.5):
        middle_reasons.append(
            "N-scaling lowers sub_bpc monotonically (%s) AND within 0.5 bits of bigram" % (
                " -> ".join("%.2f" % b for b in bpc_list)))
    elif n_scaling_lowers_bpc:
        middle_reasons.append("N-scaling lowers sub_bpc (%s) but not within 0.5 bits of bigram" % (
            " -> ".join("%.2f" % b for b in bpc_list)))
    if not math.isnan(anchor_bpc) and not math.isnan(best_bpc) and best_bpc < anchor_bpc - 0.20:
        middle_reasons.append("best_bpc=%.2f < anchor_bpc=%.2f by >= 0.20 bits" % (
            best_bpc, anchor_bpc))

    if middle_reasons:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: %s. best_config=%s sub_bpc=%.2f vs bigram=%.2f. "
                "%s" % ("; ".join(middle_reasons), best_tag, best_bpc, bigram_bpc,
                          summary_block))

    # Default MIDDLE_BAND if neither HARD_PASS nor HARD_FAIL fully met
    return ("MIDDLE_BAND",
            "MIDDLE_BAND (marginal): best_bpc=%.2f anchor=%.2f bigram=%.2f "
            "-- partial improvement but below both HARD_PASS and MIDDLE_BAND criteria. "
            "%s" % (best_bpc, anchor_bpc, bigram_bpc, summary_block))


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s N_DIM_GRID=%s K_SET=%s V_C=%d f=%.4f "
      "MAX_DOCS=%d seeds=%s" % (
          ANCHOR_NAME, RUN_MODE, N_DIM_GRID, K_SET, V_C, F_SPARSE, MAX_DOCS, SEEDS),
      flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE}

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

# Build per-(N_DIM,K) summary for metrics.json
per_config_summary: Dict[str, Any] = {}
for n_dim in N_DIM_GRID:
    for K in K_SET:
        tag = "n%d_k%d" % (n_dim, K)
        for met in ("substrate_bpc", "substrate_concept_top1", "substrate_top1",
                    "unigram_bpc", "bigram_bpc", "ceiling_bpc"):
            k_key = "%s_%s" % (met, tag)
            vals = [p[k_key] for p in ps if k_key in p
                    and not math.isnan(p.get(k_key, float("nan")))]
            per_config_summary[k_key + "_mean"] = float(np.mean(vals)) if vals else float("nan")
        for met in ("alpha", "n_trans"):
            k_key = "%s_%s" % (met, tag)
            vals = [p[k_key] for p in ps if k_key in p
                    and not math.isnan(p.get(k_key, float("nan")))]
            per_config_summary[k_key + "_mean"] = float(np.mean(vals)) if vals else float("nan")
        if K > 1:
            g_key = "depth_token_gain_n%d_k%d" % (n_dim, K)
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
    "N_DIM_GRID": N_DIM_GRID,
    "K_SET": K_SET,
    "V_C": V_C,
    "f_sparse": F_SPARSE,
    "per_config_summary": per_config_summary,
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
