"""
exp_binding_entropy_routing_cpu_v1.py -- binding entropy predicts whether a query is answerable by native K-hop -- CPU.

ROUTING: hybrid-architecture / KG-QA mechanism (H4 binding-entropy self-routing). When a (subject,relation) query has a clean match in the KG, the unbind cleanup distribution is PEAKED (low entropy); when it does not, the distribution is FLAT (high entropy). Tests whether this entropy self-routes answerable vs unanswerable queries (cheap confidence/abstention + native-vs-fuzzy routing signal). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS AUC(answerable low-entropy vs unanswerable high-entropy) >= 0.85. MIDDLE >= 0.70. HARD-FAIL < 0.70.
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
ANCHOR_NAME = "binding_entropy_routing_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg); alls = np.concatenate([pos, neg]); lab = np.concatenate([np.ones(len(pos)), np.zeros(len(neg))])
    order = np.argsort(alls); ranks = np.empty_like(order, dtype=np.float64); ranks[order] = np.arange(1, len(alls) + 1)
    return float((ranks[lab == 1].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg) + 1e-9))

def _selftest():
    p = np.array([10.0, 0, 0]); sm = np.exp(p - p.max()); sm /= sm.sum(); ent = -(sm * np.log(sm + 1e-12)).sum(); assert ent < 0.5, "peaked low entropy"; print("[selftest] PASS: binding-entropy-routing", flush=True)
def run() -> Dict:
    g = np.random.default_rng(51); N = 8192; VE = 150; VR = 16; TR = 80 if SMOKE else 250
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}
    M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(2):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    def entropy(s, r):
        sc = (ents @ np.conj(M * np.conj(ents[s] * rels[r]))).real; sm = np.exp(sc - sc.max()); sm /= sm.sum(); return -(sm * np.log(sm + 1e-12)).sum()
    ans = []; non = []
    keys = list(edges.keys()); g.shuffle(keys)
    for (s, r) in keys[:TR]:
        ans.append(entropy(s, r))
    for _ in range(TR):
        s = int(g.integers(0, VE)); r = int(g.integers(0, VR))
        if (s, r) not in edges:
            non.append(entropy(s, r))
    a = auc([-x for x in ans], [-x for x in non])           # answerable = LOW entropy -> negate so higher=answerable
    print("  AUC(answerable low-entropy vs unanswerable)=%.4f (ans mean=%.3f non mean=%.3f)" % (a, float(np.mean(ans)), float(np.mean(non))), flush=True)
    return {"auc": a}
def verdict(r) -> Tuple[str, str]:
    s = "routing AUC=%.4f" % r["auc"]
    if r["auc"] >= 0.85: return ("HARD_PASS", "HARD_PASS: binding entropy self-routes answerable vs unanswerable at AUC>=0.85 -- cheap native confidence + native-vs-fuzzy routing signal. " + s)
    if r["auc"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: routing AUC 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: routing AUC <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
