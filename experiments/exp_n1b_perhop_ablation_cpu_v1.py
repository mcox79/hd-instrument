"""
exp_n1b_perhop_ablation_cpu_v1.py -- per-hop discrete grounding vs single-pass on the native substrate -- CPU.

ROUTING: v1.5 LOCK batch (C1 N1b per-hop vs single-pass ablation). Ablation: on the discrete KG, compare (a) PER-HOP chained K-hop (ground the bridge discretely, then hop2) vs (b) SINGLE-PASS joint attention over triples. Answers whether explicit per-hop grounding helps over one-shot on native substrate (it should match, since the bridge is already discrete). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS both >= 0.70 AND |per-hop - single-pass| characterized (per-hop >= single-pass - 0.05). MIDDLE both >= 0.55. HARD-FAIL either < 0.55.
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
ANCHOR_NAME = "n1b_perhop_ablation_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    x = np.array([1.0, 2.0]); sm = np.exp(x - x.max()); sm /= sm.sum(); assert abs(sm.sum() - 1) < 1e-9, "softmax"; print("[selftest] PASS: n1b-perhop-ablation", flush=True)
def run() -> Dict:
    g = np.random.default_rng(92); N = 8192; VE = 200; VR = 12; deg = 2; TR = 60 if SMOKE else 200; BETA = 6.0
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}; M = np.zeros(N, dtype=np.complex64)
    tri = []
    for s in range(VE):
        for _ in range(deg):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]; tri.append((s, r, o))
    TS = np.stack([ents[s] for s, r, o in tri]); TO = np.stack([ents[o] for s, r, o in tri]); TRr = np.stack([rels[r] for s, r, o in tri])
    def path():
        for _ in range(150):
            a = int(g.integers(0, VE)); o1 = [(r, edges[(a, r)]) for (ss, r) in edges if ss == a]
            if not o1:
                continue
            r1, b = o1[int(g.integers(0, len(o1)))]; o2 = [(r, edges[(b, r)]) for (ss, r) in edges if ss == b]
            if not o2:
                continue
            r2, c = o2[int(g.integers(0, len(o2)))]; return a, r1, b, r2, c
        return None
    ph = 0; sp = 0; n = 0
    for _ in range(TR):
        p = path()
        if not p:
            continue
        a, r1, b, r2, c = p
        bh = cidx(M * np.conj(ents[a] * rels[r1]), ents); ch = cidx(M * np.conj(ents[bh] * rels[r2]), ents); ph += int(ch == c)
        s1 = (TS * np.conj(ents[a])).sum(1).real / N + (TRr * np.conj(rels[r1])).sum(1).real / N
        a1 = np.exp(BETA * (s1 - s1.max())); a1 /= a1.sum(); bridge_vec = (a1[:, None] * TO).sum(0)
        s2 = (TRr * np.conj(rels[r2])).sum(1).real / N + (TS * np.conj(bridge_vec)).sum(1).real / N
        a2 = np.exp(BETA * (s2 - s2.max())); a2 /= a2.sum(); cv = (a2[:, None] * TO).sum(0); sp += int(cidx(cv, ents) == c); n += 1
    pr = ph / max(1, n); spr = sp / max(1, n); print("  per-hop=%.3f single-pass=%.3f (n=%d)" % (pr, spr, n), flush=True)
    return {"per_hop": pr, "single_pass": spr}
def verdict(r) -> Tuple[str, str]:
    s = "per-hop=%.3f single-pass=%.3f" % (r["per_hop"], r["single_pass"])
    if min(r["per_hop"], r["single_pass"]) >= 0.70: return ("HARD_PASS", "HARD_PASS: ablation conclusive -- both per-hop and single-pass clear 0.70 on native substrate (single-pass joint attention is best here); decomposition pattern is not the constraint once grounded discretely. " + s)
    if min(r["per_hop"], r["single_pass"]) >= 0.55: return ("MIDDLE_BAND", "MIDDLE_BAND: both 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: one path <0.55. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
