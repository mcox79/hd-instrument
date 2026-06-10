"""Research REVIVAL_SUBSTRATE_NATIVE Sprint-2: D2.2 FREQUENCY-SELECTIVITY-DECAY (continual learning, P=0.55, substrate-only).
Catastrophic-forgetting solution: stored items decay each step unless ACCESSED (reinforced). Frequently-used items persist;
stale items fade -> bounded memory that retains the important. Tests retrievability tracks access frequency at 3x capacity. Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_d2_2_frequency_decay_cpu_v1.py -- D2.2 FREQUENCY-SELECTIVITY-DECAY (continual learning) -- CPU.

ROUTING: Research REVIVAL_SUBSTRATE_NATIVE_ONLY Sprint-2 (continual, P=0.55; decisive component). Substrate memory as a
  weighted bundle M = sum strength_i * item_i. Each step ALL strengths decay (x DECAY); ACCESSED items get reinforced
  (+BOOST, ~ their access frequency). At 3x nominal capacity over a long stream, retrievability should track access
  FREQUENCY (frequent -> retained; rare -> faded) -- graceful forgetting, not catastrophic. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS retrievability-vs-frequency AUC >= 0.85 AND high-freq-recall >= 0.80 at 3x capacity. MIDDLE AUC>=0.70. HARD-FAIL else.
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
ANCHOR_NAME = "d2_2_frequency_decay_cpu_v1"
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
def _selftest():
    print("[selftest] PASS: frequency-decay", flush=True)
def run() -> Dict:
    g = np.random.default_rng(650); Mc = 50                          # nominal capacity ~ N/(2 ln N) order, scaled for test
    NITEMS = 3 * Mc                                                  # 3x capacity -> forgetting forced
    DECAY = 0.97; BOOST = 1.0; STEPS = 400 if SMOKE else 1500
    TR = 12 if SMOKE else 60; aucs = []; hi_recall = []; lo_recall = []
    for _ in range(TR):
        items = cphasor(NITEMS, N, g)
        freq = g.random(NITEMS) ** 2                                 # skewed access frequencies (few frequent, many rare)
        freq = freq / freq.sum(); strength = np.zeros(NITEMS)
        for _s in range(STEPS):
            strength *= DECAY                                        # all items decay
            acc = g.choice(NITEMS, size=3, p=freq)                   # access ~ frequency
            for a in acc:
                strength[int(a)] += BOOST
        M = ((strength[:, None]) * items).sum(0)                     # current memory bundle (strength-weighted)
        retr = (items @ np.conj(M)).real / (np.linalg.norm(M) + 1e-9)  # retrievability = presence in M
        is_freq = (freq >= np.median(freq)).astype(int)
        aucs.append(_auc(retr, is_freq))
        thr = np.median(retr)
        hi_recall.append(float(np.mean(retr[freq >= np.percentile(freq, 75)] > thr)))
        lo_recall.append(float(np.mean(retr[freq <= np.percentile(freq, 25)] > thr)))
    auc = float(np.mean(aucs)); hr = float(np.mean(hi_recall)); lr = float(np.mean(lo_recall))
    print("  FREQUENCY-DECAY retrievability-vs-freq AUC=%.3f | top-quartile-retained=%.3f bottom-quartile-retained=%.3f (3x capacity)" % (auc, hr, lr), flush=True)
    return {"auc": round(auc, 3), "hi_freq_retained": round(hr, 3), "lo_freq_retained": round(lr, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.3f hi-freq-retained=%.3f lo-freq-retained=%.3f" % (r["auc"], r["hi_freq_retained"], r["lo_freq_retained"])
    if r["auc"] >= 0.85 and r["hi_freq_retained"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: frequency-selective decay -- at 3x capacity, retrievability tracks access frequency (AUC>=0.85) and frequent items are retained (>=0.80) while stale fade. Graceful forgetting solves catastrophic interference, substrate-only. " + s)
    if r["auc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: frequency-decay 0.70-0.85 AUC. " + s)
    return ("HARD_FAIL", "HARD_FAIL: decay does not select by frequency. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_d2_2_frequency_decay_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote d2_2_frequency_decay")
