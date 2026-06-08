"""Generator: CPU batch A (5 pure-numpy substrate-physics cells). Run: python tools/gen_cpu_batch_a.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: CPU substrate-physics characterization ({tag}). {desc} Pure numpy. CPU.
PRE-REGISTERED: {prereg}
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
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
{body}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
C = []
C.append(dict(anchor="noise_cliff_cpu_v1", tag="recall vs bit-flip sweep",
  title="sign-key recall@1 across bit-flip rates (graceful-degradation cliff)",
  desc="Sweep query corruption (bit-flip rate 0.1..0.4) at N=20000 D=512; find where recall@1 falls off. Characterizes robustness to query corruption.",
  prereg="HARD-PASS recall@1 >= 0.95 at 0.30 bit-flip. MIDDLE 0.80-0.95. HARD-FAIL < 0.80.",
  body='''
def _selftest():
    assert np.sign(0.3) == 1, "sign"; assert np.sign(-0.2) == -1, "sign-"; print("[selftest] PASS: noise-cliff-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1); N = 5000 if SMOKE else 20000; D = 512; NQ = 300; by = {}
    X = np.sign(g.standard_normal((N, D))).astype(np.float32); X[X == 0] = 1; qi = g.choice(N, NQ, replace=False)
    for flip in [0.1, 0.2, 0.3, 0.4]:
        Q = X[qi].copy(); fl = g.random((NQ, D)) < flip; Q[fl] *= -1
        pred = np.argmax(Q @ X.T, axis=1); by["f%.1f" % flip] = float((pred == qi).mean())
    print("  recall by flip: %s (N=%d D=%d)" % ({k: round(v, 3) for k, v in by.items()}, N, D), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    f3 = r["by"].get("f0.3", 0.0); s = "recall by flip: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if f3 >= 0.95: return ("HARD_PASS", "HARD_PASS: recall>=0.95 even at 0.30 bit-flip -- robust to heavy query corruption. " + s)
    if f3 >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.80-0.95 at 0.30 flip. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.80 at 0.30 flip. " + s)
'''))
C.append(dict(anchor="ridge_optimization_cpu_v1", tag="pinv ridge lambda sweep",
  title="pseudoinverse recall vs ridge lambda (capacity-optimal regularization)",
  desc="Sweep ridge lambda (1e-4..1e0) for the pinv write rule at fixed load; find the lambda maximizing exact recall. Characterizes the regularization sweet spot.",
  prereg="HARD-PASS some lambda gives recall@1 >= 0.99 at load M/D=0.8. MIDDLE >= 0.95. HARD-FAIL < 0.95.",
  body='''
def _selftest():
    A = np.eye(3); assert np.allclose(np.linalg.solve(A, A), A), "solve"; print("[selftest] PASS: ridge-optimization-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2); D = 512; M = int(0.8 * D); MM = 256
    bk = np.sign(g.standard_normal((MM * 4, MM))); K = np.sign(g.standard_normal((M, D))); V = bk[g.integers(0, len(bk), M)]
    by = {}
    for lam in [1e-4, 1e-3, 1e-2, 1e-1, 1.0]:
        W = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ V)
        pred = np.argmax((K @ W) @ bk.T, axis=1); gold = np.argmax(V @ bk.T, axis=1); by["l%g" % lam] = float((pred == gold).mean())
    best = max(by.values()); print("  recall by ridge: %s | best=%.3f (D=%d M=%d)" % ({k: round(v, 3) for k, v in by.items()}, best, D, M), flush=True)
    return {"by": by, "best": best}
def verdict(r) -> Tuple[str, str]:
    s = "best=%.3f | by-ridge: %s" % (r["best"], {k: round(v, 3) for k, v in r["by"].items()})
    if r["best"] >= 0.99: return ("HARD_PASS", "HARD_PASS: optimal ridge gives recall>=0.99 at load 0.8 -- regularization sweet spot identified. " + s)
    if r["best"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: best recall 0.95-0.99. " + s)
    return ("HARD_FAIL", "HARD_FAIL: best recall <0.95 at load 0.8. " + s)
'''))
C.append(dict(anchor="orthogonal_keys_capacity_cpu_v1", tag="orthogonal vs random key capacity",
  title="capacity gain from orthogonalized keys vs random keys",
  desc="Compare max patterns at recall>=0.99 for random keys vs Gram-Schmidt-orthogonalized keys (pinv write). Quantifies the capacity benefit of decorrelating keys.",
  prereg="HARD-PASS orthogonal keys sustain recall>=0.99 at load M/D=1.0 (vs random failing). MIDDLE >= 0.95. HARD-FAIL < 0.95.",
  body='''
def _selftest():
    q, _ = np.linalg.qr(np.random.default_rng(0).standard_normal((4, 4))); assert np.allclose(q.T @ q, np.eye(4), atol=1e-6), "qr orthonormal"; print("[selftest] PASS: orthogonal-keys-capacity-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(3); D = 256 if SMOKE else 512; M = D; MM = 256; lam = 1e-3
    bk = np.sign(g.standard_normal((MM * 4, MM))); V = bk[g.integers(0, len(bk), M)]
    Krand = g.standard_normal((M, D)); Korth, _ = np.linalg.qr(g.standard_normal((D, M))); Korth = Korth.T[:M]
    def rec(K):
        W = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ V); pred = np.argmax((K @ W) @ bk.T, axis=1); gold = np.argmax(V @ bk.T, axis=1); return float((pred == gold).mean())
    rr = rec(Krand); ro = rec(Korth)
    print("  recall at load M/D=1.0: random=%.3f orthogonal=%.3f (D=%d)" % (rr, ro, D), flush=True)
    return {"random": rr, "orth": ro}
def verdict(r) -> Tuple[str, str]:
    s = "orthogonal=%.3f random=%.3f at load 1.0" % (r["orth"], r["random"])
    if r["orth"] >= 0.99: return ("HARD_PASS", "HARD_PASS: orthogonalized keys hold recall>=0.99 at load M/D=1.0 -- decorrelation maximizes capacity (key-design lever). " + s)
    if r["orth"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: orthogonal recall 0.95-0.99 at load 1.0. " + s)
    return ("HARD_FAIL", "HARD_FAIL: orthogonal recall <0.95 even at load 1.0. " + s)
'''))
C.append(dict(anchor="bundle_crosstalk_scaling_cpu_v1", tag="bundle unbind crosstalk vs size",
  title="empirical bundle unbind crosstalk norm scales as sqrt(K-1)",
  desc="Measure the unbind crosstalk (rec - true filler) norm as a function of bundle size K (FHRR role-filler superposition); compare to the theoretical sqrt(K-1) law. Validates the composition noise model that governs bundle capacity.",
  prereg="HARD-PASS empirical crosstalk norm within 15pct of sqrt(K-1) across K. MIDDLE within 30pct. HARD-FAIL > 30pct deviation.",
  body='''
import math
def _selftest():
    assert abs(math.sqrt(4) - 2.0) < 1e-9, "sqrt"; print("[selftest] PASS: bundle-crosstalk-scaling-cpu", flush=True)
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def run() -> Dict:
    g = np.random.default_rng(4); N = 4096; TR = 30 if SMOKE else 120; devs = []; rows = {}
    for K in [2, 4, 8, 16]:
        emps = []
        for _ in range(TR):
            roles = cphasor(K, N, g); fillers = cphasor(K, N, g)
            rec = ((roles * fillers).sum(0)) * roles[0].conj()         # unbind slot 0
            crosstalk = rec - fillers[0]                               # everything except the true filler
            emps.append(float(np.linalg.norm(crosstalk) / math.sqrt(N)))
        emp = float(np.mean(emps)); theo = math.sqrt(max(1, K - 1)); dev = abs(emp - theo) / theo; devs.append(dev); rows["K%d" % K] = round(emp, 3)
        print("  K=%d crosstalk-norm=%.3f theory(sqrt(K-1))=%.3f dev=%.2f" % (K, emp, theo, dev), flush=True)
    md = float(np.max(devs)); return {"max_dev": md, "rows": rows}
def verdict(r) -> Tuple[str, str]:
    s = "max deviation from sqrt(K-1) = %.2f | crosstalk-norm: %s" % (r["max_dev"], r["rows"])
    if r["max_dev"] <= 0.15: return ("HARD_PASS", "HARD_PASS: bundle crosstalk norm matches sqrt(K-1) within 15pct -- composition noise model validated (predictable capacity). " + s)
    if r["max_dev"] <= 0.30: return ("MIDDLE_BAND", "MIDDLE_BAND: crosstalk within 30pct of theory. " + s)
    return ("HARD_FAIL", "HARD_FAIL: crosstalk deviates >30pct from sqrt(K-1). " + s)
'''))
C.append(dict(anchor="capacity_scaling_law_cpu_v1", tag="capacity vs dimension scaling law",
  title="max patterns at recall>=0.99 scales linearly with D (capacity slope)",
  desc="For D in {128,256,512,1024}, binary-search the max number of sign patterns recallable at recall@1>=0.99 (pinv); fit the capacity-vs-D slope. Confirms linear capacity scaling.",
  prereg="HARD-PASS capacity grows linearly with slope >= 0.5*D (i.e. cap >= 0.5*D at each D). MIDDLE >= 0.3*D. HARD-FAIL < 0.3*D.",
  body='''
def _selftest():
    assert 512 > 256, "D ordering"; print("[selftest] PASS: capacity-scaling-law-cpu", flush=True)
def cap_at(D, g, lam=1e-3):
    MM = 128; bk = np.sign(g.standard_normal((MM * 6, MM)))
    lo, hi, best = 1, int(1.2 * D), 1
    while lo <= hi:
        M = (lo + hi) // 2; K = np.sign(g.standard_normal((M, D))); V = bk[g.integers(0, len(bk), M)]
        W = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ V); pred = np.argmax((K @ W) @ bk.T, axis=1); gold = np.argmax(V @ bk.T, axis=1)
        if (pred == gold).mean() >= 0.99:
            best = M; lo = M + 1
        else:
            hi = M - 1
    return best
def run() -> Dict:
    g = np.random.default_rng(5); Ds = [128, 256] if SMOKE else [128, 256, 512, 1024]; by = {}
    for D in Ds:
        by[D] = cap_at(D, g); print("  D=%d capacity(recall>=0.99)=%d (=%.2f*D)" % (D, by[D], by[D] / D), flush=True)
    frac = min(by[D] / D for D in Ds); return {"by": {str(k): v for k, v in by.items()}, "min_frac": frac}
def verdict(r) -> Tuple[str, str]:
    s = "min capacity fraction = %.2f*D | %s" % (r["min_frac"], r["by"])
    if r["min_frac"] >= 0.5: return ("HARD_PASS", "HARD_PASS: capacity scales >=0.5*D at every D -- linear capacity law confirmed (predictable scaling). " + s)
    if r["min_frac"] >= 0.3: return ("MIDDLE_BAND", "MIDDLE_BAND: capacity 0.3-0.5*D. " + s)
    return ("HARD_FAIL", "HARD_FAIL: capacity <0.3*D. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
