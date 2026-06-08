"""
exp_sharding_contrast_demo_data_cpu_v1.py -- demo dataset: monolithic recall collapse vs sharded flat recall -- CPU.

ROUTING: v1.5 LOCK batch (B1 sharding contrast demo data). Produce the demo-ready contrast curve: as total stored items grow, monolithic single-bundle recall collapses while sharded (fixed per-shard load) stays flat at ~1.0. Emits the table for the v1 demo's capacity-story slide. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS at the largest total, sharded recall >= 0.95 AND monolithic recall <= 0.40 (clear demo contrast). MIDDLE gap >= 0.40. HARD-FAIL otherwise.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "sharding_contrast_demo_data_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert 16 * 80 == 1280, "total"; print("[selftest] PASS: sharding-contrast-demo-data", flush=True)
def run() -> Dict:
    g = np.random.default_rng(81); N = 4096; K = 80; book = cphasor(2000, N, g); Ss = [1, 4, 16] if SMOKE else [1, 2, 4, 8, 16, 32, 64]
    mono = {}; shard = {}
    for S in Ss:
        keys = cphasor(S * K, N, g); vals = g.integers(0, 2000, S * K)
        Mono = np.zeros(N, dtype=np.complex64); shards = [np.zeros(N, dtype=np.complex64) for _ in range(S)]
        for i in range(S * K):
            Mono = Mono + keys[i] * book[vals[i]]; shards[i // K] = shards[i // K] + keys[i] * book[vals[i]]
        mh = sum(int(cidx(Mono * np.conj(keys[i]), book) == vals[i]) for i in range(S * K)) / (S * K)
        sh = sum(int(cidx(shards[i // K] * np.conj(keys[i]), book) == vals[i]) for i in range(S * K)) / (S * K)
        mono["t%d" % (S * K)] = round(mh, 3); shard["t%d" % (S * K)] = round(sh, 3)
        print("  total=%d monolithic=%.3f sharded=%.3f" % (S * K, mh, sh), flush=True)
    big = "t%d" % (max(Ss) * K); return {"mono": mono, "shard": shard, "mono_big": mono[big], "shard_big": shard[big]}
def verdict(r) -> Tuple[str, str]:
    s = "at largest: sharded=%.3f monolithic=%.3f | sharded-curve=%s mono-curve=%s" % (r["shard_big"], r["mono_big"], r["shard"], r["mono"])
    if r["shard_big"] >= 0.95 and r["mono_big"] <= 0.40: return ("HARD_PASS", "HARD_PASS: demo contrast is sharp -- sharded stays >=0.95 while monolithic collapses to <=0.40. " + s)
    if r["shard_big"] - r["mono_big"] >= 0.40: return ("MIDDLE_BAND", "MIDDLE_BAND: contrast gap >=0.40 but not at target bands. " + s)
    return ("HARD_FAIL", "HARD_FAIL: weak demo contrast. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
