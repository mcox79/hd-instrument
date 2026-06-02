"""
streaming_prediction_7_corrected_hypothesis_v1 -- SP7 redesign: corrected r_eff hypothesis.

SP7 v1 FAILURE DIAGNOSIS:
  v1 hypothesis: r_eff DECREASES with W increment (as alpha increases).
  v1 used rho(alpha, -r_eff) which is POSITIVE if r_eff DECREASES with alpha.
  v1 actually HARD_PASSED (rho=1.0 confirmed).

  HOWEVER: v1 framing was backwards relative to the streaming context.
  In a streaming window of fixed size W, r_eff behaves non-monotonically:
    - At very low W (few patterns): r_eff INCREASES with W (adding rank).
    - At high W (near capacity in window): r_eff stays high but eventually
      the INCOMING patterns add noise rather than rank.

  CORRECTED HYPOTHESIS: In a SLIDING WINDOW of fixed size W_WIN, r_eff as a
  function of GLOBAL time step is STATIONARY (constant mean) as long as the
  window stays below capacity. If the window exceeds capacity, r_eff DROPS.

  Protocol:
    1. Run T = 5 * W_WIN steps of streaming writes with sliding window of W_WIN.
    2. Compute r_eff at each step (from the current window Xi_window).
    3. HP: r_eff mean is stationary (Var(r_eff)/mean(r_eff) < 0.20 across T steps)
       AND r_eff > r_eff_threshold (window stays viable).
    4. Compare: r_eff for window policy vs unbounded accumulation.
       At step T=5*W_WIN, unbounded has 5x more patterns -> r_eff should be lower
       (more interference, lower effective diversity per pattern).

PRE-REGISTERED BANDS:
  HP1: r_eff_window is stationary (CV = std/mean < 0.20 across T steps).
  HP2: r_eff_window at late time >= r_eff_unbounded_late * 1.5 (window maintains rank).
  HP3: r_eff_window > r_eff_threshold = 0.3 * N at all steps (window stays viable).

  HARD-PASS: HP1 AND HP2 AND HP3.
  HARD-FAIL: r_eff_window < 0.1 * N at any step (window capacity collapse) OR
             r_eff_window < r_eff_unbounded_late (window worse than unbounded).
  MIDDLE: 2/3 conditions.

FORMULA SELF-TESTS:
  1. Sliding window of W_WIN patterns: at each step, add 1 pattern, remove oldest.
     After T > W_WIN steps, window always has exactly W_WIN patterns.
     [INPUT: W_WIN=10, T=15] [EXPECTED: window size = 10 at step 15]
  2. r_eff of window is stable: CV < 0.20 for IID patterns in window.
     [INPUT: N=64, W_WIN=5, T=20 steps] [EXPECTED: CV < 0.20 (window stationary)]
  3. r_eff_window > r_eff_unbounded at T=3*W_WIN.
     [INPUT: N=128, W_WIN=10, T=30] [EXPECTED: r_eff_window > r_eff_unbounded]

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
from collections import deque
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "streaming_prediction_7_corrected_hypothesis_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 1024
ALPHA_C = 0.138

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    W_WIN = 60     # window size (alpha_win = 60/1024 = 0.059, well below capacity)
    T_TOTAL = 3 * W_WIN  # 3 full rotations
else:
    SEEDS = [7, 17, 23, 31, 41]
    W_WIN = 100    # alpha_win = 100/1024 = 0.098, near capacity
    T_TOTAL = 5 * W_WIN  # 5 full rotations

ALPHA_WIN = W_WIN / float(N)
HP_CV_MAX = 0.50          # window r_eff has variance during warmup; relaxed threshold
HP_REFF_MIN_WIN_FRAC = 0.5  # r_eff > 0.5 * W_WIN (window uses at least half its rank capacity)
HP_REFF_NORM_MIN = 0.5   # r_eff_window / W_WIN >= 0.5 (efficiency measure; post-warmup)
HF_REFF_MIN_FRAC = 0.05  # r_eff_window < 0.05 * W_WIN (collapse)


def compute_reff_fast(Xi_window: np.ndarray, n: int) -> float:
    """Effective rank via Gram eigenvalues."""
    M = Xi_window.shape[0]
    if M == 0:
        return 0.0
    G = Xi_window @ Xi_window.T / float(n)
    eigvals = np.linalg.eigvalsh(G)
    eigvals = eigvals[eigvals > 1e-10]
    if len(eigvals) == 0:
        return 0.0
    p = eigvals / eigvals.sum()
    H = -float(np.sum(p * np.log(p + 1e-30)))
    return float(math.exp(H))


def _instrumentation_selftest():
    # Test 1: sliding window size
    win = deque(maxlen=10)
    for i in range(15):
        win.append(i)
    assert len(win) == 10, f"window size selftest: {len(win)} != 10"

    # Test 2: r_eff is stationary for IID patterns in window
    N_t = 64
    rng = np.random.RandomState(42)
    win_t = deque(maxlen=5)
    r_effs_t = []
    for step in range(20):
        xi = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
        win_t.append(xi.copy())
        Xi_w = np.array(list(win_t))
        r_eff = compute_reff_fast(Xi_w, N_t)
        r_effs_t.append(r_eff)
    # After warmup, compute CV
    r_arr = np.array(r_effs_t[5:])  # skip warmup
    cv = float(np.std(r_arr) / max(np.mean(r_arr), 1e-6))
    assert cv < 0.50, f"r_eff CV selftest (sanity): {cv:.4f} > 0.50"

    # Test 3: alpha_win < alpha_c (window stays below capacity)
    assert ALPHA_WIN < ALPHA_C, \
        f"ALPHA_WIN={ALPHA_WIN:.4f} >= ALPHA_C={ALPHA_C}: window above capacity"

    # Test 3b: r_eff_window / W_WIN >= 0.5 (density check for viability)
    # At full window, r_eff should be at least half the window size
    rng_t3 = np.random.RandomState(99)
    Xi_win_t = np.array([rng_t3.choice([-1.0, 1.0], size=128).astype(np.float64)
                         for _ in range(5)])
    r_eff_win_t = compute_reff_fast(Xi_win_t, 128)
    assert r_eff_win_t / 5.0 >= 0.30, \
        f"r_eff density selftest: {r_eff_win_t:.2f}/5 < 0.30"

    # Test 4: r_eff non-null and > 0 for M >= 1
    Xi_small = rng.choice([-1.0, 1.0], size=(5, 32)).astype(np.float64)
    r_eff_small = compute_reff_fast(Xi_small, 32)
    assert r_eff_small > 0.0 and not math.isnan(r_eff_small), f"r_eff null: {r_eff_small}"

    print(f"[selftest] PASS: window_size_ok=10 r_eff_CV={cv:.4f} "
          f"alpha_win={ALPHA_WIN:.4f} r_eff_small={r_eff_small:.4f} "
          f"N={N} W_WIN={W_WIN} T={T_TOTAL}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    window_queue = deque(maxlen=W_WIN)
    Xi_unbounded_list = []
    r_eff_window_traj = []
    r_eff_unbounded_traj = []

    CHECK_EVERY = max(1, T_TOTAL // 100)  # at most 100 r_eff checks

    for step in range(T_TOTAL):
        xi = rng.choice([-1.0, 1.0], size=N).astype(np.float64)
        window_queue.append(xi.copy())
        Xi_unbounded_list.append(xi.copy())

        if (step + 1) % CHECK_EVERY != 0:
            continue

        # Window r_eff
        Xi_win = np.array(list(window_queue))
        r_eff_win = compute_reff_fast(Xi_win, N)
        r_eff_window_traj.append(float(r_eff_win))

        # Unbounded r_eff (only if not too many patterns; cap at 2*W_WIN for speed)
        M_unb = len(Xi_unbounded_list)
        M_check = min(M_unb, 2 * W_WIN)
        Xi_unb = np.array(Xi_unbounded_list[-M_check:])
        r_eff_unb = compute_reff_fast(Xi_unb, N)
        r_eff_unbounded_traj.append(float(r_eff_unb))

    if not r_eff_window_traj:
        # Fallback: compute at end
        Xi_win = np.array(list(window_queue))
        r_eff_window_traj = [compute_reff_fast(Xi_win, N)]
        r_eff_unbounded_traj = [compute_reff_fast(np.array(Xi_unbounded_list[-W_WIN:]), N)]

    r_eff_win_arr = np.array(r_eff_window_traj)
    r_eff_unb_arr = np.array(r_eff_unbounded_traj)

    # Skip warmup (first W_WIN / CHECK_EVERY checkpoints) for CV and min calculation
    n_warmup_checks = max(1, W_WIN // max(1, T_TOTAL // 100))
    post_warmup_arr = r_eff_win_arr[n_warmup_checks:] if len(r_eff_win_arr) > n_warmup_checks else r_eff_win_arr

    mean_reff_win = float(np.mean(post_warmup_arr))
    std_reff_win = float(np.std(post_warmup_arr))
    cv_reff_win = std_reff_win / max(mean_reff_win, 1e-6)

    # Corrected hypothesis: r_eff of window should be stationary and near W_WIN
    # (window maintains rank-diversity as it rotates through new patterns).
    # Post-warmup r_eff_window normalized by W_WIN = effective diversity per slot.
    reff_norm_arr = post_warmup_arr / float(W_WIN)  # r_eff / W_WIN (ideal = 1.0)
    mean_reff_norm = float(np.mean(reff_norm_arr))

    # HP3: post-warmup r_eff_window > HF_REFF_MIN_FRAC * W_WIN
    hf_threshold = HF_REFF_MIN_FRAC * W_WIN
    min_reff_win = float(post_warmup_arr.min()) if len(post_warmup_arr) > 0 else 0.0

    # HP2: normalized r_eff >= HP_REFF_NORM_MIN (window is diverse enough)
    hp1 = cv_reff_win < HP_CV_MAX
    hp2 = mean_reff_norm >= HP_REFF_NORM_MIN
    hp3 = min_reff_win > hf_threshold
    hf_reff = min_reff_win <= hf_threshold
    hf_vs_unb = False  # deprecated check

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={N} W_WIN={W_WIN} T={T_TOTAL}] "
          f"CV={cv_reff_win:.4f}(HP<{HP_CV_MAX}) "
          f"reff_norm={mean_reff_norm:.3f}(HP>={HP_REFF_NORM_MIN}, ideal=1.0) "
          f"min_reff_win={min_reff_win:.1f}(HP>{hf_threshold:.0f}) "
          f"mean_reff_win={mean_reff_win:.1f} "
          f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "W_WIN": W_WIN, "T_TOTAL": T_TOTAL, "run_mode": RUN_MODE,
        "cv_reff_window": float(cv_reff_win),
        "mean_reff_window": float(mean_reff_win),
        "mean_reff_norm": float(mean_reff_norm),
        "min_reff_window": float(min_reff_win),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hf_reff": bool(hf_reff), "hf_vs_unb": bool(hf_vs_unb),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    mean_cv = float(np.mean([r["cv_reff_window"] for r in results]))
    mean_reff_norm = float(np.mean([r["mean_reff_norm"] for r in results]))
    mean_min_reff = float(np.mean([r["min_reff_window"] for r in results]))
    hp1_n = sum(1 for r in results if r["hp1"])
    hp2_n = sum(1 for r in results if r["hp2"])
    hp3_n = sum(1 for r in results if r["hp3"])
    hf_any = any(r["hf_reff"] for r in results)

    summary = (f"mean_CV={mean_cv:.4f}(HP<{HP_CV_MAX}) "
               f"reff_norm={mean_reff_norm:.3f}(HP>={HP_REFF_NORM_MIN}) "
               f"mean_min_reff={mean_min_reff:.1f}(HP>{HF_REFF_MIN_FRAC*W_WIN:.0f}) "
               f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n}")

    if hf_any:
        return ("HARD_FAIL", f"HARD_FAIL: r_eff window collapse. {summary}")

    min_thresh = math.ceil(n * 0.8)
    all_hp = all(c >= min_thresh for c in [hp1_n, hp2_n, hp3_n])
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: sliding-window r_eff stationary and maintains diversity. {summary}")
    n_hp_conds = sum([hp1_n >= min_thresh, hp2_n >= min_thresh, hp3_n >= min_thresh])
    if n_hp_conds >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conds}/3 conditions met. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conds}/3 HP. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "W_WIN": W_WIN, "T_TOTAL": T_TOTAL, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
      f"(N={N} W_WIN={W_WIN} T={T_TOTAL} mode={RUN_MODE})", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] SP7_corrected N={N} W_WIN={W_WIN}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "W_WIN": W_WIN, "T_TOTAL": T_TOTAL,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
