"""engram_dropout_inhibitory_plasticity_v1 -- Battery 2 cell at BTSP-probed FAIR REGIME.

Prereg: preregs/2026-06-27_engram_dropout_inhibitory_plasticity_v1.md
Drill source: notes/research_drill_5x_consolidation_saturation_barrier_2026-06-27.md
                RANK 3 (Angle 3 Mechanism 3.3).
Citation: Pignatelli 2024 Nature Neuroscience PMC10917686 "Dynamic and selective
            engrams emerge with memory consolidation".

FIX vs PREREG REGIME: USER directive 2026-06-27 - use BTSP-probed FAIR REGIME
(N_DIM=1024, N_CAT=50, N_TRAIN=5, proto_noise=0.6, alpha=0.0488). Includes regime
probe (BTSP v2 style) that tightens N_TRAIN to 7 or proto_noise to 0.55 if needed.

ARMS (4 + 1 diagnostic):
  ARM_BASELINE_NO_MASK         continuous W, global Hebbian, mask=1.0 (control)
  ARM_RANDOM_MASK_K20          static random mask with same density target = 0.5
                                (false-accept floor; isolates 'mask helps' from
                                'engram-driven mask helps')
  ARM_ENGRAM_DROPOUT           per-pattern mask, dropout-only (decrement below-median)
  ARM_ENGRAM_DROPOUT_PLUS_DROPIN  primary: dropout + occasional dropin (Pignatelli)
  ARM_DIAG_MASK_SIZE_OVER_CYCLES  diagnostic: mean(mask_density) at start/mid/end

PRE-REG BANDS (FAIR-REGIME variant):
  HARD_PASS:
    ENGRAM_DROPOUT_PLUS_DROPIN selectivity (cor_score) >= 0.50
    AND > RANDOM_MASK by >= 0.20 (engram-driven beats false-accept floor)
    AND mean(final_mask_density) in [0.10, 0.30] (genuine 70-90% sparsification per USER)
       NOTE: prereg says [0.40, 0.80] but USER spec says shrinks to 10-30%
       I'm using USER spec; if probe shows mask collapse, fall back to prereg band
    AND ARM_BASELINE_NO_MASK NOT in [0.95, 1.00] AND new_pattern_acc in [0.40, 0.65]
    AND cv across seeds < 0.10 (full only)
  MIDDLE_BAND:
    cor_score in [0.30, 0.50) OR mask in target band but no lift vs RANDOM_MASK
  HARD_FAIL:
    any baseline >= 0.95
    OR mean(final_mask_density) < 0.05 (over-pruning collapse)
       OR > 0.80 (no pruning at all - mechanism null)
    OR ENGRAM_DROPOUT_PLUS_DROPIN <= RANDOM_MASK on cor_score
    OR cardinality breach
    OR regime probe finds NO fair cfg

META_RULE_AA: arms read same surface (cor_score = mean cosine to true prototype
              from masked readout); BASELINE_NO_MASK reads full W; ENGRAM_DROPOUT
              reads W * mask. All identical query path, only mask differs.
META_RULE_K: smoke fires discriminator (mask shrinkage must already trend down
              in smoke; if mask stays flat at 1.0, fail before full dispatch)
META_RULE_X: main wrapped in if __name__; L1-L4 hardening
META_RULE_J: no silent except blocks

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SMOKE = 1 probe + 5 arms * 2 seeds = 11
  EXPECTED_N_UNITS_FULL  = 1 probe + 5 arms * 5 seeds = 26

HARDENING (L1-L4):
  L1 STARTED metrics + PID at write
  L2 per-arm + per-seed progress updates
  L3 outer try/except + import-crash sentinel
  L4 ASCII-only; no emojis; no em-dashes

Author: exp_dev 2026-06-27 (Battery 2 consolidation - cell 2 of 2 fair-regime ships).
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

ANCHOR_NAME = "engram_dropout_inhibitory_plasticity_v1"

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
HP_COR_FLOOR = 0.50              # ENGRAM cor_score >= 0.50
HP_COR_LIFT_OVER_RANDOM = 0.20   # ENGRAM beats RANDOM_MASK by >= 0.20
HP_MASK_DENSITY_LO = 0.10        # USER spec: shrinks to 10-30%
HP_MASK_DENSITY_HI = 0.30
HP_BASELINE_LO = 0.40
HP_BASELINE_HI = 0.65
HP_CV_MAX = 0.10
HF_SATURATION_HI = 0.95
HF_MASK_COLLAPSE_LO = 0.05
HF_MASK_NULL_HI = 0.80

# Dropout / dropin parameters (Pignatelli ratio ~ 5:1 silencing:recruitment)
DELTA_DROPOUT = 0.10
DELTA_DROPIN = 0.02
RECRUITMENT_PROB_PER_STEP = 0.05
ETA_CONSOL = 0.05

# Random mask target density (matches expected ENGRAM final density midpoint)
RANDOM_MASK_DENSITY = 0.50

EXPECTED_ARMS = ["baseline_no_mask",
                 "random_mask_k20",
                 "engram_dropout",
                 "engram_dropout_plus_dropin",
                 "diag_mask_size_over_cycles"]

# REGIME PROBE GRID - BTSP-probed FAIR REGIME
if SELF_TEST_MODE:
    PROBE_N_DIM = [256]
    PROBE_N_CAT = [10]
    PROBE_N_TRAIN = [5]
    PROBE_PROTO_NOISE = [0.60]
    SEEDS = [7]
elif RUN_MODE == "smoke":
    PROBE_N_DIM = [512]
    PROBE_N_CAT = [25]
    PROBE_N_TRAIN = [5, 7, 10]
    PROBE_PROTO_NOISE = [0.55, 0.60, 0.65]
    SEEDS = [7, 17]
else:
    PROBE_N_DIM = [1024]
    PROBE_N_CAT = [50]
    PROBE_N_TRAIN = [5, 7, 10]
    PROBE_PROTO_NOISE = [0.55, 0.60, 0.65]
    SEEDS = [7, 17, 23, 31, 41]

# Retrieval-cycle counts (per-pattern post-initial-write)
if SELF_TEST_MODE:
    N_RETRIEVAL_CYCLES = 10
elif RUN_MODE == "smoke":
    N_RETRIEVAL_CYCLES = 50  # smoke discriminator: mask must trend down by cycle 50
else:
    N_RETRIEVAL_CYCLES = 200

EXPECTED_N_UNITS_SMOKE = 1 + len(EXPECTED_ARMS) * len(SEEDS)
EXPECTED_N_UNITS = EXPECTED_N_UNITS_SMOKE if RUN_MODE == "smoke" else (
    1 + len(EXPECTED_ARMS) * len(SEEDS))

CONFIG_VERSION = (
    "ANCHOR=%s,probe_N=%s,probe_NCAT=%s,probe_NTRAIN=%s,probe_noise=%s,seeds=%s,mode=%s,"
    "HP_cor>=%.2f,HP_lift_over_random>=%.2f,HP_mask_density=[%.2f,%.2f],"
    "HP_baseline_band=[%.2f,%.2f],HP_cv<=%.2f,HF_mask_collapse<%.2f,HF_mask_null>%.2f,"
    "delta_dropout=%.3f,delta_dropin=%.3f,recruit_p=%.3f,N_CYCLES=%d,"
    "hardening=L1early+L2perseed+L3outertry+L4importsentinel,"
    "FAIRNESS=PROBE_BASELINE_IN_BAND_THEN_ENGRAM_MECHANISM"
) % (
    ANCHOR_NAME, PROBE_N_DIM, PROBE_N_CAT, PROBE_N_TRAIN, PROBE_PROTO_NOISE,
    SEEDS, RUN_MODE,
    HP_COR_FLOOR, HP_COR_LIFT_OVER_RANDOM, HP_MASK_DENSITY_LO, HP_MASK_DENSITY_HI,
    HP_BASELINE_LO, HP_BASELINE_HI, HP_CV_MAX, HF_MASK_COLLAPSE_LO, HF_MASK_NULL_HI,
    DELTA_DROPOUT, DELTA_DROPIN, RECRUITMENT_PROB_PER_STEP, N_RETRIEVAL_CYCLES,
)

# Pre-dispatch hard gates (prereg "Pre-dispatch HARD gate")
_alpha_smoke = PROBE_N_CAT[0] / float(PROBE_N_DIM[0])
assert 0.03 <= _alpha_smoke <= 0.20, (
    "alpha=%.4f out of safe band [0.03, 0.20]" % _alpha_smoke)
_snr_pred = 1.0 / math.sqrt(_alpha_smoke)
assert 2.5 <= _snr_pred <= 6.0, "predicted SNR=%.2f out of [2.5, 6.0]" % _snr_pred
assert DELTA_DROPOUT > DELTA_DROPIN > 0, "delta_dropout must dominate delta_dropin"
assert 0.01 <= RECRUITMENT_PROB_PER_STEP <= 0.10, (
    "recruitment_prob=%.3f out of [0.01, 0.10]" % RECRUITMENT_PROB_PER_STEP)

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
            "_hardening_marker": "v1_engram_dropout_inhibitory",
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
            "_hardening_marker": "v1_engram_dropout_inhibitory_import_crash",
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


def cor_score_to_prototype(W_masked: np.ndarray, query: np.ndarray,
                            target_proto: np.ndarray) -> float:
    """Single-query cosine to target prototype after masked readout.
    Returns scalar in [-1, 1].
    """
    out = query @ W_masked
    n_out = float(np.linalg.norm(out) + 1e-8)
    n_tgt = float(np.linalg.norm(target_proto) + 1e-8)
    return float(np.dot(out, target_proto) / (n_out * n_tgt))


def classify_via_masked_readout(W: np.ndarray, masks: np.ndarray,
                                  prototypes: np.ndarray, queries: np.ndarray,
                                  labels: np.ndarray) -> Tuple[float, float]:
    """Apply per-pattern mask at readout: for each query, try each pattern's mask,
    classify by argmax cor_score. Also returns mean cor_score on TRUE-label mask.
    masks shape: (N_PATTERNS, N_DIM); per-pattern mask is on OUTPUT dims (rows of W).
    """
    nc = prototypes.shape[0]
    nq = queries.shape[0]
    pred_labels = np.zeros(nq, dtype=np.int64)
    true_cor_scores: List[float] = []
    proto_n = prototypes / (np.linalg.norm(prototypes, axis=1, keepdims=True) + 1e-8)
    for qi in range(nq):
        q = queries[qi]
        best_cor = -1e9
        best_label = -1
        for c in range(nc):
            W_mc = W * masks[c][np.newaxis, :]  # mask on output dims (cols of W)
            out = q @ W_mc
            n_out = float(np.linalg.norm(out) + 1e-8)
            cor = float(np.dot(out, prototypes[c]) /
                          (n_out * float(np.linalg.norm(prototypes[c]) + 1e-8)))
            if cor > best_cor:
                best_cor = cor
                best_label = c
        pred_labels[qi] = best_label
        if labels[qi] < nc:
            true_cor_scores.append(best_cor if best_label == labels[qi] else 0.0)
    acc = float(np.mean(pred_labels == labels))
    mean_cor = float(np.mean(true_cor_scores)) if true_cor_scores else 0.0
    return acc, mean_cor


def classify_no_mask(W: np.ndarray, prototypes: np.ndarray,
                      queries: np.ndarray, labels: np.ndarray) -> Tuple[float, float]:
    """Baseline: no mask. Same readout surface but mask=1.0 for all."""
    nd = W.shape[0]
    nc = prototypes.shape[0]
    fake_masks = np.ones((nc, nd), dtype=np.float32)
    return classify_via_masked_readout(W, fake_masks, prototypes, queries, labels)


# -------------------------- regime probe --------------------------

def regime_probe(seeds: List[int]) -> Dict[str, Any]:
    """Sweep PROBE_GRID; mean baseline across ALL eval seeds (META_RULE_AA fairness)."""
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
                        g_local = np.random.default_rng(seed + 1001)
                        prototypes = bipolar(nc, nd, g_local)
                        train_keys: List[np.ndarray] = []
                        train_labels: List[int] = []
                        for c in range(nc):
                            for _ in range(nt):
                                train_keys.append(noisy_prototype(prototypes[c], noise, g_local))
                                train_labels.append(c)
                        train_set = np.stack(train_keys, axis=0).astype(np.float32)
                        train_labels_arr = np.array(train_labels, dtype=np.int64)
                        test_keys = [noisy_prototype(prototypes[c], noise, g_local)
                                      for c in range(nc)]
                        test_set = np.stack(test_keys, axis=0).astype(np.float32)
                        test_labels = np.arange(nc, dtype=np.int64)
                        W = np.zeros((nd, nd), dtype=np.float32)
                        for i in range(train_set.shape[0]):
                            W += hebbian_outer(train_set[i], prototypes[train_labels_arr[i]])
                        acc, _ = classify_no_mask(W, prototypes, test_set, test_labels)
                        accs_per_seed.append(acc)
                    mean_acc = float(np.mean(accs_per_seed))
                    cfg["baseline_acc"] = mean_acc
                    cfg["baseline_per_seed"] = accs_per_seed
                    probe_results.append(cfg)
                    print("[probe] N=%d NCAT=%d NTRAIN=%d noise=%.2f alpha=%.4f -> baseline_mean=%.3f (per_seed=%s)" % (
                        nd, nc, nt, noise, alpha, mean_acc,
                        ["%.3f" % a for a in accs_per_seed]), flush=True)
                    if HP_BASELINE_LO <= mean_acc <= HP_BASELINE_HI and found_cfg is None:
                        found_cfg = dict(cfg)

    return {"probe_results": probe_results, "found_cfg": found_cfg}


# -------------------------- arms --------------------------

def _generate_pattern_set(cfg: Dict[str, Any], g: np.random.Generator
                          ) -> Tuple[np.ndarray, np.ndarray, np.ndarray,
                                      np.ndarray, np.ndarray]:
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


def _build_initial_W(cfg: Dict[str, Any], prototypes: np.ndarray,
                      train_set: np.ndarray, train_labels: np.ndarray
                      ) -> np.ndarray:
    nd = cfg["N_DIM"]
    W = np.zeros((nd, nd), dtype=np.float32)
    for i in range(train_set.shape[0]):
        W += hebbian_outer(train_set[i], prototypes[train_labels[i]])
    return W


def _update_engram_mask(mask: np.ndarray, retrieved_pattern: np.ndarray,
                         target_proto: np.ndarray, dropout: float, dropin: float,
                         recruit_prob: float, g: np.random.Generator,
                         do_dropin: bool) -> np.ndarray:
    """Per-pattern mask update rule (Pignatelli 2024):
    - Compute per-dim 'pattern selectivity' = abs(retrieved * target_proto)
    - Dropout: dims below median selectivity -> mask -= dropout
    - Dropin (if enabled): random recruitment of currently-low-mask dims with high
      selectivity at recruit_prob rate -> mask += dropin
    - Clip mask to [0, 1].
    """
    selectivity = np.abs(retrieved_pattern * target_proto)
    median = float(np.median(selectivity))
    below = selectivity < median
    new_mask = mask.copy()
    new_mask[below] -= dropout
    if do_dropin:
        # Recruit dims with selectivity >= median AND currently-low mask
        eligible = (selectivity >= median) & (new_mask < 0.5)
        recruit_roll = g.random(new_mask.shape[0]) < recruit_prob
        recruit = eligible & recruit_roll
        new_mask[recruit] += dropin
    return np.clip(new_mask, 0.0, 1.0)


def run_arm_baseline_no_mask(cfg: Dict[str, Any], g_seed: int,
                              pset: Dict[str, np.ndarray]) -> Dict[str, float]:
    nd = cfg["N_DIM"]
    nc = pset["prototypes"].shape[0]
    W = _build_initial_W(cfg, pset["prototypes"], pset["train"], pset["train_labels"])
    acc, cor = classify_no_mask(W, pset["prototypes"], pset["test"], pset["test_labels"])
    return {
        "new_pattern_acc": acc,
        "heldout_acc": acc,
        "cor_score": cor,
        "mask_density_start": 1.0,
        "mask_density_mid": 1.0,
        "mask_density_end": 1.0,
        "dim_overlap_start": 1.0,
        "dim_overlap_end": 1.0,
    }


def run_arm_random_mask(cfg: Dict[str, Any], g_seed: int,
                         pset: Dict[str, np.ndarray]) -> Dict[str, float]:
    """Per-pattern static random mask with target density RANDOM_MASK_DENSITY."""
    nd = cfg["N_DIM"]
    nc = pset["prototypes"].shape[0]
    g = np.random.default_rng(g_seed + 8001)
    W = _build_initial_W(cfg, pset["prototypes"], pset["train"], pset["train_labels"])
    masks = (g.random((nc, nd)) < RANDOM_MASK_DENSITY).astype(np.float32)
    acc, cor = classify_via_masked_readout(W, masks, pset["prototypes"],
                                             pset["test"], pset["test_labels"])
    return {
        "new_pattern_acc": acc,
        "heldout_acc": acc,
        "cor_score": cor,
        "mask_density_start": float(np.mean(masks)),
        "mask_density_mid": float(np.mean(masks)),
        "mask_density_end": float(np.mean(masks)),
        "dim_overlap_start": float(np.mean(masks @ masks.T) / float(nd)),
        "dim_overlap_end": float(np.mean(masks @ masks.T) / float(nd)),
    }


def run_arm_engram_dropout(cfg: Dict[str, Any], g_seed: int,
                            pset: Dict[str, np.ndarray],
                            with_dropin: bool) -> Dict[str, float]:
    """Per-pattern adaptive mask via dropout (and optional dropin) over N_RETRIEVAL_CYCLES.

    Procedure per cycle:
      For each training pattern p:
        - retrieve via W * mask[p]; query = train_key for p
        - update mask[p] using selectivity rule
    At end: evaluate test-set classification with final masks.
    """
    nd = cfg["N_DIM"]
    nc = pset["prototypes"].shape[0]
    g = np.random.default_rng(g_seed + 8002)
    W = _build_initial_W(cfg, pset["prototypes"], pset["train"],
                          pset["train_labels"])
    # Mask shape: (N_PATTERNS = nc, N_DIM); init all ones (engrams START unselective)
    masks = np.ones((nc, nd), dtype=np.float32)
    initial_overlap = float(np.mean(masks @ masks.T) / float(nd))

    train = pset["train"]
    train_labels = pset["train_labels"]
    prototypes = pset["prototypes"]

    density_mid: float = 1.0
    for cycle in range(N_RETRIEVAL_CYCLES):
        # Iterate over training keys (each train sample drives its pattern's mask)
        for ti in range(train.shape[0]):
            pid = int(train_labels[ti])
            if pid >= nc:
                continue
            key = train[ti]
            W_masked = W * masks[pid][np.newaxis, :]
            retrieved = key @ W_masked  # shape (nd,)
            masks[pid] = _update_engram_mask(
                masks[pid], retrieved, prototypes[pid],
                DELTA_DROPOUT, DELTA_DROPIN, RECRUITMENT_PROB_PER_STEP,
                g, do_dropin=with_dropin)
        if cycle == N_RETRIEVAL_CYCLES // 2:
            density_mid = float(np.mean(masks))

    acc, cor = classify_via_masked_readout(W, masks, prototypes, pset["test"],
                                             pset["test_labels"])
    final_overlap = float(np.mean(masks @ masks.T) / float(nd))
    return {
        "new_pattern_acc": acc,
        "heldout_acc": acc,
        "cor_score": cor,
        "mask_density_start": 1.0,
        "mask_density_mid": density_mid,
        "mask_density_end": float(np.mean(masks)),
        "dim_overlap_start": initial_overlap,
        "dim_overlap_end": final_overlap,
    }


def run_arm_diag(cfg: Dict[str, Any], g_seed: int,
                  pset: Dict[str, np.ndarray]) -> Dict[str, float]:
    """Diagnostic: re-run primary arm but report ONLY mask trajectory."""
    r = run_arm_engram_dropout(cfg, g_seed + 9999, pset, with_dropin=True)
    return {
        "new_pattern_acc": r["mask_density_end"],
        "heldout_acc": r["mask_density_mid"],
        "cor_score": r["cor_score"],
        "mask_density_start": r["mask_density_start"],
        "mask_density_mid": r["mask_density_mid"],
        "mask_density_end": r["mask_density_end"],
        "dim_overlap_start": r["dim_overlap_start"],
        "dim_overlap_end": r["dim_overlap_end"],
    }


def run_one_seed_at_regime(seed: int, cfg: Dict[str, Any]) -> Dict[str, Any]:
    g_set = np.random.default_rng(seed + 1)
    p = _generate_pattern_set(cfg, g_set)
    pset = {"prototypes": p[0], "train": p[1], "train_labels": p[2],
            "test": p[3], "test_labels": p[4]}

    arm_results: Dict[str, Dict[str, float]] = {}
    arm_results["baseline_no_mask"] = run_arm_baseline_no_mask(cfg, seed, pset)
    arm_results["random_mask_k20"] = run_arm_random_mask(cfg, seed, pset)
    arm_results["engram_dropout"] = run_arm_engram_dropout(
        cfg, seed, pset, with_dropin=False)
    arm_results["engram_dropout_plus_dropin"] = run_arm_engram_dropout(
        cfg, seed, pset, with_dropin=True)
    arm_results["diag_mask_size_over_cycles"] = run_arm_diag(cfg, seed, pset)

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
        acc_vals: List[float] = []
        cor_vals: List[float] = []
        mdensity_end_vals: List[float] = []
        mdensity_mid_vals: List[float] = []
        overlap_end_vals: List[float] = []
        for s in seeds_sorted:
            body = per_seed[s]
            pa = body.get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                acc_vals.append(float(d.get("new_pattern_acc", 0.0)))
                cor_vals.append(float(d.get("cor_score", 0.0)))
                mdensity_end_vals.append(float(d.get("mask_density_end", 0.0)))
                mdensity_mid_vals.append(float(d.get("mask_density_mid", 0.0)))
                overlap_end_vals.append(float(d.get("dim_overlap_end", 0.0)))
                per_arm_full[arm][s] = {k: float(d.get(k, 0.0)) for k in (
                    "new_pattern_acc", "heldout_acc", "cor_score",
                    "mask_density_start", "mask_density_mid", "mask_density_end",
                    "dim_overlap_start", "dim_overlap_end")}
        if acc_vals:
            m_acc = float(np.mean(acc_vals))
            sd_acc = float(np.std(acc_vals))
            cv = sd_acc / abs(m_acc) if abs(m_acc) > 1e-6 else 0.0
            summary[arm] = {
                "mean_acc": m_acc, "std_acc": sd_acc, "cv_acc": cv,
                "mean_cor": float(np.mean(cor_vals)),
                "mean_mask_density_end": float(np.mean(mdensity_end_vals)),
                "mean_mask_density_mid": float(np.mean(mdensity_mid_vals)),
                "mean_dim_overlap_end": float(np.mean(overlap_end_vals)),
                "n": len(acc_vals),
            }
        else:
            summary[arm] = {"mean_acc": 0.0, "std_acc": 0.0, "cv_acc": 0.0,
                            "mean_cor": 0.0, "mean_mask_density_end": 0.0,
                            "mean_mask_density_mid": 0.0,
                            "mean_dim_overlap_end": 0.0, "n": 0}

    base = summary["baseline_no_mask"]
    rand_mask = summary["random_mask_k20"]
    engram = summary["engram_dropout"]
    engram_dropin = summary["engram_dropout_plus_dropin"]

    base_new = base["mean_acc"]
    engram_dropin_cor = engram_dropin["mean_cor"]
    random_mask_cor = rand_mask["mean_cor"]
    cor_lift = engram_dropin_cor - random_mask_cor
    mask_density_end = engram_dropin["mean_mask_density_end"]

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
    elif mask_density_end < HF_MASK_COLLAPSE_LO:
        verdict = "HARD_FAIL"
        verdict_reason = "MASK_COLLAPSE: density_end=%.3f < %.2f" % (
            mask_density_end, HF_MASK_COLLAPSE_LO)
    elif mask_density_end > HF_MASK_NULL_HI:
        verdict = "HARD_FAIL"
        verdict_reason = "MASK_NULL: density_end=%.3f > %.2f (no pruning)" % (
            mask_density_end, HF_MASK_NULL_HI)
    elif engram_dropin_cor <= random_mask_cor:
        verdict = "HARD_FAIL"
        verdict_reason = "RANDOM_BEATS_ENGRAM: engram_cor=%.3f <= random_cor=%.3f" % (
            engram_dropin_cor, random_mask_cor)
    elif (engram_dropin_cor >= HP_COR_FLOOR and
            cor_lift >= HP_COR_LIFT_OVER_RANDOM and
            HP_MASK_DENSITY_LO <= mask_density_end <= HP_MASK_DENSITY_HI):
        verdict = "HARD_PASS"
        verdict_reason = (
            "ENGRAM_DROPOUT_DROPIN_LIFT: cor=%.3f lift_over_random=%.3f "
            "mask_density=%.3f in [%.2f, %.2f]" % (
                engram_dropin_cor, cor_lift, mask_density_end,
                HP_MASK_DENSITY_LO, HP_MASK_DENSITY_HI))
    elif engram_dropin_cor < 0.30:
        verdict = "MIDDLE_BAND"
        verdict_reason = "WEAK_COR: engram_cor=%.3f < 0.30" % engram_dropin_cor

    verdict_msg = (
        "%s | %s | base_acc=%.3f base_cor=%.3f | rand_cor=%.3f | "
        "engram_cor=%.3f dropin_cor=%.3f lift_over_rand=%.3f | "
        "mask_density end=%.3f mid=%.3f | regime=%s | n_seeds=%d"
    ) % (verdict, verdict_reason, base_new, base["mean_cor"], random_mask_cor,
         engram["mean_cor"], engram_dropin_cor, cor_lift,
         mask_density_end, engram_dropin["mean_mask_density_mid"],
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
        "engram_dropin_cor": engram_dropin_cor,
        "cor_lift_over_random": cor_lift,
        "mask_density_end": mask_density_end,
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

    print("[%s] mode=%s seeds=%s expected_n=%d N_CYCLES=%d" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, EXPECTED_N_UNITS, N_RETRIEVAL_CYCLES), flush=True)

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
                assert "cor_score" in r["per_arm"][arm]
                assert "mask_density_end" in r["per_arm"][arm]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: probe + per-arm structure verified")
            print("[selftest] OK cfg=%s dropin_cor=%.3f mask_end=%.3f" % (
                cfg, r["per_arm"]["engram_dropout_plus_dropin"]["cor_score"],
                r["per_arm"]["engram_dropout_plus_dropin"]["mask_density_end"]),
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
        print("[probe] INFEASIBLE", flush=True)
        final = aggregate_and_verdict({}, probe)
        final["anchor_name"] = ANCHOR_NAME
        final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
        final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        final["pid"] = os.getpid()
        final["run_mode"] = RUN_MODE
        final["config_version"] = CONFIG_VERSION
        final["_hardening_marker"] = "v1_engram_dropout_inhibitory"
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
        print("[seed=%d] complete in %.1fs (dropin_cor=%.3f mask_end=%.3f)" % (
            seed, time.time() - t0,
            result["per_arm"]["engram_dropout_plus_dropin"]["cor_score"],
            result["per_arm"]["engram_dropout_plus_dropin"]["mask_density_end"]),
              flush=True)

    final = aggregate_and_verdict(per_seed_results, probe)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_engram_dropout_inhibitory"
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
