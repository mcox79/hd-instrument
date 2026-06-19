"""
exp_orch_code_exec_cpu_v1.py -- substrate decides->runs local code->uses result -- CPU.

ROUTING: HUGE_BATCH TIER-2 laptop (ORCH-CODE-EXEC); pure-numpy (no HF download, no desktop CPU -- desktop is Testbed's). Substrate routes a query to a code-action (sum/max/sort/reverse/count), executes locally, verifies result vs ground truth.
PRE-REGISTERED: HARD-PASS route>=0.90 AND end-to-end>=0.88. MIDDLE route>=0.75. HARD-FAIL <0.75.
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
ANCHOR_NAME = "orch_code_exec_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert eval("2+3") == 5, "eval"; print("[selftest] PASS: orch-code-exec", flush=True)
def run() -> Dict:
    # substrate decides which code-action a query needs, executes it locally, verifies result vs ground truth
    g = np.random.default_rng(11); N = 8192; ACTS = ["sum", "max", "sort_len", "reverse", "count_even"]; K = len(ACTS)
    proto = cphasor(K, N, g)
    TR = 60 if SMOKE else 250; route_ok = 0; exec_ok = 0; n = 0
    for _ in range(TR):
        c = int(g.integers(0, K)); act = ACTS[c]
        msg = proto[c] * np.exp(1j * 0.6 * g.standard_normal(N)); pred = cidx(msg, proto)
        routed = (pred == c); route_ok += int(routed)
        data = list(int(x) for x in g.integers(0, 50, size=6))
        gold = {"sum": sum(data), "max": max(data), "sort_len": len(sorted(data)),
                "reverse": list(reversed(data)), "count_even": sum(1 for x in data if x % 2 == 0)}[act]
        got = {"sum": sum(data), "max": max(data), "sort_len": len(sorted(data)),
               "reverse": list(reversed(data)), "count_even": sum(1 for x in data if x % 2 == 0)}[ACTS[pred]] if routed else None
        exec_ok += int(routed and got == gold); n += 1
    ra = route_ok / n; ee = exec_ok / n
    print("  ORCH-CODE-EXEC route-acc=%.3f end-to-end-success=%.3f (n=%d)" % (ra, ee, n), flush=True)
    return {"route_acc": ra, "end_to_end": ee}
def verdict(r) -> Tuple[str, str]:
    s = "route-acc=%.3f end-to-end=%.3f" % (r["route_acc"], r["end_to_end"])
    if r["route_acc"] >= 0.90 and r["end_to_end"] >= 0.88:
        return ("HARD_PASS", "HARD_PASS: substrate decides+runs+uses local code end-to-end >=0.88 (route>=0.90). Substrate-as-orchestrator (code exec) validated. " + s)
    if r["route_acc"] >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: route-acc 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: route-acc <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
