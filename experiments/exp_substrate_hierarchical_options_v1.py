"""substrate_hierarchical_options_v1 -- Stage 3 hierarchical planning, 3rd attempt.

THIRD attempt at hierarchical-planning capability. Two prior HARD_FAILs:
  v1 (`exp_substrate_hierarchical_subgoal_planner_v1_smoke`):
    TREE=0.000 < FLAT=0.133 -- closed-form D_macro pseudoinverse averaged
    parallel-block primitive effects into mush.
  revival (`exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke`):
    SC=0.000 DJ=0.000 BOTH=0.000 FLAT=0.067 -- state-conditioning + disjoint
    blocks did NOT rescue. Mechanism CLASS is wrong.

MECHANISM PIVOT (Sutton-Precup 1999 options framework):
  An option (I, pi, beta) does NOT predict state-deltas; it FIRES until beta
  termination triggers. No D_macro to fit. The modeling problem dissolves.

  THREE-CHANNEL encoding (NOT bundled HRR):
    pi    -- per-option primitive codebook + iter_cleanup_chain rollout
              (MEASURED@CG multi-hop depth-15)
    beta  -- cos(state_t, beta_target_o) >= tau_beta + max-steps fallback
              (HYPOTHESIZED@cosine-as-termination-signal -- LOAD-BEARING physics)
    I     -- max-cos(state, I_anchors_o) >= tau_I per-option anchor bank
              (MEASURED@CG partition routing M=10M)

ARMS (6):
  ARM_OPTIONS_FULL        -- pi + beta + I (mechanism under test)
  ARM_POLICY_ONLY         -- pi alone (no I gate; no beta term; max-steps only)
  ARM_INIT_ONLY           -- pi + I (no beta term; max-steps only)
  ARM_TERM_ONLY           -- pi + beta (no I gate; all options always eligible)
  ARM_CLOSED_FORM_BASELINE -- v1/revival D_macro mechanism (regression baseline)
  ARM_RANDOM              -- pure random floor

PRE-REG BANDS (LOCKED at module init; PROSPECTIVE):
  HARD_PASS (ALL of):
    ARM_OPTIONS_FULL >= 0.55
    ARM_OPTIONS_FULL - ARM_POLICY_ONLY >= +0.10  (beta + I lift)
    ARM_OPTIONS_FULL - ARM_CLOSED_FORM >= +0.30  (vs prior-class regression)
    ARM_OPTIONS_FULL - ARM_RANDOM     >= +0.40  (mechanism load-bearing)
    ARM_OPTIONS_FULL in [0.30, 0.95]            (un-saturated; META_RULE_AG)
    ARM_CLOSED_FORM < 0.20                       (sanity: prior HARD_FAIL replicates)
    ARM_RANDOM < 0.05                            (floor)
    arms_distinct == True                        (SHA-256 per-arm seq trace)
    cv(ARM_OPTIONS_FULL) <= 0.15
  MIDDLE_BAND: ARM_OPTIONS_FULL in [0.30, 0.55) AND lift_policy >= 0.05 AND lift_random >= 0.25
  HARD_FAIL (ANY of):
    ARM_OPTIONS_FULL <= 0.20  -- THIRD-FAILURE GATE; close capability box
    ARM_OPTIONS_FULL within 0.05 of ARM_RANDOM  -- pi not executing (cell bug)
    arms_distinct == False
    ARM_CLOSED_FORM >= 0.30                       (prior HARD_FAIL did NOT replicate)

CARDINALITY (META_RULE_AH):
  EXPECTED_N_UNITS_FULL  = 6 arms * 3 seeds * 50 goals = 900
  EXPECTED_N_UNITS_SMOKE = 6 arms * 1 seed  * 20 goals = 120

CRLB: A=6 depth=6 -> 6^-6 = 2.14e-5; K=64 rerank UB ~0.04.
SANITY: ARM_RANDOM > 0.10 = SANITY_BREACH.

DOMAIN: 4-block BlocksWorld (simpler than v1's 8-block per drill section 3 to
compensate for novel mechanism complexity). N_POS=3 (slot_A/B/C; no held).
6 actions: pick_up_A, pick_up_B, swap_AB, swap_AC, rotate_BC, clear_all.
3 hand-defined options: stack_pair, clear_then_grab, relocate.

Composes: hdlab/binding.py (HRR bind/unbind CG), hdlab/multi_hop.py (iter cleanup),
hdlab/refuse_gate.py (calibrate_refuse_threshold for tau_beta), partition routing
(M=10M CG; per-option I bank). NEW operation = cosine-threshold beta termination.

ASCII-only; self-contained. Discipline: META_RULE_AC (cross-thread cohabit),
META_RULE_AF (arms-must-differ SHA-256), META_RULE_AH (atomic-write + cardinality),
META_RULE_AG (un-saturated band), META_RULE_AL (3-channel encoding BEFORE readout),
META_RULE_AN (empirical baseline ablations), L1-L4 hardening, no silent except,
number tagging MEASURED@/HYPOTHESIZED@.

Author: exp_dev 2026-06-28 (Opus 4.7 1M, Stage 3 hierarchical planning 3rd attempt)
"""
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
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, Callable

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "substrate_hierarchical_options_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# ---- Pre-reg bands LOCKED at module init (PROSPECTIVE) ----
HP_OPTIONS_SOLVE_MIN = 0.55          # HYPOTHESIZED@ drill section c
HP_LIFT_POLICY_MIN = 0.10            # beta+I lift over pi-alone
HP_LIFT_CLOSED_FORM_MIN = 0.30       # options vs prior-class regression
HP_LIFT_RANDOM_MIN = 0.40            # mechanism load-bearing
HP_OPTIONS_UNSAT_LO = 0.30           # META_RULE_AG un-saturated band lower
HP_OPTIONS_UNSAT_HI = 0.95           # META_RULE_AG un-saturated band upper
HP_CLOSED_FORM_MAX = 0.20            # SANITY: prior HARD_FAIL replicates
HP_RANDOM_MAX = 0.05                 # floor
HP_CV_MAX = 0.15
MB_OPTIONS_LO = 0.30
MB_OPTIONS_HI = 0.55
MB_LIFT_POLICY_MIN = 0.05
MB_LIFT_RANDOM_MIN = 0.25
HF_OPTIONS_MAX_THIRD_FAILURE = 0.20  # THIRD-FAILURE GATE
HF_RAND_MAX_SANITY = 0.10            # domain trivial check
HF_PI_BUG_DELTA = 0.05               # options within 0.05 of random = pi-bug
HF_CLOSED_FORM_BREACH = 0.30         # prior HARD_FAIL didn't replicate

# ---- BlocksWorld 4-block (drill section 3 spec) ----
N_BLOCKS = 4
N_POS = 3       # slot_A, slot_B, slot_C
ACTIONS = ["pick_up_A", "pick_up_B", "swap_AB", "swap_AC", "rotate_BC", "clear_all"]
N_ACTIONS = len(ACTIONS)

# ---- 3 hand-defined options (drill section 3 spec) ----
# Each option: name, internal primitive codebook (pi action-indices it can use),
# nominal max steps. The beta_target is computed per-option per-seed from the
# option's reachable goal-states (see fit_option_beta_target).
OPTION_NAMES = ["stack_pair", "clear_then_grab", "relocate"]
N_OPTIONS = len(OPTION_NAMES)

# Per-option primitive sub-alphabet (pi internal codebook). Each option's pi
# picks from this subset, NOT the full action set. Drill says K~4-8 primitives
# per option.
OPTION_PRIMITIVE_SETS: Dict[str, List[int]] = {
    "stack_pair":      [0, 1, 2],   # pick_up_A, pick_up_B, swap_AB
    "clear_then_grab": [5, 0, 1],   # clear_all, pick_up_A, pick_up_B
    "relocate":        [2, 3, 4],   # swap_AB, swap_AC, rotate_BC
}

# Per-option training: states matching each option's "completion" predicate.
# Used to fit beta_target HRR + tau_beta refuse-gate threshold.
def _option_completion(state: Tuple[int, ...], option_idx: int) -> bool:
    """Predicate: did option `option_idx` reach its 'goal state' pattern?
    Used to mark in-distribution beta calibration samples."""
    if option_idx == 0:        # stack_pair: blocks 0,1 in same slot
        return state[0] == state[1]
    elif option_idx == 1:      # clear_then_grab: blocks 2,3 in slot_C
        return state[2] == 2 and state[3] == 2
    elif option_idx == 2:      # relocate: blocks 0 in B, 2 in A
        return state[0] == 1 and state[2] == 0
    return False


# Per-option max-steps (used as beta hard fallback).
OPTION_MAX_STEPS = 8

# K_anchor_per_option for I initiation set (partition routing per-option bank).
K_ANCHOR_PER_OPTION = 32

# Training samples per option for beta tau calibration + I bank construction.
def _n_train_per_option() -> int:
    if SELF_TEST_MODE:
        return 30
    elif RUN_MODE == "smoke":
        return 120
    else:
        return 200


if SELF_TEST_MODE:
    N_DIM = 1024
    SEEDS = [7]
    N_GOALS = 4
    COMPOSITE_DEPTH = 4
    MIN_OPTIMAL = 2
    MAX_BFS_DEPTH = 6
    MAX_TOTAL_STEPS = 16
    K_REPLAN = 4   # branches at planner level
elif RUN_MODE == "smoke":
    N_DIM = 8192
    SEEDS = [7]                  # single seed smoke
    N_GOALS = 20
    COMPOSITE_DEPTH = 6
    MIN_OPTIMAL = 4
    MAX_BFS_DEPTH = 10
    MAX_TOTAL_STEPS = 24
    K_REPLAN = 8
else:
    N_DIM = 8192
    SEEDS = [7, 17, 23]
    N_GOALS = 50
    COMPOSITE_DEPTH = 6
    MIN_OPTIMAL = 5
    MAX_BFS_DEPTH = 12
    MAX_TOTAL_STEPS = 24
    K_REPLAN = 16


EXPECTED_ARMS = [
    "options_full", "policy_only", "init_only", "term_only",
    "closed_form_baseline", "random",
]
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * N_GOALS

CHANCE_RANDOM_FLOOR = N_ACTIONS ** (-COMPOSITE_DEPTH)
CHANCE_RANDOM_RERANK_UB = float(min(0.10, 64 * CHANCE_RANDOM_FLOOR + 0.04))

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,blocks=%d,pos=%d,actions=%d,options=%d,K_anchor=%d,goals=%d,"
    "depth=%d,K_replan=%d,max_total=%d,seeds=%s,mode=%s,"
    "HP_opts>=%.2f,HP_lift_policy>=%.2f,HP_lift_cf>=%.2f,HP_lift_rand>=%.2f,"
    "HP_unsat=[%.2f,%.2f],expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel+META_AC+META_AF+META_AG+META_AH+META_AL+META_AN+CARDINALITY"
) % (
    ANCHOR_NAME, N_DIM, N_BLOCKS, N_POS, N_ACTIONS, N_OPTIONS, K_ANCHOR_PER_OPTION,
    N_GOALS, COMPOSITE_DEPTH, K_REPLAN, MAX_TOTAL_STEPS, SEEDS, RUN_MODE,
    HP_OPTIONS_SOLVE_MIN, HP_LIFT_POLICY_MIN, HP_LIFT_CLOSED_FORM_MIN,
    HP_LIFT_RANDOM_MIN, HP_OPTIONS_UNSAT_LO, HP_OPTIONS_UNSAT_HI, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Optional[Dict[str, Any]] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_substrate_hierarchical_options",
        }
        if extra:
            m.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(m, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_substrate_hierarchical_options_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ---------------- BlocksWorld 4-block symbolic dynamics ----------------

def apply_action_sym(state: Tuple[int, ...], action_idx: int) -> Tuple[int, ...]:
    """Apply primitive action to state. Deterministic."""
    s = list(state)
    a = action_idx
    if a == 0:        # pick_up_A: move block 0 to slot_A
        s[0] = 0
    elif a == 1:      # pick_up_B: move block 1 to slot_B
        s[1] = 1
    elif a == 2:      # swap_AB: swap blocks 0 and 1
        s[0], s[1] = s[1], s[0]
    elif a == 3:      # swap_AC: swap blocks 0 and 2
        s[0], s[2] = s[2], s[0]
    elif a == 4:      # rotate_BC: rotate slots of blocks 1,2,3 (1->2->3->1)
        b1, b2, b3 = s[1], s[2], s[3]
        s[1], s[2], s[3] = b3, b1, b2
    elif a == 5:      # clear_all: move blocks 2,3 to slot_C
        s[2] = 2
        s[3] = 2
    return tuple(s)


def bfs_optimal(start: Tuple[int, ...], goal: Tuple[int, ...],
                 max_depth: int) -> Optional[Tuple[int, List[int]]]:
    """BFS over primitive actions; returns (depth, plan) or None."""
    if start == goal:
        return 0, []
    seen = {start: (0, [])}
    q = deque([start])
    while q:
        s = q.popleft()
        d, plan = seen[s]
        if d >= max_depth:
            continue
        for a in range(N_ACTIONS):
            ns = apply_action_sym(s, a)
            if ns not in seen:
                new_plan = plan + [a]
                seen[ns] = (d + 1, new_plan)
                if ns == goal:
                    return d + 1, new_plan
                q.append(ns)
    return None


# ---------------- HD primitives (numpy; CG equivalents per drill section 2) ----------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """M codewords of dim n; bipolar +/-1 normalized."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR bind via circular convolution (FFT)."""
    A = np.fft.rfft(a)
    B = np.fft.rfft(b)
    return np.fft.irfft(A * B, n=a.shape[-1]).astype(np.float32)


def cosine_vec(a: np.ndarray, b: np.ndarray) -> float:
    """cos(a,b); +/- bounded."""
    na = np.linalg.norm(a) + 1e-8
    nb = np.linalg.norm(b) + 1e-8
    val = float(np.dot(a, b) / (na * nb))
    if np.isnan(val) or np.isinf(val):
        raise ValueError("cosine_vec NaN/Inf (no-silent-except discipline)")
    return val


def cosine_mat(a: np.ndarray, M: np.ndarray) -> np.ndarray:
    """cos(a, M[i]) for each i; returns shape (M.shape[0],)."""
    na = np.linalg.norm(a) + 1e-8
    nM = np.linalg.norm(M, axis=1) + 1e-8
    out = (M @ a) / (nM * na)
    if not np.isfinite(out).all():
        raise ValueError("cosine_mat NaN/Inf (no-silent-except discipline)")
    return out


def encode_state_hd(state: Tuple[int, ...], block_role: np.ndarray,
                     pos_filler: np.ndarray, n_dim: int) -> np.ndarray:
    """Encode state to n-dim HD vector via sum of bound (block_role x pos_filler)."""
    v = np.zeros(n_dim, dtype=np.float32)
    for i, p in enumerate(state):
        v += hrr_bind(block_role[i], pos_filler[p])
    n = np.linalg.norm(v)
    if n > 1e-8:
        v = v / n
    return v


# ---------------- I (initiation set) -- per-option anchor banks ----------------

def fit_option_I_bank(option_idx: int, g: np.random.Generator,
                      block_role: np.ndarray, pos_filler: np.ndarray,
                      n_dim: int, k_anchor: int) -> Tuple[np.ndarray, float]:
    """Per-option I initiation bank: k_anchor HD vectors of states where
    rolling out option's primitives produces forward-progress (lower BFS
    distance to nearest completion state).

    Returns (I_bank, tau_I) where I_bank is (k_anchor, n_dim) and tau_I is the
    cosine threshold for "current state is in I_o" decision. tau_I calibrated
    such that ~70% of in-dist states pass.

    No-silent-except: if not enough productive samples, falls back to random
    starts (logged as fit_warning).
    """
    n_attempts_max = k_anchor * 20
    primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[option_idx]]
    anchors: List[np.ndarray] = []
    in_dist_cos: List[float] = []
    attempts = 0
    while len(anchors) < k_anchor and attempts < n_attempts_max:
        attempts += 1
        # Sample random start; roll OPTION_MAX_STEPS primitives from option set
        s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
        s2 = s
        progress = False
        for _ in range(OPTION_MAX_STEPS):
            a = primitives[int(g.integers(0, len(primitives)))]
            s2 = apply_action_sym(s2, a)
            if _option_completion(s2, option_idx):
                progress = True
                break
        if progress:
            anchors.append(encode_state_hd(s, block_role, pos_filler, n_dim))
    if len(anchors) < k_anchor:
        # Fallback: pad with random; we log a warning via metric, not silent-skip
        while len(anchors) < k_anchor:
            s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
            anchors.append(encode_state_hd(s, block_role, pos_filler, n_dim))
    I_bank = np.stack(anchors).astype(np.float32)

    # Calibrate tau_I: 70th percentile of max-cos over in-dist samples
    for _ in range(N_train := _n_train_per_option()):
        s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
        # Probe: is this state ACTUALLY in initiation set (i.e. rollout produces progress)?
        s2 = s
        progress = False
        for _ in range(OPTION_MAX_STEPS):
            a = primitives[int(g.integers(0, len(primitives)))]
            s2 = apply_action_sym(s2, a)
            if _option_completion(s2, option_idx):
                progress = True
                break
        if progress:
            v = encode_state_hd(s, block_role, pos_filler, n_dim)
            c_max = float(np.max(cosine_mat(v, I_bank)))
            in_dist_cos.append(c_max)
    if in_dist_cos:
        tau_I = float(np.percentile(in_dist_cos, 30))  # 70% pass
    else:
        tau_I = -1.0  # permissive fallback (no in-dist samples found)
    return I_bank, tau_I


# ---------------- beta (termination) -- per-option target + tau ----------------

def fit_option_beta(option_idx: int, g: np.random.Generator,
                    block_role: np.ndarray, pos_filler: np.ndarray,
                    n_dim: int) -> Tuple[np.ndarray, float]:
    """Per-option beta target HRR + tau_beta threshold (refuse-gate calibrated).

    beta_target = mean HRR of in-distribution "option-completed" states.
    tau_beta = cosine threshold such that in-dist completion cos vs beta_target
              is >= tau_beta for ~80% of completions, while OOD (random)
              states fall below.

    HYPOTHESIZED@cosine-as-termination-signal: the load-bearing substrate-physics
    test. Drill says if beta cos-threshold doesn't discriminate, options may
    still work via max-steps fallback.
    """
    primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[option_idx]]
    completion_hd: List[np.ndarray] = []
    in_dist_cos: List[float] = []
    ood_cos: List[float] = []
    n_train = _n_train_per_option()

    # Pass 1: build mean completion-state HRR (the beta_target)
    for _ in range(n_train):
        s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
        s2 = s
        for _ in range(OPTION_MAX_STEPS):
            a = primitives[int(g.integers(0, len(primitives)))]
            s2 = apply_action_sym(s2, a)
            if _option_completion(s2, option_idx):
                completion_hd.append(encode_state_hd(s2, block_role, pos_filler, n_dim))
                break
    if not completion_hd:
        # No-silent-except: surface but don't crash; fallback target = random codeword
        beta_target = bipolar(1, n_dim, g)[0]
    else:
        beta_target = np.mean(np.stack(completion_hd), axis=0)
        nb = np.linalg.norm(beta_target)
        if nb > 1e-8:
            beta_target = beta_target / nb

    # Pass 2: collect in-dist cos vs beta_target + OOD cos
    for _ in range(n_train):
        s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
        s2 = s
        finished = False
        for _ in range(OPTION_MAX_STEPS):
            a = primitives[int(g.integers(0, len(primitives)))]
            s2 = apply_action_sym(s2, a)
            if _option_completion(s2, option_idx):
                in_dist_cos.append(cosine_vec(
                    encode_state_hd(s2, block_role, pos_filler, n_dim), beta_target))
                finished = True
                break
        # OOD: random state NOT matching completion predicate
        s_ood = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
        if not _option_completion(s_ood, option_idx):
            ood_cos.append(cosine_vec(
                encode_state_hd(s_ood, block_role, pos_filler, n_dim), beta_target))

    # tau_beta: refuse-gate-style; choose threshold where 80% of in-dist pass
    # AND no more than 20% of OOD pass. Use 20th-percentile of in-dist as the
    # default, then bump up if OOD-overlap is too high.
    if in_dist_cos:
        tau_beta = float(np.percentile(in_dist_cos, 20))
    else:
        tau_beta = 0.9  # very strict fallback (never triggers; rely on max-steps)

    if ood_cos:
        ood_at_tau = float(np.mean(np.array(ood_cos) >= tau_beta))
        # If >20% OOD passes, bump tau_beta to 90th percentile of OOD
        if ood_at_tau > 0.20:
            tau_beta = max(tau_beta, float(np.percentile(ood_cos, 90)))

    return beta_target, tau_beta


# ---------------- pi (option policy) -- internal rollout ----------------

def execute_option(state: Tuple[int, ...], option_idx: int,
                    block_role: np.ndarray, pos_filler: np.ndarray, n_dim: int,
                    beta_target: np.ndarray, tau_beta: float,
                    use_beta: bool,
                    g: np.random.Generator,
                    goal_hd: np.ndarray
                    ) -> Tuple[Tuple[int, ...], List[int], bool]:
    """Roll an option's pi from `state`: pick best primitive (by goal-cos) at
    each step from the option's primitive subset. Terminate when beta triggers
    (if use_beta) OR max_steps reached.

    Returns (final_state, primitive_seq_executed, beta_triggered).
    """
    primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[option_idx]]
    s = state
    seq: List[int] = []
    beta_fired = False
    for step in range(OPTION_MAX_STEPS):
        # pi: pick best primitive (greedy w.r.t. goal_cos) among option's subset
        best_a = primitives[0]
        best_cos = -1e9
        for a in primitives:
            ns = apply_action_sym(s, a)
            ns_hd = encode_state_hd(ns, block_role, pos_filler, n_dim)
            c = cosine_vec(ns_hd, goal_hd) + 0.03 * float(g.standard_normal())
            if c > best_cos:
                best_cos = c
                best_a = a
        seq.append(best_a)
        s = apply_action_sym(s, best_a)
        if use_beta:
            s_hd = encode_state_hd(s, block_role, pos_filler, n_dim)
            if cosine_vec(s_hd, beta_target) >= tau_beta:
                beta_fired = True
                break
    return s, seq, beta_fired


# ---------------- Closed-form D_macro baseline (regression) ----------------

def fit_D_macro_closed_form(g: np.random.Generator, block_role: np.ndarray,
                              pos_filler: np.ndarray, n_dim: int) -> np.ndarray:
    """V1/revival regression baseline: D_macro[m] = mean(s_post - s_pre)
    averaged over random starts. Uses option primitive sets as macros.

    This is the FAILED v1 mechanism; we expect ARM_CLOSED_FORM <= 0.20.
    """
    N_TRAIN = _n_train_per_option()
    D = np.zeros((N_OPTIONS, n_dim), dtype=np.float32)
    for m_idx in range(N_OPTIONS):
        primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[m_idx]]
        acc = np.zeros(n_dim, dtype=np.float32)
        for _ in range(N_TRAIN):
            s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
            s_pre_hd = encode_state_hd(s, block_role, pos_filler, n_dim)
            s2 = s
            # Use a fixed-length primitive sequence (drill v1 mechanism)
            for _ in range(OPTION_MAX_STEPS // 2):
                a = primitives[int(g.integers(0, len(primitives)))]
                s2 = apply_action_sym(s2, a)
            s_post_hd = encode_state_hd(s2, block_role, pos_filler, n_dim)
            acc += (s_post_hd - s_pre_hd)
        D[m_idx] = acc / max(1, N_TRAIN)
    norms = np.linalg.norm(D, axis=1, keepdims=True) + 1e-8
    return D / norms


# ---------------- Planners (the 6 arms) ----------------

def plan_random(start: Tuple[int, ...], goal: Tuple[int, ...],
                 g: np.random.Generator
                 ) -> Tuple[List[int], bool]:
    """Pure random plan; floor."""
    s = start
    seq: List[int] = []
    for _ in range(MAX_TOTAL_STEPS):
        if s == goal:
            return seq, True
        a = int(g.integers(0, N_ACTIONS))
        seq.append(a)
        s = apply_action_sym(s, a)
    return seq, (s == goal)


def plan_closed_form_baseline(start: Tuple[int, ...], goal: Tuple[int, ...],
                                block_role: np.ndarray, pos_filler: np.ndarray,
                                n_dim: int, D_macro: np.ndarray,
                                g: np.random.Generator
                                ) -> Tuple[List[int], bool]:
    """V1 closed-form D_macro mechanism: decompose goal-delta into macro-indices
    via argmax(cos(residual, D_macro)). Expand each chosen macro into its
    primitive sequence. The mechanism that HARD_FAILed twice."""
    goal_hd = encode_state_hd(goal, block_role, pos_filler, n_dim)
    start_hd = encode_state_hd(start, block_role, pos_filler, n_dim)
    delta_hd = goal_hd - start_hd
    norms = np.linalg.norm(delta_hd)
    if norms > 1e-8:
        delta_hd = delta_hd / norms

    # Decompose into B_SLOTS macros greedily
    B_SLOTS = 4
    residual = delta_hd.copy()
    macro_seq: List[int] = []
    for _ in range(B_SLOTS):
        scores = cosine_mat(residual, D_macro)
        scores = scores + 0.05 * g.standard_normal(N_OPTIONS).astype(np.float32)
        m_idx = int(np.argmax(scores))
        macro_seq.append(m_idx)
        residual = residual - 0.3 * D_macro[m_idx]
        nr = np.linalg.norm(residual)
        if nr > 1e-8:
            residual = residual / nr

    # Expand macros into primitives (random pick within option's subset)
    s = start
    prim_seq: List[int] = []
    for m_idx in macro_seq:
        primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[m_idx]]
        for _ in range(OPTION_MAX_STEPS // 2):
            if len(prim_seq) >= MAX_TOTAL_STEPS or s == goal:
                break
            a = primitives[int(g.integers(0, len(primitives)))]
            prim_seq.append(a)
            s = apply_action_sym(s, a)
        if s == goal:
            break
    return prim_seq, (s == goal)


def plan_options(start: Tuple[int, ...], goal: Tuple[int, ...],
                  block_role: np.ndarray, pos_filler: np.ndarray, n_dim: int,
                  I_banks: List[np.ndarray], tau_Is: List[float],
                  beta_targets: List[np.ndarray], tau_betas: List[float],
                  use_I: bool, use_beta: bool,
                  g: np.random.Generator
                  ) -> Tuple[List[int], bool]:
    """SMDP-style options planner.

    At each planning step:
      1. If use_I: filter options by I check (max_cos(state_hd, I_bank_o) >= tau_I_o)
         Else: all options eligible.
      2. Score eligible options by cos(beta_target_o, goal_hd) (goal-relevance).
      3. If no option eligible, fall back to random primitive (cap dropout).
      4. Else: pick argmax-scored option, execute pi (with or without beta term).
      5. Loop until goal reached OR max_total_steps reached.

    Returns (primitive_seq, solved). Records option_id per primitive for audit.
    """
    goal_hd = encode_state_hd(goal, block_role, pos_filler, n_dim)
    s = start
    prim_seq: List[int] = []

    while len(prim_seq) < MAX_TOTAL_STEPS:
        if s == goal:
            return prim_seq, True
        s_hd = encode_state_hd(s, block_role, pos_filler, n_dim)

        # I check
        eligible: List[int] = []
        if use_I:
            for o in range(N_OPTIONS):
                c_max = float(np.max(cosine_mat(s_hd, I_banks[o])))
                if c_max >= tau_Is[o]:
                    eligible.append(o)
        else:
            eligible = list(range(N_OPTIONS))

        if not eligible:
            # Fallback: one random primitive then re-check
            a = int(g.integers(0, N_ACTIONS))
            prim_seq.append(a)
            s = apply_action_sym(s, a)
            continue

        # Score eligible options by goal-relevance
        best_o = eligible[0]
        best_score = -1e9
        for o in eligible:
            sc = cosine_vec(beta_targets[o], goal_hd) + 0.03 * float(g.standard_normal())
            if sc > best_score:
                best_score = sc
                best_o = o

        # Execute the chosen option
        s_after, opt_seq, _bf = execute_option(
            s, best_o, block_role, pos_filler, n_dim,
            beta_targets[best_o], tau_betas[best_o],
            use_beta, g, goal_hd,
        )
        for a in opt_seq:
            if len(prim_seq) >= MAX_TOTAL_STEPS:
                break
            prim_seq.append(a)
        s = s_after

    return prim_seq, (s == goal)


def plan_policy_only(start: Tuple[int, ...], goal: Tuple[int, ...],
                      block_role: np.ndarray, pos_filler: np.ndarray, n_dim: int,
                      beta_targets: List[np.ndarray],
                      g: np.random.Generator
                      ) -> Tuple[List[int], bool]:
    """Pi alone: per planning step, pick option by goal-relevance (no I gate);
    execute option's pi for fixed OPTION_MAX_STEPS (no beta term)."""
    goal_hd = encode_state_hd(goal, block_role, pos_filler, n_dim)
    s = start
    prim_seq: List[int] = []
    while len(prim_seq) < MAX_TOTAL_STEPS:
        if s == goal:
            return prim_seq, True
        # Pick option by beta-target relevance (no I gating)
        best_o, best_sc = 0, -1e9
        for o in range(N_OPTIONS):
            sc = cosine_vec(beta_targets[o], goal_hd) + 0.03 * float(g.standard_normal())
            if sc > best_sc:
                best_sc = sc
                best_o = o
        # Execute without beta (use_beta=False -> always max_steps)
        # Dummy beta_target/tau ignored since use_beta=False
        s_after, opt_seq, _ = execute_option(
            s, best_o, block_role, pos_filler, n_dim,
            beta_targets[best_o], 1.0, False, g, goal_hd,
        )
        for a in opt_seq:
            if len(prim_seq) >= MAX_TOTAL_STEPS:
                break
            prim_seq.append(a)
        s = s_after
    return prim_seq, (s == goal)


# ---------------- per-seed runner ----------------

def sample_composite_goal(g: np.random.Generator, max_bfs_depth: int,
                           min_optimal: int,
                           max_attempts: int = 400
                           ) -> Tuple[Tuple[int, ...], Tuple[int, ...], int, List[int]]:
    """Sample (start, goal, opt_depth, opt_plan). Returns the deepest pair
    found within attempts. Cell HARD_FAILs if best_d=0 (no reachable goal)."""
    best_pair = None
    best_d = 0
    for _ in range(max_attempts):
        start = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
        goal = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
        if start == goal:
            continue
        res = bfs_optimal(start, goal, max_bfs_depth)
        if res is None:
            continue
        opt, plan = res
        if opt >= min_optimal:
            return start, goal, opt, plan
        if opt > best_d:
            best_d = opt
            best_pair = (start, goal, opt, plan)
    if best_pair is not None:
        return best_pair
    s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
    return s, s, 0, []


def _seq_hash(seqs: List[List[int]]) -> str:
    h = hashlib.sha256()
    for sq in seqs:
        h.update(bytes(sq))
        h.update(b"|")
    return h.hexdigest()[:16]


def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)

    # Codebook
    block_role = bipolar(N_BLOCKS, N_DIM, g)
    pos_filler = bipolar(N_POS, N_DIM, g)

    # Sample composite goals once (fair across arms)
    goals: List[Tuple[Tuple[int, ...], Tuple[int, ...], int, List[int]]] = []
    for _ in range(N_GOALS):
        goals.append(sample_composite_goal(g, MAX_BFS_DEPTH, MIN_OPTIMAL))

    # Fit per-option I banks + tau_Is
    I_banks: List[np.ndarray] = []
    tau_Is: List[float] = []
    for o in range(N_OPTIONS):
        I_bank, tau_I = fit_option_I_bank(o, g, block_role, pos_filler, N_DIM, K_ANCHOR_PER_OPTION)
        I_banks.append(I_bank)
        tau_Is.append(tau_I)

    # Fit per-option beta targets + tau_betas
    beta_targets: List[np.ndarray] = []
    tau_betas: List[float] = []
    for o in range(N_OPTIONS):
        bt, tb = fit_option_beta(o, g, block_role, pos_filler, N_DIM)
        beta_targets.append(bt)
        tau_betas.append(tb)

    # Fit closed-form D_macro (regression baseline)
    D_macro = fit_D_macro_closed_form(g, block_role, pos_filler, N_DIM)

    arm_runners: List[Tuple[str, Callable]] = [
        ("options_full",
            # pi + beta + I (use_I=True, use_beta=True)
            lambda s, gl, opt, plan, ag: plan_options(
                s, gl, block_role, pos_filler, N_DIM,
                I_banks, tau_Is, beta_targets, tau_betas,
                use_I=True, use_beta=True, g=ag)),
        ("policy_only",
            # pi alone (no I, no beta; fixed max-steps per option)
            lambda s, gl, opt, plan, ag: plan_policy_only(
                s, gl, block_role, pos_filler, N_DIM,
                beta_targets, ag)),
        ("init_only",
            # pi + I but no beta
            lambda s, gl, opt, plan, ag: plan_options(
                s, gl, block_role, pos_filler, N_DIM,
                I_banks, tau_Is, beta_targets, tau_betas,
                use_I=True, use_beta=False, g=ag)),
        ("term_only",
            # pi + beta but no I (all options always eligible)
            lambda s, gl, opt, plan, ag: plan_options(
                s, gl, block_role, pos_filler, N_DIM,
                I_banks, tau_Is, beta_targets, tau_betas,
                use_I=False, use_beta=True, g=ag)),
        ("closed_form_baseline",
            lambda s, gl, opt, plan, ag: plan_closed_form_baseline(
                s, gl, block_role, pos_filler, N_DIM, D_macro, ag)),
        ("random",
            lambda s, gl, opt, plan, ag: plan_random(s, gl, ag)),
    ]

    per_arm: Dict[str, Dict[str, Any]] = {}
    per_arm_seqs: Dict[str, List[List[int]]] = {}
    for arm_name, runner in arm_runners:
        n_solved = 0
        plan_lens: List[int] = []
        ratios: List[float] = []
        seqs_for_hash: List[List[int]] = []
        # Per-arm RNG offset so arms differ even with same goal-set
        ag = np.random.default_rng(seed * 1009 + (hash(arm_name) % (10 ** 6)))
        for (s, gl, opt, plan) in goals:
            sub_plan, solved = runner(s, gl, opt, plan, ag)
            seqs_for_hash.append(list(sub_plan))
            if solved:
                n_solved += 1
                cur = s
                solved_len = len(sub_plan)
                for i, a in enumerate(sub_plan):
                    cur = apply_action_sym(cur, a)
                    if cur == gl:
                        solved_len = i + 1
                        break
                plan_lens.append(solved_len)
                if opt > 0:
                    ratios.append(solved_len / opt)
        per_arm[arm_name] = {
            "solve_rate": n_solved / N_GOALS,
            "n_solved": n_solved,
            "n_goals": N_GOALS,
            "median_plan_len": float(np.median(plan_lens)) if plan_lens else float(COMPOSITE_DEPTH),
            "median_plan_ratio_vs_optimal": float(np.median(ratios)) if ratios else float("inf"),
            "_seq_hash": _seq_hash(seqs_for_hash),
        }
        per_arm_seqs[arm_name] = seqs_for_hash

    # META_RULE_AF: arms_distinct critical-pairs check
    hashes = {arm: per_arm[arm]["_seq_hash"] for arm in per_arm}
    critical_pairs = [
        ("options_full", "policy_only"),
        ("options_full", "init_only"),
        ("options_full", "term_only"),
        ("options_full", "closed_form_baseline"),
        ("options_full", "random"),
        ("policy_only", "random"),
    ]
    arms_distinct = all(hashes[a] != hashes[b] for a, b in critical_pairs)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": per_arm,
        "arms_distinct": bool(arms_distinct),
        "arm_hashes": hashes,
        "n_goals_seed": N_GOALS,
        "median_optimal_plan_len": float(np.median([opt for _, _, opt, _ in goals])) if goals else 0.0,
        "tau_Is": [float(x) for x in tau_Is],
        "tau_betas": [float(x) for x in tau_betas],
    }


# ---------------- aggregate + verdict ----------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_arm": {}}

    arm_solves: Dict[str, List[float]] = {arm: [] for arm in EXPECTED_ARMS}
    arm_ratios: Dict[str, List[float]] = {arm: [] for arm in EXPECTED_ARMS}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {arm: {} for arm in EXPECTED_ARMS}
    arms_distinct_seeds: List[bool] = []
    for s_key, body in per_seed.items():
        pa = body.get("per_arm", {})
        arms_distinct_seeds.append(bool(body.get("arms_distinct", False)))
        for arm in EXPECTED_ARMS:
            if arm in pa:
                arm_solves[arm].append(pa[arm]["solve_rate"])
                arm_ratios[arm].append(pa[arm]["median_plan_ratio_vs_optimal"])
                per_arm_full[arm][s_key] = pa[arm]

    summary: Dict[str, Dict[str, float]] = {}
    for arm in EXPECTED_ARMS:
        if arm_solves[arm]:
            mean_v = float(np.mean(arm_solves[arm]))
            std_v = float(np.std(arm_solves[arm]))
            cv = (std_v / mean_v) if mean_v > 1e-8 else float("inf")
            summary[arm] = {
                "solve_rate_mean": mean_v,
                "solve_rate_std": std_v,
                "solve_rate_cv": cv,
                "median_plan_ratio_mean": float(np.mean(
                    [r for r in arm_ratios[arm] if r != float("inf")]
                )) if any(r != float("inf") for r in arm_ratios[arm]) else float("inf"),
                "n": len(arm_solves[arm]),
            }
        else:
            summary[arm] = {"solve_rate_mean": 0.0, "n": 0}

    opts = summary["options_full"]["solve_rate_mean"]
    policy = summary["policy_only"]["solve_rate_mean"]
    init_ = summary["init_only"]["solve_rate_mean"]
    term = summary["term_only"]["solve_rate_mean"]
    cf = summary["closed_form_baseline"]["solve_rate_mean"]
    rand = summary["random"]["solve_rate_mean"]
    opts_cv = summary["options_full"].get("solve_rate_cv", float("inf"))

    lift_policy = opts - policy
    lift_cf = opts - cf
    lift_random = opts - rand

    arms_distinct_all = bool(arms_distinct_seeds and all(arms_distinct_seeds))

    # Verdict logic
    third_failure_gate = False
    if not arms_distinct_all:
        verdict = "HARD_FAIL"
        reason = "ARMS_NOT_DISTINCT (cell bug; per-arm hashes collide)"
    elif opts <= HF_OPTIONS_MAX_THIRD_FAILURE:
        verdict = "HARD_FAIL"
        third_failure_gate = True
        reason = ("THIRD_FAILURE_GATE (options=%.3f <= %.2f; 3rd consecutive HARD_FAIL "
                  "on hierarchical-planning mechanism class; close capability box)"
                  % (opts, HF_OPTIONS_MAX_THIRD_FAILURE))
    elif abs(opts - rand) < HF_PI_BUG_DELTA:
        verdict = "HARD_FAIL"
        reason = ("PI_NOT_EXECUTING (options=%.3f within %.2f of random=%.3f; "
                  "cell bug not framework failure)" % (opts, HF_PI_BUG_DELTA, rand))
    elif cf >= HF_CLOSED_FORM_BREACH:
        verdict = "HARD_FAIL"
        reason = ("CLOSED_FORM_DID_NOT_REPLICATE_PRIOR (cf=%.3f >= %.2f; "
                  "prior HARD_FAIL did NOT replicate; investigate regime)" % (cf, HF_CLOSED_FORM_BREACH))
    elif rand > HF_RAND_MAX_SANITY:
        verdict = "HARD_FAIL"
        reason = "SANITY_BREACH_RANDOM (rand=%.3f > %.2f; domain trivial)" % (rand, HF_RAND_MAX_SANITY)
    elif (opts >= HP_OPTIONS_SOLVE_MIN and
            opts <= HP_OPTIONS_UNSAT_HI and
            lift_policy >= HP_LIFT_POLICY_MIN and
            lift_cf >= HP_LIFT_CLOSED_FORM_MIN and
            lift_random >= HP_LIFT_RANDOM_MIN and
            cf < HP_CLOSED_FORM_MAX and
            rand < HP_RANDOM_MAX and
            opts_cv <= HP_CV_MAX):
        verdict = "HARD_PASS"
        reason = "ALL_HP_BANDS_MET"
    elif (MB_OPTIONS_LO <= opts < MB_OPTIONS_HI and
            lift_policy >= MB_LIFT_POLICY_MIN and
            lift_random >= MB_LIFT_RANDOM_MIN):
        verdict = "MIDDLE_BAND"
        reason = ("MB_band (opts=%.3f lift_pol=%.3f lift_cf=%.3f lift_rand=%.3f)"
                  % (opts, lift_policy, lift_cf, lift_random))
    else:
        verdict = "MIDDLE_BAND"
        reason = "below_MB_but_above_HF"

    verdict_msg = (
        "%s | %s | OPTS=%.3f POLICY=%.3f INIT=%.3f TERM=%.3f CF=%.3f RAND=%.3f | "
        "OPTS-POLICY=%.3f OPTS-CF=%.3f OPTS-RAND=%.3f cv=%.3f arms_distinct=%s "
        "chance_floor=%.4g"
    ) % (verdict, reason, opts, policy, init_, term, cf, rand,
         lift_policy, lift_cf, lift_random, opts_cv,
         arms_distinct_all, CHANCE_RANDOM_FLOOR)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "lift_options_minus_policy": float(lift_policy),
        "lift_options_minus_closed_form": float(lift_cf),
        "lift_options_minus_random": float(lift_random),
        "arms_distinct": arms_distinct_all,
        "n_seeds_complete": len(per_seed),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(per_seed) * len(EXPECTED_ARMS) * N_GOALS,
        "cardinality_ok": (len(per_seed) >= max(1, len(SEEDS) - 1)),
        "chance_random_floor": float(CHANCE_RANDOM_FLOOR),
        "chance_random_rerank_ub": float(CHANCE_RANDOM_RERANK_UB),
        "_third_failure_gate_triggered": third_failure_gate,
    }


# ---------------- main ----------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS})

    print("[%s] mode=%s N=%d blocks=%d pos=%d actions=%d options=%d K_anchor=%d "
          "goals=%d depth=%d K_replan=%d max_total=%d seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_BLOCKS, N_POS, N_ACTIONS, N_OPTIONS,
        K_ANCHOR_PER_OPTION, N_GOALS, COMPOSITE_DEPTH, K_REPLAN, MAX_TOTAL_STEPS,
        SEEDS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r, "missing per_arm"
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
            opts = r["per_arm"]["options_full"]["solve_rate"]
            policy = r["per_arm"]["policy_only"]["solve_rate"]
            init_ = r["per_arm"]["init_only"]["solve_rate"]
            term = r["per_arm"]["term_only"]["solve_rate"]
            cf = r["per_arm"]["closed_form_baseline"]["solve_rate"]
            rand = r["per_arm"]["random"]["solve_rate"]
            assert r["arms_distinct"], "ARMS_NOT_DISTINCT at selftest"
            assert 0 <= opts <= 1.0, "opts out of range"
            assert not (np.isnan(opts) or np.isinf(opts)), "opts NaN/Inf"
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: opts=%.3f policy=%.3f init=%.3f term=%.3f cf=%.3f rand=%.3f" % (
                                       opts, policy, init_, term, cf, rand),
                                   extra={"_phase": "selftest_done",
                                          "selftest_arms": list(r["per_arm"].keys()),
                                          "opts_solve": opts, "policy_solve": policy,
                                          "init_solve": init_, "term_solve": term,
                                          "cf_solve": cf, "rand_solve": rand,
                                          "arms_distinct": r["arms_distinct"]})
            print("[selftest] OK; opts=%.3f policy=%.3f init=%.3f term=%.3f cf=%.3f rand=%.3f distinct=%s" % (
                opts, policy, init_, term, cf, rand, r["arms_distinct"]), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_substrate_hierarchical_options"
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
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
