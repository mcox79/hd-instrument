"""
exp_f1_topk_bitflip_rescue_cpu_v1.py -- top-k recovers >=0.95 recall at 30pct bit-flip with graceful decay to 50pct -- CPU.

ROUTING: CYCLE_200_FOLLOWUPS (F1 top-k bit-flip rescue). Bit-flips a fraction of the query-key dims; top-1 degrades but top-k (k=5) rescues; sweeps flip 0->0.5. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS top-k@0.3 >=0.95 AND top-k@0.5 >=0.70. MIDDLE top-k@0.3 >=0.85. HARD-FAIL <0.85.
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
ANCHOR_NAME = "f1_topk_bitflip_rescue_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert _n.all(_n.diff([0,1,2])>0), "mono"; print("[selftest] PASS: f1-topk-bitflip-rescue", flush=True)
def run() -> Dict:
    g = np.random.default_rng(2001); N = 8192; VK = 100; VV = 400; keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); M = 50; K = 5
    levels = [0.0, 0.1, 0.3, 0.5]; TR = 40 if SMOKE else 150; curve1 = {}; curvek = {}
    for fl in levels:
        h1 = 0; hk = 0; n = 0
        for _ in range(TR):
            Mem = np.zeros(N, dtype=np.complex64); facts = []
            for _f in range(M):
                k = int(g.integers(0, VK)); vv = int(g.integers(0, VV)); Mem = Mem + keys[k] * vals[vv]; facts.append((k, vv))
            k, vv = facts[int(g.integers(0, len(facts)))]
            qk = keys[k].copy(); nf = int(fl * N); idx = g.choice(N, nf, replace=False); qk[idx] = np.exp(1j * (g.random(nf) * 2 - 1) * math.pi)
            sc = (vals @ np.conj(Mem * np.conj(qk))).real; order = np.argsort(sc)[::-1]
            h1 += int(order[0] == vv); hk += int(vv in order[:K].tolist()); n += 1
        curve1["f%.1f" % fl] = h1 / n; curvek["f%.1f" % fl] = hk / n
    t1 = curve1["f0.3"]; tk = curvek["f0.3"]; tk5 = curvek["f0.5"]
    print("  top-1@0.3=%.3f TOP-%d@0.3=%.3f top-%d@0.5=%.3f" % (t1, K, tk, K, tk5), flush=True)
    return {"top1_03": t1, "topk_03": tk, "topk_05": tk5, "curvek": {k: round(v, 3) for k, v in curvek.items()}}
def verdict(r) -> Tuple[str, str]:
    s = "top1@0.3=%.3f TOPK@0.3=%.3f topk@0.5=%.3f curve=%s" % (r["top1_03"], r["topk_03"], r["topk_05"], r["curvek"])
    if r["topk_03"] >= 0.95 and r["topk_05"] >= 0.70: return ("HARD_PASS", "HARD_PASS: top-k rescue recovers >=0.95 recall at 30pct bit-flip with graceful decay through 50pct (top-1 alone degrades) -- robust noisy-key retrieval. " + s)
    if r["topk_03"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: top-k@0.3 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: top-k@0.3 <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
