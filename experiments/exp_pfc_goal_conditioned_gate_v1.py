"""pfc_goal_conditioned_gate_v1 -- substrate goal-directed planning gate.

Tests: PFC controller v1 HARD_FAIL'd because gate was goal-blind. Replacing
argmax cos(state, op_key) with argmax cos(bind(state, goal), op_key) AND
holding goal in a persistent WM slot for the whole plan closes >=50% of the
oracle gap by depth=6.

ARMS (5):
  ARM_PFC_COSINE_ARGMAX_V1     baseline v1 (regression; should reproduce HARD_FAIL)
  ARM_PFC_STATE_GOAL_BIND_GATE A1: per-step bind(state, goal) gate
  ARM_PFC_GOAL_WM_SLOT         B1: persistent WM goal slot; gate reads slot
  ARM_PFC_COMBINED             A1 + B1 fused
  ARM_DIAG_ORACLE              upper bound (oracle picks correct op sequence)

PRE-REG BANDS (LOCKED at module init, PROSPECTIVE):
  HARD_PASS:  COMBINED - V1 >= +0.20 AND
              COMBINED - max(BIND_GATE, WM_SLOT) >= +0.05 (anti-saturation) AND
              cv < 0.10 AND
              (COMBINED - V1) / (ORACLE - V1) >= 0.50 at depth=6
  MIDDLE_BAND: lift in [+0.08, +0.20)
  HARD_FAIL:  lift <= +0.03 OR ORACLE - V1 < 0.10 (no headroom)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 5 arms * 5 seeds * 2 depths = 50
  EXPECTED_N_UNITS_SMOKE = 5 arms * 2 seeds * 2 depths = 20
  Discriminator-survives-scale: smoke at N=8192 depths {3,6}.

HARDENING (META_RULE_X / J / L1-L4).
Per-arm metrics: metrics["per_arm"] = {arm: {seed: {depth: score}}}; Fix #28.

ASCII-only; no emojis; no em-dashes; self-contained.
Author: exp_dev 2026-06-27 (Opus 4.7 1M, agent-spawn)
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
import math
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

ANCHOR_NAME = "pfc_goal_conditioned_gate_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

HP_LIFT_OVER_V1 = 0.20
HP_LIFT_OVER_SINGLE_MECH = 0.05
HP_CV_MAX = 0.10
HP_ORACLE_GAP_CLOSED = 0.50
HF_LIFT_LO = 0.03
HF_ORACLE_HEADROOM_MIN = 0.10
DECISION_DEPTH = 6

EXPECTED_ARMS = [
    "pfc_cosine_argmax_v1",
    "pfc_state_goal_bind_gate",
    "pfc_goal_wm_slot",
    "pfc_combined",
    "diag_oracle",
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
    "mode=%s,HP_lift>=%.2f,HP_cv<=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, N_OPERATORS, V_ENTITIES, SEEDS, HOP_DEPTHS,
    N_TRIPLES_PER_OP, N_TEST_CHAINS, RUN_MODE,
    HP_LIFT_OVER_V1, HP_CV_MAX, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v1_pfc_goal_conditioned_gate",
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
            "_hardening_marker": "v1_pfc_goal_conditioned_gate_import_crash",
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


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    A = np.fft.fft(a); B = np.fft.fft(b)
    return np.real(np.fft.ifft(A * B)).astype(np.float32)


def hebbian_write(triples: List[Tuple[int, int]], E: np.ndarray,
                  n_dim: int) -> np.ndarray:
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    if not triples:
        return W
    arr = np.asarray(triples, dtype=np.int64)
    s_idx, o_idx = arr[:, 0], arr[:, 1]
    S = E[s_idx]; O = E[o_idx]
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


# ----------------------- gating mechanisms -----------------------

def pfc_select_op_v1(state: np.ndarray, W_ops: List[np.ndarray],
                      E: np.ndarray) -> int:
    """V1 (goal-blind): argmax over operators by max-cos-to-codebook of op(state)."""
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


def pfc_select_op_bind_gate(state: np.ndarray, goal: np.ndarray,
                             W_ops: List[np.ndarray], E: np.ndarray) -> int:
    """A1: argmax cos(op(bind(state, goal)), codebook). Goal modulates gate."""
    sg = hrr_bind(state, goal)
    sg_n = sg / (np.linalg.norm(sg) + 1e-8)
    best_idx = 0; best_score = -1.0
    for i, W in enumerate(W_ops):
        out = sg_n @ W
        out_n = out / (np.linalg.norm(out) + 1e-8)
        sims = E @ out_n
        sc = float(np.max(sims))
        if sc > best_score:
            best_score = sc
            best_idx = i
    return best_idx


def pfc_select_op_wm_slot(state: np.ndarray, goal_wm_slot: np.ndarray,
                           W_ops: List[np.ndarray], E: np.ndarray) -> int:
    """B1: per-step gate reads PERSISTENT goal from WM slot.
    Mechanism: score = cos(op(state), goal_wm) + cos(op(state), codebook).
    Goal-distance-to-leaf modulates selection."""
    state_n = state / (np.linalg.norm(state) + 1e-8)
    goal_n = goal_wm_slot / (np.linalg.norm(goal_wm_slot) + 1e-8)
    best_idx = 0; best_score = -1e9
    for i, W in enumerate(W_ops):
        out = state_n @ W
        out_n = out / (np.linalg.norm(out) + 1e-8)
        sims = E @ out_n
        manifold_sc = float(np.max(sims))
        goal_sim = float(out_n @ goal_n)  # how close this op brings us to goal
        sc = 0.5 * manifold_sc + 0.5 * goal_sim
        if sc > best_score:
            best_score = sc
            best_idx = i
    return best_idx


def pfc_select_op_combined(state: np.ndarray, goal: np.ndarray,
                            goal_wm_slot: np.ndarray,
                            W_ops: List[np.ndarray], E: np.ndarray) -> int:
    """A1 + B1: bind(state, goal) for gate AND read goal_wm for goal-distance scoring."""
    sg = hrr_bind(state, goal)
    sg_n = sg / (np.linalg.norm(sg) + 1e-8)
    goal_n = goal_wm_slot / (np.linalg.norm(goal_wm_slot) + 1e-8)
    best_idx = 0; best_score = -1e9
    for i, W in enumerate(W_ops):
        out = sg_n @ W
        out_n = out / (np.linalg.norm(out) + 1e-8)
        sims = E @ out_n
        manifold_sc = float(np.max(sims))
        goal_sim = float(out_n @ goal_n)
        sc = 0.5 * manifold_sc + 0.5 * goal_sim
        if sc > best_score:
            best_score = sc
            best_idx = i
    return best_idx


# ----------------------- KB / chain construction (matched to V1) -----------------------

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
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        for _ in range(depth):
            op = pfc_select_op_v1(state, W_ops, E)
            idx, state = apply_operator(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_bind_gate(W_ops, E, test_chains, depth):
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        goal = E[target].copy()  # goal = target entity vector
        for _ in range(depth):
            op = pfc_select_op_bind_gate(state, goal, W_ops, E)
            idx, state = apply_operator(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_wm_slot(W_ops, E, test_chains, depth):
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        goal_wm = E[target].copy()  # PERSISTENT goal slot for whole plan
        for _ in range(depth):
            op = pfc_select_op_wm_slot(state, goal_wm, W_ops, E)
            idx, state = apply_operator(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_combined(W_ops, E, test_chains, depth):
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        goal = E[target].copy()
        goal_wm = E[target].copy()  # persistent
        for _ in range(depth):
            op = pfc_select_op_combined(state, goal, goal_wm, W_ops, E)
            idx, state = apply_operator(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_oracle(W_ops, E, test_chains, depth):
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        for hop in range(depth):
            op = op_seq[hop]
            idx, state = apply_operator(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


# ----------------------- per-seed runner -----------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    E = bipolar(V_ENTITIES, N_DIM, g)
    max_d = max(HOP_DEPTHS)
    per_op, test_chains = make_kb_and_chains(
        N_OPERATORS, V_ENTITIES, N_TRIPLES_PER_OP, N_TEST_CHAINS, max_d, g)
    W_ops = [hebbian_write(per_op[i], E, N_DIM) for i in range(N_OPERATORS)]

    out: Dict[str, Dict[str, float]] = {arm: {} for arm in EXPECTED_ARMS}
    for depth in HOP_DEPTHS:
        out["pfc_cosine_argmax_v1"][str(depth)] = run_arm_v1(W_ops, E, test_chains, depth)
        out["pfc_state_goal_bind_gate"][str(depth)] = run_arm_bind_gate(W_ops, E, test_chains, depth)
        out["pfc_goal_wm_slot"][str(depth)] = run_arm_wm_slot(W_ops, E, test_chains, depth)
        out["pfc_combined"][str(depth)] = run_arm_combined(W_ops, E, test_chains, depth)
        out["diag_oracle"][str(depth)] = run_arm_oracle(W_ops, E, test_chains, depth)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm_per_depth": out,
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

    # Decision at DECISION_DEPTH (6) if available, else max depth
    decision_depth = DECISION_DEPTH if DECISION_DEPTH in HOP_DEPTHS else max(HOP_DEPTHS)
    dd = str(decision_depth)
    v1 = summary["pfc_cosine_argmax_v1"][dd]["mean"]
    bg = summary["pfc_state_goal_bind_gate"][dd]["mean"]
    ws = summary["pfc_goal_wm_slot"][dd]["mean"]
    cb = summary["pfc_combined"][dd]["mean"]
    oracle = summary["diag_oracle"][dd]["mean"]
    cb_cv = summary["pfc_combined"][dd]["cv"]

    lift_over_v1 = cb - v1
    lift_over_single = cb - max(bg, ws)
    headroom = oracle - v1
    closed = (lift_over_v1 / headroom) if headroom > 1e-6 else 0.0

    verdict = "MIDDLE_BAND"
    if headroom < HF_ORACLE_HEADROOM_MIN:
        verdict = "HARD_FAIL_NO_HEADROOM"
    elif (lift_over_v1 >= HP_LIFT_OVER_V1 and
            lift_over_single >= HP_LIFT_OVER_SINGLE_MECH and
            cb_cv < HP_CV_MAX and
            closed >= HP_ORACLE_GAP_CLOSED):
        verdict = "HARD_PASS"
    elif lift_over_v1 <= HF_LIFT_LO:
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | depth=%d | V1=%.3f BIND=%.3f WM=%.3f COMBINED=%.3f ORACLE=%.3f | "
        "lift_v1=%.3f lift_single=%.3f closed=%.3f cv=%.3f n_seeds=%d"
    ) % (verdict, decision_depth, v1, bg, ws, cb, oracle,
         lift_over_v1, lift_over_single, closed, cb_cv, len(seeds_sorted))

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "per_arm": per_arm_full, "per_arm_summary": summary,
        "decision_depth": decision_depth,
        "lift_over_v1": float(lift_over_v1),
        "lift_over_single": float(lift_over_single),
        "oracle_headroom": float(headroom), "oracle_gap_closed": float(closed),
        "combined_cv": float(cb_cv),
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(seeds_sorted) * len(HOP_DEPTHS) * len(EXPECTED_ARMS),
        "cardinality_ok": (len(seeds_sorted) * len(HOP_DEPTHS) * len(EXPECTED_ARMS)
                           >= EXPECTED_N_UNITS),
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS, "expected_depths": HOP_DEPTHS})

    print("[%s] mode=%s N=%d V=%d seeds=%s depths=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_ENTITIES, SEEDS, HOP_DEPTHS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm_per_depth" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_per_depth"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm structure verified",
                                   extra={"_phase": "selftest_done"})
            print("[selftest] OK; arms=%s" % list(r["per_arm_per_depth"].keys()), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_phase": "selftest_fail",
                                          "_traceback": traceback.format_exc()})
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
    final["_hardening_marker"] = "v1_pfc_goal_conditioned_gate"
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
