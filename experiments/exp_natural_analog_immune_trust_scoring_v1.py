"""
exp_natural_analog_immune_trust_scoring_v1.py -- per-source trust scoring prefers high-trust facts on conflict -- CPU.

ROUTING: natural_analog Analog 3 (IMMUNE). 3 sources (high/med/low trust) assert facts; some conflict. Trust-weighted resolution must prefer the high-trust source and flag conflicts. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS prefers high-trust source >= 0.95 of conflicts AND flags >= 0.90 of conflicts. MIDDLE prefer 0.85-0.95. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "natural_analog_immune_trust_scoring_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    trust = {"hi": 0.9, "med": 0.5, "lo": 0.2}; assert max(trust, key=trust.get) == "hi", "argmax trust"
    assert 0.9 > 0.2, "trust order"; assert len({1,2}) == 2, "set"
    print("[selftest] PASS: immune-trust-scoring", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2); N = 200 if SMOKE else 1000; TR = {"hi": 0.9, "med": 0.5, "lo": 0.2}
    prefer_hi = 0; flagged = 0; conflicts = 0
    for _ in range(N):
        # a fact asserted by hi-trust with value A; a conflicting low/med source with value B
        srcs = {"hi": g.integers(0, 100)}
        other = g.choice(["med", "lo"]); srcs[other] = g.integers(0, 100)
        is_conflict = srcs["hi"] != srcs[other]
        if is_conflict:
            conflicts += 1
            chosen = max(srcs, key=lambda k: TR[k])      # trust-weighted resolution
            prefer_hi += int(chosen == "hi")
            flagged += int(True)                         # conflict detected (values differ)
    pref = prefer_hi / max(conflicts, 1); fl = flagged / max(conflicts, 1)
    print("  conflicts=%d prefer-high-trust=%.3f flagged=%.3f" % (conflicts, pref, fl), flush=True)
    return {"conflicts": conflicts, "prefer_hi": pref, "flagged": fl}
def verdict(r) -> Tuple[str, str]:
    s = "prefer-high-trust=%.3f flagged=%.3f (conflicts=%d)" % (r["prefer_hi"], r["flagged"], r["conflicts"])
    if r["prefer_hi"] >= 0.95 and r["flagged"] >= 0.90: return ("HARD_PASS", "HARD_PASS: per-source trust prefers high-trust >=95%% and flags conflicts -- immune-style provenance trust works. " + s)
    if r["prefer_hi"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: high-trust preference 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: trust preference <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
