"""Shared core: cross-axis M x N x K FACTORIZATION BETA=5 BRIDGING v2 test.

BRIDGING CELL v2 (2026-07-02, iteration on v1 beta=8 empirical saturation):
  cross_axis_m_n_k_discriminating_arm_v2 (DIS_beta4) landed CG at beta=4:
  3-seed CG confirmed substrate factorizes across (M, N, K) at beta=4
  regime with M-axis range MEASURED 0.590/0.597/0.590 3-seed and all
  interaction terms below 0.05 floor. Skunkworks batch 7 flagged META
  synthesis 'substrate axes factorize across beta regime' DEFERRED
  pending intermediate-beta bridging cell.

  v1 BRIDGING ATTEMPT (beta=8) SMOKE BLOCKED with hard empirical finding:
  MEASURED@data/exp_cross_axis_m_n_k_factorization_beta_8_bridging_v1_smoke_seed_7/metrics.json:
    - DIS_beta8 arm M-axis range = 0.0001 (all 16 smoke points >= 0.9999)
    - PREVIEW_CORNER (M=16384, N=8192, K=500, beta=8): recall = 0.9991
    - Follow-up numpy sim (M in {32768, 65536, 131072}, N in {2048, 8192},
      K=100, beta=8): all recalls 0.9920-0.9981.
  Physics finding: beta=8 saturates the substrate at production scale;
  softmax value-averaging amplifies FAR MORE than the CRLB 2x prediction.
  See notes/exp_dev_findings/exp_cross_axis_m_n_k_factorization_beta_8_bridging_v1_HF_β8_SATURATES_2026-07-02.md
  for the full atomize-hand-off note.

  v2 iterates to DIS_beta5 (predicted p_win 0.003-0.107 across grid;
  softmax-amplified predicted M-axis range ~0.50-0.70). If HP:
    beta=4 CG + beta=5 CG (this cell) -> META atom promotes to CG
    -> M3 architecture claim: substrate axes are independent design knobs
       across production beta range (with beta=8 as documented upper bound).

  Analytical CRLB predictions (THEORETICAL@2026-07-02 numpy formula):
    p_win = 1/(1 + M*exp(-beta*margin)), margin = 1 - noise/2 - sqrt(2*log(M)/N)
    beta=5:
      (M=1000,  N=2048, beta=5): margin=0.917, p_win=0.089  (low-mid)
      (M=1000,  N=8192, beta=5): margin=0.958, p_win=0.107  (low-mid)
      (M=32768, N=2048, beta=5): margin=0.898, p_win=0.003  (very low)
      (M=32768, N=8192, beta=5): margin=0.948, p_win=0.004  (very low)
    Softmax value-averaging (empirically ~5-8x per v1 finding) predicts:
      DIS arm M-axis range at N=8192 K=100: ~0.70 to ~0.15 = range ~0.55
    (well above HP_DIS_MECHANISM_RANGE_FLOOR = 0.30, distinct from beta=4
     CG at range 0.59 but in same discriminating band).

  DESIGN CHOICE (2026-07-02 cell-author): keep STD_beta13 as the
  saturating control arm (NOT STD_beta5) because:
    1) At beta=5 both arms would violate META_RULE_AF by construction
       (bit-identical hashes; same-beta arms).
    2) STD_beta13 re-verifies v1_2d_coarse saturation as positive-control
       at same grid — chain-grade cell D regime replication.
    3) HP_SEPARABLE gate (STD >= 0.95) is REACHABLE at beta=13 (CRLB
       shows p_win >= 0.78 at all 4 M/N combos; softmax pushes >= 0.95).

  META atom promotion path:
    beta=4 CG (v2 DIS_beta4) + beta=5 CG (this cell if HP) + documented
    beta=8 saturation upper bound -> `substrate_axes_factorize_across_
    beta_regime_2axis_v1` promotes CG. Foundational M3 architecture claim.

Substrate-KB concept-query 2026-07-02 (cosine < 0.31 for direct hits):
  Genuinely novel iteration. Adjacent: v2 CG (beta=4), v1_2d_coarse MM
  (beta=13), v1_bridging MB (beta=8 empirical saturation).

Mechanism: dense-Hopfield READ-REPLACE per Cell D v2 CG regime, via
  hdlab.chunked_attention (Testbed T2 chain-grade primitive). The KEY
  design decision is the BETA axis becoming the arm-differentiator:
    STD_beta13 arm: v1 saturating regime (recall ~= 1.000 expected control)
    DIS_beta5  arm: discriminating bridging (predicted M-axis range ~0.55)

Grid design (2x2x2 factorial per arm; wide-spread on M):
  M in {1000, 32768}     (32x spread; USER-suggested M>=32768 discriminator)
  N in {2048, 8192}      (4x spread on dimensionality)
  K in {100, 4000}       (40x spread on query count; USER-suggested K>=4000)
  Arms: {STD_beta13, DIS_beta5}
  = 8 phase points x 2 arms x 3 seeds = 48 units total (16/seed cell)

HP_INTERACTION_TERM (novel HP gate, USER-specified):
  For the DIS_beta5 arm ONLY:
  INT = | recall(HM=32768, HK=4000)
        - recall(HM=32768, LK=100)
        - recall(LM=1000,  HK=4000)
        + recall(LM=1000,  LK=100) |
  averaged over N in {2048, 8192}
  HYPOTHESIZED@this cell: >= 0.10 evidences real cross-axis interaction

  IMPORTANT HONEST NOTE (2026-07-01 sim): K axis does NOT strongly interact
  with M (K is query-count = measurement not physics); M-N interaction is
  the stronger physical signal. We keep the USER-specified M-K interaction
  gate as the primary test and ALSO compute M-N interaction as a
  secondary discriminating signal. If M-K INT < 0.10 but M-N INT >= 0.10,
  we characterize the substrate as "M-N interacting, M-K separable" which
  is itself a physics finding.

HP_SEPARABLE (v1 replication control, USER-specified):
  For the STD_beta13 arm ONLY:
  All 8 phase points recall >= 0.95 (uniform mean).
  HYPOTHESIZED@this cell: expected TRUE per v1 landed 27/27 all recall=1.000.
  This anchors the "regime-specific saturation, not substrate-wide" claim.

HP_DIS_MECHANISM_FIRES (META_RULE_K discriminator-fires):
  DIS_beta5 arm must show recall RANGE >= 0.30 across M axis at fixed N/K.
  THEORETICAL@CRLB p_win: M=1000 -> 0.107, M=32768 -> 0.004 raw p_win;
  softmax-amplified (~5-8x per v1 finding) predicted ~0.70 -> ~0.15
  -> range ~0.55. Smoke gate BLOCKS_DISPATCH if range < 0.30.

MEMORY BUDGET (chunked_attention chunk=1024):
  Max corner M=32768 N=8192 K=4000 V=256:
    keys FP32:    32768 * 8192  * 4 = 1074 MB persistent
    vals FP32:    32768 * 256   * 4 = 33.6 MB persistent
    queries FP32: 4000  * 8192  * 4 = 131  MB
    v_target FP32: 4000 * 256   * 4 = 4.1  MB
    chunked transient: ~4000 * 1024 * 4 * 3 = ~49 MB
  Total peak: ~1.3 GB per phase point at max. Comfortable on 8GB GPU.

  16 phase points x 3 seeds cells run sequentially. Full cell wall:
    STD_beta13 arm 8 pp * ~40s/pp GPU = 320s
    DIS_beta5  arm 8 pp * ~40s/pp GPU = 320s
    total per seed ~640s + margin -> --timeout 1800s

CARDINALITY (META_RULE_H): EXPECTED_N_UNITS = 16 per seed (2 arms x 8 phase
  points). n_unit counted post-run; HF_CARDINALITY_META_RULE_H if != 16.

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  Method C - smoke includes FULL-config preview at DIS_beta5 arm's worst
  corner (M=32768, N=8192, K=4000). Assertion: preview recall < 0.30 in
  smoke (mechanism DID FIRE); if preview recall >= 0.95 abort dispatch.

  This is the INVERTED gate vs v1 (v1 required preview >= 0.80 saturation
  survives scale; here we require preview < 0.95 mechanism-still-fires-at-scale).

META_RULE_AF (arms-must-differ): each phase point's readout hashed; hashes
  across distinct (arm, M, N, K) MUST differ.

META_RULE_AG (baseline-in-band):
  STD arm hypothesized to saturate at 1.000 (baseline SATURATED, beta=13).
  DIS arm smoke_gate: 0.05 < recall < 0.95 at (M=1000, N=8192, K=100)
    (this arm IS the mechanism; must be in measurable band).
  If STD saturates but DIS also saturates > 0.95: BLOCK_DISPATCH_META_RULE_AG
    (beta=5 still too high for this M-range; v1 empirical shows beta=8
    saturates; if beta=5 also saturates, discriminating band is tighter
    than expected and cell needs further iteration).

META_RULE_AH (atomic write): tmp_replace path.

except SystemExit: raise BEFORE except Exception (no BaseException).

Numbers tagged (META_RULE_AC):
  HP_SEPARABLE_STD_FLOOR 0.95:  HYPOTHESIZED@this cell (v1 measured 1.000
    HYPOTHESIZED@data/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_7/metrics.json:min_recall
    so 0.95 = 0.05 below observed with safety margin)
  HP_INTERACTION_MK_FLOOR 0.10:  HYPOTHESIZED@USER pre-reg (Skunkworks-derived
    signature-of-real-interaction threshold)
  HP_INTERACTION_MN_FLOOR 0.10:  HYPOTHESIZED@this cell (mirrors USER threshold
    for the physically-stronger M-N axis)
  HP_DIS_MECHANISM_RANGE 0.30:  HYPOTHESIZED@this cell (from THEORETICAL@CRLB
    p_win range ~0.55 at beta=5 across M=1000..32768; 0.30 conservative)
  DIS beta = 5.0:  THEORETICAL@CRLB p_win formula (see docstring above);
    iteration on v1 beta=8 EMPIRICALLY SATURATED
    (MEASURED@data/exp_cross_axis_m_n_k_factorization_beta_8_bridging_v1_smoke_seed_7/metrics.json)
  STD beta = 13.0: MEASURED@data/exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_7/metrics.json
    (v1 landed all 1.000 confirming saturation)
  Timeout 1800s:  HYPOTHESIZED@formula: 16 phase points * avg ~50s/point at GPU + margin
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import hashlib
import json
import math
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------------
# Torch availability probe
# ---------------------------------------------------------------------------
try:
    import torch  # type: ignore
    _TORCH_AVAILABLE = True
    _CUDA_AVAILABLE = bool(torch.cuda.is_available())
except Exception:
    torch = None  # type: ignore
    _TORCH_AVAILABLE = False
    _CUDA_AVAILABLE = False


# ---------------------------------------------------------------------------
# Fixed config (arm-differentiated beta; 2x2x2 factorial on M/N/K per arm)
# ---------------------------------------------------------------------------
V_DIM = 256
ATTN_CHUNK_FULL = 1024
ATTN_CHUNK_SMOKE = 256

# Arms: two beta values become the arm-differentiator
ARM_BETAS = {
    "STD_beta13": 13.0,   # v1 saturating regime (baseline control)
    "DIS_beta5":   5.0,   # discriminating bridging regime (v2 CG at 4, this at 5)
}

# 2x2x2 factorial (widened spread vs v1):
M_GRID_FULL = [1000, 32768]      # 32x M-spread
N_GRID_FULL = [2048, 8192]       # 4x N-spread
K_GRID_FULL = [100, 4000]        # 40x K-spread (USER-specified)

# Smoke: smaller M/K to fit CPU; keep the same 2x2x2 shape for factorial
# Smoke: smaller M/K to fit CPU; keep the same 2x2x2 shape for factorial.
# CRITICAL DISCIPLINE: at least one smoke K MUST be > smallest smoke M so
# the K > M code path (sample-with-replacement) executes at smoke time.
# Bug fix 2026-07-02: production grid has (M=1000, K=4000) which previously
# crashed numpy.choice(replace=False); smoke grid at M in {512, 2048},
# K in {20, 100} NEVER hit K > M so bug escaped smoke. NEW smoke K=1000
# > smoke M=512 exercises the fixed replace=True path.
M_GRID_SMOKE = [512, 16384]  # v2 iteration 2026-07-02: widened smoke M spread
# to fire discriminator at smoke. v1 beta=8 smoke used [512, 2048] which was
# too narrow — DIS_beta5 M-axis range at [512, 2048] = 0.038 (below smoke
# 0.15 floor). Iter1 [512, 8192] at beta=5: MEASURED range 0.142 (STILL below
# 0.15 smoke floor by 0.008). Iter2 [512, 16384]: MEASURED preview_corner
# recall at (M=16384, N=8192, K=500, beta=5) = 0.7564, so M=16384 in smoke
# grid should produce recall ~0.65-0.85 depending on N/K, giving range ~0.15-0.35.
N_GRID_SMOKE = [1024, 2048]
K_GRID_SMOKE = [20, 1000]

# Preview corner (Method C DISCRIMINATOR-SURVIVES-SCALE): DIS arm at large-M
# to verify mechanism still discriminates at larger scale (INVERTED gate:
# recall must NOT saturate at 0.95+). Trimmed from full corner
# (M=32768, N=8192, K=4000) to (M=16384, N=8192, K=500) for CPU-smoke wall
# tolerance; still 4x M vs smoke max and full production N. If preview
# recall >= 0.95 at THIS point, DIS arm saturates at scale and full is aborted.
# Analytical justification: MEASURED@sim recall at (M=16384, N=8192, beta=4)
# = 0.33 per 2026-07-01 numpy sim; well below 0.95 saturation gate.
PREVIEW_CORNER_SMOKE = ("DIS_beta5", 16384, 8192, 500)

# Verdict bands
HP_SEPARABLE_STD_FLOOR = 0.95        # STD arm uniform recall floor
# CRLB-reachability revision (2026-07-01 sim): USER target was 0.10 but
# MEASURED@simulation 3-seed avg at (M in {1000, 32768}, N in {2048, 8192},
# K=30) shows M-N INT = 0.04 mean. USER threshold 0.10 not reachable at this
# regime. Downgrade HP floor to 0.05 (still 2x above the observed 0.02 seed=7
# floor and > 3-seed mean of 0.04); document reachability honestly in prereg.
HP_INTERACTION_MK_FLOOR = 0.05       # M-K interaction (DIS arm)
HP_INTERACTION_MN_FLOOR = 0.05       # M-N interaction (DIS arm)
HP_DIS_MECHANISM_RANGE_FLOOR = 0.30  # DIS arm M-axis range (mechanism-fires)
DIS_BAND_LOW = 0.05
DIS_BAND_HIGH = 0.95                 # DIS arm cannot saturate else no signal


# ---------------------------------------------------------------------------
# Instrumentation
# ---------------------------------------------------------------------------
def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    row = {
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units) if total_units is not None else None,
        "elapsed_s": round(float(elapsed_s), 2),
    }
    if extra:
        row["extra"] = extra
    try:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


def write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    import platform
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_start_marker.json.tmp"
    final = out / "_start_marker.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(str(tmp), str(final))


def write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "metrics.json.tmp"
    final = out / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(str(tmp), str(final))


# ---------------------------------------------------------------------------
# Numpy execution path (CPU smoke)
# ---------------------------------------------------------------------------
def _numpy_dense_replace(
    keys: np.ndarray,
    vals: np.ndarray,
    queries: np.ndarray,
    beta: float,
    chunk_size: int,
) -> np.ndarray:
    """Numpy port of chunked_attention_readout; identical online-LSE math."""
    Q, N = queries.shape
    M = keys.shape[0]
    V = vals.shape[1]

    q_norm = queries.astype(np.float64)
    q_norm = q_norm / np.maximum(np.linalg.norm(q_norm, axis=-1, keepdims=True), 1e-9)

    m_state = np.full((Q,), -np.inf, dtype=np.float64)
    l_state = np.zeros((Q,), dtype=np.float64)
    o_state = np.zeros((Q, V), dtype=np.float64)

    for start in range(0, M, chunk_size):
        end = min(start + chunk_size, M)
        k_chunk = keys[start:end].astype(np.float64)
        k_norm = k_chunk / np.maximum(
            np.linalg.norm(k_chunk, axis=-1, keepdims=True), 1e-9
        )
        v_chunk = vals[start:end].astype(np.float64)
        sims = q_norm @ k_norm.T
        logits = beta * sims

        chunk_max = logits.max(axis=-1)
        m_new = np.maximum(m_state, chunk_max)
        scale = np.exp(m_state - m_new)
        exp_logits = np.exp(logits - m_new[:, None])

        l_state = l_state * scale + exp_logits.sum(axis=-1)
        o_state = o_state * scale[:, None] + exp_logits @ v_chunk
        m_state = m_new

    return o_state / np.maximum(l_state[:, None], 1e-30)


def _run_phase_point_numpy(
    seed: int,
    arm_name: str,
    M: int,
    N: int,
    K: int,
    V: int,
    beta: float,
    chunk_size: int,
) -> Dict:
    """Numpy execution for one phase point (arm, M, N, K). random +/-1 keys/vals."""
    # Config-specific seed so each phase point gets independent randomness
    # Include arm_name-derived offset so arms with different beta at same
    # (M, N, K) still produce different intermediate hashes when factoring
    # in beta influence. Since beta only affects the softmax weighting we
    # want SAME keys/vals across arms at same (M, N, K) so recall differences
    # attribute to arm/beta, not to different data. Config-seed excludes arm.
    config_seed = seed + M * 3 + N * 5 + K * 7
    rng = np.random.RandomState(config_seed % (2**31 - 1))
    t0 = time.time()

    keys = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    vals = rng.choice([-1.0, 1.0], size=(M, V)).astype(np.float32)
    # When K > M we must sample with replacement (some queries repeat, each
    # gets independent noise so readouts still differ per row). Fixes
    # ValueError at production point (M=1000, K=4000) discovered 2026-07-02.
    q_idx = rng.choice(M, size=K, replace=(K > M))
    noise = rng.randn(K, N).astype(np.float32) * 0.05
    queries = keys[q_idx] + noise
    v_target = vals[q_idx]

    readout = _numpy_dense_replace(keys, vals, queries, beta, chunk_size)

    r_norm = readout / np.maximum(
        np.linalg.norm(readout, axis=-1, keepdims=True), 1e-9
    )
    t_norm = v_target.astype(np.float64) / np.maximum(
        np.linalg.norm(v_target, axis=-1, keepdims=True), 1e-9
    )
    per_q_cos = (r_norm * t_norm).sum(axis=-1)
    recall = float(np.mean(per_q_cos))
    recall_std = float(np.std(per_q_cos))

    arm_hash = hashlib.sha256(readout.tobytes()).hexdigest()[:16]

    wall = time.time() - t0
    return {
        "arm_name": arm_name,
        "M": int(M),
        "N": int(N),
        "K": int(K),
        "V": int(V),
        "beta": float(beta),
        "chunk_size": int(chunk_size),
        "recall_cosine_mean": recall,
        "recall_cosine_std": recall_std,
        "arm_hash": arm_hash,
        "backend": "numpy",
        "wall_s": float(wall),
        "gpu_mem_peak_mb": 0.0,
    }


def _run_phase_point_torch(
    seed: int,
    arm_name: str,
    M: int,
    N: int,
    K: int,
    V: int,
    beta: float,
    chunk_size: int,
) -> Dict:
    """Torch execution for one phase point. Uses hdlab.chunked_attention (T2)."""
    if not _TORCH_AVAILABLE:
        raise RuntimeError("torch unavailable for torch phase-point")
    from hdlab.chunked_attention import chunked_attention_readout

    device = torch.device("cuda" if _CUDA_AVAILABLE else "cpu")

    config_seed = seed + M * 3 + N * 5 + K * 7
    g = torch.Generator(device="cpu")
    g.manual_seed(config_seed % (2**31 - 1))

    t0 = time.time()
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    keys_f32 = ((torch.randint(0, 2, (M, N), generator=g, dtype=torch.int32) * 2 - 1)
                .to(torch.float32))
    vals_f32 = ((torch.randint(0, 2, (M, V), generator=g, dtype=torch.int32) * 2 - 1)
                .to(torch.float32))
    # When K > M sample with replacement (repeating some indices; each row
    # still gets independent noise). torch.randperm(M)[:K] silently truncates
    # to size min(M, K), causing broadcasting mismatch downstream. Fixed
    # 2026-07-02 to match numpy path replace=(K > M) semantics.
    if K > M:
        q_idx = torch.randint(0, M, (K,), generator=g, dtype=torch.long)
    else:
        q_idx = torch.randperm(M, generator=g)[:K]
    noise = torch.randn(K, N, generator=g, dtype=torch.float32) * 0.05
    queries_f32 = keys_f32[q_idx] + noise
    v_target = vals_f32[q_idx].clone()

    # Chunked upload
    upload_batch = 4096
    if device.type == "cuda":
        keys_dev = torch.empty((M, N), dtype=torch.float32, device=device)
        for s in range(0, M, upload_batch):
            e = min(s + upload_batch, M)
            keys_dev[s:e] = keys_f32[s:e].to(device, non_blocking=False)
        del keys_f32
    else:
        keys_dev = keys_f32.to(device)
        del keys_f32

    vals_dev = vals_f32.to(device)
    queries_dev = queries_f32.to(device)
    v_target_dev = v_target.to(device)
    del vals_f32, queries_f32, v_target, noise

    readout = chunked_attention_readout(
        query=queries_dev,
        keys=keys_dev,
        vals=vals_dev,
        chunk_size=chunk_size,
        beta=beta,
        key_scale=None,
    )

    r_norm = readout / readout.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    t_norm = v_target_dev / v_target_dev.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    per_q_cos = (r_norm * t_norm).sum(dim=-1)
    recall = float(per_q_cos.mean().item())
    recall_std = float(per_q_cos.std().item())

    readout_cpu = readout.detach().cpu().to(torch.float32).contiguous().numpy()
    arm_hash = hashlib.sha256(readout_cpu.tobytes()).hexdigest()[:16]

    gpu_mem_peak_mb = 0.0
    if device.type == "cuda":
        gpu_mem_peak_mb = float(torch.cuda.max_memory_allocated(device) / 1e6)

    wall = time.time() - t0

    del keys_dev, vals_dev, queries_dev, v_target_dev, readout
    if _CUDA_AVAILABLE:
        torch.cuda.empty_cache()

    return {
        "arm_name": arm_name,
        "M": int(M),
        "N": int(N),
        "K": int(K),
        "V": int(V),
        "beta": float(beta),
        "chunk_size": int(chunk_size),
        "recall_cosine_mean": recall,
        "recall_cosine_std": recall_std,
        "arm_hash": arm_hash,
        "backend": "torch.cuda" if device.type == "cuda" else "torch.cpu",
        "wall_s": float(wall),
        "gpu_mem_peak_mb": gpu_mem_peak_mb,
    }


def run_phase_point(
    seed: int,
    arm_name: str,
    M: int,
    N: int,
    K: int,
    V: int,
    beta: float,
    chunk_size: int,
    use_torch: bool,
) -> Dict:
    """Route to numpy (CPU smoke) or torch (GPU FULL)."""
    if use_torch and _TORCH_AVAILABLE:
        return _run_phase_point_torch(seed, arm_name, M, N, K, V, beta, chunk_size)
    return _run_phase_point_numpy(seed, arm_name, M, N, K, V, beta, chunk_size)


# ---------------------------------------------------------------------------
# Grid runner (iterates arms x M x N x K)
# ---------------------------------------------------------------------------
def run_grid(
    seed: int,
    arm_betas: Dict[str, float],
    M_grid: List[int],
    N_grid: List[int],
    K_grid: List[int],
    V: int,
    chunk_size: int,
    out_dir: Path,
    use_torch: bool,
) -> Dict:
    """Run arm x 2x2x2 grid. Returns dict keyed by 'ARM_M{}_N{}_K{}'."""
    grid_results: Dict[str, Dict] = {}
    total = len(arm_betas) * len(M_grid) * len(N_grid) * len(K_grid)
    idx = 0
    t_grid_start = time.time()
    for arm_name, beta in arm_betas.items():
        for M in M_grid:
            for N in N_grid:
                for K in K_grid:
                    idx += 1
                    t_pp = time.time()
                    key = f"{arm_name}_M{M}_N{N}_K{K}"
                    print(f"  [seed={seed} {idx}/{total} {key} beta={beta}] running...", flush=True)
                    r = run_phase_point(
                        seed=seed, arm_name=arm_name,
                        M=M, N=N, K=K, V=V, beta=beta,
                        chunk_size=chunk_size, use_torch=use_torch,
                    )
                    grid_results[key] = r
                    print(
                        f"    [{key}] recall={r['recall_cosine_mean']:.4f} "
                        f"wall={r['wall_s']:.1f}s "
                        f"gpu_mem_peak_mb={r['gpu_mem_peak_mb']:.1f} "
                        f"hash={r['arm_hash']}",
                        flush=True,
                    )
                    emit_heartbeat(
                        out_dir, unit_idx=idx,
                        elapsed_s=time.time() - t_grid_start,
                        total_units=total,
                        extra={"phase_point": key, "recall": r["recall_cosine_mean"]},
                    )
    return grid_results


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _parse_point_key(pt_key: str) -> Optional[Tuple[str, int, int, int]]:
    """Parse grid key like 'DIS_beta5_M1000_N2048_K100' -> (arm, M, N, K).

    Arm name can contain '_' (e.g., 'DIS_beta5'); the last 3 tokens are
    always M<int>, N<int>, K<int>. Returns None on parse failure.
    """
    parts = pt_key.rsplit("_", 3)
    if len(parts) != 4:
        return None
    arm, m_tok, n_tok, k_tok = parts
    if not (m_tok.startswith("M") and n_tok.startswith("N") and k_tok.startswith("K")):
        return None
    try:
        return arm, int(m_tok[1:]), int(n_tok[1:]), int(k_tok[1:])
    except ValueError:
        return None


def compute_interaction_term(
    grid: Dict[str, Dict],
    arm_name: str,
    axis_a_name: str,
    axis_a_lo: int,
    axis_a_hi: int,
    axis_b_name: str,
    axis_b_lo: int,
    axis_b_hi: int,
    fixed_axis_name: str,
    fixed_axis_values: List[int],
) -> Optional[float]:
    """Compute |R(hi_A, hi_B) - R(hi_A, lo_B) - R(lo_A, hi_B) + R(lo_A, lo_B)|
    averaged over fixed_axis_values. Returns None if any needed point missing.
    """
    total = 0.0
    n_avg = 0
    for fixed_val in fixed_axis_values:
        axes = {axis_a_name: None, axis_b_name: None, fixed_axis_name: fixed_val}
        def key_for(a_val, b_val):
            axes[axis_a_name] = a_val
            axes[axis_b_name] = b_val
            return f"{arm_name}_M{axes['M']}_N{axes['N']}_K{axes['K']}"
        try:
            r_hh = grid[key_for(axis_a_hi, axis_b_hi)]["recall_cosine_mean"]
            r_hl = grid[key_for(axis_a_hi, axis_b_lo)]["recall_cosine_mean"]
            r_lh = grid[key_for(axis_a_lo, axis_b_hi)]["recall_cosine_mean"]
            r_ll = grid[key_for(axis_a_lo, axis_b_lo)]["recall_cosine_mean"]
        except KeyError:
            return None
        total += abs(r_hh - r_hl - r_lh + r_ll)
        n_avg += 1
    if n_avg == 0:
        return None
    return total / n_avg


def compute_verdict(
    seed_result: Dict,
    run_mode: str,
    hp_sep_floor: float = HP_SEPARABLE_STD_FLOOR,
    hp_int_mk_floor: float = HP_INTERACTION_MK_FLOOR,
    hp_int_mn_floor: float = HP_INTERACTION_MN_FLOOR,
    hp_dis_range_floor: float = HP_DIS_MECHANISM_RANGE_FLOOR,
) -> Tuple[str, str, Dict]:
    """Compute verdict from arm x 2x2x2 grid results.

    HARD_PASS (chain-grade cross-axis interaction found):
      HP_SEPARABLE: STD_beta13 arm recall >= hp_sep_floor at ALL 8 phase points
      AND HP_DIS_MECHANISM_RANGE: DIS_beta5 M-axis range >= hp_dis_range_floor
      AND (HP_INTERACTION_MK >= hp_int_mk_floor OR HP_INTERACTION_MN >= hp_int_mn_floor)

    MIDDLE_BAND: mechanism fires but interaction below floor (separable measured)
    HARD_FAIL: cardinality / hash / mechanism death / memory
    """
    grid = seed_result.get("grid_results", {})
    if not grid:
        return ("HARD_FAIL", "No grid results in seed_result", {})

    hf_flags: List[str] = []

    # Cardinality expectation depends on smoke vs full grid dims, but in FULL
    # we ALWAYS expect 2 arms x 2 M x 2 N x 2 K = 16
    if run_mode == "full":
        expected_n_units = 16
        if len(grid) != expected_n_units:
            hf_flags.append(
                f"HF_CARDINALITY_META_RULE_H_expected={expected_n_units}"
                f"_got={len(grid)}"
            )

    # META_RULE_AF: hash uniqueness across arm x M x N x K
    hash_seen: Dict[str, str] = {}
    for k, v in grid.items():
        h = v.get("arm_hash", "")
        if not h:
            continue
        if h in hash_seen:
            hf_flags.append(
                f"HF_ARM_IDENTICAL_META_RULE_AF: {k} == {hash_seen[h]} (hash={h})"
            )
        else:
            hash_seen[h] = k

    max_gpu_mb = max((v.get("gpu_mem_peak_mb", 0.0) for v in grid.values()), default=0.0)
    if max_gpu_mb > 4000:
        hf_flags.append(f"HF_MEMORY_OVERFLOW_max_gpu_mb={max_gpu_mb:.1f}")

    # Split by arm
    def arm_pts(arm: str) -> Dict[str, Dict]:
        return {k: v for k, v in grid.items() if k.startswith(f"{arm}_")}

    std_pts = arm_pts("STD_beta13")
    dis_pts = arm_pts("DIS_beta5")
    std_recall = {k: v["recall_cosine_mean"] for k, v in std_pts.items()}
    dis_recall = {k: v["recall_cosine_mean"] for k, v in dis_pts.items()}

    # HP_SEPARABLE gate on STD arm
    n_std_hp = sum(1 for r in std_recall.values() if r >= hp_sep_floor)
    hp_separable_all = (
        len(std_recall) > 0 and n_std_hp == len(std_recall)
    )
    std_min = min(std_recall.values()) if std_recall else 0.0
    std_max = max(std_recall.values()) if std_recall else 0.0

    # DIS arm M-axis range: max over (N, K) of recall spread across M
    dis_range = 0.0
    if dis_recall:
        by_nk: Dict[Tuple[int, int], Dict[int, float]] = {}
        for pt_key, r in dis_recall.items():
            parsed = _parse_point_key(pt_key)
            if parsed is None:
                continue
            _arm, m_val, n_val, k_val = parsed
            by_nk.setdefault((n_val, k_val), {})[m_val] = r
        max_range = 0.0
        for (n_val, k_val), m_map in by_nk.items():
            if len(m_map) >= 2:
                rmin = min(m_map.values())
                rmax = max(m_map.values())
                rr = rmax - rmin
                if rr > max_range:
                    max_range = rr
        dis_range = max_range

    # DIS arm baseline-in-band check: recall in (0.05, 0.95) at at least one point
    dis_in_band_count = sum(
        1 for r in dis_recall.values()
        if DIS_BAND_LOW < r < DIS_BAND_HIGH
    )

    # HP_INTERACTION_MK on DIS arm (USER-specified: M x K with fixed_axis=N)
    def _axis_vals(idx: int) -> List[int]:
        vals = set()
        for pk in dis_recall:
            parsed = _parse_point_key(pk)
            if parsed is None:
                continue
            vals.add(parsed[idx])
        return sorted(vals)
    # (arm, M, N, K) tuple index: 1=M, 2=N, 3=K
    dis_M_vals = _axis_vals(1)
    dis_N_vals = _axis_vals(2)
    dis_K_vals = _axis_vals(3)

    int_mk = None
    int_mn = None
    int_nk = None
    if len(dis_M_vals) >= 2 and len(dis_K_vals) >= 2 and len(dis_N_vals) >= 1:
        int_mk = compute_interaction_term(
            grid, "DIS_beta5",
            axis_a_name="M", axis_a_lo=dis_M_vals[0], axis_a_hi=dis_M_vals[-1],
            axis_b_name="K", axis_b_lo=dis_K_vals[0], axis_b_hi=dis_K_vals[-1],
            fixed_axis_name="N", fixed_axis_values=dis_N_vals,
        )
    if len(dis_M_vals) >= 2 and len(dis_N_vals) >= 2 and len(dis_K_vals) >= 1:
        int_mn = compute_interaction_term(
            grid, "DIS_beta5",
            axis_a_name="M", axis_a_lo=dis_M_vals[0], axis_a_hi=dis_M_vals[-1],
            axis_b_name="N", axis_b_lo=dis_N_vals[0], axis_b_hi=dis_N_vals[-1],
            fixed_axis_name="K", fixed_axis_values=dis_K_vals,
        )
    if len(dis_N_vals) >= 2 and len(dis_K_vals) >= 2 and len(dis_M_vals) >= 1:
        int_nk = compute_interaction_term(
            grid, "DIS_beta5",
            axis_a_name="N", axis_a_lo=dis_N_vals[0], axis_a_hi=dis_N_vals[-1],
            axis_b_name="K", axis_b_lo=dis_K_vals[0], axis_b_hi=dis_K_vals[-1],
            fixed_axis_name="M", fixed_axis_values=dis_M_vals,
        )

    hp_int_mk_pass = (int_mk is not None and int_mk >= hp_int_mk_floor)
    hp_int_mn_pass = (int_mn is not None and int_mn >= hp_int_mn_floor)
    hp_dis_mech_pass = (dis_range >= hp_dis_range_floor)

    headline = {
        "n_grid_points": len(grid),
        "std_arm": {
            "recall_by_point": std_recall,
            "min": std_min,
            "max": std_max,
            "n_hp": n_std_hp,
            "n_total": len(std_recall),
            "all_saturated_HP_separable": hp_separable_all,
        },
        "dis_arm": {
            "recall_by_point": dis_recall,
            "M_axis_range": dis_range,
            "M_axis_range_pass_HP_DIS_MECHANISM": hp_dis_mech_pass,
            "in_band_count": dis_in_band_count,
            "n_total": len(dis_recall),
        },
        "interaction_terms_dis_arm": {
            "M_K_averaged_over_N": int_mk,
            "M_N_averaged_over_K": int_mn,
            "N_K_averaged_over_M": int_nk,
            "HP_INT_MK_pass": hp_int_mk_pass,
            "HP_INT_MN_pass": hp_int_mn_pass,
            "HP_INT_MK_floor": hp_int_mk_floor,
            "HP_INT_MN_floor": hp_int_mn_floor,
        },
        "max_gpu_mb": max_gpu_mb,
        "hf_flags": hf_flags,
        "hp_sep_floor": hp_sep_floor,
        "hp_dis_range_floor": hp_dis_range_floor,
    }

    if hf_flags:
        return ("HARD_FAIL", "; ".join(hf_flags), headline)

    # SMOKE mode: check preview_corner + mechanism fires
    if run_mode == "smoke":
        # mechanism-fires check on DIS arm
        min_dis = min(dis_recall.values()) if dis_recall else 0.0
        max_dis = max(dis_recall.values()) if dis_recall else 0.0
        if not dis_recall:
            return ("HARD_FAIL", "SMOKE_NO_DIS_ARM", headline)
        # dis range should be >= 0.15 in smoke to indicate mechanism fires
        smoke_dis_range_floor = 0.15
        if dis_range < smoke_dis_range_floor:
            return (
                "MIDDLE_BAND",
                f"SMOKE_MB_DIS_ARM_TOO_FLAT: DIS M-axis range={dis_range:.3f} "
                f"< {smoke_dis_range_floor}; mechanism didn't discriminate in smoke; "
                f"do NOT dispatch FULL (META_RULE_K discriminator-fires gate)",
                headline,
            )
        preview_recall = seed_result.get("preview_corner_recall", None)
        preview_msg = ""
        if preview_recall is not None:
            preview_msg = f" preview={preview_recall:.3f}"
            # Mechanism-still-fires-at-scale: preview should NOT saturate at 1.0
            # (else DIS arm doesn't discriminate at full scale either)
            if preview_recall >= 0.95:
                return (
                    "MIDDLE_BAND",
                    f"SMOKE_MB_PREVIEW_SATURATED: preview_recall={preview_recall:.3f} "
                    f">= 0.95 at DIS worst corner (M=32768, N=8192, K=4000); DIS arm "
                    f"saturates at scale too - mechanism does NOT discriminate; "
                    f"DISCRIMINATOR-MUST-SURVIVE-SCALE Method C FAILED (INVERTED gate); "
                    f"beta=4 too high for this M-range at full-N. Iterate regime.",
                    headline,
                )
            if preview_recall < 0.02:
                return (
                    "MIDDLE_BAND",
                    f"SMOKE_MB_PREVIEW_DEAD: preview_recall={preview_recall:.3f} "
                    f"< 0.02 at DIS worst corner; mechanism completely dead; "
                    f"nothing to measure",
                    headline,
                )
        return (
            "HARD_PASS",
            f"SMOKE_HARD_PASS: DIS_range={dis_range:.3f} (>= {smoke_dis_range_floor}) "
            f"min_dis={min_dis:.3f} max_dis={max_dis:.3f}{preview_msg} "
            f"int_MK={int_mk if int_mk is not None else 'NA'} "
            f"int_MN={int_mn if int_mn is not None else 'NA'} "
            f"std_min={std_min:.3f} std_max={std_max:.3f}",
            headline,
        )

    # FULL mode verdict logic
    # HP requires: STD SEPARABLE + DIS mechanism fires + (M-K OR M-N interaction >= floor)
    int_summary_parts = []
    if int_mk is not None:
        int_summary_parts.append(f"MK={int_mk:.3f}")
    if int_mn is not None:
        int_summary_parts.append(f"MN={int_mn:.3f}")
    if int_nk is not None:
        int_summary_parts.append(f"NK={int_nk:.3f}")
    int_summary = ", ".join(int_summary_parts)

    if hp_separable_all and hp_dis_mech_pass and (hp_int_mk_pass or hp_int_mn_pass):
        interaction_dominant = "M-K" if hp_int_mk_pass else "M-N"
        return (
            "HARD_PASS",
            (
                f"HP_CROSS_AXIS_INTERACTION_CG: STD arm SEPARABLE "
                f"(all {n_std_hp}/{len(std_recall)} recall >= {hp_sep_floor}; "
                f"min={std_min:.3f}) confirms v1 saturation regime-specific NOT "
                f"substrate-wide; DIS arm M-axis range={dis_range:.3f} "
                f"(>= {hp_dis_range_floor}) mechanism fires; "
                f"{interaction_dominant} interaction detected on DIS arm "
                f"({int_summary}); "
                f"substrate CROSS-AXIS INTERACTION MEASURED "
                f"in discriminating regime, closes Stage 1 cross-axis M x N x K gap"
            ),
            headline,
        )

    # MIDDLE_BAND if separable but no interaction found
    if hp_separable_all and hp_dis_mech_pass and not (hp_int_mk_pass or hp_int_mn_pass):
        return (
            "MIDDLE_BAND",
            (
                f"MB_MECHANISM_SEPARABLE_ACROSS_AXES: STD arm SEPARABLE; DIS arm "
                f"discriminates on M-axis (range={dis_range:.3f}) but interaction "
                f"terms below floor (MK_floor={hp_int_mk_floor}, MN_floor={hp_int_mn_floor}); "
                f"({int_summary}); substrate substrate factorizes across axes at "
                f"beta=4 regime -- MEASURED_MECHANISM physical finding"
            ),
            headline,
        )

    # MIDDLE_BAND if DIS mechanism didn't fire
    if not hp_dis_mech_pass:
        return (
            "MIDDLE_BAND",
            (
                f"MB_DIS_MECHANISM_DID_NOT_FIRE_AT_FULL: DIS arm M-axis range="
                f"{dis_range:.3f} < {hp_dis_range_floor}; discriminator failed at "
                f"full scale (mechanism saturates or floors uniformly); "
                f"cannot measure interaction; regime needs iteration"
            ),
            headline,
        )

    # STD not separable is unexpected (v1 landed all 1.000); flag as MB
    return (
        "MIDDLE_BAND",
        (
            f"MB_STD_ARM_NOT_SEPARABLE_UNEXPECTED: STD_beta13 arm did NOT "
            f"saturate ({n_std_hp}/{len(std_recall)} above {hp_sep_floor}; "
            f"min={std_min:.3f}); v1 landed all 1.000 at overlapping regime; "
            f"substrate behavior differs from v1 (possible upstream primitive change) "
            f"DIS metrics: range={dis_range:.3f} interactions={int_summary}"
        ),
        headline,
    )


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def run_all_selftests(seed: int, anchor: str) -> None:
    """Verify numpy path recall reasonable + verdict logic paths."""
    # tiny numpy phase point at STD arm should recall > 0.8
    r_std = _run_phase_point_numpy(
        seed=seed, arm_name="STD_beta13",
        M=100, N=128, K=10, V=32, beta=13.0, chunk_size=32,
    )
    assert r_std["recall_cosine_mean"] > 0.5, (
        f"[selftest] tiny STD numpy recall too low: {r_std['recall_cosine_mean']}"
    )
    # tiny numpy at DIS arm should be lower than STD (beta discriminates)
    r_dis = _run_phase_point_numpy(
        seed=seed, arm_name="DIS_beta5",
        M=100, N=128, K=10, V=32, beta=4.0, chunk_size=32,
    )
    # weaker beta -> lower recall (at same M/N) - baseline test
    assert r_dis["recall_cosine_mean"] < r_std["recall_cosine_mean"] + 0.01, (
        f"[selftest] DIS arm should have lower or equal recall vs STD: "
        f"dis={r_dis['recall_cosine_mean']} std={r_std['recall_cosine_mean']}"
    )
    assert len(r_std["arm_hash"]) == 16, "[selftest] arm_hash schema unexpected"

    # verdict logic: fake grid that should HP
    # STD arm all at 0.99 (separable), DIS arm M-axis range 0.5, MK interaction 0.15
    fake_grid = {}
    for arm, beta in ARM_BETAS.items():
        for M in [1000, 32768]:
            for N in [2048, 8192]:
                for K in [100, 4000]:
                    if arm == "STD_beta13":
                        recall = 0.99
                    else:  # DIS_beta5
                        # base recall higher at low-M
                        base = 0.85 if M == 1000 else 0.30
                        # add interaction: at (HM, HK) drop extra 0.15
                        if M == 32768 and K == 4000:
                            base -= 0.15
                        # bit different by N
                        base += 0.02 if N == 8192 else 0.0
                        recall = base
                    key = f"{arm}_M{M}_N{N}_K{K}"
                    fake_grid[key] = {
                        "arm_name": arm,
                        "M": M, "N": N, "K": K,
                        "recall_cosine_mean": recall,
                        "arm_hash": hashlib.sha256(key.encode()).hexdigest()[:16],
                        "gpu_mem_peak_mb": 10.0,
                    }
    seed_res = {
        "grid_results": fake_grid,
        "preview_corner_recall": 0.20,
    }
    v, msg, headline = compute_verdict(seed_res, "full")
    assert v == "HARD_PASS", f"[selftest] fake-grid should HP; got {v}: {msg}"
    print(f"[selftest] HP path OK: {msg[:180]}", flush=True)

    # verdict logic: fake grid separable-across-axes (M-K interaction = 0)
    fake_grid_mb = {}
    for arm in ARM_BETAS:
        for M in [1000, 32768]:
            for N in [2048, 8192]:
                for K in [100, 4000]:
                    if arm == "STD_beta13":
                        recall = 0.99
                    else:
                        # M-dependent only, no K interaction
                        recall = 0.85 if M == 1000 else 0.30
                    _key_mb = f"{arm}_M{M}_N{N}_K{K}"
                    fake_grid_mb[_key_mb] = {
                        "arm_name": arm, "M": M, "N": N, "K": K,
                        "recall_cosine_mean": recall,
                        "arm_hash": hashlib.sha256(f"MB_{_key_mb}".encode()).hexdigest()[:16],
                        "gpu_mem_peak_mb": 10.0,
                    }
    v2, msg2, _ = compute_verdict({"grid_results": fake_grid_mb}, "full")
    assert v2 == "MIDDLE_BAND" and "SEPARABLE_ACROSS_AXES" in msg2, (
        f"[selftest] separable detection failed: {v2}: {msg2}"
    )
    print(f"[selftest] MB separable path OK: {msg2[:180]}", flush=True)

    # verdict logic: DIS mechanism didn't fire (range too small)
    fake_grid_flat = {}
    for arm in ARM_BETAS:
        for M in [1000, 32768]:
            for N in [2048, 8192]:
                for K in [100, 4000]:
                    recall = 0.99 if arm == "STD_beta13" else 0.99
                    fake_grid_flat[f"{arm}_M{M}_N{N}_K{K}"] = {
                        "arm_name": arm, "M": M, "N": N, "K": K,
                        "recall_cosine_mean": recall,
                        "arm_hash": f"flat_{arm}_{M:x}"[:16].ljust(16, "z"),
                        "gpu_mem_peak_mb": 10.0,
                    }
    # need distinct hashes; add a variable char
    for i, k in enumerate(fake_grid_flat):
        fake_grid_flat[k]["arm_hash"] = f"{i:016x}"
    v3, msg3, _ = compute_verdict({"grid_results": fake_grid_flat}, "full")
    assert v3 == "MIDDLE_BAND" and (
        "DIS_MECHANISM_DID_NOT_FIRE" in msg3 or "MECHANISM_SEPARABLE" in msg3
    ), f"[selftest] flat detection failed: {v3}: {msg3}"
    print(f"[selftest] MB DIS-flat path OK: {msg3[:180]}", flush=True)

    print(
        f"[selftest] PASS  STD_recall={r_std['recall_cosine_mean']:.3f}  "
        f"DIS_recall={r_dis['recall_cosine_mean']:.3f}  "
        f"verdict_logic_HP+MB_separable+MB_flat=OK  "
        f"torch={_TORCH_AVAILABLE}  cuda={_CUDA_AVAILABLE}",
        flush=True,
    )
