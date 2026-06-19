"""TCFT deletion-certificate v6: N=8192 re-run with corrected timeout.

CONTEXT:
  tcft_fresh_erase_v4 HARD_PASS: 5/5 seeds, var_ratio~0.000 at N=4096.
  tcft_n8192_v5 TIMEOUT_AT_4_OF_5_SEEDS_HP_PATTERN:
    - 4/5 seeds completed: var_ratio=0.0000 (100x below 0.10 HP threshold).
    - Seed=41 killed by 1800s per-experiment timeout before completion.
    - Not a HARD_FAIL: the math is trending toward a FULL HARD_PASS.
    - Root cause: timeout_s=1800 too short (actual ~450s per seed at N=8192).
    - Verdict_handler cap_map v241 recommends: re-ship with --timeout 5400.
  v6 (THIS): same N=8192 5-seed FULL run, timeout corrected to 5400s.

SCIENTIFIC QUESTION:
  With sufficient timeout, does TCFT var_ratio < 0.10 hold for all 5/5 seeds
  at N=8192? (4/5 seeds already confirmed at HP signal in v5; v6 completes the set)

PRE-REGISTERED BANDS (same as v5; no update needed):
  HARD-PASS:
    - var_ratio < 0.10 in >= 3/5 seeds at N=8192 (EXPECTED: 5/5 given v5 4/5 HP pattern)
  HARD-FAIL:
    - var_ratio >= 1.0 in ALL 5 seeds (UNEXPECTED given v5 evidence)
  MIDDLE-BAND:
    - var_ratio < 0.10 in 1-2/5 seeds only

  Prior anchor: v5 4/5 seeds at N=8192 var_ratio=0.0000. Bands unchanged.
  Expected outcome: HARD_PASS (5/5 seeds). The truncation in v5 was timeout-only.

OOM PRE-CHECK:
  Outer-product W at N=8192: N^2 * 8 bytes (float64) = 512MB << 6GB headroom. OK.

FORMULA SELF-TESTS:
  1. mean_field_delta_F(N=16, M=2): load=0.1*2/16=0.0125, dF=-0.0975.
  2. vanilla_jarzynski(zeros(8)): delta_F~0.
  3. tcft_conditioned(zeros(2)): invalid (< MIN_CLASS_SIZE=3).
  4. var_ratio = 0 for uniform work array.

Timeout estimate:
  v5 actual: 4 seeds completed in approx 1800s => ~450s per seed at N=8192.
  5 seeds * 450s = 2250s actual.
  timeout_s = ceil(1.5 * 2250) = ceil(3375) = 3600s.
  Adding 50% safety margin per verdict_handler v241 recommendation: 5400s.
  Under 4h (14400s). 5400s < 7200s threshold (no >2h flag needed beyond note here).

N-suffix: no _nN suffix; production N = 8192 (N_FULL = 8192 explicitly below).
Queue: remote_cpu_queue (pure numpy; no CUDA; N=8192 5-seed)
Pre-reg: preregs/2026-05-27_tcft_n8192_v5.md (same bands; v6 = timeout-corrected rerun)
Parent: tcft_n8192_v5 (TIMEOUT_AT_4_OF_5_SEEDS_HP_PATTERN; cap_map v241)
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
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Import v5 core infrastructure to avoid code duplication ---
import importlib.util as _ilu
_v5_path = REPO / "experiments" / "exp_tcft_n8192_v5.py"
_v5_spec = _ilu.spec_from_file_location("tcft_v5_base", _v5_path)
_v5_mod = _ilu.module_from_spec(_v5_spec)
_v5_spec.loader.exec_module(_v5_mod)

# Reuse v5 math functions
run_one_seed = _v5_mod.run_one_seed
HP_VAR_RATIO_STRONG = _v5_mod.HP_VAR_RATIO_STRONG
HP_SEED_COUNT_MIN = _v5_mod.HP_SEED_COUNT_MIN

# Bit-precision helper (BE-1 plumbing; fp32 default = no-op = backwards compat).
sys.path.insert(0, str(REPO / "experiments"))
import _bit_precision as bp  # noqa: E402


def _make_precision_aware_works(precision: str):
    """Return a compute_cumulative_works variant that quantizes W after each update.

    Mirrors v5 exactly when precision='fp32' (delegates to original).
    For non-fp32 precisions: applies bp.quantize_roundtrip to W after every
    Hebbian outer-product update, so the works trajectory reflects substrate-at-INTN.
    """
    if precision == "fp32":
        return _v5_mod.compute_cumulative_works

    ALPHA_HEBBIAN = _v5_mod.ALPHA_HEBBIAN

    def compute_cumulative_works_quantized(N: int, M: int, seed: int):
        rng = np.random.default_rng(seed)
        patterns = rng.choice([-1.0, 1.0], size=(M, N))
        W = np.zeros((N, N), dtype=np.float64)
        works = np.zeros(M, dtype=np.float64)
        for mu in range(M):
            v = patterns[mu]
            w = -float(v @ W @ v)
            works[mu] = w
            W = W + ALPHA_HEBBIAN * np.outer(v, v) / N
            np.fill_diagonal(W, 0.0)
            # Precision intercept: quantize W after each storage update.
            # Cast to float32 for quantize backend, then back to float64 for math.
            W32 = W.astype(np.float32)
            W32 = bp.quantize_roundtrip(W32, precision)
            W = W32.astype(np.float64)
        return works

    return compute_cumulative_works_quantized

# Production config -- N_FULL = 8192 (no _nN suffix; explicit below)
N_FULL = 8192
N_SMOKE = 512
SEEDS_FULL = [7, 17, 23, 31, 41]   # same seeds as v5
SEEDS_SMOKE = [17]


def get_output_dir(default_name: str = "tcft_n8192_v6") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. N_FULL binding check
    assert N_FULL == 8192, f"N_FULL must be 8192; got {N_FULL}"

    # 2. run_one_seed importable from v5
    assert callable(run_one_seed), "run_one_seed not callable from v5"

    # 3. Run at N_SMOKE scale
    r = run_one_seed(N_SMOKE, seed=17)
    assert r["tcft_valid"] is True, f"N_SMOKE tcft_valid=False: {r}"
    vr = r.get("tcft_variance_ratio")
    assert vr is not None and math.isfinite(vr), f"tcft_variance_ratio not finite: {vr}"

    # 4. Multi-scale smoke: N_SMOKE and N_SMOKE*4
    r4 = run_one_seed(N_SMOKE * 4, seed=17)
    assert r4["tcft_valid"] is True, f"N_SMOKE*4 tcft_valid=False: {r4}"

    # 5. OOM pre-check at N=8192 (float64)
    oom_bytes = N_FULL * N_FULL * 8
    assert oom_bytes < 6e9, f"OOM check: {oom_bytes:.2e} >= 6GB"

    # 6. Output-path parameterization
    import os as _os
    _orig = _os.environ.get("HDLAB_EXP_NAME")
    _os.environ["HDLAB_EXP_NAME"] = "test_tcft_v6_path"
    _test_dir = get_output_dir()
    if _orig is None:
        del _os.environ["HDLAB_EXP_NAME"]
    else:
        _os.environ["HDLAB_EXP_NAME"] = _orig
    assert _test_dir.name == "exp_test_tcft_v6_path", \
        f"get_output_dir ignores HDLAB_EXP_NAME: got {_test_dir.name}"
    _test_dir.rmdir()

    print(f"[selftest] tcft_n8192_v6 PASSED: N={N_FULL} assertion OK, "
          f"smoke var_ratio={vr:.6f}, multi-scale OK, OOM={oom_bytes:.2e}",
          flush=True)


_instrumentation_selftest()


def run(smoke: bool = False, precision: str = "fp32") -> None:
    t0 = time.time()
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "tcft_n8192_v6")

    print(f"[run] {exp_name} {mode_str} N={N} seeds={seeds} precision={precision}",
          flush=True)
    if not smoke:
        assert N == N_FULL, f"FULL run must use N={N_FULL}; got {N}"

    out_dir = get_output_dir(exp_name)

    # Install precision-aware compute_cumulative_works if needed.
    # fp32 path leaves the original v5 function untouched (byte-exact backwards compat).
    _orig_ccw = _v5_mod.compute_cumulative_works
    try:
        if precision != "fp32":
            _v5_mod.compute_cumulative_works = _make_precision_aware_works(precision)

        per_seed: List[Dict] = []
        for seed in seeds:
            t_s = time.time()
            r = run_one_seed(N, seed)
            per_seed.append(r)
            vr = r.get("tcft_variance_ratio")
            vr_str = f"{vr:.6f}" if vr is not None else "None"
            print(f"  seed={seed}: var_ratio={vr_str} valid={r['tcft_valid']} "
                  f"({time.time()-t_s:.1f}s)", flush=True)
    finally:
        _v5_mod.compute_cumulative_works = _orig_ccw

    n_valid = sum(1 for r in per_seed if r["tcft_valid"])
    n_hp = sum(1 for r in per_seed
               if r["tcft_valid"] and r.get("tcft_variance_ratio") is not None
               and r["tcft_variance_ratio"] < HP_VAR_RATIO_STRONG)
    valid_ratios = [r["tcft_variance_ratio"] for r in per_seed
                    if r["tcft_valid"] and r.get("tcft_variance_ratio") is not None]
    mean_var_ratio = float(np.mean(valid_ratios)) if valid_ratios else 1.0

    if n_hp >= HP_SEED_COUNT_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: {n_hp}/{len(seeds)} seeds var_ratio<{HP_VAR_RATIO_STRONG} at N={N}. "
            f"TCFT deletion-certificate confirmed at N=8192. "
            f"mean_var_ratio={mean_var_ratio:.6f}. "
            f"(v5 4/5 seeds HP pattern completed; seed=41 timeout resolved.)"
        )
    elif all(r.get("tcft_variance_ratio", 1.0) >= 1.0
             for r in per_seed if r["tcft_valid"]):
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: ALL seeds var_ratio>=1.0 at N={N}. "
            f"TCFT conditioning fails at N=8192. mean_var_ratio={mean_var_ratio:.6f}"
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: {n_hp}/{len(seeds)} seeds var_ratio<{HP_VAR_RATIO_STRONG} at N={N} "
            f"(need {HP_SEED_COUNT_MIN}). mean_var_ratio={mean_var_ratio:.6f}"
        )

    elapsed = round(time.time() - t0, 2)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)

    precision_md = bp.precision_metadata(N * N, precision)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": f"tcft_n8192_v6 {mode_str} N={N}: {n_hp}/{len(seeds)} HP var_ratio<{HP_VAR_RATIO_STRONG}",
        "n_seeds": len(seeds),
        "n_valid": n_valid,
        "n_hp": n_hp,
        "mean_var_ratio": mean_var_ratio,
        "per_seed": per_seed,
        "config": {"N": N, "smoke": smoke, "seeds": seeds,
                   "bit_precision": precision},
        **precision_md,
    }
    mpath = out_dir / "metrics.json"
    tmp = mpath.with_suffix(".json.tmp")
    with open(tmp, "w") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, mpath)
    print(f"[exp] metrics -> {mpath}", flush=True)
    print(f"[precision] {precision} W_bytes={precision_md['precision_memory_bytes']} "
          f"baseline={precision_md['precision_baseline_bytes']} "
          f"ratio={precision_md['precision_compression_ratio']}x", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--bit-precision", dest="bit_precision", default="fp32",
                        choices=list(bp.VALID_PRECISIONS),
                        help="W-matrix precision for BE-1 sweep (default fp32 = no-op)")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke, precision=args.bit_precision)
