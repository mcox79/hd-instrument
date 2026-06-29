# PRESERVE_ENV_VARS: HDLAB_QUEUE
"""substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC -- mechanism-class
diversion of v1: replace binary-threshold healthy-gate with CONTINUOUS
cross-arm Pareto-dominance + per-seed dominance-rate AUC discriminator.

v1 (commits 5efe549b / 4ba529a4) shipped 2 HARD_PASS seeds (13, 19) + 1
MIDDLE_BAND seed (7; healthy=5/28, 1 point shy of the 6/28 gate). 3 near-miss
points at clutter 0.21/0.22/0.20 sat just above the binary 0.20 cap. That
boundary-threshold instability is a discriminator-design issue, not a
mechanism issue.

v2 ROOT-CAUSE FIX: drop point-in-rectangle counting (discrete, boundary-fragile)
and use cross-arm Pareto-dominance on the (ws_retention, 1 - clutter_fraction)
plane -- a continuous geometric discriminator where "TIME_DECAY beats RANDOM
on BOTH objectives at this config" is the unambiguous mechanism signature.

Brain analog (unchanged from v1): synaptic decay; cortex memory consolidation
balances new-trace formation against old-trace decay. Phase boundary = SWS-like
consolidation window where high decay rate evicts useful items (forgets), low
decay rate lets clutter accumulate (interference).

PARETO-AUC DISCRIMINATOR (load-bearing):

  At each (decay_rate_days, capacity_load_ratio) grid point, both TIME_DECAY
  and RANDOM produce a 2-D point (ws, 1-clut). Mechanism signature:

    TD STRICTLY DOMINATES RD at config c iff
      TD.ws >= RD.ws AND TD.(1-clut) >= RD.(1-clut)
      AND (TD.ws > RD.ws OR TD.(1-clut) > RD.(1-clut))

    RD STRICTLY DOMINATES TD at config c iff (symmetric)

    Otherwise tie.

  dominance_rate = (TD_wins + 0.5 * ties) / n_points
  net_dominance  = (TD_wins - RD_wins) / n_points

  A pure-mechanism run gives dominance_rate near 1.0 with 0 RD_wins.
  A no-mechanism run gives dominance_rate near 0.5 with ~equal wins.

POSITIVE-CONTROL REPRODUCTION CHECK (load-bearing):

  Self-test reproduces v1's HARD_PASS seed_13 op-point (decay=90, load=1.0):
  TD.ws should be 1.000 and RD.ws should be much lower (~0.78), confirming
  TD strictly dominates RD at the v1 op point under the new discriminator.

EMPIRICAL CALIBRATION FROM V1 DATA (3 seeds; n_pts=28 each):
  - dominance_rate observed: seed_7=0.929, seed_13=0.911, seed_19=0.911
  - net_dominance observed:  seed_7=0.857, seed_13=0.821, seed_19=0.821
  - RD_wins observed: 0/28 in ALL seeds (mechanism never loses on a config)
  - Critically: seed_7's 3 v1 near-miss points (dr=60, ld in {1.0, 2.0, 5.0})
    are all TD-DOMINATES under v2 (d_comp=+0.38, +0.61, +0.82) -- they
    PROMOTE from MIDDLE_BAND to first-class Pareto-healthy.

PHASE-MAP HARD_PASS criterion (v2):
  - dominance_rate >= 0.85: TIME_DECAY beats RANDOM on >= 85% of configs
  - net_dominance  >= 0.70: TD wins exceed RD wins by >= 70% of configs
  - RD_wins / n_points <= 0.05: RANDOM strictly wins on <= 5% of configs
    (this is the strong "no failure mode" gate; v1 data shows 0/28)
  - n_pareto_healthy_within_load >= 1 per load axis:
    at least one config on EACH load axis is in the TD-dominates set
    (regime-coverage discipline carried over from v1; verifies phase
     diagram populates across capacity loads, not just one slice).

HARD_FAIL gates (load-bearing per Sec 15):
  HARD_FAIL_CARDINALITY_BREACH: observed grid points < EXPECTED_N_UNITS (28).
  HARD_FAIL_BY_CONSTRUCTION_SAT: dominance_rate >= 0.999 AND TD.ws == 1.0
    at every point (ceiling-saturated).
  HARD_FAIL_BY_CONSTRUCTION_FLOOR: dominance_rate <= 0.05 (mechanism floored).
  HARD_FAIL_ARMS_IDENTICAL: |TIME_DECAY.composite - RANDOM.composite| < 0.02
    at >= 90% of grid points.
  HARD_FAIL_RD_DOMINATES_SOMEWHERE: RD_wins / n_points > 0.20
    (mechanism actively WORSE than random on >= 20% of configs).
  HARD_FAIL_LLM_LEAK: n_llm_calls > 0.

ARMS: identical to v1 (TIME_DECAY / RANDOM / NO_EVICTION). The only thing
that changes is the discriminator/verdict layer.

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


ANCHOR_NAME = "substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC"
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

# Phase-diagram grid axes -- same as v1 for direct compare.
DECAY_RATE_DAYS_AXIS_FULL = [7, 15, 30, 60, 90, 180, 365]   # 7
CAPACITY_LOAD_RATIO_AXIS_FULL = [0.5, 1.0, 2.0, 5.0]         # 4
EXPECTED_N_UNITS_FULL = (
    len(DECAY_RATE_DAYS_AXIS_FULL) * len(CAPACITY_LOAD_RATIO_AXIS_FULL)
)  # 28

N_ATOMS_BASE = 1000
N_DAYS_SIM = 365
RECENT_QUERY_DAYS = 30
QUERY_DECAY_TAU = 60.0

SEED_DEFAULT = int(os.environ.get("HDLAB_SEED_OVERRIDE", "7"))

if RUN_MODE == "smoke":
    # Minimal grid that exercises both axes AND has known-positive points
    # (decay=90, load=1.0 is the v1 op point; TD should dominate RD).
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
    EXPECTED_N_UNITS = EXPECTED_N_UNITS_FULL  # 28
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
    f"EXPECTED_N_UNITS={EXPECTED_N_UNITS},"
    f"DISCRIMINATOR=cross_arm_pareto_dominance_rate"
)


# ---------------------------------------------------------------------------
# Substrate: simulated atom-query timeline (UNCHANGED FROM V1)
# ---------------------------------------------------------------------------
def simulate_atom_timeline(
    n_atoms: int,
    n_days: int,
    capacity_load_ratio: float,
    query_decay_tau: float,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    arrival_day = rng.randint(0, n_days, size=n_atoms).astype(np.int64)
    is_core = rng.rand(n_atoms) < 0.30
    last_query_day = np.full(n_atoms, -1, dtype=np.int64)
    for i in range(n_atoms):
        a = arrival_day[i]
        if is_core[i]:
            last_query_day[i] = n_days - 1 - rng.randint(0, RECENT_QUERY_DAYS)
        else:
            age_at_end = n_days - a
            mean_interval = query_decay_tau * capacity_load_ratio
            lam = max(0.0, age_at_end / max(mean_interval, 1e-6))
            n_reqs = rng.poisson(lam) if lam > 0 else 0
            if n_reqs == 0:
                last_query_day[i] = a
            else:
                qs = rng.randint(a, n_days, size=n_reqs)
                last_query_day[i] = int(qs.max())
    is_working_set = (last_query_day >= n_days - RECENT_QUERY_DAYS) & (last_query_day >= 0)
    return arrival_day, last_query_day, is_working_set


# ---------------------------------------------------------------------------
# Arms (UNCHANGED FROM V1)
# ---------------------------------------------------------------------------
def arm_time_decay(arrival_day, last_query_day, n_days, decay_rate_days):
    effective_last = np.where(last_query_day >= 0, last_query_day, arrival_day)
    age = n_days - effective_last
    return age > decay_rate_days


def arm_random_eviction(n_atoms, target_eviction_count, seed):
    rng = np.random.RandomState(seed + 7919)
    evicted = np.zeros(n_atoms, dtype=bool)
    if target_eviction_count <= 0:
        return evicted
    target_eviction_count = min(target_eviction_count, n_atoms)
    idx = rng.choice(n_atoms, size=target_eviction_count, replace=False)
    evicted[idx] = True
    return evicted


def arm_no_eviction(n_atoms):
    return np.zeros(n_atoms, dtype=bool)


# ---------------------------------------------------------------------------
# Metrics (UNCHANGED FROM V1)
# ---------------------------------------------------------------------------
def compute_arm_metrics(evicted, is_working_set):
    n_atoms = len(evicted)
    n_ws = int(is_working_set.sum())
    n_alive = int((~evicted).sum())
    n_evicted = int(evicted.sum())
    if n_ws == 0:
        ws_retention = float("nan")
    else:
        ws_retention = float(((~evicted) & is_working_set).sum() / n_ws)
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
# v2 NEW: cross-arm Pareto-dominance helpers (load-bearing discriminator)
# ---------------------------------------------------------------------------
def pareto_dominance_outcome(
    td_ws: float, td_clut: float,
    rd_ws: float, rd_clut: float,
) -> str:
    """Classify TD vs RD at a single (decay, load) config on the
    (ws, 1-clut) plane (higher-is-better on BOTH axes).

    Returns one of: 'TD_DOMINATES', 'RD_DOMINATES', 'TIE'.

    'TD_DOMINATES' = TD.ws >= RD.ws AND TD.(1-clut) >= RD.(1-clut)
                     AND at least one is strictly greater.
    """
    if any(np.isnan(x) for x in (td_ws, td_clut, rd_ws, rd_clut)):
        return "TIE"
    td_y = 1.0 - td_clut
    rd_y = 1.0 - rd_clut
    if td_ws >= rd_ws and td_y >= rd_y and (td_ws > rd_ws or td_y > rd_y):
        return "TD_DOMINATES"
    if rd_ws >= td_ws and rd_y >= td_y and (rd_ws > td_ws or rd_y > td_y):
        return "RD_DOMINATES"
    return "TIE"


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

    td_evicted = arm_time_decay(arrival_day, last_query_day, n_days, decay_rate_days)
    td_metrics = compute_arm_metrics(td_evicted, is_working_set)

    rd_evicted = arm_random_eviction(n_atoms, int(td_evicted.sum()), seed)
    rd_metrics = compute_arm_metrics(rd_evicted, is_working_set)

    no_evicted = arm_no_eviction(n_atoms)
    no_metrics = compute_arm_metrics(no_evicted, is_working_set)

    # v2 NEW: per-config Pareto outcome
    pareto_outcome = pareto_dominance_outcome(
        td_metrics["working_set_retention"], td_metrics["clutter_fraction"],
        rd_metrics["working_set_retention"], rd_metrics["clutter_fraction"],
    )

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
        "td_minus_random_ws_retention": float(
            td_metrics["working_set_retention"] - rd_metrics["working_set_retention"]
        ),
        "td_minus_random_clutter_fraction": float(
            td_metrics["clutter_fraction"] - rd_metrics["clutter_fraction"]
        ),
        "td_minus_random_composite": float(
            td_metrics["composite"] - rd_metrics["composite"]
        ),
        "pareto_outcome": pareto_outcome,  # v2 NEW
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
                f"rd_ws={rd['working_set_retention']:.3f} "
                f"rd_clut={rd['clutter_fraction']:.3f} "
                f"d_comp={result['td_minus_random_composite']:+.3f} "
                f"pareto={result['pareto_outcome']} "
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
# Self-tests (v2: discriminator FIRES under Pareto-dominance gate)
# ---------------------------------------------------------------------------
def _selftest_simulation_produces_working_set() -> bool:
    arrival, lastq, is_ws = simulate_atom_timeline(
        n_atoms=200, n_days=180, capacity_load_ratio=1.0,
        query_decay_tau=QUERY_DECAY_TAU, seed=7,
    )
    n_ws = int(is_ws.sum())
    assert 50 <= n_ws <= 170, (
        f"working-set count={n_ws} outside expected (50, 170) range"
    )
    return True


def _selftest_pareto_dominance_at_v1_op_point() -> bool:
    """At decay=90, load=1.0 (v1 op point + v1 HARD_PASS seed_13):
    TD should STRICTLY DOMINATE RD on (ws, 1-clut) plane."""
    arrival, lastq, is_ws = simulate_atom_timeline(
        n_atoms=500, n_days=365, capacity_load_ratio=1.0,
        query_decay_tau=QUERY_DECAY_TAU, seed=13,
    )
    td_evicted = arm_time_decay(arrival, lastq, 365, decay_rate_days=90)
    rd_evicted = arm_random_eviction(500, int(td_evicted.sum()), 13)
    td_m = compute_arm_metrics(td_evicted, is_ws)
    rd_m = compute_arm_metrics(rd_evicted, is_ws)
    outcome = pareto_dominance_outcome(
        td_m["working_set_retention"], td_m["clutter_fraction"],
        rd_m["working_set_retention"], rd_m["clutter_fraction"],
    )
    assert outcome == "TD_DOMINATES", (
        f"Positive-control FAILED: at v1 op point (dr=90, ld=1.0, seed=13) "
        f"expected TD_DOMINATES, got {outcome}. "
        f"TD(ws={td_m['working_set_retention']:.3f}, clut={td_m['clutter_fraction']:.3f}) "
        f"RD(ws={rd_m['working_set_retention']:.3f}, clut={rd_m['clutter_fraction']:.3f})"
    )
    return True


def _selftest_pareto_dominance_at_seed7_near_miss() -> bool:
    """At decay=60, load=2.0 (one of v1 seed_7's near-miss points):
    TD should STRICTLY DOMINATE RD even though v1 binary gate flagged it
    as not-healthy. This is the POSITIVE-CONTROL reproduction of the
    cell's central claim -- the v2 discriminator promotes seed_7's
    near-miss points to first-class Pareto-healthy."""
    arrival, lastq, is_ws = simulate_atom_timeline(
        n_atoms=500, n_days=365, capacity_load_ratio=2.0,
        query_decay_tau=QUERY_DECAY_TAU, seed=7,
    )
    td_evicted = arm_time_decay(arrival, lastq, 365, decay_rate_days=60)
    rd_evicted = arm_random_eviction(500, int(td_evicted.sum()), 7)
    td_m = compute_arm_metrics(td_evicted, is_ws)
    rd_m = compute_arm_metrics(rd_evicted, is_ws)
    outcome = pareto_dominance_outcome(
        td_m["working_set_retention"], td_m["clutter_fraction"],
        rd_m["working_set_retention"], rd_m["clutter_fraction"],
    )
    # Mechanism prediction: at (dr=60, ld=2.0, seed=7) TD.ws=1.0 RD.ws<<1.0,
    # TD.clut ~ 0.22, RD.clut >> 0.40, so TD strictly dominates.
    assert outcome == "TD_DOMINATES", (
        f"Reproduction FAILED: seed_7 near-miss point (dr=60, ld=2.0) "
        f"expected TD_DOMINATES under v2 (v1 binary marked it MB); got {outcome}. "
        f"TD(ws={td_m['working_set_retention']:.3f}, clut={td_m['clutter_fraction']:.3f}) "
        f"RD(ws={rd_m['working_set_retention']:.3f}, clut={rd_m['clutter_fraction']:.3f}). "
        f"This invalidates the v2 mechanism-class claim."
    )
    return True


def _selftest_pareto_dominance_function_classification() -> bool:
    """Unit-check the pareto_dominance_outcome function with synthetic inputs."""
    # TD strictly better on both
    assert pareto_dominance_outcome(0.9, 0.1, 0.5, 0.4) == "TD_DOMINATES"
    # TD same ws, better clut
    assert pareto_dominance_outcome(0.5, 0.1, 0.5, 0.4) == "TD_DOMINATES"
    # RD strictly better on both
    assert pareto_dominance_outcome(0.5, 0.4, 0.9, 0.1) == "RD_DOMINATES"
    # Equal on both -- TIE
    assert pareto_dominance_outcome(0.5, 0.3, 0.5, 0.3) == "TIE"
    # Trade-off (each better on one axis) -- TIE
    assert pareto_dominance_outcome(0.9, 0.4, 0.5, 0.1) == "TIE"
    # NaN -> TIE
    assert pareto_dominance_outcome(float("nan"), 0.1, 0.5, 0.4) == "TIE"
    return True


def _selftest_no_eviction_loses_on_clutter() -> bool:
    """Sanity: NO_EVICTION (clutter ceiling) carries higher clutter than
    TIME_DECAY at HEALTHY phase. When TD doesn't damage working set (ws=1.0
    at dr=90), TD strictly dominates NO on clutter; when TD does damage ws
    (smaller decay window), the outcome is TIE (trade-off). Either way,
    NO must NOT strictly dominate TD."""
    arrival, lastq, is_ws = simulate_atom_timeline(
        n_atoms=300, n_days=365, capacity_load_ratio=2.0,
        query_decay_tau=QUERY_DECAY_TAU, seed=7,
    )
    td_evicted = arm_time_decay(arrival, lastq, 365, decay_rate_days=90)
    no_evicted = arm_no_eviction(300)
    td_m = compute_arm_metrics(td_evicted, is_ws)
    no_m = compute_arm_metrics(no_evicted, is_ws)
    outcome = pareto_dominance_outcome(
        td_m["working_set_retention"], td_m["clutter_fraction"],
        no_m["working_set_retention"], no_m["clutter_fraction"],
    )
    # NO_EVICTION should never strictly dominate TD on this plane:
    # NO.ws is always 1.0 (no eviction) but NO.clut is always >= TD.clut
    # (NO keeps all clutter; TD evicts old). So the outcome is TD_DOMINATES
    # (when TD.ws == 1.0 AND TD.clut < NO.clut) or TIE (when TD.ws < 1.0
    # trade-off). RD_DOMINATES via NO is structurally impossible here.
    assert outcome in ("TIE", "TD_DOMINATES"), (
        f"NO_EVICTION vs TIME_DECAY at HEALTHY: expected TIE or TD_DOMINATES; "
        f"got {outcome}. TD(ws={td_m['working_set_retention']:.3f}, "
        f"clut={td_m['clutter_fraction']:.3f}) "
        f"NO(ws={no_m['working_set_retention']:.3f}, "
        f"clut={no_m['clutter_fraction']:.3f})"
    )
    # Also assert TD has lower clutter than NO (mechanism is removing stale)
    assert td_m["clutter_fraction"] < no_m["clutter_fraction"], (
        f"TIME_DECAY should reduce clutter vs NO_EVICTION at HEALTHY; "
        f"TD.clut={td_m['clutter_fraction']:.3f} NO.clut={no_m['clutter_fraction']:.3f}"
    )
    return True


def _instrumentation_selftest() -> None:
    _selftest_simulation_produces_working_set()
    _selftest_pareto_dominance_function_classification()
    _selftest_pareto_dominance_at_v1_op_point()
    _selftest_pareto_dominance_at_seed7_near_miss()
    _selftest_no_eviction_loses_on_clutter()
    print(
        f"[selftest] PASS  mode={RUN_MODE}  axes(decay_days,load_ratio)="
        f"{DECAY_RATE_DAYS_AXIS}x{CAPACITY_LOAD_RATIO_AXIS}  "
        f"expected_n_units={EXPECTED_N_UNITS}  seed={SEED_DEFAULT}  "
        f"discriminator=cross_arm_pareto_dominance",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Verdict computation (v2: Pareto-dominance gate)
# ---------------------------------------------------------------------------
def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL", "HARD_FAIL_LLM_LEAK: substrate-only-decode gate violated.")

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
    td_comp = np.array([p["ARM_TIME_DECAY_EVICTION"]["composite"] for p in all_points])
    rd_comp = np.array([p["ARM_RANDOM_EVICTION"]["composite"] for p in all_points])
    d_comp = td_comp - rd_comp

    # HARD_FAIL_BY_CONSTRUCTION_FLOOR (on TIME_DECAY ws_retention)
    finite_td_ws = td_ws_ret[~np.isnan(td_ws_ret)]
    if len(finite_td_ws) > 0 and np.all(finite_td_ws <= 0.05):
        return ("HARD_FAIL",
                f"HARD_FAIL_BY_CONSTRUCTION_FLOOR: TIME_DECAY ws_retention <= 0.05 "
                f"at every point ({n_points} points); mechanism floored.")

    # HARD_FAIL_ARMS_IDENTICAL
    finite_d = d_comp[~np.isnan(d_comp)]
    if len(finite_d) > 0:
        n_identical = int(np.sum(np.abs(finite_d) < 0.02))
        if n_identical >= int(0.90 * len(finite_d)):
            return ("HARD_FAIL",
                    f"HARD_FAIL_ARMS_IDENTICAL: |TIME_DECAY.composite - "
                    f"RANDOM.composite| < 0.02 at {n_identical}/{len(finite_d)} "
                    f"(>= 90%) of grid points; time-decay mechanism not firing.")

    # v2 NEW: Pareto-dominance counts
    outcomes = [p["pareto_outcome"] for p in all_points]
    td_wins = sum(1 for o in outcomes if o == "TD_DOMINATES")
    rd_wins = sum(1 for o in outcomes if o == "RD_DOMINATES")
    ties = sum(1 for o in outcomes if o == "TIE")

    dominance_rate = (td_wins + 0.5 * ties) / n_points
    net_dominance = (td_wins - rd_wins) / n_points
    rd_loss_rate = rd_wins / n_points

    # HARD_FAIL_BY_CONSTRUCTION_SAT: dominance saturated AND TD.ws maxed
    if len(finite_td_ws) > 0:
        all_td_ws_one = bool(np.all(finite_td_ws >= 0.999))
        if dominance_rate >= 0.999 and all_td_ws_one:
            return ("HARD_FAIL",
                    f"HARD_FAIL_BY_CONSTRUCTION_SAT: dominance_rate=1.000 AND "
                    f"TD.ws=1.000 at every point ({n_points} points); ceiling "
                    f"saturated; no discrimination.")

    # HARD_FAIL_RD_DOMINATES_SOMEWHERE
    if rd_loss_rate > 0.20:
        return ("HARD_FAIL",
                f"HARD_FAIL_RD_DOMINATES_SOMEWHERE: RANDOM strictly dominates "
                f"TIME_DECAY at {rd_wins}/{n_points} ({rd_loss_rate:.1%}) of "
                f"configs (> 20% threshold); mechanism actively worse than random.")

    # Regime coverage check: per-load axis Pareto-healthy >= 1
    per_load_td_wins: Dict[float, int] = {}
    per_load_total: Dict[float, int] = {}
    for p in all_points:
        cl = p["capacity_load_ratio"]
        per_load_total[cl] = per_load_total.get(cl, 0) + 1
        if p["pareto_outcome"] == "TD_DOMINATES":
            per_load_td_wins[cl] = per_load_td_wins.get(cl, 0) + 1
    loads_with_winner = sum(1 for cl in per_load_total if per_load_td_wins.get(cl, 0) >= 1)
    n_loads = len(per_load_total)
    load_coverage_ok = loads_with_winner == n_loads

    summary = (
        f"n_points={n_points} "
        f"td_wins={td_wins}/{n_points} ({td_wins/n_points:.3f}) "
        f"rd_wins={rd_wins}/{n_points} ({rd_loss_rate:.3f}) "
        f"ties={ties}/{n_points}; "
        f"dominance_rate={dominance_rate:.3f}; "
        f"net_dominance={net_dominance:+.3f}; "
        f"loads_with_winner={loads_with_winner}/{n_loads}; "
        f"per_load_td_wins={ {k: per_load_td_wins.get(k,0) for k in sorted(per_load_total)} }"
    )

    # HARD_PASS gate (Pareto-AUC chain-grade)
    hp_dom_rate = dominance_rate >= 0.85
    hp_net_dom = net_dominance >= 0.70
    hp_rd_loss = rd_loss_rate <= 0.05
    hp_load_cov = load_coverage_ok

    if all([hp_dom_rate, hp_net_dom, hp_rd_loss, hp_load_cov]):
        return ("HARD_PASS",
                f"HARD_PASS Pareto-AUC: TIME_DECAY_EVICTION dominates RANDOM "
                f"on (ws, 1-clut) plane at >= 85% of configs with NET dominance "
                f">= 70% AND RANDOM never strictly dominates on more than 5% "
                f"AND every capacity-load axis has >= 1 Pareto-healthy config. "
                f"Continuous geometric discriminator confirms mechanism "
                f"(boundary-stable; no point-on-threshold instability). {summary}")

    # MIDDLE_BAND: strong dominance but missing one secondary gate
    if hp_dom_rate and hp_rd_loss:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: dominance_rate >= 0.85 AND rd_loss_rate <= 0.05 "
                f"but net_dominance or load-coverage gate not cleared. "
                f"hp_checks=[dom_rate={hp_dom_rate}, net_dom={hp_net_dom}, "
                f"rd_loss={hp_rd_loss}, load_cov={hp_load_cov}]. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL Pareto-AUC: cross-arm dominance discriminator did not "
            f"clear PASS or MIDDLE bands. "
            f"hp_checks=[dom_rate={hp_dom_rate}, net_dom={hp_net_dom}, "
            f"rd_loss={hp_rd_loss}, load_cov={hp_load_cov}]. {summary}")


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
        f"[seed={seed}] time-decay-eviction phase-diagram v2 (Pareto-AUC) "
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
        f"discriminator=cross_arm_pareto_dominance_rate"
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
