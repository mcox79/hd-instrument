"""gap3_cls_two_tier_HOPFIELD_consolidation_v1 -- substrate-native CLS slow rule.

DESIGN PROVENANCE: research drill 2026-06-27 STUB 3 (Path C lowest dev cost)
  notes/research_drill_bcm_slow_learning_at_chance_3x_2026-06-27.md
PREREG: preregs/2026-06-27_gap3_cls_two_tier_HOPFIELD_consolidation_v1.md
PRIOR: exp_gap3_cls_two_tier_BCM_slow_replay_v1 (HARD_FAIL at chance; BCM trap)

MECHANISM: drop BCM entirely; use substrate-native chain-grade NREM replay
primitive (atom 588; hdlab.continual.replay_cycle) for slow consolidation.
Replay REINFORCES attractor basins via weighted Hebbian re-write. NO
multiplicative-y plasticity -> NO degenerate fixed point. Brain analog:
Hopfield-style attractor consolidation during NREM sleep ripples
(Whittington-Behrens 2024 family; McClelland 1995 CLS).

ARMS (4 mandatory):
  ARM_BASELINE_HEBBIAN              -- rail (mean-of-instances; ~0.37; HP_BASELINE_MAX<=0.50)
  ARM_HEBBIAN_SLOW                  -- fast-tier Hebbian only, no replay (rail vs replay)
  ARM_HOPFIELD_REPLAY_SLOW          -- primary: NREM replay over STORED episodes
  ARM_HOPFIELD_GENERATIVE_REPLAY    -- variant: NREM replay over GENERATED (prototype+noise)
                                       patterns; brain DMN consolidation analog

USER 2026-06-27 NO LOCAL SMOKE: smoke + full both routed to remote_cpu_queue.

META_RULES H/J/K/L/M + SCHEMA-VET 5b per-arm HP scope.
PROT-021: imports _seed_checkpoint (timeout >= 14400s).
ASCII-only. Single-file. Resumable per (seed, arm) checkpoint key.

Author: exp_dev 2026-06-27 (substrate-native CLS slow-rule; under Research lead).
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
# Compose on chain-grade NREM replay primitive (atom 588; drift_reduction +0.57 bound)
from hdlab.continual import replay_cycle

ANCHOR_NAME = "gap3_cls_two_tier_HOPFIELD_consolidation_v1"
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_class_prototypes_HOPFIELD_NREM_replay"

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
HP_HELDOUT_ACC_FLOOR = 0.65
HP_LIFT_OVER_HEBBIAN = 0.10         # primary mechanism vs Hebbian fast-tier baseline
HP_LIFT_OVER_BASELINE = 0.20
HP_COR_SCORE_FLOOR = 0.30
CV_CHAIN_GRADE_MAX = 0.10
HF_BASELINE_MAX = 0.50              # methodology drift gate
W_SCHEMA_CONE_COSINE_LOW = 0.50
W_SCHEMA_CONE_COSINE_HIGH = 0.95
HF_CONE_COSINE_MIN = 0.30
MB_FLOOR = 0.50
MB_LIFT_MIN = 0.10

assert 0.0 < HP_HELDOUT_ACC_FLOOR < 1.0, "band locked"

# ---------------- config ----------------
ETA_FAST = 1.0                # Hebbian fast-tier write rate (per episode)
ETA_REPLAY = 1.0              # NREM replay re-Hebb lr (matches replay_cycle default)
REPLAY_FRAC = 0.2             # chain-grade NREM replay default
REPLAY_EVERY = 100            # chain-grade NREM replay default
N_CATEGORIES = 5
N_TRAIN_PER_CAT = 20
N_HELDOUT_PER_CAT = 10
PROTOTYPE_NOISE = 0.30

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

ARMS = ["ARM_BASELINE_HEBBIAN",
        "ARM_HEBBIAN_SLOW",
        "ARM_HOPFIELD_REPLAY_SLOW",
        "ARM_HOPFIELD_GENERATIVE_REPLAY"]

EXPECTED_N_UNITS = len(SEEDS) * len(ARMS)

CONFIG_VERSION = (
    "HOPFIELD_consolidation_v1: N_DIM=%d N_CAT=%d N_TRAIN=%d N_HELDOUT=%d "
    "N_REPLAY=%d eta_fast=%.2f eta_replay=%.2f replay_frac=%.2f "
    "replay_every=%d proto_noise=%.2f seeds=%s mode=%s "
    "HP_floor=%.2f HP_lift_over_hebb=%.2f HP_lift_over_baseline=%.2f "
    "HP_cor=%.2f cv<=%.2f cone=[%.2f,%.2f] EXPECTED_N=%d"
) % (
    N_DIM, N_CATEGORIES, N_TRAIN_PER_CAT, N_HELDOUT_PER_CAT,
    N_REPLAY_CYCLES, ETA_FAST, ETA_REPLAY, REPLAY_FRAC, REPLAY_EVERY,
    PROTOTYPE_NOISE, SEEDS, RUN_MODE,
    HP_HELDOUT_ACC_FLOOR, HP_LIFT_OVER_HEBBIAN, HP_LIFT_OVER_BASELINE,
    HP_COR_SCORE_FLOOR, CV_CHAIN_GRADE_MAX, W_SCHEMA_CONE_COSINE_LOW,
    W_SCHEMA_CONE_COSINE_HIGH, EXPECTED_N_UNITS,
)

_DEVICE = torch.device("cpu")


def _make_gen(seed_int: int) -> torch.Generator:
    g = torch.Generator(device=_DEVICE)
    g.manual_seed(int(seed_int))
    return g


def _random_bipolar(shape, gen: torch.Generator) -> torch.Tensor:
    X = torch.empty(*shape, device=_DEVICE, dtype=torch.float32)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return X


def build_class_episodes(seed_offset: int) -> tuple[torch.Tensor, torch.Tensor,
                                                     torch.Tensor, torch.Tensor,
                                                     torch.Tensor]:
    """Build prototypes + train + heldout (matches v1 EXACTLY for cross-cell rail)."""
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


def _per_class_cor_score(W_schema: torch.Tensor, heldout_x: torch.Tensor,
                         heldout_y: torch.Tensor) -> float:
    """Selectivity: per-class acc correlated with assigned-row alignment."""
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

def eval_arm_baseline_hebbian(seed_offset: int) -> dict:
    """ARM_BASELINE_HEBBIAN: mean-of-instances prototype (rail; ~0.37; HP_BASELINE_MAX<=0.5)."""
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
        "n_replay_cycles_applied": 0,
    }


def _hebbian_fast_tier(seed_offset: int) -> tuple[torch.Tensor, torch.Tensor,
                                                    torch.Tensor, torch.Tensor,
                                                    torch.Tensor]:
    """Build W_schema via single-pass fast-tier Hebbian writes.

    Returns (W_schema [C, N], train_x, train_y, heldout_x, heldout_y).
    """
    _, train_x, train_y, heldout_x, heldout_y = build_class_episodes(seed_offset)
    W_schema = torch.zeros((N_CATEGORIES, N_DIM), dtype=torch.float32, device=_DEVICE)
    for ep in range(N_EPISODES):
        c = int(train_y[ep].item())
        W_schema[c] += ETA_FAST * train_x[ep]
    return W_schema, train_x, train_y, heldout_x, heldout_y


def eval_arm_hebbian_slow(seed_offset: int) -> dict:
    """ARM_HEBBIAN_SLOW: fast-tier Hebbian only; NO replay. Rail vs Hopfield arms."""
    W_schema, train_x, train_y, heldout_x, heldout_y = _hebbian_fast_tier(seed_offset)
    W_episodic = train_x.clone()
    entropy_start = _eigenspectrum_entropy(W_schema)  # post fast-tier
    entropy_end = entropy_start  # no further training
    acc = _heldout_accuracy_via_prototype_match(W_schema, heldout_x, heldout_y)
    cone_cos = _cone_cosine(W_schema, W_episodic)
    cor = _per_class_cor_score(W_schema, heldout_x, heldout_y)
    return {
        "heldout_acc": float(acc),
        "w_schema_cone_cosine": float(cone_cos),
        "w_schema_eigenspectrum_entropy_delta": float(entropy_end - entropy_start),
        "cor_score": float(cor),
        "n_replay_cycles_applied": 0,
    }


def _eval_hopfield_consolidation(seed_offset: int,
                                  generative: bool) -> dict:
    """Generic Hopfield-consolidation runner.

    Uses chain-grade NREM replay primitive (atom 588). Each replay cycle re-Hebbs
    REPLAY_FRAC of stored (or generated) traces back into W_schema (re-treated as
    a [V_DIM, K_DIM] associative weight, V_DIM=N_DIM, K_DIM=N_CATEGORIES one-hot).

    The substrate-native attractor consolidation: replay reinforces basins
    proportionally to how often a class is replayed; no multiplicative-y, no
    degenerate fixed point.
    """
    prototypes, train_x, train_y, heldout_x, heldout_y = build_class_episodes(seed_offset)
    W_episodic = train_x.clone()

    # Fast-tier Hebbian initial write (mimics McClelland 1995 HC->NC pipeline)
    W_schema = torch.zeros((N_CATEGORIES, N_DIM), dtype=torch.float32, device=_DEVICE)
    for ep in range(N_EPISODES):
        c = int(train_y[ep].item())
        W_schema[c] += ETA_FAST * train_x[ep]
    entropy_start = _eigenspectrum_entropy(W_schema)

    # Treat W_schema as [V_DIM, K_DIM] = [N_DIM, N_CATEGORIES] for replay_cycle.
    # keys = one-hot class identifiers [M, N_CATEGORIES]; values = patterns [M, N_DIM].
    W_for_replay = W_schema.T.contiguous()  # [N_DIM, N_CATEGORIES]

    g_gen = _make_gen(seed_offset + 23)
    g_rep = _make_gen(seed_offset + 29)

    n_replay_cycles_applied = 0
    for cycle in range(N_REPLAY_CYCLES):
        if cycle % REPLAY_EVERY != 0:
            continue
        # Build the trace buffer for this replay event
        if generative:
            # Generative replay: synthesize prototype+noise patterns for ALL classes
            # (brain DMN consolidation analog; Olafsdottir-McClelland)
            M = N_EPISODES  # match stored cardinality
            patterns = torch.zeros((M, N_DIM), dtype=torch.float32, device=_DEVICE)
            class_ids = torch.zeros((M,), dtype=torch.long, device=_DEVICE)
            for m in range(M):
                c = m % N_CATEGORIES
                n_flip = int(PROTOTYPE_NOISE * N_DIM)
                flip_mask = torch.zeros(N_DIM, dtype=torch.bool, device=_DEVICE)
                p2 = torch.randperm(N_DIM, generator=g_gen, device=_DEVICE)
                flip_mask[p2[:n_flip]] = True
                patt = prototypes[c].clone()
                patt[flip_mask] = -patt[flip_mask]
                patterns[m] = patt
                class_ids[m] = c
        else:
            # Replay over STORED training episodes (literal HC traces)
            patterns = train_x
            class_ids = train_y

        # One-hot keys [M, N_CATEGORIES]
        M = patterns.shape[0]
        keys = torch.zeros((M, N_CATEGORIES), dtype=torch.float32, device=_DEVICE)
        keys[torch.arange(M, device=_DEVICE), class_ids] = 1.0
        replay_indices = torch.arange(M, dtype=torch.long, device=_DEVICE)
        # values = patterns [M, N_DIM] = [M, V_DIM]
        W_for_replay = replay_cycle(
            W_for_replay, replay_indices, keys, patterns,
            replay_frac=REPLAY_FRAC, lr=ETA_REPLAY,
        )
        n_replay_cycles_applied += 1

    # Pull W_schema back to [C, N] form
    W_schema = W_for_replay.T.contiguous()
    entropy_end = _eigenspectrum_entropy(W_schema)
    acc = _heldout_accuracy_via_prototype_match(W_schema, heldout_x, heldout_y)
    cone_cos = _cone_cosine(W_schema, W_episodic)
    cor = _per_class_cor_score(W_schema, heldout_x, heldout_y)
    return {
        "heldout_acc": float(acc),
        "w_schema_cone_cosine": float(cone_cos),
        "w_schema_eigenspectrum_entropy_delta": float(entropy_end - entropy_start),
        "cor_score": float(cor),
        "n_replay_cycles_applied": int(n_replay_cycles_applied),
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
    entropy_by_arm: Dict[str, List[float]] = {a: [] for a in ARMS}
    cor_by_arm: Dict[str, List[float]] = {a: [] for a in ARMS}
    for body in per_unit.values():
        arm = body["arm"]
        by_arm[arm].append(float(body["heldout_acc"]))
        cone_by_arm[arm].append(float(body["w_schema_cone_cosine"]))
        entropy_by_arm[arm].append(float(body["w_schema_eigenspectrum_entropy_delta"]))
        cor_by_arm[arm].append(float(body.get("cor_score", 0.0)))

    def stats(vals):
        if not vals:
            return float("nan"), float("nan"), 0
        m = float(np.mean(vals))
        s = float(np.std(vals)) if len(vals) > 1 else 0.0
        cv = float(s / max(m, 1e-9)) if m > 1e-9 else 0.0
        return round(m, 4), round(cv, 4), len(vals)

    baseline_m, baseline_cv, _ = stats(by_arm["ARM_BASELINE_HEBBIAN"])
    hebb_slow_m, hebb_slow_cv, _ = stats(by_arm["ARM_HEBBIAN_SLOW"])
    hopfield_m, hopfield_cv, _ = stats(by_arm["ARM_HOPFIELD_REPLAY_SLOW"])
    hopfield_gen_m, hopfield_gen_cv, _ = stats(by_arm["ARM_HOPFIELD_GENERATIVE_REPLAY"])

    # Pick best Hopfield arm
    if math.isnan(hopfield_m) and math.isnan(hopfield_gen_m):
        best_h_m = float("nan"); best_h_cv = float("nan"); best_arm = "ARM_HOPFIELD_REPLAY_SLOW"
    elif math.isnan(hopfield_gen_m):
        best_h_m = hopfield_m; best_h_cv = hopfield_cv; best_arm = "ARM_HOPFIELD_REPLAY_SLOW"
    elif math.isnan(hopfield_m):
        best_h_m = hopfield_gen_m; best_h_cv = hopfield_gen_cv; best_arm = "ARM_HOPFIELD_GENERATIVE_REPLAY"
    elif hopfield_m >= hopfield_gen_m:
        best_h_m = hopfield_m; best_h_cv = hopfield_cv; best_arm = "ARM_HOPFIELD_REPLAY_SLOW"
    else:
        best_h_m = hopfield_gen_m; best_h_cv = hopfield_gen_cv; best_arm = "ARM_HOPFIELD_GENERATIVE_REPLAY"

    best_cone = float(np.mean(cone_by_arm[best_arm])) if cone_by_arm[best_arm] else float("nan")
    best_entropy = float(np.mean(entropy_by_arm[best_arm])) if entropy_by_arm[best_arm] else float("nan")
    best_cor = float(np.mean(cor_by_arm[best_arm])) if cor_by_arm[best_arm] else 0.0

    # Compare PRIMARY Hopfield-replay mechanism vs Hebbian (HP per drill spec)
    lift_over_hebbian = (hopfield_m - hebb_slow_m) if not (math.isnan(hopfield_m) or math.isnan(hebb_slow_m)) else float("nan")
    lift_over_baseline = (best_h_m - baseline_m) if not (math.isnan(best_h_m) or math.isnan(baseline_m)) else float("nan")
    cone_in_band = W_SCHEMA_CONE_COSINE_LOW <= best_cone <= W_SCHEMA_CONE_COSINE_HIGH

    detail = {
        "cardinality_ok": cardinality_ok,
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "baseline_heldout_acc": baseline_m,
        "baseline_cv": baseline_cv,
        "hebbian_slow_heldout_acc": hebb_slow_m,
        "hebbian_slow_cv": hebb_slow_cv,
        "hopfield_replay_heldout_acc": hopfield_m,
        "hopfield_replay_cv": hopfield_cv,
        "hopfield_generative_heldout_acc": hopfield_gen_m,
        "hopfield_generative_cv": hopfield_gen_cv,
        "best_hopfield_arm": best_arm,
        "best_hopfield_heldout_acc": best_h_m,
        "best_hopfield_cv": best_h_cv,
        "lift_hopfield_over_hebbian": round(lift_over_hebbian, 4) if not math.isnan(lift_over_hebbian) else None,
        "lift_over_baseline": round(lift_over_baseline, 4) if not math.isnan(lift_over_baseline) else None,
        "best_w_schema_cone_cosine": round(best_cone, 4),
        "cone_in_band": cone_in_band,
        "best_w_schema_eigenspectrum_entropy_delta": round(best_entropy, 4),
        "best_cor_score": round(best_cor, 4),
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
                f"methodology_drift: ARM_BASELINE_HEBBIAN={baseline_m:.4f} >= "
                f"HF_BASELINE_MAX={HF_BASELINE_MAX}; rail violated",
                detail)
    # All consolidation arms within 0.05 of baseline -> mechanism null
    near_baseline = (
        (not math.isnan(hebb_slow_m) and abs(hebb_slow_m - baseline_m) < 0.05) and
        (not math.isnan(hopfield_m) and abs(hopfield_m - baseline_m) < 0.05) and
        (not math.isnan(hopfield_gen_m) and abs(hopfield_gen_m - baseline_m) < 0.05)
    )
    if near_baseline:
        return ("HARD_FAIL",
                f"mechanism_null: all consolidation arms within 0.05 of baseline "
                f"(baseline={baseline_m:.4f}, hebb={hebb_slow_m:.4f}, "
                f"hopfield={hopfield_m:.4f}, hopfield_gen={hopfield_gen_m:.4f})",
                detail)
    if best_cone < HF_CONE_COSINE_MIN:
        return ("HARD_FAIL",
                f"w_schema_off_cone: best_cone={best_cone:.4f} < {HF_CONE_COSINE_MIN}",
                detail)

    # HARD_PASS conditions (per drill: HOPFIELD_REPLAY_SLOW vs Hebbian by >=0.10)
    hp_floor_ok = not math.isnan(hopfield_m) and hopfield_m >= HP_HELDOUT_ACC_FLOOR
    hp_lift_hebb_ok = (not math.isnan(lift_over_hebbian)) and lift_over_hebbian >= HP_LIFT_OVER_HEBBIAN
    hp_cor_ok = best_cor >= HP_COR_SCORE_FLOOR
    hp_cv_ok = (not math.isnan(hopfield_cv)) and hopfield_cv <= CV_CHAIN_GRADE_MAX
    if hp_floor_ok and hp_lift_hebb_ok and hp_cor_ok and hp_cv_ok and cone_in_band:
        return ("HARD_PASS",
                f"HOPFIELD_CONSOLIDATION_chain_grade: hopfield_replay={hopfield_m:.4f} "
                f">= {HP_HELDOUT_ACC_FLOOR}; lift_over_hebbian={lift_over_hebbian:.4f} "
                f">= {HP_LIFT_OVER_HEBBIAN}; cor_score={best_cor:.4f} >= "
                f"{HP_COR_SCORE_FLOOR}; cv={hopfield_cv:.4f} <= {CV_CHAIN_GRADE_MAX}; "
                f"cone={best_cone:.4f} in [{W_SCHEMA_CONE_COSINE_LOW},"
                f"{W_SCHEMA_CONE_COSINE_HIGH}]",
                detail)

    # MIDDLE_BAND
    if best_h_m >= MB_FLOOR and not math.isnan(lift_over_baseline) and lift_over_baseline >= MB_LIFT_MIN:
        return ("MIDDLE_BAND",
                f"partial_consolidation: best_hopfield={best_h_m:.4f}; "
                f"lift_over_baseline={lift_over_baseline:.4f}; "
                f"lift_over_hebbian={lift_over_hebbian if lift_over_hebbian is not None else 'nan'}; "
                f"cone_in_band={cone_in_band}",
                detail)
    return ("MIDDLE_BAND",
            f"below_MB_floor_or_no_lift: best_hopfield={best_h_m}; "
            f"lift_over_baseline={lift_over_baseline if lift_over_baseline is not None else 'nan'}",
            detail)


# ---------------- self-test ----------------

def _selftest():
    print("[selftest] gap3_cls_two_tier_HOPFIELD_consolidation_v1 starting", flush=True)

    # T1: NREM replay primitive composes correctly (chain-grade atom 588)
    W = torch.zeros((4, 3), dtype=torch.float32)  # [V_DIM=4, K_DIM=3]
    keys = torch.eye(3, dtype=torch.float32)[:2]   # [M=2, K_DIM=3]
    values = torch.tensor([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=torch.float32)  # [M=2, V_DIM=4]
    replay_indices = torch.arange(2, dtype=torch.long)
    W2 = replay_cycle(W, replay_indices, keys, values, replay_frac=1.0, lr=1.0)
    # delta = values.T @ keys = [[1,0,0],[0,1,0],[0,0,0],[0,0,0]]
    assert W2[0, 0].item() == 1.0 and W2[1, 1].item() == 1.0, f"T1 replay outer-sum wrong"
    print(f"[selftest] T1 PASS: chain-grade replay_cycle composes correctly", flush=True)

    # T2: NO multiplicative-y; replay add never produces zero from zero+zero (but
    # crucially, zero keys + nonzero values still produces zero delta -> not an
    # issue for our use since we always pass one-hot keys)
    W = torch.zeros((4, 3), dtype=torch.float32)
    keys = torch.zeros((2, 3), dtype=torch.float32)  # all-zero keys -> zero delta
    values = torch.tensor([[1.0, 0, 0, 0], [0, 1.0, 0, 0]], dtype=torch.float32)
    W2 = replay_cycle(W, torch.arange(2, dtype=torch.long), keys, values,
                      replay_frac=1.0, lr=1.0)
    assert torch.allclose(W2, torch.zeros_like(W2)), f"T2: zero keys -> zero delta"
    # AND with one-hot keys, even from W=0, write happens (no degeneracy)
    W3 = torch.zeros((4, 3), dtype=torch.float32)
    keys_oh = torch.eye(3, dtype=torch.float32)[:2]
    W3 = replay_cycle(W3, torch.arange(2, dtype=torch.long), keys_oh, values,
                      replay_frac=1.0, lr=1.0)
    assert W3.abs().sum().item() > 0.0, f"T2: one-hot keys must escape zero (no BCM trap)"
    print(f"[selftest] T2 PASS: one-hot key replay escapes W=0 (no BCM-style degeneracy)", flush=True)

    # T3: verdict-machinery HARD_PASS synthetic path
    fake_hp = {}
    for s in [11, 13, 19]:
        fake_hp[f"{s}_ARM_BASELINE_HEBBIAN"] = {
            "arm": "ARM_BASELINE_HEBBIAN", "heldout_acc": 0.37,
            "w_schema_cone_cosine": 1.0,
            "w_schema_eigenspectrum_entropy_delta": 0.0,
            "cor_score": 0.0, "n_replay_cycles_applied": 0,
        }
        fake_hp[f"{s}_ARM_HEBBIAN_SLOW"] = {
            "arm": "ARM_HEBBIAN_SLOW", "heldout_acc": 0.55,
            "w_schema_cone_cosine": 0.72,
            "w_schema_eigenspectrum_entropy_delta": 0.0,
            "cor_score": 0.20, "n_replay_cycles_applied": 0,
        }
        fake_hp[f"{s}_ARM_HOPFIELD_REPLAY_SLOW"] = {
            "arm": "ARM_HOPFIELD_REPLAY_SLOW", "heldout_acc": 0.72,
            "w_schema_cone_cosine": 0.80,
            "w_schema_eigenspectrum_entropy_delta": -0.10,
            "cor_score": 0.40, "n_replay_cycles_applied": 50,
        }
        fake_hp[f"{s}_ARM_HOPFIELD_GENERATIVE_REPLAY"] = {
            "arm": "ARM_HOPFIELD_GENERATIVE_REPLAY", "heldout_acc": 0.70,
            "w_schema_cone_cosine": 0.78,
            "w_schema_eigenspectrum_entropy_delta": -0.08,
            "cor_score": 0.38, "n_replay_cycles_applied": 50,
        }
    global EXPECTED_N_UNITS
    saved = EXPECTED_N_UNITS
    EXPECTED_N_UNITS = 12
    try:
        v, msg, det = compute_verdict(fake_hp)
        assert v == "HARD_PASS", f"T3 expected HARD_PASS, got {v}: {msg}"
        print(f"[selftest] T3 PASS: synthetic HARD_PASS path", flush=True)

        # T4: methodology drift
        fake_drift = {k: dict(v) for k, v in fake_hp.items()}
        for k in fake_drift:
            if "BASELINE" in k:
                fake_drift[k]["heldout_acc"] = 0.55
        v, msg, det = compute_verdict(fake_drift)
        assert v == "HARD_FAIL" and "methodology_drift" in msg, f"T4 wrong: {v}/{msg}"
        print(f"[selftest] T4 PASS: methodology drift -> HARD_FAIL", flush=True)

        # T5: cardinality breach
        fake_card = dict(list(fake_hp.items())[:6])
        v, msg, det = compute_verdict(fake_card)
        assert v == "HARD_FAIL" and "cardinality" in msg, f"T5 wrong: {v}/{msg}"
        print(f"[selftest] T5 PASS: cardinality_breach -> HARD_FAIL", flush=True)

        # T6: mechanism null
        fake_null = {k: dict(v) for k, v in fake_hp.items()}
        for k in fake_null:
            fake_null[k]["heldout_acc"] = 0.37
        v, msg, det = compute_verdict(fake_null)
        assert v == "HARD_FAIL", f"T6 expected HARD_FAIL, got {v}"
        print(f"[selftest] T6 PASS: mechanism null -> HARD_FAIL", flush=True)

        # T7: cone violation
        fake_cone = {k: dict(v) for k, v in fake_hp.items()}
        for k in fake_cone:
            if "HOPFIELD" in k:
                fake_cone[k]["w_schema_cone_cosine"] = 0.20
        v, msg, det = compute_verdict(fake_cone)
        assert v == "HARD_FAIL" and "off_cone" in msg, f"T7 wrong: {v}/{msg}"
        print(f"[selftest] T7 PASS: cone violation -> HARD_FAIL", flush=True)

        # T8: MIDDLE_BAND partial
        fake_mb = {k: dict(v) for k, v in fake_hp.items()}
        for k in fake_mb:
            if "HOPFIELD" in k:
                fake_mb[k]["heldout_acc"] = 0.58  # below HP floor, above MB floor
        v, msg, det = compute_verdict(fake_mb)
        assert v == "MIDDLE_BAND", f"T8 expected MIDDLE_BAND, got {v}"
        print(f"[selftest] T8 PASS: partial -> MIDDLE_BAND", flush=True)
    finally:
        EXPECTED_N_UNITS = saved

    # T9: cone-preserving sanity
    W_e = torch.eye(5, 8, dtype=torch.float32)
    W_s = W_e.clone()
    cone = _cone_cosine(W_s, W_e)
    assert cone > 0.99, f"T9 cone={cone} should be ~1.0"
    print(f"[selftest] T9 PASS: cone cosine on identity = {cone:.4f}", flush=True)

    # T10: eigenspectrum entropy direction
    W_random = torch.randn(8, 32, dtype=torch.float32)
    ent_rand = _eigenspectrum_entropy(W_random)
    W_low_rank = torch.zeros(8, 32, dtype=torch.float32)
    W_low_rank[0, :] = 1.0
    ent_lr = _eigenspectrum_entropy(W_low_rank)
    assert ent_lr < ent_rand, f"T10 low-rank ent={ent_lr} < random ent={ent_rand}"
    print(f"[selftest] T10 PASS: low-rank entropy {ent_lr:.4f} < random {ent_rand:.4f}", flush=True)

    # T11: pre-reg envelope locks
    assert HP_HELDOUT_ACC_FLOOR == 0.65
    assert HP_LIFT_OVER_HEBBIAN == 0.10
    assert HP_LIFT_OVER_BASELINE == 0.20
    assert HP_COR_SCORE_FLOOR == 0.30
    assert CV_CHAIN_GRADE_MAX == 0.10
    assert ETA_FAST == 1.0 and ETA_REPLAY == 1.0
    assert REPLAY_FRAC == 0.2 and REPLAY_EVERY == 100
    print(f"[selftest] T11 PASS: pre-reg envelope constants LOCKED", flush=True)

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
    if arm == "ARM_BASELINE_HEBBIAN":
        out = eval_arm_baseline_hebbian(seed_offset)
    elif arm == "ARM_HEBBIAN_SLOW":
        out = eval_arm_hebbian_slow(seed_offset)
    elif arm == "ARM_HOPFIELD_REPLAY_SLOW":
        out = _eval_hopfield_consolidation(seed_offset, generative=False)
    elif arm == "ARM_HOPFIELD_GENERATIVE_REPLAY":
        out = _eval_hopfield_consolidation(seed_offset, generative=True)
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
                      f"cor={body['cor_score']:.4f} "
                      f"replay_cycles={body['n_replay_cycles_applied']} "
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
