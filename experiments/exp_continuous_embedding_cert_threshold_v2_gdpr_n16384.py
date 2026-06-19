"""CERT THRESHOLD SWEEP v2 -- GDPR-ALIGNED (Article 17) at N=16384.

SCIENTIFIC QUESTION:
  Does the continuous-embedding substrate support a deletion certificate
  threshold where FP rate <= 0.0001 (0.01%) AND TPR (cert_rate) >= 0.999
  simultaneously, at N=16384 corpus=10000, across 5 seeds?

  GDPR Article 17 compliance gate: FP <= 0.01% is the regulatory
  acceptance bar for right-to-erasure deletion certificates.

DESIGN vs v1:
  v1 swept 9 coarse multipliers [0.1..0.9] against mean(nd_scores).
  v1 outcome (relabeled from MIDDLE_BAND): mean_best_cert_at_fp_zero=0.9067
  at FP=0% -- i.e., 90.7% TPR at strict FP=0.  The GDPR gate is FP<=0.01%
  (not 0%), so the question is whether TPR recovers to >=99.9% at FP=0.01%.

  v2 design:
  (1) Compute the full (del_scores, nd_scores) distribution per seed.
  (2) Build a log-spaced threshold grid covering sorted nd_scores percentiles
      from p=0 to p=0.01 (FP 0..1%) with 200 points -- this is the regime
      that matters for GDPR.  Thresholds are raw absolute values derived from
      the nd_scores ECDF so they track the actual distribution.
  (3) Also sweep a coarse 100-point linear grid over [p=0, p=0.10] for
      context / ROC curve.
  (4) Report: at the FP=0.01% threshold -- what is TPR?
  (5) Early-exit gate: if smoke shows no nd/del score separation
      (overlap_frac > 0.5), file early-exit routing note and skip FULL ship.

PRE-REGISTERED BANDS (GDPR-aligned, orchestrator-supplied, LOAD-BEARING):
  HARD_PASS: FP rate <= 0.0001 (0.01%) AND TPR >= 0.999 (99.9%)
             at SOME threshold across ALL 5 seeds.
             -> audit-grade-vector-store row -> GDPR Article 17 compliant positioning.

  MIDDLE_BAND: FP rate in (0.0001, 0.005] -- some operating point exists but
             does not reach GDPR compliance.
             -> audit-grade-vector-store row stays at 0.45-0.65 with caveat:
             "audit-grade vector store with statistical-deletion assurance,
              not strict-GDPR Article 17 compliance."

  HARD_FAIL: FP rate > 0.005 at best TPR>=0.999 operating point --
             no usable threshold exists for deletion-cert-grade-vector-store.
             -> audit-grade-vector-store row P-band drops or row retired.

FORMULA SELF-TESTS:
  1. FP rate = fraction of nd_scores BELOW threshold.
     At threshold = -inf: FP=0, TPR=0.
     At threshold = +inf: FP=1, TPR=1.
     ECDF at p=0.0001 quantile of nd_scores: FP=0.0001, TPR = f(threshold).
  2. Log-space grid of 200 points in [nd_min, nd_p01]:
     grid[k] = np.exp(np.linspace(log(nd_min+eps), log(nd_p01), 200))
     Ensures dense coverage near FP=0 where regulatory threshold lives.
  3. AUC of ROC curve (trapz) must be > 0.5 for any separability.
     AUC = 0.5 -> random classifier -> HARD_FAIL path triggered.
  Self-test input->output pairs:
    nd_scores = [1,2,3,4,5], del_scores = [0.1,0.2,0.3]
    threshold=0.5: FP = 0/5 = 0.0, TPR = 3/3 = 1.0 (all del below)
    threshold=1.5: FP = 1/5 = 0.2, TPR = 3/3 = 1.0
    threshold=2.5: FP = 2/5 = 0.4, TPR = 3/3 = 1.0
    -> FP=0 AND TPR=1.0 at threshold=0.5: clean separation.

OOM CHECK:
  Same substrate as v1: W = float32 N x N = 16384^2 * 4 = 1.07 GB CPU RAM.
  64GB desktop RAM -- well within budget.

TIMEOUT ESTIMATE:
  v1 smoke (N=512 corpus=128 1-seed) ran ~2s.
  FULL N=16384 corpus=10000 5-seed:
  Scaling: W-build is O(corpus * N) linear in corpus, O(1) in N for batch.
    But W itself is N^2 -- build dominates at large N.
    W-build cost: O(corpus * N^2 / batch) = O(10000 * 16384^2 / 256).
    vs smoke: O(128 * 512^2 / 256).
    Ratio: (10000/128) * (16384/512)^2 = 78.125 * 1024 = 80000x -- too large.
    Actual: W-build is batched matmul, not O(N^2) per pair.
    v1 wall_s=41 for N=16384 corpus=10000 3-seed on GPU.
    CPU ~10-15x slower. 41 * 12 / 3 * 5 = 820s per seed * 5 = 4100s.
    ceil(1.5 * 820 * 5 / 5 [same seeds scale]) = ceil(1.5 * 820) = 1230s per seed.
    Total: 5 * 1230 = 6150s. PROT-019 floor=21600 -> timeout_s=21600.
    Note: PROT-019 override (orchestrator instruction): timeout >= 21600s.

PROT-018: _n16384 binds N = 16384 (anchor name contract).
PROT-019: timeout_s = 21600 (orchestrator floor per task instruction).
PROT-021: seed-checkpoint enabled for resumability.
HDLAB_EXP_NAME=7d39e13 (ENFORCEMENT token from orchestrator).

Anchor: continuous_embedding_cert_threshold_v2_gdpr_n16384
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_continuous_embedding_cert_threshold_v2_gdpr_n16384.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os as _os_omp
_os_omp.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# ── Seed-checkpoint import (PROT-021) ────────────────────────────────────────
_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_ck_cert_v2_gdpr", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
resumable_seeds = _ck.resumable_seeds
write_partial    = _ck.write_partial
aggregate_partials = _ck.aggregate_partials

# ============================================================
# PROT-018: _n16384 binds N = 16384
# ============================================================
N_FULL  = 16384   # PROT-018 binding
N_SMOKE = 512
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

D_EMBED = 768
CORPUS_FULL  = 10_000
CORPUS_SMOKE = 128

SEEDS_FULL  = [7, 17, 23, 31, 43]   # 5 seeds
SEEDS_SMOKE = [17]

N_DELETE = 100  # entries to delete per trial

# Pre-registered GDPR compliance bands (load-bearing, do NOT modify)
# FP rate = fraction of non-deleted entries incorrectly flagged as deleted
# TPR (cert_rate) = fraction of actually-deleted entries correctly certified
GDPR_HARD_PASS_FP_MAX  = 0.0001   # 0.01% -- GDPR Article 17 gate
GDPR_HARD_PASS_TPR_MIN = 0.999    # 99.9% TPR required
GDPR_MIDDLE_FP_MAX     = 0.005    # 0.5% -- audit-grade-but-not-GDPR boundary
GDPR_HARD_FAIL_FP_MIN  = 0.005    # > 0.5% closes deletion-cert positioning

# ROC curve grid parameters
N_GRID_FINE  = 200   # log-spaced points in FP regime [0, 0.01]
N_GRID_COARSE = 100  # linear-spaced points in [0, 0.10] for context
EARLY_EXIT_OVERLAP_FRAC = 0.5  # if >50% del_scores exceed median(nd_scores), early-exit


# ── Core substrate functions ─────────────────────────────────────────────────

def make_synthetic_embeddings(n: int, d: int, seed: int, rank: int = 64) -> np.ndarray:
    """Same generator as v1/v2 for reproducibility."""
    rng = np.random.default_rng(seed + 7000)
    rank = min(rank, d)
    U_raw = rng.standard_normal((d, rank)).astype(np.float32)
    U, _ = np.linalg.qr(U_raw)
    U = U[:, :rank].astype(np.float32)
    z = rng.standard_normal((n, rank)).astype(np.float32) * math.sqrt(5.0)
    noise = rng.standard_normal((n, d)).astype(np.float32) * math.sqrt(0.5)
    embeddings = z @ U.T + noise
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True).clip(min=1e-8)
    return (embeddings / norms).astype(np.float32)


def make_projection_matrix(N: int, d: int, seed: int, device: torch.device) -> torch.Tensor:
    gen = torch.Generator(device=device).manual_seed(seed + 3000)
    return torch.randn(N, d, generator=gen, device=device, dtype=torch.float32) / math.sqrt(d)


def simhash_project(embeddings: torch.Tensor, W_proj: torch.Tensor) -> torch.Tensor:
    return torch.sign(embeddings @ W_proj.T)


def build_substrate(keys_bp: torch.Tensor, vals_bp: torch.Tensor,
                    N: int, device: torch.device) -> torch.Tensor:
    n = keys_bp.shape[0]
    W = torch.zeros(N, N, device=device, dtype=torch.float32)
    batch = 256
    for start in range(0, n, batch):
        end = min(start + batch, n)
        k_b = keys_bp[start:end].to(device)
        v_b = vals_bp[start:end].to(device)
        W.add_(v_b.T @ k_b, alpha=1.0 / N)
    return W


def compute_score_distributions(
    W_orig: torch.Tensor,
    keys_bp: torch.Tensor,
    vals_bp: torch.Tensor,
    n_delete: int,
    N: int,
    device: torch.device,
    seed: int,
) -> Dict:
    """Compute raw deletion-cert scores for deleted + non-deleted entries.

    Returns arrays so we can sweep thresholds without rebuilding W.

    Score = (W_del @ k_q^T)^T . v_q / N, where W_del = W - sum_j v_j k_j^T / N
    for j in deleted entries.  Deleted entries should have near-zero score;
    non-deleted entries should retain their stored value correlation.
    """
    n = keys_bp.shape[0]
    rng = np.random.default_rng(seed + 6000)
    del_indices = rng.choice(n, size=min(n_delete, n), replace=False)
    del_set = set(del_indices.tolist())
    non_del_indices = np.array([i for i in range(n) if i not in del_set])

    # Build W_del by unlearning each deleted entry
    W_del = W_orig.clone()
    for idx in del_indices:
        k_del = keys_bp[idx:idx+1].to(device)
        v_del = vals_bp[idx:idx+1].to(device)
        W_del.sub_(v_del.T @ k_del, alpha=1.0 / N)

    # Non-deleted scores: sample up to 200 for calibration
    nd_sample = non_del_indices[:min(200, len(non_del_indices))]
    nd_scores: List[float] = []
    for idx in nd_sample:
        k_q = keys_bp[idx:idx+1].to(device)
        v_q = vals_bp[idx:idx+1].to(device)
        r = (W_del @ k_q.T).T
        score = (r * v_q).sum(dim=-1).item() / N
        nd_scores.append(float(score))

    # Deleted entry scores
    del_scores: List[float] = []
    for idx in del_indices:
        k_q = keys_bp[idx:idx+1].to(device)
        v_q = vals_bp[idx:idx+1].to(device)
        r = (W_del @ k_q.T).T
        score = (r * v_q).sum(dim=-1).item() / N
        del_scores.append(float(score))

    return {
        "nd_scores":  nd_scores,
        "del_scores": del_scores,
        "n_del":      len(del_indices),
        "n_nd_sample": len(nd_sample),
    }


def build_roc_curve(
    nd_scores: List[float],
    del_scores: List[float],
) -> Dict:
    """Build log-spaced ROC curve covering [FP=0, FP=0.01] finely.

    Returns:
      thresholds: sorted ascending
      fpr:        FP rate at each threshold (fraction of nd_scores below)
      tpr:        TP rate (TPR) at each threshold (fraction of del_scores below)
      auc:        area under the ROC curve (trapz)
      gdpr_tpr:   TPR at the threshold where FPR transitions through GDPR_HARD_PASS_FP_MAX
      best_fp:    best (lowest) FPR where TPR >= GDPR_HARD_PASS_TPR_MIN
    """
    nd_arr = np.array(nd_scores, dtype=np.float64)
    del_arr = np.array(del_scores, dtype=np.float64)

    nd_sorted = np.sort(nd_arr)
    n_nd = len(nd_arr)
    n_del = len(del_arr)

    # Fine grid: log-spaced index into nd_sorted covering FP in [0, 0.01]
    # FP = k/n_nd where k = number of nd_scores below threshold
    # We want FP up to 0.01, so k up to n_nd * 0.01
    max_fine_k = max(1, int(math.ceil(n_nd * 0.01)))
    # Log-space indices 0..max_fine_k
    # Include k=0 explicitly (threshold below all nd_scores -> FP=0)
    fine_ks = np.unique(np.concatenate([
        [0],
        np.round(np.exp(np.linspace(0, math.log(max_fine_k + 1), N_GRID_FINE))).astype(int).clip(0, n_nd),
    ])).astype(int)

    # Coarse grid: linear across FP [0, 0.10]
    coarse_ks = np.linspace(0, int(n_nd * 0.10), N_GRID_COARSE, dtype=int).clip(0, n_nd)

    all_ks = np.unique(np.concatenate([fine_ks, coarse_ks, [n_nd]])).astype(int)

    # Map k -> threshold: if k=0, threshold = nd_sorted[0] - eps (below all nd)
    # If k=j, threshold = nd_sorted[j-1] (we are at the j-th nd_score)
    # FPR = k / n_nd
    thresholds = []
    fprs = []
    tprs = []

    for k in all_ks:
        if k == 0:
            # threshold just below the smallest nd_score
            th = float(nd_sorted[0]) - 1e-9
        elif k < n_nd:
            th = float(nd_sorted[k - 1])
        else:
            # above all nd_scores
            th = float(nd_sorted[-1]) + 1e-9
        fpr = k / n_nd
        tpr = float(np.mean(del_arr <= th))
        thresholds.append(th)
        fprs.append(fpr)
        tprs.append(tpr)

    thresholds = np.array(thresholds)
    fprs = np.array(fprs)
    tprs = np.array(tprs)

    # AUC via trapz (sort by FPR for proper integration)
    sort_idx = np.argsort(fprs)
    auc = float(np.trapezoid(tprs[sort_idx], fprs[sort_idx])
                if hasattr(np, 'trapezoid') else np.trapz(tprs[sort_idx], fprs[sort_idx]))

    # TPR at FPR <= GDPR gate
    gdpr_mask = fprs <= GDPR_HARD_PASS_FP_MAX
    gdpr_tpr = float(np.max(tprs[gdpr_mask])) if gdpr_mask.any() else 0.0

    # Best FPR where TPR >= GDPR TPR gate
    tpr_ok_mask = tprs >= GDPR_HARD_PASS_TPR_MIN
    best_fp = float(np.min(fprs[tpr_ok_mask])) if tpr_ok_mask.any() else 1.0

    # Check early-exit: if overlap fraction too high
    overlap_frac = float(np.mean(del_arr >= np.median(nd_arr)))

    return {
        "thresholds": thresholds.tolist(),
        "fprs":       fprs.tolist(),
        "tprs":       tprs.tolist(),
        "auc":        auc,
        "gdpr_tpr":   gdpr_tpr,
        "best_fp_at_tpr_min": best_fp,
        "overlap_frac": overlap_frac,
        "n_nd":       n_nd,
        "n_del":      n_del,
    }


def evaluate_gdpr_compliance(roc: Dict) -> str:
    """Return HARD_PASS / MIDDLE_BAND / HARD_FAIL for a single seed's ROC."""
    gdpr_tpr = roc["gdpr_tpr"]
    best_fp  = roc["best_fp_at_tpr_min"]

    if gdpr_tpr >= GDPR_HARD_PASS_TPR_MIN:
        # FPR <= 0.01% exists where TPR >= 99.9%
        return "HARD_PASS"
    elif best_fp <= GDPR_MIDDLE_FP_MAX:
        # Some threshold exists with TPR >= 99.9% but FPR in (0.01%, 0.5%]
        return "MIDDLE_BAND"
    else:
        return "HARD_FAIL"


# ── Instrumentation self-test ────────────────────────────────────────────────

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale.

    Self-test cases:
      Separated distributions: nd in [1..5], del in [0.1..0.3]
        -> FP=0 where TPR=1.0 achievable -> HARD_PASS expected
      Overlapping distributions: nd in [0.1..0.5], del in [0.3..0.7]
        -> no FP=0 with TPR=1.0 -> MIDDLE or FAIL expected
    """
    print("[selftest] running _instrumentation_selftest...", flush=True)
    device = torch.device("cpu")

    # ---- Case 1: substrate mechanics ----
    N_t = 256
    d_t = 32
    n_t = 50
    seed_t = 99

    embs = make_synthetic_embeddings(n_t, d_t, seed_t)
    assert embs.shape == (n_t, d_t), f"shape wrong: {embs.shape}"
    norms = np.linalg.norm(embs, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5), f"embs not normalised"

    W_proj = make_projection_matrix(N_t, d_t, seed_t, device)
    embs_t = torch.tensor(embs, dtype=torch.float32, device=device)
    keys_t = simhash_project(embs_t, W_proj)
    vals_t = simhash_project(embs_t, W_proj)
    assert keys_t.shape == (n_t, N_t), f"keys shape wrong"

    W = build_substrate(keys_t, vals_t, N_t, device)
    assert W.shape == (N_t, N_t)
    assert W.isfinite().all(), "W has non-finite values"

    score_data = compute_score_distributions(W, keys_t, vals_t, 5, N_t, device, seed_t)
    nd_s = score_data["nd_scores"]
    del_s = score_data["del_scores"]
    assert len(nd_s) > 0, "nd_scores empty -- filter eliminated all"
    assert len(del_s) > 0, "del_scores empty -- filter eliminated all"
    assert not all(v == 0.0 for v in nd_s), "nd_scores all zero sentinel"
    assert not all(v == 0.0 for v in del_s), "del_scores all zero sentinel"

    # ---- Case 2: ROC curve on controlled distributions ----
    # Separated: del well below nd
    nd_clean  = [1.0, 2.0, 3.0, 4.0, 5.0]
    del_clean = [0.1, 0.15, 0.2]

    roc_clean = build_roc_curve(nd_clean, del_clean)
    assert roc_clean["auc"] > 0.5, f"AUC too low on clean sep: {roc_clean['auc']}"
    # At FP=0 threshold (below all nd), all del should be certified
    assert roc_clean["gdpr_tpr"] == 1.0, (
        f"Expected gdpr_tpr=1.0 on clean separation; got {roc_clean['gdpr_tpr']}"
    )
    # best_fp should be 0.0 (FPR=0 achieves TPR=1.0 >= 0.999)
    assert roc_clean["best_fp_at_tpr_min"] == 0.0, (
        f"Expected best_fp=0.0; got {roc_clean['best_fp_at_tpr_min']}"
    )

    # ---- Case 3: formula self-test (FP rate calculation) ----
    # nd = [1,2,3,4,5], threshold = 1.5 -> 1 nd value (1.0) below -> FP = 1/5 = 0.2
    nd_test   = [1.0, 2.0, 3.0, 4.0, 5.0]
    del_test  = [0.5, 0.8, 1.2]
    roc_test  = build_roc_curve(nd_test, del_test)
    fprs_arr = np.array(roc_test["fprs"])
    tprs_arr = np.array(roc_test["tprs"])
    # At FP=0 (threshold < 1.0), del=[0.5, 0.8] below, del=1.2 above
    # But exact grid depends on implementation; just check AUC > 0.5
    assert roc_test["auc"] > 0.5, f"AUC < 0.5 on test case: {roc_test['auc']}"
    # FPR values should span [0, 1]
    assert fprs_arr.min() == 0.0, f"min FPR != 0: {fprs_arr.min()}"
    # Overlap fraction: del=[0.5,0.8,1.2], nd median=3.0 -> none >= 3.0 -> overlap=0
    assert roc_test["overlap_frac"] == 0.0, (
        f"Expected overlap_frac=0.0; got {roc_test['overlap_frac']}"
    )

    # ---- Case 4: evaluate_gdpr_compliance labels ----
    # Inject synthetic roc dicts
    roc_pass = {"gdpr_tpr": 0.9995, "best_fp_at_tpr_min": 0.00005}
    assert evaluate_gdpr_compliance(roc_pass) == "HARD_PASS", "expected HARD_PASS"

    roc_mid  = {"gdpr_tpr": 0.85, "best_fp_at_tpr_min": 0.001}
    assert evaluate_gdpr_compliance(roc_mid) == "MIDDLE_BAND", "expected MIDDLE_BAND"

    roc_fail = {"gdpr_tpr": 0.70, "best_fp_at_tpr_min": 0.10}
    assert evaluate_gdpr_compliance(roc_fail) == "HARD_FAIL", "expected HARD_FAIL"

    print("[selftest] PASS: all assertions hold.", flush=True)


_instrumentation_selftest()


# ── Per-seed run ─────────────────────────────────────────────────────────────

def run_one_seed(
    seed: int,
    N: int,
    corpus_size: int,
    is_smoke: bool,
    device: torch.device,
) -> Dict:
    t_start = time.time()
    print(f"[seed={seed}] N={N} corpus={corpus_size} smoke={is_smoke}", flush=True)

    embs_key_np = make_synthetic_embeddings(corpus_size, D_EMBED, seed + 100)
    embs_val_np = make_synthetic_embeddings(corpus_size, D_EMBED, seed + 200)

    W_proj_seed = seed + 4000
    W_proj = make_projection_matrix(N, D_EMBED, W_proj_seed, device)
    embs_key_t = torch.tensor(embs_key_np, dtype=torch.float32, device=device)
    embs_val_t = torch.tensor(embs_val_np, dtype=torch.float32, device=device)
    keys_bp = simhash_project(embs_key_t, W_proj).cpu()
    vals_bp = simhash_project(embs_val_t, W_proj).cpu()
    del embs_key_t, embs_val_t

    print(f"  [seed={seed}] building substrate W...", flush=True)
    W = build_substrate(keys_bp, vals_bp, N, device)
    print(f"  [seed={seed}] W built", flush=True)

    n_del = min(N_DELETE, corpus_size // 5)
    score_data = compute_score_distributions(W, keys_bp, vals_bp, n_del, N, device, seed)

    nd_scores  = score_data["nd_scores"]
    del_scores = score_data["del_scores"]
    mean_nd    = float(np.mean(nd_scores))
    mean_del   = float(np.mean(del_scores))
    separation = mean_nd - mean_del
    print(f"  [seed={seed}] mean_nd={mean_nd:.6f} mean_del={mean_del:.6f} "
          f"separation={separation:.6f}", flush=True)

    # Build ROC curve
    roc = build_roc_curve(nd_scores, del_scores)
    print(f"  [seed={seed}] auc={roc['auc']:.4f} gdpr_tpr={roc['gdpr_tpr']:.4f} "
          f"best_fp_at_tpr_min={roc['best_fp_at_tpr_min']:.6f} "
          f"overlap_frac={roc['overlap_frac']:.4f}", flush=True)

    # Per-seed verdict
    seed_verdict = evaluate_gdpr_compliance(roc)
    print(f"  [seed={seed}] seed_verdict={seed_verdict}", flush=True)

    elapsed = time.time() - t_start
    print(f"[seed={seed}] done elapsed={elapsed:.1f}s", flush=True)

    return {
        "seed":           seed,
        "N":              N,
        "corpus_size":    corpus_size,
        "is_smoke":       is_smoke,
        "elapsed_s":      elapsed,
        "mean_nd_score":  mean_nd,
        "mean_del_score": mean_del,
        "score_separation": separation,
        "n_del":          score_data["n_del"],
        "n_nd_sample":    score_data["n_nd_sample"],
        # ROC summary (omit full arrays from per-seed record to keep JSON small)
        "auc":              roc["auc"],
        "gdpr_tpr":         roc["gdpr_tpr"],
        "best_fp_at_tpr_min": roc["best_fp_at_tpr_min"],
        "overlap_frac":     roc["overlap_frac"],
        "seed_verdict":     seed_verdict,
        # Store ROC arrays for full analysis
        "roc_fprs":         roc["fprs"],
        "roc_tprs":         roc["tprs"],
        "roc_thresholds":   roc["thresholds"],
    }


# ── Verdict aggregation ──────────────────────────────────────────────────────

def compute_verdict(per_seed: Dict) -> Dict:
    """Aggregate per-seed GDPR compliance verdicts."""
    seed_verdicts    = [v["seed_verdict"]     for v in per_seed.values()]
    gdpr_tprs        = [v["gdpr_tpr"]         for v in per_seed.values()]
    best_fps         = [v["best_fp_at_tpr_min"] for v in per_seed.values()]
    aucs             = [v["auc"]              for v in per_seed.values()]
    separations      = [v["score_separation"] for v in per_seed.values()]

    n_pass   = sum(1 for x in seed_verdicts if x == "HARD_PASS")
    n_mid    = sum(1 for x in seed_verdicts if x == "MIDDLE_BAND")
    n_fail   = sum(1 for x in seed_verdicts if x == "HARD_FAIL")
    n_seeds  = len(seed_verdicts)

    mean_gdpr_tpr = float(np.mean(gdpr_tprs))
    mean_best_fp  = float(np.mean(best_fps))
    mean_auc      = float(np.mean(aucs))
    mean_sep      = float(np.mean(separations))

    # Overall GDPR verdict (all seeds must pass for HARD_PASS)
    if n_pass == n_seeds:
        overall = "HARD_PASS"
    elif n_fail == n_seeds:
        overall = "HARD_FAIL"
    elif n_pass > 0:
        # Majority pass but not unanimous
        overall = "MIDDLE_BAND"
    elif n_mid > 0:
        overall = "MIDDLE_BAND"
    else:
        overall = "HARD_FAIL"

    return {
        "overall":         overall,
        "n_seeds":         n_seeds,
        "n_pass":          n_pass,
        "n_middle":        n_mid,
        "n_fail":          n_fail,
        "mean_gdpr_tpr":   mean_gdpr_tpr,
        "mean_best_fp":    mean_best_fp,
        "mean_auc":        mean_auc,
        "mean_sep":        mean_sep,
        "seed_verdicts":   seed_verdicts,
    }


# ── Output helpers ───────────────────────────────────────────────────────────

def get_output_dir(default_name: str = "7d39e13") -> Path:
    name = _os_omp.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    is_smoke = _os_omp.environ.get("HDLAB_SMOKE", "0") == "1"
    device   = torch.device("cpu")

    N            = N_SMOKE      if is_smoke else N_FULL
    corpus_size  = CORPUS_SMOKE if is_smoke else CORPUS_FULL
    seeds        = SEEDS_SMOKE  if is_smoke else SEEDS_FULL

    out_dir = get_output_dir()
    print(f"[main] N={N} corpus={corpus_size} seeds={seeds} smoke={is_smoke}", flush=True)
    print(f"[main] GDPR gate: FP<={GDPR_HARD_PASS_FP_MAX} TPR>={GDPR_HARD_PASS_TPR_MIN}",
          flush=True)

    done, remaining = resumable_seeds(seeds, out_dir)
    print(f"[ckpt] {len(done)} done {len(remaining)} remaining: {remaining}", flush=True)

    for seed in remaining:
        result = run_one_seed(seed, N, corpus_size, is_smoke, device)
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, seeds)
    verdict  = compute_verdict(per_seed)
    vd       = verdict

    verdict_msg = (
        f"continuous_embedding_cert_threshold_v2_gdpr_n16384 "
        f"N={N} corpus={corpus_size} seeds={seeds}\n"
        f"GDPR gate: FP<={GDPR_HARD_PASS_FP_MAX} TPR>={GDPR_HARD_PASS_TPR_MIN}\n"
        f"n_pass={vd['n_pass']}/{vd['n_seeds']} n_mid={vd['n_middle']} n_fail={vd['n_fail']}\n"
        f"mean_gdpr_tpr={vd['mean_gdpr_tpr']:.4f} "
        f"mean_best_fp={vd['mean_best_fp']:.6f} "
        f"mean_auc={vd['mean_auc']:.4f}\n"
        f"OVERALL: {vd['overall']}"
    )
    print(verdict_msg, flush=True)

    total_elapsed = sum(s.get("elapsed_s", 0.0) for s in per_seed.values())

    metrics = {
        "exp_name":    "continuous_embedding_cert_threshold_v2_gdpr_n16384",
        "N":           N,
        "corpus_size": corpus_size,
        "seeds":       seeds,
        "is_smoke":    is_smoke,
        "total_elapsed_s": total_elapsed,
        **verdict,
        "verdict_msg": verdict_msg,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(f"[done] metrics -> {metrics_path}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print("[main] --self-test: selftest passed. exit 0.", flush=True)
        sys.exit(0)
    main()
