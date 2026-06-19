"""Compositional generalization hold-out probe — K6 KILLER T2 rehab axis 1.

Per v190 cap_map K6 rehab axis 1: larger N=8192 + 5+ seeds.

K6 v1 verdict: COMPOSITIONAL_MIDDLE_BAND hold_out_acc=0.116 train_acc=0.652 at
N=4096 single-seed. v1 result places K6 just above HARD-FAIL 0.10 (=1.85x chance
floor 1/16=0.0625) but well below HARD-PASS 0.50. This rehab axis tests the
N-scaling hypothesis: does doubling substrate dimension N=4096->8192 lift
hold_out_acc materially while training-set accuracy stays >= 0.65?

Mechanism unchanged from v1: subject-relation-object Latin-square fact set;
single Hebbian bundle B = sum_i value_i * (s_i XOR r_i); unbind-and-cosine
readout. Only N (4096 -> 8192) and seed count (1 -> 5) change.

Pre-reg falsifier statements:

  - HARD-PASS:  mean hold_out_acc >= 0.50 across 5 seeds (chance = 0.0625).
                K6 compositional generalization passes via N-scaling rehab;
                K6 ⚪ -> ✅ track.
  - HARD-FAIL:  mean hold_out_acc <= 0.10 OR mean hold_out_acc < v1's 0.116
                BY 3 PERCENTAGE POINTS (rehab actively hurts; capacity does
                not help K6).
  - MIDDLE:     intermediate (>0.10 and <0.50). Saturation pattern at the
                Latin-square readout scope; K6 second-axis rehab needed
                (e.g., explicit hierarchical pre-binding or Bet X
                position-indexed integration).

Per [[feedback-no-smoke]]: HARD-PASS and HARD-FAIL falsifiable BEFORE running.
Per [[feedback-rehabilitation-after-rejection]]: this is rehab axis 1 of the
v190 4-axis K6 rehab list (axis 1 = N scaling).
Per [[feedback-envelope-expansion-fail-bands]]: envelope-expansion drill on
K6 PARTIAL row from v190; both bands carry forward + MIDDLE-band saturation
outcome pre-specified.

Pre-reg: preregs/2026-05-24_wave14_compositional_holdout_rehab_n8192_v1.md
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

# Load v1 base to reuse run_one_seed + compute_verdict + write_metrics.
_v1_path = REPO / "experiments" / "exp_wave14_compositional_holdout_v1.py"
_spec = importlib.util.spec_from_file_location("k6base", _v1_path)
k6base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(k6base)

N_FULL = 8192
N_SMOKE = 1024
TRAIN_FRAC_FULL = 0.75
TRAIN_FRAC_SMOKE = 0.75
EPOCHS_FULL = 30
EPOCHS_SMOKE = 5
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]


def run_experiment(smoke):
    t0 = time.monotonic()
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "train_frac": TRAIN_FRAC_SMOKE if smoke else TRAIN_FRAC_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "n_objects": k6base.N_OBJECTS, "n_attrs": k6base.N_ATTRS,
              "pass_holdout_acc": k6base.PASS_HOLDOUT_ACC,
              "fail_holdout_acc": k6base.FAIL_HOLDOUT_ACC,
              "rehab_axis": "N=8192 + 5 seeds"}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = k6base.run_one_seed(seed, config)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: hold_out_acc={r['hold_out_acc']:.3f} train_acc={r['train_acc']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = k6base.compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        k6base.self_test_verdict(); return 0
    name = os.environ.get("HDLAB_EXP_NAME",
                          "wave14_compositional_holdout_rehab_n8192_v1_smoke" if args.smoke
                          else "wave14_compositional_holdout_rehab_n8192_v1")
    out_dir = REPO / "data" / f"exp_{name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    if args.smoke:
        seed_key = list(summary["per_seed"].keys())[0]
        r = summary["per_seed"][seed_key]
        oracle.assert_baseline_high("train_acc_smoke", r["train_acc"], 0.10)
    k6base.write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
