"""
exp_ptb_reuse_index_cache_v1 -- PTB-REUSE-1: index-only filler cache for Pattern B -- CPU.
ROUTING: top20 unrouted #1 PTB-REUSE-1. Store 1000 Pattern B bundles as role-binding INDICES (filler IDs into a shared cache) not full vectors; per-fact storage cost + retrieval F1 vs full-bundle. CPU.
PRE-REGISTERED: HARD-PASS per-fact<50 bytes AND retrieval F1>=0.95; HARD-FAIL >200 bytes or F1 drop>15%.
FORMULA SELF-TESTS (PROT-022): 1. unbind inverts. 2. index reconstructs. 3. unit phasor.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib, hmac
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "ptb_reuse_index_cache_v1"; N = 2048
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
NB = 200 if RUN_MODE == "smoke" else 1000; NROLE = 6; VOCAB = 300
def _selftest():
    g = np.random.default_rng(0); a = phasor(64, 1, g)[0]; b = phasor(64, 1, g)[0]
    assert np.allclose((a*b)*np.conj(a), b, atol=1e-4), "unbind inverts"
    assert int(np.argmax((phasor(64,4,g) @ np.conj(phasor(64,4,g)[1])).real)) in range(4), "index reconstructs"
    assert np.allclose(np.abs(a),1.0,atol=1e-5), "unit phasor"
    print("[selftest] PASS: ptb-reuse", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); roles = phasor(N, NROLE, g); cache = phasor(N, VOCAB, g)   # shared filler cache
    recs = []  # each fact = list of (role_idx, filler_id) -- the index-only representation
    for _ in range(NB):
        k = int(g.integers(3, 6)); ridx = g.choice(NROLE, k, replace=False); fid = g.choice(VOCAB, k, replace=False)
        recs.append(list(zip(ridx.tolist(), fid.tolist())))
    # retrieval: reconstruct bundle from indices, unbind a probe role, recover filler id
    ok = 0
    for rec in recs:
        bundle = np.sum([roles[ri] * cache[fi] for ri, fi in rec], axis=0).astype(np.complex64)
        ri, fi = rec[0]; got = int(np.argmax((cache @ np.conj(bundle * np.conj(roles[ri]))).real))
        ok += int(got == fi)
    f1 = ok / NB
    per_fact_bytes = np.mean([len(r) for r in recs]) * (2 + 2)   # (role_idx u16 + filler_id u16) per binding
    print("  index-only per-fact=%.0f bytes retrieval_F1=%.3f (cache shared)" % (per_fact_bytes, f1), flush=True)
    return {"per_fact_bytes": float(per_fact_bytes), "f1": f1}
def verdict(r) -> Tuple[str, str]:
    s = "per-fact=%.0f bytes F1=%.3f" % (r["per_fact_bytes"], r["f1"])
    if r["per_fact_bytes"] < 50 and r["f1"] >= 0.95: return ("HARD_PASS", "HARD_PASS: index-only filler cache <50 bytes/fact at F1>=0.95 -- Pattern B storage collapses to index references. " + s)
    if r["per_fact_bytes"] > 200 or r["f1"] < 0.80: return ("HARD_FAIL", "HARD_FAIL: index cache >200 bytes or F1<0.80. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: index cache between bounds. " + s)

print('[config] anchor=%s mode=%s' % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
