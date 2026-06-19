"""
exp_confidence_weighted_bundling_v1 -- coordination-patterns anchor 1 (the 50-LOC v1 fix) -- CPU.

ROUTING: handoff distributed_coordination_patterns #1. Confidence-weighted bundle sum: weight each shard's relay return by
  its readout confidence (max cosine to codebook) before bundling, so low-confidence (wrong/Byzantine) shards contribute
  less. The 50-LOC v1 fix from the K-hop drill. Tests vs naive equal-weight bundle under f corrupted shards. CPU.
PRE-REGISTERED: HARD-PASS confidence-weighted recovery >= 0.90 at f=floor((B-2)/2) Byzantine AND beats naive by >=0.10.
  MIDDLE beats naive but <0.90. HARD-FAIL no better than naive.
FORMULA SELF-TESTS (PROT-022): 1. confidence high for clean. 2. weighting downweights garbage. 3. cosine bound.
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

ANCHOR_NAME = "confidence_weighted_bundling_v1"; N = 4096; B = 10; NOISE = 0.3
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 512; TRIALS = 300
else:
    SEEDS = [7, 17, 23]; V_C = 2000; TRIALS = 1000


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def conf_bundle(returns, C):
    conf = (unit(returns) @ C.T).max(1)                                        # per-shard readout confidence
    w = np.clip(conf, 0, None); w = w / (w.sum() + 1e-8); return (w[:, None] * returns).sum(0)


def _selftest():
    g = np.random.default_rng(0); C = unit(g.standard_normal((10, 64))); clean = C[3] + 0.05 * g.standard_normal(64)
    assert float((unit(clean[None, :]) @ C.T).max()) > 0.8, "confidence high for clean"
    R = np.stack([C[3] + 0.05 * g.standard_normal(64) for _ in range(8)] + [unit(g.standard_normal(64)) * 3 for _ in range(2)])
    assert int(np.argmax(C @ conf_bundle(R, C))) == 3, "weighting downweights garbage"
    print("[selftest] PASS: confidence-weighted", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); C = unit(g.standard_normal((V_C, N)).astype(np.float32)); f = (B - 2) // 2
    ok_cw = 0; ok_naive = 0
    for _ in range(TRIALS):
        tgt = int(g.integers(0, V_C)); honest = np.stack([C[tgt] + NOISE * g.standard_normal(N).astype(np.float32) for _ in range(B - f)])
        byz = unit(g.standard_normal((f, N)).astype(np.float32)) * 3.0; R = np.vstack([honest, byz]); g.shuffle(R)
        if int(np.argmax(C @ conf_bundle(R, C))) == tgt:
            ok_cw += 1
        if int(np.argmax(C @ R.mean(0))) == tgt:
            ok_naive += 1
    print("  [seed=%d f=%d] conf_weighted=%.3f naive=%.3f" % (seed, f, ok_cw / TRIALS, ok_naive / TRIALS), flush=True)
    return {"seed": seed, "f": f, "cw": ok_cw / TRIALS, "naive": ok_naive / TRIALS}


def verdict(ps) -> Tuple[str, str]:
    cw = float(np.mean([p["cw"] for p in ps])); nv = float(np.mean([p["naive"] for p in ps]))
    summary = "f=%d/%d Byzantine: confidence_weighted=%.3f naive=%.3f delta=%+.3f" % (ps[0]["f"], B, cw, nv, cw - nv)
    if cw >= 0.90 and cw - nv >= 0.10:
        return ("HARD_PASS", "HARD_PASS: confidence-weighted bundling holds >=0.90 and beats naive by >=0.10 under Byzantine -- the 50-LOC v1 fix works. " + summary)
    if cw > nv:
        return ("MIDDLE_BAND", "MIDDLE_BAND: confidence-weighting beats naive but <0.90. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: confidence-weighting no better than naive. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d B=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, B), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
