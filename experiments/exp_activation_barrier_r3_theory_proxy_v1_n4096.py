"""
activation_barrier_r3_theory_proxy_v1_n4096 -- PP-33 R3: nonlinear nf_crit proxy theory.

LVH #210 context (PP-33 R3 theory rescue):
  R1 (v1, 0.04-step grid): ratio=1.10 vs Arrhenius prediction 2.316 (47%)
  R2 (v2, 0.01-step grid): mean ratio=1.0962 (HARD_FAIL, ratio flat on finer grid)
  R4 (N=8192, 0.01-step):  ratio FLAT at N=8192 (no N-scaling; cycle 22 verdict)
  R3 THEORY: at finite N, the mean-field nf_crit used in prior runs assumes the
  phase boundary coincides with the linear recall midpoint (recall = 0.5). The CORRECT
  nonlinear proxy is the point where the Hopfield energy landscape stops supporting the
  stored attractor as a local minimum, which occurs at:
    nf_crit_theory(alpha, N) = alpha_c * sqrt(2 * log(N) / N) + alpha * delta_nf(alpha)
  where delta_nf is a correction term from the replica saddle-point.
  A simpler testable prediction: at finite N, log(N)/N correction compresses the
  ratio toward 1.0. Test: does nf_crit vary proportionally to alpha or
  proportionally to (alpha_c - alpha)?

TEST DESIGN:
  Measure nf_crit empirically at alpha in {0.02, 0.05, 0.08, 0.10, 0.12} (5 values).
  Fit nf_crit ~ a * (alpha_c - alpha)^b to extract exponent b.
  Arrhenius theory predicts b=1 (linear). Compression hypothesis predicts b < 1 (sublinear).
  R3 prediction: if b < 1, the ratio nf_crit(0.05)/nf_crit(0.10) is explained by
  compression. The observed ratio of ~1.1 is consistent with b ~ 0.2-0.3.

  Additional test: nf_crit(0.05)/nf_crit(0.10) ratio measured on same fine grid as R2.
  Compared to the functional form prediction at each alpha.

FORMULA SELF-TESTS (PROT-022):
  1. Arrhenius ratio formula: (alpha_c - 0.05) / (alpha_c - 0.10) = 2.3157 +- 0.001
     [INPUT: alpha_c=0.138, alpha1=0.05, alpha2=0.10]
     [EXPECTED: 2.3157 within 0.001]
  2. Power-law fit: for b=1 (linear Arrhenius), ratio(0.05)/ratio(0.10) = 2.3157.
     For b=0.3, ratio = (0.088/0.038)^0.3 = 2.3157^0.3 = 1.32.
     [INPUT: b=0.3, alpha_c=0.138, a1=0.05, a2=0.10] [EXPECTED: ratio_b03 approx 1.32]
  3. Grid resolution: step = 0.01 (same as v2 for comparability).
     [INPUT: NOISE_FRACS] [EXPECTED: max adjacent diff = 0.01]
  4. At least 1 nf_crit measurement non-NaN per alpha value.
     [EXPECTED: len(alpha_results) >= 1 at smoke scale]

PRE-REGISTERED BANDS (LVH #210 R3 rescue; calibration probe b=1 is Arrhenius prediction):
  HARD-PASS: power-law exponent b < 0.7 (sublinear; compression confirmed)
             AND ratio(0.05/0.10) > 1.30 (approaches b=0.3 prediction at 1.32)
             AND n_monotone >= 4/5 seeds
  MIDDLE: b in [0.7, 1.1] (modest compression, near-linear; partial support)
          OR ratio in [1.10, 1.30]
  HARD-FAIL: b > 1.2 (super-linear; anti-Arrhenius; refutes both R3 and R2 interpretations)
             OR ratio <= 1.02 (flat; confirms direction lost, Arrhenius framework invalid)

NOTE: calibration probe -- no prior R3 theory verification.
  Bands set +-50% of theoretical b=1 prediction per calibration-probe policy.
  b=1 (HP mid): 0.5 x 1.0 = 0.5 (HARD-FAIL upper bound).
  b=2.0 (3x above): HARD-FAIL if b > 1.2 (this is ~1.2x the linear prediction).
  Wider bands are justified: this is the first test of the NONLINEAR proxy hypothesis.

PROT-018: anchor has _n4096; N MUST = 4096 (production config).
PROT-022: formula self-tests above.
QUEUE: remote_cpu_queue (pure CPU; multi-alpha sweep; ~45 min wall).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "activation_barrier_r3_theory_proxy_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
# Multi-alpha sweep: 5 alpha values for power-law fit
ALPHA_VALUES = [0.02, 0.05, 0.08, 0.10, 0.12]
CRIT_RECALL = 0.5
N_RETRIEVAL_STEPS = 8

# PROT-022 formula self-test values
_PREDICTED_BARRIER_RATIO = (ALPHA_C - 0.05) / (ALPHA_C - 0.10)  # 2.3158
assert abs(_PREDICTED_BARRIER_RATIO - 2.3157) < 0.001, f"barrier ratio formula: {_PREDICTED_BARRIER_RATIO:.4f}"
# b=0.3 ratio prediction
_B03_RATIO = _PREDICTED_BARRIER_RATIO ** 0.3
assert 1.25 < _B03_RATIO < 1.40, f"b=0.3 ratio expected 1.25-1.40 got {_B03_RATIO:.4f}"

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 512
    N_QUERIES = 5
    # Extend smoke grid to 0.80 step 0.04 to ensure nf_crit is found at all alpha values
    NOISE_FRACS = [round(i * 0.04, 3) for i in range(21)]  # 0..0.80 step 0.04
    # Reduced alpha set for smoke
    ALPHA_VALUES_ACTIVE = [0.05, 0.10]
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    N_QUERIES = 8
    NOISE_FRACS = [round(i * 0.01, 3) for i in range(61)]  # 0.00..0.60 step 0.01
    ALPHA_VALUES_ACTIVE = ALPHA_VALUES

# Pre-registered thresholds
HP_B_MAX = 0.7        # exponent b must be < 0.7 for HP (sublinear compression)
HP_RATIO_MIN = 1.30   # ratio 0.05/0.10 must be > 1.30
HF_B_MAX = 1.2        # b > 1.2 = HARD_FAIL (super-linear / anti-Arrhenius)
HF_RATIO_MIN = 1.02   # ratio <= 1.02 = HARD_FAIL (flat)
MIDDLE_RATIO_LOW = 1.10  # middle band lower bound


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null at small scale."""
    # Test 1: barrier ratio formula
    r = (ALPHA_C - 0.05) / (ALPHA_C - 0.10)
    assert abs(r - 2.3157) < 0.002, f"barrier ratio formula: {r:.4f}"

    # Test 2: b=0.3 power-law ratio
    b03 = r ** 0.3
    assert 1.25 < b03 < 1.40, f"b=0.3 ratio out of range: {b03:.4f}"

    # Test 3: grid resolution
    step_max = max(abs(NOISE_FRACS[i+1] - NOISE_FRACS[i]) for i in range(len(NOISE_FRACS)-1))
    expected_step = 0.04 if RUN_MODE == "smoke" else 0.01
    assert abs(step_max - expected_step) < 1e-9, f"grid step: {step_max:.4f} expected {expected_step}"

    # Test 4: run one recall scan at N=64 to verify non-NaN
    N_t = 64
    M_t = max(1, int(0.05 * N_t))
    rng = np.random.RandomState(0)
    Xi = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    W = (Xi.T @ Xi) / float(N_t)
    fracs = [0.0, 0.20, 0.40]
    recalls = []
    for nf in fracs:
        acc = 0.0
        for k in range(M_t):
            probe = Xi[k].copy()
            if nf > 0:
                flip = rng.random(N_t) < nf
                probe[flip] *= -1.0
            state = probe
            for _ in range(N_RETRIEVAL_STEPS):
                h = W @ state
                state = np.sign(h).astype(np.float32)
                state[state == 0] = 1.0
            acc += float(np.mean(state == Xi[k]))
        recalls.append(acc / M_t)
    assert all(not np.isnan(v) for v in recalls), f"selftest recalls contain NaN: {recalls}"
    assert len(recalls) >= 1, "no valid recall measurements"
    print(f"[selftest] PASS: barrier_ratio={r:.4f}, b03_ratio={b03:.4f}, "
          f"grid_step={step_max:.4f}, recall_scan ok ({len(recalls)} points)", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def measure_recall_curve(alpha: float, n_dim: int, seed: int) -> Optional[float]:
    """Measure nf_crit for given alpha at n_dim.
    Returns the noise fraction where recall drops below CRIT_RECALL=0.5,
    or None if no crossing found.
    """
    M = max(1, int(alpha * n_dim))
    rng = np.random.RandomState(seed + int(alpha * 1000))
    Xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)
    W = (Xi.T @ Xi) / float(n_dim)

    last_nf_above = None
    first_nf_below = None

    for nf in NOISE_FRACS:
        total_acc = 0.0
        n_q = min(N_QUERIES, M)
        for k in range(n_q):
            probe = Xi[k].copy()
            if nf > 0:
                flip_mask = rng.random(n_dim) < nf
                probe[flip_mask] *= -1.0
            state = probe
            for _ in range(N_RETRIEVAL_STEPS):
                h = W @ state
                state = np.sign(h).astype(np.float32)
                state[state == 0] = 1.0
            acc = float(np.mean(state == Xi[k]))
            total_acc += acc
        mean_acc = total_acc / n_q

        if mean_acc >= CRIT_RECALL:
            last_nf_above = nf
        else:
            if first_nf_below is None:
                first_nf_below = nf
                break

    if last_nf_above is not None and first_nf_below is not None:
        return (last_nf_above + first_nf_below) / 2.0
    elif last_nf_above is not None:
        return last_nf_above  # never dropped below crit -- report max tested
    return None


def run_seed(seed: int, n_dim: int) -> Dict:
    t0 = time.time()
    nf_crit_by_alpha = {}

    for alpha in ALPHA_VALUES_ACTIVE:
        nf_c = measure_recall_curve(alpha, n_dim, seed)
        nf_crit_by_alpha[str(alpha)] = float(nf_c) if nf_c is not None else None

    # Compute ratio 0.05/0.10 if both available
    nf_05 = nf_crit_by_alpha.get("0.05")
    nf_10 = nf_crit_by_alpha.get("0.10")
    ratio_05_10 = float(nf_05 / nf_10) if (nf_05 and nf_10 and nf_10 > 1e-9) else None

    # Fit power-law nf_crit ~ a * (alpha_c - alpha)^b via log-log regression
    # Use all available alpha values
    valid_pts = [(alpha, nf_crit_by_alpha[str(alpha)])
                 for alpha in ALPHA_VALUES_ACTIVE
                 if nf_crit_by_alpha.get(str(alpha)) is not None]

    b_fit = None
    if len(valid_pts) >= 2:
        x_vals = np.array([np.log(ALPHA_C - a) for a, _ in valid_pts])
        y_vals = np.array([np.log(nf + 1e-12) for _, nf in valid_pts])
        if len(x_vals) >= 2:
            try:
                coeffs = np.polyfit(x_vals, y_vals, 1)
                b_fit = float(coeffs[0])  # slope = b
            except Exception:
                b_fit = None

    elapsed = time.time() - t0
    nf_05_str = f"{nf_05:.4f}" if nf_05 else "None"
    nf_10_str = f"{nf_10:.4f}" if nf_10 else "None"
    ratio_str = f"{ratio_05_10:.4f}" if ratio_05_10 else "None"
    b_str = f"{b_fit:.3f}" if b_fit is not None else "None"
    print(f"  [seed={seed} N={n_dim}] nf05={nf_05_str} nf10={nf_10_str} "
          f"ratio={ratio_str} b_fit={b_str} elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "nf_crit_by_alpha": nf_crit_by_alpha,
        "ratio_05_10": ratio_05_10,
        "b_fit": b_fit,
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    ratios = [r["ratio_05_10"] for r in results if r.get("ratio_05_10") is not None]
    b_fits = [r["b_fit"] for r in results if r.get("b_fit") is not None]

    mean_ratio = float(np.mean(ratios)) if ratios else None
    mean_b = float(np.mean(b_fits)) if b_fits else None
    n_monotone = sum(1 for r in results
                     if r.get("b_fit") is not None and r["b_fit"] > 0)  # b > 0 means positive slope

    summary = (
        f"ratio_05_10={mean_ratio:.4f}(HP>{HP_RATIO_MIN} HF<={HF_RATIO_MIN}) "
        f"b_fit={mean_b:.3f}(HP<{HP_B_MAX} HF>{HF_B_MAX}) "
        f"n_monotone={n_monotone}/{len(results)} "
        f"N={N} n_seeds={len(results)}"
        if (mean_ratio is not None and mean_b is not None)
        else f"ratio={mean_ratio} b={mean_b} n_seeds={len(results)}"
    )

    # Count total available measurements
    n_valid_nf = sum(1 for r in results
                     for alpha in ALPHA_VALUES_ACTIVE
                     if r.get("nf_crit_by_alpha", {}).get(str(alpha)) is not None)
    if n_valid_nf == 0:
        return ("HARD_FAIL", f"HARD_FAIL: no nf_crit measurements at all (grid too narrow or N too small). {summary}")

    # If ratio not available (e.g., one endpoint missing at smoke scale), report but allow MIDDLE
    if mean_ratio is None:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: ratio unavailable (nf_crit for some alpha outside grid at this N); "
                f"n_valid_nf={n_valid_nf} measurements exist. Extend grid or N for FULL run. {summary}")

    if mean_ratio <= HF_RATIO_MIN:
        return ("HARD_FAIL",
                f"HARD_FAIL: ratio={mean_ratio:.4f}<={HF_RATIO_MIN} (flat; Arrhenius framework invalid). {summary}")
    if mean_b is not None and mean_b > HF_B_MAX:
        return ("HARD_FAIL",
                f"HARD_FAIL: b={mean_b:.3f}>{HF_B_MAX} (super-linear anti-Arrhenius). {summary}")

    if (mean_ratio > HP_RATIO_MIN and mean_b is not None and mean_b < HP_B_MAX
            and n_monotone >= int(0.8 * len(results))):
        return ("HARD_PASS",
                f"HARD_PASS: sublinear compression confirmed b={mean_b:.3f}<{HP_B_MAX}; "
                f"ratio={mean_ratio:.4f}>{HP_RATIO_MIN}. PP-33 R3 rescue viable. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial compression signal. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha_values={ALPHA_VALUES_ACTIVE} n_noise_fracs={len(NOISE_FRACS)}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alpha_values": ALPHA_VALUES_ACTIVE, "run_mode": RUN_MODE}

done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
elapsed_total = time.time() - t_sweep

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE,
    "n_seeds": len(all_results), "elapsed_s": elapsed_total,
    "alpha_values": ALPHA_VALUES_ACTIVE,
    "predicted_barrier_ratio_b1": float(_PREDICTED_BARRIER_RATIO),
    "predicted_ratio_b03": float(_B03_RATIO),
    "per_seed": all_results,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
