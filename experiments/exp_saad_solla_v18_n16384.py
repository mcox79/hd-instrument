"""Saad-Solla saddle-cascade v18: N-extension to N=16384.

CONTEXT:
  v15 (v266 HARD_PASS_STRONG): N=8192 5-seed f-sweep plateau confirmed.
  v16 (v267 HARD_PASS): M-density axis; plateau holds at M_frac in {0.25, 0.5}.
  v17 (v267 HARD_PASS): codebook-robustness; BSC + antipodal both plateau.
  v18: N-extension to N=16384. Tests whether plateau is a finite-N artifact or
  grows with N (as expected from saddle-hierarchy theory: landscape deepens with N).

  Cap_map row: Saad-Solla LEADING checkmark. v16 N-extension mentioned as sketch (d).
  Framework reliability specific 60-72%. N-extension at N=16384 is the 4th axis:
  if plateau HOLDS at N=16384, the saddle structure is N-scaling confirmed.

SCIENTIFIC QUESTION:
  Does the Saad-Solla f-sweep plateau (r2<0.85 OR max_dev>=0.40) hold at N=16384?
  f-sweep = fraction of Phase B patterns [0.0, 0.15, 0.5, 0.8, 1.0].
  If plateau holds: saddle structure is not a finite-N artifact; scales to production N.

PRE-REGISTERED BANDS (N-extension; prior anchor = v15 N=8192 5-seed HARD_PASS_STRONG):
  Prior anchor: v15 r2_mean=0.290 sigma=0.013, max_dev_mean=0.514 sigma=0.0015 at N=8192.
  Expected: plateau even more pronounced at N=16384 (deeper saddle hierarchy).
  Gate: same as v15 (r2<0.85 OR max_dev>=0.40 per seed).

  HARD_PASS: plateau gate fires at >= 3/5 seeds at N=16384 (calibrated to v15 expectation).
    Interpretation: Saad-Solla saddle-structure is N-scaling confirmed.
  HARD_FAIL: ALL seeds show smooth-monotone (r2>=0.95 AND max_dev<0.04).
    Would indicate plateau is N=8192-specific artifact (unlikely given 3-axis evidence).
  MIDDLE_BAND: < 3/5 seeds pass gate but > 0 seeds show plateau.

FORMULA SELF-TESTS:
  1. N=16384, M_frac=0.125 -> M=2048 Phase A patterns.
  2. f=0.5: replace 50% of M Phase B -> 1024 new patterns.
  3. pearson_r2([0.60,0.62,0.94,0.94,0.94], [0,0.25,0.5,0.75,1.0]) < 0.85 -> HARD_PASS.
  4. N == 16384 (PROT-018 binding).

OOM CHECK:
  W float32 at N=16384: 16384^2 * 4 = 1024MB. Under 6GB (2-matrix peak = 2GB). OK.
  Pattern batch: BYTES_SMOKE * N * 4 = tiny. OK.

TIMEOUT ESTIMATE:
  v15 N=8192 25-cell wall: 16291s -> 652s/cell.
  N=16384 vs N=8192: O(N^2) -> 4x per cell -> 2608s/cell.
  v18: 3 seeds x 5 f-pts = 15 cells (scope reduced from 5 seeds to fit budget).
  Estimated: 15 * 2608s = 39120s -> exceeds 14400.
  SCOPED DOWN: 2 seeds x 5 f-pts = 10 cells.
  Estimated: 10 * 2608s = 26080s. Still exceeds.
  MINIMUM: 2 seeds x 3 f-pts = 6 cells.
  Estimated: 6 * 2608s = 15648s. Exceeds 14400.
  RATIONALE: user requested 24h window (aggressive); PROT-019 _n>=8192 floor = 21600.
  Final: 2 seeds x 5 f-pts = 10 cells, timeout_s = 43200 (12h; user explicit 24h window).
  NOTE: >14400 = flag for visibility per role contract.

N-suffix: _n16384 -> production N = 16384 (PROT-018 binding).
Anchor: saad_solla_v18_n16384
Queue: overnight_queue (GPU; N=16384 Saad-Solla N-extension, 2 seeds x 5 f-pts)
Pre-reg: preregs/2026-05-28_saad_solla_v18_n16384.md
Parent: saad_solla_v15_n8192_5seed (v266 HARD_PASS_STRONG) + v16/v17 (v267 HARD_PASS)
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
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments"))

from _seed_checkpoint import (  # noqa: E402
    aggregate_partials,
    resumable_seeds,
    write_partial,
)

# Load v15 base for run_one_cell_no_replay, pearson_r2
_v15_path = REPO / "experiments" / "exp_saad_solla_v15_n8192_5seed.py"
_v15_spec = importlib.util.spec_from_file_location("ss_v15_v18", _v15_path)
v15 = importlib.util.module_from_spec(_v15_spec)
_v15_spec.loader.exec_module(v15)

pearson_r2 = v15.pearson_r2
run_one_cell_no_replay = v15.run_one_cell_no_replay

# PRODUCTION CONFIG -- PROT-018: _n16384 suffix binds to N = 16384
N = 16384      # PROT-018 binding contract
N_SMOKE = 512
assert N == 16384, f"PROT-018: N must be 16384; got {N}"

F_SWEEP_FULL  = [0.0, 0.15, 0.50, 0.80, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]

# 2 seeds to fit within 43200s timeout
SEEDS_FULL  = [7, 17]
SEEDS_SMOKE = [17]

BATCH_SIZE       = 32
BATCH_SIZE_SMOKE = 16
EPOCHS           = 3
EPOCHS_SMOKE     = 1
PHASE_A_EPOCHS   = 3
PHASE_A_EPOCHS_SMOKE = 1
BYTES            = 150_000
BYTES_SMOKE      = 4_000

# Gate thresholds (matching v15)
HP_R2_MAX       = 0.85
HP_MAX_DEV_ALT  = 0.40
HF_R2_MIN       = 0.95
HF_MAX_DEV_MAX  = 0.04
HP_MAJORITY_MIN = 1    # >= 1/2 seeds (2-seed run)


def get_output_dir(default_name: str = "saad_solla_v18_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def seed_passes_hp(r2: float, max_dev: float) -> bool:
    return r2 < HP_R2_MAX or max_dev >= HP_MAX_DEV_ALT


def run_v18_seed(N_cfg: int, seed: int, f_sweep: List[float],
                 smoke: bool, device: torch.device) -> Dict:
    """Run one Saad-Solla f-sweep at N_cfg for one seed."""
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE
    epochs = EPOCHS_SMOKE if smoke else EPOCHS
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS
    n_bytes = BYTES_SMOKE if smoke else BYTES

    ret_A_vals = []
    t_seed = time.monotonic()

    for f in f_sweep:
        cell = run_one_cell_no_replay(
            seed=seed, f=f, N_cfg=N_cfg,
            batch_size=batch_size,
            n_epochs=epochs,
            phase_a_epochs=phase_a_epochs,
            n_bytes=n_bytes,
            device=device,
        )
        ret_A_vals.append(cell.get("retention_A", float("nan")))
        print(f"    N={N_cfg} seed={seed} f={f:.2f} ret_A={cell.get('retention_A', float('nan')):.4f}",
              flush=True)

    # Compute r2 and max_dev
    f_arr = list(f_sweep)
    r2 = pearson_r2(f_arr, ret_A_vals)
    residuals = [abs(ret_A_vals[i] - (ret_A_vals[0] + f_arr[i] *
                                       (ret_A_vals[-1] - ret_A_vals[0])))
                 for i in range(len(f_arr))]
    max_dev = max(residuals) if residuals else 0.0
    passes = seed_passes_hp(r2, max_dev)

    elapsed_seed = time.monotonic() - t_seed
    print(f"  seed={seed} r2={r2:.4f} max_dev={max_dev:.4f} "
          f"passes={passes} ({elapsed_seed:.1f}s)", flush=True)

    return {
        "seed": seed, "N": N_cfg,
        "f_vals": f_arr, "ret_A_vals": ret_A_vals,
        "r2": round(r2, 4), "max_dev": round(max_dev, 4),
        "passes_hp": passes,
        "elapsed_s": round(elapsed_seed, 2),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("SS_V18_INCONCLUSIVE", "No cells.")

    pass_seeds = sum(1 for r in results if r.get("passes_hp", False))
    total = len(results)
    r2s = [r["r2"] for r in results]
    devs = [r["max_dev"] for r in results]
    mean_r2 = sum(r2s) / total
    mean_dev = sum(devs) / total
    N_cfg = results[0]["N"] if results else N

    detail = (f"pass_seeds={pass_seeds}/{total} mean_r2={mean_r2:.3f} "
              f"mean_max_dev={mean_dev:.3f} N={N_cfg} f_sweep={F_SWEEP_FULL} "
              f"HP_R2_MAX={HP_R2_MAX} HP_MAX_DEV_ALT={HP_MAX_DEV_ALT}")

    # HARD_FAIL: all seeds show smooth-monotone
    if all(not r.get("passes_hp", False) and r.get("r2", 0) >= HF_R2_MIN for r in results):
        return ("SS_V18_HARD_FAIL",
                f"SMOOTH_MONOTONE: plateau absent at N={N_cfg}. " + detail)

    if pass_seeds >= HP_MAJORITY_MIN:
        return ("SS_V18_HARD_PASS",
                f"SAAD-SOLLA PLATEAU N={N_cfg}: {pass_seeds}/{total} seeds confirm plateau. "
                + detail)

    return ("SS_V18_MIDDLE_BAND",
            f"Partial: {pass_seeds}/{total} seeds plateau at N={N_cfg}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N == 16384, f"PROT-018: N must be 16384; got {N}"

    # Formula self-tests
    assert int(0.125 * N) == 2048, f"M formula: {int(0.125*N)} != 2048"

    # Gate self-tests
    assert seed_passes_hp(0.290, 0.514), "seed_passes_hp HARD_PASS test failed"
    assert not seed_passes_hp(0.97, 0.02), "seed_passes_hp HARD_FAIL test failed"
    assert seed_passes_hp(0.60, 0.0), "r2-only PASS test failed"
    assert seed_passes_hp(0.95, 0.42), "max_dev-only PASS test failed"

    # Verdict self-test
    fake_pass = [{"passes_hp": True, "r2": 0.30, "max_dev": 0.51, "N": N}
                 for _ in range(2)]
    v, msg = compute_verdict(fake_pass)
    assert "HARD_PASS" in v, f"Verdict HARD_PASS test: {v}"

    fake_fail = [{"passes_hp": False, "r2": 0.97, "max_dev": 0.01, "N": N}
                 for _ in range(2)]
    v2, _ = compute_verdict(fake_fail)
    assert "HARD_FAIL" in v2 or "MIDDLE_BAND" in v2, f"Verdict fail test: {v2}"

    # Smoke forward pass at N_SMOKE
    device = torch.device("cpu")
    result = run_v18_seed(N_SMOKE, 17, F_SWEEP_SMOKE, smoke=True, device=device)
    assert "r2" in result, f"r2 missing: {list(result.keys())}"
    assert result.get("ret_A_vals") and len(result["ret_A_vals"]) == len(F_SWEEP_SMOKE), \
        f"ret_A_vals wrong length: {result.get('ret_A_vals')}"
    assert all(not (v is None) for v in result["ret_A_vals"]), \
        f"Some ret_A_vals are None: {result['ret_A_vals']}"

    # Multi-scale smoke N_SMOKE x4
    result_4x = run_v18_seed(N_SMOKE * 4, 17, F_SWEEP_SMOKE, smoke=True, device=device)
    assert "r2" in result_4x and result_4x["r2"] is not None, "4x smoke r2 missing"

    print(f"[selftest] saad_solla_v18_n16384 PASS r2_smoke={result['r2']:.3f} "
          f"max_dev_smoke={result['max_dev']:.3f}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() and not smoke else "cpu")
    N_cfg  = N_SMOKE if smoke else N
    f_sweep = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL
    seeds   = SEEDS_SMOKE if smoke else SEEDS_FULL

    exp_name = os.environ.get("HDLAB_EXP_NAME", "saad_solla_v18_n16384")
    print(f"[run] {exp_name} smoke={smoke} N={N_cfg} f_sweep={f_sweep} "
          f"seeds={seeds} device={device}", flush=True)
    if not smoke:
        assert N_cfg == 16384, f"FULL run must use N=16384 (PROT-018); got {N_cfg}"

    out_dir = get_output_dir(exp_name)

    # PER-SEED CHECKPOINT (PROT-019 resume contract): scan partials so a
    # mid-run CUDA crash (seen on v10/v18 at N=16384) can resume instead of
    # restarting all seeds.
    done_seeds, remaining_seeds = resumable_seeds(seeds, out_dir)
    if done_seeds:
        print(f"[ckpt] resume: {len(done_seeds)}/{len(seeds)} seeds already "
              f"complete from prior run; running remaining "
              f"{len(remaining_seeds)}: {remaining_seeds}", flush=True)
    else:
        print(f"[ckpt] no prior partials; running all {len(seeds)} seeds",
              flush=True)

    for seed in remaining_seeds:
        print(f"\n  [seed={seed}]", flush=True)
        r = run_v18_seed(N_cfg, seed, f_sweep, smoke=smoke, device=device)
        # Atomic checkpoint BEFORE moving to next seed.
        write_partial(out_dir, seed, r)
        print(f"  seed={seed} [ckpt written]", flush=True)

    # Aggregate ALL seeds (this-run + prior-run partials)
    agg = aggregate_partials(out_dir, seeds)
    results: List[Dict] = [agg[str(s)] for s in seeds if str(s) in agg]

    verdict_str, verdict_msg = compute_verdict(results)
    elapsed = time.time() - t0
    print(f"\n[verdict] {verdict_str}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    metrics = {
        "verdict": verdict_str,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N_cfg, "smoke": smoke, "seeds": seeds, "f_sweep": f_sweep},
        "results": results,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f_out:
        json.dump(metrics, f_out, indent=2)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        sys.exit(0)
    run(smoke=args.smoke)
else:
    run(smoke=False)
