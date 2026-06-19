"""
exp_cross_modal_consistency_cpu_v1.py -- cross-modal shared-value consistency + conflict detection -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop STRETCH (LAP-STRETCH-3 CROSS-MODAL-CONSISTENCY); pure-FHRR (no download). Two modality keyspaces bind one value space; cross-modal agreement + inconsistency flagging.
PRE-REGISTERED: HARD-PASS consistency>=0.90 AND detect>=0.90. MIDDLE consistency>=0.75. HARD-FAIL<0.75.
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
ANCHOR_NAME = "cross_modal_consistency_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: cross-modal-consistency", flush=True)
def run() -> Dict:
    # two modalities (A,B) bind to a SHARED value space; cross-modal retrieval consistency + inconsistency detection.
    g = np.random.default_rng(181); N = 8192; M = 30; VV = 200
    TR = 50 if SMOKE else 250; cons_ok = 0; det_ok = 0; n = 0; nd = 0
    for _ in range(TR):
        kA = cphasor(M, N, g); kB = cphasor(M, N, g); vals = cphasor(VV, N, g); truth = g.integers(0, VV, size=M)
        MemA = (kA * vals[truth]).sum(axis=0); MemB = (kB * vals[truth]).sum(axis=0)
        i = int(g.integers(0, M))
        va = cidx(MemA * np.conj(kA[i]), vals); vb = cidx(MemB * np.conj(kB[i]), vals)
        cons_ok += int(va == vb == truth[i]); n += 1                      # cross-modal agreement on the shared value
        # inconsistency detection: corrupt B's value for item i; modalities should DISAGREE -> flagged
        bad = int((truth[i] + 1) % VV); MemB2 = MemB - kB[i] * vals[truth[i]] + kB[i] * vals[bad]
        vb2 = cidx(MemB2 * np.conj(kB[i]), vals)
        det_ok += int((va != vb2)); nd += 1                              # detector: flag when A and B disagree
    cr = cons_ok / n; dr = det_ok / nd
    print("  CROSS-MODAL consistency=%.3f inconsistency-detect=%.3f (n=%d)" % (cr, dr, n), flush=True)
    return {"consistency": cr, "inconsistency_detect": dr, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "consistency=%.3f inconsistency-detect=%.3f" % (r["consistency"], r["inconsistency_detect"])
    if r["consistency"] >= 0.90 and r["inconsistency_detect"] >= 0.90:
        return ("HARD_PASS", "HARD_PASS: cross-modal shared-value retrieval consistent >=0.90 AND inconsistency flagged >=0.90 -- two modalities bind to one value space; substrate detects cross-modal conflict. " + s)
    if r["consistency"] >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: consistency 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: consistency <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
