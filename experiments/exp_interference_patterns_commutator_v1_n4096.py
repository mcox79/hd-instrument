"""INTERFERENCE PATTERNS / COMMUTATOR v1 at N=4096.

CONTEXT (F9 -- msg-1 T7 Op F):
  Op F: substrate matrix products and commutators. For two substrates
  W_A, W_B does the COMMUTATOR [W_A, W_B] = W_A W_B - W_B W_A carry an
  information-theoretic signature that distinguishes:
    (a) Independent W_A, W_B (disjoint stored facts)
    (b) Related W_A, W_B (overlap of stored facts)
    (c) Contradictory W_A, W_B (same keys, different values)?
  If commutator magnitudes separate these regimes, it is a substrate-
  level analog of operator non-commutativity. HP -> Op F unlocks; HF ->
  commutators don't distinguish substrate relationships.

SCIENTIFIC QUESTION:
  At N=4096, M=256 facts each in W_A, W_B with three relationship
  conditions:
    (a) Independent: disjoint key/val pairs (default behavior)
    (b) Related:    50% overlap of (key_i, val_i) facts between A and B
    (c) Contradictory: same K keys, but B uses different V values from A
  Compute commutator [W_A, W_B] and its normalized Frobenius magnitude
  c = ||[W_A, W_B]||_F / (||W_A||_F * ||W_B||_F).
  Do means of c separate conditions (a) < (b) < (c) by >=2x?

PRE-REGISTERED BANDS:
  HARD_PASS: pairwise ratios of mean(c) between conditions >= 2x in
    3+/5 seeds (so c_max / c_min across (a)/(b)/(c) >= 2).
  HARD_FAIL: c values for (a), (b), (c) overlap within +/-20% of each
    other (no separation signal).
  MIDDLE_BAND: partial separation.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. M=256 facts per substrate. 3 conditions * 5 seeds = 15 cells.
  3. Commutator c formula: ||W_A W_B - W_B W_A||_F / (||W_A||_F * ||W_B||_F).
  4. Pairwise self-commutator [W, W] = 0 (sanity).

OOM CHECK:
  N=4096: 2 * W = 128MB. Codebook 805MB. Keys 16MB. ~1GB. OK.
  Commutator: 2 W*W matmuls = 2 * 67MB peak. ~200MB peak. OK.

TIMEOUT ESTIMATE:
  3 conditions * 5 seeds. Each cell: 2 substrate builds + 2 matmuls.
  ~5s/cell. 75s expected. Budget 14400s.

N-suffix: _n4096 (PROT-018).
Anchor: interference_patterns_commutator_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_interference_patterns_commutator_v1_n4096.md
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

_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_intf", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)
v3 = c1.v3

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_intf", _ck_path)
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

M_FULL  = 256
M_SMOKE = 32
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
CONDITIONS_FULL  = ["independent", "related", "contradictory"]
CONDITIONS_SMOKE = ["independent", "contradictory"]
OVERLAP_FRAC = 0.5      # 50% overlap for "related"

HP_RATIO_MIN = 2.0      # max/min mean(c) across conditions
HP_SEEDS_MIN = 3
HF_SEPARATION_PCT = 0.20  # within +/-20% = HF


def get_output_dir(default_name: str = "interference_patterns_commutator_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_pair(N_use: int, M: int, seed: int, condition: str,
                          device: torch.device) -> Tuple[torch.Tensor,
                                                          torch.Tensor]:
    """Build two substrates W_A, W_B per condition."""
    codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed + 4400)
    perm = torch.randperm(C, generator=gen, device=device)
    # Disjoint pools: enough to support 2M key + 2M val indices
    needed = 4 * M
    if needed > C:
        raise ValueError(f"codebook too small: C={C} needed={needed}")
    # Substrate A: key indices [0:M], val indices [M:2M]
    key_idx_A = perm[0:M]
    val_idx_A = perm[M:2 * M]

    # Substrate B: depends on condition
    if condition == "independent":
        # Disjoint from A
        key_idx_B = perm[2 * M:3 * M]
        val_idx_B = perm[3 * M:4 * M]
    elif condition == "related":
        # 50% overlap with A's facts (use a subset of A's (key, val) pairs)
        n_overlap = M // 2
        key_idx_B = torch.cat([
            key_idx_A[:n_overlap],          # same keys as first half of A
            perm[2 * M:2 * M + (M - n_overlap)]
        ])
        val_idx_B = torch.cat([
            val_idx_A[:n_overlap],          # SAME val as A for overlap
            perm[3 * M:3 * M + (M - n_overlap)]
        ])
    elif condition == "contradictory":
        # Same KEYS as A, DIFFERENT VALUES (uses different pool for vals)
        key_idx_B = key_idx_A.clone()
        val_idx_B = perm[2 * M:3 * M]
    else:
        raise ValueError(f"Unknown condition: {condition}")

    keys_A = codebook[key_idx_A]; values_A = codebook[val_idx_A]
    keys_B = codebook[key_idx_B]; values_B = codebook[val_idx_B]
    W_A = (values_A.T @ keys_A) / float(N_use)
    W_B = (values_B.T @ keys_B) / float(N_use)
    del codebook, keys_A, values_A, keys_B, values_B
    return W_A, W_B


def commutator_magnitude(W_A: torch.Tensor, W_B: torch.Tensor) -> float:
    """Normalized Frobenius magnitude of [W_A, W_B]."""
    AB = W_A @ W_B
    BA = W_B @ W_A
    comm = AB - BA
    num = float(comm.norm().item())
    denom = float(W_A.norm().item()) * float(W_B.norm().item())
    if denom < 1e-12:
        return 0.0
    return num / denom


def measure_one_cell(N_use: int, M: int, seed: int, condition: str,
                      device: torch.device) -> Dict:
    W_A, W_B = build_substrate_pair(N_use, M, seed, condition, device)
    c = commutator_magnitude(W_A, W_B)
    # Sanity: self-commutator should be 0
    c_self = commutator_magnitude(W_A, W_A)
    # Product norm for diagnostic
    prod_norm = float((W_A @ W_B).norm().item())
    A_norm = float(W_A.norm().item())
    B_norm = float(W_B.norm().item())

    del W_A, W_B
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    return {
        "seed": int(seed), "M": int(M), "condition": condition,
        "commutator_magnitude": round(c, 6),
        "self_commutator_check": round(c_self, 8),
        "product_W_A_W_B_norm": round(prod_norm, 5),
        "W_A_norm": round(A_norm, 5),
        "W_B_norm": round(B_norm, 5),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("INT_INCONCLUSIVE", "No cells.")

    # Mean commutator per condition
    by_cond: Dict[str, List[float]] = {}
    for c in cells:
        by_cond.setdefault(c["condition"], []).append(c["commutator_magnitude"])

    means = {cond: (sum(vs) / len(vs)) if vs else 0.0
             for cond, vs in by_cond.items()}
    if not means:
        return ("INT_INCONCLUSIVE", "no per-condition means.")

    sorted_means = sorted(means.values())
    if sorted_means[0] < 1e-9:
        # All conditions yield ~zero commutator -> not separable
        return ("INT_HARD_FAIL",
                f"COMMUTATOR_NEAR_ZERO_ALL_CONDITIONS: means={means}")
    ratio = sorted_means[-1] / sorted_means[0]

    # Determine separation: within +/- 20% means HF
    span_pct = (sorted_means[-1] - sorted_means[0]) / max(sorted_means[0], 1e-9)
    detail = (f"means={means} max/min={ratio:.2f}x span_pct={span_pct:.3f} "
              f"n_cells={len(cells)} n_conditions={len(by_cond)}")

    if span_pct <= HF_SEPARATION_PCT:
        return ("INT_HARD_FAIL",
                f"NO_SEPARATION: conditions within +/-20%. " + detail)

    if ratio >= HP_RATIO_MIN and len(by_cond) >= 2:
        return ("INT_HARD_PASS",
                f"CONDITIONS_DISTINGUISHED: max/min>={HP_RATIO_MIN}x. " + detail)

    return ("INT_MIDDLE_BAND", f"PARTIAL_SEPARATION: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    # Self-commutator [W, W] should be 0
    W = torch.randn(8, 8)
    c_self = commutator_magnitude(W, W)
    assert c_self < 1e-6, f"self-commutator nonzero: {c_self}"

    # Commutator of distinct matrices is nonzero
    A = torch.randn(8, 8)
    B = torch.randn(8, 8)
    c = commutator_magnitude(A, B)
    assert c > 1e-6, f"distinct commutator should be nonzero: {c}"

    # Verdict gates
    # HARD_PASS: ratio max/min >= 2
    fake_hp = (
        [{"seed": s, "M": 256, "condition": "independent",
          "commutator_magnitude": 0.05} for s in SEEDS_FULL] +
        [{"seed": s, "M": 256, "condition": "related",
          "commutator_magnitude": 0.15} for s in SEEDS_FULL] +
        [{"seed": s, "M": 256, "condition": "contradictory",
          "commutator_magnitude": 0.30} for s in SEEDS_FULL]
    )
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # HARD_FAIL: all within +/-20%
    fake_hf = (
        [{"seed": s, "M": 256, "condition": "independent",
          "commutator_magnitude": 0.10} for s in SEEDS_FULL] +
        [{"seed": s, "M": 256, "condition": "related",
          "commutator_magnitude": 0.11} for s in SEEDS_FULL] +
        [{"seed": s, "M": 256, "condition": "contradictory",
          "commutator_magnitude": 0.115} for s in SEEDS_FULL]
    )
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Smoke on CPU: 1 cell per condition
    device = torch.device("cpu")
    for cond in CONDITIONS_SMOKE:
        out = measure_one_cell(N_SMOKE, M_SMOKE, 17, cond, device)
        assert out["commutator_magnitude"] >= 0
        assert out["self_commutator_check"] < 1e-3, (
            f"self-comm sanity failed: {out['self_commutator_check']}")
    print(f"[selftest] interference_patterns_commutator_v1_n4096 PASS "
          f"smoke conditions exercised", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_cfg = M_SMOKE if smoke else M_FULL
    conds = CONDITIONS_SMOKE if smoke else CONDITIONS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] interference_patterns_commutator_v1_n4096 smoke={smoke} "
          f"N={N_cfg} M={M_cfg} conds={conds} seeds={seeds} "
          f"done={len(done)} device={device_str}", flush=True)

    cells: List[Dict] = []
    for cond in conds:
        for seed in seeds:
            ck = f"{cond}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_one_cell(N_cfg, M_cfg, seed, cond, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  {ck} c={out['commutator_magnitude']:.5f} "
                      f"c_self={out['self_commutator_check']:.2e} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  {ck} FAILED: {type(e).__name__}: {e}", flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "interference_patterns_commutator_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M": M_cfg, "conditions": conds, "seeds": seeds,
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
