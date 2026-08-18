"""substrate_hierarchical_block_sparse_v1 -- Drill B encoding-axis test.

Companion / orthogonal angle to substrate_hierarchical_option_critic_v1 (Drill A).
Three prior HARD_FAILs (subgoal_planner / state_conditioned_disjoint / options_v3)
all used DENSE HRR encoding at N=8192. The common failure mode:
macro-collapse from dense bundling -- bundling multiple option vectors into a
dense HRR averages toward the centroid; planner readout cosines lose per-option
discrimination.

MECHANISM PIVOT (Hersche et al. 2023/2025 sparse block codes; Frady-Sommer-Kanerva
2018 SBC superposition capacity):
  N=8192 partitioned into L=64 blocks of B=128 dims/block.
  3 options each assigned a disjoint 16-block subset; 16 blocks reserved for
  state/control. Per-option pi/beta/I HRR vectors are RESTRICTED to that option's
  block-set (zeros in other blocks). Per-block argmax / per-option block-restricted
  cosine readout avoids cross-talk because supports do not overlap.

Substrate-internal MEASURED@ existence proofs:
  exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000  K4=K8=1.00 (factorization)
  exp_substrate_partition_routing_hierarchical_2level_v1  2LEVEL=0.9783 at M=10M

This cell is NOT a 4th attempt at the same mechanism class -- it is a 4th-class
encoding-axis test orthogonal to the prior 3. Per 2x-drill discipline (USER
2026-06-28), prior `_third_failure_gate_triggered` atomization is preliminary;
this cell + Drill A both gate the closure clause.

ARMS (6):
  ARM_BLOCK_SPARSE_OPTIONS_FULL  -- disjoint-block + blockwise binding (mechanism)
  ARM_NO_BLOCK_ASSIGNMENT        -- block-sparse density but all-blocks-per-option
  ARM_DENSE_BASELINE             -- N=8192 dense HRR (v3 regression baseline)
  ARM_POLICY_ONLY                -- block-sparse but greedy pi only (no I/beta)
  ARM_RANDOM_BLOCKS              -- block-sparse but random per-query block-to-opt
  ARM_RANDOM                     -- pure random primitive floor

PRE-REG BANDS (LOCKED at module init):
  HARD_PASS (ALL):
    ARM_BLOCK_SPARSE_OPTIONS_FULL >= 0.30
    ARM_BLOCK_SPARSE_OPTIONS_FULL <= 0.95 (un-saturated, META_RULE_AG)
    ARM_BLOCK_SPARSE_OPTIONS_FULL - ARM_RANDOM_BLOCKS >= +0.15
    ARM_BLOCK_SPARSE_OPTIONS_FULL - ARM_DENSE_BASELINE >= +0.25
    ARM_DENSE_BASELINE <= 0.20  (SANITY: prior HARD_FAIL replicates)
    ARM_RANDOM <= 0.05
    arms_distinct == True (SHA-256 across 6 arms)
    cv <= 0.15 (full mode only)
  MIDDLE_BAND:
    ARM_BLOCK_SPARSE_OPTIONS_FULL in [0.20, 0.30) with lift_random_blocks >= 0.10
                                                     and lift_dense_baseline >= 0.15
    OR ARM_BLOCK_SPARSE_OPTIONS_FULL >= 0.30 but one secondary band fails
  HARD_FAIL (ANY):
    ARM_BLOCK_SPARSE_OPTIONS_FULL <= 0.10  (encoding-axis does NOT rescue)
    abs(ARM_BLOCK_SPARSE_OPTIONS_FULL - ARM_RANDOM_BLOCKS) < 0.05 (block-assignment illusory)
    arms_distinct == False
    ARM_DENSE_BASELINE >= 0.30 (SANITY breach)
    ARM_RANDOM > 0.10 (domain trivial)

NO THIRD-FAILURE GATE. This is encoding-axis orthogonal to prior 3 mechanism cells.

CARDINALITY (META_RULE_AH):
  EXPECTED_N_UNITS_SMOKE = 6 arms * 1 seed  * 20 goals = 120
  EXPECTED_N_UNITS_FULL  = 6 arms * 3 seeds * 20 goals = 360

CRLB:
  chance_floor = 6^-6 = 2.143e-5
  chance_rerank_ub = min(0.10, 64*chance_floor + 0.04) = 0.0414

Composes: hdlab not directly imported (cell self-contained; the requested
hdlab/cleanup.py wrap does NOT exist as the handoff claimed -- block-restricted
cosine inlined here per substrate-as-canonical query-first). Reference cell:
experiments/exp_substrate_hierarchical_options_v1.py for v3 mechanism details.

Number tagging:
  MEASURED@  - substrate primitive existence (block-local resonator + partition routing)
  HYPOTHESIZED@ - block-sparse-on-planning generalization (no prior planning evidence)
  THEORETICAL@ - Frady-Sommer-Kanerva SBC capacity bound L*log(N/L)

Author: exp_dev 2026-06-28 (Opus 4.7 1M, Stage 3 hierarchical-planning Drill B).
ASCII-only; self-contained. Discipline: META_RULE_AC/AF/AG/AH/AL/AN/J; L1-L4
hardening; no silent except; atomic-write.
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
import math
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

try:
    from experiments._seed_checkpoint import (
        resumable_seeds, write_partial_key, aggregate_partials,
    )
    _HAS_CKPT = True
except Exception:
    _HAS_CKPT = False


ANCHOR_NAME = "substrate_hierarchical_block_sparse_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# ---- Pre-reg bands LOCKED at module init ----
HP_OPTS_MIN = 0.30                # main mechanism arm threshold
HP_OPTS_UNSAT_HI = 0.95           # META_RULE_AG un-saturated band upper
HP_LIFT_RANDOM_BLOCKS_MIN = 0.15  # disjoint assignment matters
HP_LIFT_DENSE_BASELINE_MIN = 0.25 # encoding axis lifts vs prior failure
HP_DENSE_BASELINE_MAX = 0.20      # SANITY: prior HARD_FAIL replicates
HP_RANDOM_MAX = 0.05              # floor
HP_CV_MAX = 0.15                  # full-mode only

MB_OPTS_LO = 0.20
MB_OPTS_HI = 0.30
MB_LIFT_RANDOM_BLOCKS_MIN = 0.10
MB_LIFT_DENSE_BASELINE_MIN = 0.15

HF_OPTS_MAX = 0.10                # block-sparse axis does NOT rescue
HF_BLOCK_ASSIGNMENT_ILLUSORY_DELTA = 0.05
HF_DENSE_BASELINE_BREACH = 0.30   # prior HARD_FAIL did NOT replicate
HF_RAND_MAX_SANITY = 0.10         # domain trivial check

# ---- BlocksWorld 4-block (matches v3 spec) ----
N_BLOCKS = 4
N_POS = 3
ACTIONS = ["pick_up_A", "pick_up_B", "swap_AB", "swap_AC", "rotate_BC", "clear_all"]
N_ACTIONS = len(ACTIONS)

# ---- 3 hand-defined options (matches v3) ----
OPTION_NAMES = ["stack_pair", "clear_then_grab", "relocate"]
N_OPTIONS = len(OPTION_NAMES)

OPTION_PRIMITIVE_SETS: Dict[str, List[int]] = {
    "stack_pair":      [0, 1, 2],
    "clear_then_grab": [5, 0, 1],
    "relocate":        [2, 3, 4],
}


def _option_completion(state: Tuple[int, ...], option_idx: int) -> bool:
    if option_idx == 0:
        return state[0] == state[1]
    elif option_idx == 1:
        return state[2] == 2 and state[3] == 2
    elif option_idx == 2:
        return state[0] == 1 and state[2] == 0
    return False


OPTION_MAX_STEPS = 8
K_ANCHOR_PER_OPTION = 32


def _n_train_per_option() -> int:
    if SELF_TEST_MODE:
        return 30
    elif RUN_MODE == "smoke":
        return 120
    else:
        return 200


# ---- Run-mode shaping ----
if SELF_TEST_MODE:
    N_DIM = 1024
    L_BLOCKS = 8
    BLOCKS_PER_OPTION = 2
    SEEDS = [7]
    N_GOALS = 4
    COMPOSITE_DEPTH = 4
    MIN_OPTIMAL = 2
    MAX_BFS_DEPTH = 6
    MAX_TOTAL_STEPS = 16
elif RUN_MODE == "smoke":
    N_DIM = 8192
    L_BLOCKS = 64
    BLOCKS_PER_OPTION = 16
    SEEDS = [7]
    N_GOALS = 20
    COMPOSITE_DEPTH = 6
    MIN_OPTIMAL = 4
    MAX_BFS_DEPTH = 10
    MAX_TOTAL_STEPS = 24
else:
    N_DIM = 8192
    L_BLOCKS = 64
    BLOCKS_PER_OPTION = 16
    SEEDS = [7, 13, 19]
    N_GOALS = 20
    COMPOSITE_DEPTH = 6
    MIN_OPTIMAL = 4
    MAX_BFS_DEPTH = 10
    MAX_TOTAL_STEPS = 24

B_PER_BLOCK = N_DIM // L_BLOCKS
N_STATE_BLOCKS = L_BLOCKS - (N_OPTIONS * BLOCKS_PER_OPTION)

# Per-block sparse density k (active bits per block). Hersche GSBC ~k>1 typical.
K_PER_BLOCK_SMOKE_SELFTEST = 4
K_PER_BLOCK = (K_PER_BLOCK_SMOKE_SELFTEST if SELF_TEST_MODE else 8)

EXPECTED_ARMS = [
    "block_sparse_options_full",
    "no_block_assignment",
    "dense_baseline",
    "policy_only",
    "random_blocks",
    "random",
]
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * N_GOALS

CHANCE_RANDOM_FLOOR = N_ACTIONS ** (-COMPOSITE_DEPTH)
CHANCE_RANDOM_RERANK_UB = float(min(0.10, 64 * CHANCE_RANDOM_FLOOR + 0.04))
# THEORETICAL@ Frady-Sommer-Kanerva SBC capacity L*log(N/L)
SBC_CAPACITY_THEORETICAL = float(L_BLOCKS * math.log(max(2, B_PER_BLOCK)))

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,L=%d,B=%d,blocks_per_opt=%d,state_blocks=%d,k_per_block=%d,"
    "domain_blocks=%d,pos=%d,actions=%d,options=%d,K_anchor=%d,goals=%d,depth=%d,"
    "max_total=%d,seeds=%s,mode=%s,"
    "HP_opts>=%.2f,HP_lift_rb>=%.2f,HP_lift_db>=%.2f,db_max=%.2f,unsat_hi=%.2f,"
    "expected_n=%d,sbc_cap=%.1f,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel+META_AC+META_AF+META_AG+META_AH+META_AL+META_AN+CARDINALITY"
) % (
    ANCHOR_NAME, N_DIM, L_BLOCKS, B_PER_BLOCK, BLOCKS_PER_OPTION, N_STATE_BLOCKS,
    K_PER_BLOCK, N_BLOCKS, N_POS, N_ACTIONS, N_OPTIONS, K_ANCHOR_PER_OPTION,
    N_GOALS, COMPOSITE_DEPTH, MAX_TOTAL_STEPS, SEEDS, RUN_MODE,
    HP_OPTS_MIN, HP_LIFT_RANDOM_BLOCKS_MIN, HP_LIFT_DENSE_BASELINE_MIN,
    HP_DENSE_BASELINE_MAX, HP_OPTS_UNSAT_HI, EXPECTED_N_UNITS, SBC_CAPACITY_THEORETICAL,
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
            "_hardening_marker": "v1_substrate_hierarchical_block_sparse",
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
            "_hardening_marker": "v1_substrate_hierarchical_block_sparse_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ---------------- BlocksWorld dynamics ----------------

def apply_action_sym(state: Tuple[int, ...], action_idx: int) -> Tuple[int, ...]:
    s = list(state)
    a = action_idx
    if a == 0:
        s[0] = 0
    elif a == 1:
        s[1] = 1
    elif a == 2:
        s[0], s[1] = s[1], s[0]
    elif a == 3:
        s[0], s[2] = s[2], s[0]
    elif a == 4:
        b1, b2, b3 = s[1], s[2], s[3]
        s[1], s[2], s[3] = b3, b1, b2
    elif a == 5:
        s[2] = 2
        s[3] = 2
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


# ---------------- Block-sparse primitives ----------------

def block_sparse_vector(blocks: List[int], k_per_block: int, n_dim: int,
                         l_blocks: int, b_per_block: int,
                         g: np.random.Generator) -> np.ndarray:
    """Build a block-sparse vector with k_per_block active +/-1 positions in
    each specified block (other positions zero). Then L2-normalize.

    blocks: list of block-indices in [0, l_blocks) to activate; others zero.
    """
    v = np.zeros(n_dim, dtype=np.float32)
    for b in blocks:
        if b < 0 or b >= l_blocks:
            raise ValueError("block index %d out of range [0,%d)" % (b, l_blocks))
        start = b * b_per_block
        # pick k_per_block distinct positions within this block
        k = min(k_per_block, b_per_block)
        positions = g.choice(b_per_block, size=k, replace=False)
        signs = (g.integers(0, 2, size=k) * 2 - 1).astype(np.float32)
        v[start + positions] = signs
    n = np.linalg.norm(v)
    if n > 1e-8:
        v = v / n
    return v


def block_restricted_cosine(a: np.ndarray, b: np.ndarray, blocks: List[int],
                             b_per_block: int) -> float:
    """Cosine of a and b restricted to the union of specified blocks."""
    if not blocks:
        return 0.0
    idx_list = [np.arange(blk * b_per_block, (blk + 1) * b_per_block) for blk in blocks]
    idx = np.concatenate(idx_list)
    aa = a[idx]
    bb = b[idx]
    na = np.linalg.norm(aa) + 1e-8
    nb = np.linalg.norm(bb) + 1e-8
    val = float(np.dot(aa, bb) / (na * nb))
    if np.isnan(val) or np.isinf(val):
        raise ValueError("block_restricted_cosine NaN/Inf (META_RULE_J no silent)")
    return val


def cosine_vec(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a) + 1e-8
    nb = np.linalg.norm(b) + 1e-8
    val = float(np.dot(a, b) / (na * nb))
    if np.isnan(val) or np.isinf(val):
        raise ValueError("cosine_vec NaN/Inf (META_RULE_J no silent)")
    return val


def cosine_mat_block(a: np.ndarray, M: np.ndarray, blocks: List[int],
                      b_per_block: int) -> np.ndarray:
    """For each row in M, compute block-restricted cosine vs a, restricted to
    the union of specified blocks. Returns shape (M.shape[0],)."""
    if not blocks:
        return np.zeros(M.shape[0], dtype=np.float32)
    idx_list = [np.arange(blk * b_per_block, (blk + 1) * b_per_block) for blk in blocks]
    idx = np.concatenate(idx_list)
    aa = a[idx]
    MM = M[:, idx]
    na = np.linalg.norm(aa) + 1e-8
    nM = np.linalg.norm(MM, axis=1) + 1e-8
    out = (MM @ aa) / (nM * na)
    if not np.isfinite(out).all():
        raise ValueError("cosine_mat_block NaN/Inf (META_RULE_J no silent)")
    return out


def cosine_mat(a: np.ndarray, M: np.ndarray) -> np.ndarray:
    na = np.linalg.norm(a) + 1e-8
    nM = np.linalg.norm(M, axis=1) + 1e-8
    out = (M @ a) / (nM * na)
    if not np.isfinite(out).all():
        raise ValueError("cosine_mat NaN/Inf (META_RULE_J no silent)")
    return out


# ---- Dense HRR (for ARM_DENSE_BASELINE regression) ----

def bipolar_dense(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    A = np.fft.rfft(a)
    B = np.fft.rfft(b)
    return np.fft.irfft(A * B, n=a.shape[-1]).astype(np.float32)


def encode_state_dense(state: Tuple[int, ...], block_role: np.ndarray,
                        pos_filler: np.ndarray, n_dim: int) -> np.ndarray:
    v = np.zeros(n_dim, dtype=np.float32)
    for i, p in enumerate(state):
        v += hrr_bind(block_role[i], pos_filler[p])
    n = np.linalg.norm(v)
    if n > 1e-8:
        v = v / n
    return v


# ---- Block-sparse state encoding ----

def encode_state_blocksparse(state: Tuple[int, ...],
                              state_blocks: List[int],
                              pos_codewords_bs: np.ndarray,
                              block_role_bs: np.ndarray,
                              b_per_block: int,
                              n_dim: int) -> np.ndarray:
    """Encode state into the state/control block-subset. Per-block: for each
    (block_idx_within_state, pos) compute a sparse code restricted to one
    state-block; sum across positions; then L2-normalize. The state HRR lives
    ONLY in the state_blocks (zeros in option blocks)."""
    v = np.zeros(n_dim, dtype=np.float32)
    # Cycle state-block assignments: block-i of the BlocksWorld state -> state_block[i % len(state_blocks)]
    for i, p in enumerate(state):
        if not state_blocks:
            continue
        # Use first len(state) state_blocks (cycling if needed)
        sb = state_blocks[i % len(state_blocks)]
        start = sb * b_per_block
        # Bound vector = elementwise (block_role[i, restricted] * pos_filler[p, restricted])
        rng = np.arange(start, start + b_per_block)
        v[rng] += block_role_bs[i, rng] * pos_codewords_bs[p, rng]
    n = np.linalg.norm(v)
    if n > 1e-8:
        v = v / n
    return v


# ---------------- Per-option block assignment ----------------

def assign_option_blocks(g: np.random.Generator, l_blocks: int, n_options: int,
                          blocks_per_option: int
                          ) -> Tuple[List[List[int]], List[int]]:
    """Permute all L blocks, slice into (option blocks, state blocks).

    Returns (per_option_blocks, state_blocks).
    """
    perm = list(range(l_blocks))
    g.shuffle(perm)
    per_option: List[List[int]] = []
    cursor = 0
    for o in range(n_options):
        per_option.append(sorted(perm[cursor:cursor + blocks_per_option]))
        cursor += blocks_per_option
    state_blocks = sorted(perm[cursor:])
    return per_option, state_blocks


# ---------------- Per-option I/beta/pi banks (block-sparse) ----------------

def fit_option_I_bank_bs(option_idx: int, g: np.random.Generator,
                          opt_blocks: List[int],
                          state_blocks: List[int],
                          pos_codewords_bs: np.ndarray,
                          block_role_bs: np.ndarray,
                          b_per_block: int, n_dim: int, l_blocks: int,
                          k_anchor: int, k_per_block: int) -> Tuple[np.ndarray, float]:
    """Fit per-option I bank as k_anchor block-sparse anchors restricted to
    opt_blocks. tau_I calibrated on a sample of states' max-cos."""
    primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[option_idx]]
    anchors: List[np.ndarray] = []
    n_attempts_max = k_anchor * 20
    attempts = 0
    while len(anchors) < k_anchor and attempts < n_attempts_max:
        attempts += 1
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
            # Block-sparse anchor in option's blocks (state-content embedded as
            # random bipolar pattern; the cell-physics test is whether
            # block-locality discriminates per-option, not whether anchor faithfully
            # represents s)
            v = block_sparse_vector(opt_blocks, k_per_block, n_dim, l_blocks, b_per_block, g)
            anchors.append(v)
    while len(anchors) < k_anchor:
        v = block_sparse_vector(opt_blocks, k_per_block, n_dim, l_blocks, b_per_block, g)
        anchors.append(v)
    I_bank = np.stack(anchors).astype(np.float32)

    # Calibrate tau_I against in-distribution state HRRs (block-restricted cosine)
    in_dist_cos: List[float] = []
    for _ in range(_n_train_per_option()):
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
            v = encode_state_blocksparse(s, state_blocks, pos_codewords_bs,
                                          block_role_bs, b_per_block, n_dim)
            # Block-restricted cosine of state vs anchor bank, restricted to OPTION's blocks
            # NOTE: state HRR lives in state_blocks (zeros in option blocks). The
            # anchor lives in opt_blocks (zeros in state_blocks). So restricted-cosine
            # over opt_blocks alone is (0 vs anchor_opt) - low. We instead restrict
            # cosine over the UNION (opt_blocks + state_blocks); this is the
            # block-aware planner's compromise (per drill section c). Use union.
            union_blocks = list(set(opt_blocks) | set(state_blocks))
            c_max = float(np.max(cosine_mat_block(v, I_bank, union_blocks, b_per_block)))
            in_dist_cos.append(c_max)
    if in_dist_cos:
        tau_I = float(np.percentile(in_dist_cos, 30))
    else:
        tau_I = -1.0
    return I_bank, tau_I


def fit_option_beta_target_bs(option_idx: int, g: np.random.Generator,
                                opt_blocks: List[int],
                                state_blocks: List[int],
                                pos_codewords_bs: np.ndarray,
                                block_role_bs: np.ndarray,
                                b_per_block: int, n_dim: int, l_blocks: int,
                                k_per_block: int) -> Tuple[np.ndarray, float]:
    """Build per-option beta_target as block-sparse signature in option blocks.
    Calibrate tau_beta against in-distribution completion states (block-restricted)."""
    primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[option_idx]]
    # Build beta_target as block-sparse signature -- one designated pattern per option
    beta_target = block_sparse_vector(opt_blocks, k_per_block, n_dim, l_blocks, b_per_block, g)

    in_dist_cos: List[float] = []
    ood_cos: List[float] = []
    n_train = _n_train_per_option()
    union_blocks = list(set(opt_blocks) | set(state_blocks))
    for _ in range(n_train):
        s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
        s2 = s
        for _ in range(OPTION_MAX_STEPS):
            a = primitives[int(g.integers(0, len(primitives)))]
            s2 = apply_action_sym(s2, a)
            if _option_completion(s2, option_idx):
                v = encode_state_blocksparse(s2, state_blocks, pos_codewords_bs,
                                              block_role_bs, b_per_block, n_dim)
                in_dist_cos.append(block_restricted_cosine(v, beta_target, union_blocks, b_per_block))
                break
        s_ood = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
        if not _option_completion(s_ood, option_idx):
            v = encode_state_blocksparse(s_ood, state_blocks, pos_codewords_bs,
                                          block_role_bs, b_per_block, n_dim)
            ood_cos.append(block_restricted_cosine(v, beta_target, union_blocks, b_per_block))

    if in_dist_cos:
        tau_beta = float(np.percentile(in_dist_cos, 20))
    else:
        tau_beta = 0.9
    if ood_cos:
        ood_at_tau = float(np.mean(np.array(ood_cos) >= tau_beta))
        if ood_at_tau > 0.20:
            tau_beta = max(tau_beta, float(np.percentile(ood_cos, 90)))
    return beta_target, tau_beta


# ---------------- Option-rollout (block-sparse pi) ----------------

def execute_option_bs(state: Tuple[int, ...], option_idx: int,
                       opt_blocks: List[int],
                       state_blocks: List[int],
                       pos_codewords_bs: np.ndarray,
                       block_role_bs: np.ndarray,
                       b_per_block: int, n_dim: int, l_blocks: int,
                       beta_target: np.ndarray, tau_beta: float,
                       use_beta: bool,
                       g: np.random.Generator,
                       goal_hd: np.ndarray
                       ) -> Tuple[Tuple[int, ...], List[int], bool]:
    """Roll an option's pi from `state` using block-restricted goal-cos
    readout. Greedy primitive selection per drill spec."""
    primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[option_idx]]
    s = state
    seq: List[int] = []
    beta_fired = False
    union_blocks = list(set(opt_blocks) | set(state_blocks))
    for step in range(OPTION_MAX_STEPS):
        best_a = primitives[0]
        best_cos = -1e9
        for a in primitives:
            ns = apply_action_sym(s, a)
            ns_hd = encode_state_blocksparse(ns, state_blocks, pos_codewords_bs,
                                              block_role_bs, b_per_block, n_dim)
            # Block-restricted goal cosine (over the option's blocks union state_blocks)
            c = block_restricted_cosine(ns_hd, goal_hd, union_blocks, b_per_block) \
                + 0.03 * float(g.standard_normal())
            if c > best_cos:
                best_cos = c
                best_a = a
        seq.append(best_a)
        s = apply_action_sym(s, best_a)
        if use_beta:
            s_hd = encode_state_blocksparse(s, state_blocks, pos_codewords_bs,
                                             block_role_bs, b_per_block, n_dim)
            c_beta = block_restricted_cosine(s_hd, beta_target, union_blocks, b_per_block)
            if c_beta >= tau_beta:
                beta_fired = True
                break
    return s, seq, beta_fired


def execute_option_dense(state: Tuple[int, ...], option_idx: int,
                          block_role: np.ndarray, pos_filler: np.ndarray, n_dim: int,
                          beta_target: np.ndarray, tau_beta: float,
                          use_beta: bool,
                          g: np.random.Generator,
                          goal_hd: np.ndarray
                          ) -> Tuple[Tuple[int, ...], List[int], bool]:
    """Dense HRR version (matches v3 mechanism for ARM_DENSE_BASELINE)."""
    primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[option_idx]]
    s = state
    seq: List[int] = []
    beta_fired = False
    for step in range(OPTION_MAX_STEPS):
        best_a = primitives[0]
        best_cos = -1e9
        for a in primitives:
            ns = apply_action_sym(s, a)
            ns_hd = encode_state_dense(ns, block_role, pos_filler, n_dim)
            c = cosine_vec(ns_hd, goal_hd) + 0.03 * float(g.standard_normal())
            if c > best_cos:
                best_cos = c
                best_a = a
        seq.append(best_a)
        s = apply_action_sym(s, best_a)
        if use_beta:
            s_hd = encode_state_dense(s, block_role, pos_filler, n_dim)
            if cosine_vec(s_hd, beta_target) >= tau_beta:
                beta_fired = True
                break
    return s, seq, beta_fired


# ---------------- Planners (the 6 arms) ----------------

def plan_random(start: Tuple[int, ...], goal: Tuple[int, ...],
                 g: np.random.Generator) -> Tuple[List[int], bool]:
    s = start
    seq: List[int] = []
    for _ in range(MAX_TOTAL_STEPS):
        if s == goal:
            return seq, True
        a = int(g.integers(0, N_ACTIONS))
        seq.append(a)
        s = apply_action_sym(s, a)
    return seq, (s == goal)


def plan_block_sparse_options(start: Tuple[int, ...], goal: Tuple[int, ...],
                                per_option_blocks: List[List[int]],
                                state_blocks: List[int],
                                pos_codewords_bs: np.ndarray,
                                block_role_bs: np.ndarray,
                                b_per_block: int, n_dim: int, l_blocks: int,
                                I_banks: List[np.ndarray], tau_Is: List[float],
                                beta_targets: List[np.ndarray], tau_betas: List[float],
                                use_I: bool, use_beta: bool,
                                g: np.random.Generator
                                ) -> Tuple[List[int], bool]:
    """Block-sparse options planner.

    At each planning step:
      1. Encode current state in block-sparse representation.
      2. (use_I): per-option block-restricted max-cos vs I bank >= tau_I -> eligible.
      3. Score eligible options by block-restricted cos(beta_target_o, goal_hd) over
         the OPTION's blocks only (cross-talk-free per-option scoring).
      4. Execute chosen option's pi via execute_option_bs.
    """
    goal_hd = encode_state_blocksparse(goal, state_blocks, pos_codewords_bs,
                                         block_role_bs, b_per_block, n_dim)
    s = start
    prim_seq: List[int] = []

    while len(prim_seq) < MAX_TOTAL_STEPS:
        if s == goal:
            return prim_seq, True
        s_hd = encode_state_blocksparse(s, state_blocks, pos_codewords_bs,
                                          block_role_bs, b_per_block, n_dim)
        eligible: List[int] = []
        if use_I:
            for o in range(N_OPTIONS):
                union_blocks = list(set(per_option_blocks[o]) | set(state_blocks))
                c_max = float(np.max(cosine_mat_block(s_hd, I_banks[o], union_blocks, b_per_block)))
                if c_max >= tau_Is[o]:
                    eligible.append(o)
        else:
            eligible = list(range(N_OPTIONS))

        if not eligible:
            a = int(g.integers(0, N_ACTIONS))
            prim_seq.append(a)
            s = apply_action_sym(s, a)
            continue

        # Score by block-restricted goal-cos -- block-locality means each option's
        # score is computed in its own block subspace; cross-talk structurally zero.
        best_o = eligible[0]
        best_score = -1e9
        for o in eligible:
            # Score on the option's own blocks (NOT union -- we want pure per-option signal)
            sc = block_restricted_cosine(beta_targets[o], goal_hd,
                                          per_option_blocks[o], b_per_block) \
                 + 0.03 * float(g.standard_normal())
            if sc > best_score:
                best_score = sc
                best_o = o

        s_after, opt_seq, _bf = execute_option_bs(
            s, best_o, per_option_blocks[best_o], state_blocks,
            pos_codewords_bs, block_role_bs, b_per_block, n_dim, l_blocks,
            beta_targets[best_o], tau_betas[best_o],
            use_beta, g, goal_hd,
        )
        for a in opt_seq:
            if len(prim_seq) >= MAX_TOTAL_STEPS:
                break
            prim_seq.append(a)
        s = s_after

    return prim_seq, (s == goal)


def plan_dense_baseline(start: Tuple[int, ...], goal: Tuple[int, ...],
                         block_role: np.ndarray, pos_filler: np.ndarray, n_dim: int,
                         I_banks: List[np.ndarray], tau_Is: List[float],
                         beta_targets: List[np.ndarray], tau_betas: List[float],
                         g: np.random.Generator
                         ) -> Tuple[List[int], bool]:
    """Dense HRR options planner -- replicates v3 mechanism. Should HARD_FAIL.

    Uses dense cosine (no block restriction). All options live in same dense
    HRR space -> macro-collapse pathology."""
    goal_hd = encode_state_dense(goal, block_role, pos_filler, n_dim)
    s = start
    prim_seq: List[int] = []
    while len(prim_seq) < MAX_TOTAL_STEPS:
        if s == goal:
            return prim_seq, True
        s_hd = encode_state_dense(s, block_role, pos_filler, n_dim)
        eligible: List[int] = []
        for o in range(N_OPTIONS):
            c_max = float(np.max(cosine_mat(s_hd, I_banks[o])))
            if c_max >= tau_Is[o]:
                eligible.append(o)
        if not eligible:
            a = int(g.integers(0, N_ACTIONS))
            prim_seq.append(a)
            s = apply_action_sym(s, a)
            continue
        best_o = eligible[0]
        best_score = -1e9
        for o in eligible:
            sc = cosine_vec(beta_targets[o], goal_hd) + 0.03 * float(g.standard_normal())
            if sc > best_score:
                best_score = sc
                best_o = o
        s_after, opt_seq, _ = execute_option_dense(
            s, best_o, block_role, pos_filler, n_dim,
            beta_targets[best_o], tau_betas[best_o],
            True, g, goal_hd,
        )
        for a in opt_seq:
            if len(prim_seq) >= MAX_TOTAL_STEPS:
                break
            prim_seq.append(a)
        s = s_after
    return prim_seq, (s == goal)


def plan_block_sparse_policy_only(start: Tuple[int, ...], goal: Tuple[int, ...],
                                    per_option_blocks: List[List[int]],
                                    state_blocks: List[int],
                                    pos_codewords_bs: np.ndarray,
                                    block_role_bs: np.ndarray,
                                    b_per_block: int, n_dim: int, l_blocks: int,
                                    beta_targets: List[np.ndarray],
                                    g: np.random.Generator
                                    ) -> Tuple[List[int], bool]:
    """Block-sparse pi alone (no I gate; no beta term; max-steps only)."""
    goal_hd = encode_state_blocksparse(goal, state_blocks, pos_codewords_bs,
                                         block_role_bs, b_per_block, n_dim)
    s = start
    prim_seq: List[int] = []
    while len(prim_seq) < MAX_TOTAL_STEPS:
        if s == goal:
            return prim_seq, True
        best_o, best_sc = 0, -1e9
        for o in range(N_OPTIONS):
            sc = block_restricted_cosine(beta_targets[o], goal_hd,
                                          per_option_blocks[o], b_per_block) \
                 + 0.03 * float(g.standard_normal())
            if sc > best_sc:
                best_sc = sc
                best_o = o
        s_after, opt_seq, _ = execute_option_bs(
            s, best_o, per_option_blocks[best_o], state_blocks,
            pos_codewords_bs, block_role_bs, b_per_block, n_dim, l_blocks,
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

    # ---- Block-sparse codebooks (for block-sparse arms) ----
    # block_role_bs[i] is a dense bipolar pattern over ALL N dims -- the per-block
    # mask is applied when we restrict to specific blocks (the bipolar values
    # multiply with the pos pattern in encode_state_blocksparse).
    block_role_bs = (g.integers(0, 2, size=(N_BLOCKS, N_DIM)) * 2 - 1).astype(np.float32)
    pos_codewords_bs = (g.integers(0, 2, size=(N_POS, N_DIM)) * 2 - 1).astype(np.float32)

    # ---- Per-option block assignments (disjoint slice of L blocks) ----
    per_option_blocks, state_blocks = assign_option_blocks(
        g, L_BLOCKS, N_OPTIONS, BLOCKS_PER_OPTION)

    # ---- Per-option block-sparse I + beta banks ----
    I_banks_bs: List[np.ndarray] = []
    tau_Is_bs: List[float] = []
    for o in range(N_OPTIONS):
        ib, ti = fit_option_I_bank_bs(
            o, g, per_option_blocks[o], state_blocks,
            pos_codewords_bs, block_role_bs, B_PER_BLOCK, N_DIM, L_BLOCKS,
            K_ANCHOR_PER_OPTION, K_PER_BLOCK)
        I_banks_bs.append(ib)
        tau_Is_bs.append(ti)

    beta_targets_bs: List[np.ndarray] = []
    tau_betas_bs: List[float] = []
    for o in range(N_OPTIONS):
        bt, tb = fit_option_beta_target_bs(
            o, g, per_option_blocks[o], state_blocks,
            pos_codewords_bs, block_role_bs, B_PER_BLOCK, N_DIM, L_BLOCKS,
            K_PER_BLOCK)
        beta_targets_bs.append(bt)
        tau_betas_bs.append(tb)

    # ---- NO_BLOCK_ASSIGNMENT control: all options share ALL blocks (no partition) ----
    all_blocks = list(range(L_BLOCKS))
    per_option_blocks_all = [list(all_blocks) for _ in range(N_OPTIONS)]
    state_blocks_all = list(all_blocks)
    I_banks_nba: List[np.ndarray] = []
    tau_Is_nba: List[float] = []
    beta_targets_nba: List[np.ndarray] = []
    tau_betas_nba: List[float] = []
    for o in range(N_OPTIONS):
        ib, ti = fit_option_I_bank_bs(
            o, g, all_blocks, state_blocks_all,
            pos_codewords_bs, block_role_bs, B_PER_BLOCK, N_DIM, L_BLOCKS,
            K_ANCHOR_PER_OPTION, K_PER_BLOCK)
        I_banks_nba.append(ib)
        tau_Is_nba.append(ti)
        bt, tb = fit_option_beta_target_bs(
            o, g, all_blocks, state_blocks_all,
            pos_codewords_bs, block_role_bs, B_PER_BLOCK, N_DIM, L_BLOCKS,
            K_PER_BLOCK)
        beta_targets_nba.append(bt)
        tau_betas_nba.append(tb)

    # ---- DENSE_BASELINE codebooks + banks (v3 mechanism) ----
    block_role_dense = bipolar_dense(N_BLOCKS, N_DIM, g)
    pos_filler_dense = bipolar_dense(N_POS, N_DIM, g)
    I_banks_d: List[np.ndarray] = []
    tau_Is_d: List[float] = []
    beta_targets_d: List[np.ndarray] = []
    tau_betas_d: List[float] = []
    for o in range(N_OPTIONS):
        # Build I bank as dense HRR of in-distribution states
        primitives = OPTION_PRIMITIVE_SETS[OPTION_NAMES[o]]
        anchors: List[np.ndarray] = []
        attempts = 0
        while len(anchors) < K_ANCHOR_PER_OPTION and attempts < K_ANCHOR_PER_OPTION * 20:
            attempts += 1
            s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
            s2 = s
            progress = False
            for _ in range(OPTION_MAX_STEPS):
                a = primitives[int(g.integers(0, len(primitives)))]
                s2 = apply_action_sym(s2, a)
                if _option_completion(s2, o):
                    progress = True
                    break
            if progress:
                anchors.append(encode_state_dense(s, block_role_dense, pos_filler_dense, N_DIM))
        while len(anchors) < K_ANCHOR_PER_OPTION:
            s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
            anchors.append(encode_state_dense(s, block_role_dense, pos_filler_dense, N_DIM))
        I_banks_d.append(np.stack(anchors).astype(np.float32))
        # tau_I calibration (in-dist 30th percentile of max-cos)
        in_dist_cos: List[float] = []
        for _ in range(_n_train_per_option()):
            s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
            s2 = s
            progress = False
            for _ in range(OPTION_MAX_STEPS):
                a = primitives[int(g.integers(0, len(primitives)))]
                s2 = apply_action_sym(s2, a)
                if _option_completion(s2, o):
                    progress = True
                    break
            if progress:
                v = encode_state_dense(s, block_role_dense, pos_filler_dense, N_DIM)
                in_dist_cos.append(float(np.max(cosine_mat(v, I_banks_d[-1]))))
        tau_Is_d.append(float(np.percentile(in_dist_cos, 30)) if in_dist_cos else -1.0)

        # beta_target: mean of completion-state HRRs
        completion_hd: List[np.ndarray] = []
        for _ in range(_n_train_per_option()):
            s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
            s2 = s
            for _ in range(OPTION_MAX_STEPS):
                a = primitives[int(g.integers(0, len(primitives)))]
                s2 = apply_action_sym(s2, a)
                if _option_completion(s2, o):
                    completion_hd.append(encode_state_dense(s2, block_role_dense, pos_filler_dense, N_DIM))
                    break
        if completion_hd:
            bt = np.mean(np.stack(completion_hd), axis=0)
            nb = np.linalg.norm(bt)
            if nb > 1e-8:
                bt = bt / nb
        else:
            bt = bipolar_dense(1, N_DIM, g)[0]
        beta_targets_d.append(bt)
        # tau_beta: 20th percentile of in-dist cos vs bt
        id_cos: List[float] = []
        for _ in range(_n_train_per_option()):
            s = tuple(int(g.integers(0, N_POS)) for _ in range(N_BLOCKS))
            s2 = s
            for _ in range(OPTION_MAX_STEPS):
                a = primitives[int(g.integers(0, len(primitives)))]
                s2 = apply_action_sym(s2, a)
                if _option_completion(s2, o):
                    id_cos.append(cosine_vec(
                        encode_state_dense(s2, block_role_dense, pos_filler_dense, N_DIM), bt))
                    break
        tau_betas_d.append(float(np.percentile(id_cos, 20)) if id_cos else 0.9)

    # ---- Sample goals (once; fair across arms) ----
    goals: List[Tuple[Tuple[int, ...], Tuple[int, ...], int, List[int]]] = []
    for _ in range(N_GOALS):
        goals.append(sample_composite_goal(g, MAX_BFS_DEPTH, MIN_OPTIMAL))

    # ---- RANDOM_BLOCKS: per-query random re-assignment of blocks ----
    def random_blocks_runner(s, gl, opt, plan, ag):
        # Re-permute blocks per-query (destroys per-option locality)
        per_opt_rand, state_blocks_rand = assign_option_blocks(
            ag, L_BLOCKS, N_OPTIONS, BLOCKS_PER_OPTION)
        # Rebuild banks on-the-fly using the random assignment
        I_b_r: List[np.ndarray] = []
        tau_I_r: List[float] = []
        bt_r: List[np.ndarray] = []
        tau_b_r: List[float] = []
        for o in range(N_OPTIONS):
            ib, ti = fit_option_I_bank_bs(
                o, ag, per_opt_rand[o], state_blocks_rand,
                pos_codewords_bs, block_role_bs, B_PER_BLOCK, N_DIM, L_BLOCKS,
                K_ANCHOR_PER_OPTION, K_PER_BLOCK)
            I_b_r.append(ib)
            tau_I_r.append(ti)
            b, tb = fit_option_beta_target_bs(
                o, ag, per_opt_rand[o], state_blocks_rand,
                pos_codewords_bs, block_role_bs, B_PER_BLOCK, N_DIM, L_BLOCKS,
                K_PER_BLOCK)
            bt_r.append(b)
            tau_b_r.append(tb)
        return plan_block_sparse_options(
            s, gl, per_opt_rand, state_blocks_rand,
            pos_codewords_bs, block_role_bs, B_PER_BLOCK, N_DIM, L_BLOCKS,
            I_b_r, tau_I_r, bt_r, tau_b_r,
            use_I=True, use_beta=True, g=ag)

    arm_runners: List[Tuple[str, Callable]] = [
        ("block_sparse_options_full",
            lambda s, gl, opt, plan, ag: plan_block_sparse_options(
                s, gl, per_option_blocks, state_blocks,
                pos_codewords_bs, block_role_bs, B_PER_BLOCK, N_DIM, L_BLOCKS,
                I_banks_bs, tau_Is_bs, beta_targets_bs, tau_betas_bs,
                use_I=True, use_beta=True, g=ag)),
        ("no_block_assignment",
            lambda s, gl, opt, plan, ag: plan_block_sparse_options(
                s, gl, per_option_blocks_all, state_blocks_all,
                pos_codewords_bs, block_role_bs, B_PER_BLOCK, N_DIM, L_BLOCKS,
                I_banks_nba, tau_Is_nba, beta_targets_nba, tau_betas_nba,
                use_I=True, use_beta=True, g=ag)),
        ("dense_baseline",
            lambda s, gl, opt, plan, ag: plan_dense_baseline(
                s, gl, block_role_dense, pos_filler_dense, N_DIM,
                I_banks_d, tau_Is_d, beta_targets_d, tau_betas_d, ag)),
        ("policy_only",
            lambda s, gl, opt, plan, ag: plan_block_sparse_policy_only(
                s, gl, per_option_blocks, state_blocks,
                pos_codewords_bs, block_role_bs, B_PER_BLOCK, N_DIM, L_BLOCKS,
                beta_targets_bs, ag)),
        ("random_blocks", random_blocks_runner),
        ("random",
            lambda s, gl, opt, plan, ag: plan_random(s, gl, ag)),
    ]

    per_arm: Dict[str, Dict[str, Any]] = {}
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
            "median_plan_len": float(np.median(plan_lens)) if plan_lens else float(COMPOSITE_DEPTH),
            "median_plan_ratio_vs_optimal": float(np.median(ratios)) if ratios else float("inf"),
            "_seq_hash": _seq_hash(seqs_for_hash),
        }

    # META_RULE_AF arms_distinct critical-pairs check
    hashes = {arm: per_arm[arm]["_seq_hash"] for arm in per_arm}
    critical_pairs = [
        ("block_sparse_options_full", "no_block_assignment"),
        ("block_sparse_options_full", "dense_baseline"),
        ("block_sparse_options_full", "policy_only"),
        ("block_sparse_options_full", "random_blocks"),
        ("block_sparse_options_full", "random"),
        ("dense_baseline", "random"),
    ]
    arms_distinct = all(hashes[a] != hashes[b] for a, b in critical_pairs)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "L_blocks": L_BLOCKS,
        "B_per_block": B_PER_BLOCK,
        "blocks_per_option": BLOCKS_PER_OPTION,
        "k_per_block": K_PER_BLOCK,
        "per_option_blocks": per_option_blocks,
        "state_blocks": state_blocks,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": per_arm,
        "arms_distinct": bool(arms_distinct),
        "arm_hashes": hashes,
        "n_goals_seed": N_GOALS,
        "median_optimal_plan_len": float(np.median([opt for _, _, opt, _ in goals])) if goals else 0.0,
        "tau_Is_bs": [float(x) for x in tau_Is_bs],
        "tau_betas_bs": [float(x) for x in tau_betas_bs],
        "tau_Is_d": [float(x) for x in tau_Is_d],
        "tau_betas_d": [float(x) for x in tau_betas_d],
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

    opts = summary["block_sparse_options_full"]["solve_rate_mean"]
    nba = summary["no_block_assignment"]["solve_rate_mean"]
    db = summary["dense_baseline"]["solve_rate_mean"]
    pol = summary["policy_only"]["solve_rate_mean"]
    rb = summary["random_blocks"]["solve_rate_mean"]
    rand = summary["random"]["solve_rate_mean"]
    opts_cv = summary["block_sparse_options_full"].get("solve_rate_cv", float("inf"))

    lift_random_blocks = opts - rb
    lift_dense_baseline = opts - db
    lift_no_block = opts - nba
    lift_random = opts - rand

    arms_distinct_all = bool(arms_distinct_seeds and all(arms_distinct_seeds))

    if not arms_distinct_all:
        verdict = "HARD_FAIL"
        reason = "ARMS_NOT_DISTINCT (cell bug; per-arm hashes collide)"
    elif opts <= HF_OPTS_MAX:
        verdict = "HARD_FAIL"
        reason = ("BLOCK_SPARSE_NO_RESCUE (opts=%.3f <= %.2f; encoding-axis test "
                  "negative; closure clause activates if Drill A also HARD_FAILs)"
                  % (opts, HF_OPTS_MAX))
    elif abs(opts - rb) < HF_BLOCK_ASSIGNMENT_ILLUSORY_DELTA:
        verdict = "HARD_FAIL"
        reason = ("BLOCK_ASSIGNMENT_ILLUSORY (opts=%.3f within %.2f of "
                  "random_blocks=%.3f; disjoint assignment not the rescue)"
                  % (opts, HF_BLOCK_ASSIGNMENT_ILLUSORY_DELTA, rb))
    elif db >= HF_DENSE_BASELINE_BREACH:
        verdict = "HARD_FAIL"
        reason = ("DENSE_BASELINE_DID_NOT_REPLICATE (db=%.3f >= %.2f; "
                  "prior HARD_FAIL did NOT replicate; investigate regime)"
                  % (db, HF_DENSE_BASELINE_BREACH))
    elif rand > HF_RAND_MAX_SANITY:
        verdict = "HARD_FAIL"
        reason = "SANITY_BREACH_RANDOM (rand=%.3f > %.2f; domain trivial)" % (rand, HF_RAND_MAX_SANITY)
    elif (opts >= HP_OPTS_MIN and
            opts <= HP_OPTS_UNSAT_HI and
            lift_random_blocks >= HP_LIFT_RANDOM_BLOCKS_MIN and
            lift_dense_baseline >= HP_LIFT_DENSE_BASELINE_MIN and
            db <= HP_DENSE_BASELINE_MAX and
            rand <= HP_RANDOM_MAX and
            (opts_cv <= HP_CV_MAX or len(SEEDS) == 1)):
        verdict = "HARD_PASS"
        reason = "ALL_HP_BANDS_MET (encoding-axis rescue load-bearing)"
    elif (MB_OPTS_LO <= opts < MB_OPTS_HI and
            lift_random_blocks >= MB_LIFT_RANDOM_BLOCKS_MIN and
            lift_dense_baseline >= MB_LIFT_DENSE_BASELINE_MIN):
        verdict = "MIDDLE_BAND"
        reason = ("MB_band (opts=%.3f lift_rb=%.3f lift_db=%.3f)"
                  % (opts, lift_random_blocks, lift_dense_baseline))
    elif opts >= HP_OPTS_MIN:
        verdict = "MIDDLE_BAND"
        reason = ("opts_HP_band_but_secondary_fail (opts=%.3f lift_rb=%.3f "
                  "lift_db=%.3f db=%.3f rand=%.3f)"
                  % (opts, lift_random_blocks, lift_dense_baseline, db, rand))
    else:
        verdict = "MIDDLE_BAND"
        reason = "between_HF_and_MB"

    verdict_msg = (
        "%s | %s | BS_OPTS=%.3f NBA=%.3f DB=%.3f POL=%.3f RB=%.3f RAND=%.3f | "
        "OPTS-RB=%.3f OPTS-DB=%.3f OPTS-NBA=%.3f OPTS-RAND=%.3f cv=%.3f "
        "arms_distinct=%s chance_floor=%.4g sbc_cap=%.1f"
    ) % (verdict, reason, opts, nba, db, pol, rb, rand,
         lift_random_blocks, lift_dense_baseline, lift_no_block, lift_random,
         opts_cv, arms_distinct_all, CHANCE_RANDOM_FLOOR, SBC_CAPACITY_THEORETICAL)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "lift_options_minus_random_blocks": float(lift_random_blocks),
        "lift_options_minus_dense_baseline": float(lift_dense_baseline),
        "lift_options_minus_no_block_assignment": float(lift_no_block),
        "lift_options_minus_random": float(lift_random),
        "arms_distinct": arms_distinct_all,
        "n_seeds_complete": len(per_seed),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(per_seed) * len(EXPECTED_ARMS) * N_GOALS,
        "cardinality_ok": (len(per_seed) >= max(1, len(SEEDS) - 1)),
        "chance_random_floor": float(CHANCE_RANDOM_FLOOR),
        "chance_random_rerank_ub": float(CHANCE_RANDOM_RERANK_UB),
        "sbc_capacity_theoretical": float(SBC_CAPACITY_THEORETICAL),
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

    print("[%s] mode=%s N=%d L=%d B=%d blocks_per_opt=%d state_blocks=%d "
          "k_per_block=%d domain_blocks=%d pos=%d actions=%d options=%d "
          "K_anchor=%d goals=%d depth=%d max_total=%d seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, L_BLOCKS, B_PER_BLOCK, BLOCKS_PER_OPTION,
        N_STATE_BLOCKS, K_PER_BLOCK, N_BLOCKS, N_POS, N_ACTIONS, N_OPTIONS,
        K_ANCHOR_PER_OPTION, N_GOALS, COMPOSITE_DEPTH, MAX_TOTAL_STEPS,
        SEEDS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r, "missing per_arm"
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
            opts = r["per_arm"]["block_sparse_options_full"]["solve_rate"]
            nba = r["per_arm"]["no_block_assignment"]["solve_rate"]
            db = r["per_arm"]["dense_baseline"]["solve_rate"]
            pol = r["per_arm"]["policy_only"]["solve_rate"]
            rb = r["per_arm"]["random_blocks"]["solve_rate"]
            rand = r["per_arm"]["random"]["solve_rate"]
            assert r["arms_distinct"], "ARMS_NOT_DISTINCT at selftest"
            for nm, v in [("opts", opts), ("nba", nba), ("db", db), ("pol", pol),
                          ("rb", rb), ("rand", rand)]:
                assert 0 <= v <= 1.0, "%s out of range" % nm
                assert not (math.isnan(v) or math.isinf(v)), "%s NaN/Inf" % nm
            # Selftest is liveness check only -- N=1024, 4 goals at depth=4 with
            # MAX_TOTAL_STEPS=16 means random can plausibly solve some goals. The
            # smoke + full bands enforce the floor at deployed scale (depth=6,
            # MAX_TOTAL=24, more goals); selftest only checks no NaN / arms_distinct
            # / per-arm dict completeness.
            assert rand <= 1.0, "random arm impossibly above 1.0"
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: opts=%.3f nba=%.3f db=%.3f pol=%.3f rb=%.3f rand=%.3f" % (
                                       opts, nba, db, pol, rb, rand),
                                   extra={"_phase": "selftest_done",
                                          "selftest_arms": list(r["per_arm"].keys()),
                                          "opts_solve": opts, "nba_solve": nba,
                                          "db_solve": db, "pol_solve": pol,
                                          "rb_solve": rb, "rand_solve": rand,
                                          "arms_distinct": r["arms_distinct"]})
            print("[selftest] OK; opts=%.3f nba=%.3f db=%.3f pol=%.3f rb=%.3f rand=%.3f distinct=%s" % (
                opts, nba, db, pol, rb, rand, r["arms_distinct"]), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    # Per-seed loop
    run_config = {"N": N_DIM, "L": L_BLOCKS, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    if _HAS_CKPT:
        done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    else:
        done, remaining = [], list(SEEDS)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    per_seed_inline: Dict[str, Dict[str, Any]] = {}
    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        if _HAS_CKPT:
            write_partial_key(out_dir, seed, result)
        per_seed_inline[str(seed)] = result
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    if _HAS_CKPT:
        per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    else:
        per_seed = per_seed_inline
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_substrate_hierarchical_block_sparse"
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
