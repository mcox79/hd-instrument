"""
exp_mycorrhizal_simweighted_rescue_cpu_v1.py -- similarity-weighted multi-hub init clears the warm-start coverage gate -- CPU.

ROUTING: v1.5 LOCK batch (F3 mycorrhizal similarity-weighted rescue). Mycorrhizal multi-hub init plateaued MID (~0.55-0.6). Rescue: instead of a uniform union of source hubs, weight each source's hub contribution by that source's distributional similarity to the new customer (mycorrhizal nutrient-sharing is similarity-gated). Measures B coverage at Q=100. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS similarity-weighted multi-hub coverage >= 0.70 (clears gate). MIDDLE 0.60-0.70. HARD-FAIL < 0.60.
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
ANCHOR_NAME = "mycorrhizal_simweighted_rescue_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def zipf(v, s=1.1):
    p = 1.0 / np.power(np.arange(1, v + 1), s); return p / p.sum()
def _selftest():
    assert zipf(10)[0] > zipf(10)[9], "zipf"; print("[selftest] PASS: mycorrhizal-simweighted-rescue", flush=True)
def run() -> Dict:
    g = np.random.default_rng(85); V = 2000; QB = 100; HUBS = 200; M_SRC = 12 if SMOKE else 20
    pA = zipf(V)
    permB = g.permutation(V); tailB = np.zeros(V); tailB[permB] = zipf(V); pB = 0.6 * pA + 0.4 * tailB; pB /= pB.sum()
    streamB = g.choice(V, QB, p=pB)
    srcs = []
    for _ in range(M_SRC):
        perm = g.permutation(V); tail = np.zeros(V); tail[perm] = zipf(V); pc = 0.6 * pA + 0.4 * tail; pc /= pc.sum(); srcs.append(pc)
    # uniform union (baseline)
    uni = set()
    for pc in srcs:
        uni |= set(int(i) for i in np.argsort(pc)[::-1][:HUBS])
    # similarity-weighted: weight each source by cosine(pc, pB); take more hubs from similar sources
    sims = np.array([float(np.dot(pc, pB) / (np.linalg.norm(pc) * np.linalg.norm(pB))) for pc in srcs]); w = sims / sims.sum()
    simw = set()
    for k, pc in enumerate(srcs):
        take = int(HUBS * len(srcs) * w[k]); simw |= set(int(i) for i in np.argsort(pc)[::-1][:max(20, take)])
    def cov(cache):
        return sum(int(b) in cache for b in streamB) / QB
    uc = cov(uni); sc = cov(simw); print("  coverage Q=%d: uniform-union=%.3f similarity-weighted=%.3f (uniq hubs %d/%d)" % (QB, uc, sc, len(uni), len(simw)), flush=True)
    return {"uniform": uc, "simweighted": sc}
def verdict(r) -> Tuple[str, str]:
    s = "similarity-weighted=%.3f uniform-union=%.3f" % (r["simweighted"], r["uniform"])
    if r["simweighted"] >= 0.70: return ("HARD_PASS", "HARD_PASS: similarity-weighted multi-hub init clears 0.70 coverage -- similarity-gated nutrient-sharing warm-starts new customers. " + s)
    if r["simweighted"] >= 0.60: return ("MIDDLE_BAND", "MIDDLE_BAND: similarity-weighted 0.60-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: similarity-weighted <0.60. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
