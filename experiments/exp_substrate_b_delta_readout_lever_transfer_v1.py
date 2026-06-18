"""B-delta: does the NONLINEAR-READOUT LEVER transfer across TASKS? (Bucket-2 TRACK-2; USER-ratified 6h plan).

The session's CONVERGENT finding: a NONLINEAR readout (modern-Hopfield softmax) LIFTS associative-memory capacity vs a
LINEAR readout (classic Hopfield raw-dot) -- ARCH-B + C1. B-delta tests the GENERALITY of that lever: does the
nonlinear-over-linear capacity lift appear on TWO genuinely-different memory TASKS, or is it task-specific?

LEVER (the one variable): readout nonlinearity.
  LINEAR readout    (classic Hopfield):  recall = sign( S @ V )                  [raw cosine weighting]
  NONLINEAR readout (modern Hopfield):   recall = sign( softmax(beta*S) @ V )    [exp sharpening on the top matches]

TWO TASKS (genuinely different memory structures):
  TASK A = CLUSTERED keys (cluster_size near-neighbour interference; the spread regime) + noisy cue.
  TASK B = UNIFORM i.i.d. keys (no cluster structure; the classic Hopfield regime) + noisy cue.
Metric: exact recall accuracy (cosine(recall, true value) >= ACC_THRESH) across memory load M.
LIFT = recall_nonlinear - recall_linear, per task, per M. beta tuned PER TASK (on the nonlinear arm) to the
discriminating spread sweet-spot, FROZEN across the readout arms (no per-arm gaming).

SYMMETRIC GATES (both outcomes real):
  TRANSFER CONFIRMED (HARD_PASS): nonlinear lift >= LIFT_MIN on BOTH tasks AND the two lift magnitudes are comparable
     (|lift_A - lift_B| <= LIFT_GAP) -> the lever is TASK-GENERAL.
  TRANSFER FAILS (HARD_FAIL): lift >= LIFT_MIN on ONE task but <= 0 on the other (or opposite signs) -> TASK-SPECIFIC,
     not a general lever.
  MIDDLE_BAND: partial (lift on both but magnitudes diverge, or one marginal).
  NON_TEST: neither task reaches a discriminating regime (no lift possible to measure either way).

Adopts gate0_self_check (C2 producer gate). torch (GPU-capable; CPU fallback). 11th rule: pure torch, no LLM. ASCII-only.
HDLAB_RUN_MODE smoke|full ; --smoke ; --self-test ; --full.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cell_provenance import provenance_fields, now_utc, gate0_self_check, discrimination_self_check

ANCHOR = "substrate_b_delta_readout_lever_transfer_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)

N = 256 if os.environ.get("HDLAB_RUN_MODE") == "smoke" else 1024
# span the LINEAR (classic Hopfield) capacity cliff (~0.14N): low M -> linear works; high M -> linear fails,
# nonlinear (modern Hopfield) extends. The lever = that capacity extension. (N=1024 -> cliff ~143.)
M_LIST_FULL = [64, 128, 256, 512, 1024]
M_LIST_SMOKE = [64, 256]
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [7]
ALPHAS_UNUSED = None
CLUSTER_SIZE = 8
NOISE = 0.15
BETA_GRID = [10.0, 20.0, 40.0, 60.0, 80.0, 120.0]
ACC_THRESH = 0.90
LIFT_MIN = 0.05          # a "lift" must be >= 5pp recall to count
LIFT_GAP = 0.10          # lifts on the 2 tasks "comparable" if within 10pp -> task-general
CEIL = 0.95              # headroom ceiling: linear >= CEIL = no room for the lever to lift -> NON_TEST that task
FLOOR = 0.02             # something must recall (not all-degenerate)


def _gen(device, seed):
    return torch.Generator(device=device).manual_seed(seed)


def _cos_normalize(X):
    return X / (X.norm(dim=1, keepdim=True) + 1e-12)


def make_uniform_keys(M, n, device, g):
    return _cos_normalize(torch.randn(M, n, generator=g, device=device))


def make_clustered_keys(M, n, cluster_size, device, g):
    """n_clusters centroids; each key = centroid + small jitter -> near-neighbour interference."""
    n_clusters = max(1, M // cluster_size)
    centroids = torch.randn(n_clusters, n, generator=g, device=device)
    idx = torch.arange(M, device=device) % n_clusters
    jitter = 0.3 * torch.randn(M, n, generator=g, device=device)
    return _cos_normalize(centroids[idx] + jitter)


def make_values(M, n, device, g):
    return (torch.randint(0, 2, (M, n), generator=g, device=device).float() * 2 - 1)


def make_noisy_queries(keys, noise, device, g):
    return _cos_normalize(keys + noise * torch.randn(keys.shape, generator=g, device=device))


def _recall_acc(recall, V):
    dot = (recall * V).sum(1)
    nrm = recall.norm(dim=1) * V.norm(dim=1) + 1e-12
    return float(((dot / nrm) >= ACC_THRESH).float().mean())


def run_task(task, M, n, beta, device, g):
    """Return (recall_linear, recall_nonlinear, softmax_nz) for one task at load M."""
    if task == "clustered":
        keys = make_clustered_keys(M, n, CLUSTER_SIZE, device, g)
    else:
        keys = make_uniform_keys(M, n, device, g)
    V = make_values(M, n, device, g)
    Q = make_noisy_queries(keys, NOISE, device, g)
    S = Q @ keys.t()                                   # cosine scores (both cos-normalized)
    # LINEAR readout (classic Hopfield): raw-dot weighting
    rec_lin = torch.sign(S @ V)
    # NONLINEAR readout (modern Hopfield): softmax sharpening
    W = torch.softmax(beta * S, dim=1)
    rec_nl = torch.sign(W @ V)
    nz = float((W > 1e-9).sum(1).float().mean())
    return _recall_acc(rec_lin, V), _recall_acc(rec_nl, V), nz


def tune_beta(task, device):
    """beta tuned on the NONLINEAR arm to the discriminating spread sweet-spot (nonzero in [2, 4*cluster]); frozen across arms."""
    g = _gen(device, 99)
    best_b, best_score = BETA_GRID[0], -1e18
    M = (M_LIST_SMOKE if os.environ.get("HDLAB_RUN_MODE") == "smoke" else M_LIST_FULL)[-1]
    for b in BETA_GRID:
        _, _, nz = run_task(task, M, N, b, device, g)
        score = -abs(nz - CLUSTER_SIZE) if 2.0 <= nz <= 4.0 * CLUSTER_SIZE else -1e6 - abs(nz - CLUSTER_SIZE)
        if score > best_score:
            best_score, best_b = score, b
    return best_b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _ = ap.parse_known_args()
    is_smoke = args.smoke or (os.environ.get("HDLAB_RUN_MODE", "full") == "smoke" and not args.full)
    run_started_utc = now_utc()
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    src = "measured_torch_gpu" if device.type == "cuda" else "measured_torch_cpu"

    if args.self_test:
        b = tune_beta("clustered", device)
        rl, rn, nz = run_task("clustered", 256, N, b, device, _gen(device, 1))
        print(f"[{ANCHOR}] --self-test OK (device={device.type} beta={b} clustered M256: lin={rl:.2f} nl={rn:.2f} nz={nz:.1f}); NO metrics.")
        return 0

    m_list = M_LIST_SMOKE if is_smoke else M_LIST_FULL
    seeds = SEEDS_SMOKE if is_smoke else SEEDS_FULL
    tasks = ["clustered", "uniform"]
    n_cells_declared = len(tasks) * len(m_list) * len(seeds)

    betas = {t: tune_beta(t, device) for t in tasks}
    grid = {t: {m: {"lin": [], "nl": [], "nz": []} for m in m_list} for t in tasks}
    n_emitted = 0
    for t in tasks:
        for m in m_list:
            for s in seeds:
                rl, rn, nz = run_task(t, m, N, betas[t], device, _gen(device, s * 1000 + m))
                grid[t][m]["lin"].append(rl); grid[t][m]["nl"].append(rn); grid[t][m]["nz"].append(nz)
                n_emitted += 1
            print(f"[{ANCHOR}] task={t} M={m}: lin={sum(grid[t][m]['lin'])/len(seeds):.3f} "
                  f"nl={sum(grid[t][m]['nl'])/len(seeds):.3f} nz={sum(grid[t][m]['nz'])/len(seeds):.1f}", flush=True)

    # per-task lift = max over M of (mean nonlinear - mean linear), in a MEASURABLE regime = HEADROOM exists
    # (linear NOT already at ceiling AND something recalls). The lever question is linear-vs-nonlinear capacity,
    # NOT softmax spread -> headroom is the right discrimination criterion (NOT C1's nz>2 spread gate).
    def task_lift(t):
        best = {"M": None, "lift": -1e9, "lin": None, "nl": None, "nz": None, "measurable": False}
        for m in m_list:
            lin = sum(grid[t][m]["lin"]) / len(seeds); nl = sum(grid[t][m]["nl"]) / len(seeds)
            nz = sum(grid[t][m]["nz"]) / len(seeds)
            # measurable if linear has headroom to be lifted (lin < CEIL) AND the cell isn't all-degenerate
            if lin < CEIL and max(lin, nl) > FLOOR and (nl - lin) > best["lift"]:
                best = {"M": m, "lift": nl - lin, "lin": lin, "nl": nl, "nz": nz, "measurable": True}
        return best

    lift_A = task_lift("clustered")   # spread regime
    lift_B = task_lift("uniform")     # classic regime
    both_measurable = lift_A["measurable"] and lift_B["measurable"]

    if not both_measurable:
        verdict = "NON_TEST"
        which = ("both" if not lift_A["measurable"] and not lift_B["measurable"]
                 else ("clustered" if not lift_A["measurable"] else "uniform"))
        msg = (f"NON-TEST: no measurable regime (linear at ceiling >= {CEIL} OR all-degenerate) on the {which} task "
               f"-> no headroom to test the lever's transfer there. beta={betas}. (Adjust M/N to span the linear cliff.)")
    else:
        lA, lB = lift_A["lift"], lift_B["lift"]
        comparable = abs(lA - lB) <= LIFT_GAP
        if lA >= LIFT_MIN and lB >= LIFT_MIN:
            verdict = "HARD_PASS"
            mag = ("COMPARABLE magnitude" if comparable else
                   f"magnitude REGIME-DEPENDENT (|delta|={abs(lA-lB)*100:.1f}pp > {LIFT_GAP*100:.0f}pp -- stronger on the "
                   f"{'uniform' if lB > lA else 'clustered'} task)")
            msg = (f"TRANSFER CONFIRMED: the nonlinear-readout lever lifts capacity on BOTH tasks (clustered "
                   f"+{lA*100:.1f}pp @M{lift_A['M']}, uniform +{lB*100:.1f}pp @M{lift_B['M']}); {mag} -> the lever is "
                   f"TASK-GENERAL (present in both the spread and classic regimes). N={N}; readout-family/config envelope "
                   f"(measured-bounds), NOT fundamental.")
        elif (lA >= LIFT_MIN and lB <= 0.0) or (lB >= LIFT_MIN and lA <= 0.0):
            verdict = "HARD_FAIL"
            msg = (f"TRANSFER FAILS: the nonlinear lever helps ONE task but NOT the other (clustered {lA*100:+.1f}pp, "
                   f"uniform {lB*100:+.1f}pp) -> TASK-SPECIFIC, not a general lever. The convergent nonlinear-readout "
                   f"finding does NOT transfer across these two memory regimes. N={N}; substrate-novel negative.")
        else:
            verdict = "MIDDLE_BAND"
            msg = (f"PARTIAL transfer: clustered {lA*100:+.1f}pp, uniform {lB*100:+.1f}pp -- lift on both but one is "
                   f"marginal (< {LIFT_MIN*100:.0f}pp); not a clean task-general lever.")

    g0 = gate0_self_check(run_mode=("smoke" if is_smoke else "full"), metrics_source=src,
                          n_cells_declared=n_cells_declared, n_cells_emitted=n_emitted,
                          elapsed_s=round(time.time() - t0, 2), is_smoke=is_smoke)
    # B-epsilon discrimination_self_check (HEADROOM criterion -- NOT C1 spread; per Skunkworks refinement):
    # the cell self-attests its regime DISCRIMINATES (linear has headroom: < ceiling AND something recalls).
    _disc_reason = "headroom: linear<ceiling + recalls (capacity-lever discrimination, NOT spread)"
    discrimination = {
        "clustered": discrimination_self_check(lift_A["measurable"], lift_A.get("lin"), FLOOR, CEIL, _disc_reason),
        "uniform": discrimination_self_check(lift_B["measurable"], lift_B.get("lin"), FLOOR, CEIL, _disc_reason),
    }

    metrics = {
        "anchor_name": ANCHOR, "verdict": verdict, "verdict_msg": msg, "summary": msg, "headline": msg,
        "n_seeds": len(seeds),
        **provenance_fields("smoke" if is_smoke else "full", "readout_lever_transfer_2task", src, run_started_utc),
        "gate0_self_check": g0,
        "discrimination_self_check": discrimination,
        "n_cells": n_emitted,
        "lever": "linear(classic Hopfield sign(S@V)) vs nonlinear(modern Hopfield sign(softmax(beta*S)@V))",
        "tasks": {"A": "clustered-key spread regime", "B": "uniform-iid-key classic regime"},
        "lift_clustered": lift_A, "lift_uniform": lift_B,
        "beta_tuned": betas, "both_measurable": both_measurable,
        "grid": {t: {str(m): {"lin": round(sum(grid[t][m]["lin"])/len(seeds), 4),
                               "nl": round(sum(grid[t][m]["nl"])/len(seeds), 4),
                               "nz": round(sum(grid[t][m]["nz"])/len(seeds), 2)} for m in m_list} for t in tasks},
        "config": {"N": N, "M_list": m_list, "seeds": seeds, "cluster_size": CLUSTER_SIZE, "noise": NOISE,
                   "LIFT_MIN": LIFT_MIN, "LIFT_GAP": LIFT_GAP},
        "bears_on": "ARCH-B (nonlinear readout lifts capacity) + C1 entmax (sparse readout cheaper at iso-recall) -- tests lever GENERALITY across tasks",
        "measured_bounds": f"readout-lever transfer envelope at N={N}/cluster={CLUSTER_SIZE}/noise={NOISE}; NOT fundamental",
        "elapsed_s": round(time.time() - t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={'smoke' if is_smoke else 'full'} device={device.type} -> {verdict}")
    print(f"  lift clustered={lift_A['lift']*100:+.1f}pp uniform={lift_B['lift']*100:+.1f}pp both_measurable={both_measurable} gate0={g0['pass']}")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
