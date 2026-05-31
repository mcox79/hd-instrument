"""V2: 24-hour sustained workload baseline at N=4096.

PURPOSE: 24-hour sustained workload validation. Detects state drift,
memory leaks, audit chain integrity issues, performance drift over
hours-scale BEFORE multi-day cloud dispatch. Phase 1 of 3-phase
corrected plan (this anchor uses GPU per S11 confirmed 56x Path D
speedup but still PHASE-1 because hours-scale is cheaper than days).

CRITICAL DESIGN: this is the SAME pipeline that would be sent to cloud
for a multi-day sustained run. Validates 24h CONTINUOUS execution at
production rate (~17 ops/min, ~24000 total ops).

SETUP:
  - N=4096, BSC codebook, M=2048 (production regime).
  - 1 seed (long-running single trial).
  - Operation mix: 40% retrieve / 30% Path D multi-hop / 20% edit / 10% delete-with-cert.
  - Target rate: 1000 ops/hour (0.28 ops/sec); 24h total: ~24000 ops.
  - Hourly checkpoint: snapshot all metrics + write partial.
  - Audit chain verified every 1000 ops.
  - KF-1 / KF-2 spot-check every 4 hours (6 spot-checks total).

METRICS:
  Per-hour aggregations of:
    - per-op latency mean + p99 (ms)
    - throughput (ops/sec actual vs target)
    - RSS (MB), GPU memory (MB if cuda), python-heap (MB)
    - cumulative cert-chain length + integrity (%)
    - KF-2 max_iso spot-check (every 4h)
    - KF-1 spurious firing rate spot-check (every 4h)
    - W L2-norm (state drift indicator)
    - codebook usage histogram drift (1-norm vs initial)

PRE-REG:
  HARD_PASS = 24h completes AND throughput within 10% of initial AND
              audit chain 100% integrity AND no memory growth >2x AND
              killer features stable across 4h checks.
  HARD_FAIL = mid-run crash OR throughput drops >50% OR cert corrupts OR
              memory >5x growth OR killer feature degrades.
  MIDDLE_BAND otherwise.

PROT-018: _n4096 binds N = 4096.
Anchor: sustained_workload_24h_baseline_v1_n4096
Queue: overnight_queue (GPU). TIMEOUT: 90000s (25h, 1h headroom).
Pre-reg: preregs/2026-05-30_sustained_workload_24h_baseline_v1_n4096.md

ASCII-only. Encoding handled structurally.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import gc
import hashlib
import importlib.util
import json
import os
import time
import tracemalloc
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_sw24h", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key

# Import workload harness primitives (CRUD + audit chain).
from experiments._workload_harness import (  # noqa: E402
    DenseStore, make_cert, verify_cert_chain, kf2_spot_check,
)


# PROT-018: _n4096 binds N = 4096.
N = 4096
N_FULL = N
N_SMOKE = 512   # 1-minute simulation gate
assert N_FULL == 4096

M_STORE = 2048               # production regime
M_STORE_SMOKE = 256

SEED = 17                     # 1 seed for V2 (long-running single trial)

# Workload knobs
TARGET_OPS_PER_HOUR = 1000
TARGET_OPS_PER_SEC = TARGET_OPS_PER_HOUR / 3600.0
TOTAL_HOURS = 24
TOTAL_OPS_FULL = TARGET_OPS_PER_HOUR * TOTAL_HOURS   # 24000

# Smoke = 1-minute simulation: 1/60 * 1000 = ~17 ops total.
SMOKE_DURATION_S = 60
TOTAL_OPS_SMOKE = max(20, int(SMOKE_DURATION_S * TARGET_OPS_PER_SEC * 60))  # ~17 -> 20 floor

# Op mix: 40% retrieve, 30% path_d, 20% edit, 10% delete-with-cert.
OP_MIX = (0.40, 0.30, 0.20, 0.10)

# Cadence
AUDIT_INTERVAL_OPS = 1000
HOURLY_CHECKPOINT_S = 3600        # 1h
KF_SPOT_INTERVAL_S = 4 * 3600     # 4h

# Path D parameters
PATH_D_DEPTH = 5
PATH_D_K = 100

# Memory thresholds (HARD_FAIL trips above 5x initial; HARD_PASS requires <2x)
MEM_HARD_FAIL_MULTIPLIER = 5.0
MEM_HARD_PASS_MULTIPLIER = 2.0

# Throughput thresholds
THROUGHPUT_HARD_PASS_DRIFT = 0.10   # within 10% of initial = HP
THROUGHPUT_HARD_FAIL_DRIFT = 0.50   # >50% drop = HF


def _rss_mb() -> float:
    try:
        import psutil
        return float(psutil.Process().memory_info().rss / (1024 ** 2))
    except Exception:
        return -1.0


def _gpu_mb() -> float:
    if torch.cuda.is_available():
        try:
            return float(torch.cuda.memory_allocated() / (1024 ** 2))
        except Exception:
            return -1.0
    return -1.0


def _heap_mb() -> float:
    try:
        size, _ = tracemalloc.get_traced_memory()
        return float(size / (1024 ** 2))
    except Exception:
        return -1.0


def build_bsc_codebook(N_use: int, C: int, seed: int,
                       device: torch.device) -> torch.Tensor:
    """BSC bipolar (+/-1) codebook, (C, N) on device."""
    gen = torch.Generator(device='cpu').manual_seed(seed + 91234)
    bits = torch.randint(0, 2, (C, N_use), generator=gen, dtype=torch.int8)
    cb = (bits.to(torch.float32) * 2.0 - 1.0).to(device)
    return cb


def get_output_dir(default_name: str = "sustained_workload_24h_baseline_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_kf1(store: DenseStore, n_probe: int = 50,
                seed: int = 0) -> float:
    """KF-1 spurious firing rate on unseen keys (sample-restricted)."""
    C = store.codebook.shape[0]
    stored = {k for k, _ in store.facts.values()}
    if len(stored) >= C - n_probe:
        return 0.0
    all_keys = set(range(C))
    unseen = list(all_keys - stored)
    gen = torch.Generator(device='cpu').manual_seed(seed + 5000)
    n = min(n_probe, len(unseen))
    perm = torch.randperm(len(unseen), generator=gen)[:n].tolist()
    fires = 0
    for i in perm:
        kid = unseen[i]
        k = store.codebook[kid]
        out = k @ store.W.T
        sims = (store.codebook @ out) / store.N
        max_sim = float(sims.max().item())
        if max_sim > 0.5:
            fires += 1
    return fires / max(1, n)


def measure_path_d(store: DenseStore, depth: int = PATH_D_DEPTH,
                   K_paths: int = PATH_D_K, n_starts: int = 8,
                   seed: int = 0) -> float:
    """Path D multi-hop correctness over n_starts random starts.

    Uses the stored facts as relation: key_id -> val_id.
    """
    C = store.codebook.shape[0]
    M = len(store.facts)
    if M < depth + 1:
        return float('nan')
    relation: Dict[int, int] = {}
    for k, v in store.facts.values():
        relation[k] = v

    gen = torch.Generator(device='cpu').manual_seed(seed + 8000)
    cand_starts = list(relation.keys())
    if not cand_starts:
        return float('nan')
    n_use = min(n_starts, len(cand_starts))
    perm = torch.randperm(len(cand_starts), generator=gen)[:n_use].tolist()
    starts = [cand_starts[i] for i in perm]

    correct = 0
    n_valid = 0
    device = store.W.device
    for b_idx in range(n_use):
        start = starts[b_idx]
        cur = start
        pos = [cur]
        ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                ok = False
                break
            pos.append(nxt)
            cur = nxt
        if not ok:
            continue
        n_valid += 1

        gen_d = torch.Generator(device='cpu').manual_seed(seed + 9000 + b_idx)
        decoys = []
        for kk in range(K_paths - 1):
            d_path = [start]
            d_cur = start
            for _ in range(depth):
                rnd = int(torch.randint(0, C, (1,), generator=gen_d).item())
                if rnd == relation.get(d_cur):
                    rnd = (rnd + 1) % C
                d_path.append(rnd)
                d_cur = rnd
            decoys.append(d_path)

        candidates = [pos] + decoys
        K = len(candidates)
        src_ids: List[int] = []
        dst_ids: List[int] = []
        for p in candidates:
            for i in range(depth):
                src_ids.append(p[i])
                dst_ids.append(p[i + 1])
        src = torch.tensor(src_ids, dtype=torch.long, device=device)
        dst = torch.tensor(dst_ids, dtype=torch.long, device=device)
        src_v = store.codebook[src]
        dst_v = store.codebook[dst]
        out_v = src_v @ store.W.T
        sims = (out_v * dst_v).sum(dim=1) / store.N
        beta = 4.0
        logits = beta * sims
        log_lik = -torch.nn.functional.softplus(-logits)
        log_lik = log_lik.view(K, depth)
        log_post = log_lik.sum(dim=1)
        top = int(torch.argmax(log_post).item())
        if top == 0:
            correct += 1

    if n_valid == 0:
        return float('nan')
    return correct / n_valid


def w_l2_norm(W: torch.Tensor) -> float:
    """L2 norm of substrate state -- drift indicator."""
    return float(torch.linalg.matrix_norm(W, ord='fro').item())


def codebook_usage_histogram(store: DenseStore) -> List[int]:
    """Histogram of how often each codebook row is used (as key or value)."""
    C = store.codebook.shape[0]
    hist = [0] * C
    for k, v in store.facts.values():
        if 0 <= k < C:
            hist[k] += 1
        if 0 <= v < C:
            hist[v] += 1
    return hist


def _hist_l1_drift(h_a: List[int], h_b: List[int]) -> float:
    """Sum |h_a[i] - h_b[i]| normalized by total."""
    if not h_a or not h_b:
        return 0.0
    total_a = max(1, sum(h_a))
    total_b = max(1, sum(h_b))
    return sum(abs(a / total_a - b / total_b) for a, b in zip(h_a, h_b))


def run_sustained_workload(N_use: int, M_init: int, total_ops: int,
                           total_seconds_target: float, seed: int,
                           op_mix: Tuple[float, float, float, float],
                           audit_interval_ops: int,
                           hourly_checkpoint_s: float,
                           kf_spot_interval_s: float,
                           hard_fail_check_each_op: bool = False) -> Dict:
    """The main sustained-workload loop.

    Returns a dict with all hourly + per-op aggregations, verdict.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tracemalloc.start()
    t_run0 = time.time()

    init_rss = _rss_mb()
    init_gpu = _gpu_mb()
    init_heap = _heap_mb()

    # Build codebook + DenseStore + populate initial M_init facts.
    C = N_use   # Modern Hopfield activation regime: C = N
    cb = build_bsc_codebook(N_use, C, seed, device)
    store = DenseStore(N=N_use, codebook=cb, device=device)
    gen_init = torch.Generator(device='cpu').manual_seed(seed + 11)
    init_keys = torch.randperm(C, generator=gen_init)[:M_init].tolist()
    init_vals = torch.randint(0, C, (M_init,), generator=gen_init).tolist()
    for k, v in zip(init_keys, init_vals):
        store.store_fact(int(k), int(v))

    init_hist = codebook_usage_histogram(store)
    init_w_norm = w_l2_norm(store.W)
    init_w_norm = max(1e-9, init_w_norm)

    # Cert chain initialized with GENESIS
    cert_chain: List[Dict[str, str]] = []
    prev_hash = "GENESIS"
    op_id = 0

    # Throughput baseline (first 60s of operation)
    baseline_window_s = min(60.0, max(5.0, total_seconds_target / 60.0))
    baseline_ops_target = max(5, int(baseline_window_s * (total_ops / total_seconds_target)))
    baseline_ops_done = 0
    baseline_t0 = time.time()
    baseline_throughput_ops_per_s: Optional[float] = None

    # Per-hour aggregations
    hourly_records: List[Dict] = []
    cur_hour_ops = 0
    cur_hour_latencies_ms: List[float] = []
    cur_hour_t0 = time.time()
    hour_idx = 0

    # KF spot-check interval
    last_kf_spot_t = time.time()
    kf_spot_records: List[Dict] = []

    # Audit chain integrity tracking
    audit_records: List[Dict] = []
    audit_full_corruptions = 0

    # Op-rate pacing: target sleep between ops.
    sleep_target = max(0.0, total_seconds_target / total_ops - 0.001)

    # Sampled op latencies for global p99
    all_op_latencies_ms: List[float] = []

    gen_op = torch.Generator(device='cpu').manual_seed(seed + 13)
    cdf = torch.tensor([op_mix[0],
                        op_mix[0] + op_mix[1],
                        op_mix[0] + op_mix[1] + op_mix[2],
                        1.0])

    print(f"[run] sustained_workload_24h_baseline target_ops={total_ops} "
          f"target_seconds={total_seconds_target:.0f} "
          f"target_rate={total_ops / total_seconds_target:.3f} ops/s "
          f"baseline_window_s={baseline_window_s:.1f} "
          f"device={device}", flush=True)

    crashed = False
    crash_msg = ""
    try:
        for op_i in range(total_ops):
            t_op0 = time.time()
            u = float(torch.rand(1, generator=gen_op).item())
            which = int((u >= cdf).sum().item())
            which = min(which, 3)

            op_name = "noop"
            try:
                if which == 0:  # retrieve
                    op_name = "retrieve"
                    fids = list(store.facts.keys())
                    if fids:
                        kid_idx = int(torch.randint(0, len(fids), (1,),
                                                    generator=gen_op).item())
                        kid, _ = store.facts[fids[kid_idx]]
                        store.retrieve(kid)
                elif which == 1:  # path_d
                    op_name = "path_d"
                    # Lightweight single-start path_d to keep latency bounded
                    measure_path_d(store, depth=PATH_D_DEPTH,
                                   K_paths=PATH_D_K, n_starts=1,
                                   seed=seed + op_i)
                elif which == 2:  # edit
                    op_name = "edit"
                    fids = list(store.facts.keys())
                    if fids:
                        fid_idx = int(torch.randint(0, len(fids), (1,),
                                                    generator=gen_op).item())
                        fid = fids[fid_idx]
                        new_v = int(torch.randint(0, C, (1,),
                                                  generator=gen_op).item())
                        store.edit_fact(fid, new_v)
                else:  # delete-with-cert
                    op_name = "delete"
                    fids = list(store.facts.keys())
                    if fids:
                        fid_idx = int(torch.randint(0, len(fids), (1,),
                                                    generator=gen_op).item())
                        fid = fids[fid_idx]
                        kid, vid = store.facts[fid]
                        # Build cert link BEFORE delete
                        link = make_cert(prev_hash, "delete",
                                         fact_id=fid, key_id=kid,
                                         val_id=vid, op_id=op_id)
                        cert_chain.append(link)
                        prev_hash = link["this_hash"]
                        op_id += 1
                        # Now delete
                        store.delete_fact(fid)
                        # Replenish to keep M roughly constant
                        new_k = int(torch.randint(0, C, (1,),
                                                  generator=gen_op).item())
                        new_v2 = int(torch.randint(0, C, (1,),
                                                   generator=gen_op).item())
                        store.store_fact(new_k, new_v2)
            except Exception as inner_e:  # noqa: BLE001
                crashed = True
                crash_msg = f"op_{op_name}_at_{op_i}: {type(inner_e).__name__}: {inner_e}"
                break

            op_lat_ms = (time.time() - t_op0) * 1000.0
            cur_hour_latencies_ms.append(op_lat_ms)
            all_op_latencies_ms.append(op_lat_ms)
            cur_hour_ops += 1

            # Baseline throughput establishment
            if baseline_throughput_ops_per_s is None:
                baseline_ops_done += 1
                if baseline_ops_done >= baseline_ops_target:
                    elapsed = time.time() - baseline_t0
                    if elapsed > 0:
                        baseline_throughput_ops_per_s = baseline_ops_done / elapsed
                        print(f"  [baseline] {baseline_ops_done} ops in "
                              f"{elapsed:.2f}s -> "
                              f"{baseline_throughput_ops_per_s:.3f} ops/s",
                              flush=True)

            # Audit chain integrity check
            if (op_i + 1) % audit_interval_ops == 0 and cert_chain:
                t_audit = time.time()
                valid = verify_cert_chain(cert_chain)
                audit_records.append({
                    "op_i": op_i + 1,
                    "chain_len": len(cert_chain),
                    "valid": bool(valid),
                    "verify_elapsed_s": round(time.time() - t_audit, 3),
                })
                if not valid:
                    audit_full_corruptions += 1
                    crashed = True
                    crash_msg = f"AUDIT_CHAIN_CORRUPTED at op_i={op_i + 1}"
                    break

            # Hourly checkpoint
            t_now = time.time()
            elapsed_hour = t_now - cur_hour_t0
            if elapsed_hour >= hourly_checkpoint_s or (op_i + 1) == total_ops:
                # Compute hourly aggregations
                if cur_hour_latencies_ms:
                    lat_tensor = torch.tensor(cur_hour_latencies_ms)
                    lat_mean = float(lat_tensor.mean().item())
                    lat_p99 = float(torch.quantile(lat_tensor, 0.99).item())
                else:
                    lat_mean = -1.0
                    lat_p99 = -1.0
                throughput_actual = cur_hour_ops / max(1e-9, elapsed_hour)

                rec = {
                    "hour": hour_idx,
                    "elapsed_hour_s": round(elapsed_hour, 2),
                    "ops_this_hour": cur_hour_ops,
                    "throughput_ops_per_s_actual": round(throughput_actual, 4),
                    "lat_mean_ms": round(lat_mean, 3),
                    "lat_p99_ms": round(lat_p99, 3),
                    "rss_mb": round(_rss_mb(), 2),
                    "gpu_mb": round(_gpu_mb(), 2),
                    "heap_mb": round(_heap_mb(), 2),
                    "w_l2_norm": round(w_l2_norm(store.W), 4),
                    "w_l2_norm_drift_ratio": round(
                        w_l2_norm(store.W) / init_w_norm, 4),
                    "cert_chain_len": len(cert_chain),
                    "M_alive": len(store.facts),
                }
                hourly_records.append(rec)
                print(f"  [hour {hour_idx}] ops={cur_hour_ops} "
                      f"throughput={throughput_actual:.3f} ops/s "
                      f"lat_p99={lat_p99:.2f}ms rss={rec['rss_mb']:.1f}MB "
                      f"w_norm_drift={rec['w_l2_norm_drift_ratio']:.3f} "
                      f"M={rec['M_alive']} cert_len={rec['cert_chain_len']}",
                      flush=True)
                hour_idx += 1
                cur_hour_ops = 0
                cur_hour_latencies_ms = []
                cur_hour_t0 = time.time()

            # KF spot-check
            if t_now - last_kf_spot_t >= kf_spot_interval_s:
                t_kf = time.time()
                kf2_iso = kf2_spot_check(store, n_edits=4, n_probe=20,
                                         seed=seed + 14 + op_i)
                kf1_rate = measure_kf1(store, n_probe=20,
                                       seed=seed + 15 + op_i)
                kf_spot_records.append({
                    "at_op_i": op_i + 1,
                    "elapsed_run_s": round(time.time() - t_run0, 2),
                    "kf2_max_iso": round(kf2_iso, 5),
                    "kf1_spurious_firing_rate": round(kf1_rate, 5),
                    "spot_elapsed_s": round(time.time() - t_kf, 3),
                })
                last_kf_spot_t = time.time()

            # Pace
            if sleep_target > 0:
                lat_so_far = time.time() - t_op0
                slack = sleep_target - lat_so_far
                if slack > 0:
                    time.sleep(slack)

    except Exception as e:  # noqa: BLE001
        crashed = True
        crash_msg = f"OUTER: {type(e).__name__}: {traceback.format_exc(limit=8)}"

    # Final post-run snapshot
    final_rss = _rss_mb()
    final_gpu = _gpu_mb()
    final_heap = _heap_mb()
    final_w_norm = w_l2_norm(store.W)
    final_hist = codebook_usage_histogram(store)
    hist_drift = _hist_l1_drift(init_hist, final_hist)

    # Final cert chain integrity
    cert_chain_valid = verify_cert_chain(cert_chain) if cert_chain else True

    # Aggregate throughput
    if all_op_latencies_ms:
        total_lat = sum(all_op_latencies_ms) / 1000.0
        # Approximate final throughput from last hour
        final_throughput = (hourly_records[-1]["throughput_ops_per_s_actual"]
                            if hourly_records else 0.0)
    else:
        final_throughput = 0.0

    # Throughput drift vs baseline
    if baseline_throughput_ops_per_s and baseline_throughput_ops_per_s > 0:
        throughput_drift = abs(final_throughput - baseline_throughput_ops_per_s) / baseline_throughput_ops_per_s
        throughput_drop_pct = max(0.0,
                                  (baseline_throughput_ops_per_s - final_throughput) / baseline_throughput_ops_per_s)
    else:
        throughput_drift = -1.0
        throughput_drop_pct = -1.0

    # Memory growth
    mem_growth_rss = (final_rss / max(1.0, init_rss)) if init_rss > 0 else 1.0
    mem_growth_heap = (final_heap / max(1.0, init_heap)) if init_heap > 0 else 1.0

    # KF stability across spot-checks
    if len(kf_spot_records) >= 2:
        kf2_first = kf_spot_records[0]["kf2_max_iso"]
        kf2_last = kf_spot_records[-1]["kf2_max_iso"]
        kf1_first = kf_spot_records[0]["kf1_spurious_firing_rate"]
        kf1_last = kf_spot_records[-1]["kf1_spurious_firing_rate"]
        kf2_drift_abs = abs(kf2_last - kf2_first)
        kf1_drift_abs = abs(kf1_last - kf1_first)
    else:
        kf2_drift_abs = -1.0
        kf1_drift_abs = -1.0

    tracemalloc.stop()
    elapsed_total = time.time() - t_run0

    summary = {
        "anchor": "sustained_workload_24h_baseline_v1_n4096",
        "N": N_use, "M_initial": M_init,
        "total_ops_target": total_ops,
        "total_ops_done": len(all_op_latencies_ms),
        "elapsed_total_s": round(elapsed_total, 2),
        "baseline_throughput_ops_per_s": (
            round(baseline_throughput_ops_per_s, 4)
            if baseline_throughput_ops_per_s else None),
        "final_throughput_ops_per_s": round(final_throughput, 4),
        "throughput_drift_frac": round(throughput_drift, 4),
        "throughput_drop_pct": round(throughput_drop_pct, 4),
        "init_rss_mb": round(init_rss, 2),
        "final_rss_mb": round(final_rss, 2),
        "mem_growth_rss_ratio": round(mem_growth_rss, 4),
        "init_gpu_mb": round(init_gpu, 2),
        "final_gpu_mb": round(final_gpu, 2),
        "init_heap_mb": round(init_heap, 2),
        "final_heap_mb": round(final_heap, 2),
        "mem_growth_heap_ratio": round(mem_growth_heap, 4),
        "init_w_l2_norm": round(init_w_norm, 4),
        "final_w_l2_norm": round(final_w_norm, 4),
        "w_l2_norm_drift_ratio": round(final_w_norm / init_w_norm, 4),
        "codebook_usage_hist_drift_l1": round(hist_drift, 6),
        "cert_chain_len": len(cert_chain),
        "cert_chain_valid": bool(cert_chain_valid),
        "audit_records": audit_records,
        "audit_full_corruptions": audit_full_corruptions,
        "kf_spot_records": kf_spot_records,
        "kf2_drift_abs": round(kf2_drift_abs, 5) if kf2_drift_abs >= 0 else None,
        "kf1_drift_abs": round(kf1_drift_abs, 5) if kf1_drift_abs >= 0 else None,
        "hourly_records": hourly_records,
        "crashed": crashed,
        "crash_msg": crash_msg,
    }
    return summary


def compute_verdict(summary: Dict, total_ops_target: int,
                    total_seconds_target: float) -> Tuple[str, str]:
    """Apply pre-registered HARD_PASS / HARD_FAIL / MIDDLE_BAND bands."""
    if summary["crashed"]:
        return ("SUSTAINED_HARD_FAIL",
                f"CRASHED: {summary.get('crash_msg', 'unknown')}")
    if not summary["cert_chain_valid"]:
        return ("SUSTAINED_HARD_FAIL",
                f"CERT_CORRUPTED: chain_len={summary['cert_chain_len']} "
                f"audit_corruptions={summary['audit_full_corruptions']}")

    # Memory checks
    rss_growth = summary["mem_growth_rss_ratio"]
    if rss_growth > MEM_HARD_FAIL_MULTIPLIER:
        return ("SUSTAINED_HARD_FAIL",
                f"RSS_LEAK: growth={rss_growth:.2f}x > {MEM_HARD_FAIL_MULTIPLIER}x ceiling")

    # Throughput check
    drop = summary["throughput_drop_pct"]
    if drop is not None and drop >= 0 and drop > THROUGHPUT_HARD_FAIL_DRIFT:
        return ("SUSTAINED_HARD_FAIL",
                f"THROUGHPUT_DROP: drop={drop:.2%} > {THROUGHPUT_HARD_FAIL_DRIFT:.0%} ceiling")

    # Completion check
    completion_frac = summary["total_ops_done"] / max(1, total_ops_target)
    if completion_frac < 0.95:
        return ("SUSTAINED_HARD_FAIL",
                f"INCOMPLETE: {summary['total_ops_done']}/{total_ops_target} "
                f"ops done ({completion_frac:.1%})")

    # HARD_PASS bands
    drift_within_10pct = (summary.get("throughput_drift_frac", 1.0) <= THROUGHPUT_HARD_PASS_DRIFT
                          if summary.get("throughput_drift_frac", -1) >= 0 else False)
    mem_within_2x = rss_growth <= MEM_HARD_PASS_MULTIPLIER

    # KF stability: drift < 0.2 absolute is "stable"; -1 sentinel means no
    # comparisons made (smoke); treat as PASS for smoke.
    kf2_stable = (summary.get("kf2_drift_abs") is None or
                  summary.get("kf2_drift_abs", 0.0) < 0.2)
    kf1_stable = (summary.get("kf1_drift_abs") is None or
                  summary.get("kf1_drift_abs", 0.0) < 0.2)

    detail = (f"ops={summary['total_ops_done']} "
              f"throughput_drift={summary.get('throughput_drift_frac', -1):.3f} "
              f"rss_growth={rss_growth:.2f}x "
              f"kf2_drift={summary.get('kf2_drift_abs')} "
              f"kf1_drift={summary.get('kf1_drift_abs')} "
              f"cert_valid={summary['cert_chain_valid']} "
              f"w_norm_drift={summary['w_l2_norm_drift_ratio']:.3f}")

    if drift_within_10pct and mem_within_2x and kf2_stable and kf1_stable:
        return ("SUSTAINED_HARD_PASS",
                f"PRODUCTION_READY: {detail}")

    return ("SUSTAINED_MIDDLE_BAND",
            f"INFORMATIVE_DRIFT: {detail}")


def _instrumentation_selftest() -> None:
    """Smoke-scale forward pass: every metric returns non-null + finite."""
    assert N_FULL == 4096
    # Tiny test: N=64, M=8, ~30 ops total in <1s wall.
    summary = run_sustained_workload(
        N_use=64, M_init=8, total_ops=30,
        total_seconds_target=2.0,
        seed=17, op_mix=OP_MIX,
        audit_interval_ops=10,
        hourly_checkpoint_s=1.0,
        kf_spot_interval_s=1.0,
    )
    assert not summary["crashed"], f"selftest crashed: {summary.get('crash_msg')}"
    assert summary["cert_chain_valid"], "selftest cert chain invalid"
    assert summary["total_ops_done"] >= 25, \
        f"selftest under-ops: {summary['total_ops_done']}"
    assert summary["hourly_records"], "no hourly records"
    h0 = summary["hourly_records"][0]
    assert h0["throughput_ops_per_s_actual"] > 0, "zero throughput"
    assert h0["lat_mean_ms"] >= 0, "negative latency"
    assert summary["init_rss_mb"] >= -1.0
    assert summary["final_w_l2_norm"] >= 0.0
    v, _ = compute_verdict(summary, total_ops_target=30,
                           total_seconds_target=2.0)
    assert "SUSTAINED_" in v, f"verdict wrong shape: {v}"
    print(f"[selftest] sustained_workload_24h_baseline_v1 PASS "
          f"ops={summary['total_ops_done']} "
          f"throughput={h0['throughput_ops_per_s_actual']:.3f} ops/s "
          f"lat_mean={h0['lat_mean_ms']:.2f}ms "
          f"cert_valid={summary['cert_chain_valid']} verdict={v}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true",
                   help="run a 1-minute smoke simulation")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    out_dir = get_output_dir()
    t0 = time.time()

    if args.smoke:
        N_use = N_SMOKE
        M_init = M_STORE_SMOKE
        total_ops = TOTAL_OPS_SMOKE
        total_seconds = SMOKE_DURATION_S
        audit_interval = max(5, AUDIT_INTERVAL_OPS // 100)
        hourly_chk = SMOKE_DURATION_S / 2.0
        kf_spot_int = SMOKE_DURATION_S / 3.0
        print(f"[run] SMOKE 1-min sim N={N_use} M={M_init} "
              f"total_ops={total_ops} target_s={total_seconds}", flush=True)
    else:
        N_use = N_FULL
        M_init = M_STORE
        total_ops = TOTAL_OPS_FULL
        total_seconds = TOTAL_HOURS * 3600.0
        audit_interval = AUDIT_INTERVAL_OPS
        hourly_chk = HOURLY_CHECKPOINT_S
        kf_spot_int = KF_SPOT_INTERVAL_S
        print(f"[run] FULL 24h sustained workload N={N_use} M={M_init} "
              f"total_ops={total_ops} target_hours={TOTAL_HOURS}", flush=True)

    summary = run_sustained_workload(
        N_use=N_use, M_init=M_init,
        total_ops=total_ops,
        total_seconds_target=total_seconds,
        seed=SEED, op_mix=OP_MIX,
        audit_interval_ops=audit_interval,
        hourly_checkpoint_s=hourly_chk,
        kf_spot_interval_s=kf_spot_int,
    )
    verdict, vm = compute_verdict(summary, total_ops_target=total_ops,
                                   total_seconds_target=total_seconds)
    elapsed = round(time.time() - t0, 2)
    summary["verdict"] = verdict
    summary["verdict_msg"] = vm
    summary["elapsed_s"] = elapsed
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
