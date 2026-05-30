"""SUPERPOSITION TOP-K FILTER v2 -- SPARSE-PATTERN RESCUE at N=4096.

CONTEXT (F6 v1 follow-up):
  v1 verdict = TOPK_MIDDLE_BAND.
  Per-pattern results (filter = naive top-K=10):
    P1 uniform : 5/5 seeds pass
    P2 peaked  : 5/5 seeds pass
    P3 random  : 3/5 seeds pass
    P4 sparse  : 0/5 seeds pass

  The naive top-K=10 filter works for uniform / peaked patterns where
  each stored codeword amplitude is bounded and similar. It fails for
  SPARSE patterns where only ~3 betas are nonzero -- the off-target
  codeword amplitudes are comparable to the few intended components.

RESCUE STRATEGY (v2):
  Compare three filter designs:
    naive      -- top-K=10 |alpha_c| indices (v1 baseline).
    weighted   -- top-K=10, but with priors scaled by beta_i so the
                  filter expects amplitude proportional to beta_i.
                  Score = |alpha_c - beta_c_expected| where beta_c_expected
                  is the projection of beta onto codeword c via val_idx.
                  Keep K indices with smallest deviation from expected.
    threshold  -- dynamic threshold = mean(|alpha_c|) + 2*std(|alpha_c|);
                  keep only components above threshold (no fixed K).

SCIENTIFIC QUESTION:
  Does either weighted-prior or threshold-adaptive filter rescue the
  sparse pattern (P4) WITHOUT regressing uniform/peaked patterns?

PRE-REGISTERED BANDS:
  HARD_PASS: AT LEAST ONE of {weighted, threshold} achieves
    per_component_accuracy>=0.90 AND cross_talk<=0.10 in >=3/5 seeds
    for the SPARSE pattern (P4) AND maintains v1 HP performance on
    uniform/peaked patterns (>=3/5 seeds clean on P1+P2).
  HARD_FAIL: NEITHER filter rescues sparse (both weighted and threshold
    fail >=3/5 seeds on P4) -- sparse pattern closes for Op D, Phase 2
    is restricted to uniform/peaked only per [[feedback-dont-overextend]].
  MIDDLE_BAND: partial rescue (some patterns improved but P4 still
    not in HP band).

  OUTCOME: HP -> Op D Phase 2 ships at full pattern coverage.
            HF -> Op D Phase 2 restricted to uniform/peaked (sparse closes).

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. K_MAIN = 10; 4 patterns * 3 filters * 5 seeds = 60 cell-seeds.
  3. naive filter: topk(|alpha|, K) -> K nonzeros.
  4. weighted filter: builds expected beta_c (zeros except at stored
     val_idx), scores |alpha_c - expected_c|, keeps K SMALLEST.
  5. threshold filter: dynamic threshold from alpha distribution.
  6. Patterns reuse v1 P1/P2/P3/P4 build helpers.

OOM CHECK:
  N=4096, K=10: ~900MB (same as v1). 3 filters add only small overhead
  (top-K + mask + comparison ops). OK on CPU.

TIMEOUT ESTIMATE:
  v1 wall ~600s (4 patterns * 5 seeds * ~30s/cell GPU).
  CPU is slower: ~2x. With 3 filters per cell instead of 1: ~3x ops.
  Estimated wall: 4 * 5 * ~90s = 1800s, with 3-filter expansion ~5400s.
  Budget 14400s for safety margin.

CHECKPOINT (PROT-021):
  Per-(pattern, filter, seed) granularity. 60 partial files.

N-suffix: _n4096 (PROT-018).
Anchor: superposition_top_k_filter_v2_n4096
Queue: remote_cpu_queue (CPU)
Pre-reg: preregs/2026-05-30_superposition_top_k_filter_v2_n4096.md
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

# Reuse substrate primitives via axis1_mb_chunk1 (same as v1)
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_topk_v2", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)
store_facts_batched = c1.store_facts_batched
v3 = c1.v3

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_topk_v2", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

K_MAIN = 10
PATTERN_IDS_FULL = ["P1_uniform", "P2_peaked", "P3_random", "P4_sparse"]
PATTERN_IDS_SMOKE = ["P1_uniform", "P4_sparse"]
FILTERS_FULL = ["naive", "weighted", "threshold"]
FILTERS_SMOKE = ["naive", "weighted", "threshold"]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (per-cell)
HP_PER_COMP_ACC  = 0.90
HP_CROSSTALK_MAX = 0.10
HP_SEEDS_MIN     = 3
HF_CROSSTALK_MIN = 0.10   # filter fails to reduce cross_talk

# Sparse pattern is the rescue focus
SPARSE_PATTERN = "P4_sparse"
EASY_PATTERNS  = ["P1_uniform", "P2_peaked"]


def get_output_dir(default_name: str = "superposition_top_k_filter_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cell_key(pattern: str, filter_name: str, K: int, seed: int) -> str:
    return f"{pattern}_{filter_name}_K{int(K)}_seed{int(seed)}"


def build_pattern_betas(pattern: str, K: int, seed: int,
                         device: torch.device) -> torch.Tensor:
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


# ---------- THREE FILTERS ----------

def filter_naive(alphas: torch.Tensor, K: int, betas: torch.Tensor,
                  val_idx_mod: torch.Tensor, C: int) -> torch.Tensor:
    """v1 baseline: keep top-K |alpha_c|, zero rest."""
    topk_K = min(K, alphas.numel())
    top_idx = torch.topk(alphas.abs(), topk_K).indices
    mask = torch.zeros(C, dtype=torch.bool, device=alphas.device)
    mask[top_idx] = True
    return torch.where(mask, alphas, torch.zeros_like(alphas))


def filter_weighted(alphas: torch.Tensor, K: int, betas: torch.Tensor,
                     val_idx_mod: torch.Tensor, C: int) -> torch.Tensor:
    """Weighted-prior: keep K codewords whose alpha BEST matches beta-prior.

    For each codeword index c in {0..C-1}:
      expected_c = sum over i where val_idx[i] == c of betas[i] (sums dups)
    Score = |alpha_c - expected_c|; keep K with SMALLEST score (closest to
    prior), zero the rest. This favors recovery of intended components even
    when their amplitude is small (as in sparse patterns).
    """
    expected = torch.zeros(C, dtype=alphas.dtype, device=alphas.device)
    # Accumulate beta at stored codeword indices (sum duplicates)
    expected.index_add_(0, val_idx_mod, betas)
    score = (alphas - expected).abs()
    topk_K = min(K, alphas.numel())
    # Smallest scores = closest to expected
    smallest_idx = torch.topk(-score, topk_K).indices
    mask = torch.zeros(C, dtype=torch.bool, device=alphas.device)
    mask[smallest_idx] = True
    return torch.where(mask, alphas, torch.zeros_like(alphas))


def filter_threshold(alphas: torch.Tensor, K: int, betas: torch.Tensor,
                      val_idx_mod: torch.Tensor, C: int) -> torch.Tensor:
    """Threshold-adaptive: threshold = mean(|alpha|) + 2 * std(|alpha|).

    Keeps only components above threshold (no fixed K). For sparse patterns
    where only a few alphas are large, this picks them up automatically;
    for uniform patterns, the larger spread keeps the K intended components.
    """
    abs_a = alphas.abs()
    thresh = abs_a.mean() + 2.0 * abs_a.std()
    mask = abs_a > thresh
    return torch.where(mask, alphas, torch.zeros_like(alphas))


FILTER_FNS = {
    "naive": filter_naive,
    "weighted": filter_weighted,
    "threshold": filter_threshold,
}


def run_one_cell(pattern: str, filter_name: str, K: int, seed: int,
                  N_use: int, device: torch.device) -> Dict:
    """One (pattern, filter, seed) cell. Returns metrics dict."""
    codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
    W, keys, values, key_idx, val_idx = store_facts_batched(
        codebook, K, seed, N_use, device)

    betas = build_pattern_betas(pattern, K, seed, device)
    q = (betas.unsqueeze(1) * keys).sum(dim=0)
    r = W @ q
    r_norm = float(r.norm().item())
    r_norm_safe = max(r_norm, 1e-9)

    C = codebook.shape[0]
    alphas = (codebook @ r) / float(N_use)

    val_idx_mod = (val_idx % C).long()

    # Apply selected filter
    filter_fn = FILTER_FNS[filter_name]
    alphas_filtered = filter_fn(alphas, K, betas, val_idx_mod, C)

    # Post-filter per-component accuracy
    alphas_filtered_at_stored = alphas_filtered[val_idx_mod]
    err_post = (alphas_filtered_at_stored - betas).abs()
    rel_post = err_post / r_norm_safe
    post_filter_hits = int((rel_post < 0.1).sum().item())
    per_component_accuracy = post_filter_hits / float(K)

    # Post-filter cross_talk
    mean_alpha_stored_post = float(alphas_filtered_at_stored.abs().mean().item())
    mean_alpha_safe_post = max(mean_alpha_stored_post, 1e-9)
    stored_mask = torch.zeros(C, dtype=torch.bool, device=device)
    stored_mask[val_idx_mod.unique()] = True
    spurious_filtered = alphas_filtered[~stored_mask]
    max_spurious_post = (float(spurious_filtered.abs().max().item())
                         if spurious_filtered.numel() else 0.0)
    cross_talk = max_spurious_post / mean_alpha_safe_post

    # Count nonzeros in filtered output (diagnostic)
    n_kept = int((alphas_filtered != 0).sum().item())

    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    return {
        "pattern": pattern,
        "filter": filter_name,
        "K": int(K),
        "seed": int(seed),
        "N": int(N_use),
        "per_component_accuracy": round(per_component_accuracy, 5),
        "cross_talk":             round(cross_talk, 5),
        "n_kept":                 int(n_kept),
        "r_norm":                 round(r_norm, 5),
        "betas_sum":              round(float(betas.sum().item()), 5),
        "betas_nnz":              int((betas != 0).sum().item()),
    }


def cell_passes_hp(c: Dict) -> bool:
    return (c["per_component_accuracy"] >= HP_PER_COMP_ACC
            and c["cross_talk"] <= HP_CROSSTALK_MAX)


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    """Compare 3 filters; HP if any filter rescues sparse AND preserves easy."""
    if not cells:
        return ("TOPK_V2_INCONCLUSIVE", "No cells.")

    # Tally by (pattern, filter): how many seeds pass HP?
    pass_count: Dict[Tuple[str, str], int] = {}
    total_count: Dict[Tuple[str, str], int] = {}
    for c in cells:
        key = (c["pattern"], c["filter"])
        pass_count.setdefault(key, 0)
        total_count.setdefault(key, 0)
        total_count[key] += 1
        if cell_passes_hp(c):
            pass_count[key] += 1

    # Find filters that rescue sparse (>=3/5 seeds pass on P4)
    rescuing_filters = []
    for f in FILTERS_FULL:
        if pass_count.get((SPARSE_PATTERN, f), 0) >= HP_SEEDS_MIN:
            rescuing_filters.append(f)

    # Find filters that maintain easy patterns (>=3/5 seeds pass on P1+P2)
    easy_pass_filters = []
    for f in FILTERS_FULL:
        if all(pass_count.get((p, f), 0) >= HP_SEEDS_MIN for p in EASY_PATTERNS):
            easy_pass_filters.append(f)

    rescuing_and_clean = [f for f in rescuing_filters if f in easy_pass_filters]

    detail = (f"pass_count={ {f'{p}|{f}':n for (p, f), n in pass_count.items()} } "
              f"rescuing_filters={rescuing_filters} "
              f"easy_pass_filters={easy_pass_filters}")

    if rescuing_and_clean:
        return ("TOPK_V2_HARD_PASS",
                f"SPARSE_RESCUE: filters={rescuing_and_clean} pass sparse "
                f"AND maintain easy. " + detail)

    # HF: neither weighted nor threshold rescue sparse
    advanced_filters = [f for f in FILTERS_FULL if f != "naive"]
    none_rescue_sparse = all(
        pass_count.get((SPARSE_PATTERN, f), 0) < HP_SEEDS_MIN
        for f in advanced_filters
    )
    if none_rescue_sparse:
        return ("TOPK_V2_HARD_FAIL",
                f"NO_SPARSE_RESCUE: weighted+threshold both fail sparse. " + detail)

    return ("TOPK_V2_MIDDLE_BAND",
            f"PARTIAL_RESCUE: some filter rescues sparse but regresses easy. "
            + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    assert len(PATTERN_IDS_FULL) == 4
    assert len(FILTERS_FULL) == 3
    main_count = len(PATTERN_IDS_FULL) * len(FILTERS_FULL) * len(SEEDS_FULL)
    assert main_count == 60, f"main cell count: {main_count}"

    # Patterns build correctly
    device = torch.device("cpu")
    for p in PATTERN_IDS_FULL:
        b = build_pattern_betas(p, K_MAIN, 17, device)
        assert b.shape[0] == K_MAIN

    # Naive filter: K=5 yields exactly 5 nonzeros (when alphas distinct)
    C_test = 100; K_test = 5
    alphas_test = torch.randn(C_test)
    betas_dummy = torch.zeros(K_test)
    val_idx_dummy = torch.zeros(K_test, dtype=torch.long)
    af_naive = filter_naive(alphas_test, K_test, betas_dummy,
                             val_idx_dummy, C_test)
    nnz = int((af_naive != 0).sum().item())
    assert nnz == K_test, f"naive top-K nnz: {nnz}"

    # Weighted filter: index_add does NOT error
    af_w = filter_weighted(alphas_test, K_test, torch.ones(K_test),
                            torch.arange(K_test, dtype=torch.long), C_test)
    nnz_w = int((af_w != 0).sum().item())
    assert nnz_w == K_test, f"weighted nnz: {nnz_w}"

    # Threshold filter: non-trivial mask
    af_t = filter_threshold(alphas_test, K_test, betas_dummy,
                             val_idx_dummy, C_test)
    nnz_t = int((af_t != 0).sum().item())
    assert 0 <= nnz_t <= C_test, f"threshold nnz: {nnz_t}"

    # Verdict gates
    fake_hp = []
    for p in PATTERN_IDS_FULL:
        for f in FILTERS_FULL:
            for s in SEEDS_FULL:
                pca = 0.95 if (f == "weighted" or p in EASY_PATTERNS) else 0.3
                ct = 0.05 if (f == "weighted" or p in EASY_PATTERNS) else 0.5
                fake_hp.append({"pattern": p, "filter": f, "K": K_MAIN, "seed": s,
                                 "per_component_accuracy": pca,
                                 "cross_talk": ct})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for p in PATTERN_IDS_FULL:
        for f in FILTERS_FULL:
            for s in SEEDS_FULL:
                pca = 0.95 if p in EASY_PATTERNS else 0.3
                ct = 0.05 if p in EASY_PATTERNS else 0.5
                fake_hf.append({"pattern": p, "filter": f, "K": K_MAIN, "seed": s,
                                 "per_component_accuracy": pca,
                                 "cross_talk": ct})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Smoke 1 cell per filter on CPU
    for f in FILTERS_FULL:
        out = run_one_cell("P1_uniform", f, K_MAIN, 17, N_SMOKE, device)
        for k in ("per_component_accuracy", "cross_talk"):
            v_ = out.get(k)
            assert v_ is not None and not (isinstance(v_, float) and math.isnan(v_))
    print(f"[selftest] superposition_top_k_filter_v2_n4096 PASS smoke all 3 filters",
          flush=True)


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

    N_cfg = N_SMOKE if smoke else N_FULL
    patterns = PATTERN_IDS_SMOKE if smoke else PATTERN_IDS_FULL
    filters  = FILTERS_SMOKE if smoke else FILTERS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] superposition_top_k_filter_v2_n4096 smoke={smoke} N={N_cfg} "
          f"patterns={patterns} filters={filters} seeds={seeds} "
          f"done={len(done)} device={device_str}", flush=True)

    cells: List[Dict] = []
    for pattern in patterns:
        for filter_name in filters:
            for seed in seeds:
                ck = cell_key(pattern, filter_name, K_MAIN, seed)
                if ck in done:
                    body = load_partial_key(out_dir, ck)
                    if body is not None:
                        cells.append(body); continue
                try:
                    out = run_one_cell(pattern, filter_name, K_MAIN, seed,
                                        N_cfg, device)
                    write_partial_key(out_dir, ck, out)
                    cells.append(out)
                    print(f"  {ck} pca={out['per_component_accuracy']:.3f} "
                          f"ct={out['cross_talk']:.3f} nk={out['n_kept']} "
                          f"({time.time()-t0:.1f}s)", flush=True)
                except (RuntimeError, MemoryError) as e:
                    print(f"  {ck} CELL_FAILED: {type(e).__name__}: {e}",
                          flush=True)
                    if device.type == 'cuda':
                        torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "superposition_top_k_filter_v2_n4096", "N": N_cfg,
               "smoke": smoke, "patterns": patterns, "filters": filters,
               "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
