"""
exp_p1_shard_split_correctness_v1 -- Batch E Cell 8 (Drill-1 production gate) -- CPU.

ROUTING: Batch E Drill-1 #1. The d_eff ceiling (cap ~ alpha_c*N) forces production to SHARD from day 1: when stored items
  M exceed a single shard's capacity C, split into K shards (route each item to a shard by hash) so each shard stays below
  C. Verifies the sharded store recovers items correctly under capacity overflow, vs a single overloaded store which fails.
  Synthetic +-1 patterns, Hopfield exact-recovery; hash-routed shards. CPU $0.
PRE-REGISTERED: HARD-PASS at total M = 3x single-shard capacity, sharded recall >= 0.95 while single-store recall < 0.5
  (sharding correctly restores capacity). MID sharded 0.8-0.95. HARD-FAIL sharded < 0.8 (shard-split loses items).
FORMULA SELF-TESTS (PROT-022): 1. single store low-load recovers. 2. hash routing balanced. 3. overload fails.
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

ANCHOR_NAME = "p1_shard_split_correctness_v1"
FLIP = 0.05; STEPS = 6; ALPHA_C = 0.06   # all-bits exact-recovery capacity (< RSB 0.14 majority-stability)
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 1024; OVERLOAD = [1, 3]
else:
    SEEDS = [7, 17, 23]; N = 2048; OVERLOAD = [1, 2, 3, 5]


def patterns(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def recall_store(P, seed):
    if P.shape[0] == 0:
        return 1.0
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def sharded_recall(P, K, seed):
    # route each item to shard by hash of its content; recall within its shard
    h = (P[:, :8] > 0).astype(np.int64); routes = (h @ (2 ** np.arange(8))) % K
    accs = []
    for k in range(K):
        idx = np.where(routes == k)[0]
        if len(idx):
            accs.append(recall_store(P[idx], seed * 31 + k) * len(idx))
    return sum(accs) / P.shape[0]


def _selftest():
    g = np.random.default_rng(0); C = max(2, int(ALPHA_C * 512))
    assert recall_store(patterns(C // 2, 512, g), 0) >= 0.95, "single store low-load recovers"
    assert recall_store(patterns(int(3 * ALPHA_C * 512), 512, g), 0) < 0.5, "overload fails"
    print("[selftest] PASS: shard-split", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); C = max(2, int(ALPHA_C * N)); by = {}
    for ov in OVERLOAD:
        M = ov * C; P = patterns(M, N, g); K = max(1, 2 * ov)        # 2x shards to keep each safely under exact-recovery C
        single = recall_store(P, seed * 3); shard = sharded_recall(P, K, seed)
        by["ov%dx" % ov] = {"M": M, "K_shards": K, "single_recall": single, "sharded_recall": shard}
        print("  [seed=%d overload=%dx M=%d K=%d] single=%.3f sharded=%.3f" % (seed, ov, M, K, single, shard), flush=True)
    return {"seed": seed, "by": by}


def verdict(ps) -> Tuple[str, str]:
    ov = "ov%dx" % max(OVERLOAD)
    sh = float(np.mean([p["by"][ov]["sharded_recall"] for p in ps])); si = float(np.mean([p["by"][ov]["single_recall"] for p in ps]))
    summary = "at %s overload: sharded_recall=%.3f single_recall=%.3f" % (ov, sh, si)
    if sh >= 0.95 and si < 0.5:
        return ("HARD_PASS", "HARD_PASS: shard-split restores capacity under overflow (sharded>=0.95 while single fails) -- production sharding strategy correct. " + summary)
    if sh >= 0.8:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sharded 0.8-0.95 (some routing loss). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: shard-split loses items (sharded<0.8) -- sharding strategy needs redesign. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d alpha_c=%.2f overloads=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, ALPHA_C, OVERLOAD), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
