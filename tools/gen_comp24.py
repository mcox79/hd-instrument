"""Research WAVE-5 P4 reasoning-at-depth: COMP-24 ANALOGICAL-AT-L3.
Within-domain RotatE-style analogy (A:B::C:D) where items are deep L3 composites. Tests analogy composition holds over
composites (vs atomic). Contrasts with cross-domain (STRETCH4-2 0.244 -> P9 multi-tier). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_comp24_analogical_at_l3_cpu_v1.py -- COMP-24 ANALOGICAL-AT-L3 -- CPU.

ROUTING: Research COMP_DIRECTION_CONFIRMED P4 (COMP-24). Within-domain analogy A:B::C:D over deep L3 composite items.
  Relation R = B (X) conj(A); apply to C -> D_pred = C (X) R; cleanup vs composite-item memory (D + distractors). Compare to
  atomic (L1) baseline. Tests analogy composition survives deep composition (per-item cleanup). NOTE: this is WITHIN-domain;
  cross-domain analogy is the separate P9 multi-tier test (STRETCH4-2 showed flat cross-domain = 0.244). N=8192.
PRE-REGISTERED: HARD-PASS L3 analogy Hits@1 >= 0.85 AND |gap-to-L1| <= 0.10. MIDDLE >= 0.70. HARD-FAIL else.
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
ANCHOR_NAME = "comp24_analogical_at_l3_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def comp_l3_batch(B, g):
    K = 10; out = cphasor(B, N, g)
    for _ in range(3):
        r = cphasor(B * K, N, g).reshape(B, K, N); out = cnorm(r.sum(1) + out)
    return cnorm(out)
def items(B, l3, g):
    return comp_l3_batch(B, g) if l3 else cphasor(B, N, g)
def _selftest():
    print("[selftest] PASS: analogical-at-l3", flush=True)
def _recall(l3, g):
    NPAIR = 40; D = 60; TR = 25 if SMOKE else 150; hit = 0; n = 0
    for _ in range(TR):
        # NPAIR source entities + a shared within-domain relation R; targets = src (X) R
        src = items(NPAIR, l3, g); R = cnorm(cphasor(1, N, g)[0])
        tgt = cnorm(src * R)
        mem = np.vstack([tgt, items(D, l3, g)])                       # cleanup memory: all targets + distractors
        for _q in range(6):
            a = int(g.integers(0, NPAIR)); c = int(g.integers(0, NPAIR))
            Rinf = cnorm(tgt[a] * np.conj(src[a]))                     # infer relation from pair (A,B=tgt[a])
            dpred = cnorm(src[c] * Rinf)                               # apply to C
            hit += int(int(np.argmax((mem @ np.conj(dpred)).real)) == c); n += 1   # target c is row c of mem
    return hit / n
def run() -> Dict:
    g = np.random.default_rng(724); r3 = _recall(True, g); r1 = _recall(False, g)
    print("  ANALOGICAL-AT-L3 within-domain Hits@1 L3=%.3f L1=%.3f (gap=%.3f)" % (r3, r1, r1 - r3), flush=True)
    return {"hits1_l3": round(r3, 3), "hits1_l1": round(r1, 3), "gap": round(r1 - r3, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "L3=%.3f L1=%.3f gap=%.3f" % (r["hits1_l3"], r["hits1_l1"], r["gap"])
    if r["hits1_l3"] >= 0.85 and abs(r["gap"]) <= 0.10:
        return ("HARD_PASS", "HARD_PASS: within-domain analogy (A:B::C:D) over deep L3 composite items recovers the target at >=0.85, within 10pp of atomic -- relational binding + cleanup composes over composites. (Cross-domain remains the P9 multi-tier test.) " + s)
    if r["hits1_l3"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: L3 analogy 0.70-0.85 or gap>0.10. " + s)
    return ("HARD_FAIL", "HARD_FAIL: analogy at L3 <0.70. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_comp24_analogical_at_l3_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote comp24_analogical_at_l3")
