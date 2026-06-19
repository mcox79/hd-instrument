"""
exp_n1d_parallel_subq_native_cpu_v1.py -- parallel sub-question decomposition on the discrete-KG substrate -- CPU.

ROUTING: v1.5 LOCK batch (C2 N1d parallel sub-question on NATIVE substrate). Native counterpart to N1e (fuzzy). Decompose a 2-hop question into TWO sub-queries answerable in PARALLEL on the discrete KG: (hop1: start-r1->bridge) and, given the bridge, (hop2: bridge-r2->answer). Parallel discrete sub-queries vs the single chained K-hop. recall@1 of the answer. Tests whether parallel decomposition on native substrate matches/beats chained K-hop. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS parallel-native recall@1 >= 0.70 (matches chained K-hop on discrete). MIDDLE >= 0.55. HARD-FAIL < 0.55.
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
ANCHOR_NAME = "n1d_parallel_subq_native_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; R = cphasor(1, 64, g)[0]; b = cphasor(1, 64, g)[0]
    assert np.allclose((a * R * b) * np.conj(a * R), b, atol=1e-3), "unbind"; print("[selftest] PASS: n1d-parallel-subq-native", flush=True)
def run() -> Dict:
    g = np.random.default_rng(83); N = 8192; VE = 200; VR = 12; deg = 2; TR = 60 if SMOKE else 200
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}; M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(deg):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    def path():
        for _ in range(150):
            s = int(g.integers(0, VE)); o1 = [(r, edges[(s, r)]) for (ss, r) in edges if ss == s]
            if not o1:
                continue
            r1, b = o1[int(g.integers(0, len(o1)))]; o2 = [(r, edges[(b, r)]) for (ss, r) in edges if ss == b]
            if not o2:
                continue
            r2, a = o2[int(g.integers(0, len(o2)))]; return s, r1, b, r2, a
        return None
    chained = 0; parallel = 0; n = 0
    for _ in range(TR):
        p = path()
        if not p:
            continue
        s, r1, b, r2, a = p
        bc = cidx(M * np.conj(ents[s] * rels[r1]), ents); ac = cidx(M * np.conj(ents[bc] * rels[r2]), ents); chained += int(ac == a)
        # parallel: sub-q1 -> bridge candidates; sub-q2 anchored on each candidate -> answer; pick consistent
        sc1 = (ents @ np.conj(M * np.conj(ents[s] * rels[r1]))).real; cand = np.argsort(-sc1)[:3]
        best = -1; bs = -1e18
        for c in cand:
            sc2 = (ents @ np.conj(M * np.conj(ents[int(c)] * rels[r2]))).real; j = int(np.argmax(sc2))
            if sc1[c] + sc2[j] > bs:
                bs = sc1[c] + sc2[j]; best = j
        parallel += int(best == a); n += 1
    cr = chained / max(1, n); pr = parallel / max(1, n); print("  chained-Khop=%.3f parallel-subq-native=%.3f (n=%d)" % (cr, pr, n), flush=True)
    return {"chained": cr, "parallel": pr}
def verdict(r) -> Tuple[str, str]:
    s = "parallel-native=%.3f chained-Khop=%.3f" % (r["parallel"], r["chained"])
    if r["parallel"] >= 0.70: return ("HARD_PASS", "HARD_PASS: parallel sub-question decomposition on native substrate recall>=0.70 -- parallel matches chained K-hop on discrete (decomposition-pattern agnostic when grounded discretely). " + s)
    if r["parallel"] >= 0.55: return ("MIDDLE_BAND", "MIDDLE_BAND: parallel-native 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: parallel-native <0.55. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
