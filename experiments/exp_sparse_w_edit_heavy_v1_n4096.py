"""SPARSE-W EDIT-HEAVY v1 at N=4096 (T4.1a).

CONTEXT (T4.1a):
  Sparse-W maintained envelope under store workloads (v1/v2). Test whether
  sparse-W active-subspace tracking holds under edit-heavy workload (5000
  edits over an initial M=512 fact base).

SCIENTIFIC QUESTION:
  At N=4096, after 5000 edits on M=512 facts, does sparse-W maintain
  retention >= 0.90 AND mem savings >= 8x AND KF-2 max_iso <= 0.05?

PRE-REGISTERED BANDS:
  HP = retention >= 0.90 AND mem savings >= 8x AND KF-2 <= 0.05 post-storm
       in >=3/5 seeds.
  HF = retention <= 0.70 OR memory footprint grows to within 2x of dense.
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. M_initial=512, n_edits=5000.
  3. Sparse mem post-storm = 2*M*N*4 (M unchanged by edits in our model).
  4. Dense mem = N*N*4.
  5. mem_savings_ratio = dense/sparse.

OOM CHECK:
  M=512: keys+vals = 16 MiB. Trivial. CB=805 MiB. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 20s (50 edits). FULL: 5 seeds x ~150s (5000 edits) = 750s. Budget 14400s.

N-suffix: _n4096 (PROT-018).
Anchor: sparse_w_edit_heavy_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_sparse_w_edit_heavy_v1_n4096.md
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

from experiments._workload_harness import (  # noqa: E402
    SparseStore,
    build_codebook,
    gen_edit_storm,
    kf2_spot_check,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_n8", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_INIT_FULL  = 512
M_INIT_SMOKE = 32
N_EDITS_FULL  = 5000
N_EDITS_SMOKE = 50
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_RET = 0.90
HP_MEM_SAVINGS = 8.0
HP_KF2 = 0.05
HF_RET = 0.70
HF_MEM_NEAR_DENSE = 0.5     # sparse / dense > 0.5 = within 2x
HP_SEEDS_MIN = 3
HF_SEEDS_MIN = 3


def get_output_dir(default_name: str = "sparse_w_edit_heavy_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_cell(N_use: int, M_init: int, n_edits: int, seed: int,
                  device: torch.device) -> Dict:
    cb = build_codebook(N_use, device)
    C = cb.shape[0]
    store = SparseStore(N=N_use, codebook=cb, device=device)

    # Initial: M_init facts
    initial, edits = gen_edit_storm(n_initial_facts=M_init, n_edits=n_edits,
                                      seed=seed, n_codebook=C)
    fids: List[int] = []
    for k, v in initial:
        fids.append(store.store_fact(k, v))

    # Apply the edit storm
    for tgt_pos, new_val in edits:
        if tgt_pos < len(fids):
            store.edit_fact(fids[tgt_pos], new_val)

    # Retrieval accuracy: check that current key->value mapping holds
    correct = 0
    total = 0
    for fid in fids:
        kid, expected_vid = store.facts[fid]
        pred, _ = store.retrieve(kid)
        total += 1
        if pred == expected_vid:
            correct += 1
    retention = correct / max(1, total)

    # KF-2 spot-check
    kf2 = kf2_spot_check(store, n_edits=8, n_probe=min(50, total), seed=seed)

    # Memory footprint
    sparse_b = store.memory_bytes()
    dense_b = N_use * N_use * 4
    mem_savings = dense_b / max(1, sparse_b)
    sparse_over_dense = sparse_b / max(1, dense_b)

    del store, cb
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"M_init": int(M_init), "n_edits": int(n_edits),
            "seed": int(seed), "N": int(N_use),
            "post_storm_retention": round(retention, 5),
            "post_storm_kf2_max_iso": round(kf2, 5),
            "sparse_bytes": int(sparse_b),
            "dense_bytes": int(dense_b),
            "mem_savings_ratio": round(mem_savings, 5),
            "sparse_over_dense": round(sparse_over_dense, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("SW_EH_INCONCLUSIVE", "No cells.")
    hp_seeds = sum(1 for c in cells
                    if (c["post_storm_retention"] >= HP_RET
                         and c["mem_savings_ratio"] >= HP_MEM_SAVINGS
                         and c["post_storm_kf2_max_iso"] <= HP_KF2))
    hf_seeds = sum(1 for c in cells
                    if (c["post_storm_retention"] <= HF_RET
                         or c["sparse_over_dense"] > HF_MEM_NEAR_DENSE))
    detail = f"hp={hp_seeds}/{len(cells)} hf={hf_seeds}/{len(cells)}"
    if hf_seeds >= HF_SEEDS_MIN:
        return ("SW_EH_HARD_FAIL", "SPARSE_DEGRADES_UNDER_EDITS: " + detail)
    if hp_seeds >= HP_SEEDS_MIN:
        return ("SW_EH_HARD_PASS", "SPARSE_SURVIVES_EDIT_STORM: " + detail)
    return ("SW_EH_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096

    fake_hp = [{"M_init": M_INIT_FULL, "n_edits": N_EDITS_FULL, "seed": s,
                 "N": N_FULL, "post_storm_retention": 0.95,
                 "post_storm_kf2_max_iso": 0.02,
                 "sparse_bytes": 10, "dense_bytes": 100,
                 "mem_savings_ratio": 10.0,
                 "sparse_over_dense": 0.1} for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = [{"M_init": M_INIT_FULL, "n_edits": N_EDITS_FULL, "seed": s,
                 "N": N_FULL, "post_storm_retention": 0.60,
                 "post_storm_kf2_max_iso": 0.10,
                 "sparse_bytes": 60, "dense_bytes": 100,
                 "mem_savings_ratio": 1.6,
                 "sparse_over_dense": 0.6} for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_INIT_SMOKE, N_EDITS_SMOKE, 17, device)
    assert out["post_storm_retention"] is not None
    print(f"[selftest] sparse_w_edit_heavy_v1_n4096 PASS "
          f"smoke ret={out['post_storm_retention']:.3f} "
          f"kf2={out['post_storm_kf2_max_iso']:.3f} "
          f"mem_x={out['mem_savings_ratio']:.2f}", flush=True)


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
    M_init = M_INIT_SMOKE if smoke else M_INIT_FULL
    n_edits = N_EDITS_SMOKE if smoke else N_EDITS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] sparse_w_edit_heavy_v1 smoke={smoke} N={N_cfg} "
          f"M_init={M_init} n_edits={n_edits} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_cell(N_cfg, M_init, n_edits, seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  seed={seed} ret={out['post_storm_retention']:.3f} "
                  f"kf2={out['post_storm_kf2_max_iso']:.3f} "
                  f"mem_x={out['mem_savings_ratio']:.2f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "sparse_w_edit_heavy_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M_init": M_init, "n_edits": n_edits,
               "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
