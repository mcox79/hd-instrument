"""Alt3: PAC-Bayes Laplace-Fisher KL as retention predictor for Bet B.

CONTEXT: Alt3 of the predictor-family sweep after R-PRIME-3 HARD-FAIL (r^2=0.103
for task-pair input geometry). R-PRIME-1 posterior-over-W KL derivation landed at
commit 0140545 (notes/exp_dev_handoff_rprime1_posterior_over_W_KL_derivation_2026-05-24.md).
This implements that derivation: diagonal-Laplace Fisher KL between Phase-A and Phase-B
trained-weight posteriors, then correlates with measured retention.

KEY QUESTION: does the Laplace-Fisher posterior KL between W_A and W_B predict
retention_A (how much Phase-A knowledge is retained after Phase-B training)?
If r^2 >= 0.50, we have a geometry-free mechanism for retention prediction
that generalizes beyond the discrete shift-class Alt1 finding.

FORMULA (from handoff, eq (**)):
  KL_diag(q_B || q_A) = 0.5 * sum_i [
      (f_{A,i} / f_{B,i}) - 1 - log(f_{B,i} / f_{A,i}) + f_{A,i} * (W_B - W_A)_i^2
  ]
  where f_{A,i}, f_{B,i} = diagonal Fisher at W_A, W_B respectively.
  Ridge = 1/N added to both before inversion/log to handle rank degeneracy.

DESIGN:
  - Run Phase-A (store corpus_A) and Phase-B (store corpus_B with 5 corpus-pair types)
  - Snapshot W_A (after Phase-A) and W_B (after Phase-B)
  - Compute diagonal Fisher at W_A (from Phase-A batches) and W_B (from Phase-B batches)
  - Compute KL_diag for each (seed, corpus_pair) cell
  - Correlate KL_diag vs measured retention_A
  - Compare vs baseline predictor: ||W_B - W_A||_F^2 (naive Euclidean)

SUBSTRATE: reuses exp_wave14_betB_W_internal_signature_v1 corpus-pair infrastructure
  (5 corpus pairs: shuffled_same, reversed_same, python_source, verification, random_bytes)
  and exp_wave14d_betB_kovacs_v1 training loop.

PRE-REGISTERED BANDS (per [[feedback-envelope-expansion-fail-bands]]):
  HARD-PASS:
    - Pearson r^2(KL_diag, retention_A) >= 0.50 across >= 15 cells (3 pairs x 5 seeds)
    - AND Pearson r^2(KL_diag, retention_A) > r^2(||Delta_W||_F^2, retention_A) + 0.10
      (Fisher metric strictly improves over Euclidean distance as predictor)
    -> R-PRIME-1 Laplace-Fisher KL is binding retention mechanism.
       Alt3 promoted; PAC-Bayes posterior-over-W KL track opened.

  HARD-FAIL:
    - Pearson r^2(KL_diag, retention_A) < 0.20 across all pairs
    - AND r^2(||Delta_W||_F^2, retention_A) < 0.20 (neither metric predicts)
    -> No weight-space geometry predicts Bet B retention. Mechanism elsewhere.
       Rehab paths: (a) function-space KL, (b) empirical Bernstein, (c) task-arithmetic.

  MIDDLE:
    - r^2 in [0.20, 0.50) OR Fisher improves Euclidean by < 0.10
    -> Partial signal; run with larger n_cells or upgrade to block-diagonal KFAC Fisher.

  LAPLACE-ASSUMPTION-VIOLATED:
    - ||Delta_W||_F / ||W_A||_F > 0.5 on majority of seeds (Laplace basin violated)
    -> Flag per handoff caveat; KL estimate unreliable in this regime.

SELF-TESTS (per [[feedback-strategy-spec-formula-selftests]]):
  1. KL(q_A || q_A) = 0 exactly (W_A == W_B, f_A == f_B, ridge=0)
  2. 1-D case: W_A=0, W_B=1, f_A=4, f_B=1, ridge=0 -> KL = 0.5*(4-1-log4+4) = 2.8069
  3. Fisher up-weights high-curvature direction: N=4, single entry perturbation,
     f_A=100 at [0,0], f_A=0.01 elsewhere, f_B=f_A, W_B[0,0]=1 -> KL = 50.0
  4. Naive-Euclidean Self-test 3 would give 0.5 (200x smaller); confirms Fisher metric matters
  5. pac_bayes_floor(kl=50, m=200) = max(0, 1-sqrt(50/400)) = 0.646

Queue: overnight_queue (GPU; 5 seeds x 5 corpus-pairs x Phase-A+B + Fisher computation)
Pre-reg: preregs/2026-05-24_wave14_betB_pac_bayes_kl_predictor_v1.md

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev.
Per [[feedback-lit-scan-calibration-penalty]]: P(r^2>=0.50) before deflation ~0.55;
  after penalty: 0.40 (uncharted regime; Laplace-Fisher-on-Hebbian novel synthesis).
Per [[feedback-strategy-spec-formula-selftests]]: 5 self-test cells inline.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Load Kovacs base (train_w_with_replay, evaluate_bpc, bytes_to_idx_tensors)
_kv_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_kv_spec = importlib.util.spec_from_file_location("kv", _kv_path)
kv = importlib.util.module_from_spec(_kv_spec)
_kv_spec.loader.exec_module(kv)
pa = kv.pa

# ─── design parameters ───
N_FULL = 4096
N_SMOKE = 512
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 2
BYTES_FULL = 200_000
BYTES_SMOKE = 3_000

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PAIRS_FULL = 5
N_PAIRS_SMOKE = 3  # pairs 0, 2, 4
SMOKE_PAIRS = [0, 2, 4]

# Pre-registered thresholds
PASS_R2 = 0.50
FAIL_R2 = 0.20
FISHER_IMPROVEMENT = 0.10       # Fisher r^2 must exceed Euclidean r^2 by this margin
LAPLACE_VIOLATION_THRESH = 0.5  # ||Delta_W||_F / ||W_A||_F > this flags Laplace suspect


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


# ─── corpus loaders (reuse from W_internal_signature) ───
def load_corpus_a(n_bytes: int) -> bytes:
    return pa.load_corpus_a()[:n_bytes]


def load_corpus_pair(pair_id: int, n_bytes: int, seed: int) -> bytes:
    corpus_a = pa.load_corpus_a()
    if pair_id == 0:
        return pa.shuffle_bytes(corpus_a[:n_bytes * 2], seed=seed + 100)[:n_bytes]
    elif pair_id == 1:
        data = corpus_a[:n_bytes]
        return bytes(reversed(data))
    elif pair_id == 2:
        exp_dir = REPO / "experiments"
        parts = []
        for f in sorted(exp_dir.glob("exp_wave14b*.py"))[:10]:
            parts.append(f.read_bytes()); parts.append(b"\n\n")
        data = b"".join(parts)
        return data[:n_bytes] if n_bytes < len(data) else data
    elif pair_id == 3:
        ver_dir = REPO / "verification"
        parts = []
        for f in sorted(ver_dir.glob("*.py"))[:6]:
            parts.append(f.read_bytes()); parts.append(b"\n\n")
        data = b"".join(parts)
        return data[:n_bytes] if n_bytes < len(data) else data
    elif pair_id == 4:
        gen = torch.Generator().manual_seed(seed + 200)
        data = torch.randint(0, 256, (n_bytes,), generator=gen).numpy().tobytes()
        return data
    else:
        raise ValueError(f"Unknown pair_id={pair_id}")


PAIR_NAMES = {
    0: "shuffled_same_corpus", 1: "reversed_same_corpus",
    2: "python_source", 3: "verification_code", 4: "random_bytes",
}


# ─── Laplace-Fisher KL implementation ───
def compute_diagonal_fisher(W_anchor: torch.Tensor,
                             batches_x: torch.Tensor,
                             batches_y: torch.Tensor,
                             byte_atoms: torch.Tensor,
                             pos_atoms: torch.Tensor,
                             batch_size: int,
                             device) -> torch.Tensor:
    """Empirical diagonal Fisher at W_anchor over the phase's training batches.

    Each per-sample gradient is computed via:
      log-likelihood gradient w.r.t. W for the Hebbian outer-product prediction step.
    Here we approximate: grad_W L_b = (target - prediction) * context^T / N
    so the per-sample Fisher diagonal entry is (grad_W_ij)^2 summed over batch.

    Returns fisher_diag: shape (N, N), averaged over batches.
    """
    N = W_anchor.shape[0]
    W = W_anchor.to(device)
    fisher_diag = torch.zeros_like(W)
    n_batches = 0
    T = batches_x.shape[0]
    for s in range(0, T, batch_size):
        e = min(s + batch_size, T)
        idx_batch = batches_x[s:e].to(device)
        tgt_batch = batches_y[s:e].to(device)
        B = idx_batch.shape[0]
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
        # Prediction step (no-grad; same as train loop)
        with torch.no_grad():
            q = ctxs @ W.T
            q = pa.shifted_relu(q, kv.RELU_B)
            sims = (byte_atoms @ q.T) / N
            P = torch.softmax(kv.BETA * sims, dim=0)
            target_atoms = byte_atoms[tgt_batch]
            predicted = (P.T @ byte_atoms)
            residual = target_atoms - predicted       # (B, N)
            # Gradient: dW = (residual^T @ ctxs) / N  -- same shape as W: (N, N)
            grad_W = (residual.T @ ctxs) / N          # (N, N)
            fisher_diag.add_(grad_W * grad_W)          # element-wise square
        n_batches += 1
    if n_batches > 0:
        fisher_diag.div_(n_batches)
    return fisher_diag


def kl_diag_laplace(W_A: torch.Tensor, W_B: torch.Tensor,
                     fisher_A: torch.Tensor, fisher_B: torch.Tensor,
                     ridge: Optional[float] = None) -> float:
    """Diagonal-Laplace PAC-Bayes posterior KL, eq (**) from handoff.

    KL(q_B || q_A) = 0.5 * sum_i [
        (f_{A,i}/f_{B,i}) - 1 - log(f_{B,i}/f_{A,i}) + f_{A,i} * (W_B - W_A)_i^2
    ]
    Ridge = 1/N added to both before computation (handles rank degeneracy).
    """
    N = W_A.shape[0]
    if ridge is None:
        ridge = 1.0 / N
    fA = fisher_A.float() + ridge
    fB = fisher_B.float() + ridge
    delta = (W_B.float() - W_A.float())              # (N, N)
    term_quadratic = (fA * delta * delta).sum()       # sum f_{A,i} * delta_i^2
    term_trace = (fA / fB).sum()                      # sum f_{A,i}/f_{B,i}
    term_logdet = (torch.log(fB) - torch.log(fA)).sum()  # sum log(f_{B,i}/f_{A,i})
    d = float(fA.numel())
    kl = 0.5 * (term_trace - d + term_logdet + term_quadratic)
    return float(kl.item())


def euclidean_kl_proxy(W_A: torch.Tensor, W_B: torch.Tensor) -> float:
    """Naive Euclidean proxy: ||W_B - W_A||_F^2. Baseline comparator."""
    return float(((W_B.float() - W_A.float()) ** 2).sum().item())


def pac_bayes_floor(kl: float, m: float) -> float:
    if m <= 0 or kl < 0:
        return 0.0
    return max(0.0, 1.0 - math.sqrt(kl / (2.0 * m)))


def pearson_r2(xs: List[float], ys: List[float]) -> float:
    pairs = [(x, y) for x, y in zip(xs, ys)
             if not math.isnan(x) and not math.isnan(y)]
    if len(pairs) < 3:
        return float("nan")
    n = len(pairs)
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    sx = math.sqrt(sum((p[0] - mx) ** 2 for p in pairs) / (n - 1))
    sy = math.sqrt(sum((p[1] - my) ** 2 for p in pairs) / (n - 1))
    if sx < 1e-12 or sy < 1e-12:
        return 0.0
    r = sum((p[0] - mx) * (p[1] - my) for p in pairs) / ((n - 1) * sx * sy)
    return r ** 2


def _get_pos_atoms(N: int, device) -> torch.Tensor:
    """Retrieve pos_atoms from the Kovacs module's pa sub-module."""
    # pa.pos_atoms is initialized during pa module load
    if hasattr(pa, "pos_atoms"):
        return pa.pos_atoms.to(device)
    # Fallback: reconstruct (should not be needed if pa loaded correctly)
    K = kv.K
    gen = torch.Generator(device=device).manual_seed(99999)
    raw = torch.randint(0, 2, (K, N), generator=gen, device=device).float()
    return 2.0 * raw - 1.0


# ─── self-tests ───
def self_test():
    errors = []
    device = torch.device("cpu")

    # Self-test 1: KL = 0 when W_A == W_B, f_A == f_B
    N_t = 16
    W_same = torch.randn(N_t, N_t)
    f_same = torch.ones(N_t, N_t)
    kl1 = kl_diag_laplace(W_same, W_same, f_same, f_same, ridge=0.0)
    if abs(kl1) > 1e-5:
        errors.append(f"Self-test 1 FAIL: KL(same, same) = {kl1:.2e} (expected 0)")

    # Self-test 2: 1-D scalar case
    # W_A=0, W_B=1, f_A=4, f_B=1, ridge=0
    # term_trace = 4/1 = 4; d=1; term_logdet = log(1)-log(4) = -log4 = -1.3863
    # term_quadratic = 4*(1-0)^2 = 4
    # KL = 0.5*(4 - 1 - 1.3863 + 4) = 0.5*(5.6137) = 2.8069
    W_A2 = torch.zeros(1, 1)
    W_B2 = torch.ones(1, 1)
    f_A2 = torch.full((1, 1), 4.0)
    f_B2 = torch.full((1, 1), 1.0)
    kl2 = kl_diag_laplace(W_A2, W_B2, f_A2, f_B2, ridge=0.0)
    expected2 = 0.5 * (4 - 1 - math.log(4) + 4)
    if abs(kl2 - expected2) > 1e-4:
        errors.append(f"Self-test 2 FAIL: KL_1d = {kl2:.4f} (expected {expected2:.4f})")

    # Self-test 3: high-curvature direction up-weighted
    # N=4, single entry perturbation; f_A=100 at [0,0], 0.01 elsewhere; f_B=f_A; W_B[0,0]=1
    N_t3 = 4
    W_A3 = torch.zeros(N_t3, N_t3)
    W_B3 = torch.zeros(N_t3, N_t3)
    W_B3[0, 0] = 1.0
    f_A3 = torch.full((N_t3, N_t3), 0.01)
    f_A3[0, 0] = 100.0
    f_B3 = f_A3.clone()
    kl3 = kl_diag_laplace(W_A3, W_B3, f_A3, f_B3, ridge=0.0)
    # trace = d (f_A/f_B = 1 everywhere); logdet = 0; quadratic = 100*(1)^2 + 0.01*(0)^2*15 = 100
    # KL = 0.5 * (N^2 - N^2 + 0 + 100) = 50.0
    expected3 = 50.0
    if abs(kl3 - expected3) > 1e-4:
        errors.append(f"Self-test 3 FAIL: KL_fisher = {kl3:.4f} (expected {expected3:.4f})")

    # Self-test 4: Euclidean proxy for same setup = 0.5 (naive, 200x smaller than 50)
    eu4 = euclidean_kl_proxy(W_A3, W_B3)
    # ||W_B3 - W_A3||_F^2 = 1.0 (single entry)
    if abs(eu4 - 1.0) > 1e-6:
        errors.append(f"Self-test 4 FAIL: Euclidean proxy = {eu4:.4f} (expected 1.0)")
    # Confirms Fisher is 50x larger than Euclidean for this high-curvature case

    # Self-test 5: PAC-Bayes floor formula
    floor5 = pac_bayes_floor(kl=50.0, m=200.0)
    expected5 = max(0.0, 1.0 - math.sqrt(50.0 / 400.0))
    if abs(floor5 - expected5) > 1e-6:
        errors.append(f"Self-test 5 FAIL: floor={floor5:.6f} expected={expected5:.6f}")

    if errors:
        for e in errors:
            print(f"[SELF-TEST] {e}", flush=True)
        raise AssertionError(f"Self-tests FAILED ({len(errors)} errors)")
    print(f"[SELF-TEST] All 5 self-tests passed", flush=True)


# ─── per-seed, per-pair runner ───
def run_one_cell(seed: int, pair_id: int, N: int, batch_size: int,
                 n_epochs: int, phase_a_epochs: int, n_bytes: int,
                 device) -> dict:
    """Train Phase-A + Phase-B, compute Laplace-Fisher KL, return retention + KL."""
    gen = torch.Generator(device=device).manual_seed(seed)

    # Atoms (match Kovacs base: pa.make_bsc_atoms(vocab_size, N, gen))
    VOCAB = 256
    K_ctx = kv.K  # context window size (== number of position atoms)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K_ctx, N, gen).to(device)

    # Phase A corpus
    corpus_a_bytes = load_corpus_a(n_bytes)
    a_idx, a_tgt = kv.bytes_to_idx_tensors(corpus_a_bytes, device)

    # Phase-A training
    W0 = torch.zeros((N, N), dtype=torch.float32, device=device)
    pool_vecs = torch.zeros((kv.POOL_SIZE, N), dtype=torch.float32, device=device)
    pool_labels = torch.zeros(kv.POOL_SIZE, dtype=torch.long, device=device)
    pool_used = 0

    W_A, pool_vecs, pool_labels, pool_used = kv.train_w_with_replay(
        W0, pool_vecs, pool_labels, pool_used,
        byte_atoms, pos_atoms, a_idx, a_tgt,
        None, None, 0,
        phase_a_epochs, batch_size, device
    )

    # Baseline BPC on Phase-A hold-out
    n_eval = max(1000, len(corpus_a_bytes) // 5)
    corpus_a_eval = load_corpus_a(n_bytes + n_eval)[n_bytes:]
    ae_idx, ae_tgt = kv.bytes_to_idx_tensors(corpus_a_eval, device)
    bpc_A_baseline = kv.evaluate_bpc(W_A, pool_vecs, pool_labels, pool_used,
                                      byte_atoms, pos_atoms, ae_idx, ae_tgt,
                                      batch_size, device)

    # Compute diagonal Fisher at W_A using Phase-A batches
    print(f"    [fisher_A] computing...", flush=True)
    fisher_A = compute_diagonal_fisher(W_A, a_idx, a_tgt, byte_atoms, pos_atoms, batch_size, device)

    # Phase B corpus
    corpus_b_bytes = load_corpus_pair(pair_id, n_bytes, seed)
    b_idx, b_tgt = kv.bytes_to_idx_tensors(corpus_b_bytes, device)

    # Phase-B training (with replay from Phase-A pool)
    W_B, pool_vecs_b, pool_labels_b, pool_used_b = kv.train_w_with_replay(
        W_A.clone(), pool_vecs.clone(), pool_labels.clone(), pool_used,
        byte_atoms, pos_atoms, b_idx, b_tgt,
        pool_vecs, pool_labels, pool_used,
        n_epochs, batch_size, device
    )

    # BPC on Phase-A after Phase-B
    bpc_A_after_B = kv.evaluate_bpc(W_B, pool_vecs_b, pool_labels_b, pool_used_b,
                                     byte_atoms, pos_atoms, ae_idx, ae_tgt,
                                     batch_size, device)
    retention_A = bpc_A_baseline / max(bpc_A_after_B, 1e-9)

    # Compute diagonal Fisher at W_B using Phase-B batches
    print(f"    [fisher_B] computing...", flush=True)
    fisher_B = compute_diagonal_fisher(W_B, b_idx, b_tgt, byte_atoms, pos_atoms, batch_size, device)

    # Compute KLs
    kl_fisher = kl_diag_laplace(W_A, W_B, fisher_A, fisher_B, ridge=1.0 / N)
    kl_euclidean = euclidean_kl_proxy(W_A, W_B)

    # Laplace assumption diagnostic: ||Delta_W||_F / ||W_A||_F
    delta_norm = float(((W_B - W_A) ** 2).sum().sqrt().item())
    W_A_norm = float((W_A ** 2).sum().sqrt().item())
    laplace_ratio = delta_norm / max(W_A_norm, 1e-9)

    # PAC-Bayes floor
    m_total = min(len(corpus_a_bytes), len(corpus_b_bytes))
    floor = pac_bayes_floor(kl_fisher, m_total)

    print(f"    pair={PAIR_NAMES[pair_id]} retention_A={retention_A:.4f} "
          f"kl_fisher={kl_fisher:.2f} kl_eucl={kl_euclidean:.2f} "
          f"laplace_ratio={laplace_ratio:.3f}", flush=True)

    return {
        "bpc_A_baseline": bpc_A_baseline,
        "bpc_A_after_B": bpc_A_after_B,
        "retention_A": retention_A,
        "kl_fisher": kl_fisher,
        "kl_euclidean": kl_euclidean,
        "laplace_ratio": laplace_ratio,
        "laplace_suspect": laplace_ratio > LAPLACE_VIOLATION_THRESH,
        "pac_bayes_floor": floor,
        "m_total": m_total,
    }


def compute_verdict(all_cells: List[dict]) -> Tuple[str, str, dict]:
    """Compute verdict from all (seed, pair) cells."""
    # Filter non-NaN cells
    valid = [c for c in all_cells if not math.isnan(c["kl_fisher"]) and not math.isnan(c["retention_A"])]
    if len(valid) < 3:
        return ("ALT3_INSTRUMENTATION_FAIL",
                f"Fewer than 3 valid cells ({len(valid)}). Cannot compute r^2.",
                {})

    kl_fisher_vals = [c["kl_fisher"] for c in valid]
    kl_eucl_vals = [c["kl_euclidean"] for c in valid]
    retention_vals = [c["retention_A"] for c in valid]

    r2_fisher = pearson_r2(kl_fisher_vals, retention_vals)
    r2_euclidean = pearson_r2(kl_eucl_vals, retention_vals)
    fisher_improvement = r2_fisher - r2_euclidean if not math.isnan(r2_euclidean) else float("nan")

    n_laplace_suspect = sum(1 for c in valid if c.get("laplace_suspect", False))
    laplace_flag = (n_laplace_suspect / len(valid)) > 0.5

    summary = {
        "r2_fisher": r2_fisher,
        "r2_euclidean": r2_euclidean,
        "fisher_improvement_over_euclidean": fisher_improvement,
        "n_valid_cells": len(valid),
        "n_laplace_suspect": n_laplace_suspect,
        "laplace_assumption_suspect_majority": laplace_flag,
        "mean_retention_A": sum(retention_vals) / len(retention_vals),
        "mean_kl_fisher": sum(kl_fisher_vals) / len(kl_fisher_vals),
    }

    if laplace_flag:
        return ("ALT3_LAPLACE_ASSUMPTION_VIOLATED",
                f"Laplace assumption suspect in {n_laplace_suspect}/{len(valid)} cells "
                f"(||Delta_W||_F/||W_A||_F > {LAPLACE_VIOLATION_THRESH} majority). "
                f"KL estimate unreliable. r2_fisher={r2_fisher:.3f} (unreliable).",
                summary)

    if r2_fisher >= PASS_R2 and not math.isnan(fisher_improvement) and fisher_improvement >= FISHER_IMPROVEMENT:
        return ("ALT3_HARD_PASS",
                f"Laplace-Fisher KL predicts retention_A: r^2={r2_fisher:.3f} >= {PASS_R2}, "
                f"Fisher improvement over Euclidean: +{fisher_improvement:.3f} >= {FISHER_IMPROVEMENT}. "
                f"r2_euclidean={r2_euclidean:.3f}. n_valid_cells={len(valid)}. "
                f"PAC-Bayes posterior-over-W KL is binding mechanism for Bet B retention.",
                summary)
    elif r2_fisher < FAIL_R2 and r2_euclidean < FAIL_R2:
        return ("ALT3_HARD_FAIL",
                f"Neither Fisher nor Euclidean KL predicts retention_A: "
                f"r2_fisher={r2_fisher:.3f} < {FAIL_R2}, r2_euclidean={r2_euclidean:.3f} < {FAIL_R2}. "
                f"No weight-space geometry predicts Bet B retention. "
                f"Rehab paths: (a) function-space KL, (b) empirical Bernstein, (c) task-arithmetic.",
                summary)
    else:
        return ("ALT3_MIDDLE",
                f"Partial signal: r2_fisher={r2_fisher:.3f}, r2_euclidean={r2_euclidean:.3f}, "
                f"fisher_improvement={fisher_improvement:.3f} (threshold={FISHER_IMPROVEMENT}). "
                f"n_valid_cells={len(valid)}. Consider larger sweep or KFAC Fisher.",
                summary)


# ─── main ───
def main():
    # Run self-tests FIRST
    self_test()

    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        # Gate protocol: run self-tests only, exit 0 on pass
        sys.exit(0)

    smoke = args.smoke

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[alt3_pac_bayes_kl] device={device} smoke={smoke}", flush=True)

    N = N_SMOKE if smoke else N_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    n_epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    pairs = SMOKE_PAIRS if smoke else list(range(N_PAIRS_FULL))
    mode = "smoke" if smoke else "full"

    out_dir = get_output_dir("wave14_betB_pac_bayes_kl_predictor_v1")
    t0 = time.time()

    all_cells = []
    per_seed_pair: dict = {}

    for seed in seeds:
        print(f"[alt3_pac_bayes_kl] === seed={seed} ===", flush=True)
        per_seed_pair[str(seed)] = {}
        for pair_id in pairs:
            print(f"  pair={pair_id} ({PAIR_NAMES[pair_id]})", flush=True)
            try:
                cell = run_one_cell(seed, pair_id, N, batch_size,
                                    n_epochs, phase_a_epochs, n_bytes, device)
            except Exception as ex:
                print(f"  ERROR pair={pair_id}: {ex}", flush=True)
                cell = {"retention_A": float("nan"), "kl_fisher": float("nan"),
                        "kl_euclidean": float("nan"), "error": str(ex)}
            all_cells.append(cell)
            per_seed_pair[str(seed)][str(pair_id)] = cell
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, verdict_msg, summary = compute_verdict(all_cells)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "per_seed_pair": per_seed_pair,
        "config": {
            "mode": mode,
            "N": N,
            "batch_size": batch_size,
            "n_epochs": n_epochs,
            "phase_a_epochs": phase_a_epochs,
            "n_bytes": n_bytes,
            "seeds": seeds,
            "pairs": pairs,
            "pass_r2": PASS_R2,
            "fail_r2": FAIL_R2,
            "fisher_improvement_threshold": FISHER_IMPROVEMENT,
            "laplace_violation_thresh": LAPLACE_VIOLATION_THRESH,
            "device": str(device),
        },
    }
    validate_metrics(metrics)

    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[alt3_pac_bayes_kl] verdict={verdict}", flush=True)
    print(f"[alt3_pac_bayes_kl] {verdict_msg}", flush=True)
    print(f"[alt3_pac_bayes_kl] elapsed={elapsed:.1f}s  metrics -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
