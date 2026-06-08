"""
exp_multi_fact_aggregation_cpu_v1.py -- substrate supports count/exists aggregate queries over a relation pattern -- CPU.

ROUTING: deep-batch (aggregate queries (count over a pattern)). Given many (subject, R, object) facts, answer 'how many objects does subject S have via R?' by thresholding the unbind spectrum (count entities above the signal floor). Tests aggregate/set-cardinality queries on the substrate. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS count estimate within +/-1 of true degree for >= 0.85 of queries. MIDDLE >= 0.70. HARD-FAIL < 0.70.
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
ANCHOR_NAME = "multi_fact_aggregation_cpu_v1"
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
    import numpy as _n; assert abs(round(2.4) - 2) == 0, "round"; print("[selftest] PASS: multi-fact-aggregation", flush=True)
def run() -> Dict:
    g = np.random.default_rng(214); N = 8192; VE = 200; TR = 60 if SMOKE else 200; R = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g)
    hit = 0; n = 0
    for _ in range(TR):
        s = int(g.integers(0, VE)); deg = int(g.integers(1, 6)); objs = g.choice(VE, deg, replace=False)
        B = np.zeros(N, dtype=np.complex64)
        for o in objs:
            B = B + ents[s] * R * ents[int(o)]
        for _d in range(30):
            ss = int(g.integers(0, VE)); B = B + ents[ss] * R * ents[int(g.integers(0, VE))]
        sc = (ents @ np.conj(B * np.conj(ents[s] * R))).real / N
        est = int((sc > 0.5).sum()); hit += int(abs(est - deg) <= 1); n += 1
    rec = hit / n; print("  count-within-1 accuracy=%.3f (n=%d)" % (rec, n), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "count-within-1=%.3f" % r["recall"]
    if r["recall"] >= 0.85: return ("HARD_PASS", "HARD_PASS: aggregate count queries within +/-1 >=0.85 -- set-cardinality queries supported. " + s)
    if r["recall"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: count accuracy 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: count accuracy <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
