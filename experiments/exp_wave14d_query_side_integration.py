"""Query-side integration probe -- atom-erased != fact unrecoverable.

After erasing an atom binding for a known fact, can the substrate still
recover the fact via W's parametric memory or via other pool entries?

This is the HARDEST open problem for the GDPR-erasure product wedge: edit
the atom = "erase from HDC pool". But the substrate also has W (parametric)
and OTHER pool entries that may have stored the same fact differently.

Test:
1. Train W on corpus A, build pool
2. Pick N=30 "facts" -- specific (K-byte prefix -> target byte) pairs from training set
3. For each fact:
   (a) Baseline: query substrate, measure P(correct target byte | prefix) and argmax-prediction
   (b) Erase the relevant atom binding (find the pool entry that stored this fact, edit it)
   (c) Re-query: does the substrate still predict the correct byte? Has P(correct) dropped?
4. Compute leak rate: fraction of "erased" facts where substrate still predicts the original byte.

Honest product framing: low leak rate (e.g., 30%) means "auditable erasure of HDC representation
but model can still recover from parametric memory" -- the substrate can claim erasure of THE
HDC-STORED FORM but not erasure from W. High leak rate (e.g., 80%) means substrate edits are
mostly cosmetic.

The lower the leak rate, the stronger the product claim.
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
NUM_FACTS = 30


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
    pool_byte_at_pos = torch.zeros((POOL_SIZE, K), dtype=torch.long, device=DEVICE)
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
                    pool_byte_at_pos.index_copy_(0, dest, idx_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_byte_at_pos, pool_used


def predict_byte(W, byte_atoms, pos_atoms, prefix_idx, pool_vecs, pool_labels, pool_used,
                  alpha=ALPHA):
    ctx = build_ctx_single(byte_atoms, pos_atoms, prefix_idx)
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
        P = alpha * P_retr + (1 - alpha) * P_W
    else:
        P = P_W
    return P


def find_matching_pool_entry(prefix_idx, target_byte, pool_byte_at_pos, pool_labels, pool_used):
    """Find pool entry where pool_byte_at_pos[i] == prefix_idx AND pool_labels[i] == target_byte.
    Returns first matching index or -1."""
    for i in range(pool_used):
        if torch.equal(pool_byte_at_pos[i], prefix_idx) and int(pool_labels[i].item()) == target_byte:
            return i
    return -1


def erase_pool_entry(pool_vecs, pool_labels, pool_byte_at_pos, entry_idx):
    """Zero out the entry. Doesn't shrink pool_used; effectively excludes from retrieval."""
    pool_vecs[entry_idx] = 0.0
    # Optionally: replace with random noise to make it more thoroughly "erased"
    # but for now, zeroing is the simplest test.


def run_one(seed):
    corpus_a = load_corpus_a()
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    _say(f"  training W (K={K})...")
    W, pool_vecs, pool_labels, pool_byte_at_pos, pool_used = train_phase_a(byte_atoms, pos_atoms, train_a)

    # Pick NUM_FACTS pool entries as "facts" to erase-and-probe
    fact_gen = torch.Generator().manual_seed(seed * 7)
    fact_indices = torch.randperm(pool_used, generator=fact_gen)[:NUM_FACTS].tolist()

    leak_results = []
    for fi, fact_pool_idx in enumerate(fact_indices):
        prefix_idx = pool_byte_at_pos[fact_pool_idx].clone()
        target_byte = int(pool_labels[fact_pool_idx].item())

        # Baseline query: predict next byte
        P_before = predict_byte(W, byte_atoms, pos_atoms, prefix_idx, pool_vecs, pool_labels, pool_used)
        p_target_before = float(P_before[target_byte].item())
        argmax_before = int(P_before.argmax().item())

        # Erase the matching pool entry
        erase_pool_entry(pool_vecs, pool_labels, pool_byte_at_pos, fact_pool_idx)

        # Also erase any OTHER entries that have the same prefix (could leak)
        also_erased = 0
        for j in range(pool_used):
            if j == fact_pool_idx:
                continue
            if torch.equal(pool_byte_at_pos[j], prefix_idx) and int(pool_labels[j].item()) == target_byte:
                erase_pool_entry(pool_vecs, pool_labels, pool_byte_at_pos, j)
                also_erased += 1

        # Re-query
        P_after = predict_byte(W, byte_atoms, pos_atoms, prefix_idx, pool_vecs, pool_labels, pool_used)
        p_target_after = float(P_after[target_byte].item())
        argmax_after = int(P_after.argmax().item())

        # Pure W (alpha=0) for comparison: parametric leakage only
        P_w_only = predict_byte(W, byte_atoms, pos_atoms, prefix_idx, pool_vecs, pool_labels, pool_used, alpha=0.0)
        p_target_w_only = float(P_w_only[target_byte].item())
        argmax_w_only = int(P_w_only.argmax().item())

        leaked = (argmax_after == target_byte)
        w_only_leaked = (argmax_w_only == target_byte)
        leak_results.append({
            "fact_idx": fi,
            "p_target_before": p_target_before,
            "p_target_after": p_target_after,
            "p_target_w_only": p_target_w_only,
            "argmax_before": argmax_before,
            "argmax_after": argmax_after,
            "argmax_w_only": argmax_w_only,
            "target_byte": target_byte,
            "leaked_after_erase": leaked,
            "leaked_via_w_only": w_only_leaked,
            "also_erased_count": also_erased,
        })

        # Restore the pool entry to its original state for next fact's clean test
        # (we don't bother — sequential erasures only add noise to the test;
        # since we erase all matching entries each time, the next fact's baseline
        # is still clean because its entries are different)

    leak_rate_combined = sum(r["leaked_after_erase"] for r in leak_results) / len(leak_results)
    leak_rate_w_only = sum(r["leaked_via_w_only"] for r in leak_results) / len(leak_results)
    mean_p_drop = sum(r["p_target_before"] - r["p_target_after"] for r in leak_results) / len(leak_results)

    return {
        "leak_rate_combined": leak_rate_combined,
        "leak_rate_w_only": leak_rate_w_only,
        "mean_p_drop": mean_p_drop,
        "leak_results": leak_results,
    }


def main():
    _say(f"Query-side integration probe: K={K}, {NUM_FACTS} facts, {len(SEEDS)} seeds")
    _say(f"  Honest product claim depends on leak rate:")
    _say(f"    <30%: substrate edits effectively erase from queries (strong)")
    _say(f"    30-60%: substrate erases HDC representation, W still leaks (medium -- product is 'erase HDC form')")
    _say(f"    >60%: substrate edits are mostly cosmetic, W dominates queries (weak)")
    all_results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        r = run_one(seed)
        _say(f"  leak rate (combined W+pool query): {r['leak_rate_combined']*100:.1f}%")
        _say(f"  leak rate (W-only, alpha=0):       {r['leak_rate_w_only']*100:.1f}%")
        _say(f"  mean P(target) drop after erase:   {r['mean_p_drop']:+.4f}")
        all_results.append({"seed": seed, **r})

    _say("\n========= QUERY-SIDE INTEGRATION VERDICT =========")
    mean_combined = sum(r["leak_rate_combined"] for r in all_results) / len(all_results)
    mean_w_only = sum(r["leak_rate_w_only"] for r in all_results) / len(all_results)
    mean_drop = sum(r["mean_p_drop"] for r in all_results) / len(all_results)
    _say(f"  Mean leak rate (combined): {mean_combined*100:.1f}%")
    _say(f"  Mean leak rate (W-only):   {mean_w_only*100:.1f}%")
    _say(f"  Mean P(target) drop:       {mean_drop:+.4f}")
    if mean_combined < 0.3:
        _say(f"\n  STRONG: substrate edits effectively erase from queries. Product claim 'auditable erasure from model' is honest.")
    elif mean_combined < 0.6:
        _say(f"\n  MEDIUM: HDC representation erased but W still recovers ~{mean_w_only*100:.0f}% of facts. Honest product claim: 'auditable erasure of HDC-stored form, partial reduction from W.'")
    else:
        _say(f"\n  WEAK: substrate edits are mostly cosmetic. Need a stronger erasure primitive (also edit W).")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14d_query_side_integration"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "NUM_FACTS": NUM_FACTS, "SEEDS": SEEDS,
        "results": all_results,
    }, indent=2))


if __name__ == "__main__":
    main()
