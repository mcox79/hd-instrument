"""pfc_controller_per_step_operator_select_v1 -- B1 heterogeneous multi-hop routing.

Tests: minimum viable PFC controller (4-operator bank + cosine-argmax gate +
per-step operator selection). Tests substrate is ROUTING-bound not BINDING-bound.

ARMS (4):
  ARM_SINGLE_OPERATOR_BASELINE   fixed best-of-4-averaged operator at every hop
  ARM_RANDOM_ROUTER              random per-hop operator selection
  ARM_PFC_CONTROLLER_COSINE_ARGMAX  controller picks op with highest cos to state
  ARM_DIAG_ORACLE_ROUTER         oracle picks correct op sequence (upper bound)

PRE-REG BANDS (HARD-LOCKED at module init, PROSPECTIVE):
  HARD_PASS:  PFC lift over SINGLE >= +0.15 at depth-3 heterogeneous,
              cv across 5 seeds < 0.10,
              AND PFC > RANDOM by >= +0.10
  MIDDLE_BAND: lift in [+0.05, +0.15) OR cv in [0.10, 0.20) OR PFC >= RANDOM no margin
  HARD_FAIL:  lift < +0.05 OR PFC <= RANDOM OR cv >= 0.20 OR ORACLE bounds unachievable

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 5 seeds * 3 depths * 4 arms = 60 units
  EXPECTED_N_UNITS_SMOKE = 2 seeds * 2 depths * 4 arms = 16 units

HARDENING (META_RULE_X / J / L1-L4):
  main wrapped in if __name__ == "__main__"
  L1: minimal metrics.json with STARTED + PID at start
  L2: per-arm progress updates
  L3: outer try/except around main; failure-class to metrics
  L4: import-crash sentinel

Per-arm metrics structure (Fix #28):
  metrics["per_arm"] = {arm_name: {seed: {depth: score}}}
  metrics["summary"] = {arm_name: {depth: {mean, std, cv}}}

ASCII-only; no emojis; no em-dashes; self-contained (no hdlab/ imports).
Author: exp_dev 2026-06-27
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
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "pfc_controller_per_step_operator_select_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init
HP_LIFT_OVER_SINGLE = 0.15
HP_LIFT_OVER_RANDOM = 0.10
HP_CV_MAX = 0.10
MB_LIFT_LO = 0.05
MB_CV_HI = 0.20
HF_LIFT_LO = 0.05

EXPECTED_ARMS = ["single_operator_baseline", "random_router",
                 "pfc_controller_cosine_argmax", "diag_oracle_router"]

if SELF_TEST_MODE:
    # tiny smoke for self-test (must finish in < 180s)
    N_DIM = 512
    N_OPERATORS = 4
    SEEDS = [7]
    HOP_DEPTHS = [2]
    N_TRIPLES_PER_OP = 30
    N_TEST_CHAINS = 10
elif RUN_MODE == "smoke":
    N_DIM = 2048
    N_OPERATORS = 4
    SEEDS = [7, 17]
    HOP_DEPTHS = [2, 3]
    N_TRIPLES_PER_OP = 200
    N_TEST_CHAINS = 50
else:
    N_DIM = 8192
    N_OPERATORS = 4
    SEEDS = [7, 17, 23, 31, 41]
    HOP_DEPTHS = [2, 3, 5]
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
    HP_LIFT_OVER_SINGLE, HP_CV_MAX, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v1_pfc_controller",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
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
            "_hardening_marker": "v1_pfc_controller_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- primitives --------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar +/-1, L2-normalized. Shape (M, n)."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hebbian_write(triples: List[Tuple[int, int]], E: np.ndarray,
                  n_dim: int) -> np.ndarray:
    """Outer-product Hebbian: W[i] += s_i o_i^T. Returns (n_dim, n_dim)."""
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    if not triples:
        return W
    arr = np.asarray(triples, dtype=np.int64)
    s_idx, o_idx = arr[:, 0], arr[:, 1]
    # W += sum_i E[s_i].T outer E[o_i]
    S = E[s_idx]  # (T, n)
    O = E[o_idx]
    W = S.T @ O / float(n_dim)
    return W.astype(np.float32)


def cleanup_to_E(v: np.ndarray, E: np.ndarray) -> Tuple[int, np.ndarray]:
    """Cosine-argmax cleanup over codebook E. Returns (idx, E[idx])."""
    v = v.astype(np.float32, copy=False)
    vn = v / (np.linalg.norm(v) + 1e-8)
    sims = E @ vn  # (V,)
    idx = int(np.argmax(sims))
    return idx, E[idx]


def apply_operator(state: np.ndarray, W_op: np.ndarray,
                   E: np.ndarray) -> Tuple[int, np.ndarray]:
    """Apply W_op to state then cleanup to nearest codebook entry."""
    out_raw = state @ W_op
    idx, out_clean = cleanup_to_E(out_raw, E)
    return idx, out_clean


def pfc_select_operator(state: np.ndarray, W_ops: List[np.ndarray],
                        E: np.ndarray) -> int:
    """PFC controller: pick operator whose application output cosines best with
    state in pre-application sense. Heuristic: project state through each op
    and measure norm-stability against codebook (max sim to codebook entry =
    indicates clean op match)."""
    best_idx = 0
    best_score = -1.0
    state_n = state / (np.linalg.norm(state) + 1e-8)
    for i, W in enumerate(W_ops):
        out = state_n @ W
        out_n = out / (np.linalg.norm(out) + 1e-8)
        # max cos to codebook = "this op produces something on-manifold"
        sims = E @ out_n
        sc = float(np.max(sims))
        if sc > best_score:
            best_score = sc
            best_idx = i
    return best_idx


# -------------------------- arms --------------------------

def make_kb_and_chains(n_ops: int, V: int, n_train: int, n_test: int,
                        max_depth: int, g: np.random.Generator
                        ) -> Tuple[List[List[Tuple[int, int]]],
                                   List[Tuple[int, List[int], int]]]:
    """Build per-operator KB + heterogeneous test chains.

    Returns:
      per_op_triples: list of (s, o) lists, one per operator
      test_chains: list of (start_entity, op_sequence, final_entity)
    """
    # Each operator op_i has its own KB of (s, o) edges.
    per_op_triples: List[List[Tuple[int, int]]] = [[] for _ in range(n_ops)]

    # Build training edges: shuffle ops uniformly across (s, o) pairs
    for _ in range(n_train):
        s = int(g.integers(0, V))
        o = int(g.integers(0, V))
        op = int(g.integers(0, n_ops))
        per_op_triples[op].append((s, o))

    # Build heterogeneous test chains: each step picks an op uniformly,
    # then walks an existing edge of that op (if any), else extends KB.
    test_chains: List[Tuple[int, List[int], int]] = []
    attempts = 0
    while len(test_chains) < n_test and attempts < n_test * 100:
        attempts += 1
        s = int(g.integers(0, V))
        cur = s
        op_seq: List[int] = []
        ok = True
        for _ in range(max_depth):
            op = int(g.integers(0, n_ops))
            # Find any edge starting at cur in op's KB
            candidates = [o for (ss, o) in per_op_triples[op] if ss == cur]
            if not candidates:
                # Add an edge to make chain feasible
                new_o = int(g.integers(0, V))
                while new_o == cur:
                    new_o = int(g.integers(0, V))
                per_op_triples[op].append((cur, new_o))
                cur = new_o
            else:
                cur = candidates[0]
            op_seq.append(op)
        if ok:
            test_chains.append((s, op_seq, cur))

    return per_op_triples, test_chains


def run_arm_single_baseline(W_ops: List[np.ndarray], E: np.ndarray,
                             test_chains: List[Tuple[int, List[int], int]],
                             depth: int) -> float:
    """Always apply the average W_op (single fixed best-of-4) at every hop."""
    W_avg = np.mean(np.stack(W_ops, axis=0), axis=0).astype(np.float32)
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        for _ in range(depth):
            idx, state = apply_operator(state, W_avg, E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_random_router(W_ops: List[np.ndarray], E: np.ndarray,
                           test_chains: List[Tuple[int, List[int], int]],
                           depth: int, g: np.random.Generator) -> float:
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        for _ in range(depth):
            op = int(g.integers(0, len(W_ops)))
            idx, state = apply_operator(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_pfc_controller(W_ops: List[np.ndarray], E: np.ndarray,
                            test_chains: List[Tuple[int, List[int], int]],
                            depth: int) -> float:
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        for _ in range(depth):
            op = pfc_select_operator(state, W_ops, E)
            idx, state = apply_operator(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_oracle(W_ops: List[np.ndarray], E: np.ndarray,
                    test_chains: List[Tuple[int, List[int], int]],
                    depth: int) -> float:
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        for hop in range(depth):
            op = op_seq[hop]
            idx, state = apply_operator(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


# -------------------------- per-seed runner --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    """Run all 4 arms across all depths for one seed."""
    g = np.random.default_rng(seed)
    E = bipolar(V_ENTITIES, N_DIM, g)
    R = bipolar(N_OPERATORS, N_DIM, g)  # role-vectors not used in op-bank version
    max_d = max(HOP_DEPTHS)
    per_op, test_chains = make_kb_and_chains(
        N_OPERATORS, V_ENTITIES, N_TRIPLES_PER_OP, N_TEST_CHAINS, max_d, g
    )
    # Build W_op for each operator
    W_ops = [hebbian_write(per_op[i], E, N_DIM) for i in range(N_OPERATORS)]

    out: Dict[str, Dict[str, float]] = {
        arm: {} for arm in EXPECTED_ARMS
    }
    for depth in HOP_DEPTHS:
        out["single_operator_baseline"][str(depth)] = run_arm_single_baseline(
            W_ops, E, test_chains, depth)
        out["random_router"][str(depth)] = run_arm_random_router(
            W_ops, E, test_chains, depth, g)
        out["pfc_controller_cosine_argmax"][str(depth)] = run_arm_pfc_controller(
            W_ops, E, test_chains, depth)
        out["diag_oracle_router"][str(depth)] = run_arm_oracle(
            W_ops, E, test_chains, depth)
    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm_per_depth": out,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Compute per-arm per-depth mean/std/cv + PASS/FAIL verdict."""
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials found",
            "summary": "no per-seed partials found",
            "per_arm": {},
        }
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, Dict[str, float]]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}

    for arm in EXPECTED_ARMS:
        summary[arm] = {}
        per_arm_full[arm] = {}
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
                m = float(np.mean(vals))
                sd = float(np.std(vals))
                cv = sd / m if m > 1e-6 else 0.0
                summary[arm][d] = {"mean": m, "std": sd, "cv": cv, "n": len(vals)}
            else:
                summary[arm][d] = {"mean": 0.0, "std": 0.0, "cv": 0.0, "n": 0}

    # Discriminator: focus on depth-3 if available, else max depth
    decision_depth = 3 if 3 in HOP_DEPTHS else max(HOP_DEPTHS)
    dd = str(decision_depth)
    pfc_m = summary["pfc_controller_cosine_argmax"][dd]["mean"]
    pfc_cv = summary["pfc_controller_cosine_argmax"][dd]["cv"]
    single_m = summary["single_operator_baseline"][dd]["mean"]
    rand_m = summary["random_router"][dd]["mean"]
    oracle_m = summary["diag_oracle_router"][dd]["mean"]
    lift_over_single = pfc_m - single_m
    lift_over_random = pfc_m - rand_m

    # Verdict logic per pre-reg
    verdict = "MIDDLE_BAND"
    if (lift_over_single >= HP_LIFT_OVER_SINGLE and
            pfc_cv < HP_CV_MAX and
            lift_over_random >= HP_LIFT_OVER_RANDOM):
        verdict = "HARD_PASS"
    elif (lift_over_single < HF_LIFT_LO or pfc_m <= rand_m or
            pfc_cv >= MB_CV_HI):
        verdict = "HARD_FAIL"
    elif oracle_m < single_m + 0.05:
        # Oracle upper-bound says lift was structurally unachievable
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | depth=%d | PFC=%.3f Single=%.3f Random=%.3f Oracle=%.3f | "
        "lift_over_single=%.3f lift_over_random=%.3f pfc_cv=%.3f | n_seeds=%d"
    ) % (verdict, decision_depth, pfc_m, single_m, rand_m, oracle_m,
         lift_over_single, lift_over_random, pfc_cv, len(seeds_sorted))

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "decision_depth": decision_depth,
        "lift_over_single": lift_over_single,
        "lift_over_random": lift_over_random,
        "pfc_cv": pfc_cv,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(seeds_sorted) * len(HOP_DEPTHS) * len(EXPECTED_ARMS),
        "cardinality_ok": (len(seeds_sorted) * len(HOP_DEPTHS) * len(EXPECTED_ARMS)
                           >= EXPECTED_N_UNITS),
    }


# -------------------------- main --------------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    # L1: early minimal metrics with STARTED + PID
    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS, "expected_depths": HOP_DEPTHS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d V=%d seeds=%s depths=%s n_ops=%d expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_ENTITIES, SEEDS, HOP_DEPTHS,
        N_OPERATORS, EXPECTED_N_UNITS), flush=True)

    # Self-test mode: run one mini seed, validate output structure, exit
    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm_per_depth" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_per_depth"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm structure verified",
                                   extra={"_phase": "selftest_done"})
            print("[selftest] OK", flush=True)
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

    # L2: per-arm progress (here per-seed; each seed runs all arms)
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
    final["_hardening_marker"] = "v1_pfc_controller"
    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2), encoding="utf-8")
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
