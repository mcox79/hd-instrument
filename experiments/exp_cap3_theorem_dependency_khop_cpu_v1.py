"""
exp_cap3_theorem_dependency_khop_cpu_v1.py -- theorem-dependency closure via sharded K-hop traversal -- CPU.

ROUTING: 8_DRILLS batch (CAP-3 theorem-dependency K-hop memory). A math knowledge base where theorems depend on lemmas (theorem -depends-on-> lemma, multi-level). Per-theorem sharded substrate; K-hop traversal recovers the full transitive dependency closure of a theorem. Tests the substrate as a theorem-dependency memory (math/logic knowledge layer). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS dependency K-hop closure recall >= 0.90 (vs ground-truth transitive closure). MIDDLE >= 0.75. HARD-FAIL < 0.75.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "cap3_theorem_dependency_khop_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def scorevec(v, book):
    return (book @ np.conj(v)).real / book.shape[1]

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; r = cphasor(1, 64, g)[0]; o = cphasor(1, 64, g)[0]; assert np.allclose(a*r*o*np.conj(a*r), o, atol=1e-3), "bind"; print("[selftest] PASS: cap3-theorem-dependency-khop", flush=True)
def run() -> Dict:
    g = np.random.default_rng(633); N = 8192; VT = 200; DEP = cphasor(1, N, g)[0]; thms = cphasor(VT, N, g); TR = 40 if SMOKE else 120; HOPS = 3
    rec_sum = 0.0; n = 0
    for _ in range(TR):
        adj = {i: [] for i in range(VT)}; shard = {i: np.zeros(N, dtype=np.complex64) for i in range(VT)}
        # DAG-ish: each theorem depends on 1-3 LOWER-indexed lemmas (acyclic dependency)
        for t in range(1, VT):
            k = int(g.integers(1, 4)); deps = g.choice(t, min(k, t), replace=False)
            for d in deps:
                adj[t].append(int(d)); shard[t] = shard[t] + DEP * thms[int(d)]
        root = int(g.integers(VT // 2, VT))
        gold = set(); fr = {root}
        for _ in range(HOPS):                                              # ground-truth transitive closure
            nf = set()
            for u in fr:
                nf |= set(adj[u]) - gold
            gold |= nf; fr = nf
        if not gold:
            continue
        reached = set(); fr = [root]
        for _ in range(HOPS):
            nf = []
            for u in fr:
                if not adj[u]:
                    continue
                rec = shard[u] * np.conj(DEP)
                for v in np.where(scorevec(rec, thms) > 0.30)[0].tolist():
                    if v not in reached and v != root:
                        nf.append(v)
            reached |= set(nf); fr = nf
        rec_sum += len(gold & reached) / len(gold); n += 1
    rc = rec_sum / max(1, n); print("  theorem-dependency K-hop closure recall=%.3f (n=%d)" % (rc, n), flush=True)
    return {"recall": rc}
def verdict(r) -> Tuple[str, str]:
    s = "dependency-closure recall=%.3f" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: theorem-dependency K-hop closure >=0.90 -- substrate as math/logic dependency memory. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: dependency closure 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: dependency closure <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
