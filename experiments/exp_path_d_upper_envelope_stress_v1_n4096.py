"""U1 PATH D UPPER ENVELOPE STRESS v1 at N=4096.

CONTEXT (v289 cap_map follow-on):
  Path D is the production-default 6-axis robust mechanism. R1
  (stress_at_breaking) showed Path D unanimous 1.000 through M=24576 depth=20
  K=500 but did not find a ceiling. This anchor pushes past those limits to
  identify Path D's actual production envelope.

SCIENTIFIC QUESTION:
  At N=4096, BSC, K_paths=500: at what M and depth does Path D first lose
  accuracy? Sweep M in {16384, 24576, 32768, 49152, 65536} crossed with
  depth in {10, 20, 30, 50}.

PRE-REGISTERED BANDS:
  HP = Path D maintains >=0.85 across all 20 cells (100 cell-seeds).
       No ceiling found within tested envelope; run v2 with harder cells.
  HF = Path D drops below 0.30 at >=50% of cells (10 of 20). Clear breaking
       pattern; production envelope identified at the boundary.
  MB = otherwise. Differential breaking pattern (some cells fail, some hold);
       informative for production envelope characterization.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. M_grid=[16384,24576,32768,49152,65536], depth_grid=[10,20,30,50]
  3. 5 M x 4 depth x 5 seeds = 100 cell-seeds.
  4. K_paths fixed at 500.
  5. M_eff = min(M, C=4N=16384); past C the substrate collision rate increases.

OOM CHECK:
  N=4096: W = 4096x4096 float32 = 64 MiB. Codebook C=16384 x 4096 = 256 MiB.
  Per-path enumeration K=500 x depth=50 indices = ~2 MiB. Peak ~400 MiB.
  Well under 6 GiB headroom on the 8 GiB runner GPU.

TIMEOUT ESTIMATE:
  Smoke ~ 60s (CPU smoke + GPU smoke). FULL: 100 cell-seeds. Per cell-seed
  ~20-90s (depth=50 dominates inner loop over B starts x K=500 candidates).
  Mid-estimate ~50s/cell-seed = 5000s. With overhead and depth=50 worst-case
  ~8000s. 21600s budget per user spec for safety against deep-chain
  super-linear scaling.

N-suffix: _n4096 (PROT-018).
Anchor: path_d_upper_envelope_stress_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_path_d_upper_envelope_stress_v1_n4096.md
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
from experiments._multi_hop_mechanisms import path_d_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_u1", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_GRID_FULL  = [16384, 24576, 32768, 49152, 65536]
M_GRID_SMOKE = [512, 1024]
DEPTH_GRID_FULL  = [10, 20, 30, 50]
DEPTH_GRID_SMOKE = [3, 5]
K_PATHS_FULL  = 500
K_PATHS_SMOKE = 20
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_STARTS = 16

BETA_D = 4.0

# Pre-registered thresholds
HP_MIN_ACC = 0.85
HF_MAX_ACC = 0.30
HF_FRAC_CELLS = 0.50  # HF triggers if HF_MAX_ACC fails at >=50% of cells


def get_output_dir(default_name: str = "path_d_upper_envelope_stress_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                    device: torch.device):
    """Build substrate + relation. M_eff = min(M, C) for relation."""
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


def measure_cell(N_use: int, M: int, depth: int, K_paths: int,
                  seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    starts_list = list(relation.keys())[:N_STARTS]
    if not starts_list:
        del codebook, W
        if device.type == "cuda":
            torch.cuda.empty_cache()
        return {"M": int(M), "depth": int(depth), "seed": int(seed),
                "K_paths": int(K_paths), "accuracy": 0.0, "n_eval": 0}
    starts = torch.tensor(starts_list, dtype=torch.long, device=device)
    t0 = time.perf_counter_ns()
    correct = path_d_run(codebook, W, starts, relation, depth, K_paths,
                          seed, N_use, beta=BETA_D)
    lat_ns = time.perf_counter_ns() - t0
    acc = float(correct.mean().item())
    n_eval = int(correct.shape[0])

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"M": int(M), "depth": int(depth), "seed": int(seed),
            "K_paths": int(K_paths), "accuracy": round(acc, 5),
            "n_eval": n_eval, "lat_ns": int(lat_ns)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("U1_INCONCLUSIVE", "no cells")

    # Aggregate per (M, depth) over seeds
    by_cell: Dict[Tuple[int, int], List[float]] = {}
    for c in cells:
        k = (c["M"], c["depth"])
        by_cell.setdefault(k, []).append(c["accuracy"])
    means: Dict[Tuple[int, int], float] = {
        k: sum(v) / len(v) for k, v in by_cell.items()}

    n_cells = len(means)
    n_below_hp = sum(1 for m in means.values() if m < HP_MIN_ACC)
    n_below_hf = sum(1 for m in means.values() if m < HF_MAX_ACC)
    frac_below_hf = n_below_hf / max(1, n_cells)

    # Cell-level summary
    summary_lines = []
    for M in M_GRID_FULL:
        row = " ".join(
            f"d{d}={means.get((M, d), float('nan')):.3f}"
            for d in DEPTH_GRID_FULL)
        summary_lines.append(f"M{M}: {row}")
    detail = " | ".join(summary_lines)

    if n_below_hp == 0:
        return ("U1_HARD_PASS",
                f"PATH_D_PAST_TEST_ENVELOPE: all {n_cells} cells >= {HP_MIN_ACC}. "
                + detail)
    if frac_below_hf >= HF_FRAC_CELLS:
        return ("U1_HARD_FAIL",
                f"PATH_D_BREAKING_IDENTIFIED: {n_below_hf}/{n_cells} cells < "
                f"{HF_MAX_ACC} (>= {int(HF_FRAC_CELLS * 100)}% threshold). "
                + detail)
    return ("U1_MIDDLE_BAND",
            f"PATH_D_DIFFERENTIAL_BREAKING: {n_below_hp}/{n_cells} cells < "
            f"{HP_MIN_ACC}; {n_below_hf}/{n_cells} cells < {HF_MAX_ACC}. "
            + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(M_GRID_FULL) == 5
    assert len(DEPTH_GRID_FULL) == 4
    assert K_PATHS_FULL == 500
    assert len(SEEDS_FULL) == 5

    # Verdict gate HP
    fake_hp = []
    for M in M_GRID_FULL:
        for d in DEPTH_GRID_FULL:
            for s in SEEDS_FULL:
                fake_hp.append({"M": M, "depth": d, "seed": s,
                                  "K_paths": K_PATHS_FULL, "accuracy": 0.90,
                                  "n_eval": N_STARTS})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF (>=50% cells below 0.30)
    fake_hf = []
    n_cells = len(M_GRID_FULL) * len(DEPTH_GRID_FULL)
    cells_below = 0
    for M in M_GRID_FULL:
        for d in DEPTH_GRID_FULL:
            for s in SEEDS_FULL:
                # Make 60% of cells fail (M>=24576 + d>=20 -> fail)
                if (M >= 24576 and d >= 20):
                    acc = 0.10
                else:
                    acc = 0.90
                fake_hf.append({"M": M, "depth": d, "seed": s,
                                  "K_paths": K_PATHS_FULL, "accuracy": acc,
                                  "n_eval": N_STARTS})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, f"HF gate: {v}"

    # Verdict gate MIDDLE_BAND (some cells fail but <50%)
    fake_mb = []
    for M in M_GRID_FULL:
        for d in DEPTH_GRID_FULL:
            for s in SEEDS_FULL:
                # Only worst cell (M=65536 d=50) fails
                acc = 0.10 if (M == 65536 and d == 50) else 0.90
                fake_mb.append({"M": M, "depth": d, "seed": s,
                                  "K_paths": K_PATHS_FULL, "accuracy": acc,
                                  "n_eval": N_STARTS})
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, f"MB gate: {v}"

    # Smoke forward pass on CPU
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_GRID_SMOKE[0], DEPTH_GRID_SMOKE[0],
                        K_PATHS_SMOKE, 17, device)
    assert 0.0 <= out["accuracy"] <= 1.0
    assert out["n_eval"] > 0, "selftest produced 0 starts (filter eliminated all)"
    print(f"[selftest] path_d_upper_envelope_stress_v1_n4096 PASS "
          f"smoke M={M_GRID_SMOKE[0]} d={DEPTH_GRID_SMOKE[0]} "
          f"acc={out['accuracy']:.3f} n_eval={out['n_eval']}", flush=True)


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
    M_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    depths = DEPTH_GRID_SMOKE if smoke else DEPTH_GRID_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL
    K_paths = K_PATHS_SMOKE if smoke else K_PATHS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] path_d_upper_envelope_stress smoke={smoke} N={N_cfg} "
          f"M_grid={M_grid} depths={depths} K_paths={K_paths} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for M in M_grid:
        for d in depths:
            for seed in seeds:
                ck = f"M{M}_d{d}_seed{seed}"
                if ck in done:
                    body = load_partial_key(out_dir, ck)
                    if body is not None:
                        cells.append(body); continue
                try:
                    out = measure_cell(N_cfg, M, d, K_paths, seed, device)
                    write_partial_key(out_dir, ck, out)
                    cells.append(out)
                    print(f"  M={M} d={d} seed={seed} "
                          f"acc={out['accuracy']:.3f} "
                          f"({time.time()-t0:.1f}s)", flush=True)
                except (RuntimeError, MemoryError) as e:
                    print(f"  M={M} d={d} seed={seed} FAILED: {e}", flush=True)
                    if device.type == "cuda":
                        torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "path_d_upper_envelope_stress_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M_grid": M_grid, "depths": depths,
               "K_paths": K_paths, "seeds": seeds,
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
