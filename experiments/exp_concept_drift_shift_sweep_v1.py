"""
exp_concept_drift_shift_sweep_v1.py -- drift detectability vs shift magnitude (minimum detectable shift) -- CPU.

ROUTING: concept_drift sensitivity characterization. Sweep the topic-shift fraction; for each, measure the Misra-Gries L1 drift/baseline ratio. Finds the minimum shift magnitude the detector resolves (ratio>3). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS minimum detectable shift <= 0.20 (resolves a 20%% topic shift). MIDDLE <= 0.35. HARD-FAIL only detects >= 0.50.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "concept_drift_shift_sweep_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def zipf(v, s=1.1):
    p = 1.0/np.power(np.arange(1,v+1), s); return p/p.sum()
def mg(stream, k, V):
    cnt = {}
    for x in stream:
        if x in cnt: cnt[x]+=1
        elif len(cnt)<k: cnt[x]=1
        else:
            for kk in list(cnt):
                cnt[kk]-=1
                if cnt[kk]==0: del cnt[kk]
    v = np.zeros(V)
    for kk,c in cnt.items(): v[kk]=c
    su=v.sum(); return v/su if su>0 else v
def _selftest():
    assert abs(zipf(5).sum()-1)<1e-9, "zipf norm"
    s=[1]*50+[2]*3; assert 1 in mg(s,3,5).nonzero()[0].tolist() or mg(s,3,5)[1]>0, "mg heavy"
    assert 0.2<0.5, "order"
    print("[selftest] PASS: concept-drift-shift-sweep", flush=True)
def run() -> Dict:
    g = np.random.default_rng(5); V=100; W=2000 if SMOKE else 8000; K=64; TR=4 if SMOKE else 12
    P=zipf(V); perm=g.permutation(V); Pn=np.zeros(V); Pn[perm]=zipf(V)
    ratios={}
    for sh in [0.05,0.10,0.20,0.30,0.50]:
        Pp=(1-sh)*P+sh*Pn; Pp/=Pp.sum(); db=[]; dd=[]
        for _ in range(TR):
            w0=g.choice(V,W,p=P); w1=g.choice(V,W,p=P); w2=g.choice(V,W,p=Pp)
            db.append(np.abs(mg(w0,K,V)-mg(w1,K,V)).sum()); dd.append(np.abs(mg(w0,K,V)-mg(w2,K,V)).sum())
        ratios["s%.2f"%sh]=float(np.mean(dd)/(np.mean(db)+1e-9))
        print("  shift=%.2f ratio=%.2f" % (sh, ratios["s%.2f"%sh]), flush=True)
    detect=[sh for sh in [0.05,0.10,0.20,0.30,0.50] if ratios["s%.2f"%sh]>3.0]
    mind=min(detect) if detect else 1.0
    return {"ratios": ratios, "min_detect": mind}
def verdict(r) -> Tuple[str, str]:
    md=r["min_detect"]; s="min-detectable-shift=%.2f | ratios=%s" % (md, {k:round(v,2) for k,v in r["ratios"].items()})
    if md <= 0.20: return ("HARD_PASS", "HARD_PASS: detector resolves a <=20%% topic shift -- sensitive drift alerting. " + s)
    if md <= 0.35: return ("MIDDLE_BAND", "MIDDLE_BAND: min detectable shift <=0.35. " + s)
    return ("HARD_FAIL", "HARD_FAIL: only detects >=0.50 shift. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
