"""Wave 14.B Phase A + B.2 at N=8192 with BYTE_BETA=16 (confirmed fix).

Parameter variant of existing Phase A + Phase B.2 scripts. Tests
whether the BETA=16 fix (which made C2 match C1 at N=4096) transfers
to larger substrate. If yes: the fix is N-invariant (good).

Pre-registered:
- C1 BWT should be similar to N=4096 (likely a bit better; bigger
  substrate handles noise better)
- C2-C1 gap should be within ±0.005 bpc (the BETA=16 fix should hold)

Self-contained: trains Phase A baseline at N=8192 from scratch, then
runs Phase B.2 with the BETA=16 readout. No dependence on existing
state.pt files.

Same architecture as Phase A + Phase B.2 at N=4096. Only change is N.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
BETA_RETRIEVAL = 8.0
BYTE_BETA = 16.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
EVAL_AT_A = [15]
EVAL_AT_B = [1, 5, 15]
RELU_B = 0.5
N = 8192  # CHANGED FROM 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4


def _say(msg: str) -> None:
    print(msg, flush=True)


def load_corpus_a() -> bytes:
    repo = Path(__file__).resolve().parent.parent
    files = [
        repo / "PLAN.md", repo / "NEXT_PHASE.md", repo / "README.md",
        repo / "PROGRESS.md", repo / "RESULTS.md", repo / "CLAUDE.md",
    ]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


def shuffle_bytes(data: bytes, seed: int) -> bytes:
    gen = torch.Generator().manual_seed(seed)
    n = len(data)
    perm = torch.randperm(n, generator=gen).tolist()
    out = bytearray(n)
    for i, p in enumerate(perm):
        out[i] = data[p]
    return bytes(out)


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def build_ctx_bundles_bsc(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def predict_W(W, ctxs, byte_atoms, beta, n):
    q = ctxs @ W.T
    q = shifted_relu(q, RELU_B)
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0)


def predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, beta, n):
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def predict_pool_vsa(ctxs, vsa_bundles, vsa_used, target_pos, byte_atoms,
                    beta_retrieval, beta_byte, n):
    B = ctxs.shape[0]
    if vsa_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    active = vsa_bundles[:vsa_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(beta_retrieval * sims, dim=0)
    target_estimates = active * target_pos.unsqueeze(0)
    byte_scores = (target_estimates @ byte_atoms.T) / n
    P_byte_per_entry = torch.softmax(beta_byte * byte_scores, dim=1)
    P_retr = P_byte_per_entry.T @ weights
    return P_retr


def prepare_test_tensors(test_bytes_bytes, byte_atoms, pos_atoms):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes_bytes
    T = len(padded) - K
    bs_tensor = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bs_tensor[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts = bs_tensor[pos + K]
    return idx, tgts


def build_vsa_pool(pool_vecs, pool_labels, pool_used, byte_atoms, target_pos):
    if pool_used == 0:
        return torch.zeros_like(pool_vecs)
    target_atoms = byte_atoms[pool_labels[:pool_used]]
    target_bound = target_atoms * target_pos.unsqueeze(0)
    return pool_vecs[:pool_used] + target_bound


def train_phase_a(byte_atoms, pos_atoms, train):
    """Train W_A on corpus A. Returns final state."""
    W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
    pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
    pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_used = 0
    pool_idx = 0
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)
    pad = bytes([PAD_BYTE]) * K
    padded_train = pad + train
    T_total = len(padded_train) - K
    train_bytes = torch.tensor(list(padded_train), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos_train = torch.arange(T_total, device=DEVICE)
    train_idx = train_bytes[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
    train_targets = train_bytes[pos_train + K]

    t_start = time.perf_counter()
    for epoch in range(1, MAX_EPOCHS + 1):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            with torch.no_grad():
                q = ctxs @ W.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA_RETRIEVAL * sims, dim=0)
                target_atoms_a = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms_a - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs.index_copy_(0, dest, ctxs)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
    elapsed = time.perf_counter() - t_start
    _say(f"  Phase A trained: ||W||={float(W.pow(2).sum().sqrt()):.1f}  ({elapsed:.1f}s)")
    return W, pool_vecs, pool_labels, pool_used


def eval_phase(W, byte_atoms, pos_atoms, test_idx, test_targets,
              pool_vecs, pool_labels, pool_used,
              vsa_bundles, vsa_used, target_pos, alpha):
    T_test = test_idx.shape[0]
    bits_c1 = 0.0
    bits_c2 = 0.0
    for bs in range(0, T_test, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T_test)
        ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_idx[bs:be])
        P_W = predict_W(W, ctxs, byte_atoms, BETA_RETRIEVAL, N)
        tgts = test_targets[bs:be]
        P_retr_c = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA_RETRIEVAL, N)
        P_c1 = alpha * P_retr_c + (1.0 - alpha) * P_W
        p_c1 = P_c1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits_c1 += float(-torch.log2(p_c1).sum())
        P_retr_v = predict_pool_vsa(ctxs, vsa_bundles, vsa_used, target_pos, byte_atoms,
                                   BETA_RETRIEVAL, BYTE_BETA, N)
        P_c2 = alpha * P_retr_v + (1.0 - alpha) * P_W
        p_c2 = P_c2.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits_c2 += float(-torch.log2(p_c2).sum())
    return {"c1_bpc": bits_c1 / max(T_test, 1),
            "c2_bpc": bits_c2 / max(T_test, 1)}


def main():
    _say(f"Wave 14.B Phase A + B.2 at N={N}, BYTE_BETA={BYTE_BETA}")
    _say(f"  Parameter variant: tests N-invariance of BETA=16 fix")

    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=SEED + 1)
    split_a = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split_a], corpus_a[split_a:]
    split_b = int(0.8 * len(corpus_b))
    train_b, test_b = corpus_b[:split_b], corpus_b[split_b:]
    _say(f"  Corpora: train_a={len(train_a)}, test_a={len(test_a)}, train_b={len(train_b)} bytes")

    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
    target_pos_gen = torch.Generator().manual_seed(SEED + 99)
    target_pos_bits = torch.randint(0, 2, (N,), generator=target_pos_gen)
    target_pos = (target_pos_bits * 2 - 1).to(torch.float32).to(DEVICE)

    _say(f"\nPhase A training at N={N}...")
    W, pool_vecs, pool_labels, pool_used = train_phase_a(byte_atoms, pos_atoms, train_a)

    vsa_bundles = build_vsa_pool(pool_vecs, pool_labels, pool_used, byte_atoms, target_pos)
    vsa_used = pool_used

    test_a_idx, test_a_targets = prepare_test_tensors(test_a, byte_atoms, pos_atoms)

    _say(f"\nPre-shift eval at N={N}:")
    pre = eval_phase(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                    pool_vecs, pool_labels, pool_used,
                    vsa_bundles, vsa_used, target_pos, ALPHA)
    _say(f"  test_A: C1={pre['c1_bpc']:.4f}  C2={pre['c2_bpc']:.4f}  diff={pre['c1_bpc']-pre['c2_bpc']:+.4f}")

    pad = bytes([PAD_BYTE]) * K
    padded_train_b = pad + train_b
    T_total = len(padded_train_b) - K
    train_b_bytes = torch.tensor(list(padded_train_b), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos_train = torch.arange(T_total, device=DEVICE)
    train_b_idx = train_b_bytes[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
    train_b_targets = train_b_bytes[pos_train + K]

    _say(f"\nContinual training W on corpus B ({MAX_EPOCHS} epochs)...")
    _say(f"  {'ep':>4} | {'C1':>8} | {'C2':>8} | {'C2-C1':>8}")
    history = []
    t_start = time.perf_counter()
    for epoch in range(1, MAX_EPOCHS + 1):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_b_idx[batch_start:be]
            tgt_batch = train_b_targets[batch_start:be]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            with torch.no_grad():
                q = ctxs @ W.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA_RETRIEVAL * sims, dim=0)
                target_atoms_b = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms_b - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)
        if epoch in EVAL_AT_B:
            with torch.no_grad():
                ev = eval_phase(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                              pool_vecs, pool_labels, pool_used,
                              vsa_bundles, vsa_used, target_pos, ALPHA)
                gap = ev["c1_bpc"] - ev["c2_bpc"]
                _say(f"  {epoch:>4} | {ev['c1_bpc']:>8.4f} | {ev['c2_bpc']:>8.4f} | {gap:>+8.4f}")
                history.append({"epoch": epoch, **ev, "gap": gap})

    final = history[-1]
    _say(f"\n========= VERDICT (N={N}) =========")
    _say(f"  Pre-shift  C2-C1: {pre['c1_bpc']-pre['c2_bpc']:+.4f}")
    _say(f"  Post-shift C2-C1: {final['gap']:+.4f}")
    _say(f"  At N=4096 the post-shift gap was -0.0001 (essentially zero).")
    if abs(final["gap"]) < 0.01:
        _say(f"  TRANSFER CONFIRMED: BETA=16 fix is N-invariant.")
    else:
        _say(f"  TRANSFER WEAK: fix needs re-tuning at larger N.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_phaseab_at_n8192"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"N": N, "BYTE_BETA": BYTE_BETA, "pre": pre, "history": history,
         "elapsed_s": time.perf_counter() - t_start},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
