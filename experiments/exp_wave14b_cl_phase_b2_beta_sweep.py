"""Wave 14.B + CL Phase B.2-BETA-sweep: test softmax confidence hypothesis.

LLR test FAILED (gap got worse). Re-analysis: the gap is from softmax
*confidence ceiling*, not bundle information loss.

C1 (explicit labels): P(target | retrieved entry) = 1.0 exactly.
C2 (softmax extraction): caps at P(target) ~ e^beta / (e^beta + (M-1))
   For BETA=8, M=256: ~0.92, giving log(1/0.92) ~ 0.025 bpc per query.

Fix: increase BETA in the byte-extraction softmax. At BETA=32, the
softmax becomes effectively hard (P(target) ~ 1.0 when bundle is
decoded correctly, which is overwhelmingly likely per the SNR analysis).

Sweep BYTE_EXTRACTION_BETA in {8, 16, 32, 64, 128}.

Pre-registered:
- At BETA=32+, C2 should match C1 within 0.005 bpc.
- Failing that, the gap is from something else (resilience to wrong
  decoding when SNR is bad).
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
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS_B = 15
EVAL_AT = [15]
RELU_B = 0.5
N = 4096
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
BETA_RETRIEVAL = 8.0  # the main BETA for retrieval scoring (unchanged)
BYTE_BETA_SWEEP = [8.0, 16.0, 32.0, 64.0, 128.0]


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


def predict_pool_vsa_beta(ctxs, vsa_bundles, vsa_used, target_pos, byte_atoms,
                         beta_retrieval, beta_byte, n):
    """C2 with separable beta for retrieval scoring vs byte extraction softmax."""
    B = ctxs.shape[0]
    if vsa_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    active = vsa_bundles[:vsa_used]
    sims = (active @ ctxs.T) / n
    weights = torch.softmax(beta_retrieval * sims, dim=0)
    target_estimates = active * target_pos.unsqueeze(0)
    byte_scores = (target_estimates @ byte_atoms.T) / n
    P_byte_per_entry = torch.softmax(beta_byte * byte_scores, dim=1)
    P_retr = P_byte_per_entry.T @ weights
    return P_retr


def eval_corpus(W, byte_atoms, pos_atoms, test_idx, test_targets,
               pool_vecs, pool_labels, pool_used,
               vsa_bundles, vsa_used, target_pos, alpha, beta_byte):
    T_test = test_idx.shape[0]
    bits_c1 = 0.0
    bits_c2 = 0.0
    for bs in range(0, T_test, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T_test)
        ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, test_idx[bs:be])
        P_W = predict_W(W, ctxs, byte_atoms, BETA_RETRIEVAL, N)
        tgts = test_targets[bs:be]
        P_retr_c = predict_pool_classical(ctxs, pool_vecs, pool_labels, pool_used,
                                         BETA_RETRIEVAL, N)
        P_c1 = alpha * P_retr_c + (1.0 - alpha) * P_W
        p_c1 = P_c1.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits_c1 += float(-torch.log2(p_c1).sum())
        P_retr_v = predict_pool_vsa_beta(ctxs, vsa_bundles, vsa_used, target_pos,
                                        byte_atoms, BETA_RETRIEVAL, beta_byte, N)
        P_c2 = alpha * P_retr_v + (1.0 - alpha) * P_W
        p_c2 = P_c2.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits_c2 += float(-torch.log2(p_c2).sum())
    return {"c1_bpc": bits_c1 / max(T_test, 1),
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


def run_one_beta(beta_byte, state):
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

    pre = eval_corpus(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                    pool_vecs, pool_labels, pool_used,
                    vsa_bundles, vsa_used, target_pos, ALPHA, beta_byte)

    pad = bytes([PAD_BYTE]) * K
    padded_train_b = pad + train_b
    T_total = len(padded_train_b) - K
    train_b_bytes = torch.tensor(list(padded_train_b), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos_train = torch.arange(T_total, device=DEVICE)
    train_b_idx = train_b_bytes[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
    train_b_targets = train_b_bytes[pos_train + K]

    for epoch in range(MAX_EPOCHS_B):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_b_idx[batch_start:be]
            tgt_batch = train_b_targets[batch_start:be]
            ctxs = build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            with torch.no_grad():
                q = ctxs @ W.T
                q = shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA_RETRIEVAL * sims, dim=0)
                target_atoms_b = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms_b - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)

    post = eval_corpus(W, byte_atoms, pos_atoms, test_a_idx, test_a_targets,
                      pool_vecs, pool_labels, pool_used,
                      vsa_bundles, vsa_used, target_pos, ALPHA, beta_byte)
    return {"beta_byte": beta_byte, "pre": pre, "post": post,
           "c2_vs_c1_pre": pre["c1_bpc"] - pre["c2_bpc"],
           "c2_vs_c1_post": post["c1_bpc"] - post["c2_bpc"]}


def main():
    _say(f"Wave 14.B + CL Phase B.2 BYTE_BETA sweep")
    _say(f"  Hypothesis: gap is softmax confidence ceiling, increasing BETA closes it")
    _say(f"  Sweep BYTE_BETA: {BYTE_BETA_SWEEP}  (BETA_RETRIEVAL stays {BETA_RETRIEVAL})")

    state_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cl_phase_a" / "state.pt"
    if not state_path.exists():
        _say(f"ERROR: state.pt not found at {state_path}")
        return
    state = torch.load(state_path, weights_only=False)

    all_results = []
    t_start = time.perf_counter()
    _say(f"\n  {'beta':>6} | {'pre C1':>7} {'pre C2':>7} | {'post C1':>8} {'post C2':>8} | {'C2-C1 post':>11} | {'wall':>6}")
    _say(f"  {'-'*6}-+-{'-'*7} {'-'*7}-+-{'-'*8} {'-'*8}-+-{'-'*11}-+-{'-'*6}")
    for beta in BYTE_BETA_SWEEP:
        t0 = time.perf_counter()
        r = run_one_beta(beta, state)
        dt = time.perf_counter() - t0
        _say(f"  {beta:>6.1f} | {r['pre']['c1_bpc']:>7.4f} {r['pre']['c2_bpc']:>7.4f} | "
             f"{r['post']['c1_bpc']:>8.4f} {r['post']['c2_bpc']:>8.4f} | "
             f"{r['c2_vs_c1_post']:>+11.4f} | {dt:>5.1f}s")
        all_results.append(r)

    _say(f"\n========= VERDICT =========")
    best = max(all_results, key=lambda r: r["c2_vs_c1_post"])
    _say(f"  Best beta for C2: {best['beta_byte']}, C2-C1 post = {best['c2_vs_c1_post']:+.4f}")
    if best["c2_vs_c1_post"] >= -0.005:
        _say(f"  HYPOTHESIS CONFIRMED: C2 matches C1 at high beta. Softmax confidence was the issue.")
    elif best["c2_vs_c1_post"] >= -0.02:
        _say(f"  STRONG SUPPORT: gap mostly closes; small residual.")
    else:
        _say(f"  HYPOTHESIS WEAK: gap persists. Issue is not softmax confidence alone.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cl_phase_b2_beta_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"results": all_results, "elapsed_s": time.perf_counter() - t_start},
        indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
