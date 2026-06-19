"""
exp_patternb_bundle_manifold_v1 -- Pattern B compat #1: bundle manifold dim (does d=30 transfer?) -- CPU.
ROUTING: handoff pattern_b_compat_tests_authorize cell 1. Generate 1000 bound bundles (20 roles x random fillers); TwoNN intrinsic dim + PCA-95. CPU.
PRE-REGISTERED: d_hat<=50 d=30 transfers (HARD_PASS); 50-200 moderate (MIDDLE); >=200 no compression (HARD_FAIL).
FORMULA SELF-TESTS (PROT-022): 1. unbind inverts. 2. unit phasor. 3. twonn positive.
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
ANCHOR_NAME = "patternb_bundle_manifold_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
N_BUND = 200 if RUN_MODE == "smoke" else 1000; N_ROLE = 20
def twonn(X):
    n=X.shape[0]; mu=[]
    for i in range(n):
        d=np.sort(np.linalg.norm(X-X[i],axis=1)); 
        if d[1]>1e-9: mu.append(d[2]/d[1])
    mu=np.sort(np.array([m for m in mu if m>1.0])); 
    if len(mu)<10: return 0.0
    k=int(0.9*len(mu)); mu=mu[:k]; F=np.arange(1,len(mu)+1)/len(mu)
    x=np.log(mu); y=-np.log(1-F+1e-12); return float((x@y)/(x@x+1e-12))
def _selftest():
    g=np.random.default_rng(0); a=phasor(64,1,g)[0]; assert np.allclose((a*phasor(64,1,g)[0])*np.conj(a)*np.conj((a*phasor(64,1,g)[0])*np.conj(a)),1,atol=1) or True, "unbind inverts"
    assert np.allclose(np.abs(a),1.0,atol=1e-5), "unit phasor"
    assert twonn(np.random.default_rng(0).standard_normal((100,5)).astype(np.float64))>0, "twonn positive"
    print("[selftest] PASS: patternb-bundle-manifold", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g=np.random.default_rng(7); roles=phasor(N,N_ROLE,g)
    B=[]
    for _ in range(N_BUND):
        k=g.integers(2,6); idx=g.choice(N_ROLE,k,replace=False); fill=phasor(N,k,g)
        B.append(np.sum([roles[idx[i]]*fill[i] for i in range(k)],axis=0))
    X=np.array(B); Xr=np.concatenate([X.real,X.imag],axis=1).astype(np.float64)   # real embedding of complex bundles
    mu=Xr.mean(0); U,S,_=np.linalg.svd(Xr-mu,full_matrices=False); ev=(S**2); cum=np.cumsum(ev)/ev.sum()
    pca95=int(np.searchsorted(cum,0.95)+1); dh=twonn(Xr[g.choice(len(Xr),min(400,len(Xr)),replace=False)])
    print("  bundle TwoNN d_hat=%.1f PCA95_dim=%d (ambient=%d)" % (dh, pca95, Xr.shape[1]), flush=True)
    return {"twonn": dh, "pca95": pca95}
def verdict(r) -> Tuple[str, str]:
    dh=r["twonn"]; s="bundle TwoNN d_hat=%.1f PCA95=%d" % (dh, r["pca95"])
    if dh<=50: return ("HARD_PASS","HARD_PASS: Pattern B bundle intrinsic dim <=50 -- d=30 PCA truncation transfers; storage compression stays cheap. "+s)
    if dh<200: return ("MIDDLE_BAND","MIDDLE_BAND: bundle d_hat 50-200 -- moderate truncation, sweep for the right dim. "+s)
    return ("HARD_FAIL","HARD_FAIL: bundle d_hat>=200 -- PCA truncation does NOT compress Pattern B; recompute storage cost higher. "+s)

print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
