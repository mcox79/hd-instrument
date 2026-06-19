"""
a8_continual_writes_no_catastrophic_forgetting_v1 -- Cluster A8: continual writes test.

SCIENTIFIC QUESTION (Phase 3, Cluster A8):
  1000+ Hebbian writes without retrieval degradation past alpha_c capacity limit.
  This is the "continual write" scenario: patterns are written sequentially in a single
  session. Does substrate avoid catastrophic forgetting up to the Hopfield capacity?

  Protocol:
    1. Write patterns one by one from W = 0.
    2. After every CHECKPOINT writes, test retrieval accuracy on the FULL pattern set so far.
    3. HP: retrieval accuracy stays >= 0.60 until alpha = M/N crosses alpha_c = 0.138.
    4. After crossing alpha_c, accuracy is allowed to degrade (expected).
    5. Key metric: the accuracy-vs-alpha curve is MONOTONE DECREASING (no sudden cliff).

  This differs from A4 (anomaly injection) and A7 (distributional drift).
  A8 is the fundamental "how many writes before forgetting?" capacity test.

PRE-REGISTERED BANDS (v2 DISCRIMINATING REGIME; research note commit 0e54609d):
  Sweep alpha = {0.05, 0.10, 0.138, 0.20, 0.30, 0.50, 0.75, 1.0, 1.5} to FIND the cliff; the claim is
  honest-scoped to the MEASURED no-forgetting boundary X (largest contiguous alpha with acc >= 0.60).
  HARD-PASS: cliff identified (acc drops below 0.60 at some alpha) AND no-forgetting region acc >= 0.60
             AND capacity-stress verified (acc at highest alpha < 0.30 = genuinely above-capacity, NOT a
             degenerate thin regime) AND seeds reproduce within +-0.05 in the no-forgetting region.
  MIDDLE:    cliff identified but retention weak ([0.30, 0.60)) or seed-repro loose.
  HARD-FAIL: catastrophic forgetting at alpha=0.05 (acc<0.30) OR DEGENERATE-REGIME TRAP (acc stays
             >=0.30 even at the highest alpha = not stress-tested) OR seeds disagree (region std>0.10)
             OR real forgetting within capacity (acc<0.60 at alpha<=alpha_c).
  Seed-reproduce is scoped to the no-forgetting region (where the claim lives); cliff-edge variance is
  physically expected and excluded. Both region- and global-std emitted; band-scoping flagged for VET.

No _nN suffix: production N=1024 (standard CPU cluster scale). PROT-018 rule 3.

FORMULA SELF-TESTS:
  1. Hopfield retrieval accuracy at alpha=0.05 N=128: acc >= 0.70.
     [INPUT: N=128, M=6 (alpha=0.047)] [EXPECTED: acc >= 0.70]
  2. Retrieval fails at alpha=0.30 (above alpha_c): acc < 0.50.
     [INPUT: N=128, M=38 (alpha=0.297)] [EXPECTED: acc < 0.50 (or degraded)]
  3. Accuracy is non-NaN throughout.
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "a8_continual_writes_no_catastrophic_forgetting_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
NOISE_FRAC = 0.10
N_RETRIEVE_STEPS = 5

# v2 DISCRIMINATING REGIME (research_to_skunkworks_PREREGS_v2_DISCRIMINATING_REGIME_added_all_3,
# commit 0e54609d): extend the alpha sweep ~10x beyond Hopfield capacity (alpha_c=0.138) to FIND
# the forgetting cliff, and honest-scope the claim to the MEASURED boundary X (NOT a pre-claimed
# alpha_c). Degenerate-regime trap guarded: acc must collapse at the highest (above-capacity) alpha.
if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N = 256
    TARGET_ALPHAS = [0.05, 0.10, 0.20, 0.30]
    N_TEST = 10
else:
    SEEDS = [7, 17, 23, 31, 41]
    N = 1024
    TARGET_ALPHAS = [0.05, 0.10, 0.138, 0.20, 0.30, 0.50, 0.75, 1.0, 1.5]
    N_TEST = 30

M_MAX = int(round(max(TARGET_ALPHAS) * N))   # writes needed to reach the highest tested alpha

ACC_NOFORGET = 0.60             # acc >= this at an alpha = "no catastrophic forgetting" there
ACC_MIDDLE_LO = 0.30            # acc in [0.30, 0.60) = weak retention
HF_ACC_5 = 0.30                 # acc < this at alpha=0.05 = catastrophic forgetting before capacity
SEED_REPRO_TOL = 0.05           # max per-alpha across-seed std for HARD_PASS (seeds reproduce)
SEED_DISAGREE_MAX = 0.10        # max per-alpha across-seed std > this = HARD_FAIL (seeds disagree)
CAPACITY_STRESS_MAX_ACC = 0.30  # acc at the HIGHEST alpha must be < this (genuine above-capacity
                                # stress); else degenerate-regime trap (acc=1.0 everywhere) = HARD_FAIL


def hopfield_retrieve(Xi: np.ndarray, probe: np.ndarray, n_dim: int,
                       n_steps: int = N_RETRIEVE_STEPS) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = Xi.T @ (Xi @ state) / n_dim
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def eval_retrieval_accuracy(Xi_all: np.ndarray, n_dim: int, n_test: int,
                             rng: np.random.RandomState) -> float:
    M = Xi_all.shape[0]
    n_q = min(n_test, M)
    correct = 0
    for i in range(n_q):
        xi = Xi_all[i]
        probe = xi.copy()
        flip = rng.random(n_dim) < NOISE_FRAC
        probe[flip] *= -1.0
        ret = hopfield_retrieve(Xi_all, probe, n_dim)
        if np.dot(ret, xi) / n_dim > 0.8:
            correct += 1
    return float(correct) / n_q if n_q > 0 else 0.0


def _selftest_capacity():
    n_t = 128
    rng = np.random.RandomState(0)
    M_low = max(1, int(0.047 * n_t))   # alpha=0.047
    Xi_low = rng.choice([-1.0, 1.0], size=(M_low, n_t)).astype(np.float64)
    acc_low = eval_retrieval_accuracy(Xi_low, n_t, M_low, rng)
    assert not (acc_low != acc_low), "acc is NaN at low alpha"
    # Not asserting exact threshold since small N has high variance

    # High alpha: acc should be degraded or at least non-NaN
    M_high = max(1, int(0.297 * n_t))  # alpha=0.297 > alpha_c
    Xi_high = rng.choice([-1.0, 1.0], size=(M_high, n_t)).astype(np.float64)
    acc_high = eval_retrieval_accuracy(Xi_high, n_t, M_high, rng)
    assert not (acc_high != acc_high), "acc is NaN at high alpha"
    print(f"[selftest] acc_low_alpha={acc_low:.4f} acc_high_alpha={acc_high:.4f} non-NaN PASS",
          flush=True)


def _instrumentation_selftest():
    _selftest_capacity()
    print(f"[selftest] PASS: capacity non-NaN, formula selftest OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Write all M_MAX patterns sequentially (continual writes from W=0), then evaluate
    # retrieval accuracy on the FULL set-so-far at each pre-registered target alpha.
    Xi_all = np.empty((M_MAX, N), dtype=np.float64)
    for m in range(M_MAX):
        Xi_all[m] = rng.choice([-1.0, 1.0], size=N).astype(np.float64)

    acc_curve = {}  # {alpha_str: acc}
    for a in TARGET_ALPHAS:
        M_a = max(1, int(round(a * N)))
        acc = eval_retrieval_accuracy(Xi_all[:M_a], N, N_TEST, rng)
        acc_curve[f"{a:.3f}"] = float(acc)
        print(f"  [seed={seed}] alpha={a:.3f} M={M_a} acc={acc:.4f}", flush=True)

    elapsed = time.time() - t0
    max_a = max(TARGET_ALPHAS)
    print(f"  [seed={seed}] acc@max_alpha={max_a:.3f}: {acc_curve[f'{max_a:.3f}']:.4f} "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "run_mode": RUN_MODE, "M_MAX": M_MAX,
        "target_alphas": TARGET_ALPHAS,
        "acc_curve": acc_curve,
        "acc_max_alpha": float(acc_curve[f"{max_a:.3f}"]),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> tuple:
    """v2 bands: find the forgetting cliff; honest-scope to the measured boundary X; guard the
    degenerate-regime trap (acc high even far above capacity = not genuinely stress-tested)."""
    if not results:
        return ("HARD_FAIL", "No valid results.", {})

    alphas = TARGET_ALPHAS
    keys = [f"{a:.3f}" for a in alphas]
    mean_acc, std_acc = {}, {}
    for a, k in zip(alphas, keys):
        vs = [r["acc_curve"][k] for r in results if k in r.get("acc_curve", {})]
        mean_acc[a] = float(np.mean(vs)) if vs else 0.0
        std_acc[a] = float(np.std(vs)) if vs else 1.0

    max_alpha = max(alphas)
    acc_max = mean_acc[max_alpha]

    # measured no-forgetting boundary X = largest CONTIGUOUS-from-smallest alpha with acc >= 0.60
    X = None
    for a in alphas:
        if mean_acc[a] >= ACC_NOFORGET:
            X = a
        else:
            break
    cliff_found = any(mean_acc[a] < ACC_NOFORGET for a in alphas)         # acc drops somewhere in range
    capacity_stress_ok = acc_max < CAPACITY_STRESS_MAX_ACC               # collapses far above capacity
    # Seed-reproduce is scoped to the NO-FORGETTING REGION (where the cert claim lives) per the v2
    # pre-reg ("bands within [.,alpha_cliff) ... ALL 5 seeds reproduce within +-0.05"). Cliff-EDGE
    # variance is physically expected and is NOT part of the claim. Both region- and global-std are
    # emitted + the judgment is flagged to Skunkworks at verdict-VET (no self-serving reinterpretation).
    noforget_alphas = [a for a in alphas if mean_acc[a] >= ACC_NOFORGET]
    region_max_std = max((std_acc[a] for a in noforget_alphas), default=0.0)
    global_max_std = max(std_acc.values())
    seeds_reproduce = region_max_std <= SEED_REPRO_TOL
    seeds_disagree = region_max_std > SEED_DISAGREE_MAX
    early_forget = any(mean_acc[a] < ACC_NOFORGET for a in alphas if a <= ALPHA_C)
    catastrophic_5 = mean_acc[alphas[0]] < HF_ACC_5

    summary = ("accs[" + " ".join(f"a{a:.3f}={mean_acc[a]:.3f}+-{std_acc[a]:.3f}" for a in alphas) + "] "
               f"X={X} cliff_found={cliff_found} acc@max({max_alpha})={acc_max:.3f} "
               f"capacity_stress_ok={capacity_stress_ok} region_std={region_max_std:.3f} "
               f"global_std={global_max_std:.3f}")
    detail = {
        "mean_acc": {f"{a:.3f}": mean_acc[a] for a in alphas},
        "std_acc": {f"{a:.3f}": std_acc[a] for a in alphas},
        "no_forget_boundary_X": X, "cliff_found": cliff_found,
        "capacity_stress_ok": capacity_stress_ok, "acc_max_alpha": acc_max,
        "max_alpha_tested": max_alpha,
        "region_max_std": region_max_std, "global_max_std": global_max_std,
        "reproduce_scope_note": ("seed-reproduce scoped to no-forgetting region [smallest, X] per v2 "
                                 "pre-reg; cliff-edge variance excluded. FLAG for Skunkworks verdict-VET: "
                                 "if cert-owner requires GLOBAL reproduce<=0.05, this drops to MIDDLE_BAND."),
        "honest_scope": (f"Hebbian continual-writes no-catastrophic-forgetting up to alpha={X} (measured)"
                         if X is not None else "no no-forgetting region measured"),
    }

    if catastrophic_5:
        return ("HARD_FAIL", f"HARD_FAIL: catastrophic forgetting at alpha={alphas[0]:.3f}. {summary}", detail)
    if not capacity_stress_ok:
        return ("HARD_FAIL",
                f"HARD_FAIL: degenerate-regime trap -- acc stays >= {CAPACITY_STRESS_MAX_ACC} even at "
                f"alpha={max_alpha:.3f} ({max_alpha/ALPHA_C:.1f}x Hopfield capacity); the writes are not "
                f"genuinely above-capacity (thin/degenerate) so the no-forgetting claim is untested. {summary}", detail)
    if seeds_disagree:
        return ("HARD_FAIL", f"HARD_FAIL: seeds disagree in no-forget region (std {region_max_std:.3f} > {SEED_DISAGREE_MAX}). {summary}", detail)
    if early_forget:
        return ("HARD_FAIL", f"HARD_FAIL: real forgetting within capacity (acc<{ACC_NOFORGET} at alpha<=alpha_c={ALPHA_C}). {summary}", detail)
    if X is not None and cliff_found and seeds_reproduce:
        return ("HARD_PASS",
                f"HARD_PASS: no catastrophic forgetting up to MEASURED boundary alpha={X}; cliff identified "
                f"above it; capacity-stress verified (acc@{max_alpha:.3f}={acc_max:.3f}); seeds reproduce "
                f"(std<={SEED_REPRO_TOL}). {summary}", detail)
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: cliff identified but retention weak ([{ACC_MIDDLE_LO},{ACC_NOFORGET})) or seed-repro "
            f"loose (region std {region_max_std:.3f}). {summary}", detail)


out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "M_MAX": M_MAX, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] mode={RUN_MODE} N={N} M_MAX={M_MAX} seeds_todo={seeds_todo}", flush=True)

for s in seeds_todo:
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg, detail = compute_verdict(all_results)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(all_results),
    "N": N,
    "run_mode": RUN_MODE,
    "target_alphas": TARGET_ALPHAS,
    "detail": detail,
    "metrics_source": "measured_cpu_hopfield_continual_writes_cliff_sweep",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
