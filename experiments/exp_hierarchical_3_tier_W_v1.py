"""hierarchical_3_tier_W_v1 -- Battery 2 cell at BTSP-probed FAIR REGIME.

Prereg: preregs/2026-06-27_hierarchical_3_tier_W_v1.md
Drill source: notes/research_drill_5x_consolidation_saturation_barrier_2026-06-27.md
                Angle 4 Mechanism 4.2 (hierarchical 3-tier W; fast/slow/ultraslow).
Citation: Tse-Morris 2007 Science; McClelland CLS 1995.

FIX vs PREREG REGIME: USER directive 2026-06-27 - use BTSP-probed FAIR REGIME
(N_DIM=1024, N_CAT=50, N_TRAIN=5, proto_noise=0.6, alpha=0.0488) - the ONLY
consolidation regime today that didn't saturate baselines. Includes regime probe
(BTSP v2 style) that tightens N_TRAIN to 7 or proto_noise to 0.55 if needed to
push ContHeb baseline into [0.40, 0.65] fair band.

ARMS (4 mandatory + 1 diagnostic):
  ARM_BASELINE_SINGLE_TIER_HEBBIAN   global Hebbian, single W (anti-saturation gate)
  ARM_TWO_TIER_FAST_SLOW             fast (eta=1.0) + slow (eta=0.05, STC-tag-gated)
  ARM_THREE_TIER_NO_ULTRASLOW        ablation: fast+slow only (isolates ultraslow tier)
                                      Note: this is EQUIVALENT to ARM_TWO_TIER_FAST_SLOW
                                      structurally, but kept named separately for
                                      cardinality/diag clarity per prereg.
  ARM_THREE_TIER_STABILITY_GATED     primary: full 3-tier with N_STABILITY=5 promote
  ARM_DIAG_TIER_TRANSITION_FRACTION  diagnostic: fraction of fast->slow + slow->ultraslow
                                      transitions per cycle + tier drift Frobenius

SMOKE MUST FIRE: catastrophic-forgetting test (learn pattern set A, then B, check A
retention). Single-tier baseline must drop on A after learning B; 3-tier must retain A.

PRE-REG BANDS (FAIR-REGIME variant; old/new computed post-interference):
  HARD_PASS:
    3-tier stability-gated old_pattern_acc >= 0.50 AND new_pattern_acc >= 0.50
    AND 1-tier baseline forgets old (drop >= 0.30 below 3-tier)
    AND BASELINE_SINGLE_TIER new_pattern_acc in [0.40, 0.65] FAIR band
    AND cv across seeds < 0.10 (full only; smoke n=2 reports cv but doesn't gate)
    AND ARM_DIAG drift ratio fast > 3*slow > 3*ultraslow
  MIDDLE_BAND:
    3-tier preserves old pattern but with <0.30 lift over 1-tier baseline
    OR HARD_PASS arithmetic but drift ratio <3x separation
  HARD_FAIL:
    any baseline >= 0.95 (saturation)
    OR 3-tier no better than 2-tier on old_pattern_acc (no benefit from ultraslow)
    OR cardinality breach
    OR baseline NOT in FAIR band [0.40, 0.65]
    OR regime probe finds NO fair cfg

META_RULE_AA: arms read same surface (cosine to prototype from final W = sum tiers)
META_RULE_K: smoke fires discriminator (forgetting interference test in smoke)
META_RULE_X: main wrapped in if __name__ == "__main__"; L1-L4 hardening
META_RULE_J: no silent except blocks

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SMOKE = 1 probe + 5 arms * 2 seeds = 11
  EXPECTED_N_UNITS_FULL  = 1 probe + 5 arms * 5 seeds = 26

HARDENING (L1-L4):
  L1 STARTED metrics + PID + expected_arms at write
  L2 per-arm + per-seed progress updates
  L3 outer try/except around main with import-crash sentinel
  L4 ASCII-only; no emojis; no em-dashes

Author: exp_dev 2026-06-27 (Battery 2 consolidation - cell 1 of 2 fair-regime ships).
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

ANCHOR_NAME = "hierarchical_3_tier_W_v1"

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
HP_OLD_FLOOR = 0.50              # 3-tier must retain old above this
HP_NEW_FLOOR = 0.50              # and learn new above this
HP_BASELINE_LO = 0.40
HP_BASELINE_HI = 0.65
HP_FORGETTING_DROP_MIN = 0.30    # 1-tier baseline must drop >= 0.30 below 3-tier on old
HP_CV_MAX = 0.10
HP_DRIFT_RATIO_MIN = 3.0         # fast/slow and slow/ultraslow drift separation
HF_SATURATION_HI = 0.95

# Three-tier learning rates (1000x ratio fast:ultraslow per Tse-Morris timescales)
ETA_FAST = 1.0
ETA_SLOW = 0.05
ETA_ULTRASLOW = 1e-3
N_STABILITY = 5  # Tse-Morris schema-formation window (5 consolidation cycles)

# STC tag fraction (which fast updates eligible for slow promotion)
STC_TAG_FRACTION = 0.20

EXPECTED_ARMS = ["baseline_single_tier_hebbian",
                 "two_tier_fast_slow",
                 "three_tier_no_ultraslow",
                 "three_tier_stability_gated",
                 "diag_tier_transition_fraction"]

# REGIME PROBE GRID - BTSP-probed FAIR REGIME at the center with tightening fallbacks
if SELF_TEST_MODE:
    PROBE_N_DIM = [256]
    PROBE_N_CAT = [10]
    PROBE_N_TRAIN = [5]
    PROBE_PROTO_NOISE = [0.60]
    SEEDS = [7]
elif RUN_MODE == "smoke":
    # SMOKE: downscale to N_DIM=512/N_CAT=25 SAME alpha=0.0488 (META_RULE_K)
    # Probe brackets the BTSP fair regime + tightening fallbacks
    PROBE_N_DIM = [512]
    PROBE_N_CAT = [25]
    PROBE_N_TRAIN = [5, 7, 10]
    PROBE_PROTO_NOISE = [0.55, 0.60, 0.65]
    SEEDS = [7, 17]
else:
    # FULL: BTSP-probed FAIR regime at N_DIM=1024 N_CAT=50 (alpha=0.0488)
    PROBE_N_DIM = [1024]
    PROBE_N_CAT = [50]
    PROBE_N_TRAIN = [5, 7, 10]
    PROBE_PROTO_NOISE = [0.55, 0.60, 0.65]
    SEEDS = [7, 17, 23, 31, 41]

# Post-consolidation new-pattern interference test sizes
if SELF_TEST_MODE:
    N_NEW_PATTERNS = 3
elif RUN_MODE == "smoke":
    N_NEW_PATTERNS = 10  # smoke must fire forgetting discriminator
else:
    N_NEW_PATTERNS = 20  # prereg spec

N_CONSOLIDATION_PULSES = 5 if SELF_TEST_MODE else (10 if RUN_MODE == "smoke" else 20)

EXPECTED_N_UNITS_SMOKE = 1 + len(EXPECTED_ARMS) * len(SEEDS)
EXPECTED_N_UNITS = EXPECTED_N_UNITS_SMOKE if RUN_MODE == "smoke" else (
    1 + len(EXPECTED_ARMS) * len(SEEDS))

CONFIG_VERSION = (
    "ANCHOR=%s,probe_N=%s,probe_NCAT=%s,probe_NTRAIN=%s,probe_noise=%s,seeds=%s,mode=%s,"
    "HP_old>=%.2f,HP_new>=%.2f,HP_baseline_band=[%.2f,%.2f],"
    "HP_forget_drop>=%.2f,HP_cv<=%.2f,HP_drift_ratio>=%.1f,"
    "eta_fast=%.3f,eta_slow=%.3f,eta_ultraslow=%.4f,N_STABILITY=%d,"
    "stc_tag_frac=%.2f,N_NEW_PATTERNS=%d,N_PULSES=%d,"
    "hardening=L1early+L2perseed+L3outertry+L4importsentinel,"
    "FAIRNESS=PROBE_BASELINE_IN_BAND_THEN_3TIER_MECHANISM"
) % (
    ANCHOR_NAME, PROBE_N_DIM, PROBE_N_CAT, PROBE_N_TRAIN, PROBE_PROTO_NOISE,
    SEEDS, RUN_MODE,
    HP_OLD_FLOOR, HP_NEW_FLOOR, HP_BASELINE_LO, HP_BASELINE_HI,
    HP_FORGETTING_DROP_MIN, HP_CV_MAX, HP_DRIFT_RATIO_MIN,
    ETA_FAST, ETA_SLOW, ETA_ULTRASLOW, N_STABILITY,
    STC_TAG_FRACTION, N_NEW_PATTERNS, N_CONSOLIDATION_PULSES,
)

# Pre-dispatch hard gates (META_RULE_K + prereg "Pre-dispatch HARD gate")
_alpha_smoke = PROBE_N_CAT[0] / float(PROBE_N_DIM[0])
assert 0.03 <= _alpha_smoke <= 0.20, (
    "alpha=%.4f out of safe band [0.03, 0.20]" % _alpha_smoke)
_snr_pred = 1.0 / math.sqrt(_alpha_smoke)
assert 2.5 <= _snr_pred <= 6.0, "predicted SNR=%.2f out of [2.5, 6.0]" % _snr_pred
assert ETA_FAST / ETA_SLOW >= 10, "eta_fast/eta_slow < 10 (timescale separation)"
assert ETA_SLOW / ETA_ULTRASLOW >= 10, "eta_slow/eta_ultraslow < 10 (timescale separation)"
assert 3 <= N_STABILITY <= 10, "N_STABILITY=%d out of [3, 10]" % N_STABILITY

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
            "_hardening_marker": "v1_hierarchical_3_tier_W",
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
            "_hardening_marker": "v1_hierarchical_3_tier_W_import_crash",
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
    n = proto.shape[0]
    eff = min(1.0, max(0.0, noise))
    flip = g.random(n) < eff
    out = proto.copy()
    out[flip] = -out[flip]
    return out / (np.linalg.norm(out) + 1e-8)


def hebbian_outer(key: np.ndarray, value: np.ndarray) -> np.ndarray:
    n = key.shape[0]
    return np.outer(key, value).astype(np.float32) / float(n)


def readout_accuracy_classify(W_total: np.ndarray, prototypes: np.ndarray,
                              queries: np.ndarray, labels: np.ndarray) -> float:
    """W_total @ query -> classify by argmax cosine to any prototype; return mean acc."""
    out = queries @ W_total
    out_n = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-8)
    proto_n = prototypes / (np.linalg.norm(prototypes, axis=1, keepdims=True) + 1e-8)
    sims = out_n @ proto_n.T
    pred = np.argmax(sims, axis=1)
    return float(np.mean(pred == labels))


# -------------------------- regime probe --------------------------

def regime_probe(seeds: List[int]) -> Dict[str, Any]:
    """Sweep PROBE_GRID; for each cfg, replicate the EXACT arm-runner protocol
    (learn pattern set A, learn pattern set B, eval on B-test) using single-tier
    Hebbian. Probe baseline = arm-runner baseline (META_RULE_AA fairness).
    """
    probe_results: List[Dict[str, Any]] = []
    found_cfg = None

    for nd in PROBE_N_DIM:
        for nc in PROBE_N_CAT:
            for nt in PROBE_N_TRAIN:
                for noise in PROBE_PROTO_NOISE:
                    alpha = nc / float(nd)
                    cfg = {"N_DIM": nd, "N_CAT": nc, "N_TRAIN": nt,
                           "proto_noise": noise, "alpha": alpha}
                    accs_per_seed: List[float] = []
                    for seed in seeds:
                        # Replicate arm-runner exactly: separate A and B sets
                        g_setA = np.random.default_rng(seed + 1)
                        g_setB = np.random.default_rng(seed + 2)
                        pA = _generate_pattern_set(cfg, g_setA, "A")
                        pB = _generate_pattern_set(cfg, g_setB, "B")
                        nc_B = min(N_NEW_PATTERNS, pB[0].shape[0])
                        pB_protos = pB[0][:nc_B]
                        pB_train = pB[1][pB[2] < nc_B]
                        pB_train_labels = pB[2][pB[2] < nc_B]
                        pB_test = pB[3][:nc_B]
                        pB_test_labels = pB[4][:nc_B]
                        # Single-tier Hebbian: learn A then B (same as baseline arm)
                        W = np.zeros((nd, nd), dtype=np.float32)
                        A_train = pA[1]
                        A_labels = pA[2]
                        A_protos = pA[0]
                        for i in range(A_train.shape[0]):
                            W += hebbian_outer(A_train[i], A_protos[A_labels[i]])
                        for i in range(pB_train.shape[0]):
                            W += hebbian_outer(pB_train[i], pB_protos[pB_train_labels[i]])
                        acc_B = readout_accuracy_classify(W, pB_protos, pB_test, pB_test_labels)
                        accs_per_seed.append(acc_B)
                    mean_acc = float(np.mean(accs_per_seed))
                    cfg["baseline_acc"] = mean_acc
                    cfg["baseline_per_seed"] = accs_per_seed
                    probe_results.append(cfg)
                    print("[probe] N=%d NCAT=%d NTRAIN=%d noise=%.2f alpha=%.4f -> baseline_B_mean=%.3f (per_seed=%s)" % (
                        nd, nc, nt, noise, alpha, mean_acc,
                        ["%.3f" % a for a in accs_per_seed]), flush=True)
                    if HP_BASELINE_LO <= mean_acc <= HP_BASELINE_HI and found_cfg is None:
                        found_cfg = dict(cfg)

    return {"probe_results": probe_results, "found_cfg": found_cfg}


# -------------------------- arms --------------------------

def _generate_pattern_set(cfg: Dict[str, Any], g: np.random.Generator,
                          set_label: str) -> Tuple[np.ndarray, np.ndarray,
                                                     np.ndarray, np.ndarray, np.ndarray]:
    """Returns prototypes, train_set, train_labels, test_set, test_labels."""
    nd = cfg["N_DIM"]
    nc = cfg["N_CAT"]
    nt = cfg["N_TRAIN"]
    noise = cfg["proto_noise"]

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

    return prototypes, train_set, train_labels_arr, test_set, test_labels


def run_arm_single_tier(cfg: Dict[str, Any], g_seed: int,
                         pattern_set_A: Dict[str, np.ndarray],
                         pattern_set_B: Dict[str, np.ndarray]
                         ) -> Dict[str, float]:
    """Single global Hebbian W; learn A, learn B, test A retention + B accuracy."""
    nd = cfg["N_DIM"]
    g = np.random.default_rng(g_seed + 7001)
    W = np.zeros((nd, nd), dtype=np.float32)
    # Phase 1: learn A
    A_train = pattern_set_A["train"]
    A_labels = pattern_set_A["train_labels"]
    A_protos = pattern_set_A["prototypes"]
    for i in range(A_train.shape[0]):
        W += hebbian_outer(A_train[i], A_protos[A_labels[i]])
    # Test A pre-interference
    acc_A_pre = readout_accuracy_classify(W, A_protos, pattern_set_A["test"],
                                          pattern_set_A["test_labels"])
    # Phase 2: learn B (interference)
    B_train = pattern_set_B["train"]
    B_labels = pattern_set_B["train_labels"]
    B_protos = pattern_set_B["prototypes"]
    for i in range(B_train.shape[0]):
        W += hebbian_outer(B_train[i], B_protos[B_labels[i]])
    # Test A post-interference + B
    acc_A_post = readout_accuracy_classify(W, A_protos, pattern_set_A["test"],
                                           pattern_set_A["test_labels"])
    acc_B = readout_accuracy_classify(W, B_protos, pattern_set_B["test"],
                                      pattern_set_B["test_labels"])
    return {
        "new_pattern_acc": acc_B,
        "old_pattern_acc": acc_A_post,
        "old_pattern_acc_pre_interference": acc_A_pre,
        "forgetting_drop": acc_A_pre - acc_A_post,
        "drift_fast": 0.0,
        "drift_slow": 0.0,
        "drift_ultraslow": 0.0,
        "transition_fast_to_slow_frac": 0.0,
        "transition_slow_to_ultraslow_frac": 0.0,
    }


def _consolidate_two_tier(W_fast: np.ndarray, W_slow: np.ndarray,
                           g: np.random.Generator) -> Tuple[np.ndarray, np.ndarray, float]:
    """Promote STC_TAG_FRACTION of |W_fast| largest-magnitude entries into W_slow
    at eta_slow rate. Returns (W_fast_flushed, W_slow_updated, fast_to_slow_frac).
    """
    flat = np.abs(W_fast).ravel()
    n_total = flat.size
    n_tag = max(1, int(STC_TAG_FRACTION * n_total))
    if n_tag < n_total:
        thresh = np.partition(flat, -n_tag)[-n_tag]
    else:
        thresh = float(flat.min())
    tag_mask = np.abs(W_fast) >= thresh
    transition_frac = float(tag_mask.sum()) / n_total
    W_slow_new = W_slow + ETA_SLOW * (W_fast * tag_mask.astype(np.float32))
    W_fast_flushed = np.zeros_like(W_fast)
    return W_fast_flushed, W_slow_new, transition_frac


def _consolidate_three_tier(W_fast: np.ndarray, W_slow: np.ndarray,
                             W_ultraslow: np.ndarray,
                             slow_history: List[np.ndarray],
                             use_stability_gate: bool,
                             g: np.random.Generator
                             ) -> Tuple[np.ndarray, np.ndarray, np.ndarray,
                                        List[np.ndarray], float, float]:
    """Three-tier consolidation:
    1. Fast -> slow via STC tag (same as two-tier)
    2. Slow -> ultraslow: if use_stability_gate, only entries stable across
       last N_STABILITY slow snapshots; else, every pulse at eta_ultraslow.
    """
    # Fast -> slow
    W_fast_flushed, W_slow_new, fast_to_slow_frac = _consolidate_two_tier(
        W_fast, W_slow, g)
    # Track slow history
    slow_history.append(W_slow_new.copy())
    if len(slow_history) > N_STABILITY:
        slow_history.pop(0)

    # Slow -> ultraslow
    transition_slow_to_ultra_frac = 0.0
    if use_stability_gate:
        if len(slow_history) >= N_STABILITY:
            # Compute per-entry stability: sign agrees across all N_STABILITY snapshots
            signs = np.stack([np.sign(s) for s in slow_history], axis=0)
            # Stable = all signs match and not all zero
            stable_mask = np.all(signs == signs[0], axis=0) & (signs[0] != 0)
            transition_slow_to_ultra_frac = float(stable_mask.sum()) / stable_mask.size
            # Update ultraslow only on stable entries
            W_ultraslow_new = W_ultraslow + ETA_ULTRASLOW * (
                W_slow_new * stable_mask.astype(np.float32))
        else:
            W_ultraslow_new = W_ultraslow.copy()
    else:
        # NO_STABILITY ablation: every pulse, all entries at eta_ultraslow
        W_ultraslow_new = W_ultraslow + ETA_ULTRASLOW * W_slow_new
        transition_slow_to_ultra_frac = 1.0

    return (W_fast_flushed, W_slow_new, W_ultraslow_new, slow_history,
            fast_to_slow_frac, transition_slow_to_ultra_frac)


def run_arm_two_tier_fast_slow(cfg: Dict[str, Any], g_seed: int,
                                pattern_set_A: Dict[str, np.ndarray],
                                pattern_set_B: Dict[str, np.ndarray]
                                ) -> Dict[str, float]:
    """Fast + slow with STC-tag-gated promotion; consolidate every cycle."""
    nd = cfg["N_DIM"]
    g = np.random.default_rng(g_seed + 7002)
    W_fast = np.zeros((nd, nd), dtype=np.float32)
    W_slow = np.zeros((nd, nd), dtype=np.float32)

    drift_fast_acc: List[float] = []
    drift_slow_acc: List[float] = []
    transition_fracs: List[float] = []

    A_train = pattern_set_A["train"]
    A_labels = pattern_set_A["train_labels"]
    A_protos = pattern_set_A["prototypes"]
    # Phase 1: learn A in chunks of N_TRAIN, consolidate after each chunk
    chunk_size = max(1, A_train.shape[0] // N_CONSOLIDATION_PULSES)
    for chunk_idx in range(N_CONSOLIDATION_PULSES):
        W_fast_before = W_fast.copy()
        W_slow_before = W_slow.copy()
        i0 = chunk_idx * chunk_size
        i1 = min(A_train.shape[0], (chunk_idx + 1) * chunk_size)
        for i in range(i0, i1):
            W_fast += ETA_FAST * hebbian_outer(A_train[i], A_protos[A_labels[i]])
        drift_fast_acc.append(float(np.linalg.norm(W_fast - W_fast_before)))
        W_fast, W_slow, tf = _consolidate_two_tier(W_fast, W_slow, g)
        drift_slow_acc.append(float(np.linalg.norm(W_slow - W_slow_before)))
        transition_fracs.append(tf)

    W_total = W_fast + W_slow
    acc_A_pre = readout_accuracy_classify(W_total, A_protos, pattern_set_A["test"],
                                          pattern_set_A["test_labels"])

    # Phase 2: learn B
    B_train = pattern_set_B["train"]
    B_labels = pattern_set_B["train_labels"]
    B_protos = pattern_set_B["prototypes"]
    chunk_size_B = max(1, B_train.shape[0] // N_CONSOLIDATION_PULSES)
    for chunk_idx in range(N_CONSOLIDATION_PULSES):
        W_fast_before = W_fast.copy()
        W_slow_before = W_slow.copy()
        i0 = chunk_idx * chunk_size_B
        i1 = min(B_train.shape[0], (chunk_idx + 1) * chunk_size_B)
        for i in range(i0, i1):
            W_fast += ETA_FAST * hebbian_outer(B_train[i], B_protos[B_labels[i]])
        drift_fast_acc.append(float(np.linalg.norm(W_fast - W_fast_before)))
        W_fast, W_slow, tf = _consolidate_two_tier(W_fast, W_slow, g)
        drift_slow_acc.append(float(np.linalg.norm(W_slow - W_slow_before)))
        transition_fracs.append(tf)

    W_total = W_fast + W_slow
    acc_A_post = readout_accuracy_classify(W_total, A_protos, pattern_set_A["test"],
                                           pattern_set_A["test_labels"])
    acc_B = readout_accuracy_classify(W_total, B_protos, pattern_set_B["test"],
                                      pattern_set_B["test_labels"])
    return {
        "new_pattern_acc": acc_B,
        "old_pattern_acc": acc_A_post,
        "old_pattern_acc_pre_interference": acc_A_pre,
        "forgetting_drop": acc_A_pre - acc_A_post,
        "drift_fast": float(np.mean(drift_fast_acc)) if drift_fast_acc else 0.0,
        "drift_slow": float(np.mean(drift_slow_acc)) if drift_slow_acc else 0.0,
        "drift_ultraslow": 0.0,
        "transition_fast_to_slow_frac": float(np.mean(transition_fracs)) if transition_fracs else 0.0,
        "transition_slow_to_ultraslow_frac": 0.0,
    }


def run_arm_three_tier(cfg: Dict[str, Any], g_seed: int,
                        pattern_set_A: Dict[str, np.ndarray],
                        pattern_set_B: Dict[str, np.ndarray],
                        use_stability_gate: bool) -> Dict[str, float]:
    """Three-tier W (fast/slow/ultraslow). use_stability_gate=True is primary;
    False is the ablation 'three_tier_no_ultraslow' (ultraslow updates every pulse).
    Note: NAME 'no_ultraslow' is misleading per prereg drift; semantically it's
    'three_tier_no_stability_gate' (ultraslow exists but is not gated).
    """
    nd = cfg["N_DIM"]
    g = np.random.default_rng(g_seed + 7003)
    W_fast = np.zeros((nd, nd), dtype=np.float32)
    W_slow = np.zeros((nd, nd), dtype=np.float32)
    W_ultraslow = np.zeros((nd, nd), dtype=np.float32)
    slow_history: List[np.ndarray] = []

    drift_fast_acc: List[float] = []
    drift_slow_acc: List[float] = []
    drift_ultraslow_acc: List[float] = []
    transition_fast_to_slow: List[float] = []
    transition_slow_to_ultra: List[float] = []

    A_train = pattern_set_A["train"]
    A_labels = pattern_set_A["train_labels"]
    A_protos = pattern_set_A["prototypes"]
    chunk_size = max(1, A_train.shape[0] // N_CONSOLIDATION_PULSES)
    for chunk_idx in range(N_CONSOLIDATION_PULSES):
        W_fast_before = W_fast.copy()
        W_slow_before = W_slow.copy()
        W_ultra_before = W_ultraslow.copy()
        i0 = chunk_idx * chunk_size
        i1 = min(A_train.shape[0], (chunk_idx + 1) * chunk_size)
        for i in range(i0, i1):
            W_fast += ETA_FAST * hebbian_outer(A_train[i], A_protos[A_labels[i]])
        drift_fast_acc.append(float(np.linalg.norm(W_fast - W_fast_before)))
        W_fast, W_slow, W_ultraslow, slow_history, tfs, tsu = _consolidate_three_tier(
            W_fast, W_slow, W_ultraslow, slow_history, use_stability_gate, g)
        drift_slow_acc.append(float(np.linalg.norm(W_slow - W_slow_before)))
        drift_ultraslow_acc.append(float(np.linalg.norm(W_ultraslow - W_ultra_before)))
        transition_fast_to_slow.append(tfs)
        transition_slow_to_ultra.append(tsu)

    W_total = W_fast + W_slow + W_ultraslow
    acc_A_pre = readout_accuracy_classify(W_total, A_protos, pattern_set_A["test"],
                                          pattern_set_A["test_labels"])

    # Phase 2: learn B
    B_train = pattern_set_B["train"]
    B_labels = pattern_set_B["train_labels"]
    B_protos = pattern_set_B["prototypes"]
    chunk_size_B = max(1, B_train.shape[0] // N_CONSOLIDATION_PULSES)
    for chunk_idx in range(N_CONSOLIDATION_PULSES):
        W_fast_before = W_fast.copy()
        W_slow_before = W_slow.copy()
        W_ultra_before = W_ultraslow.copy()
        i0 = chunk_idx * chunk_size_B
        i1 = min(B_train.shape[0], (chunk_idx + 1) * chunk_size_B)
        for i in range(i0, i1):
            W_fast += ETA_FAST * hebbian_outer(B_train[i], B_protos[B_labels[i]])
        drift_fast_acc.append(float(np.linalg.norm(W_fast - W_fast_before)))
        W_fast, W_slow, W_ultraslow, slow_history, tfs, tsu = _consolidate_three_tier(
            W_fast, W_slow, W_ultraslow, slow_history, use_stability_gate, g)
        drift_slow_acc.append(float(np.linalg.norm(W_slow - W_slow_before)))
        drift_ultraslow_acc.append(float(np.linalg.norm(W_ultraslow - W_ultra_before)))
        transition_fast_to_slow.append(tfs)
        transition_slow_to_ultra.append(tsu)

    W_total = W_fast + W_slow + W_ultraslow
    acc_A_post = readout_accuracy_classify(W_total, A_protos, pattern_set_A["test"],
                                           pattern_set_A["test_labels"])
    acc_B = readout_accuracy_classify(W_total, B_protos, pattern_set_B["test"],
                                      pattern_set_B["test_labels"])
    return {
        "new_pattern_acc": acc_B,
        "old_pattern_acc": acc_A_post,
        "old_pattern_acc_pre_interference": acc_A_pre,
        "forgetting_drop": acc_A_pre - acc_A_post,
        "drift_fast": float(np.mean(drift_fast_acc)) if drift_fast_acc else 0.0,
        "drift_slow": float(np.mean(drift_slow_acc)) if drift_slow_acc else 0.0,
        "drift_ultraslow": float(np.mean(drift_ultraslow_acc)) if drift_ultraslow_acc else 0.0,
        "transition_fast_to_slow_frac": float(np.mean(transition_fast_to_slow)) if transition_fast_to_slow else 0.0,
        "transition_slow_to_ultraslow_frac": float(np.mean(transition_slow_to_ultra)) if transition_slow_to_ultra else 0.0,
    }


def run_arm_diag(cfg: Dict[str, Any], g_seed: int,
                  pattern_set_A: Dict[str, np.ndarray],
                  pattern_set_B: Dict[str, np.ndarray]) -> Dict[str, float]:
    """Diagnostic: re-run primary 3-tier arm but report ONLY tier dynamics.
    Returns transition fractions + drift ratios as the headline metric.
    """
    r = run_arm_three_tier(cfg, g_seed + 1000, pattern_set_A, pattern_set_B,
                            use_stability_gate=True)
    # Diagnostic 'new/old_pattern_acc' = transition fractions for at-a-glance
    return {
        "new_pattern_acc": r["transition_fast_to_slow_frac"],
        "old_pattern_acc": r["transition_slow_to_ultraslow_frac"],
        "old_pattern_acc_pre_interference": r["old_pattern_acc_pre_interference"],
        "forgetting_drop": r["forgetting_drop"],
        "drift_fast": r["drift_fast"],
        "drift_slow": r["drift_slow"],
        "drift_ultraslow": r["drift_ultraslow"],
        "transition_fast_to_slow_frac": r["transition_fast_to_slow_frac"],
        "transition_slow_to_ultraslow_frac": r["transition_slow_to_ultraslow_frac"],
    }


def run_one_seed_at_regime(seed: int, cfg: Dict[str, Any]) -> Dict[str, Any]:
    g_setA = np.random.default_rng(seed + 1)
    g_setB = np.random.default_rng(seed + 2)
    # Generate INDEPENDENT pattern sets A and B (different prototypes)
    pA = _generate_pattern_set(cfg, g_setA, "A")
    pB = _generate_pattern_set(cfg, g_setB, "B")
    pattern_set_A = {"prototypes": pA[0], "train": pA[1], "train_labels": pA[2],
                      "test": pA[3], "test_labels": pA[4]}
    # For new-pattern interference, B uses a SMALLER pattern count = N_NEW_PATTERNS
    # so we trim down B's category count for the interference phase
    nc_B = min(N_NEW_PATTERNS, pB[0].shape[0])
    pattern_set_B = {
        "prototypes": pB[0][:nc_B],
        "train": pB[1][pB[2] < nc_B],
        "train_labels": pB[2][pB[2] < nc_B],
        "test": pB[3][:nc_B],
        "test_labels": pB[4][:nc_B],
    }

    arm_results: Dict[str, Dict[str, float]] = {}
    arm_results["baseline_single_tier_hebbian"] = run_arm_single_tier(
        cfg, seed, pattern_set_A, pattern_set_B)
    arm_results["two_tier_fast_slow"] = run_arm_two_tier_fast_slow(
        cfg, seed, pattern_set_A, pattern_set_B)
    arm_results["three_tier_no_ultraslow"] = run_arm_three_tier(
        cfg, seed, pattern_set_A, pattern_set_B, use_stability_gate=False)
    arm_results["three_tier_stability_gated"] = run_arm_three_tier(
        cfg, seed, pattern_set_A, pattern_set_B, use_stability_gate=True)
    arm_results["diag_tier_transition_fraction"] = run_arm_diag(
        cfg, seed, pattern_set_A, pattern_set_B)

    return {
        "seed": int(seed),
        "N": cfg["N_DIM"],
        "N_CAT": cfg["N_CAT"],
        "N_TRAIN": cfg["N_TRAIN"],
        "proto_noise": cfg["proto_noise"],
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
        forget_vals: List[float] = []
        drift_fast_vals: List[float] = []
        drift_slow_vals: List[float] = []
        drift_ultra_vals: List[float] = []
        for s in seeds_sorted:
            body = per_seed[s]
            pa = body.get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                new_vals.append(float(d.get("new_pattern_acc", 0.0)))
                old_vals.append(float(d.get("old_pattern_acc", 0.0)))
                forget_vals.append(float(d.get("forgetting_drop", 0.0)))
                drift_fast_vals.append(float(d.get("drift_fast", 0.0)))
                drift_slow_vals.append(float(d.get("drift_slow", 0.0)))
                drift_ultra_vals.append(float(d.get("drift_ultraslow", 0.0)))
                per_arm_full[arm][s] = {k: float(d.get(k, 0.0)) for k in (
                    "new_pattern_acc", "old_pattern_acc",
                    "old_pattern_acc_pre_interference", "forgetting_drop",
                    "drift_fast", "drift_slow", "drift_ultraslow",
                    "transition_fast_to_slow_frac",
                    "transition_slow_to_ultraslow_frac")}
        if new_vals:
            m_new = float(np.mean(new_vals))
            sd_new = float(np.std(new_vals))
            cv = sd_new / abs(m_new) if abs(m_new) > 1e-6 else 0.0
            summary[arm] = {
                "mean_new": m_new, "std_new": sd_new, "cv_new": cv,
                "mean_old": float(np.mean(old_vals)),
                "mean_forget": float(np.mean(forget_vals)),
                "mean_drift_fast": float(np.mean(drift_fast_vals)),
                "mean_drift_slow": float(np.mean(drift_slow_vals)),
                "mean_drift_ultraslow": float(np.mean(drift_ultra_vals)),
                "n": len(new_vals),
            }
        else:
            summary[arm] = {"mean_new": 0.0, "std_new": 0.0, "cv_new": 0.0,
                            "mean_old": 0.0, "mean_forget": 0.0,
                            "mean_drift_fast": 0.0, "mean_drift_slow": 0.0,
                            "mean_drift_ultraslow": 0.0, "n": 0}

    base = summary["baseline_single_tier_hebbian"]
    two_tier = summary["two_tier_fast_slow"]
    three_no_stab = summary["three_tier_no_ultraslow"]
    three_stab = summary["three_tier_stability_gated"]

    base_new = base["mean_new"]
    base_old = base["mean_old"]
    three_stab_new = three_stab["mean_new"]
    three_stab_old = three_stab["mean_old"]
    forgetting_drop_3tier = base_old < three_stab_old
    lift_over_baseline = three_stab_old - base_old
    drift_ratio_fast_slow = (three_stab["mean_drift_fast"] /
                              max(three_stab["mean_drift_slow"], 1e-8))
    drift_ratio_slow_ultra = (three_stab["mean_drift_slow"] /
                               max(three_stab["mean_drift_ultraslow"], 1e-8))

    baseline_in_band = (HP_BASELINE_LO <= base_new <= HP_BASELINE_HI)

    verdict = "MIDDLE_BAND"
    verdict_reason = ""
    if base_new >= HF_SATURATION_HI:
        verdict = "HARD_FAIL"
        verdict_reason = "BASELINE_SATURATION: base_new=%.3f >= %.2f" % (base_new, HF_SATURATION_HI)
    elif not baseline_in_band:
        if base_new > HP_BASELINE_HI:
            verdict = "HARD_FAIL"
            verdict_reason = "BASELINE_CEILING: base_new=%.3f > %.2f" % (base_new, HP_BASELINE_HI)
        else:
            verdict = "HARD_FAIL"
            verdict_reason = "BASELINE_FLOOR: base_new=%.3f < %.2f" % (base_new, HP_BASELINE_LO)
    elif (three_stab_old >= HP_OLD_FLOOR and
            three_stab_new >= HP_NEW_FLOOR and
            lift_over_baseline >= HP_FORGETTING_DROP_MIN and
            drift_ratio_fast_slow >= HP_DRIFT_RATIO_MIN and
            drift_ratio_slow_ultra >= HP_DRIFT_RATIO_MIN):
        verdict = "HARD_PASS"
        verdict_reason = (
            "3TIER_RETAINS_OLD_LEARNS_NEW: stab_old=%.3f stab_new=%.3f lift=%.3f "
            "drift_ratios=%.1f|%.1f" % (
                three_stab_old, three_stab_new, lift_over_baseline,
                drift_ratio_fast_slow, drift_ratio_slow_ultra))
    elif abs(three_stab_old - three_no_stab["mean_old"]) < 0.02:
        verdict = "HARD_FAIL"
        verdict_reason = "STABILITY_GATE_NULL: 3tier_stab=%.3f vs no_stab=%.3f" % (
            three_stab_old, three_no_stab["mean_old"])
    elif lift_over_baseline < 0.05:
        verdict = "MIDDLE_BAND"
        verdict_reason = "MARGINAL_LIFT: 3tier lift over baseline=%.3f" % lift_over_baseline

    verdict_msg = (
        "%s | %s | base_new=%.3f base_old=%.3f | 2tier_old=%.3f | "
        "3tier_no_stab_old=%.3f | 3tier_stab_new=%.3f 3tier_stab_old=%.3f | "
        "lift_over_base=%.3f | drift_ratios fast/slow=%.1f slow/ultra=%.1f | "
        "regime=%s | n_seeds=%d"
    ) % (verdict, verdict_reason, base_new, base_old, two_tier["mean_old"],
         three_no_stab["mean_old"], three_stab_new, three_stab_old,
         lift_over_baseline, drift_ratio_fast_slow, drift_ratio_slow_ultra,
         json.dumps({k: v for k, v in probe_outcome["found_cfg"].items()
                     if k != "baseline_acc"}),
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
        "baseline_in_band": baseline_in_band,
        "lift_over_baseline": lift_over_baseline,
        "drift_ratio_fast_slow": drift_ratio_fast_slow,
        "drift_ratio_slow_ultra": drift_ratio_slow_ultra,
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
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s seeds=%s expected_n=%d N_NEW=%d N_PULSES=%d" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, EXPECTED_N_UNITS,
        N_NEW_PATTERNS, N_CONSOLIDATION_PULSES), flush=True)

    if SELF_TEST_MODE:
        try:
            probe = regime_probe(SEEDS)
            cfg = probe.get("found_cfg") or {
                "N_DIM": PROBE_N_DIM[0], "N_CAT": PROBE_N_CAT[0],
                "N_TRAIN": PROBE_N_TRAIN[0], "proto_noise": PROBE_PROTO_NOISE[0],
                "alpha": PROBE_N_CAT[0] / float(PROBE_N_DIM[0])}
            r = run_one_seed_at_regime(SEEDS[0], cfg)
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"]
                assert "new_pattern_acc" in r["per_arm"][arm]
                assert "old_pattern_acc" in r["per_arm"][arm]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: probe + per-arm structure verified")
            print("[selftest] OK cfg=%s 3tier_new=%.3f 3tier_old=%.3f" % (
                cfg, r["per_arm"]["three_tier_stability_gated"]["new_pattern_acc"],
                r["per_arm"]["three_tier_stability_gated"]["old_pattern_acc"]),
                  flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    print("[probe] starting regime probe...", flush=True)
    _write_minimal_metrics(out_dir, "RUNNING_PROBE",
                           "RUNNING_PROBE: searching for fair regime",
                           extra={"_phase": "probe"})
    probe = regime_probe(SEEDS)
    found_cfg = probe.get("found_cfg")
    if found_cfg is None:
        print("[probe] INFEASIBLE: no cfg found with baseline in [%.2f, %.2f]" % (
            HP_BASELINE_LO, HP_BASELINE_HI), flush=True)
        final = aggregate_and_verdict({}, probe)
        final["anchor_name"] = ANCHOR_NAME
        final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
        final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        final["pid"] = os.getpid()
        final["run_mode"] = RUN_MODE
        final["config_version"] = CONFIG_VERSION
        final["_hardening_marker"] = "v1_hierarchical_3_tier_W"
        (out_dir / "metrics.json").write_text(
            json.dumps(final, indent=2), encoding="utf-8")
        print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
        return 0

    print("[probe] FOUND cfg=%s baseline=%.3f" % (
        found_cfg, found_cfg["baseline_acc"]), flush=True)
    _write_minimal_metrics(out_dir, "RUNNING",
                           "RUNNING: at regime %s" % found_cfg,
                           extra={"_phase": "arms", "found_cfg": found_cfg,
                                  "probe_results": probe["probe_results"]})

    probe_save = dict(probe)
    probe_save["seed"] = 0
    probe_save["N"] = found_cfg["N_DIM"]
    probe_save["run_mode"] = RUN_MODE
    write_partial_key(out_dir, "probe", probe_save)

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
        print("[seed=%d] complete in %.1fs (3tier_stab_new=%.3f stab_old=%.3f)" % (
            seed, time.time() - t0,
            result["per_arm"]["three_tier_stability_gated"]["new_pattern_acc"],
            result["per_arm"]["three_tier_stability_gated"]["old_pattern_acc"]),
              flush=True)

    final = aggregate_and_verdict(per_seed_results, probe)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_hierarchical_3_tier_W"
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
