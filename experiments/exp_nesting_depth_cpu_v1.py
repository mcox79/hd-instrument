"""
exp_nesting_depth_cpu_v1.py -- recall vs binding nesting depth (how deep can structures go) -- CPU.

ROUTING: CPU substrate capability characterization (nested-structure depth limit). Build nested bindings of depth d (role_1*(role_2*(...*payload))) and unbind d levels + cleanup; sweep d to find where accumulated noise breaks recall. Maps the depth limit for nested data structures. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS payload recall >= 0.90 at depth 8 (N=2048, V=200). MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "nesting_depth_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 16, g)[0]; b = cphasor(1, 16, g)[0]; assert np.allclose(a * b * b.conj(), a, atol=1e-3), "unbind"; print("[selftest] PASS: nesting-depth-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(45); N = 2048; V = 200; TR = 40 if SMOKE else 150; book = cphasor(V, N, g); by = {}
    Ds = [4, 8] if SMOKE else [2, 4, 8, 12, 16]
    for depth in Ds:
        hit = 0
        for _ in range(TR):
            roles = cphasor(depth, N, g); fi = int(g.integers(0, V)); x = book[fi]
            for k in range(depth):
                x = roles[k] * x                      # nest
            for k in range(depth - 1, -1, -1):
                x = x * roles[k].conj()               # unnest
            hit += int(np.argmax((book @ x.conj()).real) == fi)
        by["d%d" % depth] = hit / TR; print("  depth=%d payload-recall=%.3f" % (depth, by["d%d" % depth]), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    d8 = r["by"].get("d8", 0.0); s = "recall by depth: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if d8 >= 0.90: return ("HARD_PASS", "HARD_PASS: nested-structure payload recall>=0.90 at depth 8 -- deep nested data structures are representable. " + s)
    if d8 >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: depth-8 recall 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: depth-8 recall <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
