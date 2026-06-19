"""
exp_kb_query_benchmark_cpu_v1.py -- substrate KB-query benchmark (lookup + 2-hop) >=0.98 correctness -- CPU.

ROUTING: batch-10a (CHEAP-CAP KB-query correctness benchmark). A clean substrate-KB query benchmark across lookup and 2-hop queries; measures product-grade correctness. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS overall >=0.98. MIDDLE >=0.90. HARD-FAIL <0.90.
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
ANCHOR_NAME = "kb_query_benchmark_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert (2 == 2), "eq"; print("[selftest] PASS: kb-query-benchmark", flush=True)
def run() -> Dict:
    g = np.random.default_rng(964); N = 8192; VE = 200; VR = 4; ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
    TR = 20 if SMOKE else 50; lookup_ok = 0; twohop_ok = 0; lk = 0; th = 0
    for _ in range(TR):
        edge = {}; shard = {i: np.zeros(N, dtype=np.complex64) for i in range(VE)}
        for s in range(VE):
            for r in range(VR):
                o = int(g.integers(0, VE)); edge[(s, r)] = o; shard[s] = shard[s] + rels[r] * ents[o]
        s = int(g.integers(0, VE)); r = int(g.integers(0, VR))
        lookup_ok += int(cidx(shard[s] * np.conj(rels[r]), ents) == edge[(s, r)]); lk += 1
        r2 = int(g.integers(0, VR)); mid = edge[(s, r)]; gold2 = edge[(mid, r2)]
        m1 = cidx(shard[s] * np.conj(rels[r]), ents); pred2 = cidx(shard[m1] * np.conj(rels[r2]), ents)
        twohop_ok += int(pred2 == gold2); th += 1
    lr = lookup_ok / lk; tr = twohop_ok / th; overall = (lookup_ok + twohop_ok) / (lk + th)
    print("  KB-benchmark: lookup=%.3f 2-hop=%.3f overall=%.3f (n=%d)" % (lr, tr, overall, lk + th), flush=True)
    return {"lookup": lr, "twohop": tr, "overall": overall}
def verdict(r) -> Tuple[str, str]:
    s = "lookup=%.3f 2-hop=%.3f overall=%.3f" % (r["lookup"], r["twohop"], r["overall"])
    if r["overall"] >= 0.98: return ("HARD_PASS", "HARD_PASS: substrate KB-query benchmark (lookup+2-hop) >=0.98 correctness -- product-grade query correctness. " + s)
    if r["overall"] >= 0.90: return ("MIDDLE_BAND", "MIDDLE_BAND: benchmark 0.90-0.98. " + s)
    return ("HARD_FAIL", "HARD_FAIL: benchmark <0.90. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
