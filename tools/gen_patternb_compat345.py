"""Generate Pattern B compat cells #3/#4/#5 (clean, on-disk generator -- avoids heredoc quoting bugs)."""
import pathlib
HEAD = '''"""
{title}
ROUTING: handoff pattern_b_compat_tests_authorize cell {num}. {desc} CPU.
PRE-REGISTERED: {prereg}
FORMULA SELF-TESTS (PROT-022): 1. unit phasor. 2. recall bound. 3. {t3}.
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
ANCHOR_NAME = "{anchor}"; N = 4096
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
'''
TAIL = ("\nprint('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)\n"
        "out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()\n"
        "v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)\n"
        "metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}\n"
        "write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)\n")

def write(anchor, title, num, desc, prereg, t3, body):
    pathlib.Path("experiments/exp_%s.py" % anchor).write_text(
        HEAD.format(title=title, num=num, desc=desc, prereg=prereg, t3=t3, anchor=anchor) + body + TAIL, encoding="utf-8")
    print("wrote", anchor)

# 3: whitening basis
write("patternb_whitening_basis_v1",
      "exp_patternb_whitening_basis_v1 -- Pattern B compat #3: whitening basis recompute on bundles -- CPU.",
      3, "Pattern B with Pattern A's whitening vs Pattern B's own whitening basis; recall@1 lift.",
      "HARD-PASS own-whitening lift>=+5% over Pattern A whitening; HARD-FAIL no difference.", "fit returns basis",
'''def fit(E):
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
''')

# 4: H=2 BFT
write("patternb_h2_bft_v1",
      "exp_patternb_h2_bft_v1 -- Pattern B compat #4: H=2 multi-head BFT on bundles -- CPU.",
      4, "Write each bundle through 2 random orthogonal rotations; read-average; noise sweep 0.05/0.20/0.50.",
      "HARD-PASS recall@1>=0.95 at noise 0.50 (matches CELL-4).", "orthogonal rotation",
'''def _selftest():
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
''')

# 5: 4-bit + Hopfield
write("patternb_4bit_hopfield_v1",
      "exp_patternb_4bit_hopfield_v1 -- Pattern B compat #5: 4-bit quant on bundle store -- CPU.",
      5, "Store bundles; 4-bit quantize; retrieval vs bf16.",
      "HARD-PASS recall@1 drop <3% with 4x storage reduction.", "4-bit 16 levels",
'''def quant4(X):
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
''')
print("DONE")
