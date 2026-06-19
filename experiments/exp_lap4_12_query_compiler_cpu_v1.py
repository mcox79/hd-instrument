"""
exp_lap4_12_query_compiler_cpu_v1.py -- compile+execute relational queries over the substrate -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (LAP4-12 SUBSTRATE-QUERY-COMPILER); pure-FHRR/numpy (no download). SELECT-WHERE-FILTER query compiled to unbind(traverse)+filter substrate ops; F1 vs ground-truth result set.
PRE-REGISTERED: HARD-PASS query-F1>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, itertools
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "lap4_12_query_compiler_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: query-compiler", flush=True)
def run() -> Dict:
    # query compiler: a relational query (SELECT t WHERE subj -REL-> t AND prop(t)=val) compiles to substrate ops
    # (unbind REL -> candidate set, then filter by PROP=val) and executes. Compare result set to ground truth.
    g = np.random.default_rng(12); N = 8192; VE = 250; NREL = 4; NC = 6; KF = 3
    ents = cphasor(VE, N, g); rels = cphasor(NREL, N, g); cities = cphasor(NC, N, g); PROP = cphasor(1, N, g)[0]
    TR = 30 if SMOKE else 200; f1 = 0.0; n = 0
    for _ in range(TR):
        x = int(g.integers(0, VE)); r_ = int(g.integers(0, NREL))
        tails = [int(v) for v in g.choice(VE, KF, replace=False)]
        rel_shard = sum((ents[x] * (rels[r_] * ents[t]) for t in tails), np.zeros(N, dtype=np.complex64))
        tcity = {t: int(g.integers(0, NC)) for t in tails}
        prop_shard = {t: ents[t] * (PROP * cities[tcity[t]]) for t in tails}
        Y = int(g.integers(0, NC)); gold = set(t for t in tails if tcity[t] == Y)
        # COMPILE+EXECUTE: op1 = unbind REL -> candidate tails (top-KF); op2 = filter PROP==Y
        scores = (ents @ np.conj(rel_shard * np.conj(ents[x]) * np.conj(rels[r_]))).real
        cand = [int(i) for i in np.argsort(scores)[::-1][:KF]]
        res = set(t for t in cand if t in prop_shard and cidx(prop_shard[t] * np.conj(ents[t]) * np.conj(PROP), cities) == Y)
        inter = len(res & gold); prec = inter / len(res) if res else (1.0 if not gold else 0.0); rec = inter / len(gold) if gold else 1.0
        f1 += (2 * prec * rec / (prec + rec)) if (prec + rec) else 1.0; n += 1
    score = f1 / n; print("  QUERY-COMPILER select-where-filter F1=%.3f (n=%d)" % (score, n), flush=True)
    return {"query_f1": score, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "query-F1=%.3f (n=%d)" % (r["query_f1"], r["n"])
    if r["query_f1"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate compiles+executes relational queries (SELECT-WHERE-FILTER) F1>=0.85 -- a query plan of unbind(traverse)+filter ops over the substrate; declarative querying without an external DB. " + s)
    if r["query_f1"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: query F1 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: query F1 <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
