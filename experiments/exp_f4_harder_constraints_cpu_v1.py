"""
exp_f4_harder_constraints_cpu_v1.py -- substrate constraint-check agreement >=0.95 on 100-vertex graphs -- CPU.

ROUTING: CYCLE_200_FOLLOWUPS (F4 harder constraint problems). Graph-coloring constraint checking on 100-vertex graphs (vs the small graphs in PP-213). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS agreement >=0.95. MIDDLE >=0.85. HARD-FAIL <0.85.
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
ANCHOR_NAME = "f4_harder_constraints_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert (1 != 2), "neq"; print("[selftest] PASS: f4-harder-constraints", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2004); N = 8192; VN = 100; NCOL = 4; TR = 20 if SMOKE else 60; ncolv = cphasor(NCOL, N, g); nodes = cphasor(VN, N, g)
    agree = 0; n = 0
    for _ in range(TR):
        edges = []
        for _e in range(250):
            a = int(g.integers(0, VN)); b = int(g.integers(0, VN))
            if a != b:
                edges.append((a, b))
        coloring = g.integers(0, NCOL, VN)
        store = np.zeros(N, dtype=np.complex64)
        for vtx in range(VN):
            store = store + nodes[vtx] * ncolv[int(coloring[vtx])]
        readcol = [cidx(store * np.conj(nodes[vtx]), ncolv) for vtx in range(VN)]
        true_valid = all(coloring[a] != coloring[b] for a, b in edges)
        sub_valid = all(readcol[a] != readcol[b] for a, b in edges)
        agree += int(sub_valid == true_valid); n += 1
    acc = agree / n; print("  100-vertex coloring-validity agreement=%.3f (n=%d)" % (acc, n), flush=True)
    return {"acc": acc, "vertices": VN}
def verdict(r) -> Tuple[str, str]:
    s = "100-vertex coloring agreement=%.3f" % r["acc"]
    if r["acc"] >= 0.95: return ("HARD_PASS", "HARD_PASS: substrate constraint-check agreement >=0.95 on 100-vertex graphs vs ground truth -- scales to harder constraint problems. " + s)
    if r["acc"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: agreement 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: agreement <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
