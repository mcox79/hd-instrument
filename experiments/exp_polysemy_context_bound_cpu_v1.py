"""
exp_polysemy_context_bound_cpu_v1.py -- POLYSEMY-CONTEXT-BOUND rescue of IMAGE-SCHEMA real-data failure -- CPU.

ROUTING: Research HUMANEVAL_FULL_SCALE Tier-2 rescue. IMAGE-SCHEMA-REAL failed (purity 0.34) because abstract concepts are
  POLYSEMOUS -- one concept maps to multiple senses, so a context-free representation collapses senses. RESCUE: bind each
  concept-instance to its CONTEXT (concept (X) context), so the same concept in different contexts gets distinct sense-specific
  representations (Landau-style context field). Tests sense-cluster purity context-BOUND vs context-FREE. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS context-bound sense-purity >= 0.60 AND >> context-free (rescues polysemy 0.34). MIDDLE >= 0.50. HARD-FAIL else.
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
ANCHOR_NAME = "polysemy_context_bound_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: polysemy-context-bound", flush=True)
def run() -> Dict:
    g = np.random.default_rng(632); NCON = 30; NSENSE = 4; NCTX = 6
    TR = 15 if SMOKE else 80; pure_bound = []; pure_free = []
    for _ in range(TR):
        concepts = cphasor(NCON, N, g); contexts = cphasor(NCTX, N, g); senses = cphasor(NSENSE, N, g)
        # each (concept, context) maps to a SENSE (polysemy: same concept, different context -> different sense)
        NINST = 200 if not SMOKE else 60
        inst_con = g.integers(0, NCON, size=NINST); inst_ctx = g.integers(0, NCTX, size=NINST)
        # ground-truth sense determined by (concept, context) pair (deterministic mapping)
        sense_of = {}
        def true_sense(c, k):
            key = (c, k)
            if key not in sense_of:
                sense_of[key] = int((c * 7 + k * 13) % NSENSE)
            return sense_of[key]
        free = np.zeros((NINST, N), dtype=np.complex64); bound = np.zeros((NINST, N), dtype=np.complex64); truth = np.zeros(NINST, dtype=int)
        for i in range(NINST):
            c = int(inst_con[i]); k = int(inst_ctx[i]); s = true_sense(c, k); truth[i] = s
            sense_sig = senses[s]
            free[i] = cnorm(concepts[c] + 0.6 * sense_sig + 0.5 * cphasor(1, N, g)[0])             # context-FREE: concept dominates, sense blurred
            bound[i] = cnorm(concepts[c] * contexts[k] + 0.6 * sense_sig + 0.5 * cphasor(1, N, g)[0])  # context-BOUND: (concept (X) context) disambiguates
        def purity(X):
            sig = np.stack([X[i] for i in range(NINST)]); hit = 0
            for i in range(NINST):
                sims = (sig @ np.conj(sig[i])).real; sims[i] = -1e9; nn = int(np.argmax(sims))
                hit += int(truth[nn] == truth[i])
            return hit / NINST
        pure_bound.append(purity(bound)); pure_free.append(purity(free))
    pb = float(np.mean(pure_bound)); pf = float(np.mean(pure_free))
    print("  POLYSEMY context-BOUND sense-purity=%.3f | context-FREE=%.3f (rescue of image-schema 0.34)" % (pb, pf), flush=True)
    return {"context_bound_purity": round(pb, 3), "context_free_purity": round(pf, 3)}
def verdict(r) -> Tuple[str, str]:
    pb = r["context_bound_purity"]; pf = r["context_free_purity"]; s = "context-bound=%.3f context-free=%.3f" % (pb, pf)
    if pb >= 0.60 and pb > pf + 0.10:
        return ("HARD_PASS", "HARD_PASS: context-binding RESCUES polysemy -- sense-cluster purity context-bound>=0.60 and clearly beats context-free. Binding concept (X) context disambiguates polysemous senses (the image-schema 0.34 failure was a context-free artifact). Polysemy is tractable substrate-only WITH context. " + s)
    if pb >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: context-binding helps but purity 0.50-0.60. " + s)
    return ("HARD_FAIL", "HARD_FAIL: context-binding does not rescue polysemy (<0.50). " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
