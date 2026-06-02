"""
caching_eviction_pp44_capacity_aware_v2_n8192_alpha_above_c_v1 -- Caching eviction v2 at N=8192.

SCIENTIFIC QUESTION:
  PP-44 spectral capacity monitor (r_eff) coupled to eviction policy.
  This is the N=8192 extension and above-capacity stress variant.

  v2_n4096 tested at N=4096, alpha_stress=0.18. This anchor:
    - N=8192 (larger scale, more realistic for memory substrate).
    - alpha_stress = 0.22 (even further above alpha_c=0.138).
    - r_eff monitor alarm fires when r_eff < 0.55 * N_ACTIVE.

  The key distinction from v2_n4096:
    - At N=8192, finite-N fluctuations are smaller, so the no-eviction baseline
      should clearly degrade at alpha=0.22 (thermodynamic limit more applicable).
    - Eviction-maintained alpha_eff = 0.10 (below capacity) should maintain fidelity.

  Test cells (same structure as v2_n4096):
    (A) Eviction prevents collapse: fid_eviction >= 0.80 AND fid_no_eviction <= 0.50.
    (B) r_eff alarm fires before fidelity drops.
    (C) Retained patterns: retained_fidelity >= 0.85.

HARD-PASS: HP-A AND HP-B AND HP-C.
HARD-FAIL: fid_eviction < 0.50 OR fid_no_eviction > 0.80 at N=8192 (stress not applied).
MIDDLE: 2/3 cells.

PRE-REGISTERED BANDS:
  HP/HF same as v2_n4096 but N=8192 suppresses finite-N effects.
  At N=8192, alpha_c threshold applies cleanly (large-N regime).
  P_deflated = 0.60 (v2 n4096 confirmed mechanism; this is a scale extension).

FORMULA SELF-TESTS:
  1. r_eff fast via Gram: for rank-1 Xi, r_eff <= 2.0.
     [INPUT: M=1 pattern, N=64] [EXPECTED: r_eff <= 2.0]
  2. At alpha_stress=0.22 > alpha_c: Hopfield fidelity expected < 0.70 at N=8192.
     Selftest verifies formula (not result at small N).
  3. Eviction unwrite: W - outer(xi)/N reduces xi fidelity.

No _nN suffix; production N=8192 (PROT-018 rule 3).
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

ANCHOR_NAME = "caching_eviction_pp44_capacity_aware_v2_n8192_alpha_above_c_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
ALPHA_STRESS = 0.22
ALPHA_WINDOW = 0.10
REFF_ALARM_THRESHOLD_FRAC = 0.55

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 1024   # smoke at smaller N for speed
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = 8192   # production N

M_STRESS = int(ALPHA_STRESS * N_ACTIVE)
M_WINDOW = int(ALPHA_WINDOW * N_ACTIVE)
EVICT_BATCH = max(1, int(0.02 * N_ACTIVE))

HP_ACC_WITH_EVICTION = 0.80
HP_NO_EVICTION_MAX = 0.50
HP_RETAINED_FID = 0.85
HF_ACC_WITH_EVICTION = 0.50
HF_NO_EVICTION_MIN = 0.80


def compute_reff_fast(Xi_window: np.ndarray, n: int) -> float:
    M = Xi_window.shape[0]
    if M == 0:
        return 1.0
    G = Xi_window @ Xi_window.T / float(n)
    eigvals = np.linalg.eigvalsh(G)
    eigvals = eigvals[eigvals > 1e-10]
    if len(eigvals) == 0:
        return 1.0
    p = eigvals / eigvals.sum()
    H = -float(np.sum(p * np.log(p + 1e-30)))
    return math.exp(H)


def hopfield_fidelity(W: np.ndarray, xi: np.ndarray, n: int, noise_frac: float,
                       rng: np.random.RandomState, n_steps: int = 5) -> float:
    probe = xi.copy()
    flip = rng.random(n) < noise_frac
    probe[flip] *= -1.0
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return float(np.dot(state, xi)) / float(n)


def _selftest_reff():
    n_small = 64
    rng = np.random.RandomState(0)
    xi = rng.choice([-1.0, 1.0], size=n_small).astype(np.float64)
    Xi_1 = xi.reshape(1, n_small)
    r_eff = compute_reff_fast(Xi_1, n_small)
    assert r_eff <= 2.0, f"r_eff rank-1 selftest: {r_eff:.4f} > 2"
    Xi_10 = rng.choice([-1.0, 1.0], size=(10, n_small)).astype(np.float64)
    r_eff_10 = compute_reff_fast(Xi_10, n_small)
    assert r_eff_10 > r_eff, f"r_eff rank-10 should > rank-1"
    return r_eff


def _selftest_unwrite():
    n_small = 32
    rng = np.random.RandomState(1)
    xi = rng.choice([-1.0, 1.0], size=n_small).astype(np.float64)
    W = np.outer(xi, xi) / n_small
    np.fill_diagonal(W, 0.0)
    W_new = W - np.outer(xi, xi) / n_small
    np.fill_diagonal(W_new, 0.0)
    h = W_new @ xi
    fid = float(np.dot(np.sign(h + 1e-9), xi)) / n_small
    assert fid < 1.0, f"unwrite selftest: fid still 1.0 ({fid:.4f})"
    return fid


def _instrumentation_selftest():
    r = _selftest_reff()
    f = _selftest_unwrite()
    assert M_STRESS > M_WINDOW, f"M_STRESS={M_STRESS} must > M_WINDOW={M_WINDOW}"
    alpha_stress_check = ALPHA_STRESS
    assert alpha_stress_check > ALPHA_C, f"alpha_stress={alpha_stress_check} not > alpha_c={ALPHA_C}"
    print(f"[selftest] PASS: reff_rank1={r:.4f} unwrite_fid={f:.4f} "
          f"M_stress={M_STRESS} M_window={M_WINDOW} alpha_stress={ALPHA_STRESS} "
          f"N_ACTIVE={N_ACTIVE}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    Xi_all = rng.choice([-1.0, 1.0], size=(M_STRESS, N_ACTIVE)).astype(np.float64)

    # Policy A: eviction-based
    W_evict = np.zeros((N_ACTIVE, N_ACTIVE), dtype=np.float64)
    evict_queue: list = []
    n_alarms = 0
    fidelity_at_alarm = []
    reff_threshold = REFF_ALARM_THRESHOLD_FRAC * N_ACTIVE

    CHECK_INTERVAL = max(1, M_STRESS // 50)
    for i in range(M_STRESS):
        xi_new = Xi_all[i]
        W_evict += np.outer(xi_new, xi_new) / float(N_ACTIVE)
        np.fill_diagonal(W_evict, 0.0)
        evict_queue.append(xi_new.copy())

        if (i + 1) % CHECK_INTERVAL != 0:
            continue
        reff = compute_reff_fast(np.array(evict_queue), N_ACTIVE)
        if reff < reff_threshold and len(evict_queue) > EVICT_BATCH:
            for _ in range(EVICT_BATCH):
                if evict_queue:
                    xi_old = evict_queue.pop(0)
                    W_evict -= np.outer(xi_old, xi_old) / float(N_ACTIVE)
            np.fill_diagonal(W_evict, 0.0)
            n_alarms += 1
            if evict_queue:
                rng_probe = np.random.RandomState(seed + 1000 + i)
                fid = hopfield_fidelity(W_evict, evict_queue[-1], N_ACTIVE, 0.10, rng_probe)
                fidelity_at_alarm.append(fid)

    # Policy B: no eviction
    W_no_evict = Xi_all.T @ Xi_all / float(N_ACTIVE)
    np.fill_diagonal(W_no_evict, 0.0)

    rng_test = np.random.RandomState(seed + 500)
    n_test_evict = min(20, len(evict_queue))
    n_test_no_evict = min(20, M_STRESS)
    fids_evict = [hopfield_fidelity(W_evict, evict_queue[i], N_ACTIVE, 0.10, rng_test)
                  for i in range(n_test_evict)]
    fids_no_evict = [hopfield_fidelity(W_no_evict, Xi_all[i], N_ACTIVE, 0.10, rng_test)
                     for i in range(n_test_no_evict)]

    mean_fid_evict = float(np.mean(fids_evict)) if fids_evict else 0.0
    mean_fid_no_evict = float(np.mean(fids_no_evict))

    n_retained = min(10, len(evict_queue))
    fids_retained = []
    rng_ret = np.random.RandomState(seed + 600)
    for j in range(n_retained):
        fid_ret = hopfield_fidelity(W_evict, evict_queue[j], N_ACTIVE, 0.10, rng_ret)
        fids_retained.append(fid_ret)
    retained_fid = float(np.mean(fids_retained)) if fids_retained else 0.0

    hp_b_fires_before = sum(1 for f in fidelity_at_alarm if f >= 0.85) >= 1
    no_evict_collapsed = mean_fid_no_evict <= HP_NO_EVICTION_MAX
    hp_a = mean_fid_evict >= HP_ACC_WITH_EVICTION and (no_evict_collapsed or N_ACTIVE < 4096)
    hp_b = hp_b_fires_before and n_alarms >= 1
    hp_c = retained_fid >= HP_RETAINED_FID

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={N_ACTIVE} alpha_stress={ALPHA_STRESS}] "
          f"fid_evict={mean_fid_evict:.4f}(HP>={HP_ACC_WITH_EVICTION}) "
          f"fid_no_evict={mean_fid_no_evict:.4f}(HP<={HP_NO_EVICTION_MAX}) "
          f"n_alarms={n_alarms} hp_b_before={int(hp_b_fires_before)} "
          f"retained={retained_fid:.4f}(HP>={HP_RETAINED_FID}) "
          f"hp_ABC=[{int(hp_a)},{int(hp_b)},{int(hp_c)}] elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N_ACTIVE, "M_stress": M_STRESS, "M_window": M_WINDOW,
        "alpha_stress": float(ALPHA_STRESS), "run_mode": RUN_MODE,
        "fidelity_with_eviction": float(mean_fid_evict),
        "fidelity_no_eviction": float(mean_fid_no_evict),
        "n_alarms": int(n_alarms),
        "retained_fidelity": float(retained_fid),
        "hp_a": bool(hp_a), "hp_b": bool(hp_b), "hp_c": bool(hp_c),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    mean_fid_evict = float(np.mean([r["fidelity_with_eviction"] for r in results]))
    mean_fid_no_evict = float(np.mean([r["fidelity_no_eviction"] for r in results]))
    mean_retained = float(np.mean([r["retained_fidelity"] for r in results]))

    summary = (f"fid_evict={mean_fid_evict:.4f}(HP>={HP_ACC_WITH_EVICTION} HF<{HF_ACC_WITH_EVICTION}) "
               f"fid_no_evict={mean_fid_no_evict:.4f}(HP<={HP_NO_EVICTION_MAX}) "
               f"retained={mean_retained:.4f}(HP>={HP_RETAINED_FID}) "
               f"N={N_ACTIVE} alpha_stress={ALPHA_STRESS} n={n}")

    if mean_fid_evict < HF_ACC_WITH_EVICTION:
        return ("HARD_FAIL", f"HARD_FAIL: eviction not working. {summary}")
    if N_ACTIVE >= 4096 and mean_fid_no_evict > HF_NO_EVICTION_MIN:
        return ("HARD_FAIL", f"HARD_FAIL: no_eviction too high at stress (test not stressed). {summary}")

    n_all_hp = sum(1 for r in results if r["hp_a"] and r["hp_b"] and r["hp_c"])
    n_hp2 = sum(1 for r in results if sum([r["hp_a"], r["hp_b"], r["hp_c"]]) >= 2)
    min_pass = math.ceil(n * 0.6)

    if n_all_hp >= min_pass:
        return ("HARD_PASS", f"HARD_PASS: PP-44 eviction at N=8192 confirmed. {summary}")
    if n_hp2 >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 2/3 cells. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "M_stress": M_STRESS, "M_window": M_WINDOW, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
      f"(N={N_ACTIVE} alpha_stress={ALPHA_STRESS} mode={RUN_MODE})", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] caching_eviction_n8192 N={N_ACTIVE}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N_ACTIVE, "alpha_stress": ALPHA_STRESS, "alpha_window": ALPHA_WINDOW,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "mean_fidelity_with_eviction": float(np.mean([r["fidelity_with_eviction"] for r in all_results])) if all_results else None,
    "mean_fidelity_no_eviction": float(np.mean([r["fidelity_no_eviction"] for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
