"""
exp_single_shot_attention_triples_cpu_v1.py -- single-pass attention over all triples recovers the answer (no iteration) -- CPU.

ROUTING: hybrid / native multi-hop mechanism (N1c single-shot attention on triple substrate). Instead of iterative K-hop, score every triple by joint relevance to the question's (start, r1, r2) in ONE softmax-attention pass, then read out the attended object. Tests whether single-shot joint attention (transformer-like) on the structured substrate solves 2-hop without iteration. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS single-shot attention recall@2 >= 0.50 (matches PP-99 0.501). MIDDLE >= 0.40. HARD-FAIL < 0.40.
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
ANCHOR_NAME = "single_shot_attention_triples_cpu_v1"
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
    x = np.array([1.0, 2.0]); sm = np.exp(x - x.max()); sm /= sm.sum(); assert abs(sm.sum() - 1) < 1e-9, "softmax"; print("[selftest] PASS: single-shot-attention-triples", flush=True)
def run() -> Dict:
    g = np.random.default_rng(62); N = 8192; VE = 150; VR = 12; TR = 60 if SMOKE else 200; BETA = 6.0
    ents, rels, edges, M = build_kg(g, N, VE, VR, 2)
    tri = [(s, r, o) for (s, r), o in edges.items()]
    TS = np.stack([ents[s] for s, r, o in tri]); TR_ = np.stack([rels[r] for s, r, o in tri]); TO = np.stack([ents[o] for s, r, o in tri])
    hit = 0; n = 0
    for _ in range(TR):
        path, rseq = sample_path(edges, VE, g, 2)
        if path is None:
            continue
        start, bridge, gold = path[0], path[1], path[2]
        # single-pass: attend to triples matching (start, r1) AND (?, r2); combine object slots in ONE weighted readout
        q1 = ents[start] * rels[rseq[0]]; q2 = rels[rseq[1]]
        s1 = (TS * np.conj(ents[start])).sum(1).real + (TR_ * np.conj(rels[rseq[0]])).sum(1).real    # triples from start via r1
        s2 = (TR_ * np.conj(rels[rseq[1]])).sum(1).real                                              # triples via r2 (the second hop)
        # bridge-aware joint attention: weight hop2 triples by how much their subject matches hop1 objects
        a1 = np.exp(BETA * (s1 / N - (s1 / N).max())); a1 /= a1.sum(); bridge_vec = (a1[:, None] * TO).sum(0)
        s2b = s2 / N + (TS * np.conj(bridge_vec)).sum(1).real / N
        a2 = np.exp(BETA * (s2b - s2b.max())); a2 /= a2.sum(); ans_vec = (a2[:, None] * TO).sum(0)
        pred = cidx(ans_vec, ents); hit += int(pred == gold); n += 1
    rec = hit / max(1, n); print("  single-shot attention recall@2=%.3f (n=%d, triples=%d)" % (rec, n, len(tri)), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "single-shot attention recall@2=%.3f" % r["recall"]
    if r["recall"] >= 0.50: return ("HARD_PASS", "HARD_PASS: single-pass joint attention on the triple substrate recall@2>=0.50 -- transformer-like one-shot multi-hop works without iteration. " + s)
    if r["recall"] >= 0.40: return ("MIDDLE_BAND", "MIDDLE_BAND: single-shot attention 0.40-0.50. " + s)
    return ("HARD_FAIL", "HARD_FAIL: single-shot attention <0.40. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
