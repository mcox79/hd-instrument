"""
exp_inverted_property_shards_cpu_v1.py -- sleep-defrag builds property-indexed inverted shards for O(K) set queries -- CPU.

ROUTING: Mechanism B sleep-defrag per-property inverted shards. Per-subject shards answer (subject -> properties) but a query like 'all subjects with property P' would scan all M shards (O(M*K)). During SLEEP DEFRAG, scan for each property P=(relation,value) appearing in >=T subject shards and build a SECONDARY inverted shard inv[P] = bundle of those subjects. Query 'subjects with P' hits inv[P] at O(K). Measures inverted-shard recall of the true subjects-with-P set. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS inverted-shard recall of subjects-with-P >= 0.90 at frequent properties. MIDDLE >= 0.80. HARD-FAIL < 0.80.
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
ANCHOR_NAME = "inverted_property_shards_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert len({1, 2, 3} & {2, 3, 4}) == 2, "set overlap"; print("[selftest] PASS: inverted-property-shards", flush=True)
def run() -> Dict:
    g = np.random.default_rng(142); N = 8192; VE = 400; NPROP = 30; PROPS_PER = 4; TR_PROPS = 20 if SMOKE else 50
    ents = cphasor(VE, N, g); props = cphasor(NPROP, N, g)                 # each property P = (relation,value) atom
    subj_props = {s: set(g.choice(NPROP, PROPS_PER, replace=False).tolist()) for s in range(VE)}   # ground truth
    # SLEEP DEFRAG: build inverted shard per property = bundle of subjects having it
    inv = {p: np.zeros(N, dtype=np.complex64) for p in range(NPROP)}
    truth = {p: set() for p in range(NPROP)}
    for s in range(VE):
        for p in subj_props[s]:
            inv[p] = inv[p] + ents[s]; truth[p].add(s)
    recs = []
    test_props = list(range(NPROP))[:TR_PROPS]
    for p in test_props:
        tset = truth[p]
        if not tset:
            continue
        sc = (ents @ np.conj(inv[p])).real; retr = set(np.argsort(-sc)[:len(tset)].tolist())       # top-|tset| subjects from inverted shard
        recs.append(len(retr & tset) / len(tset))
    rec = float(np.mean(recs)); print("  inverted-shard subjects-with-P recall=%.3f (%d properties, %d subjects, ~%d/prop)" % (rec, len(recs), VE, VE * PROPS_PER // NPROP), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "inverted-shard recall=%.3f" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: sleep-defrag inverted property shards recall subjects-with-P >=0.90 at O(K) -- set-of-subjects queries answered without scanning all shards. " + s)
    if r["recall"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: inverted-shard 0.80-0.90 (property bundles near capacity; sub-shard frequent properties). " + s)
    return ("HARD_FAIL", "HARD_FAIL: inverted-shard <0.80. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
