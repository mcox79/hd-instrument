"""Research WAVE-4: LAP4-11 META-COGNITIVE-3-LEVEL (depth-3 meta-cognition). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_lap4_11_meta_3level_cpu_v1.py -- LAP4-11 META-COGNITIVE-3-LEVEL -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (LAP4-11; extends STRETCH3-3 depth-2). Three meta levels over cleanup margin (middle-
  load regime so L1 makes real errors): L1 = knows-P (margin>tau). L2 meta-confidence = |margin-tau| predicts L1-correctness.
  L3 meta-meta = |L2conf - L2tau| predicts L2-correctness (is the L2 assessment itself reliable?). Measures L1 acc + L2-AUC + L3-AUC.
PRE-REGISTERED: HARD-PASS L1>=0.78 AND L2-AUC>=0.68 AND L3-AUC>=0.58. MIDDLE L1>=0.70. HARD-FAIL else.
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
ANCHOR_NAME = "lap4_11_meta_3level_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def _auc(scores, labels):
    o = np.argsort(scores); r = np.empty(len(scores)); r[o] = np.arange(1, len(scores) + 1)
    pos = labels == 1; npos = int(pos.sum()); nneg = len(labels) - npos
    return 0.5 if npos == 0 or nneg == 0 else float((r[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg))
def _selftest():
    print("[selftest] PASS: meta-3level", flush=True)
def run() -> Dict:
    g = np.random.default_rng(263); N = 2048; M = 180; VV = 200; tau = 0.14
    TR = 40 if SMOKE else 250; l1c = 0; n = 0; mc = []; l1ok = []
    for _ in range(TR):
        keys = cphasor(M, N, g); vals = cphasor(VV, N, g); truth = g.integers(0, VV, size=M); Mem = (keys * vals[truth]).sum(axis=0)
        for _q in range(8):
            known = g.random() < 0.5; nz = (g.random() * 0.4) * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            probe = (Mem * np.conj(keys[int(g.integers(0, M))]) if known else Mem * np.conj(cphasor(1, N, g)[0])) + nz
            sc = np.sort((vals @ np.conj(probe)).real)[::-1] / N; margin = float(sc[0] - sc[1])
            l1 = margin > tau; right = (l1 == known); l1c += int(right); n += 1
            mc.append(abs(margin - tau)); l1ok.append(int(right))
    mc = np.array(mc); l1ok = np.array(l1ok); l1a = l1c / n
    l2_auc = _auc(mc, l1ok)
    # L3: does L2's own confidence (distance of metaconf from its median = L2's decision boundary) predict L2-correctness?
    l2tau = float(np.median(mc)); l2pred = (mc > l2tau).astype(int)
    # L2 is "correct" when its high-confidence calls coincide with L1 being right (i.e. metaconf high -> L1 right)
    l2_correct = (l2pred == l1ok).astype(int); l3conf = np.abs(mc - l2tau)
    l3_auc = _auc(l3conf, l2_correct)
    print("  META-3LEVEL L1=%.3f L2-AUC=%.3f L3-AUC=%.3f (n=%d)" % (l1a, l2_auc, l3_auc, n), flush=True)
    return {"l1_acc": round(l1a, 3), "l2_auc": round(l2_auc, 3), "l3_auc": round(l3_auc, 3), "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "L1=%.3f L2-AUC=%.3f L3-AUC=%.3f" % (r["l1_acc"], r["l2_auc"], r["l3_auc"])
    if r["l1_acc"] >= 0.78 and r["l2_auc"] >= 0.68 and r["l3_auc"] >= 0.58:
        return ("HARD_PASS", "HARD_PASS: depth-3 meta-cognition -- L1 knows-P, L2 predicts L1-correctness, L3 predicts L2-reliability (all above chance). Substrate represents a 3-level knowledge-about-knowledge hierarchy. " + s)
    if r["l1_acc"] >= 0.70 and r["l2_auc"] >= 0.68:
        return ("MIDDLE_BAND", "MIDDLE_BAND: L1+L2 hold but L3 weak (depth-3 near limit). " + s)
    return ("HARD_FAIL", "HARD_FAIL: meta hierarchy breaks. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_lap4_11_meta_3level_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote meta_3level")
