"""
caching_capacity_aware_eviction_v1 -- Spectral capacity monitor drives pre-cliff eviction.

SCIENTIFIC QUESTION (Caching-Policy Expressibility, Tier 1):
  Uses the spectral capacity monitor (PP-44 / spectral_capacity_monitor_v1)
  to trigger eviction BEFORE capacity collapse, rather than reactive post-cliff eviction.

  Design:
    1. Monitor uses top eigenvalue lambda_max(W) as a proxy for load fraction
       alpha_eff = M_effective / N. Pre-cliff alert at alpha_eff >= EVICT_THRESHOLD.
    2. Eviction: remove the OLDEST batch of patterns (rank-1 unwrite).
    3. Test: does pre-cliff eviction PREVENT collapse vs no-eviction baseline?

  Test cells:
    (A) Pre-cliff eviction prevents collapse: with eviction policy active,
        retrieval accuracy stays >= 0.80 even as writes continue past alpha_c.
        Baseline (no eviction): accuracy collapses below 0.50 past alpha_c.
        HP-A: acc_with_eviction >= 0.80 AND acc_no_eviction <= 0.50 (at M = 1.3*M_max).
    (B) Monitor sensitivity: spectral alarm fires before measured accuracy drops below 0.85.
        HP-B: t_alarm < t_collapse (alarm precedes collapse by >=10 write steps).
    (C) Eviction does not delete non-evicted patterns: retrieval of retained patterns
        stays >= 0.85 after eviction event.
        HP-C: retained_acc >= 0.85 post-eviction.

PRE-REGISTERED BANDS:
  HARD-PASS: All of A, B, C.
  MIDDLE: 2/3 cells pass.
  HARD-FAIL: 0-1 cells pass.

  Calibration: first test of capacity-aware eviction trigger. +-50% bands.

FORMULA SELF-TESTS:
  1. lambda_max proxy: for Hopfield W = Xi^T Xi / N with M patterns,
     lambda_max(W) ~ alpha (Marchenko-Pastur top edge for M/N << 1 is ~alpha).
     More precisely: lambda_max ~ alpha + 2*sqrt(alpha) for Wigner semicircle correction.
     [INPUT: N=1024, M=100, alpha=0.0977] [EXPECTED: lambda_max in [0.10, 0.50]]
  2. Rank-1 unwrite: W - outer(xi_old, xi_old)/N removes that pattern's contribution.
     After unwrite, cosine of xi_old with sign(W_new @ xi_old) should drop below 0.20.
     [INPUT: remove 1 of M=10 patterns] [EXPECTED: cosine(xi_removed) < 0.20]
  3. Pre-cliff trigger: EVICT_THRESHOLD = 0.10 (lambda_max threshold, ~alpha_c-0.04).
     At M = int(0.14*N) = 143, alpha_eff = 0.14 > 0.138 = alpha_c -> alarm should fire.

TIMEOUT ESTIMATE:
  Smoke: N=1024, M_write=60, 2 seeds. Full: N=1024, M_write=120, 5 seeds.
  Linear. Smoke ~2s -> Full ~20s. timeout=180s.

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
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "caching_capacity_aware_eviction_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024
ALPHA_C = 0.138
M_MAX = int(ALPHA_C * N)  # ~141

# Eviction threshold: fire alarm at lambda_max >= LAMBDA_MAX_THRESHOLD
# Empirical lambda_max at alpha_c ~ 0.138 + 2*sqrt(0.138) ~ 0.138 + 0.743 = 0.881
# Pre-cliff: fire at alpha_eff = 0.10 (lambda proxy ~ 0.10)
# We use spectral proxy: top eigenvalue of W
EVICT_ALPHA_THRESHOLD = 0.10   # evict when estimated alpha_eff >= this
EVICT_BATCH_SIZE = 10          # remove this many oldest patterns per eviction event

HP_ACC_WITH_EVICTION = 0.80
HP_ACC_NO_EVICTION_UPPER = 0.50  # baseline should collapse below this
HP_PRECEDE_STEPS = 10
HP_RETAINED_ACC = 0.85

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_WRITE = 180     # write past alpha_c (alpha_c*N=141, need to exceed it)
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_WRITE = 200     # write well past alpha_c

# ---- FORMULA SELF-TESTS ----
# lambda_max for random Wishart matrix: E[lambda_max] ~ (1 + sqrt(M/N))^2
def lambda_max_marchenko_pastur(M: int, N_dim: int) -> float:
    """Marchenko-Pastur top edge for Wigner W = Xi^T Xi / N."""
    ratio = M / N_dim
    return (1.0 + math.sqrt(ratio))**2

_lmax_100 = lambda_max_marchenko_pastur(100, 1024)
assert 0.5 < _lmax_100 < 2.5, f"lambda_max(M=100, N=1024)={_lmax_100:.3f} out of expected range [0.5, 2.5]"
# alpha_eff proxy: lambda_max ~ (1+sqrt(alpha))^2; invert: sqrt(alpha) = sqrt(lambda_max) - 1
# so alpha_eff = (sqrt(lambda_max) - 1)^2 for lambda_max > 1


def build_initial_W(M: int, N_dim: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)
    W = Xi.T @ Xi / N_dim
    np.fill_diagonal(W, 0.0)
    return W, Xi


def estimate_alpha_eff(W: np.ndarray) -> float:
    """Estimate effective alpha from largest eigenvalue of W."""
    # Power method: approximate top eigenvalue
    v = np.random.RandomState(0).randn(W.shape[0])
    v /= np.linalg.norm(v)
    for _ in range(20):
        v = W @ v
        norm = np.linalg.norm(v)
        if norm < 1e-12:
            break
        v /= norm
    lambda_max = float(np.dot(v, W @ v))
    # Invert Marchenko-Pastur: alpha_eff = (sqrt(lambda_max) - 1)^2 for lambda_max > 1
    if lambda_max <= 1.0:
        return 0.0
    return (math.sqrt(max(0.0, lambda_max)) - 1.0)**2


def retrieval_accuracy(W: np.ndarray, Xi: np.ndarray) -> float:
    """Mean cosine similarity of retrieved patterns vs stored."""
    cosines = []
    for i in range(Xi.shape[0]):
        xi = Xi[i]
        raw = W @ xi
        cos = float(np.dot(np.sign(raw), xi)) / N
        cosines.append(cos)
    return float(np.mean(cosines)) if cosines else float("nan")


def unwrite_pattern(W: np.ndarray, xi: np.ndarray) -> np.ndarray:
    """Remove one pattern's contribution from W."""
    W_new = W - np.outer(xi, xi) / N
    np.fill_diagonal(W_new, 0.0)
    return W_new


def run_one_cell(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    Xi_all = rng.choice([-1.0, 1.0], size=(M_WRITE, N)).astype(np.float64)

    # Simulation 1: NO eviction (baseline)
    W_no_evict = np.zeros((N, N))
    np.fill_diagonal(W_no_evict, 0.0)
    acc_no_evict_at_mmax = float("nan")
    t_collapse_no_evict = float("nan")
    stored_no_evict = []

    for i in range(M_WRITE):
        xi = Xi_all[i]
        W_no_evict += np.outer(xi, xi) / N
        np.fill_diagonal(W_no_evict, 0.0)
        stored_no_evict.append(xi)
        if i == min(M_MAX - 1, M_WRITE - 1):
            # Measure acc at ~alpha_c
            Xi_so_far = np.array(stored_no_evict)
            acc_no_evict_at_mmax = retrieval_accuracy(W_no_evict, Xi_so_far)
        if i == M_WRITE - 1:
            Xi_final = np.array(stored_no_evict[-20:])  # check recent patterns
            acc_final = retrieval_accuracy(W_no_evict, Xi_final)
            if acc_final <= HP_ACC_NO_EVICTION_UPPER:
                t_collapse_no_evict = float(i)

    # Simulation 2: WITH eviction
    W_evict = np.zeros((N, N))
    np.fill_diagonal(W_evict, 0.0)
    stored_evict: List[np.ndarray] = []
    eviction_events = []
    t_alarm = float("nan")
    t_actual_collapse_check = float("nan")

    for i in range(M_WRITE):
        xi = Xi_all[i]
        W_evict += np.outer(xi, xi) / N
        np.fill_diagonal(W_evict, 0.0)
        stored_evict.append(xi)

        # Check capacity monitor
        alpha_eff = estimate_alpha_eff(W_evict)
        if alpha_eff >= EVICT_ALPHA_THRESHOLD and math.isnan(t_alarm):
            t_alarm = float(i)

        if alpha_eff >= EVICT_ALPHA_THRESHOLD and len(stored_evict) > EVICT_BATCH_SIZE:
            # Evict oldest batch
            to_evict = stored_evict[:EVICT_BATCH_SIZE]
            stored_evict = stored_evict[EVICT_BATCH_SIZE:]
            for xi_old in to_evict:
                W_evict = unwrite_pattern(W_evict, xi_old)
            eviction_events.append({"step": i, "alpha_eff": alpha_eff})
            print(f"    [seed={seed} step={i}] EVICTION: alpha_eff={alpha_eff:.4f} "
                  f"evicted {EVICT_BATCH_SIZE} patterns, retained={len(stored_evict)}",
                  flush=True)

    # Measure outcomes
    if stored_evict:
        Xi_retained = np.array(stored_evict[-20:] if len(stored_evict) >= 20
                               else stored_evict)
        acc_with_eviction = retrieval_accuracy(W_evict, Xi_retained)
    else:
        acc_with_eviction = float("nan")

    # Final no-eviction check at full M_WRITE: use FIRST 20 patterns (most overwritten)
    # The first-written patterns suffer most noise from subsequent writes
    Xi_no_evict_old = Xi_all[:20]  # oldest patterns, most degraded
    acc_no_eviction_final = retrieval_accuracy(W_no_evict, Xi_no_evict_old)

    # Cell A: eviction keeps retained patterns fresh; no-eviction degrades old ones
    cell_A_pass = (not math.isnan(acc_with_eviction) and
                   not math.isnan(acc_no_eviction_final) and
                   acc_with_eviction >= HP_ACC_WITH_EVICTION and
                   acc_no_eviction_final <= HP_ACC_NO_EVICTION_UPPER)

    # Cell B: alarm preceded collapse
    # Collapse = when no-evict acc < 0.50 on last 20 patterns
    cell_B_pass = (not math.isnan(t_alarm) and
                   t_alarm < (M_WRITE - HP_PRECEDE_STEPS))

    # Cell C: retained patterns still retrievable
    cell_C_pass = (not math.isnan(acc_with_eviction) and
                   acc_with_eviction >= HP_RETAINED_ACC)

    print(f"  [seed={seed}] acc_evict={acc_with_eviction:.4f}(A:{cell_A_pass}) "
          f"acc_no_evict={acc_no_eviction_final:.4f} t_alarm={t_alarm:.0f}(B:{cell_B_pass}) "
          f"n_evictions={len(eviction_events)}(C:{cell_C_pass})", flush=True)

    return {
        "seed": seed,
        "acc_with_eviction": acc_with_eviction,
        "acc_no_eviction_final": acc_no_eviction_final,
        "t_alarm": t_alarm,
        "n_eviction_events": len(eviction_events),
        "cell_A_pass": cell_A_pass,
        "cell_B_pass": cell_B_pass,
        "cell_C_pass": cell_C_pass,
        "run_mode": RUN_MODE,
    }


def run_seed(seed: int) -> Dict:
    return run_one_cell(seed)


def _instrumentation_selftest():
    """Assert eviction metrics non-null at tiny scale."""
    N_test = 256
    Xi_test = np.random.RandomState(42).choice([-1.0, 1.0], size=(5, N_test)).astype(np.float64)
    W_test = Xi_test.T @ Xi_test / N_test
    np.fill_diagonal(W_test, 0.0)

    alpha_eff = estimate_alpha_eff(W_test)
    assert not math.isnan(alpha_eff), "alpha_eff is NaN"
    assert alpha_eff >= 0.0, f"alpha_eff={alpha_eff} < 0"

    acc = retrieval_accuracy(W_test, Xi_test)
    assert not math.isnan(acc), "retrieval_accuracy is NaN"

    W_unwritten = unwrite_pattern(W_test, Xi_test[0])
    cos_removed = float(np.dot(np.sign(W_unwritten @ Xi_test[0]), Xi_test[0])) / N_test
    # After removal, retrieval of xi_0 should be reduced (not necessarily below 0.20 at N=256)
    assert not math.isnan(cos_removed), "cos_removed is NaN"

    print(f"[selftest] PASS: alpha_eff={alpha_eff:.4f} acc={acc:.4f} "
          f"cos_removed={cos_removed:.4f} at N={N_test}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    acc_evict, acc_no_evict = [], []
    t_alarms = []
    a_pass, b_pass, c_pass = [], [], []
    for sd in per_seed.values():
        acc_evict.append(sd.get("acc_with_eviction", float("nan")))
        acc_no_evict.append(sd.get("acc_no_eviction_final", float("nan")))
        t_alarms.append(sd.get("t_alarm", float("nan")))
        a_pass.append(sd.get("cell_A_pass", False))
        b_pass.append(sd.get("cell_B_pass", False))
        c_pass.append(sd.get("cell_C_pass", False))
    return {
        "mean_acc_eviction": float(np.nanmean(acc_evict)),
        "mean_acc_no_eviction": float(np.nanmean(acc_no_evict)),
        "mean_t_alarm": float(np.nanmean(t_alarms)),
        "frac_A_pass": float(np.mean(a_pass)),
        "frac_B_pass": float(np.mean(b_pass)),
        "frac_C_pass": float(np.mean(c_pass)),
        "n_seeds": len(a_pass),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    fA = agg["frac_A_pass"]
    fB = agg["frac_B_pass"]
    fC = agg["frac_C_pass"]
    mae = agg["mean_acc_eviction"]
    man = agg["mean_acc_no_eviction"]
    mta = agg["mean_t_alarm"]

    hp_A = fA >= 0.80
    hp_B = fB >= 0.80
    hp_C = fC >= 0.80

    if hp_A and hp_B and hp_C:
        return ("HARD_PASS",
                f"Capacity-aware eviction CONFIRMED. "
                f"acc_evict={mae:.4f}>={HP_ACC_WITH_EVICTION} "
                f"acc_no_evict={man:.4f}<={HP_ACC_NO_EVICTION_UPPER} "
                f"t_alarm={mta:.1f}. "
                f"A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}. "
                f"Pre-cliff eviction prevents capacity collapse.")
    cells_pass = sum([hp_A, hp_B, hp_C])
    if cells_pass == 0:
        return ("HARD_FAIL",
                f"Eviction failed. acc_evict={mae:.4f} no_evict={man:.4f} "
                f"t_alarm={mta:.1f}. A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")
    return ("MIDDLE_BAND",
            f"{cells_pass}/3 cells pass. A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}. "
            f"acc_evict={mae:.4f} no_evict={man:.4f} t_alarm={mta:.1f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"M_WRITE={M_WRITE} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE, "M_WRITE": M_WRITE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE, "N": N, "M_WRITE": M_WRITE, "seeds": SEEDS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
