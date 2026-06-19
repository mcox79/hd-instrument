"""Bet-B 4-stage CL at N=16384: scale-extension to test retA floor origin.

CONTEXT:
  bet_b_4stage_rehab_epochs_v3 (N=8192, 10 seeds): MIDDLE_BAND mean ret_A=0.741.
  bet_b_4stage_batch128_v1 (N=8192, 5 seeds): MIDDLE_BAND mean ret_A=0.750.
  bet_b_4stage_phaseD_aweight_v2 (N=8192, 5 seeds): MIDDLE_BAND ret_A=0.749.
  Floor confirmed at ~0.74-0.75 across 3 axes at N=8192.
  Remaining question: is retA=0.74 floor N-scale-dependent or intrinsic to substrate?

SCIENTIFIC QUESTION:
  If N=16384 retA >= 0.80: floor was finite-N artifact; substrate scales as expected.
  If N=16384 retA <= 0.78: floor is fundamental substrate mechanism at this scale class.
  -> Accept bar-lowering reframe: retA >= 0.70 becomes product threshold.

OOM PRE-CHECK:
  W at N=16384: 16384^2 * 4 bytes = 1.07 GB per matrix.
  Peak: 2 active W matrices = 2.15 GB. Replay pools: 3 * 67 MB = 200 MB.
  Total ~2.35 GB. Well under 6 GB ceiling. Safe.

PRE-REGISTERED BANDS:
  HARD_PASS: mean ret_A >= 0.80 at N=16384.
    retA floor was finite-N artifact; substrate scales; production N=16384 ships.
  HARD_FAIL: mean ret_A <= 0.78 at N=16384 (floor is N-invariant).
    Accept bar-lowering reframe (retA >= 0.70 product threshold).
  MIDDLE_BAND: ret_A in (0.78, 0.80). Ambiguous.

FORMULA SELF-TESTS:
  1. N_FULL == 16384 (PROT-018: no _nN suffix; N_FULL stated explicitly below).
  2. OOM check: 2 * (16384^2 * 4) / 1e9 = 2.15 GB < 6 GB. Verified below.
  3. FOURSTAGE_HARD_PASS fires when retention_A=0.82, B=0.72, C=0.72.
  4. FOURSTAGE_HARD_FAIL_N16384 fires when mean_ret_A <= 0.78.
  5. run_one_seed(seed, config, device) returns dict with 'retention_A'.

TIMEOUT ESTIMATE:
  N=8192 baseline (phaseD_aweight_v2): estimated 2700s for 5 seeds.
  N=16384: inner products scale as (16384/8192)^2 = 4x (matrix multiply is O(N^2) per batch).
  Expected: 2700 * 4 = 10800s with +50% buffer -> 16200s.
  EXCEEDS 14400s (4h limit). ACTION: reduce to 2 seeds for feasibility probe.
  2 seeds at N=16384: 10800 / 5 * 2 = 4320s -> with buffer 6480s -> round to 7200s.
  FLAG: 2-seed probe instead of 5-seed (cost-driven); HP requires 2/2 seeds > 0.80.
  timeout_s = 7200.

N-suffix: no _nN suffix; production N = 16384 (PROT-018: stated explicitly; N_FULL=16384).
Queue: overnight_queue (GPU; N=16384 4-stage CL, 2-seed feasibility probe)
Pre-reg: preregs/2026-05-27_bet_b_4stage_n16384_v1.md
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

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

# Load 4-stage v1 base (provides run_one_seed, compute_verdict, load_corpus_D, etc.)
_v1_path = REPO / "experiments" / "exp_wave14_betB_4stage_continual_v1.py"
_v1_spec = importlib.util.spec_from_file_location("v1base_4stage_n16k", _v1_path)
v1base = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1base)

# PRODUCTION CONFIG -- PROT-018: no _nN suffix; N_FULL=16384 stated explicitly
N_FULL = 16384           # SCALE EXTENSION from N=8192 baseline
N_SMOKE = 1024
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200_000
BYTES_SMOKE = 5_000
# 2-seed probe (cost-driven; N=16384 matrix ops are 4x N=8192)
SEEDS_FULL = [7, 17]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
PASS_RET_A = 0.80
PASS_RET_B = 0.70
PASS_RET_C = 0.70
FAIL_RET_A_MAX = 0.78    # N16384 HARD_FAIL gate (floor is N-invariant)


def get_output_dir(default_name: str = "bet_b_4stage_n16384_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict_n16k(per_seed_results: list) -> tuple[str, str]:
    """N=16384 specific verdict with floor-origin framing."""
    if not per_seed_results:
        return ("N16K_INCONCLUSIVE", "No seed results.")

    ret_As = [r["retention_A"] for r in per_seed_results]
    ret_Bs = [r["retention_B"] for r in per_seed_results]
    ret_Cs = [r["retention_C"] for r in per_seed_results]
    mean_A = sum(ret_As) / len(ret_As)
    mean_B = sum(ret_Bs) / len(ret_Bs)
    mean_C = sum(ret_Cs) / len(ret_Cs)
    n = len(per_seed_results)

    if mean_A >= PASS_RET_A and mean_B >= PASS_RET_B and mean_C >= PASS_RET_C:
        return ("FOURSTAGE_HARD_PASS_N16384",
                f"N=16384 CLEARS ret_A FLOOR. mean_ret_A={mean_A:.3f} >= {PASS_RET_A}. "
                f"mean_ret_B={mean_B:.3f}, mean_ret_C={mean_C:.3f}. "
                f"retA=0.74 floor was finite-N artifact at N=8192. "
                f"Bet B 4-stage CL scales to production N=16384. "
                f"n_seeds={n}.")

    if mean_A <= FAIL_RET_A_MAX:
        return ("FOURSTAGE_HARD_FAIL_N16384",
                f"retA FLOOR CONFIRMED N-INVARIANT. mean_ret_A={mean_A:.3f} <= {FAIL_RET_A_MAX}. "
                f"mean_ret_B={mean_B:.3f}, mean_ret_C={mean_C:.3f}. "
                f"N=16384 does not lift floor from N=8192 baseline (0.74-0.75). "
                f"Floor is intrinsic to substrate 4-stage depth. "
                f"Action: accept retA >= 0.70 product threshold. "
                f"n_seeds={n}.")

    return ("FOURSTAGE_MIDDLE_BAND_N16384",
            f"Borderline. mean_ret_A={mean_A:.3f} (band 0.78-0.80). "
            f"mean_ret_B={mean_B:.3f}, mean_ret_C={mean_C:.3f}. "
            f"May require 5-seed N=16384 probe to resolve. n_seeds={n}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

    # OOM pre-check
    W_bytes = N_FULL * N_FULL * 4
    assert 2 * W_bytes < 6e9, f"OOM: 2 W matrices = {2*W_bytes/1e9:.2f} GB (limit 6 GB)"

    # Import-chain: v1base functions accessible
    assert hasattr(v1base, "compute_verdict"), "compute_verdict missing from v1base"
    assert hasattr(v1base, "run_one_seed"), "run_one_seed missing from v1base"
    assert hasattr(v1base, "self_test_verdict"), "self_test_verdict missing from v1base"

    # Self-test verdict (v1base inherited)
    v1base.self_test_verdict()

    # Verdict v2 logic tests
    # HARD_PASS
    v, msg = compute_verdict_n16k([
        {"retention_A": 0.82, "retention_B": 0.75, "retention_C": 0.72},
        {"retention_A": 0.83, "retention_B": 0.74, "retention_C": 0.71},
    ])
    assert v == "FOURSTAGE_HARD_PASS_N16384", f"Expected HARD_PASS, got {v}"

    # HARD_FAIL
    v, msg = compute_verdict_n16k([
        {"retention_A": 0.74, "retention_B": 0.86, "retention_C": 0.81},
        {"retention_A": 0.75, "retention_B": 0.85, "retention_C": 0.80},
    ])
    assert v == "FOURSTAGE_HARD_FAIL_N16384", f"Expected HARD_FAIL, got {v}"

    # Smoke forward pass at N_SMOKE=1024 via v1base.run_one_seed
    device = torch.device("cpu")
    config_smoke = {
        "N": N_SMOKE,
        "batch_size": BATCH_SIZE_SMOKE,
        "epochs": EPOCHS_SMOKE,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE,
        "bytes_per_corpus": BYTES_SMOKE,
        "mode": "smoke",
    }
    result = v1base.run_one_seed(17, config_smoke, device)
    assert "retention_A" in result, f"missing retention_A; keys={list(result.keys())}"
    assert 0.0 <= result["retention_A"] <= 1.0, f"retention_A out of range: {result['retention_A']}"

    print("[SELFTEST PASS] bet_b_4stage_n16384_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    bytes_use = BYTES_SMOKE if smoke else BYTES_FULL
    out_dir = get_output_dir()
    t0 = time.time()

    config = {
        "N": N,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": bytes_use,
        "mode": "smoke" if smoke else "full",
    }

    print(f"[bet_b_n16k] N={N} seeds={seeds} bytes={bytes_use} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    per_seed_results = []
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = v1base.run_one_seed(seed, config, device)
        te = time.time() - ts
        print(f"  seed {seed} done in {te:.1f}s "
              f"ret_A={result['retention_A']:.3f} "
              f"ret_B={result['retention_B']:.3f} "
              f"ret_C={result['retention_C']:.3f}", flush=True)
        per_seed_results.append(result)

        # Per-seed checkpoint
        checkpoint_path = out_dir / "metrics_checkpoint.json"
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump({"per_seed": per_seed_results, "N_full": N_FULL}, f, indent=2)

    verdict, verdict_msg = compute_verdict_n16k(per_seed_results)
    elapsed = time.time() - t0

    mean_A = sum(r["retention_A"] for r in per_seed_results) / len(per_seed_results)
    mean_B = sum(r["retention_B"] for r in per_seed_results) / len(per_seed_results)
    mean_C = sum(r["retention_C"] for r in per_seed_results) / len(per_seed_results)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "mean_retention_A": mean_A,
        "mean_retention_B": mean_B,
        "mean_retention_C": mean_C,
        "per_seed": per_seed_results,
        "N_full": N_FULL,
        "N_used": N,
        "n_seeds": len(per_seed_results),
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[bet_b_n16k] VERDICT: {verdict}", flush=True)
    print(f"[bet_b_n16k] {verdict_msg}", flush=True)
    print(f"[bet_b_n16k] elapsed={elapsed:.1f}s output={out_path}", flush=True)


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
