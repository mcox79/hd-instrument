"""Generation v2 — research-recommended design at K=16.

Per wave14d_generation_from_k_gram_research.md, v1 had wrong shape:
1. K=4 is diagnosis-only — English words exceed 4 bytes, coherence impossible.
   v2: K=16 (smallest plausible product-quality regime).
2. "5x random uniform" verdict is unigram-frequency floor (always emit space).
   v2: proper baseline B3 = raw K-gram count from training corpus (Markov chain LM).
3. Add pool-on vs pool-off A/B. Pool may help at p<=4 (real context bytes) and
   hurt at p>=8 (window full of substrate's own samples). Informative either way.
4. Add K-gram-validity metric: fraction of generated K-grams present in training.

GENERATION CONFIRMED if substrate-greedy beats B3 at p=1 by >=5pp AND
K-gram-validity >= 0.4 at length 64.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 32
N = 4096
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4

SEEDS = [17, 23, 31]
NUM_PREFIXES = 30  # fewer than v1 because K=16 is slower
GEN_LENGTH = 64
EVAL_POSITIONS = [1, 2, 4, 8, 16, 32, 64]


def _say(msg):
    print(msg, flush=True)


def load_corpus_a():
    repo = Path(__file__).resolve().parent.parent
    files = [repo / "PLAN.md", repo / "NEXT_PHASE.md", repo / "README.md",
             repo / "PROGRESS.md", repo / "RESULTS.md", repo / "CLAUDE.md"]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def build_ctx_single(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms
    summed = bound.sum(dim=0)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def build_ctx_batch(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def train_phase_a(byte_atoms, pos_atoms, train_bytes):
    W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
    pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
    pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_idx = 0
    pool_used = 0
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
    T_total = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    train_idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    train_targets = bt[pos + K]
    for epoch in range(1, MAX_EPOCHS + 1):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = build_ctx_batch(byte_atoms, pos_atoms, idx_batch)
            with torch.no_grad():
                q = ctxs @ W.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs.index_copy_(0, dest, ctxs)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_used


def build_b3_table(train_bytes):
    """B3 baseline: raw K-gram counting (Markov chain LM).
    Returns dict mapping prefix tuple -> most-common-next-byte."""
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
    counts = {}
    for i in range(len(padded) - K):
        prefix = tuple(padded[i:i + K])
        next_byte = padded[i + K]
        if prefix not in counts:
            counts[prefix] = Counter()
        counts[prefix][next_byte] += 1
    table = {prefix: c.most_common(1)[0][0] for prefix, c in counts.items()}
    return table, counts


def b3_generate(b3_table, b3_counts, prefix_bytes, length, fallback_byte=ord(" ")):
    """Generate via B3 Markov chain (argmax next-byte given K-prefix).
    Falls back to space if prefix unseen."""
    ctx = list(prefix_bytes)
    generated = []
    for _ in range(length):
        window = tuple(ctx[-K:])
        next_byte = b3_table.get(window, fallback_byte)
        generated.append(next_byte)
        ctx.append(next_byte)
    return bytes(generated)


def predict_distribution(W, ctx, byte_atoms, pool_vecs, pool_labels, pool_used, use_pool):
    q = ctx @ W.T
    q = shifted_relu(q, RELU_B)
    sims = (byte_atoms @ q) / N
    P_W = torch.softmax(BETA * sims, dim=0)
    if use_pool and pool_used > 0:
        active = pool_vecs[:pool_used]
        labels = pool_labels[:pool_used]
        sims_p = (active @ ctx) / N
        weights_p = torch.softmax(BETA * sims_p, dim=0)
        P_retr = torch.zeros(VOCAB_SIZE, device=DEVICE)
        P_retr.scatter_add_(0, labels, weights_p)
        return ALPHA * P_retr + (1 - ALPHA) * P_W
    return P_W


def substrate_generate(W, byte_atoms, pos_atoms, pool_vecs, pool_labels, pool_used,
                        prefix_bytes, length, use_pool):
    ctx_bytes = list(prefix_bytes)
    generated = []
    for _ in range(length):
        window = ctx_bytes[-K:]
        idx = torch.tensor(list(reversed(window)), dtype=torch.long, device=DEVICE)
        ctx = build_ctx_single(byte_atoms, pos_atoms, idx)
        P = predict_distribution(W, ctx, byte_atoms, pool_vecs, pool_labels, pool_used, use_pool)
        next_byte = int(P.argmax().item())
        generated.append(next_byte)
        ctx_bytes.append(next_byte)
    return bytes(generated)


def k_gram_validity(generated_bytes, train_bytes, K_val):
    """Fraction of K-grams in generated_bytes that appear in train_bytes."""
    train_kgrams = set()
    pad = bytes([PAD_BYTE]) * K_val
    padded = pad + train_bytes
    for i in range(len(padded) - K_val + 1):
        train_kgrams.add(tuple(padded[i:i + K_val]))
    gen_kgrams = []
    for i in range(len(generated_bytes) - K_val + 1):
        gen_kgrams.append(tuple(generated_bytes[i:i + K_val]))
    if not gen_kgrams:
        return 0.0
    return sum(1 for kg in gen_kgrams if kg in train_kgrams) / len(gen_kgrams)


def run_one(seed):
    corpus_a = load_corpus_a()
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    _say(f"  training W (K={K}, this takes ~5-10min)...")
    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)

    _say(f"  building B3 K-gram table...")
    b3_table, b3_counts = build_b3_table(train_a)
    _say(f"  B3 has {len(b3_table)} prefix entries")

    prefix_gen = torch.Generator().manual_seed(seed * 7)
    test_len = len(test_a)
    valid_positions = test_len - K - GEN_LENGTH
    if valid_positions <= 0:
        raise RuntimeError(f"test_a too short ({test_len}) for K={K} prefix sampling")
    prefix_positions = torch.randperm(valid_positions, generator=prefix_gen)[:NUM_PREFIXES].tolist()

    pos_correct = {
        "substrate_pool": {p: 0 for p in EVAL_POSITIONS},
        "substrate_no_pool": {p: 0 for p in EVAL_POSITIONS},
        "b3": {p: 0 for p in EVAL_POSITIONS},
    }
    total = 0
    validity_scores = {"substrate_pool": [], "substrate_no_pool": [], "b3": []}
    sample_log = []

    for pos in prefix_positions:
        prefix = test_a[pos:pos + K]
        truth = test_a[pos + K:pos + K + GEN_LENGTH]

        gen_pool = substrate_generate(W_A, byte_atoms, pos_atoms, pool_A,
                                       labels_A, used_A, prefix, GEN_LENGTH, use_pool=True)
        gen_no_pool = substrate_generate(W_A, byte_atoms, pos_atoms, pool_A,
                                          labels_A, used_A, prefix, GEN_LENGTH, use_pool=False)
        gen_b3 = b3_generate(b3_table, b3_counts, prefix, GEN_LENGTH)

        for mode_name, mode_gen in [("substrate_pool", gen_pool),
                                      ("substrate_no_pool", gen_no_pool),
                                      ("b3", gen_b3)]:
            for p in EVAL_POSITIONS:
                if p <= len(truth) and p <= len(mode_gen):
                    matches = sum(1 for i in range(p) if mode_gen[i] == truth[i])
                    pos_correct[mode_name][p] += matches
            validity_scores[mode_name].append(k_gram_validity(mode_gen, train_a, K_val=4))

        total += 1
        if len(sample_log) < 3:
            def safe(b):
                return "".join(chr(c) if 32 <= c < 127 else "." for c in b)
            sample_log.append({
                "prefix": safe(prefix[-32:]),
                "truth": safe(truth[:48]),
                "gen_pool": safe(gen_pool[:48]),
                "gen_no_pool": safe(gen_no_pool[:48]),
                "gen_b3": safe(gen_b3[:48]),
            })

    accuracy = {
        mode: {p: pos_correct[mode][p] / (total * p) for p in EVAL_POSITIONS}
        for mode in pos_correct
    }
    validity_mean = {mode: sum(s) / len(s) if s else 0.0 for mode, s in validity_scores.items()}

    return {
        "accuracy": accuracy,
        "validity": validity_mean,
        "samples": sample_log,
    }


def main():
    _say(f"Generation v2 at K={K}: substrate (pool on/off) vs B3 (raw K-gram counts)")
    _say(f"  {NUM_PREFIXES} prefixes per seed, length={GEN_LENGTH}, {len(SEEDS)} seeds")
    _say(f"  Verdict: GENERATION CONFIRMED if substrate beats B3 at p=1 by >=5pp")
    _say(f"           AND K-gram-validity (K=4 substring check) >= 0.4")

    all_results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        r = run_one(seed)
        for mode in ["substrate_pool", "substrate_no_pool", "b3"]:
            acc_str = " ".join(f"p{p}={r['accuracy'][mode][p]*100:.1f}%" for p in EVAL_POSITIONS)
            _say(f"  {mode:20s}: {acc_str}  k4_validity={r['validity'][mode]:.3f}")
        _say(f"\n  Samples (truncated 48 bytes):")
        for s in r["samples"][:2]:
            _say(f"    prefix=     {s['prefix']!r}")
            _say(f"    truth=      {s['truth']!r}")
            _say(f"    pool=       {s['gen_pool']!r}")
            _say(f"    no_pool=    {s['gen_no_pool']!r}")
            _say(f"    b3=         {s['gen_b3']!r}")
            _say("")
        all_results.append({"seed": seed, **r})

    _say("\n========= GENERATION v2 VERDICT =========")
    for mode in ["substrate_pool", "substrate_no_pool", "b3"]:
        for p in EVAL_POSITIONS:
            mean_acc = sum(r["accuracy"][mode][p] for r in all_results) / len(all_results)
            _say(f"  {mode:20s} pos={p:3d}: mean accuracy = {mean_acc*100:.2f}%")
    for mode in ["substrate_pool", "substrate_no_pool", "b3"]:
        mean_val = sum(r["validity"][mode] for r in all_results) / len(all_results)
        _say(f"  {mode:20s} k4_validity: {mean_val:.3f}")

    sub_p1 = sum(r["accuracy"]["substrate_pool"]["p" if False else 1] for r in all_results) / len(all_results)
    b3_p1 = sum(r["accuracy"]["b3"][1] for r in all_results) / len(all_results)
    sub_validity = sum(r["validity"]["substrate_pool"] for r in all_results) / len(all_results)
    delta_p1 = sub_p1 - b3_p1
    _say(f"\n  substrate_pool p1: {sub_p1*100:.2f}%")
    _say(f"  B3 p1: {b3_p1*100:.2f}%")
    _say(f"  delta: {delta_p1*100:+.2f}pp")
    _say(f"  substrate_pool k4_validity: {sub_validity:.3f}")
    if delta_p1 >= 0.05 and sub_validity >= 0.4:
        _say(f"\n  GENERATION CONFIRMED")
    elif delta_p1 >= 0.02 or sub_validity >= 0.25:
        _say(f"\n  WEAK GENERATION SIGNAL")
    else:
        _say(f"\n  GENERATION NOT CONFIRMED at K={K}")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14d_generation_v2_K32"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "GEN_LENGTH": GEN_LENGTH, "SEEDS": SEEDS,
        "EVAL_POSITIONS": EVAL_POSITIONS,
        "results": all_results,
    }, indent=2))


if __name__ == "__main__":
    main()
