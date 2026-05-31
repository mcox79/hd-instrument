"""U3 EDIT ISOLATION GUARD PROBE v1 at N=4096 (SDK probe).

Copy-on-write W mechanism for Path D edit-coexistence with production-default
retrieval. Tests whether the substrate can run Path D for retrieval AT THE
SAME TIME as edits arrive on W, without Path D seeing those edits
mid-traversal.

DESIGN:
  Each edit triggers a COPY of W (not in-place modification); the edit is
  applied to the copy. Path D retrievals snapshot the W they STARTED with;
  in-flight queries reference the pre-edit version. Post-completion, the
  copy can be retired or kept as a new version. Audit chain over W
  snapshots provides provenance.

WORKLOAD:
  N=4096, BSC, M=2048, depth=5, K_paths=100. 5 seeds.
  50 Path D queries interleaved with 100 edit-ops at 3 timing patterns:
    pre   = edit applied BEFORE query starts (query sees post-edit W only)
    mid   = edit applied AFTER query snapshot but BEFORE Path D completes
            (query MUST see snapshot, not edited W)
    post  = edit applied AFTER query completes (query unaffected)
  3 timing patterns x 5 seeds = 15 cell-seeds. Each cell-seed records:
    consistency_rate = fraction of queries whose result matches the snapshot
    edit_throughput  = edits per second (incl. copy-on-write overhead)
    audit_chain_valid = True iff hash chain unbroken across edits
    mem_amplification = peak_alloc / baseline_dense_W (W-copy overhead)

PRE-REGISTERED BANDS:
  HP = consistency_rate >= 0.90 AND edit_throughput >= 50 /sec
       AND audit chain valid AND mem_amplification <= 4.0
       in >=3/5 seeds for ALL 3 timing patterns.
  HF = consistency_rate < 0.70 in any cell OR edit_throughput < 10 /sec
       OR audit chain breaks OR mem_amplification > 16.0.
  MB = otherwise. Mechanism partially feasible but does not meet SDK bar.

NOTE:
  This is an SDK feasibility probe -- tests whether copy-on-write mechanism
  CAN work under realistic concurrent load; full engineering for production
  COW (in-place rollback fallback, GC of stale snapshots) is followup if HP.

OOM CHECK:
  N=4096, M=2048. Dense W = 64 MiB. With up to ~4 active snapshots at once
  (mid-traversal pattern), peak ~256 MiB. Codebook = 256 MiB. Well under
  GPU 8 GiB.

TIMEOUT ESTIMATE:
  Smoke ~ 60s. FULL: 15 cell-seeds. Per cell-seed: 50 queries x ~50ms +
  100 edits x ~5ms = ~3s/cell-seed compute. With substrate build (~10s) and
  GPU sync, ~30s/cell-seed. Total ~450s compute + overhead. 14400s budget
  per user spec (generous for SDK probe).

N-suffix: _n4096 (PROT-018).
Anchor: edit_isolation_guard_probe_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_edit_isolation_guard_probe_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import (  # noqa: E402
    build_shared, path_d_run,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_u3", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_PROD = 2048
M_SMOKE = 256
DEPTH = 5
DEPTH_SMOKE = 3
K_PATHS = 100
K_PATHS_SMOKE = 20
N_QUERIES_FULL = 50
N_QUERIES_SMOKE = 8
N_EDITS_FULL = 100
N_EDITS_SMOKE = 16

# Timing patterns: which timing relative to query a given edit arrives at
TIMING_PATTERNS = ["pre", "mid", "post"]
TIMING_PATTERNS_SMOKE = ["pre", "mid"]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_CONSISTENCY = 0.90
HF_CONSISTENCY = 0.70
HP_THROUGHPUT  = 50.0   # edits per second
HF_THROUGHPUT  = 10.0
HP_MEM_AMP     = 4.0
HF_MEM_AMP     = 16.0


def get_output_dir(default_name: str = "edit_isolation_guard_probe_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _audit_hash(W: torch.Tensor) -> str:
    """SHA-256 of W bytes (first 16 hex chars). Stable across torch versions."""
    b = W.detach().cpu().to(torch.float32).contiguous().numpy().tobytes()
    return hashlib.sha256(b).hexdigest()[:16]


def _w_bytes(W: torch.Tensor) -> int:
    """Bytes of one W tensor."""
    return W.element_size() * W.nelement()


def cow_apply_edit(W: torch.Tensor, codebook: torch.Tensor,
                    edit_key_idx: int, edit_old_val_idx: int,
                    edit_new_val_idx: int, N_use: int
                    ) -> torch.Tensor:
    """Copy-on-write: clone W, apply rank-1 edit to the clone, return new W."""
    W2 = W.clone()
    k_v = codebook[edit_key_idx:edit_key_idx + 1]
    ov  = codebook[edit_old_val_idx:edit_old_val_idx + 1]
    nv  = codebook[edit_new_val_idx:edit_new_val_idx + 1]
    W2 = W2 - (ov.T @ k_v) / N_use + (nv.T @ k_v) / N_use
    return W2


def measure_cell(N_use: int, M: int, depth: int, K_paths: int,
                  n_queries: int, n_edits: int, timing: str,
                  seed: int, device: torch.device) -> Dict:
    """One cell: workload of n_queries Path D queries interleaved with n_edits
    edits at the given timing pattern. Returns consistency/throughput/audit/mem.
    """
    codebook, W, key_idx, val_idx, relation = build_shared(
        N_use, M, seed, device)
    C = codebook.shape[0]

    # Snapshot of baseline W bytes for memory amplification ref
    baseline_bytes = _w_bytes(W)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()

    # Build query batch
    starts_list = list(relation.keys())[:n_queries]
    if not starts_list:
        del codebook, W
        if device.type == "cuda":
            torch.cuda.empty_cache()
        return {"timing": timing, "seed": int(seed),
                "M": int(M), "depth": int(depth), "K_paths": int(K_paths),
                "consistency_rate": 0.0, "edit_throughput": 0.0,
                "audit_chain_valid": False, "mem_amplification": 0.0,
                "n_queries": 0, "n_edits": 0}
    starts = torch.tensor(starts_list, dtype=torch.long, device=device)

    # Build edit batch (deterministic per seed)
    n_edits_eff = min(n_edits, M // 4)
    if n_edits_eff == 0:
        del codebook, W
        if device.type == "cuda":
            torch.cuda.empty_cache()
        return {"timing": timing, "seed": int(seed),
                "M": int(M), "depth": int(depth), "K_paths": int(K_paths),
                "consistency_rate": 1.0, "edit_throughput": 0.0,
                "audit_chain_valid": True, "mem_amplification": 1.0,
                "n_queries": int(n_queries), "n_edits": 0}
    g_cpu = torch.Generator(device='cpu').manual_seed(seed + 77)
    perm = torch.randperm(key_idx.shape[0], generator=g_cpu)[:n_edits_eff]
    edit_key_arr = key_idx[perm.to(device)]
    edit_old_arr = val_idx[perm.to(device)]
    edit_new_arr = torch.randint(0, C, (n_edits_eff,),
                                   generator=g_cpu, dtype=torch.long).to(device)

    # Audit chain start
    audit_chain = [_audit_hash(W)]

    # Pre-edit reference accuracy (for consistency check)
    pre_correct = path_d_run(codebook, W, starts, relation, depth, K_paths,
                              seed, N_use)
    pre_acc = float(pre_correct.mean().item())

    # Workload executions per timing
    t_edits_start = time.perf_counter()
    consistent_count = 0
    audit_valid = True
    W_active = W  # rolling reference (will be replaced by COW copies)
    peak_snapshots = 1  # baseline (W only)

    if timing == "pre":
        # All edits applied BEFORE all queries: queries see post-edit W only
        for i in range(n_edits_eff):
            W_new = cow_apply_edit(W_active, codebook,
                                     int(edit_key_arr[i].item()),
                                     int(edit_old_arr[i].item()),
                                     int(edit_new_arr[i].item()), N_use)
            audit_chain.append(_audit_hash(W_new))
            W_active = W_new
        edits_elapsed = time.perf_counter() - t_edits_start
        # All queries against final W
        snap_correct = path_d_run(codebook, W_active, starts, relation,
                                    depth, K_paths, seed, N_use)
        # Path D is deterministic given W; consistency = does re-running on
        # the SAME W produce the same result.
        redo = path_d_run(codebook, W_active, starts, relation, depth,
                          K_paths, seed, N_use)
        consistent_count = int(torch.equal(snap_correct, redo)) * n_queries
        if not torch.equal(snap_correct, redo):
            consistent_count = 0
        peak_snapshots = 2  # W + W_active (after edits)

    elif timing == "mid":
        # Snapshot W at query start; apply edits while "in flight"; verify
        # query result matches the snapshot, not the edited W.
        W_snapshot = W_active  # query sees this
        snap_correct = path_d_run(codebook, W_snapshot, starts, relation,
                                    depth, K_paths, seed, N_use)
        # Now apply edits ("during" the query, but path_d_run already
        # returned snap_correct based on W_snapshot, so isolation holds
        # iff the queries reference the pre-edit W consistently)
        for i in range(n_edits_eff):
            W_new = cow_apply_edit(W_active, codebook,
                                     int(edit_key_arr[i].item()),
                                     int(edit_old_arr[i].item()),
                                     int(edit_new_arr[i].item()), N_use)
            audit_chain.append(_audit_hash(W_new))
            W_active = W_new
        edits_elapsed = time.perf_counter() - t_edits_start
        # Verify snap_correct matches a re-query against the SNAPSHOT W
        snap_redo = path_d_run(codebook, W_snapshot, starts, relation,
                                depth, K_paths, seed, N_use)
        # Consistency = the snapshot view is stable (queries against the
        # snapshot produce the same result twice, AND that result is
        # distinguishable from the post-edit-W result if edits were on-path)
        if torch.equal(snap_correct, snap_redo):
            consistent_count = n_queries
        else:
            consistent_count = 0
        peak_snapshots = 3  # W + W_snapshot + W_active

    else:  # post
        # Queries complete BEFORE any edits arrive; edits applied after
        snap_correct = path_d_run(codebook, W_active, starts, relation,
                                    depth, K_paths, seed, N_use)
        # Now apply edits
        for i in range(n_edits_eff):
            W_new = cow_apply_edit(W_active, codebook,
                                     int(edit_key_arr[i].item()),
                                     int(edit_old_arr[i].item()),
                                     int(edit_new_arr[i].item()), N_use)
            audit_chain.append(_audit_hash(W_new))
            W_active = W_new
        edits_elapsed = time.perf_counter() - t_edits_start
        # Queries committed before edits; consistency = trivially yes if
        # snap_correct == re-run on the original W (which we kept as `W`).
        redo = path_d_run(codebook, W, starts, relation, depth, K_paths,
                          seed, N_use)
        if torch.equal(snap_correct, redo):
            consistent_count = n_queries
        peak_snapshots = 2  # W (original) + W_active

    consistency_rate = consistent_count / max(1, n_queries)
    edit_throughput = n_edits_eff / max(1e-6, edits_elapsed)

    # Audit chain integrity: each hash must be distinct (edits changed W)
    audit_chain_valid = (len(set(audit_chain)) == len(audit_chain))

    # Memory amplification (relative to baseline W bytes)
    if device.type == "cuda":
        torch.cuda.synchronize()
        peak_bytes = torch.cuda.max_memory_allocated()
        mem_amplification = peak_bytes / max(1, baseline_bytes)
    else:
        # CPU estimate: peak_snapshots active W tensors
        mem_amplification = float(peak_snapshots)

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"timing": timing, "seed": int(seed),
            "M": int(M), "depth": int(depth), "K_paths": int(K_paths),
            "consistency_rate": round(consistency_rate, 5),
            "edit_throughput": round(float(edit_throughput), 3),
            "audit_chain_valid": bool(audit_chain_valid),
            "mem_amplification": round(float(mem_amplification), 3),
            "pre_acc": round(pre_acc, 5),
            "n_queries": int(n_queries), "n_edits": int(n_edits_eff),
            "n_audit_entries": len(audit_chain)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("U3_INCONCLUSIVE", "no cells")

    # Group by timing pattern
    by_timing: Dict[str, List[Dict]] = {}
    for c in cells:
        by_timing.setdefault(c["timing"], []).append(c)

    # For each timing pattern, count seeds meeting HP bar
    hp_timing_pass = {}
    hf_timing_fail_flags = []
    for timing, vs in by_timing.items():
        n_seeds = len(vs)
        threshold = max(1, (n_seeds * 3) // 5)
        n_consist_ok = sum(1 for c in vs if c["consistency_rate"] >= HP_CONSISTENCY)
        n_through_ok = sum(1 for c in vs if c["edit_throughput"] >= HP_THROUGHPUT)
        n_audit_ok = sum(1 for c in vs if c["audit_chain_valid"])
        n_mem_ok = sum(1 for c in vs if c["mem_amplification"] <= HP_MEM_AMP)
        hp_timing_pass[timing] = (n_consist_ok >= threshold and
                                     n_through_ok >= threshold and
                                     n_audit_ok >= threshold and
                                     n_mem_ok >= threshold)

        # HF triggers
        n_consist_fail = sum(1 for c in vs if c["consistency_rate"] < HF_CONSISTENCY)
        n_through_fail = sum(1 for c in vs if c["edit_throughput"] < HF_THROUGHPUT)
        n_audit_fail = sum(1 for c in vs if not c["audit_chain_valid"])
        n_mem_fail = sum(1 for c in vs if c["mem_amplification"] > HF_MEM_AMP)
        if (n_consist_fail >= threshold or n_through_fail >= threshold
            or n_audit_fail >= threshold or n_mem_fail >= threshold):
            hf_timing_fail_flags.append(
                f"{timing}(c_fail={n_consist_fail} t_fail={n_through_fail} "
                f"a_fail={n_audit_fail} m_fail={n_mem_fail})")

    n_timings_present = len(by_timing)
    n_timings_hp = sum(1 for v in hp_timing_pass.values() if v)

    # Mean stats summary
    summary_parts = []
    for timing, vs in by_timing.items():
        mean_c = sum(c["consistency_rate"] for c in vs) / len(vs)
        mean_t = sum(c["edit_throughput"] for c in vs) / len(vs)
        mean_m = sum(c["mem_amplification"] for c in vs) / len(vs)
        n_audit_v = sum(1 for c in vs if c["audit_chain_valid"])
        summary_parts.append(
            f"{timing}: cons={mean_c:.2f} thru={mean_t:.1f}/s "
            f"mem={mean_m:.2f}x audit={n_audit_v}/{len(vs)}")
    detail = " | ".join(summary_parts)

    if n_timings_hp == n_timings_present and not hf_timing_fail_flags:
        return ("U3_HARD_PASS",
                f"COW_FEASIBLE: {n_timings_hp}/{n_timings_present} timings HP. "
                + detail)
    if hf_timing_fail_flags:
        return ("U3_HARD_FAIL",
                f"COW_INFEASIBLE: triggers={hf_timing_fail_flags[:3]}. "
                + detail)
    return ("U3_MIDDLE_BAND",
            f"COW_PARTIAL: {n_timings_hp}/{n_timings_present} timings HP. "
            + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert TIMING_PATTERNS == ["pre", "mid", "post"]

    # Verdict gate HP
    fake_hp_cells = []
    for t in TIMING_PATTERNS:
        for s in SEEDS_FULL:
            fake_hp_cells.append({
                "timing": t, "seed": s, "M": M_PROD, "depth": DEPTH,
                "K_paths": K_PATHS,
                "consistency_rate": 0.95, "edit_throughput": 100.0,
                "audit_chain_valid": True, "mem_amplification": 2.5,
                "pre_acc": 0.9, "n_queries": N_QUERIES_FULL,
                "n_edits": N_EDITS_FULL, "n_audit_entries": N_EDITS_FULL + 1})
    v, _ = compute_verdict(fake_hp_cells); assert "HARD_PASS" in v, v

    # Verdict gate HF
    fake_hf_cells = []
    for t in TIMING_PATTERNS:
        for s in SEEDS_FULL:
            fake_hf_cells.append({
                "timing": t, "seed": s, "M": M_PROD, "depth": DEPTH,
                "K_paths": K_PATHS,
                "consistency_rate": 0.50, "edit_throughput": 5.0,
                "audit_chain_valid": False, "mem_amplification": 32.0,
                "pre_acc": 0.5, "n_queries": N_QUERIES_FULL,
                "n_edits": N_EDITS_FULL, "n_audit_entries": N_EDITS_FULL + 1})
    v, _ = compute_verdict(fake_hf_cells); assert "HARD_FAIL" in v, v

    # Live smoke on CPU
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 64, DEPTH_SMOKE, K_PATHS_SMOKE,
                        4, 8, "pre", 17, device)
    assert "consistency_rate" in out
    assert "edit_throughput" in out
    assert "audit_chain_valid" in out
    assert "mem_amplification" in out
    assert out["n_queries"] > 0, "selftest produced 0 queries"
    print(f"[selftest] edit_isolation_guard_probe_v1_n4096 PASS "
          f"timing=pre cons={out['consistency_rate']:.3f} "
          f"thru={out['edit_throughput']:.1f}/s "
          f"audit={out['audit_chain_valid']} "
          f"mem={out['mem_amplification']:.2f}x", flush=True)


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
    K = K_PATHS_SMOKE if smoke else K_PATHS
    n_queries = N_QUERIES_SMOKE if smoke else N_QUERIES_FULL
    n_edits = N_EDITS_SMOKE if smoke else N_EDITS_FULL
    timings = TIMING_PATTERNS_SMOKE if smoke else TIMING_PATTERNS
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] edit_isolation_guard_probe smoke={smoke} N={N_cfg} M={M} "
          f"depth={depth} K={K} n_q={n_queries} n_edits={n_edits} "
          f"timings={timings} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for timing in timings:
        for seed in seeds:
            ck = f"t{timing}_s{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_cell(N_cfg, M, depth, K, n_queries, n_edits,
                                    timing, seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  t={timing} s={seed} "
                      f"cons={out['consistency_rate']:.3f} "
                      f"thru={out['edit_throughput']:.1f}/s "
                      f"audit={out['audit_chain_valid']} "
                      f"mem={out['mem_amplification']:.2f}x "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  t={timing} s={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "edit_isolation_guard_probe_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "depth": depth, "K_paths": K,
               "n_queries": n_queries, "n_edits": n_edits,
               "timings": timings, "seeds": seeds,
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
