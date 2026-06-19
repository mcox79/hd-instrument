"""Spin glass E1: empirically localize substrate in RS vs RSB phase.

Per wave14e2_spin_glass_substrate_research:
- Single-peaked Parisi P(q) + chance-level ultrametricity = pure RS phase
  => substrate has ~350K bundle headroom; use Frady-Sommer as theory.
- Multi-peaked P(q) + ultrametricity > 0.3 = RSB hierarchy
  => substrate has emergent O(log P) tree-walk retrieval index for free.

Either outcome is decisive and shapes the substrate's enabling capabilities.
10-min CPU experiment. Dumps existing pool, computes:
  q (Edwards-Anderson overlap) histogram
  ultrametricity fraction over 10K triples
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

DEVICE = torch.device("cpu")
N = 4096
K = 4
VOCAB_SIZE = 256
PAD_BYTE = 0
POOL_SIZE = 1024
BATCH_SIZE = 64
MAX_EPOCHS = 15
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
BETA = 8.0
NUM_TRIPLES = 10000
SEED = 17


def _say(m): print(m, flush=True)


def load_corpus_a():
    repo = Path(__file__).resolve().parent.parent
    files = [repo / "PLAN.md", repo / "NEXT_PHASE.md", repo / "README.md",
             repo / "PROGRESS.md", repo / "RESULTS.md", repo / "CLAUDE.md"]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes()); parts.append(b"\n\n")
    return b"".join(parts)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def build_ctx_batch(byte_atoms, pos_atoms, idx):
    b = byte_atoms[idx] * pos_atoms.unsqueeze(0)
    s = b.sum(dim=1)
    out = torch.sign(s)
    return torch.where(out == 0, torch.ones_like(out), out)


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def build_pool(byte_atoms, pos_atoms, train_bytes):
    """Train W via delta rule (we throw it away) but harvest pool bundles."""
    W = torch.zeros((N, N), device=DEVICE)
    pool_v = torch.zeros((POOL_SIZE, N), device=DEVICE)
    pool_l = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    p_idx, p_used = 0, 0
    arange = torch.arange(BATCH_SIZE, device=DEVICE)
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offs = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offs.unsqueeze(0)]
    tgt = bt[pos + K]
    for epoch in range(1, MAX_EPOCHS + 1):
        for bs in range(0, T, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T)
            B = be - bs
            ctxs = build_ctx_batch(byte_atoms, pos_atoms, idx[bs:be])
            t = tgt[bs:be]
            with torch.no_grad():
                q = shifted_relu(ctxs @ W.T, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                resid = byte_atoms[t] - (P.T @ byte_atoms)
                dW = (resid.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY); W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if epoch == 1:
                    dest = (p_idx + arange[:B]) % POOL_SIZE
                    pool_v.index_copy_(0, dest, ctxs)
                    pool_l.index_copy_(0, dest, t)
                    p_idx = (p_idx + B) % POOL_SIZE
                    p_used = min(p_used + B, POOL_SIZE)
    return pool_v[:p_used]


def edwards_anderson_overlap_distribution(pool):
    """Compute pairwise overlap matrix Q[i,j] = (1/N) sum_k pool[i,k] * pool[j,k]."""
    P = pool.shape[0]
    Q = (pool @ pool.T) / N  # (P, P)
    # Extract upper triangle (excluding diagonal)
    mask = torch.triu(torch.ones(P, P, dtype=torch.bool), diagonal=1)
    return Q[mask]


def ultrametricity_fraction(pool, num_triples, gen):
    """For random triples (i,j,k), check if max(q_ij, q_jk, q_ik) - median(...) < epsilon.
    Ultrametric: the two largest overlaps in a triple are EQUAL (an isoceles triangle in q-space)."""
    P = pool.shape[0]
    sat = 0
    epsilon = 0.01  # tolerance for "equal" two largest overlaps
    for _ in range(num_triples):
        idxs = torch.randperm(P, generator=gen)[:3]
        i, j, k = int(idxs[0]), int(idxs[1]), int(idxs[2])
        q_ij = float((pool[i] @ pool[j]) / N)
        q_jk = float((pool[j] @ pool[k]) / N)
        q_ik = float((pool[i] @ pool[k]) / N)
        vals = sorted([q_ij, q_jk, q_ik], reverse=True)
        if abs(vals[0] - vals[1]) < epsilon:
            sat += 1
    return sat / num_triples


def histogram_peaks(values, num_bins=40):
    """Detect peaks in histogram. Returns (bin_centers, counts, peak_count)."""
    vmin, vmax = float(values.min()), float(values.max())
    bins = torch.linspace(vmin, vmax, num_bins + 1)
    counts = torch.histc(values, bins=num_bins, min=vmin, max=vmax)
    centers = (bins[:-1] + bins[1:]) / 2
    # Find local maxima (must beat both neighbors AND be > 5% of max)
    threshold = float(counts.max()) * 0.1
    peaks = []
    for i in range(1, num_bins - 1):
        if counts[i] > counts[i-1] and counts[i] > counts[i+1] and counts[i] > threshold:
            peaks.append((float(centers[i]), float(counts[i])))
    return centers, counts, peaks


def main():
    _say(f"Spin glass E1: Parisi P(q) + ultrametricity on N={N}, K={K}, POOL_SIZE={POOL_SIZE}")
    corpus = load_corpus_a()
    split = int(0.8 * len(corpus))
    train_a = corpus[:split]
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc(K, N, gen).to(DEVICE)
    _say(f"  Training to harvest pool...")
    pool = build_pool(byte_atoms, pos_atoms, train_a)
    _say(f"  Pool size: {pool.shape[0]}")

    # Edwards-Anderson overlap distribution
    overlaps = edwards_anderson_overlap_distribution(pool)
    _say(f"\n  Overlap statistics:")
    _say(f"    n_pairs = {len(overlaps)}")
    _say(f"    mean q = {float(overlaps.mean()):+.4f}")
    _say(f"    std q  = {float(overlaps.std()):.4f}")
    _say(f"    min q  = {float(overlaps.min()):+.4f}")
    _say(f"    max q  = {float(overlaps.max()):+.4f}")

    # Peak detection in P(q)
    centers, counts, peaks = histogram_peaks(overlaps, num_bins=40)
    _say(f"\n  P(q) histogram peaks (>10% of max, local maxima):")
    for c, ct in peaks:
        _say(f"    peak at q={c:+.3f}, count={int(ct)}")
    _say(f"  Number of peaks: {len(peaks)}")

    # Ultrametricity
    um_gen = torch.Generator().manual_seed(SEED * 7)
    um_frac = ultrametricity_fraction(pool, NUM_TRIPLES, um_gen)
    _say(f"\n  Ultrametricity fraction (over {NUM_TRIPLES} random triples): {um_frac:.3f}")
    _say(f"    chance level: ~0.33 (3 random orderings)")

    _say("\n========= PHASE LOCALIZATION VERDICT =========")
    multi_peak = len(peaks) >= 2
    um_excess = um_frac - 0.33
    if multi_peak and um_excess > 0.1:
        _say(f"  RSB PHASE: {len(peaks)} peaks AND ultrametricity {um_frac:.3f} (chance+{um_excess:+.3f}).")
        _say(f"  IMPLICATION: substrate has emergent hierarchical retrieval index.")
        _say(f"  Next: build O(log P) tree-walk via Parisi ultrametric clustering.")
    elif multi_peak:
        _say(f"  PARTIAL RSB: multi-peaked P(q) but ultrametricity weak.")
    elif um_excess > 0.1:
        _say(f"  PARTIAL: ultrametricity present but no clear P(q) multi-peaking.")
    else:
        _say(f"  RS PHASE: single-peaked P(q), ultrametricity at chance.")
        _say(f"  IMPLICATION: use Frady-Sommer capacity theory. ~350K bundle headroom remaining.")
        _say(f"  Substrate is pool-bounded, not capacity-bounded.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e2_parisi_ultrametricity"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "K": K, "POOL_SIZE": pool.shape[0],
        "mean_q": float(overlaps.mean()),
        "std_q": float(overlaps.std()),
        "min_q": float(overlaps.min()),
        "max_q": float(overlaps.max()),
        "num_peaks": len(peaks),
        "peaks": peaks,
        "ultrametricity_fraction": um_frac,
    }, indent=2))


if __name__ == "__main__":
    main()
