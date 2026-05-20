"""Can the substrate autoregressively generate? Test via sample-feedback loop.

Hypothesis: the substrate trains on K-gram next-byte prediction. At inference,
we can feed each predicted byte back as the next input position and roll
forward to generate sequences of arbitrary length.

Key product question: does this maintain coherence beyond 1-step prediction,
or does error accumulation kill it within a few bytes?

Test (3 seeds, K=4):
- Phase A: train W + build pool from corpus A as usual
- Eval: pick 50 random K-byte PREFIXES from held-out corpus A test split
- For each prefix:
  - Generate next 64 bytes autoregressively via greedy argmax + temp-sampled
  - Compare to ground-truth continuation (next 64 actual bytes from test_a)
  - Measure byte-level accuracy at positions 1, 2, 4, 8, 16, 32, 64
- Baselines:
  - Random (uniform): ~1/256 = 0.4% accuracy
  - Unigram-most-common (always emit space): empirical floor
  - 1-step (gets fed ground truth each step): upper bound

Generation confirmed if greedy accuracy at position 8 > 5x random baseline (>2%).
"Coherent" if accuracy at position 32 > 1.5x random.

Also outputs 5 sample generations per seed for qualitative inspection.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

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

SEEDS = [17, 23, 31]
NUM_PREFIXES = 50
GEN_LENGTH = 64
TEMPERATURES = [0.0, 0.7, 1.0]  # 0.0 = greedy
EVAL_POSITIONS = [1, 2, 4, 8, 16, 32, 64]
SAMPLE_SHOW_COUNT = 5


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
    """Build context for a single K-gram (no batch dim)."""
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


def predict_distribution(W, ctx, byte_atoms, pool_vecs, pool_labels, pool_used):
    """Get next-byte distribution given a single context vector."""
    q = ctx @ W.T
    q = shifted_relu(q, RELU_B)
    sims = (byte_atoms @ q) / N
    P_W = torch.softmax(BETA * sims, dim=0)
    if pool_used > 0:
        active = pool_vecs[:pool_used]
        labels = pool_labels[:pool_used]
        sims_p = (active @ ctx) / N
        weights_p = torch.softmax(BETA * sims_p, dim=0)
        P_retr = torch.zeros(VOCAB_SIZE, device=DEVICE)
        P_retr.scatter_add_(0, labels, weights_p)
        return ALPHA * P_retr + (1 - ALPHA) * P_W
    return P_W


def sample_from_dist(P, temperature, gen):
    if temperature == 0.0:
        return int(P.argmax().item())
    logp = torch.log(P.clamp(min=1e-12))
    scaled = logp / temperature
    P2 = torch.softmax(scaled, dim=0)
    return int(torch.multinomial(P2, num_samples=1, generator=gen).item())


def generate_sequence(W, byte_atoms, pos_atoms, pool_vecs, pool_labels, pool_used,
                       prefix_bytes, length, temperature, sample_gen):
    """Generate `length` bytes given a K-byte prefix using sample-feedback loop."""
    ctx_bytes = list(prefix_bytes)
    generated = []
    for _ in range(length):
        # build K-byte window from the last K bytes
        window = ctx_bytes[-K:]
        # reverse order matches the offsets pattern in training:
        # offsets = arange(K-1, -1, -1) means rightmost = oldest in index 0
        idx = torch.tensor(list(reversed(window)), dtype=torch.long, device=DEVICE)
        ctx = build_ctx_single(byte_atoms, pos_atoms, idx)
        P = predict_distribution(W, ctx, byte_atoms, pool_vecs, pool_labels, pool_used)
        next_byte = sample_from_dist(P, temperature, sample_gen)
        generated.append(next_byte)
        ctx_bytes.append(next_byte)
    return bytes(generated)


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


def run_one(seed):
    corpus_a = load_corpus_a()
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a)

    # Pick random prefix positions in test_a
    prefix_gen = torch.Generator().manual_seed(seed * 7)
    test_len = len(test_a)
    valid_positions = test_len - K - GEN_LENGTH
    if valid_positions <= 0:
        raise RuntimeError(f"test_a too short ({test_len}) for prefix sampling")
    prefix_positions = torch.randperm(valid_positions, generator=prefix_gen)[:NUM_PREFIXES].tolist()

    results = {}
    sample_gen = torch.Generator(device=DEVICE).manual_seed(seed * 13)
    for temp in TEMPERATURES:
        pos_correct = {p: 0 for p in EVAL_POSITIONS}
        total = 0
        samples_shown = 0
        sample_log = []
        for pos in prefix_positions:
            prefix = test_a[pos:pos + K]
            truth = test_a[pos + K:pos + K + GEN_LENGTH]
            generated = generate_sequence(W_A, byte_atoms, pos_atoms, pool_A,
                                           labels_A, used_A, prefix, GEN_LENGTH,
                                           temp, sample_gen)
            for p in EVAL_POSITIONS:
                if p <= len(truth) and p <= len(generated):
                    matches = sum(1 for i in range(p) if generated[i] == truth[i])
                    pos_correct[p] += matches
            total += 1
            if temp == 0.0 and samples_shown < SAMPLE_SHOW_COUNT:
                # Show readable preview (printable chars only)
                def safe(b):
                    return "".join(chr(c) if 32 <= c < 127 else "." for c in b)
                sample_log.append({
                    "prefix": safe(prefix),
                    "truth": safe(truth[:48]),
                    "generated": safe(generated[:48]),
                })
                samples_shown += 1
        results[f"temp_{temp}"] = {
            "pos_accuracy": {p: (pos_correct[p] / (total * p)) for p in EVAL_POSITIONS},
            "samples": sample_log if temp == 0.0 else None,
        }
    return results


def main():
    _say(f"Generation via sample-feedback: K={K}, {NUM_PREFIXES} prefixes per seed, length={GEN_LENGTH}")
    _say(f"  Temperatures: {TEMPERATURES} (0.0 = greedy)")
    _say(f"  Eval positions: {EVAL_POSITIONS}")

    all_results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        r = run_one(seed)
        for temp in TEMPERATURES:
            acc = r[f"temp_{temp}"]["pos_accuracy"]
            acc_str = " ".join(f"p{p}={acc[p]*100:.1f}%" for p in EVAL_POSITIONS)
            _say(f"  T={temp}: {acc_str}")
        # Show samples from greedy
        if r["temp_0.0"]["samples"]:
            _say(f"\n  Greedy samples (T=0.0):")
            for s in r["temp_0.0"]["samples"][:3]:
                _say(f"    prefix={s['prefix']!r}")
                _say(f"    truth=    {s['truth']!r}")
                _say(f"    generated={s['generated']!r}")
                _say("")
        all_results.append({"seed": seed, **r})

    _say("\n========= GENERATION VERDICT =========")
    for temp in TEMPERATURES:
        for p in EVAL_POSITIONS:
            mean_acc = sum(r[f"temp_{temp}"]["pos_accuracy"][p] for r in all_results) / len(all_results)
            _say(f"  T={temp} pos={p}: mean accuracy = {mean_acc*100:.2f}%")
    _say(f"\n  Random baseline (uniform 256): 0.39%")

    # Verdict on greedy at position 8
    mean_p8 = sum(r["temp_0.0"]["pos_accuracy"][8] for r in all_results) / len(all_results)
    if mean_p8 >= 0.02:
        _say(f"\n  GENERATION CONFIRMED: greedy p8 accuracy {mean_p8*100:.2f}% > 5x random.")
    elif mean_p8 >= 0.01:
        _say(f"\n  WEAK GENERATION: p8 accuracy {mean_p8*100:.2f}%, between random and meaningful.")
    else:
        _say(f"\n  GENERATION NOT WORKING: p8 accuracy {mean_p8*100:.2f}% near random baseline.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14d_generation_K8"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "GEN_LENGTH": GEN_LENGTH, "TEMPERATURES": TEMPERATURES,
        "EVAL_POSITIONS": EVAL_POSITIONS,
        "results": all_results,
    }, indent=2))


if __name__ == "__main__":
    main()
