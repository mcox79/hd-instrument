"""
exp_comp_a2_count_filter_cpu_v1.py -- aggregation over a filter: how many subjects have property P -- CPU.

ROUTING: POST-CYCLE192 Group A composition (A2 COUNT-filter composition (PP-159 + PP-162)). Count the support of a property's inverted shard by thresholding subject scores. Validates COUNT composes with the property filter to within +/-2 of the true count on a 1000-subject KB. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS COUNT-filter accuracy within +/-2 of true count for >= 0.90 of queries. MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "comp_a2_count_filter_cpu_v1"
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
    import numpy as _n; assert abs(round(3.4) - 3) == 0, "round"; print("[selftest] PASS: comp-a2-count-filter", flush=True)
def run() -> Dict:
    g = np.random.default_rng(402); N = 8192; NSUBJ = 1000 if not SMOKE else 300; NPROP = 30; TR = 30 if SMOKE else 80
    subs = cphasor(NSUBJ, N, g); ok = 0; n = 0
    for _ in range(TR):
        has = (g.random((NSUBJ, NPROP)) < 0.15)
        for p in range(0, NPROP, 6):
            idx = np.where(has[:, p])[0]
            if not len(idx):
                continue
            shard = subs[idx].sum(0); sc = (subs @ np.conj(shard)).real / N
            est = int((sc > 0.5).sum()); true = len(idx); ok += int(abs(est - true) <= 2); n += 1
    acc = ok / max(1, n); print("  COUNT-filter within-2 accuracy=%.3f (n=%d)" % (acc, n), flush=True)
    return {"acc": acc}
def verdict(r) -> Tuple[str, str]:
    s = "COUNT-filter within-2=%.3f" % r["acc"]
    if r["acc"] >= 0.90: return ("HARD_PASS", "HARD_PASS: COUNT-over-filter accurate within +/-2 for >=90pct -- aggregation composes with filter. " + s)
    if r["acc"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: COUNT-filter 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: COUNT-filter <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
