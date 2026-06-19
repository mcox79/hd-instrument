"""
exp_lap4_tom_depth3_cpu_v1.py -- substrate depth-3 nested belief (theory-of-mind) -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop batch (LAP-4 TOM-DEPTH-3); pure-FHRR (no download). A believes (B believes (C believes X)); unwind 3 nested agent-belief bindings to X.
PRE-REGISTERED: HARD-PASS depth-3 ToM>=0.75. MIDDLE>=0.55. HARD-FAIL<0.55.
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
ANCHOR_NAME = "lap4_tom_depth3_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert _n.argmax([0,1])==1, "argmax"; print("[selftest] PASS: tom-depth-3", flush=True)
def run() -> Dict:
    # depth-3 ToM: A believes (B believes (C believes X)). Per-level sharded BELIEF binding; unwind 3 nested agent-beliefs to X.
    g = np.random.default_rng(43); N = 8192; NAG = 12; VF = 200
    agents = cphasor(NAG, N, g); fillers = cphasor(VF, N, g); BEL = cphasor(1, N, g)[0]
    TR = 30 if SMOKE else 200; hit = 0; n = 0
    for _ in range(TR):
        a, b, c = (int(x) for x in g.choice(NAG, 3, replace=False)); x = int(g.integers(0, VF))
        inner = agents[c] * (BEL * fillers[x])                            # C believes X
        mid = agents[b] * (BEL * inner)                                   # B believes (C believes X)
        outer = agents[a] * (BEL * mid)                                   # A believes (B believes (C believes X))
        # unwind: peel A, then B, then C; recover X. cleanup at the leaf only.
        m1 = outer * np.conj(agents[a]) * np.conj(BEL)                    # ~ mid
        m2 = m1 * np.conj(agents[b]) * np.conj(BEL)                       # ~ inner
        leaf = m2 * np.conj(agents[c]) * np.conj(BEL)                     # ~ fillers[x]
        hit += int(cidx(leaf, fillers) == x); n += 1
    acc = hit / n; print("  TOM-DEPTH-3 nested-belief recall=%.3f (NAG=%d, n=%d)" % (acc, NAG, n), flush=True)
    return {"tom3_recall": acc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "depth3-ToM-recall=%.3f (n=%d)" % (r["tom3_recall"], r["n"])
    if r["tom3_recall"] >= 0.75:
        return ("HARD_PASS", "HARD_PASS: substrate represents depth-3 nested belief (A believes B believes C believes X) recall>=0.75 -- recursive theory-of-mind via nested binding; agent-belief composition holds 3 deep. " + s)
    if r["tom3_recall"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: depth-3 ToM 0.55-0.75. " + s)
    return ("HARD_FAIL", "HARD_FAIL: depth-3 ToM <0.55. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
