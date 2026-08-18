"""cross_task_4hop_chain_v2_sum_bind -- revival of v1.

V1 (HARD_FAIL expected): HRR chain-bind length-4 collapses to noise. Standard
HRR limit: each bind multiplies noise; with chain key = e0*r0*r1*r2*r3 the
output is buried below the cleanup threshold. Even ORACLE arm collapsed (was
0.0 in v1 partials -- meaning the schema retrieval pipeline itself was broken
beyond just the no-transfer signal).

V2 FIX (per cell author 2026-06-27): replace deep-chain bind with sum-encoded
binding -- each relation is bound to its POSITION-role-vector independently,
then bundled (summed). This is the standard HRR-sum encoding for variable-
binding sequences; it survives any chain length because retrieval is
unbind-by-role rather than unbind-by-prefix-chain.

  V1:  key = e0 (*) r0 (*) r1 (*) r2 (*) r3
       Retrieval: query with key -> bundle of value; SNR collapses at depth 4.
  V2:  key = bundle( bind(e0, pos0), bind(r0, pos1), bind(r1, pos2),
                      bind(r2, pos3), bind(r3, pos4) )
       Retrieval: query with key -> bundle of value; SNR is O(1/sqrt(depth+1))
       (since each role-binding contributes one term to the sum, not a product).

Other v1 issues addressed:
- ORACLE should now be > 0.7 (was 0.0 in v1; sanity that sum-bind is
  retrievable at all). This is a hard regression sanity check.
- Cross-task transfer mechanism: shared POSITION-role vectors across domains X
  and Y (since position roles are the structural invariant; entity + relation
  vectors differ per domain). Transfer is via slot-position structure, not
  entity-vector overlap.

ARMS (4):
  ARM_NO_TRANSFER      schemas from X only; test Y cold; should be near 0
  ARM_1_SHOT_SUM_BIND  schemas from X + 1 Y example slotted; sum-bind encoding
  ARM_5_SHOT_SUM_BIND  schemas from X + 5 Y examples; sum-bind encoding
  ARM_ORACLE           schemas from full Y training set (upper bound; MUST > 0.7)

PRE-REG BANDS (LOCKED at module init; PROSPECTIVE):
  HARD_PASS:   5_SHOT_SUM_BIND       >= 0.50 AND
               5_SHOT - NO_TRANSFER  >= 0.30 AND
               ORACLE                >  0.70  (sum-bind retrievable -- regression sanity)
  MIDDLE_BAND: 5_SHOT in [0.30, 0.50) OR lift_5 in [0.15, 0.30)
  HARD_FAIL:   5_SHOT - NO_TRANSFER  <= 0.05 OR
               ORACLE                <= 0.30 (sum-bind broken -- v1 regression)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 4 arms * 3 seeds * 100 test chains = 1200
  EXPECTED_N_UNITS_SMOKE = 4 arms * 2 seeds * 30  test chains = 240
  Discriminator-survives-scale: smoke at N=8192 depth=4 (matches v1 smoke).

HARDENING (META_RULE_X / J / L1-L4).
Per-arm metrics: metrics["per_arm"] = {arm: {seed: recall}}; Fix #28.

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

ANCHOR_NAME = "cross_task_4hop_chain_v2_sum_bind"

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
HP_ORACLE_MIN = 0.70
HF_LIFT_5SHOT_LO = 0.05
HF_ORACLE_BROKEN = 0.30
DEPTH = 4

EXPECTED_ARMS = ["no_transfer", "1_shot_sum_bind", "5_shot_sum_bind", "oracle"]

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
    "seeds=%s,mode=%s,HP_5shot>=%.2f,HP_lift5>=%.2f,HP_oracle>=%.2f,"
    "expected_n=%d,hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, N_RELATIONS_PER_DOMAIN, N_ENTITIES, N_TRAIN_X,
    N_TRAIN_Y_FULL, N_TEST, DEPTH, SEEDS, RUN_MODE,
    HP_5SHOT_MIN, HP_LIFT_5SHOT, HP_ORACLE_MIN, EXPECTED_N_UNITS,
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
            "_hardening_marker": "v2_sum_bind_cross_task_4hop",
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
            "_hardening_marker": "v2_sum_bind_cross_task_4hop_import_crash",
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
    """HRR bind via circular convolution (FFT)."""
    A = np.fft.fft(a); B = np.fft.fft(b)
    return np.real(np.fft.ifft(A * B)).astype(np.float32)


def normalize(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v) + 1e-8)


def cleanup(v: np.ndarray, E: np.ndarray) -> int:
    vn = normalize(v)
    return int(np.argmax(E @ vn))


# ----------------------- SUM-BIND encoding (V2 FIX) -----------------------

def encode_chain_sum_bind(e0: int, rels: List[int], E: np.ndarray, R: np.ndarray,
                            POS: np.ndarray) -> np.ndarray:
    """V2 encoding: key = bundle( bind(e0, pos0), bind(r0, pos1), ..., bind(r_{d-1}, pos_d) ).

    POS is the SHARED position-role codebook across domains -- this is the
    structural invariant that enables cross-domain transfer.
    """
    key = hrr_bind(E[e0], POS[0])
    for i, r in enumerate(rels):
        key = key + hrr_bind(R[r], POS[i + 1])
    return normalize(key.astype(np.float32))


def make_chains(n_chains: int, depth: int, n_entities: int, n_rels: int,
                 g: np.random.Generator) -> List[Tuple[int, List[int], int]]:
    chains: List[Tuple[int, List[int], int]] = []
    for _ in range(n_chains):
        ents = [int(g.integers(0, n_entities))]
        rels: List[int] = []
        for _ in range(depth):
            r = int(g.integers(0, n_rels))
            nxt = (ents[-1] + (r + 1) * 7 + int(g.integers(0, n_entities))) % n_entities
            if nxt == ents[-1]:
                nxt = (nxt + 1) % n_entities
            ents.append(nxt)
            rels.append(r)
        chains.append((ents[0], rels, ents[-1]))
    return chains


def build_schemas_sum_bind(chains: List[Tuple[int, List[int], int]],
                             E: np.ndarray, R: np.ndarray,
                             POS: np.ndarray) -> np.ndarray:
    """Build Hebbian memory W: key (sum-bind) -> value (e_end)."""
    n_dim = E.shape[1]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for (e0, rels, e_end) in chains:
        key = encode_chain_sum_bind(e0, rels, E, R, POS)
        val = normalize(E[e_end])
        W += np.outer(key, val).astype(np.float32) / float(n_dim)
    return W


def query_schemas_sum_bind(W: np.ndarray, e0: int, rels: List[int],
                             E: np.ndarray, R: np.ndarray,
                             POS: np.ndarray) -> int:
    key = encode_chain_sum_bind(e0, rels, E, R, POS)
    out = key @ W
    return cleanup(out, E)


def merge_schemas(W_x: np.ndarray, W_y_partial: np.ndarray,
                   alpha: float = 1.0) -> np.ndarray:
    return (W_x + alpha * W_y_partial).astype(np.float32)


def evaluate_arm(W: np.ndarray, test_chains: List[Tuple[int, List[int], int]],
                  E_y: np.ndarray, R_y: np.ndarray, POS: np.ndarray) -> float:
    if not test_chains:
        return 0.0
    correct = 0
    for (e0, rels, e_end) in test_chains:
        pred = query_schemas_sum_bind(W, e0, rels, E_y, R_y, POS)
        if pred == e_end:
            correct += 1
    return correct / len(test_chains)


# ----------------------- per-seed runner -----------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    # Two domains: X and Y. Different entity and relation codebooks.
    # SHARED position-role codebook POS (cross-domain transfer mechanism).
    E_x = bipolar(N_ENTITIES, N_DIM, g)
    R_x = bipolar(N_RELATIONS_PER_DOMAIN, N_DIM, g)
    E_y = bipolar(N_ENTITIES, N_DIM, g)
    R_y = bipolar(N_RELATIONS_PER_DOMAIN, N_DIM, g)
    POS = bipolar(DEPTH + 1, N_DIM, g)  # position-roles 0..depth (shared)

    chains_x = make_chains(N_TRAIN_X, DEPTH, N_ENTITIES, N_RELATIONS_PER_DOMAIN, g)
    W_x = build_schemas_sum_bind(chains_x, E_x, R_x, POS)

    chains_y_pool = make_chains(N_TRAIN_Y_FULL + N_TEST, DEPTH, N_ENTITIES,
                                  N_RELATIONS_PER_DOMAIN, g)
    chains_y_test = chains_y_pool[-N_TEST:]
    chains_y_pool_train = chains_y_pool[:N_TRAIN_Y_FULL]

    out: Dict[str, float] = {}

    # ARM 1: NO_TRANSFER
    out["no_transfer"] = evaluate_arm(W_x, chains_y_test, E_y, R_y, POS)

    # ARM 2: 1_SHOT_SUM_BIND
    chains_y_1 = chains_y_pool_train[:1]
    W_y_1 = build_schemas_sum_bind(chains_y_1, E_y, R_y, POS)
    W_merged_1 = merge_schemas(W_x, W_y_1)
    out["1_shot_sum_bind"] = evaluate_arm(W_merged_1, chains_y_test, E_y, R_y, POS)

    # ARM 3: 5_SHOT_SUM_BIND
    chains_y_5 = chains_y_pool_train[:5]
    W_y_5 = build_schemas_sum_bind(chains_y_5, E_y, R_y, POS)
    W_merged_5 = merge_schemas(W_x, W_y_5)
    out["5_shot_sum_bind"] = evaluate_arm(W_merged_5, chains_y_test, E_y, R_y, POS)

    # ARM 4: ORACLE
    W_y_full = build_schemas_sum_bind(chains_y_pool_train, E_y, R_y, POS)
    out["oracle"] = evaluate_arm(W_y_full, chains_y_test, E_y, R_y, POS)

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
    s1 = summary["1_shot_sum_bind"]["mean"]
    s5 = summary["5_shot_sum_bind"]["mean"]
    oracle = summary["oracle"]["mean"]
    lift_5 = s5 - no_t
    lift_1 = s1 - no_t

    verdict = "MIDDLE_BAND"
    if oracle <= HF_ORACLE_BROKEN:
        verdict = "HARD_FAIL_ORACLE_BROKEN"
    elif lift_5 <= HF_LIFT_5SHOT_LO:
        verdict = "HARD_FAIL"
    elif (s5 >= HP_5SHOT_MIN and
            lift_5 >= HP_LIFT_5SHOT and
            oracle > HP_ORACLE_MIN):
        verdict = "HARD_PASS"

    verdict_msg = (
        "%s | NO=%.3f 1SHOT=%.3f 5SHOT=%.3f ORACLE=%.3f | "
        "lift_5=%.3f lift_1=%.3f n_seeds=%d"
    ) % (verdict, no_t, s1, s5, oracle, lift_5, lift_1, len(per_seed))

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "per_arm": per_arm_full, "per_arm_summary": summary,
        "lift_5shot": float(lift_5), "lift_1shot": float(lift_1),
        "oracle_mean": float(oracle),
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
    final["_hardening_marker"] = "v2_sum_bind_cross_task_4hop"
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
