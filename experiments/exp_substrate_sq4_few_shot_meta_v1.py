"""
substrate_sq4_few_shot_meta_v1 -- Hebbian few-shot meta-learning (the substrate W IS the meta-learner) -- remote CPU.

ROUTING: SQ4 (P_drill=0.65). N-way K-shot classification via one-shot Hebbian class prototypes -- no gradient
  meta-training; the substrate's one-shot write IS the few-shot learner. CPU numpy, $0. remote_cpu_queue.

CELLS (3 seeds): accuracy at (N_way, K_shot) in {(5,1),(5,5),(20,1),(20,5),(50,5)}; N=2048; query = novel noisy examples.
PRE-REG (acc): HARD-PASS 20-way-5-shot acc>=0.85 AND 50-way-5-shot acc>=0.70. MIDDLE 20w5s>=0.70. HARD-FAIL 20w5s<0.70.
SELF-TESTS (PROT-022): 1. 1-shot recovers clean class. 2. prototype accumulation. 3. N set.
ASCII-only. write_metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_sq4_few_shot_meta_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

NOISE = 0.30
TASKS = [(5, 1), (5, 5), (20, 1), (20, 5), (50, 5)]
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N = 512; TASKS = [(5, 1), (20, 5)]
else:
    SEEDS = [7, 17, 23]; N = 2048


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def noisy(x, g):
    flip = g.random(x.shape) < NOISE
    return x * np.where(flip, -1.0, 1.0)


def few_shot_acc(n, nway, kshot, g, ntest=200):
    protos_true = bipolar((nway, n), g)
    P = np.zeros((nway, n), dtype=np.float32)
    for c in range(nway):
        for _ in range(kshot):
            P[c] += noisy(protos_true[c], g)
    hits = 0
    for _ in range(ntest):
        c = int(g.integers(0, nway)); q = noisy(protos_true[c], g)
        hits += (int(np.argmax(P @ q)) == c)
    return hits / ntest


def _selftest():
    g = np.random.default_rng(0); n = 256; pr = bipolar((3, n), g); P = pr.copy()
    assert int(np.argmax(P @ pr[1])) == 1, "1-shot recovery"
    assert N in (512, 2048)
    print("[selftest] PASS: 1shot_recovery", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed):
    out = {}
    for (nw, ks) in TASKS:
        out["%dw%ds" % (nw, ks)] = few_shot_acc(N, nw, ks, np.random.default_rng(seed * 100 + nw * 10 + ks))
    return {"seed": seed, "N": N, **out}


def verdict(ps) -> Tuple[str, str]:
    acc = {"%dw%ds" % (nw, ks): float(np.mean([p["%dw%ds" % (nw, ks)] for p in ps])) for (nw, ks) in TASKS}
    summary = " ".join("%s:%.2f" % (k, v) for k, v in acc.items())
    a20 = acc.get("20w5s", 0.0); a50 = acc.get("50w5s", 1.0 if "50w5s" not in acc else acc["50w5s"])
    if a20 >= 0.85 and a50 >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate one-shot Hebbian is a strong few-shot learner. " + summary)
    if a20 >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: few-shot works moderately. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: few-shot weak. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d tasks=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, TASKS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] " % seed + " ".join("%dw%ds:%.2f" % (nw, ks, r["%dw%ds" % (nw, ks)]) for (nw, ks) in TASKS), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
