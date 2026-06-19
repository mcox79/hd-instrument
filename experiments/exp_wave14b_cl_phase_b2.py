"""Wave 14.B + CL Phase B.2: VSA-pool with target encoded in-bundle.

C2 condition: pool entries are bundles (ctx + byte_atoms[target] (*) pos_atoms[K]).
Target is recovered at retrieval time via 14.B-style elementwise extraction:
target_estimate = bundle (*) pos_atoms[K] = byte_atom[target] + (ctx (*) pos_K)
The second term is uncorrelated noise.

Compared to C1 (classical pool with explicit labels) on the same A-pool and
same continual training on B. The W is identical. The ONLY difference is
how the pool stores and extracts targets.

Hypothesis: C2 BWT approximately equals C1 BWT (same information content,
different encoding). If C2 is significantly worse, the target extraction
is noisy. If C2 is significantly better, the VSA encoding adds something.
Either way the result is informative.

Phase B.3 will use the same pool structure but try compositional retrieval.
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
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS_B = 15
EVAL_AT = [1, 3, 5, 10, 15]
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4


def _say(msg: str) -> None:
    print(msg, flush=True)


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
    """C1 baseline: cosine match + explicit label vote."""
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


def predict_pool_vsa(ctxs, vsa_bundles, vsa_used, target_pos, byte_atoms, beta, n):
    """C2: pool stores bundles (ctx + byte_atom*target_pos). Extract target via *target_pos.

    bundle = ctx + byte_atom * target_pos  (target_pos is bipolar pos atom for slot K)
    bundle * target_pos = ctx * target_pos + byte_atom * (target_pos * target_pos)
                       = ctx * target_pos + byte_atom    (target_pos is bipolar, so squared=1)
    The first term is uncorrelated noise relative to byte codebook.
    """
    B = ctxs.shape[0]
    if vsa_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    active = vsa_bundles[:vsa_used]  # (P, N)
    # Score: similarity of query ctx to bundle (treating target term as noise)
    sims = (active @ ctxs.T) / n  # (P, B)
    weights = torch.softmax(beta * sims, dim=0)  # (P, B) over pool entries

    # Extract target estimates from each retrieved bundle
    target_estimates = active * target_pos.unsqueeze(0)  # (P, N)
    # Score against byte codebook
    byte_scores = (target_estimates @ byte_atoms.T) / n  # (P, 256)
    P_byte_per_entry = torch.softmax(beta * byte_scores, dim=1)  # (P, 256)

    # Aggregate: P(byte | query) = sum over pool entries of weight(entry, query) * P(byte | entry)
    # weights: (P, B), P_byte_per_entry: (P, 256)
    # Result: (256, B) = P_byte_per_entry.T @ weights
    P_retr = P_byte_per_entry.T @ weights  # (256, B)
    return P_retr


def eval_on_corpus(W, byte_atoms, pos_atoms, test_idx, test_targets,
                  pool_vecs, pool_labels, pool_used,
                  vsa_bundles, vsa_used, target_pos, alpha):
    """Returns dict of bpc for C0/C1/C2."""
    T_test = test_idx.shape[0]
    bits_c0 = 0.0
    bits_c1 = 0.0
    bits_c2 = 0.0
    for bs in range(0, T_test, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T_test)
        ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_idx[bs:be])
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
        tgts = test_targets[bs:be]
        # C0
        p_c0 = P_W.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits_c0 += float(-torch.log2(p_c0).sum())
        # C1
        P_retr_c = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
        P_c1 = alpha * P_retr_c + (1.0 - alpha) * P_W
        p_c1 = P_c1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits_c1 += float(-torch.log2(p_c1).sum())
        # C2
        P_retr_v = predict_pool_vsa(ctxs, vsa_bundles, vsa_used, target_pos, byte_atoms, BETA, N)
        P_c2 = alpha * P_retr_v + (1.0 - alpha) * P_W
        p_c2 = P_c2.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits_c2 += float(-torch.log2(p_c2).sum())
    return {"c0_bpc": bits_c0 / max(T_test, 1),
            "c1_bpc": bits_c1 / max(T_test, 1),
            "c2_bpc": bits_c2 / max(T_test, 1)}


def prepare_test_tensors(test_bytes, byte_atoms, pos_atoms):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bs_tensor = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bs_tensor[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts = bs_tensor[pos + K]
    return idx, tgts


def build_vsa_pool(pool_vecs, pool_labels, pool_used, byte_atoms, target_pos):
    """Rebuild pool entries as VSA bundles: ctx + byte_atom[target] * target_pos."""
    if pool_used == 0:
        return torch.zeros_like(pool_vecs)
    target_atoms = byte_atoms[pool_labels[:pool_used]]  # (pool_used, N)
    target_bound = target_atoms * target_pos.unsqueeze(0)  # (pool_used, N)
    vsa = pool_vecs[:pool_used] + target_bound
    return vsa


def main() -> None:
    _say(f"Wave 14.B + CL Phase B.2: VSA-pool (target in-bundle, 14.B extraction)")
    _say(f"  N={N}, K={K}, seed={SEED}, device={DEVICE}")

    state_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cl_phase_a" / "state.pt"
    if not state_path.exists():
        _say(f"ERROR: state.pt not found at {state_path}. Run Phase A first.")
        return
    state = torch.load(state_path, weights_only=False)
    _say(f"  Loaded state from {state_path}")

    W = state["W_A"].to(DEVICE)
    pool_vecs = state["pool_vecs_A"].to(DEVICE)
    pool_labels = state["pool_labels_A"].to(DEVICE)
    pool_used = int(state["pool_used_A"])
    byte_atoms = state["byte_atoms"].to(DEVICE)
    pos_atoms = state["pos_atoms"].to(DEVICE)
    _say(f"  Pool: {pool_used} entries from corpus A")

    # Generate target position atom (one beyond context positions 0..K-1)
    target_pos_gen = torch.Generator().manual_seed(SEED + 99)
    target_pos_bits = torch.randint(0, 2, (N,), generator=target_pos_gen)
    target_pos = (target_pos_bits * 2 - 1).to(torch.float32).to(DEVICE)
    _say(f"  target_pos: bipolar atom for slot K (orthogonal to context positions)")

    # Build VSA pool
    vsa_bundles = build_vsa_pool(pool_vecs, pool_labels, pool_used, byte_atoms, target_pos)
    vsa_used = pool_used
    _say(f"  VSA pool: {vsa_used} bundles (ctx + byte_atom[target] * target_pos)")

    test_a = state["test_a"]
    train_b = state["train_b"]
    test_b = state["test_b"]

    test_a_idx, test_a_targets = prepare_test_tensors(test_a, byte_atoms, pos_atoms)
    test_b_idx, test_b_targets = prepare_test_tensors(test_b, byte_atoms, pos_atoms)

    _say(f"\nPre-shift evaluation (W = W_A):")
    pre = eval_on_corpus(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                        pool_vecs, pool_labels, pool_used,
                        vsa_bundles, vsa_used, target_pos, ALPHA)
    _say(f"  test_A: C0={pre['c0_bpc']:.4f}  C1={pre['c1_bpc']:.4f}  C2={pre['c2_bpc']:.4f}")

    # Build train_b tensors
    pad = bytes([PAD_BYTE]) * K
    padded_train_b = pad + train_b
    T_total = len(padded_train_b) - K
    train_b_bytes = torch.tensor(list(padded_train_b), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos_train = torch.arange(T_total, device=DEVICE)
    train_b_idx = train_b_bytes[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
    train_b_targets = train_b_bytes[pos_train + K]

    history = []
    t_start = time.perf_counter()
    _say(f"\nContinual training W on corpus B ({MAX_EPOCHS_B} epochs), both pools stay as A's...")
    _say(f"  {'ep':>4} | {'tA C0':>7} | {'tA C1':>7} | {'tA C2':>7} | {'tB C0':>7} | {'wall':>6}")
    _say(f"  {'-'*4}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-{'-'*6}")

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
                ev_a = eval_on_corpus(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                                     pool_vecs, pool_labels, pool_used,
                                     vsa_bundles, vsa_used, target_pos, ALPHA)
                ev_b = eval_on_corpus(W, byte_atoms, pos_atoms, test_b_idx, test_b_targets,
                                     pool_vecs, pool_labels, pool_used,
                                     vsa_bundles, vsa_used, target_pos, ALPHA)
                w_frob = float(W.pow(2).sum().sqrt())
                elapsed = time.perf_counter() - t_start
                _say(f"  {epoch:>4} | {ev_a['c0_bpc']:>7.4f} | {ev_a['c1_bpc']:>7.4f} | "
                     f"{ev_a['c2_bpc']:>7.4f} | {ev_b['c0_bpc']:>7.4f} | {elapsed:>5.1f}s")
                history.append({"epoch": epoch,
                              "test_a_c0_bpc": ev_a["c0_bpc"],
                              "test_a_c1_bpc": ev_a["c1_bpc"],
                              "test_a_c2_bpc": ev_a["c2_bpc"],
                              "test_b_c0_bpc": ev_b["c0_bpc"],
                              "test_b_c1_bpc": ev_b["c1_bpc"],
                              "test_b_c2_bpc": ev_b["c2_bpc"],
                              "w_frob": w_frob,
                              "wall_s": elapsed})

    # BWT summary
    final = history[-1]
    bwt_c1 = pre["c1_bpc"] - final["test_a_c1_bpc"]
    bwt_c2 = pre["c2_bpc"] - final["test_a_c2_bpc"]
    _say(f"\n========= BWT SUMMARY =========")
    _say(f"  C1 (classical pool): pre={pre['c1_bpc']:.4f}  post={final['test_a_c1_bpc']:.4f}  BWT={bwt_c1:+.4f}")
    _say(f"  C2 (VSA pool):       pre={pre['c2_bpc']:.4f}  post={final['test_a_c2_bpc']:.4f}  BWT={bwt_c2:+.4f}")
    _say(f"")
    _say(f"  C2 vs C1 delta on post-shift test_A: {final['test_a_c1_bpc'] - final['test_a_c2_bpc']:+.4f} bpc")
    _say(f"  (positive = C2 better; negative = C1 better)")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cl_phase_b2"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {"pre_shift": pre, "history": history,
           "summary": {"final_c1": final["test_a_c1_bpc"],
                      "final_c2": final["test_a_c2_bpc"],
                      "bwt_c1": bwt_c1, "bwt_c2": bwt_c2,
                      "c2_vs_c1_delta": final["test_a_c1_bpc"] - final["test_a_c2_bpc"]}}
    (out_dir / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
