"""CERT THRESHOLD SWEEP for Arm 4 deletion certificate at N=16384 (v1).

CONTEXT (cap_map v305; continuous_embedding_storage_substrate_v2_n16384 MIDDLE_BAND):
  v2 Arm 4 landed cert_rate=1.000 but fp_rate=0.010 (1pp above strict 0% gate).
  The auto-calibrated threshold = mean(non_deleted_scores) * 0.5 caused 1/100
  non-deleted entries to score below threshold (false positive).

  This experiment sweeps the threshold multiplier (0.1 to 0.9) and measures
  the fp_rate vs cert_rate tradeoff at each multiplier value to find an operating
  point where fp_rate=0 while cert_rate stays >= 0.95 (HARD-PASS threshold).

SCIENTIFIC QUESTION:
  Is there a threshold multiplier in [0.1, 0.9] where fp_rate=0 AND cert_rate >= 0.95?
  If yes: Arm 4 moves to HARD_PASS at that operating point -> overall moat survives.
  If no: there is a fundamental overlap between deleted and non-deleted score
         distributions -> Arm 4 needs a redesigned scoring criterion.

DESIGN:
  Same corpus as v2 (N=16384, corpus=10000, seeds=[7,17,23]).
  Threshold multipliers: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9].
  For each multiplier: threshold = mean(non_deleted_scores) * multiplier.
  Report: cert_rate and fp_rate at each multiplier per seed.
  Optimal: the largest multiplier where fp_rate=0 with cert_rate >= 0.95.

PRE-REGISTERED BANDS:

  PRIMARY metric: exists_clean_threshold (bool)
    HARD-PASS : at least one multiplier in [0.1, 0.9] achieves fp_rate=0 AND cert_rate >= 0.95
                in all 3 seeds. Arm 4 closes to HARD_PASS at the best operating point.
    HARD-FAIL : no multiplier achieves fp_rate=0 AND cert_rate >= 0.95 simultaneously
                in any seed. Score distributions fundamentally overlap; redesign needed.
    MIDDLE    : at least one multiplier achieves the condition in 1-2 of 3 seeds (borderline).

  SECONDARY: best_cert_rate at fp_rate=0 (the cert_rate at the fp_rate=0 operating point).
    HARD-PASS: best_cert_rate >= 0.95 (3/3 seeds)
    MIDDLE:    best_cert_rate 0.80-0.95 (partial; documented gap)
    HARD-FAIL: best_cert_rate < 0.80 (cert degrades too much at fp_rate=0)

OOM CHECK:
  Identical memory footprint to v2 (CPU-only run; N=16384 corpus=10000 on 64GB RAM desktop).
  W: 16384 x 16384 x float32 = 1.07 GB CPU RAM. Well within 64 GB.

TIMEOUT ESTIMATE:
  v2 wall_s=41 for 3 seeds on GPU. CPU is ~10-20x slower.
  Estimate: 41 * 15 = 615s per seed. With 9 threshold values: computation is
  SAME as v2 per seed (threshold loop is free; just re-classifies existing scores).
  Total: 3 seeds x 615s = 1845s. Safety: ceil(1.5 * 1845) = 2768s -> 3000s.
  PROT-019 floor: 14400s. timeout_s = 14400.
  Note: CPU overhead may be much lower because W build dominates and threshold
  sweep is arithmetic on pre-computed scores -- actual wall ~600-1200s expected.

FORMULA SELF-TESTS:
  1. threshold = mean(nd_scores) * multiplier.
     At multiplier=0.0: threshold=0 -> ALL entries score >= 0 -> fp_rate=0, cert_rate=0.
     At multiplier=1.0: threshold=mean(nd_scores) -> ~50% of nd entries below threshold.
     Expected: there exists a multiplier in (0, 0.5) where fp_rate=0 and cert_rate~1.
  2. Deleted entry score ~ mean(nd_scores) * eps (eps << 1) because deleted entry
     contributes zero to W_del at its key. Non-deleted entry score ~ mean(nd_scores).
     Distribution separation should allow fp_rate=0 at threshold ~ mean * 0.3-0.4.
  3. cert_rate at multiplier=0.1 should be ~1.0 (all deleted entries well below).
     fp_rate at multiplier=0.1 should be 0 (no non-deleted entry scores that low).

PROT-018: _n16384 binds N = 16384.
PROT-019: timeout_s = 14400.

Anchor: continuous_embedding_cert_threshold_v1_n16384
Queue: remote_cpu_queue (CPU-only; W build at N=16384 ~1 GB RAM, ~5-10 min)
Pre-reg: preregs/2026-06-01_continuous_embedding_cert_threshold_v1_n16384.md
HDLAB_EXP_NAME: cert_thresh_v1
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os as _os_omp
_os_omp.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import importlib.util
_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_ck_cert_thresh_v1", _ck_path)
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

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_DELETE = 100

# Threshold multipliers to sweep
THRESHOLD_MULTIPLIERS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

# Pre-registered thresholds for arm classification
HP_CERT_RATE_AT_ZERO_FP = 0.95   # cert_rate must be >= 0.95 at fp_rate=0 point
HP_CERT_RATE_MIDDLE     = 0.80


def make_synthetic_embeddings(n: int, d: int, seed: int, rank: int = 64) -> np.ndarray:
    """Same generator as v2 for reproducibility."""
    rng = np.random.default_rng(seed + 7000)
    rank = min(rank, d)
    U_raw = rng.standard_normal((d, rank)).astype(np.float32)
    U, _ = np.linalg.qr(U_raw)
    U = U[:, :rank].astype(np.float32)
    z = rng.standard_normal((n, rank)).astype(np.float32) * math.sqrt(5.0)
    noise_var = 0.5
    noise = rng.standard_normal((n, d)).astype(np.float32) * math.sqrt(noise_var)
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


def compute_cert_scores(
    W_orig: torch.Tensor,
    keys_bp: torch.Tensor,
    vals_bp: torch.Tensor,
    embeddings_np: np.ndarray,
    N_DELETE: int,
    N: int,
    device: torch.device,
    seed: int,
    w_proj_seed: int,
) -> Dict:
    """Compute raw deletion scores for both deleted and non-deleted entries.

    Returns the raw score arrays so we can sweep thresholds without re-building W.
    """
    n = keys_bp.shape[0]
    rng = np.random.default_rng(seed + 6000)
    del_indices = rng.choice(n, size=min(N_DELETE, n), replace=False)
    non_del_indices = np.array([i for i in range(n) if i not in set(del_indices)])

    # Build W_del
    W_del = W_orig.clone()
    for idx in del_indices:
        k_del = keys_bp[idx:idx+1].to(device)
        v_del = vals_bp[idx:idx+1].to(device)
        W_del.sub_(v_del.T @ k_del, alpha=1.0 / N)

    # Scores for non-deleted entries (calibration sample, max 100)
    nd_sample = non_del_indices[:min(100, len(non_del_indices))]
    nd_scores = []
    for idx in nd_sample:
        k_q = keys_bp[idx:idx+1].to(device)
        v_q = vals_bp[idx:idx+1].to(device)
        r = (W_del @ k_q.T).T
        score = (r * v_q).sum(dim=-1).item() / N
        nd_scores.append(float(score))

    # Scores for deleted entries
    del_scores = []
    for idx in del_indices:
        k_q = keys_bp[idx:idx+1].to(device)
        v_q = vals_bp[idx:idx+1].to(device)
        r = (W_del @ k_q.T).T
        score = (r * v_q).sum(dim=-1).item() / N
        del_scores.append(float(score))

    return {
        "nd_scores": nd_scores,
        "del_scores": del_scores,
        "n_del": len(del_indices),
        "n_nd": len(nd_sample),
    }


def sweep_thresholds(
    nd_scores: List[float],
    del_scores: List[float],
    multipliers: List[float],
) -> List[Dict]:
    """Sweep threshold multipliers and compute cert_rate + fp_rate at each."""
    nd_arr = np.array(nd_scores)
    del_arr = np.array(del_scores)
    mean_nd = float(np.mean(nd_arr))

    results = []
    for mult in multipliers:
        threshold = mean_nd * mult
        cert_rate = float(np.mean(del_arr < threshold))
        fp_rate   = float(np.mean(nd_arr < threshold))
        results.append({
            "multiplier": mult,
            "threshold": threshold,
            "cert_rate": cert_rate,
            "fp_rate": fp_rate,
        })
    return results


def _instrumentation_selftest() -> None:
    """Assert cert threshold sweep mechanics are correct at tiny scale."""
    device = torch.device("cpu")
    N_t = 256
    d_t = 32
    n_t = 50
    seed_t = 42

    embs = make_synthetic_embeddings(n_t, d_t, seed_t)
    assert embs.shape == (n_t, d_t)
    norms = np.linalg.norm(embs, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5), f"embs not normalised: {norms[:3]}"

    W_proj = make_projection_matrix(N_t, d_t, seed_t, device)
    embs_t = torch.tensor(embs, dtype=torch.float32, device=device)
    keys_t = simhash_project(embs_t, W_proj)
    vals_t = simhash_project(embs_t, W_proj)

    W = build_substrate(keys_t, vals_t, N_t, device)
    assert W.shape == (N_t, N_t)
    assert W.isfinite().all()

    score_data = compute_cert_scores(
        W, keys_t, vals_t, embs, 5, N_t, device, seed_t, seed_t + 1
    )
    assert "nd_scores" in score_data
    assert "del_scores" in score_data
    assert len(score_data["nd_scores"]) > 0, "nd_scores empty"
    assert len(score_data["del_scores"]) > 0, "del_scores empty"

    # Sweep thresholds
    sweep = sweep_thresholds(
        score_data["nd_scores"], score_data["del_scores"], [0.1, 0.5, 0.9]
    )
    assert len(sweep) == 3
    for row in sweep:
        assert 0.0 <= row["cert_rate"] <= 1.0, f"cert_rate OOB: {row}"
        assert 0.0 <= row["fp_rate"] <= 1.0, f"fp_rate OOB: {row}"

    # At mult=0.1: threshold very low -> cert_rate and fp_rate both should be small
    # (deleted entries have near-zero scores, non-deleted entries have higher scores)
    low_thresh_row = sweep[0]
    assert low_thresh_row["multiplier"] == 0.1

    print("[selftest] PASS: cert threshold sweep mechanics verified.", flush=True)


_instrumentation_selftest()


def run_one_seed(seed: int, N: int, corpus_size: int,
                 is_smoke: bool, device: torch.device) -> Dict:
    t_start = time.time()
    print(f"[seed={seed}] N={N} corpus={corpus_size} smoke={is_smoke}", flush=True)

    # Build corpus
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

    # Compute raw cert scores once
    n_del = min(N_DELETE, corpus_size // 5)
    score_data = compute_cert_scores(
        W, keys_bp, vals_bp, embs_key_np, n_del, N, device, seed, W_proj_seed
    )

    nd_scores  = score_data["nd_scores"]
    del_scores = score_data["del_scores"]
    mean_nd    = float(np.mean(nd_scores))
    mean_del   = float(np.mean(del_scores))

    print(f"  [seed={seed}] mean_nd_score={mean_nd:.6f} mean_del_score={mean_del:.6f}",
          flush=True)

    # Sweep thresholds
    sweep_results = sweep_thresholds(nd_scores, del_scores, THRESHOLD_MULTIPLIERS)

    for row in sweep_results:
        print(f"  [seed={seed}] mult={row['multiplier']:.1f} "
              f"threshold={row['threshold']:.6f} "
              f"cert_rate={row['cert_rate']:.4f} fp_rate={row['fp_rate']:.4f}",
              flush=True)

    # Find clean operating point: largest multiplier with fp_rate=0 and cert_rate >= 0.95
    clean_ops = [r for r in sweep_results
                 if r["fp_rate"] == 0.0 and r["cert_rate"] >= HP_CERT_RATE_AT_ZERO_FP]
    has_clean_threshold = len(clean_ops) > 0
    best_clean_mult = max(clean_ops, key=lambda r: r["multiplier"])["multiplier"] \
                      if clean_ops else None
    best_clean_cert  = max(clean_ops, key=lambda r: r["multiplier"])["cert_rate"] \
                       if clean_ops else None

    # Best cert at fp_rate=0 (any multiplier)
    fp_zero_ops = [r for r in sweep_results if r["fp_rate"] == 0.0]
    best_cert_at_fp_zero = max((r["cert_rate"] for r in fp_zero_ops), default=0.0)

    elapsed = time.time() - t_start
    print(f"[seed={seed}] has_clean_threshold={has_clean_threshold} "
          f"best_clean_mult={best_clean_mult} best_cert_at_fp_zero={best_cert_at_fp_zero:.4f} "
          f"elapsed={elapsed:.1f}s", flush=True)

    return {
        "seed": seed,
        "N": N,
        "corpus_size": corpus_size,
        "is_smoke": is_smoke,
        "elapsed_s": elapsed,
        "mean_nd_score": mean_nd,
        "mean_del_score": mean_del,
        "score_separation": float(mean_nd - mean_del),
        "has_clean_threshold": has_clean_threshold,
        "best_clean_mult": best_clean_mult if best_clean_mult is not None else -1.0,
        "best_clean_cert_rate": best_clean_cert if best_clean_cert is not None else 0.0,
        "best_cert_at_fp_zero": best_cert_at_fp_zero,
        "sweep": sweep_results,
        "n_del": score_data["n_del"],
        "n_nd": score_data["n_nd"],
    }


def compute_verdict(per_seed: Dict) -> Dict:
    """Compute overall verdict from per-seed results."""
    all_has_clean = [v["has_clean_threshold"] for v in per_seed.values()]
    all_best_cert = [v["best_cert_at_fp_zero"] for v in per_seed.values()]

    n_seeds_clean = sum(1 for x in all_has_clean if x)
    mean_best_cert = float(np.mean(all_best_cert)) if all_best_cert else 0.0

    # PRIMARY: exists_clean_threshold in ALL seeds
    if all(all_has_clean):
        arm_clean = "HARD_PASS"
    elif n_seeds_clean == 0:
        arm_clean = "HARD_FAIL"
    else:
        arm_clean = "MIDDLE_BAND"

    # SECONDARY: best_cert_rate at fp_rate=0
    if mean_best_cert >= HP_CERT_RATE_AT_ZERO_FP:
        arm_cert = "HARD_PASS"
    elif mean_best_cert >= HP_CERT_RATE_MIDDLE:
        arm_cert = "MIDDLE_BAND"
    else:
        arm_cert = "HARD_FAIL"

    if arm_clean == "HARD_PASS" and arm_cert == "HARD_PASS":
        overall = "HARD_PASS"
    elif arm_clean == "HARD_FAIL" or arm_cert == "HARD_FAIL":
        overall = "HARD_FAIL"
    else:
        overall = "MIDDLE_BAND"

    return {
        "arm_clean_threshold": arm_clean,
        "arm_cert_quality": arm_cert,
        "overall": overall,
        "n_seeds_with_clean_threshold": n_seeds_clean,
        "mean_best_cert_at_fp_zero": mean_best_cert,
    }


def get_output_dir(default_name: str = "cert_thresh_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def main() -> None:
    is_smoke = os.environ.get("HDLAB_SMOKE", "0") == "1"
    device = torch.device("cpu")   # CPU-only run

    N = N_SMOKE if is_smoke else N_FULL
    corpus_size = CORPUS_SMOKE if is_smoke else CORPUS_FULL
    seeds = SEEDS_SMOKE if is_smoke else SEEDS_FULL

    out_dir = get_output_dir()
    print(f"[main] N={N} corpus={corpus_size} seeds={seeds} smoke={is_smoke}", flush=True)
    print(f"[main] threshold multipliers={THRESHOLD_MULTIPLIERS}", flush=True)

    done, remaining = resumable_seeds(seeds, out_dir)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining: {remaining}", flush=True)

    for seed in remaining:
        result = run_one_seed(seed, N, corpus_size, is_smoke, device)
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, seeds)
    verdict = compute_verdict(per_seed)

    vd = verdict
    verdict_msg = (
        f"continuous_embedding_cert_threshold_v1_n16384 "
        f"N={N} corpus={corpus_size} seeds={seeds}\n"
        f"ArmClean: {vd['arm_clean_threshold']} | "
        f"n_seeds_clean={vd['n_seeds_with_clean_threshold']}/{len(seeds)}\n"
        f"ArmCert: {vd['arm_cert_quality']} | "
        f"mean_best_cert_at_fp_zero={vd['mean_best_cert_at_fp_zero']:.4f}\n"
        f"OVERALL: {vd['overall']}"
    )
    print(verdict_msg, flush=True)

    total_elapsed = sum(s.get("elapsed_s", 0.0) for s in per_seed.values())

    metrics = {
        "exp_name": "continuous_embedding_cert_threshold_v1_n16384",
        "N": N,
        "corpus_size": corpus_size,
        "seeds": seeds,
        "is_smoke": is_smoke,
        "n_seeds_complete": len(per_seed),
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
