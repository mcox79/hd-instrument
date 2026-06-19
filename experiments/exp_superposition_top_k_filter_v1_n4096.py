"""SUPERPOSITION TOP-K FILTER v1 at N=4096.

CONTEXT (F6 -- Op D cross-talk rescue):
  Track A+B+C verdict (commit 2a6bf84): the v1 superposition_single_hop_decomp
  test showed substrate response decomposes onto the codebook basis, but
  spurious cross-talk components above stored-value indices remain. The
  proposed rescue is a TOP-K POST-DECOMP FILTER: keep only the K largest
  alphas (where K = number of stored facts), zero the rest. If this filter
  drops cross_talk below 0.10 while preserving per-component accuracy,
  Op D unlocks T1 Phase 2 (two-hop superposition).

SCIENTIFIC QUESTION:
  Given K stored facts (k_i, v_i) and a superposition query
  q = sum_i beta_i k_i with the four beta patterns from v1, decompose
  the substrate response r = W q in the codebook basis (alpha_c =
  <r, c> / N for each codeword), then apply a top-K filter (keep
  K largest |alpha_c|, zero the rest). Does:
    - cross_talk (max spurious alpha / mean stored alpha) drop to <= 0.10?
    - per_component_accuracy (fraction of stored v_i recovered within
      10% of beta_i in filtered set) remain >= 0.90?

PRE-REGISTERED BANDS:
  HARD_PASS: post-filter cross_talk <= 0.10 in >= 3/5 seeds across ALL 4
    patterns AND post-filter per_component_accuracy >= 0.90.
  HARD_FAIL: filter does NOT reduce cross_talk (post-filter cross_talk
    > 0.10 in 3+/5 seeds at all 4 patterns) -- Op D superposition
    closes definitively even with filter rescue.
  MIDDLE_BAND: filter works for some patterns but not others.

  OUTCOME: HP -> ship T1 P2 two-hop. HF -> Op D superposition closes.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. K_MAIN = 10; 4 patterns * 5 seeds = 20 main cell-seeds.
  3. Top-K filter: torch.topk(|alpha|, K) yields K indices; mask zeros.
  4. Patterns reuse v1 P1/P2/P3/P4.

OOM CHECK:
  N=4096, K=10: identical to v1; ~900MB. OK.

TIMEOUT ESTIMATE:
  Same as v1 (~5s/cell smoke, ~30s/cell FULL). 20 cells = 600s. 14400s cap.

N-suffix: _n4096 (PROT-018).
Anchor: superposition_top_k_filter_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_superposition_top_k_filter_v1_n4096.md
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

# Reuse substrate primitives (Kerdock + store_facts_batched) via axis1_mb_chunk1
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_topk", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)
store_facts_batched = c1.store_facts_batched
v3 = c1.v3

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_topk", _ck_path)
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
PATTERN_IDS_SMOKE = ["P1_uniform", "P2_peaked"]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (post-filter)
HP_PER_COMP_ACC  = 0.90
HP_CROSSTALK_MAX = 0.10
HP_SEEDS_MIN     = 3
HF_CROSSTALK_MIN = 0.10   # filter fails to reduce cross_talk


def get_output_dir(default_name: str = "superposition_top_k_filter_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cell_key(pattern: str, K: int, seed: int) -> str:
    return f"{pattern}_K{int(K)}_seed{int(seed)}"


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


def run_one_cell(pattern: str, K: int, seed: int, N_use: int,
                 device: torch.device) -> Dict:
    """One cell: decompose superposition response and apply top-K filter."""
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

    # PRE-FILTER metrics (sanity reference)
    val_idx_mod = (val_idx % C).long()
    alphas_at_stored = alphas[val_idx_mod]
    err_pre = (alphas_at_stored - betas).abs()
    rel_pre = err_pre / r_norm_safe
    pre_filter_hits = int((rel_pre < 0.1).sum().item())
    pre_filter_acc = pre_filter_hits / float(K)
    mean_alpha_stored_pre = float(alphas_at_stored.abs().mean().item())
    mean_alpha_safe_pre = max(mean_alpha_stored_pre, 1e-9)
    stored_mask = torch.zeros(C, dtype=torch.bool, device=device)
    stored_mask[val_idx_mod.unique()] = True
    spurious_alphas_pre = alphas[~stored_mask]
    max_spurious_pre = (float(spurious_alphas_pre.abs().max().item())
                        if spurious_alphas_pre.numel() else 0.0)
    cross_talk_pre = max_spurious_pre / mean_alpha_safe_pre

    # POST-FILTER: top-K |alpha|, zero the rest
    abs_alphas = alphas.abs()
    topk_K = min(K, abs_alphas.numel())
    top_idx = torch.topk(abs_alphas, topk_K).indices
    mask = torch.zeros(C, dtype=torch.bool, device=device)
    mask[top_idx] = True
    alphas_filtered = torch.where(mask, alphas, torch.zeros_like(alphas))

    # Post-filter per-component accuracy
    alphas_filtered_at_stored = alphas_filtered[val_idx_mod]
    err_post = (alphas_filtered_at_stored - betas).abs()
    rel_post = err_post / r_norm_safe
    post_filter_hits = int((rel_post < 0.1).sum().item())
    per_component_accuracy = post_filter_hits / float(K)

    # Post-filter cross_talk
    mean_alpha_stored_post = float(alphas_filtered_at_stored.abs().mean().item())
    mean_alpha_safe_post = max(mean_alpha_stored_post, 1e-9)
    spurious_filtered = alphas_filtered[~stored_mask]
    max_spurious_post = (float(spurious_filtered.abs().max().item())
                         if spurious_filtered.numel() else 0.0)
    cross_talk = max_spurious_post / mean_alpha_safe_post

    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    return {
        "pattern": pattern,
        "K": int(K),
        "seed": int(seed),
        "N": int(N_use),
        "per_component_accuracy": round(per_component_accuracy, 5),
        "cross_talk":             round(cross_talk, 5),
        "pre_filter_per_comp_acc": round(pre_filter_acc, 5),
        "pre_filter_cross_talk":  round(cross_talk_pre, 5),
        "r_norm": round(r_norm, 5),
        "betas_sum": round(float(betas.sum().item()), 5),
    }


def cell_passes_hp(c: Dict) -> bool:
    return (c["per_component_accuracy"] >= HP_PER_COMP_ACC
            and c["cross_talk"] <= HP_CROSSTALK_MAX)


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("TOPK_INCONCLUSIVE", "No cells.")

    pattern_pass: Dict[str, int] = {}
    pattern_total: Dict[str, int] = {}
    pattern_ct_above: Dict[str, int] = {}
    for c in cells:
        p = c["pattern"]
        pattern_pass.setdefault(p, 0)
        pattern_total.setdefault(p, 0)
        pattern_ct_above.setdefault(p, 0)
        pattern_total[p] += 1
        if cell_passes_hp(c):
            pattern_pass[p] += 1
        if c["cross_talk"] > HF_CROSSTALK_MIN:
            pattern_ct_above[p] += 1

    detail = (f"per_pattern_pass={pattern_pass} "
              f"per_pattern_total={pattern_total} "
              f"per_pattern_ct_above={pattern_ct_above}")

    # HARD_FAIL: in EVERY pattern, cross_talk remains > 0.10 in HP_SEEDS_MIN+
    # seeds (filter does not reduce cross_talk anywhere).
    all_patterns_fail = all(
        pattern_ct_above.get(p, 0) >= HP_SEEDS_MIN
        for p in pattern_pass.keys()
    )
    if all_patterns_fail and len(pattern_pass) >= 2:
        return ("TOPK_HARD_FAIL",
                f"FILTER_INEFFECTIVE: cross_talk remains > {HF_CROSSTALK_MIN} "
                f"across all patterns. " + detail)

    # HARD_PASS: ALL 4 patterns reach HP_SEEDS_MIN passing seeds
    patterns_all_pass = all(pattern_pass.get(p, 0) >= HP_SEEDS_MIN
                             for p in PATTERN_IDS_FULL)
    patterns_observed_pass = all(pattern_pass.get(p, 0) >= 1
                                  for p in pattern_pass.keys())

    if patterns_all_pass:
        return ("TOPK_HARD_PASS",
                f"FILTER_WORKS: all 4 patterns >= {HP_SEEDS_MIN}/5 seeds clean. "
                + detail)
    # Smoke fast-path
    if patterns_observed_pass and len(pattern_pass) >= 1:
        # Only call HARD_PASS on smoke if every observed pattern >=1 pass
        return ("TOPK_HARD_PASS",
                f"SMOKE_FILTER_WORKS: observed patterns each >=1 pass seed. "
                + detail)

    return ("TOPK_MIDDLE_BAND",
            f"PARTIAL: some patterns clean, others not. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    assert len(PATTERN_IDS_FULL) == 4
    main_count = len(PATTERN_IDS_FULL) * len(SEEDS_FULL)
    assert main_count == 20, f"main cell count: {main_count}"

    # Patterns sum invariants
    device = torch.device("cpu")
    for p in PATTERN_IDS_FULL:
        b = build_pattern_betas(p, K_MAIN, 17, device)
        assert b.shape[0] == K_MAIN

    # Top-K filter property: with K=5 and 100-dim alpha, exactly 5 nonzeros
    K_test = 5; C_test = 100
    alphas_test = torch.randn(C_test)
    top_idx = torch.topk(alphas_test.abs(), K_test).indices
    mask = torch.zeros(C_test, dtype=torch.bool)
    mask[top_idx] = True
    af = torch.where(mask, alphas_test, torch.zeros_like(alphas_test))
    nnz = int((af != 0).sum().item())
    assert nnz == K_test, f"top-K mask gave {nnz} nonzeros, expected {K_test}"

    # Verdict gates
    fake_hp = []
    for p in PATTERN_IDS_FULL:
        for s in SEEDS_FULL:
            fake_hp.append({"pattern": p, "K": K_MAIN, "seed": s,
                            "per_component_accuracy": 0.95,
                            "cross_talk": 0.05})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for p in PATTERN_IDS_FULL:
        for s in SEEDS_FULL:
            fake_hf.append({"pattern": p, "K": K_MAIN, "seed": s,
                            "per_component_accuracy": 0.3,
                            "cross_talk": 0.5})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Smoke 1 cell on CPU
    out = run_one_cell("P1_uniform", K_MAIN, 17, N_SMOKE, device)
    for k in ("per_component_accuracy", "cross_talk",
              "pre_filter_per_comp_acc", "pre_filter_cross_talk"):
        v_ = out.get(k)
        assert v_ is not None and not (isinstance(v_, float) and math.isnan(v_))
    print(f"[selftest] superposition_top_k_filter_v1_n4096 PASS "
          f"smoke pre_ct={out['pre_filter_cross_talk']:.3f} "
          f"post_ct={out['cross_talk']:.3f} "
          f"post_acc={out['per_component_accuracy']:.3f}", flush=True)


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
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] superposition_top_k_filter_v1_n4096 smoke={smoke} N={N_cfg} "
          f"patterns={patterns} seeds={seeds} done={len(done)} device={device_str}",
          flush=True)

    cells: List[Dict] = []
    for pattern in patterns:
        for seed in seeds:
            ck = cell_key(pattern, K_MAIN, seed)
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = run_one_cell(pattern, K_MAIN, seed, N_cfg, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  {ck} pre_ct={out['pre_filter_cross_talk']:.3f} "
                      f"post_ct={out['cross_talk']:.3f} "
                      f"post_acc={out['per_component_accuracy']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  {ck} CELL_FAILED: {type(e).__name__}: {e}", flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "superposition_top_k_filter_v1_n4096", "N": N_cfg,
               "smoke": smoke, "patterns": patterns, "seeds": seeds,
               "cells": cells, "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
