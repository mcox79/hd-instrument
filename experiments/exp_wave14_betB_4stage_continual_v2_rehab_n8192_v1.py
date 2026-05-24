"""Bet B 4-stage continual learning A->B->C->D -- v189 K2 rehab variant.

Per v189 K2 4-stage rehab promotion gate (cap_map):
  - v1 result: FOURSTAGE_MIDDLE_BAND retention_A=0.74 retention_B=0.85 retention_C=0.80
  - retention_A misses HARD-PASS 0.80 by 6pp; B and C clear 0.70 HARD-PASS
  - Rehab axis: larger N (N=8192) + stronger Phase-A consolidation (2x Phase-A epochs)

This v2 tests whether the earliest-stage retention deficit at N=4096 closes when:
  (a) substrate dimension N is doubled to 8192 (more capacity headroom)
  (b) Phase-A consolidation is doubled (16 epochs instead of 8)

Pre-reg falsifier statements:
  - HARD-PASS:  mean retention_A >= 0.80 AND retention_B >= 0.70 AND retention_C >= 0.70
                across 5 seeds. K2 4-stage CL clears HARD-PASS with capacity + consolidation rehab.
  - HARD-FAIL:  mean retention_A <= 0.50 OR catastrophic-collapse pattern at stage D.
                Capacity doubling does not help; 4-stage exceeds substrate ceiling
                regardless of N + consolidation rehab.
  - MIDDLE:     intermediate. Rehab axis adds partial benefit but does not close
                the retention_A gap. Same band as v1.

Per [[feedback-no-smoke]]: HARD-PASS and HARD-FAIL falsifiable BEFORE running.
Per [[feedback-envelope-expansion-fail-bands]]: this is an envelope-expansion drill on
the K2 row from v1; both bands carry forward + the MIDDLE-band rehab-fail outcome
("rehab does not close the gap") is also pre-specified.

Pre-reg: preregs/2026-05-24_wave14_betB_4stage_continual_v2_rehab_n8192_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from verification import oracle  # noqa: E402

# Load v1 base (provides run_one_seed, compute_verdict, self_test, write_metrics, etc).
_v1_path = REPO / "experiments" / "exp_wave14_betB_4stage_continual_v1.py"
_spec = importlib.util.spec_from_file_location("v1base", _v1_path)
v1base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1base)

# Rehab parameters: N=8192 + 16 Phase-A epochs (2x v1 baseline).
N_FULL = 8192
N_SMOKE = 1024
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 16   # doubled from v1's 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200000
BYTES_SMOKE = 5000
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "pass_ret_A": v1base.PASS_RET_A, "pass_ret_B": v1base.PASS_RET_B,
              "pass_ret_C": v1base.PASS_RET_C, "fail_ret_A": v1base.FAIL_RET_A,
              "rehab_axis": "N=8192 + 2x Phase-A epochs (16)"}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = v1base.run_one_seed(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: retention_A={r['retention_A']:.3f} "
              f"retention_B={r['retention_B']:.3f} retention_C={r['retention_C']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = v1base.compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        v1base.self_test_verdict(); return 0
    name = os.environ.get("HDLAB_EXP_NAME",
                          "wave14_betB_4stage_continual_v2_rehab_n8192_v1_smoke" if args.smoke
                          else "wave14_betB_4stage_continual_v2_rehab_n8192_v1")
    out_dir = REPO / "data" / f"exp_{name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    if args.smoke:
        seed_key = list(summary["per_seed"].keys())[0]
        r = summary["per_seed"][seed_key]
        oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.10)
    v1base.write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
