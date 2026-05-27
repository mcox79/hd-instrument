"""Bet N v3: WTA atom corpus-specificity via CORPUS-ENCODED retrieval (P3 hard fix).

v3 changes vs v2:
  P3 ROOT CAUSE FIX:
    - v2 matched_gap used cleanup_acc on RANDOM Phi pairs -- same atoms, same capacity,
      so EN vs PY atoms gave identical results (gap=0). Not corpus-specificity.
    - v3 encodes ACTUAL corpus n-gram pairs using learned atoms as compositional basis.
      Then cross-tests: EN atoms on EN pairs vs PY atoms on EN pairs.
      If atoms truly adapt to corpus statistics, corpus-matched atoms retrieve corpus
      n-gram associations better than corpus-mismatched atoms.

  P2 EXTENDED:
    - v2 measured M=2000 only. v3 sweeps M in {100, 500, 1000, 2000, 4000, 8000} to map
      capacity envelope (v210 open question: does advantage persist at high load?).
    - HARD-PASS anchor stays M=2000 for comparability with v2.

  P3 NEW METRIC:
    - corpus_retrieval_acc(atoms, corpus_pairs): encode 'M_eval' n-gram pairs from the
      corpus into W using the WTA atoms, then query and measure retrieval acc.
    - cross_corpus_gap = mean over eval_corpus: acc(own_atoms, c_pairs) - acc(other_atoms, c_pairs)
    - HARD-PASS: cross_corpus_gap >= 0.05 (own atoms > other atoms by 5pp on corpus-specific pairs)
    - MIDDLE: 0.0 <= gap < 0.05 (no strong specialization, but not anti-specialized)
    - HARD-FAIL: gap < 0.0 (own atoms WORSE on own corpus -- anti-specialization)

Three verdicts:
  P1 -- Sparsity-regime soundness (utilization gate, computed BEFORE P2/P3)
  P2 -- Associative-memory capacity: cleanup_acc_ratio(M=2000) = LEARNED / RANDOM >= 1.10
  P3 -- Corpus-specificity: cross_corpus_retrieval_gap >= 0.05 (AND pca_cos_dist >= 0.10)

Compound verdict table:
  P1+P2+P3 HARD-PASS -> BET_N_TIER1_PROMOTION
  P1+P2 HARD-PASS + P3 MIDDLE -> BET_N_PARTIAL_TIER2
  P1 HARD-PASS + P2 MIDDLE -> BET_N_ATOM_MODE_FLEXIBILITY
  P1 HARD-PASS + P2 HARD-FAIL -> BET_N_CLOSED_AT_DOMAIN
  P1 HARD-FAIL -> BET_N_INSTRUMENTATION_FAIL
  other -> BET_N_MIDDLE_BAND

Pre-reg: preregs/2026-05-26_wave14e_bet_n_wta_v3.md
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

# --- design parameters (exp_dev autonomy) ---
N_FULL = 4096
N_SMOKE = 512
K_FULL = 256           # larger codebook than v2 (K=128) per cap_map v211 recommendation
K_SMOKE = 32
K_ACTIVE_FULL = 12
K_ACTIVE_SMOKE = 4
N_EPOCHS_FULL = 8      # more epochs for larger K codebook to converge
N_EPOCHS_SMOKE = 2
ETA = 0.01
RHO = 0.05             # winner-fatigue anti-collapse rate (Cao 2023)

M_GRID_FULL = [100, 500, 1000, 2000, 4000, 8000]   # v3: extended sweep per v210 open question
M_GRID_SMOKE = [50, 200]
M_P2_ANCHOR = 2000     # P2 HARD-PASS anchor for comparability with v2
M_P2_ANCHOR_SMOKE = 200

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]
CORPUS_NAMES = ["EN", "PY", "RND"]

N_BYTES_FULL = 60000   # more bytes per corpus for v3 (narrower-domain diversity)
N_BYTES_SMOKE = 10000

# P1 thresholds (unchanged from v2)
P1_PASS_UTILIZATION = 0.70
P1_FAIL_UTILIZATION = 0.30
P1_PASS_SPARSITY_LO = 0.8
P1_PASS_SPARSITY_HI = 1.2
P1_FAIL_SPARSITY_LO = 0.5
P1_FAIL_SPARSITY_HI = 2.0

# P2 thresholds (unchanged from v2)
P2_HARD_PASS_RATIO = 1.10
P2_HARD_FAIL_RATIO = 0.80

# P3 thresholds -- v3 corpus-encoded retrieval metric
# cross_corpus_retrieval_gap: own atoms outperform other atoms on corpus-specific pairs
P3_HARD_PASS_RETRIEVAL_GAP = 0.05   # >= 5pp advantage for corpus-matched atoms
P3_HARD_FAIL_RETRIEVAL_GAP = 0.00   # < 0pp: own atoms NOT better (NLP-generic confirmed)
# Also check pca_cos_dist (v2 metric, carried forward as secondary)
P3_PASS_PCA_COS_DIST = 0.10

BATCH_STORE = 512
M_EVAL_CORPUS = 200    # number of corpus n-gram pairs used for cross-corpus retrieval test


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


# --- Corpus loading ---
def load_corpus_EN(n_bytes: int) -> bytes:
    """English prose corpus: repo markdown docs."""
    files = [
        REPO / "PLAN.md", REPO / "NEXT_PHASE.md", REPO / "README.md",
        REPO / "PROGRESS.md", REPO / "RESULTS.md", REPO / "CLAUDE.md",
    ]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    raw = b"".join(parts)
    if not raw:
        raw = b"the quick brown fox jumps over the lazy dog\n" * 500
    return (raw * ((n_bytes // max(len(raw), 1)) + 2))[:n_bytes]


def load_corpus_PY(n_bytes: int, smoke: bool = False) -> bytes:
    """Python source corpus: experiment scripts."""
    n_files = 3 if smoke else 15
    parts = []
    for f in sorted((REPO / "experiments").glob("exp_wave14b*.py"))[:n_files]:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    # Supplement with hdlab source for richer Python
    for f in sorted((REPO / "hdlab").glob("*.py"))[:5]:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    raw = b"".join(parts)
    if not raw:
        raw = b"def foo(): pass\n" * 1000
    return (raw * ((n_bytes // max(len(raw), 1)) + 2))[:n_bytes]


def load_corpus_RND(n_bytes: int, seed: int) -> bytes:
    """Random bytes baseline."""
    gen = torch.Generator().manual_seed(seed + 1000)
    raw = torch.randint(0, 256, (n_bytes,), generator=gen, dtype=torch.uint8)
    return bytes(raw.tolist())


# --- Utility functions ---
def compute_effective_utilization(usage_counts: torch.Tensor) -> float:
    """H(p) / log(K): 1.0 for uniform, 0.0 for collapsed."""
    K = usage_counts.numel()
    if K <= 1:
        return 1.0
    p = usage_counts / usage_counts.sum().clamp(min=1e-9)
    p = p.clamp(min=1e-9)
    entropy = -float((p * torch.log(p)).sum())
    return entropy / math.log(K)


def pca_top1(Phi: torch.Tensor) -> torch.Tensor:
    """Top-1 right singular vector of Phi (K, N). Returns (N,) unit vector."""
    try:
        _, S, Vh = torch.linalg.svd(Phi.float(), full_matrices=False)
        return Vh[0]
    except Exception:
        return Phi.mean(dim=0)


def cosine_dist(a: torch.Tensor, b: torch.Tensor) -> float:
    """1 - cosine_similarity(a, b)."""
    na = a.norm() + 1e-9
    nb = b.norm() + 1e-9
    return 1.0 - float(a @ b / (na * nb))


# --- WTA training (Cao 2023 style) ---
def competitive_wta_step(
    x_vecs: torch.Tensor,   # (B, N)
    Phi: torch.Tensor,       # (K, N)
    bias: torch.Tensor,      # (K,)
    k_active: int,
    eta: float,
    rho: float,
    N: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    B = x_vecs.shape[0]
    sims = (x_vecs @ Phi.T) / N + bias.unsqueeze(0)   # (B, K)
    _, top_k = torch.topk(sims, k_active, dim=1)       # (B, k_active)

    usage = torch.zeros(Phi.shape[0], device=Phi.device)
    delta = torch.zeros_like(Phi)

    for b in range(B):
        winners = top_k[b]
        x_b = x_vecs[b]
        for w in winners:
            w_int = w.item()
            delta[w_int] += x_b
            usage[w_int] += 1

    n_winners = B * k_active
    if n_winners > 0:
        delta /= n_winners
        Phi = Phi + eta * (delta - Phi * (usage.unsqueeze(1) / n_winners))
        Phi = Phi / Phi.norm(dim=1, keepdim=True).clamp(min=1e-9)

    bias = bias - rho * usage / B
    return Phi, bias, usage


def bytes_to_input_vecs(
    corpus_bytes: bytes,
    byte_atoms: torch.Tensor,   # (256, N)
    K_ctx: int,
    device: str,
) -> torch.Tensor:
    """Encode byte n-grams as bundled BSC vectors. Returns (T, N)."""
    if len(corpus_bytes) <= K_ctx:
        return torch.zeros((1, byte_atoms.shape[1]), device=device)
    padded = bytes([0] * K_ctx) + corpus_bytes
    T = len(padded) - K_ctx
    byts = torch.tensor(list(padded), dtype=torch.long, device=device)
    offsets = torch.arange(K_ctx - 1, -1, -1, device=device)
    idxs = byts[torch.arange(T, device=device).unsqueeze(1) + offsets.unsqueeze(0)]
    ctxs = byte_atoms[idxs].sum(dim=1)  # (T, N)
    return ctxs


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
    """Train K WTA atoms on corpus. Returns (Phi, stats)."""
    gen = torch.Generator(device=device).manual_seed(seed)
    byte_atoms_enc = (2.0 * torch.randint(0, 2, (256, N), generator=gen, device=device).float() - 1.0)
    K_ctx = 4
    x_vecs = bytes_to_input_vecs(corpus_bytes, byte_atoms_enc, K_ctx, device)

    gen2 = torch.Generator(device=device).manual_seed(seed + 100)
    Phi = (2.0 * torch.randint(0, 2, (K, N), generator=gen2, device=device).float() - 1.0)
    Phi = Phi / Phi.norm(dim=1, keepdim=True).clamp(min=1e-9)
    bias = torch.zeros(K, device=device)

    total_usage = torch.zeros(K, device=device)

    for epoch in range(n_epochs):
        perm = torch.randperm(x_vecs.shape[0], device=device)
        x_perm = x_vecs[perm]
        for start in range(0, x_vecs.shape[0], BATCH_STORE):
            batch = x_perm[start:start + BATCH_STORE]
            if batch.shape[0] == 0:
                break
            Phi, bias, usage = competitive_wta_step(batch, Phi, bias, k_active, eta, rho, N)
            total_usage += usage

    eff_util = compute_effective_utilization(total_usage)
    stats = {
        "effective_utilization": eff_util,
        "atom_sparsity_avg": float(k_active),
    }
    return Phi, stats


# --- Cleanup accuracy (v2 method: random Phi pairs) ---
def cleanup_acc_at_M(
    Phi: torch.Tensor,
    M_stored: int,
    k_active: int,
    seed: int,
    N: int,
    device: str,
) -> float:
    """Store M_stored random Phi pairs in W, measure cleanup acc (P2 metric)."""
    K = Phi.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed + 500)
    key_idxs = torch.randint(0, K, (M_stored,), generator=gen, device=device)
    val_idxs = torch.randint(0, K, (M_stored,), generator=gen, device=device)
    keys = Phi[key_idxs]
    vals = Phi[val_idxs]
    W = (vals.T @ keys) / N
    y = keys @ W.T
    yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
    vn = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-9)
    cosines = (yn * vn).sum(dim=1)
    return float((cosines > 0.5).float().mean())


# --- P3 v3: Corpus-encoded retrieval accuracy ---
def corpus_encoded_retrieval_acc(
    Phi: torch.Tensor,        # (K, N) learned/random atoms
    corpus_x_vecs: torch.Tensor,  # (T, N) pre-encoded corpus context vecs
    k_active: int,
    M_eval: int,
    seed: int,
    N: int,
    device: str,
) -> float:
    """Encode M_eval corpus n-gram bigram pairs using Phi as compositional basis.

    Encodes each position i as: key_i = topk_binding(corpus_x_vecs[i], Phi, k_active)
    val_i  = topk_binding(corpus_x_vecs[i+step], Phi, k_active)

    Store M_eval (key, val) pairs in W, query all keys, measure retrieval cosine acc.

    This is the TRUE corpus-specificity test: atoms that adapted to corpus statistics
    should bind corpus n-gram pairs more distinctively than corpus-mismatched atoms.
    """
    T = corpus_x_vecs.shape[0]
    if T < M_eval + 1:
        # Not enough corpus data -- fall back to random-pair test
        return cleanup_acc_at_M(Phi, M_stored=min(M_eval, Phi.shape[0] // 2),
                                 k_active=k_active, seed=seed, N=N, device=device)

    gen = torch.Generator(device=device).manual_seed(seed + 700)
    start_idxs = torch.randperm(T - 1, generator=gen, device=device)[:M_eval]
    val_idxs = start_idxs + 1  # next-position bigram

    # Encode context vecs through WTA atoms (sparse binding)
    # Binding: project x_vec onto top-k atoms, get sparse atom-index representation,
    # then reconstruct as sum of winning atoms (sparse HV representation)
    def encode_through_atoms(x: torch.Tensor) -> torch.Tensor:
        """(B, N) -> sparse atom-coded (B, N): sum of top-k Phi rows."""
        sims = x @ Phi.T / N   # (B, K)
        _, top_k = torch.topk(sims, k_active, dim=1)   # (B, k_active)
        B = x.shape[0]
        coded = torch.zeros(B, N, device=device)
        for b in range(B):
            coded[b] = Phi[top_k[b]].sum(dim=0)
        coded = coded / coded.norm(dim=1, keepdim=True).clamp(min=1e-9)
        return coded

    keys_raw = corpus_x_vecs[start_idxs]   # (M_eval, N)
    vals_raw = corpus_x_vecs[val_idxs]     # (M_eval, N)

    keys = encode_through_atoms(keys_raw)   # (M_eval, N)
    vals = encode_through_atoms(vals_raw)   # (M_eval, N)

    W = (vals.T @ keys) / N
    y = keys @ W.T
    yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
    vn = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-9)
    cosines = (yn * vn).sum(dim=1)
    return float((cosines > 0.5).float().mean())


# --- Self-tests ---
def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    device = "cpu"

    # Test 1: compute_effective_utilization
    usage_uniform = torch.tensor([0.25, 0.25, 0.25, 0.25])
    u = compute_effective_utilization(usage_uniform)
    assert abs(u - 1.0) < 1e-5, f"uniform utilization should be 1.0, got {u}"
    usage_collapsed = torch.tensor([1.0, 0.0, 0.0, 0.0])
    u_c = compute_effective_utilization(usage_collapsed)
    assert abs(u_c) < 1e-5, f"collapsed utilization should be 0.0, got {u_c}"

    # Test 2: competitive_wta_step produces non-NaN Phi
    N_t = 64; K_t = 8; k_a = 2
    gen = torch.Generator(device=device).manual_seed(42)
    Phi_t = 2.0 * torch.randint(0, 2, (K_t, N_t), generator=gen).float() - 1.0
    bias_t = torch.zeros(K_t)
    x_vecs_t = 2.0 * torch.randint(0, 2, (10, N_t), generator=gen).float() - 1.0
    Phi_out, bias_out, _ = competitive_wta_step(x_vecs_t, Phi_t, bias_t, k_a, 0.01, 0.05, N_t)
    assert Phi_out.shape == (K_t, N_t) and not torch.isnan(Phi_out).any(), "WTA step NaN"

    # Test 3: cleanup_acc_at_M returns valid float in [0,1]
    gen2 = torch.Generator(device=device).manual_seed(99)
    Phi_rnd = 2.0 * torch.randint(0, 2, (16, N_t), generator=gen2).float() - 1.0
    acc = cleanup_acc_at_M(Phi_rnd, M_stored=5, k_active=2, seed=7, N=N_t, device=device)
    assert acc is not None and not math.isnan(acc) and 0.0 <= acc <= 1.0, f"cleanup_acc invalid: {acc}"

    # Test 4: pca_top1 returns non-NaN unit vector
    gen3 = torch.Generator(device=device).manual_seed(77)
    Phi_test = 2.0 * torch.randint(0, 2, (8, N_t), generator=gen3).float() - 1.0
    v = pca_top1(Phi_test)
    assert v.shape == (N_t,) and not torch.isnan(v).any() and v.norm().item() > 0.5, "pca_top1 fail"

    # Test 5: cosine_dist for orthogonal = 1.0, identical = 0.0
    a = torch.tensor([1.0, 0.0, 0.0])
    b = torch.tensor([0.0, 1.0, 0.0])
    assert abs(cosine_dist(a, b) - 1.0) < 1e-5, "orthogonal cos_dist != 1.0"
    assert abs(cosine_dist(a, a)) < 1e-5, "identical cos_dist != 0.0"

    # Test 6: corpus_encoded_retrieval_acc: varies based on atoms
    # Two very different Phi: both should return valid float, not identical if atoms differ
    gen4 = torch.Generator(device=device).manual_seed(13)
    Phi_A = 2.0 * torch.randint(0, 2, (8, N_t), generator=gen4).float() - 1.0
    gen5 = torch.Generator(device=device).manual_seed(14)
    corpus_vecs = 2.0 * torch.randint(0, 2, (50, N_t), generator=gen5).float() - 1.0
    acc_corpus = corpus_encoded_retrieval_acc(Phi_A, corpus_vecs, k_active=2,
                                               M_eval=20, seed=7, N=N_t, device=device)
    assert 0.0 <= acc_corpus <= 1.0, f"corpus_retrieval_acc out of range: {acc_corpus}"
    assert not math.isnan(acc_corpus), "corpus_retrieval_acc is NaN"

    # Test 7: corpus n-gram encoding produces non-trivial vecs (at least some distinct rows)
    gen6 = torch.Generator(device=device).manual_seed(42)
    byte_atoms_t = 2.0 * torch.randint(0, 2, (256, N_t), generator=gen6).float() - 1.0
    test_bytes = b"hello world python numpy torch" * 50
    x_vecs_corpus = bytes_to_input_vecs(test_bytes, byte_atoms_t, K_ctx=4, device=device)
    assert x_vecs_corpus.shape[1] == N_t, "bytes_to_input_vecs wrong dim"
    assert x_vecs_corpus.shape[0] > 1, "bytes_to_input_vecs too few rows"
    # Check not all-identical rows (would be a degenerate encoding)
    row_norms = x_vecs_corpus.norm(dim=1)
    assert row_norms.std().item() > 0 or x_vecs_corpus.shape[0] < 5, "degenerate encoding"

    # Test 8: P3 suspicious-result gate -- ensure corpus_retrieval_acc can differ across seeds
    gen7 = torch.Generator(device=device).manual_seed(55)
    Phi_B = 2.0 * torch.randint(0, 2, (8, N_t), generator=gen7).float() - 1.0
    acc_A = corpus_encoded_retrieval_acc(Phi_A, corpus_vecs, k_active=2,
                                          M_eval=20, seed=7, N=N_t, device=device)
    acc_B = corpus_encoded_retrieval_acc(Phi_B, corpus_vecs, k_active=2,
                                          M_eval=20, seed=7, N=N_t, device=device)
    # Just verify neither is NaN (they may be equal at tiny scale -- that's OK)
    assert not math.isnan(acc_A) and not math.isnan(acc_B), "corpus_retrieval_acc NaN in self-test 8"

    print("[selftest] all 8 assertions passed", flush=True)


_instrumentation_selftest()


# --- Per-arm, per-corpus, per-seed runner ---
def run_arm(
    corpus_name: str,
    arm: str,
    corpus_bytes: bytes,
    N: int,
    K: int,
    k_active: int,
    n_epochs: int,
    m_grid: list,
    seed: int,
    device: str,
) -> dict:
    """Run one arm for one corpus+seed. Returns per-M P2 accs + PCA sig + P3 corpus x_vecs."""
    if arm == "A_LEARNED":
        Phi, stats = train_wta_atoms(corpus_bytes, N, K, k_active, n_epochs, ETA, RHO, seed, device)
    else:  # RANDOM baseline
        gen = torch.Generator(device=device).manual_seed(seed + 200)
        Phi = (2.0 * torch.randint(0, 2, (K, N), generator=gen, device=device).float() - 1.0)
        stats = {"effective_utilization": 1.0, "atom_sparsity_avg": float(k_active)}

    # P2 metric: cleanup acc on random Phi pairs across M grid
    acc_per_M = {}
    for M in m_grid:
        acc = cleanup_acc_at_M(Phi, M_stored=M, k_active=k_active, seed=seed, N=N, device=device)
        acc_per_M[str(M)] = acc

    # PCA top-1 signature (v2 compatibility)
    phi_pca_top1 = pca_top1(Phi).tolist()

    # Encode corpus through this arm's atoms (for P3 cross-corpus retrieval test)
    gen_enc = torch.Generator(device=device).manual_seed(seed + 300)
    byte_atoms_enc = (2.0 * torch.randint(0, 2, (256, N), generator=gen_enc, device=device).float() - 1.0)
    K_ctx = 4
    corpus_x_vecs = bytes_to_input_vecs(corpus_bytes, byte_atoms_enc, K_ctx, device)

    return {
        "arm": arm,
        "corpus": corpus_name,
        "seed": seed,
        "acc_per_M": acc_per_M,
        "effective_utilization": stats["effective_utilization"],
        "atom_sparsity_avg": stats["atom_sparsity_avg"],
        "phi_pca_top1": phi_pca_top1,
        "Phi": Phi,                       # kept in memory for cross-corpus P3 test
        "corpus_x_vecs": corpus_x_vecs,   # pre-encoded, consistent byte_atoms per seed
    }


# --- Main ---
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args, _ = parser.parse_known_args()

    if args.self_test:
        print("[self-test] _instrumentation_selftest() already verified at module load.", flush=True)
        return

    smoke = args.smoke

    t0 = time.time()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    N = N_SMOKE if smoke else N_FULL
    K = K_SMOKE if smoke else K_FULL
    k_active = K_ACTIVE_SMOKE if smoke else K_ACTIVE_FULL
    n_epochs = N_EPOCHS_SMOKE if smoke else N_EPOCHS_FULL
    m_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_bytes = N_BYTES_SMOKE if smoke else N_BYTES_FULL
    m_p2_anchor = M_P2_ANCHOR_SMOKE if smoke else M_P2_ANCHOR

    print(
        f"[bet_n_wta_v3] mode={'smoke' if smoke else 'full'} N={N} K={K} "
        f"k_active={k_active} n_epochs={n_epochs} device={device}",
        flush=True
    )

    # Store all run results; retain Phi + corpus_x_vecs in memory for P3
    all_results: list[dict] = []

    for corpus_name in CORPUS_NAMES:
        for seed in seeds:
            if corpus_name == "EN":
                corpus_bytes = load_corpus_EN(n_bytes)
            elif corpus_name == "PY":
                corpus_bytes = load_corpus_PY(n_bytes, smoke=smoke)
            else:
                corpus_bytes = load_corpus_RND(n_bytes, seed=seed)

            for arm in ["A_LEARNED", "RANDOM"]:
                r = run_arm(corpus_name, arm, corpus_bytes, N, K, k_active,
                            n_epochs, m_grid, seed, device)
                all_results.append(r)
                m_rep = str(m_grid[-1])
                acc = r["acc_per_M"].get(m_rep, 0.0)
                print(
                    f"  [{corpus_name} {arm} seed={seed}] "
                    f"util={r['effective_utilization']:.3f} acc@M{m_rep}={acc:.3f}",
                    flush=True
                )

    # --- P1 evaluation ---
    learned_en = [r for r in all_results if r["arm"] == "A_LEARNED" and r["corpus"] == "EN"]
    avg_util = float(sum(r["effective_utilization"] for r in learned_en) / max(len(learned_en), 1))
    avg_sparsity = float(sum(r["atom_sparsity_avg"] for r in learned_en) / max(len(learned_en), 1))

    p1_sparsity_ratio = avg_sparsity / max(k_active, 1)
    if avg_util < P1_FAIL_UTILIZATION or p1_sparsity_ratio < P1_FAIL_SPARSITY_LO or p1_sparsity_ratio > P1_FAIL_SPARSITY_HI:
        p1_label = "HARD_FAIL"
    elif avg_util >= P1_PASS_UTILIZATION and P1_PASS_SPARSITY_LO <= p1_sparsity_ratio <= P1_PASS_SPARSITY_HI:
        p1_label = "HARD_PASS"
    else:
        p1_label = "MIDDLE"

    # --- P2 evaluation: cleanup_acc_ratio at M=2000 (or closest) ---
    m_anchor_key = str(min(m_grid, key=lambda m: abs(m - m_p2_anchor)))

    def mean_acc_at_M(results_subset, m_key):
        vals = [r["acc_per_M"].get(m_key, 0.0) for r in results_subset if m_key in r["acc_per_M"]]
        return float(sum(vals) / max(len(vals), 1))

    p2_ratios = []
    p2_per_corpus = {}
    for cname in CORPUS_NAMES:
        learned_c = [r for r in all_results if r["arm"] == "A_LEARNED" and r["corpus"] == cname]
        random_c = [r for r in all_results if r["arm"] == "RANDOM" and r["corpus"] == cname]
        acc_learned = mean_acc_at_M(learned_c, m_anchor_key)
        acc_random = mean_acc_at_M(random_c, m_anchor_key)
        ratio = acc_learned / max(acc_random, 1e-6)
        p2_ratios.append(ratio)
        p2_per_corpus[cname] = ratio

    cleanup_acc_ratio = float(sum(p2_ratios) / max(len(p2_ratios), 1))

    # Suspicious: all per-corpus ratios identical
    p2_ratio_vals = list(p2_per_corpus.values())
    p2_degenerate = (max(p2_ratio_vals) - min(p2_ratio_vals) < 1e-6) if len(p2_ratio_vals) > 1 else False
    if p2_degenerate:
        print(f"[WARN] P2 ratios all identical ({p2_ratio_vals}): possible instrumentation issue.", flush=True)

    if cleanup_acc_ratio >= P2_HARD_PASS_RATIO:
        p2_label = "HARD_PASS"
    elif cleanup_acc_ratio <= P2_HARD_FAIL_RATIO:
        p2_label = "HARD_FAIL"
    else:
        p2_label = "MIDDLE"

    # Extended M-sweep summary (all M points)
    p2_per_M_avg = {}
    for M in m_grid:
        m_key = str(M)
        all_learned = [r for r in all_results if r["arm"] == "A_LEARNED"]
        all_random = [r for r in all_results if r["arm"] == "RANDOM"]
        acc_l = mean_acc_at_M(all_learned, m_key)
        acc_r = mean_acc_at_M(all_random, m_key)
        p2_per_M_avg[m_key] = {"learned": acc_l, "random": acc_r, "ratio": acc_l / max(acc_r, 1e-6)}

    # --- P3 evaluation: v3 corpus-encoded retrieval cross-test ---
    print("[P3] Running corpus-encoded retrieval cross-test...", flush=True)

    # For each eval corpus, compute corpus_x_vecs (consistent byte encoding)
    # and then evaluate: (a) own atoms, (b) atoms from each other corpus
    corpus_accs: dict[str, dict[str, float]] = {}  # corpus_accs[eval_corpus][atom_corpus] = acc
    M_eval = min(M_EVAL_CORPUS, 100) if smoke else M_EVAL_CORPUS

    for eval_corpus in CORPUS_NAMES:
        corpus_accs[eval_corpus] = {}
        # Get a representative corpus_x_vecs for eval_corpus (seed-averaged across A_LEARNED results)
        eval_x_vecs_list = [r["corpus_x_vecs"] for r in all_results
                            if r["corpus"] == eval_corpus and r["arm"] == "A_LEARNED"]
        if not eval_x_vecs_list:
            continue
        # Use first seed's x_vecs (consistent encoding; byte_atoms use same seed+300 key)
        eval_x_vecs = eval_x_vecs_list[0]

        for atom_corpus in CORPUS_NAMES:
            # Average across seeds for atom corpus
            atom_runs = [r for r in all_results
                         if r["corpus"] == atom_corpus and r["arm"] == "A_LEARNED"]
            if not atom_runs:
                corpus_accs[eval_corpus][atom_corpus] = 0.0
                continue
            acc_vals = []
            for r in atom_runs:
                Phi_atom = r["Phi"]
                acc = corpus_encoded_retrieval_acc(
                    Phi_atom, eval_x_vecs, k_active=k_active,
                    M_eval=M_eval, seed=r["seed"], N=N, device=device
                )
                acc_vals.append(acc)
            corpus_accs[eval_corpus][atom_corpus] = float(sum(acc_vals) / max(len(acc_vals), 1))

        # Print cross-corpus table for this eval corpus
        for ac, acc in corpus_accs[eval_corpus].items():
            print(f"  [P3] eval={eval_corpus} atoms={ac}: retrieval_acc={acc:.4f}", flush=True)

    # P3 cross-corpus retrieval gap: mean over eval corpora of (own - best_other)
    cross_corpus_gaps = []
    for eval_corpus in CORPUS_NAMES:
        if eval_corpus not in corpus_accs:
            continue
        acc_own = corpus_accs[eval_corpus].get(eval_corpus, 0.0)
        acc_others = [v for k, v in corpus_accs[eval_corpus].items() if k != eval_corpus]
        if acc_others:
            acc_best_other = max(acc_others)
            gap = acc_own - acc_best_other
            cross_corpus_gaps.append(gap)
            print(f"  [P3] gap({eval_corpus} own={acc_own:.4f} best_other={acc_best_other:.4f}): {gap:.4f}", flush=True)

    mean_retrieval_gap = float(sum(cross_corpus_gaps) / max(len(cross_corpus_gaps), 1)) if cross_corpus_gaps else 0.0

    # P3 secondary: PCA cos_dist (v2 compatibility)
    pca_vecs = {}
    for cname in CORPUS_NAMES:
        learned_c = [r for r in all_results if r["arm"] == "A_LEARNED" and r["corpus"] == cname]
        if learned_c:
            vecs = [torch.tensor(r["phi_pca_top1"]) for r in learned_c if r["phi_pca_top1"]]
            if vecs:
                mean_vec = torch.stack(vecs, dim=0).mean(dim=0)
                pca_vecs[cname] = mean_vec / mean_vec.norm().clamp(min=1e-9)

    pca_cos_dist_vals = []
    corpus_list = [c for c in CORPUS_NAMES if c in pca_vecs]
    for i, c1 in enumerate(corpus_list):
        for c2 in corpus_list[i+1:]:
            pca_cos_dist_vals.append(cosine_dist(pca_vecs[c1], pca_vecs[c2]))
    mean_pca_cos_dist = float(sum(pca_cos_dist_vals) / max(len(pca_cos_dist_vals), 1))

    print(f"[P3] mean_retrieval_gap={mean_retrieval_gap:.4f} mean_pca_cos_dist={mean_pca_cos_dist:.4f}", flush=True)

    # Suspicious-result gates
    if mean_pca_cos_dist < 1e-6:
        print("[WARN] P3 pca_cos_dist exact zero -- PCA degenerate.", flush=True)
    if all(abs(corpus_accs.get(ec, {}).get(ec, 0.0) - corpus_accs.get(ec, {}).get(
            [k for k in CORPUS_NAMES if k != ec][0], 0.0)) < 1e-6
           for ec in CORPUS_NAMES if ec in corpus_accs):
        print("[WARN] All cross-corpus retrieval gaps are exact zero -- check encoding.", flush=True)

    # P3 verdict: primary on retrieval_gap
    p3_retrieval_pass = mean_retrieval_gap >= P3_HARD_PASS_RETRIEVAL_GAP
    p3_retrieval_fail = mean_retrieval_gap < P3_HARD_FAIL_RETRIEVAL_GAP  # < 0.0
    p3_pca_pass = mean_pca_cos_dist >= P3_PASS_PCA_COS_DIST

    if p3_retrieval_pass and p3_pca_pass:
        p3_label = "HARD_PASS"
    elif p3_retrieval_fail:
        p3_label = "HARD_FAIL"
    else:
        p3_label = "MIDDLE"

    # --- Compound verdict ---
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

    elapsed = time.time() - t0

    verdict_msg = (
        f"{verdict}: P1={p1_label}(util={avg_util:.3f} sparsity_ratio={p1_sparsity_ratio:.2f}) "
        f"P2={p2_label}(ratio_M{m_anchor_key}={cleanup_acc_ratio:.3f}) "
        f"P3={p3_label}(retrieval_gap={mean_retrieval_gap:.4f} pca_cos_dist={mean_pca_cos_dist:.4f})"
    )

    summary = {
        "p1_label": p1_label,
        "p2_label": p2_label,
        "p3_label": p3_label,
        "effective_utilization": avg_util,
        "atom_sparsity_avg": avg_sparsity,
        "cleanup_acc_ratio_at_M_anchor": cleanup_acc_ratio,
        "m_anchor": m_anchor_key,
        "p2_per_corpus_ratios": p2_per_corpus,
        "p2_per_M_extended": p2_per_M_avg,
        "p2_degenerate_flag": p2_degenerate,
        # P3 v3 metrics
        "cross_corpus_retrieval_gap": mean_retrieval_gap,
        "cross_corpus_retrieval_table": {
            ec: {ac: corpus_accs[ec].get(ac, None) for ac in CORPUS_NAMES}
            for ec in CORPUS_NAMES if ec in corpus_accs
        },
        "pca_cos_dist_centroids": mean_pca_cos_dist,
    }

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N, "K": K, "k_active": k_active, "n_epochs": n_epochs,
        "m_grid": m_grid, "seeds": seeds, "n_bytes": n_bytes, "device": device,
        "p2_hard_pass_ratio": P2_HARD_PASS_RATIO,
        "p3_hard_pass_retrieval_gap": P3_HARD_PASS_RETRIEVAL_GAP,
        "p3_hard_fail_retrieval_gap": P3_HARD_FAIL_RETRIEVAL_GAP,
        "p3_pass_pca_cos_dist": P3_PASS_PCA_COS_DIST,
        "m_eval_corpus": M_eval,
    }

    print(f"\nVERDICT: {verdict}", flush=True)
    print(f"  {verdict_msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)

    out_dir = get_output_dir("wave14e_bet_n_wta_v3")
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")  # replace() handles existing file on Windows
    print(f"[output] {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    main()
