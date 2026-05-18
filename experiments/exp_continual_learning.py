"""Wave 3a: Continual learning test across substrates (post-audit revision).

Audit findings (2026-05-18) drove these revisions:
- B is now distributionally distinct from A (Python source code vs project markdown)
  rather than two markdown subsets. Without this, byte n-gram overlap masks
  forgetting and substrate differences.
- Added joint A+B (upper bound) and B-only (intrinsic difficulty) baselines.
- Forgetting metric anchored on bpc_BEST(A) per Yildiz et al. 2024 continual
  pretraining standards, not "end of Phase 1."
- Standard CL metrics (Backward Transfer, Average Accuracy) added.

Question: do sparse codes (SBC) retain prior knowledge better than dense
codes (FHRR, BSC) when training shifts to a new distribution?

Protocol:
- A: project markdown (PLAN+NEXT_PHASE+README+PROGRESS+RESULTS+CLAUDE)
- B: Python source code (concatenated .py files from hdlab/ and experiments/)
- For each substrate, four conditions:
  1. A-only training (Phase 1 only, 15 epochs) → A_baseline
  2. B-only training (no A exposure) → B_baseline
  3. Joint A+B (interleaved, upper bound for both) → joint_A, joint_B
  4. Sequential A→B (Phase 1 A, Phase 2 B; the actual CL test)
- Forgetting = bpc_current(A) − bpc_best(A) per Yildiz 2024
- Backward Transfer (BWT) = average of (final_A − best_A) across all tasks
- Average Accuracy (AA) = mean of final bpc across all tasks

Substrates:
- FHRR (combined+modReLU, current best at 2.4994 on full corpus)
- BSC (signed+ReLU, 2.4817; also our N=8192 best 2.4344)
- SBC (M=128, no ReLU, 2.9272 perplexity but predicted to win on retention)

Lit anchors:
- van de Ven, Tuytelaars, Tolias 2022 Nat Mach Intell: three-types-of-CL
  taxonomy; ours is domain-incremental
- van de Ven et al. 2020 Nat Comm: brain-inspired replay, Phase 1/Phase 2 std
- Bricken, Davies, Singh, Krotov, Kreiman 2023 arXiv:2303.11934 *Sparse
  Distributed Memory is a Continual Learner* — direct theoretical support
  for the SBC prediction
- Yildiz et al. 2024 arXiv:2402.17400 — bpc_best(A) anchored forgetting
- Lopez-Paz & Ranzato 2017 GEM — BWT/AA metrics
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
EVAL_EVERY_EPOCHS = [5, 15]  # reduced from [1,5,10,15] — eval halved across 12 runs
RELU_B = 0.5

SUBSTRATES = ["FHRR", "BSC", "SBC"]
CONDITIONS = ["A_only", "B_only", "joint_AB", "sequential_AB"]


def _say(msg: str) -> None:
    print(msg, flush=True)


def load_corpora() -> tuple[bytes, bytes]:
    """Returns (corpus_A, corpus_B) where A is markdown and B is Python source.
    These are chosen for distributional distinctness — Python has very different
    byte n-gram statistics than English prose (parens, colons, indentation, etc).
    """
    repo = Path(__file__).resolve().parent.parent
    md_files = ["PLAN.md", "NEXT_PHASE.md", "README.md",
                "PROGRESS.md", "RESULTS.md", "CLAUDE.md"]
    A = b""
    for fn in md_files:
        p = repo / fn
        if p.exists():
            A += p.read_bytes() + b"\n\n"
    # B: concatenate Python source from hdlab/ and a curated subset of experiments/
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
# Substrate-specific atom & step functions
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


def fhrr_step(W, ctxs, tgt_idx, byte_atoms, beta, decay, arousal, n):
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


def bsc_step(W, ctxs, tgt_idx, byte_atoms, beta, decay, arousal, n):
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


def sbc_step(W, ctx_dense, tgt_idx, byte_dense, beta, decay, arousal):
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


# ============================================================
# Substrate runner with four conditions
# ============================================================

def run_substrate_condition(substrate, condition, A_train, A_test, B_train, B_test):
    """Run one substrate × one condition. Returns history with per-epoch bpc on A and B."""
    gen = torch.Generator().manual_seed(SEED)

    if substrate == "FHRR":
        byte_atoms = make_fhrr_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
        pos_atoms = make_fhrr_atoms(K, N, gen).to(DEVICE)
        W = torch.zeros((N, N), dtype=torch.complex64, device=DEVICE)
        pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.complex64, device=DEVICE)
        is_complex = True
    elif substrate == "BSC":
        byte_atoms = make_bsc_atoms(VOCAB_SIZE, N, gen).to(DEVICE)
        pos_atoms = make_bsc_atoms(K, N, gen).to(DEVICE)
        W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
        pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
        is_complex = False
    elif substrate == "SBC":
        byte_atoms_idx = make_sbc_atoms(VOCAB_SIZE, gen).to(DEVICE)
        pos_atoms_idx = make_sbc_atoms(K, gen).to(DEVICE)
        byte_dense = sbc_to_dense(byte_atoms_idx, DEVICE)
        W = torch.zeros((N, N), dtype=torch.float32, device=DEVICE)
        pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=DEVICE)
        is_complex = False

    pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_used = 0
    pool_idx = 0
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)

    A_train_idx, A_train_tgt, A_test_idx, A_test_tgt = make_index_arrays(A_train, A_test, DEVICE)
    B_train_idx, B_train_tgt, B_test_idx, B_test_tgt = make_index_arrays(B_train, B_test, DEVICE)

    def build_ctx(idx_batch):
        if substrate == "FHRR": return fhrr_build_ctx(byte_atoms, pos_atoms, idx_batch)
        if substrate == "BSC": return bsc_build_ctx(byte_atoms, pos_atoms, idx_batch)
        if substrate == "SBC": return sbc_build_ctx(byte_atoms_idx, pos_atoms_idx, idx_batch, DEVICE)

    def train_step(ctxs, tgt_idx):
        if substrate == "FHRR": fhrr_step(W, ctxs, tgt_idx, byte_atoms, BETA, DECAY, AROUSAL, N)
        elif substrate == "BSC": bsc_step(W, ctxs, tgt_idx, byte_atoms, BETA, DECAY, AROUSAL, N)
        elif substrate == "SBC": sbc_step(W, ctxs, tgt_idx, byte_dense, BETA, DECAY, AROUSAL)

    def predict_W(ctxs):
        if substrate == "FHRR": return fhrr_predict_W(W, ctxs, byte_atoms, BETA)
        if substrate == "BSC": return bsc_predict_W(W, ctxs, byte_atoms, BETA)
        if substrate == "SBC": return sbc_predict_W(W, ctxs, byte_dense, BETA)

    def predict_pool(ctxs):
        if is_complex: return predict_pool_complex(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)
        return predict_pool_real(ctxs, pool_vecs, pool_labels, pool_used, BETA, N)

    def evaluate(test_idx, test_tgt):
        T = test_idx.shape[0]
        total_bits = 0.0
        for bs in range(0, T, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T)
            ctxs = build_ctx(test_idx[bs:be])
            P_W = predict_W(ctxs)
            P_retr = predict_pool(ctxs)
            P = ALPHA * P_retr + (1.0 - ALPHA) * P_W
            p_true = P.gather(0, test_tgt[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
            total_bits += float(-torch.log2(p_true).sum())
        return total_bits / max(T, 1)

    def train_epoch(train_idx, train_tgt, do_pool_write):
        nonlocal pool_used, pool_idx
        T = train_idx.shape[0]
        for batch_start in range(0, T, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_tgt[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = build_ctx(idx_batch)
            train_step(ctxs, tgt_batch)
            if do_pool_write:
                dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                pool_vecs.index_copy_(0, dest, ctxs)
                pool_labels.index_copy_(0, dest, tgt_batch)
                pool_idx = (pool_idx + B) % POOL_SIZE
                pool_used = min(pool_used + B, POOL_SIZE)

    history = {"A_bpc_per_epoch": [], "B_bpc_per_epoch": [], "phase": [], "epoch_global": []}
    t_start = time.perf_counter()

    if condition == "A_only":
        for epoch in range(1, EPOCHS_PER_PHASE + 1):
            train_epoch(A_train_idx, A_train_tgt, do_pool_write=(epoch == 1))
            if epoch in EVAL_EVERY_EPOCHS:
                A_bpc = evaluate(A_test_idx, A_test_tgt)
                B_bpc = evaluate(B_test_idx, B_test_tgt)  # eval on B too even though not trained
                history["A_bpc_per_epoch"].append(A_bpc)
                history["B_bpc_per_epoch"].append(B_bpc)
                history["phase"].append("A")
                history["epoch_global"].append(epoch)
                _say(f"    [{substrate}/{condition} ep={epoch}] A={A_bpc:.4f}  B={B_bpc:.4f}  ({time.perf_counter()-t_start:.1f}s)")

    elif condition == "B_only":
        for epoch in range(1, EPOCHS_PER_PHASE + 1):
            train_epoch(B_train_idx, B_train_tgt, do_pool_write=(epoch == 1))
            if epoch in EVAL_EVERY_EPOCHS:
                A_bpc = evaluate(A_test_idx, A_test_tgt)
                B_bpc = evaluate(B_test_idx, B_test_tgt)
                history["A_bpc_per_epoch"].append(A_bpc)
                history["B_bpc_per_epoch"].append(B_bpc)
                history["phase"].append("B")
                history["epoch_global"].append(epoch)
                _say(f"    [{substrate}/{condition} ep={epoch}] A={A_bpc:.4f}  B={B_bpc:.4f}  ({time.perf_counter()-t_start:.1f}s)")

    elif condition == "joint_AB":
        # Subsample B to A's batch count per epoch for a controlled joint baseline.
        # Each epoch: do all of A's batches + a same-count random sample of B's batches,
        # alternated. This matches standard "joint training" practice and bounds work.
        n_a_batches = (A_train_idx.shape[0] + BATCH_SIZE - 1) // BATCH_SIZE
        sub_gen = torch.Generator(device="cpu").manual_seed(SEED + 999)
        for epoch in range(1, EPOCHS_PER_PHASE + 1):
            # Sample n_a_batches random batch starts from B
            n_b_avail = B_train_idx.shape[0]
            b_starts = torch.randint(0, max(n_b_avail - BATCH_SIZE, 1), (n_a_batches,), generator=sub_gen).tolist()
            # Iterate through A's batches and subsampled B's batches in alternation
            for a_batch_idx in range(n_a_batches):
                a_start = a_batch_idx * BATCH_SIZE
                a_end = min(a_start + BATCH_SIZE, A_train_idx.shape[0])
                if a_end > a_start:
                    ctxs = build_ctx(A_train_idx[a_start:a_end])
                    train_step(ctxs, A_train_tgt[a_start:a_end])
                    if epoch == 1:
                        B = ctxs.shape[0]
                        dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                        pool_vecs.index_copy_(0, dest, ctxs)
                        pool_labels.index_copy_(0, dest, A_train_tgt[a_start:a_end])
                        pool_idx = (pool_idx + B) % POOL_SIZE
                        pool_used = min(pool_used + B, POOL_SIZE)
                b_start = b_starts[a_batch_idx]
                b_end = min(b_start + BATCH_SIZE, B_train_idx.shape[0])
                if b_end > b_start:
                    ctxs = build_ctx(B_train_idx[b_start:b_end])
                    train_step(ctxs, B_train_tgt[b_start:b_end])
                    if epoch == 1:
                        B = ctxs.shape[0]
                        dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                        pool_vecs.index_copy_(0, dest, ctxs)
                        pool_labels.index_copy_(0, dest, B_train_tgt[b_start:b_end])
                        pool_idx = (pool_idx + B) % POOL_SIZE
                        pool_used = min(pool_used + B, POOL_SIZE)
            if epoch in EVAL_EVERY_EPOCHS:
                A_bpc = evaluate(A_test_idx, A_test_tgt)
                B_bpc = evaluate(B_test_idx, B_test_tgt)
                history["A_bpc_per_epoch"].append(A_bpc)
                history["B_bpc_per_epoch"].append(B_bpc)
                history["phase"].append("joint")
                history["epoch_global"].append(epoch)
                _say(f"    [{substrate}/{condition} ep={epoch}] A={A_bpc:.4f}  B={B_bpc:.4f}  ({time.perf_counter()-t_start:.1f}s)")

    elif condition == "sequential_AB":
        # Phase 1: train A
        for epoch in range(1, EPOCHS_PER_PHASE + 1):
            train_epoch(A_train_idx, A_train_tgt, do_pool_write=(epoch == 1))
            if epoch in EVAL_EVERY_EPOCHS:
                A_bpc = evaluate(A_test_idx, A_test_tgt)
                B_bpc = evaluate(B_test_idx, B_test_tgt)
                history["A_bpc_per_epoch"].append(A_bpc)
                history["B_bpc_per_epoch"].append(B_bpc)
                history["phase"].append("A")
                history["epoch_global"].append(epoch)
                _say(f"    [{substrate}/{condition} P1 ep={epoch}] A={A_bpc:.4f}  B={B_bpc:.4f}  ({time.perf_counter()-t_start:.1f}s)")
        # Phase 2: train B (this is where forgetting of A is measured)
        for epoch in range(1, EPOCHS_PER_PHASE + 1):
            train_epoch(B_train_idx, B_train_tgt, do_pool_write=(epoch == 1))
            if epoch in EVAL_EVERY_EPOCHS:
                A_bpc = evaluate(A_test_idx, A_test_tgt)
                B_bpc = evaluate(B_test_idx, B_test_tgt)
                history["A_bpc_per_epoch"].append(A_bpc)
                history["B_bpc_per_epoch"].append(B_bpc)
                history["phase"].append("B")
                history["epoch_global"].append(EPOCHS_PER_PHASE + epoch)
                _say(f"    [{substrate}/{condition} P2 ep={epoch}] A={A_bpc:.4f}  B={B_bpc:.4f}  ({time.perf_counter()-t_start:.1f}s)")

    return {"substrate": substrate, "condition": condition, "history": history,
            "wall_s": time.perf_counter() - t_start}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--substrate", choices=["FHRR", "BSC", "SBC", "all"], default="all")
    parser.add_argument("--condition", choices=["A_only", "B_only", "joint_AB", "sequential_AB", "all"],
                        default="all")
    return parser.parse_args()


def main():
    args = parse_args()
    substrates_to_run = SUBSTRATES if args.substrate == "all" else [args.substrate]
    conditions_to_run = CONDITIONS if args.condition == "all" else [args.condition]
    chunk_tag = f"{args.substrate}_{args.condition}" if (args.substrate != "all" or args.condition != "all") else "all"
    _say(f"Chunk: substrate={args.substrate}, condition={args.condition}")
    _say("Loading corpora...")
    A, B = load_corpora()
    _say(f"  A (markdown): {len(A)} bytes")
    _say(f"  B (python source): {len(B)} bytes")

    A_train, A_test = make_train_test(A)
    B_train, B_test = make_train_test(B)
    _say(f"  A train={len(A_train)}, test={len(A_test)}")
    _say(f"  B train={len(B_train)}, test={len(B_test)}")

    _say(f"\nContinual learning (Wave 3a, post-audit)")
    _say(f"  N={N}, K={K}, epochs_per_phase={EPOCHS_PER_PHASE}")
    _say(f"  Substrates: {SUBSTRATES}")
    _say(f"  Conditions: {CONDITIONS}")
    _say(f"  Total runs: {len(SUBSTRATES) * len(CONDITIONS)}")
    _say(f"  Lit: van de Ven 2020/2022; Bricken et al. 2023 SDM-as-CL; Yildiz 2024")
    _say(f"  Prediction: SBC forgetting (sequential A then B) less than BSC and FHRR forgetting")

    all_runs = []
    t_all = time.perf_counter()
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_continual_learning"
    out_path.mkdir(parents=True, exist_ok=True)
    for substrate in substrates_to_run:
        for condition in conditions_to_run:
            _say(f"\n=== {substrate} / {condition} ===")
            torch.cuda.empty_cache()
            r = run_substrate_condition(substrate, condition, A_train, A_test, B_train, B_test)
            all_runs.append(r)
            # Incremental save: write each completed chunk to its own JSON
            chunk_file = out_path / f"chunk_{substrate}_{condition}.json"
            chunk_file.write_text(json.dumps(r, indent=2, default=str))
            _say(f"  -> saved {chunk_file.name}")

    # Compute summary metrics per substrate
    _say(f"\n========= CONTINUAL LEARNING METRICS =========")
    summary = []
    for substrate in substrates_to_run:
        runs = {r["condition"]: r for r in all_runs if r["substrate"] == substrate}
        # Only compute summary if all 4 conditions are present
        if not all(c in runs for c in CONDITIONS):
            missing = [c for c in CONDITIONS if c not in runs]
            _say(f"  {substrate}: skipping summary (missing conditions: {missing})")
            continue
        A_only_history = runs["A_only"]["history"]
        B_only_history = runs["B_only"]["history"]
        joint_history = runs["joint_AB"]["history"]
        seq_history = runs["sequential_AB"]["history"]
        # Baselines
        A_baseline_best = min(A_only_history["A_bpc_per_epoch"])  # best on A from A-only training
        B_baseline_best = min(B_only_history["B_bpc_per_epoch"])  # best on B from B-only training
        # Joint upper bound
        joint_A_final = joint_history["A_bpc_per_epoch"][-1]
        joint_B_final = joint_history["B_bpc_per_epoch"][-1]
        # Sequential measurements
        # Phase 1 ends at index EVAL_EVERY_EPOCHS_count - 1 in seq_history
        phase1_len = sum(1 for p in seq_history["phase"] if p == "A")
        seq_A_after_P1 = seq_history["A_bpc_per_epoch"][phase1_len - 1]
        seq_A_after_P2 = seq_history["A_bpc_per_epoch"][-1]
        seq_B_after_P2 = seq_history["B_bpc_per_epoch"][-1]
        # bpc_best(A) anchored forgetting (Yildiz 2024)
        A_best_anywhere = min(seq_history["A_bpc_per_epoch"])  # best A bpc reached during sequential run
        forgetting_yildiz = seq_A_after_P2 - A_best_anywhere
        # Naive forgetting (audit-rejected metric, retained for back-compat)
        forgetting_naive = seq_A_after_P2 - seq_A_after_P1
        # BWT: how much did we change the best-on-A bpc (negative = forgot)
        bwt = -forgetting_yildiz
        # Average Accuracy: mean of final-task bpc across tasks
        avg_bpc = (seq_A_after_P2 + seq_B_after_P2) / 2
        summary.append({
            "substrate": substrate,
            "A_baseline_best": A_baseline_best,
            "B_baseline_best": B_baseline_best,
            "joint_A_final": joint_A_final,
            "joint_B_final": joint_B_final,
            "seq_A_after_P1": seq_A_after_P1,
            "seq_A_after_P2": seq_A_after_P2,
            "seq_B_after_P2": seq_B_after_P2,
            "forgetting_yildiz": forgetting_yildiz,
            "forgetting_naive": forgetting_naive,
            "BWT": bwt,
            "average_accuracy_bpc": avg_bpc,
        })
        _say(f"\n  {substrate}:")
        _say(f"    A-only best:     {A_baseline_best:.4f}")
        _say(f"    B-only best:     {B_baseline_best:.4f}")
        _say(f"    Joint A final:   {joint_A_final:.4f}")
        _say(f"    Joint B final:   {joint_B_final:.4f}")
        _say(f"    Seq A after P1:  {seq_A_after_P1:.4f}")
        _say(f"    Seq A after P2:  {seq_A_after_P2:.4f}  (forgetting_yildiz = {forgetting_yildiz:+.4f}, naive = {forgetting_naive:+.4f})")
        _say(f"    Seq B after P2:  {seq_B_after_P2:.4f}")
        _say(f"    BWT = {bwt:+.4f}, AA (bpc) = {avg_bpc:.4f}")

    # Verdict on the SBC retention prediction (only if we have summaries to compare)
    forgettings = {s["substrate"]: s["forgetting_yildiz"] for s in summary}
    if forgettings:
        best_substrate = min(forgettings, key=forgettings.get)
        _say(f"\n  Least forgetting (Yildiz): {best_substrate} ({forgettings[best_substrate]:+.4f})")
        if best_substrate == "SBC":
            _say(f"  PREDICTION SUPPORTED: SBC (sparse codes) retain prior knowledge best.")
            _say(f"  Cf. Bricken et al. 2023: 'SDM is a Continual Learner'")
        else:
            _say(f"  Prediction NOT supported at this configuration.")
            _say(f"  Rehab candidates: larger N, sparser SBC (M=256 / B_size=16), longer epochs.")
    else:
        _say(f"\n  Partial run: no complete substrate summaries yet (chunk-mode running).")

    out = {"seed": SEED, "n": N, "k": K, "epochs_per_phase": EPOCHS_PER_PHASE,
           "substrates": SUBSTRATES, "conditions": CONDITIONS,
           "all_runs": all_runs, "summary": summary,
           "wall_time_total_s": time.perf_counter() - t_all}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_continual_learning"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")
    _say(f"Total wall: {time.perf_counter() - t_all:.1f}s")


if __name__ == "__main__":
    main()
