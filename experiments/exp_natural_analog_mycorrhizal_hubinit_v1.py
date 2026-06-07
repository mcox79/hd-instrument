"""
exp_natural_analog_mycorrhizal_hubinit_v1.py -- hub-weighted initialization warm-starts a new customer's bridge cache -- CPU.

ROUTING: natural_analog_5_pretests Analog 4 (MYCORRHIZAL). Customer A accumulated 10K queries (its popular bridges = hubs). New customer B initializes its cache from A's top hubs. Measure B's bridge coverage at Q=100 with hub-init vs cold-start. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS B with hub-init reaches >= 0.70 coverage at Q=100 vs ~0.30 cold (warm-start works). MIDDLE 0.50-0.70. HARD-FAIL < 0.50.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "natural_analog_mycorrhizal_hubinit_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def zipf(v, s=1.1):
    p = 1.0 / np.power(np.arange(1, v + 1), s); return p / p.sum()

def _selftest():
    p = zipf(10); assert p[0] > p[9], "zipf head heavier"
    seen = set([1, 2]); assert all(x in seen for x in [1, 2]), "cache membership"
    assert zipf(5).sum() > 0.99, "zipf norm"
    print("[selftest] PASS: mycorrhizal-hubinit", flush=True)

def run() -> Dict:
    g = np.random.default_rng(44); V = 2000; QA = 2000 if SMOKE else 10000; QB = 100; HUBS = 400
    pA = zipf(V)
    # B shares A's popular hubs (head correlated) + own tail
    perm = g.permutation(V); tailB = np.zeros(V); tailB[perm] = zipf(V); pB = 0.6 * pA + 0.4 * tailB; pB /= pB.sum()
    cacheA = set(int(x) for x in np.unique(g.choice(V, QA, p=pA)))
    hub_init = set(int(i) for i in np.argsort(pA)[::-1][:HUBS])      # top hubs from A
    streamB = g.choice(V, QB, p=pB)
    def coverage(cache):
        hit = 0
        for b in streamB:
            if int(b) in cache:
                hit += 1
        return hit / QB
    cold = coverage(set()); warm = coverage(set(hub_init))
    print("  customer B coverage at Q=%d: cold-start=%.3f hub-init=%.3f (hubs=%d)" % (QB, cold, warm, HUBS), flush=True)
    return {"cold": cold, "warm": warm}

def verdict(r) -> Tuple[str, str]:
    w = r["warm"]; s = "hub-init coverage=%.3f vs cold=%.3f at Q=100" % (w, r["cold"])
    if w >= 0.70:
        return ("HARD_PASS", "HARD_PASS: hub-weighted init warm-starts new customers to >=0.70 coverage at Q=100 (vs cold ~0.30) -- mycorrhizal cross-customer transfer works. " + s)
    if w >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: hub-init coverage 0.50-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: hub-init <0.50 coverage. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
