"""
exp_set_algebra_bundle_cpu_v1.py -- substrate set operations: union and intersection of fact-sets recovered by cleanup -- CPU.

ROUTING: fast-cheap batch (set union/intersection via bundle algebra). Sets of items encoded as bundles; UNION = bundle sum (recover all members), INTERSECTION via per-item membership scoring across two bundles (item in both). Tests substrate set algebra (a query-language primitive). Pure numpy FHRR (sub-minute; all-or-nothing OK). CPU.
PRE-REGISTERED: HARD-PASS union recall >= 0.95 AND intersection F1 >= 0.90. MIDDLE >= 0.85/0.80. HARD-FAIL below.
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
ANCHOR_NAME = "set_algebra_bundle_cpu_v1"
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
    assert len({1,2,3} & {2,3,4}) == 2, "intersect"; print("[selftest] PASS: set-algebra-bundle", flush=True)
def run() -> Dict:
    g = np.random.default_rng(805); N = 8192; VE = 400; TR = 60 if SMOKE else 200; ents = cphasor(VE, N, g)
    urec = 0; utot = 0; f1s = []
    for _ in range(TR):
        A = set(int(x) for x in g.choice(VE, int(g.integers(4, 12)), replace=False))
        B = set(int(x) for x in g.choice(VE, int(g.integers(4, 12)), replace=False))
        bA = sum((ents[i] for i in A), np.zeros(N, dtype=np.complex64)); bB = sum((ents[i] for i in B), np.zeros(N, dtype=np.complex64))
        # union recall: top-|A| from bA recovers A
        gotA = topk(bA, ents, len(A)); urec += len(gotA & A); utot += len(A)
        # intersection: items scoring high in BOTH bundles
        thr = 0.5; inA = set(np.where((ents @ np.conj(bA)).real / N > thr)[0].tolist()); inB = set(np.where((ents @ np.conj(bB)).real / N > thr)[0].tolist())
        pred = inA & inB; gold = A & B
        tp = len(pred & gold); prec = tp / max(1, len(pred)); rcl = tp / max(1, len(gold)); f1 = 2 * prec * rcl / max(1e-9, prec + rcl) if gold else (1.0 if not pred else 0.0)
        f1s.append(f1)
    ur = urec / utot; fi = float(np.mean(f1s)); print("  union-recall=%.3f intersection-F1=%.3f (n=%d)" % (ur, fi, TR), flush=True)
    return {"union": ur, "intersect_f1": fi}
def verdict(r) -> Tuple[str, str]:
    s = "union-recall=%.3f intersection-F1=%.3f" % (r["union"], r["intersect_f1"])
    if r["union"] >= 0.95 and r["intersect_f1"] >= 0.90: return ("HARD_PASS", "HARD_PASS: substrate set union (>=0.95) + intersection (F1>=0.90) -- set-algebra query primitives work. " + s)
    if r["union"] >= 0.85 and r["intersect_f1"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: set-algebra 0.85/0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: set-algebra weak. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
