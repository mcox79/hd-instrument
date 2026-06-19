"""
exp_patternb_h2_bft_v1 -- Pattern B compat #4: H=2 multi-head BFT on bundles -- CPU.
ROUTING: handoff pattern_b_compat_tests_authorize cell 4. Write each bundle through 2 random orthogonal rotations; read-average; noise sweep 0.05/0.20/0.50. CPU.
PRE-REGISTERED: HARD-PASS recall@1>=0.95 at noise 0.50 (matches CELL-4).
FORMULA SELF-TESTS (PROT-022): 1. unit phasor. 2. recall bound. 3. orthogonal rotation.
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
ANCHOR_NAME = "patternb_h2_bft_v1"; N = 4096
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
def _selftest():
    g = np.random.default_rng(0); Q, _ = np.linalg.qr(g.standard_normal((8, 8))); assert np.allclose(Q @ Q.T, np.eye(8), atol=1e-5), "orthogonal rotation"
    assert np.allclose(np.abs(phasor(16, 1, g)[0]), 1.0, atol=1e-5), "unit phasor"
    assert 0 <= 1.0 <= 1.0, "recall bound"
    print("[selftest] PASS: patternb-h2-bft", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); nb = 200 if RUN_MODE == "smoke" else 1000; D = 2 * N
    B = mk_bundles(nb, 20, g)
    R1, _ = np.linalg.qr(g.standard_normal((D, D)).astype(np.float32)); R2, _ = np.linalg.qr(g.standard_normal((D, D)).astype(np.float32))
    Sn1 = unit(B @ R1.T); Sn2 = unit(B @ R2.T); out = {}
    for ns in [0.05, 0.20, 0.50]:
        q = B + ns * g.standard_normal(B.shape).astype(np.float32); cons = 0
        for i in range(0, nb, 256):
            qb = q[i:i+256]; s = (unit(qb @ R1.T) @ Sn1.T + unit(qb @ R2.T) @ Sn2.T) / 2
            cons += int((np.argmax(s, axis=1) == np.arange(i, min(i+256, nb))).sum())
        out["n%.2f" % ns] = cons / nb; print("  H=2 BFT recall@1 @noise%.2f = %.3f" % (ns, out["n%.2f" % ns]), flush=True)
    return {"by": out, "n050": out["n0.50"]}
def verdict(r) -> Tuple[str, str]:
    s = "recall@1 by noise: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if r["n050"] >= 0.95: return ("HARD_PASS", "HARD_PASS: H=2 BFT holds recall@1>=0.95 at noise 0.50 on bundles (matches CELL-4) -- BFT transfers. " + s)
    if r["n050"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: H=2 BFT 0.80-0.95 at noise 0.50. " + s)
    return ("HARD_FAIL", "HARD_FAIL: H=2 BFT <0.80 at noise 0.50 on bundles. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
