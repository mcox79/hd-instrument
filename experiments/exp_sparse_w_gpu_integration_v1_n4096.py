"""SPARSE-W GPU-INTEGRATION v1 at N=4096 (T4.3).

CONTEXT (T4.3):
  Sparse-W (memory savings) + GPU (latency reduction) confirmed
  independently. Test combined: sparse-W substrate running on GPU.
  Verify both savings preserve AND killer features pass.

SCIENTIFIC QUESTION:
  At N=4096, M in {128, 1024, 4096}, does sparse-W on GPU achieve:
  (a) latency competitive with dense GPU (within 2x),
  (b) >= 4x memory savings preserved,
  (c) killer features (retention + KF-2) pass?

PRE-REGISTERED BANDS:
  HP = sparse_gpu_lat <= 2 * dense_gpu_lat AND mem_savings >= 4x AND
       killer features (retention >= 0.95 AND KF-2 <= 0.05) at all M
       in >=2/3 seeds.
  HF = sparse_gpu_lat > 2 * dense_gpu_lat OR killer features break under
       sparse GPU at any M in >=2/3 seeds.
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. M sweep [128, 1024, 4096].
  3. Sparse retrieve: out = (q @ keys.T) @ values / N.
  4. Dense retrieve: out = q @ W.T where W = (values.T @ keys) / N.
  5. Sparse mem = 2*M*N*4; dense mem = N*N*4.
  6. mem_savings = dense/sparse.

OOM CHECK:
  M=4096, N=4096: keys+vals = 128 MiB. W=64 MiB. CB=805 MiB. ~1GiB. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 30s. FULL: 3 M x 3 seeds x ~30s = 270s. Budget 14400s.

N-suffix: _n4096 (PROT-018).
Anchor: sparse_w_gpu_integration_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_sparse_w_gpu_integration_v1_n4096.md
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

from experiments._metric_battery import (  # noqa: E402
    make_substrate,
    metric_max_iso,
    metric_retention,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_n11", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_SWEEP_FULL  = [128, 1024, 4096]
M_SWEEP_SMOKE = [32, 128]
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
BETA = 8.0
N_TIMING_REPS = 5
N_OPS_PER_TIMING = 30

HP_LAT_RATIO = 2.0   # sparse_gpu_lat / dense_gpu_lat <= 2
HP_MEM_SAV  = 4.0
HP_RET      = 0.95
HP_KF2      = 0.05
HP_SEEDS_MIN = 2
HF_SEEDS_MIN = 2


def get_output_dir(default_name: str = "sparse_w_gpu_integration_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def time_sparse_query(keys: torch.Tensor, values: torch.Tensor,
                       codebook: torch.Tensor, key_idx: torch.Tensor,
                       N_use: int, batch_size: int,
                       device: torch.device, n_reps: int, n_ops: int) -> float:
    M = keys.shape[0]
    for _ in range(2):
        idxs = torch.randint(0, M, (batch_size,), device=device)
        q = keys[idxs]
        coeffs = (q @ keys.T) / N_use
        out = coeffs @ values
        sims = (codebook @ out.T) / N_use
        _ = torch.argmax(sims, dim=0)
        if device.type == "cuda":
            torch.cuda.synchronize()
    times: List[float] = []
    for _ in range(n_reps):
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(n_ops):
            idxs = torch.randint(0, M, (batch_size,), device=device)
            q = keys[idxs]
            coeffs = (q @ keys.T) / N_use
            out = coeffs @ values
            sims = (codebook @ out.T) / N_use
            _ = torch.argmax(sims, dim=0)
        if device.type == "cuda":
            torch.cuda.synchronize()
        t1 = time.perf_counter()
        times.append((t1 - t0) / n_ops)
    return float(sum(times) / len(times))


def time_dense_query(W: torch.Tensor, codebook: torch.Tensor,
                      keys: torch.Tensor, N_use: int, batch_size: int,
                      device: torch.device, n_reps: int, n_ops: int) -> float:
    M = keys.shape[0]
    for _ in range(2):
        idxs = torch.randint(0, M, (batch_size,), device=device)
        q = keys[idxs]
        out = q @ W.T
        sims = (codebook @ out.T) / N_use
        _ = torch.argmax(sims, dim=0)
        if device.type == "cuda":
            torch.cuda.synchronize()
    times: List[float] = []
    for _ in range(n_reps):
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(n_ops):
            idxs = torch.randint(0, M, (batch_size,), device=device)
            q = keys[idxs]
            out = q @ W.T
            sims = (codebook @ out.T) / N_use
            _ = torch.argmax(sims, dim=0)
        if device.type == "cuda":
            torch.cuda.synchronize()
        t1 = time.perf_counter()
        times.append((t1 - t0) / n_ops)
    return float(sum(times) / len(times))


def measure_cell(N_use: int, M: int, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, keys, values, key_idx, val_idx = make_substrate(
        N_use, M, seed, device)

    sparse_lat = time_sparse_query(keys, values, codebook, key_idx,
                                     N_use, batch_size=1, device=device,
                                     n_reps=N_TIMING_REPS,
                                     n_ops=N_OPS_PER_TIMING)
    dense_lat = time_dense_query(W, codebook, keys, N_use, batch_size=1,
                                   device=device,
                                   n_reps=N_TIMING_REPS,
                                   n_ops=N_OPS_PER_TIMING)
    lat_ratio = sparse_lat / max(1e-9, dense_lat)

    # Sparse retention via reference dense W (identical math).
    n_probe = min(200, M)
    probe_keys = keys[:n_probe]
    probe_val_idx = val_idx[:n_probe] % codebook.shape[0]
    coeffs = (probe_keys @ keys.T) / N_use
    out = coeffs @ values
    sims = (codebook @ out.T) / N_use
    pred = torch.argmax(sims, dim=0)
    sparse_ret = float((pred == probe_val_idx.to(device)).float().mean().item())

    m_iso = metric_max_iso(W, codebook, key_idx, val_idx, N_use, BETA,
                            seed, device, n_probe=n_probe, n_edits=16)

    sparse_b = 2 * M * N_use * 4
    dense_b = N_use * N_use * 4
    mem_sav = dense_b / max(1, sparse_b)

    del codebook, W, keys, values
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"M": int(M), "seed": int(seed), "N": int(N_use),
            "sparse_lat_s": sparse_lat,
            "dense_lat_s": dense_lat,
            "lat_ratio_sparse_over_dense": round(lat_ratio, 5),
            "sparse_retention": round(sparse_ret, 5),
            "kf2_max_iso": round(m_iso["max_iso"], 5),
            "sparse_bytes": int(sparse_b),
            "dense_bytes": int(dense_b),
            "mem_savings": round(mem_sav, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("SW_GPU_INCONCLUSIVE", "No cells.")
    by_seed: Dict[int, List[Dict]] = {}
    for c in cells:
        by_seed.setdefault(c["seed"], []).append(c)
    hp_seeds = 0
    hf_seeds = 0
    for s, cs in by_seed.items():
        hp_ok = all(c["lat_ratio_sparse_over_dense"] <= HP_LAT_RATIO
                     and c["mem_savings"] >= HP_MEM_SAV
                     and c["sparse_retention"] >= HP_RET
                     and c["kf2_max_iso"] <= HP_KF2 for c in cs)
        hf_ok = any(c["lat_ratio_sparse_over_dense"] > HP_LAT_RATIO
                     or c["sparse_retention"] < HP_RET
                     or c["kf2_max_iso"] > HP_KF2 for c in cs)
        if hp_ok:
            hp_seeds += 1
        if hf_ok:
            hf_seeds += 1

    detail = f"hp={hp_seeds}/{len(by_seed)} hf={hf_seeds}/{len(by_seed)}"
    if hf_seeds >= HF_SEEDS_MIN:
        return ("SW_GPU_HARD_FAIL", "SPARSE_GPU_BROKE: " + detail)
    if hp_seeds >= HP_SEEDS_MIN:
        return ("SW_GPU_HARD_PASS", "SPARSE_GPU_INTEGRATES: " + detail)
    return ("SW_GPU_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096

    fake_hp = []
    for M in M_SWEEP_FULL:
        for s in SEEDS_FULL:
            sparse_b = 2 * M * N_FULL * 4
            dense_b = N_FULL * N_FULL * 4
            fake_hp.append({"M": M, "seed": s, "N": N_FULL,
                             "sparse_lat_s": 0.01,
                             "dense_lat_s": 0.008,
                             "lat_ratio_sparse_over_dense": 1.25,
                             "sparse_retention": 0.97,
                             "kf2_max_iso": 0.03,
                             "sparse_bytes": sparse_b,
                             "dense_bytes": dense_b,
                             "mem_savings": max(dense_b/sparse_b, 4.0)})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for M in M_SWEEP_FULL:
        for s in SEEDS_FULL:
            fake_hf.append({"M": M, "seed": s, "N": N_FULL,
                             "sparse_lat_s": 0.05,
                             "dense_lat_s": 0.005,
                             "lat_ratio_sparse_over_dense": 10.0,
                             "sparse_retention": 0.50,
                             "kf2_max_iso": 0.50,
                             "sparse_bytes": 1, "dense_bytes": 1,
                             "mem_savings": 1.0})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 32, 17, device)
    assert out["sparse_retention"] is not None
    assert out["lat_ratio_sparse_over_dense"] > 0
    print(f"[selftest] sparse_w_gpu_integration_v1_n4096 PASS "
          f"smoke ret={out['sparse_retention']:.3f} "
          f"lat_ratio={out['lat_ratio_sparse_over_dense']:.3f} "
          f"mem_sav={out['mem_savings']:.3f}", flush=True)


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
    Ms = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] sparse_w_gpu_integration_v1 smoke={smoke} N={N_cfg} "
          f"Ms={Ms} seeds={seeds} done={len(done)} device={device.type}",
          flush=True)

    cells: List[Dict] = []
    for M in Ms:
        for seed in seeds:
            ck = f"M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_cell(N_cfg, M, seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  M={M} seed={seed} "
                      f"lat_ratio={out['lat_ratio_sparse_over_dense']:.3f} "
                      f"ret={out['sparse_retention']:.3f} "
                      f"mem_sav={out['mem_savings']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  M={M} seed={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "sparse_w_gpu_integration_v1_n4096", "N": N_cfg,
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
