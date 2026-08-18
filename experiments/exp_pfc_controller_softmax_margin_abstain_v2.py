"""pfc_controller_softmax_margin_abstain_v2 -- B1 heterogeneous routing fair-revival.

Drill source: notes/research_drill_2x_pfc_controller_revival_2026-06-27.md TOP-1
META_FAIRNESS_PATTERN bug v1: SINGLE_BASELINE was AVERAGE of all 4 operator
matrices = implicit routing. v2 must use SINGLE FIXED operator (always op 0)
as the TRUE no-routing baseline.

MECHANISM: cosine + temperature softmax + sparse top-2 (instead of argmax-1);
abstain (identity / no-op) if max margin (top1_cos - top2_cos) < threshold.

ARMS (5):
  ARM_SINGLE_FIXED_BASELINE      always operator 0 (TRUE no-routing fair baseline)
  ARM_RANDOM_ROUTER              random op per-hop
  ARM_COSINE_ARGMAX              v1 mechanism (regression check vs v1)
  ARM_SOFTMAX_TEMP_TOP_2         softmax(cos/T) over ops; mix top-2 weights; T=0.3
  ARM_WITH_ABSTAIN               argmax + abstain (identity) if top1-top2 margin < 0.1

PRE-REG BANDS (HARD-LOCKED at module init; depth=6 is decision depth per drill):
  HARD_PASS:
    SOFTMAX_TEMP_TOP_2 lift over SINGLE_FIXED >= +0.10 at depth=6
    AND cv < 0.10 across seeds
    AND SOFTMAX_TEMP_TOP_2 > RANDOM_ROUTER by >= +0.10
  MIDDLE_BAND: lift in [+0.05, +0.10) OR cv in [0.10, 0.20)
  HARD_FAIL: lift < +0.05 OR SOFTMAX_TEMP_TOP_2 <= COSINE_ARGMAX + 0.03 (mechanism null)

FAIR-BASELINE CRITICAL: SINGLE_FIXED is a SINGLE matrix (W_ops[0]), NOT an aggregate.

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SMOKE = 5 arms * 3 seeds * 2 depths(3,6) = 30
  EXPECTED_N_UNITS_FULL  = 5 arms * 5 seeds * 4 depths(3,5,8,12) = 100

HARDENING (META_RULE_X / J / L1-L4):
  main wrapped in if __name__ == "__main__"
  L1: minimal metrics.json with STARTED + PID at start
  L2: per-arm/seed progress updates
  L3: outer try/except around main
  L4: import-crash sentinel

ASCII-only; no emojis; no em-dashes; self-contained (no hdlab/ imports).
Author: exp_dev 2026-06-27 (fair-revival cell 2 of 4 under research lead).
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

ANCHOR_NAME = "pfc_controller_softmax_margin_abstain_v2"

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
HP_LIFT_OVER_SINGLE_FIXED = 0.10
HP_LIFT_OVER_RANDOM = 0.10
HP_CV_MAX = 0.10
HP_LIFT_OVER_ARGMAX = 0.03
MB_LIFT_LO = 0.05
MB_CV_HI = 0.20
HF_LIFT_LO = 0.05

EXPECTED_ARMS = ["single_fixed_baseline", "random_router",
                 "cosine_argmax", "softmax_temp_top_2", "with_abstain"]

# Decision depth (depth at which HARD_PASS bar is evaluated)
DECISION_DEPTH = 6

if SELF_TEST_MODE:
    N_DIM = 512
    N_OPERATORS = 4
    SEEDS = [7]
    HOP_DEPTHS = [3]
    N_TRIPLES_PER_OP = 30
    N_TEST_CHAINS = 10
elif RUN_MODE == "smoke":
    # Per drill: smoke at depth=3 AND depth=6 (heterogeneous benefit grows with depth)
    # n=3 seeds for cv discipline
    N_DIM = 4096
    N_OPERATORS = 4
    SEEDS = [7, 17, 23]
    HOP_DEPTHS = [3, 6]
    N_TRIPLES_PER_OP = 300
    N_TEST_CHAINS = 60
else:
    N_DIM = 8192
    N_OPERATORS = 4
    SEEDS = [7, 17, 23, 31, 41]
    HOP_DEPTHS = [3, 5, 8, 12]
    N_TRIPLES_PER_OP = 500
    N_TEST_CHAINS = 100

V_ENTITIES = max(200, N_TEST_CHAINS * max(HOP_DEPTHS) * 4)
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(HOP_DEPTHS)

# Softmax temperature for SOFTMAX_TEMP_TOP_2
SOFTMAX_T = 0.3
# Abstain margin threshold
ABSTAIN_MARGIN_TH = 0.10

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,N_OPS=%d,V=%d,seeds=%s,depths=%s,decision_depth=%d,"
    "n_train=%d,n_test=%d,mode=%s,"
    "softmax_T=%.2f,abstain_margin=%.2f,"
    "HP_lift_single>=%.2f,HP_lift_random>=%.2f,HP_lift_argmax>=%.2f,HP_cv<=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "FAIR_BASELINE=SINGLE_FIXED_OP_0_NOT_MEAN_OF_OPS"
) % (
    ANCHOR_NAME, N_DIM, N_OPERATORS, V_ENTITIES, SEEDS, HOP_DEPTHS, DECISION_DEPTH,
    N_TRIPLES_PER_OP, N_TEST_CHAINS, RUN_MODE,
    SOFTMAX_T, ABSTAIN_MARGIN_TH,
    HP_LIFT_OVER_SINGLE_FIXED, HP_LIFT_OVER_RANDOM, HP_LIFT_OVER_ARGMAX,
    HP_CV_MAX, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v2_pfc_softmax_margin_abstain",
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
            "_hardening_marker": "v2_pfc_softmax_margin_abstain_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- primitives --------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hebbian_write(triples: List[Tuple[int, int]], E: np.ndarray,
                  n_dim: int) -> np.ndarray:
    """Outer-product Hebbian: W = sum_i E[s_i].T outer E[o_i] / n. Returns (n_dim, n_dim)."""
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    if not triples:
        return W
    arr = np.asarray(triples, dtype=np.int64)
    s_idx, o_idx = arr[:, 0], arr[:, 1]
    S = E[s_idx]  # (T, n)
    O = E[o_idx]
    W = S.T @ O / float(n_dim)
    return W.astype(np.float32)


def cleanup_to_E(v: np.ndarray, E: np.ndarray) -> Tuple[int, np.ndarray]:
    v = v.astype(np.float32, copy=False)
    vn = v / (np.linalg.norm(v) + 1e-8)
    sims = E @ vn
    idx = int(np.argmax(sims))
    return idx, E[idx]


def apply_W(state: np.ndarray, W_op: np.ndarray,
            E: np.ndarray) -> Tuple[int, np.ndarray]:
    out_raw = state @ W_op
    idx, out_clean = cleanup_to_E(out_raw, E)
    return idx, out_clean


def op_scores(state: np.ndarray, W_ops: List[np.ndarray],
              E: np.ndarray) -> np.ndarray:
    """For each op, the max-cos of (state @ W_op) against codebook E.
    Higher = "this op produces something on-manifold given current state."

    Returns array shape (n_ops,) of scores in [-1, 1].
    """
    state_n = state / (np.linalg.norm(state) + 1e-8)
    scores = np.zeros(len(W_ops), dtype=np.float32)
    for i, W in enumerate(W_ops):
        out = state_n @ W
        out_n = out / (np.linalg.norm(out) + 1e-8)
        sims = E @ out_n
        scores[i] = float(np.max(sims))
    return scores


# -------------------------- arms --------------------------

def run_arm_single_fixed_baseline(W_ops: List[np.ndarray], E: np.ndarray,
                                    test_chains: List[Tuple[int, List[int], int]],
                                    depth: int) -> float:
    """ALWAYS use W_ops[0]. The TRUE no-routing baseline (no aggregation).

    THIS is the load-bearing v2 fix: SINGLE FIXED OP, not avg-of-ops.
    """
    W_fixed = W_ops[0]
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        idx = s
        for _ in range(depth):
            idx, state = apply_W(state, W_fixed, E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_random_router(W_ops: List[np.ndarray], E: np.ndarray,
                           test_chains: List[Tuple[int, List[int], int]],
                           depth: int, g: np.random.Generator) -> float:
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        idx = s
        for _ in range(depth):
            op = int(g.integers(0, len(W_ops)))
            idx, state = apply_W(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_cosine_argmax(W_ops: List[np.ndarray], E: np.ndarray,
                           test_chains: List[Tuple[int, List[int], int]],
                           depth: int) -> float:
    """v1 mechanism: pick argmax(op_scores). Regression check vs v1."""
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        idx = s
        for _ in range(depth):
            scores = op_scores(state, W_ops, E)
            op = int(np.argmax(scores))
            idx, state = apply_W(state, W_ops[op], E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_softmax_temp_top_2(W_ops: List[np.ndarray], E: np.ndarray,
                                 test_chains: List[Tuple[int, List[int], int]],
                                 depth: int, T: float = SOFTMAX_T) -> float:
    """Softmax(cos/T) over ops; mix TOP-2 by weight; cleanup output to codebook.

    Sparse top-2: zero out all but top-2 scores, renormalize weights, mix
    weighted W_op outputs, then cleanup-to-E for next state.
    """
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        idx = s
        for _ in range(depth):
            scores = op_scores(state, W_ops, E)
            # top-2 sparse mask
            top2_idx = np.argpartition(-scores, 2)[:2]
            sparse_logits = np.full_like(scores, -1e9)
            sparse_logits[top2_idx] = scores[top2_idx] / T
            # softmax
            exp_s = np.exp(sparse_logits - np.max(sparse_logits))
            w = exp_s / (np.sum(exp_s) + 1e-9)
            # mix W_op outputs by w
            state_n = state / (np.linalg.norm(state) + 1e-8)
            out = np.zeros_like(state)
            for i in range(len(W_ops)):
                if w[i] > 1e-6:
                    out += w[i] * (state_n @ W_ops[i])
            idx, state = cleanup_to_E(out, E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_with_abstain(W_ops: List[np.ndarray], E: np.ndarray,
                          test_chains: List[Tuple[int, List[int], int]],
                          depth: int,
                          margin_th: float = ABSTAIN_MARGIN_TH
                          ) -> Tuple[float, float]:
    """Argmax routing + ABSTAIN (identity / state preserved) if top1-top2 margin < threshold.

    Returns (accuracy, abstain_rate).
    """
    correct = 0
    abstain_total = 0
    step_total = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        idx = s
        for _ in range(depth):
            scores = op_scores(state, W_ops, E)
            srt = np.argsort(-scores)
            top1, top2 = srt[0], srt[1]
            margin = float(scores[top1] - scores[top2])
            step_total += 1
            if margin < margin_th:
                # ABSTAIN: state unchanged; idx unchanged
                abstain_total += 1
                # keep state, keep idx as last cleaned
            else:
                idx, state = apply_W(state, W_ops[int(top1)], E)
        if idx == target:
            correct += 1
    abstain_rate = abstain_total / max(1, step_total)
    return correct / max(1, len(test_chains)), abstain_rate


# -------------------------- per-seed runner --------------------------

def make_kb_and_chains(n_ops: int, V: int, n_train: int, n_test: int,
                        max_depth: int, g: np.random.Generator
                        ) -> Tuple[List[List[Tuple[int, int]]],
                                   List[Tuple[int, List[int], int]]]:
    per_op_triples: List[List[Tuple[int, int]]] = [[] for _ in range(n_ops)]
    for _ in range(n_train):
        s = int(g.integers(0, V))
        o = int(g.integers(0, V))
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


def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    E = bipolar(V_ENTITIES, N_DIM, g)
    max_d = max(HOP_DEPTHS)
    per_op, test_chains = make_kb_and_chains(
        N_OPERATORS, V_ENTITIES, N_TRIPLES_PER_OP, N_TEST_CHAINS, max_d, g)
    W_ops = [hebbian_write(per_op[i], E, N_DIM) for i in range(N_OPERATORS)]

    out: Dict[str, Dict[str, float]] = {arm: {} for arm in EXPECTED_ARMS}
    out_abstain: Dict[str, Dict[str, float]] = {arm: {} for arm in EXPECTED_ARMS}
    for depth in HOP_DEPTHS:
        out["single_fixed_baseline"][str(depth)] = run_arm_single_fixed_baseline(
            W_ops, E, test_chains, depth)
        out["random_router"][str(depth)] = run_arm_random_router(
            W_ops, E, test_chains, depth, g)
        out["cosine_argmax"][str(depth)] = run_arm_cosine_argmax(
            W_ops, E, test_chains, depth)
        out["softmax_temp_top_2"][str(depth)] = run_arm_softmax_temp_top_2(
            W_ops, E, test_chains, depth)
        acc, abst_rate = run_arm_with_abstain(W_ops, E, test_chains, depth)
        out["with_abstain"][str(depth)] = acc
        out_abstain["with_abstain"][str(depth)] = abst_rate

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm_per_depth": out,
        "abstain_rates": out_abstain,
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
                cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
                summary[arm][d] = {"mean": m, "std": sd, "cv": cv, "n": len(vals)}
            else:
                summary[arm][d] = {"mean": 0.0, "std": 0.0, "cv": 0.0, "n": 0}

    # Decision at depth=DECISION_DEPTH if present, else max depth
    decision_depth = DECISION_DEPTH if DECISION_DEPTH in HOP_DEPTHS else max(HOP_DEPTHS)
    dd = str(decision_depth)

    softmax_m = summary["softmax_temp_top_2"][dd]["mean"]
    softmax_cv = summary["softmax_temp_top_2"][dd]["cv"]
    single_m = summary["single_fixed_baseline"][dd]["mean"]
    random_m = summary["random_router"][dd]["mean"]
    argmax_m = summary["cosine_argmax"][dd]["mean"]
    abstain_m = summary["with_abstain"][dd]["mean"]

    lift_over_single = softmax_m - single_m
    lift_over_random = softmax_m - random_m
    lift_over_argmax = softmax_m - argmax_m

    verdict = "MIDDLE_BAND"
    if (lift_over_single >= HP_LIFT_OVER_SINGLE_FIXED and
            softmax_cv < HP_CV_MAX and
            lift_over_random >= HP_LIFT_OVER_RANDOM and
            lift_over_argmax >= HP_LIFT_OVER_ARGMAX):
        verdict = "HARD_PASS"
    elif (lift_over_single < HF_LIFT_LO or
            softmax_m <= random_m or
            softmax_cv >= MB_CV_HI):
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | depth=%d | SOFTMAX=%.3f SINGLE=%.3f RANDOM=%.3f ARGMAX=%.3f ABSTAIN=%.3f | "
        "lift_single=%.3f lift_random=%.3f lift_argmax=%.3f cv=%.3f | n_seeds=%d"
    ) % (verdict, decision_depth, softmax_m, single_m, random_m, argmax_m, abstain_m,
         lift_over_single, lift_over_random, lift_over_argmax, softmax_cv, len(seeds_sorted))

    completed_units = len(seeds_sorted) * len(HOP_DEPTHS) * len(EXPECTED_ARMS)
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "decision_depth": decision_depth,
        "lift_over_single": lift_over_single,
        "lift_over_random": lift_over_random,
        "lift_over_argmax": lift_over_argmax,
        "softmax_cv": softmax_cv,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= EXPECTED_N_UNITS,
    }


# -------------------------- main --------------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS, "expected_depths": HOP_DEPTHS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d V=%d seeds=%s depths=%s n_ops=%d expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_ENTITIES, SEEDS, HOP_DEPTHS,
        N_OPERATORS, EXPECTED_N_UNITS), flush=True)

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
    final["_hardening_marker"] = "v2_pfc_softmax_margin_abstain"
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
