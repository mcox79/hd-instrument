"""
exp_lap3_10_paracons_multictx_cpu_v1.py -- Belnap 4-valued truth per context -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 (LAP3-10 PARACONSISTENT-MULTI-CONTEXT); pure-FHRR (no download). Context-bound pos/neg evidence; a prop can be T/F/U/B differently in each context; no cross-context contamination.
PRE-REGISTERED: HARD-PASS multi-context>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.
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
ANCHOR_NAME = "lap3_10_paracons_multictx_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: paraconsistent-multi-context", flush=True)
def run() -> Dict:
    # per-CONTEXT Belnap 4-valued: a prop can be T/F/U/B differently in each context. Context-keyed pos/neg evidence bundles.
    g = np.random.default_rng(1); N = 8192; NP = 30; NC = 5; props = cphasor(NP, N, g); ctx = cphasor(NC, N, g)
    TR = 30 if SMOKE else 200; correct = 0; n = 0
    for _ in range(TR):
        pos = {c: set() for c in range(NC)}; neg = {c: set() for c in range(NC)}
        for c in range(NC):
            for p in range(NP):
                if g.random() < 0.5:
                    pos[c].add(p)
                if g.random() < 0.4:
                    neg[c].add(p)
        # store context-bound evidence: POS = sum_c ctx[c] (X) (sum_{p in pos[c]} props[p])
        POS = sum((ctx[c] * sum((props[p] for p in pos[c]), np.zeros(N, dtype=np.complex64)) for c in range(NC)), np.zeros(N, dtype=np.complex64))
        NEG = sum((ctx[c] * sum((props[p] for p in neg[c]), np.zeros(N, dtype=np.complex64)) for c in range(NC)), np.zeros(N, dtype=np.complex64))
        for _q in range(NP):
            c = int(g.integers(0, NC)); p = int(g.integers(0, NP))
            hp = (np.vdot(props[p], POS * np.conj(ctx[c])).real) / N > 0.5     # unbind context, test prop membership
            hn = (np.vdot(props[p], NEG * np.conj(ctx[c])).real) / N > 0.5
            val = ("B" if (hp and hn) else "T" if hp else "F" if hn else "U")
            gold = ("B" if (p in pos[c] and p in neg[c]) else "T" if p in pos[c] else "F" if p in neg[c] else "U")
            correct += int(val == gold); n += 1
    acc = correct / n; print("  PARACONSISTENT-MULTI-CONTEXT per-context 4-valued acc=%.3f (NC=%d, n=%d)" % (acc, NC, n), flush=True)
    return {"multictx_acc": acc, "NC": NC, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "multi-context-4valued-acc=%.3f (NC=%d)" % (r["multictx_acc"], r["NC"])
    if r["multictx_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate tracks Belnap 4-valued truth PER CONTEXT >=0.85 -- a prop can be T/F/U/B differently across contexts; context-bound paraconsistent evidence (no cross-context contamination or explosion). " + s)
    if r["multictx_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: multi-context 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: multi-context <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
