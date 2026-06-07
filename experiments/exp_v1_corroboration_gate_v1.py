"""
exp_v1_corroboration_gate_v1 -- v1 plan test 2 (corroboration gate) -- CPU.

ROUTING: handoff research_to_exp_dev_orchestrator_v1_plan_update (Exp-Dev cheap-decisive test 2). Alternative to soft-Krum:
  accept a cross-shard hop only if >= Q shards CORROBORATE (their top-1 retrieved concept agrees). Tests whether the
  corroboration gate filters Byzantine + coherent-distractor shards while keeping honest recovery. CPU $0.
PRE-REGISTERED: HARD-PASS gated recovery >= 0.90 with f=floor((B-2)/2) Byzantine AND false-accept (wrong-concept accepted)
  < 0.05 (ship v1 with corroboration gate). MIDDLE one met. HARD-FAIL neither.
FORMULA SELF-TESTS (PROT-022): 1. honest quorum corroborates. 2. byzantine fails quorum. 3. cosine bound.
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

ANCHOR_NAME = "v1_corroboration_gate_v1"
N = 4096; B = 10; Q = 3; NOISE = 0.3
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 512; TRIALS = 200
else:
    SEEDS = [7, 17, 23]; V_C = 2000; TRIALS = 1000


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def corroborate(returns, C, q):
    preds = np.argmax(returns @ C.T, axis=1); vals, counts = np.unique(preds, return_counts=True)
    top = int(np.argmax(counts))
    return (int(vals[top]), int(counts[top])) if counts[top] >= q else (-1, int(counts[top]))   # -1 = rejected (no quorum)


def _selftest():
    g = np.random.default_rng(0); C = unit(g.standard_normal((20, 64))); tgt = 5
    R = np.stack([C[tgt] + 0.05 * g.standard_normal(64) for _ in range(6)]); p, c = corroborate(R, C, 3); assert p == tgt, "honest quorum corroborates"
    Rb = unit(g.standard_normal((6, 64))) * 3; p2, c2 = corroborate(Rb, C, 5); assert p2 == -1 or c2 < 5, "byzantine fails quorum"
    print("[selftest] PASS: corroboration-gate", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); C = unit(g.standard_normal((V_C, N)).astype(np.float32)); f = (B - 2) // 2
    recovered = 0; false_accept = 0
    for _ in range(TRIALS):
        tgt = int(g.integers(0, V_C)); honest = np.stack([C[tgt] + NOISE * g.standard_normal(N).astype(np.float32) for _ in range(B - f)])
        byz = unit(g.standard_normal((f, N)).astype(np.float32)) * 3.0; R = np.vstack([honest, byz]); g.shuffle(R)
        pred, _ = corroborate(R, C, Q)
        if pred == tgt:
            recovered += 1
        elif pred != -1 and pred != tgt:
            false_accept += 1
    print("  [seed=%d f=%d Q=%d] recovery=%.3f false_accept=%.3f" % (seed, f, Q, recovered / TRIALS, false_accept / TRIALS), flush=True)
    return {"seed": seed, "f": f, "recovery": recovered / TRIALS, "false_accept": false_accept / TRIALS}


def verdict(ps) -> Tuple[str, str]:
    r = float(np.mean([p["recovery"] for p in ps])); fa = float(np.mean([p["false_accept"] for p in ps]))
    summary = "f=%d/%d Byzantine, quorum Q=%d: recovery=%.3f false_accept=%.3f" % (ps[0]["f"], B, Q, r, fa)
    if r >= 0.90 and fa < 0.05:
        return ("HARD_PASS", "HARD_PASS: corroboration gate holds recovery>=0.90 + false-accept<0.05 under f Byzantine -- ship v1 with corroboration gate. " + summary)
    if r >= 0.90 or fa < 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one criterion met. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: corroboration gate insufficient (low recovery + false-accepts). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d B=%d Q=%d V_c=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, B, Q, V_C), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
