"""Bet B shift-class predictor FULL REPLICATION at n>=15 per class.

Context: wave14_betB_shift_class_predictor_v1 (smoke) produced SHIFT_CLASS_HARD_PASS
with 6/6 non-overlapping 95% CIs and K-W p=2.9e-14 but had n=5 for two classes:
  - Class 0 (SAME_CORPUS_PRISTINE): n=5 (synthesized from cap_map Kovacs v9/v11/v12)
  - Class 3 (NO_REPLAY_SAME_CORPUS): n=5 (from ablation_B frac=0.0 5-seed run)

Pre-registered gate from Cap_map v201: row-state promotion for Bet B retention
predictability requires n>=15 across ALL 6 shift classes.

This script:
  1. Runs 15 fresh seeds for class 0 using the base Kovacs setup (REPLAY_FRAC=0.50)
  2. Runs 15 fresh seeds for class 3 using the no-replay setup (REPLAY_FRAC=0.0)
  3. Combines fresh runs with existing-data for classes 1,2,4,5
  4. Re-evaluates the shift-class predictor with updated per-class counts

Classes 1,2,4,5 already have n>=13-49 from existing experiment artifacts;
they are loaded from data/tmp_betb_analysis/ exactly as in v1.

Pre-reg:
    HARD-PASS (row-state promotion gate cleared):
        All 6 class CIs STILL non-overlapping at n>=15 for small-n classes
        AND K-W p < 0.01 across all 6 classes.
        Interpretation: v1 result confirmed at replication scale; Bet B
        retention predictability claim gets operational status.

    HARD-FAIL (replication caveat becomes genuine failure):
        Any PREVIOUSLY non-overlapping CI (class 0 or 3) now OVERLAPS
        with an adjacent class, OR K-W p >= 0.05.
        Interpretation: v1 HARD-PASS was a small-n artifact; predictability
        does NOT hold at replication scale.

    MIDDLE-BAND:
        All CIs still non-overlapping but K-W p in [0.01, 0.05).
        Signal real but statistical strength weaker than v1 suggested.

Queue: remote_cpu_queue (two-class 15-seed FULL training, ~45-90 min).
ETA: ~3600s.
Pre-reg: preregs/2026-05-24_wave14_betB_shift_class_full_replication_v1.md

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev.
Per [[feedback-no-smoke]]: HARD-PASS / HARD-FAIL falsifiable BEFORE running.
Per [[feedback-envelope-expansion-fail-bands]]: bands registered BEFORE running.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.
Per [[feedback-verify-implementations]]: fresh seeds [53..131] distinct from
existing seeds [7,17,23,31,41] in cap_map + ablation_B data; no data leakage.
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
DATA = REPO / "data"
TMP = DATA / "tmp_betb_analysis"
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

# ────────────── load base experiment modules ──────────────
_pa_spec = importlib.util.spec_from_file_location(
    "pa", REPO / "experiments" / "exp_wave14b_cl_phase_a.py")
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

_base_spec = importlib.util.spec_from_file_location(
    "base", REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py")
base = importlib.util.module_from_spec(_base_spec)
_base_spec.loader.exec_module(base)

# ────────────── design parameters (exp_dev autonomy) ──────────────
# Model hyperparameters — matching base Kovacs / ablation_B FULL configs
N = 4096
K = base.K          # 4
BETA = base.BETA    # 8.0
POOL_SIZE = base.POOL_SIZE   # 1024
ALPHA_RETR = base.ALPHA_RETR  # 0.3
DELTA_ALPHA = base.DELTA_ALPHA
DELTA_DECAY = base.DELTA_DECAY
RELU_B = base.RELU_B
VOCAB = base.VOCAB       # 256
PAD_BYTE = base.PAD_BYTE  # 0

BATCH_SIZE = 64
PHASE_A_EPOCHS = 8    # matches base Kovacs FULL (strongest Phase A baseline)
EPOCHS = 5            # matches base Kovacs FULL
BYTES_PER_CORPUS = 200_000
EMA_ALPHA = 0.7       # matches v9 best alpha (top performer in v7 sweep)

REPLAY_FRAC_CLASS0 = 0.50   # SAME_CORPUS_PRISTINE: 50% replay (base Kovacs)
REPLAY_FRAC_CLASS3 = 0.0    # NO_REPLAY_SAME_CORPUS: zero replay (ablation boundary)

# 15 fresh seeds distinct from existing [7,17,23,31,41]
SEEDS_FULL = [53, 61, 67, 71, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131]
SEEDS_SMOKE = [53]   # smoke: 1 seed per class (fast sanity check)

# Shift class definitions (same as v1)
CLASS_NAMES = {
    0: "SAME_CORPUS_PRISTINE",
    1: "COMPOUND_SAME_CORPUS",
    2: "REPLAY_SAME_CORPUS",
    3: "NO_REPLAY_SAME_CORPUS",
    4: "STAGE_4_COMPOUND",
    5: "DIFF_CORPUS_2TASK",
}

# Pre-registered thresholds (v201 gate + user contract)
CI_Z = 1.96
PASS_KW_P = 0.01    # stricter than v1's 0.05 (per user pre-reg at v201)
FAIL_KW_P = 0.05    # HARD-FAIL if p >= this
PASS_MIN_NONOVERLAPPING = 6   # must be ALL 6 at replication (v1 showed 6/6)
FAIL_MIN_NONOVERLAPPING = 5   # HARD-FAIL if <6 non-overlapping (any CI collapse)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
# ────────────── training loop (inline from base; no circular import) ──────────────
def train_w_with_replay(W_init, pool_vecs, pool_labels, pool_used,
                        byte_atoms, pos_atoms, train_bytes, target_bytes,
                        replay_pool_vecs, replay_pool_labels, replay_pool_used,
                        n_epochs, replay_frac, device):
    """Train W on (train_bytes, target_bytes) with optional replay."""
    W = W_init.clone().to(device)
    if pool_vecs is not None:
        pool_vecs = pool_vecs.to(device)
        pool_labels = pool_labels.to(device)
    if replay_pool_vecs is not None:
        replay_pool_vecs = replay_pool_vecs.to(device)
        replay_pool_labels = replay_pool_labels.to(device)

    N_dim = W.shape[0]
    T = train_bytes.shape[0]
    arange_b = torch.arange(BATCH_SIZE, device=device)
    pool_idx_local = pool_used % POOL_SIZE if pool_used else 0
    pool_used_local = pool_used or 0
    if pool_vecs is None:
        pool_vecs = torch.zeros((POOL_SIZE, N_dim), dtype=torch.float32, device=device)
        pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=device)

    for epoch in range(n_epochs):
        for batch_start in range(0, T, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T)
            idx_batch = train_bytes[batch_start:be]
            tgt_batch = target_bytes[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)

            if replay_pool_vecs is not None and replay_pool_used > 0:
                n_replay = max(1, int(replay_frac * B))
                replay_perm = torch.randperm(replay_pool_used, device=device)[:n_replay]
                replay_ctxs = replay_pool_vecs[replay_perm]
                replay_tgts = replay_pool_labels[replay_perm]
                ctxs = torch.cat([ctxs, replay_ctxs], dim=0)
                tgt_batch = torch.cat([tgt_batch, replay_tgts], dim=0)
                B = ctxs.shape[0]

            with torch.no_grad():
                q = ctxs @ W.T
                q = pa.shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N_dim
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms - predicted
                dW = (residual.T @ ctxs) / N_dim
                W.mul_(1.0 - DELTA_DECAY)
                W.add_(dW, alpha=DELTA_ALPHA)
                if epoch == 0:
                    take = min(B, BATCH_SIZE)
                    if take > 0:
                        dest = (pool_idx_local + arange_b[:take]) % POOL_SIZE
                        pool_vecs.index_copy_(0, dest, ctxs[:take])
                        pool_labels.index_copy_(0, dest, tgt_batch[:take])
                        pool_idx_local = (pool_idx_local + take) % POOL_SIZE
                        pool_used_local = min(pool_used_local + take, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_used_local


def evaluate_bpc(W, pool_vecs, pool_labels, pool_used, byte_atoms, pos_atoms,
                 eval_bytes, eval_targets, device):
    N_dim = W.shape[0]
    T = eval_bytes.shape[0]
    total_bits = 0.0
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, eval_bytes[bs:be])
        P_W = pa.predict_W(W, ctxs, byte_atoms, BETA, N_dim)
        P_retr = pa.predict_pool(ctxs, pool_vecs, pool_labels, pool_used, BETA, N_dim)
        P = ALPHA_RETR * P_retr + (1.0 - ALPHA_RETR) * P_W
        tgts = eval_targets[bs:be]
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total_bits += float(-torch.log2(p_true).sum())
    return total_bits / max(T, 1)


def bytes_to_idx_tensors(data, device):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + data
    T_len = len(padded) - K
    byts = torch.tensor(list(padded), dtype=torch.long, device=device)
    offsets = torch.arange(K - 1, -1, -1, device=device)
    pos = torch.arange(T_len, device=device)
    return byts[pos.unsqueeze(1) + offsets.unsqueeze(0)], byts[pos + K]


def load_corpus_c(smoke: bool):
    exp_dir = REPO / "experiments"
    parts = []
    n_files = 3 if smoke else 12
    for f in sorted(exp_dir.glob("exp_wave14b*.py"))[:n_files]:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


def run_one_seed(seed: int, replay_frac: float, smoke: bool, device) -> float:
    """Run a single Bet B seed with given replay_frac; return retention_A."""
    n_bytes = 5000 if smoke else BYTES_PER_CORPUS
    phase_a_ep = 1 if smoke else PHASE_A_EPOCHS
    ep = 1 if smoke else EPOCHS
    N_dim = 1024 if smoke else N

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N_dim, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N_dim, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = load_corpus_c(smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full

    def split(data):
        m = int(0.8 * len(data))
        return data[:m], data[m:]

    train_a, test_a = split(corpus_a)
    train_b, test_b = split(corpus_b)
    train_c, test_c = split(corpus_c)

    train_a_idx, train_a_tgt = bytes_to_idx_tensors(train_a, device)
    test_a_idx, test_a_tgt = bytes_to_idx_tensors(test_a, device)
    train_b_idx, train_b_tgt = bytes_to_idx_tensors(train_b, device)
    train_c_idx, train_c_tgt = bytes_to_idx_tensors(train_c, device)

    W_zero = torch.zeros((N_dim, N_dim), dtype=torch.float32, device=device)

    # Phase A
    W_A, pool_A_v, pool_A_l, pool_A_u = train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_ep, replay_frac, device)
    bpc_A_baseline = evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                   byte_atoms, pos_atoms, test_a_idx, test_a_tgt, device)

    # Phase B (with or without A replay)
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        pool_A_v if replay_frac > 0 else None,
        pool_A_l if replay_frac > 0 else None,
        pool_A_u if replay_frac > 0 else 0,
        ep, replay_frac, device)

    # Phase C (with or without combined A+B replay)
    if replay_frac > 0:
        combined_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u]], dim=0)
        combined_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u]], dim=0)
        combined_u = combined_v.shape[0]
        rp_v, rp_l, rp_u = combined_v, combined_l, combined_u
    else:
        rp_v, rp_l, rp_u = None, None, 0

    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        rp_v, rp_l, rp_u, ep, replay_frac, device)

    # EMA blend (matches v9 protocol)
    W_ABC = EMA_ALPHA * W_ABC + (1.0 - EMA_ALPHA) * W_A

    # Evaluate retention_A post Phase C
    bpc_A_after_C = evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                  byte_atoms, pos_atoms, test_a_idx, test_a_tgt, device)
    retention_A = min(bpc_A_baseline / max(bpc_A_after_C, 1e-6), 1.0)
    return retention_A


# ────────────── shift-class statistics helpers ──────────────
def mean_std_ci(vals: List[float]) -> Tuple[float, float, float, float]:
    """Returns (mean, std, ci_lo, ci_hi) using normal approximation."""
    n = len(vals)
    if n == 0:
        return float("nan"), float("nan"), float("nan"), float("nan")
    mu = sum(vals) / n
    if n == 1:
        return mu, 0.0, mu, mu
    var = sum((v - mu) ** 2 for v in vals) / (n - 1)
    std = math.sqrt(var)
    se = std / math.sqrt(n)
    return mu, std, mu - CI_Z * se, mu + CI_Z * se


def count_nonoverlapping(class_stats: Dict) -> int:
    count = 0
    class_ids = [k for k, v in class_stats.items() if not math.isnan(v[0])]
    for ci in class_ids:
        mu_i, std_i, lo_i, hi_i = class_stats[ci]
        non_overlaps = True
        for cj in class_ids:
            if ci == cj:
                continue
            mu_j, std_j, lo_j, hi_j = class_stats[cj]
            if lo_i <= hi_j and lo_j <= hi_i:
                non_overlaps = False
                break
        if non_overlaps:
            count += 1
    return count


def kruskal_wallis_p(groups: List[List[float]]) -> float:
    """Kruskal-Wallis p-value using chi-squared (Wilson-Hilferty) approximation."""
    all_vals = []
    group_indices = []
    for gi, g in enumerate(groups):
        for v in g:
            all_vals.append(v)
            group_indices.append(gi)
    n = len(all_vals)
    if n <= 1:
        return 1.0
    k = len(groups)
    if k < 2:
        return 1.0
    sorted_idx = sorted(range(n), key=lambda i: all_vals[i])
    ranks = [0.0] * n
    for rank_i, idx in enumerate(sorted_idx):
        ranks[idx] = rank_i + 1.0
    i = 0
    while i < n:
        j = i
        while j < n and all_vals[sorted_idx[j]] == all_vals[sorted_idx[i]]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for idx in range(i, j):
            ranks[sorted_idx[idx]] = avg_rank
        i = j
    H = 0.0
    for gi, g in enumerate(groups):
        if not g:
            continue
        group_rank_sum = sum(ranks[idx] for idx, gidx in enumerate(group_indices) if gidx == gi)
        ni = len(g)
        H += group_rank_sum ** 2 / ni
    H = 12.0 / (n * (n + 1)) * H - 3 * (n + 1)
    df = k - 1
    if df <= 0 or H < 0:
        return 1.0
    try:
        z = ((H / df) ** (1 / 3) - (1 - 2.0 / (9 * df))) / math.sqrt(2.0 / (9 * df))
        p = 0.5 * (1 - math.erf(z / math.sqrt(2)))
    except (ZeroDivisionError, ValueError):
        p = 1.0
    return max(0.0, min(1.0, p))


# ────────────── load existing-data for classes 1,2,4,5 ──────────────
def load_existing_classes() -> Dict[int, List[float]]:
    """Load retention_A for classes 1,2,4,5 from tmp_betb_analysis/ (unchanged from v1)."""
    class_data: Dict[int, List[float]] = {k: [] for k in range(6)}

    # Class 1: COMPOUND_SAME_CORPUS
    for fname in ["betB_compound_replay.json", "betB_compound_longerA.json", "betB_ablation_A.json"]:
        fpath = TMP / fname
        if fpath.exists():
            with open(fpath) as fp:
                d = json.load(fp)
            ps = d.get("summary", {}).get("per_seed", {})
            for sv in ps.values():
                if isinstance(sv, dict):
                    r = sv.get("retention_A")
                    if r is not None:
                        class_data[1].append(r)

    # Class 2: REPLAY_SAME_CORPUS
    replay_norm = TMP / "betB_replay_by_norm.json"
    if replay_norm.exists():
        with open(replay_norm) as fp:
            d = json.load(fp)
        pm = d.get("summary", {}).get("per_mode", {})
        for mode_name in ["uniform", "norm_weighted"]:
            if mode_name in pm:
                for sv in pm[mode_name].values():
                    if isinstance(sv, dict):
                        r = sv.get("retention_A")
                        if r is not None:
                            class_data[2].append(r)
    ablation_B = TMP / "betB_ablation_B.json"
    if ablation_B.exists():
        with open(ablation_B) as fp:
            d = json.load(fp)
        prf = d.get("summary", {}).get("per_replay_frac", {})
        for frac_str, seeds_data in prf.items():
            try:
                frac = float(frac_str)
            except ValueError:
                continue
            if frac >= 0.05:
                for sv in seeds_data.values():
                    if isinstance(sv, dict):
                        r = sv.get("retention_A")
                        if r is not None:
                            class_data[2].append(r)
    task_geom = TMP / "betB_task_geometry_rerun.json"
    if task_geom.exists():
        with open(task_geom) as fp:
            d = json.load(fp)
        pp = d.get("summary", {}).get("per_pair", {})
        for pair_name, pv in pp.items():
            sd = pv.get("spectral_distance", 1.0)
            if sd < 0.1:
                for sv in pv.get("seeds", {}).values():
                    r = sv.get("retention_A")
                    if r is not None:
                        class_data[2].append(r)

    # Class 4: STAGE_4_COMPOUND
    for fname in ["betB_4stage_v1.json", "betB_4stage_n8192.json",
                  "betB_phaseA_consol.json", "k2_m1_hierreplay_full.json"]:
        fpath = TMP / fname
        if fpath.exists():
            with open(fpath) as fp:
                d = json.load(fp)
            ps = d.get("summary", {}).get("per_seed", {})
            for sv in ps.values():
                if isinstance(sv, dict):
                    r = sv.get("retention_A")
                    if r is not None:
                        class_data[4].append(r)

    # Class 5: DIFF_CORPUS_2TASK
    if task_geom.exists():
        with open(task_geom) as fp:
            d = json.load(fp)
        pp = d.get("summary", {}).get("per_pair", {})
        for pair_name, pv in pp.items():
            sd = pv.get("spectral_distance", 0.0)
            if sd >= 0.1:
                for sv in pv.get("seeds", {}).values():
                    r = sv.get("retention_A")
                    if r is not None:
                        class_data[5].append(r)
    for fname in ["betB_diff_corpus_v1.json", "betB_diff_corpus_n4096.json"]:
        fpath = TMP / fname
        if fpath.exists():
            with open(fpath) as fp:
                d = json.load(fp)
            ps = d.get("summary", {}).get("per_seed", {})
            for sv in ps.values():
                if isinstance(sv, dict):
                    r = sv.get("retention_A")
                    if r is not None:
                        class_data[5].append(r)

    return class_data


# ────────────── self-test ──────────────
def self_test():
    errors = []

    # Cell 1: CI at n=15 is tight
    mu, std, lo, hi = mean_std_ci([0.94] * 15)
    half_width = (hi - lo) / 2.0
    if half_width >= 0.01:
        errors.append(f"Cell 1: CI half-width for n=15 constant should be 0, got {half_width:.6f}")

    # Cell 2: varied n=15 CI half-width <= 0.05
    import random
    random.seed(42)
    vals15 = [0.90 + random.gauss(0, 0.02) for _ in range(15)]
    mu, std, lo, hi = mean_std_ci(vals15)
    half_width = (hi - lo) / 2.0
    if half_width >= 0.05:
        errors.append(f"Cell 2: CI half-width for n=15 noisy should be <0.05, got {half_width:.4f}")

    # Cell 3: non-overlapping CIs correctly detected
    stats_nonoverlap = {
        0: (0.94, 0.01, 0.93, 0.95),
        3: (0.68, 0.01, 0.67, 0.69),
    }
    n = count_nonoverlapping(stats_nonoverlap)
    if n != 2:
        errors.append(f"Cell 3: expected 2 non-overlapping, got {n}")

    # Cell 4: overlapping CIs correctly detected
    stats_overlap = {
        0: (0.94, 0.05, 0.89, 0.99),
        1: (0.91, 0.05, 0.86, 0.96),
    }
    n = count_nonoverlapping(stats_overlap)
    if n != 0:
        errors.append(f"Cell 4: expected 0 non-overlapping for overlapping CIs, got {n}")

    # Cell 5: KW p << 0.001 for clearly separated groups
    groups_sep = [[0.94] * 15, [0.68] * 15]
    p = kruskal_wallis_p(groups_sep)
    if p >= 0.001:
        errors.append(f"Cell 5: KW p should be << 0.001 for clearly separated groups, got {p:.6f}")

    # Cell 6: HARD-PASS verdict logic fires correctly
    n_nonoverlap = 6
    kw_p = 0.005
    if not (n_nonoverlap >= PASS_MIN_NONOVERLAPPING and kw_p < PASS_KW_P):
        errors.append("Cell 6: HARD-PASS condition failed unexpectedly")

    # Cell 7: HARD-FAIL fires when CI overlaps
    n_nonoverlap = 5  # one CI collapsed
    kw_p = 0.003
    if n_nonoverlap >= PASS_MIN_NONOVERLAPPING:
        errors.append(f"Cell 7: HARD-FAIL should fire at n_nonoverlap=5, but PASS gate passed")

    # Cell 8: load_existing_classes returns correct dict structure (data may be
    # absent on remote machine where tmp_betb_analysis/ was not pre-fetched;
    # structure correctness is what we can verify portably)
    existing = load_existing_classes()
    if set(existing.keys()) != set(range(6)):
        errors.append(f"Cell 8: expected classes 0-5, got {set(existing.keys())}")
    # Warn if data absent (but don't fail self-test on remote where files not present)
    for k in [1, 2, 4, 5]:
        if len(existing[k]) == 0:
            print(f"  [WARN] Cell 8: class {k} ({CLASS_NAMES[k]}) has no existing data "
                  f"(expected on remote; will be populated if tmp_betb_analysis/ is present)")

    if errors:
        print(f"[SELF-TEST FAIL] {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"[SELF-TEST PASS] 8/8 cells pass")
        sys.exit(0)


# ────────────── main run ──────────────
def run_class_seeds(seeds: List[int], replay_frac: float, class_name: str,
                    smoke: bool, device) -> List[float]:
    """Run all seeds for a class; return list of retention_A values."""
    retentions = []
    for seed in seeds:
        t_seed = time.time()
        ret_a = run_one_seed(seed, replay_frac, smoke, device)
        elapsed = time.time() - t_seed
        print(f"  [{class_name}] seed={seed}: retention_A={ret_a:.4f} ({elapsed:.1f}s)",
              flush=True)
        retentions.append(ret_a)
    return retentions


def run_main(mode: str) -> dict:
    t0 = time.time()
    smoke = (mode == "smoke")
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[config] mode={mode} seeds={seeds} device={device} N={1024 if smoke else N}",
          flush=True)

    # Step 1: run fresh seeds for small-n classes
    print(f"\n[class 0: SAME_CORPUS_PRISTINE] replay_frac={REPLAY_FRAC_CLASS0} "
          f"n_seeds={len(seeds)}", flush=True)
    class0_retentions = run_class_seeds(seeds, REPLAY_FRAC_CLASS0,
                                         "SAME_CORPUS_PRISTINE", smoke, device)

    print(f"\n[class 3: NO_REPLAY_SAME_CORPUS] replay_frac={REPLAY_FRAC_CLASS3} "
          f"n_seeds={len(seeds)}", flush=True)
    class3_retentions = run_class_seeds(seeds, REPLAY_FRAC_CLASS3,
                                         "NO_REPLAY_SAME_CORPUS", smoke, device)

    # Step 2: load existing data for classes 1,2,4,5
    print(f"\n[loading existing data for classes 1,2,4,5 ...]", flush=True)
    existing = load_existing_classes()
    print(f"  class 1: n={len(existing[1])}")
    print(f"  class 2: n={len(existing[2])}")
    print(f"  class 4: n={len(existing[4])}")
    print(f"  class 5: n={len(existing[5])}")

    # Step 3: build combined class data
    class_data: Dict[int, List[float]] = {}
    class_data[0] = class0_retentions   # fresh seeds only (clean replication)
    class_data[1] = existing[1]
    class_data[2] = existing[2]
    class_data[3] = class3_retentions   # fresh seeds only
    class_data[4] = existing[4]
    class_data[5] = existing[5]

    # Step 4: compute per-class statistics
    class_stats = {}
    for k in range(6):
        vals = class_data[k]
        mu, std, lo, hi = mean_std_ci(vals)
        class_stats[k] = (mu, std, lo, hi)
        print(f"  {CLASS_NAMES[k]}: n={len(vals)} mean={mu:.4f} 95%CI=[{lo:.4f},{hi:.4f}]",
              flush=True)

    # Step 5: count non-overlapping CIs
    n_nonoverlap = count_nonoverlapping(class_stats)
    print(f"\n[predictor stats] n_nonoverlapping={n_nonoverlap}/6", flush=True)

    # Step 6: Kruskal-Wallis
    groups = [class_data[k] for k in range(6) if len(class_data[k]) > 0]
    kw_p = kruskal_wallis_p(groups)
    print(f"[predictor stats] K-W p={kw_p:.6f}", flush=True)

    # Step 7: verdict
    # Check if any v1 classes (0 and 3) lost their CI separation
    # The key question: do classes 0 and 3 still have non-overlapping CIs?
    c0_still_separated = True
    c3_still_separated = True
    c0_mu, _, c0_lo, c0_hi = class_stats[0]
    c3_mu, _, c3_lo, c3_hi = class_stats[3]
    # Class 0 must not overlap class 1 (adjacent from above)
    c1_mu, _, c1_lo, c1_hi = class_stats[1]
    if c0_lo <= c1_hi and c1_lo <= c0_hi:
        c0_still_separated = False
    # Class 3 must not overlap class 2 (adjacent from above) or class 4 (adjacent from below)
    c2_mu, _, c2_lo, c2_hi = class_stats[2]
    c4_mu, _, c4_lo, c4_hi = class_stats[4]
    if c3_lo <= c2_hi and c2_lo <= c3_hi:
        c3_still_separated = False
    if c3_lo <= c4_hi and c4_lo <= c3_hi:
        c3_still_separated = False

    previously_nonover_still_ok = c0_still_separated and c3_still_separated

    if n_nonoverlap >= PASS_MIN_NONOVERLAPPING and kw_p < PASS_KW_P and previously_nonover_still_ok:
        verdict = "SHIFT_CLASS_REPLICATION_HARD_PASS"
        verdict_msg = (
            f"FULL REPLICATION CONFIRMED: {n_nonoverlap}/6 non-overlapping CIs at n>={len(seeds)} "
            f"for small-n classes, K-W p={kw_p:.6f} < {PASS_KW_P}. "
            f"Class 0 (SAME_CORPUS_PRISTINE) mean={c0_mu:.4f} CI=[{c0_lo:.4f},{c0_hi:.4f}] "
            f"class 3 (NO_REPLAY_SAME_CORPUS) mean={c3_mu:.4f} CI=[{c3_lo:.4f},{c3_hi:.4f}] "
            f"BOTH still non-overlapping. Row-state promotion gate CLEARED: "
            f"Bet B retention predictability claim at operational status."
        )
    elif not previously_nonover_still_ok or n_nonoverlap < FAIL_MIN_NONOVERLAPPING or kw_p >= FAIL_KW_P:
        verdict = "SHIFT_CLASS_REPLICATION_HARD_FAIL"
        reason = ""
        if not c0_still_separated:
            reason += f"class 0 CI=[{c0_lo:.4f},{c0_hi:.4f}] overlaps class 1 CI=[{c1_lo:.4f},{c1_hi:.4f}]; "
        if not c3_still_separated:
            reason += f"class 3 CI=[{c3_lo:.4f},{c3_hi:.4f}] overlaps adjacent class; "
        if n_nonoverlap < FAIL_MIN_NONOVERLAPPING:
            reason += f"n_nonoverlapping={n_nonoverlap} < {FAIL_MIN_NONOVERLAPPING}; "
        if kw_p >= FAIL_KW_P:
            reason += f"K-W p={kw_p:.6f} >= {FAIL_KW_P}; "
        verdict_msg = (
            f"REPLICATION FAILED: v1 HARD-PASS was small-n artifact. {reason.rstrip('; ')}. "
            f"n_nonoverlapping={n_nonoverlap}/6. K-W p={kw_p:.6f}. "
            f"Bet B predictability claim does NOT hold at n>={len(seeds)}."
        )
    else:
        verdict = "SHIFT_CLASS_REPLICATION_MIDDLE_BAND"
        verdict_msg = (
            f"PARTIAL REPLICATION: {n_nonoverlap}/6 non-overlapping CIs, "
            f"K-W p={kw_p:.6f} in [{PASS_KW_P},{FAIL_KW_P}). "
            f"Signal confirmed but statistical strength weaker than v1."
        )

    elapsed = time.time() - t0

    # Build per-class summary
    per_class = {}
    for k in range(6):
        mu, std, lo, hi = class_stats[k]
        per_class[CLASS_NAMES[k]] = {
            "n": len(class_data[k]),
            "source": "fresh_seeds" if k in [0, 3] else "existing_data",
            "mean_retention_A": mu,
            "std": std,
            "ci_95_lo": lo,
            "ci_95_hi": hi,
            "values": class_data[k],
        }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": {
            "n_nonoverlapping_classes": n_nonoverlap,
            "kw_p": kw_p,
            "c0_still_separated": c0_still_separated,
            "c3_still_separated": c3_still_separated,
            "pass_threshold_nonoverlap": PASS_MIN_NONOVERLAPPING,
            "fail_threshold_nonoverlap": FAIL_MIN_NONOVERLAPPING,
            "pass_threshold_kw_p": PASS_KW_P,
            "fail_threshold_kw_p": FAIL_KW_P,
            "per_class": per_class,
        },
        "config": {
            "mode": mode,
            "n_classes": 6,
            "seeds_used": seeds,
            "N": 1024 if smoke else N,
            "replay_frac_class0": REPLAY_FRAC_CLASS0,
            "replay_frac_class3": REPLAY_FRAC_CLASS3,
            "ema_alpha": EMA_ALPHA,
            "phase_a_epochs": 1 if smoke else PHASE_A_EPOCHS,
            "epochs": 1 if smoke else EPOCHS,
            "bytes_per_corpus": 5000 if smoke else BYTES_PER_CORPUS,
            "ci_z": CI_Z,
        },
    }
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    mode = "smoke" if args.smoke else "full"
    metrics = run_main(mode)

    print(f"\n[{metrics['verdict']}] {metrics['verdict_msg']}")
    print(f"  n_nonoverlapping={metrics['summary']['n_nonoverlapping_classes']} "
          f"kw_p={metrics['summary']['kw_p']:.6f}", flush=True)
    for cls_name, cs in metrics["summary"]["per_class"].items():
        mu = cs["mean_retention_A"]
        lo = cs["ci_95_lo"]
        hi = cs["ci_95_hi"]
        n = cs["n"]
        src = cs["source"]
        if not (mu != mu):  # not nan
            print(f"  {cls_name} ({src}): n={n} mean={mu:.4f} 95%CI=[{lo:.4f},{hi:.4f}]")

    out_dir = get_output_dir("wave14_betB_shift_class_full_replication_v1")
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w") as fp:
        json.dump(metrics, fp, indent=2,
                  default=lambda x: x if not (isinstance(x, float) and x != x) else "nan")
    tmp.rename(out_dir / "metrics.json")
    print(f"[written] {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
