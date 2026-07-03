"""Unified SVD-cascade falsifier: equal-spacing of detached singular values across substrate variants.

HANDOFF: notes/exp_dev_handoff_unified_svd_cascade_falsifier_2026-05-26.md
PARENT RESEARCH: notes/research_framework_synthesis_moe_1rsb_saddle_2026-05-26.md

HYPOTHESIS (UNIFIED, P=0.46): Bachtis-Biroli-Decelle-Seoane 2024 SVD-cascade framework is the
master mechanism. v206 saddle-cascade + v211 1-RSB hysteresis + v212 MoE SHIFT are all projections
of one cascade of phase transitions in the singular spectrum of trained W.

FALSIFIER: The top-K detached singular values of trained W (excess above Marchenko-Pastur bulk edge)
should be equally spaced IF the unified framework holds. The equal-spacing in the plateau dimension
(spacing_error=0.0035 confirmed at v206/4corpus run) should be MATCHED by equal-spacing in the
singular-gap dimension.

DESIGN:
  For each substrate variant (saddle-cascade / 1rsb-hysteresis / moe-shift):
    1. Re-train W at N=256 (fast CPU) using the actual delta-rule training mechanism on real corpus.
    2. Compute SVD. Extract singular values.
    3. Apply Marchenko-Pastur bulk edge: bulk_top = 2 * sqrt(N) * std(W_elements).
       This is the correct MP upper edge for an N x N random matrix (MP predicts
       sigma_max = 2 * sqrt(N) * sigma_element for square matrix with iid elements).
    4. Identify K_detached = count of sigmas above bulk_top * 1.05.
    5. Compute gaps between consecutive detached excess values.
    6. Compute spacing_error = CoV(gaps).

  Substrate variants tested:
    W1: Delta-rule W trained on a SINGLE corpus phase (M_bytes = 8000) -- 1RSB regime
    W2: Delta-rule W trained on SAME corpus continued from W1 (more data) -- over-capacity
    W3: Delta-rule W trained on 4 SEQUENTIAL corpus phases (4-phase cascade)
    W4: Delta-rule W started fresh on corpus phase 2 (different distribution)
    W5: Delta-rule W trained on corpus phase 3 (yet another distribution)
  5 W instances. Verdict requires >= 3 of 5 in HARD_PASS band.

  NOTE on equal-spacing: The handoff predicts that IF the UNIFIED framework holds,
  the gaps between consecutive EXCESS singular values (above bulk) should be equal.
  This tests whether the SVD cascade produces a regular spectral ladder, matching
  the equal-spacing observed in the plateau dimension.

PRE-REGISTERED BANDS (from handoff, slightly adapted for empirical bulk edge):
  HARD-PASS (UNIFIED confirmed): spacing_error < 0.05 on >= 3 of 5 W instances
    AND K_detached >= 4 on those instances AND mean spacing_error < 0.07.
  HARD-FAIL (UNIFIED rejected): spacing_error > 0.15 on >= 3 of 5 instances
    OR K_detached < 4 on >= 3 of 5 instances.
  MIDDLE BAND: spacing_error in [0.05, 0.15] across most instances
    OR K_detached oscillates between 3 and 4.
  INSTRUMENTATION-FAIL: self-test fails OR all K_detached < 2 everywhere.

SELF-TEST (mandatory per handoff):
  Feed synthetic W = U @ diag([be+4d, be+3d, be+2d, be+d, sub-bulk...]) @ V.T
  Verify K_detached=4, spacing_error~0, band='HARD_PASS'.
  Also test: identity (K_detached=0, INSTRUMENTATION_FAIL).
  Also test: unequal detached (spacing_error > 0.15, HARD_FAIL/MIDDLE).

Queue: remote_cpu_queue (delta-rule training on text corpus, N=256, ~5-10 min per W instance)
ETA: ~30-60 min on remote CPU (5 instances x ~5min each)
Pre-reg: preregs/2026-05-26_wave14_unified_svd_cascade_falsifier_v1.md
Handoff: notes/exp_dev_handoff_unified_svd_cascade_falsifier_2026-05-26.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

N = 256            # vector dimensionality (fast CPU; enough to show structure)
SEEDS = [7, 17]   # seeds for byte_atoms / pos_atoms (not corpus randomness)
N_EPOCHS = 5       # delta-rule training epochs per phase
BATCH = 16         # minibatch size for delta-rule training

# Delta-rule hyperparameters (matches exp_wave14_1rsb_hysteresis_v3)
BETA = 8.0
DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4
RELU_B = 0.5

# Corpus slice sizes (bytes) per W instance
M_SINGLE = 8000        # W1: single-phase, moderate M
M_LARGE = 24000        # W2: large M, over-capacity
M_PHASE = 4000         # bytes per phase for 4-phase cascade (W3)
N_PHASES = 4           # W3: 4 sequential phases (matches 4-corpus setup)

# SVD analysis parameters
MP_MARGIN = 1.05   # detached = sigma > bulk_top * MP_MARGIN
MIN_DETACHED = 2   # minimum K_detached to avoid INSTRUMENTATION_FAIL


def get_output_dir() -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir("wave14_unified_svd_cascade_falsifier_v1")
    out.mkdir(parents=True, exist_ok=True)
    return out


# ---------------------------------------------------------------------------
# Load substrate modules (delta-rule training uses betB chain)
# ---------------------------------------------------------------------------

def _load_substrate_modules():
    """Load betB 4stage continual module chain for delta-rule training."""
    betB_path = REPO / "experiments" / "exp_wave14_betB_4stage_continual_v1.py"
    betB_spec = importlib.util.spec_from_file_location("betB", betB_path)
    betB_mod = importlib.util.module_from_spec(betB_spec)
    betB_spec.loader.exec_module(betB_mod)
    return betB_mod.base, betB_mod.pa   # base = kovacs, pa = cl_phase_a


# Load at module level (needed for self-tests)
_base, _pa = _load_substrate_modules()


# ---------------------------------------------------------------------------
# SVD helper -- the core testable contract from the handoff
# ---------------------------------------------------------------------------

def compute_svd_cascade_equal_spacing(W: np.ndarray, N_dim: int,
                                       bulk_edge_override: float = None) -> Dict:
    """Return SVD cascade equal-spacing analysis for a W matrix.

    Args:
        W: (N, N) float32 numpy array -- trained weight matrix.
        N_dim: vector dimensionality (= W.shape[0]).
        bulk_edge_override: if provided, use this as bulk_top instead of empirical estimate.

    Marchenko-Pastur bulk top: for an N x N random matrix with iid elements of std sigma_e,
    the largest singular value concentrates at 2 * sqrt(N) * sigma_e (Tracy-Widom edge).
    We use this empirical estimate since the W matrices are NOT iid but the bulk is
    approximately random after subtracting the structured signal.

    Returns dict with:
        sigmas: full singular spectrum, descending.
        bulk_top: estimated MP bulk edge (Tracy-Widom top).
        K_detached: count of sigmas above bulk_top * MP_MARGIN.
        excess_sigmas: top-K detached - bulk_top.
        gaps: consecutive diffs of excess_sigmas (positive for descending).
        spacing_error: CoV(gaps) = std(gaps) / mean(gaps).
        hard_pass: spacing_error < 0.05 AND K_detached >= 4.
        hard_fail: spacing_error > 0.15 OR K_detached < 2.
        band: 'HARD_PASS' | 'HARD_FAIL' | 'MIDDLE' | 'INSTRUMENTATION_FAIL'.
    """
    try:
        U, s, Vt = np.linalg.svd(W, full_matrices=False)
    except np.linalg.LinAlgError as e:
        return {
            "sigmas": [], "bulk_top": float("nan"), "K_detached": 0,
            "excess_sigmas": [], "gaps": [], "spacing_error": float("nan"),
            "hard_pass": False, "hard_fail": True, "band": "INSTRUMENTATION_FAIL",
            "error": str(e),
        }

    sigmas = s.tolist()

    if bulk_edge_override is not None:
        bulk_top = bulk_edge_override
    else:
        # Empirical MP bulk top: 2 * sqrt(N) * element_std
        sigma_e = float(np.std(W))
        bulk_top = 2.0 * math.sqrt(N_dim) * sigma_e

    threshold = bulk_top * MP_MARGIN
    detached = [sig for sig in sigmas if sig > threshold]
    K_detached = len(detached)

    if K_detached < MIN_DETACHED:
        return {
            "sigmas": sigmas,
            "bulk_top": round(bulk_top, 6),
            "K_detached": K_detached,
            "excess_sigmas": [],
            "gaps": [],
            "spacing_error": float("nan"),
            "hard_pass": False,
            "hard_fail": True,
            "band": "INSTRUMENTATION_FAIL",
            "note": f"K_detached={K_detached} < {MIN_DETACHED}",
        }

    excess = [sig - bulk_top for sig in detached]

    gaps = [excess[i] - excess[i+1] for i in range(len(excess) - 1)]

    if len(gaps) == 0:
        return {
            "sigmas": sigmas, "bulk_top": bulk_top, "K_detached": K_detached,
            "excess_sigmas": excess, "gaps": [], "spacing_error": float("nan"),
            "hard_pass": False, "hard_fail": True, "band": "INSTRUMENTATION_FAIL",
            "note": "only 1 detached mode; cannot compute gaps",
        }

    mean_gap = float(np.mean(gaps))
    std_gap = float(np.std(gaps, ddof=0))

    if abs(mean_gap) < 1e-12:
        spacing_error = float("nan")
        band = "INSTRUMENTATION_FAIL"
        hard_pass = False
        hard_fail = True
    else:
        spacing_error = std_gap / abs(mean_gap)
        hard_pass = (spacing_error < 0.05) and (K_detached >= 4)
        hard_fail = (spacing_error > 0.15) or (K_detached < 2)
        if hard_pass:
            band = "HARD_PASS"
        elif hard_fail:
            band = "HARD_FAIL"
        else:
            band = "MIDDLE"

    return {
        "sigmas": sigmas,
        "bulk_top": round(bulk_top, 6),
        "K_detached": K_detached,
        "excess_sigmas": [round(e, 6) for e in excess],
        "gaps": [round(g, 6) for g in gaps],
        "spacing_error": round(spacing_error, 6) if math.isfinite(spacing_error) else float("nan"),
        "hard_pass": hard_pass,
        "hard_fail": hard_fail,
        "band": band,
    }


# ---------------------------------------------------------------------------
# Delta-rule training helper
# ---------------------------------------------------------------------------

def train_delta_rule_W(data_bytes: bytes, N_dim: int, seed: int,
                        W_init: torch.Tensor = None) -> torch.Tensor:
    """Train delta-rule W on data_bytes corpus slice.

    Args:
        data_bytes: raw corpus bytes slice.
        N_dim: vector dimension.
        seed: for byte_atoms / pos_atoms initialization.
        W_init: starting W (zeros if None).

    Returns trained W (N x N float32 tensor).
    """
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = _pa.make_bsc_atoms(_base.VOCAB, N_dim, gen)
    pos_atoms = _pa.make_bsc_atoms(_base.K, N_dim, gen)

    idx, tgt = _base.bytes_to_idx_tensors(data_bytes, "cpu")
    if idx.shape[0] == 0:
        return torch.zeros((N_dim, N_dim), dtype=torch.float32) if W_init is None else W_init.clone()
    split = int(0.8 * idx.shape[0])
    train_idx, train_tgt = idx[:split], tgt[:split]

    W = (torch.zeros((N_dim, N_dim), dtype=torch.float32)
         if W_init is None else W_init.clone())

    T = train_idx.shape[0]
    for _epoch in range(N_EPOCHS):
        for bs in range(0, T, BATCH):
            be = min(bs + BATCH, T)
            ctxs = _pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, train_idx[bs:be])
            with torch.no_grad():
                q = ctxs @ W.T
                q_relu = torch.clamp(q - RELU_B, min=0.0)
                sims = (byte_atoms @ q_relu.T) / N_dim
                P = torch.softmax(BETA * sims, dim=0)
                tgt_atoms = byte_atoms[train_tgt[bs:be]]
                predicted = (P.T @ byte_atoms)
                residual = tgt_atoms - predicted
                dW = (residual.T @ ctxs) / N_dim
                W.mul_(1.0 - DELTA_DECAY)
                W.add_(dW, alpha=DELTA_ALPHA)
    return W


# ---------------------------------------------------------------------------
# Instrumentation self-test (MANDATORY)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Verify SVD helper against synthetic known cases."""
    print("[selftest] running SVD instrumentation self-test...", flush=True)

    N_test = 64
    # Construct a synthetic bulk_top for the test
    bulk_top_test = 10.0  # arbitrary; we override in the helper
    delta = 1.5           # gap between consecutive detached values

    rng = np.random.RandomState(42)
    U, _ = np.linalg.qr(rng.randn(N_test, N_test))
    V, _ = np.linalg.qr(rng.randn(N_test, N_test))

    # Case 1: 4 equally-spaced detached values above threshold
    detached_sigmas = [bulk_top_test * 1.05 + 4*delta,
                       bulk_top_test * 1.05 + 3*delta,
                       bulk_top_test * 1.05 + 2*delta,
                       bulk_top_test * 1.05 + 1*delta]
    bulk_sigmas = [bulk_top_test * 0.5] * (N_test - 4)
    W_synth = (U @ np.diag(detached_sigmas + bulk_sigmas) @ V.T).astype(np.float32)
    result = compute_svd_cascade_equal_spacing(W_synth, N_test,
                                               bulk_edge_override=bulk_top_test)
    assert result["K_detached"] == 4, \
        f"selftest FAIL: expected K_detached=4, got {result['K_detached']}"
    assert result["band"] == "HARD_PASS", \
        f"selftest FAIL: expected HARD_PASS, got {result['band']}, spacing_error={result['spacing_error']}"
    assert result["spacing_error"] < 0.01, \
        f"selftest FAIL: expected spacing_error~0, got {result['spacing_error']}"
    print(f"  Case 1 (equally-spaced 4-detached): K_detached={result['K_detached']}, "
          f"spacing_error={result['spacing_error']:.6f}, band={result['band']} [PASS]", flush=True)

    # Case 2: identity matrix -- singular values = 1, all below any reasonable bulk_top > 1
    W_identity = np.eye(N_test, dtype=np.float32)
    result2 = compute_svd_cascade_equal_spacing(W_identity, N_test,
                                                 bulk_edge_override=bulk_top_test)
    assert result2["K_detached"] == 0, \
        f"selftest FAIL: identity W: expected K_detached=0, got {result2['K_detached']}"
    assert result2["band"] == "INSTRUMENTATION_FAIL", \
        f"selftest FAIL: identity W: expected INSTRUMENTATION_FAIL, got {result2['band']}"
    print(f"  Case 2 (identity matrix, bulk_top={bulk_top_test}): "
          f"K_detached=0, band={result2['band']} [PASS]", flush=True)

    # Case 3: unequally-spaced detached values -> HARD_FAIL
    # 4 modes all above threshold but gaps are [0.5d, 0.5d, 2d] -> CoV > 0.15
    threshold = bulk_top_test * MP_MARGIN
    unequal_sigmas = [threshold + 4.0*delta,
                      threshold + 3.5*delta,
                      threshold + 3.0*delta,
                      threshold + 1.0*delta]  # big gap at the end
    W_unequal = (U @ np.diag(unequal_sigmas + bulk_sigmas) @ V.T).astype(np.float32)
    result3 = compute_svd_cascade_equal_spacing(W_unequal, N_test,
                                                 bulk_edge_override=bulk_top_test)
    assert result3["K_detached"] == 4, \
        f"selftest FAIL: unequal W: expected K_detached=4, got {result3['K_detached']}"
    assert result3["spacing_error"] > 0.15, \
        f"selftest FAIL: unequal W: expected spacing_error > 0.15, got {result3['spacing_error']}"
    assert result3["band"] in ("HARD_FAIL", "MIDDLE"), \
        f"selftest FAIL: unequal W: expected HARD_FAIL or MIDDLE, got {result3['band']}"
    print(f"  Case 3 (unequal detached): K_detached={result3['K_detached']}, "
          f"spacing_error={result3['spacing_error']:.4f}, band={result3['band']} [PASS]", flush=True)

    # Case 4: empirical test -- tiny delta-rule W should have K_detached >= 1
    # (sanity check that the training mechanism produces ANY detached modes)
    corpus = _pa.load_corpus_a()
    W_tiny = train_delta_rule_W(corpus[:2000], 64, seed=7)
    W_tiny_np = W_tiny.numpy()
    result4 = compute_svd_cascade_equal_spacing(W_tiny_np, 64)  # uses empirical bulk edge
    print(f"  Case 4 (tiny delta-rule W, N=64): K_detached={result4['K_detached']}, "
          f"bulk_top={result4['bulk_top']:.3f}, band={result4['band']}", flush=True)
    assert result4["K_detached"] >= 1, \
        f"selftest FAIL: tiny delta-rule W should have >= 1 detached mode, got {result4['K_detached']}"

    print("[selftest] ALL SVD instrumentation self-tests PASSED", flush=True)


# Run self-test at import time
_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Aggregate verdict
# ---------------------------------------------------------------------------

def compute_aggregate_verdict(instances: List[Dict]) -> Tuple[str, str]:
    """Aggregate verdict from per-W-instance results (pre-registered bands)."""
    n = len(instances)
    n_hard_pass = sum(1 for r in instances if r["band"] == "HARD_PASS")
    n_hard_fail_spacing = sum(1 for r in instances
                               if math.isfinite(r.get("spacing_error", float("nan")))
                               and r["spacing_error"] > 0.15)
    n_low_K = sum(1 for r in instances if r["K_detached"] < 4)
    n_instrumentation_fail = sum(1 for r in instances if r["band"] == "INSTRUMENTATION_FAIL")

    valid_se = [r["spacing_error"] for r in instances
                if math.isfinite(r.get("spacing_error", float("nan")))]
    mean_se = float(np.mean(valid_se)) if valid_se else float("nan")

    if n_instrumentation_fail == n:
        return ("INSTRUMENTATION_FAIL",
                f"All {n} W instances failed (K_detached < 2). "
                f"SVD cascade structure absent at N={N}; needs larger N or more training.")

    if n_hard_pass >= 3 and math.isfinite(mean_se) and mean_se < 0.07:
        return ("UNIFIED_HARD_PASS",
                f"UNIFIED FRAMEWORK CONFIRMED: {n_hard_pass}/{n} W instances HARD_PASS "
                f"(spacing_error < 0.05, K_detached >= 4). Mean spacing_error={mean_se:.4f}. "
                f"Equal-spaced singular ladder matches v206 plateau spacing_error=0.0035. "
                f"UNIFIED (Bachtis-Biroli-Decelle-Seoane 2024) gains strong support.")

    if n_hard_fail_spacing >= 3 or n_low_K >= 3:
        reasons = []
        if n_hard_fail_spacing >= 3:
            reasons.append(f"spacing_error > 0.15 on {n_hard_fail_spacing}/{n} instances")
        if n_low_K >= 3:
            reasons.append(f"K_detached < 4 on {n_low_K}/{n} instances")
        return ("UNIFIED_HARD_FAIL",
                f"UNIFIED FRAMEWORK REJECTED: {'; '.join(reasons)}. "
                f"Mean spacing_error={mean_se:.4f}. "
                f"Three frameworks are likely INDEPENDENT observations, not projections of one cascade. "
                f"Rehab: probe at larger N=1024, or test cross-prediction (1) and (3) per handoff.")

    return ("UNIFIED_MIDDLE_BAND",
            f"INCONCLUSIVE: {n_hard_pass}/{n} HARD_PASS, {n_hard_fail_spacing}/{n} spacing-fail, "
            f"{n_low_K}/{n} low-K. Mean spacing_error={mean_se:.4f}. "
            f"Middle instances: {[r['name'] for r in instances if r['band'] == 'MIDDLE']}. "
            f"Recommend N=1024 re-run for resolution.")


# ---------------------------------------------------------------------------
# Verdict formula self-tests
# ---------------------------------------------------------------------------

def _verdict_selftest() -> None:
    """Self-test verdict formula with known inputs."""
    all_pass = [{"band": "HARD_PASS", "K_detached": 4, "spacing_error": 0.03, "name": f"w{i}"}
                for i in range(5)]
    v, _ = compute_aggregate_verdict(all_pass)
    assert v == "UNIFIED_HARD_PASS", f"verdict selftest FAIL: expected UNIFIED_HARD_PASS, got {v}"

    mixed_fail = (
        [{"band": "HARD_FAIL", "K_detached": 4, "spacing_error": 0.20, "name": f"wf{i}"} for i in range(3)] +
        [{"band": "MIDDLE", "K_detached": 4, "spacing_error": 0.10, "name": f"wm{i}"} for i in range(2)]
    )
    v2, _ = compute_aggregate_verdict(mixed_fail)
    assert v2 == "UNIFIED_HARD_FAIL", f"verdict selftest FAIL: expected UNIFIED_HARD_FAIL, got {v2}"

    mixed_mid = (
        [{"band": "HARD_PASS", "K_detached": 4, "spacing_error": 0.03, "name": f"wp{i}"} for i in range(2)] +
        [{"band": "MIDDLE", "K_detached": 4, "spacing_error": 0.10, "name": f"wm{i}"} for i in range(2)] +
        [{"band": "HARD_FAIL", "K_detached": 4, "spacing_error": 0.20, "name": "wf0"}]
    )
    v3, _ = compute_aggregate_verdict(mixed_mid)
    assert v3 == "UNIFIED_MIDDLE_BAND", f"verdict selftest FAIL: expected UNIFIED_MIDDLE_BAND, got {v3}"

    print("[selftest] verdict formula self-tests PASSED", flush=True)


_verdict_selftest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(smoke: bool = False) -> Dict:
    t0 = time.monotonic()
    seed = SEEDS[0]  # single seed for speed; both seeds similar structure
    print(f"[unified_svd_falsifier_v1] N={N} seed={seed} smoke={smoke}", flush=True)

    corpus = _pa.load_corpus_a()
    out_dir = get_output_dir()
    instances = []

    # --- W1: single-phase, moderate M (1-RSB hysteresis regime) ---
    print("\n[W1_1rsb_regime] Training delta-rule W, single corpus, M=8000...", flush=True)
    t_inst = time.monotonic()
    W1 = train_delta_rule_W(corpus[:M_SINGLE], N, seed)
    W1_np = W1.numpy()
    r1 = compute_svd_cascade_equal_spacing(W1_np, N)
    r1["name"] = "W1_1rsb_regime"
    r1["source"] = f"delta-rule, single corpus phase, M={M_SINGLE} bytes"
    print(f"  W1: K_detached={r1['K_detached']}, spacing_error={r1.get('spacing_error','nan')}, "
          f"band={r1['band']}, bulk_top={r1['bulk_top']:.3f}", flush=True)
    print(f"  elapsed: {time.monotonic()-t_inst:.1f}s", flush=True)
    instances.append(r1)

    # --- W2: over-capacity (large M) ---
    print("\n[W2_over_capacity] Training delta-rule W, large M=24000...", flush=True)
    t_inst = time.monotonic()
    W2 = train_delta_rule_W(corpus[:M_LARGE], N, seed)
    W2_np = W2.numpy()
    r2 = compute_svd_cascade_equal_spacing(W2_np, N)
    r2["name"] = "W2_over_capacity"
    r2["source"] = f"delta-rule, single corpus, large M={M_LARGE} bytes"
    print(f"  W2: K_detached={r2['K_detached']}, spacing_error={r2.get('spacing_error','nan')}, "
          f"band={r2['band']}, bulk_top={r2['bulk_top']:.3f}", flush=True)
    print(f"  elapsed: {time.monotonic()-t_inst:.1f}s", flush=True)
    instances.append(r2)

    # --- W3: 4-phase cascade (matching 4-corpus equal-spacing setup) ---
    print("\n[W3_4phase_cascade] Training delta-rule W, 4 sequential phases...", flush=True)
    t_inst = time.monotonic()
    W_accum = None
    for phase in range(N_PHASES):
        data_slice = corpus[phase * M_PHASE: (phase + 1) * M_PHASE]
        W_accum_t = train_delta_rule_W(data_slice, N, seed,
                                        W_init=(torch.from_numpy(W_accum) if W_accum is not None else None))
        W_accum = W_accum_t.numpy()
    r3 = compute_svd_cascade_equal_spacing(W_accum, N)
    r3["name"] = "W3_4phase_cascade"
    r3["source"] = f"delta-rule, 4 sequential corpus phases ({N_PHASES}x{M_PHASE} bytes each)"
    print(f"  W3: K_detached={r3['K_detached']}, spacing_error={r3.get('spacing_error','nan')}, "
          f"band={r3['band']}, bulk_top={r3['bulk_top']:.3f}", flush=True)
    print(f"  elapsed: {time.monotonic()-t_inst:.1f}s", flush=True)
    instances.append(r3)

    # --- W4: different corpus offset (phase 2 only, fresh W) ---
    print("\n[W4_corpus_phase2] Training delta-rule W, corpus phase 2 only...", flush=True)
    t_inst = time.monotonic()
    W4 = train_delta_rule_W(corpus[M_PHASE: 2*M_PHASE], N, seed)
    W4_np = W4.numpy()
    r4 = compute_svd_cascade_equal_spacing(W4_np, N)
    r4["name"] = "W4_corpus_phase2"
    r4["source"] = f"delta-rule, corpus phase 2, M={M_PHASE} bytes, fresh W"
    print(f"  W4: K_detached={r4['K_detached']}, spacing_error={r4.get('spacing_error','nan')}, "
          f"band={r4['band']}, bulk_top={r4['bulk_top']:.3f}", flush=True)
    print(f"  elapsed: {time.monotonic()-t_inst:.1f}s", flush=True)
    instances.append(r4)

    # --- W5: different corpus offset (phase 3+4, fresh W) ---
    print("\n[W5_corpus_phase34] Training delta-rule W, corpus phases 3-4 only...", flush=True)
    t_inst = time.monotonic()
    W5 = train_delta_rule_W(corpus[2*M_PHASE: 4*M_PHASE], N, seed)
    W5_np = W5.numpy()
    r5 = compute_svd_cascade_equal_spacing(W5_np, N)
    r5["name"] = "W5_corpus_phase34"
    r5["source"] = f"delta-rule, corpus phases 3+4, M={2*M_PHASE} bytes, fresh W"
    print(f"  W5: K_detached={r5['K_detached']}, spacing_error={r5.get('spacing_error','nan')}, "
          f"band={r5['band']}, bulk_top={r5['bulk_top']:.3f}", flush=True)
    print(f"  elapsed: {time.monotonic()-t_inst:.1f}s", flush=True)
    instances.append(r5)

    # --- Aggregate ---
    verdict, verdict_msg = compute_aggregate_verdict(instances)

    # Reference: v206 plateau spacing_error for cross-comparison
    plateau_gaps = [0.0957, 0.1113, 0.1002]
    plateau_spacing_error = float(np.std(plateau_gaps) / np.mean(plateau_gaps))
    valid_svd_errors = [r["spacing_error"] for r in instances
                        if math.isfinite(r.get("spacing_error", float("nan")))]
    mean_svd_error = float(np.mean(valid_svd_errors)) if valid_svd_errors else float("nan")
    cross_match = (abs(mean_svd_error - plateau_spacing_error) < 0.10
                   if math.isfinite(mean_svd_error) else False)

    print(f"\n[summary] Verdict: {verdict}", flush=True)
    print(f"[summary] n_hard_pass={sum(1 for r in instances if r['band']=='HARD_PASS')} / {len(instances)}", flush=True)
    print(f"[summary] mean_svd_spacing_error={mean_svd_error:.4f}", flush=True)
    print(f"[summary] plateau_spacing_error_ref={plateau_spacing_error:.4f}", flush=True)
    print(f"[summary] cross_match={cross_match}", flush=True)

    elapsed = time.monotonic() - t0
    summary = {
        "instances": instances,
        "n_instances": len(instances),
        "n_hard_pass": sum(1 for r in instances if r["band"] == "HARD_PASS"),
        "n_hard_fail": sum(1 for r in instances if r["band"] == "HARD_FAIL"),
        "n_middle": sum(1 for r in instances if r["band"] == "MIDDLE"),
        "n_instrumentation_fail": sum(1 for r in instances if r["band"] == "INSTRUMENTATION_FAIL"),
        "mean_svd_spacing_error": round(mean_svd_error, 6) if math.isfinite(mean_svd_error) else None,
        "plateau_spacing_error_ref": round(plateau_spacing_error, 6),
        "cross_prediction_match": cross_match,
        "plateau_gaps_ref": plateau_gaps,
    }

    result = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": summary,
        "config": {
            "N": N,
            "seed": seed,
            "smoke": smoke,
            "M_single": M_SINGLE,
            "M_large": M_LARGE,
            "M_phase": M_PHASE,
            "N_phases": N_PHASES,
            "n_epochs": N_EPOCHS,
            "mp_margin": MP_MARGIN,
            "handoff": "notes/exp_dev_handoff_unified_svd_cascade_falsifier_2026-05-26.md",
        },
    }

    metrics_path = out_dir / "metrics.json"
    tmp_path = str(metrics_path) + ".tmp"
    with open(tmp_path, "w") as fh:
        json.dump(result, fh, indent=2)
    import shutil
    shutil.move(tmp_path, str(metrics_path))

    print(f"\n[done] verdict={verdict}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s metrics={metrics_path}", flush=True)
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print("[self-test] all self-tests passed at import", flush=True)
        return
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
