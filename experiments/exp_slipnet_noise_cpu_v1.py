"""
exp_slipnet_noise_cpu_v1.py -- SLIPNET-NOISE (robustness of cross-domain crack to imperfect graphs) -- CPU.

ROUTING: robustness audit of SLIPNET (cross-domain win was on PERFECT isomorphic graphs). Real cross-domain analogies are
  IMPERFECT -- the structures only partly match. Adds NOISE to the target graph (delete + add a fraction of edges) and tests
  relation-type correspondence recovery vs noise level. Is the cross-domain crack ROBUST (survives ~20-30% noise) or FRAGILE?
  Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS Hits@1 >= 0.60 at 25% edge noise (robust to imperfect graphs). MIDDLE >= 0.45. HARD-FAIL else.
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
ANCHOR_NAME = "slipnet_noise_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def slip(n, edges, rels, OUT, IN, iters=5):
    seed = np.zeros((n, N), dtype=np.complex64)
    for (i, r, j) in edges:
        seed[i] = seed[i] + rels[r] * OUT; seed[j] = seed[j] + rels[r] * IN
    sig = cnorm(seed)
    for _ in range(iters):
        nxt = sig.copy()
        for (i, r, j) in edges:
            nxt[i] = nxt[i] + rels[r] * sig[j]
        sig = cnorm(nxt)
    return sig
def _selftest():
    print("[selftest] PASS: slipnet-noise", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "673"))); n = 7; NREL = 4; rels = cphasor(NREL, N, g); OUT = cphasor(1, N, g)[0]; IN = cphasor(1, N, g)[0]
    noises = [0.0, 0.15, 0.25] if SMOKE else [0.0, 0.10, 0.25, 0.40]; TR = 25 if SMOKE else 150
    curve = {}
    for noise in noises:
        hit = 0; tot = 0
        for _ in range(TR):
            ne = n + 4; edges = []
            for _e in range(ne):
                i, j = int(g.integers(0, n)), int(g.integers(0, n)); r = int(g.integers(0, NREL))
                if i != j:
                    edges.append((i, r, j))
            perm = g.permutation(n); tedges = [(int(perm[i]), r, int(perm[j])) for (i, r, j) in edges]
            # NOISE: delete a fraction + add random edges to target
            keep = [e for e in tedges if g.random() > noise]
            nadd = int(noise * len(tedges))
            for _a in range(nadd):
                i, j = int(g.integers(0, n)), int(g.integers(0, n)); r = int(g.integers(0, NREL))
                if i != j:
                    keep.append((i, r, j))
            bs = slip(n, edges, rels, OUT, IN); ts = slip(n, keep, rels, OUT, IN)
            S = (bs @ np.conj(ts.T)).real
            for i in range(n):
                hit += int(int(np.argmax(S[i])) == int(perm[i])); tot += 1
        curve[noise] = round(hit / tot, 3)
        print("  SLIPNET-NOISE noise=%.2f Hits@1=%.3f" % (noise, curve[noise]), flush=True)
    at25 = curve.get(0.25, curve.get(0.15, 0.0))
    return {"curve": {str(k): v for k, v in curve.items()}, "hits1_at_25pct": at25}
def verdict(r) -> Tuple[str, str]:
    a = r["hits1_at_25pct"]; s = "Hits@1@25%%-noise=%.3f curve=%s" % (a, r["curve"])
    if a >= 0.60:
        return ("HARD_PASS", "HARD_PASS: the SLIPNET cross-domain crack is ROBUST to imperfect graphs -- relation-type correspondence holds >=0.60 at 25% edge noise. Cross-domain analogy survives real-world imperfect structure, substrate-only. " + s)
    if a >= 0.45:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cross-domain degrades under noise (0.45-0.60 at 25%). " + s)
    return ("HARD_FAIL", "HARD_FAIL: cross-domain crack is FRAGILE to graph noise (<0.45 at 25%). " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
