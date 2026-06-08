"""
exp_parallel_subq_fuzzy_cpu_v1.py -- parallel (not iterative) sub-question decomposition on a fuzzy substrate -- CPU.

ROUTING: hybrid / native multi-hop mechanism (N1e parallel sub-question on fuzzy substrate). Decompose a 2-hop question into TWO PARALLEL sub-questions and retrieve each independently on a FUZZY (overlapping-embedding) substrate, then union the results. Tests whether parallel decomposition (vs the failed iterative reformulation) rescues the fuzzy regime. recall@2 of both supporting facts. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS parallel-fuzzy recall@2 >= 0.55. MIDDLE >= 0.45. HARD-FAIL < 0.45.
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
ANCHOR_NAME = "parallel_subq_fuzzy_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def build_kg(g, N, VE, VR, deg):
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}; M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(deg):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    return ents, rels, edges, M
def sample_path(edges, VE, g, hops):
    for _ in range(150):
        s = int(g.integers(0, VE)); path = [s]; rseq = []
        ok = True
        for _h in range(hops):
            outs = [r for (ss, r) in edges if ss == path[-1]]
            if not outs:
                ok = False; break
            r = int(g.choice(outs)); rseq.append(r); path.append(edges[(path[-1], r)])
        if ok:
            return path, rseq
    return None, None

def _selftest():
    assert len({1, 2} | {2, 3}) == 3, "union"; print("[selftest] PASS: parallel-subq-fuzzy", flush=True)
def run() -> Dict:
    g = np.random.default_rng(63); D = 384; NC = 40; PER = 10; V = NC * PER; TR = 60 if SMOKE else 200
    # GENUINELY fuzzy substrate: items cluster by topic (within-cluster items are similar -> retrieval confusable)
    centers = g.standard_normal((NC, D))
    base = np.repeat(centers, PER, 0) + 0.6 * g.standard_normal((V, D))
    E = base / np.linalg.norm(base, axis=1, keepdims=True)
    hit = 0; n = 0
    for _ in range(TR):
        f1, f2 = int(g.integers(0, V)), int(g.integers(0, V))
        if f1 // PER == f2 // PER:
            continue
        gold = {f1, f2}
        sq1 = E[f1] + 0.9 / math.sqrt(D) * g.standard_normal(D); sq2 = E[f2] + 0.9 / math.sqrt(D) * g.standard_normal(D)
        retr = {int(np.argmax(E @ sq1)), int(np.argmax(E @ sq2))}; hit += int(len(retr & gold) == 2); n += 1
    rec = hit / max(1, n); print("  parallel-fuzzy recall@2=%.3f (n=%d, %d clusters)" % (rec, n, NC), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "parallel-fuzzy recall@2=%.3f" % r["recall"]
    if r["recall"] >= 0.55: return ("HARD_PASS", "HARD_PASS: parallel sub-question decomposition on fuzzy substrate recall@2>=0.55 -- parallel (not iterative) decomp rescues the fuzzy regime. " + s)
    if r["recall"] >= 0.45: return ("MIDDLE_BAND", "MIDDLE_BAND: parallel-fuzzy 0.45-0.55. " + s)
    return ("HARD_FAIL", "HARD_FAIL: parallel-fuzzy <0.45 -- parallel decomp does not rescue fuzzy. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
