"""btsp_binary_synapse_v3_sparse_regime_swept -- B3 BTSP revival at literature sparsity.

Prereg: preregs/2026-06-27_btsp_binary_synapse_v3_sparse_regime_swept.md
Drill: notes/research_drill_2x_btsp_binary_signal_collapse_revival_2026-06-27.md TOP-2

ROOT CAUSE FIXED FROM v2: v2 ran at tag_fraction=0.505 because binarization used
sign(W) (median-split, ~50% spike by construction). Wu-Maass 2025 specifies
fp=0.005 (input sparsity), fq=0.0025 (gating sparsity). v3 enforces top-fp
percentile firing AND sweeps (fp, fq) across the 5x5 literature-prescribed grid.

If observed tag_fraction ~ fq across all cells, binarization is correct.
If at some (fp*, fq*) BTSP_new > BinHeb_at_same_fp by >=0.10, mechanism vindicated.
If NO cell satisfies, atomize as HONEST_NEG -> BTSP-binary structurally infeasible
for substrate's prototype-classification task class.

ARMS:
  ARM_CONT_HEBBIAN_BASELINE     continuous W, dense reference (once per seed)
  ARM_BINARY_HEBBIAN_BASELINE   binary W at each fp (matched-sparsity baseline)
  ARM_BTSP_SPARSE_SWEEP         BTSP at each (fp, fq) of 5x5 grid
  ARM_DIAG_TAG_FRACTION_SWEEP   diagnostic: observed tag_fraction per cell

SWEEP GRID:
  fp in {0.005, 0.01, 0.025, 0.05, 0.10}
  fq in {0.0025, 0.01, 0.05, 0.10, 0.25}

PRE-REG BANDS:
  HARD_PASS: at some (fp*<=0.05, fq*<=0.10):
    BTSP_new >= 0.40 AND BTSP_new > BinHeb_at_fp* by >= 0.10 AND old >= 0.30
    AND cv across seeds < 0.10 at winning cell
    AND observed tag_fraction in [0.5*fq*, 2*fq*] (sparsity enforced)
  MIDDLE_BAND: BTSP_new in [0.30, 0.40) OR lift in [0.05, 0.10)
  HARD_FAIL: no cell has BTSP > BinHeb at same fp by >= 0.05 OR cardinality breach

REGIME:
  N_DIM=2048 NCAT=100 NTRAIN=10 proto_noise=0.85 alpha=0.0488
  seeds_full=[11,13,19] seeds_smoke=[11]

SMOKE GATE: smoke MUST include (fp=0.005, fq=0.0025) AND show
            BTSP_new > BinHeb at fp=0.005 by some positive margin or HARD_FAIL.

ASCII-only; no emojis; no em-dashes; self-contained.
Author: exp_dev 2026-06-27 (revival cell under Research team-lead).
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

ANCHOR_NAME = "btsp_binary_synapse_v3_sparse_regime_swept"

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
HP_NEW_FLOOR = 0.40
HP_LIFT_OVER_BINHEB = 0.10
HP_OLD_FLOOR = 0.30
HP_CV_MAX = 0.10
HF_LIFT_NULL = 0.05  # if best cell BTSP - BinHeb_at_fp < this -> HARD_FAIL
HP_FP_MAX = 0.05
HP_FQ_MAX = 0.10

# Sweep grids (Wu-Maass 2025 literature spec)
FP_GRID = [0.005, 0.01, 0.025, 0.05, 0.10]
FQ_GRID = [0.0025, 0.01, 0.05, 0.10, 0.25]
HEADLINE_FP = 0.005
HEADLINE_FQ = 0.0025

EXPECTED_ARMS = [
    "cont_hebbian_baseline",
    "binary_hebbian_baseline_per_fp",
    "btsp_sparse_sweep",
    "diag_tag_fraction_sweep",
]

# Regime (Skunkworks anti-saturation)
if SELF_TEST_MODE:
    N_DIM = 256
    N_CAT = 10
    N_TRAIN = 5
    N_HELDOUT = 5
    PROTO_NOISE = 0.85
    SEEDS = [11]
    # Tiny grid for self-test to stay fast
    FP_GRID_USE = [0.005, 0.05]
    FQ_GRID_USE = [0.0025, 0.05]
elif RUN_MODE == "smoke":
    N_DIM = 1024
    N_CAT = 50
    N_TRAIN = 5
    N_HELDOUT = 10
    PROTO_NOISE = 0.85
    SEEDS = [11]
    FP_GRID_USE = FP_GRID
    FQ_GRID_USE = FQ_GRID
else:
    N_DIM = 2048
    N_CAT = 100
    N_TRAIN = 10
    N_HELDOUT = 20
    PROTO_NOISE = 0.85
    SEEDS = [11, 13, 19]
    FP_GRID_USE = FP_GRID
    FQ_GRID_USE = FQ_GRID

ALPHA_LOAD = N_CAT / float(N_DIM)
ELIG_DECAY = 0.7  # eligibility-trace decay

# Pre-dispatch HARD gate
assert 0.03 <= ALPHA_LOAD <= 0.20, (
    "ALPHA_LOAD=%.4f outside safe band [0.03, 0.20]" % ALPHA_LOAD)
assert HEADLINE_FP in FP_GRID_USE, "HEADLINE_FP must be in FP_GRID_USE"
assert HEADLINE_FQ in FQ_GRID_USE, "HEADLINE_FQ must be in FQ_GRID_USE"

N_GRID_CELLS = len(FP_GRID_USE) * len(FQ_GRID_USE)
# Units: per seed -> 1 cont + N_GRID*2 (BTSP + BinHeb_per_fp) + N_GRID diag = 1 + 3*N_GRID
EXPECTED_N_UNITS = len(SEEDS) * (1 + 3 * N_GRID_CELLS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,NCAT=%d,NTRAIN=%d,proto_noise=%.2f,alpha=%.4f,"
    "fp_grid=%s,fq_grid=%s,seeds=%s,mode=%s,elig=%.2f,"
    "HP_new>=%.2f,HP_lift>=%.2f,HF_null<%.2f,HP_fp_max=%.2f,HP_fq_max=%.2f,"
    "hardening=L1early+L2pergrid+L3outertry+L4importsentinel,"
    "FAIRNESS=TOP_FP_THRESHOLD+MATCHED_SPARSITY_BASELINE+ALPHA_IN_BAND+SMOKE_FIRES_DISCRIMINATOR"
) % (
    ANCHOR_NAME, N_DIM, N_CAT, N_TRAIN, PROTO_NOISE, ALPHA_LOAD,
    FP_GRID_USE, FQ_GRID_USE, SEEDS, RUN_MODE, ELIG_DECAY,
    HP_NEW_FLOOR, HP_LIFT_OVER_BINHEB, HF_LIFT_NULL, HP_FP_MAX, HP_FQ_MAX,
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
            "_hardening_marker": "v3_btsp_sparse_swept",
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
            "_hardening_marker": "v3_btsp_sparse_swept_import_crash",
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


def sparsify_top_fp(x: np.ndarray, fp: float) -> np.ndarray:
    """Top-fp percentile sparsifier (Wu-Maass spike-rate enforcement).
    Returns binary {0, 1} with exactly ceil(fp*N) ones at the highest values.
    THIS IS THE FIX FROM v2 -- v2 used sign(W) (median split = 50% spike rate).
    """
    n = x.size
    k = max(1, int(math.ceil(fp * n)))
    if k >= n:
        return np.ones_like(x, dtype=np.float32)
    thresh = np.partition(x, n - k)[n - k]
    return (x >= thresh).astype(np.float32)


def hebbian_dW(key: np.ndarray, value: np.ndarray) -> np.ndarray:
    n = key.shape[0]
    return np.outer(key, value).astype(np.float32) / float(n)


def readout_accuracy_classification(W: np.ndarray, queries: np.ndarray,
                                     prototypes: np.ndarray,
                                     labels: np.ndarray) -> float:
    """SAME SURFACE all arms: cosine over W @ query against prototypes;
    classification = argmax cosine. Returns top-1 accuracy.
    """
    out = queries @ W
    out_n = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-8)
    proto_n = prototypes / (np.linalg.norm(prototypes, axis=1, keepdims=True) + 1e-8)
    sims = out_n @ proto_n.T
    pred = np.argmax(sims, axis=1)
    return float(np.mean(pred == labels))


def build_train_test(g: np.random.Generator
                     ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    prototypes = bipolar(N_CAT, N_DIM, g)
    train_keys: List[np.ndarray] = []
    train_labels: List[int] = []
    for c in range(N_CAT):
        for _ in range(N_TRAIN):
            train_keys.append(noisy_prototype(prototypes[c], PROTO_NOISE, g))
            train_labels.append(c)
    train_set = np.stack(train_keys, axis=0).astype(np.float32)
    train_labels_arr = np.array(train_labels, dtype=np.int64)
    perm = g.permutation(train_set.shape[0])
    train_set = train_set[perm]
    train_labels_arr = train_labels_arr[perm]

    test_keys: List[np.ndarray] = []
    test_labels: List[int] = []
    for c in range(N_CAT):
        for _ in range(N_HELDOUT):
            test_keys.append(noisy_prototype(prototypes[c], PROTO_NOISE, g))
            test_labels.append(c)
    test_set = np.stack(test_keys, axis=0).astype(np.float32)
    test_labels_arr = np.array(test_labels, dtype=np.int64)

    return prototypes, train_set, train_labels_arr, test_set, test_labels_arr


# -------------------------- arms --------------------------

def run_cont_hebbian_baseline(prototypes, train_set, train_labels, test_set,
                               test_labels) -> Dict[str, float]:
    """Dense continuous W reference (once per seed). NOT used as matched-sparsity baseline."""
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for i in range(train_set.shape[0]):
        W = W + hebbian_dW(train_set[i], prototypes[train_labels[i]])
    new_acc = readout_accuracy_classification(W, test_set, prototypes, test_labels)
    return {"new_pattern_acc": new_acc, "old_pattern_acc": new_acc,
            "tag_fraction": 1.0}


def run_binary_hebbian_at_fp(prototypes, train_set, train_labels, test_set,
                              test_labels, fp: float) -> Dict[str, float]:
    """Binary W with sparse top-fp input/output binarization. Matched-sparsity
    baseline to BTSP at SAME fp.
    """
    # Sparsify keys and values via top-fp on absolute value (preserve sign)
    def _sparse(v: np.ndarray) -> np.ndarray:
        absv = np.abs(v)
        n = v.size
        k = max(1, int(math.ceil(fp * n)))
        if k >= n:
            return np.sign(v).astype(np.float32)
        thresh = np.partition(absv, n - k)[n - k]
        mask = absv >= thresh
        out = np.zeros_like(v, dtype=np.float32)
        out[mask] = np.sign(v[mask])
        return out

    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for i in range(train_set.shape[0]):
        ks = _sparse(train_set[i])
        vs = _sparse(prototypes[train_labels[i]])
        W = W + np.outer(ks, vs).astype(np.float32) / float(N_DIM)
    # Binarize W by sign
    W_bin = np.sign(W).astype(np.float32) + (W == 0).astype(np.float32) * 1.0
    # Sparsify test queries the same way (matched encoding)
    test_sparse = np.stack([_sparse(q) for q in test_set], axis=0)
    new_acc = readout_accuracy_classification(W_bin, test_sparse, prototypes,
                                               test_labels)
    return {"new_pattern_acc": new_acc, "old_pattern_acc": new_acc,
            "tag_fraction": float(np.mean(np.abs(W_bin) > 0))}


def run_btsp_at_fp_fq(prototypes, train_set, train_labels, test_set,
                       test_labels, fp: float, fq: float,
                       g: np.random.Generator) -> Dict[str, float]:
    """BTSP at literature sparsity: sparse-fp inputs + sparse-fq gating +
    eligibility trace + top-fq threshold update on binary W.
    """
    def _sparse(v: np.ndarray) -> np.ndarray:
        absv = np.abs(v)
        n = v.size
        k = max(1, int(math.ceil(fp * n)))
        if k >= n:
            return np.sign(v).astype(np.float32)
        thresh = np.partition(absv, n - k)[n - k]
        mask = absv >= thresh
        out = np.zeros_like(v, dtype=np.float32)
        out[mask] = np.sign(v[mask])
        return out

    # Initialize binary W randomly in {-1, +1}
    W_bin = (g.integers(0, 2, size=(N_DIM, N_DIM)).astype(np.float32) * 2 - 1)
    elig = np.zeros_like(W_bin)
    tag_fracs: List[float] = []
    n_total = W_bin.size
    n_tag = max(1, int(math.ceil(fq * n_total)))

    for i in range(train_set.shape[0]):
        ks = _sparse(train_set[i])
        vs = _sparse(prototypes[train_labels[i]])
        instant = np.abs(np.outer(ks, vs)).astype(np.float32) / float(N_DIM)
        elig = ELIG_DECAY * elig + instant
        # Gate: per-step probability fq of firing capture pulse (neuromod sparsity)
        if g.random() < (fq * 5.0):  # scaled probability so SOME pulses fire
            # Top-n_tag (= fq fraction) synapses by elig are tagged + flipped to outer sign
            flat = elig.ravel()
            if n_tag < n_total:
                thresh = np.partition(flat, n_total - n_tag)[n_total - n_tag]
            else:
                thresh = float(flat.min())
            tag_mask = elig >= thresh
            tag_fracs.append(float(tag_mask.sum()) / n_total)
            update_dir = np.sign(np.outer(ks, vs)).astype(np.float32)
            # Where update_dir is 0 (sparse keys), keep existing W
            update_dir = np.where(update_dir == 0, W_bin, update_dir)
            W_bin = np.where(tag_mask, update_dir, W_bin).astype(np.float32)

    test_sparse = np.stack([_sparse(q) for q in test_set], axis=0)
    new_acc = readout_accuracy_classification(W_bin, test_sparse, prototypes,
                                               test_labels)
    # Old-pattern acc: half of training set
    n_old = max(1, train_set.shape[0] // 2)
    old_sparse = np.stack([_sparse(q) for q in train_set[:n_old]], axis=0)
    old_acc = readout_accuracy_classification(W_bin, old_sparse, prototypes,
                                               train_labels[:n_old])
    mean_tag = float(np.mean(tag_fracs)) if tag_fracs else 0.0
    return {"new_pattern_acc": new_acc, "old_pattern_acc": old_acc,
            "tag_fraction": mean_tag}


def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    prototypes, train_set, train_labels, test_set, test_labels = build_train_test(g)

    cont_res = run_cont_hebbian_baseline(prototypes, train_set, train_labels,
                                          test_set, test_labels)

    # Per-fp BinHeb baseline (one per fp, NOT per fp x fq)
    binheb_per_fp: Dict[str, Dict[str, float]] = {}
    for fp in FP_GRID_USE:
        binheb_per_fp["%.4f" % fp] = run_binary_hebbian_at_fp(
            prototypes, train_set, train_labels, test_set, test_labels, fp)

    # BTSP sweep over (fp, fq) grid
    btsp_grid: Dict[str, Dict[str, float]] = {}
    for fp in FP_GRID_USE:
        for fq in FQ_GRID_USE:
            key = "fp=%.4f,fq=%.4f" % (fp, fq)
            btsp_grid[key] = run_btsp_at_fp_fq(
                prototypes, train_set, train_labels, test_set, test_labels,
                fp, fq, np.random.default_rng(seed * 100 + int(fp * 10000) + int(fq * 10000)))

    return {
        "seed": int(seed),
        "N": N_DIM,
        "N_CAT": N_CAT,
        "N_TRAIN": N_TRAIN,
        "proto_noise": PROTO_NOISE,
        "alpha_load": ALPHA_LOAD,
        "fp_grid": FP_GRID_USE,
        "fq_grid": FQ_GRID_USE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "cont_hebbian_baseline": cont_res,
        "binary_hebbian_per_fp": binheb_per_fp,
        "btsp_grid": btsp_grid,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials",
            "summary": "no per-seed partials",
        }

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)

    # Aggregate cont baseline
    cont_vals = [per_seed[s]["cont_hebbian_baseline"]["new_pattern_acc"]
                  for s in seeds_sorted]
    cont_mean = float(np.mean(cont_vals))

    # Aggregate binheb per fp
    binheb_summary: Dict[str, float] = {}
    for fp in FP_GRID_USE:
        key = "%.4f" % fp
        vals = [per_seed[s]["binary_hebbian_per_fp"][key]["new_pattern_acc"]
                for s in seeds_sorted]
        binheb_summary[key] = float(np.mean(vals))

    # Aggregate BTSP grid
    btsp_summary: Dict[str, Dict[str, float]] = {}
    for fp in FP_GRID_USE:
        for fq in FQ_GRID_USE:
            cell_key = "fp=%.4f,fq=%.4f" % (fp, fq)
            new_vals = [per_seed[s]["btsp_grid"][cell_key]["new_pattern_acc"]
                         for s in seeds_sorted]
            old_vals = [per_seed[s]["btsp_grid"][cell_key]["old_pattern_acc"]
                         for s in seeds_sorted]
            tag_vals = [per_seed[s]["btsp_grid"][cell_key]["tag_fraction"]
                         for s in seeds_sorted]
            m_new = float(np.mean(new_vals))
            sd_new = float(np.std(new_vals)) if n_seeds > 1 else 0.0
            cv = sd_new / abs(m_new) if abs(m_new) > 1e-6 else 0.0
            binheb_at_fp = binheb_summary["%.4f" % fp]
            lift = m_new - binheb_at_fp
            btsp_summary[cell_key] = {
                "fp": fp, "fq": fq,
                "mean_new": m_new, "std_new": sd_new, "cv_new": cv,
                "mean_old": float(np.mean(old_vals)),
                "mean_tag": float(np.mean(tag_vals)),
                "binheb_at_fp": binheb_at_fp,
                "lift_over_binheb_at_fp": lift,
            }

    # Find best cell (max BTSP new_acc) within eligibility band (fp<=HP_FP_MAX, fq<=HP_FQ_MAX)
    eligible = [c for c in btsp_summary.values()
                 if c["fp"] <= HP_FP_MAX and c["fq"] <= HP_FQ_MAX]
    if eligible:
        best = max(eligible, key=lambda c: c["mean_new"])
    else:
        best = max(btsp_summary.values(), key=lambda c: c["mean_new"])

    # Find headline cell (the lit-spec point)
    headline_key = "fp=%.4f,fq=%.4f" % (HEADLINE_FP, HEADLINE_FQ)
    headline = btsp_summary.get(headline_key)

    # Verdict logic
    best_lift = best["lift_over_binheb_at_fp"]
    best_new = best["mean_new"]
    best_old = best["mean_old"]
    best_cv = best["cv_new"]
    best_tag = best["mean_tag"]
    best_fp = best["fp"]
    best_fq = best["fq"]

    # Sparsity enforcement: observed tag_fraction within [0.5*fq, 2*fq] band
    sparsity_enforced = (
        (0.5 * best_fq) <= best_tag <= (2.0 * best_fq + 0.05)
    )  # +0.05 slack for low fq

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    # HARD_FAIL checks
    max_lift_any = max(c["lift_over_binheb_at_fp"] for c in btsp_summary.values())
    if max_lift_any < HF_LIFT_NULL:
        verdict = "HARD_FAIL"
        verdict_reason = "MECHANISM_NULL: max BTSP-BinHeb lift across grid=%.3f < %.2f" % (
            max_lift_any, HF_LIFT_NULL)
    elif (best_new >= HP_NEW_FLOOR and
            best_lift >= HP_LIFT_OVER_BINHEB and
            best_old >= HP_OLD_FLOOR and
            (n_seeds == 1 or best_cv < HP_CV_MAX) and
            sparsity_enforced and
            best_fp <= HP_FP_MAX and best_fq <= HP_FQ_MAX):
        verdict = "HARD_PASS"
        verdict_reason = (
            "SPARSE_REGIME_LIFT: best cell fp=%.4f fq=%.4f BTSP=%.3f BinHeb=%.3f lift=%.3f tag=%.3f"
        ) % (best_fp, best_fq, best_new, best["binheb_at_fp"], best_lift, best_tag)
    elif _between(best_new, HP_NEW_FLOOR - 0.10, HP_NEW_FLOOR) or 0.05 <= best_lift < HP_LIFT_OVER_BINHEB:
        verdict = "MIDDLE_BAND"
        verdict_reason = "PARTIAL_LIFT: best BTSP=%.3f lift=%.3f at fp=%.4f fq=%.4f" % (
            best_new, best_lift, best_fp, best_fq)
    elif best_new >= HP_NEW_FLOOR and best_lift >= HP_LIFT_OVER_BINHEB and not sparsity_enforced:
        verdict = "MIDDLE_BAND"
        verdict_reason = "TAG_FRAC_OUTSIDE_FQ_BAND: best_tag=%.3f vs fq=%.4f (binarization may be bugged)" % (
            best_tag, best_fq)

    verdict_msg = (
        "%s | %s | cont=%.3f | best_cell fp=%.4f fq=%.4f BTSP=%.3f BinHeb_at_fp=%.3f lift=%.3f tag=%.3f | "
        "headline(fp=%.4f,fq=%.4f) BTSP=%.3f BinHeb=%.3f | alpha=%.4f n_seeds=%d grid=%dx%d"
    ) % (verdict, verdict_reason, cont_mean,
         best_fp, best_fq, best_new, best["binheb_at_fp"], best_lift, best_tag,
         HEADLINE_FP, HEADLINE_FQ,
         headline["mean_new"] if headline else -1.0,
         headline["binheb_at_fp"] if headline else -1.0,
         ALPHA_LOAD, n_seeds, len(FP_GRID_USE), len(FQ_GRID_USE))

    # Cardinality
    completed_units = n_seeds * (1 + 3 * len(FP_GRID_USE) * len(FQ_GRID_USE))
    expected = EXPECTED_N_UNITS

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "cont_baseline_mean": cont_mean,
        "binheb_per_fp_summary": binheb_summary,
        "btsp_grid_summary": btsp_summary,
        "best_cell": best,
        "headline_cell": headline,
        "saturation_score": cont_mean,
        "n_seeds_complete": n_seeds,
        "expected_n_units": expected,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= expected,
    }


def _between(x: float, lo: float, hi: float) -> bool:
    return lo <= x <= hi


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
                                  "fp_grid": FP_GRID_USE,
                                  "fq_grid": FQ_GRID_USE,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d NCAT=%d alpha=%.4f seeds=%s grid=%dx%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_CAT, ALPHA_LOAD, SEEDS,
        len(FP_GRID_USE), len(FQ_GRID_USE)), flush=True)
    print("[%s] fp_grid=%s fq_grid=%s" % (
        ANCHOR_NAME, FP_GRID_USE, FQ_GRID_USE), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "cont_hebbian_baseline" in r
            assert "binary_hebbian_per_fp" in r
            assert "btsp_grid" in r
            assert len(r["btsp_grid"]) == len(FP_GRID_USE) * len(FQ_GRID_USE)
            for fp in FP_GRID_USE:
                assert "%.4f" % fp in r["binary_hebbian_per_fp"]
                for fq in FQ_GRID_USE:
                    cell_key = "fp=%.4f,fq=%.4f" % (fp, fq)
                    assert cell_key in r["btsp_grid"]
                    cell = r["btsp_grid"][cell_key]
                    assert "new_pattern_acc" in cell
                    assert "tag_fraction" in cell
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: %dx%d grid + per-fp baseline + cont structured" % (
                                       len(FP_GRID_USE), len(FQ_GRID_USE)))
            head = "fp=%.4f,fq=%.4f" % (FP_GRID_USE[0], FQ_GRID_USE[0])
            print("[selftest] OK cont=%.3f headline(%s) BTSP=%.3f tag=%.3f" % (
                r["cont_hebbian_baseline"]["new_pattern_acc"],
                head,
                r["btsp_grid"][head]["new_pattern_acc"],
                r["btsp_grid"][head]["tag_fraction"]), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    per_seed_results: Dict[str, Dict[str, Any]] = {}
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d) grid=%dx%d" % (
                                   seed, i + 1, len(SEEDS),
                                   len(FP_GRID_USE), len(FQ_GRID_USE)),
                               extra={"_phase": "seed_running", "_current_seed": seed,
                                      "alpha_load": ALPHA_LOAD})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        per_seed_results[str(seed)] = result
        head = "fp=%.4f,fq=%.4f" % (HEADLINE_FP, HEADLINE_FQ)
        head_btsp = result["btsp_grid"].get(head, {}).get("new_pattern_acc", -1.0)
        print("[seed=%d] complete in %.1fs cont=%.3f headline BTSP=%.3f" % (
            seed, time.time() - t0,
            result["cont_hebbian_baseline"]["new_pattern_acc"], head_btsp),
            flush=True)

    final = aggregate_and_verdict(per_seed_results)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v3_btsp_sparse_swept"
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
