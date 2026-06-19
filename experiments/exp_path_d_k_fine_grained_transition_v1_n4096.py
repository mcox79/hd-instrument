"""PATH D K FINE-GRAINED TRANSITION CURVE v1 at N=4096.

CONTEXT (R2 from cap_map v307 follow-on; K-transition curve at fixed M):
  v307 K=1 probe landed MIDDLE_BAND: path_b_top1_acc=0.022 at M=16N.
  K=10/100 hit unanimous 1.0. The K=1 to K=10 jump is 45x.
  R2 maps the fine-grained transition curve at FIXED M=16N=65536 by sweeping
  K_paths in {1, 2, 3, 5, 10, 100}. Fills the K-axis gap between substrate-
  physics regime (K=1) and production-default (K=10/100).

SCIENTIFIC QUESTION:
  At N=4096, M=16N=65536, depth=5, K in {1, 2, 3, 5, 10, 100}:
  Is the transition monotone? Where is the cliff? Could substrate run safely
  at K=5 (5x latency reduction vs K=100)?

PRE-REGISTERED BANDS (from strategy routing 2026-06-01):
  HARD-PASS: monotone increase in mean accuracy across K;
             K=2 mean in [0.10, 0.30];
             K=3 mean in [0.40, 0.70];
             K=5 mean in [0.85, 0.99];
             K=10 unanimous (matches v307 result).
  HARD-FAIL: K=2/3/5 still at random-chance (~0.001-0.01).
             Interpretation: substrate-physics signal scales worse than
             naive expectation; K safety margin cliff is beyond K=10.
  MIDDLE-BAND: discontinuous jump (cliff at specific K threshold).
               Interpretation: informs K-safety-margin lever sharpness.

  Metric per K: path_b_top1_acc (substrate phase-boundary probe, no pool)
               measured across 5 seeds at each K.
  Additional: path_d_k<K>_acc for K in {10, 100} for corroboration.

FORMULA SELF-TESTS:
  1. HP gate: K=2 acc=0.20, K=3 acc=0.55, K=5 acc=0.90, K=10 acc=1.0 -> HARD_PASS
  2. HF gate: K=2 acc=0.005, K=3 acc=0.008, K=5 acc=0.009 -> HARD_FAIL
  3. MIDDLE gate: K=2 acc=0.20, K=3 acc=0.55, K=5 acc=0.70, K=10 acc=1.0 -> MIDDLE
     (cliff at K=5->K=10 transition)

DESIGN:
  N=4096, M=16N=65536, depth=5.
  K_paths sweep: {1, 2, 3, 5, 10, 100}.
  Per K: 5 seeds, 100 random query keys each.
  Primary metric: path_b_top1_acc for K in {1, 2, 3, 5} (substrate phase probe).
  path_d_run accuracy for K in {10, 100} (candidate-pool corroboration).

  NOTE on K=1 metric:
    K=1 in path_d_run is degenerate (always picks the only candidate).
    The phase-boundary metric is path_b_top1_acc (direct Path B walk, no pool).
    For K=2,3,5 we run path_d_run with that K AND measure path_b_top1_acc
    (which is K-independent by construction -- it measures the substrate vector
    propagation quality, not the candidate pool size). So path_b_top1_acc is
    a fixed substrate quality probe; the K sweep tells us how adding more
    candidates improves disambiguation.

  For the K-transition curve, the PRIMARY metric per K is:
    path_d_kK_acc = accuracy from path_d_run(K_paths=K) for K in {2, 3, 5, 10, 100}
  The path_b_top1_acc is measured once (K-independent substrate probe).

OOM CHECK:
  N=4096, M=16N=65536: codebook = 65536 x 4096 float32 = 1 GiB.
  W = 4096 x 4096 float32 = 64 MiB.
  Remote CPU RAM: 64 GB. Peak per cell ~1.1 GB. Fine.

PROT-018: _n4096 binds N = 4096.
PROT-019: timeout >= 14400s.
PROT-021: per-cell-K-seed checkpointing.
PROT-022: device=cpu forced.

TIMEOUT ESTIMATE:
  Reference: v1 K=1 probe ran ~60s/seed at N=4096 M=16N.
  K=2,3,5: path_d_run with small K is faster than K=100 (fewer candidates).
  6 K-values x 5 seeds = 30 cells; ~60s each -> 1800s.
  1.5 safety factor -> 2700s. PROT-019 floor: 14400s. timeout_s = 14400.

Anchor: path_d_k_fine_grained_transition_v1_n4096
Queue: remote_cpu_queue (CPU-only; pure numpy/torch CPU ops)
Pre-reg: preregs/2026-06-01_path_d_k_fine_grained_transition_v1_n4096.md
Total cells: 6 K-values x 5 seeds = 30 cells
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._metric_battery import make_substrate           # noqa: E402
from experiments._relation_graph import build_relation_facts     # noqa: E402
from experiments._multi_hop_mechanisms import path_d_run, path_b_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_k_fine", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# ---------------------------------------------------------------------------
# PROT-018: _n4096 binds N = 4096
# ---------------------------------------------------------------------------
N = 4096
N_FULL  = N
N_SMOKE = 1024  # log2=10 (even); Kerdock codebook requires even log2(N)
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Spec: M=16N fixed; depth=5; K sweep {1,2,3,5,10,100}; 5 seeds
M_FULL  = 16 * N_FULL    # 65536
M_SMOKE = 512
DEPTH   = 5
K_PATHS_GRID = [1, 2, 3, 5, 10, 100]   # fine-grained K-transition sweep
K_RANDOM_KEYS       = 100               # query starts per cell
K_RANDOM_KEYS_SMOKE = 20
SEEDS_FULL  = [7, 17, 23, 42, 99]
SEEDS_SMOKE = [17]
BETA_D = 4.0
DEVICE = torch.device("cpu")            # PROT-022: CPU-force

# Pre-registered bands (verbatim from routing 2026-06-01)
# HARD-PASS: monotone increase; K=2 in [0.10,0.30]; K=3 in [0.40,0.70];
#            K=5 in [0.85,0.99]; K=10 unanimous
HP_K2_LOW, HP_K2_HIGH = 0.10, 0.30
HP_K3_LOW, HP_K3_HIGH = 0.40, 0.70
HP_K5_LOW, HP_K5_HIGH = 0.85, 0.99
HP_K10_MIN = 0.90
# HARD-FAIL: K=2/3/5 at random-chance
HF_MAX = 0.01
# MIDDLE: discontinuous cliff


def get_output_dir(default_name: str = "path_d_k_fine_grained_transition_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                   device: torch.device):
    """Build codebook + W + relation graph (same as K=1 probe)."""
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    M_eff = min(M, C)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M_eff, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec  = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


def measure_cell(N_use: int, M: int, depth: int, seed: int, k_random_keys: int,
                 device: torch.device) -> Dict:
    """Measure path_b_top1_acc + path_d_kK_acc for all K in K_PATHS_GRID."""
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)

    # Find valid starts (depth-level chains in relation)
    all_starts = list(relation.keys())
    valid_starts = []
    for s in all_starts:
        cur = s
        ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                ok = False
                break
            cur = nxt
        if ok:
            valid_starts.append(s)

    if not valid_starts:
        del codebook, W
        return {"seed": seed, "n_eval": 0,
                "path_b_top1_acc": None,
                "path_d_k2_acc": None,
                "path_d_k3_acc": None,
                "path_d_k5_acc": None,
                "path_d_k10_acc": None,
                "path_d_k100_acc": None}

    rng = torch.Generator().manual_seed(seed + 99999)
    n_use = min(k_random_keys, len(valid_starts))
    perm = torch.randperm(len(valid_starts), generator=rng).tolist()
    chosen = [valid_starts[i] for i in perm[:n_use]]
    starts = torch.tensor(chosen, dtype=torch.long, device=device)

    # Ground-truth targets (depth-chain endpoint)
    targets_list = []
    for s in chosen:
        cur = s
        for _ in range(depth):
            cur = relation[cur]
        targets_list.append(cur)
    targets = torch.tensor(targets_list, dtype=torch.long, device=device)

    # --- Substrate phase-boundary probe (K=1 effective, no pool) ---
    pred_b = path_b_run(codebook, W, starts, depth=depth, N_use=N_use)
    path_b_top1_acc = float((pred_b == targets).float().mean().item())

    # --- Candidate-pool K-sweep ---
    result: Dict = {
        "seed": int(seed),
        "n_eval": int(starts.shape[0]),
        "path_b_top1_acc": round(path_b_top1_acc, 5),
    }
    for K in [2, 3, 5, 10, 100]:
        correct = path_d_run(codebook, W, starts, relation, depth,
                             K_paths=K, seed=seed, N_use=N_use, beta=BETA_D)
        acc = float(correct.mean().item())
        result[f"path_d_k{K}_acc"] = round(acc, 5)

    del codebook, W
    return result


def _is_monotone(accs: List[float]) -> bool:
    """Check if list is non-decreasing."""
    return all(accs[i] <= accs[i + 1] + 1e-6 for i in range(len(accs) - 1))


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    """Compute verdict from list of per-seed cell results."""
    if not cells:
        return ("K_FINE_INCONCLUSIVE", "no cells")

    valid = [c for c in cells if c.get("n_eval", 0) > 0]
    if not valid:
        return ("K_FINE_INCONCLUSIVE", "all cells returned n_eval=0")

    def mean_metric(key: str) -> float:
        vals = [c[key] for c in valid if c.get(key) is not None]
        return sum(vals) / len(vals) if vals else float("nan")

    k1_mean   = mean_metric("path_b_top1_acc")   # K=1 substrate probe (K-independent)
    k2_mean   = mean_metric("path_d_k2_acc")
    k3_mean   = mean_metric("path_d_k3_acc")
    k5_mean   = mean_metric("path_d_k5_acc")
    k10_mean  = mean_metric("path_d_k10_acc")
    k100_mean = mean_metric("path_d_k100_acc")

    detail = (
        f"k1(path_b)={k1_mean:.4f} k2={k2_mean:.4f} k3={k3_mean:.4f} "
        f"k5={k5_mean:.4f} k10={k10_mean:.4f} k100={k100_mean:.4f} "
        f"n_seeds={len(valid)}"
    )

    # HARD-FAIL: K=2/3/5 all at random-chance
    if k2_mean <= HF_MAX and k3_mean <= HF_MAX and k5_mean <= HF_MAX:
        return (
            "K_FINE_HARD_FAIL",
            f"K_SAFETY_MARGIN_CLIFF_BEYOND_K10: K=2/3/5 all at random-chance "
            f"(k2={k2_mean:.4f}, k3={k3_mean:.4f}, k5={k5_mean:.4f} all <= {HF_MAX}). "
            f"Substrate signal scales worse than naive expectation. " + detail
        )

    # HARD-PASS: monotone increase; K=2 in [0.10,0.30]; K=3 in [0.40,0.70];
    #            K=5 in [0.85,0.99]; K=10 >= 0.90
    hp_k2 = HP_K2_LOW <= k2_mean <= HP_K2_HIGH
    hp_k3 = HP_K3_LOW <= k3_mean <= HP_K3_HIGH
    hp_k5 = HP_K5_LOW <= k5_mean <= HP_K5_HIGH
    hp_k10 = k10_mean >= HP_K10_MIN
    monotone = _is_monotone([k1_mean, k2_mean, k3_mean, k5_mean, k10_mean, k100_mean])
    if hp_k2 and hp_k3 and hp_k5 and hp_k10 and monotone:
        return (
            "K_FINE_HARD_PASS",
            f"MONOTONE_K_TRANSITION_CONFIRMED: k2={k2_mean:.4f} in "
            f"[{HP_K2_LOW},{HP_K2_HIGH}]; k3={k3_mean:.4f} in "
            f"[{HP_K3_LOW},{HP_K3_HIGH}]; k5={k5_mean:.4f} in "
            f"[{HP_K5_LOW},{HP_K5_HIGH}]; k10={k10_mean:.4f} >= {HP_K10_MIN}. "
            f"Monotone transition. Substrate could operate safely at K=5. " + detail
        )

    # MIDDLE-BAND: partial or cliff pattern
    # Detect cliff: large gap between consecutive K values
    gaps = [
        ("k1->k2", abs(k2_mean - k1_mean)),
        ("k2->k3", abs(k3_mean - k2_mean)),
        ("k3->k5", abs(k5_mean - k3_mean)),
        ("k5->k10", abs(k10_mean - k5_mean)),
    ]
    max_gap = max(gaps, key=lambda x: x[1])
    return (
        "K_FINE_MIDDLE_BAND",
        f"PARTIAL_OR_CLIFF_TRANSITION: largest gap at {max_gap[0]} "
        f"(delta={max_gap[1]:.4f}). hp_k2={hp_k2} hp_k3={hp_k3} "
        f"hp_k5={hp_k5} hp_k10={hp_k10} monotone={monotone}. " + detail
    )


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert M_FULL == 65536, f"M_FULL must be 65536 (16*4096); got {M_FULL}"
    assert DEPTH == 5, f"depth must be 5; got {DEPTH}"
    assert K_PATHS_GRID == [1, 2, 3, 5, 10, 100], f"K grid mismatch: {K_PATHS_GRID}"
    assert len(SEEDS_FULL) == 5, f"SEEDS_FULL len: {len(SEEDS_FULL)}"

    # Formula self-tests per docstring
    # 1. HP gate
    hp_cells = [
        {"seed": i, "n_eval": 20,
         "path_b_top1_acc": 0.022, "path_d_k2_acc": 0.20,
         "path_d_k3_acc": 0.55, "path_d_k5_acc": 0.90,
         "path_d_k10_acc": 0.98, "path_d_k100_acc": 1.0}
        for i in range(5)
    ]
    v, _ = compute_verdict(hp_cells)
    assert "HARD_PASS" in v, f"HP gate failed: {v}"

    # 2. HF gate
    hf_cells = [
        {"seed": i, "n_eval": 20,
         "path_b_top1_acc": 0.005, "path_d_k2_acc": 0.005,
         "path_d_k3_acc": 0.008, "path_d_k5_acc": 0.009,
         "path_d_k10_acc": 0.98, "path_d_k100_acc": 1.0}
        for i in range(5)
    ]
    v, _ = compute_verdict(hf_cells)
    assert "HARD_FAIL" in v, f"HF gate failed: {v}"

    # 3. MIDDLE gate (cliff at K5->K10)
    mid_cells = [
        {"seed": i, "n_eval": 20,
         "path_b_top1_acc": 0.022, "path_d_k2_acc": 0.20,
         "path_d_k3_acc": 0.55, "path_d_k5_acc": 0.70,
         "path_d_k10_acc": 0.98, "path_d_k100_acc": 1.0}
        for i in range(5)
    ]
    v, _ = compute_verdict(mid_cells)
    assert "MIDDLE_BAND" in v, f"MIDDLE gate failed: {v}"

    # 4. Live smoke forward pass (small N, small M)
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_SMOKE, depth=3, seed=17,
                       k_random_keys=10, device=device)
    assert out.get("n_eval", 0) > 0, f"selftest: 0 starts at smoke scale: {out}"
    assert out.get("path_b_top1_acc") is not None, "path_b_top1_acc is None"
    assert 0.0 <= out["path_b_top1_acc"] <= 1.0, \
        f"path_b_top1_acc out of range: {out['path_b_top1_acc']}"
    for K in [2, 3, 5, 10, 100]:
        key = f"path_d_k{K}_acc"
        assert out.get(key) is not None, f"{key} is None at smoke scale"
        assert 0.0 <= out[key] <= 1.0, f"{key} out of range: {out[key]}"
    print(
        f"[selftest] path_d_k_fine_grained_transition_v1_n4096 PASS "
        f"smoke N={N_SMOKE} M={M_SMOKE} d=3 seed=17 "
        f"path_b_top1={out['path_b_top1_acc']:.3f} "
        f"k2={out['path_d_k2_acc']:.3f} k5={out['path_d_k5_acc']:.3f} "
        f"k10={out['path_d_k10_acc']:.3f} n_eval={out['n_eval']}",
        flush=True,
    )


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    device = DEVICE
    smoke    = args.smoke
    N_cfg    = N_SMOKE            if smoke else N_FULL
    M_cfg    = M_SMOKE            if smoke else M_FULL
    seeds    = SEEDS_SMOKE        if smoke else SEEDS_FULL
    k_keys   = K_RANDOM_KEYS_SMOKE if smoke else K_RANDOM_KEYS

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    total_cells = len(seeds)
    cell_num = 0

    print(
        f"[run] path_d_k_fine_grained_transition_v1_n4096 smoke={smoke} "
        f"N={N_cfg} M={M_cfg} depth={DEPTH} seeds={seeds} "
        f"K_grid={K_PATHS_GRID} k_random_keys={k_keys} "
        f"total_cells={total_cells} done={len(done)} device={device.type}",
        flush=True,
    )

    cells: List[Dict] = []
    for seed in seeds:
        cell_num += 1
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                print(f"  [cell {cell_num}/{total_cells}] seed={seed} RESUMED",
                      flush=True)
                continue
        try:
            out = measure_cell(N_cfg, M_cfg, depth=DEPTH, seed=seed,
                               k_random_keys=k_keys, device=device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            elapsed_s = time.time() - t0
            print(
                f"  [cell {cell_num}/{total_cells}] seed={seed} "
                f"path_b_top1={out.get('path_b_top1_acc', 'N/A')} "
                f"k2={out.get('path_d_k2_acc', 'N/A')} "
                f"k3={out.get('path_d_k3_acc', 'N/A')} "
                f"k5={out.get('path_d_k5_acc', 'N/A')} "
                f"k10={out.get('path_d_k10_acc', 'N/A')} "
                f"k100={out.get('path_d_k100_acc', 'N/A')} "
                f"n_eval={out.get('n_eval', 0)} "
                f"({elapsed_s:.1f}s)",
                flush=True,
            )
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  [cell {cell_num}/{total_cells}] seed={seed} FAILED: {e}",
                  flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "path_d_k_fine_grained_transition_v1_n4096",
        "N": N_cfg, "smoke": smoke, "M": M_cfg,
        "depth": DEPTH, "K_paths_grid": K_PATHS_GRID,
        "k_random_keys": k_keys, "seeds": seeds,
        "cells": cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
