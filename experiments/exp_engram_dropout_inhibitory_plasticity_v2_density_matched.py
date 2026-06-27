"""engram_dropout_inhibitory_plasticity_v2_density_matched -- Wave 2 density-confound fix.

Prereg: preregs/2026-06-27_engram_dropout_inhibitory_plasticity_v2_density_matched.md
Skunkworks audit: notes/skunkworks_mechanism_null_audit_wave2_2026-06-27.md (commit edee21b3)

ROOT CAUSE FIX vs v1:
  v1 hardcoded RANDOM_MASK_DENSITY=0.50 (line 121, 447) while engram_dropout's mask
  naturally shrinks via cycle-by-cycle pruning to mean density ~0.37.
  Density confound: RANDOM_MASK has 0.50/0.37 = 1.35x more active dims than ENGRAM.
  That gives RANDOM_MASK an apples-to-oranges advantage on raw signal capacity.
  Fix: track engram_dropout's final mask density per seed/per pattern; build
  RANDOM_MATCHED mask with EXACTLY the same per-pattern density.

PROCEDURE:
  1. Run engram_dropout (with dropin) -> capture final per-pattern densities D[p]
  2. Build RANDOM_MATCHED masks with density D[p] per pattern (random selection)
  3. Evaluate both arms with identical readout surface

HYPOTHESIS:
  With density-matched random control:
    HARD_PASS: ENGRAM_DROPOUT cor_score - RANDOM_MATCHED cor_score >= 0.05
               (genuine engram-driven selectivity, not just sparsification benefit)
    HARD_FAIL: ENGRAM <= RANDOM at matched density (confirms v1 mechanism null;
               density was doing the work, not engram-driven selection)

ARMS (4):
  ARM_BASELINE_NO_MASK         control: continuous Hebbian, mask=1.0
  ARM_RANDOM_MATCHED           per-pattern random mask with density = D[p] from engram
                               (DENSITY-CONFOUND-CONTROL; replaces v1's hardcoded 0.50)
  ARM_ENGRAM_DROPOUT           per-pattern selectivity-driven mask (dropout only)
  ARM_ENGRAM_DROPOUT_DROPIN    primary: dropout + occasional dropin (Pignatelli mechanism)

PRE-REG BANDS:
  HARD_PASS:
    ENGRAM_DROPOUT_DROPIN cor_score >= 0.40
    AND > RANDOM_MATCHED cor_score by >= 0.05  (density-matched lift)
    AND BASELINE_NO_MASK NOT in [0.95, 1.00]  (fair regime)
    AND mean(final_density) ALIGNED between ENGRAM and RANDOM_MATCHED within 5%
    AND cv across seeds < 0.10 (full only)
  MIDDLE_BAND: cor lift in [0.02, 0.05) OR density alignment off but trends right
  HARD_FAIL:
    BASELINE saturation >= 0.95
    OR ENGRAM <= RANDOM_MATCHED (mechanism null; density was the lever)
    OR density alignment > 10% off (procedure broken)
    OR cardinality breach

REGIME (per USER directive 2026-06-27 fair regime):
  full: N_DIM=512 N_CAT=25 N_TRAIN=5 proto_noise=0.6 (skunkworks Wave 2 audit regime)
  smoke: N_DIM=512 N_CAT=25 N_TRAIN=5 N_CYCLES=50
  FULL_N_PREVIEW: skip (cell is small; smoke == full size in N_DIM)

META_RULE_AA fairness:
  - All arms read SAME SURFACE: masked-readout cor_score to true prototype
  - BASELINE_NO_MASK is control (mask=1.0); ENGRAM is mechanism; RANDOM_MATCHED is
    confound control. Reading SAME surface; only mask BUILD differs.
  - Smoke discriminator FIRES: density-matched random control. If random == engram
    at matched density, mechanism is null (NOT because random is worse, because
    selection process is informationally trivial).
META_RULE_K: smoke must FIRE discriminator (matched density alignment must work)
META_RULE_X: main-guard + L1-L4 hardening
META_RULE_J: no silent except blocks

CARDINALITY_OK:
  smoke: 2 seeds * 4 arms = 8 units; HF if completed < 8
  full: 5 seeds * 4 arms = 20 units; HF if completed < 20

ASCII-only; no emojis; no em-dashes.
Author: exp_dev 2026-06-27 (Wave 2 redesign cell 2 of 4).
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

ANCHOR_NAME = "engram_dropout_inhibitory_plasticity_v2_density_matched"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands
HP_COR_FLOOR = 0.40
HP_COR_LIFT_OVER_MATCHED_RANDOM = 0.05
HP_BASELINE_LO = 0.30
HP_BASELINE_HI = 0.85
HP_CV_MAX = 0.10
HF_SATURATION_HI = 0.95
HF_DENSITY_ALIGNMENT_TOL = 0.10  # density between ENGRAM and RANDOM_MATCHED must align within 10%
MIDDLE_LIFT_LO = 0.02

# Pignatelli plasticity parameters
DELTA_DROPOUT = 0.10
DELTA_DROPIN = 0.02
RECRUITMENT_PROB_PER_STEP = 0.05

EXPECTED_ARMS = ["baseline_no_mask",
                 "random_matched",
                 "engram_dropout",
                 "engram_dropout_dropin"]

# Regime (fair: BTSP-probed sweet spot per Skunkworks audit)
if SELF_TEST_MODE:
    N_DIM = 256
    N_CAT = 10
    N_TRAIN = 5
    PROTO_NOISE = 0.6
    SEEDS = [7]
    N_RETRIEVAL_CYCLES = 10
elif RUN_MODE == "smoke":
    N_DIM = 512
    N_CAT = 25
    N_TRAIN = 5
    PROTO_NOISE = 0.6
    SEEDS = [7, 17]
    N_RETRIEVAL_CYCLES = 50
else:
    N_DIM = 512
    N_CAT = 25
    N_TRAIN = 5
    PROTO_NOISE = 0.6
    SEEDS = [7, 17, 23, 31, 41]
    N_RETRIEVAL_CYCLES = 200

ALPHA_LOAD = N_CAT / float(N_DIM)
EXPECTED_N_UNITS = len(SEEDS) * len(EXPECTED_ARMS)

assert 0.03 <= ALPHA_LOAD <= 0.20, (
    "ALPHA_LOAD=%.4f outside [0.03, 0.20]" % ALPHA_LOAD)
assert DELTA_DROPOUT > DELTA_DROPIN > 0
assert 0.01 <= RECRUITMENT_PROB_PER_STEP <= 0.10

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,NCAT=%d,NTRAIN=%d,proto_noise=%.2f,alpha=%.4f,"
    "seeds=%s,mode=%s,N_CYCLES=%d,delta_dropout=%.3f,delta_dropin=%.3f,recruit_p=%.3f,"
    "HP_cor>=%.2f,HP_lift_over_matched>=%.2f,HP_baseline=[%.2f,%.2f],HP_cv<=%.2f,"
    "HF_density_align_tol=%.2f,hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "FAIRNESS=DENSITY_MATCHED_RANDOM_PER_PATTERN_PER_SEED"
) % (
    ANCHOR_NAME, N_DIM, N_CAT, N_TRAIN, PROTO_NOISE, ALPHA_LOAD,
    SEEDS, RUN_MODE, N_RETRIEVAL_CYCLES,
    DELTA_DROPOUT, DELTA_DROPIN, RECRUITMENT_PROB_PER_STEP,
    HP_COR_FLOOR, HP_COR_LIFT_OVER_MATCHED_RANDOM,
    HP_BASELINE_LO, HP_BASELINE_HI, HP_CV_MAX, HF_DENSITY_ALIGNMENT_TOL,
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
            "_hardening_marker": "v2_engram_density_matched",
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
            "_hardening_marker": "v2_engram_density_matched_import_crash",
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


def classify_via_masked_readout(W: np.ndarray, masks: np.ndarray,
                                  prototypes: np.ndarray, queries: np.ndarray,
                                  labels: np.ndarray) -> Tuple[float, float]:
    """Per-pattern mask at readout; argmax cor_score classify."""
    nc = prototypes.shape[0]
    nq = queries.shape[0]
    pred_labels = np.zeros(nq, dtype=np.int64)
    true_cor_scores: List[float] = []
    for qi in range(nq):
        q = queries[qi]
        best_cor = -1e9
        best_label = -1
        for c in range(nc):
            W_mc = W * masks[c][np.newaxis, :]
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
    nd = W.shape[0]
    nc = prototypes.shape[0]
    fake_masks = np.ones((nc, nd), dtype=np.float32)
    return classify_via_masked_readout(W, fake_masks, prototypes, queries, labels)


def _generate_pattern_set(g: np.random.Generator
                          ) -> Tuple[np.ndarray, np.ndarray, np.ndarray,
                                      np.ndarray, np.ndarray]:
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
    test_keys = [noisy_prototype(prototypes[c], PROTO_NOISE, g) for c in range(N_CAT)]
    test_set = np.stack(test_keys, axis=0).astype(np.float32)
    test_labels = np.arange(N_CAT, dtype=np.int64)
    return prototypes, train_set, train_labels_arr, test_set, test_labels


def _build_initial_W(prototypes: np.ndarray, train_set: np.ndarray,
                      train_labels: np.ndarray) -> np.ndarray:
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for i in range(train_set.shape[0]):
        W += hebbian_outer(train_set[i], prototypes[train_labels[i]])
    return W


def _update_engram_mask(mask: np.ndarray, retrieved_pattern: np.ndarray,
                         target_proto: np.ndarray, dropout: float, dropin: float,
                         recruit_prob: float, g: np.random.Generator,
                         do_dropin: bool) -> np.ndarray:
    selectivity = np.abs(retrieved_pattern * target_proto)
    median = float(np.median(selectivity))
    below = selectivity < median
    new_mask = mask.copy()
    new_mask[below] -= dropout
    if do_dropin:
        eligible = (selectivity >= median) & (new_mask < 0.5)
        recruit_roll = g.random(new_mask.shape[0]) < recruit_prob
        recruit = eligible & recruit_roll
        new_mask[recruit] += dropin
    return np.clip(new_mask, 0.0, 1.0)


# -------------------------- arms --------------------------

def run_arm_baseline_no_mask(prototypes, train_set, train_labels, test_set,
                              test_labels) -> Dict[str, float]:
    W = _build_initial_W(prototypes, train_set, train_labels)
    acc, cor = classify_no_mask(W, prototypes, test_set, test_labels)
    return {
        "new_pattern_acc": acc, "cor_score": cor,
        "per_pattern_mask_density_mean": 1.0,
        "per_pattern_mask_density_std": 0.0,
    }


def run_arm_engram_dropout(prototypes, train_set, train_labels, test_set,
                            test_labels, g_seed: int, with_dropin: bool
                            ) -> Tuple[Dict[str, float], np.ndarray]:
    """Returns (metrics_dict, per_pattern_final_density_array)."""
    g = np.random.default_rng(g_seed + 8002)
    W = _build_initial_W(prototypes, train_set, train_labels)
    nc = prototypes.shape[0]
    masks = np.ones((nc, N_DIM), dtype=np.float32)

    for cycle in range(N_RETRIEVAL_CYCLES):
        for ti in range(train_set.shape[0]):
            pid = int(train_labels[ti])
            if pid >= nc:
                continue
            key = train_set[ti]
            W_masked = W * masks[pid][np.newaxis, :]
            retrieved = key @ W_masked
            masks[pid] = _update_engram_mask(
                masks[pid], retrieved, prototypes[pid],
                DELTA_DROPOUT, DELTA_DROPIN, RECRUITMENT_PROB_PER_STEP,
                g, do_dropin=with_dropin)

    acc, cor = classify_via_masked_readout(W, masks, prototypes, test_set, test_labels)
    per_pattern_density = np.mean(masks, axis=1)  # (nc,) mean mask density per pattern
    return {
        "new_pattern_acc": acc, "cor_score": cor,
        "per_pattern_mask_density_mean": float(np.mean(per_pattern_density)),
        "per_pattern_mask_density_std": float(np.std(per_pattern_density)),
    }, per_pattern_density


def run_arm_random_matched(prototypes, train_set, train_labels, test_set,
                            test_labels, g_seed: int,
                            target_densities: np.ndarray) -> Dict[str, float]:
    """Per-pattern random mask with density = target_densities[p] (matched to engram)."""
    g = np.random.default_rng(g_seed + 8001)
    W = _build_initial_W(prototypes, train_set, train_labels)
    nc = prototypes.shape[0]
    masks = np.zeros((nc, N_DIM), dtype=np.float32)
    for c in range(nc):
        density_c = float(target_densities[c])
        n_active = int(round(density_c * N_DIM))
        if n_active <= 0:
            n_active = 1
        if n_active >= N_DIM:
            masks[c] = 1.0
        else:
            idx = g.choice(N_DIM, size=n_active, replace=False)
            masks[c, idx] = 1.0
    acc, cor = classify_via_masked_readout(W, masks, prototypes, test_set, test_labels)
    return {
        "new_pattern_acc": acc, "cor_score": cor,
        "per_pattern_mask_density_mean": float(np.mean(np.mean(masks, axis=1))),
        "per_pattern_mask_density_std": float(np.std(np.mean(masks, axis=1))),
    }


def run_one_seed(seed: int) -> Dict[str, Any]:
    g_set = np.random.default_rng(seed + 1)
    prototypes, train_set, train_labels, test_set, test_labels = _generate_pattern_set(g_set)

    arm_results: Dict[str, Dict[str, float]] = {}
    arm_results["baseline_no_mask"] = run_arm_baseline_no_mask(
        prototypes, train_set, train_labels, test_set, test_labels)

    # Run engram_dropout (no dropin) -> capture density
    engram_no, density_engram = run_arm_engram_dropout(
        prototypes, train_set, train_labels, test_set, test_labels,
        seed, with_dropin=False)
    arm_results["engram_dropout"] = engram_no

    # Run engram_dropout_dropin -> capture density (PRIMARY for density-matched random)
    engram_yes, density_engram_dropin = run_arm_engram_dropout(
        prototypes, train_set, train_labels, test_set, test_labels,
        seed, with_dropin=True)
    arm_results["engram_dropout_dropin"] = engram_yes

    # DENSITY-MATCHED random control (matched to engram_dropout_dropin per pattern)
    arm_results["random_matched"] = run_arm_random_matched(
        prototypes, train_set, train_labels, test_set, test_labels,
        seed, target_densities=density_engram_dropin)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "N_CAT": N_CAT,
        "N_TRAIN": N_TRAIN,
        "proto_noise": PROTO_NOISE,
        "alpha_load": ALPHA_LOAD,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": arm_results,
        "density_engram_dropin_per_pattern": density_engram_dropin.tolist(),
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}
    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}
        acc_vals: List[float] = []
        cor_vals: List[float] = []
        density_mean_vals: List[float] = []
        for s in seeds_sorted:
            pa = per_seed[s].get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                acc_vals.append(float(d.get("new_pattern_acc", 0.0)))
                cor_vals.append(float(d.get("cor_score", 0.0)))
                density_mean_vals.append(float(d.get("per_pattern_mask_density_mean", 0.0)))
                per_arm_full[arm][s] = {k: float(d.get(k, 0.0)) for k in (
                    "new_pattern_acc", "cor_score",
                    "per_pattern_mask_density_mean", "per_pattern_mask_density_std")}
        if acc_vals:
            m_acc = float(np.mean(acc_vals))
            sd_acc = float(np.std(acc_vals))
            cv = sd_acc / abs(m_acc) if abs(m_acc) > 1e-6 else 0.0
            summary[arm] = {
                "mean_acc": m_acc, "std_acc": sd_acc, "cv_acc": cv,
                "mean_cor": float(np.mean(cor_vals)),
                "mean_density": float(np.mean(density_mean_vals)),
                "n": len(acc_vals),
            }
        else:
            summary[arm] = {"mean_acc": 0.0, "std_acc": 0.0, "cv_acc": 0.0,
                            "mean_cor": 0.0, "mean_density": 0.0, "n": 0}

    base = summary["baseline_no_mask"]
    rand_match = summary["random_matched"]
    engram_dropin = summary["engram_dropout_dropin"]
    base_new = base["mean_acc"]
    engram_cor = engram_dropin["mean_cor"]
    random_cor = rand_match["mean_cor"]
    cor_lift = engram_cor - random_cor
    engram_density = engram_dropin["mean_density"]
    random_density = rand_match["mean_density"]
    density_alignment = abs(engram_density - random_density) / max(engram_density, 1e-6)

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    if base_new >= HF_SATURATION_HI:
        verdict = "HARD_FAIL"
        verdict_reason = "BASELINE_SATURATION: base_new=%.3f >= %.2f" % (
            base_new, HF_SATURATION_HI)
    elif density_alignment > HF_DENSITY_ALIGNMENT_TOL:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "DENSITY_ALIGNMENT_BROKEN: engram=%.3f random_matched=%.3f rel_diff=%.3f > %.2f"
        ) % (engram_density, random_density, density_alignment, HF_DENSITY_ALIGNMENT_TOL)
    elif engram_cor <= random_cor:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "MECHANISM_NULL_AT_MATCHED_DENSITY: engram_cor=%.3f <= random_matched_cor=%.3f "
            "(density was the lever, not engram-driven selection)"
        ) % (engram_cor, random_cor)
    elif (engram_cor >= HP_COR_FLOOR and
            cor_lift >= HP_COR_LIFT_OVER_MATCHED_RANDOM and
            HP_BASELINE_LO <= base_new <= HP_BASELINE_HI):
        verdict = "HARD_PASS"
        verdict_reason = (
            "DENSITY_MATCHED_LIFT: engram_cor=%.3f - random_matched_cor=%.3f = lift=%.3f at "
            "matched density=%.3f (engram-driven selection load-bearing)"
        ) % (engram_cor, random_cor, cor_lift, engram_density)
    elif MIDDLE_LIFT_LO <= cor_lift < HP_COR_LIFT_OVER_MATCHED_RANDOM:
        verdict = "MIDDLE_BAND"
        verdict_reason = "PARTIAL_LIFT: cor_lift=%.3f in [%.2f, %.2f)" % (
            cor_lift, MIDDLE_LIFT_LO, HP_COR_LIFT_OVER_MATCHED_RANDOM)
    elif engram_cor < HP_COR_FLOOR:
        verdict = "MIDDLE_BAND"
        verdict_reason = "ENGRAM_BELOW_FLOOR: engram_cor=%.3f < %.2f" % (
            engram_cor, HP_COR_FLOOR)

    verdict_msg = (
        "%s | %s | base_acc=%.3f | engram_cor=%.3f (density=%.3f) | "
        "random_matched_cor=%.3f (density=%.3f) | lift=%.3f density_align_rel_diff=%.3f | n=%d"
    ) % (verdict, verdict_reason, base_new, engram_cor, engram_density,
         random_cor, random_density, cor_lift, density_alignment, len(seeds_sorted))

    completed_units = len(seeds_sorted) * len(EXPECTED_ARMS)
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "engram_cor": engram_cor,
        "random_matched_cor": random_cor,
        "cor_lift": cor_lift,
        "engram_density": engram_density,
        "random_matched_density": random_density,
        "density_alignment_rel_diff": density_alignment,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= EXPECTED_N_UNITS,
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
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d NCAT=%d alpha=%.4f seeds=%s N_CYCLES=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_CAT, ALPHA_LOAD, SEEDS, N_RETRIEVAL_CYCLES),
        flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
                assert "cor_score" in r["per_arm"][arm]
            engram_d = r["per_arm"]["engram_dropout_dropin"]["per_pattern_mask_density_mean"]
            random_d = r["per_arm"]["random_matched"]["per_pattern_mask_density_mean"]
            align_rel = abs(engram_d - random_d) / max(engram_d, 1e-6)
            assert align_rel < 0.15, (
                "SELFTEST_DENSITY_ALIGN_FAIL: engram=%.3f random=%.3f rel=%.3f >= 0.15" % (
                    engram_d, random_d, align_rel))
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: density-matched random verified (rel diff %.3f)" % align_rel)
            print("[selftest] OK engram_d=%.3f random_d=%.3f align=%.3f engram_cor=%.3f random_cor=%.3f" % (
                engram_d, random_d, align_rel,
                r["per_arm"]["engram_dropout_dropin"]["cor_score"],
                r["per_arm"]["random_matched"]["cor_score"]), flush=True)
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
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(SEEDS)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        per_seed_results[str(seed)] = result
        ed = result["per_arm"]["engram_dropout_dropin"]
        rm = result["per_arm"]["random_matched"]
        print("[seed=%d] complete in %.1fs engram_cor=%.3f (d=%.3f) random_cor=%.3f (d=%.3f) lift=%.3f" % (
            seed, time.time() - t0,
            ed["cor_score"], ed["per_pattern_mask_density_mean"],
            rm["cor_score"], rm["per_pattern_mask_density_mean"],
            ed["cor_score"] - rm["cor_score"]), flush=True)

    final = aggregate_and_verdict(per_seed_results)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v2_engram_density_matched"
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
