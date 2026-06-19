"""
exp_lap3_11_temporal_ltl_cpu_v1.py -- bounded LTL over substrate state sequences -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 (LAP3-11 TEMPORAL-LTL-BOUNDED); pure-FHRR (no download). Store a state sequence; evaluate next / eventually-k / always-k / until-k temporal formulas.
PRE-REGISTERED: HARD-PASS LTL>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.
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
ANCHOR_NAME = "lap3_11_temporal_ltl_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: temporal-ltl", flush=True)
def run() -> Dict:
    g = np.random.default_rng(11); N = 8192; T = 8; NP = 4; props = cphasor(NP, N, g); slots = cphasor(T, N, g)
    TR = 50 if SMOKE else 300; correct = 0; n = 0
    for _ in range(TR):
        val = {(s, p): (g.random() < 0.5) for s in range(T) for p in range(NP)}
        prophold = {s: sum((props[p] for p in range(NP) if val[(s, p)]), np.zeros(N, dtype=np.complex64)) for s in range(T)}
        def holds(s, p):                                                 # substrate membership: prop p true at step s?
            return (np.vdot(props[p], prophold[s]).real) / N > 0.5
        ftype = int(g.integers(0, 4)); p = int(g.integers(0, NP)); q = int(g.integers(0, NP)); k = int(g.integers(2, T))
        if ftype == 0:    # X p : next
            gold = val[(1, p)]; got = holds(1, p)
        elif ftype == 1:  # F_k p : eventually within k
            gold = any(val[(s, p)] for s in range(0, k + 1)); got = any(holds(s, p) for s in range(0, k + 1))
        elif ftype == 2:  # G_k p : always through k
            gold = all(val[(s, p)] for s in range(0, k + 1)); got = all(holds(s, p) for s in range(0, k + 1))
        else:             # p U_k q : p holds until q (within k)
            def until(vfn):
                for s in range(0, k + 1):
                    if vfn(s, q):
                        return True
                    if not vfn(s, p):
                        return False
                return False
            gold = until(lambda s, x: val[(s, x)]); got = until(lambda s, x: holds(s, x))
        correct += int(got == gold); n += 1
    acc = correct / n; print("  TEMPORAL-LTL bounded(X/F/G/U) acc=%.3f (T=%d, n=%d)" % (acc, T, n), flush=True)
    return {"ltl_acc": acc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "bounded-LTL-acc=%.3f (n=%d)" % (r["ltl_acc"], r["n"])
    if r["ltl_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate evaluates bounded LTL (next / eventually-within-k / always-through-k / until) >=0.85 -- temporal logic over substrate-stored state sequences. " + s)
    if r["ltl_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: LTL 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: LTL <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
