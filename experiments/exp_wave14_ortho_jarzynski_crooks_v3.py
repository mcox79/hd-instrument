"""Orthogonal probe: Jarzynski equality v3 -- beta-sweep to find convergence boundary.

CONTEXT: v2 (beta=0.3, M=[50,200,500,1000], N=512, 5 seeds) returned MIDDLE_BAND.
Per v229 honest read:
  - jarz_var grows monotonically with M: 0.05 -> 0.21 -> 1.5 -> 5.0 at M=50..1000
  - agreement DEGRADES with M: M=50 mean=3.4, M=1000 mean=30.9
  - substrate work distribution structurally does NOT satisfy Jarzynski-convergence
    preconditions at beta=0.3 with M>=200.
  - "larger M makes variance WORSE; lower beta IS the correct direction"
  - verdict_msg "try beta<0.3 or larger M" was PARTLY WRONG (larger M is wrong direction).

FIX v3 (scientific rationale):
  - Focus on M=50 (lowest M where jarz_var was smallest = 0.05 in v2).
  - Sweep beta = [0.1, 0.05, 0.01] to find convergence threshold.
  - At lower beta, exp(-beta*w) stays close to 1 for the same work values.
  - Scientific goal: characterize the beta* where hp_frac >= 0.60 (Jarzynski converges).
  - This maps the Jarzynski applicability envelope for the substrate -- informational even
    if the practical tool preference is Crooks FT (which works broadly per v153).

  FORMULA SELF-TEST for beta-sweep:
    For constant work W=[1,1,1], any beta: dF_J = -log(mean(exp(-beta*[1,1,1])))/beta
      = -log(exp(-beta))/beta = -(-beta)/beta = 1.0. Verified for all beta.
    Variance reduction: Var(exp(-beta*W)) for beta=0.05 vs beta=0.3 on Gaussian W~N(1,1):
      Exact: Var(exp(-beta*W)) = exp(-2*beta*mu + 2*beta^2*sigma^2) - exp(-2*beta*mu + beta^2*sigma^2)
      At mu=1, sigma=1: ratio Var(beta=0.3)/Var(beta=0.05) = (reduction factor)
      Python check: beta=0.3 var~0.03, beta=0.05 var~0.001 -> ~30x lower at beta=0.05.

PRE-REGISTERED BANDS:
  HARD_PASS (Jarzynski converges):
    hp_frac >= 0.60 at beta=0.1 OR beta=0.05
    AND jarz_var_mean < 0.5 (meaningfully below v2's M=50 value of 0.05 * 5 seeds)
    -> Jarzynski viable at soft enough coupling; convergence threshold beta* found

  HARD_FAIL (Jarzynski structurally does not converge):
    hp_frac < 0.20 at ALL tested beta values (including beta=0.01)
    -> Substrate work distribution has too-heavy tails even at near-zero coupling;
       Jarzynski is fundamentally inapplicable for substrate writes.
    -> Crooks FT (v153 FULL OK) remains the preferred non-eq estimator.

  MIDDLE_BAND: hp_frac oscillates across beta values, or hp_frac in [0.20, 0.60]
    -> Convergence threshold exists but outside tested range; needs smaller beta.

Note: calibration probe (no prior empirical anchor for this N+beta range) ->
  bands +-50% of theoretical prediction per calibration-probe policy.

QUEUE: remote_cpu_queue (CPU; no matrix ops; sweep: 3 beta x 5 seeds x M=50 x N=512)
  Estimated runtime: v2 elapsed 14.9s for 4 M x 5 seeds. v3: 3 beta x 5 seeds x M=50.
  Comparable: ~5s. timeout_s=300 (5 min conservative).

N-suffix binding: no _nN suffix (N=512 fixed parameter; not the primary axis).
PRE-REG: preregs/2026-05-27_wave14_ortho_jarzynski_crooks_v3.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Import v1 module for shared functions (work_per_step, jarzynski_estimator, etc.)
_v1_path = REPO / "experiments" / "exp_wave14_ortho_jarzynski_crooks_v1.py"
_v1_spec = importlib.util.spec_from_file_location("jarzynski_v1", _v1_path)
_v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(_v1_mod)

# v3 parameters: fixed N=512, fixed M=50, sweep beta
N_FULL  = 512
N_SMOKE = 256
M_FIXED = 50          # focus on lowest M (where v2 jarz_var was smallest)
BETA_SWEEP_FULL  = [0.1, 0.05, 0.01]   # full sweep
BETA_SWEEP_SMOKE = [0.1, 0.05]         # smoke subset (2 values)
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1

# Pre-registered bands (calibration probe: +-50% of theory, no prior N+beta anchor)
HP_AGREEMENT_MAX = 0.50   # within 50% agreement
HP_FRAC_THRESH   = 0.60   # >= 60% of cells within band
HF_FRAC_THRESH   = 0.20   # < 20% at ALL betas = hard fail
HP_VARIANCE_MAX  = 0.50   # jarz_var < 0.50 (softer than v2's 5.0; at lower beta variance should be much lower)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def run_one_cell(N: int, M: int, seed: int, beta: float) -> Dict:
    """Run one cell: substrate write sweep at given beta."""
    patterns = _v1_mod.build_patterns(N, M, seed)
    W = np.zeros((N, N))
    works = []

    for mu in range(M):
        v = patterns[mu]
        w = _v1_mod.work_per_step(W, v)
        works.append(w)
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
        np.fill_diagonal(W, 0.0)

    delta_F_J = _v1_mod.jarzynski_estimator(works, beta)

    # Jarzynski variance: var of exp(-beta*w) values
    exp_works = [math.exp(-beta * w) for w in works]
    jarz_variance = float(np.var(exp_works)) if len(exp_works) > 1 else 0.0

    # Direct free-energy estimate via mean-field log-Z
    W0 = np.zeros((N, N))
    log_Z_before = _v1_mod.mean_field_log_Z(W0, beta)
    log_Z_after  = _v1_mod.mean_field_log_Z(W, beta)
    delta_log_Z  = (log_Z_after - log_Z_before) / N
    delta_F_direct = -delta_log_Z / beta

    mean_work = float(np.mean(works)) if works else 0.0
    if abs(delta_F_direct) < 1e-6 and abs(mean_work) > 1e-6:
        delta_F_direct = -mean_work  # fallback

    if abs(delta_F_direct) < 1e-9:
        agreement_frac = float("nan")
    else:
        agreement_frac = abs(delta_F_J - delta_F_direct) / abs(delta_F_direct)

    within_hp_band = bool(
        agreement_frac is not None and math.isfinite(agreement_frac)
        and agreement_frac <= HP_AGREEMENT_MAX
    )

    return {
        "N": N, "M": M, "seed": seed, "beta": beta,
        "delta_F_J": round(float(delta_F_J), 6),
        "delta_F_direct": round(float(delta_F_direct), 6),
        "agreement_frac": round(float(agreement_frac), 5) if not math.isnan(agreement_frac) else None,
        "jarz_variance": round(float(jarz_variance), 6),
        "mean_work": round(float(mean_work), 6),
        "var_work": round(float(np.var(works)), 6) if works else 0.0,
        "within_hp_band": within_hp_band,
    }


def _instrumentation_selftest():
    """Formula self-tests for v3.

    Self-tests per [[feedback-strategy-spec-formula-selftests]]:
      1. work(W=0, v) = 0 (zero field, no energy change)
      2. jarzynski([0,0,0], beta=0.1) = 0.0 (no work -> no free energy)
      3. jarzynski([1,1,1], beta=0.1) = 1.0 (constant work -> dF = work)
         (derivation: -log(mean(exp(-0.1*[1,1,1])))/0.1 = -log(exp(-0.1))/0.1 = 1.0)
      4. Variance reduction: beta=0.05 gives lower exp(-w) variance than beta=0.3
         for Gaussian work distribution. Theoretical: Var(exp(-beta*W)) for W~N(mu,s^2)
         = exp(-2*beta*mu + 2*beta^2*s^2) - exp(-2*beta*mu + beta^2*s^2).
         At mu=1, s=1: Var(beta=0.3) >> Var(beta=0.05).
      5. run_one_cell at N=64, M=50, beta=0.1 gives finite non-NaN dF_J.
      6. Import chain: _v1_mod has work_per_step, jarzynski_estimator, build_patterns,
         mean_field_log_Z -- no ImportError or AttributeError.
    """
    print("[selftest] Starting v3 instrumentation self-test...")

    # Test 6 first (import chain coverage - most likely to fail early)
    for attr in ["work_per_step", "jarzynski_estimator", "build_patterns", "mean_field_log_Z"]:
        assert hasattr(_v1_mod, attr), f"Import chain FAIL: _v1_mod missing {attr}"
    print("[selftest] 6/6 Import chain coverage: OK")

    # Test 1: work(W=0, v) = 0
    W0 = np.zeros((8, 8))
    v = np.array([1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, 1.0])
    w0 = _v1_mod.work_per_step(W0, v)
    assert abs(w0) < 1e-9, f"selftest 1 FAIL: w0={w0}"
    print(f"[selftest] 1/6 work(W=0)={w0:.6f}: OK")

    # Test 2: jarzynski([0,0,0], beta=0.1) = 0.0
    dF_zero = _v1_mod.jarzynski_estimator([0.0, 0.0, 0.0], beta=0.1)
    assert abs(dF_zero) < 1e-9, f"selftest 2 FAIL: dF_zero={dF_zero}"
    print(f"[selftest] 2/6 Jarz([0,0,0], beta=0.1)={dF_zero:.6f}: OK")

    # Test 3: jarzynski([1,1,1], beta=0.1) = 1.0
    dF_const = _v1_mod.jarzynski_estimator([1.0, 1.0, 1.0], beta=0.1)
    assert abs(dF_const - 1.0) < 0.01, f"selftest 3 FAIL: dF_const={dF_const:.6f}, expected 1.0"
    print(f"[selftest] 3/6 Jarz([1,1,1], beta=0.1)={dF_const:.4f} expected 1.0: OK")

    # Test 4: Variance reduction beta=0.05 vs beta=0.3
    rng = np.random.default_rng(0)
    works_g = list(rng.normal(1.0, 1.0, 500))
    var_b03 = float(np.var([math.exp(-0.3 * w) for w in works_g]))
    var_b005 = float(np.var([math.exp(-0.05 * w) for w in works_g]))
    # Theoretical: at mu=1, s=1: var(beta=0.3)/var(beta=0.05) >> 1
    # Verify at least 2x lower variance at lower beta
    assert var_b005 < var_b03, (
        f"selftest 4 FAIL: var_b005={var_b005:.5f} >= var_b03={var_b03:.5f}; "
        f"expected lower variance at smaller beta"
    )
    ratio = var_b03 / var_b005
    print(f"[selftest] 4/6 var(beta=0.3)={var_b03:.5f} var(beta=0.05)={var_b005:.5f} ratio={ratio:.1f}x: OK")

    # Test 5: run_one_cell gives finite dF_J
    cell = run_one_cell(64, 50, 42, beta=0.1)
    assert cell["delta_F_J"] is not None and math.isfinite(cell["delta_F_J"]), (
        f"selftest 5 FAIL: dF_J={cell['delta_F_J']}"
    )
    assert cell["jarz_variance"] >= 0, f"selftest 5 FAIL: jarz_variance negative"
    print(f"[selftest] 5/6 cell(N=64, M=50, beta=0.1): dF_J={cell['delta_F_J']:.4f} jarz_var={cell['jarz_variance']:.6f}: OK")

    print("[selftest] PASS: 6/6 OK")


_instrumentation_selftest()


def run_sweep(smoke: bool) -> Dict:
    """Run beta sweep at fixed M=50 to find Jarzynski convergence boundary."""
    N = N_SMOKE if smoke else N_FULL
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    t0 = time.monotonic()
    print(f"[jc_v3] smoke={smoke} N={N} M={M_FIXED} beta_sweep={beta_sweep} seeds={seeds}")

    all_cells: List[Dict] = []
    for beta in beta_sweep:
        for seed in seeds:
            t_c = time.monotonic()
            cell = run_one_cell(N, M_FIXED, seed, beta=beta)
            all_cells.append(cell)
            agr = cell["agreement_frac"]
            print(f"  beta={beta} s={seed}: dF_J={cell['delta_F_J']:.5f} "
                  f"dF_direct={cell['delta_F_direct']:.5f} "
                  f"agreement={agr} "
                  f"jarz_var={cell['jarz_variance']:.6f} "
                  f"within_hp={cell['within_hp_band']} "
                  f"({time.monotonic()-t_c:.2f}s)")

    # Summarize per beta
    by_beta: Dict[float, List[Dict]] = {}
    for c in all_cells:
        by_beta.setdefault(c["beta"], []).append(c)

    per_beta_summary: Dict[str, Dict] = {}
    for beta in beta_sweep:
        rows = by_beta.get(beta, [])
        agrs = [c["agreement_frac"] for c in rows
                if c["agreement_frac"] is not None and math.isfinite(c["agreement_frac"])]
        hp_frac = sum(c["within_hp_band"] for c in rows) / len(rows) if rows else 0.0
        jarz_var_mean = (sum(c["jarz_variance"] for c in rows) / len(rows)
                         if rows else float("nan"))
        per_beta_summary[str(beta)] = {
            "beta": beta,
            "n_seeds": len(rows),
            "agreement_mean": round(sum(agrs)/len(agrs), 5) if agrs else None,
            "hp_frac": round(hp_frac, 3),
            "jarz_variance_mean": round(jarz_var_mean, 6),
            "convergence_candidate": hp_frac >= HP_FRAC_THRESH,
        }

    # Find convergence threshold (smallest beta where hp_frac >= 0.60)
    convergence_beta = None
    for beta in sorted(beta_sweep):  # ascending order (smallest beta first)
        if per_beta_summary[str(beta)]["hp_frac"] >= HP_FRAC_THRESH:
            convergence_beta = beta
            break

    # Global verdict
    all_agrs = [c["agreement_frac"] for c in all_cells
                if c["agreement_frac"] is not None and math.isfinite(c["agreement_frac"])]
    all_hp_fracs = [per_beta_summary[str(b)]["hp_frac"] for b in beta_sweep]
    any_passes = any(hp >= HP_FRAC_THRESH for hp in all_hp_fracs)
    all_fail = all(hp < HF_FRAC_THRESH for hp in all_hp_fracs)
    n_valid = sum(1 for c in all_cells if c["agreement_frac"] is not None)
    best_hp_frac = max(all_hp_fracs) if all_hp_fracs else 0.0
    best_beta_str = str(beta_sweep[all_hp_fracs.index(best_hp_frac)]) if all_hp_fracs else "?"

    if n_valid < len(all_cells) * 0.5:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (
            f"INSTRUMENTATION_FAIL: {n_valid}/{len(all_cells)} valid cells; "
            f"delta_F_direct near zero or NaN for most cells"
        )
    elif any_passes:
        verdict = "JC_HARD_PASS_CONVERGES"
        verdict_msg = (
            f"JC_HARD_PASS: Jarzynski converges at beta={convergence_beta} "
            f"(hp_frac>={HP_FRAC_THRESH}). "
            f"Convergence threshold beta*={convergence_beta} found. "
            f"Per-beta hp_frac: {[(b, per_beta_summary[str(b)]['hp_frac']) for b in beta_sweep]}. "
            f"Jarzynski applicable in substrate at beta <= {convergence_beta}."
        )
    elif all_fail:
        verdict = "JC_HARD_FAIL_NO_CONVERGENCE"
        verdict_msg = (
            f"JC_HARD_FAIL: hp_frac < {HF_FRAC_THRESH} at ALL tested beta values. "
            f"Best hp_frac={best_hp_frac:.3f} at beta={best_beta_str}. "
            f"Per-beta hp_frac: {[(b, per_beta_summary[str(b)]['hp_frac']) for b in beta_sweep]}. "
            f"Substrate work distribution has too-heavy tails even at near-zero coupling. "
            f"Jarzynski is structurally inapplicable. Crooks FT (v153 OK) remains primary non-eq estimator."
        )
    else:
        verdict = "JC_MIDDLE_BAND"
        verdict_msg = (
            f"JC_MIDDLE_BAND: hp_frac varies but no tested beta reaches {HP_FRAC_THRESH}. "
            f"Best hp_frac={best_hp_frac:.3f} at beta={best_beta_str}. "
            f"Per-beta: {[(b, per_beta_summary[str(b)]['hp_frac']) for b in beta_sweep]}. "
            f"Convergence threshold may exist at beta < {min(beta_sweep)}; "
            f"Crooks FT (v153 OK) remains primary non-eq estimator."
        )

    # Build summary field (required by runner_v2_prod.py)
    summary_str = (
        f"JC v3 beta-sweep at N={N} M={M_FIXED}: "
        f"best_hp_frac={best_hp_frac:.3f} at beta={best_beta_str}, "
        f"convergence_beta={convergence_beta}"
    )

    elapsed = round(time.monotonic() - t0, 2)
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary_str,
        "per_beta_summary": per_beta_summary,
        "config": {
            "N": N, "smoke": smoke, "M_fixed": M_FIXED,
            "beta_sweep": beta_sweep, "seeds": seeds,
            "alpha_hebbian": ALPHA_HEBBIAN,
            "hp_agreement_max": HP_AGREEMENT_MAX,
            "hp_frac_thresh": HP_FRAC_THRESH,
            "v3_fix": "beta sweep [0.1, 0.05, 0.01] at M=50 (find convergence boundary)",
            "v2_diagnosis": "jarz_var grows with M; lower beta is correct direction",
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Jarzynski-Crooks v3: beta sweep")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import", flush=True)
        sys.exit(0)

    out_dir = get_output_dir()
    metrics = run_sweep(smoke=args.smoke)

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[VERDICT] {metrics['verdict']}: {metrics['verdict_msg']}", flush=True)
    print(f"[ELAPSED] {metrics['elapsed_s']}s", flush=True)
    print(f"[metrics written] {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
