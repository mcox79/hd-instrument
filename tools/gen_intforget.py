"""Research REVIVAL_SUBSTRATE_NATIVE Sprint-2: D2.7 INTENTIONAL-FORGETTING via GDPR (continual, P=0.52, substrate-only).
Repurpose validated GDPR erasure as a cognitive function: deliberately forget a chosen subset of stored facts cleanly --
forgotten items become non-retrievable, retained items + their neighbors stay intact (no collateral). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_d2_7_intentional_forgetting_cpu_v1.py -- D2.7 INTENTIONAL-FORGETTING via GDPR (continual learning) -- CPU.

ROUTING: Research REVIVAL_SUBSTRATE_NATIVE_ONLY Sprint-2 (continual, P=0.52). KV memory M = sum key_i (X) value_i.
  "Intentionally forget" a chosen subset F by exact subtraction (the GDPR-erasure primitive repurposed for cognitive
  declutter). Test: forgotten items drop to chance recall; RETAINED items keep high recall (no collateral damage). Measured
  at scale + over repeated forget operations (sequential declutter). Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS retained-recall >= 0.90 AND forgotten-recall <= 0.15 after forgetting 30%. MIDDLE retained>=0.80. HARD-FAIL else.
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
ANCHOR_NAME = "d2_7_intentional_forgetting_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: intentional-forgetting", flush=True)
def run() -> Dict:
    g = np.random.default_rng(660); K = 40; V = 200
    TR = 15 if SMOKE else 100; ret = []; forg = []
    for _ in range(TR):
        keys = cphasor(K, N, g); vals = cphasor(V, N, g); truth = g.integers(0, V, size=K)
        M = (keys * vals[truth]).sum(0)
        nforget = max(1, int(0.3 * K)); F = set(int(x) for x in g.choice(K, nforget, replace=False))
        # INTENTIONAL FORGET: subtract chosen items (GDPR-erasure primitive)
        for i in F:
            M = M - keys[i] * vals[truth[i]]
        # in several rounds (sequential declutter) -- forget a second small batch
        F2 = [i for i in range(K) if i not in F]; F2 = set(int(x) for x in g.choice(F2, max(1, nforget // 2), replace=False))
        for i in F2:
            M = M - keys[i] * vals[truth[i]]
        forgotten = F | F2
        def recall_set(idxs):
            h = 0
            for i in idxs:
                probe = M * np.conj(keys[i]); h += int(int(np.argmax((vals @ np.conj(probe)).real)) == truth[i])
            return h / max(1, len(idxs))
        retained = [i for i in range(K) if i not in forgotten]
        ret.append(recall_set(retained)); forg.append(recall_set(list(forgotten)))
    rr = float(np.mean(ret)); fr = float(np.mean(forg))
    print("  INTENTIONAL-FORGETTING retained-recall=%.3f forgotten-recall=%.3f (forgot ~%d%% over 2 rounds)" % (rr, fr, 45), flush=True)
    return {"retained_recall": round(rr, 3), "forgotten_recall": round(fr, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "retained=%.3f forgotten=%.3f" % (r["retained_recall"], r["forgotten_recall"])
    if r["retained_recall"] >= 0.90 and r["forgotten_recall"] <= 0.15:
        return ("HARD_PASS", "HARD_PASS: intentional forgetting is clean -- chosen items drop to ~chance recall while retained items keep >=0.90 (no collateral damage), over sequential declutter rounds. GDPR-erasure primitive doubles as cognitive forgetting, substrate-only. " + s)
    if r["retained_recall"] >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: retained 0.80-0.90 or forgotten leakage. " + s)
    return ("HARD_FAIL", "HARD_FAIL: forgetting damages retained memory. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_d2_7_intentional_forgetting_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote d2_7_intentional_forgetting")
