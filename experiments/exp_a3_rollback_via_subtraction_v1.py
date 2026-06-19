"""
a3_rollback_via_subtraction_v1 -- Cluster A3: exact rollback via rank-1 subtraction.

SCIENTIFIC QUESTION (Phase 3, Cluster A3 = routing A3 rollback):
  Can substrate exactly rollback (undo) a previously written pattern via rank-1 subtraction,
  restoring W to within 1e-10 of the pre-write state?

  This is the "exact rollback" primitive: W_rollback = W + delta_W - delta_W = W.
  Specifically: write xi to W -> get W' = W + (1/N) xi xi^T -> rollback to
  W_rb = W' - (1/N) xi xi^T = W. Verify ||W_rb - W||_F < 1e-10.

  Physical interpretation: substrate can "undo" any single write event algebraically,
  with no numerical error accumulation. This is the substrate's "exact rollback" moat:
  no gradient-based system can achieve machine-precision rollback without replay.

PRE-REGISTERED HARD-PASS:
  HP1: ||W_rollback - W_original||_F / ||W_original||_F < 1e-10 (machine precision)
  HP2: retrieval accuracy on pre-rollback patterns >= 0.95 (no interference)
  HP3: rollback wall-time < 0.1 seconds (faster than gradient replay)

PRE-REGISTERED HARD-FAIL:
  HF1: ||relative error||_F > 1e-6 (numerical precision broken)
  HF2: retrieval accuracy drops > 5pp (rollback corrupts stored patterns)

MIDDLE BAND:
  relative error in [1e-10, 1e-6] OR accuracy drop 1-5pp

P_deflated: 0.90 (algebraically guaranteed by rank-1 structure; fp64 precision gives
  < 1e-14 relative error at N=1024; this is a structural property not a hypothesis)

FORMULA SELF-TESTS:
  1. Rollback identity: W + xi xi^T / N - xi xi^T / N = W exactly.
     [INPUT: N=4, W random, xi random] [EXPECTED: ||W_rb - W||_F = 0 exactly]
  2. Multiple rollbacks: writing then rolling back K times still returns to W.
     [INPUT: K=10 writes then K rollbacks in reverse order] [EXPECTED: ||W_rb - W||_F < 1e-12]
  3. Accuracy preserved: after rollback, patterns stored in W before the write still retrieve.
     [INPUT: M=50 patterns, 1 write, 1 rollback] [EXPECTED: accuracy restored to pre-write]

No _nN suffix; production N=1024 (pre-PROT-018).
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

ANCHOR_NAME = "a3_rollback_via_subtraction_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N = 512
    M_BASE = 40
    K_WRITES = 5    # write K patterns then rollback K
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    N = 1024
    M_BASE = 100
    K_WRITES = 20
    NOISE_FRAC = 0.10

HP_RELATIVE_ERR = 1e-10
HF_RELATIVE_ERR = 1e-6
HP_ACC_AFTER = 0.95
HF_ACC_DROP = 0.05
HP_ROLLBACK_WALL = 0.1   # seconds


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
def _selftest_rollback_identity():
    N_t = 64
    rng = np.random.RandomState(0)
    W_t = rng.randn(N_t, N_t)
    W_t = (W_t + W_t.T) / 2
    np.fill_diagonal(W_t, 0.0)
    xi = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W_written = W_t + np.outer(xi, xi) / N_t
    W_rolled = W_written - np.outer(xi, xi) / N_t
    err = float(np.linalg.norm(W_rolled - W_t, 'fro')) / max(float(np.linalg.norm(W_t, 'fro')), 1e-12)
    assert err < 1e-13, f"rollback_identity selftest: err={err:.2e}"
    return err


def _selftest_multi_rollback():
    N_t = 32
    K_t = 5
    rng = np.random.RandomState(1)
    W_t = np.zeros((N_t, N_t), dtype=np.float64)
    Xi_writes = [rng.choice([-1.0, 1.0], size=N_t).astype(np.float64) for _ in range(K_t)]
    for xi in Xi_writes:
        W_t = W_t + np.outer(xi, xi) / N_t
    W_written = W_t.copy()
    for xi in reversed(Xi_writes):
        W_written = W_written - np.outer(xi, xi) / N_t
    err = float(np.linalg.norm(W_written, 'fro'))
    assert err < 1e-12, f"multi_rollback selftest: err={err:.2e}"
    return err


def _selftest_capacity():
    alpha = (M_BASE + K_WRITES) / N
    assert alpha < ALPHA_C, f"alpha={alpha:.4f} >= alpha_c"
    return alpha


def _instrumentation_selftest():
    e1 = _selftest_rollback_identity()
    e2 = _selftest_multi_rollback()
    alpha = _selftest_capacity()
    print(
        f"[selftest] PASS: rollback_err={e1:.2e} multi_rollback_err={e2:.2e} "
        f"alpha={(M_BASE+K_WRITES)/N:.4f} N={N} M={M_BASE} K_writes={K_WRITES}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    rng_eval = np.random.RandomState(seed + 400)

    Xi_base = rng.choice([-1.0, 1.0], size=(M_BASE, N)).astype(np.float64)
    Xi_writes = rng.choice([-1.0, 1.0], size=(K_WRITES, N)).astype(np.float64)

    W_original = Xi_base.T @ Xi_base / float(N)
    np.fill_diagonal(W_original, 0.0)

    # Baseline accuracy
    rng_eval2 = np.random.RandomState(seed + 401)
    acc_before = measure_accuracy(W_original, Xi_base, NOISE_FRAC, rng_eval)

    # Write K_WRITES patterns
    W_current = W_original.copy()
    for xi in Xi_writes:
        W_current = W_current + np.outer(xi, xi) / float(N)
        np.fill_diagonal(W_current, 0.0)

    # Rollback all K_WRITES patterns in reverse order
    t_rollback_start = time.time()
    W_rolled = W_current.copy()
    for xi in reversed(Xi_writes):
        W_rolled = W_rolled - np.outer(xi, xi) / float(N)
        np.fill_diagonal(W_rolled, 0.0)
    rollback_wall = time.time() - t_rollback_start

    # Verify rollback precision
    w_norm = max(float(np.linalg.norm(W_original, 'fro')), 1e-12)
    relative_err = float(np.linalg.norm(W_rolled - W_original, 'fro')) / w_norm

    # Verify accuracy restored after rollback
    rng_eval3 = np.random.RandomState(seed + 402)
    acc_after = measure_accuracy(W_rolled, Xi_base, NOISE_FRAC, rng_eval3)
    acc_drop_pp = 100.0 * (acc_before - acc_after)

    hp1 = relative_err < HP_RELATIVE_ERR
    hp2 = acc_after >= HP_ACC_AFTER
    hp3 = rollback_wall < HP_ROLLBACK_WALL

    hf1 = relative_err > HF_RELATIVE_ERR
    hf2 = (acc_before - acc_after) > HF_ACC_DROP

    elapsed = time.time() - t0
    print(
        f"  [seed={seed} N={N} M={M_BASE} K_w={K_WRITES}] "
        f"rel_err={relative_err:.2e}(HP<{HP_RELATIVE_ERR:.0e}) "
        f"acc_before={acc_before:.4f} acc_after={acc_after:.4f} drop={acc_drop_pp:.2f}pp "
        f"rollback_t={rollback_wall:.4f}s(HP<{HP_ROLLBACK_WALL}s) "
        f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] elapsed={elapsed:.2f}s",
        flush=True,
    )

    return {
        "seed": seed, "N": N, "M_BASE": M_BASE, "K_WRITES": K_WRITES,
        "run_mode": RUN_MODE,
        "relative_err": float(relative_err),
        "acc_before": float(acc_before),
        "acc_after": float(acc_after),
        "acc_drop_pp": float(acc_drop_pp),
        "rollback_wall_s": float(rollback_wall),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hf1": bool(hf1), "hf2": bool(hf2),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    mean_err = float(np.mean([r["relative_err"] for r in results]))
    mean_acc = float(np.mean([r["acc_after"] for r in results]))
    mean_drop = float(np.mean([r["acc_drop_pp"] for r in results]))
    max_wall = float(np.max([r["rollback_wall_s"] for r in results]))
    hp1_n = sum(1 for r in results if r["hp1"])
    hp2_n = sum(1 for r in results if r["hp2"])
    hp3_n = sum(1 for r in results if r["hp3"])
    hf1_any = any(r["hf1"] for r in results)
    hf2_any = any(r["hf2"] for r in results)

    summary = (
        f"n_seeds={n} rel_err={mean_err:.2e}(HP<{HP_RELATIVE_ERR:.0e}) "
        f"acc_after={mean_acc:.4f}(HP>={HP_ACC_AFTER}) drop={mean_drop:.2f}pp "
        f"max_rollback_t={max_wall:.4f}s "
        f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n}"
    )

    if hf1_any:
        return ("HARD_FAIL", f"HARD_FAIL HF1: rollback precision broken (rel_err>{HF_RELATIVE_ERR:.0e}). {summary}")
    if hf2_any:
        return ("HARD_FAIL", f"HARD_FAIL HF2: rollback corrupts existing patterns. {summary}")

    min_threshold = math.ceil(n * 0.8)
    all_hp = all(cnt >= min_threshold for cnt in [hp1_n, hp2_n, hp3_n])
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP conditions met in >={min_threshold}/{n} seeds. {summary}")

    n_hp_conds = sum([hp1_n >= min_threshold, hp2_n >= min_threshold, hp3_n >= min_threshold])
    if n_hp_conds >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conds}/3 HP conditions met. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conds}/3 HP conditions met. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_BASE": M_BASE, "K_WRITES": K_WRITES, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
    f"(N={N} M={M_BASE} K_writes={K_WRITES} mode={RUN_MODE})",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] a3_rollback_via_subtraction N={N} M={M_BASE}...", flush=True)
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
    "N": N, "M_BASE": M_BASE, "K_WRITES": K_WRITES,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
    "per_seed": [
        {
            "seed": r.get("seed"),
            "relative_err": r.get("relative_err"),
            "acc_before": r.get("acc_before"), "acc_after": r.get("acc_after"),
            "rollback_wall_s": r.get("rollback_wall_s"),
            "hp1": r.get("hp1"), "hp2": r.get("hp2"), "hp3": r.get("hp3"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
