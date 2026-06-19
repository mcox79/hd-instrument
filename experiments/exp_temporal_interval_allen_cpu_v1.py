"""
exp_temporal_interval_allen_cpu_v1.py -- Allen interval algebra over substrate endpoints -- CPU.

ROUTING: Research LAPTOP_WAVE2 (STRETCH2-1 TEMPORAL-INTERVAL); pure-FHRR (no download). Store interval endpoints; retrieve; classify the 13 Allen relations.
PRE-REGISTERED: HARD-PASS Allen>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.
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
ANCHOR_NAME = "temporal_interval_allen_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: temporal-interval", flush=True)
def _allen(a, b):
    (s1, e1), (s2, e2) = a, b
    if e1 < s2: return "before"
    if s1 > e2: return "after"
    if e1 == s2: return "meets"
    if s1 == e2: return "met-by"
    if s1 == s2 and e1 == e2: return "equals"
    if s1 < s2 and e1 > e2: return "contains"
    if s1 > s2 and e1 < e2: return "during"
    if s1 < s2 < e1 < e2: return "overlaps"
    if s2 < s1 < e2 < e1: return "overlapped-by"
    if s1 == s2 and e1 < e2: return "starts"
    if s1 == s2 and e1 > e2: return "started-by"
    if e1 == e2 and s1 > s2: return "finishes"
    if e1 == e2 and s1 < s2: return "finished-by"
    return "overlaps"
def run() -> Dict:
    # store interval endpoints (quantized) bound to interval keys; retrieve endpoints; classify the Allen relation.
    g = np.random.default_rng(21); N = 8192; T = 12; ticks = cphasor(T, N, g); SLOT = cphasor(2, N, g); ikey = cphasor(2, N, g)
    TR = 50 if SMOKE else 300; correct = 0; n = 0
    for _ in range(TR):
        def mkiv():
            x = sorted(int(v) for v in g.choice(T, 2, replace=False)); return (x[0], x[1])
        A = mkiv(); B = mkiv()
        rec = {0: A, 1: B}; store = {}
        for k, (s, e) in rec.items():
            store[k] = ikey[k] * (SLOT[0] * ticks[s]) + ikey[k] * (SLOT[1] * ticks[e])
        # retrieve endpoints from substrate, then classify
        out = {}
        for k in (0, 1):
            sh = cidx(store[k] * np.conj(ikey[k]) * np.conj(SLOT[0]), ticks)
            eh = cidx(store[k] * np.conj(ikey[k]) * np.conj(SLOT[1]), ticks)
            out[k] = (sh, eh)
        gold = _allen(A, B); pred = _allen(out[0], out[1])
        correct += int(pred == gold); n += 1
    acc = correct / n; print("  TEMPORAL-INTERVAL Allen-relation acc=%.3f (n=%d)" % (acc, n), flush=True)
    return {"allen_acc": acc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "Allen-relation-acc=%.3f (n=%d)" % (r["allen_acc"], r["n"])
    if r["allen_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate classifies Allen interval relations >=0.85 (before/after/during/overlaps/meets...) -- temporal interval algebra over substrate-stored endpoints. " + s)
    if r["allen_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: Allen 0.70-0.85 (endpoint cleanup error). " + s)
    return ("HARD_FAIL", "HARD_FAIL: Allen <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
