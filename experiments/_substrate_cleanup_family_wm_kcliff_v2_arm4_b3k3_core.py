"""Shared core for substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3 sibling cells.

CLEANUP-FAMILY phase diagram at WM K-cliff regime, ARM4 design:
  4 cleanups: classical_hopfield / modern_hopfield_continuous /
              iterative_attractor / wta_baseline
  3 B (num_banks):    {4, 16, 64}
  3 K (K_per_bank):   {K_cliff/2, K_cliff, 2*K_cliff}   per-B where K_cliff(B) = 256 * B

Cardinality per seed: 4 * 3 * 3 = 36 phase points (single RANDOM regime; adversarial
is dropped per task scope focus on K-cliff discrimination).

DIFFERENCES vs prior v1p1 (which landed MIDDLE_BAND with 5-arm no_cleanup+kNN
baseline set at N=4096, num_banks=8, absolute-K sweep):
  * ARM SET CHANGED: 4 primitives; wta_baseline replaces no_cleanup+kNN as the
    single non-mechanism reference. WTA = one-shot argmax over codebook then
    snap to nearest bipolar code (identical mechanism to prior kNN k=1 but
    labeled as WTA to match research doc phrasing).
  * B-SWEEP INSTEAD OF REGIME-SWEEP: 3 num_banks values; drops ADVERSARIAL to
    focus on K-cliff discrimination as the outer axis-F characteristic.
  * RELATIVE K-DESIGN: K_per_bank scaled to K_cliff(B)=256*B per-B; discriminator
    fires at K=2*K_cliff where WTA is expected to floor while modern/iterative
    are expected to lift.
  * N=8192 (task-mandated, matches research phase-diagram gap analysis).
  * META_RULE_Q suspect-1.000 gate at K=K_cliff.
  * META_RULE_AX arm-distinctness across cleanup family pair-distinctness.
  * DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke previews the DISCRIMINATOR scale
    K=2*K_cliff (not K=K_cliff where WTA saturates on small B).

Config profile:
  FULL:  N=8192, B in {4,16,64}, K per B as above, 3 seeds x 36 pts = 108/seed
  SMOKE: N=8192, B=4 (smallest to fit CPU memory), K in {512, 1024}
         (K_cliff and 2*K_cliff at B=4), 4 cleanups -> 8 phase points, single
         seed. Discriminator preview at 2*K_cliff.

Pre-reg: preregs/2026-07-01_substrate_cleanup_family_WM_K_cliff_v1.md
  (task literal name "v1"; anchor slug uses "v2_arm4_b3k3" to avoid data-dir
   collision with prior v1 OOM'd + v1p1 MIDDLE_BAND cells; pre-reg documents
   this naming rationale)

Author: exp_dev 2026-07-01 (Opus 4.7 1M).
ASCII-only. No unicode.
"""
from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

# Torch at TOP for PROT-020 GPU-eligibility scan
import torch

_CUDA_OK = bool(torch.cuda.is_available())
if _CUDA_OK:
    DEVICE = torch.device("cuda")
    GPU_NAME = torch.cuda.get_device_name(0)
else:
    DEVICE = torch.device("cpu")
    GPU_NAME = "cpu_fallback"


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED)
# ---------------------------------------------------------------------------
SATURATED_RECALL = 0.995
HARD_PASS_LO = 0.80
MIDDLE_BAND_LO = 0.50
FLOOR_HI = 0.10

BETA = 8.0
HOP_MAX_STEPS = 4

CLEANUP_FAMILIES = ("classical_hopfield", "modern_hopfield_continuous",
                    "iterative_attractor", "wta_baseline")

NUM_BANKS_FULL = (4, 16, 64)
NUM_BANKS_SMOKE = (4,)

# K_cliff(B) = 256 * B => at B=4:1024, B=16:4096, B=64:16384
# K design per B: {K_cliff/2, K_cliff, 2*K_cliff}
def k_cliff_of_B(B: int) -> int:
    return 256 * B

def k_sweep_full_for_B(B: int) -> List[int]:
    kc = k_cliff_of_B(B)
    return [kc // 2, kc, 2 * kc]

# Smoke sweep at B=4: K in {K_cliff, 2*K_cliff} = {1024, 2048}
# Discriminator preview at 2*K_cliff (task-mandated)
def k_sweep_smoke_for_B(B: int) -> List[int]:
    kc = k_cliff_of_B(B)
    return [kc, 2 * kc]

N_DIM_FULL = 8192
N_DIM_SMOKE = 8192   # smoke at FULL N for DISCRIMINATOR-MUST-SURVIVE-SCALE

# Substrate params
SIGMA = 1.0
CUE_COS = 0.70

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")

# Cardinality math (LOCKED at module init; META_RULE_H)
# FULL:  4 cleanups * 3 B * 3 K = 36 phase points per seed
# SMOKE: 4 cleanups * 1 B * 2 K = 8  phase points per seed
EXPECTED_N_UNITS_FULL = len(CLEANUP_FAMILIES) * len(NUM_BANKS_FULL) * 3   # 36
EXPECTED_N_UNITS_SMOKE = len(CLEANUP_FAMILIES) * len(NUM_BANKS_SMOKE) * 2  # 8


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# Substrate primitives
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


def build_codebook(seed_offset: int, codebook_size: int, n_dim: int) -> torch.Tensor:
    g = _make_gen(seed_offset)
    return random_bipolar_t((codebook_size, n_dim), g)


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
    bound = items_per_bank * slot_tags.unsqueeze(0)
    ws = bound.sum(dim=1).float()
    if SIGMA > 0.0:
        g_noise = _make_gen(seed_offset + 23)
        noise = torch.empty(ws.shape, device=DEVICE, dtype=torch.float32)
        noise.normal_(0.0, SIGMA, generator=g_noise)
        ws = ws + noise
    return bipolar_quantize_t(ws)


# ---------------------------------------------------------------------------
# CLEANUP PRIMITIVES (OUTER axis; 4 arms; META_RULE_AF arms-must-differ)
# ---------------------------------------------------------------------------
def _sign_op(V: torch.Tensor) -> torch.Tensor:
    out = torch.sign(V)
    return torch.where(out == 0, torch.ones_like(out), out)


# Chunk size to avoid peak-allocation OOM on large-M codebook matmuls
_CHUNK_M = 128


def _chunked_sims(query: torch.Tensor, codebook: torch.Tensor) -> torch.Tensor:
    """query @ codebook.T with row-chunking over codebook to bound peak alloc."""
    K_q = query.shape[0]
    M = codebook.shape[0]
    sims = torch.empty((K_q, M), device=query.device, dtype=query.dtype)
    for start in range(0, M, _CHUNK_M):
        end = min(start + _CHUNK_M, M)
        sims[:, start:end] = query @ codebook[start:end].T
    return sims


def cleanup_wta_baseline(query: torch.Tensor, codebook: torch.Tensor
                          ) -> Tuple[torch.Tensor, torch.Tensor]:
    """WTA baseline: one-shot argmax over codebook, snap to nearest bipolar code.

    This is the "no-mechanism" reference against which the 3 real cleanups
    are compared. Identical mechanism to prior kNN k=1 but labeled to match
    research doc "WTA baseline" phrasing.
    """
    sims = _chunked_sims(query, codebook)
    pred_idx = sims.argmax(dim=1)
    del sims
    if _CUDA_OK:
        torch.cuda.empty_cache()
    recovered = codebook[pred_idx]
    return recovered, pred_idx


def cleanup_classical_hopfield(query: torch.Tensor, codebook: torch.Tensor,
                                T: int = HOP_MAX_STEPS
                                ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Classical Hopfield: Hebbian W = X.T @ X / M; iterate sign(s @ W)."""
    M, N = codebook.shape
    # W is (N, N); at N=8192 fp32 that's 256 MiB. Chunk column-wise for smaller peak.
    W = (codebook.T @ codebook) / float(M)
    W.fill_diagonal_(0.0)
    state = query
    for _ in range(max(0, T)):
        h = state @ W
        state = _sign_op(h)
    del W
    if _CUDA_OK:
        torch.cuda.empty_cache()
    sims = _chunked_sims(state, codebook)
    pred_idx = sims.argmax(dim=1)
    del sims
    return state, pred_idx


def cleanup_modern_hopfield_continuous(query: torch.Tensor, codebook: torch.Tensor,
                                        T: int = HOP_MAX_STEPS, beta: float = BETA
                                        ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Modern Hopfield / Ramsauer 2021: T-step softmax-attention update."""
    state = query
    for _ in range(max(0, T)):
        sims = _chunked_sims(state, codebook) * beta
        weights = torch.softmax(sims, dim=1)
        s_mix = weights @ codebook
        state = _sign_op(s_mix)
        del sims, weights, s_mix
        if _CUDA_OK:
            torch.cuda.empty_cache()
    final_sims = _chunked_sims(state, codebook)
    pred_idx = final_sims.argmax(dim=1)
    del final_sims
    return state, pred_idx


def cleanup_iterative_attractor(query: torch.Tensor, codebook: torch.Tensor,
                                 T: int = HOP_MAX_STEPS, beta: float = BETA
                                 ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Iterative attractor: L2-normalized cosine softmax (brain-canonical CA3).

    Effective beta scaled by sqrt(D) per Ramsauer 2021 attention-scaling trick.
    """
    D = codebook.shape[1]
    eff_beta = beta * math.sqrt(D)
    cb_norm = codebook / (torch.linalg.norm(codebook, dim=1, keepdim=True)
                          .clamp(min=1e-12))
    state = query / (torch.linalg.norm(query, dim=1, keepdim=True)
                     .clamp(min=1e-12))
    for _ in range(max(0, T)):
        sims = _chunked_sims(state, cb_norm) * eff_beta
        weights = torch.softmax(sims, dim=1)
        s_mix = weights @ cb_norm
        state = s_mix / (torch.linalg.norm(s_mix, dim=1, keepdim=True)
                         .clamp(min=1e-12))
        del sims, weights, s_mix
        if _CUDA_OK:
            torch.cuda.empty_cache()
    final_sims = _chunked_sims(state, cb_norm)
    pred_idx = final_sims.argmax(dim=1)
    del cb_norm, final_sims
    recovered = _sign_op(state)
    return recovered, pred_idx


_CLEANUP_REGISTRY: Dict[str, Callable] = {
    "classical_hopfield": cleanup_classical_hopfield,
    "modern_hopfield_continuous": cleanup_modern_hopfield_continuous,
    "iterative_attractor": cleanup_iterative_attractor,
    "wta_baseline": cleanup_wta_baseline,
}


def _apply_cleanup(family: str, query: torch.Tensor, codebook: torch.Tensor
                    ) -> Tuple[torch.Tensor, torch.Tensor]:
    fn = _CLEANUP_REGISTRY[family]
    if family in ("classical_hopfield", "modern_hopfield_continuous",
                   "iterative_attractor"):
        return fn(query, codebook, HOP_MAX_STEPS)
    return fn(query, codebook)


# ---------------------------------------------------------------------------
# Per-point eval
# ---------------------------------------------------------------------------
def eval_phase_point(cleanup_family: str, K_per_bank: int, num_banks: int,
                      codebook: torch.Tensor, seed_offset: int,
                      n_dim: int) -> Dict[str, Any]:
    """One (cleanup_family, K_per_bank, num_banks) phase point (RANDOM regime)."""
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

    cb_size = codebook.shape[0]
    g_trial = _make_gen(seed_offset + 29)
    if K_total > cb_size:
        idx_global = torch.randint(0, cb_size, (K_total,), generator=g_trial,
                                    device=DEVICE)
    else:
        idx_global = torch.randperm(cb_size, generator=g_trial,
                                      device=DEVICE)[:K_total]
    items = codebook[idx_global]
    items_per_bank = items.view(num_banks, K_per_bank, n_dim)

    workspaces = write_bank(items_per_bank, slot_tags, seed_offset + 1000)

    slot_indices = torch.arange(K_total, device=DEVICE)
    bank_true = slot_indices // K_per_bank
    local_slot = slot_indices % K_per_bank

    g_cue = _make_gen(seed_offset + 5000)
    bank_cue_base = bank_tags[bank_true].float()
    noise = torch.empty((K_total, n_dim), device=DEVICE, dtype=torch.float32)
    noise.normal_(0.0, 1.0, generator=g_cue)
    noise_bp = bipolar_quantize_t(noise)
    cues = CUE_COS * bank_cue_base + cue_noise_scale * noise_bp

    route_sims = cues @ bank_tags.T
    bank_routed = route_sims.argmax(dim=1)
    ws_selected = workspaces[bank_routed]

    slot_tag_sel = slot_tags[local_slot]
    raw_query = ws_selected * slot_tag_sel

    recovered, pred_idx = _apply_cleanup(cleanup_family, raw_query, codebook)

    true_item_idx = idx_global[slot_indices]
    match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
    recall = float(match.sum().item()) / max(K_total, 1)
    route_acc = float((bank_routed == bank_true).sum().item()) / max(K_total, 1)

    mech_output_hash = hashlib.sha256(
        recovered.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    pred_pattern_hash = hashlib.sha256(
        pred_idx.detach().cpu().numpy().tobytes()).hexdigest()[:16]

    if _CUDA_OK:
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        peak_mem_mb = -1.0

    elapsed = time.time() - t0

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

    del slot_tags, bank_tags, workspaces, cues, noise, noise_bp, bank_cue_base
    del items, items_per_bank, ws_selected, slot_tag_sel, raw_query
    del recovered, pred_idx, true_item_idx, match, bank_routed
    del idx_global, slot_indices, bank_true, local_slot, route_sims
    if _CUDA_OK:
        torch.cuda.empty_cache()

    kc = k_cliff_of_B(num_banks)
    return {
        "cleanup_family": cleanup_family,
        "K_per_bank": K_per_bank,
        "num_banks": num_banks,
        "K_total": K_total,
        "K_cliff_B": kc,
        "K_ratio_over_cliff": round(K_per_bank / max(kc, 1), 3),
        "N": n_dim,
        "recall": round(recall, 4),
        "route_acc": round(route_acc, 4),
        "mech_output_hash": mech_output_hash,
        "pred_pattern_hash": pred_pattern_hash,
        "verdict_tier_per_point": tier,
        "saturation_flag": recall >= SATURATED_RECALL,
        "peak_mem_mb": round(peak_mem_mb, 1),
        "elapsed_per_point_s": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Selftest: cardinality math + 4 arms distinct at tiny regime."""
    msgs: List[str] = []

    if EXPECTED_N_UNITS_FULL != 36:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 36"
    if EXPECTED_N_UNITS_SMOKE != 8:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 8"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    for fam in CLEANUP_FAMILIES:
        if fam not in _CLEANUP_REGISTRY or not callable(_CLEANUP_REGISTRY[fam]):
            return False, f"cleanup {fam} not registered/callable"
    msgs.append(f"4 cleanups registered: {list(_CLEANUP_REGISTRY.keys())}")

    # K_cliff formula sanity
    if k_cliff_of_B(4) != 1024 or k_cliff_of_B(16) != 4096 or k_cliff_of_B(64) != 16384:
        return False, f"K_cliff formula wrong: B=4->{k_cliff_of_B(4)} B=16->{k_cliff_of_B(16)}"
    msgs.append(f"K_cliff: B4={k_cliff_of_B(4)} B16={k_cliff_of_B(16)} B64={k_cliff_of_B(64)}")

    # Tiny-regime primitive sanity
    n_dim_san = 512
    cb_size_san = 256
    k_per_bank_san = 8
    num_banks_san = 4
    codebook = build_codebook(seed * 11 + 1, cb_size_san, n_dim_san)
    san_pred_hashes: Dict[str, str] = {}
    san_recalls: Dict[str, float] = {}
    for fam in CLEANUP_FAMILIES:
        r = eval_phase_point(fam, k_per_bank_san, num_banks_san, codebook,
                              seed_offset=seed * 7 + 100, n_dim=n_dim_san)
        san_pred_hashes[fam] = r["pred_pattern_hash"]
        san_recalls[fam] = r["recall"]
        msgs.append(f"sanity {fam}: rec={r['recall']:.3f}")

    # At least 3 of 4 arms above floor 0.20 at tiny (well below capacity)
    n_above = sum(1 for v in san_recalls.values() if v >= 0.20)
    if n_above < 3:
        return False, (f"only {n_above}/4 cleanups clear floor 0.20 at TINY sanity: "
                       f"{san_recalls}; primitives likely buggy")
    msgs.append(f"{n_above}/4 cleanups >= 0.20 at sanity")

    # META_RULE_AX/AY: at least 3 of 6 pairs must have distinct pred hashes
    fams = list(CLEANUP_FAMILIES)
    n_distinct = 0
    n_pairs = 0
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            n_pairs += 1
            if san_pred_hashes[fams[i]] != san_pred_hashes[fams[j]]:
                n_distinct += 1
    if n_distinct < 3:
        return False, (f"META_RULE_AX VIOLATION: {n_distinct}/{n_pairs} pairs distinct "
                       f"at sanity; primitives likely collapsed: {san_pred_hashes}")
    msgs.append(f"distinctness sanity: {n_distinct}/{n_pairs} pairs distinct")

    del codebook
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    banks_sweep = NUM_BANKS_SMOKE if is_smoke else NUM_BANKS_FULL
    k_sweep_fn = k_sweep_smoke_for_B if is_smoke else k_sweep_full_for_B
    n_dim = N_DIM_SMOKE if is_smoke else N_DIM_FULL
    expected_n_units = (EXPECTED_N_UNITS_SMOKE if is_smoke
                        else EXPECTED_N_UNITS_FULL)

    # Codebook size: max K_total across sweep + 2x headroom
    max_K_total = 0
    for B in banks_sweep:
        max_K_total = max(max_K_total, max(k_sweep_fn(B)) * B)
    cb_size = max(4096, int(max_K_total * 2))

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"cleanups={CLEANUP_FAMILIES} banks={banks_sweep} N={n_dim} CB={cb_size} "
          f"expected_n={expected_n_units}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()

    # Build codebook once per seed (all points share)
    cb = build_codebook(seed * 100003 + 99, cb_size, n_dim)
    print(f"[codebook] seed={seed} shape={tuple(cb.shape)}", flush=True)

    for B in banks_sweep:
        k_sweep = k_sweep_fn(B)
        print(f"[bank B={B}] K_sweep={k_sweep} (K_cliff={k_cliff_of_B(B)})",
              flush=True)
        for fam in CLEANUP_FAMILIES:
            for K in k_sweep:
                seed_offset = (seed * 100003 + K * 31 + B * 7907
                                + hash(fam) % 7919)
                print(f"[point] seed={seed} fam={fam} B={B} K={K} ...", flush=True)
                pt = eval_phase_point(fam, K, B, cb, seed_offset, n_dim)
                phase_map.append(pt)
                print(f"  -> recall={pt['recall']:.3f} ra={pt['route_acc']:.3f} "
                      f"tier={pt['verdict_tier_per_point']} "
                      f"peak_mb={pt['peak_mem_mb']:.1f} "
                      f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)
            if _CUDA_OK:
                torch.cuda.empty_cache()

    del cb
    if _CUDA_OK:
        torch.cuda.empty_cache()

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Pair-wise distinctness (META_RULE_AX): 4 cleanups -> 6 pairs
    fams = list(CLEANUP_FAMILIES)
    pred_lookup: Dict[Tuple[str, int, int], str] = {}
    mech_lookup: Dict[Tuple[str, int, int], str] = {}
    for p in phase_map:
        key = (p["cleanup_family"], p["K_per_bank"], p["num_banks"])
        pred_lookup[key] = p["pred_pattern_hash"]
        mech_lookup[key] = p["mech_output_hash"]

    pairs_pred_differ: Dict[str, bool] = {}
    pairs_mech_differ: Dict[str, bool] = {}
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            pair_key = f"{fams[i]}_vs_{fams[j]}"
            any_pred_diff = False
            any_mech_diff = False
            for B in banks_sweep:
                for K in k_sweep_fn(B):
                    k_i = (fams[i], K, B)
                    k_j = (fams[j], K, B)
                    if k_i in pred_lookup and k_j in pred_lookup:
                        if pred_lookup[k_i] != pred_lookup[k_j]:
                            any_pred_diff = True
                        if mech_lookup[k_i] != mech_lookup[k_j]:
                            any_mech_diff = True
            pairs_pred_differ[pair_key] = any_pred_diff
            pairs_mech_differ[pair_key] = any_mech_diff

    n_pairs = len(pairs_pred_differ)  # should be 6
    n_pairs_pred_d = sum(1 for v in pairs_pred_differ.values() if v)
    n_pairs_mech_d = sum(1 for v in pairs_mech_differ.values() if v)
    distinctness_pass = (n_pairs_pred_d == n_pairs and n_pairs_mech_d == n_pairs)

    # Per-cleanup summary + task-mandated discriminator computation:
    # At K=2*K_cliff (index 2 in the K sweep, 0-indexed), does any non-WTA
    # cleanup lift recall >= 0.10 above wta_baseline?
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
        # Recall at each B x K
        recall_at = {f"B{p['num_banks']}_K{p['K_per_bank']}": p["recall"]
                      for p in fam_pts}
        per_cleanup_summary[fam] = {
            "recall_mean": round(recall_mean, 4),
            "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                            "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                            "HARD_FAIL": n_fail},
            "recall_at_BK": recall_at,
        }

    # Task-mandated discriminator: at K=2*K_cliff (the highest K per B), does
    # any non-WTA cleanup lift recall by >= 0.10 vs wta_baseline?
    # Compute per-B and aggregate.
    disc_by_B: Dict[int, Dict[str, Any]] = {}
    for B in banks_sweep:
        K_disc = 2 * k_cliff_of_B(B)
        wta_key = f"B{B}_K{K_disc}"
        wta_recall = per_cleanup_summary.get("wta_baseline", {}).get(
            "recall_at_BK", {}).get(wta_key, -1.0)
        lifts = {}
        for fam in ("classical_hopfield", "modern_hopfield_continuous",
                     "iterative_attractor"):
            fam_recall = per_cleanup_summary.get(fam, {}).get(
                "recall_at_BK", {}).get(wta_key, -1.0)
            lift = fam_recall - wta_recall if wta_recall >= 0 else -1.0
            lifts[fam] = round(lift, 4)
        max_lift = max(lifts.values()) if lifts else -1.0
        disc_by_B[B] = {
            "K_disc": K_disc,
            "wta_recall": wta_recall,
            "lifts_over_wta": lifts,
            "max_lift": round(max_lift, 4),
            "discriminator_fires": max_lift >= 0.10,
        }

    n_B_discriminator_fires = sum(1 for v in disc_by_B.values()
                                    if v["discriminator_fires"])

    # META_RULE_Q: check for suspect-1.000 at K=K_cliff (task requirement)
    q_suspect_at_cliff: List[str] = []
    for B in banks_sweep:
        K_at_cliff = k_cliff_of_B(B)
        for fam in CLEANUP_FAMILIES:
            key = f"B{B}_K{K_at_cliff}"
            r = per_cleanup_summary.get(fam, {}).get("recall_at_BK", {}).get(key, -1.0)
            if r >= SATURATED_RECALL:
                q_suspect_at_cliff.append(f"{fam}_{key}={r}")

    if _CUDA_OK:
        peak_mems = [p["peak_mem_mb"] for p in phase_map if p["peak_mem_mb"] > 0]
        avg_peak = sum(peak_mems) / max(len(peak_mems), 1)
    else:
        avg_peak = 0.0

    return {
        "seed": seed,
        "run_mode": run_mode,
        "cleanup_families": list(CLEANUP_FAMILIES),
        "num_banks_sweep": list(banks_sweep),
        "N": n_dim,
        "M": cb_size,
        "phase_map": phase_map,
        "per_cleanup_summary": per_cleanup_summary,
        "cleanup_pair_pred_distinctness": pairs_pred_differ,
        "cleanup_pair_mech_distinctness": pairs_mech_differ,
        "n_pairs_pred_differ": n_pairs_pred_d,
        "n_pairs_mech_differ": n_pairs_mech_d,
        "n_pairs_total": n_pairs,
        "distinctness_self_report_pass": distinctness_pass,
        "discriminator_by_B": disc_by_B,
        "n_B_discriminator_fires": n_B_discriminator_fires,
        "q_suspect_at_cliff": q_suspect_at_cliff,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "device": str(DEVICE),
        "gpu_name": GPU_NAME,
        "avg_peak_mem_mb": round(avg_peak, 1),
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke gate + verdict
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    """Smoke gate:
      1. cardinality_ok
      2. distinctness_self_report_pass (META_RULE_AX; all 6 pairs distinct)
      3. DISCRIMINATOR-MUST-SURVIVE-SCALE: at K=2*K_cliff (B=4 smoke), at least
         one non-WTA cleanup lifts recall >= 0.10 above wta_baseline
      4. No silent dead-code: each cleanup produces phase points
    """
    observed_n = body.get("observed_n_units", 0)
    expected_n = body.get("expected_n_units", 0)
    distinctness_pass = body.get("distinctness_self_report_pass", False)
    n_pairs_pred_d = body.get("n_pairs_pred_differ", 0)
    n_pairs_mech_d = body.get("n_pairs_mech_differ", 0)
    n_pairs_total = body.get("n_pairs_total", 6)
    disc_by_B = body.get("discriminator_by_B", {})
    per_cleanup = body.get("per_cleanup_summary", {})

    if observed_n != expected_n:
        return False, f"cardinality_breach: expected={expected_n} observed={observed_n}"

    if not distinctness_pass:
        return False, (f"META_RULE_AX_DISTINCTNESS_FAIL: pred_differ="
                       f"{n_pairs_pred_d}/{n_pairs_total} mech_differ="
                       f"{n_pairs_mech_d}/{n_pairs_total} (need all {n_pairs_total} each); "
                       f"cleanup arms COLLAPSED; ABORT")

    for fam in CLEANUP_FAMILIES:
        summary = per_cleanup.get(fam, {})
        if sum(summary.get("tier_counts", {}).values()) == 0:
            return False, f"silent_dead_code: cleanup {fam} produced 0 phase points"

    # DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke runs only B=4, and the discriminator
    # is defined at K=2*K_cliff which is the highest K in smoke sweep. Require
    # discriminator to fire at at least one B (in smoke that's the only B).
    n_fires = sum(1 for v in disc_by_B.values() if v.get("discriminator_fires"))
    if n_fires < 1:
        lifts_report = {int(B): v.get("max_lift", -1.0)
                         for B, v in disc_by_B.items()}
        return False, (f"DISCRIMINATOR_FAILS_SCALE: no B produced lift >= 0.10 above "
                       f"wta_baseline at K=2*K_cliff; max_lifts_per_B={lifts_report}; "
                       f"cleanup family capability-orthogonal at WM scale even at smoke; "
                       f"ABORT full dispatch")

    return True, (f"smoke_gate_pass: cardinality_ok + distinctness "
                  f"{n_pairs_pred_d}/{n_pairs_total} pred + discriminator fires at "
                  f"{n_fires}/{len(disc_by_B)} B values")


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_NO_SEEDS: empty per_seed",
            "summary": "HARD_FAIL_NO_SEEDS",
        }

    is_smoke = (run_mode == "smoke")

    # Multi-seed aggregation: for smoke we have 1 seed; for full we may have 3.
    seed_keys = list(per_seed.keys())
    bodies = [per_seed[k] for k in seed_keys]

    # Union phase_map (for FULL cross-seed we still compute per-seed disc, then
    # aggregate at the (fam, B, K) level).
    all_phase: List[Dict[str, Any]] = []
    for b in bodies:
        for p in b.get("phase_map", []):
            all_phase.append({**p, "seed": b.get("seed")})

    # Per (fam, B, K) mean + cv across seeds
    from collections import defaultdict
    key_recalls: Dict[Tuple[str, int, int], List[float]] = defaultdict(list)
    for p in all_phase:
        key_recalls[(p["cleanup_family"], p["num_banks"], p["K_per_bank"])].append(
            p["recall"])
    per_key_stats: Dict[str, Dict[str, float]] = {}
    for k, rs in key_recalls.items():
        m = float(np.mean(rs))
        s = float(np.std(rs))
        cv = (s / max(abs(m), 1e-6)) if len(rs) >= 2 else 0.0
        per_key_stats[f"{k[0]}_B{k[1]}_K{k[2]}"] = {
            "recall_mean": round(m, 4),
            "recall_std": round(s, 4),
            "cv": round(cv, 4),
            "n_seeds": len(rs),
        }

    # Distinctness (use first-seed report; all seeds should agree)
    body0 = bodies[0]
    distinctness_pass_all = all(b.get("distinctness_self_report_pass", False)
                                 for b in bodies)
    n_pairs_pred_d = body0.get("n_pairs_pred_differ", 0)
    n_pairs_mech_d = body0.get("n_pairs_mech_differ", 0)
    n_pairs_total = body0.get("n_pairs_total", 6)

    # Discriminator across-seeds: at each B, compute mean-lift of best non-WTA
    # cleanup at K=2*K_cliff; require mean_lift >= 0.10 AND cv < 0.08.
    disc_across_seeds: Dict[int, Dict[str, Any]] = {}
    banks_all = sorted({p["num_banks"] for p in all_phase})
    for B in banks_all:
        K_disc = 2 * k_cliff_of_B(B)
        wta_key = f"wta_baseline_B{B}_K{K_disc}"
        wta_stats = per_key_stats.get(wta_key, {"recall_mean": -1.0})
        wta_mean = wta_stats.get("recall_mean", -1.0)
        best_lift = -1.0
        best_fam = None
        best_cv = 1.0
        lifts: Dict[str, float] = {}
        for fam in ("classical_hopfield", "modern_hopfield_continuous",
                     "iterative_attractor"):
            fam_key = f"{fam}_B{B}_K{K_disc}"
            fam_stats = per_key_stats.get(fam_key, {"recall_mean": -1.0, "cv": 1.0})
            fam_mean = fam_stats.get("recall_mean", -1.0)
            lift = fam_mean - wta_mean if wta_mean >= 0 else -1.0
            lifts[fam] = round(lift, 4)
            if lift > best_lift:
                best_lift = lift
                best_fam = fam
                best_cv = fam_stats.get("cv", 1.0)
        disc_across_seeds[B] = {
            "K_disc": K_disc,
            "wta_mean": round(wta_mean, 4),
            "lifts_over_wta": lifts,
            "best_fam": best_fam,
            "best_lift": round(best_lift, 4),
            "best_fam_cv": round(best_cv, 4),
            "discriminator_fires_seed_consistent": (best_lift >= 0.10
                                                     and best_cv < 0.08),
        }
    n_B_seed_consistent = sum(1 for v in disc_across_seeds.values()
                                if v["discriminator_fires_seed_consistent"])

    # Q-suspect union
    q_suspects_all: List[str] = []
    for b in bodies:
        q_suspects_all.extend(b.get("q_suspect_at_cliff", []))

    n_hp = sum(1 for p in all_phase if p["verdict_tier_per_point"] == "HARD_PASS")
    n_mb = sum(1 for p in all_phase if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in all_phase if p["verdict_tier_per_point"] == "SATURATED")
    n_floor = sum(1 for p in all_phase if p["verdict_tier_per_point"] == "FLOOR")
    n_fail = sum(1 for p in all_phase if p["verdict_tier_per_point"] == "HARD_FAIL")

    common = {
        "phase_map_flat": all_phase,
        "per_key_stats_across_seeds": per_key_stats,
        "cleanup_pair_pred_distinctness": body0.get("cleanup_pair_pred_distinctness", {}),
        "cleanup_pair_mech_distinctness": body0.get("cleanup_pair_mech_distinctness", {}),
        "n_pairs_pred_differ": n_pairs_pred_d,
        "n_pairs_mech_differ": n_pairs_mech_d,
        "n_pairs_total": n_pairs_total,
        "distinctness_self_report_pass": distinctness_pass_all,
        "discriminator_across_seeds": disc_across_seeds,
        "n_B_seed_consistent_fires": n_B_seed_consistent,
        "q_suspect_at_cliff_union": q_suspects_all,
        "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                        "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                        "HARD_FAIL": n_fail},
        "n_seeds": len(seed_keys),
        "cardinality_ok_per_seed": [b.get("cardinality_ok") for b in bodies],
        "expected_n_units_per_seed": [b.get("expected_n_units") for b in bodies],
        "observed_n_units_per_seed": [b.get("observed_n_units") for b in bodies],
        "device": body0.get("device"),
        "gpu_name": body0.get("gpu_name"),
        "beta": BETA,
        "hop_max_steps": HOP_MAX_STEPS,
        "cleanup_families": list(CLEANUP_FAMILIES),
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body0)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {common['observed_n_units_per_seed']}/"
                    f"{common['expected_n_units_per_seed']} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"pred_differ={n_pairs_pred_d}/{n_pairs_total}; "
                    f"disc_fires_by_B={ {B: v['discriminator_fires'] for B, v in body0.get('discriminator_by_B', {}).items()} }; "
                    f"gate: {reason}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_SMOKE: {reason}; sat={n_sat} hp={n_hp} mb={n_mb} "
                    f"floor={n_floor} fail={n_fail}")
        out = dict(common)
        out.update({
            "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg,
            "smoke_gate_pass": passed, "smoke_gate_reason": reason,
        })
        return out

    # FULL verdict
    if not distinctness_pass_all:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_META_RULE_AX_DISTINCTNESS: pred_differ={n_pairs_pred_d}/"
                f"{n_pairs_total} mech_differ={n_pairs_mech_d}/{n_pairs_total}; "
                f"cleanup arms COLLAPSED at FULL; UNTRUSTED")
    elif not all(common["cardinality_ok_per_seed"]):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected="
                f"{common['expected_n_units_per_seed']} observed="
                f"{common['observed_n_units_per_seed']}")
    else:
        n_B_total = len(disc_across_seeds)
        # HARD_PASS: >= 1 B has seed-consistent lift >= 0.10 (per task discriminator)
        # AND no Q-saturation contamination at K=K_cliff
        q_contamination = len(q_suspects_all) > 0
        if n_B_seed_consistent >= 1 and not q_contamination:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_CLEANUP_DISCRIMINATION_AT_WM_KCLIFF_v2: "
                    f"{n_B_seed_consistent}/{n_B_total} B produce seed-consistent "
                    f"lift >= 0.10 above wta_baseline at K=2*K_cliff (cv<0.08); "
                    f"disc_across_seeds={disc_across_seeds}; "
                    f"pred_differ={n_pairs_pred_d}/{n_pairs_total}; "
                    f"tier_counts=sat{n_sat}/hp{n_hp}/mb{n_mb}/floor{n_floor}/fail{n_fail}")
        elif n_B_seed_consistent >= 1 and q_contamination:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_CLEANUP_DISCRIMINATION_WITH_Q_CONTAMINATION: "
                    f"discriminator fires at {n_B_seed_consistent}/{n_B_total} B but "
                    f"Q-saturation contamination detected at K=K_cliff: "
                    f"{q_suspects_all}; META_RULE_Q trip; tier downgraded")
        else:
            # Check if any lift exists but is inconsistent (MB) vs all-collapse (HF)
            any_partial = any(v["best_lift"] >= 0.05 for v in disc_across_seeds.values())
            if any_partial:
                verdict = "MIDDLE_BAND"
                vmsg = (f"MIDDLE_BAND_PARTIAL_DISCRIMINATION: some B show lift>=0.05 "
                        f"but no B seed-consistent at lift>=0.10 (cv<0.08); "
                        f"disc={disc_across_seeds}")
            else:
                verdict = "HARD_FAIL"
                vmsg = (f"HARD_FAIL_CLEANUP_FAMILY_INVARIANT_AT_WM: all 4 cleanups "
                        f"collapse to within +/-0.05 at K=2*K_cliff across all B; "
                        f"cleanup choice capability-orthogonal at WM scale (matches "
                        f"PC finding); honest negative; disc={disc_across_seeds}")

    out = dict(common)
    out.update({"verdict": verdict, "verdict_msg": vmsg, "summary": vmsg})
    return out


__all__ = [
    "DEVICE", "GPU_NAME",
    "SATURATED_RECALL", "HARD_PASS_LO", "MIDDLE_BAND_LO", "FLOOR_HI",
    "BETA", "HOP_MAX_STEPS",
    "CLEANUP_FAMILIES",
    "NUM_BANKS_FULL", "NUM_BANKS_SMOKE",
    "N_DIM_FULL", "N_DIM_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "REQUIRED_FIELDS",
    "k_cliff_of_B", "k_sweep_full_for_B", "k_sweep_smoke_for_B",
    "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
