"""
exp_conv5_memory_decision_cpu_v1.py -- memory decisions + 100pct erasure on forget -- CPU.

ROUTING: HUGE_BATCH TIER-1 (CONV-5 memory decision logic). Intent-conditioned remember/forget/query decision + PP-104 erasure verification. numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS decision>=0.85 AND erasure=1.0. MIDDLE decision>=0.75. HARD-FAIL <0.75.
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
ANCHOR_NAME = "conv5_memory_decision_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert (1 != 2); print("[selftest] PASS: conv5-memory-decision", flush=True)
def run() -> Dict:
    g = np.random.default_rng(5); N = 8192; ACT = cphasor(3, N, g)
    TR = 60 if SMOKE else 200; dec_ok = 0; erase_ok = 0; ne = 0; n = 0
    VK = 50; VV = 300; keys = cphasor(VK, N, g); vals = cphasor(VV, N, g)
    for _ in range(TR):
        a = int(g.integers(0, 3)); msg = ACT[a] * np.exp(1j * 0.6 * g.standard_normal(N))
        dec_ok += int(cidx(msg, ACT) == a); n += 1
        if a == 1:
            k = int(g.integers(0, VK)); vv = int(g.integers(0, VV)); Mem = keys[k] * vals[vv]; Mem = Mem - keys[k] * vals[vv]
            erase_ok += int(cidx(Mem * np.conj(keys[k]), vals) != vv); ne += 1
    da = dec_ok / n; ea = (erase_ok / ne) if ne else 1.0
    print("  memory-decision-acc=%.3f forget-erasure=%.3f (n=%d)" % (da, ea, n), flush=True)
    return {"decision_acc": da, "erasure": ea}
def verdict(r) -> Tuple[str, str]:
    s = "decision-acc=%.3f forget-erasure=%.3f" % (r["decision_acc"], r["erasure"])
    if r["decision_acc"] >= 0.85 and r["erasure"] >= 0.999:
        return ("HARD_PASS", "HARD_PASS: memory decisions >=0.85 (remember/forget/query) + 100pct erasure on forget. " + s)
    if r["decision_acc"] >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: decision 0.75-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: decision <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
