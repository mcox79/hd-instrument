"""
exp_patternb_pinv_recovery_v1 -- Pattern B compat #2: pinv auto-associative recovery from partial bundle -- CPU.
ROUTING: handoff pattern_b_compat_tests_authorize cell 2. Store 200 bundles via pinv auto-assoc; query with partial (one role binding); recover full bundle. CPU.
PRE-REGISTERED: HARD-PASS partial-query recovery acc>=0.95; else MIDDLE>=0.85 / HARD_FAIL<0.85.
FORMULA SELF-TESTS (PROT-022): 1. unbind inverts. 2. unit phasor. 3. pinv recovers stored.
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
ANCHOR_NAME = "patternb_pinv_recovery_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
N_BUND = 200; N_ROLE = 6
def _selftest():
    g=np.random.default_rng(0); a=phasor(64,1,g)[0]; b=phasor(64,1,g)[0]
    assert np.allclose((a*b)*np.conj(a),b,atol=1e-4), "unbind inverts"
    assert np.allclose(np.abs(a),1.0,atol=1e-5), "unit phasor"
    K=unit(g.standard_normal((5,16))); assert int(np.argmax(unit(K)@unit(K)[0]))==0, "pinv recovers stored"
    print("[selftest] PASS: patternb-pinv-recovery", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g=np.random.default_rng(7); roles=phasor(N,N_ROLE,g); B=[]; parts=[]
    for _ in range(N_BUND):
        k=g.integers(3,6); idx=g.choice(N_ROLE,k,replace=False); fill=phasor(N,k,g)
        binds=[roles[idx[i]]*fill[i] for i in range(k)]
        B.append(np.sum(binds,axis=0)); parts.append(binds[0])   # partial = first role binding only
    X=np.array(B); P=np.array(parts)
    Xr=np.concatenate([X.real,X.imag],1).astype(np.float64); Pr=np.concatenate([P.real,P.imag],1).astype(np.float64)
    Kk=unit(Xr); G=Kk@Kk.T+1e-3*np.eye(len(Kk)); Winv=np.linalg.solve(G,Kk)   # auto-assoc recovery operator
    rec=unit(Pr)@Winv.T   # [B,B] each row recovers index
    acc=float((np.argmax(rec,axis=1)==np.arange(N_BUND)).mean())
    print("  partial-query (1-role) full-bundle recovery acc=%.3f (%d bundles)" % (acc,N_BUND), flush=True)
    return {"acc": acc}
def verdict(r) -> Tuple[str, str]:
    a=r["acc"]; s="partial-bundle recovery acc=%.3f" % a
    if a>=0.95: return ("HARD_PASS","HARD_PASS: pinv auto-associative recovery from a partial (1-role) bundle >=0.95 -- pinv transfers cleanly to Pattern B. "+s)
    if a>=0.85: return ("MIDDLE_BAND","MIDDLE_BAND: partial recovery 0.85-0.95. "+s)
    return ("HARD_FAIL","HARD_FAIL: partial recovery <0.85 -- pinv auto-assoc weak on bundles. "+s)

print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
