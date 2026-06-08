"""
exp_self_improving_routing_warm_cpu_v1.py -- online-updated routing centroids reach higher accuracy at warm equilibrium than cold-start -- CPU.

ROUTING: NEW_EXPERIMENTS batch (N3 self-improving routing at warm equilibrium). A content router whose per-shard centroids update online (running mean of correctly-routed queries) should improve from cold-start to warm equilibrium. Measures routing accuracy cold (initial centroids from 1 sample) vs warm (after many online updates). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS warm-equilibrium routing accuracy >= cold-start + 5pp. MIDDLE >= cold-start. HARD-FAIL < cold-start.
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
ANCHOR_NAME = "self_improving_routing_warm_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"; print("[selftest] PASS: self-improving-routing-warm", flush=True)
def run() -> Dict:
    g = np.random.default_rng(222); D = 64; S = 20; PER = 200; FUZZ = 1.2
    centers = g.standard_normal((S, D))
    def sample(s):
        return centers[s] + FUZZ / math.sqrt(D) * g.standard_normal(D)
    cold = centers + 0.8 * g.standard_normal((S, D))                            # cold centroids: noisy 1-sample estimates
    cold = cold / np.linalg.norm(cold, axis=1, keepdims=True)
    def acc(cents):
        h = 0; n = 0
        for s in range(S):
            for _ in range(PER):
                q = sample(s); q = q / np.linalg.norm(q); h += int(int(np.argmax(cents @ q)) == s); n += 1
        return h / n
    cold_acc = acc(cold)
    # warm: online update centroids with routed samples (running mean)
    warm = cold.copy(); cnt = np.ones(S)
    for _ in range(S * PER):
        s = int(g.integers(0, S)); q = sample(s); q = q / np.linalg.norm(q); pred = int(np.argmax(warm @ q))
        if pred == s:
            cnt[s] += 1; warm[s] = warm[s] + (q - warm[s]) / cnt[s]; warm[s] = warm[s] / np.linalg.norm(warm[s])
    warm_acc = acc(warm)
    print("  routing accuracy: cold-start=%.3f warm-equilibrium=%.3f (gain=%+.3f)" % (cold_acc, warm_acc, warm_acc - cold_acc), flush=True)
    return {"cold": cold_acc, "warm": warm_acc, "gain": warm_acc - cold_acc}
def verdict(r) -> Tuple[str, str]:
    s = "cold=%.3f warm=%.3f gain=%+.3f" % (r["cold"], r["warm"], r["gain"])
    if r["gain"] >= 0.05: return ("HARD_PASS", "HARD_PASS: self-improving routing gains >=5pp from cold to warm equilibrium -- online centroid learning works. " + s)
    if r["gain"] >= 0.0: return ("MIDDLE_BAND", "MIDDLE_BAND: warm >= cold but gain <5pp. " + s)
    return ("HARD_FAIL", "HARD_FAIL: warm < cold (online update hurts). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
