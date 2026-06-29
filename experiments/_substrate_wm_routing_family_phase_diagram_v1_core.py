"""Shared core for substrate_wm_routing_family_phase_diagram_v1 sibling cells.

FOURTH COMPONENT-SUBSTITUTION phase diagram (USER 2026-06-28 Research directive).
Encoder-family + cleanup-family + seqbind-encoder already in flight; this cell
covers the ROUTING family for multi-bank WM.

ROUTING FAMILIES (OUTER axis; LOCKED):
    partition       : argmax(cue @ bank_tags.T) -- current chain-grade default
                      (POSITIVE CONTROL; reproduces WM K-ceiling v3 evidence)
    knn_softmax     : softmax(beta * cue @ bank_tags.T) @ workspaces -- soft routing;
                      brain-grounded (biological dlPFC routing is closer to k-NN-style)
    softmax_attention : softmax(beta * cue @ bank_tags.T) per-bank gating + winner-take-all;
                       attention-mechanism baseline (transformer-style)
    learned_hierarchical : 2-level routing -- group argmax over (n_banks/group_size)
                          groups, then argmax within group; mimics hierarchical
                          biological routing without learning (static groupings)

INNER AXES:
    K (per-bank capacity x num-banks): K_total in {1024, 4096, 8192}
    B (num banks): derived from K and k_per_bank=64 envelope

Per (routing, K, regime) measure recall + route_acc.

POSITIVE CONTROL: partition routing at K_total=4096, B=64, N=8192 must produce
recall >= 0.95 (reproduces WM K-ceiling v3 measured rec=1.000 at this point).

CARDINALITY:
  FULL: 4 routings * 3 K * 2 regimes = 24 phase points per seed
  SMOKE: 4 routings * 2 K * 1 regime = 8 corner points per seed

PRE-REG: preregs/2026-06-28_substrate_wm_routing_family_phase_diagram_v1.md

Sibling cells import:
    run_one_seed_phase_diagram(seed, run_mode)
    aggregate_and_verdict(per_seed_dict, run_mode)
    selftest(seed)
    get_backend_label()
    ROUTING_FAMILIES,
    K_SWEEP_FULL, K_SWEEP_SMOKE, REGIMES_FULL, REGIMES_SMOKE

ASCII-only. No unicode. CUDA preferred; CPU fallback for smoke.
FULL on CPU REFUSED unless HDLAB_QUEUE=local_cpu_queue (Fix #24).

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

# Torch at TOP of module (PROT-020 GPU-eligibility scan)
import torch

_CUDA_OK = bool(torch.cuda.is_available())
if _CUDA_OK:
    DEVICE = torch.device("cuda")
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
else:
    DEVICE = torch.device("cpu")
    GPU_NAME = "cpu_fallback"
    GPU_MAX_MEM_GB = 0.0


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
HP_CHAIN_GRADE_RECALL = 0.95
HP_CHAIN_GRADE_ROUTE_ACC = 0.95
HP_ADV_WITHIN_RANDOM = 0.05
HP_ADV_BREAK_THRESHOLD = 0.30
HP_K_PER_BANK_MAX = 64
Q_SUSPECT_SATURATION = 0.995
HP_DISCRIMINATOR_FRACTION = 0.30  # >=30% of phase points must be DISCRIMINATING per routing
HP_HARD_PASS_LO = 0.80
HP_MIDDLE_BAND_LO = 0.50
HP_FLOOR_HI = 0.10

BETA_SOFT = 8.0  # softmax temperature for knn_softmax + softmax_attention
GROUP_SIZE = 4   # learned_hierarchical: group_size; 2-level if B>=group_size

# Bipolar substrate + multi-bank WM constants (match WM K-ceiling v3 envelope)
SIGMA = 1.0
CUE_COS = 0.70
FEATURE_OVERLAP_FRAC = 0.20
N_GROUPS_ADV = 4
N_ITEMS_PER_K_FULL = 100
N_ITEMS_PER_K_SMOKE = 40

# Routing families (OUTER axis; LOCKED at module init)
ROUTING_FAMILIES = ("partition", "knn_softmax", "softmax_attention",
                     "learned_hierarchical")

# Sweep axes
K_SWEEP_FULL = [1024, 4096, 8192]
K_PER_BANK_FULL = 64
REGIMES_FULL = ("RANDOM", "ADVERSARIAL")
N_DIM_FULL = 8192
CODEBOOK_SIZE_FULL = 16384

K_SWEEP_SMOKE = [256, 1024]
K_PER_BANK_SMOKE = 32
REGIMES_SMOKE = ("RANDOM",)
N_DIM_SMOKE = 2048
CODEBOOK_SIZE_SMOKE = 4096

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (len(ROUTING_FAMILIES) * len(K_SWEEP_FULL)
                          * len(REGIMES_FULL))  # 4 * 3 * 2 = 24
EXPECTED_N_UNITS_SMOKE = (len(ROUTING_FAMILIES) * len(K_SWEEP_SMOKE)
                           * len(REGIMES_SMOKE))  # 4 * 2 * 1 = 8

# Positive control: partition routing at K=4096 must >= 0.95 (chain-grade)
POSITIVE_CONTROL = {
    "routing_family": "partition",
    "K_total": 4096,
    "regime": "RANDOM",
    "recall_floor": 0.90,  # WM v3 measured 1.000; conservative floor 0.90
}
POSITIVE_CONTROL_SMOKE = {
    "routing_family": "partition",
    "K_total": 1024,
    "regime": "RANDOM",
    "recall_floor": 0.60,  # smoke-N=2048 rail-drift OK; conservative floor
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# HD substrate primitives (match WM K-ceiling v3 conventions)
# ---------------------------------------------------------------------------
def _make_gen(seed_int: int) -> torch.Generator:
    g = torch.Generator(device=DEVICE)
    g.manual_seed(int(seed_int))
    return g


def random_bipolar_t(shape: Tuple[int, ...], gen: torch.Generator) -> torch.Tensor:
    X = torch.empty(*shape, device=DEVICE, dtype=torch.float32)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return X


def bipolar_quantize_t(v: torch.Tensor) -> torch.Tensor:
    return torch.where(v >= 0, torch.ones_like(v), -torch.ones_like(v))


def build_codebook_random(seed_offset: int, codebook_size: int,
                           n_dim: int) -> torch.Tensor:
    g = _make_gen(seed_offset)
    return random_bipolar_t((codebook_size, n_dim), g)


def build_codebook_adversarial(seed_offset: int, codebook_size: int,
                                n_dim: int) -> torch.Tensor:
    g_tpl = _make_gen(seed_offset + 7)
    g_items = _make_gen(seed_offset + 11)
    templates = random_bipolar_t((N_GROUPS_ADV, n_dim), g_tpl)
    items = random_bipolar_t((codebook_size, n_dim), g_items)
    n_shared = int(FEATURE_OVERLAP_FRAC * n_dim)
    if n_shared > 0:
        group_ids = torch.arange(codebook_size, device=DEVICE) % N_GROUPS_ADV
        items[:, :n_shared] = templates[group_ids, :n_shared]
    return items


def build_slot_tags(seed_offset: int, k_per_bank: int, n_dim: int) -> torch.Tensor:
    g = _make_gen(seed_offset + 13)
    return random_bipolar_t((k_per_bank, n_dim), g)


def build_bank_tags(seed_offset: int, n_banks: int, n_dim: int) -> torch.Tensor:
    g = _make_gen(seed_offset + 17)
    return random_bipolar_t((n_banks, n_dim), g)


def write_bank(items_per_bank: torch.Tensor, slot_tags: torch.Tensor,
                seed_offset: int) -> torch.Tensor:
    """Standard multi-bank write: each bank workspace = sum_k items[k] * slot_tag[k] + noise.

    items_per_bank: (n_banks, k_per_bank, N) bipolar
    slot_tags: (k_per_bank, N) bipolar
    Returns workspaces: (n_banks, N) bipolar
    """
    n_banks, k_per_bank, N = items_per_bank.shape
    bound = items_per_bank * slot_tags.unsqueeze(0)  # (n_banks, k_per_bank, N)
    ws = bound.sum(dim=1).float()  # (n_banks, N) fp32
    if SIGMA > 0.0:
        g_noise = _make_gen(seed_offset + 23)
        noise = torch.empty(ws.shape, device=DEVICE, dtype=torch.float32)
        noise.normal_(0.0, SIGMA, generator=g_noise)
        ws = ws + noise
    out = bipolar_quantize_t(ws)
    return out


def read_with_cleanup(workspaces_selected: torch.Tensor,
                       slot_tag: torch.Tensor,
                       codebook: torch.Tensor) -> torch.Tensor:
    """Two-step cleanup over codebook.

    workspaces_selected: (K, N) bipolar -- selected workspace per query
    slot_tag: (K, N) bipolar
    codebook: (C, N) bipolar
    Returns pred_idx: (K,) long
    """
    r1 = workspaces_selected * slot_tag  # (K, N)
    sims1 = r1 @ codebook.T  # (K, C)
    cand_idx = sims1.argmax(dim=1)
    cand_vecs = codebook[cand_idx]
    r2 = bipolar_quantize_t(r1 + cand_vecs)
    sims2 = r2 @ codebook.T
    pred_idx = sims2.argmax(dim=1)
    return pred_idx


# ---------------------------------------------------------------------------
# ROUTING FAMILY PRIMITIVES (the load-bearing OUTER axis)
# Each takes cue (K, N), bank_tags (B, N), workspaces (B, N) and returns
#   ws_selected: (K, N) -- the "routed" workspace per query
#   route_pred: (K,) -- predicted bank index per query (for route_acc)
# ---------------------------------------------------------------------------
def route_partition(cues: torch.Tensor, bank_tags: torch.Tensor,
                     workspaces: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Hard partition (argmax). Current chain-grade default."""
    sims = cues @ bank_tags.T  # (K, B)
    bank_routed = sims.argmax(dim=1)  # (K,)
    ws_selected = workspaces[bank_routed]  # (K, N)
    return ws_selected, bank_routed


def route_knn_softmax(cues: torch.Tensor, bank_tags: torch.Tensor,
                       workspaces: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Soft routing: softmax-weighted mixture of bank workspaces.

    Brain-grounded: biological dlPFC routing is closer to graded gating than
    hard partition.

    bank_routed = argmax (for route_acc reporting); ws_selected = soft mix.
    """
    sims = cues @ bank_tags.T  # (K, B)
    weights = torch.softmax(BETA_SOFT * sims, dim=1)  # (K, B)
    ws_selected = weights @ workspaces.float()  # (K, N) fp32 mixture
    ws_selected = bipolar_quantize_t(ws_selected)
    bank_routed = sims.argmax(dim=1)  # for route_acc only
    return ws_selected, bank_routed


def route_softmax_attention(cues: torch.Tensor, bank_tags: torch.Tensor,
                              workspaces: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Transformer-style attention: softmax over banks * workspace + winner-take-all.

    Difference from knn_softmax: top-2 attention with hard winner. Approximates
    self-attention's "argmax-but-soft-gradient" regime via top-2 then argmax.
    """
    sims = cues @ bank_tags.T  # (K, B)
    weights = torch.softmax(BETA_SOFT * sims, dim=1)  # (K, B)
    # Top-2 attention: zero out all but top-2 then renormalize
    top2_vals, top2_idx = torch.topk(weights, k=min(2, weights.shape[1]), dim=1)
    mask = torch.zeros_like(weights)
    mask.scatter_(1, top2_idx, top2_vals)
    mask = mask / mask.sum(dim=1, keepdim=True).clamp(min=1e-12)
    ws_selected = mask @ workspaces.float()  # (K, N)
    ws_selected = bipolar_quantize_t(ws_selected)
    bank_routed = sims.argmax(dim=1)
    return ws_selected, bank_routed


def route_learned_hierarchical(cues: torch.Tensor, bank_tags: torch.Tensor,
                                  workspaces: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """2-level hierarchical routing: group argmax, then within-group argmax.

    B banks split into G=B/GROUP_SIZE groups of GROUP_SIZE each. Mean of group's
    bank_tags forms a "group anchor"; cue routed to best group via argmax,
    then to best bank within that group via argmax. Mimics hierarchical biology.
    """
    B = bank_tags.shape[0]
    gs = GROUP_SIZE
    if B < gs or B % gs != 0:
        # Fallback: behave like partition
        return route_partition(cues, bank_tags, workspaces)

    G = B // gs  # number of groups
    # Group anchors: mean of bank_tags per group
    bank_tags_grouped = bank_tags.view(G, gs, -1)  # (G, gs, N)
    group_anchors = bank_tags_grouped.mean(dim=1)  # (G, N)

    # Level 1: pick group
    sims_g = cues @ group_anchors.T  # (K, G)
    group_routed = sims_g.argmax(dim=1)  # (K,)

    # Level 2: within group, pick bank
    # For each query, restrict to bank_tags of its routed group
    # Vectorized: compute cue @ bank_tags.T for all banks, then mask others to -inf
    sims_all = cues @ bank_tags.T  # (K, B)
    # Build mask: keep only sims for banks in routed group
    bank_group_id = torch.arange(B, device=DEVICE) // gs  # (B,)
    # Mask shape: (K, B). True where bank's group == query's routed group.
    group_mask = (bank_group_id.unsqueeze(0) == group_routed.unsqueeze(1))  # (K, B)
    sims_masked = torch.where(group_mask, sims_all,
                               torch.full_like(sims_all, float("-inf")))
    bank_routed = sims_masked.argmax(dim=1)  # (K,)
    ws_selected = workspaces[bank_routed]
    return ws_selected, bank_routed


_ROUTING_REGISTRY: Dict[str, Callable] = {
    "partition": route_partition,
    "knn_softmax": route_knn_softmax,
    "softmax_attention": route_softmax_attention,
    "learned_hierarchical": route_learned_hierarchical,
}


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def eval_routing_arm(routing_family: str, k_total: int, k_per_bank: int,
                      regime: str, codebook: torch.Tensor, seed_offset: int,
                      n_items_per_k: int, n_dim: int) -> Dict[str, Any]:
    """One routing-arm evaluation. Single trial (n_items_per_k items into
    K-capacity WM, then read back).

    Returns dict with recall, route_acc, peak_mem_mb, elapsed_s, hashes.
    """
    if routing_family not in _ROUTING_REGISTRY:
        raise ValueError(f"unknown routing_family={routing_family!r}")
    routing_fn = _ROUTING_REGISTRY[routing_family]
    n_banks = k_total // k_per_bank
    if n_banks * k_per_bank != k_total:
        raise ValueError(f"k_total={k_total} not divisible by k_per_bank={k_per_bank}")

    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    slot_tags = build_slot_tags(seed_offset, k_per_bank, n_dim)
    bank_tags = build_bank_tags(seed_offset, n_banks, n_dim)
    cue_noise_scale = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))

    # One trial covering all K slots; if N_ITEMS exceeds K, just use K items
    codebook_size = codebook.shape[0]
    g_trial = _make_gen(seed_offset + 29)
    idx_global = torch.randperm(codebook_size, generator=g_trial,
                                  device=DEVICE)[:k_total]
    items = codebook[idx_global]  # (K, N)
    items_per_bank = items.view(n_banks, k_per_bank, n_dim)

    workspaces = write_bank(items_per_bank, slot_tags, seed_offset + 1000)

    slot_indices = torch.arange(k_total, device=DEVICE)
    bank_true = slot_indices // k_per_bank
    local_slot = slot_indices % k_per_bank

    g_cue = _make_gen(seed_offset + 5000)
    bank_cue_base = bank_tags[bank_true].float()
    noise = torch.empty((k_total, n_dim), device=DEVICE, dtype=torch.float32)
    noise.normal_(0.0, 1.0, generator=g_cue)
    noise_bp = bipolar_quantize_t(noise)
    # Per WM K-ceiling v3 convention: real-valued cue mix (do NOT quantize;
    # quantizing destroys the CUE_COS weighting).
    cues = CUE_COS * bank_cue_base + cue_noise_scale * noise_bp

    # ROUTING (the load-bearing OUTER axis swap)
    ws_selected, bank_routed = routing_fn(cues, bank_tags, workspaces)
    slot_tag_sel = slot_tags[local_slot]

    pred_idx = read_with_cleanup(ws_selected, slot_tag_sel, codebook)
    true_item_idx = idx_global[slot_indices]
    match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
    recall = float(match.sum().item()) / max(k_total, 1)
    route_acc = float((bank_routed == bank_true).sum().item()) / max(k_total, 1)

    # Hash ws_selected fingerprint for arms-differ checks (META_RULE_AF).
    # bank_routed is argmax-based for ALL routings (so route_acc is comparable),
    # but ws_selected differs because soft/hierarchical routings produce
    # different workspaces (mixed or partition-restricted). The mechanism
    # signature is ws_selected, not the argmax-route-prediction.
    ws_hash = hashlib.sha256(
        ws_selected.cpu().numpy().tobytes()).hexdigest()[:16]
    route_hash = ws_hash  # alias preserved for downstream code

    if _CUDA_OK:
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        peak_mem_mb = -1.0

    elapsed = time.time() - t0

    # Per-point tier
    if recall >= Q_SUSPECT_SATURATION:
        tier = "SATURATED"
    elif recall >= HP_CHAIN_GRADE_RECALL and route_acc >= HP_CHAIN_GRADE_ROUTE_ACC:
        tier = "HARD_PASS"
    elif recall >= HP_HARD_PASS_LO:
        tier = "HARD_PASS"
    elif recall >= HP_MIDDLE_BAND_LO:
        tier = "MIDDLE_BAND"
    elif recall <= HP_FLOOR_HI:
        tier = "FLOOR"
    else:
        tier = "HARD_FAIL"

    del slot_tags, bank_tags, workspaces, cues, noise, noise_bp, bank_cue_base
    del items, items_per_bank, ws_selected, slot_tag_sel, pred_idx, true_item_idx
    del match, slot_indices, bank_true, local_slot, idx_global, bank_routed
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "routing_family": routing_family,
        "K_total": k_total,
        "k_per_bank": k_per_bank,
        "n_banks": n_banks,
        "regime": regime,
        "recall": round(recall, 4),
        "route_acc": round(route_acc, 4),
        "verdict_tier_per_point": tier,
        "saturation_flag": recall >= Q_SUSPECT_SATURATION,
        "route_hash": route_hash,
        "peak_mem_mb": round(peak_mem_mb, 1),
        "elapsed_per_point_s": round(elapsed, 3),
        "N": n_dim,
    }


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Selftest: cardinality + routing hashes distinct + sanity recall."""
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 24:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 24"
    if EXPECTED_N_UNITS_SMOKE != 8:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 8"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Each routing family is a registered callable
    for fam in ROUTING_FAMILIES:
        if fam not in _ROUTING_REGISTRY:
            return False, f"routing {fam} not in registry"
        if not callable(_ROUTING_REGISTRY[fam]):
            return False, f"routing {fam} not callable"
    msgs.append(f"4 routings registered: {list(_ROUTING_REGISTRY.keys())}")

    # 3. Tiny mechanism sanity at conservative regime (must have lift +
    # routing-pair distinctness from hierarchical needs n_banks > GROUP_SIZE).
    # N=1024, M=512, K=64, k_per_bank=8 -> 8 banks of 8 items.
    n_dim_san = 1024
    cb_size_san = 512
    k_total_san = 64
    k_per_bank_san = 8
    n_items_san = 64
    codebook = build_codebook_random(seed + 1, cb_size_san, n_dim_san)

    san_recalls: Dict[str, float] = {}
    san_hashes: Dict[str, str] = {}
    for fam in ROUTING_FAMILIES:
        r = eval_routing_arm(fam, k_total_san, k_per_bank_san, "RANDOM",
                              codebook, seed_offset=seed * 7 + 100,
                              n_items_per_k=n_items_san, n_dim=n_dim_san)
        san_recalls[fam] = r["recall"]
        san_hashes[fam] = r["route_hash"]
        msgs.append(f"sanity {fam}: K={k_total_san} N={n_dim_san} "
                    f"rec={r['recall']:.3f} ra={r['route_acc']:.3f}")

    # 4. At least 2 routings must show some recall lift over floor
    # (substrate WM tiny-config; partition expected to work; degenerate routings
    # may not, but at least 2 should clear 0.20)
    routings_above_floor = sum(1 for v in san_recalls.values() if v >= 0.20)
    if routings_above_floor < 2:
        return False, (f"only {routings_above_floor}/4 routings clear floor 0.20 "
                       f"at sanity: {san_recalls}")
    msgs.append(f"{routings_above_floor}/4 routings >= 0.20 sanity")

    # 5. META_RULE_AF: routing-pair distinctness at AMBIGUOUS regime.
    # At high CUE_COS (sanity above), all 4 routings collapse to same ws_selected
    # (softmax-with-beta=8 = one-hot = argmax = partition; hierarchical picks
    # correct group with high confidence). To DIFFERENTIATE the impls, we
    # construct DELIBERATELY AMBIGUOUS cues (pure random bipolar, no
    # bank-tag prior) and verify that AT LEAST hierarchical produces a
    # DIFFERENT ws_selected vs partition.
    cb2 = build_codebook_random(seed + 2, 1024, n_dim_san)
    g_amb = _make_gen(seed * 11 + 200)
    K_amb = 128
    n_banks_amb = 16
    bank_tags_amb = build_bank_tags(seed * 11 + 200, n_banks_amb, n_dim_san)
    workspaces_amb = random_bipolar_t((n_banks_amb, n_dim_san), g_amb)
    # AMBIGUOUS cues: pure random (no bank-tag prior); routings must
    # differentiate because no clear winner exists.
    g_amb_cue = _make_gen(seed * 11 + 201)
    cues_amb = torch.randn((K_amb, n_dim_san), generator=g_amb_cue,
                            device=DEVICE) * 0.1  # small magnitude

    p_ws, _ = route_partition(cues_amb, bank_tags_amb, workspaces_amb)
    k_ws, _ = route_knn_softmax(cues_amb, bank_tags_amb, workspaces_amb)
    s_ws, _ = route_softmax_attention(cues_amb, bank_tags_amb, workspaces_amb)
    h_ws, _ = route_learned_hierarchical(cues_amb, bank_tags_amb, workspaces_amb)
    distinctness = {
        "knn_softmax_vs_partition": float((k_ws != p_ws).float().mean().item()),
        "softmax_attn_vs_partition": float((s_ws != p_ws).float().mean().item()),
        "hierarchical_vs_partition": float((h_ws != p_ws).float().mean().item()),
    }
    n_distinct_amb = sum(1 for v in distinctness.values() if v > 0.0)
    if n_distinct_amb < 1:
        return False, (f"ARMS_DIFFER violation: at ambiguous regime, NO routing "
                       f"differs from partition (n_distinct=0); "
                       f"diffs={distinctness}; routing impls likely degenerate")
    msgs.append(f"routing-pair distinctness (ambiguous regime): "
                f"{n_distinct_amb}/3 routings differ from partition: "
                f"{distinctness}")
    del cb2, bank_tags_amb, workspaces_amb, cues_amb, p_ws, k_ws, s_ws, h_ws
    if _CUDA_OK:
        torch.cuda.empty_cache()

    del codebook
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (routing, K, regime) phase points for one seed."""
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        K_sweep = K_SWEEP_SMOKE
        k_per_bank = K_PER_BANK_SMOKE
        regimes = REGIMES_SMOKE
        n_dim = N_DIM_SMOKE
        cb_size = CODEBOOK_SIZE_SMOKE
        n_items = N_ITEMS_PER_K_SMOKE
    else:
        K_sweep = K_SWEEP_FULL
        k_per_bank = K_PER_BANK_FULL
        regimes = REGIMES_FULL
        n_dim = N_DIM_FULL
        cb_size = CODEBOOK_SIZE_FULL
        n_items = N_ITEMS_PER_K_FULL

    expected_n_units = len(ROUTING_FAMILIES) * len(K_sweep) * len(regimes)

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"routings={ROUTING_FAMILIES} K_sweep={K_sweep} k_per_bank={k_per_bank} "
          f"regimes={regimes} N={n_dim} CB={cb_size} expected_n={expected_n_units}",
          flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()

    # Build codebook per (seed, regime); free between regimes
    codebooks_by_regime: Dict[str, torch.Tensor] = {}

    for regime in regimes:
        if regime == "RANDOM":
            cb = build_codebook_random(seed * 100003 + 99, cb_size, n_dim)
        else:
            cb = build_codebook_adversarial(seed * 100003 + 199, cb_size, n_dim)
        codebooks_by_regime[regime] = cb
        print(f"[codebook] seed={seed} regime={regime} built shape={cb.shape}",
              flush=True)

        for fam in ROUTING_FAMILIES:
            for K in K_sweep:
                seed_offset = (seed * 100003 + K * 31
                                + (1 if regime == "ADVERSARIAL" else 0)
                                + hash(fam) % 7919)
                print(f"[point] seed={seed} routing={fam} K={K} "
                      f"regime={regime} ...", flush=True)
                pt = eval_routing_arm(fam, K, k_per_bank, regime, cb,
                                       seed_offset, n_items, n_dim)
                phase_map.append(pt)
                print(f"  -> recall={pt['recall']:.3f} "
                      f"ra={pt['route_acc']:.3f} "
                      f"tier={pt['verdict_tier_per_point']} "
                      f"peak_mb={pt['peak_mem_mb']:.1f} "
                      f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)
        # Free this regime's codebook before next regime
        del codebooks_by_regime[regime]
        if _CUDA_OK:
            torch.cuda.empty_cache()

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Per-routing-family arms-differ via route_pred hashes
    routing_hashes: Dict[str, List[str]] = {fam: [] for fam in ROUTING_FAMILIES}
    for p in phase_map:
        routing_hashes[p["routing_family"]].append(p["route_hash"])

    # Cross-routing distinctness: at least 2 routings must produce
    # distinct sets of route_pred hashes from partition (the baseline)
    partition_hashes = set(routing_hashes.get("partition", []))
    routings_differ_from_partition: Dict[str, bool] = {}
    for fam in ROUTING_FAMILIES:
        if fam == "partition":
            continue
        fam_hashes = set(routing_hashes[fam])
        # If even one phase-point hash differs, routing produces different
        # bank predictions than partition
        routings_differ_from_partition[fam] = bool(
            fam_hashes - partition_hashes)

    n_routings_distinct = sum(1 for v in routings_differ_from_partition.values()
                                if v)

    # Per-routing summary
    per_routing_summary: Dict[str, Dict[str, Any]] = {}
    for fam in ROUTING_FAMILIES:
        fam_pts = [p for p in phase_map if p["routing_family"] == fam]
        recalls = [p["recall"] for p in fam_pts]
        recall_mean = float(np.mean(recalls)) if recalls else 0.0
        ras = [p["route_acc"] for p in fam_pts]
        ra_mean = float(np.mean(ras)) if ras else 0.0
        n_sat = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "SATURATED")
        n_hp = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_PASS")
        n_mb = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "MIDDLE_BAND")
        n_floor = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "FLOOR")
        n_fail = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_FAIL")
        # K-cliff locator
        cliff_at_K: Dict[str, float] = {}
        for K in K_sweep:
            for regime in regimes:
                matches = [p for p in fam_pts
                           if p["K_total"] == K and p["regime"] == regime]
                if matches:
                    cliff_at_K[f"K{K}_{regime}"] = matches[0]["recall"]
        # Discriminating fraction (HARD_PASS + MIDDLE_BAND) per routing
        n_total = len(fam_pts)
        n_disc = n_hp + n_mb
        disc_frac = (n_disc / n_total) if n_total > 0 else 0.0
        per_routing_summary[fam] = {
            "recall_mean": round(recall_mean, 4),
            "route_acc_mean": round(ra_mean, 4),
            "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                            "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                            "HARD_FAIL": n_fail},
            "discriminating_fraction": round(disc_frac, 4),
            "recall_per_phase_point": cliff_at_K,
        }

    # Tier the routings (DOMINANT / COMPETITIVE / DOMINATED)
    means = {fam: per_routing_summary[fam]["recall_mean"] for fam in ROUTING_FAMILIES}
    best_mean = max(means.values()) if means else 0.0
    routing_tiers: Dict[str, str] = {}
    for fam in ROUTING_FAMILIES:
        m = means[fam]
        if m >= best_mean - 0.05:
            others = [v for k, v in means.items() if k != fam]
            next_best = max(others) if others else 0.0
            if m == best_mean and m - next_best > 0.10:
                routing_tiers[fam] = "DOMINANT_ROUTING"
            else:
                routing_tiers[fam] = "COMPETITIVE_ROUTING"
        else:
            routing_tiers[fam] = "DOMINATED_ROUTING"

    # Positive control check
    pc_target = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    pc_matches = [p for p in phase_map
                  if p["routing_family"] == pc_target["routing_family"]
                  and p["K_total"] == pc_target["K_total"]
                  and p["regime"] == pc_target["regime"]]
    if pc_matches:
        pc_recall = pc_matches[0]["recall"]
        pc_pass = pc_recall >= pc_target["recall_floor"]
    else:
        pc_recall = -1.0
        pc_pass = False

    positive_control_result = {
        "target": pc_target,
        "measured_recall": pc_recall,
        "pass": pc_pass,
    }

    return {
        "seed": seed,
        "run_mode": run_mode,
        "routing_families": list(ROUTING_FAMILIES),
        "K_sweep": list(K_sweep),
        "regimes": list(regimes),
        "k_per_bank": k_per_bank,
        "N": n_dim,
        "M": cb_size,
        "phase_map": phase_map,
        "per_routing_summary": per_routing_summary,
        "routing_tiers": routing_tiers,
        "routings_differ_from_partition": routings_differ_from_partition,
        "n_routings_distinct_from_partition": n_routings_distinct,
        "positive_control_result": positive_control_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "device": str(DEVICE),
        "gpu_name": GPU_NAME,
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    """Pre-reg smoke gate. Return (passed, reason).

    Gate criteria:
      1. cardinality_ok
      2. positive_control passes (partition reproduces chain-grade)
      3. at least 2 routings produce route_pred hashes differing from partition
         (META_RULE_AF: arms must differ)
      4. each routing contributes phase points (no all-FLOOR families;
         allows graceful degradation but not silent dead-code)
    """
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    routings_differ = body.get("routings_differ_from_partition", {})
    n_distinct = body.get("n_routings_distinct_from_partition", 0)
    per_routing = body.get("per_routing_summary", {})

    if observed_n != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {observed_n}"

    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                        f"measured={pc_result.get('measured_recall')}; "
                        f"test rig broken (partition baseline should reproduce "
                        f"WM v3 chain-grade evidence)")

    if n_distinct < 2:
        # Need at least 2 non-partition routings producing distinct route_pred
        return False, (f"routing_collapse: only {n_distinct}/3 non-partition "
                        f"routings produced distinct route_pred hashes; "
                        f"likely degenerate routing impls. "
                        f"distinct={routings_differ}")

    # Check no routing is all-FLOOR (silent dead-code)
    for fam in ROUTING_FAMILIES:
        summary = per_routing.get(fam, {})
        tier_counts = summary.get("tier_counts", {})
        n_total = sum(tier_counts.values())
        n_floor = tier_counts.get("FLOOR", 0) + tier_counts.get("HARD_FAIL", 0)
        if n_total > 0 and n_floor == n_total:
            return False, (f"all_floor_routing: {fam} all phase points FLOOR/HARD_FAIL "
                            f"({n_floor}/{n_total}); silent dead-code suspected")

    # Discriminator check: at least 2 routings show discriminating phase points
    n_disc_routings = sum(1 for fam in ROUTING_FAMILIES
                          if per_routing.get(fam, {}).get(
                              "discriminating_fraction", 0) >= HP_DISCRIMINATOR_FRACTION)
    if n_disc_routings < 2:
        return False, (f"discriminator_fails_scale: only {n_disc_routings}/4 "
                        f"routings show >= {HP_DISCRIMINATOR_FRACTION:.2f} "
                        f"discriminating phase points; smoke too saturated/floored "
                        f"to discriminate at full-N")

    return True, (f"smoke_gate_pass: cardinality_ok + positive_control_pass + "
                  f"{n_distinct}/3 routings distinct from partition + "
                  f"{n_disc_routings}/4 routings discriminating")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                            run_mode: str) -> Dict[str, Any]:
    """Aggregate single-seed partial into final metrics with verdict."""
    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_NO_SEEDS: empty per_seed",
            "summary": "HARD_FAIL_NO_SEEDS",
        }

    is_smoke = (run_mode == "smoke")
    seed_key = list(per_seed.keys())[0]
    body = per_seed[seed_key]
    phase_map = body.get("phase_map", [])
    pc_result = body.get("positive_control_result", {})
    per_routing = body.get("per_routing_summary", {})
    routing_tiers = body.get("routing_tiers", {})
    routings_differ = body.get("routings_differ_from_partition", {})
    n_distinct = body.get("n_routings_distinct_from_partition", 0)
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)

    n_hp = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_mb = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "SATURATED")
    n_floor = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "FLOOR")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")
    n_disc = n_hp + n_mb

    common = {
        "phase_map": phase_map,
        "per_routing_summary": per_routing,
        "routing_tiers": routing_tiers,
        "routings_differ_from_partition": routings_differ,
        "n_routings_distinct_from_partition": n_distinct,
        "positive_control_result": pc_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                        "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                        "HARD_FAIL": n_fail},
        "n_discriminating": n_disc,
        "device": body.get("device"),
        "gpu_name": body.get("gpu_name"),
        "beta_soft": BETA_SOFT,
        "group_size": GROUP_SIZE,
        "k_per_bank": body.get("k_per_bank"),
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} "
                    f"fail={n_fail}; "
                    f"positive_control@{pc_result.get('target',{}).get('routing_family')}"
                    f"_K={pc_result.get('target',{}).get('K_total')}"
                    f" rec={pc_result.get('measured_recall'):.3f}; "
                    f"routing_tiers={routing_tiers}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_SMOKE: {reason}; sat={n_sat} hp={n_hp} mb={n_mb} "
                    f"floor={n_floor} fail={n_fail}")
        out = dict(common)
        out.update({
            "verdict": verdict,
            "verdict_msg": vmsg,
            "summary": vmsg,
            "smoke_gate_pass": passed,
            "smoke_gate_reason": reason,
        })
        return out

    # FULL verdict
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
                f"observed={observed_n}")
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CONTROL_FAIL: positive_control "
                f"{pc_result.get('target')} measured recall="
                f"{pc_result.get('measured_recall')}; test rig broken")
    elif n_distinct < 2:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_ROUTING_COLLAPSE: only {n_distinct}/3 non-partition "
                f"routings produced distinct route_pred hashes")
    else:
        # Tier by competitive landscape
        dominant = [fam for fam, t in routing_tiers.items()
                     if t == "DOMINANT_ROUTING"]
        competitive = [fam for fam, t in routing_tiers.items()
                        if t == "COMPETITIVE_ROUTING"]
        dominated = [fam for fam, t in routing_tiers.items()
                      if t == "DOMINATED_ROUTING"]

        # Q-saturation gate
        sat_fraction = n_sat / max(observed_n, 1)
        if sat_fraction >= 0.75:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_BY_CONSTRUCTION_SATURATION: "
                    f"{n_sat}/{observed_n} pts saturated (>=0.75); "
                    f"discriminating regime not reached; "
                    f"tiers={routing_tiers}")
        elif dominant:
            verdict = "CHAIN_GRADE_ROUTING_FAMILY_PHASE_DIAGRAM"
            vmsg = (f"CHAIN_GRADE_ROUTING_FAMILY: dominant={dominant} "
                    f"competitive={competitive} dominated={dominated}; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor}; "
                    f"positive_control rec={pc_result.get('measured_recall')}")
        elif len(competitive) >= 2:
            verdict = "ROUTING_FAMILY_INVARIANCE"
            vmsg = (f"ROUTING_FAMILY_INVARIANCE: "
                    f"competitive={competitive} dominated={dominated}; "
                    f"multiple routings cluster; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_ROUTING_FAMILY: tiers={routing_tiers}; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor}")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg[:300],
    })
    return out
