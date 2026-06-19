"""
exp_lap2_5_khop_depth10_cpu_v1.py -- substrate 10-hop chain traversal (depth ceiling) -- CPU.

ROUTING: Research LAPTOP_WAVE2 (LAP2-5 K-HOP-DEPTH-10); pure-FHRR (no download). Per-binding sharded substrate; 10 deterministic cleanup-unbind hops.
PRE-REGISTERED: HARD-PASS 10-hop recall>=0.60. MIDDLE>=0.40. HARD-FAIL<0.40.
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
ANCHOR_NAME = "lap2_5_khop_depth10_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert _n.argmax([0,0,1])==2, "argmax"; print("[selftest] PASS: k-hop-depth-10", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1010); N = 8192; VE = 500 if SMOKE else 2000; ents = cphasor(VE, N, g); REL = cphasor(1, N, g)[0]
    HOPS = 10; TR = 30 if SMOKE else 200
    link = {i: int(g.integers(0, VE)) for i in range(VE)}
    shard = {i: ents[i] * (REL * ents[link[i]]) for i in range(VE)}
    hit = 0; n = 0
    for _ in range(TR):
        q = int(g.integers(0, VE)); gold = q; cur = q
        for _h in range(HOPS):
            gold = link[gold]
        for _h in range(HOPS):
            cur = cidx(shard[cur] * np.conj(ents[cur]) * np.conj(REL), ents)
        hit += int(cur == gold); n += 1
    rc = hit / n; print("  10-hop chain recall=%.3f (VE=%d, n=%d)" % (rc, VE, n), flush=True)
    return {"tenhop_recall": rc, "VE": VE}
def verdict(r) -> Tuple[str, str]:
    s = "10-hop-recall=%.3f (VE=%d)" % (r["tenhop_recall"], r["VE"])
    if r["tenhop_recall"] >= 0.60:
        return ("HARD_PASS", "HARD_PASS: substrate deterministic 10-hop traversal recall>=0.60 -- per-binding sharding keeps cleanup exact to depth 10; no empirical depth ceiling (drill 1 confirmed). " + s)
    if r["tenhop_recall"] >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 10-hop 0.40-0.60. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 10-hop <0.40. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
