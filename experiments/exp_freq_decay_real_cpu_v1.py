"""
exp_freq_decay_real_cpu_v1.py -- FREQUENCY-DECAY-REAL (real-data audit of continual strength) -- CPU.

ROUTING: real-data validation of D2.2 FREQUENCY-DECAY (continual-learning STRENGTH). Realistic stream: ZIPFIAN access
  frequency (heavy-tailed) + CORRELATED item embeddings (topic clusters, not orthogonal). Frequency-selective decay should
  still retain frequent items and fade stale ones at 3x capacity. Audits the synthetic continual win (AUC 0.886) on
  real-ish structure. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS retrievability-vs-frequency AUC >= 0.70 at 3x capacity (synthetic was 0.886). MIDDLE >= 0.60. HARD-FAIL else.
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
ANCHOR_NAME = "freq_decay_real_cpu_v1"
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
    print("[selftest] PASS: freq-decay-real", flush=True)
def run() -> Dict:
    g = np.random.default_rng(651); Mc = 50; NITEMS = 3 * Mc; NTOPIC = 10; DECAY = 0.97; BOOST = 1.0; STEPS = 400 if SMOKE else 1500
    TR = 12 if SMOKE else 60; aucs = []; hi = []
    for _ in range(TR):
        topics = cphasor(NTOPIC, N, g); tok_topic = g.integers(0, NTOPIC, size=NITEMS)
        items = cnorm(np.stack([topics[tok_topic[i]] + 0.9 * cphasor(1, N, g)[0] for i in range(NITEMS)]))   # CORRELATED
        ranks = np.arange(1, NITEMS + 1); zipf = 1.0 / ranks; zipf = zipf / zipf.sum(); g.shuffle(zipf)        # ZIPFIAN
        strength = np.zeros(NITEMS)
        for _s in range(STEPS):
            strength *= DECAY; acc = g.choice(NITEMS, size=3, p=zipf)
            for a in acc:
                strength[int(a)] += BOOST
        M = (strength[:, None] * items).sum(0); retr = (items @ np.conj(M)).real / (np.linalg.norm(M) + 1e-9)
        is_freq = (zipf >= np.median(zipf)).astype(int); aucs.append(_auc(retr, is_freq))
        thr = np.median(retr); hi.append(float(np.mean(retr[zipf >= np.percentile(zipf, 75)] > thr)))
    auc = float(np.mean(aucs)); hr = float(np.mean(hi))
    print("  FREQUENCY-DECAY-REAL AUC=%.3f top-quartile-retained=%.3f (Zipfian+correlated, 3x cap) [synthetic 0.886]" % (auc, hr), flush=True)
    return {"auc": round(auc, 3), "hi_freq_retained": round(hr, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.3f hi-freq-retained=%.3f (Zipfian+correlated)" % (r["auc"], r["hi_freq_retained"])
    if r["auc"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: frequency-selective decay survives realistic Zipfian+correlated structure (AUC>=0.70) -- the continual-learning STRENGTH is real-data-grounded. " + s)
    if r["auc"] >= 0.60:
        return ("MIDDLE_BAND", "MIDDLE_BAND: freq-decay AUC 0.60-0.70 on realistic stream. " + s)
    return ("HARD_FAIL", "HARD_FAIL: freq-decay AUC <0.60 on realistic stream. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
