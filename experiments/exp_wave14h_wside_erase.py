"""W-side anti-Hebbian rank-1 erase: closes the GDPR substrate gap.

Per cycle-10 wave14d_query_side_integration: 93% leak rate after pool erasure
(W has absorbed the patterns).
Per cycle-12 wave14g_erase_under_replay: 7% erase_effective (replay re-introduces).
Per research notes/wave14g_research_wside_erasure.md: closed-form fix is rank-1
anti-Hebbian update:
    W -= alpha * (W @ k)(k^T C^-1) / (k^T C^-1 k)
where C is the key second-moment matrix. For random ±1 keys at d, C ≈ I, so:
    W -= alpha * (W @ k) k^T / d

Test: train W on N facts, erase 10 via two methods, measure prediction leak rate.
  Method A: pool-zero only (current substrate)
  Method B: pool-zero + W anti-Hebbian rank-1
Decision rule: Method B reduces leak_rate by >= 50pp while preserving non-erased
recall (>= 80%).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import torch

from hdlab.progress import update as prog_update, reset as prog_reset


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 8
N = 4096
BETA = 8.0
ALPHA_TRAIN = 0.3
DECAY = 1e-4
RELU_B = 0.5
ALPHA_ERASE = 1.0
N_FACTS = 30  # number of (key, value) facts
N_ERASURES = 10
MAX_EPOCHS = 15
SEEDS = [17, 23, 31]


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def build_ctx(byte_atoms, pos_atoms, idx):
    b = byte_atoms[idx] * pos_atoms.unsqueeze(0)
    out = torch.sign(b.sum(dim=1))
    return torch.where(out == 0, torch.ones_like(out), out)


def relu_shift(q, b):
    return torch.clamp(q - b, min=0.0)


def predict_byte(W, byte_atoms, pos_atoms, prefix_idx):
    ctx = build_ctx(byte_atoms, pos_atoms, prefix_idx.unsqueeze(0)).squeeze(0)
    q = relu_shift(ctx @ W.T, RELU_B)
    sims = (byte_atoms @ q) / N
    return torch.softmax(BETA * sims, dim=0)


def train_phase_a(byte_atoms, pos_atoms, train_bytes, total_cells, base_cell_offset):
    """Standard substrate training: train W on (context, target) pairs from byte stream."""
    W = torch.zeros((N, N), device=DEVICE)
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offs = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offs.unsqueeze(0)]
    tgt = bt[pos + K]
    batch_size = 64
    for epoch in range(1, MAX_EPOCHS + 1):
        for bs in range(0, T, batch_size):
            be = min(bs + batch_size, T)
            B_ = be - bs
            ctxs = build_ctx(byte_atoms, pos_atoms, idx[bs:be])
            t = tgt[bs:be]
            with torch.no_grad():
                q = relu_shift(ctxs @ W.T, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                resid = byte_atoms[t] - (P.T @ byte_atoms)
                dW = (resid.T @ ctxs) / N
                W.mul_(1.0 - DECAY)
                W.add_(dW, alpha=ALPHA_TRAIN)
        prog_update("training",
                    cell=base_cell_offset + epoch,
                    total_cells=total_cells)
    return W


def antihebbian_rank1_erase(W, key_vec):
    """Apply W -= alpha * (W @ k) k^T / d. Returns new W.

    For random ±1 keys, k^T k = d so C^-1 ≈ I/d. The full formula
    W -= alpha * (W @ k)(k^T C^-1) / (k^T C^-1 k) simplifies to this.
    """
    Wk = W @ key_vec               # (N,)
    k_norm_sq = float((key_vec * key_vec).sum())  # ≈ N for ±1 keys
    update = torch.outer(Wk, key_vec) / k_norm_sq
    return W - ALPHA_ERASE * update


def predict_correct_for(W, byte_atoms, pos_atoms, facts):
    """For each fact (ctx_idx, target_byte): does W predict the target?"""
    correct = 0
    for ctx_idx, tgt in facts:
        p = predict_byte(W, byte_atoms, pos_atoms, ctx_idx)
        if int(p.argmax().item()) == tgt:
            correct += 1
    return correct


def load_corpus():
    """Use the project README + key docs as a real byte corpus."""
    repo = Path(__file__).resolve().parent.parent
    files = [repo / "PLAN.md", repo / "README.md", repo / "CLAUDE.md",
              repo / "NEXT_PHASE.md"]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


def synthesize_facts_from_corpus(corpus, byte_atoms, pos_atoms, n_facts, gen):
    """Pick n_facts random (K-byte prefix, next-byte) pairs from corpus."""
    pad = bytes([PAD_BYTE]) * K
    padded = pad + corpus
    T = len(padded) - K
    facts = []
    used = set()
    bt = torch.tensor(list(padded), dtype=torch.long)
    while len(facts) < n_facts and len(used) < T:
        i = int(torch.randint(0, T, (1,), generator=gen).item())
        if i in used:
            continue
        used.add(i)
        offs = torch.arange(K - 1, -1, -1)
        prefix_idx = bt[i + offs].to(DEVICE)
        target = int(bt[i + K].item())
        facts.append((prefix_idx, target))
    return facts


def run_seed(seed, total_seeds, seed_idx):
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc(K, N, gen).to(DEVICE)
    corpus = load_corpus()
    split = int(0.8 * len(corpus))
    train_bytes = corpus[:split]

    # Training cells per seed: MAX_EPOCHS, plus 4 evaluation phases
    cells_per_seed = MAX_EPOCHS + 4
    base_cell = seed_idx * cells_per_seed

    # Train W
    W_trained = train_phase_a(byte_atoms, pos_atoms, train_bytes,
                              total_cells=total_seeds * cells_per_seed,
                              base_cell_offset=base_cell)

    # Pick facts from the corpus
    fact_gen = torch.Generator().manual_seed(seed + 100)
    facts = synthesize_facts_from_corpus(corpus, byte_atoms, pos_atoms,
                                          N_FACTS, fact_gen)

    # Baseline: how many facts does W predict correctly?
    baseline_correct = predict_correct_for(W_trained, byte_atoms, pos_atoms, facts)
    prog_update("evaluating", cell=base_cell + MAX_EPOCHS + 1,
                total_cells=total_seeds * cells_per_seed,
                phase_detail=f"seed={seed} baseline")

    # Pick 10 facts to "erase"
    erase_gen = torch.Generator().manual_seed(seed * 7)
    erase_idx_list = torch.randperm(len(facts), generator=erase_gen)[:N_ERASURES].tolist()
    erased_facts = [facts[i] for i in erase_idx_list]
    kept_facts = [f for i, f in enumerate(facts) if i not in erase_idx_list]

    # Method A: pool-zero only (no W change). Result: W still has the patterns.
    W_method_A = W_trained.clone()
    # (Pool zeroing has no effect on W; W still leaks)
    leak_A = predict_correct_for(W_method_A, byte_atoms, pos_atoms, erased_facts)
    kept_A = predict_correct_for(W_method_A, byte_atoms, pos_atoms, kept_facts)
    prog_update("evaluating", cell=base_cell + MAX_EPOCHS + 2,
                total_cells=total_seeds * cells_per_seed,
                phase_detail=f"seed={seed} method_A")

    # Method B: pool-zero + anti-Hebbian rank-1 W update per erased fact
    W_method_B = W_trained.clone()
    for ctx_idx, tgt in erased_facts:
        key_vec = build_ctx(byte_atoms, pos_atoms, ctx_idx.unsqueeze(0)).squeeze(0)
        W_method_B = antihebbian_rank1_erase(W_method_B, key_vec)
    leak_B = predict_correct_for(W_method_B, byte_atoms, pos_atoms, erased_facts)
    kept_B = predict_correct_for(W_method_B, byte_atoms, pos_atoms, kept_facts)
    prog_update("evaluating", cell=base_cell + MAX_EPOCHS + 3,
                total_cells=total_seeds * cells_per_seed,
                phase_detail=f"seed={seed} method_B")

    return {
        "seed": seed,
        "n_facts": len(facts),
        "n_kept": len(kept_facts),
        "n_erased": len(erased_facts),
        "baseline_predict_correct": baseline_correct,
        "method_A_leak_correct": leak_A,
        "method_A_kept_correct": kept_A,
        "method_B_leak_correct": leak_B,
        "method_B_kept_correct": kept_B,
        "method_A_leak_rate": leak_A / max(1, len(erased_facts)),
        "method_B_leak_rate": leak_B / max(1, len(erased_facts)),
        "method_A_kept_recall": kept_A / max(1, len(kept_facts)),
        "method_B_kept_recall": kept_B / max(1, len(kept_facts)),
    }


def main():
    print(f"W-side anti-Hebbian erase probe. K={K}, N={N}, device={DEVICE}", flush=True)
    print(f"Method A = pool zero only (status quo). Method B = pool zero + anti-Hebbian.", flush=True)
    prog_reset()
    t0 = time.monotonic()
    grid = []
    for seed_idx, seed in enumerate(SEEDS):
        r = run_seed(seed, len(SEEDS), seed_idx)
        grid.append(r)
        print(f"  seed={seed}  baseline={r['baseline_predict_correct']}/{r['n_facts']}  "
              f"A_leak={r['method_A_leak_rate']:.2f} A_kept={r['method_A_kept_recall']:.2f}  "
              f"B_leak={r['method_B_leak_rate']:.2f} B_kept={r['method_B_kept_recall']:.2f}",
              flush=True)
    elapsed = time.monotonic() - t0

    # Aggregate
    A_leak = sum(r["method_A_leak_rate"] for r in grid) / len(grid)
    B_leak = sum(r["method_B_leak_rate"] for r in grid) / len(grid)
    A_kept = sum(r["method_A_kept_recall"] for r in grid) / len(grid)
    B_kept = sum(r["method_B_kept_recall"] for r in grid) / len(grid)
    leak_reduction_pp = (A_leak - B_leak) * 100  # percentage points

    print(f"\n=== AGGREGATE ===")
    print(f"  Method A leak: {A_leak:.2%}  kept_recall: {A_kept:.2%}")
    print(f"  Method B leak: {B_leak:.2%}  kept_recall: {B_kept:.2%}")
    print(f"  Leak reduction: {leak_reduction_pp:.1f} percentage points")
    print(f"  Collateral damage on kept: {(A_kept-B_kept)*100:.1f} pp")

    if leak_reduction_pp >= 50 and B_kept >= 0.80:
        verdict = "ANTIHEBBIAN_ERASE_WORKS"
        msg = (f"Method B reduces leak by {leak_reduction_pp:.1f}pp with kept_recall {B_kept:.0%}. "
               f"GDPR substrate fix validated.")
    elif leak_reduction_pp >= 30:
        verdict = "ANTIHEBBIAN_ERASE_PARTIAL"
        msg = f"Leak reduction {leak_reduction_pp:.1f}pp is positive but below 50pp threshold."
    else:
        verdict = "ANTIHEBBIAN_ERASE_FAILED"
        msg = f"Leak reduction only {leak_reduction_pp:.1f}pp. Math-based fix is not sufficient as written."

    print(f"\n=== {verdict} ===\n{msg}")

    out = Path(__file__).resolve().parent.parent / "data" / "exp_wave14h_wside_erase"
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps({
        "K": K, "N": N, "N_FACTS": N_FACTS, "N_ERASURES": N_ERASURES,
        "ALPHA_ERASE": ALPHA_ERASE, "SEEDS": SEEDS, "device": str(DEVICE),
        "elapsed_s": elapsed, "grid": grid,
        "summary": {
            "method_A_leak_mean": A_leak, "method_B_leak_mean": B_leak,
            "method_A_kept_mean": A_kept, "method_B_kept_mean": B_kept,
            "leak_reduction_pp": leak_reduction_pp,
        },
        "verdict": verdict, "verdict_msg": msg,
    }, indent=2))
    print(f"\nwrote {out / 'metrics.json'}")


if __name__ == "__main__":
    main()
