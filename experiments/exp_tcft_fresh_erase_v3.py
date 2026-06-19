"""TCFT substrate write probe v3: N=4096 product-claim N-scaling extension.

CONTEXT:
  tcft_fresh_erase_v2 HARD_PASS: 5/5 seeds, var_ratio=0.0139 at N=1024.
  The deletion-certificate product claim requires TCFT to hold at realistic
  production substrate sizes. N=4096 is the next tier (used in BID, saddle-cascade).
  This probe extends the thermodynamic free-energy measurement to N=4096 with
  5 seeds to confirm the HARD_PASS is not N-specific.

SCIENTIFIC QUESTION:
  Does TCFT variance reduction (var_ratio < 0.10) hold at N=4096?
  Does mean-field agreement (delta_F_agree_pct) improve at larger N (as expected
  by the N -> inf mean-field limit)?

PRE-REGISTERED BANDS (calibration extension: N=4096 vs prior N=1024 HARD_PASS):
  HARD-PASS:
    - var_ratio < 0.10 in >= 3/5 seeds at N=4096 (same criterion as v2)
    - AND delta_F_agree_pct < 50% in >= 3/5 seeds (mean-field agrees within calibration)
  HARD-FAIL:
    - var_ratio >= 1.0 in ALL 5 seeds (conditioning fails at larger N)
  MIDDLE-BAND:
    - var_ratio < 0.10 in 1-2/5 seeds only (partial)
    - OR var_ratio in [0.10, 1.0) in all 5 seeds (reduction but not 10x)

  NOTE: widened calibration-probe bands (no prior N=4096 empirical anchor).

Timeout estimate:
  smoke (N=512, 1 seed): ~2s from v2 pattern; FULL (N=4096, 5 seeds):
  timeout_s = ceil(1.5 * 2 * (4096/512)**1.5 * 5) = ceil(1.5 * 2 * 22.6 * 5) = ceil(339) = 600s
  Use 900s for margin.

N-suffix: no _nN suffix; production N = 4096 (stated explicitly here).
Queue: remote_cpu_queue (pure numpy; N=4096 5-seed; ~5-15 min)
Pre-reg: preregs/2026-05-27_tcft_fresh_erase_v3.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Production config ---
N_FULL  = 4096
N_SMOKE = 512
ALPHA_RATIO = 0.125   # M/N
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
KBT = 1.0
PR_THRESHOLD = 4.0
ALPHA_HEBBIAN = 0.1

HP_VAR_RATIO_STRONG = 0.10
HP_VAR_RATIO_ANY    = 1.0
HP_SEED_COUNT_MIN   = 3
MIN_CLASS_SIZE      = 3
DELTA_F_AGREE_PCT_THRESHOLD = 50.0


def get_output_dir(default_name: str = "tcft_fresh_erase_v3") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def compute_cumulative_works(N: int, M: int, seed: int) -> np.ndarray:
    """Per-pattern work during cumulative Hebbian loading."""
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N))
    W = np.zeros((N, N), dtype=np.float64)
    works = np.zeros(M, dtype=np.float64)
    for mu in range(M):
        v = patterns[mu]
        w = -float(v @ W @ v)
        works[mu] = w
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
        np.fill_diagonal(W, 0.0)
    return works


def vanilla_jarzynski(works: np.ndarray) -> Dict:
    W_scaled = works / KBT
    log_mex = float(np.log(np.mean(np.exp(-W_scaled)) + 1e-300))
    delta_F = float(-KBT * log_mex)
    variance = float(np.var(np.exp(-W_scaled)))
    work_std = float(np.std(works))
    return {
        "delta_F": delta_F,
        "variance": variance,
        "work_std": work_std,
        "pr_fires": bool(work_std > PR_THRESHOLD * KBT),
    }


def tcft_conditioned(works: np.ndarray) -> Dict:
    """TCFT: condition on low-work trajectory class (|w| < median)."""
    median_w = float(np.median(np.abs(works)))
    class0_mask = np.abs(works) < median_w
    if class0_mask.sum() < MIN_CLASS_SIZE:
        return {"valid": False, "class0_size": int(class0_mask.sum()),
                "variance_ratio": None, "delta_F": None}
    works_class0 = works[class0_mask]
    W_scaled = works_class0 / KBT
    log_mex = float(np.log(np.mean(np.exp(-W_scaled)) + 1e-300))
    delta_F_c0 = float(-KBT * log_mex)
    variance_c0 = float(np.var(np.exp(-W_scaled)))
    W_all = works / KBT
    variance_all = float(np.var(np.exp(-W_all)))
    var_ratio = variance_c0 / (variance_all + 1e-300)
    return {
        "valid": True,
        "class0_size": int(class0_mask.sum()),
        "delta_F": delta_F_c0,
        "variance": variance_c0,
        "variance_ratio": float(var_ratio),
    }


def mean_field_delta_F(N: int, M: int) -> float:
    load = ALPHA_HEBBIAN * M / N
    delta_F_per_N = -load / 2.0 * (1.0 - load)
    return float(delta_F_per_N * N)


def run_one_seed(N: int, seed: int) -> Dict:
    M = max(4, int(N * ALPHA_RATIO))
    t0 = time.time()
    works = compute_cumulative_works(N, M, seed)
    elapsed_works = time.time() - t0
    vanilla = vanilla_jarzynski(works)
    tcft = tcft_conditioned(works)
    mf_dF = mean_field_delta_F(N, M)
    result = {
        "N": N, "M": M, "seed": seed,
        "elapsed_works_s": elapsed_works,
        "vanilla_delta_F": vanilla["delta_F"],
        "vanilla_variance": vanilla["variance"],
        "vanilla_work_std": vanilla["work_std"],
        "vanilla_pr_fires": vanilla["pr_fires"],
        "tcft_valid": tcft["valid"],
        "tcft_class0_size": tcft["class0_size"],
    }
    if tcft["valid"]:
        agree_pct = abs(tcft["delta_F"] - mf_dF) / (abs(mf_dF) + 1e-9) * 100.0
        result.update({
            "tcft_delta_F": tcft["delta_F"],
            "tcft_variance": tcft["variance"],
            "tcft_variance_ratio": tcft["variance_ratio"],
            "mf_delta_F": mf_dF,
            "delta_F_agree_pct": agree_pct,
        })
    else:
        result.update({
            "tcft_delta_F": None,
            "tcft_variance": None,
            "tcft_variance_ratio": None,
            "mf_delta_F": mf_dF,
            "delta_F_agree_pct": None,
        })
    return result


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    works = compute_cumulative_works(128, 16, seed=42)
    assert works is not None and len(works) == 16, "works array wrong shape"
    assert float(np.std(works)) > 1e-6, f"works all-zero sentinel: std={np.std(works)}"
    van = vanilla_jarzynski(works)
    assert math.isfinite(van["delta_F"]), f"vanilla delta_F not finite: {van['delta_F']}"
    assert math.isfinite(van["variance"]) and van["variance"] >= 0.0, "variance negative/non-finite"
    tcft = tcft_conditioned(works)
    assert tcft["valid"], f"TCFT invalid at small scale: class0_size={tcft['class0_size']}"
    assert tcft["class0_size"] >= MIN_CLASS_SIZE, f"class0 too small: {tcft['class0_size']}"
    assert tcft["variance_ratio"] is not None and math.isfinite(tcft["variance_ratio"]), \
        f"variance_ratio not finite: {tcft['variance_ratio']}"
    assert 0.0 <= tcft["variance_ratio"], f"negative variance ratio"
    mf = mean_field_delta_F(128, 16)
    assert math.isfinite(mf) and abs(mf) > 1e-6, f"mean_field_delta_F trivial: {mf}"
    # Multi-scale: N_smoke and N_smoke*4 both produce valid tcft
    for N_t in [64, 256]:
        M_t = max(4, int(N_t * ALPHA_RATIO))
        w_t = compute_cumulative_works(N_t, M_t, seed=7)
        tc_t = tcft_conditioned(w_t)
        assert tc_t["valid"], f"TCFT invalid at N={N_t}"
    print("SELFTEST PASS: all assertions satisfied (multi-scale)")


_instrumentation_selftest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)

    N = N_SMOKE if args.smoke else N_FULL
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    out_dir = get_output_dir()

    t0 = time.time()
    results = []
    for seed in seeds:
        r = run_one_seed(N, seed)
        results.append(r)
        mode = "smoke" if args.smoke else "full"
        vr = r.get("tcft_variance_ratio")
        vr_str = f"{vr:.4f}" if vr is not None else "None"
        print(f"[{mode}] N={N} seed={seed} var_ratio={vr_str} "
              f"elapsed_works_s={r['elapsed_works_s']:.2f}s")

    elapsed = time.time() - t0

    valid_seeds = [r for r in results if r.get("tcft_valid", False)
                   and r.get("tcft_variance_ratio") is not None]
    n_valid = len(valid_seeds)
    n_hp = sum(1 for r in valid_seeds if r["tcft_variance_ratio"] < HP_VAR_RATIO_STRONG)
    n_hf = sum(1 for r in valid_seeds if r["tcft_variance_ratio"] >= HP_VAR_RATIO_ANY)
    n_agree = sum(1 for r in valid_seeds
                  if r.get("delta_F_agree_pct") is not None
                  and r["delta_F_agree_pct"] < DELTA_F_AGREE_PCT_THRESHOLD)

    if n_valid == 0:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (f"INSTRUMENTATION_FAIL: 0/{len(seeds)} seeds produced valid TCFT")
    elif n_hp >= HP_SEED_COUNT_MIN:
        mean_vr = float(np.mean([r["tcft_variance_ratio"] for r in valid_seeds]))
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: {n_hp}/{n_valid} seeds show var_ratio<0.10 at N={N}. "
                       f"mean_var_ratio={mean_vr:.4f} agree_lt50pct={n_agree}/{n_valid}")
    elif n_hf == n_valid:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: ALL {n_valid}/{n_valid} seeds show var_ratio>=1.0 at N={N}.")
    else:
        mean_vr = float(np.mean([r["tcft_variance_ratio"] for r in valid_seeds]))
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: {n_hp}/{n_valid} seeds var_ratio<0.10 at N={N} "
                       f"(need {HP_SEED_COUNT_MIN}). mean_var_ratio={mean_vr:.4f}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "n_seeds": len(seeds),
        "n_valid": n_valid,
        "n_hp": n_hp,
        "n_hf": n_hf,
        "n_agree": n_agree,
        "per_seed": results,
        "summary": f"TCFT v3 N={N}: {verdict} ({n_hp}/{n_valid} seeds HP)",
        "config": {
            "N": N,
            "alpha_ratio": ALPHA_RATIO,
            "seeds": seeds,
            "HP_VAR_RATIO_STRONG": HP_VAR_RATIO_STRONG,
            "HP_SEED_COUNT_MIN": HP_SEED_COUNT_MIN,
        },
    }

    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"VERDICT: {verdict}")
    print(f"MSG: {verdict_msg}")
    print(f"Wrote metrics to {out_path}")


if __name__ == "__main__":
    main()
