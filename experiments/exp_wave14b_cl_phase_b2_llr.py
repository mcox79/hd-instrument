"""Wave 14.B + CL Phase B.2-LLR: test LLR calibration hypothesis.

Theory (unbiased survey 2026-05-19) predicts the C2 vs C1 gap of
0.02-0.06 bpc is NOT bundle information loss (theoretical lower bound
is ~10^-95 bpc). Most likely cause: uncalibrated softmax readout. The
Bayes-optimal LLR is 2v/(B-1), not raw v.

This experiment is identical to Phase B.2 EXCEPT predict_pool_vsa
applies the calibration factor 2/(B-1) to the extracted target estimate
before softmax. B here = K+1 = 5 (4 context + 1 target binding).

Pre-registered prediction (notes/wave14b_bundle_noise_theory.md):
- If C2-vs-C1 gap closes to <0.005 bpc: calibration was the story.
- If gap remains 0.04+ bpc: deeper issue, hypothesis falsified.
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

# LLR calibration: B is the total bundle size (K context + 1 target = 5)
B_BUNDLE = K + 1
LLR_FACTOR = 2.0 / (B_BUNDLE - 1)


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


def predict_pool_vsa_llr(ctxs, vsa_bundles, vsa_used, target_pos, byte_atoms, beta, n):
    """C2-LLR: same as predict_pool_vsa but with LLR calibration on extracted target.

    Theory says target_estimate = bundle * target_pos has noise variance B-1 per
    coordinate. The Bayes-optimal LLR is 2*target_estimate/(B-1). Apply this
    factor before computing byte scores.
    """
    B = ctxs.shape[0]
    if vsa_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    active = vsa_bundles[:vsa_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(beta * sims, dim=0)
    # LLR-calibrated target extraction
    target_estimates = active * target_pos.unsqueeze(0) * LLR_FACTOR
    byte_scores = (target_estimates @ byte_atoms.T) / n
    P_byte_per_entry = torch.softmax(beta * byte_scores, dim=1)
    P_retr = P_byte_per_entry.T @ weights
    return P_retr


def eval_corpus(W, byte_atoms, pos_atoms, test_idx, test_targets,
               pool_vecs, pool_labels, pool_used,
               vsa_bundles, vsa_used, target_pos, alpha):
    T_test = test_idx.shape[0]
    bits_c0 = 0.0
    bits_c1 = 0.0
    bits_c2 = 0.0
    for bs in range(0, T_test, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T_test)
        ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_idx[bs:be])
        P_W = predict_W(W, ctxs, byte_atoms, BETA, N)
        tgts = test_targets[bs:be]
        p_c0 = P_W.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits_c0 += float(-torch.log2(p_c0).sum())
        P_retr_c = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
        P_c1 = alpha * P_retr_c + (1.0 - alpha) * P_W
        p_c1 = P_c1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits_c1 += float(-torch.log2(p_c1).sum())
        P_retr_v = predict_pool_vsa_llr(ctxs, vsa_bundles, vsa_used, target_pos, byte_atoms, BETA, N)
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
    if pool_used == 0:
        return torch.zeros_like(pool_vecs)
    target_atoms = byte_atoms[pool_labels[:pool_used]]
    target_bound = target_atoms * target_pos.unsqueeze(0)
    return pool_vecs[:pool_used] + target_bound


def main():
    _say(f"Wave 14.B + CL Phase B.2-LLR: LLR-calibrated target extraction")
    _say(f"  N={N}, K={K}, B_BUNDLE={B_BUNDLE}, LLR factor=2/(B-1)={LLR_FACTOR}")
    _say(f"  Pre-registered: gap closes <0.005 bpc -> calibration confirmed")

    state_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cl_phase_a" / "state.pt"
    if not state_path.exists():
        _say(f"ERROR: state.pt not found at {state_path}")
        return
    state = torch.load(state_path, weights_only=False)

    W = state["W_A"].to(DEVICE)
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
    test_b = state["test_b"]
    test_a_idx, test_a_targets = prepare_test_tensors(test_a, byte_atoms, pos_atoms)
    test_b_idx, test_b_targets = prepare_test_tensors(test_b, byte_atoms, pos_atoms)

    _say(f"\nPre-shift evaluation:")
    pre = eval_corpus(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                     pool_vecs, pool_labels, pool_used,
                     vsa_bundles, vsa_used, target_pos, ALPHA)
    _say(f"  test_A: C0={pre['c0_bpc']:.4f}  C1={pre['c1_bpc']:.4f}  C2_LLR={pre['c2_bpc']:.4f}")
    _say(f"  Pre-shift C2_LLR vs C1: {pre['c1_bpc'] - pre['c2_bpc']:+.4f}")

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
    _say(f"\nContinual training on corpus B...")
    _say(f"  {'ep':>4} | {'tA C0':>7} | {'tA C1':>7} | {'tA C2_LLR':>10} | {'C2-C1':>8} | {'wall':>6}")
    _say(f"  {'-'*4}-+-{'-'*7}-+-{'-'*7}-+-{'-'*10}-+-{'-'*8}-+-{'-'*6}")

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
                ev = eval_corpus(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                                pool_vecs, pool_labels, pool_used,
                                vsa_bundles, vsa_used, target_pos, ALPHA)
                w_frob = float(W.pow(2).sum().sqrt())
                elapsed = time.perf_counter() - t_start
                c2_vs_c1 = ev["c1_bpc"] - ev["c2_bpc"]
                _say(f"  {epoch:>4} | {ev['c0_bpc']:>7.4f} | {ev['c1_bpc']:>7.4f} | "
                     f"{ev['c2_bpc']:>10.4f} | {c2_vs_c1:>+8.4f} | {elapsed:>5.1f}s")
                history.append({"epoch": epoch,
                              "test_a_c0_bpc": ev["c0_bpc"],
                              "test_a_c1_bpc": ev["c1_bpc"],
                              "test_a_c2_llr_bpc": ev["c2_bpc"],
                              "c2_vs_c1": c2_vs_c1,
                              "w_frob": w_frob,
                              "wall_s": elapsed})

    final = history[-1]
    final_gap = final["c2_vs_c1"]  # positive = C2 better
    _say(f"\n========= VERDICT =========")
    _say(f"  Pre-shift C2_LLR vs C1: {pre['c1_bpc'] - pre['c2_bpc']:+.4f} bpc")
    _say(f"  Post-shift C2_LLR vs C1: {final_gap:+.4f} bpc")
    _say(f"")
    _say(f"  Baseline B.2 (raw v) had: post-shift C2-C1 = -0.0559 bpc")
    _say(f"  Theory predicted near-zero gap with LLR calibration")
    if abs(final_gap) < 0.005:
        _say(f"  HYPOTHESIS CONFIRMED: gap closes to <0.005 bpc (calibration was the story)")
    elif final_gap > -0.02 and final_gap < 0.02:
        _say(f"  PARTIAL: gap dramatically reduced but not zero. Most of effect is calibration.")
    else:
        _say(f"  HYPOTHESIS FALSIFIED: gap remains. Deeper issue beyond calibration.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cl_phase_b2_llr"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {"pre_shift": pre, "history": history,
           "final_gap": final_gap, "LLR_factor": LLR_FACTOR,
           "B_bundle": B_BUNDLE}
    (out_dir / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
