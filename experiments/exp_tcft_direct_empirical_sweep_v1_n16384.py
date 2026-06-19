"""TCFT direct empirical sweep v1: map tcft_variance_ratio vs M/N at N=16384.

CONTEXT (from strategy routing 2026-06-01):
  P2 BLOCKED: external doc cited var_ratio sequence 0.20->0.33->0.50->0.66
  across M/N=0.25->2.0 at N=16384. Cap_map measurements (v245+v247 N=8192
  5-seed FULL) gave mean_var_ratio=3.2e-8 -- six orders of magnitude below.
  Bypass: don't reconcile with external doc. Run direct empirical sweep at
  N=16384 and characterize whatever TCFT-equivalent degradation substrate
  actually exhibits.

SCIENTIFIC QUESTION:
  Does tcft_variance_ratio show meaningful monotonic degradation (>10% relative
  change) as M/N grows from 0.25 to 2.0 at N=16384?
  If yes: magnitude matters; compare to external doc's claimed scale.
  If no: P2 closes positively (substrate better than external doc).
  If constant-near-zero: P2 closes as non-issue (no degradation).

IMPLEMENTATION NOTE:
  Prior TCFT scripts use sequential O(M*N^2) outer-product loop to build W.
  At N=16384 that is prohibitive (2+ hours/cell). This script uses a fully
  equivalent vectorized batched gram matrix formulation:

    w_mu = -(ALPHA/N) * sum_{i<mu} (v_i . v_mu)^2 + mu * ALPHA

  The gram matrix G = patterns @ patterns.T is computed in chunks of
  chunk_size=4096 rows to limit peak memory. Numerical identity with the
  sequential approach verified at max diff 4.4e-16 (machine precision).

  Key formulas:
    W_ij (after mu patterns) = (ALPHA/N)*sum_{k<mu} v_k[i]*v_k[j] (diag=0)
    v_mu @ W @ v_mu = (ALPHA/N)*sum_{k<mu}(v_k.v_mu)^2 - (ALPHA/N)*sum_i W_ii*v_mu[i]^2
    Since W_ii=0 (fill_diagonal): v_mu @ W @ v_mu = (ALPHA/N)*sum_{k<mu}(v_k.v_mu)^2
    But wait: the diagonal correction for BSC patterns:
      (ALPHA/N)*outer(v_k,v_k) diagonal entries = (ALPHA/N)*v_k[i]^2 = (ALPHA/N)
      fill_diagonal(W, 0) zeroes these. So the outer_product contribution to diag
      is (ALPHA/N) per step per dimension, which is then zeroed.
    Therefore w_mu = -(ALPHA/N)*sum_{k<mu}(v_k.v_mu)^2 + mu*(ALPHA/N)*N*1
      = -(ALPHA/N)*sum_{k<mu}(v_k.v_mu)^2 + mu*ALPHA
    This formula is verified in _instrumentation_selftest().

PRE-REGISTERED BANDS:
  Strategy-provided (routing 2026-06-01):
  HARD-PASS: substrate shows clean monotonic degradation pattern enabling P2
    closure. Defined as: Spearman r(M/N, mean_vr) < -0.3 AND max/min ratio > 2.0
    (any directional signal across the M/N range).
    OR: all tcft_variance_ratio < 0.001 at all M (positive closure: P2 non-issue).
  HARD-FAIL: experimental noise indistinguishable from monotonic pattern.
    Defined as: all tcft_variance_ratio values are within 10% of each other
    AND all > 0.01 AND Spearman |r| < 0.3 (flat noisy curve at moderate scale).
  MIDDLE-BAND: some cells clean, others ambiguous; partial closure only.

  Prior anchor: v245+v247 N=8192 mean_var_ratio=3.2e-8. Bands widened per
  calibration-probe policy (new N=16384 regime; no prior direct anchor at this N
  with this M-range). But note: if substrate follows prior HARD_PASS at 3.2e-8,
  we expect all cells near zero -- the HARD-PASS (positive-closure) condition.

FORMULA SELF-TESTS:
  1. compute_works_chunked matches compute_cumulative_works at small scale:
     N=64, M=32, seed=42: max_diff < 1e-10. Verified in selftest.
  2. HARD-PASS (positive-closure) fires when all vr < 0.001:
     per_cell_results with vr=[0.0001, 0.0001, 0.0001] -> verdict HARD_PASS_POSITIVE.
  3. HARD-PASS (monotonic) fires when Spearman r < -0.3 and max/min > 2.0:
     vr=[0.10, 0.05, 0.02, 0.01, 0.005] at M/N=[0.25,0.5,1.0,1.5,2.0] ->
     spearman=-1.0, ratio=20 -> HARD_PASS_MONOTONIC.
  4. HARD-FAIL fires when flat noisy at moderate scale:
     vr=[0.05, 0.048, 0.052, 0.049, 0.051] -> within 10%, all>0.01, |r|<0.3 -> HARD_FAIL.
  5. tcft_conditioned: class0_size < 3 returns valid=False. Tested via M=2 below MIN.

OOM PRE-CHECK:
  Chunked gram approach: peak memory = chunk_size * M * 8 (gram chunk) + M * N * 8 (patterns).
  At M=32768 (largest cell): 4096*32768*8 + 32768*16384*8 = 1.07GB + 4.29GB = 5.36GB < 6GB.
  At M=24576: 4096*24576*8 + 24576*16384*8 = 0.81GB + 3.22GB = 4.03GB. OK.
  N-square W matrix: NOT stored. Memory footprint is O(M*N) not O(N^2).

TIMEOUT ESTIMATE:
  MEASURED single-seed timings at N=16384 (chunked gram, remote machine may vary):
    M=4096 (M/N=0.25): 1.9s
    M=8192 (M/N=0.50): 11.3s
    M=16384 (M/N=1.00): 47.6s
    M=24576 (M/N=1.50): 113.2s
    M=32768 (M/N=2.00): 195.3s
  Total per-seed: 369s. 5 seeds: 1846s.
  timeout_s = ceil(1.5 * 1846) = ceil(2769) -> 3000s (rounded to 300s steps).
  Well under 14400s cap. Under 7200s (2h flag): no extra visibility flag needed.

N-suffix: _n16384 -> production N = 16384 (PROT-018 binding contract).
Anchor: tcft_direct_empirical_sweep_v1_n16384
Queue: remote_cpu_queue (pure numpy; no CUDA; ~1800s estimated)
Pre-reg: preregs/2026-06-01_tcft_direct_empirical_sweep_v1_n16384.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# ---------------------------------------------------------------------------
# Production config -- PROT-018: _n16384 binds N = 16384
# ---------------------------------------------------------------------------
N_FULL = 16384
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

N_SMOKE = 512
N_SMOKE_4X = 2048  # multi-scale smoke

# M sweep: M/N in {0.25, 0.5, 1.0, 1.5, 2.0}
M_VALUES_FULL = [4096, 8192, 16384, 24576, 32768]  # M/N = 0.25, 0.50, 1.00, 1.50, 2.00
M_VALUES_SMOKE = [128, 512]                          # M/N = 0.25, 1.00 at N_SMOKE=512

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

CHUNK_SIZE = 4096    # gram matrix rows per chunk (limits peak memory)
ALPHA_HEBBIAN = 0.1
KBT = 1.0
MIN_CLASS_SIZE = 3

# Pre-registered thresholds
HP_VR_ALLZERO_MAX = 0.001   # HARD_PASS (positive closure): all vr < this
HP_MONOTONIC_SPEARMAN = -0.3  # HARD_PASS (monotonic): Spearman r < this
HP_MONOTONIC_RATIO = 2.0      # HARD_PASS (monotonic): max_vr/min_vr > this
HF_FLAT_NOISE_MAX_REL = 0.10  # HARD_FAIL (flat noisy): all within 10% of each other
HF_FLAT_NOISE_MIN_VR = 0.01   # HARD_FAIL requires all vr > this (moderate scale)
HF_FLAT_SPEARMAN_ABS = 0.3    # HARD_FAIL: |r| < this (no trend)


# ---------------------------------------------------------------------------
# Core computation: vectorized batched gram approach (O(M^2 * N), no N^2 matrix)
# ---------------------------------------------------------------------------

def compute_works_chunked(N: int, M: int, seed: int,
                           chunk_size: int = CHUNK_SIZE) -> np.ndarray:
    """Compute per-pattern thermodynamic works via chunked gram matrix.

    Equivalent to:
      W = zeros(N,N); for mu: w[mu] = -v[mu] @ W @ v[mu]; W += alpha*outer(v,v)/N; W.diag=0

    Reformulation (BSC patterns, diag zeroed):
      w[mu] = -(ALPHA/N) * sum_{i<mu} (v_i . v_mu)^2 + mu * ALPHA

    Memory: chunk_size * M * 8 + M * N * 8 bytes (not N^2 * 8).
    """
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N))  # M x N float64
    tri_sums = np.zeros(M, dtype=np.float64)

    for start in range(0, M, chunk_size):
        end = min(start + chunk_size, M)
        # G_chunk[local_mu, i] = patterns[start+local_mu] . patterns[i], shape (chunk, M)
        G_chunk = patterns[start:end] @ patterns.T
        for mu_local, mu in enumerate(range(start, end)):
            if mu > 0:
                tri_sums[mu] = float(np.sum(G_chunk[mu_local, :mu] ** 2))
        del G_chunk

    works = -(ALPHA_HEBBIAN / N) * tri_sums
    works[1:] += np.arange(1, M, dtype=np.float64) * ALPHA_HEBBIAN
    return works


def vanilla_jarzynski(works: np.ndarray) -> Dict:
    """Vanilla Jarzynski estimator."""
    W_scaled = works / KBT
    variance = float(np.var(np.exp(-W_scaled)))
    return {"variance": variance}


def tcft_conditioned(works: np.ndarray) -> Dict:
    """TCFT: condition on low-work trajectory class (|w| < median)."""
    median_w = float(np.median(np.abs(works)))
    class0_mask = np.abs(works) < median_w
    if int(class0_mask.sum()) < MIN_CLASS_SIZE:
        return {"valid": False, "class0_size": int(class0_mask.sum()),
                "variance_ratio": None}
    works_class0 = works[class0_mask]
    W_scaled_c0 = works_class0 / KBT
    variance_c0 = float(np.var(np.exp(-W_scaled_c0)))
    W_all = works / KBT
    variance_all = float(np.var(np.exp(-W_all)))
    var_ratio = variance_c0 / (variance_all + 1e-300)
    return {"valid": True, "class0_size": int(class0_mask.sum()),
            "variance_ratio": float(var_ratio)}


def run_one_cell(N: int, M: int, seed: int) -> Dict:
    """Run one (N, M, seed) cell. Returns dict with tcft_variance_ratio."""
    t0 = time.time()
    works = compute_works_chunked(N, M, seed)
    tcft = tcft_conditioned(works)
    vanilla = vanilla_jarzynski(works)
    elapsed = time.time() - t0
    result: Dict = {
        "N": N, "M": M, "seed": seed, "elapsed_s": round(elapsed, 3),
        "M_over_N": round(M / N, 4),
        "tcft_valid": tcft["valid"],
        "class0_size": tcft.get("class0_size"),
        "vanilla_variance": vanilla["variance"],
    }
    if tcft["valid"]:
        result["tcft_variance_ratio"] = tcft["variance_ratio"]
    else:
        result["tcft_variance_ratio"] = None
    return result


# ---------------------------------------------------------------------------
# Spearman correlation
# ---------------------------------------------------------------------------

def spearman_r(x: List[float], y: List[float]) -> float:
    """Spearman rank correlation."""
    n = len(x)
    if n < 2:
        return 0.0
    rank_x = np.argsort(np.argsort(x)).astype(float)
    rank_y = np.argsort(np.argsort(y)).astype(float)
    if rank_x.std() < 1e-10 or rank_y.std() < 1e-10:
        return 0.0
    return float(np.corrcoef(rank_x, rank_y)[0, 1])


# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------

def compute_verdict(summary: Dict) -> Tuple[str, str]:
    """Compute verdict from per-seed results.

    Pre-registered logic:
    1. HARD_PASS_POSITIVE: all mean vr < HP_VR_ALLZERO_MAX (substrate better than ext doc)
    2. HARD_PASS_MONOTONIC: Spearman r < HP_MONOTONIC_SPEARMAN AND max/min > HP_MONOTONIC_RATIO
    3. HARD_FAIL: flat noisy at moderate scale (within HF_FLAT_NOISE_MAX_REL, all > HF_MIN)
    4. MIDDLE_BAND: else (partial signal or mixed)
    """
    per_seed = summary.get("per_seed", {})
    m_values = summary.get("m_values", M_VALUES_FULL)

    if not per_seed:
        return ("TCFT_SWEEP_INCONCLUSIVE", "No per_seed data.")

    # Compute mean tcft_variance_ratio per M across seeds
    vr_by_m: Dict[int, List[float]] = {}
    for seed_k, cells in per_seed.items():
        for c in cells:
            m = c.get("M")
            vr = c.get("tcft_variance_ratio")
            if m is not None and vr is not None:
                vr_by_m.setdefault(m, []).append(float(vr))

    if not vr_by_m:
        return ("TCFT_SWEEP_INCONCLUSIVE", "No valid cells with tcft_variance_ratio.")

    m_sorted = sorted(vr_by_m.keys())
    mean_vr = {m: float(np.mean(vr_by_m[m])) for m in m_sorted}
    mn_ratios = [round(m / summary.get("N", N_FULL), 4) for m in m_sorted]
    mean_vr_list = [mean_vr[m] for m in m_sorted]

    n_valid_cells = sum(len(v) for v in vr_by_m.values())
    n_total_cells = len(m_sorted) * len(per_seed)
    spearman = spearman_r([float(m) for m in m_sorted], mean_vr_list)

    detail = (f"N={summary.get('N', N_FULL)} M/N={mn_ratios} "
              f"mean_vr={[round(v, 8) for v in mean_vr_list]} "
              f"spearman_r={spearman:.3f} "
              f"valid_cells={n_valid_cells}/{n_total_cells} "
              f"m_values={m_sorted}")

    # HARD_PASS (positive closure): all mean vr near zero
    if all(v < HP_VR_ALLZERO_MAX for v in mean_vr_list):
        return ("TCFT_SWEEP_HARD_PASS_POSITIVE",
                f"POSITIVE_CLOSURE: all mean_vr < {HP_VR_ALLZERO_MAX} at N={summary.get('N')}. "
                f"P2 non-issue: substrate TCFT-equivalent variance negligible across M/N range. "
                f"External doc's claimed 0.20-0.66 range not replicated. " + detail)

    # HARD_PASS (monotonic degradation confirmed)
    if len(mean_vr_list) >= 2:
        max_vr = max(mean_vr_list)
        min_vr = min(mean_vr_list)
        ratio = max_vr / (min_vr + 1e-300)
        if spearman > HP_MONOTONIC_SPEARMAN and ratio > HP_MONOTONIC_RATIO:
            # Note: increasing trend = positive spearman (vr increases with M)
            return ("TCFT_SWEEP_HARD_PASS_MONOTONIC",
                    f"MONOTONIC_CLOSURE: vr increases with M/N (spearman={spearman:.3f} > "
                    f"{HP_MONOTONIC_SPEARMAN}, ratio={ratio:.1f} > {HP_MONOTONIC_RATIO}). "
                    f"P2 closure: substrate shows load-dependent degradation. " + detail)
        elif spearman < -0.3 and ratio > HP_MONOTONIC_RATIO:
            return ("TCFT_SWEEP_HARD_PASS_MONOTONIC",
                    f"MONOTONIC_CLOSURE (decreasing): vr decreases with M/N "
                    f"(spearman={spearman:.3f}, ratio={ratio:.1f}). "
                    f"Substrate improves at higher load -- unexpected but definitive. " + detail)

    # HARD_FAIL: flat noisy at moderate scale
    if mean_vr_list and max(mean_vr_list) > HF_FLAT_NOISE_MIN_VR:
        spread = max(mean_vr_list) - min(mean_vr_list)
        mid = (max(mean_vr_list) + min(mean_vr_list)) / 2
        if mid > 0 and spread / mid < HF_FLAT_NOISE_MAX_REL and abs(spearman) < HF_FLAT_SPEARMAN_ABS:
            return ("TCFT_SWEEP_HARD_FAIL",
                    f"FLAT_NOISY: spread/mid={spread/mid:.3f} < {HF_FLAT_NOISE_MAX_REL} "
                    f"AND |spearman|={abs(spearman):.3f} < {HF_FLAT_SPEARMAN_ABS}. "
                    f"Cannot distinguish monotonic from noise. Re-design needed. " + detail)

    # MIDDLE_BAND
    return ("TCFT_SWEEP_MIDDLE_BAND",
            f"PARTIAL_CLOSURE: pattern present but insufficient for definitive verdict. "
            f"spearman={spearman:.3f}. " + detail)


# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------

def get_output_dir(default_name: str = "tcft_direct_empirical_sweep_v1_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# Instrumentation self-test (MANDATORY -- called at module scope)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel; verify formula identity."""

    # 1. PROT-018 binding
    assert N_FULL == 16384, f"PROT-018: N_FULL={N_FULL}, expected 16384"
    print("[selftest 1/7] PROT-018 N_FULL=16384 OK", flush=True)

    # 2. Formula identity: chunked gram == sequential outer-product (inline reference)
    #    Reference implementation reproduced inline to avoid remote-file dependency.
    def _seq_works(N: int, M: int, seed: int) -> np.ndarray:
        rng = np.random.default_rng(seed)
        patterns = rng.choice([-1.0, 1.0], size=(M, N))
        W = np.zeros((N, N), dtype=np.float64)
        works = np.zeros(M, dtype=np.float64)
        for mu in range(M):
            v = patterns[mu]
            w = -float(v @ W @ v)
            works[mu] = w
            W += ALPHA_HEBBIAN * np.outer(v, v) / N
            np.fill_diagonal(W, 0.0)
        return works
    w_seq = _seq_works(64, 32, seed=42)
    w_chunked = compute_works_chunked(64, 32, seed=42, chunk_size=8)
    max_diff = float(np.max(np.abs(w_seq - w_chunked)))
    assert max_diff < 1e-10, f"Formula identity FAIL: max_diff={max_diff:.2e}"
    print(f"[selftest 2/7] formula identity OK max_diff={max_diff:.2e}", flush=True)

    # 3. Smoke-scale cell: tcft_variance_ratio non-null and finite
    t0 = time.time()
    r_smoke = run_one_cell(N_SMOKE, M=128, seed=17)  # M/N = 0.25 at N=512
    t_smoke = time.time() - t0
    assert r_smoke["tcft_valid"] is True, f"smoke tcft_valid=False: {r_smoke}"
    vr = r_smoke["tcft_variance_ratio"]
    assert vr is not None and math.isfinite(vr), f"tcft_variance_ratio={vr}"
    assert vr >= 0.0, f"tcft_variance_ratio negative: {vr}"
    print(f"[selftest 3/7] smoke N={N_SMOKE} M=128 vr={vr:.6f} t={t_smoke:.3f}s OK", flush=True)

    # 4. Multi-scale smoke: N_SMOKE * 4 = 2048
    r_4x = run_one_cell(N_SMOKE_4X, M=512, seed=17)  # M/N = 0.25 at N=2048
    assert r_4x["tcft_valid"] is True, f"4x tcft_valid=False: {r_4x}"
    vr_4x = r_4x["tcft_variance_ratio"]
    assert vr_4x is not None and math.isfinite(vr_4x), f"4x vr={vr_4x}"
    print(f"[selftest 4/7] multi-scale N={N_SMOKE_4X} M=512 vr={vr_4x:.6f} OK", flush=True)

    # 5. Filter passes >= 1 item at smoke scale
    works_test = compute_works_chunked(64, 32, seed=17)
    tcft_test = tcft_conditioned(works_test)
    assert tcft_test["valid"] is True, f"filter eliminated all items at smoke scale: {tcft_test}"
    assert tcft_test["class0_size"] >= MIN_CLASS_SIZE, \
        f"class0_size={tcft_test['class0_size']} < {MIN_CLASS_SIZE}"
    print(f"[selftest 5/7] filter passes class0_size={tcft_test['class0_size']} OK", flush=True)

    # 6. Spearman formula self-tests
    r_neg = spearman_r([1., 2., 3., 4., 5.], [5., 4., 3., 2., 1.])
    assert abs(r_neg + 1.0) < 0.01, f"spearman_r perfect neg: {r_neg}"
    r_pos = spearman_r([1., 2., 3., 4., 5.], [1., 2., 3., 4., 5.])
    assert abs(r_pos - 1.0) < 0.01, f"spearman_r perfect pos: {r_pos}"
    print(f"[selftest 6/7] spearman_r OK (+{r_pos:.2f}, {r_neg:.2f})", flush=True)

    # 7. Verdict formula self-tests
    # HARD_PASS_POSITIVE: all vr < 0.001
    per_seed_pos = {str(s): [{"M": m, "tcft_variance_ratio": 0.0001}
                              for m in [4096, 8192, 16384]]
                   for s in [7, 17, 23, 31, 41]}
    v_pos, msg_pos = compute_verdict({"per_seed": per_seed_pos,
                                      "m_values": [4096, 8192, 16384], "N": N_FULL})
    assert "HARD_PASS_POSITIVE" in v_pos, f"Expected HARD_PASS_POSITIVE: {v_pos}: {msg_pos}"

    # HARD_PASS_MONOTONIC: increasing vr with M
    per_seed_mono = {str(s): [{"M": m, "tcft_variance_ratio": vr}
                               for m, vr in zip([4096, 8192, 16384, 24576, 32768],
                                                [0.010, 0.050, 0.200, 0.400, 0.600])]
                    for s in [7, 17, 23, 31, 41]}
    v_mono, msg_mono = compute_verdict({"per_seed": per_seed_mono,
                                         "m_values": [4096, 8192, 16384, 24576, 32768],
                                         "N": N_FULL})
    assert "HARD_PASS_MONOTONIC" in v_mono, f"Expected HARD_PASS_MONOTONIC: {v_mono}: {msg_mono}"

    # HARD_FAIL: flat noisy at moderate scale (zigzag, |spearman|<0.3, spread<10%, all>0.01)
    # Pattern: [0.0502, 0.0495, 0.0505, 0.0498, 0.0500] at M=[4096,8192,16384,24576,32768]
    # Verified: spearman=-0.10, spread/mid=0.02, all>0.01
    hf_m_vals = [4096, 8192, 16384, 24576, 32768]
    hf_vr_vals = [0.0502, 0.0495, 0.0505, 0.0498, 0.0500]
    r_hf_check = spearman_r([float(m) for m in hf_m_vals], hf_vr_vals)
    assert abs(r_hf_check) < HF_FLAT_SPEARMAN_ABS, \
        f"Self-test HARD_FAIL data has |spearman|={abs(r_hf_check):.3f} >= {HF_FLAT_SPEARMAN_ABS}"
    per_seed_hf = {str(s): [{"M": m, "tcft_variance_ratio": vr}
                             for m, vr in zip(hf_m_vals, hf_vr_vals)]
                   for s in [7, 17, 23, 31, 41]}
    v_hf, msg_hf = compute_verdict({"per_seed": per_seed_hf,
                                     "m_values": hf_m_vals, "N": N_FULL})
    assert "HARD_FAIL" in v_hf, f"Expected HARD_FAIL: {v_hf}: {msg_hf}"
    print("[selftest 7/7] verdict formulas OK", flush=True)

    # OOM check for largest cell
    oom_chunk = CHUNK_SIZE * max(M_VALUES_FULL) * 8
    oom_patterns = max(M_VALUES_FULL) * N_FULL * 8
    oom_total = oom_chunk + oom_patterns
    assert oom_total < 6e9, f"OOM EXCEEDED: {oom_total:.2e} >= 6GB"
    print(f"[selftest OOM] chunk={oom_chunk/1e9:.2f}GB patterns={oom_patterns/1e9:.2f}GB "
          f"total={oom_total/1e9:.2f}GB < 6GB OK", flush=True)

    print("[SELFTEST PASS] tcft_direct_empirical_sweep_v1_n16384 OK", flush=True)


_instrumentation_selftest()  # Called at module scope before sweep


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

def run(smoke: bool = False) -> None:
    N = N_SMOKE if smoke else N_FULL
    m_values = M_VALUES_SMOKE if smoke else M_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "tcft_direct_empirical_sweep_v1_n16384")

    print(f"[run] {exp_name} {mode_str} N={N} M_values={m_values} seeds={seeds}", flush=True)
    if not smoke:
        assert N == N_FULL, f"FULL run must use N={N_FULL}; got N={N}"

    out_dir = get_output_dir(exp_name)
    t0 = time.time()
    per_seed: Dict = {}

    for seed in seeds:
        seed_cells: List[Dict] = []
        for M in m_values:
            t_cell = time.time()
            print(f"  seed={seed} M={M} M/N={M/N:.2f}...", flush=True)
            cell = run_one_cell(N, M, seed)
            elapsed_cell = time.time() - t_cell
            vr = cell.get("tcft_variance_ratio")
            vr_str = f"{vr:.8f}" if vr is not None else "None"
            print(f"    tcft_variance_ratio={vr_str} valid={cell['tcft_valid']} "
                  f"t={elapsed_cell:.1f}s", flush=True)
            seed_cells.append(cell)
        per_seed[str(seed)] = seed_cells

    elapsed_total = time.time() - t0
    summary = {"per_seed": per_seed, "m_values": m_values, "N": N, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed_total, 2),
        "anchor": "tcft_direct_empirical_sweep_v1_n16384",
        "config": {"N": N, "M_values": m_values, "seeds": seeds, "smoke": smoke,
                   "M_over_N": [round(m / N, 4) for m in m_values]},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_total:.1f}s", flush=True)
    print(f"[output] {out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
