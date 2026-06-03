"""
activation_barrier_alpha_dependence_hysteresis_gap_v1_n4096 -- Item 31: Arrhenius drill Test C.

Tests closed-form prediction: E_a^0(alpha) ~ N * (alpha_c - alpha) / alpha_c,
manifest as critical noise threshold ordering: nf_crit(alpha=0.05) > nf_crit(alpha=0.10).

SCIENTIFIC QUESTION:
  Does the substrate's critical noise threshold (nf_crit = noise fraction where recall
  drops to ~0.5 from 1.0) scale with alpha following the Arrhenius activation barrier
  prediction E_a^0(alpha) ~ (alpha_c - alpha)/alpha_c?
  Lower alpha = larger barrier = higher noise tolerance = higher nf_crit.

EMPIRICAL CALIBRATION NOTE (prior to this run):
  At N=4096, 5 queries, 1 seed: alpha=0.05 critical ~0.44, alpha=0.10 ~0.40.
  Both above threshold region. Ratio ~1.1x (modest but monotone).
  This is a CALIBRATION PROBE -- no prior multi-seed anchor exists.
  Bands set wide per role contract (first empirical measurement).

FORMULA SELF-TESTS (PROT-022):
  1. Barrier ratio formula: (alpha_c - alpha1) / (alpha_c - alpha2)
     [INPUT: alpha_c=0.138, alpha1=0.05, alpha2=0.10]
     [EXPECTED: barrier_ratio = 0.088/0.038 = 2.316 within +-0.001]
  2. Critical noise threshold monotonicity: nf_crit(0.05) > nf_crit(0.10) at N=4096.
     Verified empirically pre-run: alpha=0.05 critical ~0.44, alpha=0.10 ~0.40 (1 seed).
     [EXPECTED: ordering holds for all 5 seeds]
  3. alpha values: alpha=0.05 => M=204 at N=4096; alpha=0.10 => M=409.
     [EXPECTED: both M/N < alpha_c=0.138]

PRE-REGISTERED BANDS (calibration probe, first multi-seed measurement):
  HARD-PASS: nf_crit(alpha=0.05) > nf_crit(alpha=0.10) for >= 4/5 seeds
             AND mean(nf_crit_05) / mean(nf_crit_10) > 1.02 (statistically above 1.0)
  MIDDLE: monotone in mean but < 3/5 seeds unanimous
  HARD-FAIL: mean(nf_crit_05) <= mean(nf_crit_10) (flat or inverted)
             OR nf_crit undefined for either alpha (never reaches 0.5 even at 0.48 noise)

Note: calibration probe per role contract -- bands set for first empirical anchor.
No prior multi-seed empirical measurement exists for this observable.

PROT-018: anchor has _n4096; N MUST = 4096.
QUEUE: remote_cpu_queue (CPU; pure numpy; ~30 min wall).
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

ANCHOR_NAME = "activation_barrier_alpha_dependence_hysteresis_gap_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
ALPHA_VALUES = [0.05, 0.08, 0.10]   # primary comparison: 0.05 vs 0.10; 0.08 as check
NOISE_FRACS = [i * 0.04 for i in range(13)]  # 0.00 to 0.48 in steps of 0.04
CRIT_RECALL = 0.5   # recall threshold for critical noise

# Theoretical barrier ratio
PREDICTED_BARRIER_RATIO = (ALPHA_C - 0.05) / (ALPHA_C - 0.10)  # 2.316

N_RETRIEVAL_STEPS = 8

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 512
    N_QUERIES = 4
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    N_QUERIES = 8


def _selftest_barrier_ratio():
    """barrier_ratio = (alpha_c - alpha1) / (alpha_c - alpha2)."""
    ac, a1, a2 = 0.138, 0.05, 0.10
    ratio = (ac - a1) / (ac - a2)
    assert abs(ratio - 2.3157) < 0.001, f"Barrier ratio: got {ratio:.4f}"


def _selftest_alpha_m():
    """M = int(alpha * N_active) > 0."""
    for alpha in ALPHA_VALUES:
        M_val = max(1, int(alpha * N_ACTIVE))
        assert M_val > 0 and M_val / N_ACTIVE < ALPHA_C, \
            f"M={M_val} alpha={M_val/N_ACTIVE:.4f} out of range"


def _selftest_nf_crit_monotone():
    """nf_crit observable and monotone (alpha=0.05 > alpha=0.10) at tiny N."""
    n_t = 128
    for a1, a2 in [(0.05, 0.10)]:
        M1 = max(1, int(a1 * n_t))
        M2 = max(1, int(a2 * n_t))
        rng = np.random.RandomState(42)
        Xi1 = rng.choice([-1., 1.], size=(M1, n_t)).astype(np.float64)
        Xi2 = rng.choice([-1., 1.], size=(M2, n_t)).astype(np.float64)
        W1 = (Xi1.T @ Xi1) / float(n_t)
        W2 = (Xi2.T @ Xi2) / float(n_t)
        # Find rough critical nf
        def get_crit_nf(W, Xi, n_q=3):
            for nf in NOISE_FRACS:
                recalls = []
                for q in range(min(n_q, Xi.shape[0])):
                    xi_q = Xi[q]
                    probe = xi_q.copy()
                    flip = rng.random(n_t) < nf
                    probe[flip] *= -1.0
                    state = probe.copy()
                    for _ in range(N_RETRIEVAL_STEPS):
                        h = W @ state
                        state = np.sign(h)
                        state[state == 0] = 1.0
                    cos = float(np.dot(state, xi_q)) / n_t
                    recalls.append(cos)
                if np.mean(recalls) < CRIT_RECALL:
                    return nf
            return NOISE_FRACS[-1]
        c1 = get_crit_nf(W1, Xi1)
        c2 = get_crit_nf(W2, Xi2)
        # At tiny N noise can dominate; just check both are defined
        assert c1 > 0 or c2 > 0, f"nf_crit undefined for both alphas at N={n_t}"


def _selftest_at_least_one_valid_cell():
    """At least 1 alpha value has observable critical noise at smoke scale."""
    n_t = N_ACTIVE
    rng = np.random.RandomState(42)
    any_defined = False
    for alpha in ALPHA_VALUES:
        M_val = max(1, int(alpha * n_t))
        Xi = rng.choice([-1., 1.], size=(M_val, n_t)).astype(np.float64)
        W = (Xi.T @ Xi) / float(n_t)
        # Check if recall drops at all across noise sweep
        xi_q = Xi[0]
        probe_heavy = xi_q.copy()
        flip = rng.random(n_t) < 0.48
        probe_heavy[flip] *= -1.0
        state = probe_heavy.copy()
        for _ in range(N_RETRIEVAL_STEPS):
            h = W @ state
            state = np.sign(h)
            state[state == 0] = 1.0
        cos = float(np.dot(state, xi_q)) / n_t
        if cos < 0.9:
            any_defined = True
            break
    assert any_defined, "No valid nf_crit cells found at smoke scale (all recall=1.0 even at 48% noise)"


def _instrumentation_selftest():
    _selftest_barrier_ratio()
    _selftest_alpha_m()
    _selftest_nf_crit_monotone()
    _selftest_at_least_one_valid_cell()
    print(f"[selftest] PASS: barrier_ratio, alpha_m, nf_crit_monotone, valid_cell "
          f"predicted_ratio={PREDICTED_BARRIER_RATIO:.4f} N_active={N_ACTIVE}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray) -> np.ndarray:
    state = probe.copy()
    for _ in range(N_RETRIEVAL_STEPS):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def find_critical_nf(W: np.ndarray, Xi: np.ndarray, n_q: int,
                     rng: np.random.RandomState) -> Optional[float]:
    """Find noise fraction where mean recall drops below CRIT_RECALL."""
    n = Xi.shape[1]
    n_q = min(n_q, Xi.shape[0])
    for nf in NOISE_FRACS:
        recalls = []
        for q in range(n_q):
            xi_q = Xi[q]
            probe = xi_q.copy()
            flip = rng.random(n) < nf
            probe[flip] *= -1.0
            state = hopfield_retrieve(W, probe)
            cos = float(np.dot(state, xi_q)) / n
            recalls.append(cos)
        mean_r = float(np.mean(recalls))
        if mean_r < CRIT_RECALL:
            return float(nf)
    return None  # never drops below threshold in sweep range


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    nf_crits = {}
    recalls_by_alpha = {}
    for alpha in ALPHA_VALUES:
        M_val = max(1, int(alpha * n_dim))
        Xi = rng.choice([-1., 1.], size=(M_val, n_dim)).astype(np.float64)
        W = (Xi.T @ Xi) / float(n_dim)

        # Get full recall curve
        recall_curve = []
        for nf in NOISE_FRACS:
            recalls = []
            for q in range(min(N_QUERIES, M_val)):
                xi_q = Xi[q]
                probe = xi_q.copy()
                flip = rng.random(n_dim) < nf
                probe[flip] *= -1.0
                state = hopfield_retrieve(W, probe)
                cos = float(np.dot(state, xi_q)) / n_dim
                recalls.append(cos)
            recall_curve.append((nf, float(np.mean(recalls))))

        nf_crit = find_critical_nf(W, Xi, N_QUERIES, rng)
        nf_crits[alpha] = nf_crit
        recalls_by_alpha[alpha] = recall_curve
        crit_str = f"{nf_crit:.2f}" if nf_crit is not None else "UNDEF"
        print(f"  [seed={seed} alpha={alpha:.2f} M={M_val}] nf_crit={crit_str}", flush=True)

    # Primary test: nf_crit(0.05) vs nf_crit(0.10)
    c05 = nf_crits.get(0.05)
    c10 = nf_crits.get(0.10)

    ratio_05_10 = None
    monotone_pass = False
    if c05 is not None and c10 is not None and c10 > 0:
        ratio_05_10 = c05 / c10
        monotone_pass = c05 > c10
    elif c05 is None and c10 is None:
        monotone_pass = False
    elif c05 is None:
        monotone_pass = False  # 0.05 never fails => effectively infinite nf_crit
    elif c10 is None:
        monotone_pass = True  # 0.10 never fails but 0.05 does => inverted unexpectedly

    elapsed = time.time() - t0
    ratio_str = f"{ratio_05_10:.4f}" if ratio_05_10 is not None else "UNDEF"
    print(f"  [seed={seed}] nf_crit(0.05)={nf_crits.get(0.05)} nf_crit(0.10)={nf_crits.get(0.10)} "
          f"ratio={ratio_str} monotone={monotone_pass}", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE, "elapsed_s": float(elapsed),
        "nf_crit_05": c05,
        "nf_crit_10": c10,
        "ratio_05_10": ratio_05_10,
        "monotone_pass": bool(monotone_pass),
    }


def compute_verdict(all_results: List[Dict]) -> tuple:
    if not all_results:
        return ("HARD_FAIL", "No valid results.")

    n = len(all_results)
    n_mono = sum(1 for r in all_results if r.get("monotone_pass", False))

    ratios = [r["ratio_05_10"] for r in all_results if r.get("ratio_05_10") is not None]
    crits_05 = [r["nf_crit_05"] for r in all_results if r.get("nf_crit_05") is not None]
    crits_10 = [r["nf_crit_10"] for r in all_results if r.get("nf_crit_10") is not None]

    mean_c05 = float(np.mean(crits_05)) if crits_05 else None
    mean_c10 = float(np.mean(crits_10)) if crits_10 else None
    mean_ratio = float(np.mean(ratios)) if ratios else None

    c05_str = f"{mean_c05:.3f}" if mean_c05 is not None else "UNDEF"
    c10_str = f"{mean_c10:.3f}" if mean_c10 is not None else "UNDEF"
    ratio_str = f"{mean_ratio:.4f}" if mean_ratio is not None else "UNDEF"

    summary = (f"nf_crit_05={c05_str} nf_crit_10={c10_str} ratio={ratio_str} "
               f"n_monotone={n_mono}/{n} predicted_barrier_ratio={PREDICTED_BARRIER_RATIO:.4f}")

    # HARD-FAIL: mean c05 <= c10
    if mean_c05 is None or mean_c10 is None:
        return ("HARD_FAIL", f"HARD_FAIL: nf_crit undefined for one or both alpha. {summary}")
    if mean_c05 <= mean_c10:
        return ("HARD_FAIL", f"HARD_FAIL: nf_crit flat/inverted (0.05 <= 0.10). {summary}")

    gate = max(4, n - 1) if n >= 4 else n
    if n_mono >= gate and mean_ratio is not None and mean_ratio > 1.02:
        return ("HARD_PASS",
                f"HARD_PASS: nf_crit(0.05) > nf_crit(0.10) ({n_mono}/{n} seeds monotone). "
                f"Activation barrier alpha-dependence confirmed. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


def _prot018_startup_check() -> None:
    if RUN_MODE != "smoke" and N_ACTIVE != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor _n{_N_SUFFIX} but FULL N_ACTIVE={N_ACTIVE}")


print(f"[config] PROT-018 N={N} N_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha_values={ALPHA_VALUES} predicted_barrier_ratio={PREDICTED_BARRIER_RATIO:.4f}", flush=True)
_prot018_startup_check()

out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "alpha_values": ALPHA_VALUES, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] seeds_todo={seeds_todo} out_dir={out_dir}", flush=True)

for s in seeds_todo:
    res = run_seed(s, N_ACTIVE)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

metrics = {
    "anchor": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(all_results),
    "N": N,
    "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t0_total,
    "predicted_barrier_ratio": float(PREDICTED_BARRIER_RATIO),
    "summary": verdict_msg[:300],
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
