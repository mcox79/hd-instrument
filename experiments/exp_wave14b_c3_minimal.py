"""Wave 14.B C3 minimal: simplest possible compositional retrieval test.

Standard pool retrieval scores ctx against stored bundle by full cosine
similarity. C3's idea: match by SUBSET of positions only, then use the
unmatched positions to extract the "filled in" prediction from the
retrieved bundles.

Minimal version:
- Score by similarity of ctx restricted to positions {0, 1, 2} (drop pos 3)
- From retrieved bundle, extract position 3's contribution via 14.B
  (multiply by pos_atoms[3] to get position-3 atom in noise)
- Project to byte codebook -> P(byte at position 3 | partial ctx match)
- Compare to C1 (whole-ctx similarity, explicit label lookup)

If C3 beats C1 here, partial matching adds real information. If equal
or worse, the substrate's compositional retrieval doesn't help on this
task (byte-LM might not be compositional enough to benefit).

Same data + state as Phase B.2 (load state.pt). Compares C1, C2, C3
on the same pool, same W, same test set.
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
BETA = 8.0
BYTE_BETA = 16.0
BATCH_SIZE = 64
ALPHA = 0.3
MAX_EPOCHS_B = 15
EVAL_AT = [15]
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
# Which positions to use for partial matching in C3 (others are "wildcards")
C3_MATCH_POSITIONS = [0, 1, 2]  # match by positions 0-2, treat 3 as fill-in


def _say(msg: str) -> None:
    print(msg, flush=True)


def build_ctx_bundles_bsc(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def build_ctx_partial(byte_atoms, pos_atoms, indices, positions_to_use):
    """Like build_ctx_bundles_bsc but only sums over positions_to_use.
    Used for C3 query construction to mask out wildcards."""
    pos_mask = pos_atoms[positions_to_use].unsqueeze(0)  # (1, |used|, N)
    bound = byte_atoms[indices][:, positions_to_use, :] * pos_mask
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
    return P_byte_per_entry.T @ weights


def predict_pool_c3_partial(ctxs_partial, vsa_bundles, vsa_used,
                            target_pos, byte_atoms,
                            beta_retrieval, beta_byte, n):
    """C3: score by partial ctx (subset of positions), extract target via 14.B.

    ctxs_partial is built from C3_MATCH_POSITIONS only — wildcards excluded.
    Match against vsa_bundles (which contain ALL positions); the wildcard
    contribution acts as additional noise that's the same across all
    pool entries, hence cancels in the relative scoring.
    """
    B = ctxs_partial.shape[0]
    if vsa_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs_partial.device)
    active = vsa_bundles[:vsa_used]
    # Score: partial-ctx similarity to whole stored bundle.
    # The "missing" positions and target term in bundle act as noise that
    # is uncorrelated with the partial-ctx query. Match drives signal.
    sims = (active @ ctxs_partial.T) / n
    weights = torch.softmax(beta_retrieval * sims, dim=0)
    # Extract target estimates from retrieved bundles (same as C2)
    target_estimates = active * target_pos.unsqueeze(0)
    byte_scores = (target_estimates @ byte_atoms.T) / n
    P_byte_per_entry = torch.softmax(beta_byte * byte_scores, dim=1)
    return P_byte_per_entry.T @ weights


def eval_all(W, byte_atoms, pos_atoms, test_idx, test_targets,
            pool_vecs, pool_labels, pool_used,
            vsa_bundles, vsa_used, target_pos, alpha):
    T_test = test_idx.shape[0]
    bits = {"c0": 0.0, "c1": 0.0, "c2": 0.0, "c3": 0.0}
    for bs in range(0, T_test, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T_test)
        ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_idx[bs:be])
        ctxs_partial = build_ctx_partial(byte_atoms, pos_atoms, test_idx[bs:be],
                                          C3_MATCH_POSITIONS)
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
        tgts = test_targets[bs:be]
        # C0
        p_c0 = P_W.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits["c0"] += float(-torch.log2(p_c0).sum())
        # C1
        P_c = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
        P_1 = alpha * P_c + (1 - alpha) * P_W
        bits["c1"] += float(-torch.log2(P_1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
        # C2
        P_v = predict_pool_vsa(ctxs, vsa_bundles, vsa_used, target_pos, byte_atoms,
                              BETA, BYTE_BETA, N)
        P_2 = alpha * P_v + (1 - alpha) * P_W
        bits["c2"] += float(-torch.log2(P_2.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
        # C3: partial-ctx match
        P_3v = predict_pool_c3_partial(ctxs_partial, vsa_bundles, vsa_used, target_pos,
                                       byte_atoms, BETA, BYTE_BETA, N)
        P_3 = alpha * P_3v + (1 - alpha) * P_W
        bits["c3"] += float(-torch.log2(P_3.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)).sum())
    return {k: v / max(T_test, 1) for k, v in bits.items()}


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
    return pool_vecs[:pool_used] + target_atoms * target_pos.unsqueeze(0)


def main():
    _say(f"Wave 14.B C3 minimal: partial-ctx compositional retrieval")
    _say(f"  Match positions: {C3_MATCH_POSITIONS} (drop pos 3 = wildcard)")

    state_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cl_phase_a" / "state.pt"
    state = torch.load(state_path, weights_only=False)

    W = state["W_A"].to(DEVICE).clone()
    pool_vecs = state["pool_vecs_A"].to(DEVICE)
    pool_labels = state["pool_labels_A"].to(DEVICE)
    pool_used = int(state["pool_used_A"])
    byte_atoms = state["byte_atoms"].to(DEVICE)
    pos_atoms = state["pos_atoms"].to(DEVICE)

    target_pos_gen = torch.Generator().manual_seed(SEED + 99)
    target_pos_bits = torch.randint(0, 2, (N,), generator=target_pos_gen)
    target_pos = (target_pos_bits * 2 - 1).to(torch.float32).to(DEVICE)
    vsa_bundles = build_vsa_pool(pool_vecs, pool_labels, pool_used, byte_atoms, target_pos)
    vsa_used = pool_used

    test_a = state["test_a"]
    train_b = state["train_b"]
    test_a_idx, test_a_targets = prepare_test_tensors(test_a, byte_atoms, pos_atoms)

    _say(f"\nPre-shift eval:")
    pre = eval_all(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                  pool_vecs, pool_labels, pool_used,
                  vsa_bundles, vsa_used, target_pos, ALPHA)
    _say(f"  C0={pre['c0']:.4f}  C1={pre['c1']:.4f}  C2={pre['c2']:.4f}  C3={pre['c3']:.4f}")
    _say(f"  Pre-shift C3 vs C1: {pre['c1']-pre['c3']:+.4f} bpc")

    # Train on corpus B
    pad = bytes([PAD_BYTE]) * K
    padded_train_b = pad + train_b
    T_total = len(padded_train_b) - K
    train_b_bytes = torch.tensor(list(padded_train_b), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos_train = torch.arange(T_total, device=DEVICE)
    train_b_idx = train_b_bytes[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
    train_b_targets = train_b_bytes[pos_train + K]

    _say(f"\nContinual training on corpus B...")
    _say(f"  {'ep':>4} | {'C0':>7} | {'C1':>7} | {'C2':>7} | {'C3':>7} | {'C3-C1':>8}")
    t_start = time.perf_counter()
    history = []
    for epoch in range(1, MAX_EPOCHS_B + 1):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_b_idx[batch_start:be]
            tgt_batch = train_b_targets[batch_start:be]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            with torch.no_grad():
                q = ctxs @ W.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms_b = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms_b - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)
        if epoch in EVAL_AT:
            with torch.no_grad():
                ev = eval_all(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                            pool_vecs, pool_labels, pool_used,
                            vsa_bundles, vsa_used, target_pos, ALPHA)
                c3_vs_c1 = ev["c1"] - ev["c3"]
                _say(f"  {epoch:>4} | {ev['c0']:>7.4f} | {ev['c1']:>7.4f} | {ev['c2']:>7.4f} | "
                     f"{ev['c3']:>7.4f} | {c3_vs_c1:>+8.4f}")
                history.append({"epoch": epoch, **ev, "c3_vs_c1": c3_vs_c1})

    final = history[-1]
    _say(f"\n========= C3 VERDICT =========")
    _say(f"  Pre-shift  C3 vs C1: {pre['c1']-pre['c3']:+.4f}")
    _say(f"  Post-shift C3 vs C1: {final['c3_vs_c1']:+.4f}")
    if final["c3_vs_c1"] > 0.01:
        _say(f"  C3 BEATS C1 by >0.01 bpc. Compositional retrieval helps.")
    elif abs(final["c3_vs_c1"]) < 0.01:
        _say(f"  C3 ≈ C1. Partial match adds no extra info on this task.")
    else:
        _say(f"  C3 WORSE than C1. Partial match loses information.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_c3_minimal"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"C3_MATCH_POSITIONS": C3_MATCH_POSITIONS,
         "pre_shift": pre, "history": history,
         "elapsed_s": time.perf_counter() - t_start},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
