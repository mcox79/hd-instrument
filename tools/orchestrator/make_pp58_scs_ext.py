"""Script to create PP-58 SCS extended d sweep from existing template."""
import re

src = open('d:/AI/hd-instrument/experiments/exp_pp58_scs_formula_test_d8_tau005_v1_n8192.py', encoding='utf-8').read()

new = src

# 1. Anchor name
new = new.replace('pp58_scs_formula_test_d8_tau005_v1_n8192', 'pp58_scs_extended_d_sweep_v1_n8192')

# 2. ALPHA_FIXED -> ALPHA_GRID
new = new.replace(
    'ALPHA_FIXED = 0.05\nALPHA_C = 0.138\nassert ALPHA_C > ALPHA_FIXED, f"alpha_c={ALPHA_C} must be > ALPHA_FIXED={ALPHA_FIXED}"',
    'ALPHA_GRID = [0.02, 0.04, 0.06, 0.08, 0.12, 0.18]\nALPHA_C = 0.138\nassert all(a < ALPHA_C for a in ALPHA_GRID), f"all alphas must be < alpha_c={ALPHA_C}"'
)

# 3. Formula selftests: replace M_check
new = new.replace(
    '_M_check = int(ALPHA_FIXED * N)\nassert _M_check == 409, f"M check: {_M_check} expected 409"\nprint(f"[selftest-formula] M = {_M_check} at N={N} alpha={ALPHA_FIXED}", flush=True)',
    '_M_check_min = int(0.02 * N)\nassert _M_check_min == 163, f"M min alpha check: {_M_check_min} expected 163"\nprint(f"[selftest-formula] M at alpha_min=0.02: {_M_check_min}", flush=True)\nassert all(a < ALPHA_C for a in ALPHA_GRID), "alpha grid capacity check"\nprint(f"[selftest-formula] ALPHA_GRID={ALPHA_GRID} all within capacity={ALPHA_C}", flush=True)'
)

# 4. Smoke/full config
new = new.replace(
    'if RUN_MODE == "smoke":\n    N_ACTIVE = 256\n    SEEDS = [7, 17]\n    N_PROBES = 100\nelse:\n    N_ACTIVE = N\n    SEEDS = [7, 17, 23, 31, 41]\n    N_PROBES = 500',
    'if RUN_MODE == "smoke":\n    N_ACTIVE = 256\n    SEEDS = [7, 17]\n    N_PROBES = 100\n    ALPHA_SWEEP = [0.04, 0.08, 0.18]  # 3 alphas for smoke\nelse:\n    N_ACTIVE = N\n    SEEDS = [7, 17, 23]\n    N_PROBES = 300\n    ALPHA_SWEEP = ALPHA_GRID  # full alpha sweep'
)

# 5. run_seed: replace single-alpha with multi-alpha loop
old_run = '''def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    M = int(ALPHA_FIXED * n_dim)
    xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)

    print(f"  [seed={seed} N={n_dim}] M={M} building W...", flush=True)
    tau = measure_tau(xi, n_dim)
    d_est = measure_d_estimate(xi, n_dim)
    gamma_scs = _scs_gamma(d_est, tau)

    rng2 = np.random.default_rng(seed + 1000)
    gamma_emp = measure_gamma_emp(xi, n_dim, rng2, N_PROBES)

    scs_rel_error = abs(gamma_scs - gamma_emp) / max(gamma_emp, 1e-6)
    scs_ratio = gamma_scs / max(gamma_emp, 1e-6)

    elapsed = time.time() - t0
    print(f"  [seed={seed}] tau={tau:.4f} d={d_est:.3f} "
          f"gamma_scs={gamma_scs:.3f} gamma_emp={gamma_emp:.3f} "
          f"rel_err={scs_rel_error:.3f} ratio={scs_ratio:.3f} "
          f"elapsed={elapsed:.1f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "tau_estimate": float(tau),
        "d_estimate": float(d_est),
        "gamma_scs": float(gamma_scs),
        "gamma_emp": float(gamma_emp),
        "scs_rel_error": float(scs_rel_error),
        "scs_ratio": float(scs_ratio),
        "elapsed_s": float(elapsed),
    }'''

new_run = '''def run_seed(seed: int, n_dim: int) -> Dict:
    t0 = time.time()
    cell_results = {}
    for alpha in ALPHA_SWEEP:
        rng = np.random.default_rng(seed + int(alpha * 10000))
        M = int(alpha * n_dim)
        xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)
        print(f"  [seed={seed} N={n_dim} alpha={alpha:.2f}] M={M} SVD...", flush=True)
        tau = measure_tau(xi, n_dim)
        d_est = measure_d_estimate(xi, n_dim)
        gamma_scs = _scs_gamma(d_est, tau)
        rng2 = np.random.default_rng(seed + int(alpha * 10000) + 9999)
        gamma_emp = measure_gamma_emp(xi, n_dim, rng2, N_PROBES)
        scs_rel_error = abs(gamma_scs - gamma_emp) / max(gamma_emp, 1e-6)
        scs_ratio = gamma_scs / max(gamma_emp, 1e-6)
        key = f"a{alpha:.4f}"
        cell_results[key] = {
            "alpha": float(alpha), "M": M, "tau": float(tau), "d": float(d_est),
            "gamma_scs": float(gamma_scs), "gamma_emp": float(gamma_emp),
            "scs_rel_error": float(scs_rel_error), "scs_ratio": float(scs_ratio),
        }
        print(f"  [seed={seed} alpha={alpha:.2f}] tau={tau:.4f} d={d_est:.3f} "
              f"gamma_scs={gamma_scs:.3f} gamma_emp={gamma_emp:.3f} "
              f"ratio={scs_ratio:.3f}", flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "elapsed_s": float(elapsed), "cells": cell_results,
    }'''

new = new.replace(old_run, new_run)

# 6. instrumentation selftest: use ALPHA_SWEEP[0] and ALPHA_SWEEP[-1]
old_st = '''def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    n_test = 256
    M_test = int(ALPHA_FIXED * n_test)
    rng = np.random.default_rng(42)
    xi_test = rng.choice([-1.0, 1.0], size=(M_test, n_test)).astype(np.float32)

    tau_test = measure_tau(xi_test, n_test)
    assert not np.isnan(tau_test), "tau is NaN"
    assert 0.0 <= tau_test <= 1.0, f"tau out of [0,1]: {tau_test}"

    d_test = measure_d_estimate(xi_test, n_test)
    assert not np.isnan(d_test), "d_estimate is NaN"
    assert d_test > 0, f"d_estimate is not positive: {d_test}"

    gamma_scs_test = _scs_gamma(d_test, tau_test)
    assert gamma_scs_test > 0, f"gamma_scs is not positive: {gamma_scs_test}"

    rng2 = np.random.default_rng(99)
    gamma_emp_test = measure_gamma_emp(xi_test, n_test, rng2, n_probes=100)
    assert gamma_emp_test >= 0, f"gamma_emp is negative: {gamma_emp_test}"
    assert gamma_emp_test > 0, f"gamma_emp is exactly zero -- instrumentation broken"

    print(f"[selftest] PASS: tau={tau_test:.4f} d={d_test:.3f} "
          f"gamma_scs={gamma_scs_test:.3f} gamma_emp={gamma_emp_test:.3f} N={n_test}", flush=True)'''

new_st = '''def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    n_test = 256
    for alpha_test in [ALPHA_SWEEP[0], ALPHA_SWEEP[-1]]:
        M_test = int(alpha_test * n_test)
        rng = np.random.default_rng(42 + int(alpha_test * 100))
        xi_test = rng.choice([-1.0, 1.0], size=(M_test, n_test)).astype(np.float32)
        tau_test = measure_tau(xi_test, n_test)
        assert not np.isnan(tau_test), f"tau is NaN at alpha={alpha_test}"
        assert 0.0 <= tau_test <= 1.0, f"tau out of [0,1] at alpha={alpha_test}: {tau_test}"
        d_test = measure_d_estimate(xi_test, n_test)
        assert not np.isnan(d_test), f"d_estimate is NaN at alpha={alpha_test}"
        assert d_test > 0, f"d_estimate not positive at alpha={alpha_test}: {d_test}"
        gamma_scs_test = _scs_gamma(d_test, tau_test)
        assert gamma_scs_test > 0, f"gamma_scs not positive at alpha={alpha_test}"
        rng2 = np.random.default_rng(99 + int(alpha_test * 100))
        gamma_emp_test = measure_gamma_emp(xi_test, n_test, rng2, n_probes=100)
        assert gamma_emp_test >= 0, f"gamma_emp negative at alpha={alpha_test}"
        assert gamma_emp_test > 0, f"gamma_emp exactly zero at alpha={alpha_test} -- broken"
        print(f"[selftest] alpha={alpha_test:.2f}: tau={tau_test:.4f} d={d_test:.3f} "
              f"gamma_scs={gamma_scs_test:.3f} gamma_emp={gamma_emp_test:.3f}", flush=True)
    print(f"[selftest] PASS: multi-alpha={ALPHA_SWEEP} all non-null N={n_test}", flush=True)'''

new = new.replace(old_st, new_st)

# 7. compute_verdict: multi-alpha structure
old_verdict = '''def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    taus = [r["tau_estimate"] for r in results]
    ds = [r["d_estimate"] for r in results]
    ratios = [r["scs_ratio"] for r in results]
    gamma_emps = [r["gamma_emp"] for r in results]
    gamma_scss = [r["gamma_scs"] for r in results]

    mean_tau = float(np.mean(taus))
    mean_d = float(np.mean(ds))
    mean_ratio = float(np.mean(ratios))
    mean_gamma_emp = float(np.mean(gamma_emps))
    mean_gamma_scs = float(np.mean(gamma_scss))

    match_count = sum(1 for r in results if r["scs_rel_error"] < SCS_MATCH_TOL)

    summary = (f"gamma_emp={mean_gamma_emp:.3f} gamma_scs={mean_gamma_scs:.3f} "
               f"ratio={mean_ratio:.3f} tau={mean_tau:.4f} d={mean_d:.3f} "
               f"match_{SCS_MATCH_TOL:.0%}={match_count}/{len(results)}")

    # HARD-FAIL checks
    if mean_d < HF_D_MIN:
        return ("HARD_FAIL",
                f"HARD_FAIL: d_estimate={mean_d:.3f} < {HF_D_MIN} (no spike; SCS assumption violated). "
                f"{summary}")
    if mean_tau > HF_TAU_MAX:
        return ("HARD_FAIL",
                f"HARD_FAIL: tau_estimate={mean_tau:.4f} > {HF_TAU_MAX} "
                f"(not near-Ginibre; SCS assumption violated). {summary}")
    if mean_ratio < HF_RATIO_LOW or mean_ratio > HF_RATIO_HIGH:
        return ("HARD_FAIL",
                f"HARD_FAIL: SCS ratio={mean_ratio:.3f} outside [{HF_RATIO_LOW},{HF_RATIO_HIGH}]. "
                f"SCS formula off by >2x. {summary}")

    # HARD-PASS
    d_in_range = HP_D_LOW <= mean_d <= HP_D_HIGH
    tau_in_range = HP_TAU_LOW <= mean_tau <= HP_TAU_HIGH
    ratio_in_range = HP_RATIO_LOW <= mean_ratio <= HP_RATIO_HIGH
    if (match_count >= HP_MATCH_MIN_SEEDS and d_in_range and
            tau_in_range and ratio_in_range):
        return ("HARD_PASS",
                f"HARD_PASS: SCS formula validated: match={match_count}/{len(results)} "
                f"ratio_in_range={ratio_in_range} d_ok={d_in_range} tau_ok={tau_in_range}. "
                f"{summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: match={match_count}/{len(results)} ratio={mean_ratio:.3f} "
            f"d_ok={d_in_range} tau_ok={tau_in_range}. {summary}")'''

new_verdict = '''def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    # Aggregate per-alpha stats across seeds
    alpha_ratios: Dict[str, list] = {}
    alpha_ds: Dict[str, list] = {}
    for r in results:
        for key, cell in r.get("cells", {}).items():
            alpha_ratios.setdefault(key, []).append(cell["scs_ratio"])
            alpha_ds.setdefault(key, []).append(cell["d"])

    if not alpha_ratios:
        return ("HARD_FAIL", "No cell data in results.")

    mean_ratios = {k: float(np.mean(v)) for k, v in alpha_ratios.items()}
    mean_ds = {k: float(np.mean(v)) for k, v in alpha_ds.items()}

    in_range_count = sum(1 for r in mean_ratios.values() if HP_RATIO_LOW <= r <= HP_RATIO_HIGH)
    catastrophic = any(r < 0.3 or r > 3.0 for r in mean_ratios.values())

    d_vals = list(mean_ds.values())
    d_max = max(d_vals) if d_vals else 0.0
    d_min = max(min(d_vals), 0.01) if d_vals else 1.0
    d_range_ratio = d_max / d_min

    summary = (f"in_range={in_range_count}/{len(mean_ratios)} "
               f"d_range={d_min:.1f}-{d_max:.1f}({d_range_ratio:.1f}x) "
               f"n_seeds={len(results)}")

    if catastrophic:
        return ("HARD_FAIL", f"HARD_FAIL: catastrophic SCS failure (ratio<0.3 or >3.0). {summary}")
    if in_range_count < 2:
        return ("HARD_FAIL",
                f"HARD_FAIL: SCS valid at only {in_range_count}/{len(mean_ratios)} alpha values. {summary}")

    if in_range_count >= 4 and d_range_ratio >= 3.0:
        return ("HARD_PASS",
                f"HARD_PASS: SCS formula valid at {in_range_count}/{len(mean_ratios)} alphas, "
                f"d_range={d_range_ratio:.1f}x. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: SCS valid at {in_range_count}/{len(mean_ratios)} alphas, "
            f"d_range={d_range_ratio:.1f}x. {summary}")'''

new = new.replace(old_verdict, new_verdict)

# 8. Fix metrics output per_seed
new = new.replace(
    '    "per_seed": [\n        {"seed": r.get("seed"),\n         "tau": r.get("tau_estimate"),\n         "d": r.get("d_estimate"),\n         "gamma_scs": r.get("gamma_scs"),\n         "gamma_emp": r.get("gamma_emp"),\n         "scs_rel_error": r.get("scs_rel_error"),\n         "scs_ratio": r.get("scs_ratio"),\n         "elapsed_s": r.get("elapsed_s")}\n        for r in all_results\n    ],',
    '    "per_seed": [\n        {"seed": r.get("seed"),\n         "elapsed_s": r.get("elapsed_s"),\n         "cells": r.get("cells", {})}\n        for r in all_results\n    ],'
)

# 9. Fix config print
new = new.replace(
    'print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} alpha={ALPHA_FIXED}", flush=True)',
    'print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} alpha_sweep={ALPHA_SWEEP}", flush=True)'
)

# 10. Fix metrics dict: remove alpha field
new = new.replace(
    '"N": N, "alpha": ALPHA_FIXED, "run_mode": RUN_MODE,',
    '"N": N, "alpha_sweep": ALPHA_SWEEP, "run_mode": RUN_MODE,'
)

# Verify
assert 'pp58_scs_extended_d_sweep_v1_n8192' in new, "ANCHOR MISSING"
assert 'N = 8192' in new, "N MISSING"
assert 'ALPHA_GRID = [0.02, 0.04, 0.06, 0.08, 0.12, 0.18]' in new, "ALPHA_GRID MISSING"

open('d:/AI/hd-instrument/experiments/exp_pp58_scs_extended_d_sweep_v1_n8192.py', 'w', encoding='utf-8').write(new)
print("DONE")
print("ANCHOR:", 'pp58_scs_extended_d_sweep_v1_n8192' in new)
print("N=8192:", 'N = 8192' in new)
print("ALPHA_GRID:", 'ALPHA_GRID = [0.02, 0.04, 0.06, 0.08, 0.12, 0.18]' in new)
