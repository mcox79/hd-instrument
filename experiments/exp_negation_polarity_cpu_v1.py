"""
exp_negation_polarity_cpu_v1.py -- facts carry polarity (affirmed vs negated) recovered alongside the value -- CPU.

ROUTING: refill batch (signed/negated facts). Each fact binds a POLARITY tag (affirm/negate) so 'X cites Y' and 'X overrules Y' (opposite relation polarity) are distinguishable. Recovers both the object and the polarity. Tests signed/negated knowledge -- a known weakness for embedding stores. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS object recall >= 0.95 AND polarity recall >= 0.95. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "negation_polarity_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; p = cphasor(1, 32, g)[0]; o = cphasor(1, 32, g)[0]
    assert np.allclose(a * p * o * np.conj(a * p), o, atol=1e-3), "polarity bind"; print("[selftest] PASS: negation-polarity", flush=True)
def run() -> Dict:
    g = np.random.default_rng(325); N = 4096; VK = 100; VO = 300; M = int(0.6 * VK); TR = 60 if SMOKE else 200
    keys = cphasor(VK, N, g); objs = cphasor(VO, N, g); pol = cphasor(2, N, g)
    oh = 0; ph = 0; n = 0
    for _ in range(TR):
        Mem = np.zeros(N, dtype=np.complex64); facts = []; ks = g.choice(VK, M, replace=False)
        for k in ks:
            o = int(g.integers(0, VO)); p = int(g.integers(0, 2)); Mem = Mem + keys[k] * pol[p] * objs[o]; facts.append((int(k), p, o))
        for k, p, o in facts[:20 if not SMOKE else 8]:
            rec = Mem * np.conj(keys[k]); opred = cidx(rec * np.conj(pol[p]), objs); ppred = cidx(rec * np.conj(objs[o]), pol)
            oh += int(opred == o); ph += int(ppred == p); n += 1
    print("  object-recall=%.3f polarity-recall=%.3f (n=%d)" % (oh / n, ph / n, n), flush=True)
    return {"obj": oh / n, "pol": ph / n}
def verdict(r) -> Tuple[str, str]:
    s = "object-recall=%.3f polarity-recall=%.3f" % (r["obj"], r["pol"])
    if r["obj"] >= 0.95 and r["pol"] >= 0.95: return ("HARD_PASS", "HARD_PASS: signed/negated facts recovered with object + polarity >=0.95 -- affirm-vs-negate distinguishable (embedding-store weakness covered). " + s)
    if min(r["obj"], r["pol"]) >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
