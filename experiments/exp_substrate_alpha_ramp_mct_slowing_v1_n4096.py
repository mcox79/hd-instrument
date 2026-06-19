"""
substrate_alpha_ramp_mct_slowing_v1_n4096 -- capacity degradation curve + MCT critical-slowing early-warning.

ROUTING: notes/exp_dev_handoff_research_cross_domain_interference_capacity_degradation_2026-06-04.md
  (anchor candidate 1: alpha-ramp graceful->catastrophic + MCT critical slowing). Per
  [[feedback-no-experiment-design-in-prompts]] exp_dev designed all parameters. CPU (numpy; N=4096).

CAPABILITY QUESTION:
  (a) Does the Hopfield-class auto-associative capacity curve show a GRACEFUL regime (retrieval acc > 95%
  below ~85% of alpha_c=0.138) and a CATASTROPHIC drop at alpha_c -> establishing M < 0.85*alpha_c*N as the
  product operational safety constant? (b) MCT: does the argmax/sign convergence step-count DIVERGE near
  alpha_c -- a FREE capacity early-warning signal (substrate self-reports approaching capacity via slowing)?

MODEL: bipolar patterns Xi (M, N); W = Xi^T Xi / N, diagonal zeroed. Recall = iterate x <- sign(W x) until
  fixed point (or MAX_ITERS); record (1) final overlap m = mean (xi . x_final)/N, (2) fraction with m>0.95,
  (3) convergence step count (MCT proxy). Sweep alpha = M/N across the graceful/critical/catastrophic zones.

ALPHA GRID (relative to alpha_c=0.138): {0.02,0.05,0.08,0.10,0.117(=0.85*ac),0.138(=ac),0.16,0.20}; N=4096; 3 seeds.

PRE-REGISTERED BANDS:
  HARD-PASS: GRACEFUL confirmed (frac_recalled > 0.95 at alpha <= 0.117) AND CATASTROPHIC drop (frac_recalled
    falls > 0.30 absolute between alpha=0.117 and alpha=0.16) AND MCT slowing (mean convergence steps at
    alpha>=0.138 > 1.5x steps at alpha<=0.08). -> operational safety constant + free early-warning both validated.
  MIDDLE: degradation curve present but MCT slowing < 1.5x (early-warning weak) OR catastrophic drop 0.15-0.30.
  HARD-FAIL: no graceful zone (frac_recalled < 0.95 even at alpha=0.05) OR monotone-smooth with no transition.

FORMULA SELF-TESTS (PROT-022):
  1. low-load (alpha=0.02) frac_recalled ~ 1.0. 2. classical alpha_c = 0.138. 3. convergence step >= 1.
  4. overlap in [-1,1].

PROT-018: anchor _n4096 -> N=4096. PROT-019: _n4096 timeout floor 14400s. PROT-021: per-seed partials.
QUEUE: remote_cpu_queue (numpy; N=4096 auto-assoc matmul + sign iteration; GPU not needed). ASCII-only.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, json, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_alpha_ramp_mct_slowing_v1_n4096"
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
ALPHA_GRID = [0.02, 0.05, 0.08, 0.10, 0.117, 0.138, 0.16, 0.20]
MAX_ITERS = 20
GRACEFUL_ALPHA = 0.117      # 0.85 * alpha_c
RECALL_THRESH = 0.95

if RUN_MODE == "smoke":
    N_DIM = 512; SEEDS = [1, 2]
else:
    N_DIM = N; SEEDS = [7, 17, 23]


def ramp_cell(n, M, gen) -> Tuple[float, float, float]:
    """Return (frac_recalled m>0.95, mean_final_overlap, mean_convergence_steps)."""
    Xi = (gen.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    W = (Xi.T @ Xi) / n
    np.fill_diagonal(W, 0.0)
    overlaps = np.zeros(M); steps = np.zeros(M)
    for i in range(M):
        x = Xi[i].copy()
        s = 0
        for s in range(1, MAX_ITERS + 1):
            xn = np.sign(W @ x); xn[xn == 0] = 1.0
            if np.array_equal(xn, x):
                break
            x = xn
        overlaps[i] = float((Xi[i] @ x) / n); steps[i] = s
    return float(np.mean(overlaps > RECALL_THRESH)), float(np.mean(overlaps)), float(np.mean(steps))


def _selftest():
    g = np.random.default_rng(0)
    fr, mo, st = ramp_cell(512, int(0.02 * 512), g)
    assert fr > 0.9, f"low-load frac {fr}"
    assert abs(ALPHA_C - 0.138) < 1e-6 and st >= 1.0 and -1.0 <= mo <= 1.0
    print(f"[selftest] PASS: low_load_frac={fr:.3f} mean_steps={st:.2f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = np.random.default_rng(seed)
    t0 = time.time(); cells = []
    for a in ALPHA_GRID:
        M = max(2, int(round(a * n_dim)))
        fr, mo, st = ramp_cell(n_dim, M, gen)
        cells.append({"alpha": a, "M": M, "frac_recalled": fr, "mean_overlap": mo, "mean_steps": st})
        print(f"  [seed={seed} alpha={a} M={M}] frac_recalled={fr:.3f} overlap={mo:.3f} steps={st:.2f}", flush=True)
    return {"seed": seed, "N": n_dim, "cells": cells, "elapsed_s": time.time() - t0}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "no results")
    def mean_at(a, key):
        vs = [c[key] for r in results for c in r["cells"] if abs(c["alpha"] - a) < 1e-6]
        return float(np.mean(vs)) if vs else float("nan")
    fr = {a: mean_at(a, "frac_recalled") for a in ALPHA_GRID}
    steps = {a: mean_at(a, "mean_steps") for a in ALPHA_GRID}
    graceful = all(fr[a] > RECALL_THRESH for a in ALPHA_GRID if a <= GRACEFUL_ALPHA)
    catastrophic_drop = fr[0.117] - fr[0.16]
    steps_low = float(np.mean([steps[a] for a in ALPHA_GRID if a <= 0.08]))
    steps_hi = float(np.mean([steps[a] for a in ALPHA_GRID if a >= 0.138]))
    mct_ratio = steps_hi / (steps_low + 1e-9)
    summary = ("frac_recalled=" + " ".join(f"a{a}:{fr[a]:.2f}" for a in ALPHA_GRID) +
               f" | catastrophic_drop={catastrophic_drop:.2f} mct_ratio={mct_ratio:.2f} (steps_low={steps_low:.2f} hi={steps_hi:.2f})")
    if fr[0.05] < RECALL_THRESH:
        return ("HARD_FAIL", f"HARD_FAIL: no graceful zone (frac<{RECALL_THRESH} at alpha=0.05). {summary}")
    if graceful and catastrophic_drop > 0.30 and mct_ratio > 1.5:
        return ("HARD_PASS", f"HARD_PASS: graceful zone (M<0.85 alpha_c) + catastrophic drop + MCT slowing>1.5x "
                             f"(free early-warning). {summary}")
    if catastrophic_drop > 0.15 or mct_ratio > 1.2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: degradation present, MCT slowing or drop sub-threshold. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: no clear transition. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_DIM} alpha_grid={ALPHA_GRID} mode={RUN_MODE} seeds={SEEDS}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "alpha_grid": ALPHA_GRID})
print(f"[ckpt] {len(done)} done, {len(remaining)} to run", flush=True)
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    write_partial(out_dir, seed, run_seed(seed, N_DIM))
per_seed = aggregate_partials(out_dir, SEEDS); all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg, "N": N_DIM,
           "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "alpha_grid": ALPHA_GRID,
           "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells"), "elapsed_s": r.get("elapsed_s")} for r in all_results]}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
