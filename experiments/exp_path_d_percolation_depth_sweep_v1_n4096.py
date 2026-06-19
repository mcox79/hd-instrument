"""PATH D PERCOLATION DEPTH-SWEEP DIAGNOSTIC v1 (base N=4096).

CONTEXT (follow-on to R4 null-prediction HARD_FAIL 2026-06-01; percolation
  framework rescue: composed-function threshold effect hypothesis):

  The P3 percolation framework predicted K=1 signal is N-independent.
  R4 null test (path_d_k1_cross_n_null_prediction_v1_n4096) refuted this
  prediction at depth=5: K=1 signal at N=16384 exceeded the N-independence
  band (max_delta ~18x gate). This could be:
    (a) per-hop K=1 physics IS N-dependent -> percolation framework fails
        at the single-hop level (requires escalation to FSS; Test 1B).
    (b) per-hop K=1 IS N-independent; depth=5 COMPOSITION crosses a
        reliability threshold whose position in (N, M, D) space is N-dependent
        -> a composed-function threshold effect, NOT a substrate-physics failure.

  This experiment discriminates (a) vs (b) by sweeping depth in {1, 2, 3, 5}
  at N in {4096, 16384}, K=1 fixed, M=16N fixed.

SCIENTIFIC QUESTION:
  At K=1, M=16N, sweeping N in {4096, 16384} x depth in {1, 2, 3, 5}:
  Does depth=1 signal stay N-independent (within 10%) while divergence
  emerges at depth >= 3 or 5? Or does divergence already appear at depth=1?

PRE-REGISTERED BANDS (load-bearing from research routing 2026-06-01):

  HARD-PASS (composition cliff confirmed):
    depth=1 mean path_b_top1_acc at N=4096 and N=16384 within 10% of each
    other (relative divergence <= 10%); AND depth=3 or depth=5 shows
    divergence > 2x between N values.
    Interpretation: percolation framework valid at per-hop (single-hop);
    depth-composition is the new framework gap. Closes the percolation
    refutation as composed-function threshold, NOT substrate-physics failure.
    Cap-map action: add depth-composition cliff caveat at K=1 D>=3 large-N;
    framework keeps single-hop K=1 prediction.

  HARD-FAIL (per-hop physics IS N-dependent):
    depth=1 already shows > 20% relative divergence between N values.
    Interpretation: percolation framework loses K=1 single-hop prediction.
    Escalate to Test 1B FSS power-law sweep (GPU, contingently pre-authorized).

  MIDDLE-BAND:
    depth=1 relative divergence in (10%, 20%] -- ambiguous; escalate to
    5-seed retest for tighter statistics.

DIVERGENCE METRIC:
  relative_div(d) = |acc(N=16384, d) - acc(N=4096, d)| / max(acc(N=4096, d), 1e-6)
  HP: relative_div(d=1) <= 0.10 AND max(relative_div(d=3), relative_div(d=5)) > 2.0
  HF: relative_div(d=1) > 0.20
  MIDDLE: relative_div(d=1) in (0.10, 0.20]

FORMULA SELF-TESTS:
  1. HP: d=1 acc(4096)=0.025, acc(16384)=0.027 -> rel_div=0.08 <= 0.10;
         d=5 acc(4096)=0.022, acc(16384)=0.060 -> rel_div=1.73 > 2.0 -> FALSE
         (must be >2.0 for HP, this is 1.73; adjust: d=5 acc(16384)=0.076
         -> rel_div=2.45 > 2.0 -> HP)
  2. HF: d=1 acc(4096)=0.025, acc(16384)=0.060 -> rel_div=1.40 > 0.20 -> HF
  3. MIDDLE: d=1 acc(4096)=0.025, acc(16384)=0.033 -> rel_div=0.32 -> that is
     > 0.20 actually. Middle: d=1 acc(4096)=0.025, acc(16384)=0.029 ->
     rel_div=0.16 in (0.10, 0.20] -> MIDDLE

OOM CHECK:
  N=4096, M=16N=65536: codebook=65536*4096 float32 = 1 GiB.
  N=16384, M=16N=262144: codebook=262144*16384 float32 = 16 GiB.
  Remote CPU has 64 GB RAM. Peak ~17 GiB at N=16384. Fits with margin.

PROT-018: _n4096 binds base N = 4096 (minimum N in sweep).
  The sweep includes N=16384 as a second cell-axis point; anchor records base.
PROT-019: timeout >= 14400s.
PROT-021: per-cell-N-depth-seed checkpointing.
PROT-022: device=cpu forced.

TIMEOUT ESTIMATE:
  Cross-N null test (depth=5, N in {4096,16384}, 5 seeds) ran ~18 CPU-min.
  This sweep: 4 depths * 2 N-values * 3 seeds = 24 cells.
  Compare: 10 cells at depth=5 -> 1080s total estimate from routing.
  Per-cell at N=16384 depth=5 ~= 45s. depth=1 much cheaper (~5s).
  Average cell ~20s. 24 cells * 20s * 1.5 safety = 720s.
  N-scaling: N=16384 cells are ~8x heavier than N=4096 per routing.
  Weighted estimate: 12 cells * 5s (N=4096) + 12 cells * 40s (N=16384)
    = 60 + 480 = 540s * 1.5 = 810s. PROT-019 floor: 14400s.
  timeout_s = 14400 (PROT-019 floor dominates).

Anchor: path_d_percolation_depth_sweep_v1_n4096
Queue: remote_cpu_queue (CPU-only; ~18 CPU-min; research-specified)
Pre-reg: prereqs/2026-06-01_path_d_percolation_depth_sweep_v1_n4096.md
Total cells: 2 N-values x 4 depths x 3 seeds = 24 cells
HDLAB_EXP_NAME: 7d39e13 (per dispatch)
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
from experiments._multi_hop_mechanisms import path_b_run         # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_perc_depth", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# ---------------------------------------------------------------------------
# PROT-018: _n4096 binds base N = 4096 (minimum N in N-sweep grid)
# The anchor name records base N=4096; N=16384 is a second cell-axis point.
# ---------------------------------------------------------------------------
N = 4096
N_FULL  = N
assert N_FULL == 4096, f"PROT-018: base N_FULL must be 4096; got {N_FULL}"

# N-sweep grid (N=8192 skipped: log2=13 odd, Kerdock constraint from R4)
N_GRID_FULL  = [4096, 16384]
N_GRID_SMOKE = [1024, 4096]   # smoke uses smaller N values

# Depth sweep grid
DEPTH_GRID = [1, 2, 3, 5]

K_PATHS = 1          # K=1 fixed throughout (null prediction at single-hop)
K_RANDOM_KEYS_FULL  = 100
K_RANDOM_KEYS_SMOKE = 20
SEEDS_FULL  = [7, 17, 42]    # 3 seeds per research routing
SEEDS_SMOKE = [17]
DEVICE = torch.device("cpu")  # PROT-022: CPU-force

# Pre-registered bands (verbatim from research routing 2026-06-01)
# HP: depth=1 relative_div <= 10% AND at least one of {depth=3, depth=5}
#     has relative_div > 200% (>2x)
HP_D1_REL_DIV_MAX  = 0.10    # 10% max at depth=1
HP_DEEP_REL_DIV_MIN = 2.0    # >2x divergence at depth>=3 required for HP
HF_D1_REL_DIV_MIN  = 0.20    # >20% at depth=1 -> HF
# MIDDLE: depth=1 relative_div in (10%, 20%]

# Smoke N anchor
N_SMOKE = 1024


def get_output_dir(default_name: str = "path_d_percolation_depth_sweep_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                   device: torch.device):
    """Build codebook + W + relation graph."""
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    M_eff = min(M, C)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M_eff, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec  = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


def measure_cell(N_use: int, depth: int, seed: int, k_random_keys: int,
                 device: torch.device) -> Dict:
    """Measure path_b_top1_acc at K=1 for given (N, depth) cell; M=16N fixed."""
    M = 16 * N_use  # alpha=16 fixed (M=16N)

    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)

    # Filter starts: must have depth-level chain
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
        return {"N": N_use, "M": M, "depth": depth, "seed": seed,
                "n_eval": 0, "path_b_top1_acc": None}

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

    pred_b = path_b_run(codebook, W, starts, depth=depth, N_use=N_use)
    path_b_top1_acc = float((pred_b == targets).float().mean().item())

    del codebook, W

    return {
        "N": N_use, "M": M, "depth": int(depth), "seed": int(seed),
        "n_eval": int(starts.shape[0]),
        "path_b_top1_acc": round(path_b_top1_acc, 5),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    """Compute verdict from per-(N, depth, seed) cell results.

    Primary discriminator: depth=1 relative divergence between N_small and N_large
    (the two N values present in cells; for FULL: 4096 and 16384).
    Secondary: whether deep-depth (3 or 5) divergence is >2x (for HP).
    Works for both smoke (N in {1024, 4096}) and full (N in {4096, 16384}) runs.
    """
    if not cells:
        return ("PERC_DEPTH_INCONCLUSIVE", "no cells")

    valid = [c for c in cells if c.get("n_eval", 0) > 0
             and c.get("path_b_top1_acc") is not None]
    if not valid:
        return ("PERC_DEPTH_INCONCLUSIVE", "all cells returned n_eval=0 or None")

    # Group by (N, depth) -> mean path_b_top1_acc
    nd_accs: Dict[Tuple[int, int], List[float]] = {}
    for c in valid:
        key = (c["N"], c["depth"])
        nd_accs.setdefault(key, []).append(c["path_b_top1_acc"])

    nd_means: Dict[Tuple[int, int], float] = {
        k: sum(v) / len(v) for k, v in nd_accs.items()
    }

    detail_parts = [
        f"N={n} d={d} mean={m:.4f}"
        for (n, d), m in sorted(nd_means.items())
    ]
    detail = "; ".join(detail_parts)

    # Compute relative divergence per depth
    # relative_div(d) = |acc(N_large, d) - acc(N_small, d)| / max(acc(N_small, d), 1e-6)
    # Use the actual N values present in cells (works for both smoke and full runs)
    n_values_present = sorted({c["N"] for c in valid})
    if len(n_values_present) < 2:
        return ("PERC_DEPTH_INCONCLUSIVE",
                f"Only one N value present ({n_values_present}); need 2 for divergence. {detail}")
    N_small = n_values_present[0]   # smallest N in this run
    N_large = n_values_present[-1]  # largest N in this run

    rel_divs: Dict[int, float] = {}
    for d in DEPTH_GRID:
        acc_small = nd_means.get((N_small, d))
        acc_large = nd_means.get((N_large, d))
        if acc_small is not None and acc_large is not None:
            denom = max(acc_small, 1e-6)
            rel_divs[d] = abs(acc_large - acc_small) / denom

    if 1 not in rel_divs:
        return ("PERC_DEPTH_INCONCLUSIVE",
                f"depth=1 cells missing for both N values. {detail}")

    d1_div = rel_divs[1]
    deep_divs = {d: v for d, v in rel_divs.items() if d >= 3}
    max_deep_div = max(deep_divs.values()) if deep_divs else 0.0

    div_detail = (
        " | ".join(f"d={d} rel_div={v:.3f}" for d, v in sorted(rel_divs.items()))
    )

    # HARD-FAIL: depth=1 relative_div > 20%
    if d1_div > HF_D1_REL_DIV_MIN:
        return (
            "PERC_DEPTH_HARD_FAIL",
            f"PER_HOP_N_DEPENDENT: depth=1 rel_div={d1_div:.3f} > {HF_D1_REL_DIV_MIN} "
            f"(20%). Percolation framework loses K=1 single-hop prediction. "
            f"Escalate to Test 1B FSS power-law sweep. "
            f"Divs: {div_detail} | {detail}"
        )

    # HARD-PASS: depth=1 N-independent (<=10%) AND deep depth diverges (>2x)
    if d1_div <= HP_D1_REL_DIV_MAX and max_deep_div > HP_DEEP_REL_DIV_MIN:
        return (
            "PERC_DEPTH_HARD_PASS",
            f"COMPOSITION_CLIFF_CONFIRMED: depth=1 rel_div={d1_div:.3f} <= {HP_D1_REL_DIV_MAX} "
            f"(N-independent); max_deep_div={max_deep_div:.3f} > {HP_DEEP_REL_DIV_MIN} "
            f"(2x) at depth>=3. Percolation valid at per-hop; depth-composition is "
            f"new framework gap. Closes percolation refutation. "
            f"Divs: {div_detail} | {detail}"
        )

    # MIDDLE-BAND: depth=1 divergence in (10%, 20%]
    if HP_D1_REL_DIV_MAX < d1_div <= HF_D1_REL_DIV_MIN:
        return (
            "PERC_DEPTH_MIDDLE_BAND",
            f"DEPTH1_AMBIGUOUS: depth=1 rel_div={d1_div:.3f} in "
            f"({HP_D1_REL_DIV_MAX}, {HF_D1_REL_DIV_MIN}]. "
            f"Escalate to 5-seed for tighter statistics. "
            f"Divs: {div_detail} | {detail}"
        )

    # depth=1 N-independent but deep depths not yet diverging (partial data)
    return (
        "PERC_DEPTH_INCONCLUSIVE",
        f"PARTIAL_RESULT: depth=1 rel_div={d1_div:.3f} (N-independent) "
        f"but max_deep_div={max_deep_div:.3f} not exceeding 2x threshold. "
        f"Possibly insufficient seeds or missing deep-depth cells. "
        f"Divs: {div_detail} | {detail}"
    )


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018 assertion
    assert N_FULL == 4096, "PROT-018: base N_FULL must be 4096"
    assert N_GRID_FULL == [4096, 16384], f"N grid mismatch: {N_GRID_FULL}"
    assert K_PATHS == 1, f"K_PATHS must be 1; got {K_PATHS}"
    assert DEPTH_GRID == [1, 2, 3, 5], f"depth grid mismatch: {DEPTH_GRID}"
    assert len(SEEDS_FULL) == 3

    # Formula self-tests from docstring

    # Self-test 1: HP path
    # d=1: acc(4096)=0.025, acc(16384)=0.026 -> rel_div=0.04 <= 0.10 (N-independent)
    # d=5: acc(4096)=0.022, acc(16384)=0.076 -> rel_div=2.45 > 2.0 (deep divergence)
    hp_cells = (
        [{"N": 4096,  "depth": 1, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.025}
         for i in range(3)] +
        [{"N": 16384, "depth": 1, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.026}
         for i in range(3)] +
        [{"N": 4096,  "depth": 3, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.023}
         for i in range(3)] +
        [{"N": 16384, "depth": 3, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.023}
         for i in range(3)] +
        [{"N": 4096,  "depth": 5, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.022}
         for i in range(3)] +
        [{"N": 16384, "depth": 5, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.076}
         for i in range(3)]
    )
    v, msg = compute_verdict(hp_cells)
    assert "HARD_PASS" in v, f"HP self-test gate failed: {v} | {msg}"

    # Self-test 2: HF path
    # d=1: acc(4096)=0.025, acc(16384)=0.060 -> rel_div=1.40 > 0.20 -> HF
    hf_cells = (
        [{"N": 4096,  "depth": 1, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.025}
         for i in range(3)] +
        [{"N": 16384, "depth": 1, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.060}
         for i in range(3)]
    )
    v, msg = compute_verdict(hf_cells)
    assert "HARD_FAIL" in v, f"HF self-test gate failed: {v} | {msg}"

    # Self-test 3: MIDDLE-BAND path
    # d=1: acc(4096)=0.025, acc(16384)=0.029 -> rel_div=0.16 in (0.10, 0.20] -> MIDDLE
    mid_cells = (
        [{"N": 4096,  "depth": 1, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.025}
         for i in range(3)] +
        [{"N": 16384, "depth": 1, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.029}
         for i in range(3)] +
        [{"N": 4096,  "depth": 5, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.022}
         for i in range(3)] +
        [{"N": 16384, "depth": 5, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.076}
         for i in range(3)]
    )
    v, msg = compute_verdict(mid_cells)
    assert "MIDDLE_BAND" in v, f"MIDDLE self-test gate failed: {v} | {msg}"

    # Self-test 4: Inconclusive -- no cells
    v, _ = compute_verdict([])
    assert "INCONCLUSIVE" in v, f"Inconclusive gate failed: {v}"

    # Live smoke forward pass: N=1024 (even log2), depth=1, seed=17
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, depth=1, seed=17,
                       k_random_keys=10, device=device)
    assert out.get("n_eval", 0) > 0, f"selftest: 0 starts at smoke scale: {out}"
    assert out.get("path_b_top1_acc") is not None, "path_b_top1_acc is None at depth=1"
    assert 0.0 <= out["path_b_top1_acc"] <= 1.0, \
        f"path_b_top1_acc out of range: {out['path_b_top1_acc']}"
    assert out["M"] == 16 * N_SMOKE, f"M not 16*N_SMOKE: {out['M']}"
    assert out["depth"] == 1, f"depth field mismatch: {out['depth']}"

    # Also verify depth=3 at smoke scale
    out3 = measure_cell(N_SMOKE, depth=3, seed=17,
                        k_random_keys=10, device=device)
    assert out3.get("n_eval", 0) > 0, f"selftest: 0 starts at depth=3 smoke: {out3}"
    assert out3.get("path_b_top1_acc") is not None, "path_b_top1_acc is None at depth=3"

    print(
        f"[selftest] path_d_percolation_depth_sweep_v1_n4096 PASS "
        f"smoke N={N_SMOKE} M={16*N_SMOKE} "
        f"d=1 acc={out['path_b_top1_acc']:.3f} n_eval={out['n_eval']} | "
        f"d=3 acc={out3['path_b_top1_acc']:.3f} n_eval={out3['n_eval']}",
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
    smoke  = args.smoke
    n_grid  = N_GRID_SMOKE  if smoke else N_GRID_FULL
    seeds   = SEEDS_SMOKE   if smoke else SEEDS_FULL
    k_keys  = K_RANDOM_KEYS_SMOKE if smoke else K_RANDOM_KEYS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    total_cells = len(n_grid) * len(DEPTH_GRID) * len(seeds)
    cell_num = 0

    print(
        f"[run] path_d_percolation_depth_sweep_v1_n4096 smoke={smoke} "
        f"N_grid={n_grid} depth_grid={DEPTH_GRID} "
        f"K=1 alpha=16 seeds={seeds} k_random_keys={k_keys} "
        f"total_cells={total_cells} done={len(done)} device={device.type}",
        flush=True,
    )

    cells: List[Dict] = []
    for N_val in n_grid:
        for depth in DEPTH_GRID:
            for seed in seeds:
                cell_num += 1
                ck = f"N{N_val}_d{depth}_seed{seed}"
                if ck in done:
                    body = load_partial_key(out_dir, ck)
                    if body is not None:
                        cells.append(body)
                        print(
                            f"  [cell {cell_num}/{total_cells}] "
                            f"N={N_val} d={depth} seed={seed} RESUMED",
                            flush=True,
                        )
                        continue
                try:
                    out = measure_cell(N_val, depth=depth, seed=seed,
                                       k_random_keys=k_keys, device=device)
                    write_partial_key(out_dir, ck, out)
                    cells.append(out)
                    elapsed_s = time.time() - t0
                    print(
                        f"  [cell {cell_num}/{total_cells}] "
                        f"N={N_val} d={depth} seed={seed} "
                        f"acc={out.get('path_b_top1_acc', 'N/A')} "
                        f"n_eval={out.get('n_eval', 0)} "
                        f"({elapsed_s:.1f}s)",
                        flush=True,
                    )
                except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
                    print(
                        f"  [cell {cell_num}/{total_cells}] "
                        f"N={N_val} d={depth} seed={seed} FAILED: {e}",
                        flush=True,
                    )

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)

    # Multi-scale smoke check: for smoke mode, log both N values
    summary = {
        "anchor": "path_d_percolation_depth_sweep_v1_n4096",
        "N_grid": n_grid,
        "depth_grid": DEPTH_GRID,
        "smoke": smoke,
        "K_paths": K_PATHS,
        "k_random_keys": k_keys,
        "seeds": seeds,
        "cells": cells,
        "verdict": verdict,
        "verdict_msg": vm,
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
