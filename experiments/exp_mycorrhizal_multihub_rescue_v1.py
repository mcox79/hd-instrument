"""
exp_mycorrhizal_multihub_rescue_v1 -- mycorrhizal MULTI-HUB init rescue (2x for the 0.57 single-hub MIDDLE) -- CPU.

ROUTING: 2x_negatives_FILL (mycorrhizal hub-init rescue per always-research-negatives rule). Single-source hub-init gave 0.57
  coverage (MIDDLE). RESCUE: initialize a new customer's cache from the UNION of top-hubs across MULTIPLE existing customers
  (each shares the common popular head + contributes its own tail hubs), giving broader hub coverage. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS multi-hub init >= 0.70 coverage at Q=100 (clears the original gate). MIDDLE 0.57-0.70. HARD-FAIL < 0.57.
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
ANCHOR_NAME = "mycorrhizal_multihub_rescue_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def zipf(v, s=1.1):
    p = 1.0 / np.power(np.arange(1, v + 1), s); return p / p.sum()


def _selftest():
    assert zipf(10)[0] > zipf(10)[9], "zipf head"; assert len(set([1, 2]) | set([2, 3])) == 3, "union"; print("[selftest] PASS: mycorrhizal-multihub-rescue", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(44); V = 2000; QB = 100; HUBS_PER = 200
    M_SRC = 5 if SMOKE else 12
    pA = zipf(V)
    # new customer B: shared head + own tail
    permB = g.permutation(V); tailB = np.zeros(V); tailB[permB] = zipf(V); pB = 0.6 * pA + 0.4 * tailB; pB /= pB.sum()
    streamB = g.choice(V, QB, p=pB)
    # single-hub baseline: top hubs from pA only
    single = set(int(i) for i in np.argsort(pA)[::-1][:HUBS_PER])
    # multi-hub: union of top hubs from M_SRC customers (each shared head + own tail)
    multi = set()
    for _ in range(M_SRC):
        perm = g.permutation(V); tail = np.zeros(V); tail[perm] = zipf(V); pc = 0.6 * pA + 0.4 * tail; pc /= pc.sum()
        multi |= set(int(i) for i in np.argsort(pc)[::-1][:HUBS_PER])
    def cov(cache):
        return sum(int(b) in cache for b in streamB) / QB
    s_cov = cov(single); m_cov = cov(multi)
    print("  coverage at Q=%d: single-hub=%.3f multi-hub(%d srcs, %d uniq hubs)=%.3f" % (QB, s_cov, M_SRC, len(multi), m_cov), flush=True)
    return {"single": s_cov, "multi": m_cov, "n_hubs": len(multi)}


def verdict(r) -> Tuple[str, str]:
    m = r["multi"]; s = "multi-hub coverage=%.3f vs single-hub=%.3f (%d uniq hubs)" % (m, r["single"], r["n_hubs"])
    if m >= 0.70:
        return ("HARD_PASS", "HARD_PASS: multi-hub init reaches >=0.70 coverage at Q=100 (clears the original gate; single-hub 0.57 rescued) -- pooling hubs across customers warm-starts new customers well. " + s)
    if m >= 0.57:
        return ("MIDDLE_BAND", "MIDDLE_BAND: multi-hub 0.57-0.70 -- improves over single-hub but below gate. " + s)
    return ("HARD_FAIL", "HARD_FAIL: multi-hub < 0.57 (no improvement). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
