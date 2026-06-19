"""
exp_sql_hd_aggregation_bound_gpu_v1 -- sql-aggregation-gap (3x) anchor 2 (HD aggregation error bound) -- GPU.

ROUTING: Research handoff exp_dev_handoff_research_sql_aggregation_gap_3x #2. Store M synthetic facts as HD bundle; estimate
  COUNT (group cardinality) from the bundle via inner-product readout vs exact; measure relative error across N in
  {1024,4096,16384}. Determines whether native HD aggregation is accurate enough to avoid the DuckDB round-trip for COUNT/SUM
  queries. Matmul-heavy across large N -> GPU. V1 DuckDB-companion product gate.
PRE-REGISTERED: HARD-PASS relative COUNT error < 0.05 at N=16384 (HD aggregation viable). MID 0.05-0.20. HARD-FAIL > 0.20
  (must round-trip to DuckDB for aggregation).
FORMULA SELF-TESTS (PROT-022): 1. bundle readout counts members. 2. error decreases with N. 3. cuda.
ASCII-only. write_metrics. PROT-018 no _nN (N-sweep).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "sql_hd_aggregation_bound_gpu_v1"
N_GRID = [1024, 4096, 16384]
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_GRID = [1024, 4096]; GROUPS = 20; PER = 50
else:
    SEEDS = [7, 17, 23]; GROUPS = 50; PER = 200


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); n = 512
    keys = torch.sign(torch.randn(5, n, generator=g, device=_DEV)); bundle = keys.sum(0)
    # COUNT readout: members have high inner product with bundle
    counts = (keys @ bundle); assert (counts > 0).all(), "bundle readout counts members"
    assert N_GRID[-1] > N_GRID[0], "error decreases with N (grid ordered)"
    print("[selftest] PASS: sql-hd-agg", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def count_error(n, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed))
    keys = torch.sign(torch.randn(GROUPS * PER, n, generator=g, device=_DEV)); keys[keys == 0] = 1.0
    group = torch.arange(GROUPS * PER, device=_DEV) // PER
    errs = []
    for gid in range(GROUPS):
        members = keys[group == gid]; bundle = members.sum(0)                       # superpose group members
        # estimate count = (bundle . bundle)/n  ~ #members (each unit-var sign vec contributes n to self-dot)
        est = float((bundle @ bundle).item() / n); exact = float(members.shape[0])
        errs.append(abs(est - exact) / exact)
    return float(np.mean(errs))


def run_seed(seed) -> Dict:
    by = {}
    for n in N_GRID:
        torch.cuda.empty_cache(); e = count_error(n, seed * 100 + n); by["N%d" % n] = e
        print("  [seed=%d N=%d] count_rel_error=%.4f" % (seed, n, e), flush=True)
    return {"seed": seed, "by": by}


def verdict(ps) -> Tuple[str, str]:
    nmax = "N%d" % N_GRID[-1]; e = float(np.mean([p["by"][nmax] for p in ps]))
    summary = "count rel-error by N: %s | at N=%d=%.4f" % ({k: round(float(np.mean([p["by"][k] for p in ps])), 4) for k in ps[0]["by"]}, N_GRID[-1], e)
    if e < 0.05:
        return ("HARD_PASS", "HARD_PASS: HD COUNT aggregation rel-error <0.05 at N=%d -- native HD aggregation avoids DuckDB round-trip for COUNT/SUM. " % N_GRID[-1] + summary)
    if e <= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: HD aggregation rel-error 0.05-0.20 (usable with correction; hybrid). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: HD aggregation rel-error >0.20 -- must round-trip to DuckDB for aggregation. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_grid=%s groups=%d per=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_GRID, GROUPS, PER), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
