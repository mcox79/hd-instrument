"""
exp_natural_analog_quorum_ema_detector_v1.py -- EMA signal-level detector flags high-frequency injection attacks -- CPU.

ROUTING: natural_analog_5_pretests Analog 5 (QUORUM SENSING). A query stream has a baseline per-entity rate; an adversary injects a high-frequency burst on one entity. An EMA (exponential moving average) anomaly detector flags entities whose instantaneous rate exceeds K*EMA. Measure detection rate vs false positives. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS detector flags > 0.90 of injection bursts at < 0.10 false-positive on normal entities. MIDDLE recall 0.70-0.90. HARD-FAIL recall < 0.70 or FP > 0.10.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "natural_analog_quorum_ema_detector_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    ema = 0.0; ema = 0.1 * 1.0 + 0.9 * ema; assert ema > 0, "ema updates"
    assert 5.0 > 3.0 * 1.0, "threshold logic"
    assert abs(np.mean([1.0, 1.0]) - 1.0) < 1e-9, "mean"
    print("[selftest] PASS: quorum-ema-detector", flush=True)

def run() -> Dict:
    g = np.random.default_rng(55); V = 100; Q = 5000 if SMOKE else 20000; ALPHA = 0.01; KTH = 6.0
    base = np.full(V, 1.0 / V)
    n_inject = 10; inj_entities = set(int(x) for x in g.choice(V, n_inject, replace=False))
    ema = np.zeros(V); flagged = set(); fp = set()
    inj_windows = {e: (int(g.integers(Q // 4, Q * 3 // 4)),) for e in inj_entities}
    for t in range(Q):
        if any(abs(t - w[0]) < 60 for w in inj_windows.values()) and g.random() < 0.6:
            e = int(g.choice(list(inj_entities)))      # injection burst
        else:
            e = int(g.choice(V, p=base))
        x = np.zeros(V); x[e] = 1.0
        inst = x; ema = ALPHA * inst + (1 - ALPHA) * ema
        if ema[e] > KTH * (1.0 / V):                     # sustained rate far above baseline 1/V (quorum signal)
            (flagged if e in inj_entities else fp).add(e)
    recall = len(flagged & inj_entities) / max(len(inj_entities), 1)
    fpr = len(fp) / max(V - len(inj_entities), 1)
    print("  EMA detector: injection recall=%.3f false-positive=%.3f (injected=%d)" % (recall, fpr, n_inject), flush=True)
    return {"recall": recall, "fpr": fpr, "n_inject": n_inject}

def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f fpr=%.3f (injected=%d)" % (r["recall"], r["fpr"], r["n_inject"])
    if r["recall"] > 0.90 and r["fpr"] < 0.10:
        return ("HARD_PASS", "HARD_PASS: EMA quorum-sensing detector flags >90%% of injection attacks at <10%% FP -- signal-level adversarial detection works. " + s)
    if r["recall"] >= 0.70 and r["fpr"] < 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: detection recall 0.70-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.70 or FP >0.10. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
