"""
exp_binding_associativity_cpu_v1.py -- FHRR binding is associative/commutative and deep unbind chains stay exact -- CPU.

ROUTING: CPU substrate-physics characterization (FHRR algebraic properties). Verify FHRR bind is commutative + associative to numerical precision, and that a 4-deep bind/unbind chain recovers the payload via cleanup. Confirms the algebraic substrate for nested structures. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS associativity+commutativity hold to 1e-4 AND 4-deep unbind recall >= 0.95. MIDDLE recall >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "binding_associativity_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 16, g)[0]; b = cphasor(1, 16, g)[0]; assert np.allclose(a * b, b * a), "commute"; print("[selftest] PASS: binding-associativity-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(24); N = 2048; V = 500; TR = 50 if SMOKE else 200
    a = cphasor(1, N, g)[0]; b = cphasor(1, N, g)[0]; c = cphasor(1, N, g)[0]
    assoc = float(np.max(np.abs((a * b) * c - a * (b * c)))); commu = float(np.max(np.abs(a * b - b * a)))
    book = cphasor(V, N, g); hit = 0
    for _ in range(TR):
        roles = cphasor(4, N, g); fi = int(g.integers(0, V))
        bound = roles[0] * roles[1] * roles[2] * roles[3] * book[fi]
        rec = bound * roles[0].conj() * roles[1].conj() * roles[2].conj() * roles[3].conj()
        hit += int(np.argmax((book @ rec.conj()).real) == fi)
    deep = hit / TR
    print("  assoc-err=%.2e commute-err=%.2e | 4-deep unbind recall=%.3f" % (assoc, commu, deep), flush=True)
    return {"assoc": assoc, "commute": commu, "deep_recall": deep}
def verdict(r) -> Tuple[str, str]:
    s = "assoc-err=%.1e commute-err=%.1e 4-deep-recall=%.3f" % (r["assoc"], r["commute"], r["deep_recall"])
    if r["assoc"] <= 1e-4 and r["commute"] <= 1e-4 and r["deep_recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: FHRR binding is associative+commutative to 1e-4 and 4-deep unbind recovers payload >=0.95 -- algebraic substrate for nested structures confirmed. " + s)
    if r["deep_recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: 4-deep recall 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: deep unbind recall <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
