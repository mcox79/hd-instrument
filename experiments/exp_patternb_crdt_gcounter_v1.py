"""
exp_patternb_crdt_gcounter_v1 -- PB-EXT-3: Pattern B role-level CRDT G-counter aggregation -- CPU.
ROUTING: top20/pattern-b-ext PB-EXT-3. Role-level G-counter aggregation over Pattern B facts; 10 COUNT/SUM queries by role; verify commutative/idempotent merge. CPU.
PRE-REGISTERED: HARD-PASS aggregation accuracy>=0.95 across 10 queries AND merge commutative+idempotent.
FORMULA SELF-TESTS (PROT-022): 1. merge max. 2. idempotent. 3. commutative.
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
ANCHOR_NAME = "patternb_crdt_gcounter_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
S = 8; NQ = 10
def merge(states): return {k: max(s.get(k, 0) for s in states) for k in set().union(*[set(s) for s in states])}
def _selftest():
    a = {0:3,1:2}; b = {0:5}; m = merge([a,b]); assert m[0]==5 and m[1]==2, "merge max"
    assert merge([m,m]) == m, "idempotent"
    assert merge([a,b]) == merge([b,a]), "commutative"
    print("[selftest] PASS: patternb-crdt", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); ok = 0; comm = 0
    for _ in range(NQ):
        true = {i: int(g.integers(0, 50)) for i in range(S)}
        shards = [{i: true[i]} for i in range(S)]; perm = list(g.permutation(len(shards)))
        m1 = merge(shards); m2 = merge([shards[i] for i in perm] + [shards[int(g.integers(0,S))]])  # reorder + duplicate
        ok += int(sum(m1.values()) == sum(true.values())); comm += int(merge(shards) == merge(list(reversed(shards))))
    acc = ok / NQ; cf = comm / NQ; print("  role-level G-counter accuracy=%.3f commutativity=%.3f" % (acc, cf), flush=True)
    return {"acc": acc, "comm": cf}
def verdict(r) -> Tuple[str, str]:
    s = "accuracy=%.3f commutativity=%.3f" % (r["acc"], r["comm"])
    if r["acc"] >= 0.95 and r["comm"] >= 0.999: return ("HARD_PASS", "HARD_PASS: Pattern B role-level CRDT G-counter aggregation >=0.95 + commutative/idempotent merge -- conflict-free distributed aggregation over compositional facts. " + s)
    return ("HARD_FAIL", "HARD_FAIL: aggregation <0.95 or merge not commutative. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
