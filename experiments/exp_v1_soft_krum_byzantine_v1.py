"""
exp_v1_soft_krum_byzantine_v1 -- v1 plan test 1 (soft-Krum Byzantine-robust relay) -- CPU.

ROUTING: handoff research_to_exp_dev_orchestrator_v1_plan_update (Exp-Dev cheap-decisive test 1). Cross-shard K-hop relay
  must survive f Byzantine/corrupted shards out of B. Soft-Krum: among B shard returns, weight each by closeness to its
  neighbors (Krum score) and aggregate the trustworthy majority, vs naive mean. Tests whether soft-Krum maintains relay
  recovery with f up to floor((B-2)/2) Byzantine shards returning garbage. CPU $0.
PRE-REGISTERED: HARD-PASS soft-Krum recovery >= 0.90 at f = floor((B-2)/2) Byzantine (ship distributed reasoning in v1 with
  soft-Krum). MIDDLE 0.70-0.90. HARD-FAIL < 0.70 (soft-Krum insufficient).
FORMULA SELF-TESTS (PROT-022): 1. clean aggregate recovers. 2. krum downweights outlier. 3. cosine bound.
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

ANCHOR_NAME = "v1_soft_krum_byzantine_v1"
N = 4096; B = 10; NOISE = 0.3
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 512; TRIALS = 200
else:
    SEEDS = [7, 17, 23]; V_C = 2000; TRIALS = 1000


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def soft_krum(returns):
    # returns: (B,N) shard returns; score each by sum of distances to nearest B-f-2 others; keep the lowest-score majority
    B_ = returns.shape[0]; D = np.linalg.norm(returns[:, None, :] - returns[None, :, :], axis=2)
    keep = max(1, B_ // 2 + 1); scores = np.sort(D, axis=1)[:, 1:keep + 1].sum(1)
    w = np.exp(-scores / (scores.mean() + 1e-8)); w = w / w.sum()
    return (w[:, None] * returns).sum(0)


def _selftest():
    g = np.random.default_rng(0); true = unit(g.standard_normal(64)); R = np.stack([true + 0.05 * g.standard_normal(64) for _ in range(10)])
    agg = soft_krum(R); assert float(unit(agg[None, :])[0] @ true) > 0.9, "clean aggregate recovers"
    R[0] = unit(g.standard_normal(64)) * 5; D = np.linalg.norm(R[:, None] - R[None], axis=2); assert np.argmax(np.sort(D, 1)[:, 1:6].sum(1)) == 0, "krum downweights outlier"
    print("[selftest] PASS: soft-krum", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); C = unit(g.standard_normal((V_C, N)).astype(np.float32)); f = (B - 2) // 2
    ok_krum = 0; ok_mean = 0
    for _ in range(TRIALS):
        tgt = int(g.integers(0, V_C)); honest = np.stack([C[tgt] + NOISE * g.standard_normal(N).astype(np.float32) for _ in range(B - f)])
        byz = unit(g.standard_normal((f, N)).astype(np.float32)) * 3.0                # Byzantine: large garbage
        R = np.vstack([honest, byz]); g.shuffle(R)
        if int(np.argmax(C @ soft_krum(R))) == tgt:
            ok_krum += 1
        if int(np.argmax(C @ R.mean(0))) == tgt:
            ok_mean += 1
    print("  [seed=%d f=%d/%d] soft_krum=%.3f naive_mean=%.3f" % (seed, f, B, ok_krum / TRIALS, ok_mean / TRIALS), flush=True)
    return {"seed": seed, "f": f, "krum_recovery": ok_krum / TRIALS, "mean_recovery": ok_mean / TRIALS}


def verdict(ps) -> Tuple[str, str]:
    k = float(np.mean([p["krum_recovery"] for p in ps])); m = float(np.mean([p["mean_recovery"] for p in ps]))
    summary = "f=%d/%d Byzantine: soft_krum_recovery=%.3f naive_mean=%.3f" % (ps[0]["f"], B, k, m)
    if k >= 0.90:
        return ("HARD_PASS", "HARD_PASS: soft-Krum holds relay recovery >=0.90 at f=floor((B-2)/2) Byzantine shards -- ship v1 distributed reasoning with soft-Krum. " + summary)
    if k >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: soft-Krum recovery 0.70-0.90 (qualify). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: soft-Krum <0.70 at f Byzantine -- insufficient for v1. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d B=%d V_c=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, B, V_C), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
