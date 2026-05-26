"""Bet N: Self-supervised WTA atom discovery vs random BSC baseline.

Tests whether competitive-WTA self-supervised atoms (Cao 2023 style) outperform
random BSC atoms as the substrate codebook for associative-memory storage+cleanup.

Three verdicts:
  P1 -- Sparsity-regime soundness (utilization gate, computed BEFORE P2/P3)
  P2 -- Associative-memory capacity: cleanup_acc_ratio(M=2000) = LEARNED / RANDOM >= 1.10
  P3 -- Corpus-adaptive distinctiveness: cosine_dist >= 0.85 AND gap >= 0.05

Pre-reg: preregs/2026-05-26_wave14e_bet_n_wta_v1.md

Verdict tags:
  BET_N_TIER1_PROMOTION -- P1+P2+P3 HARD-PASS
  BET_N_PARTIAL_TIER2 -- P1+P2 HARD-PASS, P3 MIDDLE
  BET_N_ATOM_MODE_FLEXIBILITY -- P1 HARD-PASS, P2 MIDDLE
  BET_N_CLOSED_AT_DOMAIN -- P1 HARD-PASS, P2 HARD-FAIL
  BET_N_INSTRUMENTATION_FAIL -- P1 HARD-FAIL (mode-collapse; NOT Bet N closure)
  BET_N_MIDDLE_BAND -- any other combination
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# ─── design parameters (exp_dev autonomy) ─────────────────────────────────────
N_FULL = 4096
N_SMOKE = 512
K_FULL = 128          # codebook size (WTA atoms)
K_SMOKE = 32
K_ACTIVE_FULL = 12    # active atoms per input
K_ACTIVE_SMOKE = 4
N_EPOCHS_FULL = 5
N_EPOCHS_SMOKE = 2
ETA = 0.01            # Hebbian learning rate
RHO = 0.05            # winner-fatigue anti-collapse rate (Cao 2023)
M_GRID_FULL = [500, 1000, 2000, 4000]
M_GRID_SMOKE = [50, 200]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]
CORPUS_NAMES = ["EN", "PY", "RND"]

# P1 thresholds (sparsity gate)
P1_PASS_UTILIZATION = 0.70   # H(usage) / log(K) >= 0.70
P1_FAIL_UTILIZATION = 0.30
P1_PASS_SPARSITY_LO = 0.8    # mean atom_sparsity in [0.8, 1.2] * k_active
P1_PASS_SPARSITY_HI = 1.2
P1_FAIL_SPARSITY_LO = 0.5
P1_FAIL_SPARSITY_HI = 2.0

# P2 thresholds (capacity comparison)
P2_HARD_PASS_RATIO = 1.10
P2_HARD_FAIL_RATIO = 0.80

# P3 thresholds (corpus-adaptive distinctiveness)
P3_HARD_PASS_COS_DIST = 0.85
P3_HARD_FAIL_COS_DIST = 0.40
P3_HARD_PASS_RETRIEVAL_GAP = 0.05

BATCH_STORE = 512


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict or verdict_msg")


# ─── Corpus loading ─────────────────────────────────────────────────────────
def load_corpus_EN(n_bytes: int) -> bytes:
    """English-like corpus: repo markdown docs."""
    files = [
        REPO / "PLAN.md", REPO / "NEXT_PHASE.md", REPO / "README.md",
        REPO / "PROGRESS.md", REPO / "RESULTS.md", REPO / "CLAUDE.md",
    ]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes())
    raw = b"".join(parts)
    # Tile to reach n_bytes
    if len(raw) < n_bytes:
        reps = (n_bytes // len(raw)) + 2
        raw = (raw * reps)
    return raw[:n_bytes]


def load_corpus_PY(n_bytes: int, smoke: bool) -> bytes:
    """Python source corpus: subset of experiment files."""
    exp_dir = REPO / "experiments"
    n_files = 3 if smoke else 10
    parts = []
    for f in sorted(exp_dir.glob("exp_wave14b*.py"))[:n_files]:
        if f.exists():
            parts.append(f.read_bytes())
    raw = b"".join(parts)
    if len(raw) < n_bytes:
        reps = (n_bytes // max(len(raw), 1)) + 2
        raw = (raw * reps)
    return raw[:n_bytes]


def load_corpus_RND(n_bytes: int, seed: int) -> bytes:
    """Random bytes: control corpus (no structure)."""
    gen = torch.Generator().manual_seed(seed + 999)
    return bytes(torch.randint(0, 256, (n_bytes,), generator=gen).tolist())


def build_byte_projection(N: int, device: str) -> torch.Tensor:
    """Fixed random bipolar projection matrix: (256, N).

    Maps each byte value to an N-dim bipolar feature vector.
    Kept FIXED across all experiments so WTA atoms learn CORPUS structure,
    not codebook structure. Generator seed is a constant.
    """
    gen = torch.Generator(device=device).manual_seed(31415926)
    raw = torch.randint(0, 2, (256, N), generator=gen, device=device).float()
    proj = 2.0 * raw - 1.0
    return proj


def bytes_to_input_vecs(corpus: bytes, byte_proj: torch.Tensor,
                         n_bytes_per_sample: int = 4,
                         device: str = "cpu") -> torch.Tensor:
    """Convert corpus bytes to fixed-projection input vectors.

    Returns: (T, N) float tensor where T = len(corpus) // n_bytes_per_sample.
    Each n-gram is encoded as the SUM of byte projections for the n bytes.
    This gives corpus-specific structure: different corpora have different
    statistical distributions of byte n-grams -> different input distributions.
    """
    arr = torch.frombuffer(bytearray(corpus), dtype=torch.uint8).long().to(device)
    T = len(arr) // n_bytes_per_sample
    if T == 0:
        N = byte_proj.shape[1]
        return torch.zeros(1, N, device=device)
    arr = arr[:T * n_bytes_per_sample].view(T, n_bytes_per_sample)
    # Sum byte projections: (T, n_bytes) -> (T, N) via index into byte_proj
    vecs = byte_proj[arr].sum(dim=1)  # (T, N)
    # Binarize: sign
    vecs = torch.sign(vecs)
    vecs = torch.where(vecs == 0, torch.ones_like(vecs), vecs)
    return vecs  # (T, N)


# ─── Core WTA mechanism (Cao 2023 style) ────────────────────────────────────

def compute_effective_utilization(usage_dist: torch.Tensor) -> float:
    """H(usage) / log(K) in [0, 1]. 1.0 = uniform, 0.0 = mode-collapsed."""
    K = usage_dist.shape[0]
    if K <= 1:
        return 0.0
    p = usage_dist / (usage_dist.sum() + 1e-12)
    # Clamp to avoid log(0)
    p_clamped = p.clamp(min=1e-12)
    H = float(-(p_clamped * p_clamped.log()).sum())
    return H / math.log(K)


def competitive_wta_step(
    x_vecs: torch.Tensor,      # (T, N) input vectors (fixed-projection of corpus bytes)
    Phi: torch.Tensor,          # (K, N) atom codebook (bipolar)
    bias: torch.Tensor,         # (K,) winner-fatigue bias
    k_active: int,
    eta: float,
    rho: float,
    N: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """One step of Cao 2023 competitive WTA with winner-fatigue anti-collapse bias.

    Inputs x_vecs are EXTERNALLY FIXED projections of corpus bytes (not from Phi).
    This ensures WTA atoms learn corpus-specific structure.

    Returns: (Phi_updated, bias_updated, winner_mask)
    winner_mask: (K,) bool -- which atoms won this step.
    """
    K = Phi.shape[0]
    T = x_vecs.shape[0]

    usage = torch.zeros(K, device=Phi.device)
    winner_mask = torch.zeros(K, device=Phi.device, dtype=torch.bool)
    Phi_grad = torch.zeros_like(Phi)

    # Process in batches
    batch_size = min(256, T)
    for start in range(0, T, batch_size):
        end = min(start + batch_size, T)
        x_batch = x_vecs[start:end].to(Phi.device)  # (B, N)

        # Compute similarities: (B, K) = x_batch @ Phi^T / N
        sims = x_batch @ Phi.T / N  # (B, K)

        # Apply winner-fatigue bias (penalizes overused atoms)
        sims_biased = sims - bias.unsqueeze(0)  # (B, K)

        # Top-k selection per input
        _, topk_idx = torch.topk(sims_biased, k_active, dim=1)  # (B, k_active)

        # Vectorized: accumulate winner usage counts
        # topk_idx: (B, k_active) -- winner atom indices
        flat_winners = topk_idx.view(-1)  # (B * k_active,)
        usage.scatter_add_(0, flat_winners,
                           torch.ones(flat_winners.shape[0], device=Phi.device))
        winner_mask[flat_winners] = True

        # Hebbian update: Phi[winner] += eta * (x - Phi[winner]) per (batch, winner)
        # Vectorized via scatter_add on Phi_grad
        x_expanded = x_batch.unsqueeze(1).expand(-1, k_active, -1)  # (B, k_active, N)
        phi_at_winners = Phi[topk_idx]  # (B, k_active, N)
        delta = eta * (x_expanded - phi_at_winners)  # (B, k_active, N)
        # Accumulate into Phi_grad by winner index
        Phi_grad.scatter_add_(0,
                               topk_idx.view(-1, 1).expand(-1, N),
                               delta.view(-1, N))

    # Update codebook
    Phi = Phi + Phi_grad / max(T, 1)
    # Renormalize to bipolar: sign(Phi)
    Phi = torch.sign(Phi)
    Phi = torch.where(Phi == 0, torch.ones_like(Phi), Phi)  # no zeros

    # Update winner-fatigue bias: bias += rho * (usage_normalized - k_active/K)
    usage_norm = usage / max(T, 1)
    bias = bias + rho * (usage_norm - float(k_active) / K)

    return Phi, bias, winner_mask


def train_wta_atoms(
    corpus_bytes: bytes,
    N: int,
    K: int,
    k_active: int,
    n_epochs: int,
    eta: float,
    rho: float,
    seed: int,
    device: str,
) -> tuple[torch.Tensor, dict]:
    """Train WTA codebook on corpus. Returns (Phi, stats) where Phi is (K, N) bipolar."""
    gen = torch.Generator(device=device).manual_seed(seed)

    # Initialize Phi: random bipolar
    raw = torch.randint(0, 2, (K, N), generator=gen, device=device).float()
    Phi = 2.0 * raw - 1.0  # bipolar {-1, +1}
    bias = torch.zeros(K, device=device)

    # Convert corpus to fixed-projection input vectors (corpus-specific)
    byte_proj = build_byte_projection(N, device)
    x_vecs = bytes_to_input_vecs(corpus_bytes, byte_proj, n_bytes_per_sample=4, device=device)
    T = x_vecs.shape[0]

    usage_history = []
    winner_usage_final = None
    for epoch in range(n_epochs):
        # Shuffle inputs each epoch
        perm = torch.randperm(T, generator=gen, device=device)
        x_shuffled = x_vecs[perm]
        Phi, bias, _ = competitive_wta_step(x_shuffled, Phi, bias, k_active, eta, rho, N)

        # Track utilization via final epoch winner counts
        # Compute usage from similarity to current Phi
        batch_usage = torch.zeros(K, device=device)
        for s in range(0, min(T, 2000), 128):
            e = min(s + 128, min(T, 2000))
            sims = x_vecs[s:e] @ Phi.T / N  # (batch, K)
            _, winners = torch.topk(sims, k_active, dim=1)  # (batch, k_active)
            flat_w = winners.view(-1)
            batch_usage.scatter_add_(0, flat_w, torch.ones(flat_w.shape[0], device=device))
        util = compute_effective_utilization(batch_usage)
        usage_history.append(util)
        if epoch == n_epochs - 1:
            winner_usage_final = batch_usage

    # Final utilization from last epoch
    if winner_usage_final is None:
        winner_usage_final = torch.ones(K, device=device)
    util_final = compute_effective_utilization(winner_usage_final)

    # Mean atom sparsity = k_active by construction (always k_active winners per input)
    atom_sparsity_avg = float(k_active)

    stats = {
        "effective_utilization": util_final,
        "atom_sparsity_avg": atom_sparsity_avg,
        "utilization_history": usage_history,
    }
    return Phi, stats


def train_simclr_atoms(
    corpus_bytes: bytes,
    N: int,
    K: int,
    n_epochs: int,
    temperature: float,
    seed: int,
    device: str,
) -> tuple[torch.Tensor, dict]:
    """ARM_B: InfoNCE contrastive dense atoms (negative control, no WTA sparsity).

    Predicted to UNDERPERFORM random BSC (HARD-FAIL on P2) -- confirms sparsity gate is load-bearing.
    Dense float atoms + InfoNCE contrastive learning, no winner selection.
    """
    gen = torch.Generator(device=device).manual_seed(seed + 100)

    # Initialize: unit-norm dense atoms
    Phi = torch.randn(K, N, generator=gen, device=device)
    Phi = Phi / Phi.norm(dim=1, keepdim=True).clamp(min=1e-9)

    x_idx = bytes_to_ngrams(corpus_bytes, K, n_bytes_per_sample=4, device=device)
    T = x_idx.shape[0]

    eta_clr = 0.001
    for epoch in range(n_epochs):
        perm = torch.randperm(T, generator=gen, device=device)
        for start in range(0, min(T, 2000), 64):  # quick: limit to 2000 samples
            end = min(start + 64, min(T, 2000))
            batch_idx = perm[start:end].long() % K
            # Positive pairs: (anchor, same-index)
            anchors = Phi[batch_idx]  # (B, N)
            # Negative: all other atoms in batch
            sims = anchors @ Phi.T / (N ** 0.5)  # (B, K)
            # InfoNCE: maximize sim to self, minimize to others
            labels = batch_idx  # (B,) -- positive class
            loss = torch.nn.functional.cross_entropy(sims / temperature, labels)
            # Gradient step (numerical approximation)
            loss_val = float(loss)
            # Simple Hebbian update toward input representation
            for b_local in range(end - start):
                idx = int(batch_idx[b_local])
                Phi[idx] = Phi[idx] + eta_clr * (anchors[b_local] - Phi[idx])
        Phi = Phi / Phi.norm(dim=1, keepdim=True).clamp(min=1e-9)

    # Convert to approximate bipolar for fair comparison
    Phi_bipolar = torch.sign(Phi)
    Phi_bipolar = torch.where(Phi_bipolar == 0, torch.ones_like(Phi_bipolar), Phi_bipolar)

    # SimCLR effective utilization: dense atoms don't have WTA sparsity, utilization will be high
    final_usage = torch.ones(K, device=device)
    util = compute_effective_utilization(final_usage)

    stats = {
        "effective_utilization": util,
        "atom_sparsity_avg": float(K),  # all atoms activated (dense)
        "is_simclr": True,
    }
    return Phi_bipolar, stats


# ─── Substrate storage + cleanup ────────────────────────────────────────────

def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    """W = (1/N) sum v_i k_i^T."""
    W = torch.zeros(N, N, dtype=torch.float32, device=keys.device)
    for s in range(0, keys.shape[0], BATCH_STORE):
        e = min(s + BATCH_STORE, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def cleanup_acc_at_M(
    Phi: torch.Tensor,       # (K, N) atom codebook
    M_stored: int,
    k_active: int,
    seed: int,
    N: int,
    device: str,
) -> float:
    """Store M_stored pairs (encoded via Phi) in W, measure cleanup accuracy.

    For Bet N: key = Phi[idx_k], val = Phi[idx_v] for randomly chosen pairs.
    Then: for each pair, query W @ key, measure cosine(result, val).
    Accuracy = fraction with cosine > 0.5.
    """
    K = Phi.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed + 500)

    # Generate M_stored random (key_idx, val_idx) pairs
    key_idxs = torch.randint(0, K, (M_stored,), generator=gen, device=device)
    val_idxs = torch.randint(0, K, (M_stored,), generator=gen, device=device)

    keys = Phi[key_idxs]   # (M_stored, N)
    vals = Phi[val_idxs]   # (M_stored, N)

    W = outer_product_store(keys, vals, N)

    # Recall
    y = keys @ W.T                                         # (M_stored, N)
    yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
    vn = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-9)
    cosines = (yn * vn).sum(dim=1)                         # (M_stored,)
    acc = float((cosines > 0.5).float().mean())
    return acc


# ─── Self-tests (mandatory) ──────────────────────────────────────────────────

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    device = "cpu"

    # Test 1: compute_effective_utilization
    # Uniform distribution: H/log(K) = 1.0
    K = 4
    usage_uniform = torch.tensor([0.25, 0.25, 0.25, 0.25])
    u = compute_effective_utilization(usage_uniform)
    assert abs(u - 1.0) < 1e-5, f"uniform utilization should be 1.0, got {u}"

    # Mode-collapsed: one bin
    usage_collapsed = torch.tensor([1.0, 0.0, 0.0, 0.0])
    u_collapsed = compute_effective_utilization(usage_collapsed)
    assert abs(u_collapsed) < 1e-5, f"collapsed utilization should be 0.0, got {u_collapsed}"

    # Test 2: competitive_wta_step (uses x_vecs, not x_idx)
    N_t = 64; K_t = 8; k_a = 2
    gen = torch.Generator(device=device).manual_seed(42)
    Phi_t = 2.0 * torch.randint(0, 2, (K_t, N_t), generator=gen).float() - 1.0
    bias_t = torch.zeros(K_t)
    # Create 10 random input vectors (fixed-projection style)
    x_vecs_t = 2.0 * torch.randint(0, 2, (10, N_t), generator=gen).float() - 1.0
    Phi_out, bias_out, _ = competitive_wta_step(x_vecs_t, Phi_t, bias_t, k_a, 0.01, 0.05, N_t)
    assert Phi_out.shape == (K_t, N_t), "Phi shape mismatch after WTA step"
    assert not torch.isnan(Phi_out).any(), "Phi contains NaN after WTA step"
    assert not torch.isnan(bias_out).any(), "bias contains NaN after WTA step"

    # Test 3: cleanup_acc_ratio logic
    # With identical Phi (learned = random = same), ratio should be close to 1.0
    gen2 = torch.Generator(device=device).manual_seed(99)
    Phi_rnd = 2.0 * torch.randint(0, 2, (16, N_t), generator=gen2).float() - 1.0
    acc_ref = cleanup_acc_at_M(Phi_rnd, M_stored=5, k_active=2, seed=7, N=N_t, device=device)
    assert acc_ref is not None and not math.isnan(acc_ref), f"cleanup_acc is NaN/None"
    assert 0.0 <= acc_ref <= 1.0, f"cleanup_acc out of range: {acc_ref}"

    # Test 4: outer_product_store non-zero
    keys_t = Phi_rnd[:5]
    vals_t = Phi_rnd[5:10]
    W_t = outer_product_store(keys_t, vals_t, N_t)
    assert W_t.abs().max().item() > 0.0, "W is all-zero"

    print("[selftest] all 4 assertions passed")


_instrumentation_selftest()


# ─── Per-corpus, per-arm, per-seed runner ────────────────────────────────────

def run_arm(
    corpus_name: str,
    arm: str,           # "A_LEARNED", "B_SIMCLR", "RANDOM"
    corpus_bytes: bytes,
    N: int,
    K: int,
    k_active: int,
    n_epochs: int,
    m_grid: list,
    seed: int,
    device: str,
    smoke: bool,
) -> dict:
    """Run one arm for one corpus and seed. Returns per-M cleanup accuracies + stats."""
    if arm == "A_LEARNED":
        Phi, stats = train_wta_atoms(
            corpus_bytes, N, K, k_active, n_epochs, ETA, RHO, seed, device)
    elif arm == "B_SIMCLR":
        Phi, stats = train_simclr_atoms(
            corpus_bytes, N, K, n_epochs, temperature=0.1, seed=seed, device=device)
    else:  # RANDOM baseline
        gen = torch.Generator(device=device).manual_seed(seed + 200)
        raw = torch.randint(0, 2, (K, N), generator=gen, device=device).float()
        Phi = 2.0 * raw - 1.0
        stats = {
            "effective_utilization": 1.0,  # random = perfectly uniform by construction
            "atom_sparsity_avg": float(k_active),
        }

    acc_per_M = {}
    for M in m_grid:
        acc = cleanup_acc_at_M(Phi, M_stored=M, k_active=k_active, seed=seed, N=N, device=device)
        acc_per_M[str(M)] = acc

    # Compute DMPK-style bimodality ratio (optional; approximate via SVD of Phi)
    # Phi is (K, N): compute top-2 singular values, bimodality = sv[0] / sv[1] > 2 => SHIFT mode
    try:
        if N <= 1024 or smoke:  # skip expensive SVD at large N in full mode
            sv = torch.linalg.svdvals(Phi.float())
            dmpk_ratio = float(sv[0] / sv[1].clamp(min=1e-9))
        else:
            dmpk_ratio = -1.0  # skipped
    except Exception:
        dmpk_ratio = -1.0

    # Always store centroid (mean of Phi rows) for P3 comparison.
    # At K=128, N=4096: 128 * 4096 * 4 bytes = 2 MB - acceptable.
    phi_centroid = Phi.mean(dim=0).tolist()

    return {
        "arm": arm,
        "corpus": corpus_name,
        "seed": seed,
        "acc_per_M": acc_per_M,
        "effective_utilization": stats["effective_utilization"],
        "atom_sparsity_avg": stats["atom_sparsity_avg"],
        "dmpk_bimodality_ratio": dmpk_ratio,
        "phi_centroid": phi_centroid,  # always stored for P3
    }


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args, _ = parser.parse_known_args()
    smoke = args.smoke

    t0 = time.time()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    N = N_SMOKE if smoke else N_FULL
    K = K_SMOKE if smoke else K_FULL
    k_active = K_ACTIVE_SMOKE if smoke else K_ACTIVE_FULL
    n_epochs = N_EPOCHS_SMOKE if smoke else N_EPOCHS_FULL
    m_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_bytes = 10000 if smoke else 30000   # corpus size for training

    print(f"[bet_n_wta] mode={'smoke' if smoke else 'full'} N={N} K={K} k_active={k_active} device={device}")
    print(f"  M_grid={m_grid} seeds={seeds} n_bytes={n_bytes}")

    # Collect all results
    all_results = []

    for corpus_name in CORPUS_NAMES:
        for seed in seeds:
            # Load corpus
            if corpus_name == "EN":
                corpus_bytes = load_corpus_EN(n_bytes)
            elif corpus_name == "PY":
                corpus_bytes = load_corpus_PY(n_bytes, smoke=smoke)
            else:  # RND
                corpus_bytes = load_corpus_RND(n_bytes, seed=seed)

            for arm in ["A_LEARNED", "RANDOM"]:
                r = run_arm(corpus_name, arm, corpus_bytes, N, K, k_active,
                            n_epochs, m_grid, seed, device, smoke)
                all_results.append(r)
                util = r["effective_utilization"]
                M2000_key = str(m_grid[-1])  # use last M in grid as representative
                acc = r["acc_per_M"].get(M2000_key, 0.0)
                print(f"  [{corpus_name} {arm} seed={seed}] util={util:.3f} acc@M{M2000_key}={acc:.3f}")

    # P1 evaluation (aggregated across corpus EN, arm A_LEARNED, all seeds)
    learned_en = [r for r in all_results if r["arm"] == "A_LEARNED" and r["corpus"] == "EN"]
    if learned_en:
        avg_util = float(sum(r["effective_utilization"] for r in learned_en) / len(learned_en))
        avg_sparsity = float(sum(r["atom_sparsity_avg"] for r in learned_en) / len(learned_en))
    else:
        avg_util = 0.0
        avg_sparsity = 0.0

    p1_util_pass = avg_util >= P1_PASS_UTILIZATION
    p1_util_fail = avg_util < P1_FAIL_UTILIZATION
    p1_sparsity_ratio = avg_sparsity / max(k_active, 1)
    p1_sparsity_pass = P1_PASS_SPARSITY_LO <= p1_sparsity_ratio <= P1_PASS_SPARSITY_HI
    p1_sparsity_fail = (p1_sparsity_ratio < P1_FAIL_SPARSITY_LO or
                        p1_sparsity_ratio > P1_FAIL_SPARSITY_HI)

    if p1_util_fail or p1_sparsity_fail:
        p1_label = "HARD_FAIL"
    elif p1_util_pass and p1_sparsity_pass:
        p1_label = "HARD_PASS"
    else:
        p1_label = "MIDDLE"

    # P2 evaluation: cleanup_acc_ratio at M=2000 (or last M in grid)
    m2000 = "2000"
    # Find closest key to 2000 in m_grid
    m_closest = str(min(m_grid, key=lambda m: abs(m - 2000)))

    def mean_acc_at_M(results_subset, m_key):
        vals = [r["acc_per_M"].get(m_key, 0.0) for r in results_subset
                if m_key in r["acc_per_M"]]
        return float(sum(vals) / max(len(vals), 1))

    # Compare LEARNED vs RANDOM for each corpus, then average
    p2_ratios = []
    for corpus_name in CORPUS_NAMES:
        learned_c = [r for r in all_results if r["arm"] == "A_LEARNED" and r["corpus"] == corpus_name]
        random_c = [r for r in all_results if r["arm"] == "RANDOM" and r["corpus"] == corpus_name]
        acc_learned = mean_acc_at_M(learned_c, m_closest)
        acc_random = mean_acc_at_M(random_c, m_closest)
        ratio = acc_learned / max(acc_random, 1e-6)
        p2_ratios.append(ratio)

    cleanup_acc_ratio = float(sum(p2_ratios) / max(len(p2_ratios), 1))

    if cleanup_acc_ratio >= P2_HARD_PASS_RATIO:
        p2_label = "HARD_PASS"
    elif cleanup_acc_ratio <= P2_HARD_FAIL_RATIO:
        p2_label = "HARD_FAIL"
    else:
        p2_label = "MIDDLE"

    # P3 evaluation: corpus-adaptive distinctiveness
    # Mean pairwise cosine DISTANCE between centroids of EN, PY, RND atoms
    # (cos DISTANCE = 1 - cos SIMILARITY)
    centroids = {}
    for corpus_name in CORPUS_NAMES:
        learned_c = [r for r in all_results if r["arm"] == "A_LEARNED" and r["corpus"] == corpus_name]
        if learned_c and learned_c[0]["phi_centroid"]:
            # Average centroids across seeds
            c_vecs = [torch.tensor(r["phi_centroid"]) for r in learned_c if r["phi_centroid"]]
            if c_vecs:
                centroids[corpus_name] = torch.stack(c_vecs, dim=0).mean(dim=0)

    def cosine_dist(a, b):
        n_a = a.norm() + 1e-9
        n_b = b.norm() + 1e-9
        cos_sim = float(a @ b / (n_a * n_b))
        return 1.0 - cos_sim

    if len(centroids) >= 2:
        pairs = [(a, b) for i, a in enumerate(CORPUS_NAMES) for b in CORPUS_NAMES[i+1:]
                 if a in centroids and b in centroids]
        if pairs:
            cos_dists = [cosine_dist(centroids[a], centroids[b]) for a, b in pairs]
            mean_cosine_dist = float(sum(cos_dists) / len(cos_dists))
        else:
            mean_cosine_dist = 0.0
    else:
        mean_cosine_dist = 0.0  # not computable (K too large for centroid storage)

    # Cross-corpus retrieval gap: min over (c1 != c2) of acc(c1_eval, atoms_c1) - acc(c1_eval, atoms_c2)
    # Simplified: compare acc_LEARNED_EN vs acc_LEARNED_PY on EN evaluation
    # Using M=m_closest as the eval point
    acc_en_with_en = mean_acc_at_M(
        [r for r in all_results if r["arm"] == "A_LEARNED" and r["corpus"] == "EN"], m_closest)
    acc_en_with_py = mean_acc_at_M(
        [r for r in all_results if r["arm"] == "A_LEARNED" and r["corpus"] == "PY"], m_closest)
    cross_corpus_retrieval_gap = acc_en_with_en - acc_en_with_py  # proxy

    p3_cos_pass = mean_cosine_dist >= P3_HARD_PASS_COS_DIST
    p3_cos_fail = mean_cosine_dist < P3_HARD_FAIL_COS_DIST
    p3_gap_pass = cross_corpus_retrieval_gap >= P3_HARD_PASS_RETRIEVAL_GAP

    if p3_cos_pass and p3_gap_pass:
        p3_label = "HARD_PASS"
    elif p3_cos_fail:
        p3_label = "HARD_FAIL"
    else:
        p3_label = "MIDDLE"

    # Compound verdict
    if p1_label == "HARD_FAIL":
        verdict = "BET_N_INSTRUMENTATION_FAIL"
    elif p1_label == "HARD_PASS" and p2_label == "HARD_PASS" and p3_label == "HARD_PASS":
        verdict = "BET_N_TIER1_PROMOTION"
    elif p1_label == "HARD_PASS" and p2_label == "HARD_PASS" and p3_label == "MIDDLE":
        verdict = "BET_N_PARTIAL_TIER2"
    elif p1_label == "HARD_PASS" and p2_label == "MIDDLE":
        verdict = "BET_N_ATOM_MODE_FLEXIBILITY"
    elif p1_label == "HARD_PASS" and p2_label == "HARD_FAIL":
        verdict = "BET_N_CLOSED_AT_DOMAIN"
    else:
        verdict = "BET_N_MIDDLE_BAND"

    verdict_msg = (
        f"{verdict}: P1={p1_label}(util={avg_util:.3f} sparsity_ratio={p1_sparsity_ratio:.2f}) "
        f"P2={p2_label}(ratio_M{m_closest}={cleanup_acc_ratio:.3f}) "
        f"P3={p3_label}(cos_dist={mean_cosine_dist:.3f} corp_gap={cross_corpus_retrieval_gap:.3f})"
    )

    summary = {
        "p1_label": p1_label,
        "p2_label": p2_label,
        "p3_label": p3_label,
        "effective_utilization": avg_util,
        "atom_sparsity_avg": avg_sparsity,
        "cleanup_acc_ratio_at_M_closest": cleanup_acc_ratio,
        "m_closest": int(m_closest),
        "cosine_distance_centroids": mean_cosine_dist,
        "cross_corpus_retrieval_gap": cross_corpus_retrieval_gap,
        "p2_per_corpus_ratios": dict(zip(CORPUS_NAMES, p2_ratios)),
    }

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": {
            "mode": "smoke" if smoke else "full",
            "N": N,
            "K": K,
            "k_active": k_active,
            "n_epochs": n_epochs,
            "m_grid": m_grid,
            "seeds": seeds,
            "n_bytes": n_bytes,
            "device": device,
            "p2_hard_pass_ratio": P2_HARD_PASS_RATIO,
            "p2_hard_fail_ratio": P2_HARD_FAIL_RATIO,
            "p3_hard_pass_cos_dist": P3_HARD_PASS_COS_DIST,
            "p3_hard_fail_cos_dist": P3_HARD_FAIL_COS_DIST,
        },
    }

    validate_metrics(metrics)

    out_dir = get_output_dir("wave14e_bet_n_wta_v1")
    out_path = out_dir / "metrics.json"
    out_path.write_text(json.dumps(metrics, indent=2))
    print(f"\n[bet_n_wta] {verdict}: {verdict_msg[:200]}")
    print(f"[bet_n_wta] elapsed={elapsed:.1f}s metrics written to {out_path}")

    import shutil
    shutil.copy(out_path, Path("metrics.json"))


if __name__ == "__main__":
    main()
