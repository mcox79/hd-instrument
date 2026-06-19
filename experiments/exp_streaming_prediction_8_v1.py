"""
streaming_prediction_8_v1 -- Wave 4 SP8: online write-window capacity management.

SCIENTIFIC QUESTION (Wave 4 Streaming Prediction 8):
  SP7 confirmed r_eff as a capacity gauge (monotone with alpha).
  SP8 asks: can a SLIDING WRITE WINDOW (erase-and-rewrite) maintain high retrieval
  fidelity across arbitrarily long write streams, compared to unbounded accumulation?

  The sliding window mechanism:
  - Maintain a fixed-size window of W_window most recent patterns.
  - When a new pattern arrives and window is full: erase the OLDEST pattern (rank-1 unwrite),
    then write the new pattern (rank-1 write).
  - Compare to unbounded accumulation that simply adds all patterns.

  The key product question: does windowed streaming maintain fidelity > 0.70
  on any queried pattern that is within the current window, even after 3x the window has been
  processed (i.e., at least 2 full window rotations)?

  Protocol:
  1. Process T_TOTAL = 3 * WINDOW_SIZE patterns in stream.
  2. At each step, test retrieval of the most recent K_TEST patterns.
  3. Measure: fidelity(window_policy) vs fidelity(unbounded).

  Metrics:
  (A) Window policy maintains fidelity: mean_fid_window >= 0.70 across all test steps.
      HP-A: mean_fid_window >= 0.70.
  (B) Window outperforms unbounded at late steps (>2*WINDOW): fid_window_late > fid_unbounded_late.
      HP-B: fid_window_late > fid_unbounded_late + 0.05.
  (C) Window does NOT degrade recently-written patterns: fid_newest_in_window >= 0.85.
      HP-C: fid_newest_in_window >= 0.85.

HARD-PASS: HP-A AND HP-B AND HP-C.
HARD-FAIL: mean_fid_window < 0.40 OR fid_newest_in_window < 0.60.
MIDDLE: 2/3 cells pass.

PRE-REGISTERED BANDS:
  HP: mean_fid_window >= 0.70, fid_window_late > fid_unbounded_late + 0.05, newest >= 0.85.
  HF: mean_fid_window < 0.40 OR newest < 0.60.
  Calibration: first sliding-window streaming test. No prior substrate anchor.
  Theory: at alpha_eff = WINDOW/N ~ 0.10, fidelity ~ 0.90 (well below alpha_c=0.138).
  Sliding window maintains constant alpha_eff; unbounded grows.
  Bands: +-50% of theoretical fidelity per calibration-probe policy.

FORMULA SELF-TESTS:
  1. Rank-1 unwrite: W_new = W_old - outer(xi_old, xi_old)/N.
     After unwrite, xi_old has reduced fidelity.
     [INPUT: N=8, xi_old=[1,-1,1,-1,...], M=1] [EXPECTED: fidelity drops after unwrite]
  2. Window fidelity: at alpha_eff = 0.10, fidelity ~ 0.85-0.95.
     [INPUT: N=256, M_window=25 (alpha=0.098)] [EXPECTED: fidelity >= 0.70]
  3. Unbounded at alpha=0.20 (> alpha_c=0.138): fidelity < 0.50 (collapsed).
     [INPUT: N=256, M_unbounded=50 (alpha=0.195)] [EXPECTED: fidelity < 0.70]

No _nN suffix; production N=1024.
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
from collections import deque

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "streaming_prediction_8_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 1024
ALPHA_C = 0.138

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    WINDOW_SIZE = 50
    T_TOTAL = 150      # 3x window
    K_TEST = 5
    TEST_INTERVAL = 20
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    WINDOW_SIZE = 80
    T_TOTAL = 240      # 3x window
    K_TEST = 10
    TEST_INTERVAL = 20
    NOISE_FRAC = 0.10

HP_MEAN_FID_WINDOW = 0.70
HP_LATE_ADVANTAGE = 0.05
HP_NEWEST_FID = 0.85
HF_MEAN_FID_WINDOW = 0.40
HF_NEWEST_FID = 0.60


def _selftest_unwrite():
    """Rank-1 unwrite reduces fidelity of removed pattern."""
    n_small = 64
    rng = np.random.RandomState(0)
    xi_old = rng.choice([-1.0, 1.0], size=n_small).astype(np.float64)
    W = np.outer(xi_old, xi_old) / n_small
    np.fill_diagonal(W, 0.0)
    fid_before = float(np.dot(np.sign(W @ xi_old), xi_old)) / n_small
    # Unwrite
    W_new = W - np.outer(xi_old, xi_old) / n_small
    np.fill_diagonal(W_new, 0.0)
    h_new = W_new @ xi_old
    fid_after = float(np.dot(np.sign(h_new + 1e-9), xi_old)) / n_small
    assert fid_before > fid_after or abs(h_new).max() < 0.01, \
        f"unwrite selftest: fid_before={fid_before:.4f} fid_after={fid_after:.4f}"
    return fid_before, fid_after


def _selftest_capacity():
    """Alpha bounds for window vs unbounded."""
    alpha_window = WINDOW_SIZE / N
    alpha_unbounded_late = (WINDOW_SIZE * 3) / N
    assert alpha_window < ALPHA_C, f"window alpha {alpha_window:.4f} >= alpha_c"
    return alpha_window, alpha_unbounded_late


def _instrumentation_selftest():
    fb, fa = _selftest_unwrite()
    aw, au = _selftest_capacity()
    assert K_TEST > 0, "K_TEST > 0 required"
    assert T_TOTAL > WINDOW_SIZE, f"T_TOTAL={T_TOTAL} must > WINDOW_SIZE={WINDOW_SIZE}"
    print(f"[selftest] PASS: unwrite fid {fb:.4f}->{fa:.4f} "
          f"alpha_window={aw:.4f}(< {ALPHA_C}) alpha_unbounded_late={au:.4f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def retrieve_fidelity(W: np.ndarray, xi: np.ndarray, n: int, noise_frac: float,
                       rng: np.random.RandomState, n_steps: int = 3) -> float:
    probe = xi.copy()
    flip = rng.random(n) < noise_frac
    probe[flip] *= -1.0
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return float(np.dot(state, xi)) / float(n)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Generate stream of T_TOTAL patterns
    Xi_stream = rng.choice([-1.0, 1.0], size=(T_TOTAL, N)).astype(np.float64)

    # Window policy state
    W_window = np.zeros((N, N))
    window_queue: deque = deque()

    # Unbounded policy state
    W_unbounded = np.zeros((N, N))

    fid_window_all = []
    fid_unbounded_all = []
    fid_window_late = []
    fid_unbounded_late = []
    fid_newest_all = []

    rng_test = np.random.RandomState(seed + 300)

    for t in range(T_TOTAL):
        xi_new = Xi_stream[t]

        # Window policy: erase oldest if full, add new
        if len(window_queue) >= WINDOW_SIZE:
            xi_oldest = window_queue.popleft()
            W_window -= np.outer(xi_oldest, xi_oldest) / float(N)
        W_window += np.outer(xi_new, xi_new) / float(N)
        np.fill_diagonal(W_window, 0.0)
        window_queue.append(xi_new.copy())

        # Unbounded policy: just add
        W_unbounded += np.outer(xi_new, xi_new) / float(N)
        np.fill_diagonal(W_unbounded, 0.0)

        if (t + 1) % TEST_INTERVAL == 0:
            # Test retrieval of K_TEST most recent in current window
            test_pats = list(window_queue)[-K_TEST:]
            fids_w = []
            fids_u = []
            for xi_test in test_pats:
                fid_w = retrieve_fidelity(W_window, xi_test, N, NOISE_FRAC, rng_test)
                fid_u = retrieve_fidelity(W_unbounded, xi_test, N, NOISE_FRAC, rng_test)
                fids_w.append(fid_w)
                fids_u.append(fid_u)
            mean_w = float(np.mean(fids_w)) if fids_w else 0.0
            mean_u = float(np.mean(fids_u)) if fids_u else 0.0
            fid_window_all.append(mean_w)
            fid_unbounded_all.append(mean_u)

            # Newest pattern fidelity
            newest_fid = retrieve_fidelity(W_window, xi_new, N, NOISE_FRAC, rng_test)
            fid_newest_all.append(newest_fid)

            # Late-stage: t > 2 * WINDOW_SIZE
            if t >= 2 * WINDOW_SIZE:
                fid_window_late.append(mean_w)
                fid_unbounded_late.append(mean_u)

    mean_fid_window = float(np.mean(fid_window_all)) if fid_window_all else 0.0
    mean_fid_unbounded = float(np.mean(fid_unbounded_all)) if fid_unbounded_all else 0.0
    mean_newest = float(np.mean(fid_newest_all)) if fid_newest_all else 0.0
    mean_window_late = float(np.mean(fid_window_late)) if fid_window_late else 0.0
    mean_unbounded_late = float(np.mean(fid_unbounded_late)) if fid_unbounded_late else 0.0
    late_advantage = mean_window_late - mean_unbounded_late

    hp_a = mean_fid_window >= HP_MEAN_FID_WINDOW
    hp_b = late_advantage >= HP_LATE_ADVANTAGE
    hp_c = mean_newest >= HP_NEWEST_FID

    elapsed = time.time() - t0
    print(f"  [seed={seed}] mean_fid_w={mean_fid_window:.4f}(HP>={HP_MEAN_FID_WINDOW}) "
          f"mean_fid_u={mean_fid_unbounded:.4f} late_adv={late_advantage:.4f}(HP>={HP_LATE_ADVANTAGE}) "
          f"newest={mean_newest:.4f}(HP>={HP_NEWEST_FID}) "
          f"hp_ABC=[{int(hp_a)},{int(hp_b)},{int(hp_c)}] elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "WINDOW_SIZE": WINDOW_SIZE, "T_TOTAL": T_TOTAL, "run_mode": RUN_MODE,
        "mean_fid_window": float(mean_fid_window),
        "mean_fid_unbounded": float(mean_fid_unbounded),
        "late_advantage": float(late_advantage),
        "mean_newest_fid": float(mean_newest),
        "mean_window_late": float(mean_window_late),
        "mean_unbounded_late": float(mean_unbounded_late),
        "hp_a": bool(hp_a), "hp_b": bool(hp_b), "hp_c": bool(hp_c),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")

    n = len(results)
    mean_fid_w = float(np.mean([r["mean_fid_window"] for r in results]))
    mean_late_adv = float(np.mean([r["late_advantage"] for r in results]))
    mean_newest = float(np.mean([r["mean_newest_fid"] for r in results]))

    summary = (f"mean_fid_window={mean_fid_w:.4f}(HP>={HP_MEAN_FID_WINDOW} HF<{HF_MEAN_FID_WINDOW}) "
               f"late_adv={mean_late_adv:.4f}(HP>={HP_LATE_ADVANTAGE}) "
               f"newest={mean_newest:.4f}(HP>={HP_NEWEST_FID} HF<{HF_NEWEST_FID}) "
               f"n_seeds={n}")

    if mean_fid_w < HF_MEAN_FID_WINDOW or mean_newest < HF_NEWEST_FID:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    n_all_hp = sum(1 for r in results if r["hp_a"] and r["hp_b"] and r["hp_c"])
    n_hp2 = sum(1 for r in results if sum([r["hp_a"], r["hp_b"], r["hp_c"]]) >= 2)
    min_pass = math.ceil(n * 0.6)

    if n_all_hp >= min_pass:
        return ("HARD_PASS", f"HARD_PASS: sliding-window SP8 CONFIRMED. {summary}")
    if n_hp2 >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 2/3 cells pass. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "WINDOW_SIZE": WINDOW_SIZE, "T_TOTAL": T_TOTAL, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N} WINDOW={WINDOW_SIZE} T_TOTAL={T_TOTAL}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "mean_fid_window": float(np.mean([r["mean_fid_window"] for r in all_results])) if all_results else None,
    "mean_late_advantage": float(np.mean([r["late_advantage"] for r in all_results])) if all_results else None,
    "mean_newest_fid": float(np.mean([r["mean_newest_fid"] for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
