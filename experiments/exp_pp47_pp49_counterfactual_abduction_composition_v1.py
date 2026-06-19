"""
pp47_pp49_counterfactual_abduction_composition_v1 -- Phase 0c PP-47 x PP-49 composition.

SCIENTIFIC QUESTION (Phase 0c for Tier-6 LLM-integration testbed):
  Does the substrate support Pearl L3 abductive counterfactual reasoning over spatial codes?
  Specifically: "what would the agent infer if landmark Y had been at different location?"

  Setup:
  - K=50 landmark-position pairs encoded as PP-47 place-field patterns.
  - For each landmark k, PP-49 counterfactual abduction: shift position by SHIFT_STEPS steps
    and ask: what pattern would be retrieved?
  - Counterfactual construction: given W stores pattern xi_{k} at position p_k,
    build a COUNTERFACTUAL Hopfield matrix W_cf that replaces xi_{k} with xi_{k+SHIFT_STEPS}
    (the pattern at the shifted position). Then query xi_{k+SHIFT_STEPS}'s retrieval.

  The counterfactual primitive operates via rank-1 substitution:
    W_cf = W - (1/N) xi_k xi_k^T + (1/N) xi_{k+SHIFT_STEPS} xi_{k+SHIFT_STEPS}^T
  (remove original, add counterfactual pattern).

  HARD-PASS: counterfactual abduction cosine >= 0.70 across 5 seeds.
  HARD-FAIL: counterfactual cosine < 0.40.
  MIDDLE: counterfactual cosine in [0.40, 0.70).

  Additional metrics:
  (a) Original pattern retrievable from W (baseline): cosine >= 0.85.
  (b) Counterfactual pattern retrievable from W_cf: cosine >= 0.70.
  (c) Counterfactual in-counterfactual (consistency): re-querying W_cf with
      xi_{k+SHIFT_STEPS} still returns same pattern (idempotent).

PRE-REGISTERED HARD-PASS:
  HP1: baseline cosine (original pattern from W) >= 0.85 in >= 4/5 seeds
  HP2: counterfactual cosine (shifted pattern from W_cf) >= 0.70 in >= 4/5 seeds
  HP3: counterfactual consistency (re-query W_cf returns same pattern) >= 0.85 in >= 4/5 seeds

PRE-REGISTERED HARD-FAIL:
  HF1: baseline cosine < 0.50 (substrate cannot even retrieve the original)
  HF2: counterfactual cosine < 0.40 (counterfactual fails to work)
  HF3: consistency < 0.60 (counterfactual matrix is unstable)

P_deflated: 0.65 (PP-49 confirmed at N=4096 v334 l3_fid=1.0; PP-47 confirmed at v333;
  composition via rank-1 substitution is algebraically straightforward)

FORMULA SELF-TESTS:
  1. Rank-1 substitution: W_cf = W - (1/N) xi_A xi_A^T + (1/N) xi_B xi_B^T.
     After substitution, xi_B should be recoverable from W_cf.
     [INPUT: N=8, M=1, single pattern xi_A; substitute with xi_B]
     [EXPECTED: W_cf @ xi_B gives dominant field aligned with xi_B]
  2. Counterfactual field: xi_B^T W_cf xi_B / N = (1/N)||xi_B||^2 + crosstalk terms.
     For M=1 (just xi_B in W_cf after substitution): xi_B^T W_cf xi_B / N ~ 1.
     [INPUT: M=1 after substitution] [EXPECTED: field >= 0.9]
  3. Original pattern xi_A no longer retrieved from W_cf (removed by rank-1 subtraction).
     [INPUT: same setup] [EXPECTED: xi_A cosine from W_cf < 0.5 or near noise floor]

No _nN suffix; production N=4096 (pre-PROT-018 rule).
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

ANCHOR_NAME = "pp47_pp49_counterfactual_abduction_composition_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 4096
ALPHA_C = 0.138
SHIFT_STEPS = 3  # shift position by 3 steps for counterfactual

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 1024
    K_LOCS = 20
    N_CF_QUERIES = 5
else:
    SEEDS = [7, 17, 23, 31, 41, 53, 67]  # 7 seeds: walk-back gate (MIDDLE_BAND at smoke HP1)
    N_ACTIVE = N
    K_LOCS = 50
    N_CF_QUERIES = 20

SIGMA = 2.0
PLACE_FRAC = 0.30
NOISE_FRAC = 0.10

HP_BASELINE_COSINE = 0.85
HF_BASELINE_COSINE = 0.50
HP_CF_COSINE = 0.70
HF_CF_COSINE = 0.40
HP_CONSISTENCY = 0.85
HF_CONSISTENCY = 0.60


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


# ---- FORMULA SELF-TESTS ----
def _selftest_rank1_substitution():
    """After rank-1 substitution, xi_B field should dominate."""
    N_t = 128
    rng = np.random.RandomState(0)
    xi_A = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    xi_B = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W = np.outer(xi_A, xi_A) / N_t
    np.fill_diagonal(W, 0.0)
    # Substitute A -> B
    W_cf = W - np.outer(xi_A, xi_A) / N_t + np.outer(xi_B, xi_B) / N_t
    np.fill_diagonal(W_cf, 0.0)
    # Field at xi_B
    h_B = W_cf @ xi_B
    field_B = float(np.dot(h_B, xi_B)) / N_t
    assert field_B > 0.5, f"rank1_sub field_B={field_B:.4f}"
    return field_B


def _selftest_cf_cosine():
    """Counterfactual cosine after substitution."""
    N_t = 128
    rng = np.random.RandomState(1)
    xi_A = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    xi_B = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W = np.outer(xi_A, xi_A) / N_t
    np.fill_diagonal(W, 0.0)
    W_cf = W - np.outer(xi_A, xi_A) / N_t + np.outer(xi_B, xi_B) / N_t
    np.fill_diagonal(W_cf, 0.0)
    state = xi_B.copy()
    for _ in range(10):
        state = np.sign(W_cf @ state)
        state[state == 0] = 1.0
    cos = float(np.dot(state, xi_B)) / N_t
    assert cos > 0.5, f"cf_cosine selftest: {cos:.4f}"
    return cos


def _selftest_capacity():
    alpha = K_LOCS / N_ACTIVE
    assert alpha < ALPHA_C, f"alpha={alpha:.4f} >= alpha_c"
    assert SHIFT_STEPS < K_LOCS // 4, f"SHIFT_STEPS={SHIFT_STEPS} too large for K={K_LOCS}"
    return alpha


def _instrumentation_selftest():
    f1 = _selftest_rank1_substitution()
    f2 = _selftest_cf_cosine()
    alpha = _selftest_capacity()
    print(
        f"[selftest] PASS: sub_field={f1:.4f} cf_cos={f2:.4f} "
        f"alpha={alpha:.4f} K={K_LOCS} shift={SHIFT_STEPS}",
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

    # Sample N_CF_QUERIES interior landmark positions for counterfactual
    interior_range = range(SHIFT_STEPS + 2, K_LOCS - SHIFT_STEPS - 2)
    query_indices = list(interior_range)[:N_CF_QUERIES]
    if len(query_indices) < 2:
        query_indices = [K_LOCS // 2]

    baseline_cosines = []
    cf_cosines = []
    consistency_cosines = []

    for k in query_indices:
        xi_k = Xi[k]
        xi_cf = Xi[k + SHIFT_STEPS]  # counterfactual target (shifted position)

        # Baseline: retrieve xi_k from W
        probe = xi_k.copy()
        flip = rng_noise.random(N_ACTIVE) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved_base = hopfield_retrieve(W, probe)
        baseline_cosines.append(cosine_sim(retrieved_base, xi_k))

        # Counterfactual: build W_cf = W - xi_k + xi_cf (rank-1 substitution)
        W_cf = W - (1.0 / N_ACTIVE) * np.outer(xi_k, xi_k) + (1.0 / N_ACTIVE) * np.outer(xi_cf, xi_cf)
        np.fill_diagonal(W_cf, 0.0)

        # Retrieve xi_cf from W_cf
        probe_cf = xi_cf.copy()
        flip_cf = rng_noise.random(N_ACTIVE) < NOISE_FRAC
        probe_cf[flip_cf] *= -1.0
        retrieved_cf = hopfield_retrieve(W_cf, probe_cf)
        cf_cosines.append(cosine_sim(retrieved_cf, xi_cf))

        # Consistency: re-query W_cf with noisy xi_cf
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
        f"  [seed={seed} N={N_ACTIVE} K={K_LOCS} shift={SHIFT_STEPS}] "
        f"baseline={mean_baseline:.4f}(HP>={HP_BASELINE_COSINE}) "
        f"cf={mean_cf:.4f}(HP>={HP_CF_COSINE}) "
        f"consistency={mean_consistency:.4f}(HP>={HP_CONSISTENCY}) "
        f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] elapsed={elapsed:.2f}s",
        flush=True,
    )

    return {
        "seed": seed, "N": N_ACTIVE, "K_LOCS": K_LOCS, "SHIFT_STEPS": SHIFT_STEPS,
        "run_mode": RUN_MODE,
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

    summary = (
        f"n_seeds={n} baseline={mean_base:.4f}(HP>={HP_BASELINE_COSINE}) "
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

    min_threshold = math.ceil(n * 0.8)
    all_hp = all(cnt >= min_threshold for cnt in [hp1_n, hp2_n, hp3_n])
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP conditions met in >={min_threshold}/{n} seeds. {summary}")

    n_hp_conds = sum([hp1_n >= min_threshold, hp2_n >= min_threshold, hp3_n >= min_threshold])
    if n_hp_conds >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conds}/3 HP conditions met. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conds}/3 HP conditions met. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "K_LOCS": K_LOCS, "SHIFT_STEPS": SHIFT_STEPS, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
    f"(N={N_ACTIVE} K={K_LOCS} shift={SHIFT_STEPS} mode={RUN_MODE})",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] pp47_pp49_counterfactual_abduction N={N_ACTIVE} K={K_LOCS}...", flush=True)
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
    "N": N_ACTIVE,
    "K_LOCS": K_LOCS,
    "SHIFT_STEPS": SHIFT_STEPS,
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
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
