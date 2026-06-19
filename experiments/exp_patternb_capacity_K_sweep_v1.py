"""
exp_patternb_capacity_K_sweep_v1 -- #13: Pattern B bundle capacity vs K (items/bundle) at production N -- CPU.
ROUTING: top20/pattern-b-ext #13 capacity-K. Sweep K (role-filler items per bundle) 5..50 at N=4096; measure retrieval F1; identify production K limit at F1>=0.95. CPU.
PRE-REGISTERED: HARD-PASS identify K limit where F1>=0.95 at N=4096.
FORMULA SELF-TESTS (PROT-022): 1. unbind inverts. 2. unit phasor. 3. K sweep.
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
ANCHOR_NAME = "patternb_capacity_K_sweep_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
KS = [5, 10, 20] if RUN_MODE == "smoke" else [5, 10, 20, 30, 40, 50]; NB = 200; VOCAB = 500
def _selftest():
    g = np.random.default_rng(0); a = phasor(64,1,g)[0]; b = phasor(64,1,g)[0]
    assert np.allclose((a*b)*np.conj(a), b, atol=1e-4), "unbind inverts"
    assert np.allclose(np.abs(a),1.0,atol=1e-5), "unit phasor"
    assert len(KS) >= 2, "K sweep"
    print("[selftest] PASS: patternb-capacity-K", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); cache = phasor(N, VOCAB, g); by = {}; klim = 0
    for K in KS:
        roles = phasor(N, K, g); ok = 0
        for _ in range(NB):
            fid = g.choice(VOCAB, K, replace=False); bundle = np.sum([roles[i]*cache[fid[i]] for i in range(K)], axis=0).astype(np.complex64)
            j = int(g.integers(0, K)); got = int(np.argmax((cache @ np.conj(bundle * np.conj(roles[j]))).real)); ok += int(got == fid[j])
        f1 = ok / NB; by["K%d" % K] = f1
        if f1 >= 0.95: klim = K
        print("  K=%d retrieval_F1=%.3f" % (K, f1), flush=True)
    return {"by": by, "klim": klim}
def verdict(r) -> Tuple[str, str]:
    s = "F1 by K: %s; production K-limit(F1>=0.95)=%d at N=%d" % ({k: round(v,3) for k,v in r["by"].items()}, r["klim"], N)
    if r["klim"] >= 20: return ("HARD_PASS", "HARD_PASS: Pattern B holds >=20 items/bundle at F1>=0.95 (N=%d) -- ample compositional capacity. " % N + s)
    if r["klim"] >= 10: return ("MIDDLE_BAND", "MIDDLE_BAND: K-limit 10-20. " + s)
    return ("HARD_FAIL", "HARD_FAIL: K-limit <10. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
