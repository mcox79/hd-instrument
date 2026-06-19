"""
exp_subs_naive_scan_cpu_cost_v1 -- reactive-subscriptions anchor 1 (CHEAP DECISIVE) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_reactive_subscriptions. The API-design drill claimed 1000 subs + 100
  writes/sec = 10%% CPU; the scaling drill REFUTES this (13.1 GFLOP/s required vs ~10 GFLOP/s practical -> saturates a core).
  This measures the truth: naive linear scan over S=1000 subscription vectors at N=65536, per write event; report the core
  utilization implied at write_rate=100/sec. Gates the v1 subscription S-limit doc. CPU $0.
PRE-REGISTERED (research bands): HARD-PASS core utilization >= 90%% at S=1000 (confirms model; scan saturates a core).
  MID 40-90%% (SIMD helping). HARD-FAIL < 20%% (model wrong by >6x; prior claim ~right).
FORMULA SELF-TESTS (PROT-022): 1. flop count. 2. scan correctness. 3. timing positive.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "subs_naive_scan_cpu_cost_v1"
N = 65536; WRITE_RATE = 100
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    S_GRID = [1000]; N_WRITES = 30
else:
    S_GRID = [200, 500, 1000, 2000]; N_WRITES = 200


def scan_time(S, n, n_writes, seed):
    g = np.random.default_rng(seed); subs = g.standard_normal((S, n)).astype(np.float32); writes = g.standard_normal((n_writes, n)).astype(np.float32)
    t0 = time.perf_counter()
    for w in writes:
        _ = subs @ w                                                # naive scan: S dot products per write event
    dt = time.perf_counter() - t0
    return dt / n_writes                                            # seconds per write event


def _selftest():
    g = np.random.default_rng(0); subs = g.standard_normal((4, 8)).astype(np.float32); w = g.standard_normal(8).astype(np.float32)
    assert np.allclose(subs @ w, np.array([subs[i] @ w for i in range(4)]), atol=1e-4), "scan correctness"
    assert scan_time(4, 8, 3, 0) > 0, "timing positive"
    assert 2 * 1000 * 65536 == 131072000, "flop count"
    print("[selftest] PASS: subs-naive-scan", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    by = {}
    for S in S_GRID:
        spw = scan_time(S, N, N_WRITES, 7)                          # sec per write event
        core_util = spw * WRITE_RATE                                # core-seconds consumed per wall-second at WRITE_RATE
        gflops = (S * N * 2) / spw / 1e9
        by["S%d" % S] = {"sec_per_write": spw, "core_util_at_100hz": core_util, "gflops": gflops}
        print("  [S=%d] sec/write=%.5f core_util@100Hz=%.2f achieved=%.1f GFLOP/s" % (S, spw, core_util, gflops), flush=True)
    return {"by": by}


def verdict(r) -> Tuple[str, str]:
    u = r["by"]["S1000"]["core_util_at_100hz"]; gf = r["by"]["S1000"]["gflops"]
    summary = "at S=1000,N=65536,100writes/sec: core_util=%.2f (%.0f%%) achieved=%.1f GFLOP/s | curve: %s" % (
        u, u * 100, gf, {k: round(v["core_util_at_100hz"], 2) for k, v in r["by"].items()})
    if u >= 0.90:
        return ("HARD_PASS", "HARD_PASS: naive scan saturates a core (>=90%%) at S=1000 -- scaling-drill model confirmed; document S_limit conservatively. " + summary)
    if u >= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 20-90%% core util -- SIMD efficiency partially helps; S_limit shifts right. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: <20%% core util -- model wrong by >5x; prior 10%%-CPU claim was approximately right. " + summary)


print("[config] anchor=%s mode=%s S_grid=%s N=%d write_rate=%d" % (ANCHOR_NAME, RUN_MODE, S_GRID, N, WRITE_RATE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
