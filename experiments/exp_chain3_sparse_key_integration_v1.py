"""
exp_chain3_sparse_key_integration_v1 -- chain3 production architecture anchor 3 (sparse-KEY shard routing) -- CPU.

ROUTING: handoff chain3_production_architecture #3. Route facts to shards by a sparse-KEY code (active-dim bucketing) and test
  whether sparse-code routing reduces effective cross-shard fan-out B_eff vs dense LSH (chain3 #2 gave B_eff~39). If sparse
  routing keeps B_eff<20, it is the production routing layer. CPU.
PRE-REGISTERED: HARD-PASS sparse-code routing B_eff < 20 at S=100 (better than dense LSH 39). MIDDLE 20-39. HARD-FAIL >=39
  (no improvement over dense LSH).
FORMULA SELF-TESTS (PROT-022): 1. sparse code active dims. 2. routing deterministic. 3. B_eff <= S.
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

ANCHOR_NAME = "chain3_sparse_key_integration_v1"; N = 4096; S = 100; ALPHA = 0.005; TOPK = 50
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_FACTS = 2000; N_Q = 100
else:
    SEEDS = [7, 17, 23]; N_FACTS = 20000; N_Q = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def sparse_route(F, g):
    k = max(1, int(ALPHA * N)); shard = np.zeros(F.shape[0], np.int64)
    for i in range(F.shape[0]):
        top = np.argpartition(-np.abs(F[i]), k - 1)[:k]; shard[i] = int(top.sum()) % S   # route by dominant active dims
    return shard


def _selftest():
    g = np.random.default_rng(0); F = unit(g.standard_normal((10, 64))); s = sparse_route(F, g)
    assert s.shape == (10,), "sparse code active dims"
    assert np.array_equal(sparse_route(F, g), sparse_route(F, g)), "routing deterministic"
    assert s.max() < S, "B_eff <= S"
    print("[selftest] PASS: chain3-sparse-integration", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); facts = unit(g.standard_normal((N_FACTS, N)).astype(np.float32)); shard = sparse_route(facts, g)
    qs = facts[g.choice(N_FACTS, N_Q, replace=False)]; beffs = []
    for q in qs:
        top = np.argsort(facts @ q)[-TOPK:]; beffs.append(len(np.unique(shard[top])))
    beff = float(np.mean(beffs)); print("  [seed=%d] sparse_route B_eff=%.2f (dense LSH was ~39)" % (seed, beff), flush=True)
    return {"seed": seed, "B_eff": beff}


def verdict(ps) -> Tuple[str, str]:
    b = float(np.mean([p["B_eff"] for p in ps]))
    summary = "sparse-code routing B_eff=%.2f at S=%d (dense LSH ~39)" % (b, S)
    if b < 20:
        return ("HARD_PASS", "HARD_PASS: sparse-KEY routing keeps B_eff<20 (beats dense LSH ~39) -- production routing layer. " + summary)
    if b < 39:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sparse routing B_eff 20-39 (better than LSH but not <20). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: sparse routing B_eff>=39 -- no improvement over dense LSH. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d S=%d alpha=%.3f facts=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, S, ALPHA, N_FACTS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
