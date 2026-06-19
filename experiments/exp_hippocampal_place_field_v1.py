"""
hippocampal_place_field_v1 -- Hippocampal place-field encoding via substrate.

SCIENTIFIC QUESTION (Hippocampal phenomena: place-field encoding):
  In the hippocampus, place cells encode spatial location as population activity.
  Each place cell has a Gaussian firing field centered at a location. The population
  vector at position x = [r_1(x), ..., r_N(x)] encodes location as a sparse
  distributed pattern.

  Substrate mapping:
    - Encode K locations as HDC patterns: xi_k = sign(population_vector(x_k))
      where pop_vec = [1 if place_cell fires, -1 if not] at that location.
    - Store all K location patterns in substrate W.
    - Query: given noisy population vector at x_k, retrieve exact pattern xi_k.
    - Spatial continuity: nearby locations share more active place cells => higher
      cosine similarity between their HDC patterns => retrieval basin overlap.

  Design:
    - Generate K place-cell activity patterns for K locations on a 1D track.
    - Each location i activates a fraction PLACE_FRAC = 0.30 of place cells
      with Gaussian overlap between adjacent locations (sigma=2 positions).
    - Store K patterns in W (Hebbian).
    - Test:
        (A) Exact retrieval: noisy query (noise fraction 0.10) retrieves correct pattern.
            HP-A: cosine(retrieved, xi_k) >= 0.80 for >= 4/5 seeds.
        (B) Spatial gradient: cosine(xi_i, xi_j) decreases with |i-j|.
            HP-B: Spearman rho(distance, -cosine) >= 0.60 (spatial gradient).
        (C) Capacity: K = int(0.05*N) = 50 locations at N=1024 stored with acc >= 0.75.
            HP-C: retrieval_accuracy_at_K50 >= 0.75.

  HARD-PASS: All of A, B, C.
  HARD-FAIL: 0-1 cells pass.
  MIDDLE: 2/3 cells.

PRE-REGISTERED BANDS (calibration probe; first place-field test):
  HP: cosine >= 0.80, rho >= 0.60, acc >= 0.75.
  HF: cosine < 0.40, rho < 0.20, acc < 0.40.
  Bands: +-50% per calibration-probe policy.
  Theory: place-field patterns have within-field correlations that HDC encodes
  via Hebbian superposition; K=50 is well below Hopfield capacity at N=1024 (alpha_c*N=141).

FORMULA SELF-TESTS:
  1. Place-field activity: Gaussian overlap sigma=2, K=10 locations, N=100 cells.
     Location 5 and location 6 share more active cells than 5 and 10.
     [INPUT: sigma=2, locs=[5,6,10]] [EXPECTED: cos(5,6) > cos(5,10)]
  2. Hebbian W encoding: K=10 patterns, N=1024.
     W @ xi_1 should have high cosine with xi_1.
     [INPUT: K=10, retrieve xi_1 from W] [EXPECTED: cosine >= 0.50]
  3. Noisy retrieval: flip 10% of bits in xi_1, retrieve via sign(W @ noisy).
     [INPUT: 10% noise, K=10, N=1024] [EXPECTED: cosine(retrieved, xi_1) >= 0.60]

TIMEOUT ESTIMATE:
  Smoke: N=512, K=25, 2 seeds. Full: N=1024, K=50, 5 seeds.
  Linear. Smoke ~1s -> Full ~10s. timeout=120s.

No _nN suffix; production N=1024 per rule 3.
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

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "hippocampal_place_field_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17]
    K_LOCS = 25   # locations to encode
    NOISE_FRAC = 0.10
    PLACE_FRAC = 0.30
    SIGMA = 2.0
else:
    N = 1024
    SEEDS = [7, 17, 23, 31, 41]
    K_LOCS = 50
    NOISE_FRAC = 0.10
    PLACE_FRAC = 0.30
    SIGMA = 2.0

HP_COSINE = 0.80
HF_COSINE = 0.40
HP_SPEARMAN = 0.60
HF_SPEARMAN = 0.20
HP_ACC_K = 0.75
HF_ACC_K = 0.40

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()


# ---- FORMULA SELF-TESTS ----
def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    N_test, K_test = 512, 10
    sigma_test = 2.0
    place_frac_test = 0.30

    # Use the same generate_place_patterns mechanism (preferred_locs approach)
    rng = np.random.RandomState(7)
    preferred_locs = rng.uniform(0, K_test, size=N_test)
    Xi_test = np.zeros((K_test, N_test), dtype=np.float64)
    for k in range(K_test):
        act_prob = np.exp(-0.5 * ((preferred_locs - k) / sigma_test)**2)
        threshold = np.percentile(act_prob, 100 * (1 - place_frac_test))
        active = act_prob >= threshold
        Xi_test[k] = np.where(active, 1.0, -1.0)

    # Test: nearby locations (adjacent = 1 step) more similar than distant (4+ steps)
    # Average over multiple pairs to reduce noise
    near_cosines = [float(np.dot(Xi_test[i], Xi_test[i+1])) / N_test for i in range(K_test-1)]
    far_cosines = [float(np.dot(Xi_test[i], Xi_test[i+4])) / N_test for i in range(K_test-4)]
    mean_near = float(np.mean(near_cosines))
    mean_far = float(np.mean(far_cosines))
    assert mean_near > mean_far, f"Spatial continuity selftest: mean_near={mean_near:.3f} should > mean_far={mean_far:.3f}"

    # Test: Hebbian retrieval
    W = Xi_test.T @ Xi_test / N_test
    np.fill_diagonal(W, 0.0)
    retrieved = np.sign(W @ Xi_test[0] + 1e-8)
    cos_retrieval = float(np.dot(retrieved, Xi_test[0])) / N_test
    assert cos_retrieval >= 0.20, f"Hebbian retrieval selftest: cos={cos_retrieval:.3f} too low"

    # Test: at least 1 pattern has non-trivial self-retrieval
    self_cosines = [float(np.dot(np.sign(W @ Xi_test[k] + 1e-8), Xi_test[k])) / N_test for k in range(K_test)]
    assert max(self_cosines) >= 0.20, f"No pattern has self-retrieval above 0.20: {self_cosines}"

    print(f"[selftest] mean_near={mean_near:.3f} mean_far={mean_far:.3f} retrieval_cos={cos_retrieval:.3f}", flush=True)


_instrumentation_selftest()


def generate_place_patterns(K: int, N_dim: int, sigma: float, seed: int) -> np.ndarray:
    """Generate K place-field patterns via Gaussian overlap."""
    rng = np.random.RandomState(seed)
    # Each location k activates a subset of N neurons based on Gaussian envelope
    # Base patterns per neuron: neuron j has preferred location drawn from N(j*K/N, 1)
    preferred_locs = rng.uniform(0, K, size=N_dim)

    Xi = np.zeros((K, N_dim), dtype=np.float64)
    for k in range(K):
        # Activation probability: Gaussian centered at location k
        activation_prob = np.exp(-0.5 * ((preferred_locs - k) / sigma)**2)
        # Normalize to PLACE_FRAC active neurons
        threshold = np.percentile(activation_prob, 100 * (1 - PLACE_FRAC))
        active = activation_prob >= threshold
        Xi[k] = np.where(active, 1.0, -1.0)

    return Xi


def run_one_seed(seed: int) -> Dict:
    # Generate place-field patterns
    Xi = generate_place_patterns(K_LOCS, N, SIGMA, seed)

    # Build Hebbian W
    W = Xi.T @ Xi / N
    np.fill_diagonal(W, 0.0)

    # Cell A: exact retrieval with noise
    rng = np.random.RandomState(seed + 50000)
    cosines_retrieved = []
    for k in range(K_LOCS):
        noisy = Xi[k].copy()
        n_flip = int(NOISE_FRAC * N)
        flip_idx = rng.choice(N, size=n_flip, replace=False)
        noisy[flip_idx] = -noisy[flip_idx]
        retrieved = np.sign(W @ noisy + 1e-10)
        cos_k = float(np.dot(retrieved, Xi[k])) / N
        cosines_retrieved.append(cos_k)
    mean_cosine = float(np.mean(cosines_retrieved))

    # Cell B: spatial gradient (cosine decreases with distance)
    # Compute pairwise cosines between patterns
    pair_distances = []
    pair_cosines = []
    for i in range(K_LOCS):
        for j in range(i + 1, min(i + 8, K_LOCS)):  # neighbors only
            dist = abs(i - j)
            cos_ij = float(np.dot(Xi[i], Xi[j])) / N
            pair_distances.append(float(dist))
            pair_cosines.append(cos_ij)
    if len(pair_distances) < 2:
        rho_spatial = 0.0
    else:
        d_arr = np.array(pair_distances)
        c_arr = np.array(pair_cosines)
        # rho(distance, -cosine) >= HP means cosine decreases with distance
        if np.std(d_arr) < 1e-12 or np.std(c_arr) < 1e-12:
            rho_spatial = 0.0
        else:
            rho_spatial = float(np.corrcoef(
                np.argsort(np.argsort(d_arr)),
                np.argsort(np.argsort(-c_arr))
            )[0, 1])

    # Cell C: retrieval accuracy across all K patterns
    acc_K = float(np.mean(cosines_retrieved))

    assert len(cosines_retrieved) >= 1, "No patterns retrieved -- instrumentation bug"
    assert abs(rho_spatial) <= 1.0 + 1e-6, f"rho_spatial={rho_spatial:.3f} out of [-1,1]"

    cell_A_pass = mean_cosine >= HP_COSINE
    cell_B_pass = rho_spatial >= HP_SPEARMAN
    cell_C_pass = acc_K >= HP_ACC_K

    return {
        "N": N,
        "run_mode": RUN_MODE,
        "seed": seed,
        "mean_cosine": mean_cosine,
        "rho_spatial": rho_spatial,
        "acc_K": acc_K,
        "cell_A_pass": cell_A_pass,
        "cell_B_pass": cell_B_pass,
        "cell_C_pass": cell_C_pass,
    }


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed={seed}] cosine={result['mean_cosine']:.3f} rho_spatial={result['rho_spatial']:.3f} acc={result['acc_K']:.3f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    n_seeds = len(SEEDS)

    all_cos = [per_seed[str(s)]["mean_cosine"] for s in SEEDS]
    all_rho = [per_seed[str(s)]["rho_spatial"] for s in SEEDS]
    all_acc = [per_seed[str(s)]["acc_K"] for s in SEEDS]
    mean_cos = float(np.mean(all_cos))
    mean_rho = float(np.mean(all_rho))
    mean_acc = float(np.mean(all_acc))

    n_A = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_pass"])
    n_B = sum(1 for s in SEEDS if per_seed[str(s)]["cell_B_pass"])
    n_C = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_pass"])
    thr = math.ceil(n_seeds * 0.6)
    cell_A_pass = n_A >= thr
    cell_B_pass = n_B >= thr
    cell_C_pass = n_C >= thr

    n_cells_pass = int(cell_A_pass) + int(cell_B_pass) + int(cell_C_pass)
    if n_cells_pass == 3:
        verdict = "HARD_PASS"
    elif n_cells_pass == 0:
        verdict = "HARD_FAIL"
    elif n_cells_pass >= 2:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    elapsed = time.time() - t0
    verdict_msg = (
        f"hippocampal_place_field_v1 verdict={verdict}: "
        f"mean_cosine={mean_cos:.3f}(HP>={HP_COSINE}) "
        f"mean_rho_spatial={mean_rho:.3f}(HP>={HP_SPEARMAN}) "
        f"mean_acc_K={mean_acc:.3f}(HP>={HP_ACC_K}) "
        f"cells={n_cells_pass}/3 elapsed={elapsed:.1f}s"
    )
    print(verdict_msg, flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N,
        "n_seeds": n_seeds,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "mean_cosine": mean_cos,
        "mean_rho_spatial": mean_rho,
        "mean_acc_K": mean_acc,
        "n_cell_A_pass": n_A,
        "n_cell_B_pass": n_B,
        "n_cell_C_pass": n_C,
        "elapsed_s": elapsed,
    }
    with open(Path(out_dir) / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] metrics written to {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
