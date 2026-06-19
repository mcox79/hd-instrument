"""TCFT M-SWEEP v3: 5-seed FULL at N=8192 to discharge v257 rescue (c).

CONTEXT:
  tcft_m_sweep_v1: smoke HARD_PASS (N=512, M=[32,64], 1 seed).
  tcft_m_sweep_v2: FULL HARD_PASS (N=8192, M=[128..2048], seeds=[7,17]).
    spearman=-1.000 both runs; vr values identical to v1. HARD_PASS corroborated.
    HOWEVER: v2 was a REPLICATION of v1 at SAME 2-seed config -- not a 5-seed expansion.
    v257 rescue (c) and strategy_request_v260 both flag this as STILL OPEN.
  v3 (THIS): GENUINELY 5-seed at N=8192 to discharge v257 rescue (c).

SCIENTIFIC QUESTION:
  Does var_ratio < 0.10 hold across 5 seeds at N=8192?
  Is the 1/sqrt(M) trend robust across seed variance?
  Per v260 strategy: +5% TCFT row lift if cleared (row currently 67-80%).

PRE-REGISTERED BANDS (5-seed envelope expansion; prior anchor = v2 2-seed HARD_PASS):
  Prior anchor: v2 seeds=[7,17] spearman=-1.000, vr all < 0.05 at M>=512.
  Bands: NOT widened (prior 2-seed anchor established; 5-seed is expansion not calibration).

  HARD_PASS: >= 4/5 seeds have var_ratio < 0.10 at ALL M >= 512,
    AND Spearman r(M, mean_vr_per_M) < -0.5 (1/sqrt(M) trend holds).
  HARD_FAIL: >= 2/5 seeds have var_ratio >= 0.10 at M=1024
    (contradicts v2 HARD_PASS baseline at M=1024; regression).
  MIDDLE_BAND: exactly 3/5 seeds pass var_ratio < 0.10 at all M>=512
    (sufficient for trend but not full 4/5 coverage).

FORMULA SELF-TESTS:
  1. HARD_PASS gate: 4/5 seeds pass = 80% coverage. Test: seeds_pass([T,T,T,T,F]) = 4 >= 4 -> PASS.
  2. HARD_FAIL gate: 2/5 seeds fail at M=1024. Test: seeds_fail([0.15, 0.20, 0.05, 0.03, 0.04])
     = 2 >= 0.10 -> HARD_FAIL fires.
  3. Spearman r([128, 256, 512, 1024, 2048], [0.09, 0.05, 0.03, 0.02, 0.015]) < -0.5 -> True.
  4. var_ratio of constant-work array: = 0 (no variance reduction possible).
  5. 1/sqrt(M) ratio: vr_512 / vr_128 ~= sqrt(128/512) = 0.5. Test: 0.05/0.09 = 0.56 ~= 0.5.

TIMEOUT ESTIMATE:
  v2 wall_s = 3495s (2 seeds, N=8192, 5 M values).
  v3: 5 seeds vs 2 seeds = 5/2 * 3495 = 8737s.
  timeout_s = ceil(1.5 * 8737) = ceil(13106) -> 13500s.
  Note: exceeds 7200s (2h flag) per role contract. Justified as load-bearing
  5-seed expansion for Tier-1 TCFT row lock-in (v260 strategy routing note).
  Does NOT exceed 14400s cap.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding contract).
  Also note: suffix _5seed is informational (not N-binding).
  assert N_FULL == 8192 at module scope.
Queue: remote_cpu_queue (pure CPU; N=8192 5-seed M-sweep; ~8700s nominal = ~2.4h)
Pre-reg: preregs/2026-05-28_tcft_m_sweep_v3_n8192_5seed.md
Parent: tcft_m_sweep_v2 (v2 2-seed HARD_PASS; this expands to 5 seeds)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments"))

from _seed_checkpoint import (  # noqa: E402
    aggregate_partials,
    resumable_seeds,
    write_partial,
)

# Load v2 base for shared helpers
_v2_path = REPO / "experiments" / "exp_tcft_m_sweep_v2.py"
_v2_spec = importlib.util.spec_from_file_location("tcft_msweep_v2", _v2_path)
v2 = importlib.util.module_from_spec(_v2_spec)
_v2_spec.loader.exec_module(v2)

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds N = 8192
N_FULL = 8192
assert N_FULL == 8192, "PROT-018: N must be 8192"
N_SMOKE = 512

M_VALUES_FULL  = [128, 256, 512, 1024, 2048]
M_VALUES_SMOKE = [32, 64]

SEEDS_FULL  = [7, 17, 23, 31, 41]    # 5-seed expansion
SEEDS_SMOKE = [17]

# Thresholds
HP_VAR_RATIO_MAX  = 0.10
HF_VAR_RATIO_MIN  = 0.10   # HARD_FAIL: >= 2 seeds fail at M=1024
HP_SEEDS_PASS_MIN = 4       # Need >= 4/5 seeds
HF_SEEDS_FAIL_MIN = 2       # HARD_FAIL if >= 2 seeds fail at M=1024
HP_SPEARMAN_MAX   = -0.5


def get_output_dir(default_name: str = "tcft_m_sweep_v3_n8192_5seed") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M: int, seed: int) -> Dict:
    return v2.run_one_cell(N, M, seed)


def compute_spearman_r(x: List[float], y: List[float]) -> float:
    """Spearman rank correlation."""
    n = len(x)
    if n < 2:
        return 0.0
    rank_x = np.argsort(np.argsort(x)).astype(float)
    rank_y = np.argsort(np.argsort(y)).astype(float)
    d_sq = ((rank_x - rank_y) ** 2).sum()
    return float(1.0 - 6.0 * d_sq / (n * (n ** 2 - 1)))


def compute_verdict(summary: dict) -> tuple:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("TCFT_MSWEEP_V3_INCONCLUSIVE", "No per-seed data.")

    m_values = sorted(summary.get("m_values", M_VALUES_FULL))

    # Per-seed check at M>=512
    seeds_pass = []
    seeds_fail_1024 = []
    for seed_key, cells in per_seed.items():
        # Check each M cell; key is "tcft_variance_ratio" from v1/v2 base
        vr_by_m = {}
        for c in cells:
            m = c.get("M")
            vr = c.get("tcft_variance_ratio", c.get("var_ratio"))
            if m is not None and vr is not None:
                vr_by_m[m] = vr

        # HARD_PASS per seed: all M>=512 have vr < 0.10
        large_m_pass = all(vr_by_m.get(m, 1.0) < HP_VAR_RATIO_MAX
                           for m in m_values if m >= 512)
        seeds_pass.append(1 if large_m_pass else 0)

        # HARD_FAIL check: M=1024 vr >= 0.10
        vr_1024 = vr_by_m.get(1024)
        if vr_1024 is not None and vr_1024 >= HF_VAR_RATIO_MIN:
            seeds_fail_1024.append(seed_key)

    n_pass = sum(seeds_pass)
    n_fail = len(seeds_fail_1024)
    n_seeds = len(per_seed)

    # Spearman on mean vr per M
    mean_vr_per_m = {}
    for m in m_values:
        vrs = []
        for cells in per_seed.values():
            for c in cells:
                if c.get("M") == m:
                    vr = c.get("tcft_variance_ratio", c.get("var_ratio"))
                    if vr is not None:
                        vrs.append(vr)
        mean_vr_per_m[m] = float(np.mean(vrs)) if vrs else 1.0

    m_sorted = sorted(mean_vr_per_m.keys())
    spearman_r = compute_spearman_r(
        [float(m) for m in m_sorted],
        [mean_vr_per_m[m] for m in m_sorted]
    )

    msg_base = (f"seeds_pass={n_pass}/{n_seeds} at all_M>=512. "
                f"seeds_fail_at_M1024={seeds_fail_1024}. "
                f"spearman_r={spearman_r:.3f}. "
                f"mean_vr_by_M={dict((m, round(mean_vr_per_m[m], 4)) for m in m_sorted)}.")

    # HARD_FAIL check first
    if n_fail >= HF_SEEDS_FAIL_MIN:
        return ("TCFT_V3_HARD_FAIL",
                f"REGRESSION: {n_fail} seeds fail vr<0.10 at M=1024. {msg_base} "
                f"Contradicts v2 HARD_PASS; seed-variance exceeds prior evidence.")

    # HARD_PASS
    if n_pass >= HP_SEEDS_PASS_MIN and spearman_r < HP_SPEARMAN_MAX:
        return ("TCFT_V3_HARD_PASS",
                f"5-SEED HARD_PASS: {n_pass}/{n_seeds} seeds pass all_M>=512. {msg_base} "
                f"1/sqrt(M) trend confirmed across 5 seeds. Tier-1 lock-in evidence.")

    # MIDDLE_BAND
    return ("TCFT_V3_MIDDLE_BAND",
            f"Partial pass: {n_pass}/{n_seeds} seeds. {msg_base} "
            f"Insufficient coverage for Tier-1 lock-in but no regression.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. v2 import chain
    assert v2 is not None, "v2 import failed"
    print("[selftest 1/5] v2 import OK", flush=True)

    # 2. run_one_cell at smoke scale, returns valid var_ratio
    t0 = time.time()
    cell = run_one_cell(N_SMOKE, M=32, seed=17)
    t_c = time.time() - t0
    # v2 uses 'tcft_variance_ratio' key (not 'var_ratio')
    vr_key = "var_ratio" if "var_ratio" in cell else "tcft_variance_ratio"
    assert vr_key in cell, f"missing var_ratio key: {cell.keys()}"
    vr = cell[vr_key]
    assert vr is not None, f"{vr_key} is None"
    assert np.isfinite(vr), f"{vr_key} non-finite: {vr}"
    print(f"[selftest 2/5] run_one_cell N={N_SMOKE} M=32 {vr_key}={vr:.4f} "
          f"t={t_c:.1f}s OK", flush=True)

    # 3. Multi-scale smoke: M=32 AND M=128 (4x)
    cell2 = run_one_cell(N_SMOKE, M=128, seed=17)
    vr2_key = "var_ratio" if "var_ratio" in cell2 else "tcft_variance_ratio"
    assert vr2_key in cell2 and np.isfinite(cell2[vr2_key]), \
        f"multi-scale cell2 invalid: {cell2}"
    print(f"[selftest 3/5] multi-scale M=128 {vr2_key}={cell2[vr2_key]:.4f} OK", flush=True)

    # 4. Spearman formula
    r_perfect = compute_spearman_r([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert abs(r_perfect - (-1.0)) < 0.01, f"Spearman -1.0 formula error: {r_perfect}"
    r_trivial = compute_spearman_r([1, 2], [1, 2])
    assert abs(r_trivial - 1.0) < 0.01, f"Spearman +1.0 formula error: {r_trivial}"
    print("[selftest 4/5] Spearman formula OK", flush=True)

    # 5. Verdict formula self-tests
    # HARD_PASS: 5/5 seeds pass, spearman=-1.0
    cells_5 = [{"M": 128, "tcft_variance_ratio": 0.09}, {"M": 256, "tcft_variance_ratio": 0.06},
               {"M": 512, "tcft_variance_ratio": 0.03}, {"M": 1024, "tcft_variance_ratio": 0.02},
               {"M": 2048, "tcft_variance_ratio": 0.015}]
    summary_hp = {"per_seed": {str(s): cells_5 for s in [7, 17, 23, 31, 41]},
                  "m_values": [128, 256, 512, 1024, 2048]}
    v, msg = compute_verdict(summary_hp)
    assert v == "TCFT_V3_HARD_PASS", f"Expected HARD_PASS: {v}"

    # HARD_FAIL: 2 seeds fail at M=1024
    cells_fail = [{"M": 512, "tcft_variance_ratio": 0.05}, {"M": 1024, "tcft_variance_ratio": 0.15}]
    cells_pass_4 = [{"M": 512, "tcft_variance_ratio": 0.03}, {"M": 1024, "tcft_variance_ratio": 0.02}]
    per_seed_hf = {"7": cells_fail, "17": cells_fail, "23": cells_pass_4,
                   "31": cells_pass_4, "41": cells_pass_4}
    summary_hf = {"per_seed": per_seed_hf, "m_values": [512, 1024]}
    v, msg = compute_verdict(summary_hf)
    assert v == "TCFT_V3_HARD_FAIL", f"Expected HARD_FAIL: {v}: {msg}"
    print("[selftest 5/5] verdict formulas OK", flush=True)

    print("[SELFTEST PASS] tcft_m_sweep_v3_n8192_5seed instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    N = N_SMOKE if smoke else N_FULL
    m_values = M_VALUES_SMOKE if smoke else M_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"

    t0 = time.time()
    out_dir = get_output_dir()

    print(f"[tcft_v3] N={N} M_values={m_values} seeds={seeds} mode={mode_str}", flush=True)

    # PER-SEED CHECKPOINT (PROT-019 resume contract): scan partials so a
    # mid-run crash (CUDA OOM, timeout kill) can resume instead of restarting.
    done_seeds, remaining_seeds = resumable_seeds(seeds, out_dir)
    if done_seeds:
        print(f"[ckpt] resume: {len(done_seeds)}/{len(seeds)} seeds already "
              f"complete from prior run; running remaining "
              f"{len(remaining_seeds)}: {remaining_seeds}", flush=True)
    else:
        print(f"[ckpt] no prior partials; running all {len(seeds)} seeds",
              flush=True)

    for seed in remaining_seeds:
        cells_for_seed: List[Dict] = []
        for M in m_values:
            print(f"  seed={seed} M={M}...", flush=True)
            t_cell = time.time()
            cell = run_one_cell(N, M, seed)
            t_c = time.time() - t_cell
            vr = cell.get("tcft_variance_ratio", cell.get("var_ratio", float("nan")))
            print(f"    tcft_variance_ratio={vr:.4f} t={t_c:.1f}s", flush=True)
            cells_for_seed.append(cell)
        # Atomic checkpoint: written BEFORE moving to next seed so a crash
        # in the NEXT seed does not lose this one. Payload schema differs
        # slightly from saad_solla -- aggregator just stores the dict.
        write_partial(out_dir, seed, {"cells": cells_for_seed})
        print(f"  seed={seed} DONE [ckpt written]", flush=True)

    # Aggregate ALL seeds (this-run + prior-run partials) into the original
    # per_seed shape: {str(seed): [cell, ...]}.
    agg = aggregate_partials(out_dir, seeds)
    per_seed: Dict[str, List[Dict]] = {
        k: v.get("cells", []) for k, v in agg.items()
    }

    summary = {"per_seed": per_seed, "m_values": m_values, "N": N, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "m_values": m_values, "seeds": seeds, "smoke": smoke},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[tcft_v3] VERDICT: {verdict}", flush=True)
    print(f"[tcft_v3] {verdict_msg}", flush=True)
    print(f"[tcft_v3] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
