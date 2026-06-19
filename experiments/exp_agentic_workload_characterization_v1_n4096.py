"""G13b PHASE 1 AGENTIC WORKLOAD CHARACTERIZATION v1 at N=4096.

CONTEXT (G13b_p1, user revision of original G13):
  Realistic agentic patterns matter MORE for product positioning than
  depth-500 extrapolation. Simulate 3 agentic workload types and report
  per-call latency, accuracy, audit trail completeness, killer feature
  stability at session end.

WORKLOADS (5 sessions each = 15 sessions total):
  Workload A "Customer Support":      15 calls/sess, depths 1-5 (mostly 1-3),
                                       retrieves + occasional edits, ~7 min wall
  Workload B "Compliance Reasoning":  35 calls/sess, depths 3-8,
                                       read-heavy + audit verification, ~22 min
  Workload C "Diagnostic":            65 calls/sess, depths 5-15,
                                       retrieves + confidence-aware queries, ~32 min

  Between-call delays (0.5-2s) MODEL LLM reasoning between substrate calls.
  We accelerate these for FULL run (scaled by inter_call_scale) to fit timeout.

SETUP:
  N=4096, BSC, M=8192 (production operating point).
  Path D mechanism for multi-hop calls.

METRICS (per session):
  per-call latency p50/p95/p99 (ms), per-call accuracy, total session wall,
  session-level mean accuracy, audit-trail completeness (cert chain valid 100%),
  killer feature stability checkpoint at session end:
    KF stable iff retention >= 0.90 AND KF-2 max_iso <= 0.05 at session end.
  Aggregated across 5 sessions per workload.

PRE-REGISTERED BANDS:
  HARD_PASS = all 3 workloads complete AND per-call p99 <= 200 ms AND
              session-level accuracy >= 0.90 AND killer features stable
              at session end in >= 4/5 sessions per workload.
  HARD_FAIL = any workload's session times out OR session-level accuracy
              < 0.50 OR killer features degrade (in >= 4/5 sessions per workload).
  MIDDLE_BAND = otherwise.

NOTE: Simulated between-call sleep delays model LLM reasoning. We use
INTER_CALL_SCALE to compress these for timed runs (still preserve ordering).

OOM CHECK:
  N=4096, M=8192: 256 MiB facts + 64 MiB W + 256 MiB codebook < 1 GiB.
  Path D K_paths=500, max depth=15: 500*15=7500 hops/query ~ 120 MiB. OK on 8 GiB GPU.

TIMEOUT ESTIMATE:
  Sessions sequential. FULL: 15 sessions x avg ~12 min compressed wall = ~3h.
  With INTER_CALL_SCALE=0.1 (10x compression): ~18 min net.
  Plus 15 * (build_shared at N=4096) overhead ~2 min.
  Budget: 21600s (6h, well-padded).
  Per-experiment formula: smoke_wall ~ 30s, FULL/smoke seeds 5, sess 15,
  ceil(1.5 * 30 * (4)^1.5 * (15/3)) = ceil(1800) = 1800s,
  but inter-call delays dominate -> set 21600s for safety.

PROT-018: _n4096 binds N = 4096.
PROT-020: torch+cuda.
PROT-021: per-session checkpoint.

Anchor: agentic_workload_characterization_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_agentic_workload_characterization_v1_n4096.md
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
from experiments._metric_battery import (  # noqa: E402
    metric_retention, metric_max_iso,
)
from experiments._workload_harness import (  # noqa: E402
    make_cert, verify_cert_chain,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g13b1", _ck_path)
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

M_FULL  = 8192          # production
M_SMOKE = 256

K_PATHS = 500
K_PATHS_SMOKE = 30

# Three workload archetypes (calls_per_session, depth_min, depth_max, edit_frac)
WORKLOADS_FULL = {
    "A_customer_support":   {"calls": 15, "d_min": 1, "d_max": 5,  "edit_frac": 0.15},
    "B_compliance":         {"calls": 35, "d_min": 3, "d_max": 8,  "edit_frac": 0.05},
    "C_diagnostic":         {"calls": 65, "d_min": 5, "d_max": 15, "edit_frac": 0.05},
}

WORKLOADS_SMOKE = {
    "A_customer_support":   {"calls": 4, "d_min": 1, "d_max": 3, "edit_frac": 0.0},
    "B_compliance":         {"calls": 5, "d_min": 2, "d_max": 4, "edit_frac": 0.0},
    "C_diagnostic":         {"calls": 6, "d_min": 3, "d_max": 5, "edit_frac": 0.0},
}

SESSIONS_PER_WORKLOAD_FULL = 5
SESSIONS_PER_WORKLOAD_SMOKE = 1

# Inter-call delay scale factor (model LLM reasoning between substrate calls)
INTER_CALL_SCALE_FULL = 0.10    # 10x compression of 0.5-2s -> 0.05-0.2s
INTER_CALL_SCALE_SMOKE = 0.0    # no delay in smoke

# Pre-reg thresholds
HP_P99_MS = 200.0
HP_ACC = 0.90
HP_KF_SESSIONS_MIN = 4
KF_RET_MIN = 0.90
KF_ISO_MAX = 0.05
HF_ACC = 0.50


def get_output_dir(default_name: str = "agentic_workload_characterization_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _do_one_call(codebook: torch.Tensor, W: torch.Tensor, relation: Dict[int, int],
                  depth: int, K: int, seed: int, N_use: int,
                  device: torch.device) -> Tuple[float, int]:
    """One agentic substrate call. Returns (latency_ms, correct_flag 0/1)."""
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
    return dt_ms, int(correct.sum().item())


def _run_one_session(N_use: int, M: int, workload: Dict, K: int,
                      seed: int, session_id: int,
                      inter_call_scale: float,
                      device: torch.device) -> Dict:
    """Run one workload session and return aggregated metrics."""
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)

    gen = torch.Generator(device="cpu").manual_seed(seed + session_id * 1000)
    n_calls = int(workload["calls"])
    d_min = int(workload["d_min"])
    d_max = int(workload["d_max"])
    edit_frac = float(workload["edit_frac"])

    latencies_ms: List[float] = []
    n_correct = 0
    n_calls_acc = 0
    cert_chain: List[Dict] = []
    prev_hash = "GENESIS"
    op_counter = 0

    sess_start = time.time()
    for call_i in range(n_calls):
        # Decide: query or edit?
        u = float(torch.rand(1, generator=gen).item())
        is_edit = (u < edit_frac)

        depth = int(torch.randint(d_min, d_max + 1, (1,), generator=gen).item())

        # Sleep between calls (model LLM reasoning)
        if call_i > 0 and inter_call_scale > 0.0:
            sleep_s = float(torch.empty(1).uniform_(0.5, 2.0, generator=gen).item())
            time.sleep(sleep_s * inter_call_scale)

        if is_edit:
            # Edit op: pick a random fact, rank-1 swap on W
            if key_idx.shape[0] == 0:
                continue
            ed_pos = int(torch.randint(0, key_idx.shape[0], (1,), generator=gen).item())
            new_val_i = int(torch.randint(0, codebook.shape[0], (1,), generator=gen).item())
            t0 = time.perf_counter()
            old_key = codebook[key_idx[ed_pos] % codebook.shape[0]]
            old_val = codebook[val_idx[ed_pos] % codebook.shape[0]]
            new_val = codebook[new_val_i]
            W = W + torch.outer(new_val - old_val, old_key) / N_use
            if device.type == "cuda":
                torch.cuda.synchronize()
            dt_ms = (time.perf_counter() - t0) * 1000.0
            latencies_ms.append(dt_ms)

            # Audit cert link
            link = make_cert(prev_hash, op="edit", fact_id=ed_pos,
                              key_id=int(key_idx[ed_pos].item()),
                              val_id=new_val_i, op_id=op_counter)
            cert_chain.append(link)
            prev_hash = link["this_hash"]
            op_counter += 1
        else:
            # Multi-hop query
            dt_ms, ok = _do_one_call(codebook, W, relation, depth, K,
                                       seed + call_i, N_use, device)
            latencies_ms.append(dt_ms)
            n_correct += ok
            n_calls_acc += 1

            # Audit cert link
            link = make_cert(prev_hash, op="query", fact_id=-1,
                              key_id=-1, val_id=-1, op_id=op_counter)
            cert_chain.append(link)
            prev_hash = link["this_hash"]
            op_counter += 1

    session_wall_s = time.time() - sess_start

    # Killer-feature checkpoint at session end
    ret = metric_retention(W, codebook, key_idx, val_idx, N_use,
                            beta=8.0, seed=seed, device=device,
                            n_probe=min(50, key_idx.shape[0]))
    iso = metric_max_iso(W, codebook, key_idx, val_idx, N_use,
                          beta=8.0, seed=seed, device=device,
                          n_probe=min(50, key_idx.shape[0]),
                          n_edits=min(8, max(1, key_idx.shape[0] - 50)))
    kf_stable = bool(ret["retention"] >= KF_RET_MIN and iso["max_iso"] <= KF_ISO_MAX)

    # Audit chain integrity
    chain_ok = verify_cert_chain(cert_chain)

    # Percentiles
    lat_sorted = sorted(latencies_ms)
    nn = len(lat_sorted)
    def pct(p):
        if nn == 0: return 0.0
        i = min(nn - 1, max(0, int(p * nn) - 1))
        return float(lat_sorted[i])
    p50 = pct(0.50); p95 = pct(0.95); p99 = pct(0.99)
    mean_lat = float(sum(latencies_ms) / nn) if nn else 0.0

    sess_acc = (n_correct / n_calls_acc) if n_calls_acc > 0 else 0.0

    if device.type == "cuda":
        torch.cuda.empty_cache()
    del codebook, W

    return {
        "session_id": int(session_id),
        "n_calls": int(n_calls),
        "n_calls_acc": int(n_calls_acc),
        "session_acc": round(sess_acc, 5),
        "session_wall_s": round(session_wall_s, 2),
        "per_call_mean_ms": round(mean_lat, 3),
        "per_call_p50_ms":  round(p50, 3),
        "per_call_p95_ms":  round(p95, 3),
        "per_call_p99_ms":  round(p99, 3),
        "retention_end":    float(ret["retention"]),
        "max_iso_end":      float(iso["max_iso"]),
        "kf_stable":        bool(kf_stable),
        "audit_chain_ok":   bool(chain_ok),
        "cert_chain_len":   int(len(cert_chain)),
    }


def compute_verdict(cells: List[Dict],
                     workloads: Dict) -> Tuple[str, str]:
    if not cells:
        return ("G13B_P1_INCONCLUSIVE", "no cells")

    # group by workload_name
    by_wl: Dict[str, List[Dict]] = {wl: [] for wl in workloads}
    for c in cells:
        wl = c.get("workload_name", "")
        if wl in by_wl:
            by_wl[wl].append(c)

    hp_all = True
    hf_any = False
    summary_parts = []

    for wl in workloads:
        sess = by_wl.get(wl, [])
        if not sess:
            hp_all = False
            summary_parts.append(f"{wl}=NO_DATA")
            continue
        p99s   = [s["per_call_p99_ms"] for s in sess]
        accs   = [s["session_acc"] for s in sess]
        kfs    = [int(s["kf_stable"]) for s in sess]
        chains = [int(s["audit_chain_ok"]) for s in sess]

        n_kf_stable = sum(kfs)
        all_chains_ok = all(c == 1 for c in chains)
        mean_p99 = sum(p99s) / len(p99s)
        mean_acc = sum(accs) / len(accs)

        summary_parts.append(
            f"{wl}: n={len(sess)} acc_mean={mean_acc:.3f} p99_ms={mean_p99:.1f} "
            f"kf={n_kf_stable}/{len(sess)} chain_ok={int(all_chains_ok)}"
        )

        wl_hp = (mean_p99 <= HP_P99_MS and mean_acc >= HP_ACC
                  and n_kf_stable >= HP_KF_SESSIONS_MIN
                  and all_chains_ok)
        if not wl_hp:
            hp_all = False
        # HF: in >=4/5 sessions per workload, acc < 0.50 OR KF degrades
        n_acc_fail = sum(1 for a in accs if a < HF_ACC)
        n_kf_fail  = len(sess) - n_kf_stable
        if n_acc_fail >= HP_KF_SESSIONS_MIN or n_kf_fail >= HP_KF_SESSIONS_MIN:
            hf_any = True

    detail = "; ".join(summary_parts)
    if hf_any:
        return ("G13B_P1_HARD_FAIL", f"AGENTIC_FAIL: {detail}")
    if hp_all:
        return ("G13B_P1_HARD_PASS", f"AGENTIC_OK: {detail}")
    return ("G13B_P1_MIDDLE_BAND", f"PARTIAL: {detail}")


def _instrumentation_selftest() -> None:
    """Assert metrics non-null + audit chain at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096, got {N_FULL}"
    device = torch.device("cpu")
    # Kerdock 4-coset requires N in {1024, 4096, 16384}
    out = _run_one_session(
        N_use=1024, M=64,
        workload={"calls": 4, "d_min": 1, "d_max": 2, "edit_frac": 0.25},
        K=20, seed=17, session_id=0,
        inter_call_scale=0.0, device=device)
    assert out["per_call_mean_ms"] > 0.0, "per_call_mean_ms not measured"
    assert out["cert_chain_len"] >= 1, "cert chain empty"
    assert out["audit_chain_ok"] is True, "audit chain selftest invalid"
    assert isinstance(out["kf_stable"], bool), "kf_stable type wrong"
    # multi-scale check at N=4096 production (still small M to stay fast)
    out2 = _run_one_session(
        N_use=4096, M=64,
        workload={"calls": 3, "d_min": 1, "d_max": 2, "edit_frac": 0.2},
        K=20, seed=17, session_id=1,
        inter_call_scale=0.0, device=device)
    assert out2["per_call_p50_ms"] > 0.0
    print(f"[selftest] agentic_workload_characterization_v1_n4096 PASS "
          f"sess_acc={out['session_acc']:.3f} p99={out['per_call_p99_ms']:.1f}ms",
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

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_cfg = 256    if smoke else M_FULL
    K_cfg = K_PATHS_SMOKE if smoke else K_PATHS
    workloads = WORKLOADS_SMOKE if smoke else WORKLOADS_FULL
    sessions_per = SESSIONS_PER_WORKLOAD_SMOKE if smoke else SESSIONS_PER_WORKLOAD_FULL
    inter_scale = INTER_CALL_SCALE_SMOKE if smoke else INTER_CALL_SCALE_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] agentic_workload smoke={smoke} N={N_cfg} M={M_cfg} K={K_cfg} "
          f"workloads={list(workloads.keys())} sessions={sessions_per} "
          f"inter_scale={inter_scale} device={device.type} done={len(done)}",
          flush=True)

    cells: List[Dict] = []
    for wl_name, wl_def in workloads.items():
        for s_i in range(sessions_per):
            ck = f"{wl_name}_sess{s_i}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    body["workload_name"] = wl_name
                    cells.append(body)
                    continue
            try:
                seed = 17 + s_i * 100
                out = _run_one_session(N_cfg, M_cfg, wl_def, K_cfg,
                                        seed, s_i, inter_scale, device)
                out["workload_name"] = wl_name
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  {wl_name} sess{s_i} acc={out['session_acc']:.3f} "
                      f"p99={out['per_call_p99_ms']:.1f}ms "
                      f"kf={out['kf_stable']} chain={out['audit_chain_ok']} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  {wl_name} sess{s_i} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells, workloads)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "agentic_workload_characterization_v1_n4096",
        "N": N_cfg, "smoke": smoke, "M": M_cfg, "K_paths": K_cfg,
        "workloads": {k: v for k, v in workloads.items()},
        "sessions_per_workload": sessions_per,
        "cells": cells, "verdict": verdict, "verdict_msg": vm,
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
