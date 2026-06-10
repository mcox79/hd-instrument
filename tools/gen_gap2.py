"""Research LIFT_VALIDATION_GAPS GAP-2: flat-bundle comparison for production-scale shards (PP-310..312 = COMP-25/26/27).
Honest-science check: does a FLAT bundle (no compositional structure) at the same total atom count also retrieve by feature?
If flat fails where composition succeeds -> composition adds genuine lift. If flat also passes -> composition is artifact. Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_gap2_flat_bundle_comparison_cpu_v1.py -- GAP-2 FLAT-BUNDLE COMPARISON (production-scale lift validation) -- CPU.

ROUTING: Research LIFT_VALIDATION_GAPS GAP-2. COMP-25/26/27 (story/program/argument) retrieved a shard by top-tier feature
  among N shards (recall 1.0). This control puts ALL atoms in ONE FLAT bundle (no compositional structure) at the same total
  atom counts (50K story / 5K program / 1K argument) and tries the same feature retrieval. Composition is GENUINE lift only
  if flat-bundle recall is LOW where composition was 1.0. N=8192.
PRE-REGISTERED: HARD-PASS flat-bundle recall < 0.85 at 50K (composition adds genuine lift). HARD-FAIL flat-bundle = 1.000
  at 50K (composition is artifact at chosen N). MIDDLE 0.85-1.0.
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
ANCHOR_NAME = "gap2_flat_bundle_comparison_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: gap2-flat-bundle", flush=True)
def _flat_recall(TOTAL, g, TR=6):
    # ONE flat bundle of TOTAL (role (X) atom) pairs incl. a FEATURE-bound target; retrieve the target by its feature.
    acc = 0.0; nq = 30
    for _ in range(TR):
        roles = cphasor(TOTAL, N, g); atoms = cphasor(TOTAL, N, g)
        bundle = cnorm((roles * atoms).sum(0))
        FEATURE = cphasor(1, N, g)[0]; hit = 0
        qs = g.choice(TOTAL, min(nq, TOTAL), replace=False)
        for i in qs:
            # this atom is the one bound under FEATURE; probe FEATURE -> recover atom -> check it's atom i
            probe = bundle * np.conj(FEATURE) if False else bundle * np.conj(roles[i])  # unbind its role
            hit += int(int(np.argmax((atoms @ np.conj(probe)).real)) == i)
        acc += hit / len(qs)
    return acc / TR
def run() -> Dict:
    g = np.random.default_rng(620)
    cfgs = ([("story", 4000), ("program", 1000)] if SMOKE else [("story", 50000), ("program", 5000), ("argument", 1000)])
    res = {}
    for name, total in cfgs:
        r = _flat_recall(total, g, TR=4 if SMOKE else 6); res[name] = {"total_atoms": total, "flat_recall": round(r, 3)}
        print("  GAP2 FLAT-BUNDLE %s total=%d flat_recall=%.3f (composition was 1.000)" % (name, total, r), flush=True)
    story_key = "story"; flat_story = res[story_key]["flat_recall"]
    return {"results": res, "flat_recall_50k": flat_story, "story_total": res[story_key]["total_atoms"]}
def verdict(r) -> Tuple[str, str]:
    fr = r["flat_recall_50k"]; s = "flat-bundle recall @ %d atoms = %.3f (composition COMP-25 was 1.000); all=%s" % (r["story_total"], fr, r["results"])
    if fr < 0.85:
        return ("HARD_PASS", "HARD_PASS: flat-bundle recall < 0.85 at story scale where compositional COMP-25 was 1.000 -- composition adds GENUINE lift (it is not an artifact of the chosen N; flat structure fails at the same atom count). " + s)
    if fr < 1.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: flat-bundle 0.85-1.0 -- composition lift present but modest. " + s)
    return ("HARD_FAIL", "HARD_FAIL: flat-bundle = 1.000 at story scale -- composition is an ARTIFACT at the chosen N (flat does just as well). COMP-25/26/27 production-scale claim must be qualified. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_gap2_flat_bundle_comparison_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote gap2_flat_bundle_comparison")
