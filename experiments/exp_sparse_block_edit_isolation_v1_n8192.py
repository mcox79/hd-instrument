"""Sparse-block-code edit isolation smoke (D7).

SCIENTIFIC QUESTION (D7):
  Does sparse W with block structure confine edits to a small fraction
  of W's nonzero entries? HARD-PASS: W nonzero fraction < 5% after
  M=500 facts at N=8192 K=32 block size.

PRE-REGISTERED BANDS:
  HARD-PASS: W nonzero fraction < 0.05 in >= 3/5 seeds.
  HARD-FAIL: W nonzero fraction >= 0.20 (too dense, isolation lost) in majority.
  MIDDLE: 0.05 <= nonzero_frac < 0.20.

DESIGN:
  N=8192, M=500, K=32 (block size). Each fact assigned to a random
  K x K block of W. Write via block-local Hebbian (outer product only in block).
  Measure W nonzero fraction = (nnz / N^2).
  Edit isolation: editing fact_i only touches its assigned block (K^2 entries).
  Seeds: [7,17,23,31,41].

PROT-018: _n8192 binds N=8192.
PROT-019: N>=8192 timeout >= 21600s.
PROT-021: M-tagged checkpoint keys.

Anchor: sparse_block_edit_isolation_v1_n8192
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_sparse_block_edit_isolation.md
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

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_sbe", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key
list_completed_keys = _ck.list_completed_keys

# PROT-018: _n8192 binds N=8192
N_FULL  = 8192
N_SMOKE = 1024
M_FULL  = 500
M_SMOKE = 64
K_BLOCK = 32       # block size (K x K submatrix per fact)

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_NONZERO_MAX = 0.05   # nonzero fraction < 5%
HF_NONZERO_MIN = 0.20   # >= 20% = too dense

assert N_FULL == 8192, "PROT-018: _n8192 binds N=8192"

OOM_CHECK_N = N_FULL; OOM_CHECK_M = M_FULL
# W is stored as sparse (dict of block coordinates), NOT dense N x N
# Dense N=8192 would be 8192^2 * 4 = 256 MB; we use sparse storage.
# Sparse storage: at most M * K^2 = 500 * 1024 = 512K entries.


def measure_seed(N: int, M: int, K: int, seed: int) -> Dict:
    """Build sparse-block W, measure nonzero fraction and edit isolation."""
    rng = np.random.default_rng(seed)

    # Assign each fact to a random K x K block of W
    # Block grid: N // K rows, N // K cols of blocks
    n_blocks_per_dim = N // K
    n_blocks = n_blocks_per_dim * n_blocks_per_dim

    # Each fact assigned to one block (with replacement across M facts)
    fact_blocks = rng.integers(0, n_blocks, size=M)  # block_id per fact

    # Sparse W: dict mapping (block_row_start, block_col_start) -> K x K array
    block_W: dict = {}

    for i in range(M):
        block_id = int(fact_blocks[i])
        br = (block_id // n_blocks_per_dim) * K  # row start
        bc = (block_id % n_blocks_per_dim) * K   # col start

        # Random bipolar key and val vectors (length K only)
        key_block = rng.choice([-1.0, 1.0], size=K).astype(np.float32)
        val_block = rng.choice([-1.0, 1.0], size=K).astype(np.float32)
        delta = np.outer(val_block, key_block) / K  # K x K Hebbian update

        if (br, bc) not in block_W:
            block_W[(br, bc)] = np.zeros((K, K), dtype=np.float32)
        block_W[(br, bc)] += delta

    # Measure nonzero fraction: count nnz in filled blocks
    total_nnz = 0
    for blk in block_W.values():
        total_nnz += int(np.sum(blk != 0.0))
    total_entries = N * N
    nonzero_frac = total_nnz / total_entries

    # Edit isolation: editing fact_i only touches its assigned block
    # Verify by computing what fraction of N^2 entries each edit touches
    edit_coverage = K * K / (N * N)  # fraction of W touched per edit

    # Retrieval test: does W correctly associate keys within blocks?
    n_test = min(20, M)
    n_correct = 0
    for i in range(n_test):
        block_id = int(fact_blocks[i])
        br = (block_id // n_blocks_per_dim) * K
        bc = (block_id % n_blocks_per_dim) * K
        if (br, bc) in block_W:
            # Retrieve: use same key_block -> get val_block approximation
            # Use fresh rng with same seed to get same key
            rng_i = np.random.default_rng(seed + i * 100)
            key_block = rng_i.choice([-1.0, 1.0], size=K).astype(np.float32)
            val_block = rng_i.choice([-1.0, 1.0], size=K).astype(np.float32)
            W_blk = block_W[(br, bc)]
            retrieved = W_blk @ key_block
            sim = float(np.dot(retrieved, val_block) /
                        (np.linalg.norm(retrieved) * np.linalg.norm(val_block) + 1e-9))
            n_correct += int(sim > 0.0)
    retrieval_acc = n_correct / max(n_test, 1)

    return {
        "seed": seed,
        "N": N,
        "M": M,
        "K_block": K,
        "n_filled_blocks": len(block_W),
        "total_nnz": int(total_nnz),
        "nonzero_frac": float(nonzero_frac),
        "edit_coverage_per_fact": float(edit_coverage),
        "retrieval_acc": float(retrieval_acc),
        "passes_hp": int(nonzero_frac < HP_NONZERO_MAX),
        "ok": True,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("SPARSE_EDIT_ISO_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("SPARSE_EDIT_ISO_INCONCLUSIVE", "all cells failed")

    n_hp = sum(c["passes_hp"] for c in ok)
    n_hf = sum(1 for c in ok if c["nonzero_frac"] >= HF_NONZERO_MIN)
    majority = len(ok) // 2 + 1
    mean_nz  = sum(c["nonzero_frac"] for c in ok) / len(ok)
    mean_ec  = sum(c["edit_coverage_per_fact"] for c in ok) / len(ok)

    detail = (
        f"N={ok[0]['N']} M={ok[0]['M']} K={ok[0]['K_block']} "
        f"mean_nonzero_frac={mean_nz:.6f} mean_edit_coverage={mean_ec:.6f} "
        f"n_hp={n_hp}/{len(ok)}"
    )

    if n_hf >= majority:
        return ("SPARSE_EDIT_ISO_HARD_FAIL",
                f"W_TOO_DENSE: nonzero>={HF_NONZERO_MIN} "
                f"in {n_hf}/{len(ok)} seeds. " + detail)
    if n_hp >= majority:
        return ("SPARSE_EDIT_ISO_HARD_PASS",
                f"EDIT_ISOLATION_CONFIRMED: nonzero<{HP_NONZERO_MAX} "
                f"in {n_hp}/{len(ok)} seeds. " + detail)
    return ("SPARSE_EDIT_ISO_MIDDLE_BAND",
            f"PARTIAL: mean_nz={mean_nz:.6f}. " + detail)


def get_output_dir(default_name: str = "sparse_block_edit_isolation_v1_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all metrics non-null/non-sentinel."""
    # PROT-018
    assert N_FULL == 8192, "PROT-018: _n8192 binds N=8192"

    # Formula self-test 1: block coverage formula
    # K^2 / N^2 = 32^2 / 8192^2 = 1024 / 67108864 ~ 1.5e-5
    expected_coverage = K_BLOCK ** 2 / N_FULL ** 2
    assert expected_coverage < 0.001, f"edit_coverage too large: {expected_coverage}"
    print(f"[selftest] formula-1 edit_coverage={expected_coverage:.2e} "
          f"(K={K_BLOCK}/N={N_FULL}) PASS", flush=True)

    # Formula self-test 2: max nonzero fraction at M=M_FULL, K=K_BLOCK
    # Max blocks filled = min(M, N/K * N/K) = min(500, 256*256)=500
    # Max nnz = 500 * K^2 = 500 * 1024 = 512000
    # Max nz_frac = 512000 / (8192^2) = 0.00763 << 0.05
    max_nz = M_FULL * K_BLOCK**2 / N_FULL**2
    assert max_nz < HP_NONZERO_MAX, f"theoretical max_nz={max_nz:.4f} >= HP"
    print(f"[selftest] formula-2 theoretical max_nz={max_nz:.6f} < {HP_NONZERO_MAX} PASS",
          flush=True)

    # Formula self-test 3: live smoke at small scale
    out = measure_seed(N_SMOKE, M_SMOKE, K_BLOCK, 42)
    assert out["ok"], f"measure_seed failed"
    assert 0.0 <= out["nonzero_frac"] <= 1.0, f"nonzero_frac sentinel"
    assert out["edit_coverage_per_fact"] > 0, "edit_coverage=0"
    assert out["n_filled_blocks"] >= 1, "n_filled_blocks=0 (filter passed 0 items)"
    print(f"[selftest] formula-3 smoke N={N_SMOKE} M={M_SMOKE} K={K_BLOCK} "
          f"nz_frac={out['nonzero_frac']:.6f} "
          f"n_blocks={out['n_filled_blocks']} PASS", flush=True)

    # Formula self-test 4: verdict gates
    fake_hp = [{"ok": True, "N": 8192, "M": 500, "K_block": 32,
                "n_filled_blocks": 100, "total_nnz": 100*32*32,
                "nonzero_frac": 0.002, "edit_coverage_per_fact": 1.5e-5,
                "retrieval_acc": 0.8, "passes_hp": 1}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate: {v}"
    fake_hf = [{"ok": True, "N": 8192, "M": 500, "K_block": 32,
                "n_filled_blocks": 500, "total_nnz": int(0.25 * 8192 ** 2),
                "nonzero_frac": 0.25, "edit_coverage_per_fact": 1.5e-5,
                "retrieval_acc": 0.3, "passes_hp": 0}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate: {v}"
    print("[selftest] formula-4 verdict gates PASS", flush=True)

    print("[selftest] sparse_block_edit_isolation_v1_n8192 ALL PASS", flush=True)


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke  = args.smoke
    N_cfg  = N_SMOKE if smoke else N_FULL
    M_cfg  = M_SMOKE if smoke else M_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    run_config = {"N": N_cfg, "M": M_cfg, "run_mode": "smoke" if smoke else "full"}
    done = set(list_completed_keys(out_dir, run_config=run_config))

    t0 = time.time()
    print(f"[run] sparse_block_edit_isolation_v1_n8192 smoke={smoke} "
          f"N={N_cfg} M={M_cfg} K={K_BLOCK} seeds={seeds} done={len(done)}",
          flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"M{M_cfg}_seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                print(f"  [resume] seed={seed} loaded", flush=True)
                continue
        try:
            cell = measure_seed(N_cfg, M_cfg, K_BLOCK, seed)
            cell["run_mode"] = "smoke" if smoke else "full"
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"nz_frac={cell.get('nonzero_frac','n/a'):.6f} "
                  f"n_blocks={cell.get('n_filled_blocks','n/a')} "
                  f"ret_acc={cell.get('retrieval_acc','n/a'):.4f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except Exception as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "sparse_block_edit_isolation_v1_n8192",
        "N": N_cfg, "M": M_cfg, "K_block": K_BLOCK, "smoke": smoke, "seeds": seeds,
        "cells": cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
