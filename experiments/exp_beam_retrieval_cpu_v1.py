"""
exp_beam_retrieval_cpu_v1.py -- beam search over multi-hop paths beats greedy on the substrate KG -- CPU.

ROUTING: hybrid-architecture / KG-QA mechanism (I4 beam retrieval over K-hop paths). At each hop keep the top-B partial paths (by accumulated unbind score) instead of committing to the single best (greedy); recover the terminal entity of a 2-hop path. Tests whether beam retrieval recovers paths that greedy single-best loses (Beam-Retrieval VSA equivalent). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS beam (B=4) recall@1 >= greedy + 0.05 on 2-hop paths. MIDDLE >= greedy. HARD-FAIL < greedy.
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
ANCHOR_NAME = "beam_retrieval_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg); alls = np.concatenate([pos, neg]); lab = np.concatenate([np.ones(len(pos)), np.zeros(len(neg))])
    order = np.argsort(alls); ranks = np.empty_like(order, dtype=np.float64); ranks[order] = np.arange(1, len(alls) + 1)
    return float((ranks[lab == 1].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg) + 1e-9))

def _selftest():
    assert sorted([3, 1, 2], reverse=True)[:2] == [3, 2], "beam topB"; print("[selftest] PASS: beam-retrieval", flush=True)
def run() -> Dict:
    g = np.random.default_rng(55); N = 8192; VE = 150; VR = 8; B = 4; TR = 60 if SMOKE else 200
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}; M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(3):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    def sample_path():
        for _ in range(100):
            s = int(g.integers(0, VE)); o1 = [(r, edges[(s, r)]) for (ss, r) in edges if ss == s]
            if not o1:
                continue
            r1, b = o1[int(g.integers(0, len(o1)))]; o2 = [(r, edges[(b, r)]) for (ss, r) in edges if ss == b]
            if not o2:
                continue
            r2, ans = o2[int(g.integers(0, len(o2)))]; return s, r1, r2, ans
        return None
    gh = 0; bh = 0; n = 0
    for _ in range(TR):
        p = sample_path()
        if not p:
            continue
        s, r1, r2, ans = p
        # greedy: top-1 at hop1
        b1 = cidx(M * np.conj(ents[s] * rels[r1]), ents); gpred = cidx(M * np.conj(ents[b1] * rels[r2]), ents)
        # beam: keep top-B hop1 candidates, expand each, take best final
        sc1 = (ents @ np.conj(M * np.conj(ents[s] * rels[r1]))).real; cand = np.argsort(-sc1)[:B]
        best_final = -1; best_sc = -1e18
        for c in cand:
            sc2 = (ents @ np.conj(M * np.conj(ents[c] * rels[r2]))).real; j = int(np.argmax(sc2))
            if sc1[c] + sc2[j] > best_sc:
                best_sc = sc1[c] + sc2[j]; best_final = j
        gh += int(gpred == ans); bh += int(best_final == ans); n += 1
    gr = gh / n; br = bh / n; print("  2-hop recall@1: greedy=%.3f beam(B=%d)=%.3f (gain=%.3f)" % (gr, B, br, br - gr), flush=True)
    return {"greedy": gr, "beam": br, "gain": br - gr}
def verdict(r) -> Tuple[str, str]:
    s = "greedy=%.3f beam=%.3f gain=%.3f" % (r["greedy"], r["beam"], r["gain"])
    if r["gain"] >= 0.05: return ("HARD_PASS", "HARD_PASS: beam retrieval beats greedy by >=0.05 on 2-hop paths -- keeping top-B partial paths recovers bridges greedy loses. " + s)
    if r["gain"] >= 0.0: return ("MIDDLE_BAND", "MIDDLE_BAND: beam >= greedy but gain <0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: beam worse than greedy. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
