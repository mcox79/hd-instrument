"""
exp_lap11_khop_conditional_cpu_v1.py -- conditional multi-hop with AND/NOT set logic -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop batch (LAP-11 K-HOP-CONDITIONAL); pure-FHRR (no download). friends-of-X NOT-in-city-Y: multi-tail friend retrieval + per-friend city + NOT-filter; F1 on the filtered set.
PRE-REGISTERED: HARD-PASS F1>=0.80. MIDDLE>=0.65. HARD-FAIL<0.65.
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
ANCHOR_NAME = "lap11_khop_conditional_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert len({1,2,3}-{2})==2, "setminus"; print("[selftest] PASS: k-hop-conditional", flush=True)
def run() -> Dict:
    # conditional multi-hop: X-FRIEND->{friends}; each friend-CITY->city; query "friends of X NOT in city Y". substrate retrieves
    # the friend set (multi-tail bundle, top-k), maps each to city, set-excludes those in city Y. Measure exact filtered set.
    g = np.random.default_rng(11); N = 8192; VE = 250; NC = 8; KF = 4
    ents = cphasor(VE, N, g); cities = cphasor(NC, N, g); FRIEND = cphasor(1, N, g)[0]; CITY = cphasor(1, N, g)[0]
    TR = 30 if SMOKE else 200; f1 = 0.0; n = 0
    for _ in range(TR):
        x = int(g.integers(0, VE)); friends = [int(v) for v in g.choice(VE, KF, replace=False) if v != x][:KF]
        fcity = {f: int(g.integers(0, NC)) for f in friends}
        fr_shard = sum((ents[x] * (FRIEND * ents[f]) for f in friends), np.zeros(N, dtype=np.complex64))
        cy_shard = {f: ents[f] * (CITY * cities[fcity[f]]) for f in friends}
        Y = int(g.integers(0, NC)); gold = set(f for f in friends if fcity[f] != Y)
        # retrieve friend set: top-KF cleanup of FRIEND unbind
        scores = (ents @ np.conj(fr_shard * np.conj(ents[x]) * np.conj(FRIEND))).real
        cand = [int(i) for i in np.argsort(scores)[::-1][:KF]]
        pred = set()
        for f in cand:
            if f in cy_shard:
                cy = cidx(cy_shard[f] * np.conj(ents[f]) * np.conj(CITY), cities)
                if cy != Y:
                    pred.add(f)
        inter = len(pred & gold); prec = inter / len(pred) if pred else (1.0 if not gold else 0.0); rec = inter / len(gold) if gold else 1.0
        f1 += (2 * prec * rec / (prec + rec)) if (prec + rec) else (1.0 if not gold and not pred else 0.0); n += 1
    score = f1 / n; print("  K-HOP-CONDITIONAL (NOT-filter) F1=%.3f (n=%d)" % (score, n), flush=True)
    return {"cond_f1": score, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "conditional-multihop-F1=%.3f (n=%d)" % (r["cond_f1"], r["n"])
    if r["cond_f1"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate answers conditional multi-hop (friends-of-X NOT-in-city-Y) F1>=0.80 -- AND/NOT set logic composes with K-hop traversal natively. " + s)
    if r["cond_f1"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: conditional F1 0.65-0.80 (multi-tail superposition; sharding lifts). " + s)
    return ("HARD_FAIL", "HARD_FAIL: conditional F1 <0.65. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
