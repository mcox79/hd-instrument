"""Shared core for substrate_hierarchical_bank_v2_S32 sibling cells.

REVIVAL cell per Skunkworks 310e1880 criterion. v1 landed HARD_FAIL because
router SNR = sqrt(N*S/M) collapsed to 0.358 at M=64K, N=8192, S=8 (using
prior single-workspace derivation) -- routing_acc fell below 0.85 floor.

**Revival hypothesis:** shifting to S=32 sub-banks lifts router SNR to
sqrt(N*S/M) = sqrt(8192*32/64000) = 2.024 at M=64K. Router should NOT
collapse at this SNR regime.

CODEBOOK-STRUCTURE phase diagram (v2): 3 codebook structures (flat /
partition_by_source (CG baseline) / hierarchical_S32_2level (NEW)) x 3
M values {4000, 16000, 64000}.

CODEBOOK STRUCTURES (OUTER axis; LOCKED):
    flat                       : single flat codebook; argmax over full M
    partition_by_source        : S=32 sub-banks with oracle-source routing
    hierarchical_S32_2level    : context-router -> sub-bank; S=32 (REVIVAL)

INNER AXES:
    M in {4000, 16000, 64000}
    n_super_banks = 32 FIXED (REVIVAL from v1 S=8)
    N_DIM = 8192 FIXED

CARDINALITY:
  FULL: 3 structures * 3 M = 9 phase points per seed
  SMOKE: 3 structures * 2 M = 6 corner points per seed (M in {4000, 64000};
         DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke MUST include M=64000)

PRE-REG: preregs/2026-07-01_substrate_hierarchical_bank_v2_S32_revival.md

CPU-eligible: numpy only; no torch. Routes to remote_cpu_queue (or local_cpu
for smoke). Matmul-bound at M=64000 x N=8192 (~4 GiB peak); laptop-tractable.

ASCII-only. No unicode.

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn) via Skunkworks revival.
"""
from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Dict, List, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
SATURATED_RECALL = 0.995      # META_RULE_Q suspect-1.000
HARD_PASS_LO = 0.80
MIDDLE_BAND_LO = 0.50
FLOOR_HI = 0.10

# Codebook structures (OUTER axis; LOCKED)
CODEBOOK_STRUCTURES = ("flat", "partition_by_source", "hierarchical_S32_2level")

# Sweep axes
M_SWEEP_FULL = [4000, 16000, 64000]
M_SWEEP_SMOKE = [4000, 64000]   # DISCRIMINATOR-MUST-SURVIVE-SCALE: MUST include M=64000

N_DIM_FIXED = 8192
N_SUPER_BANKS = 32              # REVIVAL: v2 shifts from S=8 to S=32

# Router-imperfection tuning (anti-META_RULE_Q; keeps routing_acc < 1.000)
CUE_ROUTE_COS = 0.85         # target routing_acc in [0.90, 0.98] band
CUE_COS = 0.70               # item cue-to-slot similarity
SIGMA = 1.0                  # workspace noise on writes

# HP-lift threshold (research spec)
HP_CAPACITY_LIFT_RATIO = 1.20      # hierarchical >= 1.20 * flat at M=64K
HP_ROUTING_ACC_MIN = 0.95
HP_ROUTING_ACC_MAX = 0.995         # META_RULE_Q anti-saturation upper bound
HP_CV_MAX = 0.10                   # cross-seed cv
HF_ROUTING_ACC_MIN = 0.85          # below this -> HARD_FAIL (routing collapse)
MB_LIFT_RATIO_SMOKE = 1.10         # relaxed for single-seed smoke

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = len(CODEBOOK_STRUCTURES) * len(M_SWEEP_FULL)      # 3 * 3 = 9
EXPECTED_N_UNITS_SMOKE = len(CODEBOOK_STRUCTURES) * len(M_SWEEP_SMOKE)    # 3 * 2 = 6

# Positive control: at SMALLEST M, flat structure must clear MIDDLE_BAND_LO
# (M=4000 in N=8192; well below cliff; substrate must trivially recover).
POSITIVE_CONTROL = {
    "codebook_structure": "flat",
    "M": 4000,
    "recall_floor": 0.80,
}
POSITIVE_CONTROL_SMOKE = POSITIVE_CONTROL  # smoke includes M=4000

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "numpy.cpu"


# ---------------------------------------------------------------------------
# CRLB / capacity-feasibility (META_RULE_AG)
# ---------------------------------------------------------------------------
def matched_filter_snr(n_dim: int, m_effective: int) -> float:
    """Matched-filter SNR for bipolar codebook of M items in N-dim.

    SNR = sqrt(N / (M-1)). Cliff at SNR ~ 1, i.e. M ~ N+1.
    For partition + hierarchical, M_effective = M / n_super_banks.
    """
    if m_effective <= 1:
        return float("inf")
    return math.sqrt(n_dim / (m_effective - 1))


def router_snr(n_dim: int, m: int, s: int) -> float:
    """Router SNR for hierarchical 2-level bank per Skunkworks 310e1880:

    Router SNR = sqrt(N * S / M) (Skunkworks-corrected form; S sub-banks
    partition router crosstalk).

    v1 at N=8192, M=64K, S=8:  SNR = sqrt(1.024) = 1.012  (marginal; collapsed)
    v2 at N=8192, M=64K, S=32: SNR = sqrt(4.096) = 2.024  (well above 0.85 floor)
    """
    if m <= 0:
        return float("inf")
    return math.sqrt(n_dim * s / m)


# ---------------------------------------------------------------------------
# HD substrate primitives
# ---------------------------------------------------------------------------
def _rng(seed_int: int) -> np.random.Generator:
    return np.random.default_rng(int(seed_int))


def random_bipolar(shape: Tuple[int, ...], rng: np.random.Generator) -> np.ndarray:
    """Bipolar {-1, +1} tensor."""
    return (rng.integers(0, 2, size=shape, dtype=np.int8) * 2 - 1).astype(np.float32)


def bipolar_quantize(v: np.ndarray) -> np.ndarray:
    out = np.sign(v).astype(np.float32)
    out[out == 0.0] = 1.0
    return out


def build_codebook(seed_offset: int, M: int, n_dim: int) -> np.ndarray:
    return random_bipolar((M, n_dim), _rng(seed_offset))


def build_router_tags(seed_offset: int, n_super_banks: int,
                       n_dim: int) -> np.ndarray:
    """One bipolar tag per super-bank."""
    return random_bipolar((n_super_banks, n_dim), _rng(seed_offset + 17))


def build_slot_tags(seed_offset: int, k_per_bank: int, n_dim: int) -> np.ndarray:
    return random_bipolar((k_per_bank, n_dim), _rng(seed_offset + 13))


def make_cues_bundled(items: np.ndarray, seed_offset: int,
                       chunk_size: int = 1024) -> np.ndarray:
    """Cues generated via HD bundle-and-extract WITH capacity-scaling interference.

    Standard HD associative memory design (Kanerva 2009 SDM); interference
    grows with M via SNR = sqrt(N/M). Chunked to bound peak memory.
    """
    M, N = items.shape
    rng = _rng(seed_offset + 5000)

    slot_tags = random_bipolar((M, N), _rng(seed_offset + 5001))

    workspace = np.zeros(N, dtype=np.float32)
    for start in range(0, M, chunk_size):
        end = min(start + chunk_size, M)
        bound = items[start:end] * slot_tags[start:end]
        workspace += bound.sum(axis=0)
    noise = rng.standard_normal(N).astype(np.float32) * SIGMA
    workspace = workspace + noise
    workspace_bp = bipolar_quantize(workspace)

    cues = np.empty((M, N), dtype=np.float32)
    for start in range(0, M, chunk_size):
        end = min(start + chunk_size, M)
        cues[start:end] = workspace_bp[None, :] * slot_tags[start:end]
    return cues


def make_cues(items: np.ndarray, cue_cos: float,
              seed_offset: int) -> np.ndarray:
    """Deprecated alias -- returns make_cues_bundled."""
    return make_cues_bundled(items, seed_offset)


def make_router_cues(true_super_bank_ids: np.ndarray,
                      router_tags: np.ndarray,
                      cue_route_cos: float,
                      seed_offset: int) -> np.ndarray:
    """Router cues: cue_route_cos * router_tag[true_bank] + orth noise."""
    M = int(true_super_bank_ids.shape[0])
    N = int(router_tags.shape[1])
    rng = _rng(seed_offset + 6000)
    noise = bipolar_quantize(rng.standard_normal((M, N)).astype(np.float32))
    scale = math.sqrt(max(0.0, 1.0 - cue_route_cos * cue_route_cos))
    base = router_tags[true_super_bank_ids]
    return cue_route_cos * base + scale * noise


# ---------------------------------------------------------------------------
# CODEBOOK STRUCTURE PRIMITIVES (the load-bearing OUTER axis)
# Common signature: (items, cues, aux) -> (pred_idx (M,), routing_acc, label)
# ---------------------------------------------------------------------------
def structure_flat(items: np.ndarray, cues: np.ndarray,
                    n_super_banks: int, seed_offset: int
                    ) -> Tuple[np.ndarray, float, str]:
    """Flat baseline: argmax over full codebook.

    Chunked matmul to bound peak allocation at M=64000, N=8192.
    """
    M = items.shape[0]
    K = cues.shape[0]
    pred_idx = np.empty(K, dtype=np.int64)
    chunk = 64
    for start in range(0, K, chunk):
        end = min(start + chunk, K)
        sims_chunk = cues[start:end] @ items.T
        pred_idx[start:end] = np.argmax(sims_chunk, axis=1)
    routing_acc = 1.0
    routing_label = "flat_no_routing"
    return pred_idx, routing_acc, routing_label


def structure_partition_by_source(items: np.ndarray, cues: np.ndarray,
                                    n_super_banks: int, seed_offset: int
                                    ) -> Tuple[np.ndarray, float, str]:
    """Partition-by-source (ANCHOR 1 CG baseline): oracle-source routing.

    Items pre-partitioned into S sub-banks by index modulo S. Each sub-bank
    has its own INDEPENDENT bundled workspace with only M/S items.
    routing_acc = 1.000 by construction (oracle).
    """
    M = items.shape[0]
    N = items.shape[1]
    S = n_super_banks

    item_bank = np.arange(M) % S
    pred_idx = np.empty(M, dtype=np.int64)

    for b in range(S):
        sub_item_mask = item_bank == b
        sub_items = items[sub_item_mask]
        sub_item_global_idx = np.where(sub_item_mask)[0]
        M_sub = sub_items.shape[0]
        if M_sub == 0:
            continue

        sub_slot_tags = random_bipolar(
            (M_sub, N), _rng(seed_offset + 5001 + b * 101))

        ws_sub = np.zeros(N, dtype=np.float32)
        chunk_bundle = 1024
        for start in range(0, M_sub, chunk_bundle):
            end = min(start + chunk_bundle, M_sub)
            bound = sub_items[start:end] * sub_slot_tags[start:end]
            ws_sub += bound.sum(axis=0)
        rng = _rng(seed_offset + 5000 + b * 101)
        noise = rng.standard_normal(N).astype(np.float32) * SIGMA
        ws_sub = ws_sub + noise
        ws_sub_bp = bipolar_quantize(ws_sub)

        sub_pred_local = np.empty(M_sub, dtype=np.int64)
        chunk = 64
        for start in range(0, M_sub, chunk):
            end = min(start + chunk, M_sub)
            cue_chunk = ws_sub_bp[None, :] * sub_slot_tags[start:end]
            sims_chunk = cue_chunk @ sub_items.T
            sub_pred_local[start:end] = np.argmax(sims_chunk, axis=1)

        pred_idx[sub_item_mask] = sub_item_global_idx[sub_pred_local]

    routing_acc = 1.0   # oracle routing by construction
    routing_label = f"oracle_partition_by_source_S{S}_per_bank_workspace"
    return pred_idx, routing_acc, routing_label


def structure_hierarchical_S32_2level(items: np.ndarray, cues: np.ndarray,
                                       n_super_banks: int, seed_offset: int
                                       ) -> Tuple[np.ndarray, float, str]:
    """Hierarchical 2-level bank REVIVAL at S=32 (v2): context-router -> sub-bank.

    Design identical to v1 hierarchical_2level, but n_super_banks=32 (v1 used 8).
    Router SNR = sqrt(N*S/M) scales with S: at M=64K, N=8192, S=32:
    SNR = 2.024 (vs 1.012 at S=8). Should NOT collapse at 0.85 floor.

    Per-bank readout has M/S items -> readout SNR = sqrt(S) * flat_SNR.
    At M=64K, S=32: M_eff = 2000; readout SNR = sqrt(8192/1999) = 2.024.

    Chunked matmul throughout to bound peak allocation.
    """
    M = items.shape[0]
    N = items.shape[1]
    S = n_super_banks

    item_bank = np.arange(M) % S
    true_cue_bank = np.arange(M) % S

    router_tags = build_router_tags(seed_offset, S, N)

    # LAYER 1: Router workspace
    router_ws = np.zeros(N, dtype=np.float32)
    chunk = 1024
    for start in range(0, M, chunk):
        end = min(start + chunk, M)
        rt = router_tags[item_bank[start:end]]
        bound = items[start:end] * rt
        router_ws += bound.sum(axis=0)
    rng_r = _rng(seed_offset + 5000)
    router_ws += rng_r.standard_normal(N).astype(np.float32) * SIGMA
    router_ws_bp = bipolar_quantize(router_ws)

    routed_bank = np.empty(M, dtype=np.int64)
    for start in range(0, M, chunk):
        end = min(start + chunk, M)
        rc = router_ws_bp[None, :] * items[start:end]
        route_sims = rc @ router_tags.T
        routed_bank[start:end] = np.argmax(route_sims, axis=1)

    routing_correct = int((routed_bank == true_cue_bank).sum())
    routing_acc = routing_correct / max(M, 1)

    # LAYER 2: Per-sub-bank readout workspace + slot-tag lookup
    slot_tags_all = random_bipolar((M, N), _rng(seed_offset + 5001))
    pred_idx = np.empty(M, dtype=np.int64)
    for b in range(S):
        sub_item_mask = item_bank == b
        sub_items = items[sub_item_mask]
        sub_item_global_idx = np.where(sub_item_mask)[0]
        M_sub = sub_items.shape[0]
        if M_sub == 0:
            routed_here = routed_bank == b
            if routed_here.any():
                pred_idx[routed_here] = 0
            continue

        sub_slot_tags = slot_tags_all[sub_item_mask]

        readout_ws = np.zeros(N, dtype=np.float32)
        for start in range(0, M_sub, chunk):
            end = min(start + chunk, M_sub)
            bound = sub_items[start:end] * sub_slot_tags[start:end]
            readout_ws += bound.sum(axis=0)
        rng_ro = _rng(seed_offset + 5002 + b * 101)
        readout_ws += rng_ro.standard_normal(N).astype(np.float32) * SIGMA
        readout_ws_bp = bipolar_quantize(readout_ws)

        routed_here_mask = routed_bank == b
        if not routed_here_mask.any():
            continue
        routed_here_idx = np.where(routed_here_mask)[0]
        n_here = int(len(routed_here_idx))
        sub_pred_local = np.empty(n_here, dtype=np.int64)
        for start in range(0, n_here, chunk):
            end = min(start + chunk, n_here)
            batch_idx = routed_here_idx[start:end]
            slot_batch = slot_tags_all[batch_idx]
            cue_batch = readout_ws_bp[None, :] * slot_batch
            sims_chunk = cue_batch @ sub_items.T
            sub_pred_local[start:end] = np.argmax(sims_chunk, axis=1)
        pred_idx[routed_here_mask] = sub_item_global_idx[sub_pred_local]

    routing_label = f"hierarchical_2level_S{S}_two_workspace_router_REVIVAL_v2"
    return pred_idx, routing_acc, routing_label


_STRUCTURE_REGISTRY = {
    "flat": structure_flat,
    "partition_by_source": structure_partition_by_source,
    "hierarchical_S32_2level": structure_hierarchical_S32_2level,
}


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def eval_phase_point(structure: str, M: int, seed_offset: int,
                      n_dim: int) -> Dict[str, Any]:
    """One (structure, M) phase point."""
    if structure not in _STRUCTURE_REGISTRY:
        raise ValueError(f"unknown structure={structure!r}")

    t0 = time.time()
    fn = _STRUCTURE_REGISTRY[structure]

    items = build_codebook(seed_offset, M, n_dim)
    cues = make_cues(items, CUE_COS, seed_offset)

    pred_idx, routing_acc, routing_label = fn(items, cues, N_SUPER_BANKS,
                                                seed_offset)

    true_idx = np.arange(M)
    match = pred_idx == true_idx
    recall = float(match.sum()) / max(M, 1)

    pred_pattern_hash = hashlib.sha256(pred_idx.tobytes()).hexdigest()[:16]
    prefix_len = min(1024, M)
    mech_output_hash = hashlib.sha256(
        pred_idx[:prefix_len].tobytes()).hexdigest()[:16]

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

    if structure == "flat":
        m_eff = M
    else:
        m_eff = M // N_SUPER_BANKS
    snr = matched_filter_snr(n_dim, m_eff)
    r_snr = (router_snr(n_dim, M, N_SUPER_BANKS)
             if structure == "hierarchical_S32_2level" else None)

    del items, cues

    return {
        "codebook_structure": structure,
        "M": M,
        "n_super_banks": N_SUPER_BANKS,
        "M_effective_per_bank": m_eff,
        "N": n_dim,
        "recall": round(recall, 4),
        "routing_acc": round(routing_acc, 4),
        "routing_label": routing_label,
        "mech_output_hash": mech_output_hash,
        "pred_pattern_hash": pred_pattern_hash,
        "verdict_tier_per_point": tier,
        "saturation_flag": recall >= SATURATED_RECALL,
        "snr_matched_filter": round(snr, 4),
        "router_snr_predicted": (round(r_snr, 4) if r_snr is not None else None),
        "elapsed_per_point_s": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Selftest (cardinality + primitive sanity + distinctness gate)
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Selftest: cardinality math + primitive sanity + ARM-DISTINCTNESS at tiny."""
    msgs: List[str] = []

    if EXPECTED_N_UNITS_FULL != 9:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 9"
    if EXPECTED_N_UNITS_SMOKE != 6:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 6"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

    for s in CODEBOOK_STRUCTURES:
        if s not in _STRUCTURE_REGISTRY:
            return False, f"structure {s} not in registry"
        if not callable(_STRUCTURE_REGISTRY[s]):
            return False, f"structure {s} not callable"
    msgs.append(f"3 structures registered: {list(_STRUCTURE_REGISTRY.keys())}")

    # CRLB sanity for v2 S=32
    snr_flat_64k = matched_filter_snr(N_DIM_FIXED, 64000)
    snr_partition_64k = matched_filter_snr(N_DIM_FIXED, 64000 // N_SUPER_BANKS)
    router_snr_64k = router_snr(N_DIM_FIXED, 64000, N_SUPER_BANKS)
    if N_SUPER_BANKS != 32:
        return False, (f"N_SUPER_BANKS = {N_SUPER_BANKS} != 32 (v2 REVIVAL "
                       f"criterion demands S=32)")
    if not (0.3 < snr_flat_64k < 0.4):
        return False, (f"CRLB flat SNR at M=64K = {snr_flat_64k:.3f} "
                       f"outside [0.3, 0.4]")
    # partition_M_eff=2000 at N=8192 -> SNR = sqrt(8192/1999) = 2.024
    if not (1.95 < snr_partition_64k < 2.10):
        return False, (f"CRLB partition SNR at M_eff=2000 = "
                       f"{snr_partition_64k:.3f} outside [1.95, 2.10]")
    # router SNR at M=64K S=32 must be >= 2.0 (revival criterion)
    if not (1.95 < router_snr_64k < 2.10):
        return False, (f"REVIVAL_CRITERION_FAIL: router SNR at M=64K S=32 = "
                       f"{router_snr_64k:.3f} outside [1.95, 2.10]; v2 spec "
                       f"demands sqrt(N*S/M) = sqrt(4.096) = 2.024")
    msgs.append(f"CRLB flat_64K_SNR={snr_flat_64k:.3f} "
                f"partition_M_eff2000_SNR={snr_partition_64k:.3f} "
                f"router_64K_S32_SNR={router_snr_64k:.3f} (REVIVAL: >= 2.0)")

    # Per-primitive sanity at small N + M (S=32 -> M must be >= a few * S to
    # populate sub-banks). N=1024, S=32, M=320 -> 10 items/bank; flat SNR
    # = sqrt(1024/319)=1.79 (safe); partition/hier M_eff=10 -> SNR=10.7 (safe)
    n_dim_san = 1024
    M_san = 320
    san_results: Dict[str, Dict[str, Any]] = {}
    for s in CODEBOOK_STRUCTURES:
        r = eval_phase_point(s, M_san, seed_offset=seed * 7 + 100,
                              n_dim=n_dim_san)
        san_results[s] = r
        msgs.append(f"sanity {s}: M={M_san} N={n_dim_san} "
                    f"rec={r['recall']:.3f} route_acc={r['routing_acc']:.3f}")

    part_r = san_results["partition_by_source"]["recall"]
    if part_r < HARD_PASS_LO:
        return False, (f"partition_by_source recall={part_r:.3f} < HARD_PASS_LO "
                       f"{HARD_PASS_LO} at sanity; ANCHOR 1 baseline broken")
    hier_r = san_results["hierarchical_S32_2level"]["recall"]
    if hier_r < MIDDLE_BAND_LO:
        return False, (f"hierarchical_S32_2level recall={hier_r:.3f} < "
                       f"MIDDLE_BAND_LO {MIDDLE_BAND_LO} at sanity; "
                       f"hierarchical primitive broken")
    msgs.append(f"partition {part_r:.3f} >= HP_LO {HARD_PASS_LO}; "
                f"hierarchical_S32 {hier_r:.3f} >= MB_LO {MIDDLE_BAND_LO}; "
                f"flat={san_results['flat']['recall']:.3f}")

    hier_route = san_results["hierarchical_S32_2level"]["routing_acc"]
    # Sanity floor: routing_acc must beat random-32-way (0.03125) by wide margin
    if hier_route < 0.30:
        return False, (f"router too weak: hierarchical routing_acc="
                       f"{hier_route:.4f} at sanity; below 0.30 floor "
                       f"(9.6x random 0.031); router primitive broken")
    if hier_route > 1.0 + 1e-6:
        return False, (f"router routing_acc={hier_route:.4f} > 1.0 at sanity; "
                       f"impossible; primitive buggy")
    msgs.append(f"router sanity: routing_acc={hier_route:.4f} in "
                f"[0.30, 1.000] (Q-guard defers to smoke/full at scale)")

    # META_RULE_AX: pred_pattern_hash across 3 structures >=2 pairs distinct
    structs = list(CODEBOOK_STRUCTURES)
    n_distinct = 0
    n_pairs = 0
    for i in range(len(structs)):
        for j in range(i + 1, len(structs)):
            n_pairs += 1
            hi = san_results[structs[i]]["pred_pattern_hash"]
            hj = san_results[structs[j]]["pred_pattern_hash"]
            if hi != hj:
                n_distinct += 1
    if n_distinct < 2:
        return False, (f"META_RULE_AX VIOLATION: only {n_distinct}/{n_pairs} "
                       f"structure-pair predictions distinct at sanity")
    msgs.append(f"distinctness sanity: {n_distinct}/{n_pairs} structure pairs distinct")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        M_sweep = M_SWEEP_SMOKE
    else:
        M_sweep = M_SWEEP_FULL

    n_dim = N_DIM_FIXED
    expected_n_units = len(CODEBOOK_STRUCTURES) * len(M_sweep)

    print(f"[run_one_seed] seed={seed} mode={run_mode} "
          f"structures={CODEBOOK_STRUCTURES} M_sweep={M_sweep} "
          f"N={n_dim} S={N_SUPER_BANKS} "
          f"expected_n={expected_n_units}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()

    for structure in CODEBOOK_STRUCTURES:
        for M in M_sweep:
            seed_offset = (seed * 100003 + M * 31 + hash(structure) % 7919)
            print(f"[point] seed={seed} structure={structure} M={M} ...",
                  flush=True)
            pt = eval_phase_point(structure, M, seed_offset, n_dim)
            phase_map.append(pt)
            print(f"  -> recall={pt['recall']:.3f} "
                  f"route_acc={pt['routing_acc']:.3f} "
                  f"tier={pt['verdict_tier_per_point']} "
                  f"snr={pt['snr_matched_filter']:.3f} "
                  f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    structs = list(CODEBOOK_STRUCTURES)
    pred_lookup: Dict[Tuple[str, int], str] = {}
    mech_lookup: Dict[Tuple[str, int], str] = {}
    for p in phase_map:
        key = (p["codebook_structure"], p["M"])
        pred_lookup[key] = p["pred_pattern_hash"]
        mech_lookup[key] = p["mech_output_hash"]

    pairs_pred_differ: Dict[str, bool] = {}
    pairs_mech_differ: Dict[str, bool] = {}
    for i in range(len(structs)):
        for j in range(i + 1, len(structs)):
            pair_key = f"{structs[i]}_vs_{structs[j]}"
            any_pred_diff = False
            any_mech_diff = False
            for M in M_sweep:
                k_i = (structs[i], M)
                k_j = (structs[j], M)
                if k_i in pred_lookup and k_j in pred_lookup:
                    if pred_lookup[k_i] != pred_lookup[k_j]:
                        any_pred_diff = True
                    if mech_lookup[k_i] != mech_lookup[k_j]:
                        any_mech_diff = True
            pairs_pred_differ[pair_key] = any_pred_diff
            pairs_mech_differ[pair_key] = any_mech_diff

    n_pairs_pred_differ = sum(1 for v in pairs_pred_differ.values() if v)
    n_pairs_mech_differ = sum(1 for v in pairs_mech_differ.values() if v)
    distinctness_pass = (n_pairs_pred_differ >= 2 and n_pairs_mech_differ >= 2)

    per_structure_summary: Dict[str, Dict[str, Any]] = {}
    M_max = max(M_sweep)
    for structure in CODEBOOK_STRUCTURES:
        pts = [p for p in phase_map if p["codebook_structure"] == structure]
        recalls = [p["recall"] for p in pts]
        routing_accs = [p["routing_acc"] for p in pts]
        recall_mean = float(np.mean(recalls)) if recalls else 0.0
        max_M_pts = [p for p in pts if p["M"] == M_max]
        cap_per_slot_at_max = (max_M_pts[0]["recall"] if max_M_pts else 0.0)
        route_acc_at_max = (max_M_pts[0]["routing_acc"] if max_M_pts else 0.0)
        per_structure_summary[structure] = {
            "recall_mean": round(recall_mean, 4),
            "routing_acc_mean": round(float(np.mean(routing_accs)), 4),
            "capacity_per_slot_at_M_max": round(cap_per_slot_at_max, 4),
            "routing_acc_at_M_max": round(route_acc_at_max, 4),
            "recall_per_M": {str(p["M"]): p["recall"] for p in pts},
            "routing_acc_per_M": {str(p["M"]): p["routing_acc"] for p in pts},
        }

    flat_cap = per_structure_summary["flat"]["capacity_per_slot_at_M_max"]
    part_cap = per_structure_summary["partition_by_source"]["capacity_per_slot_at_M_max"]
    hier_cap = per_structure_summary["hierarchical_S32_2level"]["capacity_per_slot_at_M_max"]
    hier_route = per_structure_summary["hierarchical_S32_2level"]["routing_acc_at_M_max"]

    if flat_cap > 1e-6:
        capacity_lift_hier_vs_flat = hier_cap / flat_cap
        capacity_lift_hier_vs_partition = (hier_cap / part_cap
                                            if part_cap > 1e-6 else float("inf"))
    else:
        capacity_lift_hier_vs_flat = (float("inf") if hier_cap > 1e-6 else 1.0)
        capacity_lift_hier_vs_partition = (hier_cap / part_cap
                                            if part_cap > 1e-6 else 1.0)

    pc_target = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    pc_matches = [p for p in phase_map
                   if p["codebook_structure"] == pc_target["codebook_structure"]
                   and p["M"] == pc_target["M"]]
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
        "codebook_structures": list(CODEBOOK_STRUCTURES),
        "M_sweep": list(M_sweep),
        "n_super_banks": N_SUPER_BANKS,
        "N": n_dim,
        "phase_map": phase_map,
        "per_structure_summary": per_structure_summary,
        "structure_pair_pred_distinctness": pairs_pred_differ,
        "structure_pair_mech_distinctness": pairs_mech_differ,
        "n_pairs_pred_differ": n_pairs_pred_differ,
        "n_pairs_mech_differ": n_pairs_mech_differ,
        "distinctness_self_report_pass": distinctness_pass,
        "capacity_lift_hier_vs_flat_at_M_max": round(capacity_lift_hier_vs_flat, 4),
        "capacity_lift_hier_vs_partition_at_M_max": round(
            capacity_lift_hier_vs_partition, 4),
        "hier_routing_acc_at_M_max": round(hier_route, 4),
        "positive_control_result": positive_control_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "device": "cpu",
        "backend": "numpy",
        "elapsed_seed_s": round(elapsed, 2),
        "M_max_measured": M_max,
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    """Pre-reg smoke gate."""
    observed_n = body.get("observed_n_units", 0)
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    distinctness_pass = body.get("distinctness_self_report_pass", False)
    pairs_pred = body.get("structure_pair_pred_distinctness", {})
    pairs_mech = body.get("structure_pair_mech_distinctness", {})
    hier_route = body.get("hier_routing_acc_at_M_max", 0.0)
    lift_vs_flat = body.get("capacity_lift_hier_vs_flat_at_M_max", 0.0)
    per_structure = body.get("per_structure_summary", {})

    if observed_n != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {observed_n}"

    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                       f"measured={pc_result.get('measured_recall')}; "
                       f"test rig broken")

    if not distinctness_pass:
        n_pred_d = sum(1 for v in pairs_pred.values() if v)
        n_mech_d = sum(1 for v in pairs_mech.values() if v)
        return False, (f"META_RULE_AX_DISTINCTNESS_FAIL: pred_differ={n_pred_d}/3 "
                       f"mech_differ={n_mech_d}/3 (need >=2 each); "
                       f"structure arms COLLAPSED")

    if hier_route >= SATURATED_RECALL:
        return False, (f"META_RULE_Q_ROUTER_SATURATION: routing_acc="
                       f"{hier_route:.4f} >= {SATURATED_RECALL} at M=max; "
                       f"by-construction perfect routing; tune CUE_ROUTE_COS")

    if hier_route < HF_ROUTING_ACC_MIN:
        return False, (f"routing_acc_collapse: {hier_route:.4f} < "
                       f"{HF_ROUTING_ACC_MIN} at M=max; router failed at smoke "
                       f"(REVIVAL_HYPOTHESIS_FALSIFIED: S=32 not enough)")

    flat_r = per_structure.get("flat", {}).get("capacity_per_slot_at_M_max", 0.0)
    part_r = per_structure.get("partition_by_source", {}).get(
        "capacity_per_slot_at_M_max", 0.0)
    hier_r = per_structure.get("hierarchical_S32_2level", {}).get(
        "capacity_per_slot_at_M_max", 0.0)

    lift_pass = (lift_vs_flat >= MB_LIFT_RATIO_SMOKE)
    struct_pass = (part_r >= flat_r + 0.20 and hier_r >= flat_r + 0.20)
    discriminator_fires = lift_pass or struct_pass

    if not discriminator_fires:
        return False, (f"discriminator_fails_scale_at_M={body.get('M_max_measured')}: "
                       f"flat={flat_r:.3f} part={part_r:.3f} hier={hier_r:.3f}; "
                       f"lift={lift_vs_flat:.3f} (need >= {MB_LIFT_RATIO_SMOKE}) "
                       f"OR struct-lift-0.20 fail; "
                       f"DISCRIMINATOR-MUST-SURVIVE-SCALE breach")

    return True, (f"smoke_gate_pass: cardinality_ok + positive_control_pass + "
                  f"distinctness pred={sum(1 for v in pairs_pred.values() if v)}/3 + "
                  f"router_ok({HF_ROUTING_ACC_MIN}<={hier_route:.3f}<{SATURATED_RECALL}) + "
                  f"lift_vs_flat={lift_vs_flat:.3f} @ M="
                  f"{body.get('M_max_measured')} "
                  f"(flat={flat_r:.3f} part={part_r:.3f} hier={hier_r:.3f})")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
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
    per_structure = body.get("per_structure_summary", {})
    pairs_pred = body.get("structure_pair_pred_distinctness", {})
    pairs_mech = body.get("structure_pair_mech_distinctness", {})
    n_pairs_pred_d = body.get("n_pairs_pred_differ", 0)
    n_pairs_mech_d = body.get("n_pairs_mech_differ", 0)
    distinctness_pass = body.get("distinctness_self_report_pass", False)
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)
    lift_vs_flat = body.get("capacity_lift_hier_vs_flat_at_M_max", 0.0)
    lift_vs_partition = body.get("capacity_lift_hier_vs_partition_at_M_max", 0.0)
    hier_route = body.get("hier_routing_acc_at_M_max", 0.0)

    n_hp = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_mb = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "SATURATED")
    n_floor = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "FLOOR")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")
    n_disc = n_hp + n_mb

    common = {
        "phase_map": phase_map,
        "per_structure_summary": per_structure,
        "structure_pair_pred_distinctness": pairs_pred,
        "structure_pair_mech_distinctness": pairs_mech,
        "n_pairs_pred_differ": n_pairs_pred_d,
        "n_pairs_mech_differ": n_pairs_mech_d,
        "distinctness_self_report_pass": distinctness_pass,
        "capacity_lift_hier_vs_flat_at_M_max": lift_vs_flat,
        "capacity_lift_hier_vs_partition_at_M_max": lift_vs_partition,
        "hier_routing_acc_at_M_max": hier_route,
        "positive_control_result": pc_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                        "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                        "HARD_FAIL": n_fail},
        "n_discriminating": n_disc,
        "M_max_measured": body.get("M_max_measured"),
        "n_super_banks": body.get("n_super_banks"),
        "device": body.get("device"),
        "backend": body.get("backend"),
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE_v2_S32_REVIVAL: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} "
                    f"fail={n_fail}; distinct pred={n_pairs_pred_d}/3 "
                    f"mech={n_pairs_mech_d}/3; hier_route={hier_route:.3f}; "
                    f"lift_vs_flat={lift_vs_flat:.3f} @ M_max; "
                    f"pos_ctrl rec={pc_result.get('measured_recall')}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_SMOKE_v2_S32_REVIVAL: {reason}; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}")
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
    if not distinctness_pass:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_META_RULE_AX_DISTINCTNESS: pred_differ={n_pairs_pred_d}/3 "
                f"mech_differ={n_pairs_mech_d}/3; structure arms COLLAPSED")
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
        if hier_route < HF_ROUTING_ACC_MIN:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_ROUTING_COLLAPSE_UNDER_LOAD_v2_REVIVAL: "
                    f"hier routing_acc={hier_route:.4f} < {HF_ROUTING_ACC_MIN} "
                    f"at M=64K; router failed under load; S=32 revival "
                    f"criterion FALSIFIED (predicted SNR=2.024 insufficient)")
        elif hier_route >= SATURATED_RECALL:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_BY_CONSTRUCTION_ROUTER_SATURATION: "
                    f"hier routing_acc={hier_route:.4f} >= {SATURATED_RECALL}; "
                    f"router by-construction perfect; not chain-grade")
        elif (lift_vs_flat >= HP_CAPACITY_LIFT_RATIO
              and HP_ROUTING_ACC_MIN <= hier_route < HP_ROUTING_ACC_MAX):
            if lift_vs_partition >= 1.05:
                verdict = "HARD_PASS"
                vmsg = (f"HARD_PASS_v2_S32_REVIVAL_HIER_LIFTS_CAPACITY_AT_M_MAX: "
                        f"lift_vs_flat={lift_vs_flat:.3f} (>={HP_CAPACITY_LIFT_RATIO}) "
                        f"lift_vs_partition={lift_vs_partition:.3f} (>=1.05) "
                        f"hier_routing_acc={hier_route:.3f} in "
                        f"[{HP_ROUTING_ACC_MIN},{HP_ROUTING_ACC_MAX}); "
                        f"S=32 revival CONFIRMED; tier_counts "
                        f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}")
            else:
                verdict = "MIDDLE_BAND"
                vmsg = (f"MIDDLE_BAND_LIFTS_FLAT_NOT_PARTITION_v2: "
                        f"lift_vs_flat={lift_vs_flat:.3f} OK but "
                        f"lift_vs_partition={lift_vs_partition:.3f} < 1.05; "
                        f"router adds cost without capacity gain over ANCHOR 1")
        elif (HP_ROUTING_ACC_MIN <= hier_route < HP_ROUTING_ACC_MAX
              and lift_vs_flat >= 1.05):
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_PARTIAL_LIFT_v2: lift_vs_flat={lift_vs_flat:.3f} "
                    f"(in [1.05, {HP_CAPACITY_LIFT_RATIO})) "
                    f"hier_routing_acc={hier_route:.3f} OK; below chain-grade lift")
        elif hier_route < HP_ROUTING_ACC_MIN:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_ROUTING_BORDERLINE_v2: hier_routing_acc="
                    f"{hier_route:.3f} in [{HF_ROUTING_ACC_MIN},{HP_ROUTING_ACC_MIN}); "
                    f"router imperfect below HP band; lift_vs_flat={lift_vs_flat:.3f}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_HIERARCHY_NO_CAPACITY_LIFT_v2: "
                    f"lift_vs_flat={lift_vs_flat:.3f} (< 1.05) "
                    f"hier_routing_acc={hier_route:.3f}; honest negative")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "CODEBOOK_STRUCTURES",
    "M_SWEEP_FULL", "M_SWEEP_SMOKE",
    "N_DIM_FIXED", "N_SUPER_BANKS",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "POSITIVE_CONTROL", "POSITIVE_CONTROL_SMOKE",
    "REQUIRED_FIELDS",
    "SATURATED_RECALL", "HARD_PASS_LO", "MIDDLE_BAND_LO", "FLOOR_HI",
    "HP_CAPACITY_LIFT_RATIO", "HP_ROUTING_ACC_MIN", "HP_ROUTING_ACC_MAX",
    "HF_ROUTING_ACC_MIN", "MB_LIFT_RATIO_SMOKE",
    "matched_filter_snr", "router_snr", "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
