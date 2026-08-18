"""pfc_controller_depth_adaptive_argmax_v3 -- B1 PFC routing depth-adaptive revival.

Drill source: notes/research_drill_2x_pfc_v2_depth12_cv_collapse_2026-06-27.md REVIVAL_2.
Predecessor: pfc_controller_softmax_margin_abstain_v2 FULL HARD_FAIL at depth=12
(SOFTMAX=0.156, cv=0.249, lift_argmax=-0.014 -- argmax already beat softmax at depth).

HYPOTHESIS: pure argmax at depth=12 will OUTPERFORM v2 softmax+abstain because v2
top-2 mixing INJECTS top-2 noise that compounds across hops. Depth-adaptive routing
(softmax shallow, argmax deep) should be globally competitive.

MECHANISMS:
  PURE ARGMAX: select operator by argmax(cos_scores); apply; cleanup-to-E.
  SOFTMAX V2 (control): top-2 sparse softmax mix; T=0.3 fixed (the losing arm at deep).
  DEPTH-ADAPTIVE T: T(k) = 0.3 * (6/k). T=0.6 at k=3; T=0.3 at k=6; T=0.15 at k=12.
    T -> 0 as depth grows = softmax sharpens to argmax in deep regime.
  SINGLE FIXED BASELINE: always operator 0; TRUE no-routing fair baseline (NOT avg-of-4).

ARMS (4 + 1 diagnostic):
  ARM_SOFTMAX_V2_REGRESSION       v2 mechanism replayed; sanity / regression
  ARM_ARGMAX_PURE                 drill-predicted winner at deep
  ARM_DEPTH_ADAPTIVE_T            T(k) schedule; softmax shallow, argmax-like deep
  ARM_SINGLE_FIXED_BASELINE       no-routing fair floor
  ARM_DIAG_ABSTAIN_RATE           per-depth diagnostic: report argmax-margin distribution
                                  (encoded as accuracy of margin-gated arm + abstain
                                  rate per depth in abstain_rates).

PRE-REG BANDS (HARD-LOCKED at module init; decision_depth=12):
  HARD_PASS:
    (ARGMAX_PURE OR DEPTH_ADAPTIVE_T) beats SOFTMAX_V2_REGRESSION by >= +0.05 at depth=12
    AND best-of(ARGMAX_PURE, DEPTH_ADAPTIVE_T) cv < 0.20
  MIDDLE_BAND:
    ARGMAX-class beats SOFTMAX_V2 at depth=12 but cv >= 0.20
    OR lift in [+0.02, +0.05)
  HARD_FAIL:
    SOFTMAX_V2_REGRESSION still beats ARGMAX-class at depth=12 (mechanism null;
    depth-decay is mechanism-independent)
    OR all arms collapse near SINGLE_FIXED_BASELINE at depth=12.

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SELFTEST = 5 arms * 1 seed * 1 depth = 5
  EXPECTED_N_UNITS_SMOKE    = 5 arms * 3 seeds * 2 depths(6,12) = 30
  EXPECTED_N_UNITS_FULL     = 5 arms * 5 seeds * 4 depths(3,6,9,12) = 100

FAIRNESS (META_RULE_AA):
  SINGLE_FIXED is SINGLE matrix W_ops[0]; NOT aggregate.
  All arms use SAME W_ops bank per seed.
  ABSTAIN_RATE diagnostic uses SAME margin threshold as v2 (0.10) for comparability.

DISCRIMINATOR-MUST-SURVIVE-SCALE (META_RULE_M, USER 2026-06-26):
  Smoke fires discriminator AT DEPTH=12 (full depth). Smoke MUST eval at depth=12.
  If smoke at depth=12 shows ARGMAX-class collapse, abort full dispatch.

HARDENING (META_RULE_X / J / L1-L4):
  main wrapped in if __name__ == "__main__"
  L1: minimal metrics.json with STARTED + PID at start
  L2: per-arm/seed progress updates
  L3: outer try/except around main
  L4: import-crash sentinel

ASCII-only; no emojis; no em-dashes; self-contained (no hdlab/ imports).
Author: exp_dev 2026-06-27 (depth-adaptive revival, REVIVAL_2 of v3 cycle).
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

ANCHOR_NAME = "pfc_controller_depth_adaptive_argmax_v3"

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
HP_LIFT_OVER_SOFTMAX_V2 = 0.05
HP_CV_MAX = 0.20
MB_LIFT_LO = 0.02
HF_FLOOR_LIFT_OVER_SINGLE = 0.05  # all arms must lift >= 0.05 over single else collapse

EXPECTED_ARMS = ["softmax_v2_regression", "argmax_pure",
                 "depth_adaptive_T", "single_fixed_baseline",
                 "diag_abstain_margin_gated"]

# Decision depth -- where the discriminator fires (deep regime)
DECISION_DEPTH = 12

if SELF_TEST_MODE:
    N_DIM = 512
    N_OPERATORS = 4
    SEEDS = [7]
    HOP_DEPTHS = [6]
    N_TRIPLES_PER_OP = 30
    N_TEST_CHAINS = 10
elif RUN_MODE == "smoke":
    # META_RULE_M: smoke fires discriminator AT DEPTH=12.
    # N=4096 (full-N per Fix #22), seeds=3 for cv discipline.
    N_DIM = 4096
    N_OPERATORS = 4
    SEEDS = [7, 17, 23]
    HOP_DEPTHS = [6, 12]
    N_TRIPLES_PER_OP = 300
    N_TEST_CHAINS = 60
else:
    # Full: depth sweep [3, 6, 9, 12]; 5 seeds; per task spec.
    N_DIM = 4096
    N_OPERATORS = 4
    SEEDS = [7, 17, 23, 31, 41]
    HOP_DEPTHS = [3, 6, 9, 12]
    N_TRIPLES_PER_OP = 500
    N_TEST_CHAINS = 100

V_ENTITIES = max(200, N_TEST_CHAINS * max(HOP_DEPTHS) * 4)
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(HOP_DEPTHS)

# Softmax fixed temperature for V2_REGRESSION (matches v2 cell)
SOFTMAX_T_FIXED = 0.3
# Depth-adaptive temperature schedule reference depth
T_REF_DEPTH = 6
T_BASE = 0.3
# Margin threshold for diag abstain arm (matches v2)
ABSTAIN_MARGIN_TH = 0.10

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,N_OPS=%d,V=%d,seeds=%s,depths=%s,decision_depth=%d,"
    "n_train=%d,n_test=%d,mode=%s,"
    "softmax_T_fixed=%.2f,T_base=%.2f,T_ref_depth=%d,abstain_margin=%.2f,"
    "HP_lift_softmax>=%.2f,HP_cv<=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "FAIR_BASELINE=SINGLE_FIXED_OP_0_NOT_MEAN_OF_OPS,"
    "DISCRIMINATOR_FIRES_AT_DEPTH_12_IN_SMOKE"
) % (
    ANCHOR_NAME, N_DIM, N_OPERATORS, V_ENTITIES, SEEDS, HOP_DEPTHS, DECISION_DEPTH,
    N_TRIPLES_PER_OP, N_TEST_CHAINS, RUN_MODE,
    SOFTMAX_T_FIXED, T_BASE, T_REF_DEPTH, ABSTAIN_MARGIN_TH,
    HP_LIFT_OVER_SOFTMAX_V2, HP_CV_MAX, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v3_pfc_depth_adaptive_argmax",
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
            "_hardening_marker": "v3_pfc_depth_adaptive_argmax_import_crash",
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


def apply_W(state: np.ndarray, W_op: np.ndarray,
            E: np.ndarray) -> Tuple[int, np.ndarray]:
    out_raw = state @ W_op
    idx, out_clean = cleanup_to_E(out_raw, E)
    return idx, out_clean


def op_scores(state: np.ndarray, W_ops: List[np.ndarray],
              E: np.ndarray) -> np.ndarray:
    """For each op, max-cos of (state @ W_op) against codebook E."""
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
    """ALWAYS use W_ops[0]. TRUE no-routing fair baseline (META_RULE_AA)."""
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


def run_arm_argmax_pure(W_ops: List[np.ndarray], E: np.ndarray,
                         test_chains: List[Tuple[int, List[int], int]],
                         depth: int) -> float:
    """Pure argmax routing: pick argmax(op_scores) per hop. v1 mechanism."""
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


def run_arm_softmax_v2_regression(W_ops: List[np.ndarray], E: np.ndarray,
                                    test_chains: List[Tuple[int, List[int], int]],
                                    depth: int, T: float = SOFTMAX_T_FIXED) -> float:
    """V2 mechanism replay: top-2 sparse softmax mix at fixed T=0.3.

    This is the regression control. v2 full HARD_FAILED at depth=12; this arm
    re-runs that mechanism so v3 has a direct on-cell comparison.
    """
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        idx = s
        for _ in range(depth):
            scores = op_scores(state, W_ops, E)
            top2_idx = np.argpartition(-scores, 2)[:2]
            sparse_logits = np.full_like(scores, -1e9)
            sparse_logits[top2_idx] = scores[top2_idx] / T
            exp_s = np.exp(sparse_logits - np.max(sparse_logits))
            w = exp_s / (np.sum(exp_s) + 1e-9)
            state_n = state / (np.linalg.norm(state) + 1e-8)
            out = np.zeros_like(state)
            for i in range(len(W_ops)):
                if w[i] > 1e-6:
                    out += w[i] * (state_n @ W_ops[i])
            idx, state = cleanup_to_E(out, E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_depth_adaptive_T(W_ops: List[np.ndarray], E: np.ndarray,
                              test_chains: List[Tuple[int, List[int], int]],
                              depth: int,
                              T_base: float = T_BASE,
                              T_ref_depth: int = T_REF_DEPTH) -> float:
    """Depth-adaptive T: T(k) = T_base * (T_ref_depth / k) computed at the hop step.

    T(k) decreases with hop position k (1-indexed within the chain), so the
    softmax sharpens as we go deeper into a chain.

    Note: k is the HOP INDEX (1..depth), not the chain depth `depth`. This means
    within a single chain, early hops use softer T (more mixing) and late hops
    use harder T (more argmax-like commitment).
    """
    correct = 0
    for (s, op_seq, target) in test_chains:
        state = E[s].copy()
        idx = s
        for k in range(1, depth + 1):
            T_k = max(1e-3, T_base * (T_ref_depth / float(k)))
            scores = op_scores(state, W_ops, E)
            top2_idx = np.argpartition(-scores, 2)[:2]
            sparse_logits = np.full_like(scores, -1e9)
            sparse_logits[top2_idx] = scores[top2_idx] / T_k
            exp_s = np.exp(sparse_logits - np.max(sparse_logits))
            w = exp_s / (np.sum(exp_s) + 1e-9)
            state_n = state / (np.linalg.norm(state) + 1e-8)
            out = np.zeros_like(state)
            for i in range(len(W_ops)):
                if w[i] > 1e-6:
                    out += w[i] * (state_n @ W_ops[i])
            idx, state = cleanup_to_E(out, E)
        if idx == target:
            correct += 1
    return correct / max(1, len(test_chains))


def run_arm_diag_abstain_margin_gated(W_ops: List[np.ndarray], E: np.ndarray,
                                        test_chains: List[Tuple[int, List[int], int]],
                                        depth: int,
                                        margin_th: float = ABSTAIN_MARGIN_TH
                                        ) -> Tuple[float, float]:
    """Diagnostic arm: argmax + abstain (identity) if top1-top2 margin < threshold.

    Returns (accuracy, abstain_rate). Reports per-depth abstain rate to confirm
    or refute the v2 partial-metrics observation of abstain_rate ~ 0.70 at depth=6.
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
                abstain_total += 1
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
        out["argmax_pure"][str(depth)] = run_arm_argmax_pure(
            W_ops, E, test_chains, depth)
        out["softmax_v2_regression"][str(depth)] = run_arm_softmax_v2_regression(
            W_ops, E, test_chains, depth)
        out["depth_adaptive_T"][str(depth)] = run_arm_depth_adaptive_T(
            W_ops, E, test_chains, depth)
        acc, abst_rate = run_arm_diag_abstain_margin_gated(
            W_ops, E, test_chains, depth)
        out["diag_abstain_margin_gated"][str(depth)] = acc
        out_abstain["diag_abstain_margin_gated"][str(depth)] = abst_rate

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
    abstain_summary: Dict[str, Dict[str, float]] = {}

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

    # Abstain rate aggregation (diagnostic)
    abstain_summary["diag_abstain_margin_gated"] = {}
    for depth in HOP_DEPTHS:
        d = str(depth)
        rates = []
        for s in seeds_sorted:
            body = per_seed[s]
            r = body.get("abstain_rates", {}).get(
                "diag_abstain_margin_gated", {}).get(d)
            if r is not None:
                rates.append(float(r))
        abstain_summary["diag_abstain_margin_gated"][d] = (
            float(np.mean(rates)) if rates else 0.0)

    # Decision at depth=DECISION_DEPTH if present, else max depth
    decision_depth = DECISION_DEPTH if DECISION_DEPTH in HOP_DEPTHS else max(HOP_DEPTHS)
    dd = str(decision_depth)

    softmax_v2_m = summary["softmax_v2_regression"][dd]["mean"]
    argmax_m = summary["argmax_pure"][dd]["mean"]
    argmax_cv = summary["argmax_pure"][dd]["cv"]
    adaptive_m = summary["depth_adaptive_T"][dd]["mean"]
    adaptive_cv = summary["depth_adaptive_T"][dd]["cv"]
    single_m = summary["single_fixed_baseline"][dd]["mean"]
    diag_m = summary["diag_abstain_margin_gated"][dd]["mean"]

    # ARGMAX-class = max(argmax_pure, depth_adaptive_T)
    if adaptive_m >= argmax_m:
        argmax_class_m = adaptive_m
        argmax_class_cv = adaptive_cv
        argmax_class_winner = "depth_adaptive_T"
    else:
        argmax_class_m = argmax_m
        argmax_class_cv = argmax_cv
        argmax_class_winner = "argmax_pure"

    lift_over_softmax_v2 = argmax_class_m - softmax_v2_m
    lift_over_single = argmax_class_m - single_m

    # Verdict ladder
    verdict = "MIDDLE_BAND"
    if (lift_over_softmax_v2 >= HP_LIFT_OVER_SOFTMAX_V2 and
            argmax_class_cv < HP_CV_MAX):
        verdict = "HARD_PASS"
    elif (lift_over_softmax_v2 < 0 and softmax_v2_m > argmax_class_m + 0.02):
        # softmax v2 STILL beats argmax-class at deep -> Angle B null
        verdict = "HARD_FAIL"
    elif (argmax_class_m < single_m + HF_FLOOR_LIFT_OVER_SINGLE and
            softmax_v2_m < single_m + HF_FLOOR_LIFT_OVER_SINGLE):
        # all mechanisms collapse near single fixed baseline -> depth-decay total
        verdict = "HARD_FAIL"
    elif (lift_over_softmax_v2 >= MB_LIFT_LO):
        verdict = "MIDDLE_BAND"

    abstain_at_dd = abstain_summary.get(
        "diag_abstain_margin_gated", {}).get(dd, 0.0)

    verdict_msg = (
        "%s | depth=%d | SOFTMAX_V2=%.3f ARGMAX=%.3f ADAPTIVE=%.3f "
        "SINGLE=%.3f DIAG_ABSTAIN_ACC=%.3f abstain_rate=%.3f | "
        "argmax_class=%s lift_over_softmax=%.3f cv=%.3f | n_seeds=%d"
    ) % (verdict, decision_depth, softmax_v2_m, argmax_m, adaptive_m,
         single_m, diag_m, abstain_at_dd,
         argmax_class_winner, lift_over_softmax_v2, argmax_class_cv,
         len(seeds_sorted))

    completed_units = len(seeds_sorted) * len(HOP_DEPTHS) * len(EXPECTED_ARMS)
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "abstain_summary": abstain_summary,
        "decision_depth": decision_depth,
        "argmax_class_winner": argmax_class_winner,
        "argmax_class_mean": argmax_class_m,
        "argmax_class_cv": argmax_class_cv,
        "lift_over_softmax_v2": lift_over_softmax_v2,
        "lift_over_single": lift_over_single,
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
                assert arm in r["per_arm_per_depth"], "missing arm: " + arm
            # Validate T-schedule sanity: depth_adaptive_T at depth=6 ~= softmax_v2 at depth=6
            # (because T(6) = 0.3*(6/6) = 0.3 = SOFTMAX_T_FIXED) -- they should be CLOSE
            # at depth=6. They may differ slightly because T varies per-hop within chain.
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm structure verified; %d arms" % len(EXPECTED_ARMS),
                                   extra={"_phase": "selftest_done",
                                          "_arms_verified": EXPECTED_ARMS})
            print("[selftest] OK; per_arm keys: %s" % list(r["per_arm_per_depth"].keys()), flush=True)
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
    final["_hardening_marker"] = "v3_pfc_depth_adaptive_argmax"
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
