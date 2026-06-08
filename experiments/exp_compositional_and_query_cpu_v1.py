"""
exp_compositional_and_query_cpu_v1.py -- retrieve items satisfying TWO bound attribute constraints simultaneously -- CPU.

ROUTING: refill batch (conjunctive (AND) constraint query). Items each bind several attribute=value facets (color, shape, size). A conjunctive query (color=red AND shape=circle) is answered by scoring items against the combined constraints; only items matching BOTH should rank top. Measures precision@matchcount of the AND. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS conjunctive-query precision >= 0.90 (matching items ranked above non-matching). MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "compositional_and_query_cpu_v1"
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
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; v = cphasor(1, 64, g)[0]; assert np.allclose(a * v * np.conj(a), v, atol=1e-3), "bind"; print("[selftest] PASS: compositional-and-query", flush=True)
def run() -> Dict:
    g = np.random.default_rng(326); N = 8192; NITEM = 300; NF = 3; VALS = 5; TR = 40 if SMOKE else 120
    facets = cphasor(NF, N, g); vals = cphasor(NF * VALS, N, g)
    hit = 0; tot = 0
    for _ in range(TR):
        item_attr = g.integers(0, VALS, (NITEM, NF)); items = np.zeros((NITEM, N), dtype=np.complex64)
        for it in range(NITEM):
            for f in range(NF):
                items[it] = items[it] + facets[f] * vals[f * VALS + int(item_attr[it, f])]
        items = items / (np.abs(items) + 1e-8)
        f1, f2 = 0, 1; v1 = int(g.integers(0, VALS)); v2 = int(g.integers(0, VALS))
        gold = set(it for it in range(NITEM) if item_attr[it, f1] == v1 and item_attr[it, f2] == v2)
        if not gold:
            continue
        q = facets[f1] * vals[f1 * VALS + v1] + facets[f2] * vals[f2 * VALS + v2]   # conjunctive constraint vector
        top = topk(q, items, len(gold)); hit += len(top & gold); tot += len(gold)
    prec = hit / max(1, tot); print("  conjunctive AND-query precision@k=%.3f" % prec, flush=True)
    return {"precision": prec}
def verdict(r) -> Tuple[str, str]:
    s = "AND-query precision=%.3f" % r["precision"]
    if r["precision"] >= 0.90: return ("HARD_PASS", "HARD_PASS: conjunctive (A AND B) query precision >=0.90 -- multi-constraint structured retrieval works. " + s)
    if r["precision"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: AND-query 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: AND-query <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
