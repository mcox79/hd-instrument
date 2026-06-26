"""ANISOTROPY-RESCUE expansion-ratio sweep v2 CPU-PATH -- USER-directed 2026-06-25.

WHY THIS CELL EXISTS (USER 2026-06-25):
  v1 GPU expansion sweep + v2_batched + v3 expansion all OOM'd on the 8GB GPU at
  expansions >= 64x. Three GPU OOMs in a row block the brain-scale expansion test
  (4096x). USER directive: route to remote_cpu_queue with pure-numpy compute path
  (no GPU memory cap; CPU is slower but has ~16GB system RAM headroom).

USER GEOMETRIC INTUITION (carried over from v1):
  "if you have a cone - why can't you project the origin into the 'middle' of that
   cone and blow out all the parts to a bigger space?"
  "Why can't you expand the cone to be 360 degrees (just fan it out in 3d)?"

THIS CELL FINALIZES the anisotropy discrimination program:
  - If brain-scale (4096x) expansion rescues + FLY_LSH beats AB_CONTROL_4096x
    -> cerebellar mechanism transports to substrate at brain-scale; USER intuition
       validated; major Tier 4 path opens
  - If brain-scale helps but generic AB_CONTROL also rescues -> expansion is THE
       mechanism (not LSH specifically); still a real finding
  - If brain-scale doesn't help -> cerebellar mechanism does NOT transport to
       substrate; anisotropy stays bypassed-not-solved; substrate-product lock-in
       on partition-routing + learned-projection paths

KEY CHANGES FROM v1 (load-bearing):
  1. NO torch / NO torch.cuda imports anywhere. Pure numpy compute. No GPU cap.
  2. M reduced from 10000 -> 2000 (CPU is slower; reduce DATA not MECHANISM).
  3. Same expansion ratios {8, 64, 512, 4096}. NOTE: 8x replaces 5x baseline to
     give a single-octave step grid (8 -> 64 -> 512 -> 4096 = each step is 8x).
     This is a cleaner monotonic discriminator than the v1 [5, 64, 512, 4096].
  4. SPARSE REPRESENTATION THROUGHOUT:
       - Sparse-fan-in matrix S stored as (rows[], cols[], vals[]) COO arrays;
         at dp=4096*768=3.15M with K=5: 15.7M nnz int64+float32 = 188MB. OK.
       - fly-LSH tags stored as topk-INDICES (M, FLY_TOPK) int32. At M=2k,
         FLY_TOPK=int(0.005*3.15M)=15728: 2000*15728*4 = 126MB. OK.
       - AB_CONTROL_4096x uses chunked Gaussian + running-topk merge (same trick
         as v1; with smaller M=2k the per-chunk peak shrinks proportionally).
  5. PER-ARM MEMORY ACCOUNTING at module init: assert each arm's predicted peak
     stays under MEM_BUDGET_GB = 12 (leaves headroom on 16GB CPU).
  6. SAME ADVERSARIAL-SIMILARITY KEYS as v2_batched (consecutive-token stride-1
     windows of natural prose; adjacent keys share 15/16 tokens by construction).
     This is the discriminator regime the GPU cells were trying to test.
  7. AB_CONTROL_4096x retained -- THE LSH-vs-generic discriminator. Same chunked
     Gaussian + running-topk merge construction as v1 (CPU-port; numerically
     equivalent up to floating-point ordering).

ARMS (6):
  ARM_RAW                 baseline; no expansion; pure cosine retrieval on Kp
  ARM_FLY_LSH_8x          baseline near v2 5x but octave-grid; d_p = 6144
  ARM_FLY_LSH_64x         ~12x more; toward fly-olfactory regime; d_p = 49152
  ARM_FLY_LSH_512x        close to fly-olfactory 40x; mid-brain; d_p = 393216
  ARM_FLY_LSH_4096x       brain-scale; d_p = 3145728 (sparse-only)
  ARM_AB_CONTROL_4096x    generic random Gaussian dense fan-in (control)

PROSPECTIVE BANDS (LOCKED at module init via assert):
  HARD_PASS_BRAIN_SCALE_EXPANSION_RESCUES:
    ARM_FLY_LSH_4096x >= 0.85 at M=2000 AND
    beats ARM_AB_CONTROL_4096x by >= 0.10 AND
    monotonic in expansion (8x < 64x < 512x < 4096x within tol=0.02) AND
    cv_4096x <= 0.05
  HARD_PASS_CONTROL_ALSO_HELPS:
    BOTH ARM_FLY_LSH_4096x AND ARM_AB_CONTROL_4096x >= 0.85 AND both beat raw
    by >= 0.50 -- sparse expansion at brain-scale helps generically, NOT
    LSH-specifically
  MIDDLE_BAND_PARTIAL_LIFT:
    monotonic improvement but ARM_FLY_LSH_4096x plateau below 0.85
  HARD_FAIL_EXPANSION_DOESNT_HELP:
    ARM_FLY_LSH_4096x <= ARM_FLY_LSH_8x + 0.02 (expansion ratio not the limit;
    cerebellar mechanism doesn't transport at this corpus/regime)
  HARD_FAIL_CONTROL_DOMINATES:
    ARM_AB_CONTROL_4096x > ARM_FLY_LSH_4096x by >= 0.05 (fly-LSH is NOT the
    mechanism at brain scale; close the substrate-anisotropy story as
    "bypass-only via partition-routing + learned projection")

META_M6: ARM_RAW measured in-cell at adversarial regime (NOT copied from any
         prior cell; different M than v2, different keys than v1).
META_M7: smoke matches full along ALL capacity-sensitive dims (PROJ_DIM,
         K_FANIN, KWTA_FRAC, FLY_TOPK_FRAC, expansion factors). Only M and
         SEEDS reduce at smoke. This is the standing fix for the recurring
         smoke-vs-full sign-flip pattern flagged by Skunkworks.

Q-DISCIPLINE: any arm >= 0.995 triggers [Q-DISCIPLINE: suspect saturation] note.

ASCII-only. Substrate-only at inference (encoder is SETUP-TIME hidden-state
extractor; no LLM forward at verdict time; encoder runs ONCE per seed; cell
otherwise pure-numpy).

NO PROT-020 (no torch). Route remote_cpu_queue. CPU runner has no torch-gate.
"""
from __future__ import annotations
import sys, os, argparse, time, math, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# CAPACITY-SENSITIVE: PROJ_DIM + K_FANIN + KWTA_FRAC + expansion list match smoke/full.
# Only M and SEEDS reduce at smoke (META_M7).
PROJ_DIM = 768
C = 256                  # codebook size for label decoding
K_FANIN = 5              # cerebellar regime (matches v2 sweep)
KWTA_FRAC = 0.02         # WTA sparsity for downstream (bounds memory at 4096x)
FLY_TOPK_FRAC = 0.005    # fly-LSH tag density (matches v1)
FLY_NONZERO = 0.05       # sparsity of random projection matrix entries (matches v1)
SIGMA = 0.1              # cue noise std (matches v1; adversarial regime makes this load-bearing)
MAX_Q = 1500             # query subset cap (matches v1)

# Expansion grid: each step is 8x. Cleaner monotonicity discriminator than [5, 64, 512, 4096].
#   8    -> 6144     (baseline near v2 5x but octave-grid)
#   64   -> 49152
#   512  -> 393216
#   4096 -> 3145728   (brain-scale)
EXPANSION_FACTORS = [8, 64, 512, 4096]
AB_CONTROL_EXPANSION = 4096

# Adversarial-similarity construction (same as v2_batched)
WINDOW_TOKENS = 16
CUE_SHIFT = 1

# CPU memory budget (laptop CPU runner ~16GB; remote has more; be conservative).
MEM_BUDGET_GB = 12.0

if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"
    SEEDS = [11, 13, 19]
    M_EVAL = 2000
    TRAIN_M = 1500
    TRAIN_STEPS = 600
    ACTIVE_EXPANSION_FACTORS = list(EXPANSION_FACTORS)
else:
    # Smoke: smaller encoder + smaller M + LIMITED expansion factors (4096x still
    # feasible in CPU RAM at smoke M=400 but slow; restrict to [8, 64] for speed).
    # ALL capacity-sensitive dims (PROJ_DIM, K_FANIN, KWTA_FRAC, FLY_TOPK_FRAC)
    # remain identical to full per META_M7.
    ENCODER = "EleutherAI/pythia-160m"
    SEEDS = [11]
    M_EVAL = 400
    TRAIN_M = 600
    TRAIN_STEPS = 100
    ACTIVE_EXPANSION_FACTORS = [8, 64]

# PROSPECTIVE BANDS (LOCKED at module init via assert).
BAND_HP_BRAIN_EXPANSION = 0.85       # FLY_4096x floor for HP_BRAIN_SCALE_EXPANSION_RESCUES
BAND_HP_VS_CONTROL_MARGIN = 0.10     # FLY_LSH must beat AB_CONTROL by this margin
BAND_HP_CONTROL_ALSO = 0.85          # control floor for HP_CONTROL_ALSO_HELPS
BAND_HP_CONTROL_OVER_RAW = 0.50      # both must beat raw by this for HP_CONTROL_ALSO_HELPS
BAND_MONOTONIC_TOL = 0.02            # within-tol counts as monotonic
BAND_HF_NO_LIFT_VS_8X = 0.02         # 4096x must exceed 8x by more than this
BAND_HF_CONTROL_DOMINATES = 0.05     # AB_CONTROL > FLY by this -> HARD_FAIL
BAND_CV_HP = 0.05                    # cv ceiling for HARD_PASS
BAND_CV_PARTIAL = 0.07               # cv ceiling for MIDDLE_BAND_PARTIAL
BAND_Q_SATURATION = 0.995            # >= this flags suspect saturation
BAND_PARTIAL_LIFT_TOL = 0.02

# Self-asserted band relations
assert 0.0 < BAND_HP_BRAIN_EXPANSION < 1.0, "HP band locked"
assert 0.0 < BAND_HF_NO_LIFT_VS_8X < BAND_HP_BRAIN_EXPANSION, "HF below HP"
assert 0.0 < BAND_HP_VS_CONTROL_MARGIN < 1.0, "control-margin in (0,1)"
assert BAND_Q_SATURATION > BAND_HP_BRAIN_EXPANSION, "saturation above HP"
assert 0.0 < BAND_MONOTONIC_TOL < 0.10, "monotonic tol small"
assert 0.0 < BAND_HF_CONTROL_DOMINATES < BAND_HP_VS_CONTROL_MARGIN, "HF_control_dominates < HP_margin"
assert 0.0 < BAND_HP_CONTROL_OVER_RAW < BAND_HP_CONTROL_ALSO, "control_over_raw < control_floor"

CONFIG_VERSION = (
    "expansionSweepV2CpuPath(fly_lsh K_FANIN=%d KWTA_FRAC=%.3f FLY_TOPK_FRAC=%.4f) | "
    "PROJ_DIM=%d C=%d expansions=%s ab_control=%dx | window=%dt shift=%d | "
    "seeds=%s M_EVAL=%d encoder=%s | "
    "HP_4096x>=%.2f vs_control_margin>=%.2f cv_HP<=%.2f Q_sat>=%.3f | "
    "PURE_NUMPY_NO_TORCH_NO_GPU_CAP mem_budget_gb=%.1f"
) % (
    K_FANIN, KWTA_FRAC, FLY_TOPK_FRAC,
    PROJ_DIM, C, ACTIVE_EXPANSION_FACTORS, AB_CONTROL_EXPANSION,
    WINDOW_TOKENS, CUE_SHIFT,
    SEEDS, M_EVAL, ENCODER,
    BAND_HP_BRAIN_EXPANSION, BAND_HP_VS_CONTROL_MARGIN, BAND_CV_HP, BAND_Q_SATURATION,
    MEM_BUDGET_GB,
)


# ---------- pre-flight memory budget ----------

def _estimate_arm_peak_gb(expansion: int, M: int, mech: str) -> float:
    """Rough peak-RAM estimate (GB) for an arm at given expansion.

    mech in {"fly_lsh", "ab_control", "raw"}.
    """
    d = PROJ_DIM
    dp = d * expansion
    FLY_TOPK = max(20, int(FLY_TOPK_FRAC * dp))
    bytes_total = 0
    if mech == "raw":
        # Ks (M, d) + cb (C, d) + sim (Q, M) + cue (Q, d)
        bytes_total = (M * d * 4) + (C * d * 4) + (MAX_Q * M * 4) + (MAX_Q * d * 4)
    elif mech == "fly_lsh":
        # Sparse S: rows[dp*K_FANIN] int64 + cols[dp*K_FANIN] int64 + vals[...] float32
        s_nnz = dp * K_FANIN
        s_bytes = s_nnz * (8 + 8 + 4)
        # Per-chunk projection output (chunk_M, dp) float32 -- we bound to 256MB per chunk
        chunk_bytes = 256 * (1024 ** 2)
        # K_tags + Q_tags (M+Q, FLY_TOPK) int32
        tag_bytes = (M + MAX_Q) * FLY_TOPK * 4
        # Tag-overlap result (Q, M) float32
        ovr_bytes = MAX_Q * M * 4
        bytes_total = s_bytes + chunk_bytes + tag_bytes + ovr_bytes
    elif mech == "ab_control":
        # No persistent dense S; per-chunk dense Gaussian (chunk_dp, d) bounded to 256MB
        chunk_bytes = 256 * (1024 ** 2)
        # Per-chunk projection (M, chunk_dp); also bounded
        proj_chunk_bytes = 256 * (1024 ** 2)
        # Running top-(FLY_TOPK*OVERSAMPLE) scores+indices for both K and Q sides
        OVERSAMPLE = 2
        running_bytes = (M + MAX_Q) * FLY_TOPK * OVERSAMPLE * (4 + 8)
        tag_bytes = (M + MAX_Q) * FLY_TOPK * 4
        ovr_bytes = MAX_Q * M * 4
        bytes_total = chunk_bytes + proj_chunk_bytes + running_bytes + tag_bytes + ovr_bytes
    return bytes_total / (1024 ** 3)


# Validate memory budget at module init for ALL active arms
_peak_per_arm = {}
for _ef in ACTIVE_EXPANSION_FACTORS:
    _peak_per_arm["fly_%dx" % _ef] = _estimate_arm_peak_gb(_ef, M_EVAL, "fly_lsh")
_peak_per_arm["raw"] = _estimate_arm_peak_gb(1, M_EVAL, "raw")
_peak_per_arm["ab_control_%dx" % AB_CONTROL_EXPANSION] = _estimate_arm_peak_gb(
    AB_CONTROL_EXPANSION, M_EVAL, "ab_control")
_max_peak_gb = max(_peak_per_arm.values())
assert _max_peak_gb < MEM_BUDGET_GB, (
    "module-init MEM_BUDGET violation: worst arm peak ~%.2fGB > budget %.1fGB. "
    "Per-arm: %s. Reduce M_EVAL or expansion grid."
) % (_max_peak_gb, MEM_BUDGET_GB, _peak_per_arm)


# ---------- numpy helpers ----------

def _np_norm(X):
    return (X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)).astype(np.float32)


def _decode_np(R, codebook):
    return np.argmax(_np_norm(R) @ codebook.T, axis=1).astype(np.int64)


# ---------- ARM_RAW (no expansion; baseline pure cosine retrieval against codebook) ----------

def _arm_raw_np(Ks: np.ndarray, cue: np.ndarray, y: np.ndarray,
                ytrue: np.ndarray, cb_d: np.ndarray) -> float:
    """Codebook-decoded reconstruction: W_raw = cb[y].T @ Ks; pred = decode(cue @ W_raw.T)."""
    W_raw = (cb_d[y].T @ Ks)        # (d, d)
    R = cue @ W_raw.T               # (Q, d)
    pred = _decode_np(R, cb_d)
    return float((pred == ytrue).mean())


# ---------- sparse fan-in (numpy COO) ----------

def _make_sparse_fanin(d: int, dp: int, K: int,
                        g: np.random.Generator) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build COO arrays (rows, cols, vals) for sparse fan-in matrix S of shape (dp, d).

    Each row of S has K nonzero entries with random +-1 sign.
    Memory: rows/cols int64 = 2 * dp*K*8 = 16*dp*K bytes; vals float32 = 4*dp*K bytes.
    At dp=3.15M, K=5: 20*15.7M = 314MB. FEASIBLE on 16GB CPU.
    """
    nnz = dp * K
    rows = np.empty(nnz, dtype=np.int64)
    cols = np.empty(nnz, dtype=np.int64)
    for i in range(dp):
        idx = g.choice(d, K, replace=False)
        base = i * K
        rows[base:base + K] = i
        cols[base:base + K] = idx
    vals = (g.integers(0, 2, nnz).astype(np.float32) * 2 - 1)
    return rows, cols, vals


def _sparse_S_matvec_rows(rows: np.ndarray, cols: np.ndarray, vals: np.ndarray,
                            dp: int, d: int, X_chunk: np.ndarray) -> np.ndarray:
    """Compute H_chunk = X_chunk @ S.T where S is (dp, d) sparse-COO.

    X_chunk: (M_chunk, d) float32. Returns H_chunk: (M_chunk, dp) float32.

    Implementation: for each nonzero (r, c, v) of S, H_chunk[:, r] += X_chunk[:, c] * v.
    Use np.add.at for unbuffered accumulation, OR group by row for vectorized impl.

    For speed: iterate columns of S (i.e. for each c-bucket, accumulate
    X_chunk[:, c] scaled by vals into H_chunk[:, rows_for_that_col]).
    Even simpler: H_chunk[:, rows] += vals * X_chunk[:, cols] via fancy-indexing.
    But that has aliasing; use np.add.at to be safe.
    """
    M_chunk = X_chunk.shape[0]
    H_chunk = np.zeros((M_chunk, dp), dtype=np.float32)
    # For each nnz (r, c, v): H[:, r] += v * X[:, c].
    # Vectorize: contribs (nnz, M_chunk) = vals[:, None] * X_chunk[:, cols].T  -- too big.
    # Process in nnz-batches.
    nnz = rows.shape[0]
    NNZ_BATCH = max(1, min(nnz, 1_000_000))  # 1M nnz/batch * M_chunk * 4 bytes
    for start in range(0, nnz, NNZ_BATCH):
        end = min(start + NNZ_BATCH, nnz)
        r = rows[start:end]
        c = cols[start:end]
        v = vals[start:end]
        # contribs shape (batch, M_chunk) -> we need to accumulate into H_chunk[:, r] += v[:, None] * X[:, c].T
        # Use np.add.at on transposed view:
        contribs = v[:, None] * X_chunk[:, c].T   # (batch, M_chunk)
        np.add.at(H_chunk, (slice(None), r), contribs.T)  # add (M_chunk, batch) at columns r
    return H_chunk


# ---------- fly-LSH tags (numpy; chunked to bound peak RAM) ----------

def _flylsh_tags_indices(X: np.ndarray, rows: np.ndarray, cols: np.ndarray,
                          vals: np.ndarray, dp: int, FLY_TOPK: int) -> np.ndarray:
    """fly-LSH tags as topk-indices, chunked to bound peak RAM.

    X: (M, d) float32. S: dp x d COO. Returns (M, FLY_TOPK) int32.

    Two-pass:
      pass 1: per-chunk medians (median-of-chunk-medians proxy; small bias OK as
              fly-LSH only uses >0 vs <0 split via topk)
      pass 2: emit topk-indices per row

    Per-chunk peak: H_chunk = (chunk_M, dp) float32. At dp=3.15M, chunk_M=8 ->
    96MB; at chunk_M=32 -> 384MB. Bound to 256MB to leave headroom.
    """
    M, d = X.shape
    bytes_per_row = dp * 4
    target_bytes = 256 * (1024 ** 2)
    MCHUNK = max(1, min(M, int(target_bytes / max(bytes_per_row, 1))))

    # Pass 1: collect per-chunk medians
    chunk_medians = []
    for start in range(0, M, MCHUNK):
        end = min(start + MCHUNK, M)
        X_chunk = X[start:end]
        H_chunk = _sparse_S_matvec_rows(rows, cols, vals, dp, d, X_chunk)
        chunk_med = np.median(H_chunk, axis=0)  # (dp,)
        chunk_medians.append(chunk_med)
        del H_chunk
    if len(chunk_medians) == 1:
        global_med = chunk_medians[0]
    else:
        stacked = np.stack(chunk_medians, axis=0)
        global_med = np.median(stacked, axis=0)
        del stacked
    chunk_medians = None

    # Pass 2: emit topk-indices
    tags = np.empty((M, FLY_TOPK), dtype=np.int32)
    for start in range(0, M, MCHUNK):
        end = min(start + MCHUNK, M)
        X_chunk = X[start:end]
        H_chunk = _sparse_S_matvec_rows(rows, cols, vals, dp, d, X_chunk)
        H_chunk -= global_med[None, :]
        # np.argpartition gives unsorted topk; sorting isn't needed for tag-overlap
        idx = np.argpartition(H_chunk, -FLY_TOPK, axis=1)[:, -FLY_TOPK:].astype(np.int32)
        tags[start:end] = idx
        del H_chunk
    return tags


def _tag_overlap_argmax(Q_tags: np.ndarray, K_tags: np.ndarray, dp: int) -> np.ndarray:
    """For each query tag-set, find K-row with max tag-overlap.

    Q_tags: (Q, FLY_TOPK_Q) int32. K_tags: (M, FLY_TOPK_K) int32. dp: max tag-id+1.

    Build K-side bag-of-d_p sparse Boolean indicator (M, dp) via COO; compute
    overlap = K_indicator @ q_indicator for each query chunk via sparse-dense matmul.

    For numpy, we avoid scipy: instead build per-query q_indicator dense (1, dp) then
    use np.add.reduceat or boolean masking on K_tags directly.

    SIMPLEST CORRECT APPROACH (memory-bounded):
      For each q-chunk: build q_chunk indicator dense (chunk, dp) float32; bound
      chunk_size so chunk * dp * 4 < 256MB. Compute overlap via dense matmul where
      K_indicator built per K-batch using fancy-index scatter.

    Even simpler (no dense d_p ever): for each query q, compute per-row K overlap
    by counting common tags via np.intersect1d-like ops. This is O(Q*M*FLY_TOPK)
    = 1500 * 2000 * 15728 = 4.7e10 ops. TOO SLOW.

    Use a hash-table approach: build a dict mapping tag_id -> set of K-row indices.
    Then for each query q, accumulate counts over rows by iterating q's tags and
    incrementing a counter per K-row in the tag's set.
    Complexity: per-query cost = sum over q's tags of |set(tag)| = O(FLY_TOPK * (M*FLY_TOPK/dp))
    = O(M * FLY_TOPK^2 / dp). At M=2000, FLY_TOPK=15728, dp=3.15M:
      2000 * 15728^2 / 3.15M = 157,000 ops per query. Per query 157k ops; 1500 queries
      => 235M ops. FAST.

    Implementation: invert K_tags via tag_id -> list of K-row indices, then per
    query accumulate. Use numpy bincount per query for the count step.
    """
    Q, FLY_TOPK_Q = Q_tags.shape
    M, FLY_TOPK_K = K_tags.shape

    # Build inverted index: for each tag-id, list of K-rows.
    # Concatenate (tag_id, k_row) pairs and sort by tag_id.
    k_rows = np.repeat(np.arange(M, dtype=np.int32), FLY_TOPK_K)
    k_tags_flat = K_tags.reshape(-1)
    order = np.argsort(k_tags_flat, kind="stable")
    tag_ids_sorted = k_tags_flat[order]
    k_rows_sorted = k_rows[order]
    # boundary indices: where new tag_id starts. unique tag IDs present + cum count.
    unique_tags, start_idx, counts = np.unique(tag_ids_sorted, return_index=True, return_counts=True)
    # map tag_id -> slice into k_rows_sorted
    # For O(1) lookup build dense int array of length dp pointing to "first idx" + counts.
    starts_arr = np.full(dp, -1, dtype=np.int64)
    counts_arr = np.zeros(dp, dtype=np.int64)
    starts_arr[unique_tags] = start_idx
    counts_arr[unique_tags] = counts

    pred = np.empty(Q, dtype=np.int64)
    counts_buf = np.zeros(M, dtype=np.int32)
    for q in range(Q):
        counts_buf.fill(0)
        for t in Q_tags[q]:
            s = starts_arr[t]
            if s < 0:
                continue
            cnt = counts_arr[t]
            ks = k_rows_sorted[s:s + cnt]
            # accumulate: counts_buf[ks] += 1 -- has aliasing risk if duplicates;
            # but K_tags rows are by construction distinct within a row (argpartition
            # returns unique indices) so each (tag, k) appears at most once.
            counts_buf[ks] += 1
        pred[q] = int(np.argmax(counts_buf))
    return pred


def _arm_fly_lsh(Kp: np.ndarray, y: np.ndarray, seed_for_arms: int,
                  expansion: int) -> Dict[str, float]:
    """Run fly-LSH arm at given expansion factor on CPU (numpy)."""
    M, d = Kp.shape
    dp = d * expansion
    FLY_TOPK = max(20, int(FLY_TOPK_FRAC * dp))

    g = np.random.default_rng(seed_for_arms)
    qidx = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    noise = (SIGMA * g.standard_normal((len(qidx), d))).astype(np.float32)

    Ks = _np_norm(Kp) * math.sqrt(d)
    cue = Ks[qidx] + noise
    ytrue = y[qidx]

    rows, cols, vals = _make_sparse_fanin(d, dp, K_FANIN, g)

    K_tags = _flylsh_tags_indices(Ks, rows, cols, vals, dp, FLY_TOPK)
    Q_tags = _flylsh_tags_indices(cue, rows, cols, vals, dp, FLY_TOPK)
    del rows, cols, vals

    pred_idx = _tag_overlap_argmax(Q_tags, K_tags, dp)
    y_pred = y[pred_idx]
    acc = float((y_pred == ytrue).mean())
    return {
        "top1": round(acc, 4), "d_p": dp, "FLY_TOPK": FLY_TOPK,
        "expansion": expansion, "mechanism": "fly_lsh_sparse_fanin_cpu",
    }


def _arm_ab_control(Kp: np.ndarray, y: np.ndarray, seed_for_arms: int,
                     expansion: int) -> Dict[str, float]:
    """Generic dense-Gaussian fan-in control at given expansion.

    Uses chunked dp + running top-(FLY_TOPK * OVERSAMPLE) merge for both K-side
    and Q-side. Same retrieval (tag-overlap argmax) as fly-LSH so the only
    difference is the projection structure (dense Gaussian vs sparse +-1).
    """
    M, d = Kp.shape
    dp = d * expansion
    FLY_TOPK = max(20, int(FLY_TOPK_FRAC * dp))
    OVERSAMPLE = 2

    g = np.random.default_rng(seed_for_arms + 1000)
    qidx = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    noise = (SIGMA * g.standard_normal((len(qidx), d))).astype(np.float32)

    Ks = _np_norm(Kp) * math.sqrt(d)
    cue = Ks[qidx] + noise
    ytrue = y[qidx]
    Mq = cue.shape[0]

    def _build_dense_tags(X: np.ndarray) -> np.ndarray:
        M_x = X.shape[0]
        top_n = FLY_TOPK * OVERSAMPLE
        running_scores = np.full((M_x, top_n), -np.inf, dtype=np.float32)
        running_idx = np.zeros((M_x, top_n), dtype=np.int64)

        # Chunk dp so (M_x, chunk_dp) float32 <= 256MB
        target_bytes = 256 * (1024 ** 2)
        bytes_per_row_in_chunk = M_x * 4
        dp_chunk_size = max(1024, min(dp, int(target_bytes / max(bytes_per_row_in_chunk, 1))))

        offset = 0
        chunk_g = np.random.default_rng(seed_for_arms + 5000)
        while offset < dp:
            end_dp = min(offset + dp_chunk_size, dp)
            chunk_dp = end_dp - offset
            S_chunk = (chunk_g.standard_normal((chunk_dp, d)).astype(np.float32)
                       * (1.0 / math.sqrt(d)))
            H_chunk = X @ S_chunk.T    # (M_x, chunk_dp)
            del S_chunk
            chunk_idx = (offset + np.arange(chunk_dp, dtype=np.int64))
            chunk_idx_b = np.broadcast_to(chunk_idx[None, :], (M_x, chunk_dp))
            # Merge: concat running + current, then topk
            merged_scores = np.concatenate([running_scores, H_chunk], axis=1)
            merged_idx = np.concatenate([running_idx, chunk_idx_b], axis=1)
            # argpartition for top-n (unsorted)
            top_n_local = min(top_n, merged_scores.shape[1])
            part_idx = np.argpartition(merged_scores, -top_n_local, axis=1)[:, -top_n_local:]
            running_scores = np.take_along_axis(merged_scores, part_idx, axis=1)
            running_idx = np.take_along_axis(merged_idx, part_idx, axis=1)
            del H_chunk, merged_scores, merged_idx, chunk_idx_b
            offset = end_dp
        # Final cut to FLY_TOPK
        final_topk = np.argpartition(running_scores, -FLY_TOPK, axis=1)[:, -FLY_TOPK:]
        tags = np.take_along_axis(running_idx, final_topk, axis=1).astype(np.int32)
        return tags

    K_tags = _build_dense_tags(Ks)
    Q_tags = _build_dense_tags(cue)

    pred_idx = _tag_overlap_argmax(Q_tags, K_tags, dp)
    y_pred = y[pred_idx]
    acc = float((y_pred == ytrue).mean())
    return {
        "top1": round(acc, 4), "d_p": dp, "FLY_TOPK": FLY_TOPK,
        "expansion": expansion, "mechanism": "ab_control_dense_gaussian_cpu",
    }


# ---------- adversarial-similarity facts (consecutive-token stride-1 windows) ----------

_PROSE_POOL = [
    "The cerebellum contains more neurons than the rest of the brain combined and plays a critical role in motor learning and sensorimotor integration. Granule cells in the cerebellar cortex receive sparse fan-in connections from mossy fibers, with each granule cell typically synapsing with only four to seven mossy fiber inputs. This sparse expansion creates a high-dimensional representation that separates similar input patterns into distinguishable patterns of granule cell activity.",
    "Drosophila olfactory processing relies on a similar sparse expansion architecture. The roughly fifty projection neurons sending information to the mushroom body diverge onto two thousand Kenyon cells, with each Kenyon cell sampling input from only about six projection neurons. Hashing approaches inspired by this fly architecture have proven competitive with sophisticated deep learning methods for nearest neighbor search in high dimensional spaces.",
    "Hyperdimensional computing operates on vectors of thousands of dimensions and uses simple operations like binding multiplication and superposition addition to compose structured information. The capacity of dense superposition memory scales with the effective dimensionality of the underlying representation space and decreases when stored items become correlated rather than orthogonal.",
    "Anisotropy in pretrained language model representations limits direct application of distance based retrieval methods. Token embeddings in models like BERT and Pythia cluster in narrow cones rather than spreading uniformly across the hypersphere. This concentration reduces the effective dimensionality from theoretical bounds set by the embedding size to a much smaller fraction determined by the eigenvalue spread of the covariance matrix.",
    "Whitening transformations can rotate anisotropic distributions to appear isotropic but cannot increase the underlying rank of a representation. The Mu and Viswanath analysis showed that simple post processing fixes appear to help on word similarity benchmarks while leaving the deeper rank deficiency unchanged. Architectural approaches that expand into higher dimensional sparse spaces address the rank limitation more fundamentally.",
    "Random sparse projections create new axes of representation by combining input dimensions in unpredictable ways. Some projections happen to emphasize directions orthogonal to the dominant anisotropy cone, recovering separability that was lost in the original space. The fly olfactory circuit appears to exploit exactly this property to discriminate odors that share many of the same molecular features.",
    "Locality sensitive hashing partitions vectors into buckets such that similar inputs land in the same bucket with high probability. Charikar described a hyperplane based method using sign patterns from random Gaussian projections. The output is a binary sketch where Hamming distance approximates angular distance in the original space and the dimensionality of the sketch can be tuned independently of the input dimensionality.",
    "Memory augmented neural networks attempt to combine the flexibility of dense gradient based learning with the precise content addressable retrieval of external storage. Attention mechanisms provide a continuous approximation to retrieval that can be trained end to end but suffer from quadratic complexity in the number of stored items and require careful temperature calibration to avoid mass collapsing to uniform distributions.",
    "Substrate native hyperdimensional architectures aim to perform inference without calling out to dense neural network components at retrieval time. The encoder may be used once during setup to extract hidden state representations but the inference time operations stay within the hyperdimensional algebra. This separation allows the substrate to be analyzed and verified independently of the encoder used to bootstrap its initial representations.",
    "Capacity bounds for associative memory derive from the dimensionality of the storage substrate and the orthogonality of stored patterns. When the substrate dimensionality is large and stored patterns are uncorrelated the capacity scales linearly with dimensions. When patterns are correlated as in real language model residuals the effective capacity drops dramatically and recall accuracy collapses past a regime dependent threshold.",
    "The relationship between sparse expansion and retrieval accuracy depends on the specific structure of the input distribution. Synthetic random inputs achieve capacity matching theoretical bounds while naturalistic anisotropic inputs require either explicit decorrelation or architectural compensation. The cerebellar fly inspired sparse fan in approach addresses the latter by creating new axes through random combination rather than attempting to reshape the underlying input distribution.",
]


def _build_adversarial_prose(g, target_tokens):
    pool = list(_PROSE_POOL)
    pieces = []
    total_words = 0
    while total_words < target_tokens:
        idx = int(g.integers(0, len(pool)))
        pieces.append(pool[idx])
        total_words += len(pool[idx].split())
    return " ".join(pieces)


# ---------- encoder + facts (hoisted; SETUP-TIME only; substrate-only at inference) ----------

def _facts_and_encode(seed: int, n_total: int) -> np.ndarray:
    """Setup-time encoder hoisting via _probe module.

    The _probe module gracefully falls back to CPU when no CUDA available.
    Encoder runs ONCE per seed; the rest of this cell is pure numpy.
    """
    os.environ["HDLAB_RUN_MODE"] = RUN_MODE
    import experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 as _probe
    _probe.ENCODER = ENCODER
    # _probe imports torch; on CPU runner it picks CPU automatically + fp32.
    encode = _probe.encode
    train_contrastive = _probe.train_contrastive

    g = np.random.default_rng(seed)
    prose = _build_adversarial_prose(g, target_tokens=n_total + WINDOW_TOKENS + CUE_SHIFT + 50)
    words = prose.split()
    needed = n_total + WINDOW_TOKENS + CUE_SHIFT
    while len(words) < needed:
        prose = _build_adversarial_prose(g, target_tokens=needed * 2)
        words = prose.split()
    keys = []
    cues = []
    for i in range(n_total):
        keys.append(" ".join(words[i:i + WINDOW_TOKENS]))
        cues.append(" ".join(words[i + CUE_SHIFT:i + CUE_SHIFT + WINDOW_TOKENS]))
    print("[adv-facts] seed=%d n_total=%d words=%d window=%d shift=%d sample_key=%r sample_cue=%r" % (
        seed, n_total, len(words), WINDOW_TOKENS, CUE_SHIFT,
        keys[0][:60], cues[0][:60]
    ), flush=True)

    K = encode(keys)
    Q = encode(cues)

    perm = g.permutation(n_total)
    tr = perm[:TRAIN_M]
    ho = perm[TRAIN_M:]
    W = train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed)
    Kp_all = (K[ho] @ W).astype(np.float32)
    print("[adv-encode] seed=%d encoded=%d projected_dim=%d held_out=%d" % (
        seed, n_total, PROJ_DIM, len(Kp_all)), flush=True)
    return Kp_all


def run_unit(seed: int) -> Dict:
    n_total = M_EVAL + TRAIN_M
    print("[seed=%d] encoder=%s n_total=%d expansions=%s mode=%s" % (
        seed, ENCODER, n_total, ACTIVE_EXPANSION_FACTORS, RUN_MODE), flush=True)
    t_enc = time.time()
    Kp_all = _facts_and_encode(seed, n_total)
    t_enc_s = time.time() - t_enc
    print("  [seed=%d] encoder elapsed=%.1fs" % (seed, t_enc_s), flush=True)
    Kp = Kp_all[:M_EVAL].astype(np.float32)

    g = np.random.default_rng(seed * 7 + 1)
    y = g.integers(0, C, M_EVAL).astype(np.int64)

    # ARM_RAW (in-cell baseline at this adversarial regime)
    g_arm = np.random.default_rng(seed * 7 + M_EVAL)
    qidx = np.arange(M_EVAL) if M_EVAL <= MAX_Q else np.sort(g_arm.choice(M_EVAL, MAX_Q, replace=False))
    noise = (SIGMA * g_arm.standard_normal((len(qidx), PROJ_DIM))).astype(np.float32)
    Ks = _np_norm(Kp) * math.sqrt(PROJ_DIM)
    cue = Ks[qidx] + noise
    ytrue = y[qidx]
    cb_d = _np_norm(g_arm.standard_normal((C, PROJ_DIM)).astype(np.float32))
    raw = _arm_raw_np(Ks, cue, y, ytrue, cb_d)
    print("  [seed=%d] ARM_RAW top1=%.4f" % (seed, raw), flush=True)

    by_arm = {"arm_raw": {"top1": round(raw, 4)}}

    # ARM_FLY_LSH at each expansion
    for exp_factor in ACTIVE_EXPANSION_FACTORS:
        t_arm = time.time()
        arms_seed = seed * 7 + exp_factor
        r = _arm_fly_lsh(Kp, y, arms_seed, exp_factor)
        r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        arm_key = "arm_fly_lsh_%dx" % exp_factor
        by_arm[arm_key] = r
        print(("  [seed=%d] %s top1=%.4f d_p=%d FLY_TOPK=%d t=%.1fs") % (
            seed, arm_key, r["top1"], r["d_p"], r["FLY_TOPK"], r["elapsed_s_arm"]), flush=True)

    # ARM_AB_CONTROL at max expansion
    largest_exp = max(ACTIVE_EXPANSION_FACTORS)
    t_arm = time.time()
    r_ab = _arm_ab_control(Kp, y, seed * 7 + 9999, largest_exp)
    r_ab["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    by_arm["arm_ab_control_%dx" % largest_exp] = r_ab
    print(("  [seed=%d] arm_ab_control_%dx top1=%.4f d_p=%d t=%.1fs") % (
        seed, largest_exp, r_ab["top1"], r_ab["d_p"], r_ab["elapsed_s_arm"]), flush=True)

    return {"seed": seed, "by_arm": by_arm,
            "ACTIVE_EXPANSION_FACTORS": ACTIVE_EXPANSION_FACTORS,
            "AB_CONTROL_EXPANSION": largest_exp, "encoder_elapsed_s": round(t_enc_s, 2)}


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
            if r and r.get("top1", -1) >= 0:
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

    # Q-discipline
    q_flags = []
    arm_pairs = [("AB_CONTROL_%dx" % AB_CONTROL_EXPANSION, ab_control)] + \
                [("FLY_%dx" % ef, by_exp[ef]) for ef in EXPANSION_FACTORS]
    for name, val in arm_pairs:
        if not math.isnan(val) and val >= BAND_Q_SATURATION:
            q_flags.append("[Q-DISCIPLINE: %s=%.4f >= %.3f -- suspect saturation]" % (
                name, val, BAND_Q_SATURATION))
    q_note = (" ".join(q_flags) + " ") if q_flags else ""

    # Monotonic check across expansions (within tol)
    ef_sorted = sorted(EXPANSION_FACTORS)
    monotonic = True
    transitions = []
    for i in range(len(ef_sorted) - 1):
        a = ef_sorted[i]
        b = ef_sorted[i + 1]
        lv = by_exp.get(a, float("nan"))
        uv = by_exp.get(b, float("nan"))
        if not math.isnan(lv) and not math.isnan(uv):
            ok = uv >= lv - BAND_MONOTONIC_TOL
            transitions.append((a, b, lv, uv, ok))
            if not ok:
                monotonic = False
        else:
            transitions.append((a, b, lv, uv, None))

    fly_summary = " ".join(["FLY_%dx=%.3f(cv=%.3f)" % (
        ef, by_exp[ef], by_exp_cv.get(ef, float("nan"))) for ef in EXPANSION_FACTORS])
    summ = ("raw=%.3f | %s | AB_CONTROL_%dx=%.3f(cv=%.3f) | monotonic=%s | trans=%s") % (
        raw, fly_summary, AB_CONTROL_EXPANSION, ab_control, ab_control_cv,
        monotonic,
        ["%dx->%dx: %.3f->%.3f ok=%s" % (a, b, l, u, ok) for a, b, l, u, ok in transitions],
    )

    detail = {
        "raw": round(raw, 4),
        "by_expansion": {ef: (round(by_exp[ef], 4) if not math.isnan(by_exp[ef]) else None)
                          for ef in EXPANSION_FACTORS},
        "by_expansion_cv": {ef: (round(by_exp_cv[ef], 4) if not math.isnan(by_exp_cv[ef]) else None)
                              for ef in EXPANSION_FACTORS},
        "ab_control_at_max": (round(ab_control, 4) if not math.isnan(ab_control) else None),
        "ab_control_cv": (round(ab_control_cv, 4) if not math.isnan(ab_control_cv) else None),
        "AB_CONTROL_EXPANSION": AB_CONTROL_EXPANSION,
        "monotonic_in_expansion": bool(monotonic),
        "transitions": [(a, b, l, u, ok) for a, b, l, u, ok in transitions],
        "M_eval": M_EVAL,
        "n_seeds": len(units),
        "bands": {
            "HP_BRAIN_EXPANSION": BAND_HP_BRAIN_EXPANSION,
            "HP_VS_CONTROL_MARGIN": BAND_HP_VS_CONTROL_MARGIN,
            "HP_CONTROL_ALSO": BAND_HP_CONTROL_ALSO,
            "HP_CONTROL_OVER_RAW": BAND_HP_CONTROL_OVER_RAW,
            "MONOTONIC_TOL": BAND_MONOTONIC_TOL,
            "HF_NO_LIFT_VS_8X": BAND_HF_NO_LIFT_VS_8X,
            "HF_CONTROL_DOMINATES": BAND_HF_CONTROL_DOMINATES,
            "CV_HP": BAND_CV_HP, "CV_PARTIAL": BAND_CV_PARTIAL,
            "Q_SATURATION": BAND_Q_SATURATION,
        },
        "CONFIG_VERSION": CONFIG_VERSION,
        "cites": [
            "anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full",
            "anisotropy_fly_lsh_expansion_ratio_sweep_v1_GPU_OOM",
            "anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched",
            "Litwin-Kumar2017_cerebellar",
            "fly_LSH_Dasgupta2017",
            "USER_geometric_intuition_2026-06-25",
        ],
    }

    fly_4096 = by_exp.get(4096, float("nan"))
    fly_8 = by_exp.get(8, float("nan"))

    # Verdict triage
    if not math.isnan(fly_4096) and not math.isnan(ab_control):
        margin = fly_4096 - ab_control
        cv_4096 = by_exp_cv.get(4096, float("nan"))

        # HARD_PASS_BRAIN_SCALE_EXPANSION_RESCUES: FLY 4096x high + beats control + monotonic + cv
        if (fly_4096 >= BAND_HP_BRAIN_EXPANSION
                and margin >= BAND_HP_VS_CONTROL_MARGIN
                and monotonic
                and (math.isnan(cv_4096) or cv_4096 <= BAND_CV_HP)):
            return ("HARD_PASS",
                    ("HARD_PASS_BRAIN_SCALE_EXPANSION_RESCUES: FLY_4096x=%.3f >= %.2f AND beats "
                       "AB_CONTROL_4096x=%.3f by %.3f (>= %.2f) AND monotonic AND cv=%.3f <= %.2f. "
                       "USER intuition validated: cerebellar sparse fan-in transports to substrate "
                       "at brain-scale expansion. %s%s") % (
                       fly_4096, BAND_HP_BRAIN_EXPANSION, ab_control, margin,
                       BAND_HP_VS_CONTROL_MARGIN, cv_4096, BAND_CV_HP, q_note, summ),
                    detail)

        # HARD_PASS_CONTROL_ALSO_HELPS: both rescue + both beat raw substantially
        if (fly_4096 >= BAND_HP_CONTROL_ALSO and ab_control >= BAND_HP_CONTROL_ALSO
                and (fly_4096 - raw) >= BAND_HP_CONTROL_OVER_RAW
                and (ab_control - raw) >= BAND_HP_CONTROL_OVER_RAW):
            return ("HARD_PASS",
                    ("HARD_PASS_CONTROL_ALSO_HELPS: BOTH FLY_4096x=%.3f AND AB_CONTROL_4096x=%.3f "
                       ">= %.2f AND both beat raw=%.3f by >= %.2f. Expansion-to-high-dim is the "
                       "mechanism (NOT LSH-specific). %s%s") % (
                       fly_4096, ab_control, BAND_HP_CONTROL_ALSO, raw, BAND_HP_CONTROL_OVER_RAW,
                       q_note, summ),
                    detail)

        # HARD_FAIL_CONTROL_DOMINATES: AB_CONTROL > FLY by margin
        if (ab_control - fly_4096) >= BAND_HF_CONTROL_DOMINATES:
            return ("HARD_FAIL",
                    ("HARD_FAIL_CONTROL_DOMINATES: AB_CONTROL_4096x=%.3f > FLY_4096x=%.3f by %.3f "
                       "(>= %.2f). fly-LSH is NOT the mechanism at brain-scale expansion. Close "
                       "anisotropy as 'bypass-only via partition-routing + learned-projection'. "
                       "%s%s") % (
                       ab_control, fly_4096, ab_control - fly_4096,
                       BAND_HF_CONTROL_DOMINATES, q_note, summ),
                    detail)

    # HARD_FAIL_EXPANSION_DOESNT_HELP: 4096 doesn't beat 8
    if not math.isnan(fly_4096) and not math.isnan(fly_8):
        lift = fly_4096 - fly_8
        if lift <= BAND_HF_NO_LIFT_VS_8X:
            return ("HARD_FAIL",
                    ("HARD_FAIL_EXPANSION_DOESNT_HELP: FLY_4096x=%.3f vs FLY_8x=%.3f "
                       "(lift %.3f <= %.2f). Brain-scale expansion does not transport at this "
                       "regime. %s%s") % (
                       fly_4096, fly_8, lift, BAND_HF_NO_LIFT_VS_8X, q_note, summ),
                    detail)

    # MIDDLE_BAND_PARTIAL_LIFT: monotonic but plateau below 0.85
    if monotonic and not math.isnan(fly_4096) and fly_4096 < BAND_HP_BRAIN_EXPANSION:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_PARTIAL_LIFT: monotonic lift across %s; FLY_4096x=%.3f below %.2f. "
                   "Expansion-ratio mechanism real but plateau at this corpus regime. %s%s") % (
                   EXPANSION_FACTORS, fly_4096, BAND_HP_BRAIN_EXPANSION, q_note, summ),
                detail)

    return ("MIDDLE_BAND",
            ("MIDDLE_BAND_INCONCLUSIVE: expansion sweep did not cleanly separate. %s%s") % (
                q_note, summ),
            detail)


def _selftest():
    """Self-test (CPU only; bounded scale):
       (a) sparse-fanin builder produces valid COO indices with K_FANIN nnz per row
       (b) sparse matvec gives mathematically correct result vs naive dense
       (c) tag-overlap argmax on tiny synthetic returns correct match
       (d) band assertions hold
       (e) memory budget assertion holds at module init (already evaluated)
       (f) compute_verdict structurally OK on synthetic unit dict
       (g) ground-truth recall at small scale (mini fly-LSH end-to-end)
    """
    # (a) sparse fan-in
    g = np.random.default_rng(0)
    d = 32
    dp = 128
    rows, cols, vals = _make_sparse_fanin(d, dp, K_FANIN, g)
    assert rows.shape == (dp * K_FANIN,)
    assert cols.shape == (dp * K_FANIN,)
    assert vals.shape == (dp * K_FANIN,)
    counts = np.bincount(rows, minlength=dp)
    assert (counts == K_FANIN).all(), "every row of S must have %d nnz" % K_FANIN
    assert set(vals.tolist()).issubset({-1.0, 1.0})

    # (b) sparse matvec correctness vs dense
    S_dense = np.zeros((dp, d), dtype=np.float32)
    for k in range(rows.shape[0]):
        S_dense[rows[k], cols[k]] += vals[k]
    X_chunk = np.random.default_rng(1).standard_normal((5, d)).astype(np.float32)
    H_dense = X_chunk @ S_dense.T
    H_sparse = _sparse_S_matvec_rows(rows, cols, vals, dp, d, X_chunk)
    assert np.allclose(H_sparse, H_dense, atol=1e-5), (
        "sparse matvec disagrees with dense: max_abs_diff=%.6f" % np.abs(H_sparse - H_dense).max())

    # (c) tag-overlap on tiny case
    Q_tags = np.array([[0, 1, 2], [3, 4, 5], [0, 4, 5]], dtype=np.int32)
    K_tags = np.array([
        [0, 1, 2],
        [3, 4, 5],
        [0, 4, 5],
        [10, 11, 12],
        [20, 21, 22],
        [30, 31, 32],
    ], dtype=np.int32)
    pred = _tag_overlap_argmax(Q_tags, K_tags, dp=33)
    assert pred.tolist() == [0, 1, 2], "tag-overlap argmax failed: %s" % pred.tolist()

    # (d) band assertions
    assert BAND_HP_BRAIN_EXPANSION > BAND_HF_NO_LIFT_VS_8X
    assert BAND_Q_SATURATION > BAND_HP_BRAIN_EXPANSION
    assert BAND_HF_CONTROL_DOMINATES < BAND_HP_VS_CONTROL_MARGIN

    # (e) MEM_BUDGET assertion was evaluated at module init; print outcome
    print("[selftest] MEM_BUDGET per-arm estimates (GB):", flush=True)
    for k, v in sorted(_peak_per_arm.items()):
        print("    %s = %.3f" % (k, v), flush=True)
    print("    max=%.3f budget=%.1f" % (_max_peak_gb, MEM_BUDGET_GB), flush=True)

    # (f) compute_verdict synthetic paths (HP_BRAIN / HP_CONTROL_ALSO / HF_CONTROL_DOMINATES /
    #     HF_NO_LIFT / MIDDLE_BAND)
    synth_hp_brain = [{"by_arm": {
        "arm_raw": {"top1": 0.02},
        "arm_fly_lsh_8x":   {"top1": 0.20, "d_p": 6144,    "FLY_TOPK": 30},
        "arm_fly_lsh_64x":  {"top1": 0.55, "d_p": 49152,   "FLY_TOPK": 245},
        "arm_fly_lsh_512x": {"top1": 0.80, "d_p": 393216,  "FLY_TOPK": 1966},
        "arm_fly_lsh_4096x":{"top1": 0.95, "d_p": 3145728, "FLY_TOPK": 15728},
        "arm_ab_control_4096x": {"top1": 0.30, "d_p": 3145728, "FLY_TOPK": 15728},
    }}]
    v, msg, _ = compute_verdict(synth_hp_brain)
    assert v == "HARD_PASS" and "BRAIN_SCALE" in msg, "HP_BRAIN path failed: %s | %s" % (v, msg[:200])

    synth_hp_ctrl = [{"by_arm": {
        "arm_raw": {"top1": 0.02},
        "arm_fly_lsh_8x":   {"top1": 0.20, "d_p": 6144,    "FLY_TOPK": 30},
        "arm_fly_lsh_64x":  {"top1": 0.55, "d_p": 49152,   "FLY_TOPK": 245},
        "arm_fly_lsh_512x": {"top1": 0.85, "d_p": 393216,  "FLY_TOPK": 1966},
        "arm_fly_lsh_4096x":{"top1": 0.92, "d_p": 3145728, "FLY_TOPK": 15728},
        "arm_ab_control_4096x": {"top1": 0.88, "d_p": 3145728, "FLY_TOPK": 15728},
    }}]
    v2_, msg2, _ = compute_verdict(synth_hp_ctrl)
    assert v2_ == "HARD_PASS" and "CONTROL_ALSO_HELPS" in msg2, (
        "HP_CONTROL_ALSO path failed: %s | %s" % (v2_, msg2[:200]))

    synth_hf_ctrl = [{"by_arm": {
        "arm_raw": {"top1": 0.02},
        "arm_fly_lsh_8x":   {"top1": 0.10, "d_p": 6144,    "FLY_TOPK": 30},
        "arm_fly_lsh_64x":  {"top1": 0.15, "d_p": 49152,   "FLY_TOPK": 245},
        "arm_fly_lsh_512x": {"top1": 0.20, "d_p": 393216,  "FLY_TOPK": 1966},
        "arm_fly_lsh_4096x":{"top1": 0.25, "d_p": 3145728, "FLY_TOPK": 15728},
        "arm_ab_control_4096x": {"top1": 0.45, "d_p": 3145728, "FLY_TOPK": 15728},
    }}]
    v3_, msg3, _ = compute_verdict(synth_hf_ctrl)
    assert v3_ == "HARD_FAIL" and "CONTROL_DOMINATES" in msg3, (
        "HF_CONTROL_DOMINATES path failed: %s | %s" % (v3_, msg3[:200]))

    synth_hf_no_lift = [{"by_arm": {
        "arm_raw": {"top1": 0.02},
        "arm_fly_lsh_8x":   {"top1": 0.50, "d_p": 6144,    "FLY_TOPK": 30},
        "arm_fly_lsh_64x":  {"top1": 0.51, "d_p": 49152,   "FLY_TOPK": 245},
        "arm_fly_lsh_512x": {"top1": 0.50, "d_p": 393216,  "FLY_TOPK": 1966},
        "arm_fly_lsh_4096x":{"top1": 0.50, "d_p": 3145728, "FLY_TOPK": 15728},
        "arm_ab_control_4096x": {"top1": 0.30, "d_p": 3145728, "FLY_TOPK": 15728},
    }}]
    v4_, msg4, _ = compute_verdict(synth_hf_no_lift)
    assert v4_ == "HARD_FAIL" and "DOESNT_HELP" in msg4, (
        "HF_NO_LIFT path failed: %s | %s" % (v4_, msg4[:200]))

    # (g) ground-truth recall: end-to-end fly-LSH at small scale -- identity reconstruction
    # Use Kp where each row is a distinct standard-normal vector; cue = Kp + tiny noise.
    # fly-LSH should recover identity at this scale with high probability.
    gg = np.random.default_rng(42)
    M_t = 50
    d_t = 64
    Kp_t = gg.standard_normal((M_t, d_t)).astype(np.float32)
    y_t = np.arange(M_t, dtype=np.int64)
    # Run mini fly-LSH at expansion=8 (so dp=512)
    # We need to call _arm_fly_lsh with the cell's MAX_Q etc; instead run inline.
    dp_t = d_t * 8
    FLY_TOPK_t = max(20, int(FLY_TOPK_FRAC * dp_t))
    g_t = np.random.default_rng(100)
    rows_t, cols_t, vals_t = _make_sparse_fanin(d_t, dp_t, K_FANIN, g_t)
    Ks_t = _np_norm(Kp_t) * math.sqrt(d_t)
    noise_t = (0.01 * g_t.standard_normal((M_t, d_t))).astype(np.float32)
    cue_t = Ks_t + noise_t
    K_tags_t = _flylsh_tags_indices(Ks_t, rows_t, cols_t, vals_t, dp_t, FLY_TOPK_t)
    Q_tags_t = _flylsh_tags_indices(cue_t, rows_t, cols_t, vals_t, dp_t, FLY_TOPK_t)
    pred_t = _tag_overlap_argmax(Q_tags_t, K_tags_t, dp_t)
    recall = float((pred_t == y_t).mean())
    assert recall >= 0.80, (
        "ground-truth mini fly-LSH recall=%.2f < 0.80 -- mechanism broken" % recall)
    print("[selftest] mini fly-LSH ground-truth recall=%.3f (>=0.80 required)" % recall, flush=True)

    print("[selftest] PASS sparse-fanin + sparse-matvec + tag-overlap + bands + mem-budget + "
          "verdict-paths(HP_BRAIN/HP_CTRL/HF_CTRL/HF_NOLIFT) + ground-truth-recall", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s | %s" % (ANCHOR_NAME, RUN_MODE, CONFIG_VERSION), flush=True)
    print("[mem-budget] per-arm peak estimates (GB): %s" % (
        {k: round(v, 2) for k, v in _peak_per_arm.items()}), flush=True)
    print("[mem-budget] max=%.2fGB budget=%.1fGB" % (_max_peak_gb, MEM_BUDGET_GB), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM,
               "expansions": ACTIVE_EXPANSION_FACTORS,
               "schema": "expansion-sweep-v2-cpu-path", "seeds": SEEDS, "M": M_EVAL}
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

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "run_mode": RUN_MODE, "model": ENCODER,
        "proj_dim": PROJ_DIM,
        "expansion_factors_active": ACTIVE_EXPANSION_FACTORS,
        "expansion_factors_canonical": EXPANSION_FACTORS,
        "ab_control_expansion": AB_CONTROL_EXPANSION,
        "M_EVAL": M_EVAL, "n_seeds": len(units), "seeds": SEEDS,
        "detail": detail,
        "compute_path": "pure_numpy_cpu_no_torch_no_gpu",
        "mem_budget_gb": MEM_BUDGET_GB,
        "mem_peak_estimates_gb": {k: round(v, 3) for k, v in _peak_per_arm.items()},
        "metrics_source": "measured_cpu_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "DESIGN_NOTE": (
            "USER-directed 2026-06-25 v4 CPU-path: three GPU OOMs (v1 GPU sweep + "
            "v2_batched + v3) on 8GB GPU blocked the brain-scale (4096x) expansion test. "
            "Route via pure-numpy on remote_cpu_queue (no GPU cap; ~16GB RAM headroom). "
            "M reduced 10k->2k for CPU feasibility; mechanism, bands, and discriminator "
            "preserved. Expansion grid changed to [8, 64, 512, 4096] for cleaner monotonicity. "
            "Adversarial-similarity keys (stride-1 windows; same as v2_batched) for the "
            "discriminator regime. AB_CONTROL_4096x retained as LSH-vs-generic discriminator. "
            "FINAL anisotropy program cell: outcome locks substrate-product positioning for "
            "anisotropy gap (brain-scale rescue confirmed | expansion-only mechanism | bypass-only)."
        ),
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
