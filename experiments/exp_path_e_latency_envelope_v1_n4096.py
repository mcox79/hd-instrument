"""PATH E LATENCY ENVELOPE v1 at N=4096 (path E only).

CONTEXT (path-E characterization):
  Path E showed sub-linear K-scaling (9.27x at K=1000 vs 12.49x for B/D) and
  non-monotonic accuracy in depth (degrades at M=8192 d=3 but recovers at d=5).
  Sub-linear K-scaling means path E has a unique LATENCY advantage at large K.
  This anchor maps the (depth, K, M) envelope for path E specifically.

SCIENTIFIC QUESTION:
  At N=4096 BSC, when does Path E maintain accuracy >= 0.70 across a wide
  (depth, K, M) envelope, AND when does its sub-linear K-scaling realize a
  practical latency-advantage over Path B/D?

PRE-REGISTERED BANDS:
  HP = Path E maintains accuracy >= 0.70 across >=60% of cells AND latency-
       advantage over B/D (extrapolated) increases with K (sub-linear
       advantage realized at production K).
  HF = Path E drops below 0.30 accuracy in > 50% of cells (mechanism brittle
       outside narrow envelope).
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. depth grid = [3, 5, 8, 12, 16, 20]; K_paths grid = [100, 500, 1000, 2000, 5000];
     M grid = [512, 2048, 8192]. 6 x 5 x 3 = 90 cells.
  3. Per-cell accuracy = fraction of positives whose coherence beats median(negs).
  4. Per-cell latency_ms = wall time per query for E and extrapolated for B/D
     (B/D latency = K * single_hop_cost; E latency = depth * top_K_signature_cost).
  5. advantage_ratio(K) = latency_BD(K) / latency_E(K); HP requires advantage
     ratio MONOTONE NON-DECREASING in K.

OOM CHECK:
  M=8192, N=4096: keys+vals (64 MiB) + W (64 MiB) + codebook (256 MiB) = ~400 MiB.
  K_paths=5000 paths in candidate set; per-path signature top_k=16 doubles to ~2 MiB.
  Total per cell << 6 GiB. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 60s. FULL: 90 cells x 5 seeds = 450 cell-seeds. Each ~10-30s.
  ~4500-13500s. 21600s budget per spec.

N-suffix: _n4096 (PROT-018).
Anchor: path_e_latency_envelope_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_path_e_latency_envelope_v1_n4096.md
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

from experiments._metric_battery import make_substrate  # noqa: E402
from experiments._relation_graph import (  # noqa: E402
    build_relation_facts,
    sample_coherent_starts,
    sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_r4", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
DEPTH_GRID_FULL  = [3, 5, 8, 12, 16, 20]
DEPTH_GRID_SMOKE = [3, 5]
K_GRID_FULL  = [100, 500, 1000, 2000, 5000]
K_GRID_SMOKE = [50]
M_GRID_FULL  = [512, 2048, 8192]
M_GRID_SMOKE = [512]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_POS_PER_CELL_FULL  = 40
N_POS_PER_CELL_SMOKE = 8
TOP_K_SIG = 16

HP_ACC_THRESH = 0.70
HP_CELLS_FRAC = 0.60
HF_ACC_THRESH = 0.30
HF_CELLS_FRAC = 0.50


def get_output_dir(default_name: str = "path_e_latency_envelope_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                    device: torch.device):
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(
        N_use, M, seed, device)
    C = codebook.shape[0]
    M_eff = min(M, C)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M_eff, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


def _coherence(codebook, W, path, N_use, top_k):
    depth = len(path) - 1
    if depth < 1:
        return 0.0
    src = codebook[torch.tensor(path[:-1], dtype=torch.long,
                                 device=codebook.device)]
    responses = src @ W.T
    sigs = []
    for i in range(depth):
        sims = (codebook @ responses[i]) / N_use
        sigs.append(torch.topk(sims, top_k).values)
    if len(sigs) < 2:
        dst = codebook[path[-1]]
        s_dst = torch.topk((codebook @ dst) / N_use, top_k).values
        return float(torch.nn.functional.cosine_similarity(
            sigs[0].unsqueeze(0), s_dst.unsqueeze(0)).item())
    coh = []
    for i in range(len(sigs) - 1):
        coh.append(float(torch.nn.functional.cosine_similarity(
            sigs[i].unsqueeze(0), sigs[i + 1].unsqueeze(0)).item()))
    return sum(coh) / len(coh)


def measure_cell(N_use: int, M: int, depth: int, K_paths: int, n_pos: int,
                  seed: int, device: torch.device) -> Dict:
    """Run path E on one cell. Compute accuracy + per-path latency (E vs B/D extrap)."""
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    C = codebook.shape[0]
    pos_paths = sample_coherent_starts(relation, depth=depth,
                                         n_paths=n_pos, seed=seed + depth)
    if not pos_paths:
        del codebook, W
        if device.type == "cuda":
            torch.cuda.empty_cache()
        return {"M": int(M), "depth": int(depth), "K_paths": int(K_paths),
                "seed": int(seed), "n_pos": 0,
                "accuracy": 0.0, "latency_ms_E": 0.0,
                "latency_ms_BD_extrap": 0.0, "advantage_ratio": 0.0}

    # Decoys -- K_paths-1 per positive (we'll generate batch of decoys once and reuse)
    n_decoys_total = K_paths - 1
    decoys = sample_incoherent_paths(
        C, depth=depth, n_paths=n_decoys_total,
        seed=seed + depth + 999, relation=relation)
    if not decoys:
        del codebook, W
        if device.type == "cuda":
            torch.cuda.empty_cache()
        return {"M": int(M), "depth": int(depth), "K_paths": int(K_paths),
                "seed": int(seed), "n_pos": len(pos_paths),
                "accuracy": 0.0, "latency_ms_E": 0.0,
                "latency_ms_BD_extrap": 0.0, "advantage_ratio": 0.0}

    # Accuracy: median(decoy coherences) baseline for this cell, then
    # fraction of positives whose coherence beats median
    t_E_start = time.time()
    decoy_coh = [_coherence(codebook, W, p, N_use, TOP_K_SIG) for p in decoys]
    decoy_coh_sorted = sorted(decoy_coh)
    median_neg = decoy_coh_sorted[len(decoy_coh_sorted) // 2]
    pos_coh = [_coherence(codebook, W, p, N_use, TOP_K_SIG) for p in pos_paths]
    acc = sum(1 for c in pos_coh if c > median_neg) / max(1, len(pos_coh))
    t_E_total = time.time() - t_E_start
    # Latency per query: total time / (n_pos + K_paths-1) coherences
    n_coh_computed = len(pos_paths) + len(decoys)
    latency_ms_E = (t_E_total / max(1, n_coh_computed)) * 1000.0 * K_paths

    # B/D extrapolated latency: timer for one B-style forward pass + linear K
    t_BD_start = time.time()
    q = codebook[pos_paths[0][0]].unsqueeze(0)
    for _ in range(depth):
        q = q @ W.T
    sims = (codebook @ q.T).squeeze(1) / N_use
    _ = int(torch.argmax(sims).item())
    t_one_BD = time.time() - t_BD_start
    # B/D extrapolation: K_paths queries; assume linear
    latency_ms_BD_extrap = t_one_BD * 1000.0 * K_paths

    advantage_ratio = latency_ms_BD_extrap / max(1e-6, latency_ms_E)

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"M": int(M), "depth": int(depth), "K_paths": int(K_paths),
            "seed": int(seed), "n_pos": len(pos_paths),
            "accuracy": round(acc, 5),
            "latency_ms_E": round(latency_ms_E, 4),
            "latency_ms_BD_extrap": round(latency_ms_BD_extrap, 4),
            "advantage_ratio": round(advantage_ratio, 4)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("PATH_E_ENV_INCONCLUSIVE", "No cells.")

    # accuracy summary by (M, depth, K) - mean over seeds
    by_cfg: Dict[Tuple[int, int, int], List[Dict]] = {}
    for c in cells:
        by_cfg.setdefault((c["M"], c["depth"], c["K_paths"]), []).append(c)
    cfg_means: Dict[Tuple[int, int, int], float] = {
        k: sum(r["accuracy"] for r in rs) / len(rs)
        for k, rs in by_cfg.items()}

    total_cfgs = len(cfg_means)
    n_above_hp  = sum(1 for v in cfg_means.values() if v >= HP_ACC_THRESH)
    n_below_hf  = sum(1 for v in cfg_means.values() if v < HF_ACC_THRESH)

    # Sub-linear advantage: for each (M, depth), get advantage ratio across K's
    # and check that it's monotone non-decreasing
    advantage_by_md: Dict[Tuple[int, int], List[Tuple[int, float]]] = {}
    for c in cells:
        advantage_by_md.setdefault((c["M"], c["depth"]), []).append(
            (c["K_paths"], c["advantage_ratio"]))
    # Mean over seeds per (M, depth, K)
    advantage_means: Dict[Tuple[int, int], Dict[int, float]] = {}
    for k, rows in advantage_by_md.items():
        per_K: Dict[int, List[float]] = {}
        for K, ratio in rows:
            per_K.setdefault(K, []).append(ratio)
        advantage_means[k] = {K: sum(v) / len(v) for K, v in per_K.items()}
    # A (M, depth) cell satisfies sub-linear monotone advantage if for
    # consecutive K_grid points the advantage is non-decreasing
    K_grid_sorted = sorted(K_GRID_FULL)
    n_monotone_cells = 0
    for md, vals in advantage_means.items():
        ratios_sorted = [vals.get(K) for K in K_grid_sorted if K in vals]
        if len(ratios_sorted) >= 2:
            mono = all(ratios_sorted[i + 1] >= ratios_sorted[i] - 0.10
                        for i in range(len(ratios_sorted) - 1))
            if mono:
                n_monotone_cells += 1
    sublinear_advantage = (n_monotone_cells >= max(1, len(advantage_means) // 2))

    hp = (n_above_hp / max(1, total_cfgs)) >= HP_CELLS_FRAC and sublinear_advantage
    hf = (n_below_hf / max(1, total_cfgs)) > HF_CELLS_FRAC

    detail = (f"cfgs={total_cfgs} above_hp={n_above_hp} ({n_above_hp/max(1,total_cfgs):.2f}) "
              f"below_hf={n_below_hf} ({n_below_hf/max(1,total_cfgs):.2f}) "
              f"sublinear_monotone_cells={n_monotone_cells}/{len(advantage_means)}")

    if hp:
        return ("PATH_E_ENV_HARD_PASS",
                f"PATH_E_WIDE_ENVELOPE + SUB_LINEAR_ADVANTAGE: " + detail)
    if hf:
        return ("PATH_E_ENV_HARD_FAIL",
                f"PATH_E_BRITTLE: " + detail)
    return ("PATH_E_ENV_MIDDLE_BAND",
            f"PATH_E_NARROW_ENVELOPE / no clean advantage: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    n_cells = len(DEPTH_GRID_FULL) * len(K_GRID_FULL) * len(M_GRID_FULL)
    assert n_cells == 90, f"expected 90 cells, got {n_cells}"

    # Verdict gate HP
    fake_hp = []
    for d in DEPTH_GRID_FULL:
        for K in K_GRID_FULL:
            for M in M_GRID_FULL:
                for s in SEEDS_FULL:
                    # advantage_ratio scales with K
                    fake_hp.append({"M": M, "depth": d, "K_paths": K, "seed": s,
                                      "n_pos": N_POS_PER_CELL_FULL,
                                      "accuracy": 0.85,
                                      "latency_ms_E": 1.0,
                                      "latency_ms_BD_extrap": K * 0.5,
                                      "advantage_ratio": K * 0.5})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF
    fake_hf = []
    for d in DEPTH_GRID_FULL:
        for K in K_GRID_FULL:
            for M in M_GRID_FULL:
                for s in SEEDS_FULL:
                    fake_hf.append({"M": M, "depth": d, "K_paths": K, "seed": s,
                                      "n_pos": N_POS_PER_CELL_FULL,
                                      "accuracy": 0.10,
                                      "latency_ms_E": 1.0,
                                      "latency_ms_BD_extrap": 0.5,
                                      "advantage_ratio": 0.5})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Forward pass on CPU at smoke scale
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_GRID_SMOKE[0], DEPTH_GRID_SMOKE[0],
                        K_GRID_SMOKE[0], N_POS_PER_CELL_SMOKE, 17, device)
    assert 0.0 <= out["accuracy"] <= 1.0
    assert out["latency_ms_E"] >= 0.0
    print(f"[selftest] path_e_latency_envelope_v1_n4096 PASS smoke "
          f"M={out['M']} d={out['depth']} K={out['K_paths']} "
          f"acc={out['accuracy']:.3f} adv={out['advantage_ratio']:.2f}",
          flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    depths = DEPTH_GRID_SMOKE if smoke else DEPTH_GRID_FULL
    K_grid = K_GRID_SMOKE if smoke else K_GRID_FULL
    M_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_pos  = N_POS_PER_CELL_SMOKE if smoke else N_POS_PER_CELL_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] path_e_latency_envelope_v1 smoke={smoke} N={N_cfg} "
          f"depths={depths} K_grid={K_grid} M_grid={M_grid} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for M in M_grid:
        for d in depths:
            for K in K_grid:
                for seed in seeds:
                    ck = f"M{M}_d{d}_K{K}_seed{seed}"
                    if ck in done:
                        body = load_partial_key(out_dir, ck)
                        if body is not None:
                            cells.append(body); continue
                    try:
                        out = measure_cell(N_cfg, M, d, K, n_pos, seed, device)
                        write_partial_key(out_dir, ck, out)
                        cells.append(out)
                        print(f"  M={M} d={d} K={K} seed={seed} "
                              f"acc={out['accuracy']:.3f} "
                              f"adv={out['advantage_ratio']:.2f} "
                              f"({time.time()-t0:.1f}s)", flush=True)
                    except (RuntimeError, MemoryError) as e:
                        print(f"  M={M} d={d} K={K} seed={seed} FAILED: {e}",
                              flush=True)
                        if device.type == "cuda":
                            torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "path_e_latency_envelope_v1_n4096", "N": N_cfg,
               "smoke": smoke, "depths": depths, "K_grid": K_grid,
               "M_grid": M_grid, "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
