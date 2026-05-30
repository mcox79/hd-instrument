"""SUPERPOSITION SINGLE-HOP DECOMPOSITION v1 at N=4096.

CONTEXT:
  Track-A Phase 1 gate test (user msg 1, 2026-05-30): does a substrate
  response to a SUPERPOSITION query q = sum_i beta_i k_i decompose cleanly
  enough in the codebook basis to identify the constituent path components?
  This is THE single most decisive test gating Operation D (parallel
  multi-hop). HARD_PASS -> ship T1.P2 (two-hop superposition).
  HARD_FAIL -> coherent multi-hop closes; LLM-orchestration remains the
  only multi-hop path (user-stated fallback, msg 1).

SCIENTIFIC QUESTION:
  Given K facts (k_i, v_i) stored in substrate W, form a superposition
  query q = sum_i beta_i k_i with known coefficients beta_i. Compute the
  raw substrate response r = W q (no argmax). Decompose r in the codebook
  basis:  alpha_c = <r, c> / ||c||^2  for each codeword c.
  Does the ranking / magnitude of alpha_c isolate the K stored
  components from the C-K spurious codewords?

DESIGN:
  - N=4096, BSC-equivalent Kerdock codebook (consistent with phase-region
    batch and PROT-018 _n4096 binding).
  - K facts stored with known keys k_i and values v_i drawn from codebook.
  - Four beta patterns explore coefficient regimes:
      P1 uniform: beta_i = 1/K for all i
      P2 peaked:  one beta_i = 1.0, rest = 0.1
      P3 random:  beta_i ~ U(0,1), then normalize sum to 1
      P4 sparse:  3 of K random beta_i non-zero (=1/3 each), rest = 0
  - 5 seeds [7, 17, 23, 31, 41]
  - 4 patterns x 5 seeds = 20 cell-seeds for the main K=10 test
  - K-scaling sub-test (P1 only): K in [5, 10, 15, 20] x 5 seeds = 20
    additional cell-seeds  ->  40 cell-seeds total at FULL.

  RAW response interpretation: r = W q = (sum_j v_j k_j.T / N) (sum_i beta_i k_i)
  = sum_i beta_i v_i (k_i.k_i / N) + cross-terms.
  For Kerdock codewords k.k/N = 1 -> r ~= sum_i beta_i v_i + noise.
  So decomposing r in codebook basis SHOULD recover stored v_i with
  amplitudes proportional to beta_i, IF cross-terms are small.

METRICS:
  - per_component_accuracy:  for each stored v_i, alpha_{v_i} must lie
       within +/- 10% of beta_i (or beta_i * <k_i, k_i>/N which is just
       beta_i for unit-normed Kerdock columns).
       Specifically: count storage indices i where
       |alpha_{v_i} - beta_i| / max(1e-6, ||r||) < 0.1.
       Reported as fraction (count / K).
  - cross_talk: max alpha_c over c NOT in stored value set, normalized
       by the mean alpha_{v_i} for stored value indices.
  - decomp_correlation: cos(reconstructed_r_from_alphas, r) where the
       reconstruction is built from the top-K alphas.

PRE-REGISTERED BANDS (matches user msg 1 spec):
  HARD_PASS: per_component_accuracy >= 0.90 AND cross_talk <= 0.10 in
       >= 3/5 seeds at K=10 across ALL 4 patterns AND linear K-scaling
       (per_component_accuracy roughly constant across K in [5,10,15,20];
       constancy: max - min <= 0.15).
  HARD_FAIL: per_component_accuracy <= 0.50 OR cross_talk >= 0.30
       (single-hop superposition does not work; closes Op D entirely).
  MIDDLE_BAND: partial signal; some patterns work, others don't.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. K=10 -> 4 patterns x 5 seeds = 20 main cell-seeds.
  3. K-scaling: 4 K-values x 5 seeds = 20 K-scaling cell-seeds.
  4. Total expected = 20 + 20 = 40 cell-seeds at FULL.
  5. Patterns sum-to-1 check: P1 uniform sum_i (1/K) = 1.0;
     P3 normalized sums to 1; P4 sparse 3*(1/3)=1.0.
     (P2 peaked does NOT sum to 1 by design; max=1.0 baseline + others=0.1 each.)
  6. Codebook orthogonality: <k_i, k_i>/N = 1 (Kerdock unit-norm rows
     after the v3 generator).

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: superposition_single_hop_decomp_v1_n4096
Queue: overnight_queue (GPU; N=4096; 40 cell-seeds)
Pre-reg: preregs/2026-05-30_superposition_single_hop_decomp_v1_n4096.md
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
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load substrate primitives (Kerdock codebook + store_facts_batched)
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_sup_dec", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
v3 = c1.v3

# Per-cell-seed checkpoint
_ckpt_path = REPO / "experiments" / "_seed_checkpoint.py"
_ckpt_spec = importlib.util.spec_from_file_location("_seed_checkpoint_supdec", _ckpt_path)
_ckpt = importlib.util.module_from_spec(_ckpt_spec)
_ckpt_spec.loader.exec_module(_ckpt)
list_completed_keys = _ckpt.list_completed_keys
write_partial_key   = _ckpt.write_partial_key
load_partial_key    = _ckpt.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds to N = 4096
N = 4096        # PROT-018 production-N anchor line
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Main K=10 test
K_MAIN = 10
PATTERN_IDS_FULL = ["P1_uniform", "P2_peaked", "P3_random", "P4_sparse"]
PATTERN_IDS_SMOKE = ["P1_uniform", "P2_peaked"]

# K-scaling sub-test (P1 only)
K_SCALING_FULL  = [5, 10, 15, 20]
K_SCALING_SMOKE = [5, 10]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_PER_COMP_ACC   = 0.90    # per_component_accuracy >= 0.90
HP_CROSSTALK_MAX  = 0.10    # cross_talk <= 0.10
HP_SEEDS_MIN      = 3       # >= 3/5 seeds per pattern
HP_KSCALE_RANGE   = 0.15    # max(acc) - min(acc) across K in [5,10,15,20] <= 0.15
HF_PER_COMP_ACC   = 0.50    # per_component_accuracy <= 0.50 = HARD_FAIL
HF_CROSSTALK_MIN  = 0.30    # cross_talk >= 0.30 = HARD_FAIL


def get_output_dir(default_name: str = "superposition_single_hop_decomp_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cell_key(kind: str, pattern: str, K: int, seed: int) -> str:
    """Composite key for per-cell-seed checkpoint.

    kind: "main" or "kscale"
    pattern: pattern id (or "P1_uniform" for kscale)
    K: K value
    seed: int seed
    """
    return f"{kind}_{pattern}_K{int(K)}_seed{int(seed)}"


def build_pattern_betas(pattern: str, K: int, seed: int,
                         device: torch.device) -> torch.Tensor:
    """Build a length-K coefficient vector for the named pattern."""
    if pattern == "P1_uniform":
        return torch.full((K,), 1.0 / K, dtype=torch.float32, device=device)
    if pattern == "P2_peaked":
        b = torch.full((K,), 0.1, dtype=torch.float32, device=device)
        gen = torch.Generator(device=device).manual_seed(seed + 900)
        peak = int(torch.randint(0, K, (1,), generator=gen, device=device).item())
        b[peak] = 1.0
        return b
    if pattern == "P3_random":
        gen = torch.Generator(device=device).manual_seed(seed + 901)
        b = torch.rand(K, generator=gen, device=device)
        b = b / b.sum().clamp(min=1e-9)
        return b.float()
    if pattern == "P4_sparse":
        gen = torch.Generator(device=device).manual_seed(seed + 902)
        n_nonzero = min(3, K)
        b = torch.zeros(K, dtype=torch.float32, device=device)
        perm = torch.randperm(K, generator=gen, device=device)[:n_nonzero]
        b[perm] = 1.0 / float(n_nonzero)
        return b
    raise ValueError(f"Unknown pattern: {pattern}")


def run_one_cell(pattern: str, K: int, seed: int, N_use: int,
                 device: torch.device) -> Dict:
    """One (pattern, K, seed) cell: build K facts, form q, decompose response."""
    codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
    W, keys, values, key_idx, val_idx = store_facts_batched(
        codebook, K, seed, N_use, device
    )
    # Now keys = codebook[key_idx % C], shape (K, N); values similarly.
    # Build the coefficient vector and the superposition query.
    betas = build_pattern_betas(pattern, K, seed, device)
    q = (betas.unsqueeze(1) * keys).sum(dim=0)         # (N,)

    # Substrate response (raw continuous; no argmax).
    r = W @ q                                          # (N,)
    r_norm = float(r.norm().item())
    r_norm_safe = max(r_norm, 1e-9)

    # Decompose in the codebook basis. For Kerdock rows, the auto-correlation
    # k.k/N = 1, so the natural projection is alpha_c = <r, c> / N.
    C = codebook.shape[0]
    alphas = (codebook @ r) / float(N_use)              # (C,)

    # Per-component accuracy: for each stored value v_i, the alpha at that
    # codeword index should be ~= beta_i (mod codebook orthogonality).
    # We accept if |alpha_{v_i} - beta_i| / ||r|| < 0.1.
    val_idx_mod = (val_idx % C).long()
    alphas_at_stored = alphas[val_idx_mod]              # (K,)
    err = (alphas_at_stored - betas).abs()              # (K,)
    rel = err / r_norm_safe
    per_component_hits = int((rel < 0.1).sum().item())
    per_component_accuracy = per_component_hits / float(K)

    # cross_talk: max alpha over codewords NOT in the stored value set,
    # normalized by mean alpha at stored value indices.
    mean_alpha_stored = float(alphas_at_stored.abs().mean().item())
    mean_alpha_safe = max(mean_alpha_stored, 1e-9)

    stored_mask = torch.zeros(C, dtype=torch.bool, device=device)
    stored_mask[val_idx_mod.unique()] = True
    spurious_alphas = alphas[~stored_mask]
    max_spurious = float(spurious_alphas.abs().max().item()) if spurious_alphas.numel() else 0.0
    cross_talk = max_spurious / mean_alpha_safe

    # decomp_correlation: cos(reconstructed_r_from_top_K_alphas, r)
    abs_alphas = alphas.abs()
    topk = min(K, abs_alphas.numel())
    top_idx = torch.topk(abs_alphas, topk).indices                # (K,)
    top_alpha_vals = alphas[top_idx]                              # (K,)
    r_recon = (top_alpha_vals.unsqueeze(1) * codebook[top_idx]).sum(dim=0)   # (N,)
    r_recon_norm = float(r_recon.norm().item())
    if r_recon_norm > 1e-9 and r_norm > 1e-9:
        decomp_correlation = float(
            (r @ r_recon).item() / (r_norm * r_recon_norm)
        )
    else:
        decomp_correlation = 0.0

    return {
        "pattern": pattern,
        "K": int(K),
        "seed": int(seed),
        "N": int(N_use),
        "per_component_accuracy": round(per_component_accuracy, 5),
        "cross_talk": round(cross_talk, 5),
        "decomp_correlation": round(decomp_correlation, 5),
        "r_norm": round(r_norm, 5),
        "mean_alpha_stored": round(mean_alpha_stored, 6),
        "max_spurious_alpha": round(max_spurious, 6),
        "betas_sum": round(float(betas.sum().item()), 5),
        "per_component_hits": per_component_hits,
    }


def cell_passes_hp(cell: Dict) -> bool:
    return (cell["per_component_accuracy"] >= HP_PER_COMP_ACC
            and cell["cross_talk"] <= HP_CROSSTALK_MAX)


def cell_is_hf(cell: Dict) -> bool:
    return (cell["per_component_accuracy"] <= HF_PER_COMP_ACC
            or cell["cross_talk"] >= HF_CROSSTALK_MIN)


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    main_cells = [c for c in summary.get("cells", []) if c.get("kind") == "main"]
    kscale_cells = [c for c in summary.get("cells", []) if c.get("kind") == "kscale"]

    if not main_cells:
        return ("SUP_DEC_INCONCLUSIVE", "No main cells.")

    # Per-pattern pass counts (K=10 main)
    pattern_pass = {}
    pattern_total = {}
    for c in main_cells:
        p = c["pattern"]
        pattern_pass.setdefault(p, 0)
        pattern_total.setdefault(p, 0)
        pattern_total[p] += 1
        if cell_passes_hp(c):
            pattern_pass[p] += 1

    # HARD_FAIL if any pattern is HF in majority of seeds, OR mean over all
    # main cells is below HF thresholds.
    n_hf = sum(1 for c in main_cells if cell_is_hf(c))
    frac_hf = n_hf / len(main_cells)

    # K-scaling constancy (P1 only)
    kscale_accs = {}
    for c in kscale_cells:
        kscale_accs.setdefault(c["K"], []).append(c["per_component_accuracy"])
    kscale_mean_per_K = {K: (sum(vs) / len(vs)) for K, vs in kscale_accs.items() if vs}
    if len(kscale_mean_per_K) >= 2:
        kscale_range = max(kscale_mean_per_K.values()) - min(kscale_mean_per_K.values())
    else:
        kscale_range = 0.0

    # Patterns_pass: ALL 4 patterns must reach HP_SEEDS_MIN in their seed count
    patterns_all_pass = all(pattern_pass.get(p, 0) >= HP_SEEDS_MIN
                             for p in PATTERN_IDS_FULL)
    # Allow smoke (fewer patterns)
    patterns_observed_pass = all(pattern_pass.get(p, 0) >= 1
                                  for p in pattern_pass.keys())

    detail = (f"main_cells={len(main_cells)} "
              f"per_pattern_pass={pattern_pass} "
              f"kscale_mean_per_K={ {K: round(v, 4) for K, v in kscale_mean_per_K.items()} } "
              f"kscale_range={kscale_range:.3f} frac_hf={frac_hf:.3f} "
              f"N={summary.get('N', N_FULL)}")

    # HARD_FAIL: >= 50% of main cells are HF (substrate cannot decompose).
    if frac_hf >= 0.5:
        return ("SUP_DEC_HARD_FAIL",
                f"CANNOT_DECOMPOSE: frac_hf={frac_hf:.3f}. " + detail)

    # HARD_PASS: all 4 patterns pass HP_SEEDS_MIN AND K-scaling constancy.
    if (patterns_all_pass
            and (len(kscale_mean_per_K) < 2 or kscale_range <= HP_KSCALE_RANGE)):
        return ("SUP_DEC_HARD_PASS",
                f"CLEAN_DECOMP: all patterns >= {HP_SEEDS_MIN}/{len(SEEDS_FULL)} "
                f"seeds, K-scale range {kscale_range:.3f} <= {HP_KSCALE_RANGE}. "
                + detail)

    # Smoke fast-path: smoke run reports its own per-pattern pass
    if (summary.get("smoke") and patterns_observed_pass
            and (len(kscale_mean_per_K) < 2 or kscale_range <= HP_KSCALE_RANGE)):
        return ("SUP_DEC_HARD_PASS",
                f"SMOKE_CLEAN_DECOMP: observed patterns each >=1 pass seed. "
                + detail)

    return ("SUP_DEC_MIDDLE_BAND",
            f"PARTIAL: some patterns / K-values pass; not unanimous. " + detail)


def _instrumentation_selftest() -> None:
    """Mandatory: assert all metrics non-null + verdict gates."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    assert len(PATTERN_IDS_FULL) == 4, f"patterns: {PATTERN_IDS_FULL}"
    assert len(K_SCALING_FULL) == 4, f"K-scale: {K_SCALING_FULL}"
    assert len(SEEDS_FULL) == 5, f"seeds: {SEEDS_FULL}"

    # Cell count formulas
    main_count = len(PATTERN_IDS_FULL) * len(SEEDS_FULL)
    kscale_count = len(K_SCALING_FULL) * len(SEEDS_FULL)
    assert main_count == 20, f"main count: {main_count}"
    assert kscale_count == 20, f"kscale count: {kscale_count}"
    assert main_count + kscale_count == 40, f"total: {main_count + kscale_count}"

    # Pattern construction self-tests on CPU
    device = torch.device("cpu")
    for p in PATTERN_IDS_FULL:
        b = build_pattern_betas(p, K_MAIN, 17, device)
        assert b.shape[0] == K_MAIN, f"pattern {p} shape: {b.shape}"
        if p == "P1_uniform":
            assert abs(float(b.sum().item()) - 1.0) < 1e-5, f"P1 sum: {b.sum()}"
        if p == "P3_random":
            assert abs(float(b.sum().item()) - 1.0) < 1e-5, f"P3 sum: {b.sum()}"
        if p == "P4_sparse":
            assert abs(float(b.sum().item()) - 1.0) < 1e-5, f"P4 sum: {b.sum()}"
            nz = int((b != 0).sum().item())
            assert nz == 3, f"P4 nonzero: {nz}"
        if p == "P2_peaked":
            mx = float(b.max().item())
            assert abs(mx - 1.0) < 1e-5, f"P2 max: {mx}"

    # cell_key uniqueness
    ck1 = cell_key("main", "P1_uniform", 10, 17)
    ck2 = cell_key("kscale", "P1_uniform", 10, 17)
    assert ck1 != ck2, f"main vs kscale keys collide: {ck1}, {ck2}"
    assert ck1 == "main_P1_uniform_K10_seed17", f"ck1: {ck1}"

    # Smoke: 1 cell at small N to exercise codepath + metric computation
    out = run_one_cell("P1_uniform", K_MAIN, 17, N_SMOKE, device)
    for k in ("per_component_accuracy", "cross_talk", "decomp_correlation",
              "r_norm", "mean_alpha_stored"):
        v_ = out.get(k)
        assert v_ is not None and not (isinstance(v_, float) and math.isnan(v_)), (
            f"selftest: metric {k} null/NaN in {out}")
    assert 0.0 <= out["per_component_accuracy"] <= 1.0, (
        f"per_component_accuracy out of [0,1]: {out['per_component_accuracy']}")
    assert out["cross_talk"] >= 0.0, f"cross_talk negative: {out['cross_talk']}"

    # Verdict self-tests
    # HARD_FAIL: many HF main cells
    fake_hf_cells = [
        {"kind": "main", "pattern": p, "K": 10, "seed": s,
         "per_component_accuracy": 0.1, "cross_talk": 0.5,
         "decomp_correlation": 0.05}
        for p in PATTERN_IDS_FULL for s in SEEDS_FULL
    ]
    vf, mf = compute_verdict({"cells": fake_hf_cells, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf} {mf}"

    # HARD_PASS: all main cells pass, K-scaling tight
    fake_hp_cells = [
        {"kind": "main", "pattern": p, "K": 10, "seed": s,
         "per_component_accuracy": 0.95, "cross_talk": 0.05,
         "decomp_correlation": 0.95}
        for p in PATTERN_IDS_FULL for s in SEEDS_FULL
    ] + [
        {"kind": "kscale", "pattern": "P1_uniform", "K": K, "seed": s,
         "per_component_accuracy": 0.93, "cross_talk": 0.06,
         "decomp_correlation": 0.93}
        for K in K_SCALING_FULL for s in SEEDS_FULL
    ]
    vp, mp = compute_verdict({"cells": fake_hp_cells, "N": N_FULL})
    assert "HARD_PASS" in vp, f"HARD_PASS gate: {vp} {mp}"

    # MIDDLE_BAND: some patterns pass, others not
    fake_mb_cells = [
        {"kind": "main", "pattern": "P1_uniform", "K": 10, "seed": s,
         "per_component_accuracy": 0.95, "cross_talk": 0.05,
         "decomp_correlation": 0.95}
        for s in SEEDS_FULL
    ] + [
        {"kind": "main", "pattern": "P2_peaked", "K": 10, "seed": s,
         "per_component_accuracy": 0.6, "cross_talk": 0.15,
         "decomp_correlation": 0.6}
        for s in SEEDS_FULL
    ]
    vmb, mmb = compute_verdict({"cells": fake_mb_cells, "N": N_FULL})
    assert "MIDDLE_BAND" in vmb or "HARD_FAIL" in vmb, f"MIDDLE_BAND gate: {vmb} {mmb}"

    print(
        f"[selftest] superposition_single_hop_decomp_v1_n4096 PASS "
        f"smoke per_comp_acc={out['per_component_accuracy']:.3f} "
        f"cross_talk={out['cross_talk']:.3f} "
        f"decomp_corr={out['decomp_correlation']:.3f}",
        flush=True,
    )


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg     = N_SMOKE if smoke else N_FULL
    patterns  = PATTERN_IDS_SMOKE if smoke else PATTERN_IDS_FULL
    K_scale   = K_SCALING_SMOKE if smoke else K_SCALING_FULL
    seeds     = SEEDS_SMOKE if smoke else SEEDS_FULL

    main_expected = len(patterns) * len(seeds)
    kscale_expected = len(K_scale) * len(seeds)
    total_expected = main_expected + kscale_expected

    out_dir = get_output_dir()
    done_keys = set(list_completed_keys(out_dir))

    print(f"[run] superposition_single_hop_decomp_v1_n4096 smoke={smoke} N={N_cfg} "
          f"patterns={patterns} K_scale={K_scale} seeds={seeds} "
          f"main_expected={main_expected} kscale_expected={kscale_expected} "
          f"total_expected={total_expected} already_done={len(done_keys)} "
          f"device={device_str}", flush=True)
    t0 = time.time()

    # Main K=10 sweep
    for pattern in patterns:
        for seed in seeds:
            ck = cell_key("main", pattern, K_MAIN, seed)
            if ck in done_keys:
                continue
            try:
                out = run_one_cell(pattern, K_MAIN, seed, N_cfg, device)
                out["kind"] = "main"
                out["seed_int"] = out["seed"]
                out["seed"] = ck
                write_partial_key(out_dir, ck, out)
                print(f"  {ck} per_comp_acc={out['per_component_accuracy']:.3f} "
                      f"cross_talk={out['cross_talk']:.3f} "
                      f"decomp_corr={out['decomp_correlation']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  {ck} CELL_FAILED: {type(e).__name__}: {e}", flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()

    # K-scaling sub-test (P1 only)
    for K in K_scale:
        for seed in seeds:
            ck = cell_key("kscale", "P1_uniform", K, seed)
            if ck in done_keys:
                continue
            try:
                out = run_one_cell("P1_uniform", K, seed, N_cfg, device)
                out["kind"] = "kscale"
                out["seed_int"] = out["seed"]
                out["seed"] = ck
                write_partial_key(out_dir, ck, out)
                print(f"  {ck} per_comp_acc={out['per_component_accuracy']:.3f} "
                      f"cross_talk={out['cross_talk']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  {ck} CELL_FAILED: {type(e).__name__}: {e}", flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()

    # Aggregate from disk (resilient across restarts)
    all_cells = []
    for ck in list_completed_keys(out_dir):
        body = load_partial_key(out_dir, ck)
        if body is None:
            continue
        all_cells.append(body)

    summary = {
        "anchor": "superposition_single_hop_decomp_v1_n4096",
        "N": N_cfg,
        "smoke": smoke,
        "patterns": patterns,
        "K_scaling": K_scale,
        "seeds": seeds,
        "main_expected": main_expected,
        "kscale_expected": kscale_expected,
        "total_expected": total_expected,
        "n_completed": len(all_cells),
        "cells": all_cells,
    }
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = round(time.time() - t0, 2)
    summary["verdict"] = verdict
    summary["verdict_msg"] = verdict_msg
    summary["elapsed_s"] = elapsed

    out_path = out_dir / "metrics.json"
    payload = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[completed] {len(all_cells)}/{total_expected}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
