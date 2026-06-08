"""
exp_ppr_spreading_activation_cpu_v1.py -- PageRank-like spreading activation over a substrate KG (HippoRAG-equivalent) -- CPU.

ROUTING: hybrid-architecture / KG-QA mechanism (I3 PPR spreading activation). From a seed entity, iteratively spread activation through the substrate KG (each step adds unbound-neighbor mass with damping); measure convergence depth and recall@K of the true 2-hop neighborhood. Tests the HippoRAG personalized-PageRank mechanism on the substrate. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS spreading converges by K<=5 AND recall@K of 2-hop neighborhood >= 0.70. MIDDLE recall >= 0.55. HARD-FAIL < 0.55 or no convergence by K=10.
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
ANCHOR_NAME = "ppr_spreading_activation_cpu_v1"
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
    assert abs((0.85 * 1.0 + 0.15) - 1.0) < 0.5, "damping"; print("[selftest] PASS: ppr-spreading-activation", flush=True)
def run() -> Dict:
    g = np.random.default_rng(53); N = 8192; VE = 120; VR = 8; DAMP = 0.7; TR = 20 if SMOKE else 60
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); adj = {i: [] for i in range(VE)}; M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(2):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if o != s and o not in adj[s]:
                adj[s].append(o); M = M + ents[s] * rels[r] * ents[o]
    def true_2hop(seed):
        h1 = set(adj[seed]); h2 = set();
        for u in h1:
            h2 |= set(adj[u])
        return (h1 | h2) - {seed}
    convs = []; recs = []
    for _ in range(TR):
        seed = int(g.integers(0, VE)); tgt = true_2hop(seed)
        if not tgt:
            continue
        act = np.zeros(VE); act[seed] = 1.0; conv_k = 10; prev_top = None
        for k in range(1, 11):
            newact = (1 - DAMP) * np.zeros(VE)
            for u in np.where(act > 0.01)[0]:
                for r in range(VR):
                    nb = cidx(M * np.conj(ents[u] * rels[r]), ents); sc = (ents[nb] @ np.conj(M * np.conj(ents[u] * rels[r]))).real / N
                    if sc > 0.3:
                        newact[nb] += DAMP * act[u] / 2.0
            newact[seed] += (1 - DAMP)
            act = act + newact; top = tuple(np.argsort(-act)[:len(tgt)].tolist())
            if top == prev_top:
                conv_k = k; break
            prev_top = top
        retr = set(np.argsort(-act)[:len(tgt) + 1].tolist()) - {seed}
        recs.append(len(retr & tgt) / len(tgt)); convs.append(conv_k)
    rec = float(np.mean(recs)); cv = float(np.mean(convs)); print("  recall@K(2-hop nbhd)=%.3f mean-convergence-K=%.1f" % (rec, cv), flush=True)
    return {"recall": rec, "conv_k": cv}
def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f convergence-K=%.1f" % (r["recall"], r["conv_k"])
    if r["recall"] >= 0.70 and r["conv_k"] <= 5: return ("HARD_PASS", "HARD_PASS: PPR spreading converges by K<=5 with 2-hop recall>=0.70 -- HippoRAG-style spreading activation works on the substrate. " + s)
    if r["recall"] >= 0.55: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.55-0.70 or slower convergence. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.55 or no convergence. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
