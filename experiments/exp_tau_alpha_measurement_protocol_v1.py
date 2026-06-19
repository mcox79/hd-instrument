"""
tau_alpha_measurement_protocol_v1 -- tau_alpha measurement for streaming-write aging.

SCIENTIFIC QUESTION:
  Streaming writes age stored patterns through the effective memory time constant tau_alpha.
  Research predicts: tau_alpha = N / (alpha * write_rate) in the continuous-time limit,
  equivalently tau_alpha inversely proportional to alpha for fixed write rate.
  This is the first direct empirical pinning of tau_alpha vs alpha.

  Protocol:
    1. Store M = alpha * N patterns. Measure baseline retrieval fidelity f_0.
    2. Perform T additional streaming writes (new patterns, overwriting old).
    3. Re-measure retrieval fidelity f(t) after T writes.
    4. Fit exponential decay f(t) = f_0 * exp(-t / tau_alpha_emp).
    5. Compare tau_alpha_emp vs theory: tau_alpha_theory = N / (alpha * 1.0) (write_rate=1).
    6. Repeat across alpha sweep: alpha in {0.05, 0.10, 0.15, 0.20}.

  HP: tau_alpha empirically pinned within +/-15% of theory across alpha sweep.
      |tau_alpha_emp - tau_alpha_theory| / tau_alpha_theory <= 0.15 for each alpha.
  HF: deviation > 3x theory (systematic error, not statistical noise).
  MIDDLE: some alpha values within 15%, some between 15% and 3x.

PRE-REGISTERED BANDS (calibration probe -- no prior direct tau_alpha measurement):
  HP: relative_deviation <= 0.15 for >= 75% of alpha values tested.
  HF: relative_deviation > 3.0 for any alpha (>3x theory is instrumentation failure).
  MIDDLE: 50%-75% of alpha values within HP.
  Note: first direct measurement; bands set +-50% of theory per calibration-probe policy.
  tau_alpha_theory = N / alpha; this is the dominant first-order term from aging derivation.

FORMULA SELF-TESTS:
  1. tau_alpha_theory = N / alpha.
     [INPUT: N=1024, alpha=0.10] [EXPECTED: tau_alpha_theory = 10240]
  2. tau_alpha_theory = N / alpha.
     [INPUT: N=1024, alpha=0.20] [EXPECTED: tau_alpha_theory = 5120]
  3. Exponential decay: f(T) = f_0 * exp(-T/tau). T=tau -> f/f_0 = 1/e ~ 0.368.
     [INPUT: f_0=0.95, T=tau_alpha_theory] [EXPECTED: f/f_0 ~ 0.368]
  4. Relative deviation: |tau_emp - tau_theory| / tau_theory.
     [INPUT: tau_emp=9500, tau_theory=10240] [EXPECTED: rel_dev ~ 0.072]

No _nN suffix; production N=1024 per PROT-018 rule 3.
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "tau_alpha_measurement_protocol_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 1024

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    ALPHA_LIST = [0.05, 0.10]
    N_PROBE_PATTERNS = 10    # patterns to test retrieval on
    T_WRITE_STEPS = [10, 50, 100, 200]  # streaming write counts
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_LIST = [0.05, 0.10, 0.15, 0.20]
    N_PROBE_PATTERNS = 20
    T_WRITE_STEPS = [10, 50, 100, 200, 500, 1000]

HP_REL_DEV = 0.15       # 15% of theory
HF_REL_DEV = 3.0        # 3x theory -> instrumentation failure
HP_FRACTION = 0.75      # >= 75% of alphas within HP
MIDDLE_FRACTION = 0.50  # >= 50% for MIDDLE

TAU_THEORY_SCALE = 50   # In this measurement, tau_alpha is in units of T_writes:
                         # tau_alpha = N / alpha / N = 1/alpha (normalized write units)
                         # For N=1024, alpha=0.10: tau_alpha_theory = 1/0.10 = 10 write-units

# ---- FORMULA SELF-TESTS ----
# Test 1
_tau_t1 = 1024 / 0.10
assert abs(_tau_t1 - 10240.0) < 1e-6, f"tau_theory T1: {_tau_t1}"
# Test 2
_tau_t2 = 1024 / 0.20
assert abs(_tau_t2 - 5120.0) < 1e-6, f"tau_theory T2: {_tau_t2}"
# Test 3
_f_ratio = math.exp(-1.0)
assert abs(_f_ratio - 0.36787944) < 1e-4, f"exp decay T3: {_f_ratio}"
# Test 4
_rel_dev = abs(9500 - 10240) / 10240
assert abs(_rel_dev - 0.07226) < 1e-3, f"rel_dev T4: {_rel_dev}"
print(f"[formula_selftest] tau_theory(N=1024,a=0.10)={_tau_t1:.0f} "
      f"tau_theory(N=1024,a=0.20)={_tau_t2:.0f} "
      f"exp_decay_at_tau={_f_ratio:.4f} rel_dev_T4={_rel_dev:.4f} OK", flush=True)


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = 5) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def measure_fidelity(W: np.ndarray, Xi_probe: np.ndarray,
                     Xi_targets: np.ndarray, seed: int,
                     n_dim: int) -> float:
    """Measure mean cosine fidelity of retrieved patterns vs targets."""
    rng = np.random.RandomState(seed)
    fids = []
    n_test = min(Xi_probe.shape[0], Xi_targets.shape[0])
    for i in range(n_test):
        probe = Xi_probe[i].copy()
        flip = rng.random(n_dim) < 0.10
        probe[flip] *= -1.0
        r = hopfield_retrieve(W, probe)
        fids.append(cosine_sim(r, Xi_targets[i]))
    return float(np.mean(fids)) if fids else 0.0


def fit_tau_alpha(write_steps: List[int], fidelities: List[float],
                  f_0: float) -> float:
    """Fit tau_alpha from exponential decay f(t) = f_0 * exp(-t/tau).

    Uses log-linear regression on log(f(t)/f_0) = -t/tau.
    Returns tau_emp in units of write steps.
    """
    if f_0 < 1e-6:
        return float("nan")
    log_ratios = []
    ts = []
    for t, f in zip(write_steps, fidelities):
        ratio = f / f_0
        if ratio > 1e-6:
            log_ratios.append(math.log(ratio))
            ts.append(float(t))
    if len(ts) < 2:
        return float("nan")
    # -1/tau = slope of log_ratio vs t
    ts_arr = np.array(ts)
    lr_arr = np.array(log_ratios)
    slope = float(np.polyfit(ts_arr, lr_arr, 1)[0])
    if abs(slope) < 1e-12:
        return float("nan")
    tau_emp = -1.0 / slope
    return tau_emp


def _instrumentation_selftest():
    """Verify all claimed metrics are non-null at small scale."""
    N_t = 256
    alpha = 0.10
    M_t = int(alpha * N_t)  # 25 patterns
    seed = 42
    rng = np.random.RandomState(seed)

    Xi_stored = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W = Xi_stored.T @ Xi_stored / float(N_t)
    np.fill_diagonal(W, 0.0)

    # Test fidelity measurement returns non-null
    f0 = measure_fidelity(W, Xi_stored[:5], Xi_stored[:5], seed, N_t)
    assert f0 is not None and not math.isnan(f0), f"fidelity null: {f0}"
    assert f0 > 0.0, f"fidelity zero at N={N_t} M={M_t}: {f0}"

    # Test tau fit returns non-null
    # Simulate decay
    decay_fids = [f0 * math.exp(-t / 50) for t in [10, 20, 40, 80]]
    tau_fit = fit_tau_alpha([10, 20, 40, 80], decay_fids, f0)
    assert tau_fit is not None and not math.isnan(tau_fit), f"tau_fit null: {tau_fit}"
    assert tau_fit > 0, f"tau_fit non-positive: {tau_fit}"

    # Test at least 1 alpha survives the sweep (ALPHA_LIST non-empty at smoke scale)
    assert len(ALPHA_LIST) > 0, "ALPHA_LIST empty at smoke scale"
    assert len(T_WRITE_STEPS) >= 2, f"need >= 2 write steps; got {T_WRITE_STEPS}"

    print(f"[selftest] PASS: fidelity_f0={f0:.4f} tau_fit={tau_fit:.2f} "
          f"alpha_list={ALPHA_LIST} write_steps={T_WRITE_STEPS} OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    results = {}

    for alpha in ALPHA_LIST:
        M = max(1, int(alpha * N))
        # tau_alpha_theory in write-step units: each write adds 1 pattern
        # tau_alpha = N / (alpha * N) = 1 / alpha (normalized)
        # In absolute write steps: tau_theory = N / alpha (pattern count scale)
        # But we measure in # of streaming writes; normalize to M_0 scale:
        tau_theory = float(N) / alpha  # write steps at which fidelity drops to 1/e

        # Store initial M patterns
        Xi_init = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
        W = Xi_init.T @ Xi_init / float(N)
        np.fill_diagonal(W, 0.0)

        # Baseline fidelity
        f_0 = measure_fidelity(W, Xi_init[:N_PROBE_PATTERNS], Xi_init[:N_PROBE_PATTERNS], seed, N)

        # Streaming writes and fidelity decay
        fidelities = []
        for T in T_WRITE_STEPS:
            # Add T streaming writes (new random patterns)
            Xi_new = rng.choice([-1.0, 1.0], size=(T, N)).astype(np.float64)
            W_updated = W + Xi_new.T @ Xi_new / float(N)
            # Note: no forgetting rule here; just additive writes (test aging signal)
            f_t = measure_fidelity(W_updated, Xi_init[:N_PROBE_PATTERNS],
                                   Xi_init[:N_PROBE_PATTERNS], seed, N)
            fidelities.append(f_t)

        # Fit tau_alpha
        tau_emp = fit_tau_alpha(T_WRITE_STEPS, fidelities, f_0 if f_0 > 1e-6 else 1.0)
        rel_dev = abs(tau_emp - tau_theory) / tau_theory if (tau_emp is not None and
                                                              not math.isnan(tau_emp)) else float("nan")

        hp_ok = (tau_emp is not None and
                 not math.isnan(tau_emp) and
                 rel_dev <= HP_REL_DEV)
        hf_ok = (tau_emp is None or
                 math.isnan(tau_emp) or
                 rel_dev > HF_REL_DEV)

        print(f"  [seed={seed} alpha={alpha:.2f}] f_0={f_0:.4f} "
              f"fids={[f'{f:.3f}' for f in fidelities[:4]]} "
              f"tau_emp={tau_emp:.1f} tau_theory={tau_theory:.1f} "
              f"rel_dev={rel_dev:.3f} hp={hp_ok}", flush=True)

        results[str(alpha)] = {
            "alpha": float(alpha),
            "M": M,
            "N": N,
            "f_0": float(f_0),
            "fidelities": fidelities,
            "tau_emp": float(tau_emp) if tau_emp is not None and not math.isnan(tau_emp) else None,
            "tau_theory": float(tau_theory),
            "rel_dev": float(rel_dev) if not math.isnan(rel_dev) else None,
            "hp_ok": bool(hp_ok),
            "hf_ok": bool(hf_ok),
        }

    return {"alpha_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    alpha_hp = {str(a): [] for a in ALPHA_LIST}
    alpha_rel_devs = {str(a): [] for a in ALPHA_LIST}

    for sd in per_seed.values():
        for ak, v in sd.get("alpha_results", {}).items():
            if ak in alpha_hp:
                alpha_hp[ak].append(v.get("hp_ok", False))
                if v.get("rel_dev") is not None:
                    alpha_rel_devs[ak].append(v["rel_dev"])

    alpha_pass = []
    hf_triggered = False
    for ak in [str(a) for a in ALPHA_LIST]:
        hp_votes = alpha_hp.get(ak, [])
        rel_devs = alpha_rel_devs.get(ak, [])
        if not hp_votes:
            alpha_pass.append(False)
            continue
        frac_hp = sum(hp_votes) / len(hp_votes)
        alpha_pass.append(frac_hp >= HP_FRACTION)
        # HF: mean rel_dev > 3x
        if rel_devs and float(np.mean(rel_devs)) > HF_REL_DEV:
            hf_triggered = True

    n_alpha_pass = sum(alpha_pass)
    frac_pass = n_alpha_pass / len(ALPHA_LIST) if ALPHA_LIST else 0.0

    # Aggregate relative deviations for summary
    all_devs = {ak: float(np.mean(v)) if v else float("nan")
                for ak, v in alpha_rel_devs.items()}
    summary = (f"alpha_pass={n_alpha_pass}/{len(ALPHA_LIST)} "
               f"frac_hp={frac_pass:.2f} (HP>={HP_FRACTION}) "
               f"mean_rel_devs={all_devs} "
               f"HP_REL_DEV={HP_REL_DEV} HF_REL_DEV={HF_REL_DEV}")

    if hf_triggered:
        return ("HARD_FAIL", f"HARD_FAIL: HF triggered (rel_dev > {HF_REL_DEV}). {summary}")
    if frac_pass >= HP_FRACTION:
        return ("HARD_PASS", f"HARD_PASS: {summary}")
    if frac_pass >= MIDDLE_FRACTION:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: frac_pass={frac_pass:.2f} < {MIDDLE_FRACTION}. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] tau_alpha measurement N={N} alphas={ALPHA_LIST}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_s,
    "alpha_list": ALPHA_LIST,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
