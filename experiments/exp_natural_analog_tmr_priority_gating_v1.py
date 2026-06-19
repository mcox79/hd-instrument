"""
exp_natural_analog_tmr_priority_gating_v1.py -- priority-gated sleep-defrag aggregation boosts flagged-binding recall -- CPU.

ROUTING: natural_analog Analog 1 (HIPPOCAMPAL TMR). 20 of 100 facts are customer-flagged high-priority; sleep-defrag aggregation weights them higher (TMR analog). Measure recall@1 of priority vs unflagged bindings under crosstalk. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS priority bindings recall >= 1.5x unflagged. MIDDLE 1.2-1.5x. HARD-FAIL < 1.2x.
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
ANCHOR_NAME = "natural_analog_tmr_priority_gating_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def phasor(m, d, g):
    return np.exp(1j * g.uniform(-np.pi, np.pi, (m, d))).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    g = np.random.default_rng(0); b = phasor(5, 16, g); assert cidx(b[2], b) == 2, "cleanup self"
    assert np.allclose(b[0]*b[1]*np.conj(b[1]), b[0], atol=1e-4), "bind inverse"
    assert 1.5 > 1.2, "ratio order"
    print("[selftest] PASS: tmr-priority-gating", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1); D = 256; N = 60 if SMOKE else 100; NP = N // 5; W_PRI = 3.0
    book = phasor(N, D, g); roles = phasor(N, D, g); pri = set(range(NP))
    B = np.sum([(W_PRI if i in pri else 1.0) * roles[i] * book[i] for i in range(N)], axis=0)
    rp = np.mean([cidx(B*np.conj(roles[i]), book) == i for i in pri])
    ru = np.mean([cidx(B*np.conj(roles[i]), book) == i for i in range(NP, N)])
    print("  priority recall=%.3f unflagged recall=%.3f (ratio=%.2f, w=%.1f)" % (rp, ru, rp/(ru+1e-9), W_PRI), flush=True)
    return {"pri": float(rp), "unflagged": float(ru), "ratio": float(rp/(ru+1e-9))}
def verdict(r) -> Tuple[str, str]:
    s = "priority=%.3f unflagged=%.3f ratio=%.2f" % (r["pri"], r["unflagged"], r["ratio"])
    if r["ratio"] >= 1.5: return ("HARD_PASS", "HARD_PASS: TMR priority gating gives flagged bindings >=1.5x recall -- customer-important facts protected in defrag. " + s)
    if r["ratio"] >= 1.2: return ("MIDDLE_BAND", "MIDDLE_BAND: priority ratio 1.2-1.5x. " + s)
    return ("HARD_FAIL", "HARD_FAIL: priority gating ratio <1.2x. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
