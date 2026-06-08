"""
exp_cheap1_contradiction_detect_cpu_v1.py -- pre-output conflict detection: small top1-top2 gap flags contradictory facts -- CPU.

ROUTING: 8_DRILLS cheap-decisive batch (CHEAP-1 ACC-style contradiction detection). ACC-style (Botvinick 2001) conflict monitor: a subject with two competing equally-bound objects for the same relation yields a SMALL top1-top2 cleanup gap (conflict); a clean single-object fact yields a LARGE gap. Flag contradiction when gap < threshold. Directly a hallucination/conflict pre-check. Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS contradiction recall >= 0.90 AND false-positive rate < 0.02 on a 200-item KB. MIDDLE recall >= 0.80 / FP < 0.05. HARD-FAIL below.
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
ANCHOR_NAME = "cheap1_contradiction_detect_cpu_v1"
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
    g = np.random.default_rng(0); a = cphasor(3, 64, g); s = a[0] + a[1]; sc = scores(s, a); assert sc[2] < min(sc[0], sc[1]), "conflict"; print("[selftest] PASS: cheap1-contradiction-detect", flush=True)
def run() -> Dict:
    g = np.random.default_rng(611); N = 8192; VE = 200; REL = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g); TR = 80 if SMOKE else 200; THRESH = 0.25
    det = 0; ncon = 0; fp = 0; nclean = 0
    for _ in range(TR):
        s = int(g.integers(0, VE))
        if g.random() < 0.5:  # CONTRADICTION: two competing objects, same relation
            o1, o2 = g.choice(VE, 2, replace=False); shard = ents[int(o1)] * REL + ents[int(o2)] * REL
            ncon += 1; rec = shard * np.conj(REL); sc = np.sort(scores(rec, ents))[::-1]; gap = sc[0] - sc[1]
            det += int(gap < THRESH)
        else:                 # CLEAN: single object
            o = int(g.integers(0, VE)); shard = ents[o] * REL
            nclean += 1; rec = shard * np.conj(REL); sc = np.sort(scores(rec, ents))[::-1]; gap = sc[0] - sc[1]
            fp += int(gap < THRESH)
    rc = det / max(1, ncon); fpr = fp / max(1, nclean); print("  contradiction recall=%.3f FP-rate=%.3f (n_con=%d n_clean=%d)" % (rc, fpr, ncon, nclean), flush=True)
    return {"recall": rc, "fp": fpr}
def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f FP-rate=%.3f" % (r["recall"], r["fp"])
    if r["recall"] >= 0.90 and r["fp"] < 0.02: return ("HARD_PASS", "HARD_PASS: ACC-style contradiction detection >=0.90 recall, <0.02 FP -- pre-output conflict/hallucination pre-check works. " + s)
    if r["recall"] >= 0.80 and r["fp"] < 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: contradiction 0.80-0.90 / FP<0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: contradiction detection weak. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
