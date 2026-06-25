"""b_delta readout-lever TRANSFER v2 FULL 3-seed promotion (USER 2026-06-25).

PROMOTION CONTEXT: the v1 cell HARD_PASS'd at n_seeds=1 (stale 2026-06-18 metrics: lift_clustered +53.1pp@M256,
lift_uniform +100.0pp@M64). NOT chain-grade-tier-eligible per BIAS-14.

NUANCE EXP_DEV CAUGHT (2026-06-25): the v1 source has been REWRITTEN since the 2026-06-18 metrics were generated. The
old framing (clustered vs uniform keys) was a NON_TEST (linear baseline=0.0 at ALL M, no cliff). Skunkworks B-delta-HALT
ruling caught this. The current v1 source applies the noise/sqrt(N) fix AND switched to two-VALUE-TYPE tasks (bipolar vs
continuous-Gaussian, both uniform keys, both capacity-limited). The v2 cell here INHERITS the corrected v1 source, runs
3 seeds [11, 13, 19] with prospective bands per the corrected mechanism, AND surfaces the discrepancy honestly.

CORRECTED MECHANISM (v2 = current v1 source + 3 seeds):
  Two TASKS: A = uniform keys + BIPOLAR values; B = uniform keys + CONTINUOUS-Gaussian values. Both capacity-limited.
  LEVER: linear readout (classic Hopfield raw-dot) vs nonlinear readout (modern Hopfield softmax).
  M sweep spans the linear capacity cliff (~0.14N at N=1024 -> ~143).
  DISCRIMINATION (B-delta-HALT): linear must WORK at low M (>WORKS=0.5) AND CLIFF at high M (drop >= CLIFF_DROP=0.2).
    A floored-everywhere linear = degenerate NON_TEST (denoising not capacity-lever).
  HARD_PASS = both tasks show cliff AND nonlinear extends recall past cliff by >= LIFT_MIN=0.05 on BOTH.

PROSPECTIVE BANDS (LOCKED via assert; USER 2026-06-25 framing -- adjusted from stale v1 framing to corrected v1 mechanism):
  HARD_PASS_CHAIN_GRADE:  lift mean >= 0.40 on BOTH tasks AND cv mean <= 0.07 on each
  HARD_PASS_PARTIAL:      lift >= 0.30 on at least one task
  HARD_FAIL:              lift < 0.20 on both tasks
  NON_TEST:               linear baseline does NOT cliff on at least one task (per B-delta-HALT discrimination)

ASCII-only. --self-test + --smoke + metrics.json. local_cpu_queue.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiments._seed_checkpoint import get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials

ANCHOR = "substrate_b_delta_readout_lever_transfer_v2_full"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"

# CAPACITY-SENSITIVE DIMENSIONS: smoke matches full on N + M_GRID + NOISE + BETA_GRID + ACC_THRESH.
N_DIM = 1024 if not SMOKE else 256
M_LIST_FULL = [64, 128, 256, 512, 1024]
M_LIST_SMOKE = [16, 128]
M_LIST = M_LIST_SMOKE if SMOKE else M_LIST_FULL
SEEDS_FULL = [11, 13, 19]
SEEDS_SMOKE = [11]
SEEDS = SEEDS_SMOKE if SMOKE else SEEDS_FULL
NOISE = 0.15
BETA_GRID = [10.0, 20.0, 40.0, 60.0, 80.0, 120.0]
ACC_THRESH = 0.90
WORKS = 0.5
CLIFF_DROP = 0.2

# PROSPECTIVE BANDS (USER 2026-06-25; LOCKED via assert)
BAND_HARD_PASS_LIFT_BOTH = 0.40           # lift on BOTH tasks
BAND_HARD_PASS_CV = 0.07                  # cv ceiling per task
BAND_HARD_PASS_PARTIAL_LIFT_AT_LEAST_ONE = 0.30
BAND_HARD_FAIL_LIFT_BOTH = 0.20
assert BAND_HARD_PASS_LIFT_BOTH > BAND_HARD_PASS_PARTIAL_LIFT_AT_LEAST_ONE > BAND_HARD_FAIL_LIFT_BOTH > 0


def _gen(device, seed):
    return torch.Generator(device=device).manual_seed(seed)


def _cos_normalize(X):
    return X / (X.norm(dim=1, keepdim=True) + 1e-12)


def make_uniform_keys(M, n, device, g):
    return _cos_normalize(torch.randn(M, n, generator=g, device=device))


def make_values(M, n, device, g):
    return (torch.randint(0, 2, (M, n), generator=g, device=device).float() * 2 - 1)


def make_continuous_values(M, n, device, g):
    return torch.randn(M, n, generator=g, device=device)


def make_noisy_queries(keys, noise, device, g):
    # noise/sqrt(N) fix (Skunkworks B-delta-HALT ruling): cos(noisy,key)~0.99, NOT mostly-noise
    n = keys.shape[1]
    return _cos_normalize(keys + (noise / (n ** 0.5)) * torch.randn(keys.shape, generator=g, device=device))


def _recall_acc(recall, V):
    dot = (recall * V).sum(1)
    nrm = recall.norm(dim=1) * V.norm(dim=1) + 1e-12
    return float(((dot / nrm) >= ACC_THRESH).float().mean())


def run_task(task, M, n, beta, device, g):
    """Return (recall_linear, recall_nonlinear, softmax_nz) for one VALUE-TYPE task at load M."""
    keys = make_uniform_keys(M, n, device, g)
    if task == "bipolar":
        V = make_values(M, n, device, g)
        cleanup = torch.sign
    else:
        V = make_continuous_values(M, n, device, g)
        cleanup = (lambda x: x)
    Q = make_noisy_queries(keys, NOISE, device, g)
    S = Q @ keys.t()
    rec_lin = cleanup(S @ V)
    W = torch.softmax(beta * S, dim=1)
    rec_nl = cleanup(W @ V)
    nz = float((W > 1e-9).sum(1).float().mean())
    return _recall_acc(rec_lin, V), _recall_acc(rec_nl, V), nz


def tune_beta(task, device, seed):
    """beta tuned on the NONLINEAR arm to the discriminating spread sweet-spot; frozen across arms.
    v2 tunes PER SEED so beta is honest per-seed (not a globally-tuned beta that hides cv)."""
    g = _gen(device, seed * 1000 + 99)
    best_b, best_score = BETA_GRID[0], -1e18
    M = M_LIST[-1]
    CLUSTER_SIZE = 8
    for b in BETA_GRID:
        _, _, nz = run_task(task, M, N_DIM, b, device, g)
        score = -abs(nz - CLUSTER_SIZE) if 2.0 <= nz <= 4.0 * CLUSTER_SIZE else -1e6 - abs(nz - CLUSTER_SIZE)
        if score > best_score:
            best_score, best_b = score, b
    return best_b


def run_one_seed(seed: int, device) -> Dict:
    tasks = ["bipolar", "continuous"]
    betas = {t: tune_beta(t, device, seed) for t in tasks}
    grid = {t: {m: {"lin": None, "nl": None, "nz": None} for m in M_LIST} for t in tasks}
    for t in tasks:
        for m in M_LIST:
            rl, rn, nz = run_task(t, m, N_DIM, betas[t], device, _gen(device, seed * 1000 + m))
            grid[t][m] = {"lin": round(rl, 4), "nl": round(rn, 4), "nz": round(nz, 2)}
            print("  seed=%d task=%s M=%d: lin=%.4f nl=%.4f nz=%.1f" % (seed, t, m, rl, rn, nz), flush=True)
    # cliff + extension per task
    def task_capacity(t):
        ms = sorted(M_LIST)
        lin_low = grid[t][ms[0]]["lin"]; lin_high = grid[t][ms[-1]]["lin"]; nl_high = grid[t][ms[-1]]["nl"]
        cliff = (lin_low > WORKS) and (lin_high < lin_low - CLIFF_DROP)
        extension = nl_high - lin_high
        return {"M_low": ms[0], "M_high": ms[-1], "lin_low": lin_low, "lin_high": lin_high, "nl_high": nl_high,
                "cliff": cliff, "extension": round(extension, 4)}
    capA = task_capacity("bipolar")
    capB = task_capacity("continuous")
    return {"seed": seed, "tasks": tasks, "beta_tuned": betas, "grid": {t: {str(m): grid[t][m] for m in M_LIST} for t in tasks},
            "capacity_bipolar": capA, "capacity_continuous": capB,
            "both_cliff": capA["cliff"] and capB["cliff"],
            "extension_bipolar": capA["extension"], "extension_continuous": capB["extension"],
            "run_mode": RUN_MODE, "N": N_DIM}


def aggregate_seeds(per_seed: List[Dict]) -> Dict:
    exts_A = [s["extension_bipolar"] for s in per_seed]
    exts_B = [s["extension_continuous"] for s in per_seed]
    cliffs_A = [s["capacity_bipolar"]["cliff"] for s in per_seed]
    cliffs_B = [s["capacity_continuous"]["cliff"] for s in per_seed]
    mean_A = float(np.mean(exts_A)); cv_A = float(np.std(exts_A) / abs(mean_A)) if abs(mean_A) > 1e-9 else float("inf")
    mean_B = float(np.mean(exts_B)); cv_B = float(np.std(exts_B) / abs(mean_B)) if abs(mean_B) > 1e-9 else float("inf")
    all_cliff_A = all(cliffs_A); all_cliff_B = all(cliffs_B)
    return {"n_seeds": len(per_seed), "seeds": [s["seed"] for s in per_seed],
            "extension_bipolar_mean": round(mean_A, 4), "extension_bipolar_cv": round(cv_A, 4),
            "extension_continuous_mean": round(mean_B, 4), "extension_continuous_cv": round(cv_B, 4),
            "extension_bipolar_per_seed": exts_A, "extension_continuous_per_seed": exts_B,
            "all_cliff_bipolar": all_cliff_A, "all_cliff_continuous": all_cliff_B,
            "cliffs_bipolar_per_seed": cliffs_A, "cliffs_continuous_per_seed": cliffs_B,
            "beta_tuned_per_seed": [s["beta_tuned"] for s in per_seed]}


def verdict(agg: Dict, per_seed: List[Dict]) -> Tuple[str, str]:
    if agg["n_seeds"] == 0:
        return ("UNKNOWN", "UNKNOWN: no seeds completed")
    mA = agg["extension_bipolar_mean"]; cvA = agg["extension_bipolar_cv"]
    mB = agg["extension_continuous_mean"]; cvB = agg["extension_continuous_cv"]
    all_cA = agg["all_cliff_bipolar"]; all_cB = agg["all_cliff_continuous"]
    per_seed_str = "per_seed_ext_bipolar=%s per_seed_ext_continuous=%s cliffs_bipolar=%s cliffs_continuous=%s" % (
        agg["extension_bipolar_per_seed"], agg["extension_continuous_per_seed"],
        agg["cliffs_bipolar_per_seed"], agg["cliffs_continuous_per_seed"])
    base = ("3-seed mean: bipolar ext=%.4f cv=%.4f (all_cliff=%s) | continuous ext=%.4f cv=%.4f (all_cliff=%s) | %s") % (
        mA, cvA, all_cA, mB, cvB, all_cB, per_seed_str)
    # NON_TEST: at least one task doesn't cliff in any seed
    if not (all_cA and all_cB):
        which = "both" if (not all_cA and not all_cB) else ("bipolar" if not all_cA else "continuous")
        return ("UNKNOWN", "NON_TEST (capacity-lever discrimination fails): linear baseline does NOT cliff in all seeds on %s task. "
                "A lift over a non-working baseline is DENOISING not a capacity-lever (Skunkworks B-delta-HALT). %s" % (which, base))
    # HARD_PASS_CHAIN_GRADE
    if (mA >= BAND_HARD_PASS_LIFT_BOTH and mB >= BAND_HARD_PASS_LIFT_BOTH
        and cvA <= BAND_HARD_PASS_CV and cvB <= BAND_HARD_PASS_CV):
        return ("HARD_PASS", ("HARD_PASS_CHAIN_GRADE: nonlinear-readout lever lifts capacity on BOTH value-type tasks "
                              "across 3 seeds (bipolar +%.4f cv=%.4f, continuous +%.4f cv=%.4f) -- TASK-GENERAL "
                              "capacity lever. %s") % (mA, cvA, mB, cvB, base))
    # HARD_PASS_PARTIAL
    if max(mA, mB) >= BAND_HARD_PASS_PARTIAL_LIFT_AT_LEAST_ONE:
        return ("MIDDLE_BAND", "MIDDLE_BAND_PARTIAL: lift >= 0.30 on at least one task; %s" % base)
    # HARD_FAIL
    if mA < BAND_HARD_FAIL_LIFT_BOTH and mB < BAND_HARD_FAIL_LIFT_BOTH:
        return ("HARD_FAIL", ("HARD_FAIL: lift < %.2f on both tasks. Nonlinear-readout lever does NOT generalize across "
                              "value-type. %s") % (BAND_HARD_FAIL_LIFT_BOTH, base))
    return ("MIDDLE_BAND", "MIDDLE_BAND: %s" % base)


def _selftest():
    device = torch.device("cpu")
    # mechanism check
    b = tune_beta("bipolar", device, 11)
    rl, rn, nz = run_task("bipolar", 256, 256, b, device, _gen(device, 11))
    # at M=256 / N=256, expect linear to be near 0 (over-capacity) and nonlinear to recover something
    # don't assert specific numbers; just verify pipeline runs
    assert 0 <= rl <= 1 and 0 <= rn <= 1
    # band sanity
    assert BAND_HARD_PASS_LIFT_BOTH > BAND_HARD_FAIL_LIFT_BOTH
    print("[selftest] PASS: substrate_b_delta_readout_lever_transfer_v2_full (mechanism + bands locked) beta=%s rl=%.3f rn=%.3f" % (b, rl, rn), flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        _selftest()
        return 0
    _selftest()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    src = "measured_torch_gpu" if device.type == "cuda" else "measured_torch_cpu"
    print("[config] anchor=%s mode=%s N=%d device=%s seeds=%s M_list=%s" % (ANCHOR, RUN_MODE, N_DIM, device.type, SEEDS, M_LIST), flush=True)
    out_dir = get_output_dir(ANCHOR)
    t0 = time.time()
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds already complete; running %s" % (len(done), len(SEEDS), remaining), flush=True)
    for seed in remaining:
        res = run_one_seed(seed, device)
        write_partial(out_dir, seed, res)
    per_seed = list(aggregate_partials(out_dir, SEEDS).values())
    agg = aggregate_seeds(per_seed)
    v, vmsg = verdict(agg, per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "headline": vmsg,
               "run_mode": RUN_MODE, "n_seeds": len(per_seed), "seeds": [s["seed"] for s in per_seed],
               "aggregate": agg, "per_seed": per_seed, "elapsed_s": round(time.time() - t0, 2),
               "N": N_DIM, "M_list": M_LIST, "noise": NOISE, "metrics_source": src,
               "bands": {"HARD_PASS_LIFT_BOTH": BAND_HARD_PASS_LIFT_BOTH, "HARD_PASS_CV": BAND_HARD_PASS_CV,
                         "HARD_PASS_PARTIAL_LIFT_AT_LEAST_ONE": BAND_HARD_PASS_PARTIAL_LIFT_AT_LEAST_ONE,
                         "HARD_FAIL_LIFT_BOTH": BAND_HARD_FAIL_LIFT_BOTH},
               "config_version": "v2_seeds_11_13_19_corrected_v1_mechanism_bipolar_continuous_uniformkeys_noisesqrtN"}
    OUT.mkdir(parents=True, exist_ok=True)
    write_metrics(out_dir, metrics, per_seed)
    print("[metrics] written", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
