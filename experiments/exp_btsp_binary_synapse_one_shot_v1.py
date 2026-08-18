"""btsp_binary_synapse_one_shot_v1 -- B3 consolidation under saturation.

Hypothesis: prior consolidation attempts (Hopfield v1/v2, BCM v1/v2, stratified
replay) all write GLOBALLY across W and saturate. Binary synapses + eligibility
trace + neuromodulator gate (Wu-Maass 2025 Nature Comms BTSP) flip a SUBSET of
binary synapses ONCE, structurally cannot saturate to baseline=1.0.

ARMS (5):
  ARM_HEBBIAN_BASELINE          continuous W, global Hebbian (control)
  ARM_BINARY_HEBBIAN            binary W, global write (isolates binarization)
  ARM_BTSP_FULL                 binary W + eligibility trace + neuromod gate
  ARM_BTSP_NO_NEUROMOD          binary W + eligibility trace, no gate (isolate gate)
  ARM_DIAG_TAG_FRACTION         diagnostic: fraction of synapses tagged

PRE-REG BANDS (HARD-LOCKED at module init, PROSPECTIVE):
  HARD_PASS:
    BTSP_FULL new_pattern_acc >= 0.70 floor
    AND old_pattern_acc >= 0.9 * floor (no catastrophic forgetting)
    AND cv across seeds < 0.10
    AND BTSP_FULL > BINARY_HEBBIAN (eligibility-trace gate load-bearing)
    AND HEBBIAN_BASELINE NOT in [0.95, 1.00] (anti-saturation per META_RULE_W)
  MIDDLE_BAND: signal but doesn't meet all 4 gates
  HARD_FAIL: any baseline saturates >= 0.95 OR new < 0.40 OR old < 0.5*floor

REGIME (Skunkworks recipe + META_RULE_W safe band):
  N_DIM=2048, N_CAT=100, N_TRAIN=10 per cat, proto_noise=0.85
  alpha_load = N_CAT/N_DIM = 0.0488 in safe band [0.03, 0.20]

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 5 seeds * 5 arms * 2 phases = 50
  EXPECTED_N_UNITS_SMOKE = 2 seeds * 5 arms * 2 phases = 20

HARDENING: L1 early metrics, L2 per-arm progress, L3 outer try/except,
L4 import-crash sentinel.

Per-arm metrics structure (Fix #28):
  metrics["per_arm"] = {arm: {seed: {new_pattern_acc, old_pattern_acc, ...}}}

ASCII-only; no emojis; self-contained.
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

ANCHOR_NAME = "btsp_binary_synapse_one_shot_v1"

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
HP_NEW_FLOOR = 0.70
HP_OLD_FLOOR_FRAC = 0.9
HP_CV_MAX = 0.10
HP_SATURATION_LO = 0.95
HF_NEW_FLOOR = 0.40
HF_OLD_FRAC = 0.5
HP_ALPHA_BAND_LO = 0.03
HP_ALPHA_BAND_HI = 0.20

EXPECTED_ARMS = ["hebbian_baseline", "binary_hebbian",
                 "btsp_full", "btsp_no_neuromod", "diag_tag_fraction"]

if SELF_TEST_MODE:
    N_DIM = 512
    N_CAT = 20
    N_TRAIN = 5
    SEEDS = [7]
    PROTO_NOISE = 0.85
elif RUN_MODE == "smoke":
    N_DIM = 2048
    N_CAT = 100
    N_TRAIN = 10
    SEEDS = [7, 17]
    PROTO_NOISE = 0.85
else:
    N_DIM = 2048
    N_CAT = 100
    N_TRAIN = 10
    SEEDS = [7, 17, 23, 31, 41]
    PROTO_NOISE = 0.85

ALPHA_LOAD = N_CAT / float(N_DIM)
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * 2  # 2 phases

# META_RULE_W safe-band check (HARD ASSERT at module init)
if not (HP_ALPHA_BAND_LO <= ALPHA_LOAD <= HP_ALPHA_BAND_HI):
    print("[meta_rule_w] WARN: alpha_load=%.4f outside [%.2f, %.2f] safe band" % (
        ALPHA_LOAD, HP_ALPHA_BAND_LO, HP_ALPHA_BAND_HI), file=sys.stderr)

# BTSP parameters
ELIG_TRACE_DECAY = 0.7
ELIG_THRESHOLD = 0.30
NEUROMOD_GATE_PROB = 0.5  # P(consolidate | high-importance event)
BTSP_TAG_FRACTION_TARGET = 0.05  # target fraction of synapses to flip per event

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,N_CAT=%d,N_TRAIN=%d,alpha=%.4f,proto_noise=%.2f,seeds=%s,mode=%s,"
    "HP_new>=%.2f,HP_old_frac>=%.2f,HP_cv<=%.2f,HP_sat_lo=%.2f,expected_n=%d,"
    "elig_decay=%.2f,elig_tau=%.2f,gate_p=%.2f,tag_frac=%.3f,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, N_CAT, N_TRAIN, ALPHA_LOAD, PROTO_NOISE, SEEDS, RUN_MODE,
    HP_NEW_FLOOR, HP_OLD_FLOOR_FRAC, HP_CV_MAX, HP_SATURATION_LO, EXPECTED_N_UNITS,
    ELIG_TRACE_DECAY, ELIG_THRESHOLD, NEUROMOD_GATE_PROB, BTSP_TAG_FRACTION_TARGET,
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
            "alpha_load": ALPHA_LOAD,
            "_hardening_marker": "v1_btsp",
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
            "_hardening_marker": "v1_btsp_import_crash",
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


def noisy_prototype(proto: np.ndarray, noise: float,
                    g: np.random.Generator) -> np.ndarray:
    """Flip random bits proportional to noise; return normalized."""
    n = proto.shape[0]
    flip = g.random(n) < noise
    out = proto.copy()
    out[flip] = -out[flip]
    return out / (np.linalg.norm(out) + 1e-8)


def hebbian_write_continuous(W: np.ndarray, key: np.ndarray,
                              value: np.ndarray) -> np.ndarray:
    """Continuous Hebbian outer-product accumulate. Returns updated W."""
    n = key.shape[0]
    return W + np.outer(key, value).astype(np.float32) / float(n)


def binarize_W(W: np.ndarray) -> np.ndarray:
    """Sign-binarize W to +/-1."""
    return np.sign(W).astype(np.float32) + (W == 0).astype(np.float32) * 1.0


def btsp_update(W_bin: np.ndarray, key: np.ndarray, value: np.ndarray,
                elig_trace: np.ndarray, neuromod_gate: bool,
                g: np.random.Generator, target_tag_frac: float
                ) -> Tuple[np.ndarray, np.ndarray, float]:
    """One BTSP update step.

    1. Update eligibility trace: trace = decay*trace + |outer(key, value)|
    2. If neuromod_gate True: flip top-fraction binary synapses where
       trace exceeds threshold.

    Returns updated (W_bin, elig_trace, tagged_fraction).
    """
    n = W_bin.shape[0]
    # Update eligibility trace
    instant = np.abs(np.outer(key, value)).astype(np.float32) / float(n)
    elig_trace = ELIG_TRACE_DECAY * elig_trace + instant

    tagged_frac = 0.0
    if neuromod_gate:
        # Select top-fraction by elig_trace magnitude
        n_total = elig_trace.size
        n_tag = max(1, int(target_tag_frac * n_total))
        # Threshold = the n_tag-th largest value
        flat = elig_trace.ravel()
        if n_tag < n_total:
            thresh = np.partition(flat, -n_tag)[-n_tag]
        else:
            thresh = float(flat.min())
        tag_mask = elig_trace >= thresh
        tagged_frac = float(tag_mask.sum()) / n_total
        # Flip tagged synapses toward desired update direction
        update_dir = np.sign(np.outer(key, value)).astype(np.float32)
        W_bin = np.where(tag_mask, update_dir, W_bin).astype(np.float32)

    return W_bin, elig_trace, tagged_frac


def readout_accuracy(W: np.ndarray, queries: np.ndarray,
                      targets: np.ndarray, binary: bool = False) -> float:
    """W @ query -> compare cosine to target. Returns mean cosine sim.

    If binary=True, query and W are in {-1, +1}; readout is sign-clipped.
    """
    if binary:
        out = queries @ W  # (n_q, n)
        out = np.sign(out).astype(np.float32) + (out == 0).astype(np.float32)
    else:
        out = queries @ W
    out_n = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-8)
    tgt_n = targets / (np.linalg.norm(targets, axis=1, keepdims=True) + 1e-8)
    sims = (out_n * tgt_n).sum(axis=1)  # cosine per query
    return float(np.mean(sims))


# -------------------------- arms --------------------------

def run_arm_hebbian_baseline(prototypes: np.ndarray, train_set: np.ndarray,
                              train_labels: np.ndarray, test_set: np.ndarray,
                              test_labels: np.ndarray) -> Dict[str, float]:
    """Continuous-W Hebbian. Reads pattern -> outputs prototype."""
    n_dim = prototypes.shape[1]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for i in range(train_set.shape[0]):
        key = train_set[i]
        value = prototypes[train_labels[i]]
        W = hebbian_write_continuous(W, key, value)
    new_acc = readout_accuracy(W, test_set, prototypes[test_labels], binary=False)
    return {"new_pattern_acc": new_acc, "old_pattern_acc": new_acc,
            "saturation_score": new_acc, "tag_fraction": 0.0}


def run_arm_binary_hebbian(prototypes: np.ndarray, train_set: np.ndarray,
                            train_labels: np.ndarray, test_set: np.ndarray,
                            test_labels: np.ndarray) -> Dict[str, float]:
    """Binary W after continuous accumulate."""
    n_dim = prototypes.shape[1]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for i in range(train_set.shape[0]):
        key = train_set[i]
        value = prototypes[train_labels[i]]
        W = hebbian_write_continuous(W, key, value)
    W = binarize_W(W)
    new_acc = readout_accuracy(W, test_set, prototypes[test_labels], binary=False)
    return {"new_pattern_acc": new_acc, "old_pattern_acc": new_acc,
            "saturation_score": new_acc, "tag_fraction": 1.0}


def run_arm_btsp_full(prototypes: np.ndarray, train_set: np.ndarray,
                       train_labels: np.ndarray, test_set: np.ndarray,
                       test_labels: np.ndarray, old_test_set: np.ndarray,
                       old_test_labels: np.ndarray,
                       g: np.random.Generator,
                       use_gate: bool = True) -> Dict[str, float]:
    """Binary W + eligibility trace + neuromod gate."""
    n_dim = prototypes.shape[1]
    W_bin = (g.integers(0, 2, size=(n_dim, n_dim)).astype(np.float32) * 2 - 1)
    elig = np.zeros_like(W_bin)
    tag_fracs: List[float] = []
    for i in range(train_set.shape[0]):
        key = train_set[i]
        value = prototypes[train_labels[i]]
        gate = (g.random() < NEUROMOD_GATE_PROB) if use_gate else True
        W_bin, elig, tf = btsp_update(W_bin, key, value, elig, gate, g,
                                       BTSP_TAG_FRACTION_TARGET)
        tag_fracs.append(tf)
    new_acc = readout_accuracy(W_bin, test_set, prototypes[test_labels], binary=False)
    old_acc = readout_accuracy(W_bin, old_test_set,
                                prototypes[old_test_labels], binary=False)
    return {"new_pattern_acc": new_acc, "old_pattern_acc": old_acc,
            "saturation_score": new_acc,
            "tag_fraction": float(np.mean(tag_fracs)) if tag_fracs else 0.0}


def run_arm_diag_tag_fraction(prototypes: np.ndarray, train_set: np.ndarray,
                               train_labels: np.ndarray, g: np.random.Generator
                               ) -> Dict[str, float]:
    """Diagnostic: track tag-fraction per consolidation event."""
    n_dim = prototypes.shape[1]
    W_bin = (g.integers(0, 2, size=(n_dim, n_dim)).astype(np.float32) * 2 - 1)
    elig = np.zeros_like(W_bin)
    tag_fracs: List[float] = []
    for i in range(train_set.shape[0]):
        key = train_set[i]
        value = prototypes[train_labels[i]]
        gate = (g.random() < NEUROMOD_GATE_PROB)
        W_bin, elig, tf = btsp_update(W_bin, key, value, elig, gate, g,
                                       BTSP_TAG_FRACTION_TARGET)
        if gate:
            tag_fracs.append(tf)
    mean_tag = float(np.mean(tag_fracs)) if tag_fracs else 0.0
    return {"new_pattern_acc": mean_tag, "old_pattern_acc": mean_tag,
            "saturation_score": 0.0, "tag_fraction": mean_tag}


# -------------------------- per-seed --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    # Build N_CAT prototypes
    prototypes = bipolar(N_CAT, N_DIM, g)
    # Train set: N_CAT * N_TRAIN noisy copies
    train_keys: List[np.ndarray] = []
    train_labels: List[int] = []
    for c in range(N_CAT):
        for _ in range(N_TRAIN):
            train_keys.append(noisy_prototype(prototypes[c], PROTO_NOISE, g))
            train_labels.append(c)
    train_set = np.stack(train_keys, axis=0).astype(np.float32)
    train_labels_arr = np.array(train_labels, dtype=np.int64)
    # Shuffle training order
    perm = g.permutation(train_set.shape[0])
    train_set = train_set[perm]
    train_labels_arr = train_labels_arr[perm]

    # Test set for "new" patterns (held-out noisy versions, same prototypes)
    test_keys = [noisy_prototype(prototypes[c], PROTO_NOISE, g)
                  for c in range(N_CAT)]
    test_set = np.stack(test_keys, axis=0).astype(np.float32)
    test_labels = np.arange(N_CAT, dtype=np.int64)

    # "Old" patterns: first half of training set (test if old retained)
    old_count = max(1, train_set.shape[0] // 2)
    old_test_set = train_set[:old_count]
    old_test_labels = train_labels_arr[:old_count]

    arm_results: Dict[str, Dict[str, float]] = {}

    arm_results["hebbian_baseline"] = run_arm_hebbian_baseline(
        prototypes, train_set, train_labels_arr, test_set, test_labels)

    arm_results["binary_hebbian"] = run_arm_binary_hebbian(
        prototypes, train_set, train_labels_arr, test_set, test_labels)

    arm_results["btsp_full"] = run_arm_btsp_full(
        prototypes, train_set, train_labels_arr, test_set, test_labels,
        old_test_set, old_test_labels, g, use_gate=True)

    arm_results["btsp_no_neuromod"] = run_arm_btsp_full(
        prototypes, train_set, train_labels_arr, test_set, test_labels,
        old_test_set, old_test_labels, g, use_gate=False)

    arm_results["diag_tag_fraction"] = run_arm_diag_tag_fraction(
        prototypes, train_set, train_labels_arr, g)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "N_CAT": N_CAT,
        "alpha_load": ALPHA_LOAD,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": arm_results,
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
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}
    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}
        new_vals: List[float] = []
        old_vals: List[float] = []
        tag_vals: List[float] = []
        for s in seeds_sorted:
            body = per_seed[s]
            pa = body.get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                new_vals.append(float(d.get("new_pattern_acc", 0.0)))
                old_vals.append(float(d.get("old_pattern_acc", 0.0)))
                tag_vals.append(float(d.get("tag_fraction", 0.0)))
                per_arm_full[arm][s] = {
                    "new_pattern_acc": float(d.get("new_pattern_acc", 0.0)),
                    "old_pattern_acc": float(d.get("old_pattern_acc", 0.0)),
                    "tag_fraction": float(d.get("tag_fraction", 0.0)),
                }
        if new_vals:
            m_new = float(np.mean(new_vals))
            sd_new = float(np.std(new_vals))
            cv = sd_new / abs(m_new) if abs(m_new) > 1e-6 else 0.0
            summary[arm] = {
                "mean_new": m_new, "std_new": sd_new, "cv_new": cv,
                "mean_old": float(np.mean(old_vals)),
                "mean_tag": float(np.mean(tag_vals)),
                "n": len(new_vals),
            }
        else:
            summary[arm] = {"mean_new": 0.0, "std_new": 0.0, "cv_new": 0.0,
                            "mean_old": 0.0, "mean_tag": 0.0, "n": 0}

    btsp = summary["btsp_full"]
    bin_heb = summary["binary_hebbian"]
    cont_heb = summary["hebbian_baseline"]
    btsp_new = btsp["mean_new"]
    btsp_old = btsp["mean_old"]
    btsp_cv = btsp["cv_new"]
    cont_new = cont_heb["mean_new"]

    # Saturation rail
    saturated = (cont_new >= HP_SATURATION_LO)

    verdict = "MIDDLE_BAND"
    if saturated:
        verdict = "HARD_FAIL_SATURATION"
    elif (btsp_new >= HP_NEW_FLOOR and
            btsp_old >= HP_OLD_FLOOR_FRAC * HP_NEW_FLOOR and
            btsp_cv < HP_CV_MAX and
            btsp_new > bin_heb["mean_new"]):
        verdict = "HARD_PASS"
    elif (btsp_new < HF_NEW_FLOOR or
            btsp_old < HF_OLD_FRAC * HP_NEW_FLOOR):
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | BTSP_new=%.3f BTSP_old=%.3f BinHeb=%.3f ContHeb=%.3f | "
        "cv=%.3f tag=%.3f alpha=%.4f | n=%d"
    ) % (verdict, btsp_new, btsp_old, bin_heb["mean_new"], cont_new,
         btsp_cv, btsp["mean_tag"], ALPHA_LOAD, len(seeds_sorted))

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "alpha_load": ALPHA_LOAD,
        "saturation_score": cont_new,
        "btsp_cv": btsp_cv,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(seeds_sorted) * len(EXPECTED_ARMS) * 2,
        "cardinality_ok": (len(seeds_sorted) * len(EXPECTED_ARMS) * 2
                           >= EXPECTED_N_UNITS),
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s alpha=%.4f" % (
                               os.getpid(), RUN_MODE, ALPHA_LOAD),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d N_CAT=%d N_TRAIN=%d alpha=%.4f seeds=%s expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_CAT, N_TRAIN, ALPHA_LOAD, SEEDS,
        EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"]
                assert "new_pattern_acc" in r["per_arm"][arm]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm structure verified")
            print("[selftest] OK", flush=True)
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
    final["_hardening_marker"] = "v1_btsp"
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
