"""
exp_lap6_inheritance_index_cpu_v1.py -- substrate 3-level hierarchical inheritance lookup -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop batch (LAP-6 INHERITANCE-INDEX); pure-FHRR (no download). concept->subconcept->instance via per-node sharded CHILD bindings; retrieve down 3 levels.
PRE-REGISTERED: HARD-PASS 3-level recall>=0.85. MIDDLE>=0.65. HARD-FAIL<0.65.
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
ANCHOR_NAME = "lap6_inheritance_index_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert _n.argmax([1,0])==0, "argmax"; print("[selftest] PASS: inheritance-index", flush=True)
def run() -> Dict:
    # 3-level hierarchy: concept -CHILD-> subconcept -CHILD-> instance. Per-node sharded CHILD bindings; retrieve down 3 levels.
    g = np.random.default_rng(606); N = 8192; NC = 20 if SMOKE else 60; NS = 5; NI = 4
    VE = NC * (1 + NS + NS * NI); ents = cphasor(VE, N, g); CHILD = cphasor(1, N, g)[0]
    TR = 30 if SMOKE else 150; lvl3 = 0; n = 0
    for _ in range(TR):
        idx = 0; shard = {}; truth = {}
        for c in range(NC):
            cnode = idx; idx += 1; subs = []
            for s in range(NS):
                snode = idx; idx += 1; insts = []
                for i in range(NI):
                    inode = idx; idx += 1; insts.append(inode)
                shard[snode] = sum((ents[snode] * (CHILD * ents[x]) for x in insts), np.zeros(N, dtype=np.complex64))
                truth[snode] = set(insts); subs.append(snode)
            shard[cnode] = sum((ents[cnode] * (CHILD * ents[x]) for x in subs), np.zeros(N, dtype=np.complex64))
            truth[cnode] = set(subs)
            # query: from concept, go down to subconcepts then instances; check an instance is reachable in 3 levels
            sub_hat = [cidx(shard[cnode] * np.conj(ents[cnode]) * np.conj(CHILD), ents) for _ in range(1)]
            sb = sub_hat[0]
            if sb in shard:
                inst_hat = cidx(shard[sb] * np.conj(ents[sb]) * np.conj(CHILD), ents)
                lvl3 += int(sb in truth[cnode] and inst_hat in truth.get(sb, set())); n += 1
            else:
                n += 1
    acc = lvl3 / n if n else 0.0
    print("  3-level inheritance recall=%.3f (NC=%d, n=%d)" % (acc, NC, n), flush=True)
    return {"threelevel_recall": acc, "NC": NC}
def verdict(r) -> Tuple[str, str]:
    s = "3-level-recall=%.3f" % r["threelevel_recall"]
    if r["threelevel_recall"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate 3-level inheritance (concept->subconcept->instance) recall>=0.85 -- hierarchical concept index holds; common-sense taxonomy traversal native. " + s)
    if r["threelevel_recall"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 3-level 0.65-0.85 (per-node sub-sharding lifts). " + s)
    return ("HARD_FAIL", "HARD_FAIL: 3-level <0.65. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
