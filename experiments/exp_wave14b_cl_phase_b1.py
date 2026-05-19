"""Wave 14.B + CL Phase B.1: classical-pool forgetting baseline.

Loads state from Phase A (W_A trained on corpus A, pool_A with A entries).
Continues training W on corpus B (overwrites W_A). Pool stays as A's
(no B entries added) to test the pool's retention of A-knowledge after
W is destroyed.

Two conditions measured at each eval epoch:
- C0: W only (no pool). Should show catastrophic forgetting.
- C1: W + classical pool (cosine similarity retrieval against A pool entries).
      Should mitigate forgetting.

Also tracks bpc on test_B to confirm B is being learned in W.

Phase B.2 will add VSA-pool (target encoded in-bundle, 14.B decomposition).
Phase B.3 will add compositional retrieval (partial-ctx match + 14.B fill).
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


def predict_pool(ctxs, pool_vecs, pool_labels, pool_used, beta, n):
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


def eval_on_corpus(W, byte_atoms, pos_atoms, test_bytes_tensor, test_idx, test_targets,
                  pool_vecs, pool_labels, pool_used, alpha):
    """Returns dict of bpc for C0 (W only) and C1 (W + pool)."""
    T_test = test_idx.shape[0]
    bits_c0 = 0.0
    bits_c1 = 0.0
    for bs in range(0, T_test, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T_test)
        ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_idx[bs:be])
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
        tgts = test_targets[bs:be]
        # C0: W only
        p_c0 = P_W.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits_c0 += float(-torch.log2(p_c0).sum())
        # C1: W + pool
        P_retr = predict_pool(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
        P_c1 = alpha * P_retr + (1.0 - alpha) * P_W
        p_c1 = P_c1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits_c1 += float(-torch.log2(p_c1).sum())
    return {"c0_bpc": bits_c0 / max(T_test, 1),
            "c1_bpc": bits_c1 / max(T_test, 1)}


def prepare_test_tensors(test: bytes, byte_atoms, pos_atoms):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test
    T = len(padded) - K
    bs_tensor = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bs_tensor[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts = bs_tensor[pos + K]
    return bs_tensor, idx, tgts


def main() -> None:
    _say(f"Wave 14.B + CL Phase B.1: classical-pool forgetting baseline")
    _say(f"  N={N}, K={K}, seed={SEED}, device={DEVICE}")

    state_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cl_phase_a" / "state.pt"
    if not state_path.exists():
        _say(f"ERROR: state.pt not found at {state_path}. Run Phase A first.")
        return
    state = torch.load(state_path, weights_only=False)
    _say(f"  Loaded state from {state_path}")
    _say(f"  Pre-shift bpc on test_A: {state['history_A'][-1]['test_bpc']:.4f}")

    W = state["W_A"].to(DEVICE)
    pool_vecs = state["pool_vecs_A"].to(DEVICE)
    pool_labels = state["pool_labels_A"].to(DEVICE)
    pool_used = int(state["pool_used_A"])
    byte_atoms = state["byte_atoms"].to(DEVICE)
    pos_atoms = state["pos_atoms"].to(DEVICE)
    _say(f"  Pool: {pool_used} entries from corpus A")

    test_a = state["test_a"]
    train_b = state["train_b"]
    test_b = state["test_b"]
    _say(f"  train_b: {len(train_b)} bytes  test_a: {len(test_a)} bytes  test_b: {len(test_b)} bytes")

    _, test_a_idx, test_a_targets = prepare_test_tensors(test_a, byte_atoms, pos_atoms)
    _, test_b_idx, test_b_targets = prepare_test_tensors(test_b, byte_atoms, pos_atoms)

    _say(f"\nPre-shift evaluation (W = W_A):")
    pre = eval_on_corpus(W, byte_atoms, pos_atoms, None, test_a_idx, test_a_targets,
                        pool_vecs, pool_labels, pool_used, ALPHA)
    _say(f"  test_A bpc: C0(W only)={pre['c0_bpc']:.4f}  C1(W+pool)={pre['c1_bpc']:.4f}")

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
    _say(f"\nContinual training W on corpus B ({MAX_EPOCHS_B} epochs), pool stays as A's...")
    _say(f"  {'ep':>4} | {'test_A C0':>9} | {'test_A C1':>9} | {'test_B C0':>9} | {'||W||':>8} | {'wall':>6}")
    _say(f"  {'-'*4}-+-{'-'*9}-+-{'-'*9}-+-{'-'*9}-+-{'-'*8}-+-{'-'*6}")

    for epoch in range(1, MAX_EPOCHS_B + 1):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_b_idx[batch_start:be]
            tgt_batch = train_b_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
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

        if epoch in EVAL_AT:
            with torch.no_grad():
                # Eval on test_A (the forgetting test)
                ev_a = eval_on_corpus(W, byte_atoms, pos_atoms, None,
                                     test_a_idx, test_a_targets,
                                     pool_vecs, pool_labels, pool_used, ALPHA)
                # Eval on test_B (verify B is learned)
                ev_b = eval_on_corpus(W, byte_atoms, pos_atoms, None,
                                     test_b_idx, test_b_targets,
                                     pool_vecs, pool_labels, pool_used, ALPHA)
                w_frob = float(W.pow(2).sum().sqrt())
                elapsed = time.perf_counter() - t_start
                _say(f"  {epoch:>4} | {ev_a['c0_bpc']:>9.4f} | {ev_a['c1_bpc']:>9.4f} | "
                     f"{ev_b['c0_bpc']:>9.4f} | {w_frob:>8.1f} | {elapsed:>5.1f}s")
                history.append({"epoch": epoch,
                              "test_a_c0_bpc": ev_a["c0_bpc"],
                              "test_a_c1_bpc": ev_a["c1_bpc"],
                              "test_b_c0_bpc": ev_b["c0_bpc"],
                              "test_b_c1_bpc": ev_b["c1_bpc"],
                              "w_frob": w_frob,
                              "wall_s": elapsed})

    # Final BWT summary
    pre_a_c0 = state["history_A"][-1]["test_bpc"]  # pre-shift bpc (W_A on test_A using full system)
    # NOTE: pre uses W+pool from Phase A training; for clean BWT we should use the
    # W-only number. Use the C0 measurement from our pre-shift eval:
    pre_c0 = pre["c0_bpc"]
    pre_c1 = pre["c1_bpc"]
    final_c0 = history[-1]["test_a_c0_bpc"]
    final_c1 = history[-1]["test_a_c1_bpc"]
    bwt_c0 = pre_c0 - final_c0  # positive = degradation (we lost knowledge)
    bwt_c1 = pre_c1 - final_c1
    _say(f"\n========= BWT SUMMARY =========")
    _say(f"  test_A bpc, pre-shift  | post-shift | delta (negative = forgetting)")
    _say(f"  C0 (W only):  {pre_c0:.4f}      | {final_c0:.4f}     | {pre_c0 - final_c0:+.4f}")
    _say(f"  C1 (W+pool):  {pre_c1:.4f}      | {final_c1:.4f}     | {pre_c1 - final_c1:+.4f}")
    _say(f"")
    _say(f"  Catastrophic forgetting on C0: {final_c0 - pre_c0:+.4f} bpc")
    _say(f"  Pool mitigation (C1 vs C0):    {final_c0 - final_c1:+.4f} bpc savings via pool")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cl_phase_b1"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {"pre_shift": pre, "history": history,
           "summary": {"pre_c0": pre_c0, "pre_c1": pre_c1,
                      "final_c0": final_c0, "final_c1": final_c1,
                      "c0_forgetting": final_c0 - pre_c0,
                      "c1_forgetting": final_c1 - pre_c1,
                      "pool_mitigation_savings": final_c0 - final_c1}}
    (out_dir / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
