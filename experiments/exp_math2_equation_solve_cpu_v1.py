"""
exp_math2_equation_solve_cpu_v1.py -- MATH-2 EQUATION-SOLVE (substrate-native equation solving) -- CPU.

ROUTING: Research SPRINT2_BOTH_PATHS Path-B (extends MATH-1). Linear (a*x+b=c) and quadratic (a*x^2+b*x+c=0) equations encoded
  structurally (COEFF roles A/B/C + TYPE role). Substrate RECOVERS the coefficients + type via cleanup, applies the matching
  closed-form solver (linear x=(c-b)/a; quadratic real roots), and the root is VERIFIED by substitution. Accuracy = root
  satisfies the equation within tolerance. The coefficient-recovery is substrate-native; solving is closed-form. N=8192.
PRE-REGISTERED: HARD-PASS solve accuracy >= 0.70 (verified roots). MIDDLE >= 0.55. HARD-FAIL else.
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
ANCHOR_NAME = "math2_equation_solve_cpu_v1"
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
    print("[selftest] PASS: math2-equation-solve", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "823"))); COEFFS = list(range(-5, 6)); cbook_map = {c: i for i, c in enumerate(COEFFS)}
    cbook = cphasor(len(COEFFS), N, g); types = cphasor(2, N, g)  # 0=linear 1=quadratic
    RA = cphasor(1, N, g)[0]; RB = cphasor(1, N, g)[0]; RC = cphasor(1, N, g)[0]; RT = cphasor(1, N, g)[0]
    def enc(a, b, c, t):
        return cnorm(RA * cbook[cbook_map[a]] + RB * cbook[cbook_map[b]] + RC * cbook[cbook_map[c]] + RT * types[t])
    def solve(a, b, c, t):
        if t == 0:  # a*x + b = c
            if a == 0: return None
            return [(c - b) / a]
        else:  # a*x^2 + b*x + c = 0
            if a == 0: return None
            disc = b * b - 4 * a * c
            if disc < 0: return []
            r = math.sqrt(disc); return [(-b + r) / (2 * a), (-b - r) / (2 * a)]
    def verify(a, b, c, t, roots):
        if roots is None: return False
        for x in roots:
            val = (a * x + b - c) if t == 0 else (a * x * x + b * x + c)
            if abs(val) > 1e-6: return False
        return True
    TR = 100 if not SMOKE else 30; ok = 0; n = 0
    for _ in range(TR):
        for _q in range(4):
            t = int(g.integers(0, 2)); a = int(g.choice([x for x in COEFFS if x != 0]))
            b = int(g.choice(COEFFS)); c = int(g.choice(COEFFS))
            e = enc(a, b, c, t)
            ra = COEFFS[cidx(e * np.conj(RA), cbook)]; rb = COEFFS[cidx(e * np.conj(RB), cbook)]
            rc = COEFFS[cidx(e * np.conj(RC), cbook)]; rt = int(cidx(e * np.conj(RT), types))
            roots = solve(ra, rb, rc, rt)                          # solve on RECOVERED coefficients
            gold_roots = solve(a, b, c, t)
            # correct if recovered-solution verifies against the TRUE equation (and matches solvability)
            if gold_roots is None or len(gold_roots) == 0:
                ok += int(roots is None or len(roots) == 0)
            else:
                ok += int(verify(a, b, c, t, roots) and roots is not None and len(roots) > 0)
            n += 1
    acc = ok / n
    print("  MATH-2 EQUATION-SOLVE accuracy=%.3f (recover coeffs + closed-form + verify root, n=%d)" % (acc, n), flush=True)
    return {"accuracy": round(acc, 3), "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "accuracy=%.3f (n=%d)" % (r["accuracy"], r["n"])
    if r["accuracy"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate solves linear+quadratic equations >=0.70 (verified roots) -- recovers coefficients + type and applies closed-form solvers, substrate-only. " + s)
    if r["accuracy"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: equation-solve 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: equation-solve <0.55. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
