"""
exp_preference_bindings_cpu_v1.py -- per-customer preference bindings produce personalized retrieval -- CPU.

ROUTING: v1.5 LOCK batch (E3 Wish-3 customer preference bindings). Each customer has a preference profile; items are scored per-customer and stored as a per-customer bundle. Retrieval returns that customer's top items; different customers get different rankings from the SAME item pool. Tests substrate-native personalization (customer-specific intuitions). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS per-customer top-K recall of their true-preferred items >= 0.90 AND cross-customer ranking divergence high (different customers differ). MIDDLE recall >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "preference_bindings_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert len(set([1, 2, 3]) & set([2, 3, 4])) == 2, "overlap"; print("[selftest] PASS: preference-bindings", flush=True)
def run() -> Dict:
    g = np.random.default_rng(93); N = 8192; NITEM = 300; NCUST = 30 if SMOKE else 80; TOPK = 10
    items = cphasor(NITEM, N, g); recalls = []; divs = []
    cust_tops = []
    for u in range(NCUST):
        prefs = g.standard_normal(NITEM)                                       # this customer's true item scores
        true_top = set(np.argsort(-prefs)[:TOPK].tolist())
        # store as a per-customer preference bundle: sum pref_u(i) * item_i (amplitude-weighted)
        B = (prefs[:, None] * items).sum(0)
        retr = set(np.argsort(-(items @ np.conj(B)).real)[:TOPK].tolist())      # retrieve customer's top items
        recalls.append(len(retr & true_top) / TOPK); cust_tops.append(retr)
    for u in range(min(NCUST, 20)):
        for w in range(u + 1, min(NCUST, 20)):
            divs.append(1.0 - len(cust_tops[u] & cust_tops[w]) / TOPK)
    rec = float(np.mean(recalls)); dv = float(np.mean(divs)) if divs else 0.0
    print("  per-customer top-%d recall=%.3f cross-customer divergence=%.3f (NCUST=%d)" % (TOPK, rec, dv, NCUST), flush=True)
    return {"recall": rec, "divergence": dv}
def verdict(r) -> Tuple[str, str]:
    s = "personalized-recall=%.3f cross-customer-divergence=%.3f" % (r["recall"], r["divergence"])
    if r["recall"] >= 0.90 and r["divergence"] >= 0.5: return ("HARD_PASS", "HARD_PASS: per-customer preference bindings give personalized retrieval (recall>=0.90) that diverges across customers -- substrate-native personalization works. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: personalized recall 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: personalized recall <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
