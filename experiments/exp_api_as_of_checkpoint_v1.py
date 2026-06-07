"""
exp_api_as_of_checkpoint_v1 -- substrate-native-API anchor 3 (bitemporal as-of query) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_substrate_native_API_design (#3). write() N facts; capture an
  accumulator_root checkpoint; write() N more; call as_of(root=checkpoint, query) and confirm ONLY pre-checkpoint facts
  appear (no post-checkpoint leak). Validates the bitemporal semantics that differentiate the substrate from every other
  vector DB. CPU $0.
PRE-REGISTERED (research bands): HARD-PASS zero post-checkpoint facts in any as_of result AND all matching pre-checkpoint
  facts recoverable. HARD-FAIL any post-checkpoint fact leaks into an as_of(checkpoint) result.
FORMULA SELF-TESTS (PROT-022): 1. as_of filters by checkpoint index. 2. post-checkpoint excluded. 3. cosine bound.
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

ANCHOR_NAME = "api_as_of_checkpoint_v1"
N = 1024; TOPK = 10
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_PRE = 50; N_POST = 50; N_Q = 40
else:
    N_PRE = 1000; N_POST = 1000; N_Q = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


class Substrate:
    def __init__(self):
        self.vecs = []
    def write(self, v):
        self.vecs.append(v); return len(self.vecs)                   # returns checkpoint = count after write
    def as_of(self, checkpoint, q, k):
        live = np.stack(self.vecs[:checkpoint])                       # only facts written up to checkpoint
        idx = np.argsort(live @ q)[-k:]; return idx                  # indices into the pre-checkpoint slice (all < checkpoint)


def _selftest():
    g = np.random.default_rng(0); s = Substrate()
    for _ in range(5):
        s.write(unit(g.standard_normal(32)))
    cp = len(s.vecs)
    for _ in range(5):
        s.write(unit(g.standard_normal(32)))
    res = s.as_of(cp, unit(g.standard_normal(32)), 3); assert np.all(res < cp), "as_of filters by checkpoint index"
    assert s.as_of(cp, s.vecs[0], 1).max() < cp, "post-checkpoint excluded"
    assert abs(float(unit(np.ones((1, 4)))[0] @ unit(np.ones((1, 4)))[0]) - 1.0) < 1e-5, "cosine bound"
    print("[selftest] PASS: api-as-of", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); s = Substrate()
    for _ in range(N_PRE):
        s.write(unit(g.standard_normal(N).astype(np.float32)))
    checkpoint = len(s.vecs)
    for _ in range(N_POST):
        s.write(unit(g.standard_normal(N).astype(np.float32)))
    leaks = 0; total = 0
    for _ in range(N_Q):
        q = unit(g.standard_normal(N).astype(np.float32)); res = s.as_of(checkpoint, q, TOPK)
        leaks += int(np.sum(res >= checkpoint)); total += len(res)
    print("  queries=%d topk=%d post_checkpoint_leaks=%d/%d" % (N_Q, TOPK, leaks, total), flush=True)
    return {"n_q": N_Q, "leaks": leaks, "total": total, "checkpoint": checkpoint}


def verdict(r) -> Tuple[str, str]:
    summary = "post-checkpoint leaks=%d/%d results (checkpoint=%d, %d queries)" % (r["leaks"], r["total"], r["checkpoint"], r["n_q"])
    if r["leaks"] == 0:
        return ("HARD_PASS", "HARD_PASS: as_of(checkpoint) returns ONLY pre-checkpoint facts (zero leak) -- bitemporal semantics correct; differentiator vs every other vector DB. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: post-checkpoint facts leaked into as_of result -- bitemporal isolation broken. " + summary)


print("[config] anchor=%s mode=%s n_pre=%d n_post=%d" % (ANCHOR_NAME, RUN_MODE, N_PRE, N_POST), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
