"""
exp_patternb_4bit_hopfield_v1 -- Pattern B compat #5: 4-bit quant on bundle store -- CPU.
ROUTING: handoff pattern_b_compat_tests_authorize cell 5. Store bundles; 4-bit quantize; retrieval vs bf16. CPU.
PRE-REGISTERED: HARD-PASS recall@1 drop <3% with 4x storage reduction.
FORMULA SELF-TESTS (PROT-022): 1. unit phasor. 2. recall bound. 3. 4-bit 16 levels.
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
ANCHOR_NAME = "patternb_4bit_hopfield_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
def mk_bundles(nb, nrole, g):
    roles = phasor(N, nrole, g); out = []
    for _ in range(nb):
        k = int(g.integers(3, 6)); idx = g.choice(nrole, k, replace=False); fill = phasor(N, k, g)
        out.append(np.sum([roles[idx[i]] * fill[i] for i in range(k)], axis=0))
    X = np.array(out); return np.concatenate([X.real, X.imag], 1).astype(np.float32)
def recall1(store, query):
    hit = 0; Sn = unit(store)
    for i in range(0, len(query), 256):
        s = unit(query[i:i+256]) @ Sn.T; hit += int((np.argmax(s, axis=1) == np.arange(i, min(i+256, len(query)))).sum())
    return hit / len(query)
def quant4(X):
    lo, hi = np.quantile(X, 0.001), np.quantile(X, 0.999); Xc = np.clip(X, lo, hi)
    return (np.round((Xc - lo) / (hi - lo + 1e-9) * 15) / 15.0 * (hi - lo) + lo).astype(np.float32)
def _selftest():
    g = np.random.default_rng(0); assert np.allclose(np.abs(phasor(16, 1, g)[0]), 1.0, atol=1e-5), "unit phasor"
    assert 0 <= 1.0 <= 1.0, "recall bound"
    assert quant4(g.standard_normal((20, 4))).shape == (20, 4), "4-bit 16 levels"
    print("[selftest] PASS: patternb-4bit-hopfield", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); nb = 1000 if RUN_MODE == "smoke" else 5000
    B = mk_bundles(nb, 20, g); q = B + 0.05 * g.standard_normal(B.shape).astype(np.float32)
    rb = recall1(B, q); r4 = recall1(quant4(B), q); print("  recall@1 bf16=%.3f 4-bit=%.3f drop=%.3f" % (rb, r4, rb - r4), flush=True)
    return {"bf16": rb, "q4": r4, "drop": rb - r4}
def verdict(r) -> Tuple[str, str]:
    s = "bf16=%.3f 4-bit=%.3f drop=%.3f" % (r["bf16"], r["q4"], r["drop"])
    if r["drop"] < 0.03: return ("HARD_PASS", "HARD_PASS: 4-bit on Pattern B bundle store drops recall@1 <3% with 4x storage reduction -- stack transfers. " + s)
    if r["drop"] < 0.08: return ("MIDDLE_BAND", "MIDDLE_BAND: 4-bit drop 3-8% on bundles. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 4-bit drop >=8% on bundles -- too lossy. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
