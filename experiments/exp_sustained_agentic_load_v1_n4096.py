"""G13b PHASE 2 SUSTAINED AGENTIC LOAD v1 at N=4096.

CONTEXT (G13b_p2, user revision):
  Phase 2: 10 concurrent agentic sessions of mixed types, sustained for
  2-4 hours. Reuses agentic workload definitions from G13b_p1.

WORKLOAD:
  10 concurrent sessions (round-robin interleaved):
    3 Customer Support (A) + 4 Compliance (B) + 3 Diagnostic (C).
  Sustained 2.5h wall target.
  Realistic edits interspersed at 50 edits/hour total: 50% legitimate
  updates + 50% GDPR-deletion-style operations.

CONCURRENCY MODEL:
  Single-process round-robin "agent step" loop. Each tick, advance ONE
  session's next call by ~1 step. We do NOT use python threading on a
  shared GPU; this gives equivalent interleaving without OOM/race risk.

INSTRUMENTATION:
  Per-session: same as G13b_p1 (latencies p50/p95/p99, accuracy, KF stable).
  System-wide: ops/sec throughput, peak memory growth multiplier,
  audit chain integrity at 30-min checkpoints.

PRE-REGISTERED BANDS:
  HARD_PASS = all 10 sessions complete (or run 2.5h without crash) AND
              ops/sec within 20% of initial AND audit chain 100% integrity
              AND no memory growth > 2x initial.
  HARD_FAIL = any session crashes (OOM, unhandled exception) OR audit chain
              corrupts OR throughput drops > 50%.
  MIDDLE_BAND = otherwise.

OOM CHECK:
  N=4096, M=8192 (shared single substrate across sessions):
    facts: 8192 * 4096 * 4 * 2 = 256 MiB
    W:     4096^2 * 4           =  64 MiB
    CB:    4*4096 * 4096 * 4    = 256 MiB
  Sessions share substrate state -> ~600 MiB total. OK on 8 GiB GPU.

TIMEOUT ESTIMATE:
  Target wall 2.5h sustained. Buffer 1h. Setup 15 min. Budget: 14400s (4h).

PROT-018: _n4096 binds N = 4096.
PROT-020: torch+cuda.
PROT-021: per-session checkpoint.

Anchor: sustained_agentic_load_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_sustained_agentic_load_v1_n4096.md
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
    build_shared, path_d_run,
)
from experiments._metric_battery import (  # noqa: E402
    metric_retention, metric_max_iso,
)
from experiments._workload_harness import (  # noqa: E402
    make_cert, verify_cert_chain,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g13b2", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096.
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096

M_FULL  = 8192
M_SMOKE = 256

K_PATHS = 500
K_PATHS_SMOKE = 30

# Per-session config (matches G13b_p1)
WORKLOAD_CFG = {
    "A_customer_support":   {"d_min": 1, "d_max": 5,  "calls_per_hour": 130},
    "B_compliance":         {"d_min": 3, "d_max": 8,  "calls_per_hour":  95},
    "C_diagnostic":         {"d_min": 5, "d_max": 15, "calls_per_hour": 120},
}

# 10 sessions: 3A + 4B + 3C
SESSIONS_FULL = (
    [("A_customer_support", i) for i in range(3)] +
    [("B_compliance",       i) for i in range(4)] +
    [("C_diagnostic",       i) for i in range(3)]
)
SESSIONS_SMOKE = (
    [("A_customer_support", 0)] +
    [("B_compliance",       0)] +
    [("C_diagnostic",       0)]
)

TARGET_WALL_S_FULL  = 9000      # 2.5h
TARGET_WALL_S_SMOKE = 60        # 1 min smoke

EDITS_PER_HOUR_FULL  = 50
EDITS_PER_HOUR_SMOKE = 5

CHECKPOINT_EVERY_S_FULL  = 1800  # 30 min
CHECKPOINT_EVERY_S_SMOKE = 30

INTER_TICK_SLEEP_S_FULL  = 0.05  # 50 ms baseline gap between any-session ticks
INTER_TICK_SLEEP_S_SMOKE = 0.0

# Pre-reg thresholds
HP_THROUGHPUT_DELTA = 0.20    # within +/-20% of initial
HP_MEM_GROWTH_MAX = 2.0
HF_THROUGHPUT_DROP = 0.50     # > 50% drop is HF


def get_output_dir(default_name: str = "sustained_agentic_load_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _make_session_state(name: str, seed: int):
    """Return mutable session state dict."""
    return {
        "name": name,
        "seed": int(seed),
        "n_calls_done": 0,
        "n_correct": 0,
        "n_calls_acc": 0,
        "latencies_ms": [],
    }


def _do_one_call(session, codebook, W, relation, N_use, K, device):
    cfg = WORKLOAD_CFG[session["name"]]
    seed = session["seed"] + session["n_calls_done"]
    gen = torch.Generator(device="cpu").manual_seed(seed)
    depth = int(torch.randint(cfg["d_min"], cfg["d_max"] + 1, (1,),
                                generator=gen).item())
    keys_list = list(relation.keys())
    if not keys_list:
        return 0.0, 0
    start_id = keys_list[seed % len(keys_list)]
    starts = torch.tensor([start_id], dtype=torch.long, device=device)

    if device.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.perf_counter()
    correct = path_d_run(codebook, W, starts, relation, depth, K, seed, N_use)
    if device.type == "cuda":
        torch.cuda.synchronize()
    dt_ms = (time.perf_counter() - t0) * 1000.0

    session["latencies_ms"].append(dt_ms)
    session["n_calls_done"] += 1
    session["n_calls_acc"] += 1
    session["n_correct"] += int(correct.sum().item())
    return dt_ms, int(correct.sum().item())


def _do_edit_or_delete(codebook, W, key_idx, val_idx, N_use, gen,
                        cert_chain, prev_hash, op_counter, do_delete: bool,
                        device):
    """Edit (rank-1 swap) or Delete (rank-1 retract) on shared W. Return new W, hash, op_counter, success."""
    if key_idx.shape[0] == 0:
        return W, prev_hash, op_counter, False
    pos = int(torch.randint(0, key_idx.shape[0], (1,), generator=gen).item())
    old_key = codebook[key_idx[pos] % codebook.shape[0]]
    old_val = codebook[val_idx[pos] % codebook.shape[0]]
    if do_delete:
        # GDPR-style delete: subtract old contribution
        W = W - torch.outer(old_val, old_key) / N_use
        op = "delete"
        new_val_i = -1
    else:
        # Legitimate edit: rank-1 swap to a new value
        new_val_i = int(torch.randint(0, codebook.shape[0], (1,), generator=gen).item())
        new_val = codebook[new_val_i]
        W = W + torch.outer(new_val - old_val, old_key) / N_use
        op = "edit"
    link = make_cert(prev_hash, op=op, fact_id=pos,
                      key_id=int(key_idx[pos].item()),
                      val_id=new_val_i, op_id=op_counter)
    cert_chain.append(link)
    prev_hash = link["this_hash"]
    op_counter += 1
    return W, prev_hash, op_counter, True


def _percentiles(xs: List[float]) -> Tuple[float, float, float, float]:
    if not xs:
        return 0.0, 0.0, 0.0, 0.0
    s = sorted(xs)
    nn = len(s)
    def pct(p):
        i = min(nn - 1, max(0, int(p * nn) - 1))
        return float(s[i])
    return (float(sum(s) / nn), pct(0.50), pct(0.95), pct(0.99))


def _peak_mem_bytes(device: torch.device) -> int:
    if device.type == "cuda":
        return int(torch.cuda.max_memory_allocated(device))
    return 0


def run_sustained(N_use: int, M: int, sessions_def: List[Tuple[str, int]],
                   K: int, target_wall_s: float,
                   edits_per_hour: float, checkpoint_every_s: float,
                   inter_tick_sleep_s: float,
                   device: torch.device) -> Dict:
    """Run sustained interleaved sessions, return full metrics dict."""
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, 17, device)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    mem_initial = _peak_mem_bytes(device)

    sessions = []
    for name, i in sessions_def:
        sessions.append(_make_session_state(name, seed=17 + i * 100
                                              + hash(name) % 1000))

    cert_chain: List[Dict] = []
    prev_hash = "GENESIS"
    op_counter = 0

    sess_start = time.time()
    next_checkpoint = sess_start + checkpoint_every_s
    next_edit_at = sess_start + (3600.0 / max(1.0, edits_per_hour))
    edit_gen = torch.Generator(device="cpu").manual_seed(42)

    initial_window_ops = 0
    initial_window_t   = 60.0  # measure first 60s for throughput baseline
    initial_window_done = False
    initial_throughput = 0.0
    final_throughput = 0.0
    final_window_ops = 0
    final_window_start = 0.0

    checkpoint_chain_ok = []
    chain_break = False
    crash = False

    si = 0
    while True:
        now = time.time()
        elapsed = now - sess_start
        if elapsed >= target_wall_s:
            break

        sess = sessions[si % len(sessions)]
        si += 1

        # Throughput measurement window
        if not initial_window_done and elapsed >= initial_window_t:
            initial_throughput = initial_window_ops / max(0.001, initial_window_t)
            initial_window_done = True
            final_window_start = elapsed
            final_window_ops = 0

        # One call for this session
        try:
            dt_ms, _ = _do_one_call(sess, codebook, W, relation, N_use, K, device)
            if not initial_window_done:
                initial_window_ops += 1
            else:
                final_window_ops += 1
        except (RuntimeError, MemoryError) as e:
            crash = True
            print(f"  CRASH session={sess['name']}: {e}", flush=True)
            break

        # Cert link for query
        link = make_cert(prev_hash, op="query", fact_id=-1, key_id=-1,
                          val_id=-1, op_id=op_counter)
        cert_chain.append(link)
        prev_hash = link["this_hash"]
        op_counter += 1

        # Edit/delete at scheduled interval
        if now >= next_edit_at:
            do_delete = (float(torch.rand(1, generator=edit_gen).item()) < 0.5)
            try:
                W, prev_hash, op_counter, ok = _do_edit_or_delete(
                    codebook, W, key_idx, val_idx, N_use, edit_gen,
                    cert_chain, prev_hash, op_counter, do_delete, device)
            except (RuntimeError, MemoryError) as e:
                crash = True
                print(f"  CRASH edit op: {e}", flush=True)
                break
            next_edit_at = now + (3600.0 / max(1.0, edits_per_hour))

        # Checkpoint
        if now >= next_checkpoint:
            chain_ok = verify_cert_chain(cert_chain)
            checkpoint_chain_ok.append(bool(chain_ok))
            if not chain_ok:
                chain_break = True
                print(f"  CHAIN_BREAK at t={elapsed:.0f}s", flush=True)
                break
            print(f"  [checkpoint] t={elapsed:.0f}s ops={op_counter} "
                  f"chain_ok={chain_ok}", flush=True)
            next_checkpoint = now + checkpoint_every_s

        if inter_tick_sleep_s > 0:
            time.sleep(inter_tick_sleep_s)

    total_wall_s = time.time() - sess_start
    # Final throughput window (last segment after initial_window)
    final_elapsed = max(0.001, total_wall_s - initial_window_t) if initial_window_done else total_wall_s
    final_throughput = final_window_ops / final_elapsed if final_elapsed > 0 else 0.0

    # Final audit chain check
    final_chain_ok = verify_cert_chain(cert_chain)
    if not final_chain_ok:
        chain_break = True

    # Per-session metrics
    per_session = []
    for s in sessions:
        mean_ms, p50, p95, p99 = _percentiles(s["latencies_ms"])
        acc = (s["n_correct"] / s["n_calls_acc"]) if s["n_calls_acc"] > 0 else 0.0
        per_session.append({
            "name": s["name"], "seed": s["seed"],
            "n_calls_done": s["n_calls_done"],
            "session_acc": round(acc, 5),
            "per_call_mean_ms": round(mean_ms, 3),
            "per_call_p50_ms": round(p50, 3),
            "per_call_p95_ms": round(p95, 3),
            "per_call_p99_ms": round(p99, 3),
        })

    # KF stability at end
    ret = metric_retention(W, codebook, key_idx, val_idx, N_use,
                            beta=8.0, seed=17, device=device,
                            n_probe=min(50, key_idx.shape[0]))
    iso = metric_max_iso(W, codebook, key_idx, val_idx, N_use,
                          beta=8.0, seed=17, device=device,
                          n_probe=min(50, key_idx.shape[0]),
                          n_edits=min(8, max(1, key_idx.shape[0] - 50)))

    mem_final = _peak_mem_bytes(device)
    mem_ratio = (mem_final / max(1, mem_initial)) if mem_initial > 0 else 1.0

    if device.type == "cuda":
        torch.cuda.empty_cache()
    del codebook, W

    return {
        "total_wall_s": round(total_wall_s, 2),
        "n_sessions": len(sessions),
        "per_session": per_session,
        "total_ops": int(op_counter),
        "initial_throughput_ops_s": round(initial_throughput, 4),
        "final_throughput_ops_s":   round(final_throughput, 4),
        "throughput_drop_frac":     round(
            (initial_throughput - final_throughput) / max(0.001, initial_throughput)
            if initial_throughput > 0 else 0.0, 5),
        "cert_chain_len":     int(len(cert_chain)),
        "audit_chain_ok":     bool(final_chain_ok),
        "checkpoint_chain_ok": checkpoint_chain_ok,
        "chain_break":        bool(chain_break),
        "retention_end":      float(ret["retention"]),
        "max_iso_end":        float(iso["max_iso"]),
        "mem_initial_b":      int(mem_initial),
        "mem_final_b":        int(mem_final),
        "mem_growth_ratio":   round(mem_ratio, 4),
        "crash":              bool(crash),
    }


def compute_verdict(metrics: Dict) -> Tuple[str, str]:
    detail = (f"sessions_done={metrics['n_sessions']} "
              f"ops={metrics['total_ops']} "
              f"wall={metrics['total_wall_s']:.0f}s "
              f"init_tp={metrics['initial_throughput_ops_s']:.2f} "
              f"final_tp={metrics['final_throughput_ops_s']:.2f} "
              f"drop={metrics['throughput_drop_frac']:.3f} "
              f"chain_ok={metrics['audit_chain_ok']} "
              f"mem_ratio={metrics['mem_growth_ratio']:.2f}")

    if metrics["crash"]:
        return ("G13B_P2_HARD_FAIL", f"CRASH: {detail}")
    if metrics["chain_break"]:
        return ("G13B_P2_HARD_FAIL", f"CHAIN_CORRUPT: {detail}")
    if metrics["throughput_drop_frac"] > HF_THROUGHPUT_DROP:
        return ("G13B_P2_HARD_FAIL", f"THROUGHPUT_COLLAPSE: {detail}")

    tp_within_20 = abs(metrics["throughput_drop_frac"]) <= HP_THROUGHPUT_DELTA
    chain_ok = metrics["audit_chain_ok"]
    mem_ok = metrics["mem_growth_ratio"] <= HP_MEM_GROWTH_MAX

    if tp_within_20 and chain_ok and mem_ok:
        return ("G13B_P2_HARD_PASS", f"SUSTAINED_OK: {detail}")
    return ("G13B_P2_MIDDLE_BAND", f"PARTIAL: {detail}")


def _instrumentation_selftest() -> None:
    """Brief sustained run at smoke scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096, got {N_FULL}"
    device = torch.device("cpu")
    sessions_def = [("A_customer_support", 0), ("B_compliance", 0), ("C_diagnostic", 0)]
    # Kerdock 4-coset requires N in {1024, 4096, 16384}
    m = run_sustained(N_use=1024, M=64, sessions_def=sessions_def, K=20,
                       target_wall_s=10.0, edits_per_hour=300.0,
                       checkpoint_every_s=4.0, inter_tick_sleep_s=0.0,
                       device=device)
    assert m["total_ops"] > 0, "no ops executed in 10s smoke"
    assert m["audit_chain_ok"] is True, "audit chain invalid at smoke"
    assert m["cert_chain_len"] >= 1, "cert chain empty"
    print(f"[selftest] sustained_agentic_load_v1_n4096 PASS "
          f"ops={m['total_ops']} chain={m['audit_chain_ok']} "
          f"init_tp={m['initial_throughput_ops_s']:.2f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_cfg = M_SMOKE if smoke else M_FULL
    K_cfg = K_PATHS_SMOKE if smoke else K_PATHS
    sessions_def = SESSIONS_SMOKE if smoke else SESSIONS_FULL
    target_wall = TARGET_WALL_S_SMOKE if smoke else TARGET_WALL_S_FULL
    edits_ph    = EDITS_PER_HOUR_SMOKE if smoke else EDITS_PER_HOUR_FULL
    chkpt_every = CHECKPOINT_EVERY_S_SMOKE if smoke else CHECKPOINT_EVERY_S_FULL
    tick_sleep  = INTER_TICK_SLEEP_S_SMOKE if smoke else INTER_TICK_SLEEP_S_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] sustained_agentic smoke={smoke} N={N_cfg} M={M_cfg} K={K_cfg} "
          f"sessions={len(sessions_def)} target_wall={target_wall:.0f}s "
          f"edits/h={edits_ph} chkpt_every={chkpt_every}s "
          f"device={device.type}", flush=True)

    ck = "run0"
    if ck in done:
        body = load_partial_key(out_dir, ck)
        if body is not None:
            metrics = body
            print(f"  [resumed from checkpoint]", flush=True)
        else:
            metrics = run_sustained(N_cfg, M_cfg, sessions_def, K_cfg,
                                     target_wall, edits_ph, chkpt_every,
                                     tick_sleep, device)
            write_partial_key(out_dir, ck, metrics)
    else:
        metrics = run_sustained(N_cfg, M_cfg, sessions_def, K_cfg,
                                 target_wall, edits_ph, chkpt_every,
                                 tick_sleep, device)
        write_partial_key(out_dir, ck, metrics)

    verdict, vm = compute_verdict(metrics)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "sustained_agentic_load_v1_n4096",
        "N": N_cfg, "smoke": smoke, "M": M_cfg, "K_paths": K_cfg,
        "sessions_def": [list(s) for s in sessions_def],
        "target_wall_s": target_wall,
        "edits_per_hour": edits_ph,
        "checkpoint_every_s": chkpt_every,
        "metrics": metrics,
        "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
