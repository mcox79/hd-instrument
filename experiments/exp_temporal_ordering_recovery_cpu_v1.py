"""
exp_temporal_ordering_recovery_cpu_v1.py -- recover the temporal order of events stored with ordinal-position binding -- CPU.

ROUTING: refill batch (event sequence ordering). A sequence of events each bound to an ordinal-position vector; the stored order is recovered by querying each position and reading out the event. Measures adjacent-pair order accuracy (is event[i] correctly before event[i+1]). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS adjacent-pair order accuracy >= 0.90 over sequences. MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "temporal_ordering_recovery_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; p = cphasor(1, 32, g)[0]; assert np.allclose(a * p * np.conj(p), a, atol=1e-3), "pos bind"; print("[selftest] PASS: temporal-ordering-recovery", flush=True)
def run() -> Dict:
    g = np.random.default_rng(327); N = 4096; VE = 200; L = 8; TR = 60 if SMOKE else 200; ents = cphasor(VE, N, g); pos = cphasor(L, N, g)
    correct = 0; tot = 0
    for _ in range(TR):
        seq = g.choice(VE, L, replace=False); M = np.zeros(N, dtype=np.complex64)
        for i in range(L):
            M = M + pos[i] * ents[int(seq[i])]
        readout = [cidx(M * np.conj(pos[i]), ents) for i in range(L)]
        for i in range(L - 1):
            correct += int(readout[i] == int(seq[i]) and readout[i + 1] == int(seq[i + 1])); tot += 1
    acc = correct / tot; print("  adjacent-pair order accuracy=%.3f (L=%d)" % (acc, L), flush=True)
    return {"acc": acc}
def verdict(r) -> Tuple[str, str]:
    s = "order-accuracy=%.3f" % r["acc"]
    if r["acc"] >= 0.90: return ("HARD_PASS", "HARD_PASS: temporal sequence order recovered >=0.90 adjacent-pair -- event ordering supported. " + s)
    if r["acc"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: order 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: order <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
