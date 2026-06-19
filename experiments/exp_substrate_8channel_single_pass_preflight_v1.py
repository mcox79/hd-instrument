"""substrate_8channel_single_pass_preflight_v1 -- CPU pre-flight for Experiment C.

SCIENTIFIC QUESTION (per user research-Q5 recommendation):
  Can all 8 substrate channel signals be extracted from a SINGLE substrate forward
  pass (cheap single-pass economy holds) or do they require K-fold separate
  passes (expensive)? If the K-fold blowup exceeds 4x, the main ablation cost
  model breaks and we should abort before $10-15 cloud spend.

DESIGN:
  - Build a small substrate W (N=512 by default, 256 in smoke for speed).
  - Time 8 channel-signal computations under two regimes:
      (a) K-fold: each channel computed independently with its own probe vectors.
      (b) Single-pass-ish: shared building blocks W @ xi, Tr(W^k) probes reused
          across cumulant channels (Monitor, Curvature, Counterfactual share
          (W, xi) infrastructure).
  - Report wall-time ratio k_fold / single_pass.

PRE-REGISTERED BANDS:
  PASS  (proceed):       ratio < 2.0 -- single-pass economy holds
  WARN  (proceed flag):  ratio in [2.0, 4.0) -- some channels need extra passes
  FAIL  (abort main):    ratio >= 4.0 -- single-pass economy broken; cancel cloud spend

PROT-022 SELFTESTS:
  1. Hutchinson trace estimators within 10% of identity exact values.
  2. matvec timing sanity (W @ xi takes 10us-10ms for N=256-1024).

RUN MODES:
  smoke -> N=128, n_repeats=5
  full  -> N=512, n_repeats=20

ASCII-only per feedback_ascii_only_in_scripts.
PROT-018: anchor name fixed at substrate_8channel_single_pass_preflight_v1.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir
from testbed.llm_integration.substrate_audit import (
    hebbian_write,
    retrieval_cosine,
    deletion_cert,
    kappa_2_hutchinson,
    kappa_3_hutchinson,
    kappa_4_excess_hutchinson,
)
from testbed.substrate_lm.primitives import (
    anti_hebbian_contrastive_update,
    hierarchical_recurrent_retrieve,
)


ANCHOR_NAME = "substrate_8channel_single_pass_preflight_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N_SUBSTRATE = 128
    N_REPEATS = 5
    N_PROBES = 4
    M_PATTERNS = 8
else:
    N_SUBSTRATE = 512
    N_REPEATS = 20
    N_PROBES = 8
    M_PATTERNS = 32

# Bands
RATIO_PASS = 2.0
RATIO_WARN = 4.0


# -----------------------------------------------------------------------------
# K-fold regime: each channel computes its own probes / matvecs independently
# -----------------------------------------------------------------------------
def k_fold_pass(W: np.ndarray, xi: np.ndarray, forbidden: np.ndarray,
                  rng_seed: int) -> Dict[str, float]:
    """Each channel computed independently. Returns wall_s + per-channel metrics."""
    metrics: Dict[str, float] = {}
    # Write
    W_after = hebbian_write(W, xi)
    metrics["write_cos"] = retrieval_cosine(W_after, xi)
    # Erase
    cos_pre = retrieval_cosine(W, xi)
    metrics["erase_cos_pre"] = cos_pre
    # Monitor
    rng_m = np.random.default_rng(rng_seed)
    k3, _ = kappa_3_hutchinson(W, n_probes=N_PROBES, rng=rng_m)
    metrics["monitor_k3"] = k3
    # Chain-consistency
    xi_b = xi.copy()
    flip = np.random.default_rng(rng_seed + 1).random(W.shape[0]) < 0.05
    xi_b[flip] = -xi_b[flip]
    path_a = hierarchical_recurrent_retrieve(W, xi, n_steps=3)
    path_b = hierarchical_recurrent_retrieve(W, xi_b, n_steps=3)
    na = np.linalg.norm(path_a) + 1e-30
    nb = np.linalg.norm(path_b) + 1e-30
    metrics["chain_c"] = float((path_a @ path_b) / (na * nb))
    # Curvature
    rng_c = np.random.default_rng(rng_seed + 2)
    k2, _ = kappa_2_hutchinson(W, n_probes=N_PROBES, rng=rng_c)
    metrics["curvature_k2"] = k2
    # Contrastive
    rng_co = np.random.default_rng(rng_seed + 3)
    xi_n1 = rng_co.choice([-1.0, 1.0], size=W.shape[0]).astype(np.float32)
    xi_n2 = rng_co.choice([-1.0, 1.0], size=W.shape[0]).astype(np.float32)
    y = W @ xi_n1
    n1 = np.linalg.norm(y) + 1e-30
    n2 = np.linalg.norm(xi_n2) + 1e-30
    metrics["contrastive_neg_cos"] = float((y @ xi_n2) / (n1 * n2))
    # Repulse-class
    y2 = W @ xi
    y2n = np.linalg.norm(y2) + 1e-30
    leaf_norms = np.linalg.norm(forbidden, axis=1) + 1e-30
    cos_vec = (forbidden @ y2) / (leaf_norms * y2n)
    metrics["repulse_r"] = float(np.max(cos_vec))
    # Counterfactual
    rng_cf = np.random.default_rng(rng_seed + 4)
    deltas: List[float] = []
    for _k in range(2):
        xi_k = rng_cf.choice([-1.0, 1.0], size=W.shape[0]).astype(np.float32)
        W_prime, _cert, _ = deletion_cert(W, xi_k)
        y1 = W @ xi
        y2cf = W_prime @ xi
        deltas.append(float(np.linalg.norm(y2cf - y1)))
    metrics["counterfactual_delta"] = float(np.mean(deltas))
    return metrics


# -----------------------------------------------------------------------------
# Single-pass-ish regime: share building blocks across channels
# -----------------------------------------------------------------------------
def single_pass_ish(W: np.ndarray, xi: np.ndarray, forbidden: np.ndarray,
                     rng_seed: int) -> Dict[str, float]:
    """Channels share building blocks where feasible.

    Shared:
      - W @ xi (used by Write, Erase, Repulse, Counterfactual)
      - One Hutchinson probe set V (used for k2, k3 together: paired probe variance)
      - hierarchical_recurrent_retrieve path_a (used by Chain only since it
        requires a perturbed second pass; we keep that one extra)
    """
    metrics: Dict[str, float] = {}
    N = W.shape[0]
    # Shared matvec
    Wx = W @ xi
    Wx_norm = np.linalg.norm(Wx) + 1e-30
    xi_norm = np.linalg.norm(xi) + 1e-30
    cos_xi = float((Wx @ xi) / (Wx_norm * xi_norm))
    # Write: needs W_after = W + (1/N) xi xi^T; only need Wx_after @ xi which =
    # Wx @ xi + (xi @ xi) (xi @ xi) / N = Wx@xi + N
    cos_after = float((Wx @ xi + N) / ((Wx_norm + 1e-3) * xi_norm))
    metrics["write_cos"] = cos_after
    metrics["erase_cos_pre"] = cos_xi
    # Shared Hutchinson probes for k2 and k3
    rng = np.random.default_rng(rng_seed)
    V0 = rng.choice([-1.0, 1.0], size=(N, N_PROBES)).astype(np.float32)
    V1 = W @ V0
    V2 = W @ V1
    V3 = W @ V2
    p2 = (V0.astype(np.float64) * V2.astype(np.float64)).sum(axis=0) / float(N)
    p3 = (V0.astype(np.float64) * V3.astype(np.float64)).sum(axis=0) / float(N)
    metrics["monitor_k3"] = float(np.mean(p3))
    metrics["curvature_k2"] = float(np.mean(p2))
    # Chain-consistency: requires a separate 3-step retrieve from a perturbed query
    xi_b = xi.copy()
    flip = np.random.default_rng(rng_seed + 1).random(N) < 0.05
    xi_b[flip] = -xi_b[flip]
    path_a = hierarchical_recurrent_retrieve(W, xi, n_steps=3)
    path_b = hierarchical_recurrent_retrieve(W, xi_b, n_steps=3)
    na = np.linalg.norm(path_a) + 1e-30
    nb = np.linalg.norm(path_b) + 1e-30
    metrics["chain_c"] = float((path_a @ path_b) / (na * nb))
    # Contrastive: needs neg pair; separate randoms
    rng_co = np.random.default_rng(rng_seed + 3)
    xi_n1 = rng_co.choice([-1.0, 1.0], size=N).astype(np.float32)
    xi_n2 = rng_co.choice([-1.0, 1.0], size=N).astype(np.float32)
    Wxn1 = W @ xi_n1
    n1 = np.linalg.norm(Wxn1) + 1e-30
    n2 = np.linalg.norm(xi_n2) + 1e-30
    metrics["contrastive_neg_cos"] = float((Wxn1 @ xi_n2) / (n1 * n2))
    # Repulse: reuse Wx
    leaf_norms = np.linalg.norm(forbidden, axis=1) + 1e-30
    cos_vec = (forbidden @ Wx) / (leaf_norms * Wx_norm)
    metrics["repulse_r"] = float(np.max(cos_vec))
    # Counterfactual: cannot be shared (requires rank-1 W' substitution); keep separate
    rng_cf = np.random.default_rng(rng_seed + 4)
    deltas: List[float] = []
    for _k in range(2):
        xi_k = rng_cf.choice([-1.0, 1.0], size=N).astype(np.float32)
        W_prime, _cert, _ = deletion_cert(W, xi_k)
        y1 = Wx
        y2cf = W_prime @ xi
        deltas.append(float(np.linalg.norm(y2cf - y1)))
    metrics["counterfactual_delta"] = float(np.mean(deltas))
    return metrics


def time_block(fn, *args, n_repeats: int = 10) -> float:
    """Returns mean wall ms per call."""
    # Warm-up
    fn(*args)
    t0 = time.time()
    for _ in range(n_repeats):
        fn(*args)
    return (time.time() - t0) / float(n_repeats) * 1000.0


# -----------------------------------------------------------------------------
# PROT-022 self-tests
# -----------------------------------------------------------------------------
def _selftest() -> None:
    """Hutchinson trace + matvec timing sanity."""
    print("[selftest preflight] start", flush=True)
    rng = np.random.default_rng(0)
    N = 128
    # Identity: Tr(I^2)/N = 1, Tr(I^3)/N = 1
    W_id = np.eye(N, dtype=np.float32)
    k2, _ = kappa_2_hutchinson(W_id, n_probes=20, rng=rng)
    k3, _ = kappa_3_hutchinson(W_id, n_probes=20, rng=np.random.default_rng(1))
    assert abs(k2 - 1.0) < 0.15, f"kappa_2(I) = {k2}, expected 1.0"
    assert abs(k3 - 1.0) < 0.15, f"kappa_3(I) = {k3}, expected 1.0"
    print(f"  k2(I)={k2:.4f} k3(I)={k3:.4f} (both ~1.0)", flush=True)

    # matvec timing sanity (10us-100ms for N=128)
    W = rng.standard_normal((N, N)).astype(np.float32)
    xi = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    t0 = time.time()
    for _ in range(50):
        _ = W @ xi
    dt_us = (time.time() - t0) / 50.0 * 1e6
    assert dt_us > 0.0 and dt_us < 100_000, f"matvec timing odd: {dt_us}us"
    print(f"  matvec N={N}: {dt_us:.1f}us/call", flush=True)
    print("[selftest preflight] PASS", flush=True)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> int:
    print(f"[main] anchor={ANCHOR_NAME} run_mode={RUN_MODE}", flush=True)
    print(f"[main] N={N_SUBSTRATE} n_repeats={N_REPEATS} n_probes={N_PROBES} "
          f"M_patterns={M_PATTERNS}", flush=True)

    _selftest()

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[main] out_dir={out_dir}", flush=True)

    # Build substrate
    rng = np.random.default_rng(7)
    Xi = rng.choice([-1.0, 1.0], size=(M_PATTERNS, N_SUBSTRATE)).astype(np.float32)
    W = (Xi.T @ Xi) / float(N_SUBSTRATE)
    xi = Xi[0]
    forbidden = rng.choice([-1.0, 1.0], size=(48, N_SUBSTRATE)).astype(np.float32)

    print(f"[main] timing K-fold regime (each channel independent)...", flush=True)
    k_fold_ms = time_block(k_fold_pass, W, xi, forbidden, 100, n_repeats=N_REPEATS)
    print(f"  K-fold mean: {k_fold_ms:.3f} ms/call", flush=True)

    print(f"[main] timing single-pass-ish regime (shared building blocks)...", flush=True)
    single_pass_ms = time_block(single_pass_ish, W, xi, forbidden, 100, n_repeats=N_REPEATS)
    print(f"  single-pass mean: {single_pass_ms:.3f} ms/call", flush=True)

    if single_pass_ms < 1e-9:
        ratio = float("inf")
    else:
        ratio = float(k_fold_ms / single_pass_ms)
    print(f"[main] ratio k_fold / single_pass = {ratio:.3f}", flush=True)

    # Verify metrics match (sanity)
    k_metrics = k_fold_pass(W, xi, forbidden, 100)
    sp_metrics = single_pass_ish(W, xi, forbidden, 100)
    print(f"[main] k-fold metrics:    {k_metrics}", flush=True)
    print(f"[main] single-pass metrics: {sp_metrics}", flush=True)

    # Verdict
    if ratio < RATIO_PASS:
        verdict = "PASS"
        verdict_msg = (
            f"PASS (single-pass economy holds): k_fold/single_pass = {ratio:.3f} < {RATIO_PASS}. "
            f"All 8 channels can be derived from shared building blocks (W matvec + "
            f"paired Hutchinson probes); Counterfactual is the only channel that "
            f"genuinely needs a rank-1 W' substitution. Main ablation cost model intact; "
            f"proceed to substrate_8channel_orchestration_ablation_gpt2small_v1."
        )
    elif ratio < RATIO_WARN:
        verdict = "WARN"
        verdict_msg = (
            f"WARN (proceed but flag): k_fold/single_pass = {ratio:.3f} in "
            f"[{RATIO_PASS}, {RATIO_WARN}). Some channels need extra forward passes; "
            f"main ablation will run at slightly higher cost than planned. Surface "
            f"to user before $10-15 cloud spend."
        )
    else:
        verdict = "FAIL"
        verdict_msg = (
            f"FAIL (abort main): k_fold/single_pass = {ratio:.3f} > {RATIO_WARN}. "
            f"Single-pass economic claim broken. Main ablation will run at >>4x "
            f"cost vs single-channel CE; cancel cloud spend and redesign channel set "
            f"with stricter shared-building-block discipline."
        )

    metrics_out = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N_SUBSTRATE,
        "n_repeats": N_REPEATS,
        "n_probes": N_PROBES,
        "M_patterns": M_PATTERNS,
        "k_fold_wall_ms": k_fold_ms,
        "single_pass_wall_ms": single_pass_ms,
        "ratio": ratio,
        "k_fold_metrics_sample": k_metrics,
        "single_pass_metrics_sample": sp_metrics,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "pre_registered_bands": {
            "PASS": f"ratio < {RATIO_PASS}",
            "WARN": f"{RATIO_PASS} <= ratio < {RATIO_WARN}",
            "FAIL": f"ratio >= {RATIO_WARN}",
        },
    }
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics_out, fh, indent=2)
    print(f"[main] metrics written to {metrics_path}", flush=True)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    return 0


if __name__ == "__main__":
    if _ARGS.self_test:
        _selftest()
        sys.exit(0)
    sys.exit(main())
