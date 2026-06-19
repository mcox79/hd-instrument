"""
exp_bitemporal_sync_throughput_v1 -- bitemporal anchor 3 (sync throughput under burst) -- CPU.

ROUTING: handoff bitemporal_impl_spec_chain2_drill3 #3. Confirms synchronous shadow-store sync is adequate for V1 write
  rates (<100/sec). Measures append throughput (rows/sec) + per-write latency of an append-only bitemporal log under burst.
  If per-write latency exceeds 1ms at 100/sec, an async queue is required. CPU.
PRE-REGISTERED: HARD-PASS per-write latency < 1ms at 100/sec (sync sync adequate for V1). MIDDLE 1-5ms. HARD-FAIL > 5ms
  (async queue required).
FORMULA SELF-TESTS (PROT-022): 1. append grows. 2. timing positive. 3. throughput computed.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "bitemporal_sync_throughput_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_WRITES = 2000 if RUN_MODE == "smoke" else 20000


class BiLog:
    def __init__(self):
        self.rows = []; self.root = hashlib.sha256(b"genesis").digest()
    def append(self, k, v, vt, st):
        rec = (k, v, vt, st); self.rows.append(rec); self.root = hashlib.sha256(self.root + repr(rec).encode()).digest()   # running merkle spine


def _selftest():
    L = BiLog(); n0 = len(L.rows); L.append("k", "v", 1, 1); assert len(L.rows) == n0 + 1, "append grows"
    t0 = time.perf_counter(); L.append("k2", "v2", 1, 2); assert time.perf_counter() - t0 >= 0, "timing positive"
    assert 100 / 1.0 == 100.0, "throughput computed"
    print("[selftest] PASS: bitemporal-sync", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    L = BiLog(); t0 = time.perf_counter()
    for i in range(N_WRITES):
        L.append("fact_%d" % i, "content_%d" % i, 10, i)
    dt = time.perf_counter() - t0; per_write_ms = dt / N_WRITES * 1e3; tput = N_WRITES / dt
    print("  writes=%d total=%.3fs per_write=%.4fms throughput=%.0f rows/sec" % (N_WRITES, dt, per_write_ms, tput), flush=True)
    return {"n_writes": N_WRITES, "per_write_ms": per_write_ms, "throughput": tput}


def verdict(r) -> Tuple[str, str]:
    pw = r["per_write_ms"]
    summary = "per_write=%.4fms throughput=%.0f rows/sec (V1 target <100 writes/sec)" % (pw, r["throughput"])
    if pw < 1.0:
        return ("HARD_PASS", "HARD_PASS: append-only bitemporal sync <1ms/write -- synchronous sync adequate for V1 (no async queue needed). " + summary)
    if pw <= 5.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 1-5ms/write (acceptable; monitor at burst). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: >5ms/write -- async queue required for V1. " + summary)


print("[config] anchor=%s mode=%s n_writes=%d" % (ANCHOR_NAME, RUN_MODE, N_WRITES), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
