"""Wave 3a.5: Catastrophic forgetting mitigations across substrates.

Goal: decompose the +2.15 bpc forgetting we saw on FHRR/sequential_AB into:
- forgetting from multiplicative W decay (each batch shrinks W by ~0.0001)
- forgetting from overwriting W with B-target updates
- forgetting from overwriting the pool ring-buffer in Phase 2

Three mitigations, each isolating one mechanism:

1. `decay_off_P2`: set decay=0 during Phase 2. W still gets new B updates but
   isn't multiplicatively annihilated. Tests: how much forgetting is from
   pure decay over 120K+ steps?

2. `W_frozen_P2`: W is frozen during Phase 2. Only the pool can absorb B
   content. Tests: if W is preserved, can the pool alone hold B without
   destroying A? Equivalently: how good is our pool as B-only memory?

3. `dual_pool`: Phase 2 writes to a SECOND pool (pool_B); pool_A is
   preserved. Combined pool retrieval queries both. Tests: how much
   forgetting is from pool overwrite, holding W behavior constant.

Plus baseline (no mitigation) — we already have this from Wave 3a results,
but include it here for direct comparison if desired.

Cross-substrate: 3 mitigations × 3 substrates (FHRR/BSC/SBC) = 9 runs.
Each is a sequential_AB protocol (Phase 1 on A, Phase 2 on B) with the
specified mitigation active during Phase 2.

Per-chunk runtime: ~3-12 min depending on substrate and corpus size.
Total estimated wall: ~1-2 hours.

Lit:
- Yildiz et al. 2024 arXiv:2402.17400 — continual pretraining forgetting
  curves and metric standardization.
- Bricken et al. 2023 arXiv:2303.11934 — SDM-as-CL: sparse codes prevent
  catastrophic forgetting (the substrate-level claim).
- Lopez-Paz Ranzato 2017 GEM, Kirkpatrick et al. 2017 EWC — architectural
  mitigations (we test simpler versions).
"""

from __future__ import annotations

import argparse
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
K = 4
AROUSAL = 0.3
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3
DECAY = 1e-4
EPOCHS_PER_PHASE = 15
EVAL_AT = [5, 15]
RELU_B = 0.5

SUBSTRATES = ["FHRR", "BSC", "SBC"]
MITIGATIONS = ["baseline", "decay_off_P2", "W_frozen_P2", "dual_pool"]


def _say(msg: str) -> None:
    print(msg, flush=True)


def load_corpora() -> tuple[bytes, bytes]:
    repo = Path(__file__).resolve().parent.parent
    md_files = ["PLAN.md", "NEXT_PHASE.md", "README.md",
                "PROGRESS.md", "RESULTS.md", "CLAUDE.md"]
    A = b""
    for fn in md_files:
        p = repo / fn
        if p.exists():
            A += p.read_bytes() + b"\n\n"
    py_dirs = [repo / "hdlab", repo / "experiments"]
    B = b""
    for d in py_dirs:
        if d.exists():
            for p in sorted(d.glob("*.py")):
                B += p.read_bytes() + b"\n\n"
    return A, B


def make_train_test(corpus, frac=0.8):
    cut = int(len(corpus) * frac)
    return corpus[:cut], corpus[cut:]


def make_index_arrays(corpus_train, corpus_test, device):
    pad = bytes([PAD_BYTE]) * K
    padded_train = pad + corpus_train
    padded_test = pad + corpus_test
    T_total = len(padded_train) - K
    T_test = len(padded_test) - K
    train_bytes = torch.tensor(list(padded_train), dtype=torch.long).to(device)
    test_bytes = torch.tensor(list(padded_test), dtype=torch.long).to(device)
    offsets = torch.arange(K - 1, -1, -1, device=device)
    pos_train = torch.arange(T_total, device=device)
    pos_test = torch.arange(T_test, device=device)
    train_idx = train_bytes[pos_train.unsqueeze(1) + offsets.unsqueeze(0)]
    train_targets = train_bytes[pos_train + K]
    test_idx = test_bytes[pos_test.unsqueeze(1) + offsets.unsqueeze(0)]
    test_targets = test_bytes[pos_test + K]
    return train_idx, train_targets, test_idx, test_targets


# ============================================================
# Substrate functions
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


def fhrr_step(W, ctxs, tgt_idx, byte_atoms, beta, decay, arousal, n, frozen=False):
    if frozen:
        return  # no W update
    P_W = fhrr_predict_W(W, ctxs, byte_atoms, beta)
    targets = byte_atoms[tgt_idx]
    expected = P_W.T.to(byte_atoms.dtype) @ byte_atoms
    errors = targets - expected
    dW = errors.T @ ctxs.conj() / n
    if decay > 0:
        W.mul_(1.0 - decay)
    W.add_(dW, alpha=arousal)


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


def bsc_step(W, ctxs, tgt_idx, byte_atoms, beta, decay, arousal, n, frozen=False):
    if frozen:
        return
    P_W = bsc_predict_W(W, ctxs, byte_atoms, beta)
    targets = byte_atoms[tgt_idx]
    expected = P_W.T @ byte_atoms
    errors = targets - expected
    dW = errors.T @ ctxs / n
    if decay > 0:
        W.mul_(1.0 - decay)
    W.add_(dW, alpha=arousal)


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


def sbc_step(W, ctx_dense, tgt_idx, byte_dense, beta, decay, arousal, frozen=False):
    if frozen:
        return
    P_W = sbc_predict_W(W, ctx_dense, byte_dense, beta)
    targets = byte_dense[tgt_idx]
    expected = P_W.T @ byte_dense
    errors = targets - expected
    dW = errors.T @ ctx_dense / N
    if decay > 0:
        W.mul_(1.0 - decay)
    W.add_(dW, alpha=arousal)


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


def run_substrate_mitigation(substrate, mitigation, A_train, A_test, B_train, B_test):
    """Run sequential_AB with specified mitigation during Phase 2."""
    gen = torch.Generator().manual_seed(SEED)

    if substrate == "FHRR":
        byte_atoms = make_fhrr_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
        pos_atoms = make_fhrr_atoms(K, N, gen).to(DEVICE)
        W = torch.zeros((N, N), dtype=torch.complex64, device=DEVICE)
        pool_vecs_A = torch.zeros((POOL_SIZE, N), dtype=torch.complex64, device=DEVICE)
        pool_vecs_B = torch.zeros((POOL_SIZE, N), dtype=torch.complex64, device=DEVICE)
        is_complex = True
    elif substrate == "BSC":
        byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
        pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
        W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
        pool_vecs_A = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
        pool_vecs_B = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
        is_complex = False
    elif substrate == "SBC":
        byte_atoms_idx = make_sbc_atoms(VOCAB_SIZE, gen).to(DEVICE)
        pos_atoms_idx = make_sbc_atoms(K, gen).to(DEVICE)
        byte_dense = sbc_to_dense(byte_atoms_idx, DEVICE)
        W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
        pool_vecs_A = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
        pool_vecs_B = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
        is_complex = False

    pool_labels_A = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_labels_B = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_A_used = 0
    pool_A_idx = 0
    pool_B_used = 0
    pool_B_idx = 0
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)

    A_train_idx, A_train_tgt, A_test_idx, A_test_tgt = make_index_arrays(A_train, A_test, DEVICE)
    B_train_idx, B_train_tgt, B_test_idx, B_test_tgt = make_index_arrays(B_train, B_test, DEVICE)

    use_dual_pool = (mitigation == "dual_pool")

    def build_ctx(idx_batch):
        if substrate == "FHRR": return fhrr_build_ctx(byte_atoms, pos_atoms, idx_batch)
        if substrate == "BSC": return bsc_build_ctx(byte_atoms, pos_atoms, idx_batch)
        if substrate == "SBC": return sbc_build_ctx(byte_atoms_idx, pos_atoms_idx, idx_batch, DEVICE)

    def step(ctxs, tgt_idx, decay_active, frozen):
        if substrate == "FHRR":
            fhrr_step(W, ctxs, tgt_idx, byte_atoms, BETA, decay_active, AROUSAL, N, frozen=frozen)
        elif substrate == "BSC":
            bsc_step(W, ctxs, tgt_idx, byte_atoms, BETA, decay_active, AROUSAL, N, frozen=frozen)
        elif substrate == "SBC":
            sbc_step(W, ctxs, tgt_idx, byte_dense, BETA, decay_active, AROUSAL, frozen=frozen)

    def predict_W(ctxs):
        if substrate == "FHRR": return fhrr_predict_W(W, ctxs, byte_atoms, BETA)
        if substrate == "BSC": return bsc_predict_W(W, ctxs, byte_atoms, BETA)
        if substrate == "SBC": return sbc_predict_W(W, ctxs, byte_dense, BETA)

    def predict_combined_pool(ctxs):
        # For dual_pool: query BOTH pools, combine retrieval distributions
        if not use_dual_pool:
            if is_complex:
                return predict_pool_complex(ctxs, pool_vecs_A, pool_labels_A, pool_A_used, BETA, N)
            return predict_pool_real(ctxs, pool_vecs_A, pool_labels_A, pool_A_used, BETA, N)
        # Dual pool: combine A and B retrievals weighted by pool sizes
        if is_complex:
            P_A = predict_pool_complex(ctxs, pool_vecs_A, pool_labels_A, pool_A_used, BETA, N)
            P_B = predict_pool_complex(ctxs, pool_vecs_B, pool_labels_B, pool_B_used, BETA, N)
        else:
            P_A = predict_pool_real(ctxs, pool_vecs_A, pool_labels_A, pool_A_used, BETA, N)
            P_B = predict_pool_real(ctxs, pool_vecs_B, pool_labels_B, pool_B_used, BETA, N)
        # Weight by pool occupancy; if one pool is empty, the other wins entirely
        tot = max(pool_A_used + pool_B_used, 1)
        w_A = pool_A_used / tot
        w_B = pool_B_used / tot
        return w_A * P_A + w_B * P_B

    def evaluate(test_idx, test_tgt):
        T = test_idx.shape[0]
        total_bits = 0.0
        for bs in range(0, T, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T)
            ctxs = build_ctx(test_idx[bs:be])
            P_W = predict_W(ctxs)
            P_retr = predict_combined_pool(ctxs)
            P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
            p_true = P.gather(0, test_tgt[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            total_bits += float(-torch.log2(p_true).sum())
        return total_bits / max(T, 1)

    def train_epoch(train_idx, train_tgt, phase, epoch):
        nonlocal pool_A_used, pool_A_idx, pool_B_used, pool_B_idx
        # Decide if W is frozen and what decay value to use
        frozen = (phase == "B" and mitigation == "W_frozen_P2")
        decay_active = DECAY
        if phase == "B" and mitigation == "decay_off_P2":
            decay_active = 0.0
        T = train_idx.shape[0]
        for batch_start in range(0, T, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_tgt[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = build_ctx(idx_batch)
            step(ctxs, tgt_batch, decay_active, frozen)
            # Pool write: epoch 1 of each phase
            if epoch == 1:
                if use_dual_pool:
                    # Write to phase-specific pool
                    if phase == "A":
                        dest = (pool_A_idx + arange_b[:B]) % POOL_SIZE
                        pool_vecs_A.index_copy_(0, dest, ctxs)
                        pool_labels_A.index_copy_(0, dest, tgt_batch)
                        pool_A_idx = (pool_A_idx + B) % POOL_SIZE
                        pool_A_used = min(pool_A_used + B, POOL_SIZE)
                    else:  # phase == "B"
                        dest = (pool_B_idx + arange_b[:B]) % POOL_SIZE
                        pool_vecs_B.index_copy_(0, dest, ctxs)
                        pool_labels_B.index_copy_(0, dest, tgt_batch)
                        pool_B_idx = (pool_B_idx + B) % POOL_SIZE
                        pool_B_used = min(pool_B_used + B, POOL_SIZE)
                else:
                    # Single-pool: just keep writing to pool_A (gets overwritten by B in baseline)
                    dest = (pool_A_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs_A.index_copy_(0, dest, ctxs)
                    pool_labels_A.index_copy_(0, dest, tgt_batch)
                    pool_A_idx = (pool_A_idx + B) % POOL_SIZE
                    pool_A_used = min(pool_A_used + B, POOL_SIZE)

    history = {"A_bpc_per_epoch": [], "B_bpc_per_epoch": [], "phase": [], "epoch_global": []}
    t_start = time.perf_counter()

    # Phase 1: train A
    _say(f"  Phase 1: train A (no mitigation)")
    for epoch in range(1, EPOCHS_PER_PHASE + 1):
        train_epoch(A_train_idx, A_train_tgt, phase="A", epoch=epoch)
        if epoch in EVAL_AT:
            A_bpc = evaluate(A_test_idx, A_test_tgt)
            B_bpc = evaluate(B_test_idx, B_test_tgt)
            history["A_bpc_per_epoch"].append(A_bpc)
            history["B_bpc_per_epoch"].append(B_bpc)
            history["phase"].append("A")
            history["epoch_global"].append(epoch)
            _say(f"    [{substrate}/{mitigation} P1 ep={epoch}] A={A_bpc:.4f}  B={B_bpc:.4f}  ({time.perf_counter()-t_start:.1f}s)")

    # Phase 2: train B with mitigation active
    _say(f"  Phase 2: train B with mitigation={mitigation}")
    for epoch in range(1, EPOCHS_PER_PHASE + 1):
        train_epoch(B_train_idx, B_train_tgt, phase="B", epoch=epoch)
        if epoch in EVAL_AT:
            A_bpc = evaluate(A_test_idx, A_test_tgt)
            B_bpc = evaluate(B_test_idx, B_test_tgt)
            history["A_bpc_per_epoch"].append(A_bpc)
            history["B_bpc_per_epoch"].append(B_bpc)
            history["phase"].append("B")
            history["epoch_global"].append(EPOCHS_PER_PHASE + epoch)
            _say(f"    [{substrate}/{mitigation} P2 ep={epoch}] A={A_bpc:.4f}  B={B_bpc:.4f}  ({time.perf_counter()-t_start:.1f}s)")

    A_after_P1 = history["A_bpc_per_epoch"][1]  # epoch 15 of Phase 1
    A_after_P2 = history["A_bpc_per_epoch"][-1]
    B_after_P2 = history["B_bpc_per_epoch"][-1]
    forgetting = A_after_P2 - A_after_P1

    return {
        "substrate": substrate,
        "mitigation": mitigation,
        "history": history,
        "A_after_P1": A_after_P1,
        "A_after_P2": A_after_P2,
        "B_after_P2": B_after_P2,
        "forgetting": forgetting,
        "wall_s": time.perf_counter() - t_start,
    }


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--substrate", choices=SUBSTRATES + ["all"], default="all")
    p.add_argument("--mitigation", choices=MITIGATIONS + ["all"], default="all")
    return p.parse_args()


def main():
    args = parse_args()
    substrates_to_run = SUBSTRATES if args.substrate == "all" else [args.substrate]
    mitigations_to_run = MITIGATIONS if args.mitigation == "all" else [args.mitigation]
    _say(f"Chunk: substrate={args.substrate}, mitigation={args.mitigation}")

    _say("Loading corpora...")
    A, B = load_corpora()
    _say(f"  A (markdown): {len(A)} bytes")
    _say(f"  B (python source): {len(B)} bytes")
    A_train, A_test = make_train_test(A)
    B_train, B_test = make_train_test(B)

    _say(f"\nWave 3a.5: catastrophic forgetting mitigations")
    _say(f"  Substrates: {substrates_to_run}")
    _say(f"  Mitigations: {mitigations_to_run}")
    _say(f"  Protocol: sequential_AB (Phase 1 A, Phase 2 B with mitigation)")
    _say(f"  Reference (Wave 3a FHRR baseline): A_after_P2=4.6458 (forgetting +2.15)")

    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_continual_mitigations"
    out_path.mkdir(parents=True, exist_ok=True)
    all_runs = []
    t_all = time.perf_counter()
    for substrate in substrates_to_run:
        for mitigation in mitigations_to_run:
            _say(f"\n=== {substrate} / {mitigation} ===")
            torch.cuda.empty_cache()
            r = run_substrate_mitigation(substrate, mitigation, A_train, A_test, B_train, B_test)
            all_runs.append(r)
            chunk_file = out_path / f"chunk_{substrate}_{mitigation}.json"
            chunk_file.write_text(json.dumps(r, indent=2, default=str))
            _say(f"  -> saved {chunk_file.name} | forgetting={r['forgetting']:+.4f}")

    _say(f"\n========= MITIGATION SUMMARY =========")
    _say(f"{'substrate':>10s} {'mitigation':>15s} {'A_P1':>8s} {'A_P2':>8s} {'B_P2':>8s} {'forgetting':>12s}")
    for r in all_runs:
        _say(f"{r['substrate']:>10s} {r['mitigation']:>15s} "
             f"{r['A_after_P1']:>8.4f} {r['A_after_P2']:>8.4f} "
             f"{r['B_after_P2']:>8.4f} {r['forgetting']:>+12.4f}")

    out = {"seed": SEED, "n": N, "k": K, "epochs_per_phase": EPOCHS_PER_PHASE,
           "substrates": substrates_to_run, "mitigations": mitigations_to_run,
           "all_runs": all_runs, "wall_time_total_s": time.perf_counter() - t_all}
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nTotal wall: {time.perf_counter() - t_all:.1f}s")


if __name__ == "__main__":
    main()
