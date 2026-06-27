"""multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu.

GPU PORT of exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3.py
(numpy v3 preserved as-is for reference). Per USER Fix #24 GPU mandate:
GPU dispatch must ACTUALLY use GPU.

KEY GPU TRANSFORMATIONS (vs numpy v3):
  - DEVICE = 'cuda'; assert torch.cuda.is_available() at boot
  - E, R, W are torch.float32 tensors on cuda
  - All matmuls (W @ x, E @ y, W.T @ x) are torch ops on GPU tensors
  - argmax uses torch.argmax
  - BATCHED CANDIDATE SCORING (the real GPU win): in v3 numpy, arms B/D/E
    looped `for Z in range(V_C):` computing backward_state per candidate.
    Each backward_state computes (mid) matvecs of size N=8192 -> bottleneck.
    GPU port computes ALL V_C backward_states simultaneously by starting
    from E (V_C, N) and applying the backward ops as batched matmuls:
        S = E.clone()                                # (V_C, N)
        for p in reversed(preds[mid:]):
            S = S @ W                                # (V_C, N) -- W.T @ s for each row
            S = S * (R[p] * sq)                      # broadcast elementwise
    Then cosine vs the single state_fwd is one (V_C, N) @ (N,) matmul.
    Expected ~50-200x speedup vs CPU numpy at N=8192, V_C=200.
  - Encoder + W hoisted outside per-arm loops (Fix #24)
  - torch.cuda.empty_cache() between depth iterations (avoid OOM accumulation)

PROT-021 checkpoint preserved. Same cell semantics as v3 numpy:
  - 7 arms x 4 depths x 5 seeds = 115 records (per-seed); 125 cell-author check
  - HARD_PASS conditions identical (BIDIR_MEET_MID >= 0.45 at d=9, etc.)
  - SACRED_SANITY / META_M7 / BIAS_Q guards identical

ASCII-only; per-seed checkpoint; atexit synthesizer; NO_SILENT_EXCEPT.
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
import atexit
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics
)

ANCHOR_NAME = "multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# ============================================================
# PROSPECTIVE BANDS (LOCKED at module-init; per drill 2026-06-27)
# Identical to numpy v3 -- semantics preserved.
# ============================================================
HP_BIDIR_D9_FLOOR = 0.45
HP_BIDIR_OVER_HALF = 0.10
HP_BIDIR_OVER_RANDOM = 0.15
HP_META_M7_REPLICATE_FLOOR = 0.60

META_M7_RAIL_LO = 0.08
META_M7_RAIL_HI = 0.25

SACRED_SANITY_LO = 0.60
SACRED_SANITY_HI = 1.00

HF_BIDIR_D9_COLLAPSE = 0.05
HF_BIDIR_OVER_HALF_BREACH = 0.05

EXPECTED_N_ARMS_DEPTH_DEP = 6
EXPECTED_N_ARMS_DEPTH_INDEP = 1
EXPECTED_N_DEPTHS = 4
EXPECTED_N_SEEDS_FULL = 5
EXPECTED_N_SEEDS_SMOKE = 1
HARD_FAIL_CARDINALITY_BREACH_FULL = (
    EXPECTED_N_ARMS_DEPTH_DEP * EXPECTED_N_DEPTHS * EXPECTED_N_SEEDS_FULL
    + EXPECTED_N_ARMS_DEPTH_INDEP * EXPECTED_N_SEEDS_FULL
)
HARD_FAIL_CARDINALITY_BREACH_SMOKE = (
    EXPECTED_N_ARMS_DEPTH_DEP * 1 * EXPECTED_N_SEEDS_SMOKE
    + EXPECTED_N_ARMS_DEPTH_INDEP * EXPECTED_N_SEEDS_SMOKE
)

V1_REGIME_N_CHAINS = 200
POINTER_V2_N_CHAINS = 200
POINTER_V2_MAX_DEPTH = 10
BASELINE_V_P = 2
POINTER_V_P = 10

DEPTHS = [3, 5, 7, 9]

assert HP_BIDIR_D9_FLOOR > HF_BIDIR_D9_COLLAPSE
assert HP_BIDIR_OVER_HALF > HF_BIDIR_OVER_HALF_BREACH
assert HP_BIDIR_OVER_RANDOM > HP_BIDIR_OVER_HALF
assert META_M7_RAIL_LO < META_M7_RAIL_HI < HP_META_M7_REPLICATE_FLOOR
assert SACRED_SANITY_LO < SACRED_SANITY_HI
assert all(d >= 3 for d in DEPTHS) and DEPTHS == sorted(DEPTHS)

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 200
    SEEDS = [7]
    POINTER_N_CHAINS = 50
    POINTER_V2_N_CHAINS_LOCAL = 100
    BASELINE_N_CHAINS_LOCAL = V1_REGIME_N_CHAINS
    SMOKE_DEPTHS = [5]
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    SEEDS = [7, 17, 23, 41, 53]
    POINTER_N_CHAINS = V1_REGIME_N_CHAINS
    POINTER_V2_N_CHAINS_LOCAL = POINTER_V2_N_CHAINS
    BASELINE_N_CHAINS_LOCAL = V1_REGIME_N_CHAINS
    SMOKE_DEPTHS = DEPTHS

n_predicates = max(BASELINE_V_P, POINTER_V_P)

CONFIG_VERSION = (
    "bidirMeetMidDepthScalingV3_GPU: N=%d V_C=%d BASELINE_V_P=%d BASELINE_N=%d "
    "POINTER_V_P=%d POINTER_N=%d POINTER_V2_N=%d POINTER_V2_DEPTH=%d "
    "depths=%s seeds=%s mode=%s "
    "HP_d9>=%.2f HP_over_half>=%.2f HP_over_random>=%.2f HP_m7_rep>=%.2f "
    "META_M7=[%.2f,%.2f] sanity=[%.2f,%.2f] "
    "card_full=%d card_smoke=%d device=cuda"
) % (
    N_DIM, V_CONCEPTS, BASELINE_V_P, BASELINE_N_CHAINS_LOCAL,
    POINTER_V_P, POINTER_N_CHAINS, POINTER_V2_N_CHAINS_LOCAL, POINTER_V2_MAX_DEPTH,
    DEPTHS, SEEDS, RUN_MODE,
    HP_BIDIR_D9_FLOOR, HP_BIDIR_OVER_HALF, HP_BIDIR_OVER_RANDOM, HP_META_M7_REPLICATE_FLOOR,
    META_M7_RAIL_LO, META_M7_RAIL_HI,
    SACRED_SANITY_LO, SACRED_SANITY_HI,
    HARD_FAIL_CARDINALITY_BREACH_FULL, HARD_FAIL_CARDINALITY_BREACH_SMOKE,
)


# ============================================================
# Torch / CUDA boot (Fix #24)
# ============================================================
try:
    import torch
except Exception as e:
    print("[FATAL] torch import failed: %s" % e, flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA required (Fix #24 GPU mandate; numpy v3 already exists for CPU)", flush=True)
    sys.exit(1)

DEVICE = torch.device("cuda")
print("[GPU] device=%s" % torch.cuda.get_device_name(0), flush=True)


# ============================================================
# Substrate primitives (GPU; chain-equivalent to numpy v3)
# ============================================================
def bipolar_np(M: int, n: int, g) -> np.ndarray:
    """Numpy-side bipolar generator (kept for triple-building parity with v3)."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def bipolar_torch(M: int, n: int, g) -> torch.Tensor:
    """GPU bipolar generator -- byte-equivalent to numpy version (same RNG)."""
    X_np = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    X = torch.from_numpy(X_np).to(DEVICE)
    X = X / (X.norm(dim=1, keepdim=True) + 1e-8)
    return X


def ingest_hebbian_torch(triples, E: torch.Tensor, R: torch.Tensor,
                          sq: float, n_dim: int, batch: int = 2000) -> torch.Tensor:
    """W = sum_t (E[o_t].T @ (E[s_t] * R[p_t] * sq)) / n_dim -- on GPU."""
    if not triples:
        return torch.zeros((n_dim, n_dim), dtype=torch.float32, device=DEVICE)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx = torch.from_numpy(tr[:, 0]).to(DEVICE)
    p_idx = torch.from_numpy(tr[:, 1]).to(DEVICE)
    o_idx = torch.from_numpy(tr[:, 2]).to(DEVICE)
    W = torch.zeros((n_dim, n_dim), dtype=torch.float32, device=DEVICE)
    n_tr = len(tr)
    for b in range(0, n_tr, batch):
        e = min(b + batch, n_tr)
        ks = E[s_idx[b:e]] * R[p_idx[b:e]] * sq           # (batch, n_dim)
        # outer-sum: E[o].T @ ks  -- (n_dim, batch) @ (batch, n_dim) = (n_dim, n_dim)
        W = W + (E[o_idx[b:e]].t() @ ks) / n_dim
    return W


def make_deep_chains(n_chains, V, P, max_depth, g, disallow_s):
    """Pure-numpy chain builder (returns Python lists of int triples; no tensors)."""
    all_triples, chain_queries, used_s = [], [], set(disallow_s)
    tries = 0
    while len(chain_queries) < n_chains and tries < n_chains * 200:
        tries += 1
        nodes = []
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        nodes.append(s)
        for _ in range(max_depth):
            cand = int(g.integers(0, V))
            while cand in nodes:
                cand = int(g.integers(0, V))
            nodes.append(cand)
        chain = []
        for i in range(max_depth):
            p = int(g.integers(0, P))
            chain.append((nodes[i], p, nodes[i + 1]))
        all_triples.extend(chain)
        chain_queries.append(chain)
        used_s.add(s)
    if len(chain_queries) < n_chains:
        raise RuntimeError("BLOCKING make_deep_chains: only %d/%d" % (len(chain_queries), n_chains))
    return all_triples, chain_queries


# ------ GPU forward / backward primitives (single-vector) ------
def _retrieve_1hop_t(E: torch.Tensor, W: torch.Tensor, R: torch.Tensor,
                      s: int, p: int, sq: float) -> int:
    key = E[s] * R[p] * sq
    return int(torch.argmax(E @ (W @ key)).item())


def _forward_state_t(E: torch.Tensor, W: torch.Tensor, R: torch.Tensor,
                      sq: float, start_idx: int, predicates: List[int]) -> torch.Tensor:
    state = E[start_idx].clone()
    for p in predicates:
        state = W @ (state * R[p] * sq)
    return state


def _backward_state_t(E: torch.Tensor, W: torch.Tensor, R: torch.Tensor,
                       sq: float, end_idx: int, predicates: List[int]) -> torch.Tensor:
    state = E[end_idx].clone()
    for i in range(len(predicates) - 1, -1, -1):
        p = predicates[i]
        state = W.t() @ state
        state = state * R[p] * sq
    return state


# ------ GPU BATCHED backward state across ALL candidates Z ------
def _backward_state_all_Z(E: torch.Tensor, W: torch.Tensor, R: torch.Tensor,
                           sq: float, predicates: List[int]) -> torch.Tensor:
    """Compute backward_state simultaneously for every Z in 0..V-1.

    Starting from S = E (shape V_C, N), apply the backward ops as batched matmuls:
        S = S @ W              # (V_C, N) -- equivalent to W.T @ s for each row s
        S = S * (R[p] * sq)    # broadcast elementwise
    Final S has shape (V_C, N); row Z is backward_state(Z, predicates).

    This is the load-bearing GPU win: replaces V_C separate matvecs with one
    batched matmul per predicate. ~50-200x speedup vs per-candidate loop at
    N=8192, V_C=200.
    """
    S = E.clone()                                       # (V_C, N)
    for i in range(len(predicates) - 1, -1, -1):
        p = predicates[i]
        S = S @ W                                       # (V_C, N) = batched (W.T @ row)
        S = S * (R[p] * sq)                             # broadcast (N,) -> (V_C, N)
    return S


# ============================================================
# ARMS (GPU)
# ============================================================
def arm_baseline_forward_full_depth(E, R, sq, W, chains_test, depth) -> Dict[str, Any]:
    """A: forward-only chain at depth d. Compounding-error ceiling."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop_t(E, W, R, s, p, sq)
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "n_queries": n, "depth": depth,
            "mechanism": "forward_only_full_depth"}


def arm_bidir_meet_mid(E, R, sq, W, chains_test, depth) -> Dict[str, Any]:
    """B: forward d/2 + backward d/2; rank over V_C candidates by midpoint cosine.

    GPU win: backward_state computed for ALL V_C candidates in one batched pass.
    """
    n = len(chains_test)
    V = E.shape[0]
    mid = depth // 2
    hits = 0
    per_query_correct = []
    for chain in chains_test:
        S = chain[0][0]
        preds = [chain[i][1] for i in range(depth)]
        true_Z = chain[depth - 1][2]

        state_fwd = _forward_state_t(E, W, R, sq, S, preds[:mid])      # (N,)
        fnorm = state_fwd.norm() + 1e-8

        # Batched: all V_C backward_states at once -> (V_C, N)
        bstates = _backward_state_all_Z(E, W, R, sq, preds[mid:])
        bnorms = bstates.norm(dim=1) + 1e-8                            # (V_C,)
        # cos[Z] = (bstates[Z] . state_fwd) / (bnorms[Z] * fnorm)
        dots = bstates @ state_fwd                                     # (V_C,)
        cos = dots / (bnorms * fnorm)
        best_Z = int(torch.argmax(cos).item())

        correct = (best_Z == true_Z)
        if correct:
            hits += 1
        per_query_correct.append(1 if correct else 0)
    return {"top1": round(hits / max(n, 1), 4),
            "n_queries": n, "depth": depth, "midpoint_hop": mid,
            "mechanism": "bidirectional_meet_middle_rank_full_V_C_gpu_batched",
            "_correct_per_query": per_query_correct}


def arm_forward_half_depth(E, R, sq, W, chains_test, depth) -> Dict[str, Any]:
    """C: forward-only at depth floor(d/2). Proves meeting > shorter chain."""
    n = len(chains_test)
    half = depth // 2
    if half == 0:
        return {"top1": 0.0, "n_queries": n, "depth": depth, "half_depth": half,
                "mechanism": "forward_only_half_depth_degenerate"}
    hits = 0
    for chain in chains_test:
        s = chain[0][0]
        for i in range(half):
            p = chain[i][1]
            s = _retrieve_1hop_t(E, W, R, s, p, sq)
        true_mid = chain[half - 1][2]
        if s == true_mid:
            hits += 1
    return {"top1": round(hits / max(n, 1), 4),
            "n_queries": n, "depth": depth, "half_depth": half,
            "mechanism": "forward_only_half_depth"}


def arm_random_meet_baseline(E, R, sq, W, chains_test, depth, seed) -> Dict[str, Any]:
    """D: meet at RANDOM midpoint hop (not floor(d/2)). True-midpoint discriminator.

    GPU win: same batched backward across all V_C.
    """
    n = len(chains_test)
    V = E.shape[0]
    rng = np.random.default_rng(seed * 1009 + 31)
    hits = 0
    for chain in chains_test:
        S = chain[0][0]
        preds = [chain[i][1] for i in range(depth)]
        true_Z = chain[depth - 1][2]
        true_mid = depth // 2
        candidates = [m for m in range(1, depth) if m != true_mid]
        if not candidates:
            candidates = [1]
        random_mid = int(rng.choice(candidates))

        state_fwd = _forward_state_t(E, W, R, sq, S, preds[:random_mid])
        fnorm = state_fwd.norm() + 1e-8

        bstates = _backward_state_all_Z(E, W, R, sq, preds[random_mid:])
        bnorms = bstates.norm(dim=1) + 1e-8
        dots = bstates @ state_fwd
        cos = dots / (bnorms * fnorm)
        best_Z = int(torch.argmax(cos).item())

        if best_Z == true_Z:
            hits += 1
    return {"top1": round(hits / max(n, 1), 4),
            "n_queries": n, "depth": depth,
            "true_midpoint_excluded": (depth // 2),
            "mechanism": "bidirectional_meet_at_random_midpoint_gpu_batched"}


def arm_multiscale_bidirectional(E, R, sq, W, chains_test, depth) -> Dict[str, Any]:
    """E: meet at multiple midpoints {1, floor(d/2), d-1}; sum cosines.

    GPU win: one batched backward per midpoint (3 passes total instead of V_C*3).
    """
    n = len(chains_test)
    V = E.shape[0]
    midpoints = sorted(set([1, depth // 2, max(1, depth - 1)]))
    if depth <= 2:
        midpoints = [1]
    hits = 0
    for chain in chains_test:
        S = chain[0][0]
        preds = [chain[i][1] for i in range(depth)]
        true_Z = chain[depth - 1][2]

        score = torch.zeros(V, dtype=torch.float32, device=DEVICE)
        for m in midpoints:
            fs = _forward_state_t(E, W, R, sq, S, preds[:m])           # (N,)
            fnorm = fs.norm() + 1e-8
            bstates = _backward_state_all_Z(E, W, R, sq, preds[m:])    # (V_C, N)
            bnorms = bstates.norm(dim=1) + 1e-8
            cos = (bstates @ fs) / (bnorms * fnorm)
            score = score + cos
        best_Z = int(torch.argmax(score).item())

        if best_Z == true_Z:
            hits += 1
    return {"top1": round(hits / max(n, 1), 4),
            "n_queries": n, "depth": depth, "midpoints_used": midpoints,
            "mechanism": "multiscale_bidirectional_sum_cosines_gpu_batched"}


def arm_meta_m7_rail_replicate(E, R, sq, W_pointer_v2, chains_test, depth) -> Dict[str, Any]:
    """F: pointer-v2-regime W; forward-only at depth d. v2 verified [0.08, 0.25] at d=5."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop_t(E, W_pointer_v2, R, s, p, sq)
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "n_queries": n, "depth": depth,
            "mechanism": "pointer_v2_regime_forward_only"}


def arm_meta_m7_bidir_replicate(E, R, sq, W_pointer_v2, chains_test, depth) -> Dict[str, Any]:
    """F': BIDIR_MEET_MID on pointer-v2-regime W at depth d."""
    return arm_bidir_meet_mid(E, R, sq, W_pointer_v2, chains_test, depth)


def arm_sacred_sanity_k1(E, R, sq, W, chains_test) -> Dict[str, Any]:
    """G: K=1 forward; absolute floor sanity rail. Depth-independent."""
    n = len(chains_test)
    hits = 0
    for chain in chains_test:
        s = chain[0][0]
        p = chain[0][1]
        s_pred = _retrieve_1hop_t(E, W, R, s, p, sq)
        if s_pred == chain[0][2]:
            hits += 1
    return {"top1": round(hits / max(n, 1), 4),
            "n_queries": n, "depth": 1,
            "mechanism": "forward_K1_sanity_floor"}


# ============================================================
# SELF-TEST (T1-T12 + T13 GPU-equivalence; module-init gate)
# In-process only -- no remote dispatch yet (USER NO LOCAL SMOKE).
# ============================================================
def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    V = 30
    sq = math.sqrt(n)
    E = bipolar_torch(V, n, g)
    R = bipolar_torch(max(POINTER_V_P, 4), n, g)

    # T1: primitives + Hebbian build on GPU
    triples, chains = make_deep_chains(8, V, 4, max_depth=9, g=g, disallow_s=set())
    W = ingest_hebbian_torch(triples, E, R, sq, n)
    assert W.shape == (n, n)
    assert W.device.type == "cuda", "T1: W not on cuda"
    assert E.device.type == "cuda", "T1: E not on cuda"

    # T2: forward-full-depth arm
    chains_d5 = [c[:5] for c in chains]
    r_a = arm_baseline_forward_full_depth(E, R, sq, W, chains_d5, depth=5)
    assert 0.0 <= r_a["top1"] <= 1.0
    assert len(r_a["per_step_acc"]) == 5

    # T3: bidir meet mid arm (GPU batched)
    r_b = arm_bidir_meet_mid(E, R, sq, W, chains_d5, depth=5)
    assert 0.0 <= r_b["top1"] <= 1.0
    assert r_b["midpoint_hop"] == 2

    # T4: forward half depth arm
    r_c = arm_forward_half_depth(E, R, sq, W, chains_d5, depth=5)
    assert 0.0 <= r_c["top1"] <= 1.0
    assert r_c["half_depth"] == 2

    # T5: random meet baseline
    r_d = arm_random_meet_baseline(E, R, sq, W, chains_d5, depth=5, seed=0)
    assert 0.0 <= r_d["top1"] <= 1.0
    assert r_d["true_midpoint_excluded"] == 2

    # T6: multiscale bidir
    r_e = arm_multiscale_bidirectional(E, R, sq, W, chains_d5, depth=5)
    assert 0.0 <= r_e["top1"] <= 1.0
    assert len(r_e["midpoints_used"]) >= 1
    assert all(1 <= m <= 4 for m in r_e["midpoints_used"])

    # T7: META_M7 replicate (forward + bidir)
    triples_v2, chains_v2 = make_deep_chains(8, V, 4, max_depth=10, g=g, disallow_s=set())
    W_v2 = ingest_hebbian_torch(triples_v2, E, R, sq, n)
    chains_v2_d5 = [c[:5] for c in chains_v2]
    r_f_fwd = arm_meta_m7_rail_replicate(E, R, sq, W_v2, chains_v2_d5, depth=5)
    r_f_bid = arm_meta_m7_bidir_replicate(E, R, sq, W_v2, chains_v2_d5, depth=5)
    assert 0.0 <= r_f_fwd["top1"] <= 1.0
    assert 0.0 <= r_f_bid["top1"] <= 1.0

    # T8: sacred sanity (K=1)
    r_g = arm_sacred_sanity_k1(E, R, sq, W, chains_d5)
    assert 0.0 <= r_g["top1"] <= 1.0
    assert r_g["depth"] == 1

    # T9: forward/backward state math on clean 1-hop W (GPU tensors)
    g2 = np.random.default_rng(1)
    E1 = bipolar_torch(V, n, g2)
    R1 = bipolar_torch(4, n, g2)
    triple_1hop = [(0, 0, 1)]
    W1 = ingest_hebbian_torch(triple_1hop, E1, R1, sq, n)
    fwd_state = W1 @ (E1[0] * R1[0] * sq)
    fwd_cos = float((fwd_state @ E1[1]) /
                    (fwd_state.norm() * E1[1].norm() + 1e-8))
    bwd_state = (W1.t() @ E1[1]) * R1[0] * sq
    bwd_cos = float((bwd_state @ E1[0]) /
                    (bwd_state.norm() * E1[0].norm() + 1e-8))
    assert fwd_cos > 0.2, "selftest forward-cos=%.3f too low" % fwd_cos
    assert bwd_cos > 0.2, "selftest backward-cos=%.3f too low" % bwd_cos

    # T10: cleanup primitive determinism
    s_chain = chains[0][0][0]
    p_chain = chains[0][0][1]
    direct = _retrieve_1hop_t(E, W, R, s_chain, p_chain, sq)
    s_walk = _retrieve_1hop_t(E, W, R, s_chain, p_chain, sq)
    assert direct == s_walk, "META_M7 selftest: cleanup primitive byte-equivalence broken"

    # T11: cardinality constants honored
    assert HARD_FAIL_CARDINALITY_BREACH_FULL == 125
    assert HARD_FAIL_CARDINALITY_BREACH_SMOKE == 7
    assert len(DEPTHS) == EXPECTED_N_DEPTHS

    # T12: bands locked (numeric value asserts)
    assert HP_BIDIR_D9_FLOOR == 0.45
    assert HP_BIDIR_OVER_HALF == 0.10
    assert HP_BIDIR_OVER_RANDOM == 0.15
    assert HP_META_M7_REPLICATE_FLOOR == 0.60
    assert META_M7_RAIL_LO == 0.08 and META_M7_RAIL_HI == 0.25
    assert _LLM_CALL_COUNTER[0] == 0

    # T13: GPU batched-backward equivalence with single-Z loop (GPU-specific gate)
    # Verifies the load-bearing GPU optimization preserves arm-B semantics.
    g3 = np.random.default_rng(2)
    E3 = bipolar_torch(V, n, g3)
    R3 = bipolar_torch(4, n, g3)
    triples3, chains3 = make_deep_chains(4, V, 4, max_depth=5, g=g3, disallow_s=set())
    W3 = ingest_hebbian_torch(triples3, E3, R3, sq, n)
    preds_test = [chains3[0][i][1] for i in range(5)]
    # batched: all V backward states at once
    bstates_batch = _backward_state_all_Z(E3, W3, R3, sq, preds_test[2:])
    # single-Z reference loop
    for Z in [0, 1, 5, 17, V - 1]:
        ref = _backward_state_t(E3, W3, R3, sq, Z, preds_test[2:])
        diff = float((bstates_batch[Z] - ref).abs().max().item())
        assert diff < 1e-4, "T13: batched-backward mismatch at Z=%d diff=%.2e" % (Z, diff)

    print("[selftest] PASS a=%.3f b=%.3f c=%.3f d=%.3f e=%.3f f_fwd=%.3f f_bid=%.3f g=%.3f "
          "fwd_cos=%.3f bwd_cos=%.3f device=%s"
          % (r_a["top1"], r_b["top1"], r_c["top1"], r_d["top1"], r_e["top1"],
             r_f_fwd["top1"], r_f_bid["top1"], r_g["top1"], fwd_cos, bwd_cos,
             torch.cuda.get_device_name(0)), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ============================================================
# Per-seed run (GPU; encoder + W hoisted per Fix #24)
# ============================================================
def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)

    # HOISTED (Fix #24): encoder + W built ONCE per seed and reused across all arms/depths.
    E = bipolar_torch(V_CONCEPTS, N_DIM, g)
    R = bipolar_torch(n_predicates, N_DIM, g)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "n_predicates": n_predicates,
        "v1_regime_n_chains": POINTER_N_CHAINS,
        "pointer_v2_n_chains": POINTER_V2_N_CHAINS_LOCAL,
        "pointer_v2_max_depth": POINTER_V2_MAX_DEPTH,
        "depths": SMOKE_DEPTHS if RUN_MODE == "smoke" else DEPTHS,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "device": "cuda",
        "gpu_name": torch.cuda.get_device_name(0),
        "by_depth": {},
    }

    # Build v1-regime W: chains long enough for max depth (9 in full mode)
    max_depth_run = max(SMOKE_DEPTHS if RUN_MODE == "smoke" else DEPTHS)
    t_arm = time.time()
    v1_triples, v1_chains = make_deep_chains(
        POINTER_N_CHAINS, V_CONCEPTS, POINTER_V_P,
        max_depth=max_depth_run, g=g, disallow_s=set())
    W_v1 = ingest_hebbian_torch(v1_triples, E, R, sq, N_DIM)
    out["v1_regime_W_n_bindings"] = len(v1_triples)
    print("  [seed=%d] v1-regime W built on GPU (%d triples, max_depth=%d) t=%.1fs" % (
        seed, len(v1_triples), max_depth_run, round(time.time() - t_arm, 2)), flush=True)

    # Build pointer-v2-regime W (for arm F at d=5 only)
    t_arm = time.time()
    v2_triples, v2_chains = make_deep_chains(
        POINTER_V2_N_CHAINS_LOCAL, V_CONCEPTS, POINTER_V_P,
        max_depth=POINTER_V2_MAX_DEPTH, g=g, disallow_s=set())
    W_v2 = ingest_hebbian_torch(v2_triples, E, R, sq, N_DIM)
    out["v2_regime_W_n_bindings"] = len(v2_triples)
    print("  [seed=%d] pointer-v2-regime W built on GPU (%d triples, depth=%d) t=%.1fs" % (
        seed, len(v2_triples), POINTER_V2_MAX_DEPTH,
        round(time.time() - t_arm, 2)), flush=True)

    # SACRED SANITY (G): depth-independent, run once
    t_arm = time.time()
    v1_chains_d1 = [[c[0]] for c in v1_chains]
    r_g = arm_sacred_sanity_k1(E, R, sq, W_v1, v1_chains_d1)
    r_g["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_sacred_sanity_k1"] = r_g
    print("  [seed=%d] SACRED_SANITY_K1 top1=%.4f t=%.1fs" % (
        seed, r_g["top1"], r_g["elapsed_s_arm"]), flush=True)
    sanity_ok = (SACRED_SANITY_LO <= r_g["top1"] <= SACRED_SANITY_HI)
    out["sacred_sanity_ok"] = sanity_ok

    # Per-depth loop: A, B, C, D, E (v1-regime W) + F_fwd, F_bid (v2-regime W at d=5)
    depths_to_run = SMOKE_DEPTHS if RUN_MODE == "smoke" else DEPTHS
    for depth in depths_to_run:
        depth_rec: Dict[str, Any] = {"depth": depth}
        v1_chains_test = [c[:depth] for c in v1_chains]

        # A: forward full depth
        t_arm = time.time()
        r_a = arm_baseline_forward_full_depth(E, R, sq, W_v1, v1_chains_test, depth)
        r_a["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        depth_rec["arm_baseline_forward_full_depth"] = r_a
        print("    [seed=%d d=%d] A_FWD_FULL top1=%.4f t=%.1fs" % (
            seed, depth, r_a["top1"], r_a["elapsed_s_arm"]), flush=True)

        # B: bidir meet mid (THE MECHANISM)
        t_arm = time.time()
        r_b = arm_bidir_meet_mid(E, R, sq, W_v1, v1_chains_test, depth)
        r_b["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        depth_rec["arm_bidir_meet_mid"] = r_b
        print("    [seed=%d d=%d] B_BIDIR_MEET_MID top1=%.4f t=%.1fs" % (
            seed, depth, r_b["top1"], r_b["elapsed_s_arm"]), flush=True)

        # C: forward half depth (control)
        t_arm = time.time()
        r_c = arm_forward_half_depth(E, R, sq, W_v1, v1_chains_test, depth)
        r_c["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        depth_rec["arm_forward_half_depth"] = r_c
        print("    [seed=%d d=%d] C_FWD_HALF top1=%.4f t=%.1fs" % (
            seed, depth, r_c["top1"], r_c["elapsed_s_arm"]), flush=True)

        # D: random meet baseline (control)
        t_arm = time.time()
        r_d = arm_random_meet_baseline(E, R, sq, W_v1, v1_chains_test, depth, seed=seed)
        r_d["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        depth_rec["arm_random_meet_baseline"] = r_d
        print("    [seed=%d d=%d] D_RANDOM_MEET top1=%.4f t=%.1fs" % (
            seed, depth, r_d["top1"], r_d["elapsed_s_arm"]), flush=True)

        # E: multiscale bidir
        t_arm = time.time()
        r_e = arm_multiscale_bidirectional(E, R, sq, W_v1, v1_chains_test, depth)
        r_e["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        depth_rec["arm_multiscale_bidirectional"] = r_e
        print("    [seed=%d d=%d] E_MULTISCALE top1=%.4f t=%.1fs" % (
            seed, depth, r_e["top1"], r_e["elapsed_s_arm"]), flush=True)

        # F: META_M7 rail replicate (only at d=5)
        if depth == 5:
            v2_chains_d5 = [c[:5] for c in v2_chains]
            t_arm = time.time()
            r_f_fwd = arm_meta_m7_rail_replicate(E, R, sq, W_v2, v2_chains_d5, depth=5)
            r_f_fwd["elapsed_s_arm"] = round(time.time() - t_arm, 2)
            depth_rec["arm_meta_m7_rail_forward"] = r_f_fwd
            meta_m7_fwd_ok = (META_M7_RAIL_LO <= r_f_fwd["top1"] <= META_M7_RAIL_HI)
            depth_rec["meta_m7_rail_forward_ok"] = meta_m7_fwd_ok
            print("    [seed=%d d=5] F_META_M7_FWD top1=%.4f ok=%s t=%.1fs" % (
                seed, r_f_fwd["top1"], meta_m7_fwd_ok, r_f_fwd["elapsed_s_arm"]), flush=True)

            t_arm = time.time()
            r_f_bid = arm_meta_m7_bidir_replicate(E, R, sq, W_v2, v2_chains_d5, depth=5)
            r_f_bid["elapsed_s_arm"] = round(time.time() - t_arm, 2)
            depth_rec["arm_meta_m7_bidir_replicate"] = r_f_bid
            print("    [seed=%d d=5] F_META_M7_BIDIR top1=%.4f t=%.1fs" % (
                seed, r_f_bid["top1"], r_f_bid["elapsed_s_arm"]), flush=True)

        out["by_depth"][str(depth)] = depth_rec

        # OOM-prevention between depth iterations (Fix #24 hygiene)
        torch.cuda.empty_cache()

    # Cardinality check
    expected = (HARD_FAIL_CARDINALITY_BREACH_SMOKE if RUN_MODE == "smoke"
                else HARD_FAIL_CARDINALITY_BREACH_FULL)
    actual_records = sum(
        len([k for k in d.keys() if k.startswith("arm_")])
        for d in out["by_depth"].values()
    ) + 1
    out["cardinality_records_per_seed"] = actual_records
    out["cardinality_ok"] = (actual_records >= 8 if RUN_MODE == "smoke" else actual_records >= 23)

    # Per-depth lift summary
    lift_summary = {}
    for d_str, drec in out["by_depth"].items():
        d = int(d_str)
        bidir = drec["arm_bidir_meet_mid"]["top1"]
        fwd_half = drec["arm_forward_half_depth"]["top1"]
        rand = drec["arm_random_meet_baseline"]["top1"]
        lift_summary[d_str] = {
            "bidir_vs_fwd_half": round(bidir - fwd_half, 4),
            "bidir_vs_random": round(bidir - rand, 4),
        }
    out["lift_per_depth"] = lift_summary

    out["elapsed_s"] = round(time.time() - t, 1)

    # Free per-seed GPU memory before next seed's encoder rebuilds
    del E, R, W_v1, W_v2
    torch.cuda.empty_cache()

    return out


# ============================================================
# Verdict (identical to numpy v3)
# ============================================================
def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def mean_at(depth: int, arm: str) -> float:
        vals = []
        for p in per_seed:
            drec = p.get("by_depth", {}).get(str(depth))
            if drec and arm in drec:
                t1 = drec[arm].get("top1")
                if isinstance(t1, (int, float)) and not math.isnan(t1):
                    vals.append(t1)
        return float(np.mean(vals)) if vals else float("nan")

    def cv_at(depth: int, arm: str) -> float:
        vals = []
        for p in per_seed:
            drec = p.get("by_depth", {}).get(str(depth))
            if drec and arm in drec:
                t1 = drec[arm].get("top1")
                if isinstance(t1, (int, float)) and not math.isnan(t1):
                    vals.append(t1)
        if len(vals) < 2:
            return float("nan")
        m = float(np.mean(vals))
        return float(np.std(vals) / max(m, 1e-9))

    depths_seen = sorted({int(d) for p in per_seed for d in p.get("by_depth", {}).keys()})

    table_rows = []
    for d in depths_seen:
        a = mean_at(d, "arm_baseline_forward_full_depth")
        b = mean_at(d, "arm_bidir_meet_mid")
        c = mean_at(d, "arm_forward_half_depth")
        rd = mean_at(d, "arm_random_meet_baseline")
        e = mean_at(d, "arm_multiscale_bidirectional")
        b_cv = cv_at(d, "arm_bidir_meet_mid")
        table_rows.append("d=%d:fwd=%.3f bidir=%.3f(cv=%.3f) fwd_half=%.3f rand=%.3f mscale=%.3f"
                          % (d, a, b, b_cv, c, rd, e))

    sanity_breaches = sum(1 for p in per_seed if not p.get("sacred_sanity_ok", True))

    bias_q_flags = []
    for p in per_seed:
        for d_str, drec in p.get("by_depth", {}).items():
            for arm_name, arm_data in drec.items():
                if arm_name.startswith("arm_"):
                    t1 = arm_data.get("top1")
                    if isinstance(t1, (int, float)) and t1 >= 0.999:
                        bias_q_flags.append("seed=%d d=%s arm=%s top1=%.4f" % (
                            p.get("seed", -1), d_str, arm_name, t1))

    bidir_d9 = mean_at(9, "arm_bidir_meet_mid") if 9 in depths_seen else float("nan")
    cond1 = (not math.isnan(bidir_d9)) and bidir_d9 >= HP_BIDIR_D9_FLOOR

    cond2 = True
    cond2_fail = []
    for d in depths_seen:
        b = mean_at(d, "arm_bidir_meet_mid")
        c = mean_at(d, "arm_forward_half_depth")
        if math.isnan(b) or math.isnan(c) or b < c + HP_BIDIR_OVER_HALF:
            cond2 = False
            cond2_fail.append("d=%d:bidir=%.3f<fwd_half=%.3f+%.2f" % (d, b, c, HP_BIDIR_OVER_HALF))

    cond3 = True
    cond3_fail = []
    for d in depths_seen:
        b = mean_at(d, "arm_bidir_meet_mid")
        rd = mean_at(d, "arm_random_meet_baseline")
        if math.isnan(b) or math.isnan(rd) or b < rd + HP_BIDIR_OVER_RANDOM:
            cond3 = False
            cond3_fail.append("d=%d:bidir=%.3f<rand=%.3f+%.2f" % (d, b, rd, HP_BIDIR_OVER_RANDOM))

    m7_bidir_d5 = mean_at(5, "arm_meta_m7_bidir_replicate") if 5 in depths_seen else float("nan")
    cond4 = (not math.isnan(m7_bidir_d5)) and m7_bidir_d5 >= HP_META_M7_REPLICATE_FLOOR

    conds = [cond1, cond2, cond3, cond4]
    n_pass = sum(conds)

    hard_fail_collapse = (not math.isnan(bidir_d9)) and bidir_d9 < HF_BIDIR_D9_COLLAPSE

    hard_fail_no_premium = False
    no_premium_at = []
    for d in depths_seen:
        if d < 5:
            continue
        b = mean_at(d, "arm_bidir_meet_mid")
        c = mean_at(d, "arm_forward_half_depth")
        if not math.isnan(b) and not math.isnan(c) and b <= c + HF_BIDIR_OVER_HALF_BREACH:
            hard_fail_no_premium = True
            no_premium_at.append("d=%d:bidir=%.3f<=fwd_half=%.3f+%.2f" % (
                d, b, c, HF_BIDIR_OVER_HALF_BREACH))

    summ = ("DEPTH_SCALING_v3_GPU: %s | cond1(d9>=%.2f)=%s(%.3f) cond2(over_half>=%.2f)=%s "
            "cond3(over_rand>=%.2f)=%s cond4(m7_bidir_d5>=%.2f)=%s(%.3f) | "
            "sanity_breach=%d/%d bias_q=%d") % (
        "; ".join(table_rows),
        HP_BIDIR_D9_FLOOR, cond1, bidir_d9,
        HP_BIDIR_OVER_HALF, cond2,
        HP_BIDIR_OVER_RANDOM, cond3,
        HP_META_M7_REPLICATE_FLOOR, cond4, m7_bidir_d5,
        sanity_breaches, len(per_seed),
        len(bias_q_flags),
    )
    if cond2_fail:
        summ += " | cond2_fails=" + ",".join(cond2_fail)
    if cond3_fail:
        summ += " | cond3_fails=" + ",".join(cond3_fail)
    if no_premium_at:
        summ += " | no_premium_at=" + ",".join(no_premium_at)
    if bias_q_flags:
        summ += " | BIAS_Q_FLAGS=" + ";".join(bias_q_flags[:3])

    if sanity_breaches >= max(1, (len(per_seed) + 1) // 2):
        return "SANITY_BREACH", "SANITY_BREACH_K1_OUT_OF_BAND: " + summ

    if hard_fail_collapse:
        return "HARD_FAIL_NO_DEPTH_SCALING", \
               "HARD_FAIL_NO_DEPTH_SCALING_bidir_d9_below_%.2f: " % HF_BIDIR_D9_COLLAPSE + summ

    if hard_fail_no_premium:
        return "HARD_FAIL_NO_MEETING_PREMIUM", \
               "HARD_FAIL_NO_MEETING_PREMIUM_bidir_indistinguishable_from_fwd_half: " + summ

    if n_pass == 4:
        return "HARD_PASS_CHAIN_GRADE_DEPTH_SCALING", \
               "HARD_PASS_CHAIN_GRADE_DEPTH_SCALING_sqrt_style_survival_meeting_premium_true_midpoint: " + summ

    if n_pass >= 2:
        return "MIDDLE_BAND_PARTIAL_DEPTH_SCALING", \
               "MIDDLE_BAND_PARTIAL_DEPTH_SCALING_%d_of_4_conditions: " % n_pass + summ

    return "MIDDLE_BAND_WEAK", "MIDDLE_BAND_WEAK_%d_of_4_conditions: " % n_pass + summ


_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        if (od / "metrics.json").exists():
            return
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)
        raise


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d depths=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM,
        SMOKE_DEPTHS if RUN_MODE == "smoke" else DEPTHS,
        CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS], run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "device": "cuda",
        "gpu_name": torch.cuda.get_device_name(0),
        "DESIGN_NOTE": (
            "V3 GPU port of depth-scaling cell. Per Fix #24 GPU mandate: torch.cuda + "
            "batched candidate scoring (V_C backward states computed in one matmul instead "
            "of V_C separate matvecs); encoder + W hoisted per seed; empty_cache between "
            "depths. Semantics identical to numpy v3 (same arms / depths / seeds / HARD_PASS "
            "conditions / bands). T13 self-test verifies batched-vs-loop equivalence to <1e-4. "
            "v1/v2 ran depth=5 and chain-graded BIDIR_MEET_MID=0.620 (cv=0.064). V3 tests "
            "sqrt-style scaling at d in {3,5,7,9}, ARM_FORWARD_HALF_DEPTH (meeting > shorter), "
            "ARM_RANDOM_MEET_BASELINE (true midpoint matters), ARM_MULTISCALE_BIDIRECTIONAL "
            "(scale-invariance), ARM_META_M7_RAIL_REPLICATE/_BIDIR (regime-drift). 5 seeds for "
            "depth-scaling stability. Per drill 2026-06-27 HARD_PASS requires: (1) bidir d=9 "
            ">= 0.45 (2) bidir >= fwd_half + 0.10 EVERY depth (3) bidir >= random + 0.15 EVERY "
            "depth (4) m7_bidir d=5 >= 0.60."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
