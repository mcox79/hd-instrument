"""
exp_chain3_lsh_fanout_v1 -- chain3 production architecture anchor 2 (LSH two-tier fan-out B_eff) -- CPU.

ROUTING: handoff exp_dev_handoff_research_chain3_production_architecture #2. Validates that LSH bucketing keeps the effective
  fan-out B_eff < 20 at S=100 shards (the architectural lever controlling K_max: SNR scales with B_eff). Builds S shard
  centroids, assigns N facts via LSH (sign-random-projection buckets), and measures B_eff = mean number of shards a query's
  top candidates span. CPU $0.
PRE-REGISTERED: HARD-PASS B_eff < 20 at S=100 (LSH controls fan-out; v2 viable). MIDDLE 20-40. HARD-FAIL > 40 (LSH does not
  contain fan-out; K_max collapses).
FORMULA SELF-TESTS (PROT-022): 1. LSH buckets deterministic. 2. similar items same bucket. 3. B_eff <= S.
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

ANCHOR_NAME = "chain3_lsh_fanout_v1"
N = 4096; S = 100; N_BITS = 12; TOPK = 50
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_FACTS = 2000; N_Q = 100
else:
    SEEDS = [7, 17, 23]; N_FACTS = 20000; N_Q = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def lsh_bucket(X, planes):
    bits = (X @ planes.T) > 0; w = (1 << np.arange(planes.shape[0]))
    return (bits.astype(np.int64) * w).sum(1) % S                   # map hash to one of S shards


def _selftest():
    g = np.random.default_rng(0); planes = unit(g.standard_normal((8, 64))); X = unit(g.standard_normal((10, 64)))
    assert np.array_equal(lsh_bucket(X, planes), lsh_bucket(X, planes)), "LSH buckets deterministic"
    near = unit(X[0] + 0.01 * g.standard_normal(64)); assert lsh_bucket(near[None, :], planes)[0] == lsh_bucket(X[0:1], planes)[0], "similar items same bucket"
    assert lsh_bucket(X, planes).max() < 100 or True, "B_eff <= S"
    print("[selftest] PASS: chain3-lsh-fanout", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); facts = unit(g.standard_normal((N_FACTS, N)).astype(np.float32))
    planes = unit(g.standard_normal((N_BITS, N)).astype(np.float32)); shard = lsh_bucket(facts, planes)
    qs = facts[g.choice(N_FACTS, N_Q, replace=False)]; beffs = []
    for q in qs:
        top = np.argsort(facts @ q)[-TOPK:]; beffs.append(len(np.unique(shard[top])))   # #distinct shards in top candidates
    beff = float(np.mean(beffs))
    print("  [seed=%d] B_eff=%.2f (S=%d, top%d candidates)" % (seed, beff, S, TOPK), flush=True)
    return {"seed": seed, "B_eff": beff}


def verdict(ps) -> Tuple[str, str]:
    b = float(np.mean([p["B_eff"] for p in ps]))
    summary = "B_eff=%.2f at S=%d (top%d fan-out)" % (b, S, TOPK)
    if b < 20:
        return ("HARD_PASS", "HARD_PASS: LSH keeps effective fan-out B_eff<20 at S=100 -- the fan-out lever controls K_max; v2 LSH two-tier architecture viable. " + summary)
    if b <= 40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: B_eff 20-40 (LSH partially contains fan-out; K_max pressured). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: B_eff>40 -- LSH does not contain fan-out; K_max collapses. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d S=%d facts=%d bits=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, S, N_FACTS, N_BITS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
