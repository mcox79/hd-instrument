"""SPARSE-W DELETION-SEQUENCES v1 at N=4096 (T4.1c).

CONTEXT (T4.1c):
  Test sparse-W interaction with deletion certificate chain. M_init=1000
  facts, sequentially delete 500 with certs. Verify cert generation,
  post-delete retrieval semantics (deleted not retrievable; non-deleted is),
  audit chain integrity, KF-2 post-deletion.

SCIENTIFIC QUESTION:
  At N=4096, over a 500-delete sequence on M_init=1000, do all certs
  generate, post-delete retrieval reflect deletions, audit chain remain
  valid, and KF-2 stay <= 0.05?

PRE-REGISTERED BANDS:
  HP = 100% cert generation AND post-delete retrieval semantics correct
       AND audit chain valid AND KF-2 <= 0.05 in >=3/5 seeds.
  HF = any cert fails OR retrieval semantics break OR audit chain corrupts
       in >=3/5 seeds.
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. M_init=1000, n_deletes=500.
  3. cert chain = list of {prev_hash, op, fact_id, key_id, val_id, op_id,
     this_hash}. verify_cert_chain walks SHA256.
  4. retrieval semantics: for deleted fid, kid retrieve != original vid;
     for non-deleted fid, kid retrieve == original vid.

OOM CHECK:
  M=1000, N=4096: keys+vals = 32 MiB. CB=805 MiB. ~840 MiB. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 30s. FULL: 5 seeds x 500 deletes x ~0.1s = ~250s. Budget 14400s.

N-suffix: _n4096 (PROT-018).
Anchor: sparse_w_deletion_sequences_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_sparse_w_deletion_sequences_v1_n4096.md
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
    kf2_spot_check,
    make_cert,
    verify_cert_chain,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_n10", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_INIT_FULL  = 1000
M_INIT_SMOKE = 32
N_DELETES_FULL  = 500
N_DELETES_SMOKE = 16
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_KF2 = 0.05
HP_SEEDS_MIN = 3
HF_SEEDS_MIN = 3


def get_output_dir(default_name: str = "sparse_w_deletion_sequences_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_cell(N_use: int, M_init: int, n_deletes: int, seed: int,
                  device: torch.device) -> Dict:
    cb = build_codebook(N_use, device)
    C = cb.shape[0]
    store = SparseStore(N=N_use, codebook=cb, device=device)

    gen = torch.Generator(device="cpu").manual_seed(seed + 11000)
    keys = torch.randperm(C, generator=gen)[:M_init].tolist()
    vals = torch.randint(0, C, (M_init,), generator=gen).tolist()
    fids: List[int] = []
    fact_kv: Dict[int, Tuple[int, int]] = {}
    for k, v in zip(keys, vals):
        fid = store.store_fact(int(k), int(v))
        fids.append(fid)
        fact_kv[fid] = (int(k), int(v))

    # Choose deletion order
    del_order_idx = torch.randperm(M_init, generator=gen)[:n_deletes].tolist()
    delete_fids = [fids[i] for i in del_order_idx]

    chain: List[Dict[str, str]] = []
    prev_hash = "GENESIS"
    cert_count_success = 0
    op_id = 0
    for fid in delete_fids:
        kid, vid = fact_kv[fid]
        ok = store.delete_fact(fid)
        if not ok:
            continue
        link = make_cert(prev_hash, "delete", fact_id=fid,
                          key_id=kid, val_id=vid, op_id=op_id)
        chain.append(link)
        prev_hash = link["this_hash"]
        cert_count_success += 1
        op_id += 1

    cert_rate = cert_count_success / max(1, len(delete_fids))

    # Retrieval semantics: deleted not retrievable; non-deleted retrievable
    n_del_check = min(50, len(delete_fids))
    deleted_correctly_gone = 0
    for fid in delete_fids[:n_del_check]:
        kid, vid_orig = fact_kv[fid]
        pred, _ = store.retrieve(kid)
        if pred != vid_orig:
            deleted_correctly_gone += 1
    del_gone_rate = deleted_correctly_gone / max(1, n_del_check)

    surviving = [fid for fid in fids if fid not in set(delete_fids)]
    n_surv_check = min(50, len(surviving))
    surv_correctly_present = 0
    for fid in surviving[:n_surv_check]:
        kid, vid = fact_kv[fid]
        pred, _ = store.retrieve(kid)
        if pred == vid:
            surv_correctly_present += 1
    surv_present_rate = surv_correctly_present / max(1, n_surv_check)

    audit_valid = verify_cert_chain(chain)
    kf2 = kf2_spot_check(store, n_edits=8,
                          n_probe=min(50, len(surviving)), seed=seed + 99)

    del store, cb
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"M_init": int(M_init), "n_deletes": int(n_deletes),
            "seed": int(seed), "N": int(N_use),
            "cert_count_success": int(cert_count_success),
            "cert_rate": round(cert_rate, 5),
            "audit_chain_valid": bool(audit_valid),
            "deleted_gone_rate": round(del_gone_rate, 5),
            "surviving_present_rate": round(surv_present_rate, 5),
            "post_delete_kf2": round(kf2, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("SW_DS_INCONCLUSIVE", "No cells.")
    hp_seeds = 0
    hf_seeds = 0
    for c in cells:
        hp_ok = (c["cert_rate"] >= 0.999
                  and c["audit_chain_valid"]
                  and c["deleted_gone_rate"] >= 0.95
                  and c["surviving_present_rate"] >= 0.95
                  and c["post_delete_kf2"] <= HP_KF2)
        hf_ok = (c["cert_rate"] < 1.0
                  or not c["audit_chain_valid"]
                  or c["deleted_gone_rate"] < 0.80
                  or c["surviving_present_rate"] < 0.80)
        if hp_ok:
            hp_seeds += 1
        if hf_ok:
            hf_seeds += 1
    detail = f"hp={hp_seeds}/{len(cells)} hf={hf_seeds}/{len(cells)}"
    if hf_seeds >= HF_SEEDS_MIN:
        return ("SW_DS_HARD_FAIL", "DELETION_INTEGRITY_BROKE: " + detail)
    if hp_seeds >= HP_SEEDS_MIN:
        return ("SW_DS_HARD_PASS", "DELETION_INTEGRITY_HOLDS: " + detail)
    return ("SW_DS_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096

    fake_hp = [{"M_init": M_INIT_FULL, "n_deletes": N_DELETES_FULL, "seed": s,
                 "N": N_FULL, "cert_count_success": N_DELETES_FULL,
                 "cert_rate": 1.0, "audit_chain_valid": True,
                 "deleted_gone_rate": 1.0, "surviving_present_rate": 0.98,
                 "post_delete_kf2": 0.03} for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = [{"M_init": M_INIT_FULL, "n_deletes": N_DELETES_FULL, "seed": s,
                 "N": N_FULL, "cert_count_success": 0,
                 "cert_rate": 0.0, "audit_chain_valid": False,
                 "deleted_gone_rate": 0.3, "surviving_present_rate": 0.5,
                 "post_delete_kf2": 0.5} for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_INIT_SMOKE, N_DELETES_SMOKE, 17, device)
    assert out["cert_rate"] is not None
    assert out["audit_chain_valid"] is True
    print(f"[selftest] sparse_w_deletion_sequences_v1_n4096 PASS "
          f"smoke cert_rate={out['cert_rate']:.3f} "
          f"audit={out['audit_chain_valid']} "
          f"gone={out['deleted_gone_rate']:.3f} "
          f"surv={out['surviving_present_rate']:.3f}", flush=True)


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
    n_del = N_DELETES_SMOKE if smoke else N_DELETES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] sparse_w_deletion_sequences_v1 smoke={smoke} N={N_cfg} "
          f"M_init={M_init} n_del={n_del} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_cell(N_cfg, M_init, n_del, seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  seed={seed} cert={out['cert_rate']:.3f} "
                  f"audit={out['audit_chain_valid']} "
                  f"gone={out['deleted_gone_rate']:.3f} "
                  f"surv={out['surviving_present_rate']:.3f} "
                  f"kf2={out['post_delete_kf2']:.3f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "sparse_w_deletion_sequences_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M_init": M_init, "n_deletes": n_del,
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
