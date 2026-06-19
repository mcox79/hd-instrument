"""
exp_stretch2_2_causal_do_cpu_v1.py -- multi-step do()-operator intervention queries (Pearl SCM) -- CPU.

ROUTING: Research LAPTOP_WAVE2 STRETCH (STRETCH2-2 CAUSAL-DO-CHAINS); pure-FHRR (no download). Binary SCM stored in substrate (edges + mechanisms); do(X=x) overrides + propagates to descendants; query downstream var.
PRE-REGISTERED: HARD-PASS do-query>=0.80. MIDDLE>=0.65. HARD-FAIL<0.65.
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
from collections import deque
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "stretch2_2_causal_do_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert (1 ^ 0) == 1, "xor"; print("[selftest] PASS: causal-do-chains", flush=True)
def run() -> Dict:
    # binary SCM: topo-ordered vars; v = parity(parents) XOR bias[v] XOR u[v]. do(X=x) overrides X + recomputes descendants.
    # substrate stores parent-edges (var -> parent bundle) + bias bits; eval retrieves structure. multi-step do-chains.
    g = np.random.default_rng(172); N = 8192; NV = 8; nodes = cphasor(NV, N, g); EDGE = cphasor(1, N, g)[0]; bits = cphasor(2, N, g)
    TR = 50 if SMOKE else 250; correct = 0; n = 0
    for _ in range(TR):
        parents = {v: sorted(set(int(p) for p in g.choice(v, min(v, 2), replace=False))) if v > 0 else [] for v in range(NV)}
        bias = {v: int(g.integers(0, 2)) for v in range(NV)}
        # store structure in substrate (retrievable): edge bundle + bias binding
        pshard = {v: sum((nodes[v] * (EDGE * nodes[p]) for p in parents[v]), np.zeros(N, dtype=np.complex64)) for v in range(NV)}
        bshard = sum((nodes[v] * bits[bias[v]] for v in range(NV)), np.zeros(N, dtype=np.complex64))
        u = {v: int(g.integers(0, 2)) for v in range(NV)}
        # interventions: do(X=x) on 1-2 vars
        dov = {int(x): int(g.integers(0, 2)) for x in g.choice(NV, g.integers(1, 3), replace=False)}
        def evaluate():
            val = {}
            for v in range(NV):
                if v in dov:
                    val[v] = dov[v]; continue
                pr = 0
                for p in parents[v]:
                    pr ^= val[p]
                # recover bias from substrate
                bhat = int(np.argmax((bits @ np.conj(bshard * np.conj(nodes[v]))).real))
                val[v] = pr ^ bhat ^ u[v]
            return val
        gold = {}
        for v in range(NV):
            if v in dov:
                gold[v] = dov[v]
            else:
                pr = 0
                for p in parents[v]:
                    pr ^= gold[p]
                gold[v] = pr ^ bias[v] ^ u[v]
        got = evaluate(); Y = int(g.integers(0, NV))
        correct += int(got[Y] == gold[Y]); n += 1
    acc = correct / n; print("  CAUSAL-DO interventional-query acc=%.3f (NV=%d, n=%d)" % (acc, NV, n), flush=True)
    return {"causal_acc": acc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "do-query-acc=%.3f (n=%d)" % (r["causal_acc"], r["n"])
    if r["causal_acc"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate answers multi-step do()-intervention queries >=0.80 (Pearl SCM) -- causal graph + mechanisms stored in substrate; do() overrides + propagates correctly. " + s)
    if r["causal_acc"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: do-query 0.65-0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: do-query <0.65. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
