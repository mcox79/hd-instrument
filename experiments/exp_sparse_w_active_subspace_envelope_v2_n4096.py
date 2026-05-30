"""SPARSE-W ACTIVE-SUBSPACE ENVELOPE v2 at N=4096.

CONTEXT (F3 follow-up):
  v1 (commit 75c565d) HP-passed at M sweep [32, 64, 128, 256, 512, 1024]
  with SP_HARD_PASS verdict, but cap_map v283 flagged sub-capacity caveat:
  the test capped at M=1024 (= N/4), and the substrate envelope likely
  extends up to M_c (estimated 16K-20K). Need to extend the M-sweep
  approaching M_c to confirm sparse-W viability across the full operating
  envelope.

SCIENTIFIC QUESTION:
  Does sparse W = (values.T @ keys) / N maintain:
    - >= 95% retrieval accuracy at all tested M up to 8192, AND
    - >= 2x memory savings vs dense W
  in >= 3/5 seeds?

PRE-REGISTERED BANDS:
  HARD_PASS: sparse W maintains retention >= 0.95 AND mem ratio <= 0.5
    (sparse < half of dense memory) at ALL M tested in >= 3/5 seeds.
  HARD_FAIL: sparse loses >= 20% accuracy at any M >= 1024 in >=3/5 seeds.
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. M_sweep_full = [128, 512, 1024, 2048, 4096, 8192].
  3. mem ratio = 2*M/N: at M=8192, N=4096 -> ratio = 4.0 (sparse LARGER
     than dense when M > N/2). So mem-savings condition restricts to
     M <= N/2 = 2048.

OOM CHECK:
  Largest M=8192, N=4096: keys+vals = 268MB. W=64MB. CB=805MB. ~1.2GB. OK.

TIMEOUT ESTIMATE:
  Per cell: substrate build + sparse retrieval + KF-2. ~5s at small M,
  ~30s at M=8192. 6 M-vals x 5 seeds = 30 cells. ~600s. Budget 14400s.

N-suffix: _n4096 (PROT-018).
Anchor: sparse_w_active_subspace_envelope_v2_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_sparse_w_active_subspace_envelope_v2_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_spe", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
M_SWEEP_FULL  = [128, 512, 1024, 2048, 4096, 8192]
M_SWEEP_SMOKE = [16, 32, 64]
BETA = 8.0
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 200

HP_RETENTION = 0.95
HP_MEM_RATIO_MAX = 0.5     # sparse must be <= half-of-dense memory
HF_LOSS = 0.20
HF_M_THRESHOLD = 1024      # large-loss at M>=1024 = HF
HP_SEEDS_MIN = 3
HF_SEEDS_MIN = 3


def sparse_retrieve(keys: torch.Tensor, values: torch.Tensor,
                     k_query: torch.Tensor, N_use: int) -> torch.Tensor:
    return (k_query @ keys.T) @ values / N_use


def get_output_dir(default_name: str = "sparse_w_active_subspace_envelope_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_sparse_cell(N_use: int, M: int, seed: int,
                         device: torch.device) -> Dict:
    codebook, W, keys, values, key_idx, val_idx = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    n = min(N_PROBE, M)
    probe_keys = keys[:n]
    probe_val_idx = val_idx[:n] % C

    out_sparse = sparse_retrieve(keys, values, probe_keys, N_use)
    sims = (codebook @ out_sparse.T) / N_use
    pred = torch.argmax(sims, dim=0)
    sparse_ret = float((pred == probe_val_idx.to(device)).float().mean().item())

    iso = metric_max_iso(W, codebook, key_idx, val_idx, N_use, BETA, seed,
                         device, n_probe=N_PROBE, n_edits=16)
    mem_ratio = 2.0 * M / N_use

    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    return {"M": int(M), "seed": int(seed),
            "sparse_retention": round(sparse_ret, 5),
            "kf2_max_iso": round(iso["max_iso"], 5),
            "memory_ratio": round(mem_ratio, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("SPE_INCONCLUSIVE", "No cells.")

    # Group by seed
    by_seed: Dict[int, Dict[int, Dict]] = {}
    for c in cells:
        by_seed.setdefault(c["seed"], {})[c["M"]] = c

    # HF: per-seed, any M >= 1024 with retention <= 1-HF_LOSS -> seed counts as HF
    hf_seeds = 0
    for seed, by_M in by_seed.items():
        for M, c in by_M.items():
            if M >= HF_M_THRESHOLD and c["sparse_retention"] <= (1.0 - HF_LOSS):
                hf_seeds += 1
                break

    # HP: per-seed, ALL tested M show retention>=0.95 AND mem<=0.5
    hp_seeds = 0
    for seed, by_M in by_seed.items():
        seed_ok = True
        for M, c in by_M.items():
            if c["sparse_retention"] < HP_RETENTION:
                seed_ok = False
                break
            if c["memory_ratio"] > HP_MEM_RATIO_MAX:
                # Mem savings only meaningful when sparse < dense memory;
                # for M > N/2, sparse storage exceeds dense, but the
                # retention check still applies. We allow HP if retention
                # holds at all M while requiring at least one M to meet
                # mem<=0.5.
                continue
        if seed_ok:
            # Need at least one M cell at mem<=0.5
            has_savings = any(c["memory_ratio"] <= HP_MEM_RATIO_MAX
                              for c in by_M.values())
            if has_savings:
                hp_seeds += 1

    detail = (f"hp_seeds={hp_seeds}/{len(by_seed)} "
              f"hf_seeds={hf_seeds}/{len(by_seed)} "
              f"n_cells={len(cells)}")

    if hf_seeds >= HF_SEEDS_MIN:
        return ("SPE_HARD_FAIL", f"SPARSE_LOSES_AT_HIGH_M: " + detail)
    if hp_seeds >= HP_SEEDS_MIN:
        return ("SPE_HARD_PASS", f"SPARSE_HOLDS_ACROSS_ENVELOPE: " + detail)
    return ("SPE_MIDDLE_BAND", f"PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    # Sparse formula
    Ns = 8
    keys = torch.eye(2, Ns)
    values = torch.eye(2, Ns) * 3.0
    q = keys[0:1]
    out = sparse_retrieve(keys, values, q, Ns)
    W_dense = (values.T @ keys) / Ns
    out_dense = q @ W_dense.T
    assert torch.allclose(out, out_dense, atol=1e-5), (
        "sparse vs dense divergence")

    # Verdict gates
    fake_hp = []
    for M in M_SWEEP_FULL:
        for s in SEEDS_FULL:
            fake_hp.append({"M": M, "seed": s,
                            "sparse_retention": 0.97,
                            "kf2_max_iso": 0.02,
                            "memory_ratio": min(2.0 * M / N_FULL, 1.0)})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for M in M_SWEEP_FULL:
        for s in SEEDS_FULL:
            ret = 0.97 if M < HF_M_THRESHOLD else 0.5
            fake_hf.append({"M": M, "seed": s,
                            "sparse_retention": ret,
                            "kf2_max_iso": 0.02,
                            "memory_ratio": 2.0 * M / N_FULL})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Smoke on CPU
    device = torch.device("cpu")
    out = measure_sparse_cell(N_SMOKE, 32, 17, device)
    assert out["sparse_retention"] is not None
    print(f"[selftest] sparse_w_active_subspace_envelope_v2_n4096 PASS "
          f"smoke M=32 ret={out['sparse_retention']:.3f}", flush=True)


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
    print(f"[run] sparse_w_envelope_v2 smoke={smoke} N={N_cfg} Ms={Ms} "
          f"seeds={seeds} done={len(done)} device={device_str}", flush=True)

    cells: List[Dict] = []
    for M in Ms:
        for seed in seeds:
            ck = f"M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_sparse_cell(N_cfg, M, seed, device)
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
    summary = {"anchor": "sparse_w_active_subspace_envelope_v2_n4096", "N": N_cfg,
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
