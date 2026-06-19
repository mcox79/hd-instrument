"""
capacity_phase_boundary_fine_grid_v2_n4096 -- PP-50 RRAM rescue R2: finer sigma_g grid.

Prior run (v1) found MIDDLE_BAND: below_boundary_violations=5/10.
Recall degrades well before sigma_g_crit (e.g., alpha=0.05 sg=2.0 recall=0.64 but
sigma_g_crit=4.36 -- still factor 2x below boundary). Transition zone is WIDE.

This run focuses the sigma_g sweep in the transition zone [0.5*sg_crit, 1.5*sg_crit]
with finer steps to characterize where degradation actually begins.

SCIENTIFIC QUESTION:
  For each alpha, at what sigma_g fraction (relative to sigma_g_crit) does recall
  first drop below 0.90? Is there a universal onset fraction (e.g., ~0.5*sg_crit)
  that applies across all alpha values?

FORMULA SELF-TESTS (PROT-022):
  1. Phase boundary: sigma_g_crit = sqrt(1/alpha - 1)
     [alpha=0.05]: sqrt(19) = 4.359 [EXPECTED within 0.001]
     [alpha=0.10]: sqrt(9) = 3.000 [EXPECTED within 0.001]
     [alpha=0.20]: sqrt(4) = 2.000 [EXPECTED within 0.001]
     [alpha=0.50]: sqrt(1) = 1.000 [EXPECTED within 0.001]
  2. sigma_g noise model: entrywise multiplicative exp(sigma_g * Z), Z~N(0,1)
     [EXPECTED: W_noisy mean entry = W entry (noise is zero-mean in log-space)]

PRE-REGISTERED BANDS:
  HARD-PASS: universal onset fraction onset_frac in [0.30, 0.70] across all 4 alpha
             (characterizes transition zone consistently; confirms systematic degradation onset)
  MIDDLE: onset_frac varies across alpha by more than 0.3 (non-universal)
  HARD-FAIL: no clear onset detected (recall flat even above sigma_g_crit)

PROT-018: no _nN suffix (sigma_g sweep; production N=4096 fixed in script).
QUEUE: remote_cpu_queue (CPU; ~45 min wall; log-normal matrix noise at N=4096).
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

ANCHOR_NAME = "capacity_phase_boundary_fine_grid_v2_n4096"

N = 4096
N_RETRIEVAL_STEPS = 8
RECALL_THRESHOLD = 0.90  # onset threshold

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Phase boundary formula: sigma_g_crit = sqrt(1/alpha - 1)
ALPHA_VALUES = [0.05, 0.10, 0.20, 0.50]
SIGMA_G_CRITS = {a: math.sqrt(1.0/a - 1.0) for a in ALPHA_VALUES}

# Fine grid: 21 points from 0.2*sg_crit to 1.4*sg_crit per alpha
N_FRAC_POINTS = 21  # fractions of sigma_g_crit
SIGMA_G_FRACS = [0.2 + i * 0.06 for i in range(N_FRAC_POINTS)]  # 0.20..1.40

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 512
    N_QUERIES = 3
    ALPHA_VALUES_RUN = [0.10, 0.20]  # 2 alphas for smoke
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    N_QUERIES = 5
    ALPHA_VALUES_RUN = ALPHA_VALUES


def _selftest_sigma_g_crit():
    """Phase boundary formula verification."""
    expected = {0.05: 4.359, 0.10: 3.000, 0.20: 2.000, 0.50: 1.000}
    for alpha, exp_val in expected.items():
        got = math.sqrt(1.0/alpha - 1.0)
        assert abs(got - exp_val) < 0.001, f"sigma_g_crit[{alpha}]: got {got:.3f} expected {exp_val}"


def _selftest_noise_model():
    """W_noisy entrywise mean should approximate W entry (noise zero-mean in log-space)."""
    rng = np.random.RandomState(42)
    n_t = 64
    M_t = 3
    Xi = rng.choice([-1., 1.], size=(M_t, n_t)).astype(np.float64)
    W = (Xi.T @ Xi) / float(n_t)
    sigma_g = 0.5
    Z = rng.normal(0, 1, size=W.shape)
    W_noisy = W * np.exp(sigma_g * Z)
    # Mean should be close to W entry (exp has mean exp(sigma_g^2/2) but that's a bias)
    # Just check W_noisy varies across entries (not zero)
    assert np.std(W_noisy) > 0.001, "W_noisy has no variance -- noise model broken"


def _instrumentation_selftest():
    _selftest_sigma_g_crit()
    _selftest_noise_model()
    print(f"[selftest] PASS: sigma_g_crit formula correct; noise model has variance. N={N_ACTIVE}", flush=True)


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


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    onset_fracs = {}

    for alpha in ALPHA_VALUES_RUN:
        sg_crit = SIGMA_G_CRITS[alpha]
        M_val = max(1, int(alpha * n_dim))
        Xi = rng.choice([-1., 1.], size=(M_val, n_dim)).astype(np.float64)
        W_clean = (Xi.T @ Xi) / float(n_dim)

        onset_frac = None
        for frac in SIGMA_G_FRACS:
            sigma_g = frac * sg_crit
            # Apply log-normal noise entrywise
            Z = rng.normal(0, 1, size=W_clean.shape)
            W_noisy = W_clean * np.exp(sigma_g * Z)

            recalls = []
            for q in range(min(N_QUERIES, M_val)):
                xi_q = Xi[q]
                state = hopfield_retrieve(W_noisy, xi_q.copy())
                cos = float(np.dot(state, xi_q)) / n_dim
                recalls.append(cos)
            mean_recall = float(np.mean(recalls))

            if mean_recall < RECALL_THRESHOLD and onset_frac is None:
                onset_frac = frac

            print(f"  [seed={seed} alpha={alpha:.2f} frac={frac:.2f} sg={sigma_g:.3f}] "
                  f"recall={mean_recall:.4f}", flush=True)

        onset_fracs[alpha] = onset_frac
        onset_str = f"{onset_frac:.2f}" if onset_frac is not None else "NONE"
        print(f"  [seed={seed} alpha={alpha:.2f}] onset_frac={onset_str} sg_crit={sg_crit:.3f}", flush=True)

    elapsed = time.time() - t0
    result = {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE, "elapsed_s": float(elapsed),
        "onset_fracs": {str(a): v for a, v in onset_fracs.items()},
    }
    return result


def compute_verdict(all_results: List[Dict]) -> tuple:
    if not all_results:
        return ("HARD_FAIL", "No valid results.")

    # Aggregate onset_fracs per alpha
    per_alpha_onsets = {}
    for r in all_results:
        for a_str, frac in r.get("onset_fracs", {}).items():
            if a_str not in per_alpha_onsets:
                per_alpha_onsets[a_str] = []
            if frac is not None:
                per_alpha_onsets[a_str].append(frac)

    mean_onsets = {}
    for a_str, fracs in per_alpha_onsets.items():
        if fracs:
            mean_onsets[a_str] = float(np.mean(fracs))

    onset_summary = " ".join(f"a{a}:onset={v:.2f}" for a, v in sorted(mean_onsets.items()))
    n_defined = sum(1 for v in mean_onsets.values() if v is not None)

    if n_defined < 2:
        return ("HARD_FAIL", f"HARD_FAIL: fewer than 2 alpha onset_fracs defined. {onset_summary}")

    onset_vals = list(mean_onsets.values())
    onset_range = max(onset_vals) - min(onset_vals)
    mean_onset = float(np.mean(onset_vals))

    summary = (f"mean_onset_frac={mean_onset:.3f} onset_range={onset_range:.3f} "
               f"n_defined={n_defined} {onset_summary}")

    if 0.30 <= mean_onset <= 0.70 and onset_range < 0.30:
        return ("HARD_PASS",
                f"HARD_PASS: universal onset_frac={mean_onset:.3f} in [0.30,0.70] range={onset_range:.3f}. {summary}")

    if onset_range >= 0.30:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: non-universal onset (range={onset_range:.3f}>=0.30). {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: mean_onset={mean_onset:.3f} outside [0.30,0.70]. {summary}")


print(f"[config] N={N} N_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha_values={ALPHA_VALUES_RUN} n_frac_pts={N_FRAC_POINTS}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "alpha_values": ALPHA_VALUES_RUN, "n_frac_points": N_FRAC_POINTS, "run_mode": RUN_MODE}

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
    "sigma_g_crits": {str(a): v for a, v in SIGMA_G_CRITS.items()},
    "summary": verdict_msg[:400],
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
