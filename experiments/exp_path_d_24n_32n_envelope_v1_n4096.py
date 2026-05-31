"""G7 PATH D 24N 32N ENVELOPE v1 at N=4096.

CONTEXT (v290 cap_map follow-on):
  U1 found no ceiling at 16N depth=50. G7 extends the envelope to 24N and
  32N to identify whether Path D maintains accuracy past 16N.

SCIENTIFIC QUESTION:
  At N=4096, BSC, K_paths=100: does Path D maintain >=0.85 accuracy at
  M in {24N, 32N} crossed with depth in {10, 20, 30, 50}?

PRE-REGISTERED BANDS:
  HP = all 40 cell-seeds (2 M * 4 depth * 5 seeds) >= 0.85
       (no ceiling within 32N depth=50 envelope).
  HF = >= 10 cell-seeds < 0.50 (ceiling identified within envelope).
  MB = otherwise.

PROT-018: _n4096 binds N = 4096.
PROT-020: torch + cuda available (GPU runner).
PROT-021: per-cell-seed checkpointing.

OOM CHECK:
  N=4096: W = 4096x4096 float32 = 64 MiB. Codebook C = max(M) = 32N = 131072
  x 4096 = 2 GiB. K_paths=100 x depth=50 indices = ~0.4 MiB. Peak ~2.5 GiB,
  under 6 GiB headroom.

Anchor: path_d_24n_32n_envelope_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_path_d_24n_32n_envelope_v1_n4096.md
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
from experiments._relation_graph import build_relation_facts  # noqa: E402
from experiments._multi_hop_mechanisms import path_d_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g7", _ck_path)
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

M_GRID_FULL  = [24 * N_FULL, 32 * N_FULL]   # [98304, 131072]
M_GRID_SMOKE = [512, 1024]
DEPTH_GRID_FULL  = [10, 20, 30, 50]
DEPTH_GRID_SMOKE = [3, 5]
K_PATHS_FULL  = 100
K_PATHS_SMOKE = 20
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_STARTS = 16
BETA_D = 4.0

HP_MIN_ACC = 0.85
HF_MAX_ACC = 0.50
HF_MIN_CELL_SEEDS = 10  # >=10 cell-seeds < HF_MAX_ACC = HF


def get_output_dir(default_name: str = "path_d_24n_32n_envelope_v1_n4096") -> Path:
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
        return ("G7_INCONCLUSIVE", "no cells")
    # Per cell-seed accuracy
    accs = [c["accuracy"] for c in cells]
    n_total = len(accs)
    n_below_hp = sum(1 for a in accs if a < HP_MIN_ACC)
    n_below_hf = sum(1 for a in accs if a < HF_MAX_ACC)

    # Aggregate per (M, depth) for detail
    by_cell: Dict[Tuple[int, int], List[float]] = {}
    for c in cells:
        k = (c["M"], c["depth"])
        by_cell.setdefault(k, []).append(c["accuracy"])
    means = {k: sum(v) / len(v) for k, v in by_cell.items()}

    summary_lines = []
    for M in M_GRID_FULL:
        row = " ".join(f"d{d}={means.get((M, d), float('nan')):.3f}"
                       for d in DEPTH_GRID_FULL)
        summary_lines.append(f"M{M}: {row}")
    detail = " | ".join(summary_lines)

    if n_below_hp == 0:
        return ("G7_HARD_PASS",
                f"PATH_D_PAST_32N_ENVELOPE: all {n_total} cell-seeds >= {HP_MIN_ACC}. "
                + detail)
    if n_below_hf >= HF_MIN_CELL_SEEDS:
        return ("G7_HARD_FAIL",
                f"PATH_D_CEILING_IDENTIFIED: {n_below_hf}/{n_total} cell-seeds "
                f"< {HF_MAX_ACC} (>= {HF_MIN_CELL_SEEDS} threshold). " + detail)
    return ("G7_MIDDLE_BAND",
            f"PATH_D_DIFFERENTIAL: {n_below_hp}/{n_total} < {HP_MIN_ACC}; "
            f"{n_below_hf}/{n_total} < {HF_MAX_ACC}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert M_GRID_FULL == [98304, 131072]
    assert DEPTH_GRID_FULL == [10, 20, 30, 50]
    assert K_PATHS_FULL == 100
    assert len(SEEDS_FULL) == 5

    # Total cells = 2 M * 4 depth * 5 seeds = 40
    expected_cells = len(M_GRID_FULL) * len(DEPTH_GRID_FULL) * len(SEEDS_FULL)
    assert expected_cells == 40, expected_cells

    # Verdict gate HP
    fake_hp = []
    for M in M_GRID_FULL:
        for d in DEPTH_GRID_FULL:
            for s in SEEDS_FULL:
                fake_hp.append({"M": M, "depth": d, "seed": s,
                                "K_paths": K_PATHS_FULL, "accuracy": 0.90,
                                "n_eval": N_STARTS})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF (>=10 cell-seeds below 0.50)
    fake_hf = []
    cnt = 0
    for M in M_GRID_FULL:
        for d in DEPTH_GRID_FULL:
            for s in SEEDS_FULL:
                # Make ~30% (12 cells) fail
                if (d == 50 and (M, d) != (M_GRID_FULL[0], 10)):
                    acc = 0.10
                    cnt += 1
                else:
                    acc = 0.90
                fake_hf.append({"M": M, "depth": d, "seed": s,
                                "K_paths": K_PATHS_FULL, "accuracy": acc,
                                "n_eval": N_STARTS})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, f"HF gate: {v} cnt={cnt}"

    # Verdict gate MB (<10 cells below 0.50)
    fake_mb = []
    for M in M_GRID_FULL:
        for d in DEPTH_GRID_FULL:
            for s in SEEDS_FULL:
                # Only worst cell (M=131072 d=50) fails (5 cell-seeds total)
                acc = 0.10 if (M == M_GRID_FULL[1] and d == 50) else 0.90
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
    print(f"[selftest] path_d_24n_32n_envelope_v1_n4096 PASS "
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
    print(f"[run] path_d_24n_32n_envelope_v1_n4096 smoke={smoke} N={N_cfg} "
          f"M_grid={M_grid} depths={depths} K_paths={K_paths} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

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
                    print(f"  M={M} d={d} seed={seed} acc={out['accuracy']:.3f} "
                          f"({time.time()-t0:.1f}s)", flush=True)
                except (RuntimeError, MemoryError) as e:
                    print(f"  M={M} d={d} seed={seed} FAILED: {e}", flush=True)
                    if device.type == "cuda":
                        torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "path_d_24n_32n_envelope_v1_n4096",
               "N": N_cfg, "smoke": smoke, "M_grid": M_grid,
               "depths": depths, "K_paths": K_paths, "seeds": seeds,
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
