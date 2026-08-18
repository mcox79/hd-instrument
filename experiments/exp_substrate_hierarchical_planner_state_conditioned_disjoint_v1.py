"""substrate_hierarchical_planner_state_conditioned_disjoint_v1 -- Stage 3 REVIVAL.

REVIVAL of substrate_hierarchical_subgoal_planner_v1 (HARD_FAIL TREE=0.000 < FLAT=0.133).

V1 DIAGNOSIS (per drill 2026-06-28):
  Closed-form D_macro = mean(s_post_hd - s_pre_hd) over random starts averaged
  parallel-block primitive effects into mush. Macros are NON-STATIONARY (effect
  depends on start-state), so a single global D_macro per macro cannot capture
  any specific transition. Per-level cleanup then snaps to the wrong (averaged)
  codeword, the residual is corrupted, and the tree never finds a valid plan.

SMALLEST-DELTA REVIVAL (composes 4 existing CG primitives + 1 NEW operation):
  MECHANISM A (state-conditioned macro vocabulary):
    Cluster start-states into K_CLASS state-classes (deterministic hash on
    state-tuple). Fit D_macro[class_k, macro_m] = mean(s_post - s_pre)
    restricted to starts in class k. At plan-time, classify start-state,
    look up state-conditioned macro codebook. This addresses the parallel-
    block-averaging bug at its root.

  MECHANISM B (disjoint per-level capacity reservation):
    Reserve N_DIM/3 dimensions per tree level (level-1 goal-decomp dims;
    level-2 macro-binding dims; level-3 primitive-rollout dims). Each level's
    cleanup only sees its own block. Eliminates cross-level interference where
    level-2 cleanup contaminates level-1 residual via HRR-bind crosstalk.

ARMS (6):
  ARM_REPRODUCE_RAIL           BFS oracle (upper bound)
  ARM_RANDOM_PLAN              chance baseline (K=64 + cosine rerank)
  ARM_FLAT_PREPLAY_K64_D8      v1 baseline (no hierarchy)
  ARM_TREE_3LVL_STATE_COND     mechanism A only (state-conditioned, no disjoint)
  ARM_TREE_3LVL_DISJOINT_BLOCK mechanism B only (disjoint, no state-cond)
  ARM_TREE_3LVL_BOTH           full mechanism (state-cond + disjoint) = under test

PRE-REG BANDS (LOCKED at module init, PROSPECTIVE):
  HARD_PASS (ALL of):
    ARM_TREE_BOTH solve_rate >= 0.50
    ARM_TREE_BOTH - ARM_FLAT_PREPLAY_K64_D8 >= +0.25   (mechanism adds value)
    ARM_TREE_BOTH - ARM_TREE_STATE_COND     >= +0.10   (disjoint adds)
    ARM_TREE_BOTH - ARM_TREE_DISJOINT       >= +0.10   (state-cond adds)
    ARM_REPRODUCE_RAIL solve_rate >= 0.95
    cv across seeds (ARM_TREE_BOTH) < 0.15
    arms_distinct == True (SHA-256 per-arm seq trace)
  MIDDLE_BAND: ARM_TREE_BOTH solve_rate in [0.25, 0.50]
  HARD_FAIL (ANY of):
    ARM_TREE_BOTH <= ARM_FLAT_PREPLAY_K64_D8  (mechanism still useless)
    arms_distinct == False                    (cell bug)
    ARM_REPRODUCE_RAIL < 0.95                 (BFS broken)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 6 arms * 5 seeds * 100 goals = 3000
  EXPECTED_N_UNITS_SMOKE = 6 arms * 2 seeds * 30 goals  = 360

CRLB: at |A|=6 depth=8, chance ~ 6^-6 = 2.1e-5; K=64 rerank lifts to ~0.0013.
SANITY: ARM_RANDOM > 0.15 = SANITY_BREACH.

Brain analog:
  Koechlin 2003 anterior PFC hierarchical control (state-classes = task-set context).
  Badre & D'Esposito 2009 rostro-caudal PFC abstract->concrete gradient (disjoint
  per-level dim-blocks mirror cortical-layer-segregated processing).
  Sutton & Precup 1999 options framework (macros = options).

Composes: hdlab/binding.py (HRR bind/unbind CG), hdlab/multi_hop.py (iter cleanup
CG depth-15), hdlab/partition_routing.py (M=10M disjoint partition CG), hdlab/
working_memory.py (TWO_TIER generational W CG). NEW operation = state-conditioned
chunk-dictionary fit.

ASCII-only; self-contained. Discipline: META_RULE_AF (arms-must-differ SHA-256),
META_RULE_AH (atomic-final-metrics-write tmp+os.replace), META_RULE_AL (encoding
= state-conditioned chunk-dict fit; readout = plan-solve via cleanup),
L1-L4 hardening + cardinality_ok, number tagging MEASURED@/HYPOTHESIZED@.

Author: exp_dev 2026-06-28 (Opus 4.7 1M, Stage 3 hierarchical planning REVIVAL)
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
from typing import Any, Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "substrate_hierarchical_planner_state_conditioned_disjoint_v1"

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
HP_BOTH_SOLVE_MIN = 0.50          # HYPOTHESIZED@ from drill section c
HP_BOTH_OVER_FLAT_MIN = 0.25      # HYPOTHESIZED@ (mechanism lift discriminator)
HP_BOTH_OVER_STATE_COND_MIN = 0.10  # HYPOTHESIZED@ (disjoint-block lift)
HP_BOTH_OVER_DISJOINT_MIN = 0.10  # HYPOTHESIZED@ (state-cond lift)
HP_RAIL_MIN = 0.95                # MEASURED@ BFS analytic (deterministic)
HP_CV_MAX = 0.15
MB_BOTH_SOLVE_LO = 0.25           # MIDDLE_BAND floor
MB_BOTH_SOLVE_HI = 0.50           # MIDDLE_BAND ceiling (= HP floor)
HF_RAND_MAX = 0.15                # SANITY: RANDOM > 0.15 means domain trivial

# ---- BlocksWorld 8-block extended domain (identical to v1 for apples-to-apples) ----
N_BLOCKS = 8
ACTIONS = ["pick_up", "put_down", "stack", "unstack", "move_aside", "swap"]
N_ACTIONS = len(ACTIONS)
N_POS = 4  # 0=slot_A, 1=slot_B, 2=slot_C, 3=held

MACRO_NAMES = ["tower", "separate", "gather", "order", "clear_surface"]
N_MACROS = len(MACRO_NAMES)
MACRO_PRIMITIVES = {
    "tower":         [2, 2],
    "separate":      [3, 1],
    "gather":        [0, 1, 0, 1],
    "order":         [4, 4],
    "clear_surface": [3, 3, 1],
}

# State-class config (MECHANISM A): K_CLASS partitions of start-state space.
# Deterministic hash on state-tuple modulo K_CLASS.
K_CLASS = 8

if SELF_TEST_MODE:
    N_DIM = 1024
    SEEDS = [7]
    N_GOALS = 4
    K_FLAT = 8
    K_TREE = 4
    DEPTH = 6
    MAX_BFS_DEPTH = 8
    MIN_OPTIMAL = 4
elif RUN_MODE == "smoke":
    N_DIM = 8160  # divisible by 3 for disjoint-block (8160/3 = 2720)
    SEEDS = [7, 17]
    N_GOALS = 30
    K_FLAT = 64
    K_TREE = 16
    DEPTH = 8
    MAX_BFS_DEPTH = 12
    MIN_OPTIMAL = 6
else:
    N_DIM = 8160  # divisible by 3
    SEEDS = [7, 17, 23, 31, 41]
    N_GOALS = 100
    K_FLAT = 64
    K_TREE = 16
    DEPTH = 8
    MAX_BFS_DEPTH = 12
    MIN_OPTIMAL = 6

# Per-level block size for MECHANISM B (disjoint-block).
# 3 levels: goal-decomp / macro-binding / primitive-rollout.
BLOCK_PER_LEVEL = N_DIM // 3

EXPECTED_ARMS = [
    "reproduce_rail", "random_plan", "flat_preplay_k64_d8",
    "tree_3lvl_state_cond", "tree_3lvl_disjoint_block", "tree_3lvl_both",
]
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * N_GOALS

CHANCE_RANDOM_FLOOR = 6.0 ** (-DEPTH)
CHANCE_RANDOM_RERANK_UB = float(min(0.15, K_FLAT * CHANCE_RANDOM_FLOOR + 0.05))

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,blocks=%d,actions=%d,macros=%d,K_class=%d,goals=%d,depth=%d,"
    "K_flat=%d,K_tree=%d,block_per_lvl=%d,seeds=%s,mode=%s,"
    "HP_both>=%.2f,HP_lift_flat>=%.2f,HP_lift_sc>=%.2f,HP_lift_dj>=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel+META_AF+META_AH+META_AL+CARDINALITY"
) % (
    ANCHOR_NAME, N_DIM, N_BLOCKS, N_ACTIONS, N_MACROS, K_CLASS, N_GOALS, DEPTH,
    K_FLAT, K_TREE, BLOCK_PER_LEVEL, SEEDS, RUN_MODE,
    HP_BOTH_SOLVE_MIN, HP_BOTH_OVER_FLAT_MIN, HP_BOTH_OVER_STATE_COND_MIN,
    HP_BOTH_OVER_DISJOINT_MIN, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v1_substrate_hierarchical_planner_state_cond_disjoint",
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
            "_hardening_marker": "v1_substrate_hierarchical_planner_state_cond_disjoint_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ---------------- BlocksWorld 8-block symbolic dynamics (identical to v1) ----------------

def apply_action_sym(state: Tuple[int, ...], action_idx: int) -> Tuple[int, ...]:
    s = list(state)
    a = action_idx
    if a == 0:
        s[0] = 3
    elif a == 1:
        if s[0] == 3:
            s[0] = 0
    elif a == 2:
        if s[0] in (0, 1, 2):
            s[1] = s[0]
            s[3] = s[0]
            s[5] = s[0]
    elif a == 3:
        for bi in (1, 3, 5):
            if s[bi] in (0, 1, 2):
                s[bi] = (s[bi] + 1) % 3
    elif a == 4:
        for bi in (2, 4, 6, 7):
            if s[bi] in (0, 1, 2):
                s[bi] = (s[bi] + 1) % 3
    elif a == 5:
        s[0], s[7] = s[7], s[0]
        s[2], s[5] = s[5], s[2]
    return tuple(s)


def bfs_optimal(start: Tuple[int, ...], goal: Tuple[int, ...],
                 max_depth: int) -> Optional[Tuple[int, List[int]]]:
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


# ---------------- HD primitives (numpy; chain-grade equivalents) ----------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    A = np.fft.rfft(a)
    B = np.fft.rfft(b)
    return np.fft.irfft(A * B, n=a.shape[-1]).astype(np.float32)


def hrr_unbind(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    a_inv = np.empty_like(a)
    a_inv[0] = a[0]
    a_inv[1:] = a[:0:-1]
    return hrr_bind(c, a_inv)


def cosine_vec(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a) + 1e-8
    nb = np.linalg.norm(b) + 1e-8
    return float(np.dot(a, b) / (na * nb))


def cosine_mat(a: np.ndarray, M: np.ndarray) -> np.ndarray:
    na = np.linalg.norm(a) + 1e-8
    nM = np.linalg.norm(M, axis=1) + 1e-8
    return (M @ a) / (nM * na)


def encode_state_hd(state: Tuple[int, ...], block_role: np.ndarray,
                     pos_filler: np.ndarray, n_dim: int) -> np.ndarray:
    """Encode state into n_dim HD vector. block_role and pos_filler must have
    last-axis == n_dim (caller picks correct view for disjoint-block arms)."""
    v = np.zeros(n_dim, dtype=np.float32)
    for i, p in enumerate(state):
        v += hrr_bind(block_role[i], pos_filler[p])
    n = np.linalg.norm(v)
    if n > 1e-8:
        v = v / n
    return v


# ---------------- State-class assignment (MECHANISM A) ----------------

def state_class_id(state: Tuple[int, ...]) -> int:
    """Deterministic state-class assignment via SHA-256 hash modulo K_CLASS.
    Replaces the v1 'all-states-share-one-codebook' assumption: states in
    different classes get DIFFERENT D_macro codewords for the same macro.

    Why hash-based not Euclidean-cluster: deterministic + reproducible across
    seeds + no chicken-and-egg (clustering needs an encoder which depends on
    the codebook). Falsifiable: if class assignment is the load-bearing piece,
    we'd see ARM_TREE_STATE_COND >> ARM_TREE_DISJOINT.
    """
    h = hashlib.sha256(bytes(state)).digest()
    return int.from_bytes(h[:4], "big") % K_CLASS


# ---------------- Chunk dictionaries (per-level codebooks) ----------------

def fit_macro_dictionary_global(g: np.random.Generator,
                                  block_role: np.ndarray,
                                  pos_filler: np.ndarray,
                                  n_dim: int) -> np.ndarray:
    """V1-baseline codebook: single D_macro per macro, averaged over random
    starts. Used by ARM_TREE_DISJOINT (no state-conditioning)."""
    N_TRAIN = 200 if RUN_MODE == "full" else 60
    D = np.zeros((N_MACROS, n_dim), dtype=np.float32)
    for m_idx, m_name in enumerate(MACRO_NAMES):
        primitives = MACRO_PRIMITIVES[m_name]
        acc = np.zeros(n_dim, dtype=np.float32)
        for _ in range(N_TRAIN):
            s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
            s_pre_hd = encode_state_hd(s, block_role, pos_filler, n_dim)
            s2 = s
            for a in primitives:
                s2 = apply_action_sym(s2, a)
            s_post_hd = encode_state_hd(s2, block_role, pos_filler, n_dim)
            acc += (s_post_hd - s_pre_hd)
        D[m_idx] = acc / max(1, N_TRAIN)
    norms = np.linalg.norm(D, axis=1, keepdims=True) + 1e-8
    return D / norms


def fit_macro_dictionary_state_conditioned(g: np.random.Generator,
                                             block_role: np.ndarray,
                                             pos_filler: np.ndarray,
                                             n_dim: int) -> np.ndarray:
    """MECHANISM A: D_macro_sc[k_class, m_macro] = mean(s_post - s_pre)
    restricted to starts in class k_class.

    Returns array shape (K_CLASS, N_MACROS, n_dim). At plan-time, classify
    start-state -> look up D_macro_sc[k] for state-conditioned codebook.

    Per-class N_TRAIN sample budget keeps total work comparable to global
    fit. If a class gets fewer than 3 samples, falls back to global mean
    so codeword is non-degenerate.
    """
    N_TRAIN_TOTAL = (200 if RUN_MODE == "full" else 60) * K_CLASS
    # Per-class accumulators
    D_per_class = np.zeros((K_CLASS, N_MACROS, n_dim), dtype=np.float32)
    count_per_class = np.zeros((K_CLASS, N_MACROS), dtype=np.int64)

    # Also fit global as fallback for under-represented classes
    D_global = np.zeros((N_MACROS, n_dim), dtype=np.float32)
    count_global = 0

    for m_idx, m_name in enumerate(MACRO_NAMES):
        primitives = MACRO_PRIMITIVES[m_name]
        for _ in range(N_TRAIN_TOTAL // N_MACROS):
            s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
            k = state_class_id(s)
            s_pre_hd = encode_state_hd(s, block_role, pos_filler, n_dim)
            s2 = s
            for a in primitives:
                s2 = apply_action_sym(s2, a)
            s_post_hd = encode_state_hd(s2, block_role, pos_filler, n_dim)
            delta = s_post_hd - s_pre_hd
            D_per_class[k, m_idx] += delta
            count_per_class[k, m_idx] += 1
            D_global[m_idx] += delta
            count_global += 1

    # Mean per class; fallback to global for classes with < 3 samples
    for k in range(K_CLASS):
        for m_idx in range(N_MACROS):
            c = count_per_class[k, m_idx]
            if c < 3:
                # Fallback: global mean (still better than zero)
                if count_global > 0:
                    D_per_class[k, m_idx] = D_global[m_idx] / max(1, count_global // N_MACROS)
            else:
                D_per_class[k, m_idx] = D_per_class[k, m_idx] / c

    # Normalize per (k, m)
    for k in range(K_CLASS):
        norms = np.linalg.norm(D_per_class[k], axis=1, keepdims=True) + 1e-8
        D_per_class[k] = D_per_class[k] / norms
    return D_per_class


# ---------------- Planners ----------------

def plan_oracle_bfs(start: Tuple[int, ...], goal: Tuple[int, ...],
                     opt_plan: List[int]) -> Tuple[List[int], bool]:
    s = start
    for a in opt_plan:
        s = apply_action_sym(s, a)
    return list(opt_plan), (s == goal)


def plan_random_rerank(start: Tuple[int, ...], goal: Tuple[int, ...],
                        block_role: np.ndarray, pos_filler: np.ndarray,
                        n_dim: int, K: int, D: int,
                        g: np.random.Generator) -> Tuple[List[int], bool]:
    goal_hd = encode_state_hd(goal, block_role, pos_filler, n_dim)
    best_seq: Optional[List[int]] = None
    best_score = -1e9
    best_solved = False
    for _ in range(K):
        s = start
        seq: List[int] = []
        solved = False
        for _d in range(D):
            if s == goal:
                solved = True
                break
            a = int(g.integers(0, N_ACTIONS))
            seq.append(a)
            s = apply_action_sym(s, a)
        if s == goal:
            solved = True
        s_hd = encode_state_hd(s, block_role, pos_filler, n_dim)
        score = cosine_vec(s_hd, goal_hd)
        if solved:
            if not best_solved or len(seq) < len(best_seq):
                best_solved = True
                best_seq = seq
                best_score = score
        elif not best_solved and score > best_score:
            best_score = score
            best_seq = seq
    return (best_seq or [], best_solved)


def plan_flat_preplay(start: Tuple[int, ...], goal: Tuple[int, ...],
                       block_role: np.ndarray, pos_filler: np.ndarray,
                       n_dim: int, K: int, D: int,
                       g: np.random.Generator) -> Tuple[List[int], bool]:
    """v1-baseline: flat-K=64 preplay with softmax goal-conditioning."""
    goal_hd = encode_state_hd(goal, block_role, pos_filler, n_dim)
    best_seq: Optional[List[int]] = None
    best_score = -1e9
    best_solved = False
    for _ in range(K):
        s = start
        seq: List[int] = []
        solved = False
        for _d in range(D):
            if s == goal:
                solved = True
                break
            scores = []
            for a in range(N_ACTIONS):
                ns = apply_action_sym(s, a)
                ns_hd = encode_state_hd(ns, block_role, pos_filler, n_dim)
                sc = cosine_vec(ns_hd, goal_hd)
                scores.append(sc + 0.05 * float(g.standard_normal()))
            arr = np.array(scores)
            arr = arr - arr.max()
            p = np.exp(arr / 0.1)
            p = p / p.sum()
            a_pick = int(g.choice(N_ACTIONS, p=p))
            seq.append(a_pick)
            s = apply_action_sym(s, a_pick)
        if s == goal:
            solved = True
        s_hd = encode_state_hd(s, block_role, pos_filler, n_dim)
        score = cosine_vec(s_hd, goal_hd)
        if solved:
            if not best_solved or len(seq) < len(best_seq):
                best_solved = True
                best_seq = seq
                best_score = score
        elif not best_solved and score > best_score:
            best_score = score
            best_seq = seq
    return (best_seq or [], best_solved)


def _decompose_via_codebook(start: Tuple[int, ...], goal: Tuple[int, ...],
                              block_role: np.ndarray, pos_filler: np.ndarray,
                              n_dim: int,
                              D_macro_lookup: np.ndarray,
                              K_branches: int,
                              g: np.random.Generator,
                              use_state_cond: bool) -> List[List[int]]:
    """Decompose goal into B_SLOTS macro-indices using D_macro_lookup codebook.

    use_state_cond=True: D_macro_lookup is (K_CLASS, N_MACROS, n_dim); look up
      D_macro_lookup[state_class_id(start)].
    use_state_cond=False: D_macro_lookup is (N_MACROS, n_dim); use directly.

    Returns K_branches candidate macro-decompositions, each B_SLOTS long.
    """
    goal_hd = encode_state_hd(goal, block_role, pos_filler, n_dim)
    start_hd = encode_state_hd(start, block_role, pos_filler, n_dim)
    delta_hd = goal_hd - start_hd
    norms = np.linalg.norm(delta_hd)
    if norms > 1e-8:
        delta_hd = delta_hd / norms

    if use_state_cond:
        k = state_class_id(start)
        D_macro = D_macro_lookup[k]
    else:
        D_macro = D_macro_lookup

    B_SLOTS = 4
    mid_roles = bipolar(B_SLOTS, n_dim, g)

    candidate_decomps: List[List[int]] = []
    for _branch in range(K_branches):
        b_rng = np.random.default_rng(int(g.integers(0, 2**31)))
        decomp: List[int] = []
        residual = delta_hd.copy()
        for slot_idx in range(B_SLOTS):
            macro_scores = cosine_mat(residual, D_macro)
            macro_scores = macro_scores + 0.05 * b_rng.standard_normal(N_MACROS).astype(np.float32)
            # Per-level cleanup: argmax (the Plate ch.6 mechanism)
            m_idx = int(np.argmax(macro_scores))
            decomp.append(m_idx)
            chosen = D_macro[m_idx]
            explained = hrr_bind(mid_roles[slot_idx], chosen)
            residual = residual - 0.3 * explained
            nr = np.linalg.norm(residual)
            if nr > 1e-8:
                residual = residual / nr
        candidate_decomps.append(decomp)
    return candidate_decomps


def plan_hrr_tree_combined(start: Tuple[int, ...], goal: Tuple[int, ...],
                             block_role_full: np.ndarray, pos_filler_full: np.ndarray,
                             block_role_lvl1: np.ndarray, pos_filler_lvl1: np.ndarray,
                             D_macro_lookup: np.ndarray,
                             K_branches: int, max_steps: int,
                             g: np.random.Generator,
                             use_state_cond: bool,
                             use_disjoint_block: bool) -> Tuple[List[int], bool]:
    """3-level HRR tree planner with optional state-conditioning + disjoint-block.

    use_state_cond=True: D_macro_lookup is (K_CLASS, N_MACROS, dim).
    use_disjoint_block=True: decomposition uses lvl1 block_role/pos_filler (dim=BLOCK_PER_LEVEL);
      rollout uses the full block_role/pos_filler (dim=N_DIM).
    use_disjoint_block=False: decomposition uses full block_role/pos_filler (dim=N_DIM).

    Returns (best_seq, solved). Tree branches over K_branches candidate decompositions;
    each candidate is expanded to primitives via MACRO_PRIMITIVES; final state simulated;
    re-ranked by cos(s_final_hd_full, goal_hd_full) at level 3.
    """
    if use_disjoint_block:
        decomp_role = block_role_lvl1
        decomp_pos = pos_filler_lvl1
        decomp_dim = BLOCK_PER_LEVEL
    else:
        decomp_role = block_role_full
        decomp_pos = pos_filler_full
        decomp_dim = N_DIM

    candidates = _decompose_via_codebook(
        start, goal, decomp_role, decomp_pos, decomp_dim,
        D_macro_lookup, K_branches, g, use_state_cond,
    )

    # Level 3 readout: simulate primitive rollouts; rerank by goal-cosine in full-dim space
    goal_hd_full = encode_state_hd(goal, block_role_full, pos_filler_full, N_DIM)
    best_seq: Optional[List[int]] = None
    best_score = -1e9
    best_solved = False
    for macro_seq in candidates:
        prim_seq: List[int] = []
        for m_idx in macro_seq:
            m_name = MACRO_NAMES[m_idx]
            prim_seq.extend(MACRO_PRIMITIVES[m_name])
            if len(prim_seq) >= max_steps:
                break
        prim_seq = prim_seq[:max_steps]
        s = start
        actual: List[int] = []
        solved = False
        for a in prim_seq:
            if s == goal:
                solved = True
                break
            actual.append(a)
            s = apply_action_sym(s, a)
            if s == goal:
                solved = True
                break
        s_hd = encode_state_hd(s, block_role_full, pos_filler_full, N_DIM)
        score = cosine_vec(s_hd, goal_hd_full)
        if solved:
            if not best_solved or len(actual) < len(best_seq):
                best_solved = True
                best_seq = actual
                best_score = score
        elif not best_solved and score > best_score:
            best_score = score
            best_seq = actual
    return (best_seq or [], best_solved)


# ---------------- per-seed runner ----------------

def sample_composite_goal(g: np.random.Generator, max_bfs_depth: int,
                           min_optimal: int = 6,
                           max_attempts: int = 400
                           ) -> Tuple[Tuple[int, ...], Tuple[int, ...], int, List[int]]:
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

    # Full-dim role/filler (for rollout + non-disjoint planners)
    block_role_full = bipolar(N_BLOCKS, N_DIM, g)
    pos_filler_full = bipolar(N_POS, N_DIM, g)

    # Level-1 disjoint block: separate independent role/filler at dim=BLOCK_PER_LEVEL.
    # This is the key MECHANISM B operation: decomposition runs in its OWN
    # dim-block so cleanup at level-1 cannot bleed into level-2/3 representations.
    block_role_lvl1 = bipolar(N_BLOCKS, BLOCK_PER_LEVEL, g)
    pos_filler_lvl1 = bipolar(N_POS, BLOCK_PER_LEVEL, g)

    # Sample composite goals once for this seed (fair across arms)
    goals: List[Tuple[Tuple[int, ...], Tuple[int, ...], int, List[int]]] = []
    for _ in range(N_GOALS):
        goals.append(sample_composite_goal(g, MAX_BFS_DEPTH, min_optimal=MIN_OPTIMAL))

    # Fit codebooks
    # Global codebook (full-dim) for DISJOINT-only arm (no state-cond)
    D_macro_global_full = fit_macro_dictionary_global(g, block_role_full, pos_filler_full, N_DIM)
    # Global codebook (lvl1-dim) for DISJOINT-only arm requires lvl1-dim codebook too
    D_macro_global_lvl1 = fit_macro_dictionary_global(g, block_role_lvl1, pos_filler_lvl1, BLOCK_PER_LEVEL)
    # State-conditioned codebook (full-dim) for STATE_COND-only arm
    D_macro_sc_full = fit_macro_dictionary_state_conditioned(g, block_role_full, pos_filler_full, N_DIM)
    # State-conditioned codebook (lvl1-dim) for BOTH arm
    D_macro_sc_lvl1 = fit_macro_dictionary_state_conditioned(g, block_role_lvl1, pos_filler_lvl1, BLOCK_PER_LEVEL)

    arm_runners = [
        ("reproduce_rail",
            lambda s, gl, opt, plan, ag: plan_oracle_bfs(s, gl, plan)),
        ("random_plan",
            lambda s, gl, opt, plan, ag: plan_random_rerank(
                s, gl, block_role_full, pos_filler_full, N_DIM, K_FLAT, DEPTH, ag)),
        ("flat_preplay_k64_d8",
            lambda s, gl, opt, plan, ag: plan_flat_preplay(
                s, gl, block_role_full, pos_filler_full, N_DIM, K_FLAT, DEPTH, ag)),
        ("tree_3lvl_state_cond",
            # MECHANISM A only: state-conditioned, NO disjoint-block
            lambda s, gl, opt, plan, ag: plan_hrr_tree_combined(
                s, gl, block_role_full, pos_filler_full,
                block_role_lvl1, pos_filler_lvl1,
                D_macro_sc_full,
                K_TREE, DEPTH, ag,
                use_state_cond=True, use_disjoint_block=False)),
        ("tree_3lvl_disjoint_block",
            # MECHANISM B only: disjoint-block, NO state-conditioning
            lambda s, gl, opt, plan, ag: plan_hrr_tree_combined(
                s, gl, block_role_full, pos_filler_full,
                block_role_lvl1, pos_filler_lvl1,
                D_macro_global_lvl1,
                K_TREE, DEPTH, ag,
                use_state_cond=False, use_disjoint_block=True)),
        ("tree_3lvl_both",
            # FULL MECHANISM: state-conditioned + disjoint-block
            lambda s, gl, opt, plan, ag: plan_hrr_tree_combined(
                s, gl, block_role_full, pos_filler_full,
                block_role_lvl1, pos_filler_lvl1,
                D_macro_sc_lvl1,
                K_TREE, DEPTH, ag,
                use_state_cond=True, use_disjoint_block=True)),
    ]

    per_arm: Dict[str, Dict[str, Any]] = {}
    per_arm_seqs: Dict[str, List[List[int]]] = {}
    for arm_name, runner in arm_runners:
        n_solved = 0
        plan_lens: List[int] = []
        ratios: List[float] = []
        seqs_for_hash: List[List[int]] = []
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
            "median_plan_len": float(np.median(plan_lens)) if plan_lens else float(DEPTH),
            "median_plan_ratio_vs_optimal": float(np.median(ratios)) if ratios else float("inf"),
            "_seq_hash": _seq_hash(seqs_for_hash),
        }
        per_arm_seqs[arm_name] = seqs_for_hash

    # META_RULE_AF: verify arms_distinct (per-arm seq-hash must differ on critical pairs)
    hashes = {arm: per_arm[arm]["_seq_hash"] for arm in per_arm}
    critical_pairs = [
        ("reproduce_rail", "tree_3lvl_both"),
        ("tree_3lvl_both", "tree_3lvl_state_cond"),
        ("tree_3lvl_both", "tree_3lvl_disjoint_block"),
        ("flat_preplay_k64_d8", "tree_3lvl_both"),
        ("random_plan", "tree_3lvl_both"),
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

    rail = summary["reproduce_rail"]["solve_rate_mean"]
    rand = summary["random_plan"]["solve_rate_mean"]
    flat = summary["flat_preplay_k64_d8"]["solve_rate_mean"]
    sc = summary["tree_3lvl_state_cond"]["solve_rate_mean"]
    dj = summary["tree_3lvl_disjoint_block"]["solve_rate_mean"]
    both = summary["tree_3lvl_both"]["solve_rate_mean"]
    both_cv = summary["tree_3lvl_both"].get("solve_rate_cv", float("inf"))

    lift_over_flat = both - flat
    lift_over_sc = both - sc
    lift_over_dj = both - dj

    arms_distinct_all = bool(arms_distinct_seeds and all(arms_distinct_seeds))

    verdict = "MIDDLE_BAND"
    if rail < HP_RAIL_MIN:
        verdict = "HARD_FAIL"
        reason = "RAIL_BROKEN (rail=%.3f < %.2f)" % (rail, HP_RAIL_MIN)
    elif not arms_distinct_all:
        verdict = "HARD_FAIL"
        reason = "ARMS_NOT_DISTINCT (cell bug; per-arm hashes collide)"
    elif rand > HF_RAND_MAX:
        verdict = "HARD_FAIL"
        reason = "SANITY_BREACH_RANDOM (rand=%.3f > %.2f; domain trivial)" % (rand, HF_RAND_MAX)
    elif both <= flat:
        verdict = "HARD_FAIL"
        reason = "BOTH_NO_LIFT_OVER_FLAT (both=%.3f <= flat=%.3f; mechanism still useless)" % (both, flat)
    elif (both >= HP_BOTH_SOLVE_MIN and
            lift_over_flat >= HP_BOTH_OVER_FLAT_MIN and
            lift_over_sc >= HP_BOTH_OVER_STATE_COND_MIN and
            lift_over_dj >= HP_BOTH_OVER_DISJOINT_MIN and
            both_cv < HP_CV_MAX):
        verdict = "HARD_PASS"
        reason = "ALL_HP_BANDS_MET"
    elif MB_BOTH_SOLVE_LO <= both < MB_BOTH_SOLVE_HI:
        verdict = "MIDDLE_BAND"
        reason = "MB_band (both=%.3f lift_flat=%.3f lift_sc=%.3f lift_dj=%.3f)" % (
            both, lift_over_flat, lift_over_sc, lift_over_dj)
    else:
        verdict = "MIDDLE_BAND"
        reason = "below_MB_but_above_HF"

    verdict_msg = (
        "%s | %s | RAIL=%.3f RAND=%.3f FLAT=%.3f SC=%.3f DJ=%.3f BOTH=%.3f | "
        "BOTH-FLAT=%.3f BOTH-SC=%.3f BOTH-DJ=%.3f cv=%.3f arms_distinct=%s "
        "chance_floor=%.4g"
    ) % (verdict, reason, rail, rand, flat, sc, dj, both,
         lift_over_flat, lift_over_sc, lift_over_dj, both_cv,
         arms_distinct_all, CHANCE_RANDOM_FLOOR)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "both_minus_flat": float(lift_over_flat),
        "both_minus_state_cond": float(lift_over_sc),
        "both_minus_disjoint": float(lift_over_dj),
        "arms_distinct": arms_distinct_all,
        "n_seeds_complete": len(per_seed),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(per_seed) * len(EXPECTED_ARMS) * N_GOALS,
        "cardinality_ok": (len(per_seed) >= max(1, len(SEEDS) - 1)),
        "chance_random_floor": float(CHANCE_RANDOM_FLOOR),
        "chance_random_rerank_ub": float(CHANCE_RANDOM_RERANK_UB),
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

    print("[%s] mode=%s N=%d blocks=%d goals=%d depth=%d K_flat=%d K_tree=%d K_class=%d block_per_lvl=%d seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_BLOCKS, N_GOALS, DEPTH, K_FLAT, K_TREE,
        K_CLASS, BLOCK_PER_LEVEL, SEEDS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r, "missing per_arm"
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
            rail = r["per_arm"]["reproduce_rail"]["solve_rate"]
            both = r["per_arm"]["tree_3lvl_both"]["solve_rate"]
            sc = r["per_arm"]["tree_3lvl_state_cond"]["solve_rate"]
            dj = r["per_arm"]["tree_3lvl_disjoint_block"]["solve_rate"]
            flat = r["per_arm"]["flat_preplay_k64_d8"]["solve_rate"]
            rand = r["per_arm"]["random_plan"]["solve_rate"]
            assert rail >= 0.99, "RAIL_BROKEN at selftest: rail=%.3f" % rail
            assert r["arms_distinct"], "ARMS_NOT_DISTINCT at selftest"
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: rail=%.3f both=%.3f sc=%.3f dj=%.3f flat=%.3f rand=%.3f" % (
                                       rail, both, sc, dj, flat, rand),
                                   extra={"_phase": "selftest_done",
                                          "selftest_arms": list(r["per_arm"].keys()),
                                          "rail_solve": rail, "both_solve": both,
                                          "sc_solve": sc, "dj_solve": dj,
                                          "flat_solve": flat, "rand_solve": rand,
                                          "arms_distinct": r["arms_distinct"]})
            print("[selftest] OK; rail=%.3f both=%.3f sc=%.3f dj=%.3f flat=%.3f rand=%.3f distinct=%s" % (
                rail, both, sc, dj, flat, rand, r["arms_distinct"]), flush=True)
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
    final["_hardening_marker"] = "v1_substrate_hierarchical_planner_state_cond_disjoint"
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
