"""
activation_barrier_fine_grid_v2_n4096 -- LVH #208 rescue R2: finer nf_frac grid.

Prior run (v1, 0.04-step grid) found ratio=1.10 vs Arrhenius-predicted 2.316 (47%).
LVH #208 annotation: most likely cause is coarse grid (0.04 step) compressing the
ratio -- adjacent grid points 0.40 vs 0.44 give ratio 1.10 by construction.
This run uses 0.01-step grid to resolve true nf_crit values more precisely.

SCIENTIFIC QUESTION:
  With 0.01-step nf_frac grid, does the measured ratio nf_crit(0.05)/nf_crit(0.10)
  approach the Arrhenius prediction of 2.316?
  If ratio increases substantially (e.g., 1.5+) this confirms coarse-grid artifact.
  If ratio stays ~1.1, barrier formula over-predicts for this substrate at N=4096.

FORMULA SELF-TESTS (PROT-022):
  1. Barrier ratio formula: (alpha_c - 0.05) / (alpha_c - 0.10) = 2.316 +- 0.001
     [INPUT: alpha_c=0.138, alpha1=0.05, alpha2=0.10]
     [EXPECTED: 2.3157 within 0.001]
  2. Grid resolution: min step size = 0.01 (4x finer than v1).
     [INPUT: NOISE_FRACS] [EXPECTED: max(diff)=0.01]

PRE-REGISTERED BANDS:
  HARD-PASS: ratio > 1.5 (confirms coarse-grid artifact; toward Arrhenius)
             AND n_monotone >= 4/5
  MIDDLE: 1.1 < ratio <= 1.5 (partial improvement; grid helped partially)
          OR monotone direction but ratio in [1.02, 1.5)
  HARD-FAIL: ratio <= 1.02 (flat; direction lost on finer grid)

PROT-018: no _nN suffix (alpha-sweep; production N=4096 fixed in script).
QUEUE: remote_cpu_queue (CPU; ~45 min wall; finer grid adds ~2x compute vs v1).
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

ANCHOR_NAME = "activation_barrier_fine_grid_v2_n4096"

N = 4096

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
ALPHA_VALUES = [0.05, 0.10]
PREDICTED_BARRIER_RATIO = (ALPHA_C - 0.05) / (ALPHA_C - 0.10)  # 2.3157

# Fine grid: 0.01 step from 0.00 to 0.60 (wider range too)
NOISE_FRACS_FINE = [round(i * 0.01, 3) for i in range(61)]  # 0.00..0.60 step 0.01
CRIT_RECALL = 0.5
N_RETRIEVAL_STEPS = 8

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 512
    N_QUERIES = 4
    NOISE_FRACS = [round(i * 0.04, 3) for i in range(13)]  # 0..0.48 step 0.04 (smoke: same as v1 for comparability)
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    N_QUERIES = 8
    NOISE_FRACS = NOISE_FRACS_FINE


def _selftest_barrier_ratio():
    """barrier_ratio = (alpha_c - 0.05) / (alpha_c - 0.10)."""
    ac, a1, a2 = 0.138, 0.05, 0.10
    ratio = (ac - a1) / (ac - a2)
    assert abs(ratio - 2.3157) < 0.001, f"Barrier ratio: got {ratio:.4f}"


def _selftest_grid_resolution():
    """Fine grid has step 0.01."""
    diffs = [round(NOISE_FRACS_FINE[i+1] - NOISE_FRACS_FINE[i], 4) for i in range(len(NOISE_FRACS_FINE)-1)]
    assert all(abs(d - 0.01) < 1e-6 for d in diffs), f"Grid step not 0.01: {set(diffs)}"


def _instrumentation_selftest():
    _selftest_barrier_ratio()
    _selftest_grid_resolution()
    print(f"[selftest] PASS: barrier_ratio={PREDICTED_BARRIER_RATIO:.4f} grid_step=0.01 N={N_ACTIVE}", flush=True)


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
    return None


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    nf_crits = {}
    for alpha in ALPHA_VALUES:
        M_val = max(1, int(alpha * n_dim))
        Xi = rng.choice([-1., 1.], size=(M_val, n_dim)).astype(np.float64)
        W = (Xi.T @ Xi) / float(n_dim)
        nf_crit = find_critical_nf(W, Xi, N_QUERIES, rng)
        nf_crits[alpha] = nf_crit
        crit_str = f"{nf_crit:.3f}" if nf_crit is not None else "UNDEF"
        print(f"  [seed={seed} alpha={alpha:.2f} M={M_val}] nf_crit={crit_str}", flush=True)

    c05 = nf_crits.get(0.05)
    c10 = nf_crits.get(0.10)

    ratio_05_10 = None
    monotone_pass = False
    if c05 is not None and c10 is not None and c10 > 0:
        ratio_05_10 = c05 / c10
        monotone_pass = c05 > c10
    elif c05 is None:
        monotone_pass = False
    elif c10 is None:
        monotone_pass = True

    elapsed = time.time() - t0
    ratio_str = f"{ratio_05_10:.4f}" if ratio_05_10 is not None else "UNDEF"
    print(f"  [seed={seed}] nf_crit(0.05)={c05} nf_crit(0.10)={c10} "
          f"ratio={ratio_str} monotone={monotone_pass} elapsed={elapsed:.1f}s", flush=True)

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
               f"n_monotone={n_mono}/{n} predicted_barrier_ratio={PREDICTED_BARRIER_RATIO:.4f} "
               f"grid_step=0.01")

    if mean_c05 is None or mean_c10 is None:
        return ("HARD_FAIL", f"HARD_FAIL: nf_crit undefined. {summary}")
    if mean_c05 <= mean_c10 * 1.02:
        return ("HARD_FAIL", f"HARD_FAIL: ratio flat/inverted on fine grid (ratio<={mean_ratio:.3f}). {summary}")

    if mean_ratio is not None and mean_ratio > 1.5 and n_mono >= max(4, n - 1):
        return ("HARD_PASS",
                f"HARD_PASS: fine-grid ratio={mean_ratio:.4f}>1.5 (coarse-grid artifact confirmed). {summary}")

    if mean_ratio is not None and mean_ratio > 1.1:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: fine-grid ratio={mean_ratio:.4f} improved over v1=1.10 but <1.5. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


print(f"[config] N={N} N_active={N_ACTIVE} mode={RUN_MODE} "
      f"n_noise_fracs={len(NOISE_FRACS)} predicted_barrier_ratio={PREDICTED_BARRIER_RATIO:.4f}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "alpha_values": ALPHA_VALUES, "grid_step": 0.01, "run_mode": RUN_MODE}

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
    "grid_step": 0.01,
    "summary": verdict_msg[:400],
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
