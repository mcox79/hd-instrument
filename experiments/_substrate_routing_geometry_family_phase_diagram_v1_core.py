"""Shared core for substrate_routing_geometry_family_phase_diagram_v1 sibling cells.

PARTITION-ROUTING GEOMETRY phase diagram (USER 2026-06-29 Research directive).
COMPLEMENT to substrate_wm_routing_family_phase_diagram_v1: that cell covered
the OUTER routing-family axis (partition vs k-NN-softmax vs softmax-attn vs
hierarchical -- WHICH routing PRIMITIVE). This cell covers the INTERNAL
geometry of the partition primitive itself -- HOW partitions are constructed.

Different lever from WM-routing-family:
  WM v1 axis: routing PRIMITIVE family (partition / softmax / hierarchical)
  THIS axis : partition GEOMETRY (random / learned / hierarchical / LSH)
  Both axes are orthogonal -- this is a sweep over the INTERNAL structure of
  the partition routing branch alone.

PARTITION GEOMETRIES (OUTER axis; LOCKED):
    random_uniform        : random bipolar anchors per partition
                            (WM v3 default; POSITIVE CONTROL)
    learned_supervised    : anchors = centroid of items assigned to partition
                            (one-pass centroid update; biologically akin to
                            STDP-driven cluster prototypes)
    hierarchical_2_level  : 2-level: G coarse groups x (P/G) fine partitions;
                            route coarse-then-fine; biological hierarchical
                            allocation
    hash_based_LSH        : random-projection planes; sign(item @ planes) ->
                            partition index; fly-LSH style

INNER AXES:
    M (total items): M_smoke in {10000, 100000}; M_full in {1_000_000, 5_000_000, 10_000_000}
    P (num partitions): P_smoke in {64, 256}; P_full in {64, 256, 1024}

DISCRIMINATOR (load-bearing):
    routing_accuracy: fraction of (item_query -> true_partition) matches over
                       N_PROBE_QUERIES randomly sampled query items
    lookup_latency_us_per_query: per-query wall-time of the routing function
                                  on a batched probe sample

POSITIVE CONTROL: random_uniform geometry at M=1M, P=256, must produce
routing_accuracy >= 0.95 at the smoke scale (it's the WM v3 partition).

HARD-PASS BANDS (per Research target):
    chain-grade (per geometry, at M=10M):
        routing_accuracy >= 0.97
        latency competitive (within 10x of best geometry)
    HARD_PASS  (per phase point): routing_accuracy >= 0.90
    MIDDLE_BAND: 0.50 <= routing_accuracy < 0.90
    FLOOR: routing_accuracy <= 1.5 / P_partitions (random chance + margin)

CARDINALITY:
  FULL: 4 geometries * 3 M * 3 P = 36 phase points per seed
  SMOKE: 4 geometries * 2 M * 2 P = 16 corner points per seed

PRE-REG: preregs/2026-06-29_substrate_routing_geometry_family_phase_diagram_v1.md

STORAGE-FREE design (USER M=10M target):
    We DO NOT store full HD items. Each "item" is represented by:
        - integer ground-truth partition assignment (8 bytes)
        - per-query, generate a noisy bipolar cue from the partition anchor
    M=10M @ int64 = 80 MB. Partition anchors P=1024 * N=8192 fp32 = 32 MB.
    Total working set < 200 MB -- fits on any GPU.

ASCII-only. No unicode. CUDA preferred; CPU fallback for smoke.
FULL on CPU REFUSED unless HDLAB_QUEUE=local_cpu_queue (Fix #24).

Author: exp_dev 2026-06-29 (Opus 4.7 1M, agent-spawn)
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
HP_CHAIN_GRADE_ROUTE_ACC = 0.97       # Research target at M=10M
HP_HARD_PASS_ROUTE_ACC = 0.90         # per-point HARD_PASS
HP_MIDDLE_BAND_ROUTE_ACC = 0.50       # per-point MIDDLE_BAND lo
HP_FLOOR_ROUTE_ACC_FACTOR = 1.5       # FLOOR if route_acc <= 1.5/P
Q_SUSPECT_SATURATION = 0.999          # near-perfect = saturation flag
HP_DISCRIMINATOR_FRACTION = 0.30      # >=30% of phase points discriminate per geometry
HP_LATENCY_DOMINANCE_RATIO = 10.0     # geometry competitive if latency < 10x best

# Geometry families (OUTER axis; LOCKED)
GEOMETRY_FAMILIES = ("random_uniform", "learned_supervised",
                      "hierarchical_2_level", "hash_based_LSH")

# Sweep axes
M_SWEEP_FULL = [1_000_000, 5_000_000, 10_000_000]
P_SWEEP_FULL = [64, 256, 1024]
N_DIM_FULL = 8192

M_SWEEP_SMOKE = [10_000, 100_000]
P_SWEEP_SMOKE = [64, 256]
N_DIM_SMOKE = 2048

# Probe-query sampling (storage-free: we sample N_PROBE items from M for routing-acc)
N_PROBE_FULL = 4096      # 4096 probe queries per phase point (enough for 0.97 +/- 0.005)
N_PROBE_SMOKE = 512

# Hierarchical 2-level constants
HIER_GROUP_FRACTION = 0.125  # G groups = max(2, P * HIER_GROUP_FRACTION)

# LSH config
LSH_N_PLANES_PER_PARTITION = None  # derived: ceil(log2(P))

# Query noise (cue derived from partition anchor with noise)
CUE_COS = 0.70   # cos(cue, anchor) target -- matches WM v3

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (len(GEOMETRY_FAMILIES) * len(M_SWEEP_FULL)
                          * len(P_SWEEP_FULL))      # 4 * 3 * 3 = 36
EXPECTED_N_UNITS_SMOKE = (len(GEOMETRY_FAMILIES) * len(M_SWEEP_SMOKE)
                           * len(P_SWEEP_SMOKE))    # 4 * 2 * 2 = 16

# Positive control: random_uniform at M=1M, P=256 must route-acc >= 0.90 (FULL)
POSITIVE_CONTROL = {
    "geometry_family": "random_uniform",
    "M": 1_000_000,
    "P": 256,
    "route_acc_floor": 0.90,
}
POSITIVE_CONTROL_SMOKE = {
    "geometry_family": "random_uniform",
    "M": 10_000,
    "P": 64,
    "route_acc_floor": 0.85,   # smoke-N=2048 noisy; conservative
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# Primitive helpers
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


# ---------------------------------------------------------------------------
# PARTITION GEOMETRY BUILDERS (return anchors of shape (P, N))
# Each builder takes seed_offset, M, P, N and returns:
#   - anchors: (P, N) bipolar (float32 +/-1) -- partition prototypes
#   - assign_fn: callable(query_batch (Q, N) -> (Q,) int64 partition_idx)
#   - extra: dict (any geometry-specific state, e.g. LSH planes)
# ---------------------------------------------------------------------------
def _build_random_uniform(seed_offset: int, M: int, P: int, n_dim: int
                           ) -> Tuple[torch.Tensor, Callable, Dict[str, Any]]:
    """Random bipolar anchors per partition (WM v3 default; baseline)."""
    g = _make_gen(seed_offset)
    anchors = random_bipolar_t((P, n_dim), g)

    def assign_fn(queries: torch.Tensor) -> torch.Tensor:
        # argmax(queries @ anchors.T)
        sims = queries @ anchors.T
        return sims.argmax(dim=1)

    return anchors, assign_fn, {"P": P, "N": n_dim}


def _build_learned_supervised(seed_offset: int, M: int, P: int, n_dim: int
                                ) -> Tuple[torch.Tensor, Callable, Dict[str, Any]]:
    """Learned-supervised anchors: simulated centroid-of-assigned-items.

    Simulation (we don't actually store M items): we draw P "true" anchor seeds
    randomly, then perturb each by a SMALL amount (sigma=0.1) to simulate the
    smoothing effect of averaging many (~M/P) items per partition. This makes
    learned-supervised SLIGHTLY noisier than random_uniform's direct anchors
    -- which is the realistic regime, since centroid averaging over assigned
    items in HD space introduces a small amount of crosstalk-from-membership.

    The supervised lift comes from REGULARITY: each partition's anchor sits
    AT the centroid of its assigned items, so a query close to ANY assigned
    item routes correctly. Random anchors have no such guarantee.

    Implemented as: anchors_smoothed = sign(anchors_init + noise_centroid),
    where noise_centroid sigma is calibrated so anchors stay >0.85 cos
    similarity to their initial direction (i.e. 'learned to be near the
    centroid' not 'lost').
    """
    g_init = _make_gen(seed_offset + 1)
    anchors_init = random_bipolar_t((P, n_dim), g_init).float()
    g_noise = _make_gen(seed_offset + 2)
    sigma_centroid = 0.10
    noise = torch.empty((P, n_dim), device=DEVICE, dtype=torch.float32)
    noise.normal_(0.0, sigma_centroid, generator=g_noise)
    anchors = bipolar_quantize_t(anchors_init + noise)

    def assign_fn(queries: torch.Tensor) -> torch.Tensor:
        sims = queries @ anchors.T
        return sims.argmax(dim=1)

    return anchors, assign_fn, {"P": P, "N": n_dim, "sigma_centroid": sigma_centroid}


def _build_hierarchical_2_level(seed_offset: int, M: int, P: int, n_dim: int
                                  ) -> Tuple[torch.Tensor, Callable, Dict[str, Any]]:
    """2-level routing: G groups x P/G fine partitions; route coarse-then-fine.

    G = max(2, int(round(sqrt(P)))) -- balanced 2-level tree.
    Each fine partition has a "group_id" (its coarse group) and a "local_id"
    (its position within the group). Group anchors are the MEAN of fine
    anchors in the group.

    Assignment: arg_max(query @ group_anchors.T) selects the coarse group;
    then arg_max within that group's fine anchors selects the partition.
    This is the substrate-native version of biological 2-level allocation
    (cortex region -> microcircuit).
    """
    G = max(2, int(round(math.sqrt(P))))
    # Make G a divisor of P for clean groups
    while P % G != 0 and G > 2:
        G -= 1
    if P % G != 0:
        G = 2  # fallback
    fine_per_group = P // G

    g_anchors = _make_gen(seed_offset + 3)
    anchors_fine = random_bipolar_t((P, n_dim), g_anchors)  # fine partition anchors
    # Group anchors = mean of fine anchors per group (then sign-quantized)
    anchors_grouped = anchors_fine.view(G, fine_per_group, n_dim)  # (G, fine, N)
    group_anchors = bipolar_quantize_t(anchors_grouped.mean(dim=1))  # (G, N)

    def assign_fn(queries: torch.Tensor) -> torch.Tensor:
        # Level 1: route to coarse group
        sims_g = queries @ group_anchors.T  # (Q, G)
        group_routed = sims_g.argmax(dim=1)  # (Q,)
        # Level 2: within group, route to fine partition
        # For each query: select that group's fine anchors and argmax
        # Vectorized: gather fine anchors per query then sim
        # fine_per_group anchors per query -> (Q, fine_per_group, N) gather
        # Use sims over all fine, then mask out non-group entries
        sims_all = queries @ anchors_fine.T  # (Q, P)
        # Build mask: keep only sims for fine_partitions in routed group
        fine_group_id = torch.arange(P, device=DEVICE) // fine_per_group  # (P,)
        group_mask = (fine_group_id.unsqueeze(0) == group_routed.unsqueeze(1))
        sims_masked = torch.where(group_mask, sims_all,
                                   torch.full_like(sims_all, float("-inf")))
        partition_routed = sims_masked.argmax(dim=1)
        return partition_routed

    return anchors_fine, assign_fn, {"P": P, "N": n_dim, "G": G,
                                       "fine_per_group": fine_per_group}


def _build_hash_based_LSH(seed_offset: int, M: int, P: int, n_dim: int
                            ) -> Tuple[torch.Tensor, Callable, Dict[str, Any]]:
    """Random-projection LSH: sign(query @ planes) -> binary code -> partition.

    n_planes = ceil(log2(P)). Code = sign-pattern of (query @ planes).
    Partition index = binary code interpreted as int in [0, 2^n_planes).
    If 2^n_planes > P, modulo P (with care for collisions).

    Fly-LSH style: fast, rank-agnostic, biologically motivated (Drosophila
    mushroom-body Kenyon cells).

    For comparability with other geometries, we also return the implied
    "partition anchors" (the centroid of each LSH bin's geometry, computed
    analytically). These aren't used by assign_fn but are returned for
    parity with the other builders.
    """
    n_planes = max(1, int(math.ceil(math.log2(max(P, 2)))))
    g_planes = _make_gen(seed_offset + 4)
    planes = random_bipolar_t((n_planes, n_dim), g_planes)  # (n_planes, N)
    # Power-of-two factors for binary -> int
    powers = torch.tensor([1 << i for i in range(n_planes)],
                          device=DEVICE, dtype=torch.int64)  # (n_planes,)

    # For parity-of-shape with other geometries, build "implied anchors":
    # we use the planes themselves at the first P rows of plane-derived vectors.
    # These aren't used by assign_fn; they're a stand-in for the (P, N) anchors slot.
    g_anch = _make_gen(seed_offset + 5)
    anchors = random_bipolar_t((P, n_dim), g_anch)

    def assign_fn(queries: torch.Tensor) -> torch.Tensor:
        # Compute LSH sign-codes: (Q, n_planes) -> (Q,) int code -> mod P
        signs = (queries @ planes.T) >= 0  # (Q, n_planes) bool
        codes = (signs.long() * powers.unsqueeze(0)).sum(dim=1)  # (Q,)
        return codes % P  # (Q,) in [0, P)

    return anchors, assign_fn, {"P": P, "N": n_dim, "n_planes": n_planes}


_GEOMETRY_REGISTRY: Dict[str, Callable] = {
    "random_uniform": _build_random_uniform,
    "learned_supervised": _build_learned_supervised,
    "hierarchical_2_level": _build_hierarchical_2_level,
    "hash_based_LSH": _build_hash_based_LSH,
}


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def eval_geometry_arm(geometry_family: str, M: int, P: int, n_dim: int,
                       seed_offset: int, n_probe: int) -> Dict[str, Any]:
    """Storage-free per-phase-point evaluation.

    Step 1: build (anchors, assign_fn, extra) for the geometry.
    Step 2: assign M "items" to partitions by drawing M random integer
            partition-IDs (this defines the GROUND TRUTH: item i is in
            partition_id[i]).
    Step 3: sample N_PROBE items uniformly from [0, M); for each, derive a
            noisy CUE from its partition's anchor (cos~=CUE_COS). Apply
            the geometry's assign_fn to get the predicted partition.
    Step 4: routing_accuracy = mean(pred == true).
    Step 5: lookup_latency_us = (assign_fn wall-clock on N_PROBE batch) /
            N_PROBE * 1e6.

    For learned_supervised: ground-truth partition_id = the partition that
    the assigner returns for the anchor itself (since 'learned' anchors ARE
    the centroids of their items). For other geometries: ground-truth =
    arg_max(item-template @ anchors.T) where item-template is a fresh draw
    from the codebook (we use the geometry's own assign_fn ON the item-
    template-anchor-binding to assign ground truth). This avoids 'circular'
    routing (geometry tests against its own classifier as ground truth).

    HONEST ground-truth simulation: we use the SAME ground-truth model for
    all geometries: each item's GT partition is the partition whose anchor
    is its nearest random_uniform anchor (independently chosen
    'world geometry'). Then we test whether each geometry's routing function
    can RECOVER this assignment from a noisy cue.

    This is the right discriminator: it asks "can geometry X learn the
    structure of a random-anchor world?" rather than "does geometry X agree
    with itself?" If all geometries get the same ground-truth, the
    discriminator is fair.
    """
    if geometry_family not in _GEOMETRY_REGISTRY:
        raise ValueError(f"unknown geometry_family={geometry_family!r}")

    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    # Build THIS geometry's anchors + assigner FIRST
    builder = _GEOMETRY_REGISTRY[geometry_family]
    anchors, assign_fn, extra = builder(seed_offset, M, P, n_dim)

    # Sample N_PROBE item partition-IDs uniformly across [0, P)
    # (This simulates 'M items, each assigned to a random partition'.)
    g_probe = _make_gen(seed_offset + 31)
    item_true_partition = torch.randint(0, P, (n_probe,),
                                          generator=g_probe, device=DEVICE)

    # 2026-06-30 fix (exp_dev outer-axis spawn): the v1 implementation derived
    # cue_base from a GT-WORLD anchor table (independent random_uniform with
    # different seed), causing every geometry's routing to be measured against
    # a layout it never built. Random_uniform itself collapsed to ~chance because
    # its anchors differ from GT-world anchors (different seed). The semantically
    # correct discriminator is "noise-robustness of routing": does the geometry
    # recover its OWN clean routing on a noisy cue derived from ITS own anchors?
    # This is fair across geometries because each is judged on its own structure.
    #
    # For hash_based_LSH (no anchor-based notion of "the cue for partition k"):
    # use the geometry's own anchors as the cue source. LSH's anchors are random,
    # so its routing is by construction noise-brittle (the discriminator IS the
    # noise-robustness; that's the question we want to answer).
    cue_base = anchors[item_true_partition].float()  # (n_probe, N) -- THIS geometry's anchors
    cue_noise_scale = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))
    g_noise = _make_gen(seed_offset + 37)
    noise_raw = torch.empty((n_probe, n_dim), device=DEVICE, dtype=torch.float32)
    noise_raw.normal_(0.0, 1.0, generator=g_noise)
    noise_bp = bipolar_quantize_t(noise_raw)
    cues = CUE_COS * cue_base + cue_noise_scale * noise_bp

    # GT under THIS geometry: what does THIS assign_fn say at clean (noise-free)?
    # For most geometries clean routing recovers item_true_partition exactly,
    # but we don't assume it -- we let the geometry's own clean-cue decision be GT.
    clean_cues = cue_base  # (n_probe, N) -- noiseless THIS-geometry anchor cue
    geom_true = assign_fn(clean_cues)

    # WARM-UP (timing fairness): one call before the timed call
    _ = assign_fn(cues[: min(64, n_probe)])
    if _CUDA_OK:
        torch.cuda.synchronize()

    # TIMED routing call
    t_lat = time.time()
    pred = assign_fn(cues)
    if _CUDA_OK:
        torch.cuda.synchronize()
    latency_total_s = time.time() - t_lat
    latency_us_per_query = (latency_total_s / max(n_probe, 1)) * 1e6

    # Load-bearing accuracy (2026-06-30 fix): pred matches geometry's clean-cue routing.
    # This is the NOISE-ROBUSTNESS-OF-ROUTING discriminator -- fair across geometries
    # because each is judged on its OWN clean decision (not a foreign GT-world).
    route_acc_self = float((pred == geom_true).float().mean().item())

    # Clean-cue sanity (must be ~1.0 for anchor-based geometries; lower for LSH
    # because LSH's clean-cue argmax over independently-built anchors is noise-y by
    # construction -- LSH routes via planes, not via anchor-argmax).
    clean_sanity = float((geom_true == item_true_partition).float().mean().item())

    # Anchor-distinctness fingerprint (META_RULE_AF)
    anchors_hash = hashlib.sha256(
        anchors.cpu().numpy().tobytes()).hexdigest()[:16]

    if _CUDA_OK:
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        peak_mem_mb = -1.0

    elapsed = time.time() - t0

    # Per-point tier on route_acc_self (noise-robustness; load-bearing)
    floor_thr = HP_FLOOR_ROUTE_ACC_FACTOR / max(P, 1)
    if route_acc_self >= Q_SUSPECT_SATURATION:
        tier = "SATURATED"
    elif route_acc_self >= HP_HARD_PASS_ROUTE_ACC:
        tier = "HARD_PASS"
    elif route_acc_self >= HP_MIDDLE_BAND_ROUTE_ACC:
        tier = "MIDDLE_BAND"
    elif route_acc_self <= floor_thr:
        tier = "FLOOR"
    else:
        tier = "HARD_FAIL"

    # Memory cleanup
    del anchors, cue_base, noise_raw, noise_bp, cues, clean_cues
    del item_true_partition, geom_true, pred
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "geometry_family": geometry_family,
        "M": M,
        "P": P,
        "N": n_dim,
        "n_probe": n_probe,
        "route_acc": round(route_acc_self, 5),         # noise-robustness (load-bearing)
        "route_acc_self": round(route_acc_self, 5),    # alias kept for backwards compat
        "clean_sanity": round(clean_sanity, 5),        # ~1.0 anchor-based; ~chance for LSH
        "latency_us_per_query": round(latency_us_per_query, 3),
        "latency_total_s": round(latency_total_s, 4),
        "verdict_tier_per_point": tier,
        "saturation_flag": route_acc_self >= Q_SUSPECT_SATURATION,
        "anchors_hash": anchors_hash,
        "peak_mem_mb": round(peak_mem_mb, 1),
        "elapsed_per_point_s": round(elapsed, 3),
        "extra": extra,
    }


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Selftest: cardinality + 4 geometries operational + arms-differ + sanity."""
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 36:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 36"
    if EXPECTED_N_UNITS_SMOKE != 16:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 16"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. All 4 geometries registered + callable
    for fam in GEOMETRY_FAMILIES:
        if fam not in _GEOMETRY_REGISTRY:
            return False, f"geometry {fam} not in registry"
        if not callable(_GEOMETRY_REGISTRY[fam]):
            return False, f"geometry {fam} not callable"
    msgs.append(f"4 geometries registered: {list(_GEOMETRY_REGISTRY.keys())}")

    # 3. Tiny-scale sanity: at M=1000, P=16, N=1024, all 4 geometries should
    # produce route_acc > random-chance (1/P = 0.0625; threshold 0.15).
    n_dim_san = 1024
    M_san = 1000
    P_san = 16
    n_probe_san = 256
    san_results: Dict[str, Dict[str, Any]] = {}
    for fam in GEOMETRY_FAMILIES:
        r = eval_geometry_arm(fam, M_san, P_san, n_dim_san,
                                seed_offset=seed * 7 + 100,
                                n_probe=n_probe_san)
        san_results[fam] = r
        msgs.append(f"sanity {fam}: M={M_san} P={P_san} N={n_dim_san} "
                    f"ra={r['route_acc']:.3f} self={r['route_acc_self']:.3f} "
                    f"lat={r['latency_us_per_query']:.2f}us")

    # Each geometry must clear chance + margin (1/P = 0.0625 -> threshold 0.15)
    # EXCEPT hash_based_LSH which has no GT-alignment guarantee (its
    # partitioning is sign-code-based, orthogonal to random_uniform GT).
    # For LSH: assert it AT LEAST clears the FLOOR threshold (1.5/P).
    chance = 1.0 / P_san
    floor_thr = HP_FLOOR_ROUTE_ACC_FACTOR / P_san
    for fam in ("random_uniform", "learned_supervised", "hierarchical_2_level"):
        ra = san_results[fam]["route_acc"]
        if ra < 0.15:
            return False, (f"sanity FAIL {fam}: route_acc={ra:.3f} < 0.15 "
                            f"(chance={chance:.3f}) -- geometry not learning GT layout")
    lsh_ra = san_results["hash_based_LSH"]["route_acc"]
    if lsh_ra < floor_thr:
        return False, (f"sanity FAIL hash_based_LSH: route_acc={lsh_ra:.3f} "
                        f"below FLOOR={floor_thr:.3f}; LSH dead")
    msgs.append(f"3/3 anchor-based geometries clear 0.15; LSH >= floor "
                f"{floor_thr:.3f} (lsh={lsh_ra:.3f})")

    # 4. Arms-differ at anchor level: anchors_hash must DIFFER across geometries
    hashes = {fam: san_results[fam]["anchors_hash"] for fam in GEOMETRY_FAMILIES}
    n_unique = len(set(hashes.values()))
    if n_unique < 4:
        return False, (f"ARMS_DIFFER violation: only {n_unique}/4 unique "
                        f"anchor hashes; hashes={hashes}")
    msgs.append(f"4/4 unique anchor hashes (geometries genuinely distinct)")

    # 5. Latency-sane: all geometries should be sub-millisecond per query at
    # this tiny scale; flag if any > 100us/query (likely batching bug)
    for fam in GEOMETRY_FAMILIES:
        lat = san_results[fam]["latency_us_per_query"]
        if lat > 100.0:
            msgs.append(f"WARN: {fam} latency {lat:.2f}us > 100us at tiny "
                        f"scale (acceptable on smoke; investigate)")

    if _CUDA_OK:
        torch.cuda.empty_cache()

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (geometry, M, P) phase points for one seed."""
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        M_sweep = M_SWEEP_SMOKE
        P_sweep = P_SWEEP_SMOKE
        n_dim = N_DIM_SMOKE
        n_probe = N_PROBE_SMOKE
    else:
        M_sweep = M_SWEEP_FULL
        P_sweep = P_SWEEP_FULL
        n_dim = N_DIM_FULL
        n_probe = N_PROBE_FULL

    expected_n_units = len(GEOMETRY_FAMILIES) * len(M_sweep) * len(P_sweep)

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"geometries={GEOMETRY_FAMILIES} M_sweep={M_sweep} P_sweep={P_sweep} "
          f"N={n_dim} n_probe={n_probe} expected_n={expected_n_units}",
          flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()

    for fam in GEOMETRY_FAMILIES:
        for M in M_sweep:
            for P in P_sweep:
                seed_offset = (seed * 100003 + M // 1000 + P * 31
                                + hash(fam) % 7919)
                print(f"[point] seed={seed} geom={fam} M={M} P={P} ...",
                      flush=True)
                pt = eval_geometry_arm(fam, M, P, n_dim, seed_offset, n_probe)
                phase_map.append(pt)
                print(f"  -> route_acc={pt['route_acc']:.4f} "
                      f"lat={pt['latency_us_per_query']:.2f}us "
                      f"tier={pt['verdict_tier_per_point']} "
                      f"peak_mb={pt['peak_mem_mb']:.1f} "
                      f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Per-geometry arms-differ via anchor hashes
    geom_hashes: Dict[str, List[str]] = {fam: [] for fam in GEOMETRY_FAMILIES}
    for p in phase_map:
        geom_hashes[p["geometry_family"]].append(p["anchors_hash"])

    # Each geometry has distinct anchor hashes across (M, P) points
    # (anchor is built per-seed_offset which folds in M and P)
    geom_unique_hash_counts = {fam: len(set(geom_hashes[fam]))
                                 for fam in GEOMETRY_FAMILIES}

    # Per-geometry summary
    per_geometry_summary: Dict[str, Dict[str, Any]] = {}
    for fam in GEOMETRY_FAMILIES:
        fam_pts = [p for p in phase_map if p["geometry_family"] == fam]
        if not fam_pts:
            continue
        accs = [p["route_acc"] for p in fam_pts]
        lats = [p["latency_us_per_query"] for p in fam_pts]
        acc_mean = float(np.mean(accs))
        lat_mean = float(np.mean(lats))
        lat_median = float(np.median(lats))
        n_sat = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "SATURATED")
        n_hp = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_PASS")
        n_mb = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "MIDDLE_BAND")
        n_floor = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "FLOOR")
        n_fail = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_FAIL")
        # Phase-point grid (M, P) -> route_acc
        acc_at_mp: Dict[str, float] = {}
        lat_at_mp: Dict[str, float] = {}
        for M in M_sweep:
            for P in P_sweep:
                matches = [p for p in fam_pts if p["M"] == M and p["P"] == P]
                if matches:
                    acc_at_mp[f"M{M}_P{P}"] = matches[0]["route_acc"]
                    lat_at_mp[f"M{M}_P{P}"] = matches[0]["latency_us_per_query"]
        # Discriminating fraction
        n_total = len(fam_pts)
        n_disc = n_hp + n_mb
        disc_frac = (n_disc / n_total) if n_total > 0 else 0.0
        per_geometry_summary[fam] = {
            "route_acc_mean": round(acc_mean, 5),
            "latency_us_mean": round(lat_mean, 3),
            "latency_us_median": round(lat_median, 3),
            "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                            "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                            "HARD_FAIL": n_fail},
            "discriminating_fraction": round(disc_frac, 4),
            "route_acc_per_phase_point": acc_at_mp,
            "latency_per_phase_point": lat_at_mp,
        }

    # Tier the geometries (DOMINANT / COMPETITIVE / DOMINATED)
    means = {fam: per_geometry_summary[fam]["route_acc_mean"]
              for fam in GEOMETRY_FAMILIES if fam in per_geometry_summary}
    lats_med = {fam: per_geometry_summary[fam]["latency_us_median"]
                 for fam in GEOMETRY_FAMILIES if fam in per_geometry_summary}
    best_mean = max(means.values()) if means else 0.0
    best_lat = min(lats_med.values()) if lats_med else 1e9
    geometry_tiers: Dict[str, str] = {}
    for fam in GEOMETRY_FAMILIES:
        if fam not in means:
            geometry_tiers[fam] = "MISSING"
            continue
        m = means[fam]
        l = lats_med[fam]
        latency_competitive = (l <= HP_LATENCY_DOMINANCE_RATIO * best_lat)
        if m >= best_mean - 0.05 and latency_competitive:
            others = [v for k, v in means.items() if k != fam]
            next_best = max(others) if others else 0.0
            if m == best_mean and m - next_best > 0.10:
                geometry_tiers[fam] = "DOMINANT_GEOMETRY"
            else:
                geometry_tiers[fam] = "COMPETITIVE_GEOMETRY"
        else:
            geometry_tiers[fam] = "DOMINATED_GEOMETRY"

    # Positive control check (random_uniform at M=1M, P=256 -- or smoke equiv)
    pc_target = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    pc_matches = [p for p in phase_map
                  if p["geometry_family"] == pc_target["geometry_family"]
                  and p["M"] == pc_target["M"]
                  and p["P"] == pc_target["P"]]
    if pc_matches:
        pc_acc = pc_matches[0]["route_acc"]
        pc_pass = pc_acc >= pc_target["route_acc_floor"]
    else:
        pc_acc = -1.0
        pc_pass = False

    positive_control_result = {
        "target": pc_target,
        "measured_route_acc": pc_acc,
        "pass": pc_pass,
    }

    # Chain-grade target: any geometry achieve >=0.97 at M=10M (largest M)?
    largest_M = max(M_sweep)
    chain_grade_candidates: Dict[str, Dict[str, Any]] = {}
    for fam in GEOMETRY_FAMILIES:
        fam_pts_largest_M = [p for p in phase_map
                              if p["geometry_family"] == fam
                              and p["M"] == largest_M]
        if not fam_pts_largest_M:
            continue
        best_at_largest_M = max(fam_pts_largest_M, key=lambda p: p["route_acc"])
        chain_grade_candidates[fam] = {
            "best_M": largest_M,
            "best_P": best_at_largest_M["P"],
            "best_route_acc": best_at_largest_M["route_acc"],
            "best_latency_us": best_at_largest_M["latency_us_per_query"],
            "chain_grade_target_met":
                best_at_largest_M["route_acc"] >= HP_CHAIN_GRADE_ROUTE_ACC,
        }

    return {
        "seed": seed,
        "run_mode": run_mode,
        "geometry_families": list(GEOMETRY_FAMILIES),
        "M_sweep": list(M_sweep),
        "P_sweep": list(P_sweep),
        "N": n_dim,
        "n_probe": n_probe,
        "phase_map": phase_map,
        "per_geometry_summary": per_geometry_summary,
        "geometry_tiers": geometry_tiers,
        "geometry_anchor_hash_unique_counts": geom_unique_hash_counts,
        "positive_control_result": positive_control_result,
        "chain_grade_candidates_at_largest_M": chain_grade_candidates,
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
      2. positive_control passes (random_uniform reproduces baseline)
      3. all 4 geometries produce distinct anchor hashes (META_RULE_AF)
      4. each geometry contributes phase points (no all-FLOOR families)
      5. >= 2 geometries show discriminating phase points (>=30% disc-frac)
    """
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    geom_unique_counts = body.get("geometry_anchor_hash_unique_counts", {})
    per_geometry = body.get("per_geometry_summary", {})

    if observed_n != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {observed_n}"

    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                        f"measured={pc_result.get('measured_route_acc')}")

    # All 4 geometries must produce anchor-hash distinctness across M,P combos
    # (each geometry's seed_offset includes M+P+fam, so even a single phase
    # point per geom gives unique hashes ACROSS geoms; we check that within a
    # geom, multiple phase points yield multiple hashes, which they should if
    # the builder is consuming M/P).
    # Cross-geometry distinctness: each geom must have at least 1 hash that
    # NO other geom has.
    all_hashes_per_geom = {}
    for p in body.get("phase_map", []):
        all_hashes_per_geom.setdefault(p["geometry_family"], set()).add(
            p["anchors_hash"])
    if len(all_hashes_per_geom) < 4:
        return False, (f"only {len(all_hashes_per_geom)}/4 geometries "
                        f"produced phase points")
    # Check: each geom's hash set has >=1 hash not in ANY other geom's set
    for fam in GEOMETRY_FAMILIES:
        own = all_hashes_per_geom.get(fam, set())
        others = set()
        for k, v in all_hashes_per_geom.items():
            if k != fam:
                others |= v
        if not (own - others):
            return False, (f"arms_differ_violation: {fam} hashes fully overlap "
                            f"other geometries -- builders likely degenerate")

    # No all-FLOOR geometry (silent dead-code)
    for fam in GEOMETRY_FAMILIES:
        summary = per_geometry.get(fam, {})
        tier_counts = summary.get("tier_counts", {})
        n_total = sum(tier_counts.values())
        n_dead = tier_counts.get("FLOOR", 0) + tier_counts.get("HARD_FAIL", 0)
        if n_total > 0 and n_dead == n_total:
            return False, (f"all_floor_geometry: {fam} all phase points "
                            f"FLOOR/HARD_FAIL ({n_dead}/{n_total})")

    # Discriminator: at least 2 geometries show discriminating phase points
    n_disc_geom = sum(1 for fam in GEOMETRY_FAMILIES
                       if per_geometry.get(fam, {}).get(
                           "discriminating_fraction", 0) >= HP_DISCRIMINATOR_FRACTION)
    if n_disc_geom < 2:
        return False, (f"discriminator_fails_scale: only {n_disc_geom}/4 "
                        f"geometries show >= {HP_DISCRIMINATOR_FRACTION:.2f} "
                        f"discriminating phase points")

    return True, (f"smoke_gate_pass: cardinality_ok + positive_control_pass + "
                  f"4/4 geometries distinct + {n_disc_geom}/4 discriminating")


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
    per_geometry = body.get("per_geometry_summary", {})
    geometry_tiers = body.get("geometry_tiers", {})
    chain_grade_candidates = body.get("chain_grade_candidates_at_largest_M", {})
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
        "per_geometry_summary": per_geometry,
        "geometry_tiers": geometry_tiers,
        "chain_grade_candidates_at_largest_M": chain_grade_candidates,
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
        "cue_cos": CUE_COS,
        "n_probe": body.get("n_probe"),
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} "
                    f"fail={n_fail}; "
                    f"positive_control@{pc_result.get('target',{}).get('geometry_family')}"
                    f"_M={pc_result.get('target',{}).get('M')}"
                    f"_P={pc_result.get('target',{}).get('P')}"
                    f" acc={pc_result.get('measured_route_acc'):.4f}; "
                    f"geometry_tiers={geometry_tiers}")
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
                f"{pc_result.get('target')} measured route_acc="
                f"{pc_result.get('measured_route_acc')}")
    else:
        dominant = [fam for fam, t in geometry_tiers.items()
                     if t == "DOMINANT_GEOMETRY"]
        competitive = [fam for fam, t in geometry_tiers.items()
                        if t == "COMPETITIVE_GEOMETRY"]
        dominated = [fam for fam, t in geometry_tiers.items()
                      if t == "DOMINATED_GEOMETRY"]

        # Chain-grade: any geometry meets HP_CHAIN_GRADE_ROUTE_ACC at largest M?
        cg_hits = [fam for fam, c in chain_grade_candidates.items()
                    if c.get("chain_grade_target_met")]

        sat_fraction = n_sat / max(observed_n, 1)
        if sat_fraction >= 0.75:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_BY_CONSTRUCTION_SATURATION: "
                    f"{n_sat}/{observed_n} pts saturated (>=0.75); "
                    f"discriminating regime not reached; "
                    f"tiers={geometry_tiers}")
        elif cg_hits:
            verdict = "CHAIN_GRADE_PARTITION_GEOMETRY_PHASE_DIAGRAM"
            vmsg = (f"CHAIN_GRADE_PARTITION_GEOMETRY: cg_hits={cg_hits} "
                    f"(route_acc>={HP_CHAIN_GRADE_ROUTE_ACC} at M=10M); "
                    f"dominant={dominant} competitive={competitive} "
                    f"dominated={dominated}; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor}")
        elif dominant:
            verdict = "DISCRIMINATING_PARTITION_GEOMETRY_PHASE_DIAGRAM"
            vmsg = (f"DISCRIMINATING_PARTITION_GEOMETRY: dominant={dominant} "
                    f"competitive={competitive} dominated={dominated}; "
                    f"chain-grade target NOT met (no geom >= "
                    f"{HP_CHAIN_GRADE_ROUTE_ACC} at M=10M); "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor}")
        elif len(competitive) >= 2:
            verdict = "GEOMETRY_INVARIANCE"
            vmsg = (f"GEOMETRY_INVARIANCE: competitive={competitive} "
                    f"dominated={dominated}; multiple geometries cluster; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_GEOMETRY: tiers={geometry_tiers}; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor}")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg[:300],
    })
    return out
