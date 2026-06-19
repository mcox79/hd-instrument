"""
exp_comp_a3_temporal_asof_cpu_v1.py -- order of events AS-OF time T: temporal sequence restricted to a valid-time -- CPU.

ROUTING: POST-CYCLE192 Group A composition (A3 temporal+bitemporal composition (PP-164 + PP-154)). Events carry an ordinal position and a valid-time; an AS-OF(T) query recovers the ordered sequence of events valid at time T. Validates temporal ordering composes with bitemporal as-of. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS AS-OF temporal ordering recall = 1.000 (all valid events recovered in order). MIDDLE >= 0.90. HARD-FAIL < 0.90.
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
ANCHOR_NAME = "comp_a3_temporal_asof_cpu_v1"
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
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; p = cphasor(1, 32, g)[0]; t = cphasor(1, 32, g)[0]
    assert np.allclose(a * p * t * np.conj(p * t), a, atol=1e-3), "pos-time bind"; print("[selftest] PASS: comp-a3-temporal-asof", flush=True)
def run() -> Dict:
    g = np.random.default_rng(403); N = 8192; VE = 200; L = 6; NT = 5; TR = 60 if SMOKE else 200
    ents = cphasor(VE, N, g); pos = cphasor(L, N, g); times = cphasor(NT, N, g)
    hit = 0; tot = 0
    for _ in range(TR):
        # at each time period a prefix of the sequence is valid (events accrue over time)
        seq = g.choice(VE, L, replace=False); M = np.zeros(N, dtype=np.complex64)
        valid_upto = {}
        for i in range(L):
            t_app = int(g.integers(0, NT)); valid_upto[i] = t_app
            for t in range(t_app, NT):
                M = M + times[t] * pos[i] * ents[int(seq[i])]
        T = int(g.integers(0, NT)); valid_idx = [i for i in range(L) if valid_upto[i] <= T]
        for i in valid_idx:
            pred = cidx(M * np.conj(times[T] * pos[i]), ents); hit += int(pred == int(seq[i])); tot += 1
    rec = hit / max(1, tot); print("  AS-OF temporal ordering recall=%.3f" % rec, flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "AS-OF ordering recall=%.3f" % r["recall"]
    if r["recall"] >= 0.999: return ("HARD_PASS", "HARD_PASS: AS-OF temporal ordering recall=1.0 -- temporal sequence + bitemporal as-of compose. " + s)
    if r["recall"] >= 0.90: return ("MIDDLE_BAND", "MIDDLE_BAND: AS-OF ordering 0.90-1.0. " + s)
    return ("HARD_FAIL", "HARD_FAIL: AS-OF ordering <0.90. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
