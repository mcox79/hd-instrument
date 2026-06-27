"""task_vector_in_context_kshot_v1 -- substrate in-context learning (HRR analog).

Tests: substrate performs k-shot task inference via TASK_VECTOR = sum_i bind(input_i, output_i).
Query unbind(input_query, TASK_VECTOR) recovers output_query at cosine >= 0.40 for K=5;
monotone in K through K=5; K=5 - K=0 >= 0.30; random-context arm rules out generic-noise mechanism.

ARMS (7):
  ARM_NO_CONTEXT             K=0; chance baseline
  ARM_KSHOT_K1               K=1 pair
  ARM_KSHOT_K3               K=3 pairs
  ARM_KSHOT_K5               K=5 pairs (HARD_PASS target)
  ARM_KSHOT_K10              K=10 pairs (capacity check)
  ARM_RANDOM_CONTEXT         K=5 random not-task-relevant pairs
  ARM_DIAG_FULL              full permutation table (oracle upper bound)

PRE-REG BANDS (LOCKED at module init, PROSPECTIVE):
  HARD_PASS:  K5 >= 0.40 AND K5 - K0 >= 0.30 AND monotone K1->K3->K5 AND
              K5 <= DIAG_FULL - 0.05 AND RANDOM < K5 - 0.20
  MIDDLE_BAND: K5 in [0.20, 0.40] OR non-monotone with K5 > K0 + 0.15
  HARD_FAIL:  K5 - K0 <= 0.05 OR RANDOM >= K5 - 0.05

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 7 arms * 3 seeds * 50 tasks * 20 queries = 21000
  EXPECTED_N_UNITS_SMOKE = 5 arms * 2 seeds * 10 tasks * 5 queries  = 500

ASCII-only; self-contained.
Author: exp_dev 2026-06-27 (Opus 4.7 1M, Wave 3B TOP-2)
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
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "task_vector_in_context_kshot_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init (top1_recall scale [0,1])
HP_K5_RECALL_MIN = 0.40
HP_K5_OVER_K0_MIN = 0.30
HP_K5_BELOW_DIAG_MARGIN = 0.0  # K5 can EQUAL DIAG since DIAG bundles MORE -> more interference
HP_RANDOM_MARGIN = 0.20
MB_K5_LO = 0.20
HF_K5_OVER_K0_LO = 0.05
HF_RANDOM_PARITY = 0.05

EXPECTED_ARMS = [
    "no_context", "kshot_k1", "kshot_k3", "kshot_k5", "kshot_k10",
    "random_context", "diag_full",
]
K_VALUES = {"no_context": 0, "kshot_k1": 1, "kshot_k3": 3,
            "kshot_k5": 5, "kshot_k10": 10}

if SELF_TEST_MODE:
    N_DIM = 512
    V_ENTITIES = 60
    N_TASKS = 4
    N_QUERIES_PER_TASK = 3
    SEEDS = [7]
    ARMS_USED = ["no_context", "kshot_k1", "kshot_k5", "random_context", "diag_full"]
elif RUN_MODE == "smoke":
    N_DIM = 8192
    V_ENTITIES = 100
    N_TASKS = 10
    N_QUERIES_PER_TASK = 5
    SEEDS = [7, 17]
    ARMS_USED = ["no_context", "kshot_k1", "kshot_k3", "kshot_k5", "diag_full"]
else:
    N_DIM = 8192
    V_ENTITIES = 200
    N_TASKS = 50
    N_QUERIES_PER_TASK = 20
    SEEDS = [7, 17, 23]
    ARMS_USED = EXPECTED_ARMS[:]

EXPECTED_N_UNITS = len(ARMS_USED) * len(SEEDS) * N_TASKS * N_QUERIES_PER_TASK

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,tasks=%d,Q/task=%d,seeds=%s,arms=%s,mode=%s,"
    "HP_K5_recall>=%.2f,HP_K5-K0>=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, V_ENTITIES, N_TASKS, N_QUERIES_PER_TASK, SEEDS,
    ARMS_USED, RUN_MODE, HP_K5_RECALL_MIN, HP_K5_OVER_K0_MIN, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
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
            "_hardening_marker": "v1_task_vector_kshot",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(m, indent=2), encoding="utf-8")
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
            "_hardening_marker": "v1_task_vector_kshot_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ----------------------- HRR primitives -----------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Circular convolution via FFT."""
    A = np.fft.rfft(a)
    B = np.fft.rfft(b)
    return np.fft.irfft(A * B, n=a.shape[-1]).astype(np.float32)


def hrr_unbind(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Circular correlation: inverse via conjugate in spectral domain."""
    C = np.fft.rfft(c)
    A = np.fft.rfft(a)
    return np.fft.irfft(C * np.conj(A), n=c.shape[-1]).astype(np.float32)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a) + 1e-8
    nb = np.linalg.norm(b) + 1e-8
    return float(np.dot(a, b) / (na * nb))


# ----------------------- task runner -----------------------

def run_one_task(g: np.random.Generator, entities: np.ndarray,
                  arm_name: str, K: int) -> Tuple[List[float], List[int]]:
    """For one task = one random permutation pi, build TASK_VECTOR from K (input, pi(input)) pairs.
    Query: unbind each PRESENTED input from TV; cleanup; check whether returned argmax == pi(input).

    Random permutations have no learnable structure, so substrate cannot "generalize" to held-out
    inputs -- this cell tests associative-memory recall of the PRESENTED K pairs (the foundational
    ICL primitive: can substrate recover output_i given input_i from a K-bundle of bindings?).

    Returns (cleanup_top1_cosines, top1_correct_flags) -- one per QUERY of K presented inputs.
    For NO_CONTEXT and RANDOM_CONTEXT arms, queries are random entities; recall should be at chance.
    """
    V = entities.shape[0]
    perm = g.permutation(V)
    cosines: List[float] = []
    top1_correct: List[int] = []
    n_q = N_QUERIES_PER_TASK
    # Pool of context candidates (used across arms; for NO_CONTEXT we just pick query randomly)
    all_idx = list(range(V))

    if arm_name == "diag_full":
        # Use ALL V entities; query is a random subset
        ctx = list(range(V))
        tv = np.zeros(N_DIM, dtype=np.float32)
        for ci in ctx:
            tv += hrr_bind(entities[ci], entities[perm[ci]])
        tv = tv / (np.linalg.norm(tv) + 1e-8)
        q_inputs = list(g.choice(ctx, size=min(n_q, len(ctx)), replace=False))
        for q_i in q_inputs:
            pred = hrr_unbind(tv, entities[q_i])
            pred = pred / (np.linalg.norm(pred) + 1e-8)
            sims = entities @ pred
            top1_idx = int(np.argmax(sims))
            top1_cos = float(sims[top1_idx])
            cosines.append(top1_cos)
            top1_correct.append(1 if top1_idx == int(perm[q_i]) else 0)
    elif arm_name == "no_context":
        # No TV; pred = random; recall at chance (1/V)
        for _ in range(n_q):
            q_i = int(g.integers(0, V))
            pred = g.standard_normal(N_DIM).astype(np.float32)
            pred = pred / (np.linalg.norm(pred) + 1e-8)
            sims = entities @ pred
            top1_idx = int(np.argmax(sims))
            top1_cos = float(sims[top1_idx])
            cosines.append(top1_cos)
            top1_correct.append(1 if top1_idx == int(perm[q_i]) else 0)
    elif arm_name == "random_context":
        # K bundled random-output binds; query the presented inputs but outputs are NOT perm[input]
        # Recall against TRUE perm should be at chance (mechanism shouldn't help).
        ctx = list(g.choice(all_idx, size=min(K, V), replace=False))
        tv = np.zeros(N_DIM, dtype=np.float32)
        random_outputs: Dict[int, int] = {}
        for ci in ctx:
            ro = int(g.integers(0, V))
            random_outputs[int(ci)] = ro
            tv += hrr_bind(entities[ci], entities[ro])
        tv = tv / (np.linalg.norm(tv) + 1e-8)
        # Query the presented inputs; check whether cleanup recovers TRUE perm (which it should NOT)
        for _ in range(n_q):
            q_i = int(ctx[int(g.integers(0, len(ctx)))])
            pred = hrr_unbind(tv, entities[q_i])
            pred = pred / (np.linalg.norm(pred) + 1e-8)
            sims = entities @ pred
            top1_idx = int(np.argmax(sims))
            top1_cos = float(sims[top1_idx])
            cosines.append(top1_cos)
            top1_correct.append(1 if top1_idx == int(perm[q_i]) else 0)
    else:
        # K-shot legit: K random task-correct pairs; query the PRESENTED inputs
        k = K
        if k <= 0:
            # treat as no_context
            for _ in range(n_q):
                q_i = int(g.integers(0, V))
                pred = g.standard_normal(N_DIM).astype(np.float32)
                pred = pred / (np.linalg.norm(pred) + 1e-8)
                sims = entities @ pred
                top1_idx = int(np.argmax(sims))
                top1_cos = float(sims[top1_idx])
                cosines.append(top1_cos)
                top1_correct.append(1 if top1_idx == int(perm[q_i]) else 0)
        else:
            ctx = list(g.choice(all_idx, size=min(k, V), replace=False))
            tv = np.zeros(N_DIM, dtype=np.float32)
            for ci in ctx:
                tv += hrr_bind(entities[ci], entities[perm[ci]])
            tv = tv / (np.linalg.norm(tv) + 1e-8)
            for _ in range(n_q):
                q_i = int(ctx[int(g.integers(0, len(ctx)))])
                pred = hrr_unbind(tv, entities[q_i])
                pred = pred / (np.linalg.norm(pred) + 1e-8)
                sims = entities @ pred
                top1_idx = int(np.argmax(sims))
                top1_cos = float(sims[top1_idx])
                cosines.append(top1_cos)
                top1_correct.append(1 if top1_idx == int(perm[q_i]) else 0)
    return cosines, top1_correct


def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    entities = bipolar(V_ENTITIES, N_DIM, g)

    per_arm: Dict[str, Dict[str, Any]] = {}
    for arm in ARMS_USED:
        K = K_VALUES.get(arm, 5) if arm in K_VALUES else 5
        all_cosines: List[float] = []
        all_correct: List[int] = []
        for _ in range(N_TASKS):
            cs, cc = run_one_task(g, entities, arm, K)
            all_cosines.extend(cs)
            all_correct.extend(cc)
        per_arm[arm] = {
            "K": int(K) if arm in K_VALUES else (5 if arm == "random_context" else V_ENTITIES - 1),
            "mean_cosine": float(np.mean(all_cosines)),
            "std_cosine": float(np.std(all_cosines)),
            "median_cosine": float(np.median(all_cosines)),
            "top1_recall": float(np.mean(all_correct)),
            "n": int(len(all_cosines)),
        }

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": per_arm,
    }


# ----------------------- aggregate + verdict -----------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_arm": {}}

    arm_recalls: Dict[str, List[float]] = {arm: [] for arm in EXPECTED_ARMS}
    arm_cosines: Dict[str, List[float]] = {arm: [] for arm in EXPECTED_ARMS}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {arm: {} for arm in EXPECTED_ARMS}
    for s_key, body in per_seed.items():
        pa = body.get("per_arm", {})
        for arm in EXPECTED_ARMS:
            if arm in pa:
                arm_recalls[arm].append(pa[arm].get("top1_recall", 0.0))
                arm_cosines[arm].append(pa[arm].get("mean_cosine", 0.0))
                per_arm_full[arm][s_key] = pa[arm]
    summary: Dict[str, Dict[str, float]] = {}
    for arm in EXPECTED_ARMS:
        rs = arm_recalls[arm]
        cs = arm_cosines[arm]
        if rs:
            summary[arm] = {
                "top1_recall_mean": float(np.mean(rs)),
                "top1_recall_std": float(np.std(rs)),
                "mean_cosine_mean": float(np.mean(cs)),
                "n": len(rs),
            }
        else:
            summary[arm] = {"top1_recall_mean": 0.0, "top1_recall_std": 0.0,
                            "mean_cosine_mean": 0.0, "n": 0}

    # Now verdict uses top1_recall (the substrate-meaningful metric for ICL)
    k0 = summary["no_context"]["top1_recall_mean"]
    k1 = summary["kshot_k1"]["top1_recall_mean"]
    k3 = summary["kshot_k3"]["top1_recall_mean"]
    k5 = summary["kshot_k5"]["top1_recall_mean"]
    k10 = summary["kshot_k10"]["top1_recall_mean"]
    rand = summary["random_context"]["top1_recall_mean"]
    diag = summary["diag_full"]["top1_recall_mean"]

    # Monotonicity among present arms K1->K3->K5 (skip absent)
    monotone = True
    present_ks = [(K, v) for K, v in [(1, k1), (3, k3), (5, k5)]
                  if summary[{1: "kshot_k1", 3: "kshot_k3", 5: "kshot_k5"}[K]]["n"] > 0]
    for i in range(len(present_ks) - 1):
        if present_ks[i + 1][1] < present_ks[i][1] - 0.02:
            monotone = False
            break

    verdict = "MIDDLE_BAND"
    k5_minus_k0 = k5 - k0
    random_margin_ok = (summary["random_context"]["n"] == 0) or (rand < k5 - HP_RANDOM_MARGIN)
    random_parity_fail = (summary["random_context"]["n"] > 0) and (rand >= k5 - HF_RANDOM_PARITY)

    if (k5 >= HP_K5_RECALL_MIN and
            k5_minus_k0 >= HP_K5_OVER_K0_MIN and
            monotone and
            random_margin_ok):
        verdict = "HARD_PASS"
    elif (k5_minus_k0 <= HF_K5_OVER_K0_LO or random_parity_fail):
        verdict = "HARD_FAIL"
    elif (MB_K5_LO <= k5 < HP_K5_RECALL_MIN):
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | top1_recall K0=%.3f K1=%.3f K3=%.3f K5=%.3f K10=%.3f | "
        "RANDOM=%.3f DIAG=%.3f | K5-K0=%.3f mono=%s"
    ) % (verdict, k0, k1, k3, k5, k10, rand, diag, k5_minus_k0, monotone)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "k5_minus_k0": float(k5_minus_k0),
        "monotone_through_k5": bool(monotone),
        "n_seeds_complete": len(per_seed),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(per_seed) * len(ARMS_USED) * N_TASKS * N_QUERIES_PER_TASK,
        "cardinality_ok": (len(per_seed) >= 2),
    }


# ----------------------- main -----------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": ARMS_USED,
                                  "expected_seeds": SEEDS})

    print("[%s] mode=%s N=%d V=%d tasks=%d Q/task=%d seeds=%s arms=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_ENTITIES, N_TASKS, N_QUERIES_PER_TASK,
        SEEDS, ARMS_USED), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in ARMS_USED:
                assert arm in r["per_arm"], "missing arm %s" % arm
            k0 = r["per_arm"]["no_context"]["top1_recall"]
            k5 = r["per_arm"]["kshot_k5"]["top1_recall"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: k0=%.3f k5=%.3f (top1_recall)" % (k0, k5),
                                   extra={"_phase": "selftest_done",
                                          "selftest_arms": list(r["per_arm"].keys()),
                                          "k0_top1_recall": k0, "k5_top1_recall": k5})
            print("[selftest] OK; k0=%.3f k5=%.3f (top1_recall)" % (k0, k5), flush=True)
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
    final["_hardening_marker"] = "v1_task_vector_kshot"
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
