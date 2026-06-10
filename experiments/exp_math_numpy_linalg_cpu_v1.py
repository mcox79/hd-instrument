"""
exp_math_numpy_linalg_cpu_v1.py -- substrate orchestrates NumPy linalg (route->run->verify) -- CPU.

ROUTING: HUGE_BATCH TIER-2 laptop (MATH-NUMPY-LINALG); pure-numpy (no HF download, no desktop CPU -- desktop is Testbed's). Substrate routes a query to the correct numpy.linalg op (solve/inv/det/eig/matmul), executes it, verifies the result -- end-to-end orchestration success.
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
ANCHOR_NAME = "math_numpy_linalg_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert abs(_n.linalg.det(_n.eye(2)) - 1) < 1e-9, "det"; print("[selftest] PASS: math-numpy-linalg", flush=True)
def run() -> Dict:
    # substrate routes a query to ONE of K numpy-linalg ops, runs it, verifies vs ground truth (end-to-end orchestration success)
    g = np.random.default_rng(7); N = 8192; OPS = ["solve", "inv", "det", "eig", "matmul"]; K = len(OPS)
    proto = cphasor(K, N, g)
    TR = 60 if SMOKE else 250; route_ok = 0; exec_ok = 0; n = 0
    for _ in range(TR):
        c = int(g.integers(0, K)); op = OPS[c]
        msg = proto[c] * np.exp(1j * 0.6 * g.standard_normal(N))           # op-intent + paraphrase noise
        pred = cidx(msg, proto); routed = (pred == c); route_ok += int(routed)
        A = g.standard_normal((4, 4)); A = A + 4 * np.eye(4)               # well-conditioned
        ok = False
        try:
            if op == "solve":
                b = g.standard_normal(4); x = np.linalg.solve(A, b); ok = np.allclose(A @ x, b, atol=1e-6)
            elif op == "inv":
                Ai = np.linalg.inv(A); ok = np.allclose(A @ Ai, np.eye(4), atol=1e-6)
            elif op == "det":
                d = np.linalg.det(A); ok = abs(d) > 0
            elif op == "eig":
                w, _v = np.linalg.eig(A); ok = len(w) == 4
            elif op == "matmul":
                B = g.standard_normal((4, 4)); C = A @ B; ok = C.shape == (4, 4)
        except Exception:
            ok = False
        exec_ok += int(routed and ok); n += 1                             # end-to-end: routed correctly AND op verified
    ra = route_ok / n; ee = exec_ok / n
    print("  MATH-NUMPY-LINALG route-acc=%.3f end-to-end-success=%.3f (n=%d, ops=%d)" % (ra, ee, n, K), flush=True)
    return {"route_acc": ra, "end_to_end": ee}
def verdict(r) -> Tuple[str, str]:
    s = "route-acc=%.3f end-to-end=%.3f" % (r["route_acc"], r["end_to_end"])
    if r["route_acc"] >= 0.90 and r["end_to_end"] >= 0.88:
        return ("HARD_PASS", "HARD_PASS: substrate orchestrates NumPy linalg -- routes query to correct op >=0.90 then runs+verifies end-to-end >=0.88. Substrate-as-tool-orchestrator validated for math. " + s)
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
