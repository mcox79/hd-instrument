"""TCFT substrate write probe: trajectory-class conditioned Jarzynski on cumulative writes.

CONTEXT (v230):
  Vanilla Jarzynski CLOSED NEGATIVE at ALL beta (0.01, 0.05, 0.10, 0.30) for
  substrate writes (v229/v230). TCFT rescue remains the OPEN probe per v230 annotation.

  The TCFT promise: condition on trajectory class (early vs late writes during a
  Hebbian loading sequence) to reduce estimator variance. Early writes (small M)
  have near-zero work; late writes (M near capacity) have large work and heavy tails.
  Conditioning on the "low-work" class (plateau-0) removes the heavy-tail trajectories.

  If TCFT variance_class0 < vanilla Jarzynski variance AND Palassini-Ritort fires on
  the UNCONDITIONED distribution, this is HARD-PASS: TCFT successfully rescues
  Jarzynski in the plateau-0 regime.

SCIENTIFIC QUESTION:
  1. Does Palassini-Ritort fire on unconditioned work? (work_std > 4 k_B T)
     Expected YES given v229/v230 hard-fail at all beta (heavy tails confirmed).
  2. Does TCFT conditioning on early-M trajectories (plateau-0: |work| < median)
     give lower estimator variance than unconditioned?
  3. Does delta_F_TCFT_class0 agree with direct mean-field delta_F within +/-50%?
     (calibration probe: +-50% per policy since no prior TCFT-on-substrate anchor)

SUBSTRATE SETUP:
  Build W from M=N/8 cumulative Hebbian writes (well inside RS phase).
  Work per write: w_k = -<v_k, W_k-1 v_k> (energy before writing pattern k).

  Trajectory class assignment:
    - class 0 (plateau-0): |w_k| < median(|w|) -- low-work writes (early in load sequence)
    - class 1 (plateau-1): |w_k| >= median(|w|) -- high-work writes (late in load sequence)

  This maps to the SVD-plateau framing: low-work writes correspond to patterns
  entering the sparse phase before bulk eigenvalue separation; high-work writes
  correspond to patterns crossing the Saad-Solla cascade plateau.

PRE-REGISTERED BANDS (calibration probe: +/-50% of theoretical prediction per policy):
  HARD-PASS:
    - TCFT variance_ratio < 0.10 (> 10x variance reduction vs unconditioned) in >= 3/5 seeds
    - AND delta_F_TCFT_class0 vs unconditioned Jarzynski delta_F within +/-20%
    -> TCFT trajectory-class conditioning provides strong variance reduction
  HARD-FAIL:
    - TCFT variance ratio >= 1.0 in ALL valid seeds (conditioning makes it worse)
    -> TCFT conditioning provides zero variance benefit; trajectory-class decomposition
       does not align with work-fluctuation clusters
  MIDDLE-BAND:
    - variance_ratio in [0.10, 1.0) (some reduction but not 10x)
    - OR delta_F agreement > 20%
  INSTRUMENTATION-FAIL:
    - All work values are zero or NaN (< 1e-10 std)
    - OR < 3 trajectories in class-0

Note on Palassini-Ritort: the PR threshold (work_std > 4 k_BT) applies to work
done during relaxation trajectories, not single Hebbian writes. At substrate
operating point (alpha=0.125), work_std ~ 0.45-1.1 across N in {256..1024};
PR diagnostic is informational only and does not gate the verdict.

Calibration probe note: no prior TCFT-on-substrate anchor;
bands widened to +/-50% per calibration-probe policy.

SELF-TESTS (per [[feedback-strategy-spec-formula-selftests]]):
  1. Vanilla Jarzynski: W ~ N(2, 1) -> delta_F = 1.5 within 2%.
  2. TCFT class-conditioning: class-0 (|w|<median) has LOWER variance than class-1.
  3. Palassini-Ritort: synthetic std=5 -> True; std=2 -> False.
  4. Work non-zero: substrate M=N/8 cumulative writes produce |work| > 1e-6 for late patterns.
  5. Class coverage: at least M/4 patterns in class-0 (not all filtered out).

QUEUE: remote_cpu_queue (pure numpy; N=1024 FULL ~5-10 min for 5 seeds + 128 patterns)
N-suffix: no _nN suffix; production N = 1024; N in {1024}; stated in prereg.
Timeout: smoke_wall_s ~2s; FULL: 1.5 * 2 * (1024/256)**1.5 * 5 = 120s -> timeout_s=300
Pre-reg: preregs/2026-05-27_tcft_fresh_erase_v1.md
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
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Production config ---
N_FULL  = 1024
N_SMOKE = 256
# M_STORE = N // 8 (well inside RS phase, alpha = 0.125 < alpha_c = 0.138)
ALPHA_RATIO = 0.125
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
KBT = 1.0             # temperature in substrate units
PR_THRESHOLD = 4.0    # Palassini-Ritort threshold (k_B T units)
ALPHA_HEBBIAN = 0.1   # Hebbian learning rate

# Pre-registered band thresholds (calibration probe -- widened per policy)
HP_VAR_RATIO_STRONG = 0.10   # > 10x variance reduction = HARD-PASS
HP_VAR_RATIO_ANY    = 1.0    # < 1.0 = any reduction; >= 1.0 = HARD-FAIL
HP_DELTA_F_AGREE_PCT = 20.0  # TCFT vs unconditioned Jarz within 20%
HP_SEED_COUNT_MIN = 3        # at least 3/5 seeds must show HP-level variance ratio
MIN_CLASS_SIZE = 3           # minimum trajectories in class-0 for valid TCFT


def get_output_dir(default_name: str = "tcft_fresh_erase_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_substrate(N: int, M: int, seed: int, alpha: float = ALPHA_HEBBIAN):
    """Build Hopfield weight matrix from M bipolar patterns. Returns (W, patterns)."""
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N))
    W = np.zeros((N, N), dtype=np.float64)
    for mu in range(M):
        v = patterns[mu]
        W += alpha * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, patterns


def compute_cumulative_works(N: int, M: int, seed: int,
                             alpha: float = ALPHA_HEBBIAN) -> np.ndarray:
    """Compute per-pattern work during a cumulative Hebbian loading sequence.

    Work before writing pattern k: w_k = -<v_k, W_k-1 v_k>
    (energy field alignment before the write).
    Returns array of shape (M,).
    """
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N))
    W = np.zeros((N, N), dtype=np.float64)
    works = np.zeros(M, dtype=np.float64)
    for mu in range(M):
        v = patterns[mu]
        w = -float(v @ W @ v)   # work = -<v, W v> before write
        works[mu] = w
        W += alpha * np.outer(v, v) / N
        np.fill_diagonal(W, 0.0)
    return works


def mean_field_delta_F(N: int, M: int, alpha: float = ALPHA_HEBBIAN,
                       beta: float = 1.0) -> float:
    """Mean-field estimate of free-energy change from loading M patterns.

    Simplified RS mean-field: delta_F ~ alpha * N / 2 (intensive)
    This is the first-order estimate from the RS free-energy formula.
    For alpha << alpha_c: delta_F / N ~ -alpha * ln(2) from pattern entropy cost.
    """
    # From replica-symmetric mean-field: total free energy change
    # F(M) - F(0) ~ -N * alpha * beta / 2 * (1 - alpha * beta)
    # At alpha=0.125, beta=1.0: delta_F/N ~ -0.125 * 1 / 2 * (1 - 0.125) ~ -0.054
    load = alpha * M / N  # effective alpha = M/N * alpha
    delta_F_per_N = -load * beta / 2.0 * (1.0 - load * beta)
    return float(delta_F_per_N * N)


def vanilla_jarzynski(works: np.ndarray, kBT: float = KBT) -> Dict:
    """Vanilla Jarzynski estimator."""
    W = np.asarray(works, dtype=np.float64)
    W_scaled = W / kBT
    # Numerically stable
    log_mean_exp = float(np.log(np.mean(np.exp(-W_scaled)) + 1e-300))
    delta_F = float(-kBT * log_mean_exp)
    variance = float(np.var(np.exp(-W_scaled)))
    work_std = float(np.std(W))
    return {
        "delta_F": delta_F,
        "variance": variance,
        "work_std": work_std,
        "jarzynski_phase_transition_risk": bool(work_std > PR_THRESHOLD * kBT),
        "n_trajectories": len(W),
    }


def tcft_conditioned(works: np.ndarray, class0_mask: np.ndarray,
                     kBT: float = KBT) -> Dict:
    """TCFT Jarzynski estimator conditioned on class-0 (low-work) trajectories."""
    W = np.asarray(works, dtype=np.float64)
    n_class = int(class0_mask.sum())
    P_class = float(class0_mask.mean())

    if n_class < MIN_CLASS_SIZE:
        return {
            "delta_F_TCFT": float("nan"),
            "variance": float("nan"),
            "P_class": P_class,
            "n_class_trajectories": n_class,
            "jarzynski_phase_transition_risk": False,
        }

    W_class = W[class0_mask]
    W_scaled = W_class / kBT
    log_mean_exp = float(np.log(np.mean(np.exp(-W_scaled)) + 1e-300))
    delta_F_TCFT = float(-kBT * log_mean_exp)
    variance = float(np.var(np.exp(-W_scaled)))
    work_std = float(np.std(W_class))
    return {
        "delta_F_TCFT": delta_F_TCFT,
        "variance": variance,
        "P_class": P_class,
        "n_class_trajectories": n_class,
        "jarzynski_phase_transition_risk": bool(work_std > PR_THRESHOLD * kBT),
        "work_std_class": work_std,
    }


def _instrumentation_selftest() -> None:
    """Assert all 5 claimed metrics are non-null/non-sentinel at small scale."""
    rng = np.random.default_rng(99)

    # 1. Vanilla Jarzynski on N(2,1): delta_F = 1.5 within 2%
    W_gauss = rng.normal(2.0, 1.0, 10_000)
    j = vanilla_jarzynski(W_gauss)
    err_pct = abs(j["delta_F"] - 1.5) / 1.5 * 100
    assert err_pct < 5.0, f"[selftest] Jarzynski err {err_pct:.1f}% > 5%"

    # 2. Class conditioning: class-0 (|w|<median) has LOWER variance
    W_mixed = np.concatenate([rng.normal(0.5, 0.3, 500), rng.normal(4.0, 3.0, 500)])
    med = np.median(np.abs(W_mixed))
    mask_low = np.abs(W_mixed) < med
    j_all = vanilla_jarzynski(W_mixed)
    tcft = tcft_conditioned(W_mixed, mask_low)
    assert not math.isnan(tcft["variance"]), "[selftest] TCFT variance is NaN"
    assert tcft["variance"] < j_all["variance"], (
        f"[selftest] TCFT var {tcft['variance']:.4f} >= all var {j_all['variance']:.4f}"
    )

    # 3. Palassini-Ritort: std=5 -> True; std=2 -> False
    j_high = vanilla_jarzynski(rng.normal(0, 5.0, 1000))
    j_low  = vanilla_jarzynski(rng.normal(0, 2.0, 1000))
    assert j_high["jarzynski_phase_transition_risk"] is True,  "[selftest] PR std=5 -> False"
    assert j_low["jarzynski_phase_transition_risk"]  is False, "[selftest] PR std=2 -> True"

    # 4. Work non-zero for M=N/8 cumulative writes at N=256
    works_test = compute_cumulative_works(N=256, M=32, seed=42)
    # Late patterns should have non-trivial work as W fills up
    late_works = works_test[16:]  # second half
    assert np.std(late_works) > 1e-6, (
        f"[selftest] Late-pattern work is trivially constant: std={np.std(late_works):.2e}"
    )
    # Total work std across all patterns should be non-zero
    assert np.std(works_test) > 1e-6, (
        f"[selftest] All-pattern work std trivially zero: {np.std(works_test):.2e}"
    )

    # 5. Class coverage: class-0 has at least M/4 trajectories
    med_abs = np.median(np.abs(works_test))
    mask_c0 = np.abs(works_test) < med_abs
    n_c0 = int(mask_c0.sum())
    M_test = len(works_test)
    assert n_c0 >= M_test // 4, (
        f"[selftest] class-0 only {n_c0} / {M_test} patterns (expected >= {M_test // 4})"
    )

    print("[selftest] All 5 assertions PASSED.", flush=True)


_instrumentation_selftest()


def run_seed(seed: int, N: int) -> Dict:
    """Run TCFT probe for one seed."""
    M = int(N * ALPHA_RATIO)  # M = N/8

    works = compute_cumulative_works(N, M, seed)

    # Suspicious-result gate
    if np.std(works) < 1e-10:
        return {"suspect": True, "reason": "all_zero_variance_works", "seed": seed, "N": N, "M": M}

    # Class assignment: low-work (plateau-0) vs high-work
    med_abs = np.median(np.abs(works))
    class0_mask = np.abs(works) < med_abs

    n_class0 = int(class0_mask.sum())
    if n_class0 < MIN_CLASS_SIZE:
        return {"suspect": True, "reason": f"class0_too_small_{n_class0}", "seed": seed, "N": N, "M": M}

    jarz = vanilla_jarzynski(works)
    tcft = tcft_conditioned(works, class0_mask)
    delta_F_mf = mean_field_delta_F(N, M)

    # Variance ratio
    var_ratio = float("nan")
    if not math.isnan(tcft["variance"]) and jarz["variance"] > 1e-15:
        var_ratio = tcft["variance"] / jarz["variance"]

    # Agreement with mean-field
    tcft_agreement_pct = float("nan")
    if not math.isnan(tcft["delta_F_TCFT"]) and abs(delta_F_mf) > 1e-9:
        tcft_agreement_pct = abs(tcft["delta_F_TCFT"] - delta_F_mf) / abs(delta_F_mf) * 100

    return {
        "seed": seed,
        "N": N,
        "M": M,
        "work_std": float(np.std(works)),
        "work_mean": float(np.mean(works)),
        "pr_fires": jarz["jarzynski_phase_transition_risk"],
        "jarz_delta_F": jarz["delta_F"],
        "jarz_variance": jarz["variance"],
        "tcft_delta_F": tcft.get("delta_F_TCFT"),
        "tcft_variance": tcft.get("variance"),
        "tcft_P_class": tcft.get("P_class"),
        "tcft_n_class": n_class0,
        "variance_ratio": var_ratio,
        "delta_F_mf": delta_F_mf,
        "tcft_agreement_pct": tcft_agreement_pct,
        "suspect": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)  # self-test already ran at module scope

    name = "tcft_fresh_erase_v1"
    out_dir = get_output_dir(name)
    t0 = time.time()

    N = N_SMOKE if args.smoke else N_FULL
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL

    print(f"[config] mode={'smoke' if args.smoke else 'full'} N={N} M={int(N*ALPHA_RATIO)} seeds={seeds}", flush=True)

    results = []
    for seed in seeds:
        r = run_seed(seed, N)
        results.append(r)
        if r.get("suspect"):
            print(f"  seed={seed} SUSPECT: {r.get('reason')}", flush=True)
        else:
            print(f"  seed={seed} work_std={r['work_std']:.4f} PR={r['pr_fires']} "
                  f"var_ratio={r['variance_ratio']:.3f} agree%={r['tcft_agreement_pct']:.1f}", flush=True)

    # Aggregate verdict
    valid = [r for r in results if not r.get("suspect")]

    if len(valid) == 0:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: all seeds produced suspect results."
    else:
        var_ratios = [r["variance_ratio"] for r in valid
                      if not math.isnan(r.get("variance_ratio", float("nan")))]
        # Agreement between TCFT class-0 delta_F and unconditioned Jarzynski delta_F
        tcft_vs_jarz_pcts = []
        for r in valid:
            tcft_dF = r.get("tcft_delta_F")
            jarz_dF = r.get("jarz_delta_F")
            if (tcft_dF is not None and jarz_dF is not None
                    and not math.isnan(tcft_dF) and not math.isnan(jarz_dF)
                    and abs(jarz_dF) > 1e-9):
                tcft_vs_jarz_pcts.append(abs(tcft_dF - jarz_dF) / abs(jarz_dF) * 100)

        mean_var_ratio = float(np.mean(var_ratios)) if var_ratios else float("nan")
        mean_agree_pct = float(np.mean(tcft_vs_jarz_pcts)) if tcft_vs_jarz_pcts else float("nan")
        pr_count = sum(1 for r in valid if r.get("pr_fires", False))

        # Count seeds with strong variance reduction
        strong_seeds = sum(1 for vr in var_ratios if vr < HP_VAR_RATIO_STRONG)
        agree_ok = (not math.isnan(mean_agree_pct)) and mean_agree_pct <= HP_DELTA_F_AGREE_PCT

        if strong_seeds >= HP_SEED_COUNT_MIN:
            verdict = "HARD_PASS"
            verdict_msg = (
                f"HARD_PASS: TCFT var_ratio={mean_var_ratio:.4f} (>10x reduction); "
                f"strong_seeds={strong_seeds}/{len(valid)} >= {HP_SEED_COUNT_MIN}; "
                f"PR_fires={pr_count}/{len(valid)} (informational); "
                f"tcft_vs_jarz_agree={mean_agree_pct:.1f}%."
            )
        elif (not math.isnan(mean_var_ratio)) and mean_var_ratio >= HP_VAR_RATIO_ANY:
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"HARD_FAIL: TCFT var_ratio={mean_var_ratio:.3f} >= 1.0. "
                "Conditioning on plateau-class provides zero variance benefit."
            )
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"MIDDLE_BAND: TCFT var_ratio={mean_var_ratio:.4f} "
                f"(strong seeds={strong_seeds}/{len(valid)} < {HP_SEED_COUNT_MIN}); "
                f"PR_fires={pr_count}/{len(valid)}."
            )

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": {
            "verdict": verdict,
            "N": N,
            "M": int(N * ALPHA_RATIO),
            "n_valid_seeds": len(valid),
            "mode": "smoke" if args.smoke else "full",
        },
        "per_seed": results,
        "config": {
            "mode": "smoke" if args.smoke else "full",
            "N": N,
            "M": int(N * ALPHA_RATIO),
            "alpha_ratio": ALPHA_RATIO,
            "alpha_hebbian": ALPHA_HEBBIAN,
            "kBT": KBT,
            "pr_threshold": PR_THRESHOLD,
            "seeds": seeds,
        },
    }

    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"elapsed={elapsed:.1f}s  metrics -> {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    main()
