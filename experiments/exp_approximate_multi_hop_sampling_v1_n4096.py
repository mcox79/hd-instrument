"""S10 APPROXIMATE MULTI-HOP SAMPLING v1 at N=4096 (E6.2).

Approximate multi-hop via random sampling. Latency-accuracy tradeoff
per path.

SAMPLING:
  Path B: sample subset of W columns at each retrieval, rates {10,25,50,75,100}%
  Path D: sample subset of candidate paths for likelihood, same rates
  Path E: top-k partial spectral decomposition (k = N * rate)

PRE-REGISTERED BANDS:
  HP = at least one path achieves >=3x latency reduction with <5%
       accuracy loss in 3+ seeds.
  HF = sampling degrades accuracy by >50% even at 75% rate.
  MB = otherwise.

PROT-018: _n4096.
Anchor: approximate_multi_hop_sampling_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_approximate_multi_hop_sampling_v1_n4096.md
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

from experiments._multi_hop_mechanisms import (  # noqa: E402
    build_shared, path_b_run, path_d_run, path_e_run,
)
from experiments._relation_graph import (  # noqa: E402
    sample_coherent_starts, sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s10", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


N = 4096
N_FULL  = N
N_SMOKE = 1024
M_PROD = 2048
M_SMOKE = 256
DEPTH = 5
DEPTH_SMOKE = 3
K_PATHS = 500
RATES = [0.10, 0.25, 0.50, 0.75, 1.00]
RATES_SMOKE = [0.25, 1.00]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS = 32

HP_SPEEDUP = 3.0
HP_ACC_LOSS = 0.05
HF_ACC_LOSS = 0.50
HF_RATE_THRESHOLD = 0.75


def get_output_dir(default_name: str = "approximate_multi_hop_sampling_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_seed(N_use: int, M: int, depth: int, K: int, rates: List[float],
                  seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    C = codebook.shape[0]
    starts = torch.tensor(list(relation.keys())[:N_PATHS],
                          dtype=torch.long, device=device)
    targets = []
    for k in starts.tolist():
        cur = int(k); ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None: ok = False; break
            cur = int(nxt)
        targets.append(cur if ok else -1)
    tgt = torch.tensor(targets, dtype=torch.long, device=device)
    valid = tgt >= 0

    pos = sample_coherent_starts(relation, depth, N_PATHS, seed)
    neg = sample_incoherent_paths(C, depth, N_PATHS, seed, relation=relation)

    out: List[Dict] = []
    for rate in rates:
        t0 = time.perf_counter_ns()
        pred_b = path_b_run(codebook, W, starts, depth, N_use, col_rate=rate)
        lat_b = time.perf_counter_ns() - t0
        acc_b = float((pred_b[valid] == tgt[valid]).float().mean().item()) if valid.any() else 0.0

        t1 = time.perf_counter_ns()
        correct_d = path_d_run(codebook, W, starts, relation, depth, K, seed,
                                N_use, path_sample_rate=rate)
        lat_d = time.perf_counter_ns() - t1
        acc_d = float(correct_d.mean().item())

        if pos and neg:
            t2 = time.perf_counter_ns()
            auc_e = path_e_run(codebook, W, pos, neg, N_use, spectrum_rate=rate)
            lat_e = time.perf_counter_ns() - t2
        else:
            auc_e = 0.5; lat_e = 0

        out.append({
            "rate": float(rate),
            "acc_b": round(acc_b, 5), "lat_b_ns": int(lat_b),
            "acc_d": round(acc_d, 5), "lat_d_ns": int(lat_d),
            "auc_e": round(auc_e, 5), "lat_e_ns": int(lat_e),
        })

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"seed": int(seed), "M": int(M), "depth": int(depth),
            "rate_results": out}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S10_INCONCLUSIVE", "no cells")

    # For each path, find best (rate < 1.0) achieving >=3x speedup vs rate=1.0
    # with <=5% acc loss across >=3 seeds.
    n_seeds = len(cells)

    def speedup_pass(path_key_acc, path_key_lat, is_auc=False):
        n_pass = 0
        for c in cells:
            results = c["rate_results"]
            full = next((r for r in results if r["rate"] == 1.0), None)
            if full is None: continue
            full_acc = full[path_key_acc]
            full_lat = full[path_key_lat]
            if full_lat <= 0: continue
            best_speedup_at_acc = False
            for r in results:
                if r["rate"] >= 1.0: continue
                sp = full_lat / max(1, r[path_key_lat])
                # For AUC, work in (auc-0.5)*2 space
                if is_auc:
                    full_eff = max(0.0, (full_acc - 0.5) * 2.0)
                    r_eff = max(0.0, (r[path_key_acc] - 0.5) * 2.0)
                else:
                    full_eff = full_acc
                    r_eff = r[path_key_acc]
                loss = (full_eff - r_eff) / max(1e-6, full_eff)
                if sp >= HP_SPEEDUP and loss <= HP_ACC_LOSS:
                    best_speedup_at_acc = True
                    break
            if best_speedup_at_acc:
                n_pass += 1
        return n_pass

    n_b = speedup_pass("acc_b", "lat_b_ns")
    n_d = speedup_pass("acc_d", "lat_d_ns")
    n_e = speedup_pass("auc_e", "lat_e_ns", is_auc=True)

    threshold = max(1, n_seeds * 3 // 5)
    hp_paths = []
    if n_b >= threshold: hp_paths.append("B")
    if n_d >= threshold: hp_paths.append("D")
    if n_e >= threshold: hp_paths.append("E")

    # HF: at rate >= HF_RATE_THRESHOLD, all paths degrade >50%
    n_hf_paths = 0
    for path_key_acc in ["acc_b", "acc_d", "auc_e"]:
        is_auc = path_key_acc == "auc_e"
        n_path_hf = 0
        for c in cells:
            results = c["rate_results"]
            full = next((r for r in results if r["rate"] == 1.0), None)
            if full is None: continue
            r_at = next((r for r in results if r["rate"] == HF_RATE_THRESHOLD), None)
            if r_at is None: continue
            if is_auc:
                full_eff = max(0.0, (full[path_key_acc] - 0.5) * 2.0)
                r_eff = max(0.0, (r_at[path_key_acc] - 0.5) * 2.0)
            else:
                full_eff = full[path_key_acc]
                r_eff = r_at[path_key_acc]
            loss = (full_eff - r_eff) / max(1e-6, full_eff)
            if loss > HF_ACC_LOSS:
                n_path_hf += 1
        if n_path_hf >= threshold:
            n_hf_paths += 1

    detail = (f"hp_paths={hp_paths} n_b={n_b} n_d={n_d} n_e={n_e} "
              f"n_hf_paths={n_hf_paths}/3")

    if hp_paths:
        return ("S10_HARD_PASS", "SAMPLING_SPEEDUP: " + detail)
    if n_hf_paths == 3:
        return ("S10_HARD_FAIL", "SAMPLING_DEGRADES: " + detail)
    return ("S10_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 64, 2, 20, [0.5, 1.0], 17, device)
    assert len(out["rate_results"]) == 2
    print(f"[selftest] approximate_multi_hop_sampling_v1_n4096 PASS", flush=True)


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
    M = M_SMOKE if smoke else M_PROD
    depth = DEPTH_SMOKE if smoke else DEPTH
    rates = RATES_SMOKE if smoke else RATES
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] approximate_multi_hop_sampling smoke={smoke} N={N_cfg} M={M} "
          f"depth={depth} rates={rates} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_seed(N_cfg, M, depth, K_PATHS, rates, seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  s={seed} done ({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  s={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "approximate_multi_hop_sampling_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "depth": depth, "K_paths": K_PATHS,
               "rates": rates, "seeds": seeds,
               "cells": cells, "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
