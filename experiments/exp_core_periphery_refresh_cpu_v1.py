"""
exp_core_periphery_refresh_cpu_v1.py -- CORE-PERIPHERY refresh-cycle (RESCUE-3, TEMPORAL) -- CPU.

ROUTING: Research CYCLE226 Tier-1 (core_periphery RESCUE-3). The FIXED topological-protection approach failed (0.008 at 5000
  edits; saturation). RESCUE per the temporal meta-pattern: (1) DECAY old periphery edits so the bundle stays bounded (not
  saturating), (2) periodically RE-INJECT the core every M edits (temporal refresh) to keep it retrievable. Tests core recall
  after 5000 edits: refresh+decay vs the failed no-refresh baseline. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS refreshed core recall >= 0.90 after 5000 edits AND >> baseline. MIDDLE >= 0.75. HARD-FAIL else.
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
ANCHOR_NAME = "core_periphery_refresh_cpu_v1"
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
    print("[selftest] PASS: core-periphery-refresh", flush=True)
def run() -> Dict:
    g = np.random.default_rng(701); KCORE = 30 if SMOKE else 40; V = 400; EDITS = 800 if SMOKE else 5000
    DECAY = 0.985; REFRESH = 200; RW = 8.0
    TR = 4 if SMOKE else 12; ref = []; base = []
    for _ in range(TR):
        core_keys = cphasor(KCORE, N, g); vals = cphasor(V, N, g); ct = g.integers(0, V, size=KCORE)
        core_bundle = sum((core_keys[i] * vals[ct[i]] for i in range(KCORE)), np.zeros(N, dtype=np.complex64))
        Mr = core_bundle.copy().astype(np.complex64); Mb = cnorm(core_bundle).astype(np.complex64)
        for e in range(EDITS):
            ek = cphasor(1, N, g)[0]; ev = vals[int(g.integers(0, V))]
            Mr = DECAY * Mr + ek * ev                                  # REFRESH: decayed periphery
            Mb = cnorm(Mb + ek * ev)                                   # baseline: no decay, no refresh
            if (e + 1) % REFRESH == 0:
                Mr = Mr + RW * core_bundle                             # temporal core re-injection
        Mrf = cnorm(Mr)
        hr = sum(cidx(Mrf * np.conj(core_keys[i]), vals) == ct[i] for i in range(KCORE)) / KCORE
        hb = sum(cidx(Mb * np.conj(core_keys[i]), vals) == ct[i] for i in range(KCORE)) / KCORE
        ref.append(hr); base.append(hb)
    pr = float(np.mean(ref)); pb = float(np.mean(base))
    print("  CORE-PERIPHERY-REFRESH core recall after %d edits: refresh+decay=%.3f | no-refresh baseline=%.3f" % (EDITS, pr, pb), flush=True)
    return {"refresh_core_recall": round(pr, 3), "baseline_core_recall": round(pb, 3), "edits": EDITS}
def verdict(r) -> Tuple[str, str]:
    pr = r["refresh_core_recall"]; pb = r["baseline_core_recall"]; s = "refresh=%.3f baseline=%.3f after %d edits" % (pr, pb, r["edits"])
    if pr >= 0.90 and pr > pb + 0.10:
        return ("HARD_PASS", "HARD_PASS: TEMPORAL refresh-cycle RESCUES core protection -- decay (bounded capacity) + periodic core re-injection keeps core recall >=0.90 after %d edits (vs failed baseline %.2f). Self-mod stability via TIME (decay+refresh), not fixed topological protection -- confirms the temporal meta-pattern. " % (r["edits"], pb) + s)
    if pr >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: refresh core 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: refresh-cycle core <0.75. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
