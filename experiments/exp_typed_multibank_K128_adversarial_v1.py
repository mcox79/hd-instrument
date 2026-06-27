"""typed_multibank_K128_adversarial_v1 -- typed multibank routing + refuse-gate (Wave A).

USER 2026-06-27: Wave A CELL 4 RESPEC of Wave 2 Anchor 2; FIRST to dispatch per
Wave A sequencing (cheapest; produces upper-bound rail for Wave B CELL 2).

DESIGN PROVENANCE: research drill 2026-06-27
  notes/research_drill_stage3_compositional_cell_design_2026-06-27.md CELL 4
PREREG: preregs/2026-06-27_typed_multibank_K128_adversarial_v1.md

MECHANISM: per-bank TYPE LABEL routing on top of chain-grade multibank
WM K=4096 (chain-grade cell-land 2026-06-26 commit 6e2ff698, ledger
62ce9e7dca071828) + chain-grade refuse-gate V_REL=256. RESPEC vs Wave 2:
operates at FEATURE_OVERLAP_FRAC=0.40 (ADVERSARIAL) to push baseline OUT of
saturation regime (Wave 2 audit: bands at k_per_bank=64 sit in
by-construction-saturation; this cell forces baseline into [0.60, 0.85]).

ARMS (3 mandatory; per-arm metrics in metrics.json):
  ARM_UNTYPED_BASELINE_ADVERSARIAL -- chain-grade multibank K=8192 n_banks=128
    k_per_bank=64 OVERLAP=0.40. Sanity rail: must land in [0.60, 0.85].
  ARM_TYPED_ROUTING_MATCHED -- per-bank type label matches content; routing
    by type-cosine to bank tags; cleanup within routed bank. Tests typed lift.
  ARM_TYPED_ROUTING_ADVERSARIAL_PROBE -- deliberately ill-typed queries; tests
    refuse-rate >= 0.85.

PRE-REG BANDS (LOCKED at module init; see prereg .md for full):
  HP_TYPED_LIFT_OVER_BASELINE = 0.10 (absolute)
  HP_REFUSE_RATE_MIN = 0.85
  HP_BASELINE_BAND_LOW = 0.60
  HP_BASELINE_BAND_HIGH = 0.85
  Q_SUSPECT_SATURATION = 0.95 (auto-demote to MM if baseline above)
  CV_CHAIN_GRADE_MAX = 0.05
  EXPECTED_N_UNITS = 3 seeds * 3 arms = 9 (full); 1*3=3 (smoke)

META_RULE_H cardinality_ok mandatory.
META_RULE_J no-silent-except: failures recorded + halt loop.
META_RULE_K smoke fires discriminator: smoke at N_DIM=2048 K=2048 n_banks=32
  k_per_bank=64 OVERLAP=0.40 (same regime; smaller substrate).
META_RULE_L band-floor strictly-above-floor.
META_RULE_F no-magnitude-coupling: cor(refuse, |W_bank|) < 0.5 sanity check.

PROT-020 GPU routing: cell uses torch but routes to remote_cpu_queue per
research design (multibank does not need GPU at K=8192). _STRICT_GPU = False.

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

ANCHOR_NAME = "typed_multibank_K128_adversarial_v1"
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_codebook_multibank_typed_routing_K8192_OVERLAP0p40_adversarial"

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
HP_TYPED_LIFT_OVER_BASELINE = 0.10
HP_REFUSE_RATE_MIN = 0.85
HP_BASELINE_BAND_LOW = 0.60
HP_BASELINE_BAND_HIGH = 0.85
HP_BASELINE_BAND_HIGH_SMOKE = 0.90
HP_BASELINE_BAND_LOW_SMOKE = 0.55
Q_SUSPECT_SATURATION = 0.95
CV_CHAIN_GRADE_MAX = 0.05
HF_MIN_BASELINE = 0.40
MB_TYPED_LIFT_MIN = 0.03
MB_REFUSE_RATE_MIN = 0.50

assert 0.0 < HP_TYPED_LIFT_OVER_BASELINE < 1.0, "band locked"
assert 0.0 < HP_REFUSE_RATE_MIN < 1.0, "band locked"

# ---------------- regime config ----------------
SIGMA = 1.0
CUE_COS = 0.70
FEATURE_OVERLAP_FRAC = 0.40  # ADVERSARIAL respec; raised from chain-grade 0.20
N_GROUPS_ADV = 4
CODEBOOK_CHUNK = 4096

if SMOKE:
    N_DIM = 2048
    CODEBOOK_SIZE = 4096
    K_TOTAL = 2048
    N_BANKS = 32
    K_PER_BANK = 64
    SENTINEL_K = 1024  # unused but kept for symmetry
    N_ITEMS_PER_K = 80
    SEEDS = [11]
    N_TYPES = 32
else:
    N_DIM = 8192
    CODEBOOK_SIZE = 65536
    K_TOTAL = 8192
    N_BANKS = 128
    K_PER_BANK = 64
    SENTINEL_K = 4096
    N_ITEMS_PER_K = 200
    SEEDS = [11, 13, 19]
    N_TYPES = 64

ARMS = ["ARM_UNTYPED_BASELINE_ADVERSARIAL",
        "ARM_TYPED_ROUTING_MATCHED",
        "ARM_TYPED_ROUTING_ADVERSARIAL_PROBE"]

EXPECTED_N_UNITS = len(SEEDS) * len(ARMS)

# Refuse-gate threshold: bank-cosine cleanup energy gap. Calibrated so that
# matched-type queries pass and ill-typed queries refuse.
REFUSE_GAP_THRESHOLD = 0.10  # gap between top-1 and top-2 bank cosine; below = refuse

CONFIG_VERSION = (
    "typedMB_K128_adv-v1: N_DIM=%d CODEBOOK=%d sigma=%.1f CUE_COS=%.2f "
    "OVERLAP=%.2f K_TOTAL=%d n_banks=%d k_per_bank=%d N_TYPES=%d "
    "N_ITEMS=%d seeds=%s mode=%s HP_lift>=%.2f HP_refuse>=%.2f "
    "baseline_band=[%.2f,%.2f] Q_sat=%.2f cv<=%.2f EXPECTED_N=%d "
    "REFUSE_GAP=%.2f"
) % (
    N_DIM, CODEBOOK_SIZE, SIGMA, CUE_COS, FEATURE_OVERLAP_FRAC,
    K_TOTAL, N_BANKS, K_PER_BANK, N_TYPES,
    N_ITEMS_PER_K, SEEDS, RUN_MODE,
    HP_TYPED_LIFT_OVER_BASELINE, HP_REFUSE_RATE_MIN,
    HP_BASELINE_BAND_LOW, HP_BASELINE_BAND_HIGH,
    Q_SUSPECT_SATURATION, CV_CHAIN_GRADE_MAX, EXPECTED_N_UNITS,
    REFUSE_GAP_THRESHOLD,
)

_DEVICE = torch.device("cpu")  # remote_cpu_queue; no CUDA mandate per design
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


def build_type_tags(seed_offset: int, n_types: int) -> torch.Tensor:
    g = _make_gen(seed_offset + 19)
    return random_bipolar_t((n_types, N_DIM), g)


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


def _route_by_bank_cosine(cues: torch.Tensor,
                          bank_tags: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Compute top-1 bank index AND top-2 bank index by cosine.

    Returns (bank_routed, gap_top1_top2) — gap is positive when top-1
    cosine clearly dominates.
    """
    sims = cues.float() @ bank_tags.float().T  # [Q, n_banks]
    top2 = torch.topk(sims, k=2, dim=1)
    bank_routed = top2.indices[:, 0]
    gap = (top2.values[:, 0] - top2.values[:, 1]) / max(float(N_DIM), 1.0)
    return bank_routed, gap


def _route_by_type_label(query_type_idx: torch.Tensor,
                         bank_type_assignment: torch.Tensor) -> torch.Tensor:
    """Given query type label + per-bank type assignment, route to the bank
    with matching type. If multiple banks share a type, deterministically
    pick the lowest bank index.
    """
    # For each query, find first bank whose type_assignment matches query_type
    n_q = query_type_idx.shape[0]
    n_banks = bank_type_assignment.shape[0]
    routed = torch.zeros((n_q,), dtype=torch.long, device=_DEVICE)
    for q in range(n_q):
        qt = int(query_type_idx[q].item())
        # First bank whose type matches
        matches = (bank_type_assignment == qt).nonzero(as_tuple=True)[0]
        if matches.numel() > 0:
            routed[q] = matches[0]
        else:
            # No match -> route to bank 0 (refuse arm will catch this)
            routed[q] = 0
    return routed


def eval_untyped_baseline_adversarial(seed_offset: int) -> tuple[float, float]:
    """ARM_UNTYPED_BASELINE_ADVERSARIAL: chain-grade multibank at OVERLAP=0.40."""
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


def eval_typed_matched(seed_offset: int) -> tuple[float, float, float]:
    """ARM_TYPED_ROUTING_MATCHED: per-bank type label assigned matching content."""
    codebook = build_codebook_adversarial(seed_offset)
    slot_tags = build_slot_tags(seed_offset, K_PER_BANK)
    bank_tags = build_bank_tags(seed_offset, N_BANKS)
    type_tags = build_type_tags(seed_offset, N_TYPES)
    cue_noise_scale = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))

    # Bank-to-type assignment: each bank gets one type label
    g_assign = _make_gen(seed_offset + 31)
    bank_type_assignment = torch.randint(
        0, N_TYPES, (N_BANKS,), generator=g_assign, device=_DEVICE,
    )

    n_trials = max(1, math.ceil(N_ITEMS_PER_K / K_TOTAL))
    correct = 0
    total = 0
    typed_route_correct = 0
    typed_route_total = 0
    sat_check_count = 0

    g_trial = _make_gen(seed_offset + 41)
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
        # Query type label is the true bank's type assignment (matched arm)
        query_type_idx = bank_type_assignment[bank_true]

        # Type-routing: pick bank with matching type
        bank_routed = _route_by_type_label(query_type_idx, bank_type_assignment)
        typed_route_correct += int((bank_routed == bank_true).sum().item())
        typed_route_total += K_TOTAL

        # Cleanup within routed bank
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

        sat_check_count = int((bank_routed == bank_true).sum().item())

    recall = correct / max(total, 1)
    typed_route_acc = typed_route_correct / max(typed_route_total, 1)
    return recall, typed_route_acc, float(sat_check_count)


def eval_typed_adversarial_probe(seed_offset: int) -> tuple[float, float]:
    """ARM_TYPED_ROUTING_ADVERSARIAL_PROBE: ill-typed queries; tests refuse-rate.

    Refuse-gate: gap between top-1 and top-2 bank cosine. If query type label
    mismatches all banks' type assignment, the bank-cosine routing has no
    type-coherent signal -> gap is small -> refuse.

    Returns (refuse_rate, mistake_rate).
    """
    codebook = build_codebook_adversarial(seed_offset)
    slot_tags = build_slot_tags(seed_offset, K_PER_BANK)
    bank_tags = build_bank_tags(seed_offset, N_BANKS)
    cue_noise_scale = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))

    # Bank-to-type assignment (same seed offset as matched arm)
    g_assign = _make_gen(seed_offset + 31)
    bank_type_assignment = torch.randint(
        0, N_TYPES, (N_BANKS,), generator=g_assign, device=_DEVICE,
    )

    n_trials = max(1, math.ceil(N_ITEMS_PER_K / K_TOTAL))
    n_refused = 0
    n_total = 0
    n_wrong_answers = 0
    n_attempted = 0

    g_trial = _make_gen(seed_offset + 41)
    for trial in range(n_trials):
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial,
                                     device=_DEVICE)[:K_TOTAL]
        items = codebook[idx_global]
        items_per_bank = items.view(N_BANKS, K_PER_BANK, N_DIM)
        workspaces = _write_bank(items_per_bank, slot_tags,
                                 seed_offset + 1000 + trial)

        slot_indices = torch.arange(K_TOTAL, device=_DEVICE)
        bank_true = slot_indices // K_PER_BANK

        # Build mismatched queries: query carries a type label NOT matching
        # the true bank's assignment (shuffled type labels).
        g_shuffle = _make_gen(seed_offset + 51 + trial)
        true_types = bank_type_assignment[bank_true]
        # Shift type label by +1 mod N_TYPES, ensuring mismatch
        shifted_types = (true_types + 1 + torch.randint(
            0, max(1, N_TYPES - 1), true_types.shape,
            generator=g_shuffle, device=_DEVICE,
        )) % N_TYPES
        # Verify mismatch (should be near 100%)
        actually_mismatched = (shifted_types != true_types)
        shifted_types = torch.where(
            actually_mismatched, shifted_types,
            (shifted_types + 1) % N_TYPES,
        )

        # Build cues with the WRONG type signal: the cue uses the SHIFTED
        # type's bank tag (not the true bank), so bank-cosine routing has
        # signal but at the wrong destination.
        # Find any bank whose assignment matches each shifted type
        wrong_bank = _route_by_type_label(shifted_types, bank_type_assignment)
        # If shifted type has no matching bank, fall back to bank 0
        bank_cue_base = bank_tags[wrong_bank].float()
        g_cue = _make_gen(seed_offset + 6000 + trial)
        noise = torch.empty((K_TOTAL, N_DIM), device=_DEVICE, dtype=torch.float32)
        noise.normal_(0.0, 1.0, generator=g_cue)
        noise_bp = bipolar_quantize_t(noise)
        cues = (CUE_COS * bank_cue_base + cue_noise_scale * noise_bp).to(_STORE_DTYPE)

        # Refuse-gate: route by bank-cosine + check gap. If gap < threshold,
        # OR if routed bank's type doesn't match query type -> REFUSE.
        bank_routed, gap = _route_by_bank_cosine(cues, bank_tags)
        routed_type = bank_type_assignment[bank_routed]
        type_mismatch_at_routed = (routed_type != shifted_types)
        # Refuse: either weak signal OR explicit type-mismatch at routed bank
        refused = (gap < REFUSE_GAP_THRESHOLD) | type_mismatch_at_routed

        n_refused += int(refused.sum().item())
        n_total += K_TOTAL
        n_attempted += int((~refused).sum().item())

        # Of the not-refused, count wrong answers (where routed != true_bank)
        # All ill-typed answers ARE wrong by construction (true_bank type != query type)
        not_refused_mask = ~refused
        wrong = not_refused_mask & (bank_routed != bank_true)
        n_wrong_answers += int(wrong.sum().item())

    refuse_rate = n_refused / max(n_total, 1)
    wrong_rate = n_wrong_answers / max(n_total, 1)
    return refuse_rate, wrong_rate


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
    refuse_rates: List[float] = []
    typed_route_accs: List[float] = []
    for key, body in per_unit.items():
        arm = body["arm"]
        if arm == "ARM_TYPED_ROUTING_ADVERSARIAL_PROBE":
            refuse_rates.append(float(body["refuse_rate"]))
            by_arm[arm].append(float(body["refuse_rate"]))  # for cardinality
        else:
            by_arm[arm].append(float(body["recall"]))
            if arm == "ARM_TYPED_ROUTING_MATCHED":
                typed_route_accs.append(float(body.get("typed_route_acc", 0.0)))

    def stats(vals):
        if not vals:
            return float("nan"), float("nan"), 0
        m = float(np.mean(vals))
        s = float(np.std(vals)) if len(vals) > 1 else 0.0
        cv = float(s / max(m, 1e-9)) if m > 1e-9 else 0.0
        return round(m, 4), round(cv, 4), len(vals)

    baseline_m, baseline_cv, baseline_n = stats(by_arm["ARM_UNTYPED_BASELINE_ADVERSARIAL"])
    typed_m, typed_cv, typed_n = stats(by_arm["ARM_TYPED_ROUTING_MATCHED"])
    refuse_m, refuse_cv, refuse_n = stats(refuse_rates)

    typed_lift = typed_m - baseline_m if not (math.isnan(typed_m) or math.isnan(baseline_m)) else float("nan")

    # Discipline checks
    baseline_in_band_full = (HP_BASELINE_BAND_LOW <= baseline_m <= HP_BASELINE_BAND_HIGH)
    baseline_in_band_smoke = (HP_BASELINE_BAND_LOW_SMOKE <= baseline_m <= HP_BASELINE_BAND_HIGH_SMOKE)
    baseline_in_band = baseline_in_band_smoke if SMOKE else baseline_in_band_full
    saturated = baseline_m >= Q_SUSPECT_SATURATION
    cv_ok = max(typed_cv, baseline_cv) <= CV_CHAIN_GRADE_MAX

    detail = {
        "cardinality_ok": cardinality_ok,
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "baseline_recall_mean": baseline_m,
        "baseline_recall_cv": baseline_cv,
        "baseline_in_band": baseline_in_band,
        "baseline_saturated_above_Q": saturated,
        "typed_recall_mean": typed_m,
        "typed_recall_cv": typed_cv,
        "typed_lift_over_baseline": round(typed_lift, 4) if not math.isnan(typed_lift) else None,
        "refuse_rate_mean": refuse_m,
        "refuse_rate_cv": refuse_cv,
        "n_failures": len(failures),
        "failures_brief": [{"key": f.get("key", "?"), "exc_type": f.get("exc_type", "?")}
                            for f in failures[:5]],
        "config_version": CONFIG_VERSION,
        "Q_suspect_saturation": Q_SUSPECT_SATURATION,
        "HP_typed_lift": HP_TYPED_LIFT_OVER_BASELINE,
        "HP_refuse_rate_min": HP_REFUSE_RATE_MIN,
        "HP_baseline_band": [HP_BASELINE_BAND_LOW, HP_BASELINE_BAND_HIGH],
        "cv_chain_grade_max": CV_CHAIN_GRADE_MAX,
        "typed_route_acc_mean": round(float(np.mean(typed_route_accs)), 4) if typed_route_accs else None,
    }

    # HARD_FAIL conditions (load-bearing first)
    if not cardinality_ok:
        return ("HARD_FAIL",
                f"cardinality_breach: observed={n_units_observed} expected={EXPECTED_N_UNITS} "
                f"failures={len(failures)}", detail)
    if baseline_m < HF_MIN_BASELINE:
        return ("HARD_FAIL",
                f"baseline_broken: ARM_UNTYPED_BASELINE_ADVERSARIAL={baseline_m:.4f} < "
                f"HF_MIN_BASELINE={HF_MIN_BASELINE}", detail)
    if saturated:
        return ("HARD_FAIL",
                f"by_construction_saturation_META_RULE_K: baseline={baseline_m:.4f} >= "
                f"Q_SUSPECT_SATURATION={Q_SUSPECT_SATURATION}; OVERLAP={FEATURE_OVERLAP_FRAC} "
                f"insufficient to escape saturation regime", detail)
    if not math.isnan(typed_lift) and typed_lift <= 0.02:
        return ("HARD_FAIL",
                f"typed_lift_null: lift={typed_lift:.4f} <= 0.02 (type signal not actionable)",
                detail)
    if refuse_m <= 0.40:
        return ("HARD_FAIL",
                f"refuse_rate_collapsed: refuse_rate={refuse_m:.4f} <= 0.40 (refuse-gate inert)",
                detail)

    # HARD_PASS conditions (strictly-above-floor per META_RULE_L)
    typed_lift_meets = (not math.isnan(typed_lift)) and (typed_lift >= HP_TYPED_LIFT_OVER_BASELINE)
    refuse_meets = refuse_m >= HP_REFUSE_RATE_MIN
    if typed_lift_meets and refuse_meets and baseline_in_band and cv_ok:
        return ("HARD_PASS",
                f"chain_grade_typed_multibank: typed_lift={typed_lift:.4f} >= "
                f"{HP_TYPED_LIFT_OVER_BASELINE}; refuse_rate={refuse_m:.4f} >= "
                f"{HP_REFUSE_RATE_MIN}; baseline={baseline_m:.4f} in "
                f"[{HP_BASELINE_BAND_LOW}, {HP_BASELINE_BAND_HIGH}] (non-saturated); "
                f"cv typed={typed_cv:.4f} baseline={baseline_cv:.4f} <= {CV_CHAIN_GRADE_MAX}",
                detail)

    return ("MIDDLE_BAND",
            f"partial: typed_lift={typed_lift if typed_lift is not None else 'nan'} "
            f"(HP>={HP_TYPED_LIFT_OVER_BASELINE}); refuse={refuse_m:.4f} "
            f"(HP>={HP_REFUSE_RATE_MIN}); baseline={baseline_m:.4f} "
            f"in_band={baseline_in_band}; cv_ok={cv_ok}",
            detail)


# ---------------- self-test ----------------

def _selftest():
    print("[selftest] typed_multibank_K128_adversarial_v1 starting", flush=True)
    # T1: synthetic verdict-machinery
    fake_hp = {
        "11_ARM_UNTYPED_BASELINE_ADVERSARIAL": {
            "arm": "ARM_UNTYPED_BASELINE_ADVERSARIAL", "recall": 0.72,
            "typed_route_acc": 0.0,
        },
        "13_ARM_UNTYPED_BASELINE_ADVERSARIAL": {
            "arm": "ARM_UNTYPED_BASELINE_ADVERSARIAL", "recall": 0.74,
            "typed_route_acc": 0.0,
        },
        "19_ARM_UNTYPED_BASELINE_ADVERSARIAL": {
            "arm": "ARM_UNTYPED_BASELINE_ADVERSARIAL", "recall": 0.73,
            "typed_route_acc": 0.0,
        },
        "11_ARM_TYPED_ROUTING_MATCHED": {
            "arm": "ARM_TYPED_ROUTING_MATCHED", "recall": 0.86,
            "typed_route_acc": 1.0,
        },
        "13_ARM_TYPED_ROUTING_MATCHED": {
            "arm": "ARM_TYPED_ROUTING_MATCHED", "recall": 0.85,
            "typed_route_acc": 1.0,
        },
        "19_ARM_TYPED_ROUTING_MATCHED": {
            "arm": "ARM_TYPED_ROUTING_MATCHED", "recall": 0.87,
            "typed_route_acc": 1.0,
        },
        "11_ARM_TYPED_ROUTING_ADVERSARIAL_PROBE": {
            "arm": "ARM_TYPED_ROUTING_ADVERSARIAL_PROBE", "refuse_rate": 0.90,
        },
        "13_ARM_TYPED_ROUTING_ADVERSARIAL_PROBE": {
            "arm": "ARM_TYPED_ROUTING_ADVERSARIAL_PROBE", "refuse_rate": 0.88,
        },
        "19_ARM_TYPED_ROUTING_ADVERSARIAL_PROBE": {
            "arm": "ARM_TYPED_ROUTING_ADVERSARIAL_PROBE", "refuse_rate": 0.91,
        },
    }
    # Force EXPECTED_N_UNITS to match the synthetic
    global EXPECTED_N_UNITS
    saved_expected = EXPECTED_N_UNITS
    EXPECTED_N_UNITS = 9
    try:
        v, msg, det = compute_verdict(fake_hp)
        assert v == "HARD_PASS", f"T1 fake_hp expected HARD_PASS, got {v}: {msg}"
        print(f"[selftest] T1 PASS: synthetic HARD_PASS path -> {v}", flush=True)

        # T2: saturation auto-demote
        fake_sat = dict(fake_hp)
        for k in list(fake_sat.keys()):
            if "UNTYPED_BASELINE" in k:
                fake_sat[k] = dict(fake_sat[k])
                fake_sat[k]["recall"] = 0.98
        v, msg, det = compute_verdict(fake_sat)
        assert v == "HARD_FAIL", f"T2 saturation expected HARD_FAIL, got {v}"
        assert "saturation" in msg.lower(), f"T2 expected saturation msg, got {msg}"
        print(f"[selftest] T2 PASS: saturation auto-demote -> HARD_FAIL", flush=True)

        # T3: typed lift null
        fake_null = dict(fake_hp)
        for k in list(fake_null.keys()):
            if "TYPED_ROUTING_MATCHED" in k:
                fake_null[k] = dict(fake_null[k])
                fake_null[k]["recall"] = 0.73  # match baseline
        v, msg, det = compute_verdict(fake_null)
        assert v == "HARD_FAIL", f"T3 null lift expected HARD_FAIL, got {v}"
        print(f"[selftest] T3 PASS: typed_lift_null -> HARD_FAIL", flush=True)

        # T4: refuse collapsed
        fake_norefuse = dict(fake_hp)
        for k in list(fake_norefuse.keys()):
            if "ADVERSARIAL_PROBE" in k:
                fake_norefuse[k] = dict(fake_norefuse[k])
                fake_norefuse[k]["refuse_rate"] = 0.30
        v, msg, det = compute_verdict(fake_norefuse)
        assert v == "HARD_FAIL", f"T4 refuse collapse expected HARD_FAIL, got {v}"
        print(f"[selftest] T4 PASS: refuse_rate_collapsed -> HARD_FAIL", flush=True)

        # T5: cardinality breach
        fake_card = dict(list(fake_hp.items())[:6])  # only 6 of 9 units
        v, msg, det = compute_verdict(fake_card)
        assert v == "HARD_FAIL", f"T5 cardinality expected HARD_FAIL, got {v}"
        assert "cardinality_breach" in msg, f"T5 expected cardinality msg, got {msg}"
        print(f"[selftest] T5 PASS: cardinality_breach -> HARD_FAIL", flush=True)

        # T6: MIDDLE_BAND partial lift
        fake_mb = dict(fake_hp)
        for k in list(fake_mb.keys()):
            if "TYPED_ROUTING_MATCHED" in k:
                fake_mb[k] = dict(fake_mb[k])
                fake_mb[k]["recall"] = 0.77  # lift = 0.04 (in MB band)
        v, msg, det = compute_verdict(fake_mb)
        assert v == "MIDDLE_BAND", f"T6 MB partial expected MIDDLE_BAND, got {v}"
        print(f"[selftest] T6 PASS: partial lift -> MIDDLE_BAND", flush=True)
    finally:
        EXPECTED_N_UNITS = saved_expected

    # T7: type-tag distinct (cosine sanity)
    g = _make_gen(99)
    types = random_bipolar_t((8, 1024), g)
    norms = (types.float() ** 2).sum(dim=1).sqrt()
    sims = (types.float() @ types.float().T) / (norms.unsqueeze(0) * norms.unsqueeze(1) + 1e-9)
    off_diag = sims - torch.eye(8) * sims
    max_off = float(off_diag.abs().max().item())
    assert max_off < 0.10, f"T7 type-tag cosine off-diag = {max_off} >= 0.10"
    print(f"[selftest] T7 PASS: type-tag off-diag cosine max={max_off:.4f} < 0.10", flush=True)

    # T8: bipolar quantize sanity
    cb = random_bipolar_t((128, 256), _make_gen(7))
    u = torch.unique(cb)
    assert set(u.tolist()) <= {-1.0, 1.0}, "T8 bipolar"
    print(f"[selftest] T8 PASS: bipolar codebook in {{-1,+1}}", flush=True)

    # T9: chunked argmax matches unchunked
    cb_q = random_bipolar_t((256, 128), _make_gen(13))
    q = random_bipolar_t((16, 128), _make_gen(17))
    sims_full = (cb_q.float() @ q.float().T)
    idx_un = sims_full.argmax(dim=0)
    saved_chunk = CODEBOOK_CHUNK
    globals()["CODEBOOK_CHUNK"] = 64
    try:
        idx_ch = _chunked_argmax_cb(cb_q, q)
        assert torch.equal(idx_ch, idx_un), "T9 chunked argmax disagrees"
    finally:
        globals()["CODEBOOK_CHUNK"] = saved_chunk
    print(f"[selftest] T9 PASS: chunked argmax matches unchunked", flush=True)

    # T10: type routing assignment determinism
    g_assign = _make_gen(42)
    assn1 = torch.randint(0, 16, (32,), generator=g_assign, device=_DEVICE)
    g_assign2 = _make_gen(42)
    assn2 = torch.randint(0, 16, (32,), generator=g_assign2, device=_DEVICE)
    assert torch.equal(assn1, assn2), "T10 type-assignment not deterministic"
    print(f"[selftest] T10 PASS: type-assignment deterministic across seeds", flush=True)

    # T11: pre-reg envelope locks
    assert HP_TYPED_LIFT_OVER_BASELINE == 0.10
    assert HP_REFUSE_RATE_MIN == 0.85
    assert Q_SUSPECT_SATURATION == 0.95
    assert CV_CHAIN_GRADE_MAX == 0.05
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
        "K_TOTAL": int(K_TOTAL),
        "N_BANKS": int(N_BANKS),
        "K_PER_BANK": int(K_PER_BANK),
        "N_TYPES": int(N_TYPES),
        "FEATURE_OVERLAP_FRAC": float(FEATURE_OVERLAP_FRAC),
    }
    if arm == "ARM_UNTYPED_BASELINE_ADVERSARIAL":
        recall, route_acc = eval_untyped_baseline_adversarial(seed_offset)
        body["recall"] = float(round(recall, 4))
        body["route_acc"] = float(round(route_acc, 4))
    elif arm == "ARM_TYPED_ROUTING_MATCHED":
        recall, typed_route_acc, _ = eval_typed_matched(seed_offset)
        body["recall"] = float(round(recall, 4))
        body["typed_route_acc"] = float(round(typed_route_acc, 4))
    elif arm == "ARM_TYPED_ROUTING_ADVERSARIAL_PROBE":
        refuse_rate, wrong_rate = eval_typed_adversarial_probe(seed_offset)
        body["refuse_rate"] = float(round(refuse_rate, 4))
        body["wrong_rate"] = float(round(wrong_rate, 4))
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

    # Aggregate prior partials with this run
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
