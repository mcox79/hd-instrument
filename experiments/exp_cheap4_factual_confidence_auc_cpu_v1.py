"""
exp_cheap4_factual_confidence_auc_cpu_v1.py -- cleanup confidence separates true from hallucinated claims (AUC) -- CPU.

ROUTING: 8_DRILLS cheap-decisive batch (CHEAP-4 substrate confidence as factual predictor). For a claim (subject, relation, claimed-object), the substrate cleanup confidence (score of the claimed object after unbinding subject*relation from the KB shard) is high for TRUE claims (object actually bound) and low for HALLUCINATED claims (wrong object). Measures AUC of confidence as a factual-vs-hallucinated classifier -- a customer-presentable hallucination-detection number. Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS confidence AUC >= 0.90 (true vs hallucinated). MIDDLE >= 0.80. HARD-FAIL < 0.80.
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
ANCHOR_NAME = "cheap4_factual_confidence_auc_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def scores(v, book):
    return (book @ np.conj(v)).real / book.shape[1]
def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg); c = 0; t = 0
    for p in pos:
        c += (neg < p).sum() + 0.5 * (neg == p).sum(); t += len(neg)
    return c / max(1, t)
def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    ra = ra - ra.mean(); rb = rb - rb.mean()
    d = math.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / d) if d > 0 else 0.0

def _selftest():
    assert auc([0.9,0.8],[0.1,0.2]) == 1.0, "auc"; print("[selftest] PASS: cheap4-factual-confidence-auc", flush=True)
def run() -> Dict:
    g = np.random.default_rng(614); N = 8192; VE = 300; REL = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g); TR = 80 if SMOKE else 250
    pos = []; neg = []
    for _ in range(TR):
        s = int(g.integers(0, VE)); deg = int(g.integers(2, 6)); objs = g.choice(VE, deg, replace=False)
        shard = np.zeros(N, dtype=np.complex64)
        for o in objs:
            shard = shard + ents[int(o)] * REL
        rec = shard * np.conj(REL)
        true_o = int(objs[0]); pos.append(float(scores(rec, ents)[true_o]))   # true claim confidence
        wrong = int(g.integers(0, VE))
        while wrong in objs:
            wrong = int(g.integers(0, VE))
        neg.append(float(scores(rec, ents)[wrong]))                            # hallucinated claim confidence
    a = auc(pos, neg); print("  factual-confidence AUC=%.3f (true mean=%.3f, halluc mean=%.3f, n=%d)" % (a, float(np.mean(pos)), float(np.mean(neg)), len(pos)), flush=True)
    return {"auc": a}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.3f" % r["auc"]
    if r["auc"] >= 0.90: return ("HARD_PASS", "HARD_PASS: substrate confidence separates true vs hallucinated claims AUC>=0.90 -- usable factual-accuracy/hallucination predictor (EU AI Act verification claim). " + s)
    if r["auc"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: factual AUC 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: factual AUC <0.80. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
