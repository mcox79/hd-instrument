"""gap3_cls_two_tier_BCM_v2_init_fix -- BCM rescue cell (init + theta + warmup).

DESIGN PROVENANCE: research drill 2026-06-27 STUB 1 (Path A primary rescue)
  notes/research_drill_bcm_slow_learning_at_chance_3x_2026-06-27.md
PREREG: preregs/2026-06-27_gap3_cls_two_tier_BCM_v2_init_fix.md
PRIOR: exp_gap3_cls_two_tier_BCM_slow_replay_v1 (HARD_FAIL at chance 0.20;
  zero-init W + zero-init theta = degenerate fixed point dW=0 forever)

CHANGES vs v1 (load-bearing; everything else preserved):
  (1) W_schema init: torch.empty(...).normal_(mean=0.0, std=0.01)  [non-zero variance]
  (2) theta_M_per_class init: torch.full(..., 0.5)                 [warm threshold]
  (3) Two-phase BCM_FULL arm: 500 cycles Hebbian-warmup -> 4500 cycles BCM
  (4) Ablation arms isolate which fix is load-bearing

ARMS (4 mandatory; 3 BCM variants + baseline rail):
  ARM_BASELINE_SINGLE_W -- rail (must replicate ~0.37 within 0.05).
  ARM_BCM_V2_INIT_ONLY  -- random init only (theta=0, no warmup); ablation.
  ARM_BCM_V2_WARMUP_ONLY -- zero init + Hebbian warmup (no theta init); ablation.
  ARM_BCM_V2_FULL       -- init + theta=0.5 + 500c warmup + 4500c BCM; primary.

MANDATORY SMOKE DISCRIMINATOR (META_RULE_K):
  Smoke at N_DIM=2048 records first-200-cycle |y| trace for BCM_V2_FULL.
  If max(|y|) within first 200 cycles < 0.01 -> RuntimeError(degenerate_fixed_point).
  Catches the v1 trap: smoke proves the discriminator FIRES, not just that
  the cell runs.

USER 2026-06-27 NO LOCAL SMOKE: smoke + full both routed to remote_cpu_queue.

PROT-021: imports _seed_checkpoint (timeout >= 14400s).
ASCII-only. Single-file. Resumable per (seed, arm) checkpoint key.

Author: exp_dev 2026-06-27 (BCM rescue cell; under Research lead).
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

ANCHOR_NAME = "gap3_cls_two_tier_BCM_v2_init_fix"
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_class_prototypes_BCM_v2_init_fix"

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
HP_HELDOUT_ACC_FLOOR = 0.65       # BCM_V2_FULL learning happens (>HP_BASELINE_MAX=0.5)
HP_LIFT_OVER_BASELINE = 0.15      # BCM_V2_FULL > baseline by margin
HP_BCM_OVER_INIT_ONLY = 0.05      # combined fix > init-only ablation
HP_COR_SCORE_FLOOR = 0.30         # selectivity emerges (per-class W aligns)
CV_CHAIN_GRADE_MAX = 0.10         # 3 seeds dispersion ceiling
HF_BASELINE_MAX = 0.50            # methodology drift gate (rail)
W_SCHEMA_CONE_COSINE_LOW = 0.50
W_SCHEMA_CONE_COSINE_HIGH = 0.95
HF_CONE_COSINE_MIN = 0.30
MB_BCM_FLOOR = 0.50
MB_BCM_LIFT_MIN = 0.10
MIN_Y_MAGNITUDE_FIRST_200 = 0.01  # smoke discriminator threshold

assert 0.0 < HP_HELDOUT_ACC_FLOOR < 1.0, "band locked"

# ---------------- config (v2 fixes) ----------------
ETA_SLOW = 1e-3           # BCM slow-tier learning rate (unchanged)
ETA_WARM = 1e-2           # Hebbian warmup rate (10x BCM; faster coarse tuning)
THETA_M_WINDOW = 200      # BCM EWMA window (unchanged)
W_INIT_STD = 0.01         # NEW v2: non-zero W init variance (Bio-protocol)
THETA_INIT = 0.5          # NEW v2: warm theta init (BN-analog; breaks symmetry)
N_WARMUP_CYCLES = 500     # NEW v2: Hebbian warmup phase length
REPLAY_FRAC = 0.2
N_CATEGORIES = 5
N_TRAIN_PER_CAT = 20
N_HELDOUT_PER_CAT = 10
PROTOTYPE_NOISE = 0.30

if SMOKE:
    N_DIM = 2048
    N_REPLAY_CYCLES = 500          # smoke must FIRE discriminator; not just RUN
    N_WARMUP_CYCLES_SMOKE = 100
    SEEDS = [11]
else:
    N_DIM = 8192
    N_REPLAY_CYCLES = 5000          # full: 500 warmup + 4500 BCM for FULL arm
    N_WARMUP_CYCLES_SMOKE = N_WARMUP_CYCLES
    SEEDS = [11, 13, 19]

N_EPISODES = N_CATEGORIES * N_TRAIN_PER_CAT
N_HELDOUT = N_CATEGORIES * N_HELDOUT_PER_CAT

ARMS = ["ARM_BASELINE_SINGLE_W",
        "ARM_BCM_V2_INIT_ONLY",
        "ARM_BCM_V2_WARMUP_ONLY",
        "ARM_BCM_V2_FULL"]

EXPECTED_N_UNITS = len(SEEDS) * len(ARMS)

CONFIG_VERSION = (
    "BCM_v2_init_fix: N_DIM=%d N_CAT=%d N_TRAIN=%d N_HELDOUT=%d "
    "N_REPLAY=%d N_WARMUP=%d eta_slow=%.4f eta_warm=%.4f theta_window=%d "
    "W_init_std=%.3f theta_init=%.2f replay_frac=%.2f proto_noise=%.2f "
    "seeds=%s mode=%s HP_floor=%.2f HP_lift=%.2f HP_cor=%.2f cv<=%.2f "
    "cone=[%.2f,%.2f] EXPECTED_N=%d min_y_first_200=%.4f"
) % (
    N_DIM, N_CATEGORIES, N_TRAIN_PER_CAT, N_HELDOUT_PER_CAT,
    N_REPLAY_CYCLES, N_WARMUP_CYCLES, ETA_SLOW, ETA_WARM, THETA_M_WINDOW,
    W_INIT_STD, THETA_INIT, REPLAY_FRAC, PROTOTYPE_NOISE,
    SEEDS, RUN_MODE, HP_HELDOUT_ACC_FLOOR, HP_LIFT_OVER_BASELINE,
    HP_COR_SCORE_FLOOR, CV_CHAIN_GRADE_MAX, W_SCHEMA_CONE_COSINE_LOW,
    W_SCHEMA_CONE_COSINE_HIGH, EXPECTED_N_UNITS, MIN_Y_MAGNITUDE_FIRST_200,
)

_DEVICE = torch.device("cpu")  # remote_cpu_queue; CPU-bound BCM iteration


def _make_gen(seed_int: int) -> torch.Generator:
    g = torch.Generator(device=_DEVICE)
    g.manual_seed(int(seed_int))
    return g


def _random_bipolar(shape, gen: torch.Generator) -> torch.Tensor:
    X = torch.empty(*shape, device=_DEVICE, dtype=torch.float32)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return X


def _init_W_schema_random(seed_offset: int) -> torch.Tensor:
    """v2 init: normal(mean=0, std=0.01); non-zero variance escapes degeneracy."""
    g = _make_gen(seed_offset + 31)
    W = torch.empty((N_CATEGORIES, N_DIM), dtype=torch.float32, device=_DEVICE)
    W.normal_(mean=0.0, std=W_INIT_STD, generator=g)
    return W


def _init_W_schema_zero() -> torch.Tensor:
    """v1 init for ablations: zero matrix (degenerate fixed point trap)."""
    return torch.zeros((N_CATEGORIES, N_DIM), dtype=torch.float32, device=_DEVICE)


def build_class_episodes(seed_offset: int) -> tuple[torch.Tensor, torch.Tensor,
                                                     torch.Tensor, torch.Tensor,
                                                     torch.Tensor]:
    """Build prototypes + train + heldout (matches v1 exactly for cross-cell rail)."""
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
    W_norm = W_schema / (W_schema.norm(dim=1, keepdim=True) + 1e-9)
    x_norm = heldout_x / (heldout_x.norm(dim=1, keepdim=True) + 1e-9)
    sims = x_norm @ W_norm.T
    pred = sims.argmax(dim=1)
    return float((pred == heldout_y).float().mean().item())


def _eigenspectrum_entropy(W: torch.Tensor) -> float:
    if W.numel() == 0:
        return 0.0
    s = torch.linalg.svdvals(W).float()
    s = s / (s.sum() + 1e-9)
    s = torch.clamp(s, min=1e-9)
    return float(-(s * s.log()).sum().item())


def _cone_cosine(W_schema: torch.Tensor, W_episodic: torch.Tensor) -> float:
    W_s = W_schema / (W_schema.norm(dim=1, keepdim=True) + 1e-9)
    W_e = W_episodic / (W_episodic.norm(dim=1, keepdim=True) + 1e-9)
    sims = W_s @ W_e.T
    return float(sims.max(dim=1).values.mean().item())


def _bcm_update(W_row: torch.Tensor, x: torch.Tensor, theta_M: float,
                eta: float = ETA_SLOW) -> tuple[torch.Tensor, float, float]:
    """BCM sliding-threshold update. Returns (W_new, theta_new, y).

    Returns y for smoke-discriminator trace (META_RULE_K). v1 returned only
    (W_new, theta_new) which made y=0 trap impossible to detect inside the
    cell loop; v2 surfaces y to the caller.
    """
    y = float((W_row * x).sum().item())
    dW = eta * x * y * (y - theta_M)
    W_new = W_row + dW
    alpha = 1.0 / THETA_M_WINDOW
    theta_new = (1 - alpha) * theta_M + alpha * (y * y)
    return W_new, theta_new, y


def _hebbian_step(W_row: torch.Tensor, x: torch.Tensor,
                  eta: float = ETA_WARM) -> torch.Tensor:
    """Pure additive Hebbian; symmetry-breaking warmup."""
    return W_row + eta * x


def _per_class_cor_score(W_schema: torch.Tensor, heldout_x: torch.Tensor,
                         heldout_y: torch.Tensor) -> float:
    """Selectivity score: per-class accuracy correlated with assigned-row
    cosine alignment to held-out class mean. Higher = more selective (BCM
    actually contributed beyond uniform accuracy)."""
    W_norm = W_schema / (W_schema.norm(dim=1, keepdim=True) + 1e-9)
    per_class_acc = []
    per_class_align = []
    for c in range(N_CATEGORIES):
        mask = (heldout_y == c)
        if int(mask.sum().item()) == 0:
            per_class_acc.append(0.0)
            per_class_align.append(0.0)
            continue
        x_c = heldout_x[mask]
        x_norm = x_c / (x_c.norm(dim=1, keepdim=True) + 1e-9)
        sims = x_norm @ W_norm.T
        pred = sims.argmax(dim=1)
        per_class_acc.append(float((pred == c).float().mean().item()))
        # selectivity: sims[:, c] mean (alignment with assigned row)
        per_class_align.append(float(sims[:, c].mean().item()))
    if N_CATEGORIES < 2:
        return 0.0
    a = torch.tensor(per_class_acc, dtype=torch.float32)
    g = torch.tensor(per_class_align, dtype=torch.float32)
    if a.std() < 1e-9 or g.std() < 1e-9:
        return 0.0
    cov = ((a - a.mean()) * (g - g.mean())).sum().item() / (N_CATEGORIES - 1)
    return float(cov / (a.std().item() * g.std().item() + 1e-9))


# ---------------- arm implementations ----------------

def eval_arm_baseline_single_w(seed_offset: int) -> dict:
    """ARM_BASELINE_SINGLE_W: mean-of-instances prototype (rail; ~0.37)."""
    _, train_x, train_y, heldout_x, heldout_y = build_class_episodes(seed_offset)
    proto = torch.zeros((N_CATEGORIES, N_DIM), dtype=torch.float32, device=_DEVICE)
    counts = torch.zeros((N_CATEGORIES,), dtype=torch.float32, device=_DEVICE)
    for ep in range(N_EPISODES):
        c = int(train_y[ep].item())
        proto[c] += train_x[ep]
        counts[c] += 1.0
    proto = proto / counts.unsqueeze(1)
    acc = _heldout_accuracy_via_prototype_match(proto, heldout_x, heldout_y)
    return {
        "heldout_acc": float(acc),
        "w_schema_cone_cosine": 1.0,
        "w_schema_eigenspectrum_entropy_delta": 0.0,
        "cor_score": 0.0,
        "max_abs_y_first_200": 0.0,  # baseline has no BCM trace
    }


def _bcm_loop(W_schema: torch.Tensor,
              theta_M_per_class: torch.Tensor,
              train_x: torch.Tensor, train_y: torch.Tensor,
              seed_offset: int, n_cycles: int,
              warmup_cycles: int = 0) -> tuple[torch.Tensor, torch.Tensor, float]:
    """Run optional Hebbian warmup then BCM cycles. Returns (W, theta, max|y|@first200).

    max_abs_y_first_200 traces over the BCM phase only (post-warmup if any).
    """
    g = _make_gen(seed_offset + 19)
    max_abs_y_first_200 = 0.0
    bcm_cycle_index = 0
    for cycle in range(n_cycles):
        n_replay = max(1, int(REPLAY_FRAC * N_EPISODES))
        perm = torch.randperm(N_EPISODES, generator=g, device=_DEVICE)[:n_replay]
        for ep in perm.tolist():
            c = int(train_y[ep].item())
            x_sample = train_x[ep]
            if cycle < warmup_cycles:
                # Hebbian additive (no y-multiplier; symmetry-breaking)
                W_schema[c] = _hebbian_step(W_schema[c], x_sample)
            else:
                theta = float(theta_M_per_class[c].item())
                W_new, theta_new, y = _bcm_update(W_schema[c], x_sample, theta)
                W_schema[c] = W_new
                theta_M_per_class[c] = theta_new
                if bcm_cycle_index < 200:
                    if abs(y) > max_abs_y_first_200:
                        max_abs_y_first_200 = abs(y)
        if cycle >= warmup_cycles:
            bcm_cycle_index += 1
    return W_schema, theta_M_per_class, max_abs_y_first_200


def _eval_bcm_variant(seed_offset: int,
                      init_random: bool,
                      theta_warm: bool,
                      use_warmup: bool,
                      arm_name: str) -> dict:
    """Generic BCM arm runner. ARMS differ ONLY in (init_random, theta_warm, use_warmup)."""
    prototypes, train_x, train_y, heldout_x, heldout_y = build_class_episodes(seed_offset)
    W_episodic = train_x.clone()
    if init_random:
        W_schema = _init_W_schema_random(seed_offset)
    else:
        W_schema = _init_W_schema_zero()
    if theta_warm:
        theta_M_per_class = torch.full((N_CATEGORIES,), THETA_INIT,
                                       dtype=torch.float32, device=_DEVICE)
    else:
        theta_M_per_class = torch.zeros((N_CATEGORIES,), dtype=torch.float32, device=_DEVICE)
    entropy_start = _eigenspectrum_entropy(W_schema)
    warmup = N_WARMUP_CYCLES if use_warmup else 0
    if SMOKE:
        warmup = N_WARMUP_CYCLES_SMOKE if use_warmup else 0
    W_schema, theta_M_per_class, max_y = _bcm_loop(
        W_schema, theta_M_per_class, train_x, train_y,
        seed_offset, N_REPLAY_CYCLES, warmup_cycles=warmup,
    )
    entropy_end = _eigenspectrum_entropy(W_schema)
    acc = _heldout_accuracy_via_prototype_match(W_schema, heldout_x, heldout_y)
    cone_cos = _cone_cosine(W_schema, W_episodic)
    cor_score = _per_class_cor_score(W_schema, heldout_x, heldout_y)
    return {
        "heldout_acc": float(acc),
        "w_schema_cone_cosine": float(cone_cos),
        "w_schema_eigenspectrum_entropy_delta": float(entropy_end - entropy_start),
        "cor_score": float(cor_score),
        "max_abs_y_first_200": float(max_y),
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
    cor_by_arm: Dict[str, List[float]] = {a: [] for a in ARMS}
    max_y_by_arm: Dict[str, List[float]] = {a: [] for a in ARMS}
    for body in per_unit.values():
        arm = body["arm"]
        by_arm[arm].append(float(body["heldout_acc"]))
        cone_by_arm[arm].append(float(body["w_schema_cone_cosine"]))
        entropy_delta_by_arm[arm].append(float(body["w_schema_eigenspectrum_entropy_delta"]))
        cor_by_arm[arm].append(float(body.get("cor_score", 0.0)))
        max_y_by_arm[arm].append(float(body.get("max_abs_y_first_200", 0.0)))

    def stats(vals):
        if not vals:
            return float("nan"), float("nan"), 0
        m = float(np.mean(vals))
        s = float(np.std(vals)) if len(vals) > 1 else 0.0
        cv = float(s / max(m, 1e-9)) if m > 1e-9 else 0.0
        return round(m, 4), round(cv, 4), len(vals)

    baseline_m, baseline_cv, _ = stats(by_arm["ARM_BASELINE_SINGLE_W"])
    init_only_m, init_only_cv, _ = stats(by_arm["ARM_BCM_V2_INIT_ONLY"])
    warmup_only_m, warmup_only_cv, _ = stats(by_arm["ARM_BCM_V2_WARMUP_ONLY"])
    full_m, full_cv, _ = stats(by_arm["ARM_BCM_V2_FULL"])

    full_cone = float(np.mean(cone_by_arm["ARM_BCM_V2_FULL"])) if cone_by_arm["ARM_BCM_V2_FULL"] else float("nan")
    full_entropy_delta = float(np.mean(entropy_delta_by_arm["ARM_BCM_V2_FULL"])) if entropy_delta_by_arm["ARM_BCM_V2_FULL"] else float("nan")
    full_cor = float(np.mean(cor_by_arm["ARM_BCM_V2_FULL"])) if cor_by_arm["ARM_BCM_V2_FULL"] else 0.0
    full_max_y = float(np.mean(max_y_by_arm["ARM_BCM_V2_FULL"])) if max_y_by_arm["ARM_BCM_V2_FULL"] else 0.0

    lift_over_baseline = full_m - baseline_m if not math.isnan(baseline_m) else float("nan")
    lift_over_init_only = full_m - init_only_m if not math.isnan(init_only_m) else float("nan")

    cone_in_band = W_SCHEMA_CONE_COSINE_LOW <= full_cone <= W_SCHEMA_CONE_COSINE_HIGH

    detail = {
        "cardinality_ok": cardinality_ok,
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "baseline_heldout_acc": baseline_m,
        "baseline_cv": baseline_cv,
        "init_only_heldout_acc": init_only_m,
        "init_only_cv": init_only_cv,
        "warmup_only_heldout_acc": warmup_only_m,
        "warmup_only_cv": warmup_only_cv,
        "full_heldout_acc": full_m,
        "full_cv": full_cv,
        "lift_over_baseline": round(lift_over_baseline, 4) if not math.isnan(lift_over_baseline) else None,
        "lift_over_init_only": round(lift_over_init_only, 4) if not math.isnan(lift_over_init_only) else None,
        "full_w_schema_cone_cosine": round(full_cone, 4),
        "cone_in_band": cone_in_band,
        "full_w_schema_eigenspectrum_entropy_delta": round(full_entropy_delta, 4),
        "compression_happened": full_entropy_delta < 0,
        "full_cor_score": round(full_cor, 4),
        "full_max_abs_y_first_200": round(full_max_y, 6),
        "y_degeneracy_escaped": full_max_y >= MIN_Y_MAGNITUDE_FIRST_200,
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
    if not detail["y_degeneracy_escaped"]:
        return ("HARD_FAIL",
                f"BCM_DEGENERATE_FIXED_POINT: full_max_abs_y_first_200={full_max_y:.6f} "
                f"< {MIN_Y_MAGNITUDE_FIRST_200}; v2 init+theta+warmup did NOT escape "
                f"v1's W=0,theta=0 trap (y stayed at zero -> dW=0 forever)",
                detail)
    # All BCM v2 arms within 0.05 of baseline -> mechanism null
    near_baseline = (abs(init_only_m - baseline_m) < 0.05 and
                     abs(warmup_only_m - baseline_m) < 0.05 and
                     abs(full_m - baseline_m) < 0.05)
    if near_baseline:
        return ("HARD_FAIL",
                f"mechanism_null: all BCM_v2 arms within 0.05 of baseline "
                f"(baseline={baseline_m:.4f}, init_only={init_only_m:.4f}, "
                f"warmup_only={warmup_only_m:.4f}, full={full_m:.4f})",
                detail)
    if full_cone < HF_CONE_COSINE_MIN:
        return ("HARD_FAIL",
                f"w_schema_off_cone: full_cone={full_cone:.4f} < {HF_CONE_COSINE_MIN}",
                detail)

    # HARD_PASS conditions
    hp_floor_ok = full_m >= HP_HELDOUT_ACC_FLOOR
    hp_lift_ok = (not math.isnan(lift_over_baseline)) and lift_over_baseline >= HP_LIFT_OVER_BASELINE
    hp_cor_ok = full_cor >= HP_COR_SCORE_FLOOR
    hp_cv_ok = full_cv <= CV_CHAIN_GRADE_MAX
    if hp_floor_ok and hp_lift_ok and hp_cor_ok and hp_cv_ok and cone_in_band:
        return ("HARD_PASS",
                f"BCM_v2_RESCUE: full={full_m:.4f} >= {HP_HELDOUT_ACC_FLOOR}; "
                f"lift={lift_over_baseline:.4f} >= {HP_LIFT_OVER_BASELINE}; "
                f"cor_score={full_cor:.4f} >= {HP_COR_SCORE_FLOOR} (selectivity emerges); "
                f"cv={full_cv:.4f} <= {CV_CHAIN_GRADE_MAX}; "
                f"cone={full_cone:.4f} in [{W_SCHEMA_CONE_COSINE_LOW},"
                f"{W_SCHEMA_CONE_COSINE_HIGH}]; y_max_first200={full_max_y:.4f} "
                f"(degeneracy escaped)",
                detail)

    # MIDDLE_BAND
    if full_m >= MB_BCM_FLOOR and (not math.isnan(lift_over_baseline)) and lift_over_baseline >= MB_BCM_LIFT_MIN:
        return ("MIDDLE_BAND",
                f"partial_rescue: full={full_m:.4f}; lift={lift_over_baseline:.4f}; "
                f"cor={full_cor:.4f}; cone_in_band={cone_in_band}; "
                f"compression={detail['compression_happened']}",
                detail)
    return ("MIDDLE_BAND",
            f"below_MB_floor_or_no_lift: full={full_m:.4f}; "
            f"lift={lift_over_baseline if lift_over_baseline is not None else 'nan'}",
            detail)


# ---------------- self-test ----------------

def _selftest():
    print("[selftest] gap3_cls_two_tier_BCM_v2_init_fix starting", flush=True)

    # T1: v1 zero-init reproduces the degenerate fixed point trap
    W_zero = torch.zeros(3, dtype=torch.float32)
    x = torch.tensor([1.0, -1.0, 1.0], dtype=torch.float32)
    W_new, theta_new, y = _bcm_update(W_zero, x, 0.0)
    assert y == 0.0, f"T1 v1 zero-init: expected y=0, got {y}"
    assert torch.allclose(W_new, W_zero), f"T1 v1: W must not move from zero"
    assert theta_new == 0.0, f"T1 v1: theta must stay zero"
    print(f"[selftest] T1 PASS: v1 zero-init reproduces W=0,theta=0,y=0 trap", flush=True)

    # T2: v2 non-zero init breaks the trap
    g = torch.Generator(); g.manual_seed(42)
    W_v2 = torch.empty(8, dtype=torch.float32)
    W_v2.normal_(mean=0.0, std=W_INIT_STD, generator=g)
    x = torch.tensor([1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0], dtype=torch.float32)
    W_new, theta_new, y = _bcm_update(W_v2, x, THETA_INIT)
    assert abs(y) > 0.0, f"T2 v2: y must be non-zero with non-zero init, got {y}"
    assert not torch.allclose(W_new, W_v2), f"T2 v2: W must move with non-zero init"
    print(f"[selftest] T2 PASS: v2 init+theta breaks degenerate trap (y={y:.6f})", flush=True)

    # T3: BCM rule arithmetic correctness (regression on v1 formula)
    W_row = torch.tensor([0.5, 0.5, 0.5], dtype=torch.float32)
    x = torch.tensor([1.0, 1.0, 1.0], dtype=torch.float32)
    theta_M = 0.5
    W_new, theta_new, y = _bcm_update(W_row, x, theta_M)
    assert abs(y - 1.5) < 1e-6, f"T3: y={y} expected 1.5"
    expected_W = W_row + ETA_SLOW * x * 1.5 * (1.5 - 0.5)
    assert torch.allclose(W_new, expected_W, atol=1e-6), f"T3 BCM update wrong"
    expected_theta = (1 - 1/200) * 0.5 + (1/200) * 2.25
    assert abs(theta_new - expected_theta) < 1e-6, f"T3 theta wrong"
    print(f"[selftest] T3 PASS: BCM rule arithmetic", flush=True)

    # T4: Hebbian warmup step correctness
    W_row = torch.zeros(4, dtype=torch.float32)
    x = torch.tensor([1.0, -1.0, 1.0, -1.0], dtype=torch.float32)
    W_after = _hebbian_step(W_row, x)
    expected = ETA_WARM * x
    assert torch.allclose(W_after, expected, atol=1e-6), f"T4 Hebbian wrong"
    print(f"[selftest] T4 PASS: Hebbian warmup additive (eta_warm={ETA_WARM})", flush=True)

    # T5: verdict-machinery HARD_PASS synthetic path
    fake_hp = {}
    for s in [11, 13, 19]:
        fake_hp[f"{s}_ARM_BASELINE_SINGLE_W"] = {
            "arm": "ARM_BASELINE_SINGLE_W", "heldout_acc": 0.37,
            "w_schema_cone_cosine": 1.0,
            "w_schema_eigenspectrum_entropy_delta": 0.0,
            "cor_score": 0.0, "max_abs_y_first_200": 0.0,
        }
        fake_hp[f"{s}_ARM_BCM_V2_INIT_ONLY"] = {
            "arm": "ARM_BCM_V2_INIT_ONLY", "heldout_acc": 0.55,
            "w_schema_cone_cosine": 0.72,
            "w_schema_eigenspectrum_entropy_delta": -0.05,
            "cor_score": 0.25, "max_abs_y_first_200": 0.5,
        }
        fake_hp[f"{s}_ARM_BCM_V2_WARMUP_ONLY"] = {
            "arm": "ARM_BCM_V2_WARMUP_ONLY", "heldout_acc": 0.60,
            "w_schema_cone_cosine": 0.75,
            "w_schema_eigenspectrum_entropy_delta": -0.08,
            "cor_score": 0.28, "max_abs_y_first_200": 0.3,
        }
        fake_hp[f"{s}_ARM_BCM_V2_FULL"] = {
            "arm": "ARM_BCM_V2_FULL", "heldout_acc": 0.72,
            "w_schema_cone_cosine": 0.80,
            "w_schema_eigenspectrum_entropy_delta": -0.15,
            "cor_score": 0.40, "max_abs_y_first_200": 0.6,
        }
    global EXPECTED_N_UNITS
    saved = EXPECTED_N_UNITS
    EXPECTED_N_UNITS = 12
    try:
        v, msg, det = compute_verdict(fake_hp)
        assert v == "HARD_PASS", f"T5 expected HARD_PASS, got {v}: {msg}"
        print(f"[selftest] T5 PASS: synthetic HARD_PASS path", flush=True)

        # T6: degenerate fixed point trap detection (v1 trap re-played)
        fake_trap = {k: dict(v) for k, v in fake_hp.items()}
        for k in fake_trap:
            if "FULL" in k:
                fake_trap[k]["max_abs_y_first_200"] = 0.0  # never escaped
                fake_trap[k]["heldout_acc"] = 0.20         # at chance
        v, msg, det = compute_verdict(fake_trap)
        assert v == "HARD_FAIL", f"T6 expected HARD_FAIL, got {v}"
        assert "DEGENERATE_FIXED_POINT" in msg, f"T6 expected degeneracy msg, got {msg}"
        print(f"[selftest] T6 PASS: y=0 degenerate trap caught by verdict", flush=True)

        # T7: methodology drift
        fake_drift = {k: dict(v) for k, v in fake_hp.items()}
        for k in fake_drift:
            if "BASELINE" in k:
                fake_drift[k]["heldout_acc"] = 0.55
        v, msg, det = compute_verdict(fake_drift)
        assert v == "HARD_FAIL" and "methodology_drift" in msg, f"T7 wrong: {v}/{msg}"
        print(f"[selftest] T7 PASS: methodology drift -> HARD_FAIL", flush=True)

        # T8: cardinality breach
        fake_card = dict(list(fake_hp.items())[:6])
        v, msg, det = compute_verdict(fake_card)
        assert v == "HARD_FAIL" and "cardinality" in msg, f"T8 wrong: {v}/{msg}"
        print(f"[selftest] T8 PASS: cardinality_breach -> HARD_FAIL", flush=True)

        # T9: MIDDLE_BAND partial rescue
        fake_mb = {k: dict(v) for k, v in fake_hp.items()}
        for k in fake_mb:
            if "FULL" in k:
                fake_mb[k]["heldout_acc"] = 0.55   # below HP floor but above MB floor
        v, msg, det = compute_verdict(fake_mb)
        assert v == "MIDDLE_BAND", f"T9 expected MIDDLE_BAND, got {v}"
        print(f"[selftest] T9 PASS: partial rescue -> MIDDLE_BAND", flush=True)
    finally:
        EXPECTED_N_UNITS = saved

    # T10: pre-reg envelope locks
    assert HP_HELDOUT_ACC_FLOOR == 0.65
    assert HP_LIFT_OVER_BASELINE == 0.15
    assert HP_COR_SCORE_FLOOR == 0.30
    assert CV_CHAIN_GRADE_MAX == 0.10
    assert ETA_SLOW == 1e-3 and ETA_WARM == 1e-2
    assert W_INIT_STD == 0.01 and THETA_INIT == 0.5
    assert N_WARMUP_CYCLES == 500
    assert MIN_Y_MAGNITUDE_FIRST_200 == 0.01
    print(f"[selftest] T10 PASS: pre-reg envelope constants LOCKED", flush=True)

    print("[selftest] ALL PASS", flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ---------------- main runner ----------------

# Arm config table: (init_random, theta_warm, use_warmup)
_ARM_CONFIG = {
    "ARM_BCM_V2_INIT_ONLY":   (True,  False, False),
    "ARM_BCM_V2_WARMUP_ONLY": (False, False, True),
    "ARM_BCM_V2_FULL":        (True,  True,  True),
}


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
    elif arm in _ARM_CONFIG:
        init_random, theta_warm, use_warmup = _ARM_CONFIG[arm]
        out = _eval_bcm_variant(seed_offset, init_random, theta_warm, use_warmup, arm)
        # Smoke discriminator: FULL arm must escape y-degeneracy within first 200 cycles
        if SMOKE and arm == "ARM_BCM_V2_FULL":
            if out["max_abs_y_first_200"] < MIN_Y_MAGNITUDE_FIRST_200:
                raise RuntimeError(
                    f"SMOKE_DISCRIMINATOR_FAILED: BCM_V2_FULL max|y| over first 200 "
                    f"BCM cycles = {out['max_abs_y_first_200']:.6f} < "
                    f"{MIN_Y_MAGNITUDE_FIRST_200}; v2 init+theta+warmup did NOT "
                    f"escape v1's degenerate fixed point. Halt before full dispatch "
                    f"(META_RULE_K)."
                )
    else:
        raise ValueError(f"unknown arm: {arm}")
    body.update(out)
    body["wall_s"] = float(round(time.time() - t0, 2))
    return body


def main():
    import traceback as _tb
    out_dir = get_output_dir(ANCHOR_NAME)
    done_keys = set(list_completed_keys(out_dir))
    print(f"[run] {ANCHOR_NAME} smoke={SMOKE} {CONFIG_VERSION}", flush=True)
    print(f"[run] EXPECTED_N_UNITS={EXPECTED_N_UNITS} done={len(done_keys)}", flush=True)

    failures: List[Dict] = []
    per_unit: Dict[str, Dict] = {}

    # v2_init_fix exception-surface patch (2026-06-27): a prior remote run
    # crashed in _bcm_loop with `RuntimeError: value cannot be converted to
    # type float without overflow` (BCM update at N_DIM=8192 blew up theta
    # after the baseline arm passed). The raise propagated and main() exited
    # WITHOUT writing metrics.json -- runner saw missing-metrics, Director
    # had no HARD_FAIL artifact to atomize, true failure mode invisible.
    # META_RULE_J fix: surface the exception as a structured
    # HARD_FAIL_UNIT_EXCEPTION metrics.json BEFORE re-raising, so the
    # failure is visible to the verdict pipeline.
    crash_key: str | None = None
    crash_exc_type: str | None = None
    crash_exc_msg: str | None = None
    crash_tb: str | None = None

    try:
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
                          f"cor={body['cor_score']:.4f} "
                          f"max_y={body['max_abs_y_first_200']:.4f} "
                          f"wall={body['wall_s']}s", flush=True)
                except Exception as e:
                    fail = {
                        "key": key,
                        "exc_type": type(e).__name__,
                        "exc_msg": str(e),
                        "exc_traceback": _tb.format_exc(),
                    }
                    failures.append(fail)
                    crash_key = key
                    crash_exc_type = type(e).__name__
                    crash_exc_msg = str(e)
                    crash_tb = _tb.format_exc()
                    print(f"  [{key}] FAILED: {e}", flush=True)
                    raise  # META_RULE_J no silent except
    except Exception:
        # Write a HARD_FAIL_UNIT_EXCEPTION metrics.json with full crash
        # details BEFORE re-raising, so the runner + Director see a
        # structured failure artifact instead of missing-metrics silence.
        per_unit_partial = aggregate_partials(out_dir)
        fail_summary = {
            "anchor": ANCHOR_NAME,
            "smoke": SMOKE,
            "config_version": CONFIG_VERSION,
            "per_arm_metrics": {a: [b for b in per_unit_partial.values()
                                    if b.get("arm") == a]
                                for a in ARMS},
            "n_completed_units": len(per_unit_partial),
            "n_expected_units": EXPECTED_N_UNITS,
            "n_failures": len(failures),
            "failures": failures,
            "crash_key": crash_key,
            "crash_exc_type": crash_exc_type,
            "crash_exc_msg": crash_exc_msg,
            "crash_traceback": crash_tb,
            "corpus_provenance": CORPUS_PROVENANCE,
            "zero_llm_calls_at_inference": True,
        }
        fail_payload = {
            "verdict": "HARD_FAIL",
            "verdict_msg": (
                f"HARD_FAIL_UNIT_EXCEPTION: key={crash_key} "
                f"exc_type={crash_exc_type} exc_msg={crash_exc_msg!r} "
                f"(completed {len(per_unit_partial)}/{EXPECTED_N_UNITS} "
                f"units before crash)"
            ),
            "elapsed_s": sum(float(b.get("wall_s", 0.0))
                             for b in per_unit_partial.values()),
            "summary": fail_summary,
        }
        try:
            write_metrics(out_dir, fail_payload)
            print(f"\n[verdict] HARD_FAIL_UNIT_EXCEPTION", flush=True)
            print(f"[verdict_msg] {fail_payload['verdict_msg']}", flush=True)
            print(f"[metrics] HARD_FAIL metrics.json WRITTEN before re-raise",
                  flush=True)
        except Exception as write_exc:
            # If metrics write fails, log it but re-raise the original crash.
            print(f"[metrics] WRITE_FAILED while surfacing crash: {write_exc}",
                  flush=True)
        raise  # propagate so runner exit code is non-zero (HARD_FAIL signal)

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
