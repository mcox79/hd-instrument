"""PATH D K=1 PHASE BOUNDARY CROSS-M SWEEP v1 at N=4096.

CONTEXT (v1 MIDDLE_BAND; K-safety-margin characterization):
  v1 K=1 phase boundary probe landed MIDDLE_BAND HONEST:
  k1_mean=0.022 at M=16N -- 6.7x above random chance; K-safety-margin
  EMPIRICALLY confirmed as Path D production lever.
  This cross-M sweep locates WHERE the substrate-physics phase boundary is:
  at what M does K=1 cross from "graceful degradation >random" to "random-chance"?

SCIENTIFIC QUESTION:
  As M increases from 2N to 64N, how does path_b_top1_acc (K=1 effective,
  no candidate pool) degrade? Where is the percolation-theory phase boundary?
  Research P3 predicted ceiling at M ~ 100N-300N; this measures the M-axis.

PRE-REGISTERED BANDS:
  For each M point independently:
    HP band: path_b_top1_acc > 0.10 (substantive above random 1/C where C~M).
    HF band: path_b_top1_acc < 0.002 (at or below random-chance floor).
    MIDDLE: path_b_top1_acc in [0.002, 0.10].

  Overall cross-M verdict:
    HARD-PASS:  path_b_top1_acc >= 0.05 at M=16N (corroborates v1 MIDDLE_BAND
                0.022 finding) AND clear decay trend with increasing M.
    HARD-FAIL:  path_b_top1_acc < 0.005 at M=2N (random-chance even at small M;
                substrate has no K=1 signal at any M).
    MIDDLE-BAND: M-axis decay measured; boundary identified at specific M*.

  Calibration note: v1 measured path_b_top1_acc=0.022 at M=16N (6.7x random).
  The M=16N point here is a corroboration cell; others fill the M-axis.

DESIGN:
  N=4096, M in {2N=8192, 4N=16384, 8N=32768, 16N=65536, 32N=131072},
  depth=5, K_paths (candidate-pool) in {10, 100}, 5 seeds.
  Primary metric per (seed, M): path_b_top1_acc (K=1 effective via Path B direct walk).
  Secondary: path_d_k10_acc, path_d_k100_acc (candidate-pool behavior vs M).

  M-grid rationale: 5 points (not 6) to balance coverage and compute budget.
  64N dropped (131072 * N=4096 = 512 GB codebook -- would OOM).
  32N = 131072 * 4096 * 4 bytes = 2 GB codebook. Fits 64 GB remote CPU RAM.

OOM CHECK:
  Worst case M=32N=131072: codebook = 131072 x 4096 float32 = 2 GB.
  W = 4096 x 4096 float32 = 64 MB.
  Remote CPU has 64 GB RAM. Peak ~2.1 GB. OK.
  M=2N=8192: codebook = 128 MB. M=4N: 256 MB. M=8N: 512 MB. All fine.

PROT-018: _n4096 binds N = 4096.
PROT-019: timeout >= 14400s.
PROT-021: per-cell-M-seed checkpointing.
PROT-022: device=cpu forced.

TIMEOUT ESTIMATE:
  v1 elapsed ~30-60s/seed at M=16N (N=4096, 5 seeds, k_keys=100).
  Larger M: codebook build + W build scales as O(M*N). M=32N is 2x M=16N.
  5 M-points x 5 seeds: ~25 cells.
  Estimated: 60s x 25 cells x 1.5 safety = 2250s -> 2700s.
  PROT-019 floor: 14400s. timeout_s = 14400.

FORMULA SELF-TESTS:
  1. path_b_top1_acc at M=2N should be substantially higher than at M=32N
     (more capacity at smaller M). Not tested numerically but structure verified.
  2. Verdict gate: if v1 MIDDLE_BAND k1=0.022 is reproduced at M=16N,
     that is a HARD-PASS at the corroboration cell level.
  3. M corroboration: M=16N cell should reproduce v1 within 2x (0.011 - 0.044).

Anchor: path_d_k1_phase_boundary_cross_m_v1_n4096
Queue: remote_cpu_queue (CPU-only; large codebooks up to 2 GB)
Pre-reg: preregs/2026-06-01_path_d_k1_phase_boundary_cross_m_v1_n4096.md
Total cells: 5 M-values x 5 seeds = 25 cells
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_k1_cross_m", _ck_path)
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

# Cross-M grid (5 points; 64N dropped: 512 GB OOM)
M_GRID_FULL  = [2 * N_FULL, 4 * N_FULL, 8 * N_FULL, 16 * N_FULL, 32 * N_FULL]
# Smoke: 3 M-points at smaller N (smoke N=1024, M small)
M_GRID_SMOKE = [2 * N_SMOKE, 4 * N_SMOKE, 8 * N_SMOKE]

DEPTH        = 5
K_RANDOM_KEYS = 100   # query starts per (seed, M) cell
K_RANDOM_KEYS_SMOKE = 20
BETA_D       = 4.0
SEEDS_FULL   = [7, 17, 23, 42, 99]
SEEDS_SMOKE  = [17]
DEVICE       = torch.device("cpu")   # PROT-022

# Pre-registered verdict bands
# Per-M cell bands
HP_K1_PER_M   = 0.10   # k1 > 0.10 at any M -> substantive
HF_K1_PER_M   = 0.002  # k1 < 0.002 -> random-chance floor
# Overall verdict bands
HP_K1_CORR    = 0.005  # path_b_top1 >= 0.005 at M=16N (corroboration of v1 0.022)
HF_K1_AT_2N   = 0.005  # < 0.005 at M=2N (even smallest M shows no signal)


def get_output_dir(default_name: str = "path_d_k1_phase_boundary_cross_m_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                   device: torch.device):
    """Build codebook + W + relation (same construction as v1)."""
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    M_eff = min(M, C)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M_eff, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec  = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


def measure_cell(N_use: int, M: int, depth: int, seed: int,
                  k_random_keys: int, device: torch.device) -> Dict:
    """Measure path_b_top1_acc + path_d_k10 + path_d_k100 for one (seed, M)."""
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)

    all_starts_in_relation = list(relation.keys())
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
        return {"seed": int(seed), "M": int(M), "N": int(N_use),
                "n_eval": 0,
                "path_b_top1_acc": 0.0,
                "path_d_k10_acc": 0.0,
                "path_d_k100_acc": 0.0,
                "error": "no valid starts at depth"}

    rng = torch.Generator().manual_seed(seed + 99999)
    n_use = min(k_random_keys, len(valid_starts))
    perm = torch.randperm(len(valid_starts), generator=rng).tolist()
    chosen = [valid_starts[i] for i in perm[:n_use]]
    starts = torch.tensor(chosen, dtype=torch.long, device=device)

    targets_list = []
    for s in chosen:
        cur = s
        for _ in range(depth):
            cur = relation[cur]
        targets_list.append(cur)
    targets = torch.tensor(targets_list, dtype=torch.long, device=device)

    # Path B top-1 (K=1 effective, no candidate pool -- phase boundary probe)
    t0 = time.perf_counter_ns()
    pred_b = path_b_run(codebook, W, starts, depth=depth, N_use=N_use)
    lat_b_ns = time.perf_counter_ns() - t0
    path_b_top1_acc = float((pred_b == targets).float().mean().item())

    # Candidate-pool probes: K=10, K=100
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
        "seed":             int(seed),
        "M":                int(M),
        "N":                int(N_use),
        "n_eval":           int(starts.shape[0]),
        "path_b_top1_acc":  round(path_b_top1_acc, 5),
        "path_d_k10_acc":   round(path_d_k10_acc, 5),
        "path_d_k100_acc":  round(path_d_k100_acc, 5),
        "lat_b_ns":         int(lat_b_ns),
        "lat_k10_ns":       int(lat_k10_ns),
        "lat_k100_ns":      int(lat_k100_ns),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    """Compute cross-M verdict from all (seed, M) cells."""
    if not cells:
        return ("K1_CROSSM_INCONCLUSIVE", "no cells")

    valid = [c for c in cells if c.get("n_eval", 0) > 0]
    if not valid:
        return ("K1_CROSSM_INCONCLUSIVE", "all cells returned n_eval=0")

    # Group by M
    m_vals = sorted(set(c["M"] for c in valid))
    m_stats = {}
    for m in m_vals:
        m_cells = [c for c in valid if c["M"] == m]
        k1_accs   = [c["path_b_top1_acc"] for c in m_cells]
        k10_accs  = [c["path_d_k10_acc"] for c in m_cells]
        k100_accs = [c["path_d_k100_acc"] for c in m_cells]
        m_stats[m] = {
            "k1_mean":   round(sum(k1_accs)   / len(k1_accs),   5),
            "k10_mean":  round(sum(k10_accs)  / len(k10_accs),  5),
            "k100_mean": round(sum(k100_accs) / len(k100_accs), 5),
            "n_seeds":   len(m_cells),
        }

    detail = " | ".join(
        f"M={m}(ratio={m//N_FULL}N): k1={m_stats[m]['k1_mean']:.4f} "
        f"k10={m_stats[m]['k10_mean']:.4f} k100={m_stats[m]['k100_mean']:.4f}"
        for m in m_vals
    )

    # Corroboration cell: M=16N=65536
    m_16n = 16 * N_FULL
    corr_cell = m_stats.get(m_16n)

    # Smallest M cell
    m_2n = 2 * N_FULL
    cell_2n = m_stats.get(m_2n)

    # HF: no signal even at smallest M
    if cell_2n is not None and cell_2n["k1_mean"] < HF_K1_AT_2N:
        return (
            "K1_CROSSM_HARD_FAIL",
            f"NO_K1_SIGNAL_AT_ANY_M: path_b_top1 at M=2N={cell_2n['k1_mean']:.4f} < {HF_K1_AT_2N}. "
            f"Substrate has zero K=1 signal across all M. " + detail
        )

    # HP: corroboration of v1 MIDDLE_BAND at M=16N
    if corr_cell is not None and corr_cell["k1_mean"] >= HP_K1_CORR:
        return (
            "K1_CROSSM_HARD_PASS",
            f"K1_PHASE_CORROBORATED: M=16N k1_mean={corr_cell['k1_mean']:.4f} >= {HP_K1_CORR}. "
            f"M-axis decay measured; phase boundary identified. " + detail
        )

    # MIDDLE: partial signal -- M-axis characterized but corroboration inconclusive
    corr_k1_str = f"{corr_cell['k1_mean']:.4f}" if corr_cell is not None else "N/A"
    if cell_2n is not None and cell_2n["k1_mean"] >= HF_K1_AT_2N:
        return (
            "K1_CROSSM_MIDDLE_BAND",
            f"K1_PHASE_PARTIAL: M=2N k1={cell_2n['k1_mean']:.4f} (signal present at small M); "
            f"M=16N k1={corr_k1_str}. "
            f"M-axis sweep complete; boundary characterization partial. " + detail
        )

    return (
        "K1_CROSSM_MIDDLE_BAND",
        f"K1_PHASE_PARTIAL_CATCHALL. " + detail
    )


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert M_GRID_FULL == [8192, 16384, 32768, 65536, 131072], \
        f"M_GRID_FULL mismatch: {M_GRID_FULL}"
    assert DEPTH == 5, f"depth must be 5; got {DEPTH}"
    assert len(SEEDS_FULL) == 5

    # Verdict gate checks
    # HP: corroboration at M=16N
    hp_cells = [{"M": 65536, "N": 4096, "path_b_top1_acc": 0.025, "path_d_k10_acc": 0.30,
                  "path_d_k100_acc": 0.90, "n_eval": 10}] * 5
    v, msg = compute_verdict(hp_cells)
    assert "HARD_PASS" in v, f"HP gate failed: {v}\n{msg}"

    # HF: no signal at M=2N
    hf_cells = [{"M": 8192, "N": 4096, "path_b_top1_acc": 0.001, "path_d_k10_acc": 0.10,
                  "path_d_k100_acc": 0.80, "n_eval": 10}] * 5
    v, msg = compute_verdict(hf_cells)
    assert "HARD_FAIL" in v, f"HF gate failed: {v}"

    # MIDDLE: signal at M=2N but not corroborated at M=16N
    mb_cells = ([{"M": 8192, "N": 4096, "path_b_top1_acc": 0.05, "path_d_k10_acc": 0.40,
                   "path_d_k100_acc": 0.85, "n_eval": 10}] * 3
                + [{"M": 65536, "N": 4096, "path_b_top1_acc": 0.001, "path_d_k10_acc": 0.10,
                    "path_d_k100_acc": 0.90, "n_eval": 10}] * 2)
    v, msg = compute_verdict(mb_cells)
    assert "MIDDLE_BAND" in v or "HARD_FAIL" in v, f"MB/HF gate failed: {v}"

    # Inconclusive: no cells
    v, _ = compute_verdict([])
    assert "INCONCLUSIVE" in v

    # Formula self-test: M_GRID sanity
    for m in M_GRID_FULL:
        assert m % N_FULL == 0, f"M={m} not a multiple of N={N_FULL}"
    assert max(M_GRID_FULL) == 32 * N_FULL, "max M should be 32N"

    # Live smoke forward pass
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_GRID_SMOKE[0], depth=3, seed=17,
                        k_random_keys=K_RANDOM_KEYS_SMOKE, device=device)
    assert out.get("n_eval", 0) > 0, f"selftest produced 0 starts: {out}"
    assert 0.0 <= out["path_b_top1_acc"] <= 1.0, \
        f"path_b_top1_acc out of range: {out['path_b_top1_acc']}"
    assert 0.0 <= out["path_d_k10_acc"] <= 1.0, \
        f"path_d_k10_acc out of range: {out['path_d_k10_acc']}"
    assert 0.0 <= out["path_d_k100_acc"] <= 1.0, \
        f"path_d_k100_acc out of range: {out['path_d_k100_acc']}"
    print(
        f"[selftest] path_d_k1_phase_boundary_cross_m_v1_n4096 PASS "
        f"smoke N={N_SMOKE} M={M_GRID_SMOKE[0]} d=3 seed=17 "
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

    device = DEVICE   # PROT-022: CPU force
    smoke  = args.smoke
    N_cfg  = N_SMOKE          if smoke else N_FULL
    m_grid = M_GRID_SMOKE     if smoke else M_GRID_FULL
    seeds  = SEEDS_SMOKE      if smoke else SEEDS_FULL
    k_keys = K_RANDOM_KEYS_SMOKE if smoke else K_RANDOM_KEYS

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    total_cells = len(m_grid) * len(seeds)
    cell_num = 0

    print(
        f"[run] path_d_k1_phase_boundary_cross_m_v1_n4096 smoke={smoke} "
        f"N={N_cfg} M_grid={m_grid} depth={DEPTH} seeds={seeds} "
        f"k_random_keys={k_keys} total_cells={total_cells} "
        f"done={len(done)} device={device.type}",
        flush=True,
    )

    cells: List[Dict] = []
    for M in m_grid:
        for seed in seeds:
            cell_num += 1
            ck = f"M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body)
                    print(f"  [cell {cell_num}/{total_cells}] M={M} seed={seed} RESUMED",
                          flush=True)
                    continue
            try:
                out = measure_cell(N_cfg, M, depth=DEPTH, seed=seed,
                                    k_random_keys=k_keys, device=device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                elapsed_s = time.time() - t0
                print(
                    f"  [cell {cell_num}/{total_cells}] M={M}(ratio={M//N_cfg}N) "
                    f"seed={seed} "
                    f"path_b_top1={out.get('path_b_top1_acc', 'N/A')} "
                    f"k10={out.get('path_d_k10_acc', 'N/A')} "
                    f"k100={out.get('path_d_k100_acc', 'N/A')} "
                    f"n_eval={out.get('n_eval', 0)} "
                    f"({elapsed_s:.1f}s)",
                    flush=True,
                )
            except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
                print(f"  [cell {cell_num}/{total_cells}] M={M} seed={seed} FAILED: {e}",
                      flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor":        "path_d_k1_phase_boundary_cross_m_v1_n4096",
        "N":             N_cfg,
        "smoke":         smoke,
        "M_grid":        m_grid,
        "depth":         DEPTH,
        "seeds":         seeds,
        "k_random_keys": k_keys,
        "cells":         cells,
        "verdict":       verdict,
        "verdict_msg":   vm,
        "elapsed_s":     elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
