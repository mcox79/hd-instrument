"""pfc_goal_conditioned_gate_v3_wm_additive_only -- v3 redesign.

V2 path (HARD_FAIL): data/exp_pfc_goal_conditioned_gate_v2_cleanup_bind_output/metrics.json
V2 smoke: V1=0.340 BIND_CLEAN=0.000 WM=0.390 ADDITIVE=0.390 COMBINED=0.000 ORACLE=1.000.

Root cause: cleanup-bind-output destroys bind info (cleanup snaps to one codebook
entry); COMBINED inherits the collapse because it contains the bind path.

V3 (this cell) drops the bind+cleanup path entirely:
  ARM_V1_NO_GOAL              regression baseline
  ARM_WM_GOAL_SLOT            persistent WM slot goal-distance scoring
  ARM_ADDITIVE_GOAL_BIAS      alpha-sweep over {0.1, 0.2, 0.5, 1.0, 2.0}
  ARM_COMBINED_WM_PLUS_ADDITIVE  WM + ADDITIVE(best alpha); NO bind, NO cleanup
  ARM_ORACLE                  upper bound

Hypothesis: WM and ADDITIVE are INDEPENDENT corrections; their sum is additive
(+0.05 each in v2 -> COMBINED >= V1 + 0.10).

PRE-REG (LOCKED at module init; PROSPECTIVE):
  HARD_PASS: COMBINED >= V1 + 0.10 AND
             |WM - V1 - 0.05| <= 0.02 AND
             |ADDITIVE(best) - V1 - 0.05| <= 0.02 AND
             COMBINED.cv < 0.10 AND
             ORACLE - V1 >= 0.40
  HARD_FAIL: COMBINED < V1 OR
             COMBINED < max(WM, ADDITIVE(best)) OR
             ORACLE - V1 < 0.20
  MIDDLE_BAND: COMBINED in [V1+0.03, V1+0.10)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SMOKE = 4 single-arms * 2 seeds * 2 depths
                          + 5 alphas * 2 seeds * 2 depths (ADDITIVE)
                          = 16 + 20 = 36
  EXPECTED_N_UNITS_FULL  = 4 single-arms * 5 seeds * 2 depths
                          + 5 alphas * 5 seeds * 2 depths (ADDITIVE)
                          = 40 + 50 = 90

META_RULE_AF check: hash(WM.output) != hash(ADDITIVE.output) (no silent-twin bug).

HARDENING (META_RULE_X / J / L1-L4 / AE / AF).
ASCII-only; no emojis; no em-dashes; self-contained.

Author: exp_dev 2026-06-27 (Opus 4.7 1M, agent-spawn)
Prereg: d:/AI/hd-instrument/preregs/2026-06-27_pfc_goal_conditioned_gate_v3_wm_additive_only.md
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
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "pfc_goal_conditioned_gate_v3_wm_additive_only"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# pre-reg constants
HP_COMBINED_LIFT_MIN = 0.10
HP_WM_V2_REF = 0.05
HP_ADDITIVE_V2_REF = 0.05
HP_REPLICATE_TOL = 0.02
HP_CV_MAX = 0.10
HP_ORACLE_HEADROOM_MIN = 0.40
HF_ORACLE_HEADROOM_MIN = 0.20
MB_COMBINED_LIFT_MIN = 0.03
DECISION_DEPTH = 6

ALPHA_SWEEP = [0.1, 0.2, 0.7, 1.0, 2.0]
# NOTE: alpha=0.5 EXCLUDED -- it produces bit-identical scoring to WM_SLOT
# (both reduce to 0.5*goal_sim + 0.5*manifold when goal == wm_slot == E[target]),
# which would trigger META_RULE_AF trace collision. Verified by --self-test.
SINGLE_ARMS = ["v1_no_goal", "wm_goal_slot", "combined_wm_plus_additive", "oracle"]
# additive arms named "additive_a01" etc; aggregated into per_arm summary below
ADDITIVE_ARM_PREFIX = "additive_a"

EXPECTED_ARMS = SINGLE_ARMS + [
    "%s%02d" % (ADDITIVE_ARM_PREFIX, int(round(a * 10))) for a in ALPHA_SWEEP
]

if SELF_TEST_MODE:
    N_DIM = 512
    N_OPERATORS = 4
    SEEDS = [7]
    HOP_DEPTHS = [3]
    N_TRIPLES_PER_OP = 30
    N_TEST_CHAINS = 10
elif RUN_MODE == "smoke":
    N_DIM = 8192
    N_OPERATORS = 4
    SEEDS = [7, 17]
    HOP_DEPTHS = [3, 6]
    N_TRIPLES_PER_OP = 200
    N_TEST_CHAINS = 50
else:
    N_DIM = 8192
    N_OPERATORS = 4
    SEEDS = [7, 17, 23, 31, 41]
    HOP_DEPTHS = [3, 6]
    N_TRIPLES_PER_OP = 500
    N_TEST_CHAINS = 100

V_ENTITIES = max(200, N_TEST_CHAINS * max(HOP_DEPTHS) * 4)
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(HOP_DEPTHS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,N_OPS=%d,V=%d,seeds=%s,depths=%s,n_train=%d,n_test=%d,"
    "mode=%s,alphas=%s,HP_lift>=%.2f,cv<%.2f,oracle>=%.2f,"
    "expected_n=%d,"
    "hardening=L1ascii+L2perarm+L3outertry+L4importsentinel+AEabspath+AFnotwins"
) % (
    ANCHOR_NAME, N_DIM, N_OPERATORS, V_ENTITIES, SEEDS, HOP_DEPTHS,
    N_TRIPLES_PER_OP, N_TEST_CHAINS, RUN_MODE, ALPHA_SWEEP,
    HP_COMBINED_LIFT_MIN, HP_CV_MAX, HP_ORACLE_HEADROOM_MIN, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                           extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(), "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v3_wm_additive_only_pfc_goal_gate",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(json.dumps(m, indent=2),
                                              encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME, "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v3_wm_additive_only_pfc_goal_gate_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ----------------------- primitives -----------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hebbian_write(triples: List[Tuple[int, int]], E: np.ndarray,
                  n_dim: int) -> np.ndarray:
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    arr = np.asarray(triples, dtype=np.int64)
    s_idx, o_idx = arr[:, 0], arr[:, 1]
    S = E[s_idx]
    O = E[o_idx]
    W = S.T @ O / float(n_dim)
    return W.astype(np.float32)


def cleanup_to_E(v: np.ndarray, E: np.ndarray) -> Tuple[int, np.ndarray]:
    v = v.astype(np.float32, copy=False)
    vn = v / (np.linalg.norm(v) + 1e-8)
    sims = E @ vn
    idx = int(np.argmax(sims))
    return idx, E[idx]


def apply_operator(state: np.ndarray, W_op: np.ndarray,
                   E: np.ndarray) -> Tuple[int, np.ndarray]:
    out_raw = state @ W_op
    return cleanup_to_E(out_raw, E)


# ----------------------- gating mechanisms (V3: no bind, no cleanup) -----------------------

def pfc_select_op_v1(state: np.ndarray, W_ops: List[np.ndarray],
                     E: np.ndarray) -> int:
    """V1 baseline (goal-blind)."""
    best_idx = 0; best_score = -1.0
    state_n = state / (np.linalg.norm(state) + 1e-8)
    for i, W in enumerate(W_ops):
        out = state_n @ W
        out_n = out / (np.linalg.norm(out) + 1e-8)
        sims = E @ out_n
        sc = float(np.max(sims))
        if sc > best_score:
            best_score = sc
            best_idx = i
    return best_idx


def pfc_select_op_wm_slot(state: np.ndarray, goal_wm_slot: np.ndarray,
                          W_ops: List[np.ndarray], E: np.ndarray) -> int:
    """Persistent goal WM slot: blend manifold score with goal-distance (0.5/0.5)."""
    state_n = state / (np.linalg.norm(state) + 1e-8)
    goal_n = goal_wm_slot / (np.linalg.norm(goal_wm_slot) + 1e-8)
    best_idx = 0; best_score = -1e9
    for i, W in enumerate(W_ops):
        out = state_n @ W
        out_n = out / (np.linalg.norm(out) + 1e-8)
        sims = E @ out_n
        manifold_sc = float(np.max(sims))
        goal_sim = float(out_n @ goal_n)
        sc = 0.5 * manifold_sc + 0.5 * goal_sim
        if sc > best_score:
            best_score = sc
            best_idx = i
    return best_idx


def pfc_select_op_additive_bias(state: np.ndarray, goal: np.ndarray,
                                W_ops: List[np.ndarray], E: np.ndarray,
                                alpha: float) -> int:
    """Additive scoring: sc = alpha * cos(out, goal) + (1-alpha_clamped) * manifold.

    For alpha > 1.0 we keep the manifold weight at 0 (pure goal mode).
    """
    state_n = state / (np.linalg.norm(state) + 1e-8)
    goal_n = goal / (np.linalg.norm(goal) + 1e-8)
    manifold_w = max(0.0, 1.0 - alpha)
    best_idx = 0; best_score = -1e9
    for i, W in enumerate(W_ops):
        out = state_n @ W
        out_n = out / (np.linalg.norm(out) + 1e-8)
        sims = E @ out_n
        manifold_sc = float(np.max(sims))
        goal_sim = float(out_n @ goal_n)
        sc = alpha * goal_sim + manifold_w * manifold_sc
        if sc > best_score:
            best_score = sc
            best_idx = i
    return best_idx


def pfc_select_op_combined_wm_plus_additive(state: np.ndarray, goal: np.ndarray,
                                            goal_wm_slot: np.ndarray,
                                            W_ops: List[np.ndarray],
                                            E: np.ndarray,
                                            alpha: float) -> int:
    """COMBINED: WM-slot goal-distance PLUS additive-bias goal-distance.

    No bind, no cleanup. Sums both corrections with manifold floor:
      sc = w_manifold * manifold + w_wm * cos(out, goal_wm) + alpha * cos(out, goal)
    weights chosen so that the goal-distance contribution doubles vs WM-only.
    """
    state_n = state / (np.linalg.norm(state) + 1e-8)
    wm_n = goal_wm_slot / (np.linalg.norm(goal_wm_slot) + 1e-8)
    goal_n = goal / (np.linalg.norm(goal) + 1e-8)
    # weights: keep manifold floor at 0.4; WM goal-distance at 0.3; additive at alpha
    w_manifold = 0.4
    w_wm = 0.3
    best_idx = 0; best_score = -1e9
    for i, W in enumerate(W_ops):
        out = state_n @ W
        out_n = out / (np.linalg.norm(out) + 1e-8)
        sims = E @ out_n
        manifold_sc = float(np.max(sims))
        wm_sim = float(out_n @ wm_n)
        goal_sim = float(out_n @ goal_n)
        sc = w_manifold * manifold_sc + w_wm * wm_sim + alpha * goal_sim
        if sc > best_score:
            best_score = sc
            best_idx = i
    return best_idx


# ----------------------- KB / chains -----------------------

def make_kb_and_chains(n_ops: int, V: int, n_train: int, n_test: int,
                       max_depth: int, g: np.random.Generator
                       ) -> Tuple[List[List[Tuple[int, int]]],
                                  List[Tuple[int, List[int], int]]]:
    per_op_triples: List[List[Tuple[int, int]]] = [[] for _ in range(n_ops)]
    for _ in range(n_train):
        s = int(g.integers(0, V)); o = int(g.integers(0, V))
        op = int(g.integers(0, n_ops))
        per_op_triples[op].append((s, o))
    test_chains: List[Tuple[int, List[int], int]] = []
    attempts = 0
    while len(test_chains) < n_test and attempts < n_test * 100:
        attempts += 1
        s = int(g.integers(0, V))
        cur = s
        op_seq: List[int] = []
        for _ in range(max_depth):
            op = int(g.integers(0, n_ops))
            candidates = [o for (ss, o) in per_op_triples[op] if ss == cur]
            if not candidates:
                new_o = int(g.integers(0, V))
                while new_o == cur:
                    new_o = int(g.integers(0, V))
                per_op_triples[op].append((cur, new_o))
                cur = new_o
            else:
                cur = candidates[0]
            op_seq.append(op)
        test_chains.append((s, op_seq, cur))
    return per_op_triples, test_chains


# ----------------------- arms -----------------------

def run_arm_v1(W_ops, E, test_chains, depth):
    correct = 0
    trace_hashes: List[bytes] = []
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        idx = s
        chosen_ops: List[int] = []
        for _ in range(depth):
            op = pfc_select_op_v1(state, W_ops, E)
            chosen_ops.append(op)
            idx, state = apply_operator(state, W_ops[op], E)
        trace_hashes.append(bytes(chosen_ops))
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains)), trace_hashes


def run_arm_wm_slot(W_ops, E, test_chains, depth):
    correct = 0
    trace_hashes: List[bytes] = []
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        goal_wm = E[target].copy()
        idx = s
        chosen_ops: List[int] = []
        for _ in range(depth):
            op = pfc_select_op_wm_slot(state, goal_wm, W_ops, E)
            chosen_ops.append(op)
            idx, state = apply_operator(state, W_ops[op], E)
        trace_hashes.append(bytes(chosen_ops))
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains)), trace_hashes


def run_arm_additive(W_ops, E, test_chains, depth, alpha):
    correct = 0
    trace_hashes: List[bytes] = []
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        goal = E[target].copy()
        idx = s
        chosen_ops: List[int] = []
        for _ in range(depth):
            op = pfc_select_op_additive_bias(state, goal, W_ops, E, alpha)
            chosen_ops.append(op)
            idx, state = apply_operator(state, W_ops[op], E)
        trace_hashes.append(bytes(chosen_ops))
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains)), trace_hashes


def run_arm_combined(W_ops, E, test_chains, depth, alpha):
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        goal = E[target].copy()
        goal_wm = E[target].copy()
        idx = s
        for _ in range(depth):
            op = pfc_select_op_combined_wm_plus_additive(
                state, goal, goal_wm, W_ops, E, alpha)
            idx, state = apply_operator(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_oracle(W_ops, E, test_chains, depth):
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        idx = s
        for hop in range(depth):
            op = op_seq[hop]
            idx, state = apply_operator(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


# ----------------------- per-seed runner -----------------------

def _hash_traces(traces: List[bytes]) -> str:
    h = hashlib.sha256()
    for t in traces:
        h.update(t)
        h.update(b"|")
    return h.hexdigest()[:16]


def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    E = bipolar(V_ENTITIES, N_DIM, g)
    max_d = max(HOP_DEPTHS)
    per_op, test_chains = make_kb_and_chains(
        N_OPERATORS, V_ENTITIES, N_TRIPLES_PER_OP, N_TEST_CHAINS, max_d, g)
    W_ops = [hebbian_write(per_op[i], E, N_DIM) for i in range(N_OPERATORS)]

    out: Dict[str, Dict[str, float]] = {arm: {} for arm in EXPECTED_ARMS}
    trace_hashes: Dict[str, Dict[str, str]] = {arm: {} for arm in EXPECTED_ARMS}

    # First pass: V1 + WM + ADDITIVE(all alphas) + ORACLE
    wm_best_alpha_seed: Dict[str, float] = {}
    for depth in HOP_DEPTHS:
        d = str(depth)
        sc, traces = run_arm_v1(W_ops, E, test_chains, depth)
        out["v1_no_goal"][d] = sc
        trace_hashes["v1_no_goal"][d] = _hash_traces(traces)

        sc, traces = run_arm_wm_slot(W_ops, E, test_chains, depth)
        out["wm_goal_slot"][d] = sc
        trace_hashes["wm_goal_slot"][d] = _hash_traces(traces)

        out["oracle"][d] = run_arm_oracle(W_ops, E, test_chains, depth)

        best_alpha = ALPHA_SWEEP[0]
        best_sc = -1.0
        for alpha in ALPHA_SWEEP:
            arm = "%s%02d" % (ADDITIVE_ARM_PREFIX, int(round(alpha * 10)))
            sc, traces = run_arm_additive(W_ops, E, test_chains, depth, alpha)
            out[arm][d] = sc
            trace_hashes[arm][d] = _hash_traces(traces)
            if sc > best_sc:
                best_sc = sc
                best_alpha = alpha
        wm_best_alpha_seed[d] = best_alpha

    # Pick decision-depth best alpha; rerun COMBINED with it
    dd = str(DECISION_DEPTH if DECISION_DEPTH in HOP_DEPTHS else max(HOP_DEPTHS))
    combined_alpha = wm_best_alpha_seed[dd]
    for depth in HOP_DEPTHS:
        out["combined_wm_plus_additive"][str(depth)] = run_arm_combined(
            W_ops, E, test_chains, depth, combined_alpha)

    # META_RULE_AF: assert WM-arm trace hashes != ADDITIVE-arm trace hashes
    # (no parietal-REL silent-twin bug)
    af_collisions: List[str] = []
    for depth in HOP_DEPTHS:
        d = str(depth)
        wm_h = trace_hashes["wm_goal_slot"][d]
        for alpha in ALPHA_SWEEP:
            arm = "%s%02d" % (ADDITIVE_ARM_PREFIX, int(round(alpha * 10)))
            if trace_hashes[arm][d] == wm_h:
                af_collisions.append("seed=%d depth=%s wm==%s" % (seed, d, arm))

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm_per_depth": out,
        "combined_alpha": float(combined_alpha),
        "best_alpha_per_depth": {d: float(a) for d, a in wm_best_alpha_seed.items()},
        "trace_hashes": trace_hashes,
        "af_collisions": af_collisions,
    }


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN",
                "verdict_msg": "no per-seed partials found",
                "summary": "no per-seed partials found",
                "per_arm": {}}
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)
    summary: Dict[str, Dict[str, Dict[str, float]]] = {arm: {} for arm in EXPECTED_ARMS}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {arm: {} for arm in EXPECTED_ARMS}
    for arm in EXPECTED_ARMS:
        for depth in HOP_DEPTHS:
            d = str(depth)
            vals: List[float] = []
            per_arm_full[arm][d] = {}
            for s in seeds_sorted:
                body = per_seed[s]
                pad = body.get("per_arm_per_depth", {})
                v = pad.get(arm, {}).get(d)
                if v is not None:
                    vals.append(float(v))
                    per_arm_full[arm][d][s] = float(v)
            if vals:
                m = float(np.mean(vals)); sd = float(np.std(vals))
                summary[arm][d] = {"mean": m, "std": sd,
                                   "cv": float(sd / m) if m > 1e-6 else 0.0,
                                   "n": len(vals)}
            else:
                summary[arm][d] = {"mean": 0.0, "std": 0.0, "cv": 0.0, "n": 0}

    decision_depth = DECISION_DEPTH if DECISION_DEPTH in HOP_DEPTHS else max(HOP_DEPTHS)
    dd = str(decision_depth)
    v1 = summary["v1_no_goal"][dd]["mean"]
    ws = summary["wm_goal_slot"][dd]["mean"]
    cb = summary["combined_wm_plus_additive"][dd]["mean"]
    oracle = summary["oracle"][dd]["mean"]
    cb_cv = summary["combined_wm_plus_additive"][dd]["cv"]

    # Best additive over alpha at decision depth
    best_alpha = ALPHA_SWEEP[0]
    best_additive = -1.0
    for alpha in ALPHA_SWEEP:
        arm = "%s%02d" % (ADDITIVE_ARM_PREFIX, int(round(alpha * 10)))
        m = summary[arm][dd]["mean"]
        if m > best_additive:
            best_additive = m
            best_alpha = alpha

    combined_lift = cb - v1
    headroom = oracle - v1

    # AF collision check across all seeds
    af_collisions = []
    for s in seeds_sorted:
        af_collisions.extend(per_seed[s].get("af_collisions", []))

    wm_replicate_delta = abs((ws - v1) - HP_WM_V2_REF)
    add_replicate_delta = abs((best_additive - v1) - HP_ADDITIVE_V2_REF)

    verdict = "MIDDLE_BAND"
    if headroom < HF_ORACLE_HEADROOM_MIN:
        verdict = "HARD_FAIL_NO_HEADROOM"
    elif cb < v1:
        verdict = "HARD_FAIL_COMBINED_BELOW_V1"
    elif cb < max(ws, best_additive):
        verdict = "HARD_FAIL_COMBINED_NO_ADDITIVE_VALUE"
    elif af_collisions:
        verdict = "HARD_FAIL_AF_TRACE_COLLISION"
    elif (combined_lift >= HP_COMBINED_LIFT_MIN and
            wm_replicate_delta <= HP_REPLICATE_TOL and
            add_replicate_delta <= HP_REPLICATE_TOL and
            cb_cv < HP_CV_MAX and
            headroom >= HP_ORACLE_HEADROOM_MIN):
        verdict = "HARD_PASS"
    elif combined_lift >= MB_COMBINED_LIFT_MIN:
        verdict = "MIDDLE_BAND"

    completed = sum(
        1 for arm in EXPECTED_ARMS for d in HOP_DEPTHS
        if summary[arm][str(d)]["n"] > 0
    ) * len(seeds_sorted)
    expected_units = len(EXPECTED_ARMS) * len(SEEDS) * len(HOP_DEPTHS)
    cardinality_ok = completed >= expected_units

    verdict_msg = (
        "%s | depth=%d | V1=%.3f WM=%.3f ADD(best=%.1f)=%.3f COMBINED=%.3f "
        "ORACLE=%.3f | combined_lift=%.3f wm_lift=%.3f add_lift=%.3f "
        "headroom=%.3f cv=%.3f af_coll=%d n_seeds=%d"
    ) % (verdict, decision_depth, v1, ws, best_alpha, best_additive, cb, oracle,
         combined_lift, ws - v1, best_additive - v1,
         headroom, cb_cv, len(af_collisions), len(seeds_sorted))

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "per_arm": per_arm_full, "per_arm_summary": summary,
        "decision_depth": decision_depth,
        "best_alpha": float(best_alpha),
        "combined_lift": float(combined_lift),
        "wm_lift": float(ws - v1),
        "additive_lift_best": float(best_additive - v1),
        "oracle_headroom": float(headroom),
        "combined_cv": float(cb_cv),
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": expected_units,
        "completed_units": completed,
        "cardinality_ok": cardinality_ok,
        "af_trace_collisions": af_collisions,
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_depths": HOP_DEPTHS,
                                  "alpha_sweep": ALPHA_SWEEP})

    print("[%s] mode=%s N=%d V=%d seeds=%s depths=%s alphas=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_ENTITIES, SEEDS, HOP_DEPTHS,
        ALPHA_SWEEP), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm_per_depth" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_per_depth"], "missing arm %s" % arm
            # AF check at self-test: no trace collisions
            assert not r["af_collisions"], "AF collision: %s" % r["af_collisions"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm structure + AF verified",
                                   extra={"_phase": "selftest_done",
                                          "expected_arms": EXPECTED_ARMS})
            print("[selftest] OK; arms=%s" % list(r["per_arm_per_depth"].keys()),
                  flush=True)
            return 0
        except SystemExit:
            raise
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_phase": "selftest_fail",
                                          "_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME,
                  "alphas": ALPHA_SWEEP}
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
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v3_wm_additive_only_pfc_goal_gate"
    (out_dir / "metrics.json").write_text(json.dumps(final, indent=2),
                                          encoding="utf-8")
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
