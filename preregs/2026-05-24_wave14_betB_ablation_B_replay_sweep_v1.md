# Pre-reg: Bet B Ablation B — replay-only sweep across replay_frac

**Date**: 2026-05-24
**Script**: `experiments/exp_wave14_betB_ablation_B_replay_sweep_v1.py`
**Queue**: overnight_queue (GPU)
**Designed by**: exp_dev (user override "YOU design everything" per the 2026-05-24 ship dispatch)
**Anchor source**: `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md` Anchor 2

## Hypothesis

Replay frequency (replay_frac) is the load-bearing knob for Bet B retention; the 73% retention ceiling at replay_frac=0.10 is not a structural bound but a knob-position artifact, and sweeping replay_frac up to 1.0 unlocks higher retention.

## Mechanism

Same single-shared-W A->B->C pipeline as base Bet B Kovacs experiment, sweeping replay_frac in {0.0, 0.05, 0.10, 0.25, 0.50, 0.75, 1.0} (7 cells). EMA blend alpha=0.7 fixed (best-alpha from base v1).

## Parameters

- N = 4096
- K = 4
- BETA = 8.0
- ALPHA_RETR = 0.3
- batch_size = 64
- bytes_per_corpus = 200,000
- Phase A epochs = 8
- Phases B/C epochs = 5
- EMA blend alpha = 0.7
- replay_frac sweep = [0.0, 0.05, 0.10, 0.25, 0.50, 0.75, 1.0]
- Seeds: [7, 17, 23, 31, 41] (5)

Total cells: 7 fracs x 5 seeds = 35 A->B->C runs.

## Falsifier bands (HARD-PASS / HARD-FAIL / MIDDLE)

Pre-registered before running per [[feedback-no-smoke]] and [[feedback-envelope-expansion-fail-bands]]:

- **HARD-PASS monotone**: retention_A (mean across seeds, per-frac) is monotone-non-decreasing across the 7 cells (with tol=0.02 for noise) AND peak retention_A >= 0.90. Conclusion: replay-alone can close the gap; cost-vs-retention frontier is the design knob.
- **HARD-FAIL plateau**: max retention_A across cells with replay_frac >= 0.25 is < 0.80. Conclusion: ceiling at ~73-80% bounded by a structural property of the substrate; only structural-separation routes (MoE, sub-substrate Ablation A) can break this.
- **MIDDLE-BAND**: any other pattern; report bands.

## Comparison anchor

73% retention_A at replay_frac=0.10 from earlier Bet B Kovacs runs is the established midpoint.

## Self-tests (pre-flight)

`python experiments/exp_wave14_betB_ablation_B_replay_sweep_v1.py --self-test` -> 5/5 verdict cells PASS + 4/4 monotone-helper unit tests PASS.

## Discipline citations

- Per [[feedback-rehabilitation-after-rejection]]: this is the replay-frequency rescue path for EWC-null.
- Per [[feedback-no-papers-product-only]]: substrate-product framing only.
- Per [[feedback-ascii-only-in-scripts]]: ASCII-only output.

## Estimated wallclock

GPU full at N=4096, 5 seeds, 7 fracs: ~60-120 min (7x base Bet B Kovacs cell cost).
