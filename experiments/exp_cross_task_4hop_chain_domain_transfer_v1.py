"""cross_task_4hop_chain_domain_transfer_v1 -- Tse-Morris substrate slot-fill.

Tests: substrate trained on 4-hop chains in domain X (kinship relations) can
solve 4-hop chains in domain Y (causal relations) after 1 or 5 Y examples,
via partial-key match into existing schemas (Tse-Morris 2007 mPFC slot-fill).

ARMS (4):
  ARM_NO_TRANSFER     schemas from X only; test Y cold (chance baseline)
  ARM_1_SHOT_TRANSFER schemas from X + 1 Y example slotted in; test remaining
  ARM_5_SHOT_TRANSFER schemas from X + 5 Y examples slotted in; test remaining
  ARM_DIAG_ORACLE     schemas from full Y training set (upper bound)

PRE-REG BANDS (LOCKED at module init, PROSPECTIVE):
  HARD_PASS:  5_SHOT_recall >= 0.50 AND
              (5_SHOT - NO_TRANSFER) >= 0.30 AND
              (1_SHOT - NO_TRANSFER) >= 0.15 (monotone) AND
              5_SHOT <= ORACLE - 0.05 (non-saturated)
  MIDDLE_BAND: lifts in [0.15, 0.30] for 5-shot or non-monotone
  HARD_FAIL:  (5_SHOT - NO_TRANSFER) <= 0.05 (no transfer signal)
              OR NO_TRANSFER >= 0.30 (cold-start too easy = regime broken)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 4 arms * 3 seeds * 100 test chains = 1200
  EXPECTED_N_UNITS_SMOKE = 4 arms * 2 seeds * 30 test chains  = 240
  Discriminator-survives-scale: smoke at N=8192 depth=4 (not toy depth=2).

HARDENING (META_RULE_X / J / L1-L4): L1 STARTED, L2 per-arm, L3 outer try, L4 import sentinel.
Per-arm metrics: metrics["per_arm"] = {arm: {seed: recall}}; Fix #28 compliant.

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

ANCHOR_NAME = "cross_task_4hop_chain_domain_transfer_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

HP_5SHOT_MIN = 0.50
HP_LIFT_5SHOT = 0.30
HP_LIFT_1SHOT = 0.15
HP_NON_SATURATED_GAP = 0.05
HF_LIFT_5SHOT_LO = 0.05
HF_COLD_TOO_EASY = 0.30
DEPTH = 4

EXPECTED_ARMS = ["no_transfer", "1_shot_transfer", "5_shot_transfer", "diag_oracle"]

if SELF_TEST_MODE:
    N_DIM = 512
    N_RELATIONS_PER_DOMAIN = 4
    N_ENTITIES = 30
    N_TRAIN_X = 20
    N_TRAIN_Y_FULL = 20
    N_TEST = 10
    SEEDS = [7]
elif RUN_MODE == "smoke":
    N_DIM = 8192
    N_RELATIONS_PER_DOMAIN = 6
    N_ENTITIES = 80
    N_TRAIN_X = 200
    N_TRAIN_Y_FULL = 200
    N_TEST = 30
    SEEDS = [7, 17]
else:
    N_DIM = 8192
    N_RELATIONS_PER_DOMAIN = 8
    N_ENTITIES = 150
    N_TRAIN_X = 500
    N_TRAIN_Y_FULL = 500
    N_TEST = 100
    SEEDS = [7, 17, 23]

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * N_TEST

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,REL=%d,ENT=%d,TRAIN_X=%d,TRAIN_Y=%d,TEST=%d,DEPTH=%d,"
    "seeds=%s,mode=%s,HP_5shot>=%.2f,HP_lift5>=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, N_RELATIONS_PER_DOMAIN, N_ENTITIES, N_TRAIN_X,
    N_TRAIN_Y_FULL, N_TEST, DEPTH, SEEDS, RUN_MODE,
    HP_5SHOT_MIN, HP_LIFT_5SHOT, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v1_cross_task_4hop_chain_domain_transfer",
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
            "_hardening_marker": "v1_cross_task_4hop_chain_domain_transfer_import_crash",
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
    """HRR bind via circular convolution (using FFT)."""
    A = np.fft.fft(a); B = np.fft.fft(b)
    return np.real(np.fft.ifft(A * B)).astype(np.float32)


def hrr_unbind(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    """HRR unbind via correlation with inverse of a."""
    A = np.fft.fft(a)
    A_inv = np.conjugate(A) / (np.abs(A) ** 2 + 1e-8)
    C = np.fft.fft(c)
    return np.real(np.fft.ifft(C * A_inv)).astype(np.float32)


def cleanup(v: np.ndarray, E: np.ndarray) -> int:
    """Cosine-argmax cleanup to nearest codebook entry."""
    vn = v / (np.linalg.norm(v) + 1e-8)
    return int(np.argmax(E @ vn))


# ----------------------- task / schema construction -----------------------

def make_chains(n_chains: int, depth: int, n_entities: int,
                n_rels: int, g: np.random.Generator
                ) -> List[Tuple[int, List[int], int]]:
    """Each chain: (start_entity, relation_sequence, end_entity).
    Chain defines: e0 -r0-> e1 -r1-> ... -r_{d-1}-> e_d  (where e_{i+1} != e_i)."""
    chains: List[Tuple[int, List[int], int]] = []
    for _ in range(n_chains):
        ents = [int(g.integers(0, n_entities))]
        rels: List[int] = []
        for _ in range(depth):
            r = int(g.integers(0, n_rels))
            # Walk to a different entity per relation (deterministic step via hash)
            nxt = (ents[-1] + (r + 1) * 7 + int(g.integers(0, n_entities))) % n_entities
            if nxt == ents[-1]:
                nxt = (nxt + 1) % n_entities
            ents.append(nxt)
            rels.append(r)
        chains.append((ents[0], rels, ents[-1]))
    return chains


def build_schemas(chains: List[Tuple[int, List[int], int]],
                  E: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Cortex schema bank = bundle of (e_start bind r0 bind r1 ... bind r_{d-1}) -> e_end.
    Returns memory matrix W (n_dim, n_dim) via Hebbian outer product.
    Encoding: key = e_start bind r0 bind r1 ... bind r_{d-1}; value = e_end."""
    n_dim = E.shape[1]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for (e0, rels, e_end) in chains:
        key = E[e0].copy()
        for r in rels:
            key = hrr_bind(key, R[r])
        key = key / (np.linalg.norm(key) + 1e-8)
        val = E[e_end] / (np.linalg.norm(E[e_end]) + 1e-8)
        W += np.outer(key, val).astype(np.float32) / float(n_dim)
    return W


def query_schemas(W: np.ndarray, e_start: int, rels: List[int],
                   E: np.ndarray, R: np.ndarray) -> int:
    """Query the schema bank with key = e_start bind r0 ... bind r_{d-1}."""
    key = E[e_start].copy()
    for r in rels:
        key = hrr_bind(key, R[r])
    key_n = key / (np.linalg.norm(key) + 1e-8)
    out = key_n @ W
    return cleanup(out, E)


def merge_schemas(W_x: np.ndarray, W_y_partial: np.ndarray,
                   alpha: float = 1.0) -> np.ndarray:
    """Tse-Morris slot-fill: merge new Y examples into X schemas by additive
    Hebbian update (alpha controls how much weight Y gets vs X)."""
    return (W_x + alpha * W_y_partial).astype(np.float32)


def evaluate_arm(W: np.ndarray, test_chains: List[Tuple[int, List[int], int]],
                  E_y: np.ndarray, R_y: np.ndarray) -> float:
    """Recall: fraction of test chains where predicted e_end matches truth."""
    if not test_chains:
        return 0.0
    correct = 0
    for (e0, rels, e_end) in test_chains:
        pred = query_schemas(W, e0, rels, E_y, R_y)
        if pred == e_end:
            correct += 1
    return correct / len(test_chains)


# ----------------------- per-seed runner -----------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    # Two disjoint domains: X (kinship) and Y (causal). Different entity codebooks
    # AND different relation codebooks -- so transfer is via SCHEMA STRUCTURE.
    E_x = bipolar(N_ENTITIES, N_DIM, g)
    R_x = bipolar(N_RELATIONS_PER_DOMAIN, N_DIM, g)
    E_y = bipolar(N_ENTITIES, N_DIM, g)
    R_y = bipolar(N_RELATIONS_PER_DOMAIN, N_DIM, g)

    # Domain X training chains
    chains_x = make_chains(N_TRAIN_X, DEPTH, N_ENTITIES, N_RELATIONS_PER_DOMAIN, g)
    W_x = build_schemas(chains_x, E_x, R_x)

    # Domain Y training pool
    chains_y_pool = make_chains(N_TRAIN_Y_FULL + N_TEST, DEPTH, N_ENTITIES,
                                  N_RELATIONS_PER_DOMAIN, g)
    chains_y_test = chains_y_pool[-N_TEST:]
    chains_y_pool_train = chains_y_pool[:N_TRAIN_Y_FULL]

    out: Dict[str, float] = {}

    # ARM 1: NO_TRANSFER -- use W_x only on Y test
    # (Y test uses E_y, R_y; W_x was built on E_x, R_x; so this should be near-chance)
    out["no_transfer"] = evaluate_arm(W_x, chains_y_test, E_y, R_y)

    # ARM 2: 1_SHOT_TRANSFER -- merge 1 Y chain into schemas
    chains_y_1 = chains_y_pool_train[:1]
    W_y_1 = build_schemas(chains_y_1, E_y, R_y)
    W_merged_1 = merge_schemas(W_x, W_y_1)
    out["1_shot_transfer"] = evaluate_arm(W_merged_1, chains_y_test, E_y, R_y)

    # ARM 3: 5_SHOT_TRANSFER -- merge 5 Y chains
    chains_y_5 = chains_y_pool_train[:5]
    W_y_5 = build_schemas(chains_y_5, E_y, R_y)
    W_merged_5 = merge_schemas(W_x, W_y_5)
    out["5_shot_transfer"] = evaluate_arm(W_merged_5, chains_y_test, E_y, R_y)

    # ARM 4: DIAG_ORACLE -- schemas from full Y train set (upper bound)
    W_y_full = build_schemas(chains_y_pool_train, E_y, R_y)
    out["diag_oracle"] = evaluate_arm(W_y_full, chains_y_test, E_y, R_y)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": out,
        "n_test": N_TEST,
        "depth": DEPTH,
    }


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN",
                "verdict_msg": "no per-seed partials found",
                "summary": "no per-seed partials found",
                "per_arm": {}}
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, float]] = {arm: {} for arm in EXPECTED_ARMS}
    for arm in EXPECTED_ARMS:
        vals: List[float] = []
        for s_key, body in per_seed.items():
            pa = body.get("per_arm", {})
            if arm in pa:
                vals.append(float(pa[arm]))
                per_arm_full[arm][s_key] = float(pa[arm])
        if vals:
            m = float(np.mean(vals))
            sd = float(np.std(vals))
            summary[arm] = {"mean": m, "std": sd,
                            "cv": float(sd / m) if m > 1e-6 else 0.0,
                            "n": len(vals)}
        else:
            summary[arm] = {"mean": 0.0, "std": 0.0, "cv": 0.0, "n": 0}

    no_t = summary["no_transfer"]["mean"]
    s1 = summary["1_shot_transfer"]["mean"]
    s5 = summary["5_shot_transfer"]["mean"]
    oracle = summary["diag_oracle"]["mean"]
    lift_5 = s5 - no_t
    lift_1 = s1 - no_t

    verdict = "MIDDLE_BAND"
    if (s5 >= HP_5SHOT_MIN and
            lift_5 >= HP_LIFT_5SHOT and
            lift_1 >= HP_LIFT_1SHOT and
            s5 <= oracle - HP_NON_SATURATED_GAP):
        verdict = "HARD_PASS"
    elif (lift_5 <= HF_LIFT_5SHOT_LO):
        verdict = "HARD_FAIL"
    elif (no_t >= HF_COLD_TOO_EASY):
        verdict = "HARD_FAIL_COLD_TOO_EASY"

    verdict_msg = (
        "%s | NO_TRANSFER=%.3f 1SHOT=%.3f 5SHOT=%.3f ORACLE=%.3f | "
        "lift_5=%.3f lift_1=%.3f n_seeds=%d"
    ) % (verdict, no_t, s1, s5, oracle, lift_5, lift_1, len(per_seed))

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "per_arm": per_arm_full, "per_arm_summary": summary,
        "lift_5shot": float(lift_5), "lift_1shot": float(lift_1),
        "n_seeds_complete": len(per_seed),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(per_seed) * len(EXPECTED_ARMS) * N_TEST,
        "cardinality_ok": (len(per_seed) >= 2),
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS})

    print("[%s] mode=%s N=%d depth=%d test=%d seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, DEPTH, N_TEST, SEEDS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm structure verified",
                                   extra={"_phase": "selftest_done",
                                          "selftest_arms": r["per_arm"]})
            print("[selftest] OK; arms=%s" % r["per_arm"], flush=True)
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
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining),
          flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running",
                                      "_current_seed": seed})
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
    final["_hardening_marker"] = "v1_cross_task_4hop_chain_domain_transfer"
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
