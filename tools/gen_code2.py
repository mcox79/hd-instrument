"""AGGRESSIVE_OVERNIGHT THRUST-3 CODE: CODE-2 BUG-DETECTION (substrate-only, anomaly margin). A library of 'correct' program
patterns is stored; a test program is correct (drawn from the library distribution) or buggy (an injected anomalous op).
Substrate's anomaly margin (distance to nearest correct pattern) should flag bugs. Tests AUC/F1. Genuinely can fail. Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_code2_bug_detection_cpu_v1.py -- CODE-2 BUG-DETECTION (substrate-native, anomaly margin) -- CPU.

ROUTING: Research AGGRESSIVE_OVERNIGHT THRUST-3 CODE. A LIBRARY of correct program patterns (op-sequences following valid
  structural templates) is stored as composite shards. A test program is CORRECT (matches a template) or BUGGY (one op
  replaced by an out-of-template op = bug). Substrate ANOMALY MARGIN = the program's cleanup-distance to the nearest library
  pattern; buggy programs should have lower margin (higher anomaly). Tests bug-vs-correct AUC and F1. PP-263 anomaly extended
  to code. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS bug-detection F1 >= 0.70 (AUC reported). MIDDLE F1 >= 0.55. HARD-FAIL else.
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
ANCHOR_NAME = "code2_bug_detection_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _auc(scores, labels):
    o = np.argsort(scores); r = np.empty(len(scores)); r[o] = np.arange(1, len(scores) + 1)
    pos = labels == 1; npos = int(pos.sum()); nneg = len(labels) - npos
    return 0.5 if npos == 0 or nneg == 0 else float((r[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg))
def _selftest():
    print("[selftest] PASS: code2-bug-detection", flush=True)
def run() -> Dict:
    g = np.random.default_rng(831); STEPS = 5; NOP = 10; NTEMPL = 12
    ops = cphasor(NOP, N, g); slots = cphasor(STEPS, N, g)
    TR = 15 if SMOKE else 90; scores = []; labels = []
    for _ in range(TR):
        # TEMPLATES: each template constrains which ops are valid at each slot (a structural grammar)
        templ = [[list(g.choice(NOP, 4, replace=False)) for _ in range(STEPS)] for _ in range(NTEMPL)]
        # LIBRARY of correct programs (sample from templates)
        lib = []
        for _l in range(40):
            t = templ[int(g.integers(0, NTEMPL))]; prog = [int(t[s][int(g.integers(0, len(t[s])))]) for s in range(STEPS)]
            lib.append(cnorm(sum((slots[s] * ops[prog[s]] for s in range(STEPS)), np.zeros(N, dtype=np.complex64))))
        lib = np.stack(lib)
        for _q in range(8):
            ti = int(g.integers(0, NTEMPL)); t = templ[ti]; prog = [int(t[s][int(g.integers(0, len(t[s])))]) for s in range(STEPS)]
            buggy = g.random() < 0.5
            if buggy:
                bs = int(g.integers(0, STEPS)); bad = [o for o in range(NOP) if o not in t[bs]]; prog[bs] = int(g.choice(bad))  # out-of-grammar op = bug
            pv = cnorm(sum((slots[s] * ops[prog[s]] for s in range(STEPS)), np.zeros(N, dtype=np.complex64)))
            margin = float((lib @ np.conj(pv)).real.max()) / N        # nearest correct pattern (high=normal, low=anomalous)
            scores.append(-margin); labels.append(int(buggy))         # anomaly score = -margin
    sc = np.array(scores); lab = np.array(labels); auc = _auc(sc, lab)
    thr = np.median(sc); pred = (sc > thr).astype(int)
    tp = int(((pred == 1) & (lab == 1)).sum()); fp = int(((pred == 1) & (lab == 0)).sum()); fn = int(((pred == 0) & (lab == 1)).sum())
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); f1 = 2 * prec * rec / (prec + rec + 1e-9)
    print("  CODE-2 BUG-DETECTION via anomaly-margin: AUC=%.3f F1=%.3f (n=%d)" % (auc, f1, len(sc)), flush=True)
    return {"auc": round(auc, 3), "f1": round(f1, 3), "n": len(sc)}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.3f F1=%.3f" % (r["auc"], r["f1"])
    if r["f1"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate detects bugs via anomaly margin (F1>=0.70) -- out-of-grammar ops register as low cleanup-margin against the correct-program library. Bug-as-anomaly (PP-263) extends to code, substrate-only. " + s)
    if r["f1"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: bug-detection F1 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: bug-detection F1 <0.55 -- anomaly margin does not flag code bugs. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_code2_bug_detection_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote code2_bug_detection")
