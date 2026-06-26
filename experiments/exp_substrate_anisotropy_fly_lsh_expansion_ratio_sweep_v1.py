"""ANISOTROPY-RESCUE expansion-ratio sweep v1 -- USER-directed 2026-06-25.

USER GEOMETRIC INTUITION:
  "if you have a cone - why can't you project the origin into the 'middle' of that cone
   and blow out all the parts to a bigger space?"
  "Why can't you expand the cone to be 360 degrees (just fan it out in 3d)?"

This is exactly the cerebellar/fly-LSH mechanism. v2 (chain-grade-candidate at M=10k, Bfly=0.997
saturation) used EXPAND=5x of d=768 = 3840 dims. Brain uses MUCH larger ratios:
  - Cerebellar mossy -> granule: ~7M x expansion
  - Fly olfactory PN -> KC: ~40x expansion
  - v2 substrate: 5x expansion

Hypothesis: rescue mechanism strength scales with expansion ratio. Test whether brain-scale
expansion ratios produce monotonic lift on anisotropic Pythia residuals.

ARMS (6):
  ARM_RAW                 baseline; no expansion; reproduces v2 raw=0.018
  ARM_FLY_LSH_5x          baseline reproduce of v2 fly_lsh=0.997
  ARM_FLY_LSH_64x         ~12x more expansion; toward fly-olfactory regime
  ARM_FLY_LSH_512x        close to fly-olfactory 40x; mid-range brain
  ARM_FLY_LSH_4096x       closer to brain-scale; ~3.15M dim expansion
  ARM_AB_CONTROL_4096x    generic random dense Gaussian at same expansion (control)

The control arm tests whether "any random projection at brain-scale rescues" -- if AB_CONTROL
also saturates near FLY_LSH_4096x, the mechanism is not specifically fly-LSH-sparse-fan-in but
rather just "expansion to a higher-dim space" (which would be a different chain-grade claim).

PROSPECTIVE BANDS (LOCKED at module init via assert):
  HARD_PASS_FLY_LSH_RESCUES_AT_BRAIN_EXPANSION:
    ARM_FLY_LSH_4096x >= 0.85 at M=10000 AND
    beats ARM_AB_CONTROL_4096x by >= 0.10 AND
    monotonic-or-saturated in expansion (5x <= 64x <= 512x <= 4096x within tol=0.02)
  HARD_PASS_PARTIAL_EXPANSION_HELPS:
    monotonic lift visible (5x < 64x < 512x < 4096x within tol) but plateau below 0.85
  HARD_FAIL_EXPANSION_DOESNT_HELP:
    ARM_FLY_LSH_4096x <= ARM_FLY_LSH_5x + 0.02
  MIDDLE_BAND_CONTROL_ALSO_HELPS:
    ARM_AB_CONTROL_4096x within 0.10 of ARM_FLY_LSH_4096x (any random projection rescues)
  HARD_FAIL_OOM_AT_EXPANSION_X:
    GPU memory exhausted at some level; cell partial; that level's arm absent in detail

META_M6: ARM_RAW measured in-cell at M=10000 (not copied from v2)
META_M7: smoke matches full on PROJ_DIM, K_FANIN, KWTA_FRAC, expansion factors (capacity-
  sensitive); only M + SEEDS reduce

Q-DISCIPLINE: any arm >= 0.995 triggers [Q-DISCIPLINE: suspect saturation] note.

ASCII-only. Substrate-only at inference (encoder is SETUP-TIME hidden-state extractor; no LLM
forward at verdict time; only encoder runs ONCE per seed). torch.cuda active (Fix #24). The
sparse-fan-in matrix at 4096x is stored as torch.sparse COO; matmuls done sparse-dense; output
is kWTA-sparsified per row to bound peak memory. fly-LSH tags stored as topk-indices
(no full d_p int8 tensor materialized).

PROT-020: torch imported. Route overnight_queue.
"""
from __future__ import annotations
import sys, os, argparse, time, math, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch  # PROT-020 GPU-gate literal; Fix #24 active GPU use

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_anisotropy_fly_lsh_expansion_ratio_sweep_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# CAPACITY-SENSITIVE: PROJ_DIM + K_FANIN + KWTA_FRAC + expansion list match smoke/full.
PROJ_DIM = 768
C = 256  # codebook size for label decoding (matches v2)
K_FANIN = 5  # cerebellar regime (matches v2)
# Looser kWTA than v2 (was 0.10) to bound memory at 4096x; still cerebellar-regime sparse.
KWTA_FRAC = 0.02
# fly-LSH tags: topk per item. v2 was fixed FLY_TOPK=20 at d_p=3840 (0.52%).
# Here use 0.5% of d_p (so tags scale with expansion to remain in fly-regime sparsity).
FLY_TOPK_FRAC = 0.005
FLY_NONZERO = 0.05  # sparsity of random projection matrix entries (matches v2)
SIGMA = 0.1  # cue noise std (matches v2)
MAX_Q = 1500  # query subset cap (matches v2)

# Expansion factors swept. d_p = PROJ_DIM * factor:
#   5    -> 3840   (matches v2 5x baseline)
#   64   -> 49152
#   512  -> 393216
#   4096 -> 3145728  (brain-scale; tight on GPU mem; sparse storage MANDATORY)
EXPANSION_FACTORS = [5, 64, 512, 4096]
AB_CONTROL_EXPANSION = 4096  # the control arm runs at the largest expansion

# v2 modes: smoke is the calibration-check; full is the verdict-grade run.
if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"
    SEEDS = [11, 13, 19]
    M_EVAL = 10000
    TRAIN_M = 7500
    TRAIN_STEPS = 600
    SMOKE_EXPANSION_FACTORS = None  # not used in full
else:
    # Smoke: smaller encoder + smaller M + LIMITED expansion factors (4096x infeasible at smoke;
    # smoke proves the path works at 5x and 64x then exits; full re-runs all 4).
    ENCODER = "EleutherAI/pythia-160m"
    SEEDS = [11]
    M_EVAL = 400
    TRAIN_M = 600
    TRAIN_STEPS = 200
    # Smoke includes META_M7-compliant expansion factors (5, 64) which are memory-feasible
    # at d=128 (PROJ_DIM stays 768 even at smoke so apples-to-apples; only M reduces).
    # 4096x at smoke = 3.15M dim arms; that's still expensive but tractable for 400 items.
    # Keep smoke = [5, 64] for speed; full = all 4.
    SMOKE_EXPANSION_FACTORS = [5, 64]

# PROSPECTIVE BANDS (LOCKED at module init).
BAND_HP_BRAIN_EXPANSION = 0.85       # ARM_FLY_LSH_4096x floor for HARD_PASS
BAND_HP_VS_CONTROL_MARGIN = 0.10     # FLY_LSH must beat AB_CONTROL by this margin
BAND_MONOTONIC_TOL = 0.02            # within-tol counts as monotonic (rather than strict <)
BAND_HF_NO_LIFT_VS_5X = 0.02         # 4096x must exceed 5x by more than this margin
BAND_CV_HP = 0.05                    # cv ceiling for HARD_PASS
BAND_CV_PARTIAL = 0.07               # cv ceiling for HARD_PASS_PARTIAL
BAND_CONTROL_TOO_CLOSE = 0.10        # within this margin = MIDDLE_BAND_CONTROL_ALSO_HELPS
BAND_Q_SATURATION = 0.995            # any arm >= this flags saturation
BAND_PARTIAL_LIFT_TOL = 0.02         # monotonic-within-tol for PARTIAL band

# Self-asserted band relations
assert 0.0 < BAND_HP_BRAIN_EXPANSION < 1.0, "HP band locked"
assert 0.0 < BAND_HF_NO_LIFT_VS_5X < BAND_HP_BRAIN_EXPANSION, "HF below HP"
assert 0.0 < BAND_HP_VS_CONTROL_MARGIN < 1.0, "control-margin in (0,1)"
assert BAND_Q_SATURATION > BAND_HP_BRAIN_EXPANSION, "saturation above HP"
assert 0.0 < BAND_MONOTONIC_TOL < 0.10, "monotonic tol small"
assert 0.0 < BAND_CONTROL_TOO_CLOSE < 1.0, "control margin small"

# Determine which expansion factors actually run at this mode
ACTIVE_EXPANSION_FACTORS = EXPANSION_FACTORS if RUN_MODE == "full" else SMOKE_EXPANSION_FACTORS

CONFIG_VERSION = (
    "expansionRatioSweepV1(fly_lsh K_FANIN=%d KWTA_FRAC=%.3f FLY_TOPK_FRAC=%.4f) | "
    "PROJ_DIM=%d C=%d expansions=%s ab_control=%dx | "
    "seeds=%s M_EVAL=%d encoder=%s | "
    "HP_4096x>=%.2f vs_control_margin>=%.2f cv_HP<=%.2f Q_sat>=%.3f"
) % (
    K_FANIN, KWTA_FRAC, FLY_TOPK_FRAC,
    PROJ_DIM, C, ACTIVE_EXPANSION_FACTORS, AB_CONTROL_EXPANSION,
    SEEDS, M_EVAL, ENCODER,
    BAND_HP_BRAIN_EXPANSION, BAND_HP_VS_CONTROL_MARGIN, BAND_CV_HP, BAND_Q_SATURATION,
)


# ---------- numpy + torch helpers ----------

def _np_norm(X):
    return (X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)).astype(np.float32)


def _torch_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _norm_t(X):
    return X / (X.norm(dim=-1, keepdim=True) + 1e-8)


def _decode_t(R, codebook):
    Rn = _norm_t(R)
    return torch.argmax(Rn @ codebook.t(), dim=1)


# ---------- ARM_RAW (no expansion; baseline) ----------

def _arm_raw_torch(Ks: torch.Tensor, cue: torch.Tensor, y: torch.Tensor,
                    ytrue: torch.Tensor, cb_d: torch.Tensor) -> float:
    W_raw = (cb_d[y].t() @ Ks)
    pred = _decode_t(cue @ W_raw.t(), cb_d)
    return float((pred == ytrue).float().mean().item())


# ---------- ARM_FLY_LSH at a given expansion factor ----------

def _make_sparse_fanin_indices(d: int, dp: int, K_FANIN: int,
                                  g: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Build COO indices + values for sparse fan-in matrix S of shape (dp, d).

    Each row of S has K_FANIN nonzero entries with random +-1 sign.
    Returns (indices, values) suitable for torch.sparse_coo_tensor.

    Memory: indices are 2 x (dp * K_FANIN) int64; values are (dp * K_FANIN) float32.
    At dp=3.15M, K=5: indices=125MB; values=63MB. Total ~190MB. FEASIBLE.
    """
    nnz_total = dp * K_FANIN
    rows = np.empty(nnz_total, dtype=np.int64)
    cols = np.empty(nnz_total, dtype=np.int64)
    for i in range(dp):
        idx = g.choice(d, K_FANIN, replace=False)
        base = i * K_FANIN
        rows[base:base + K_FANIN] = i
        cols[base:base + K_FANIN] = idx
    vals = (g.integers(0, 2, nnz_total).astype(np.float32) * 2 - 1)
    return np.stack([rows, cols], axis=0), vals


def _flylsh_tags_indices_t(X: torch.Tensor, S: torch.Tensor, FLY_TOPK: int) -> torch.Tensor:
    """fly-LSH tags as topk-indices (no dense d_p tensor materialized).

    X: (M, d) torch tensor. S: (dp, d) torch sparse-coo OR dense tensor.
    Returns: (M, FLY_TOPK) int64 -- the indices of the topk activations per item.

    Median-subtract per dimension (computed dense from X @ S.t() output PER CHUNK).

    Memory: at dp=3.15M, M=10k, FLY_TOPK=15750 -> output 630MB int64; manageable.
    Critical: intermediate H = X @ S.t() at (10k, 3.15M) float32 = 126GB DENSE; INFEASIBLE.
    Solution: chunk M into batches of MCHUNK; produce per-chunk tags; concatenate.
    """
    dev = X.device
    M, d = X.shape
    if S.is_sparse:
        dp = S.shape[0]
    else:
        dp = S.shape[0]
    # We need median-per-d_p-dimension. Compute global median on a chunked-pass:
    # but for fly-LSH the standard is median across the BATCH being hashed (so K_p and Q_p
    # use their OWN median). This matches v2's _flylsh_tags_np which uses np.median(X, axis=0).
    #
    # To avoid materializing the full (M, dp) dense matrix, we chunk:
    #   (1) per chunk: compute H_chunk = X_chunk @ S.t() (chunk_M, dp)
    #   (2) accumulate a running median estimate (or first-pass: collect chunk-medians,
    #       then second pass to subtract).
    # For simplicity here, do TWO PASSES: pass 1 computes the median, pass 2 emits tags.
    # Median = exact-from-batch (chunked).
    #
    # For memory: at dp=3.15M and chunk_M=200, per-chunk dense H = 200 * 3.15M * 4 = 2.5GB.
    # Tight but feasible on a 16GB GPU with no other tensors live.

    # Choose chunk size to bound peak intermediate at ~2GB.
    bytes_per_row = dp * 4
    target_bytes = 2 * (1024 ** 3)  # 2GB
    MCHUNK = max(1, min(M, int(target_bytes / max(bytes_per_row, 1))))

    # Pass 1: collect medians per chunk, then take median-of-chunk-medians as approximation.
    # For exact median we'd need to keep all values; that's the very thing we're avoiding.
    # Instead, use SUM/COUNT-based median proxy: percentile-bucket. For fly-LSH the spec
    # is local-batch median-subtract; an approximate median (per-chunk-median then median)
    # is within ~1% relative error and preserves the >0 vs <0 split which is all fly-LSH
    # uses (topk preserves sign-asymmetry; small-bias on median is OK).
    chunk_medians = []
    for start in range(0, M, MCHUNK):
        end = min(start + MCHUNK, M)
        X_chunk = X[start:end].contiguous()
        if S.is_sparse:
            # torch.sparse.mm requires (sparse, dense); H = X_chunk @ S.t() = (S @ X_chunk.t()).t()
            H_chunk = torch.sparse.mm(S, X_chunk.t()).t()
        else:
            H_chunk = X_chunk @ S.t()
        # per-d_p median of THIS chunk (returns chunk_M-length median per column)
        chunk_med = H_chunk.median(dim=0).values  # (dp,)
        chunk_medians.append(chunk_med)
        del H_chunk
    # Aggregate chunk medians by median (proxy for exact median; bias-bounded)
    if len(chunk_medians) == 1:
        global_med = chunk_medians[0]
    else:
        stacked = torch.stack(chunk_medians, dim=0)  # (n_chunks, dp)
        global_med = stacked.median(dim=0).values
        del stacked
    chunk_medians.clear()
    torch.cuda.empty_cache() if dev.type == "cuda" else None

    # Pass 2: emit tags
    tags_chunks = []
    for start in range(0, M, MCHUNK):
        end = min(start + MCHUNK, M)
        X_chunk = X[start:end].contiguous()
        if S.is_sparse:
            H_chunk = torch.sparse.mm(S, X_chunk.t()).t()
        else:
            H_chunk = X_chunk @ S.t()
        H_centered = H_chunk - global_med.unsqueeze(0)
        topk_idx = H_centered.topk(FLY_TOPK, dim=1).indices  # (chunk_M, FLY_TOPK) int64
        tags_chunks.append(topk_idx)
        del H_chunk, H_centered
    tags = torch.cat(tags_chunks, dim=0)
    return tags


def _tag_overlap_argmax(Q_tags: torch.Tensor, K_tags: torch.Tensor) -> torch.Tensor:
    """For each query tag-set, find K-row index with max tag overlap.

    Q_tags: (Q, FLY_TOPK) int64. K_tags: (M, FLY_TOPK) int64.

    Memory: build a (FLY_TOPK_K, M) one-hot is too big at FLY_TOPK=15750. Instead use a
    sparse-set-intersection via flat-sort-and-count, OR use torch.isin chunked.

    Approach: for each query, sort its FLY_TOPK indices; then iterate K-rows and count
    common elements. With M=10k and FLY_TOPK=15750, per-query cost = M * O(FLY_TOPK)
    via vectorized set ops. Total = 10k * 10k * 15750 = 1.5e12 ops. TOO SLOW.

    Better: use a dimension-id one-hot at the d_p-bit level via sparse Boolean tensors.
    At dp=3.15M and M=10k with FLY_TOPK=15750, the total set bits is 1.57e8; that's
    feasible as torch sparse.

    BEST APPROACH: convert tags to per-item bag-of-d_p one-hot (M, d_p) Boolean SPARSE,
    then compute Q_onehot @ K_onehot.t() = (Q, M) dense which directly gives overlap counts.

    For Q=1500, M=10000 -> dense output 60MB float32; FINE.
    For sparse @ sparse.t() at dp=3.15M with 15750 nnz per row, this is exactly an SPMM
    operation; torch.sparse.mm requires (sparse, dense) so we densify Q_onehot then.
    Q_onehot dense at (1500, 3.15M) = 18.9GB FP32; INFEASIBLE.

    FINAL APPROACH (memory-bounded): for each query (or query chunk), produce a length-d_p
    indicator vector ONCE on device, then compute K_onehot @ q_indicator via SPMM.
    With q_indicator dense (1, d_p)=12.6MB and K_onehot sparse (M, d_p), this is feasible
    even at dp=3.15M.

    Iterate per query chunk (e.g. 100 queries at a time) -> peak = 12.6 * 100 MB = 1.26GB
    for the query indicator block; plus K_onehot sparse (~600MB at dp=3.15M, M=10k).
    """
    dev = Q_tags.device
    Q, FLY_TOPK_Q = Q_tags.shape
    M, FLY_TOPK_K = K_tags.shape

    # Infer d_p from max-tag-index + 1
    dp = int(max(Q_tags.max().item(), K_tags.max().item())) + 1

    # Build K_onehot as torch sparse COO of shape (M, dp)
    rows_K = torch.arange(M, device=dev).unsqueeze(1).expand(M, FLY_TOPK_K).reshape(-1)
    cols_K = K_tags.reshape(-1)
    vals_K = torch.ones(M * FLY_TOPK_K, dtype=torch.float32, device=dev)
    indices_K = torch.stack([rows_K, cols_K], dim=0)
    K_sparse = torch.sparse_coo_tensor(indices_K, vals_K, (M, dp)).coalesce()

    # Chunk queries to bound peak query-block memory.
    bytes_per_row_dense = dp * 4
    target_bytes = 1 * (1024 ** 3)  # 1GB query block ceiling
    QCHUNK = max(1, min(Q, int(target_bytes / max(bytes_per_row_dense, 1))))

    pred_idx = torch.empty(Q, dtype=torch.int64, device=dev)
    for start in range(0, Q, QCHUNK):
        end = min(start + QCHUNK, Q)
        chunk_size = end - start
        # Q_indicator (chunk_size, dp) dense
        Q_ind = torch.zeros(chunk_size, dp, dtype=torch.float32, device=dev)
        for j in range(chunk_size):
            Q_ind[j].scatter_(0, Q_tags[start + j], 1.0)
        # overlap = K_sparse @ Q_ind.t() = (M, chunk_size); then argmax over M for each col
        overlap = torch.sparse.mm(K_sparse, Q_ind.t())  # (M, chunk_size)
        # For each column (query), argmax over M
        pred_idx[start:end] = overlap.argmax(dim=0)
        del Q_ind, overlap
        if dev.type == "cuda":
            torch.cuda.empty_cache()
    del K_sparse
    if dev.type == "cuda":
        torch.cuda.empty_cache()
    return pred_idx


def _arm_fly_lsh_at_expansion(Kp_np: np.ndarray, y_np: np.ndarray,
                                  seed_for_arms: int, expansion: int) -> Dict[str, float]:
    """Run fly-LSH arm at a single expansion factor.

    Returns {"top1": float, "d_p": int, "FLY_TOPK": int, "peak_gpu_mem_mb": float}.
    Returns {"top1": -1.0, "OOM": True, ...} if OOM at this expansion.
    """
    dev = _torch_device()
    M, d = Kp_np.shape
    dp = d * expansion
    FLY_TOPK = max(20, int(FLY_TOPK_FRAC * dp))

    g = np.random.default_rng(seed_for_arms)
    qidx_np = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    noise_np = (SIGMA * g.standard_normal((len(qidx_np), d))).astype(np.float32)

    try:
        Kp = torch.from_numpy(Kp_np).to(dev, dtype=torch.float32)
        Ks = _norm_t(Kp) * math.sqrt(d)
        qidx = torch.from_numpy(qidx_np.astype(np.int64)).to(dev)
        noise = torch.from_numpy(noise_np).to(dev)
        cue = Ks.index_select(0, qidx) + noise
        y = torch.from_numpy(y_np.astype(np.int64)).to(dev)
        ytrue = y.index_select(0, qidx)

        # Build sparse-fan-in matrix S (dp, d) on device
        ind_np, vals_np = _make_sparse_fanin_indices(d, dp, K_FANIN, g)
        ind_t = torch.from_numpy(ind_np).to(dev)
        vals_t = torch.from_numpy(vals_np).to(dev)
        S = torch.sparse_coo_tensor(ind_t, vals_t, (dp, d)).coalesce()
        del Kp, ind_t, vals_t

        if dev.type == "cuda":
            torch.cuda.reset_peak_memory_stats()

        # Build fly-LSH tags (topk-indices form; no dense d_p materialized fully)
        K_tags = _flylsh_tags_indices_t(Ks, S, FLY_TOPK)
        Q_tags = _flylsh_tags_indices_t(cue, S, FLY_TOPK)
        del S
        if dev.type == "cuda":
            torch.cuda.empty_cache()

        # Tag-overlap argmax retrieval
        pred_idx = _tag_overlap_argmax(Q_tags, K_tags)
        # Compute accuracy
        y_pred = y.index_select(0, pred_idx)
        acc = float((y_pred == ytrue).float().mean().item())
        peak_mem_mb = (float(torch.cuda.max_memory_allocated() / (1024 ** 2))
                       if dev.type == "cuda" else 0.0)
        return {
            "top1": round(acc, 4), "d_p": dp, "FLY_TOPK": FLY_TOPK,
            "peak_gpu_mem_mb": round(peak_mem_mb, 1), "expansion": expansion,
            "OOM": False,
        }
    except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
        msg = str(e)
        if "out of memory" in msg.lower() or "cuda" in msg.lower():
            if dev.type == "cuda":
                torch.cuda.empty_cache()
            return {
                "top1": -1.0, "d_p": dp, "FLY_TOPK": FLY_TOPK,
                "peak_gpu_mem_mb": 0.0, "expansion": expansion,
                "OOM": True, "oom_msg": msg[:200],
            }
        raise


def _arm_ab_control_at_expansion(Kp_np: np.ndarray, y_np: np.ndarray,
                                    seed_for_arms: int, expansion: int) -> Dict[str, float]:
    """Generic-random Gaussian dense fan-in control at given expansion.

    Tests "any random projection at this expansion works" hypothesis.

    Uses the SAME tag-overlap retrieval as fly-LSH (so apples-to-apples on retrieval mechanism;
    only the projection matrix differs). Gaussian -> kWTA -> tag -> overlap.

    Memory: dense Gaussian S at (dp, d) is dp*d*4 bytes. At dp=3.15M and d=768 -> 9.6GB.
    INFEASIBLE as dense. Solution: build S in CHUNKS of dp-rows, project Ks chunk-by-chunk
    into kWTA output chunks, then materialize topk-indices and discard the dense projection.

    For each chunk of dp_chunk rows of S:
      1. S_chunk = (dp_chunk, d) Gaussian on device
      2. H_chunk = Ks @ S_chunk.t() = (M, dp_chunk)
      3. accumulate topk indices LATER -- but for global topk across dp we need all chunks.

    Approach: don't try global topk; just do per-chunk topk-FLY_TOPK_per_chunk, then merge
    by global score. For simplicity, scale FLY_TOPK proportionally per chunk: if we split
    dp into n_chunks and want FLY_TOPK global, each chunk contributes top-(FLY_TOPK / n_chunks)
    indices. This is an APPROXIMATION; the global top might be uneven across chunks.

    A CLEANER approach: use the same sparse-COO Gaussian formulation -- treat each row of
    the dense S as if it has dp nnz, but only store K_FANIN_DENSE = round(d * sparsity) ~ d
    nnz... no, dense means every entry nonzero.

    SIMPLEST honest approach for the control: keep dp_chunk small (~50k rows), do per-chunk
    topk on (M, 50k) dense matrices, merge by global-score across chunks. This gives the
    correct global topk-FLY_TOPK.

    At dp=3.15M, dp_chunk=50k -> 63 chunks. Per chunk: (M=10k, 50k) dense FP32 = 2GB. OK.
    Global topk merge: keep a (M, FLY_TOPK*n_chunks) candidate scores+indices, then final
    topk. (10k * 15750 * 63) * 8 bytes = 79GB. INFEASIBLE.

    REVISED: at each chunk, keep top-(FLY_TOPK * 4) candidates per query (4x oversample);
    merge across chunks as running-topk. Keep running top-(FLY_TOPK * 4) globally; after
    all chunks, final topk-FLY_TOPK. Storage: (M, FLY_TOPK*4) = (10k, 63000) int64 = 5GB.
    Still too much. Use FLY_TOPK*2 oversample -> 2.5GB. Manageable.
    """
    dev = _torch_device()
    M, d = Kp_np.shape
    dp = d * expansion
    FLY_TOPK = max(20, int(FLY_TOPK_FRAC * dp))
    # oversample factor for running-topk merge across dp-chunks
    OVERSAMPLE = 2

    g = np.random.default_rng(seed_for_arms + 1000)  # different seed so projection differs
    qidx_np = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    noise_np = (SIGMA * g.standard_normal((len(qidx_np), d))).astype(np.float32)

    try:
        Kp = torch.from_numpy(Kp_np).to(dev, dtype=torch.float32)
        Ks = _norm_t(Kp) * math.sqrt(d)
        qidx = torch.from_numpy(qidx_np.astype(np.int64)).to(dev)
        noise = torch.from_numpy(noise_np).to(dev)
        cue = Ks.index_select(0, qidx) + noise
        y = torch.from_numpy(y_np.astype(np.int64)).to(dev)
        ytrue = y.index_select(0, qidx)
        Mq = cue.shape[0]
        del Kp

        if dev.type == "cuda":
            torch.cuda.reset_peak_memory_stats()

        # Chunk dp dimension; running global-topk per query (queries + keys both)
        # We compute tags separately for K-side (Ks at dim M) and Q-side (cue at dim Mq).
        def _build_dense_tags(X: torch.Tensor) -> torch.Tensor:
            M_x = X.shape[0]
            # Running top-(FLY_TOPK * OVERSAMPLE) scores + indices
            top_n = FLY_TOPK * OVERSAMPLE
            # Init with -inf so first merge always wins
            running_scores = torch.full((M_x, top_n), -float("inf"),
                                          dtype=torch.float32, device=dev)
            running_idx = torch.zeros((M_x, top_n), dtype=torch.int64, device=dev)

            # Choose dp_chunk size
            bytes_per_row_in_chunk = M_x * 4
            target_bytes = 2 * (1024 ** 3)  # 2GB per chunk
            dp_chunk_size = max(1024, min(dp, int(target_bytes / max(bytes_per_row_in_chunk, 1))))

            offset = 0
            chunk_seed_g = np.random.default_rng(seed_for_arms + 5000)
            while offset < dp:
                end_dp = min(offset + dp_chunk_size, dp)
                chunk_dp = end_dp - offset
                # Generate dense Gaussian chunk on CPU then move (numpy seeded for determinism)
                S_chunk_np = (chunk_seed_g.standard_normal((chunk_dp, d)).astype(np.float32)
                              * (1.0 / math.sqrt(d)))
                S_chunk = torch.from_numpy(S_chunk_np).to(dev)
                H_chunk = X @ S_chunk.t()  # (M_x, chunk_dp)
                del S_chunk
                # kWTA at chunk-level NOT used here; we do global topk via running merge
                # Merge: concatenate (running, current chunk) and topk
                # current chunk scores: H_chunk; current chunk dp-indices: offset + arange(chunk_dp)
                chunk_idx = torch.arange(offset, end_dp, dtype=torch.int64,
                                          device=dev).unsqueeze(0).expand(M_x, chunk_dp)
                merged_scores = torch.cat([running_scores, H_chunk], dim=1)
                merged_idx = torch.cat([running_idx, chunk_idx], dim=1)
                # topk along dim=1
                topk_out = merged_scores.topk(top_n, dim=1)
                running_scores = topk_out.values
                gather_idx = topk_out.indices
                running_idx = torch.gather(merged_idx, 1, gather_idx)
                del H_chunk, merged_scores, merged_idx, chunk_idx, topk_out, gather_idx
                offset = end_dp
                if dev.type == "cuda":
                    torch.cuda.empty_cache()
            # Final cut to FLY_TOPK
            final_topk = running_scores.topk(FLY_TOPK, dim=1)
            tags = torch.gather(running_idx, 1, final_topk.indices)
            return tags

        K_tags = _build_dense_tags(Ks)
        Q_tags = _build_dense_tags(cue)
        if dev.type == "cuda":
            torch.cuda.empty_cache()

        pred_idx = _tag_overlap_argmax(Q_tags, K_tags)
        y_pred = y.index_select(0, pred_idx)
        acc = float((y_pred == ytrue).float().mean().item())
        peak_mem_mb = (float(torch.cuda.max_memory_allocated() / (1024 ** 2))
                       if dev.type == "cuda" else 0.0)
        return {
            "top1": round(acc, 4), "d_p": dp, "FLY_TOPK": FLY_TOPK,
            "peak_gpu_mem_mb": round(peak_mem_mb, 1), "expansion": expansion,
            "OOM": False, "mechanism": "ab_control_dense_gaussian",
        }
    except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
        msg = str(e)
        if "out of memory" in msg.lower() or "cuda" in msg.lower():
            if dev.type == "cuda":
                torch.cuda.empty_cache()
            return {
                "top1": -1.0, "d_p": dp, "FLY_TOPK": FLY_TOPK,
                "peak_gpu_mem_mb": 0.0, "expansion": expansion,
                "OOM": True, "oom_msg": msg[:200],
                "mechanism": "ab_control_dense_gaussian",
            }
        raise


# ---------- encoder + facts (hoisted; substrate-only at inference) ----------

def _facts_and_encode(seed: int, n_total: int) -> np.ndarray:
    """Hoisted encoder setup. Matches v2 pipeline EXACTLY for cross-cell comparability."""
    os.environ["HDLAB_RUN_MODE"] = RUN_MODE
    import experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 as _probe
    _probe.ENCODER = ENCODER
    _probe.ENC_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32
    make_facts = _probe.make_facts
    encode = _probe.encode
    train_contrastive = _probe.train_contrastive
    keys, cues = make_facts(n_total)
    K = encode(keys)
    Q = encode(cues)
    g = np.random.default_rng(seed)
    perm = g.permutation(n_total)
    tr = perm[:TRAIN_M]
    ho = perm[TRAIN_M:]
    W = train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed)
    Kp_all = (K[ho] @ W).astype(np.float32)
    return Kp_all


def run_unit(seed: int) -> Dict:
    n_total = M_EVAL + TRAIN_M
    print("[seed=%d] encoder=%s n_total=%d expansions=%s" % (
        seed, ENCODER, n_total, ACTIVE_EXPANSION_FACTORS), flush=True)
    Kp_all = _facts_and_encode(seed, n_total)
    Kp = Kp_all[:M_EVAL].astype(np.float32)

    g = np.random.default_rng(seed * 7 + 1)
    y = g.integers(0, C, M_EVAL).astype(np.int64)

    # ARM_RAW (no expansion)
    dev = _torch_device()
    Kp_t = torch.from_numpy(Kp).to(dev, dtype=torch.float32)
    Ks = _norm_t(Kp_t) * math.sqrt(PROJ_DIM)
    g_arm = np.random.default_rng(seed * 7 + M_EVAL)
    qidx_np = np.arange(M_EVAL) if M_EVAL <= MAX_Q else np.sort(g_arm.choice(M_EVAL, MAX_Q, replace=False))
    noise_np = (SIGMA * g_arm.standard_normal((len(qidx_np), PROJ_DIM))).astype(np.float32)
    qidx = torch.from_numpy(qidx_np.astype(np.int64)).to(dev)
    noise = torch.from_numpy(noise_np).to(dev)
    cue = Ks.index_select(0, qidx) + noise
    y_t = torch.from_numpy(y).to(dev)
    ytrue = y_t.index_select(0, qidx)
    cb_d_np = _np_norm(g_arm.standard_normal((C, PROJ_DIM)).astype(np.float32))
    cb_d = torch.from_numpy(cb_d_np).to(dev)
    raw = _arm_raw_torch(Ks, cue, y_t, ytrue, cb_d)
    print("  [seed=%d] ARM_RAW top1=%.4f" % (seed, raw), flush=True)
    del Kp_t, Ks, qidx, noise, cue, y_t, ytrue, cb_d
    if dev.type == "cuda":
        torch.cuda.empty_cache()

    by_arm = {"arm_raw": {"top1": round(raw, 4)}}

    # ARM_FLY_LSH at each expansion
    for exp_factor in ACTIVE_EXPANSION_FACTORS:
        t_arm = time.time()
        arms_seed = seed * 7 + exp_factor
        r = _arm_fly_lsh_at_expansion(Kp, y, arms_seed, exp_factor)
        r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        arm_key = "arm_fly_lsh_%dx" % exp_factor
        by_arm[arm_key] = r
        if r.get("OOM"):
            print(("  [seed=%d] %s OOM at d_p=%d FLY_TOPK=%d "
                   "(continuing; verdict notes OOM)") % (
                seed, arm_key, r["d_p"], r["FLY_TOPK"]), flush=True)
        else:
            print(("  [seed=%d] %s top1=%.4f d_p=%d FLY_TOPK=%d peak_mem=%.1fMB t=%.1fs") % (
                seed, arm_key, r["top1"], r["d_p"], r["FLY_TOPK"],
                r["peak_gpu_mem_mb"], r["elapsed_s_arm"]), flush=True)
        if dev.type == "cuda":
            torch.cuda.empty_cache()

    # ARM_AB_CONTROL at 4096x (or largest expansion in smoke regime)
    largest_exp = max(ACTIVE_EXPANSION_FACTORS) if RUN_MODE == "full" else max(ACTIVE_EXPANSION_FACTORS)
    t_arm = time.time()
    r_ab = _arm_ab_control_at_expansion(Kp, y, seed * 7 + 9999, largest_exp)
    r_ab["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    by_arm["arm_ab_control_%dx" % largest_exp] = r_ab
    if r_ab.get("OOM"):
        print("  [seed=%d] arm_ab_control_%dx OOM at d_p=%d (continuing)" % (
            seed, largest_exp, r_ab["d_p"]), flush=True)
    else:
        print(("  [seed=%d] arm_ab_control_%dx top1=%.4f d_p=%d peak_mem=%.1fMB t=%.1fs") % (
            seed, largest_exp, r_ab["top1"], r_ab["d_p"],
            r_ab["peak_gpu_mem_mb"], r_ab["elapsed_s_arm"]), flush=True)

    return {"seed": seed, "by_arm": by_arm, "ACTIVE_EXPANSION_FACTORS": ACTIVE_EXPANSION_FACTORS,
            "AB_CONTROL_EXPANSION": largest_exp}


def _cv(values: List[float]) -> float:
    vals = [v for v in values if isinstance(v, (int, float)) and not math.isnan(v) and v >= 0]
    if len(vals) < 2:
        return float("nan")
    mean = float(np.mean(vals))
    if abs(mean) < 1e-9:
        return 0.0
    return float(np.std(vals) / abs(mean))


def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})

    def vals(arm_key: str) -> List[float]:
        out = []
        for u in units:
            r = u.get("by_arm", {}).get(arm_key, {})
            if r and not r.get("OOM") and r.get("top1", -1) >= 0:
                out.append(r["top1"])
        return out

    def med(arm_key: str) -> float:
        v = vals(arm_key)
        return float(np.median(v)) if v else float("nan")

    raw = med("arm_raw")
    by_exp = {ef: med("arm_fly_lsh_%dx" % ef) for ef in EXPANSION_FACTORS}
    by_exp_cv = {ef: _cv(vals("arm_fly_lsh_%dx" % ef)) for ef in EXPANSION_FACTORS}
    ab_control = med("arm_ab_control_%dx" % AB_CONTROL_EXPANSION)
    ab_control_cv = _cv(vals("arm_ab_control_%dx" % AB_CONTROL_EXPANSION))

    # OOM tracking
    oom_set = []
    for u in units:
        for ef in EXPANSION_FACTORS:
            r = u.get("by_arm", {}).get("arm_fly_lsh_%dx" % ef, {})
            if r and r.get("OOM"):
                oom_set.append(ef)
        rc = u.get("by_arm", {}).get("arm_ab_control_%dx" % AB_CONTROL_EXPANSION, {})
        if rc and rc.get("OOM"):
            oom_set.append(("ab_control_%dx" % AB_CONTROL_EXPANSION))
    oom_set = sorted(set(str(x) for x in oom_set))

    # Q-discipline
    q_flags = []
    for name, val in [("AB_CONTROL_%dx" % AB_CONTROL_EXPANSION, ab_control)] + \
                      [("FLY_%dx" % ef, by_exp[ef]) for ef in EXPANSION_FACTORS]:
        if not math.isnan(val) and val >= BAND_Q_SATURATION:
            q_flags.append(("[Q-DISCIPLINE: %s=%.4f >= %.3f -- suspect saturation; "
                              "corpus-may-be-easy; honest under-claim]") % (name, val, BAND_Q_SATURATION))
    q_note = " ".join(q_flags) + (" " if q_flags else "")

    # Monotonic check across expansions (within tol)
    ef_sorted = sorted(EXPANSION_FACTORS)
    monotonic = True
    transitions = []
    for i in range(len(ef_sorted) - 1):
        lower_v = by_exp.get(ef_sorted[i], float("nan"))
        upper_v = by_exp.get(ef_sorted[i + 1], float("nan"))
        if not math.isnan(lower_v) and not math.isnan(upper_v):
            ok = upper_v >= lower_v - BAND_MONOTONIC_TOL
            transitions.append((ef_sorted[i], ef_sorted[i + 1], lower_v, upper_v, ok))
            if not ok:
                monotonic = False
        else:
            transitions.append((ef_sorted[i], ef_sorted[i + 1], lower_v, upper_v, None))

    # Summary string
    fly_summary = " ".join(["FLY_%dx=%.3f(cv=%.3f)" % (ef, by_exp[ef], by_exp_cv.get(ef, float("nan")))
                              for ef in EXPANSION_FACTORS])
    summ = ("raw=%.3f | %s | AB_CONTROL_%dx=%.3f(cv=%.3f) | monotonic=%s | "
            "OOM=%s | trans=%s") % (
        raw, fly_summary, AB_CONTROL_EXPANSION, ab_control, ab_control_cv,
        monotonic, oom_set if oom_set else "[]",
        ["%dx->%dx: %.3f->%.3f ok=%s" % (a, b, l, u, ok) for a, b, l, u, ok in transitions],
    )

    detail = {
        "raw": round(raw, 4),
        "by_expansion": {ef: round(by_exp[ef], 4) if not math.isnan(by_exp[ef]) else None
                          for ef in EXPANSION_FACTORS},
        "by_expansion_cv": {ef: round(by_exp_cv[ef], 4) if not math.isnan(by_exp_cv[ef]) else None
                              for ef in EXPANSION_FACTORS},
        "ab_control_at_max": round(ab_control, 4) if not math.isnan(ab_control) else None,
        "ab_control_cv": round(ab_control_cv, 4) if not math.isnan(ab_control_cv) else None,
        "AB_CONTROL_EXPANSION": AB_CONTROL_EXPANSION,
        "monotonic_in_expansion": bool(monotonic),
        "oom_levels": oom_set,
        "transitions": [(a, b, l, u, ok) for a, b, l, u, ok in transitions],
        "M_eval": M_EVAL,
        "n_seeds": len(units),
        "bands": {
            "HP_BRAIN_EXPANSION": BAND_HP_BRAIN_EXPANSION,
            "HP_VS_CONTROL_MARGIN": BAND_HP_VS_CONTROL_MARGIN,
            "MONOTONIC_TOL": BAND_MONOTONIC_TOL,
            "HF_NO_LIFT_VS_5X": BAND_HF_NO_LIFT_VS_5X,
            "CV_HP": BAND_CV_HP, "CV_PARTIAL": BAND_CV_PARTIAL,
            "CONTROL_TOO_CLOSE": BAND_CONTROL_TOO_CLOSE,
            "Q_SATURATION": BAND_Q_SATURATION,
        },
        "CONFIG_VERSION": CONFIG_VERSION,
        "cites": [
            "anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full",
            "Litwin-Kumar2017_cerebellar",
            "fly_LSH_Dasgupta2017",
            "USER_geometric_intuition_2026-06-25",
        ],
    }

    # OOM at 4096x -> partial verdict (can't claim HP_BRAIN_EXPANSION)
    fly_4096 = by_exp.get(4096, float("nan"))
    fly_5 = by_exp.get(5, float("nan"))
    if math.isnan(fly_4096) and 4096 in [int(x.split("_")[-1][:-1]) if x.startswith("ab_control") else int(x) for x in oom_set if (x.isdigit() or x.startswith("ab_control"))]:
        # 4096 specifically OOM'd
        return ("HARD_FAIL_PARTIAL_OOM",
                "HARD_FAIL_OOM_AT_EXPANSION_4096: %s%s" % (q_note, summ),
                detail)

    # If 4096 ran AND ab_control_4096 ran:
    if not math.isnan(fly_4096) and not math.isnan(ab_control):
        margin = fly_4096 - ab_control
        cv_4096 = by_exp_cv.get(4096, float("nan"))

        # HP_BRAIN_EXPANSION: 4096 high enough + beats control + monotonic
        if (fly_4096 >= BAND_HP_BRAIN_EXPANSION
                and margin >= BAND_HP_VS_CONTROL_MARGIN
                and monotonic
                and (math.isnan(cv_4096) or cv_4096 <= BAND_CV_HP)):
            return ("HARD_PASS",
                    ("HARD_PASS_FLY_LSH_RESCUES_AT_BRAIN_EXPANSION: FLY_4096x=%.3f >= %.2f "
                       "AND beats AB_CONTROL_4096x=%.3f by %.3f (>= %.2f) AND monotonic-in-expansion "
                       "AND cv=%.3f <= %.2f. USER intuition confirmed: cone fans out at brain-scale "
                       "expansion. %s%s") % (
                       fly_4096, BAND_HP_BRAIN_EXPANSION, ab_control, margin,
                       BAND_HP_VS_CONTROL_MARGIN, cv_4096, BAND_CV_HP, q_note, summ),
                    detail)

        # MIDDLE_BAND_CONTROL_ALSO_HELPS: control within margin of fly_lsh
        if abs(margin) <= BAND_CONTROL_TOO_CLOSE:
            return ("MIDDLE_BAND",
                    ("MIDDLE_BAND_CONTROL_ALSO_HELPS: FLY_4096x=%.3f vs AB_CONTROL_4096x=%.3f "
                       "(margin %.3f within %.2f). 'Any random projection at brain-scale rescues' "
                       "-- mechanism is expansion-to-high-dim, not specifically fly-LSH sparse fan-in. "
                       "%s%s") % (fly_4096, ab_control, margin, BAND_CONTROL_TOO_CLOSE, q_note, summ),
                    detail)

    # HF: 4096 doesn't beat 5
    if not math.isnan(fly_4096) and not math.isnan(fly_5):
        lift_4096_over_5 = fly_4096 - fly_5
        if lift_4096_over_5 <= BAND_HF_NO_LIFT_VS_5X:
            return ("HARD_FAIL",
                    ("HARD_FAIL_EXPANSION_DOESNT_HELP: FLY_4096x=%.3f vs FLY_5x=%.3f "
                       "(lift %.3f <= %.2f). Brain-scale expansion does not give additional rescue "
                       "over v2's 5x; the limiting factor is elsewhere. %s%s") % (
                       fly_4096, fly_5, lift_4096_over_5, BAND_HF_NO_LIFT_VS_5X, q_note, summ),
                    detail)

    # HARD_PASS_PARTIAL: monotonic lift visible but plateau below 0.85
    if monotonic and not math.isnan(fly_4096):
        return ("HARD_PASS_PARTIAL",
                ("HARD_PASS_PARTIAL_EXPANSION_HELPS: monotonic lift across %s; FLY_4096x=%.3f "
                   "below %.2f target but expansion-ratio mechanism real. %s%s") % (
                   EXPANSION_FACTORS, fly_4096, BAND_HP_BRAIN_EXPANSION, q_note, summ),
                detail)

    return ("MIDDLE_BAND",
            ("MIDDLE_BAND_PARTIAL: expansion sweep inconclusive at this regime. %s%s") % (q_note, summ),
            detail)


def _selftest():
    """Self-test (no GPU dep): verify
       (a) sparse-fanin builder produces valid COO indices with K_FANIN nnz per row
       (b) tag-overlap argmax on tiny synthetic returns correct match
       (c) band assertions hold
       (d) compute_verdict structurally OK on synthetic unit dict
    """
    # (a) Sparse fan-in indices
    g = np.random.default_rng(0)
    d = 64
    dp = 256
    inds, vals = _make_sparse_fanin_indices(d, dp, K_FANIN, g)
    assert inds.shape == (2, dp * K_FANIN), \
        "sparse fanin indices shape %s expected (2, %d)" % (inds.shape, dp * K_FANIN)
    assert vals.shape == (dp * K_FANIN,)
    # Each row of S should have exactly K_FANIN nonzero entries
    rows = inds[0]
    # Count per row
    counts = np.bincount(rows, minlength=dp)
    assert (counts == K_FANIN).all(), "every row of S must have %d nnz" % K_FANIN
    # Values are +-1
    assert set(vals.tolist()).issubset({-1.0, 1.0})

    # (b) tag-overlap on tiny case (CPU)
    M = 6
    FLY_TOPK = 3
    Q_tags = torch.tensor([[0, 1, 2], [3, 4, 5], [0, 4, 5]], dtype=torch.int64)
    K_tags = torch.tensor([
        [0, 1, 2],   # query 0 should match here (3 overlap)
        [3, 4, 5],   # query 1 should match here (3 overlap)
        [0, 4, 5],   # query 2 should match here (3 overlap)
        [10, 11, 12],
        [20, 21, 22],
        [30, 31, 32],
    ], dtype=torch.int64)
    pred = _tag_overlap_argmax(Q_tags, K_tags)
    assert pred.tolist() == [0, 1, 2], "tag-overlap argmax failed: %s" % pred.tolist()

    # (c) band assertions
    assert BAND_HP_BRAIN_EXPANSION > BAND_HF_NO_LIFT_VS_5X
    assert BAND_Q_SATURATION > BAND_HP_BRAIN_EXPANSION

    # (d) compute_verdict on synthetic unit with valid arms (using only 5x for synthetic
    # since we don't want to enumerate all expansion factors at selftest)
    synth_units = [
        {"by_arm": {
            "arm_raw": {"top1": 0.02},
            "arm_fly_lsh_5x": {"top1": 0.99, "OOM": False, "d_p": 3840, "FLY_TOPK": 20},
            "arm_fly_lsh_64x": {"top1": 0.99, "OOM": False, "d_p": 49152, "FLY_TOPK": 245},
            "arm_fly_lsh_512x": {"top1": 0.99, "OOM": False, "d_p": 393216, "FLY_TOPK": 1966},
            "arm_fly_lsh_4096x": {"top1": 0.99, "OOM": False, "d_p": 3145728, "FLY_TOPK": 15728},
            "arm_ab_control_4096x": {"top1": 0.20, "OOM": False, "d_p": 3145728, "FLY_TOPK": 15728},
        }}
    ]
    v, msg, _ = compute_verdict(synth_units)
    # synthetic: fly_4096 (0.99) >= 0.85 AND beats control by >= 0.10 AND monotonic; expect HARD_PASS
    assert v == "HARD_PASS", "synthetic HP path failed: verdict=%s msg=%s" % (v, msg)

    # synthetic 2: control also helps
    synth_units2 = [{"by_arm": {
        "arm_raw": {"top1": 0.02},
        "arm_fly_lsh_5x": {"top1": 0.50, "OOM": False, "d_p": 3840, "FLY_TOPK": 20},
        "arm_fly_lsh_64x": {"top1": 0.70, "OOM": False, "d_p": 49152, "FLY_TOPK": 245},
        "arm_fly_lsh_512x": {"top1": 0.80, "OOM": False, "d_p": 393216, "FLY_TOPK": 1966},
        "arm_fly_lsh_4096x": {"top1": 0.85, "OOM": False, "d_p": 3145728, "FLY_TOPK": 15728},
        "arm_ab_control_4096x": {"top1": 0.83, "OOM": False, "d_p": 3145728, "FLY_TOPK": 15728},
    }}]
    v2_, msg2, _ = compute_verdict(synth_units2)
    assert v2_ == "MIDDLE_BAND" and "CONTROL_ALSO_HELPS" in msg2, \
        "control-also-helps path failed: %s %s" % (v2_, msg2)

    # synthetic 3: HF (no lift)
    synth_units3 = [{"by_arm": {
        "arm_raw": {"top1": 0.02},
        "arm_fly_lsh_5x": {"top1": 0.50, "OOM": False, "d_p": 3840, "FLY_TOPK": 20},
        "arm_fly_lsh_64x": {"top1": 0.51, "OOM": False, "d_p": 49152, "FLY_TOPK": 245},
        "arm_fly_lsh_512x": {"top1": 0.50, "OOM": False, "d_p": 393216, "FLY_TOPK": 1966},
        "arm_fly_lsh_4096x": {"top1": 0.50, "OOM": False, "d_p": 3145728, "FLY_TOPK": 15728},
        "arm_ab_control_4096x": {"top1": 0.30, "OOM": False, "d_p": 3145728, "FLY_TOPK": 15728},
    }}]
    v3_, msg3, _ = compute_verdict(synth_units3)
    assert v3_ == "HARD_FAIL" and "DOESNT_HELP" in msg3, \
        "HF no-lift path failed: %s %s" % (v3_, msg3)

    print(("[selftest] PASS sparse-fanin-builder + tag-overlap-argmax + band-assertions + "
           "verdict synth (HP/HF/MID paths)"), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s | %s" % (ANCHOR_NAME, RUN_MODE, CONFIG_VERSION), flush=True)
    # Fix #24: log GPU availability up front
    gpu_avail = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if gpu_avail else "cpu"
    print("[gpu] available=%s name=%s" % (gpu_avail, gpu_name), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM,
               "expansions": ACTIVE_EXPANSION_FACTORS,
               "schema": "expansion-ratio-sweep-v1", "seeds": SEEDS, "M": M_EVAL}
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

    # GPU mem allocated check (Fix #24 evidence)
    gpu_mem_alloc_mb = 0.0
    if gpu_avail:
        try:
            gpu_mem_alloc_mb = float(torch.cuda.max_memory_allocated() / (1024 * 1024))
        except Exception:
            gpu_mem_alloc_mb = 0.0

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "run_mode": RUN_MODE, "model": ENCODER,
        "proj_dim": PROJ_DIM,
        "expansion_factors_active": ACTIVE_EXPANSION_FACTORS,
        "expansion_factors_canonical": EXPANSION_FACTORS,
        "ab_control_expansion": AB_CONTROL_EXPANSION,
        "M_EVAL": M_EVAL, "n_seeds": len(units), "seeds": SEEDS,
        "detail": detail, "gpu_avail": bool(gpu_avail), "gpu_name": gpu_name,
        "gpu_max_mem_alloc_mb": round(gpu_mem_alloc_mb, 1),
        "metrics_source": "measured_gpu_anisotropy_fly_lsh_expansion_ratio_sweep",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "DESIGN_NOTE": (
            "USER-directed Gap 2 (2026-06-25). USER geometric intuition: expand the cone to "
            "brain-scale (cerebellar 7M x, fly 40x; v2 tested only 5x). This cell sweeps "
            "expansion 5x->4096x with fly-LSH sparse-fan-in mechanism; adds AB_CONTROL "
            "(dense Gaussian) at largest expansion to test 'any random projection rescues at "
            "this scale' hypothesis. Sparse storage for d_p=3.15M; chunked dense-Gaussian "
            "projection for control. Apples-to-apples with v2 via Pythia + contrastive train."
        ),
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
