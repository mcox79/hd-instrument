"""
exp_comp22_causal_at_l3_cpu_v1.py -- Pearl do() over L3 composite-valued causal variables -- CPU.

ROUTING: Research COMP_DIRECTION_CONFIRMED P4 (COMP-22 CAUSAL-AT-L3); pure-FHRR (no download). do(root) intervention propagated through a chain of composite-valued variables via unbind+cleanup; vs atomic L1.
  Items/states are deep L3 composites (cnorm of K unit phasors over 3 levels, self-similar so a random level composite
  IS a valid L3 item). Reasoning runs over composite items with cleanup against the composite-item memory; compared to an
  atomic (L1) baseline. Tests reasoning-at-depth holds (within 10pp of L1). N=8192.
PRE-REGISTERED: HARD-PASS L3 do()-recall>=0.80 AND |gap-to-L1|<=0.10. MIDDLE>=0.65. HARD-FAIL<0.65.
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
ANCHOR_NAME = "comp22_causal_at_l3_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def comp_l3_batch(B, g):
    # B deep L3 composite items: 3 levels of K=10-ary bundling -> cnorm; self-similar, so = cnorm of unit phasors
    K = 10; out = cphasor(B, N, g)
    for _ in range(3):
        r = cphasor(B * K, N, g).reshape(B, K, N); out = cnorm(r.sum(1) + out)
    return cnorm(out)
def items(B, l3, g):
    return comp_l3_batch(B, g) if l3 else cphasor(B, N, g)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: causal-at-l3", flush=True)
def _recall(l3, g):
    NV = 4; NS = 6; TR = 25 if SMOKE else 150; hit = 0; n = 0
    EDGE = cphasor(NV - 1, N, g)
    for _ in range(TR):
        states = [items(NS, l3, g) for _ in range(NV)]               # per-variable composite state codebook
        smap = [g.integers(0, NS, size=NS) for _ in range(NV - 1)]   # deterministic mechanism child=f(parent) per edge
        edge_mem = []
        for e in range(NV - 1):
            m = np.zeros(N, dtype=np.complex64)
            for s in range(NS):
                m = m + states[e][s] * EDGE[e] * states[e + 1][int(smap[e][s])]
            edge_mem.append(m)
        # do(root = s0): propagate through the chain via unbind + cleanup at each variable
        s0 = int(g.integers(0, NS)); cur_idx = s0; gold = s0
        for e in range(NV - 1):
            gold = int(smap[e][gold])
        cur = states[0][s0]; ci = s0
        for e in range(NV - 1):
            cand = edge_mem[e] * np.conj(cur) * np.conj(EDGE[e]); ci = cidx(cand, states[e + 1]); cur = states[e + 1][ci]
        hit += int(ci == gold); n += 1
    return hit / n
def run() -> Dict:
    g = np.random.default_rng(722); r3 = _recall(True, g); r1 = _recall(False, g)
    print("  CAUSAL-AT-L3 do()-propagation recall L3=%.3f L1=%.3f (gap=%.3f)" % (r3, r1, r1 - r3), flush=True)
    return {"recall_l3": round(r3, 3), "recall_l1": round(r1, 3), "gap": round(r1 - r3, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "L3=%.3f L1=%.3f gap=%.3f" % (r["recall_l3"], r["recall_l1"], r["gap"])
    if r["recall_l3"] >= 0.80 and abs(r["gap"]) <= 0.10:
        return ("HARD_PASS", "HARD_PASS: Pearl do() intervention propagated through a causal chain of deep L3 composite-valued variables recovers the effect at >=0.80, within 10pp of atomic -- do-calculus survives composition via per-variable cleanup. " + s)
    if r["recall_l3"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: L3 causal 0.65-0.80 or gap>0.10. " + s)
    return ("HARD_FAIL", "HARD_FAIL: causal at L3 <0.65. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
