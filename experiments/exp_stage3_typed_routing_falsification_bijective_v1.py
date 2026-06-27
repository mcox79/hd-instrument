"""stage3_typed_routing_falsification_bijective_v1 -- STUB E falsification probe.

USER 2026-06-27 NO LOCAL: cell-author smoke + dispatch on remote only.

DESIGN PROVENANCE: research drill 2026-06-27
  notes/research_drill_typed_multibank_actively_hurts_3x_2026-06-27.md STUB E
PREREG: preregs/2026-06-27_stage3_typed_routing_falsification_bijective_v1.md

MECHANISM: bijective N_TYPES = N_BANKS = 64 typed routing (drill fix M1).
Falsification probe for typed-routing branch. Should HARD_PASS (P=0.80) if
substrate working correctly; HARD_FAIL definitively kills typed-routing class.

ARMS (3 mandatory; per-arm metrics in metrics.json):
  ARM_BASELINE -- chain-grade content-cosine multibank (no typing); sanity rail.
  ARM_BIJECTIVE_TYPED -- N_TYPES = N_BANKS = 64, each bank unique type;
    routing accuracy = 1.000 by construction.
  ARM_FALLBACK_FIRST_MATCH -- N_TYPES = N_BANKS / 2 = 32, replicates v1
    first-match-deterministic collision regime; expected recall ~ 0.44 per
    drill A1.2 math (validates META_RULE_K discriminator).

PRE-REG BANDS (LOCKED at module init; see prereg .md for full):
  HP_BIJECTIVE_LIFT_MIN = 0.10 (typed >= baseline + 0.10)
  HP_BASELINE_FLOOR = 0.90 (sanity rail)
  HP_COLLISION_BAND_LOW = 0.38 (drill math: E[1/k] * cleanup ~= 0.44)
  HP_COLLISION_BAND_HIGH = 0.50
  HF_BIJECTIVE_HURTS = 0.02 (typed < baseline by 0.02 -> HARD_FAIL)
  HF_BASELINE_BROKEN = 0.85
  CV_CHAIN_GRADE_MAX = 0.05
  EXPECTED_N_UNITS = 3 seeds * 3 arms = 9 (full); 1 * 3 = 3 (smoke)

META_RULE_H cardinality_ok mandatory.
META_RULE_J no-silent-except: failures recorded + halt loop.
META_RULE_K smoke fires discriminator: smoke at N_DIM=2048 K=1024 n_banks=16
  with N_TYPES=8 for collision arm (same 2-banks-per-type as full).
META_RULE_L band-floor strictly-above-floor.
META_RULE_F NA: no per-atom |W| coupling (integer type labels only).

PROT-020 GPU routing: cell uses torch but routes to remote_cpu_queue per
drill spec (multibank at this scale does not need GPU). _STRICT_GPU = False.

ASCII-only. Single-file. Resumable per (seed, arm) checkpoint key.
Author: exp_dev 2026-06-27 (STUB E; under Research lead).
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

ANCHOR_NAME = "stage3_typed_routing_falsification_bijective_v1"
CORPUS_PROVENANCE = (
    "synthetic_substrate_bipolar_codebook_multibank_bijective_typed_routing_falsification_"
    "K4096_OVERLAP0p40_NTYPES_eq_NBANKS_64"
)

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) \
    else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

# ---------------- pre-reg bands (LOCKED at module init) ----------------
HP_BIJECTIVE_LIFT_MIN = 0.10
HP_BASELINE_FLOOR = 0.90
HP_BASELINE_FLOOR_SMOKE = 0.85
HP_COLLISION_BAND_LOW = 0.38
HP_COLLISION_BAND_HIGH = 0.50
HF_BIJECTIVE_HURTS = 0.02
HF_BASELINE_BROKEN = 0.85
HF_BASELINE_BROKEN_SMOKE = 0.75
HF_COLLISION_BAND_LOW = 0.30
HF_COLLISION_BAND_HIGH = 0.60
Q_SUSPECT_SATURATION = 0.98
CV_CHAIN_GRADE_MAX = 0.05
MB_BIJECTIVE_NULL_WINDOW = 0.05

assert 0.0 < HP_BIJECTIVE_LIFT_MIN < 1.0, "band locked"
assert HP_COLLISION_BAND_LOW < HP_COLLISION_BAND_HIGH, "band locked"

# ---------------- regime config ----------------
SIGMA = 1.0
CUE_COS = 0.70
FEATURE_OVERLAP_FRAC = 0.40
N_GROUPS_ADV = 4
CODEBOOK_CHUNK = 4096

if SMOKE:
    N_DIM = 2048
    CODEBOOK_SIZE = 4096
    K_TOTAL = 1024
    N_BANKS = 16
    K_PER_BANK = 64
    N_ITEMS_PER_K = 80
    SEEDS = [11]
    N_TYPES_BIJECTIVE = 16  # equals N_BANKS (bijective)
    N_TYPES_FALLBACK = 8    # N_BANKS / 2 (2 banks per type collision)
else:
    N_DIM = 8192
    CODEBOOK_SIZE = 16384
    K_TOTAL = 4096
    N_BANKS = 64
    K_PER_BANK = 64
    N_ITEMS_PER_K = 100
    SEEDS = [11, 13, 19]
    N_TYPES_BIJECTIVE = 64  # equals N_BANKS (bijective)
    N_TYPES_FALLBACK = 32   # N_BANKS / 2 (2 banks per type collision)

# Sanity assert bijective + collision invariants
assert N_TYPES_BIJECTIVE == N_BANKS, "bijective: N_TYPES must equal N_BANKS"
assert N_TYPES_FALLBACK * 2 == N_BANKS, "collision: N_TYPES must equal N_BANKS / 2"

ARMS = ["ARM_BASELINE", "ARM_BIJECTIVE_TYPED", "ARM_FALLBACK_FIRST_MATCH"]
EXPECTED_N_UNITS = len(SEEDS) * len(ARMS)

CONFIG_VERSION = (
    "stage3_typed_falsif_bijective-v1: N_DIM=%d CODEBOOK=%d sigma=%.1f CUE_COS=%.2f "
    "OVERLAP=%.2f K_TOTAL=%d n_banks=%d k_per_bank=%d N_TYPES_BIJ=%d N_TYPES_FALL=%d "
    "N_ITEMS=%d seeds=%s mode=%s HP_lift>=%.2f HP_baseline>=%.2f "
    "collision_band=[%.2f,%.2f] cv<=%.2f EXPECTED_N=%d"
) % (
    N_DIM, CODEBOOK_SIZE, SIGMA, CUE_COS, FEATURE_OVERLAP_FRAC,
    K_TOTAL, N_BANKS, K_PER_BANK, N_TYPES_BIJECTIVE, N_TYPES_FALLBACK,
    N_ITEMS_PER_K, SEEDS, RUN_MODE,
    HP_BIJECTIVE_LIFT_MIN, HP_BASELINE_FLOOR,
    HP_COLLISION_BAND_LOW, HP_COLLISION_BAND_HIGH,
    CV_CHAIN_GRADE_MAX, EXPECTED_N_UNITS,
)

_DEVICE = torch.device("cpu")
_STORE_DTYPE = torch.float32


def _make_gen(seed_int: int) -> torch.Generator:
    g = torch.Generator(device=_DEVICE)
    g.manual_seed(int(seed_int))
    return g


def random_bipolar_t(shape, gen: torch.Generator) -> torch.Tensor:
    X = torch.empty(*shape, device=_DEVICE, dtype=_STORE_DTYPE)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return X


def bipolar_quantize_t(v: torch.Tensor) -> torch.Tensor:
    return torch.where(v >= 0, torch.ones_like(v), -torch.ones_like(v))


def build_codebook_adversarial(seed_offset: int) -> torch.Tensor:
    g_tpl = _make_gen(seed_offset + 7)
    g_items = _make_gen(seed_offset + 11)
    templates = random_bipolar_t((N_GROUPS_ADV, N_DIM), g_tpl)
    items = random_bipolar_t((CODEBOOK_SIZE, N_DIM), g_items)
    n_shared = int(FEATURE_OVERLAP_FRAC * N_DIM)
    if n_shared > 0:
        group_ids = torch.arange(CODEBOOK_SIZE, device=_DEVICE) % N_GROUPS_ADV
        items[:, :n_shared] = templates[group_ids, :n_shared]
    return items


def build_slot_tags(seed_offset: int, k_per_bank: int) -> torch.Tensor:
    g = _make_gen(seed_offset + 13)
    return random_bipolar_t((k_per_bank, N_DIM), g)


def build_bank_tags(seed_offset: int, n_banks: int) -> torch.Tensor:
    g = _make_gen(seed_offset + 17)
    return random_bipolar_t((n_banks, N_DIM), g)


def _write_bank(items_per_bank: torch.Tensor,
                slot_tags: torch.Tensor,
                seed_offset: int) -> torch.Tensor:
    n_banks = items_per_bank.shape[0]
    D = items_per_bank.shape[2]
    ws_acc = torch.zeros((n_banks, D), device=_DEVICE, dtype=torch.float32)
    slot_tags_f = slot_tags.float()
    for b in range(n_banks):
        chunk_bound = items_per_bank[b].float() * slot_tags_f
        ws_acc[b] = chunk_bound.sum(dim=0)
    if SIGMA > 0.0:
        g_noise = _make_gen(seed_offset + 23)
        noise = torch.empty(ws_acc.shape, device=_DEVICE, dtype=torch.float32)
        noise.normal_(0.0, SIGMA, generator=g_noise)
        ws_acc = ws_acc + noise
    return bipolar_quantize_t(ws_acc).to(_STORE_DTYPE)


def _chunked_argmax_cb(codebook: torch.Tensor, queries: torch.Tensor) -> torch.Tensor:
    C = codebook.shape[0]
    Q = queries.shape[0]
    best_scores = torch.full((Q,), float("-inf"), device=queries.device, dtype=torch.float32)
    best_idx = torch.zeros((Q,), device=queries.device, dtype=torch.long)
    q_T = queries.T
    for c0 in range(0, C, CODEBOOK_CHUNK):
        c1 = min(c0 + CODEBOOK_CHUNK, C)
        sims_chunk = (codebook[c0:c1] @ q_T).float()
        chunk_max, chunk_idx = sims_chunk.max(dim=0)
        better = chunk_max > best_scores
        best_scores = torch.where(better, chunk_max, best_scores)
        best_idx = torch.where(better, chunk_idx + c0, best_idx)
    return best_idx


def _read_with_cleanup(workspaces: torch.Tensor,
                       slot_tag: torch.Tensor,
                       codebook: torch.Tensor) -> torch.Tensor:
    r1 = (workspaces * slot_tag)
    cand_idx = _chunked_argmax_cb(codebook, r1)
    cand_vecs = codebook[cand_idx]
    r2 = bipolar_quantize_t(r1.float() + cand_vecs.float()).to(_STORE_DTYPE)
    pred_idx = _chunked_argmax_cb(codebook, r2)
    return pred_idx


def _route_by_type_label_first_match(query_type_idx: torch.Tensor,
                                     bank_type_assignment: torch.Tensor) -> torch.Tensor:
    """First-match deterministic type-to-bank routing (drill v1 regime)."""
    n_q = query_type_idx.shape[0]
    routed = torch.zeros((n_q,), dtype=torch.long, device=_DEVICE)
    for q in range(n_q):
        qt = int(query_type_idx[q].item())
        matches = (bank_type_assignment == qt).nonzero(as_tuple=True)[0]
        if matches.numel() > 0:
            routed[q] = matches[0]
        else:
            routed[q] = 0
    return routed


def eval_baseline(seed_offset: int) -> Tuple[float, float]:
    """ARM_BASELINE: chain-grade content-cosine multibank routing (no typing)."""
    codebook = build_codebook_adversarial(seed_offset)
    slot_tags = build_slot_tags(seed_offset, K_PER_BANK)
    bank_tags = build_bank_tags(seed_offset, N_BANKS)
    cue_noise_scale = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))

    n_trials = max(1, math.ceil(N_ITEMS_PER_K / K_TOTAL))
    correct = 0
    total = 0
    route_correct = 0
    route_total = 0

    g_trial = _make_gen(seed_offset + 29)
    for trial in range(n_trials):
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial,
                                     device=_DEVICE)[:K_TOTAL]
        items = codebook[idx_global]
        items_per_bank = items.view(N_BANKS, K_PER_BANK, N_DIM)
        workspaces = _write_bank(items_per_bank, slot_tags,
                                 seed_offset + 1000 + trial)

        slot_indices = torch.arange(K_TOTAL, device=_DEVICE)
        bank_true = slot_indices // K_PER_BANK
        local_slot = slot_indices % K_PER_BANK

        g_cue = _make_gen(seed_offset + 5000 + trial)
        bank_cue_base = bank_tags[bank_true].float()
        noise = torch.empty((K_TOTAL, N_DIM), device=_DEVICE, dtype=torch.float32)
        noise.normal_(0.0, 1.0, generator=g_cue)
        noise_bp = bipolar_quantize_t(noise)
        cues = (CUE_COS * bank_cue_base + cue_noise_scale * noise_bp).to(_STORE_DTYPE)

        # Content-cosine routing
        sims_bank = cues @ bank_tags.T
        bank_routed = sims_bank.argmax(dim=1)
        route_correct += int((bank_routed == bank_true).sum().item())
        route_total += K_TOTAL

        ws_selected = workspaces[bank_routed]
        slot_tag_sel = slot_tags[local_slot]
        pred_idx = _read_with_cleanup(ws_selected, slot_tag_sel, codebook)
        true_item_idx = idx_global[slot_indices]
        match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
        correct += int(match.sum().item())
        total += K_TOTAL

    recall = correct / max(total, 1)
    route_acc = route_correct / max(route_total, 1)
    return recall, route_acc


def eval_bijective_typed(seed_offset: int) -> Tuple[float, float]:
    """ARM_BIJECTIVE_TYPED: N_TYPES = N_BANKS; each bank unique type.

    Routing accuracy = 1.000 by construction (every query's type-label maps
    to exactly one bank). Tests whether typed adds value vs chain-grade
    content-cosine when collisions are eliminated.
    """
    codebook = build_codebook_adversarial(seed_offset)
    slot_tags = build_slot_tags(seed_offset, K_PER_BANK)
    bank_tags = build_bank_tags(seed_offset, N_BANKS)
    cue_noise_scale = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))

    # BIJECTIVE assignment: bank i has type i
    bank_type_assignment = torch.arange(N_BANKS, device=_DEVICE, dtype=torch.long)
    # Verify bijective (each type appears exactly once)
    unique_types = torch.unique(bank_type_assignment)
    assert unique_types.numel() == N_BANKS, "bijective assignment broken"

    n_trials = max(1, math.ceil(N_ITEMS_PER_K / K_TOTAL))
    correct = 0
    total = 0
    typed_route_correct = 0
    typed_route_total = 0

    g_trial = _make_gen(seed_offset + 29)
    for trial in range(n_trials):
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial,
                                     device=_DEVICE)[:K_TOTAL]
        items = codebook[idx_global]
        items_per_bank = items.view(N_BANKS, K_PER_BANK, N_DIM)
        workspaces = _write_bank(items_per_bank, slot_tags,
                                 seed_offset + 1000 + trial)

        slot_indices = torch.arange(K_TOTAL, device=_DEVICE)
        bank_true = slot_indices // K_PER_BANK
        local_slot = slot_indices % K_PER_BANK

        # Query type label is the true bank's type assignment (bijective)
        query_type_idx = bank_type_assignment[bank_true]

        # Bijective routing: direct index by type (no collisions possible)
        bank_routed = _route_by_type_label_first_match(query_type_idx,
                                                      bank_type_assignment)
        typed_route_correct += int((bank_routed == bank_true).sum().item())
        typed_route_total += K_TOTAL

        # Cleanup within routed bank (cue uses TRUE bank tag; routing is via type)
        g_cue = _make_gen(seed_offset + 5000 + trial)
        bank_cue_base = bank_tags[bank_routed].float()
        noise = torch.empty((K_TOTAL, N_DIM), device=_DEVICE, dtype=torch.float32)
        noise.normal_(0.0, 1.0, generator=g_cue)
        noise_bp = bipolar_quantize_t(noise)
        cues = (CUE_COS * bank_cue_base + cue_noise_scale * noise_bp).to(_STORE_DTYPE)

        ws_selected = workspaces[bank_routed]
        slot_tag_sel = slot_tags[local_slot]
        pred_idx = _read_with_cleanup(ws_selected, slot_tag_sel, codebook)
        true_item_idx = idx_global[slot_indices]
        match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
        correct += int(match.sum().item())
        total += K_TOTAL

    recall = correct / max(total, 1)
    typed_route_acc = typed_route_correct / max(typed_route_total, 1)
    return recall, typed_route_acc


def eval_fallback_first_match(seed_offset: int) -> Tuple[float, float]:
    """ARM_FALLBACK_FIRST_MATCH: N_TYPES = N_BANKS / 2; collision regime.

    Replicates v1 first-match-deterministic routing under 2-banks-per-type
    expectation. Drill A1.2 math predicts recall ~ 0.44 (E[1/k] * cleanup).
    Validates META_RULE_K discriminator: if collision arm doesn't land near
    0.44, drill math is wrong and we abort dispatch interpretation.
    """
    codebook = build_codebook_adversarial(seed_offset)
    slot_tags = build_slot_tags(seed_offset, K_PER_BANK)
    bank_tags = build_bank_tags(seed_offset, N_BANKS)
    cue_noise_scale = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))

    # Random assignment with N_TYPES = N_BANKS / 2 (2 banks per type avg)
    g_assign = _make_gen(seed_offset + 31)
    bank_type_assignment = torch.randint(
        0, N_TYPES_FALLBACK, (N_BANKS,), generator=g_assign, device=_DEVICE,
    )

    n_trials = max(1, math.ceil(N_ITEMS_PER_K / K_TOTAL))
    correct = 0
    total = 0
    typed_route_correct = 0
    typed_route_total = 0

    g_trial = _make_gen(seed_offset + 29)
    for trial in range(n_trials):
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial,
                                     device=_DEVICE)[:K_TOTAL]
        items = codebook[idx_global]
        items_per_bank = items.view(N_BANKS, K_PER_BANK, N_DIM)
        workspaces = _write_bank(items_per_bank, slot_tags,
                                 seed_offset + 1000 + trial)

        slot_indices = torch.arange(K_TOTAL, device=_DEVICE)
        bank_true = slot_indices // K_PER_BANK
        local_slot = slot_indices % K_PER_BANK

        # Query type label is true bank's assignment (some banks share types)
        query_type_idx = bank_type_assignment[bank_true]

        # First-match routing -> collision-bound at E[1/k] ~= 0.44
        bank_routed = _route_by_type_label_first_match(query_type_idx,
                                                      bank_type_assignment)
        typed_route_correct += int((bank_routed == bank_true).sum().item())
        typed_route_total += K_TOTAL

        g_cue = _make_gen(seed_offset + 5000 + trial)
        bank_cue_base = bank_tags[bank_routed].float()
        noise = torch.empty((K_TOTAL, N_DIM), device=_DEVICE, dtype=torch.float32)
        noise.normal_(0.0, 1.0, generator=g_cue)
        noise_bp = bipolar_quantize_t(noise)
        cues = (CUE_COS * bank_cue_base + cue_noise_scale * noise_bp).to(_STORE_DTYPE)

        ws_selected = workspaces[bank_routed]
        slot_tag_sel = slot_tags[local_slot]
        pred_idx = _read_with_cleanup(ws_selected, slot_tag_sel, codebook)
        true_item_idx = idx_global[slot_indices]
        match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
        correct += int(match.sum().item())
        total += K_TOTAL

    recall = correct / max(total, 1)
    typed_route_acc = typed_route_correct / max(typed_route_total, 1)
    return recall, typed_route_acc


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
    for key, body in per_unit.items():
        arm = body["arm"]
        if arm in by_arm:
            by_arm[arm].append(float(body["recall"]))

    def stats(vals):
        if not vals:
            return float("nan"), float("nan"), 0
        m = float(np.mean(vals))
        s = float(np.std(vals)) if len(vals) > 1 else 0.0
        cv = float(s / max(m, 1e-9)) if m > 1e-9 else 0.0
        return round(m, 4), round(cv, 4), len(vals)

    baseline_m, baseline_cv, baseline_n = stats(by_arm["ARM_BASELINE"])
    bijective_m, bijective_cv, bijective_n = stats(by_arm["ARM_BIJECTIVE_TYPED"])
    collision_m, collision_cv, collision_n = stats(by_arm["ARM_FALLBACK_FIRST_MATCH"])

    bij_lift = bijective_m - baseline_m if not (math.isnan(bijective_m) or math.isnan(baseline_m)) else float("nan")

    # Band selection by mode
    baseline_floor = HP_BASELINE_FLOOR_SMOKE if SMOKE else HP_BASELINE_FLOOR
    baseline_broken_floor = HF_BASELINE_BROKEN_SMOKE if SMOKE else HF_BASELINE_BROKEN

    # Discipline checks
    baseline_ok = baseline_m >= baseline_floor
    saturated = baseline_m >= Q_SUSPECT_SATURATION
    collision_in_hp_band = (HP_COLLISION_BAND_LOW <= collision_m <= HP_COLLISION_BAND_HIGH)
    collision_in_hf_band = (HF_COLLISION_BAND_LOW <= collision_m <= HF_COLLISION_BAND_HIGH)
    cv_ok = max(baseline_cv, bijective_cv, collision_cv) <= CV_CHAIN_GRADE_MAX

    detail = {
        "cardinality_ok": cardinality_ok,
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "baseline_recall_mean": baseline_m,
        "baseline_recall_cv": baseline_cv,
        "bijective_recall_mean": bijective_m,
        "bijective_recall_cv": bijective_cv,
        "collision_recall_mean": collision_m,
        "collision_recall_cv": collision_cv,
        "bijective_lift_vs_baseline": round(bij_lift, 4) if not math.isnan(bij_lift) else None,
        "collision_in_drill_math_band": collision_in_hp_band,
        "baseline_saturated_above_Q": saturated,
        "n_failures": len(failures),
        "failures_brief": [{"key": f.get("key", "?"), "exc_type": f.get("exc_type", "?")}
                           for f in failures[:5]],
        "config_version": CONFIG_VERSION,
        "HP_bijective_lift_min": HP_BIJECTIVE_LIFT_MIN,
        "HP_baseline_floor": baseline_floor,
        "HP_collision_band": [HP_COLLISION_BAND_LOW, HP_COLLISION_BAND_HIGH],
        "Q_suspect_saturation": Q_SUSPECT_SATURATION,
        "cv_chain_grade_max": CV_CHAIN_GRADE_MAX,
        "n_types_bijective": N_TYPES_BIJECTIVE,
        "n_types_fallback": N_TYPES_FALLBACK,
    }

    # HARD_FAIL conditions (load-bearing first)
    if not cardinality_ok:
        return ("HARD_FAIL",
                f"cardinality_breach: observed={n_units_observed} expected={EXPECTED_N_UNITS} "
                f"failures={len(failures)}", detail)
    if baseline_m < baseline_broken_floor:
        return ("HARD_FAIL",
                f"baseline_broken: ARM_BASELINE={baseline_m:.4f} < {baseline_broken_floor} "
                f"(methodology drift; chain-grade content-cosine should be >={baseline_floor})",
                detail)
    if not math.isnan(bij_lift) and bij_lift < -HF_BIJECTIVE_HURTS:
        return ("HARD_FAIL",
                f"bijective_hurts_baseline: lift={bij_lift:.4f} < -{HF_BIJECTIVE_HURTS} "
                f"(typed actively HURTS even with zero collisions; KILL typed-routing class)",
                detail)
    if not collision_in_hf_band:
        return ("HARD_FAIL",
                f"collision_arm_off_drill_math: collision={collision_m:.4f} outside "
                f"[{HF_COLLISION_BAND_LOW}, {HF_COLLISION_BAND_HIGH}] (drill A1.2 math wrong; "
                f"substrate behaves differently than predicted)",
                detail)
    if saturated:
        return ("HARD_FAIL",
                f"by_construction_saturation_META_RULE_K: baseline={baseline_m:.4f} >= "
                f"{Q_SUSPECT_SATURATION}; lift requirement structurally unachievable",
                detail)

    # HARD_PASS conditions (drill: KEEP typed-routing as concept)
    bij_lift_meets = (not math.isnan(bij_lift)) and (bij_lift >= HP_BIJECTIVE_LIFT_MIN)
    if bij_lift_meets and baseline_ok and collision_in_hp_band and cv_ok:
        return ("HARD_PASS",
                f"bijective_typed_adds_value: lift={bij_lift:.4f} >= {HP_BIJECTIVE_LIFT_MIN}; "
                f"baseline={baseline_m:.4f} >= {baseline_floor}; collision={collision_m:.4f} "
                f"in drill-math band [{HP_COLLISION_BAND_LOW}, {HP_COLLISION_BAND_HIGH}]; "
                f"cv max={max(baseline_cv, bijective_cv, collision_cv):.4f} <= {CV_CHAIN_GRADE_MAX} "
                f"(drill: KEEP typed-routing concept)",
                detail)

    # MIDDLE_BAND: typed adds no value (within window) but math validated
    bij_null_window = (not math.isnan(bij_lift)) and (abs(bij_lift) < MB_BIJECTIVE_NULL_WINDOW)
    if bij_null_window and baseline_ok and collision_in_hp_band:
        return ("MIDDLE_BAND",
                f"bijective_redundant_with_content_cosine: lift={bij_lift:.4f} within "
                f"+/-{MB_BIJECTIVE_NULL_WINDOW}; drill math validated; "
                f"drill recommendation: KILL typed-routing branch (redundant)",
                detail)

    return ("MIDDLE_BAND",
            f"partial: bij_lift={bij_lift if bij_lift is not None else 'nan'} "
            f"(HP>={HP_BIJECTIVE_LIFT_MIN}); baseline={baseline_m:.4f} ok={baseline_ok}; "
            f"collision={collision_m:.4f} in_drill_band={collision_in_hp_band}; "
            f"cv_ok={cv_ok}",
            detail)


# ---------------- self-test ----------------

def _selftest():
    print("[selftest] stage3_typed_routing_falsification_bijective_v1 starting", flush=True)

    # T1: bijective + collision invariants
    assert N_TYPES_BIJECTIVE == N_BANKS, "T1 bijective"
    assert N_TYPES_FALLBACK * 2 == N_BANKS, "T1 collision"
    print(f"[selftest] T1 PASS: N_TYPES_BIJECTIVE={N_TYPES_BIJECTIVE} == N_BANKS={N_BANKS}; "
          f"N_TYPES_FALLBACK={N_TYPES_FALLBACK} * 2 == N_BANKS", flush=True)

    # T2: bipolar codebook in {-1, +1}
    g = _make_gen(7)
    cb = random_bipolar_t((128, 256), g)
    u = torch.unique(cb)
    assert set(u.tolist()) <= {-1.0, 1.0}, "T2 bipolar"
    print(f"[selftest] T2 PASS: bipolar codebook in {{-1,+1}}", flush=True)

    # T3: type-tag distinct labels
    bank_assn_bij = torch.arange(16, dtype=torch.long)
    unique_bij = torch.unique(bank_assn_bij)
    assert unique_bij.numel() == 16, "T3 bijective unique"
    print(f"[selftest] T3 PASS: bijective assignment has N_BANKS unique labels", flush=True)

    # T4: routing-by-type-lookup correctness (bijective)
    g_assn = _make_gen(42)
    test_bank_assn = torch.arange(8, dtype=torch.long)  # bijective 8-way
    queries = torch.arange(8, dtype=torch.long)  # one query per type
    routed = _route_by_type_label_first_match(queries, test_bank_assn)
    expected = torch.arange(8, dtype=torch.long)
    assert torch.equal(routed, expected), f"T4 bijective routing wrong: {routed} vs {expected}"
    print(f"[selftest] T4 PASS: bijective first-match routing is identity", flush=True)

    # T5: drill-math Monte Carlo validation
    # E[1/k] for k = 1 + Binomial(N_BANKS-1, 1/N_TYPES) when N_TYPES = N_BANKS/2
    # For N_BANKS=64, N_TYPES=32, this should be ~0.42-0.46 per drill
    g_mc = _make_gen(999)
    n_mc_trials = 1000
    test_nbanks = 64
    test_ntypes = 32
    p_first_match = 0.0
    for trial in range(n_mc_trials):
        g_t = _make_gen(999 + trial)
        assn = torch.randint(0, test_ntypes, (test_nbanks,), generator=g_t, dtype=torch.long)
        # Pick a random true bank, see if first-match returns it
        true_bank = int(torch.randint(0, test_nbanks, (1,), generator=g_t).item())
        true_type = int(assn[true_bank].item())
        matches = (assn == true_type).nonzero(as_tuple=True)[0]
        if matches.numel() > 0 and int(matches[0].item()) == true_bank:
            p_first_match += 1.0
    p_first_match /= n_mc_trials
    # Drill A1.2 predicts E[1/k] ~ 0.42-0.46
    assert 0.35 <= p_first_match <= 0.55, (
        f"T5 drill-math: P(first-match)={p_first_match:.4f} outside [0.35, 0.55]; "
        f"drill A1.2 math may be wrong"
    )
    print(f"[selftest] T5 PASS: drill-math P(first-match)={p_first_match:.4f} "
          f"in [0.35, 0.55] (drill predicts ~0.44)", flush=True)

    # T6: verdict-machinery synthetic cases
    # T6 HP synthetic: baseline ~0.88 + bijective 1.0 -> lift 0.12 >= 0.10 HP_min.
    # MIDDLE_BAND test (T6b) flips bij to 0.89 -> lift 0.01 within +/-0.05 null window.
    fake_hp = {
        "11_ARM_BASELINE": {"arm": "ARM_BASELINE", "recall": 0.88},
        "13_ARM_BASELINE": {"arm": "ARM_BASELINE", "recall": 0.88},
        "19_ARM_BASELINE": {"arm": "ARM_BASELINE", "recall": 0.88},
        "11_ARM_BIJECTIVE_TYPED": {"arm": "ARM_BIJECTIVE_TYPED", "recall": 1.0},
        "13_ARM_BIJECTIVE_TYPED": {"arm": "ARM_BIJECTIVE_TYPED", "recall": 1.0},
        "19_ARM_BIJECTIVE_TYPED": {"arm": "ARM_BIJECTIVE_TYPED", "recall": 1.0},
        "11_ARM_FALLBACK_FIRST_MATCH": {"arm": "ARM_FALLBACK_FIRST_MATCH", "recall": 0.44},
        "13_ARM_FALLBACK_FIRST_MATCH": {"arm": "ARM_FALLBACK_FIRST_MATCH", "recall": 0.43},
        "19_ARM_FALLBACK_FIRST_MATCH": {"arm": "ARM_FALLBACK_FIRST_MATCH", "recall": 0.45},
    }
    global EXPECTED_N_UNITS
    saved_expected = EXPECTED_N_UNITS
    EXPECTED_N_UNITS = 9
    try:
        v, msg, det = compute_verdict(fake_hp)
        assert v == "HARD_PASS", f"T6a HP expected, got {v}: {msg}"
        print(f"[selftest] T6a PASS: synthetic HARD_PASS path -> {v}", flush=True)

        # T6b: MIDDLE_BAND (typed adds no value within null window)
        fake_mb = dict(fake_hp)
        for k in list(fake_mb.keys()):
            if "BIJECTIVE_TYPED" in k:
                fake_mb[k] = dict(fake_mb[k])
                fake_mb[k]["recall"] = 0.89  # ~baseline (lift 0.01, within null window)
        v, msg, det = compute_verdict(fake_mb)
        assert v == "MIDDLE_BAND", f"T6b MB expected, got {v}: {msg}"
        print(f"[selftest] T6b PASS: bijective_redundant -> MIDDLE_BAND", flush=True)

        # T6c: HARD_FAIL bijective hurts
        fake_hurt = dict(fake_hp)
        for k in list(fake_hurt.keys()):
            if "BIJECTIVE_TYPED" in k:
                fake_hurt[k] = dict(fake_hurt[k])
                fake_hurt[k]["recall"] = 0.85  # below baseline by 0.07
        v, msg, det = compute_verdict(fake_hurt)
        assert v == "HARD_FAIL", f"T6c HF expected, got {v}: {msg}"
        assert "bijective_hurts" in msg, f"T6c expected hurts msg, got {msg}"
        print(f"[selftest] T6c PASS: bijective_hurts -> HARD_FAIL", flush=True)

        # T6d: HARD_FAIL collision off math
        fake_offmath = dict(fake_hp)
        for k in list(fake_offmath.keys()):
            if "FALLBACK_FIRST_MATCH" in k:
                fake_offmath[k] = dict(fake_offmath[k])
                fake_offmath[k]["recall"] = 0.85  # way off drill math 0.44
        v, msg, det = compute_verdict(fake_offmath)
        assert v == "HARD_FAIL", f"T6d HF expected, got {v}: {msg}"
        assert "collision_arm_off_drill_math" in msg, f"T6d expected math msg, got {msg}"
        print(f"[selftest] T6d PASS: collision_off_math -> HARD_FAIL", flush=True)

        # T6e: HARD_FAIL cardinality
        fake_card = dict(list(fake_hp.items())[:6])
        v, msg, det = compute_verdict(fake_card)
        assert v == "HARD_FAIL", f"T6e HF expected, got {v}"
        assert "cardinality_breach" in msg, f"T6e expected card msg, got {msg}"
        print(f"[selftest] T6e PASS: cardinality_breach -> HARD_FAIL", flush=True)

        # T6f: HARD_FAIL baseline broken
        fake_baseline_broken = dict(fake_hp)
        for k in list(fake_baseline_broken.keys()):
            if k.endswith("ARM_BASELINE"):
                fake_baseline_broken[k] = dict(fake_baseline_broken[k])
                fake_baseline_broken[k]["recall"] = 0.50  # way below 0.85 floor
        v, msg, det = compute_verdict(fake_baseline_broken)
        assert v == "HARD_FAIL", f"T6f HF expected, got {v}"
        assert "baseline_broken" in msg, f"T6f expected baseline msg, got {msg}"
        print(f"[selftest] T6f PASS: baseline_broken -> HARD_FAIL", flush=True)
    finally:
        EXPECTED_N_UNITS = saved_expected

    # T7: pre-reg envelope locks
    assert HP_BIJECTIVE_LIFT_MIN == 0.10
    assert HP_BASELINE_FLOOR == 0.90
    assert HP_COLLISION_BAND_LOW == 0.38
    assert HP_COLLISION_BAND_HIGH == 0.50
    assert CV_CHAIN_GRADE_MAX == 0.05
    print(f"[selftest] T7 PASS: pre-reg envelope constants LOCKED", flush=True)

    # T8: chunked argmax matches unchunked
    cb_q = random_bipolar_t((256, 128), _make_gen(13))
    q = random_bipolar_t((16, 128), _make_gen(17))
    sims_full = (cb_q.float() @ q.float().T)
    idx_un = sims_full.argmax(dim=0)
    saved_chunk = CODEBOOK_CHUNK
    globals()["CODEBOOK_CHUNK"] = 64
    try:
        idx_ch = _chunked_argmax_cb(cb_q, q)
        assert torch.equal(idx_ch, idx_un), "T8 chunked argmax disagrees"
    finally:
        globals()["CODEBOOK_CHUNK"] = saved_chunk
    print(f"[selftest] T8 PASS: chunked argmax matches unchunked", flush=True)

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
        "K_TOTAL": int(K_TOTAL),
        "N_BANKS": int(N_BANKS),
        "K_PER_BANK": int(K_PER_BANK),
        "FEATURE_OVERLAP_FRAC": float(FEATURE_OVERLAP_FRAC),
    }
    if arm == "ARM_BASELINE":
        recall, route_acc = eval_baseline(seed_offset)
        body["recall"] = float(round(recall, 4))
        body["route_acc"] = float(round(route_acc, 4))
        body["N_TYPES"] = 0
    elif arm == "ARM_BIJECTIVE_TYPED":
        recall, route_acc = eval_bijective_typed(seed_offset)
        body["recall"] = float(round(recall, 4))
        body["route_acc"] = float(round(route_acc, 4))
        body["N_TYPES"] = int(N_TYPES_BIJECTIVE)
    elif arm == "ARM_FALLBACK_FIRST_MATCH":
        recall, route_acc = eval_fallback_first_match(seed_offset)
        body["recall"] = float(round(recall, 4))
        body["route_acc"] = float(round(route_acc, 4))
        body["N_TYPES"] = int(N_TYPES_FALLBACK)
    else:
        raise ValueError(f"unknown arm: {arm}")
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
                print(f"  [{key}] {body}", flush=True)
            except Exception as e:
                fail = {
                    "key": key,
                    "exc_type": type(e).__name__,
                    "exc_msg": str(e),
                }
                failures.append(fail)
                print(f"  [{key}] FAILED: {e}", flush=True)
                # META_RULE_J: halt loop on first failure (no silent except)
                raise

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
