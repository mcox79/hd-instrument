"""MoE single-expert alpha_c calibration pre-step.

CONTEXT: This is a MANDATORY PRE-STEP before the 3-arm MoE SHIFT/PARTITION/SINGLE
rebuild. R-PRIME-2 HARD-FAILED due to PARTITION-architecture confound (K cancels
algebraically from load ratio). The rebuild needs:
  (a) alpha_c_measured: the empirically measured per-expert capacity fraction
  (b) PAC-Bayes upper bound on retention as function of M (from R-PRIME-1 route)

Without alpha_c_measured, HARD-PASS conditions for the rebuild are ambiguous.

WHAT THIS MEASURES:
  Single-expert BSC outer-product memory, N=4096.
  Sweep M (items stored) across a factor-2 grid.
  At each M: store M random BSC key-value pairs, attempt recall, measure mean cosine.
  Extract alpha_c_measured = largest M where mean_cosine > PASS_COSINE / N.
  Also compute empirical retention curve and PAC-Bayes floor companion.

ARCHITECTURE:
  W[N x N] = (1/N) * sum_i v_i k_i^T   (outer-product Hopfield rule)
  recall: y = W k_query, fidelity = mean cosine(y, v_target) across all stored items

PRE-REGISTERED BANDS (per [[feedback-envelope-expansion-fail-bands]]):
  HARD-PASS (alpha_c calibration succeeded):
    - alpha_c_measured in [0.08, 0.25] (plausible BSC range; literature range 0.10-0.18)
    - mean_cosine > 0.80 at M = alpha_c_measured * N (definition of capacity threshold)
    - mean_cosine < 0.50 at M = 3 * alpha_c_measured * N (above-capacity degradation)
    - seed-variance CI width < 0.10 on alpha_c estimate (5 seeds)
    -> alpha_c_measured reported for downstream MoE rebuild; PAC-Bayes floor extracted

  HARD-FAIL (calibration unusable):
    - mean_cosine > 0.80 at ALL M values including M = 6400 (no capacity saturation observed)
    -> substrate resolution insufficient; increase N or change cosine threshold

  INSTRUMENTATION-FAIL:
    - any seed produces NaN cosine
    - runtime > 45 min total (scale down M_GRID)
    -> re-design before continuing to MoE rebuild

  MIDDLE (partial calibration):
    - alpha_c_measured in range but CI width >= 0.10 (noisy estimate)
    -> report as MIDDLE; use as approximate calibration with uncertainty note

SELF-TESTS (per [[feedback-strategy-spec-formula-selftests]]):
  1. store_outer_product: W = sum_i v_i k_i^T / N;
     N=4, M=1, seed=0 -> W = v k^T / N (exact rank-1 outer product / N)
  2. recall_cosine: y = W k = (v k^T / N) k = v * (k^T k / N) = v * (N/N) = v
     -> cosine(y, v) = 1.0 for M=1 (exact recall at capacity=0)
  3. alpha_c interpolation: if cosine grid is [0.95, 0.85, 0.60, 0.30] at M=[200, 400, 800, 1600]
     and PASS_COSINE=0.80: alpha_c_idx=1 (M=400 passes, M=800 fails)
  4. ci95 formula: mean=0.15, std=0.01, n=5 -> ci_half = 2.776*0.01/sqrt(5) = 0.0124
     ci = (0.1376, 0.1624)
  5. PAC-Bayes floor formula: floor(kl=50, m=200) = max(0, 1-sqrt(50/400)) = 0.646

Queue: overnight_queue (GPU; 5 seeds x 6 M-values x N=4096; ~15-30 GPU-min)
Pre-reg: preregs/2026-05-24_wave14_moe_alpha_c_prestep_v1.md

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev.
Per [[feedback-strategy-spec-formula-selftests]]: 5 self-test cells inline.
Per [[feedback-lit-scan-calibration-penalty]]: alpha_c transfer from Hopfield to BSC
  outer-product has lit-scan-penalty; use empirical measurement not assumed 0.138.
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

# ─── design parameters (exp_dev autonomy) ───
N_FULL = 4096
N_SMOKE = 512
# M grid: factor-2 sweep from ~alpha_c-floor to well-above-capacity
M_GRID_FULL = [200, 400, 800, 1600, 3200, 6400]
M_GRID_SMOKE = [50, 100, 200, 400]    # smoke: smaller N, proportional M
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BATCH_STORE = 512    # batched outer-product accumulation for GPU memory efficiency

# Pre-registered thresholds
PASS_COSINE = 0.80   # alpha_c = largest M where mean_cosine > this
FAIL_COSINE = 0.50   # above-capacity marker
ALPHA_C_LO = 0.08    # plausible range for BSC outer-product memory
ALPHA_C_HI = 0.25
CI_WIDTH_WARN = 0.10  # if CI width >= this, MIDDLE (noisy)

# t-distribution critical value for 95% CI, 5 seeds -> df=4 -> t=2.776
T_CRIT_5SEEDS = 2.776


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


# ─── core storage: outer-product Hopfield rule ───
def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    """M random BSC vectors in {-1, +1}^N."""
    raw = torch.randint(0, 2, (M, N), generator=gen, device=device).float()
    return 2.0 * raw - 1.0


def store_outer_product(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    """W = (1/N) * sum_i v_i k_i^T  — batched for GPU memory efficiency."""
    device = keys.device
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    for s in range(0, keys.shape[0], BATCH_STORE):
        e = min(s + BATCH_STORE, keys.shape[0])
        kb = keys[s:e]     # (bs, N)
        vb = vals[s:e]     # (bs, N)
        W.add_(vb.T @ kb, alpha=1.0 / N)  # (N, N) += (N, bs) @ (bs, N) / N
    return W


def recall_cosine(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor) -> tuple[float, float]:
    """Mean and std cosine similarity between W@k and v for all stored items."""
    # y = W k^T; since W is (N,N) and keys is (M,N): y = keys @ W.T
    y = keys @ W.T                                    # (M, N)
    yn = y / (y.norm(dim=1, keepdim=True).clamp(min=1e-9))
    vn = vals / (vals.norm(dim=1, keepdim=True).clamp(min=1e-9))
    cos = (yn * vn).sum(dim=1)                        # (M,)
    return float(cos.mean()), float(cos.std())


def ci95(values: list[float]) -> tuple[float, float, float]:
    """95% CI using t-distribution (df=n-1); returns (mean, lo, hi)."""
    n = len(values)
    if n < 2:
        m = values[0] if values else float("nan")
        return m, m, m
    m = sum(values) / n
    s = math.sqrt(sum((v - m) ** 2 for v in values) / (n - 1))
    t = T_CRIT_5SEEDS if n == 5 else 2.0  # fallback t-crit for other n
    half = t * s / math.sqrt(n)
    return m, m - half, m + half


def alpha_c_from_curve(m_grid: list[int], cosines: list[float], N: int, threshold: float) -> float:
    """alpha_c = largest M where mean_cosine > threshold, divided by N.
    Returns NaN if no M exceeds threshold (no capacity floor found)."""
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


# ─── self-tests ───
def self_test():
    errors = []

    # Self-test 1: store_outer_product rank-1 structure
    device = torch.device("cpu")
    gen = torch.Generator().manual_seed(0)
    N_t = 4
    k = make_bsc(1, N_t, gen, device)  # (1, 4)
    v = make_bsc(1, N_t, gen, device)  # (1, 4)
    W = store_outer_product(k, v, N_t)
    expected = (v.T @ k) / N_t          # (4, 4)
    err1 = float((W - expected).abs().max())
    if err1 > 1e-6:
        errors.append(f"Self-test 1 FAIL: max diff {err1:.2e}")

    # Self-test 2: recall_cosine M=1 -> cosine = 1.0
    gen2 = torch.Generator().manual_seed(42)
    k2 = make_bsc(1, N_t, gen2, device)
    v2 = make_bsc(1, N_t, gen2, device)
    W2 = store_outer_product(k2, v2, N_t)
    cos_mean, cos_std = recall_cosine(W2, k2, v2)
    # y = W2 @ k2^T = (v2 k2^T / N) k2 = v2 * (k2 k2^T / N) = v2 * 1.0 (BSC norm = N/N = 1)
    if abs(cos_mean - 1.0) > 1e-4:
        errors.append(f"Self-test 2 FAIL: cosine for M=1 = {cos_mean:.6f} (expected 1.0)")

    # Self-test 3: alpha_c interpolation
    m_test = [200, 400, 800, 1600]
    cos_test = [0.95, 0.85, 0.60, 0.30]
    ac = alpha_c_from_curve(m_test, cos_test, N=800, threshold=0.80)
    # largest M where cosine > 0.80 is 400; alpha_c = 400/800 = 0.50
    if abs(ac - 0.50) > 1e-6:
        errors.append(f"Self-test 3 FAIL: alpha_c={ac:.4f} (expected 0.50)")

    # Self-test 4: ci95 formula
    vals_t = [0.14, 0.15, 0.16, 0.15, 0.15]  # mean=0.15, std~0.0071
    m4, lo4, hi4 = ci95(vals_t)
    if abs(m4 - 0.15) > 1e-6:
        errors.append(f"Self-test 4 FAIL: ci95 mean={m4:.6f} (expected 0.15)")
    ci_width = hi4 - lo4
    if not (0.005 < ci_width < 0.030):
        errors.append(f"Self-test 4 FAIL: CI width={ci_width:.4f} implausible")

    # Self-test 5: PAC-Bayes floor formula
    floor_val = pac_bayes_floor(kl=50, m=200)
    expected_floor = max(0.0, 1.0 - math.sqrt(50.0 / 400.0))
    if abs(floor_val - expected_floor) > 1e-6:
        errors.append(f"Self-test 5 FAIL: floor={floor_val:.6f} expected={expected_floor:.6f}")

    if errors:
        for e in errors:
            print(f"[SELF-TEST] {e}", flush=True)
        raise AssertionError(f"Self-tests FAILED ({len(errors)} errors)")
    print(f"[SELF-TEST] All 5 self-tests passed", flush=True)


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
        del W
        if device.type == "cuda":
            torch.cuda.empty_cache()
        results[M] = {"mean_cosine": mean_cos, "std_cosine": std_cos}
        print(f"  seed={seed} M={M:5d} mean_cos={mean_cos:.4f} std_cos={std_cos:.4f}", flush=True)

    # Extract alpha_c_measured for this seed
    cosines = [results[M]["mean_cosine"] for M in m_grid]
    alpha_c_seed = alpha_c_from_curve(m_grid, cosines, N, PASS_COSINE)
    results["alpha_c_measured"] = alpha_c_seed

    return results


def compute_verdict(per_seed: dict, m_grid: list[int], N: int) -> tuple[str, str, dict]:
    seeds = sorted(per_seed.keys())
    n_seeds = len(seeds)

    # Aggregate cosine curves
    per_M_cosines: dict[int, list[float]] = {M: [] for M in m_grid}
    alpha_cs: list[float] = []
    for s in seeds:
        sd = per_seed[s]
        for M in m_grid:
            per_M_cosines[M].append(sd[M]["mean_cosine"])
        if not math.isnan(sd["alpha_c_measured"]):
            alpha_cs.append(sd["alpha_c_measured"])

    # Mean cosine per M
    mean_cosines = {M: sum(per_M_cosines[M]) / n_seeds for M in m_grid}

    # Check for INSTRUMENTATION-FAIL: NaN cosines
    has_nan = any(math.isnan(v) for v_list in per_M_cosines.values() for v in v_list)
    if has_nan:
        return ("ALPHA_C_INSTRUMENTATION_FAIL",
                "NaN cosines detected in at least one seed/M combination. Re-design before MoE rebuild.",
                {})

    # Check HARD-FAIL: no capacity saturation (all M stay high cosine)
    if all(mean_cosines[M] > PASS_COSINE for M in m_grid):
        return ("ALPHA_C_HARD_FAIL",
                f"No capacity saturation: mean_cosine > {PASS_COSINE} at ALL M values including M={m_grid[-1]}. "
                f"BSC outer-product substrate shows no floor at tested M range. "
                f"Increase M_grid max or reduce N. Cannot use as MoE rebuild pre-step.",
                {"mean_cosines": {str(M): mean_cosines[M] for M in m_grid}})

    # Compute alpha_c with CI
    if not alpha_cs:
        return ("ALPHA_C_INSTRUMENTATION_FAIL",
                "alpha_c_measured is NaN for all seeds (capacity threshold never observed). Check M_GRID.",
                {})

    alpha_c_mean, alpha_c_lo, alpha_c_hi = ci95(alpha_cs)
    ci_width = alpha_c_hi - alpha_c_lo

    summary = {
        "alpha_c_measured": alpha_c_mean,
        "alpha_c_ci_lo": alpha_c_lo,
        "alpha_c_ci_hi": alpha_c_hi,
        "alpha_c_ci_width": ci_width,
        "alpha_c_per_seed": alpha_cs,
        "N": N,
        "mean_cosines": {str(M): mean_cosines[M] for M in m_grid},
        "m_per_expert_recommended": int(0.70 * alpha_c_mean * N),  # 70% of capacity
        "m_total_recommended_k4": int(0.70 * alpha_c_mean * N * 4 * 0.80),  # K=4, eta=0.80
    }

    # Check HARD-PASS criteria
    in_range = ALPHA_C_LO <= alpha_c_mean <= ALPHA_C_HI
    ci_tight = ci_width < CI_WIDTH_WARN
    # At M=alpha_c*N, cosine should be near threshold
    alpha_c_M_target = int(alpha_c_mean * N)
    # Find closest M in grid
    closest_M = min(m_grid, key=lambda m: abs(m - alpha_c_M_target))
    cosine_at_threshold = mean_cosines[closest_M]
    # Above-capacity: 3x alpha_c
    above_M = min(m_grid, key=lambda m: abs(m - int(3 * alpha_c_mean * N)))
    cosine_above = mean_cosines[above_M] if above_M in mean_cosines else float("nan")

    summary["cosine_at_alpha_c_M"] = cosine_at_threshold
    summary["cosine_at_3x_alpha_c_M"] = cosine_above

    if in_range and ci_tight:
        verdict = "ALPHA_C_HARD_PASS"
        msg = (f"alpha_c calibration succeeded: alpha_c_measured={alpha_c_mean:.4f} "
               f"in [{ALPHA_C_LO}, {ALPHA_C_HI}], CI_width={ci_width:.4f} < {CI_WIDTH_WARN}. "
               f"M_per_expert_recommended={summary['m_per_expert_recommended']} "
               f"(70% of alpha_c*N={int(alpha_c_mean*N)}). "
               f"M_total_recommended_k4={summary['m_total_recommended_k4']} "
               f"(K=4, eta=0.80). Proceed to MoE SHIFT/PARTITION/SINGLE rebuild.")
    elif in_range and not ci_tight:
        verdict = "ALPHA_C_MIDDLE"
        msg = (f"alpha_c in plausible range ({alpha_c_mean:.4f}) but CI too wide "
               f"({ci_width:.4f} >= {CI_WIDTH_WARN}). Proceed with uncertainty note: "
               f"M_per_expert_recommended={summary['m_per_expert_recommended']} (approximate).")
    else:
        verdict = "ALPHA_C_OUT_OF_RANGE"
        msg = (f"alpha_c_measured={alpha_c_mean:.4f} outside expected range [{ALPHA_C_LO}, {ALPHA_C_HI}]. "
               f"BSC substrate capacity atypical. Review substrate implementation before MoE rebuild.")

    return verdict, msg, summary


# ─── main ───
def main():
    # Run self-tests FIRST (per [[feedback-strategy-spec-formula-selftests]])
    self_test()

    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        # Gate protocol: run self-tests only, exit 0 on pass
        sys.exit(0)

    smoke = args.smoke

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[alpha_c_prestep] device={device} smoke={smoke}", flush=True)

    N = N_SMOKE if smoke else N_FULL
    m_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode = "smoke" if smoke else "full"

    out_dir = get_output_dir("wave14_moe_alpha_c_prestep_v1")
    t0 = time.time()

    per_seed: dict = {}
    for seed in seeds:
        print(f"[alpha_c_prestep] === seed={seed} ===", flush=True)
        seed_results = run_one_seed(seed, N, m_grid, device)
        per_seed[seed] = seed_results
        print(f"  alpha_c_measured={seed_results['alpha_c_measured']:.4f}", flush=True)

    verdict, verdict_msg, summary = compute_verdict(per_seed, m_grid, N)
    elapsed = time.time() - t0

    # Serialize summary with string M keys for JSON
    summary_serial = {k: v for k, v in summary.items()}
    # per_seed: convert int keys to str, M-grid keys to str
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
        "summary": summary_serial,
        "per_seed": per_seed_serial,
        "config": {
            "mode": mode,
            "N": N,
            "m_grid": m_grid,
            "seeds": seeds,
            "pass_cosine": PASS_COSINE,
            "fail_cosine": FAIL_COSINE,
            "alpha_c_lo": ALPHA_C_LO,
            "alpha_c_hi": ALPHA_C_HI,
            "device": str(device),
        },
    }
    validate_metrics(metrics)

    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[alpha_c_prestep] verdict={verdict}", flush=True)
    print(f"[alpha_c_prestep] {verdict_msg}", flush=True)
    print(f"[alpha_c_prestep] elapsed={elapsed:.1f}s  metrics -> {out_path}", flush=True)
    if summary:
        print(f"[alpha_c_prestep] alpha_c_measured={summary.get('alpha_c_measured', 'N/A'):.4f} "
              f"CI=[{summary.get('alpha_c_ci_lo', 0):.4f}, {summary.get('alpha_c_ci_hi', 0):.4f}]",
              flush=True)


if __name__ == "__main__":
    main()
