"""
exp_zkl_timing_immunity_v1 -- ZKL Certificate battery cell 4 (GOLD 3.0 timing-immunity claim) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_ZKL_Certificate_10h_battery cell 4. The substrate's timing-side-channel-
  immunity claim depends on query latency being data-INDEPENDENT (a member query and a non-member query take the same time,
  because retrieval is the same dense matmul regardless of membership). Measures per-query latency for 500 member + 500
  non-member queries, trains a classifier on latency alone, reports AUC. CPU.
PRE-REGISTERED (research bands): HARD-PASS AUC in [0.48,0.52] (indistinguishable from random). MID [0.52,0.60] (qualify w/
  hardware caveat). HARD-FAIL > 0.60 (timing is data-dependent; side-channel-immune claim breaks).
FORMULA SELF-TESTS (PROT-022): 1. AUC bounds. 2. identical dists -> AUC~0.5. 3. retrieval runs.
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

ANCHOR_NAME = "zkl_timing_immunity_v1"
N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_KB = 500; N_EACH = 80
else:
    N_KB = 4000; N_EACH = 500


def auc(scores, labels):
    scores = np.asarray(scores); labels = np.asarray(labels)
    pos = scores[labels == 1]; neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    r = np.argsort(np.argsort(np.concatenate([pos, neg]))); a = (r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg))
    return float(max(a, 1 - a))                                     # classifier can use either direction


def retrieve_latency(kb, q):
    t0 = time.perf_counter(); _ = (kb @ q).argmax(); return time.perf_counter() - t0


def _selftest():
    g = np.random.default_rng(0); x = g.standard_normal(200)
    assert 0.49 <= auc(x, (np.arange(200) % 2)) <= 0.65, "identical dists -> AUC~0.5"
    assert auc([1, 1, 0, 0], [1, 1, 0, 0]) == 1.0, "AUC bounds"
    kb = g.standard_normal((10, 32)).astype(np.float32); assert retrieve_latency(kb, g.standard_normal(32).astype(np.float32)) >= 0, "retrieval runs"
    print("[selftest] PASS: zkl-timing", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); kb = g.standard_normal((N_KB, N)).astype(np.float32)
    members = kb[g.choice(N_KB, N_EACH, replace=False)]                       # stored facts (member queries)
    nonmembers = g.standard_normal((N_EACH, N)).astype(np.float32)            # never stored
    for _ in range(50):                                                       # warmup (thermal/cache steady state)
        _ = retrieve_latency(kb, members[0])
    # INTERLEAVE member/non-member so any time-drift (thermal/cache) affects both labels equally (no order confound)
    order = [(members[i], 1) if j % 2 == 0 else (nonmembers[i], 0) for i in range(N_EACH) for j in range(2)]
    lat = []; lab = []
    for q, y in order:
        lat.append(retrieve_latency(kb, q)); lab.append(y)
    a = auc(lat, lab); lm = float(np.median(np.array(lat)[np.array(lab) == 1])); ln = float(np.median(np.array(lat)[np.array(lab) == 0]))
    print("  latency_AUC=%.4f median_member=%.2fus median_nonmember=%.2fus" % (a, lm * 1e6, ln * 1e6), flush=True)
    return {"latency_auc": a, "median_member_us": lm * 1e6, "median_nonmember_us": ln * 1e6, "n_each": N_EACH}


def verdict(r) -> Tuple[str, str]:
    a = r["latency_auc"]
    summary = "latency_AUC=%.4f (member med=%.2fus nonmember med=%.2fus, n=%d each)" % (a, r["median_member_us"], r["median_nonmember_us"], r["n_each"])
    if a <= 0.52:
        return ("HARD_PASS", "HARD_PASS: query latency is membership-independent (AUC<=0.52) -- timing side-channel immunity holds. " + summary)
    if a <= 0.60:
        return ("MIDDLE_BAND", "MIDDLE_BAND: AUC 0.52-0.60 -- timing partially data-dependent; qualify with hardware caveat. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: AUC>0.60 -- latency leaks membership; side-channel-immune claim breaks. " + summary)


print("[config] anchor=%s mode=%s N=%d n_kb=%d n_each=%d" % (ANCHOR_NAME, RUN_MODE, N, N_KB, N_EACH), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
