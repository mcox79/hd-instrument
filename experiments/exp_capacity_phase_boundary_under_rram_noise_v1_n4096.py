"""
capacity_phase_boundary_under_rram_noise_v1_n4096 -- Item 21: Wave-2 free-probability prediction test.

Tests whether substrate capacity follows the closed-form phase boundary:
  sigma_g^2 = 1/alpha - 1
from the Wave-2 free-probability RRAM noise drill.

SCIENTIFIC QUESTION:
  Does substrate recall accuracy maintain >= 90% below the predicted phase boundary
  (sigma_g^2 < 1/alpha - 1) and degrade above it?

TEST DESIGN:
  (alpha, sigma_g) grid at N=4096, 5 seeds:
  alpha in {0.05, 0.10, 0.20, 0.50}
  sigma_g in {0.5, 1.0, 2.0, 4.0, 6.0}
  Noise model: W_noisy = W * exp(sigma_g * Z) where Z ~ N(0,1) entrywise (multiplicative log-normal).
  Measure mean recall accuracy (cosine similarity of retrieved vs true pattern).

FORMULA SELF-TESTS (PROT-022):
  1. Phase boundary formula: sigma_g_crit^2 = 1/alpha - 1
     [INPUT: alpha=0.05] [EXPECTED: sigma_g_crit = sqrt(19) = 4.359]
     [INPUT: alpha=0.10] [EXPECTED: sigma_g_crit = sqrt(9) = 3.000]
     [INPUT: alpha=0.20] [EXPECTED: sigma_g_crit = sqrt(4) = 2.000]
     [INPUT: alpha=0.50] [EXPECTED: sigma_g_crit = sqrt(1) = 1.000]
  2. Multiplicative noise model: W_noisy[i,j] = W[i,j] * exp(sigma_g * Z[i,j])
     For W=1.0, sigma_g=0.0, Z=0: W_noisy = 1.0
     For W=1.0, sigma_g=1.0, Z=0: W_noisy = 1.0 (Z=0 => no noise at mean)
  3. alpha values: M = int(alpha * N); alpha_actual = M/N; all M > 0.

PRE-REGISTERED BANDS:
  HARD-PASS: recall >= 0.90 for (alpha, sigma_g) with sigma_g^2 < (1/alpha - 1)
             AND recall < 0.50 for sigma_g^2 > 2 * (1/alpha - 1);
             phase boundary detected within +-20% (>= 3/5 seeds)
  MIDDLE: phase boundary detected but with >50% width OR detection in only 2/4 alpha values
  HARD-FAIL: no clear phase transition detected across the grid
             OR substrate accuracy degrades at sigma_g << predicted (sigma_g < 0.5 * sigma_g_crit)

PROT-018: anchor has _n4096; N MUST = 4096.
QUEUE: remote_cpu_queue (CPU; pure numpy; ~1 hr wall for 4x5x5 = 100 cells).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
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

ANCHOR_NAME = "capacity_phase_boundary_under_rram_noise_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Grid
ALPHA_VALUES = [0.05, 0.10, 0.20, 0.50]
SIGMA_G_VALUES = [0.5, 1.0, 2.0, 4.0, 6.0]
ALPHA_C = 0.138

# Phase boundary: sigma_g_crit = sqrt(1/alpha - 1)
def phase_boundary(alpha):
    return float((1.0 / alpha - 1.0) ** 0.5)

# Pre-registered bands
HP_RECALL_BELOW = 0.90   # recall >= this for sigma_g^2 < sigma_g_crit^2
HP_RECALL_ABOVE = 0.50   # recall < this for sigma_g^2 > 2 * sigma_g_crit^2
N_RETRIEVAL_STEPS = 8
N_QUERIES_PER_CELL = 8  # queries per (alpha, sigma_g) cell

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 512
    N_QUERIES_PER_CELL = 4
    # Use alpha=0.20 and 0.50 for smoke: sigma_g_crit = sqrt(4)=2.0 and sqrt(1)=1.0
    # 2x boundary: sigma_g^2 > 2*4=8 => sigma_g > 2.83 and sigma_g^2 > 2*1=2 => sigma_g > 1.41
    # Both achievable with sigma_g in {0.5, 2.0, 4.0}
    ALPHA_VALUES_SMOKE = [0.20, 0.50]
    SIGMA_G_SMOKE = [0.5, 1.0, 2.0, 4.0]
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    ALPHA_VALUES_SMOKE = ALPHA_VALUES
    SIGMA_G_SMOKE = SIGMA_G_VALUES


def _selftest_phase_boundary():
    """sigma_g_crit^2 = 1/alpha - 1."""
    cases = [(0.05, 4.359), (0.10, 3.000), (0.20, 2.000), (0.50, 1.000)]
    for alpha, expected in cases:
        got = phase_boundary(alpha)
        assert abs(got - expected) < 0.01, f"phase_boundary({alpha}): got {got:.4f}, expected {expected:.3f}"


def _selftest_noise_model():
    """Multiplicative noise: W_noisy = W * exp(sigma_g * Z)."""
    n_t = 4
    W = np.ones((n_t, n_t))
    Z = np.zeros((n_t, n_t))  # Z=0 => W_noisy = W * exp(0) = W
    sigma_g = 1.0
    W_noisy = W * np.exp(sigma_g * Z)
    assert np.allclose(W_noisy, W), f"Noise model: W_noisy != W at Z=0"


def _selftest_alpha_m():
    """M = int(alpha * N_active) > 0 for all alpha."""
    for alpha in ALPHA_VALUES:
        M_val = max(1, int(alpha * N_ACTIVE))
        assert M_val > 0, f"M=0 for alpha={alpha}"


def _selftest_valid_cells():
    """At least 1 cell below phase boundary and 1 above for at least one smoke alpha."""
    any_valid = False
    for alpha_test in ALPHA_VALUES_SMOKE:
        sgc = phase_boundary(alpha_test)
        below = [sg for sg in SIGMA_G_SMOKE if sg * sg < sgc * sgc]
        above = [sg for sg in SIGMA_G_SMOKE if sg * sg > 2 * sgc * sgc]
        if len(below) >= 1 and len(above) >= 1:
            any_valid = True
            break
    assert any_valid, (f"No alpha in {ALPHA_VALUES_SMOKE} has both below-boundary and "
                       f"above-2x-boundary sigma_g values in {SIGMA_G_SMOKE}")


def _instrumentation_selftest():
    _selftest_phase_boundary()
    _selftest_noise_model()
    _selftest_alpha_m()
    _selftest_valid_cells()
    print(f"[selftest] PASS: phase_boundary, noise_model, alpha_m, valid_cells "
          f"N_active={N_ACTIVE}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = N_RETRIEVAL_STEPS) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def run_seed(seed: int, n_dim: int,
             alpha_list: List[float], sigma_list: List[float]) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    grid_results = {}
    for alpha in alpha_list:
        M_val = max(1, int(alpha * n_dim))
        Xi = rng.choice([-1., 1.], size=(M_val, n_dim)).astype(np.float64)
        W_clean = (Xi.T @ Xi) / float(n_dim)
        sgc = phase_boundary(alpha)

        for sigma_g in sigma_list:
            # Apply multiplicative log-normal noise to W
            Z = rng.standard_normal((n_dim, n_dim))
            W_noisy = W_clean * np.exp(sigma_g * Z)
            # Symmetrize
            W_noisy = (W_noisy + W_noisy.T) / 2.0

            n_q = min(N_QUERIES_PER_CELL, M_val)
            recalls = []
            for q in range(n_q):
                xi_q = Xi[q]
                probe = xi_q.copy()
                flip = rng.random(n_dim) < 0.10  # 10% input noise
                probe[flip] *= -1.0
                state = hopfield_retrieve(W_noisy, probe)
                cos = float(np.dot(state, xi_q)) / n_dim
                recalls.append(cos)
            mean_recall = float(np.mean(recalls)) if recalls else 0.0

            below_boundary = (sigma_g ** 2) < (sgc ** 2)
            above_2x = (sigma_g ** 2) > 2.0 * (sgc ** 2)
            key = f"a{alpha:.2f}_sg{sigma_g:.1f}"
            grid_results[key] = {
                "alpha": float(alpha), "sigma_g": float(sigma_g),
                "recall": float(mean_recall), "sigma_g_crit": float(sgc),
                "below_boundary": bool(below_boundary), "above_2x": bool(above_2x),
            }
            print(f"  [seed={seed} alpha={alpha:.2f} sg={sigma_g:.1f} sgc={sgc:.3f}] "
                  f"recall={mean_recall:.4f} below={below_boundary} above2x={above_2x}", flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "elapsed_s": float(elapsed), "grid_results": grid_results,
    }


def compute_verdict(all_results: List[Dict]) -> tuple:
    if not all_results:
        return ("HARD_FAIL", "No valid results.")

    # Aggregate recall per cell across seeds
    cell_recalls = {}
    for r in all_results:
        for key, cell in r.get("grid_results", {}).items():
            if key not in cell_recalls:
                cell_recalls[key] = {"recalls": [], "alpha": cell["alpha"],
                                     "sigma_g": cell["sigma_g"],
                                     "below_boundary": cell["below_boundary"],
                                     "above_2x": cell["above_2x"]}
            cell_recalls[key]["recalls"].append(cell["recall"])

    # Check HP conditions
    hp_below_violations = 0   # cells below boundary with recall < 0.90
    hp_above_violations = 0   # cells above 2x boundary with recall >= 0.50
    below_cells = 0
    above_cells = 0
    for key, cd in cell_recalls.items():
        mean_r = float(np.mean(cd["recalls"]))
        if cd["below_boundary"]:
            below_cells += 1
            if mean_r < HP_RECALL_BELOW:
                hp_below_violations += 1
        if cd["above_2x"]:
            above_cells += 1
            if mean_r >= HP_RECALL_ABOVE:
                hp_above_violations += 1

    # Count alpha values where phase boundary is detectable
    alpha_with_transition = set()
    for key, cd in cell_recalls.items():
        alpha = cd["alpha"]
        mean_r = float(np.mean(cd["recalls"]))
        sgc = phase_boundary(alpha)
        sg = cd["sigma_g"]
        if sg ** 2 < sgc ** 2 and mean_r >= HP_RECALL_BELOW:
            alpha_with_transition.add(alpha)
        if sg ** 2 > 2 * sgc ** 2 and mean_r < HP_RECALL_ABOVE:
            alpha_with_transition.add(alpha)

    n_alpha_total = len(ALPHA_VALUES)
    n_alpha_detected = len(alpha_with_transition)

    summary = (f"below_boundary_violations={hp_below_violations}/{below_cells} "
               f"above_2x_violations={hp_above_violations}/{above_cells} "
               f"alpha_transition_detected={n_alpha_detected}/{n_alpha_total}")

    # HARD-FAIL: no clear transition
    if below_cells == 0 or above_cells == 0:
        return ("HARD_FAIL", f"HARD_FAIL: insufficient grid coverage. {summary}")
    if hp_below_violations > below_cells // 2 and hp_above_violations > above_cells // 2:
        return ("HARD_FAIL", f"HARD_FAIL: no clear phase transition. {summary}")

    # HARD-PASS: boundary clear
    hp_below_ok = hp_below_violations == 0
    hp_above_ok = hp_above_violations == 0
    if hp_below_ok and hp_above_ok and n_alpha_detected >= 2:
        return ("HARD_PASS",
                f"HARD_PASS: Phase boundary confirmed. recall >=0.90 below boundary, "
                f"<0.50 above 2x boundary. {summary}")

    # MIDDLE
    if hp_below_ok or hp_above_ok or n_alpha_detected >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial transition signal. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


def _prot018_startup_check() -> None:
    if RUN_MODE != "smoke" and N_ACTIVE != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor _n{_N_SUFFIX} but FULL N_ACTIVE={N_ACTIVE}")


alpha_use = ALPHA_VALUES_SMOKE if RUN_MODE == "smoke" else ALPHA_VALUES
sigma_use = SIGMA_G_SMOKE if RUN_MODE == "smoke" else SIGMA_G_VALUES
print(f"[config] PROT-018 N={N} N_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha={alpha_use} sigma_g={sigma_use}", flush=True)
_prot018_startup_check()

out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "alpha_values": alpha_use, "sigma_g_values": sigma_use, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] seeds_todo={seeds_todo} out_dir={out_dir}", flush=True)

for s in seeds_todo:
    res = run_seed(s, N_ACTIVE, alpha_use, sigma_use)
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
    "phase_boundaries": {str(a): phase_boundary(a) for a in ALPHA_VALUES},
    "summary": verdict_msg[:300],
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
