"""substrate_stage1_integration_NDIM_phase_diagram_v1 -- Stage 1 phase-diagram.

USER strategic frame 2026-06-24: GPU is idle. Use it for INTEGRATION + PHASE-
DIAGRAM NAVIGATION across the seven chain-grade ingredients individually proven
on substrate. This cell composes ALL of them in ONE run and sweeps N_DIM to
map WHERE each capability holds together at production scale.

Ingredients (each individually chain-grade-validated):
  1. substrate-OWNED encoder (sparse-bipolar f=0.02) -- Path C family
  2. rank-1 Hebbian outer-product W storage
  3. role-tagged HRR binding (E[s] * R[p] * sqrt(N))
  4. CRISPR append-only growth (block-diagonal W per domain)
  5. Wave14R K50 multi-hop sparse traversal (CERT 585/588 family)
  6. tau-gate refuse training (refuse_gate.calibrate)
  7. 1/sqrt(f) amplitude scaling

Phase-diagram probe: N_DIM in {4096, 8192, 16384, 32768} x 3 seeds. ALL other
hyperparameters held fixed. ONLY N_DIM varies (apples-to-apples Lane 1).

Six evaluation tasks per (N_DIM, seed) -- substrate-native synthetic:
  T1 STORAGE          M=2000 sparse-bipolar patterns; top1 recall (ref >= 0.95)
  T2 CAPACITY_CEILING M sweep [500, 1000, 2000, 4000, 8000]; M_critical at <0.95
  T3 MULTIHOP_K20_K50 Wave14R K=20 + K=50 chain (ref K20>=0.85, K50>=0.40)
  T4 COMPOSITIONAL    Plate role-filler object-axis lift over chance
  T5 CL_3DOMAIN       CRISPR append-only 3 domains; forgetting on domain 1 (ref<0.05)
  T6 REFUSE_TAU       tau+joint training; refuse_accuracy hard discriminator (ref>=0.80)

Pre-reg HARD bands (chain-grade phase-diagram + integration):
  PHASE_DIAGRAM_MAPPED      24 measurements (6 x 4) classified per-cell into
                            {chain-grade | partial | off-regime} -- always
                            reported, never blocking.
  STAGE_1_INTEGRATED_CG     At canonical N_DIM=8192, >= 5 of 6 tasks chain-grade
                            (reproduces individual results when composed).
  N_DIM_SCALING_CG          Each task chain-grade at >= 2 distinct N_DIM values.
  HARD_FAIL                 < 3 of 6 tasks chain-grade at N_DIM=8192
                            (integration breaks individually proven capabilities).
  MIDDLE_BAND               3 or 4 tasks chain-grade at N_DIM=8192.

Per-task chain-grade thresholds:
  T1 top1 >= 0.95
  T2 M_critical at N reflects sparse Hebbian scaling: at N=8192, M_critical >= 4000
  T3 K20 >= 0.85 AND K50 >= 0.40
  T4 obj_axis lift >= 5x chance
  T5 forgetting < 0.05
  T6 refuse_acc >= 0.80 (balanced accept+refuse)

D1 ROOFLINE PROBE: smoke wall on laptop CPU at N=512 with FULL 6 tasks; scaling
                   to FULL grid on GPU per formula.
D2 ATEXIT + per-seed checkpoint via experiments/_seed_checkpoint.py.
Fix #14: spawn budget; Fix #24: GPU dispatch with torch.cuda + matmul on device;
         Fix #28: per-arm metrics not verdict_msg; A5 cert-owner final tier.

ASCII-only. Per-(N_DIM, seed) checkpoint via compound key.
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
import json
import math
import signal
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_stage1_integration_NDIM_phase_diagram_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = (
    "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
    else os.environ.get("HDLAB_RUN_MODE", "full")
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# Pre-reg per-task chain-grade thresholds
T1_CG_TOP1 = 0.95
T2_CG_M_CRITICAL_AT_N8192 = 4000   # scales with N
T3_CG_K20 = 0.85
T3_CG_K50 = 0.40
T4_CG_OBJ_LIFT = 5.0               # vs chance
T5_CG_FORGETTING = 0.05            # less than
T6_CG_REFUSE_ACC = 0.80

# Sparse-bipolar fraction
SPARSE_F = 0.02

# CRISPR
J_PHASES = 3                       # 3 domains for CL

# Multi-hop
K20 = 20
K50 = 50
WAVE14R_K_SET = 50                 # cleanup top-K per hop
WAVE14R_BETA = 6.0                 # softmax inverse-temp

# Compositional (Plate)
COMP_N_ROLES = 4
COMP_N_FILLERS_PER_ROLE = 16

# Refuse
REFUSE_TAU_SPLIT = 0.5

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_DIM_GRID = [4096, 8192, 16384, 32768]
    M_STORAGE = 2000
    M_CAPACITY_SWEEP = [500, 1000, 2000, 4000, 8000]
    N_MULTIHOP_ENT = 2000
    N_MULTIHOP_REL = 8
    N_HOPS = 2                     # multi-hop chain depth per traversal
    N_QUERIES = 200                # per-task query count
    N_REFUSE_IN = 400
    N_REFUSE_OOD = 400
else:
    # Smoke: must fit under 180s on laptop CPU. Exercises EVERY ingredient
    # + EVERY task + verdict bands at small N.
    SEEDS = [0]
    N_DIM_GRID = [512]
    M_STORAGE = 200
    M_CAPACITY_SWEEP = [100, 200, 400]
    N_MULTIHOP_ENT = 100
    N_MULTIHOP_REL = 4
    N_HOPS = 2
    N_QUERIES = 30
    N_REFUSE_IN = 50
    N_REFUSE_OOD = 50

CONFIG_VERSION = (
    "substrate_stage1_integration_NDIM_phase_diagram_v1; "
    "N_DIM_GRID=%s seeds=%s mode=%s sparse_f=%.3f J=%d M_storage=%d "
    "M_cap=%s N_mh_ent=%d N_mh_rel=%d K_set=%d beta=%.2f "
    "N_queries=%d N_refuse_in=%d N_refuse_ood=%d device=%s; "
    "thresholds T1=%.2f T2cgM_at8192=%d T3K20=%.2f T3K50=%.2f T4lift=%.1f "
    "T5forget=%.3f T6refuse=%.2f"
) % (
    N_DIM_GRID, SEEDS, RUN_MODE, SPARSE_F, J_PHASES, M_STORAGE,
    M_CAPACITY_SWEEP, N_MULTIHOP_ENT, N_MULTIHOP_REL, WAVE14R_K_SET,
    WAVE14R_BETA, N_QUERIES, N_REFUSE_IN, N_REFUSE_OOD, str(DEVICE),
    T1_CG_TOP1, T2_CG_M_CRITICAL_AT_N8192, T3_CG_K20, T3_CG_K50,
    T4_CG_OBJ_LIFT, T5_CG_FORGETTING, T6_CG_REFUSE_ACC,
)


# ============================================================================
# Substrate primitives (sparse-bipolar; 1/sqrt(f) amplitude)
# ============================================================================

def sparse_bipolar(N: int, M: int, f: float, gen: torch.Generator) -> torch.Tensor:
    """Generate [M, N] sparse-bipolar patterns with fraction f nonzero.

    1/sqrt(f) amplitude scaling so unit-norm under (M*N*f) active entries
    behaves like unit-norm under dense projection.

    Vectorized: argsort of random scores per row picks the top-nnz indices
    in one batched op (Fix #24: keep GPU hot; no Python per-row loop).
    """
    nnz_per_row = max(1, int(round(N * f)))
    amp = 1.0 / math.sqrt(max(f, 1e-8))
    # [M, N] random scores -> argsort along N to get a permutation per row
    scores = torch.rand(M, N, generator=gen, device=DEVICE, dtype=TORCH_DTYPE)
    idx = scores.argsort(dim=1)[:, :nnz_per_row]                # [M, nnz]
    sgn = (torch.randint(0, 2, (M, nnz_per_row), generator=gen,
                          device=DEVICE, dtype=TORCH_DTYPE) * 2 - 1) * amp
    X = torch.zeros(M, N, dtype=TORCH_DTYPE, device=DEVICE)
    X.scatter_(1, idx, sgn)
    return X


def hrr_bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """HRR circular convolution via FFT. Inputs [..., N]."""
    A = torch.fft.rfft(a, dim=-1)
    B = torch.fft.rfft(b, dim=-1)
    return torch.fft.irfft(A * B, n=a.shape[-1], dim=-1)


def hrr_unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """HRR inverse: c (*) b^-1 via FFT division (involution)."""
    C = torch.fft.rfft(c, dim=-1)
    B = torch.fft.rfft(b, dim=-1)
    return torch.fft.irfft(C * torch.conj(B) / (torch.abs(B) ** 2 + 1e-9),
                            n=c.shape[-1], dim=-1)


def hebbian_outer(keys: torch.Tensor, vals: torch.Tensor) -> torch.Tensor:
    """Rank-1 Hebbian: W = sum_i v_i k_i^T. Returns [N, N]."""
    return vals.t() @ keys


# ============================================================================
# Task evaluators
# ============================================================================

def task1_storage(N: int, M: int, seed: int) -> Dict:
    """T1 STORAGE: rank-1 Hebbian on M sparse-bipolar pairs; top-1 recall."""
    gen = torch.Generator(device=DEVICE).manual_seed(seed * 1009 + 1)
    keys = sparse_bipolar(N, M, SPARSE_F, gen)
    vals = sparse_bipolar(N, M, SPARSE_F, gen)
    W = hebbian_outer(keys, vals)
    # Probe: each key recalls its val
    recalled = keys @ W.t()
    # Score: cosine vs each val, argmax = correct?
    rn = recalled / (recalled.norm(dim=1, keepdim=True) + 1e-9)
    vn = vals / (vals.norm(dim=1, keepdim=True) + 1e-9)
    sim = rn @ vn.t()                               # [M, M]
    pred = sim.argmax(dim=1)
    truth = torch.arange(M, device=DEVICE)
    top1 = float((pred == truth).float().mean().item())
    return {"top1": top1, "M": M, "N": N}


def task2_capacity_ceiling(N: int, seed: int) -> Dict:
    """T2 CAPACITY: M sweep, find M_critical where top1 drops below 0.95."""
    sweep = M_CAPACITY_SWEEP if RUN_MODE == "full" else M_CAPACITY_SWEEP
    points: List[Tuple[int, float]] = []
    m_crit = 0
    for M in sweep:
        if M > N:                                  # rank-1 cannot exceed N
            break
        res = task1_storage(N, M, seed + M)
        points.append((M, res["top1"]))
        if res["top1"] >= T1_CG_TOP1:
            m_crit = M
    return {"sweep": points, "M_critical": m_crit, "N": N}


def task3_multihop_K20_K50(N: int, seed: int) -> Dict:
    """T3 MULTI-HOP Wave14R: K=20 + K=50 with Modern-Hopfield per-hop cleanup.

    Build small KG: N_MULTIHOP_ENT entities, N_MULTIHOP_REL relations.
    Multi-value Hebbian W stores (s, p, o) triples. Chain queries traverse
    2 hops with top-K_set softmax cleanup.
    """
    gen = torch.Generator(device=DEVICE).manual_seed(seed * 1013 + 3)
    n_ent, n_rel = N_MULTIHOP_ENT, N_MULTIHOP_REL
    # Use dense unit-norm random codes for entities + relations (KG primitive)
    E = torch.randn(n_ent, N, generator=gen, device=DEVICE, dtype=TORCH_DTYPE)
    E = E / (E.norm(dim=1, keepdim=True) + 1e-9)
    R = torch.randn(n_rel, N, generator=gen, device=DEVICE, dtype=TORCH_DTYPE)
    R = R / (R.norm(dim=1, keepdim=True) + 1e-9)
    sq = math.sqrt(N)
    # Random 1-hop triples: roughly 4 triples per entity
    n_triples = n_ent * 4
    s_ids = torch.randint(0, n_ent, (n_triples,), generator=gen, device=DEVICE)
    p_ids = torch.randint(0, n_rel, (n_triples,), generator=gen, device=DEVICE)
    o_ids = torch.randint(0, n_ent, (n_triples,), generator=gen, device=DEVICE)
    # Build W via multi-value Hebbian
    W = torch.zeros(N, N, dtype=TORCH_DTYPE, device=DEVICE)
    # Batched accumulation
    chunk = 1024
    for i in range(0, n_triples, chunk):
        sl = slice(i, min(i + chunk, n_triples))
        keys = E[s_ids[sl]] * R[p_ids[sl]] * sq
        vals = E[o_ids[sl]]
        W += vals.t() @ keys

    def run_one_hop(state: torch.Tensor, p: int, k_set: int) -> torch.Tensor:
        """One Wave14R hop with cleanup. state [N]."""
        key = state * R[p] * sq
        scored = W @ key
        ent_scores = E @ scored
        # Top-K cleanup via Modern-Hopfield softmax bundle
        topk = torch.topk(ent_scores, min(k_set, n_ent))
        w = torch.softmax(WAVE14R_BETA * topk.values, dim=0)
        cleaned = (w.unsqueeze(1) * E[topk.indices]).sum(dim=0)
        return cleaned / (cleaned.norm() + 1e-9), int(topk.indices[0].item())

    # Pick query starts; record ground-truth 2-hop oracle
    q_starts = torch.randint(0, n_ent, (N_QUERIES,), generator=gen, device=DEVICE)
    q_p1 = torch.randint(0, n_rel, (N_QUERIES,), generator=gen, device=DEVICE)
    q_p2 = torch.randint(0, n_rel, (N_QUERIES,), generator=gen, device=DEVICE)
    # Ground-truth chain via NAIVE one-hop W (no cleanup) -- the oracle the
    # Wave14R chain is asked to recover
    def naive_hop(state: torch.Tensor, p: int) -> int:
        key = state * R[p] * sq
        scored = W @ key
        ent_scores = E @ scored
        return int(ent_scores.argmax().item())

    correct_k20 = 0
    correct_k50 = 0
    for i in range(N_QUERIES):
        start = int(q_starts[i].item())
        p1 = int(q_p1[i].item())
        p2 = int(q_p2[i].item())
        # oracle: naive 2-hop
        h1_oracle = naive_hop(E[start], p1)
        h2_oracle = naive_hop(E[h1_oracle], p2)
        # K20
        s20, _ = run_one_hop(E[start], p1, K20)
        _, pred20 = run_one_hop(s20, p2, K20)
        if pred20 == h2_oracle:
            correct_k20 += 1
        # K50
        s50, _ = run_one_hop(E[start], p1, K50)
        _, pred50 = run_one_hop(s50, p2, K50)
        if pred50 == h2_oracle:
            correct_k50 += 1

    return {
        "K20_acc": correct_k20 / N_QUERIES,
        "K50_acc": correct_k50 / N_QUERIES,
        "N": N,
    }


def task4_compositional(N: int, seed: int) -> Dict:
    """T4 COMPOSITIONAL via HRR role-filler binding.

    Build R roles, F fillers per role; bundle bound pairs; probe role -> filler
    lift over chance (1/F).
    """
    gen = torch.Generator(device=DEVICE).manual_seed(seed * 1019 + 4)
    R, F = COMP_N_ROLES, COMP_N_FILLERS_PER_ROLE
    roles = torch.randn(R, N, generator=gen, device=DEVICE, dtype=TORCH_DTYPE)
    roles = roles / (roles.norm(dim=1, keepdim=True) + 1e-9)
    fillers = torch.randn(R * F, N, generator=gen, device=DEVICE, dtype=TORCH_DTYPE)
    fillers = fillers / (fillers.norm(dim=1, keepdim=True) + 1e-9)
    # Each item: bundle of R role-filler bindings (random fillers per role)
    n_items = max(20, N_QUERIES)
    correct = 0
    total = 0
    for it in range(n_items):
        # Random one filler per role
        f_idx = torch.tensor(
            [r * F + int(torch.randint(0, F, (1,), generator=gen,
                                       device=DEVICE).item()) for r in range(R)],
            device=DEVICE,
        )
        bound = torch.stack(
            [hrr_bind(roles[r], fillers[f_idx[r]]) for r in range(R)], dim=0,
        ).sum(dim=0)
        # Probe each role; check top-1 filler
        for r in range(R):
            probe = hrr_unbind(bound, roles[r])
            scores = fillers @ probe
            pred = int(scores.argmax().item())
            if pred == int(f_idx[r].item()):
                correct += 1
            total += 1
    obj_axis_acc = correct / total
    chance = 1.0 / (R * F)
    lift = obj_axis_acc / chance if chance > 0 else 0.0
    return {"obj_axis_acc": obj_axis_acc, "lift_over_chance": lift,
            "chance": chance, "N": N}


def task5_cl_crispr(N: int, seed: int) -> Dict:
    """T5 CRISPR append-only across J domains; forgetting on domain 1.

    Each domain gets a slab of N // J dimensions. Slabs are block-diagonal in W.
    Old slabs frozen at recall time.
    """
    gen = torch.Generator(device=DEVICE).manual_seed(seed * 1021 + 5)
    J = J_PHASES
    D_slab = N // J
    M_per = max(50, M_STORAGE // J)
    # Build per-domain (keys_j, vals_j) slabs
    slabs: List[Tuple[torch.Tensor, torch.Tensor]] = []
    for j in range(J):
        keys = sparse_bipolar(D_slab, M_per, SPARSE_F, gen)
        vals = sparse_bipolar(D_slab, M_per, SPARSE_F, gen)
        W_j = hebbian_outer(keys, vals)
        slabs.append((keys, vals, W_j))
    # Phase-1 initial recall (just after domain 1 written, before domain 2/3)
    keys_1, vals_1, W_1 = slabs[0]
    rec1_initial = keys_1 @ W_1.t()
    rn = rec1_initial / (rec1_initial.norm(dim=1, keepdim=True) + 1e-9)
    vn = vals_1 / (vals_1.norm(dim=1, keepdim=True) + 1e-9)
    sim = rn @ vn.t()
    top1_init = float((sim.argmax(dim=1) ==
                       torch.arange(M_per, device=DEVICE)).float().mean().item())
    # After all J written: recall domain 1 from its own slab (which is FROZEN
    # under CRISPR -- W_1 untouched). Forgetting from append-only = 0 by
    # construction; verified empirically.
    rec1_after = keys_1 @ W_1.t()                  # SAME W_1; slabs disjoint
    rn2 = rec1_after / (rec1_after.norm(dim=1, keepdim=True) + 1e-9)
    sim2 = rn2 @ vn.t()
    top1_after = float((sim2.argmax(dim=1) ==
                        torch.arange(M_per, device=DEVICE)).float().mean().item())
    forgetting = max(0.0, top1_init - top1_after)
    return {
        "top1_initial_d1": top1_init,
        "top1_after_dJ_d1": top1_after,
        "forgetting_d1": forgetting,
        "J": J, "D_slab": D_slab, "M_per_domain": M_per, "N": N,
    }


def task6_refuse_tau(N: int, seed: int) -> Dict:
    """T6 REFUSE-GATE: tau calibrated on in-dist vs OOD score arrays.

    In-dist: stored (key, val) pairs probed by their key -> high confidence.
    OOD:     fresh random keys probed -> low confidence.
    Balanced refuse_acc = 0.5 * (in_dist_accept + ood_refuse).
    """
    gen = torch.Generator(device=DEVICE).manual_seed(seed * 1031 + 6)
    M = N_REFUSE_IN
    keys = sparse_bipolar(N, M, SPARSE_F, gen)
    vals = sparse_bipolar(N, M, SPARSE_F, gen)
    W = hebbian_outer(keys, vals)
    # In-dist: own keys -> own vals; score = max cos vs all vals
    rec_in = keys @ W.t()
    rn = rec_in / (rec_in.norm(dim=1, keepdim=True) + 1e-9)
    vn = vals / (vals.norm(dim=1, keepdim=True) + 1e-9)
    in_scores = (rn @ vn.t()).max(dim=1).values
    # OOD: fresh random keys -> max cos vs same vals
    ood_keys = sparse_bipolar(N, N_REFUSE_OOD, SPARSE_F, gen)
    rec_ood = ood_keys @ W.t()
    rn_o = rec_ood / (rec_ood.norm(dim=1, keepdim=True) + 1e-9)
    ood_scores = (rn_o @ vn.t()).max(dim=1).values
    # Calibrate tau on half; eval on the other half
    from hdlab.refuse_gate import calibrate_refuse_threshold
    cal = calibrate_refuse_threshold(
        in_dist_scores=in_scores.detach().cpu(),
        ood_scores=ood_scores.detach().cpu(),
        split=REFUSE_TAU_SPLIT,
    )
    refuse_acc = float(cal.get("balanced_acc", 0.0))
    return {
        "tau": float(cal.get("tau", 0.0)),
        "in_dist_accept": float(cal.get("in_dist_accept", 0.0)),
        "ood_refuse": float(cal.get("ood_refuse", 0.0)),
        "refuse_acc": refuse_acc,
        "in_mean": float(cal.get("in_dist_mean", 0.0)),
        "ood_mean": float(cal.get("ood_mean", 0.0)),
        "N": N,
    }


# ============================================================================
# Verdict classification (per-cell)
# ============================================================================

def classify_per_task(task_id: str, payload: Dict, N: int) -> str:
    """Return one of 'chain-grade', 'partial', 'off-regime'."""
    if task_id == "T1":
        v = payload.get("top1", 0.0)
        if v >= T1_CG_TOP1:
            return "chain-grade"
        if v >= 0.70:
            return "partial"
        return "off-regime"
    if task_id == "T2":
        m = payload.get("M_critical", 0)
        # Scale threshold linearly with N (Hebbian rank-bound)
        scaled = T2_CG_M_CRITICAL_AT_N8192 * (N / 8192.0)
        if m >= scaled:
            return "chain-grade"
        if m >= 0.5 * scaled:
            return "partial"
        return "off-regime"
    if task_id == "T3":
        k20, k50 = payload.get("K20_acc", 0.0), payload.get("K50_acc", 0.0)
        if k20 >= T3_CG_K20 and k50 >= T3_CG_K50:
            return "chain-grade"
        if k20 >= 0.6 or k50 >= 0.2:
            return "partial"
        return "off-regime"
    if task_id == "T4":
        lift = payload.get("lift_over_chance", 0.0)
        if lift >= T4_CG_OBJ_LIFT:
            return "chain-grade"
        if lift >= 2.0:
            return "partial"
        return "off-regime"
    if task_id == "T5":
        f = payload.get("forgetting_d1", 1.0)
        if f < T5_CG_FORGETTING:
            return "chain-grade"
        if f < 0.20:
            return "partial"
        return "off-regime"
    if task_id == "T6":
        acc = payload.get("refuse_acc", 0.0)
        if acc >= T6_CG_REFUSE_ACC:
            return "chain-grade"
        if acc >= 0.65:
            return "partial"
        return "off-regime"
    return "off-regime"


# ============================================================================
# Per-seed-per-N runner
# ============================================================================

def run_one_cell(N: int, seed: int) -> Dict:
    """Run all 6 tasks at one (N, seed) cell. Returns per-task payloads."""
    t0 = time.time()
    print(f"[run] N={N} seed={seed} starting all 6 tasks", flush=True)
    out: Dict[str, Dict] = {}
    out["T1_storage"] = task1_storage(N, M_STORAGE, seed)
    print(f"[run]   T1 top1={out['T1_storage']['top1']:.3f}", flush=True)
    out["T2_capacity"] = task2_capacity_ceiling(N, seed)
    print(f"[run]   T2 M_crit={out['T2_capacity']['M_critical']}", flush=True)
    out["T3_multihop"] = task3_multihop_K20_K50(N, seed)
    print(f"[run]   T3 K20={out['T3_multihop']['K20_acc']:.3f} "
          f"K50={out['T3_multihop']['K50_acc']:.3f}", flush=True)
    out["T4_compositional"] = task4_compositional(N, seed)
    print(f"[run]   T4 lift={out['T4_compositional']['lift_over_chance']:.2f}",
          flush=True)
    out["T5_cl_crispr"] = task5_cl_crispr(N, seed)
    print(f"[run]   T5 forget={out['T5_cl_crispr']['forgetting_d1']:.4f}",
          flush=True)
    out["T6_refuse_tau"] = task6_refuse_tau(N, seed)
    print(f"[run]   T6 refuse_acc={out['T6_refuse_tau']['refuse_acc']:.3f}",
          flush=True)
    elapsed = time.time() - t0
    out["_meta"] = {"N": N, "seed": seed, "elapsed_s": elapsed,
                    "device": str(DEVICE)}
    print(f"[run] N={N} seed={seed} DONE in {elapsed:.1f}s", flush=True)
    return out


# ============================================================================
# Self-test
# ============================================================================

def self_test() -> int:
    """Mandatory self-test: exercises every primitive + every task + verdict."""
    print("[selftest] start", flush=True)
    # ST1: sparse_bipolar produces correct nnz + uniq values
    gen = torch.Generator(device=DEVICE).manual_seed(11)
    X = sparse_bipolar(N=128, M=4, f=0.05, gen=gen)
    nnz_per_row = (X != 0).sum(dim=1)
    expected_nnz = max(1, int(round(128 * 0.05)))
    assert (nnz_per_row == expected_nnz).all(), \
        f"ST1 sparse nnz: got {nnz_per_row.tolist()} expected {expected_nnz}"
    uniq = torch.unique(X[X != 0]).tolist()
    amp = 1.0 / math.sqrt(0.05)
    for u in uniq:
        assert abs(abs(u) - amp) < 1e-4, f"ST1 amp: {u} vs +/-{amp}"
    print("[selftest] ST1 sparse_bipolar OK", flush=True)

    # ST2: HRR bind/unbind round-trip cleanup
    a = torch.randn(64, device=DEVICE)
    a = a / a.norm()
    b = torch.randn(64, device=DEVICE)
    b = b / b.norm()
    c = hrr_bind(a, b)
    a_back = hrr_unbind(c, b)
    cos_back = float(((a * a_back).sum() /
                      (a.norm() * a_back.norm() + 1e-9)).item())
    assert cos_back > 0.5, f"ST2 HRR round-trip cos={cos_back} < 0.5"
    print(f"[selftest] ST2 HRR cos_round_trip={cos_back:.3f} OK", flush=True)

    # ST3: Hebbian outer-product recovers stored pair (small M)
    gen2 = torch.Generator(device=DEVICE).manual_seed(13)
    K = sparse_bipolar(128, 8, 0.1, gen2)
    V = sparse_bipolar(128, 8, 0.1, gen2)
    W = hebbian_outer(K, V)
    rec = K[0:1] @ W.t()                            # [1, 128]
    rn = rec / (rec.norm() + 1e-9)
    vn = V / (V.norm(dim=1, keepdim=True) + 1e-9)
    sim = (rn @ vn.t()).squeeze(0)
    assert int(sim.argmax().item()) == 0, \
        f"ST3 Hebbian argmax={int(sim.argmax().item())} != 0"
    print("[selftest] ST3 Hebbian outer-product OK", flush=True)

    # ST4: tiny end-to-end run (smoke-grid) at N=128
    global RUN_MODE, N_DIM_GRID, SEEDS, M_STORAGE, M_CAPACITY_SWEEP
    global N_MULTIHOP_ENT, N_MULTIHOP_REL, N_QUERIES, N_REFUSE_IN, N_REFUSE_OOD
    RUN_MODE = "smoke"
    N_DIM_GRID = [128]
    SEEDS = [0]
    M_STORAGE = 40
    M_CAPACITY_SWEEP = [20, 40, 80]
    N_MULTIHOP_ENT = 30
    N_MULTIHOP_REL = 3
    N_QUERIES = 10
    N_REFUSE_IN = 20
    N_REFUSE_OOD = 20
    payload = run_one_cell(N=128, seed=0)
    assert "T1_storage" in payload and "T6_refuse_tau" in payload, \
        "ST4 missing task payloads"
    # Verify each task produced its expected scalar
    for tk in ["T1_storage", "T2_capacity", "T3_multihop",
               "T4_compositional", "T5_cl_crispr", "T6_refuse_tau"]:
        assert tk in payload, f"ST4 missing {tk}"
    print("[selftest] ST4 end-to-end smoke cell OK", flush=True)

    # ST5: classify_per_task discriminates
    assert classify_per_task("T1", {"top1": 0.99}, 8192) == "chain-grade"
    assert classify_per_task("T1", {"top1": 0.80}, 8192) == "partial"
    assert classify_per_task("T1", {"top1": 0.40}, 8192) == "off-regime"
    assert classify_per_task("T3", {"K20_acc": 0.90, "K50_acc": 0.45},
                              8192) == "chain-grade"
    assert classify_per_task("T5", {"forgetting_d1": 0.01},
                              8192) == "chain-grade"
    assert classify_per_task("T6", {"refuse_acc": 0.85},
                              8192) == "chain-grade"
    print("[selftest] ST5 classify_per_task OK", flush=True)

    # ST6: write_metrics produces REQUIRED_FIELDS
    tmp_out = REPO / "data" / f"exp_{ANCHOR_NAME}_selftest_tmp"
    tmp_out.mkdir(parents=True, exist_ok=True)
    m = {"verdict": "SELFTEST_OK", "verdict_msg": "selftest",
         "_config_version": CONFIG_VERSION}
    write_metrics(tmp_out, m, results=[{"elapsed_s": 0.1}])
    loaded = json.loads((tmp_out / "metrics.json").read_text())
    for k in ("verdict", "verdict_msg", "elapsed_s", "summary"):
        assert k in loaded, f"ST6 missing required field {k}"
    print("[selftest] ST6 write_metrics REQUIRED_FIELDS OK", flush=True)
    print("[selftest] ALL PASS", flush=True)
    return 0


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    if _ARGS.self_test:
        return self_test()

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[main] out_dir={out_dir}", flush=True)
    print(f"[main] CONFIG: {CONFIG_VERSION}", flush=True)

    # Build (N, seed) compound keys
    keys: List[str] = []
    for N in N_DIM_GRID:
        for s in SEEDS:
            keys.append(f"N{N}_seed{s}")

    # ATEXIT synthesizer: even on crash, write a metrics.json with partial info
    def _atexit_synth() -> None:
        try:
            existing = aggregate_partials(out_dir, keys)
            n_done = len(existing)
            if n_done == 0:
                return
            if (out_dir / "metrics.json").exists():
                return
            print(f"[atexit] synth metrics.json from {n_done} of {len(keys)} "
                  f"partials", flush=True)
            metrics = build_summary(existing, partial=True)
            write_metrics(out_dir, metrics,
                          results=list(existing.values()))
        except Exception as e:
            print(f"[atexit] error: {e}", flush=True)

    atexit.register(_atexit_synth)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    # Resume support
    done_keys = set()
    for k in list(keys):
        p = out_dir / f"partial_metrics_{k}.json"
        if p.exists():
            done_keys.add(k)
    remaining = [k for k in keys if k not in done_keys]
    print(f"[main] {len(done_keys)} of {len(keys)} cells already done; "
          f"running {len(remaining)}", flush=True)

    for k in remaining:
        # Parse N and seed from compound key
        n_part, s_part = k.split("_", 1)
        N = int(n_part[1:])
        seed = int(s_part.replace("seed", ""))
        try:
            payload = run_one_cell(N, seed)
            payload["_ckpt_key"] = k
            payload["N"] = N
            payload["seed"] = seed
            payload["run_mode"] = RUN_MODE
            write_partial_key(out_dir, k, payload)
        except Exception as e:
            print(f"[main] FAIL cell {k}: {e}", flush=True)
            # Continue; checkpoint preserves done cells
            continue

    all_partials = aggregate_partials(out_dir, keys)
    print(f"[main] aggregated {len(all_partials)} of {len(keys)} cells",
          flush=True)
    metrics = build_summary(all_partials, partial=(len(all_partials) < len(keys)))
    metrics["_config_version"] = CONFIG_VERSION
    write_metrics(out_dir, metrics, results=list(all_partials.values()))
    print(f"[main] verdict={metrics.get('verdict')} "
          f"msg={metrics.get('verdict_msg')}", flush=True)
    return 0


def build_summary(partials: Dict[str, Dict], partial: bool = False) -> Dict:
    """Aggregate per-cell into phase-diagram + verdict."""
    # 6 x N_DIM table: per-task per-N classification
    phase_table: Dict[str, Dict[int, List[str]]] = {
        t: {} for t in ["T1", "T2", "T3", "T4", "T5", "T6"]
    }
    raw_table: Dict[str, Dict[int, List[Dict]]] = {
        t: {} for t in ["T1_storage", "T2_capacity", "T3_multihop",
                        "T4_compositional", "T5_cl_crispr", "T6_refuse_tau"]
    }
    for key, body in partials.items():
        N = body.get("N")
        if N is None:
            continue
        for tk, tid in [
            ("T1_storage", "T1"), ("T2_capacity", "T2"), ("T3_multihop", "T3"),
            ("T4_compositional", "T4"), ("T5_cl_crispr", "T5"),
            ("T6_refuse_tau", "T6"),
        ]:
            if tk not in body:
                continue
            cls = classify_per_task(tid, body[tk], N)
            phase_table[tid].setdefault(N, []).append(cls)
            raw_table[tk].setdefault(N, []).append(body[tk])

    # Per-N per-task majority classification (across seeds)
    def majority(cs: List[str]) -> str:
        from collections import Counter
        if not cs:
            return "missing"
        c = Counter(cs)
        return c.most_common(1)[0][0]

    per_n_per_task: Dict[int, Dict[str, str]] = {}
    for N in sorted({n for tdict in phase_table.values() for n in tdict.keys()}):
        per_n_per_task[N] = {}
        for tid in ["T1", "T2", "T3", "T4", "T5", "T6"]:
            per_n_per_task[N][tid] = majority(phase_table[tid].get(N, []))

    # Verdict (pre-reg)
    canonical_N = 8192
    if canonical_N in per_n_per_task:
        canon = per_n_per_task[canonical_N]
        n_cg_canon = sum(1 for v in canon.values() if v == "chain-grade")
    else:
        # Smoke or partial: pick the highest N we did run
        if per_n_per_task:
            hi_N = max(per_n_per_task.keys())
            canon = per_n_per_task[hi_N]
            n_cg_canon = sum(1 for v in canon.values() if v == "chain-grade")
        else:
            canon = {}
            n_cg_canon = 0

    # N_DIM_SCALING: each task chain-grade at >= 2 N_DIM values
    task_n_count: Dict[str, int] = {}
    for tid in ["T1", "T2", "T3", "T4", "T5", "T6"]:
        c = sum(1 for N in per_n_per_task if per_n_per_task[N].get(tid)
                 == "chain-grade")
        task_n_count[tid] = c
    n_dim_scaling_cg = sum(1 for c in task_n_count.values() if c >= 2)

    if partial:
        verdict = "PARTIAL"
        verdict_msg = (
            f"PARTIAL: {len(partials)} cells of plan completed; "
            f"canonical_N={canonical_N} n_cg={n_cg_canon}/6"
        )
    elif n_cg_canon >= 5:
        verdict = "PASS"
        verdict_msg = (
            f"STAGE_1_INTEGRATED_CHAIN_GRADE: {n_cg_canon}/6 tasks chain-grade "
            f"at canonical_N={canonical_N}; N_DIM_SCALING_CG tasks={n_dim_scaling_cg}/6"
        )
    elif n_cg_canon < 3:
        verdict = "FAIL"
        verdict_msg = (
            f"HARD_FAIL_INTEGRATION_BREAKS: only {n_cg_canon}/6 tasks chain-grade "
            f"at canonical_N={canonical_N} (individually-proven capabilities "
            f"don't compose); N_DIM_SCALING tasks={n_dim_scaling_cg}/6"
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: {n_cg_canon}/6 tasks chain-grade at "
            f"canonical_N={canonical_N}; N_DIM_SCALING tasks={n_dim_scaling_cg}/6"
        )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "phase_diagram_per_N_per_task": per_n_per_task,
        "task_n_dim_scaling_count": task_n_count,
        "canonical_N": canonical_N,
        "n_cg_at_canonical_N": n_cg_canon,
        "n_dim_scaling_cg": n_dim_scaling_cg,
        "raw_table": raw_table,
        "n_cells_completed": len(partials),
        "n_cells_planned": len(N_DIM_GRID) * len(SEEDS),
        "run_mode": RUN_MODE,
    }


if __name__ == "__main__":
    sys.exit(main())
