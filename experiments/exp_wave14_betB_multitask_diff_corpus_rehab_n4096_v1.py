"""U1/U7 Multi-task transfer (corpus A -> corpus C) -- v190 rehab axis 2.

Per v190 cap_map U1/U7 rehab axis 2: larger N=4096 for retention floor.

U1/U7 v1 verdict: MULTITASK_DIFF_MIDDLE_BAND retention_A=0.600 gain_C=3.76 at
N=2048 5-seed. Strong new-corpus uptake (gain_C >> HARD-PASS 0.3) but
retention_A=0.600 below per-corpus retention HARD-PASS 0.7. This rehab axis
tests whether doubling N (2048 -> 4096) lifts retention_A floor.

Mechanism unchanged from v1: Phase A on corpus_a (English bytes); Phase C on
hex-encoded numerical corpus with A-replay (single-shared-W); evaluate
retention_A (BPC on held-out A after C) and gain_C (BPC reduction on C vs
zero-W baseline). Only N (2048 -> 4096) changes.

Pre-reg falsifier statements:

  - HARD-PASS:  mean retention_A >= 0.70 AND mean gain_C >= 0.30 across 5 seeds.
                U1/U7 cross-corpus retention rehab passes via N-scaling; U1/U7
                🟡 -> ✅ track.
  - HARD-FAIL:  mean retention_A <= 0.30 OR mean gain_C <= 0.05. Either
                catastrophic forgetting OR new-corpus uptake collapses with
                bigger N.
  - MIDDLE:     intermediate. N=4096 lifts retention partially but does not
                clear HARD-PASS 0.70 (joins axis 1 as second saturation
                point; structural-separation axis routing required).

Per [[feedback-no-smoke]]: bands falsifiable BEFORE running.
Per [[feedback-rehabilitation-after-rejection]]: rehab axis 2 of v190 3-axis
U1/U7 rehab list (axis 1 = MoE structural separation; axis 2 = N scaling;
axis 3 = weighted replay favoring corpus-A).
Per [[feedback-envelope-expansion-fail-bands]]: envelope-expansion drill on
U1/U7 PARTIAL row from v190.

Pre-reg: preregs/2026-05-24_wave14_betB_multitask_diff_corpus_rehab_n4096_v1.md
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

# Load v1 module to reuse run_one_seed + compute_verdict + write_metrics.
_v1_path = REPO / "experiments" / "exp_wave14_betB_multitask_diff_corpus_v1.py"
_spec = importlib.util.spec_from_file_location("u1base", _v1_path)
u1base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(u1base)
base = u1base.base
pa = u1base.pa

N_FULL = 4096
N_SMOKE = 1024
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 3
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 5
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 80000
BYTES_SMOKE = 4000
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "pass_ret_A": u1base.PASS_RET_A, "pass_gain_C": u1base.PASS_GAIN_C,
              "fail_ret_A": u1base.FAIL_RET_A, "fail_gain_C": u1base.FAIL_GAIN_C,
              "corpus_C": "hex_encoded_numerical",
              "rehab_axis": "N=4096 (v1 was N=2048)"}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = u1base.run_one_seed(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: retention_A={r['retention_A']:.3f} gain_C={r['gain_C']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = u1base.compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        u1base.self_test_verdict(); return 0
    name = os.environ.get("HDLAB_EXP_NAME",
                          "wave14_betB_multitask_diff_corpus_rehab_n4096_v1_smoke" if args.smoke
                          else "wave14_betB_multitask_diff_corpus_rehab_n4096_v1")
    out_dir = REPO / "data" / f"exp_{name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    if args.smoke:
        seed_key = list(summary["per_seed"].keys())[0]
        r = summary["per_seed"][seed_key]
        oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.10)
    u1base.write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
