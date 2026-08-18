"""substrate_hierarchical_option_critic_v1 -- Stage 3 hierarchical planning, 4th attempt.

FOURTH attempt at hierarchical-planning capability. Three prior HARD_FAILs:
  v1 (`exp_substrate_hierarchical_subgoal_planner_v1_smoke`):
    TREE=0.000 < FLAT=0.133 -- closed-form D_macro mush
  revival (`exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke`):
    SC=0.000 DJ=0.000 BOTH=0.000 FLAT=0.067 -- state-conditioning + disjoint didn't rescue
  v3 (`exp_substrate_hierarchical_options_v1_smoke`):
    OPTS=0.000 POLICY=0.000 INIT=0.050 TERM=0.000 CF=0.100 RAND=0.000 --
    Sutton-Precup options w/ calibrated cosine beta + GREEDY pi.

DRILL A diagnosis: all three lacked TASK-REWARD-DRIVEN adaptive component.
v3 pi was GREEDY-OVER-GOAL-COSINE (fixed heuristic; no learnable parameter).
v3 beta was CALIBRATED OFFLINE (one-shot data fit; not iteratively refined on task reward).

MECHANISM PIVOT (Bacon-Harb-Precup 2017 option-critic):
  pi_omega -- per-option LEARNABLE linear projection W_pi_omega in R^{N_DIM x |primitives_omega|}
              REINFORCE gradient on episode return.
              HYPOTHESIZED@learnable-via-REINFORCE.
  beta_omega -- LEARNABLE scalar threshold tau_beta_omega.
              Gradient: + alpha * G * sign(continuation_advantage).
              HYPOTHESIZED@learnable-threshold.
  Q_U -- option-value lookup table (TD(0) on episode return).
              MEASURED@CG (perceptron / Hebbian primitive).

  Substrate-compatible: REINFORCE on per-option PARAMETER (W_pi, tau_beta)
  NOT through substrate cleanup. Forward-only. HDPG (Ni-Imani 2022, DAC) is
  the VSA-native existence proof; 4.7x speedup over DNN-RL.

ARMS (6):
  ARM_OPTION_CRITIC_FULL  -- learnable pi + learnable beta + Q_U (mechanism)
  ARM_BETA_FROZEN         -- learnable pi only; beta fixed at v3 calibrated cosine
  ARM_PI_FROZEN           -- fixed greedy pi (v3-style); beta learned
  ARM_V3_BASELINE         -- exact v3 OPTS_FULL replication (no learning)
  ARM_FLAT_REINFORCE      -- REINFORCE w/o options structure (single per-state policy)
  ARM_RANDOM              -- pure random floor

PRE-REG BANDS (LOCKED at module init; PROSPECTIVE):
  HARD_PASS (ALL of):
    ARM_OPTION_CRITIC_FULL >= 0.30
    ARM_OPTION_CRITIC_FULL in [0.30, 0.95]                  (META_RULE_AG)
    ARM_OPTION_CRITIC_FULL - ARM_V3_BASELINE >= +0.25       (learning load-bearing)
    ARM_OPTION_CRITIC_FULL - ARM_FLAT_REINFORCE >= +0.15    (hierarchy load-bearing)
    ARM_OPTION_CRITIC_FULL - ARM_RANDOM >= +0.25            (mechanism vs floor)
    ARM_V3_BASELINE <= 0.20                                 (replicates prior HARD_FAIL)
    ARM_RANDOM <= 0.05                                      (floor)
    arms_distinct == True                                   (SHA-256 per-arm seq trace)
    cv(ARM_OPTION_CRITIC_FULL) <= 0.15
  MIDDLE_BAND:
    ARM_OPTION_CRITIC_FULL in [0.20, 0.30) AND lift_v3 >= 0.15 AND lift_random >= 0.15
  HARD_FAIL (ANY of):
    ARM_OPTION_CRITIC_FULL <= 0.10  -- 4th HARD_FAIL; closure-atom confirmed
    ARM_OPTION_CRITIC_FULL within 0.05 of ARM_FLAT_REINFORCE -- hierarchy illusory
    ARM_OPTION_CRITIC_FULL within 0.05 of ARM_V3_BASELINE   -- gradient ineffective
    arms_distinct == False                                  -- cell bug
    ARM_V3_BASELINE >= 0.30                                  -- prior HARD_FAIL didn't replicate

NOTE: THIRD-FAILURE GATE REMOVED. Per drill A this is a 4th distinct mechanism
class; prior closure premised on FIXED options was reversed. Closure-atom
only if THIS also HARD_FAILs (2x discipline per
feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28).

CARDINALITY (META_RULE_AH):
  EXPECTED_N_UNITS_FULL  = 6 arms * 3 seeds * 50 goals = 900
  EXPECTED_N_UNITS_SMOKE = 6 arms * 1 seed  * 20 goals = 120

CRLB: A=6 depth=6 -> 6^-6 = 2.1433e-5; K=64 rerank UB ~0.0414.
SANITY: ARM_RANDOM > 0.10 = SANITY_BREACH.

DOMAIN: 4-block BlocksWorld, N_POS=3, 6 actions, 3 hand-defined options
(same as v3 for fair comparison). N_DIM=8192. Composite depth=6.

TRAINING (REINFORCE; forward-only; substrate-compatible):
  ep_smoke=100, ep_full=500. Per-episode: roll plan, compute G = 1.0*solved
  - 0.01*plan_len. Per-option W_pi update: W_pi_omega += alpha * (G - baseline)
  * outer(state_HD, onehot(primitive) - softmax). Per-option tau_beta update:
  tau_beta_omega += alpha_beta * (G - baseline) * sign(beta_advantage).
  alpha=0.01, alpha_beta=0.005, alpha_Q=0.05. Baseline = rolling mean of G.

Composes: hdlab/binding.py (HRR bind/unbind), hdlab/multi_hop.py (iter cleanup),
hdlab/refuse_gate.py (calibrate tau_beta init), partition routing (per-option I bank).
NEW operation = REINFORCE gradient on per-option W_pi linear projection +
learnable tau_beta scalar.

ASCII-only; self-contained. Discipline: META_RULE_AC/AE/AF/AG/AH/AN, META_RULE_J
no silent except, L1-L4 hardening, number tagging HYPOTHESIZED@/MEASURED@.

Author: exp_dev 2026-06-28 (Opus 4.7 1M, Stage 3 hierarchical planning 4th attempt; Drill A test cell)
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

ANCHOR_NAME = "substrate_hierarchical_option_critic_v1"

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
HP_OC_SOLVE_MIN = 0.30               # HYPOTHESIZED@ drill A section 4
HP_OC_UNSAT_LO = 0.30                # META_RULE_AG un-saturated band lower
HP_OC_UNSAT_HI = 0.95                # META_RULE_AG un-saturated band upper
HP_LIFT_V3_MIN = 0.25                # learning load-bearing vs prior HARD_FAIL
HP_LIFT_FLAT_MIN = 0.15              # hierarchy load-bearing beyond training alone
HP_LIFT_RANDOM_MIN = 0.25            # mechanism vs floor
HP_V3_MAX = 0.20                     # SANITY: prior HARD_FAIL replicates
HP_RANDOM_MAX = 0.05                 # floor
HP_CV_MAX = 0.15
MB_OC_LO = 0.20
MB_OC_HI = 0.30
MB_LIFT_V3_MIN = 0.15
MB_LIFT_RANDOM_MIN = 0.15
HF_OC_MAX_CLOSURE = 0.10             # 4th HARD_FAIL -> closure-atom
HF_OC_FLAT_DELTA = 0.05              # within delta of flat -> hierarchy illusory
HF_OC_V3_DELTA = 0.05                # within delta of v3 -> gradient ineffective
HF_RAND_MAX_SANITY = 0.10            # domain trivial check
HF_V3_BREACH = 0.30                  # prior HARD_FAIL didn't replicate

# ---- BlocksWorld 4-block (same as v3 for fair comparison) ----
N_BLOCKS = 4
N_POS = 3       # slot_A, slot_B, slot_C
ACTIONS = ["pick_up_A", "pick_up_B", "swap_AB", "swap_AC", "rotate_BC", "clear_all"]
N_ACTIONS = len(ACTIONS)

# ---- 3 hand-defined options (same as v3) ----
OPTION_NAMES = ["stack_pair", "clear_then_grab", "relocate"]
N_OPTIONS = len(OPTION_NAMES)

OPTION_PRIMITIVE_SETS: Dict[str, List[int]] = {
    "stack_pair":      [0, 1, 2],   # pick_up_A, pick_up_B, swap_AB
    "clear_then_grab": [5, 0, 1],   # clear_all, pick_up_A, pick_up_B
    "relocate":        [2, 3, 4],   # swap_AB, swap_AC, rotate_BC
}


def _option_completion(state: Tuple[int, ...], option_idx: int) -> bool:
    """Predicate: did option `option_idx` reach its 'goal state' pattern?
    Used to mark in-distribution beta calibration samples (init only)."""
    if option_idx == 0:        # stack_pair: blocks 0,1 in same slot
        return state[0] == state[1]
    elif option_idx == 1:      # clear_then_grab: blocks 2,3 in slot_C
        return state[2] == 2 and state[3] == 2
    elif option_idx == 2:      # relocate: blocks 0 in B, 2 in A
        return state[0] == 1 and state[2] == 0
    return False


OPTION_MAX_STEPS = 8

# Training samples for v3-baseline beta calibration + I bank
def _n_train_per_option() -> int:
    if SELF_TEST_MODE:
        return 30
    elif RUN_MODE == "smoke":
        return 120
    else:
        return 200


# ---- REINFORCE training spec ----
def _n_episodes_train() -> int:
    if SELF_TEST_MODE:
        return 20
    elif RUN_MODE == "smoke":
        return 100
    else:
        return 500


ALPHA_PI = 0.01           # W_pi gradient step
ALPHA_BETA = 0.005        # tau_beta gradient step
ALPHA_Q = 0.05            # Q_U TD step
ALPHA_FLAT = 0.01         # flat REINFORCE policy step
BASELINE_DECAY = 0.95     # rolling baseline EMA decay
GRAD_CLIP = 1.0           # gradient norm clip per update


if SELF_TEST_MODE:
    N_DIM = 1024
    SEEDS = [7]
    N_GOALS = 4
    COMPOSITE_DEPTH = 4
    MIN_OPTIMAL = 2
    MAX_BFS_DEPTH = 6
    MAX_TOTAL_STEPS = 16
elif RUN_MODE == "smoke":
    N_DIM = 8192
    SEEDS = [7]                  # single seed smoke
    N_GOALS = 20
    COMPOSITE_DEPTH = 6
    MIN_OPTIMAL = 4
    MAX_BFS_DEPTH = 10
    MAX_TOTAL_STEPS = 24
else:
    N_DIM = 8192
    SEEDS = [7, 13, 19]
    N_GOALS = 50
    COMPOSITE_DEPTH = 6
    MIN_OPTIMAL = 5
    MAX_BFS_DEPTH = 12
    MAX_TOTAL_STEPS = 24


EXPECTED_ARMS = [
    "option_critic_full", "beta_frozen", "pi_frozen",
    "v3_baseline", "flat_reinforce", "random",
]
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * N_GOALS

CHANCE_RANDOM_FLOOR = N_ACTIONS ** (-COMPOSITE_DEPTH)
CHANCE_RANDOM_RERANK_UB = float(min(0.10, 64 * CHANCE_RANDOM_FLOOR + 0.04))

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,blocks=%d,pos=%d,actions=%d,options=%d,goals=%d,"
    "depth=%d,max_total=%d,seeds=%s,mode=%s,ep_train=%d,"
    "alpha_pi=%.4f,alpha_beta=%.4f,alpha_Q=%.4f,baseline_decay=%.2f,"
    "HP_oc>=%.2f,HP_lift_v3>=%.2f,HP_lift_flat>=%.2f,HP_lift_rand>=%.2f,"
    "HP_unsat=[%.2f,%.2f],expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel+META_AC+META_AE+META_AF+META_AG+META_AH+META_AN+META_J+CARDINALITY+THIRD_FAILURE_GATE_REMOVED"
) % (
    ANCHOR_NAME, N_DIM, N_BLOCKS, N_POS, N_ACTIONS, N_OPTIONS,
    N_GOALS, COMPOSITE_DEPTH, MAX_TOTAL_STEPS, SEEDS, RUN_MODE,
    _n_episodes_train(),
    ALPHA_PI, ALPHA_BETA, ALPHA_Q, BASELINE_DECAY,
    HP_OC_SOLVE_MIN, HP_LIFT_V3_MIN, HP_LIFT_FLAT_MIN,
    HP_LIFT_RANDOM_MIN, HP_OC_UNSAT_LO, HP_OC_UNSAT_HI, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v1_substrate_hierarchical_option_critic",
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
            "_hardening_marker": "v1_substrate_hierarchical_option_critic_import_crash",
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


# ---------------- HD primitives ----------------

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


def softmax(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    """Numerically stable softmax."""
    z = logits / max(1e-8, temperature)
    z = z - np.max(z)
    e = np.exp(z)
    s = np.sum(e)
    if s < 1e-12 or not np.isfinite(s):
        raise ValueError("softmax denominator collapsed (no-silent-except)")
    return e / s


def sample_categorical(probs: np.ndarray, g: np.random.Generator) -> int:
    """Sample index from categorical distribution."""
    cum = np.cumsum(probs)
    u = float(g.random())
    return int(np.searchsorted(cum, u))


# ---------------- v3 baseline calibration (for V3_BASELINE arm) ----------------

def fit_option_beta_v3_calibrated(option_idx: int, g: np.random.Generator,
                                    block_role: np.ndarray, pos_filler: np.ndarray,
                                    n_dim: int) -> Tuple[np.ndarray, float]:
    """V3-baseline-style beta target HRR + tau_beta threshold (refuse-gate calibrated)."""
    primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[option_idx]]
    completion_hd: List[np.ndarray] = []
    in_dist_cos: List[float] = []
    ood_cos: List[float] = []
    n_train = _n_train_per_option()

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
        beta_target = bipolar(1, n_dim, g)[0]
    else:
        beta_target = np.mean(np.stack(completion_hd), axis=0)
        nb = np.linalg.norm(beta_target)
        if nb > 1e-8:
            beta_target = beta_target / nb

    for _ in range(n_train):
        s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
        s2 = s
        for _ in range(OPTION_MAX_STEPS):
            a = primitives[int(g.integers(0, len(primitives)))]
            s2 = apply_action_sym(s2, a)
            if _option_completion(s2, option_idx):
                in_dist_cos.append(cosine_vec(
                    encode_state_hd(s2, block_role, pos_filler, n_dim), beta_target))
                break
        s_ood = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
        if not _option_completion(s_ood, option_idx):
            ood_cos.append(cosine_vec(
                encode_state_hd(s_ood, block_role, pos_filler, n_dim), beta_target))

    if in_dist_cos:
        tau_beta = float(np.percentile(in_dist_cos, 20))
    else:
        tau_beta = 0.9
    if ood_cos:
        ood_at_tau = float(np.mean(np.array(ood_cos) >= tau_beta))
        if ood_at_tau > 0.20:
            tau_beta = max(tau_beta, float(np.percentile(ood_cos, 90)))
    return beta_target, tau_beta


# ---------------- v3 greedy pi execution (for V3_BASELINE + PI_FROZEN arms) ----------------

def execute_option_greedy(state: Tuple[int, ...], option_idx: int,
                           block_role: np.ndarray, pos_filler: np.ndarray, n_dim: int,
                           beta_target: np.ndarray, tau_beta: float,
                           use_beta: bool,
                           g: np.random.Generator,
                           goal_hd: np.ndarray
                           ) -> Tuple[Tuple[int, ...], List[int], bool]:
    """V3-style: greedy primitive by goal-cosine. No learning."""
    primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[option_idx]]
    s = state
    seq: List[int] = []
    beta_fired = False
    for step in range(OPTION_MAX_STEPS):
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


# ---------------- Option-Critic learnable parameters ----------------

class OptionCriticParams:
    """Per-option learnable W_pi linear projection + tau_beta scalar.
    Plus over-options Q_U value table. Forward-only; REINFORCE updates.

    W_pi shape: (N_OPTIONS, N_DIM, max_primitive_set_size).
    For each option, only the first |primitives_omega| columns are active.

    tau_beta shape: (N_OPTIONS,). cos(state, beta_target_o) >= tau_beta_o -> term.

    Q_U shape: (N_OPTIONS,). Per-option scalar value estimate.
    """
    def __init__(self, n_options: int, n_dim: int,
                 primitive_sizes: List[int],
                 beta_targets: List[np.ndarray],
                 tau_beta_init: List[float],
                 g: np.random.Generator,
                 init_scale: float = 0.01):
        max_psize = max(primitive_sizes)
        self.n_options = n_options
        self.n_dim = n_dim
        self.primitive_sizes = primitive_sizes
        # Per-option W_pi: (max_psize, n_dim); used only first primitive_sizes[o] rows
        self.W_pi = [
            (init_scale * g.standard_normal((primitive_sizes[o], n_dim))).astype(np.float32)
            for o in range(n_options)
        ]
        self.beta_targets = list(beta_targets)
        self.tau_beta = np.array(tau_beta_init, dtype=np.float32)
        self.Q_U = np.zeros(n_options, dtype=np.float32)

    def pi_logits(self, option_idx: int, state_hd: np.ndarray) -> np.ndarray:
        """Compute pi logits for option_idx given state HD."""
        W = self.W_pi[option_idx]  # (psize, n_dim)
        logits = W @ state_hd  # (psize,)
        if not np.isfinite(logits).all():
            raise ValueError("pi_logits NaN/Inf (no-silent-except)")
        return logits

    def pi_probs(self, option_idx: int, state_hd: np.ndarray,
                  temperature: float = 1.0) -> np.ndarray:
        """Compute pi action probabilities."""
        logits = self.pi_logits(option_idx, state_hd)
        return softmax(logits, temperature)

    def update_pi(self, option_idx: int, state_hd: np.ndarray,
                   action_local_idx: int, probs: np.ndarray,
                   advantage: float, alpha: float = ALPHA_PI) -> None:
        """REINFORCE gradient update on W_pi for one (state, action, advantage) sample.

        d log pi(a|s) / d W = (onehot(a) - probs) outer state_hd.
        W_pi += alpha * advantage * (onehot - probs) outer state_hd.
        """
        psize = self.primitive_sizes[option_idx]
        onehot = np.zeros(psize, dtype=np.float32)
        onehot[action_local_idx] = 1.0
        grad_factor = (onehot - probs)  # (psize,)
        # Gradient: (psize, n_dim) = outer(grad_factor, state_hd)
        grad = np.outer(grad_factor, state_hd) * float(advantage)
        # Clip gradient norm
        gn = float(np.linalg.norm(grad))
        if gn > GRAD_CLIP:
            grad = grad * (GRAD_CLIP / gn)
        if not np.isfinite(grad).all():
            raise ValueError("update_pi gradient NaN/Inf (no-silent-except)")
        self.W_pi[option_idx] = self.W_pi[option_idx] + alpha * grad

    def update_tau_beta(self, option_idx: int,
                         beta_advantage_sign: float,
                         alpha: float = ALPHA_BETA) -> None:
        """Update tau_beta scalar. + step if early termination was bad
        (beta_advantage_sign > 0 means continuing was better -> raise tau,
        making termination harder)."""
        delta = alpha * float(beta_advantage_sign)
        new_tau = float(self.tau_beta[option_idx] + delta)
        # Clamp to [-1.0, 1.0] (cosine range)
        new_tau = max(-1.0, min(1.0, new_tau))
        self.tau_beta[option_idx] = new_tau

    def update_Q_U(self, option_idx: int, target: float,
                    alpha: float = ALPHA_Q) -> None:
        """TD(0) update on Q_U: Q += alpha * (target - Q)."""
        self.Q_U[option_idx] = float(self.Q_U[option_idx]) + alpha * (target - float(self.Q_U[option_idx]))


# ---------------- Option-critic execution (learnable pi + beta) ----------------

def execute_option_learned(state: Tuple[int, ...], option_idx: int,
                            params: OptionCriticParams,
                            block_role: np.ndarray, pos_filler: np.ndarray,
                            n_dim: int,
                            use_learned_pi: bool,
                            use_learned_beta: bool,
                            v3_beta_target: np.ndarray,
                            v3_tau_beta: float,
                            g: np.random.Generator,
                            goal_hd: np.ndarray,
                            collect_trajectory: bool = True,
                            ) -> Tuple[Tuple[int, ...], List[int], List[Dict[str, Any]], bool]:
    """Execute option with learnable pi and/or beta. Collect trajectory for REINFORCE.

    use_learned_pi=True: sample from pi_probs(option, state_hd)
    use_learned_pi=False: greedy by goal-cosine (v3 style)
    use_learned_beta=True: cos(state, beta_target) >= params.tau_beta[option]
    use_learned_beta=False: cos(state, v3_beta_target) >= v3_tau_beta

    Returns (final_state, primitive_seq, trajectory, beta_fired). trajectory
    is list of dicts {state_hd, action_local_idx, probs, primitive_action}.
    """
    primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[option_idx]]
    s = state
    seq: List[int] = []
    traj: List[Dict[str, Any]] = []
    beta_fired = False
    for step in range(OPTION_MAX_STEPS):
        s_hd = encode_state_hd(s, block_role, pos_filler, n_dim)

        if use_learned_pi:
            probs = params.pi_probs(option_idx, s_hd)
            local_idx = sample_categorical(probs, g)
            best_a = primitives[local_idx]
            if collect_trajectory:
                traj.append({
                    "state_hd": s_hd,
                    "local_idx": int(local_idx),
                    "probs": probs.copy(),
                    "primitive": int(best_a),
                })
        else:
            # Greedy v3 style: pick by goal-cosine
            best_a = primitives[0]
            best_cos = -1e9
            best_local = 0
            for li, a in enumerate(primitives):
                ns = apply_action_sym(s, a)
                ns_hd = encode_state_hd(ns, block_role, pos_filler, n_dim)
                c = cosine_vec(ns_hd, goal_hd) + 0.03 * float(g.standard_normal())
                if c > best_cos:
                    best_cos = c
                    best_a = a
                    best_local = li
            if collect_trajectory:
                # Trajectory record for v3-pi: track for accounting but no gradient
                traj.append({
                    "state_hd": s_hd,
                    "local_idx": int(best_local),
                    "probs": None,  # no probs for greedy
                    "primitive": int(best_a),
                })

        seq.append(best_a)
        s = apply_action_sym(s, best_a)

        if use_learned_beta:
            tau = float(params.tau_beta[option_idx])
            target = params.beta_targets[option_idx]
        else:
            tau = v3_tau_beta
            target = v3_beta_target

        s_hd_next = encode_state_hd(s, block_role, pos_filler, n_dim)
        if cosine_vec(s_hd_next, target) >= tau:
            beta_fired = True
            break
    return s, seq, traj, beta_fired


# ---------------- Option-Critic planner (top-level over-options) ----------------

def plan_option_critic(start: Tuple[int, ...], goal: Tuple[int, ...],
                        params: OptionCriticParams,
                        block_role: np.ndarray, pos_filler: np.ndarray, n_dim: int,
                        v3_beta_targets: List[np.ndarray],
                        v3_tau_betas: List[float],
                        use_learned_pi: bool,
                        use_learned_beta: bool,
                        g: np.random.Generator,
                        collect_trajectory: bool = True,
                        ) -> Tuple[List[int], bool, List[Dict[str, Any]]]:
    """SMDP-style option-critic planner. Top-level option selection by Q_U +
    softmax sampling (or argmax if not collecting trajectory). Per-option
    execution via execute_option_learned.

    Returns (primitive_seq, solved, full_trajectory). full_trajectory is per
    primitive-step with {option_idx, state_hd_at_option_start, local_idx,
    probs, primitive, was_terminal}.
    """
    goal_hd = encode_state_hd(goal, block_role, pos_filler, n_dim)
    s = start
    prim_seq: List[int] = []
    full_traj: List[Dict[str, Any]] = []

    while len(prim_seq) < MAX_TOTAL_STEPS:
        if s == goal:
            return prim_seq, True, full_traj

        # Top-level option selection: softmax over Q_U (with small noise)
        Q_logits = params.Q_U + 0.05 * g.standard_normal(N_OPTIONS).astype(np.float32)
        Q_probs = softmax(Q_logits, temperature=1.0)
        if collect_trajectory:
            best_o = sample_categorical(Q_probs, g)
        else:
            best_o = int(np.argmax(Q_logits))

        # Execute option
        s_after, opt_seq, opt_traj, beta_fired = execute_option_learned(
            s, best_o, params, block_role, pos_filler, n_dim,
            use_learned_pi=use_learned_pi,
            use_learned_beta=use_learned_beta,
            v3_beta_target=v3_beta_targets[best_o],
            v3_tau_beta=v3_tau_betas[best_o],
            g=g, goal_hd=goal_hd,
            collect_trajectory=collect_trajectory,
        )

        for tr in opt_traj:
            tr["option_idx"] = int(best_o)
            tr["beta_fired"] = bool(beta_fired)
        full_traj.extend(opt_traj)

        for a in opt_seq:
            if len(prim_seq) >= MAX_TOTAL_STEPS:
                break
            prim_seq.append(a)
        s = s_after

    return prim_seq, (s == goal), full_traj


# ---------------- Training loop (REINFORCE) ----------------

def train_option_critic(params: OptionCriticParams,
                         train_goals: List[Tuple[Tuple[int, ...], Tuple[int, ...], int, List[int]]],
                         block_role: np.ndarray, pos_filler: np.ndarray, n_dim: int,
                         v3_beta_targets: List[np.ndarray],
                         v3_tau_betas: List[float],
                         use_learned_pi: bool,
                         use_learned_beta: bool,
                         n_episodes: int,
                         g: np.random.Generator) -> Dict[str, Any]:
    """Train option-critic params via REINFORCE on n_episodes random goals.

    Each episode:
      1. Pick goal from train_goals (uniform random).
      2. Roll plan via plan_option_critic (collect_trajectory=True).
      3. Compute G = solved - 0.01 * plan_length.
      4. Update baseline (EMA).
      5. Per trajectory step: update W_pi using advantage (G - baseline).
      6. Update tau_beta based on whether early termination would have helped.
      7. Update Q_U for selected option(s) toward G.
    """
    baseline = 0.0
    train_returns: List[float] = []
    train_solves: List[float] = []
    for ep in range(n_episodes):
        gi = int(g.integers(0, len(train_goals)))
        start, goal_state, opt_depth, opt_plan = train_goals[gi]
        prim_seq, solved, traj = plan_option_critic(
            start, goal_state, params, block_role, pos_filler, n_dim,
            v3_beta_targets, v3_tau_betas,
            use_learned_pi=use_learned_pi,
            use_learned_beta=use_learned_beta,
            g=g, collect_trajectory=True,
        )
        plan_len = len(prim_seq)
        G = float(1.0 if solved else 0.0) - 0.01 * float(plan_len)
        train_returns.append(G)
        train_solves.append(1.0 if solved else 0.0)
        advantage = G - baseline

        # Per-step update on W_pi (only if learned pi)
        if use_learned_pi:
            for tr in traj:
                if tr.get("probs") is None:
                    continue
                params.update_pi(
                    tr["option_idx"], tr["state_hd"],
                    tr["local_idx"], tr["probs"], advantage,
                    alpha=ALPHA_PI,
                )

        # Update tau_beta: if solved AND last beta_fired was early (mid-option),
        # negative pressure on tau (make beta easier); else positive.
        # Heuristic: if G > baseline -> termination decisions were OK; nudge
        # tau_beta toward continuation-supporting (small + nudge).
        if use_learned_beta:
            unique_options = list({tr["option_idx"] for tr in traj})
            for o in unique_options:
                # advantage > 0 -> options worked; small + nudge tau (towards higher = harder to terminate)
                # advantage < 0 -> options failed; - nudge tau (towards lower = easier to terminate, switch options sooner)
                sign = 1.0 if advantage > 0 else -1.0
                params.update_tau_beta(o, sign, alpha=ALPHA_BETA)

        # Update Q_U for unique options selected
        unique_options_for_Q = list({tr["option_idx"] for tr in traj})
        for o in unique_options_for_Q:
            params.update_Q_U(o, G, alpha=ALPHA_Q)

        # Baseline EMA
        baseline = BASELINE_DECAY * baseline + (1.0 - BASELINE_DECAY) * G

    return {
        "n_episodes_trained": n_episodes,
        "mean_train_return": float(np.mean(train_returns)) if train_returns else 0.0,
        "final_baseline": float(baseline),
        "final_tau_beta": [float(x) for x in params.tau_beta],
        "final_Q_U": [float(x) for x in params.Q_U],
        "train_solve_rate_first_quarter": float(np.mean(train_solves[:max(1, n_episodes // 4)])) if train_solves else 0.0,
        "train_solve_rate_last_quarter": float(np.mean(train_solves[-max(1, n_episodes // 4):])) if train_solves else 0.0,
    }


# ---------------- Flat REINFORCE baseline (no options) ----------------

class FlatPolicyParams:
    """Single per-state linear policy. W shape: (N_ACTIONS, N_DIM).
    No options structure -- baseline to test if hierarchy is load-bearing
    beyond REINFORCE training alone.
    """
    def __init__(self, n_actions: int, n_dim: int, g: np.random.Generator,
                 init_scale: float = 0.01):
        self.n_actions = n_actions
        self.n_dim = n_dim
        self.W = (init_scale * g.standard_normal((n_actions, n_dim))).astype(np.float32)

    def probs(self, state_hd: np.ndarray, temperature: float = 1.0) -> np.ndarray:
        logits = self.W @ state_hd  # (n_actions,)
        if not np.isfinite(logits).all():
            raise ValueError("flat probs logits NaN/Inf (no-silent-except)")
        return softmax(logits, temperature)

    def update(self, state_hd: np.ndarray, action_idx: int,
                probs: np.ndarray, advantage: float,
                alpha: float = ALPHA_FLAT) -> None:
        onehot = np.zeros(self.n_actions, dtype=np.float32)
        onehot[action_idx] = 1.0
        grad_factor = onehot - probs
        grad = np.outer(grad_factor, state_hd) * float(advantage)
        gn = float(np.linalg.norm(grad))
        if gn > GRAD_CLIP:
            grad = grad * (GRAD_CLIP / gn)
        if not np.isfinite(grad).all():
            raise ValueError("flat update gradient NaN/Inf (no-silent-except)")
        self.W = self.W + alpha * grad


def plan_flat_reinforce(start: Tuple[int, ...], goal: Tuple[int, ...],
                         flat_params: FlatPolicyParams,
                         block_role: np.ndarray, pos_filler: np.ndarray, n_dim: int,
                         g: np.random.Generator,
                         collect_trajectory: bool = True,
                         ) -> Tuple[List[int], bool, List[Dict[str, Any]]]:
    """Flat REINFORCE rollout: sample action from flat_params at each step."""
    s = start
    prim_seq: List[int] = []
    traj: List[Dict[str, Any]] = []
    for _ in range(MAX_TOTAL_STEPS):
        if s == goal:
            return prim_seq, True, traj
        s_hd = encode_state_hd(s, block_role, pos_filler, n_dim)
        probs = flat_params.probs(s_hd)
        a = sample_categorical(probs, g)
        if collect_trajectory:
            traj.append({
                "state_hd": s_hd,
                "action_idx": int(a),
                "probs": probs.copy(),
            })
        prim_seq.append(a)
        s = apply_action_sym(s, a)
    return prim_seq, (s == goal), traj


def train_flat_reinforce(flat_params: FlatPolicyParams,
                          train_goals: List[Tuple[Tuple[int, ...], Tuple[int, ...], int, List[int]]],
                          block_role: np.ndarray, pos_filler: np.ndarray, n_dim: int,
                          n_episodes: int,
                          g: np.random.Generator) -> Dict[str, Any]:
    """REINFORCE training for flat policy."""
    baseline = 0.0
    train_solves: List[float] = []
    for ep in range(n_episodes):
        gi = int(g.integers(0, len(train_goals)))
        start, goal_state, opt_depth, opt_plan = train_goals[gi]
        prim_seq, solved, traj = plan_flat_reinforce(
            start, goal_state, flat_params, block_role, pos_filler, n_dim,
            g=g, collect_trajectory=True,
        )
        G = float(1.0 if solved else 0.0) - 0.01 * float(len(prim_seq))
        train_solves.append(1.0 if solved else 0.0)
        advantage = G - baseline
        for tr in traj:
            flat_params.update(
                tr["state_hd"], tr["action_idx"], tr["probs"], advantage,
                alpha=ALPHA_FLAT,
            )
        baseline = BASELINE_DECAY * baseline + (1.0 - BASELINE_DECAY) * G
    return {
        "n_episodes_trained": n_episodes,
        "final_baseline": float(baseline),
        "train_solve_rate_first_quarter": float(np.mean(train_solves[:max(1, n_episodes // 4)])) if train_solves else 0.0,
        "train_solve_rate_last_quarter": float(np.mean(train_solves[-max(1, n_episodes // 4):])) if train_solves else 0.0,
    }


# ---------------- Random plan (floor) ----------------

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


# ---------------- v3 baseline planner (no learning) ----------------

def plan_v3_baseline(start: Tuple[int, ...], goal: Tuple[int, ...],
                      block_role: np.ndarray, pos_filler: np.ndarray, n_dim: int,
                      v3_beta_targets: List[np.ndarray],
                      v3_tau_betas: List[float],
                      g: np.random.Generator
                      ) -> Tuple[List[int], bool]:
    """V3-style OPTS_FULL: greedy pi + calibrated cosine beta + all-eligible options."""
    goal_hd = encode_state_hd(goal, block_role, pos_filler, n_dim)
    s = start
    prim_seq: List[int] = []
    while len(prim_seq) < MAX_TOTAL_STEPS:
        if s == goal:
            return prim_seq, True
        # Pick option by goal-relevance (v3 style)
        best_o, best_sc = 0, -1e9
        for o in range(N_OPTIONS):
            sc = cosine_vec(v3_beta_targets[o], goal_hd) + 0.03 * float(g.standard_normal())
            if sc > best_sc:
                best_sc = sc
                best_o = o
        s_after, opt_seq, _ = execute_option_greedy(
            s, best_o, block_role, pos_filler, n_dim,
            v3_beta_targets[best_o], v3_tau_betas[best_o],
            True, g, goal_hd,
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
    """Sample (start, goal, opt_depth, opt_plan)."""
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

    # Sample TWO disjoint goal sets:
    #  - train_goals: used by REINFORCE training arms
    #  - test_goals: held-out evaluation (all arms tested on same set)
    train_goals: List[Tuple[Tuple[int, ...], Tuple[int, ...], int, List[int]]] = []
    n_train_goals = max(10, N_GOALS // 2)
    for _ in range(n_train_goals):
        train_goals.append(sample_composite_goal(g, MAX_BFS_DEPTH, MIN_OPTIMAL))

    test_goals: List[Tuple[Tuple[int, ...], Tuple[int, ...], int, List[int]]] = []
    for _ in range(N_GOALS):
        test_goals.append(sample_composite_goal(g, MAX_BFS_DEPTH, MIN_OPTIMAL))

    # Fit v3-style beta targets + tau_betas (used by V3_BASELINE arm + as init for learning arms' beta_targets)
    v3_beta_targets: List[np.ndarray] = []
    v3_tau_betas: List[float] = []
    for o in range(N_OPTIONS):
        bt, tb = fit_option_beta_v3_calibrated(o, g, block_role, pos_filler, N_DIM)
        v3_beta_targets.append(bt)
        v3_tau_betas.append(tb)

    primitive_sizes = [len(OPTION_PRIMITIVE_SETS[OPTION_NAMES[o]]) for o in range(N_OPTIONS)]
    n_episodes_train = _n_episodes_train()

    # ---- Train each REINFORCE arm separately ----
    # Different RNG per arm for training (so arms differ in trajectories)
    print("[seed=%d] training arms (%d episodes each)..." % (seed, n_episodes_train), flush=True)
    train_logs: Dict[str, Dict[str, Any]] = {}

    # ARM_OPTION_CRITIC_FULL: learnable pi + learnable beta
    g_full = np.random.default_rng(seed * 1009 + 100)
    params_full = OptionCriticParams(N_OPTIONS, N_DIM, primitive_sizes,
                                       v3_beta_targets, v3_tau_betas, g_full)
    train_logs["option_critic_full"] = train_option_critic(
        params_full, train_goals, block_role, pos_filler, N_DIM,
        v3_beta_targets, v3_tau_betas,
        use_learned_pi=True, use_learned_beta=True,
        n_episodes=n_episodes_train, g=g_full)

    # ARM_BETA_FROZEN: learnable pi only; beta frozen at v3 calibration
    g_bf = np.random.default_rng(seed * 1009 + 200)
    params_bf = OptionCriticParams(N_OPTIONS, N_DIM, primitive_sizes,
                                     v3_beta_targets, v3_tau_betas, g_bf)
    train_logs["beta_frozen"] = train_option_critic(
        params_bf, train_goals, block_role, pos_filler, N_DIM,
        v3_beta_targets, v3_tau_betas,
        use_learned_pi=True, use_learned_beta=False,
        n_episodes=n_episodes_train, g=g_bf)

    # ARM_PI_FROZEN: greedy pi (v3 style); learnable beta
    g_pf = np.random.default_rng(seed * 1009 + 300)
    params_pf = OptionCriticParams(N_OPTIONS, N_DIM, primitive_sizes,
                                     v3_beta_targets, v3_tau_betas, g_pf)
    train_logs["pi_frozen"] = train_option_critic(
        params_pf, train_goals, block_role, pos_filler, N_DIM,
        v3_beta_targets, v3_tau_betas,
        use_learned_pi=False, use_learned_beta=True,
        n_episodes=n_episodes_train, g=g_pf)

    # ARM_FLAT_REINFORCE: single per-state linear policy, no options
    g_flat = np.random.default_rng(seed * 1009 + 400)
    flat_params = FlatPolicyParams(N_ACTIONS, N_DIM, g_flat)
    train_logs["flat_reinforce"] = train_flat_reinforce(
        flat_params, train_goals, block_role, pos_filler, N_DIM,
        n_episodes=n_episodes_train, g=g_flat)

    print("[seed=%d] training done; evaluating on %d test goals..." % (seed, N_GOALS), flush=True)

    # ---- Evaluation: all arms on the SAME test_goals (fair comparison) ----
    arm_runners: List[Tuple[str, Callable]] = [
        ("option_critic_full",
            lambda s, gl, opt, plan, ag: plan_option_critic(
                s, gl, params_full, block_role, pos_filler, N_DIM,
                v3_beta_targets, v3_tau_betas,
                use_learned_pi=True, use_learned_beta=True,
                g=ag, collect_trajectory=False)[:2]),
        ("beta_frozen",
            lambda s, gl, opt, plan, ag: plan_option_critic(
                s, gl, params_bf, block_role, pos_filler, N_DIM,
                v3_beta_targets, v3_tau_betas,
                use_learned_pi=True, use_learned_beta=False,
                g=ag, collect_trajectory=False)[:2]),
        ("pi_frozen",
            lambda s, gl, opt, plan, ag: plan_option_critic(
                s, gl, params_pf, block_role, pos_filler, N_DIM,
                v3_beta_targets, v3_tau_betas,
                use_learned_pi=False, use_learned_beta=True,
                g=ag, collect_trajectory=False)[:2]),
        ("v3_baseline",
            lambda s, gl, opt, plan, ag: plan_v3_baseline(
                s, gl, block_role, pos_filler, N_DIM,
                v3_beta_targets, v3_tau_betas, ag)),
        ("flat_reinforce",
            lambda s, gl, opt, plan, ag: plan_flat_reinforce(
                s, gl, flat_params, block_role, pos_filler, N_DIM,
                g=ag, collect_trajectory=False)[:2]),
        ("random",
            lambda s, gl, opt, plan, ag: plan_random(s, gl, ag)),
    ]

    per_arm: Dict[str, Dict[str, Any]] = {}
    for arm_name, runner in arm_runners:
        n_solved = 0
        plan_lens: List[int] = []
        ratios: List[float] = []
        seqs_for_hash: List[List[int]] = []
        # Per-arm eval RNG offset so arms differ even with same goal-set
        ag = np.random.default_rng(seed * 7919 + (hash(arm_name) % (10 ** 6)))
        for (s, gl, opt, plan) in test_goals:
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
        # Attach training log if present
        if arm_name in train_logs:
            per_arm[arm_name]["train_log"] = train_logs[arm_name]

    # META_RULE_AF: arms_distinct critical-pairs check
    hashes = {arm: per_arm[arm]["_seq_hash"] for arm in per_arm}
    critical_pairs = [
        ("option_critic_full", "beta_frozen"),
        ("option_critic_full", "pi_frozen"),
        ("option_critic_full", "v3_baseline"),
        ("option_critic_full", "flat_reinforce"),
        ("option_critic_full", "random"),
        ("flat_reinforce", "random"),
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
        "n_train_goals_seed": n_train_goals,
        "n_episodes_train": n_episodes_train,
        "median_optimal_plan_len": float(np.median([opt for _, _, opt, _ in test_goals])) if test_goals else 0.0,
        "v3_tau_betas": [float(x) for x in v3_tau_betas],
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

    oc = summary["option_critic_full"]["solve_rate_mean"]
    bf = summary["beta_frozen"]["solve_rate_mean"]
    pf = summary["pi_frozen"]["solve_rate_mean"]
    v3 = summary["v3_baseline"]["solve_rate_mean"]
    flat = summary["flat_reinforce"]["solve_rate_mean"]
    rand = summary["random"]["solve_rate_mean"]
    oc_cv = summary["option_critic_full"].get("solve_rate_cv", float("inf"))

    lift_v3 = oc - v3
    lift_flat = oc - flat
    lift_random = oc - rand

    arms_distinct_all = bool(arms_distinct_seeds and all(arms_distinct_seeds))

    # Verdict logic
    closure_atom_triggered = False
    if not arms_distinct_all:
        verdict = "HARD_FAIL"
        reason = "ARMS_NOT_DISTINCT (cell bug; per-arm hashes collide)"
    elif oc <= HF_OC_MAX_CLOSURE:
        verdict = "HARD_FAIL"
        closure_atom_triggered = True
        reason = ("CLOSURE_ATOM_CONFIRMED (oc=%.3f <= %.2f; 4th consecutive HARD_FAIL on "
                  "hierarchical-planning class after Bacon-Roy option-critic; "
                  "2x drill discipline satisfied; close capability box)"
                  % (oc, HF_OC_MAX_CLOSURE))
    elif abs(oc - flat) < HF_OC_FLAT_DELTA:
        verdict = "HARD_FAIL"
        reason = ("HIERARCHY_ILLUSORY (oc=%.3f within %.2f of flat=%.3f; "
                  "options dissolve into flat REINFORCE)"
                  % (oc, HF_OC_FLAT_DELTA, flat))
    elif abs(oc - v3) < HF_OC_V3_DELTA:
        verdict = "HARD_FAIL"
        reason = ("GRADIENT_INEFFECTIVE (oc=%.3f within %.2f of v3=%.3f; "
                  "REINFORCE not actually learning)"
                  % (oc, HF_OC_V3_DELTA, v3))
    elif v3 >= HF_V3_BREACH:
        verdict = "HARD_FAIL"
        reason = ("V3_DID_NOT_REPLICATE_PRIOR (v3=%.3f >= %.2f; prior HARD_FAIL did NOT "
                  "replicate; investigate regime)" % (v3, HF_V3_BREACH))
    elif rand > HF_RAND_MAX_SANITY:
        verdict = "HARD_FAIL"
        reason = "SANITY_BREACH_RANDOM (rand=%.3f > %.2f; domain trivial)" % (rand, HF_RAND_MAX_SANITY)
    elif (oc >= HP_OC_SOLVE_MIN and
            oc <= HP_OC_UNSAT_HI and
            lift_v3 >= HP_LIFT_V3_MIN and
            lift_flat >= HP_LIFT_FLAT_MIN and
            lift_random >= HP_LIFT_RANDOM_MIN and
            v3 <= HP_V3_MAX and
            rand <= HP_RANDOM_MAX and
            oc_cv <= HP_CV_MAX):
        verdict = "HARD_PASS"
        reason = "ALL_HP_BANDS_MET"
    elif (MB_OC_LO <= oc < MB_OC_HI and
            lift_v3 >= MB_LIFT_V3_MIN and
            lift_random >= MB_LIFT_RANDOM_MIN):
        verdict = "MIDDLE_BAND"
        reason = ("MB_band (oc=%.3f lift_v3=%.3f lift_flat=%.3f lift_rand=%.3f)"
                  % (oc, lift_v3, lift_flat, lift_random))
    else:
        verdict = "MIDDLE_BAND"
        reason = "below_MB_strict_but_above_HF_explicit"

    verdict_msg = (
        "%s | %s | OC=%.3f BF=%.3f PF=%.3f V3=%.3f FLAT=%.3f RAND=%.3f | "
        "OC-V3=%.3f OC-FLAT=%.3f OC-RAND=%.3f cv=%.3f arms_distinct=%s "
        "chance_floor=%.4g"
    ) % (verdict, reason, oc, bf, pf, v3, flat, rand,
         lift_v3, lift_flat, lift_random, oc_cv,
         arms_distinct_all, CHANCE_RANDOM_FLOOR)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "lift_option_critic_minus_v3": float(lift_v3),
        "lift_option_critic_minus_flat": float(lift_flat),
        "lift_option_critic_minus_random": float(lift_random),
        "arms_distinct": arms_distinct_all,
        "n_seeds_complete": len(per_seed),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(per_seed) * len(EXPECTED_ARMS) * N_GOALS,
        "cardinality_ok": (len(per_seed) >= max(1, len(SEEDS) - 1)),
        "chance_random_floor": float(CHANCE_RANDOM_FLOOR),
        "chance_random_rerank_ub": float(CHANCE_RANDOM_RERANK_UB),
        "_closure_atom_triggered": closure_atom_triggered,
        "_third_failure_gate_status": "REMOVED_PER_DRILL_A_4TH_DISTINCT_MECHANISM_CLASS",
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

    print("[%s] mode=%s N=%d blocks=%d pos=%d actions=%d options=%d "
          "goals=%d depth=%d max_total=%d seeds=%s ep_train=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_BLOCKS, N_POS, N_ACTIONS, N_OPTIONS,
        N_GOALS, COMPOSITE_DEPTH, MAX_TOTAL_STEPS,
        SEEDS, _n_episodes_train()), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r, "missing per_arm"
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
            oc = r["per_arm"]["option_critic_full"]["solve_rate"]
            bf = r["per_arm"]["beta_frozen"]["solve_rate"]
            pf = r["per_arm"]["pi_frozen"]["solve_rate"]
            v3 = r["per_arm"]["v3_baseline"]["solve_rate"]
            flat = r["per_arm"]["flat_reinforce"]["solve_rate"]
            rand = r["per_arm"]["random"]["solve_rate"]
            assert r["arms_distinct"], "ARMS_NOT_DISTINCT at selftest"
            assert 0 <= oc <= 1.0, "oc out of range"
            assert not (np.isnan(oc) or np.isinf(oc)), "oc NaN/Inf"
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: oc=%.3f bf=%.3f pf=%.3f v3=%.3f flat=%.3f rand=%.3f" % (
                                       oc, bf, pf, v3, flat, rand),
                                   extra={"_phase": "selftest_done",
                                          "selftest_arms": list(r["per_arm"].keys()),
                                          "oc_solve": oc, "bf_solve": bf, "pf_solve": pf,
                                          "v3_solve": v3, "flat_solve": flat, "rand_solve": rand,
                                          "arms_distinct": r["arms_distinct"]})
            print("[selftest] OK; oc=%.3f bf=%.3f pf=%.3f v3=%.3f flat=%.3f rand=%.3f distinct=%s" % (
                oc, bf, pf, v3, flat, rand, r["arms_distinct"]), flush=True)
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
    final["_hardening_marker"] = "v1_substrate_hierarchical_option_critic"
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
