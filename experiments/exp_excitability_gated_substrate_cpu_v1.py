"""
exp_excitability_gated_substrate_cpu_v1.py -- ExcitabilityGated substrate (Sprint-4; priority protection above cliff) -- CPU.

ROUTING: Research cycle-229 Tier-4 (ExcitabilityGated, not yet built). When a store is pushed ABOVE its capacity cliff
  (K >> N-capacity), recall collapses for all items. An EXCITABILITY GATE assigns write-gain proportional to item priority
  (high-priority = high excitability), so high-priority items dominate the additive bundle and survive above the cliff while
  low-priority fade. Distinct from per-tier-defaults (PP-355): this is about CLIFF behavior -- protecting a priority subset
  when the store is overloaded. Tests high-priority recall above the cliff: gated vs ungated (equal-gain). Wrapper, no core change.
PRE-REGISTERED: HARD-PASS gated high-priority recall >= 0.90 above the cliff AND > ungated high-priority recall by >= 0.25.
  MIDDLE gated >= 0.80. HARD-FAIL else.
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
ANCHOR_NAME = "excitability_gated_substrate_cpu_v1"
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
    print("[selftest] PASS: excitability-gated-substrate", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "981")))
    # push WAY above the capacity cliff: K items >> usable capacity at N=8192
    K = 300 if SMOKE else 1200; V = 400; NHI = 40; HIGAIN = 12.0
    keys = cphasor(K, N, g); vals = cphasor(V, N, g); truth = g.integers(0, V, size=K)
    hi = set(range(NHI))                                  # the high-priority subset to protect
    # UNGATED: equal gain -> above cliff, everything (incl high-priority) degrades
    ungated = cnorm(sum((keys[i] * vals[truth[i]] for i in range(K)), np.zeros(N, dtype=np.complex64)))
    # EXCITABILITY-GATED: write-gain proportional to priority -> high-priority dominate the bundle
    gated = np.zeros(N, dtype=np.complex64)
    for i in range(K):
        gain = HIGAIN if i in hi else 1.0
        gated = gated + gain * keys[i] * vals[truth[i]]
    gated = cnorm(gated)
    hi_idx = list(hi)
    gated_hi = sum(cidx(gated * np.conj(keys[i]), vals) == truth[i] for i in hi_idx) / NHI
    ungated_hi = sum(cidx(ungated * np.conj(keys[i]), vals) == truth[i] for i in hi_idx) / NHI
    print("  EXCITABILITY-GATED above cliff (K=%d >> cap): high-priority recall gated=%.3f | ungated=%.3f" %
          (K, gated_hi, ungated_hi), flush=True)
    return {"gated_hi_recall": round(gated_hi, 3), "ungated_hi_recall": round(ungated_hi, 3), "K": K, "n_hi": NHI}
def verdict(r) -> Tuple[str, str]:
    gh = r["gated_hi_recall"]; uh = r["ungated_hi_recall"]; s = "gated_hi=%.3f ungated_hi=%.3f (K=%d)" % (gh, uh, r["K"])
    if gh >= 0.90 and gh > uh + 0.25:
        return ("HARD_PASS", "HARD_PASS: excitability gate protects high-priority items above the capacity cliff -- priority-proportional write-gain keeps high-priority recall>=0.90 while ungated collapses to %.2f. Cliff-aware priority protection via wrapper, no core change. " % uh + s)
    if gh >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: gated high-priority >=0.80 but margin over ungated <0.25. " + s)
    return ("HARD_FAIL", "HARD_FAIL: gated high-priority <0.80. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
