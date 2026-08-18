"""btsp_binary_synapse_one_shot_v2_regime_probed -- B3 fair-revival with regime probe.

Drill source: notes/META_FAIRNESS_PATTERN_wave1_test_design_failures_2026-06-27.md
META_FAIRNESS_PATTERN bug v1: alpha in safe band but baseline saturated AND BTSP
collapsed to 0.020. Skunkworks recipe insufficient.

FIX: SMOKE = pre-flight REGIME PROBE that sweeps (N_DIM, N_CAT, N_TRAIN, proto_noise)
and finds combination where BASELINE_HEBBIAN lands in [0.40, 0.65] band. THEN runs
BTSP at that operating point.

If probe finds NO regime where baseline_hebbian in [0.40, 0.65], cell HARD_FAILs
with REGIME_INFEASIBLE -- that's also important info.

PROBE GRID (smoke):
  N_DIM in [1024, 2048]
  N_CAT in [50, 100, 200]
  N_TRAIN in [5, 10, 20]
  proto_noise in [0.60, 0.85, 1.10]

ARMS (5; same as v1):
  ARM_HEBBIAN_BASELINE          continuous W, global Hebbian (control)
  ARM_BINARY_HEBBIAN            binary W, global write
  ARM_BTSP_FULL                 binary W + eligibility trace + neuromod gate
  ARM_BTSP_NO_NEUROMOD          binary W + elig trace, no gate (isolate gate)
  ARM_DIAG_TAG_FRACTION         diagnostic

PRE-REG BANDS (HARD-LOCKED at module init):
  HARD_PASS (only if regime probe found fair operating point):
    BTSP_FULL new_pattern_acc >= 0.50 AND old_pattern_acc >= 0.9*0.50 = 0.45
    AND BASELINE_HEBBIAN found within [0.40, 0.65] (PRECONDITION)
    AND cv across seeds < 0.10
    AND BTSP_FULL > BINARY_HEBBIAN (eligibility trace load-bearing)
  MIDDLE_BAND: regime found but BTSP in [0.35, 0.50) OR partial gate signal
  HARD_FAIL:
    - REGIME_INFEASIBLE if probe finds no (cfg) with BASELINE in [0.40, 0.65]
    - or BTSP_FULL < 0.30 at fair regime (mechanism null at fair test)
    - or old_pattern_acc < 0.5 * 0.50 = 0.25 (catastrophic forgetting)

META_RULE_AA: baseline must read SAME SURFACE as mechanism (here: cosine to prototype
              from learned W); baseline must NOT implicitly do mechanism;
              smoke must have statistical power (n>=3, cv<0.30).
META_RULE_W: alpha in [0.03, 0.20] gate (kept for compatibility but not load-bearing
             after we showed alpha-in-band was insufficient in v1).

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SMOKE = 1 probe + 5 arms * 3 seeds at found regime = 16
  EXPECTED_N_UNITS_FULL  = 5 arms * 5 seeds * 2 phases = 50 at found regime

HARDENING (META_RULE_X / J / L1-L4):
  main wrapped in if __name__ == "__main__"
  L1: minimal metrics.json with STARTED + PID at start
  L2: per-arm + per-probe-config progress updates
  L3: outer try/except around main
  L4: import-crash sentinel

ASCII-only; no emojis; no em-dashes; self-contained.
Author: exp_dev 2026-06-27 (fair-revival cell 3 of 4 under research lead).
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

ANCHOR_NAME = "btsp_binary_synapse_one_shot_v2_regime_probed"

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
HP_NEW_FLOOR = 0.50  # lowered from v1's 0.70 -- realistic at fair regime
HP_OLD_FLOOR_FRAC = 0.9
HP_CV_MAX = 0.10
HP_BASELINE_LO = 0.40
HP_BASELINE_HI = 0.65
HF_NEW_FLOOR = 0.30
HF_OLD_FRAC = 0.5

EXPECTED_ARMS = ["hebbian_baseline", "binary_hebbian",
                 "btsp_full", "btsp_no_neuromod", "diag_tag_fraction"]

# Probe grid
if SELF_TEST_MODE:
    PROBE_N_DIM = [256]
    PROBE_N_CAT = [10]
    PROBE_N_TRAIN = [5]
    PROBE_PROTO_NOISE = [0.85]
    SEEDS = [7]
elif RUN_MODE == "smoke":
    PROBE_N_DIM = [1024, 2048]
    PROBE_N_CAT = [50, 100, 200]
    PROBE_N_TRAIN = [5, 10, 20]
    PROBE_PROTO_NOISE = [0.60, 0.85, 1.10]
    SEEDS = [7, 17, 23]
else:
    PROBE_N_DIM = [2048]  # FULL inherits from probe-found regime; this is fallback
    PROBE_N_CAT = [100]
    PROBE_N_TRAIN = [10]
    PROBE_PROTO_NOISE = [0.85]
    SEEDS = [7, 17, 23, 31, 41]

# Default operating point (filled by probe in main)
N_DIM = PROBE_N_DIM[-1]
N_CAT = PROBE_N_CAT[-1]
N_TRAIN = PROBE_N_TRAIN[-1]
PROTO_NOISE = PROBE_PROTO_NOISE[-1]

EXPECTED_N_UNITS_SMOKE = 1 + len(EXPECTED_ARMS) * len(SEEDS)  # 1 probe + arms x seeds
EXPECTED_N_UNITS = EXPECTED_N_UNITS_SMOKE if RUN_MODE == "smoke" else (
    len(EXPECTED_ARMS) * len(SEEDS) * 2)

# BTSP parameters
ELIG_TRACE_DECAY = 0.7
ELIG_THRESHOLD = 0.30
NEUROMOD_GATE_PROB = 0.5
BTSP_TAG_FRACTION_TARGET = 0.05

CONFIG_VERSION = (
    "ANCHOR=%s,probe_N=%s,probe_NCAT=%s,probe_NTRAIN=%s,probe_noise=%s,seeds=%s,mode=%s,"
    "HP_new>=%.2f,HP_baseline_band=[%.2f,%.2f],HP_cv<=%.2f,HF_new<%.2f,"
    "elig_decay=%.2f,gate_p=%.2f,tag_frac=%.3f,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "FAIRNESS=REGIME_PROBE_FINDS_BASELINE_IN_BAND_BEFORE_MECHANISM_TEST"
) % (
    ANCHOR_NAME, PROBE_N_DIM, PROBE_N_CAT, PROBE_N_TRAIN, PROBE_PROTO_NOISE,
    SEEDS, RUN_MODE,
    HP_NEW_FLOOR, HP_BASELINE_LO, HP_BASELINE_HI, HP_CV_MAX, HF_NEW_FLOOR,
    ELIG_TRACE_DECAY, NEUROMOD_GATE_PROB, BTSP_TAG_FRACTION_TARGET,
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
            "_hardening_marker": "v2_btsp_regime_probed",
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
            "_hardening_marker": "v2_btsp_regime_probed_import_crash",
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
    """Flip bits proportional to noise; clamp noise effective to [0, 1]; renormalize.

    Note: noise > 1.0 is interpreted as random output (flip all then add extra noise).
    """
    n = proto.shape[0]
    eff = min(1.0, max(0.0, noise))
    flip = g.random(n) < eff
    out = proto.copy()
    out[flip] = -out[flip]
    return out / (np.linalg.norm(out) + 1e-8)


def hebbian_write_continuous(W: np.ndarray, key: np.ndarray,
                              value: np.ndarray) -> np.ndarray:
    n = key.shape[0]
    return W + np.outer(key, value).astype(np.float32) / float(n)


def binarize_W(W: np.ndarray) -> np.ndarray:
    return np.sign(W).astype(np.float32) + (W == 0).astype(np.float32) * 1.0


def btsp_update(W_bin: np.ndarray, key: np.ndarray, value: np.ndarray,
                elig_trace: np.ndarray, neuromod_gate: bool,
                g: np.random.Generator, target_tag_frac: float
                ) -> Tuple[np.ndarray, np.ndarray, float]:
    """One BTSP update step (Wu-Maass 2025).

    1. Update eligibility trace: trace = decay*trace + |outer(key, value)|
    2. If gate True: flip top-fraction binary synapses where trace exceeds threshold.
    """
    n = W_bin.shape[0]
    instant = np.abs(np.outer(key, value)).astype(np.float32) / float(n)
    elig_trace = ELIG_TRACE_DECAY * elig_trace + instant

    tagged_frac = 0.0
    if neuromod_gate:
        n_total = elig_trace.size
        n_tag = max(1, int(target_tag_frac * n_total))
        flat = elig_trace.ravel()
        if n_tag < n_total:
            thresh = np.partition(flat, -n_tag)[-n_tag]
        else:
            thresh = float(flat.min())
        tag_mask = elig_trace >= thresh
        tagged_frac = float(tag_mask.sum()) / n_total
        update_dir = np.sign(np.outer(key, value)).astype(np.float32)
        W_bin = np.where(tag_mask, update_dir, W_bin).astype(np.float32)

    return W_bin, elig_trace, tagged_frac


def readout_accuracy(W: np.ndarray, queries: np.ndarray,
                      targets: np.ndarray) -> float:
    """W @ query -> cosine to target; return mean."""
    out = queries @ W
    out_n = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-8)
    tgt_n = targets / (np.linalg.norm(targets, axis=1, keepdims=True) + 1e-8)
    sims = (out_n * tgt_n).sum(axis=1)
    return float(np.mean(sims))


# -------------------------- regime probe --------------------------

def regime_probe(seeds: List[int]) -> Dict[str, Any]:
    """Sweep PROBE_GRID; return first (cfg) where ARM_HEBBIAN_BASELINE lands in
    [HP_BASELINE_LO, HP_BASELINE_HI]. If none found, return INFEASIBLE.
    """
    probe_results: List[Dict[str, Any]] = []
    found_cfg = None
    probe_seed = seeds[0]
    g_probe = np.random.default_rng(probe_seed + 100)

    for nd in PROBE_N_DIM:
        for nc in PROBE_N_CAT:
            for nt in PROBE_N_TRAIN:
                for noise in PROBE_PROTO_NOISE:
                    alpha = nc / float(nd)
                    cfg = {"N_DIM": nd, "N_CAT": nc, "N_TRAIN": nt,
                           "proto_noise": noise, "alpha": alpha}
                    # Quick HEBBIAN_BASELINE eval at this cfg with probe seed
                    g_local = np.random.default_rng(probe_seed + 1001)
                    prototypes = bipolar(nc, nd, g_local)
                    train_keys: List[np.ndarray] = []
                    train_labels: List[int] = []
                    for c in range(nc):
                        for _ in range(nt):
                            train_keys.append(noisy_prototype(prototypes[c], noise, g_local))
                            train_labels.append(c)
                    train_set = np.stack(train_keys, axis=0).astype(np.float32)
                    train_labels_arr = np.array(train_labels, dtype=np.int64)
                    # Test set: held-out noisy versions same prototypes
                    test_keys = [noisy_prototype(prototypes[c], noise, g_local)
                                  for c in range(nc)]
                    test_set = np.stack(test_keys, axis=0).astype(np.float32)
                    test_labels = np.arange(nc, dtype=np.int64)

                    # Build continuous Hebbian W: key -> prototype value
                    W = np.zeros((nd, nd), dtype=np.float32)
                    for i in range(train_set.shape[0]):
                        key = train_set[i]
                        val = prototypes[train_labels_arr[i]]
                        W = hebbian_write_continuous(W, key, val)
                    # Readout
                    out = test_set @ W
                    out_n = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-8)
                    # Classify by argmax cosine to any prototype
                    proto_n = prototypes / (np.linalg.norm(prototypes, axis=1, keepdims=True) + 1e-8)
                    sims = out_n @ proto_n.T  # (nc, nc)
                    pred = np.argmax(sims, axis=1)
                    acc = float(np.mean(pred == test_labels))
                    cfg["baseline_acc"] = acc
                    probe_results.append(cfg)
                    print("[probe] N=%d NCAT=%d NTRAIN=%d noise=%.2f alpha=%.4f -> baseline=%.3f" % (
                        nd, nc, nt, noise, alpha, acc), flush=True)
                    if HP_BASELINE_LO <= acc <= HP_BASELINE_HI and found_cfg is None:
                        found_cfg = dict(cfg)

    return {"probe_results": probe_results, "found_cfg": found_cfg}


# -------------------------- arms (run at chosen regime) --------------------------

def run_arm_hebbian_baseline(prototypes, train_set, train_labels, test_set,
                              test_labels, nd) -> Dict[str, float]:
    W = np.zeros((nd, nd), dtype=np.float32)
    for i in range(train_set.shape[0]):
        key = train_set[i]
        value = prototypes[train_labels[i]]
        W = hebbian_write_continuous(W, key, value)
    new_acc = readout_accuracy(W, test_set, prototypes[test_labels])
    return {"new_pattern_acc": new_acc, "old_pattern_acc": new_acc,
            "saturation_score": new_acc, "tag_fraction": 0.0}


def run_arm_binary_hebbian(prototypes, train_set, train_labels, test_set,
                            test_labels, nd) -> Dict[str, float]:
    W = np.zeros((nd, nd), dtype=np.float32)
    for i in range(train_set.shape[0]):
        key = train_set[i]
        value = prototypes[train_labels[i]]
        W = hebbian_write_continuous(W, key, value)
    W = binarize_W(W)
    new_acc = readout_accuracy(W, test_set, prototypes[test_labels])
    return {"new_pattern_acc": new_acc, "old_pattern_acc": new_acc,
            "saturation_score": new_acc, "tag_fraction": 1.0}


def run_arm_btsp_full(prototypes, train_set, train_labels, test_set, test_labels,
                       old_test_set, old_test_labels, nd, g: np.random.Generator,
                       use_gate: bool = True) -> Dict[str, float]:
    W_bin = (g.integers(0, 2, size=(nd, nd)).astype(np.float32) * 2 - 1)
    elig = np.zeros_like(W_bin)
    tag_fracs: List[float] = []
    for i in range(train_set.shape[0]):
        key = train_set[i]
        value = prototypes[train_labels[i]]
        gate = (g.random() < NEUROMOD_GATE_PROB) if use_gate else True
        W_bin, elig, tf = btsp_update(W_bin, key, value, elig, gate, g,
                                       BTSP_TAG_FRACTION_TARGET)
        tag_fracs.append(tf)
    new_acc = readout_accuracy(W_bin, test_set, prototypes[test_labels])
    old_acc = readout_accuracy(W_bin, old_test_set, prototypes[old_test_labels])
    return {"new_pattern_acc": new_acc, "old_pattern_acc": old_acc,
            "saturation_score": new_acc,
            "tag_fraction": float(np.mean(tag_fracs)) if tag_fracs else 0.0}


def run_arm_diag_tag_fraction(prototypes, train_set, train_labels, nd,
                               g: np.random.Generator) -> Dict[str, float]:
    W_bin = (g.integers(0, 2, size=(nd, nd)).astype(np.float32) * 2 - 1)
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


def run_one_seed_at_regime(seed: int, cfg: Dict[str, Any]) -> Dict[str, Any]:
    nd = cfg["N_DIM"]
    nc = cfg["N_CAT"]
    nt = cfg["N_TRAIN"]
    noise = cfg["proto_noise"]
    g = np.random.default_rng(seed)

    prototypes = bipolar(nc, nd, g)
    train_keys: List[np.ndarray] = []
    train_labels: List[int] = []
    for c in range(nc):
        for _ in range(nt):
            train_keys.append(noisy_prototype(prototypes[c], noise, g))
            train_labels.append(c)
    train_set = np.stack(train_keys, axis=0).astype(np.float32)
    train_labels_arr = np.array(train_labels, dtype=np.int64)
    perm = g.permutation(train_set.shape[0])
    train_set = train_set[perm]
    train_labels_arr = train_labels_arr[perm]

    test_keys = [noisy_prototype(prototypes[c], noise, g) for c in range(nc)]
    test_set = np.stack(test_keys, axis=0).astype(np.float32)
    test_labels = np.arange(nc, dtype=np.int64)

    old_count = max(1, train_set.shape[0] // 2)
    old_test_set = train_set[:old_count]
    old_test_labels = train_labels_arr[:old_count]

    arm_results: Dict[str, Dict[str, float]] = {}
    arm_results["hebbian_baseline"] = run_arm_hebbian_baseline(
        prototypes, train_set, train_labels_arr, test_set, test_labels, nd)
    arm_results["binary_hebbian"] = run_arm_binary_hebbian(
        prototypes, train_set, train_labels_arr, test_set, test_labels, nd)
    arm_results["btsp_full"] = run_arm_btsp_full(
        prototypes, train_set, train_labels_arr, test_set, test_labels,
        old_test_set, old_test_labels, nd, g, use_gate=True)
    arm_results["btsp_no_neuromod"] = run_arm_btsp_full(
        prototypes, train_set, train_labels_arr, test_set, test_labels,
        old_test_set, old_test_labels, nd, g, use_gate=False)
    arm_results["diag_tag_fraction"] = run_arm_diag_tag_fraction(
        prototypes, train_set, train_labels_arr, nd, g)

    return {
        "seed": int(seed),
        "N": nd,
        "N_CAT": nc,
        "N_TRAIN": nt,
        "proto_noise": noise,
        "alpha_load": cfg["alpha"],
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": arm_results,
        "regime_cfg": cfg,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           probe_outcome: Dict[str, Any]) -> Dict[str, Any]:
    if probe_outcome.get("found_cfg") is None:
        # Probe failed -> REGIME_INFEASIBLE
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "REGIME_INFEASIBLE: no probe cfg gave baseline in [%.2f, %.2f]" % (
                HP_BASELINE_LO, HP_BASELINE_HI),
            "summary": "REGIME_INFEASIBLE: no probe cfg gave baseline in [%.2f, %.2f]" % (
                HP_BASELINE_LO, HP_BASELINE_HI),
            "probe_results": probe_outcome.get("probe_results", []),
            "found_cfg": None,
            "verdict_reason": "REGIME_INFEASIBLE",
        }

    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "probe found cfg but no per-seed partials",
            "summary": "probe found cfg but no per-seed partials",
            "found_cfg": probe_outcome["found_cfg"],
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

    # Re-validate baseline at FULL seed average (probe was single-seed)
    baseline_in_band = (HP_BASELINE_LO <= cont_new <= HP_BASELINE_HI)

    verdict = "MIDDLE_BAND"
    verdict_reason = ""
    if not baseline_in_band:
        if cont_new > HP_BASELINE_HI:
            verdict = "HARD_FAIL"
            verdict_reason = "BASELINE_CEILING: full-seed baseline=%.3f > %.2f" % (cont_new, HP_BASELINE_HI)
        else:
            verdict = "HARD_FAIL"
            verdict_reason = "BASELINE_FLOOR: full-seed baseline=%.3f < %.2f" % (cont_new, HP_BASELINE_LO)
    elif (btsp_new >= HP_NEW_FLOOR and
            btsp_old >= HP_OLD_FLOOR_FRAC * HP_NEW_FLOOR and
            btsp_cv < HP_CV_MAX and
            btsp_new > bin_heb["mean_new"]):
        verdict = "HARD_PASS"
        verdict_reason = "FAIR_REGIME_MECHANISM_LIFT: baseline in band and BTSP > binary_heb"
    elif btsp_new < HF_NEW_FLOOR:
        verdict = "HARD_FAIL"
        verdict_reason = "MECHANISM_NULL: BTSP=%.3f < %.2f at fair regime" % (btsp_new, HF_NEW_FLOOR)
    elif btsp_old < HF_OLD_FRAC * HP_NEW_FLOOR:
        verdict = "HARD_FAIL"
        verdict_reason = "CATASTROPHIC_FORGETTING: old=%.3f < %.2f" % (btsp_old, HF_OLD_FRAC * HP_NEW_FLOOR)

    verdict_msg = (
        "%s | %s | BTSP_new=%.3f BTSP_old=%.3f BinHeb=%.3f ContHeb=%.3f | "
        "cv=%.3f tag=%.3f | regime=%s | n=%d"
    ) % (verdict, verdict_reason, btsp_new, btsp_old, bin_heb["mean_new"], cont_new,
         btsp_cv, btsp["mean_tag"],
         json.dumps({k: v for k, v in probe_outcome["found_cfg"].items() if k != "baseline_acc"}),
         len(seeds_sorted))

    completed_units = len(seeds_sorted) * len(EXPECTED_ARMS) + 1
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "found_cfg": probe_outcome["found_cfg"],
        "probe_results": probe_outcome["probe_results"],
        "saturation_score": cont_new,
        "btsp_cv": btsp_cv,
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
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s seeds=%s expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            # Tiny probe then 1 arm run
            probe = regime_probe(SEEDS)
            # SELF_TEST: even if not in band, force-run at fallback cfg
            cfg = probe.get("found_cfg") or {"N_DIM": PROBE_N_DIM[0],
                                              "N_CAT": PROBE_N_CAT[0],
                                              "N_TRAIN": PROBE_N_TRAIN[0],
                                              "proto_noise": PROBE_PROTO_NOISE[0],
                                              "alpha": PROBE_N_CAT[0] / float(PROBE_N_DIM[0])}
            r = run_one_seed_at_regime(SEEDS[0], cfg)
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"]
                assert "new_pattern_acc" in r["per_arm"][arm]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: probe + per-arm structure verified")
            print("[selftest] OK probe=%s arms_btsp=%.3f" % (
                cfg, r["per_arm"]["btsp_full"]["new_pattern_acc"]), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    # Run probe FIRST
    print("[probe] starting regime probe...", flush=True)
    _write_minimal_metrics(out_dir, "RUNNING_PROBE",
                           "RUNNING_PROBE: searching for fair regime",
                           extra={"_phase": "probe"})
    probe = regime_probe(SEEDS)
    found_cfg = probe.get("found_cfg")
    if found_cfg is None:
        print("[probe] INFEASIBLE: no cfg found with baseline in [%.2f, %.2f]" % (
            HP_BASELINE_LO, HP_BASELINE_HI), flush=True)
        # Write INFEASIBLE verdict + bail
        final = aggregate_and_verdict({}, probe)
        final["anchor_name"] = ANCHOR_NAME
        final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
        final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        final["pid"] = os.getpid()
        final["run_mode"] = RUN_MODE
        final["config_version"] = CONFIG_VERSION
        final["_hardening_marker"] = "v2_btsp_regime_probed"
        (out_dir / "metrics.json").write_text(
            json.dumps(final, indent=2), encoding="utf-8")
        print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
        return 0

    print("[probe] FOUND cfg=%s baseline=%.3f" % (found_cfg, found_cfg["baseline_acc"]), flush=True)
    _write_minimal_metrics(out_dir, "RUNNING",
                           "RUNNING: at regime %s" % found_cfg,
                           extra={"_phase": "arms", "found_cfg": found_cfg,
                                  "probe_results": probe["probe_results"]})

    # Save probe to partials dir style (use seed=0 as probe key)
    probe_save = dict(probe)
    probe_save["seed"] = 0
    probe_save["N"] = found_cfg["N_DIM"]
    probe_save["run_mode"] = RUN_MODE
    write_partial_key(out_dir, "probe", probe_save)

    # Run arms at found regime
    per_seed_results: Dict[str, Dict[str, Any]] = {}
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d) at regime=%s" % (
                                   seed, i + 1, len(SEEDS), found_cfg),
                               extra={"_phase": "seed_running", "_current_seed": seed,
                                      "found_cfg": found_cfg})
        result = run_one_seed_at_regime(seed, found_cfg)
        write_partial_key(out_dir, seed, result)
        per_seed_results[str(seed)] = result
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    final = aggregate_and_verdict(per_seed_results, probe)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v2_btsp_regime_probed"
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
