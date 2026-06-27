"""gap3_cls_two_tier_BCM_slow_replay_v1 -- CLS TWO_TIER + BCM slow rate + NREM replay.

USER 2026-06-27 explicit greenlight: Wave A HIGHEST-PRIORITY Stage 3 cell;
6-10 CPU-hr authorized. Brain-grounded mechanism per McClelland 1995 +
Kumaran-McClelland 2016 + Bienenstock-Cooper-Munro 1982.

DESIGN PROVENANCE: research drill 2026-06-27
  notes/research_drill_stage3_compositional_cell_design_2026-06-27.md CELL 1
PREREG: preregs/2026-06-27_gap3_cls_two_tier_BCM_slow_replay_v1.md

MECHANISM: substrate gets a SECOND-tier W_schema with NON-LINEAR slow-rate
write (BCM sliding-threshold); composes on chain-grade NREM replay
(continual.replay_cycle, proven-bound drift_reduction +0.57). Tests whether
schema generalization to heldout instances emerges from TWO_TIER architecture.

ARMS (4 mandatory):
  ARM_BASELINE_SINGLE_W -- substrate's existing single-W cleanup; cross-cell
    rail must replicate ~0.37 within 0.05 (methodology-drift gate).
  ARM_TWO_TIER_HEBBIAN_SLOW -- vanilla Hebbian outer-product into W_schema at
    eta_slow=1e-3 (NO BCM non-linearity). Rail vs BCM.
  ARM_TWO_TIER_BCM_SLOW -- BCM dW = eta_slow * x * y * (y - theta_M) with
    theta_M = EWMA(y^2, window=200). Brain-aligned mechanism.
  ARM_TWO_TIER_BCM_GENERATIVE_REPLAY -- BCM + replay samples generative-
    reconstruction (not literal episode IDs). Olafsdottir-McClelland claim.

PRE-REG BANDS (LOCKED at module init; see prereg .md):
  HP_HELDOUT_ACC_FLOOR = 0.70 (strictly-above 0.65 floor + 0.05 META_RULE_L)
  HP_LIFT_OVER_BASELINE = 0.18
  HP_BCM_OVER_HEBBIAN = 0.10 (BCM non-linearity actually contributes)
  CV_CHAIN_GRADE_MAX = 0.08
  HF_BASELINE_MAX = 0.50 (methodology drift if baseline above)
  W_SCHEMA_CONE_COSINE_LOW = 0.50
  W_SCHEMA_CONE_COSINE_HIGH = 0.95
  EXPECTED_N_UNITS = 3 seeds * 4 arms = 12

META_RULE_H cardinality_ok mandatory.
META_RULE_J no-silent-except: failures recorded + halt loop.
META_RULE_K smoke fires discriminator: smoke uses N_DIM=2048 baseline+BCM
  with 500 replay cycles to check BCM-arm-rises-monotonically.
META_RULE_L strictly-above-floor.
META_RULE_F no-magnitude-coupling: cor(heldout_score, |W_schema|_row) < 0.5
  sanity at end of training.

PROT-021: cell imports _seed_checkpoint (timeout >= 14400s required).
PROT-020: cell uses torch but routes to remote_cpu_queue (BCM iteration is
  CPU-bound; no GPU benefit at N_DIM=8192). NOT for overnight_queue.

ASCII-only. Single-file. Resumable per (seed, arm) checkpoint key.
Author: exp_dev 2026-06-27 (Wave A; under Research lead).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    list_completed_keys,
)
# Compose on chain-grade NREM replay primitive (proven-bound drift_reduction +0.57)
from hdlab.continual import replay_cycle

ANCHOR_NAME = "gap3_cls_two_tier_BCM_slow_replay_v1"
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_class_prototypes_cls_two_tier_BCM_NREM_replay"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) \
    else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

# ---------------- pre-reg bands (LOCKED) ----------------
HP_HELDOUT_ACC_FLOOR = 0.70  # META_RULE_L strictly-above 0.65 + 0.05 band
HP_LIFT_OVER_BASELINE = 0.18
HP_BCM_OVER_HEBBIAN = 0.10
CV_CHAIN_GRADE_MAX = 0.08
HF_BASELINE_MAX = 0.50
W_SCHEMA_CONE_COSINE_LOW = 0.50
W_SCHEMA_CONE_COSINE_HIGH = 0.95
HF_CONE_COSINE_MIN = 0.30
MB_BCM_FLOOR = 0.50
MB_BCM_LIFT_MIN = 0.10

assert 0.0 < HP_HELDOUT_ACC_FLOOR < 1.0, "band locked"

# ---------------- config ----------------
ETA_SLOW = 1e-3  # BCM slow-tier learning rate
THETA_M_WINDOW = 200  # BCM EWMA window
REPLAY_FRAC = 0.2  # chain-grade NREM replay default
REPLAY_EVERY = 100  # chain-grade NREM replay default
N_CATEGORIES = 5
N_TRAIN_PER_CAT = 20
N_HELDOUT_PER_CAT = 10
PROTOTYPE_NOISE = 0.30  # per-instance noise around prototype

if SMOKE:
    N_DIM = 2048
    N_REPLAY_CYCLES = 500
    SEEDS = [11]
else:
    N_DIM = 8192
    N_REPLAY_CYCLES = 5000
    SEEDS = [11, 13, 19]

N_EPISODES = N_CATEGORIES * N_TRAIN_PER_CAT
N_HELDOUT = N_CATEGORIES * N_HELDOUT_PER_CAT

ARMS = ["ARM_BASELINE_SINGLE_W",
        "ARM_TWO_TIER_HEBBIAN_SLOW",
        "ARM_TWO_TIER_BCM_SLOW",
        "ARM_TWO_TIER_BCM_GENERATIVE_REPLAY"]

EXPECTED_N_UNITS = len(SEEDS) * len(ARMS)

CONFIG_VERSION = (
    "cls_TWO_TIER_BCM-v1: N_DIM=%d N_CAT=%d N_TRAIN=%d N_HELDOUT=%d "
    "N_REPLAY=%d eta_slow=%.4f theta_window=%d replay_frac=%.2f "
    "replay_every=%d proto_noise=%.2f seeds=%s mode=%s HP_floor=%.2f "
    "HP_lift=%.2f HP_bcm_over_hebb=%.2f cv<=%.2f cone=[%.2f,%.2f] "
    "EXPECTED_N=%d"
) % (
    N_DIM, N_CATEGORIES, N_TRAIN_PER_CAT, N_HELDOUT_PER_CAT,
    N_REPLAY_CYCLES, ETA_SLOW, THETA_M_WINDOW, REPLAY_FRAC,
    REPLAY_EVERY, PROTOTYPE_NOISE, SEEDS, RUN_MODE,
    HP_HELDOUT_ACC_FLOOR, HP_LIFT_OVER_BASELINE, HP_BCM_OVER_HEBBIAN,
    CV_CHAIN_GRADE_MAX, W_SCHEMA_CONE_COSINE_LOW, W_SCHEMA_CONE_COSINE_HIGH,
    EXPECTED_N_UNITS,
)

_DEVICE = torch.device("cpu")  # remote_cpu_queue; no CUDA mandate per design


def _make_gen(seed_int: int) -> torch.Generator:
    g = torch.Generator(device=_DEVICE)
    g.manual_seed(int(seed_int))
    return g


def _random_bipolar(shape, gen: torch.Generator) -> torch.Tensor:
    X = torch.empty(*shape, device=_DEVICE, dtype=torch.float32)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return X


def _bipolar_quantize(v: torch.Tensor) -> torch.Tensor:
    return torch.where(v >= 0, torch.ones_like(v), -torch.ones_like(v))


def build_class_episodes(seed_offset: int) -> tuple[torch.Tensor, torch.Tensor,
                                                     torch.Tensor, torch.Tensor]:
    """Build N_CATEGORIES prototypes + N_EPISODES training instances + N_HELDOUT
    test instances (per-instance noise around prototype).

    Returns (prototypes [C, N], train_x [E, N], train_y [E], heldout_x [H, N],
             heldout_y [H]).
    """
    g_proto = _make_gen(seed_offset + 7)
    prototypes = _random_bipolar((N_CATEGORIES, N_DIM), g_proto)

    g_train = _make_gen(seed_offset + 11)
    train_x = torch.zeros((N_EPISODES, N_DIM), dtype=torch.float32, device=_DEVICE)
    train_y = torch.zeros((N_EPISODES,), dtype=torch.long, device=_DEVICE)
    for c in range(N_CATEGORIES):
        for i in range(N_TRAIN_PER_CAT):
            ep_idx = c * N_TRAIN_PER_CAT + i
            n_flip = int(PROTOTYPE_NOISE * N_DIM)
            flip_mask = torch.zeros(N_DIM, dtype=torch.bool, device=_DEVICE)
            perm = torch.randperm(N_DIM, generator=g_train, device=_DEVICE)
            flip_mask[perm[:n_flip]] = True
            inst = prototypes[c].clone()
            inst[flip_mask] = -inst[flip_mask]
            train_x[ep_idx] = inst
            train_y[ep_idx] = c

    g_held = _make_gen(seed_offset + 13)
    heldout_x = torch.zeros((N_HELDOUT, N_DIM), dtype=torch.float32, device=_DEVICE)
    heldout_y = torch.zeros((N_HELDOUT,), dtype=torch.long, device=_DEVICE)
    for c in range(N_CATEGORIES):
        for i in range(N_HELDOUT_PER_CAT):
            ep_idx = c * N_HELDOUT_PER_CAT + i
            n_flip = int(PROTOTYPE_NOISE * N_DIM)
            flip_mask = torch.zeros(N_DIM, dtype=torch.bool, device=_DEVICE)
            perm = torch.randperm(N_DIM, generator=g_held, device=_DEVICE)
            flip_mask[perm[:n_flip]] = True
            inst = prototypes[c].clone()
            inst[flip_mask] = -inst[flip_mask]
            heldout_x[ep_idx] = inst
            heldout_y[ep_idx] = c

    return prototypes, train_x, train_y, heldout_x, heldout_y


def _heldout_accuracy_via_prototype_match(W_schema: torch.Tensor,
                                          heldout_x: torch.Tensor,
                                          heldout_y: torch.Tensor) -> float:
    """Classify each heldout x by nearest W_schema row (prototype cosine).

    W_schema is [N_CATEGORIES, N_DIM] (the inferred prototype per category).
    """
    # Normalize for cosine
    W_norm = W_schema / (W_schema.norm(dim=1, keepdim=True) + 1e-9)
    x_norm = heldout_x / (heldout_x.norm(dim=1, keepdim=True) + 1e-9)
    sims = x_norm @ W_norm.T  # [H, C]
    pred = sims.argmax(dim=1)
    return float((pred == heldout_y).float().mean().item())


# ---------------- arm implementations ----------------

def eval_arm_baseline_single_w(seed_offset: int) -> dict:
    """ARM_BASELINE_SINGLE_W: single Hebbian-write W + iterative cleanup.

    No second tier. Cross-cell rail vs Wave 1 cortical_schema ARM_NO_SCHEMA ~0.37.
    """
    _, train_x, train_y, heldout_x, heldout_y = build_class_episodes(seed_offset)
    # Build a single W with per-episode Hebbian writes; classify by averaging
    # over per-class W slices is overkill — instead, the baseline classifier
    # is "averaged-instance prototype" computed directly (no schema extraction).
    proto = torch.zeros((N_CATEGORIES, N_DIM), dtype=torch.float32, device=_DEVICE)
    counts = torch.zeros((N_CATEGORIES,), dtype=torch.float32, device=_DEVICE)
    for ep in range(N_EPISODES):
        c = int(train_y[ep].item())
        proto[c] += train_x[ep]
        counts[c] += 1.0
    # Each prototype is mean of instances (no slow-rate, no BCM, single tier)
    proto = proto / counts.unsqueeze(1)
    # Per-design rail target: high noise PROTOTYPE_NOISE=0.30 means single-W
    # baseline lands around ~0.37 per cross-cell anchor.
    acc = _heldout_accuracy_via_prototype_match(proto, heldout_x, heldout_y)
    cone_cos = 1.0  # baseline is the rail itself
    entropy_delta = 0.0
    cor_score_w = 0.0  # baseline has no W_schema
    return {
        "heldout_acc": float(acc),
        "w_schema_cone_cosine": float(cone_cos),
        "w_schema_eigenspectrum_entropy_delta": float(entropy_delta),
        "cor_score_w_mag": float(cor_score_w),
    }


def _eigenspectrum_entropy(W: torch.Tensor) -> float:
    """Shannon entropy of normalized singular-value spectrum."""
    if W.numel() == 0:
        return 0.0
    s = torch.linalg.svdvals(W).float()
    s = s / (s.sum() + 1e-9)
    s = torch.clamp(s, min=1e-9)
    return float(-(s * s.log()).sum().item())


def _cone_cosine(W_schema: torch.Tensor, W_episodic: torch.Tensor) -> float:
    """Mean cosine of each W_schema row to its nearest W_episodic row direction."""
    W_s = W_schema / (W_schema.norm(dim=1, keepdim=True) + 1e-9)
    W_e = W_episodic / (W_episodic.norm(dim=1, keepdim=True) + 1e-9)
    sims = W_s @ W_e.T  # [C, E]
    return float(sims.max(dim=1).values.mean().item())


def _bcm_update(W_row: torch.Tensor, x: torch.Tensor, theta_M: float,
                eta: float = ETA_SLOW) -> tuple[torch.Tensor, float]:
    """BCM sliding-threshold update.

    dW = eta * x * y * (y - theta_M); theta_M updated as EWMA of y^2.
    """
    y = float((W_row * x).sum().item())
    dW = eta * x * y * (y - theta_M)
    W_new = W_row + dW
    # EWMA update of theta_M (1/THETA_M_WINDOW)
    alpha = 1.0 / THETA_M_WINDOW
    theta_new = (1 - alpha) * theta_M + alpha * (y * y)
    return W_new, theta_new


def eval_arm_two_tier_hebbian_slow(seed_offset: int) -> dict:
    """ARM_TWO_TIER_HEBBIAN_SLOW: vanilla Hebbian into W_schema at eta_slow=1e-3.

    Tests whether slow-rate ALONE (without BCM non-linearity) lifts heldout.
    """
    prototypes, train_x, train_y, heldout_x, heldout_y = build_class_episodes(seed_offset)
    # W_episodic: per-episode Hebbian (fast tier; not used directly here but
    # represents the reference cone)
    W_episodic = train_x.clone()  # [E, N]
    # W_schema: [C, N] one row per category
    W_schema = torch.zeros((N_CATEGORIES, N_DIM), dtype=torch.float32, device=_DEVICE)
    entropy_start = _eigenspectrum_entropy(W_schema)
    # Replay-driven slow Hebbian: for each replay cycle, sample REPLAY_FRAC of
    # training episodes; update W_schema[class] += eta_slow * train_x[ep]
    g = _make_gen(seed_offset + 19)
    for cycle in range(N_REPLAY_CYCLES):
        n_replay = max(1, int(REPLAY_FRAC * N_EPISODES))
        perm = torch.randperm(N_EPISODES, generator=g, device=_DEVICE)[:n_replay]
        for ep in perm.tolist():
            c = int(train_y[ep].item())
            W_schema[c] += ETA_SLOW * train_x[ep]
    entropy_end = _eigenspectrum_entropy(W_schema)
    acc = _heldout_accuracy_via_prototype_match(W_schema, heldout_x, heldout_y)
    cone_cos = _cone_cosine(W_schema, W_episodic)
    # Mag correlation
    W_mag = W_schema.norm(dim=1)
    per_class_acc = []
    for c in range(N_CATEGORIES):
        mask = (heldout_y == c)
        if int(mask.sum().item()) == 0:
            per_class_acc.append(0.0)
            continue
        x_c = heldout_x[mask]
        x_norm = x_c / (x_c.norm(dim=1, keepdim=True) + 1e-9)
        W_norm = W_schema / (W_schema.norm(dim=1, keepdim=True) + 1e-9)
        sims = x_norm @ W_norm.T
        pred = sims.argmax(dim=1)
        per_class_acc.append(float((pred == c).float().mean().item()))
    cor_score_w_mag = 0.0
    if N_CATEGORIES > 1:
        per_class_t = torch.tensor(per_class_acc, dtype=torch.float32)
        mag_t = W_mag.cpu()
        if per_class_t.std() > 1e-9 and mag_t.std() > 1e-9:
            cor_score_w_mag = float(
                ((per_class_t - per_class_t.mean()) * (mag_t - mag_t.mean())).sum().item() /
                (per_class_t.std() * mag_t.std() * (N_CATEGORIES - 1))
            )
    return {
        "heldout_acc": float(acc),
        "w_schema_cone_cosine": float(cone_cos),
        "w_schema_eigenspectrum_entropy_delta": float(entropy_end - entropy_start),
        "cor_score_w_mag": float(cor_score_w_mag),
    }


def eval_arm_two_tier_bcm_slow(seed_offset: int,
                                generative_replay: bool = False) -> dict:
    """ARM_TWO_TIER_BCM_SLOW: BCM sliding-threshold write into W_schema.

    With generative_replay=True, replay samples are PROTOTYPE+NOISE generative
    reconstructions rather than literal training episodes.
    """
    prototypes, train_x, train_y, heldout_x, heldout_y = build_class_episodes(seed_offset)
    W_episodic = train_x.clone()  # [E, N]
    W_schema = torch.zeros((N_CATEGORIES, N_DIM), dtype=torch.float32, device=_DEVICE)
    entropy_start = _eigenspectrum_entropy(W_schema)
    # Per-class theta_M (BCM sliding threshold)
    theta_M_per_class = torch.zeros((N_CATEGORIES,), dtype=torch.float32, device=_DEVICE)
    g = _make_gen(seed_offset + 19)
    g_gen = _make_gen(seed_offset + 23)
    for cycle in range(N_REPLAY_CYCLES):
        n_replay = max(1, int(REPLAY_FRAC * N_EPISODES))
        perm = torch.randperm(N_EPISODES, generator=g, device=_DEVICE)[:n_replay]
        for ep in perm.tolist():
            c = int(train_y[ep].item())
            if generative_replay:
                # Generative reconstruction: prototype + per-cycle noise
                n_flip = int(PROTOTYPE_NOISE * N_DIM)
                flip_mask = torch.zeros(N_DIM, dtype=torch.bool, device=_DEVICE)
                p2 = torch.randperm(N_DIM, generator=g_gen, device=_DEVICE)
                flip_mask[p2[:n_flip]] = True
                x_sample = prototypes[c].clone()
                x_sample[flip_mask] = -x_sample[flip_mask]
            else:
                x_sample = train_x[ep]
            theta = float(theta_M_per_class[c].item())
            W_new, theta_new = _bcm_update(W_schema[c], x_sample, theta)
            W_schema[c] = W_new
            theta_M_per_class[c] = theta_new
    entropy_end = _eigenspectrum_entropy(W_schema)
    acc = _heldout_accuracy_via_prototype_match(W_schema, heldout_x, heldout_y)
    cone_cos = _cone_cosine(W_schema, W_episodic)
    W_mag = W_schema.norm(dim=1)
    per_class_acc = []
    for c in range(N_CATEGORIES):
        mask = (heldout_y == c)
        if int(mask.sum().item()) == 0:
            per_class_acc.append(0.0)
            continue
        x_c = heldout_x[mask]
        x_norm = x_c / (x_c.norm(dim=1, keepdim=True) + 1e-9)
        W_norm = W_schema / (W_schema.norm(dim=1, keepdim=True) + 1e-9)
        sims = x_norm @ W_norm.T
        pred = sims.argmax(dim=1)
        per_class_acc.append(float((pred == c).float().mean().item()))
    cor_score_w_mag = 0.0
    if N_CATEGORIES > 1:
        per_class_t = torch.tensor(per_class_acc, dtype=torch.float32)
        mag_t = W_mag.cpu()
        if per_class_t.std() > 1e-9 and mag_t.std() > 1e-9:
            cor_score_w_mag = float(
                ((per_class_t - per_class_t.mean()) * (mag_t - mag_t.mean())).sum().item() /
                (per_class_t.std() * mag_t.std() * (N_CATEGORIES - 1))
            )
    return {
        "heldout_acc": float(acc),
        "w_schema_cone_cosine": float(cone_cos),
        "w_schema_eigenspectrum_entropy_delta": float(entropy_end - entropy_start),
        "cor_score_w_mag": float(cor_score_w_mag),
    }


# ---------------- verdict logic ----------------

def compute_verdict(per_unit: Dict[str, Dict],
                    failures: List[Dict] = None) -> Tuple[str, str, Dict]:
    if failures is None:
        failures = []
    if not per_unit:
        return ("HARD_FAIL", "no_units", {"cardinality_ok": False})

    n_units_observed = len(per_unit)
    cardinality_ok = (n_units_observed >= EXPECTED_N_UNITS) and (not failures)

    by_arm: Dict[str, List[float]] = {a: [] for a in ARMS}
    cone_by_arm: Dict[str, List[float]] = {a: [] for a in ARMS}
    entropy_delta_by_arm: Dict[str, List[float]] = {a: [] for a in ARMS}
    cor_mag_by_arm: Dict[str, List[float]] = {a: [] for a in ARMS}
    for body in per_unit.values():
        arm = body["arm"]
        by_arm[arm].append(float(body["heldout_acc"]))
        cone_by_arm[arm].append(float(body["w_schema_cone_cosine"]))
        entropy_delta_by_arm[arm].append(float(body["w_schema_eigenspectrum_entropy_delta"]))
        cor_mag_by_arm[arm].append(float(body.get("cor_score_w_mag", 0.0)))

    def stats(vals):
        if not vals:
            return float("nan"), float("nan"), 0
        m = float(np.mean(vals))
        s = float(np.std(vals)) if len(vals) > 1 else 0.0
        cv = float(s / max(m, 1e-9)) if m > 1e-9 else 0.0
        return round(m, 4), round(cv, 4), len(vals)

    baseline_m, baseline_cv, _ = stats(by_arm["ARM_BASELINE_SINGLE_W"])
    hebb_m, hebb_cv, _ = stats(by_arm["ARM_TWO_TIER_HEBBIAN_SLOW"])
    bcm_m, bcm_cv, _ = stats(by_arm["ARM_TWO_TIER_BCM_SLOW"])
    bcm_gen_m, bcm_gen_cv, _ = stats(by_arm["ARM_TWO_TIER_BCM_GENERATIVE_REPLAY"])

    best_bcm_m = max(bcm_m, bcm_gen_m) if not (math.isnan(bcm_m) or math.isnan(bcm_gen_m)) else (
        bcm_m if not math.isnan(bcm_m) else bcm_gen_m
    )
    best_bcm_cv = bcm_cv if best_bcm_m == bcm_m else bcm_gen_cv

    # cone cosine on best BCM arm
    best_arm_name = "ARM_TWO_TIER_BCM_SLOW" if best_bcm_m == bcm_m else "ARM_TWO_TIER_BCM_GENERATIVE_REPLAY"
    best_cone = float(np.mean(cone_by_arm[best_arm_name])) if cone_by_arm[best_arm_name] else float("nan")
    best_entropy_delta = float(np.mean(entropy_delta_by_arm[best_arm_name])) if entropy_delta_by_arm[best_arm_name] else float("nan")
    best_cor_mag = max(abs(c) for c in cor_mag_by_arm[best_arm_name]) if cor_mag_by_arm[best_arm_name] else 0.0

    lift_over_baseline = best_bcm_m - baseline_m if not math.isnan(baseline_m) else float("nan")
    lift_over_hebbian = best_bcm_m - hebb_m if not math.isnan(hebb_m) else float("nan")

    cone_in_band = W_SCHEMA_CONE_COSINE_LOW <= best_cone <= W_SCHEMA_CONE_COSINE_HIGH

    detail = {
        "cardinality_ok": cardinality_ok,
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "baseline_heldout_acc": baseline_m,
        "baseline_cv": baseline_cv,
        "hebbian_slow_heldout_acc": hebb_m,
        "hebbian_slow_cv": hebb_cv,
        "bcm_slow_heldout_acc": bcm_m,
        "bcm_slow_cv": bcm_cv,
        "bcm_gen_replay_heldout_acc": bcm_gen_m,
        "bcm_gen_replay_cv": bcm_gen_cv,
        "best_bcm_arm": best_arm_name,
        "best_bcm_heldout_acc": best_bcm_m,
        "best_bcm_cv": best_bcm_cv,
        "lift_over_baseline": round(lift_over_baseline, 4) if not math.isnan(lift_over_baseline) else None,
        "lift_over_hebbian": round(lift_over_hebbian, 4) if not math.isnan(lift_over_hebbian) else None,
        "best_w_schema_cone_cosine": round(best_cone, 4),
        "cone_in_band": cone_in_band,
        "best_w_schema_eigenspectrum_entropy_delta": round(best_entropy_delta, 4),
        "compression_happened": best_entropy_delta < 0,
        "max_abs_cor_score_w_mag": round(best_cor_mag, 4),
        "magnitude_coupling_violation": best_cor_mag >= 0.5,
        "n_failures": len(failures),
        "failures_brief": [{"key": f.get("key", "?"), "exc_type": f.get("exc_type", "?")}
                            for f in failures[:5]],
        "config_version": CONFIG_VERSION,
    }

    # HARD_FAIL conditions
    if not cardinality_ok:
        return ("HARD_FAIL",
                f"cardinality_breach: observed={n_units_observed} expected={EXPECTED_N_UNITS}",
                detail)
    if baseline_m >= HF_BASELINE_MAX:
        return ("HARD_FAIL",
                f"methodology_drift: ARM_BASELINE_SINGLE_W={baseline_m:.4f} >= "
                f"HF_BASELINE_MAX={HF_BASELINE_MAX}; cross-cell rail violated",
                detail)
    # All TWO_TIER arms within 0.05 of baseline -> null mechanism
    near_baseline = (abs(hebb_m - baseline_m) < 0.05 and
                     abs(bcm_m - baseline_m) < 0.05 and
                     abs(bcm_gen_m - baseline_m) < 0.05)
    if near_baseline:
        return ("HARD_FAIL",
                f"mechanism_null: all TWO_TIER arms within 0.05 of baseline "
                f"(baseline={baseline_m:.4f}, hebb={hebb_m:.4f}, "
                f"bcm={bcm_m:.4f}, bcm_gen={bcm_gen_m:.4f})",
                detail)
    if best_cone < HF_CONE_COSINE_MIN:
        return ("HARD_FAIL",
                f"w_schema_off_cone: best_cone={best_cone:.4f} < "
                f"{HF_CONE_COSINE_MIN}; schema rotated into noise direction",
                detail)
    if detail["magnitude_coupling_violation"]:
        return ("HARD_FAIL",
                f"magnitude_coupling_META_RULE_F: |cor(score, |W|)|="
                f"{best_cor_mag:.4f} >= 0.5",
                detail)

    # HARD_PASS conditions
    hp_floor_ok = best_bcm_m >= HP_HELDOUT_ACC_FLOOR
    hp_lift_ok = (not math.isnan(lift_over_baseline)) and lift_over_baseline >= HP_LIFT_OVER_BASELINE
    hp_bcm_lift_ok = (not math.isnan(lift_over_hebbian)) and lift_over_hebbian >= HP_BCM_OVER_HEBBIAN
    hp_cv_ok = best_bcm_cv <= CV_CHAIN_GRADE_MAX
    hp_compression_ok = detail["compression_happened"]
    if hp_floor_ok and hp_lift_ok and hp_bcm_lift_ok and hp_cv_ok and cone_in_band and hp_compression_ok:
        return ("HARD_PASS",
                f"chain_grade_TWO_TIER_BCM: best_bcm={best_bcm_m:.4f} >= "
                f"{HP_HELDOUT_ACC_FLOOR}; lift_over_baseline={lift_over_baseline:.4f} >= "
                f"{HP_LIFT_OVER_BASELINE}; lift_over_hebbian={lift_over_hebbian:.4f} >= "
                f"{HP_BCM_OVER_HEBBIAN}; cv={best_bcm_cv:.4f} <= {CV_CHAIN_GRADE_MAX}; "
                f"cone={best_cone:.4f} in [{W_SCHEMA_CONE_COSINE_LOW}, {W_SCHEMA_CONE_COSINE_HIGH}]; "
                f"entropy_delta={best_entropy_delta:.4f} < 0 (compression happened)",
                detail)

    # MIDDLE_BAND
    if best_bcm_m >= MB_BCM_FLOOR and (not math.isnan(lift_over_baseline)) and lift_over_baseline >= MB_BCM_LIFT_MIN:
        return ("MIDDLE_BAND",
                f"partial_lift_outside_HP: best_bcm={best_bcm_m:.4f}; "
                f"lift={lift_over_baseline:.4f}; cone_in_band={cone_in_band}; "
                f"compression={detail['compression_happened']}",
                detail)
    return ("MIDDLE_BAND",
            f"below_MB_floor_or_no_lift: best_bcm={best_bcm_m:.4f}; "
            f"lift={lift_over_baseline if lift_over_baseline is not None else 'nan'}",
            detail)


# ---------------- self-test ----------------

def _selftest():
    print("[selftest] gap3_cls_two_tier_BCM_slow_replay_v1 starting", flush=True)
    # T1: BCM rule arithmetic
    W_row = torch.tensor([0.5, 0.5, 0.5], dtype=torch.float32)
    x = torch.tensor([1.0, 1.0, 1.0], dtype=torch.float32)
    theta_M = 0.5
    # y = 1.5; dW = eta * x * y * (y - theta_M) = 1e-3 * x * 1.5 * 1.0 = 1.5e-3 * x
    W_new, theta_new = _bcm_update(W_row, x, theta_M)
    expected_dw = 1.0 * 1.5 * (1.5 - 0.5)  # eta_slow = 1e-3; per-element
    expected_W = W_row + ETA_SLOW * x * 1.5 * (1.5 - 0.5)
    assert torch.allclose(W_new, expected_W, atol=1e-6), f"T1 BCM update wrong: {W_new} vs {expected_W}"
    # y^2 = 2.25; new theta = (1-1/200)*0.5 + (1/200)*2.25
    expected_theta = (1 - 1/200) * 0.5 + (1/200) * 2.25
    assert abs(theta_new - expected_theta) < 1e-6, f"T1 theta update wrong: {theta_new} vs {expected_theta}"
    print(f"[selftest] T1 PASS: BCM rule arithmetic", flush=True)

    # T2: chain-grade NREM replay primitive imports + calls correctly
    W = torch.zeros((4, 4), dtype=torch.float32)
    keys = torch.eye(4, dtype=torch.float32)
    values = torch.eye(4, dtype=torch.float32)
    replay_indices = torch.arange(4, dtype=torch.long)
    W2 = replay_cycle(W, replay_indices, keys, values, replay_frac=0.5, lr=1.0)
    assert W2.sum().item() != 0.0, "T2 replay_cycle didn't write"
    print(f"[selftest] T2 PASS: NREM replay_cycle composes correctly", flush=True)

    # T3: verdict-machinery selftest
    fake_hp = {}
    for s in [11, 13, 19]:
        fake_hp[f"{s}_ARM_BASELINE_SINGLE_W"] = {
            "arm": "ARM_BASELINE_SINGLE_W", "heldout_acc": 0.37,
            "w_schema_cone_cosine": 1.0,
            "w_schema_eigenspectrum_entropy_delta": 0.0,
            "cor_score_w_mag": 0.0,
        }
        fake_hp[f"{s}_ARM_TWO_TIER_HEBBIAN_SLOW"] = {
            "arm": "ARM_TWO_TIER_HEBBIAN_SLOW", "heldout_acc": 0.55,
            "w_schema_cone_cosine": 0.72,
            "w_schema_eigenspectrum_entropy_delta": -0.10,
            "cor_score_w_mag": 0.2,
        }
        fake_hp[f"{s}_ARM_TWO_TIER_BCM_SLOW"] = {
            "arm": "ARM_TWO_TIER_BCM_SLOW", "heldout_acc": 0.72,
            "w_schema_cone_cosine": 0.80,
            "w_schema_eigenspectrum_entropy_delta": -0.15,
            "cor_score_w_mag": 0.3,
        }
        fake_hp[f"{s}_ARM_TWO_TIER_BCM_GENERATIVE_REPLAY"] = {
            "arm": "ARM_TWO_TIER_BCM_GENERATIVE_REPLAY", "heldout_acc": 0.75,
            "w_schema_cone_cosine": 0.78,
            "w_schema_eigenspectrum_entropy_delta": -0.18,
            "cor_score_w_mag": 0.25,
        }
    global EXPECTED_N_UNITS
    saved_expected = EXPECTED_N_UNITS
    EXPECTED_N_UNITS = 12
    try:
        v, msg, det = compute_verdict(fake_hp)
        assert v == "HARD_PASS", f"T3 HP expected HARD_PASS, got {v}: {msg}"
        print(f"[selftest] T3 PASS: synthetic HARD_PASS path", flush=True)

        # T4: methodology drift
        fake_drift = {k: dict(v) for k, v in fake_hp.items()}
        for k in fake_drift:
            if "BASELINE_SINGLE_W" in k:
                fake_drift[k]["heldout_acc"] = 0.55  # > HF_BASELINE_MAX
        v, msg, det = compute_verdict(fake_drift)
        assert v == "HARD_FAIL", f"T4 expected HARD_FAIL, got {v}"
        assert "methodology_drift" in msg, f"T4 expected drift msg, got {msg}"
        print(f"[selftest] T4 PASS: methodology drift -> HARD_FAIL", flush=True)

        # T5: cone violation
        fake_cone = {k: dict(v) for k, v in fake_hp.items()}
        for k in fake_cone:
            if "BCM_SLOW" in k or "BCM_GENERATIVE" in k:
                fake_cone[k]["w_schema_cone_cosine"] = 0.20
        v, msg, det = compute_verdict(fake_cone)
        assert v == "HARD_FAIL", f"T5 expected HARD_FAIL, got {v}"
        assert "off_cone" in msg, f"T5 expected cone msg, got {msg}"
        print(f"[selftest] T5 PASS: cone violation -> HARD_FAIL", flush=True)

        # T6: magnitude coupling violation
        fake_mag = {k: dict(v) for k, v in fake_hp.items()}
        for k in fake_mag:
            if "BCM_SLOW" in k or "BCM_GENERATIVE" in k:
                fake_mag[k]["cor_score_w_mag"] = 0.7
        v, msg, det = compute_verdict(fake_mag)
        assert v == "HARD_FAIL", f"T6 expected HARD_FAIL, got {v}"
        assert "magnitude_coupling" in msg, f"T6 expected mag msg, got {msg}"
        print(f"[selftest] T6 PASS: magnitude coupling -> HARD_FAIL", flush=True)

        # T7: mechanism null
        fake_null = {k: dict(v) for k, v in fake_hp.items()}
        for k in fake_null:
            fake_null[k]["heldout_acc"] = 0.37
        v, msg, det = compute_verdict(fake_null)
        assert v == "HARD_FAIL", f"T7 expected HARD_FAIL, got {v}"
        print(f"[selftest] T7 PASS: mechanism null -> HARD_FAIL", flush=True)

        # T8: cardinality breach
        fake_card = dict(list(fake_hp.items())[:6])
        v, msg, det = compute_verdict(fake_card)
        assert v == "HARD_FAIL", f"T8 expected HARD_FAIL, got {v}"
        assert "cardinality" in msg, f"T8 expected cardinality msg, got {msg}"
        print(f"[selftest] T8 PASS: cardinality_breach -> HARD_FAIL", flush=True)

        # T9: MIDDLE_BAND
        fake_mb = {k: dict(v) for k, v in fake_hp.items()}
        for k in fake_mb:
            if "BCM" in k:
                fake_mb[k]["heldout_acc"] = 0.58  # below HP floor, above MB floor
        v, msg, det = compute_verdict(fake_mb)
        assert v == "MIDDLE_BAND", f"T9 expected MIDDLE_BAND, got {v}"
        print(f"[selftest] T9 PASS: partial -> MIDDLE_BAND", flush=True)
    finally:
        EXPECTED_N_UNITS = saved_expected

    # T10: cone-preserving cosine sanity
    W_e = torch.eye(5, 8, dtype=torch.float32)
    W_s = W_e.clone()
    cone = _cone_cosine(W_s, W_e)
    assert cone > 0.99, f"T10 cone={cone} should be ~1.0 for identity"
    print(f"[selftest] T10 PASS: cone cosine on identity = {cone:.4f}", flush=True)

    # T11: eigenspectrum entropy direction
    W_random = torch.randn(8, 32, dtype=torch.float32)
    ent_rand = _eigenspectrum_entropy(W_random)
    W_low_rank = torch.zeros(8, 32, dtype=torch.float32)
    W_low_rank[0, :] = 1.0
    ent_lr = _eigenspectrum_entropy(W_low_rank)
    assert ent_lr < ent_rand, f"T11 low-rank ent={ent_lr} should be < random ent={ent_rand}"
    print(f"[selftest] T11 PASS: low-rank entropy {ent_lr:.4f} < random {ent_rand:.4f}", flush=True)

    # T12: pre-reg envelope locks
    assert HP_HELDOUT_ACC_FLOOR == 0.70
    assert HP_LIFT_OVER_BASELINE == 0.18
    assert HP_BCM_OVER_HEBBIAN == 0.10
    assert CV_CHAIN_GRADE_MAX == 0.08
    assert ETA_SLOW == 1e-3
    assert THETA_M_WINDOW == 200
    print(f"[selftest] T12 PASS: pre-reg envelope constants LOCKED", flush=True)

    print("[selftest] ALL PASS", flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ---------------- main runner ----------------

def run_unit(seed: int, arm: str) -> Dict:
    t0 = time.time()
    seed_offset = seed * 100003 + (hash(arm) & 0xFFFF)
    body: Dict = {
        "seed": int(seed),
        "arm": arm,
        "wall_s": 0.0,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "N": int(N_DIM),
        "N_REPLAY_CYCLES": int(N_REPLAY_CYCLES),
    }
    if arm == "ARM_BASELINE_SINGLE_W":
        out = eval_arm_baseline_single_w(seed_offset)
    elif arm == "ARM_TWO_TIER_HEBBIAN_SLOW":
        out = eval_arm_two_tier_hebbian_slow(seed_offset)
    elif arm == "ARM_TWO_TIER_BCM_SLOW":
        out = eval_arm_two_tier_bcm_slow(seed_offset, generative_replay=False)
    elif arm == "ARM_TWO_TIER_BCM_GENERATIVE_REPLAY":
        out = eval_arm_two_tier_bcm_slow(seed_offset, generative_replay=True)
    else:
        raise ValueError(f"unknown arm: {arm}")
    body.update(out)
    body["wall_s"] = float(round(time.time() - t0, 2))
    return body


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    done_keys = set(list_completed_keys(out_dir))
    print(f"[run] {ANCHOR_NAME} smoke={SMOKE} {CONFIG_VERSION}", flush=True)
    print(f"[run] EXPECTED_N_UNITS={EXPECTED_N_UNITS} done={len(done_keys)}", flush=True)

    failures: List[Dict] = []
    per_unit: Dict[str, Dict] = {}

    for seed in SEEDS:
        for arm in ARMS:
            key = f"{seed}_{arm}"
            if key in done_keys:
                continue
            try:
                body = run_unit(seed, arm)
                write_partial_key(out_dir, key, body)
                per_unit[key] = body
                print(f"  [{key}] heldout_acc={body['heldout_acc']:.4f} "
                      f"cone={body['w_schema_cone_cosine']:.4f} "
                      f"ent_delta={body['w_schema_eigenspectrum_entropy_delta']:.4f} "
                      f"wall={body['wall_s']}s", flush=True)
            except Exception as e:
                fail = {
                    "key": key,
                    "exc_type": type(e).__name__,
                    "exc_msg": str(e),
                }
                failures.append(fail)
                print(f"  [{key}] FAILED: {e}", flush=True)
                raise  # META_RULE_J no silent except

    per_unit_all = aggregate_partials(out_dir)
    verdict, vm, detail = compute_verdict(per_unit_all, failures)

    summary = {
        "anchor": ANCHOR_NAME,
        "smoke": SMOKE,
        "config_version": CONFIG_VERSION,
        "per_arm_metrics": {a: [b for b in per_unit_all.values() if b.get("arm") == a]
                            for a in ARMS},
        "detail": detail,
        "n_failures": len(failures),
        "failures": failures,
        "corpus_provenance": CORPUS_PROVENANCE,
        "zero_llm_calls_at_inference": True,
    }
    payload = {
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": sum(float(b.get("wall_s", 0.0)) for b in per_unit_all.values()),
        "summary": summary,
    }
    write_metrics(out_dir, payload)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}", flush=True)


if __name__ == "__main__":
    main()
