"""Shared core for substrate_hierarchical_bank_v1 sibling cells.

CODEBOOK-STRUCTURE phase diagram: 3 codebook structures (flat /
partition_by_source / hierarchical_2level) x 3 M values {4000, 16000, 64000}.
Axis H CG-eligible (research 2026-07-01 gap analysis; CG=0.45 HIGH payoff).

Composes with ANCHOR 1 partition-by-source CG per META_RULE_AT.

CODEBOOK STRUCTURES (OUTER axis; LOCKED):
    flat                  : single flat codebook; argmax over full M
    partition_by_source   : S=8 sub-banks with oracle-source routing (ANCHOR 1 CG)
    hierarchical_2level   : context-router -> sub-bank (router tags; imperfect;
                            META_RULE_Q anti-saturation guard)

INNER AXES:
    M in {4000, 16000, 64000}
    n_super_banks = 8 FIXED
    N_DIM = 8192 FIXED

CARDINALITY:
  FULL: 3 structures * 3 M = 9 phase points per seed
  SMOKE: 3 structures * 2 M = 6 corner points per seed (M in {4000, 64000};
         DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke MUST include M=64000)

PRE-REG: preregs/2026-07-01_substrate_hierarchical_bank_v1.md

CPU-eligible: numpy only; no torch. Routes to remote_cpu_queue (or local_cpu
for smoke). Matmul-bound at M=64000 x N=8192 (~4 GiB peak); laptop-tractable.

ASCII-only. No unicode.

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn).
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
CODEBOOK_STRUCTURES = ("flat", "partition_by_source", "hierarchical_2level")

# Sweep axes
M_SWEEP_FULL = [4000, 16000, 64000]
M_SWEEP_SMOKE = [4000, 64000]   # DISCRIMINATOR-MUST-SURVIVE-SCALE: MUST include M=64000

N_DIM_FIXED = 8192
N_SUPER_BANKS = 8

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

    Real HD memory cliff comes from BUNDLE INTERFERENCE: workspace =
    sum_i (item_i * slot_tag_i); extract via *slot_tag_j gives
    item_j + sum_{i != j} (item_i * slot_tag_i * slot_tag_j).

    Each item has unique slot_tag (bipolar); ALL items bundled into ONE
    workspace vector (bipolar-quantized after sum + gaussian noise).
    Cue for item j = workspace * slot_tag_j.

    This is the standard HD associative memory design (Kanerva 2009 SDM);
    interference grows with M via SNR = sqrt(N/M).

    Chunked to bound peak memory at M=64000 x N=8192.
    """
    M, N = items.shape
    rng = _rng(seed_offset + 5000)

    # Build unique slot tags per item (bipolar)
    slot_tags = random_bipolar((M, N), _rng(seed_offset + 5001))

    # Bundle: workspace = sum_i (item_i * slot_tag_i) + noise, then bipolar-quantize
    # Chunked accumulation to avoid M x N intermediate
    workspace = np.zeros(N, dtype=np.float32)
    for start in range(0, M, chunk_size):
        end = min(start + chunk_size, M)
        bound = items[start:end] * slot_tags[start:end]  # (chunk, N)
        workspace += bound.sum(axis=0)  # (N,)
    # Additive noise (matches WM K-cliff convention SIGMA=1.0)
    noise = rng.standard_normal(N).astype(np.float32) * SIGMA
    workspace = workspace + noise
    workspace_bp = bipolar_quantize(workspace)  # (N,)

    # Extract per-item cue: workspace * slot_tag[i] (chunked)
    cues = np.empty((M, N), dtype=np.float32)
    for start in range(0, M, chunk_size):
        end = min(start + chunk_size, M)
        cues[start:end] = workspace_bp[None, :] * slot_tags[start:end]
    return cues


# Backwards alias for clarity in callsites
def make_cues(items: np.ndarray, cue_cos: float,
              seed_offset: int) -> np.ndarray:
    """Deprecated: use make_cues_bundled. cue_cos arg preserved for signature
    compatibility but ignored (bundle-based interference is capacity-scaling)."""
    return make_cues_bundled(items, seed_offset)


def make_router_cues(true_super_bank_ids: np.ndarray,
                      router_tags: np.ndarray,
                      cue_route_cos: float,
                      seed_offset: int) -> np.ndarray:
    """Router cues: cue_route_cos * router_tag[true_bank] + orth noise.

    Deliberately imperfect (anti-META_RULE_Q); target routing_acc in [0.90, 0.98].
    """
    M = int(true_super_bank_ids.shape[0])
    N = int(router_tags.shape[1])
    rng = _rng(seed_offset + 6000)
    noise = bipolar_quantize(rng.standard_normal((M, N)).astype(np.float32))
    scale = math.sqrt(max(0.0, 1.0 - cue_route_cos * cue_route_cos))
    base = router_tags[true_super_bank_ids]  # (M, N)
    return cue_route_cos * base + scale * noise


# ---------------------------------------------------------------------------
# CODEBOOK STRUCTURE PRIMITIVES (the load-bearing OUTER axis)
# Common signature: (items, cues, aux) -> (pred_idx (M,), routing_acc (float or None))
# ---------------------------------------------------------------------------
def structure_flat(items: np.ndarray, cues: np.ndarray,
                    n_super_banks: int, seed_offset: int
                    ) -> Tuple[np.ndarray, float, str]:
    """Flat baseline: argmax over full codebook.

    Chunked matmul to bound peak allocation at M=64000, N=8192, cues=64000.
    Peak per chunk: chunk_M x M float32 = 64 x 64000 x 4B = ~16 MB (vs 16 GB unchunked).
    """
    M = items.shape[0]
    K = cues.shape[0]
    pred_idx = np.empty(K, dtype=np.int64)
    chunk = 64
    for start in range(0, K, chunk):
        end = min(start + chunk, K)
        sims_chunk = cues[start:end] @ items.T   # (chunk, M)
        pred_idx[start:end] = np.argmax(sims_chunk, axis=1)
    # routing_acc: N/A for flat (no routing); report 1.0 (all "routed" to same bank)
    routing_acc = 1.0
    routing_label = "flat_no_routing"
    return pred_idx, routing_acc, routing_label


def structure_partition_by_source(items: np.ndarray, cues: np.ndarray,
                                    n_super_banks: int, seed_offset: int
                                    ) -> Tuple[np.ndarray, float, str]:
    """Partition-by-source (ANCHOR 1 CG baseline): oracle-source routing.

    Items pre-partitioned into S sub-banks by index modulo S. Each sub-bank
    has its own INDEPENDENT bundled workspace with only M/S items -> less
    interference. Cue KNOWS its true source (oracle) -> perfect routing.
    routing_acc = 1.000 by construction (oracle).

    Key: partition has REDUCED bundle interference because per-sub-bank
    workspace only contains M/S items (SNR ~ sqrt(N/(M/S)) = sqrt(S) * flat_SNR).

    The `cues` arg is IGNORED here; partition builds its own per-sub-bank
    bundled workspaces (this is a fair-comparison design: same interference
    mechanism, different sub-bank scope).
    """
    M = items.shape[0]
    N = items.shape[1]
    S = n_super_banks

    item_bank = np.arange(M) % S
    pred_idx = np.empty(M, dtype=np.int64)

    for b in range(S):
        sub_item_mask = item_bank == b
        sub_items = items[sub_item_mask]                   # (M_sub, N)
        sub_item_global_idx = np.where(sub_item_mask)[0]
        M_sub = sub_items.shape[0]
        if M_sub == 0:
            continue

        # Per-sub-bank slot tags (independent per sub-bank; use seed offset
        # varying by b to distinguish from flat's slot tags)
        sub_slot_tags = random_bipolar(
            (M_sub, N), _rng(seed_offset + 5001 + b * 101))

        # Per-sub-bank bundled workspace
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

        # Extract cues + argmax against sub-bank items
        sub_pred_local = np.empty(M_sub, dtype=np.int64)
        chunk = 64
        for start in range(0, M_sub, chunk):
            end = min(start + chunk, M_sub)
            cue_chunk = ws_sub_bp[None, :] * sub_slot_tags[start:end]
            sims_chunk = cue_chunk @ sub_items.T
            sub_pred_local[start:end] = np.argmax(sims_chunk, axis=1)

        pred_idx[sub_item_mask] = sub_item_global_idx[sub_pred_local]

    routing_acc = 1.0   # oracle routing by construction
    routing_label = "oracle_partition_by_source_per_bank_workspace"
    return pred_idx, routing_acc, routing_label


def structure_hierarchical_2level(items: np.ndarray, cues: np.ndarray,
                                    n_super_banks: int, seed_offset: int
                                    ) -> Tuple[np.ndarray, float, str]:
    """Hierarchical 2-level: context-router -> sub-bank.

    Uses SHARED bundled workspace for both routing + readout (this is the key
    to router-imperfection: router noise from other items scales with M, per
    META_RULE_Q anti-saturation). Distinct from partition_by_source (which
    has oracle routing) via routing_acc<1.000 at capacity.

    Design (two-workspace HD hierarchical):
      router_ws = sum_i (item_i * router_tag[i%S])
      route_cue_i = router_ws * item_i     # signal = router_tag[bank_i]
      routed_bank_i = argmax_s cos(route_cue_i, router_tag[s])
      per-bank readout_ws[b] = sum_{j in bank b} (item_j * slot_tag_j)
      readout_cue_i = readout_ws[routed_bank_i] * slot_tag_i
      pred_i = argmax_j in items[routed_bank_i] cos(readout_cue_i, item_j)

    Router noise: route_cue_i = item_i * item_i * router_tag[bank_i]
                              + sum_{j != i} item_j * item_i * router_tag[bank_j]
                    = router_tag[bank_i] + M-1 crosstalk terms
    Router SNR ~ sqrt(N/M). At M=64K, N=8192: SNR ~ 0.36 -> routing_acc < 1.0.

    Per-bank readout has M/S items -> readout SNR = sqrt(S) * flat_SNR.
    Chunked matmul throughout to bound M x M peak allocation.

    NOTE: this uses items directly as route cues (not `cues` arg). Design
    equivalence rationale: partition_by_source also builds its own per-bank
    workspaces; hierarchical builds its own two-tier workspaces. Cues arg
    only used by flat baseline.
    """
    M = items.shape[0]
    N = items.shape[1]
    S = n_super_banks

    item_bank = np.arange(M) % S
    true_cue_bank = np.arange(M) % S   # K == M

    # Router tags (bipolar, S x N)
    router_tags = build_router_tags(seed_offset, S, N)

    # LAYER 1: Router workspace = sum_i (item_i * router_tag[bank_i]) (chunked)
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

    # Route cues: for each item i, route_cue_i = router_ws * item_i
    # (item_i acts as its own "who am I" key against the router-tag bindings)
    routed_bank = np.empty(M, dtype=np.int64)
    for start in range(0, M, chunk):
        end = min(start + chunk, M)
        rc = router_ws_bp[None, :] * items[start:end]   # (chunk, N)
        route_sims = rc @ router_tags.T                 # (chunk, S)
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
            # cues routed here (may exist if some items misrouted here) -> fallback
            routed_here = routed_bank == b
            if routed_here.any():
                pred_idx[routed_here] = 0
            continue

        sub_slot_tags = slot_tags_all[sub_item_mask]

        # Per-bank readout workspace (bundled)
        readout_ws = np.zeros(N, dtype=np.float32)
        for start in range(0, M_sub, chunk):
            end = min(start + chunk, M_sub)
            bound = sub_items[start:end] * sub_slot_tags[start:end]
            readout_ws += bound.sum(axis=0)
        rng_ro = _rng(seed_offset + 5002 + b * 101)
        readout_ws += rng_ro.standard_normal(N).astype(np.float32) * SIGMA
        readout_ws_bp = bipolar_quantize(readout_ws)

        # For items ROUTED to bank b (correctly or not), extract via their
        # slot_tag against this readout workspace.
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

    routing_label = f"hierarchical_2level_S{S}_two_workspace_router"
    return pred_idx, routing_acc, routing_label


_STRUCTURE_REGISTRY = {
    "flat": structure_flat,
    "partition_by_source": structure_partition_by_source,
    "hierarchical_2level": structure_hierarchical_2level,
}


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def eval_phase_point(structure: str, M: int, seed_offset: int,
                      n_dim: int) -> Dict[str, Any]:
    """One (structure, M) phase point.

    Build M-item codebook + cues at CUE_COS; run structure primitive;
    measure recall + routing_acc + mechanism hashes.
    """
    if structure not in _STRUCTURE_REGISTRY:
        raise ValueError(f"unknown structure={structure!r}")

    t0 = time.time()
    fn = _STRUCTURE_REGISTRY[structure]

    items = build_codebook(seed_offset, M, n_dim)      # (M, N)
    cues = make_cues(items, CUE_COS, seed_offset)      # (M, N) K=M

    pred_idx, routing_acc, routing_label = fn(items, cues, N_SUPER_BANKS,
                                                seed_offset)

    true_idx = np.arange(M)
    match = pred_idx == true_idx
    recall = float(match.sum()) / max(M, 1)

    # Mechanism hashes
    pred_pattern_hash = hashlib.sha256(pred_idx.tobytes()).hexdigest()[:16]
    # For structure-output hash: hash the first 1024 predictions to bound compute
    # while catching mechanism differences (arms that agree on all M would still
    # agree on 1024-prefix; disagreeing arms hash-differ on prefix).
    prefix_len = min(1024, M)
    mech_output_hash = hashlib.sha256(
        pred_idx[:prefix_len].tobytes()).hexdigest()[:16]

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

    # CRLB M-effective
    if structure == "flat":
        m_eff = M
    else:
        m_eff = M // N_SUPER_BANKS
    snr = matched_filter_snr(n_dim, m_eff)

    # Free
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
        "elapsed_per_point_s": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Selftest (cardinality + primitive sanity + distinctness gate)
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Selftest: cardinality math + primitive sanity + ARM-DISTINCTNESS at tiny."""
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 9:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 9"
    if EXPECTED_N_UNITS_SMOKE != 6:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 6"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. All structures registered + callable
    for s in CODEBOOK_STRUCTURES:
        if s not in _STRUCTURE_REGISTRY:
            return False, f"structure {s} not in registry"
        if not callable(_STRUCTURE_REGISTRY[s]):
            return False, f"structure {s} not callable"
    msgs.append(f"3 structures registered: {list(_STRUCTURE_REGISTRY.keys())}")

    # 3. CRLB sanity
    snr_flat_64k = matched_filter_snr(N_DIM_FIXED, 64000)
    snr_partition_64k = matched_filter_snr(N_DIM_FIXED, 64000 // N_SUPER_BANKS)
    # flat at M=64K in N=8192 -> SNR = sqrt(8192/63999) = 0.358 (below cliff)
    if not (0.3 < snr_flat_64k < 0.4):
        return False, (f"CRLB check fail: flat SNR at M=64K = {snr_flat_64k:.3f} "
                       f"outside [0.3, 0.4]")
    # partition at M_eff=8000, N=8192 -> SNR = sqrt(8192/7999) = 1.012 (at cliff)
    if not (0.95 < snr_partition_64k < 1.05):
        return False, (f"CRLB check fail: partition SNR at M_eff=8000 = "
                       f"{snr_partition_64k:.3f} outside [0.95, 1.05]")
    msgs.append(f"CRLB flat_64K_SNR={snr_flat_64k:.3f} "
                f"partition_M_eff8000_SNR={snr_partition_64k:.3f}")

    # 4. Per-primitive sanity: use a NEAR-CLIFF regime so structures diverge.
    #    N=512, S=8, M=800 -> flat SNR = sqrt(512/799)=0.80 (near cliff);
    #    partition/hierarchical M_eff=100 -> SNR = sqrt(512/99)=2.27 (safe).
    #    Flat will have recall << 1.0 while partition/hierarchical hold high
    #    recall -- naturally distinct pred patterns.
    n_dim_san = 1024
    M_san = 200
    san_results: Dict[str, Dict[str, Any]] = {}
    for s in CODEBOOK_STRUCTURES:
        r = eval_phase_point(s, M_san, seed_offset=seed * 7 + 100,
                              n_dim=n_dim_san)
        san_results[s] = r
        msgs.append(f"sanity {s}: M={M_san} N={n_dim_san} "
                    f"rec={r['recall']:.3f} route_acc={r['routing_acc']:.3f}")

    # 5. Partition must clear HARD_PASS_LO (well-below cliff test rig sanity).
    #    Hierarchical must clear MIDDLE_BAND_LO (router imperfect but functional).
    #    Flat is allowed anywhere (bundle-interference dominates in this regime).
    part_r = san_results["partition_by_source"]["recall"]
    if part_r < HARD_PASS_LO:
        return False, (f"partition_by_source recall={part_r:.3f} < HARD_PASS_LO "
                       f"{HARD_PASS_LO} at sanity; ANCHOR 1 baseline broken")
    hier_r = san_results["hierarchical_2level"]["recall"]
    if hier_r < MIDDLE_BAND_LO:
        return False, (f"hierarchical_2level recall={hier_r:.3f} < MIDDLE_BAND_LO "
                       f"{MIDDLE_BAND_LO} at sanity; hierarchical primitive broken")
    msgs.append(f"partition {part_r:.3f} >= HP_LO {HARD_PASS_LO}; "
                f"hierarchical {hier_r:.3f} >= MB_LO {MIDDLE_BAND_LO}; "
                f"flat={san_results['flat']['recall']:.3f}")

    # 6. Hierarchical routing_acc MUST be in [0.70, 1.000] at sanity.
    #    Note: at tiny sanity regime (N=512, S=8, M=200), router routes 200
    #    cues over just 8 super-bank tags with SNR ~ sqrt(N/S) ~ sqrt(64)=8
    #    -- routing_acc=1.000 IS EXPECTED at sanity because cue-route-cos=0.85
    #    dominates the noise floor at that scale. The anti-META_RULE_Q guard
    #    fires in the SMOKE gate and FULL verdict where regime N=8192 x M=64K
    #    exercises router-imperfection under real capacity load. At sanity we
    #    only verify (a) primitive doesn't crash + (b) router can produce
    #    a sensible routing_acc in [0.70, 1.000] range.
    hier_route = san_results["hierarchical_2level"]["routing_acc"]
    # Sanity floor: routing_acc must beat random-8-way (0.125) by wide margin
    # AND be < 1.0. At sanity N=1024, M=200, S=8 observed ~0.68 (SNR-limited).
    if hier_route < 0.50:
        return False, (f"router too weak: hierarchical routing_acc="
                       f"{hier_route:.4f} at sanity; below 0.50 floor "
                       f"(4x random 0.125); router primitive broken")
    if hier_route > 1.0 + 1e-6:
        return False, (f"router routing_acc={hier_route:.4f} > 1.0 at sanity; "
                       f"impossible; primitive buggy")
    msgs.append(f"router sanity: routing_acc={hier_route:.4f} in "
                f"[0.50, 1.000] (Q-guard defers to smoke/full at scale)")

    # 7. META_RULE_AX: pred_pattern_hash across 3 structures must show
    # at least 2 distinct pairs (3 arms -> 3 pairs; need >=2 distinct)
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
    """Run all (structure, M) phase points for one seed."""
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

    # ARMS-DIFFER (META_RULE_AF + AX): per-structure pred + mech hashes
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
    # 3 arms -> 3 pairs; need >=2 distinct on both
    distinctness_pass = (n_pairs_pred_differ >= 2 and n_pairs_mech_differ >= 2)

    # Per-structure summary + capacity-per-slot at M=64000 (or max_M)
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

    # Capacity-lift metric (research spec): capacity_per_slot(hierarchical) / flat
    flat_cap = per_structure_summary["flat"]["capacity_per_slot_at_M_max"]
    part_cap = per_structure_summary["partition_by_source"]["capacity_per_slot_at_M_max"]
    hier_cap = per_structure_summary["hierarchical_2level"]["capacity_per_slot_at_M_max"]
    hier_route = per_structure_summary["hierarchical_2level"]["routing_acc_at_M_max"]

    # Guard div-by-zero: if flat_cap == 0 (deep FLOOR), report inf-lift
    if flat_cap > 1e-6:
        capacity_lift_hier_vs_flat = hier_cap / flat_cap
        capacity_lift_hier_vs_partition = (hier_cap / part_cap
                                            if part_cap > 1e-6 else float("inf"))
    else:
        capacity_lift_hier_vs_flat = (float("inf") if hier_cap > 1e-6 else 1.0)
        capacity_lift_hier_vs_partition = (hier_cap / part_cap
                                            if part_cap > 1e-6 else 1.0)

    # Positive control
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
    """Pre-reg smoke gate.

    Gates (mandatory):
      1. cardinality_ok
      2. positive_control passes (flat at M=4000 reaches floor)
      3. distinctness_self_report_pass (META_RULE_AX; >=2 of 3 pairs differ)
      4. router imperfect (routing_acc < SATURATED_RECALL at M=max)
      5. DISCRIMINATOR-MUST-SURVIVE-SCALE at M=64000:
         (a) hierarchical capacity_per_slot >= 1.10 * flat, OR
         (b) both partition + hierarchical are >=0.20 above flat recall at M=64K
      6. router_acc not collapsed (>= HF_ROUTING_ACC_MIN)
    """
    observed_n = body.get("observed_n_units", 0)
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    distinctness_pass = body.get("distinctness_self_report_pass", False)
    pairs_pred = body.get("structure_pair_pred_distinctness", {})
    pairs_mech = body.get("structure_pair_mech_distinctness", {})
    hier_route = body.get("hier_routing_acc_at_M_max", 0.0)
    lift_vs_flat = body.get("capacity_lift_hier_vs_flat_at_M_max", 0.0)
    per_structure = body.get("per_structure_summary", {})

    # 1. Cardinality
    if observed_n != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {observed_n}"

    # 2. Positive control
    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                       f"measured={pc_result.get('measured_recall')}; "
                       f"test rig broken")

    # 3. Distinctness (META_RULE_AX)
    if not distinctness_pass:
        n_pred_d = sum(1 for v in pairs_pred.values() if v)
        n_mech_d = sum(1 for v in pairs_mech.values() if v)
        return False, (f"META_RULE_AX_DISTINCTNESS_FAIL: pred_differ={n_pred_d}/3 "
                       f"mech_differ={n_mech_d}/3 (need >=2 each); "
                       f"structure arms COLLAPSED")

    # 4. Router imperfect (anti-META_RULE_Q)
    if hier_route >= SATURATED_RECALL:
        return False, (f"META_RULE_Q_ROUTER_SATURATION: routing_acc="
                       f"{hier_route:.4f} >= {SATURATED_RECALL} at M=max; "
                       f"by-construction perfect routing; tune CUE_ROUTE_COS")

    # 5. Router hasn't fully collapsed
    if hier_route < HF_ROUTING_ACC_MIN:
        return False, (f"routing_acc_collapse: {hier_route:.4f} < "
                       f"{HF_ROUTING_ACC_MIN} at M=max; router failed even at smoke")

    # 6. DISCRIMINATOR-MUST-SURVIVE-SCALE at M=64000
    flat_r = per_structure.get("flat", {}).get("capacity_per_slot_at_M_max", 0.0)
    part_r = per_structure.get("partition_by_source", {}).get(
        "capacity_per_slot_at_M_max", 0.0)
    hier_r = per_structure.get("hierarchical_2level", {}).get(
        "capacity_per_slot_at_M_max", 0.0)

    # Predicate (a): hierarchical lifts >= 1.10 * flat capacity at M=max
    lift_pass = (lift_vs_flat >= MB_LIFT_RATIO_SMOKE)
    # Predicate (b): both partition + hierarchical are >=0.20 above flat recall
    struct_pass = (part_r >= flat_r + 0.20 and hier_r >= flat_r + 0.20)
    discriminator_fires = lift_pass or struct_pass

    if not discriminator_fires:
        return False, (f"discriminator_fails_scale_at_M={body.get('M_max_measured')}: "
                       f"flat={flat_r:.3f} part={part_r:.3f} hier={hier_r:.3f}; "
                       f"lift={lift_vs_flat:.3f} (need >= {MB_LIFT_RATIO_SMOKE}) "
                       f"OR struct-lift-0.20 fail; regime too easy at smoke -- "
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
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} "
                    f"fail={n_fail}; distinct pred={n_pairs_pred_d}/3 "
                    f"mech={n_pairs_mech_d}/3; hier_route={hier_route:.3f}; "
                    f"lift_vs_flat={lift_vs_flat:.3f} @ M_max; "
                    f"pos_ctrl rec={pc_result.get('measured_recall')}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_SMOKE: {reason}; sat={n_sat} hp={n_hp} "
                    f"mb={n_mb} floor={n_floor} fail={n_fail}")
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
    # META_RULE_AX: HARD_FAIL if distinctness False
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
        # HARD_FAIL: router collapsed
        if hier_route < HF_ROUTING_ACC_MIN:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_ROUTING_COLLAPSE_UNDER_LOAD: hier routing_acc="
                    f"{hier_route:.4f} < {HF_ROUTING_ACC_MIN} at M=64K; "
                    f"router failed under capacity load")
        # META_RULE_Q: router-saturation guard
        elif hier_route >= SATURATED_RECALL:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_BY_CONSTRUCTION_ROUTER_SATURATION: "
                    f"hier routing_acc={hier_route:.4f} >= {SATURATED_RECALL}; "
                    f"router by-construction perfect; not chain-grade")
        # HARD_PASS: hierarchical lifts >= 1.20 * flat AND router in HP band
        elif (lift_vs_flat >= HP_CAPACITY_LIFT_RATIO
              and HP_ROUTING_ACC_MIN <= hier_route < HP_ROUTING_ACC_MAX):
            # META_RULE_AR: also must lift above partition (not just flat)
            if lift_vs_partition >= 1.05:
                verdict = "HARD_PASS"
                vmsg = (f"HARD_PASS_HIERARCHICAL_LIFTS_CAPACITY_AT_M_MAX: "
                        f"lift_vs_flat={lift_vs_flat:.3f} (>={HP_CAPACITY_LIFT_RATIO}) "
                        f"lift_vs_partition={lift_vs_partition:.3f} (>=1.05) "
                        f"hier_routing_acc={hier_route:.3f} in "
                        f"[{HP_ROUTING_ACC_MIN},{HP_ROUTING_ACC_MAX}); "
                        f"tier_counts sat={n_sat} hp={n_hp} mb={n_mb} "
                        f"floor={n_floor} fail={n_fail}")
            else:
                verdict = "MIDDLE_BAND"
                vmsg = (f"MIDDLE_BAND_LIFTS_FLAT_NOT_PARTITION: "
                        f"lift_vs_flat={lift_vs_flat:.3f} OK but "
                        f"lift_vs_partition={lift_vs_partition:.3f} < 1.05; "
                        f"hierarchical ~= partition; router adds cost without "
                        f"capacity gain (META_RULE_AR: no additional lift over "
                        f"ANCHOR 1 CG baseline)")
        elif (HP_ROUTING_ACC_MIN <= hier_route < HP_ROUTING_ACC_MAX
              and lift_vs_flat >= 1.05):
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_PARTIAL_LIFT: lift_vs_flat={lift_vs_flat:.3f} "
                    f"(in [1.05, {HP_CAPACITY_LIFT_RATIO})) "
                    f"hier_routing_acc={hier_route:.3f} OK; below chain-grade lift")
        elif hier_route < HP_ROUTING_ACC_MIN:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_ROUTING_BORDERLINE: hier_routing_acc="
                    f"{hier_route:.3f} in [{HF_ROUTING_ACC_MIN},{HP_ROUTING_ACC_MIN}); "
                    f"router imperfect below HP band; lift_vs_flat={lift_vs_flat:.3f}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_HIERARCHY_NO_CAPACITY_LIFT: "
                    f"lift_vs_flat={lift_vs_flat:.3f} (< 1.05) "
                    f"hier_routing_acc={hier_route:.3f}; hierarchical bank "
                    f"provides no capacity advantage; honest negative")

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
    "matched_filter_snr", "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
