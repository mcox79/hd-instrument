"""Substrate-native uncertainty — does any internal signal correlate with byte accuracy?

Train substrate, eval on test_a. For each test prediction:
- Record softmax entropy H(P)
- Record top-1 margin (P_top1 - P_top2)
- Record pool retrieval entropy
- Record W-pool agreement (do W and pool agree on argmax?)
- Record whether the prediction was correct

Compute correlation between each signal and correctness. Also AUROC for
abstention: at what threshold can we refuse to answer with high reliability?

Pass: any signal has |correlation| > 0.3 with correctness AND
abstention AUROC > 0.7.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
N = 4096
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
MAX_EPOCHS = 15
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
SEED = 17


def _say(m): print(m, flush=True)


def load_corpus_a():
    repo = Path(__file__).resolve().parent.parent
    files = [repo / "PLAN.md", repo / "NEXT_PHASE.md", repo / "README.md",
             repo / "PROGRESS.md", repo / "RESULTS.md", repo / "CLAUDE.md"]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes()); parts.append(b"\n\n")
    return b"".join(parts)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def build_ctx(byte_atoms, pos_atoms, idx):
    b = byte_atoms[idx] * pos_atoms.unsqueeze(0)
    s = b.sum(dim=1)
    out = torch.sign(s)
    return torch.where(out == 0, torch.ones_like(out), out)


def relu_shift(q, b): return torch.clamp(q - b, min=0.0)


def train_phase_a(byte_atoms, pos_atoms, train_bytes):
    W = torch.zeros((N, N), device=DEVICE)
    pool_v = torch.zeros((POOL_SIZE, N), device=DEVICE)
    pool_l = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    p_idx, p_used = 0, 0
    arange = torch.arange(BATCH_SIZE, device=DEVICE)
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offs = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offs.unsqueeze(0)]
    tgt = bt[pos + K]
    for epoch in range(1, MAX_EPOCHS + 1):
        for bs in range(0, T, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T)
            B = be - bs
            ctxs = build_ctx(byte_atoms, pos_atoms, idx[bs:be])
            t = tgt[bs:be]
            with torch.no_grad():
                q = relu_shift(ctxs @ W.T, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                resid = byte_atoms[t] - (P.T @ byte_atoms)
                dW = (resid.T @ ctxs) / N
                W.mul_(1.0 - DELTA_RULE_DECAY); W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if epoch == 1:
                    dest = (p_idx + arange[:B]) % POOL_SIZE
                    pool_v.index_copy_(0, dest, ctxs)
                    pool_l.index_copy_(0, dest, t)
                    p_idx = (p_idx + B) % POOL_SIZE
                    p_used = min(p_used + B, POOL_SIZE)
    return W, pool_v, pool_l, p_used


def evaluate_with_signals(W, byte_atoms, pos_atoms, test_bytes, pool_v, pool_l, p_used):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offs = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offs.unsqueeze(0)]
    tgt = bt[pos + K]
    records = []
    active = pool_v[:p_used]
    labels = pool_l[:p_used]
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        B = be - bs
        ctxs = build_ctx(byte_atoms, pos_atoms, idx[bs:be])
        t = tgt[bs:be]
        q = relu_shift(ctxs @ W.T, RELU_B)
        sims = (byte_atoms @ q.T) / N
        P_W = torch.softmax(BETA * sims, dim=0)
        sims_p = (active @ ctxs.T) / N
        w_p = torch.softmax(BETA * sims_p, dim=0)
        P_retr = torch.zeros(VOCAB_SIZE, B, device=DEVICE)
        P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), w_p)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        # signals (per-query)
        log_P = torch.log(P.clamp(min=1e-12))
        entropy = -(P * log_P).sum(dim=0)
        topk = P.topk(2, dim=0).values
        margin = topk[0] - topk[1]
        pool_entropy = -(w_p * torch.log(w_p.clamp(min=1e-12))).sum(dim=0)
        argmax = P.argmax(dim=0)
        W_argmax = P_W.argmax(dim=0)
        retr_argmax = P_retr.argmax(dim=0)
        W_pool_agree = (W_argmax == retr_argmax).float()
        correct = (argmax == t).float()
        # accumulate
        for b in range(B):
            records.append({
                "entropy": float(entropy[b]),
                "margin": float(margin[b]),
                "pool_entropy": float(pool_entropy[b]),
                "agree": float(W_pool_agree[b]),
                "correct": int(correct[b]),
            })
    return records


def correlation(xs, ys):
    n = len(xs)
    mx = sum(xs) / n; my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx * dy < 1e-9:
        return 0.0
    return num / (dx * dy)


def abstention_auroc(signal_vals, correct_vals, descending=True):
    """AUROC for predicting correctness from signal. If descending, larger signal=more confident."""
    paired = sorted(zip(signal_vals, correct_vals), key=lambda x: x[0], reverse=descending)
    n_pos = sum(c for _, c in paired)
    n_neg = len(paired) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    auc = 0.0
    seen_neg = 0
    for _, c in paired:
        if c == 0:
            seen_neg += 1
        else:
            auc += seen_neg
    return auc / (n_pos * n_neg)


def main():
    _say(f"Substrate uncertainty probe: K={K}, N={N}, seed={SEED}")
    corpus = load_corpus_a()
    split = int(0.8 * len(corpus))
    train_a, test_a = corpus[:split], corpus[split:]
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc(K, N, gen).to(DEVICE)
    W, pool_v, pool_l, p_used = train_phase_a(byte_atoms, pos_atoms, train_a)
    records = evaluate_with_signals(W, byte_atoms, pos_atoms, test_a, pool_v, pool_l, p_used)

    correct = [r["correct"] for r in records]
    acc = sum(correct) / len(correct)
    _say(f"  Overall accuracy: {acc*100:.2f}% over {len(records)} tokens")

    for sig in ["entropy", "margin", "pool_entropy", "agree"]:
        vals = [r[sig] for r in records]
        # entropy/pool_entropy: LOW = confident. margin/agree: HIGH = confident.
        descending = sig in ("margin", "agree")
        corr = correlation([-v if not descending else v for v in vals], correct)
        auc = abstention_auroc(vals, correct, descending=descending)
        _say(f"  {sig:14s}: corr(with correct)={corr:+.3f}  abstention AUROC={auc:.3f}")

    # Composite signal: margin - entropy*0.3 (weighted)
    comp = [r["margin"] - r["entropy"] * 0.3 for r in records]
    corr_comp = correlation(comp, correct)
    auc_comp = abstention_auroc(comp, correct, descending=True)
    _say(f"  composite     : corr(with correct)={corr_comp:+.3f}  abstention AUROC={auc_comp:.3f}")

    _say("\n========= UNCERTAINTY VERDICT =========")
    best_auc = max([abstention_auroc([r[s] for r in records], correct,
                                       descending=(s in ("margin", "agree"))) for s in ["entropy", "margin", "pool_entropy", "agree"]] + [auc_comp])
    if best_auc >= 0.7:
        _say(f"  PASS: best AUROC = {best_auc:.3f}. Substrate self-calibrates.")
    elif best_auc >= 0.6:
        _say(f"  PARTIAL: AUROC {best_auc:.3f}. Some signal but not strong.")
    else:
        _say(f"  WEAK: AUROC {best_auc:.3f}. No substrate-internal signal reliably predicts correctness.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e_substrate_uncertainty"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "K": K, "accuracy": acc, "best_auc": best_auc, "n_records": len(records),
    }, indent=2))


if __name__ == "__main__":
    main()
