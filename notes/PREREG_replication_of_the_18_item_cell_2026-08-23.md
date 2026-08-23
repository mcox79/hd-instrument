# PRE-REGISTRATION (filed in notes/, NOT scratch/ -- scratch is gitignored, and a
# pre-registration that is not committed before the run is not a pre-registration) -- written BEFORE the run, so the result cannot be reinterpreted afterwards

**2026-08-23.** I flagged a `17/18 = 0.9444` cell as post-hoc, arrived at after slicing one dataset
by band, by stage, by anchor size, by weighting and by rounding, and said it must be re-tested on a
population fixed in advance. This is that test. **Written and committed before the numbers exist.**

## THE CLAIM UNDER TEST

Among items the SIM-WEIGHTED vote commits to but an UNWEIGHTED (membership-only) vote does not,
those SURVIVING the pseudo-count rounding are more accurate than those DISCARDED by it.

## WHY THIS POPULATION IS FRESH, AND WHERE IT IS NOT

**The anchor changes from the 52-word set to the 84-word extended set.** That changes every
neighbourhood, so the in-range anchor sets, the vote margins, the commit decisions and therefore the
CELL MEMBERSHIP are all freshly determined. **I have never run this split under that anchor.**

⚠️ **HONEST LIMIT: the item pool overlaps the original.** This is a replication under a different
mechanism configuration, **not** an independent sample. A fresh gold set would be stronger and I do
not have one -- the disk enumeration found exactly one valence lexicon. **Stated here rather than
discovered in the write-up.**

## PRE-SPECIFIED CELLS -- these four, no others, no re-slicing afterwards

1. weighted-only, SURVIVES the rounding
2. weighted-only, DISCARDED
3. overlap, SURVIVES
4. overlap, DISCARDED

## PRE-SPECIFIED VERDICT

**REPRODUCED** iff BOTH hold:
- cell 1 accuracy > cell 2 accuracy, **and**
- cell 1 accuracy `>= 0.75`

**NOT REPRODUCED** otherwise. **If cell 1 has fewer than 10 items, the verdict is UNTESTABLE** --
not "reproduced", not "failed".

## WHAT I EXPECT

**I genuinely do not know.** The original cell is small and post-hoc; a coin-flip outcome would not
surprise me. **If it fails I will report it as a failed replication and retire the finding**, which
is the whole reason for writing this down first.

## WHAT I WILL NOT DO AFTERWARDS

- Not change the threshold, the cells, or the verdict rule.
- Not report a third slice that happens to look better.
- Not describe a failure as "directionally consistent".
