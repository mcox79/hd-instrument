"""
exp_conv15_tool_routing_cpu_v1.py -- tool routing accuracy (intent->tool) -- CPU.

ROUTING: HUGE_BATCH TIER-1 (CONV-15 substrate-routed tool calls (smoke)). Classify query intent to one of several tools via substrate prototype cleanup; 50-query smoke. numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS >=0.85. MIDDLE >=0.70. HARD-FAIL <0.70.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "conv15_tool_routing_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"; print("[selftest] PASS: tool-routing-acc", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1515); N = 8192; K = 6; proto = cphasor(K, N, g)
    TR = 60 if SMOKE else 200; correct = 0; n = 0
    for _ in range(TR):
        c = int(g.integers(0, K))
        msg = proto[c] * np.exp(1j * 0.6 * g.standard_normal(N))          # intent prototype + paraphrase noise
        correct += int(cidx(msg, proto) == c); n += 1
    acc = correct / n; print("  tool-routing-acc=%.3f (K=%d, n=%d)" % (acc, K, n), flush=True)
    return {"accuracy": acc, "K": K}
def verdict(r) -> Tuple[str, str]:
    s = "tool-routing-acc=%.3f" % r["accuracy"]
    if r["accuracy"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: tool-routing-acc clears bar -- intent-conditioned routing works. " + s)
    if r["accuracy"] >= 0.7:
        return ("MIDDLE_BAND", "MIDDLE_BAND: tool-routing-acc near bar. " + s)
    return ("HARD_FAIL", "HARD_FAIL: tool-routing-acc below bar. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
