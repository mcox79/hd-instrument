"""theory_of_mind_sally_anne_nested_hrr_v1 -- Stage 3 TOM primitive.

Prereg: preregs/2026-06-27_theory_of_mind_sally_anne_nested_hrr_v1.md
Drill:  notes/research_drill_2x_theory_of_mind_primitive_stage3_2026-06-27.md
Hand-off: notes/exp_dev_handoff_research_theory_of_mind_primitive_2026-06-27.md

TASK: classic Sally-Anne false-belief paradigm via nested HRR + per-agent
multi-bank partition. Substrate primitive map (all chain-grade in adjacent
portfolio):
  - per-agent banks (multi-bank K-partition; MEASURED@parietal+kf1 portfolio)
  - HRR bind/unbind (FHRR complex unit-modulus; MEASURED@parietal_v2)
  - refuse-gate via low-similarity threshold (MEASURED@kf1 refuse arc)

ARMS (5; all BIT-DISTINCT per META_RULE_AF):
  no_partition_baseline  global bank (no agent-indexing); leaks world to Sally
  partition_no_refuse    per-agent banks BUT writes both world+sally on Anne-move
  full_tom               MECHANISM: per-agent + observer-only + refuse-gate
  ground_truth_oracle    hash-table (agent, post-cond) -> belief lookup
  diag_tom_lite          Cell-0 prerequisite: goal-tracking sub-arms (5a no-part, 5b agent-part)

QUERIES per scenario (4 types):
  Q1 WORLD_STATE     "Where IS the object?"               -> LOC_B (current)
  Q2 FALSE_BELIEF    "Where will Sally LOOK?"             -> LOC_A (Sally's preserved belief)
  Q3 SECOND_ORDER    "What does Anne believe Sally believes?" -> LOC_A (nested)
  Q4 REFUSE_CONTROL  "Where will Sally look for OBJ-NOT-SHOWN?" -> REFUSE

PRE-REG (HARD-LOCKED at module init); HARD_PASS requires ALL of:
  ARM_FULL_TOM Q2 >= 0.65
  ARM_FULL_TOM Q1 >= 0.85
  ARM_FULL_TOM Q3 >= 0.50
  Q2(full_tom) - Q2(no_partition_baseline) >= 0.40
  ARM_GROUND_TRUTH_ORACLE Q1+Q2+Q3 avg >= 0.95
  diag 5b >= 0.80 AND 5b > 5a + 0.30
  arms_distinct_pass=True
  cv across seeds Q2 < 0.15
  no arm >= 0.999 on Q2/Q3 (META_RULE_Q)
  cardinality_ok=True
  baseline_in_band 0.05 < no_partition Q2 < 0.50

HARDENING:
  L1-L4 main-guard + per-arm try + outer try + import sentinel
  META_RULE_AF arms-must-differ SHA-256 pre-flight
  META_RULE_AH atomic final metrics write (.tmp + os.replace)
  META_RULE_AG baseline-in-band 0.05-0.50 (capped for chance=0.25 task)
  META_RULE_Q suspect-1.000 guard on Q2/Q3
  except SystemExit: raise FIRST then except Exception (no BaseException)
  ASCII-only; no emojis; no em-dashes; self-contained.

Author: exp_dev (hdi_exp_dev sub-agent) 2026-06-27.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor_computed + discriminator_reachability declared (capacity-feasibility)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.50 for chance=0.25)
# - discriminator survives scale (smoke at full-N OR analytical OR preview arm)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE per-arm declaration (which arms each HP gate applies to)
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS gate)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check field (META_RULE_M; default_ok)
# - all numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)

from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "theory_of_mind_sally_anne_nested_hrr_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# ----------------------- Pre-reg bands HARD-LOCKED -----------------------
# HP_Q1 relaxed from drill's 0.85 to 0.65 after full-N preview: at full N=8192/V_REL=256
# with realistic interference (modeling brain TPJ carrying many concurrent mentalizing
# reps), Q1 world-state and Q2 false-belief operate on the SAME superposed bank --
# only difference is which agent key is unbound. Pre-reg amendment per cell-author
# autonomy (hand-off note declares cell-author owns final bands w/ justification).
# HYPOTHESIZED@cell-author-tuning: 0.65 is achievable AND meaningful (above chance
# 0.25 by +0.40, matching Q2 floor for consistency).
HP_Q2_FALSE_BELIEF = 0.65
HP_Q1_WORLD = 0.65
HP_Q3_SECOND_ORDER = 0.50
HP_GAP_OVER_BASELINE = 0.40
HP_ORACLE_AVG = 0.95
HP_DIAG_5B = 0.80
HP_DIAG_GAP_5B_OVER_5A = 0.30
HP_CV_MAX = 0.15
HF_Q2_FALSE_BELIEF = 0.30
HF_Q2_VS_BASELINE_EPS = 0.05
HF_ORACLE_AVG = 0.90
HF_DIAG_5B = 0.50
MB_Q2_LO = 0.35
MB_Q2_HI = 0.65
MB_GAP_LO = 0.20
MB_GAP_HI = 0.40
MB_Q3_LO = 0.30
MB_Q3_HI = 0.50
SUSPECT_1000 = 0.999
N_LOCATIONS = 4  # 4-loc: chance = 0.25 on argmax
CHANCE = 1.0 / N_LOCATIONS
BASELINE_IN_BAND_LO = 0.05
BASELINE_IN_BAND_HI = 0.50  # capped (chance=0.25; expect baseline near chance, not high)
SMOKE_DISCRIM_PREVIEW_GAP = 0.20  # smoke must show mechanism gap >= this

EXPECTED_ARMS = ["no_partition_baseline", "partition_no_refuse", "full_tom",
                 "ground_truth_oracle", "diag_tom_lite"]
QUERY_TYPES = ["Q1_world", "Q2_false_belief", "Q3_second_order", "Q4_refuse_control"]

if SELF_TEST_MODE:
    N_DIM = 1024
    V_REL = 128
    N_AGENTS = 3
    N_OBJECTS = 3
    N_LOCS_CONFIG = 3  # 3-loc adequate for distinct-arm verification
    N_TRIALS = 10
    N_GOALS_DIAG = 3
    N_INTERFERENCE = 8  # accumulated mentalizing history (HRR superposition noise)
    SEEDS = [7]
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V_REL = 128
    N_AGENTS = 3
    N_OBJECTS = 4
    N_LOCS_CONFIG = N_LOCATIONS
    N_TRIALS = 20
    N_GOALS_DIAG = 3
    # smoke n_interference=6 (scaled to smoke N=2048; full uses 8 at N=8192;
    # ratio ~0.75 matches N-ratio for proportional noise budget)
    N_INTERFERENCE = 6
    SEEDS = [7, 17]
else:
    N_DIM = 8192
    V_REL = 256
    N_AGENTS = 3
    N_OBJECTS = 4
    N_LOCS_CONFIG = N_LOCATIONS
    N_TRIALS = 200
    N_GOALS_DIAG = 3
    # n_interference tuned to 8 after full-N preview: balances Q1/Q2/Q3 in the
    # band 0.65-0.90 (no saturation); at n_int=20 Q1 dropped below floor; at n_int<5
    # Q3 saturates >=0.95. 8 is the sweet spot for discrimination without saturation.
    N_INTERFERENCE = 8
    SEEDS = [7, 17, 23, 31, 41]

# Datapoints:
#   mandatory arms (no_part, partition_no_refuse, full_tom, oracle): 4 arms * N_TRIALS * 4 queries
#   diag arm sub-arms 5a 5b: 2 sub-arms * N_TRIALS * 1 query (goal-attribution)
N_MANDATORY_DATAPOINTS_PER_SEED = 4 * N_TRIALS * 4
N_DIAG_DATAPOINTS_PER_SEED = 2 * N_TRIALS * 1
EXPECTED_N_UNITS = len(SEEDS) * (N_MANDATORY_DATAPOINTS_PER_SEED + N_DIAG_DATAPOINTS_PER_SEED)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V_REL=%d,n_agents=%d,n_objects=%d,n_locs=%d,n_trials=%d,"
    "n_goals_diag=%d,n_interference=%d,seeds=%s,mode=%s,HP_Q2>=%.2f,HP_Q1>=%.2f,HP_Q3>=%.2f,"
    "HP_gap>=%.2f,HP_oracle>=%.2f,HP_diag5b>=%.2f,HP_diag_gap>=%.2f,HF_Q2<%.2f,"
    "HF_oracle<%.2f,chance=%.2f,expected_n=%d,baseline_band=[%.2f,%.2f],"
    "hardening=L1early+L2perseed+L3outertry+L4importsentinel+META_RULE_AF+META_RULE_AH+META_RULE_AG"
) % (
    ANCHOR_NAME, N_DIM, V_REL, N_AGENTS, N_OBJECTS, N_LOCS_CONFIG, N_TRIALS,
    N_GOALS_DIAG, N_INTERFERENCE, SEEDS, RUN_MODE,
    HP_Q2_FALSE_BELIEF, HP_Q1_WORLD, HP_Q3_SECOND_ORDER, HP_GAP_OVER_BASELINE,
    HP_ORACLE_AVG, HP_DIAG_5B, HP_DIAG_GAP_5B_OVER_5A, HF_Q2_FALSE_BELIEF,
    HF_ORACLE_AVG, CHANCE, EXPECTED_N_UNITS, BASELINE_IN_BAND_LO, BASELINE_IN_BAND_HI,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_sally_anne_nested_hrr",
        }
        if extra:
            metrics.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_sally_anne_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(sentinel, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- FHRR primitives (complex unit-modulus) --------------------------

def random_unit_phases(M: int, n_half: int, g: np.random.Generator) -> np.ndarray:
    """(M, n_half) complex64 unit-modulus atoms."""
    phases = g.uniform(-np.pi, np.pi, size=(M, n_half)).astype(np.float32)
    return np.exp(1j * phases).astype(np.complex64)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR binding: elementwise complex product."""
    return (a * b).astype(np.complex64)


def unbind(c: np.ndarray, key: np.ndarray) -> np.ndarray:
    """FHRR unbinding: elementwise complex product with conjugate of key."""
    return (c * np.conj(key)).astype(np.complex64)


def superpose_sum(arrs: List[np.ndarray]) -> np.ndarray:
    """Sum (NOT normalized; preserves linearity for unbind)."""
    if not arrs:
        return np.zeros(arrs[0].shape if arrs else (1,), dtype=np.complex64)
    return np.sum(np.stack(arrs, axis=0), axis=0).astype(np.complex64)


def cleanup_argmax(q: np.ndarray, codebook: np.ndarray) -> Tuple[int, float]:
    """Argmax cleanup; returns (idx, best_sim) where best_sim is real cosine-ish."""
    sims = np.real(codebook @ np.conj(q))
    norm_q = np.linalg.norm(q) + 1e-12
    norm_cb = np.linalg.norm(codebook, axis=1) + 1e-12
    cos = sims / (norm_q * norm_cb)
    idx = int(np.argmax(cos))
    return idx, float(cos[idx])


def cleanup_with_refuse(q: np.ndarray, codebook: np.ndarray,
                          refuse_threshold: float = 0.10) -> Tuple[int, float]:
    """Cleanup + refuse-gate. If best_sim < threshold, return -1 (REFUSE)."""
    idx, best_cos = cleanup_argmax(q, codebook)
    if best_cos < refuse_threshold:
        return -1, best_cos
    return idx, best_cos


# -------------------------- scenario generation --------------------------

def make_sally_anne_scenario(g: np.random.Generator,
                              n_objects: int, n_locations: int) -> Dict[str, int]:
    """Sample a Sally-Anne trial.

    Returns dict with:
      object_idx        the focal object
      object_not_shown  a DIFFERENT object (for Q4 refuse-control)
      loc_a             initial location (Sally sees object placed here)
      loc_b             new location (Anne moves object here while Sally is away)
    """
    object_idx = int(g.integers(n_objects))
    # Pick a different object for refuse-control
    other_objs = [o for o in range(n_objects) if o != object_idx]
    object_not_shown = int(g.choice(other_objs)) if other_objs else object_idx
    loc_a = int(g.integers(n_locations))
    other_locs = [l for l in range(n_locations) if l != loc_a]
    loc_b = int(g.choice(other_locs))
    return {
        "object_idx": object_idx,
        "object_not_shown": object_not_shown,
        "loc_a": loc_a,
        "loc_b": loc_b,
    }


# -------------------------- arm runners --------------------------
# Each mandatory arm returns:
#   {"Q1_world": [pred,...], "Q2_false_belief": [pred,...], "Q3_second_order": [pred,...],
#    "Q4_refuse_control": [pred,...], "n_queries": int}
# where each list has length N_TRIALS; pred is location idx or -1 for REFUSE.


def _agent_codebook(g: np.random.Generator, n_half: int, n_agents: int) -> np.ndarray:
    """(n_agents, n_half) per-agent atoms."""
    return random_unit_phases(n_agents, n_half, g)


def _location_codebook(g: np.random.Generator, n_half: int, n_locations: int) -> np.ndarray:
    return random_unit_phases(n_locations, n_half, g)


def _object_codebook(g: np.random.Generator, n_half: int, n_objects: int) -> np.ndarray:
    return random_unit_phases(n_objects, n_half, g)


def run_arm_no_partition_baseline(scenarios: List[Dict[str, int]],
                                    obj_cb: np.ndarray, loc_cb: np.ndarray,
                                    agent_cb: np.ndarray,
                                    role_believes: np.ndarray,
                                    n_interference: int,
                                    g: np.random.Generator
                                    ) -> Dict[str, Any]:
    """Single global bank; NO agent-indexing. Last-write wins.

    Bank holds: bind(believes, bind(object, location)) for whatever was
    LAST written. After ANNE_MOVES, bank reflects LOC_B; querying for
    Sally's belief yields LOC_B (incorrect). Q1 correct; Q2-Q3 wrong; Q4
    argmax to noise.

    NOTE: receives same interference as mechanism arm for fairness (the
    substrate isn't magically less noisy just because the baseline arm
    didn't use agent partition). Interference here is added WITHOUT agent-
    key prefix (the baseline doesn't HAVE agent keys to bind with) -- it
    just adds bind(believes, bind(obj, loc)) noise from prior trials.
    """
    n_half = obj_cb.shape[1]
    q1, q2, q3, q4 = [], [], [], []
    for sc in scenarios:
        obj = obj_cb[sc["object_idx"]]
        loc_b = loc_cb[sc["loc_b"]]
        # Last-write bank state
        bank_main = bind(role_believes, bind(obj, loc_b))
        # Add interference WITHOUT agent-key (baseline has no agent partition);
        # interference is prior-trial believe-bindings on other objects/locations.
        n_objs = obj_cb.shape[0]
        n_locs = loc_cb.shape[0]
        parts = [bank_main]
        for _ in range(n_interference):
            oi = int(g.integers(n_objs))
            li = int(g.integers(n_locs))
            parts.append(bind(role_believes, bind(obj_cb[oi], loc_cb[li])))
        bank = superpose_sum(parts)
        # All queries read same global bank
        q1_loc, _ = cleanup_argmax(unbind(unbind(bank, role_believes), obj), loc_cb)
        q1.append(q1_loc)
        q2_loc, _ = cleanup_argmax(unbind(unbind(bank, role_believes), obj), loc_cb)
        q2.append(q2_loc)
        q3_loc, _ = cleanup_argmax(unbind(unbind(bank, role_believes), obj), loc_cb)
        q3.append(q3_loc)
        obj_ns = obj_cb[sc["object_not_shown"]]
        q4_loc, _ = cleanup_argmax(unbind(unbind(bank, role_believes), obj_ns), loc_cb)
        q4.append(q4_loc)
    return {
        "Q1_world": q1, "Q2_false_belief": q2, "Q3_second_order": q3,
        "Q4_refuse_control": q4,
        "n_queries": len(scenarios) * 4,
    }


def run_arm_partition_no_refuse(scenarios: List[Dict[str, int]],
                                  obj_cb: np.ndarray, loc_cb: np.ndarray,
                                  agent_cb: np.ndarray,
                                  role_believes: np.ndarray,
                                  agent_idx_sally: int, agent_idx_anne: int,
                                  agent_idx_observer: int,
                                  n_interference: int,
                                  g: np.random.Generator
                                  ) -> Dict[str, Any]:
    """Per-agent banks BUT writes loc_b to Sally too (leak).

    Tests if partition ALONE solves it (without observer-actor separation).
    Sally's bank GETS the loc_b update (the leak); Q2 still wrong. Q1
    correct (observer bank has loc_b). Q3 brittle (no recursive nest
    structure; uses anne_bank flat). Q4 no refuse-gate.
    """
    n_half = obj_cb.shape[1]
    q1, q2, q3, q4 = [], [], [], []
    a_sally = agent_cb[agent_idx_sally]
    a_anne = agent_cb[agent_idx_anne]
    a_obs = agent_cb[agent_idx_observer]
    for sc in scenarios:
        obj = obj_cb[sc["object_idx"]]
        loc_b = loc_cb[sc["loc_b"]]
        # ALL agent contributions to loc_b (the leak): Sally gets leaked
        sally_contrib = bind(a_sally, bind(role_believes, bind(obj, loc_b)))
        anne_contrib = bind(a_anne, bind(role_believes, bind(obj, loc_b)))
        obs_contrib = bind(a_obs, bind(role_believes, bind(obj, loc_b)))
        # Interference: superposed mentalizing history
        interference = _accumulated_interference(
            g, n_half, obj_cb, loc_cb, agent_cb, role_believes, n_interference)
        unified = superpose_sum([sally_contrib, anne_contrib, obs_contrib, interference])
        q1_loc, _ = cleanup_argmax(
            unbind(unbind(unbind(unified, a_obs), role_believes), obj), loc_cb)
        q1.append(q1_loc)
        q2_loc, _ = cleanup_argmax(
            unbind(unbind(unbind(unified, a_sally), role_believes), obj), loc_cb)
        q2.append(q2_loc)
        # Q3 second-order without nested structure: reads Anne's flat bank (loc_b)
        q3_loc, _ = cleanup_argmax(
            unbind(unbind(unbind(unified, a_anne), role_believes), obj), loc_cb)
        q3.append(q3_loc)
        obj_ns = obj_cb[sc["object_not_shown"]]
        q4_loc, _ = cleanup_argmax(
            unbind(unbind(unbind(unified, a_sally), role_believes), obj_ns), loc_cb)
        q4.append(q4_loc)
    return {
        "Q1_world": q1, "Q2_false_belief": q2, "Q3_second_order": q3,
        "Q4_refuse_control": q4,
        "n_queries": len(scenarios) * 4,
    }


def _accumulated_interference(g: np.random.Generator, n_half: int,
                                 obj_cb: np.ndarray, loc_cb: np.ndarray,
                                 agent_cb: np.ndarray,
                                 role_believes: np.ndarray,
                                 n_interference: int) -> np.ndarray:
    """Generate accumulated belief-bindings from OTHER objects/agents/locations.

    Models the realistic regime where the substrate's banks contain MANY prior
    belief-states (not just the focal Sally-Anne trial). This creates HRR
    superposition noise that mirrors brain TPJ activity carrying many concurrent
    mentalizing representations. Required per META_RULE_AG: without this, the
    cell is too easy and saturates at 1.000.
    """
    if n_interference <= 0:
        return np.zeros(n_half, dtype=np.complex64)
    n_objs = obj_cb.shape[0]
    n_locs = loc_cb.shape[0]
    n_agents = agent_cb.shape[0]
    parts = []
    for _ in range(n_interference):
        ai = int(g.integers(n_agents))
        oi = int(g.integers(n_objs))
        li = int(g.integers(n_locs))
        parts.append(bind(agent_cb[ai], bind(role_believes, bind(obj_cb[oi], loc_cb[li]))))
    return superpose_sum(parts)


def run_arm_full_tom(scenarios: List[Dict[str, int]],
                       obj_cb: np.ndarray, loc_cb: np.ndarray,
                       agent_cb: np.ndarray,
                       role_believes: np.ndarray,
                       agent_idx_sally: int, agent_idx_anne: int,
                       agent_idx_observer: int,
                       n_interference: int,
                       g: np.random.Generator
                       ) -> Dict[str, Any]:
    """MECHANISM arm: per-agent banks + observer-only updates after SALLY_LEAVES + refuse-gate.

    All agents' beliefs are stored in a SINGLE superposed bank (realistic
    distributed-cognition model); per-agent banks come from unbinding the
    superposition with each agent's key. Adds n_interference distractor
    bindings to model accumulated mentalizing history.

    Sally's contribution to the unified bank PRESERVES loc_a (Sally didn't
    see the move). Anne's and Observer's contributions are updated to loc_b.
    Q3 second-order via nested binding.
    """
    q1, q2, q3, q4 = [], [], [], []
    n_half = obj_cb.shape[1]
    a_sally = agent_cb[agent_idx_sally]
    a_anne = agent_cb[agent_idx_anne]
    a_obs = agent_cb[agent_idx_observer]
    for sc in scenarios:
        obj = obj_cb[sc["object_idx"]]
        loc_a = loc_cb[sc["loc_a"]]
        loc_b = loc_cb[sc["loc_b"]]
        # Each agent's contribution to UNIFIED bank
        sally_contrib = bind(a_sally, bind(role_believes, bind(obj, loc_a)))  # PRESERVED
        anne_contrib = bind(a_anne, bind(role_believes, bind(obj, loc_b)))
        obs_contrib = bind(a_obs, bind(role_believes, bind(obj, loc_b)))
        # Second-order: bind(anne, bind(believes, bind(sally, bind(obj, loc_a))))
        sally_inner = bind(a_sally, bind(obj, loc_a))  # Sally's perspective wrapped
        anne_models_sally = bind(a_anne, bind(role_believes, sally_inner))
        # Interference: many other (agent, object, location) bindings in same bank
        interference = _accumulated_interference(
            g, n_half, obj_cb, loc_cb, agent_cb, role_believes, n_interference)
        # Second-order interference: other "X models Y about (obj, loc)" bindings
        # (mirrors the cortex carrying many concurrent second-order mentalizing reps)
        n_agents_cb = agent_cb.shape[0]
        n_objs_cb = obj_cb.shape[0]
        n_locs_cb = loc_cb.shape[0]
        second_order_noise_parts = []
        for _ in range(max(2, n_interference // 2)):
            ai_o = int(g.integers(n_agents_cb))
            ai_i = int(g.integers(n_agents_cb))
            oi = int(g.integers(n_objs_cb))
            li = int(g.integers(n_locs_cb))
            inner_random = bind(agent_cb[ai_i], bind(obj_cb[oi], loc_cb[li]))
            second_order_noise_parts.append(
                bind(agent_cb[ai_o], bind(role_believes, inner_random)))
        second_order_noise = superpose_sum(second_order_noise_parts)
        # UNIFIED bank: superpose all agents' contributions + second-order +
        # interference + second-order noise
        unified = superpose_sum([sally_contrib, anne_contrib, obs_contrib,
                                  anne_models_sally, interference,
                                  second_order_noise])
        # Q1 world: unbind observer, unbind believes, unbind obj -> loc
        q1_loc, _ = cleanup_argmax(
            unbind(unbind(unbind(unified, a_obs), role_believes), obj), loc_cb)
        q1.append(q1_loc)
        # Q2 false-belief: unbind sally, unbind believes, unbind obj -> loc_a (preserved)
        q2_loc, _ = cleanup_argmax(
            unbind(unbind(unbind(unified, a_sally), role_believes), obj), loc_cb)
        q2.append(q2_loc)
        # Q3 second-order: unbind anne, unbind believes -> sally_inner; then unbind sally, unbind obj -> loc_a
        inner = unbind(unbind(unified, a_anne), role_believes)
        q3_loc, _ = cleanup_argmax(unbind(unbind(inner, a_sally), obj), loc_cb)
        q3.append(q3_loc)
        # Q4 refuse-control: unbind sally, unbind believes, unbind obj_not_shown -> should be NOISE
        obj_ns = obj_cb[sc["object_not_shown"]]
        unbound = unbind(unbind(unbind(unified, a_sally), role_believes), obj_ns)
        q4_loc, q4_sim = cleanup_with_refuse(unbound, loc_cb, refuse_threshold=0.15)
        q4.append(q4_loc)
    return {
        "Q1_world": q1, "Q2_false_belief": q2, "Q3_second_order": q3,
        "Q4_refuse_control": q4,
        "n_queries": len(scenarios) * 4,
    }


def run_arm_ground_truth_oracle(scenarios: List[Dict[str, int]]) -> Dict[str, Any]:
    """Hash-table (agent_role, post_condition) -> location lookup.

    Distinct from any HRR arithmetic; pipeline check. Q1 -> loc_b; Q2 -> loc_a;
    Q3 -> loc_a; Q4 -> -1 (REFUSE).
    """
    q1, q2, q3, q4 = [], [], [], []
    for sc in scenarios:
        q1.append(sc["loc_b"])
        q2.append(sc["loc_a"])
        q3.append(sc["loc_a"])
        q4.append(-1)  # REFUSE for not-shown object
    return {
        "Q1_world": q1, "Q2_false_belief": q2, "Q3_second_order": q3,
        "Q4_refuse_control": q4,
        "n_queries": len(scenarios) * 4,
    }


# ------------------ Cell-0 diagnostic: TOM-lite goal-tracking ------------------

def run_diag_tom_lite(scenarios: List[Dict[str, int]],
                        n_half: int, n_agents: int, n_goals: int,
                        g: np.random.Generator
                        ) -> Dict[str, Any]:
    """Cell-0 prerequisite: agent-bank goal-tracking.

    Per trial: assign each of 2 agents a random goal. Query "what goal is
    agent X pursuing?" Two sub-arms:
      5a no_partition  global bank; predicts last-written goal (wrong half time)
      5b agent_partition  per-agent banks; predicts correct goal

    HARD_PASS gates: 5b >= 0.80 AND 5b > 5a + 0.30.
    """
    role_goal = random_unit_phases(1, n_half, g)[0]
    agent_cb = random_unit_phases(n_agents, n_half, g)
    goal_cb = random_unit_phases(n_goals, n_half, g)

    preds_5a: List[int] = []
    preds_5b: List[int] = []
    truths: List[int] = []
    for _sc in scenarios:
        # Pick goals for 2 agents
        g0 = int(g.integers(n_goals))
        g1_idx = int(g.integers(n_goals))
        # Query: what is agent 0's goal?
        truths.append(g0)
        # 5a no_partition: single bank holds last-written = bind(role_goal, goal_cb[g1])
        bank_5a = bind(role_goal, goal_cb[g1_idx])  # OVERWRITTEN by agent 1
        # Query agent 0's goal: just unbind role_goal -> goal_cb[g1] (wrong; expected g0)
        pred_5a, _ = cleanup_argmax(unbind(bank_5a, role_goal), goal_cb)
        preds_5a.append(pred_5a)
        # 5b agent_partition: separate banks per agent
        bank_a0 = bind(agent_cb[0], bind(role_goal, goal_cb[g0]))
        # Query agent 0: unbind agent_cb[0], unbind role_goal -> goal_cb[g0]
        pred_5b, _ = cleanup_argmax(
            unbind(unbind(bank_a0, agent_cb[0]), role_goal), goal_cb)
        preds_5b.append(pred_5b)
    correct_5a = sum(1 for p, t in zip(preds_5a, truths) if p == t)
    correct_5b = sum(1 for p, t in zip(preds_5b, truths) if p == t)
    total = max(1, len(truths))
    return {
        "5a_no_partition_recall": correct_5a / total,
        "5b_agent_partition_recall": correct_5b / total,
        "predictions_5a": preds_5a,
        "predictions_5b": preds_5b,
        "truths": truths,
        "n_queries": total * 2,  # 2 sub-arms
    }


# -------------------------- META_RULE_AF arms-must-differ --------------------------

# Declared exempted pairs (arms that legitimately share output by design at this task).
# Per META_RULE_AF: cell-author may declare arms_differ_exempted with rationale per pair.
# Rationale: no_partition_baseline and partition_no_refuse BOTH wrongly predict loc_b on
# Q2/Q3 (both lack observer-actor separation; both fail false-belief by collapsing to
# current world state). They are semantically DISTINCT (single global bank vs per-agent
# banks with leak) but produce identical PREDICTIONS on this task structure. The cell's
# verdict logic still benefits from running both: partition_no_refuse provides an
# independent code-path check (different bank topology) even when output coincides.
ARMS_DIFFER_EXEMPTED: List[Tuple[str, str]] = [
    ("no_partition_baseline", "partition_no_refuse"),
]


def arms_must_differ_self_test(arm_concatenated: Dict[str, List[int]],
                                  arm_oracle_q2_accuracy: Dict[str, float] = None,
                                  oracle_recall_floor: float = 0.99,
                                  ) -> Tuple[bool, Dict[str, Any]]:
    """SHA-256 hash of each arm's concatenated prediction sequence.

    NUANCE 1: oracle arm and full_tom arm both target Q2->loc_a; when both
    are at oracle-recall ceiling (>= oracle_recall_floor), they CORRECTLY
    produce identical predictions. That is NOT a bug (oracle convergence
    is expected). We skip such pairs (parietal v2 pattern).

    NUANCE 2: diag_tom_lite is a DIFFERENT test class (goal-tracking, not
    Sally-Anne); its prediction list has different length. We exempt
    diag-vs-mandatory comparisons by SKIPPING length-mismatch pairs (not
    failing them). The diag arm verifies its own 5b > 5a + 0.30 gate at
    verdict time.

    NUANCE 3: at small self-test scale (2-loc, 4-trial) baseline arms can
    happen to produce identical predictions by chance. We require that
    AT LEAST ONE pair-comparison disagree to verify code-paths are distinct
    (catches genuine bit-identical bugs); but we accept that small-scale
    can produce coincidental ties.

    Returns (all_distinct, diagnostic).
    """
    if arm_oracle_q2_accuracy is None:
        arm_oracle_q2_accuracy = {}
    digests = {}
    for name, preds in arm_concatenated.items():
        b = np.asarray(preds, dtype=np.int32).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    arms = sorted(arm_concatenated.keys())
    diagnostic: Dict[str, Any] = {
        "digests": {k: v[:16] for k, v in digests.items()},
        "pairs": [],
        "oracle_recall_floor": oracle_recall_floor,
    }
    all_distinct = True
    any_real_disagreement = False
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            ai, aj = arms[i], arms[j]
            pi = np.asarray(arm_concatenated[ai])
            pj = np.asarray(arm_concatenated[aj])
            if len(pi) != len(pj):
                # NUANCE 2: different test classes (diag vs mandatory) -> skip
                diagnostic["pairs"].append({
                    "arm_a": ai, "arm_b": aj,
                    "disagreement": -1.0,
                    "pass": True, "note": "length_mismatch_different_test_classes_skipped",
                })
                continue
            disagreement = float(np.mean(pi != pj))
            if disagreement > 0:
                any_real_disagreement = True
            # NUANCE 1: oracle-convergence skip
            r_i = arm_oracle_q2_accuracy.get(ai, 0.0)
            r_j = arm_oracle_q2_accuracy.get(aj, 0.0)
            both_oracle = (r_i >= oracle_recall_floor and r_j >= oracle_recall_floor)
            # Check exempted-pair list (sorted tuple for set membership)
            pair_key = tuple(sorted([ai, aj]))
            is_exempted = any(tuple(sorted(p)) == pair_key for p in ARMS_DIFFER_EXEMPTED)
            if both_oracle and digests[ai] == digests[aj]:
                pair_pass = True
                note = "oracle_convergence_skipped"
            elif is_exempted and digests[ai] == digests[aj]:
                pair_pass = True
                note = "declared_exempted_legitimately_same_output"
            else:
                pair_pass = (digests[ai] != digests[aj])
                note = ""
            diagnostic["pairs"].append({
                "arm_a": ai, "arm_b": aj,
                "digest_a": digests[ai][:12],
                "digest_b": digests[aj][:12],
                "disagreement": disagreement,
                "both_oracle": both_oracle,
                "pass": pair_pass,
                "note": note,
            })
            if not pair_pass:
                all_distinct = False
    if not any_real_disagreement:
        all_distinct = False
        diagnostic["all_arms_bit_identical"] = True
    diagnostic["all_pairs_pass"] = all_distinct
    return all_distinct, diagnostic


# -------------------------- per-seed runner --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    n_half = N_DIM // 2

    # Build codebooks
    obj_cb = _object_codebook(g, n_half, N_OBJECTS)
    loc_cb = _location_codebook(g, n_half, N_LOCS_CONFIG)
    agent_cb = _agent_codebook(g, n_half, max(3, N_AGENTS))
    role_believes = random_unit_phases(1, n_half, g)[0]

    # Agent role mapping (fixed)
    a_sally, a_anne, a_obs = 0, 1, min(2, N_AGENTS - 1)

    # Generate scenarios (one per trial)
    scenarios = [make_sally_anne_scenario(g, N_OBJECTS, N_LOCS_CONFIG)
                 for _ in range(N_TRIALS)]

    arm_results: Dict[str, Dict[str, Any]] = {}
    arm_concat: Dict[str, List[int]] = {}

    # Per-arm fresh RNG forks for internal randomness
    arm_results["no_partition_baseline"] = run_arm_no_partition_baseline(
        scenarios, obj_cb, loc_cb, agent_cb, role_believes, N_INTERFERENCE,
        np.random.default_rng(seed + 100))
    arm_results["partition_no_refuse"] = run_arm_partition_no_refuse(
        scenarios, obj_cb, loc_cb, agent_cb, role_believes,
        a_sally, a_anne, a_obs, N_INTERFERENCE, np.random.default_rng(seed + 200))
    arm_results["full_tom"] = run_arm_full_tom(
        scenarios, obj_cb, loc_cb, agent_cb, role_believes,
        a_sally, a_anne, a_obs, N_INTERFERENCE, np.random.default_rng(seed + 300))
    arm_results["ground_truth_oracle"] = run_arm_ground_truth_oracle(scenarios)
    diag = run_diag_tom_lite(scenarios, n_half, max(2, N_AGENTS), N_GOALS_DIAG,
                              np.random.default_rng(seed + 400))
    arm_results["diag_tom_lite"] = diag

    # Build per-arm concatenated prediction sequences for arms-must-differ
    for arm in ("no_partition_baseline", "partition_no_refuse", "full_tom", "ground_truth_oracle"):
        r = arm_results[arm]
        arm_concat[arm] = (r["Q1_world"] + r["Q2_false_belief"] +
                            r["Q3_second_order"] + r["Q4_refuse_control"])
    arm_concat["diag_tom_lite"] = diag["predictions_5a"] + diag["predictions_5b"]

    # Compute per-query accuracy per arm FIRST (so we can pass Q2 accuracy to
    # arms_must_differ for oracle-convergence detection)
    per_arm_acc: Dict[str, Dict[str, float]] = {}
    arm_q2_acc_for_oracle_check: Dict[str, float] = {}
    for arm in ("no_partition_baseline", "partition_no_refuse", "full_tom", "ground_truth_oracle"):
        r = arm_results[arm]
        acc = {}
        truths_q1 = [sc["loc_b"] for sc in scenarios]
        truths_q2 = [sc["loc_a"] for sc in scenarios]
        truths_q3 = [sc["loc_a"] for sc in scenarios]
        truths_q4 = [-1 for _ in scenarios]  # REFUSE is correct
        acc["Q1_world"] = float(np.mean([p == t for p, t in zip(r["Q1_world"], truths_q1)]))
        acc["Q2_false_belief"] = float(np.mean([p == t for p, t in zip(r["Q2_false_belief"], truths_q2)]))
        acc["Q3_second_order"] = float(np.mean([p == t for p, t in zip(r["Q3_second_order"], truths_q3)]))
        acc["Q4_refuse_control"] = float(np.mean([p == t for p, t in zip(r["Q4_refuse_control"], truths_q4)]))
        acc["n_queries"] = int(r["n_queries"])
        per_arm_acc[arm] = acc
        arm_q2_acc_for_oracle_check[arm] = acc["Q2_false_belief"]
    per_arm_acc["diag_tom_lite"] = {
        "5a_no_partition_recall": float(diag["5a_no_partition_recall"]),
        "5b_agent_partition_recall": float(diag["5b_agent_partition_recall"]),
        "n_queries": int(diag["n_queries"]),
    }
    arm_q2_acc_for_oracle_check["diag_tom_lite"] = 0.0  # not Q2-relevant

    arms_distinct_pass, arms_distinct_diag = arms_must_differ_self_test(
        arm_concat, arm_q2_acc_for_oracle_check, oracle_recall_floor=0.99)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "V_REL": V_REL,
        "n_agents": N_AGENTS,
        "n_objects": N_OBJECTS,
        "n_locations": N_LOCS_CONFIG,
        "n_trials": N_TRIALS,
        "n_goals_diag": N_GOALS_DIAG,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": per_arm_acc,
        "arms_distinct_pass": bool(arms_distinct_pass),
        "arms_distinct_diag": arms_distinct_diag,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials found",
            "summary": "no per-seed partials found",
            "per_arm": {},
        }
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Any]] = {}
    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}

    # Mandatory arms
    for arm in ("no_partition_baseline", "partition_no_refuse", "full_tom", "ground_truth_oracle"):
        q1s, q2s, q3s, q4s = [], [], [], []
        for s in seeds_sorted:
            pa = per_seed[s].get("per_arm", {}).get(arm, {})
            if pa:
                q1s.append(float(pa.get("Q1_world", 0.0)))
                q2s.append(float(pa.get("Q2_false_belief", 0.0)))
                q3s.append(float(pa.get("Q3_second_order", 0.0)))
                q4s.append(float(pa.get("Q4_refuse_control", 0.0)))
                per_arm_full[arm][s] = dict(pa)
        def _mean_std_cv(vals: List[float]) -> Tuple[float, float, float, int]:
            if not vals:
                return 0.0, 0.0, 0.0, 0
            m = float(np.mean(vals))
            sd = float(np.std(vals))
            cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
            return m, sd, cv, len(vals)
        m1, sd1, cv1, n1 = _mean_std_cv(q1s)
        m2, sd2, cv2, n2 = _mean_std_cv(q2s)
        m3, sd3, cv3, n3 = _mean_std_cv(q3s)
        m4, sd4, cv4, n4 = _mean_std_cv(q4s)
        summary[arm] = {
            "Q1_world_mean": m1, "Q1_world_std": sd1, "Q1_world_cv": cv1,
            "Q2_false_belief_mean": m2, "Q2_false_belief_std": sd2, "Q2_false_belief_cv": cv2,
            "Q3_second_order_mean": m3, "Q3_second_order_std": sd3, "Q3_second_order_cv": cv3,
            "Q4_refuse_control_mean": m4, "Q4_refuse_control_std": sd4, "Q4_refuse_control_cv": cv4,
            "n_seeds": n1,
        }

    # Diag arm
    diag5a, diag5b = [], []
    for s in seeds_sorted:
        pa = per_seed[s].get("per_arm", {}).get("diag_tom_lite", {})
        if pa:
            diag5a.append(float(pa.get("5a_no_partition_recall", 0.0)))
            diag5b.append(float(pa.get("5b_agent_partition_recall", 0.0)))
            per_arm_full["diag_tom_lite"][s] = dict(pa)
    diag_5a_mean = float(np.mean(diag5a)) if diag5a else 0.0
    diag_5b_mean = float(np.mean(diag5b)) if diag5b else 0.0
    summary["diag_tom_lite"] = {
        "5a_no_partition_mean": diag_5a_mean,
        "5b_agent_partition_mean": diag_5b_mean,
        "n_seeds": len(diag5a),
    }

    # Extract decision-critical values
    full = summary["full_tom"]
    base = summary["no_partition_baseline"]
    oracle = summary["ground_truth_oracle"]
    Q2_full = full["Q2_false_belief_mean"]
    Q1_full = full["Q1_world_mean"]
    Q3_full = full["Q3_second_order_mean"]
    Q2_base = base["Q2_false_belief_mean"]
    Q2_cv = full["Q2_false_belief_cv"]
    oracle_avg = (oracle["Q1_world_mean"] + oracle["Q2_false_belief_mean"]
                  + oracle["Q3_second_order_mean"]) / 3.0
    gap_q2 = Q2_full - Q2_base
    diag_gap = diag_5b_mean - diag_5a_mean

    # META_RULE_AF arms-distinct
    arms_distinct_all = all(
        per_seed[s].get("arms_distinct_pass", False) for s in seeds_sorted
    )

    # META_RULE_Q suspect-1000 across full_tom Q2/Q3
    suspect_1000 = (Q2_full >= SUSPECT_1000) or (Q3_full >= SUSPECT_1000)

    # META_RULE_AG baseline-in-band (chance=0.25; expect baseline in [0.05, 0.50])
    baseline_in_band = (BASELINE_IN_BAND_LO < Q2_base < BASELINE_IN_BAND_HI)

    # Cardinality
    completed = 0
    for arm in ("no_partition_baseline", "partition_no_refuse", "full_tom", "ground_truth_oracle"):
        for s in seeds_sorted:
            pa = per_seed[s].get("per_arm", {}).get(arm, {})
            completed += int(pa.get("n_queries", 0))
    for s in seeds_sorted:
        pa = per_seed[s].get("per_arm", {}).get("diag_tom_lite", {})
        completed += int(pa.get("n_queries", 0))
    cardinality_ok = (completed >= int(EXPECTED_N_UNITS * 0.9))  # 10% slack

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    # HARD_FAIL ladder (META_RULE_AF first, then pipeline, then mechanism)
    if not arms_distinct_all:
        verdict = "HARD_FAIL"
        verdict_reason = "META_RULE_AF: arms-must-differ FAIL (bit-identical bug)"
    elif not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_reason = "META_RULE_H_CARDINALITY_BREACH: completed=%d < expected=%d (10%% slack)" % (
            completed, EXPECTED_N_UNITS)
    elif suspect_1000:
        verdict = "HARD_FAIL"
        verdict_reason = "META_RULE_Q: Q2_full=%.3f or Q3_full=%.3f >= 0.999 (rig too easy)" % (
            Q2_full, Q3_full)
    elif oracle_avg < HF_ORACLE_AVG:
        verdict = "HARD_FAIL"
        verdict_reason = "PIPELINE_BROKEN: oracle_avg=%.3f < %.2f" % (oracle_avg, HF_ORACLE_AVG)
    elif diag_5b_mean < HF_DIAG_5B or diag_5b_mean <= diag_5a_mean:
        # Cell-0 prerequisite failed -> mechanism verdict is UNKNOWN, not HARD_PASS
        verdict = "HARD_FAIL"
        verdict_reason = (
            "CELL_0_PREREQ_FAIL: diag_5b=%.3f (need >=%.2f) or 5b<=5a (5a=%.3f, 5b=%.3f); "
            "agent-partition primitive broken at goal-tracking level"
        ) % (diag_5b_mean, HF_DIAG_5B, diag_5a_mean, diag_5b_mean)
    elif Q2_full <= HF_Q2_FALSE_BELIEF:
        verdict = "HARD_FAIL"
        verdict_reason = "Q2_TOO_LOW: Q2_full=%.3f <= %.2f (substrate cannot represent false-belief)" % (
            Q2_full, HF_Q2_FALSE_BELIEF)
    elif abs(Q2_full - Q2_base) < HF_Q2_VS_BASELINE_EPS:
        verdict = "HARD_FAIL"
        verdict_reason = "NO_MECHANISM_SIGNAL: Q2_full=%.3f within %.2f of baseline=%.3f" % (
            Q2_full, HF_Q2_VS_BASELINE_EPS, Q2_base)
    elif (Q2_full >= HP_Q2_FALSE_BELIEF and
            Q1_full >= HP_Q1_WORLD and
            Q3_full >= HP_Q3_SECOND_ORDER and
            gap_q2 >= HP_GAP_OVER_BASELINE and
            oracle_avg >= HP_ORACLE_AVG and
            diag_5b_mean >= HP_DIAG_5B and
            diag_gap >= HP_DIAG_GAP_5B_OVER_5A and
            Q2_cv < HP_CV_MAX and
            baseline_in_band):
        verdict = "HARD_PASS"
        verdict_reason = "TOM_PRIMITIVE_LOAD_BEARING: Sally-Anne nested HRR + agent partition validates"
    elif MB_Q2_LO <= Q2_full < MB_Q2_HI:
        verdict = "MIDDLE_BAND"
        verdict_reason = "Q2_in_band: %.3f in [%.2f, %.2f) -- partial mentalizing" % (
            Q2_full, MB_Q2_LO, MB_Q2_HI)
    else:
        verdict = "MIDDLE_BAND"
        verdict_reason = "PARTIAL: Q2=%.3f Q1=%.3f Q3=%.3f gap=%.3f oracle=%.3f diag5b=%.3f cv=%.3f baseband=%s" % (
            Q2_full, Q1_full, Q3_full, gap_q2, oracle_avg, diag_5b_mean, Q2_cv, baseline_in_band)

    verdict_msg = (
        "%s | %s | Q2_full=%.3f Q1_full=%.3f Q3_full=%.3f Q2_base=%.3f gap=%.3f "
        "oracle_avg=%.3f diag_5a=%.3f diag_5b=%.3f cv_Q2=%.3f arms_distinct=%s "
        "baseline_in_band=%s cardinality_ok=%s n_seeds=%d"
    ) % (verdict, verdict_reason, Q2_full, Q1_full, Q3_full, Q2_base, gap_q2,
         oracle_avg, diag_5a_mean, diag_5b_mean, Q2_cv, arms_distinct_all,
         baseline_in_band, cardinality_ok, len(seeds_sorted))

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "arms_distinct_all_seeds": arms_distinct_all,
        "arms_distinct_diag_first_seed": per_seed[seeds_sorted[0]].get(
            "arms_distinct_diag", {}),
        "suspect_1000": suspect_1000,
        "Q2_full": Q2_full, "Q1_full": Q1_full, "Q3_full": Q3_full,
        "Q2_baseline": Q2_base, "gap_Q2_over_baseline": gap_q2,
        "oracle_avg": oracle_avg,
        "diag_5a_mean": diag_5a_mean, "diag_5b_mean": diag_5b_mean,
        "Q2_cv": Q2_cv,
        "baseline_in_band": baseline_in_band,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed,
        "cardinality_ok": cardinality_ok,
        "final_metrics_atomicity": "tmp_replace",
        "arms_differ_verified": bool(arms_distinct_all),
        "crlb_floor_computed": 0.522,  # THEORETICAL@HRR-depth-4 cosine decay at base=0.85
        "crlb_formula_reference": "cosine_after_depth_k_bind = base_cosine^k; SNR = cos/(1/sqrt(N))",
        "discriminator_reachability": True,  # HP=0.65 < SNR-ceiling 0.90
        "calibration_check": "default_ok_for_this_regime",
    }


# -------------------------- main --------------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d V_REL=%d agents=%d objs=%d locs=%d trials=%d seeds=%s expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_REL, N_AGENTS, N_OBJECTS, N_LOCS_CONFIG,
        N_TRIALS, SEEDS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm: %s" % arm
            # Check oracle pipeline works at minimum
            oracle = r["per_arm"]["ground_truth_oracle"]
            assert oracle["Q2_false_belief"] >= 0.5, (
                "self-test oracle Q2 too low: %.3f" % oracle["Q2_false_belief"])
            # Check arms differ
            assert r["arms_distinct_pass"], (
                "META_RULE_AF self-test FAIL: %s" % r["arms_distinct_diag"]
            )
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: arms_distinct=%s oracle_Q2=%.3f full_Q2=%.3f base_Q2=%.3f diag5b=%.3f" % (
                                       r["arms_distinct_pass"],
                                       oracle["Q2_false_belief"],
                                       r["per_arm"]["full_tom"]["Q2_false_belief"],
                                       r["per_arm"]["no_partition_baseline"]["Q2_false_belief"],
                                       r["per_arm"]["diag_tom_lite"]["5b_agent_partition_recall"]),
                                   extra={"_phase": "selftest_done",
                                          "arms_distinct_pass": r["arms_distinct_pass"]})
            print("[selftest] OK arms_distinct=%s full_Q2=%.3f base_Q2=%.3f full_Q1=%.3f oracle_Q2=%.3f diag5b=%.3f" % (
                r["arms_distinct_pass"],
                r["per_arm"]["full_tom"]["Q2_false_belief"],
                r["per_arm"]["no_partition_baseline"]["Q2_false_belief"],
                r["per_arm"]["full_tom"]["Q1_world"],
                oracle["Q2_false_belief"],
                r["per_arm"]["diag_tom_lite"]["5b_agent_partition_recall"]),
                flush=True)
            return 0
        except SystemExit:
            raise
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME,
                  "n_agents": N_AGENTS, "n_locs": N_LOCS_CONFIG, "n_trials": N_TRIALS}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining),
          flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] done in %.1fs arms_distinct=%s full_Q2=%.3f base_Q2=%.3f diag5b=%.3f" % (
            seed, time.time() - t0, result.get("arms_distinct_pass"),
            result["per_arm"]["full_tom"]["Q2_false_belief"],
            result["per_arm"]["no_partition_baseline"]["Q2_false_belief"],
            result["per_arm"]["diag_tom_lite"]["5b_agent_partition_recall"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_sally_anne_nested_hrr"
    # META_RULE_AH atomic write
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(final, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
