"""G12 MEMORY PATTERN CHARACTERIZATION v1 at N=4096.

CONTEXT (v290 cap_map follow-on):
  Production engineering foundation. Profile memory access patterns for
  substrate operations (store, retrieve, edit, Path D multi-hop).

INSTRUMENTATION:
  torch.cuda.memory_allocated trace + memory_reserved trace + per-op
  allocation count. Identify hot allocations (peak alloc per op).

OPERATIONS:
  1. store: build W from M outer products
  2. retrieve: single-hop W @ q
  3. edit: rank-1 delta to W
  4. multi_hop: Path D depth=5 K=100

PRE-REGISTERED BANDS:
  HP = clean profile emitted for all 4 operations AND identifies dominant
       allocation per operation.
  HF = instrumentation crashes OR profile incoherent.
  MB = partial.

NOTE: this is a CHARACTERIZATION test. The result IS the profile, not a
HP/HF call on substrate behavior. We pass when profiling cleanly runs.

PROT-018: _n4096 binds N = 4096.
PROT-020: torch + cuda available.
PROT-021: per-cell-seed checkpointing.

Anchor: memory_pattern_characterization_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_memory_pattern_characterization_v1_n4096.md
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

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g12", _ck_path)
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
N_OPS_PER_TYPE = 100
N_OPS_SMOKE = 8
DEPTH = 5
DEPTH_SMOKE = 2
K_PATHS = 100
K_PATHS_SMOKE = 10
N_STARTS = 16
N_STARTS_SMOKE = 4
BETA_D = 4.0
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

OPERATIONS = ["store", "retrieve", "edit", "multi_hop"]


def get_output_dir(default_name: str = "memory_pattern_characterization_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe_clear(device: torch.device) -> None:
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass


def _mem_alloc_bytes(device: torch.device) -> int:
    if device.type == "cuda":
        return int(torch.cuda.memory_allocated())
    # CPU fallback: track via best-effort (no precise API)
    return 0


def _mem_reserved_bytes(device: torch.device) -> int:
    if device.type == "cuda":
        return int(torch.cuda.memory_reserved())
    return 0


def _reset_peak(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats()


def _peak_alloc_bytes(device: torch.device) -> int:
    if device.type == "cuda":
        return int(torch.cuda.max_memory_allocated())
    return 0


def profile_store_op(N_use, M, seed, device) -> Dict:
    """Profile: build W from M outer products."""
    _safe_clear(device)
    _reset_peak(device)
    pre = _mem_alloc_bytes(device)
    samples = []
    t0 = time.perf_counter()
    g = torch.Generator(device='cpu').manual_seed(seed)
    keys = torch.randn(M, N_use)
    vals = torch.randn(M, N_use)
    if device.type == 'cuda':
        keys = keys.to(device)
        vals = vals.to(device)
    samples.append(_mem_alloc_bytes(device) - pre)
    W = (vals.T @ keys) / N_use
    samples.append(_mem_alloc_bytes(device) - pre)
    elapsed = time.perf_counter() - t0
    peak = _peak_alloc_bytes(device)
    del keys, vals, W
    _safe_clear(device)
    return {"op": "store",
            "peak_alloc_bytes": int(peak),
            "trace_bytes": [int(s) for s in samples],
            "mean_alloc_bytes": int(sum(samples) / max(1, len(samples))),
            "elapsed_s": round(elapsed, 4),
            "n_allocs": len(samples)}


def profile_retrieve_op(codebook, W, keys, vals, N_use, n_ops, seed,
                          device) -> Dict:
    """Profile: single-hop retrieval, n_ops queries."""
    _safe_clear(device)
    _reset_peak(device)
    pre = _mem_alloc_bytes(device)
    samples = []
    t0 = time.perf_counter()
    g = torch.Generator(device='cpu').manual_seed(seed + 10)
    perm = torch.randperm(keys.shape[0], generator=g)[:n_ops].to(device)
    q = keys[perm]
    samples.append(_mem_alloc_bytes(device) - pre)
    out = q @ W.T
    samples.append(_mem_alloc_bytes(device) - pre)
    sims = (codebook @ out.T) / N_use
    samples.append(_mem_alloc_bytes(device) - pre)
    pred = torch.argmax(sims, dim=0)
    samples.append(_mem_alloc_bytes(device) - pre)
    elapsed = time.perf_counter() - t0
    peak = _peak_alloc_bytes(device)
    del q, out, sims, pred
    _safe_clear(device)
    return {"op": "retrieve",
            "peak_alloc_bytes": int(peak),
            "trace_bytes": [int(s) for s in samples],
            "mean_alloc_bytes": int(sum(samples) / max(1, len(samples))),
            "elapsed_s": round(elapsed, 4),
            "n_allocs": len(samples)}


def profile_edit_op(codebook, W, key_idx, val_idx, N_use, n_ops, seed,
                     device) -> Dict:
    """Profile: apply n_ops rank-1 edits to W."""
    _safe_clear(device)
    _reset_peak(device)
    pre = _mem_alloc_bytes(device)
    samples = []
    t0 = time.perf_counter()
    g = torch.Generator(device='cpu').manual_seed(seed + 20)
    e_perm = torch.randperm(key_idx.shape[0], generator=g)[:n_ops].to(device)
    e_k = codebook[key_idx[e_perm]]
    e_ov = codebook[val_idx[e_perm]]
    g2 = torch.Generator(device='cpu').manual_seed(seed + 30)
    e_nv_idx = torch.randint(0, codebook.shape[0], (n_ops,), generator=g2,
                              dtype=torch.long).to(device)
    e_nv = codebook[e_nv_idx]
    samples.append(_mem_alloc_bytes(device) - pre)
    W_edit = W - (e_ov.T @ e_k) / N_use + (e_nv.T @ e_k) / N_use
    samples.append(_mem_alloc_bytes(device) - pre)
    elapsed = time.perf_counter() - t0
    peak = _peak_alloc_bytes(device)
    del e_k, e_ov, e_nv, W_edit
    _safe_clear(device)
    return {"op": "edit",
            "peak_alloc_bytes": int(peak),
            "trace_bytes": [int(s) for s in samples],
            "mean_alloc_bytes": int(sum(samples) / max(1, len(samples))),
            "elapsed_s": round(elapsed, 4),
            "n_allocs": len(samples)}


def profile_multi_hop_op(codebook, W, key_idx, val_idx, relation, N_use,
                           n_starts, depth, K_paths, seed, device) -> Dict:
    """Profile: Path D multi-hop."""
    _safe_clear(device)
    _reset_peak(device)
    pre = _mem_alloc_bytes(device)
    samples = []
    t0 = time.perf_counter()
    starts_list = list(relation.keys())[:n_starts]
    if not starts_list:
        return {"op": "multi_hop", "peak_alloc_bytes": 0, "trace_bytes": [0],
                "mean_alloc_bytes": 0, "elapsed_s": 0.0, "n_allocs": 0,
                "error": "no starts"}
    starts = torch.tensor(starts_list, dtype=torch.long, device=device)
    samples.append(_mem_alloc_bytes(device) - pre)
    correct = path_d_run(codebook, W, starts, relation, depth, K_paths,
                          seed, N_use, beta=BETA_D)
    samples.append(_mem_alloc_bytes(device) - pre)
    elapsed = time.perf_counter() - t0
    peak = _peak_alloc_bytes(device)
    del starts, correct
    _safe_clear(device)
    return {"op": "multi_hop",
            "peak_alloc_bytes": int(peak),
            "trace_bytes": [int(s) for s in samples],
            "mean_alloc_bytes": int(sum(samples) / max(1, len(samples))),
            "elapsed_s": round(elapsed, 4),
            "n_allocs": len(samples)}


def measure_seed(N_use: int, M: int, n_ops: int, depth: int, K_paths: int,
                   n_starts: int, seed: int, device: torch.device) -> Dict:
    out = {}
    try:
        # store profile (fresh build)
        out["store"] = profile_store_op(N_use, M, seed, device)
        # Build substrate for subsequent ops
        codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
        keys = codebook[key_idx]
        vals = codebook[val_idx]
        out["retrieve"] = profile_retrieve_op(codebook, W, keys, vals, N_use,
                                                n_ops, seed, device)
        out["edit"] = profile_edit_op(codebook, W, key_idx, val_idx, N_use,
                                        n_ops, seed, device)
        out["multi_hop"] = profile_multi_hop_op(codebook, W, key_idx, val_idx,
                                                  relation, N_use, n_starts,
                                                  depth, K_paths, seed, device)
        del codebook, W
        _safe_clear(device)
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)[:300]
    return {"seed": int(seed), "M": int(M), "device": device.type,
            "profiles": out}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("G12_INCONCLUSIVE", "no cells")
    valid_cells = [c for c in cells if "error" not in c.get("profiles", {})]
    if not valid_cells:
        return ("G12_HARD_FAIL", f"all {len(cells)} cells errored")

    # All 4 ops present in all valid cells?
    all_ops_present = all(
        all(op in c["profiles"] for op in OPERATIONS)
        for c in valid_cells)
    if not all_ops_present:
        return ("G12_MIDDLE_BAND", "some_ops_missing")

    # Identify dominant alloc per op
    dom_summary = {}
    for op in OPERATIONS:
        peaks = [c["profiles"][op]["peak_alloc_bytes"] for c in valid_cells
                 if "peak_alloc_bytes" in c["profiles"][op]]
        means = [c["profiles"][op]["mean_alloc_bytes"] for c in valid_cells
                 if "mean_alloc_bytes" in c["profiles"][op]]
        elap = [c["profiles"][op]["elapsed_s"] for c in valid_cells
                if "elapsed_s" in c["profiles"][op]]
        dom_summary[op] = {
            "median_peak_mb": round(sorted(peaks)[len(peaks) // 2] / (1024 * 1024), 3) if peaks else 0,
            "median_mean_mb": round(sorted(means)[len(means) // 2] / (1024 * 1024), 3) if means else 0,
            "median_elapsed_s": round(sorted(elap)[len(elap) // 2], 4) if elap else 0,
        }

    detail = " | ".join(
        f"{op}: peak={dom_summary[op]['median_peak_mb']:.2f}MB "
        f"elap={dom_summary[op]['median_elapsed_s']:.3f}s"
        for op in OPERATIONS)
    return ("G12_HARD_PASS", "PROFILE_EMITTED: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(OPERATIONS) == 4
    assert len(SEEDS_FULL) == 5

    # Verdict gate HP
    fake_hp = [{"seed": s, "M": M_PROD, "device": "cpu",
                "profiles": {op: {"peak_alloc_bytes": 1024 * 1024 * 100,
                                    "trace_bytes": [100, 200, 300],
                                    "mean_alloc_bytes": 200,
                                    "elapsed_s": 0.1, "n_allocs": 3}
                              for op in OPERATIONS}}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF (all error)
    fake_hf = [{"seed": s, "M": M_PROD, "device": "cpu",
                "profiles": {"error": "fake"}}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Live smoke on CPU
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 128, 4, DEPTH_SMOKE, K_PATHS_SMOKE,
                        N_STARTS_SMOKE, 17, device)
    assert "profiles" in out
    for op in OPERATIONS:
        assert op in out["profiles"], f"op {op} missing"
        assert "peak_alloc_bytes" in out["profiles"][op]
    print(f"[selftest] memory_pattern_characterization_v1_n4096 PASS "
          f"4/4 operations profiled", flush=True)


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
    n_ops = N_OPS_SMOKE if smoke else N_OPS_PER_TYPE
    depth = DEPTH_SMOKE if smoke else DEPTH
    K_paths = K_PATHS_SMOKE if smoke else K_PATHS
    n_starts = N_STARTS_SMOKE if smoke else N_STARTS
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] memory_pattern_characterization_v1_n4096 smoke={smoke} "
          f"N={N_cfg} M={M} n_ops={n_ops} depth={depth} K_paths={K_paths} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            cell = measure_seed(N_cfg, M, n_ops, depth, K_paths, n_starts,
                                  seed, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ops={list(cell['profiles'].keys())} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)
            _safe_clear(device)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "memory_pattern_characterization_v1_n4096",
               "N": N_cfg, "smoke": smoke, "M": M, "n_ops": n_ops,
               "depth": depth, "K_paths": K_paths, "seeds": seeds,
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
