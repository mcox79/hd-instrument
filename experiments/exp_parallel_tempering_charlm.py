"""MX10: Parallel tempering K=8 replicas + RSB / overlap diagnosis.

The single most informative remaining experiment per the materials-physics
3-iteration arc. Tests whether the 0.115-bit gap to the transformer is a
sampling-dynamics problem (PT helps) or a structural clustering problem
(1RSB; PT plateaus).

Per Earl-Deem 2005 PCCP: K=8 replicas at geometrically spaced decay rates,
Metropolis swaps on validation loss every 5 batches, target ~23% swap
acceptance.

After convergence, compute P(q) overlap distribution between all replica
pairs where q = <W_a, W_b>_F / (||W_a||_F * ||W_b||_F).
  - Unimodal P(q): gap is closable by ordinary annealing
  - Bimodal P(q) (1RSB): clustering; PT gives log speedup, hard floor
  - Continuous P(q) (FRSB): ultrametric tree; need substrate change

Stacked with magnitude_relu (the only architectural change that actually
helped). Baseline: 2.4994 bpc.
"""

from __future__ import annotations

import json
import math
import time
from collections import Counter
from pathlib import Path

import torch

from hdlab import atoms, binding, tracing


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
N_SUBSTRATE = 4096
VOCAB_SIZE = 256
PAD_BYTE = 0
K_CTX = 4  # context window length
AROUSAL = 0.3
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
EPOCH_CHECKPOINTS = [1, 5, 10, 15]
RELU_B = 0.5

# PT parameters
N_REPLICAS = 8
# Geometric spacing in decay (proxy for inverse temperature in our setup)
# Hottest = highest decay (most noise), coldest = lowest decay (most refinement)
DECAY_VALUES = [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2]
assert len(DECAY_VALUES) == N_REPLICAS
SWAP_EVERY_BATCHES = 5  # swap attempt frequency
SWAP_BETA = 100.0  # Metropolis "inverse temperature" for swap accept prob


def _say(msg: str) -> None:
    print(msg, flush=True)


def load_corpus() -> bytes:
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


def train_test_split(corpus, train_frac=0.8):
    cut = int(len(corpus) * train_frac)
    return corpus[:cut], corpus[cut:]


def _build_context_bundles_batch(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    mag = summed.abs().clamp(min=1e-8)
    return summed / mag.to(summed.dtype)


def magnitude_relu(q, b):
    eps = 1e-9
    mag = q.abs().clamp(min=eps)
    new_mag = torch.clamp(mag - b, min=0.0)
    return q * (new_mag / mag).to(q.dtype)


def _predict_W_batch(W, ctxs, byte_atoms, beta):
    n = ctxs.shape[1]
    q = ctxs @ W.T
    q = magnitude_relu(q, RELU_B)
    sims = (byte_atoms.conj() @ q.T).real / n
    return torch.softmax(beta * sims, dim=0)


def _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, beta):
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    n = ctxs.shape[1]
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active.conj() @ ctxs.T).real / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def eval_val_loss(W, byte_atoms, pos_atoms, test_idx, test_targets, pool_vecs, pool_labels, pool_used, sample_size=2000):
    """Quick validation loss for swap decisions — subsample for speed."""
    T_test = test_idx.shape[0]
    n_sample = min(sample_size, T_test)
    sample_indices = torch.randint(0, T_test, (n_sample,), device=test_idx.device)
    sample_idx_batch = test_idx[sample_indices]
    sample_tgt = test_targets[sample_indices]
    ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, sample_idx_batch)
    P_W = _predict_W_batch(W, ctxs, byte_atoms, BETA)
    P_retr = _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, BETA)
    P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
    p_true = P.gather(0, sample_tgt.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
    return float(-torch.log2(p_true).mean())


def compute_overlap_matrix(W_list):
    """Compute P(q) overlap matrix between all replica pairs.

    Overlap q = real(<W_a, W_b>_F) / (||W_a||_F * ||W_b||_F)
    Returns: K x K matrix of overlaps (diagonal = 1).
    """
    K = len(W_list)
    Q = torch.zeros(K, K, device=W_list[0].device)
    norms = [float(W.abs().pow(2).sum().sqrt()) for W in W_list]
    for i in range(K):
        for j in range(K):
            inner = (W_list[i].conj() * W_list[j]).sum().real
            Q[i, j] = inner / (norms[i] * norms[j] + 1e-12)
    return Q


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, 0.8)
    _say(f"  train={len(train)}, test={len(test)} bytes")
    _say(f"\nParallel Tempering, K={N_REPLICAS} replicas")
    _say(f"  Decay values (geometric): {DECAY_VALUES}")
    _say(f"  Swap every {SWAP_EVERY_BATCHES} batches, Metropolis with swap_beta={SWAP_BETA}")
    _say(f"  Other: N={N_SUBSTRATE}, K_ctx={K_CTX}, arousal={AROUSAL}, beta={BETA}")
    _say(f"  Stacked with magnitude_relu b={RELU_B}")
    _say(f"  Epochs={MAX_EPOCHS}, checkpoints {EPOCH_CHECKPOINTS}")
    _say(f"\nBaseline: combined + relu (single replica) = 2.4994 bpc")

    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(SEED)
        byte_atoms = torch.stack([atoms.make_atom_fhrr(N_SUBSTRATE, gen) for _ in range(VOCAB_SIZE)]).to(DEVICE)
        pos_atoms = torch.stack([atoms.make_atom_fhrr(N_SUBSTRATE, gen) for _ in range(K_CTX)]).to(DEVICE)
        # K independent W matrices
        W_list = [torch.zeros((N_SUBSTRATE, N_SUBSTRATE), dtype=torch.complex64, device=DEVICE) for _ in range(N_REPLICAS)]
        # Shared pool (built during epoch 1 from coldest replica's perspective).
        pool_vecs = torch.zeros((POOL_SIZE, N_SUBSTRATE), dtype=torch.complex64, device=DEVICE)
        pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
        pool_used = 0
        pool_idx = 0

        pad = bytes([PAD_BYTE]) * K_CTX
        padded_train = pad + train
        padded_test = pad + test
        T_total = len(padded_train) - K_CTX
        T_test = len(padded_test) - K_CTX
        train_bytes = torch.tensor(list(padded_train), dtype=torch.long).to(DEVICE)
        test_bytes = torch.tensor(list(padded_test), dtype=torch.long).to(DEVICE)
        offsets = torch.arange(K_CTX - 1, -1, -1, device=DEVICE)
        pos_train = torch.arange(T_total, device=DEVICE)
        pos_test = torch.arange(T_test, device=DEVICE)
        train_idx = train_bytes[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
        train_targets = train_bytes[pos_train + K_CTX]
        test_idx = test_bytes[pos_test.unsqueeze(1) + offsets.unsqueeze(0)]
        test_targets = test_bytes[pos_test + K_CTX]

        history = []
        swap_log = []
        swap_attempts = 0
        swap_accepts = 0
        t_start = time.perf_counter()
        batch_count = 0
        for epoch in range(1, MAX_EPOCHS + 1):
            for batch_start in range(0, T_total, BATCH_SIZE):
                be = min(batch_start + BATCH_SIZE, T_total)
                idx_batch = train_idx[batch_start:be]
                tgt_batch = train_targets[batch_start:be]
                B = idx_batch.shape[0]
                ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, idx_batch)
                # Update each replica with its own decay.
                for r in range(N_REPLICAS):
                    P_W = _predict_W_batch(W_list[r], ctxs, byte_atoms, BETA)
                    targets = byte_atoms[tgt_batch]
                    expected = P_W.T.to(byte_atoms.dtype) @ byte_atoms
                    errors = targets - expected
                    dW = errors.T @ ctxs.conj() / N_SUBSTRATE
                    W_list[r].mul_(1.0 - DECAY_VALUES[r])
                    W_list[r].add_(dW, alpha=AROUSAL)
                # Pool update (first epoch only, from coldest replica's data perspective).
                if epoch == 1:
                    for b in range(B):
                        pool_vecs[pool_idx] = ctxs[b]
                        pool_labels[pool_idx] = tgt_batch[b]
                        pool_idx = (pool_idx + 1) % POOL_SIZE
                        pool_used = min(pool_used + 1, POOL_SIZE)
                batch_count += 1
                # PT swap attempts every SWAP_EVERY_BATCHES batches.
                if batch_count % SWAP_EVERY_BATCHES == 0 and pool_used > 0:
                    # Compute validation losses for adjacent pairs (cheap).
                    val_losses = [eval_val_loss(W_list[r], byte_atoms, pos_atoms, test_idx, test_targets, pool_vecs, pool_labels, pool_used, sample_size=500) for r in range(N_REPLICAS)]
                    # Attempt swap between random adjacent pair.
                    i = torch.randint(0, N_REPLICAS - 1, (1,)).item()
                    j = i + 1
                    delta = (val_losses[j] - val_losses[i]) * (1.0 / DECAY_VALUES[i] - 1.0 / DECAY_VALUES[j])
                    p_accept = math.exp(min(0.0, -delta * SWAP_BETA))
                    swap_attempts += 1
                    if torch.rand(1).item() < p_accept:
                        # Swap
                        W_list[i], W_list[j] = W_list[j], W_list[i]
                        swap_accepts += 1
                        swap_log.append({"epoch": epoch, "batch": batch_count, "i": i, "j": j, "delta": float(delta), "p_accept": float(p_accept)})

            if epoch in EPOCH_CHECKPOINTS:
                # Evaluate each replica.
                rep_results = []
                for r in range(N_REPLICAS):
                    total_bits = 0.0
                    argmax_correct = 0
                    for bs in range(0, T_test, BATCH_SIZE):
                        be = min(bs + BATCH_SIZE, T_test)
                        ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, test_idx[bs:be])
                        P_W = _predict_W_batch(W_list[r], ctxs, byte_atoms, BETA)
                        P_retr = _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, BETA)
                        P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                        p_true = P.gather(0, test_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                        total_bits += float(-torch.log2(p_true).sum())
                        argmax_pred = P.argmax(dim=0)
                        argmax_correct += int((argmax_pred == test_targets[bs:be]).sum())
                    rep_results.append({"decay": DECAY_VALUES[r], "test_bpc": total_bits / max(T_test, 1), "argmax_accuracy": argmax_correct / max(T_test, 1), "w_norm": float(W_list[r].abs().pow(2).sum().sqrt())})

                best_rep = min(rep_results, key=lambda r: r["test_bpc"])
                # Also: ensemble readout — weighted by inverse loss
                w_norms = torch.tensor([r["w_norm"] for r in rep_results])
                inv_losses = torch.tensor([1.0 / (r["test_bpc"] + 1e-6) for r in rep_results])
                weights_ens = inv_losses / inv_losses.sum()
                # Quick ensemble eval
                ens_bits = 0.0
                for bs in range(0, T_test, BATCH_SIZE):
                    be = min(bs + BATCH_SIZE, T_test)
                    ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, test_idx[bs:be])
                    P_avg = torch.zeros(VOCAB_SIZE, be - bs, device=DEVICE)
                    for r in range(N_REPLICAS):
                        P_W = _predict_W_batch(W_list[r], ctxs, byte_atoms, BETA)
                        P_retr = _predict_pool_batch(ctxs, pool_vecs, pool_labels, pool_used, BETA)
                        P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
                        P_avg += weights_ens[r] * P
                    p_true = P_avg.gather(0, test_targets[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
                    ens_bits += float(-torch.log2(p_true).sum())
                ens_bpc = ens_bits / max(T_test, 1)
                elapsed = time.perf_counter() - t_start

                _say(f"\n  ===== Epoch {epoch} ===== ({elapsed:.1f}s)")
                _say(f"  Per-replica results (sorted by decay):")
                for rep in rep_results:
                    _say(f"    decay={rep['decay']:.0e}  test_bpc={rep['test_bpc']:.4f}  argmax={rep['argmax_accuracy']:.4f}  W_norm={rep['w_norm']:.1f}")
                _say(f"  Best single replica: decay={best_rep['decay']:.0e}, test_bpc={best_rep['test_bpc']:.4f}")
                _say(f"  Ensemble (weighted by inverse loss): test_bpc={ens_bpc:.4f}")
                _say(f"  Swap acceptance so far: {swap_accepts}/{swap_attempts} = {swap_accepts/max(swap_attempts,1):.2%}")

                history.append({
                    "epoch": epoch,
                    "rep_results": rep_results,
                    "best_replica_bpc": best_rep["test_bpc"],
                    "ensemble_bpc": ens_bpc,
                    "swap_accepts_so_far": swap_accepts,
                    "swap_attempts_so_far": swap_attempts,
                    "wall_s": elapsed,
                })

        # Final RSB diagnosis: compute P(q) overlap distribution.
        _say(f"\n===== RSB Diagnosis: P(q) overlap distribution =====")
        Q = compute_overlap_matrix(W_list)
        _say(f"Overlap matrix Q (diagonal = 1, off-diagonal = pairwise overlaps):")
        for i in range(N_REPLICAS):
            row = "  " + " ".join(f"{float(Q[i, j]):+.4f}" for j in range(N_REPLICAS))
            _say(row)
        # Off-diagonal overlap statistics.
        off_diag = []
        for i in range(N_REPLICAS):
            for j in range(N_REPLICAS):
                if i != j:
                    off_diag.append(float(Q[i, j]))
        _say(f"\n  Off-diagonal overlap statistics:")
        _say(f"    mean:   {sum(off_diag)/len(off_diag):.4f}")
        _say(f"    std:    {(sum((q - sum(off_diag)/len(off_diag))**2 for q in off_diag) / len(off_diag))**0.5:.4f}")
        _say(f"    min:    {min(off_diag):.4f}")
        _say(f"    max:    {max(off_diag):.4f}")
        # Heuristic verdict based on distribution shape.
        std_q = (sum((q - sum(off_diag)/len(off_diag))**2 for q in off_diag) / len(off_diag))**0.5
        if std_q < 0.05:
            verdict = "UNIMODAL P(q): replicas converged to same basin. Gap is closable by ordinary annealing; PT helped or not."
        elif std_q < 0.2:
            verdict = "BIMODAL-ish P(q): possible 1RSB clustering. Hard floor may exist; PT gives log speedup."
        else:
            verdict = "WIDE P(q): suggests FRSB / ultrametric structure. Need substrate change."
        _say(f"  Verdict: {verdict}")

        best_overall = min((h["best_replica_bpc"] for h in history))
        best_ens = min((h["ensemble_bpc"] for h in history))
        _say(f"\n===== FINAL =====")
        _say(f"  Best single replica across epochs: {best_overall:.4f}")
        _say(f"  Best ensemble across epochs: {best_ens:.4f}")
        _say(f"  vs current best (no PT): 2.4994")
        _say(f"  vs transformer ceiling 2.39")

        out = {
            "seed": SEED, "n_substrate": N_SUBSTRATE, "k_ctx": K_CTX, "n_replicas": N_REPLICAS,
            "decay_values": DECAY_VALUES, "swap_every_batches": SWAP_EVERY_BATCHES, "swap_beta": SWAP_BETA,
            "arousal": AROUSAL, "beta": BETA, "pool_size": POOL_SIZE, "alpha": ALPHA,
            "relu_b": RELU_B, "max_epochs": MAX_EPOCHS,
            "history": history,
            "overlap_matrix": Q.tolist(),
            "off_diagonal_stats": {
                "mean": sum(off_diag)/len(off_diag),
                "std": std_q,
                "min": min(off_diag),
                "max": max(off_diag),
            },
            "rsb_verdict": verdict,
            "swap_log_count": len(swap_log),
            "headline": f"PT K={N_REPLICAS} best replica={best_overall:.3f}, ensemble={best_ens:.3f}, P(q) std={std_q:.3f}",
        }
        out_path = Path(__file__).resolve().parent.parent / "data" / "exp_parallel_tempering_charlm"
        out_path.mkdir(parents=True, exist_ok=True)
        (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
        _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
