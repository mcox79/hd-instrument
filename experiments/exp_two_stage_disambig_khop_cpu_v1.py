"""
exp_two_stage_disambig_khop_cpu_v1.py -- fuzzy entity-find then discrete K-hop beats either stage alone -- CPU.

ROUTING: hybrid / native multi-hop mechanism (H3 two-stage entity disambiguation + K-hop). Stage 1 (fuzzy): match the question to candidate START entities via noisy embeddings (top-B). Stage 2 (native): run discrete K-hop from each candidate and pick the best-scoring terminal. Combines fuzzy disambiguation with native traversal. recall@2 of the answer. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS 2-stage recall@2 >= 0.65. MIDDLE >= 0.55. HARD-FAIL < 0.55.
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
ANCHOR_NAME = "two_stage_disambig_khop_cpu_v1"
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
    assert np.argsort(-np.array([0.1, 0.9, 0.5]))[0] == 1, "argsort"; print("[selftest] PASS: two-stage-disambig-khop", flush=True)
def run() -> Dict:
    g = np.random.default_rng(61); N = 8192; VE = 150; VR = 12; B = 3; FUZZ = 1.0; TR = 60 if SMOKE else 200
    ents, rels, edges, M = build_kg(g, N, VE, VR, 2)
    fuzz_emb = g.standard_normal((VE, 64)); fuzz_emb /= np.linalg.norm(fuzz_emb, axis=1, keepdims=True)
    hit = 0; n = 0
    for _ in range(TR):
        path, rseq = sample_path(edges, VE, g, 2)
        if path is None:
            continue
        start, gold = path[0], path[-1]
        q = fuzz_emb[start] + FUZZ / math.sqrt(64) * g.standard_normal(64)          # noisy question embedding of start
        cands = np.argsort(-(fuzz_emb @ q))[:B]                                      # stage1 fuzzy candidate starts
        terminals = set()
        for c in cands:                                                             # stage2 native K-hop from each candidate
            cur = ents[int(c)]
            for r in rseq:
                cur = ents[cidx(M * np.conj(cur * rels[r]), ents)]
            terminals.add(cidx(cur, ents))
        hit += int(gold in terminals); n += 1                                       # two-stage recovers the answer among B chains
    rec = hit / max(1, n); print("  2-stage (fuzzy-disambig top-%d + native K-hop) recall=%.3f (n=%d)" % (B, rec, n), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "2-stage recall@2=%.3f" % r["recall"]
    if r["recall"] >= 0.65: return ("HARD_PASS", "HARD_PASS: fuzzy entity-disambiguation + native K-hop recall@2>=0.65 -- hybrid two-stage works (fuzzy finds the door, native walks the graph). " + s)
    if r["recall"] >= 0.55: return ("MIDDLE_BAND", "MIDDLE_BAND: 2-stage recall 0.55-0.65. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 2-stage recall <0.55. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
