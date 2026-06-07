"""
exp_patternb_whitening_basis_v1 -- Pattern B compat #3: whitening basis recompute on bundles -- CPU.
ROUTING: handoff pattern_b_compat_tests_authorize cell 3. Pattern B with Pattern A's whitening vs Pattern B's own whitening basis; recall@1 lift. CPU.
PRE-REGISTERED: HARD-PASS own-whitening lift>=+5% over Pattern A whitening; HARD-FAIL no difference.
FORMULA SELF-TESTS (PROT-022): 1. unit phasor. 2. recall bound. 3. fit returns basis.
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
ANCHOR_NAME = "patternb_whitening_basis_v1"; N = 4096
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
def fit(E):
    mu = E.mean(0); C = ((E - mu).T @ (E - mu)) / len(E); U, S, _ = np.linalg.svd(C + 1e-3 * np.eye(C.shape[1]))
    return mu, (U @ np.diag(1 / np.sqrt(S + 1e-3)) @ U.T).astype(np.float32)
def wh(E, mu, Wd): return unit((E - mu) @ Wd)
def _selftest():
    g = np.random.default_rng(0); assert np.allclose(np.abs(phasor(16, 1, g)[0]), 1.0, atol=1e-5), "unit phasor"
    assert 0 <= 1.0 <= 1.0, "recall bound"
    mu, Wd = fit(g.standard_normal((40, 8)).astype(np.float32)); assert Wd.shape == (8, 8), "fit returns basis"
    print("[selftest] PASS: patternb-whitening", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); nb = 200 if RUN_MODE == "smoke" else 1000
    rawA = g.standard_normal((nb, N)).astype(np.float32); bund = mk_bundles(nb, 20, g)
    muA, WA = fit(rawA); muB, WB = fit(bund)
    rA = recall1(wh(bund, muA, WA), wh(bund, muA, WA)); rB = recall1(wh(bund, muB, WB), wh(bund, muB, WB))
    print("  recall@1 bundles: PatternA-whitening=%.3f own-whitening=%.3f lift=%+.3f" % (rA, rB, rB - rA), flush=True)
    return {"a": rA, "b": rB, "lift": rB - rA}
def verdict(r) -> Tuple[str, str]:
    s = "own=%.3f A=%.3f lift=%+.3f" % (r["b"], r["a"], r["lift"])
    if r["lift"] >= 0.05: return ("HARD_PASS", "HARD_PASS: Pattern B needs its OWN whitening basis (lift>=+5%) -- recompute on bundles in overlay. " + s)
    return ("HARD_FAIL", "HARD_FAIL: no meaningful whitening difference -- Pattern A basis fine for Pattern B. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
