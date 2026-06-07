"""
exp_sql_rolling_window_v1 -- sql-aggregation anchor 4 (rolling-window aggregation drift) -- CPU.

ROUTING: handoff sql_aggregation_gap_3x #4. A rolling-window COUNT/SUM over a streaming HD bundle must stay accurate as old
  items are unbundled (subtracted) and new ones added. Measures relative error of a rolling-window HD count vs exact as the
  window slides over a stream (tests accumulation drift from repeated add/subtract). CPU.
PRE-REGISTERED: HARD-PASS rolling rel-error < 0.05 after a full stream pass (no drift). MIDDLE 0.05-0.20. HARD-FAIL >0.20
  (add/subtract drift accumulates -> needs periodic rebuild).
FORMULA SELF-TESTS (PROT-022): 1. add then subtract restores. 2. count readout. 3. window size.
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

ANCHOR_NAME = "sql_rolling_window_v1"; N = 4096; WIN = 100
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]
STREAM = 500 if RUN_MODE == "smoke" else 5000


def _selftest():
    g = np.random.default_rng(0); v = g.standard_normal(64).astype(np.float32); b = np.zeros(64, np.float32)
    b = b + v; b = b - v; assert np.allclose(b, 0, atol=1e-5), "add then subtract restores"
    bundle = np.stack([g.standard_normal(64) for _ in range(5)]).sum(0); assert abs((bundle @ bundle) / 64 - 5) < 5, "count readout"
    assert WIN > 0, "window size"
    print("[selftest] PASS: sql-rolling", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); items = (g.integers(0, 2, (STREAM, N)) * 2 - 1).astype(np.float32)
    bundle = np.zeros(N, np.float32); errs = []
    for t in range(STREAM):
        bundle = bundle + items[t]
        if t >= WIN:
            bundle = bundle - items[t - WIN]                                   # slide window (unbundle oldest)
        if t >= WIN:
            est = float((bundle @ bundle) / N); exact = float(WIN); errs.append(abs(est - exact) / exact)
    re = float(np.mean(errs[-100:]))                                            # steady-state error
    print("  [seed=%d] rolling_rel_error(steady)=%.4f (window=%d, stream=%d)" % (seed, re, WIN, STREAM), flush=True)
    return {"seed": seed, "rel_error": re}


def verdict(ps) -> Tuple[str, str]:
    e = float(np.mean([p["rel_error"] for p in ps]))
    summary = "rolling-window steady-state rel-error=%.4f (window=%d)" % (e, WIN)
    if e < 0.05:
        return ("HARD_PASS", "HARD_PASS: rolling-window HD aggregation rel-error <0.05 after full stream -- no add/subtract drift; native streaming aggregation viable. " + summary)
    if e <= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: rolling rel-error 0.05-0.20 (periodic rebuild advisable). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: rolling rel-error >0.20 -- add/subtract drift accumulates. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d window=%d stream=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, WIN, STREAM), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
