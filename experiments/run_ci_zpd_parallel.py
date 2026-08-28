"""experiments/run_ci_zpd_parallel.py -- parallel launcher for exp_reading_comprehensible_input_zpd_v1.

The 6 arms x 3 seeds = 18 (arm,seed) units are INDEPENDENT (each is its own sequential adaptive
reading simulation).  Within a unit the sentences are strictly sequential and each step is Python
control-flow over tiny 2048-dim ops -- not a GPU workload -- so the only real speedup axis is running
the 18 units concurrently across CPU cores.  This launcher does exactly that: one subprocess per
(arm,seed) writing to its OWN tag dir (no units.jsonl contention), a concurrency cap, then a merge +
register-controlled verdict over all units.  ~1.5h sequential -> ~one-unit wall time.

Run: .venv/Scripts/python.exe experiments/run_ci_zpd_parallel.py --budget 6000 --seeds 0,1,2 [--jobs 14]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Dict, List

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_reading_comprehensible_input_zpd_v1 import (
    ANCHOR_NAME, ARMS, N_BOOT_FULL, build_register_context, build_verdict, coverage_block)

PY = os.path.join(REPO_ROOT, ".venv", "Scripts", "python.exe")
CELL = os.path.join(REPO_ROOT, "experiments", "exp_reading_comprehensible_input_zpd_v1.py")


def _unit_dir(arm: str, seed: int) -> str:
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_par_{arm}_s{seed}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=6000)
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--jobs", type=int, default=min(14, (os.cpu_count() or 4) - 2))
    ap.add_argument("--out-tag", default="parallel")
    args = ap.parse_args()
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    units = [(a, s) for a in ARMS for s in seeds]
    print(f"[parallel] {len(units)} units across {args.jobs} workers, budget={args.budget}", flush=True)

    t0 = time.time()
    running: Dict[tuple, subprocess.Popen] = {}
    pending = list(units)
    done: List[tuple] = []
    logs: Dict[tuple, str] = {}

    def launch(unit):
        arm, seed = unit
        tag = f"par_{arm}_s{seed}"
        logp = os.path.join(REPO_ROOT, "data", f"_ci_{tag}.log")
        logs[unit] = logp
        env = dict(os.environ)
        f = open(logp, "w")
        p = subprocess.Popen([PY, CELL, "--mode", "full", "--budget", str(args.budget),
                              "--arms", arm, "--seeds", str(seed), "--tag", tag],
                             cwd=REPO_ROOT, stdout=f, stderr=subprocess.STDOUT, env=env)
        p._logfile = f  # type: ignore
        running[unit] = p

    while pending or running:
        while pending and len(running) < args.jobs:
            launch(pending.pop(0))
        time.sleep(2)
        for unit, p in list(running.items()):
            if p.poll() is not None:
                p._logfile.close()  # type: ignore
                done.append(unit)
                del running[unit]
                print(f"[parallel] finished {unit} rc={p.returncode} "
                      f"({len(done)}/{len(units)}) t={time.time()-t0:.0f}s", flush=True)

    # ---- merge all units + register-controlled verdict
    ctx = build_register_context("full")
    per: Dict[str, list] = {a: [] for a in ARMS}
    missing = []
    for arm, seed in units:
        up = os.path.join(_unit_dir(arm, seed), "units.jsonl")
        if not os.path.exists(up):
            missing.append((arm, seed)); continue
        with open(up, encoding="utf-8") as fh:
            rows = [json.loads(ln) for ln in fh if ln.strip()]
        if rows:
            per[arm].append(rows[-1])
    if missing:
        print(f"[parallel] WARNING missing units: {missing}", flush=True)

    verdict = build_verdict(ctx, per, N_BOOT_FULL)
    # per-arm register-controlled coverage table
    table = {}
    for a in ARMS:
        cvs = [coverage_block(ctx, r["grounded_subjects"])["register_controlled_coverage"] for r in per[a]]
        gr = [r["n_grounded"] for r in per[a]]
        table[a] = {"rc_cov_by_seed": [round(c, 6) for c in cvs],
                    "rc_cov_mean": round(sum(cvs) / len(cvs), 6) if cvs else None,
                    "grounded_by_seed": gr, "n_seeds": len(cvs)}
    out = {"anchor_name": ANCHOR_NAME + "_" + args.out_tag, "verdict": verdict["verdict"],
           "verdict_msg": verdict["verdict_msg"], "checks": verdict.get("checks"),
           "per_arm_summary": table, "budget": args.budget, "seeds": seeds,
           "n_units": len(units), "n_missing": len(missing), "wall_s": round(time.time() - t0, 1),
           "register_context": {"n_probe": len(ctx["probe"]), "n_reachable": len(ctx["reachable"]),
                                "n_unreachable": len(ctx["unreachable"])},
           "per_arm_units": {a: per[a] for a in ARMS}}
    outdir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_{args.out_tag}")
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(outdir, "metrics.json"))
    print(json.dumps({"verdict": out["verdict"], "verdict_msg": out["verdict_msg"],
                      "wall_s": out["wall_s"], "table": table}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
