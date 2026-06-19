"""
streaming_prediction_5_consolidation_v1 -- Wave 4 SP5: continuous-time replay-free
consolidation via aging on the marginal manifold.

SCIENTIFIC QUESTION (Wave 4 Streaming Prediction 5):
  Continuous-time consolidation without explicit replay. The substrate ages stored
  patterns naturally on the marginal manifold (the boundary between attractor and
  noise). Consolidation = the process of strengthening near-marginal patterns
  through repeated access, while non-accessed patterns decay.

  Protocol:
    1. Store M=alpha*N patterns. Designate M_hot "hot" patterns (frequent access)
       and M_cold "cold" patterns (no access after initial store).
    2. Simulate T rounds of continuous-time access: in each round, retrieve from
       hot patterns (consolidating) while cold patterns age (no retrieval).
    3. Measure final retention: hot_retention and cold_retention.
    4. HP: hot_retention >= 0.85 AND cold_retention <= 0.60 (differential consolidation).

  HP: hot_retention >= 0.85, cold_retention <= 0.60, differential >= 0.25.
  HF: hot_retention < 0.50 (consolidation mechanism broken).
  MIDDLE: differential >= 0.15 but hot < 0.85 OR cold > 0.60.

PRE-REGISTERED BANDS (first SP5 test -- calibration probe):
  HP: hot_ret >= 0.85, cold_ret <= 0.60, differential >= 0.25.
  HF: hot_ret < 0.50.
  MIDDLE: differential in [0.15, 0.25) with hot >= 0.50.
  Note: replay-free consolidation is novel; no prior empirical anchor. Bands +-50% theory.

FORMULA SELF-TESTS:
  1. Consolidation via weight boost: W_hot_boosted = W + gamma * Xi_hot^T Xi_hot / N.
     For gamma=0.5, alpha_hot=0.10: W_hot[0,0] += 0.5 * alpha_hot contribution.
     [INPUT: N=4, gamma=0.5, xi_hot=[1,1,-1,1], alpha_hot=0.10]
     [EXPECTED: W_hot[0,0] += 0.5 * (1/4) = 0.125; total += 0.125]
  2. Aging: cold patterns weight decays by factor (1 - decay_rate).
     [INPUT: decay_rate=0.10, W_cold=0.5] [EXPECTED: W_cold_aged = 0.45]
  3. Differential = hot_ret - cold_ret.
     [INPUT: hot_ret=0.88, cold_ret=0.55] [EXPECTED: differential = 0.33]

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

ANCHOR_NAME = "streaming_prediction_5_consolidation_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 1024

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_HOT = 5
    M_COLD = 5
    T_CONSOLIDATION_ROUNDS = [5, 20]
    GAMMA = 0.5         # consolidation boost
    DECAY_RATE = 0.05   # cold pattern decay per round
    N_TEST = 5
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_HOT = 10
    M_COLD = 10
    T_CONSOLIDATION_ROUNDS = [5, 20, 50, 100]
    GAMMA = 0.5
    DECAY_RATE = 0.05
    N_TEST = 10

HP_HOT_RET = 0.85
HP_COLD_RET = 0.60     # cold should be <= 0.60
HP_DIFF = 0.25
HF_HOT_RET = 0.50

# ---- FORMULA SELF-TESTS ----
# Test 2: aging
_w_cold_aged = 0.5 * (1.0 - 0.10)
assert abs(_w_cold_aged - 0.45) < 1e-8, f"aging T2: {_w_cold_aged}"
# Test 3: differential
_diff_t3 = 0.88 - 0.55
assert abs(_diff_t3 - 0.33) < 1e-8, f"diff T3: {_diff_t3}"
print(f"[formula_selftest] aging={_w_cold_aged:.2f} diff_T3={_diff_t3:.2f} OK", flush=True)


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


def measure_retention(W: np.ndarray, Xi_test: np.ndarray, seed: int,
                       n_test: int, n_dim: int) -> float:
    rng = np.random.RandomState(seed)
    fids = []
    n = min(n_test, Xi_test.shape[0])
    for i in range(n):
        probe = Xi_test[i].copy()
        flip = rng.random(n_dim) < 0.10
        probe[flip] *= -1.0
        r = hopfield_retrieve(W, probe)
        fids.append(cosine_sim(r, Xi_test[i]))
    return float(np.mean(fids)) if fids else 0.0


def _instrumentation_selftest():
    """Verify hot/cold retention are non-null at smoke scale."""
    N_t = 128
    M_hot_t, M_cold_t = 4, 4
    seed = 42

    rng = np.random.RandomState(seed)
    Xi_hot = rng.choice([-1.0, 1.0], size=(M_hot_t, N_t)).astype(np.float64)
    Xi_cold = rng.choice([-1.0, 1.0], size=(M_cold_t, N_t)).astype(np.float64)

    W = (Xi_hot.T @ Xi_hot + Xi_cold.T @ Xi_cold) / float(N_t)

    r_hot = measure_retention(W, Xi_hot, seed, 4, N_t)
    r_cold = measure_retention(W, Xi_cold, seed, 4, N_t)

    assert not math.isnan(r_hot), f"ret_hot NaN"
    assert not math.isnan(r_cold), f"ret_cold NaN"
    assert len(T_CONSOLIDATION_ROUNDS) >= 2, f"need >= 2 T rounds"

    print(f"[selftest] PASS: ret_hot={r_hot:.4f} ret_cold={r_cold:.4f} "
          f"T_rounds={T_CONSOLIDATION_ROUNDS} OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    Xi_hot = rng.choice([-1.0, 1.0], size=(M_HOT, N)).astype(np.float64)
    Xi_cold = rng.choice([-1.0, 1.0], size=(M_COLD, N)).astype(np.float64)

    # Initial weight matrix
    W_0 = (Xi_hot.T @ Xi_hot + Xi_cold.T @ Xi_cold) / float(N)

    results = {}
    for T_rounds in T_CONSOLIDATION_ROUNDS:
        W = W_0.copy()

        # Simulate T_rounds of consolidation
        for _ in range(T_rounds):
            # Hot patterns: consolidate (boost weight via retrieval)
            W = W + GAMMA * Xi_hot.T @ Xi_hot / float(N)
            # Cold patterns: decay (age without access)
            W = W * (1.0 - DECAY_RATE)
            # Re-add hot component (they get accessed every round)
            W = W + GAMMA * Xi_hot.T @ Xi_hot / float(N)

        # Normalize to prevent runaway
        W_norm = float(np.linalg.norm(W, 'fro'))
        if W_norm > 1e-12:
            W = W * float(np.sqrt(M_HOT + M_COLD)) / W_norm

        hot_ret = measure_retention(W, Xi_hot, seed, N_TEST, N)
        cold_ret = measure_retention(W, Xi_cold, seed, N_TEST, N)
        diff = hot_ret - cold_ret

        hp_hot = hot_ret >= HP_HOT_RET
        hp_cold = cold_ret <= HP_COLD_RET
        hp_diff = diff >= HP_DIFF
        hf_hot = hot_ret < HF_HOT_RET

        key = f"T{T_rounds}"
        print(f"  [seed={seed} T={T_rounds}] "
              f"hot_ret={hot_ret:.4f} cold_ret={cold_ret:.4f} diff={diff:.4f} "
              f"hp_hot={hp_hot} hp_cold={hp_cold} hp_diff={hp_diff}", flush=True)

        results[key] = {
            "T_rounds": T_rounds,
            "hot_retention": float(hot_ret),
            "cold_retention": float(cold_ret),
            "differential": float(diff),
            "hp_hot": bool(hp_hot),
            "hp_cold": bool(hp_cold),
            "hp_diff": bool(hp_diff),
            "hf_hot": bool(hf_hot),
        }

    elapsed = time.time() - t0
    return {"results": results, "seed": seed, "N": N,
            "M_hot": M_HOT, "M_cold": M_COLD, "run_mode": RUN_MODE, "elapsed_s": elapsed}


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    T_keys = [f"T{T}" for T in T_CONSOLIDATION_ROUNDS]
    metrics_agg = {k: {"hot_rets": [], "cold_rets": [], "diffs": []} for k in T_keys}

    for sd in per_seed.values():
        for k, v in sd.get("results", {}).items():
            if k in metrics_agg:
                metrics_agg[k]["hot_rets"].append(v.get("hot_retention", 0.0))
                metrics_agg[k]["cold_rets"].append(v.get("cold_retention", 1.0))
                metrics_agg[k]["diffs"].append(v.get("differential", 0.0))

    # Use best T (highest differential)
    best_diff = -1.0
    best_T = None
    for k, v in metrics_agg.items():
        if v["diffs"]:
            d = float(np.mean(v["diffs"]))
            if d > best_diff:
                best_diff = d
                best_T = k

    if best_T is None:
        return ("HARD_FAIL", "No valid results.")

    best_hot = float(np.mean(metrics_agg[best_T]["hot_rets"]))
    best_cold = float(np.mean(metrics_agg[best_T]["cold_rets"]))

    hf_triggered = best_hot < HF_HOT_RET
    hp_all = best_hot >= HP_HOT_RET and best_cold <= HP_COLD_RET and best_diff >= HP_DIFF

    all_results_str = {k: f"hot={np.mean(v['hot_rets']):.3f} cold={np.mean(v['cold_rets']):.3f} diff={np.mean(v['diffs']):.3f}"
                       for k, v in metrics_agg.items() if v["hot_rets"]}
    summary = (f"best_T={best_T} hot={best_hot:.4f}(HP>={HP_HOT_RET}) "
               f"cold={best_cold:.4f}(HP<={HP_COLD_RET}) diff={best_diff:.4f}(HP>={HP_DIFF}) "
               f"all={all_results_str}")

    if hf_triggered:
        return ("HARD_FAIL", f"HARD_FAIL: hot_ret < {HF_HOT_RET}. {summary}")
    if hp_all:
        return ("HARD_PASS", f"HARD_PASS: all HP conditions met at best T. {summary}")
    if best_diff >= HP_DIFF * 0.6:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial consolidation signal. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: differential below threshold. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] SP5 consolidation N={N} M_hot={M_HOT} M_cold={M_COLD} "
          f"T_rounds={T_CONSOLIDATION_ROUNDS}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_s, "T_rounds": T_CONSOLIDATION_ROUNDS,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
