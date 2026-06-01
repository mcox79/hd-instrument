"""PATH D K=1 PHASE BOUNDARY PROBE v1 at N=4096.

CONTEXT (percolation-theory Phase-D K-trivialization diagnostic):
  Path D's validated "no-ceiling at M=64N depth=50" envelope (cap_map v297+v299
  LIFTs) uses K_paths=100 candidates. At K=100, p_eff = K/M = 3.8e-4 at M=64N
  is 100x above the ER percolation threshold 1/M. The validated envelope may be
  operating entirely in the candidate-safety-margin regime rather than the
  substrate-physics regime.

SCIENTIFIC QUESTION:
  At N=4096, M=16N=65536, depth=5, sweeping K_paths in {1, 10, 100}:
  Does K=1 retrieval show graceful degradation (substantive accuracy in
  [0.50, 0.95] but > random = 0.0033)?  Or does K=1 already hit random-chance
  (substrate Path D operating entirely in safety-margin regime)?

PRE-REGISTERED BANDS:
  HP = K=1 accuracy in [0.50, 0.95]; K=10 closes most of gap to K=100;
       K=100 hits unanimous-consistent (>= 0.90).
       Interpretation: substrate-physics signal present; Path D envelope is
       partially substrate-physics, not pure K-safety-margin.
  HF = K=1 accuracy in [0.001, 0.01] (random-chance band).
       Interpretation: substrate Path D was operating entirely in the
       candidate-safety-margin regime; Path D production-default sub-row
       P-band should be substantially dropped.
  MIDDLE = K=1 accuracy in (0.01, 0.50).
           Interpretation: partial substrate-physics signal; characterizable.

  Note: random baseline = 1/K = 1/1 = 1.0 for K=1 degenerate (only 1 path,
  always selected). The REAL baseline question at K=1 is whether the Bayesian
  log-likelihood correctly scores the coherent path ABOVE random codebook
  vectors. With K=1 there are no decoys -- path_d_run returns 1.0 (always
  picks the only candidate). To actually probe the phase boundary, K_random
  query count probes whether DIFFERENT random query keys return accurate
  reconstructions.  See experimental design note below.

EXPERIMENTAL DESIGN:
  K_paths sweeps {1, 10, 100} independently per (seed, K_random_keys) cell.
  K_random_keys = 100 random codebook indices used as query starts per cell.
  For each query start, build the coherent depth-5 path from the relation
  graph. For K_paths=1: only the true path is evaluated (the log-posterior
  over 1 candidate always picks that candidate, so accuracy = 1.0 trivially).
  This is NOT the right probe. Instead, for K=1, we measure: given a random
  codebook index q as query, does depth-5 Path D walk arrive at a codebook
  atom within the TOP-1 nearest neighbour of the ground-truth destination?
  I.e., direct top-1 retrieval after K=1 Bayesian walk from a random start
  toward the stored relation endpoint.

  Concretely:
  - K_paths = 1: run path_d_run(... K_paths=1) which forces path_d_run to
    only sample decoys=0 (no negative paths). The function returns 1.0 per
    start because it always picks the only candidate. This is a degenerate
    probe of K=1.
  - True K=1 phase boundary probe: for each query start s, walk s depth=5
    steps using Path B (no candidate pool), then measure whether the final
    embedding cosine-similarity to the ground-truth destination is above
    threshold (top-1 NN in the codebook).

  RESOLUTION: run BOTH probes per K value:
  (a) path_d_run(K_paths=K) -- standard accuracy metric (candidate-pool probe)
  (b) path_b_run top-1 accuracy -- direct substrate phase boundary probe
      (no candidate pool; pure vector propagation)

  For the K-sweep interpretation:
  - path_d_k1_acc = acc from path_d_run(K_paths=1) -- always 1.0 (degenerate)
  - path_b_top1_acc = acc from path_b_run at depth=5 -- THIS is the phase
    boundary probe (what fraction of random starts can Path D substrate
    propagate to correct endpoint without any candidate pool)
  - path_d_k10_acc, path_d_k100_acc = standard candidate-pool accuracy

  PRIMARY METRIC: path_b_top1_acc (substrate phase boundary at K=1 effective)
  SECONDARY: path_d_k10_acc, path_d_k100_acc (candidate-pool behavior)

PROT-018: _n4096 binds N = 4096.
PROT-021: per-cell-seed checkpointing.
PROT-022: device=cpu forced (N=4096 CPU-safe; GPU queue has 2 pending).

OOM CHECK:
  N=4096: W = 4096x4096 float32 = 64 MiB. Codebook = M=16N=65536 x 4096
  = 1 GiB. Well under any constraint (8 GiB CPU RAM budget).

Anchor: path_d_k1_phase_boundary_probe_v1_n4096
Queue: remote_cpu_queue (routing spec: ~30-60min CPU)
Pre-reg: preregs/2026-06-01_path_d_k1_phase_boundary_probe_v1_n4096.md
Total cells: 3 K-values x 5 seeds = 15 cells
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_k1_phase", _ck_path)
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
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Spec: M=16N fixed; depth=5; K sweep {1, 10, 100}; 5 seeds
M_FULL  = 16 * N_FULL    # 65536
M_SMOKE = 512
DEPTH   = 5
K_PATHS_GRID = [1, 10, 100]   # K_paths sweep
K_RANDOM_KEYS = 100            # number of query starts per cell
SEEDS_FULL  = [7, 17, 23, 42, 99]
SEEDS_SMOKE = [17]
BETA_D = 4.0
DEVICE = torch.device("cpu")   # PROT-022: CPU-force

# Pre-registered bands (verbatim from spec)
# HP: path_b_top1_acc (K=1 phase boundary) in [0.50, 0.95]
#     + path_d_k100_acc >= 0.90
HP_K1_LOW  = 0.50
HP_K1_HIGH = 0.95
HP_K100_MIN = 0.90
# HF: path_b_top1_acc in [0.001, 0.01] (random-chance)
HF_K1_LOW  = 0.001
HF_K1_HIGH = 0.01
# MIDDLE: path_b_top1_acc in (0.01, 0.50)
MB_K1_LOW  = 0.01
MB_K1_HIGH = 0.50


def get_output_dir(default_name: str = "path_d_k1_phase_boundary_probe_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                   device: torch.device):
    """Build codebook + W + relation (same construction as G7/G7EXT)."""
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    M_eff = min(M, C)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M_eff, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec  = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


def measure_cell_k_sweep(N_use: int, M: int, depth: int, seed: int,
                          k_random_keys: int, device: torch.device) -> Dict:
    """Measure path_b_top1_acc + path_d_k10_acc + path_d_k100_acc for one seed."""
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    C = codebook.shape[0]

    # Sample k_random_keys starts from relation keys that have depth-5 paths
    all_starts_in_relation = list(relation.keys())
    # Filter: must have depth-5 coherent path
    valid_starts = []
    for s in all_starts_in_relation:
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
                "path_b_top1_acc": 0.0,
                "path_d_k10_acc": 0.0,
                "path_d_k100_acc": 0.0}

    # Cap to k_random_keys; deterministic selection from seed
    rng = torch.Generator().manual_seed(seed + 99999)
    n_use = min(k_random_keys, len(valid_starts))
    perm = torch.randperm(len(valid_starts), generator=rng).tolist()
    chosen = [valid_starts[i] for i in perm[:n_use]]
    starts = torch.tensor(chosen, dtype=torch.long, device=device)

    # Build ground-truth targets for each start (depth-5 chain endpoint)
    targets_list = []
    for s in chosen:
        cur = s
        for _ in range(depth):
            cur = relation[cur]
        targets_list.append(cur)
    targets = torch.tensor(targets_list, dtype=torch.long, device=device)

    # --- Phase boundary probe: Path B top-1 (K=1 effective, no pool) ---
    t0 = time.perf_counter_ns()
    pred_b = path_b_run(codebook, W, starts, depth=depth, N_use=N_use)
    lat_b_ns = time.perf_counter_ns() - t0
    path_b_top1_acc = float((pred_b == targets).float().mean().item())

    # --- Candidate-pool probes: K=10, K=100 ---
    t1 = time.perf_counter_ns()
    correct_k10 = path_d_run(codebook, W, starts, relation, depth,
                              K_paths=10, seed=seed, N_use=N_use, beta=BETA_D)
    lat_k10_ns = time.perf_counter_ns() - t1
    path_d_k10_acc = float(correct_k10.mean().item())

    t2 = time.perf_counter_ns()
    correct_k100 = path_d_run(codebook, W, starts, relation, depth,
                               K_paths=100, seed=seed, N_use=N_use, beta=BETA_D)
    lat_k100_ns = time.perf_counter_ns() - t2
    path_d_k100_acc = float(correct_k100.mean().item())

    del codebook, W

    return {
        "seed": int(seed),
        "n_eval": int(starts.shape[0]),
        "path_b_top1_acc": round(path_b_top1_acc, 5),
        "path_d_k10_acc": round(path_d_k10_acc, 5),
        "path_d_k100_acc": round(path_d_k100_acc, 5),
        "lat_b_ns": int(lat_b_ns),
        "lat_k10_ns": int(lat_k10_ns),
        "lat_k100_ns": int(lat_k100_ns),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("K1_PHASE_INCONCLUSIVE", "no cells")

    valid = [c for c in cells if c.get("n_eval", 0) > 0]
    if not valid:
        return ("K1_PHASE_INCONCLUSIVE", "all cells returned n_eval=0")

    k1_accs = [c["path_b_top1_acc"] for c in valid]
    k10_accs = [c["path_d_k10_acc"] for c in valid]
    k100_accs = [c["path_d_k100_acc"] for c in valid]

    k1_mean  = sum(k1_accs) / len(k1_accs)
    k10_mean = sum(k10_accs) / len(k10_accs)
    k100_mean = sum(k100_accs) / len(k100_accs)

    n_valid = len(valid)
    detail = (
        f"k1(path_b_top1)={k1_mean:.4f} "
        f"k10={k10_mean:.4f} "
        f"k100={k100_mean:.4f} "
        f"n_seeds={n_valid}"
    )

    # HF: K=1 at random-chance (path_b_top1 in [0.001, 0.01])
    if HF_K1_LOW <= k1_mean <= HF_K1_HIGH:
        return (
            "K1_PHASE_HARD_FAIL",
            f"PATH_D_PURE_K_SAFETY_MARGIN: k1_mean={k1_mean:.4f} in "
            f"[{HF_K1_LOW},{HF_K1_HIGH}] random-chance band. "
            f"Path D envelope is entirely K-safety-margin, not substrate-physics. "
            + detail
        )

    # HP: K=1 in [0.50, 0.95] AND K=100 >= 0.90
    if HP_K1_LOW <= k1_mean <= HP_K1_HIGH and k100_mean >= HP_K100_MIN:
        return (
            "K1_PHASE_HARD_PASS",
            f"PATH_D_SUBSTRATE_PHYSICS_CONFIRMED: k1_mean={k1_mean:.4f} in "
            f"[{HP_K1_LOW},{HP_K1_HIGH}] (substantive). "
            f"K=10 closes gap: k10={k10_mean:.4f}. "
            f"K=100 unanimous: k100={k100_mean:.4f}. "
            + detail
        )

    # MIDDLE: K=1 in (0.01, 0.50) -- partial substrate-physics signal
    if MB_K1_LOW < k1_mean < MB_K1_HIGH:
        return (
            "K1_PHASE_MIDDLE_BAND",
            f"PATH_D_PARTIAL_SUBSTRATE_SIGNAL: k1_mean={k1_mean:.4f} in "
            f"({MB_K1_LOW},{MB_K1_HIGH}). "
            f"Partial substrate-physics; characterizable. "
            + detail
        )

    # K=1 < 0.001 (below even random-chance band) -- extreme failure
    if k1_mean < HF_K1_LOW:
        return (
            "K1_PHASE_HARD_FAIL",
            f"PATH_D_BELOW_RANDOM_CHANCE: k1_mean={k1_mean:.4f} < {HF_K1_LOW}. "
            f"Substrate-physics entirely absent at K=1 equivalent. "
            + detail
        )

    # K=1 > 0.95 -- unexpectedly high at K=1 (stronger than HP expected)
    if k1_mean > HP_K1_HIGH:
        return (
            "K1_PHASE_HARD_PASS",
            f"PATH_D_STRONG_SUBSTRATE_PHYSICS: k1_mean={k1_mean:.4f} > {HP_K1_HIGH} "
            f"(above HP upper bound; substrate physics stronger than expected). "
            + detail
        )

    # Default: middle-band catchall
    return (
        "K1_PHASE_MIDDLE_BAND",
        f"PATH_D_PARTIAL_SIGNAL_CATCHALL: k1_mean={k1_mean:.4f}. " + detail
    )


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert M_FULL == 65536, f"M_FULL must be 65536 (16*4096); got {M_FULL}"
    assert DEPTH == 5, f"depth must be 5; got {DEPTH}"
    assert K_PATHS_GRID == [1, 10, 100]
    assert len(SEEDS_FULL) == 5

    # Verdict gate checks
    # HP: k1=0.70, k100=0.92
    hp_cells = [{"path_b_top1_acc": 0.70, "path_d_k10_acc": 0.85,
                  "path_d_k100_acc": 0.92, "n_eval": 10}] * 5
    v, _ = compute_verdict(hp_cells)
    assert "HARD_PASS" in v, f"HP gate failed: {v}"

    # HF: k1=0.005 (random-chance band)
    hf_cells = [{"path_b_top1_acc": 0.005, "path_d_k10_acc": 0.10,
                  "path_d_k100_acc": 0.92, "n_eval": 10}] * 5
    v, _ = compute_verdict(hf_cells)
    assert "HARD_FAIL" in v, f"HF gate failed: {v}"

    # MIDDLE: k1=0.25
    mb_cells = [{"path_b_top1_acc": 0.25, "path_d_k10_acc": 0.60,
                  "path_d_k100_acc": 0.92, "n_eval": 10}] * 5
    v, _ = compute_verdict(mb_cells)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v}"

    # Inconclusive: no cells
    v, _ = compute_verdict([])
    assert "INCONCLUSIVE" in v, f"Inconclusive gate failed: {v}"

    # Live smoke forward pass (small N, small M)
    device = torch.device("cpu")
    out = measure_cell_k_sweep(N_SMOKE, M_SMOKE, depth=3, seed=17,
                                k_random_keys=10, device=device)
    assert out.get("n_eval", 0) > 0, f"selftest produced 0 starts: {out}"
    assert 0.0 <= out["path_b_top1_acc"] <= 1.0, \
        f"path_b_top1_acc out of range: {out['path_b_top1_acc']}"
    assert 0.0 <= out["path_d_k10_acc"] <= 1.0, \
        f"path_d_k10_acc out of range: {out['path_d_k10_acc']}"
    assert 0.0 <= out["path_d_k100_acc"] <= 1.0, \
        f"path_d_k100_acc out of range: {out['path_d_k100_acc']}"
    print(
        f"[selftest] path_d_k1_phase_boundary_probe_v1_n4096 PASS "
        f"smoke N={N_SMOKE} M={M_SMOKE} d=3 seed=17 "
        f"path_b_top1={out['path_b_top1_acc']:.3f} "
        f"k10={out['path_d_k10_acc']:.3f} "
        f"k100={out['path_d_k100_acc']:.3f} "
        f"n_eval={out['n_eval']}",
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

    # PROT-022: CPU force (M=16N=65536 * N=4096 = 1 GiB codebook -- fits CPU RAM)
    device = DEVICE
    smoke   = args.smoke
    N_cfg   = N_SMOKE       if smoke else N_FULL
    M_cfg   = M_SMOKE       if smoke else M_FULL
    seeds   = SEEDS_SMOKE   if smoke else SEEDS_FULL
    k_keys  = 20            if smoke else K_RANDOM_KEYS

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    total_cells = len(seeds)
    cell_num = 0
    print(
        f"[run] path_d_k1_phase_boundary_probe_v1_n4096 smoke={smoke} "
        f"N={N_cfg} M={M_cfg} depth={DEPTH} seeds={seeds} "
        f"k_random_keys={k_keys} total_cells={total_cells} "
        f"done={len(done)} device={device.type}",
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
            out = measure_cell_k_sweep(N_cfg, M_cfg, depth=DEPTH, seed=seed,
                                        k_random_keys=k_keys, device=device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            elapsed_s = time.time() - t0
            print(
                f"  [cell {cell_num}/{total_cells}] seed={seed} "
                f"path_b_top1={out.get('path_b_top1_acc', 'N/A')} "
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
        "anchor": "path_d_k1_phase_boundary_probe_v1_n4096",
        "N": N_cfg, "smoke": smoke, "M": M_cfg,
        "depth": DEPTH, "K_paths_grid": K_PATHS_GRID, "seeds": seeds,
        "k_random_keys": k_keys,
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
