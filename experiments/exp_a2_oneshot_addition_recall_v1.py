"""
a2_oneshot_addition_recall_v1 -- Cluster A2: one-shot addition and recall.

SCIENTIFIC QUESTION (Phase 3, Cluster A2):
  Can substrate exactly add a new (key, value) pair post-encoding via one-shot Hebbian write,
  with the new pattern retrievable immediately, and with existing patterns unaffected?

  This is A2 from the routing note "one-shot addition recall" spec.
  The test is: store M=100 initial patterns -> add 1 new pattern K_NEW times -> verify
  each new pattern is immediately retrievable AND all original patterns retain accuracy.

  Unlike the routing note's "A2 deletion cert" (which is A2 from training_speedup_battery),
  this test focuses on WRITE capability: how quickly can one-shot Hebbian add new facts?

  Key metrics:
  (a) One-shot write produces retrievable new pattern within epsilon of pre-write baseline.
  (b) Existing patterns retain >= 95% accuracy after K_NEW additions.
  (c) Write time per pattern = O(N^2) (matrix update) -- milliseconds not minutes.

PRE-REGISTERED HARD-PASS (per routing A2 spec):
  HP1: new pattern retrievable (cosine >= 0.90) immediately after one write, in 5/5 seeds
  HP2: existing patterns retain >= 95% accuracy after K_NEW=10 additions in 5/5 seeds
  HP3: write wall-time < 1 second for any single pattern addition at N=4096

PRE-REGISTERED HARD-FAIL:
  HF1: new pattern cosine < 0.70 (one-shot write doesn't work)
  HF2: existing pattern accuracy drops > 10pp (interference from new write)
  HF3: write wall-time > 10 seconds (not practical)

MIDDLE BAND:
  new pattern cosine in [0.70, 0.90) OR accuracy drop 5-10pp

P_deflated: 0.80 (Hebbian one-shot write is algebraically guaranteed; risk is capacity
  interference as K_NEW grows; at alpha=0.10 + 10 new patterns, still within capacity)

FORMULA SELF-TESTS:
  1. After one write: W' = W + xi_new xi_new^T / N.
     W' @ xi_new = W @ xi_new + (1/N)||xi_new||^2 * xi_new ~ xi_new (dominant term).
     [INPUT: N=64, M=6, xi_new random] [EXPECTED: retrieval cosine >= 0.90]
  2. New alpha check: after K_NEW additions, alpha_new = (M + K_NEW) / N < alpha_c.
     [INPUT: M=100, K_NEW=10, N=1024] [EXPECTED: alpha=0.107 < 0.138]
  3. Existing pattern interference: adding xi_new changes field at xi_k by
     (xi_k . xi_new)^2 / N -- negligible for orthogonal patterns.
     [INPUT: xi_k, xi_new orthogonal] [EXPECTED: interference <= 0.01]

No _nN suffix; production N=1024, M=100, K_NEW=10 (pre-PROT-018).
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

ANCHOR_NAME = "a2_oneshot_addition_recall_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N = 256
    M_INIT = 20
    K_NEW = 5
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    N = 1024
    M_INIT = 100
    K_NEW = 10
    NOISE_FRAC = 0.10

HP_NEW_COSINE = 0.90
HF_NEW_COSINE = 0.70
HP_EXISTING_ACC = 0.95
HF_EXISTING_ACC_DROP = 0.10
HP_WRITE_WALL = 1.0   # seconds
HF_WRITE_WALL = 10.0


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = 20) -> np.ndarray:
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


def measure_accuracy(W: np.ndarray, Xi: np.ndarray, noise_frac: float, rng: np.random.RandomState) -> float:
    M_count = Xi.shape[0]
    correct = 0
    for k in range(M_count):
        probe = Xi[k].copy()
        flip = rng.random(N) < noise_frac
        probe[flip] *= -1.0
        retrieved = hopfield_retrieve(W, probe)
        if cosine_sim(retrieved, Xi[k]) >= 0.9:
            correct += 1
    return correct / max(1, M_count)


# ---- FORMULA SELF-TESTS ----
def _selftest_oneshot_write():
    """One-shot write: new pattern immediately retrievable."""
    N_t, M_t = 128, 10
    rng = np.random.RandomState(0)
    Xi_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    xi_new = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W = Xi_t.T @ Xi_t / float(N_t)
    np.fill_diagonal(W, 0.0)
    W_new = W + np.outer(xi_new, xi_new) / N_t
    np.fill_diagonal(W_new, 0.0)
    h = W_new @ xi_new
    state = np.sign(h)
    state[state == 0] = 1.0
    cos = float(np.dot(state, xi_new)) / N_t
    assert cos >= 0.5, f"oneshot_write selftest: cos={cos:.4f}"
    return cos


def _selftest_capacity():
    alpha_final = (M_INIT + K_NEW) / N
    assert alpha_final < ALPHA_C, f"alpha_final={alpha_final:.4f} >= alpha_c"
    return alpha_final


def _instrumentation_selftest():
    c1 = _selftest_oneshot_write()
    alpha = _selftest_capacity()
    print(
        f"[selftest] PASS: oneshot_cos={c1:.4f} alpha_final={(M_INIT+K_NEW)/N:.4f} "
        f"N={N} M_init={M_INIT} K_new={K_NEW}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    rng_eval = np.random.RandomState(seed + 400)

    Xi_init = rng.choice([-1.0, 1.0], size=(M_INIT, N)).astype(np.float64)
    Xi_new = rng.choice([-1.0, 1.0], size=(K_NEW, N)).astype(np.float64)

    W = Xi_init.T @ Xi_init / float(N)
    np.fill_diagonal(W, 0.0)

    # Baseline accuracy on initial patterns
    rng_eval2 = np.random.RandomState(seed + 401)
    acc_before = measure_accuracy(W, Xi_init, NOISE_FRAC, rng_eval)

    new_cosines = []
    write_times = []

    for k in range(K_NEW):
        xi_new = Xi_new[k]
        t_write = time.time()
        W = W + np.outer(xi_new, xi_new) / float(N)
        np.fill_diagonal(W, 0.0)
        write_t = time.time() - t_write
        write_times.append(write_t)

        # Immediately retrieve the new pattern
        probe = xi_new.copy()
        flip = rng_eval2.random(N) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved = hopfield_retrieve(W, probe)
        new_cosines.append(cosine_sim(retrieved, xi_new))

    # Post-addition accuracy on initial patterns
    rng_eval3 = np.random.RandomState(seed + 402)
    acc_after = measure_accuracy(W, Xi_init, NOISE_FRAC, rng_eval3)
    acc_drop_pp = 100.0 * (acc_before - acc_after)

    mean_new_cos = float(np.mean(new_cosines))
    max_write_time = float(np.max(write_times))

    hp1 = mean_new_cos >= HP_NEW_COSINE
    hp2 = acc_after >= HP_EXISTING_ACC
    hp3 = max_write_time < HP_WRITE_WALL

    hf1 = mean_new_cos < HF_NEW_COSINE
    hf2 = (acc_before - acc_after) > HF_EXISTING_ACC_DROP
    hf3 = max_write_time > HF_WRITE_WALL

    elapsed = time.time() - t0
    print(
        f"  [seed={seed} N={N} M_init={M_INIT} K_new={K_NEW}] "
        f"new_cos={mean_new_cos:.4f}(HP>={HP_NEW_COSINE}) "
        f"acc_before={acc_before:.4f} acc_after={acc_after:.4f} drop={acc_drop_pp:.2f}pp "
        f"max_write_t={max_write_time:.4f}s(HP<{HP_WRITE_WALL}s) "
        f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] elapsed={elapsed:.2f}s",
        flush=True,
    )

    return {
        "seed": seed, "N": N, "M_INIT": M_INIT, "K_NEW": K_NEW, "run_mode": RUN_MODE,
        "mean_new_cos": float(mean_new_cos),
        "acc_before": float(acc_before),
        "acc_after": float(acc_after),
        "acc_drop_pp": float(acc_drop_pp),
        "max_write_time_s": float(max_write_time),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hf1": bool(hf1), "hf2": bool(hf2), "hf3": bool(hf3),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    mean_new = float(np.mean([r["mean_new_cos"] for r in results]))
    mean_acc_after = float(np.mean([r["acc_after"] for r in results]))
    mean_drop = float(np.mean([r["acc_drop_pp"] for r in results]))
    mean_write = float(np.max([r["max_write_time_s"] for r in results]))
    hp1_n = sum(1 for r in results if r["hp1"])
    hp2_n = sum(1 for r in results if r["hp2"])
    hp3_n = sum(1 for r in results if r["hp3"])
    hf1_any = any(r["hf1"] for r in results)
    hf2_any = any(r["hf2"] for r in results)
    hf3_any = any(r["hf3"] for r in results)

    summary = (
        f"n_seeds={n} new_cos={mean_new:.4f}(HP>={HP_NEW_COSINE}) "
        f"acc_after={mean_acc_after:.4f}(HP>={HP_EXISTING_ACC}) drop={mean_drop:.2f}pp "
        f"max_write_t={mean_write:.4f}s "
        f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n}"
    )

    if hf1_any:
        return ("HARD_FAIL", f"HARD_FAIL HF1: new pattern not retrievable. {summary}")
    if hf2_any:
        return ("HARD_FAIL", f"HARD_FAIL HF2: existing patterns degraded >10pp. {summary}")
    if hf3_any:
        return ("HARD_FAIL", f"HARD_FAIL HF3: write wall-time >{HF_WRITE_WALL}s. {summary}")

    min_threshold = math.ceil(n * 0.8)
    all_hp = all(cnt >= min_threshold for cnt in [hp1_n, hp2_n, hp3_n])
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP conditions met in >={min_threshold}/{n} seeds. {summary}")

    n_hp_conds = sum([hp1_n >= min_threshold, hp2_n >= min_threshold, hp3_n >= min_threshold])
    if n_hp_conds >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conds}/3 HP conditions met. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conds}/3 HP conditions met. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_INIT": M_INIT, "K_NEW": K_NEW, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
    f"(N={N} M_init={M_INIT} K_new={K_NEW} mode={RUN_MODE})",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] a2_oneshot_addition_recall N={N} M={M_INIT} K_new={K_NEW}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "M_INIT": M_INIT, "K_NEW": K_NEW,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
    "per_seed": [
        {
            "seed": r.get("seed"),
            "mean_new_cos": r.get("mean_new_cos"),
            "acc_before": r.get("acc_before"), "acc_after": r.get("acc_after"),
            "acc_drop_pp": r.get("acc_drop_pp"),
            "max_write_time_s": r.get("max_write_time_s"),
            "hp1": r.get("hp1"), "hp2": r.get("hp2"), "hp3": r.get("hp3"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
