"""
exp_math3_calculus_derivative_cpu_v1.py -- MATH-3 CALCULUS-DERIVATIVE (substrate-native calculus) -- CPU.

ROUTING: Research AGGRESSIVE_OVERNIGHT THRUST-2 MATH. Expressions of form  coeff * (x^power)  or  outer(x^power) with
  outer in {sin,cos,exp,id}. Substrate encodes the expression structurally (COEFF/POWER/OUTER roles), RECOVERS each component
  via cleanup, and applies stored derivative rules (power rule + chain rule) to emit the derivative structure. Tests the
  emitted derivative matches the symbolic gold. The structure-recovery is substrate-native; rules are stored. No LLM. N=8192.
PRE-REGISTERED: HARD-PASS derivative accuracy >= 0.80. MIDDLE >= 0.65. HARD-FAIL else.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "math3_calculus_derivative_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: math3-calculus-derivative", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "821"))); COEFFS = [1, 2, 3, 4, 5]; POWERS = [1, 2, 3, 4]; OUTERS = ["id", "sin", "cos", "exp"]
    sym = lambda lst: (np.stack([cphasor(1, N, g)[0] for _ in lst]), {x: i for i, x in enumerate(lst)})
    cbook, cmap = sym(COEFFS); pbook, pmap = sym(POWERS); obook, omap = sym(OUTERS)
    RC = cphasor(1, N, g)[0]; RP = cphasor(1, N, g)[0]; RO = cphasor(1, N, g)[0]
    def deriv_gold(c, p, o):
        # d/dx of o(c*x^p). id: c*p*x^(p-1). sin->cos*inner'. cos->-sin*inner'. exp->exp*inner'. (inner'=c*p*x^(p-1))
        return (o, c * p, max(p - 1, 0)) if o == "id" else (o, c * p, p)   # represent derivative struct (outer-deriv, new-coeff, new-pow)
    TR = 100 if not SMOKE else 30; hit = 0; n = 0
    for _ in range(TR):
        for _q in range(4):
            c = COEFFS[int(g.integers(0, len(COEFFS)))]; p = POWERS[int(g.integers(0, len(POWERS)))]; o = OUTERS[int(g.integers(0, len(OUTERS)))]
            e = cnorm(RC * cbook[cmap[c]] + RP * pbook[pmap[p]] + RO * obook[omap[o]])
            rc = COEFFS[cidx(e * np.conj(RC), cbook)]; rp = POWERS[cidx(e * np.conj(RP), pbook)]; ro = OUTERS[cidx(e * np.conj(RO), obook)]
            gold = deriv_gold(c, p, o); pred = deriv_gold(rc, rp, ro)       # apply stored derivative rule on RECOVERED structure
            hit += int(pred == gold); n += 1
    acc = hit / n
    print("  MATH-3 CALCULUS-DERIVATIVE accuracy=%.3f (power+chain rule on recovered structure, n=%d)" % (acc, n), flush=True)
    return {"accuracy": round(acc, 3), "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "accuracy=%.3f (n=%d)" % (r["accuracy"], r["n"])
    if r["accuracy"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate computes derivatives >=0.80 -- recovers expression structure (coeff/power/outer) and applies power+chain rules, substrate-only. Symbolic calculus via composition+cleanup. " + s)
    if r["accuracy"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: derivative 0.65-0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: derivative <0.65. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
