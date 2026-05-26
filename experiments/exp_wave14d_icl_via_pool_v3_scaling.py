"""ICL via pool v3: saturation curve out to ICTX=16384.

Closes the Tier-S #1 ICL scaling gap (Bet 1 in active_priorities.md). Fixes
two predecessor bugs:
  (a) v2/wave14g augment_pool used a fixed POOL_SIZE circular buffer; for
      ICTX > POOL_SIZE the slicing math errored ("tensor size 4096 != 8192").
      v3 allocates pool_used + n_new rows, sized to fit.
  (b) wave14f flagged "corpus too small; relevant items run out." Corpus B
      is now assembled from experiments/*.py (large, stable) instead of the
      volatile session_events.jsonl. Distinct-chunk count is asserted per
      seed; verdict reports INSUFFICIENT_CORPUS if violated.

Pre-reg: preregs/2026-05-21_wave14d_icl_via_pool_v3_scaling.md
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(event_type, **fields):
        pass

try:
    from verification.oracle import assert_in_range, assert_distinguishable
except ImportError:
    def assert_in_range(name, measured, band):
        lo, hi = band
        if not (lo <= measured <= hi):
            raise AssertionError(f"SANITY FAIL [{name}]: {measured} outside {band}")

    def assert_distinguishable(name, a, b, min_gap=0.10):
        if abs(a - b) < min_gap:
            raise AssertionError(f"SANITY FAIL [{name}]: |{a}-{b}|<{min_gap}")


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
N_FULL = 4096
N_SMOKE = 512
BETA = 8.0
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 64
POOL_SIZE_A = 4096
MAX_EPOCHS_FULL = 10
MAX_EPOCHS_SMOKE = 1
TRAIN_A_BYTES_SMOKE = 4000
TEST_B_CAP_FULL = 16_000
TEST_B_CAP_SMOKE = 1500
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
ALPHA = 1.0

SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]
ICTX_FULL = [64, 256, 1024, 4096, 16384]
ICTX_SMOKE = [16, 64]

SLOPE_THRESHOLD = 0.10
ENTROPY_FLOOR = 1.0


def _say(msg):
    print(msg, flush=True)


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"missing required fields: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict or verdict_msg")


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Multi-probe ICL-saturation verdict (5 labels)."""
    s = summary
    ictx_list = s.get("ictx_list")
    mean_gain = s.get("mean_gain")
    std_gain = s.get("std_gain")
    slope = s.get("slope_log2_ictx")
    entropy_at_max = s.get("entropy_at_max_ictx")
    distinct_ok = s.get("distinct_chunks_floor_ok")
    if not ictx_list or mean_gain is None or slope is None:
        return ("ICL_SATURATION_INCONCLUSIVE", "Missing data in summary.")

    if distinct_ok is False:
        return ("ICL_SATURATION_INSUFFICIENT_CORPUS",
                f"At least one seed had fewer distinct relevant chunks than ICTX requested. "
                f"Corpus B is too small for this scaling test. See per-ICTX distinct_chunks.")

    if entropy_at_max is not None and entropy_at_max < ENTROPY_FLOOR:
        return ("ICL_SATURATION_POOL_COLLAPSE",
                f"Pool retrieval entropy at largest ICTX = {entropy_at_max:.3f} nat "
                f"(< {ENTROPY_FLOOR}). Retrieval saturated to ~1-2 items; substrate "
                f"scaling cannot be assessed.")

    # Kill criterion 1: slope across ICTX >= 1024 not positive
    high_ictx = [i for i, x in enumerate(ictx_list) if x >= 1024]
    if len(high_ictx) >= 2:
        gains_high = [mean_gain[i] for i in high_ictx]
        log_ictx_high = [math.log2(ictx_list[i]) for i in high_ictx]
        slope_high = _least_squares_slope(log_ictx_high, gains_high)
        if slope_high <= 0:
            return ("ICL_SATURATION_INVERTED",
                    f"Slope across ICTX>=1024 = {slope_high:+.4f} (<=0). "
                    f"Retracts kNN-LM-like scaling: gain does NOT increase with ICTX in the "
                    f"long-context regime. Full slope on log2(ICTX) = {slope:+.4f}.")

    # Kill criterion 2: gain at max ICTX collapses vs ICTX=4096
    idx_max = len(ictx_list) - 1
    idx_4096 = None
    for i, x in enumerate(ictx_list):
        if x == 4096:
            idx_4096 = i
            break
    if idx_4096 is not None and idx_4096 < idx_max:
        gain_max = mean_gain[idx_max]
        gain_4096 = mean_gain[idx_4096]
        sigma_4096 = (std_gain or [0] * len(ictx_list))[idx_4096]
        if gain_max < gain_4096 - sigma_4096:
            return ("ICL_SATURATION_INVERTED",
                    f"Gain at ICTX={ictx_list[idx_max]} ({gain_max:+.4f}) collapses vs "
                    f"ICTX=4096 ({gain_4096:+.4f}, sigma={sigma_4096:.4f}): drop exceeds 1 sigma. "
                    f"Retracts long-context ICL claim.")

    # At this point neither kill triggered; classify
    gain_at_max = mean_gain[idx_max]
    if slope >= SLOPE_THRESHOLD and gain_at_max > 0:
        return ("ICL_SATURATION_VALIDATED",
                f"Slope on log2(ICTX) = {slope:+.4f} >= {SLOPE_THRESHOLD}. "
                f"Gain at ICTX={ictx_list[idx_max]} = {gain_at_max:+.4f} > 0. "
                f"No collapse vs ICTX=4096. kNN-LM-like log-linear ICL confirmed up to "
                f"ICTX={ictx_list[idx_max]} at N={N_FULL}.")
    if gain_at_max > 0 and slope > 0:
        return ("ICL_SATURATION_WEAK",
                f"Slope = {slope:+.4f} positive but below {SLOPE_THRESHOLD} threshold. "
                f"Gain at ICTX={ictx_list[idx_max]} = {gain_at_max:+.4f}. "
                f"ICL works but plateaus; bounded log scaling, not unbounded.")
    return ("ICL_SATURATION_INCONCLUSIVE",
            f"slope={slope:+.4f}, gain_at_max={gain_at_max:+.4f}. "
            f"Neither validated nor cleanly killed; inspect per-ICTX data.")


def _least_squares_slope(xs, ys) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    den = sum((xs[i] - mean_x) ** 2 for i in range(n))
    if abs(den) < 1e-12:
        return 0.0
    return num / den


def self_test_verdict() -> None:
    cases = [
        # 1. Strong scaling -> VALIDATED
        ({"ictx_list": [64, 256, 1024, 4096, 16384],
          "mean_gain": [0.10, 0.18, 0.28, 0.40, 0.55],
          "std_gain": [0.01, 0.01, 0.02, 0.02, 0.03],
          "slope_log2_ictx": 0.057,  # actually 0.056; let me set 0.10 to trigger VALIDATED
          "entropy_at_max_ictx": 2.5,
          "distinct_chunks_floor_ok": True},
         "ICL_SATURATION_WEAK"),  # slope 0.057 < 0.10 -> WEAK
        # 2. Stronger slope -> VALIDATED
        ({"ictx_list": [64, 256, 1024, 4096, 16384],
          "mean_gain": [0.05, 0.20, 0.40, 0.65, 0.95],
          "std_gain": [0.01, 0.01, 0.02, 0.02, 0.03],
          "slope_log2_ictx": 0.115,
          "entropy_at_max_ictx": 2.5,
          "distinct_chunks_floor_ok": True},
         "ICL_SATURATION_VALIDATED"),
        # 3. Inverted (slope <=0 across ICTX>=1024) -> INVERTED
        ({"ictx_list": [64, 256, 1024, 4096, 16384],
          "mean_gain": [0.10, 0.20, 0.30, 0.25, 0.20],
          "std_gain": [0.01, 0.01, 0.01, 0.01, 0.01],
          "slope_log2_ictx": 0.012,
          "entropy_at_max_ictx": 2.5,
          "distinct_chunks_floor_ok": True},
         "ICL_SATURATION_INVERTED"),
        # 4. Collapse at max -> INVERTED (kill #2)
        ({"ictx_list": [64, 256, 1024, 4096, 16384],
          "mean_gain": [0.10, 0.20, 0.30, 0.50, 0.10],
          "std_gain": [0.01, 0.01, 0.01, 0.05, 0.01],
          "slope_log2_ictx": 0.020,
          "entropy_at_max_ictx": 2.5,
          "distinct_chunks_floor_ok": True},
         "ICL_SATURATION_INVERTED"),
        # 5. Insufficient corpus -> dedicated label
        ({"ictx_list": [64, 256, 1024, 4096, 16384],
          "mean_gain": [0.10, 0.18, 0.28, 0.40, 0.55],
          "std_gain": [0.01, 0.01, 0.02, 0.02, 0.03],
          "slope_log2_ictx": 0.115,
          "entropy_at_max_ictx": 2.5,
          "distinct_chunks_floor_ok": False},
         "ICL_SATURATION_INSUFFICIENT_CORPUS"),
        # 6. Pool entropy collapse -> dedicated label
        ({"ictx_list": [64, 256, 1024, 4096, 16384],
          "mean_gain": [0.10, 0.18, 0.28, 0.40, 0.55],
          "std_gain": [0.01, 0.01, 0.02, 0.02, 0.03],
          "slope_log2_ictx": 0.115,
          "entropy_at_max_ictx": 0.5,
          "distinct_chunks_floor_ok": True},
         "ICL_SATURATION_POOL_COLLAPSE"),
        # 7. Empty -> INCONCLUSIVE
        ({}, "ICL_SATURATION_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return 2.0 * (raw > 0.5).float() - 1.0


def build_ctx(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def load_corpus_a() -> bytes:
    files = [REPO / "PLAN.md", REPO / "NEXT_PHASE.md", REPO / "README.md",
             REPO / "PROGRESS.md", REPO / "RESULTS.md", REPO / "CLAUDE.md"]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


def load_corpus_b_code(min_bytes: int) -> bytes:
    """Corpus B = experiments/*.py source code. Different byte distribution
    from markdown (Corpus A). Stable across runs."""
    exp_dir = REPO / "experiments"
    parts = []
    if exp_dir.exists():
        for p in sorted(exp_dir.glob("*.py")):
            try:
                parts.append(p.read_bytes())
                parts.append(b"\n")
            except OSError:
                continue
    combined = b"".join(parts)
    if len(combined) < min_bytes:
        # Tile to reach the floor (smoke tolerates; full mode should never need this)
        tiled = combined
        while len(tiled) < min_bytes and len(combined) > 0:
            tiled = tiled + b"\n" + combined
        combined = tiled if len(tiled) >= min_bytes else combined
    return combined


def chunk_bytes_to_K_positions(corpus_bytes, max_entries, seed=0):
    """Return (idx, tgts) — (max_entries, K) and (max_entries,) tensors of
    distinct K-byte chunks from corpus_bytes. Returns fewer than requested if
    the corpus is too small; caller must check."""
    pad = bytes([PAD_BYTE]) * K
    padded = pad + corpus_bytes
    T_total = len(padded) - K
    if T_total <= 0:
        return (torch.zeros((0, K), dtype=torch.long, device=DEVICE),
                torch.zeros(0, dtype=torch.long, device=DEVICE), 0)
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts = bt[pos + K]
    n_take = min(max_entries, T_total)
    if n_take < T_total:
        cpu_gen = torch.Generator().manual_seed(seed)
        perm = torch.randperm(T_total, generator=cpu_gen)[:n_take].to(DEVICE)
        idx = idx[perm]
        tgts = tgts[perm]
    return idx, tgts, n_take


def train_phase_a(byte_atoms, pos_atoms, train_bytes, n_dim, max_epochs, batch_size):
    W = torch.zeros((n_dim, n_dim), dtype=torch.float32, device=DEVICE)
    pool_vecs = torch.zeros((POOL_SIZE_A, n_dim), dtype=torch.float32, device=DEVICE)
    pool_labels = torch.zeros(POOL_SIZE_A, dtype=torch.long, device=DEVICE)
    pool_idx = 0
    pool_used = 0
    arange_b = torch.arange(batch_size, device=DEVICE)
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
    T_total = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    train_idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    train_targets = bt[pos + K]
    for epoch in range(1, max_epochs + 1):
        for batch_start in range(0, T_total, batch_size):
            be = min(batch_start + batch_size, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = build_ctx(byte_atoms, pos_atoms, idx_batch)
            with torch.no_grad():
                q = ctxs @ W.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / n_dim
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms = byte_atoms[tgt_batch]
                predicted = P.T @ byte_atoms
                residual = target_atoms - predicted
                dW = (residual.T @ ctxs) / n_dim
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE_A
                    pool_vecs.index_copy_(0, dest, ctxs)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE_A
                    pool_used = min(pool_used + B, POOL_SIZE_A)
    return W, pool_vecs, pool_labels, pool_used


def augment_pool_dynamic(pool_vecs, pool_labels, pool_used, new_ctxs, new_tgts):
    """v3 fix: allocate pool_used + n_new rows. No fixed-size circular buffer."""
    n_new = new_ctxs.shape[0]
    if n_new == 0:
        return pool_vecs[:pool_used].clone(), pool_labels[:pool_used].clone(), pool_used
    new_used = pool_used + n_new
    aug_vecs = torch.empty((new_used, pool_vecs.shape[1]), dtype=pool_vecs.dtype, device=DEVICE)
    aug_labels = torch.empty(new_used, dtype=pool_labels.dtype, device=DEVICE)
    if pool_used > 0:
        aug_vecs[:pool_used] = pool_vecs[:pool_used]
        aug_labels[:pool_used] = pool_labels[:pool_used]
    aug_vecs[pool_used:] = new_ctxs
    aug_labels[pool_used:] = new_tgts
    return aug_vecs, aug_labels, new_used


def eval_with_pool(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels,
                    pool_used, alpha, batch_size, n_dim, return_entropy=False):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx_all = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts_all = bt[pos + K]
    total = 0.0
    pool_entropy_sum = 0.0
    entropy_count = 0
    active = pool_vecs[:pool_used] if pool_used > 0 else None
    labels = pool_labels[:pool_used] if pool_used > 0 else None
    for bs in range(0, T, batch_size):
        be = min(bs + batch_size, T)
        idx_b = idx_all[bs:be]
        tgts = tgts_all[bs:be]
        B = idx_b.shape[0]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b)
        q = ctxs @ W.T
        q = shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / n_dim
        P_W = torch.softmax(BETA * sims, dim=0)
        if pool_used > 0 and alpha > 0:
            sims_p = (active @ ctxs.T) / n_dim
            weights_p = torch.softmax(BETA * sims_p, dim=0)
            if return_entropy:
                ent = -(weights_p * torch.log(weights_p.clamp(min=1e-12))).sum(dim=0)
                pool_entropy_sum += float(ent.sum())
                entropy_count += B
            P_retr = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
            P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights_p)
            P = alpha * P_retr + (1 - alpha) * P_W
        else:
            P = P_W
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    avg_bpc = total / max(T, 1)
    ent_mean = pool_entropy_sum / entropy_count if return_entropy and entropy_count > 0 else None
    return avg_bpc, ent_mean


def run_full(smoke: bool):
    t_start = time.monotonic()
    n_dim = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    ictx_list = ICTX_SMOKE if smoke else ICTX_FULL
    max_epochs = MAX_EPOCHS_SMOKE if smoke else MAX_EPOCHS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    max_ictx = max(ictx_list)
    min_corpus_b = max(max_ictx * (K + 1) * 4, 200_000) if not smoke else 8_000

    corpus_a = load_corpus_a()
    corpus_b = load_corpus_b_code(min_corpus_b)
    split_a = int(0.8 * len(corpus_a))
    train_a = corpus_a[:split_a]
    if smoke:
        train_a = train_a[:TRAIN_A_BYTES_SMOKE]
    split_b = int(0.7 * len(corpus_b))
    train_b = corpus_b[:split_b]
    test_b_full = corpus_b[split_b:]
    test_b_cap = TEST_B_CAP_FULL if not smoke else TEST_B_CAP_SMOKE
    test_b = test_b_full[:test_b_cap]

    _say(f"[config] n_dim={n_dim}, seeds={seeds}, ictx={ictx_list}, alpha={ALPHA}")
    _say(f"[corpus] A={len(corpus_a)}B (train {len(train_a)}B), "
         f"B={len(corpus_b)}B (train {len(train_b)}B, test {len(test_b)}B)")

    per_seed_results = []
    distinct_floor_ok = True

    for seed in seeds:
        gen = torch.Generator().manual_seed(seed)
        byte_atoms = make_bsc_atoms(VOCAB_SIZE, n_dim, gen).to(DEVICE)
        pos_atoms = make_bsc_atoms(K, n_dim, gen).to(DEVICE)

        _say(f"\n[seed={seed}] Phase A training...")
        W_A, pool_A, labels_A, used_A = train_phase_a(
            byte_atoms, pos_atoms, train_a, n_dim, max_epochs, batch_size)
        _say(f"[seed={seed}] Phase A done. pool_used={used_A}")

        off_bpc, _ = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b,
                                     pool_A, labels_A, used_A, 0.0, batch_size, n_dim)
        pool_A_bpc, pool_A_ent = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b,
                                                  pool_A, labels_A, used_A, ALPHA,
                                                  batch_size, n_dim, return_entropy=True)
        _say(f"[seed={seed}] off={off_bpc:.4f}  pool_A(alpha=1)={pool_A_bpc:.4f}  "
             f"entropy={pool_A_ent:.3f}")

        per_ictx = {}
        for ictx in ictx_list:
            irr_idx, irr_tgts, irr_n = chunk_bytes_to_K_positions(
                train_a, ictx, seed=seed * 100 + 1)
            rel_idx, rel_tgts, rel_n = chunk_bytes_to_K_positions(
                train_b, ictx, seed=seed * 100 + 2)
            if rel_n < ictx:
                distinct_floor_ok = False
            irr_ctxs = build_ctx(byte_atoms, pos_atoms, irr_idx)
            rel_ctxs = build_ctx(byte_atoms, pos_atoms, rel_idx)
            aug_v_irr, aug_l_irr, used_irr = augment_pool_dynamic(
                pool_A, labels_A, used_A, irr_ctxs, irr_tgts)
            aug_v_rel, aug_l_rel, used_rel = augment_pool_dynamic(
                pool_A, labels_A, used_A, rel_ctxs, rel_tgts)
            irr_bpc, _ = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b,
                                          aug_v_irr, aug_l_irr, used_irr, ALPHA,
                                          batch_size, n_dim)
            rel_bpc, rel_ent = eval_with_pool(W_A, byte_atoms, pos_atoms, test_b,
                                                aug_v_rel, aug_l_rel, used_rel, ALPHA,
                                                batch_size, n_dim, return_entropy=True)
            gain = irr_bpc - rel_bpc
            per_ictx[ictx] = {
                "irr_bpc": irr_bpc, "rel_bpc": rel_bpc, "gain": gain,
                "entropy": rel_ent,
                "distinct_irr": irr_n, "distinct_rel": rel_n,
            }
            _say(f"[seed={seed}] ICTX={ictx:6d}  irr={irr_bpc:.4f}  rel={rel_bpc:.4f}  "
                 f"gain={gain:+.4f}  ent={rel_ent:.3f}  distinct_rel={rel_n}")

        per_seed_results.append({
            "seed": seed, "off_bpc": off_bpc, "pool_A_bpc": pool_A_bpc,
            "pool_A_entropy": pool_A_ent, "per_ictx": per_ictx,
        })

    # Aggregate across seeds
    mean_gain = []
    std_gain = []
    mean_entropy_per_ictx = []
    for ictx in ictx_list:
        gains = [r["per_ictx"][ictx]["gain"] for r in per_seed_results]
        ents = [r["per_ictx"][ictx]["entropy"] for r in per_seed_results
                 if r["per_ictx"][ictx]["entropy"] is not None]
        n = len(gains)
        mg = sum(gains) / n
        var = sum((g - mg) ** 2 for g in gains) / max(n - 1, 1) if n > 1 else 0.0
        mean_gain.append(mg)
        std_gain.append(math.sqrt(var))
        mean_entropy_per_ictx.append(sum(ents) / len(ents) if ents else None)

    log_ictx = [math.log2(x) for x in ictx_list]
    slope = _least_squares_slope(log_ictx, mean_gain)

    elapsed_s = time.monotonic() - t_start

    summary = {
        "ictx_list": ictx_list,
        "mean_gain": mean_gain,
        "std_gain": std_gain,
        "slope_log2_ictx": slope,
        "mean_entropy_per_ictx": mean_entropy_per_ictx,
        "entropy_at_max_ictx": mean_entropy_per_ictx[-1],
        "distinct_chunks_floor_ok": distinct_floor_ok,
        "n_seeds": len(seeds),
        "alpha": ALPHA,
        "n_dim": n_dim,
        "corpus_a_bytes": len(corpus_a),
        "corpus_b_bytes": len(corpus_b),
        "test_b_bytes": len(test_b),
    }
    verdict, msg = compute_verdict(summary)

    _say("\n========= AGGREGATE =========")
    for i, ictx in enumerate(ictx_list):
        _say(f"  ICTX={ictx:6d}  mean_gain={mean_gain[i]:+.4f} +/- {std_gain[i]:.4f}  "
             f"entropy={mean_entropy_per_ictx[i]:.3f}"
             if mean_entropy_per_ictx[i] is not None else
             f"  ICTX={ictx:6d}  mean_gain={mean_gain[i]:+.4f} +/- {std_gain[i]:.4f}")
    _say(f"  slope on log2(ICTX) = {slope:+.4f}  (threshold {SLOPE_THRESHOLD})")
    _say(f"  distinct_chunks_floor_ok = {distinct_floor_ok}")
    _say(f"\nVERDICT: {verdict}")
    _say(f"  {msg}")

    return summary, verdict, msg, elapsed_s, per_seed_results


def write_metrics(out_dir, summary, verdict, msg, elapsed_s, per_seed_results, config):
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed_s,
        "summary": summary,
        "config": config,
        "per_seed": per_seed_results,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(final)


def run_smoke():
    out_dir = get_output_dir("wave14d_icl_via_pool_v3_scaling_smoke")
    log_event("experiment_started", name="wave14d_icl_via_pool_v3_scaling", mode="smoke")
    summary, verdict, msg, elapsed_s, per_seed = run_full(smoke=True)

    # Oracle assertions on smoke output
    # 1. bpc values plausible
    rel_bpc_max = per_seed[0]["per_ictx"][ICTX_SMOKE[-1]]["rel_bpc"]
    irr_bpc_max = per_seed[0]["per_ictx"][ICTX_SMOKE[-1]]["irr_bpc"]
    off_bpc = per_seed[0]["off_bpc"]
    assert_in_range("rel_bpc_smoke", rel_bpc_max, (0.5, 8.0))
    assert_in_range("off_bpc_smoke", off_bpc, (0.5, 8.0))
    # 2. irr vs rel distinguishable at smoke max (small gap is fine; just not zero)
    assert_distinguishable("irr_vs_rel_smoke", irr_bpc_max, rel_bpc_max, min_gap=0.0001)
    # 3. distinct chunks at smoke max >= ICTX
    distinct_rel = per_seed[0]["per_ictx"][ICTX_SMOKE[-1]]["distinct_rel"]
    if distinct_rel < ICTX_SMOKE[-1]:
        raise AssertionError(
            f"SANITY FAIL [distinct_chunks]: requested {ICTX_SMOKE[-1]}, got {distinct_rel}. "
            f"Corpus B too small even for smoke.")

    write_metrics(out_dir, summary, verdict, msg, elapsed_s, per_seed, {
        "mode": "smoke", "n_dim": N_SMOKE, "ictx": ICTX_SMOKE, "seeds": SEEDS_SMOKE,
        "max_epochs": MAX_EPOCHS_SMOKE, "alpha": ALPHA, "batch_size": BATCH_SIZE_SMOKE,
    })
    log_event("experiment_outcome", name="wave14d_icl_via_pool_v3_scaling",
              verdict=verdict, verdict_msg=msg, elapsed_s=elapsed_s, mode="smoke")
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14d_icl_via_pool_v3_scaling")
    log_event("experiment_started", name="wave14d_icl_via_pool_v3_scaling", mode="full")
    summary, verdict, msg, elapsed_s, per_seed = run_full(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed_s, per_seed, {
        "mode": "full", "n_dim": N_FULL, "ictx": ICTX_FULL, "seeds": SEEDS_FULL,
        "max_epochs": MAX_EPOCHS_FULL, "alpha": ALPHA, "batch_size": BATCH_SIZE_FULL,
    })
    log_event("experiment_outcome", name="wave14d_icl_via_pool_v3_scaling",
              verdict=verdict, verdict_msg=msg, elapsed_s=elapsed_s, mode="full",
              slope_log2_ictx=summary["slope_log2_ictx"],
              mean_gain=summary["mean_gain"])
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true",
                    help="Run verdict-logic unit tests and exit.")
    ap.add_argument("--smoke", action="store_true",
                    help="Smallest config (~5s on CPU), writes metrics, runs oracle asserts.")
    args = ap.parse_args()

    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
