"""C2 MULTI HOP CACHING BASELINE v1 at N=4096.

CONTEXT (v290 cap_map follow-on):
  Baseline implementation of simple LRU cache for Path D multi-hop results.
  Measures cache hit rate + latency reduction across Zipfian skew levels.

SCIENTIFIC QUESTION:
  At N=4096, M=2048, depth=5, K_paths=100, Zipfian alpha in {0.5, 1.0, 1.5}:
  what is the cache hit rate and latency reduction? Does the cache preserve
  audit chain integrity (cached result == fresh recomputation)?

PRE-REGISTERED BANDS:
  HP = hit rate >=0.30 at alpha=1.0 AND hot query latency <10ms AND
       audit chain integrity 100% (all cache hits match fresh recompute).
  HF = hit rate <0.10 OR audit chain corrupts (any cache hit mismatches).
  MB = otherwise.

CACHE: simple Python OrderedDict-based LRU, capacity = 256.

PROT-018: _n4096 binds N = 4096.
PROT-021: per-cell-seed checkpointing.

Anchor: multi_hop_caching_baseline_v1_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-30_multi_hop_caching_baseline_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
import math
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_c2", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_PROD = 2048
M_SMOKE = 256
DEPTH = 5
DEPTH_SMOKE = 3
K_PATHS = 100
K_PATHS_SMOKE = 10
N_QUERIES = 1000
N_QUERIES_SMOKE = 30
ALPHA_SWEEP_FULL = [0.5, 1.0, 1.5]
ALPHA_SWEEP_SMOKE = [1.0]
N_STARTS = 16
N_STARTS_SMOKE = 4
BETA_D = 4.0
CACHE_CAPACITY = 256
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_MIN_HIT_RATE_AT_A1 = 0.30
HP_MAX_HOT_LATENCY_S = 0.010  # 10ms
HF_MAX_HIT_RATE = 0.10


def get_output_dir(default_name: str = "multi_hop_caching_baseline_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _zipf_samples(n_total: int, alpha: float, n_unique: int, seed: int) -> List[int]:
    """Sample n_total integers in [0, n_unique) from Zipf(alpha)."""
    g = torch.Generator(device='cpu').manual_seed(seed + 50)
    # CDF of Zipf
    ranks = torch.arange(1, n_unique + 1, dtype=torch.float64)
    weights = ranks ** (-alpha)
    weights = weights / weights.sum()
    cum = torch.cumsum(weights, dim=0)
    u = torch.rand(n_total, generator=g, dtype=torch.float64)
    # Bucket each u into the cumulative distribution
    idx = torch.searchsorted(cum, u)
    idx = torch.clamp(idx, max=n_unique - 1)
    return idx.tolist()


def measure_seed(N_use: int, M: int, depth: int, K_paths: int,
                   alpha: float, n_q: int, n_starts: int, seed: int,
                   device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)

    starts_list = list(relation.keys())[:n_starts]
    if not starts_list:
        return {"seed": int(seed), "alpha": float(alpha), "ok": False,
                "error": "no starts"}

    # Generate Zipfian query stream (each query = one start_idx in starts_list)
    n_unique = len(starts_list)
    query_stream = _zipf_samples(n_q, alpha, n_unique, seed)

    # Cache: key = (start_idx, depth, K_paths), value = (correct_tensor, lat_ns)
    cache: OrderedDict = OrderedDict()
    n_hits = 0
    audit_violations = 0
    hot_latencies = []
    cold_latencies = []
    for q_idx in query_stream:
        start_value = starts_list[q_idx]
        cache_key = (start_value, depth, K_paths)
        # Always do a fresh recompute (small) to check audit chain
        starts_one = torch.tensor([start_value], dtype=torch.long, device=device)
        t0 = time.perf_counter()
        fresh = path_d_run(codebook, W, starts_one, relation, depth, K_paths,
                            seed, N_use, beta=BETA_D)
        fresh_t = time.perf_counter() - t0
        if cache_key in cache:
            # Hit: serve from cache, but ALSO check vs fresh for audit
            cached_val = cache.pop(cache_key)
            cache[cache_key] = cached_val  # move to end (LRU)
            cached_correct = cached_val[0]
            if not torch.equal(cached_correct, fresh):
                audit_violations += 1
            n_hits += 1
            hot_latencies.append(cached_val[1])
        else:
            # Miss
            cache[cache_key] = (fresh.clone(), fresh_t)
            cold_latencies.append(fresh_t)
            if len(cache) > CACHE_CAPACITY:
                cache.popitem(last=False)

    n_total = len(query_stream)
    hit_rate = n_hits / max(1, n_total)
    mean_hot = sum(hot_latencies) / max(1, len(hot_latencies)) if hot_latencies else 0.0
    mean_cold = sum(cold_latencies) / max(1, len(cold_latencies)) if cold_latencies else 0.0
    audit_integrity = 1.0 - audit_violations / max(1, n_hits)

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"seed": int(seed), "alpha": float(alpha),
            "M": int(M), "depth": int(depth), "K_paths": int(K_paths),
            "ok": True,
            "n_queries": int(n_total),
            "n_hits": int(n_hits),
            "hit_rate": round(hit_rate, 5),
            "mean_hot_latency_s": round(mean_hot, 6),
            "mean_cold_latency_s": round(mean_cold, 6),
            "audit_violations": int(audit_violations),
            "audit_integrity": round(audit_integrity, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("C2_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("C2_INCONCLUSIVE", f"all {len(cells)} cells failed")

    # Per-alpha aggregation
    by_alpha: Dict[float, Dict[str, List[float]]] = {}
    for c in ok:
        a = c["alpha"]
        by_alpha.setdefault(a, {"hit": [], "hot": [], "audit": []})
        by_alpha[a]["hit"].append(c["hit_rate"])
        by_alpha[a]["hot"].append(c["mean_hot_latency_s"])
        by_alpha[a]["audit"].append(c["audit_integrity"])

    summaries = {}
    for a, m in by_alpha.items():
        summaries[a] = {
            "mean_hit": sum(m["hit"]) / len(m["hit"]),
            "mean_hot": sum(m["hot"]) / max(1, len(m["hot"])),
            "min_audit": min(m["audit"]),
        }

    detail = " | ".join(
        f"a={a}: hit={summaries[a]['mean_hit']:.3f} hot={summaries[a]['mean_hot']*1000:.2f}ms "
        f"audit={summaries[a]['min_audit']:.3f}"
        for a in sorted(summaries.keys()))

    # Audit must be 100% always; HF if any audit < 1.0
    any_audit_break = any(s["min_audit"] < 1.0 for s in summaries.values())
    if any_audit_break:
        return ("C2_HARD_FAIL", "AUDIT_CHAIN_VIOLATION: " + detail)

    # alpha=1.0 must hit HP_MIN_HIT_RATE_AT_A1
    s_a1 = summaries.get(1.0)
    if s_a1 is None:
        return ("C2_INCONCLUSIVE", "no alpha=1.0 cell. " + detail)
    if s_a1["mean_hit"] < HF_MAX_HIT_RATE:
        return ("C2_HARD_FAIL",
                f"HIT_RATE_TOO_LOW at alpha=1.0: {s_a1['mean_hit']:.3f}. " + detail)
    if (s_a1["mean_hit"] >= HP_MIN_HIT_RATE_AT_A1
        and s_a1["mean_hot"] <= HP_MAX_HOT_LATENCY_S):
        return ("C2_HARD_PASS",
                f"CACHE_VIABLE hit={s_a1['mean_hit']:.3f} hot={s_a1['mean_hot']*1000:.2f}ms. " + detail)
    return ("C2_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(SEEDS_FULL) == 5

    # Verdict gate HP
    fake_hp = [{"seed": s, "alpha": 1.0, "ok": True, "M": M_PROD,
                "depth": DEPTH, "K_paths": K_PATHS, "n_queries": 1000,
                "n_hits": 400, "hit_rate": 0.40,
                "mean_hot_latency_s": 0.005, "mean_cold_latency_s": 0.05,
                "audit_violations": 0, "audit_integrity": 1.0}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF (audit broken)
    fake_hf = [{"seed": s, "alpha": 1.0, "ok": True, "M": M_PROD,
                "depth": DEPTH, "K_paths": K_PATHS, "n_queries": 1000,
                "n_hits": 400, "hit_rate": 0.40,
                "mean_hot_latency_s": 0.005, "mean_cold_latency_s": 0.05,
                "audit_violations": 10, "audit_integrity": 0.95}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Verdict gate MB (audit ok but hit rate borderline + slow hot)
    fake_mb = [{"seed": s, "alpha": 1.0, "ok": True, "M": M_PROD,
                "depth": DEPTH, "K_paths": K_PATHS, "n_queries": 1000,
                "n_hits": 350, "hit_rate": 0.35,
                "mean_hot_latency_s": 0.050, "mean_cold_latency_s": 0.10,
                "audit_violations": 0, "audit_integrity": 1.0}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    # Smoke
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 128, DEPTH_SMOKE, K_PATHS_SMOKE,
                        1.0, N_QUERIES_SMOKE, N_STARTS_SMOKE, 17, device)
    assert out.get("ok"), f"selftest measure_seed failed: {out.get('error')}"
    assert "hit_rate" in out
    assert "audit_integrity" in out
    print(f"[selftest] multi_hop_caching_baseline_v1_n4096 PASS "
          f"hit={out['hit_rate']:.3f} audit={out['audit_integrity']:.3f}",
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
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M = M_SMOKE if smoke else M_PROD
    depth = DEPTH_SMOKE if smoke else DEPTH
    K_paths = K_PATHS_SMOKE if smoke else K_PATHS
    n_q = N_QUERIES_SMOKE if smoke else N_QUERIES
    n_starts = N_STARTS_SMOKE if smoke else N_STARTS
    alpha_sweep = ALPHA_SWEEP_SMOKE if smoke else ALPHA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] multi_hop_caching_baseline_v1_n4096 smoke={smoke} N={N_cfg} "
          f"M={M} depth={depth} K_paths={K_paths} n_q={n_q} alphas={alpha_sweep} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for alpha in alpha_sweep:
        for seed in seeds:
            ck = f"a{alpha}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                cell = measure_seed(N_cfg, M, depth, K_paths, alpha, n_q,
                                      n_starts, seed, device)
                write_partial_key(out_dir, ck, cell)
                cells.append(cell)
                print(f"  alpha={alpha} seed={seed} ok={cell.get('ok')} "
                      f"hit={cell.get('hit_rate', 'n/a')} "
                      f"audit={cell.get('audit_integrity', 'n/a')} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
                print(f"  alpha={alpha} seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "multi_hop_caching_baseline_v1_n4096",
               "N": N_cfg, "smoke": smoke, "M": M, "depth": depth,
               "K_paths": K_paths, "n_q": n_q, "alphas": alpha_sweep,
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
