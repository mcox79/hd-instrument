"""SPARSE-W MIXED-CRUD v1 at N=4096 (T4.1b).

CONTEXT (T4.1b):
  Sustained 10000-op CRUD workload (40% store / 30% query / 20% edit /
  10% delete). Test whether sparse-W maintains retention AND killer
  features throughout the run.

SCIENTIFIC QUESTION:
  At N=4096, after 10000 mixed CRUD ops, does sparse-W maintain retention
  >= 0.90 AND KF-2 <= 0.05 at every 2500-op checkpoint?

PRE-REGISTERED BANDS:
  HP = retention >= 0.90 AND KF-2 <= 0.05 at all 4 checkpoints in >=3/5 seeds.
  HF = retention drops <= 0.70 at any checkpoint OR KF-2 isolation breaks
       (>0.10) in >=3/5 seeds.
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. M_init=128, n_total_ops=10000.
  3. op_mix = (0.4, 0.3, 0.2, 0.1).
  4. checkpoints at op counts {2500, 5000, 7500, 10000}.

OOM CHECK:
  Live M is bounded by store - delete ops. Expected ceiling ~ 4000 facts.
  4000 * N * 4 = 64 MiB keys, 64 MiB values. Trivial.

TIMEOUT ESTIMATE:
  Smoke ~ 30s (200 ops). FULL: 5 seeds x 10000 ops x ~0.02s/op = 1000s.
  Budget 21600s.

N-suffix: _n4096 (PROT-018).
Anchor: sparse_w_mixed_crud_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_sparse_w_mixed_crud_v1_n4096.md
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
    gen_mixed_crud,
    kf2_spot_check,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_n9", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_INIT_FULL  = 128
M_INIT_SMOKE = 16
N_OPS_FULL  = 10000
N_OPS_SMOKE = 200
OP_MIX = (0.4, 0.3, 0.2, 0.1)
N_CHECKPOINTS = 4
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_RET = 0.90
HP_KF2 = 0.05
HF_RET = 0.70
HF_KF2 = 0.10
HP_SEEDS_MIN = 3
HF_SEEDS_MIN = 3


def get_output_dir(default_name: str = "sparse_w_mixed_crud_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_cell(N_use: int, M_init: int, n_ops: int, seed: int,
                  device: torch.device) -> Dict:
    cb = build_codebook(N_use, device)
    C = cb.shape[0]
    store = SparseStore(N=N_use, codebook=cb, device=device)

    initial, ops = gen_mixed_crud(n_initial_facts=M_init,
                                    n_total_ops=n_ops,
                                    op_mix=OP_MIX,
                                    seed=seed, n_codebook=C)
    for k, v in initial:
        store.store_fact(k, v)

    n_per_ckpt = max(1, n_ops // N_CHECKPOINTS)
    checkpoints: List[Dict] = []
    n_queries = 0
    n_query_correct = 0

    for i, (op_name, idx_a, idx_b) in enumerate(ops):
        living = list(store.facts.keys())
        if op_name == "store":
            store.store_fact(idx_a, idx_b)
        elif op_name == "query":
            if living:
                fid = living[i % len(living)]
                kid, vid = store.facts[fid]
                pred, _ = store.retrieve(kid)
                n_queries += 1
                if pred == vid:
                    n_query_correct += 1
        elif op_name == "edit":
            if living:
                tgt = living[i % len(living)]
                store.edit_fact(tgt, idx_b)
        elif op_name == "delete":
            if living:
                tgt = living[i % len(living)]
                store.delete_fact(tgt)

        if (i + 1) % n_per_ckpt == 0 and len(checkpoints) < N_CHECKPOINTS:
            # Spot retention on living facts
            living2 = list(store.facts.keys())
            if living2:
                sample_n = min(50, len(living2))
                c2 = 0
                for fid in living2[:sample_n]:
                    kid, vid = store.facts[fid]
                    pred, _ = store.retrieve(kid)
                    if pred == vid:
                        c2 += 1
                ckpt_ret = c2 / sample_n
            else:
                ckpt_ret = 0.0
            ckpt_kf2 = kf2_spot_check(store, n_edits=4,
                                        n_probe=min(20, len(living2)),
                                        seed=seed + i)
            checkpoints.append({
                "op_count": int(i + 1),
                "live_M": len(living2),
                "retention": round(ckpt_ret, 5),
                "kf2_max_iso": round(ckpt_kf2, 5),
            })

    final_query_ret = (n_query_correct / max(1, n_queries))
    del store, cb
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"M_init": int(M_init), "n_ops": int(n_ops), "seed": int(seed),
            "N": int(N_use),
            "n_queries_seen": int(n_queries),
            "running_query_retention": round(final_query_ret, 5),
            "checkpoints": checkpoints}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("SW_CRUD_INCONCLUSIVE", "No cells.")
    hp_seeds = 0
    hf_seeds = 0
    for c in cells:
        cps = c["checkpoints"]
        if not cps:
            continue
        hp_ok = all(cp["retention"] >= HP_RET and cp["kf2_max_iso"] <= HP_KF2
                     for cp in cps)
        hf_ok = any(cp["retention"] <= HF_RET or cp["kf2_max_iso"] > HF_KF2
                     for cp in cps)
        if hp_ok:
            hp_seeds += 1
        if hf_ok:
            hf_seeds += 1
    detail = (f"hp={hp_seeds}/{len(cells)} hf={hf_seeds}/{len(cells)} "
              f"n_cells={len(cells)}")
    if hf_seeds >= HF_SEEDS_MIN:
        return ("SW_CRUD_HARD_FAIL", "SPARSE_BROKE_IN_WORKLOAD: " + detail)
    if hp_seeds >= HP_SEEDS_MIN:
        return ("SW_CRUD_HARD_PASS", "SPARSE_HOLDS_CRUD: " + detail)
    return ("SW_CRUD_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    assert abs(sum(OP_MIX) - 1.0) < 1e-6

    fake_hp = [{"M_init": M_INIT_FULL, "n_ops": N_OPS_FULL, "seed": s,
                 "N": N_FULL, "n_queries_seen": 3000,
                 "running_query_retention": 0.95,
                 "checkpoints": [{"op_count": 2500, "live_M": 200,
                                    "retention": 0.95, "kf2_max_iso": 0.02}
                                  for _ in range(N_CHECKPOINTS)]}
                for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = [{"M_init": M_INIT_FULL, "n_ops": N_OPS_FULL, "seed": s,
                 "N": N_FULL, "n_queries_seen": 3000,
                 "running_query_retention": 0.60,
                 "checkpoints": [{"op_count": 2500, "live_M": 200,
                                    "retention": 0.60, "kf2_max_iso": 0.20}
                                  for _ in range(N_CHECKPOINTS)]}
                for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_INIT_SMOKE, N_OPS_SMOKE, 17, device)
    assert out["checkpoints"] is not None
    assert len(out["checkpoints"]) > 0
    print(f"[selftest] sparse_w_mixed_crud_v1_n4096 PASS "
          f"smoke ckpt0_ret={out['checkpoints'][0]['retention']:.3f} "
          f"live_M_last={out['checkpoints'][-1]['live_M']}", flush=True)


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
    n_ops = N_OPS_SMOKE if smoke else N_OPS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] sparse_w_mixed_crud_v1 smoke={smoke} N={N_cfg} "
          f"M_init={M_init} n_ops={n_ops} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_cell(N_cfg, M_init, n_ops, seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            last_cp = out["checkpoints"][-1] if out["checkpoints"] else {}
            print(f"  seed={seed} run_qret={out['running_query_retention']:.3f} "
                  f"last_cp_ret={last_cp.get('retention','-')} "
                  f"last_cp_kf2={last_cp.get('kf2_max_iso','-')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "sparse_w_mixed_crud_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M_init": M_init, "n_ops": n_ops,
               "op_mix": OP_MIX, "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
