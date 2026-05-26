# Pre-reg: Bet B Ablation A — per-task sub-substrate

**Date**: 2026-05-24
**Script**: `experiments/exp_wave14_betB_ablation_A_per_task_v1.py`
**Queue**: overnight_queue (GPU)
**Designed by**: exp_dev (user override "YOU design everything" per the 2026-05-24 ship dispatch; supersedes [[feedback-no-experiment-design-in-prompts]] for this cycle)
**Anchor source**: `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md` Anchor 1

## Hypothesis

Per-task sub-substrate concatenation (train 3 independent W matrices on corpora A/B/C, average their byte-prediction distributions at retrieval) is the structural-separation-axis rescue path for EWC-null Bet B retention.

## Mechanism

- Phase A: train W_A on corpus_A (zero init), pool_A.
- Phase B: train W_B on corpus_B (zero init; no shared params with W_A), pool_B.
- Phase C: train W_C on corpus_C (zero init), pool_C.
- Retrieval readout: predict-byte distribution = (P_W_A + P_W_B + P_W_C) / 3, blended with retrieval-pool prediction at alpha_retr=0.3 (matches base-script schema).
- Combined pool for retrieval = union of pool_A, pool_B, pool_C.

## Parameters

- N = 4096
- K = 4
- BETA = 8.0
- ALPHA_RETR = 0.3
- batch_size = 64
- bytes_per_corpus = 200,000
- Phase A epochs = 8
- Phases B/C epochs = 5
- Replay frac WITHIN each per-task substrate = 0.0 (the ablation isolates structural separation)
- Seeds: [7, 17, 23, 31, 41] (5)

## Falsifier bands (HARD-PASS / HARD-FAIL / MIDDLE)

Pre-registered before running per [[feedback-no-smoke]] and [[feedback-envelope-expansion-fail-bands]]:

- **HARD-PASS**: mean retention_A across 5 seeds >= 0.95 -> structural separation IS the load-bearing axis for Bet B retention; substrate-level analog of MoE result.
- **HARD-FAIL**: mean retention_A across 5 seeds < 0.80 -> structural separation NOT load-bearing; 73% replay-driven ceiling bounded by something else.
- **MIDDLE-BAND**: 0.80 <= mean retention_A < 0.95; partial structural-separation effect; report bands and propose follow-up.

## Comparison anchor

Base Bet B Kovacs (single shared W, replay_frac=0.5) gives ~73% retention_A — established prior result the rescue must beat.

## Self-tests (pre-flight)

`python experiments/exp_wave14_betB_ablation_A_per_task_v1.py --self-test` -> 7/7 PASS (covers HARD-PASS, HARD-FAIL, MIDDLE, edge cases, empty input).

## Discipline citations

- Per [[feedback-rehabilitation-after-rejection]]: this is the structural-separation rescue for EWC-null; if A passes, MoE PASS predicted on same axis.
- Per [[feedback-no-papers-product-only]]: substrate-product framing only.
- Per [[feedback-ascii-only-in-scripts]]: ASCII-only output.

## Estimated wallclock

GPU full at N=4096, 5 seeds, 3 phase trainings + 3 evaluations per seed: ~30-60 min.
