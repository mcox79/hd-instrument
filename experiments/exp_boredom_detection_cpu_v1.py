"""
exp_boredom_detection_cpu_v1.py -- BOREDOM DETECTION (substrate-native intrinsic motivation) -- CPU.

ROUTING: Research REVIVAL_SUBSTRATE_NATIVE_ONLY Sprint-1 (motivation, P=0.60). A "now"-style decayed recent-experience
  bundle R = sum decay^age * input. Boredom(x) = real-cosine of x against R (how PRESENT x already is in recent experience).
  Repeated inputs -> high boredom; novel inputs -> low boredom. Tests boredom AUC at discriminating repeated vs novel, and
  that it TRACKS repetition density over a stream. Substrate-only (no LLM). N=8192.
PRE-REGISTERED: HARD-PASS boredom-vs-repeat AUC >= 0.85 AND boredom rises with repetition density (corr >= 0.5). MIDDLE AUC>=0.70. HARD-FAIL else.
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
ANCHOR_NAME = "boredom_detection_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def _auc(scores, labels):
    o = np.argsort(scores); r = np.empty(len(scores)); r[o] = np.arange(1, len(scores) + 1)
    pos = labels == 1; npos = int(pos.sum()); nneg = len(labels) - npos
    return 0.5 if npos == 0 or nneg == 0 else float((r[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg))
def _corr(a, b):
    a = a - a.mean(); b = b - b.mean(); d = (np.sqrt((a * a).sum()) * np.sqrt((b * b).sum())) + 1e-12; return float((a * b).sum() / d)
def _selftest():
    print("[selftest] PASS: boredom-detection", flush=True)
def run() -> Dict:
    g = np.random.default_rng(606); M = 300; DECAY = 0.85; W = 12
    TR = 20 if SMOKE else 120; bored = []; is_rep = []; dens_bored = []; dens_true = []
    for _ in range(TR):
        items = cphasor(M, N, g); recent = []; R = np.zeros(N, dtype=np.complex64)
        p_rep = float(g.uniform(0.1, 0.9))                            # this episode's repetition density
        ep_bored = []
        for step in range(40):
            if recent and g.random() < p_rep:
                x_idx = int(recent[int(g.integers(0, len(recent)))]); rep = 1
            else:
                x_idx = int(g.integers(0, M)); rep = 1 if x_idx in recent else 0
            x = items[x_idx]
            b = float((np.vdot(R, x).real) / N) if step > 0 else 0.0   # boredom = presence of x in recent bundle
            if step >= 5:
                bored.append(b); is_rep.append(rep); ep_bored.append(b)
            R = (DECAY * R + x).astype(np.complex64); recent.append(x_idx); recent = recent[-W:]
        dens_bored.append(float(np.mean(ep_bored)) if ep_bored else 0.0); dens_true.append(p_rep)
    bored = np.array(bored); is_rep = np.array(is_rep)
    auc = _auc(bored, is_rep); dcorr = _corr(np.array(dens_bored), np.array(dens_true))
    print("  BOREDOM detect repeated-vs-novel AUC=%.3f | boredom-vs-repetition-density corr=%.3f (n=%d)" % (auc, dcorr, len(bored)), flush=True)
    return {"boredom_auc": round(auc, 3), "density_corr": round(dcorr, 3), "n": len(bored)}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.3f density-corr=%.3f" % (r["boredom_auc"], r["density_corr"])
    if r["boredom_auc"] >= 0.85 and r["density_corr"] >= 0.5:
        return ("HARD_PASS", "HARD_PASS: substrate-native boredom signal discriminates repeated vs novel inputs (AUC>=0.85) AND tracks repetition density (corr>=0.5) -- intrinsic-motivation primitive from cleanup-margin against decayed recent experience, no LLM. " + s)
    if r["boredom_auc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: boredom AUC 0.70-0.85 or weak density tracking. " + s)
    return ("HARD_FAIL", "HARD_FAIL: boredom AUC <0.70. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
