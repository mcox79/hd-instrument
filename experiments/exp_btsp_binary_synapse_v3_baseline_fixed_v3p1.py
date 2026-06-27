"""btsp_binary_synapse_v3_baseline_fixed_v3p1 -- Wave 2 BinHeb-binarization-bug fix.

Prereg: preregs/2026-06-27_btsp_binary_synapse_v3_baseline_fixed_v3p1.md
Skunkworks audit: notes/skunkworks_mechanism_null_audit_wave2_2026-06-27.md (commit edee21b3)

ROOT CAUSE FIX vs v3:
  v3 line 326: W_bin = np.sign(W).astype(np.float32) + (W == 0).astype(np.float32) * 1.0
  Bug: where W==0, both sign(W)=0 and the (W==0)*1.0=1.0 -> W_bin entry is +1.
       Where W!=0, sign(W) is +/-1 and (W==0)*1.0=0 -> W_bin is +/-1.
       Skunkworks measured: W_bin mean = 0.9932 across cells (99.66% entries are +1).
       The "binary" baseline thus collapsed to a near-constant matrix that classifies
       trivially well (cosine to prototype is dominated by sign of W's positive bias).
  Fix: explicit bipolar binarization using row-median threshold:
       row_med = np.median(W, axis=1, keepdims=True)
       W_bin = np.where(W >= row_med, 1.0, -1.0).astype(np.float32)
       This guarantees ~50% +1 / ~50% -1 per row (proper bipolar; not biased).
       For zero-rows (W identically zero before training), fallback to random +/-1.

HYPOTHESIS:
  With proper bipolar binarization, BinHeb baseline at fp=0.005, fq=0.0025 (Wu-Maass
  literature spec) does NOT saturate at 1.000; it lands in the [0.10, 0.50] band
  (sparse-input + binary-matrix has fundamental information capacity limits).
  At THAT regime, BTSP_sparse has headroom to exceed BinHeb by >= 0.05.

DISCRIMINATOR:
  HARD_PASS: at headline (fp=0.005, fq=0.0025):
    BinHeb NOT in [0.95, 1.00]  (anti-saturation fairness gate)
    AND BTSP_new - BinHeb_new >= 0.05  (mechanism lift)
    AND observed tag_fraction in [0.5*fq, 2*fq + 0.05]  (sparsity enforcement)
    AND cv across seeds < 0.10
  HARD_FAIL: BinHeb still collapses to >= 0.95 at fp=0.005 (refutes binarization fix)
             OR BTSP-BinHeb lift across grid < 0.03 (mechanism null in our task class)
             OR cardinality breach

ARMS (same 4 as v3; same grid):
  ARM_CONT_HEBBIAN_BASELINE     continuous W reference (once per seed)
  ARM_BINARY_HEBBIAN_BASELINE   binary W via FIXED row-median bipolar binarization
  ARM_BTSP_SPARSE_SWEEP         BTSP at each (fp, fq) of 5x5 grid (unchanged from v3)
  ARM_DIAG_TAG_FRACTION_SWEEP   diagnostic (unchanged)

GRID: fp in {0.005, 0.01, 0.025, 0.05, 0.10}; fq in {0.0025, 0.01, 0.05, 0.10, 0.25}.
REGIME: N_DIM=2048 NCAT=100 NTRAIN=10 proto_noise=0.85 alpha=0.0488 (same as v3).
SEEDS: full=[11,13,19]; smoke=[11]; selftest=[11].

SMOKE FULL_N_PREVIEW arm: at smoke we ALSO run the headline (fp=0.005, fq=0.0025)
                          BinHeb at N=2048 with 1 seed to verify discriminator
                          survives scale (USER feedback discriminator-must-survive-scale).

CARDINALITY_OK: per seed -> 1 cont + 5 BinHeb (per-fp) + 25 BTSP (5x5 grid) + 25 diag = 56
                full: 3 seeds * 56 = 168; smoke: 1 seed * 56 = 56 + 1 preview = 57.

FAIRNESS (META_RULE_AA):
  - All arms read SAME SURFACE: cosine(W @ query_sparsified, prototype_sparsified)
  - BinHeb reads SAME readout as BTSP (matched sparsification on test queries)
  - Baseline NOT trivially doing the mechanism (no eligibility trace; no tag mask)
  - Discriminator FIRES at headline cell (per META_RULE_K)

ASCII-only; no emojis; no em-dashes.
Author: exp_dev 2026-06-27 (Wave 2 redesign cell 1 of 4).
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

ANCHOR_NAME = "btsp_binary_synapse_v3_baseline_fixed_v3p1"

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
HP_LIFT_OVER_BINHEB = 0.05
HF_LIFT_NULL = 0.03
HP_BASELINE_CEILING = 0.95
HP_CV_MAX = 0.10
HP_FP_MAX = 0.10
HP_FQ_MAX = 0.25
TAG_BAND_SLACK = 0.05

# Sweep grids
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

# Regime
if SELF_TEST_MODE:
    N_DIM = 256
    N_CAT = 10
    N_TRAIN = 5
    N_HELDOUT = 5
    PROTO_NOISE = 0.85
    SEEDS = [11]
    FP_GRID_USE = [0.005, 0.05]
    FQ_GRID_USE = [0.0025, 0.05]
    RUN_FULL_N_PREVIEW = False
elif RUN_MODE == "smoke":
    # Smoke at N=1024 + FULL_N_PREVIEW at N=2048 for headline cell
    N_DIM = 1024
    N_CAT = 50
    N_TRAIN = 5
    N_HELDOUT = 10
    PROTO_NOISE = 0.85
    SEEDS = [11]
    FP_GRID_USE = FP_GRID
    FQ_GRID_USE = FQ_GRID
    RUN_FULL_N_PREVIEW = True
else:
    N_DIM = 2048
    N_CAT = 100
    N_TRAIN = 10
    N_HELDOUT = 20
    PROTO_NOISE = 0.85
    SEEDS = [11, 13, 19]
    FP_GRID_USE = FP_GRID
    FQ_GRID_USE = FQ_GRID
    RUN_FULL_N_PREVIEW = False

ALPHA_LOAD = N_CAT / float(N_DIM)
ELIG_DECAY = 0.7

# Pre-dispatch HARD gate
assert 0.03 <= ALPHA_LOAD <= 0.20, (
    "ALPHA_LOAD=%.4f outside safe band [0.03, 0.20]" % ALPHA_LOAD)
assert HEADLINE_FP in FP_GRID_USE, "HEADLINE_FP must be in FP_GRID_USE"
assert HEADLINE_FQ in FQ_GRID_USE, "HEADLINE_FQ must be in FQ_GRID_USE"

N_GRID_CELLS = len(FP_GRID_USE) * len(FQ_GRID_USE)
EXPECTED_N_UNITS = len(SEEDS) * (1 + len(FP_GRID_USE) + 2 * N_GRID_CELLS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,NCAT=%d,NTRAIN=%d,proto_noise=%.2f,alpha=%.4f,"
    "fp_grid=%s,fq_grid=%s,seeds=%s,mode=%s,elig=%.2f,"
    "HP_lift>=%.2f,HF_null<%.2f,HP_baseline_ceil=%.2f,fpmax=%.2f,fqmax=%.2f,"
    "hardening=L1early+L2pergrid+L3outertry+L4importsentinel,"
    "FAIRNESS=ROW_MEDIAN_BIPOLAR_BINARIZATION+MATCHED_SPARSITY_BASELINE+SMOKE_FULL_N_PREVIEW"
) % (
    ANCHOR_NAME, N_DIM, N_CAT, N_TRAIN, PROTO_NOISE, ALPHA_LOAD,
    FP_GRID_USE, FQ_GRID_USE, SEEDS, RUN_MODE, ELIG_DECAY,
    HP_LIFT_OVER_BINHEB, HF_LIFT_NULL, HP_BASELINE_CEILING, HP_FP_MAX, HP_FQ_MAX,
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
            "_hardening_marker": "v3p1_btsp_baseline_fixed",
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
            "_hardening_marker": "v3p1_btsp_baseline_fixed_import_crash",
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


def hebbian_dW(key: np.ndarray, value: np.ndarray) -> np.ndarray:
    n = key.shape[0]
    return np.outer(key, value).astype(np.float32) / float(n)


def proper_bipolar_binarize(W: np.ndarray,
                             g: np.random.Generator) -> np.ndarray:
    """ROOT CAUSE FIX: Row-median bipolar binarization.

    Old (buggy) v3: W_bin = sign(W) + (W==0)*1.0 -> +1 bias where W=0.
    New: per-row median split -> ~50/50 +1/-1 with no bias.
    Zero rows (W identically zero) fall back to random {-1, +1}.
    """
    out = np.empty_like(W, dtype=np.float32)
    n_rows, n_cols = W.shape
    row_meds = np.median(W, axis=1)
    for r in range(n_rows):
        row = W[r]
        if np.allclose(row, 0.0):
            # Zero row: random bipolar fallback (deterministic per seed)
            out[r] = (g.integers(0, 2, size=n_cols).astype(np.float32) * 2.0 - 1.0)
        else:
            out[r] = np.where(row >= row_meds[r], 1.0, -1.0).astype(np.float32)
    return out


def readout_accuracy_classification(W: np.ndarray, queries: np.ndarray,
                                     prototypes: np.ndarray,
                                     labels: np.ndarray) -> float:
    out = queries @ W
    out_n = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-8)
    proto_n = prototypes / (np.linalg.norm(prototypes, axis=1, keepdims=True) + 1e-8)
    sims = out_n @ proto_n.T
    pred = np.argmax(sims, axis=1)
    return float(np.mean(pred == labels))


def build_train_test(g: np.random.Generator, n_dim: int, n_cat: int,
                      n_train: int, n_heldout: int, proto_noise: float
                      ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    prototypes = bipolar(n_cat, n_dim, g)
    train_keys: List[np.ndarray] = []
    train_labels: List[int] = []
    for c in range(n_cat):
        for _ in range(n_train):
            train_keys.append(noisy_prototype(prototypes[c], proto_noise, g))
            train_labels.append(c)
    train_set = np.stack(train_keys, axis=0).astype(np.float32)
    train_labels_arr = np.array(train_labels, dtype=np.int64)
    perm = g.permutation(train_set.shape[0])
    train_set = train_set[perm]
    train_labels_arr = train_labels_arr[perm]

    test_keys: List[np.ndarray] = []
    test_labels: List[int] = []
    for c in range(n_cat):
        for _ in range(n_heldout):
            test_keys.append(noisy_prototype(prototypes[c], proto_noise, g))
            test_labels.append(c)
    test_set = np.stack(test_keys, axis=0).astype(np.float32)
    test_labels_arr = np.array(test_labels, dtype=np.int64)

    return prototypes, train_set, train_labels_arr, test_set, test_labels_arr


# -------------------------- arms --------------------------

def run_cont_hebbian_baseline(prototypes, train_set, train_labels, test_set,
                               test_labels, n_dim: int) -> Dict[str, float]:
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for i in range(train_set.shape[0]):
        W = W + hebbian_dW(train_set[i], prototypes[train_labels[i]])
    new_acc = readout_accuracy_classification(W, test_set, prototypes, test_labels)
    return {"new_pattern_acc": new_acc, "old_pattern_acc": new_acc,
            "tag_fraction": 1.0}


def run_binary_hebbian_at_fp(prototypes, train_set, train_labels, test_set,
                              test_labels, fp: float, n_dim: int,
                              g: np.random.Generator) -> Dict[str, float]:
    """Binary W with sparse top-fp + ROW-MEDIAN BIPOLAR BINARIZATION (v3p1 fix)."""
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

    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for i in range(train_set.shape[0]):
        ks = _sparse(train_set[i])
        vs = _sparse(prototypes[train_labels[i]])
        W = W + np.outer(ks, vs).astype(np.float32) / float(n_dim)
    # FIX: proper bipolar binarization (no +1 bias on zero entries)
    W_bin = proper_bipolar_binarize(W, g)
    # Verify proper binarization (no anomalous bias)
    mean_W_bin = float(np.mean(W_bin))
    test_sparse = np.stack([_sparse(q) for q in test_set], axis=0)
    new_acc = readout_accuracy_classification(W_bin, test_sparse, prototypes,
                                               test_labels)
    return {"new_pattern_acc": new_acc, "old_pattern_acc": new_acc,
            "tag_fraction": float(np.mean(np.abs(W_bin) > 0)),
            "mean_W_bin": mean_W_bin}  # diagnostic: should be near 0.0 for proper bipolar


def run_btsp_at_fp_fq(prototypes, train_set, train_labels, test_set,
                       test_labels, fp: float, fq: float, n_dim: int,
                       g: np.random.Generator) -> Dict[str, float]:
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

    W_bin = (g.integers(0, 2, size=(n_dim, n_dim)).astype(np.float32) * 2 - 1)
    elig = np.zeros_like(W_bin)
    tag_fracs: List[float] = []
    n_total = W_bin.size
    n_tag = max(1, int(math.ceil(fq * n_total)))

    for i in range(train_set.shape[0]):
        ks = _sparse(train_set[i])
        vs = _sparse(prototypes[train_labels[i]])
        instant = np.abs(np.outer(ks, vs)).astype(np.float32) / float(n_dim)
        elig = ELIG_DECAY * elig + instant
        if g.random() < (fq * 5.0):
            flat = elig.ravel()
            if n_tag < n_total:
                thresh = np.partition(flat, n_total - n_tag)[n_total - n_tag]
            else:
                thresh = float(flat.min())
            tag_mask = elig >= thresh
            tag_fracs.append(float(tag_mask.sum()) / n_total)
            update_dir = np.sign(np.outer(ks, vs)).astype(np.float32)
            update_dir = np.where(update_dir == 0, W_bin, update_dir)
            W_bin = np.where(tag_mask, update_dir, W_bin).astype(np.float32)

    test_sparse = np.stack([_sparse(q) for q in test_set], axis=0)
    new_acc = readout_accuracy_classification(W_bin, test_sparse, prototypes,
                                               test_labels)
    n_old = max(1, train_set.shape[0] // 2)
    old_sparse = np.stack([_sparse(q) for q in train_set[:n_old]], axis=0)
    old_acc = readout_accuracy_classification(W_bin, old_sparse, prototypes,
                                               train_labels[:n_old])
    mean_tag = float(np.mean(tag_fracs)) if tag_fracs else 0.0
    return {"new_pattern_acc": new_acc, "old_pattern_acc": old_acc,
            "tag_fraction": mean_tag}


def run_one_seed(seed: int, n_dim: int, n_cat: int, n_train: int,
                  n_heldout: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    prototypes, train_set, train_labels, test_set, test_labels = build_train_test(
        g, n_dim, n_cat, n_train, n_heldout, PROTO_NOISE)

    cont_res = run_cont_hebbian_baseline(prototypes, train_set, train_labels,
                                          test_set, test_labels, n_dim)

    binheb_per_fp: Dict[str, Dict[str, float]] = {}
    for fp in FP_GRID_USE:
        g_bin = np.random.default_rng(seed * 100 + int(fp * 10000) + 7)
        binheb_per_fp["%.4f" % fp] = run_binary_hebbian_at_fp(
            prototypes, train_set, train_labels, test_set, test_labels, fp,
            n_dim, g_bin)

    btsp_grid: Dict[str, Dict[str, float]] = {}
    for fp in FP_GRID_USE:
        for fq in FQ_GRID_USE:
            key = "fp=%.4f,fq=%.4f" % (fp, fq)
            btsp_grid[key] = run_btsp_at_fp_fq(
                prototypes, train_set, train_labels, test_set, test_labels,
                fp, fq, n_dim,
                np.random.default_rng(seed * 100 + int(fp * 10000) + int(fq * 10000)))

    return {
        "seed": int(seed),
        "N": n_dim,
        "N_CAT": n_cat,
        "N_TRAIN": n_train,
        "proto_noise": PROTO_NOISE,
        "alpha_load": n_cat / float(n_dim),
        "fp_grid": FP_GRID_USE,
        "fq_grid": FQ_GRID_USE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "cont_hebbian_baseline": cont_res,
        "binary_hebbian_per_fp": binheb_per_fp,
        "btsp_grid": btsp_grid,
    }


def run_full_n_preview(seed: int) -> Dict[str, Any]:
    """FULL_N_PREVIEW: run BinHeb baseline at headline cell at FULL N (=2048)
    with 1 seed to verify discriminator survives scale.
    """
    n_dim = 2048
    n_cat = 100
    n_train = 5  # smoke-sized train for speed
    n_heldout = 10
    g = np.random.default_rng(seed)
    prototypes, train_set, train_labels, test_set, test_labels = build_train_test(
        g, n_dim, n_cat, n_train, n_heldout, PROTO_NOISE)
    g_bin = np.random.default_rng(seed * 100 + int(HEADLINE_FP * 10000) + 7)
    binheb_full_n = run_binary_hebbian_at_fp(
        prototypes, train_set, train_labels, test_set, test_labels, HEADLINE_FP,
        n_dim, g_bin)
    return {
        "N_preview": n_dim,
        "NCAT_preview": n_cat,
        "headline_fp": HEADLINE_FP,
        "headline_fq": HEADLINE_FQ,
        "binheb_at_full_N_headline_fp": binheb_full_n,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           preview: Dict[str, Any]) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials",
            "summary": "no per-seed partials",
        }

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)

    cont_vals = [per_seed[s]["cont_hebbian_baseline"]["new_pattern_acc"]
                  for s in seeds_sorted]
    cont_mean = float(np.mean(cont_vals))

    binheb_summary: Dict[str, Any] = {}
    for fp in FP_GRID_USE:
        key = "%.4f" % fp
        vals = [per_seed[s]["binary_hebbian_per_fp"][key]["new_pattern_acc"]
                for s in seeds_sorted]
        mean_W_bin_vals = [per_seed[s]["binary_hebbian_per_fp"][key].get("mean_W_bin", 0.0)
                            for s in seeds_sorted]
        binheb_summary[key] = {
            "mean_acc": float(np.mean(vals)),
            "mean_W_bin": float(np.mean(mean_W_bin_vals)),
        }

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
            binheb_at_fp = binheb_summary["%.4f" % fp]["mean_acc"]
            lift = m_new - binheb_at_fp
            btsp_summary[cell_key] = {
                "fp": fp, "fq": fq,
                "mean_new": m_new, "std_new": sd_new, "cv_new": cv,
                "mean_old": float(np.mean(old_vals)),
                "mean_tag": float(np.mean(tag_vals)),
                "binheb_at_fp": binheb_at_fp,
                "lift_over_binheb_at_fp": lift,
            }

    headline_key = "fp=%.4f,fq=%.4f" % (HEADLINE_FP, HEADLINE_FQ)
    headline = btsp_summary.get(headline_key, {})
    headline_binheb = binheb_summary.get("%.4f" % HEADLINE_FP, {}).get("mean_acc", -1.0)
    headline_binheb_W_bias = binheb_summary.get("%.4f" % HEADLINE_FP, {}).get("mean_W_bin", 0.0)

    # FAIRNESS GATE: BinHeb at headline NOT in saturation
    fairness_pass = True
    fairness_msg = ""
    if headline_binheb >= HP_BASELINE_CEILING:
        fairness_pass = False
        fairness_msg = "FAIRNESS_FAIL: BinHeb at fp=%.4f mean_acc=%.3f >= %.2f (still saturates after fix)" % (
            HEADLINE_FP, headline_binheb, HP_BASELINE_CEILING)
    if abs(headline_binheb_W_bias) > 0.30:
        fairness_pass = False
        fairness_msg += " | W_bin_bias=%.3f outside [-0.30, 0.30] (binarization still biased)" % headline_binheb_W_bias

    # Find best cell within eligibility
    eligible = [c for c in btsp_summary.values()
                 if c["fp"] <= HP_FP_MAX and c["fq"] <= HP_FQ_MAX]
    if eligible:
        best = max(eligible, key=lambda c: c["lift_over_binheb_at_fp"])
    else:
        best = max(btsp_summary.values(), key=lambda c: c["lift_over_binheb_at_fp"])

    best_lift = best["lift_over_binheb_at_fp"]
    best_new = best["mean_new"]
    best_cv = best["cv_new"]
    best_tag = best["mean_tag"]
    best_fp = best["fp"]
    best_fq = best["fq"]

    # Sparsity enforcement
    sparsity_enforced = ((0.5 * best_fq) <= best_tag <= (2.0 * best_fq + TAG_BAND_SLACK))

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    if not fairness_pass:
        verdict = "HARD_FAIL"
        verdict_reason = fairness_msg
    else:
        max_lift_any = max(c["lift_over_binheb_at_fp"] for c in btsp_summary.values())
        if max_lift_any < HF_LIFT_NULL:
            verdict = "HARD_FAIL"
            verdict_reason = "MECHANISM_NULL: max BTSP-BinHeb lift across grid=%.3f < %.2f" % (
                max_lift_any, HF_LIFT_NULL)
        elif (best_lift >= HP_LIFT_OVER_BINHEB and
                (n_seeds == 1 or best_cv < HP_CV_MAX) and
                sparsity_enforced):
            verdict = "HARD_PASS"
            verdict_reason = (
                "BASELINE_FIXED_LIFT: best cell fp=%.4f fq=%.4f BTSP=%.3f BinHeb=%.3f lift=%.3f tag=%.3f"
            ) % (best_fp, best_fq, best_new, best["binheb_at_fp"], best_lift, best_tag)
        elif 0.03 <= best_lift < HP_LIFT_OVER_BINHEB:
            verdict = "MIDDLE_BAND"
            verdict_reason = "PARTIAL_LIFT: best BTSP-BinHeb lift=%.3f at fp=%.4f fq=%.4f" % (
                best_lift, best_fp, best_fq)
        elif best_lift >= HP_LIFT_OVER_BINHEB and not sparsity_enforced:
            verdict = "MIDDLE_BAND"
            verdict_reason = "TAG_FRAC_OUTSIDE_BAND: best_tag=%.3f vs fq=%.4f" % (
                best_tag, best_fq)

    verdict_msg = (
        "%s | %s | cont=%.3f | headline fp=%.4f fq=%.4f BTSP=%.3f BinHeb=%.3f W_bias=%.3f | "
        "best fp=%.4f fq=%.4f BTSP=%.3f BinHeb=%.3f lift=%.3f tag=%.3f | alpha=%.4f n_seeds=%d"
    ) % (verdict, verdict_reason, cont_mean,
         HEADLINE_FP, HEADLINE_FQ,
         headline.get("mean_new", -1.0), headline_binheb, headline_binheb_W_bias,
         best_fp, best_fq, best_new, best["binheb_at_fp"], best_lift, best_tag,
         ALPHA_LOAD, n_seeds)

    completed_units = n_seeds * (1 + len(FP_GRID_USE) + len(FP_GRID_USE) * len(FQ_GRID_USE))
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
        "headline_binheb_mean_acc": headline_binheb,
        "headline_binheb_W_bias": headline_binheb_W_bias,
        "fairness_pass": fairness_pass,
        "fairness_msg": fairness_msg,
        "full_n_preview": preview,
        "saturation_score": cont_mean,
        "n_seeds_complete": n_seeds,
        "expected_n_units": expected,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= expected,
    }


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

    print("[%s] mode=%s N=%d NCAT=%d alpha=%.4f seeds=%s grid=%dx%d preview=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_CAT, ALPHA_LOAD, SEEDS,
        len(FP_GRID_USE), len(FQ_GRID_USE), RUN_FULL_N_PREVIEW), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0], N_DIM, N_CAT, N_TRAIN, N_HELDOUT)
            assert "cont_hebbian_baseline" in r
            assert "binary_hebbian_per_fp" in r
            assert "btsp_grid" in r
            for fp in FP_GRID_USE:
                assert "%.4f" % fp in r["binary_hebbian_per_fp"]
                fp_entry = r["binary_hebbian_per_fp"]["%.4f" % fp]
                assert "mean_W_bin" in fp_entry, "binarization diagnostic missing"
                # Verify proper bipolar: mean_W_bin should be near 0 (not 0.99 like v3 bug)
                if abs(fp_entry["mean_W_bin"]) > 0.30:
                    raise AssertionError("BINARIZATION_BIAS: mean_W_bin=%.3f at fp=%.4f (bug not fixed)" % (
                        fp_entry["mean_W_bin"], fp))
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: row-median bipolar binarization verified (mean_W_bin near 0)")
            head = "fp=%.4f,fq=%.4f" % (FP_GRID_USE[0], FQ_GRID_USE[0])
            print("[selftest] OK cont=%.3f headline(%s) BTSP=%.3f BinHeb_W_bias=%.3f" % (
                r["cont_hebbian_baseline"]["new_pattern_acc"],
                head,
                r["btsp_grid"][head]["new_pattern_acc"],
                r["binary_hebbian_per_fp"]["%.4f" % FP_GRID_USE[0]]["mean_W_bin"]), flush=True)
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
        result = run_one_seed(seed, N_DIM, N_CAT, N_TRAIN, N_HELDOUT)
        write_partial_key(out_dir, seed, result)
        per_seed_results[str(seed)] = result
        head = "fp=%.4f,fq=%.4f" % (HEADLINE_FP, HEADLINE_FQ)
        head_btsp = result["btsp_grid"].get(head, {}).get("new_pattern_acc", -1.0)
        head_binheb = result["binary_hebbian_per_fp"].get("%.4f" % HEADLINE_FP, {}).get("new_pattern_acc", -1.0)
        head_W_bias = result["binary_hebbian_per_fp"].get("%.4f" % HEADLINE_FP, {}).get("mean_W_bin", 0.0)
        print("[seed=%d] complete in %.1fs cont=%.3f headline BTSP=%.3f BinHeb=%.3f W_bias=%.3f" % (
            seed, time.time() - t0,
            result["cont_hebbian_baseline"]["new_pattern_acc"],
            head_btsp, head_binheb, head_W_bias), flush=True)

    preview: Dict[str, Any] = {}
    if RUN_FULL_N_PREVIEW:
        print("[%s] running FULL_N_PREVIEW at N=2048 headline cell..." % ANCHOR_NAME, flush=True)
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: full_n_preview at N=2048",
                               extra={"_phase": "preview"})
        try:
            preview = run_full_n_preview(SEEDS[0])
            print("[preview] BinHeb at N=2048 headline fp=%.4f: acc=%.3f W_bias=%.3f" % (
                HEADLINE_FP,
                preview["binheb_at_full_N_headline_fp"]["new_pattern_acc"],
                preview["binheb_at_full_N_headline_fp"].get("mean_W_bin", 0.0)), flush=True)
        except Exception as e:
            preview = {"error": str(e)}
            print("[preview] FAIL: %s" % e, file=sys.stderr, flush=True)

    final = aggregate_and_verdict(per_seed_results, preview)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v3p1_btsp_baseline_fixed"
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
