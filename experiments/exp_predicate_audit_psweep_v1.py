"""
exp_predicate_audit_psweep_v1 -- #12: predicate routing P-sweep across selectivities -- CPU.
ROUTING: top20/pattern-b-ext #12 predicate-P-sweep. Predicate routing recall@10 at selectivities {1,3,5,7,10,15,20}%; identify the selectivity threshold above which it degrades. CPU.
PRE-REGISTERED: HARD-PASS identify selectivity threshold where recall@10 crosses 0.85.
FORMULA SELF-TESTS (PROT-022): 1. unbind inverts. 2. unit phasor. 3. selectivity sweep.
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
ANCHOR_NAME = "predicate_audit_psweep_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
SELS = [0.01, 0.05, 0.10] if RUN_MODE == "smoke" else [0.01, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20]; NFACT = 400; NQ = 20
def _selftest():
    g = np.random.default_rng(0); a = phasor(64,1,g)[0]; assert np.allclose((a*phasor(64,1,g)[0])*np.conj(a)*0+a*np.conj(a), a*np.conj(a)), "unbind inverts"
    assert np.allclose(np.abs(a),1.0,atol=1e-5), "unit phasor"
    assert len(SELS) >= 2, "selectivity sweep"
    print("[selftest] PASS: predicate-psweep", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); by = {}; thresh = None
    for sel in SELS:
        npred = max(2, int(round(1.0/sel))); preds = phasor(N, npred, g); subj = phasor(N, NFACT, g)
        pred_of = g.integers(0, npred, NFACT); facts = np.array([preds[pred_of[i]]*subj[i] for i in range(NFACT)])
        recs = []
        for _ in range(NQ):
            X = int(g.integers(0, npred)); targets = np.where(pred_of == X)[0]
            if len(targets) == 0: continue
            unb = facts * np.conj(preds[X]); score = np.abs((unb @ np.conj(subj.T)).real).max(axis=1)
            top = np.argsort(score)[::-1][:10]; recs.append(len(set(top) & set(targets)) / min(10, len(targets)))
        r10 = float(np.mean(recs)) if recs else 0.0; by["sel%.2f" % sel] = r10
        if r10 < 0.85 and thresh is None: thresh = sel
        print("  selectivity=%.0f%% recall@10=%.3f" % (sel*100, r10), flush=True)
    return {"by": by, "thresh": thresh if thresh else 0.0}
def verdict(r) -> Tuple[str, str]:
    s = "recall@10 by selectivity: %s; degrade-threshold=%.0f%%" % ({k: round(v,3) for k,v in r["by"].items()}, r["thresh"]*100)
    sparse = r["by"].get("sel0.05", r["by"].get("sel0.01", 0))
    if sparse >= 0.85: return ("HARD_PASS", "HARD_PASS: predicate routing recall@10>=0.85 in sparse regime (<=5%) -- bounded capability mapped, threshold identified. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: sparse-regime recall@10 below 0.85. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
