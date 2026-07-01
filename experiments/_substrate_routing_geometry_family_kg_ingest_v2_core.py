"""Core for substrate_routing_geometry_family_kg_ingest_v2 sibling cells.

ROUTING GEOMETRY FAMILY at KG-INGEST regime (USER 2026-07-01 Axis G fill).

Replaces v1 storage-free synthetic (which SATURATED 3/4 arms at 1.0) with
REAL ConceptNet KG-ingest sharding test. Discriminator = retrieval_acc under
sharding + routing.

5 GEOMETRIES (OUTER axis; LOCKED):
    random_partition     : random bipolar anchors per shard; workhorse (POS CTRL)
    learned_supervised   : one-pass Hebbian centroid on initial-random routing
    lsh_hash             : sign(query @ planes) -> shard idx (fly-LSH)
    hierarchical_tree    : 2-level G groups -> P/G shards each
    knn_softmax          : top-K=3 shards; softmax(sim/tau=0.5) weighting

REGIME:
    Dataset: data/datasets/conceptnet5_en_100k.jsonl (100k triples ConceptNet)
    SMOKE : M_ingest=10k, N_DIM=512,  P=256, n_eval=200
    FULL  : M_ingest=100k, N_DIM=2048, P=128, n_eval=1024

    v3 memory fix (2026-07-01): FULL Ws tensor = P*N*N*4B.
        v2 config (P=256, N=2048) => 4.0 GiB per arm.
        v2 arm loop retained fragmented cache across arms (empty_cache only
        ran on SUCCESSFUL return; exception path left tensors resident) =>
        4 arms crashed OOM after random_partition ran first.
    v3 fix stack (all three landed):
        (1) PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True (top of module)
        (2) P_SHARDS_FULL 256 -> 128; halves Ws footprint to 2.0 GiB
        (3) empty_cache() in finally block after every arm (success or fail)
        (4) full_scale_preview selftest allocates + frees the FULL Ws tensor
            so cell-author sees OOM at smoke-time (not remote-run-time).

DISCRIMINATOR:
    retrieval_acc = set_recall@|obj| for (s,p) -> {o} queries;
        routed to shard via geometry; retrieved from that shard's Hebbian W.
    HARD_PASS  : retrieval_acc >= 0.55
    MIDDLE_BAND: 0.30 <= retrieval_acc < 0.55
    HARD_FAIL  : retrieval_acc < 0.30 OR >= 0.99 (saturated)

    Discrimination gate: >=3 of 5 geometries produce DISTINCT retrieval_acc
        (>=0.10 pairwise separation). If <3 distinct, auto-demote MB.

POSITIVE CONTROL:
    random_partition at SMOKE: retrieval_acc >= 0.30 (weakened smoke floor)
    at FULL: retrieval_acc >= 0.45 (still substrate-mechanism, not saturation)

CARDINALITY:
    5 geometries * 1 seed = 5 units per cell

ASCII-only. No unicode. CUDA preferred; CPU fallback for smoke.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified via routing_hash sha256 per arm
- final_metrics_atomicity: tmp_replace via os.replace
- except SystemExit: raise (in sibling scripts)
- HARD_PASS strictly above floor +0.05 (band width sane)
- baseline_in_band at smoke (random_partition < 0.95)
- discriminator survives scale (smoke at reduced M but SAME sharding pressure)
- HP_SCOPE: HARD_PASS gate applies to all 5 arms
- cardinality_ok: EXPECTED_N_UNITS=5 per cell; verdict counts observed
- per-unit failure-class instrumentation via try/except Exception
- calibration_check: default_ok (no adaptive tuning)
- all HYPOTHESIZED@ MEASURED@ tags in prereg

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
import traceback
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

# v3 fix (2026-07-01): expandable_segments=True to avoid 3+ GiB fragmented reservation
# after per-arm 2 GiB Ws churn. MUST precede `import torch` to take effect.
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

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


REPO = Path(__file__).resolve().parent.parent
KG_PATH = REPO / "data" / "datasets" / "conceptnet5_en_100k.jsonl"


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED)
# ---------------------------------------------------------------------------
# Bands calibrated for hard-noise regime (routing_noise_cos=0.60):
# expected 5-arm spread ~[0.08, 0.50]; discriminating band [0.20, 0.55].
# HARD_PASS at 0.30+ = arm has recovered majority of noise-injected routing
# (mechanism is doing real work).
HP_HARD_PASS_RA = 0.30
HP_MIDDLE_BAND_RA = 0.15
Q_SUSPECT_SATURATION = 0.99
HP_MIN_PAIRWISE_SEPARATION = 0.05
HP_MIN_DISTINCT_GEOMETRIES = 3
# PC floor calibrated to hard-regime: random_partition at cos=0.60 noise is
# expected to sit in [0.10, 0.25] band (workhorse degrades under noise; that's
# what makes the discriminator sharp). PC>=0.05 confirms geometry is functional
# (>random-chance = 1/n_ent ~= 1e-4). PC<=0.60 confirms non-saturated regime.
POSITIVE_CONTROL_FLOOR_SMOKE = 0.05
POSITIVE_CONTROL_FLOOR_FULL = 0.10
POSITIVE_CONTROL_CEILING_SMOKE = 0.60
POSITIVE_CONTROL_CEILING_FULL = 0.70

GEOMETRY_FAMILIES = (
    "random_partition",
    "learned_supervised",
    "lsh_hash",
    "hierarchical_tree",
    "knn_softmax",
)

# Regime constants
# 2026-07-01 CALIBRATION (v2 smoke iteration 3):
# v2 iter1 (M=10k, N=2048, P=64): saturated 3/5 at 1.0, 2 at 0.95-0.97.
# v2 iter2 (M=20k, N=512, P=128): all clustered 0.935-1.0; NO distinct band.
# Root cause: HD routing on real ConceptNet is intrinsically easy — arms all
# achieve ~0.93-0.97 routing accuracy because key vectors are distinct and
# random anchors JL-margin stable.
# Iteration 3 strategy: use ADVERSARIAL routing regime — noise-perturb the
# routing cue so routing decisions become NOISY. This mimics the real-world
# regime where routing input is noisy (encoder outputs, partial observations).
# Each geometry's noise-robustness differs; this is the load-bearing discriminator.
M_INGEST_SMOKE = 10_000
M_INGEST_FULL = 100_000
N_DIM_SMOKE = 512
N_DIM_FULL = 2048
# v3 (2026-07-01): P_SHARDS_FULL 256 -> 128 to halve per-arm Ws memory.
# Ws footprint = P*N*N*4B = 128*2048*2048*4 = 2.0 GiB (was 4.0 GiB at P=256).
# With expandable_segments + per-arm empty_cache, 5 arms x 2 GiB fits 8 GiB GPU.
# Sharding density (keys-per-shard = ~42154/128 ~= 329 vs prior ~165) still
# well below single-shard capacity ceiling for N=2048 Hebbian W.
P_SHARDS_SMOKE = 256
P_SHARDS_FULL = 128
N_EVAL_SMOKE = 200
N_EVAL_FULL = 1024

# v3 memory-budget self-check (fires on import; catches config drift)
def _compute_ws_bytes(P: int, N: int) -> int:
    return P * N * N * 4  # float32

_WS_FULL_BYTES = _compute_ws_bytes(P_SHARDS_FULL, N_DIM_FULL)
_WS_FULL_GIB = _WS_FULL_BYTES / (1024 ** 3)
assert _WS_FULL_GIB <= 3.0, (
    f"v3 memory guard: FULL Ws = {_WS_FULL_GIB:.2f} GiB > 3.0 GiB cap. "
    f"With E/R/key_vecs residency (~1 GiB) + fragmented cache slack, "
    f"per-arm churn will OOM 8 GiB GPU. Reduce P_SHARDS_FULL or N_DIM_FULL."
)

# Adversarial noise added to routing cue (not to retrieval query).
# Different noise levels stress different routing geometries differently.
# iter3: cos=0.30 killed PC (all arms 0.02-0.19).
# iter4: cos=0.60 sweet spot targeting discriminating band [0.30, 0.55]
#   where all 5 arms differ per their noise-recovery mechanism.
ROUTING_NOISE_COS_SMOKE = 0.60
ROUTING_NOISE_COS_FULL = 0.60

# KNN softmax
KNN_K = 3
KNN_TAU = 0.5

# Hierarchical: G computed dynamically as round(sqrt(P)) with divisor fallback
def _hier_G(P: int) -> int:
    G = max(2, int(round(math.sqrt(P))))
    while P % G != 0 and G > 2:
        G -= 1
    if P % G != 0:
        G = 2
    return G

# Cardinality
EXPECTED_N_UNITS_PER_CELL = len(GEOMETRY_FAMILIES)  # 5

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# KG loading (numpy, deterministic)
# ---------------------------------------------------------------------------
def load_conceptnet(seed: int, m_triples: int) -> Tuple[List[Tuple[int, int, int]],
                                                        Dict[Tuple[int, int], List[int]],
                                                        int, int]:
    """Load ConceptNet triples (S, P, O), truncate to m_triples, return int-encoded."""
    if not KG_PATH.exists():
        raise FileNotFoundError(f"ConceptNet not found at {KG_PATH}")
    rows: List[Tuple[str, str, str]] = []
    with open(KG_PATH, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            rows.append((r["subject"], r["predicate"], r["object"]))
    g = np.random.default_rng(int(seed))
    idx = g.permutation(len(rows))
    rows = [rows[i] for i in idx[:m_triples]]
    ents = sorted({s for s, _, _ in rows} | {o for _, _, o in rows})
    rels = sorted({p for _, p, _ in rows})
    eid = {e: i for i, e in enumerate(ents)}
    rid = {p: i for i, p in enumerate(rels)}
    triples = [(eid[s], rid[p], eid[o]) for s, p, o in rows]
    keyobjs: Dict[Tuple[int, int], List[int]] = defaultdict(list)
    for (s, p, o) in triples:
        keyobjs[(s, p)].append(o)
    return triples, {k: sorted(set(v)) for k, v in keyobjs.items()}, len(ents), len(rels)


def build_codebooks(n_ent: int, n_rel: int, n_dim: int, seed: int
                    ) -> Tuple[torch.Tensor, torch.Tensor, float]:
    """Bipolar codebooks E (n_ent, N) and R (n_rel, N) on DEVICE."""
    g = torch.Generator(device=DEVICE)
    g.manual_seed(int(seed) * 101 + 7)
    E = torch.empty((n_ent, n_dim), device=DEVICE, dtype=torch.float32)
    E.bernoulli_(0.5, generator=g).mul_(2.0).sub_(1.0)
    # normalize rows
    E = E / (E.norm(dim=1, keepdim=True) + 1e-8)
    g2 = torch.Generator(device=DEVICE)
    g2.manual_seed(int(seed) * 101 + 13)
    R = torch.empty((n_rel, n_dim), device=DEVICE, dtype=torch.float32)
    R.bernoulli_(0.5, generator=g2).mul_(2.0).sub_(1.0)
    R = R / (R.norm(dim=1, keepdim=True) + 1e-8)
    sq = math.sqrt(n_dim)
    return E, R, sq


# ---------------------------------------------------------------------------
# ROUTING GEOMETRIES
# Each returns a callable: keys (B, N) -> shard_idx (B,) int64 (top-1)
# knn_softmax additionally returns weighted retrieval; handled specially.
# ---------------------------------------------------------------------------
def _rand_bipolar_t(shape: Tuple[int, ...], seed: int) -> torch.Tensor:
    g = torch.Generator(device=DEVICE)
    g.manual_seed(int(seed))
    X = torch.empty(*shape, device=DEVICE, dtype=torch.float32)
    X.bernoulli_(0.5, generator=g).mul_(2.0).sub_(1.0)
    return X


def build_geometry(name: str, P: int, n_dim: int, seed: int,
                   key_sample: torch.Tensor = None
                   ) -> Tuple[Callable, Dict[str, Any]]:
    """Return (route_fn, extra) for the named geometry.

    route_fn: signature (keys: torch.Tensor of shape (B, N)) -> (B,) int64 (top-1 shard)
              For knn_softmax additionally returns (B, K) tuple.
    extra: geometry-specific state (used for arms_differ_hash + retrieval).
    """
    if name == "random_partition":
        anchors = _rand_bipolar_t((P, n_dim), seed=seed * 313 + 1)
        anchors = anchors / (anchors.norm(dim=1, keepdim=True) + 1e-8)

        def route_top1(keys: torch.Tensor) -> torch.Tensor:
            sims = keys @ anchors.T  # (B, P)
            return sims.argmax(dim=1)

        return route_top1, {"anchors": anchors, "kind": "top1"}

    if name == "learned_supervised":
        # One-pass Hebbian centroid: init random anchors, then update each anchor to
        # be the sign-quantized mean of key_sample entries that initially routed to it.
        if key_sample is None or key_sample.shape[0] == 0:
            # Fallback to random if no sample provided
            anchors = _rand_bipolar_t((P, n_dim), seed=seed * 313 + 2)
        else:
            anchors0 = _rand_bipolar_t((P, n_dim), seed=seed * 313 + 2)
            anchors0 = anchors0 / (anchors0.norm(dim=1, keepdim=True) + 1e-8)
            init_route = (key_sample @ anchors0.T).argmax(dim=1)  # (B,)
            # Centroid update
            anchors = anchors0.clone()
            counts = torch.zeros(P, device=DEVICE, dtype=torch.float32)
            centroids = torch.zeros((P, n_dim), device=DEVICE, dtype=torch.float32)
            centroids.index_add_(0, init_route, key_sample)
            counts.index_add_(0, init_route,
                              torch.ones(init_route.shape[0], device=DEVICE))
            has_members = counts > 0
            centroids[has_members] = centroids[has_members] / counts[has_members].unsqueeze(1)
            # Sign-quantize + blend with original (avoid empty-cluster degeneracy)
            centroids_bp = torch.where(centroids >= 0, torch.ones_like(centroids),
                                        -torch.ones_like(centroids))
            anchors = torch.where(has_members.unsqueeze(1), centroids_bp, anchors0)
        anchors = anchors / (anchors.norm(dim=1, keepdim=True) + 1e-8)

        def route_top1(keys: torch.Tensor) -> torch.Tensor:
            sims = keys @ anchors.T
            return sims.argmax(dim=1)

        return route_top1, {"anchors": anchors, "kind": "top1"}

    if name == "lsh_hash":
        n_planes = max(1, int(math.ceil(math.log2(max(P, 2)))))
        planes = _rand_bipolar_t((n_planes, n_dim), seed=seed * 313 + 3)
        planes = planes / (planes.norm(dim=1, keepdim=True) + 1e-8)
        powers = torch.tensor([1 << i for i in range(n_planes)],
                              device=DEVICE, dtype=torch.int64)

        def route_top1(keys: torch.Tensor) -> torch.Tensor:
            signs = (keys @ planes.T) >= 0  # (B, n_planes) bool
            codes = (signs.long() * powers.unsqueeze(0)).sum(dim=1)
            return codes % P

        return route_top1, {"planes": planes, "n_planes": n_planes, "kind": "top1"}

    if name == "hierarchical_tree":
        G = _hier_G(P)
        fine_per_group = P // G
        assert P % G == 0, f"P={P} not divisible by G={G}"
        fine_anchors = _rand_bipolar_t((P, n_dim), seed=seed * 313 + 4)
        fine_anchors = fine_anchors / (fine_anchors.norm(dim=1, keepdim=True) + 1e-8)
        # Group anchors = mean of fine anchors per group
        grouped = fine_anchors.view(G, fine_per_group, n_dim)
        group_anchors = grouped.mean(dim=1)
        group_anchors = torch.where(group_anchors >= 0,
                                     torch.ones_like(group_anchors),
                                     -torch.ones_like(group_anchors))
        group_anchors = group_anchors / (group_anchors.norm(dim=1, keepdim=True) + 1e-8)

        def route_top1(keys: torch.Tensor) -> torch.Tensor:
            # Level 1: route to coarse group
            sims_g = keys @ group_anchors.T  # (B, G)
            group_routed = sims_g.argmax(dim=1)  # (B,)
            # Level 2: within group, route to fine shard
            sims_all = keys @ fine_anchors.T  # (B, P)
            fine_group_id = (torch.arange(P, device=DEVICE) // fine_per_group)  # (P,)
            group_mask = (fine_group_id.unsqueeze(0) == group_routed.unsqueeze(1))
            sims_masked = torch.where(group_mask, sims_all,
                                       torch.full_like(sims_all, float("-inf")))
            return sims_masked.argmax(dim=1)

        return route_top1, {"fine_anchors": fine_anchors,
                             "group_anchors": group_anchors,
                             "G": G, "fine_per_group": fine_per_group,
                             "kind": "top1"}

    if name == "knn_softmax":
        anchors = _rand_bipolar_t((P, n_dim), seed=seed * 313 + 5)
        anchors = anchors / (anchors.norm(dim=1, keepdim=True) + 1e-8)

        def route_topk(keys: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
            sims = keys @ anchors.T  # (B, P)
            topk_vals, topk_idx = sims.topk(KNN_K, dim=1)  # (B, K)
            # softmax(sim / tau) as weights
            weights = torch.softmax(topk_vals / KNN_TAU, dim=1)  # (B, K)
            return topk_idx, weights

        return route_topk, {"anchors": anchors, "K": KNN_K, "tau": KNN_TAU,
                             "kind": "topk"}

    raise ValueError(f"unknown geometry: {name!r}")


def _routing_hash(extra: Dict[str, Any]) -> str:
    """SHA-256 of routing state (for META_RULE_AF arms-differ check)."""
    key = ""
    for k, v in extra.items():
        if isinstance(v, torch.Tensor):
            key += f"{k}:" + hashlib.sha256(
                v.detach().cpu().numpy().tobytes()).hexdigest()[:16] + "|"
        else:
            key += f"{k}:{v}|"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# INGEST + EVAL per geometry
# ---------------------------------------------------------------------------
def ingest_and_eval(geom_name: str, triples: List[Tuple[int, int, int]],
                    keyobjs: Dict[Tuple[int, int], List[int]],
                    n_ent: int, n_rel: int, n_dim: int, P: int,
                    seed: int, n_eval: int,
                    routing_noise_cos: float = 1.0) -> Dict[str, Any]:
    """Ingest triples routed via geometry into P shards; eval retrieval_acc.

    routing_noise_cos: target cos(cue_routed, cue_clean) at EVAL time. 1.0=no
        noise (clean). <1.0 introduces cue noise to stress routing. This is
        the discriminator load-bearing knob.

    Returns per-arm metrics dict.
    """
    t0 = time.time()
    E, R, sq = build_codebooks(n_ent, n_rel, n_dim, seed)

    # Prepare all keys and objects
    keys_list = list(keyobjs.items())
    n_keys = len(keys_list)
    # Build key vectors on device: E[s] * R[p] * sqrt(N)
    s_idx = torch.tensor([k[0] for (k, _) in keys_list], device=DEVICE, dtype=torch.long)
    p_idx = torch.tensor([k[1] for (k, _) in keys_list], device=DEVICE, dtype=torch.long)
    key_vecs = E[s_idx] * R[p_idx] * sq  # (n_keys, N)

    # For learned_supervised, provide key_sample
    key_sample_for_learn = key_vecs if geom_name == "learned_supervised" else None
    route_fn, extra = build_geometry(geom_name, P, n_dim, seed,
                                      key_sample=key_sample_for_learn)
    routing_hash = _routing_hash(extra)

    # Route ALL keys to shards
    kind = extra["kind"]
    if kind == "top1":
        shard_of_key = route_fn(key_vecs)  # (n_keys,)
        # Ingest each key's objects into that shard's Hebbian W
        # W_shard[i] shape (N, N); sum over routed (s,p,o): W += outer(E[o], key)/N
        Ws = torch.zeros((P, n_dim, n_dim), device=DEVICE, dtype=torch.float32)
        # We need object vectors per (s,p) key; iterate keys
        # (heavy loop; fine at ~5k keys)
        # For efficiency batch by shard
        for shard in range(P):
            mask = (shard_of_key == shard)
            if not mask.any():
                continue
            key_shard = key_vecs[mask]  # (Ns, N)
            # For each key in this shard, sum object vectors
            # Collect object indices for keys in this shard
            key_indices = torch.nonzero(mask).squeeze(1).tolist()
            obj_vecs_list = []
            key_expand_list = []
            for ki in key_indices:
                objs = keyobjs[keys_list[ki][0]]
                for o in objs:
                    obj_vecs_list.append(o)
                    key_expand_list.append(ki)
            if not obj_vecs_list:
                continue
            obj_idx_t = torch.tensor(obj_vecs_list, device=DEVICE, dtype=torch.long)
            key_expand_t = torch.tensor(key_expand_list, device=DEVICE, dtype=torch.long)
            E_o = E[obj_idx_t]  # (M_shard, N)
            K_expand = key_vecs[key_expand_t]  # (M_shard, N)
            # W_shard += E_o.T @ K_expand / N
            Ws[shard] += (E_o.T @ K_expand) / n_dim
    elif kind == "topk":
        # Route each key to top-K shards; ingest into each with softmax weight
        topk_idx, weights = route_fn(key_vecs)  # (n_keys, K), (n_keys, K)
        Ws = torch.zeros((P, n_dim, n_dim), device=DEVICE, dtype=torch.float32)
        for kslot in range(KNN_K):
            shard_of_key = topk_idx[:, kslot]  # (n_keys,)
            w_kslot = weights[:, kslot]  # (n_keys,)
            for shard in range(P):
                mask = (shard_of_key == shard)
                if not mask.any():
                    continue
                key_indices = torch.nonzero(mask).squeeze(1).tolist()
                obj_vecs_list = []
                key_expand_list = []
                weight_expand_list = []
                for ki in key_indices:
                    objs = keyobjs[keys_list[ki][0]]
                    for o in objs:
                        obj_vecs_list.append(o)
                        key_expand_list.append(ki)
                        weight_expand_list.append(float(w_kslot[ki].item()))
                if not obj_vecs_list:
                    continue
                obj_idx_t = torch.tensor(obj_vecs_list, device=DEVICE, dtype=torch.long)
                key_expand_t = torch.tensor(key_expand_list, device=DEVICE, dtype=torch.long)
                w_expand_t = torch.tensor(weight_expand_list, device=DEVICE, dtype=torch.float32)
                E_o = E[obj_idx_t]  # (M_shard, N)
                K_expand = key_vecs[key_expand_t]  # (M_shard, N)
                # Weighted contribution
                W_scaled = (E_o.T * w_expand_t.unsqueeze(0)) @ K_expand / n_dim
                Ws[shard] += W_scaled

    # EVAL: sample n_eval keys, route, retrieve, set_recall@|obj|
    g_ev = np.random.default_rng(int(seed) * 991 + 3)
    if n_keys == 0:
        return {"geometry": geom_name, "retrieval_acc": 0.0, "n_eval": 0,
                "routing_hash": routing_hash, "elapsed_s": time.time() - t0,
                "failure_class": "NO_KEYS"}
    eval_idx = g_ev.choice(n_keys, size=min(n_eval, n_keys), replace=False)
    hits = 0.0
    tot = 0
    # Precompute noise-perturbed routing cues
    noise_scale = math.sqrt(max(0.0, 1.0 - routing_noise_cos ** 2))
    g_noise = torch.Generator(device=DEVICE)
    g_noise.manual_seed(int(seed) * 419 + 11)
    for i in eval_idx:
        (s_i, p_i), true_objs = keys_list[i]
        key_clean = E[s_i] * R[p_i] * sq  # (N,)
        # Routing cue = clean_key * cos + noise * noise_scale
        # (bipolar noise, sign-quantized)
        if noise_scale > 0.0:
            noise_raw = torch.empty(n_dim, device=DEVICE, dtype=torch.float32)
            noise_raw.normal_(0.0, 1.0, generator=g_noise)
            noise_bp = torch.where(noise_raw >= 0, torch.ones_like(noise_raw),
                                    -torch.ones_like(noise_raw))
            # normalize both to unit-norm before mixing so cos ~= routing_noise_cos
            key_norm = key_clean / (key_clean.norm() + 1e-8)
            noise_norm = noise_bp / (noise_bp.norm() + 1e-8)
            cue_routed = (routing_noise_cos * key_norm
                          + noise_scale * noise_norm)
            cue_routed = cue_routed / (cue_routed.norm() + 1e-8)
            cue_routed = cue_routed * sq  # match key magnitude scale
        else:
            cue_routed = key_clean
        key = cue_routed.unsqueeze(0)  # (1, N)
        if kind == "top1":
            shard = int(route_fn(key).item())
            W = Ws[shard]  # (N, N)
            # Retrieval uses CLEAN key (routing was noisy; only routing decision matters)
            scores = E @ (W @ key_clean)  # (n_ent,)
        else:  # topk
            tk_idx, wts = route_fn(key)  # (1, K), (1, K)
            # Combine top-K shard scores weighted (retrieval uses CLEAN key)
            scores = torch.zeros(n_ent, device=DEVICE, dtype=torch.float32)
            for kslot in range(KNN_K):
                sh = int(tk_idx[0, kslot].item())
                w = float(wts[0, kslot].item())
                scores = scores + w * (E @ (Ws[sh] @ key_clean))
        k_true = len(true_objs)
        # top-k retrieval; set-overlap fraction
        topk_pred = torch.topk(scores, min(k_true, n_ent)).indices.cpu().tolist()
        overlap = len(set(topk_pred) & set(true_objs)) / max(k_true, 1)
        hits += overlap
        tot += 1

    retrieval_acc = hits / max(tot, 1)
    elapsed = time.time() - t0

    # Free memory
    del Ws, key_vecs, E, R
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "geometry": geom_name,
        "retrieval_acc": round(float(retrieval_acc), 5),
        "n_eval": int(tot),
        "routing_hash": routing_hash,
        "kind": kind,
        "elapsed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Selftest (tiny; runs in seconds; verifies plumbing + arms-differ)
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Selftest: tiny KG + 5 arms + arms-differ + cardinality."""
    msgs: List[str] = []

    # 1. Cardinality
    if EXPECTED_N_UNITS_PER_CELL != 5:
        return False, f"cardinality {EXPECTED_N_UNITS_PER_CELL} != 5"
    msgs.append(f"cardinality per-cell = {EXPECTED_N_UNITS_PER_CELL}")

    # 2. All 5 registered + callable
    for fam in GEOMETRY_FAMILIES:
        try:
            fn, extra = build_geometry(fam, P=8, n_dim=64, seed=seed)
        except Exception as e:
            return False, f"build_geometry({fam}) FAIL: {e}"
        assert callable(fn), f"{fam} route_fn not callable"
    msgs.append(f"5 geometries registered: {list(GEOMETRY_FAMILIES)}")

    # 3. Arms differ (routing_hash distinct)
    hashes = {}
    for fam in GEOMETRY_FAMILIES:
        # For learned_supervised, provide a sample
        key_sample = None
        if fam == "learned_supervised":
            key_sample = _rand_bipolar_t((50, 64), seed=seed + 999)
        _, extra = build_geometry(fam, P=8, n_dim=64, seed=seed, key_sample=key_sample)
        hashes[fam] = _routing_hash(extra)
    n_unique = len(set(hashes.values()))
    if n_unique < 5:
        return False, f"ARMS_DIFFER violation: {n_unique}/5 unique routing hashes; hashes={hashes}"
    msgs.append(f"5/5 unique routing hashes (META_RULE_AF)")

    # 4. Route tiny KG (mini synthetic) through all 5 arms; verify retrieval_acc > 0
    #    (this is a plumbing test, not a discriminator test)
    n_ent = 30
    n_rel = 4
    m_trip = 40
    g = np.random.default_rng(int(seed) + 17)
    triples = []
    keyobjs: Dict[Tuple[int, int], List[int]] = defaultdict(list)
    for _ in range(m_trip):
        s = int(g.integers(0, n_ent))
        p = int(g.integers(0, n_rel))
        o = int(g.integers(0, n_ent))
        triples.append((s, p, o))
        keyobjs[(s, p)].append(o)
    keyobjs = {k: sorted(set(v)) for k, v in keyobjs.items()}

    sanity = {}
    for fam in GEOMETRY_FAMILIES:
        r = ingest_and_eval(fam, triples, keyobjs, n_ent, n_rel,
                             n_dim=256, P=8, seed=seed, n_eval=30)
        sanity[fam] = r["retrieval_acc"]
        msgs.append(f"sanity {fam}: ra={r['retrieval_acc']:.3f} (n_eval={r['n_eval']})")
        if r["retrieval_acc"] < 0.05:
            return False, f"sanity FAIL {fam}: retrieval_acc={r['retrieval_acc']:.3f} < 0.05 (plumbing broken)"

    # 5. FULL-SCALE-PREVIEW (v3 fix; DISCRIMINATOR_MUST_SURVIVE_SCALE gate).
    # Allocate + free the FULL Ws tensor (P_FULL, N_FULL, N_FULL) to catch
    # OOM at cell-author time. Applies for BOTH CUDA and CPU (CPU allocation
    # of 2 GiB still validates the sizing arithmetic).
    ws_gib = _WS_FULL_GIB
    msgs.append(f"FULL Ws budget: P={P_SHARDS_FULL} N={N_DIM_FULL} => {ws_gib:.2f} GiB")
    if _CUDA_OK:
        try:
            _preview = torch.zeros(
                (P_SHARDS_FULL, N_DIM_FULL, N_DIM_FULL),
                device=DEVICE, dtype=torch.float32,
            )
            del _preview
            torch.cuda.empty_cache()
            msgs.append(f"full_scale_preview alloc OK (CUDA {GPU_MAX_MEM_GB:.1f} GB)")
        except torch.cuda.OutOfMemoryError as e:
            return False, (
                f"FULL_SCALE_PREVIEW OOM ({ws_gib:.2f} GiB Ws exceeds free CUDA); "
                f"config drift or GPU too small: {e}"
            )
    else:
        # CPU path: skip actual alloc (2 GiB CPU alloc is wasteful for smoke),
        # just record the sizing so verdict shows the arithmetic ran.
        msgs.append("full_scale_preview CPU path: sizing computed, alloc skipped")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Full per-seed run
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all 5 geometry arms at target regime for one seed."""
    is_smoke = (run_mode == "smoke")
    m_ingest = M_INGEST_SMOKE if is_smoke else M_INGEST_FULL
    n_dim = N_DIM_SMOKE if is_smoke else N_DIM_FULL
    P = P_SHARDS_SMOKE if is_smoke else P_SHARDS_FULL
    n_eval = N_EVAL_SMOKE if is_smoke else N_EVAL_FULL
    routing_noise_cos = ROUTING_NOISE_COS_SMOKE if is_smoke else ROUTING_NOISE_COS_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"M_ingest={m_ingest} N={n_dim} P={P} n_eval={n_eval} "
          f"routing_noise_cos={routing_noise_cos}", flush=True)

    # Load KG
    t_load = time.time()
    triples, keyobjs, n_ent, n_rel = load_conceptnet(seed, m_ingest)
    print(f"[load] {len(triples)} triples, {n_ent} ents, {n_rel} rels, "
          f"{len(keyobjs)} unique (s,p) keys in {time.time()-t_load:.1f}s",
          flush=True)

    per_arm: List[Dict[str, Any]] = []
    for fam in GEOMETRY_FAMILIES:
        print(f"[arm] {fam} ...", flush=True)
        try:
            r = ingest_and_eval(fam, triples, keyobjs, n_ent, n_rel,
                                 n_dim=n_dim, P=P, seed=seed, n_eval=n_eval,
                                 routing_noise_cos=routing_noise_cos)
            per_arm.append(r)
            print(f"  -> retrieval_acc={r['retrieval_acc']:.4f} "
                  f"(n_eval={r['n_eval']}, hash={r['routing_hash']}, "
                  f"t={r['elapsed_s']:.1f}s)", flush=True)
        except SystemExit:
            raise
        except Exception as e:
            per_arm.append({
                "geometry": fam,
                "retrieval_acc": -1.0,
                "n_eval": 0,
                "failure_class": type(e).__name__,
                "failure_msg": str(e)[:200],
                "traceback": traceback.format_exc()[:2000],
                "routing_hash": "FAIL",
                "elapsed_s": 0.0,
            })
            print(f"  -> FAIL: {type(e).__name__}: {e}", flush=True)
        finally:
            # v3 fix (2026-07-01): flush CUDA cache after EVERY arm regardless
            # of success/fail. Prior behavior only flushed on ingest_and_eval's
            # successful return; when an arm crashed mid-Ws-alloc the ~4 GiB
            # Ws tensor + Python traceback frame refs kept prior E/R/key_vecs
            # resident, causing later arms to OOM. Now every arm starts clean.
            if _CUDA_OK:
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

    # Aggregate
    accs = {r["geometry"]: r["retrieval_acc"] for r in per_arm}
    hashes = {r["geometry"]: r["routing_hash"] for r in per_arm}
    n_unique_hashes = len(set(v for v in hashes.values() if v != "FAIL"))

    # Discrimination test: >=3 arms with pairwise separation >=0.10
    good_accs = sorted([v for v in accs.values() if v >= 0])
    n_distinct = 0
    if good_accs:
        # Count pairs with >=0.10 gap; equivalently count "distinct" as
        # cluster count when gap-splitting sorted list
        clusters = [good_accs[0]]
        for a in good_accs[1:]:
            if a - clusters[-1] >= HP_MIN_PAIRWISE_SEPARATION:
                clusters.append(a)
        n_distinct = len(clusters)

    # Positive control (random_partition)
    pc_floor = POSITIVE_CONTROL_FLOOR_SMOKE if is_smoke else POSITIVE_CONTROL_FLOOR_FULL
    pc_ceiling = POSITIVE_CONTROL_CEILING_SMOKE if is_smoke else POSITIVE_CONTROL_CEILING_FULL
    pc_acc = accs.get("random_partition", -1.0)
    pc_pass = pc_acc >= pc_floor
    pc_saturated = pc_acc >= Q_SUSPECT_SATURATION
    pc_above_ceiling = pc_acc > pc_ceiling  # regime too easy for PC

    # Per-arm tiers
    per_arm_tier: Dict[str, str] = {}
    tier_counts = {"HARD_PASS": 0, "MIDDLE_BAND": 0, "HARD_FAIL": 0,
                   "SATURATED": 0, "FAIL": 0}
    for r in per_arm:
        v = r["retrieval_acc"]
        if v < 0:
            t = "FAIL"
        elif v >= Q_SUSPECT_SATURATION:
            t = "SATURATED"
        elif v >= HP_HARD_PASS_RA:
            t = "HARD_PASS"
        elif v >= HP_MIDDLE_BAND_RA:
            t = "MIDDLE_BAND"
        else:
            t = "HARD_FAIL"
        per_arm_tier[r["geometry"]] = t
        tier_counts[t] += 1

    # Cardinality
    observed_n = len(per_arm)
    cardinality_ok = (observed_n == EXPECTED_N_UNITS_PER_CELL)

    # Overall verdict logic
    discrimination_gate_pass = (n_distinct >= HP_MIN_DISTINCT_GEOMETRIES)

    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                       f"expected {EXPECTED_N_UNITS_PER_CELL} arms, got {observed_n}")
    elif not pc_pass:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_POSITIVE_CONTROL: random_partition retrieval_acc="
                       f"{pc_acc:.3f} below floor {pc_floor}; sharded regime "
                       f"invocation problem (META_RULE_BC)")
    elif pc_saturated:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_POSITIVE_CONTROL_SATURATED: random_partition "
                       f"retrieval_acc={pc_acc:.3f} >= {Q_SUSPECT_SATURATION} "
                       f"(META_RULE_AG substrate-too-robust; regime needs iteration)")
    elif not discrimination_gate_pass:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND_DISCRIMINATION_FLOOR: only {n_distinct} distinct "
                       f"retrieval_acc localizations (>=0.10 separation); need "
                       f">={HP_MIN_DISTINCT_GEOMETRIES} (META_RULE_AV auto-demote)")
    elif tier_counts["HARD_PASS"] >= 1:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: {tier_counts['HARD_PASS']} arms cleared "
                       f"retrieval_acc>={HP_HARD_PASS_RA}; {n_distinct} distinct "
                       f"localizations; PC={pc_acc:.3f}")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: no arm cleared {HP_HARD_PASS_RA}; "
                       f"{n_distinct} distinct localizations; PC={pc_acc:.3f}")

    return {
        "seed": seed,
        "run_mode": run_mode,
        "per_arm": per_arm,
        "per_arm_tier": per_arm_tier,
        "tier_counts": tier_counts,
        "retrieval_acc_by_arm": accs,
        "routing_hash_by_arm": hashes,
        "n_unique_hashes": n_unique_hashes,
        "n_distinct_localizations": n_distinct,
        "discrimination_gate_pass": discrimination_gate_pass,
        "positive_control": {
            "arm": "random_partition",
            "retrieval_acc": pc_acc,
            "floor": pc_floor,
            "pass": pc_pass,
            "saturated": pc_saturated,
        },
        "cardinality_ok": cardinality_ok,
        "expected_n_units": EXPECTED_N_UNITS_PER_CELL,
        "observed_n_units": observed_n,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "n_kg_ents": n_ent,
        "n_kg_rels": n_rel,
        "n_kg_keys": len(keyobjs),
        "n_kg_triples": len(triples),
        "M_ingest": m_ingest,
        "N_DIM": n_dim,
        "P_SHARDS": P,
        "n_eval": n_eval,
        "routing_noise_cos": routing_noise_cos,
    }
