"""TCFT deletion-certificate v5: N=8192 envelope extension.

CONTEXT:
  tcft_fresh_erase_v2 HARD_PASS: 5/5 seeds, var_ratio=0.0139 at N=1024.
  tcft_fresh_erase_v4 HARD_PASS: 5/5 seeds, var_ratio~0.000 at N=4096.
  v5 (THIS): push to N=8192. Tests whether TCFT conditioning property holds
    at even larger N (deletion-certificate killer feature at production scale).

SCIENTIFIC QUESTION:
  At N=8192, does the thermodynamic conditioning still reduce variance?
  Mean-field theory predicts var_ratio should approach 0 as N -> inf
  (cleaner thermodynamic work trajectories). v5 confirms or refutes this.

PRE-REGISTERED BANDS (envelope extension of v4 HARD_PASS at N=4096):
  HARD-PASS:
    - var_ratio < 0.10 in >= 3/5 seeds at N=8192
  HARD-FAIL:
    - var_ratio >= 1.0 in ALL 5 seeds (conditioning fails at N=8192)
  MIDDLE-BAND:
    - var_ratio < 0.10 in 1-2/5 seeds only

  Prior anchor: v4 HARD_PASS at N=4096 with var_ratio~0.000.
  Bands NOT widened to +-50% (prior anchor exists).
  Narrowing from v4 threshold (same threshold; expected to be even more clearly HP).

OOM PRE-CHECK:
  Outer-product W at N=8192: O(N^2) = 8192^2 * 8 bytes (float64) = 512MB.
  TCFT uses numpy float64 for thermodynamic precision.
  Single W: 512MB << 6GB headroom. OK.

FORMULA SELF-TESTS:
  1. mean_field_delta_F(N=16, M=2): load=0.1*2/16=0.0125, dF=-0.0975. (same as v4)
  2. vanilla_jarzynski(zeros(8)): delta_F~0.
  3. tcft_conditioned(zeros(2)): invalid (< MIN_CLASS_SIZE=3).
  4. var_ratio = 0 for uniform work array.

Timeout estimate:
  v4 at N=4096 5 seeds elapsed=291s.
  v5 at N=8192 5 seeds: numpy outer-product scales as N^2.
  N-scale: (8192/4096)^2 = 4.0x (outer-product dominant, scaling_exp=2.0)
  Seed ratio: 5/5 = 1.0
  timeout_s = ceil(1.5 * 291 * 4.0 * 1.0) = ceil(1746) -> 1800s.
  Under 4h. Flag as >30min for visibility.

N-suffix: no _nN suffix; production N = 8192 (stated explicitly).
Queue: remote_cpu_queue (pure numpy; no CUDA; N=8192)
Pre-reg: preregs/2026-05-27_tcft_n8192_v5.md
Parent: tcft_fresh_erase_v4 (HARD_PASS N=4096)
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
from typing import Dict, List, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Production config ---
N_FULL = 8192
N_SMOKE = 512
ALPHA_RATIO = 0.125   # M/N
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
KBT = 1.0
PR_THRESHOLD = 4.0
ALPHA_HEBBIAN = 0.1
MIN_CLASS_SIZE = 3

HP_VAR_RATIO_STRONG = 0.10
HP_SEED_COUNT_MIN = 3
DELTA_F_AGREE_PCT_THRESHOLD = 50.0


def get_output_dir(default_name: str = "tcft_n8192_v5") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def compute_cumulative_works(N: int, M: int, seed: int) -> np.ndarray:
    """Per-pattern thermodynamic work during cumulative Hebbian loading."""
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
    elapsed = time.time() - t0
    vanilla = vanilla_jarzynski(works)
    tcft = tcft_conditioned(works)
    mf_dF = mean_field_delta_F(N, M)
    result: Dict = {
        "N": N, "M": M, "seed": seed,
        "elapsed_s": elapsed,
        "vanilla_delta_F": vanilla["delta_F"],
        "vanilla_variance": vanilla["variance"],
        "vanilla_pr_fires": vanilla["pr_fires"],
        "tcft_valid": tcft["valid"],
        "tcft_class0_size": tcft["class0_size"],
        "mf_delta_F": mf_dF,
    }
    if tcft["valid"]:
        agree_pct = abs(tcft["delta_F"] - mf_dF) / (abs(mf_dF) + 1e-9) * 100.0
        result.update({
            "tcft_delta_F": tcft["delta_F"],
            "tcft_variance": tcft["variance"],
            "tcft_variance_ratio": float(tcft["variance_ratio"]),
            "delta_F_agree_pct": agree_pct,
        })
    else:
        result.update({
            "tcft_delta_F": None,
            "tcft_variance": None,
            "tcft_variance_ratio": None,
            "delta_F_agree_pct": None,
        })
    return result


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: works array non-null at smoke scale
    works = compute_cumulative_works(128, 16, seed=42)
    assert works is not None and len(works) == 16, "works array wrong shape"
    assert not np.all(works == 0.0), "works all zero (sentinel)"

    # Self-test 2: mean_field_delta_F formula check
    mf = mean_field_delta_F(16, 2)
    assert abs(mf - (-0.0975)) < 0.01, f"mean_field_delta_F formula error: {mf}"

    # Self-test 3: vanilla_jarzynski with zero works
    vj = vanilla_jarzynski(np.zeros(8))
    assert abs(vj["delta_F"]) < 1e-6, f"zero works -> delta_F should be ~0; got {vj['delta_F']}"

    # Self-test 4: tcft_conditioned with too-small array
    result_small = tcft_conditioned(np.array([0.1, 0.2]))
    assert result_small["valid"] is False, "small array should be invalid"

    # Self-test 5: run_one_seed at smoke N returns valid metrics
    result = run_one_seed(N_SMOKE, seed=17)
    assert result["tcft_valid"] is True, "N=512 should have valid TCFT"
    assert result["tcft_variance_ratio"] is not None, "var_ratio is None"
    assert result["tcft_variance_ratio"] >= 0.0, f"var_ratio negative: {result['tcft_variance_ratio']}"

    # Self-test 6: multi-scale smoke -- N_SMOKE and N_SMOKE*4
    r_smoke = run_one_seed(N_SMOKE, seed=17)
    r_smoke4 = run_one_seed(N_SMOKE * 4, seed=17)
    assert r_smoke["tcft_valid"] is True, "N_SMOKE TCFT not valid"
    assert r_smoke4["tcft_valid"] is True, "N_SMOKE*4 TCFT not valid"

    # Self-test 7: OOM check
    oom_bytes_f64 = N_FULL * N_FULL * 8  # float64
    assert oom_bytes_f64 < 6e9, f"OOM check failed: {oom_bytes_f64:.2e}"

    print(f"[selftest] tcft_n8192_v5 PASSED: var_ratio={result['tcft_variance_ratio']:.4f} "
          f"OOM={oom_bytes_f64:.2e} formula_dF OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0_run = time.time()
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "tcft_n8192_v5")

    print(f"[run] {exp_name} {mode_str} N={N} seeds={seeds}", flush=True)
    out_dir = get_output_dir(exp_name)

    per_seed: List[Dict] = []
    for seed in seeds:
        r = run_one_seed(N, seed)
        per_seed.append(r)
        vr = r.get("tcft_variance_ratio")
        vr_str = f"{vr:.4f}" if vr is not None else "None"
        print(f"  seed={seed}: var_ratio={vr_str} valid={r['tcft_valid']}", flush=True)

    n_valid = sum(1 for r in per_seed if r["tcft_valid"])
    n_hp = sum(1 for r in per_seed if r["tcft_valid"] and
               r.get("tcft_variance_ratio") is not None and
               r["tcft_variance_ratio"] < HP_VAR_RATIO_STRONG)
    valid_ratios = [r["tcft_variance_ratio"] for r in per_seed
                    if r["tcft_valid"] and r.get("tcft_variance_ratio") is not None]
    mean_var_ratio = float(np.mean(valid_ratios)) if valid_ratios else 1.0

    if n_hp >= HP_SEED_COUNT_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: {n_hp}/{len(seeds)} seeds var_ratio<{HP_VAR_RATIO_STRONG} at N={N}. "
            f"TCFT deletion-certificate confirmed at N=8192. "
            f"mean_var_ratio={mean_var_ratio:.4f}"
        )
    elif all(r.get("tcft_variance_ratio", 1.0) is not None and
             r.get("tcft_variance_ratio", 1.0) >= 1.0
             for r in per_seed if r["tcft_valid"]):
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: ALL seeds var_ratio>=1.0 at N={N}. "
            f"TCFT conditioning fails at N=8192. mean_var_ratio={mean_var_ratio:.4f}"
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: {n_hp}/{len(seeds)} seeds var_ratio<{HP_VAR_RATIO_STRONG} at N={N} "
            f"(need {HP_SEED_COUNT_MIN}). mean_var_ratio={mean_var_ratio:.4f}"
        )

    elapsed = round(time.time() - t0_run, 2)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": f"tcft_n8192_v5 {mode_str} N={N}: {n_hp}/{len(seeds)} HP var_ratio<0.10",
        "n_seeds": len(seeds),
        "n_valid": n_valid,
        "n_hp": n_hp,
        "mean_var_ratio": mean_var_ratio,
        "per_seed": per_seed,
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="Smoke run at N=512")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
