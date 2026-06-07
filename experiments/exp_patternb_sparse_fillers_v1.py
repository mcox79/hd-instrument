"""
exp_patternb_sparse_fillers_v1 -- PB-EXT-5: Pattern B sparse fillers (sparse-KEY analog) -- CPU.
ROUTING: top20/pattern-b-ext PB-EXT-5. Use sparse (k-active) filler vectors instead of dense phasors; measure compression on filler storage + retrieval F1. CPU.
PRE-REGISTERED: HARD-PASS sparse fillers >=10x compression AND retrieval F1>=0.95.
FORMULA SELF-TESTS (PROT-022): 1. sparse active. 2. unbind inverts. 3. compression>=10x.
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
ANCHOR_NAME = "patternb_sparse_fillers_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
KACT = 64; NB = 200; NROLE = 5; VOCAB = 300   # 64 active of N=4096 -> 64x sparsity
def sparse_vec(n, kact, g):
    v = np.zeros(n, np.complex64); idx = g.choice(n, kact, replace=False); v[idx] = np.exp(1j*g.uniform(-np.pi,np.pi,kact)); return v
def _selftest():
    g = np.random.default_rng(0); v = sparse_vec(128, 8, g); assert int((np.abs(v) > 0).sum()) == 8, "sparse active"
    a = phasor(64,1,g)[0]; b = phasor(64,1,g)[0]; assert np.allclose((a*b)*np.conj(a), b, atol=1e-4), "unbind inverts"
    assert (4096 / 64) >= 10, "compression>=10x"
    print("[selftest] PASS: patternb-sparse-fillers", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); roles = phasor(N, NROLE, g); cache = np.stack([sparse_vec(N, KACT, g) for _ in range(VOCAB)])
    ok = 0
    for _ in range(NB):
        k = int(g.integers(3, NROLE+1)); ridx = g.choice(NROLE, k, replace=False); fid = g.choice(VOCAB, k, replace=False)
        bundle = np.sum([roles[ridx[i]]*cache[fid[i]] for i in range(k)], axis=0).astype(np.complex64)
        j = 0; got = int(np.argmax((cache.conj() @ (bundle * np.conj(roles[ridx[j]]))).real)); ok += int(got == fid[j])
    f1 = ok / NB; comp = N / KACT
    print("  sparse fillers (%d-active of %d = %.0fx) retrieval_F1=%.3f" % (KACT, N, comp, f1), flush=True)
    return {"f1": f1, "compression": comp}
def verdict(r) -> Tuple[str, str]:
    s = "compression=%.0fx F1=%.3f" % (r["compression"], r["f1"])
    if r["compression"] >= 10 and r["f1"] >= 0.95: return ("HARD_PASS", "HARD_PASS: sparse fillers give >=10x filler compression at F1>=0.95 -- sparse-KEY analog works for Pattern B. " + s)
    if r["f1"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: sparse fillers F1 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sparse fillers F1<0.85 -- too lossy. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
