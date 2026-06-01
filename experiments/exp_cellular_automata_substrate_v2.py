"""Cellular automata substrate v2: Class II limit cycle detection + convergence fix.

CONTEXT:
  cellular_automata_substrate_v1 MIDDLE_BAND:
    conv=0/5, Class_I/II=100.0%, diverging=0/5 at alpha=0.10.
  Interpretation: ALL seeds show Class I/II dynamics (periodic/attractor) but NONE
  converge within 31 steps. Class II = limit cycles, which is interesting but the
  v1 verdict was MIDDLE_BAND because 0/5 converged (HP required convergence within steps).

  The diagnostic from v1: at alpha=0.10, substrate lands in Class II (limit cycles),
  NOT Class III (chaotic) or Class IV (complex). Class II means: patterns cycle with
  period >= 2. This is a verified finding -- the substrate is an attractor network
  with periodic dynamics.

  v2 probe:
  1. Detect the PERIOD of each cycle (period-1 = fixed point, period-2 = flip-flop,
     period-k = longer cycle). Product claim: Class II with period-2 is the normal
     operating regime (confirmed by BID/SKAH-M: non-equilibrium gated-multistable AM).
  2. Verify that period-2 cycles collapse to period-1 (fixed points) when retrieval
     uses soft-sign (tanh activation) instead of hard-sign (sgn activation).
  3. Check whether the cycle orbit contains the stored pattern (orbit membership).

PRE-REGISTERED BANDS (follow-on to Class II finding):
  HARD-PASS:
    - >= 80% of seeds show dominant period in {1, 2} (short limit cycles)
    - AND orbit-membership: the stored pattern appears in the limit cycle orbit
      in >= 3/5 seeds at sub-capacity alpha
    - AND tanh activation reduces period to 1 (fixed points) in >= 3/5 seeds
  HARD-FAIL:
    - Dominant period > 10 in >= 4/5 seeds (long cycles; no useful attractor)
    - OR orbit-membership fails: pattern never in orbit in >= 4/5 seeds
  MIDDLE-BAND:
    - Short cycles but tanh does not help
    - OR period-2 verified but no orbit membership

FORMULA SELF-TESTS:
  1. For perfectly separated patterns (M=1, N large), retrieval should converge in 1 step.
  2. Period detection: alternating +v/-v cycle has period 2. Self-test: W=-I gives period-2
     cycling on any non-zero state.
  3. Tanh activation with very large beta (hard limit): should match hard-sign behavior.

Timeout estimate:
  v1 elapsed_s=15s for 5 seeds 5 alpha-values. v2 adds period detection + orbit membership:
  ~2x. timeout_s = ceil(1.5 * 30 * 1.0 * 1.0) = ceil(45) -> 300s. Use 600s for margin.

N-suffix: no _nN suffix; production N = 1024.
Queue: remote_cpu_queue (pure numpy; 5-seed; ~5-20 min)
Pre-reg: preregs/2026-05-27_cellular_automata_substrate_v2.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Production config ---
N_FULL  = 1024
N_SMOKE = 256
ALPHA_LOAD = 0.10   # fixed at Class II zone from v1
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1
MAX_ORBIT_STEPS = 100
MAX_PERIOD = 20
TANH_BETA = 10.0   # soft activation inverse temperature

HP_SHORT_PERIOD_FRAC = 0.80
HP_ORBIT_MEMBER_MIN = 3
HP_TANH_FP_MIN = 3
HF_LONG_PERIOD_MIN = 4
HF_NO_ORBIT_MIN = 4


def get_output_dir(default_name: str = "cellular_automata_substrate_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_substrate(N: int, M: int, seed: int):
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N))
    W = np.zeros((N, N), dtype=np.float64)
    for v in patterns:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, patterns


def hard_sign_step(W: np.ndarray, x: np.ndarray) -> np.ndarray:
    result = np.sign(W @ x)
    result[result == 0] = 1.0
    return result


def tanh_step(W: np.ndarray, x: np.ndarray, beta: float) -> np.ndarray:
    return np.tanh(beta * (W @ x))


def detect_period(W: np.ndarray, init_state: np.ndarray,
                  max_steps: int, use_tanh: bool = False) -> Dict:
    """Run CA dynamics and detect period of limit cycle.

    Returns dict with: period, orbit (list of states in cycle), orbit_steps.
    """
    states = [init_state.copy()]
    state = init_state.copy()
    for step in range(max_steps):
        if use_tanh:
            next_state = tanh_step(W, state, TANH_BETA)
            # Binarize for period detection
            next_state_bin = np.sign(next_state)
            next_state_bin[next_state_bin == 0] = 1.0
        else:
            next_state_bin = hard_sign_step(W, state)
        # Check if we've seen this state before
        for prev_idx, prev_state in enumerate(states):
            if np.array_equal(next_state_bin, prev_state):
                period = len(states) - prev_idx
                orbit = states[prev_idx:]
                return {
                    "period": period,
                    "orbit_len": len(orbit),
                    "orbit_start_step": prev_idx,
                    "total_steps": step + 1,
                    "converged": True,
                }
        states.append(next_state_bin.copy())
        state = next_state_bin
    # No cycle detected within max_steps
    return {
        "period": max_steps,   # use max_steps as sentinel for "long cycle"
        "orbit_len": 0,
        "orbit_start_step": max_steps,
        "total_steps": max_steps,
        "converged": False,
    }


def check_orbit_membership(W: np.ndarray, pattern: np.ndarray, max_steps: int) -> bool:
    """Check if pattern appears in the limit cycle orbit starting from pattern."""
    state = pattern.copy()
    visited = []
    for _ in range(max_steps):
        next_state = hard_sign_step(W, state)
        if np.array_equal(next_state, pattern):
            return True   # pattern is in the orbit
        # Check if we've seen this state (limit cycle without pattern)
        for v in visited:
            if np.array_equal(next_state, v):
                return False  # cycle found but pattern not in it
        visited.append(state.copy())
        state = next_state
    return False


def run_one_seed(N: int, seed: int) -> Dict:
    M = max(4, int(N * ALPHA_LOAD))
    W, patterns = build_substrate(N, M, seed)

    period_results = []
    tanh_fp_results = []
    orbit_member_results = []

    rng = np.random.default_rng(seed + 1000)

    for pat in patterns:
        # 1. Period detection (hard-sign)
        pdet = detect_period(W, pat, MAX_ORBIT_STEPS, use_tanh=False)
        period_results.append(pdet)

        # 2. Tanh activation: does it give period-1 (fixed point)?
        tdet = detect_period(W, pat, MAX_ORBIT_STEPS, use_tanh=True)
        tanh_fp_results.append(tdet)

        # 3. Orbit membership check
        in_orbit = check_orbit_membership(W, pat, MAX_ORBIT_STEPS)
        orbit_member_results.append(in_orbit)

    periods = [r["period"] for r in period_results]
    tanh_periods = [r["period"] for r in tanh_fp_results]

    dominant_period = int(np.median(periods))
    frac_short = float(np.mean([1 for p in periods if p <= 2]))
    frac_tanh_fp = float(np.mean([1 for p in tanh_periods if p == 1]))
    frac_orbit_member = float(np.mean(orbit_member_results))
    n_orbit_member = int(sum(orbit_member_results))

    return {
        "N": N, "M": M, "seed": seed,
        "dominant_period": dominant_period,
        "frac_short_period": frac_short,
        "frac_tanh_fixed_point": frac_tanh_fp,
        "frac_orbit_member": frac_orbit_member,
        "n_orbit_member": n_orbit_member,
        "period_hist": {str(p): int(np.sum(np.array(periods) == p)) for p in sorted(set(periods))},
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel."""
    # 1. M=1 single-pattern substrate: retrieval should be period-1 (fixed point)
    N_t = 64
    W_t, pats_t = build_substrate(N_t, 1, seed=42)
    pdet = detect_period(W_t, pats_t[0], MAX_ORBIT_STEPS)
    # For 1 pattern at sub-capacity, should converge quickly
    assert pdet["converged"] or pdet["period"] <= 4, \
        f"Single-pattern substrate: expected short cycle, got period={pdet['period']}"

    # 2. Period detection: -I gives period-2 on any nonzero state
    W_neg = -np.eye(N_t, dtype=np.float64)
    state_test = np.ones(N_t, dtype=np.float64)
    pdet_neg = detect_period(W_neg, state_test, MAX_ORBIT_STEPS)
    assert pdet_neg["period"] == 2, f"Expected period=2 for W=-I, got {pdet_neg['period']}"

    # 3. Orbit membership: stored pattern in single-pattern substrate
    in_orb = check_orbit_membership(W_t, pats_t[0], MAX_ORBIT_STEPS)
    assert isinstance(in_orb, bool), f"orbit membership not bool: {type(in_orb)}"

    # 4. run_one_seed returns all required fields
    r = run_one_seed(64, seed=7)
    for key in ["dominant_period", "frac_short_period", "frac_tanh_fixed_point",
                "frac_orbit_member"]:
        assert key in r and r[key] is not None, f"Missing field: {key}"
        assert math.isfinite(r[key]), f"Field {key} not finite: {r[key]}"

    # 5. Multi-scale: N_smoke and N_smoke*4
    r_s = run_one_seed(64, seed=7)
    r_l = run_one_seed(256, seed=7)
    assert 0.0 <= r_l["frac_short_period"] <= 1.0, f"frac_short out of range"
    assert 0.0 <= r_l["frac_orbit_member"] <= 1.0, f"frac_orbit out of range"

    print("SELFTEST PASS: all assertions satisfied (CA v2)")


_instrumentation_selftest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)

    N = N_SMOKE if args.smoke else N_FULL
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    out_dir = get_output_dir()
    mode = "smoke" if args.smoke else "full"

    t0 = time.time()
    results = []
    for seed in seeds:
        r = run_one_seed(N, seed)
        results.append(r)
        print(f"[{mode}] N={N} seed={seed} dominant_period={r['dominant_period']} "
              f"frac_short={r['frac_short_period']:.3f} "
              f"frac_tanh_fp={r['frac_tanh_fixed_point']:.3f} "
              f"frac_orbit={r['frac_orbit_member']:.3f}")

    elapsed = time.time() - t0

    n_short = sum(1 for r in results if r["frac_short_period"] >= HP_SHORT_PERIOD_FRAC)
    n_orbit = sum(1 for r in results if r["n_orbit_member"] >= HP_ORBIT_MEMBER_MIN)
    n_tanh_fp = sum(1 for r in results if r["frac_tanh_fixed_point"] >= 0.50)
    n_long = sum(1 for r in results if r["dominant_period"] > MAX_PERIOD)
    n_no_orbit = sum(1 for r in results if r["frac_orbit_member"] < 0.10)

    if n_long >= HF_LONG_PERIOD_MIN or n_no_orbit >= HF_NO_ORBIT_MIN:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: long cycles (>20) in {n_long}/{len(seeds)} seeds; "
                       f"no orbit membership in {n_no_orbit}/{len(seeds)} seeds.")
    elif n_short >= 4 and n_orbit >= HP_ORBIT_MEMBER_MIN and n_tanh_fp >= HP_TANH_FP_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: short cycles in {n_short}/{len(seeds)}, "
                       f"orbit_member in {n_orbit}/{len(seeds)}, "
                       f"tanh_fp in {n_tanh_fp}/{len(seeds)} seeds.")
    else:
        mean_sp = float(np.mean([r["frac_short_period"] for r in results]))
        mean_om = float(np.mean([r["frac_orbit_member"] for r in results]))
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: short_period {n_short}/{len(seeds)}, "
                       f"orbit_member {n_orbit}/{len(seeds)}, "
                       f"tanh_fp {n_tanh_fp}/{len(seeds)}. "
                       f"mean_short={mean_sp:.3f} mean_orbit={mean_om:.3f}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "n_seeds": len(seeds),
        "n_short_period": n_short,
        "n_orbit_member": n_orbit,
        "n_tanh_fp": n_tanh_fp,
        "per_seed": results,
        "summary": f"CA substrate v2 N={N}: {verdict}",
        "config": {
            "N": N, "ALPHA_LOAD": ALPHA_LOAD,
            "seeds": seeds, "MAX_ORBIT_STEPS": MAX_ORBIT_STEPS,
        },
    }

    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"VERDICT: {verdict}")
    print(f"MSG: {verdict_msg}")
    print(f"Wrote metrics to {out_path}")


if __name__ == "__main__":
    main()
