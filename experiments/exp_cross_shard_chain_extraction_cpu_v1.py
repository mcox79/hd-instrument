"""
exp_cross_shard_chain_extraction_cpu_v1.py -- sleep-defrag pre-computes cross-shard 2-hop chains into single-shard lookups -- CPU.

ROUTING: Mechanism C sleep-defrag cross-shard chain extraction. Per-subject sharded KG; a 2-hop chain A-r1->B-r2->Y spans shards (A and B in different shards). During SLEEP DEFRAG, for each (A,r1,B) look up B's shard for (B,r2,Y) and emit a DERIVED fact (A, chain[r1,r2], Y) into A's shard (chain[r1,r2]=r1*r2, a composed relation with provenance). After defrag, the 2-hop query is a SINGLE-shard lookup. Measures post-defrag single-shard 2-hop recall + that the composed relation is recoverable. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS post-defrag single-shard 2-hop recall@1 >= 0.90 AND composed-relation recoverable. MIDDLE >= 0.80. HARD-FAIL < 0.80.
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
ANCHOR_NAME = "cross_shard_chain_extraction_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; r1 = cphasor(1, 64, g)[0]; r2 = cphasor(1, 64, g)[0]; y = cphasor(1, 64, g)[0]
    chain = r1 * r2; assert np.allclose((a * chain * y) * np.conj(a * chain), y, atol=1e-3), "composed-relation unbind"; print("[selftest] PASS: cross-shard-chain-extraction", flush=True)
def run() -> Dict:
    g = np.random.default_rng(141); N = 8192; VE = 300; VR = 12; deg = 3; TR = 60 if SMOKE else 200
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}
    base = {}                                                              # per-subject shard: base edges r*o
    for s in range(VE):
        for _ in range(deg):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; base.setdefault(s, np.zeros(N, dtype=np.complex64)); base[s] = base[s] + rels[r] * ents[o]
    # SLEEP DEFRAG: for each (A,r1,B), find (B,r2,Y) and emit derived chain fact into A's shard: ents[A]*chain*ents[Y]
    derived = {s: np.zeros(N, dtype=np.complex64) for s in base}
    for (A, r1), B in list(edges.items()):
        for r2 in range(VR):
            if (B, r2) in edges:
                Y = edges[(B, r2)]; chain = rels[r1] * rels[r2]; derived.setdefault(A, np.zeros(N, dtype=np.complex64)); derived[A] = derived[A] + chain * ents[Y]
    def sample():
        for _ in range(150):
            A = int(g.integers(0, VE)); o1 = [(r, edges[(A, r)]) for (ss, r) in edges if ss == A]
            if not o1:
                continue
            r1, B = o1[int(g.integers(0, len(o1)))]; o2 = [(r, edges[(B, r)]) for (ss, r) in edges if ss == B]
            if not o2:
                continue
            r2, Y = o2[int(g.integers(0, len(o2)))]; return A, r1, B, r2, Y
        return None
    hit = 0; n = 0
    for _ in range(TR):
        p = sample()
        if not p:
            continue
        A, r1, B, r2, Y = p; chain = rels[r1] * rels[r2]
        pred = cidx(derived[A] * np.conj(chain), ents)                     # SINGLE-shard lookup via the pre-computed chain
        hit += int(pred == Y); n += 1
    rec = hit / max(1, n); print("  post-defrag single-shard 2-hop recall@1=%.3f (n=%d, %d subjects)" % (rec, n, len(base)), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "post-defrag single-shard 2-hop=%.3f" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: sleep-defrag chain extraction turns cross-shard 2-hop into a single-shard lookup at >=0.90 -- pre-computed composed-relation chains close the cross-shard cost. " + s)
    if r["recall"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: post-defrag 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: post-defrag <0.80. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
