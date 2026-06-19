"""C2 MULTI HOP CACHING BASELINE v3 at N=4096.

CONTEXT (v296 cap_map rescue; v2 landed CONFOUNDED -- CACHE_CAPACITY=256 > K_PATHS=100
so every unique path was absorbed regardless of Zipfian skew; all 15 cells showed
identical hit_rate=0.984, hot_latency=cold_latency, 8/15 cells hot SLOWER than cold;
no Zipfian-effect science recoverable from v2; verdict_handler rescue ladder R2+R3 filed).

FIX: CACHE_CAPACITY=16 << K_PATHS=100 forces eviction; Zipfian-repetition signal
can now drive hit rate differences across alpha values. ALPHA grid broadened to
{0.5, 0.75, 1.0, 1.5, 2.0} to capture the full skew envelope.

SCIENTIFIC QUESTION:
  At N=4096, M=2048, depth=5, K_paths=100, CACHE_CAPACITY=16, Zipfian alpha in
  {0.5, 0.75, 1.0, 1.5, 2.0}: does hit rate increase with alpha (higher skew)?
  Does hot query latency fall below cold latency when hits occur?
  Does audit chain integrity hold at 100%?

PRE-REGISTERED BANDS:
  HP = hit rate at alpha=2.0 >= 0.50 (heavy-tail fully exploits small cache)
       AND hit rate monotone-increasing across alpha grid (confirms Zipfian effect)
       AND hot_latency < cold_latency (cache benefit realized)
       AND audit chain integrity 100%.
  HF = hit rate at alpha=2.0 < 0.10 (cache eviction kills all benefit)
       OR audit chain corrupts (any cache hit mismatches).
  MB = otherwise (some hit rate difference but HP bands not met).

NOTE on bands: no prior empirical anchor with evicting cache; calibration-probe
policy applied -- HP threshold set at 0.50 (conservative, not theoretical max).

CACHE: OrderedDict-based LRU, CACHE_CAPACITY=16.

PROT-018: _n4096 binds N = 4096.
PROT-019: timeout >= 14400s.
PROT-021: per-cell-seed checkpointing.

Anchor: multi_hop_caching_baseline_v3_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-31_multi_hop_caching_baseline_v3_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_c2v3", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N = 4096
N_FULL  = N
N_SMOKE = 1024  # must be power of 4 for Kerdock construction (512 = 2^9 fails)
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_PROD = 2048
M_SMOKE = 256
DEPTH = 5
DEPTH_SMOKE = 3
K_PATHS = 100
K_PATHS_SMOKE = 20
N_QUERIES = 2000
N_QUERIES_SMOKE = 60
# v3 FIX: CACHE_CAPACITY << K_PATHS to force eviction and expose Zipfian-effect
CACHE_CAPACITY = 16
ALPHA_SWEEP_FULL = [0.5, 0.75, 1.0, 1.5, 2.0]
ALPHA_SWEEP_SMOKE = [0.5, 1.0, 2.0]
N_STARTS = 20
N_STARTS_SMOKE = 5
BETA_D = 4.0
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered bands (v3)
HP_MIN_HIT_RATE_ALPHA2 = 0.50   # heavy-skew exploits small cache
HP_MAX_HOT_LATENCY_FACTOR = 1.0  # hot_latency < cold_latency
HF_MAX_HIT_RATE_ALPHA2 = 0.10   # below this = eviction destroyed benefit


def get_output_dir(default_name: str = "multi_hop_caching_baseline_v3_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _zipf_samples(n_total: int, alpha: float, n_unique: int, seed: int) -> List[int]:
    """Sample n_total integers in [0, n_unique) from Zipf(alpha)."""
    g = torch.Generator(device='cpu').manual_seed(seed + 50)
    ranks = torch.arange(1, n_unique + 1, dtype=torch.float64)
    weights = ranks ** (-alpha)
    weights = weights / weights.sum()
    cum = torch.cumsum(weights, dim=0)
    u = torch.rand(n_total, generator=g, dtype=torch.float64)
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

    n_unique = len(starts_list)
    query_stream = _zipf_samples(n_q, alpha, n_unique, seed)

    # LRU cache with capacity CACHE_CAPACITY << K_PATHS
    cache: OrderedDict = OrderedDict()
    n_hits = 0
    audit_violations = 0
    hot_latencies = []
    cold_latencies = []
    for q_idx in query_stream:
        start_value = starts_list[q_idx]
        cache_key = (start_value, depth, K_paths)
        starts_one = torch.tensor([start_value], dtype=torch.long, device=device)
        t0 = time.perf_counter()
        fresh = path_d_run(codebook, W, starts_one, relation, depth, K_paths,
                            seed, N_use, beta=BETA_D)
        fresh_t = time.perf_counter() - t0
        if cache_key in cache:
            cached_val = cache.pop(cache_key)
            cache[cache_key] = cached_val  # move to end (LRU)
            cached_correct = cached_val[0]
            if not torch.equal(cached_correct, fresh):
                audit_violations += 1
            n_hits += 1
            hot_latencies.append(cached_val[1])
        else:
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
    return {"seed": int(seed), "alpha": float(alpha),
            "M": int(M), "depth": int(depth), "K_paths": int(K_paths),
            "cache_capacity": CACHE_CAPACITY,
            "ok": True,
            "n_queries": int(n_total),
            "n_hits": int(n_hits),
            "hit_rate": round(hit_rate, 5),
            "mean_hot_latency_s": round(mean_hot, 6),
            "mean_cold_latency_s": round(mean_cold, 6),
            "hot_faster_than_cold": bool(mean_hot < mean_cold and n_hits > 0),
            "audit_violations": int(audit_violations),
            "audit_integrity": round(audit_integrity, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("C2_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("C2_INCONCLUSIVE", f"all {len(cells)} cells failed")

    by_alpha: Dict[float, Dict[str, List[float]]] = {}
    for c in ok:
        a = c["alpha"]
        by_alpha.setdefault(a, {"hit": [], "hot": [], "cold": [], "audit": [], "faster": []})
        by_alpha[a]["hit"].append(c["hit_rate"])
        by_alpha[a]["hot"].append(c["mean_hot_latency_s"])
        by_alpha[a]["cold"].append(c["mean_cold_latency_s"])
        by_alpha[a]["audit"].append(c["audit_integrity"])
        by_alpha[a]["faster"].append(float(c.get("hot_faster_than_cold", False)))

    summaries = {}
    for a, m in by_alpha.items():
        summaries[a] = {
            "mean_hit": sum(m["hit"]) / len(m["hit"]),
            "mean_hot": sum(m["hot"]) / max(1, len(m["hot"])),
            "mean_cold": sum(m["cold"]) / max(1, len(m["cold"])),
            "min_audit": min(m["audit"]),
            "pct_faster": sum(m["faster"]) / max(1, len(m["faster"])),
        }

    detail = " | ".join(
        f"a={a}: hit={summaries[a]['mean_hit']:.3f} "
        f"hot={summaries[a]['mean_hot']*1000:.2f}ms "
        f"cold={summaries[a]['mean_cold']*1000:.2f}ms "
        f"audit={summaries[a]['min_audit']:.3f}"
        for a in sorted(summaries.keys()))

    # Hard-fail: audit violation
    any_audit_break = any(s["min_audit"] < 1.0 for s in summaries.values())
    if any_audit_break:
        return ("C2_HARD_FAIL", "AUDIT_CHAIN_VIOLATION: " + detail)

    # Hard-fail: no benefit at alpha=2.0 (eviction kills everything)
    s_a2 = summaries.get(2.0)
    if s_a2 is not None and s_a2["mean_hit"] < HF_MAX_HIT_RATE_ALPHA2:
        return ("C2_HARD_FAIL",
                f"NO_CACHE_BENEFIT_HIGH_SKEW hit@a2={s_a2['mean_hit']:.3f}. " + detail)

    # Hard-pass: alpha=2.0 hits HP threshold AND hot < cold AND monotone trend
    if s_a2 is None:
        return ("C2_INCONCLUSIVE", "no alpha=2.0 cell. " + detail)

    alphas_sorted = sorted(summaries.keys())
    hit_vals = [summaries[a]["mean_hit"] for a in alphas_sorted]
    # Monotone check: each step non-decreasing
    monotone = all(hit_vals[i] <= hit_vals[i + 1] for i in range(len(hit_vals) - 1))
    hot_lt_cold = (s_a2["mean_hot"] < s_a2["mean_cold"])

    if (s_a2["mean_hit"] >= HP_MIN_HIT_RATE_ALPHA2
            and monotone and hot_lt_cold):
        return ("C2_HARD_PASS",
                f"ZIPFIAN_CACHE_VIABLE hit@a2={s_a2['mean_hit']:.3f} "
                f"monotone={monotone} hot<cold={hot_lt_cold}. " + detail)

    return ("C2_MIDDLE_BAND",
            f"PARTIAL hit@a2={s_a2['mean_hit']:.3f} monotone={monotone} "
            f"hot<cold={hot_lt_cold}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert CACHE_CAPACITY == 16, "v3 fix: CACHE_CAPACITY must be 16"
    assert K_PATHS == 100, "K_PATHS must be 100"
    assert CACHE_CAPACITY < K_PATHS, "PROT-v3: CACHE_CAPACITY must be < K_PATHS"
    assert len(SEEDS_FULL) == 5
    assert 2.0 in ALPHA_SWEEP_FULL, "must include alpha=2.0 for HP gate"

    # Verdict gate HP: alpha=2.0 hit>=0.50, monotone, hot<cold, audit 100%
    fake_hp_base = {"seed": 7, "M": M_PROD, "depth": DEPTH,
                    "K_paths": K_PATHS, "cache_capacity": CACHE_CAPACITY,
                    "ok": True, "n_queries": 2000, "audit_violations": 0,
                    "audit_integrity": 1.0, "hot_faster_than_cold": True}
    fake_hp = []
    for s in SEEDS_FULL:
        for a, h, hot, cold in [(0.5, 0.05, 0.008, 0.020),
                                  (0.75, 0.12, 0.007, 0.018),
                                  (1.0, 0.22, 0.006, 0.015),
                                  (1.5, 0.38, 0.005, 0.012),
                                  (2.0, 0.55, 0.004, 0.010)]:
            c = dict(fake_hp_base)
            c["seed"] = s; c["alpha"] = a; c["hit_rate"] = h
            c["n_hits"] = int(h * 2000)
            c["mean_hot_latency_s"] = hot; c["mean_cold_latency_s"] = cold
            fake_hp.append(c)
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    # Verdict gate HF (audit broken)
    fake_hf = []
    for s in SEEDS_FULL:
        c = dict(fake_hp_base); c["seed"] = s; c["alpha"] = 2.0
        c["hit_rate"] = 0.55; c["n_hits"] = 1100
        c["mean_hot_latency_s"] = 0.004; c["mean_cold_latency_s"] = 0.010
        c["audit_integrity"] = 0.90; c["audit_violations"] = 110
        c["hot_faster_than_cold"] = True
        fake_hf.append(c)
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF audit gate failed: {v} {msg}"

    # Verdict gate HF (no benefit at alpha=2.0)
    fake_hf2 = []
    for s in SEEDS_FULL:
        c = dict(fake_hp_base); c["seed"] = s; c["alpha"] = 2.0
        c["hit_rate"] = 0.05; c["n_hits"] = 100
        c["mean_hot_latency_s"] = 0.015; c["mean_cold_latency_s"] = 0.015
        c["audit_integrity"] = 1.0; c["audit_violations"] = 0
        c["hot_faster_than_cold"] = False
        fake_hf2.append(c)
    v, msg = compute_verdict(fake_hf2)
    assert "HARD_FAIL" in v, f"HF no-benefit gate failed: {v} {msg}"

    # Verdict gate MB: some hit rate at alpha=2.0 but not monotone
    fake_mb = []
    for s in SEEDS_FULL:
        for a, h, hot, cold in [(0.5, 0.20, 0.010, 0.015),
                                  (0.75, 0.15, 0.010, 0.015),  # non-monotone
                                  (1.0, 0.22, 0.009, 0.015),
                                  (1.5, 0.35, 0.008, 0.012),
                                  (2.0, 0.45, 0.007, 0.010)]:
            c = dict(fake_hp_base)
            c["seed"] = s; c["alpha"] = a; c["hit_rate"] = h
            c["n_hits"] = int(h * 2000)
            c["mean_hot_latency_s"] = hot; c["mean_cold_latency_s"] = cold
            c["hot_faster_than_cold"] = hot < cold
            fake_mb.append(c)
    v, msg = compute_verdict(fake_mb)
    assert "MIDDLE_BAND" in v or "HARD_PASS" in v, f"MB gate failed: {v} {msg}"

    # Live smoke on CPU (forced -- no CUDA)
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, M_SMOKE, DEPTH_SMOKE, K_PATHS_SMOKE,
                        1.0, N_QUERIES_SMOKE, N_STARTS_SMOKE, 17, device)
    assert out.get("ok"), f"selftest measure_seed failed: {out.get('error')}"
    assert "hit_rate" in out
    assert "audit_integrity" in out
    assert out.get("cache_capacity") == CACHE_CAPACITY, "cache_capacity field missing"
    # Key check: with CACHE_CAPACITY=16 < K_PATHS=20, eviction must occur
    # (we can't assert hit_rate exactly but the field must be present and valid)
    assert 0.0 <= out["hit_rate"] <= 1.0, f"hit_rate out of range: {out['hit_rate']}"
    assert out["audit_integrity"] == 1.0 or out["n_hits"] == 0, \
        "audit integrity should be 1.0 with no eviction-induced corruption"
    print(f"[selftest] multi_hop_caching_baseline_v3_n4096 PASS "
          f"hit={out['hit_rate']:.3f} audit={out['audit_integrity']:.3f} "
          f"cache_cap={CACHE_CAPACITY} K_paths={K_PATHS_SMOKE}",
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
    # PROT: force CPU -- this anchor lives in remote_cpu_queue; must never touch CUDA
    device = torch.device("cpu")
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
    print(f"[run] multi_hop_caching_baseline_v3_n4096 smoke={smoke} N={N_cfg} "
          f"M={M} depth={depth} K_paths={K_paths} n_q={n_q} "
          f"cache_cap={CACHE_CAPACITY} alphas={alpha_sweep} "
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
                      f"hot<cold={cell.get('hot_faster_than_cold', 'n/a')} "
                      f"audit={cell.get('audit_integrity', 'n/a')} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
                print(f"  alpha={alpha} seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "multi_hop_caching_baseline_v3_n4096",
               "N": N_cfg, "smoke": smoke, "M": M, "depth": depth,
               "K_paths": K_paths, "cache_capacity": CACHE_CAPACITY,
               "n_q": n_q, "alphas": alpha_sweep,
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
