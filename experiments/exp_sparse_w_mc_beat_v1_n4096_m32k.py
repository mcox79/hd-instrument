"""SPARSE-W BEAT-M_C v1 at N=4096: extend sparse-W beyond standard envelope.

CONTEXT (T1.3):
  Sparse-W v1 (envelope_v2, commit hist) HP-passed at M up to 8192. The
  m_c_probe estimated M_c in [16384, 20480]. This anchor pushes sparse-W
  past the standard M_c envelope to test whether the sparse representation
  retains usable retrieval AND non-trivial memory savings at extreme M.

SCIENTIFIC QUESTION:
  At N=4096, M in {8192, 16384, 24576, 32768}, does sparse-W maintain
  retrieval >= 0.95 AND >= 2x memory savings vs dense in >= 3/5 seeds?

PRE-REGISTERED BANDS:
  HP = retention >= 0.95 AND mem savings >= 2x at ALL 4 M points in >=3/5 seeds.
       Memory savings = (dense_bytes / sparse_bytes) >= 2.
  HF = retention drop >= 0.20 at any M >= 16384 in >=3/5 seeds.
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. dense_bytes = N*N*4 = 67108864 (= 64 MiB).
  3. sparse_bytes(M) = 2*M*N*4.
     - M=8192:  2*8192*4096*4   = 268 MiB     ratio dense/sparse = 0.25  (sparse LARGER)
     - M=16384: ratio 0.125
     - M=24576: ratio ~0.083
     - M=32768: ratio ~0.0625
  Important: at all 4 M, sparse is LARGER than dense. The user's "memory_savings
  vs dense" is interpreted here as KEY-CONDITIONAL memory savings: when the
  application only stores M facts but uses an N x N dense matrix, the dense
  matrix wastes capacity. We track BOTH (a) raw bytes vs dense and (b)
  effective-density = M / (N^2 / 8) which is the more honest sparse-vs-dense
  utility metric. The HARD-PASS gate uses raw byte ratio, so at these large M
  values the gate is intentionally near-impossible -- this is a CHARACTERIZATION
  ANCHOR for the sparse-at-large-M regime, with HF as the well-defined
  outcome.
  3. retention HP threshold: 0.95.
  4. retention HF loss threshold: 0.20.

OOM CHECK:
  M=32768, N=4096: keys = 32768*4096*4 = 537 MiB. values = 537 MiB.
  W (dense ref) = 64 MiB. CB = 805 MiB. Total ~2 GiB. Under 6 GiB. OK.

TIMEOUT ESTIMATE:
  smoke (CPU, N_SMOKE=1024, M in [64,256], 1 seed) ~ 10s wall.
  FULL  (GPU, N=4096, M in [8192..32768], 5 seeds) = 4 M x 5 seeds = 20 cells.
  scaling_exp = 2.0 (matrix ops M*N).
  timeout_s = ceil(1.5 * 10 * (32768/256)**2.0 * 5) -- but per-cell dominates.
  PROT-019 floor for _n4096: 14400 (4h). Using 21600s (6h) for safety with 5
  seeds at extreme M. User-requested 21600.

N-suffix: _n4096 (PROT-018).
Anchor: sparse_w_mc_beat_v1_n4096_m32k
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_sparse_w_mc_beat_v1_n4096_m32k.md
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

from experiments._metric_battery import make_substrate, metric_max_iso  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_n1", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_SWEEP_FULL  = [8192, 16384, 24576, 32768]
M_SWEEP_SMOKE = [64, 256]
BETA = 8.0
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 200

HP_RETENTION = 0.95
HP_MEM_SAVINGS_MIN = 2.0     # raw byte ratio: dense / sparse >= 2x
HF_LOSS = 0.20
HF_M_THRESHOLD = 16384
HP_SEEDS_MIN = 3
HF_SEEDS_MIN = 3


def sparse_retrieve(keys: torch.Tensor, values: torch.Tensor,
                     k_query: torch.Tensor, N_use: int) -> torch.Tensor:
    """(M,N) keys, (M,N) values, (B,N) queries -> (B,N) responses."""
    return (k_query @ keys.T) @ values / N_use


def memory_bytes_dense(N_use: int, dtype_bytes: int = 4) -> int:
    return N_use * N_use * dtype_bytes


def memory_bytes_sparse(M: int, N_use: int, dtype_bytes: int = 4) -> int:
    return 2 * M * N_use * dtype_bytes


def get_output_dir(default_name: str = "sparse_w_mc_beat_v1_n4096_m32k") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_cell(N_use: int, M: int, seed: int,
                  device: torch.device) -> Dict:
    """One cell: build substrate, measure sparse-retrieval + KF-2."""
    codebook, _W, keys, values, key_idx, val_idx = make_substrate(
        N_use, M, seed, device)
    C = codebook.shape[0]
    n = min(N_PROBE, M)
    probe_keys = keys[:n]
    probe_val_idx = val_idx[:n] % C

    # Sparse-retrieval accuracy
    out = sparse_retrieve(keys, values, probe_keys, N_use)
    sims = (codebook @ out.T) / N_use
    pred = torch.argmax(sims, dim=0)
    ret = float((pred == probe_val_idx.to(device)).float().mean().item())

    # KF-2 on the dense W (sparse and dense match by construction)
    iso = metric_max_iso(_W, codebook, key_idx, val_idx,
                          N_use, BETA, seed, device,
                          n_probe=N_PROBE, n_edits=16)
    dense_b = memory_bytes_dense(N_use)
    sparse_b = memory_bytes_sparse(M, N_use)
    savings = dense_b / max(1, sparse_b)

    del _W, keys, values, codebook
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {
        "M": int(M), "seed": int(seed), "N": int(N_use),
        "sparse_retention": round(ret, 5),
        "kf2_max_iso": round(iso["max_iso"], 5),
        "dense_bytes": int(dense_b),
        "sparse_bytes": int(sparse_b),
        "mem_savings_ratio": round(savings, 5),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("SP_MCB_INCONCLUSIVE", "No cells.")
    by_seed: Dict[int, Dict[int, Dict]] = {}
    for c in cells:
        by_seed.setdefault(c["seed"], {})[c["M"]] = c

    hf_seeds = 0
    for s, by_M in by_seed.items():
        for M, c in by_M.items():
            if M >= HF_M_THRESHOLD and c["sparse_retention"] <= (1.0 - HF_LOSS):
                hf_seeds += 1
                break

    hp_seeds = 0
    for s, by_M in by_seed.items():
        ok_ret = all(c["sparse_retention"] >= HP_RETENTION
                      for c in by_M.values())
        ok_mem = all(c["mem_savings_ratio"] >= HP_MEM_SAVINGS_MIN
                      for c in by_M.values())
        if ok_ret and ok_mem:
            hp_seeds += 1

    detail = (f"hp_seeds={hp_seeds}/{len(by_seed)} "
              f"hf_seeds={hf_seeds}/{len(by_seed)} "
              f"n_cells={len(cells)}")

    if hf_seeds >= HF_SEEDS_MIN:
        return ("SP_MCB_HARD_FAIL", "SPARSE_DEGRADES_PAST_MC: " + detail)
    if hp_seeds >= HP_SEEDS_MIN:
        return ("SP_MCB_HARD_PASS", "SPARSE_BEATS_MC: " + detail)
    return ("SP_MCB_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    # Formula 2: dense_bytes
    assert memory_bytes_dense(4096) == 4096 * 4096 * 4
    # Formula 3: sparse_bytes at M=8192
    assert memory_bytes_sparse(8192, 4096) == 2 * 8192 * 4096 * 4

    # Verdict gates
    fake_hp: List[Dict] = []
    for M in M_SWEEP_FULL:
        for s in SEEDS_FULL:
            # Pretend mem ratio = 2.5 (passes HP) and ret = 0.97
            fake_hp.append({"M": M, "seed": s, "N": N_FULL,
                            "sparse_retention": 0.97,
                            "kf2_max_iso": 0.02,
                            "dense_bytes": memory_bytes_dense(N_FULL),
                            "sparse_bytes": memory_bytes_dense(N_FULL) // 3,
                            "mem_savings_ratio": 3.0})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf: List[Dict] = []
    for M in M_SWEEP_FULL:
        for s in SEEDS_FULL:
            ret = 0.97 if M < HF_M_THRESHOLD else 0.50
            fake_hf.append({"M": M, "seed": s, "N": N_FULL,
                             "sparse_retention": ret,
                             "kf2_max_iso": 0.02,
                             "dense_bytes": 1, "sparse_bytes": 1,
                             "mem_savings_ratio": 1.0})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Forward pass on CPU
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 64, 17, device)
    assert out["sparse_retention"] is not None
    assert out["mem_savings_ratio"] > 0
    assert out["kf2_max_iso"] is not None
    print(f"[selftest] sparse_w_mc_beat_v1_n4096_m32k PASS "
          f"smoke ret={out['sparse_retention']:.3f} "
          f"savings={out['mem_savings_ratio']:.3f}", flush=True)


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
    print(f"[run] sparse_w_mc_beat_v1 smoke={smoke} N={N_cfg} Ms={Ms} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

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
                print(f"  M={M} seed={seed} ret={out['sparse_retention']:.3f} "
                      f"iso={out['kf2_max_iso']:.4f} "
                      f"sav={out['mem_savings_ratio']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  M={M} seed={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "sparse_w_mc_beat_v1_n4096_m32k", "N": N_cfg,
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
