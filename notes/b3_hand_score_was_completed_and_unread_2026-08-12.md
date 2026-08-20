# B3 IS NOT PENDING -- IT WAS SCORED ON 2026-08-12 AND NEVER READ

**Resolved 2026-08-20.** `metrics.json` is DELIBERATELY NOT MODIFIED: rewriting a landed verdict
record is the same hazard class as adjusting a gate after the fact, and the original is the
provenance. This sidecar is the correction; the verdict field stays as it was written.

## WHAT THE CELL SAID

    verdict:      STRUCTURAL_PASS_PENDING_B3
    verdict_msg:  "structural gates pass; 100 blind rows written for the director's hand-score.
                   THIS CELL MAKES NO QUALITY CLAIM."

`notes/SUBSTRATE_CHARTER_read_first.md` makes this the third of three conditions on **GROWTH STAYS
PAUSED**, and `MEMORY.md` records the matching belief: *"The surviving number is 634, and it has not
been re-vetted."*

## WHAT WAS ACTUALLY ON DISK

`_joined_verdicts.json` -- written **10 minutes AFTER** `blind_sample.json` -- contains **all 100
rows, scored MEANINGFUL / RELATED / NOISE and already joined to their arm.** The hand-score was
done. Only the verdict field and the downstream docs were never updated.

| arm | n | MEANINGFUL | RELATED | NOISE | MEANINGFUL rate [95% CI] |
|---|---|---|---|---|---|
| PBV_BASE | 50 | 1 | 12 | 37 | 0.020 [0.000, 0.060] |
| PBV_F1F3 (read-out fix) | 50 | 2 | 7 | 41 | 0.040 [0.000, 0.100] |

**`BASE - F1F3` = -0.020, 95% CI [-0.080, +0.040] -- NOT separated.** The read-out fix did not move
grounding quality. Overall **3 MEANINGFUL / 19 RELATED / 78 NOISE**.

## SCOPE -- READ THIS BEFORE QUOTING THE NUMBER

- **0 of 100 rows are self-tautologies**, so the tautology gate worked and this is the CROSS-GROUNDED
  population, not the tautology-inflated one. That is the axis on which it is comparable.
- **⛔ DO NOT PLACE THIS BESIDE THE HISTORICAL 35% / 64% / 94% FIGURES.** `MEMORY.md` carries an
  explicit standing prohibition on that juxtaposition, and the corpora differ -- this sample is
  onestop reading-levels plus biology.
- **n is tiny where it counts: MEANINGFUL counts are 1 and 2, and both CIs touch zero.** This
  separates "poor" from "excellent". It does not resolve 2% from 5%.
- **Single scorer, no second witness**, and the scorer was a prior session's director.
- **DIFFERENT OBJECT from the word-recall task.** This scores the GROUNDED_MEANING fact store, not
  the accumulated word profiles the rank metric scores. Numbers do not transfer between them.
- ✅ **The charter's own prediction reproduces, which is the nearest thing to a positive control
  here:** *"meaningful groundings concentrate in the dense technical (biology) segment"* --
  `bio_new` 9 of 17 meaningful-or-related (53%) vs `adv_new` 6 of 42 (14%).

## CONSEQUENCE

**Condition 3 is MET, and it does NOT confirm quality.** Growth stays paused on EVIDENCE rather than
on an open item. The charter line can now be resolved either way instead of hanging indefinitely.

Recomputed by `scratch/` analysis on 2026-08-20; the raw rows are in `_joined_verdicts.json` beside
this file and the arithmetic is a `collections.Counter` over its `v` field grouped by `arm`.
