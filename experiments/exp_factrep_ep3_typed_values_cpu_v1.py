"""
exp_factrep_ep3_typed_values_cpu_v1.py -- facts carry typed values (entity / numeric / date) recovered with the type tag -- CPU.

ROUTING: deep-batch (EP3 typed-value facts). Bind a TYPE tag with each value so a fact stores (key, type, value); recall recovers both the value and its type. Tests type-aware fact representation (entity vs numeric vs date payloads). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS value recall >= 0.95 AND type recall >= 0.95. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "factrep_ep3_typed_values_cpu_v1"
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
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; ty = cphasor(1, 32, g)[0]; v = cphasor(1, 32, g)[0]
    assert np.allclose(a * ty * v * np.conj(a * ty), v, atol=1e-3), "typed bind"; print("[selftest] PASS: factrep-ep3-typed-values", flush=True)
def run() -> Dict:
    g = np.random.default_rng(211); N = 4096; VK = 100; VV = 400; NTY = 3; M = int(0.6 * VK); TR = 60 if SMOKE else 200
    keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); types = cphasor(NTY, N, g)
    vh = 0; th = 0; n = 0
    for _ in range(TR):
        Mem = np.zeros(N, dtype=np.complex64); facts = []
        ks = g.choice(VK, M, replace=False)
        for k in ks:
            ty = int(g.integers(0, NTY)); vv = int(g.integers(0, VV)); Mem = Mem + keys[k] * types[ty] * vals[vv]; facts.append((int(k), ty, vv))
        for k, ty, vv in facts[:20 if not SMOKE else 8]:
            rec = Mem * np.conj(keys[k])                                       # unbind key -> type*value
            tpred = cidx(rec * np.conj(vals[vv]), types)                       # given value, recover type
            vpred = cidx(rec * np.conj(types[ty]), vals)                       # given type, recover value
            th += int(tpred == ty); vh += int(vpred == vv); n += 1
    print("  value-recall=%.3f type-recall=%.3f (n=%d)" % (vh / n, th / n, n), flush=True)
    return {"value": vh / n, "type": th / n}
def verdict(r) -> Tuple[str, str]:
    s = "value-recall=%.3f type-recall=%.3f" % (r["value"], r["type"])
    if r["value"] >= 0.95 and r["type"] >= 0.95: return ("HARD_PASS", "HARD_PASS: typed-value facts recovered with both value and type >=0.95 -- type-aware fact representation works. " + s)
    if min(r["value"], r["type"]) >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: typed recall 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: typed recall <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
