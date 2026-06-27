"""loopy_belief_propagation_damped_v1 -- Battery 2 Barrier 1 Angle 1 pure-math drill (CPU).

Prereg: preregs/2026-06-27_loopy_belief_propagation_damped_v1.md
Drill source: 4-cycle heterogeneous query; loopy BP with damping (Pearl 1988 + Murphy et al 1999).

DIFFERENTIAL from 2026-06-24 soft-superposition HARD_FAIL:
  soft-superposition v1 added soft mixing of NEIGHBOR states (averaging in superposition)
  -> failed (saturating crosstalk, no iteration, no damping).
  THIS cell adds (a) explicit MULTI-STEP message-passing iteration, (b) DAMPING (Murphy et al
  damping factor; alpha in (0,1) mixes old/new messages each iteration), and (c) EXTRINSIC
  INFORMATION (each message excludes the receiver-to-sender prior, the classical BP requirement).
  Different mechanism class entirely; legitimate revival.

TASK -- 4-cycle heterogeneous query:
  Build a 4-cycle factor graph over 4 variable nodes (a -- b -- c -- d -- a), with 4 edge factors.
  Each factor encodes one of N_OPS Hebbian operator relationships (sampled per cycle).
  Variable a is observed (initial state); query: argmax marginal at d after MP.

ARMS (4):
  ARM_D0_BASELINE              0 iterations of MP (just forward chain a->b->c->d) -- no loop
  ARM_D2_DAMPED                2 iterations of damped MP (alpha=0.3)
  ARM_D5_DAMPED                5 iterations of damped MP (alpha=0.3)
  ARM_D5_UNDAMPED              5 iterations of UNDAMPED MP (tests divergence; classic loopy-BP failure)

PRE-REG BANDS:
  HARD_PASS:
    D2 mean > D0 mean by >= +0.08
    AND D5_DAMPED mean > D0 mean by >= +0.08   (damped converges; doesn't diverge)
    AND D5_DAMPED >= D5_UNDAMPED - 0.05         (damping doesn't hurt, may help against undamped)
    AND cv across seeds < 0.10
  MIDDLE_BAND:
    D2 lift in [+0.04, +0.08) OR D5_DAMPED divergence relative to D2 < +0.04
  HARD_FAIL:
    D2 < D0 + 0.04 OR D5_DAMPED diverges below D0 - 0.05 (loops actively hurt)

FAIR-BASELINE (META_RULE_AA): D0 uses SAME factors, SAME readout (argmax marginal at d),
  SAME query distribution; only difference is the number of MP iterations + damping.

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SMOKE = 4 arms * 3 seeds * 1 depth(4-cycle) = 12
  EXPECTED_N_UNITS_FULL  = 4 arms * 5 seeds * 3 cycle-sizes(3,4,5) = 60

HARDENING: L1-L4 + main-guard.
ASCII-only; no emojis. Author: exp_dev 2026-06-27 (Battery 2 Barrier 1 Angle 1).
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

ANCHOR_NAME = "loopy_belief_propagation_damped_v1"

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
HP_LIFT_D2_OVER_D0 = 0.08
HP_LIFT_D5_OVER_D0 = 0.08
HP_D5_OVER_UNDAMPED_TOLERANCE = -0.05  # D5_DAMPED >= D5_UNDAMPED + this (tolerates -0.05)
HP_CV_MAX = 0.10
MB_LIFT_LO = 0.04
MB_CV_HI = 0.20
HF_LIFT_LO = 0.04
HF_DIVERGE_BELOW_D0 = -0.05   # D5_DAMPED < D0 + this counts as actively hurting

EXPECTED_ARMS = ["d0_baseline", "d2_damped", "d5_damped", "d5_undamped"]

DAMPING_ALPHA = 0.3

if SELF_TEST_MODE:
    N_DIM = 512
    N_OPERATORS = 4
    SEEDS = [7]
    CYCLE_SIZES = [4]
    N_TRIPLES_PER_OP = 30
    N_TEST_CYCLES = 10
elif RUN_MODE == "smoke":
    N_DIM = 4096
    N_OPERATORS = 4
    SEEDS = [7, 17, 23]
    CYCLE_SIZES = [4]
    N_TRIPLES_PER_OP = 300
    N_TEST_CYCLES = 60
else:
    N_DIM = 8192
    N_OPERATORS = 4
    SEEDS = [7, 17, 23, 31, 41]
    CYCLE_SIZES = [3, 4, 5]
    N_TRIPLES_PER_OP = 500
    N_TEST_CYCLES = 100

V_ENTITIES = max(200, N_TEST_CYCLES * max(CYCLE_SIZES) * 4)
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(CYCLE_SIZES)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,N_OPS=%d,V=%d,seeds=%s,cycle_sizes=%s,"
    "n_train=%d,n_test=%d,mode=%s,damping_alpha=%.2f,"
    "HP_d2_lift>=%.2f,HP_d5_lift>=%.2f,HP_cv<=%.2f,expected_n=%d,"
    "FAIR=SAME_FACTORS_SAME_READOUT_DIFFER_ONLY_MP_ITERS,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, N_OPERATORS, V_ENTITIES, SEEDS, CYCLE_SIZES,
    N_TRIPLES_PER_OP, N_TEST_CYCLES, RUN_MODE, DAMPING_ALPHA,
    HP_LIFT_D2_OVER_D0, HP_LIFT_D5_OVER_D0, HP_CV_MAX, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v1_loopy_bp_damped",
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
            "_hardening_marker": "v1_loopy_bp_damped_import_crash",
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


def hebbian_write(triples: List[Tuple[int, int]], E: np.ndarray, n_dim: int) -> np.ndarray:
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
    vn = v / (np.linalg.norm(v) + 1e-8)
    sims = E @ vn
    idx = int(np.argmax(sims))
    return idx, E[idx]


# -------------------------- arms --------------------------

def run_forward_chain(W_ops: List[np.ndarray], E: np.ndarray,
                       cycle_ops: List[int], obs_state: np.ndarray) -> Tuple[int, np.ndarray]:
    """ARM_D0: just forward chain a->b->c->d using op_seq. No loop; no MP iterations."""
    state = obs_state.copy()
    idx_last = -1
    for op in cycle_ops:
        out = state @ W_ops[op]
        idx_last, state = cleanup_to_E(out, E)
    return idx_last, state


def run_loopy_bp(W_ops: List[np.ndarray], E: np.ndarray,
                  cycle_ops: List[int], obs_state: np.ndarray,
                  n_iters: int, alpha_damp: float) -> Tuple[int, np.ndarray]:
    """Damped loopy BP on a cycle.

    Variables v0..v_{k-1} arranged in cycle; v0 observed. Each edge factor i (between v_i and v_{i+1})
    is operator W_ops[cycle_ops[i]] (forward) and W_ops[cycle_ops[i]].T (reverse).

    Messages:
      m_{i->i+1}^t = clean( (incoming-without-back-edge) @ W_op_i )
    Init: each variable's state = uniform-ish (small noise) except v0 = obs_state.
    Damped update: msg^{t+1} = (1-alpha) * msg^t + alpha * new_msg, then renormalize.

    For HD-substrate: state vectors are unit-norm; messages are also unit-norm HD vectors.
    Marginal at target = aggregated (sum) of incoming messages, then cleanup_to_E.
    Returns argmax-index at last variable (v_{k-1}).
    """
    k = len(cycle_ops) + 1  # cycle has k variable nodes; cycle_ops has k edges (closes the cycle? we treat as path here)
    # NB: for true 4-cycle, edges = k variables; cycle_ops has k entries (one per edge), last closes to v0.
    # Our op_seq has len = cycle_size; we'll treat it as cycle: var_i -> var_{(i+1) mod k}.
    n_vars = len(cycle_ops)
    # State estimates per variable (start at noise except observed v0)
    states = [None] * n_vars
    n = obs_state.shape[0]
    states[0] = obs_state.copy()
    for i in range(1, n_vars):
        # Init non-observed with small random noise (use deterministic from obs_state)
        noise = (obs_state * 0.1).copy()
        states[i] = noise / (np.linalg.norm(noise) + 1e-8)

    # Messages: msg[i] = m_{i -> (i+1) mod n_vars}; initial = zeros
    msgs = [np.zeros(n, dtype=np.float32) for _ in range(n_vars)]
    # Reverse messages: rmsg[i] = m_{(i+1) mod n_vars -> i}
    rmsgs = [np.zeros(n, dtype=np.float32) for _ in range(n_vars)]

    for it in range(n_iters):
        new_msgs = []
        new_rmsgs = []
        # Forward pass
        for i in range(n_vars):
            j = (i + 1) % n_vars
            # m_{i->j} = (state_i * (excluding back-msg from j)) @ W_ops[cycle_ops[i]]
            # Aggregated state at i excluding back-msg from j: state[i] + rmsg from neighbor OTHER than j
            prev_i = (i - 1) % n_vars
            agg_state = states[i] + rmsgs[prev_i]   # incoming from the OTHER neighbor
            agg_n = agg_state / (np.linalg.norm(agg_state) + 1e-8)
            new_m = agg_n @ W_ops[cycle_ops[i]]
            # Damped update
            damped = (1.0 - alpha_damp) * msgs[i] + alpha_damp * new_m
            damped_n = damped / (np.linalg.norm(damped) + 1e-8)
            new_msgs.append(damped_n)

            # Reverse: m_{j->i} = (state_j + msg from j's other neighbor) @ W_ops[cycle_ops[i]].T
            next_j = (j + 1) % n_vars
            agg_state_j = states[j] + msgs[next_j]   # incoming to j from its OTHER neighbor
            agg_n_j = agg_state_j / (np.linalg.norm(agg_state_j) + 1e-8)
            new_rm = agg_n_j @ W_ops[cycle_ops[i]].T
            damped_r = (1.0 - alpha_damp) * rmsgs[i] + alpha_damp * new_rm
            damped_r_n = damped_r / (np.linalg.norm(damped_r) + 1e-8)
            new_rmsgs.append(damped_r_n)

        msgs = new_msgs
        rmsgs = new_rmsgs

        # Update state estimates from incoming messages
        for j in range(1, n_vars):    # v0 is observed; do not update
            prev_j = (j - 1) % n_vars
            next_j = j  # rmsg from j+1
            inc = msgs[prev_j] + rmsgs[next_j]
            inc_n = inc / (np.linalg.norm(inc) + 1e-8)
            states[j] = inc_n

    # Read out final marginal at v_{n_vars-1}
    final = states[n_vars - 1]
    idx, _ = cleanup_to_E(final, E)
    return idx, final


# -------------------------- per-seed runner --------------------------

def make_kb_and_cycles(n_ops: int, V: int, n_train: int, n_test: int,
                        cycle_size: int, g: np.random.Generator
                        ) -> Tuple[List[List[Tuple[int, int]]],
                                   List[Tuple[int, List[int], int]]]:
    per_op_triples: List[List[Tuple[int, int]]] = [[] for _ in range(n_ops)]
    for _ in range(n_train):
        s = int(g.integers(0, V))
        o = int(g.integers(0, V))
        op = int(g.integers(0, n_ops))
        per_op_triples[op].append((s, o))

    test_cycles: List[Tuple[int, List[int], int]] = []
    attempts = 0
    while len(test_cycles) < n_test and attempts < n_test * 100:
        attempts += 1
        s = int(g.integers(0, V))
        cur = s
        op_seq: List[int] = []
        for _ in range(cycle_size):
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
        # Target = last variable in the cycle (forward chain end)
        test_cycles.append((s, op_seq, cur))
    return per_op_triples, test_cycles


def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    E = bipolar(V_ENTITIES, N_DIM, g)

    per_arm_per_cycle: Dict[str, Dict[str, float]] = {arm: {} for arm in EXPECTED_ARMS}
    for cycle_size in CYCLE_SIZES:
        per_op, test_cycles = make_kb_and_cycles(
            N_OPERATORS, V_ENTITIES, N_TRIPLES_PER_OP, N_TEST_CYCLES, cycle_size, g)
        W_ops = [hebbian_write(per_op[i], E, N_DIM) for i in range(N_OPERATORS)]

        def acc_for(arm_fn) -> float:
            correct = 0
            for (s, op_seq, target) in test_cycles:
                obs = E[s].copy()
                idx, _ = arm_fn(W_ops, E, op_seq, obs)
                if idx == target:
                    correct += 1
            return correct / max(1, len(test_cycles))

        d0_acc = acc_for(lambda Wo, Ee, ops, obs: run_forward_chain(Wo, Ee, ops, obs))
        d2_acc = acc_for(lambda Wo, Ee, ops, obs: run_loopy_bp(Wo, Ee, ops, obs,
                                                                  n_iters=2, alpha_damp=DAMPING_ALPHA))
        d5_damp = acc_for(lambda Wo, Ee, ops, obs: run_loopy_bp(Wo, Ee, ops, obs,
                                                                    n_iters=5, alpha_damp=DAMPING_ALPHA))
        d5_undamp = acc_for(lambda Wo, Ee, ops, obs: run_loopy_bp(Wo, Ee, ops, obs,
                                                                      n_iters=5, alpha_damp=1.0))

        cs_key = str(cycle_size)
        per_arm_per_cycle["d0_baseline"][cs_key] = d0_acc
        per_arm_per_cycle["d2_damped"][cs_key] = d2_acc
        per_arm_per_cycle["d5_damped"][cs_key] = d5_damp
        per_arm_per_cycle["d5_undamped"][cs_key] = d5_undamp

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm_per_cycle": per_arm_per_cycle,
        "damping_alpha": DAMPING_ALPHA,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN",
                "verdict_msg": "no per-seed partials found",
                "summary": "no per-seed partials found",
                "per_arm": {}}
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)
    summary: Dict[str, Dict[str, Dict[str, float]]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}

    for arm in EXPECTED_ARMS:
        summary[arm] = {}
        per_arm_full[arm] = {}
        for cs in CYCLE_SIZES:
            cs_key = str(cs)
            vals: List[float] = []
            per_arm_full[arm][cs_key] = {}
            for s in seeds_sorted:
                body = per_seed[s]
                v = body.get("per_arm_per_cycle", {}).get(arm, {}).get(cs_key)
                if v is not None:
                    vals.append(float(v))
                    per_arm_full[arm][cs_key][s] = float(v)
            if vals:
                m = float(np.mean(vals))
                sd = float(np.std(vals)) if n_seeds > 1 else 0.0
                cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
                summary[arm][cs_key] = {"mean": m, "std": sd,
                                          "cv": cv, "n": len(vals)}
            else:
                summary[arm][cs_key] = {"mean": 0.0, "std": 0.0, "cv": 0.0, "n": 0}

    decision_cycle = 4 if 4 in CYCLE_SIZES else max(CYCLE_SIZES)
    dc = str(decision_cycle)
    d0_m = summary["d0_baseline"][dc]["mean"]
    d2_m = summary["d2_damped"][dc]["mean"]
    d2_cv = summary["d2_damped"][dc]["cv"]
    d5d_m = summary["d5_damped"][dc]["mean"]
    d5d_cv = summary["d5_damped"][dc]["cv"]
    d5u_m = summary["d5_undamped"][dc]["mean"]

    lift_d2 = d2_m - d0_m
    lift_d5d = d5d_m - d0_m
    damping_help = d5d_m - d5u_m   # >=0 means damping helps; large negative = damping hurts

    verdict = "MIDDLE_BAND"
    if (lift_d2 >= HP_LIFT_D2_OVER_D0 and
            lift_d5d >= HP_LIFT_D5_OVER_D0 and
            damping_help >= HP_D5_OVER_UNDAMPED_TOLERANCE and
            d2_cv < HP_CV_MAX and d5d_cv < HP_CV_MAX):
        verdict = "HARD_PASS"
    elif (lift_d2 < HF_LIFT_LO or
            lift_d5d < HF_DIVERGE_BELOW_D0):   # D5_DAMPED actively hurts
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | cycle=%d | D0=%.3f D2_damp=%.3f D5_damp=%.3f D5_undamp=%.3f | "
        "lift_d2=%+.3f lift_d5d=%+.3f damping_help=%+.3f cv_d2=%.3f cv_d5d=%.3f | n_seeds=%d"
    ) % (verdict, decision_cycle, d0_m, d2_m, d5d_m, d5u_m,
         lift_d2, lift_d5d, damping_help, d2_cv, d5d_cv, n_seeds)

    completed_units = n_seeds * len(CYCLE_SIZES) * len(EXPECTED_ARMS)
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "decision_cycle": decision_cycle,
        "lift_d2_over_d0": lift_d2,
        "lift_d5d_over_d0": lift_d5d,
        "damping_help": damping_help,
        "n_seeds_complete": n_seeds,
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
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_cycles": CYCLE_SIZES,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d V=%d seeds=%s cycles=%s n_ops=%d expected_n=%d alpha=%.2f" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_ENTITIES, SEEDS, CYCLE_SIZES,
        N_OPERATORS, EXPECTED_N_UNITS, DAMPING_ALPHA), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm_per_cycle" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_per_cycle"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm + per-cycle structure verified",
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
    final["_hardening_marker"] = "v1_loopy_bp_damped"
    (out_dir / "metrics.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
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
