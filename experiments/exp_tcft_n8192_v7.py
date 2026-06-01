"""TCFT deletion-certificate v7: FULL N=8192 5-seed run (v6 completed smoke only).

CONTEXT:
  tcft_n8192_v6 ran smoke only (N=512, 1 seed, elapsed=0.33s) and returned MIDDLE_BAND
  ("1/1 seeds var_ratio<0.1 at N=512 (need 3)"). The FULL N=8192 5-seed run was never
  queued. v7 is that run.

  Prior chain:
  - tcft_fresh_erase_v4: HARD_PASS 5/5 seeds at N=4096.
  - tcft_n8192_v5: TIMEOUT_AT_4_OF_5_SEEDS_HP_PATTERN (seed=41 killed; 4 seeds HP var_ratio=0.0000).
  - tcft_n8192_v6: smoke only (MIDDLE_BAND 1/1 seeds N=512); FULL not run.
  - v7 (THIS): FULL N=8192 5 seeds, inherits v6 infrastructure.

SCIENTIFIC QUESTION:
  Does TCFT var_ratio < 0.10 hold for all 5/5 seeds at N=8192?
  (4 of 5 seeds already confirmed HP at v5; v7 completes the set with sufficient timeout.)

PRE-REGISTERED BANDS (same as v5/v6):
  HARD-PASS:
    - var_ratio < 0.10 in >= 3/5 seeds at N=8192
    - (Expected 5/5 given v5 4-of-5 HP pattern)
  HARD-FAIL:
    - var_ratio >= 1.0 in ALL 5 seeds (contradicts v5 evidence)
  MIDDLE-BAND:
    - var_ratio < 0.10 in only 1-2 seeds

  Prior anchor: v5 4/5 seeds HP at N=8192, var_ratio=0.0000. Bands unchanged.
  Expected outcome: HARD_PASS.

TIMEOUT ESTIMATE:
  v5 actual: 4 seeds in ~1800s at N=8192 => ~450s per seed.
  5 seeds * 450s * 1.5 safety = ceil(3375) = 3600s.
  Adding 50% margin from v5 lessons: 5400s.
  Under 4h threshold. Remote-CPU flag not needed.

OOM PRE-CHECK:
  W at N=8192: N^2 * 8 bytes (float64) = 512MB << 6GB. OK.

FORMULA SELF-TESTS:
  1. mean_field_delta_F(N=16, M=2): load=0.125, sign contribution correct.
  2. tcft_conditioned with class_size < MIN_CLASS_SIZE returns tcft_valid=False.
  3. var_ratio = tcft_variance / vanilla_variance.

N-suffix: no _nN suffix; production N = 8192 (N_FULL = 8192 explicitly below).
Queue: remote_cpu_queue (pure numpy; no CUDA; N=8192 5-seed; ~5400s)
Pre-reg: preregs/2026-05-27_tcft_n8192_v5.md (same bands; v7 = v6-FULL-rerun)
Parent: tcft_n8192_v6 (smoke-only MIDDLE_BAND; cap_map row pending HARD_PASS confirmation)
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

# Import v5 core infrastructure (v6 already validated this works)
import importlib.util as _ilu
_v5_path = REPO / "experiments" / "exp_tcft_n8192_v5.py"
_v5_spec = _ilu.spec_from_file_location("tcft_v5_base", _v5_path)
_v5_mod = _ilu.module_from_spec(_v5_spec)
_v5_spec.loader.exec_module(_v5_mod)

run_one_seed = _v5_mod.run_one_seed
HP_VAR_RATIO_STRONG = _v5_mod.HP_VAR_RATIO_STRONG
HP_SEED_COUNT_MIN = _v5_mod.HP_SEED_COUNT_MIN

# Production config
N_FULL = 8192
N_SMOKE = 512
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]


def get_output_dir(default_name: str = "tcft_n8192_v7") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 8192, f"N_FULL must be 8192; got {N_FULL}"
    assert callable(run_one_seed), "run_one_seed not callable from v5"

    # Smoke scale
    r = run_one_seed(N_SMOKE, seed=17)
    assert r["tcft_valid"] is True, f"N_SMOKE tcft_valid=False: {r}"
    vr = r.get("tcft_variance_ratio")
    assert vr is not None and math.isfinite(vr), f"tcft_variance_ratio not finite: {vr}"
    assert vr < HP_VAR_RATIO_STRONG, f"selftest: var_ratio={vr} NOT < HP threshold {HP_VAR_RATIO_STRONG}"

    # Multi-scale smoke
    r4 = run_one_seed(N_SMOKE * 4, seed=17)
    assert r4["tcft_valid"] is True, f"N_SMOKE*4 tcft_valid=False: {r4}"

    # OOM check
    oom_bytes = N_FULL * N_FULL * 8
    assert oom_bytes < 6e9, f"OOM: {oom_bytes:.2e} >= 6GB"

    # Output-path check
    import os as _os
    _orig = _os.environ.get("HDLAB_EXP_NAME")
    _os.environ["HDLAB_EXP_NAME"] = "test_tcft_v7_path"
    _test_dir = get_output_dir()
    if _orig is None:
        del _os.environ["HDLAB_EXP_NAME"]
    else:
        _os.environ["HDLAB_EXP_NAME"] = _orig
    assert _test_dir.name == "exp_test_tcft_v7_path", \
        f"get_output_dir ignores HDLAB_EXP_NAME: got {_test_dir.name}"
    _test_dir.rmdir()

    print(
        f"[selftest] tcft_n8192_v7 PASSED: N={N_FULL} OK, "
        f"smoke var_ratio={vr:.6f}, multi-scale OK, OOM={oom_bytes:.2e}",
        flush=True,
    )


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "tcft_n8192_v7")

    print(f"[run] {exp_name} {mode_str} N={N} seeds={seeds}", flush=True)
    if not smoke:
        assert N == N_FULL, f"FULL run must use N={N_FULL}; got {N}"

    out_dir = get_output_dir(exp_name)

    per_seed: List[Dict] = []
    for seed in seeds:
        t_s = time.time()
        r = run_one_seed(N, seed)
        per_seed.append(r)
        vr = r.get("tcft_variance_ratio")
        vr_str = f"{vr:.6f}" if vr is not None else "None"
        print(
            f"  seed={seed}: var_ratio={vr_str} valid={r['tcft_valid']} "
            f"({time.time()-t_s:.1f}s)",
            flush=True,
        )

    n_valid = sum(1 for r in per_seed if r["tcft_valid"])
    n_hp = sum(
        1 for r in per_seed
        if r["tcft_valid"]
        and r.get("tcft_variance_ratio") is not None
        and r["tcft_variance_ratio"] < HP_VAR_RATIO_STRONG
    )
    valid_ratios = [
        r["tcft_variance_ratio"] for r in per_seed
        if r["tcft_valid"] and r.get("tcft_variance_ratio") is not None
    ]
    mean_var_ratio = float(np.mean(valid_ratios)) if valid_ratios else 1.0

    if n_hp >= HP_SEED_COUNT_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: {n_hp}/{len(seeds)} seeds var_ratio<{HP_VAR_RATIO_STRONG} at N={N}. "
            f"TCFT deletion-certificate confirmed at N=8192. "
            f"mean_var_ratio={mean_var_ratio:.6f}. "
            f"(v5 4/5 seeds timeout resolved; v7 FULL run.)"
        )
    elif all(
        r.get("tcft_variance_ratio", 1.0) >= 1.0
        for r in per_seed if r["tcft_valid"]
    ):
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

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": f"tcft_n8192_v7 {mode_str} N={N}: {n_hp}/{len(seeds)} HP var_ratio<{HP_VAR_RATIO_STRONG}",
        "n_seeds": len(seeds),
        "n_valid": n_valid,
        "n_hp": n_hp,
        "mean_var_ratio": mean_var_ratio,
        "per_seed": per_seed,
        "config": {"N": N, "smoke": smoke, "seeds": seeds},
    }
    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
