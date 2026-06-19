"""MVP3 R3 gate: erase-under-replay correctness.

GDPR claim: substrate erases facts surgically + audit log proves erasure.
But replay during Phase B re-introduces evidence from the pool. If a pool entry
was erased, does replay still bring it back? CRITICAL for the compliance story.

Test:
1. Train W on corpus A (with replay pool)
2. Erase N=10 specific pool entries (set them to zero / sign of empty)
3. Run Phase B training with random replay (which DRAWS from the pool)
4. Verify: do the erased patterns get re-introduced into W via replay?
5. Then query Phase A test: does the model still predict the erased facts?

Pass: erased facts have predicted byte WRONG >=90% on Phase A test (proves
erasure survives replay) OR replay does NOT visit the erased indices.

Verifies: substrate's erase primitive is replay-equivalent.

3 seeds, K=8, NUM_ERASURES=10.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 8
N = 4096
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
REPLAY_FRACTION = 0.5

SEEDS = [17, 23, 31]
NUM_ERASURES = 10


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


def shuffle_bytes(data, seed):
    gen = torch.Generator().manual_seed(seed)
    perm = torch.randperm(len(data), generator=gen).tolist()
    return bytes(data[p] for p in perm)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def build_ctx(byte_atoms, pos_atoms, idx):
    b = byte_atoms[idx] * pos_atoms.unsqueeze(0)
    out = torch.sign(b.sum(dim=1))
    return torch.where(out == 0, torch.ones_like(out), out)


def relu_shift(q, b): return torch.clamp(q - b, min=0.0)


def train_phase_a(byte_atoms, pos_atoms, train_bytes):
    W = torch.zeros((N, N), device=DEVICE)
    pool_v = torch.zeros((POOL_SIZE, N), device=DEVICE)
    pool_l = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_idx_track = torch.zeros((POOL_SIZE, K), dtype=torch.long, device=DEVICE)
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
            ctxs = build_ctx(byte_atoms, pos_atoms, idx[bs:be])
            t = tgt[bs:be]
            with torch.no_grad():
                q = relu_shift(ctxs @ W.T, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                resid = byte_atoms[t] - (P.T @ byte_atoms)
                dW = (resid.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY); W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if epoch == 1:
                    dest = (p_idx + arange[:B]) % POOL_SIZE
                    pool_v.index_copy_(0, dest, ctxs)
                    pool_l.index_copy_(0, dest, t)
                    pool_idx_track.index_copy_(0, dest, idx[bs:be])
                    p_idx = (p_idx + B) % POOL_SIZE
                    p_used = min(p_used + B, POOL_SIZE)
    return W, pool_v, pool_l, pool_idx_track, p_used


def erase_pool_entries(pool_v, pool_l, indices):
    """Mark entries as erased: zero the bundle, set label to PAD_BYTE."""
    for i in indices:
        pool_v[i] = 0
        pool_l[i] = PAD_BYTE


def train_phase_b_with_replay(byte_atoms, pos_atoms, train_bytes, W_start,
                                 pool_v, pool_l, p_used, replay_fraction):
    W = W_start.clone()
    visited_pool_indices = set()
    gen = torch.Generator(device="cpu").manual_seed(99)
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offs = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offs.unsqueeze(0)]
    tgt = bt[pos + K]
    for epoch in range(MAX_EPOCHS):
        for bs in range(0, T, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T)
            B = be - bs
            ctxs = build_ctx(byte_atoms, pos_atoms, idx[bs:be])
            t = tgt[bs:be]
            if replay_fraction > 0 and p_used > 0:
                n_replay = int(B * replay_fraction)
                if n_replay > 0:
                    replay_idx = torch.randint(0, p_used, (n_replay,), generator=gen).to(DEVICE)
                    for r_idx in replay_idx.cpu().tolist():
                        visited_pool_indices.add(r_idx)
                    replay_ctxs = pool_v[replay_idx]
                    replay_tgts = pool_l[replay_idx]
                    ctxs = torch.cat([ctxs[:B - n_replay], replay_ctxs], dim=0)
                    t = torch.cat([t[:B - n_replay], replay_tgts], dim=0)
            with torch.no_grad():
                q = relu_shift(ctxs @ W.T, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                resid = byte_atoms[t] - (P.T @ byte_atoms)
                dW = (resid.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY); W.add_(dW, alpha=DELTA_RULE_ALPHA)
    return W, visited_pool_indices


def predict_byte(W, byte_atoms, pos_atoms, prefix_idx):
    ctx = build_ctx(byte_atoms, pos_atoms, prefix_idx.unsqueeze(0)).squeeze(0)
    q = relu_shift(ctx @ W.T, RELU_B)
    sims = (byte_atoms @ q) / N
    return torch.softmax(BETA * sims, dim=0)


def run_one(seed):
    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=seed + 1)
    split = int(0.8 * len(corpus_a))
    train_a = corpus_a[:split]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc(K, N, gen).to(DEVICE)

    W_A, pool_v, pool_l, pool_idx, p_used = train_phase_a(byte_atoms, pos_atoms, train_a)

    # Pick 10 random pool entries to erase
    erase_gen = torch.Generator().manual_seed(seed * 7)
    erase_indices = torch.randperm(p_used, generator=erase_gen)[:NUM_ERASURES].cpu().tolist()
    # Capture the prefixes + targets BEFORE erasure
    erased_facts = [(pool_idx[i].clone(), int(pool_l[i].item())) for i in erase_indices]

    # Baseline: predict erased targets before erasure
    base_correct = 0
    for prefix, target in erased_facts:
        p = predict_byte(W_A, byte_atoms, pos_atoms, prefix)
        if int(p.argmax().item()) == target:
            base_correct += 1

    # Erase
    erase_pool_entries(pool_v, pool_l, erase_indices)

    # Phase B training with replay (which draws from the erased-pool)
    W_AB, visited = train_phase_b_with_replay(byte_atoms, pos_atoms, train_b, W_A,
                                                pool_v, pool_l, p_used, REPLAY_FRACTION)

    # Did replay visit the erased entries?
    erased_visited = sum(1 for i in erase_indices if i in visited)

    # After Phase B + replay, can we still predict the erased facts?
    after_correct = 0
    after_correct_w_only = 0
    for prefix, target in erased_facts:
        p = predict_byte(W_AB, byte_atoms, pos_atoms, prefix)
        if int(p.argmax().item()) == target:
            after_correct += 1

    return {
        "baseline_correct_pre_erase": base_correct,
        "erased_visited_by_replay": erased_visited,
        "predict_correct_after_replay": after_correct,
        "n_erasures": NUM_ERASURES,
    }


def main():
    _say(f"Erase-under-replay correctness: K={K}, {NUM_ERASURES} erasures, replay={REPLAY_FRACTION}, 3 seeds")
    all_results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        r = run_one(seed)
        _say(f"  pre-erase predict correct: {r['baseline_correct_pre_erase']}/{NUM_ERASURES}")
        _say(f"  erased entries visited by replay: {r['erased_visited_by_replay']}/{NUM_ERASURES}")
        _say(f"  post-Phase-B predict correct: {r['predict_correct_after_replay']}/{NUM_ERASURES}")
        all_results.append({"seed": seed, **r})

    _say(f"\n========= ERASE-UNDER-REPLAY VERDICT =========")
    mean_pre = sum(r['baseline_correct_pre_erase'] for r in all_results) / len(all_results)
    mean_after = sum(r['predict_correct_after_replay'] for r in all_results) / len(all_results)
    erase_effective = (mean_pre - mean_after) / max(mean_pre, 1)
    _say(f"  Mean pre-erase correct: {mean_pre:.1f}/{NUM_ERASURES}")
    _say(f"  Mean post-replay correct: {mean_after:.1f}/{NUM_ERASURES}")
    _say(f"  Erase effectiveness: {erase_effective*100:.0f}% (1.0 = perfect erasure, 0 = replay re-introduced)")
    if erase_effective >= 0.9:
        _say(f"  PASS: erase survives replay. GDPR substrate claim holds.")
    elif erase_effective >= 0.5:
        _say(f"  PARTIAL: erase weakened by replay. Need stronger erase primitive (e.g., re-train W after erase).")
    else:
        _say(f"  FAIL: replay re-introduces erased facts. Substrate erase is NOT replay-equivalent without additional protocol.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14g_erase_under_replay"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "NUM_ERASURES": NUM_ERASURES, "REPLAY_FRACTION": REPLAY_FRACTION,
        "SEEDS": SEEDS, "results": all_results,
        "mean_pre": mean_pre, "mean_after": mean_after, "erase_effective": erase_effective,
    }, indent=2))


if __name__ == "__main__":
    main()
