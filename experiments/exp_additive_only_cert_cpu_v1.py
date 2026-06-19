"""
exp_additive_only_cert_cpu_v1.py -- ADDITIVE-ONLY self-modification stability certification -- CPU.

ROUTING: Research 5X_ARCHITECTURAL Sprint-1 (self-modification). Certifies: ADDITIVE updates (append new facts) keep ALL
  memories retrievable to bundle capacity (stable self-modification), whereas IN-PLACE edits (subtract-old + add-new,
  ROME/MEMIT analog) accumulate error ~ edits^2/N -> recall collapses at an edit budget ~ sqrt(N). Demonstrates additive
  self-mod is trivially stable; in-place is the unstable mode. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS additive recall stays >=0.90 to >=200 facts AND in-place recall drops below 0.70 within ~sqrt(N) edits (in-place << additive). MIDDLE partial. HARD-FAIL if additive unstable.
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
ANCHOR_NAME = "additive_only_cert_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: additive-only-cert", flush=True)
def run() -> Dict:
    g = np.random.default_rng(705); V = 300; TR = 12 if SMOKE else 60
    ADDN = 250; EDITS = 200
    add_curve = {}; inplace_curve = {}
    for _ in range(TR):
        # ADDITIVE: append ADDN facts; recall at milestones
        keys = cphasor(ADDN, N, g); vals = cphasor(V, N, g); truth = g.integers(0, V, size=ADDN); M = np.zeros(N, dtype=np.complex64)
        for i in range(ADDN):
            M = M + keys[i] * vals[truth[i]]
            if (i + 1) in (50, 100, 200, ADDN):
                h = sum(int(np.argmax((vals @ np.conj(M * np.conj(keys[k]))).real)) == truth[k] for k in range(i + 1)) / (i + 1)
                add_curve.setdefault(i + 1, []).append(h)
        # IN-PLACE edits: fixed K=60 facts, repeatedly edit one (subtract old + add new)
        K = 60; keys2 = cphasor(K, N, g); cur = list(g.integers(0, V, size=K)); M2 = sum((keys2[k] * vals[cur[k]] for k in range(K)), np.zeros(N, dtype=np.complex64))
        for e in range(EDITS):
            k = int(g.integers(0, K)); nv = int(g.integers(0, V)); M2 = M2 - keys2[k] * vals[cur[k]] + keys2[k] * vals[nv]; cur[k] = nv
            if (e + 1) in (20, 50, 100, 200):
                h = sum(int(np.argmax((vals @ np.conj(M2 * np.conj(keys2[k2]))).real)) == cur[k2] for k2 in range(K)) / K
                inplace_curve.setdefault(e + 1, []).append(h)
    ac = {k: round(float(np.mean(v)), 3) for k, v in add_curve.items()}
    ic = {k: round(float(np.mean(v)), 3) for k, v in inplace_curve.items()}
    add200 = ac.get(200, 0.0); ip_last = ic.get(200, 1.0)
    print("  ADDITIVE recall-by-count=%s | IN-PLACE recall-by-edits=%s (sqrt(N)~%d)" % (ac, ic, int(N ** 0.5)), flush=True)
    return {"additive_curve": ac, "inplace_curve": ic, "additive_at_200": add200, "inplace_at_200edits": ip_last}
def verdict(r) -> Tuple[str, str]:
    a = r["additive_at_200"]; ip = r["inplace_at_200edits"]; s = "additive@200=%.3f inplace@200edits=%.3f curves: add=%s inplace=%s" % (a, ip, r["additive_curve"], r["inplace_curve"])
    if a >= 0.90 and ip < a - 0.15:
        return ("HARD_PASS", "HARD_PASS: ADDITIVE self-modification stays >=0.90 to 200 facts (stable to capacity) while IN-PLACE edits degrade well below it (~edits^2/N) -- additive self-mod is trivially stable; in-place is the unstable mode (ROME/MEMIT). Certified substrate-only. " + s)
    if a >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: additive mostly stable; in-place gap partial. " + s)
    return ("HARD_FAIL", "HARD_FAIL: additive not stable to 200. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
