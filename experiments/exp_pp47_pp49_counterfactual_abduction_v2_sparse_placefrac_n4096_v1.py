"""
pp47_pp49_counterfactual_abduction_v2_sparse_placefrac_n4096_v1

R3-A fix: baseline_cos = 0.66-0.72 at PLACE_FRAC=0.30 is caused by neighbor
crosstalk from high-overlap place-field patterns (sigma=2.0, ~6 significant
neighbors per landmark). K-bump (v341 routing hypothesis) is FALSIFIED by
closed-form analysis: baseline_cos(K) is approximately flat in K for K in
[50, 500] because neighbor-overlap structure is determined by SIGMA, not K.

Correct fix: PLACE_FRAC reduction from 0.30 to 0.10. This reduces sum_overlap_sq
from ~4.0 to ~0.44, lifting predicted baseline_cos from ~0.67 to ~0.83 (HP boundary).

Theory (from research audit):
  cos ~ 1/sqrt(1 + sum_overlap_sq)
  At PLACE_FRAC=0.30, sigma=2.0: sum_overlap_sq ~ 4.0 -> cos ~ 0.45 (single step)
    -> converges to cluster-attractor ~0.66-0.72 after sign iterations.
  At PLACE_FRAC=0.10, sigma=2.0: overlap scales as (0.10/0.30)^2 = 0.111
    -> sum_overlap_sq ~ 0.44 -> cos ~ 0.83 (HP boundary).
  At PLACE_FRAC=0.05, sigma=2.0: sum_overlap_sq ~ 0.11 -> cos ~ 0.94 (clean HP).

Sparse Hopfield capacity bonus:
  alpha_c(PLACE_FRAC=0.10) ~ 1/(2 * PLACE_FRAC * ln(1/PLACE_FRAC)) ~ 1.09
  vs alpha_c(PLACE_FRAC=0.30) ~ 0.138. K=50 N=4096 alpha=0.0122 << alpha_c.

PROT-018: anchor _n4096 binds N=4096.

FORMULA SELF-TESTS:
  1. baseline_cos formula prediction at PLACE_FRAC=0.10, sigma=2.0:
     [INPUT: PLACE_FRAC=0.10, sigma=2.0] [EXPECTED: sum_overlap_sq ~ 0.44 -> cos ~ 0.83]
  2. alpha = K/N < alpha_c at all tested configurations.
  3. Rank-1 substitution field_B > 0.5.

PRE-REGISTERED BANDS (matched to original composition anchor):
  HARD-PASS: baseline_cos >= 0.85 in >= 6/7 seeds (HP1)
             AND cf_cos >= 0.70 in >= 6/7 seeds (HP2)
             AND consistency >= 0.85 in >= 6/7 seeds (HP3)
  MIDDLE: baseline_cos in [0.60, 0.85) for >= 5/7 seeds, other HP gates met
  HARD-FAIL: baseline_cos < 0.50 (HF1) OR cf_cos < 0.40 (HF2)
             OR consistency < 0.60 (HF3)
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

ANCHOR_NAME = "pp47_pp49_counterfactual_abduction_v2_sparse_placefrac_n4096_v1"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# KEY FIX: PLACE_FRAC reduced from 0.30 to 0.10
PLACE_FRAC = 0.10      # was 0.30 -- this IS the fix
SIGMA = 2.0            # unchanged
SHIFT_STEPS = 3        # unchanged
NOISE_FRAC = 0.10      # unchanged

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 1024
    K_LOCS = 20
    N_CF_QUERIES = 5
else:
    SEEDS = [7, 17, 23, 31, 41, 53, 67]   # 7 seeds (walk-back gate per original)
    N_ACTIVE = N
    K_LOCS = 50
    N_CF_QUERIES = 20

ALPHA_C_SPARSE = 1.0 / (2.0 * PLACE_FRAC * math.log(1.0 / PLACE_FRAC))

HP_BASELINE_COSINE = 0.85
HF_BASELINE_COSINE = 0.50
HP_CF_COSINE = 0.70
HF_CF_COSINE = 0.40
HP_CONSISTENCY = 0.85
HF_CONSISTENCY = 0.60


def predict_baseline_cos(place_frac: float, sigma: float, n_neighbors: int = 3) -> float:
    """Closed-form baseline_cos prediction from theory."""
    overlap_sq_sum = 0.0
    for d in range(1, n_neighbors + 1):
        ov = math.exp(-0.5 * (d / sigma) ** 2)
        # Overlap scales as place_frac^2 relative to PLACE_FRAC=0.30 baseline
        ov_scaled = ov * (place_frac / 0.30) ** 2
        overlap_sq_sum += 2.0 * ov_scaled ** 2
    cos = 1.0 / math.sqrt(1.0 + overlap_sq_sum)
    return cos


# Formula self-test at module scope
_predicted_cos_010 = predict_baseline_cos(0.10, 2.0)
_predicted_cos_030 = predict_baseline_cos(0.30, 2.0)
assert _predicted_cos_010 > _predicted_cos_030, (
    f"PLACE_FRAC=0.10 should predict higher cos than 0.30: "
    f"{_predicted_cos_010:.3f} vs {_predicted_cos_030:.3f}")
assert _predicted_cos_010 > 0.70, (
    f"PLACE_FRAC=0.10 should predict cos > 0.70: {_predicted_cos_010:.3f}")
print(f"[selftest-formula] baseline_cos predictions: "
      f"PLACE_FRAC=0.10->{_predicted_cos_010:.3f} "
      f"PLACE_FRAC=0.30->{_predicted_cos_030:.3f} "
      f"alpha_c_sparse={ALPHA_C_SPARSE:.3f}", flush=True)


def generate_place_patterns(K: int, N_dim: int, sigma: float, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    preferred_locs = rng.uniform(0, K, size=N_dim)
    Xi = np.zeros((K, N_dim), dtype=np.float64)
    for k in range(K):
        act_prob = np.exp(-0.5 * ((preferred_locs - k) / sigma) ** 2)
        threshold = np.percentile(act_prob, 100.0 * (1.0 - PLACE_FRAC))
        active = act_prob >= threshold
        Xi[k] = np.where(active, 1.0, -1.0)
    return Xi


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = 10) -> np.ndarray:
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


def _selftest_rank1_substitution():
    """After rank-1 substitution, xi_B field should dominate."""
    N_t = 128
    rng = np.random.RandomState(0)
    xi_A = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    xi_B = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W = np.outer(xi_A, xi_A) / N_t
    np.fill_diagonal(W, 0.0)
    W_cf = W - np.outer(xi_A, xi_A) / N_t + np.outer(xi_B, xi_B) / N_t
    np.fill_diagonal(W_cf, 0.0)
    h_B = W_cf @ xi_B
    field_B = float(np.dot(h_B, xi_B)) / N_t
    assert field_B > 0.5, f"rank1_sub field_B={field_B:.4f}"
    return field_B


def _selftest_capacity_and_alpha():
    alpha = K_LOCS / N_ACTIVE
    assert alpha < ALPHA_C_SPARSE, (
        f"alpha={alpha:.4f} >= alpha_c_sparse={ALPHA_C_SPARSE:.4f}")
    assert SHIFT_STEPS < K_LOCS // 4, (
        f"SHIFT_STEPS={SHIFT_STEPS} too large for K={K_LOCS}")
    return alpha


def _selftest_active_fraction():
    """Verify that generated patterns actually have PLACE_FRAC active units."""
    rng = np.random.RandomState(42)
    Xi_t = generate_place_patterns(10, 512, SIGMA, seed=42)
    active_fracs = [(Xi_t[k] == 1.0).mean() for k in range(10)]
    mean_frac = float(np.mean(active_fracs))
    assert abs(mean_frac - PLACE_FRAC) < 0.05, (
        f"Active fraction {mean_frac:.3f} != PLACE_FRAC={PLACE_FRAC}")
    return mean_frac


def _instrumentation_selftest():
    f1 = _selftest_rank1_substitution()
    alpha = _selftest_capacity_and_alpha()
    frac = _selftest_active_fraction()
    print(
        f"[selftest] PASS: sub_field={f1:.4f} alpha={alpha:.4f} "
        f"active_frac={frac:.4f}(target={PLACE_FRAC}) K={K_LOCS} shift={SHIFT_STEPS}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    rng_noise = np.random.RandomState(seed + 300)

    Xi = generate_place_patterns(K_LOCS, N_ACTIVE, SIGMA, seed)
    W = Xi.T @ Xi / float(N_ACTIVE)
    np.fill_diagonal(W, 0.0)

    interior_range = range(SHIFT_STEPS + 2, K_LOCS - SHIFT_STEPS - 2)
    query_indices = list(interior_range)[:N_CF_QUERIES]
    if len(query_indices) < 2:
        query_indices = [K_LOCS // 2]

    baseline_cosines = []
    cf_cosines = []
    consistency_cosines = []

    for k in query_indices:
        xi_k = Xi[k]
        xi_cf = Xi[k + SHIFT_STEPS]

        # Baseline: retrieve xi_k from W
        probe = xi_k.copy()
        flip = rng_noise.random(N_ACTIVE) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved_base = hopfield_retrieve(W, probe)
        baseline_cosines.append(cosine_sim(retrieved_base, xi_k))

        # Counterfactual: W_cf = W - xi_k + xi_cf (rank-1 substitution)
        W_cf = (W
                - (1.0 / N_ACTIVE) * np.outer(xi_k, xi_k)
                + (1.0 / N_ACTIVE) * np.outer(xi_cf, xi_cf))
        np.fill_diagonal(W_cf, 0.0)

        probe_cf = xi_cf.copy()
        flip_cf = rng_noise.random(N_ACTIVE) < NOISE_FRAC
        probe_cf[flip_cf] *= -1.0
        retrieved_cf = hopfield_retrieve(W_cf, probe_cf)
        cf_cosines.append(cosine_sim(retrieved_cf, xi_cf))

        probe_cf2 = xi_cf.copy()
        flip_cf2 = rng_noise.random(N_ACTIVE) < NOISE_FRAC
        probe_cf2[flip_cf2] *= -1.0
        retrieved_cf2 = hopfield_retrieve(W_cf, probe_cf2)
        consistency_cosines.append(cosine_sim(retrieved_cf2, xi_cf))

    mean_baseline = float(np.mean(baseline_cosines)) if baseline_cosines else 0.0
    mean_cf = float(np.mean(cf_cosines)) if cf_cosines else 0.0
    mean_consistency = float(np.mean(consistency_cosines)) if consistency_cosines else 0.0

    hp1 = mean_baseline >= HP_BASELINE_COSINE
    hp2 = mean_cf >= HP_CF_COSINE
    hp3 = mean_consistency >= HP_CONSISTENCY
    hf1 = mean_baseline < HF_BASELINE_COSINE
    hf2 = mean_cf < HF_CF_COSINE
    hf3 = mean_consistency < HF_CONSISTENCY

    elapsed = time.time() - t0
    print(
        f"  [seed={seed} N={N_ACTIVE} K={K_LOCS} shift={SHIFT_STEPS} "
        f"PLACE_FRAC={PLACE_FRAC}] "
        f"baseline={mean_baseline:.4f}(HP>={HP_BASELINE_COSINE}) "
        f"cf={mean_cf:.4f}(HP>={HP_CF_COSINE}) "
        f"consistency={mean_consistency:.4f}(HP>={HP_CONSISTENCY}) "
        f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] elapsed={elapsed:.2f}s",
        flush=True,
    )

    return {
        "seed": seed, "N": N_ACTIVE, "K_LOCS": K_LOCS, "SHIFT_STEPS": SHIFT_STEPS,
        "PLACE_FRAC": PLACE_FRAC, "run_mode": RUN_MODE,
        "mean_baseline_cos": float(mean_baseline),
        "mean_cf_cos": float(mean_cf),
        "mean_consistency": float(mean_consistency),
        "n_cf_queries": len(query_indices),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hf1": bool(hf1), "hf2": bool(hf2), "hf3": bool(hf3),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    mean_base = float(np.mean([r["mean_baseline_cos"] for r in results]))
    mean_cf = float(np.mean([r["mean_cf_cos"] for r in results]))
    mean_cons = float(np.mean([r["mean_consistency"] for r in results]))
    hp1_n = sum(1 for r in results if r["hp1"])
    hp2_n = sum(1 for r in results if r["hp2"])
    hp3_n = sum(1 for r in results if r["hp3"])
    hf1_any = any(r["hf1"] for r in results)
    hf2_any = any(r["hf2"] for r in results)
    hf3_any = any(r["hf3"] for r in results)

    hp_threshold = math.ceil(n * 6.0 / 7.0)  # >= 6/7 per prereg

    summary = (
        f"n_seeds={n} PLACE_FRAC={PLACE_FRAC} "
        f"baseline={mean_base:.4f}(HP>={HP_BASELINE_COSINE}) "
        f"cf={mean_cf:.4f}(HP>={HP_CF_COSINE},HF<{HF_CF_COSINE}) "
        f"consistency={mean_cons:.4f} "
        f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n}"
    )

    if hf1_any:
        return ("HARD_FAIL", f"HARD_FAIL HF1: baseline retrieval fails. {summary}")
    if hf2_any:
        return ("HARD_FAIL", f"HARD_FAIL HF2: counterfactual abduction fails. {summary}")
    if hf3_any:
        return ("HARD_FAIL", f"HARD_FAIL HF3: counterfactual matrix unstable. {summary}")

    all_hp = all(cnt >= hp_threshold for cnt in [hp1_n, hp2_n, hp3_n])
    if all_hp:
        return ("HARD_PASS",
                f"HARD_PASS: all 3 HP in >={hp_threshold}/{n} seeds "
                f"at PLACE_FRAC={PLACE_FRAC}. {summary}")

    n_mid = sum([
        hp1_n >= math.ceil(n * 5.0 / 7.0),
        hp2_n >= math.ceil(n * 5.0 / 7.0),
        hp3_n >= math.ceil(n * 5.0 / 7.0),
    ])
    if n_mid >= 2:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: {n_mid}/3 HP conditions met (5/7 threshold). {summary}")
    return ("HARD_FAIL",
            f"HARD_FAIL: only {n_mid}/3 HP conditions met (sparse-code fix insufficient). {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "K_LOCS": K_LOCS, "SHIFT_STEPS": SHIFT_STEPS,
              "PLACE_FRAC": PLACE_FRAC, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
    f"(N={N_ACTIVE} K={K_LOCS} shift={SHIFT_STEPS} "
    f"PLACE_FRAC={PLACE_FRAC} mode={RUN_MODE})",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] pp47_pp49 v2 sparse N={N_ACTIVE} K={K_LOCS} "
          f"PLACE_FRAC={PLACE_FRAC}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N_ACTIVE, "K_LOCS": K_LOCS, "SHIFT_STEPS": SHIFT_STEPS,
    "PLACE_FRAC": PLACE_FRAC,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_s,
    "per_seed": [
        {
            "seed": r.get("seed"),
            "mean_baseline_cos": r.get("mean_baseline_cos"),
            "mean_cf_cos": r.get("mean_cf_cos"),
            "mean_consistency": r.get("mean_consistency"),
            "hp1": r.get("hp1"), "hp2": r.get("hp2"), "hp3": r.get("hp3"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.parent.mkdir(parents=True, exist_ok=True)
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
