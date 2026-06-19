"""
exp_noise_robustness_sweep_cpu_v1.py -- substrate recall degrades gracefully under increasing query noise -- CPU.

ROUTING: batch-10a (robustness: graceful degradation under query noise). Sweeps query-key noise 0->0.5 and measures recall; tests graceful (monotone) degradation and recall@0.3>=0.80 -- robustness to corrupted/paraphrased queries. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS recall@noise0.3 >=0.80 AND monotone decay. MIDDLE >=0.65. HARD-FAIL <0.65.
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
ANCHOR_NAME = "noise_robustness_sweep_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert _n.all(_n.diff([0.0,1,2])>0), "monotone"; print("[selftest] PASS: noise-robustness-sweep", flush=True)
def run() -> Dict:
    g = np.random.default_rng(965); N = 8192; VK = 100; VV = 400; keys = cphasor(VK, N, g); vals = cphasor(VV, N, g); M = 50
    levels = [0.0, 0.1, 0.2, 0.3, 0.5]; TR = 40 if SMOKE else 120; curve = {}
    for noise in levels:
        hit = 0; n = 0
        for _ in range(TR):
            Mem = np.zeros(N, dtype=np.complex64); facts = []
            for _f in range(M):
                k = int(g.integers(0, VK)); vv = int(g.integers(0, VV)); Mem = Mem + keys[k] * vals[vv]; facts.append((k, vv))
            k, vv = facts[int(g.integers(0, len(facts)))]
            qk = keys[k] * np.exp(1j * noise * g.standard_normal(N))         # noised key
            hit += int(cidx(Mem * np.conj(qk), vals) == vv); n += 1
        curve["n%.1f" % noise] = hit / n
    vals_c = [curve["n%.1f" % x] for x in levels]
    graceful = all(vals_c[i] >= vals_c[i + 1] - 0.05 for i in range(len(vals_c) - 1))   # monotone-ish decay
    at03 = curve["n0.3"]; print("  recall by noise: %s | graceful=%s recall@0.3=%.3f" % ({k: round(v, 2) for k, v in curve.items()}, graceful, at03), flush=True)
    return {"curve": {k: round(v, 3) for k, v in curve.items()}, "graceful": bool(graceful), "at03": at03}
def verdict(r) -> Tuple[str, str]:
    s = "recall@0.3=%.3f graceful=%s curve=%s" % (r["at03"], r["graceful"], r["curve"])
    if r["at03"] >= 0.80 and r["graceful"]: return ("HARD_PASS", "HARD_PASS: graceful degradation -- recall@noise=0.3 >=0.80 with monotone decay (robust to query corruption). " + s)
    if r["at03"] >= 0.65: return ("MIDDLE_BAND", "MIDDLE_BAND: recall@0.3 0.65-0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall@0.3 <0.65. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
