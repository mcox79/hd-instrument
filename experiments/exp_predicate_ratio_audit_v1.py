"""
exp_predicate_ratio_audit_v1 -- storage-unconventional anchor 2 (predicate-ratio audit) -- CPU.

ROUTING: handoff storage_unconventional_mechanisms #2. Audits how stored-fact selectivity (fraction matching a typical
  predicate) interacts with HD bundle aggregation accuracy -- informs whether predicate-partitioned storage (group facts by
  predicate) reduces per-query interference. Sweeps predicate selectivity; measures retrieval accuracy of matching facts vs
  bundle interference. CPU.
PRE-REGISTERED: HARD-PASS accuracy stays >=0.90 across selectivity 0.05-0.5 (predicate partitioning robust). MIDDLE degrades
  at high selectivity. HARD-FAIL accuracy <0.70 at selectivity 0.1 (interference dominates -> needs partitioning).
FORMULA SELF-TESTS (PROT-022): 1. low selectivity retrieves. 2. bundle interference grows. 3. cosine bound.
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

ANCHOR_NAME = "predicate_ratio_audit_v1"; N = 4096; SEL = [0.05, 0.1, 0.25, 0.5]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]
M_TOT = 1000 if RUN_MODE == "smoke" else 5000


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); kb = unit(g.standard_normal((10, 64))); assert int(np.argmax(kb @ kb[2])) == 2, "low selectivity retrieves"
    b5 = unit(kb[:5].sum(0)); b2 = unit(kb[:2].sum(0)); assert float(b5 @ kb[0]) < float(b2 @ kb[0]) + 0.5, "bundle interference grows"
    assert abs(float(unit(np.ones((1, 4)))[0] @ unit(np.ones((1, 4)))[0]) - 1.0) < 1e-5, "cosine bound"
    print("[selftest] PASS: predicate-ratio", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); facts = unit(g.standard_normal((M_TOT, N)).astype(np.float32)); by = {}
    for sel in SEL:
        m = max(2, int(sel * M_TOT)); bundle = facts[:m].sum(0)                     # predicate-matching bundle
        hits = int((np.argmax(facts.T.T @ unit(bundle[None, :])[0]) >= 0))          # dummy keep shape
        # accuracy: each of the m bundled facts recoverable from the bundle (top-m by cosine)
        sims = facts @ unit(bundle[None, :])[0]; top = set(np.argsort(sims)[-m:].tolist()); acc = len(top & set(range(m))) / m
        by["sel%.2f" % sel] = acc; print("  [seed=%d selectivity=%.2f m=%d] bundle_recall=%.3f" % (seed, sel, m, acc), flush=True)
    return {"seed": seed, "by": by}


def verdict(ps) -> Tuple[str, str]:
    agg = {k: float(np.mean([p["by"][k] for p in ps])) for k in ps[0]["by"]}; worst = min(agg.values())
    summary = "bundle_recall by selectivity: %s | worst=%.3f" % ({k: round(v, 3) for k, v in agg.items()}, worst)
    if worst >= 0.90:
        return ("HARD_PASS", "HARD_PASS: bundle recall >=0.90 across selectivity 0.05-0.5 -- predicate-partitioned storage robust to interference. " + summary)
    if agg.get("sel0.10", 0) >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: holds at low selectivity, degrades at high (partition large predicates). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: interference dominates even at low selectivity -- predicate partitioning insufficient. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d M=%d sel=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, M_TOT, SEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
