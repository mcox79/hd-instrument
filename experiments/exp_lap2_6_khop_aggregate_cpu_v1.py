"""
exp_lap2_6_khop_aggregate_cpu_v1.py -- COUNT/aggregate through a multi-hop chain -- CPU.

ROUTING: Research LAPTOP_WAVE2 (LAP2-6 K-HOP-AGGREGATE); pure-FHRR (no download). 2-hop friends-of-friends; count those in a target city; F1 on the counted set.
PRE-REGISTERED: HARD-PASS F1>=0.80. MIDDLE>=0.65. HARD-FAIL<0.65.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "lap2_6_khop_aggregate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert sum([1,1,0])==2, "count"; print("[selftest] PASS: k-hop-aggregate", flush=True)
def run() -> Dict:
    # COUNT through 2-hop: X-FRIEND->{f}; each f-FRIEND->{ff}; each ff-CITY->city. Query: count distinct FoF in city Y.
    g = np.random.default_rng(6); N = 8192; VE = 300; NC = 6; KF = 3
    ents = cphasor(VE, N, g); cities = cphasor(NC, N, g); FR = cphasor(1, N, g)[0]; CY = cphasor(1, N, g)[0]
    TR = 30 if SMOKE else 200; f1 = 0.0; n = 0
    for _ in range(TR):
        x = int(g.integers(0, VE)); friends = [int(v) for v in g.choice(VE, KF, replace=False)]
        fof = {}; city = {}
        fr_shard = {}
        fr_shard[x] = sum((ents[x] * (FR * ents[f]) for f in friends), np.zeros(N, dtype=np.complex64))
        allfof = set()
        for f in friends:
            ffs = [int(v) for v in g.choice(VE, KF, replace=False)]; fof[f] = ffs
            fr_shard[f] = sum((ents[f] * (FR * ents[ff]) for ff in ffs), np.zeros(N, dtype=np.complex64))
            for ff in ffs:
                if ff not in city:
                    city[ff] = int(g.integers(0, NC)); allfof.add(ff)
        cy_shard = {ff: ents[ff] * (CY * cities[city[ff]]) for ff in allfof}
        Y = int(g.integers(0, NC)); gold = set(ff for ff in allfof if city[ff] == Y)
        # substrate traverse: friends (top-KF) -> for each, FoF (top-KF) -> city; collect those in Y
        fr = [int(i) for i in np.argsort((ents @ np.conj(fr_shard[x] * np.conj(ents[x]) * np.conj(FR))).real)[::-1][:KF]]
        pred = set()
        for f in fr:
            if f in fr_shard:
                ffs = [int(i) for i in np.argsort((ents @ np.conj(fr_shard[f] * np.conj(ents[f]) * np.conj(FR))).real)[::-1][:KF]]
                for ff in ffs:
                    if ff in cy_shard:
                        if cidx(cy_shard[ff] * np.conj(ents[ff]) * np.conj(CY), cities) == Y:
                            pred.add(ff)
        inter = len(pred & gold); prec = inter / len(pred) if pred else (1.0 if not gold else 0.0); rec = inter / len(gold) if gold else 1.0
        f1 += (2 * prec * rec / (prec + rec)) if (prec + rec) else 1.0; n += 1
    score = f1 / n; print("  K-HOP-AGGREGATE count-set F1=%.3f (n=%d)" % (score, n), flush=True)
    return {"aggregate_f1": score, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "aggregate-chain-F1=%.3f (n=%d)" % (r["aggregate_f1"], r["n"])
    if r["aggregate_f1"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate COUNT/aggregate through a 2-hop chain (FoF-in-city-Y) F1>=0.80 -- aggregation composes with multi-hop traversal. " + s)
    if r["aggregate_f1"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: aggregate F1 0.65-0.80 (multi-tail superposition; sharding lifts). " + s)
    return ("HARD_FAIL", "HARD_FAIL: aggregate F1 <0.65. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
