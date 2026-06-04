"""
pp58_scs_low_tau_sweep_d8_v1_n8192 -- PP-58 SCS tau_crit search at d=8, tau=0.01..0.09.

CONTEXT (v378 cycle 46 rescue R2):
  tau=0.10 test HARD_FAILed: ratio=14.668 (gamma_scs=19.149 vs gamma_emp=1.306).
  Three SCS failure modes now confirmed: sub-threshold-d (tau=0.05), high-alpha (alpha>=0.07),
  and high-tau (tau=0.10). R2 rescue: sweep tau=0.01..0.09 at d=8, alpha=0.05 (known-valid alpha)
  to locate tau_crit where SCS transitions from over-prediction to valid.
  Prior valid regime: alpha<=0.06 (from extended_d_sweep v376). This sweep tests low-tau boundary.

DESIGN:
  For each seed, sweep tau_targets = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09].
  Each tau_target: build asymmetric W per exp_pp58_scs_tau_sweep_d8_tau010 recipe,
  measure (tau_actual, d_est, gamma_scs, gamma_emp), compute ratio.
  Output: per-seed per-tau ratio table to locate tau_crit.

SCIENTIFIC QUESTION:
  Is there a tau_crit < 0.10 below which SCS ratio falls within [0.5, 2.0]?
  If yes: characterise the SCS validity window (alpha<=0.06 AND tau<=tau_crit).
  If no: SCS sub-property may be closed (all tau regimes fail at d=8, alpha=0.05).

PRE-REGISTERED BANDS:
  HARD-PASS: at least 4/9 tau values have mean ratio in [0.5, 2.0] across 5 seeds
             AND identified tau_crit <= 0.05 (low-tau regime valid).
  MIDDLE: 1-3/9 tau values in [0.5,2.0] OR tau_crit identified but > 0.05.
  HARD-FAIL: 0/9 tau values have ratio in [0.5, 2.0] (SCS invalid across all tested tau).

FORMULA SELF-TESTS (PROT-022):
  1. SCS gamma(d=8, tau=0.01) = (8 + 0.01/8)/(1.01) = 8.00125/1.01 = 7.9220 within 0.005.
     [INPUT: d=8, tau=0.01] [EXPECTED: 7.9220]
  2. SCS gamma(d=8, tau=0.09) = (8 + 0.09/8)/(1.09) = 8.01125/1.09 = 7.3498 within 0.001.
     [INPUT: d=8, tau=0.09] [EXPECTED: 7.3498]
  3. M = int(0.05 * 8192) = 409. [EXPECTED: 409]
  4. len(TAU_LIST) == 9. [EXPECTED: 9]

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: seed checkpoints keyed with run_mode + seed.
QUEUE: remote_cpu_queue (pure numpy; CPU; 9-tau x 5-seed sweep).
TIMEOUT ESTIMATE: tau010 elapsed ~206s/5seeds; this sweep is 9 tau values per seed.
  smoke_wall_s~206, FULL 9 tau values vs 1 = 9x more cells.
  ceil(1.5 * 206 * 9 * (5/5)) = ceil(2781) = 2781s. Round to 3600s.
  Note: eigvalsh at N=8192 dominates; 9 cells x 5 seeds = 45 eigvalsh calls.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp58_scs_low_tau_sweep_d8_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_FIXED = 0.05
TAU_LIST = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]


def _scs_gamma(d: float, tau: float) -> float:
    return (d + tau / d) / (1.0 + tau)


# PROT-022 formula self-tests at module scope
_g_d8_tau001 = _scs_gamma(8.0, 0.01)
# (8 + 0.01/8)/(1.01) = 8.00125/1.01 = 7.9220
print(f"[selftest-formula] SCS gamma(d=8,tau=0.01): {_g_d8_tau001:.4f} (expected 7.9220)", flush=True)
assert abs(_g_d8_tau001 - 7.9220) < 0.005, f"SCS selftest tau=0.01: got {_g_d8_tau001}"

_g_d8_tau009 = _scs_gamma(8.0, 0.09)
# (8 + 0.09/8)/(1.09) = 8.01125/1.09 = 7.3498
print(f"[selftest-formula] SCS gamma(d=8,tau=0.09): {_g_d8_tau009:.4f} (expected 7.3498)", flush=True)
assert abs(_g_d8_tau009 - 7.3498) < 0.005, f"SCS selftest tau=0.09: got {_g_d8_tau009}"

_M_check = int(ALPHA_FIXED * N)
assert _M_check == 409, f"M check: {_M_check} expected 409"
print(f"[selftest-formula] M={_M_check} at N={N} alpha={ALPHA_FIXED}", flush=True)

assert len(TAU_LIST) == 9, f"TAU_LIST length: {len(TAU_LIST)} expected 9"
print(f"[selftest-formula] len(TAU_LIST)={len(TAU_LIST)} expected 9", flush=True)

# Pre-registered thresholds
HP_VALID_TAU_MIN = 4          # at least 4/9 tau values with ratio in valid range
HP_RATIO_LOW = 0.5
HP_RATIO_HIGH = 2.0
HP_TAU_CRIT_MAX = 0.05        # tau_crit must be <= 0.05 for HP
MID_VALID_TAU_MIN = 1
SCS_MATCH_TOL = 0.30

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    N_PROBES = 50
    TAU_LIST_ACTIVE = [0.01, 0.05, 0.09]   # 3 tau values for smoke speed
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_PROBES = 500
    TAU_LIST_ACTIVE = TAU_LIST


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at tiny scale (N=64)."""
    rng = np.random.default_rng(0)
    n_tiny = 64   # MUST be tiny; eigvalsh at N=8192 takes >3min; self-test must be <5s
    M_tiny = max(1, int(ALPHA_FIXED * n_tiny))
    xi = rng.choice([-1.0, 1.0], size=(M_tiny, n_tiny)).astype(np.float32)
    W_sym = (xi.T @ xi) / n_tiny
    tau_t = 0.05
    rng_asym = np.random.default_rng(999)
    W_rand = rng_asym.standard_normal((n_tiny, n_tiny)).astype(np.float32) / math.sqrt(n_tiny)
    W_rand_asym = (W_rand - W_rand.T) / 2.0
    scale = np.linalg.norm(W_sym, 'fro') / max(np.linalg.norm(W_rand_asym, 'fro'), 1e-10)
    W = (1.0 - tau_t) * W_sym + tau_t * (W_rand_asym * scale)
    ev = np.linalg.eigvalsh(W)
    ev_sorted = np.sort(np.abs(ev))[::-1]
    d_est = float(ev_sorted[0]) / max(float(np.mean(ev_sorted[1:])), 1e-10)
    W_asym_part = (W - W.T) / 2.0
    tau_meas = float(np.linalg.norm(W_asym_part, 'fro') / max(np.linalg.norm(W, 'fro'), 1e-10))
    gamma = _scs_gamma(d_est, tau_meas)
    assert d_est is not None and not math.isnan(d_est), f"d_est is nan"
    assert tau_meas is not None and not math.isnan(tau_meas), f"tau_meas is nan"
    assert gamma is not None and not math.isnan(gamma), f"gamma is nan"
    assert d_est > 0, f"d_est <= 0: {d_est}"
    print(f"[selftest-inst] d_est={d_est:.3f} tau_meas={tau_meas:.4f} gamma={gamma:.3f} OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    print("[self-test] ALL PASSED -- exiting", flush=True)
    import sys as _sys; _sys.exit(0)


def build_asymmetric_W(xi: np.ndarray, n: int, tau_t: float) -> np.ndarray:
    """Build W with controlled asymmetry: W = (1-tau_t)*W_sym + tau_t*W_rand_asym_scaled."""
    W_sym = (xi.T @ xi) / n
    rng_asym = np.random.default_rng(seed=999)
    W_rand = rng_asym.standard_normal((n, n)).astype(np.float32) / math.sqrt(n)
    W_rand_asym = (W_rand - W_rand.T) / 2.0
    scale = np.linalg.norm(W_sym, 'fro') / max(np.linalg.norm(W_rand_asym, 'fro'), 1e-10)
    W_rand_asym_scaled = W_rand_asym * scale
    return (1.0 - tau_t) * W_sym + tau_t * W_rand_asym_scaled


def measure_tau_from_W(W: np.ndarray) -> float:
    W_asym = (W - W.T) / 2.0
    return float(np.linalg.norm(W_asym, 'fro') / max(np.linalg.norm(W, 'fro'), 1e-10))


def measure_d_from_W(W: np.ndarray) -> float:
    ev = np.linalg.eigvalsh(W)
    ev_sorted = np.sort(np.abs(ev))[::-1]
    if len(ev_sorted) < 2:
        return 1.0
    return float(ev_sorted[0]) / max(float(np.mean(ev_sorted[1:])), 1e-10)


def measure_kappa3(W: np.ndarray, n: int, rng: np.random.Generator, n_probes: int) -> float:
    V = rng.choice([-1.0, 1.0], size=(n, n_probes))
    return float(np.mean((V * (W @ (W @ (W @ V)))).sum(axis=0) / n))


def measure_gamma_emp(W_base: np.ndarray, n: int, rng: np.random.Generator, n_probes: int) -> float:
    delta_M = max(1, int(0.01 * n))
    xi_extra = rng.choice([-1.0, 1.0], size=(delta_M, n)).astype(np.float32)
    W_aug = W_base + (xi_extra.T @ xi_extra) / n
    k3_base = measure_kappa3(W_base, n, rng, n_probes)
    k3_aug = measure_kappa3(W_aug, n, rng, n_probes)
    return abs(k3_aug) / max(abs(k3_base), 1e-6)


def run_seed(seed: int, n_dim: int) -> Dict:
    """Run one seed across all TAU_LIST_ACTIVE values."""
    rng = np.random.default_rng(seed)
    t0 = time.time()
    M = int(ALPHA_FIXED * n_dim)
    xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)

    tau_results = []
    for tau_t in TAU_LIST_ACTIVE:
        print(f"  [seed={seed} N={n_dim}] tau_target={tau_t:.2f} building W...", flush=True)
        W = build_asymmetric_W(xi, n_dim, tau_t)
        tau_actual = measure_tau_from_W(W)
        d_est = measure_d_from_W(W)
        gamma_scs = _scs_gamma(d_est, tau_actual)
        rng2 = np.random.default_rng(seed + 1000 + int(tau_t * 100))
        gamma_emp = measure_gamma_emp(W, n_dim, rng2, N_PROBES)
        ratio = gamma_scs / max(gamma_emp, 1e-6)
        rel_err = abs(gamma_scs - gamma_emp) / max(gamma_emp, 1e-6)
        in_range = HP_RATIO_LOW <= ratio <= HP_RATIO_HIGH
        print(f"  [seed={seed}] tau_t={tau_t:.2f} tau_act={tau_actual:.4f} d={d_est:.3f} "
              f"gamma_scs={gamma_scs:.3f} gamma_emp={gamma_emp:.3f} ratio={ratio:.3f} "
              f"in_range={in_range}", flush=True)
        tau_results.append({
            "tau_target": tau_t,
            "tau_actual": tau_actual,
            "d_estimate": d_est,
            "gamma_scs": gamma_scs,
            "gamma_emp": gamma_emp,
            "scs_ratio": ratio,
            "scs_rel_error": rel_err,
            "in_range": in_range,
        })

    elapsed = time.time() - t0
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE,
            "tau_results": tau_results, "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    # Per-tau aggregation across seeds
    from collections import defaultdict
    per_tau = defaultdict(list)
    for r in results:
        for tr in r["tau_results"]:
            per_tau[tr["tau_target"]].append(tr["scs_ratio"])

    valid_taus = []
    tau_summary_parts = []
    for tau_t in TAU_LIST:
        if tau_t not in per_tau:
            continue
        ratios = per_tau[tau_t]
        mean_r = float(np.mean(ratios))
        in_range = HP_RATIO_LOW <= mean_r <= HP_RATIO_HIGH
        if in_range:
            valid_taus.append(tau_t)
        tau_summary_parts.append(f"tau={tau_t:.2f}:ratio={mean_r:.3f}(ok={in_range})")

    tau_summary = " ".join(tau_summary_parts)
    valid_count = len(valid_taus)
    tau_crit = min(valid_taus) if valid_taus else None

    if valid_count >= HP_VALID_TAU_MIN and tau_crit is not None and tau_crit <= HP_TAU_CRIT_MAX:
        return ("HARD_PASS",
                f"HARD_PASS: {valid_count}/9 tau values in [0.5,2.0]; tau_crit={tau_crit:.2f}<={HP_TAU_CRIT_MAX}. {tau_summary}")
    if valid_count >= MID_VALID_TAU_MIN:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: {valid_count}/9 tau values in [0.5,2.0]; tau_crit={tau_crit}. {tau_summary}")
    return ("HARD_FAIL",
            f"HARD_FAIL: 0/9 tau values have ratio in [0.5,2.0]; SCS invalid across all low-tau. {tau_summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha={ALPHA_FIXED} tau_list={TAU_LIST_ACTIVE}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE, "tau_list": TAU_LIST_ACTIVE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
print(f"[elapsed] total: {elapsed_total:.1f}s", flush=True)

# Build per_tau summary for metrics
from collections import defaultdict
per_tau_agg = defaultdict(list)
for r in all_results:
    for tr in r.get("tau_results", []):
        per_tau_agg[tr["tau_target"]].append(tr)

per_tau_summary = {}
for tau_t, trs in sorted(per_tau_agg.items()):
    mean_ratio = float(np.mean([t["scs_ratio"] for t in trs]))
    mean_d = float(np.mean([t["d_estimate"] for t in trs]))
    mean_gamma_emp = float(np.mean([t["gamma_emp"] for t in trs]))
    mean_gamma_scs = float(np.mean([t["gamma_scs"] for t in trs]))
    per_tau_summary[str(tau_t)] = {
        "mean_ratio": mean_ratio,
        "mean_d": mean_d,
        "mean_gamma_emp": mean_gamma_emp,
        "mean_gamma_scs": mean_gamma_scs,
        "in_range": HP_RATIO_LOW <= mean_ratio <= HP_RATIO_HIGH,
    }

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "alpha": ALPHA_FIXED,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "summary": verdict_msg,
    "per_tau": per_tau_summary,
    "per_seed": [
        {"seed": r.get("seed"), "elapsed_s": r.get("elapsed_s"),
         "n_tau": len(r.get("tau_results", []))}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
