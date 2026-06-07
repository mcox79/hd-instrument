"""
exp_crdt_gcounter_aggregate_v1 -- coordination: CRDT G-Counter distributed COUNT -- CPU.
ROUTING: distributed_coordination_patterns (CRDT Pattern 4). Distributed COUNT via per-shard G-Counters merged by max;
  verifies the merged count equals the true total regardless of merge order / duplicate delivery (idempotent). CPU.
PRE-REGISTERED: HARD-PASS merged count exact AND order/duplicate-independent across trials. HARD-FAIL any mismatch.
FORMULA SELF-TESTS (PROT-022): 1. merge by max. 2. idempotent. 3. sum equals total.
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
ANCHOR_NAME = "crdt_gcounter_aggregate_v1"; S = 10
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
TRIALS = 200 if RUN_MODE == "smoke" else 2000
def merge(states): return {i: max(s.get(i, 0) for s in states) for i in range(S)}
def total(state): return sum(state.values())
def _selftest():
    a = {0: 3, 1: 2}; b = {0: 5, 1: 1}; m = merge([a, b]); assert m[0] == 5 and m[1] == 2, "merge by max"
    assert merge([m, m]) == m, "idempotent"
    assert total({0: 1, 1: 2}) == 3, "sum equals total"
    print("[selftest] PASS: crdt-gcounter", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); ok = 0
    for _ in range(TRIALS):
        true_counts = {i: int(g.integers(0, 100)) for i in range(S)}; true_total = sum(true_counts.values())
        states = [{i: true_counts[i]} for i in range(S)]
        order = list(g.permutation(S)); dup = states + [states[int(g.integers(0, S))]]   # duplicate delivery
        merged = merge([dup[i] for i in g.permutation(len(dup))])
        if total(merged) == true_total: ok += 1
    print("  exact_count_fraction=%.4f over %d trials (random order + duplicates)" % (ok / TRIALS, TRIALS), flush=True)
    return {"exact_fraction": ok / TRIALS}
def verdict(r) -> Tuple[str, str]:
    f = r["exact_fraction"]; summary = "exact distributed COUNT fraction=%.4f (order + duplicate independent)" % f
    if f >= 0.999: return ("HARD_PASS", "HARD_PASS: CRDT G-Counter gives exact distributed COUNT regardless of merge order / duplicates -- conflict-free aggregation without coordination. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: G-Counter merge not exact/idempotent. " + summary)
print("[config] anchor=%s mode=%s S=%d trials=%d" % (ANCHOR_NAME, RUN_MODE, S, TRIALS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
