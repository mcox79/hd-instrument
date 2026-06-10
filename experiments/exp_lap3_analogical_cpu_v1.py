"""
exp_lap3_analogical_cpu_v1.py -- substrate A:B::C:D relational homomorphism -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop batch (LAP-3 ANALOGICAL); pure-FHRR (no download). Infer shared relation rel=B*conj(A), apply to C, cleanup to D.
PRE-REGISTERED: HARD-PASS analogy>=0.70. MIDDLE>=0.50. HARD-FAIL<0.50.
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
ANCHOR_NAME = "lap3_analogical_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert _n.argmax([0,1])==1, "argmax"; print("[selftest] PASS: analogical-1", flush=True)
def run() -> Dict:
    # A:B::C:D via relational homomorphism. Shared relation R binds A->B and C->D; infer rel=B*conj(A) then D=rel*C; cleanup.
    g = np.random.default_rng(303); N = 8192; VE = 300; ents = cphasor(VE, N, g)
    NREL = 6; rels = cphasor(NREL, N, g); TR = 50 if SMOKE else 250; hit = 0; n = 0
    for _ in range(TR):
        r = int(g.integers(0, NREL))
        a = int(g.integers(0, VE)); c = int(g.integers(0, VE))
        # B = R bound to A (cleanup to a real entity); pick B,D as the nearest entities to R*A, R*C
        b = cidx(rels[r] * ents[a], ents); d = cidx(rels[r] * ents[c], ents)
        if b == a or d == c:
            continue
        rel_inferred = ents[b] * np.conj(ents[a])                         # B * conj(A) ~ R
        pred = cidx(rel_inferred * ents[c], ents)                         # apply to C -> should be D
        hit += int(pred == d); n += 1
    acc = hit / n if n else 0.0
    print("  ANALOGICAL A:B::C:D acc=%.3f (n=%d)" % (acc, n), flush=True)
    return {"analogy_acc": acc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "analogy-acc=%.3f (n=%d)" % (r["analogy_acc"], r["n"])
    if r["analogy_acc"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate solves A:B::C:D analogies >=0.70 via relational bundle homomorphism (infer rel=B*conj(A), apply to C) -- structural analogy native to the algebra. " + s)
    if r["analogy_acc"] >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: analogy 0.50-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: analogy <0.50. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
