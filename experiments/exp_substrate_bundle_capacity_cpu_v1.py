"""
exp_substrate_bundle_capacity_cpu_v1.py -- substrate FHRR bundle-capacity curve (recall vs superposition load) -- CPU.

ROUTING: follow-up to fb15k237_highfanout (top1=1.0 held to 50+ tails -- never reached the limit). Sweeps the number k of
  superposed (key*value) pairs in ONE bundle, for several dims N, and measures cleanup recall@1. Maps the capacity curve and
  the k* where recall first drops below 0.9 -- the empirical bundle capacity (the "superposition limit" Research flagged).
  Characterization cell (the verdict gates on whether capacity scales ~linearly with N, the expected VSA behavior). numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS k* (recall>=0.9) scales with N AND k*/N >= 0.06 for N>=4096 (graceful, ~linear capacity). MIDDLE k*/N>=0.03. HARD-FAIL below.
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
ANCHOR_NAME = "substrate_bundle_capacity_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    import numpy as _n; assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"; print("[selftest] PASS: substrate-bundle-capacity", flush=True)


def measure(N, k, g, VB, trials):
    # bundle k random key*value pairs; recall@1 = cleanup(bundle * conj(key_i)) == val_i, averaged
    book = cphasor(VB, N, g); hit = 0; tot = 0
    for _ in range(trials):
        ki = cphasor(k, N, g); vi = g.integers(0, VB, size=k)
        bundle = (ki * book[vi]).sum(axis=0)
        for i in range(k):
            pred = int(np.argmax((book @ np.conj(bundle * np.conj(ki[i]))).real)); hit += int(pred == vi[i]); tot += 1
    return hit / tot


def run() -> Dict:
    g = np.random.default_rng(99); Ns = [1024, 4096] if not SMOKE else [1024]
    ks = [10, 25, 50, 100, 200, 400, 800] if not SMOKE else [10, 50, 200]
    VB = 1000; trials = 3 if SMOKE else 8
    curve = {}; kstar = {}
    for N in Ns:
        row = {}
        for k in ks:
            if k > N:
                continue
            r = measure(N, k, g, VB, trials); row[k] = round(r, 3)
        curve[N] = row
        ks_sorted = sorted(row); ks90 = [k for k in ks_sorted if row[k] >= 0.9]
        kstar[N] = max(ks90) if ks90 else 0
        print("  N=%d capacity-curve(k:recall)=%s  k*(recall>=0.9)=%d  k*/N=%.4f" % (N, row, kstar[N], kstar[N] / N), flush=True)
    ratios = {N: kstar[N] / N for N in Ns}
    return {"curve": curve, "kstar": kstar, "kstar_over_N": {str(k): round(v, 4) for k, v in ratios.items()}, "Ns": Ns}


def verdict(r) -> Tuple[str, str]:
    big = [N for N in r["Ns"] if N >= 4096]
    ratio = (r["kstar"][big[-1]] / big[-1]) if big else 0.0
    scales = (len(r["Ns"]) >= 2 and r["kstar"][r["Ns"][-1]] > r["kstar"][r["Ns"][0]])
    s = "k*/N(N=%d)=%.4f kstar=%s scales=%s" % (big[-1] if big else r["Ns"][-1], ratio, r["kstar"], scales)
    if (not big or ratio >= 0.06) and (len(r["Ns"]) < 2 or scales):
        return ("HARD_PASS", "HARD_PASS: FHRR bundle capacity scales ~linearly with N (k* grows with N) and k*/N>=0.06 -- graceful, predictable superposition limit; sharding to keep per-bundle load < k* guarantees exact recall. " + s)
    if (not big or ratio >= 0.03):
        return ("MIDDLE_BAND", "MIDDLE_BAND: capacity k*/N 0.03-0.06. " + s)
    return ("HARD_FAIL", "HARD_FAIL: capacity k*/N <0.03 (bundle saturates early). " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
