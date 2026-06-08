"""
exp_type_confusion_sharded_cpu_v1.py -- same-name-different-referent disambiguation via per-name sharding (rescue of N5 0.75) -- CPU.

ROUTING: refill batch (N5 RESCUE: per-name sharding). N5 (monolithic bundle) hit only 0.75 because 600 facts in one bundle overloaded it. Rescue: SHARD by name -- each name's (sense,context,referent) facts live in their own sub-bundle. Context-conditioned disambiguation should jump to near-1.0, demonstrating sharding fixes named-entity ambiguity at scale (the locked invariant). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS sharded disambiguation >= 0.95 (and beats N5 monolithic 0.75). MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "type_confusion_sharded_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; c = cphasor(1, 32, g)[0]; r = cphasor(1, 32, g)[0]
    assert np.allclose(a * c * r * np.conj(a * c), r, atol=1e-3), "name-ctx bind"; print("[selftest] PASS: type-confusion-sharded", flush=True)
def run() -> Dict:
    g = np.random.default_rng(324); N = 4096; NNAME = 50; SENSE = 3; NCTX = 40; TR = 60 if SMOKE else 200
    names = cphasor(NNAME, N, g); ctxs = cphasor(NCTX, N, g); VR = NNAME * SENSE; refs = cphasor(VR, N, g)
    shard = {n: np.zeros(N, dtype=np.complex64) for n in range(NNAME)}; sense_ctx = {}
    for nm in range(NNAME):
        cset_all = g.choice(NCTX, 4 * SENSE, replace=False)                   # DISJOINT contexts across this name's senses
        for se in range(SENSE):
            ref_id = nm * SENSE + se; cset = cset_all[se * 4:(se + 1) * 4]; sense_ctx[(nm, se)] = set(int(x) for x in cset)
            for c in cset:
                shard[nm] = shard[nm] + names[nm] * ctxs[int(c)] * refs[ref_id]   # per-NAME shard
    hit = 0; n = 0
    for _ in range(TR):
        nm = int(g.integers(0, NNAME)); se = int(g.integers(0, SENSE)); c = int(g.choice(list(sense_ctx[(nm, se)])))
        pred = cidx(shard[nm] * np.conj(names[nm] * ctxs[c]), refs); hit += int(pred == nm * SENSE + se); n += 1
    rec = hit / n; print("  sharded type-confusion disambiguation=%.3f (vs N5 monolithic 0.75)" % rec, flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "sharded disambiguation=%.3f" % r["recall"]
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: per-name sharding lifts disambiguation to >=0.95 (from N5 monolithic 0.75) -- sharding fixes named-entity ambiguity. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: sharded 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sharded <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
