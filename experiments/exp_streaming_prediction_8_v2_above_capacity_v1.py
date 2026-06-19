"""
streaming_prediction_8_v2_above_capacity_v1 -- SP8 v2: above-capacity sliding window.

REDESIGN (v1 -> v2):
  v1 tested window policy at alpha_eff = WINDOW/N ~ 0.078 (below capacity).
  Smoke showed HARD_FAIL: below-capacity regime means both window and unbounded
  policies work fine, so there's no discriminating signal.

  v2 redesign: probe the ABOVE-CAPACITY regime where unbounded accumulation FAILS
  but windowed streaming SHOULD maintain fidelity by evicting old patterns.

  Specifically:
  - T_TOTAL = 5 * WINDOW_SIZE patterns (5 full rotations)
  - WINDOW_SIZE = 120 (alpha_eff = 120/1024 = 0.117, within capacity)
  - Unbounded accumulation reaches alpha=0.585 at T=5*WINDOW (far above alpha_c=0.138)
  - The window policy should maintain alpha_eff = 0.117 (within capacity)

  EXPECTED BEHAVIOR:
  - Window policy: constant alpha_eff -> constant fidelity ~ 0.90 throughout
  - Unbounded: alpha grows -> fidelity collapses after ~1x window (alpha > alpha_c)
  - Discrimination signal: late window fidelity > late unbounded fidelity + 0.20

PRE-REGISTERED HARD-PASS:
  HP-A: mean_fid_window >= 0.70 across all test steps (window maintains capacity)
  HP-B: fid_window_late > fid_unbounded_late + 0.20 (window discriminates vs unbounded)
  HP-C: fid_newest_in_window >= 0.80 (most recent patterns still retrievable)

PRE-REGISTERED HARD-FAIL:
  HF-A: mean_fid_window < 0.40 (window policy fails)
  HF-B: fid_window_late <= fid_unbounded_late (no discrimination)
  HF-C: fid_newest_in_window < 0.50 (window corrupts recent writes)

MIDDLE BAND: 2/3 cells pass

P_deflated: 0.70 (v1 confirmed the mechanism works; v2 probes a stronger regime
  where theory clearly predicts discrimination; Hopfield capacity theorem applies)

FORMULA SELF-TESTS:
  1. Rank-1 unwrite: W_new = W_old - outer(xi_old, xi_old)/N.
     After unwrite, xi_old retrieval should fail.
     [INPUT: N=64, xi=[1,-1,...], M=1] [EXPECTED: fidelity drops after unwrite]
  2. Window alpha_eff constant: WINDOW_SIZE/N = 0.117 < alpha_c=0.138.
     [INPUT: N=1024, WINDOW=120] [EXPECTED: alpha_eff=0.117 < 0.138]
  3. Unbounded alpha at step T=5*WINDOW: T/N = 600/1024 > alpha_c.
     [INPUT: T=5*120=600, N=1024] [EXPECTED: alpha_unbounded=0.586 > alpha_c]

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
from collections import deque

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "streaming_prediction_8_v2_above_capacity_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 1024
ALPHA_C = 0.138

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    WINDOW_SIZE = 60    # alpha_eff = 0.059 (smoke)
    T_TOTAL = 300       # 5x window
    K_TEST = 5
    TEST_INTERVAL = 30
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    WINDOW_SIZE = 120   # alpha_eff = 0.117 (within capacity)
    T_TOTAL = 600       # 5x window; alpha_unbounded = 0.586 >> alpha_c
    K_TEST = 10
    TEST_INTERVAL = 30
    NOISE_FRAC = 0.10

HP_MEAN_FID_WINDOW = 0.70
HP_LATE_ADVANTAGE = 0.20
HP_NEWEST_FID = 0.80
HF_MEAN_FID_WINDOW = 0.40
HF_LATE_ADVANTAGE = 0.0   # window must be STRICTLY better than unbounded
HF_NEWEST_FID = 0.50


def _selftest_unwrite():
    n_s = 128
    rng = np.random.RandomState(0)
    xi_old = rng.choice([-1.0, 1.0], size=n_s).astype(np.float64)
    W = np.outer(xi_old, xi_old) / n_s
    np.fill_diagonal(W, 0.0)
    fid_before = float(np.dot(np.sign(W @ xi_old + 1e-9), xi_old)) / n_s
    W_new = W - np.outer(xi_old, xi_old) / n_s
    np.fill_diagonal(W_new, 0.0)
    h = W_new @ xi_old
    fid_after = float(np.dot(np.sign(h + 1e-9), xi_old)) / n_s
    assert fid_before > fid_after or abs(h).max() < 0.01, \
        f"unwrite selftest: fid {fid_before:.3f} -> {fid_after:.3f}"
    return fid_before, fid_after


def _selftest_capacity():
    alpha_window = WINDOW_SIZE / N
    alpha_unbounded_late = T_TOTAL / N
    assert alpha_window < ALPHA_C, f"window alpha {alpha_window:.4f} >= alpha_c={ALPHA_C}"
    assert alpha_unbounded_late > ALPHA_C, \
        f"unbounded alpha {alpha_unbounded_late:.4f} NOT > alpha_c (v2 needs above-capacity)"
    return alpha_window, alpha_unbounded_late


def _instrumentation_selftest():
    fb, fa = _selftest_unwrite()
    aw, au = _selftest_capacity()
    assert K_TEST > 0, "K_TEST > 0"
    assert T_TOTAL > WINDOW_SIZE * 3, "T_TOTAL must be >= 3*WINDOW for late-step testing"
    print(
        f"[selftest] PASS: unwrite fid {fb:.3f}->{fa:.3f} "
        f"alpha_window={aw:.4f}(<alpha_c={ALPHA_C}) alpha_unbounded_late={au:.4f}(>alpha_c)",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def retrieve_fidelity(W: np.ndarray, xi: np.ndarray, noise_frac: float,
                       rng: np.random.RandomState, n_steps: int = 5) -> float:
    probe = xi.copy()
    flip = rng.random(N) < noise_frac
    probe[flip] *= -1.0
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return float(np.dot(state, xi)) / float(N)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    Xi_stream = rng.choice([-1.0, 1.0], size=(T_TOTAL, N)).astype(np.float64)

    W_window = np.zeros((N, N), dtype=np.float64)
    window_queue: deque = deque()
    W_unbounded = np.zeros((N, N), dtype=np.float64)

    fid_window_all = []
    fid_unbounded_all = []
    fid_window_late = []
    fid_unbounded_late = []
    fid_newest_all = []

    rng_test = np.random.RandomState(seed + 300)

    # Late regime starts at T_TOTAL // 2
    late_start = T_TOTAL // 2

    for t in range(T_TOTAL):
        xi_new = Xi_stream[t]

        # Window policy
        if len(window_queue) >= WINDOW_SIZE:
            xi_oldest = window_queue.popleft()
            W_window -= np.outer(xi_oldest, xi_oldest) / float(N)
        W_window += np.outer(xi_new, xi_new) / float(N)
        np.fill_diagonal(W_window, 0.0)
        window_queue.append(xi_new.copy())

        # Unbounded policy
        W_unbounded += np.outer(xi_new, xi_new) / float(N)
        np.fill_diagonal(W_unbounded, 0.0)

        if (t + 1) % TEST_INTERVAL == 0:
            recent_items = list(window_queue)[-K_TEST:]
            # Window fidelity
            fids_w = []
            for xi in recent_items:
                fids_w.append(retrieve_fidelity(W_window, xi, NOISE_FRAC, rng_test))
            mean_fid_w = float(np.mean(fids_w)) if fids_w else 0.0

            # Unbounded fidelity (query same patterns)
            fids_u = []
            for xi in recent_items:
                fids_u.append(retrieve_fidelity(W_unbounded, xi, NOISE_FRAC, rng_test))
            mean_fid_u = float(np.mean(fids_u)) if fids_u else 0.0

            # Newest fidelity (just written)
            newest_fid = retrieve_fidelity(W_window, xi_new, NOISE_FRAC, rng_test)

            fid_window_all.append(mean_fid_w)
            fid_unbounded_all.append(mean_fid_u)
            fid_newest_all.append(newest_fid)

            if t >= late_start:
                fid_window_late.append(mean_fid_w)
                fid_unbounded_late.append(mean_fid_u)

    mean_fid_window = float(np.mean(fid_window_all)) if fid_window_all else 0.0
    mean_fid_newest = float(np.mean(fid_newest_all)) if fid_newest_all else 0.0
    mean_fid_late_w = float(np.mean(fid_window_late)) if fid_window_late else 0.0
    mean_fid_late_u = float(np.mean(fid_unbounded_late)) if fid_unbounded_late else 0.0
    late_advantage = mean_fid_late_w - mean_fid_late_u

    hpa = mean_fid_window >= HP_MEAN_FID_WINDOW
    hpb = late_advantage > HP_LATE_ADVANTAGE
    hpc = mean_fid_newest >= HP_NEWEST_FID

    hfa = mean_fid_window < HF_MEAN_FID_WINDOW
    hfb = late_advantage <= HF_LATE_ADVANTAGE
    hfc = mean_fid_newest < HF_NEWEST_FID

    elapsed = time.time() - t0
    print(
        f"  [seed={seed} N={N} W={WINDOW_SIZE} T={T_TOTAL}] "
        f"mean_fid_w={mean_fid_window:.4f}(HP>={HP_MEAN_FID_WINDOW}) "
        f"late_w={mean_fid_late_w:.4f} late_u={mean_fid_late_u:.4f} "
        f"late_adv={late_advantage:+.4f}(HP>{HP_LATE_ADVANTAGE}) "
        f"newest={mean_fid_newest:.4f}(HP>={HP_NEWEST_FID}) "
        f"hp=[{int(hpa)},{int(hpb)},{int(hpc)}] elapsed={elapsed:.2f}s",
        flush=True,
    )

    return {
        "seed": seed, "N": N, "WINDOW_SIZE": WINDOW_SIZE, "T_TOTAL": T_TOTAL,
        "run_mode": RUN_MODE,
        "mean_fid_window": float(mean_fid_window),
        "mean_fid_newest": float(mean_fid_newest),
        "mean_fid_late_w": float(mean_fid_late_w),
        "mean_fid_late_u": float(mean_fid_late_u),
        "late_advantage": float(late_advantage),
        "hpa": bool(hpa), "hpb": bool(hpb), "hpc": bool(hpc),
        "hfa": bool(hfa), "hfb": bool(hfb), "hfc": bool(hfc),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    mean_fid = float(np.mean([r["mean_fid_window"] for r in results]))
    mean_adv = float(np.mean([r["late_advantage"] for r in results]))
    mean_new = float(np.mean([r["mean_fid_newest"] for r in results]))
    mean_late_u = float(np.mean([r["mean_fid_late_u"] for r in results]))
    mean_late_w = float(np.mean([r["mean_fid_late_w"] for r in results]))

    hpa_n = sum(1 for r in results if r["hpa"])
    hpb_n = sum(1 for r in results if r["hpb"])
    hpc_n = sum(1 for r in results if r["hpc"])
    hfa_any = any(r["hfa"] for r in results)
    hfb_any = any(r["hfb"] for r in results)
    hfc_any = any(r["hfc"] for r in results)

    summary = (
        f"n_seeds={n} mean_fid_w={mean_fid:.4f}(HP>={HP_MEAN_FID_WINDOW}) "
        f"late_w={mean_late_w:.4f} late_u={mean_late_u:.4f} "
        f"late_adv={mean_adv:+.4f}(HP>{HP_LATE_ADVANTAGE}) "
        f"newest={mean_new:.4f}(HP>={HP_NEWEST_FID}) "
        f"hpa={hpa_n}/{n} hpb={hpb_n}/{n} hpc={hpc_n}/{n}"
    )

    if hfa_any:
        return ("HARD_FAIL", f"HARD_FAIL HF-A: window fidelity collapsed. {summary}")
    if hfb_any:
        return ("HARD_FAIL", f"HARD_FAIL HF-B: window does not outperform unbounded. {summary}")
    if hfc_any:
        return ("HARD_FAIL", f"HARD_FAIL HF-C: window corrupts recent writes. {summary}")

    min_threshold = math.ceil(n * 0.8)
    all_hp = all(cnt >= min_threshold for cnt in [hpa_n, hpb_n, hpc_n])
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP conditions met in >={min_threshold}/{n} seeds. {summary}")

    n_hp_conds = sum([hpa_n >= min_threshold, hpb_n >= min_threshold, hpc_n >= min_threshold])
    if n_hp_conds >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conds}/3 HP conditions met. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conds}/3 HP conditions met. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "WINDOW_SIZE": WINDOW_SIZE, "T_TOTAL": T_TOTAL, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
    f"(N={N} W={WINDOW_SIZE} T={T_TOTAL} mode={RUN_MODE})",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] SP8_v2_above_capacity N={N} W={WINDOW_SIZE} T={T_TOTAL}...", flush=True)
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
    "N": N, "WINDOW_SIZE": WINDOW_SIZE, "T_TOTAL": T_TOTAL,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
    "per_seed": [
        {
            "seed": r.get("seed"),
            "mean_fid_window": r.get("mean_fid_window"),
            "late_advantage": r.get("late_advantage"),
            "mean_fid_newest": r.get("mean_fid_newest"),
            "mean_fid_late_w": r.get("mean_fid_late_w"),
            "mean_fid_late_u": r.get("mean_fid_late_u"),
            "hpa": r.get("hpa"), "hpb": r.get("hpb"), "hpc": r.get("hpc"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
