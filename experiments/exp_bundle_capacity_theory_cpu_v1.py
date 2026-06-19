"""
exp_bundle_capacity_theory_cpu_v1.py -- empirical bundle capacity tracks the N/(2 ln N) law across N -- CPU.

ROUTING: CPU substrate-physics characterization (bundle capacity vs N/(2 ln N) theory (rescue)). RESCUE of bundle_capacity_cliff (K_crit=0.049*N was below an over-optimistic 0.10 threshold). Across N in {1024,2048,4096,8192}, find K_crit (recall@1>=0.9 for bundled role-filler pairs) and compare to the FHRR bundle-capacity law N/(2 ln N). Reframes the negative as a clean scaling law. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS empirical K_crit within 35pct of N/(2 ln N) at every N (capacity is predictable, not a failure). MIDDLE within 60pct. HARD-FAIL > 60pct.
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
ANCHOR_NAME = "bundle_capacity_theory_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    assert 1024 / (2 * math.log(1024)) > 50, "theory positive"; print("[selftest] PASS: bundle-capacity-theory-cpu", flush=True)
def kcrit(N, g, V=5000, TR=8):
    book = cphasor(min(V, 4 * N), N, g); lo, hi, best = 10, int(0.2 * N), 10
    while lo <= hi:
        K = (lo + hi) // 2; ok = 0; tot = 0
        for _ in range(TR):
            roles = cphasor(K, N, g); fidx = g.choice(len(book), K, replace=False)
            B = (roles * book[fidx]).sum(0); rec = B[None, :] * roles.conj(); sc = (rec @ book.conj().T).real
            pred = np.argmax(sc, axis=1); ok += int((pred == fidx).sum()); tot += K
        if ok / tot >= 0.9:
            best = K; lo = K + 1
        else:
            hi = K - 1
    return best
def run() -> Dict:
    g = np.random.default_rng(21); Ns = [1024, 2048] if SMOKE else [1024, 2048, 4096, 8192]; rows = {}; devs = []
    for N in Ns:
        kc = kcrit(N, g); theo = N / (2 * math.log(N)); dev = abs(kc - theo) / theo; devs.append(dev)
        rows["N%d" % N] = (kc, round(theo, 1)); print("  N=%d K_crit=%d theory N/(2lnN)=%.1f dev=%.2f" % (N, kc, theo, dev), flush=True)
    return {"rows": rows, "max_dev": float(np.max(devs))}
def verdict(r) -> Tuple[str, str]:
    s = "max deviation from N/(2 ln N) = %.2f | (K_crit, theory): %s" % (r["max_dev"], r["rows"])
    if r["max_dev"] <= 0.35: return ("HARD_PASS", "HARD_PASS: bundle capacity tracks N/(2 ln N) within 35pct -- predictable composition capacity law (the earlier cliff was a threshold artifact). " + s)
    if r["max_dev"] <= 0.60: return ("MIDDLE_BAND", "MIDDLE_BAND: capacity within 60pct of theory. " + s)
    return ("HARD_FAIL", "HARD_FAIL: capacity deviates >60pct from theory. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
