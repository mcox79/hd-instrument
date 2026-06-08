"""
exp_hierarchical_2level_cpu_v1.py -- 2-level hierarchy: query a category, retrieve its member items -- CPU.

ROUTING: CPU substrate capability characterization (category-conditioned retrieval). Store items bound to their category (M = sum cat[c]*item). Query a category by unbinding -> superposition of its members -> cleanup top-n recovers them. Tests hierarchical/faceted retrieval. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS category-conditioned recall of members >= 0.90 (n_per_cat members, C cats). MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "hierarchical_2level_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    assert np.argsort(-np.array([0.1, 0.9, 0.5]))[0] == 1, "argsort"; print("[selftest] PASS: hierarchical-2level-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(32); N = 2048; C = 20; PER = 6; V = C * PER
    cats = cphasor(C, N, g); items = cphasor(V, N, g)
    M = np.zeros(N, dtype=np.complex64)
    for c in range(C):
        for j in range(PER):
            M = M + cats[c] * items[c * PER + j]
    hit = 0; tot = 0
    for c in range(C):
        rec = M * cats[c].conj(); sc = (items @ rec.conj()).real; top = np.argsort(-sc)[:PER]
        members = set(range(c * PER, c * PER + PER)); hit += len(set(top.tolist()) & members); tot += PER
    rec = hit / tot; print("  category-conditioned member recall=%.3f (C=%d PER=%d N=%d)" % (rec, C, PER, N), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "member-recall=%.3f" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: category query recovers its members >=0.90 -- hierarchical/faceted retrieval works. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: member recall 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: member recall <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
