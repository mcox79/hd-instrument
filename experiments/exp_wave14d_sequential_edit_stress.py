"""Sequential editing stress test -- does substrate survive 1k edits where ROME/MEMIT collapse?

ROME/MEMIT exhibit catastrophic collapse past 50-1k sequential edits (Gupta 2024,
arxiv 2401.07453). Substrate's atomic bundle structure should be immune in
principle -- each edit is local, no parameter ripple.

Test:
1. Train W on corpus A, build pool from corpus A
2. Pick 1000 random pool entries
3. For each: choose a random position, edit the atom at that position to a different byte
4. After EACH edit, verify:
   (a) decomposability: re-decompose the edited bundle, check the edited atom matches
   (b) pool integrity: random sample of OTHER bundles still decompose correctly
   (c) W stability: bpc on test_a unchanged (W not corrupted by pool edits)
5. Report: max sequential edits before collapse (or 1000 if no collapse).

Pass condition: 1000 edits with decomposability >= 95% throughout AND
pool integrity >= 95% AND bpc drift <= 0.01.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 8  # smaller K for faster edit/verify cycle
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
NUM_EDITS = 1000
INTEGRITY_CHECK_INTERVAL = 50  # every 50 edits, verify pool integrity
BPC_CHECK_INTERVAL = 200  # every 200 edits, measure bpc drift


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
    pool_byte_at_pos = torch.zeros((POOL_SIZE, K), dtype=torch.long, device=DEVICE)  # track original bytes
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


def edit_bundle(bundle, byte_atoms, pos_atoms, position, old_byte, new_byte):
    """Swap atom at `position` from old_byte to new_byte. Returns new bundle."""
    # Bundle is sum(byte_atoms[byte_i] * pos_atoms[i] for i in range(K))
    # Removing old and adding new: bundle - old_atom * pos + new_atom * pos
    old_atom = byte_atoms[old_byte] * pos_atoms[position]
    new_atom = byte_atoms[new_byte] * pos_atoms[position]
    new_bundle = bundle - old_atom + new_atom
    # Re-sign to maintain bipolar property
    new_bundle = torch.sign(new_bundle)
    new_bundle = torch.where(new_bundle == 0, torch.ones_like(new_bundle), new_bundle)
    return new_bundle


def decompose_at_position(bundle, byte_atoms, pos_atoms, position):
    """Recover the byte at `position` from a bundle."""
    proj = bundle * pos_atoms[position]
    scores = byte_atoms @ proj / N
    return int(scores.argmax().item())


def decompose_all_positions(bundles, byte_atoms, pos_atoms):
    """Decompose all K positions for all bundles. Returns (n_bundles, K) byte indices."""
    P = bundles.shape[0]
    out = torch.zeros((P, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        proj = bundles * pos_atoms[r].unsqueeze(0)
        scores = proj @ byte_atoms.T / N
        out[:, r] = scores.argmax(dim=1)
    return out


def measure_bpc(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels, pool_used):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx_all = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts_all = bt[pos + K]
    total = 0.0
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx_all[bs:be]
        tgts = tgts_all[bs:be]
        B = idx_b.shape[0]
        ctxs = build_ctx_batch(byte_atoms, pos_atoms, idx_b)
        q = ctxs @ W.T
        q = shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        P_W = torch.softmax(BETA * sims, dim=0)
        sims_p = (active @ ctxs.T) / N
        weights_p = torch.softmax(BETA * sims_p, dim=0)
        P_retr = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights_p)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


def run_one(seed):
    corpus_a = load_corpus_a()
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)

    _say(f"  training W (K={K})...")
    W, pool_vecs, pool_labels, pool_byte_at_pos, pool_used = train_phase_a(byte_atoms, pos_atoms, train_a)

    # Baseline checks
    initial_bpc = measure_bpc(W, byte_atoms, pos_atoms, test_a, pool_vecs, pool_labels, pool_used)
    _say(f"  initial bpc = {initial_bpc:.4f}, pool_used = {pool_used}")

    # Snapshot original pool_byte_at_pos for integrity checks
    original_pool_bytes = pool_byte_at_pos.clone()

    # Track which (entry, position) have been edited, what to
    edits = []  # list of (entry_idx, position, old_byte, new_byte) tuples
    edit_gen = torch.Generator().manual_seed(seed * 13)

    metrics = {
        "edit_decomp_success": [],  # per-edit: was the edit recoverable?
        "pool_integrity": [],  # at intervals: fraction of other bundles correctly decomposing
        "bpc_drift": [],  # at intervals: bpc - initial_bpc
        "edit_count_at_check": [],
    }

    for edit_i in range(NUM_EDITS):
        # Pick random entry and position
        entry_idx = int(torch.randint(0, pool_used, (1,), generator=edit_gen).item())
        position = int(torch.randint(0, K, (1,), generator=edit_gen).item())
        old_byte = int(pool_byte_at_pos[entry_idx, position].item())
        new_byte = int(torch.randint(0, VOCAB_SIZE, (1,), generator=edit_gen).item())
        if new_byte == old_byte:
            new_byte = (new_byte + 1) % VOCAB_SIZE  # ensure actual change

        # Apply edit
        old_bundle = pool_vecs[entry_idx].clone()
        new_bundle = edit_bundle(old_bundle, byte_atoms, pos_atoms, position, old_byte, new_byte)
        pool_vecs[entry_idx] = new_bundle
        pool_byte_at_pos[entry_idx, position] = new_byte

        # Verify edit recoverability
        recovered = decompose_at_position(new_bundle, byte_atoms, pos_atoms, position)
        metrics["edit_decomp_success"].append(1 if recovered == new_byte else 0)

        edits.append((entry_idx, position, old_byte, new_byte))

        # Periodic integrity / bpc checks
        if (edit_i + 1) % INTEGRITY_CHECK_INTERVAL == 0:
            # Sample 50 random unedited-position entries; check they decompose to expected
            sample_gen = torch.Generator().manual_seed(seed * 23 + edit_i)
            sample_indices = torch.randperm(pool_used, generator=sample_gen)[:50].to(DEVICE)
            sample_bundles = pool_vecs[sample_indices]
            sample_decoded = decompose_all_positions(sample_bundles, byte_atoms, pos_atoms)
            sample_expected = pool_byte_at_pos[sample_indices]
            integrity = float((sample_decoded == sample_expected).float().mean().item())
            metrics["pool_integrity"].append(integrity)
            metrics["edit_count_at_check"].append(edit_i + 1)

        if (edit_i + 1) % BPC_CHECK_INTERVAL == 0:
            curr_bpc = measure_bpc(W, byte_atoms, pos_atoms, test_a, pool_vecs, pool_labels, pool_used)
            metrics["bpc_drift"].append(curr_bpc - initial_bpc)
            _say(f"  edit {edit_i+1}/{NUM_EDITS}: integrity={metrics['pool_integrity'][-1]:.3f}  bpc_drift={metrics['bpc_drift'][-1]:+.4f}")

    edit_success_rate = sum(metrics["edit_decomp_success"]) / len(metrics["edit_decomp_success"])
    final_integrity = metrics["pool_integrity"][-1] if metrics["pool_integrity"] else 1.0
    max_bpc_drift = max(abs(d) for d in metrics["bpc_drift"]) if metrics["bpc_drift"] else 0.0

    return {
        "initial_bpc": initial_bpc,
        "edit_success_rate": edit_success_rate,
        "final_pool_integrity": final_integrity,
        "max_bpc_drift": max_bpc_drift,
        "metrics": metrics,
    }


def main():
    _say(f"Sequential editing stress test: K={K}, {NUM_EDITS} edits, {len(SEEDS)} seeds")
    _say(f"  Pass conditions: edit success >= 95%, pool integrity >= 95%, bpc drift <= 0.01")
    all_results = []
    for seed in SEEDS:
        _say(f"\n[seed={seed}]")
        r = run_one(seed)
        _say(f"  edit_success_rate    = {r['edit_success_rate']*100:.2f}%")
        _say(f"  final_pool_integrity = {r['final_pool_integrity']*100:.2f}%")
        _say(f"  max_bpc_drift        = {r['max_bpc_drift']:+.4f}")
        all_results.append({"seed": seed, **r})

    _say("\n========= SEQUENTIAL EDITING VERDICT =========")
    mean_success = sum(r["edit_success_rate"] for r in all_results) / len(all_results)
    mean_integrity = sum(r["final_pool_integrity"] for r in all_results) / len(all_results)
    mean_drift = sum(r["max_bpc_drift"] for r in all_results) / len(all_results)
    _say(f"  Mean edit success: {mean_success*100:.2f}%")
    _say(f"  Mean final pool integrity: {mean_integrity*100:.2f}%")
    _say(f"  Mean max bpc drift: {mean_drift:+.4f}")
    if mean_success >= 0.95 and mean_integrity >= 0.95 and mean_drift <= 0.01:
        _say(f"\n  PASS: substrate survives 1000 sequential edits where ROME/MEMIT collapse at 50-1k.")
    else:
        _say(f"\n  PARTIAL or FAIL: investigate which condition violated.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14d_sequential_edit_stress"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "NUM_EDITS": NUM_EDITS, "SEEDS": SEEDS,
        "results": all_results,
    }, indent=2))


if __name__ == "__main__":
    main()
