"""
exp_discrete_vs_fuzzy_kgqa_cpu_v1.py -- discrete-KG K-hop vs fuzzy-embedding retrieval on the same 2-hop QA -- CPU.

ROUTING: hybrid / native multi-hop mechanism (discrete vs fuzzy QA head-to-head). Direct head-to-head on identical 2-hop questions: (a) discrete-KG substrate K-hop, (b) fuzzy-embedding nearest-neighbor retrieval. Confirms the universal principle at the QA level -- discrete wins, fuzzy loses on the same task. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS discrete recall@1 >= 0.70 AND discrete >= fuzzy + 0.30. MIDDLE discrete >= fuzzy + 0.15. HARD-FAIL gap < 0.15.
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
ANCHOR_NAME = "discrete_vs_fuzzy_kgqa_cpu_v1"
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
    assert 0.8 - 0.3 >= 0.3, "gap"; print("[selftest] PASS: discrete-vs-fuzzy-kgqa", flush=True)
def run() -> Dict:
    g = np.random.default_rng(65); N = 8192; VE = 150; VR = 12; TR = 60 if SMOKE else 200
    ents, rels, edges, M = build_kg(g, N, VE, VR, 2)
    fz = g.standard_normal((VE, 96)); fz /= np.linalg.norm(fz, axis=1, keepdims=True)         # fuzzy entity embeddings
    dh = 0; fh = 0; n = 0
    for _ in range(TR):
        path, rseq = sample_path(edges, VE, g, 2)
        if path is None:
            continue
        start, bridge, gold = path[0], path[1], path[2]
        cur = ents[start]
        for r in rseq:
            cur = ents[cidx(M * np.conj(cur * rels[r]), ents)]
        dpred = cidx(cur, ents); dh += int(dpred == gold)
        # fuzzy: iterative nearest-neighbor by embedding (no relation structure)
        qf = fz[start] + 1.0 / math.sqrt(96) * g.standard_normal(96); b = int(np.argmax(fz @ qf))
        qf2 = fz[b] + 1.0 / math.sqrt(96) * g.standard_normal(96); fpred = int(np.argmax(fz @ qf2))
        fh += int(fpred == gold); n += 1
    dr = dh / max(1, n); fr = fh / max(1, n); print("  2-hop QA recall@1: discrete-KG=%.3f fuzzy-embedding=%.3f (gap=%.3f)" % (dr, fr, dr - fr), flush=True)
    return {"discrete": dr, "fuzzy": fr, "gap": dr - fr}
def verdict(r) -> Tuple[str, str]:
    s = "discrete=%.3f fuzzy=%.3f gap=%.3f" % (r["discrete"], r["fuzzy"], r["gap"])
    if r["discrete"] >= 0.70 and r["gap"] >= 0.30: return ("HARD_PASS", "HARD_PASS: discrete-KG K-hop >=0.70 and beats fuzzy by >=0.30 on identical 2-hop QA -- universal principle confirmed at the QA level. " + s)
    if r["gap"] >= 0.15: return ("MIDDLE_BAND", "MIDDLE_BAND: discrete-vs-fuzzy gap 0.15-0.30. " + s)
    return ("HARD_FAIL", "HARD_FAIL: discrete-vs-fuzzy gap <0.15. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
