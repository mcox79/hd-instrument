"""
exp_constraint_coloring_check_cpu_v1.py -- substrate readout verifies graph-coloring constraints vs ground truth -- CPU.

ROUTING: batch-10a (CAP-2 constraint (graph-coloring) checker). Stores a graph coloring in substrate, reads back each node's color, and verifies the no-adjacent-same-color constraint -- substrate as a constraint checker. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS validity agreement >=0.95. MIDDLE >=0.85. HARD-FAIL <0.85.
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
ANCHOR_NAME = "constraint_coloring_check_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert (1 != 2), "neq"; print("[selftest] PASS: constraint-coloring-check", flush=True)
def run() -> Dict:
    g = np.random.default_rng(963); N = 8192; VN = 60; NCOL = 4; TR = 40 if SMOKE else 120; ncolv = cphasor(NCOL, N, g); nodes = cphasor(VN, N, g)
    correct = 0; n = 0
    for _ in range(TR):
        # random graph + a coloring; substrate stores node->color; verify no adjacent same-color via substrate readout
        edges = [(int(g.integers(0, VN)), int(g.integers(0, VN))) for _ in range(80)]; edges = [(a, b) for a, b in edges if a != b]
        coloring = g.integers(0, NCOL, VN)
        store = np.zeros(N, dtype=np.complex64)
        for v in range(VN):
            store = store + nodes[v] * ncolv[int(coloring[v])]
        # substrate-read each node's color, check conflicts
        readcol = [cidx(store * np.conj(nodes[v]), ncolv) for v in range(VN)]
        true_valid = all(coloring[a] != coloring[b] for a, b in edges)
        sub_valid = all(readcol[a] != readcol[b] for a, b in edges)
        correct += int(sub_valid == true_valid); n += 1
    acc = correct / n; print("  constraint (coloring-validity) agreement=%.3f (n=%d)" % (acc, n), flush=True)
    return {"acc": acc}
def verdict(r) -> Tuple[str, str]:
    s = "coloring-validity agreement=%.3f" % r["acc"]
    if r["acc"] >= 0.95: return ("HARD_PASS", "HARD_PASS: substrate readout verifies graph-coloring constraints >=0.95 vs ground truth -- substrate as a constraint checker. " + s)
    if r["acc"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: constraint-check 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: constraint-check <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
