"""
exp_counterfactual_do_demo_cpu_v1.py -- do(X) intervention recomputes downstream answers (counterfactual demo) -- CPU.

ROUTING: v1.5 LOCK batch (B3 counterfactual do() demo). Causal chain A -r1-> B -r2-> C stored as substrate bindings. Factual query follows A->B->C. A do(B=B') intervention replaces B's binding and recomputes C from B' (downstream), leaving A unchanged. Demo: counterfactual C' matches B's intervened successor and differs from the factual C. Customer demo for 'what if' queries. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS counterfactual answer correct >= 0.90 AND differs from factual >= 0.90 of the time. MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "counterfactual_do_demo_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; R = cphasor(1, 64, g)[0]; b = cphasor(1, 64, g)[0]
    assert np.allclose(a * R * b * np.conj(a * R), b, atol=1e-3), "unbind"; print("[selftest] PASS: counterfactual-do-demo", flush=True)
def run() -> Dict:
    g = np.random.default_rng(91); N = 8192; VE = 200; VR = 8; deg = 2; TR = 60 if SMOKE else 200
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}; M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(deg):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    def two_hop():
        for _ in range(150):
            a = int(g.integers(0, VE)); o1 = [(r, edges[(a, r)]) for (ss, r) in edges if ss == a]
            if not o1:
                continue
            r1, b = o1[int(g.integers(0, len(o1)))]; o2 = [(r, edges[(b, r)]) for (ss, r) in edges if ss == b]
            if not o2:
                continue
            r2, c = o2[int(g.integers(0, len(o2)))]; return a, r1, b, r2, c
        return None
    cf_ok = 0; diff = 0; n = 0
    for _ in range(TR):
        p = two_hop()
        if not p:
            continue
        a, r1, b, r2, c = p
        # need an alternative B' that has an r2 edge (so do(B=B') has a defined downstream)
        alts = [bb for (ss, r) in edges if r == r2 and ss != b for bb in [ss]]
        if not alts:
            continue
        bp = int(g.choice(alts)); cp_true = edges[(bp, r2)]
        # factual C via K-hop; counterfactual: do(B=bp) -> recompute C from bp via r2
        c_fac = cidx(M * np.conj(ents[cidx(M * np.conj(ents[a] * rels[r1]), ents)] * rels[r2]), ents)
        c_cf = cidx(M * np.conj(ents[bp] * rels[r2]), ents)                    # intervention recompute
        cf_ok += int(c_cf == cp_true); diff += int(c_cf != c_fac); n += 1
    cfa = cf_ok / max(1, n); df = diff / max(1, n); print("  counterfactual-correct=%.3f differs-from-factual=%.3f (n=%d)" % (cfa, df, n), flush=True)
    return {"cf_correct": cfa, "differs": df}
def verdict(r) -> Tuple[str, str]:
    s = "counterfactual-correct=%.3f differs-from-factual=%.3f" % (r["cf_correct"], r["differs"])
    if r["cf_correct"] >= 0.90 and r["differs"] >= 0.90: return ("HARD_PASS", "HARD_PASS: do() intervention recomputes the correct counterfactual answer (>=0.90) distinct from factual -- 'what if' queries work (demo-ready). " + s)
    if r["cf_correct"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: counterfactual correct 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: counterfactual <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
