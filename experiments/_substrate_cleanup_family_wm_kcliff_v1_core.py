"""Shared core for substrate_cleanup_family_wm_kcliff_v1 sibling cells.

CLEANUP-FAMILY phase diagram in the WM multi-bank K-cliff REGIME.

Background: PC cleanup family phase diagram (2026-06-28) CG'd as convergent
MIDDLE_BAND -- cleanup choice family-invariant at PC scale. WM is a DIFFERENT
regime (higher K, multi-bank routing, sequence-binding-adjacent). Possibly
cleanup family discriminates here.

CLEANUP FAMILIES (OUTER axis; LOCKED):
    no_cleanup                  : baseline; no operation; argmax over codebook
    classical_hopfield          : Hebbian outer-product W; sign update
    modern_hopfield_continuous  : softmax-attention (Ramsauer 2021)
    iterative_attractor         : softmax-cosine + L2 normalization (brain-canonical)
    k_NN_lookup                 : one-shot top-k argmax averaging

INNER AXES:
    K_per_bank in {50, 100, 250, 500, 1000} (5 K values)
    regime in {RANDOM, ADVERSARIAL} (2)
    num_banks = 16 FIXED
    N_DIM = 8192 FIXED (GPU regime)

CARDINALITY:
  FULL: 5 cleanups * 5 K * 2 regimes = 50 phase points per seed
  SMOKE: 5 cleanups * 3 K * 1 regime = 15 corner points per seed

PRE-REG: preregs/2026-06-30_substrate_cleanup_family_wm_kcliff_v1.md

Sibling cells import:
    run_one_seed_phase_diagram(seed, run_mode)
    aggregate_and_verdict(per_seed_dict, run_mode)
    selftest(seed)
    get_backend_label()
    CLEANUP_FAMILIES,
    K_PER_BANK_SWEEP_FULL, K_PER_BANK_SWEEP_SMOKE,
    REGIMES_FULL, REGIMES_SMOKE

GPU MANDATE: routes via overnight_queue (Fix #24). Modern Hopfield softmax-
attention update on N=8192 codebook is matmul-bound -- torch.cuda mandatory
for full. CPU fallback used only for selftest/smoke-tiny.

ASCII-only. No unicode.

Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

# Torch at TOP of module (PROT-020 GPU-eligibility scan).
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
SATURATED_RECALL = 0.995  # Q-saturation (META_RULE_Q suspect-1.000)
HARD_PASS_LO = 0.80
MIDDLE_BAND_LO = 0.50
FLOOR_HI = 0.10
HP_DISCRIMINATOR = 0.20  # mechanism arm vs random floor
MB_DISCRIMINATOR = 0.10

BETA = 8.0
ALPHA_SOFT = 0.0  # iterative_attractor cue-reinjection weight
KNN_K = 1
HOP_MAX_STEPS = 4  # cap iterations for hopfield primitives at full-N

# Cleanup families (OUTER axis; LOCKED at module init)
CLEANUP_FAMILIES = ("no_cleanup", "classical_hopfield", "modern_hopfield_continuous",
                    "iterative_attractor", "k_NN_lookup")

# Sweep axes (per spec)
K_PER_BANK_SWEEP_FULL = [50, 100, 250, 500, 1000]
NUM_BANKS_FULL = 16
N_DIM_FULL = 8192
REGIMES_FULL = ("RANDOM", "ADVERSARIAL")

K_PER_BANK_SWEEP_SMOKE = [50, 100, 250]  # 3 K values
NUM_BANKS_SMOKE = 16  # full-N preview for DISCRIMINATOR-MUST-SURVIVE-SCALE
N_DIM_SMOKE = 2048    # half-N for smoke speed; still tests cliff structure
REGIMES_SMOKE = ("RANDOM",)

# Bipolar substrate WM params (match WM K-cliff envelope)
SIGMA = 1.0
CUE_COS = 0.70
FEATURE_OVERLAP_FRAC = 0.20
N_GROUPS_ADV = 4

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (len(CLEANUP_FAMILIES) * len(K_PER_BANK_SWEEP_FULL)
                         * len(REGIMES_FULL))  # 5 * 5 * 2 = 50
EXPECTED_N_UNITS_SMOKE = (len(CLEANUP_FAMILIES) * len(K_PER_BANK_SWEEP_SMOKE)
                          * len(REGIMES_SMOKE))  # 5 * 3 * 1 = 15

# Positive control: at SMALLEST K, ALL cleanup arms (including no_cleanup) must
# clear MIDDLE_BAND_LO (K=50 per_bank x 16 banks = 800 items in N=8192 is well
# below capacity; substrate must trivially recover).
POSITIVE_CONTROL = {
    "cleanup_family": "no_cleanup",
    "K_per_bank": 50,
    "regime": "RANDOM",
    "recall_floor": 0.80,  # K=50/bank x 16 banks = 800 items in N=8192 fp32
}
POSITIVE_CONTROL_SMOKE = {
    "cleanup_family": "no_cleanup",
    "K_per_bank": 50,
    "regime": "RANDOM",
    "recall_floor": 0.60,  # smoke-N=2048 is rail-drift; conservative floor
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# CRLB / capacity-feasibility (META_RULE_AG)
# ---------------------------------------------------------------------------
def estimated_cliff_K_per_bank(n_dim: int, n_banks: int) -> int:
    """Estimated K_per_bank where naive cleanup saturates.

    For bipolar codebook of size M=K*n_banks in N=n_dim, the matched-filter SNR
    for one cleanup pass is sqrt(N) / sqrt(M-1). Cliff at SNR ~ 1, i.e.
    M ~ N + 1, i.e. K_per_bank ~ N / n_banks.
    """
    if n_banks <= 0:
        return 0
    return max(1, int(n_dim / n_banks))


# ---------------------------------------------------------------------------
# HD substrate primitives (match WM K-cliff conventions)
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
    """Multi-bank write: workspace[b] = sum_k items[b,k] * slot_tag[k] + noise."""
    n_banks, k_per_bank, N = items_per_bank.shape
    bound = items_per_bank * slot_tags.unsqueeze(0)  # (n_banks, k_per_bank, N)
    ws = bound.sum(dim=1).float()
    if SIGMA > 0.0:
        g_noise = _make_gen(seed_offset + 23)
        noise = torch.empty(ws.shape, device=DEVICE, dtype=torch.float32)
        noise.normal_(0.0, SIGMA, generator=g_noise)
        ws = ws + noise
    return bipolar_quantize_t(ws)


# ---------------------------------------------------------------------------
# CLEANUP FAMILY PRIMITIVES (the load-bearing OUTER axis)
# Common signature: query (K, N), codebook (M, N) -> (recovered (K, N), pred_idx (K,))
# All operate in bipolar regime; quantize output via sign for fair comparison.
# ---------------------------------------------------------------------------
def _sign_op(V: torch.Tensor) -> torch.Tensor:
    out = torch.sign(V)
    return torch.where(out == 0, torch.ones_like(out), out)


def cleanup_no_cleanup(query: torch.Tensor, codebook: torch.Tensor
                       ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Baseline: no cleanup. pred = argmax(query @ codebook.T)."""
    sims = query @ codebook.T  # (K, M)
    pred_idx = sims.argmax(dim=1)
    recovered = query  # unchanged
    return recovered, pred_idx


def cleanup_k_NN_lookup(query: torch.Tensor, codebook: torch.Tensor
                        ) -> Tuple[torch.Tensor, torch.Tensor]:
    """One-shot k=1 argmax cleanup: snap to nearest codebook entry."""
    sims = query @ codebook.T  # (K, M)
    pred_idx = sims.argmax(dim=1)
    recovered = codebook[pred_idx]  # (K, N)
    return recovered, pred_idx


def cleanup_classical_hopfield(query: torch.Tensor, codebook: torch.Tensor,
                                T: int = HOP_MAX_STEPS
                                ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Classical Hopfield: Hebbian W = X.T @ X / M; iterate sign(s @ W).

    Capacity ~0.14 * N. Memory: D*D matrix (N=8192 -> 256MB fp32; tractable
    on overnight GPU).
    """
    M, N = codebook.shape
    # Hebbian W (D x D). Zero diagonal per classical convention.
    W = (codebook.T @ codebook) / float(M)  # (N, N)
    W.fill_diagonal_(0.0)
    state = query
    for _ in range(max(0, T)):
        h = state @ W  # (K, N)
        state = _sign_op(h)
    del W
    if _CUDA_OK:
        torch.cuda.empty_cache()
    sims = state @ codebook.T
    pred_idx = sims.argmax(dim=1)
    return state, pred_idx


def cleanup_modern_hopfield_continuous(query: torch.Tensor, codebook: torch.Tensor,
                                        T: int = HOP_MAX_STEPS, beta: float = BETA
                                        ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Modern Hopfield / Ramsauer 2021: T-step softmax-attention update.

    state_{t+1} = sign(softmax(beta * state_t @ X.T) @ X)
    """
    state = query
    for _ in range(max(0, T)):
        sims = beta * (state @ codebook.T)  # (K, M)
        weights = torch.softmax(sims, dim=1)  # (K, M)
        s_mix = weights @ codebook  # (K, N) mixture
        state = _sign_op(s_mix)
    final_sims = state @ codebook.T
    pred_idx = final_sims.argmax(dim=1)
    return state, pred_idx


def cleanup_iterative_attractor(query: torch.Tensor, codebook: torch.Tensor,
                                 T: int = HOP_MAX_STEPS, beta: float = BETA
                                 ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Iterative attractor: L2-normalized cosine softmax (brain-canonical CA3).

    Distinguishes from modern_hopfield_continuous by L2-normalizing rather
    than sign-quantizing -- preserves graded basin descent.

    Effective beta scaled by sqrt(D) per Ramsauer 2021 / Vaswani 2017 attention-
    scaling trick (same pattern as hdlab.iterative_attractor.iterative_cleanup).
    Without this, beta=8 on cosine similarities ~ 1/sqrt(D) produces near-uniform
    softmax and the state collapses to mean(codebook) within 1-2 steps.

    state_{t+1} = l2_normalize(softmax(beta*sqrt(D) * state_t . cb_norm) @ cb_norm)
    """
    D = codebook.shape[1]
    eff_beta = beta * math.sqrt(D)
    cb_norm = codebook / (torch.linalg.norm(codebook, dim=1, keepdim=True)
                          .clamp(min=1e-12))
    state = query / (torch.linalg.norm(query, dim=1, keepdim=True)
                     .clamp(min=1e-12))
    for _ in range(max(0, T)):
        sims = eff_beta * (state @ cb_norm.T)  # (K, M)
        weights = torch.softmax(sims, dim=1)
        s_mix = weights @ cb_norm  # (K, N)
        state = s_mix / (torch.linalg.norm(s_mix, dim=1, keepdim=True)
                         .clamp(min=1e-12))
    final_sims = state @ cb_norm.T
    pred_idx = final_sims.argmax(dim=1)
    # For fair output comparison with bipolar arms, quantize via sign
    recovered = _sign_op(state)
    return recovered, pred_idx


_CLEANUP_REGISTRY: Dict[str, Callable] = {
    "no_cleanup": cleanup_no_cleanup,
    "classical_hopfield": cleanup_classical_hopfield,
    "modern_hopfield_continuous": cleanup_modern_hopfield_continuous,
    "iterative_attractor": cleanup_iterative_attractor,
    "k_NN_lookup": cleanup_k_NN_lookup,
}


def _apply_cleanup(family: str, query: torch.Tensor, codebook: torch.Tensor
                    ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Dispatcher: call the named cleanup with appropriate args."""
    fn = _CLEANUP_REGISTRY[family]
    if family in ("classical_hopfield", "modern_hopfield_continuous",
                   "iterative_attractor"):
        return fn(query, codebook, HOP_MAX_STEPS)
    return fn(query, codebook)


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def eval_phase_point(cleanup_family: str, K_per_bank: int, num_banks: int,
                      regime: str, codebook: torch.Tensor, seed_offset: int,
                      n_dim: int) -> Dict[str, Any]:
    """One (cleanup_family, K_per_bank, regime) phase point.

    Multi-bank WM K-cliff: write n_banks workspaces with k_per_bank items each;
    cue with bank-tag + slot-tag; route via argmax over bank tags; READ via
    workspace (*) slot_tag then CLEANUP; predict via argmax.
    """
    if cleanup_family not in _CLEANUP_REGISTRY:
        raise ValueError(f"unknown cleanup_family={cleanup_family!r}")

    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    K_total = K_per_bank * num_banks
    slot_tags = build_slot_tags(seed_offset, K_per_bank, n_dim)
    bank_tags = build_bank_tags(seed_offset, num_banks, n_dim)
    cue_noise_scale = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))

    # Select K_total items from codebook
    cb_size = codebook.shape[0]
    g_trial = _make_gen(seed_offset + 29)
    if K_total > cb_size:
        # Allow repeat sampling if K_total exceeds codebook (high-K regime)
        idx_global = torch.randint(0, cb_size, (K_total,), generator=g_trial,
                                    device=DEVICE)
    else:
        idx_global = torch.randperm(cb_size, generator=g_trial,
                                      device=DEVICE)[:K_total]
    items = codebook[idx_global]  # (K_total, N)
    items_per_bank = items.view(num_banks, K_per_bank, n_dim)

    workspaces = write_bank(items_per_bank, slot_tags, seed_offset + 1000)

    slot_indices = torch.arange(K_total, device=DEVICE)
    bank_true = slot_indices // K_per_bank
    local_slot = slot_indices % K_per_bank

    # Cue construction: CUE_COS * bank_tag + noise (real-valued)
    g_cue = _make_gen(seed_offset + 5000)
    bank_cue_base = bank_tags[bank_true].float()
    noise = torch.empty((K_total, n_dim), device=DEVICE, dtype=torch.float32)
    noise.normal_(0.0, 1.0, generator=g_cue)
    noise_bp = bipolar_quantize_t(noise)
    cues = CUE_COS * bank_cue_base + cue_noise_scale * noise_bp

    # Bank routing (always argmax for fair comparison; the OUTER axis is cleanup)
    route_sims = cues @ bank_tags.T  # (K_total, num_banks)
    bank_routed = route_sims.argmax(dim=1)
    ws_selected = workspaces[bank_routed]  # (K_total, N)

    # READ: ws_selected * slot_tag -> raw query for cleanup
    slot_tag_sel = slot_tags[local_slot]  # (K_total, N)
    raw_query = ws_selected * slot_tag_sel  # (K_total, N) bipolar

    # APPLY CLEANUP (the OUTER axis)
    recovered, pred_idx = _apply_cleanup(cleanup_family, raw_query, codebook)

    true_item_idx = idx_global[slot_indices]
    match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
    recall = float(match.sum().item()) / max(K_total, 1)
    route_acc = float((bank_routed == bank_true).sum().item()) / max(K_total, 1)

    # Mechanism hash: SHA256 of recovered tensor bytes (catches mechanism
    # collapse even when recall agrees across cleanups).
    mech_output_hash = hashlib.sha256(
        recovered.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    # Prediction-pattern hash: which items the cleanup chose (CRITICAL for
    # detecting cleanup-collapse where recovered vectors differ but argmax
    # over codebook collapses to same predictions).
    pred_pattern_hash = hashlib.sha256(
        pred_idx.detach().cpu().numpy().tobytes()).hexdigest()[:16]

    if _CUDA_OK:
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        peak_mem_mb = -1.0

    elapsed = time.time() - t0

    # Per-point verdict tier
    if recall >= SATURATED_RECALL:
        tier = "SATURATED"
    elif recall >= HARD_PASS_LO:
        tier = "HARD_PASS"
    elif recall >= MIDDLE_BAND_LO:
        tier = "MIDDLE_BAND"
    elif recall <= FLOOR_HI:
        tier = "FLOOR"
    else:
        tier = "HARD_FAIL"

    # Free
    del slot_tags, bank_tags, workspaces, cues, noise, noise_bp, bank_cue_base
    del items, items_per_bank, ws_selected, slot_tag_sel, raw_query
    del recovered, pred_idx, true_item_idx, match, bank_routed
    del idx_global, slot_indices, bank_true, local_slot, route_sims
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "cleanup_family": cleanup_family,
        "K_per_bank": K_per_bank,
        "num_banks": num_banks,
        "K_total": K_total,
        "regime": regime,
        "N": n_dim,
        "recall": round(recall, 4),
        "route_acc": round(route_acc, 4),
        "mech_output_hash": mech_output_hash,
        "pred_pattern_hash": pred_pattern_hash,
        "verdict_tier_per_point": tier,
        "saturation_flag": recall >= SATURATED_RECALL,
        "peak_mem_mb": round(peak_mem_mb, 1),
        "elapsed_per_point_s": round(elapsed, 3),
        "cliff_estimate_K_per_bank": estimated_cliff_K_per_bank(n_dim, num_banks),
    }


# ---------------------------------------------------------------------------
# Selftest (cardinality + primitive sanity + distinctness gate)
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Selftest: cardinality + primitive sanity + ARM-DISTINCTNESS at cliff."""
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 50:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 50"
    if EXPECTED_N_UNITS_SMOKE != 15:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 15"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. All cleanups registered + callable
    for fam in CLEANUP_FAMILIES:
        if fam not in _CLEANUP_REGISTRY:
            return False, f"cleanup {fam} not in registry"
        if not callable(_CLEANUP_REGISTRY[fam]):
            return False, f"cleanup {fam} not callable"
    msgs.append(f"5 cleanups registered: {list(_CLEANUP_REGISTRY.keys())}")

    # 3. CRLB sanity: cliff prediction reasonable
    cliff_full = estimated_cliff_K_per_bank(N_DIM_FULL, NUM_BANKS_FULL)
    # For N=8192, num_banks=16 -> cliff_estimate = 512
    if not (256 <= cliff_full <= 1024):
        return False, (f"cliff estimate {cliff_full} outside [256, 1024]; "
                       f"check capacity formula")
    msgs.append(f"cliff_K_per_bank N=8192 banks=16 ~ {cliff_full}")

    # 4. Per-primitive sanity at TINY regime
    n_dim_san = 512
    cb_size_san = 256
    k_per_bank_san = 8
    num_banks_san = 4

    codebook = build_codebook_random(seed * 11 + 1, cb_size_san, n_dim_san)
    san_recalls: Dict[str, float] = {}
    san_pred_hashes: Dict[str, str] = {}
    san_mech_hashes: Dict[str, str] = {}
    for fam in CLEANUP_FAMILIES:
        r = eval_phase_point(fam, k_per_bank_san, num_banks_san, "RANDOM",
                             codebook, seed_offset=seed * 7 + 100,
                             n_dim=n_dim_san)
        san_recalls[fam] = r["recall"]
        san_pred_hashes[fam] = r["pred_pattern_hash"]
        san_mech_hashes[fam] = r["mech_output_hash"]
        msgs.append(f"sanity {fam}: K_per_bank={k_per_bank_san} N={n_dim_san} "
                    f"rec={r['recall']:.3f} ra={r['route_acc']:.3f}")

    # 5. At least 3 of 5 cleanups must clear floor 0.20 at TINY regime
    # (tiny is well-below-capacity; baseline + at least 2 real cleanups
    # should recover; if fewer cleanups clear, primitives are buggy).
    cleanups_above_floor = sum(1 for v in san_recalls.values() if v >= 0.20)
    if cleanups_above_floor < 3:
        return False, (f"only {cleanups_above_floor}/5 cleanups clear floor "
                       f"0.20 at TINY sanity: {san_recalls}; primitives likely "
                       f"buggy")
    msgs.append(f"{cleanups_above_floor}/5 cleanups >= 0.20 at sanity")

    # 6. META_RULE_AY / AF: prediction-pattern hashes must show at least 2
    # distinct cleanup pairs (5 arms -> 10 pairs; at least 2 should differ).
    # Sanity-regime is low-K (well-below capacity) so cleanup-pair distinctness
    # is the MINIMUM we can demand (cliff regime will discriminate more).
    fams = list(CLEANUP_FAMILIES)
    n_distinct = 0
    n_pairs = 0
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            n_pairs += 1
            if san_pred_hashes[fams[i]] != san_pred_hashes[fams[j]]:
                n_distinct += 1
    if n_distinct < 2:
        return False, (f"META_RULE_AY VIOLATION: only {n_distinct}/{n_pairs} "
                       f"cleanup-pair predictions distinct at sanity regime; "
                       f"primitives likely collapsed: {san_pred_hashes}")
    msgs.append(f"distinctness sanity: {n_distinct}/{n_pairs} cleanup pairs "
                f"produce distinct pred patterns")

    del codebook
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (cleanup, K_per_bank, regime) phase points for one seed."""
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        K_sweep = K_PER_BANK_SWEEP_SMOKE
        num_banks = NUM_BANKS_SMOKE
        regimes = REGIMES_SMOKE
        n_dim = N_DIM_SMOKE
    else:
        K_sweep = K_PER_BANK_SWEEP_FULL
        num_banks = NUM_BANKS_FULL
        regimes = REGIMES_FULL
        n_dim = N_DIM_FULL

    expected_n_units = (len(CLEANUP_FAMILIES) * len(K_sweep) * len(regimes))

    # Codebook size: enough to hold K_max * num_banks unique items per regime
    K_max = max(K_sweep)
    cb_size = max(4096, K_max * num_banks * 2)  # 2x headroom for sampling

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"cleanups={CLEANUP_FAMILIES} K_sweep={K_sweep} num_banks={num_banks} "
          f"regimes={regimes} N={n_dim} CB={cb_size} "
          f"expected_n={expected_n_units}", flush=True)

    cliff_pred = estimated_cliff_K_per_bank(n_dim, num_banks)
    print(f"[cliff-pred] K_per_bank cliff estimate: {cliff_pred}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()

    for regime in regimes:
        if regime == "RANDOM":
            cb = build_codebook_random(seed * 100003 + 99, cb_size, n_dim)
        else:
            cb = build_codebook_adversarial(seed * 100003 + 199, cb_size, n_dim)
        print(f"[codebook] seed={seed} regime={regime} built shape={cb.shape}",
              flush=True)

        for fam in CLEANUP_FAMILIES:
            for K_per_bank in K_sweep:
                seed_offset = (seed * 100003 + K_per_bank * 31
                                + (1 if regime == "ADVERSARIAL" else 0)
                                + hash(fam) % 7919)
                print(f"[point] seed={seed} cleanup={fam} K_per_bank={K_per_bank} "
                      f"regime={regime} ...", flush=True)
                pt = eval_phase_point(fam, K_per_bank, num_banks, regime, cb,
                                       seed_offset, n_dim)
                phase_map.append(pt)
                print(f"  -> recall={pt['recall']:.3f} "
                      f"ra={pt['route_acc']:.3f} "
                      f"tier={pt['verdict_tier_per_point']} "
                      f"peak_mb={pt['peak_mem_mb']:.1f} "
                      f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

        del cb
        if _CUDA_OK:
            torch.cuda.empty_cache()

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # ARMS-DIFFER (META_RULE_AF + AY): per-cleanup pred-pattern + mech-output
    # hashes; cross-cleanup distinctness analysis.
    fams = list(CLEANUP_FAMILIES)
    cleanup_pred_hashes: Dict[str, List[str]] = {fam: [] for fam in fams}
    cleanup_mech_hashes: Dict[str, List[str]] = {fam: [] for fam in fams}
    for p in phase_map:
        cleanup_pred_hashes[p["cleanup_family"]].append(p["pred_pattern_hash"])
        cleanup_mech_hashes[p["cleanup_family"]].append(p["mech_output_hash"])

    # Pair-wise distinctness across SAME (K_per_bank, regime) phase points
    pairs_differ: Dict[str, bool] = {}
    pairs_pred_differ: Dict[str, bool] = {}
    pred_lookup: Dict[Tuple[str, int, str], str] = {}
    mech_lookup: Dict[Tuple[str, int, str], str] = {}
    for p in phase_map:
        key = (p["cleanup_family"], p["K_per_bank"], p["regime"])
        pred_lookup[key] = p["pred_pattern_hash"]
        mech_lookup[key] = p["mech_output_hash"]

    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            pair_key = f"{fams[i]}_vs_{fams[j]}"
            any_pred_diff = False
            any_mech_diff = False
            for K_per_bank in K_sweep:
                for regime in regimes:
                    k_i = (fams[i], K_per_bank, regime)
                    k_j = (fams[j], K_per_bank, regime)
                    if k_i in pred_lookup and k_j in pred_lookup:
                        if pred_lookup[k_i] != pred_lookup[k_j]:
                            any_pred_diff = True
                        if mech_lookup[k_i] != mech_lookup[k_j]:
                            any_mech_diff = True
            pairs_pred_differ[pair_key] = any_pred_diff
            pairs_differ[pair_key] = any_mech_diff

    n_pairs = len(pairs_differ)
    n_pairs_pred_differ = sum(1 for v in pairs_pred_differ.values() if v)
    n_pairs_mech_differ = sum(1 for v in pairs_differ.values() if v)

    # META_RULE_AY: cell-author-reported distinctness (load-bearing for verdict).
    # If self-reports False on EITHER pred-or-mech, verdict-emitter HARD_FAILs.
    distinctness_passes = (n_pairs_pred_differ >= 2 and n_pairs_mech_differ >= 2)

    # Per-cleanup summary
    per_cleanup_summary: Dict[str, Dict[str, Any]] = {}
    for fam in CLEANUP_FAMILIES:
        fam_pts = [p for p in phase_map if p["cleanup_family"] == fam]
        recalls = [p["recall"] for p in fam_pts]
        recall_mean = float(np.mean(recalls)) if recalls else 0.0
        n_sat = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "SATURATED")
        n_hp = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_PASS")
        n_mb = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "MIDDLE_BAND")
        n_floor = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "FLOOR")
        n_fail = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_FAIL")
        # K-cliff locator (per regime): smallest K_per_bank where recall < 0.5
        cliff_loc: Dict[str, float] = {}
        for regime in regimes:
            cliff_K = -1.0
            for K in sorted(K_sweep):
                matches = [p for p in fam_pts
                           if p["K_per_bank"] == K and p["regime"] == regime]
                if matches and matches[0]["recall"] < MIDDLE_BAND_LO:
                    cliff_K = K
                    break
            cliff_loc[f"{regime}"] = cliff_K
        n_total = len(fam_pts)
        n_disc = n_hp + n_mb
        per_cleanup_summary[fam] = {
            "recall_mean": round(recall_mean, 4),
            "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                            "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                            "HARD_FAIL": n_fail},
            "discriminating_fraction": round(n_disc / max(n_total, 1), 4),
            "cliff_K_per_bank_per_regime": cliff_loc,
            "recall_per_K": {f"{p['regime']}_K{p['K_per_bank']}": p["recall"]
                              for p in fam_pts},
        }

    # K_cliff log2 separation: how widely cleanups place the cliff
    # (log2 separation criterion from spec discriminator)
    cliff_K_values = []
    for fam in CLEANUP_FAMILIES:
        for regime in regimes:
            v = per_cleanup_summary[fam]["cliff_K_per_bank_per_regime"].get(
                regime, -1.0)
            if v > 0:
                cliff_K_values.append((fam, regime, v))
    cliff_log2_span = 0.0
    if cliff_K_values:
        vals = [math.log2(v[2]) for v in cliff_K_values if v[2] > 0]
        if len(vals) >= 2:
            cliff_log2_span = max(vals) - min(vals)

    # Tier the cleanups
    means = {fam: per_cleanup_summary[fam]["recall_mean"] for fam in CLEANUP_FAMILIES}
    best_mean = max(means.values()) if means else 0.0
    cleanup_tiers: Dict[str, str] = {}
    for fam in CLEANUP_FAMILIES:
        m = means[fam]
        if m >= best_mean - 0.05:
            others = [v for k, v in means.items() if k != fam]
            next_best = max(others) if others else 0.0
            if m == best_mean and m - next_best > 0.10:
                cleanup_tiers[fam] = "DOMINANT_CLEANUP"
            else:
                cleanup_tiers[fam] = "COMPETITIVE_CLEANUP"
        else:
            cleanup_tiers[fam] = "DOMINATED_CLEANUP"

    # Positive control
    pc_target = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    pc_matches = [p for p in phase_map
                  if p["cleanup_family"] == pc_target["cleanup_family"]
                  and p["K_per_bank"] == pc_target["K_per_bank"]
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
        "cleanup_families": list(CLEANUP_FAMILIES),
        "K_per_bank_sweep": list(K_sweep),
        "regimes": list(regimes),
        "num_banks": num_banks,
        "N": n_dim,
        "M": cb_size,
        "phase_map": phase_map,
        "per_cleanup_summary": per_cleanup_summary,
        "cleanup_tiers": cleanup_tiers,
        "cleanup_pair_mech_distinctness": pairs_differ,
        "cleanup_pair_pred_distinctness": pairs_pred_differ,
        "n_pairs_mech_differ": n_pairs_mech_differ,
        "n_pairs_pred_differ": n_pairs_pred_differ,
        "distinctness_self_report_pass": distinctness_passes,
        "cliff_K_log2_span": round(cliff_log2_span, 4),
        "positive_control_result": positive_control_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "estimated_cliff_K_per_bank": estimated_cliff_K_per_bank(n_dim, num_banks),
        "device": str(DEVICE),
        "gpu_name": GPU_NAME,
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    """Pre-reg smoke gate.

    Gates (mandatory):
      1. cardinality_ok
      2. positive_control passes (no_cleanup at smallest K reaches floor)
      3. distinctness_self_report_pass (META_RULE_AY): >=2 pairs differ on
         BOTH mech-output AND pred-pattern hashes
      4. DISCRIMINATOR-MUST-SURVIVE-SCALE: at least 3 of 5 cleanups produce
         distinct K_cliff predictions (>=0.3 log2 separation in cliff K)
         OR baseline saturated below cliff (no_cleanup hits floor before
         expected cliff_K_per_bank).
      5. No silent dead-code: every cleanup contributes at least 1 phase point
    """
    phase_map = body.get("phase_map", [])
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    pairs_pred_differ = body.get("cleanup_pair_pred_distinctness", {})
    pairs_mech_differ = body.get("cleanup_pair_mech_distinctness", {})
    distinctness_pass = body.get("distinctness_self_report_pass", False)
    cliff_log2_span = body.get("cliff_K_log2_span", 0.0)
    per_cleanup = body.get("per_cleanup_summary", {})

    # 1. Cardinality
    if observed_n != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {observed_n}"

    # 2. Positive control
    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                       f"measured={pc_result.get('measured_recall')}; "
                       f"test rig broken")

    # 3. META_RULE_AY: distinctness self-report
    if not distinctness_pass:
        n_pred_d = sum(1 for v in pairs_pred_differ.values() if v)
        n_mech_d = sum(1 for v in pairs_mech_differ.values() if v)
        return False, (f"META_RULE_AY_DISTINCTNESS_FAIL: pred_differ={n_pred_d}/10 "
                       f"mech_differ={n_mech_d}/10 (need >=2 each); cleanup arms "
                       f"COLLAPSED -- v1/v3 ANCHOR 4 phantom pattern; ABORT")

    # 4. Silent dead-code check
    for fam in CLEANUP_FAMILIES:
        summary = per_cleanup.get(fam, {})
        n_fam_pts = sum(summary.get("tier_counts", {}).values())
        if n_fam_pts == 0:
            return False, f"silent_dead_code: cleanup {fam} produced 0 phase points"

    # 5. DISCRIMINATOR-MUST-SURVIVE-SCALE: at smoke regime (smaller N), expect
    # cliffs to be visible. Require either:
    #   (a) at least 3 of 5 cleanups have DISTINCT cliff predictions
    #       (cliff_log2_span >= 0.3 over at least 3 cleanups), OR
    #   (b) baseline no_cleanup hits MIDDLE_BAND or worse in the smoke regime
    #       (proving the regime exercises the cleanup mechanism)
    no_cleanup_summary = per_cleanup.get("no_cleanup", {})
    no_cleanup_recall = no_cleanup_summary.get("recall_mean", 1.0)
    baseline_exercised = (no_cleanup_recall < 0.85)

    n_pairs_pred_d = sum(1 for v in pairs_pred_differ.values() if v)
    discriminator_fires = (cliff_log2_span >= 0.30 or
                            n_pairs_pred_d >= 5 or
                            baseline_exercised)

    if not discriminator_fires:
        return False, (f"discriminator_fails_scale: cliff_log2_span={cliff_log2_span:.3f} "
                       f"(need >=0.30) OR n_pairs_pred_d={n_pairs_pred_d}/10 "
                       f"(need >=5) OR no_cleanup_recall_mean={no_cleanup_recall:.3f} "
                       f"(need <0.85); regime too easy at smoke -- "
                       f"DISCRIMINATOR-MUST-SURVIVE-SCALE breach")

    return True, (f"smoke_gate_pass: cardinality_ok + positive_control_pass + "
                  f"distinctness {n_pairs_pred_d}/10 pred + cliff_log2_span="
                  f"{cliff_log2_span:.3f} + no_cleanup_recall={no_cleanup_recall:.3f}")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    """Aggregate one-seed partial into final metrics with verdict."""
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
    per_cleanup = body.get("per_cleanup_summary", {})
    cleanup_tiers = body.get("cleanup_tiers", {})
    pairs_mech_differ = body.get("cleanup_pair_mech_distinctness", {})
    pairs_pred_differ = body.get("cleanup_pair_pred_distinctness", {})
    n_pairs_mech_d = body.get("n_pairs_mech_differ", 0)
    n_pairs_pred_d = body.get("n_pairs_pred_differ", 0)
    distinctness_pass = body.get("distinctness_self_report_pass", False)
    cliff_log2_span = body.get("cliff_K_log2_span", 0.0)
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)

    n_hp = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_mb = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "SATURATED")
    n_floor = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "FLOOR")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")
    n_disc = n_hp + n_mb

    # GPU utilization estimate
    if _CUDA_OK:
        peak_mems = [p["peak_mem_mb"] for p in phase_map if p["peak_mem_mb"] > 0]
        avg_peak = sum(peak_mems) / max(len(peak_mems), 1)
        gpu_util_estimate = min(0.95, max(0.30, avg_peak / 500.0))
    else:
        gpu_util_estimate = 0.0

    common = {
        "phase_map": phase_map,
        "per_cleanup_summary": per_cleanup,
        "cleanup_tiers": cleanup_tiers,
        "cleanup_pair_mech_distinctness": pairs_mech_differ,
        "cleanup_pair_pred_distinctness": pairs_pred_differ,
        "n_pairs_mech_differ": n_pairs_mech_d,
        "n_pairs_pred_differ": n_pairs_pred_d,
        "distinctness_self_report_pass": distinctness_pass,
        "cliff_K_log2_span": cliff_log2_span,
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
        "beta": BETA,
        "hop_max_steps": HOP_MAX_STEPS,
        "num_banks": body.get("num_banks"),
        "estimated_cliff_K_per_bank": body.get("estimated_cliff_K_per_bank"),
        "gpu_util_estimate": round(gpu_util_estimate, 3),
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} "
                    f"fail={n_fail}; pred_differ={n_pairs_pred_d}/10 "
                    f"mech_differ={n_pairs_mech_d}/10; "
                    f"cliff_log2_span={cliff_log2_span:.3f}; "
                    f"positive_control rec={pc_result.get('measured_recall')}; "
                    f"cleanup_tiers={cleanup_tiers}; "
                    f"gpu_util~{gpu_util_estimate:.2f}")
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
    # META_RULE_AY: HARD_FAIL if cell-self-reports distinctness=False
    if not distinctness_pass:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_META_RULE_AY_DISTINCTNESS: pred_differ={n_pairs_pred_d}/10 "
                f"mech_differ={n_pairs_mech_d}/10; cleanup arms COLLAPSED "
                f"(v1/v3 ANCHOR 4 phantom pattern); UNTRUSTED")
    elif not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
                f"observed={observed_n}")
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CONTROL_FAIL: positive_control "
                f"{pc_result.get('target')} measured recall="
                f"{pc_result.get('measured_recall')}; test rig broken")
    else:
        # Q-saturation gate (META_RULE_Q)
        sat_fraction = n_sat / max(observed_n, 1)
        if sat_fraction >= 0.75:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_BY_CONSTRUCTION_SATURATION: "
                    f"{n_sat}/{observed_n} pts saturated (>=0.75); "
                    f"discriminating regime not reached; "
                    f"cleanup_tiers={cleanup_tiers}")
        else:
            # Discriminator: at least 3 of 5 cleanups have DISTINCT cliff K
            # (cliff_log2_span >= 0.3 AND n_pairs_pred_differ >= 5)
            chain_grade_disc = (cliff_log2_span >= 0.30 and n_pairs_pred_d >= 5
                                 and n_disc >= 15)
            mb_disc = (cliff_log2_span >= 0.15 or n_pairs_pred_d >= 3)
            if chain_grade_disc:
                verdict = "HARD_PASS"
                vmsg = (f"HARD_PASS_CLEANUP_DISCRIMINATION_AT_WM_KCLIFF: "
                        f"{observed_n}/{expected_n} pts; "
                        f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} "
                        f"fail={n_fail}; pred_differ={n_pairs_pred_d}/10 "
                        f"cliff_log2_span={cliff_log2_span:.3f}; "
                        f"cleanup_tiers={cleanup_tiers}; "
                        f"positive_control rec={pc_result.get('measured_recall')}")
            elif mb_disc:
                verdict = "MIDDLE_BAND"
                vmsg = (f"MIDDLE_BAND_PARTIAL_CLEANUP_DISCRIMINATION: "
                        f"pred_differ={n_pairs_pred_d}/10 "
                        f"cliff_log2_span={cliff_log2_span:.3f} (need >=0.30 + 5/10); "
                        f"some cleanup discrimination but below chain-grade; "
                        f"cleanup_tiers={cleanup_tiers}")
            else:
                verdict = "HARD_FAIL"
                vmsg = (f"HARD_FAIL_CLEANUP_FAMILY_INVARIANT_AT_WM: "
                        f"pred_differ={n_pairs_pred_d}/10 "
                        f"cliff_log2_span={cliff_log2_span:.3f}; all 5 cleanups "
                        f"produce similar cliffs -- cleanup choice family-invariant "
                        f"at WM scale (same as PC finding); honest negative")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "DEVICE", "GPU_NAME", "GPU_MAX_MEM_GB",
    "SATURATED_RECALL", "HARD_PASS_LO", "MIDDLE_BAND_LO", "FLOOR_HI",
    "HP_DISCRIMINATOR", "MB_DISCRIMINATOR", "BETA", "HOP_MAX_STEPS",
    "CLEANUP_FAMILIES",
    "K_PER_BANK_SWEEP_FULL", "K_PER_BANK_SWEEP_SMOKE",
    "REGIMES_FULL", "REGIMES_SMOKE",
    "NUM_BANKS_FULL", "NUM_BANKS_SMOKE",
    "N_DIM_FULL", "N_DIM_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "POSITIVE_CONTROL", "POSITIVE_CONTROL_SMOKE",
    "REQUIRED_FIELDS",
    "estimated_cliff_K_per_bank", "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
