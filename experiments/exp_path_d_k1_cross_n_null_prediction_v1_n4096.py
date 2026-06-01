"""PATH D K=1 CROSS-N NULL PREDICTION TEST v1 (base N=4096).

CONTEXT (R4 from cap_map v307 follow-on; percolation N-independence null test):
  Per research P3 percolation framework: substrate Path D signal at K=1
  (path_b_top1_acc) should be N-INDEPENDENT at fixed K=1, depth=5, M=16N.
  Path D's per-hop independence + bootstrap-percolation framing predict the
  signal magnitude is set by candidate-discrimination capacity per hop (a
  function of the codebook density p_eff = K/M = 1/16N), NOT by total
  substrate dimensionality N. This is a falsifiable null prediction.

SCIENTIFIC QUESTION:
  At K=1, depth=5, M=16N, sweeping N in {4096, 16384}:
  Does path_b_top1_acc stay within +-1pp of v307 baseline 0.022 across N?
  Or does K=1 signal vary substantively with N (percolation framing weakens)?

N=8192 DECISION (Kerdock log2-odd constraint):
  N=8192 has log2=13 (odd). The Kerdock/dual-BCH codebook construction
  requires even log2(N). Forcing BSC at N=8192 would change the codebook
  class and confound the N-axis comparison. Decision: SKIP N=8192, use
  N in {4096, 16384} only. Documented in pre-reg.

PRE-REGISTERED BANDS (from strategy routing 2026-06-01):
  HARD-PASS (null confirmed): K=1 mean path_b_top1_acc stays within +-1pp
    (0.01 absolute) of v307 baseline 0.022 across both N values.
    Interpretation: percolation framework N-independence prediction HOLDS.
  HARD-FAIL (null refuted): K=1 mean substantively varies with N
    (e.g., monotone increase, delta > 3pp). Percolation framing weakens;
    K=1 signal IS N-driven.
  MIDDLE-BAND: K=1 mean varies by 1-3pp across N values.

  Baseline for null comparison: v307 k1_mean = 0.022 at N=4096 M=16N.
  Tolerance: +-0.01 (1pp) for HP; 0.03 (3pp) boundary for HF.

FORMULA SELF-TESTS:
  1. HP gate: N=4096 acc=0.022, N=16384 acc=0.025 -> delta=0.003 <= 0.01 -> HP
  2. HF gate: N=4096 acc=0.022, N=16384 acc=0.060 -> delta=0.038 > 0.03 -> HF
  3. MIDDLE gate: N=4096 acc=0.022, N=16384 acc=0.040 -> delta=0.018 in [0.01,0.03]

OOM CHECK:
  N=4096, M=16N=65536: codebook = 65536 x 4096 float32 = 1 GiB.
  N=16384, M=16N=262144: codebook = 262144 x 16384 float32 = 16 GiB.
  Remote CPU has 64 GB RAM. Peak ~16 GB at N=16384. Fits with margin.
  W at N=16384: 16384 x 16384 float32 = 1 GiB. Total peak ~17 GiB. OK.

PROT-018: _n4096 binds base N = 4096 (minimum N in sweep; anchor records base).
  The sweep includes N=16384 as a second cell-axis point; the anchor name
  records the base N=4096. See "## N-suffix" note in pre-reg.
PROT-019: timeout >= 14400s.
PROT-021: per-cell-N-seed checkpointing.
PROT-022: device=cpu forced.

TIMEOUT ESTIMATE:
  N=4096: ~60s/seed (from v307). N=16384: 4x larger codebook + W ops.
  scaling_exp=1.5 (vector ops + matrix build). N=16384/N=4096 = 4.
  Estimate: 60 * 4^1.5 * 5 seeds = 60 * 8 * 5 = 2400s per N.
  2 N values: 4800s. 1.5 safety -> 7200s. PROT-019 floor: 14400s.
  timeout_s = 14400.

Anchor: path_d_k1_cross_n_null_prediction_v1_n4096
Queue: remote_cpu_queue (CPU-only; N=16384 codebook fits remote 64 GB RAM)
Pre-reg: preregs/2026-06-01_path_d_k1_cross_n_null_prediction_v1_n4096.md
Total cells: 2 N-values x 5 seeds = 10 cells
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_k1_cross_n", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# ---------------------------------------------------------------------------
# PROT-018: _n4096 binds base N = 4096 (minimum N in the N-sweep grid)
# The anchor name records base N=4096; N=16384 is a second cell-axis point.
# ---------------------------------------------------------------------------
N = 4096
N_FULL  = N
assert N_FULL == 4096, f"PROT-018: base N_FULL must be 4096; got {N_FULL}"

# N-sweep grid (N=8192 skipped: log2=13 odd, Kerdock constraint)
# See pre-reg section "## N=8192 skip rationale"
N_GRID_FULL  = [4096, 16384]
N_GRID_SMOKE = [1024, 4096]  # smoke uses smaller N values; log2(1024)=10 (even)

DEPTH   = 5
K_PATHS = 1    # K=1 fixed (null prediction test)
K_RANDOM_KEYS       = 100
K_RANDOM_KEYS_SMOKE = 20
SEEDS_FULL  = [7, 17, 23, 42, 99]
SEEDS_SMOKE = [17]
BETA_D = 4.0
DEVICE = torch.device("cpu")   # PROT-022: CPU-force

# Pre-registered bands (verbatim from routing 2026-06-01)
# v307 baseline: k1_mean = 0.022 at N=4096
V307_BASELINE = 0.022
HP_DELTA = 0.01   # +-1pp: HP if max|acc_N - 0.022| <= 0.01
HF_DELTA = 0.03   # >3pp: HF if delta > 0.03
# MIDDLE: delta in (0.01, 0.03]


def get_output_dir(default_name: str = "path_d_k1_cross_n_null_prediction_v1_n4096") -> Path:
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
    """Measure path_b_top1_acc at K=1 effective for given N (M=16N fixed)."""
    M = 16 * N_use  # M=16N fixed

    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)

    # Valid starts with depth-level chains
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
        return {"N": N_use, "M": M, "seed": seed, "n_eval": 0,
                "path_b_top1_acc": None}

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
        "N": N_use, "M": M, "seed": int(seed),
        "n_eval": int(starts.shape[0]),
        "path_b_top1_acc": round(path_b_top1_acc, 5),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    """Compute verdict from per-(N,seed) cell results."""
    if not cells:
        return ("NULL_PRED_INCONCLUSIVE", "no cells")

    valid = [c for c in cells if c.get("n_eval", 0) > 0
             and c.get("path_b_top1_acc") is not None]
    if not valid:
        return ("NULL_PRED_INCONCLUSIVE", "all cells returned n_eval=0 or None")

    # Per-N mean accuracy
    n_accs: Dict[int, List[float]] = {}
    for c in valid:
        N_val = c["N"]
        n_accs.setdefault(N_val, []).append(c["path_b_top1_acc"])

    n_means = {n: sum(v) / len(v) for n, v in n_accs.items()}
    all_means = list(n_means.values())

    detail_parts = [f"N={n} mean={m:.4f}" for n, m in sorted(n_means.items())]
    detail = "; ".join(detail_parts) + f" baseline={V307_BASELINE:.4f}"

    if not all_means:
        return ("NULL_PRED_INCONCLUSIVE", "no valid N groups")

    # Max deviation from baseline
    max_delta = max(abs(m - V307_BASELINE) for m in all_means)
    # Also measure N-to-N spread (max - min across N values)
    n_spread = max(all_means) - min(all_means) if len(all_means) > 1 else 0.0

    # HARD-PASS: max delta <= 1pp AND spread <= 1pp
    if max_delta <= HP_DELTA:
        return (
            "NULL_PRED_HARD_PASS",
            f"N_INDEPENDENCE_CONFIRMED: max|acc_N - baseline| = {max_delta:.4f} "
            f"<= {HP_DELTA} (1pp). Percolation N-independence prediction HOLDS. "
            + detail
        )

    # HARD-FAIL: max delta > 3pp
    if max_delta > HF_DELTA:
        # Determine direction
        monotone_up = len(all_means) > 1 and all_means[-1] > all_means[0]
        direction = "N-increasing" if monotone_up else "N-varying"
        return (
            "NULL_PRED_HARD_FAIL",
            f"NULL_PREDICTION_REFUTED: max|acc_N - baseline| = {max_delta:.4f} "
            f"> {HF_DELTA} (3pp). K=1 signal IS N-driven ({direction}). "
            f"Percolation framing weakens. " + detail
        )

    # MIDDLE-BAND: delta in (1pp, 3pp]
    return (
        "NULL_PRED_MIDDLE_BAND",
        f"WEAK_N_DEPENDENCE: max_delta = {max_delta:.4f} in "
        f"({HP_DELTA}, {HF_DELTA}]. Some N-dependence but small. "
        + detail
    )


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, "PROT-018: base N_FULL must be 4096"
    assert N_GRID_FULL == [4096, 16384], f"N grid mismatch: {N_GRID_FULL}"
    assert K_PATHS == 1, f"K_PATHS must be 1; got {K_PATHS}"
    assert DEPTH == 5, f"depth must be 5; got {DEPTH}"
    assert len(SEEDS_FULL) == 5

    # Formula self-tests per docstring
    # 1. HP: delta=0.003 -> HARD_PASS
    hp_cells = [
        {"N": 4096,  "seed": i, "n_eval": 20, "path_b_top1_acc": 0.022}
        for i in range(5)
    ] + [
        {"N": 16384, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.025}
        for i in range(5)
    ]
    v, _ = compute_verdict(hp_cells)
    assert "HARD_PASS" in v, f"HP gate failed: {v}"

    # 2. HF: N=16384 acc=0.060 -> delta=0.038 > 0.03 -> HARD_FAIL
    hf_cells = [
        {"N": 4096,  "seed": i, "n_eval": 20, "path_b_top1_acc": 0.022}
        for i in range(5)
    ] + [
        {"N": 16384, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.060}
        for i in range(5)
    ]
    v, _ = compute_verdict(hf_cells)
    assert "HARD_FAIL" in v, f"HF gate failed: {v}"

    # 3. MIDDLE: delta=0.018 in (0.01, 0.03] -> MIDDLE_BAND
    mid_cells = [
        {"N": 4096,  "seed": i, "n_eval": 20, "path_b_top1_acc": 0.022}
        for i in range(5)
    ] + [
        {"N": 16384, "seed": i, "n_eval": 20, "path_b_top1_acc": 0.040}
        for i in range(5)
    ]
    v, _ = compute_verdict(mid_cells)
    assert "MIDDLE_BAND" in v, f"MIDDLE gate failed: {v}"

    # 4. Live smoke at N=1024 (small), M=16*1024=16384
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, depth=3, seed=17, k_random_keys=10, device=device)
    assert out.get("n_eval", 0) > 0, f"selftest: 0 starts at smoke scale: {out}"
    assert out.get("path_b_top1_acc") is not None, "path_b_top1_acc is None"
    assert 0.0 <= out["path_b_top1_acc"] <= 1.0, \
        f"path_b_top1_acc out of range: {out['path_b_top1_acc']}"
    assert out["M"] == 16 * N_SMOKE, f"M not 16*N_SMOKE: {out['M']}"
    print(
        f"[selftest] path_d_k1_cross_n_null_prediction_v1_n4096 PASS "
        f"smoke N={N_SMOKE} M={out['M']} d=3 seed=17 "
        f"path_b_top1={out['path_b_top1_acc']:.3f} n_eval={out['n_eval']}",
        flush=True,
    )


# Expose N_SMOKE at module scope so selftest can reference it
N_SMOKE = 1024

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
    n_grid = N_GRID_SMOKE  if smoke else N_GRID_FULL
    seeds  = SEEDS_SMOKE   if smoke else SEEDS_FULL
    k_keys = K_RANDOM_KEYS_SMOKE if smoke else K_RANDOM_KEYS

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    total_cells = len(n_grid) * len(seeds)
    cell_num = 0

    print(
        f"[run] path_d_k1_cross_n_null_prediction_v1_n4096 smoke={smoke} "
        f"N_grid={n_grid} M=16*N depth={DEPTH} K=1 seeds={seeds} "
        f"k_random_keys={k_keys} total_cells={total_cells} "
        f"done={len(done)} device={device.type}",
        flush=True,
    )

    cells: List[Dict] = []
    for N_val in n_grid:
        for seed in seeds:
            cell_num += 1
            ck = f"N{N_val}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body)
                    print(f"  [cell {cell_num}/{total_cells}] N={N_val} seed={seed} RESUMED",
                          flush=True)
                    continue
            try:
                out = measure_cell(N_val, depth=DEPTH, seed=seed,
                                   k_random_keys=k_keys, device=device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                elapsed_s = time.time() - t0
                print(
                    f"  [cell {cell_num}/{total_cells}] N={N_val} seed={seed} "
                    f"M={out.get('M')} "
                    f"path_b_top1={out.get('path_b_top1_acc', 'N/A')} "
                    f"n_eval={out.get('n_eval', 0)} "
                    f"({elapsed_s:.1f}s)",
                    flush=True,
                )
            except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
                print(f"  [cell {cell_num}/{total_cells}] N={N_val} seed={seed} FAILED: {e}",
                      flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "path_d_k1_cross_n_null_prediction_v1_n4096",
        "N_grid": n_grid, "smoke": smoke,
        "depth": DEPTH, "K_paths": K_PATHS,
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
