"""SPARSE-W ACTIVE-SUBSPACE FEASIBILITY v1 at N=4096.

CONTEXT:
  Standard W stores M rank-1 outer products in a dense N x N matrix
  (storage = N^2). For sparse storage we keep only the rank-1 components
  (M values + M keys = 2 * M * N storage). At M < N/2, this gives memory
  savings.

SCIENTIFIC QUESTION:
  Does sparse-W store-and-retrieve work?
    - At M sweep [32, 64, 128, 256, 512, 1024]: retrieval accuracy?
    - Memory ratio M-linear (2*M*N) vs dense (N*N) = 2*M/N.
    - Does KF-2 isolation hold under sparse storage?

PRE-REGISTERED BANDS:
  HARD_PASS: sparse W at M=128 uses <= 1/4 memory of dense AT >= 95%
    retention AND KF-2 max_iso <= 0.05.
  HARD_FAIL: sparse loses >= 20% accuracy at any tested M.
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N=4096 (PROT-018).
  2. Memory ratio at M=128, N=4096: 2*128/4096 = 0.0625 < 0.25. PASS condition.
  3. Sparse retrieval: out = sum_i v_i * (k_i . k_query) / N
     = (keys.T @ values).T @ k_query / N = W_dense @ k_query / N. Mathematically
     EQUIVALENT to dense retrieval, so accuracy should be identical (modulo
     numerical precision).

OOM CHECK: M_max=1024, N=4096. Keys 1024*4096*4=16.8MB. Vals same. Total ~35MB.
  CB 805MB. OK.

TIMEOUT ESTIMATE: 6 M values * 5 seeds. ~5s/cell. ~150s. Budget 14400s.

N-suffix: _n4096 (PROT-018).
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

from experiments._metric_battery import make_substrate, metric_max_iso  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_spr", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
M_SWEEP_FULL  = [32, 64, 128, 256, 512, 1024]
M_SWEEP_SMOKE = [16, 32, 64]
BETA = 8.0
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 200

HP_M_FOR_SAVINGS = 128
HP_MEM_RATIO = 0.25
HP_RETENTION = 0.95
HP_MAX_ISO = 0.05
HF_LOSS = 0.20


def sparse_retrieve(keys: torch.Tensor, values: torch.Tensor,
                     k_query: torch.Tensor, N_use: int) -> torch.Tensor:
    """Sparse retrieval: out = sum_i v_i * (k_i . k_query) / N.

    keys: (M, N), values: (M, N), k_query: (n_q, N).
    Returns out: (n_q, N) = (k_query @ keys.T) @ values / N.
    """
    return (k_query @ keys.T) @ values / N_use


def get_output_dir(default_name: str = "sparse_w_active_subspace_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_sparse(N_use: int, M: int, seed: int,
                    device: torch.device) -> Dict:
    codebook, W, keys, values, key_idx, val_idx = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    n = min(N_PROBE, M)
    probe_keys = keys[:n]
    probe_val_idx = val_idx[:n] % C
    # Sparse retrieval (mathematically equivalent to dense W @ probe)
    out_sparse = sparse_retrieve(keys, values, probe_keys, N_use)
    sims = (codebook @ out_sparse.T) / N_use
    pred = torch.argmax(sims, dim=0)
    sparse_ret = float((pred == probe_val_idx.to(device)).float().mean().item())

    # KF-2 isolation via metric battery
    iso = metric_max_iso(W, codebook, key_idx, val_idx, N_use, BETA, seed,
                         device, n_probe=N_PROBE, n_edits=16)
    mem_ratio = 2.0 * M / N_use   # sparse storage / dense storage

    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    return {"M": M, "seed": seed,
            "sparse_retention": round(sparse_ret, 5),
            "kf2_max_iso": round(iso["max_iso"], 5),
            "memory_ratio": round(mem_ratio, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("SP_INCONCLUSIVE", "No cells.")
    # HARD_FAIL: any tested M loses >= 20% accuracy (assume baseline 1.0)
    for c in cells:
        if c["sparse_retention"] <= 1.0 - HF_LOSS:
            return ("SP_HARD_FAIL",
                    f"LARGE_LOSS_AT_M{c['M']}_seed{c['seed']}: "
                    f"ret={c['sparse_retention']:.3f}. n_cells={len(cells)}")
    # HARD_PASS: at M=HP_M_FOR_SAVINGS, mem<=0.25, ret>=0.95, iso<=0.05
    hp_cells = [c for c in cells if c["M"] == HP_M_FOR_SAVINGS]
    if not hp_cells:
        return ("SP_INCONCLUSIVE", f"no M={HP_M_FOR_SAVINGS} cells.")
    mem = hp_cells[0]["memory_ratio"]
    ret_avg = sum(c["sparse_retention"] for c in hp_cells) / len(hp_cells)
    iso_avg = sum(c["kf2_max_iso"]      for c in hp_cells) / len(hp_cells)
    detail = (f"M={HP_M_FOR_SAVINGS} mem={mem:.4f} ret={ret_avg:.3f} "
              f"iso={iso_avg:.4f} n_seeds={len(hp_cells)} n_cells={len(cells)}")
    if mem <= HP_MEM_RATIO and ret_avg >= HP_RETENTION and iso_avg <= HP_MAX_ISO:
        return ("SP_HARD_PASS", f"SPARSE_W_WORKS: " + detail)
    return ("SP_MIDDLE_BAND", f"PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    # Sparse formula self-test
    Ns = 8
    keys = torch.eye(2, Ns)
    values = torch.eye(2, Ns) * 3.0
    q = keys[0:1]
    out = sparse_retrieve(keys, values, q, Ns)
    expected = (q @ keys.T) @ values / Ns
    assert torch.allclose(out, expected, atol=1e-6), "sparse formula mismatch"
    # Verify mathematically equivalent to dense W = (values.T @ keys) / N
    W_dense = (values.T @ keys) / Ns
    out_dense = q @ W_dense.T
    assert torch.allclose(out, out_dense, atol=1e-5), (
        f"sparse vs dense divergence: {out.flatten()[:4]} vs {out_dense.flatten()[:4]}")

    # Verdict gates
    fake_hp = [{"M": 128, "seed": s, "sparse_retention": 0.97,
                "kf2_max_iso": 0.02, "memory_ratio": 0.0625}
               for s in [7, 17, 23, 31, 41]] + \
              [{"M": 32, "seed": 17, "sparse_retention": 0.98,
                "kf2_max_iso": 0.01, "memory_ratio": 0.0156}]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v
    fake_hf = [{"M": 128, "seed": 17, "sparse_retention": 0.5,
                "kf2_max_iso": 0.02, "memory_ratio": 0.0625}]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    device = torch.device("cpu")
    out = measure_sparse(N_SMOKE, 32, 17, device)
    assert out["sparse_retention"] is not None
    print(f"[selftest] sparse_w_active_subspace_v1_n4096 PASS "
          f"smoke M=32 ret={out['sparse_retention']:.3f} "
          f"iso={out['kf2_max_iso']:.3f} mem={out['memory_ratio']:.4f}",
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
    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    Ms = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] sparse_w smoke={smoke} N={N_cfg} Ms={Ms} seeds={seeds} "
          f"done={len(done)} device={device_str}", flush=True)

    cells: List[Dict] = []
    for M in Ms:
        for seed in seeds:
            ck = f"M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_sparse(N_cfg, M, seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  M={M} seed={seed} ret={out['sparse_retention']:.3f} "
                      f"iso={out['kf2_max_iso']:.4f} mem={out['memory_ratio']:.4f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  M={M} seed={seed} FAILED: {e}", flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "sparse_w_active_subspace_v1_n4096", "N": N_cfg,
               "smoke": smoke, "Ms": Ms, "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
