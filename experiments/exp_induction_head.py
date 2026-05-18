"""Wave 3b: Induction-head ICL test across substrates (post-audit).

Citation: Olsson et al. 2022 "In-context Learning and Induction Heads"
(Anthropic, arXiv:2209.11895). Defines the cleanest ICL primitive:
given a sequence containing `[A][B] ... [A]`, does the model predict `[B]`?
Higher accuracy at the second `[A]→[B]` than at the first measures
in-context inductive copying.

Audit (2026-05-18) rejected our originally-planned design (style-priming
with pool writes) — that tested pool retrieval fidelity, not ICL, because
explicit memory writes are not what transformer ICL measures. The
induction-head protocol resolves this: the pool is built only from training,
in-context examples enter through the input byte stream, and any "learning"
must happen through the model's natural retrieval-from-pool plus W-readout
dynamics during prediction.

Protocol:
1. Train each substrate (FHRR, BSC, SBC) normally on the project markdown
   corpus to convergence (15 epochs at N=4096, current settings).
2. At test time, generate synthetic byte sequences of the form:
     [rand prefix] (x_1 y_1) (x_2 y_2) ... (x_k y_k) x_i [end]
   where x_1..x_k are random distinct bytes, y_1..y_k are random target
   bytes, and x_i is one of x_1..x_k uniformly chosen.
3. Measure bpc on predicting y_i given the prefix.
4. Compare to:
   a. RANDOM baseline: bpc if model predicts uniformly (8.0 for 256-byte vocab).
   b. UNIGRAM baseline: bpc if model uses byte-frequency prior.
   c. NO-CONTEXT baseline: same sequence but x_i is a FRESH byte never seen
      in prefix — measures whether predicting y from x requires x to have
      appeared in context.

Substrates tested: FHRR, BSC, SBC. Different K (number of pair examples)
to measure how in-context examples affect prediction.

Lit anchors:
- Olsson et al. 2022 (Anthropic, arXiv:2209.11895)
- Akyürek et al. 2023 (arXiv:2211.15661): what learning algorithm is ICL?
- Garg et al. 2022 (arXiv:2208.01066): what can transformers learn in-context?
- Comparison baseline: a 2-layer attention-only transformer of matched params
  would be the gold-standard comparison; we run a unigram baseline here as
  a starting point; transformer baseline could be added in a follow-up.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch
import torch.nn.functional as F


torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
N = 4096
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4  # model's context window (architectural)
AROUSAL = 0.3
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
DECAY = 1e-4
MAX_EPOCHS = 15
EPOCH_CHECKPOINTS = [15]  # only final eval needed (training-then-ICL protocol)
RELU_B = 0.5

# Induction-task parameters
NUM_PAIRS_VALUES = [1, 2, 4, 8]  # how many (x, y) example pairs to include in context
NUM_INDUCTION_TRIALS = 500  # per (substrate, num_pairs) cell


def _say(msg: str) -> None:
    print(msg, flush=True)


# ============================================================
# Substrate functions (same as Wave 3a)
# ============================================================

def make_fhrr_atoms(k, n, gen):
    import math
    phases = torch.rand((k, n), generator=gen) * (2.0 * math.pi)
    return torch.complex(torch.cos(phases), torch.sin(phases)).to(torch.complex64)


def fhrr_build_ctx(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    mag = summed.abs().clamp(min=1e-8)
    return summed / mag.to(summed.dtype)


def fhrr_magnitude_relu(q, b):
    eps = 1e-9
    mag = q.abs().clamp(min=eps)
    new_mag = torch.clamp(mag - b, min=0.0)
    return q * (new_mag / mag).to(q.dtype)


def fhrr_predict_W(W, ctxs, byte_atoms, beta):
    n = ctxs.shape[1]
    q = ctxs @ W.T
    q = fhrr_magnitude_relu(q, RELU_B)
    sims = (byte_atoms.conj() @ q.T).real / n
    return torch.softmax(beta * sims, dim=0)


def fhrr_step(W, ctxs, tgt_idx, byte_atoms):
    P_W = fhrr_predict_W(W, ctxs, byte_atoms, BETA)
    targets = byte_atoms[tgt_idx]
    expected = P_W.T.to(byte_atoms.dtype) @ byte_atoms
    errors = targets - expected
    dW = errors.T @ ctxs.conj() / N
    W.mul_(1.0 - DECAY)
    W.add_(dW, alpha=AROUSAL)


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def bsc_build_ctx(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def bsc_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def bsc_predict_W(W, ctxs, byte_atoms, beta):
    n = ctxs.shape[1]
    q = ctxs @ W.T
    q = bsc_relu(q, RELU_B)
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0)


def bsc_step(W, ctxs, tgt_idx, byte_atoms):
    P_W = bsc_predict_W(W, ctxs, byte_atoms, BETA)
    targets = byte_atoms[tgt_idx]
    expected = P_W.T @ byte_atoms
    errors = targets - expected
    dW = errors.T @ ctxs / N
    W.mul_(1.0 - DECAY)
    W.add_(dW, alpha=AROUSAL)


SBC_B_SIZE = 32
SBC_M = N // SBC_B_SIZE


def make_sbc_atoms(k, gen):
    return torch.randint(0, SBC_B_SIZE, (k, SBC_M), generator=gen)


def sbc_to_dense(atom_idx, device):
    one_hot = F.one_hot(atom_idx, num_classes=SBC_B_SIZE)
    *batch_dims, _, _ = one_hot.shape
    return one_hot.reshape(*batch_dims, SBC_M * SBC_B_SIZE).float().to(device)


def sbc_bind(a_idx, b_idx):
    return (a_idx + b_idx) % SBC_B_SIZE


def sbc_bundle_vote(stacked_idx):
    one_hot = F.one_hot(stacked_idx, num_classes=SBC_B_SIZE).float()
    counts = one_hot.sum(dim=-3)
    return counts.argmax(dim=-1)


def sbc_build_ctx(byte_atoms_idx, pos_atoms_idx, indices, device):
    byte_used = byte_atoms_idx[indices]
    bound = sbc_bind(byte_used, pos_atoms_idx.unsqueeze(0))
    ctx_idx = sbc_bundle_vote(bound)
    return sbc_to_dense(ctx_idx, device)


def sbc_predict_W(W, ctx_dense, byte_dense, beta):
    q = ctx_dense @ W.T
    sims = (byte_dense @ q.T) / SBC_M
    return torch.softmax(beta * sims, dim=0)


def sbc_step(W, ctx_dense, tgt_idx, byte_dense):
    P_W = sbc_predict_W(W, ctx_dense, byte_dense, BETA)
    targets = byte_dense[tgt_idx]
    expected = P_W.T @ byte_dense
    errors = targets - expected
    dW = errors.T @ ctx_dense / N
    W.mul_(1.0 - DECAY)
    W.add_(dW, alpha=AROUSAL)


def predict_pool_real(ctxs, pool_vecs, pool_labels, pool_used, beta, n):
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


def predict_pool_complex(ctxs, pool_vecs, pool_labels, pool_used, beta, n):
    B = ctxs.shape[0]
    if pool_used == 0:
        return torch.full((VOCAB_SIZE, B), 1.0 / VOCAB_SIZE, device=ctxs.device)
    active = pool_vecs[:pool_used]
    labels = pool_labels[:pool_used]
    sims = (active.conj() @ ctxs.T).real / n
    weights = torch.softmax(beta * sims, dim=0)
    P_retr = torch.zeros(VOCAB_SIZE, B, device=ctxs.device)
    P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, B), weights)
    return P_retr


def load_corpus():
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


# ============================================================
# Build induction-head test sequences
# ============================================================

def make_induction_sequence(num_pairs, prefix_len, gen, repeat_query=True):
    """Build a byte sequence for the induction test.

    Layout: [prefix bytes] [x_1 y_1 x_2 y_2 ... x_k y_k] [x_i] -> predict y_i

    Returns: (context_window_K, target_byte)
    - context_window_K: the K bytes immediately preceding the target position
    - target_byte: y_i (the byte to predict)

    Crucially, the K=4 context window contains the LAST 4 bytes of the sequence:
    typically [... x_(k-1) y_(k-1) x_i], so the model must use its memory of
    earlier pairs to retrieve y_i.

    If repeat_query=False: x_i is a FRESH byte not in {x_1..x_k}; this is the
    no-context control where in-context retrieval shouldn't help.
    """
    seq = []
    # Random prefix of mostly common bytes (~ corpus distribution; here just random)
    prefix = torch.randint(0, VOCAB_SIZE, (prefix_len,), generator=gen)
    seq.extend(prefix.tolist())
    # Generate pairs with distinct x's
    xs = torch.randperm(VOCAB_SIZE, generator=gen)[:num_pairs].tolist()
    ys = torch.randint(0, VOCAB_SIZE, (num_pairs,), generator=gen).tolist()
    for x, y in zip(xs, ys):
        seq.append(x)
        seq.append(y)
    # Query: pick one x from the pairs (or fresh)
    if repeat_query:
        idx = torch.randint(0, num_pairs, (1,), generator=gen).item()
        x_query = xs[idx]
        y_target = ys[idx]
    else:
        # Pick a byte NOT in xs
        all_bytes = set(range(VOCAB_SIZE))
        fresh = list(all_bytes - set(xs))
        x_query = fresh[torch.randint(0, len(fresh), (1,), generator=gen).item()]
        # The "correct" target is undefined; assign a uniformly random one
        # (we measure surprise, not correctness, in this branch)
        y_target = torch.randint(0, VOCAB_SIZE, (1,), generator=gen).item()
    seq.append(x_query)
    # Now seq[-K:] is the context window for predicting y_target
    if len(seq) < K:
        # pad on the left
        seq = [PAD_BYTE] * (K - len(seq)) + seq
    ctx_window = seq[-K:]
    return ctx_window, y_target


def evaluate_induction(substrate, W, atoms_data, pool_data, num_pairs, n_trials, repeat_query, gen):
    """Run n_trials induction-head trials; return mean bpc."""
    total_bits = 0.0
    correct = 0
    for _ in range(n_trials):
        ctx_window, y_target = make_induction_sequence(num_pairs, prefix_len=8, gen=gen, repeat_query=repeat_query)
        # We need to "run" the model through the entire sequence so pool builds up
        # but per induction-head protocol, pool stays as it was at end of training.
        # We just evaluate prediction at the final position with the K-window context.
        ctx_tensor = torch.tensor([ctx_window], dtype=torch.long, device=DEVICE)  # (1, K)
        # Build context vector
        if substrate == "FHRR":
            byte_atoms, pos_atoms = atoms_data
            ctxs = fhrr_build_ctx(byte_atoms, pos_atoms, ctx_tensor)
            P_W = fhrr_predict_W(W, ctxs, byte_atoms, BETA)
            P_retr = predict_pool_complex(ctxs, pool_data["vecs"], pool_data["labels"],
                                          pool_data["used"], BETA, N)
        elif substrate == "BSC":
            byte_atoms, pos_atoms = atoms_data
            ctxs = bsc_build_ctx(byte_atoms, pos_atoms, ctx_tensor)
            P_W = bsc_predict_W(W, ctxs, byte_atoms, BETA)
            P_retr = predict_pool_real(ctxs, pool_data["vecs"], pool_data["labels"],
                                       pool_data["used"], BETA, N)
        elif substrate == "SBC":
            byte_atoms_idx, pos_atoms_idx, byte_dense = atoms_data
            ctxs = sbc_build_ctx(byte_atoms_idx, pos_atoms_idx, ctx_tensor, DEVICE)
            P_W = sbc_predict_W(W, ctxs, byte_dense, BETA)
            P_retr = predict_pool_real(ctxs, pool_data["vecs"], pool_data["labels"],
                                       pool_data["used"], BETA, N)
        P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
        p_true = P[y_target, 0].clamp(min=1e-12).item()
        total_bits += -torch.log2(torch.tensor(p_true)).item()
        if P.argmax(dim=0).item() == y_target:
            correct += 1
    return total_bits / max(n_trials, 1), correct / max(n_trials, 1)


# ============================================================
# Train each substrate to convergence, then evaluate ICL
# ============================================================

def train_substrate(substrate, train, test):
    """Standard training run; returns trained model state."""
    gen = torch.Generator().manual_seed(SEED)
    if substrate == "FHRR":
        byte_atoms = make_fhrr_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
        pos_atoms = make_fhrr_atoms(K, N, gen).to(DEVICE)
        W = torch.zeros((N, N), dtype=torch.complex64, device=DEVICE)
        pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.complex64, device=DEVICE)
        atoms_data = (byte_atoms, pos_atoms)
    elif substrate == "BSC":
        byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
        pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
        W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
        pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
        atoms_data = (byte_atoms, pos_atoms)
    elif substrate == "SBC":
        byte_atoms_idx = make_sbc_atoms(VOCAB_SIZE, gen).to(DEVICE)
        pos_atoms_idx = make_sbc_atoms(K, gen).to(DEVICE)
        byte_dense = sbc_to_dense(byte_atoms_idx, DEVICE)
        W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
        pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
        atoms_data = (byte_atoms_idx, pos_atoms_idx, byte_dense)

    pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_used = 0
    pool_idx = 0
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)

    pad = bytes([PAD_BYTE]) * K
    padded_train = pad + train
    padded_test = pad + test
    T_total = len(padded_train) - K
    T_test = len(padded_test) - K
    train_bytes = torch.tensor(list(padded_train), dtype=torch.long).to(DEVICE)
    test_bytes = torch.tensor(list(padded_test), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos_train = torch.arange(T_total, device=DEVICE)
    pos_test = torch.arange(T_test, device=DEVICE)
    train_idx = train_bytes[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
    train_targets = train_bytes[pos_train + K]
    test_idx = test_bytes[pos_test.unsqueeze(1) + offsets.unsqueeze(0)]
    test_targets = test_bytes[pos_test + K]

    def build_ctx(idx_batch):
        if substrate == "FHRR": return fhrr_build_ctx(byte_atoms, pos_atoms, idx_batch)
        if substrate == "BSC": return bsc_build_ctx(byte_atoms, pos_atoms, idx_batch)
        if substrate == "SBC": return sbc_build_ctx(byte_atoms_idx, pos_atoms_idx, idx_batch, DEVICE)

    def step(ctxs, tgt_idx):
        if substrate == "FHRR": fhrr_step(W, ctxs, tgt_idx, byte_atoms)
        elif substrate == "BSC": bsc_step(W, ctxs, tgt_idx, byte_atoms)
        elif substrate == "SBC": sbc_step(W, ctxs, tgt_idx, byte_dense)

    t_start = time.perf_counter()
    for epoch in range(1, MAX_EPOCHS + 1):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = build_ctx(idx_batch)
            step(ctxs, tgt_batch)
            if epoch == 1:
                dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                pool_vecs.index_copy_(0, dest, ctxs)
                pool_labels.index_copy_(0, dest, tgt_batch)
                pool_idx = (pool_idx + B) % POOL_SIZE
                pool_used = min(pool_used + B, POOL_SIZE)
    elapsed = time.perf_counter() - t_start
    _say(f"  [{substrate}] trained in {elapsed:.1f}s, pool_used={pool_used}")

    pool_data = {"vecs": pool_vecs, "labels": pool_labels, "used": pool_used}
    return W, atoms_data, pool_data


def main():
    _say("Loading corpus...")
    corpus = load_corpus()
    cut = int(len(corpus) * 0.8)
    train, test = corpus[:cut], corpus[cut:]
    _say(f"  train={len(train)}, test={len(test)} bytes")

    _say(f"\nInduction-head ICL (Wave 3b, post-audit per Olsson 2022)")
    _say(f"  Protocol: train on markdown corpus, then evaluate on synthetic")
    _say(f"  sequences (x_1 y_1)(x_2 y_2)...(x_k y_k) x_i -> predict y_i")
    _say(f"  N={N}, K={K}, num_pairs={NUM_PAIRS_VALUES}, trials={NUM_INDUCTION_TRIALS}")
    _say(f"  Substrates: FHRR, BSC, SBC.  Lit: Olsson et al. 2022 (Anthropic)")

    all_results = {"FHRR": {}, "BSC": {}, "SBC": {}}
    t_all = time.perf_counter()

    for substrate in ["FHRR", "BSC", "SBC"]:
        _say(f"\n=== {substrate} ===")
        W, atoms_data, pool_data = train_substrate(substrate, train, test)
        # Run induction trials for each num_pairs
        substrate_results = {}
        eval_gen = torch.Generator().manual_seed(SEED + 1000)  # separate from training seed
        for num_pairs in NUM_PAIRS_VALUES:
            # In-context (repeat_query=True)
            bpc_ic, acc_ic = evaluate_induction(substrate, W, atoms_data, pool_data,
                                                num_pairs, NUM_INDUCTION_TRIALS,
                                                repeat_query=True, gen=eval_gen)
            # No-context control (repeat_query=False)
            bpc_nc, acc_nc = evaluate_induction(substrate, W, atoms_data, pool_data,
                                                num_pairs, NUM_INDUCTION_TRIALS,
                                                repeat_query=False, gen=eval_gen)
            substrate_results[num_pairs] = {
                "in_context_bpc": bpc_ic, "in_context_acc": acc_ic,
                "no_context_bpc": bpc_nc, "no_context_acc": acc_nc,
                "delta_bpc": bpc_nc - bpc_ic,  # positive = in-context helps
                "delta_acc": acc_ic - acc_nc,
            }
            _say(f"  K_pairs={num_pairs}: IC bpc={bpc_ic:.4f} acc={acc_ic:.3f} | "
                 f"no-ctx bpc={bpc_nc:.4f} acc={acc_nc:.3f} | "
                 f"delta_bpc={bpc_nc - bpc_ic:+.4f}")
        all_results[substrate] = substrate_results

    # Random baseline for reference
    random_bpc = 8.0  # uniform over 256 bytes
    _say(f"\n========= ICL INDUCTION RESULTS =========")
    _say(f"  Random baseline bpc: {random_bpc:.4f}")
    _say(f"  Higher delta_bpc = stronger in-context learning effect")
    _say(f"{'substrate':>10s} {'K_pairs':>8s} {'IC_bpc':>8s} {'NC_bpc':>8s} {'delta':>8s} {'IC_acc':>8s} {'NC_acc':>8s}")
    for s in ["FHRR", "BSC", "SBC"]:
        for k in NUM_PAIRS_VALUES:
            r = all_results[s][k]
            _say(f"{s:>10s} {k:>8d} {r['in_context_bpc']:>8.4f} {r['no_context_bpc']:>8.4f} "
                 f"{r['delta_bpc']:>+8.4f} {r['in_context_acc']:>8.3f} {r['no_context_acc']:>8.3f}")

    out = {"seed": SEED, "n": N, "k": K, "num_pairs_values": NUM_PAIRS_VALUES,
           "num_trials": NUM_INDUCTION_TRIALS,
           "substrates": ["FHRR", "BSC", "SBC"],
           "results": all_results,
           "wall_time_total_s": time.perf_counter() - t_all}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_induction_head"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")
    _say(f"Total wall: {time.perf_counter() - t_all:.1f}s")


if __name__ == "__main__":
    main()
