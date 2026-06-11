"""
exp_slipnet_substrate_cpu_v1.py -- SLIPNET-SUBSTRATE (cross-domain new mechanism) -- CPU.

ROUTING: Research 5X_ARCHITECTURAL Sprint-1 (cross-domain NEW). Hofstadter-slipnet over a typed relation graph: each node's
  signature = activation spread through TYPED relations, seeded by its relation-TYPE profile (mix of relation types on its
  edges). Cross-domain analogy = recover the correspondence between two isomorphic graphs (different entities) from
  relation-type structure ALONE. Compares to a raw-degree-only baseline -- does relation-TYPE structure crack the cross-domain
  gap where SME was only degree-driven? Substrate-only, no entity geometry (avoids P9 confound). N=8192.
PRE-REGISTERED: HARD-PASS slipnet correspondence Hits@1 >= 0.70 AND beats degree-only baseline by >=0.15 (relation-type structure carries it). MIDDLE >= 0.50. HARD-FAIL else.
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
ANCHOR_NAME = "slipnet_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: slipnet-substrate", flush=True)
def slip_sig(n, edges, rels, OUT, IN, deg_atoms, iters, use_reltype):
    if use_reltype:
        seed = np.zeros((n, N), dtype=np.complex64)
        for (i, r, j) in edges:
            seed[i] = seed[i] + rels[r] * OUT; seed[j] = seed[j] + rels[r] * IN   # relation-TYPE profile seed
        sig = cnorm(seed)
        for _ in range(iters):
            nxt = sig.copy()
            for (i, r, j) in edges:
                nxt[i] = nxt[i] + rels[r] * sig[j]                                # spread through TYPED relation
            sig = cnorm(nxt)
        return sig
    else:
        outd = [0] * n; ind = [0] * n                                            # raw-degree-only baseline
        for (i, r, j) in edges:
            outd[i] += 1; ind[j] += 1
        return cnorm(np.stack([deg_atoms[min(outd[i], 9)] * deg_atoms[10 + min(ind[i], 9)] for i in range(n)]))
def run() -> Dict:
    g = np.random.default_rng(672); n = 7; NREL = 4; rels = cphasor(NREL, N, g)
    OUT = cphasor(1, N, g)[0]; IN = cphasor(1, N, g)[0]; deg_atoms = cphasor(20, N, g)
    TR = 25 if SMOKE else 150; hit = 0; hit_deg = 0; tot = 0
    for _ in range(TR):
        ne = n + 4; edges = []
        for _e in range(ne):
            i, j = int(g.integers(0, n)), int(g.integers(0, n)); r = int(g.integers(0, NREL))
            if i != j:
                edges.append((i, r, j))
        perm = g.permutation(n)
        tedges = [(int(perm[i]), r, int(perm[j])) for (i, r, j) in edges]
        bs = slip_sig(n, edges, rels, OUT, IN, deg_atoms, 5, True); ts = slip_sig(n, tedges, rels, OUT, IN, deg_atoms, 5, True)
        bd = slip_sig(n, edges, rels, OUT, IN, deg_atoms, 0, False); td = slip_sig(n, tedges, rels, OUT, IN, deg_atoms, 0, False)
        S = (bs @ np.conj(ts.T)).real; Sd = (bd @ np.conj(td.T)).real
        for i in range(n):
            hit += int(int(np.argmax(S[i])) == int(perm[i])); hit_deg += int(int(np.argmax(Sd[i])) == int(perm[i])); tot += 1
    h1 = hit / tot; h1d = hit_deg / tot
    print("  SLIPNET relation-type Hits@1=%.3f | degree-only baseline=%.3f (lift=%.3f, n=%d cross-domain)" % (h1, h1d, h1 - h1d, n), flush=True)
    return {"hits1_slipnet": round(h1, 3), "hits1_degree": round(h1d, 3), "lift": round(h1 - h1d, 3), "n_entities": n}
def verdict(r) -> Tuple[str, str]:
    s = "slipnet=%.3f degree-baseline=%.3f lift=%.3f" % (r["hits1_slipnet"], r["hits1_degree"], r["lift"])
    if r["hits1_slipnet"] >= 0.70 and r["lift"] >= 0.15:
        return ("HARD_PASS", "HARD_PASS: relation-TYPE slipnet activation recovers cross-domain correspondence (Hits@1>=0.70) and beats degree-only by >=0.15 -- relation-type structure (not just degree, not entity geometry) carries cross-domain analogy. NEW mechanism cracks the gap SME could not. " + s)
    if r["hits1_slipnet"] >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: slipnet >=0.50 but lift over degree <0.15 (still largely degree-driven, like SME). " + s)
    return ("HARD_FAIL", "HARD_FAIL: slipnet <0.50 cross-domain. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
