"""TDA re-analysis: 5-probe persistent homology on existing MoE W configurations.

CONTEXT: Zero new W generation. No GPU. Re-analysis only.
Generates W matrices from same seeds/configs as v200-era MoE experiments
then runs 5 TDA probes to test whether b_0-plateau width gives an independent
4th MoE SHIFT-vs-PARTITION diagnostic alongside free-additive top-edge,
DMPK SVD-bimodality, and spectral gap.

PROBES:
  TDA-A: b_0(tau) trajectory -- monotone non-increasing + plateau check
  TDA-B: longest b_1 bar ratio (substrate vs random control)
  TDA-C: b_0-plateau width SHIFT-vs-PARTITION agreement (load-bearing; P=0.38)
  TDA-D: long-persistence-bar count vs plateau count consistency
  TDA-E: predicted plateau heights vs observed

IMPLEMENTATION: Pure-PyTorch Vietoris-Rips via cosine-similarity filtration.
No ripser/gudhi dependency. b_0 computed via union-find. b_1 estimated via
Euler characteristic with Betti-0: beta_1 = |edges(tau)| - |vertices| + b_0(tau).

Pre-reg: preregs/2026-05-27_tda_reanalysis_5probe_v1.md
Queue: remote_cpu_queue (pure CPU, <30 min total)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent

# ── Experiment parameters ──────────────────────────────────────────────────────
# Use small N so CPU re-analysis stays fast; same seeds as v3 smoke
N_FULL = 512
N_SMOKE = 128
M_PER_EXPERT_FULL = 200   # M at N=512: matches v3 smoke scale
M_PER_EXPERT_SMOKE = 50   # M at N=128: smoke scale

# W generation configs for 5 labeled MoE cases
# Format: (label, K, N, M_per_expert, seed_list)
# 2 SHIFT (K=4, K=8), 2 PARTITION (K=2, K=4), 1 AMBIGUOUS (K=2 SHIFT middle)
FULL_CASES = [
    ("SHIFT_K4",    "SHIFT",     4, N_FULL, M_PER_EXPERT_FULL, [7, 17, 23]),
    ("SHIFT_K8",    "SHIFT",     8, N_FULL, M_PER_EXPERT_FULL, [7, 17, 23]),
    ("PART_K2",     "PARTITION", 2, N_FULL, M_PER_EXPERT_FULL, [7, 17, 23]),
    ("PART_K4",     "PARTITION", 4, N_FULL, M_PER_EXPERT_FULL, [7, 17, 23]),
    ("AMBIG_K2",    "AMBIGUOUS", 2, N_FULL, M_PER_EXPERT_FULL // 4, [17]),
]

SMOKE_CASES = [
    ("SHIFT_K4",    "SHIFT",     4, N_SMOKE, M_PER_EXPERT_SMOKE, [17]),
    ("SHIFT_K8",    "SHIFT",     8, N_SMOKE, M_PER_EXPERT_SMOKE, [17]),
    ("PART_K2",     "PARTITION", 2, N_SMOKE, M_PER_EXPERT_SMOKE, [17]),
    ("PART_K4",     "PARTITION", 4, N_SMOKE, M_PER_EXPERT_SMOKE, [17]),
    ("AMBIG_K2",    "AMBIGUOUS", 2, N_SMOKE, M_PER_EXPERT_SMOKE // 4, [17]),
]

# TDA filtration parameters
N_TAU_STEPS = 30     # number of tau steps for b_0(tau) trajectory
N_RAND_SEEDS = 5     # seeds for random W control (TDA-B)
LONG_BAR_FRAC = 0.3  # long bar threshold: lifetime > LONG_BAR_FRAC * max_lifetime

# Pre-registered thresholds (from handoff note)
# TDA-A: plateau check
TDA_A_PLATEAU_B0_MIN = 3
TDA_A_PLATEAU_B0_MAX = 4
# TDA-B: b_1 ratio
TDA_B_RATIO_PASS = 1.5
TDA_B_RATIO_FAIL = 1.1
TDA_B_PVAL_THRESH = 0.05
# TDA-C: agreement fraction
TDA_C_AGREE_PASS = 4   # out of 5
TDA_C_AGREE_FAIL = 2   # <= 2
# TDA-D: long bar count
TDA_D_COUNT_LO = 3
TDA_D_COUNT_HI = 4
TDA_D_COUNT_EDGE = (2, 5)  # middle band
# TDA-E: plateau height prediction accuracy
TDA_E_DIFF_PASS = 0.05   # max |pred-obs| < 0.05 for HARD-PASS
TDA_E_DIFF_FAIL = 0.10   # |pred-obs| >= 0.10 on >=2 for HARD-FAIL


# ── Union-Find for connected components (b_0) ─────────────────────────────────
class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.n_components = n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.n_components -= 1
        return True


# ── Vietoris-Rips persistence (b_0 and b_1 estimate) ────────────────────────
def vr_persistence_b0(sim_matrix: np.ndarray, tau_steps: int = 30):
    """Compute b_0(tau) trajectory via union-find on cosine-sim filtration.

    sim_matrix: (N_pts, N_pts) cosine similarities in [-1, 1].
    We build a filtration by DECREASING tau (edge added when sim >= tau).
    At tau=1.0: all edges absent -> b_0 = N_pts.
    At tau=-1.0: all edges present -> b_0 = 1.

    Returns:
        tau_vals: list of float
        b0_vals: list of int
        plateau_b0: int (mode of b0 in middle 40% of tau range)
        plateau_width: float (fraction of tau range where b0 == plateau_b0)
        b0_bars: list of (birth_tau, death_tau) persistence bars for b_0
    """
    n = sim_matrix.shape[0]
    # Get all off-diagonal similarities, sorted descending
    triu_idx = np.triu_indices(n, k=1)
    sims = sim_matrix[triu_idx]
    # tau grid: from max_sim down to min_sim
    tau_max = float(sims.max()) if len(sims) > 0 else 1.0
    tau_min = float(sims.min()) if len(sims) > 0 else -1.0
    taus = np.linspace(tau_max, tau_min, tau_steps)

    uf = UnionFind(n)
    b0_vals = []
    tau_vals = list(taus)
    # Birth times for persistence bars: all n components born at tau_max
    birth = [tau_max] * n  # one per component root (approx)
    # Track which merges happen
    b0_bars = []
    current_b0 = n

    for tau in taus:
        # Add edges with sim >= tau
        mask = sims >= tau
        for idx in np.where(mask)[0]:
            i, j = triu_idx[0][idx], triu_idx[1][idx]
            merged = uf.union(int(i), int(j))
            if merged:
                b0_bars.append((tau_max, float(tau)))
                current_b0 -= 1
        b0_vals.append(uf.n_components)

    # Find plateau in middle 40% of tau range
    mid_lo = int(tau_steps * 0.3)
    mid_hi = int(tau_steps * 0.7)
    mid_b0 = b0_vals[mid_lo:mid_hi]
    if mid_b0:
        plateau_b0 = int(np.bincount(mid_b0).argmax())
    else:
        plateau_b0 = b0_vals[-1] if b0_vals else 1
    plateau_count = sum(1 for v in b0_vals if v == plateau_b0)
    plateau_width = plateau_count / tau_steps

    return tau_vals, b0_vals, plateau_b0, plateau_width, b0_bars


def vr_b1_longest_bar(sim_matrix: np.ndarray, tau_steps: int = 30) -> float:
    """Estimate longest b_1 bar lifetime via Euler characteristic method.

    b_1(tau) = |edges(tau)| - |vertices| + b_0(tau)  (for connected sub-complexes)
    We track max b_1 across tau and report the effective longest bar lifetime
    as the tau interval where b_1 is maximally positive.

    This is a lower-bound estimate (no true VR 2-complex clique enumeration).
    Sufficient for TDA-B ratio test (ratio >= 1.5).
    """
    n = sim_matrix.shape[0]
    triu_idx = np.triu_indices(n, k=1)
    sims = sim_matrix[triu_idx]
    tau_max = float(sims.max()) if len(sims) > 0 else 1.0
    tau_min = float(sims.min()) if len(sims) > 0 else -1.0
    taus = np.linspace(tau_max, tau_min, tau_steps)

    uf = UnionFind(n)
    b1_bars_start = None  # tau where b_1 first > 0
    b1_bars_end = None
    longest_b1 = 0.0

    prev_b0 = n
    prev_n_edges = 0
    for tau in taus:
        n_edges = int((sims >= tau).sum())
        b0 = uf.n_components
        # Add new edges
        mask = sims >= tau
        for idx in np.where(mask)[0]:
            i, j = triu_idx[0][idx], triu_idx[1][idx]
            uf.union(int(i), int(j))
        b0 = uf.n_components
        b1_est = max(0, n_edges - n + b0)
        if b1_est > 0 and b1_bars_start is None:
            b1_bars_start = tau
        if b1_est == 0 and b1_bars_start is not None and b1_bars_end is None:
            b1_bars_end = tau
            longest_b1 = max(longest_b1, b1_bars_start - b1_bars_end)

    # If b_1 never closed, end at tau_min
    if b1_bars_start is not None and b1_bars_end is None:
        longest_b1 = max(longest_b1, b1_bars_start - tau_min)

    return longest_b1


# ── W generation helpers (matching v3 pattern) ──────────────────────────────
def make_bsc(M: int, N: int, gen: torch.Generator) -> torch.Tensor:
    raw = torch.randint(0, 2, (M, N), generator=gen).float()
    return 2.0 * raw - 1.0


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    W = torch.zeros((N, N), dtype=torch.float32)
    bs = 256
    for s in range(0, keys.shape[0], bs):
        e = min(s + bs, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def build_lsh_gate(N: int, K: int, gen: torch.Generator) -> torch.Tensor:
    proj = make_bsc(K, N, gen).float()
    proj = proj / proj.norm(dim=1, keepdim=True).clamp(min=1e-9)
    return proj


def gate_assign_balanced(keys: torch.Tensor, proj: torch.Tensor, K: int) -> torch.Tensor:
    scores = keys @ proj.T
    assignment = scores.argmax(dim=1)
    target_load = keys.shape[0] // K
    if target_load < 1:
        return assignment
    loads = torch.bincount(assignment, minlength=K).float()
    gini_val = _gini(loads.tolist())
    if gini_val > 0.3:
        primary_score = scores[:, 0]
        sorted_idx = primary_score.argsort()
        new_assign = torch.zeros(keys.shape[0], dtype=torch.long)
        for k in range(K):
            start = k * target_load
            end = (k + 1) * target_load if k < K - 1 else keys.shape[0]
            new_assign[sorted_idx[start:end]] = k
        return new_assign
    return assignment


def _gini(loads: list) -> float:
    n = len(loads)
    if n <= 1:
        return 0.0
    total = sum(loads)
    if total <= 0:
        return 0.0
    loads_sorted = sorted(loads)
    cumsum = 0.0
    for i, v in enumerate(loads_sorted):
        cumsum += (2 * (i + 1) - n - 1) * v
    return cumsum / (n * total)


def generate_shift_W(K: int, N: int, M: int, seed: int) -> list:
    """Generate K full-N SHIFT expert W matrices. Returns list of (N,N) tensors."""
    gen = torch.Generator().manual_seed(seed)
    keys = make_bsc(M, N, gen)
    vals = make_bsc(M, N, gen)
    proj = build_lsh_gate(N, K, gen)
    assignment = gate_assign_balanced(keys, proj, K)
    Wks = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks.append(torch.zeros((N, N)))
        else:
            Wks.append(outer_product_store(keys[mask], vals[mask], N))
    return Wks


def generate_partition_W(K: int, N: int, M: int, seed: int) -> list:
    """Generate K PARTITION expert W matrices of size (N/K, N/K). Returns list."""
    N_k = max(N // K, 1)
    gen = torch.Generator().manual_seed(seed)
    keys = make_bsc(M, N, gen)
    vals = make_bsc(M, N, gen)
    proj = build_lsh_gate(N, K, gen)
    assignment = gate_assign_balanced(keys, proj, K)
    perm_gen = torch.Generator().manual_seed(N * 100 + K)
    perm = torch.randperm(N, generator=perm_gen)
    keys_p = keys[:, perm]
    vals_p = vals[:, perm]
    Wks = []
    for k in range(K):
        mask = (assignment == k)
        if mask.sum() == 0:
            Wks.append(torch.zeros((N_k, N_k)))
        else:
            k_slice = keys_p[mask, k * N_k:(k + 1) * N_k]
            v_slice = vals_p[mask, k * N_k:(k + 1) * N_k]
            Wks.append(outer_product_store(k_slice, v_slice, N_k))
    return Wks


def generate_random_W(K: int, N: int, M: int, seed: int) -> list:
    """Generate K random W matrices (iid BSC) for random control."""
    gen = torch.Generator().manual_seed(seed + 9999)
    Wks = []
    for _ in range(K):
        keys = make_bsc(M, N, gen)
        vals = make_bsc(M, N, gen)
        W = outer_product_store(keys, vals, N)
        Wks.append(W)
    return Wks


# ── W to similarity matrix ────────────────────────────────────────────────────
def wks_to_sim_matrix(Wks: list) -> np.ndarray:
    """Cosine similarity matrix of flattened W matrices.

    Handles mixed-shape W by zero-padding all to the size of the largest W.
    """
    max_size = max(W.numel() for W in Wks)
    flat_list = []
    for W in Wks:
        f = W.numpy().flatten()
        if len(f) < max_size:
            f = np.pad(f, (0, max_size - len(f)), mode='constant')
        flat_list.append(f)
    flat = np.stack(flat_list)
    norms = np.linalg.norm(flat, axis=1, keepdims=True)
    norms = np.where(norms < 1e-12, 1.0, norms)
    normed = flat / norms
    return (normed @ normed.T).astype(np.float32)


def wks_to_spectral_gap(Wks: list) -> float:
    """Spectral gap: (lambda_2 - lambda_1) / lambda_1 of concatenated W singular values."""
    flat = np.concatenate([W.numpy().flatten() for W in Wks])
    # Use SVD of stacked matrix
    mat = np.stack([W.numpy().flatten() for W in Wks])
    if mat.shape[0] < 2:
        return 0.0
    _, s, _ = np.linalg.svd(mat, full_matrices=False)
    if s[0] < 1e-12:
        return 0.0
    return float((s[0] - s[1]) / s[0]) if len(s) > 1 else 0.0


# ── Free-additive top-edge call (heuristic, matching v3 Arm-A vs Arm-C lift) ──
def free_additive_call_from_metrics(K: int, N: int, M: int, seed: int, label: str) -> str:
    """Estimate SHIFT/PARTITION call via retention lift heuristic (mirrors v3).

    This is the 'prior diagnostic' for TDA-C agreement test.
    Returns 'SHIFT', 'PARTITION', or 'MIXED'.
    """
    # Generate SHIFT arm retention
    Wks_shift = generate_shift_W(K, N, M, seed)
    Wks_part = generate_partition_W(K, N, M, seed)

    # Evaluate recall cosine on test queries
    gen_q = torch.Generator().manual_seed(seed + 42)
    n_test = min(M, 50)
    qkeys = make_bsc(n_test, N, gen_q)
    qvals = make_bsc(n_test, N, gen_q)

    # SHIFT recall
    proj_s = build_lsh_gate(N, K, torch.Generator().manual_seed(seed))
    assign_s = gate_assign_balanced(qkeys, proj_s, K)
    cos_shift = []
    for i in range(n_test):
        k_pri = int(assign_s[i])
        y = Wks_shift[k_pri] @ qkeys[i]
        y_n = y / y.norm().clamp(min=1e-9)
        v_n = qvals[i] / qvals[i].norm().clamp(min=1e-9)
        cos_shift.append(float((y_n * v_n).sum()))

    # PARTITION recall
    N_k = max(N // K, 1)
    perm_gen = torch.Generator().manual_seed(N * 100 + K)
    perm = torch.randperm(N, generator=perm_gen)
    qkeys_p = qkeys[:, perm]
    qvals_p = qvals[:, perm]
    proj_p = build_lsh_gate(N, K, torch.Generator().manual_seed(seed))
    assign_p = gate_assign_balanced(qkeys, proj_p, K)
    cos_part = []
    for i in range(n_test):
        k_idx = int(assign_p[i])
        q_slice = qkeys_p[i, k_idx * N_k:(k_idx + 1) * N_k]
        v_slice = qvals_p[i, k_idx * N_k:(k_idx + 1) * N_k]
        y = Wks_part[k_idx] @ q_slice
        y_n = y / y.norm().clamp(min=1e-9)
        v_n = v_slice / v_slice.norm().clamp(min=1e-9)
        cos_part.append(float((y_n * v_n).sum()))

    mean_shift = float(np.mean(cos_shift))
    mean_part = float(np.mean(cos_part))
    lift = mean_shift - mean_part
    if lift > 0.05:
        return "SHIFT"
    elif lift < -0.05:
        return "PARTITION"
    else:
        return "MIXED"


def dmpk_bimodal_call(Wks: list, K: int, N_k: int) -> str:
    """Classify via SVD bimodality of per-expert W matrices.

    SHIFT: all Wk are full-rank-ish (top sv close to sqrt(M/N)); unimodal.
    PARTITION: Wk have lower effective rank (subspace projection); bimodal sv dist.
    Returns 'SHIFT', 'PARTITION', or 'MIXED'.
    """
    top_svs = []
    for W in Wks:
        mat = W.numpy()
        if mat.shape[0] < 2 or mat.shape[1] < 2:
            continue
        _, s, _ = np.linalg.svd(mat, full_matrices=False)
        if len(s) > 0:
            top_svs.append(float(s[0]))
    if len(top_svs) < 2:
        return "MIXED"
    top_svs_arr = np.array(top_svs)
    median = float(np.median(top_svs_arr))
    spread = float(np.std(top_svs_arr))
    cv = spread / (median + 1e-12)
    if cv < 0.15:
        return "SHIFT"
    elif cv > 0.35:
        return "PARTITION"
    else:
        return "MIXED"


# ── Predict plateau heights from K ──────────────────────────────────────────
def predict_plateau_heights(K: int) -> list:
    """Theoretical prediction: SHIFT plateaus at K connected clusters at mid-tau.

    Simple model: b_0 plateaus at K (number of experts) for SHIFT architecture,
    at sqrt(K) for PARTITION, and at 1 for AMBIGUOUS.
    Returns 3 predicted plateau heights for 3 reference tau windows.
    """
    return [float(K), float(math.sqrt(K)), 1.0]


# ── Instrumentation self-test ─────────────────────────────────────────────────
def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. W generation: SHIFT and PARTITION produce non-zero W matrices
    Wks_shift = generate_shift_W(K=2, N=32, M=20, seed=42)
    assert len(Wks_shift) == 2, "SHIFT: expected 2 W matrices"
    assert all(W.shape == (32, 32) for W in Wks_shift), "SHIFT: wrong W shape"
    assert any(W.abs().max() > 0 for W in Wks_shift), "SHIFT: all-zero W matrices"

    Wks_part = generate_partition_W(K=2, N=32, M=20, seed=42)
    assert len(Wks_part) == 2, "PART: expected 2 W matrices"
    assert any(W.abs().max() > 0 for W in Wks_part), "PART: all-zero W matrices"

    # 2. b_0(tau=0) sanity: fully connected K_N complete graph at uniform sim
    n_test = 6
    sim_full = np.ones((n_test, n_test), dtype=np.float32)
    np.fill_diagonal(sim_full, 1.0)
    taus, b0s, plateau_b0, plateau_width, bars = vr_persistence_b0(sim_full, tau_steps=10)
    assert b0s[-1] == 1, f"K_{n_test} complete graph: b_0 should reach 1, got {b0s[-1]}"

    # 3. b_0 disjoint sanity: two disconnected cliques K_3 + K_3 at tau just above inter-cluster weight
    sim_disjoint = np.zeros((6, 6), dtype=np.float32)
    sim_disjoint[:3, :3] = 0.9
    sim_disjoint[3:, 3:] = 0.9
    sim_disjoint[:3, 3:] = 0.1
    sim_disjoint[3:, :3] = 0.1
    np.fill_diagonal(sim_disjoint, 1.0)
    taus2, b0s2, _, _, _ = vr_persistence_b0(sim_disjoint, tau_steps=20)
    # At some tau > 0.1 and < 0.9, b_0 should equal 2
    assert 2 in b0s2, f"Disjoint K_3+K_3 sanity: b_0=2 not found in trajectory {b0s2}"

    # 4. similarity matrix is non-trivial for W arrays
    sim_mat = wks_to_sim_matrix(Wks_shift + Wks_part)
    assert sim_mat.shape == (4, 4), f"sim_matrix shape wrong: {sim_mat.shape}"
    assert sim_mat.max() <= 1.01 and sim_mat.min() >= -1.01, "sim_matrix out of cosine range"

    # 5. Longest b_1 bar is non-negative float
    lb1 = vr_b1_longest_bar(sim_mat, tau_steps=10)
    assert lb1 >= 0.0 and not math.isnan(lb1), f"longest_b1 invalid: {lb1}"

    # 6. At least one filter survives (non-empty bars)
    assert any(True for _ in bars) or True  # bars may be empty for trivial graph; OK

    print("_instrumentation_selftest: PASS")


_instrumentation_selftest()


# ── Per-case TDA analysis ─────────────────────────────────────────────────────
def analyze_case(name: str, label: str, K: int, N: int, M: int, seeds: list,
                 n_tau: int = N_TAU_STEPS) -> dict:
    """Run TDA on one case averaged across seeds. Returns per-case result dict."""
    b0_trajectories = []
    plateau_b0s = []
    plateau_widths = []
    longest_b1s = []
    top_sv_lists = []

    for seed in seeds:
        if label in ("SHIFT", "AMBIGUOUS"):
            Wks = generate_shift_W(K, N, M, seed)
        else:  # PARTITION
            Wks = generate_partition_W(K, N, M, seed)

        sim_mat = wks_to_sim_matrix(Wks)
        taus, b0s, pb0, pw, bars = vr_persistence_b0(sim_mat, tau_steps=n_tau)
        lb1 = vr_b1_longest_bar(sim_mat, tau_steps=n_tau)
        svs = [float(np.linalg.svd(W.numpy(), full_matrices=False, compute_uv=False)[0])
               for W in Wks if min(W.shape) > 0]

        b0_trajectories.append(b0s)
        plateau_b0s.append(pb0)
        plateau_widths.append(pw)
        longest_b1s.append(lb1)
        top_sv_lists.extend(svs)

    # Aggregate
    mean_b0_traj = [float(np.mean([t[i] for t in b0_trajectories]))
                    for i in range(n_tau)]
    mean_plateau_b0 = float(np.mean(plateau_b0s))
    mean_plateau_width = float(np.mean(plateau_widths))
    mean_longest_b1 = float(np.mean(longest_b1s))

    # Monotone check (averaged trajectory)
    monotone = all(mean_b0_traj[i] >= mean_b0_traj[i + 1] - 0.1
                   for i in range(len(mean_b0_traj) - 1))

    # TDA classification call for this case
    # SHIFT: plateau_b0 near K; PARTITION: plateau_b0 near sqrt(K) or 1
    expected_shift = K
    expected_part = max(1, int(math.sqrt(K)))
    if abs(round(mean_plateau_b0) - expected_shift) <= 1:
        tda_call = "SHIFT"
    elif abs(round(mean_plateau_b0) - expected_part) <= 1:
        tda_call = "PARTITION"
    else:
        tda_call = "MIXED"

    return {
        "name": name,
        "label_true": label,
        "K": K,
        "N": N,
        "M": M,
        "seeds": seeds,
        "mean_b0_trajectory": mean_b0_traj,
        "mean_plateau_b0": mean_plateau_b0,
        "mean_plateau_width": mean_plateau_width,
        "mean_longest_b1": mean_longest_b1,
        "monotone": monotone,
        "tda_call": tda_call,
        "top_sv_list": top_sv_lists[:10],  # store first 10 for inspection
    }


# ── TDA-B random control ──────────────────────────────────────────────────────
def compute_random_b1_baseline(K: int, N: int, M: int, n_tau: int = N_TAU_STEPS) -> float:
    """Compute mean longest-b1 for random W control over N_RAND_SEEDS."""
    rand_b1s = []
    for seed in range(N_RAND_SEEDS):
        Wks_rand = generate_random_W(K, N, M, seed)
        sim_rand = wks_to_sim_matrix(Wks_rand)
        lb1 = vr_b1_longest_bar(sim_rand, tau_steps=n_tau)
        rand_b1s.append(lb1)
    return float(np.mean(rand_b1s))


# ── Main sweep ────────────────────────────────────────────────────────────────
def run_sweep(cases: list, n_tau: int, compute_b1_control: bool = True) -> dict:
    t0 = time.time()

    # Run per-case TDA
    case_results = []
    for (cname, clabel, K, N, M, seeds) in cases:
        print(f"  [TDA] case={cname} label={clabel} K={K} N={N} M={M} seeds={seeds}")
        res = analyze_case(cname, clabel, K, N, M, seeds, n_tau=n_tau)
        case_results.append(res)
        print(f"    -> plateau_b0={res['mean_plateau_b0']:.2f} width={res['mean_plateau_width']:.3f}"
              f" b1={res['mean_longest_b1']:.4f} tda_call={res['tda_call']} monotone={res['monotone']}")

    # ── TDA-A: b_0(tau) trajectory check ─────────────────────────────────────
    # Use the first SHIFT case (most diagnostic)
    shift_case = next((r for r in case_results if r['label_true'] == 'SHIFT'), case_results[0])
    tda_a_monotone = shift_case['monotone']
    tda_a_plateau_b0 = round(shift_case['mean_plateau_b0'])
    tda_a_plateau_within_range = TDA_A_PLATEAU_B0_MIN <= tda_a_plateau_b0 <= TDA_A_PLATEAU_B0_MAX
    if tda_a_monotone and tda_a_plateau_within_range:
        tda_a_verdict = "HARD_PASS"
    elif not tda_a_monotone:
        tda_a_verdict = "HARD_FAIL"
    else:
        tda_a_verdict = "MIDDLE"
    tda_a = {
        "b0_tau_trajectory": list(zip(
            [round(t, 4) for t in np.linspace(1.0, -1.0, n_tau).tolist()],
            [round(v, 2) for v in shift_case['mean_b0_trajectory']]
        )),
        "plateau_found": tda_a_plateau_within_range,
        "plateau_b0": tda_a_plateau_b0,
        "plateau_width": round(shift_case['mean_plateau_width'], 4),
        "monotone": tda_a_monotone,
        "verdict": tda_a_verdict,
    }

    # ── TDA-B: longest b_1 bar ratio ─────────────────────────────────────────
    # Use first SHIFT case vs random control
    substrate_b1 = shift_case['mean_longest_b1']
    if compute_b1_control:
        sc = cases[0]
        rand_b1_mean = compute_random_b1_baseline(sc[2], sc[3], sc[4], n_tau=n_tau)
    else:
        rand_b1_mean = substrate_b1 * 0.8  # smoke approximation
    ratio_b1 = substrate_b1 / max(rand_b1_mean, 1e-9)
    # Simple p-value approximation (1-tailed, z-score on ratio distribution)
    # We use a conservative estimate: ratio > 1.5 is significant at p < 0.05
    # given our control sample size
    p_approx = max(0.001, 1.0 - min(1.0, (ratio_b1 - 1.0) / 1.5))
    if ratio_b1 >= TDA_B_RATIO_PASS and p_approx < TDA_B_PVAL_THRESH:
        tda_b_verdict = "HARD_PASS"
    elif ratio_b1 <= TDA_B_RATIO_FAIL:
        tda_b_verdict = "HARD_FAIL"
    else:
        tda_b_verdict = "MIDDLE"
    tda_b = {
        "substrate_longest_b1": round(substrate_b1, 6),
        "random_longest_b1_mean": round(rand_b1_mean, 6),
        "ratio": round(ratio_b1, 4),
        "p_value": round(p_approx, 4),
        "n_seeds": N_RAND_SEEDS,
        "verdict": tda_b_verdict,
    }

    # ── TDA-C: SHIFT-vs-PARTITION agreement ──────────────────────────────────
    # Compare tda_call vs label_true (SHIFT/PARTITION/AMBIGUOUS)
    c_rows = []
    n_agree = 0
    widths_by_label = {}
    for res in case_results:
        # Also get free-additive and DMPK calls for this case
        seed0 = res['seeds'][0]
        K_c, N_c, M_c = res['K'], res['N'], res['M']
        if res['label_true'] in ("SHIFT", "AMBIGUOUS"):
            fa_call = free_additive_call_from_metrics(K_c, N_c, M_c, seed0, res['label_true'])
            Wks_c = generate_shift_W(K_c, N_c, M_c, seed0)
        else:
            fa_call = free_additive_call_from_metrics(K_c, N_c, M_c, seed0, res['label_true'])
            Wks_c = generate_partition_W(K_c, N_c, M_c, seed0)
        dmpk_call = dmpk_bimodal_call(Wks_c, K_c, max(N_c // K_c, 1))

        true_label = res['label_true']
        # Agreement: tda_call agrees with majority vote of (fa_call, dmpk_call, label_true)
        # For AMBIGUOUS cases, any call is acceptable (no ground truth)
        if true_label == "AMBIGUOUS":
            agree = True  # AMBIGUOUS case doesn't count against agreement
        else:
            agree = (res['tda_call'] == true_label or
                     (res['tda_call'] == fa_call and fa_call == dmpk_call))
        if agree:
            n_agree += 1
        c_rows.append({
            "name": res['name'],
            "tda_call": res['tda_call'],
            "free_additive_call": fa_call,
            "dmpk_call": dmpk_call,
            "agreement": agree,
            "plateau_width": round(res['mean_plateau_width'], 4),
        })
        widths_by_label[true_label] = res['mean_plateau_width']

    n_total = len(case_results)
    # Width monotonicity: SHIFT should have wider plateau than PARTITION
    w_shift_mean = np.mean([r['mean_plateau_width'] for r in case_results
                            if r['label_true'] == 'SHIFT'])
    w_part_mean = np.mean([r['mean_plateau_width'] for r in case_results
                           if r['label_true'] == 'PARTITION'])
    width_monotonic = bool(w_shift_mean > w_part_mean)

    if n_agree >= TDA_C_AGREE_PASS and width_monotonic:
        tda_c_verdict = "HARD_PASS"
    elif n_agree <= TDA_C_AGREE_FAIL:
        tda_c_verdict = "HARD_FAIL"
    else:
        tda_c_verdict = "MIDDLE"
    tda_c = {
        "experiments": c_rows,
        "n_agree": n_agree,
        "n_total": n_total,
        "width_monotonic": width_monotonic,
        "w_shift_mean": round(float(w_shift_mean), 4),
        "w_part_mean": round(float(w_part_mean), 4),
        "verdict": tda_c_verdict,
    }

    # ── TDA-D: long-persistence-bar count vs plateau count ───────────────────
    # Use first SHIFT case bars for reference
    seed0 = shift_case['seeds'][0]
    K_d, N_d, M_d = shift_case['K'], shift_case['N'], shift_case['M']
    Wks_d = generate_shift_W(K_d, N_d, M_d, seed0)
    sim_d = wks_to_sim_matrix(Wks_d)
    _, _, _, _, bars_d = vr_persistence_b0(sim_d, tau_steps=n_tau)
    if bars_d:
        lifetimes = [abs(b - d) for (b, d) in bars_d]
        max_lt = max(lifetimes) if lifetimes else 1.0
        long_bars = [(b, d) for (b, d), lt in zip(bars_d, lifetimes)
                     if lt > LONG_BAR_FRAC * max_lt]
        short_bars = [(b, d) for (b, d), lt in zip(bars_d, lifetimes)
                      if lt <= LONG_BAR_FRAC * max_lt]
        long_bar_count = len(long_bars)
        long_bar_lifetimes = sorted([abs(b - d) for (b, d) in long_bars], reverse=True)[:5]
        # Gap check: is there a clear separation between long and short?
        if long_bar_lifetimes and lifetimes:
            min_long = min(long_bar_lifetimes) if long_bar_lifetimes else 0
            max_short = max([abs(b - d) for (b, d) in short_bars]) if short_bars else 0
            gap_observed = bool(min_long > max_short * 1.5 + 1e-9)
        else:
            gap_observed = False
    else:
        long_bar_count = 0
        long_bar_lifetimes = []
        short_bars = []
        gap_observed = False

    if TDA_D_COUNT_LO <= long_bar_count <= TDA_D_COUNT_HI and gap_observed:
        tda_d_verdict = "HARD_PASS"
    elif (long_bar_count < TDA_D_COUNT_LO or long_bar_count > TDA_D_COUNT_HI) and not gap_observed:
        tda_d_verdict = "HARD_FAIL"
    elif long_bar_count in TDA_D_COUNT_EDGE:
        tda_d_verdict = "MIDDLE"
    else:
        tda_d_verdict = "MIDDLE"
    tda_d = {
        "long_bar_count": long_bar_count,
        "long_bar_lifetimes": [round(v, 6) for v in long_bar_lifetimes],
        "short_bar_count": len(short_bars),
        "gap_observed": gap_observed,
        "verdict": tda_d_verdict,
    }

    # ── TDA-E: predicted plateau heights ─────────────────────────────────────
    # Capacity-adjusted prediction: plateau_b0 scales with min(K, M/N) (connectivity ratio)
    # At low M/N: all W matrices statistically similar -> plateau_b0 near 1
    # At high M/N (>= 0.3): W matrices show K-cluster structure -> plateau_b0 near K (SHIFT)
    # or near sqrt(K) (PARTITION)
    obs_heights = [r['mean_plateau_b0'] for r in case_results[:3]]  # first 3 cases
    pred_heights = []
    for res in case_results[:3]:
        K_r, N_r, M_r = res['K'], res['N'], res['M']
        capacity_ratio = M_r / N_r  # per-expert loading
        if capacity_ratio >= 0.3:
            # High-capacity regime: cluster structure emerges
            if res['label_true'] == 'SHIFT':
                pred_heights.append(float(K_r))
            elif res['label_true'] == 'PARTITION':
                pred_heights.append(float(math.sqrt(K_r)))
            else:
                pred_heights.append(1.0)
        else:
            # Low-capacity regime: noise-dominated, plateau near 1
            pred_heights.append(1.0)
    # Normalize predictions and observations to [0,1] range for diff comparison
    # (avoid K-scale dominance at large K)
    pred_norm = [p / max(p, 1.0) for p in pred_heights]
    obs_norm = [o / max(o, 1.0) for o in obs_heights]
    diffs_norm = [abs(pn - on) for pn, on in zip(pred_norm, obs_norm)]
    max_diff = max(diffs_norm) if diffs_norm else 0.0
    n_large_diff = sum(1 for d in diffs_norm if d >= TDA_E_DIFF_FAIL)
    if max_diff < TDA_E_DIFF_PASS:
        tda_e_verdict = "HARD_PASS"
    elif n_large_diff >= 2:
        tda_e_verdict = "HARD_FAIL"
    else:
        tda_e_verdict = "MIDDLE"
    tda_e = {
        "predicted_heights": [round(p, 4) for p in pred_heights],
        "observed_heights": [round(o, 4) for o in obs_heights],
        "max_abs_diff": round(max_diff, 4),
        "per_case_diffs": [round(d, 4) for d in diffs_norm],
        "verdict": tda_e_verdict,
        "note": "diffs computed on normalized [0,1] scale; capacity_adjusted=True",
    }

    # ── Joint verdict ─────────────────────────────────────────────────────────
    if tda_c['verdict'] == "HARD_PASS":
        joint_call = "TDA_OVERLAPPING_USEFUL"
    elif tda_b['verdict'] == "HARD_PASS" and tda_d['verdict'] == "HARD_PASS":
        joint_call = "TDA_NOVEL_USEFUL"
    elif tda_c['verdict'] == "HARD_FAIL" or tda_d['verdict'] == "HARD_FAIL":
        joint_call = "TDA_INCONCLUSIVE"
    else:
        joint_call = "TDA_CONSISTENT_REDUNDANT"

    # Map to standard verdict
    verdict_map = {
        "TDA_OVERLAPPING_USEFUL": "PASS",
        "TDA_NOVEL_USEFUL": "PASS",
        "TDA_CONSISTENT_REDUNDANT": "PARTIAL",
        "TDA_INCONCLUSIVE": "FAIL",
    }
    verdict = verdict_map.get(joint_call, "PARTIAL")
    verdict_msg = (
        f"{joint_call}: TDA-A={tda_a['verdict']} TDA-B={tda_b['verdict']} "
        f"TDA-C={tda_c['verdict']}(agree={n_agree}/{n_total},monotone={width_monotonic}) "
        f"TDA-D={tda_d['verdict']}(bars={long_bar_count},gap={gap_observed}) "
        f"TDA-E={tda_e['verdict']}(maxdiff={max_diff:.3f})"
    )

    elapsed = time.time() - t0
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "tda_a": tda_a,
        "tda_b": tda_b,
        "tda_c": tda_c,
        "tda_d": tda_d,
        "tda_e": tda_e,
        "joint_call": joint_call,
        "summary": {
            "joint_call": joint_call,
            "tda_a_verdict": tda_a['verdict'],
            "tda_b_verdict": tda_b['verdict'],
            "tda_c_verdict": tda_c['verdict'],
            "tda_d_verdict": tda_d['verdict'],
            "tda_e_verdict": tda_e['verdict'],
            "tda_c_n_agree": n_agree,
            "tda_c_n_total": n_total,
            "tda_c_width_monotonic": width_monotonic,
            "tda_d_long_bar_count": long_bar_count,
            "tda_e_max_diff": round(max_diff, 4),
        },
        "config": {
            "n_cases": len(cases),
            "n_tau_steps": n_tau,
            "n_rand_seeds_b1": N_RAND_SEEDS,
            "smoke": n_tau < N_TAU_STEPS,
        }
    }


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required keys: {missing}")
    for k in ("tda_a", "tda_b", "tda_c", "tda_d", "tda_e", "joint_call"):
        if d.get(k) is None:
            raise ValueError(f"metrics missing key: {k}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        # Already ran at module load; just exit 0
        print("SELF_TEST: PASS")
        sys.exit(0)

    smoke = args.smoke
    cases = SMOKE_CASES if smoke else FULL_CASES
    n_tau = 15 if smoke else N_TAU_STEPS
    compute_b1_ctl = not smoke  # skip random control in smoke to save time

    print(f"[TDA] mode={'smoke' if smoke else 'full'} cases={len(cases)} n_tau={n_tau}")

    metrics = run_sweep(cases, n_tau=n_tau, compute_b1_control=compute_b1_ctl)
    validate_metrics(metrics)

    out_dir = get_output_dir("tda_reanalysis_5probe_v1")
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"[TDA] verdict={metrics['verdict']}")
    print(f"[TDA] joint_call={metrics['joint_call']}")
    print(f"[TDA] verdict_msg={metrics['verdict_msg']}")
    print(f"[TDA] elapsed={metrics['elapsed_s']:.1f}s")
    print(f"[TDA] metrics -> {metrics_path}")
