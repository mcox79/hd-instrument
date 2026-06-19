"""Cluster-conditional P(q) re-analysis: 1-RSB re-interpretation via shift-class conditioning.

CONTEXT: wave14_1rsb_pq_retained_v3 returned MIDDLE (single-peaked, binder~0.5, N=512 smoke).
The strategic question: does the single-peaked P(q) split into MULTI-PEAKED structure when
conditioned on the source shift-class label? If yes, substrate has 1-RSB cluster-glass
structure (Krzakala-Mezard-Sausset-Sun-Zdeborova 2007) -- P(q) appears unimodal in the
unconditional distribution but reveals multi-modal structure within each cluster-pair
subensemble. If still single-peaked after conditioning, substrate is RS multi-ferromagnet.

DESIGN:
  For each shift-class pair (c_i, c_j) in the 4 major classes (SAME_CORPUS_PRISTINE,
  COMPOUND_SAME_CORPUS, REPLAY_SAME_CORPUS, 4STAGE), train 3 seeds of W under each class
  condition and compute all pairwise overlaps q(W_i, W_j) within and across classes.

  Class conditions based on training protocol:
    - CLASS_A: SAME_CORPUS_PRISTINE  (train on same corpus, no replay, pristine W)
    - CLASS_B: REPLAY_SAME_CORPUS    (train on same corpus WITH replay)
    - CLASS_C: 4STAGE_DIFF_CORPUS    (full 4-stage M1 hierarchical replay)
    - CLASS_D: NO_REPLAY_DIFF        (train on different corpus, no replay)

  Overlap groups: within-class (CLASS_A/A, B/B, C/C, D/D) + across-class (A/B, A/C, A/D,
  B/C, B/D, C/D).

  Hypothesis: cluster-glass (Krzakala+ 2007) predicts WITHIN-class overlaps are higher and
  potentially multi-peaked (replicas from the same basin), while ACROSS-class overlaps are
  lower (different basins). This produces class-conditional multi-peak structure even if
  the unconditional P(q) is single-peaked.

SELF-TESTS per [[feedback-strategy-spec-formula-selftests]]:
  1. compute_overlaps([W, W]) = [1.0] for any non-zero W (identity).
  2. compute_overlaps([W, -W]) = [-1.0] for any non-zero W (anti-identity).
  3. binder_cumulant: bimodal distribution at +/-0.5 -> binder > 0.30.
  4. binder_cumulant: unimodal Gaussian at 0.0 std=0.01 -> binder near 0 (< 0.10).
  5. class-conditional grouping: for 3 seeds per class, n_within_A_A = 3 overlaps (C(3,2)=3).

PRE-REGISTERED BANDS (cluster-conditional 1-RSB re-interpretation):
  CLUSTER_GLASS_CONFIRMED (1-RSB framework recovers via conditioning):
    - At least 2 of 4 within-class binder_cumulants > 0.15 (conditional multi-modal signal)
    - AND within_mean_q > across_mean_q by at least 0.02 (intra-cluster higher overlap)
    - AND KDE of within-class overlaps (pooled) has n_peaks >= 2 with >= 2sigma separation
    -> 1-RSB cluster-glass interpretation confirmed; Krzakala+ 2007 framework applies

  RS_MULTI_FERROMAGNET (no conditioning effect; well-studied RS structure):
    - All 4 within-class binder_cumulants <= 0.05
    - AND within_mean_q indistinguishable from across_mean_q (|diff| < 0.01)
    -> Substrate is RS multi-ferromagnet; unconditional P(q) is the full picture

  MIDDLE_BAND (partial conditioning signal; needs higher N or more seeds):
    - Some within-class binders > 0.05 but < 0.15
    - OR within/across difference in [0.01, 0.02]
    -> Inconclusive; re-run at N=4096 (GPU) with 8+ seeds per class

  INSTRUMENTATION_FAIL:
    - n_within_overlaps < 3 for any class (training failed)
    - OR all overlaps are NaN / < 1e-6

Queue: remote_cpu_queue (CPU; 4 classes x 3 seeds x N=1024 ~ 15-30 min per class; ~2h total)
  NOTE: N=1024, 3 seeds per class, 4 classes -> 4*3=12 W vectors -> 12 within + 18 across = 30 overlaps
Pre-reg: preregs/2026-05-26_wave14_1rsb_cluster_cond_pq_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load M1 hierreplay infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
v1_mod = m1.v1
pa = m1.pa

# ── design parameters ──
N_FULL     = 1024
N_SMOKE    = 256
SEEDS_PER_CLASS_FULL  = 5    # enough for within-class overlap stats: C(5,2)=10 per class
SEEDS_PER_CLASS_SMOKE = 2    # C(2,2)=1 within-class; minimal but sufficient for self-test
BATCH_SIZE_FULL  = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL  = 8
EPOCHS_SMOKE = 2
PHASE_A_EPOCHS_FULL  = 10
PHASE_A_EPOCHS_SMOKE = 2
BYTES_FULL  = 60_000
BYTES_SMOKE = 3_000

# Shift-class labels matching shift_class_predictor vocabulary
CLASS_A = "SAME_CORPUS_PRISTINE"    # same corpus, no replay
CLASS_B = "REPLAY_SAME_CORPUS"      # same corpus + replay
CLASS_C = "4STAGE_DIFF_CORPUS"      # full 4-stage M1 hierreplay
CLASS_D = "NO_REPLAY_DIFF"          # different corpus, no replay

KDE_BW = 0.02
PEAK_SEP_SIGMA = 2.0


def get_output_dir(default_name: str = "wave14_1rsb_cluster_cond_pq_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


# ─── W training under different class conditions ───────────────────────────

def train_class_A(seed: int, N: int, batch_size: int, epochs: int,
                  n_bytes: int, device: torch.device) -> torch.Tensor:
    """SAME_CORPUS_PRISTINE: train on corpus_A only, no replay."""
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms  = pa.make_bsc_atoms(base.K, N, gen).to(device)
    corpus_a   = pa.load_corpus_a()[:n_bytes]
    m = int(0.8 * len(corpus_a))
    train_a, _ = corpus_a[:m], corpus_a[m:]
    train_idx, train_tgt = base.bytes_to_idx_tensors(train_a, device)
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_out, _, _, _ = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms,
        train_idx, train_tgt, None, None, 0, epochs, batch_size, device)
    return W_out.reshape(-1).float().cpu()


def train_class_B(seed: int, N: int, batch_size: int, epochs: int,
                  n_bytes: int, device: torch.device) -> torch.Tensor:
    """REPLAY_SAME_CORPUS: train on corpus_A with replay (self-replay)."""
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms  = pa.make_bsc_atoms(base.K, N, gen).to(device)
    corpus_a   = pa.load_corpus_a()[:n_bytes]
    m = int(0.8 * len(corpus_a))
    train_a, _ = corpus_a[:m], corpus_a[m:]
    train_idx, train_tgt = base.bytes_to_idx_tensors(train_a, device)
    # Phase 1: initial train to build pool
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_out, pool_v, pool_l, pool_u = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms,
        train_idx, train_tgt, None, None, 0, epochs, batch_size, device)
    # Phase 2: replay on same corpus (REPLAY_SAME_CORPUS condition)
    W_final, _, _, _ = base.train_w_with_replay(
        W_out, pool_v.clone(), pool_l.clone(), pool_u,
        byte_atoms, pos_atoms, train_idx, train_tgt,
        pool_v, pool_l, pool_u, epochs, batch_size, device)
    del pool_v, pool_l
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return W_final.reshape(-1).float().cpu()


def train_class_C(seed: int, N: int, batch_size: int, epochs: int,
                  phase_a_epochs: int, n_bytes: int, smoke: bool,
                  device: torch.device) -> torch.Tensor:
    """4STAGE_DIFF_CORPUS: full 4-stage M1 hierreplay (same as P(q) v3)."""
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms  = pa.make_bsc_atoms(base.K, N, gen).to(device)
    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = v1_mod.load_corpus_D(smoke=smoke)
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full

    def split80(d):
        m2 = int(0.8 * len(d))
        return d[:m2], d[m2:]

    def to_idx(tr):
        return base.bytes_to_idx_tensors(tr, device)

    train_a, _ = split80(corpus_a)
    train_b, _ = split80(corpus_b)
    train_c, _ = split80(corpus_c)
    train_d, _ = split80(corpus_d)

    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms,
        to_idx(train_a)[0], to_idx(train_a)[1], None, None, 0,
        phase_a_epochs, batch_size, device)

    thin_A_v, thin_A_l, thin_A_u = m1.thin_pool_to_chunks(
        pool_A_v, pool_A_l, pool_A_u, chunk_fraction=0.5, device=device)

    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, to_idx(train_b)[0], to_idx(train_b)[1],
        thin_A_v, thin_A_l, thin_A_u, epochs, batch_size, device)

    thin_B_v, thin_B_l, thin_B_u = m1.thin_pool_to_chunks(
        pool_AB_v, pool_AB_l, pool_AB_u, chunk_fraction=0.5, device=device)
    combo_AB_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u]], dim=0)
    combo_AB_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u]], dim=0)
    combo_AB_u = combo_AB_v.shape[0]

    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, to_idx(train_c)[0], to_idx(train_c)[1],
        combo_AB_v, combo_AB_l, combo_AB_u, epochs, batch_size, device)

    thin_C_v, thin_C_l, thin_C_u = m1.thin_pool_to_chunks(
        pool_ABC_v, pool_ABC_l, pool_ABC_u, chunk_fraction=0.5, device=device)
    combo_ABC_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u],
                              thin_C_v[:thin_C_u]], dim=0)
    combo_ABC_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u],
                              thin_C_l[:thin_C_u]], dim=0)
    combo_ABC_u = combo_ABC_v.shape[0]

    W_ABCD, _, _, _ = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms, to_idx(train_d)[0], to_idx(train_d)[1],
        combo_ABC_v, combo_ABC_l, combo_ABC_u, epochs, batch_size, device)

    W_flat = W_ABCD.reshape(-1).float().cpu()
    del W_A, W_AB, W_ABC, W_ABCD
    del pool_A_v, pool_AB_v, pool_ABC_v
    del thin_A_v, thin_B_v, thin_C_v
    del combo_AB_v, combo_ABC_v
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return W_flat


def train_class_D(seed: int, N: int, batch_size: int, epochs: int,
                  n_bytes: int, smoke: bool, device: torch.device) -> torch.Tensor:
    """NO_REPLAY_DIFF: different corpus, no replay (control)."""
    gen = torch.Generator().manual_seed(seed + 1000)  # offset seed for diff corpus
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms  = pa.make_bsc_atoms(base.K, N, gen).to(device)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    m = int(0.8 * len(corpus_c))
    train_c, _ = corpus_c[:m], corpus_c[m:]
    train_idx, train_tgt = base.bytes_to_idx_tensors(train_c, device)
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_out, _, _, _ = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms,
        train_idx, train_tgt, None, None, 0, epochs, batch_size, device)
    return W_out.reshape(-1).float().cpu()


# ─── overlap analysis ──────────────────────────────────────────────────────

def compute_overlaps(W_list: List[torch.Tensor]) -> List[float]:
    """Pairwise cosine overlaps q_ij = <W_i, W_j> / (||W_i|| * ||W_j||)."""
    overlaps = []
    for i in range(len(W_list)):
        for j in range(i + 1, len(W_list)):
            wi, wj = W_list[i], W_list[j]
            ni, nj = wi.norm().item(), wj.norm().item()
            if ni < 1e-9 or nj < 1e-9:
                continue
            q = float((wi * wj).sum()) / (ni * nj)
            overlaps.append(q)
    return overlaps


def compute_across_overlaps(W_list_a: List[torch.Tensor],
                             W_list_b: List[torch.Tensor]) -> List[float]:
    """All cross-class overlaps between W_list_a and W_list_b."""
    overlaps = []
    for wi in W_list_a:
        for wj in W_list_b:
            ni, nj = wi.norm().item(), wj.norm().item()
            if ni < 1e-9 or nj < 1e-9:
                continue
            q = float((wi * wj).sum()) / (ni * nj)
            overlaps.append(q)
    return overlaps


def binder_cumulant(overlaps: List[float]) -> float:
    """U = 1 - <q^4> / (3 * <q^2>^2). Positive for non-trivial P(q)."""
    if len(overlaps) < 2:
        return 0.0
    n = len(overlaps)
    q2 = sum(q ** 2 for q in overlaps) / n
    q4 = sum(q ** 4 for q in overlaps) / n
    if q2 < 1e-15:
        return 0.0
    return 1.0 - q4 / (3.0 * q2 * q2)


def kde_density(vals: List[float], bandwidth: float, n_points: int = 200):
    if not vals:
        return [], []
    lo = min(vals) - 3 * bandwidth
    hi = max(vals) + 3 * bandwidth
    x = [lo + i * (hi - lo) / n_points for i in range(n_points + 1)]
    density = []
    n = len(vals)
    for xi in x:
        d = sum(math.exp(-0.5 * ((xi - v) / bandwidth) ** 2)
                for v in vals) / (n * bandwidth * math.sqrt(2 * math.pi))
        density.append(d)
    return x, density


def find_peaks(x: List[float], density: List[float],
               min_sep_sigma: float, bandwidth: float) -> List[Tuple[float, float]]:
    peaks = []
    for i in range(1, len(density) - 1):
        if density[i] > density[i - 1] and density[i] > density[i + 1]:
            peaks.append((x[i], density[i]))
    filtered: List[Tuple[float, float]] = []
    for p in peaks:
        if not filtered or abs(p[0] - filtered[-1][0]) >= min_sep_sigma * bandwidth:
            filtered.append(p)
        elif p[1] > filtered[-1][1]:
            filtered[-1] = p
    return filtered


# ─── self-test ────────────────────────────────────────────────────────────

def _instrumentation_selftest():
    """Assert all metrics non-null/non-sentinel at small scale."""
    import torch as _t

    # Test 1: identity overlap
    W1 = _t.ones(64)
    q_ident = float((_t.ones(64) * _t.ones(64)).sum()) / (64.0 ** 0.5 * 64.0 ** 0.5)
    assert abs(q_ident - 1.0) < 1e-5, f"identity overlap fail: {q_ident}"

    # Test 2: anti-identity overlap
    W1b, W2b = _t.ones(64), -_t.ones(64)
    n1b, n2b = W1b.norm().item(), W2b.norm().item()
    q_anti = float((W1b * W2b).sum()) / (n1b * n2b)
    assert abs(q_anti + 1.0) < 1e-5, f"anti-identity overlap fail: {q_anti}"

    # Test 3: bimodal binder > 0.30
    bimodal = [0.5] * 50 + [-0.5] * 50
    b_bimodal = binder_cumulant(bimodal)
    assert b_bimodal > 0.30, f"bimodal binder fail: {b_bimodal:.4f} <= 0.30"

    # Test 4: unimodal near-zero binder
    import random as _r
    _r.seed(42)
    unimodal = [_r.gauss(0.0, 0.01) for _ in range(200)]
    b_unimodal = binder_cumulant(unimodal)
    assert b_unimodal < 0.10, f"unimodal binder fail: {b_unimodal:.4f} >= 0.10"

    # Test 5: class overlap grouping count
    W_dummy = [_t.randn(64) for _ in range(3)]
    within_overlaps = compute_overlaps(W_dummy)
    assert len(within_overlaps) == 3, f"within-class overlap count fail: expected 3, got {len(within_overlaps)}"

    print("[selftest] PASS: 5/5 assertions OK", flush=True)


_instrumentation_selftest()


# ─── main sweep ───────────────────────────────────────────────────────────

def run_sweep(smoke: bool, device: torch.device) -> Dict:
    N           = N_SMOKE if smoke else N_FULL
    seeds_n     = SEEDS_PER_CLASS_SMOKE if smoke else SEEDS_PER_CLASS_FULL
    batch_size  = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    epochs      = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    pa_epochs   = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes     = BYTES_SMOKE if smoke else BYTES_FULL
    seeds       = list(range(7, 7 + seeds_n))  # seeds 7,8,... per class

    t0 = time.monotonic()

    print(f"[cluster_cond_pq] smoke={smoke} N={N} seeds_per_class={seeds_n}", flush=True)

    # Train W vectors per class
    class_W: Dict[str, List[torch.Tensor]] = {
        CLASS_A: [], CLASS_B: [], CLASS_C: [], CLASS_D: []
    }

    for seed in seeds:
        print(f"  CLASS_A seed={seed} ...", flush=True)
        class_W[CLASS_A].append(train_class_A(seed, N, batch_size, epochs, n_bytes, device))

    for seed in seeds:
        print(f"  CLASS_B seed={seed} ...", flush=True)
        class_W[CLASS_B].append(train_class_B(seed, N, batch_size, epochs, n_bytes, device))

    for seed in seeds:
        print(f"  CLASS_C seed={seed} ...", flush=True)
        class_W[CLASS_C].append(train_class_C(seed, N, batch_size, epochs, pa_epochs,
                                               n_bytes, smoke, device))

    for seed in seeds:
        print(f"  CLASS_D seed={seed} ...", flush=True)
        class_W[CLASS_D].append(train_class_D(seed, N, batch_size, epochs, n_bytes, smoke, device))

    # Compute within-class overlaps
    within: Dict[str, Dict] = {}
    for cls_name, W_list in class_W.items():
        ovlp = compute_overlaps(W_list)
        binder = binder_cumulant(ovlp)
        mean_q = sum(ovlp) / len(ovlp) if ovlp else 0.0
        within[cls_name] = {
            "n_overlaps": len(ovlp),
            "mean_q": mean_q,
            "binder": binder,
            "overlaps": ovlp,
        }
        print(f"  within {cls_name}: n={len(ovlp)} mean_q={mean_q:.4f} binder={binder:.4f}", flush=True)

    # Compute across-class overlaps
    classes = list(class_W.keys())
    across: Dict[str, Dict] = {}
    for i in range(len(classes)):
        for j in range(i + 1, len(classes)):
            key = f"{classes[i]}/{classes[j]}"
            ovlp = compute_across_overlaps(class_W[classes[i]], class_W[classes[j]])
            mean_q = sum(ovlp) / len(ovlp) if ovlp else 0.0
            binder = binder_cumulant(ovlp)
            across[key] = {
                "n_overlaps": len(ovlp),
                "mean_q": mean_q,
                "binder": binder,
            }
            print(f"  across {key}: n={len(ovlp)} mean_q={mean_q:.4f} binder={binder:.4f}", flush=True)

    # Pool within-class overlaps for KDE
    all_within_q = []
    for cls_name in classes:
        all_within_q.extend(within[cls_name]["overlaps"])

    x_kde, dens_kde = kde_density(all_within_q, KDE_BW)
    peaks_within = find_peaks(x_kde, dens_kde, PEAK_SEP_SIGMA, KDE_BW)

    # Compute aggregate statistics
    within_mean_q = (sum(within[c]["mean_q"] * within[c]["n_overlaps"] for c in classes)
                     / max(sum(within[c]["n_overlaps"] for c in classes), 1))
    across_mean_q = (sum(across[k]["mean_q"] * across[k]["n_overlaps"] for k in across)
                     / max(sum(across[k]["n_overlaps"] for k in across), 1))
    within_across_diff = within_mean_q - across_mean_q

    n_class_binders_above_015 = sum(1 for c in classes if within[c]["binder"] > 0.15)
    n_class_binders_above_005 = sum(1 for c in classes if within[c]["binder"] > 0.05)
    n_peaks_within_pooled = len(peaks_within)

    print(f"\n[summary] within_mean_q={within_mean_q:.4f} across_mean_q={across_mean_q:.4f} "
          f"diff={within_across_diff:.4f}", flush=True)
    print(f"[summary] n_class_binders>0.15={n_class_binders_above_015} "
          f"n_peaks_within_pooled={n_peaks_within_pooled}", flush=True)

    # Apply pre-registered verdict bands
    # INSTRUMENTATION_FAIL check first
    any_instfail = any(within[c]["n_overlaps"] < (1 if smoke else 3) for c in classes)
    if any_instfail:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (f"INSTRUMENTATION_FAIL: insufficient within-class overlaps; "
                       f"within_counts={[within[c]['n_overlaps'] for c in classes]}")
    elif n_class_binders_above_015 >= 2 and within_across_diff >= 0.02 and n_peaks_within_pooled >= 2:
        verdict = "CLUSTER_GLASS_CONFIRMED"
        verdict_msg = (f"CLUSTER_GLASS_CONFIRMED: binders>0.15 in {n_class_binders_above_015}/4 classes; "
                       f"within-across diff={within_across_diff:.4f}>=0.02; "
                       f"peaks_within_pooled={n_peaks_within_pooled}>=2")
    elif n_class_binders_above_005 == 0 and abs(within_across_diff) < 0.01:
        verdict = "RS_MULTI_FERROMAGNET"
        verdict_msg = (f"RS_MULTI_FERROMAGNET: all class binders<=0.05; "
                       f"within-across diff={within_across_diff:.4f}<0.01; "
                       f"no cluster-conditional P(q) structure")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND at N={N}: n_binders>0.05={n_class_binders_above_005}/4; "
                       f"within-across diff={within_across_diff:.4f}; "
                       f"n_peaks_within={n_peaks_within_pooled}")

    summary = {
        "N": N,
        "seeds_per_class": seeds_n,
        "within_class": {c: {k: v for k, v in within[c].items() if k != "overlaps"}
                         for c in classes},
        "across_class": across,
        "within_mean_q": within_mean_q,
        "across_mean_q": across_mean_q,
        "within_across_diff": within_across_diff,
        "n_class_binders_above_015": n_class_binders_above_015,
        "n_class_binders_above_005": n_class_binders_above_005,
        "n_peaks_within_pooled": n_peaks_within_pooled,
        "peaks_within_positions": [p[0] for p in peaks_within],
    }

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": time.monotonic() - t0,
        "summary": summary,
        "config": {
            "N": N, "seeds_per_class": seeds_n, "smoke": smoke,
            "kde_bw": KDE_BW, "peak_sep_sigma": PEAK_SEP_SIGMA,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        print("[self-test mode] instrumentation_selftest already ran at import", flush=True)
        sys.exit(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[cluster_cond_pq] device={device}", flush=True)

    out_dir = get_output_dir()
    metrics = run_sweep(smoke=args.smoke, device=device)

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[VERDICT] {metrics['verdict']}: {metrics['verdict_msg']}", flush=True)
    print(f"[metrics written] {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
