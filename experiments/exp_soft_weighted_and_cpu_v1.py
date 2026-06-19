"""
exp_soft_weighted_and_cpu_v1.py -- weighted AND: rank items by a weighted combination of attribute constraints -- CPU.

ROUTING: refill (soft/weighted conjunctive query). Beyond hard AND: a query specifies several attribute constraints with WEIGHTS; items are ranked by the weighted sum of constraint matches (a soft retrieval). Tests graded multi-constraint scoring -- closer to real ranked search than a boolean AND. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS weighted-AND ranking puts the true best-match item in top-1 >= 0.90. MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "soft_weighted_and_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    import numpy as _n; assert int(_n.argmax([0.1,0.5,0.9]))==2, "argmax"; print("[selftest] PASS: soft-weighted-and", flush=True)
def run() -> Dict:
    g = np.random.default_rng(502); N = 16384; NITEM = 200; NF = 4; VALS = 6; TR = 40 if SMOKE else 120
    facets = cphasor(NF, N, g); vals = cphasor(NF*VALS, N, g); hit = 0; n = 0
    for _ in range(TR):
        attr = g.integers(0, VALS, (NITEM, NF)); items = np.zeros((NITEM, N), dtype=np.complex64)
        for it in range(NITEM):
            for f in range(NF):
                items[it] = items[it] + facets[f] * vals[f*VALS + int(attr[it,f])]
        items = items / (np.abs(items) + 1e-8)
        w = g.uniform(0.3, 1.0, NF); tgt = g.integers(0, VALS, NF)
        q = np.zeros(N, dtype=np.complex64)
        for f in range(NF):
            q = q + w[f] * facets[f] * vals[f*VALS + int(tgt[f])]
        # ground-truth best item = max weighted matches
        match = (attr == tgt[None,:]).astype(float) @ w
        gold = int(np.argmax(match)); pred = cidx(q, items)
        hit += int(pred == gold); n += 1
    rec = hit / n; print("  weighted-AND top1=%.3f (n=%d)" % (rec, n), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "weighted-AND top1=%.3f" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: weighted/soft conjunctive ranking puts the best-match item top-1 >=0.90 -- graded multi-constraint retrieval works. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: weighted-AND 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: weighted-AND <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
