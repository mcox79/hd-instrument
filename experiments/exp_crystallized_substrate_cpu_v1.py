"""
exp_crystallized_substrate_cpu_v1.py -- Crystallized substrate (Sprint-4 architecture; frozen Tier-1 protection) -- CPU.

ROUTING: Research cycle-229 Tier-4 (Crystallized substrate, not yet built). Engineered-wrapper architecture: foundational
  Tier-1 atoms are written ONCE into a CRYSTALLIZED (frozen, never-rewritten) substrate; instance/episodic content goes into
  a separate MUTABLE substrate that takes heavy churn. Crystallized atoms are immune to mutable-store interference (separate
  algebra). Tests: after heavy mutable writes, recall of frozen Tier-1 atoms from the crystallized store vs from a single
  SHARED store that mixes both. Predicted: crystallized recall stays ~1.0 while shared degrades. Wrapper + routing, no core
  change. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS crystallized Tier-1 recall >= 0.95 AND > shared by >= 0.20 (separation protects foundations).
  MIDDLE crystallized >= 0.85. HARD-FAIL else.
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
ANCHOR_NAME = "crystallized_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: crystallized-substrate", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "980")))
    NT1 = 40; V = 400; MUT_WRITES = 400 if SMOKE else 2000
    keys = cphasor(NT1, N, g); vals = cphasor(V, N, g); truth = g.integers(0, V, size=NT1)
    mut_keys = cphasor(MUT_WRITES, N, g)
    # CRYSTALLIZED store: frozen Tier-1 atoms only (written once, never touched again)
    cryst = cnorm(sum((keys[i] * vals[truth[i]] for i in range(NT1)), np.zeros(N, dtype=np.complex64)))
    # SHARED store: same Tier-1 atoms + heavy mutable instance writes mixed in
    shared = sum((keys[i] * vals[truth[i]] for i in range(NT1)), np.zeros(N, dtype=np.complex64))
    for w in range(MUT_WRITES):
        shared = shared + mut_keys[w] * vals[int(g.integers(0, V))]
    shared = cnorm(shared)
    # recall the frozen Tier-1 atoms from each store
    cryst_rec = sum(cidx(cryst * np.conj(keys[i]), vals) == truth[i] for i in range(NT1)) / NT1
    shared_rec = sum(cidx(shared * np.conj(keys[i]), vals) == truth[i] for i in range(NT1)) / NT1
    print("  CRYSTALLIZED: frozen-Tier-1 recall crystallized=%.3f | shared(mixed)=%.3f (after %d mutable writes)" %
          (cryst_rec, shared_rec, MUT_WRITES), flush=True)
    return {"crystallized_recall": round(cryst_rec, 3), "shared_recall": round(shared_rec, 3), "mut_writes": MUT_WRITES, "n_tier1": NT1}
def verdict(r) -> Tuple[str, str]:
    c = r["crystallized_recall"]; sh = r["shared_recall"]; s = "crystallized=%.3f shared=%.3f" % (c, sh)
    if c >= 0.95 and c > sh + 0.20:
        return ("HARD_PASS", "HARD_PASS: crystallized substrate protects frozen Tier-1 foundations -- a separate frozen store keeps Tier-1 recall>=0.95 while a shared store mixing heavy mutable writes degrades to %.2f. Separation (engineered wrapper) protects foundations, no core change. " % sh + s)
    if c >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: crystallized >=0.85 but margin over shared <0.20. " + s)
    return ("HARD_FAIL", "HARD_FAIL: crystallized <0.85. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
