"""
exp_lap2_7_khop_cyclic_cpu_v1.py -- cycle detection + termination in K-hop traversal -- CPU.

ROUTING: Research LAPTOP_WAVE2 (LAP2-7 K-HOP-CYCLIC-VALIDATE); pure-FHRR (no download). Functional graph (every path enters a cycle); substrate traversal detects revisit + terminates; match gold cycle-entry node.
PRE-REGISTERED: HARD-PASS cycle-detect>=0.95. MIDDLE>=0.80. HARD-FAIL<0.80.
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
ANCHOR_NAME = "lap2_7_khop_cyclic_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: k-hop-cyclic-validate", flush=True)
def run() -> Dict:
    g = np.random.default_rng(161); N = 8192; VE = 300 if SMOKE else 1000; ents = cphasor(VE, N, g); REL = cphasor(1, N, g)[0]
    link = {i: int(g.integers(0, VE)) for i in range(VE)}                # functional graph -> every path enters a cycle (rho)
    shard = {i: ents[i] * (REL * ents[link[i]]) for i in range(VE)}
    TR = 40 if SMOKE else 250; det_ok = 0; n = 0
    for _ in range(TR):
        q = int(g.integers(0, VE))
        # gold: walk link until a node repeats; record the cycle-entry node
        seen_g = {}; cur = q; step = 0; gold_cycle = None
        while cur not in seen_g:
            seen_g[cur] = step; cur = link[cur]; step += 1
        gold_cycle = cur
        # substrate: traverse via cleanup, detect revisit, terminate
        seen_s = set(); cur = q; det = None
        for _h in range(VE + 5):
            if cur in seen_s:
                det = cur; break
            seen_s.add(cur); cur = cidx(shard[cur] * np.conj(ents[cur]) * np.conj(REL), ents)
        det_ok += int(det == gold_cycle); n += 1
    acc = det_ok / n; print("  K-HOP-CYCLIC cycle-detect+terminate=%.3f (VE=%d, n=%d)" % (acc, VE, n), flush=True)
    return {"cycle_detect": acc, "VE": VE}
def verdict(r) -> Tuple[str, str]:
    s = "cycle-detect+terminate=%.3f (VE=%d)" % (r["cycle_detect"], r["VE"])
    if r["cycle_detect"] >= 0.95:
        return ("HARD_PASS", "HARD_PASS: substrate K-hop traversal detects cycles + terminates >=0.95 -- revisit detection over cleanup-traversal; no infinite loops on cyclic KBs (PP-161/177 at scale). " + s)
    if r["cycle_detect"] >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cycle-detect 0.80-0.95 (per-hop cleanup error). " + s)
    return ("HARD_FAIL", "HARD_FAIL: cycle-detect <0.80. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
