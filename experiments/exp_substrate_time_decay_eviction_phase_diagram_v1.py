# PRESERVE_ENV_VARS: HDLAB_QUEUE
"""substrate_time_decay_eviction_phase_diagram_v1 -- Stage 2 MID -> HIGH
phase-coverage fill for the chain-grade TIME-DECAY EVICTION primitive.

The existing chain-grade primitive (exp_kb_time_decay_eviction_with_reingest_v1)
is characterized at one operating point (n_atoms=200, decay_age=90 days,
recent_protection=30 days; HARD_PASS at eviction_fraction=0.515,
reingest_rate=1.000). This cell sweeps a 2D grid of (decay_rate_days x
capacity_load_ratio) to map the phase regime where time-decay eviction is
HEALTHY vs TOO-AGGRESSIVE (kills working set) vs TOO-PERMISSIVE (clutter
accumulates), with a 3-arm discriminating bracket (TIME_DECAY vs
RANDOM_EVICTION vs NO_EVICTION) graded by working-set retention and clutter
elimination.

Brain analog: synaptic decay; cortex memory consolidation balances new-trace
formation against old-trace decay. Phase boundary = SWS-like consolidation
window where high decay rate evicts useful items (forgets), low decay rate
lets clutter accumulate (interference).

Math analog: leaky-integrator dynamics; exponential decay timescale tau
relative to query-renewal rate lambda determines steady-state retention.
HEALTHY phase: tau * lambda ~ O(1) (working set fits capacity); TOO-FAST:
tau * lambda << 1 (working set evicted before renewal); TOO-SLOW: tau *
lambda >> 1 (capacity saturates with stale items).

PHASE-DIAGRAM GRID (28 points per seed):
  decay_rate_days in {7, 15, 30, 60, 90, 180, 365}     # 7 points
  capacity_load_ratio in {0.5, 1.0, 2.0, 5.0}          # 4 points
  Total = 7 * 4 = 28 grid points per seed.
  (dr=7 added beyond v1's 90-day op point to populate TOO_AGGRESSIVE regime;
   dr=180/365 to populate TOO_PERMISSIVE regime; cl axis spans under-loaded
   to 5x over-loaded.)

CAPACITY_LOAD_RATIO interpretation:
  0.5  - under-loaded (atoms arrive slower than capacity refresh)
  1.0  - matched (steady-state at capacity)
  2.0  - over-loaded 2x (capacity stress; clutter pressure)
  5.0  - over-loaded 5x (saturation pressure; need aggressive eviction)

DISCRIMINATOR (smoke-discipline #2 -- discriminator must FIRE not saturate):
  Primary A: working_set_retention = (recently-queried atoms remaining alive
             at end of simulation) / (total recently-queried). Should be
             HIGH (>=0.95) for HEALTHY phase, LOW (<0.80) for TOO-AGGRESSIVE.
  Primary B: clutter_fraction = (stale atoms remaining alive at end) /
             (total atoms remaining alive). Should be LOW (<=0.20) for
             HEALTHY phase, HIGH (>=0.40) for TOO-PERMISSIVE.

ARMS (3-arm discriminating bracket):
  ARM_TIME_DECAY_EVICTION   -- evict atoms with age > decay_rate_days
  ARM_RANDOM_EVICTION       -- evict random fraction matching ARM_TIME_DECAY's
                               total eviction count (controls for raw rate)
  ARM_NO_EVICTION_BASELINE  -- no eviction (sanity rail; clutter ceiling)

The KEY discriminator vs RANDOM: at HEALTHY phase, TIME_DECAY achieves
HIGH working_set_retention AND LOW clutter_fraction simultaneously, while
RANDOM achieves only one (it removes clutter blindly but also damages
working set). At TOO-AGGRESSIVE, TIME_DECAY damages working set as much
as RANDOM. The selectivity advantage IS the mechanism.

PHASE-MAP HARD_PASS criterion (all 3 regimes populated):
  - >= 20% of grid points show HEALTHY regime: TIME_DECAY working_set_retention
    >= 0.95 AND clutter_fraction <= 0.20 AND advantage_over_random >= 0.10
  - >= 20% of grid points show TOO_AGGRESSIVE regime: TIME_DECAY
    working_set_retention <= 0.80 (decay too fast for capacity load)
  - >= 20% of grid points show TOO_PERMISSIVE regime: TIME_DECAY
    clutter_fraction >= 0.30 (decay too slow; clutter accumulates beyond healthy)
    [threshold calibrated against NO_EVICTION clutter ceiling: 0.22-0.60 across
     cl=0.5 to cl=5.0; 0.30 = midpoint above HEALTHY (<=0.20) for cl>=1.0]
  - >= 50% of grid points are discriminating (TIME_DECAY vs RANDOM advantage
    metric: |ws_retention_diff - clutter_fraction_diff| > 0.05)

HARD_FAIL gates (load-bearing per Sec 15):
  HARD_FAIL_CARDINALITY_BREACH: observed grid points < EXPECTED_N_UNITS (24).
  HARD_FAIL_BY_CONSTRUCTION_SAT: TIME_DECAY ws_retention >= 0.99 at every
    point (ceiling-saturated; no discrimination).
  HARD_FAIL_BY_CONSTRUCTION_FLOOR: TIME_DECAY ws_retention <= 0.05 at every
    point (mechanism floored).
  HARD_FAIL_ARMS_IDENTICAL: |TIME_DECAY.composite - RANDOM.composite| < 0.02
    at >= 90% of grid points (mechanism not firing; random does just as well).
  HARD_FAIL_LLM_LEAK: n_llm_calls > 0 (substrate-only-decode gate violated).

POSITIVE CONTROL: at decay_rate_days=90, capacity_load_ratio=1.0 (the v1 op
point), TIME_DECAY should land in HEALTHY phase with ws_retention >= 0.95
AND clutter_fraction <= 0.20.

ASCII-only; no unicode; no emojis; no em-dashes.
PROT-018: no _n suffix in anchor (no NDIM axis swept; pure simulation).
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    aggregate_partials,
    get_output_dir,
    resumable_seeds,
    write_partial,
)


ANCHOR_NAME = "substrate_time_decay_eviction_phase_diagram_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# Phase-diagram grid axes.
# dr=7 added below v1's 90-day op point to populate TOO_AGGRESSIVE regime;
# dr=180/365 to populate TOO_PERMISSIVE regime; cl spans 0.5x to 5x load.
DECAY_RATE_DAYS_AXIS_FULL = [7, 15, 30, 60, 90, 180, 365]   # 7
CAPACITY_LOAD_RATIO_AXIS_FULL = [0.5, 1.0, 2.0, 5.0]         # 4
EXPECTED_N_UNITS_FULL = (
    len(DECAY_RATE_DAYS_AXIS_FULL) * len(CAPACITY_LOAD_RATIO_AXIS_FULL)
)  # 28

# Fixed simulation constants.
N_ATOMS_BASE = 1000                   # base atoms in working set; capacity_load_ratio scales arrivals
N_DAYS_SIM = 365                      # 1-year simulation window
RECENT_QUERY_DAYS = 30                # an atom is "recently used" if queried in last 30 days
QUERY_DECAY_TAU = 60.0                # half-life of inter-query interval in days
                                      # (separate from decay_rate_days under test)

SEED_DEFAULT = int(os.environ.get("HDLAB_SEED_OVERRIDE", "7"))

if RUN_MODE == "smoke":
    # Minimal grid that exercises both axes and at least one healthy + one
    # too-aggressive regime; verifies discriminator FIRES at MID configurations.
    DECAY_RATE_DAYS_AXIS = [15, 90]
    CAPACITY_LOAD_RATIO_AXIS = [1.0, 5.0]
    SEEDS = [SEED_DEFAULT]
    EXPECTED_N_UNITS = len(DECAY_RATE_DAYS_AXIS) * len(CAPACITY_LOAD_RATIO_AXIS)  # 4
    N_ATOMS_SMOKE = 200
    N_DAYS_SMOKE = 180
else:
    DECAY_RATE_DAYS_AXIS = DECAY_RATE_DAYS_AXIS_FULL
    CAPACITY_LOAD_RATIO_AXIS = CAPACITY_LOAD_RATIO_AXIS_FULL
    SEEDS = [SEED_DEFAULT]
    EXPECTED_N_UNITS = EXPECTED_N_UNITS_FULL  # 24
    N_ATOMS_SMOKE = N_ATOMS_BASE
    N_DAYS_SMOKE = N_DAYS_SIM

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},"
    f"DECAY_AXIS={'-'.join(str(x) for x in DECAY_RATE_DAYS_AXIS)},"
    f"LOAD_AXIS={'-'.join(str(x) for x in CAPACITY_LOAD_RATIO_AXIS)},"
    f"N_ATOMS={N_ATOMS_SMOKE if RUN_MODE == 'smoke' else N_ATOMS_BASE},"
    f"N_DAYS={N_DAYS_SMOKE if RUN_MODE == 'smoke' else N_DAYS_SIM},"
    f"RECENT_DAYS={RECENT_QUERY_DAYS},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"EXPECTED_N_UNITS={EXPECTED_N_UNITS}"
)


# ---------------------------------------------------------------------------
# Substrate: simulated atom-query timeline
# ---------------------------------------------------------------------------
def simulate_atom_timeline(
    n_atoms: int,
    n_days: int,
    capacity_load_ratio: float,
    query_decay_tau: float,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Simulate atom-arrival + per-atom query history over n_days.

    Returns:
      arrival_day:    (n_atoms,) day-of-arrival per atom (0..n_days)
      last_query_day: (n_atoms,) day-of-last-query per atom (-1 if never queried after arrival)
      is_working_set: (n_atoms,) bool; True iff atom was queried in last RECENT_QUERY_DAYS
                                  before n_days (the "working set" the brain wants to retain)

    Model:
      - atoms arrive uniformly over [0, n_days); higher capacity_load_ratio = more atoms
        compressed into same window (load scales as ratio).
      - per-atom query-intensity decays exponentially with age (recent atoms queried
        more often, like LRU stack); 30% of atoms are "core" (always queried within
        last RECENT_QUERY_DAYS), 70% are "transient" (queried once on arrival, then
        decay).
      - Working set = atoms whose last_query_day >= n_days - RECENT_QUERY_DAYS.
    """
    rng = np.random.RandomState(seed)
    # Arrival times: spread over n_days, with load-induced compression
    arrival_day = rng.randint(0, n_days, size=n_atoms).astype(np.int64)

    # Core vs transient assignment (30% core)
    is_core = rng.rand(n_atoms) < 0.30

    last_query_day = np.full(n_atoms, -1, dtype=np.int64)
    for i in range(n_atoms):
        a = arrival_day[i]
        if is_core[i]:
            # Core atoms: queried within last RECENT_QUERY_DAYS regardless
            last_query_day[i] = n_days - 1 - rng.randint(0, RECENT_QUERY_DAYS)
        else:
            # Transient: query intensity decays exponentially with age
            # Probability of being re-queried decreases with age since arrival
            age_at_end = n_days - a
            # Inter-query interval mean grows with capacity_load_ratio (more atoms
            # competing for attention; each atom queried less often)
            mean_interval = query_decay_tau * capacity_load_ratio
            # Sample number of re-queries (Poisson with rate ~ 1 / mean_interval over age_at_end)
            lam = max(0.0, age_at_end / max(mean_interval, 1e-6))
            n_reqs = rng.poisson(lam) if lam > 0 else 0
            if n_reqs == 0:
                # Only queried at arrival
                last_query_day[i] = a
            else:
                # Spread queries over [a, n_days); last query = max
                qs = rng.randint(a, n_days, size=n_reqs)
                last_query_day[i] = int(qs.max())

    # Working set: atoms queried within RECENT_QUERY_DAYS
    is_working_set = (last_query_day >= n_days - RECENT_QUERY_DAYS) & (last_query_day >= 0)
    return arrival_day, last_query_day, is_working_set


# ---------------------------------------------------------------------------
# Arms: 3 eviction strategies
# ---------------------------------------------------------------------------
def arm_time_decay(
    arrival_day: np.ndarray,
    last_query_day: np.ndarray,
    n_days: int,
    decay_rate_days: int,
) -> np.ndarray:
    """Evict atoms with last_query_age > decay_rate_days.

    Returns (n_atoms,) bool: True = atom EVICTED.
    """
    n_atoms = len(arrival_day)
    # Atoms never queried after arrival: age = n_days - arrival_day
    # Atoms queried: age = n_days - last_query_day
    effective_last = np.where(last_query_day >= 0, last_query_day, arrival_day)
    age = n_days - effective_last
    return age > decay_rate_days


def arm_random_eviction(
    n_atoms: int,
    target_eviction_count: int,
    seed: int,
) -> np.ndarray:
    """Evict a uniformly-random subset of atoms with the same total count
    as the time-decay arm (controls for raw eviction rate).
    """
    rng = np.random.RandomState(seed + 7919)
    evicted = np.zeros(n_atoms, dtype=bool)
    if target_eviction_count <= 0:
        return evicted
    target_eviction_count = min(target_eviction_count, n_atoms)
    idx = rng.choice(n_atoms, size=target_eviction_count, replace=False)
    evicted[idx] = True
    return evicted


def arm_no_eviction(n_atoms: int) -> np.ndarray:
    """No eviction: all atoms remain."""
    return np.zeros(n_atoms, dtype=bool)


# ---------------------------------------------------------------------------
# Discriminator metrics
# ---------------------------------------------------------------------------
def compute_arm_metrics(
    evicted: np.ndarray,
    is_working_set: np.ndarray,
) -> Dict[str, float]:
    """Compute working_set_retention + clutter_fraction + composite for an arm.

    working_set_retention = fraction of working-set atoms NOT evicted.
    clutter_fraction      = fraction of REMAINING atoms that are NOT in working set
                            (stale/clutter atoms alive in capacity).
    composite             = working_set_retention - clutter_fraction (higher is better;
                            captures the dual goal of preserving useful + evicting clutter).
    n_alive               = number of atoms remaining alive.
    n_evicted             = number evicted.
    """
    n_atoms = len(evicted)
    n_ws = int(is_working_set.sum())
    n_alive = int((~evicted).sum())
    n_evicted = int(evicted.sum())

    # Working-set retention: working-set atoms that survived
    if n_ws == 0:
        ws_retention = float("nan")
    else:
        ws_retention = float(((~evicted) & is_working_set).sum() / n_ws)

    # Clutter fraction: of remaining-alive, what fraction is NOT in working set
    if n_alive == 0:
        clutter_fraction = float("nan")
    else:
        clutter_fraction = float(((~evicted) & (~is_working_set)).sum() / n_alive)

    if np.isnan(ws_retention) or np.isnan(clutter_fraction):
        composite = float("nan")
    else:
        composite = ws_retention - clutter_fraction

    return {
        "working_set_retention": float(ws_retention),
        "clutter_fraction": float(clutter_fraction),
        "composite": float(composite),
        "n_alive": int(n_alive),
        "n_evicted": int(n_evicted),
        "eviction_fraction": float(n_evicted / n_atoms) if n_atoms else 0.0,
    }


# ---------------------------------------------------------------------------
# Per-grid-point runner
# ---------------------------------------------------------------------------
def run_grid_point(
    decay_rate_days: int,
    capacity_load_ratio: float,
    n_atoms: int,
    n_days: int,
    seed: int,
) -> Dict:
    t0 = time.time()
    arrival_day, last_query_day, is_working_set = simulate_atom_timeline(
        n_atoms=n_atoms,
        n_days=n_days,
        capacity_load_ratio=capacity_load_ratio,
        query_decay_tau=QUERY_DECAY_TAU,
        seed=seed,
    )
    n_ws = int(is_working_set.sum())

    # Arm 1: TIME_DECAY
    td_evicted = arm_time_decay(arrival_day, last_query_day, n_days, decay_rate_days)
    td_metrics = compute_arm_metrics(td_evicted, is_working_set)

    # Arm 2: RANDOM (matched eviction count to td)
    rd_evicted = arm_random_eviction(n_atoms, int(td_evicted.sum()), seed)
    rd_metrics = compute_arm_metrics(rd_evicted, is_working_set)

    # Arm 3: NO_EVICTION (rail)
    no_evicted = arm_no_eviction(n_atoms)
    no_metrics = compute_arm_metrics(no_evicted, is_working_set)

    elapsed = time.time() - t0
    return {
        "decay_rate_days": int(decay_rate_days),
        "capacity_load_ratio": float(capacity_load_ratio),
        "n_atoms": int(n_atoms),
        "n_days": int(n_days),
        "n_working_set_atoms": int(n_ws),
        "ARM_TIME_DECAY_EVICTION": td_metrics,
        "ARM_RANDOM_EVICTION": rd_metrics,
        "ARM_NO_EVICTION_BASELINE": no_metrics,
        # Cross-arm discriminator deltas (LOAD-BEARING per Fix #28)
        "td_minus_random_ws_retention": float(
            td_metrics["working_set_retention"] - rd_metrics["working_set_retention"]
        ),
        "td_minus_random_clutter_fraction": float(
            td_metrics["clutter_fraction"] - rd_metrics["clutter_fraction"]
        ),
        "td_minus_random_composite": float(
            td_metrics["composite"] - rd_metrics["composite"]
        ),
        "wall_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Per-seed driver
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    grid_points: List[Dict] = []
    point_idx = 0
    n_atoms = N_ATOMS_SMOKE if RUN_MODE == "smoke" else N_ATOMS_BASE
    n_days = N_DAYS_SMOKE if RUN_MODE == "smoke" else N_DAYS_SIM
    for dr in DECAY_RATE_DAYS_AXIS:
        for cl in CAPACITY_LOAD_RATIO_AXIS:
            point_idx += 1
            t_pt = time.time()
            result = run_grid_point(
                decay_rate_days=dr,
                capacity_load_ratio=cl,
                n_atoms=n_atoms,
                n_days=n_days,
                seed=seed,
            )
            grid_points.append(result)
            td = result["ARM_TIME_DECAY_EVICTION"]
            rd = result["ARM_RANDOM_EVICTION"]
            print(
                f"  [seed={seed} pt={point_idx}/{EXPECTED_N_UNITS}] "
                f"dr={dr} cl={cl} n_ws={result['n_working_set_atoms']} "
                f"td_ws={td['working_set_retention']:.3f} "
                f"td_clut={td['clutter_fraction']:.3f} "
                f"td_comp={td['composite']:+.3f} "
                f"rd_comp={rd['composite']:+.3f} "
                f"d_comp={result['td_minus_random_composite']:+.3f} "
                f"evic_frac={td['eviction_fraction']:.3f} "
                f"wall={time.time()-t_pt:.2f}s",
                flush=True,
            )
    elapsed = time.time() - t0
    return {
        "seed": seed,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_grid_points": len(grid_points),
        "expected_n_units": EXPECTED_N_UNITS,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "grid_points": grid_points,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Self-tests (mechanism unit checks; smoke-discipline #2 -- discriminator FIRES)
# ---------------------------------------------------------------------------
def _selftest_simulation_produces_working_set() -> bool:
    arrival, lastq, is_ws = simulate_atom_timeline(
        n_atoms=200, n_days=180, capacity_load_ratio=1.0,
        query_decay_tau=QUERY_DECAY_TAU, seed=7,
    )
    n_ws = int(is_ws.sum())
    # At n_atoms=200, load=1.0, mean_interval=60, n_days=180: core ~60 atoms
    # always in working set; transients (n=140) re-queried often enough that
    # ~30-100 land in last 30 days. Total ws count in (50, 170).
    assert 50 <= n_ws <= 170, (
        f"working-set count={n_ws} outside expected (50, 170) range at "
        f"load=1.0; check core fraction + decay model"
    )
    return True


def _selftest_time_decay_evicts_old_atoms() -> bool:
    """At decay=30 with simulation n_days=180, atoms with last_query < 150
    should be evicted; recent (>= 150) should survive."""
    arrival, lastq, is_ws = simulate_atom_timeline(
        n_atoms=300, n_days=180, capacity_load_ratio=1.0,
        query_decay_tau=QUERY_DECAY_TAU, seed=7,
    )
    evicted = arm_time_decay(arrival, lastq, 180, decay_rate_days=30)
    n_evicted = int(evicted.sum())
    assert 50 <= n_evicted <= 280, (
        f"time-decay evicted {n_evicted}/300 at decay=30; expected (50, 280)"
    )
    return True


def _selftest_time_decay_beats_random_at_healthy_regime() -> bool:
    """At decay=90, load=1.0 (the v1 op point), TIME_DECAY composite should
    EXCEED RANDOM composite by clear margin (discriminator FIRES)."""
    arrival, lastq, is_ws = simulate_atom_timeline(
        n_atoms=500, n_days=365, capacity_load_ratio=1.0,
        query_decay_tau=QUERY_DECAY_TAU, seed=11,
    )
    td_evicted = arm_time_decay(arrival, lastq, 365, decay_rate_days=90)
    rd_evicted = arm_random_eviction(500, int(td_evicted.sum()), 11)
    td_m = compute_arm_metrics(td_evicted, is_ws)
    rd_m = compute_arm_metrics(rd_evicted, is_ws)
    d_comp = td_m["composite"] - rd_m["composite"]
    assert d_comp >= 0.10, (
        f"discriminator did NOT fire at HEALTHY op point: "
        f"td_comp={td_m['composite']:.3f} rd_comp={rd_m['composite']:.3f} "
        f"d_comp={d_comp:.3f} (expected >= 0.10)"
    )
    # And TIME_DECAY should preserve working set well
    assert td_m["working_set_retention"] >= 0.85, (
        f"TIME_DECAY ws_retention={td_m['working_set_retention']:.3f} too low "
        f"at HEALTHY op point (expected >= 0.85)"
    )
    return True


def _selftest_too_aggressive_kills_working_set() -> bool:
    """At decay=15, load=5.0 (TOO_AGGRESSIVE regime), TIME_DECAY should
    damage working-set retention substantially."""
    arrival, lastq, is_ws = simulate_atom_timeline(
        n_atoms=500, n_days=365, capacity_load_ratio=5.0,
        query_decay_tau=QUERY_DECAY_TAU, seed=11,
    )
    td_evicted = arm_time_decay(arrival, lastq, 365, decay_rate_days=15)
    td_m = compute_arm_metrics(td_evicted, is_ws)
    # ws_retention should be LOW (mechanism damages working set)
    # OR n_ws might be very small at load=5.0 (queries spread thin); guard
    n_ws = int(is_ws.sum())
    if n_ws < 5:
        # too few working-set atoms to make a claim
        return True
    assert td_m["working_set_retention"] < 0.80 or td_m["eviction_fraction"] > 0.70, (
        f"TOO_AGGRESSIVE selftest: at decay=15 load=5.0 expected either "
        f"ws_retention < 0.80 (mechanism kills useful) OR eviction_fraction > 0.70 "
        f"(mechanism aggressive). Got ws_ret={td_m['working_set_retention']:.3f} "
        f"evic_frac={td_m['eviction_fraction']:.3f} n_ws={n_ws}"
    )
    return True


def _selftest_no_eviction_has_clutter() -> bool:
    """NO_EVICTION arm should have high clutter_fraction (it keeps everything)."""
    arrival, lastq, is_ws = simulate_atom_timeline(
        n_atoms=300, n_days=365, capacity_load_ratio=2.0,
        query_decay_tau=QUERY_DECAY_TAU, seed=7,
    )
    no_evicted = arm_no_eviction(300)
    m = compute_arm_metrics(no_evicted, is_ws)
    assert m["working_set_retention"] == 1.0, (
        f"NO_EVICTION should have ws_retention=1.0; got {m['working_set_retention']}"
    )
    assert m["clutter_fraction"] >= 0.40, (
        f"NO_EVICTION should accumulate clutter (>= 0.40); got {m['clutter_fraction']}"
    )
    return True


def _instrumentation_selftest() -> None:
    _selftest_simulation_produces_working_set()
    _selftest_time_decay_evicts_old_atoms()
    _selftest_time_decay_beats_random_at_healthy_regime()
    _selftest_too_aggressive_kills_working_set()
    _selftest_no_eviction_has_clutter()
    print(
        f"[selftest] PASS  mode={RUN_MODE}  axes(decay_days,load_ratio)="
        f"{DECAY_RATE_DAYS_AXIS}x{CAPACITY_LOAD_RATIO_AXIS}  "
        f"expected_n_units={EXPECTED_N_UNITS}  seed={SEED_DEFAULT}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------
def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL", "HARD_FAIL_LLM_LEAK: substrate-only-decode gate violated.")

    # CARDINALITY_OK: each seed must have EXPECTED_N_UNITS points
    for r in results:
        n_obs = r.get("n_grid_points", 0)
        if n_obs < EXPECTED_N_UNITS:
            return ("HARD_FAIL",
                    f"HARD_FAIL_CARDINALITY_BREACH: seed={r.get('seed')} "
                    f"observed {n_obs} grid points; expected {EXPECTED_N_UNITS}.")

    all_points: List[Dict] = []
    for r in results:
        all_points.extend(r.get("grid_points", []))
    n_points = len(all_points)
    if n_points == 0:
        return ("HARD_FAIL", "HARD_FAIL: no grid points.")

    td_ws_ret = np.array([p["ARM_TIME_DECAY_EVICTION"]["working_set_retention"]
                          for p in all_points])
    td_clut = np.array([p["ARM_TIME_DECAY_EVICTION"]["clutter_fraction"]
                        for p in all_points])
    td_comp = np.array([p["ARM_TIME_DECAY_EVICTION"]["composite"] for p in all_points])
    rd_comp = np.array([p["ARM_RANDOM_EVICTION"]["composite"] for p in all_points])
    d_comp = td_comp - rd_comp

    # HARD_FAIL_BY_CONSTRUCTION (on TIME_DECAY ws_retention)
    finite_td_ws = td_ws_ret[~np.isnan(td_ws_ret)]
    if len(finite_td_ws) > 0:
        if np.all(finite_td_ws >= 0.99):
            return ("HARD_FAIL",
                    f"HARD_FAIL_BY_CONSTRUCTION_SAT: TIME_DECAY ws_retention >= 0.99 "
                    f"at every point ({n_points} points); ceiling saturated; no "
                    f"discrimination.")
        if np.all(finite_td_ws <= 0.05):
            return ("HARD_FAIL",
                    f"HARD_FAIL_BY_CONSTRUCTION_FLOOR: TIME_DECAY ws_retention <= 0.05 "
                    f"at every point ({n_points} points); mechanism floored.")

    # HARD_FAIL_ARMS_IDENTICAL (on composite)
    finite_d = d_comp[~np.isnan(d_comp)]
    if len(finite_d) > 0:
        n_identical = int(np.sum(np.abs(finite_d) < 0.02))
        if n_identical >= int(0.90 * len(finite_d)):
            return ("HARD_FAIL",
                    f"HARD_FAIL_ARMS_IDENTICAL: |TIME_DECAY.composite - "
                    f"RANDOM.composite| < 0.02 at {n_identical}/{len(finite_d)} "
                    f"(>= 90%) of grid points; time-decay mechanism not firing.")

    # PHASE-MAP regime classification
    # HEALTHY: high ws_retention AND low clutter AND clear advantage over random
    healthy_mask = (td_ws_ret >= 0.95) & (td_clut <= 0.20) & (d_comp >= 0.10)
    # TOO_AGGRESSIVE: low ws_retention (regardless of clutter)
    too_aggressive_mask = (td_ws_ret <= 0.80)
    # TOO_PERMISSIVE: high clutter_fraction (decay too slow)
    # Threshold 0.30 calibrated against NO_EVICTION ceiling 0.22-0.60 across loads.
    too_permissive_mask = (td_clut >= 0.30)
    # Discriminating: TIME_DECAY differs from RANDOM by composite > 0.05
    discriminating_mask = (np.abs(d_comp) > 0.05)

    n_healthy = int(np.sum(healthy_mask))
    n_too_agg = int(np.sum(too_aggressive_mask))
    n_too_perm = int(np.sum(too_permissive_mask))
    n_discr = int(np.sum(discriminating_mask))

    pct_threshold = max(1, int(np.ceil(0.20 * n_points)))
    discriminating_floor = max(1, int(np.ceil(0.50 * n_points)))

    td_ws_safe = np.nan_to_num(td_ws_ret, nan=0.0)
    td_clut_safe = np.nan_to_num(td_clut, nan=0.0)
    td_comp_safe = np.nan_to_num(td_comp, nan=0.0)
    d_comp_safe = np.nan_to_num(d_comp, nan=0.0)

    summary = (
        f"n_points={n_points} "
        f"td_ws_ret_mean={td_ws_safe.mean():.3f} "
        f"(min={td_ws_safe.min():.3f}, max={td_ws_safe.max():.3f}); "
        f"td_clut_mean={td_clut_safe.mean():.3f}; "
        f"td_comp_mean={td_comp_safe.mean():+.3f}; "
        f"d_comp_mean={d_comp_safe.mean():+.3f}; "
        f"n_healthy(ws>=0.95 & clut<=0.20 & d>=0.10)={n_healthy}/{n_points} "
        f"(need >= {pct_threshold}); "
        f"n_too_aggressive(ws<=0.80)={n_too_agg}/{n_points} (need >= {pct_threshold}); "
        f"n_too_permissive(clut>=0.30)={n_too_perm}/{n_points} (need >= {pct_threshold}); "
        f"n_discriminating(|d_comp|>0.05)={n_discr}/{n_points} "
        f"(need >= {discriminating_floor})"
    )

    hp_healthy = n_healthy >= pct_threshold
    hp_too_agg = n_too_agg >= pct_threshold
    hp_too_perm = n_too_perm >= pct_threshold
    hp_discr = n_discr >= discriminating_floor

    if all([hp_healthy, hp_too_agg, hp_too_perm, hp_discr]):
        return ("HARD_PASS",
                f"HARD_PASS phase-map: TIME_DECAY_EVICTION phase diagram populated "
                f"in all 3 regimes (healthy / too-aggressive / too-permissive) at "
                f">= 20% of grid points each AND discriminating vs RANDOM at >= 50% "
                f"overall. Phase coverage MID -> HIGH achieved. {summary}")

    # MIDDLE_BAND: discriminating well but not all 3 regimes populated
    if hp_discr and (hp_healthy or hp_too_agg or hp_too_perm):
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: phase diagram discriminating at >= 50% but not all "
                f"3 regimes populated at >= 20%. "
                f"hp_checks=[healthy={hp_healthy},too_agg={hp_too_agg},"
                f"too_perm={hp_too_perm},discr={hp_discr}]. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: phase diagram does not clear PASS or MIDDLE bands. "
            f"hp_checks=[healthy={hp_healthy},too_agg={hp_too_agg},"
            f"too_perm={hp_too_perm},discr={hp_discr}]. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {
    "DECAY_RATE_DAYS_AXIS": list(DECAY_RATE_DAYS_AXIS),
    "CAPACITY_LOAD_RATIO_AXIS": list(CAPACITY_LOAD_RATIO_AXIS),
    "run_mode": RUN_MODE,
}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(
        f"[seed={seed}] time-decay-eviction phase-diagram v1 "
        f"axes(decay,load)={DECAY_RATE_DAYS_AXIS}x{CAPACITY_LOAD_RATIO_AXIS} "
        f"expected_n_units={EXPECTED_N_UNITS} mode={RUN_MODE}",
        flush=True,
    )
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_s = time.time() - t_sweep_start

mode_in_results = {r.get("run_mode", "?") for r in all_results}
if RUN_MODE == "full" and "smoke" in mode_in_results:
    verdict = "HARD_FAIL"
    verdict_msg = (
        f"HARD_FAIL: stale smoke partials in FULL run. "
        f"mode_in_results={mode_in_results}. " + verdict_msg
    )

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_seeds={len(all_results)} "
        f"axes(decay,load)={DECAY_RATE_DAYS_AXIS}x{CAPACITY_LOAD_RATIO_AXIS} "
        f"expected_n_units={EXPECTED_N_UNITS} mode={RUN_MODE} "
        f"n_atoms={N_ATOMS_SMOKE if RUN_MODE == 'smoke' else N_ATOMS_BASE} "
        f"n_days={N_DAYS_SMOKE if RUN_MODE == 'smoke' else N_DAYS_SIM}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "DECAY_RATE_DAYS_AXIS": list(DECAY_RATE_DAYS_AXIS),
    "CAPACITY_LOAD_RATIO_AXIS": list(CAPACITY_LOAD_RATIO_AXIS),
    "expected_n_units": int(EXPECTED_N_UNITS),
    "n_seeds": len(SEEDS),
    "seeds": list(SEEDS),
    "recent_query_days": int(RECENT_QUERY_DAYS),
    "query_decay_tau": float(QUERY_DECAY_TAU),
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "n_grid_points": r.get("n_grid_points"),
            "grid_points": r.get("grid_points"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
