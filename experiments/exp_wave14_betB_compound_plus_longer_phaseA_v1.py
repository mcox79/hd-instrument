"""Bet B compound + longer-Phase-A consolidation — third-axis HARD-PASS probe.

v187 pre-registered untested item. The v187 verdict confirmed compound per-task +
replay STACKS sub-additively to retention_A=0.915 but does NOT clear HARD-PASS
0.95 (gap of 3.5pp). One cheap orthogonal axis is to EXTEND Phase A consolidation
(more epochs on the first task before any phase shift) — the hypothesis is that
the substrate has not fully settled on task A at PHASE_A_EPOCHS=8 and that
longer consolidation will lift the retention_A floor on top of which the
compound axis-stacking acts.

Mechanism: same as exp_wave14_betB_compound_pertask_replay_v1 but with
PHASE_A_EPOCHS_FULL=24 (3x the v187 baseline 8). All other parameters identical.

Pre-reg falsifier statements:

  - HARD-PASS:  mean retention_A >= 0.95 across 5 seeds. Longer Phase A
                consolidation IS the missing third axis; substrate ceiling
                broken; Bet B retention rehab clears HARD-PASS.
  - HARD-FAIL:  mean retention_A <= 0.915 (the v187 baseline). Longer
                consolidation adds NOTHING above the v187 compound baseline;
                Phase A 8 epochs is already saturating; new axis is required.
  - MIDDLE:     0.915 < mean retention_A < 0.95. Longer consolidation lifts
                retention partially but does not clear HARD-PASS; v187 ceiling
                breaks but third-axis benefit is bounded.

Per [[feedback-no-smoke]]: HARD-PASS and HARD-FAIL falsifiable BEFORE running.
Per [[feedback-rehabilitation-after-rejection]]: third-axis rescue for v187
compound-axis-stacking-additive-but-bounded annotation.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.

Pre-reg: preregs/2026-05-24_wave14_betB_compound_plus_longer_phaseA_v1.md
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

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# Load compound base.
_base_path = REPO / "experiments" / "exp_wave14_betB_compound_pertask_replay_v1.py"
_spec = importlib.util.spec_from_file_location("compound_base", _base_path)
compound = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compound)

# Override Phase A epochs. All other constants inherited.
PHASE_A_EPOCHS_FULL = 24  # 3x v187 baseline 8
PHASE_A_EPOCHS_SMOKE = 2

# Verdict thresholds (designed; documented above).
PASS_RETENTION = 0.95
FAIL_RETENTION = 0.915  # v187 compound baseline; this variant must beat it.


def compute_verdict(summary):
    seeds_data = summary.get("per_seed")
    if not seeds_data:
        return ("LONGER_PHASEA_INCONCLUSIVE", "Missing per-seed data.")
    seeds = list(seeds_data.values())
    ret_A_mean = sum(s["retention_A"] for s in seeds) / len(seeds)
    ret_B_mean = sum(s["retention_B"] for s in seeds) / len(seeds)
    if ret_A_mean >= PASS_RETENTION:
        return ("LONGER_PHASEA_HARD_PASS",
                f"Longer Phase A IS the third axis: retention_A={ret_A_mean:.3f}>={PASS_RETENTION}. "
                f"Bet B retention rehab clears HARD-PASS via longer consolidation. retention_B={ret_B_mean:.3f}.")
    if ret_A_mean <= FAIL_RETENTION:
        return ("LONGER_PHASEA_HARD_FAIL",
                f"Longer Phase A adds NOTHING above v187 compound: retention_A={ret_A_mean:.3f}<={FAIL_RETENTION}. "
                f"Phase A 8 epochs already saturating; consolidation NOT the missing axis. retention_B={ret_B_mean:.3f}.")
    return ("LONGER_PHASEA_MIDDLE_BAND",
            f"retention_A={ret_A_mean:.3f} in ({FAIL_RETENTION},{PASS_RETENTION}); "
            f"longer consolidation partial benefit; ceiling breaks but HARD-PASS NOT cleared. retention_B={ret_B_mean:.3f}.")


def self_test_verdict():
    def mk(ra, rb):
        return {"per_seed": {"17": {"retention_A": ra, "retention_B": rb}}}
    cases = [
        (mk(0.96, 0.93), "LONGER_PHASEA_HARD_PASS"),
        (mk(0.95, 0.90), "LONGER_PHASEA_HARD_PASS"),
        (mk(0.93, 0.88), "LONGER_PHASEA_MIDDLE_BAND"),
        (mk(0.92, 0.85), "LONGER_PHASEA_MIDDLE_BAND"),
        (mk(0.915, 0.85), "LONGER_PHASEA_HARD_FAIL"),
        (mk(0.85, 0.70), "LONGER_PHASEA_HARD_FAIL"),
        ({}, "LONGER_PHASEA_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": compound.N_SMOKE if smoke else compound.N_FULL,
              "batch_size": compound.BATCH_SIZE_SMOKE if smoke else compound.BATCH_SIZE_FULL,
              "epochs": compound.EPOCHS_SMOKE if smoke else compound.EPOCHS_FULL,
              "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": compound.BYTES_PER_CORPUS_SMOKE if smoke else compound.BYTES_PER_CORPUS_FULL,
              "seeds": compound.SEEDS_SMOKE if smoke else compound.SEEDS_FULL,
              "replay_frac": compound.REPLAY_FRAC,
              "pass_retention": PASS_RETENTION,
              "fail_retention": FAIL_RETENTION,
              "variant": "longer_phaseA"}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = compound.run_one_seed_compound(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: retention_A={r['retention_A']:.3f} retention_B={r['retention_B']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    compound.validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict(); return 0
    name = os.environ.get("HDLAB_EXP_NAME",
                          "wave14_betB_compound_plus_longer_phaseA_v1_smoke" if args.smoke
                          else "wave14_betB_compound_plus_longer_phaseA_v1")
    out_dir = _canonical_get_output_dir(name)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    if args.smoke:
        seed_key = list(summary["per_seed"].keys())[0]
        r = summary["per_seed"][seed_key]
        oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.10)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
