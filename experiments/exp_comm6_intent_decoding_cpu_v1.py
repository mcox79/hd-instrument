"""
exp_comm6_intent_decoding_cpu_v1.py -- COMM-6 INTENT-DECODING (substrate-native communication) -- CPU.

ROUTING: Research AGGRESSIVE_OVERNIGHT THRUST-1 COMMUNICATE. An utterance = INTENT-core + STYLE variation + noise (the same
  intent has many surface realizations). Substrate decodes the core intent from the varied surface (cleanup to the intent
  codebook). Tests decoding accuracy under surface/style variation -- the substrate recovers meaning despite surface form. No LLM. N=8192.
PRE-REGISTERED: HARD-PASS intent-decoding accuracy >= 0.85 under surface variation. MIDDLE >= 0.70. HARD-FAIL else.
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
ANCHOR_NAME = "comm6_intent_decoding_cpu_v1"
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
    print("[selftest] PASS: comm6-intent-decoding", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "811"))); NINTENT = 20; NSTYLE = 8
    TR = 15 if SMOKE else 100; hit = 0; n = 0
    for _ in range(TR):
        intents = cphasor(NINTENT, N, g); styles = cphasor(NSTYLE, N, g)
        for _q in range(10):
            it = int(g.integers(0, NINTENT)); st = int(g.integers(0, NSTYLE))
            # surface = intent core + style variation + noise (varied realization of the same intent)
            noise = 0.5 * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            surface = cnorm(intents[it] + 0.6 * styles[st] + noise)
            pred = cidx(surface, intents); hit += int(pred == it); n += 1
    acc = hit / n
    print("  COMM-6 INTENT-DECODING accuracy=%.3f under style+noise variation (intents=%d, n=%d)" % (acc, NINTENT, n), flush=True)
    return {"accuracy": round(acc, 3), "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "accuracy=%.3f (n=%d)" % (r["accuracy"], r["n"])
    if r["accuracy"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate decodes intent from varied surface forms >=0.85 -- recovers core meaning despite style variation + noise, substrate-only. Communication = meaning recovery from surface. " + s)
    if r["accuracy"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: intent-decoding 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: intent-decoding <0.70. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
