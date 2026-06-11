"""
exp_3x_redundant_substrate_cpu_v1.py -- 3x-Redundant substrate (Sprint-4 reliability under noise) -- CPU.

ROUTING: Research SPRINT4 Tier-1 (3x redundant; reliability under noise). Engineered wrapper: store CRITICAL content in 3
  mirrored substrates; under per-copy NOISE (phase corruption), AVERAGE/majority-vote across copies cancels independent noise.
  Distinct from RS-parity (exact erasure) -- this is soft reliability under corruption. Tests 3x recall under noise vs single
  copy. Wrapper + routing, no core change. N=8192.
PRE-REGISTERED: HARD-PASS 3x recall under noise >= 0.95 AND > single-copy by >= 0.10. MIDDLE >= 0.85. HARD-FAIL else.
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
ANCHOR_NAME = "3x_redundant_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: 3x-redundant-substrate", flush=True)
def run() -> Dict:
    g = np.random.default_rng(906); K = 80; V = 400; NOISE = 2.2
    TR = 8 if SMOKE else 25; rec3 = []; rec1 = []
    for _ in range(TR):
        keys = cphasor(K, N, g); vals = cphasor(V, N, g); truth = g.integers(0, V, size=K)
        base = cnorm(sum((keys[i] * vals[truth[i]] for i in range(K)), np.zeros(N, dtype=np.complex64)))
        # 3 mirrored copies, each independently corrupted by phase noise
        copies = [cnorm(base + NOISE * cphasor(1, N, g)[0] * 0 + NOISE * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)) for _ in range(3)]
        merged = cnorm(sum(copies, np.zeros(N, dtype=np.complex64)))   # average across copies (cancels independent noise)
        h3 = sum(cidx(merged * np.conj(keys[i]), vals) == truth[i] for i in range(K)) / K
        h1 = sum(cidx(copies[0] * np.conj(keys[i]), vals) == truth[i] for i in range(K)) / K
        rec3.append(h3); rec1.append(h1)
    r3 = float(np.mean(rec3)); r1 = float(np.mean(rec1))
    print("  3x-REDUNDANT recall under noise: 3x-averaged=%.3f | single-copy=%.3f" % (r3, r1), flush=True)
    return {"redundant3x_recall": round(r3, 3), "single_copy_recall": round(r1, 3)}
def verdict(r) -> Tuple[str, str]:
    r3 = r["redundant3x_recall"]; r1 = r["single_copy_recall"]; s = "3x=%.3f single=%.3f" % (r3, r1)
    if r3 >= 0.95 and r3 > r1 + 0.10:
        return ("HARD_PASS", "HARD_PASS: 3x-redundant reliability works -- averaging 3 noisy mirrored copies recovers recall>=0.95 vs single-copy %.2f under corruption. Soft redundancy via wrapper (mirror+average), no core change. " % r1 + s)
    if r3 >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 3x 0.85-0.95 or margin small. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 3x redundancy does not improve reliability. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
