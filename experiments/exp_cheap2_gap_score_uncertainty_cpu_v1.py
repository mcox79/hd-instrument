"""
exp_cheap2_gap_score_uncertainty_cpu_v1.py -- top1-top2 cleanup gap correlates with answer correctness (second-order uncertainty) -- CPU.

ROUTING: 8_DRILLS cheap-decisive batch (CHEAP-2 gap-score uncertainty signal). The cleanup gap (top-1 minus top-2 similarity) is a usable uncertainty signal: when the substrate answer is correct the gap is large, when wrong/uncertain it is small. Vary distractor load so correctness varies; measure Spearman(gap, correct). Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS AUC(gap separates correct vs incorrect) >= 0.75. MIDDLE >= 0.65. HARD-FAIL < 0.65.
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
ANCHOR_NAME = "cheap2_gap_score_uncertainty_cpu_v1"
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
    assert abs(spearman([1,2,3,4],[1,2,3,4]) - 1.0) < 1e-9, "spearman"; print("[selftest] PASS: cheap2-gap-score-uncertainty", flush=True)
def run() -> Dict:
    g = np.random.default_rng(612); N = 4096; VE = 400; REL = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g); TR = 150 if SMOKE else 500
    gaps = []; correct = []
    for _ in range(TR):
        s = int(g.integers(0, VE)); o = int(g.integers(0, VE)); load = int(g.integers(5, 400))  # wide load -> correctness spans (needed for correlation)
        shard = ents[s] * REL * ents[o]
        for _d in range(load):
            shard = shard + ents[int(g.integers(0, VE))] * REL * ents[int(g.integers(0, VE))]
        rec = shard * np.conj(ents[s] * REL); allsc = scores(rec, ents); order = np.sort(allsc)[::-1]; gap = order[0] - order[1]
        pred = int(np.argmax(allsc)); gaps.append(gap); correct.append(int(pred == o))
    gaps = np.array(gaps); correct = np.array(correct)
    gc = gaps[correct == 1]; gw = gaps[correct == 0]
    a = auc(gc, gw) if (len(gc) and len(gw)) else 0.5; rho = spearman(gaps, correct); acc = float(correct.mean())
    print("  AUC(gap|correct-vs-wrong)=%.3f (point-biserial rho=%.3f, acc=%.3f, n=%d)" % (a, rho, acc, TR), flush=True)
    return {"auc": a, "spearman": rho, "acc": acc}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.3f (rho=%.3f, acc=%.3f)" % (r["auc"], r["spearman"], r["acc"])
    if r["auc"] >= 0.75: return ("HARD_PASS", "HARD_PASS: cleanup gap-score separates correct vs incorrect answers AUC>=0.75 -- usable second-order uncertainty/abstention signal. " + s)
    if r["auc"] >= 0.65: return ("MIDDLE_BAND", "MIDDLE_BAND: gap-AUC 0.65-0.75. " + s)
    return ("HARD_FAIL", "HARD_FAIL: gap-AUC <0.65. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
