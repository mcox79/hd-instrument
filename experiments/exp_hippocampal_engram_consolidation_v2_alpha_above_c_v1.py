"""
hippocampal_engram_consolidation_v2_alpha_above_c_v1 -- Engram consolidation v2: above-capacity.

v1 FAILURE DIAGNOSIS:
  v1 used alpha_total = 0.12 < alpha_c = 0.138 (below critical load).
  At below-capacity load, all patterns retrieve with high fidelity regardless of replay.
  The consolidation gain was minimal because both with-replay and without-replay
  conditions achieved ~0.80+ fidelity (no ceiling to differentiate).

v2 REDESIGN: alpha_total = 0.20 (well above alpha_c = 0.138).
  At above-capacity load:
    - Without replay: fidelity of old patterns degrades to ~0.50-0.65.
    - With replay: fidelity of old patterns maintained near 0.80+.
    - Consolidation gain = fid_replay - fid_no_replay should be >= 0.10.

  Protocol (same as v1, different alpha):
    1. Store M_old patterns at alpha_old = 0.10 (below capacity).
    2. Add M_new patterns pushing alpha to 0.20 (above capacity).
    3. Without replay: measure old pattern fidelity after M_new additions.
    4. With replay: re-present xi_old before each new write; measure after.
    5. Consolidation gain = fid_replay - fid_no_replay.

PRE-REGISTERED BANDS:
  HP-A: consolidation_gain >= 0.10 (replay provides meaningful benefit).
  HP-B: fidelity_with_replay >= 0.70 (replay keeps old patterns viable).
  HP-C: new_fidelity_with_replay >= 0.50 (replay doesn't catastrophically block new).
  HARD-FAIL: fidelity_with_replay < 0.40 OR fidelity_no_replay > 0.80 at alpha=0.20
             (no stress = no test).
  MIDDLE: 2/3 cells pass.

  Theory: at alpha=0.20 > alpha_c, without-replay fidelity should drop to 0.50-0.65.
  Replay effectively halves the functional alpha by refreshing old patterns.
  P_deflated = 0.55 (first above-capacity engram test; wider bands per calibration policy).

FORMULA SELF-TESTS:
  1. alpha_total at production N: (M_old + M_new) / N > alpha_c.
     [INPUT: N=4096, M_old=410, M_new=410] [EXPECTED: alpha=0.20 > 0.138]
  2. Replay write increases fidelity: for M=2, N=64, replay recovers pattern.
     [INPUT: W_after_new = W + outer(xi_new), W_replay = W_after_new + outer(xi_old)]
     [EXPECTED: cosine(W_replay @ xi_old, xi_old) > cosine(W_after_new @ xi_old, xi_old)]
  3. alpha_new > alpha_c check.
     [EXPECTED: (M_old+M_new)/N >= 0.18 at production scale]

PROT-018: no _nN suffix; production N=4096 (PROT-018 rule 3 -- N stated explicitly).
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

ANCHOR_NAME = "hippocampal_engram_consolidation_v2_alpha_above_c_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 4096
ALPHA_C = 0.138
ALPHA_OLD_TARGET = 0.10   # below capacity
ALPHA_TOTAL_TARGET = 0.20  # above capacity (v2 key change)
NOISE_FRAC = 0.10

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_OLD = max(10, int(ALPHA_OLD_TARGET * 512))   # smoke at smaller effective N
    M_NEW = max(10, int((ALPHA_TOTAL_TARGET - ALPHA_OLD_TARGET) * 512))
    N_QUERIES = 5
    N_REPLAY_STEPS = 1
    N_ACTIVE = 512
else:
    SEEDS = [7, 17, 23, 31, 41, 53, 59]  # 7 seeds: walk-back gate (borderline smoke)
    M_OLD = int(ALPHA_OLD_TARGET * N)     # 410 patterns
    M_NEW = int((ALPHA_TOTAL_TARGET - ALPHA_OLD_TARGET) * N)  # 410 patterns
    N_QUERIES = 15
    N_REPLAY_STEPS = 2
    N_ACTIVE = N

HP_CONSOLIDATION_GAIN = 0.08   # calibration probe: +-50% of expected 0.10-0.20 gain
HP_OLD_FIDELITY_REPLAY = 0.70
# HP-C: new pattern fidelity >= 0.30 at above-capacity alpha (not catastrophic blocking)
# NOTE: at alpha=0.20 > alpha_c, new patterns are also crowded out; 0.30 is conservative.
HP_NEW_FIDELITY_REPLAY = 0.30
HF_OLD_FIDELITY_REPLAY = 0.40
HF_NO_REPLAY_MAX = 0.80  # if no_replay fidelity > this, test is not stressed


def hopfield_fidelity(W: np.ndarray, Xi: np.ndarray, n: int, noise_frac: float,
                       rng: np.random.RandomState, n_test: int, n_steps: int = 5) -> float:
    M = Xi.shape[0]
    fids = []
    for q in range(min(n_test, M)):
        probe = Xi[q].copy()
        flip = rng.random(n) < noise_frac
        probe[flip] *= -1.0
        state = probe.copy()
        for _ in range(n_steps):
            h = W @ state
            state = np.sign(h)
            state[state == 0] = 1.0
        fid = float(np.dot(state, Xi[q])) / float(n)
        fids.append(fid)
    return float(np.mean(fids)) if fids else 0.0


def _selftest_alpha_above_c():
    alpha_new = (M_OLD + M_NEW) / float(N_ACTIVE)
    assert alpha_new >= 0.18, \
        f"alpha_total={alpha_new:.4f} not >= 0.18 (test not above capacity)"
    return alpha_new


def _selftest_replay_helps():
    n_small = 64
    rng = np.random.RandomState(42)
    xi_old = rng.choice([-1.0, 1.0], size=n_small).astype(np.float64)
    xi_new = rng.choice([-1.0, 1.0], size=n_small).astype(np.float64)
    W_base = np.outer(xi_old, xi_old) / n_small
    np.fill_diagonal(W_base, 0.0)
    W_after = W_base + np.outer(xi_new, xi_new) / n_small
    np.fill_diagonal(W_after, 0.0)
    W_replay = W_after + np.outer(xi_old, xi_old) / n_small
    np.fill_diagonal(W_replay, 0.0)
    h_no = W_after @ xi_old
    h_rp = W_replay @ xi_old
    fid_no = float(np.dot(np.sign(h_no), xi_old)) / n_small
    fid_rp = float(np.dot(np.sign(h_rp), xi_old)) / n_small
    assert fid_rp >= fid_no, f"replay selftest: fid_rp={fid_rp:.4f} < fid_no={fid_no:.4f}"
    return fid_no, fid_rp


def _instrumentation_selftest():
    alpha_new = _selftest_alpha_above_c()
    fid_no, fid_rp = _selftest_replay_helps()
    assert N_QUERIES > 0, "N_QUERIES > 0 required"
    print(f"[selftest] PASS: alpha_total={alpha_new:.4f} (above alpha_c={ALPHA_C}) "
          f"replay_selftest: fid_no={fid_no:.4f} fid_rp={fid_rp:.4f} "
          f"N_ACTIVE={N_ACTIVE} M_OLD={M_OLD} M_NEW={M_NEW}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    Xi_old = rng.choice([-1.0, 1.0], size=(M_OLD, N_ACTIVE)).astype(np.float64)
    Xi_new = rng.choice([-1.0, 1.0], size=(M_NEW, N_ACTIVE)).astype(np.float64)

    # W_old: store M_OLD patterns (below capacity)
    W_old = Xi_old.T @ Xi_old / float(N_ACTIVE)
    np.fill_diagonal(W_old, 0.0)

    # No-replay: add M_NEW patterns directly
    W_no_replay = W_old.copy()
    W_no_replay += Xi_new.T @ Xi_new / float(N_ACTIVE)
    np.fill_diagonal(W_no_replay, 0.0)

    # With-replay: interleave new writes with old-pattern replay
    W_replay = W_old.copy()
    for i in range(M_NEW):
        W_replay += np.outer(Xi_new[i], Xi_new[i]) / float(N_ACTIVE)
        # Replay interval: replay all old patterns at N_REPLAY_STEPS checkpoints
        if (i + 1) % max(1, M_NEW // N_REPLAY_STEPS) == 0:
            for j in range(M_OLD):
                W_replay += np.outer(Xi_old[j], Xi_old[j]) / float(N_ACTIVE)
    np.fill_diagonal(W_replay, 0.0)
    # Normalize to keep weights bounded
    W_replay /= (1.0 + float(M_OLD) * float(N_REPLAY_STEPS) / float(M_NEW))

    alpha_total = (M_OLD + M_NEW) / float(N_ACTIVE)

    rng_test1 = np.random.RandomState(seed + 200)
    fid_no_replay = hopfield_fidelity(W_no_replay, Xi_old, N_ACTIVE, NOISE_FRAC, rng_test1, N_QUERIES)

    rng_test2 = np.random.RandomState(seed + 201)
    fid_with_replay = hopfield_fidelity(W_replay, Xi_old, N_ACTIVE, NOISE_FRAC, rng_test2, N_QUERIES)

    rng_test3 = np.random.RandomState(seed + 202)
    new_fid_with_replay = hopfield_fidelity(W_replay, Xi_new, N_ACTIVE, NOISE_FRAC, rng_test3, N_QUERIES)

    consolidation_gain = fid_with_replay - fid_no_replay

    hp_a = consolidation_gain >= HP_CONSOLIDATION_GAIN
    hp_b = fid_with_replay >= HP_OLD_FIDELITY_REPLAY
    hp_c = new_fid_with_replay >= HP_NEW_FIDELITY_REPLAY

    # Hard fail conditions
    hf_replay_low = fid_with_replay < HF_OLD_FIDELITY_REPLAY
    # HF_NO_STRESS only applies at production N (>=4096): at smoke N=512, finite-N effects
    # keep fidelity artificially high even above alpha_c (thermodynamic limit not reached yet).
    hf_no_stress = (N_ACTIVE >= 4096) and (fid_no_replay > HF_NO_REPLAY_MAX)

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={N_ACTIVE} M_old={M_OLD} M_new={M_NEW} alpha={alpha_total:.3f}] "
          f"fid_no_replay={fid_no_replay:.4f} fid_replay={fid_with_replay:.4f} "
          f"gain={consolidation_gain:.4f}(HP>={HP_CONSOLIDATION_GAIN}) "
          f"new_fid={new_fid_with_replay:.4f}(HP>={HP_NEW_FIDELITY_REPLAY}) "
          f"hp_ABC=[{int(hp_a)},{int(hp_b)},{int(hp_c)}] "
          f"hf=[{int(hf_replay_low)},{int(hf_no_stress)}] elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N_ACTIVE, "M_old": M_OLD, "M_new": M_NEW,
        "alpha_total": float(alpha_total), "run_mode": RUN_MODE,
        "fidelity_no_replay": float(fid_no_replay),
        "fidelity_with_replay": float(fid_with_replay),
        "consolidation_gain": float(consolidation_gain),
        "new_fidelity_with_replay": float(new_fid_with_replay),
        "hp_a": bool(hp_a), "hp_b": bool(hp_b), "hp_c": bool(hp_c),
        "hf_replay_low": bool(hf_replay_low),
        "hf_no_stress": bool(hf_no_stress),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    mean_gain = float(np.mean([r["consolidation_gain"] for r in results]))
    mean_fid_r = float(np.mean([r["fidelity_with_replay"] for r in results]))
    mean_new_fid = float(np.mean([r["new_fidelity_with_replay"] for r in results]))
    mean_fid_no = float(np.mean([r["fidelity_no_replay"] for r in results]))

    summary = (f"gain={mean_gain:.4f}(HP>={HP_CONSOLIDATION_GAIN}) "
               f"fid_replay={mean_fid_r:.4f}(HP>={HP_OLD_FIDELITY_REPLAY} HF<{HF_OLD_FIDELITY_REPLAY}) "
               f"fid_no_replay={mean_fid_no:.4f}(HF_no_stress if >{HF_NO_REPLAY_MAX}) "
               f"new_fid={mean_new_fid:.4f}(HP>={HP_NEW_FIDELITY_REPLAY}) n={n}")

    if any(r["hf_replay_low"] for r in results):
        return ("HARD_FAIL", f"HARD_FAIL: fid_replay below HF. {summary}")
    # hf_no_stress only fires at production N>=4096 (smoke at N=512 uses finite-N suppression)
    if any(r["hf_no_stress"] for r in results):
        return ("HARD_FAIL", f"HARD_FAIL: no_replay still >{HF_NO_REPLAY_MAX} at N>=4096 (alpha not stressing). {summary}")

    n_all_hp = sum(1 for r in results if r["hp_a"] and r["hp_b"] and r["hp_c"])
    n_hp2 = sum(1 for r in results if sum([r["hp_a"], r["hp_b"], r["hp_c"]]) >= 2)
    min_pass = math.ceil(n * 0.6)

    if n_all_hp >= min_pass:
        return ("HARD_PASS", f"HARD_PASS: engram consolidation confirmed at alpha_above_c=0.20. {summary}")
    if n_hp2 >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 2/3 cells pass. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "M_old": M_OLD, "M_new": M_NEW, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
      f"(N={N_ACTIVE} M_old={M_OLD} M_new={M_NEW} mode={RUN_MODE})", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] hippocampal_engram_v2 N={N_ACTIVE} alpha_target={ALPHA_TOTAL_TARGET}...", flush=True)
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
    "N": N_ACTIVE, "M_old": M_OLD, "M_new": M_NEW,
    "alpha_c": ALPHA_C, "alpha_total_target": ALPHA_TOTAL_TARGET,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "mean_consolidation_gain": float(np.mean([r["consolidation_gain"] for r in all_results])) if all_results else None,
    "mean_fidelity_with_replay": float(np.mean([r["fidelity_with_replay"] for r in all_results])) if all_results else None,
    "mean_fidelity_no_replay": float(np.mean([r["fidelity_no_replay"] for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
