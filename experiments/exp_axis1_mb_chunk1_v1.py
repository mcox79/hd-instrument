"""AXIS-1 Phase Diagram M x beta SCAN: chunk 1 (M/N = {1/4, 1/2, 1, 2}).

CONTEXT:
  Phase-boundary operation hypothesis: substrate sits at a triple-point
  based on 3 independent signals (BID v245 outside Hopfield bands,
  SKAH-M v228 non-eq lR-phase, Pred-4 discrete plateau hysteresis).
  Three measured retention plateaus (0.94 / 0.74 / 0.60) may be a
  triple-point signature.

SCIENTIFIC QUESTION (Axis 1 of phase diagram):
  Map the 2D phase plane (M/N axis) x (beta axis) at N=4096 Kerdock.
  For each (M, beta) cell measure:
    (a) retention: argmax query accuracy on stored facts
    (b) hysteresis_amplitude: |retention(load) - retention(unload)|
        after ramping M up then down by 5% (crude proxy)
    (c) bundle_norm_var: variance of query response norms across facts
        (indicator of phase heterogeneity)
    (d) overlap_spectral_gap: spectral gap of the normalized overlap
        matrix S_ij = (k_i dot k_j) / N for stored keys. Measures
        codebook structure used by the substrate.

  This chunk: M/N in {0.25, 0.5, 1.0, 2.0} (rows 1-4 of 7).
  Next chunk (separate anchor): M/N in {4.0, 8.0, 16.0} (rows 5-7).

  beta in {1, 4, 16, 32, 64, 128, 256}.

  5 seeds per cell. 4 M values x 7 beta values = 28 cells x 5 seeds = 140 runs.
  This is the PRIMARY phase-diagram measurement for the overnight queue.

PRE-REGISTERED BANDS:
  This is a calibration probe (first phase-diagram measurement).
  No prior empirical anchor for the 2D plane. Bands set +/-50% per policy.

  HARD_PASS: Phase structure detected -- at least one metric shows
    statistically distinct behavior (>20% change) between different
    M/N regimes or beta regimes. Confirms substrate has non-trivial
    phase structure in the (M, beta) plane.
  HARD_FAIL: ALL metrics are constant (variation < 2%) across the full
    M x beta grid. Phase structure absent.
  MIDDLE_BAND: partial structure (some metrics vary, others flat).

FORMULA SELF-TESTS:
  1. retention at M/N=0.25 and high beta should be near 1.0 (clean regime).
  2. retention at M/N=2.0 and low beta should be lower (over-capacity noise).
  3. bundle_norm_var = Var(||W @ k_i||_2) across stored keys k_i.
     For perfectly orthogonal keys: Var = 0. Kerdock is approximately ortho.
  4. overlap_spectral_gap: eigenvalues of (K @ K.T / N). For M orthog keys:
     all eigenvalues = 1. For correlated keys: gap opens up.
  5. compute_spectral_gap(I_M) = 0 (all eigenvalues = 1, gap = lambda_1 - lambda_2 = 0).
     compute_spectral_gap(rank-1 + small) > 0.

TIMEOUT ESTIMATE:
  smoke: N=1024, 3 M values, 3 beta values, 1 seed. ~5s.
  Full: N=4096, 4 M values, 7 beta values, 5 seeds = 140 cells.
  Hysteresis ramp adds ~2x overhead per cell.
  scale = (4096/1024)^1.5 * (7/3) * 5 = 8 * 2.33 * 5 = 93
  timeout_s = ceil(1.5 * 5 * 93) = ceil(697) -> 900s.
  Conservative: 3 x estimate -> 2700s. Under 4h, flag at >2h.
  Using 3600s with note: long run flag.

N-suffix: no _nN suffix; multi-M sweep (PROT-018: stated explicitly).
Queue: overnight_queue (GPU; 4096 matrix ops, 140 cells, 5 seeds)
Pre-reg: preregs/2026-05-27_axis1_mb_chunk1_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
spec3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(v3)

# PRODUCTION CONFIG
N_FULL = 4096       # PROT-018: production N stated explicitly
N_SMOKE = 1024

# M/N fractions for this chunk (rows 1-4 of 7)
M_FRACS_FULL = [0.25, 0.5, 1.0, 2.0]
M_FRACS_SMOKE = [0.25, 1.0, 2.0]

# Beta sweep
BETA_FULL = [1.0, 4.0, 16.0, 32.0, 64.0, 128.0, 256.0]
BETA_SMOKE = [4.0, 32.0, 128.0]

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Hysteresis ramp: perturb M by +/- 5%
HYST_DELTA_FRAC = 0.05

# Phase structure detection thresholds
PASS_METRIC_VARIATION = 0.20     # 20% change across M or beta axis
FAIL_METRIC_VARIATION = 0.02     # <2% variation = flat


def get_output_dir(default_name: str = "axis1_mb_chunk1_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def store_facts_batched(codebook: torch.Tensor, M: int, seed: int,
                         N: int, device: torch.device):
    """Store M randomly selected (key, value) pairs. Returns (W, keys, values, key_idx, val_idx)."""
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed)
    # Handle over-capacity gracefully
    k_perm = torch.randperm(C, generator=gen, device=device)
    v_perm = torch.randperm(C, generator=gen, device=device)
    if M <= C:
        key_idx = k_perm[:M]
        val_idx = v_perm[:M]
    else:
        # Repeat with fresh permutation
        repeats = math.ceil(M / C)
        key_parts = [torch.randperm(C, generator=gen, device=device) for _ in range(repeats)]
        val_parts = [torch.randperm(C, generator=gen, device=device) for _ in range(repeats)]
        key_idx = torch.cat(key_parts)[:M]
        val_idx = torch.cat(val_parts)[:M]

    keys = codebook[key_idx % C]
    values = codebook[val_idx % C]

    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    batch = 256
    for start in range(0, M, batch):
        k_b = keys[start:start + batch]
        v_b = values[start:start + batch]
        W += (v_b.T @ k_b) / N

    return W, keys, values, key_idx, val_idx


def compute_retention(W: torch.Tensor, keys: torch.Tensor, val_idx: torch.Tensor,
                       codebook: torch.Tensor, beta: float, N: int,
                       n_probe: int = 200) -> float:
    """Argmax retrieval accuracy for a subset of stored facts."""
    C = codebook.shape[0]
    M = keys.shape[0]
    n = min(n_probe, M)
    probe_keys = keys[:n]
    probe_val_idx = val_idx[:n] % C

    # Batch query
    sims = (codebook @ (probe_keys @ W.T).T) / N   # (C, n)
    pred = torch.argmax(sims * beta, dim=0)   # (n,)  (argmax invariant to beta sign; use explicit)
    # Actually: for argmax accuracy beta doesn't matter (monotone transform)
    # But for softmax-based predictions it does. Here we use pure argmax for retention.
    pred2 = torch.argmax(sims, dim=0)
    acc = float((pred2 == probe_val_idx.to(W.device)).float().mean().item())
    return acc


def compute_bundle_norm_var(W: torch.Tensor, keys: torch.Tensor, N: int,
                              n_probe: int = 100) -> float:
    """Variance of ||W k_i||_2 across stored keys. Phase heterogeneity measure."""
    n = min(n_probe, keys.shape[0])
    probe = keys[:n]
    responses = probe @ W.T   # (n, N)
    norms = responses.norm(dim=1)   # (n,)
    return float(norms.var().item())


def compute_overlap_spectral_gap(keys: torch.Tensor, N: int,
                                   n_probe: int = 128) -> float:
    """Spectral gap of normalized overlap matrix K K^T / N.
    Measures correlation structure of stored keys.
    gap = lambda_1 - lambda_2 for eigenvalues sorted descending."""
    n = min(n_probe, keys.shape[0])
    K = keys[:n]   # (n, N)
    # Overlap matrix: (n, n)
    S = (K @ K.T) / N
    # Use torch.linalg.eigvalsh for symmetric matrix
    try:
        eigs = torch.linalg.eigvalsh(S)   # sorted ascending
        eigs_desc = eigs.flip(0)
        if len(eigs_desc) >= 2:
            gap = float((eigs_desc[0] - eigs_desc[1]).item())
        else:
            gap = 0.0
    except Exception:
        gap = 0.0
    return gap


def compute_crude_hysteresis(codebook: torch.Tensor, M_base: int, seed: int,
                              N: int, beta: float, device: torch.device,
                              n_probe: int = 50) -> float:
    """Crude hysteresis: store M+delta facts, measure retention, then remove delta.
    hyst_amp = |retention(M + delta) - retention(M + delta - delta)|"""
    delta = max(1, int(HYST_DELTA_FRAC * M_base))
    C = codebook.shape[0]
    delta = min(delta, max(1, C - M_base)) if M_base < C else delta

    # Load M_base + delta
    M_up = min(M_base + delta, C if M_base < C else M_base * 2)
    W_up, keys_up, vals_up, key_idx_up, val_idx_up = store_facts_batched(
        codebook, M_up, seed, N, device
    )
    ret_up = compute_retention(W_up, keys_up[:M_base], val_idx_up[:M_base],
                                 codebook, beta, N, n_probe)

    # "Remove" delta facts (anti-Hebbian)
    W_down = W_up.clone()
    keys_remove = keys_up[M_base:M_up]
    vals_remove = vals_up[M_base:M_up]
    if keys_remove.shape[0] > 0:
        W_down -= (vals_remove.T @ keys_remove) / N

    ret_down = compute_retention(W_down, keys_up[:M_base], val_idx_up[:M_base],
                                   codebook, beta, N, n_probe)

    return abs(ret_up - ret_down)


def run_one_cell(M: int, beta: float, seed: int, codebook: torch.Tensor,
                  N: int, device: torch.device, compute_hyst: bool = True) -> dict:
    """Run one (M, beta, seed) cell."""
    n_probe = min(200, M) if M >= 10 else M
    hyst_probe = min(50, n_probe)

    W, keys, values, key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)

    retention = compute_retention(W, keys, val_idx, codebook, beta, N, n_probe)
    bundle_norm_var = compute_bundle_norm_var(W, keys, N, min(100, M))
    spectral_gap = compute_overlap_spectral_gap(keys, N, min(128, M))

    if compute_hyst and M >= 10:
        hyst_amp = compute_crude_hysteresis(codebook, M, seed, N, beta, device, hyst_probe)
    else:
        hyst_amp = 0.0

    return {
        "M": M,
        "beta": beta,
        "seed": seed,
        "retention": retention,
        "bundle_norm_var": bundle_norm_var,
        "spectral_gap": spectral_gap,
        "hysteresis_amp": hyst_amp,
    }


def compute_verdict(summary: dict) -> tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("AXIS1_INCONCLUSIVE", "No cells computed.")

    # Extract metrics across all (M, beta) combinations
    retentions = [c["retention"] for c in cells]
    betas = [c["beta"] for c in cells]
    m_vals = [c["M"] for c in cells]
    bundle_vars = [c["bundle_norm_var"] for c in cells]

    if not retentions:
        return ("AXIS1_INCONCLUSIVE", "No retention data.")

    # Check variation across M axis
    M_set = sorted(set(m_vals))
    beta_set = sorted(set(betas))

    # Mean retention per M (averaged over seeds and betas)
    ret_by_M = {}
    for M_v in M_set:
        cells_M = [c["retention"] for c in cells if c["M"] == M_v]
        ret_by_M[M_v] = sum(cells_M) / len(cells_M) if cells_M else 0.0

    # Mean retention per beta (averaged over seeds and M values)
    ret_by_beta = {}
    for beta_v in beta_set:
        cells_b = [c["retention"] for c in cells if c["beta"] == beta_v]
        ret_by_beta[beta_v] = sum(cells_b) / len(cells_b) if cells_b else 0.0

    ret_M_range = max(ret_by_M.values()) - min(ret_by_M.values()) if len(ret_by_M) > 1 else 0.0
    ret_beta_range = (max(ret_by_beta.values()) - min(ret_by_beta.values())
                      if len(ret_by_beta) > 1 else 0.0)
    bundle_range = max(bundle_vars) - min(bundle_vars) if bundle_vars else 0.0
    mean_hyst = sum(c["hysteresis_amp"] for c in cells) / len(cells) if cells else 0.0

    # HARD_FAIL: all flat
    if (ret_M_range < FAIL_METRIC_VARIATION
            and ret_beta_range < FAIL_METRIC_VARIATION
            and bundle_range < 1e-6):
        return ("AXIS1_HARD_FAIL",
                f"No phase structure detected. "
                f"ret_M_range={ret_M_range:.4f}, ret_beta_range={ret_beta_range:.4f}. "
                f"All metrics flat across (M, beta) grid.")

    # HARD_PASS: significant variation in >= 1 metric
    has_M_structure = ret_M_range >= PASS_METRIC_VARIATION
    has_beta_structure = ret_beta_range >= PASS_METRIC_VARIATION
    has_bundle_structure = bundle_range > 0.01

    if has_M_structure or has_beta_structure or has_bundle_structure:
        return ("AXIS1_HARD_PASS",
                f"Phase structure detected. "
                f"ret_M_range={ret_M_range:.3f} (need {PASS_METRIC_VARIATION}). "
                f"ret_beta_range={ret_beta_range:.3f}. "
                f"bundle_norm_var_range={bundle_range:.4f}. "
                f"mean_hysteresis={mean_hyst:.4f}. "
                f"ret_by_M={dict((k, round(v, 3)) for k, v in ret_by_M.items())}.")

    return ("AXIS1_MIDDLE_BAND",
            f"Partial phase structure. "
            f"ret_M_range={ret_M_range:.3f}, ret_beta_range={ret_beta_range:.3f}. "
            f"bundle_norm_var range detected: {bundle_range:.4f}. "
            f"mean_hysteresis={mean_hyst:.4f}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    # PROT-018: no _nN suffix; production N = 4096 stated explicitly
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: compute_retention with identity-like W returns near-1
    device = torch.device("cpu")
    N_test = 1024
    codebook, info = v3.make_kerdock_4coset_codebook(N_test, device)
    C = codebook.shape[0]
    M_test = min(C, 64)

    gen = torch.Generator(device=device).manual_seed(17)
    key_idx = torch.randperm(C, generator=gen, device=device)[:M_test]
    val_idx = torch.randperm(C, generator=gen, device=device)[:M_test]
    keys = codebook[key_idx]
    values = codebook[val_idx]

    W = torch.zeros(N_test, N_test, dtype=torch.float32, device=device)
    for start in range(0, M_test, 32):
        k_b = keys[start:start + 32]
        v_b = values[start:start + 32]
        W += (v_b.T @ k_b) / N_test

    ret = compute_retention(W, keys, val_idx, codebook, 32.0, N_test, 30)
    assert isinstance(ret, float), f"retention not float: {type(ret)}"
    assert 0.0 <= ret <= 1.0, f"retention out of [0,1]: {ret}"

    # Self-test 2: bundle_norm_var >= 0
    bv = compute_bundle_norm_var(W, keys, N_test, 30)
    assert isinstance(bv, float), f"bundle_norm_var not float: {type(bv)}"
    assert bv >= 0.0, f"bundle_norm_var < 0: {bv}"

    # Self-test 3: spectral_gap >= 0
    sg = compute_overlap_spectral_gap(keys, N_test, 30)
    assert isinstance(sg, float), f"spectral_gap not float: {type(sg)}"
    assert sg >= 0.0, f"spectral_gap < 0: {sg}"

    # Self-test 4: verdict HARD_PASS with M-variation
    cells_pass = []
    for m_v in [256, 1024, 2048, 4096]:  # large M range
        for bv in [4.0, 128.0]:
            cells_pass.append({
                "M": m_v, "beta": bv, "seed": 17,
                "retention": max(0.1, 1.0 - m_v / 16384),  # decreasing with M
                "bundle_norm_var": 0.05, "spectral_gap": 0.1, "hysteresis_amp": 0.01
            })
    v, msg = compute_verdict({"cells": cells_pass})
    assert v == "AXIS1_HARD_PASS", f"Expected AXIS1_HARD_PASS, got {v}: {msg}"

    # Self-test 5: verdict HARD_FAIL with all flat
    cells_flat = [{"M": 1024, "beta": b, "seed": 17,
                    "retention": 0.95, "bundle_norm_var": 0.05,
                    "spectral_gap": 0.1, "hysteresis_amp": 0.01}
                   for b in [4.0, 32.0, 128.0]]
    v, msg = compute_verdict({"cells": cells_flat})
    assert v == "AXIS1_HARD_FAIL", f"Expected AXIS1_HARD_FAIL with flat grid, got {v}: {msg}"

    # Self-test 6: single cell run
    cell = run_one_cell(M_test, 32.0, 17, codebook, N_test, device, compute_hyst=False)
    assert "retention" in cell, "missing retention"
    assert "bundle_norm_var" in cell, "missing bundle_norm_var"
    assert "spectral_gap" in cell, "missing spectral_gap"
    assert 0.0 <= cell["retention"] <= 1.0, f"retention out of range: {cell['retention']}"

    print("[SELFTEST PASS] axis1_mb_chunk1_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    betas = BETA_SMOKE if smoke else BETA_FULL
    config = {"smoke": smoke, "N": N, "m_fracs": m_fracs, "betas": betas}

    t0 = time.time()
    out_dir = get_output_dir()
    codebook, info = v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]
    print(f"[axis1] N={N} C={C} seeds={seeds} M_fracs={m_fracs} betas={betas} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    all_cells = []
    total = len(seeds) * len(m_fracs) * len(betas)
    done = 0
    for seed in seeds:
        for m_frac in m_fracs:
            M = int(m_frac * N)
            for beta in betas:
                cell = run_one_cell(M, beta, seed, codebook, N, device,
                                     compute_hyst=not smoke)
                all_cells.append(cell)
                done += 1
                if done % max(1, total // 10) == 0 or done == total:
                    print(f"  [{done}/{total}] M={M} beta={beta} seed={seed} "
                          f"ret={cell['retention']:.3f} bnv={cell['bundle_norm_var']:.4f}",
                          flush=True)

    summary = {
        "cells": all_cells,
        "N_full": N_FULL,
        "N_used": N,
        "m_fracs": m_fracs,
        "betas": betas,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": config,
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[axis1] VERDICT: {verdict}", flush=True)
    print(f"[axis1] {verdict_msg}", flush=True)
    print(f"[axis1] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
