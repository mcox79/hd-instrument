"""
streaming_prediction_6_above_capacity_v1 -- SP6 redesign: above-capacity discrimination.

SP6 v1 FAILURE DIAGNOSIS:
  v1 tested importance-weighted fidelity at alpha = M/N = 0.049 (well below capacity).
  At below-capacity load, ALL patterns retrieve with high fidelity regardless of
  importance weights. The fidelity is near-ceiling, so Spearman rho between importance
  and fidelity is near-zero (no variance in the dependent variable).
  Root cause: no discrimination possible when everything works.

REDESIGN (SP6 above-capacity):
  Test at alpha > alpha_c to probe the regime where the substrate MUST prioritize.
  Use a two-group design:
    - Group HIGH: M_HIGH patterns written with weight w_high = 2.0.
    - Group LOW: M_LOW patterns written with weight w_low = 1.0.
    - Total alpha = (M_HIGH * w_high + M_LOW * w_low) / N (effective load).
    - At above-capacity load, high-weight patterns should retain fidelity
      while low-weight patterns degrade.

  Protocol:
    1. Build W = (1/N) * [w_high * sum(xi_high) + w_low * sum(xi_low)].
    2. Measure retrieval fidelity for high vs low groups.
    3. HP: fid_high > fid_low + 0.10 (at above-capacity stress).

PRE-REGISTERED BANDS:
  HP: fid_high - fid_low >= 0.10 AND fid_high >= 0.70 (importance keeps high group viable).
  HF: fid_high - fid_low < 0.0 (inverted: low group retrieves better than high group).
  MIDDLE: difference in [0.0, 0.10).

  Above-capacity probe with no prior directly comparable anchor.
  Theory: Hopfield energy landscape is distorted by heterogeneous weights;
  high-weight patterns occupy deeper basins. P_deflated = 0.55.

FORMULA SELF-TESTS:
  1. W = (1/N) * sum_k w_k * outer(xi_k, xi_k): check at N=4.
     [INPUT: N=4, w=[2,1], xi_0=[1,-1,1,-1], xi_1=[1,1,-1,-1]]
     [EXPECTED: W[0,0] = (2*1 + 1*1)/4 = 0.75]
  2. Above-capacity regime: alpha_eff > 0.138 at production N.
     [INPUT: N, M_HIGH, M_LOW, w_high, w_low] [EXPECTED: alpha_eff >= 0.18]
  3. fid_high > fid_low at above-capacity (directional, may not be 100% reliable
     at small test scale; selftest just checks formula not result).

No _nN suffix; production N=1024 (PROT-018 rule 3).
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

ANCHOR_NAME = "streaming_prediction_6_above_capacity_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 1024
ALPHA_C = 0.138
W_HIGH = 2.0
W_LOW = 1.0
NOISE_FRAC = 0.10

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_HIGH = 40    # alpha effective for high group
    M_LOW = 80     # larger low group to stress capacity
    N_QUERIES = 15
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_HIGH = 80    # alpha_high_contribution = 80*2/1024 ~ 0.156
    M_LOW = 120    # alpha_low_contribution = 120/1024 ~ 0.117
    N_QUERIES = 30  # total alpha_eff ~ 0.273 > alpha_c

HP_FID_DIFF = 0.10
HF_FID_DIFF = 0.0
HP_FID_HIGH = 0.70


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


def _instrumentation_selftest():
    # Test 1: W construction check
    N_t = 4
    w_t = np.array([2.0, 1.0])
    xi_0 = np.array([1.0, -1.0, 1.0, -1.0])
    xi_1 = np.array([1.0, 1.0, -1.0, -1.0])
    W_t = (1.0 / N_t) * (w_t[0] * np.outer(xi_0, xi_0) + w_t[1] * np.outer(xi_1, xi_1))
    expected_diag_00 = (2.0 * 1.0 + 1.0 * 1.0) / N_t  # xi_0[0]^2=xi_1[0]^2=1
    assert abs(W_t[0, 0] - expected_diag_00) < 1e-8, \
        f"W_diag[0,0]={W_t[0,0]:.4f} expected {expected_diag_00:.4f}"

    # Test 2: above-capacity check at FULL N
    alpha_high = M_HIGH * W_HIGH / float(N)
    alpha_low = M_LOW * W_LOW / float(N)
    alpha_eff = alpha_high + alpha_low
    assert alpha_eff > ALPHA_C, \
        f"alpha_eff={alpha_eff:.4f} not > alpha_c={ALPHA_C} (not above-capacity)"

    assert N_QUERIES > 0, "N_QUERIES must be > 0"
    print(f"[selftest] PASS: W_diag_check OK alpha_eff={alpha_eff:.4f} > alpha_c={ALPHA_C} "
          f"M_HIGH={M_HIGH} M_LOW={M_LOW} N={N}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    Xi_high = rng.choice([-1.0, 1.0], size=(M_HIGH, N)).astype(np.float64)
    Xi_low = rng.choice([-1.0, 1.0], size=(M_LOW, N)).astype(np.float64)

    # Build importance-weighted W
    W = np.zeros((N, N), dtype=np.float64)
    for k in range(M_HIGH):
        W += W_HIGH * np.outer(Xi_high[k], Xi_high[k])
    for k in range(M_LOW):
        W += W_LOW * np.outer(Xi_low[k], Xi_low[k])
    W /= float(N)
    np.fill_diagonal(W, 0.0)

    alpha_eff = (M_HIGH * W_HIGH + M_LOW * W_LOW) / float(N)

    # Measure fidelity for high vs low groups
    rng_noise = np.random.RandomState(seed + 100)
    n_test_high = min(N_QUERIES, M_HIGH)
    n_test_low = min(N_QUERIES, M_LOW)
    fids_high = []
    fids_low = []

    for k in range(n_test_high):
        probe = Xi_high[k].copy()
        flip = rng_noise.random(N) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved = hopfield_retrieve(W, probe)
        fids_high.append(cosine_sim(retrieved, Xi_high[k]))

    for k in range(n_test_low):
        probe = Xi_low[k].copy()
        flip = rng_noise.random(N) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved = hopfield_retrieve(W, probe)
        fids_low.append(cosine_sim(retrieved, Xi_low[k]))

    mean_fid_high = float(np.mean(fids_high)) if fids_high else 0.0
    mean_fid_low = float(np.mean(fids_low)) if fids_low else 0.0
    fid_diff = mean_fid_high - mean_fid_low

    hp_diff = fid_diff >= HP_FID_DIFF
    hp_high = mean_fid_high >= HP_FID_HIGH
    hf_diff = fid_diff < HF_FID_DIFF

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={N} M_HIGH={M_HIGH} M_LOW={M_LOW} alpha_eff={alpha_eff:.3f}] "
          f"fid_high={mean_fid_high:.4f} fid_low={mean_fid_low:.4f} "
          f"diff={fid_diff:.4f}(HP>={HP_FID_DIFF}) "
          f"hp=[{int(hp_diff)},{int(hp_high)}] elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "M_HIGH": M_HIGH, "M_LOW": M_LOW,
        "alpha_eff": float(alpha_eff), "run_mode": RUN_MODE,
        "fid_high": float(mean_fid_high),
        "fid_low": float(mean_fid_low),
        "fid_diff": float(fid_diff),
        "hp_diff": bool(hp_diff),
        "hp_high": bool(hp_high),
        "hf_diff": bool(hf_diff),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    mean_diff = float(np.mean([r["fid_diff"] for r in results]))
    mean_fid_h = float(np.mean([r["fid_high"] for r in results]))
    n_hp_diff = sum(1 for r in results if r["hp_diff"])
    n_hp_high = sum(1 for r in results if r["hp_high"])
    hf_any = any(r["hf_diff"] for r in results)

    summary = (f"mean_diff={mean_diff:.4f}(HP>={HP_FID_DIFF} HF<{HF_FID_DIFF}) "
               f"mean_fid_high={mean_fid_h:.4f}(HP>={HP_FID_HIGH}) "
               f"n_hp_diff={n_hp_diff}/{n} n_hp_high={n_hp_high}/{n}")

    if hf_any:
        return ("HARD_FAIL", f"HARD_FAIL: low group retrieves better than high group (inverted). {summary}")

    min_thresh = math.ceil(n * 0.8)
    if n_hp_diff >= min_thresh and n_hp_high >= min_thresh:
        return ("HARD_PASS", f"HARD_PASS: above-capacity importance discrimination confirmed. {summary}")
    if mean_diff >= 0.0 and (n_hp_diff >= min_thresh or n_hp_high >= min_thresh):
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial discrimination. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP conditions. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_HIGH": M_HIGH, "M_LOW": M_LOW, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
      f"(N={N} M_HIGH={M_HIGH} M_LOW={M_LOW} mode={RUN_MODE})", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] SP6_above_capacity N={N}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "M_HIGH": M_HIGH, "M_LOW": M_LOW,
    "W_HIGH": W_HIGH, "W_LOW": W_LOW,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
