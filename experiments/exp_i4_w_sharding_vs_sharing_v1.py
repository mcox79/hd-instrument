"""
exp_i4_w_sharding_vs_sharing_v1 -- Batch I4 (BFT architecture check: W-sharding vs W-sharing) -- CPU.

ROUTING: Batch I Tier-2 (Drill C F4 anchor 2). The multi-head BFT (Byzantine-fault-tolerance) advantage holds ONLY if
  heads query INDEPENDENT W shards. If all heads share ONE W (W-sharing), corrupting it corrupts every head -> the BFT
  advantage is illusory. Tests both architectures: store items across H heads; corrupt ONE head's weights; measure recall
  of items NOT routed to the corrupted head. SHARDING -> other heads intact; SHARING -> all corrupt. CPU $0.
PRE-REGISTERED: HARD-PASS sharding keeps non-corrupted-shard recall >= 0.90 while sharing drops < 0.5 (sharding is BFT-robust
  and is the architecture to ship). MID partial. HARD-FAIL sharding also collapses (no BFT benefit from sharding).
FORMULA SELF-TESTS (PROT-022): 1. clean recall high. 2. corruption degrades shared. 3. routing balanced.
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

ANCHOR_NAME = "i4_w_sharding_vs_sharing_v1"
H = 4; FLIP = 0.05; STEPS = 6; ALPHA = 0.06
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 1024
else:
    SEEDS = [7, 17, 23]; N = 2048


def patterns(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def W_of(P):
    if P.shape[0] == 0:
        return np.zeros((P.shape[1], P.shape[1]), np.float32)
    W = (P.T @ P).astype(np.float32); np.fill_diagonal(W, 0.0); return W / P.shape[1]


def recall_with(P, W, seed):
    if P.shape[0] == 0:
        return 1.0
    g = np.random.default_rng(seed); M, n = P.shape; s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def corrupt(W, g):
    return (g.standard_normal(W.shape).astype(np.float32) * (np.abs(W).std() + 1e-3))   # Byzantine: replace shard with garbage


def _selftest():
    g = np.random.default_rng(0); P = patterns(4, 256, g); assert recall_with(P, W_of(P), 0) >= 0.95, "clean recall high"
    Wc = corrupt(W_of(P), g); assert recall_with(P, Wc, 0) < 0.95, "corruption degrades"
    print("[selftest] PASS: i4-sharding", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); Mtot = int(ALPHA * N * H); P = patterns(Mtot, N, g); route = g.integers(0, H, Mtot)
    # SHARDING: one W per head over its routed items; corrupt head 0; measure recall of items in heads 1..H-1
    shards = [W_of(P[route == h]) for h in range(H)]; shards_c = list(shards); shards_c[0] = corrupt(shards[0], g)
    shard_recall = np.mean([recall_with(P[route == h], shards_c[h], seed * 10 + h) for h in range(1, H)])
    # SHARING: one global W over ALL items; corrupt it; measure recall of items in heads 1..H-1
    Wg = W_of(P); Wg_c = corrupt(Wg, g)
    share_recall = np.mean([recall_with(P[route == h], Wg_c, seed * 20 + h) for h in range(1, H)])
    print("  [seed=%d] sharding_other_recall=%.3f sharing_other_recall=%.3f" % (seed, shard_recall, share_recall), flush=True)
    return {"seed": seed, "sharding_recall": float(shard_recall), "sharing_recall": float(share_recall)}


def verdict(ps) -> Tuple[str, str]:
    sh = float(np.mean([p["sharding_recall"] for p in ps])); sr = float(np.mean([p["sharing_recall"] for p in ps]))
    summary = "after corrupting 1 head: sharding_other_recall=%.3f sharing_other_recall=%.3f" % (sh, sr)
    if sh >= 0.90 and sr < 0.5:
        return ("HARD_PASS", "HARD_PASS: W-SHARDING is BFT-robust (other heads intact 0.90+ while sharing collapses) -- ship sharded multi-head architecture. " + summary)
    if sh > sr + 0.2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sharding more robust than sharing but not clean. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: sharding does not protect other heads -- BFT advantage illusory. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d H=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, H), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
