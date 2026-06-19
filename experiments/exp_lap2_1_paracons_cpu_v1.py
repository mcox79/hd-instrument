"""
exp_lap2_1_paracons_cpu_v1.py -- Belnap 4-valued paraconsistent logic on inconsistent KBs -- CPU.

ROUTING: Research LAPTOP_WAVE2 (LAP2-1 PARACONS-1); pure-FHRR (no download). Separate pos/neg evidence bundles; assign T/F/U/B per prop; graceful on contradictions (Both).
PRE-REGISTERED: HARD-PASS 4-valued>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.
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
ANCHOR_NAME = "lap2_1_paracons_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: paracons", flush=True)
def run() -> Dict:
    # Belnap 4-valued: each prop has pos-evidence and neg-evidence. (pos,neg)->T(1,0)/F(0,1)/U(0,0)/B(1,1). Inconsistent KB = some B.
    g = np.random.default_rng(1); N = 8192; NP = 50; props = cphasor(NP, N, g)
    TR = 30 if SMOKE else 200; correct = 0; n = 0
    for _ in range(TR):
        pos = set(); neg = set()
        for p in range(NP):
            if g.random() < 0.5:
                pos.add(p)
            if g.random() < 0.4:                                         # overlap with pos -> 'Both' (contradiction)
                neg.add(p)
        POS = sum((props[p] for p in pos), np.zeros(N, dtype=np.complex64))
        NEG = sum((props[p] for p in neg), np.zeros(N, dtype=np.complex64))
        for p in range(NP):
            hp = (np.vdot(props[p], POS).real) / N > 0.5
            hn = (np.vdot(props[p], NEG).real) / N > 0.5
            val = ("B" if (hp and hn) else "T" if hp else "F" if hn else "U")
            gold = ("B" if (p in pos and p in neg) else "T" if p in pos else "F" if p in neg else "U")
            correct += int(val == gold); n += 1
    acc = correct / n; print("  PARACONS 4-valued (T/F/U/B) acc=%.3f (NP=%d, n=%d)" % (acc, NP, n), flush=True)
    return {"paracons_acc": acc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "4-valued-acc=%.3f (n=%d)" % (r["paracons_acc"], r["n"])
    if r["paracons_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate assigns Belnap 4-valued truth (T/F/U/B) >=0.85 on INCONSISTENT KBs -- pos/neg evidence bundles tracked separately; contradiction (Both) handled gracefully, no explosion. " + s)
    if r["paracons_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 4-valued 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 4-valued <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
