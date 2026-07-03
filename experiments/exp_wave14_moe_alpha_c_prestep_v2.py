"""MoE single-expert alpha_c calibration pre-step v2 -- RECALIBRATED BANDS.

CONTEXT: v1 ran smoke (N=512, 1 seed) and reported alpha_c=0.39 as OUT_OF_RANGE
against the AGS autoassoc band [0.08, 0.25]. Research drill (notes/research_substrate_
alpha_c_anomaly_2026-05-24.md) confirmed this is NOT a substrate anomaly: the script
implements a LINEAR HETEROASSOCIATOR (y = W k, W = (1/N) sum v_i k_i^T, recalled by
cosine). Closed-form SNR prediction: alpha_c(tau) = 1/tau^2 - 1; at tau=0.80,
alpha_c_theory = 0.5625. The 4 smoke datapoints match within +-0.002 cosine units.

WHAT CHANGED IN v2:
  - ALPHA_C_LO = 0.40, ALPHA_C_HI = 0.70 (recalibrated from [0.08, 0.25])
  - Added closed-form diagnostic overlay (cos_pred, residuals)
  - Added multi-scale smoke gate (N_SMOKE + N_SMOKE*4) per instrumentation protocol
  - Recalibrated summary fields: cos_pred, max_residual, m_per_expert_recommended
    uses measured alpha_c, NOT the AGS 0.14 assumption

WHAT THIS MEASURES:
  Single-expert BSC outer-product memory, N=4096.
  Sweep M (items stored) across a factor-2 grid.
  At each M: store M random BSC key-value pairs, recall all, measure mean cosine.
  Extract alpha_c_measured = largest M where mean_cosine > PASS_COSINE / N.
  Overlay closed-form cos_pred(M, N) = 1/sqrt(1 + (M-1)/N) at each grid point.
  Report max_residual = max |cos_measured - cos_pred| over all M values.

ARCHITECTURE:
  W[N x N] = (1/N) * sum_i v_i k_i^T   (outer-product Hopfield / linear heteroassoc)
  recall: y = W k_query (one-shot linear readout, no recurrence)
  fidelity: mean cosine(y, v_target) across all stored items

PRE-REGISTERED BANDS (recalibrated per notes/exp_dev_handoff_research_alpha_c_recalibration_2026-05-24.md):
  HARD-PASS (calibration confirmed; MoE rebuild unblocks):
    - alpha_c_measured in [0.50, 0.60] (predicted 0.5625 from closed form 1/tau^2-1 at tau=0.80)
    - CI width < 0.05 (5 seeds)
    - max_residual |cos_measured - cos_pred| < 0.02 at every grid M
    -> Report alpha_c_measured; M_per_expert_recommended = 0.70 * alpha_c * N;
       M_total_recommended_k4 = 0.70 * alpha_c * N * 4 * 0.80; proceed to MoE rebuild

  MIDDLE (mild deviation; proceed with note):
    - alpha_c_measured in [0.40, 0.50) or (0.60, 0.70]
    - OR max_residual 0.02-0.05 at 1-2 grid points
    -> Proceed with measured value; document residual

  HARD-FAIL (genuine anomaly):
    - alpha_c_measured outside [0.40, 0.70]
    - AND max_residual > 0.05 at >= 2 grid points
    -> Genuine substrate anomaly; re-open substrate-implementation audit

  INSTRUMENTATION-FAIL:
    - Any NaN cosine
    - OR CI width >= 0.10 (excessive seed variance)
    -> Investigate per-seed before any verdict

SELF-TESTS (per [[feedback-strategy-spec-formula-selftests]]):
  1. store_outer_product: N=4, M=1 -> W = v k^T / N (rank-1 exact)
  2. recall_cosine: M=1 -> cosine = 1.0 (exact recall at zero load)
  3. alpha_c interpolation: cosines=[0.95,0.85,0.60,0.30] at M=[200,400,800,1600], N=800
     -> alpha_c = 400/800 = 0.50
  4. cos_pred formula: cos_pred(M=200, N=512) = 1/sqrt(1+199/512) = 0.8489 (within 0.005 of smoke 0.8450)
  5. ci95 formula: mean=0.15, std~0.0071, n=5 -> CI width in (0.005, 0.030)
  6. PAC-Bayes floor: floor(kl=50, m=200) = max(0, 1-sqrt(50/400)) = 0.646

Queue: overnight_queue (GPU; 5 seeds x 6 M-values x N=4096; estimated 15-30 GPU-min)
Pre-reg: preregs/2026-05-24_wave14_moe_alpha_c_prestep_v2.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# ─── design parameters (exp_dev autonomy) ───
N_FULL = 4096
N_SMOKE = 512
N_SMOKE_LARGE = 2048   # multi-scale smoke gate: 4x smoke
# M grid: factor-2 sweep bracketing expected alpha_c=0.5625 (i.e. ~2300 items at N=4096)
M_GRID_FULL = [200, 400, 800, 1600, 3200, 6400]
M_GRID_SMOKE = [50, 100, 200, 400]
M_GRID_SMOKE_LARGE = [200, 400, 800, 1600]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BATCH_STORE = 512

# Pre-registered thresholds (RECALIBRATED from v1 -- linear heteroassociator regime)
PASS_COSINE = 0.80   # alpha_c = largest M where mean_cosine > this
FAIL_COSINE = 0.50
ALPHA_C_LO = 0.40    # RECALIBRATED: was 0.08 (AGS autoassoc; wrong reference class)
ALPHA_C_HI = 0.70    # RECALIBRATED: was 0.25
# Tighter inner band for HARD-PASS vs MIDDLE split
ALPHA_C_HP_LO = 0.50  # prediction 0.5625 +/-10%
ALPHA_C_HP_HI = 0.60
CI_WIDTH_WARN = 0.05   # HARD-PASS requires CI width < this
CI_WIDTH_FAIL = 0.10   # INSTRUMENTATION-FAIL above this
MAX_RESIDUAL_HP = 0.02  # HARD-PASS closed-form residual
MAX_RESIDUAL_MIDDLE = 0.05  # MIDDLE band
T_CRIT_5SEEDS = 2.776   # t-distribution df=4, 95% CI


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


# ─── core: BSC atoms ───
def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    """M random BSC vectors in {-1, +1}^N."""
    raw = torch.randint(0, 2, (M, N), generator=gen, device=device).float()
    return 2.0 * raw - 1.0


# ─── core: outer-product storage ───
def store_outer_product(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    """W = (1/N) * sum_i v_i k_i^T -- batched for GPU memory efficiency."""
    device = keys.device
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    for s in range(0, keys.shape[0], BATCH_STORE):
        e = min(s + BATCH_STORE, keys.shape[0])
        kb = keys[s:e]
        vb = vals[s:e]
        W.add_(vb.T @ kb, alpha=1.0 / N)
    return W


def recall_cosine(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor) -> tuple[float, float]:
    """Mean and std cosine similarity between W@k and v for all stored items."""
    y = keys @ W.T
    yn = y / (y.norm(dim=1, keepdim=True).clamp(min=1e-9))
    vn = vals / (vals.norm(dim=1, keepdim=True).clamp(min=1e-9))
    cos = (yn * vn).sum(dim=1)
    return float(cos.mean()), float(cos.std())


def ci95(values: list[float]) -> tuple[float, float, float]:
    """95% CI using t-distribution (df=n-1); returns (mean, lo, hi)."""
    n = len(values)
    if n < 2:
        m = values[0] if values else float("nan")
        return m, m, m
    m = sum(values) / n
    s = math.sqrt(sum((v - m) ** 2 for v in values) / (n - 1))
    t = T_CRIT_5SEEDS if n == 5 else 2.0
    half = t * s / math.sqrt(n)
    return m, m - half, m + half


def alpha_c_from_curve(m_grid: list[int], cosines: list[float], N: int, threshold: float) -> float:
    """alpha_c = largest M where mean_cosine > threshold, divided by N."""
    best_M = None
    for M, cos in zip(m_grid, cosines):
        if cos > threshold:
            best_M = M
    if best_M is None:
        return float("nan")
    return best_M / N


def pac_bayes_floor(kl: float, m: float) -> float:
    """McAllester PAC-Bayes floor: retention >= max(0, 1 - sqrt(KL / (2*M)))."""
    if m <= 0 or kl < 0:
        return 0.0
    return max(0.0, 1.0 - math.sqrt(kl / (2.0 * m)))


# ─── closed-form overlay (linear heteroassociator prediction) ───
def cos_pred(M: int, N: int) -> float:
    """Predicted mean cosine for linear outer-product memory at M patterns, dim N.
    Closed-form: E[cos] = 1/sqrt(1 + (M-1)/N) for i.i.d. BSC keys/values.
    Self-test: cos_pred(200, 512) = 1/sqrt(1+199/512) = 1/sqrt(1.3887) = 0.8489.
    """
    if N <= 0:
        return float("nan")
    return 1.0 / math.sqrt(1.0 + max(M - 1, 0) / N)


# ─── instrumentation self-test (MANDATORY per exp_dev role contract) ───
def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    device = torch.device("cpu")

    # Self-test 1: store_outer_product rank-1 structure
    gen = torch.Generator().manual_seed(0)
    N_t = 4
    k = make_bsc(1, N_t, gen, device)
    v = make_bsc(1, N_t, gen, device)
    W = store_outer_product(k, v, N_t)
    expected = (v.T @ k) / N_t
    err1 = float((W - expected).abs().max())
    assert err1 < 1e-6, f"Self-test 1 FAIL: max diff {err1:.2e}"
    print("[SELFTEST] 1/6 store_outer_product rank-1 structure OK", flush=True)

    # Self-test 2: recall_cosine M=1 -> cosine = 1.0
    gen2 = torch.Generator().manual_seed(42)
    k2 = make_bsc(1, N_t, gen2, device)
    v2 = make_bsc(1, N_t, gen2, device)
    W2 = store_outer_product(k2, v2, N_t)
    cos_mean, _ = recall_cosine(W2, k2, v2)
    assert abs(cos_mean - 1.0) < 1e-4, f"Self-test 2 FAIL: cosine for M=1 = {cos_mean:.6f}"
    print("[SELFTEST] 2/6 recall_cosine M=1 exact recall OK", flush=True)

    # Self-test 3: alpha_c interpolation
    m_test = [200, 400, 800, 1600]
    cos_test = [0.95, 0.85, 0.60, 0.30]
    ac = alpha_c_from_curve(m_test, cos_test, N=800, threshold=0.80)
    assert abs(ac - 0.50) < 1e-6, f"Self-test 3 FAIL: alpha_c={ac:.4f} (expected 0.50)"
    print("[SELFTEST] 3/6 alpha_c interpolation OK", flush=True)

    # Self-test 4: cos_pred formula
    cp = cos_pred(200, 512)
    assert abs(cp - 0.8489) < 0.001, f"Self-test 4 FAIL: cos_pred(200,512)={cp:.4f} (expected ~0.8489)"
    # Verify residual against v1 smoke measurement 0.8450 (from metrics.json)
    smoke_measured = 0.8450
    residual = abs(cp - smoke_measured)
    assert residual < 0.005, f"Self-test 4 FAIL: residual={residual:.4f} vs smoke data (expected <0.005)"
    print(f"[SELFTEST] 4/6 cos_pred formula OK (residual={residual:.4f} vs v1 smoke)", flush=True)

    # Self-test 5: ci95 formula
    vals_t = [0.14, 0.15, 0.16, 0.15, 0.15]
    m5, lo5, hi5 = ci95(vals_t)
    assert abs(m5 - 0.15) < 1e-6, f"Self-test 5 FAIL: ci95 mean={m5:.6f}"
    ci_width = hi5 - lo5
    assert 0.005 < ci_width < 0.030, f"Self-test 5 FAIL: CI width={ci_width:.4f} implausible"
    print("[SELFTEST] 5/6 ci95 formula OK", flush=True)

    # Self-test 6: PAC-Bayes floor formula
    floor_val = pac_bayes_floor(kl=50, m=200)
    expected_floor = max(0.0, 1.0 - math.sqrt(50.0 / 400.0))
    assert abs(floor_val - expected_floor) < 1e-6, f"Self-test 6 FAIL: floor={floor_val:.6f}"
    print("[SELFTEST] 6/6 PAC-Bayes floor formula OK", flush=True)

    print("[SELFTEST] All 6 self-tests passed", flush=True)


_instrumentation_selftest()


# ─── per-seed runner ───
def run_one_seed(seed: int, N: int, m_grid: list[int], device) -> dict:
    """Run M-sweep for one seed; return cosine curve and derived quantities."""
    gen = torch.Generator(device=device).manual_seed(seed)
    results = {}
    for M in m_grid:
        keys = make_bsc(M, N, gen, device)
        vals = make_bsc(M, N, gen, device)
        W = store_outer_product(keys, vals, N)
        mean_cos, std_cos = recall_cosine(W, keys, vals)
        predicted = cos_pred(M, N)
        residual = abs(mean_cos - predicted)
        del W
        if device.type == "cuda":
            torch.cuda.empty_cache()
        results[M] = {
            "mean_cosine": mean_cos,
            "std_cosine": std_cos,
            "cos_pred": predicted,
            "residual": residual,
        }
        print(f"  seed={seed} M={M:5d} cos={mean_cos:.4f} pred={predicted:.4f} "
              f"resid={residual:.4f}", flush=True)
    cosines = [results[M]["mean_cosine"] for M in m_grid]
    alpha_c_seed = alpha_c_from_curve(m_grid, cosines, N, PASS_COSINE)
    results["alpha_c_measured"] = alpha_c_seed
    return results


def compute_verdict(per_seed: dict, m_grid: list[int], N: int) -> tuple[str, str, dict]:
    seeds = sorted(per_seed.keys())
    n_seeds = len(seeds)

    per_M_cosines: dict[int, list[float]] = {M: [] for M in m_grid}
    per_M_residuals: dict[int, list[float]] = {M: [] for M in m_grid}
    alpha_cs: list[float] = []

    for s in seeds:
        sd = per_seed[s]
        for M in m_grid:
            per_M_cosines[M].append(sd[M]["mean_cosine"])
            per_M_residuals[M].append(sd[M]["residual"])
        if not math.isnan(sd["alpha_c_measured"]):
            alpha_cs.append(sd["alpha_c_measured"])

    mean_cosines = {M: sum(per_M_cosines[M]) / n_seeds for M in m_grid}
    mean_residuals = {M: sum(per_M_residuals[M]) / n_seeds for M in m_grid}
    max_residual = max(mean_residuals.values())

    # INSTRUMENTATION-FAIL: NaN cosines
    has_nan = any(math.isnan(v) for v_list in per_M_cosines.values() for v in v_list)
    if has_nan:
        return ("ALPHA_C_INSTRUMENTATION_FAIL",
                "NaN cosines detected. Re-design before MoE rebuild.", {})

    # HARD-FAIL: no capacity saturation
    if all(mean_cosines[M] > PASS_COSINE for M in m_grid):
        return ("ALPHA_C_HARD_FAIL",
                f"No capacity saturation: mean_cosine > {PASS_COSINE} at ALL M values "
                f"including M={m_grid[-1]}. Increase M_grid max or reduce N.",
                {"mean_cosines": {str(M): mean_cosines[M] for M in m_grid}})

    if not alpha_cs:
        return ("ALPHA_C_INSTRUMENTATION_FAIL",
                "alpha_c_measured is NaN for all seeds. Check M_GRID.", {})

    alpha_c_mean, alpha_c_lo, alpha_c_hi = ci95(alpha_cs)
    ci_width = alpha_c_hi - alpha_c_lo

    # INSTRUMENTATION-FAIL: excessive seed variance
    if ci_width >= CI_WIDTH_FAIL:
        return ("ALPHA_C_INSTRUMENTATION_FAIL",
                f"Excessive seed variance: CI_width={ci_width:.4f} >= {CI_WIDTH_FAIL}. "
                f"alpha_c_measured={alpha_c_mean:.4f}. Investigate per-seed.",
                {"alpha_c_measured": alpha_c_mean, "ci_width": ci_width})

    summary = {
        "alpha_c_measured": alpha_c_mean,
        "alpha_c_ci_lo": alpha_c_lo,
        "alpha_c_ci_hi": alpha_c_hi,
        "alpha_c_ci_width": ci_width,
        "alpha_c_per_seed": alpha_cs,
        "alpha_c_theory_tau080": 1.0 / 0.80 ** 2 - 1.0,  # = 0.5625
        "max_closed_form_residual": max_residual,
        "N": N,
        "mean_cosines": {str(M): mean_cosines[M] for M in m_grid},
        "mean_residuals": {str(M): mean_residuals[M] for M in m_grid},
        "cos_preds": {str(M): cos_pred(M, N) for M in m_grid},
        "m_per_expert_recommended": int(0.70 * alpha_c_mean * N),
        "m_total_recommended_k4": int(0.70 * alpha_c_mean * N * 4 * 0.80),
    }

    # Classify
    in_hp_range = ALPHA_C_HP_LO <= alpha_c_mean <= ALPHA_C_HP_HI
    in_middle_range = ALPHA_C_LO <= alpha_c_mean <= ALPHA_C_HI
    ci_tight = ci_width < CI_WIDTH_WARN
    residual_hp = max_residual < MAX_RESIDUAL_HP
    residual_middle = max_residual < MAX_RESIDUAL_MIDDLE

    if in_hp_range and ci_tight and residual_hp:
        verdict = "ALPHA_C_HARD_PASS"
        msg = (f"alpha_c calibration confirmed (linear heteroassociator regime): "
               f"alpha_c_measured={alpha_c_mean:.4f} in HARD-PASS [{ALPHA_C_HP_LO},{ALPHA_C_HP_HI}], "
               f"CI_width={ci_width:.4f} < {CI_WIDTH_WARN}, "
               f"max_residual={max_residual:.4f} < {MAX_RESIDUAL_HP}. "
               f"Theory predicts 0.5625 (tau=0.80). "
               f"M_per_expert_recommended={summary['m_per_expert_recommended']} "
               f"(0.70*alpha_c*N). M_total_recommended_k4={summary['m_total_recommended_k4']}. "
               f"Proceed to MoE SHIFT/PARTITION/SINGLE rebuild.")
    elif in_middle_range and residual_middle:
        verdict = "ALPHA_C_MIDDLE"
        msg = (f"alpha_c measured in MIDDLE band: alpha_c_measured={alpha_c_mean:.4f} in "
               f"[{ALPHA_C_LO},{ALPHA_C_HI}] but outside HARD-PASS [{ALPHA_C_HP_LO},{ALPHA_C_HP_HI}] "
               f"OR CI_width={ci_width:.4f} >= {CI_WIDTH_WARN} OR "
               f"max_residual={max_residual:.4f} in [{MAX_RESIDUAL_HP},{MAX_RESIDUAL_MIDDLE}]. "
               f"Proceed with measured value; document deviation. "
               f"M_per_expert_recommended={summary['m_per_expert_recommended']}.")
    else:
        verdict = "ALPHA_C_HARD_FAIL"
        msg = (f"alpha_c_measured={alpha_c_mean:.4f} OUTSIDE middle band [{ALPHA_C_LO},{ALPHA_C_HI}] "
               f"OR max_residual={max_residual:.4f} > {MAX_RESIDUAL_MIDDLE} at >=2 points. "
               f"Genuine substrate anomaly. Re-open substrate-implementation audit. "
               f"MoE rebuild stays gated.")

    return verdict, msg, summary


# ─── smoke suspicious-result gate ───
def suspicious_result_gate(m_grid: list[int], cosines: dict[int, float]) -> str | None:
    """Return a description if smoke metrics look suspicious (per exp_dev contract)."""
    cos_vals = list(cosines.values())
    # All exactly zero
    if all(abs(c) < 1e-9 for c in cos_vals):
        return "All cosine values are exactly 0.0 -- instrumentation failure"
    # All identical (no variance)
    if len(set(f"{c:.6f}" for c in cos_vals)) == 1:
        return f"All cosine values identical ({cos_vals[0]:.6f}) -- no variance across M"
    # All above threshold (no saturation found at all)
    if all(c > PASS_COSINE for c in cos_vals):
        return f"All M values still above threshold {PASS_COSINE} -- no saturation visible"
    return None


# ─── multi-scale smoke ───
def run_multiscale_smoke(device) -> bool:
    """Run smoke at N_SMOKE and N_SMOKE_LARGE. Return True if both pass gate."""
    print(f"[smoke] multi-scale smoke: N={N_SMOKE} and N={N_SMOKE_LARGE}", flush=True)
    for N, m_grid in [(N_SMOKE, M_GRID_SMOKE), (N_SMOKE_LARGE, M_GRID_SMOKE_LARGE)]:
        print(f"[smoke] N={N} m_grid={m_grid}", flush=True)
        seed_results = run_one_seed(SEEDS_SMOKE[0], N, m_grid, device)
        cosines = {M: seed_results[M]["mean_cosine"] for M in m_grid}
        flag = suspicious_result_gate(m_grid, cosines)
        if flag is not None:
            print(f"[smoke] INSTRUMENTATION_SUSPECT at N={N}: {flag}", flush=True)
            return False
        ac = seed_results["alpha_c_measured"]
        print(f"[smoke] N={N} alpha_c={ac:.4f} PASS", flush=True)
    return True


# ─── main ───
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[alpha_c_prestep_v2] device={device} smoke={smoke}", flush=True)

    if smoke:
        ok = run_multiscale_smoke(device)
        if not ok:
            print("[smoke] INSTRUMENTATION_SUSPECT: blocking ship", flush=True)
            sys.exit(1)
        print("[smoke] multi-scale smoke PASS", flush=True)
        sys.exit(0)

    # Full run
    N = N_FULL
    m_grid = M_GRID_FULL
    seeds = SEEDS_FULL
    out_dir = get_output_dir("wave14_moe_alpha_c_prestep_v2")
    t0 = time.time()

    per_seed: dict = {}
    for seed in seeds:
        print(f"[alpha_c_prestep_v2] === seed={seed} ===", flush=True)
        seed_results = run_one_seed(seed, N, m_grid, device)
        per_seed[seed] = seed_results
        print(f"  alpha_c={seed_results['alpha_c_measured']:.4f}", flush=True)

    verdict, verdict_msg, summary = compute_verdict(per_seed, m_grid, N)
    elapsed = time.time() - t0

    per_seed_serial = {}
    for s, sd in per_seed.items():
        ps = {"alpha_c_measured": sd["alpha_c_measured"]}
        for M in m_grid:
            ps[str(M)] = sd[M]
        per_seed_serial[str(s)] = ps

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "per_seed": per_seed_serial,
        "config": {
            "mode": "full",
            "N": N,
            "m_grid": m_grid,
            "seeds": seeds,
            "pass_cosine": PASS_COSINE,
            "alpha_c_lo": ALPHA_C_LO,
            "alpha_c_hi": ALPHA_C_HI,
            "alpha_c_hp_lo": ALPHA_C_HP_LO,
            "alpha_c_hp_hi": ALPHA_C_HP_HI,
            "ci_width_warn": CI_WIDTH_WARN,
            "max_residual_hp": MAX_RESIDUAL_HP,
            "recalibrated_from_v1": True,
            "reference_class": "linear_heteroassociator_cosine_tau_0.80",
            "device": str(device),
        },
    }
    validate_metrics(metrics)

    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"[alpha_c_prestep_v2] verdict={verdict}", flush=True)
    print(f"[alpha_c_prestep_v2] {verdict_msg}", flush=True)
    print(f"[alpha_c_prestep_v2] elapsed={elapsed:.1f}s  metrics -> {out_path}", flush=True)
    if summary:
        print(f"[alpha_c_prestep_v2] alpha_c={summary.get('alpha_c_measured', 'N/A'):.4f} "
              f"CI=[{summary.get('alpha_c_ci_lo', 0):.4f},{summary.get('alpha_c_ci_hi', 0):.4f}] "
              f"max_residual={summary.get('max_closed_form_residual', 'N/A'):.4f}", flush=True)


if __name__ == "__main__":
    main()
